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
SCRIPT = REPO_ROOT / "scripts" / "state_research" / "analyze_step19_gate_quality.py"

TRADES_INPUT = Path("live_logs/trades_l1_auto_analysis.csv")
SHADOW_INPUT = Path("live_logs/passive_shadow_risk_snapshots.csv")

SOURCE_SHA256 = "3069392f6c459d2dc54db1278bfa575756228e007159b8da80dff91b9f9a11e8"
SOURCE_LINES = 59
SUCCESS_STDOUT_SHA256 = "0bf31b04f63da292728641b31840f772101014f5221aeb30aa66255aa729a8d6"

FULL_RUNTIME_AVAILABLE = importlib.util.find_spec("pandas") is not None

TRADES_ROWS = (
    {
        "trade_index": "1",
        "entry_timestamp_utc": "2026-01-01T00:01:00Z",
        "exit_timestamp_utc": "2026-01-01T00:02:00Z",
        "pnl": "10",
    },
    {
        "trade_index": "2",
        "entry_timestamp_utc": "2026-01-01T00:03:00Z",
        "exit_timestamp_utc": "2026-01-01T00:04:00Z",
        "pnl": "-4",
    },
    {
        "trade_index": "3",
        "entry_timestamp_utc": "2026-01-01T00:05:00Z",
        "exit_timestamp_utc": "2026-01-01T00:06:00Z",
        "pnl": "0",
    },
    {
        "trade_index": "4",
        "entry_timestamp_utc": "2026-01-01T00:07:00Z",
        "exit_timestamp_utc": "2026-01-01T00:08:00Z",
        "pnl": "8",
    },
    {
        "trade_index": "5",
        "entry_timestamp_utc": "2026-01-01T00:09:00Z",
        "exit_timestamp_utc": "2026-01-01T00:10:00Z",
        "pnl": "2",
    },
    {
        "trade_index": "6",
        "entry_timestamp_utc": "2026-01-02T00:00:00Z",
        "exit_timestamp_utc": "2026-01-02T00:01:00Z",
        "pnl": "999",
    },
)

SHADOW_ROWS = (
    {"timestamp_utc": "2026-01-01T00:01:00Z", "shadow_risk_score": "0.40"},
    {"timestamp_utc": "2026-01-01T00:02:00Z", "shadow_risk_score": "0.60"},
    {"timestamp_utc": "2026-01-01T00:03:00Z", "shadow_risk_score": "0.40"},
    {"timestamp_utc": "2026-01-01T00:05:00Z", "shadow_risk_score": "0.30"},
    {"timestamp_utc": "2026-01-01T00:07:00Z", "shadow_risk_score": "0.60"},
    {"timestamp_utc": "2026-01-01T00:09:00Z", "shadow_risk_score": "0.70"},
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


def _group_loop() -> ast.For:
    loops = [
        node
        for node in _tree().body
        if isinstance(node, ast.For)
        and isinstance(node.target, ast.Tuple)
        and [element.id for element in node.target.elts if isinstance(element, ast.Name)]
        == ["group_name", "g"]
    ]
    if len(loops) != 1:
        raise AssertionError(f"expected one group loop, found {len(loops)}")
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


class Step19GateQualityCharacterizationTests(unittest.TestCase):
    maxDiff = None

    def test_source_identity_and_fixed_group_boundary_are_bound(self) -> None:
        raw = SCRIPT.read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), SOURCE_SHA256)
        self.assertEqual(len(raw.decode("utf-8").splitlines()), SOURCE_LINES)
        lambdas = [node for node in ast.walk(_tree()) if isinstance(node, ast.Lambda)]
        self.assertEqual(len(lambdas), 1)
        self.assertEqual(
            ast.unparse(lambdas[0]),
            "lambda x: 'HIGH_RISK' if x > 0.5 else 'LOW_RISK'",
        )

    def test_script_remains_an_import_time_executor(self) -> None:
        tree = _tree()
        self.assertEqual(
            [node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))],
            [],
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
        self.assertEqual(len(reads), 2)
        self.assertIn("df.groupby('group')", ast.unparse(_group_loop().iter))

    def test_fixed_input_read_and_timestamp_conversion_order_is_bound(self) -> None:
        body = _tree().body
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

    def test_inclusive_window_row_win_label_and_skip_contract_is_bound(self) -> None:
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
        row_dicts = [
            node.args[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "append"
            and len(node.args) == 1
            and isinstance(node.args[0], ast.Dict)
        ]
        self.assertEqual(len(row_dicts), 1)
        self.assertEqual(
            [ast.literal_eval(key) for key in row_dicts[0].keys],
            ["pnl", "win", "mean_shadow_risk"],
        )
        self.assertEqual(ast.unparse(row_dicts[0].values[1]), "int(pnl > 0.0)")
        self.assertTrue(any(isinstance(node, ast.Continue) for node in ast.walk(tree)))

    def test_group_metrics_output_order_and_nonwriter_contract_are_bound(self) -> None:
        loop = _group_loop()
        assignments = {
            target.id: ast.unparse(node.value)
            for node in loop.body
            if isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance((target := node.targets[0]), ast.Name)
        }
        self.assertEqual(assignments["wins"], "g[g['pnl'] > 0]")
        self.assertEqual(assignments["losses"], "g[g['pnl'] <= 0]")
        self.assertEqual(assignments["gross_profit"], "wins['pnl'].sum()")
        self.assertEqual(assignments["gross_loss"], "abs(losses['pnl'].sum())")
        self.assertEqual(
            assignments["pf"],
            "gross_profit / gross_loss if gross_loss > 0 else float('inf')",
        )

        print_arguments = [
            [ast.unparse(argument) for argument in node.value.args]
            for node in loop.body
            if isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Name)
            and node.value.func.id == "print"
        ]
        self.assertEqual(
            print_arguments,
            [
                [],
                ["'GROUP:'", "group_name"],
                ["'trades:'", "len(g)"],
                ["'winrate:'", "round(g['win'].mean(), 4)"],
                ["'avg_pnl:'", "round(g['pnl'].mean(), 2)"],
                ["'gross_profit:'", "round(gross_profit, 2)"],
                ["'gross_loss:'", "round(gross_loss, 2)"],
                ["'profit_factor:'", "round(pf, 4)"],
                [],
            ],
        )
        writer_calls = [
            node
            for node in ast.walk(_tree())
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr in {"mkdir", "open", "to_csv", "write_bytes", "write_text"}
        ]
        self.assertEqual(writer_calls, [])

    @unittest.skipUnless(FULL_RUNTIME_AVAILABLE, "pandas fixture runtime required")
    def test_successful_fixture_stdout_and_nonmutation_are_bound(self) -> None:
        with tempfile.TemporaryDirectory(prefix="step19_gate_quality_success_") as temp_dir:
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
        self.assertLess(result.stdout.index("GROUP: HIGH_RISK"), result.stdout.index("GROUP: LOW_RISK"))
        self.assertIn("GROUP: HIGH_RISK\ntrades: 2\nwinrate: 1.0\navg_pnl: 5.0", result.stdout)
        self.assertIn("gross_loss: 0.0\nprofit_factor: inf", result.stdout)
        self.assertIn("GROUP: LOW_RISK\ntrades: 3\nwinrate: 0.3333\navg_pnl: 2.0", result.stdout)
        self.assertIn("gross_loss: 4.0\nprofit_factor: 2.5", result.stdout)

    @unittest.skipUnless(FULL_RUNTIME_AVAILABLE, "pandas fixture runtime required")
    def test_missing_inputs_fail_closed_in_read_order(self) -> None:
        with tempfile.TemporaryDirectory(prefix="step19_gate_quality_missing_first_") as temp_dir:
            root = Path(temp_dir)
            result = _run(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "")
            self.assertIn("FileNotFoundError", result.stderr)
            self.assertIn(TRADES_INPUT.as_posix(), result.stderr.replace("\\", "/"))
            self.assertEqual(_manifest(root), {})

        with tempfile.TemporaryDirectory(prefix="step19_gate_quality_missing_second_") as temp_dir:
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
                "pnl": "1",
            },
        )
        with tempfile.TemporaryDirectory(prefix="step19_gate_quality_unmatched_") as temp_dir:
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
