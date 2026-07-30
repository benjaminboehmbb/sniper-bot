# RCC-002 S8BCP-001 Revision 2 Mechanical Verification

## Document Control

| Field | Value |
|---|---|
| Verification ID | `RCC-002-S8BCP001-REV2-MV-001` |
| Date | 2026-07-30 |
| Status | PASS |
| Scope | Corrected normative candidate before focused re-review |

## 1. Deterministic Artifact Check

The repository-local verifier
`scripts/rcc002/verify_s8bcp001_artifacts.py` completed with:

```json
{
  "audit_v2_fields": 534,
  "correction_bundle_class_counts": {
    "REVIEW_ARTIFACT": 5,
    "SCHEMA_ARTIFACT": 103
  },
  "json_files": 94,
  "manifest_negative_fixtures": 66,
  "manifest_positive_fixtures": 12,
  "manifest_schemas": 6,
  "result": "PASS",
  "source_identity_golden_sha256": "3bddbcade7a268026a2912acbaf95817723ac243dfa57a77c2a75a2dae69ab32"
}
```

This check parsed every JSON file, verified exact specification metadata
versions, recalculated every S8 allowlist hash from the ownership registry,
proved Audit V2/Label Research field-array equality, reproduced Source
Snapshot V1 and Source Row ID V2 Golden values, checked Markdown fence/newline
integrity and compiled both verification scripts.

## 2. JSON Schema Verification

The six released schemas were compiled independently with:

```text
ajv-cli 5.0.0
ajv-formats 3.0.1
JSON Schema Draft 2020-12
```

| Schema | Compile | Positive fixtures | Negative fixtures |
|---|---|---:|---:|
| Source Manifest 1.0.0 | PASS | 2/2 | 11/11 rejected |
| Stage Manifest 1.0.0 | PASS | 2/2 | 11/11 rejected |
| Run Manifest 1.0.0 | PASS | 2/2 | 11/11 rejected |
| Dataset Manifest 1.0.0 | PASS | 2/2 | 11/11 rejected |
| Review Manifest 1.0.0 | PASS | 2/2 | 11/11 rejected |
| Reproduction Manifest 1.0.0 | PASS | 2/2 | 11/11 rejected |

Negative classes cover:

- missing required field;
- wrong type/nullability;
- extra property;
- invalid deterministic ID;
- non-UTC-Z timestamp;
- absolute path;
- path traversal;
- secret-like field;
- secret-like value;
- wrong schema identity;
- wrong schema version.

## 3. Provider Evidence Verification

`scripts/rcc002/verify_binance_provider_evidence.py` independently rescanned
the immutable uploaded evidence package:

| Metric | Result |
|---|---|
| Outer evidence SHA-256 | `e2c8218461d8a41e6c6b6122c3b1f8ac29935834193f3f0757edaae0b2e8ddbf` |
| Provider archives | 4 |
| Records scanned | 92,160 |
| Provider checksum failures | 0 |
| ZIP/member/header/column failures | 0 |
| Timestamp-unit/remainder failures | 0 |
| Candle relation/continuity failures | 0 |
| Result | PASS |

## 4. Candidate Byte Inventory

The corrected candidate uses a lexicographically ordered SHA-256 inventory
that excludes itself. `sha256sum -c` passed for every listed file. The
inventory's own byte hash is recorded outside its bytes and is the review
subject identifier used by the focused re-reviews.

## 5. Limitation

This verification proves artifact structure and the specified evidence
properties. It does not certify the future S0–S7 implementation, S3-to-S7
`indicator_schema_ref` repair or full production build.
