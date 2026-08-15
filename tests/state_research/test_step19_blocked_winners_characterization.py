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
SCRIPT = REPO_ROOT / "scripts" / "state_research" / "analyze_step19_blocked_winners.py"

TRADES_INPUT = Path("live_logs/trades_l1_auto_analysis.csv")
SHADOW_INPUT = Path("live_logs/passive_shadow_risk_snapshots.csv")

SOURCE_SHA256 = "f62a34fd96055610a222dab685f62b50b316755be362176043ea197d4cc6908a"
SOURCE_LINES = 51
SUCCESS_STDOUT_SHA256 = "353a9ce33e95ad176e95bb0436841dee245726fd3be3ab02ca4493430294722b"

FULL_RUNTIME_AVAILABLE = importlib.util.find_spec("pandas") is not None

TRADES_ROWS = (
    {
        "trade_index": "1",
        "entry_timestamp_utc": "2026-01-01T00:01:00Z",
        "exit_timestamp_utc": "2026-01-01T00:02:00Z",
        "side": "BUY",
        "pnl": "10",
        "exit_reason": "BOUNDARY",
    },
    {
        "trade_index": "2",
        "entry_timestamp_utc": "2026-01-01T00:03:00Z",
        "exit_timestamp_utc": "2026-01-01T00:04:00Z",
        "side": "BUY",
        "pnl": "8",
        "exit_reason": "TAKE_PROFIT",
    },
    {
        "trade_index": "3",
        "entry_timestamp_utc": "2026-01-01T00:05:00Z",
        "exit_timestamp_utc": "2026-01-01T00:06:00Z",
        "side": "SELL",
        "pnl": "-3",
        "exit_reason": "STOP",
    },
    {
        "trade_index": "4",
        "entry_timestamp_utc": "2026-01-01T00:07:00Z",
        "exit_timestamp_utc": "2026-01-01T00:08:00Z",
        "side": "SELL",
        "pnl": "0",
        "exit_reason": "TIME",
    },
    {
        "trade_index": "5",
        "entry_timestamp_utc": "2026-01-01T00:09:00Z",
        "exit_timestamp_utc": "2026-01-01T00:10:00Z",
        "side": "SELL",
        "pnl": "5",
        "exit_reason": "TRAIL",
    },
    {
        "trade_index": "6",
        "entry_timestamp_utc": "2026-01-01T00:11:00Z",
        "exit_timestamp_utc": "2026-01-01T00:12:00Z",
        "side": "BUY",
        "pnl": "99",
        "exit_reason": "NO_SNAPSHOT",
    },
)

SHADOW_ROWS = (
    {"timestamp_utc": "2026-01-01T00:01:00Z", "shadow_risk_score": "0.3"},
    {"timestamp_utc": "2026-01-01T00:02:00Z", "shadow_risk_score": "0.5"},
    {"timestamp_utc": "2026-01-01T00:03:00Z", "shadow_risk_score": "0.5"},
    {"timestamp_utc": "2026-01-01T00:04:00Z", "shadow_risk_score": "0.5"},
    {"timestamp_utc": "2026-01-01T00:05:00Z", "shadow_risk_score": "0.6"},
    {"timestamp_utc": "2026-01-01T00:06:00Z", "shadow_risk_score": "0.6"},
    {"timestamp_utc": "2026-01-01T00:07:00Z", "shadow_risk_score": "0.7"},
    {"timestamp_utc": "2026-01-01T00:08:00Z", "shadow_risk_score": "0.7"},
    {"timestamp_utc": "2026-01-01T00:09:00Z", "shadow_risk_score": "0.8"},
    {"timestamp_utc": "2026-01-01T00:10:00Z", "shadow_risk_score": "0.8"},
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


class Step19BlockedWinnersCharacterizationTests(unittest.TestCase):
    maxDiff = None

    def test_source_identity_and_threshold_are_bound(self) -> None:
        raw = SCRIPT.read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), SOURCE_SHA256)
        self.assertEqual(len(raw.decode("utf-8").splitlines()), SOURCE_LINES)
        threshold_assignments = [
            node
            for node in _tree().body
            if isinstance(node, ast.Assign)
            and any(isinstance(target, ast.Name) and target.id == "THRESHOLD" for target in node.targets)
        ]
        self.assertEqual(len(threshold_assignments), 1)
        self.assertEqual(ast.literal_eval(threshold_assignments[0].value), 0.4)

    def test_entrypoint_is_contained_behind_main_guard(self) -> None:
        tree = _tree()
        guards = [node for node in tree.body if _is_main_guard(node)]
        main_function = _main_function()
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

    def test_fixed_input_read_and_timestamp_conversion_order_is_bound(self) -> None:
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
            and len(node.value.args) == 1
            and isinstance(node.value.args[0], ast.Subscript)
        ]
        self.assertEqual(conversions, ["entry_timestamp_utc", "exit_timestamp_utc", "timestamp_utc"])

    def test_inclusive_window_row_and_skip_contract_is_bound(self) -> None:
        tree = _tree()
        window_ops = {
            type(node.ops[0])
            for node in ast.walk(tree)
            if isinstance(node, ast.Compare)
            and len(node.ops) == 1
            and isinstance(node.left, ast.Subscript)
            and isinstance(node.left.slice, ast.Constant)
            and node.left.slice.value == "timestamp_utc"
        }
        self.assertEqual(window_ops, {ast.GtE, ast.LtE})
        row_keys = [
            ast.literal_eval(key)
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "append"
            and len(node.args) == 1
            and isinstance(node.args[0], ast.Dict)
            for key in node.args[0].keys
        ]
        self.assertEqual(
            row_keys,
            ["trade_index", "side", "pnl", "exit_reason", "mean_shadow_risk"],
        )
        self.assertTrue(any(isinstance(node, ast.Continue) for node in ast.walk(tree)))

    def test_blocked_winner_loser_and_grouping_contract_is_bound(self) -> None:
        tree = _tree()
        compare_signatures = {
            (
                ast.literal_eval(node.left.slice),
                type(node.ops[0]),
                node.comparators[0].id if isinstance(node.comparators[0], ast.Name) else ast.literal_eval(node.comparators[0]),
            )
            for node in ast.walk(tree)
            if isinstance(node, ast.Compare)
            and len(node.ops) == 1
            and isinstance(node.left, ast.Subscript)
            and isinstance(node.left.slice, ast.Constant)
            and node.left.slice.value in {"mean_shadow_risk", "pnl"}
        }
        self.assertEqual(
            compare_signatures,
            {
                ("mean_shadow_risk", ast.Gt, "THRESHOLD"),
                ("pnl", ast.Gt, 0),
                ("pnl", ast.LtE, 0),
            },
        )
        group_fields = [
            ast.literal_eval(node.args[0])
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "groupby"
            and len(node.args) == 1
        ]
        self.assertEqual(group_fields, ["side", "exit_reason"])
        aggregations = [
            ast.literal_eval(node.args[0])
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "agg"
            and len(node.args) == 1
        ]
        self.assertEqual(aggregations, [["count", "mean", "sum"], ["count", "mean", "sum"]])
        sort_calls = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "sort_values"
        ]
        self.assertEqual(len(sort_calls), 1)
        self.assertEqual(ast.literal_eval(sort_calls[0].args[0]), "sum")
        self.assertIs(ast.literal_eval(sort_calls[0].keywords[0].value), False)

        writer_calls = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr in {"mkdir", "open", "to_csv", "write_bytes", "write_text"}
        ]
        self.assertEqual(writer_calls, [])

    @unittest.skipUnless(FULL_RUNTIME_AVAILABLE, "pandas fixture runtime required")
    def test_import_is_silent_and_has_no_filesystem_side_effects(self) -> None:
        with tempfile.TemporaryDirectory(prefix="step19_blocked_winners_import_") as temp_dir:
            root = Path(temp_dir)
            stdout = io.StringIO()
            stderr = io.StringIO()
            previous_cwd = Path.cwd()
            try:
                os.chdir(root)
                with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                    namespace = runpy.run_path(
                        str(SCRIPT),
                        run_name="_step19_blocked_winners_import",
                    )
            finally:
                os.chdir(previous_cwd)
            self.assertEqual(stdout.getvalue(), "")
            self.assertEqual(stderr.getvalue(), "")
            self.assertEqual(_manifest(root), {})
            self.assertEqual([path for path in root.rglob("*") if path.is_dir()], [])
            self.assertTrue(callable(namespace.get("main")))

    @unittest.skipUnless(FULL_RUNTIME_AVAILABLE, "pandas fixture runtime required")
    def test_successful_fixture_stdout_and_nonmutation_are_bound(self) -> None:
        with tempfile.TemporaryDirectory(prefix="step19_blocked_winners_success_") as temp_dir:
            root = Path(temp_dir)
            _write_csv(root / TRADES_INPUT, TRADES_ROWS)
            _write_csv(root / SHADOW_INPUT, SHADOW_ROWS)
            before = _manifest(root)
            result = _run(root)
            after = _manifest(root)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertEqual(after, before)
        self.assertEqual(hashlib.sha256(result.stdout.encode("utf-8")).hexdigest(), SUCCESS_STDOUT_SHA256)
        self.assertIn("blocked_total: 4", result.stdout)
        self.assertIn("blocked_winners: 2 sum_pnl: 13.0", result.stdout)
        self.assertIn("blocked_losers: 2 sum_pnl: -3.0", result.stdout)
        self.assertNotIn("BOUNDARY", result.stdout)
        self.assertNotIn("NO_SNAPSHOT", result.stdout)

    @unittest.skipUnless(FULL_RUNTIME_AVAILABLE, "pandas fixture runtime required")
    def test_missing_inputs_fail_closed_in_read_order(self) -> None:
        with tempfile.TemporaryDirectory(prefix="step19_blocked_winners_missing_first_") as temp_dir:
            root = Path(temp_dir)
            result = _run(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "")
            self.assertIn("FileNotFoundError", result.stderr)
            self.assertIn(TRADES_INPUT.as_posix(), result.stderr.replace("\\", "/"))
            self.assertEqual(_manifest(root), {})

        with tempfile.TemporaryDirectory(prefix="step19_blocked_winners_missing_second_") as temp_dir:
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
    def test_no_matched_window_fails_closed_before_stdout(self) -> None:
        unmatched_trades = (
            {
                "trade_index": "1",
                "entry_timestamp_utc": "2026-01-02T00:00:00Z",
                "exit_timestamp_utc": "2026-01-02T00:01:00Z",
                "side": "BUY",
                "pnl": "1",
                "exit_reason": "TIME",
            },
        )
        with tempfile.TemporaryDirectory(prefix="step19_blocked_winners_unmatched_") as temp_dir:
            root = Path(temp_dir)
            _write_csv(root / TRADES_INPUT, unmatched_trades)
            _write_csv(root / SHADOW_INPUT, SHADOW_ROWS)
            before = _manifest(root)
            result = _run(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "")
            self.assertIn("KeyError", result.stderr)
            self.assertIn("mean_shadow_risk", result.stderr)
            self.assertEqual(_manifest(root), before)


if __name__ == "__main__":
    unittest.main()
