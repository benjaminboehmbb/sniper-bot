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
SCRIPT = REPO_ROOT / "scripts" / "state_research" / "analyze_step19B_real_exit_replay.py"

TRADES_INPUT = Path("live_logs/trades_l1_auto_analysis.csv")
LIFECYCLE_INPUT = Path("live_logs/trade_lifecycle_snapshots.csv")
SHADOW_INPUT = Path("live_logs/passive_shadow_risk_snapshots.csv")
OUTPUT = Path("reports/step18/step19B_real_exit_replay.csv")

SOURCE_SHA256 = "414fe6edbf7a315351b86f9973f2c633c0a055e448c30352ffe300c896686ffc"
SOURCE_LINES = 115
START_CAPITAL = 10000.0
THRESHOLD = 0.50
CONSECUTIVE = 3

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
        "pnl": "30",
    },
    {
        "trade_index": "2",
        "entry_timestamp_utc": "2026-01-01T00:10:00Z",
        "exit_timestamp_utc": "2026-01-01T00:12:00Z",
        "side": "SHORT",
        "pnl": "-40",
    },
)

LIFECYCLE_ROWS = (
    {"timestamp_utc": "2026-01-01T00:00:00Z", "entry_timestamp_utc": "2026-01-01T00:00:00Z", "side": "long", "entry_price": "100", "current_price": "99", "position_size": "2"},
    {"timestamp_utc": "2026-01-01T00:01:00Z", "entry_timestamp_utc": "2026-01-01T00:00:00Z", "side": "LONG", "entry_price": "100", "current_price": "98", "position_size": "2"},
    {"timestamp_utc": "2026-01-01T00:02:00Z", "entry_timestamp_utc": "2026-01-01T00:00:00Z", "side": "Long", "entry_price": "100", "current_price": "97", "position_size": "2"},
    {"timestamp_utc": "2026-01-01T00:10:00Z", "entry_timestamp_utc": "2026-01-01T00:10:00Z", "side": "short", "entry_price": "100", "current_price": "101", "position_size": "3"},
    {"timestamp_utc": "2026-01-01T00:11:00Z", "entry_timestamp_utc": "2026-01-01T00:10:00Z", "side": "SHORT", "entry_price": "100", "current_price": "102", "position_size": "3"},
    {"timestamp_utc": "2026-01-01T00:12:00Z", "entry_timestamp_utc": "2026-01-01T00:10:00Z", "side": "Short", "entry_price": "100", "current_price": "103", "position_size": "3"},
    {"timestamp_utc": "2026-01-01T00:30:00Z", "entry_timestamp_utc": "2026-01-01T00:30:00Z", "side": "short", "entry_price": "100", "current_price": "99", "position_size": "1"},
)

SHADOW_ROWS = (
    {"timestamp_utc": "2026-01-01T00:00:00Z", "shadow_risk_score": "0.51"},
    {"timestamp_utc": "2026-01-01T00:01:00Z", "shadow_risk_score": "0.51"},
    {"timestamp_utc": "2026-01-01T00:02:00Z", "shadow_risk_score": "0.51"},
    {"timestamp_utc": "2026-01-01T00:10:00Z", "shadow_risk_score": "0.50"},
    {"timestamp_utc": "2026-01-01T00:11:00Z", "shadow_risk_score": "0.50"},
    {"timestamp_utc": "2026-01-01T00:12:00Z", "shadow_risk_score": "0.50"},
    {"timestamp_utc": "2026-01-01T00:20:00Z", "shadow_risk_score": "0.80"},
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


class Step19BRealExitReplayCharacterizationTests(unittest.TestCase):
    maxDiff = None

    def test_source_identity_constants_and_import_time_executor_are_bound(self) -> None:
        raw = SCRIPT.read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), SOURCE_SHA256)
        self.assertEqual(len(raw.decode("utf-8").splitlines()), SOURCE_LINES)
        assignments = {
            target.id: ast.literal_eval(node.value)
            for node in _tree().body
            if isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance((target := node.targets[0]), ast.Name)
            and target.id in {"START_CAPITAL", "THRESHOLD", "CONSECUTIVE"}
        }
        self.assertEqual(
            assignments,
            {
                "START_CAPITAL": START_CAPITAL,
                "THRESHOLD": THRESHOLD,
                "CONSECUTIVE": CONSECUTIVE,
            },
        )
        self.assertEqual([node for node in _tree().body if isinstance(node, ast.FunctionDef)], [])
        self.assertEqual([node for node in _tree().body if _is_main_guard(node)], [])

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

    def test_trade_match_inclusive_window_merge_and_missing_match_exit_are_bound(self) -> None:
        source = ast.unparse(_trade_loop())
        self.assertIn("life['entry_timestamp_utc'] == entry_ts", source)
        self.assertIn("life['side'].astype(str).str.lower() == side", source)
        self.assertIn("shadow['timestamp_utc'] >= entry_ts", source)
        self.assertIn("shadow['timestamp_utc'] <= exit_ts", source)
        self.assertIn("if len(life_trade) == 0 or len(shadow_trade) == 0", source)
        self.assertIn("replay_pnl = float(trade['pnl'])", source)
        self.assertIn("exit_type = 'ORIGINAL_NO_LIFECYCLE'", source)
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

    def test_strict_high_streak_first_trigger_and_exit_types_are_bound(self) -> None:
        source = ast.unparse(_trade_loop())
        self.assertIn("merged['high'] = merged['shadow_risk_score'] > THRESHOLD", source)
        self.assertIn("merged['high'].astype(int).groupby((merged['high'] != merged['high'].shift()).cumsum()).cumsum()", source)
        self.assertIn("trigger = merged[merged['streak'] >= CONSECUTIVE]", source)
        self.assertIn("row = trigger.iloc[0]", source)
        self.assertIn("exit_type = 'STEP19B_DYNAMIC_EXIT'", source)
        self.assertIn("exit_type = 'ORIGINAL_EXIT'", source)

    def test_trigger_price_side_formula_and_output_row_schema_are_bound(self) -> None:
        source = ast.unparse(_trade_loop())
        self.assertIn("entry_price = float(row['entry_price'])", source)
        self.assertIn("exit_price = float(row['current_price'])", source)
        self.assertIn("size = float(row['position_size'])", source)
        self.assertIn("if side == 'long':", source)
        self.assertIn("replay_pnl = (exit_price - entry_price) * size", source)
        self.assertIn("else:", source)
        self.assertIn("replay_pnl = (entry_price - exit_price) * size", source)
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
            ["trade_index", "side", "original_pnl", "replay_pnl", "exit_type"],
        )
        self.assertEqual(ast.unparse(row.values[0]), "int(trade['trade_index'])")
        self.assertEqual(ast.unparse(row.values[1]), "side")
        self.assertEqual(ast.unparse(row.values[2]), "float(trade['pnl'])")

    def test_sort_metrics_stdout_groupby_and_writer_contract_are_bound(self) -> None:
        tree = _tree()
        source = ast.unparse(tree)
        self.assertIn("df = pd.DataFrame(rows).sort_values('trade_index')", source)
        self.assertIn("df['win'] = (df['replay_pnl'] > 0).astype(int)", source)
        self.assertIn("df['equity'] = START_CAPITAL + df['replay_pnl'].cumsum()", source)
        self.assertIn("df['peak'] = df['equity'].cummax()", source)
        self.assertIn("df['dd_abs'] = df['peak'] - df['equity']", source)
        self.assertIn("df['dd_pct'] = df['dd_abs'] / df['peak']", source)
        self.assertIn("wins = df[df['replay_pnl'] > 0]", source)
        self.assertIn("losses = df[df['replay_pnl'] < 0]", source)
        self.assertIn("pf = gross_profit / gross_loss if gross_loss > 0 else float('inf')", source)
        self.assertIn("df.groupby('exit_type')['replay_pnl'].agg(['count', 'mean', 'sum'])", source)

        print_labels = [
            ast.literal_eval(node.value.args[0])
            for node in tree.body
            if isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Name)
            and node.value.func.id == "print"
            and node.value.args
            and isinstance(node.value.args[0], ast.Constant)
        ]
        self.assertEqual(
            print_labels,
            [
                "---- STEP19B REAL EXIT REPLAY ----",
                "threshold:",
                "consecutive:",
                "trades:",
                "dynamic_exits:",
                "final_equity:",
                "total_pnl:",
                "return_pct:",
                "winrate:",
                "profit_factor:",
                "max_drawdown_abs:",
                "max_drawdown_pct:",
                "written:",
            ],
        )
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
            "---- STEP19B REAL EXIT REPLAY ----\n"
            "threshold: 0.5\n"
            "consecutive: 3\n"
            "trades: 4\n"
            "dynamic_exits: 1\n"
            "final_equity: 9964.0\n"
            "total_pnl: -36.0\n"
            "return_pct: -0.0036\n"
            "winrate: 0.25\n"
            "profit_factor: 0.4545\n"
            "max_drawdown_abs: 40.0\n"
            "max_drawdown_pct: 0.004\n"
            "\n"
            "                       count  mean   sum\n"
            "exit_type                               \n"
            "ORIGINAL_EXIT              1 -40.0 -40.0\n"
            "ORIGINAL_NO_LIFECYCLE      2   5.0  10.0\n"
            "STEP19B_DYNAMIC_EXIT       1  -6.0  -6.0\n"
            "\n"
            f"written: {OUTPUT.as_posix()}\n"
        )
        with tempfile.TemporaryDirectory(prefix="step19b_real_exit_success_") as temp_dir:
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
        self.assertEqual([row["original_pnl"] for row in rows], ["100.0", "-40.0", "30.0", "-20.0"])
        self.assertEqual([row["replay_pnl"] for row in rows], ["-6.0", "-40.0", "30.0", "-20.0"])
        self.assertEqual(
            [row["exit_type"] for row in rows],
            [
                "STEP19B_DYNAMIC_EXIT",
                "ORIGINAL_EXIT",
                "ORIGINAL_NO_LIFECYCLE",
                "ORIGINAL_NO_LIFECYCLE",
            ],
        )
        self.assertEqual([row["win"] for row in rows], ["0", "0", "1", "0"])

    @unittest.skipUnless(FULL_RUNTIME_AVAILABLE, "pandas fixture runtime required")
    def test_missing_inputs_fail_closed_in_fixed_read_order(self) -> None:
        stages = (
            ((), TRADES_INPUT),
            (((TRADES_INPUT, TRADES_ROWS),), LIFECYCLE_INPUT),
            (((TRADES_INPUT, TRADES_ROWS), (LIFECYCLE_INPUT, LIFECYCLE_ROWS)), SHADOW_INPUT),
        )
        for provided, missing in stages:
            with self.subTest(missing=missing.as_posix()):
                with tempfile.TemporaryDirectory(prefix="step19b_real_exit_missing_") as temp_dir:
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
        with tempfile.TemporaryDirectory(prefix="step19b_real_exit_empty_") as temp_dir:
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
        with tempfile.TemporaryDirectory(prefix="step19b_real_exit_missing_output_") as temp_dir:
            root = Path(temp_dir)
            _write_csv(root / TRADES_INPUT, TRADES_ROWS)
            _write_csv(root / LIFECYCLE_INPUT, LIFECYCLE_ROWS)
            _write_csv(root / SHADOW_INPUT, SHADOW_ROWS)
            before = _manifest(root)
            before_directories = _directories(root)
            result = _run(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertTrue(result.stdout.startswith("\n---- STEP19B REAL EXIT REPLAY ----\n"))
            self.assertIn("STEP19B_DYNAMIC_EXIT", result.stdout)
            self.assertNotIn("written:", result.stdout)
            self.assertIn("OSError", result.stderr)
            self.assertIn(OUTPUT.parent.as_posix(), result.stderr.replace("\\", "/"))
            self.assertEqual(_manifest(root), before)
            self.assertEqual(_directories(root), before_directories)

    @unittest.skipUnless(FULL_RUNTIME_AVAILABLE, "pandas fixture runtime required")
    def test_malformed_first_timestamp_fails_before_stdout_and_without_mutation(self) -> None:
        malformed_trades = tuple(dict(row) for row in TRADES_ROWS)
        malformed_trades[0]["entry_timestamp_utc"] = "not-a-timestamp"
        with tempfile.TemporaryDirectory(prefix="step19b_real_exit_bad_time_") as temp_dir:
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
