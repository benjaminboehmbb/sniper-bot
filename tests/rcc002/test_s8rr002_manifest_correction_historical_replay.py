#!/usr/bin/env python3
"""Historical replay adapter for certified RCC-002 S8-RR-002."""

from __future__ import annotations

import ast
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path, PurePosixPath


REPO_ROOT = Path(__file__).resolve().parents[2]

SCOPE_PATH = (
    "docs/review/evidence/"
    "RCC_002_S8RR002_CORRECTION_VERIFIER_SCOPE_V1.json"
)
VERIFIER_PATH = "scripts/rcc002/verify_s8rr002_artifacts.py"
TEST_MODULE_PATH = "tests/rcc002/test_s8rr002_manifest_correction.py"

DP_PATH = (
    "docs/specifications/"
    "RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md"
)
RM_PATH = (
    "docs/specifications/"
    "RCC_002_REPRODUCIBILITY_AND_MANIFEST_2026-07-23.md"
)
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

PROTECTED_BUILDER_PATH = "scripts/build_rcc002_spec_bundle.py"

EXPECTED_SCOPE_SHA256 = (
    "7253c44c9d342e6a26e356d07f1ca37efcb43b843d93636e9e7e1594530c840c"
)
EXPECTED_IMMUTABLE_PATH_DIGEST = (
    "84f8e56b489c404b4b181279928002260bc4b989e4c04adb91df093da41e3590"
)
EXPECTED_CANDIDATE_PATH_DIGEST = (
    "f655ef0e91feaec65f14ef7d53b0059164bf2c50d5335bb05f02db3e992c7469"
)
EXPECTED_UNION_PATH_DIGEST = (
    "af2916414d4a1d075a69282482dca56a2f599afa342b621cb3dba1cf3a0e3a85"
)
EXPECTED_SPECIAL_PATH_DIGEST = (
    "b637dea3390acaa8e99471d245c03a1814c0254731d5b2be6ffa8e5e700d9e37"
)
EXPECTED_GENERIC_PATH_DIGEST = (
    "ae75f1d8cd4b09a045910db654cafa33fbab2e7943d551d2ce5738a86b42dba4"
)

EXPECTED_IMMUTABLE_INPUTS = (
    "docs/review/RCC_002_S8RR002_BLOCKER_CORRECTION_PROPOSAL_REV2_2026-07-31.md",
    DP_PATH,
    "docs/specifications/RCC_002_DATA_VALIDATION_2026-07-23.md",
    "docs/specifications/RCC_002_INDICATOR_SPECIFICATION_2026-07-23.md",
    (
        "docs/specifications/"
        "RCC_002_LABEL_AND_FORWARD_RETURN_SPECIFICATION_2026-07-23.md"
    ),
    (
        "docs/specifications/"
        "RCC_002_REGIME_AND_GATE_SPECIFICATION_2026-07-23.md"
    ),
    (
        "docs/specifications/"
        "RCC_002_SIGNAL_TRANSFORMATION_2026-07-23.md"
    ),
    "schemas/rcc002/manifests/dataset-manifest/1.0.0.schema.json",
    "schemas/rcc002/manifests/stage-manifest/1.0.0.schema.json",
    (
        "tests/fixtures/rcc002/manifests/dataset-manifest/"
        "1.0.0/complete-valid.json"
    ),
    (
        "tests/fixtures/rcc002/manifests/dataset-manifest/"
        "1.0.0/minimal-valid.json"
    ),
)

EXPECTED_CANDIDATE_OUTPUTS = (
    SCOPE_PATH,
    RM_PATH,
    "requirements-rcc002-review.txt",
    "schemas/rcc002/manifests/dataset-manifest/1.0.1.schema.json",
    VERIFIER_PATH,
    (
        "tests/fixtures/rcc002/manifests/dataset-manifest/"
        "1.0.1/complete-valid.json"
    ),
    (
        "tests/fixtures/rcc002/manifests/dataset-manifest/"
        "1.0.1/minimal-valid.json"
    ),
    (
        "tests/fixtures/rcc002/manifests/dataset-manifest/"
        "1.0.1/negative/CASE_LEDGER.json"
    ),
    (
        "tests/fixtures/rcc002/manifests/dataset-manifest/"
        "1.0.1/negative/absolute-path.json"
    ),
    (
        "tests/fixtures/rcc002/manifests/dataset-manifest/"
        "1.0.1/negative/duplicate-specification.json"
    ),
    (
        "tests/fixtures/rcc002/manifests/dataset-manifest/"
        "1.0.1/negative/duplicate-view.json"
    ),
    (
        "tests/fixtures/rcc002/manifests/dataset-manifest/"
        "1.0.1/negative/extra-property.json"
    ),
    (
        "tests/fixtures/rcc002/manifests/dataset-manifest/"
        "1.0.1/negative/invalid-id.json"
    ),
    (
        "tests/fixtures/rcc002/manifests/dataset-manifest/"
        "1.0.1/negative/invalid-timestamp.json"
    ),
    (
        "tests/fixtures/rcc002/manifests/dataset-manifest/"
        "1.0.1/negative/missing-required-field.json"
    ),
    (
        "tests/fixtures/rcc002/manifests/dataset-manifest/"
        "1.0.1/negative/missing-specification.json"
    ),
    (
        "tests/fixtures/rcc002/manifests/dataset-manifest/"
        "1.0.1/negative/missing-view.json"
    ),
    (
        "tests/fixtures/rcc002/manifests/dataset-manifest/"
        "1.0.1/negative/path-traversal.json"
    ),
    (
        "tests/fixtures/rcc002/manifests/dataset-manifest/"
        "1.0.1/negative/reordered-specification.json"
    ),
    (
        "tests/fixtures/rcc002/manifests/dataset-manifest/"
        "1.0.1/negative/reordered-view.json"
    ),
    (
        "tests/fixtures/rcc002/manifests/dataset-manifest/"
        "1.0.1/negative/secret-like-field.json"
    ),
    (
        "tests/fixtures/rcc002/manifests/dataset-manifest/"
        "1.0.1/negative/secret-like-value.json"
    ),
    (
        "tests/fixtures/rcc002/manifests/dataset-manifest/"
        "1.0.1/negative/stale-specification-version.json"
    ),
    (
        "tests/fixtures/rcc002/manifests/dataset-manifest/"
        "1.0.1/negative/unknown-specification.json"
    ),
    (
        "tests/fixtures/rcc002/manifests/dataset-manifest/"
        "1.0.1/negative/unknown-view.json"
    ),
    (
        "tests/fixtures/rcc002/manifests/dataset-manifest/"
        "1.0.1/negative/wrong-schema-identity.json"
    ),
    (
        "tests/fixtures/rcc002/manifests/dataset-manifest/"
        "1.0.1/negative/wrong-schema-version.json"
    ),
    (
        "tests/fixtures/rcc002/manifests/dataset-manifest/"
        "1.0.1/negative/wrong-type-nullability.json"
    ),
    (
        "tests/fixtures/rcc002/manifests/dataset-manifest/"
        "1.0.1/negative/wrong-view-allowlist-hash.json"
    ),
    TEST_MODULE_PATH,
)

SPECIAL_PATHS = (
    DP_PATH,
    RM_PATH,
    VERIFIER_PATH,
    TEST_MODULE_PATH,
)

EXPECTED_SHA256_TEXT = """\
0c61ef159ca34aa12cacd4cae8419bf97c8b7d302ec560adf47fc3376e5f5511  docs/review/RCC_002_S8RR002_BLOCKER_CORRECTION_PROPOSAL_REV2_2026-07-31.md
7253c44c9d342e6a26e356d07f1ca37efcb43b843d93636e9e7e1594530c840c  docs/review/evidence/RCC_002_S8RR002_CORRECTION_VERIFIER_SCOPE_V1.json
0e060d30b75082b74eb5211b1d378837aa7872d86f62e5e162586e2a2cc37fad  docs/specifications/RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md
459c4a99a266b420d52a69f2fb1a6b36a99529e999842bc8271f3336c444bb31  docs/specifications/RCC_002_DATA_VALIDATION_2026-07-23.md
0d8ad604cce88daa56193ee054f4d28237d60135a67cebbde883d2c00d18539d  docs/specifications/RCC_002_INDICATOR_SPECIFICATION_2026-07-23.md
526665966c83c8fc7254c663474fe08ee721125ae6cdcd88e5a4f5b80af5882f  docs/specifications/RCC_002_LABEL_AND_FORWARD_RETURN_SPECIFICATION_2026-07-23.md
37ee84f1ddd86c0765e9c4df3b57aa5907472ba481f54181e8f8d6dccf354cdc  docs/specifications/RCC_002_REGIME_AND_GATE_SPECIFICATION_2026-07-23.md
23fd2fc0a0338124e9bbd9d95bf6797662d1e32012cb6247763e47a47bf61cf1  docs/specifications/RCC_002_REPRODUCIBILITY_AND_MANIFEST_2026-07-23.md
b3de8b4b7c69c30fd811edbeceb246b1b981d7d561c54b585535e72ca0fd8c74  docs/specifications/RCC_002_SIGNAL_TRANSFORMATION_2026-07-23.md
756cc9e506ae4ee1a6f6c0507088b5cfc0dc8ba350fb2d2d46f1ffa72033adb6  requirements-rcc002-review.txt
4462193667777f268119ea253adefb63972dc91b7c8769f14d9cce169543c523  schemas/rcc002/manifests/dataset-manifest/1.0.0.schema.json
52380b9b6c9244308e03fc3c900d48b118735aa84e5e634d0a83396822e674a3  schemas/rcc002/manifests/dataset-manifest/1.0.1.schema.json
12f3e4a39dd0647681867bcd05ead249460dd2882b5b4a74d89620477f8e4c10  schemas/rcc002/manifests/stage-manifest/1.0.0.schema.json
2c67bfddc0b99a3a07497240a2e6c26dbc2dd41674ade898eb00b25ef38d9335  scripts/rcc002/verify_s8rr002_artifacts.py
1766958549c83bcb1fb808fc1334fe8c11ef0fb17618095296b38ccc8e653002  tests/fixtures/rcc002/manifests/dataset-manifest/1.0.0/complete-valid.json
1766958549c83bcb1fb808fc1334fe8c11ef0fb17618095296b38ccc8e653002  tests/fixtures/rcc002/manifests/dataset-manifest/1.0.0/minimal-valid.json
d0b14abd53a0be6586ca6e21c30576721149f63625a71bcc7d06c9761e798da9  tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/complete-valid.json
23c2d69c5b80aa479134539982a14b38b46644297cd1a0d2aa6d2e28cb15547c  tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/minimal-valid.json
f5dcbddff9bf71bc73561d76487bfc39d059a786013814afd7cbc97fc9a61e55  tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/negative/CASE_LEDGER.json
a6b4721cb7098a6fd698f4d169f3801cfb47e0be30ce9902085bea3f31c1d4a1  tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/negative/absolute-path.json
617adafc069d0d67ba734f87bfa9b5cba0f6596402637d11cb1ff988da0680f6  tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/negative/duplicate-specification.json
9a16ed661bb6dfa141517ac38dba31be7f1bf8683c19b2341b640a1a9cdfdede  tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/negative/duplicate-view.json
7aa44468965408a7248c6d8507fcdf35e23ba14754b675bcc292d1ce5324753d  tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/negative/extra-property.json
739654e8de3225aaefaea6f4c2ebff016f25e8deef7fb145acc2aef88a630af1  tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/negative/invalid-id.json
e21cb198997a3b3511aa8e9230b5503fd3193d86f12515b2fc0c96c4ffd076db  tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/negative/invalid-timestamp.json
62223cdf3a2c03e6c528cc452c21a27e405df8bf3a8949c3d1446531c5536553  tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/negative/missing-required-field.json
3b2c10d55dad0b5a6f72d17b9a356e7b9458912967abc5b0df97fa045fe19d17  tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/negative/missing-specification.json
8f3bcc611eabd0ecfee6166ded160a3d0e5936c6b869b04ee94f5b4b8f040313  tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/negative/missing-view.json
956c9bfc285e67fbb215eafe9f330d1153d59ae9dd43e77f4fdb44a202a64d7f  tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/negative/path-traversal.json
65e4d87594226168953c64382103ce020521665d4db6971e7199e1f866a94de1  tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/negative/reordered-specification.json
5bc015c904822f01b2059d7a43ac0f903992def3703f5a014217590f50a2d977  tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/negative/reordered-view.json
5496bc93372291e97972152b0f703ad25f662a70d026f3a8a204cdd07fd2c290  tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/negative/secret-like-field.json
2bc3d9e2b1757bb0b0de85d5855f0bb810467089bd430de275349e4ab1c07b1b  tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/negative/secret-like-value.json
978a72e1949eeebed2bd3a9d00c001dd386713c83cda84f5c04b48838e347444  tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/negative/stale-specification-version.json
5a55c022cedd20d692c07bb7742789d1f4cf182c8a830993200a7ff29e1a3732  tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/negative/unknown-specification.json
03d245b699fa7ff9b4c883018d3fad2444b956c88d8eaae935413e8e8299fc5a  tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/negative/unknown-view.json
e7008f18d5d5aeef467d5b802c9867df381083af1bdb12244d61054d7d8b47a9  tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/negative/wrong-schema-identity.json
1069f77177ec3cccac4dec529eb7bb848c010a389198a573b9a68503b86a05da  tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/negative/wrong-schema-version.json
58cd3f317c4822777414e0e227bfc8f6dbc228a154722c0824c7e39832fc52fe  tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/negative/wrong-type-nullability.json
e6c5c4b3e4869e7bf48017bf7c033bc2a23887750179341a8137353d303ffcab  tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/negative/wrong-view-allowlist-hash.json
2b977dc2952058ee1381723332786fcd252534c0a8de560c64af932fb46abaf4  tests/rcc002/test_s8rr002_manifest_correction.py
"""


class ReplayError(AssertionError):
    """Raised when the historical replay contract is violated."""


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def path_digest(paths: tuple[str, ...]) -> str:
    raw = json.dumps(
        list(paths),
        ensure_ascii=True,
        separators=(",", ":"),
    ).encode("ascii")
    return sha256_hex(raw)


def parse_expected_hashes() -> dict[str, str]:
    result: dict[str, str] = {}

    for line in EXPECTED_SHA256_TEXT.splitlines():
        digest, path = line.split("  ", 1)

        if not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise ReplayError(f"invalid digest for {path}")

        if path in result:
            raise ReplayError(f"duplicate digest path: {path}")

        result[path] = digest

    if len(result) != 41:
        raise ReplayError("digest authority must contain 41 paths")

    return result


EXPECTED_SHA256 = parse_expected_hashes()


def validate_path(path: str) -> None:
    pure = PurePosixPath(path)

    if pure.is_absolute() or "\\" in path or ".." in pure.parts:
        raise ReplayError(f"unsafe path: {path}")

    if path == PROTECTED_BUILDER_PATH:
        raise ReplayError("protected builder entered replay authority")


def validate_partition(
    immutable: tuple[str, ...],
    candidate: tuple[str, ...],
    special: tuple[str, ...] = SPECIAL_PATHS,
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    if len(immutable) != 11 or len(set(immutable)) != 11:
        raise ReplayError("immutable category count mismatch")

    if len(candidate) != 30 or len(set(candidate)) != 30:
        raise ReplayError("candidate category count mismatch")

    if immutable != tuple(sorted(immutable)):
        raise ReplayError("immutable category order mismatch")

    if candidate != tuple(sorted(candidate)):
        raise ReplayError("candidate category order mismatch")

    if path_digest(immutable) != EXPECTED_IMMUTABLE_PATH_DIGEST:
        raise ReplayError("immutable category membership mismatch")

    if path_digest(candidate) != EXPECTED_CANDIDATE_PATH_DIGEST:
        raise ReplayError("candidate category membership mismatch")

    if set(immutable) & set(candidate):
        raise ReplayError("immutable/candidate overlap detected")

    union = tuple(sorted(set(immutable) | set(candidate)))

    if len(union) != 41:
        raise ReplayError("certified union count mismatch")

    if path_digest(union) != EXPECTED_UNION_PATH_DIGEST:
        raise ReplayError("certified union membership mismatch")

    if len(special) != 4 or len(set(special)) != 4:
        raise ReplayError("special-path count mismatch")

    if path_digest(special) != EXPECTED_SPECIAL_PATH_DIGEST:
        raise ReplayError("special-path authority mismatch")

    if not set(special).issubset(union):
        raise ReplayError("special path absent from certified union")

    generic = tuple(path for path in union if path not in set(special))

    if len(generic) != 37:
        raise ReplayError("generic remainder count mismatch")

    if path_digest(generic) != EXPECTED_GENERIC_PATH_DIGEST:
        raise ReplayError("generic remainder membership mismatch")

    for path in union:
        validate_path(path)

    return union, generic


def load_scope() -> dict:
    raw = (REPO_ROOT / SCOPE_PATH).read_bytes()

    if sha256_hex(raw) != EXPECTED_SCOPE_SHA256:
        raise ReplayError("certified scope SHA-256 mismatch")

    scope = json.loads(raw.decode("utf-8"))

    expected_keys = {
        "scope_schema_version",
        "scope_id",
        "correction_id",
        "findings_in_scope",
        "consumed_by",
        "path_ordering",
        "immutable_reference_inputs",
        "correction_candidate_outputs",
    }

    if set(scope) != expected_keys:
        raise ReplayError("scope top-level key mismatch")

    if scope["scope_schema_version"] != "1":
        raise ReplayError("scope schema version mismatch")

    if scope["scope_id"] != (
        "RCC002_S8RR002_CORRECTION_VERIFIER_SCOPE_V1"
    ):
        raise ReplayError("scope ID mismatch")

    if scope["correction_id"] != (
        "RCC-002-S8RR002-BCP-001-REV2"
    ):
        raise ReplayError("scope correction ID mismatch")

    if scope["findings_in_scope"] != [
        "S8-RR2-B01",
        "S8-RR2-B02",
    ]:
        raise ReplayError("scope findings mismatch")

    validate_partition(
        tuple(scope["immutable_reference_inputs"]),
        tuple(scope["correction_candidate_outputs"]),
    )

    return scope


def source_path(path: str) -> Path:
    if path == DP_PATH:
        return REPO_ROOT / DP_FROZEN_COPY_PATH

    if path == RM_PATH:
        return REPO_ROOT / RM_FROZEN_COPY_PATH

    return REPO_ROOT / path


def read_verified_source(path: str) -> bytes:
    validate_path(path)
    source = source_path(path)

    if not source.is_file():
        raise ReplayError(f"certified source missing: {path}")

    raw = source.read_bytes()
    actual = sha256_hex(raw)
    expected = EXPECTED_SHA256[path]

    if actual != expected:
        raise ReplayError(
            f"certified source digest mismatch for {path}: "
            f"{actual} != {expected}"
        )

    return raw


def count_certified_test_methods(raw: bytes) -> int:
    tree = ast.parse(raw.decode("utf-8"))
    methods = [
        node.name
        for class_node in tree.body
        if isinstance(class_node, ast.ClassDef)
        for node in class_node.body
        if (
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name.startswith("test_")
        )
    ]

    if len(methods) != 28 or len(set(methods)) != 28:
        raise ReplayError("certified test-method count mismatch")

    return len(methods)


def load_sources() -> tuple[dict[str, bytes], tuple[str, ...]]:
    scope = load_scope()
    union, generic = validate_partition(
        tuple(scope["immutable_reference_inputs"]),
        tuple(scope["correction_candidate_outputs"]),
    )

    if set(EXPECTED_SHA256) != set(union):
        raise ReplayError("hardcoded digest authority mismatch")

    sources = {path: read_verified_source(path) for path in union}

    if len(sources) != 41:
        raise ReplayError("certified source-map count mismatch")

    count_certified_test_methods(sources[TEST_MODULE_PATH])

    return sources, generic


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
) -> None:
    try:
        root.resolve().relative_to(REPO_ROOT.resolve())
    except ValueError:
        pass
    else:
        raise ReplayError("temporary root is inside repository")

    if set(sources) != set(EXPECTED_SHA256):
        raise ReplayError("source-map membership mismatch")

    copied: set[str] = set()

    for path in SPECIAL_PATHS:
        copy_once(root, path, sources[path], copied)

    for path in generic:
        copy_once(root, path, sources[path], copied)

    if copied != set(EXPECTED_SHA256):
        raise ReplayError("not every certified path was copied once")


def execute_original(root: Path) -> subprocess.CompletedProcess[str]:
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


def output_of(result: subprocess.CompletedProcess[str]) -> str:
    return result.stdout + result.stderr


def require_positive(result: subprocess.CompletedProcess[str]) -> None:
    output = output_of(result)

    if result.returncode != 0:
        raise ReplayError("historical replay failed:\n" + output)

    if re.findall(r"Ran ([0-9]+) tests? in ", output) != ["28"]:
        raise ReplayError("historical replay summary is not exactly 28")

    if len(re.findall(r"(?m)^OK$", output)) != 1:
        raise ReplayError("historical replay lacks one exact OK line")


def require_negative(result: subprocess.CompletedProcess[str]) -> None:
    output = output_of(result)

    if result.returncode == 0:
        raise ReplayError("live-state substitution unexpectedly passed")

    if re.search(r"(?m)^OK$", output):
        raise ReplayError("live-state substitution emitted OK")


def run_positive(
    sources: dict[str, bytes],
    generic: tuple[str, ...],
) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory(
        prefix="rcc002-s8rr002-positive-",
    ) as temporary:
        root = Path(temporary)
        materialize(root, sources, generic)
        result = execute_original(root)
        require_positive(result)
        return result


def run_negative(
    sources: dict[str, bytes],
    generic: tuple[str, ...],
) -> subprocess.CompletedProcess[str]:
    substituted = dict(sources)
    live_dp = (REPO_ROOT / DP_PATH).read_bytes()
    live_rm = (REPO_ROOT / RM_PATH).read_bytes()

    if sha256_hex(live_dp) == EXPECTED_SHA256[DP_PATH]:
        raise ReplayError("live DP equals historical DP")

    if sha256_hex(live_rm) == EXPECTED_SHA256[RM_PATH]:
        raise ReplayError("live RM equals historical RM")

    substituted[DP_PATH] = live_dp
    substituted[RM_PATH] = live_rm

    with tempfile.TemporaryDirectory(
        prefix="rcc002-s8rr002-negative-",
    ) as temporary:
        root = Path(temporary)
        materialize(root, substituted, generic)
        result = execute_original(root)
        require_negative(result)
        return result


def run_historical_replay() -> dict[str, object]:
    sources, generic = load_sources()
    positive = run_positive(sources, generic)
    negative = run_negative(sources, generic)

    return {
        "result": "PASS",
        "replay_id": "RCC-002-S8-RR-002",
        "immutable_inputs": 11,
        "candidate_outputs": 30,
        "overlap": 0,
        "certified_union": 41,
        "special_paths": 4,
        "generic_remainder": 37,
        "certified_test_methods": 28,
        "positive_returncode": positive.returncode,
        "live_state_negative_returncode": negative.returncode,
        "protected_builder_excluded": True,
    }


class S8RR002HistoricalReplayTests(unittest.TestCase):
    def test_historical_replay(self) -> None:
        report = run_historical_replay()
        self.assertEqual(report["result"], "PASS")
        self.assertEqual(report["certified_union"], 41)
        self.assertEqual(report["generic_remainder"], 37)
        self.assertEqual(report["certified_test_methods"], 28)


def main() -> int:
    try:
        sources, generic = load_sources()
        positive = run_positive(sources, generic)
        positive_output = output_of(positive)

        if positive_output:
            print(
                positive_output,
                end="" if positive_output.endswith("\n") else "\n",
            )

        negative = run_negative(sources, generic)

        print(
            json.dumps(
                {
                    "result": "PASS",
                    "replay_id": "RCC-002-S8-RR-002",
                    "immutable_inputs": 11,
                    "candidate_outputs": 30,
                    "overlap": 0,
                    "certified_union": 41,
                    "special_paths": 4,
                    "generic_remainder": 37,
                    "certified_test_methods": 28,
                    "positive_returncode": positive.returncode,
                    "live_state_negative_returncode": (
                        negative.returncode
                    ),
                    "protected_builder_excluded": True,
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0
    except ReplayError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
