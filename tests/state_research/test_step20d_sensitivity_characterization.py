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
SCRIPT = REPO_ROOT / "scripts" / "state_research" / "analyze_step20D_sensitivity.py"

TRADES_INPUT = Path("live_logs/trades_l1_auto_analysis.csv")
LIFECYCLE_INPUT = Path("live_logs/trade_lifecycle_snapshots.csv")
SHADOW_INPUT = Path("live_logs/passive_shadow_risk_snapshots.csv")

SOURCE_SHA256 = "49f37fe4d47e3205e4f6b1eb57cc67330fe2a81258f18d832aa3b849268e7636"
SOURCE_LINES = 97
START_CAPITAL = 10000.0
CONFIGS = [
    ("D1", 0.50, 0.25, 0.10),
    ("D2", 0.75, 0.50, 0.25),
    ("D3", 1.00, 0.50, 0.25),
]

FULL_RUNTIME_AVAILABLE = importlib.util.find_spec("pandas") is not None

TRADES_ROWS = (
    {
        "entry_timestamp_utc": "2026-01-01T00:00:00Z",
        "exit_timestamp_utc": "2026-01-01T00:02:00Z",
        "side": "LONG",
        "pnl": "100",
    },
    {
        "entry_timestamp_utc": "2026-01-01T00:10:00Z",
        "exit_timestamp_utc": "2026-01-01T00:12:00Z",
        "side": "SHORT",
        "pnl": "-80",
    },
    {
        "entry_timestamp_utc": "2026-01-01T00:20:00Z",
        "exit_timestamp_utc": "2026-01-01T00:22:00Z",
        "side": "LONG",
        "pnl": "40",
    },
    {
        "entry_timestamp_utc": "2026-01-01T00:30:00Z",
        "exit_timestamp_utc": "2026-01-01T00:32:00Z",
        "side": "SHORT",
        "pnl": "-20",
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


def _get_multiplier_function() -> ast.FunctionDef:
    functions = [
        node
        for node in _tree().body
        if isinstance(node, ast.FunctionDef) and node.name == "get_multiplier"
    ]
    if len(functions) != 1:
        raise AssertionError(f"expected one get_multiplier function, found {len(functions)}")
    return functions[0]


def _config_loop() -> ast.For:
    loops = [
        node
        for node in _tree().body
        if isinstance(node, ast.For)
        and isinstance(node.target, ast.Tuple)
        and [ast.unparse(item) for item in node.target.elts] == ["name", "m030", "m050", "m070"]
    ]
    if len(loops) != 1:
        raise AssertionError(f"expected one config loop, found {len(loops)}")
    return loops[0]


def _trade_loop() -> ast.For:
    loops = [
        node
        for node in _config_loop().body
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


class Step20DSensitivityCharacterizationTests(unittest.TestCase):
    maxDiff = None

    def test_source_identity_constants_and_import_time_executor_are_bound(self) -> None:
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
            and target.id in {"START_CAPITAL", "configs"}
        }
        self.assertEqual(assignments, {"START_CAPITAL": START_CAPITAL, "configs": CONFIGS})
        self.assertEqual([node.name for node in tree.body if isinstance(node, ast.FunctionDef)], ["get_multiplier"])
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
        function = _get_multiplier_function()
        namespace: dict[str, object] = {}
        module = ast.fix_missing_locations(ast.Module(body=[function], type_ignores=[]))
        exec(compile(module, str(SCRIPT), "exec"), namespace)
        get_multiplier = namespace["get_multiplier"]
        self.assertEqual(get_multiplier([0.30, 0.30, 0.30], 0.5, 0.25, 0.1), 1.0)
        self.assertEqual(get_multiplier([0.31, 0.31, 0.31], 0.5, 0.25, 0.1), 0.5)
        self.assertEqual(get_multiplier([0.51, 0.51, 0.51], 0.75, 0.5, 0.25), 0.5)
        self.assertEqual(get_multiplier([0.71, 0.71, 0.71], 1.0, 0.5, 0.25), 0.25)
        self.assertEqual(get_multiplier([0.31, 0.31, 0.30, 0.31, 0.31], 0.5, 0.25, 0.1), 1.0)
        self.assertEqual(get_multiplier([0.71, 0.71, 0.71, 0.0, 0.0, 0.0], 0.5, 0.25, 0.1), 0.1)
        source = ast.unparse(function)
        self.assertIn("s030 = s030 + 1 if r > 0.3 else 0", source)
        self.assertIn("s050 = s050 + 1 if r > 0.5 else 0", source)
        self.assertIn("s070 = s070 + 1 if r > 0.7 else 0", source)
        self.assertEqual(source.count("if s0"), 3)
        self.assertEqual(source.count("m = min(m,"), 3)

    def test_trade_match_shadow_window_merge_and_default_multiplier_are_bound(self) -> None:
        source = ast.unparse(_trade_loop())
        self.assertIn("life['entry_timestamp_utc'] == entry_ts", source)
        self.assertIn("life['side'].astype(str).str.lower() == side", source)
        self.assertIn("shadow['timestamp_utc'] >= entry_ts", source)
        self.assertIn("shadow['timestamp_utc'] <= exit_ts", source)
        self.assertIn("if len(life_trade) == 0 or len(shadow_trade) == 0:\n        mult = 1.0", source)
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

    def test_retroactive_scaled_pnl_row_schema_and_metrics_are_bound(self) -> None:
        loop = _config_loop()
        source = ast.unparse(loop)
        self.assertIn("'pnl': float(trade['pnl']) * mult", source)
        self.assertIn("'mult': mult", source)
        self.assertIn("equity = START_CAPITAL + df['pnl'].cumsum()", source)
        self.assertIn("peak = equity.cummax()", source)
        self.assertIn("dd_pct = ((peak - equity) / peak).max()", source)
        self.assertIn("wins = df[df['pnl'] > 0]", source)
        self.assertIn("losses = df[df['pnl'] < 0]", source)
        self.assertIn("pf = gp / gl if gl > 0 else float('inf')", source)
        self.assertIn("vc = df['mult'].value_counts()", source)
        append_call = next(
            node
            for node in ast.walk(_trade_loop())
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "append"
        )
        row = append_call.args[0]
        self.assertIsInstance(row, ast.Dict)
        self.assertEqual([ast.literal_eval(key) for key in row.keys], ["pnl", "mult"])

    def test_stdout_header_precision_distribution_order_and_no_writer_are_bound(self) -> None:
        print_calls = [
            node.value
            for node in ast.walk(_tree())
            if isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Name)
            and node.value.func.id == "print"
        ]
        self.assertEqual(len(print_calls), 2)
        self.assertEqual(
            ast.literal_eval(print_calls[0].args[0]),
            "config,total_pnl,pf,max_dd_pct,m_010,m_025,m_050,m_075,m_100",
        )
        formatted = ast.unparse(print_calls[1])
        self.assertIn("df['pnl'].sum():.2f", formatted)
        self.assertIn("pf:.4f", formatted)
        self.assertIn("dd_pct:.4f", formatted)
        self.assertLess(formatted.index("vc.get(0.1, 0)"), formatted.index("vc.get(0.25, 0)"))
        self.assertLess(formatted.index("vc.get(0.25, 0)"), formatted.index("vc.get(0.5, 0)"))
        self.assertLess(formatted.index("vc.get(0.5, 0)"), formatted.index("vc.get(0.75, 0)"))
        self.assertLess(formatted.index("vc.get(0.75, 0)"), formatted.index("vc.get(1.0, 0)"))
        writers = [
            node
            for node in ast.walk(_tree())
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr in {"to_csv", "to_json", "write_text", "write_bytes"}
        ]
        self.assertEqual(writers, [])

    @unittest.skipUnless(FULL_RUNTIME_AVAILABLE, "pandas fixture runtime required")
    def test_successful_fixture_stdout_and_input_nonmutation_are_bound(self) -> None:
        expected_stdout = (
            "config,total_pnl,pf,max_dd_pct,m_010,m_025,m_050,m_075,m_100\n"
            "D1,14.00,1.3500,0.0036,1,1,1,0,1\n"
            "D2,25.00,1.4167,0.0050,0,1,1,1,1\n"
            "D3,50.00,1.8333,0.0050,0,1,1,0,2\n"
        )
        with tempfile.TemporaryDirectory(prefix="step20d_sensitivity_success_") as temp_dir:
            root = Path(temp_dir)
            _write_csv(root / TRADES_INPUT, TRADES_ROWS)
            _write_csv(root / LIFECYCLE_INPUT, LIFECYCLE_ROWS)
            _write_csv(root / SHADOW_INPUT, SHADOW_ROWS)
            before = _manifest(root)
            before_directories = _directories(root)
            result = _run(root)
            after = _manifest(root)
            after_directories = _directories(root)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertEqual(result.stdout, expected_stdout)
        self.assertEqual(after, before)
        self.assertEqual(after_directories, before_directories)

    @unittest.skipUnless(FULL_RUNTIME_AVAILABLE, "pandas fixture runtime required")
    def test_missing_inputs_fail_closed_in_fixed_read_order(self) -> None:
        stages = (
            ((), TRADES_INPUT),
            (((TRADES_INPUT, TRADES_ROWS),), LIFECYCLE_INPUT),
            (((TRADES_INPUT, TRADES_ROWS), (LIFECYCLE_INPUT, LIFECYCLE_ROWS)), SHADOW_INPUT),
        )
        for provided, missing in stages:
            with self.subTest(missing=missing.as_posix()):
                with tempfile.TemporaryDirectory(prefix="step20d_sensitivity_missing_") as temp_dir:
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
    def test_empty_trades_fail_after_header_without_filesystem_mutation(self) -> None:
        with tempfile.TemporaryDirectory(prefix="step20d_sensitivity_empty_") as temp_dir:
            root = Path(temp_dir)
            _write_header(root / TRADES_INPUT, tuple(TRADES_ROWS[0]))
            _write_csv(root / LIFECYCLE_INPUT, LIFECYCLE_ROWS)
            _write_csv(root / SHADOW_INPUT, SHADOW_ROWS)
            before = _manifest(root)
            before_directories = _directories(root)
            result = _run(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(
                result.stdout,
                "config,total_pnl,pf,max_dd_pct,m_010,m_025,m_050,m_075,m_100\n",
            )
            self.assertIn("KeyError", result.stderr)
            self.assertIn("pnl", result.stderr)
            self.assertEqual(_manifest(root), before)
            self.assertEqual(_directories(root), before_directories)

    @unittest.skipUnless(FULL_RUNTIME_AVAILABLE, "pandas fixture runtime required")
    def test_malformed_first_timestamp_fails_before_header_and_without_mutation(self) -> None:
        malformed_trades = tuple(dict(row) for row in TRADES_ROWS)
        malformed_trades[0]["entry_timestamp_utc"] = "not-a-timestamp"
        with tempfile.TemporaryDirectory(prefix="step20d_sensitivity_bad_time_") as temp_dir:
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
