#!/usr/bin/env python3
"""Verify the RCC-002 S8 Track-1 mandatory-gate scope."""

from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path, PurePosixPath
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]

MANIFEST_PATH = (
    "docs/review/evidence/"
    "RCC_002_S8CANDBCP_GATE_SCOPE_V1.json"
)

EXPECTED_MANIFEST_SHA256 = (
    "c2be410babdfb62813b2588a7de2473ae744c35b076c790f331b2113becf7723"
)

POLICY_ID = "RCC002_S8CANDBCP_GATE_POLICY_V1"
SCOPE_SCHEMA_VERSION = "1"
SCOPE_ID = "RCC002_S8CANDBCP_GATE_SCOPE_V1"

APPROVED_PROPOSAL_PATH = (
    "docs/review/"
    "RCC_002_S8_IMPLEMENTATION_CANDIDATE_BLOCKER_"
    "CORRECTION_PROPOSAL_REV9_2026-08-02.md"
)
APPROVED_PROPOSAL_SHA256 = (
    "6b7651306368bb015508263db0cbe3fc07d51aa504aecf30be6634b190d6225f"
)

EXPECTED_POLICY_PREIMAGE_SHA256 = (
    "27414251ea113e9f135f7ed93ce120bd0fe454575914083654b8c9d71e2bfbe1"
)
EXPECTED_POLICY_PREIMAGE_LINES = 65
EXPECTED_POLICY_PREIMAGE_BYTES = 2687

PROTECTED_BUILDER_PATH = "scripts/build_rcc002_spec_bundle.py"
EXCLUDED_TRACK2_PREFIX = "tests/rcc002/s8/"

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
    CURRENT_STATE_MODULES
    + HISTORICAL_REPLAY_ADAPTER_MODULES
    + HISTORICAL_AUDIT_ONLY_MODULES
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

EXPECTED_CONSUMED_BY = (
    "scripts/rcc002/verify_s8candbcp_gate_scope.py",
    "scripts/rcc002/run_s8candbcp_gate.py",
    "tests/rcc002/test_s8candbcp_gate_scope.py",
)

EXPECTED_TOP_LEVEL_KEYS = {
    "scope_schema_version",
    "scope_id",
    "approved_proposal",
    "policy_id",
    "policy_preimage_rule",
    "counts",
    "path_digests",
    "current_state_modules",
    "historical_replay_adapter_modules",
    "historical_audit_only_modules",
    "excluded_track2_candidate_modules",
    "consumed_by",
}

EXPECTED_PREIMAGE_RULE = {
    "encoding": "ASCII",
    "category_order": list(CATEGORY_ORDER),
    "line_grammar": [
        "policy_id=<policy_id>",
        "category=<category_name>",
        "path=<repository_relative_posix_path>",
    ],
    "path_order": "exact array order within each category",
    "line_separator": "LF",
    "final_terminator": "exactly one LF",
    "line_count": EXPECTED_POLICY_PREIMAGE_LINES,
    "byte_count": EXPECTED_POLICY_PREIMAGE_BYTES,
    "sha256": EXPECTED_POLICY_PREIMAGE_SHA256,
}


class ScopeVerificationError(AssertionError):
    """Raised when the mandatory-gate scope is invalid."""

    def __init__(self, invariant: str, detail: str) -> None:
        super().__init__(f"{invariant}: {detail}")
        self.invariant = invariant
        self.detail = detail


def fail(invariant: str, detail: str) -> None:
    raise ScopeVerificationError(invariant, detail)


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def path_digest(paths: tuple[str, ...] | list[str]) -> str:
    raw = json.dumps(
        list(paths),
        ensure_ascii=True,
        separators=(",", ":"),
    ).encode("ascii")
    return sha256_hex(raw)


def require_exact_type(
    value: Any,
    expected_type: type,
    invariant: str,
) -> None:
    if type(value) is not expected_type:
        fail(
            invariant,
            f"expected {expected_type.__name__}, got {type(value).__name__}",
        )


def validate_repository_path(
    path: str,
    *,
    excluded: bool,
) -> None:
    try:
        path.encode("ascii")
    except UnicodeEncodeError as exc:
        fail(
            "policy_path_non_ascii",
            f"{path!r}: {exc}",
        )

    pure = PurePosixPath(path)

    if pure.is_absolute():
        fail("policy_path_absolute", path)

    if "\\" in path or ".." in pure.parts:
        fail("policy_path_unsafe", path)

    if (
        not path.startswith("tests/rcc002/")
        or not path.endswith(".py")
    ):
        fail("policy_path_wrong_shape", path)

    if path == PROTECTED_BUILDER_PATH:
        fail("protected_builder_in_policy", path)

    is_track2 = path.startswith(EXCLUDED_TRACK2_PREFIX)

    if excluded and not is_track2:
        fail("excluded_category_contains_track1", path)

    if not excluded and is_track2:
        fail("governed_category_contains_track2", path)


def validate_category(
    name: str,
    value: Any,
    expected: tuple[str, ...],
    *,
    excluded: bool,
) -> tuple[str, ...]:
    require_exact_type(
        value,
        list,
        f"{name}_not_list",
    )

    if not all(type(path) is str for path in value):
        fail(
            f"{name}_contains_non_string",
            repr(value),
        )

    paths = tuple(value)

    if len(paths) != len(set(paths)):
        fail(
            f"{name}_duplicate_path",
            repr(paths),
        )

    if paths != tuple(sorted(paths)):
        fail(
            f"{name}_wrong_order",
            repr(paths),
        )

    for path in paths:
        validate_repository_path(
            path,
            excluded=excluded,
        )

    if paths != expected:
        fail(
            f"{name}_wrong_membership",
            "category differs from independent authority",
        )

    return paths


def build_policy_preimage(
    categories: dict[str, tuple[str, ...]] | None = None,
) -> bytes:
    selected = (
        CATEGORY_PATHS
        if categories is None
        else categories
    )

    if tuple(selected) != CATEGORY_ORDER:
        fail(
            "policy_category_order_mismatch",
            repr(tuple(selected)),
        )

    lines = [f"policy_id={POLICY_ID}"]

    for category in CATEGORY_ORDER:
        paths = selected[category]
        lines.append(f"category={category}")

        for path in paths:
            lines.append(f"path={path}")

    try:
        raw = ("\n".join(lines) + "\n").encode("ascii")
    except UnicodeEncodeError as exc:
        fail(
            "policy_preimage_non_ascii",
            str(exc),
        )

    return raw


def validate_independent_authority() -> None:
    expected_lengths = {
        "current_state_modules": 45,
        "historical_replay_adapter_modules": 2,
        "historical_audit_only_modules": 2,
        "excluded_track2_candidate_modules": 11,
    }

    for name in CATEGORY_ORDER:
        paths = CATEGORY_PATHS[name]

        if len(paths) != expected_lengths[name]:
            fail(
                "independent_category_count_mismatch",
                name,
            )

        if len(paths) != len(set(paths)):
            fail(
                "independent_category_duplicate",
                name,
            )

        if paths != tuple(sorted(paths)):
            fail(
                "independent_category_order_mismatch",
                name,
            )

        for path in paths:
            validate_repository_path(
                path,
                excluded=(
                    name
                    == "excluded_track2_candidate_modules"
                ),
            )

    if len(POLICY_PATHS) != 60:
        fail(
            "independent_policy_count_mismatch",
            str(len(POLICY_PATHS)),
        )

    if len(set(POLICY_PATHS)) != 60:
        fail(
            "independent_category_overlap",
            "policy paths are not unique",
        )

    if len(GOVERNED_TRACK1_MODULES) != 49:
        fail(
            "independent_governed_count_mismatch",
            str(len(GOVERNED_TRACK1_MODULES)),
        )

    if len(EXECUTABLE_MODULES) != 47:
        fail(
            "independent_executable_count_mismatch",
            str(len(EXECUTABLE_MODULES)),
        )

    if set(HISTORICAL_AUDIT_ONLY_MODULES) & set(
        EXECUTABLE_MODULES
    ):
        fail(
            "audit_module_entered_executable_union",
            "audit/executable overlap",
        )

    actual_path_digests = {
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

    if actual_path_digests != EXPECTED_PATH_DIGESTS:
        fail(
            "independent_path_digest_mismatch",
            repr(actual_path_digests),
        )

    preimage = build_policy_preimage()

    if len(preimage.splitlines()) != (
        EXPECTED_POLICY_PREIMAGE_LINES
    ):
        fail(
            "independent_preimage_line_count_mismatch",
            str(len(preimage.splitlines())),
        )

    if len(preimage) != EXPECTED_POLICY_PREIMAGE_BYTES:
        fail(
            "independent_preimage_byte_count_mismatch",
            str(len(preimage)),
        )

    if sha256_hex(preimage) != (
        EXPECTED_POLICY_PREIMAGE_SHA256
    ):
        fail(
            "independent_preimage_digest_mismatch",
            sha256_hex(preimage),
        )


def load_manifest(repo_root: Path) -> tuple[dict[str, Any], bytes]:
    path = repo_root / MANIFEST_PATH

    if not path.is_file():
        fail(
            "scope_manifest_missing",
            MANIFEST_PATH,
        )

    raw = path.read_bytes()

    if sha256_hex(raw) != EXPECTED_MANIFEST_SHA256:
        fail(
            "scope_manifest_digest_mismatch",
            sha256_hex(raw),
        )

    if raw.startswith(b"\xef\xbb\xbf"):
        fail(
            "scope_manifest_bom",
            MANIFEST_PATH,
        )

    if b"\r" in raw:
        fail(
            "scope_manifest_cr",
            MANIFEST_PATH,
        )

    if not raw.endswith(b"\n") or raw.endswith(b"\n\n"):
        fail(
            "scope_manifest_final_lf",
            MANIFEST_PATH,
        )

    try:
        text = raw.decode("ascii")
    except UnicodeDecodeError as exc:
        fail(
            "scope_manifest_non_ascii",
            str(exc),
        )

    for number, line in enumerate(text.splitlines(), 1):
        if line.endswith((" ", "\t")):
            fail(
                "scope_manifest_trailing_whitespace",
                f"line {number}",
            )

    try:
        document = json.loads(text)
    except json.JSONDecodeError as exc:
        fail(
            "scope_manifest_invalid_json",
            str(exc),
        )

    require_exact_type(
        document,
        dict,
        "scope_manifest_root_not_object",
    )

    return document, raw


def validate_manifest(document: dict[str, Any]) -> dict[str, Any]:
    if set(document) != EXPECTED_TOP_LEVEL_KEYS:
        fail(
            "scope_manifest_top_level_keys",
            repr(sorted(document)),
        )

    if document["scope_schema_version"] != SCOPE_SCHEMA_VERSION:
        fail(
            "scope_schema_version_mismatch",
            repr(document["scope_schema_version"]),
        )

    if document["scope_id"] != SCOPE_ID:
        fail(
            "scope_id_mismatch",
            repr(document["scope_id"]),
        )

    if document["policy_id"] != POLICY_ID:
        fail(
            "policy_id_mismatch",
            repr(document["policy_id"]),
        )

    proposal = document["approved_proposal"]
    require_exact_type(
        proposal,
        dict,
        "approved_proposal_not_object",
    )

    if set(proposal) != {"path", "sha256"}:
        fail(
            "approved_proposal_keys",
            repr(sorted(proposal)),
        )

    if proposal["path"] != APPROVED_PROPOSAL_PATH:
        fail(
            "approved_proposal_path_mismatch",
            repr(proposal["path"]),
        )

    if proposal["sha256"] != APPROVED_PROPOSAL_SHA256:
        fail(
            "approved_proposal_digest_mismatch",
            repr(proposal["sha256"]),
        )

    if document["policy_preimage_rule"] != (
        EXPECTED_PREIMAGE_RULE
    ):
        fail(
            "policy_preimage_rule_mismatch",
            repr(document["policy_preimage_rule"]),
        )

    if document["counts"] != EXPECTED_COUNTS:
        fail(
            "scope_counts_mismatch",
            repr(document["counts"]),
        )

    if document["path_digests"] != EXPECTED_PATH_DIGESTS:
        fail(
            "scope_path_digests_mismatch",
            repr(document["path_digests"]),
        )

    manifest_categories = {
        "current_state_modules": validate_category(
            "current_state_modules",
            document["current_state_modules"],
            CURRENT_STATE_MODULES,
            excluded=False,
        ),
        "historical_replay_adapter_modules": validate_category(
            "historical_replay_adapter_modules",
            document["historical_replay_adapter_modules"],
            HISTORICAL_REPLAY_ADAPTER_MODULES,
            excluded=False,
        ),
        "historical_audit_only_modules": validate_category(
            "historical_audit_only_modules",
            document["historical_audit_only_modules"],
            HISTORICAL_AUDIT_ONLY_MODULES,
            excluded=False,
        ),
        "excluded_track2_candidate_modules": validate_category(
            "excluded_track2_candidate_modules",
            document["excluded_track2_candidate_modules"],
            EXCLUDED_TRACK2_CANDIDATE_MODULES,
            excluded=True,
        ),
    }

    consumed_by = document["consumed_by"]
    require_exact_type(
        consumed_by,
        list,
        "consumed_by_not_list",
    )

    if tuple(consumed_by) != EXPECTED_CONSUMED_BY:
        fail(
            "consumed_by_mismatch",
            repr(consumed_by),
        )

    manifest_policy_paths = tuple(
        path
        for category in CATEGORY_ORDER
        for path in manifest_categories[category]
    )

    if len(manifest_policy_paths) != 60:
        fail(
            "manifest_policy_count_mismatch",
            str(len(manifest_policy_paths)),
        )

    if len(set(manifest_policy_paths)) != 60:
        fail(
            "manifest_category_overlap",
            "manifest paths are not unique",
        )

    manifest_governed = (
        manifest_categories["current_state_modules"]
        + manifest_categories[
            "historical_replay_adapter_modules"
        ]
        + manifest_categories[
            "historical_audit_only_modules"
        ]
    )

    manifest_executable = (
        manifest_categories["current_state_modules"]
        + manifest_categories[
            "historical_replay_adapter_modules"
        ]
    )

    if manifest_governed != GOVERNED_TRACK1_MODULES:
        fail(
            "manifest_governed_union_mismatch",
            "governed union differs from authority",
        )

    if manifest_executable != EXECUTABLE_MODULES:
        fail(
            "manifest_executable_union_mismatch",
            "executable union differs from authority",
        )

    preimage = build_policy_preimage(manifest_categories)

    if len(preimage.splitlines()) != (
        EXPECTED_POLICY_PREIMAGE_LINES
    ):
        fail(
            "manifest_preimage_line_count_mismatch",
            str(len(preimage.splitlines())),
        )

    if len(preimage) != EXPECTED_POLICY_PREIMAGE_BYTES:
        fail(
            "manifest_preimage_byte_count_mismatch",
            str(len(preimage)),
        )

    preimage_sha256 = sha256_hex(preimage)

    if preimage_sha256 != EXPECTED_POLICY_PREIMAGE_SHA256:
        fail(
            "manifest_preimage_digest_mismatch",
            preimage_sha256,
        )

    return {
        "policy_paths": manifest_policy_paths,
        "governed_track1_modules": manifest_governed,
        "executable_modules": manifest_executable,
        "policy_preimage": preimage,
        "policy_preimage_sha256": preimage_sha256,
    }


def verify_gate_scope(
    repo_root: str | os.PathLike[str] | Path = REPO_ROOT,
) -> dict[str, Any]:
    root = Path(repo_root).resolve()

    validate_independent_authority()
    document, raw = load_manifest(root)
    derived = validate_manifest(document)

    return {
        "result": "PASS",
        "scope_id": SCOPE_ID,
        "policy_id": POLICY_ID,
        "manifest_sha256": sha256_hex(raw),
        "policy_preimage_sha256": (
            derived["policy_preimage_sha256"]
        ),
        "policy_preimage_line_count": len(
            derived["policy_preimage"].splitlines()
        ),
        "policy_preimage_byte_count": len(
            derived["policy_preimage"]
        ),
        "policy_path_count": len(
            derived["policy_paths"]
        ),
        "governed_track1_module_count": len(
            derived["governed_track1_modules"]
        ),
        "current_state_module_count": len(
            CURRENT_STATE_MODULES
        ),
        "historical_replay_adapter_module_count": len(
            HISTORICAL_REPLAY_ADAPTER_MODULES
        ),
        "historical_audit_only_module_count": len(
            HISTORICAL_AUDIT_ONLY_MODULES
        ),
        "excluded_track2_candidate_module_count": len(
            EXCLUDED_TRACK2_CANDIDATE_MODULES
        ),
        "executable_module_count": len(
            derived["executable_modules"]
        ),
        "current_state_modules": list(
            CURRENT_STATE_MODULES
        ),
        "historical_replay_adapter_modules": list(
            HISTORICAL_REPLAY_ADAPTER_MODULES
        ),
        "historical_audit_only_modules": list(
            HISTORICAL_AUDIT_ONLY_MODULES
        ),
        "excluded_track2_candidate_modules": list(
            EXCLUDED_TRACK2_CANDIDATE_MODULES
        ),
        "governed_track1_modules": list(
            GOVERNED_TRACK1_MODULES
        ),
        "executable_modules": list(
            EXECUTABLE_MODULES
        ),
        "protected_builder_excluded": (
            PROTECTED_BUILDER_PATH not in POLICY_PATHS
        ),
        "track2_filesystem_access_performed": False,
    }


def main() -> int:
    try:
        result = verify_gate_scope(REPO_ROOT)
    except ScopeVerificationError as exc:
        print(
            f"FAIL: {exc.invariant}: {exc.detail}",
            file=sys.stderr,
        )
        return 1

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
