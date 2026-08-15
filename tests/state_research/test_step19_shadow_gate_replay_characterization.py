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
SCRIPT = REPO_ROOT / "scripts" / "state_research" / "analyze_step19_shadow_gate_replay.py"

TRADES_INPUT = Path("live_logs/trades_l1_auto_analysis.csv")
SHADOW_INPUT = Path("live_logs/passive_shadow_risk_snapshots.csv")
TRADES_OUTPUT = Path("reports/step18/step19_shadow_gate_replay_trades.csv")
KEPT_OUTPUT = Path("reports/step18/step19_shadow_gate_replay_kept_trades.csv")

SOURCE_SHA256 = "0a91b7e836679b3611c9650d1a3c1385768911329e266fdaff54681e16cc09ad"
SOURCE_LINES = 70
START_CAPITAL = 10000.0
THRESHOLDS = [0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70]

FULL_RUNTIME_AVAILABLE = importlib.util.find_spec("pandas") is not None

TRADES_ROWS = (
    {
        "trade_index": "2",
        "entry_timestamp_utc": "2026-01-01T00:03:00Z",
        "exit_timestamp_utc": "2026-01-01T00:04:00Z",
        "pnl": "-5",
    },
    {
        "trade_index": "1",
        "entry_timestamp_utc": "2026-01-01T00:01:00Z",
        "exit_timestamp_utc": "2026-01-01T00:02:00Z",
        "pnl": "10",
    },
    {
        "trade_index": "3",
        "entry_timestamp_utc": "2026-01-02T00:00:00Z",
        "exit_timestamp_utc": "2026-01-02T00:01:00Z",
        "pnl": "999",
    },
)

SHADOW_ROWS = (
    {"timestamp_utc": "2026-01-01T00:01:00Z", "shadow_risk_score": "0.30"},
    {"timestamp_utc": "2026-01-01T00:02:00Z", "shadow_risk_score": "0.50"},
    {"timestamp_utc": "2026-01-01T00:03:00Z", "shadow_risk_score": "0.60"},
    {"timestamp_utc": "2026-01-01T00:04:00Z", "shadow_risk_score": "0.60"},
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


class Step19ShadowGateReplayCharacterizationTests(unittest.TestCase):
    maxDiff = None

    def test_source_identity_constants_and_unbound_threshold_are_bound(self) -> None:
        raw = SCRIPT.read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), SOURCE_SHA256)
        self.assertEqual(len(raw.decode("utf-8").splitlines()), SOURCE_LINES)
        constants = {
            target.id: ast.literal_eval(node.value)
            for node in _tree().body
            if isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance((target := node.targets[0]), ast.Name)
            and target.id in {"START_CAPITAL", "THRESHOLDS"}
        }
        self.assertEqual(
            constants,
            {"START_CAPITAL": START_CAPITAL, "THRESHOLDS": THRESHOLDS},
        )
        threshold_loads = [
            node
            for node in ast.walk(_tree())
            if isinstance(node, ast.Name)
            and node.id == "THRESHOLD"
            and isinstance(node.ctx, ast.Load)
        ]
        threshold_stores = [
            node
            for node in ast.walk(_tree())
            if isinstance(node, ast.Name)
            and node.id == "THRESHOLD"
            and isinstance(node.ctx, ast.Store)
        ]
        thresholds_loads = [
            node
            for node in ast.walk(_tree())
            if isinstance(node, ast.Name)
            and node.id == "THRESHOLDS"
            and isinstance(node.ctx, ast.Load)
        ]
        self.assertEqual(len(threshold_loads), 2)
        self.assertEqual(threshold_stores, [])
        self.assertEqual(thresholds_loads, [])

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

    def test_inclusive_window_row_sort_and_missing_window_contract_are_bound(self) -> None:
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
            ["trade_index", "pnl", "win", "mean_shadow_risk"],
        )
        self.assertEqual(ast.unparse(row_dicts[0].values[2]), "int(float(trade['pnl']) > 0)")
        sort_calls = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "sort_values"
        ]
        self.assertEqual(len(sort_calls), 1)
        self.assertEqual(ast.literal_eval(sort_calls[0].args[0]), "trade_index")
        self.assertTrue(any(isinstance(node, ast.Continue) for node in ast.walk(tree)))

    def test_latent_replay_metrics_writers_and_output_order_are_bound(self) -> None:
        tree = _tree()
        source = ast.unparse(tree)
        self.assertIn("df['kept'] = df['mean_shadow_risk'] <= THRESHOLD", source)
        self.assertIn("kept = df[df['kept']].copy()", source)
        self.assertIn("kept['equity'] = START_CAPITAL + kept['pnl'].cumsum()", source)
        self.assertIn("kept['equity_peak'] = kept['equity'].cummax()", source)
        self.assertIn("kept['drawdown_abs'] = kept['equity_peak'] - kept['equity']", source)
        self.assertIn("kept['drawdown_pct'] = kept['drawdown_abs'] / kept['equity_peak']", source)
        self.assertIn("wins = kept[kept['pnl'] > 0]", source)
        self.assertIn("losses = kept[kept['pnl'] <= 0]", source)
        self.assertIn("pf = gross_profit / gross_loss if gross_loss > 0 else float('inf')", source)

        writes = [
            node
            for node in tree.body
            if isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Attribute)
            and node.value.func.attr == "to_csv"
        ]
        self.assertEqual(
            [ast.literal_eval(node.value.args[0]) for node in writes],
            [TRADES_OUTPUT.as_posix(), KEPT_OUTPUT.as_posix()],
        )
        self.assertTrue(
            all(
                len(node.value.keywords) == 1
                and node.value.keywords[0].arg == "index"
                and ast.literal_eval(node.value.keywords[0].value) is False
                for node in writes
            )
        )
        mkdir_calls = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "mkdir"
        ]
        self.assertEqual(mkdir_calls, [])
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
                "---- STEP19A SHADOW GATE REPLAY ----",
                "threshold:",
                "start_capital:",
                "original_trades:",
                "kept_trades:",
                "blocked_trades:",
                "final_equity:",
                "total_pnl:",
                "return_pct:",
                "winrate:",
                "profit_factor:",
                "max_drawdown_abs:",
                "max_drawdown_pct:",
                "written:",
                TRADES_OUTPUT.as_posix(),
                KEPT_OUTPUT.as_posix(),
            ],
        )

    @unittest.skipUnless(FULL_RUNTIME_AVAILABLE, "pandas fixture runtime required")
    def test_matched_fixture_propagates_unbound_threshold_before_outputs(self) -> None:
        with tempfile.TemporaryDirectory(prefix="step19_shadow_gate_replay_matched_") as temp_dir:
            root = Path(temp_dir)
            _write_csv(root / TRADES_INPUT, TRADES_ROWS)
            _write_csv(root / SHADOW_INPUT, SHADOW_ROWS)
            before = _manifest(root)
            before_directories = _directories(root)
            result = _run(root)
            after = _manifest(root)
            after_directories = _directories(root)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertIn("NameError", result.stderr)
        self.assertIn("THRESHOLD", result.stderr)
        self.assertEqual(after, before)
        self.assertEqual(after_directories, before_directories)
        self.assertNotIn(TRADES_OUTPUT.as_posix(), after)
        self.assertNotIn(KEPT_OUTPUT.as_posix(), after)

    @unittest.skipUnless(FULL_RUNTIME_AVAILABLE, "pandas fixture runtime required")
    def test_missing_inputs_fail_closed_in_read_order(self) -> None:
        with tempfile.TemporaryDirectory(prefix="step19_shadow_gate_replay_missing_first_") as temp_dir:
            root = Path(temp_dir)
            result = _run(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "")
            self.assertIn("FileNotFoundError", result.stderr)
            self.assertIn(TRADES_INPUT.as_posix(), result.stderr.replace("\\", "/"))
            self.assertEqual(_manifest(root), {})

        with tempfile.TemporaryDirectory(prefix="step19_shadow_gate_replay_missing_second_") as temp_dir:
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
    def test_no_matched_window_fails_before_unbound_threshold(self) -> None:
        unmatched_trades = (
            {
                "trade_index": "1",
                "entry_timestamp_utc": "2026-01-02T00:00:00Z",
                "exit_timestamp_utc": "2026-01-02T00:01:00Z",
                "pnl": "1",
            },
        )
        with tempfile.TemporaryDirectory(prefix="step19_shadow_gate_replay_unmatched_") as temp_dir:
            root = Path(temp_dir)
            _write_csv(root / TRADES_INPUT, unmatched_trades)
            _write_csv(root / SHADOW_INPUT, SHADOW_ROWS)
            before = _manifest(root)
            result = _run(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "")
            self.assertIn("KeyError", result.stderr)
            self.assertIn("trade_index", result.stderr)
            self.assertNotIn("NameError", result.stderr)
            self.assertEqual(_manifest(root), before)


if __name__ == "__main__":
    unittest.main()
