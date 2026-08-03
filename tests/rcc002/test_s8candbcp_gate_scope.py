#!/usr/bin/env python3
"""Independent tests for the RCC-002 S8 Track-1 mandatory gate."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import io
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[2]

MANIFEST_PATH = (
    "docs/review/evidence/"
    "RCC_002_S8CANDBCP_GATE_SCOPE_V1.json"
)
VERIFIER_PATH = (
    "scripts/rcc002/verify_s8candbcp_gate_scope.py"
)
RUNNER_PATH = "scripts/rcc002/run_s8candbcp_gate.py"

EXPECTED_MANIFEST_SHA256 = (
    "c2be410babdfb62813b2588a7de2473ae744c35b076c790f331b2113becf7723"
)
EXPECTED_VERIFIER_SHA256 = (
    "60e6c8c3a0c3f4dcd0c9ebfebbc22b6515b4dba0597575078cb182c2dc3e5eb3"
)
EXPECTED_RUNNER_SHA256 = (
    "a9245ba054d7698a35fa726f6884f2b482f61056cb9171cfbec2eb23466ddfa1"
)

POLICY_ID = "RCC002_S8CANDBCP_GATE_POLICY_V1"
EXPECTED_POLICY_PREIMAGE_SHA256 = (
    "27414251ea113e9f135f7ed93ce120bd0fe454575914083654b8c9d71e2bfbe1"
)

CURRENT_STATE_MODULES = (
    "tests/rcc002/s0/test_ingest.py",
    "tests/rcc002/s0/test_integrity.py",
    "tests/rcc002/s0/test_manifest.py",
    "tests/rcc002/s0/test_profiles.py",
    "tests/rcc002/s0/test_source_identity.py",
    "tests/rcc002/s1/test_normalize.py",
    "tests/rcc002/s1/test_numeric.py",
    "tests/rcc002/s1/test_row_id.py",
    "tests/rcc002/s1/test_schema.py",
    "tests/rcc002/s1/test_time.py",
    "tests/rcc002/s2/test_anomalies.py",
    "tests/rcc002/s2/test_duplicates.py",
    "tests/rcc002/s2/test_invariants.py",
    "tests/rcc002/s2/test_schema.py",
    "tests/rcc002/s2/test_segment.py",
    "tests/rcc002/s2/test_validate.py",
    "tests/rcc002/s3/test_compute.py",
    "tests/rcc002/s3/test_formulas.py",
    "tests/rcc002/s3/test_golden_fixtures.py",
    "tests/rcc002/s3/test_schema.py",
    "tests/rcc002/s3/test_segment.py",
    "tests/rcc002/s3/test_state.py",
    "tests/rcc002/s4/test_compute.py",
    "tests/rcc002/s5/test_compute.py",
    "tests/rcc002/s5/test_formulas.py",
    "tests/rcc002/s5/test_golden_fixtures.py",
    "tests/rcc002/s5/test_schema.py",
    "tests/rcc002/s5/test_state.py",
    "tests/rcc002/s6/test_compute.py",
    "tests/rcc002/s6/test_formulas.py",
    "tests/rcc002/s6/test_golden_fixtures.py",
    "tests/rcc002/s6/test_reason_codes.py",
    "tests/rcc002/s6/test_schema.py",
    "tests/rcc002/s7/test_compute.py",
    "tests/rcc002/s7/test_formulas.py",
    "tests/rcc002/s7/test_golden_fixtures.py",
    "tests/rcc002/s7/test_planning.py",
    "tests/rcc002/s7/test_reason_codes.py",
    "tests/rcc002/s7/test_schema.py",
    "tests/rcc002/test_constants.py",
    "tests/rcc002/test_reason_codes.py",
    "tests/rcc002/test_s8bcp001_implementation_correction.py",
    "tests/rcc002/test_s8candbcp_gate_scope.py",
    "tests/rcc002/test_s8candbcp_rev2_normative_ledger.py",
    "tests/rcc002/test_s8candbcp_rev2_track1_normative_scope.py",
)

HISTORICAL_REPLAY_ADAPTER_MODULES = (
    "tests/rcc002/test_s8rr002_manifest_correction_historical_replay.py",
    "tests/rcc002/test_s8rr003_normative_ledger_historical_replay.py",
)

HISTORICAL_AUDIT_ONLY_MODULES = (
    "tests/rcc002/test_s8rr002_manifest_correction.py",
    "tests/rcc002/test_s8rr003_normative_ledger.py",
)

EXCLUDED_TRACK2_CANDIDATE_MODULES = (
    "tests/rcc002/s8/test_artifact_class.py",
    "tests/rcc002/s8/test_canonical.py",
    "tests/rcc002/s8/test_field_registry.py",
    "tests/rcc002/s8/test_identity.py",
    "tests/rcc002/s8/test_manifests.py",
    "tests/rcc002/s8/test_projection.py",
    "tests/rcc002/s8/test_publication.py",
    "tests/rcc002/s8/test_reconciliation.py",
    "tests/rcc002/s8/test_states.py",
    "tests/rcc002/s8/test_validation.py",
    "tests/rcc002/s8/test_views.py",
)

CATEGORY_ORDER = (
    "current_state_modules",
    "historical_replay_adapter_modules",
    "historical_audit_only_modules",
    "excluded_track2_candidate_modules",
)

CATEGORY_PATHS = {
    "current_state_modules": CURRENT_STATE_MODULES,
    "historical_replay_adapter_modules": (
        HISTORICAL_REPLAY_ADAPTER_MODULES
    ),
    "historical_audit_only_modules": (
        HISTORICAL_AUDIT_ONLY_MODULES
    ),
    "excluded_track2_candidate_modules": (
        EXCLUDED_TRACK2_CANDIDATE_MODULES
    ),
}

GOVERNED_TRACK1_MODULES = (
    CURRENT_STATE_MODULES
    + HISTORICAL_REPLAY_ADAPTER_MODULES
    + HISTORICAL_AUDIT_ONLY_MODULES
)

EXECUTABLE_MODULES = (
    CURRENT_STATE_MODULES
    + HISTORICAL_REPLAY_ADAPTER_MODULES
)

POLICY_PATHS = (
    GOVERNED_TRACK1_MODULES
    + EXCLUDED_TRACK2_CANDIDATE_MODULES
)

EXPECTED_COUNTS = {
    "policy_path_count": 60,
    "governed_track1_module_count": 49,
    "current_state_module_count": 45,
    "historical_replay_adapter_module_count": 2,
    "historical_audit_only_module_count": 2,
    "excluded_track2_candidate_module_count": 11,
    "executable_module_count": 47,
}

EXPECTED_PATH_DIGESTS = {
    "current_state_modules": (
        "f9c7f83efe8ce803137164c156e0e96b05efa06638c0837bb980dc6cf316bda0"
    ),
    "historical_replay_adapter_modules": (
        "afc9cc6661e4a850f28cfd98029fc9d50da1c36428c1acc07307f955da73b00c"
    ),
    "historical_audit_only_modules": (
        "14e9b8d244a09f5cc5409d3ca080a5436e2f9c8d5c0db01a95dec97b47c749a6"
    ),
    "excluded_track2_candidate_modules": (
        "dd0c85003474bdc4672e8eebdef16f61ae7dd9568a7de0f33d4c613f0e786f3a"
    ),
    "governed_track1_modules": (
        "188186713fc48329629439d7c5cddaade388723270236126fb41f1bd756f3d2c"
    ),
    "executable_modules": (
        "b80cda1c8adf75c7b687f93952dc897e1c0f1e4c06dab5bd6e5b777d19fa653a"
    ),
    "policy_paths": (
        "b611d04c24a509c13701570474057b661993c929c4655db2727d22943da95641"
    ),
}


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def path_digest(paths: tuple[str, ...] | list[str]) -> str:
    raw = json.dumps(
        list(paths),
        ensure_ascii=True,
        separators=(",", ":"),
    ).encode("ascii")
    return sha256_hex(raw)


def build_policy_preimage(
    categories: dict[str, tuple[str, ...]] = CATEGORY_PATHS,
) -> bytes:
    lines = [f"policy_id={POLICY_ID}"]

    for category in CATEGORY_ORDER:
        lines.append(f"category={category}")

        for path in categories[category]:
            lines.append(f"path={path}")

    return ("\n".join(lines) + "\n").encode("ascii")


def load_module(name: str, path: Path) -> types.ModuleType:
    specification = importlib.util.spec_from_file_location(
        name,
        path,
    )

    if specification is None or specification.loader is None:
        raise AssertionError(f"unable to load module: {path}")

    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


VERIFIER = load_module(
    "_s8candbcp_gate_scope_test_verifier",
    REPO_ROOT / VERIFIER_PATH,
)
RUNNER = load_module(
    "_s8candbcp_gate_scope_test_runner",
    REPO_ROOT / RUNNER_PATH,
)


def load_manifest_document() -> dict:
    return json.loads(
        (REPO_ROOT / MANIFEST_PATH).read_text(
            encoding="ascii"
        )
    )


def passing_module_source() -> bytes:
    return (
        "import unittest\n"
        "\n"
        "class SyntheticPassingTest(unittest.TestCase):\n"
        "    def test_pass(self):\n"
        "        self.assertTrue(True)\n"
    ).encode("ascii")


def failing_module_source() -> bytes:
    return (
        "import unittest\n"
        "\n"
        "class SyntheticFailingTest(unittest.TestCase):\n"
        "    def test_fail(self):\n"
        "        self.fail('deliberate synthetic failure')\n"
    ).encode("ascii")


def error_module_source() -> bytes:
    return (
        "import unittest\n"
        "\n"
        "class SyntheticErrorTest(unittest.TestCase):\n"
        "    def test_error(self):\n"
        "        raise RuntimeError('deliberate synthetic error')\n"
    ).encode("ascii")


def syntax_error_module_source() -> bytes:
    return b"this is deliberately invalid python !!!\n"


def import_marker_module_source(marker: Path) -> bytes:
    text = (
        "from pathlib import Path\n"
        f"Path({str(marker)!r}).write_text("
        "'IMPORTED', encoding='ascii')\n"
        "import unittest\n"
        "\n"
        "class SyntheticMarkerTest(unittest.TestCase):\n"
        "    def test_pass(self):\n"
        "        self.assertTrue(True)\n"
    )
    return text.encode("ascii")


def ensure_test_packages(root: Path, module_path: str) -> None:
    parent = (root / module_path).parent

    while parent != root:
        relative = parent.relative_to(root).as_posix()

        if relative == "tests" or relative.startswith("tests/"):
            init_path = parent / "__init__.py"
            init_path.parent.mkdir(parents=True, exist_ok=True)
            init_path.touch(exist_ok=True)

        parent = parent.parent


def write_file(root: Path, relative: str, raw: bytes) -> None:
    target = root / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(raw)


def copy_production_gate_artifacts(root: Path) -> None:
    for relative in (
        MANIFEST_PATH,
        VERIFIER_PATH,
        RUNNER_PATH,
    ):
        source = REPO_ROOT / relative
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)


def sitecustomize_source() -> bytes:
    return r'''import _io
import builtins
import io
import os

_guard_root = os.path.abspath(
    os.environ["RCC002_EXCLUDED_GUARD_ROOT"]
)
_guard_log = os.environ["RCC002_EXCLUDED_GUARD_LOG"]

_original_builtin_open = builtins.open
_original_io_open = io.open
_original_open_code = _io.open_code
_original_os_open = os.open
_original_stat = os.stat
_original_lstat = os.lstat
_original_scandir = os.scandir
_original_listdir = os.listdir


def _as_absolute(value):
    try:
        raw = os.fspath(value)
    except TypeError:
        return None

    if isinstance(raw, bytes):
        raw = os.fsdecode(raw)

    return os.path.abspath(raw)


def _is_excluded(value):
    absolute = _as_absolute(value)

    if absolute is None:
        return False

    return (
        absolute == _guard_root
        or absolute.startswith(_guard_root + os.sep)
    )


def _block(operation, value):
    if not _is_excluded(value):
        return

    with _original_builtin_open(
        _guard_log,
        "a",
        encoding="ascii",
    ) as stream:
        stream.write(
            operation + ":" + str(_as_absolute(value)) + "\n"
        )

    raise RuntimeError(
        "excluded Track-2 access blocked: "
        + operation
        + ":"
        + str(_as_absolute(value))
    )


def guarded_builtin_open(file, *args, **kwargs):
    _block("builtins.open", file)
    return _original_builtin_open(file, *args, **kwargs)


def guarded_io_open(file, *args, **kwargs):
    _block("io.open", file)
    return _original_io_open(file, *args, **kwargs)


def guarded_open_code(path):
    _block("_io.open_code", path)
    return _original_open_code(path)


def guarded_os_open(path, *args, **kwargs):
    _block("os.open", path)
    return _original_os_open(path, *args, **kwargs)


def guarded_stat(path, *args, **kwargs):
    _block("os.stat", path)
    return _original_stat(path, *args, **kwargs)


def guarded_lstat(path, *args, **kwargs):
    _block("os.lstat", path)
    return _original_lstat(path, *args, **kwargs)


def guarded_scandir(path="."):
    _block("os.scandir", path)
    return _original_scandir(path)


def guarded_listdir(path="."):
    _block("os.listdir", path)
    return _original_listdir(path)


builtins.open = guarded_builtin_open
io.open = guarded_io_open
_io.open_code = guarded_open_code
os.open = guarded_os_open
os.stat = guarded_stat
os.lstat = guarded_lstat
os.scandir = guarded_scandir
os.listdir = guarded_listdir
'''.encode("ascii")


def build_synthetic_repository(
    root: Path,
    *,
    include_excluded: bool = False,
    overrides: dict[str, bytes] | None = None,
    extra_modules: dict[str, bytes] | None = None,
    install_excluded_guard: bool = False,
) -> Path | None:
    copy_production_gate_artifacts(root)

    selected_overrides = {} if overrides is None else overrides
    selected_extra = {} if extra_modules is None else extra_modules

    for path in GOVERNED_TRACK1_MODULES:
        ensure_test_packages(root, path)

        if path in selected_overrides:
            raw = selected_overrides[path]
        elif path in HISTORICAL_AUDIT_ONLY_MODULES:
            raw = failing_module_source()
        else:
            raw = passing_module_source()

        write_file(root, path, raw)

    for path, raw in selected_extra.items():
        ensure_test_packages(root, path)
        write_file(root, path, raw)

    if include_excluded:
        for path in EXCLUDED_TRACK2_CANDIDATE_MODULES:
            ensure_test_packages(root, path)
            write_file(root, path, failing_module_source())

    if not install_excluded_guard:
        return None

    guard_log = root / "excluded-track2-access.log"
    write_file(root, "sitecustomize.py", sitecustomize_source())
    return guard_log


def execute_synthetic_gate(
    root: Path,
    *,
    guard_log: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["PYTHONPATH"] = str(root)

    if guard_log is not None:
        environment["RCC002_EXCLUDED_GUARD_ROOT"] = str(
            root / "tests/rcc002/s8"
        )
        environment["RCC002_EXCLUDED_GUARD_LOG"] = str(
            guard_log
        )

    return subprocess.run(
        [sys.executable, str(root / RUNNER_PATH)],
        cwd=root,
        env=environment,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def parse_runner_report(
    result: subprocess.CompletedProcess[str],
) -> dict:
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise AssertionError(
            f"runner stdout is not JSON:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        ) from exc


def assert_positive_control(
    testcase: unittest.TestCase,
    result: subprocess.CompletedProcess[str],
) -> dict:
    output = result.stdout + result.stderr

    testcase.assertEqual(
        result.returncode,
        0,
        msg=output,
    )
    testcase.assertEqual(
        re.findall(r"Ran ([0-9]+) tests? in ", output),
        ["47"],
        msg=output,
    )
    testcase.assertEqual(
        len(re.findall(r"(?m)^OK$", output)),
        1,
        msg=output,
    )

    report = parse_runner_report(result)

    testcase.assertEqual(report["result"], "PASS")
    testcase.assertEqual(
        report["discovered_module_count"],
        49,
    )
    testcase.assertEqual(
        report["loaded_module_count"],
        47,
    )
    testcase.assertEqual(
        report["executable_module_count"],
        47,
    )
    testcase.assertEqual(
        report["test_case_count"],
        47,
    )
    testcase.assertEqual(report["failure_count"], 0)
    testcase.assertEqual(report["error_count"], 0)
    testcase.assertFalse(
        report["track2_subtree_children_enumerated"]
    )
    testcase.assertFalse(
        report["protected_builder_accessed"]
    )

    return report


class IndependentAuthorityTests(unittest.TestCase):
    def test_exact_counts_and_category_partition(self) -> None:
        self.assertEqual(len(CURRENT_STATE_MODULES), 45)
        self.assertEqual(
            len(HISTORICAL_REPLAY_ADAPTER_MODULES),
            2,
        )
        self.assertEqual(
            len(HISTORICAL_AUDIT_ONLY_MODULES),
            2,
        )
        self.assertEqual(
            len(EXCLUDED_TRACK2_CANDIDATE_MODULES),
            11,
        )
        self.assertEqual(len(GOVERNED_TRACK1_MODULES), 49)
        self.assertEqual(len(EXECUTABLE_MODULES), 47)
        self.assertEqual(len(POLICY_PATHS), 60)
        self.assertEqual(len(set(POLICY_PATHS)), 60)

    def test_exact_path_digests(self) -> None:
        actual = {
            "current_state_modules": path_digest(
                CURRENT_STATE_MODULES
            ),
            "historical_replay_adapter_modules": path_digest(
                HISTORICAL_REPLAY_ADAPTER_MODULES
            ),
            "historical_audit_only_modules": path_digest(
                HISTORICAL_AUDIT_ONLY_MODULES
            ),
            "excluded_track2_candidate_modules": path_digest(
                EXCLUDED_TRACK2_CANDIDATE_MODULES
            ),
            "governed_track1_modules": path_digest(
                GOVERNED_TRACK1_MODULES
            ),
            "executable_modules": path_digest(
                EXECUTABLE_MODULES
            ),
            "policy_paths": path_digest(POLICY_PATHS),
        }

        self.assertEqual(actual, EXPECTED_PATH_DIGESTS)

    def test_exact_policy_preimage(self) -> None:
        preimage = build_policy_preimage()

        self.assertEqual(len(preimage.splitlines()), 65)
        self.assertEqual(len(preimage), 2687)
        self.assertEqual(
            sha256_hex(preimage),
            EXPECTED_POLICY_PREIMAGE_SHA256,
        )
        self.assertTrue(preimage.endswith(b"\n"))
        self.assertFalse(preimage.endswith(b"\n\n"))

    def test_production_artifact_hashes(self) -> None:
        expected = {
            MANIFEST_PATH: EXPECTED_MANIFEST_SHA256,
            VERIFIER_PATH: EXPECTED_VERIFIER_SHA256,
            RUNNER_PATH: EXPECTED_RUNNER_SHA256,
        }

        for relative, digest in expected.items():
            with self.subTest(path=relative):
                self.assertEqual(
                    sha256_hex(
                        (REPO_ROOT / relative).read_bytes()
                    ),
                    digest,
                )

    def test_manifest_verifies_against_independent_authority(
        self,
    ) -> None:
        result = VERIFIER.verify_gate_scope(REPO_ROOT)

        self.assertEqual(result["result"], "PASS")
        self.assertEqual(
            result["current_state_modules"],
            list(CURRENT_STATE_MODULES),
        )
        self.assertEqual(
            result["historical_replay_adapter_modules"],
            list(HISTORICAL_REPLAY_ADAPTER_MODULES),
        )
        self.assertEqual(
            result["historical_audit_only_modules"],
            list(HISTORICAL_AUDIT_ONLY_MODULES),
        )
        self.assertEqual(
            result["excluded_track2_candidate_modules"],
            list(EXCLUDED_TRACK2_CANDIDATE_MODULES),
        )
        self.assertEqual(
            result["governed_track1_modules"],
            list(GOVERNED_TRACK1_MODULES),
        )
        self.assertEqual(
            result["executable_modules"],
            list(EXECUTABLE_MODULES),
        )

    def test_runner_constants_match_independent_authority(
        self,
    ) -> None:
        self.assertEqual(
            RUNNER.EXPECTED_POLICY_PATH_COUNT,
            60,
        )
        self.assertEqual(
            RUNNER.EXPECTED_GOVERNED_MODULE_COUNT,
            49,
        )
        self.assertEqual(
            RUNNER.EXPECTED_CURRENT_MODULE_COUNT,
            45,
        )
        self.assertEqual(
            RUNNER.EXPECTED_REPLAY_MODULE_COUNT,
            2,
        )
        self.assertEqual(
            RUNNER.EXPECTED_AUDIT_MODULE_COUNT,
            2,
        )
        self.assertEqual(
            RUNNER.EXPECTED_EXCLUDED_MODULE_COUNT,
            11,
        )
        self.assertEqual(
            RUNNER.EXPECTED_EXECUTABLE_MODULE_COUNT,
            47,
        )
        self.assertEqual(
            RUNNER.EXPECTED_POLICY_PREIMAGE_SHA256,
            EXPECTED_POLICY_PREIMAGE_SHA256,
        )

    def test_protected_builder_and_track2_are_excluded(
        self,
    ) -> None:
        self.assertNotIn(
            "scripts/build_rcc002_spec_bundle.py",
            POLICY_PATHS,
        )
        self.assertFalse(
            any(
                path.startswith("tests/rcc002/s8/")
                for path in GOVERNED_TRACK1_MODULES
            )
        )
        self.assertTrue(
            all(
                path.startswith("tests/rcc002/s8/")
                for path in EXCLUDED_TRACK2_CANDIDATE_MODULES
            )
        )


class ManifestMutationTests(unittest.TestCase):
    def assert_manifest_rejected(
        self,
        document: dict,
    ) -> None:
        with self.assertRaises(
            VERIFIER.ScopeVerificationError
        ):
            VERIFIER.validate_manifest(document)

    def test_missing_path_is_rejected(self) -> None:
        document = load_manifest_document()
        document["current_state_modules"].pop(0)
        self.assert_manifest_rejected(document)

    def test_extra_path_is_rejected(self) -> None:
        document = load_manifest_document()
        document["current_state_modules"].append(
            "tests/rcc002/test_extra_policy_path.py"
        )
        document["current_state_modules"].sort()
        self.assert_manifest_rejected(document)

    def test_duplicate_path_is_rejected(self) -> None:
        document = load_manifest_document()
        document["current_state_modules"].append(
            document["current_state_modules"][0]
        )
        document["current_state_modules"].sort()
        self.assert_manifest_rejected(document)

    def test_reordered_path_is_rejected(self) -> None:
        document = load_manifest_document()
        document["current_state_modules"] = list(
            reversed(document["current_state_modules"])
        )
        self.assert_manifest_rejected(document)

    def test_unsafe_path_is_rejected(self) -> None:
        document = load_manifest_document()
        document["current_state_modules"][0] = (
            "tests/rcc002/../unsafe/test_escape.py"
        )
        document["current_state_modules"].sort()
        self.assert_manifest_rejected(document)

    def test_same_count_substitution_is_rejected(self) -> None:
        document = load_manifest_document()
        document["current_state_modules"][0] = (
            "tests/rcc002/s0/test_same_count_substitute.py"
        )
        document["current_state_modules"].sort()
        self.assert_manifest_rejected(document)

    def test_pairwise_category_overlap_is_rejected(self) -> None:
        pairs = (
            (
                "current_state_modules",
                "historical_replay_adapter_modules",
            ),
            (
                "current_state_modules",
                "historical_audit_only_modules",
            ),
            (
                "current_state_modules",
                "excluded_track2_candidate_modules",
            ),
            (
                "historical_replay_adapter_modules",
                "historical_audit_only_modules",
            ),
            (
                "historical_replay_adapter_modules",
                "excluded_track2_candidate_modules",
            ),
            (
                "historical_audit_only_modules",
                "excluded_track2_candidate_modules",
            ),
        )

        for target_category, source_category in pairs:
            with self.subTest(
                target=target_category,
                source=source_category,
            ):
                document = load_manifest_document()
                document[target_category][0] = document[
                    source_category
                ][0]
                document[target_category].sort()
                self.assert_manifest_rejected(document)

    def test_bidirectional_reclassification_is_rejected(
        self,
    ) -> None:
        pairs = (
            (
                "current_state_modules",
                "historical_replay_adapter_modules",
            ),
            (
                "current_state_modules",
                "historical_audit_only_modules",
            ),
            (
                "current_state_modules",
                "excluded_track2_candidate_modules",
            ),
        )

        for left, right in pairs:
            for source, target in ((left, right), (right, left)):
                with self.subTest(source=source, target=target):
                    document = load_manifest_document()
                    moved = document[source].pop(0)
                    document[target].append(moved)
                    document[target].sort()
                    self.assert_manifest_rejected(document)

    def test_wrong_metadata_and_counts_are_rejected(self) -> None:
        mutations = (
            ("policy_id", "WRONG_POLICY"),
            ("scope_id", "WRONG_SCOPE"),
        )

        for key, value in mutations:
            with self.subTest(key=key):
                document = load_manifest_document()
                document[key] = value
                self.assert_manifest_rejected(document)

        document = load_manifest_document()
        document["counts"]["executable_module_count"] = 48
        self.assert_manifest_rejected(document)

    def test_wrong_policy_digest_is_rejected(self) -> None:
        document = load_manifest_document()
        document["policy_preimage_rule"]["sha256"] = "0" * 64
        self.assert_manifest_rejected(document)

    def test_wrong_path_digest_is_rejected(self) -> None:
        document = load_manifest_document()
        document["path_digests"]["policy_paths"] = "0" * 64
        self.assert_manifest_rejected(document)

    def test_manifest_byte_drift_is_rejected_before_json_use(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory(
            prefix="rcc002-gate-manifest-drift-",
        ) as temporary:
            root = Path(temporary)
            document = load_manifest_document()
            document["policy_id"] = "DRIFTED"
            raw = (
                json.dumps(
                    document,
                    ensure_ascii=True,
                    indent=2,
                )
                + "\n"
            ).encode("ascii")
            write_file(root, MANIFEST_PATH, raw)

            with self.assertRaises(
                VERIFIER.ScopeVerificationError
            ) as context:
                VERIFIER.load_manifest(root)

            self.assertEqual(
                context.exception.invariant,
                "scope_manifest_digest_mismatch",
            )


class RunnerUnitTests(unittest.TestCase):
    def valid_scope_result(self) -> dict:
        return VERIFIER.verify_gate_scope(REPO_ROOT)

    def test_runner_reconstructs_exact_policy_digest(
        self,
    ) -> None:
        result = self.valid_scope_result()
        preimage = RUNNER.reconstruct_policy_preimage(result)

        self.assertEqual(len(preimage.splitlines()), 65)
        self.assertEqual(len(preimage), 2687)
        self.assertEqual(
            sha256_hex(preimage),
            EXPECTED_POLICY_PREIMAGE_SHA256,
        )

    def test_runner_rejects_same_count_policy_substitution(
        self,
    ) -> None:
        result = self.valid_scope_result()
        result["current_state_modules"][0] = (
            "tests/rcc002/s0/test_runner_substitute.py"
        )
        result["current_state_modules"].sort()

        with self.assertRaises(RUNNER.GateRunnerError):
            RUNNER.validate_scope_result(result)

    def test_runner_rejects_false_executable_union(
        self,
    ) -> None:
        result = self.valid_scope_result()
        executable = list(result["executable_modules"])
        executable[-1] = (
            HISTORICAL_AUDIT_ONLY_MODULES[0]
        )
        result["executable_modules"] = executable

        with self.assertRaises(RUNNER.GateRunnerError):
            RUNNER.validate_scope_result(result)

    def test_scope_validation_occurs_before_discovery_and_import(
        self,
    ) -> None:
        error = RUNNER.GateRunnerError(
            "synthetic_scope_failure",
            "expected",
        )

        with mock.patch.object(
            RUNNER,
            "obtain_scope_authority",
            side_effect=error,
        ), mock.patch.object(
            RUNNER,
            "discover_governed_modules",
        ) as discover, mock.patch.object(
            RUNNER,
            "load_test_module",
        ) as load:
            with self.assertRaises(RUNNER.GateRunnerError):
                RUNNER.run_gate(REPO_ROOT)

        discover.assert_not_called()
        load.assert_not_called()

    def test_scope_only_performs_no_discovery_or_import(
        self,
    ) -> None:
        scope_result = self.valid_scope_result()
        categories = RUNNER.validate_scope_result(
            scope_result
        )

        with mock.patch.object(
            RUNNER,
            "obtain_scope_authority",
            return_value=(scope_result, categories),
        ), mock.patch.object(
            RUNNER,
            "discover_governed_modules",
        ) as discover, mock.patch.object(
            RUNNER,
            "load_test_module",
        ) as load:
            report = RUNNER.run_scope_only(REPO_ROOT)

        self.assertEqual(report["result"], "PASS")
        self.assertFalse(
            report["filesystem_discovery_performed"]
        )
        self.assertFalse(
            report["test_module_imports_performed"]
        )
        discover.assert_not_called()
        load.assert_not_called()

    def test_loader_calls_are_exactly_47_once_and_in_order(
        self,
    ) -> None:
        calls: list[str] = []

        def fake_load(
            _repo_root: Path,
            path: str,
        ) -> types.ModuleType:
            calls.append(path)
            module = types.ModuleType(
                path[:-3].replace("/", ".")
            )

            class SyntheticPassingTest(unittest.TestCase):
                def test_pass(self) -> None:
                    self.assertTrue(True)

            setattr(
                module,
                "SyntheticPassingTest",
                SyntheticPassingTest,
            )
            return module

        with mock.patch.object(
            RUNNER,
            "load_test_module",
            side_effect=fake_load,
        ):
            suite, loaded = RUNNER.build_test_suite(
                REPO_ROOT,
                EXECUTABLE_MODULES,
            )

        self.assertEqual(loaded, 47)
        self.assertEqual(suite.countTestCases(), 47)
        self.assertEqual(tuple(calls), EXECUTABLE_MODULES)
        self.assertEqual(len(calls), len(set(calls)))
        self.assertFalse(
            set(calls) & set(HISTORICAL_AUDIT_ONLY_MODULES)
        )
        self.assertFalse(
            set(calls) & set(EXCLUDED_TRACK2_CANDIDATE_MODULES)
        )

    def test_scope_verifier_byte_drift_is_rejected(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory(
            prefix="rcc002-gate-verifier-drift-",
        ) as temporary:
            root = Path(temporary)
            raw = (REPO_ROOT / VERIFIER_PATH).read_bytes()
            write_file(
                root,
                VERIFIER_PATH,
                raw + b"\n",
            )

            with self.assertRaises(
                RUNNER.GateRunnerError
            ) as context:
                RUNNER.load_scope_verifier(root)

            self.assertEqual(
                context.exception.invariant,
                "scope_verifier_digest_mismatch",
            )


class ProductionPositiveAndNegativeControls(
    unittest.TestCase
):
    def test_positive_control_a_clean_track1_tree(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory(
            prefix="rcc002-gate-positive-a-",
        ) as temporary:
            root = Path(temporary)
            build_synthetic_repository(root)
            result = execute_synthetic_gate(root)
            assert_positive_control(self, result)

    def test_positive_control_b_track2_exists_but_is_untouched(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory(
            prefix="rcc002-gate-positive-b-",
        ) as temporary:
            root = Path(temporary)
            guard_log = build_synthetic_repository(
                root,
                include_excluded=True,
                install_excluded_guard=True,
            )
            self.assertIsNotNone(guard_log)

            result = execute_synthetic_gate(
                root,
                guard_log=guard_log,
            )
            assert_positive_control(self, result)

            assert guard_log is not None

            if guard_log.exists():
                self.assertEqual(
                    guard_log.read_text(
                        encoding="ascii"
                    ),
                    "",
                )

    def test_unknown_extra_module_rejected_before_import(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory(
            prefix="rcc002-gate-extra-before-import-",
        ) as temporary:
            root = Path(temporary)
            marker = root / "import-marker.txt"
            guarded_module = EXECUTABLE_MODULES[0]

            build_synthetic_repository(
                root,
                overrides={
                    guarded_module: (
                        import_marker_module_source(marker)
                    ),
                },
                extra_modules={
                    "tests/rcc002/test_unknown_extra.py": (
                        passing_module_source()
                    ),
                },
            )

            result = execute_synthetic_gate(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                "disk_discovery_count_mismatch",
                result.stderr,
            )
            self.assertFalse(marker.exists())

    def test_missing_governed_module_is_rejected(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory(
            prefix="rcc002-gate-missing-module-",
        ) as temporary:
            root = Path(temporary)
            build_synthetic_repository(root)
            missing = root / GOVERNED_TRACK1_MODULES[0]
            missing.unlink()

            result = execute_synthetic_gate(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                "disk_discovery_count_mismatch",
                result.stderr,
            )

    def test_import_failure_returns_nonzero(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory(
            prefix="rcc002-gate-import-failure-",
        ) as temporary:
            root = Path(temporary)
            build_synthetic_repository(
                root,
                overrides={
                    EXECUTABLE_MODULES[0]: (
                        syntax_error_module_source()
                    ),
                },
            )

            result = execute_synthetic_gate(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                "executable_module_import_failure",
                result.stderr,
            )

    def test_test_failure_returns_nonzero(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory(
            prefix="rcc002-gate-test-failure-",
        ) as temporary:
            root = Path(temporary)
            build_synthetic_repository(
                root,
                overrides={
                    EXECUTABLE_MODULES[0]: (
                        failing_module_source()
                    ),
                },
            )

            result = execute_synthetic_gate(root)
            output = result.stdout + result.stderr

            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(
                re.findall(
                    r"Ran ([0-9]+) tests? in ",
                    output,
                ),
                ["47"],
            )
            self.assertNotRegex(output, r"(?m)^OK$")
            report = parse_runner_report(result)
            self.assertEqual(report["result"], "FAIL")
            self.assertEqual(report["failure_count"], 1)
            self.assertEqual(report["error_count"], 0)

    def test_test_error_returns_nonzero(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory(
            prefix="rcc002-gate-test-error-",
        ) as temporary:
            root = Path(temporary)
            build_synthetic_repository(
                root,
                overrides={
                    EXECUTABLE_MODULES[0]: (
                        error_module_source()
                    ),
                },
            )

            result = execute_synthetic_gate(root)
            output = result.stdout + result.stderr

            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(
                re.findall(
                    r"Ran ([0-9]+) tests? in ",
                    output,
                ),
                ["47"],
            )
            self.assertNotRegex(output, r"(?m)^OK$")
            report = parse_runner_report(result)
            self.assertEqual(report["result"], "FAIL")
            self.assertEqual(report["failure_count"], 0)
            self.assertEqual(report["error_count"], 1)


if __name__ == "__main__":
    unittest.main(verbosity=1)
