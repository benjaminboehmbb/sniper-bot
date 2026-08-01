#!/usr/bin/env python3
"""Mechanical verification for RCC-002 S8RR002-BCP-001-REV2 correction artifacts.

Verifies closure of readiness findings S8-RR2-B01 and S8-RR2-B02 against the
generated Dataset Manifest Schema 1.0.1, its fixtures, and the corrected
Reproducibility and Manifest 0.9.0 normative text, per
docs/review/RCC_002_S8RR002_BLOCKER_CORRECTION_PROPOSAL_REV2_2026-07-31.md
Section 5.6.

This verifier reads only paths declared in the committed, versioned scope
manifest (docs/review/evidence/RCC_002_S8RR002_CORRECTION_VERIFIER_SCOPE_V1.json).
It never uses Path.rglob, os.walk, shell find or equivalent unscoped
full-tree traversal, so it remains meaningful outside a Git working tree.

Does not modify, repurpose, or invoke scripts/rcc002/verify_s8bcp001_artifacts.py.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from importlib import metadata
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCOPE_PATH = REPO / "docs/review/evidence/RCC_002_S8RR002_CORRECTION_VERIFIER_SCOPE_V1.json"
DATASET_MANIFEST_SCHEMA_PATH = REPO / "schemas/rcc002/manifests/dataset-manifest/1.0.1.schema.json"
RM_PATH = REPO / "docs/specifications/RCC_002_REPRODUCIBILITY_AND_MANIFEST_2026-07-23.md"
DATA_PIPELINE_PATH = REPO / "docs/specifications/RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md"
FIXTURE_ROOT = REPO / "tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1"
NEGATIVE_ROOT = FIXTURE_ROOT / "negative"
CASE_LEDGER_PATH = NEGATIVE_ROOT / "CASE_LEDGER.json"

REQUIRED_JSONSCHEMA_VERSION = "4.26.0"

ZERO_DIGEST = "0" * 64

# Six non-self specification literal hashes, per Revision 2 SS4.3.
NON_SELF_SPECIFICATIONS = [
    ("RCC_002_DATA_PIPELINE_SPECIFICATION", "0.8.0",
     "0e060d30b75082b74eb5211b1d378837aa7872d86f62e5e162586e2a2cc37fad",
     "RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md"),
    ("RCC-002-DV", "0.6.0",
     "459c4a99a266b420d52a69f2fb1a6b36a99529e999842bc8271f3336c444bb31",
     "RCC_002_DATA_VALIDATION_2026-07-23.md"),
    ("RCC-002-IS", "0.4.3",
     "0d8ad604cce88daa56193ee054f4d28237d60135a67cebbde883d2c00d18539d",
     "RCC_002_INDICATOR_SPECIFICATION_2026-07-23.md"),
    ("RCC-002-ST", "0.4.2",
     "b3de8b4b7c69c30fd811edbeceb246b1b981d7d561c54b585535e72ca0fd8c74",
     "RCC_002_SIGNAL_TRANSFORMATION_2026-07-23.md"),
    ("RCC-002-RG", "0.5.1",
     "37ee84f1ddd86c0765e9c4df3b57aa5907472ba481f54181e8f8d6dccf354cdc",
     "RCC_002_REGIME_AND_GATE_SPECIFICATION_2026-07-23.md"),
    ("RCC-002-LF", "0.5.0",
     "526665966c83c8fc7254c663474fe08ee721125ae6cdcd88e5a4f5b80af5882f",
     "RCC_002_LABEL_AND_FORWARD_RETURN_SPECIFICATION_2026-07-23.md"),
]
SELF_SPECIFICATION = ("RCC-002-RM", "0.9.0", "RCC_002_REPRODUCIBILITY_AND_MANIFEST_2026-07-23.md")

EXPECTED_VIEW_IDENTITY = [
    ("rcc002.view.research-features", "1.0.0",
     "2f2fd811b5ed8754ad8b02ee2222d885d7da3e7551ecbd5cf65fe38831c0806e"),
    ("rcc002.view.backtest-inputs", "1.0.0",
     "2f2fd811b5ed8754ad8b02ee2222d885d7da3e7551ecbd5cf65fe38831c0806e"),
    ("rcc002.view.paper", "1.0.0",
     "2f2fd811b5ed8754ad8b02ee2222d885d7da3e7551ecbd5cf65fe38831c0806e"),
    ("rcc002.view.live", "1.0.0",
     "2f2fd811b5ed8754ad8b02ee2222d885d7da3e7551ecbd5cf65fe38831c0806e"),
    ("rcc002.view.label-research", "1.0.0",
     "0e223d60ed4139f73194f1cb3b886a8eface9229183ad522a093e966827518cc"),
    ("rcc002.view.audit", "2.0.0",
     "0e223d60ed4139f73194f1cb3b886a8eface9229183ad522a093e966827518cc"),
]

EXPECTED_IMMUTABLE_HASHES = {
    "schemas/rcc002/manifests/dataset-manifest/1.0.0.schema.json":
        "4462193667777f268119ea253adefb63972dc91b7c8769f14d9cce169543c523",
    "tests/fixtures/rcc002/manifests/dataset-manifest/1.0.0/minimal-valid.json":
        "1766958549c83bcb1fb808fc1334fe8c11ef0fb17618095296b38ccc8e653002",
    "tests/fixtures/rcc002/manifests/dataset-manifest/1.0.0/complete-valid.json":
        "1766958549c83bcb1fb808fc1334fe8c11ef0fb17618095296b38ccc8e653002",
    "schemas/rcc002/manifests/stage-manifest/1.0.0.schema.json":
        "12f3e4a39dd0647681867bcd05ead249460dd2882b5b4a74d89620477f8e4c10",
}

# ---------------------------------------------------------------------------
# Exact closed scope contract (S8RR002-CAND-ARCH-001 repair).
#
# These are the independently authoritative required scope sets and scope
# metadata values. The committed scope manifest is validated against them
# with exact list equality (order and membership), not merely checked for
# internal self-consistency. A scope manifest that omits, adds, duplicates,
# reorders or re-categorizes a required entry therefore fails closed here,
# before any candidate or fixture byte is read.
# ---------------------------------------------------------------------------

EXPECTED_SCOPE_SCHEMA_VERSION = "1"
EXPECTED_SCOPE_ID = "RCC002_S8RR002_CORRECTION_VERIFIER_SCOPE_V1"
EXPECTED_CORRECTION_ID = "RCC-002-S8RR002-BCP-001-REV2"
EXPECTED_FINDINGS_IN_SCOPE = ["S8-RR2-B01", "S8-RR2-B02"]
EXPECTED_CONSUMED_BY = "scripts/rcc002/verify_s8rr002_artifacts.py"
EXPECTED_PATH_ORDERING = "deterministic lexical order, repository-relative POSIX paths"

EXPECTED_IMMUTABLE_REFERENCE_INPUTS = [
    "docs/review/RCC_002_S8RR002_BLOCKER_CORRECTION_PROPOSAL_REV2_2026-07-31.md",
    "docs/specifications/RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md",
    "docs/specifications/RCC_002_DATA_VALIDATION_2026-07-23.md",
    "docs/specifications/RCC_002_INDICATOR_SPECIFICATION_2026-07-23.md",
    "docs/specifications/RCC_002_LABEL_AND_FORWARD_RETURN_SPECIFICATION_2026-07-23.md",
    "docs/specifications/RCC_002_REGIME_AND_GATE_SPECIFICATION_2026-07-23.md",
    "docs/specifications/RCC_002_SIGNAL_TRANSFORMATION_2026-07-23.md",
    "schemas/rcc002/manifests/dataset-manifest/1.0.0.schema.json",
    "schemas/rcc002/manifests/stage-manifest/1.0.0.schema.json",
    "tests/fixtures/rcc002/manifests/dataset-manifest/1.0.0/complete-valid.json",
    "tests/fixtures/rcc002/manifests/dataset-manifest/1.0.0/minimal-valid.json",
]

# The complete set of 30 files generated or modified by the S8RR002-BCP-001-
# REV2 correction cycle, including the scope manifest, verifier and focused
# test file themselves (Finding S8RR002-CAND-ARCH-001, items 4 and "Required
# correction" 1/4). Listing the scope manifest's own path here is safe: the
# scope contains paths, not embedded file hashes, so hashing its final bytes
# for the candidate inventory does not create a self-hash cycle.
EXPECTED_CANDIDATE_OUTPUTS = [
    "docs/review/evidence/RCC_002_S8RR002_CORRECTION_VERIFIER_SCOPE_V1.json",
    "docs/specifications/RCC_002_REPRODUCIBILITY_AND_MANIFEST_2026-07-23.md",
    "requirements-rcc002-review.txt",
    "schemas/rcc002/manifests/dataset-manifest/1.0.1.schema.json",
    "scripts/rcc002/verify_s8rr002_artifacts.py",
    "tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/complete-valid.json",
    "tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/minimal-valid.json",
    "tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/negative/CASE_LEDGER.json",
    "tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/negative/absolute-path.json",
    "tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/negative/duplicate-specification.json",
    "tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/negative/duplicate-view.json",
    "tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/negative/extra-property.json",
    "tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/negative/invalid-id.json",
    "tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/negative/invalid-timestamp.json",
    "tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/negative/missing-required-field.json",
    "tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/negative/missing-specification.json",
    "tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/negative/missing-view.json",
    "tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/negative/path-traversal.json",
    "tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/negative/reordered-specification.json",
    "tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/negative/reordered-view.json",
    "tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/negative/secret-like-field.json",
    "tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/negative/secret-like-value.json",
    "tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/negative/stale-specification-version.json",
    "tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/negative/unknown-specification.json",
    "tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/negative/unknown-view.json",
    "tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/negative/wrong-schema-identity.json",
    "tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/negative/wrong-schema-version.json",
    "tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/negative/wrong-type-nullability.json",
    "tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/negative/wrong-view-allowlist-hash.json",
    "tests/rcc002/test_s8rr002_manifest_correction.py",
]
assert EXPECTED_IMMUTABLE_REFERENCE_INPUTS == sorted(EXPECTED_IMMUTABLE_REFERENCE_INPUTS)
assert len(EXPECTED_IMMUTABLE_REFERENCE_INPUTS) == 11
assert EXPECTED_CANDIDATE_OUTPUTS == sorted(EXPECTED_CANDIDATE_OUTPUTS)
assert len(EXPECTED_CANDIDATE_OUTPUTS) == 30

FIXTURE_PREFIX = "tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/"
NEGATIVE_PREFIX = FIXTURE_PREFIX + "negative/"
CASE_LEDGER_REL = NEGATIVE_PREFIX + "CASE_LEDGER.json"

# Every semantic negative fixture is declared to differ from the shared valid
# baseline in exactly one of these two top-level arrays.
SEMANTIC_NEGATIVE_DIMENSION = {
    "duplicate-view.json": "views",
    "missing-view.json": "views",
    "reordered-view.json": "views",
    "unknown-view.json": "views",
    "wrong-view-allowlist-hash.json": "views",
    "duplicate-specification.json": "specification_profile",
    "missing-specification.json": "specification_profile",
    "reordered-specification.json": "specification_profile",
    "unknown-specification.json": "specification_profile",
    "stale-specification-version.json": "specification_profile",
}


class VerificationError(AssertionError):
    pass


def fail(message: str) -> None:
    raise VerificationError(message)


def read_bytes_checked(path: Path) -> bytes:
    if not path.is_file():
        fail(f"declared path does not exist: {path}")
    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        fail(f"{path}: UTF-8 BOM present")
    if b"\r\n" in raw:
        fail(f"{path}: CRLF line ending present (LF required)")
    return raw


def read_text_checked(path: Path) -> str:
    return read_bytes_checked(path).decode("utf-8")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


# ---------------------------------------------------------------------------
# Step 1: load and validate the versioned scope manifest before anything else.
# ---------------------------------------------------------------------------

def validate_scope(scope: dict) -> None:
    """Validate a parsed scope dict against the exact closed scope contract.

    Operates purely on the in-memory dict so it can be exercised against
    mutated copies in tests without touching repository artifacts. Existence
    checks (`(REPO / p).is_file()`) are the only part that consults the real
    filesystem; every set-membership, ordering, duplication, path-safety and
    metadata check is a pure in-memory comparison against the independently
    hardcoded EXPECTED_* constants above.
    """
    if scope.get("scope_schema_version") != EXPECTED_SCOPE_SCHEMA_VERSION:
        fail("scope manifest: scope_schema_version must be "
             f"{EXPECTED_SCOPE_SCHEMA_VERSION!r}")
    if scope.get("scope_id") != EXPECTED_SCOPE_ID:
        fail(f"scope manifest: scope_id must be {EXPECTED_SCOPE_ID!r}")
    if scope.get("correction_id") != EXPECTED_CORRECTION_ID:
        fail(f"scope manifest: correction_id must be {EXPECTED_CORRECTION_ID!r}")
    if scope.get("findings_in_scope") != EXPECTED_FINDINGS_IN_SCOPE:
        fail(f"scope manifest: findings_in_scope must be exactly {EXPECTED_FINDINGS_IN_SCOPE!r}")
    if scope.get("consumed_by") != EXPECTED_CONSUMED_BY:
        fail(f"scope manifest: consumed_by must be {EXPECTED_CONSUMED_BY!r}")
    if scope.get("path_ordering") != EXPECTED_PATH_ORDERING:
        fail(f"scope manifest: path_ordering must be {EXPECTED_PATH_ORDERING!r}")

    expected_by_key = {
        "immutable_reference_inputs": EXPECTED_IMMUTABLE_REFERENCE_INPUTS,
        "correction_candidate_outputs": EXPECTED_CANDIDATE_OUTPUTS,
    }

    all_paths: list[str] = []
    for key, expected in expected_by_key.items():
        paths = scope.get(key)
        if not isinstance(paths, list) or not paths:
            fail(f"scope manifest: '{key}' must be a non-empty list")
        if paths != sorted(paths):
            fail(f"scope manifest: '{key}' is not in deterministic lexical order")
        if len(paths) != len(set(paths)):
            fail(f"scope manifest: '{key}' contains a duplicate path")
        for p in paths:
            if p.startswith("/") or re.match(r"^[A-Za-z]:[\\/]", p) or "\\" in p:
                fail(f"scope manifest: absolute or non-POSIX path '{p}' in '{key}'")
            if ".." in p.split("/"):
                fail(f"scope manifest: parent-traversal path '{p}' in '{key}'")
        all_paths.extend(paths)

        # Exact set-and-order equality against the independently required
        # scope: this is what makes a missing, extra, or re-categorized
        # required entry fail closed, even though every remaining declared
        # path may still resolve to a real, untouched file on disk.
        if paths != expected:
            missing = sorted(set(expected) - set(paths))
            extra = sorted(set(paths) - set(expected))
            fail(
                f"scope manifest: '{key}' does not equal the exact required "
                f"set (missing={missing}, extra={extra})"
            )

    if len(all_paths) != len(set(all_paths)):
        fail("scope manifest: duplicate path across immutable/candidate categories")
    if len(all_paths) != len(EXPECTED_IMMUTABLE_REFERENCE_INPUTS) + len(EXPECTED_CANDIDATE_OUTPUTS):
        fail("scope manifest: total declared path count does not match the exact required scope")
    for p in all_paths:
        if not (REPO / p).is_file():
            fail(f"scope manifest: declared path does not exist: {p}")


def load_scope() -> dict:
    scope = json.loads(read_text_checked(SCOPE_PATH))
    validate_scope(scope)
    return scope


def verify_no_undeclared_fixture_files(scope: dict) -> None:
    """Fail before any read if an undeclared file exists in the fixture dirs.

    Uses a narrowly scoped directory-name enumeration limited to exactly the
    two 1.0.1 fixture directories, comparing file *names* only against the
    scope-declared candidate paths. No byte of any file is read here; this
    check exists solely to catch an undeclared extra fixture that the
    scope-driven read set below would otherwise silently never look at.
    """
    declared = set(scope["correction_candidate_outputs"])

    for name in sorted(p.name for p in FIXTURE_ROOT.glob("*.json")):
        rel = f"{FIXTURE_PREFIX}{name}"
        if rel not in declared:
            fail(f"undeclared candidate file present on disk (not in scope): {rel}")

    for name in sorted(p.name for p in NEGATIVE_ROOT.glob("*.json")):
        rel = f"{NEGATIVE_PREFIX}{name}"
        if rel not in declared:
            fail(f"undeclared candidate file present on disk (not in scope): {rel}")


# ---------------------------------------------------------------------------
# Steps 2-4: extract authoritative contracts and compare literal hashes.
# ---------------------------------------------------------------------------

def find_json_block(text: str, heading_pattern: str, label: str) -> dict:
    match = re.search(
        heading_pattern + r".*?```json\n(.*?)\n```",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    if match is None:
        fail(f"{label}: JSON block not found for pattern {heading_pattern!r}")
    return json.loads(match.group(1))


def extract_data_pipeline_view_contracts(dp_text: str) -> list[dict]:
    views = []
    for index in range(1, 7):
        pattern = rf"^##### 7\.9\.3\.{index} `([^`]+)`"
        heading = re.search(pattern, dp_text, flags=re.MULTILINE)
        if heading is None:
            fail(f"Data Pipeline: view heading 7.9.3.{index} not found")
        view = find_json_block(
            dp_text, re.escape(heading.group(0)), f"Data Pipeline view {index}"
        )
        for field in ("schema_id", "schema_version", "schema_ref", "allowlist_sha256"):
            if field not in view:
                fail(f"Data Pipeline view {index}: missing field {field!r}")
        views.append(view)
    return views


def extract_rm_specification_profile(rm_text: str) -> list[tuple[str, str]]:
    start = rm_text.find("### 12.3 Spezifikationsprofil")
    if start < 0:
        fail("Reproducibility and Manifest: Section 12.3 heading not found")
    end = rm_text.find("### 12.4", start)
    if end < 0:
        fail("Reproducibility and Manifest: Section 12.4 heading not found")
    section = rm_text[start:end]
    rows = re.findall(r"^\| `([^`]+)` \| `([^`]+)` \|$", section, flags=re.MULTILINE)
    if len(rows) != 7:
        fail(f"Section 12.3: expected 7 profile rows, found {len(rows)}")
    return rows


def extract_rm_view_registry(rm_text: str) -> list[tuple[str, str, str, str]]:
    start = rm_text.find("### 8.7 Kanonisches Stufen- und View-Schemaregister")
    if start < 0:
        fail("Reproducibility and Manifest: Section 8.7 heading not found")
    end = rm_text.find("#### 8.7.1", start)
    if end < 0:
        fail("Reproducibility and Manifest: Section 8.7.1 heading not found")
    section = rm_text[start:end]
    rows = re.findall(
        r"^\| `([^`]+)` \| `([^`]+)` \| `([^`]+)` \| \S+ \| `([0-9a-f]{64})` \|$",
        section,
        flags=re.MULTILINE,
    )
    if len(rows) != 6:
        fail(f"Section 8.7: expected 6 view registry rows, found {len(rows)}")
    return rows


def extract_section_24_example(rm_text: str) -> dict:
    heading = "## 24. Minimales kanonisches Dataset-Manifest"
    return find_json_block(rm_text, re.escape(heading), "Section 24 example")


def verify_literal_specification_hashes(rm_full_bytes: bytes) -> str:
    rm_actual_sha256 = sha256_hex(rm_full_bytes)
    for doc_id, version, expected_sha, filename in NON_SELF_SPECIFICATIONS:
        path = REPO / "docs/specifications" / filename
        actual = sha256_hex(read_bytes_checked(path))
        if actual != expected_sha:
            fail(
                f"{doc_id}/{version}: on-disk sha256 {actual} does not match "
                f"Revision 2 literal hash {expected_sha}"
            )
        header_pattern = rf"^\| Version \| `?{re.escape(version)}`? \|$"
        text = path.read_text(encoding="utf-8")
        if not re.search(header_pattern, text, flags=re.MULTILINE):
            fail(f"{doc_id}: header does not declare Version {version}")
    self_id, self_version, self_filename = SELF_SPECIFICATION
    assert self_filename == RM_PATH.name
    header_pattern = rf"^\| Version \| `?{re.escape(self_version)}`? \|$"
    if not re.search(header_pattern, rm_full_bytes.decode("utf-8"), flags=re.MULTILINE):
        fail(f"{self_id}: header does not declare Version {self_version}")
    return rm_actual_sha256


def compare_view_tuple(actual: dict, expected: tuple[str, str, str], label: str) -> None:
    exp_id, exp_version, exp_allow = expected
    if actual["schema_id"] != exp_id:
        fail(f"{label}: schema_id {actual['schema_id']!r} != expected {exp_id!r}")
    if actual["schema_version"] != exp_version:
        fail(f"{label}: schema_version {actual['schema_version']!r} != expected {exp_version!r}")
    if actual["allowlist_sha256"] != exp_allow:
        fail(f"{label}: allowlist_sha256 mismatch")


def compare_spec_tuple(actual: dict, expected_id: str, expected_version: str, label: str) -> None:
    if actual["id"] != expected_id:
        fail(f"{label}: id {actual['id']!r} != expected {expected_id!r}")
    if actual["version"] != expected_version:
        fail(f"{label}: version {actual['version']!r} != expected {expected_version!r}")


# ---------------------------------------------------------------------------
# Step 6: positive fixture reconciliation.
# ---------------------------------------------------------------------------

def verify_positive_fixture_contract(payload: dict, rm_actual_sha256: str, label: str) -> None:
    views = payload["views"]
    if len(views) != 6:
        fail(f"{label}: views must contain exactly 6 entries, found {len(views)}")
    for i, (view, expected) in enumerate(zip(views, EXPECTED_VIEW_IDENTITY)):
        compare_view_tuple(view, expected, f"{label} views[{i}]")

    profile = payload["specification_profile"]
    if len(profile) != 7:
        fail(f"{label}: specification_profile must contain exactly 7 entries, found {len(profile)}")
    for i, (doc_id, version, expected_sha, _filename) in enumerate(NON_SELF_SPECIFICATIONS):
        compare_spec_tuple(profile[i], doc_id, version, f"{label} specification_profile[{i}]")
        if profile[i]["sha256"] != expected_sha:
            fail(f"{label} specification_profile[{i}]: sha256 is not the literal non-self hash")
    self_entry = profile[6]
    compare_spec_tuple(self_entry, SELF_SPECIFICATION[0], SELF_SPECIFICATION[1], f"{label} specification_profile[6]")
    if self_entry["sha256"] != rm_actual_sha256:
        fail(
            f"{label} specification_profile[6]: RM self sha256 must equal the actual "
            f"current RM 0.9.0 byte digest ({rm_actual_sha256}), got {self_entry['sha256']}"
        )
    if self_entry["sha256"] == ZERO_DIGEST:
        fail(f"{label} specification_profile[6]: fixtures must not use the placeholder digest")


# ---------------------------------------------------------------------------
# Step 5: Section 24 example reconciliation (placeholder exception applies).
# ---------------------------------------------------------------------------

def verify_section_24_example(example: dict) -> None:
    if example["manifest_schema_version"] != "1.0.1":
        fail("Section 24: manifest_schema_version must be 1.0.1")
    if example["manifest_schema_ref"] != "rcc002.dataset-manifest/1.0.1":
        fail("Section 24: manifest_schema_ref must be rcc002.dataset-manifest/1.0.1")

    views = example["views"]
    if len(views) != 6:
        fail(f"Section 24: views must contain exactly 6 entries, found {len(views)}")
    for i, (view, expected) in enumerate(zip(views, EXPECTED_VIEW_IDENTITY)):
        compare_view_tuple(view, expected, f"Section 24 views[{i}]")

    profile = example["specification_profile"]
    if len(profile) != 7:
        fail(f"Section 24: specification_profile must contain exactly 7 entries, found {len(profile)}")
    for i, (doc_id, version, expected_sha, _filename) in enumerate(NON_SELF_SPECIFICATIONS):
        compare_spec_tuple(profile[i], doc_id, version, f"Section 24 specification_profile[{i}]")
        if profile[i]["sha256"] != expected_sha:
            fail(f"Section 24 specification_profile[{i}]: sha256 is not the literal non-self hash")
    self_entry = profile[6]
    compare_spec_tuple(self_entry, SELF_SPECIFICATION[0], SELF_SPECIFICATION[1], "Section 24 specification_profile[6]")
    if self_entry["sha256"] != ZERO_DIGEST:
        fail("Section 24 specification_profile[6]: RM self entry must be the labelled all-zero placeholder")


# ---------------------------------------------------------------------------
# Step 8: schema 1.0.1 encodes the exact ordered contracts.
# ---------------------------------------------------------------------------

def verify_schema_encodes_contracts(schema: dict) -> None:
    if schema["properties"]["manifest_schema_version"] != {"const": "1.0.1"}:
        fail("schema 1.0.1: manifest_schema_version const must be 1.0.1")
    if schema["properties"]["manifest_schema_ref"] != {"const": "rcc002.dataset-manifest/1.0.1"}:
        fail("schema 1.0.1: manifest_schema_ref const must be rcc002.dataset-manifest/1.0.1")

    views_schema = schema["properties"]["views"]
    if views_schema.get("minItems") != 6 or views_schema.get("maxItems") != 6:
        fail("schema 1.0.1: views must declare minItems == maxItems == 6")
    if views_schema.get("items") is not False:
        fail("schema 1.0.1: views must reject additional entries with items: false")
    prefix = views_schema.get("prefixItems")
    if not isinstance(prefix, list) or len(prefix) != 6:
        fail("schema 1.0.1: views.prefixItems must declare exactly 6 entries")
    for i, (expected_id, expected_version, expected_allow) in enumerate(EXPECTED_VIEW_IDENTITY):
        props = prefix[i]["properties"]
        if props["schema_id"] != {"const": expected_id}:
            fail(f"schema 1.0.1: views.prefixItems[{i}].schema_id const mismatch")
        if props["schema_version"] != {"const": expected_version}:
            fail(f"schema 1.0.1: views.prefixItems[{i}].schema_version const mismatch")
        if props["allowlist_sha256"] != {"const": expected_allow}:
            fail(f"schema 1.0.1: views.prefixItems[{i}].allowlist_sha256 const mismatch")

    spec_schema = schema["properties"]["specification_profile"]
    if spec_schema.get("minItems") != 7 or spec_schema.get("maxItems") != 7:
        fail("schema 1.0.1: specification_profile must declare minItems == maxItems == 7")
    if spec_schema.get("items") is not False:
        fail("schema 1.0.1: specification_profile must reject additional entries with items: false")
    sprefix = spec_schema.get("prefixItems")
    if not isinstance(sprefix, list) or len(sprefix) != 7:
        fail("schema 1.0.1: specification_profile.prefixItems must declare exactly 7 entries")
    expected_ids_versions = [(d, v) for d, v, _s, _f in NON_SELF_SPECIFICATIONS] + [
        (SELF_SPECIFICATION[0], SELF_SPECIFICATION[1])
    ]
    for i, (expected_id, expected_version) in enumerate(expected_ids_versions):
        props = sprefix[i]["properties"]
        if props["id"] != {"const": expected_id}:
            fail(f"schema 1.0.1: specification_profile.prefixItems[{i}].id const mismatch")
        if props["version"] != {"const": expected_version}:
            fail(f"schema 1.0.1: specification_profile.prefixItems[{i}].version const mismatch")


# ---------------------------------------------------------------------------
# Steps 9-10: Draft 2020-12 structural validation of every fixture.
# ---------------------------------------------------------------------------

def verify_jsonschema_dependency() -> None:
    installed = metadata.version("jsonschema")
    if installed != REQUIRED_JSONSCHEMA_VERSION:
        fail(
            f"jsonschema {REQUIRED_JSONSCHEMA_VERSION} is required for review "
            f"verification; found {installed}"
        )
    declared = read_text_checked(REPO / "requirements-rcc002-review.txt").strip()
    if declared != f"jsonschema=={REQUIRED_JSONSCHEMA_VERSION}":
        fail(f"requirements-rcc002-review.txt does not pin jsonschema=={REQUIRED_JSONSCHEMA_VERSION}")


def run_structural_validation(schema: dict, positive_paths: list[Path], negative_paths: list[Path]) -> dict:
    from jsonschema import Draft202012Validator

    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)

    positive_hashes = set()
    for path in positive_paths:
        raw = read_bytes_checked(path)
        payload = json.loads(raw)
        errors = list(validator.iter_errors(payload))
        if errors:
            fail(f"positive fixture rejected (must be accepted): {path}: {errors[0].message}")
        positive_hashes.add(sha256_hex(raw))

    for path in negative_paths:
        raw = read_bytes_checked(path)
        payload = json.loads(raw)
        errors = list(validator.iter_errors(payload))
        if not errors:
            fail(f"negative fixture accepted (must be rejected): {path}")

    return {
        "positive_fixture_files": len(positive_paths),
        "positive_fixture_distinct_payloads": len(positive_hashes),
    }


# ---------------------------------------------------------------------------
# Step 7: every semantic negative fixture differs in exactly its declared
# invalid dimension relative to the shared positive baseline.
# ---------------------------------------------------------------------------

def canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def verify_semantic_negative_isolation(baseline: dict, ledger: dict) -> None:
    for filename, dimension in SEMANTIC_NEGATIVE_DIMENSION.items():
        if filename not in ledger["cases"]:
            fail(f"case ledger: missing declared entry for {filename}")
        declared_class = ledger["cases"][filename]["rejection_class"]
        expected_class = filename[: -len(".json")].replace("-", "_")
        if declared_class != expected_class:
            fail(f"case ledger: {filename} rejection_class {declared_class!r} != {expected_class!r}")

        payload = json.loads(read_text_checked(NEGATIVE_ROOT / filename))
        for key in baseline:
            if key == dimension:
                continue
            if canonical(payload.get(key)) != canonical(baseline[key]):
                fail(
                    f"{filename}: field {key!r} deviates from the positive baseline; "
                    f"a semantic negative fixture must isolate its declared dimension "
                    f"({dimension!r}) and leave every other field unchanged"
                )
        if canonical(payload[dimension]) == canonical(baseline[dimension]):
            fail(f"{filename}: declared dimension {dimension!r} is unchanged from baseline")


# ---------------------------------------------------------------------------
# Immutable historical artifact byte-identity.
# ---------------------------------------------------------------------------

def verify_immutable_artifacts() -> None:
    for rel_path, expected_sha in EXPECTED_IMMUTABLE_HASHES.items():
        actual = sha256_hex(read_bytes_checked(REPO / rel_path))
        if actual != expected_sha:
            fail(f"immutable historical artifact changed: {rel_path} (expected {expected_sha}, got {actual})")


def derive_fixture_paths_from_scope(scope: dict) -> tuple[list[Path], list[Path]]:
    """Derive the positive/negative fixture read sets from the validated
    scope manifest rather than independent directory globbing (Finding
    S8RR002-CAND-ARCH-001, evidence item 2)."""
    declared = scope["correction_candidate_outputs"]
    if CASE_LEDGER_REL not in declared:
        fail(f"scope manifest: candidate outputs must declare {CASE_LEDGER_REL!r}")

    positive_rel = sorted(
        p for p in declared
        if p.startswith(FIXTURE_PREFIX) and not p.startswith(NEGATIVE_PREFIX)
    )
    negative_rel = sorted(
        p for p in declared
        if p.startswith(NEGATIVE_PREFIX) and p != CASE_LEDGER_REL
    )
    return [REPO / p for p in positive_rel], [REPO / p for p in negative_rel]


def main() -> int:
    scope = load_scope()

    # Narrow, name-only directory check: catches an undeclared extra fixture
    # file before any read occurs. This is the only directory enumeration in
    # this verifier; it never supplies the read set itself.
    verify_no_undeclared_fixture_files(scope)

    verify_jsonschema_dependency()

    rm_bytes = read_bytes_checked(RM_PATH)
    rm_text = rm_bytes.decode("utf-8")
    dp_text = read_text_checked(DATA_PIPELINE_PATH)

    rm_actual_sha256 = verify_literal_specification_hashes(rm_bytes)

    dp_views = extract_data_pipeline_view_contracts(dp_text)
    for i, (view, expected) in enumerate(zip(dp_views, EXPECTED_VIEW_IDENTITY)):
        compare_view_tuple(view, expected, f"Data Pipeline view[{i}]")

    rm_views = extract_rm_view_registry(rm_text)
    for i, (schema_id, schema_version, schema_ref, allowlist_sha256) in enumerate(rm_views):
        expected_id, expected_version, expected_allow = EXPECTED_VIEW_IDENTITY[i]
        if (schema_id, schema_version, allowlist_sha256) != (expected_id, expected_version, expected_allow):
            fail(f"RM SS8.7 view[{i}] does not match the authoritative Data Pipeline contract")
        if schema_ref != f"{schema_id}/{schema_version}":
            fail(f"RM SS8.7 view[{i}] schema_ref does not equal schema_id/schema_version")

    rm_profile = extract_rm_specification_profile(rm_text)
    expected_ids_versions = [(d, v) for d, v, _s, _f in NON_SELF_SPECIFICATIONS] + [
        (SELF_SPECIFICATION[0], SELF_SPECIFICATION[1])
    ]
    if rm_profile != expected_ids_versions:
        fail(f"RM SS12.3 specification profile mismatch: {rm_profile} != {expected_ids_versions}")

    example = extract_section_24_example(rm_text)
    verify_section_24_example(example)

    schema = json.loads(read_text_checked(DATASET_MANIFEST_SCHEMA_PATH))
    verify_schema_encodes_contracts(schema)

    positive_paths, negative_paths = derive_fixture_paths_from_scope(scope)

    baseline = json.loads(read_text_checked(FIXTURE_ROOT / "minimal-valid.json"))
    if len(positive_paths) != 2:
        fail(f"expected exactly 2 positive fixtures declared in scope, found {len(positive_paths)}")
    for path in positive_paths:
        payload = json.loads(read_text_checked(path))
        verify_positive_fixture_contract(payload, rm_actual_sha256, path.name)

    if len(negative_paths) != 21:
        fail(f"expected exactly 21 negative fixtures declared in scope, found {len(negative_paths)}")

    ledger = json.loads(read_text_checked(CASE_LEDGER_PATH))
    for path in negative_paths:
        if path.name not in ledger["cases"]:
            fail(f"case ledger: missing entry for {path.name}")
    if len(ledger["cases"]) != len(negative_paths):
        fail("case ledger: entry count does not match negative fixture count")

    verify_semantic_negative_isolation(baseline, ledger)

    structural_report = run_structural_validation(schema, positive_paths, negative_paths)

    verify_immutable_artifacts()

    if len(scope["correction_candidate_outputs"]) != len(EXPECTED_CANDIDATE_OUTPUTS):
        fail(
            "candidate inventory: scope declares "
            f"{len(scope['correction_candidate_outputs'])} candidate outputs, "
            f"expected exactly {len(EXPECTED_CANDIDATE_OUTPUTS)}"
        )

    candidate_inventory = {}
    for rel_path in scope["correction_candidate_outputs"]:
        candidate_inventory[rel_path] = sha256_hex(read_bytes_checked(REPO / rel_path))

    if len(candidate_inventory) != len(EXPECTED_CANDIDATE_OUTPUTS):
        fail(
            "candidate inventory: produced an incomplete inventory "
            f"({len(candidate_inventory)} of {len(EXPECTED_CANDIDATE_OUTPUTS)} required entries)"
        )

    print(
        json.dumps(
            {
                "result": "PASS",
                "correction_id": scope["correction_id"],
                "findings_closed": scope["findings_in_scope"],
                "rm_actual_sha256": rm_actual_sha256,
                "views_verified": len(EXPECTED_VIEW_IDENTITY),
                "specification_profile_verified": len(expected_ids_versions),
                "negative_fixtures_verified": len(negative_paths),
                **structural_report,
                "immutable_artifacts_verified": len(EXPECTED_IMMUTABLE_HASHES),
                "candidate_sha256_inventory": candidate_inventory,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except VerificationError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
