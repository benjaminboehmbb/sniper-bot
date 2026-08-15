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
STATE_RESEARCH_DIR = REPO_ROOT / "scripts" / "state_research"
BUCKETS_SCRIPT = STATE_RESEARCH_DIR / "analyze_step18_buckets.py"
LIFETIME_SCRIPT = STATE_RESEARCH_DIR / "analyze_step18_trade_lifetime.py"

TRADES_INPUT = Path("live_logs/trades_l1_auto_analysis.csv")
SHADOW_INPUT = Path("live_logs/passive_shadow_risk_snapshots.csv")

SOURCE_SHA256 = {
    "analyze_step18_buckets.py": "89fe1b9cdd1c28027c07775b4e2520a077b0206becf31782b21cff8d882f64ec",
    "analyze_step18_trade_lifetime.py": "1f9b0d69bff434a84ad8a45243b241ec77dc24412b553645840701dfd02e2af1",
}
SOURCE_LINES = {
    "analyze_step18_buckets.py": 55,
    "analyze_step18_trade_lifetime.py": 64,
}
BUCKETS_STDOUT_SHA256 = "4253c8fec7c481c68c4a74763d5d86adcf7dd99ea67869c9c51da98d04f223a0"
LIFETIME_STDOUT_SHA256 = "bb2c4166fe44f1b76b99398c99fda29a40cee6c8e24902d8c32007c26c5db61c"
PANDAS_AVAILABLE = importlib.util.find_spec("pandas") is not None


BUCKET_TRADES = (
    {"entry_timestamp_utc": "2025-12-31T23:59:00Z", "pnl": "9"},
    {"entry_timestamp_utc": "2026-01-01T00:01:00Z", "pnl": "10"},
    {"entry_timestamp_utc": "2026-01-01T00:02:00Z", "pnl": "-5"},
    {"entry_timestamp_utc": "2026-01-01T00:03:00Z", "pnl": "4"},
    {"entry_timestamp_utc": "2026-01-01T00:04:00Z", "pnl": "-2"},
)
BUCKET_SHADOW = (
    {"timestamp_utc": "2026-01-01T00:01:00Z", "shadow_risk_score": "0.1"},
    {"timestamp_utc": "2026-01-01T00:02:00Z", "shadow_risk_score": "0.3"},
    {"timestamp_utc": "2026-01-01T00:03:00Z", "shadow_risk_score": "0.7"},
    {"timestamp_utc": "2026-01-01T00:04:00Z", "shadow_risk_score": "1.0"},
)

LIFETIME_TRADES = (
    {
        "entry_timestamp_utc": "2025-12-31T23:00:00Z",
        "exit_timestamp_utc": "2025-12-31T23:30:00Z",
        "pnl": "7",
    },
    {
        "entry_timestamp_utc": "2026-01-01T00:00:00Z",
        "exit_timestamp_utc": "2026-01-01T00:01:00Z",
        "pnl": "10",
    },
    {
        "entry_timestamp_utc": "2026-01-01T00:02:00Z",
        "exit_timestamp_utc": "2026-01-01T00:03:00Z",
        "pnl": "-5",
    },
    {
        "entry_timestamp_utc": "2026-01-01T00:04:00Z",
        "exit_timestamp_utc": "2026-01-01T00:05:00Z",
        "pnl": "2",
    },
)
LIFETIME_SHADOW = (
    {"timestamp_utc": "2026-01-01T00:00:00Z", "shadow_risk_score": "0.1", "meta_state_score": "0.2"},
    {"timestamp_utc": "2026-01-01T00:01:00Z", "shadow_risk_score": "0.3", "meta_state_score": "0.4"},
    {"timestamp_utc": "2026-01-01T00:02:00Z", "shadow_risk_score": "0.5", "meta_state_score": "0.6"},
    {"timestamp_utc": "2026-01-01T00:03:00Z", "shadow_risk_score": "0.7", "meta_state_score": "0.8"},
    {"timestamp_utc": "2026-01-01T00:04:00Z", "shadow_risk_score": "0.2", "meta_state_score": "0.9"},
    {"timestamp_utc": "2026-01-01T00:05:00Z", "shadow_risk_score": "0.4", "meta_state_score": "0.5"},
)


def _tree(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


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


def _file_manifest(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def _run_fixture(
    script: Path,
    trades: tuple[dict[str, str], ...],
    shadow: tuple[dict[str, str], ...],
) -> tuple[subprocess.CompletedProcess[str], dict[str, str], dict[str, str]]:
    with tempfile.TemporaryDirectory(prefix="step18_stdout_pair_") as temp_dir:
        root = Path(temp_dir)
        _write_csv(root / TRADES_INPUT, trades)
        _write_csv(root / SHADOW_INPUT, shadow)
        before = _file_manifest(root)
        completed = subprocess.run(
            [sys.executable, str(script)],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
        )
        after = _file_manifest(root)
    completed.stdout = completed.stdout.replace("\r\n", "\n")
    completed.stderr = completed.stderr.replace("\r\n", "\n")
    return completed, before, after


class Step18StdoutPairCharacterizationTests(unittest.TestCase):
    def test_source_identities_are_bound(self) -> None:
        for script in (BUCKETS_SCRIPT, LIFETIME_SCRIPT):
            with self.subTest(script=script.name):
                raw = script.read_bytes()
                self.assertEqual(hashlib.sha256(raw).hexdigest(), SOURCE_SHA256[script.name])
                self.assertEqual(len(raw.decode("utf-8").splitlines()), SOURCE_LINES[script.name])

    def test_both_entry_points_are_contained_behind_main_guards(self) -> None:
        expected_reads = (TRADES_INPUT.as_posix(), SHADOW_INPUT.as_posix())
        for script in (BUCKETS_SCRIPT, LIFETIME_SCRIPT):
            with self.subTest(script=script.name):
                tree = _tree(script)
                main_guards = [node for node in tree.body if _is_main_guard(node)]
                main_functions = [
                    node
                    for node in tree.body
                    if isinstance(node, ast.FunctionDef) and node.name == "main"
                ]
                self.assertEqual(len(main_guards), 1)
                self.assertEqual(len(main_functions), 1)
                main_function = main_functions[0]
                self.assertEqual(main_function.args.posonlyargs, [])
                self.assertEqual(main_function.args.args, [])
                self.assertEqual(main_function.args.kwonlyargs, [])
                self.assertIsNone(main_function.args.vararg)
                self.assertIsNone(main_function.args.kwarg)
                self.assertEqual(len(main_guards[0].body), 1)
                guard_call = main_guards[0].body[0]
                self.assertIsInstance(guard_call, ast.Expr)
                self.assertIsInstance(guard_call.value, ast.Call)
                self.assertIsInstance(guard_call.value.func, ast.Name)
                self.assertEqual(guard_call.value.func.id, "main")
                self.assertEqual(guard_call.value.args, [])
                self.assertEqual(guard_call.value.keywords, [])
                top_level_reads = [
                    node.value.args[0].value
                    for node in tree.body
                    if isinstance(node, ast.Assign)
                    and isinstance(node.value, ast.Call)
                    and isinstance(node.value.func, ast.Attribute)
                    and isinstance(node.value.func.value, ast.Name)
                    and node.value.func.value.id == "pd"
                    and node.value.func.attr == "read_csv"
                    and len(node.value.args) == 1
                    and isinstance(node.value.args[0], ast.Constant)
                ]
                self.assertEqual(top_level_reads, [])
                contained_reads = [
                    node.args[0].value
                    for node in ast.walk(main_function)
                    if isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Attribute)
                    and isinstance(node.func.value, ast.Name)
                    and node.func.value.id == "pd"
                    and node.func.attr == "read_csv"
                    and len(node.args) == 1
                    and isinstance(node.args[0], ast.Constant)
                ]
                self.assertEqual(tuple(contained_reads), expected_reads)

    def test_buckets_cut_and_aggregation_contract_is_bound(self) -> None:
        tree = _tree(BUCKETS_SCRIPT)
        cut_calls = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "pd"
            and node.func.attr == "cut"
        ]
        self.assertEqual(len(cut_calls), 1)
        keywords = {keyword.arg: keyword.value for keyword in cut_calls[0].keywords}
        self.assertEqual(ast.literal_eval(keywords["bins"]), [0, 0.2, 0.4, 0.6, 0.8, 1.0])
        self.assertIs(ast.literal_eval(keywords["include_lowest"]), True)

        agg_calls = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "agg"
        ]
        self.assertEqual(len(agg_calls), 1)
        self.assertEqual(
            {keyword.arg: ast.literal_eval(keyword.value) for keyword in agg_calls[0].keywords},
            {
                "trades": ("pnl", "count"),
                "avg_pnl": ("pnl", "mean"),
                "winrate": ("win", "mean"),
            },
        )

    def test_trade_lifetime_correlation_contract_is_bound(self) -> None:
        expected_pairs = {
            ("mean_shadow_risk", "pnl"),
            ("mean_shadow_risk", "win"),
            ("max_shadow_risk", "pnl"),
            ("max_shadow_risk", "win"),
            ("mean_meta_state", "pnl"),
            ("mean_meta_state", "win"),
        }
        observed_pairs: set[tuple[str, str]] = set()
        for node in ast.walk(_tree(LIFETIME_SCRIPT)):
            if not (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "corr"
                and isinstance(node.func.value, ast.Subscript)
                and len(node.args) == 1
                and isinstance(node.args[0], ast.Subscript)
            ):
                continue
            left = ast.literal_eval(node.func.value.slice)
            right = ast.literal_eval(node.args[0].slice)
            observed_pairs.add((left, right))
        self.assertEqual(observed_pairs, expected_pairs)

    def test_neither_script_contains_file_writer_calls(self) -> None:
        writer_attributes = {
            "mkdir",
            "open",
            "to_csv",
            "to_excel",
            "to_feather",
            "to_json",
            "to_parquet",
            "write_bytes",
            "write_text",
        }
        for script in (BUCKETS_SCRIPT, LIFETIME_SCRIPT):
            with self.subTest(script=script.name):
                tree = _tree(script)
                attribute_calls = {
                    node.func.attr
                    for node in ast.walk(tree)
                    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                }
                builtin_open_calls = [
                    node
                    for node in ast.walk(tree)
                    if isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Name)
                    and node.func.id == "open"
                ]
                self.assertFalse(attribute_calls & writer_attributes)
                self.assertEqual(builtin_open_calls, [])

    @unittest.skipUnless(PANDAS_AVAILABLE, "pandas fixture runtime required")
    def test_buckets_fixture_output_and_non_mutation_are_bound(self) -> None:
        completed, before, after = _run_fixture(BUCKETS_SCRIPT, BUCKET_TRADES, BUCKET_SHADOW)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(completed.stderr, "")
        self.assertEqual(before, after)
        self.assertEqual(set(after), {TRADES_INPUT.as_posix(), SHADOW_INPUT.as_posix()})
        self.assertEqual(hashlib.sha256(completed.stdout.encode("utf-8")).hexdigest(), BUCKETS_STDOUT_SHA256)

    @unittest.skipUnless(PANDAS_AVAILABLE, "pandas fixture runtime required")
    def test_trade_lifetime_fixture_output_and_non_mutation_are_bound(self) -> None:
        completed, before, after = _run_fixture(
            LIFETIME_SCRIPT,
            LIFETIME_TRADES,
            LIFETIME_SHADOW,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(completed.stderr, "")
        self.assertEqual(before, after)
        self.assertEqual(set(after), {TRADES_INPUT.as_posix(), SHADOW_INPUT.as_posix()})
        self.assertEqual(hashlib.sha256(completed.stdout.encode("utf-8")).hexdigest(), LIFETIME_STDOUT_SHA256)

    @unittest.skipUnless(PANDAS_AVAILABLE, "pandas fixture runtime required")
    def test_import_paths_have_no_input_read_stdout_or_mutation(self) -> None:
        for script in (BUCKETS_SCRIPT, LIFETIME_SCRIPT):
            with self.subTest(script=script.name):
                with tempfile.TemporaryDirectory(prefix="step18_stdout_pair_import_") as temp_dir:
                    root = Path(temp_dir)
                    original_cwd = Path.cwd()
                    stdout = io.StringIO()
                    try:
                        os.chdir(root)
                        with contextlib.redirect_stdout(stdout):
                            namespace = runpy.run_path(
                                str(script),
                                run_name=f"{script.stem}_import_probe",
                            )
                    finally:
                        os.chdir(original_cwd)
                    self.assertEqual(_file_manifest(root), {})
                self.assertEqual(stdout.getvalue(), "")
                self.assertIn("main", namespace)
                self.assertTrue(callable(namespace["main"]))

    @unittest.skipUnless(PANDAS_AVAILABLE, "pandas fixture runtime required")
    def test_missing_first_input_fails_closed_before_stdout(self) -> None:
        for script in (BUCKETS_SCRIPT, LIFETIME_SCRIPT):
            with self.subTest(script=script.name):
                with tempfile.TemporaryDirectory(prefix="step18_stdout_pair_missing_") as temp_dir:
                    completed = subprocess.run(
                        [sys.executable, str(script)],
                        cwd=Path(temp_dir),
                        check=False,
                        capture_output=True,
                        text=True,
                    )
                self.assertNotEqual(completed.returncode, 0)
                self.assertEqual(completed.stdout, "")
                self.assertIn("FileNotFoundError", completed.stderr)
                self.assertIn(TRADES_INPUT.as_posix(), completed.stderr.replace("\\", "/"))


if __name__ == "__main__":
    unittest.main()
