# RCC-002 S8BCP-001 Revision 2 Implementation Scientific Review Resolution

Date: 2026-07-30

Status: CORRECTED CANDIDATE READY FOR INDEPENDENT RE-REVIEW

This document resolves the findings in:

```text
RCC_002_S8BCP001_REV2_IMPLEMENTATION_SCIENTIFIC_REVIEW_2026-07-30.md
SHA256=5c27a496f51c0f1768d15ec7245d634018d9263256bb8400659bd8df205102ab
FINAL VERDICT=REJECT
```

The prior verdict remains an immutable audit result for the reviewed
minimal package. This resolution does not replace independent re-review and
does not certify the corrected candidate.

## Finding Resolution

| Finding | Classification | Resolution | Status |
|---|---|---|---|
| `F1` | Minimal-package evidence gap, not an implementation defect | The full package includes `rcc002/s3/constants.py` in both `BASELINE` and `CANDIDATE`. The files are byte-identical (`SHA256=5758c4036df5a8570c6a7e72d1b4bb6fb10ddc548b46f94a28cd25299ad5219a`). The candidate defines `INDICATOR_SCHEMA_REF` from `rcc002.stage.s3-indicators` and `1.0.0`. | RESOLVED BY COMPLETE EVIDENCE |
| `F2` | Minimal-package evidence gap and incorrect modification inference | The full package includes `rcc002/s4/schema.py` through `rcc002/s7/schema.py` in both trees. Each baseline/candidate pair is byte-identical. S4 inherits S3, S5 inherits S4, S6 inherits S5, and S7 inherits S6; therefore the inherited source-coordinate and schema-reference fields require no modification to those schema files. | RESOLVED BY COMPLETE EVIDENCE |
| `F3` | Confirmed implementation defect | `SourceManifest.__post_init__` now compares the stored `source_files` tuple with `build_source_snapshot(...).source_files` and raises `RCC_SOURCE_FILE_ORDER_MISMATCH` before publication if they differ. A regression test reproduces the prior reverse-order counterexample and verifies the registered error code from the Golden fixture. | CORRECTED |
| `F4` | Mixed: correct pre-sort implementation, incomplete registered error and fixture coverage | The existing normalization continues to assign `original_record_index` by enumerating raw rows before sorting. `SourceRowIdError` now carries structured reason codes. Width overflow raises `RCC_SOURCE_ROW_ID_WIDTH_OVERFLOW`. `S1Row` validates that each V2 row ID encodes its stored snapshot, ordinal, and original index; an index mismatch raises `RCC_SOURCE_RECORD_INDEX_NOT_ORIGINAL`. All four Golden negative cases are now directly fixture-bound. Historical V1 identities remain read-only compatible. | CORRECTED |
| `F5` | Minimal-package evidence gap, not an implementation defect | The full package includes `tests/fixtures/rcc002/source/binance_spot_kline_timestamp_golden.v1.json` and its exercising tests. | RESOLVED BY COMPLETE EVIDENCE |
| `F6` | Confirmed test-design gap | `tests/rcc002/s3/test_schema.py` now independently asserts `INDICATOR_SCHEMA_REF == "rcc002.stage.s3-indicators/1.0.0"` and verifies the row value against the same literal. | CORRECTED |

## Corrected-Candidate Verification

Executed in the isolated implementation-correction tree:

```text
python3 -m compileall -q rcc002 scripts/rcc002 tests/rcc002
PASS

python3 -m unittest discover -s tests/rcc002 -p 'test_*.py'
Ran 627 tests
OK

python3 scripts/rcc002/verify_source_profile_implementation.py \
  RCC_002_BINANCE_PROVIDER_EVIDENCE_INPUT_2026-07-30.zip
PASS
```

Provider-bound results:

```text
archive_count=4
record_count=92160
source_row_id_unique_count=92160
2024 timestamp unit=MILLISECOND
2025 timestamp unit=MICROSECOND
S0/S1 normalization parity=PASS for every archive
```

Repository-wide regression and historical-artifact verification remain
deferred until controlled import because the isolated candidate does not
contain the unrelated `run_engine` tree or every historical repository
artifact.

## Disposition

All findings from the rejected scientific review are either corrected in
code/tests or resolved by the complete evidence supplied in the full
re-review package. The corrected candidate is ready for independent
scientific re-review. It remains NOT CERTIFIED, and S8 remains prohibited.
