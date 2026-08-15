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
SCRIPT = REPO_ROOT / "scripts" / "state_research" / "analyze_step19_risk_escalation.py"

TRADES_INPUT = Path("live_logs/trades_l1_auto_analysis.csv")
SHADOW_INPUT = Path("live_logs/passive_shadow_risk_snapshots.csv")

SOURCE_SHA256 = "2b0eafa4c5b8f94509b608d0ecc026ba5bc7f0032bf33459a9e9a1b639df1fe9"
SOURCE_LINES = 60
SUCCESS_STDOUT_SHA256 = "b8a823f50b41e113d1617a3785c9faecb019136ee1b15961cb2f017c491f5cff"

RISK_FIELDS = [
    "entry_risk",
    "max_risk",
    "mean_risk",
    "high_risk_count",
    "high_risk_pct",
]

FULL_RUNTIME_AVAILABLE = importlib.util.find_spec("pandas") is not None

TRADES_ROWS = (
    {
        "trade_index": "1",
        "entry_timestamp_utc": "2026-01-01T00:01:00Z",
        "exit_timestamp_utc": "2026-01-01T00:04:00Z",
        "pnl": "10",
    },
    {
        "trade_index": "2",
        "entry_timestamp_utc": "2026-01-01T00:05:00Z",
        "exit_timestamp_utc": "2026-01-01T00:08:00Z",
        "pnl": "4",
    },
    {
        "trade_index": "3",
        "entry_timestamp_utc": "2026-01-01T00:09:00Z",
        "exit_timestamp_utc": "2026-01-01T00:12:00Z",
        "pnl": "-6",
    },
    {
        "trade_index": "4",
        "entry_timestamp_utc": "2026-01-01T00:13:00Z",
        "exit_timestamp_utc": "2026-01-01T00:16:00Z",
        "pnl": "0",
    },
    {
        "trade_index": "5",
        "entry_timestamp_utc": "2026-01-01T00:17:00Z",
        "exit_timestamp_utc": "2026-01-01T00:20:00Z",
        "pnl": "999",
    },
    {
        "trade_index": "6",
        "entry_timestamp_utc": "2026-01-02T00:00:00Z",
        "exit_timestamp_utc": "2026-01-02T00:01:00Z",
        "pnl": "999",
    },
)

SHADOW_ROWS = (
    {"timestamp_utc": "2026-01-01T00:01:00Z", "shadow_risk_score": "0.2"},
    {"timestamp_utc": "2026-01-01T00:02:00Z", "shadow_risk_score": "0.5"},
    {"timestamp_utc": "2026-01-01T00:04:00Z", "shadow_risk_score": "0.6"},
    {"timestamp_utc": "2026-01-01T00:05:00Z", "shadow_risk_score": "0.4"},
    {"timestamp_utc": "2026-01-01T00:06:00Z", "shadow_risk_score": "0.7"},
    {"timestamp_utc": "2026-01-01T00:08:00Z", "shadow_risk_score": "0.8"},
    {"timestamp_utc": "2026-01-01T00:09:00Z", "shadow_risk_score": "0.9"},
    {"timestamp_utc": "2026-01-01T00:10:00Z", "shadow_risk_score": "0.5"},
    {"timestamp_utc": "2026-01-01T00:12:00Z", "shadow_risk_score": "0.1"},
    {"timestamp_utc": "2026-01-01T00:13:00Z", "shadow_risk_score": "0.3"},
    {"timestamp_utc": "2026-01-01T00:14:00Z", "shadow_risk_score": "0.4"},
    {"timestamp_utc": "2026-01-01T00:16:00Z", "shadow_risk_score": "0.5"},
    {"timestamp_utc": "2026-01-01T00:17:00Z", "shadow_risk_score": "0.9"},
    {"timestamp_utc": "2026-01-01T00:20:00Z", "shadow_risk_score": "0.9"},
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


class Step19RiskEscalationCharacterizationTests(unittest.TestCase):
    maxDiff = None

    def test_source_identity_snapshot_minimum_and_high_risk_boundary_are_bound(self) -> None:
        raw = SCRIPT.read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), SOURCE_SHA256)
        self.assertEqual(len(raw.decode("utf-8").splitlines()), SOURCE_LINES)
        self.assertIn("if len(s) < 3:\n        continue", SCRIPT.read_text(encoding="utf-8"))
        high_risk_comparisons = [
            node
            for node in ast.walk(_tree())
            if isinstance(node, ast.Compare)
            and len(node.ops) == 1
            and isinstance(node.ops[0], ast.Gt)
            and isinstance(node.left, ast.Subscript)
            and isinstance(node.left.slice, ast.Constant)
            and node.left.slice.value == "shadow_risk_score"
            and len(node.comparators) == 1
            and isinstance(node.comparators[0], ast.Constant)
            and node.comparators[0].value == 0.5
        ]
        self.assertEqual(len(high_risk_comparisons), 2)

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

    def test_inclusive_window_row_and_first_snapshot_contract_is_bound(self) -> None:
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
            ["win", "pnl", "entry_risk", "max_risk", "mean_risk", "high_risk_count", "high_risk_pct"],
        )
        row_values = [ast.unparse(value) for value in row_dicts[0].values]
        self.assertEqual(
            row_values,
            [
                "int(pnl > 0)",
                "pnl",
                "float(s.iloc[0]['shadow_risk_score'])",
                "float(s['shadow_risk_score'].max())",
                "float(s['shadow_risk_score'].mean())",
                "int((s['shadow_risk_score'] > 0.5).sum())",
                "float((s['shadow_risk_score'] > 0.5).mean())",
            ],
        )
        copy_calls = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "copy"
        ]
        self.assertEqual(len(copy_calls), 1)

    def test_partition_projection_correlations_output_and_nonwriter_contract_are_bound(self) -> None:
        tree = _tree()
        source = ast.unparse(tree)
        self.assertIn("df[df['win'] == 1]", source)
        self.assertIn("df[df['win'] == 0]", source)
        projected_fields = [
            ast.literal_eval(element)
            for node in ast.walk(tree)
            if isinstance(node, ast.List)
            and len(node.elts) == len(RISK_FIELDS)
            and all(isinstance(element, ast.Constant) for element in node.elts)
            for element in node.elts
        ]
        self.assertEqual(projected_fields, RISK_FIELDS + RISK_FIELDS)
        correlations = [
            ast.unparse(node)
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "corr"
        ]
        self.assertEqual(
            correlations,
            [
                "df['mean_risk'].corr(df['pnl'])",
                "df['max_risk'].corr(df['pnl'])",
                "df['high_risk_pct'].corr(df['pnl'])",
            ],
        )
        print_labels = [
            ast.literal_eval(node.args[0])
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "print"
            and node.args
            and isinstance(node.args[0], ast.Constant)
        ]
        self.assertEqual(
            print_labels,
            [
                "WINNERS",
                "LOSERS",
                "CORRELATIONS",
                "mean_risk vs pnl:",
                "max_risk vs pnl :",
                "high_risk_pct vs pnl :",
            ],
        )
        writer_calls = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr in {"mkdir", "open", "to_csv", "write_bytes", "write_text"}
        ]
        self.assertEqual(writer_calls, [])

    @unittest.skipUnless(FULL_RUNTIME_AVAILABLE, "pandas fixture runtime required")
    def test_successful_fixture_stdout_and_nonmutation_are_bound(self) -> None:
        with tempfile.TemporaryDirectory(prefix="step19_risk_escalation_success_") as temp_dir:
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
        self.assertIn("WINNERS\nentry_risk         0.300000", result.stdout)
        self.assertIn("LOSERS\nentry_risk         0.600000", result.stdout)
        self.assertIn("high_risk_count    1.500000", result.stdout)
        self.assertIn("high_risk_count    0.500000", result.stdout)
        self.assertIn("CORRELATIONS", result.stdout)

    @unittest.skipUnless(FULL_RUNTIME_AVAILABLE, "pandas fixture runtime required")
    def test_missing_inputs_fail_closed_in_read_order(self) -> None:
        with tempfile.TemporaryDirectory(prefix="step19_risk_escalation_missing_first_") as temp_dir:
            root = Path(temp_dir)
            result = _run(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "")
            self.assertIn("FileNotFoundError", result.stderr)
            self.assertIn(TRADES_INPUT.as_posix(), result.stderr.replace("\\", "/"))
            self.assertEqual(_manifest(root), {})

        with tempfile.TemporaryDirectory(prefix="step19_risk_escalation_missing_second_") as temp_dir:
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
    def test_no_eligible_window_fails_closed_after_winners_heading(self) -> None:
        unmatched_trades = (
            {
                "trade_index": "1",
                "entry_timestamp_utc": "2026-01-02T00:00:00Z",
                "exit_timestamp_utc": "2026-01-02T00:01:00Z",
                "pnl": "1",
            },
        )
        with tempfile.TemporaryDirectory(prefix="step19_risk_escalation_unmatched_") as temp_dir:
            root = Path(temp_dir)
            _write_csv(root / TRADES_INPUT, unmatched_trades)
            _write_csv(root / SHADOW_INPUT, SHADOW_ROWS)
            before = _manifest(root)
            result = _run(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "\nWINNERS\n")
            self.assertIn("KeyError", result.stderr)
            self.assertIn("win", result.stderr)
            self.assertEqual(_manifest(root), before)


if __name__ == "__main__":
    unittest.main()
