#!/usr/bin/env python3
"""Historical replay adapter for certified RCC-002 S8-RR-003."""

from __future__ import annotations

import ast
import copy
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path, PurePosixPath
from typing import Callable


REPO_ROOT = Path(__file__).resolve().parents[2]

SCOPE_PATH = (
    "docs/review/evidence/"
    "RCC_002_S8RR003_NORMATIVE_LEDGER_SCOPE_V1.json"
)
VERIFIER_PATH = "scripts/rcc002/verify_s8rr003_normative_ledger.py"
TEST_MODULE_PATH = "tests/rcc002/test_s8rr003_normative_ledger.py"

DP_PATH = (
    "docs/specifications/"
    "RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md"
)
RM_PATH = (
    "docs/specifications/"
    "RCC_002_REPRODUCIBILITY_AND_MANIFEST_2026-07-23.md"
)

NORMATIVE_LEDGER_PATH = (
    "docs/review/evidence/"
    "RCC_002_S8BCP001_REV2_NORMATIVE_BUNDLE_SHA256SUMS_2026-07-30.txt"
)
ROOT_LEDGER_PATH = "SHA256SUMS"

DP_FROZEN_COPY_PATH = (
    "docs/review/evidence/"
    "RCC_002_S8RR002_HISTORICAL_DATA_PIPELINE_SPECIFICATION_"
    "0_8_0_CERTIFIED_COPY_2026-08-02.txt"
)
RM_FROZEN_COPY_PATH = (
    "docs/review/evidence/"
    "RCC_002_S8RR002_HISTORICAL_REPRODUCIBILITY_AND_MANIFEST_"
    "0_9_0_CERTIFIED_COPY_2026-08-02.txt"
)
ROOT_LEDGER_FROZEN_COPY_PATH = (
    "docs/review/evidence/"
    "RCC_002_S8CANDBCP_REV2_NORMATIVE_LEDGER_HISTORICAL_COPY_"
    "2026-08-01.txt"
)

PROTECTED_BUILDER_PATH = "scripts/build_rcc002_spec_bundle.py"
EXCLUDED_TRACK2_PREFIX = "tests/rcc002/s8/"

EXPECTED_SCOPE_SHA256 = (
    "ee939b42778a28982eef40fbd0c02d861d043b85f72634e6a2f3f7d8fa2da396"
)
EXPECTED_VERIFIER_SHA256 = (
    "48c92bae7c8b5bd51c965fcd48917ffe0a3ee84c9dfe32bd490abab88f9b6cea"
)
EXPECTED_TEST_MODULE_SHA256 = (
    "07afd3045f60c8b1cf8109da8b2b4162c3b4d664dfb4108662d0fec005cbdbce"
)
EXPECTED_NORMATIVE_LEDGER_SHA256 = (
    "a34e5139dadfdfa9d72210ac12b733b0493b00c8396f8e48680634dfb5988e43"
)
EXPECTED_ROOT_LEDGER_SHA256 = (
    "469236e8459a9ad86d3434a67a81f037a699e076c6a8af8b0a887ecb60a30302"
)

EXPECTED_HISTORICAL_PATH_DIGEST = (
    "b323bde6b213fe47c050430df8652b7591f45bbe5ab81ec43969a195a5c5e4a2"
)
EXPECTED_RR002_PATH_DIGEST = (
    "f655ef0e91feaec65f14ef7d53b0059164bf2c50d5335bb05f02db3e992c7469"
)
EXPECTED_RR003_PATH_DIGEST = (
    "95aa3454eb631e1bb2ea2a1dc9248c2b760d5556a8dffd087b176025170c9031"
)
EXPECTED_CURRENT_PATH_DIGEST = (
    "57601441c4dcdce4204ddaa166685e9c16717f08f3f133f1241767acf7c00791"
)
EXPECTED_SPECIAL_PATH_DIGEST = (
    "31f9fb1a931efc45a8e7f3b819a0fe778bcbcc3e1f098b1def691f2681adb78a"
)
EXPECTED_GENERIC_PATH_DIGEST = (
    "288b413aaebb8bcc8a4d74b2a6159236581eaac44d13425779dabbeae10f62d7"
)
EXPECTED_TEST_METHOD_NAME_DIGEST = (
    "52e20de998e4304d4337c2f568869ada206a9b59ecd99d19fa2fabff9b8a96a1"
)

EXPECTED_SCOPE_KEYS = {
    "scope_schema_version",
    "scope_id",
    "correction_id",
    "finding_in_scope",
    "ledger_path",
    "historical_ledger_sha256",
    "path_ordering",
    "entry_format",
    "expected_current_entry_count",
    "consumed_by",
    "historical_normative_paths",
    "s8rr002_correction_outputs",
    "s8rr003_lifecycle_outputs",
    "current_ledger_paths",
}

SPECIAL_PATHS = (
    VERIFIER_PATH,
    TEST_MODULE_PATH,
    DP_PATH,
    RM_PATH,
    SCOPE_PATH,
    NORMATIVE_LEDGER_PATH,
)

LEDGER_LINE_RE = re.compile(
    rb"^([0-9a-f]{64})  \./([^\\\r\n]+)$"
)


class ReplayError(AssertionError):
    """Raised when the historical replay contract is violated."""


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def path_digest(paths: tuple[str, ...] | list[str]) -> str:
    payload = json.dumps(
        list(paths),
        ensure_ascii=True,
        separators=(",", ":"),
    ).encode("ascii")
    return sha256_hex(payload)


def validate_path(path: str) -> None:
    pure = PurePosixPath(path)

    if pure.is_absolute() or "\\" in path or ".." in pure.parts:
        raise ReplayError(f"unsafe repository path: {path}")

    if path == PROTECTED_BUILDER_PATH:
        raise ReplayError(
            "protected builder entered S8-RR-003 replay authority"
        )

    if path.startswith(EXCLUDED_TRACK2_PREFIX):
        raise ReplayError(
            f"excluded Track 2 path entered replay authority: {path}"
        )


def parse_ledger(
    raw: bytes,
    *,
    expected_count: int,
    label: str,
) -> tuple[tuple[str, str], ...]:
    if raw.startswith(b"\xef\xbb\xbf"):
        raise ReplayError(f"{label}: UTF-8 BOM detected")

    if b"\r" in raw:
        raise ReplayError(f"{label}: CR byte detected")

    if not raw.endswith(b"\n") or raw.endswith(b"\n\n"):
        raise ReplayError(
            f"{label}: exactly one final LF is required"
        )

    entries: list[tuple[str, str]] = []

    for number, line in enumerate(raw.splitlines(), 1):
        match = LEDGER_LINE_RE.fullmatch(line)

        if match is None:
            raise ReplayError(
                f"{label}: malformed ledger line {number}"
            )

        digest = match.group(1).decode("ascii")
        path = match.group(2).decode("utf-8")
        validate_path(path)
        entries.append((path, digest))

    paths = tuple(path for path, _digest in entries)

    if len(entries) != expected_count:
        raise ReplayError(
            f"{label}: entry count {len(entries)} != {expected_count}"
        )

    if paths != tuple(sorted(paths)):
        raise ReplayError(f"{label}: paths are not sorted")

    if len(paths) != len(set(paths)):
        raise ReplayError(f"{label}: duplicate path detected")

    return tuple(entries)


def validate_scope(
    scope: dict,
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    if set(scope) != EXPECTED_SCOPE_KEYS:
        raise ReplayError("scope top-level key contract mismatch")

    metadata = {
        "scope_schema_version": "1",
        "scope_id": "RCC002_S8RR003_NORMATIVE_LEDGER_SCOPE_V1",
        "correction_id": "RCC-002-S8RR003-NLBCP-001-REV2",
        "finding_in_scope": "S8-RR3-B01",
        "ledger_path": ROOT_LEDGER_PATH,
        "historical_ledger_sha256": EXPECTED_NORMATIVE_LEDGER_SHA256,
        "path_ordering": (
            "LC_ALL=C lexical order, repository-relative POSIX paths"
        ),
        "entry_format": (
            "lowercase SHA-256, two spaces, ./-prefixed path"
        ),
        "expected_current_entry_count": 145,
        "consumed_by": VERIFIER_PATH,
    }

    for key, expected in metadata.items():
        if scope.get(key) != expected:
            raise ReplayError(
                f"scope metadata mismatch for {key}"
            )

    category_names = (
        "historical_normative_paths",
        "s8rr002_correction_outputs",
        "s8rr003_lifecycle_outputs",
        "current_ledger_paths",
    )

    categories: dict[str, tuple[str, ...]] = {}

    for name in category_names:
        value = scope.get(name)

        if not isinstance(value, list):
            raise ReplayError(
                f"scope category is not a list: {name}"
            )

        if not all(isinstance(path, str) for path in value):
            raise ReplayError(
                f"scope category contains non-string value: {name}"
            )

        paths = tuple(value)

        if paths != tuple(sorted(paths)):
            raise ReplayError(
                f"scope category ordering mismatch: {name}"
            )

        if len(paths) != len(set(paths)):
            raise ReplayError(
                f"scope category duplicate path: {name}"
            )

        for path in paths:
            validate_path(path)

        categories[name] = paths

    historical = categories["historical_normative_paths"]
    rr002 = categories["s8rr002_correction_outputs"]
    rr003 = categories["s8rr003_lifecycle_outputs"]
    current = categories["current_ledger_paths"]

    if len(historical) != 110:
        raise ReplayError("historical category count mismatch")

    if len(rr002) != 30:
        raise ReplayError("S8-RR-002 category count mismatch")

    if len(rr003) != 6:
        raise ReplayError("S8-RR-003 category count mismatch")

    if len(current) != 145:
        raise ReplayError("current-ledger category count mismatch")

    historical_rr002_overlap = set(historical) & set(rr002)
    historical_rr003_overlap = set(historical) & set(rr003)
    rr002_rr003_overlap = set(rr002) & set(rr003)

    if historical_rr002_overlap != {RM_PATH}:
        raise ReplayError(
            "historical/S8-RR-002 overlap must be exactly RM"
        )

    if historical_rr003_overlap:
        raise ReplayError(
            "historical/S8-RR-003 overlap must be empty"
        )

    if rr002_rr003_overlap:
        raise ReplayError(
            "S8-RR-002/S8-RR-003 overlap must be empty"
        )

    derived = tuple(
        sorted(set(historical) | set(rr002) | set(rr003))
    )

    if len(derived) != 145:
        raise ReplayError("derived source-category union count mismatch")

    if derived != current:
        raise ReplayError(
            "current_ledger_paths differs from source-category union"
        )

    if not set(SPECIAL_PATHS).issubset(current):
        raise ReplayError(
            "at least one required special path is absent"
        )

    generic = tuple(
        path
        for path in current
        if path not in set(SPECIAL_PATHS)
    )

    if len(generic) != 139:
        raise ReplayError("generic remainder count mismatch")

    digest_contracts = (
        (
            historical,
            EXPECTED_HISTORICAL_PATH_DIGEST,
            "historical_normative_paths",
        ),
        (
            rr002,
            EXPECTED_RR002_PATH_DIGEST,
            "s8rr002_correction_outputs",
        ),
        (
            rr003,
            EXPECTED_RR003_PATH_DIGEST,
            "s8rr003_lifecycle_outputs",
        ),
        (
            current,
            EXPECTED_CURRENT_PATH_DIGEST,
            "current_ledger_paths",
        ),
        (
            SPECIAL_PATHS,
            EXPECTED_SPECIAL_PATH_DIGEST,
            "special_paths",
        ),
        (
            generic,
            EXPECTED_GENERIC_PATH_DIGEST,
            "generic_remainder",
        ),
    )

    for paths, expected_digest, label in digest_contracts:
        if path_digest(paths) != expected_digest:
            raise ReplayError(
                f"exact path authority mismatch: {label}"
            )

    return current, generic


def load_scope() -> tuple[
    dict,
    tuple[str, ...],
    tuple[str, ...],
]:
    raw = (REPO_ROOT / SCOPE_PATH).read_bytes()

    if sha256_hex(raw) != EXPECTED_SCOPE_SHA256:
        raise ReplayError("certified scope SHA-256 mismatch")

    scope = json.loads(raw.decode("utf-8"))

    if not isinstance(scope, dict):
        raise ReplayError("scope root is not an object")

    current, generic = validate_scope(scope)
    return scope, current, generic


def count_certified_test_methods(raw: bytes) -> tuple[str, ...]:
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ReplayError(
            f"certified test module is not UTF-8: {exc}"
        ) from exc

    tree = ast.parse(text)

    methods = tuple(
        sorted(
            node.name
            for class_node in tree.body
            if isinstance(class_node, ast.ClassDef)
            for node in class_node.body
            if (
                isinstance(
                    node,
                    (ast.FunctionDef, ast.AsyncFunctionDef),
                )
                and node.name.startswith("test_")
            )
        )
    )

    if len(methods) != 41 or len(set(methods)) != 41:
        raise ReplayError(
            "certified test-method count is not exactly 41"
        )

    if path_digest(methods) != EXPECTED_TEST_METHOD_NAME_DIGEST:
        raise ReplayError(
            "certified test-method authority mismatch"
        )

    return methods


def load_root_ledger() -> tuple[
    bytes,
    tuple[tuple[str, str], ...],
]:
    path = REPO_ROOT / ROOT_LEDGER_FROZEN_COPY_PATH

    if not path.is_file():
        raise ReplayError(
            "frozen S8-RR-003 root ledger is missing"
        )

    raw = path.read_bytes()

    if sha256_hex(raw) != EXPECTED_ROOT_LEDGER_SHA256:
        raise ReplayError(
            "frozen S8-RR-003 root-ledger SHA-256 mismatch"
        )

    entries = parse_ledger(
        raw,
        expected_count=145,
        label="certified root ledger",
    )
    return raw, entries


def load_normative_ledger() -> tuple[
    bytes,
    tuple[tuple[str, str], ...],
]:
    path = REPO_ROOT / NORMATIVE_LEDGER_PATH

    if not path.is_file():
        raise ReplayError(
            "certified normative ledger is missing"
        )

    raw = path.read_bytes()

    if sha256_hex(raw) != EXPECTED_NORMATIVE_LEDGER_SHA256:
        raise ReplayError(
            "certified normative-ledger SHA-256 mismatch"
        )

    entries = parse_ledger(
        raw,
        expected_count=110,
        label="certified normative ledger",
    )
    return raw, entries


def source_path(path: str) -> Path:
    if path == DP_PATH:
        return REPO_ROOT / DP_FROZEN_COPY_PATH

    if path == RM_PATH:
        return REPO_ROOT / RM_FROZEN_COPY_PATH

    return REPO_ROOT / path


def load_sources() -> tuple[
    dict[str, bytes],
    tuple[str, ...],
    bytes,
]:
    scope, current, generic = load_scope()
    root_ledger_raw, root_entries = load_root_ledger()
    normative_raw, normative_entries = load_normative_ledger()

    root_map = dict(root_entries)
    root_paths = tuple(root_map)

    if root_paths != current:
        raise ReplayError(
            "root-ledger targets differ from scope current paths"
        )

    historical = tuple(scope["historical_normative_paths"])
    normative_paths = tuple(
        path for path, _digest in normative_entries
    )

    if normative_paths != historical:
        raise ReplayError(
            "normative-ledger targets differ from historical category"
        )

    sources: dict[str, bytes] = {}

    for path in current:
        source = source_path(path)

        if not source.is_file():
            raise ReplayError(
                f"certified source is missing: {path}"
            )

        raw = source.read_bytes()
        actual = sha256_hex(raw)
        expected = root_map[path]

        if actual != expected:
            raise ReplayError(
                f"certified source digest mismatch for {path}: "
                f"{actual} != {expected}"
            )

        sources[path] = raw

    if len(sources) != 145:
        raise ReplayError(
            "certified source map does not contain 145 paths"
        )

    if sha256_hex(sources[VERIFIER_PATH]) != (
        EXPECTED_VERIFIER_SHA256
    ):
        raise ReplayError("certified verifier digest mismatch")

    if sha256_hex(sources[TEST_MODULE_PATH]) != (
        EXPECTED_TEST_MODULE_SHA256
    ):
        raise ReplayError("certified test-module digest mismatch")

    if sources[NORMATIVE_LEDGER_PATH] != normative_raw:
        raise ReplayError(
            "normative-ledger source-map identity mismatch"
        )

    count_certified_test_methods(sources[TEST_MODULE_PATH])

    return sources, generic, root_ledger_raw


def copy_once(
    root: Path,
    path: str,
    raw: bytes,
    copied: set[str],
) -> None:
    validate_path(path)

    if path in copied:
        raise ReplayError(f"double-copy detected: {path}")

    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(raw)
    copied.add(path)


def materialize(
    root: Path,
    sources: dict[str, bytes],
    generic: tuple[str, ...],
    root_ledger_raw: bytes,
) -> None:
    resolved_root = root.resolve()
    resolved_repo = REPO_ROOT.resolve()

    try:
        resolved_root.relative_to(resolved_repo)
    except ValueError:
        pass
    else:
        raise ReplayError(
            "temporary replay root must be outside repository"
        )

    if set(sources) != set(SPECIAL_PATHS) | set(generic):
        raise ReplayError("source-map membership mismatch")

    copied: set[str] = set()

    for path in SPECIAL_PATHS:
        copy_once(root, path, sources[path], copied)

    for path in generic:
        copy_once(root, path, sources[path], copied)

    if len(copied) != 145 or copied != set(sources):
        raise ReplayError(
            "not every certified target was copied exactly once"
        )

    ledger_target = root / ROOT_LEDGER_PATH

    if ledger_target.exists():
        raise ReplayError(
            "root ledger unexpectedly exists before materialization"
        )

    ledger_target.write_bytes(root_ledger_raw)


def execute_original(
    root: Path,
) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["PYTHONPATH"] = str(root)

    return subprocess.run(
        [sys.executable, str(root / TEST_MODULE_PATH)],
        cwd=root,
        env=environment,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def combined_output(
    result: subprocess.CompletedProcess[str],
) -> str:
    return result.stdout + result.stderr


def require_positive(
    result: subprocess.CompletedProcess[str],
) -> None:
    output = combined_output(result)

    if result.returncode != 0:
        raise ReplayError(
            "certified S8-RR-003 replay failed:\n" + output
        )

    counts = re.findall(
        r"Ran ([0-9]+) tests? in ",
        output,
    )

    if counts != ["41"]:
        raise ReplayError(
            f"expected exactly one 'Ran 41 tests' summary, got {counts}"
        )

    if len(re.findall(r"(?m)^OK$", output)) != 1:
        raise ReplayError(
            "certified replay lacks one exact OK line"
        )


def require_negative(
    result: subprocess.CompletedProcess[str],
) -> None:
    output = combined_output(result)

    if result.returncode == 0:
        raise ReplayError(
            "live-state substitution unexpectedly passed"
        )

    if re.search(r"(?m)^OK$", output):
        raise ReplayError(
            "live-state substitution emitted a false OK result"
        )


def run_positive(
    sources: dict[str, bytes],
    generic: tuple[str, ...],
    root_ledger_raw: bytes,
) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory(
        prefix="rcc002-s8rr003-positive-",
    ) as temporary:
        root = Path(temporary)
        materialize(
            root,
            sources,
            generic,
            root_ledger_raw,
        )
        result = execute_original(root)
        require_positive(result)
        return result


def run_live_state_negative(
    sources: dict[str, bytes],
    generic: tuple[str, ...],
    root_ledger_raw: bytes,
) -> subprocess.CompletedProcess[str]:
    substituted = dict(sources)

    live_dp = (REPO_ROOT / DP_PATH).read_bytes()
    live_rm = (REPO_ROOT / RM_PATH).read_bytes()
    live_root_ledger = (REPO_ROOT / ROOT_LEDGER_PATH).read_bytes()

    if sha256_hex(live_dp) == sha256_hex(sources[DP_PATH]):
        raise ReplayError(
            "live DP no longer differs from historical DP"
        )

    if sha256_hex(live_rm) == sha256_hex(sources[RM_PATH]):
        raise ReplayError(
            "live RM no longer differs from historical RM"
        )

    if live_root_ledger == root_ledger_raw:
        raise ReplayError(
            "live root ledger no longer differs from historical ledger"
        )

    substituted[DP_PATH] = live_dp
    substituted[RM_PATH] = live_rm

    with tempfile.TemporaryDirectory(
        prefix="rcc002-s8rr003-negative-",
    ) as temporary:
        root = Path(temporary)
        materialize(
            root,
            substituted,
            generic,
            live_root_ledger,
        )
        result = execute_original(root)
        require_negative(result)
        return result


def expect_replay_error(
    operation: Callable[[], object],
    label: str,
) -> None:
    try:
        operation()
    except ReplayError:
        return

    raise ReplayError(
        f"mutation control unexpectedly passed: {label}"
    )


def run_mutation_controls() -> None:
    scope, _current, _generic = load_scope()

    missing = copy.deepcopy(scope)
    missing["historical_normative_paths"].pop(0)
    expect_replay_error(
        lambda: validate_scope(missing),
        "missing path",
    )

    extra = copy.deepcopy(scope)
    extra["s8rr003_lifecycle_outputs"].append(
        "docs/review/EXTRA_S8RR003_PATH.md"
    )
    extra["s8rr003_lifecycle_outputs"].sort()
    expect_replay_error(
        lambda: validate_scope(extra),
        "extra path",
    )

    duplicate = copy.deepcopy(scope)
    duplicate_path = duplicate[
        "s8rr002_correction_outputs"
    ][0]
    duplicate["s8rr002_correction_outputs"].append(
        duplicate_path
    )
    duplicate["s8rr002_correction_outputs"].sort()
    expect_replay_error(
        lambda: validate_scope(duplicate),
        "duplicate path",
    )

    overlap = copy.deepcopy(scope)
    overlap_path = overlap[
        "s8rr002_correction_outputs"
    ][0]
    overlap["s8rr003_lifecycle_outputs"][-1] = overlap_path
    overlap["s8rr003_lifecycle_outputs"].sort()
    expect_replay_error(
        lambda: validate_scope(overlap),
        "category overlap",
    )

    substitution = copy.deepcopy(scope)
    substitution["historical_normative_paths"][0] = (
        "docs/review/SAME_COUNT_SUBSTITUTION.md"
    )
    substitution["historical_normative_paths"].sort()
    expect_replay_error(
        lambda: validate_scope(substitution),
        "same-count substitution",
    )

    absent_special = copy.deepcopy(scope)

    for category in (
        "historical_normative_paths",
        "s8rr002_correction_outputs",
        "s8rr003_lifecycle_outputs",
        "current_ledger_paths",
    ):
        values = absent_special[category]

        if VERIFIER_PATH in values:
            index = values.index(VERIFIER_PATH)
            values[index] = (
                "scripts/rcc002/"
                "verify_s8rr003_missing_special_replacement.py"
            )
            values.sort()

    expect_replay_error(
        lambda: validate_scope(absent_special),
        "absent special path",
    )

    _sources, _generic, _ledger = load_sources()
    test_raw = _sources[TEST_MODULE_PATH]
    marker = b"def test_full_repo_state_passes"

    if marker not in test_raw:
        raise ReplayError(
            "certified omission-control method marker is absent"
        )

    omitted = test_raw.replace(
        marker,
        b"def omitted_full_repo_state_passes",
        1,
    )

    expect_replay_error(
        lambda: count_certified_test_methods(omitted),
        "omitted certified test method",
    )

    with tempfile.TemporaryDirectory(
        prefix="rcc002-s8rr003-double-copy-",
    ) as temporary:
        copied: set[str] = set()
        root = Path(temporary)
        path = SPECIAL_PATHS[0]
        copy_once(root, path, b"first", copied)

        expect_replay_error(
            lambda: copy_once(
                root,
                path,
                b"second",
                copied,
            ),
            "double-copy detection",
        )


def run_historical_replay() -> dict[str, object]:
    sources, generic, root_ledger_raw = load_sources()
    run_mutation_controls()

    positive = run_positive(
        sources,
        generic,
        root_ledger_raw,
    )
    negative = run_live_state_negative(
        sources,
        generic,
        root_ledger_raw,
    )

    return {
        "result": "PASS",
        "replay_id": "RCC-002-S8-RR-003",
        "certified_targets": 145,
        "special_paths": 6,
        "generic_remainder": 139,
        "certified_test_methods": 41,
        "mutation_controls": 8,
        "positive_returncode": positive.returncode,
        "live_state_negative_returncode": negative.returncode,
        "protected_builder_excluded": True,
        "track2_subtree_excluded": True,
    }


class S8RR003HistoricalReplayTests(unittest.TestCase):
    def test_historical_replay(self) -> None:
        report = run_historical_replay()

        self.assertEqual(report["result"], "PASS")
        self.assertEqual(report["certified_targets"], 145)
        self.assertEqual(report["special_paths"], 6)
        self.assertEqual(report["generic_remainder"], 139)
        self.assertEqual(report["certified_test_methods"], 41)
        self.assertEqual(report["mutation_controls"], 8)


def main() -> int:
    try:
        sources, generic, root_ledger_raw = load_sources()
        run_mutation_controls()

        positive = run_positive(
            sources,
            generic,
            root_ledger_raw,
        )
        output = combined_output(positive)

        if output:
            print(
                output,
                end="" if output.endswith("\n") else "\n",
            )

        negative = run_live_state_negative(
            sources,
            generic,
            root_ledger_raw,
        )

        report = {
            "result": "PASS",
            "replay_id": "RCC-002-S8-RR-003",
            "certified_targets": 145,
            "special_paths": 6,
            "generic_remainder": 139,
            "certified_test_methods": 41,
            "mutation_controls": 8,
            "positive_returncode": positive.returncode,
            "live_state_negative_returncode": (
                negative.returncode
            ),
            "protected_builder_excluded": True,
            "track2_subtree_excluded": True,
        }

        print(json.dumps(report, indent=2, sort_keys=True))
        return 0
    except ReplayError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
