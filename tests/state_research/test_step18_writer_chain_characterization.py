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
CORE_SCRIPT = STATE_RESEARCH_DIR / "build_step18_core_pipeline.py"
CLUSTER_SCRIPT = STATE_RESEARCH_DIR / "analyze_step18_clusters.py"

SHADOW_INPUT = Path("live_logs/passive_shadow_risk_snapshots.csv")
REPORT_DIR = Path("reports/step18")
CORE_METRICS = REPORT_DIR / "step18_core_metrics.csv"

SOURCE_SHA256 = {
    "build_step18_core_pipeline.py": "57a819ed2fb04f075e059b5dc60cf4fba3b2c284b4b27e0120f30e01512fcf98",
    "analyze_step18_clusters.py": "65918c7346b1819862dc17db2124768f0de6c8ca45daa93b0a846a4cbc80c5a3",
}
SOURCE_LINES = {
    "build_step18_core_pipeline.py": 141,
    "analyze_step18_clusters.py": 86,
}

CORE_OUTPUTS = {
    REPORT_DIR / "step18_core_metrics.csv",
    REPORT_DIR / "step18_regime_summary.csv",
    REPORT_DIR / "step18_boundary_events.csv",
    REPORT_DIR / "step18_collapse_events.csv",
    REPORT_DIR / "step18_sustainable_topologies.csv",
}
CLUSTER_OUTPUTS = {
    REPORT_DIR / "step18_top_boundary_clusters.csv",
    REPORT_DIR / "step18_top_collapse_clusters.csv",
    REPORT_DIR / "step18_top_sustainable_clusters.csv",
    REPORT_DIR / "step18_cluster_summary.csv",
}

REQUIRED_COLUMNS = (
    "current_score",
    "shadow_risk_score",
    "meta_state_score",
    "market_regime",
    "atr_quality",
)
CORE_COLUMNS = (
    "tick_id",
    "timestamp_utc",
    "side",
    "position",
    "price",
    "current_score",
    "market_regime",
    "atr_quality",
    "shadow_risk_score",
    "shadow_risk_name",
    "meta_state_score",
    "meta_state_bucket",
    "collapse_exposure",
    "score_pressure",
    "atr_stress",
    "regime_stress",
    "boundary_tension",
    "coherence_score",
    "recovery_strength",
    "overload_pressure",
    "dissipation_efficiency",
    "sustainable_efficiency",
    "step18_regime",
)

CHAIN_FINGERPRINTS = {
    "core_stdout": "a5b8162b0f5180547232b5dc612409356ab210ad3953e53a64a7dbb8dd6f0c14",
    "cluster_stdout": "1572efed45b7ad613311ddffe40d1d41dd3f53e72f97664c6c69ffa2e73343fb",
    "reports/step18/step18_core_metrics.csv": "5dc9a669dbce1761e1f47d9d959c6c7f29fa6f19913a852286519ea87a25cf5f",
    "reports/step18/step18_regime_summary.csv": "9224ad812b32d0e20e893028cfdda3dc8b3cb0db17bc7ef44b1aa0406827b71d",
    "reports/step18/step18_boundary_events.csv": "28d4a1da686d894d8893eb6813ace1883f0062fd69178084311cac8ccb5b8444",
    "reports/step18/step18_collapse_events.csv": "52b984bac4c1d95165276aaba0c71e4588aa770c9436dcb118737f74b24dbfa4",
    "reports/step18/step18_sustainable_topologies.csv": "1a7068e49bfc7f10827fd97403a0812a777355b4630dab72f7670f1072ac379f",
    "reports/step18/step18_top_boundary_clusters.csv": "5fc303bc3b62fdd02e034bc164444b63f8d94cba18d4e4fbcf04b01b6263678b",
    "reports/step18/step18_top_collapse_clusters.csv": "8cda5f6c40affa325d93a60d8ec997cacb4503e7d9915f22497dbcb653b834e0",
    "reports/step18/step18_top_sustainable_clusters.csv": "4ddcc764a68a98a2b572075877dfdfe9edbdee45a74dcbae4a2ec293adc1fd3e",
    "reports/step18/step18_cluster_summary.csv": "e40b7b7837bd32065667438915a28a423b957c679925e7e5a6aceeefd234c616",
}

FULL_RUNTIME_AVAILABLE = (
    importlib.util.find_spec("numpy") is not None
    and importlib.util.find_spec("pandas") is not None
)

SHADOW_ROWS = (
    {
        "tick_id": "tick-collapse",
        "timestamp_utc": "2026-01-01T00:00:00Z",
        "side": "BUY",
        "position": "LONG",
        "price": "100",
        "current_score": "1",
        "market_regime": "bear",
        "atr_quality": "good",
        "shadow_risk_score": "0.8",
        "shadow_risk_name": "high",
        "shadow_risk_level": "3",
        "meta_state_score": "0.2",
        "meta_state_bucket": "low",
    },
    {
        "tick_id": "tick-boundary",
        "timestamp_utc": "2026-01-01T00:01:00Z",
        "side": "BUY",
        "position": "LONG",
        "price": "101",
        "current_score": "4",
        "market_regime": "bull",
        "atr_quality": "bad",
        "shadow_risk_score": "0.6",
        "shadow_risk_name": "medium",
        "shadow_risk_level": "2",
        "meta_state_score": "0.4",
        "meta_state_bucket": "medium",
    },
    {
        "tick_id": "tick-sustainable",
        "timestamp_utc": "2026-01-01T00:02:00Z",
        "side": "HOLD",
        "position": "FLAT",
        "price": "102",
        "current_score": "0",
        "market_regime": "bull",
        "atr_quality": "good",
        "shadow_risk_score": "0.1",
        "shadow_risk_name": "low",
        "shadow_risk_level": "1",
        "meta_state_score": "0.9",
        "meta_state_bucket": "high",
    },
    {
        "tick_id": "tick-neutral-atr",
        "timestamp_utc": "2026-01-01T00:03:00Z",
        "side": "SELL",
        "position": "LONG",
        "price": "103",
        "current_score": "0",
        "market_regime": "bull",
        "atr_quality": "bad",
        "shadow_risk_score": "0.5",
        "shadow_risk_name": "medium",
        "shadow_risk_level": "2",
        "meta_state_score": "0.5",
        "meta_state_bucket": "medium",
    },
    {
        "tick_id": "tick-neutral-score",
        "timestamp_utc": "2026-01-01T00:04:00Z",
        "side": "HOLD",
        "position": "FLAT",
        "price": "104",
        "current_score": "2",
        "market_regime": "sideways",
        "atr_quality": "good",
        "shadow_risk_score": "0.3",
        "shadow_risk_name": "medium",
        "shadow_risk_level": "2",
        "meta_state_score": "0.6",
        "meta_state_bucket": "medium",
    },
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


def _main_function(path: Path) -> ast.FunctionDef:
    functions = [
        node
        for node in _tree(path).body
        if isinstance(node, ast.FunctionDef) and node.name == "main"
    ]
    if len(functions) != 1:
        raise AssertionError(f"expected one main function in {path}, found {len(functions)}")
    return functions[0]


def _write_csv(path: Path, rows: tuple[dict[str, str], ...]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=tuple(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _raw_file_manifest(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def _canonical_csv_sha256(path: Path) -> str:
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _directories(root: Path) -> set[str]:
    return {
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_dir()
    }


def _run(script: Path, root: Path) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        [sys.executable, str(script)],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    completed.stdout = completed.stdout.replace("\r\n", "\n")
    completed.stderr = completed.stderr.replace("\r\n", "\n")
    return completed


def _read_csv(path: Path) -> tuple[tuple[str, ...], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return tuple(reader.fieldnames or ()), list(reader)


def _normalized_slashes(value: str) -> str:
    normalized = value.replace("\\", "/")
    while "//" in normalized:
        normalized = normalized.replace("//", "/")
    return normalized


class Step18WriterChainCharacterizationTests(unittest.TestCase):
    maxDiff = None

    def test_source_identities_are_bound(self) -> None:
        for script in (CORE_SCRIPT, CLUSTER_SCRIPT):
            with self.subTest(script=script.name):
                raw = script.read_bytes()
                self.assertEqual(hashlib.sha256(raw).hexdigest(), SOURCE_SHA256[script.name])
                self.assertEqual(len(raw.decode("utf-8").splitlines()), SOURCE_LINES[script.name])

    def test_both_entry_points_are_contained_behind_main_guards(self) -> None:
        for script in (CORE_SCRIPT, CLUSTER_SCRIPT):
            with self.subTest(script=script.name):
                tree = _tree(script)
                main_guards = [node for node in tree.body if _is_main_guard(node)]
                main_function = _main_function(script)
                self.assertEqual(len(main_guards), 1)
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

                top_level_effects = [
                    node
                    for node in tree.body
                    if isinstance(node, ast.Expr)
                    and isinstance(node.value, ast.Call)
                    and isinstance(node.value.func, ast.Attribute)
                    and node.value.func.attr in {"mkdir", "to_csv"}
                ]
                top_level_reads = [
                    node
                    for node in tree.body
                    if isinstance(node, ast.Assign)
                    and isinstance(node.value, ast.Call)
                    and isinstance(node.value.func, ast.Attribute)
                    and node.value.func.attr == "read_csv"
                ]
                self.assertEqual(top_level_effects, [])
                self.assertEqual(top_level_reads, [])

    def test_core_mkdir_precedes_input_read(self) -> None:
        main_function = _main_function(CORE_SCRIPT)
        mkdir_index = next(
            index
            for index, node in enumerate(main_function.body)
            if isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Attribute)
            and node.value.func.attr == "mkdir"
        )
        read_index = next(
            index
            for index, node in enumerate(main_function.body)
            if isinstance(node, ast.Assign)
            and isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Attribute)
            and node.value.func.attr == "read_csv"
        )
        self.assertLess(mkdir_index, read_index)

    def test_writer_counts_and_chain_paths_are_bound(self) -> None:
        core_strings = {
            node.value
            for node in ast.walk(_tree(CORE_SCRIPT))
            if isinstance(node, ast.Constant)
            and isinstance(node.value, str)
            and node.value.endswith(".csv")
        }
        cluster_strings = {
            node.value
            for node in ast.walk(_tree(CLUSTER_SCRIPT))
            if isinstance(node, ast.Constant)
            and isinstance(node.value, str)
            and node.value.endswith(".csv")
        }
        self.assertEqual(
            core_strings,
            {SHADOW_INPUT.as_posix()} | {path.name for path in CORE_OUTPUTS},
        )
        self.assertEqual(
            cluster_strings,
            {CORE_METRICS.as_posix()} | {path.name for path in CLUSTER_OUTPUTS},
        )
        core_writes = [
            node
            for node in ast.walk(_tree(CORE_SCRIPT))
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "to_csv"
        ]
        cluster_writes = [
            node
            for node in ast.walk(_tree(CLUSTER_SCRIPT))
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "to_csv"
        ]
        self.assertEqual(len(core_writes), 5)
        self.assertEqual(len(cluster_writes), 4)

    def test_required_and_implicit_core_columns_are_bound(self) -> None:
        required_assignments = [
            node
            for node in ast.walk(_tree(CORE_SCRIPT))
            if isinstance(node, ast.Assign)
            and any(isinstance(target, ast.Name) and target.id == "required" for target in node.targets)
        ]
        self.assertEqual(len(required_assignments), 1)
        self.assertEqual(tuple(ast.literal_eval(required_assignments[0].value)), REQUIRED_COLUMNS)
        self.assertNotIn("shadow_risk_level", REQUIRED_COLUMNS)
        shadow_risk_level_reads = [
            node
            for node in ast.walk(_tree(CORE_SCRIPT))
            if isinstance(node, ast.Subscript)
            and isinstance(node.slice, ast.Constant)
            and node.slice.value == "shadow_risk_level"
        ]
        self.assertGreaterEqual(len(shadow_risk_level_reads), 2)

    @unittest.skipUnless(FULL_RUNTIME_AVAILABLE, "numpy/pandas fixture runtime required")
    def test_imports_are_silent_and_have_no_filesystem_side_effects(self) -> None:
        for script in (CORE_SCRIPT, CLUSTER_SCRIPT):
            with self.subTest(script=script.name):
                with tempfile.TemporaryDirectory(prefix="step18_writer_import_") as temp_dir:
                    root = Path(temp_dir)
                    stdout = io.StringIO()
                    stderr = io.StringIO()
                    previous_cwd = Path.cwd()
                    try:
                        os.chdir(root)
                        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                            namespace = runpy.run_path(
                                str(script),
                                run_name=f"_step18_import_{script.stem}",
                            )
                    finally:
                        os.chdir(previous_cwd)
                    self.assertEqual(stdout.getvalue(), "")
                    self.assertEqual(stderr.getvalue(), "")
                    self.assertEqual(_raw_file_manifest(root), {})
                    self.assertEqual(_directories(root), set())
                    self.assertTrue(callable(namespace.get("main")))

    @unittest.skipUnless(FULL_RUNTIME_AVAILABLE, "numpy/pandas fixture runtime required")
    def test_successful_chain_outputs_and_fingerprints_are_bound(self) -> None:
        with tempfile.TemporaryDirectory(prefix="step18_writer_chain_") as temp_dir:
            root = Path(temp_dir)
            _write_csv(root / SHADOW_INPUT, SHADOW_ROWS)
            before = _raw_file_manifest(root)
            core_result = _run(CORE_SCRIPT, root)
            after_core = _raw_file_manifest(root)
            self.assertEqual(core_result.returncode, 0, core_result.stderr)
            self.assertEqual(core_result.stderr, "")
            self.assertEqual(set(after_core), {SHADOW_INPUT.as_posix()} | {p.as_posix() for p in CORE_OUTPUTS})
            self.assertEqual(after_core[SHADOW_INPUT.as_posix()], before[SHADOW_INPUT.as_posix()])
            core_outputs_before_cluster = {
                path.as_posix(): after_core[path.as_posix()]
                for path in CORE_OUTPUTS
            }

            cluster_result = _run(CLUSTER_SCRIPT, root)
            after_cluster = _raw_file_manifest(root)
            self.assertEqual(cluster_result.returncode, 0, cluster_result.stderr)
            self.assertEqual(cluster_result.stderr, "")
            self.assertEqual(
                set(after_cluster),
                {SHADOW_INPUT.as_posix()}
                | {p.as_posix() for p in CORE_OUTPUTS}
                | {p.as_posix() for p in CLUSTER_OUTPUTS},
            )
            self.assertEqual(after_cluster[SHADOW_INPUT.as_posix()], before[SHADOW_INPUT.as_posix()])
            self.assertEqual(
                {path.as_posix(): after_cluster[path.as_posix()] for path in CORE_OUTPUTS},
                core_outputs_before_cluster,
            )

            actual_fingerprints = {
                "core_stdout": hashlib.sha256(
                    _normalized_slashes(core_result.stdout).encode("utf-8")
                ).hexdigest(),
                "cluster_stdout": hashlib.sha256(
                    _normalized_slashes(cluster_result.stdout).encode("utf-8")
                ).hexdigest(),
            }
            actual_fingerprints.update(
                {
                    path.as_posix(): _canonical_csv_sha256(root / path)
                    for path in CORE_OUTPUTS | CLUSTER_OUTPUTS
                }
            )
            self.assertEqual(actual_fingerprints, CHAIN_FINGERPRINTS)

            core_fields, core_rows = _read_csv(root / CORE_METRICS)
            self.assertEqual(core_fields, CORE_COLUMNS)
            self.assertEqual(len(core_rows), 5)
            self.assertEqual(
                [row["step18_regime"] for row in core_rows],
                ["collapse_risk", "boundary_stress", "sustainable", "neutral", "neutral"],
            )
            expected_counts = {
                REPORT_DIR / "step18_regime_summary.csv": 4,
                REPORT_DIR / "step18_boundary_events.csv": 5,
                REPORT_DIR / "step18_collapse_events.csv": 5,
                REPORT_DIR / "step18_sustainable_topologies.csv": 5,
                REPORT_DIR / "step18_top_boundary_clusters.csv": 5,
                REPORT_DIR / "step18_top_collapse_clusters.csv": 5,
                REPORT_DIR / "step18_top_sustainable_clusters.csv": 5,
                REPORT_DIR / "step18_cluster_summary.csv": 4,
            }
            for path, expected_count in expected_counts.items():
                with self.subTest(path=path.as_posix()):
                    _, rows = _read_csv(root / path)
                    self.assertEqual(len(rows), expected_count)
            _, boundary_rows = _read_csv(root / REPORT_DIR / "step18_top_boundary_clusters.csv")
            _, collapse_rows = _read_csv(root / REPORT_DIR / "step18_top_collapse_clusters.csv")
            _, sustainable_rows = _read_csv(root / REPORT_DIR / "step18_top_sustainable_clusters.csv")
            self.assertEqual(boundary_rows[0]["tick_id"], "tick-boundary")
            self.assertEqual(collapse_rows[0]["tick_id"], "tick-collapse")
            self.assertEqual(sustainable_rows[0]["tick_id"], "tick-sustainable")

    @unittest.skipUnless(FULL_RUNTIME_AVAILABLE, "numpy/pandas fixture runtime required")
    def test_core_missing_input_creates_empty_report_directory_before_failure(self) -> None:
        with tempfile.TemporaryDirectory(prefix="step18_core_missing_") as temp_dir:
            root = Path(temp_dir)
            result = _run(CORE_SCRIPT, root)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "")
            self.assertIn("FileNotFoundError", result.stderr)
            self.assertIn(SHADOW_INPUT.as_posix(), _normalized_slashes(result.stderr))
            self.assertEqual(_raw_file_manifest(root), {})
            self.assertEqual(_directories(root), {"reports", "reports/step18"})

    @unittest.skipUnless(FULL_RUNTIME_AVAILABLE, "numpy/pandas fixture runtime required")
    def test_cluster_missing_input_has_no_filesystem_side_effect(self) -> None:
        with tempfile.TemporaryDirectory(prefix="step18_cluster_missing_") as temp_dir:
            root = Path(temp_dir)
            result = _run(CLUSTER_SCRIPT, root)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "")
            self.assertIn("FileNotFoundError", result.stderr)
            self.assertIn(CORE_METRICS.as_posix(), _normalized_slashes(result.stderr))
            self.assertEqual(_raw_file_manifest(root), {})
            self.assertEqual(_directories(root), set())

    @unittest.skipUnless(FULL_RUNTIME_AVAILABLE, "numpy/pandas fixture runtime required")
    def test_core_missing_declared_columns_fails_before_output_files(self) -> None:
        with tempfile.TemporaryDirectory(prefix="step18_core_columns_") as temp_dir:
            root = Path(temp_dir)
            _write_csv(root / SHADOW_INPUT, ({"current_score": "1"},))
            input_manifest = _raw_file_manifest(root)
            result = _run(CORE_SCRIPT, root)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "")
            self.assertIn("ValueError", result.stderr)
            self.assertIn("Missing required columns", result.stderr)
            self.assertEqual(_raw_file_manifest(root), input_manifest)
            self.assertEqual(_directories(root), {"live_logs", "reports", "reports/step18"})

    @unittest.skipUnless(FULL_RUNTIME_AVAILABLE, "numpy/pandas fixture runtime required")
    def test_core_implicit_shadow_risk_level_fails_closed(self) -> None:
        row = {column: "1" for column in REQUIRED_COLUMNS}
        with tempfile.TemporaryDirectory(prefix="step18_core_implicit_") as temp_dir:
            root = Path(temp_dir)
            _write_csv(root / SHADOW_INPUT, (row,))
            input_manifest = _raw_file_manifest(root)
            result = _run(CORE_SCRIPT, root)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "")
            self.assertIn("KeyError", result.stderr)
            self.assertIn("shadow_risk_level", result.stderr)
            self.assertEqual(_raw_file_manifest(root), input_manifest)
            self.assertEqual(_directories(root), {"live_logs", "reports", "reports/step18"})


if __name__ == "__main__":
    unittest.main()
