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
SCRIPT = REPO_ROOT / "scripts" / "state_research" / "analyze_step19_blocked_trades.py"

TRADES_INPUT = Path("live_logs/trades_l1_auto_analysis.csv")
SHADOW_INPUT = Path("live_logs/passive_shadow_risk_snapshots.csv")

SOURCE_SHA256 = "376e0a01572aec43fc377a4a282dc58aca12b649ae81510bfcd49976e6798ef5"
SOURCE_LINES = 41
SUCCESS_STDOUT_SHA256 = "4c0c24b3d840037590bdd871cd683aa1ca5afca71bc7ca5feb01d2ef6ea67dfb"

FULL_RUNTIME_AVAILABLE = importlib.util.find_spec("pandas") is not None

TRADES_ROWS = (
    {
        "entry_timestamp_utc": "2026-01-01T00:01:00Z",
        "exit_timestamp_utc": "2026-01-01T00:03:00Z",
        "side": "BUY",
        "pnl": "10",
        "exit_reason": "TAKE_PROFIT",
    },
    {
        "entry_timestamp_utc": "2026-01-01T00:04:00Z",
        "exit_timestamp_utc": "2026-01-01T00:05:00Z",
        "side": "SELL",
        "pnl": "-4",
        "exit_reason": "STOP",
    },
    {
        "entry_timestamp_utc": "2026-01-01T00:06:00Z",
        "exit_timestamp_utc": "2026-01-01T00:07:00Z",
        "side": "BUY",
        "pnl": "-2",
        "exit_reason": "STOP",
    },
    {
        "entry_timestamp_utc": "2026-01-01T00:08:00Z",
        "exit_timestamp_utc": "2026-01-01T00:09:00Z",
        "side": "SELL",
        "pnl": "5",
        "exit_reason": "TIME",
    },
    {
        "entry_timestamp_utc": "2026-01-01T00:10:00Z",
        "exit_timestamp_utc": "2026-01-01T00:11:00Z",
        "side": "SELL",
        "pnl": "3",
        "exit_reason": "TAKE_PROFIT",
    },
)

SHADOW_ROWS = (
    {"timestamp_utc": "2026-01-01T00:01:00Z", "shadow_risk_score": "0.4"},
    {"timestamp_utc": "2026-01-01T00:03:00Z", "shadow_risk_score": "0.8"},
    {"timestamp_utc": "2026-01-01T00:04:00Z", "shadow_risk_score": "0.5"},
    {"timestamp_utc": "2026-01-01T00:05:00Z", "shadow_risk_score": "0.5"},
    {"timestamp_utc": "2026-01-01T00:06:00Z", "shadow_risk_score": "0.9"},
    {"timestamp_utc": "2026-01-01T00:07:00Z", "shadow_risk_score": "0.7"},
    {"timestamp_utc": "2026-01-01T00:10:00Z", "shadow_risk_score": "0.9"},
    {"timestamp_utc": "2026-01-01T00:11:00Z", "shadow_risk_score": "0.9"},
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


class Step19BlockedTradesCharacterizationTests(unittest.TestCase):
    maxDiff = None

    def test_source_identity_is_bound(self) -> None:
        raw = SCRIPT.read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), SOURCE_SHA256)
        self.assertEqual(len(raw.decode("utf-8").splitlines()), SOURCE_LINES)

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

        top_level_calls = [
            node
            for node in tree.body
            if isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Call)
            and not _is_main_guard(node)
        ]
        top_level_reads = [
            node
            for node in tree.body
            if isinstance(node, ast.Assign)
            and isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Attribute)
            and node.value.func.attr == "read_csv"
        ]
        self.assertEqual(top_level_calls, [])
        self.assertEqual(top_level_reads, [])

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
        self.assertEqual(
            conversions,
            ["entry_timestamp_utc", "exit_timestamp_utc", "timestamp_utc"],
        )

    def test_inclusive_window_mean_and_strict_threshold_are_bound(self) -> None:
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

        means = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "mean"
            and isinstance(node.func.value, ast.Subscript)
            and isinstance(node.func.value.slice, ast.Constant)
            and node.func.value.slice.value == "shadow_risk_score"
        ]
        self.assertEqual(len(means), 1)

        thresholds = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Compare)
            and len(node.ops) == 1
            and isinstance(node.ops[0], ast.Gt)
            and len(node.comparators) == 1
            and isinstance(node.comparators[0], ast.Constant)
            and node.comparators[0].value == 0.5
        ]
        self.assertEqual(len(thresholds), 1)

    def test_grouping_aggregation_and_sort_contract_is_bound(self) -> None:
        tree = _tree()
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

        sort_values = [
            ast.literal_eval(node.args[0])
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "sort_values"
            and len(node.args) == 1
        ]
        self.assertEqual(sort_values, ["sum"])

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
        with tempfile.TemporaryDirectory(prefix="step19_blocked_import_") as temp_dir:
            root = Path(temp_dir)
            stdout = io.StringIO()
            stderr = io.StringIO()
            previous_cwd = Path.cwd()
            try:
                os.chdir(root)
                with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                    namespace = runpy.run_path(
                        str(SCRIPT),
                        run_name="_step19_blocked_trades_import",
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
        with tempfile.TemporaryDirectory(prefix="step19_blocked_success_") as temp_dir:
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
        self.assertIn("BUY", result.stdout)
        self.assertIn("SELL", result.stdout)
        self.assertIn("STOP", result.stdout)
        self.assertIn("TAKE_PROFIT", result.stdout)
        self.assertNotIn("TIME", result.stdout)

    @unittest.skipUnless(FULL_RUNTIME_AVAILABLE, "pandas fixture runtime required")
    def test_missing_inputs_fail_closed_in_read_order(self) -> None:
        with tempfile.TemporaryDirectory(prefix="step19_blocked_missing_first_") as temp_dir:
            root = Path(temp_dir)
            result = _run(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "")
            self.assertIn("FileNotFoundError", result.stderr)
            self.assertIn(TRADES_INPUT.as_posix(), result.stderr.replace("\\", "/"))
            self.assertEqual(_manifest(root), {})

        with tempfile.TemporaryDirectory(prefix="step19_blocked_missing_second_") as temp_dir:
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
                "entry_timestamp_utc": "2026-01-02T00:00:00Z",
                "exit_timestamp_utc": "2026-01-02T00:01:00Z",
                "side": "BUY",
                "pnl": "1",
                "exit_reason": "TIME",
            },
        )
        with tempfile.TemporaryDirectory(prefix="step19_blocked_unmatched_") as temp_dir:
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
