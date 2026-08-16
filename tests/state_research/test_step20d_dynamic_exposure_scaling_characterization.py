from __future__ import annotations

import ast
import csv
import hashlib
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "state_research" / "analyze_step20D_dynamic_exposure_scaling.py"

TRADES_INPUT = Path("live_logs/trades_l1_auto_analysis.csv")
LIFECYCLE_INPUT = Path("live_logs/trade_lifecycle_snapshots.csv")
SHADOW_INPUT = Path("live_logs/passive_shadow_risk_snapshots.csv")
OUTPUT = Path("reports/step18/step20D_dynamic_exposure_scaling.csv")

SOURCE_SHA256 = "04bdee183f4854753068851361867cc34283bd77204ac2af1e1adc51365c1fd0"
SOURCE_LINES = 128
START_CAPITAL = 10000.0

FULL_RUNTIME_AVAILABLE = importlib.util.find_spec("pandas") is not None

TRADES_ROWS = (
    {
        "trade_index": "4",
        "entry_timestamp_utc": "2026-01-01T00:30:00Z",
        "exit_timestamp_utc": "2026-01-01T00:32:00Z",
        "side": "SHORT",
        "pnl": "-20",
    },
    {
        "trade_index": "1",
        "entry_timestamp_utc": "2026-01-01T00:00:00Z",
        "exit_timestamp_utc": "2026-01-01T00:02:00Z",
        "side": "LONG",
        "pnl": "100",
    },
    {
        "trade_index": "3",
        "entry_timestamp_utc": "2026-01-01T00:20:00Z",
        "exit_timestamp_utc": "2026-01-01T00:22:00Z",
        "side": "LONG",
        "pnl": "40",
    },
    {
        "trade_index": "2",
        "entry_timestamp_utc": "2026-01-01T00:10:00Z",
        "exit_timestamp_utc": "2026-01-01T00:12:00Z",
        "side": "SHORT",
        "pnl": "-80",
    },
)

LIFECYCLE_ROWS = (
    {"timestamp_utc": "2026-01-01T00:00:00Z", "entry_timestamp_utc": "2026-01-01T00:00:00Z", "side": "long"},
    {"timestamp_utc": "2026-01-01T00:01:00Z", "entry_timestamp_utc": "2026-01-01T00:00:00Z", "side": "LONG"},
    {"timestamp_utc": "2026-01-01T00:02:00Z", "entry_timestamp_utc": "2026-01-01T00:00:00Z", "side": "Long"},
    {"timestamp_utc": "2026-01-01T00:10:00Z", "entry_timestamp_utc": "2026-01-01T00:10:00Z", "side": "short"},
    {"timestamp_utc": "2026-01-01T00:11:00Z", "entry_timestamp_utc": "2026-01-01T00:10:00Z", "side": "SHORT"},
    {"timestamp_utc": "2026-01-01T00:12:00Z", "entry_timestamp_utc": "2026-01-01T00:10:00Z", "side": "Short"},
    {"timestamp_utc": "2026-01-01T00:20:00Z", "entry_timestamp_utc": "2026-01-01T00:20:00Z", "side": "long"},
    {"timestamp_utc": "2026-01-01T00:21:00Z", "entry_timestamp_utc": "2026-01-01T00:20:00Z", "side": "LONG"},
    {"timestamp_utc": "2026-01-01T00:22:00Z", "entry_timestamp_utc": "2026-01-01T00:20:00Z", "side": "Long"},
)

SHADOW_ROWS = (
    {"timestamp_utc": "2026-01-01T00:00:00Z", "shadow_risk_score": "0.31"},
    {"timestamp_utc": "2026-01-01T00:01:00Z", "shadow_risk_score": "0.31"},
    {"timestamp_utc": "2026-01-01T00:02:00Z", "shadow_risk_score": "0.31"},
    {"timestamp_utc": "2026-01-01T00:10:00Z", "shadow_risk_score": "0.51"},
    {"timestamp_utc": "2026-01-01T00:11:00Z", "shadow_risk_score": "0.51"},
    {"timestamp_utc": "2026-01-01T00:12:00Z", "shadow_risk_score": "0.51"},
    {"timestamp_utc": "2026-01-01T00:20:00Z", "shadow_risk_score": "0.71"},
    {"timestamp_utc": "2026-01-01T00:21:00Z", "shadow_risk_score": "0.71"},
    {"timestamp_utc": "2026-01-01T00:22:00Z", "shadow_risk_score": "0.71"},
    {"timestamp_utc": "2026-01-01T00:30:00Z", "shadow_risk_score": "0.90"},
)


def _tree() -> ast.Module:
    return ast.parse(SCRIPT.read_text(encoding="utf-8"), filename=str(SCRIPT))


def _is_main_guard(node: ast.AST) -> bool:
    if not isinstance(node, ast.If):
        return False
    test = node.test
    return (
        isinstance(test, ast.Compare)
        and isinstance(test.left, ast.Name)
        and test.left.id == "__name__"
        and len(test.ops) == 1
        and isinstance(test.ops[0], ast.Eq)
        and len(test.comparators) == 1
        and isinstance(test.comparators[0], ast.Constant)
        and test.comparators[0].value == "__main__"
    )


def _multiplier_function() -> ast.FunctionDef:
    functions = [
        node
        for node in _tree().body
        if isinstance(node, ast.FunctionDef) and node.name == "multiplier_from_streaks"
    ]
    if len(functions) != 1:
        raise AssertionError(f"expected one multiplier function, found {len(functions)}")
    return functions[0]


def _calc_stats_function() -> ast.FunctionDef:
    functions = [
        node
        for node in _tree().body
        if isinstance(node, ast.FunctionDef) and node.name == "calc_stats"
    ]
    if len(functions) != 1:
        raise AssertionError(f"expected one calc_stats function, found {len(functions)}")
    return functions[0]


def _trade_loop() -> ast.For:
    loops = [
        node
        for node in _tree().body
        if isinstance(node, ast.For)
        and isinstance(node.iter, ast.Call)
        and isinstance(node.iter.func, ast.Attribute)
        and node.iter.func.attr == "iterrows"
    ]
    if len(loops) != 1:
        raise AssertionError(f"expected one trade loop, found {len(loops)}")
    return loops[0]


def _write_csv(path: Path, rows: tuple[dict[str, str], ...]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=tuple(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _write_header(path: Path, fieldnames: tuple[str, ...]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        csv.DictWriter(handle, fieldnames=fieldnames).writeheader()


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _manifest(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def _directories(root: Path) -> set[str]:
    return {
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_dir()
    }


def _run(root: Path) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        [sys.executable, str(SCRIPT)],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    completed.stdout = completed.stdout.replace("\r\n", "\n")
    completed.stderr = completed.stderr.replace("\r\n", "\n")
    return completed


class Step20DDynamicExposureScalingCharacterizationTests(unittest.TestCase):
    maxDiff = None

    def test_source_identity_constant_functions_and_import_time_executor_are_bound(self) -> None:
        raw = SCRIPT.read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), SOURCE_SHA256)
        self.assertEqual(len(raw.decode("utf-8").splitlines()), SOURCE_LINES)
        tree = _tree()
        assignments = {
            target.id: ast.literal_eval(node.value)
            for node in tree.body
            if isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance((target := node.targets[0]), ast.Name)
            and target.id == "START_CAPITAL"
        }
        self.assertEqual(assignments, {"START_CAPITAL": START_CAPITAL})
        self.assertEqual(
            [node.name for node in tree.body if isinstance(node, ast.FunctionDef)],
            ["multiplier_from_streaks", "calc_stats"],
        )
        self.assertEqual([node for node in tree.body if _is_main_guard(node)], [])
        reads = [
            node
            for node in tree.body
            if isinstance(node, ast.Assign)
            and isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Attribute)
            and node.value.func.attr == "read_csv"
        ]
        self.assertEqual(len(reads), 3)
        first_function_index = next(index for index, node in enumerate(tree.body) if isinstance(node, ast.FunctionDef))
        self.assertTrue(all(tree.body.index(node) < first_function_index for node in reads))

    def test_fixed_read_and_timestamp_conversion_order_are_bound(self) -> None:
        reads = [
            ast.literal_eval(node.value.args[0])
            for node in _tree().body
            if isinstance(node, ast.Assign)
            and isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Attribute)
            and node.value.func.attr == "read_csv"
        ]
        self.assertEqual(
            reads,
            [TRADES_INPUT.as_posix(), LIFECYCLE_INPUT.as_posix(), SHADOW_INPUT.as_posix()],
        )
        conversions = [
            ast.literal_eval(node.value.args[0].slice)
            for node in _tree().body
            if isinstance(node, ast.Assign)
            and isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Attribute)
            and node.value.func.attr == "to_datetime"
            and isinstance(node.value.args[0], ast.Subscript)
        ]
        self.assertEqual(
            conversions,
            [
                "entry_timestamp_utc",
                "exit_timestamp_utc",
                "timestamp_utc",
                "entry_timestamp_utc",
                "timestamp_utc",
            ],
        )
        utc_keywords = [
            node.value.keywords
            for node in _tree().body
            if isinstance(node, ast.Assign)
            and isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Attribute)
            and node.value.func.attr == "to_datetime"
        ]
        self.assertTrue(all(len(keywords) == 1 and keywords[0].arg == "utc" and ast.literal_eval(keywords[0].value) is True for keywords in utc_keywords))

    def test_multiplier_strict_boundaries_consecutive_streaks_and_minimum_are_bound(self) -> None:
        function = _multiplier_function()
        namespace: dict[str, object] = {}
        module = ast.fix_missing_locations(ast.Module(body=[function], type_ignores=[]))
        exec(compile(module, str(SCRIPT), "exec"), namespace)
        multiplier_from_streaks = namespace["multiplier_from_streaks"]
        self.assertEqual(multiplier_from_streaks([0.30, 0.30, 0.30]), 1.0)
        self.assertEqual(multiplier_from_streaks([0.31, 0.31, 0.31]), 0.5)
        self.assertEqual(multiplier_from_streaks([0.51, 0.51, 0.51]), 0.25)
        self.assertEqual(multiplier_from_streaks([0.71, 0.71, 0.71]), 0.1)
        self.assertEqual(multiplier_from_streaks([0.31, 0.31, 0.30, 0.31, 0.31]), 1.0)
        self.assertEqual(multiplier_from_streaks([0.71, 0.71, 0.71, 0.0, 0.0, 0.0]), 0.1)
        source = ast.unparse(function)
        self.assertIn("high_030 = high_030 + 1 if risk > 0.3 else 0", source)
        self.assertIn("high_050 = high_050 + 1 if risk > 0.5 else 0", source)
        self.assertIn("high_070 = high_070 + 1 if risk > 0.7 else 0", source)
        self.assertIn("multiplier = min(multiplier, 0.5)", source)
        self.assertIn("multiplier = min(multiplier, 0.25)", source)
        self.assertIn("multiplier = min(multiplier, 0.1)", source)

    def test_trade_match_inclusive_window_merge_and_default_multiplier_are_bound(self) -> None:
        source = ast.unparse(_trade_loop())
        self.assertIn("life['entry_timestamp_utc'] == entry_ts", source)
        self.assertIn("life['side'].astype(str).str.lower() == side", source)
        self.assertIn("shadow['timestamp_utc'] >= entry_ts", source)
        self.assertIn("shadow['timestamp_utc'] <= exit_ts", source)
        self.assertIn("if len(life_trade) == 0 or len(shadow_trade) == 0:", source)
        self.assertIn("multiplier = 1.0", source)
        merge_calls = [
            node
            for node in ast.walk(_trade_loop())
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "merge_asof"
        ]
        self.assertEqual(len(merge_calls), 1)
        keywords = {keyword.arg: ast.unparse(keyword.value) for keyword in merge_calls[0].keywords}
        self.assertEqual(
            keywords,
            {
                "on": "'timestamp_utc'",
                "direction": "'nearest'",
                "tolerance": "pd.Timedelta('2min')",
            },
        )
        self.assertIn("merged['shadow_risk_score'] = merged['shadow_risk_score'].fillna(0.0)", source)
        self.assertIn("multiplier_from_streaks(merged['shadow_risk_score'].tolist())", source)

    def test_retroactive_scaled_pnl_row_schema_and_sort_are_bound(self) -> None:
        source = ast.unparse(_trade_loop())
        self.assertIn("original_pnl = float(trade['pnl'])", source)
        self.assertIn("scaled_pnl = original_pnl * multiplier", source)
        append_call = next(
            node
            for node in ast.walk(_trade_loop())
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "append"
        )
        row = append_call.args[0]
        self.assertIsInstance(row, ast.Dict)
        self.assertEqual(
            [ast.literal_eval(key) for key in row.keys],
            ["trade_index", "side", "original_pnl", "final_multiplier", "scaled_pnl"],
        )
        self.assertEqual(ast.unparse(row.values[0]), "int(trade['trade_index'])")
        self.assertEqual(ast.unparse(row.values[1]), "side")
        all_source = ast.unparse(_tree())
        self.assertIn("df = pd.DataFrame(rows).sort_values('trade_index')", all_source)

    def test_stats_stdout_distribution_and_writer_contract_are_bound(self) -> None:
        tree = _tree()
        function = _calc_stats_function()
        source = ast.unparse(function)
        self.assertEqual([argument.arg for argument in function.args.args], ["pnl_col"])
        self.assertIn("equity = START_CAPITAL + df[pnl_col].cumsum()", source)
        self.assertIn("peak = equity.cummax()", source)
        self.assertIn("dd_abs = peak - equity", source)
        self.assertIn("dd_pct = dd_abs / peak", source)
        self.assertIn("wins = df[df[pnl_col] > 0]", source)
        self.assertIn("losses = df[df[pnl_col] < 0]", source)
        self.assertIn("pf = gross_profit / gross_loss if gross_loss > 0 else float('inf')", source)
        returned = next(node.value for node in function.body if isinstance(node, ast.Return))
        self.assertIsInstance(returned, ast.Dict)
        self.assertEqual(
            [ast.literal_eval(key) for key in returned.keys],
            [
                "final_equity",
                "total_pnl",
                "return_pct",
                "winrate",
                "profit_factor",
                "max_drawdown_abs",
                "max_drawdown_pct",
            ],
        )
        calls = [
            ast.literal_eval(node.value.args[0])
            for node in tree.body
            if isinstance(node, ast.Assign)
            and isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Name)
            and node.value.func.id == "calc_stats"
        ]
        self.assertEqual(calls, ["original_pnl", "scaled_pnl"])
        all_source = ast.unparse(tree)
        self.assertIn("df['final_multiplier'].value_counts().sort_index()", all_source)

        out_assignment = next(
            node
            for node in tree.body
            if isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id == "out"
        )
        self.assertEqual(ast.literal_eval(out_assignment.value), OUTPUT.as_posix())
        writes = [
            node
            for node in tree.body
            if isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Attribute)
            and node.value.func.attr == "to_csv"
        ]
        self.assertEqual(len(writes), 1)
        self.assertEqual(ast.unparse(writes[0].value.args[0]), "out")
        self.assertEqual([(keyword.arg, ast.literal_eval(keyword.value)) for keyword in writes[0].value.keywords], [("index", False)])
        self.assertEqual(
            [
                node
                for node in ast.walk(tree)
                if isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "mkdir"
            ],
            [],
        )

    @unittest.skipUnless(FULL_RUNTIME_AVAILABLE, "pandas fixture runtime required")
    def test_successful_fixture_stdout_csv_and_input_nonmutation_are_bound(self) -> None:
        expected_stdout = (
            "\n"
            "---- STEP20D DYNAMIC EXPOSURE SCALING ----\n"
            "trades: 4\n"
            "\n"
            "ORIGINAL\n"
            "final_equity: 10040.0\n"
            "total_pnl: 40.0\n"
            "return_pct: 0.004\n"
            "winrate: 0.5\n"
            "profit_factor: 1.4\n"
            "max_drawdown_abs: 80.0\n"
            "max_drawdown_pct: 0.0079\n"
            "\n"
            "STEP20D\n"
            "final_equity: 10014.0\n"
            "total_pnl: 14.0\n"
            "return_pct: 0.0014\n"
            "winrate: 0.5\n"
            "profit_factor: 1.35\n"
            "max_drawdown_abs: 36.0\n"
            "max_drawdown_pct: 0.0036\n"
            "\n"
            "FINAL MULTIPLIER DISTRIBUTION\n"
            "final_multiplier\n"
            "0.10    1\n"
            "0.25    1\n"
            "0.50    1\n"
            "1.00    1\n"
            "Name: count, dtype: int64\n"
            "\n"
            f"written: {OUTPUT.as_posix()}\n"
        )
        with tempfile.TemporaryDirectory(prefix="step20d_dynamic_exposure_success_") as temp_dir:
            root = Path(temp_dir)
            _write_csv(root / TRADES_INPUT, TRADES_ROWS)
            _write_csv(root / LIFECYCLE_INPUT, LIFECYCLE_ROWS)
            _write_csv(root / SHADOW_INPUT, SHADOW_ROWS)
            (root / OUTPUT.parent).mkdir(parents=True)
            before = _manifest(root)
            result = _run(root)
            after = _manifest(root)
            rows = _read_csv(root / OUTPUT)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertEqual(result.stdout, expected_stdout)
        self.assertEqual({path: after[path] for path in before}, before)
        self.assertIn(OUTPUT.as_posix(), after)
        self.assertEqual([row["trade_index"] for row in rows], ["1", "2", "3", "4"])
        self.assertEqual([row["side"] for row in rows], ["long", "short", "long", "short"])
        self.assertEqual([row["original_pnl"] for row in rows], ["100.0", "-80.0", "40.0", "-20.0"])
        self.assertEqual([row["final_multiplier"] for row in rows], ["0.5", "0.25", "0.1", "1.0"])
        self.assertEqual([row["scaled_pnl"] for row in rows], ["50.0", "-20.0", "4.0", "-20.0"])

    @unittest.skipUnless(FULL_RUNTIME_AVAILABLE, "pandas fixture runtime required")
    def test_missing_inputs_fail_closed_in_fixed_read_order(self) -> None:
        stages = (
            ((), TRADES_INPUT),
            (((TRADES_INPUT, TRADES_ROWS),), LIFECYCLE_INPUT),
            (((TRADES_INPUT, TRADES_ROWS), (LIFECYCLE_INPUT, LIFECYCLE_ROWS)), SHADOW_INPUT),
        )
        for provided, missing in stages:
            with self.subTest(missing=missing.as_posix()):
                with tempfile.TemporaryDirectory(prefix="step20d_dynamic_exposure_missing_") as temp_dir:
                    root = Path(temp_dir)
                    for path, rows in provided:
                        _write_csv(root / path, rows)
                    before = _manifest(root)
                    before_directories = _directories(root)
                    result = _run(root)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertEqual(result.stdout, "")
                    self.assertIn("FileNotFoundError", result.stderr)
                    self.assertIn(missing.as_posix(), result.stderr.replace("\\", "/"))
                    self.assertEqual(_manifest(root), before)
                    self.assertEqual(_directories(root), before_directories)

    @unittest.skipUnless(FULL_RUNTIME_AVAILABLE, "pandas fixture runtime required")
    def test_empty_trades_fail_before_stdout_and_without_mutation(self) -> None:
        with tempfile.TemporaryDirectory(prefix="step20d_dynamic_exposure_empty_") as temp_dir:
            root = Path(temp_dir)
            _write_header(root / TRADES_INPUT, tuple(TRADES_ROWS[0]))
            _write_csv(root / LIFECYCLE_INPUT, LIFECYCLE_ROWS)
            _write_csv(root / SHADOW_INPUT, SHADOW_ROWS)
            before = _manifest(root)
            before_directories = _directories(root)
            result = _run(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "")
            self.assertIn("KeyError", result.stderr)
            self.assertIn("trade_index", result.stderr)
            self.assertEqual(_manifest(root), before)
            self.assertEqual(_directories(root), before_directories)

    @unittest.skipUnless(FULL_RUNTIME_AVAILABLE, "pandas fixture runtime required")
    def test_missing_output_directory_fails_after_stats_before_written_line(self) -> None:
        with tempfile.TemporaryDirectory(prefix="step20d_dynamic_exposure_missing_output_") as temp_dir:
            root = Path(temp_dir)
            _write_csv(root / TRADES_INPUT, TRADES_ROWS)
            _write_csv(root / LIFECYCLE_INPUT, LIFECYCLE_ROWS)
            _write_csv(root / SHADOW_INPUT, SHADOW_ROWS)
            before = _manifest(root)
            before_directories = _directories(root)
            result = _run(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertTrue(result.stdout.startswith("\n---- STEP20D DYNAMIC EXPOSURE SCALING ----\n"))
            self.assertIn("FINAL MULTIPLIER DISTRIBUTION", result.stdout)
            self.assertNotIn("written:", result.stdout)
            self.assertIn("OSError", result.stderr)
            self.assertIn(OUTPUT.parent.as_posix(), result.stderr.replace("\\", "/"))
            self.assertEqual(_manifest(root), before)
            self.assertEqual(_directories(root), before_directories)

    @unittest.skipUnless(FULL_RUNTIME_AVAILABLE, "pandas fixture runtime required")
    def test_malformed_first_timestamp_fails_before_stdout_and_without_mutation(self) -> None:
        malformed_trades = tuple(dict(row) for row in TRADES_ROWS)
        malformed_trades[0]["entry_timestamp_utc"] = "not-a-timestamp"
        with tempfile.TemporaryDirectory(prefix="step20d_dynamic_exposure_bad_time_") as temp_dir:
            root = Path(temp_dir)
            _write_csv(root / TRADES_INPUT, malformed_trades)
            _write_csv(root / LIFECYCLE_INPUT, LIFECYCLE_ROWS)
            _write_csv(root / SHADOW_INPUT, SHADOW_ROWS)
            before = _manifest(root)
            before_directories = _directories(root)
            result = _run(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "")
            self.assertIn("DateParseError", result.stderr)
            self.assertIn("not-a-timestamp", result.stderr)
            self.assertEqual(_manifest(root), before)
            self.assertEqual(_directories(root), before_directories)


if __name__ == "__main__":
    unittest.main()
