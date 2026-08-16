from __future__ import annotations

import ast
import contextlib
import csv
import hashlib
import importlib.util
import io
import os
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "state_research" / "analyze_step19_dynamic_exit_replay.py"

TRADES_INPUT = Path("live_logs/trades_l1_auto_analysis.csv")
SHADOW_INPUT = Path("live_logs/passive_shadow_risk_snapshots.csv")

SOURCE_SHA256 = "c7b95427b3b7e3ca52b840011cb30949d8ca17f64f48b9417a7c325e3a1a7fa1"
SOURCE_LINES = 82
RUNTIME_AST_SHA256 = "729083ca5488e5710533e1497950e4de493c6145ba7cfb4aabb3253ef7560a50"
SUCCESS_STDOUT_SHA256 = "a8c1b354dc05d20484944afda1a9fe50641e82bb63acd478669987d58b9cfcc2"
START_CAPITAL = 10000.0
CONFIGS = [
    {"threshold": 0.50, "consecutive": 3},
    {"threshold": 0.50, "consecutive": 5},
    {"threshold": 0.60, "consecutive": 3},
    {"threshold": 0.60, "consecutive": 5},
]
HEADER = "threshold,consecutive,trades,early_exits,total_pnl,winrate,pf,max_dd_pct"

FULL_RUNTIME_AVAILABLE = importlib.util.find_spec("pandas") is not None

TRADES_ROWS = (
    {
        "trade_index": "1",
        "entry_timestamp_utc": "2026-01-01T00:01:00Z",
        "exit_timestamp_utc": "2026-01-01T00:03:00Z",
        "pnl": "100",
    },
    {
        "trade_index": "2",
        "entry_timestamp_utc": "2026-01-01T00:11:00Z",
        "exit_timestamp_utc": "2026-01-01T00:13:00Z",
        "pnl": "-40",
    },
    {
        "trade_index": "3",
        "entry_timestamp_utc": "2026-01-01T00:21:00Z",
        "exit_timestamp_utc": "2026-01-01T00:25:00Z",
        "pnl": "60",
    },
    {
        "trade_index": "4",
        "entry_timestamp_utc": "2026-01-01T00:31:00Z",
        "exit_timestamp_utc": "2026-01-01T00:33:00Z",
        "pnl": "-20",
    },
    {
        "trade_index": "5",
        "entry_timestamp_utc": "2026-01-01T00:41:00Z",
        "exit_timestamp_utc": "2026-01-01T00:45:00Z",
        "pnl": "0",
    },
    {
        "trade_index": "6",
        "entry_timestamp_utc": "2026-01-02T00:00:00Z",
        "exit_timestamp_utc": "2026-01-02T00:01:00Z",
        "pnl": "999",
    },
)

SHADOW_ROWS = (
    {"timestamp_utc": "2026-01-01T00:01:00Z", "shadow_risk_score": "0.51"},
    {"timestamp_utc": "2026-01-01T00:02:00Z", "shadow_risk_score": "0.52"},
    {"timestamp_utc": "2026-01-01T00:03:00Z", "shadow_risk_score": "0.53"},
    {"timestamp_utc": "2026-01-01T00:11:00Z", "shadow_risk_score": "0.61"},
    {"timestamp_utc": "2026-01-01T00:12:00Z", "shadow_risk_score": "0.61"},
    {"timestamp_utc": "2026-01-01T00:13:00Z", "shadow_risk_score": "0.61"},
    {"timestamp_utc": "2026-01-01T00:21:00Z", "shadow_risk_score": "0.61"},
    {"timestamp_utc": "2026-01-01T00:22:00Z", "shadow_risk_score": "0.61"},
    {"timestamp_utc": "2026-01-01T00:23:00Z", "shadow_risk_score": "0.61"},
    {"timestamp_utc": "2026-01-01T00:24:00Z", "shadow_risk_score": "0.61"},
    {"timestamp_utc": "2026-01-01T00:25:00Z", "shadow_risk_score": "0.61"},
    {"timestamp_utc": "2026-01-01T00:31:00Z", "shadow_risk_score": "0.50"},
    {"timestamp_utc": "2026-01-01T00:32:00Z", "shadow_risk_score": "0.60"},
    {"timestamp_utc": "2026-01-01T00:33:00Z", "shadow_risk_score": "0.50"},
    {"timestamp_utc": "2026-01-01T00:41:00Z", "shadow_risk_score": "0.70"},
    {"timestamp_utc": "2026-01-01T00:42:00Z", "shadow_risk_score": "0.70"},
    {"timestamp_utc": "2026-01-01T00:43:00Z", "shadow_risk_score": "0.40"},
    {"timestamp_utc": "2026-01-01T00:44:00Z", "shadow_risk_score": "0.70"},
    {"timestamp_utc": "2026-01-01T00:45:00Z", "shadow_risk_score": "0.70"},
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


def _main_function() -> ast.FunctionDef:
    functions = [
        node
        for node in _tree().body
        if isinstance(node, ast.FunctionDef) and node.name == "main"
    ]
    if len(functions) != 1:
        raise AssertionError(f"expected one main function, found {len(functions)}")
    return functions[0]


def _runtime_ast_sha256() -> str:
    runtime_module = ast.Module(body=_main_function().body, type_ignores=[])
    payload = ast.dump(runtime_module, include_attributes=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _config_loop() -> ast.For:
    loops = [
        node
        for node in _main_function().body
        if isinstance(node, ast.For)
        and isinstance(node.target, ast.Name)
        and node.target.id == "cfg"
    ]
    if len(loops) != 1:
        raise AssertionError(f"expected one config loop, found {len(loops)}")
    return loops[0]


def _trade_loop() -> ast.For:
    loops = [
        node
        for node in _config_loop().body
        if isinstance(node, ast.For)
        and isinstance(node.target, ast.Tuple)
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


class Step19DynamicExitReplayCharacterizationTests(unittest.TestCase):
    maxDiff = None

    def test_source_identity_start_capital_and_config_order_are_bound(self) -> None:
        raw = SCRIPT.read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), SOURCE_SHA256)
        self.assertEqual(len(raw.decode("utf-8").splitlines()), SOURCE_LINES)
        assignments = {
            target.id: ast.literal_eval(node.value)
            for node in [*_tree().body, *_main_function().body]
            if isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance((target := node.targets[0]), ast.Name)
            and target.id in {"START_CAPITAL", "configs"}
        }
        self.assertEqual(
            assignments,
            {"START_CAPITAL": START_CAPITAL, "configs": CONFIGS},
        )
        loop = _config_loop()
        self.assertEqual(ast.unparse(loop.iter), "configs")
        self.assertEqual(ast.unparse(loop.body[0]), "threshold = cfg['threshold']")
        self.assertEqual(ast.unparse(loop.body[1]), "consecutive = cfg['consecutive']")

    def test_entrypoint_is_contained_with_runtime_ast_identity(self) -> None:
        tree = _tree()
        main_function = _main_function()
        guards = [node for node in tree.body if _is_main_guard(node)]
        self.assertEqual(len(guards), 1)
        self.assertIsInstance(main_function.returns, ast.Constant)
        self.assertIsNone(main_function.returns.value)
        self.assertEqual(main_function.args.posonlyargs, [])
        self.assertEqual(main_function.args.args, [])
        self.assertEqual(main_function.args.kwonlyargs, [])
        self.assertIsNone(main_function.args.vararg)
        self.assertIsNone(main_function.args.kwarg)
        self.assertEqual(len(guards[0].body), 1)
        guard_call = guards[0].body[0]
        self.assertIsInstance(guard_call, ast.Expr)
        self.assertIsInstance(guard_call.value, ast.Call)
        self.assertIsInstance(guard_call.value.func, ast.Name)
        self.assertEqual(guard_call.value.func.id, "main")
        self.assertEqual(guard_call.value.args, [])
        self.assertEqual(guard_call.value.keywords, [])
        self.assertEqual(_runtime_ast_sha256(), RUNTIME_AST_SHA256)

        top_level_reads = [
            node
            for node in tree.body
            if isinstance(node, ast.Assign)
            and isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Attribute)
            and node.value.func.attr == "read_csv"
        ]
        top_level_calls = [
            node
            for node in tree.body
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call)
        ]
        self.assertEqual(top_level_reads, [])
        self.assertEqual(top_level_calls, [])

        writer_calls = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and (
                (
                    isinstance(node.func, ast.Attribute)
                    and node.func.attr
                    in {"mkdir", "open", "to_csv", "to_json", "write_bytes", "write_text"}
                )
                or (isinstance(node.func, ast.Name) and node.func.id == "open")
            )
        ]
        self.assertEqual(writer_calls, [])

    def test_fixed_read_conversion_and_header_order_are_bound(self) -> None:
        body = _main_function().body
        reads = [
            ast.literal_eval(node.value.args[0])
            for node in body
            if isinstance(node, ast.Assign)
            and isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Attribute)
            and node.value.func.attr == "read_csv"
        ]
        self.assertEqual(reads, [TRADES_INPUT.as_posix(), SHADOW_INPUT.as_posix()])
        conversions = [
            ast.literal_eval(node.value.args[0].slice)
            for node in body
            if isinstance(node, ast.Assign)
            and isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Attribute)
            and node.value.func.attr == "to_datetime"
            and isinstance(node.value.args[0], ast.Subscript)
        ]
        self.assertEqual(conversions, ["entry_timestamp_utc", "exit_timestamp_utc", "timestamp_utc"])
        header_index = next(
            index
            for index, node in enumerate(body)
            if isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Name)
            and node.value.func.id == "print"
        )
        config_loop_index = next(
            index
            for index, node in enumerate(body)
            if isinstance(node, ast.For)
            and isinstance(node.target, ast.Name)
            and node.target.id == "cfg"
        )
        self.assertEqual(ast.literal_eval(body[header_index].value.args[0]), HEADER)
        self.assertLess(header_index, config_loop_index)

    def test_inclusive_window_copy_skip_and_input_order_contract_are_bound(self) -> None:
        tree = _tree()
        window_ops = {
            type(node.ops[0])
            for node in ast.walk(_trade_loop())
            if isinstance(node, ast.Compare)
            and len(node.ops) == 1
            and isinstance(node.left, ast.Subscript)
            and isinstance(node.left.slice, ast.Constant)
            and node.left.slice.value == "timestamp_utc"
        }
        self.assertEqual(window_ops, {ast.GtE, ast.LtE})
        copy_calls = [
            node
            for node in ast.walk(_trade_loop())
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "copy"
        ]
        self.assertEqual(len(copy_calls), 1)
        self.assertTrue(any(isinstance(node, ast.Continue) for node in ast.walk(_trade_loop())))
        sort_calls = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr in {"sort_index", "sort_values"}
        ]
        self.assertEqual(sort_calls, [])

    def test_strict_high_streak_trigger_and_conservative_pnl_are_bound(self) -> None:
        source = ast.unparse(_trade_loop())
        self.assertIn("s['high'] = s['shadow_risk_score'] > threshold", source)
        self.assertIn("s['high'].astype(int).groupby", source)
        self.assertIn("(s['high'] != s['high'].shift()).cumsum()", source)
        self.assertIn("triggered = (s['streak'] >= consecutive).any()", source)
        assignments = {
            target.id: ast.unparse(node.value)
            for node in _trade_loop().body
            if isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance((target := node.targets[0]), ast.Name)
            and target.id in {"pnl", "replay_pnl"}
        }
        self.assertEqual(assignments["pnl"], "float(trade['pnl'])")
        self.assertEqual(assignments["replay_pnl"], "0.0 if triggered else pnl")
        row_dict = next(
            node.args[0]
            for node in ast.walk(_trade_loop())
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "append"
        )
        self.assertEqual(
            [ast.literal_eval(key) for key in row_dict.keys],
            ["pnl", "win", "triggered"],
        )
        self.assertEqual(ast.unparse(row_dict.values[1]), "int(replay_pnl > 0)")
        self.assertEqual(ast.unparse(row_dict.values[2]), "int(triggered)")

    def test_metrics_loss_partition_and_output_format_are_bound(self) -> None:
        loop = _config_loop()
        source = ast.unparse(loop)
        self.assertIn("df['equity'] = START_CAPITAL + df['pnl'].cumsum()", source)
        self.assertIn("df['peak'] = df['equity'].cummax()", source)
        self.assertIn("df['dd_pct'] = (df['peak'] - df['equity']) / df['peak']", source)
        self.assertIn("wins = df[df['pnl'] > 0]", source)
        self.assertIn("losses = df[df['pnl'] < 0]", source)
        self.assertIn("gross_profit = wins['pnl'].sum()", source)
        self.assertIn("gross_loss = abs(losses['pnl'].sum())", source)
        self.assertIn("pf = gross_profit / gross_loss if gross_loss > 0 else float('inf')", source)
        self.assertIn("{df['pnl'].sum():.2f}", source)
        self.assertIn("{df['win'].mean():.4f}", source)
        self.assertIn("{pf:.4f}", source)
        self.assertIn("{df['dd_pct'].max():.4f}", source)

    @unittest.skipUnless(FULL_RUNTIME_AVAILABLE, "pandas fixture runtime required")
    def test_import_is_silent_and_has_no_filesystem_side_effects(self) -> None:
        with tempfile.TemporaryDirectory(prefix="step19_dynamic_exit_replay_import_") as temp_dir:
            root = Path(temp_dir)
            stdout = io.StringIO()
            stderr = io.StringIO()
            previous_cwd = Path.cwd()
            try:
                os.chdir(root)
                with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                    namespace = runpy.run_path(
                        str(SCRIPT),
                        run_name="_step19_dynamic_exit_replay_import",
                    )
            finally:
                os.chdir(previous_cwd)
            self.assertEqual(stdout.getvalue(), "")
            self.assertEqual(stderr.getvalue(), "")
            self.assertEqual(_manifest(root), {})
            self.assertEqual(_directories(root), set())
            self.assertTrue(callable(namespace.get("main")))

    @unittest.skipUnless(FULL_RUNTIME_AVAILABLE, "pandas fixture runtime required")
    def test_successful_fixture_stdout_and_nonmutation_are_bound(self) -> None:
        expected_stdout = (
            f"{HEADER}\n"
            "0.5,3,5,3,-20.00,0.0000,0.0000,0.0020\n"
            "0.5,5,5,1,40.00,0.2000,1.6667,0.0059\n"
            "0.6,3,5,2,80.00,0.2000,5.0000,0.0020\n"
            "0.6,5,5,1,40.00,0.2000,1.6667,0.0059\n"
        )
        with tempfile.TemporaryDirectory(prefix="step19_dynamic_exit_replay_success_") as temp_dir:
            root = Path(temp_dir)
            _write_csv(root / TRADES_INPUT, TRADES_ROWS)
            _write_csv(root / SHADOW_INPUT, SHADOW_ROWS)
            before = _manifest(root)
            before_directories = _directories(root)
            result = _run(root)
            after = _manifest(root)
            after_directories = _directories(root)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertEqual(result.stdout, expected_stdout)
        self.assertEqual(hashlib.sha256(result.stdout.encode("utf-8")).hexdigest(), SUCCESS_STDOUT_SHA256)
        self.assertEqual(after, before)
        self.assertEqual(after_directories, before_directories)
        self.assertEqual(set(after), {TRADES_INPUT.as_posix(), SHADOW_INPUT.as_posix()})

    @unittest.skipUnless(FULL_RUNTIME_AVAILABLE, "pandas fixture runtime required")
    def test_missing_inputs_fail_closed_in_read_order(self) -> None:
        with tempfile.TemporaryDirectory(prefix="step19_dynamic_exit_replay_missing_first_") as temp_dir:
            root = Path(temp_dir)
            result = _run(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "")
            self.assertIn("FileNotFoundError", result.stderr)
            self.assertIn(TRADES_INPUT.as_posix(), result.stderr.replace("\\", "/"))
            self.assertEqual(_manifest(root), {})

        with tempfile.TemporaryDirectory(prefix="step19_dynamic_exit_replay_missing_second_") as temp_dir:
            root = Path(temp_dir)
            _write_csv(root / TRADES_INPUT, TRADES_ROWS)
            before = _manifest(root)
            before_directories = _directories(root)
            result = _run(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "")
            self.assertIn("FileNotFoundError", result.stderr)
            self.assertIn(SHADOW_INPUT.as_posix(), result.stderr.replace("\\", "/"))
            self.assertEqual(_manifest(root), before)
            self.assertEqual(_directories(root), before_directories)

    @unittest.skipUnless(FULL_RUNTIME_AVAILABLE, "pandas fixture runtime required")
    def test_no_matched_windows_fail_after_header_on_first_config(self) -> None:
        unmatched_trades = (
            {
                "trade_index": "1",
                "entry_timestamp_utc": "2026-01-02T00:00:00Z",
                "exit_timestamp_utc": "2026-01-02T00:01:00Z",
                "pnl": "1",
            },
        )
        with tempfile.TemporaryDirectory(prefix="step19_dynamic_exit_replay_unmatched_") as temp_dir:
            root = Path(temp_dir)
            _write_csv(root / TRADES_INPUT, unmatched_trades)
            _write_csv(root / SHADOW_INPUT, SHADOW_ROWS)
            before = _manifest(root)
            before_directories = _directories(root)
            result = _run(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(result.stdout, f"{HEADER}\n")
            self.assertIn("KeyError", result.stderr)
            self.assertIn("pnl", result.stderr)
            self.assertEqual(_manifest(root), before)
            self.assertEqual(_directories(root), before_directories)


if __name__ == "__main__":
    unittest.main()
