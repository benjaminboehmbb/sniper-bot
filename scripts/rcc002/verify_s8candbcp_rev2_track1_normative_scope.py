#!/usr/bin/env python3
"""RCC-002 S8-CAND-BCP-001-REV9 Track 1 normative-scope verifier.

Independently re-derives and verifies the exact 46-path Track 1 scope for
correction candidate RCC-002-S8-CAND-BCP-001-REV9. Standard library only.

The verifier compares three independent sources with exact list equality in
strict LC_ALL=C order:

1. the hardcoded expected list below;
2. the scope manifest file; and
3. the actual repository tree for a bounded, individually named path set.

No recursive directory traversal is performed.

Run from repository root:

    python3 scripts/rcc002/verify_s8candbcp_rev2_track1_normative_scope.py
"""

import json
import os
import sys


REPO_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

SCOPE_ID = "RCC002_S8CANDBCP_REV2_TRACK1_NORMATIVE_SCOPE_V1"
CORRECTION_ID = "RCC-002-S8-CAND-BCP-001-REV9"
SCOPE_MANIFEST_PATH = (
    "docs/review/evidence/"
    "RCC_002_S8CANDBCP_REV2_TRACK1_NORMATIVE_SCOPE_V1.json"
)
PROTECTED_BUILDER_PATH = "scripts/build_rcc002_spec_bundle.py"

EXPECTED_TOTAL = 46
EXPECTED_MODIFIED = 4
EXPECTED_NEW = 42

EXPECTED_FINDINGS = (
    "S8-CAND-B02",
    "S8-CAND-BCP-REV4-ARCH-001",
    "S8-CAND-BCP-REV4-DOC-001",
)

EXPECTED_ENTRIES = (
    ("CLAUDE.md", "MODIFIED"),
    ("SHA256SUMS", "MODIFIED"),
    (
        "docs/review/evidence/"
        "RCC_002_S8CANDBCP_GATE_SCOPE_V1.json",
        "NEW",
    ),
    (
        "docs/review/evidence/"
        "RCC_002_S8CANDBCP_REV2_NORMATIVE_LEDGER_HISTORICAL_COPY_"
        "2026-08-01.txt",
        "NEW",
    ),
    (
        "docs/review/evidence/"
        "RCC_002_S8CANDBCP_REV2_NORMATIVE_LEDGER_SCOPE_V1.json",
        "NEW",
    ),
    (
        "docs/review/evidence/"
        "RCC_002_S8CANDBCP_REV2_TRACK1_NORMATIVE_SCOPE_V1.json",
        "NEW",
    ),
    (
        "docs/review/evidence/"
        "RCC_002_S8RR002_HISTORICAL_DATA_PIPELINE_SPECIFICATION_"
        "0_8_0_CERTIFIED_COPY_2026-08-02.txt",
        "NEW",
    ),
    (
        "docs/review/evidence/"
        "RCC_002_S8RR002_HISTORICAL_REPRODUCIBILITY_AND_MANIFEST_"
        "0_9_0_CERTIFIED_COPY_2026-08-02.txt",
        "NEW",
    ),
    (
        "docs/specifications/"
        "RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md",
        "MODIFIED",
    ),
    (
        "docs/specifications/"
        "RCC_002_REPRODUCIBILITY_AND_MANIFEST_2026-07-23.md",
        "MODIFIED",
    ),
    (
        "registries/rcc002/views/"
        "s8_view_schema_fingerprint_profile.v1.json",
        "NEW",
    ),
    (
        "schemas/rcc002/manifests/dataset-manifest/"
        "1.0.2.schema.json",
        "NEW",
    ),
    ("scripts/rcc002/run_s8candbcp_gate.py", "NEW"),
    ("scripts/rcc002/verify_s8candbcp_gate_scope.py", "NEW"),
    (
        "scripts/rcc002/"
        "verify_s8candbcp_rev2_normative_ledger.py",
        "NEW",
    ),
    (
        "scripts/rcc002/"
        "verify_s8candbcp_rev2_track1_normative_scope.py",
        "NEW",
    ),
    (
        "tests/fixtures/rcc002/manifests/dataset-manifest/"
        "1.0.2/complete-valid.json",
        "NEW",
    ),
    (
        "tests/fixtures/rcc002/manifests/dataset-manifest/"
        "1.0.2/minimal-valid.json",
        "NEW",
    ),
    (
        "tests/fixtures/rcc002/manifests/dataset-manifest/"
        "1.0.2/negative/CASE_LEDGER.json",
        "NEW",
    ),
    (
        "tests/fixtures/rcc002/manifests/dataset-manifest/"
        "1.0.2/negative/absolute-path.json",
        "NEW",
    ),
    (
        "tests/fixtures/rcc002/manifests/dataset-manifest/"
        "1.0.2/negative/duplicate-specification.json",
        "NEW",
    ),
    (
        "tests/fixtures/rcc002/manifests/dataset-manifest/"
        "1.0.2/negative/duplicate-view.json",
        "NEW",
    ),
    (
        "tests/fixtures/rcc002/manifests/dataset-manifest/"
        "1.0.2/negative/extra-property.json",
        "NEW",
    ),
    (
        "tests/fixtures/rcc002/manifests/dataset-manifest/"
        "1.0.2/negative/invalid-id.json",
        "NEW",
    ),
    (
        "tests/fixtures/rcc002/manifests/dataset-manifest/"
        "1.0.2/negative/invalid-timestamp.json",
        "NEW",
    ),
    (
        "tests/fixtures/rcc002/manifests/dataset-manifest/"
        "1.0.2/negative/missing-required-field.json",
        "NEW",
    ),
    (
        "tests/fixtures/rcc002/manifests/dataset-manifest/"
        "1.0.2/negative/missing-specification.json",
        "NEW",
    ),
    (
        "tests/fixtures/rcc002/manifests/dataset-manifest/"
        "1.0.2/negative/missing-view.json",
        "NEW",
    ),
    (
        "tests/fixtures/rcc002/manifests/dataset-manifest/"
        "1.0.2/negative/path-traversal.json",
        "NEW",
    ),
    (
        "tests/fixtures/rcc002/manifests/dataset-manifest/"
        "1.0.2/negative/reordered-specification.json",
        "NEW",
    ),
    (
        "tests/fixtures/rcc002/manifests/dataset-manifest/"
        "1.0.2/negative/reordered-view.json",
        "NEW",
    ),
    (
        "tests/fixtures/rcc002/manifests/dataset-manifest/"
        "1.0.2/negative/secret-like-field.json",
        "NEW",
    ),
    (
        "tests/fixtures/rcc002/manifests/dataset-manifest/"
        "1.0.2/negative/secret-like-value.json",
        "NEW",
    ),
    (
        "tests/fixtures/rcc002/manifests/dataset-manifest/"
        "1.0.2/negative/stale-specification-version.json",
        "NEW",
    ),
    (
        "tests/fixtures/rcc002/manifests/dataset-manifest/"
        "1.0.2/negative/unknown-specification.json",
        "NEW",
    ),
    (
        "tests/fixtures/rcc002/manifests/dataset-manifest/"
        "1.0.2/negative/unknown-view.json",
        "NEW",
    ),
    (
        "tests/fixtures/rcc002/manifests/dataset-manifest/"
        "1.0.2/negative/wrong-schema-identity.json",
        "NEW",
    ),
    (
        "tests/fixtures/rcc002/manifests/dataset-manifest/"
        "1.0.2/negative/wrong-schema-version.json",
        "NEW",
    ),
    (
        "tests/fixtures/rcc002/manifests/dataset-manifest/"
        "1.0.2/negative/wrong-type-nullability.json",
        "NEW",
    ),
    (
        "tests/fixtures/rcc002/manifests/dataset-manifest/"
        "1.0.2/negative/wrong-view-allowlist-hash.json",
        "NEW",
    ),
    (
        "tests/fixtures/rcc002/manifests/dataset-manifest/"
        "1.0.2/negative/wrong-view-fingerprint-hash.json",
        "NEW",
    ),
    ("tests/rcc002/test_s8candbcp_gate_scope.py", "NEW"),
    (
        "tests/rcc002/"
        "test_s8candbcp_rev2_normative_ledger.py",
        "NEW",
    ),
    (
        "tests/rcc002/"
        "test_s8candbcp_rev2_track1_normative_scope.py",
        "NEW",
    ),
    (
        "tests/rcc002/"
        "test_s8rr002_manifest_correction_historical_replay.py",
        "NEW",
    ),
    (
        "tests/rcc002/"
        "test_s8rr003_normative_ledger_historical_replay.py",
        "NEW",
    ),
)


class ScopeVerificationError(Exception):
    """Raised when the normative Track 1 scope is inconsistent."""


def _is_safe_relative_path(path):
    if not isinstance(path, str) or not path:
        return False
    if path.startswith("/") or path.startswith("\\"):
        return False
    if ":" in path.split("/")[0] and len(path) > 1 and path[1] == ":":
        return False
    if "\\" in path:
        return False

    segments = path.split("/")

    if any(segment in ("", ".", "..") for segment in segments):
        return False

    if any(
        ord(character) < 0x20 or ord(character) == 0x7F
        for segment in segments
        for character in segment
    ):
        return False

    return True


def verify(entries, *, source_label):
    if len(entries) != EXPECTED_TOTAL:
        raise ScopeVerificationError(
            f"{source_label}: total count {len(entries)} "
            f"!= expected {EXPECTED_TOTAL}"
        )

    paths = [path for path, _category in entries]

    if len(set(paths)) != len(paths):
        seen = set()

        for path in paths:
            if path in seen:
                raise ScopeVerificationError(
                    f"{source_label}: duplicate entry {path!r}"
                )
            seen.add(path)

    for path in paths:
        if not _is_safe_relative_path(path):
            raise ScopeVerificationError(
                f"{source_label}: unsafe path {path!r}"
            )

        if path == PROTECTED_BUILDER_PATH:
            raise ScopeVerificationError(
                f"{source_label}: protected builder path present"
            )

    if paths != sorted(paths):
        for index in range(len(paths) - 1):
            if paths[index] > paths[index + 1]:
                raise ScopeVerificationError(
                    f"{source_label}: order violation at index {index}: "
                    f"{paths[index]!r} must sort after "
                    f"{paths[index + 1]!r}"
                )

        raise ScopeVerificationError(
            f"{source_label}: not in LC_ALL=C order"
        )

    modified = [
        path for path, category in entries
        if category == "MODIFIED"
    ]
    new = [
        path for path, category in entries
        if category == "NEW"
    ]
    other = [
        category for _path, category in entries
        if category not in ("MODIFIED", "NEW")
    ]

    if other:
        raise ScopeVerificationError(
            f"{source_label}: unknown category value(s): {other}"
        )

    if len(modified) != EXPECTED_MODIFIED:
        raise ScopeVerificationError(
            f"{source_label}: modified count {len(modified)} "
            f"!= expected {EXPECTED_MODIFIED}"
        )

    if len(new) != EXPECTED_NEW:
        raise ScopeVerificationError(
            f"{source_label}: new count {len(new)} "
            f"!= expected {EXPECTED_NEW}"
        )

    if list(entries) != list(EXPECTED_ENTRIES):
        expected_paths = [path for path, _category in EXPECTED_ENTRIES]
        expected_set = set(expected_paths)
        actual_set = set(paths)
        missing = sorted(expected_set - actual_set)
        extra = sorted(actual_set - expected_set)

        if missing:
            raise ScopeVerificationError(
                f"{source_label}: missing entries: {missing}"
            )

        if extra:
            raise ScopeVerificationError(
                f"{source_label}: extra entries: {extra}"
            )

        for expected, actual in zip(EXPECTED_ENTRIES, entries):
            expected_path, expected_category = expected
            actual_path, actual_category = actual

            if expected_path != actual_path:
                raise ScopeVerificationError(
                    f"{source_label}: reordered entry: expected "
                    f"{expected_path!r} at this position, found "
                    f"{actual_path!r}"
                )

            if expected_category != actual_category:
                raise ScopeVerificationError(
                    f"{source_label}: miscategorized entry "
                    f"{actual_path!r}: expected {expected_category}, "
                    f"found {actual_category}"
                )

        raise ScopeVerificationError(
            f"{source_label}: entry list mismatch "
            "(undeclared divergence)"
        )


def verify_scope_manifest_file(manifest_path):
    full_path = os.path.join(REPO_ROOT, manifest_path)

    with open(full_path, "r", encoding="ascii") as handle:
        manifest = json.load(handle)

    expected_keys = {
        "scope_schema_version",
        "scope_id",
        "correction_id",
        "findings_in_scope",
        "path_ordering",
        "total_entries",
        "modified_entries",
        "new_entries",
        "entries",
    }

    if set(manifest) != expected_keys:
        raise ScopeVerificationError(
            "scope manifest top-level key set mismatch"
        )

    if manifest.get("scope_schema_version") != "1":
        raise ScopeVerificationError(
            "scope_schema_version mismatch: "
            f"{manifest.get('scope_schema_version')!r}"
        )

    if manifest.get("scope_id") != SCOPE_ID:
        raise ScopeVerificationError(
            f"scope_id mismatch: {manifest.get('scope_id')!r}"
        )

    if manifest.get("correction_id") != CORRECTION_ID:
        raise ScopeVerificationError(
            "correction_id mismatch: "
            f"{manifest.get('correction_id')!r}"
        )

    if tuple(manifest.get("findings_in_scope", ())) != EXPECTED_FINDINGS:
        raise ScopeVerificationError(
            "findings_in_scope mismatch"
        )

    if manifest.get("path_ordering") != (
        "LC_ALL=C lexical order, repository-relative POSIX paths"
    ):
        raise ScopeVerificationError(
            "path_ordering mismatch"
        )

    if manifest.get("total_entries") != EXPECTED_TOTAL:
        raise ScopeVerificationError(
            "manifest total_entries "
            f"{manifest.get('total_entries')} != {EXPECTED_TOTAL}"
        )

    if manifest.get("modified_entries") != EXPECTED_MODIFIED:
        raise ScopeVerificationError(
            "manifest modified_entries "
            f"{manifest.get('modified_entries')} "
            f"!= {EXPECTED_MODIFIED}"
        )

    if manifest.get("new_entries") != EXPECTED_NEW:
        raise ScopeVerificationError(
            "manifest new_entries "
            f"{manifest.get('new_entries')} != {EXPECTED_NEW}"
        )

    raw_entries = manifest.get("entries")

    if not isinstance(raw_entries, list):
        raise ScopeVerificationError(
            "manifest entries is not a list"
        )

    entries = []

    for index, entry in enumerate(raw_entries):
        if not isinstance(entry, dict):
            raise ScopeVerificationError(
                f"manifest entry {index} is not an object"
            )

        if set(entry) != {"path", "category"}:
            raise ScopeVerificationError(
                f"manifest entry {index} key set mismatch"
            )

        entries.append((entry["path"], entry["category"]))

    verify(entries, source_label="scope manifest")


def verify_tree_membership(entries):
    """Check only the 46 individually named paths; never walk directories."""

    for path, category in entries:
        full_path = os.path.join(REPO_ROOT, path)
        exists = os.path.isfile(full_path)

        if category == "MODIFIED" and not exists:
            raise ScopeVerificationError(
                f"MODIFIED path missing from tree: {path!r}"
            )

        if category == "NEW" and not exists:
            raise ScopeVerificationError(
                f"NEW path missing from tree: {path!r}"
            )


def main():
    try:
        verify(
            EXPECTED_ENTRIES,
            source_label="hardcoded expectation (self-check)",
        )
        verify_scope_manifest_file(SCOPE_MANIFEST_PATH)
        verify_tree_membership(EXPECTED_ENTRIES)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(
            f"FAIL: {CORRECTION_ID} Track 1 normative scope: "
            f"manifest or filesystem error: {exc}"
        )
        return 1
    except ScopeVerificationError as exc:
        print(
            f"FAIL: {CORRECTION_ID} Track 1 normative scope: {exc}"
        )
        return 1

    print(
        f"PASS: {CORRECTION_ID} Track 1 normative scope verified: "
        f"{EXPECTED_TOTAL} entries "
        f"({EXPECTED_MODIFIED} modified, {EXPECTED_NEW} new), "
        "strict LC_ALL=C order, exact list equality across hardcoded "
        "expectation, scope manifest, and repository tree."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
