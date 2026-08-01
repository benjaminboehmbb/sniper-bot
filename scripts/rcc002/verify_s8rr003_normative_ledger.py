#!/usr/bin/env python3
"""RCC-002 S8-RR-003 normative ledger mechanical verifier.

Independently re-derives and verifies the exact 145-entry SHA256SUMS
successor scope for correction candidate RCC-002-S8RR003-NLBCP-001-REV2
(finding S8-RR3-B01). Standard library only.

Run from repository root:
    python3 scripts/rcc002/verify_s8rr003_normative_ledger.py
"""
import hashlib
import json
import os
import pathlib
import re
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# --- Independent hardcoded expected metadata (not read from the scope file) ---
SCOPE_SCHEMA_VERSION = "1"
SCOPE_ID = "RCC002_S8RR003_NORMATIVE_LEDGER_SCOPE_V1"
CORRECTION_ID = "RCC-002-S8RR003-NLBCP-001-REV2"
FINDING_IN_SCOPE = "S8-RR3-B01"
LEDGER_PATH = "SHA256SUMS"
HISTORICAL_LEDGER_SHA256 = "a34e5139dadfdfa9d72210ac12b733b0493b00c8396f8e48680634dfb5988e43"
PATH_ORDERING = "LC_ALL=C lexical order, repository-relative POSIX paths"
ENTRY_FORMAT = "lowercase SHA-256, two spaces, ./-prefixed path"
EXPECTED_CURRENT_ENTRY_COUNT = 145
CONSUMED_BY = "scripts/rcc002/verify_s8rr003_normative_ledger.py"

SCOPE_MANIFEST_PATH = "docs/review/evidence/RCC_002_S8RR003_NORMATIVE_LEDGER_SCOPE_V1.json"
HISTORICAL_EVIDENCE_PATH = "docs/review/evidence/RCC_002_S8BCP001_REV2_NORMATIVE_BUNDLE_SHA256SUMS_2026-07-30.txt"

PROTECTED_BUILDER_PATH = "scripts/build_rcc002_spec_bundle.py"

CURRENT_RM_PATH = "docs/specifications/RCC_002_REPRODUCIBILITY_AND_MANIFEST_2026-07-23.md"
CURRENT_RM_SHA256 = "23fd2fc0a0338124e9bbd9d95bf6797662d1e32012cb6247763e47a47bf61cf1"
STALE_RM_SHA256 = "22d6460f16f7f70e677a40dcd4e428e3739d9bb37fb0f7340512cca1b1ebb382"

EXPECTED_OVERLAP_PATH = CURRENT_RM_PATH

# The four S8-RR-003 lifecycle outputs that are not the two pre-existing
# review documents (readiness review, approved proposal); these are the
# net-new normative payload files this candidate introduces.
NEW_CORRECTION_PAYLOAD_PATHS = (
    HISTORICAL_EVIDENCE_PATH,
    SCOPE_MANIFEST_PATH,
    "scripts/rcc002/verify_s8rr003_normative_ledger.py",
    "tests/rcc002/test_s8rr003_normative_ledger.py",
)

# --- Independent hardcoded exact category path lists ---

HISTORICAL_NORMATIVE_PATHS = (
    "docs/review/RCC_002_S8BCP001_REV2_CORRECTED_ARTIFACT_ARCHITECTURE_RE_REVIEW_2026-07-30.md",
    "docs/review/RCC_002_S8BCP001_REV2_CORRECTED_ARTIFACT_SCIENTIFIC_RE_REVIEW_2026-07-30.md",
    "docs/review/RCC_002_S8BCP001_REV2_CORRECTED_CANDIDATE_SHA256SUMS_2026-07-30.txt",
    "docs/review/RCC_002_S8BCP001_REV2_DEPENDENCY_MATRIX_2026-07-30.md",
    "docs/review/RCC_002_S8BCP001_REV2_IDENTITY_GRAPH_2026-07-30.md",
    "docs/review/RCC_002_S8BCP001_REV2_MECHANICAL_VERIFICATION_2026-07-30.md",
    "docs/review/RCC_002_S8BCP001_REV2_PROVIDER_EVIDENCE_VERIFICATION_2026-07-30.md",
    "docs/specifications/RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md",
    "docs/specifications/RCC_002_DATA_VALIDATION_2026-07-23.md",
    "docs/specifications/RCC_002_INDICATOR_SPECIFICATION_2026-07-23.md",
    "docs/specifications/RCC_002_LABEL_AND_FORWARD_RETURN_SPECIFICATION_2026-07-23.md",
    "docs/specifications/RCC_002_REGIME_AND_GATE_SPECIFICATION_2026-07-23.md",
    "docs/specifications/RCC_002_REPRODUCIBILITY_AND_MANIFEST_2026-07-23.md",
    "docs/specifications/RCC_002_SIGNAL_TRANSFORMATION_2026-07-23.md",
    "registries/rcc002/release/release_artifact_class_registry.v1.json",
    "registries/rcc002/source/provider_archive_evidence.v1.json",
    "registries/rcc002/source/source_column_profile_registry.v1.json",
    "registries/rcc002/source/source_retrieval_registry.v1.json",
    "registries/rcc002/source/source_row_id_profile.v2.json",
    "registries/rcc002/source/source_snapshot_id_profile.v1.json",
    "registries/rcc002/source/timestamp_unit_profile.v1.json",
    "schemas/rcc002/manifests/dataset-manifest/1.0.0.schema.json",
    "schemas/rcc002/manifests/reproduction-manifest/1.0.0.schema.json",
    "schemas/rcc002/manifests/review-manifest/1.0.0.schema.json",
    "schemas/rcc002/manifests/run-manifest/1.0.0.schema.json",
    "schemas/rcc002/manifests/source-manifest/1.0.0.schema.json",
    "schemas/rcc002/manifests/stage-manifest/1.0.0.schema.json",
    "scripts/rcc002/verify_binance_provider_evidence.py",
    "scripts/rcc002/verify_s8bcp001_artifacts.py",
    "tests/fixtures/rcc002/manifests/dataset-manifest/1.0.0/complete-valid.json",
    "tests/fixtures/rcc002/manifests/dataset-manifest/1.0.0/minimal-valid.json",
    "tests/fixtures/rcc002/manifests/dataset-manifest/1.0.0/negative/absolute-path.json",
    "tests/fixtures/rcc002/manifests/dataset-manifest/1.0.0/negative/extra-property.json",
    "tests/fixtures/rcc002/manifests/dataset-manifest/1.0.0/negative/invalid-id.json",
    "tests/fixtures/rcc002/manifests/dataset-manifest/1.0.0/negative/invalid-timestamp.json",
    "tests/fixtures/rcc002/manifests/dataset-manifest/1.0.0/negative/missing-required-field.json",
    "tests/fixtures/rcc002/manifests/dataset-manifest/1.0.0/negative/path-traversal.json",
    "tests/fixtures/rcc002/manifests/dataset-manifest/1.0.0/negative/secret-like-field.json",
    "tests/fixtures/rcc002/manifests/dataset-manifest/1.0.0/negative/secret-like-value.json",
    "tests/fixtures/rcc002/manifests/dataset-manifest/1.0.0/negative/wrong-schema-identity.json",
    "tests/fixtures/rcc002/manifests/dataset-manifest/1.0.0/negative/wrong-schema-version.json",
    "tests/fixtures/rcc002/manifests/dataset-manifest/1.0.0/negative/wrong-type-nullability.json",
    "tests/fixtures/rcc002/manifests/reproduction-manifest/1.0.0/complete-valid.json",
    "tests/fixtures/rcc002/manifests/reproduction-manifest/1.0.0/minimal-valid.json",
    "tests/fixtures/rcc002/manifests/reproduction-manifest/1.0.0/negative/absolute-path.json",
    "tests/fixtures/rcc002/manifests/reproduction-manifest/1.0.0/negative/extra-property.json",
    "tests/fixtures/rcc002/manifests/reproduction-manifest/1.0.0/negative/invalid-id.json",
    "tests/fixtures/rcc002/manifests/reproduction-manifest/1.0.0/negative/invalid-timestamp.json",
    "tests/fixtures/rcc002/manifests/reproduction-manifest/1.0.0/negative/missing-required-field.json",
    "tests/fixtures/rcc002/manifests/reproduction-manifest/1.0.0/negative/path-traversal.json",
    "tests/fixtures/rcc002/manifests/reproduction-manifest/1.0.0/negative/secret-like-field.json",
    "tests/fixtures/rcc002/manifests/reproduction-manifest/1.0.0/negative/secret-like-value.json",
    "tests/fixtures/rcc002/manifests/reproduction-manifest/1.0.0/negative/wrong-schema-identity.json",
    "tests/fixtures/rcc002/manifests/reproduction-manifest/1.0.0/negative/wrong-schema-version.json",
    "tests/fixtures/rcc002/manifests/reproduction-manifest/1.0.0/negative/wrong-type-nullability.json",
    "tests/fixtures/rcc002/manifests/review-manifest/1.0.0/complete-valid.json",
    "tests/fixtures/rcc002/manifests/review-manifest/1.0.0/minimal-valid.json",
    "tests/fixtures/rcc002/manifests/review-manifest/1.0.0/negative/absolute-path.json",
    "tests/fixtures/rcc002/manifests/review-manifest/1.0.0/negative/extra-property.json",
    "tests/fixtures/rcc002/manifests/review-manifest/1.0.0/negative/invalid-id.json",
    "tests/fixtures/rcc002/manifests/review-manifest/1.0.0/negative/invalid-timestamp.json",
    "tests/fixtures/rcc002/manifests/review-manifest/1.0.0/negative/missing-required-field.json",
    "tests/fixtures/rcc002/manifests/review-manifest/1.0.0/negative/path-traversal.json",
    "tests/fixtures/rcc002/manifests/review-manifest/1.0.0/negative/secret-like-field.json",
    "tests/fixtures/rcc002/manifests/review-manifest/1.0.0/negative/secret-like-value.json",
    "tests/fixtures/rcc002/manifests/review-manifest/1.0.0/negative/wrong-schema-identity.json",
    "tests/fixtures/rcc002/manifests/review-manifest/1.0.0/negative/wrong-schema-version.json",
    "tests/fixtures/rcc002/manifests/review-manifest/1.0.0/negative/wrong-type-nullability.json",
    "tests/fixtures/rcc002/manifests/run-manifest/1.0.0/complete-valid.json",
    "tests/fixtures/rcc002/manifests/run-manifest/1.0.0/minimal-valid.json",
    "tests/fixtures/rcc002/manifests/run-manifest/1.0.0/negative/absolute-path.json",
    "tests/fixtures/rcc002/manifests/run-manifest/1.0.0/negative/extra-property.json",
    "tests/fixtures/rcc002/manifests/run-manifest/1.0.0/negative/invalid-id.json",
    "tests/fixtures/rcc002/manifests/run-manifest/1.0.0/negative/invalid-timestamp.json",
    "tests/fixtures/rcc002/manifests/run-manifest/1.0.0/negative/missing-required-field.json",
    "tests/fixtures/rcc002/manifests/run-manifest/1.0.0/negative/path-traversal.json",
    "tests/fixtures/rcc002/manifests/run-manifest/1.0.0/negative/secret-like-field.json",
    "tests/fixtures/rcc002/manifests/run-manifest/1.0.0/negative/secret-like-value.json",
    "tests/fixtures/rcc002/manifests/run-manifest/1.0.0/negative/wrong-schema-identity.json",
    "tests/fixtures/rcc002/manifests/run-manifest/1.0.0/negative/wrong-schema-version.json",
    "tests/fixtures/rcc002/manifests/run-manifest/1.0.0/negative/wrong-type-nullability.json",
    "tests/fixtures/rcc002/manifests/source-manifest/1.0.0/complete-valid.json",
    "tests/fixtures/rcc002/manifests/source-manifest/1.0.0/minimal-valid.json",
    "tests/fixtures/rcc002/manifests/source-manifest/1.0.0/negative/absolute-path.json",
    "tests/fixtures/rcc002/manifests/source-manifest/1.0.0/negative/extra-property.json",
    "tests/fixtures/rcc002/manifests/source-manifest/1.0.0/negative/invalid-id.json",
    "tests/fixtures/rcc002/manifests/source-manifest/1.0.0/negative/invalid-timestamp.json",
    "tests/fixtures/rcc002/manifests/source-manifest/1.0.0/negative/missing-required-field.json",
    "tests/fixtures/rcc002/manifests/source-manifest/1.0.0/negative/path-traversal.json",
    "tests/fixtures/rcc002/manifests/source-manifest/1.0.0/negative/secret-like-field.json",
    "tests/fixtures/rcc002/manifests/source-manifest/1.0.0/negative/secret-like-value.json",
    "tests/fixtures/rcc002/manifests/source-manifest/1.0.0/negative/wrong-schema-identity.json",
    "tests/fixtures/rcc002/manifests/source-manifest/1.0.0/negative/wrong-schema-version.json",
    "tests/fixtures/rcc002/manifests/source-manifest/1.0.0/negative/wrong-type-nullability.json",
    "tests/fixtures/rcc002/manifests/stage-manifest/1.0.0/complete-valid.json",
    "tests/fixtures/rcc002/manifests/stage-manifest/1.0.0/minimal-valid.json",
    "tests/fixtures/rcc002/manifests/stage-manifest/1.0.0/negative/absolute-path.json",
    "tests/fixtures/rcc002/manifests/stage-manifest/1.0.0/negative/extra-property.json",
    "tests/fixtures/rcc002/manifests/stage-manifest/1.0.0/negative/invalid-id.json",
    "tests/fixtures/rcc002/manifests/stage-manifest/1.0.0/negative/invalid-timestamp.json",
    "tests/fixtures/rcc002/manifests/stage-manifest/1.0.0/negative/missing-required-field.json",
    "tests/fixtures/rcc002/manifests/stage-manifest/1.0.0/negative/path-traversal.json",
    "tests/fixtures/rcc002/manifests/stage-manifest/1.0.0/negative/secret-like-field.json",
    "tests/fixtures/rcc002/manifests/stage-manifest/1.0.0/negative/secret-like-value.json",
    "tests/fixtures/rcc002/manifests/stage-manifest/1.0.0/negative/wrong-schema-identity.json",
    "tests/fixtures/rcc002/manifests/stage-manifest/1.0.0/negative/wrong-schema-version.json",
    "tests/fixtures/rcc002/manifests/stage-manifest/1.0.0/negative/wrong-type-nullability.json",
    "tests/fixtures/rcc002/source/binance_spot_kline_negative_fixtures.v1.json",
    "tests/fixtures/rcc002/source/binance_spot_kline_timestamp_golden.v1.json",
    "tests/fixtures/rcc002/source/source_identity_golden.v1.json",
)

S8RR002_CORRECTION_OUTPUTS = (
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
)

S8RR003_LIFECYCLE_OUTPUTS = (
    "docs/review/RCC_002_S8RR003_NORMATIVE_LEDGER_BLOCKER_CORRECTION_PROPOSAL_REV2_2026-08-01.md",
    "docs/review/RCC_002_S8_IMPLEMENTATION_READINESS_REVIEW_2026-08-01.md",
    "docs/review/evidence/RCC_002_S8BCP001_REV2_NORMATIVE_BUNDLE_SHA256SUMS_2026-07-30.txt",
    "docs/review/evidence/RCC_002_S8RR003_NORMATIVE_LEDGER_SCOPE_V1.json",
    "scripts/rcc002/verify_s8rr003_normative_ledger.py",
    "tests/rcc002/test_s8rr003_normative_ledger.py",
)

CURRENT_LEDGER_PATHS = (
    "docs/review/RCC_002_S8BCP001_REV2_CORRECTED_ARTIFACT_ARCHITECTURE_RE_REVIEW_2026-07-30.md",
    "docs/review/RCC_002_S8BCP001_REV2_CORRECTED_ARTIFACT_SCIENTIFIC_RE_REVIEW_2026-07-30.md",
    "docs/review/RCC_002_S8BCP001_REV2_CORRECTED_CANDIDATE_SHA256SUMS_2026-07-30.txt",
    "docs/review/RCC_002_S8BCP001_REV2_DEPENDENCY_MATRIX_2026-07-30.md",
    "docs/review/RCC_002_S8BCP001_REV2_IDENTITY_GRAPH_2026-07-30.md",
    "docs/review/RCC_002_S8BCP001_REV2_MECHANICAL_VERIFICATION_2026-07-30.md",
    "docs/review/RCC_002_S8BCP001_REV2_PROVIDER_EVIDENCE_VERIFICATION_2026-07-30.md",
    "docs/review/RCC_002_S8RR003_NORMATIVE_LEDGER_BLOCKER_CORRECTION_PROPOSAL_REV2_2026-08-01.md",
    "docs/review/RCC_002_S8_IMPLEMENTATION_READINESS_REVIEW_2026-08-01.md",
    "docs/review/evidence/RCC_002_S8BCP001_REV2_NORMATIVE_BUNDLE_SHA256SUMS_2026-07-30.txt",
    "docs/review/evidence/RCC_002_S8RR002_CORRECTION_VERIFIER_SCOPE_V1.json",
    "docs/review/evidence/RCC_002_S8RR003_NORMATIVE_LEDGER_SCOPE_V1.json",
    "docs/specifications/RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md",
    "docs/specifications/RCC_002_DATA_VALIDATION_2026-07-23.md",
    "docs/specifications/RCC_002_INDICATOR_SPECIFICATION_2026-07-23.md",
    "docs/specifications/RCC_002_LABEL_AND_FORWARD_RETURN_SPECIFICATION_2026-07-23.md",
    "docs/specifications/RCC_002_REGIME_AND_GATE_SPECIFICATION_2026-07-23.md",
    "docs/specifications/RCC_002_REPRODUCIBILITY_AND_MANIFEST_2026-07-23.md",
    "docs/specifications/RCC_002_SIGNAL_TRANSFORMATION_2026-07-23.md",
    "registries/rcc002/release/release_artifact_class_registry.v1.json",
    "registries/rcc002/source/provider_archive_evidence.v1.json",
    "registries/rcc002/source/source_column_profile_registry.v1.json",
    "registries/rcc002/source/source_retrieval_registry.v1.json",
    "registries/rcc002/source/source_row_id_profile.v2.json",
    "registries/rcc002/source/source_snapshot_id_profile.v1.json",
    "registries/rcc002/source/timestamp_unit_profile.v1.json",
    "requirements-rcc002-review.txt",
    "schemas/rcc002/manifests/dataset-manifest/1.0.0.schema.json",
    "schemas/rcc002/manifests/dataset-manifest/1.0.1.schema.json",
    "schemas/rcc002/manifests/reproduction-manifest/1.0.0.schema.json",
    "schemas/rcc002/manifests/review-manifest/1.0.0.schema.json",
    "schemas/rcc002/manifests/run-manifest/1.0.0.schema.json",
    "schemas/rcc002/manifests/source-manifest/1.0.0.schema.json",
    "schemas/rcc002/manifests/stage-manifest/1.0.0.schema.json",
    "scripts/rcc002/verify_binance_provider_evidence.py",
    "scripts/rcc002/verify_s8bcp001_artifacts.py",
    "scripts/rcc002/verify_s8rr002_artifacts.py",
    "scripts/rcc002/verify_s8rr003_normative_ledger.py",
    "tests/fixtures/rcc002/manifests/dataset-manifest/1.0.0/complete-valid.json",
    "tests/fixtures/rcc002/manifests/dataset-manifest/1.0.0/minimal-valid.json",
    "tests/fixtures/rcc002/manifests/dataset-manifest/1.0.0/negative/absolute-path.json",
    "tests/fixtures/rcc002/manifests/dataset-manifest/1.0.0/negative/extra-property.json",
    "tests/fixtures/rcc002/manifests/dataset-manifest/1.0.0/negative/invalid-id.json",
    "tests/fixtures/rcc002/manifests/dataset-manifest/1.0.0/negative/invalid-timestamp.json",
    "tests/fixtures/rcc002/manifests/dataset-manifest/1.0.0/negative/missing-required-field.json",
    "tests/fixtures/rcc002/manifests/dataset-manifest/1.0.0/negative/path-traversal.json",
    "tests/fixtures/rcc002/manifests/dataset-manifest/1.0.0/negative/secret-like-field.json",
    "tests/fixtures/rcc002/manifests/dataset-manifest/1.0.0/negative/secret-like-value.json",
    "tests/fixtures/rcc002/manifests/dataset-manifest/1.0.0/negative/wrong-schema-identity.json",
    "tests/fixtures/rcc002/manifests/dataset-manifest/1.0.0/negative/wrong-schema-version.json",
    "tests/fixtures/rcc002/manifests/dataset-manifest/1.0.0/negative/wrong-type-nullability.json",
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
    "tests/fixtures/rcc002/manifests/reproduction-manifest/1.0.0/complete-valid.json",
    "tests/fixtures/rcc002/manifests/reproduction-manifest/1.0.0/minimal-valid.json",
    "tests/fixtures/rcc002/manifests/reproduction-manifest/1.0.0/negative/absolute-path.json",
    "tests/fixtures/rcc002/manifests/reproduction-manifest/1.0.0/negative/extra-property.json",
    "tests/fixtures/rcc002/manifests/reproduction-manifest/1.0.0/negative/invalid-id.json",
    "tests/fixtures/rcc002/manifests/reproduction-manifest/1.0.0/negative/invalid-timestamp.json",
    "tests/fixtures/rcc002/manifests/reproduction-manifest/1.0.0/negative/missing-required-field.json",
    "tests/fixtures/rcc002/manifests/reproduction-manifest/1.0.0/negative/path-traversal.json",
    "tests/fixtures/rcc002/manifests/reproduction-manifest/1.0.0/negative/secret-like-field.json",
    "tests/fixtures/rcc002/manifests/reproduction-manifest/1.0.0/negative/secret-like-value.json",
    "tests/fixtures/rcc002/manifests/reproduction-manifest/1.0.0/negative/wrong-schema-identity.json",
    "tests/fixtures/rcc002/manifests/reproduction-manifest/1.0.0/negative/wrong-schema-version.json",
    "tests/fixtures/rcc002/manifests/reproduction-manifest/1.0.0/negative/wrong-type-nullability.json",
    "tests/fixtures/rcc002/manifests/review-manifest/1.0.0/complete-valid.json",
    "tests/fixtures/rcc002/manifests/review-manifest/1.0.0/minimal-valid.json",
    "tests/fixtures/rcc002/manifests/review-manifest/1.0.0/negative/absolute-path.json",
    "tests/fixtures/rcc002/manifests/review-manifest/1.0.0/negative/extra-property.json",
    "tests/fixtures/rcc002/manifests/review-manifest/1.0.0/negative/invalid-id.json",
    "tests/fixtures/rcc002/manifests/review-manifest/1.0.0/negative/invalid-timestamp.json",
    "tests/fixtures/rcc002/manifests/review-manifest/1.0.0/negative/missing-required-field.json",
    "tests/fixtures/rcc002/manifests/review-manifest/1.0.0/negative/path-traversal.json",
    "tests/fixtures/rcc002/manifests/review-manifest/1.0.0/negative/secret-like-field.json",
    "tests/fixtures/rcc002/manifests/review-manifest/1.0.0/negative/secret-like-value.json",
    "tests/fixtures/rcc002/manifests/review-manifest/1.0.0/negative/wrong-schema-identity.json",
    "tests/fixtures/rcc002/manifests/review-manifest/1.0.0/negative/wrong-schema-version.json",
    "tests/fixtures/rcc002/manifests/review-manifest/1.0.0/negative/wrong-type-nullability.json",
    "tests/fixtures/rcc002/manifests/run-manifest/1.0.0/complete-valid.json",
    "tests/fixtures/rcc002/manifests/run-manifest/1.0.0/minimal-valid.json",
    "tests/fixtures/rcc002/manifests/run-manifest/1.0.0/negative/absolute-path.json",
    "tests/fixtures/rcc002/manifests/run-manifest/1.0.0/negative/extra-property.json",
    "tests/fixtures/rcc002/manifests/run-manifest/1.0.0/negative/invalid-id.json",
    "tests/fixtures/rcc002/manifests/run-manifest/1.0.0/negative/invalid-timestamp.json",
    "tests/fixtures/rcc002/manifests/run-manifest/1.0.0/negative/missing-required-field.json",
    "tests/fixtures/rcc002/manifests/run-manifest/1.0.0/negative/path-traversal.json",
    "tests/fixtures/rcc002/manifests/run-manifest/1.0.0/negative/secret-like-field.json",
    "tests/fixtures/rcc002/manifests/run-manifest/1.0.0/negative/secret-like-value.json",
    "tests/fixtures/rcc002/manifests/run-manifest/1.0.0/negative/wrong-schema-identity.json",
    "tests/fixtures/rcc002/manifests/run-manifest/1.0.0/negative/wrong-schema-version.json",
    "tests/fixtures/rcc002/manifests/run-manifest/1.0.0/negative/wrong-type-nullability.json",
    "tests/fixtures/rcc002/manifests/source-manifest/1.0.0/complete-valid.json",
    "tests/fixtures/rcc002/manifests/source-manifest/1.0.0/minimal-valid.json",
    "tests/fixtures/rcc002/manifests/source-manifest/1.0.0/negative/absolute-path.json",
    "tests/fixtures/rcc002/manifests/source-manifest/1.0.0/negative/extra-property.json",
    "tests/fixtures/rcc002/manifests/source-manifest/1.0.0/negative/invalid-id.json",
    "tests/fixtures/rcc002/manifests/source-manifest/1.0.0/negative/invalid-timestamp.json",
    "tests/fixtures/rcc002/manifests/source-manifest/1.0.0/negative/missing-required-field.json",
    "tests/fixtures/rcc002/manifests/source-manifest/1.0.0/negative/path-traversal.json",
    "tests/fixtures/rcc002/manifests/source-manifest/1.0.0/negative/secret-like-field.json",
    "tests/fixtures/rcc002/manifests/source-manifest/1.0.0/negative/secret-like-value.json",
    "tests/fixtures/rcc002/manifests/source-manifest/1.0.0/negative/wrong-schema-identity.json",
    "tests/fixtures/rcc002/manifests/source-manifest/1.0.0/negative/wrong-schema-version.json",
    "tests/fixtures/rcc002/manifests/source-manifest/1.0.0/negative/wrong-type-nullability.json",
    "tests/fixtures/rcc002/manifests/stage-manifest/1.0.0/complete-valid.json",
    "tests/fixtures/rcc002/manifests/stage-manifest/1.0.0/minimal-valid.json",
    "tests/fixtures/rcc002/manifests/stage-manifest/1.0.0/negative/absolute-path.json",
    "tests/fixtures/rcc002/manifests/stage-manifest/1.0.0/negative/extra-property.json",
    "tests/fixtures/rcc002/manifests/stage-manifest/1.0.0/negative/invalid-id.json",
    "tests/fixtures/rcc002/manifests/stage-manifest/1.0.0/negative/invalid-timestamp.json",
    "tests/fixtures/rcc002/manifests/stage-manifest/1.0.0/negative/missing-required-field.json",
    "tests/fixtures/rcc002/manifests/stage-manifest/1.0.0/negative/path-traversal.json",
    "tests/fixtures/rcc002/manifests/stage-manifest/1.0.0/negative/secret-like-field.json",
    "tests/fixtures/rcc002/manifests/stage-manifest/1.0.0/negative/secret-like-value.json",
    "tests/fixtures/rcc002/manifests/stage-manifest/1.0.0/negative/wrong-schema-identity.json",
    "tests/fixtures/rcc002/manifests/stage-manifest/1.0.0/negative/wrong-schema-version.json",
    "tests/fixtures/rcc002/manifests/stage-manifest/1.0.0/negative/wrong-type-nullability.json",
    "tests/fixtures/rcc002/source/binance_spot_kline_negative_fixtures.v1.json",
    "tests/fixtures/rcc002/source/binance_spot_kline_timestamp_golden.v1.json",
    "tests/fixtures/rcc002/source/source_identity_golden.v1.json",
    "tests/rcc002/test_s8rr002_manifest_correction.py",
    "tests/rcc002/test_s8rr003_normative_ledger.py",
)


# --- Exact top-level scope-schema contract (independent of the scope file) ---

REQUIRED_TOP_LEVEL_KEYS = frozenset((
    'scope_schema_version',
    'scope_id',
    'correction_id',
    'finding_in_scope',
    'ledger_path',
    'historical_ledger_sha256',
    'path_ordering',
    'entry_format',
    'expected_current_entry_count',
    'consumed_by',
    'historical_normative_paths',
    's8rr002_correction_outputs',
    's8rr003_lifecycle_outputs',
    'current_ledger_paths',
))

CATEGORY_KEYS = (
    'historical_normative_paths',
    's8rr002_correction_outputs',
    's8rr003_lifecycle_outputs',
    'current_ledger_paths',
)

HEX64_RE = re.compile(r'^[0-9a-f]{64}$')


class VerificationError(Exception):
    """Raised when a mechanical invariant is violated."""

    def __init__(self, invariant, detail=None):
        self.invariant = invariant
        self.detail = detail
        super().__init__(invariant)


LEDGER_LINE_RE = re.compile(r'^([0-9a-f]{64})  (\./[^\\\r\n]+)$')


def validate_ascii_bytes(data, label):
    try:
        return data.decode('ascii')
    except UnicodeDecodeError:
        raise VerificationError('%s_non_ascii' % label)


def validate_no_crlf(data, label):
    if b'\r' in data:
        raise VerificationError('%s_crlf' % label)


def validate_final_newline(text, label):
    if text == '':
        raise VerificationError('%s_empty_file' % label)
    if not text.endswith('\n'):
        raise VerificationError('%s_missing_final_newline' % label)
    if text.endswith('\n\n'):
        raise VerificationError('%s_multiple_final_newlines' % label)


def validate_safe_relpath(path, label):
    if path.startswith('/'):
        raise VerificationError('%s_absolute_path' % label, path)
    if '\\' in path:
        raise VerificationError('%s_backslash_path' % label, path)
    parts = path.split('/')
    if '..' in parts:
        raise VerificationError('%s_parent_traversal' % label, path)
    if '' in parts or '.' in parts:
        raise VerificationError('%s_unsafe_path_component' % label, path)


def parse_ledger_bytes(data, label='ledger'):
    """Parse raw SHA256SUMS bytes into an ordered list of (digest, relpath).

    Structural parsing only -- never opens any declared target file.
    """
    validate_no_crlf(data, label)
    text = validate_ascii_bytes(data, label)
    validate_final_newline(text, label)
    body = text[:-1]
    lines = body.split('\n') if body else []
    entries = []
    seen_lines = set()
    seen_paths = set()
    for line in lines:
        if line == '':
            raise VerificationError('%s_empty_line' % label)
        m = LEDGER_LINE_RE.match(line)
        if not m:
            raise VerificationError('%s_malformed_line' % label)
        digest, rel = m.group(1), m.group(2)
        relpath = rel[2:]  # strip './'
        validate_safe_relpath(relpath, label)
        if relpath == LEDGER_PATH:
            raise VerificationError('%s_self_entry' % label)
        if line in seen_lines:
            raise VerificationError('%s_duplicate_line' % label)
        seen_lines.add(line)
        if relpath in seen_paths:
            raise VerificationError('%s_duplicate_path' % label)
        seen_paths.add(relpath)
        entries.append((digest, relpath))
    return entries


def require_exact_ordered_equality(actual, expected, label):
    actual = list(actual)
    expected = list(expected)
    if len(actual) != len(expected):
        raise VerificationError('%s_count_mismatch' % label, (len(actual), len(expected)))
    if set(actual) != set(expected):
        missing = sorted(set(expected) - set(actual))
        extra = sorted(set(actual) - set(expected))
        raise VerificationError('%s_set_mismatch' % label, {'missing': missing, 'extra': extra})
    if actual != expected:
        raise VerificationError('%s_order_mismatch' % label)


def require_sorted_unique(paths, label):
    if len(set(paths)) != len(paths):
        raise VerificationError('%s_duplicate_within_category' % label)
    if list(paths) != sorted(paths):
        raise VerificationError('%s_not_sorted' % label)


def require_protected_builder_absent(paths, label):
    if PROTECTED_BUILDER_PATH in paths:
        raise VerificationError('%s_protected_builder_present' % label)


def derive_union(a, b, c):
    return sorted(set(a) | set(b) | set(c))


def compute_overlap(a, b):
    return set(a) & set(b)


def require_single_expected_overlap(overlap_set, expected_path, label):
    if overlap_set != {expected_path}:
        raise VerificationError('%s_unexpected_overlap' % label, sorted(overlap_set))


def require_digest_for_path(entries, path, expected_digest, label):
    digest_by_path = {p: d for d, p in entries}
    if digest_by_path.get(path) != expected_digest:
        raise VerificationError('%s_digest_mismatch' % label, path)


def require_exact_bytes_hash(data, expected_hash, label):
    actual = hashlib.sha256(data).hexdigest()
    if actual != expected_hash:
        raise VerificationError('%s_hash_mismatch' % label, actual)


def require_object_root(doc, label):
    if not isinstance(doc, dict):
        raise VerificationError('%s_non_object_root' % label)


def require_exact_top_level_keys(doc, label):
    """Reject any scope document whose top-level key set is not exactly
    REQUIRED_TOP_LEVEL_KEYS -- missing or additional keys alike. Must run
    before any metadata or category value is inspected."""
    require_object_root(doc, label)
    actual_keys = set(doc.keys())
    missing = sorted(REQUIRED_TOP_LEVEL_KEYS - actual_keys)
    if missing:
        raise VerificationError('%s_missing_top_level_keys' % label, missing)
    extra = sorted(actual_keys - REQUIRED_TOP_LEVEL_KEYS)
    if extra:
        raise VerificationError('%s_extra_top_level_keys' % label, extra)


def require_single_hash_authority(doc, label):
    """Prove the only 64-hex-lowercase value anywhere in the scope document
    (top-level scalars or category list elements) is the exact
    historical_ledger_sha256 value at its authorized field. Hash authority
    belongs exclusively to the root ledger, apart from that one field."""
    require_object_root(doc, label)
    for key, value in doc.items():
        candidates = []
        if isinstance(value, str):
            candidates.append(value)
        elif isinstance(value, list):
            candidates.extend(item for item in value if isinstance(item, str))
        for candidate in candidates:
            if HEX64_RE.match(candidate):
                if key != 'historical_ledger_sha256' or candidate != HISTORICAL_LEDGER_SHA256:
                    raise VerificationError('%s_unauthorized_hash_value' % label, key)


def sha256_of_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha256_of_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def validate_scope_metadata(doc):
    require_object_root(doc, 'scope_metadata')
    expected = {
        'scope_schema_version': SCOPE_SCHEMA_VERSION,
        'scope_id': SCOPE_ID,
        'correction_id': CORRECTION_ID,
        'finding_in_scope': FINDING_IN_SCOPE,
        'ledger_path': LEDGER_PATH,
        'historical_ledger_sha256': HISTORICAL_LEDGER_SHA256,
        'path_ordering': PATH_ORDERING,
        'entry_format': ENTRY_FORMAT,
        'expected_current_entry_count': EXPECTED_CURRENT_ENTRY_COUNT,
        'consumed_by': CONSUMED_BY,
    }
    for key, value in expected.items():
        if key not in doc:
            raise VerificationError('scope_metadata_missing_%s' % key)
        actual_value = doc[key]
        if type(actual_value) is not type(value):
            raise VerificationError('scope_metadata_wrong_type_%s' % key)
        if actual_value != value:
            raise VerificationError('scope_metadata_mismatch_%s' % key, actual_value)


def validate_scope_categories(doc):
    require_object_root(doc, 'scope_categories')
    for key, expected in (
        ('historical_normative_paths', HISTORICAL_NORMATIVE_PATHS),
        ('s8rr002_correction_outputs', S8RR002_CORRECTION_OUTPUTS),
        ('s8rr003_lifecycle_outputs', S8RR003_LIFECYCLE_OUTPUTS),
        ('current_ledger_paths', CURRENT_LEDGER_PATHS),
    ):
        if key not in doc:
            raise VerificationError('scope_category_missing_%s' % key)
        actual = doc[key]
        if not isinstance(actual, list):
            raise VerificationError('scope_category_not_list_%s' % key)
        if not all(isinstance(item, str) for item in actual):
            raise VerificationError('scope_category_non_string_element_%s' % key)
        require_sorted_unique(actual, key)
        require_protected_builder_absent(actual, key)
        require_exact_ordered_equality(actual, expected, key)


def validate_derived_union():
    derived = derive_union(HISTORICAL_NORMATIVE_PATHS, S8RR002_CORRECTION_OUTPUTS, S8RR003_LIFECYCLE_OUTPUTS)
    require_exact_ordered_equality(derived, CURRENT_LEDGER_PATHS, 'derived_union')
    if len(derived) != EXPECTED_CURRENT_ENTRY_COUNT:
        raise VerificationError('derived_union_count_mismatch', len(derived))


def validate_overlap():
    overlap_ab = compute_overlap(HISTORICAL_NORMATIVE_PATHS, S8RR002_CORRECTION_OUTPUTS)
    require_single_expected_overlap(overlap_ab, EXPECTED_OVERLAP_PATH, 'overlap_a_b')
    overlap_ac = compute_overlap(HISTORICAL_NORMATIVE_PATHS, S8RR003_LIFECYCLE_OUTPUTS)
    if overlap_ac:
        raise VerificationError('unexpected_overlap_a_c', sorted(overlap_ac))
    overlap_bc = compute_overlap(S8RR002_CORRECTION_OUTPUTS, S8RR003_LIFECYCLE_OUTPUTS)
    if overlap_bc:
        raise VerificationError('unexpected_overlap_b_c', sorted(overlap_bc))


def validate_no_protected_builder_anywhere(doc):
    require_protected_builder_absent(HISTORICAL_NORMATIVE_PATHS, 'hardcoded_historical')
    require_protected_builder_absent(S8RR002_CORRECTION_OUTPUTS, 'hardcoded_s8rr002')
    require_protected_builder_absent(S8RR003_LIFECYCLE_OUTPUTS, 'hardcoded_s8rr003')
    require_protected_builder_absent(CURRENT_LEDGER_PATHS, 'hardcoded_union')
    for key in CATEGORY_KEYS:
        require_protected_builder_absent(doc[key], 'scope_%s' % key)


def validate_historical_evidence(repo_root):
    path = os.path.join(repo_root, HISTORICAL_EVIDENCE_PATH)
    if os.path.islink(path):
        raise VerificationError('historical_evidence_is_symlink')
    if not os.path.isfile(path):
        raise VerificationError('historical_evidence_missing')
    data = pathlib.Path(path).read_bytes()
    require_exact_bytes_hash(data, HISTORICAL_LEDGER_SHA256, 'historical_evidence')
    entries = parse_ledger_bytes(data, label='historical_evidence')
    if len(entries) != 110:
        raise VerificationError('historical_evidence_count_mismatch', len(entries))
    paths = [p for _, p in entries]
    require_sorted_unique(paths, 'historical_evidence')
    require_protected_builder_absent(paths, 'historical_evidence')
    require_digest_for_path(entries, CURRENT_RM_PATH, STALE_RM_SHA256, 'historical_evidence_stale_rm')
    return data, entries


def validate_current_ledger(repo_root):
    path = os.path.join(repo_root, LEDGER_PATH)
    if os.path.islink(path):
        raise VerificationError('current_ledger_is_symlink')
    if not os.path.isfile(path):
        raise VerificationError('current_ledger_missing')
    data = pathlib.Path(path).read_bytes()
    entries = parse_ledger_bytes(data, label='current_ledger')
    if len(entries) != EXPECTED_CURRENT_ENTRY_COUNT:
        raise VerificationError('current_ledger_count_mismatch', len(entries))
    paths = [p for _, p in entries]
    require_protected_builder_absent(paths, 'current_ledger')
    require_exact_ordered_equality(paths, CURRENT_LEDGER_PATHS, 'current_ledger_paths')
    require_digest_for_path(entries, CURRENT_RM_PATH, CURRENT_RM_SHA256, 'current_ledger_certified_rm')
    entry_paths = {p for _, p in entries}
    for p in NEW_CORRECTION_PAYLOAD_PATHS:
        if p not in entry_paths:
            raise VerificationError('current_ledger_missing_correction_payload', p)
    return data, entries


def validate_ledgers_differ(historical_data, current_data):
    if historical_data == current_data:
        raise VerificationError('historical_and_current_ledger_identical')


def validate_target_files(repo_root, entries):
    """Only called after every scope and ledger-structure gate has passed."""
    for digest, relpath in entries:
        abspath = os.path.join(repo_root, relpath)
        if os.path.islink(abspath):
            raise VerificationError('target_is_symlink', relpath)
        if not os.path.isfile(abspath):
            raise VerificationError('target_missing', relpath)
        actual = sha256_of_file(abspath)
        if actual != digest:
            raise VerificationError('target_hash_mismatch', relpath)


def load_scope_manifest(repo_root):
    path = os.path.join(repo_root, SCOPE_MANIFEST_PATH)
    if os.path.islink(path):
        raise VerificationError('scope_manifest_is_symlink')
    if not os.path.isfile(path):
        raise VerificationError('scope_manifest_missing')
    data = pathlib.Path(path).read_bytes()
    text = validate_ascii_bytes(data, 'scope_manifest')
    validate_final_newline(text, 'scope_manifest')
    try:
        doc = json.loads(text)
    except json.JSONDecodeError:
        raise VerificationError('scope_manifest_invalid_json')
    require_object_root(doc, 'scope_manifest')
    return doc


def run_verification(repo_root):
    # 0: exact top-level scope-schema contract and single-hash-authority proof,
    # before any metadata value, category value, or ledger byte is read.
    doc = load_scope_manifest(repo_root)
    require_exact_top_level_keys(doc, 'scope')
    require_single_hash_authority(doc, 'scope')

    # 1-4: scope metadata / category equality / derived union, before any ledger read.
    validate_scope_metadata(doc)
    validate_scope_categories(doc)
    validate_derived_union()
    validate_overlap()
    validate_no_protected_builder_anywhere(doc)

    # 5-7: parse root SHA256SUMS structurally, without reading declared targets.
    current_path = os.path.join(repo_root, LEDGER_PATH)
    if os.path.islink(current_path):
        raise VerificationError('current_ledger_is_symlink')
    current_data = pathlib.Path(current_path).read_bytes()
    current_entries = parse_ledger_bytes(current_data, label='current_ledger')
    current_paths = [p for _, p in current_entries]
    require_protected_builder_absent(current_paths, 'current_ledger')  # 8
    if len(current_entries) != EXPECTED_CURRENT_ENTRY_COUNT:
        raise VerificationError('current_ledger_count_mismatch', len(current_entries))
    require_exact_ordered_equality(current_paths, CURRENT_LEDGER_PATHS, 'current_ledger_paths')
    require_digest_for_path(current_entries, CURRENT_RM_PATH, CURRENT_RM_SHA256, 'current_ledger_certified_rm')
    current_entry_paths = {p for _, p in current_entries}
    for p in NEW_CORRECTION_PAYLOAD_PATHS:
        if p not in current_entry_paths:
            raise VerificationError('current_ledger_missing_correction_payload', p)

    # Historical evidence copy: structural + digest proof, still no target-file reads.
    historical_data, historical_entries = validate_historical_evidence(repo_root)
    validate_ledgers_differ(historical_data, current_data)

    # Only now, after every scope and ledger-structure gate has passed, hash targets.
    validate_target_files(repo_root, current_entries)

    return {
        'result': 'PASS',
        'scope_id': SCOPE_ID,
        'correction_id': CORRECTION_ID,
        'finding_in_scope': FINDING_IN_SCOPE,
        'historical_entry_count': len(HISTORICAL_NORMATIVE_PATHS),
        's8rr002_output_count': len(S8RR002_CORRECTION_OUTPUTS),
        's8rr003_output_count': len(S8RR003_LIFECYCLE_OUTPUTS),
        'current_ledger_entry_count': len(current_entries),
        'verified_entry_count': len(current_entries),
        'historical_ledger_sha256': HISTORICAL_LEDGER_SHA256,
        'current_rm_sha256': CURRENT_RM_SHA256,
    }


def main():
    try:
        result = run_verification(REPO_ROOT)
    except VerificationError as exc:
        failure = {
            'result': 'FAIL',
            'scope_id': SCOPE_ID,
            'failed_invariant': exc.invariant,
        }
        sys.stdout.write(json.dumps(failure, indent=2, sort_keys=False) + '\n')
        return 1
    sys.stdout.write(json.dumps(result, indent=2, sort_keys=False) + '\n')
    return 0


if __name__ == '__main__':
    sys.exit(main())
