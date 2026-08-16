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
SCRIPT = REPO_ROOT / "scripts" / "state_research" / "analyze_step20C_live_replay.py"

TRADES_INPUT = Path("live_logs/trades_l1_auto_analysis.csv")
SHADOW_INPUT = Path("live_logs/passive_shadow_risk_snapshots.csv")
OUTPUT = Path("reports/step18/step20C_live_replay.csv")

SOURCE_SHA256 = "8c344af52182788fb57a3791e17ad5fa690b1000bae2b757b50b6f4ec88d2b40"
SOURCE_LINES = 100
RUNTIME_AST_SHA256 = "d14480e22d3095bb5c22b7aa3bac1d540a7a20946fdfe8997bc44203cdbba7c2"
SUCCESS_STDOUT_SHA256 = "f6278aafabf111b4ec3b39ad4f6cd67f6f594258284c8f9af8680f21aa0abad6"
START_CAPITAL = 10000.0

FULL_RUNTIME_AVAILABLE = importlib.util.find_spec("pandas") is not None

TRADES_ROWS = (
    {
        "trade_index": "3",
        "entry_timestamp_utc": "2026-01-01T00:30:00Z",
        "side": "LONG",
        "pnl": "40",
    },
    {
        "trade_index": "1",
        "entry_timestamp_utc": "2026-01-01T00:10:00Z",
        "side": "SHORT",
        "pnl": "100",
    },
    {
        "trade_index": "2",
        "entry_timestamp_utc": "2026-01-01T00:20:00Z",
        "side": "LONG",
        "pnl": "-50",
    },
    {
        "trade_index": "4",
        "entry_timestamp_utc": "2025-12-31T23:59:00Z",
        "side": "SHORT",
        "pnl": "999",
    },
)

SHADOW_ROWS = (
    {"timestamp_utc": "2026-01-01T00:00:00Z", "shadow_risk_score": "0.30"},
    {"timestamp_utc": "2026-01-01T00:15:00Z", "shadow_risk_score": "0.50"},
    {"timestamp_utc": "2026-01-01T00:25:00Z", "shadow_risk_score": "0.51"},
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


def _calc_stats() -> ast.FunctionDef:
    functions = [
        node
        for node in _main_function().body
        if isinstance(node, ast.FunctionDef) and node.name == "calc_stats"
    ]
    if len(functions) != 1:
        raise AssertionError(f"expected one calc_stats function, found {len(functions)}")
    return functions[0]


def _trade_loop() -> ast.For:
    loops = [
        node
        for node in _main_function().body
        if isinstance(node, ast.For)
        and isinstance(node.target, ast.Tuple)
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


class Step20CLiveReplayCharacterizationTests(unittest.TestCase):
    maxDiff = None

    def test_source_identity_start_capital_and_import_executor_are_bound(self) -> None:
        raw = SCRIPT.read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), SOURCE_SHA256)
        self.assertEqual(len(raw.decode("utf-8").splitlines()), SOURCE_LINES)
        assignments = {
            target.id: ast.literal_eval(node.value)
            for node in [*_tree().body, *_main_function().body]
            if isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance((target := node.targets[0]), ast.Name)
            and target.id == "START_CAPITAL"
        }
        self.assertEqual(assignments, {"START_CAPITAL": START_CAPITAL})
        main_function = _main_function()
        guards = [node for node in _tree().body if _is_main_guard(node)]
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
            for node in _tree().body
            if isinstance(node, ast.Assign)
            and isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Attribute)
            and node.value.func.attr == "read_csv"
        ]
        top_level_calls = [
            node
            for node in _tree().body
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call)
        ]
        self.assertEqual(top_level_reads, [])
        self.assertEqual(top_level_calls, [])

        stats_function = _calc_stats()
        self.assertEqual([argument.arg for argument in stats_function.args.args], ["pnl_col"])
        self.assertIsNone(stats_function.returns)

    def test_fixed_read_and_timestamp_conversion_order_are_bound(self) -> None:
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
        self.assertEqual(conversions, ["entry_timestamp_utc", "timestamp_utc"])

    def test_pre_entry_snapshot_selection_skip_and_sort_contract_are_bound(self) -> None:
        source = ast.unparse(_trade_loop())
        self.assertIn("entry_ts = trade['entry_timestamp_utc']", source)
        self.assertIn("shadow[shadow['timestamp_utc'] <= entry_ts].tail(1)", source)
        self.assertIn("snap = snap.iloc[0]", source)
        self.assertTrue(any(isinstance(node, ast.Continue) for node in ast.walk(_trade_loop())))
        all_source = ast.unparse(_tree())
        self.assertNotIn("shadow.sort_values", all_source)
        sort_calls = [
            node
            for node in ast.walk(_tree())
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "sort_values"
        ]
        self.assertEqual(len(sort_calls), 1)
        self.assertEqual(ast.literal_eval(sort_calls[0].args[0]), "trade_index")

    def test_multiplier_boundaries_scaled_pnl_and_row_schema_are_bound(self) -> None:
        source = ast.unparse(_trade_loop())
        self.assertIn("if risk <= 0.3:\n        multiplier = 1.0", source)
        self.assertIn("elif risk <= 0.5:\n        multiplier = 0.5", source)
        self.assertIn("else:\n        multiplier = 0.25", source)
        self.assertIn("scaled_pnl = original_pnl * multiplier", source)
        row_dict = next(
            node.args[0]
            for node in ast.walk(_trade_loop())
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "append"
        )
        self.assertEqual(
            [ast.literal_eval(key) for key in row_dict.keys],
            [
                "trade_index",
                "side",
                "original_pnl",
                "entry_shadow_risk",
                "multiplier",
                "scaled_pnl",
            ],
        )
        self.assertEqual(ast.unparse(row_dict.values[0]), "int(trade['trade_index'])")
        self.assertEqual(ast.unparse(row_dict.values[1]), "trade['side']")

    def test_calc_stats_global_df_metrics_and_key_order_are_bound(self) -> None:
        function = _calc_stats()
        source = ast.unparse(function)
        self.assertIn("START_CAPITAL + df[pnl_col].cumsum()", source)
        self.assertIn("peak = equity.cummax()", source)
        self.assertIn("dd_abs = peak - equity", source)
        self.assertIn("dd_pct = dd_abs / peak", source)
        self.assertIn("wins = df[df[pnl_col] > 0]", source)
        self.assertIn("losses = df[df[pnl_col] < 0]", source)
        self.assertIn("pf = gp / gl if gl > 0 else float('inf')", source)
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
            for node in _main_function().body
            if isinstance(node, ast.Assign)
            and isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Name)
            and node.value.func.id == "calc_stats"
        ]
        self.assertEqual(calls, ["original_pnl", "scaled_pnl"])

    def test_stdout_labels_writer_path_order_and_no_mkdir_are_bound(self) -> None:
        tree = _tree()
        body = _main_function().body
        print_labels = [
            ast.literal_eval(node.value.args[0])
            for node in body
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
                "---- STEP20C LIVE-COMPATIBLE REPLAY ----",
                "trades:",
                "ORIGINAL",
                "STEP20C",
                "MULTIPLIER DISTRIBUTION",
                "written:",
            ],
        )
        out_assignment = next(
            node
            for node in body
            if isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id == "out"
        )
        self.assertEqual(ast.literal_eval(out_assignment.value), OUTPUT.as_posix())
        writes = [
            node
            for node in body
            if isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Attribute)
            and node.value.func.attr == "to_csv"
        ]
        self.assertEqual(len(writes), 1)
        self.assertEqual(ast.unparse(writes[0].value.args[0]), "out")
        self.assertEqual(len(writes[0].value.keywords), 1)
        self.assertEqual(writes[0].value.keywords[0].arg, "index")
        self.assertIs(ast.literal_eval(writes[0].value.keywords[0].value), False)
        mkdir_calls = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "mkdir"
        ]
        self.assertEqual(mkdir_calls, [])

    @unittest.skipUnless(FULL_RUNTIME_AVAILABLE, "pandas fixture runtime required")
    def test_import_is_silent_and_has_no_filesystem_side_effects(self) -> None:
        with tempfile.TemporaryDirectory(prefix="step20c_live_replay_import_") as temp_dir:
            root = Path(temp_dir)
            stdout = io.StringIO()
            stderr = io.StringIO()
            previous_cwd = Path.cwd()
            try:
                os.chdir(root)
                with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                    namespace = runpy.run_path(
                        str(SCRIPT),
                        run_name="_step20c_live_replay_import",
                    )
            finally:
                os.chdir(previous_cwd)
            self.assertEqual(stdout.getvalue(), "")
            self.assertEqual(stderr.getvalue(), "")
            self.assertEqual(_manifest(root), {})
            self.assertEqual(_directories(root), set())
            self.assertTrue(callable(namespace.get("main")))

    @unittest.skipUnless(FULL_RUNTIME_AVAILABLE, "pandas fixture runtime required")
    def test_successful_fixture_stdout_csv_and_input_nonmutation_are_bound(self) -> None:
        expected_stdout = (
            "\n"
            "---- STEP20C LIVE-COMPATIBLE REPLAY ----\n"
            "trades: 3\n"
            "\n"
            "ORIGINAL\n"
            "final_equity: 10090.0\n"
            "total_pnl: 90.0\n"
            "return_pct: 0.009\n"
            "winrate: 0.6667\n"
            "profit_factor: 2.8\n"
            "max_drawdown_abs: 50.0\n"
            "max_drawdown_pct: 0.005\n"
            "\n"
            "STEP20C\n"
            "final_equity: 10085.0\n"
            "total_pnl: 85.0\n"
            "return_pct: 0.0085\n"
            "winrate: 0.6667\n"
            "profit_factor: 4.4\n"
            "max_drawdown_abs: 25.0\n"
            "max_drawdown_pct: 0.0025\n"
            "\n"
            "MULTIPLIER DISTRIBUTION\n"
            "multiplier\n"
            "0.25    1\n"
            "0.50    1\n"
            "1.00    1\n"
            "Name: count, dtype: int64\n"
            "\n"
            f"written: {OUTPUT.as_posix()}\n"
        )
        with tempfile.TemporaryDirectory(prefix="step20c_live_replay_success_") as temp_dir:
            root = Path(temp_dir)
            _write_csv(root / TRADES_INPUT, TRADES_ROWS)
            _write_csv(root / SHADOW_INPUT, SHADOW_ROWS)
            (root / OUTPUT.parent).mkdir(parents=True)
            before = _manifest(root)
            result = _run(root)
            after = _manifest(root)
            rows = _read_csv(root / OUTPUT)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertEqual(result.stdout, expected_stdout)
        self.assertEqual(hashlib.sha256(result.stdout.encode("utf-8")).hexdigest(), SUCCESS_STDOUT_SHA256)
        self.assertEqual({path: after[path] for path in before}, before)
        self.assertIn(OUTPUT.as_posix(), after)
        self.assertEqual([row["trade_index"] for row in rows], ["1", "2", "3"])
        self.assertEqual([row["side"] for row in rows], ["SHORT", "LONG", "LONG"])
        self.assertEqual([row["entry_shadow_risk"] for row in rows], ["0.3", "0.5", "0.51"])
        self.assertEqual([row["multiplier"] for row in rows], ["1.0", "0.5", "0.25"])
        self.assertEqual([row["scaled_pnl"] for row in rows], ["100.0", "-25.0", "10.0"])

    @unittest.skipUnless(FULL_RUNTIME_AVAILABLE, "pandas fixture runtime required")
    def test_pre_entry_tail_uses_file_order_without_timestamp_sort(self) -> None:
        trades = (
            {
                "trade_index": "1",
                "entry_timestamp_utc": "2026-01-01T00:30:00Z",
                "side": "LONG",
                "pnl": "10",
            },
        )
        unsorted_shadow = (
            {"timestamp_utc": "2026-01-01T00:25:00Z", "shadow_risk_score": "0.90"},
            {"timestamp_utc": "2026-01-01T00:00:00Z", "shadow_risk_score": "0.10"},
            {"timestamp_utc": "2026-01-01T00:15:00Z", "shadow_risk_score": "0.40"},
        )
        with tempfile.TemporaryDirectory(prefix="step20c_live_replay_order_") as temp_dir:
            root = Path(temp_dir)
            _write_csv(root / TRADES_INPUT, trades)
            _write_csv(root / SHADOW_INPUT, unsorted_shadow)
            (root / OUTPUT.parent).mkdir(parents=True)
            before = _manifest(root)
            result = _run(root)
            after = _manifest(root)
            rows = _read_csv(root / OUTPUT)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertEqual({path: after[path] for path in before}, before)
        self.assertEqual(rows[0]["entry_shadow_risk"], "0.4")
        self.assertEqual(rows[0]["multiplier"], "0.5")
        self.assertEqual(rows[0]["scaled_pnl"], "5.0")

    @unittest.skipUnless(FULL_RUNTIME_AVAILABLE, "pandas fixture runtime required")
    def test_missing_inputs_fail_closed_in_read_order(self) -> None:
        with tempfile.TemporaryDirectory(prefix="step20c_live_replay_missing_first_") as temp_dir:
            root = Path(temp_dir)
            result = _run(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "")
            self.assertIn("FileNotFoundError", result.stderr)
            self.assertIn(TRADES_INPUT.as_posix(), result.stderr.replace("\\", "/"))
            self.assertEqual(_manifest(root), {})

        with tempfile.TemporaryDirectory(prefix="step20c_live_replay_missing_second_") as temp_dir:
            root = Path(temp_dir)
            _write_csv(root / TRADES_INPUT, TRADES_ROWS)
            before = _manifest(root)
            result = _run(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "")
            self.assertIn("FileNotFoundError", result.stderr)
            self.assertIn(SHADOW_INPUT.as_posix(), result.stderr.replace("\\", "/"))
            self.assertEqual(_manifest(root), before)

    @unittest.skipUnless(FULL_RUNTIME_AVAILABLE, "pandas fixture runtime required")
    def test_no_eligible_pre_entry_snapshots_fail_before_stdout(self) -> None:
        future_shadow = (
            {"timestamp_utc": "2026-01-03T00:00:00Z", "shadow_risk_score": "0.1"},
        )
        with tempfile.TemporaryDirectory(prefix="step20c_live_replay_no_snap_") as temp_dir:
            root = Path(temp_dir)
            _write_csv(root / TRADES_INPUT, TRADES_ROWS)
            _write_csv(root / SHADOW_INPUT, future_shadow)
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
        with tempfile.TemporaryDirectory(prefix="step20c_live_replay_missing_output_") as temp_dir:
            root = Path(temp_dir)
            _write_csv(root / TRADES_INPUT, TRADES_ROWS)
            _write_csv(root / SHADOW_INPUT, SHADOW_ROWS)
            before = _manifest(root)
            before_directories = _directories(root)
            result = _run(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("---- STEP20C LIVE-COMPATIBLE REPLAY ----", result.stdout)
            self.assertIn("MULTIPLIER DISTRIBUTION", result.stdout)
            self.assertNotIn("written:", result.stdout)
            self.assertIn("OSError", result.stderr)
            self.assertIn(OUTPUT.parent.as_posix(), result.stderr.replace("\\", "/"))
            self.assertEqual(_manifest(root), before)
            self.assertEqual(_directories(root), before_directories)


if __name__ == "__main__":
    unittest.main()
