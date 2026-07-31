# RCC-002 S8BCP-001 Revision 2 Implementation — Independent Scientific Consistency Re-Review

## Document Control

| Field | Value |
|---|---|
| Review ID | `RCC-002-S8BCP001-REV2-IMPL-SCI-002` |
| Date | 2026-07-30 |
| Review class | Independent scientific consistency **re-review** (post-correction) |
| Reviewed package | `/home/benja/rcc002-reviews/2026-07-30/scientific-re-review` |
| Repository baseline | `d9e37cba304b049fa518e163810c53eb9c83fc13` |
| Prior verdict re-examined | `RCC_002_S8BCP001_REV2_IMPLEMENTATION_SCIENTIFIC_REVIEW_2026-07-30.md` — **REJECT** (`F1`–`F6`) |
| Resolution document re-examined, not trusted uncritically | `CANDIDATE/docs/review/RCC_002_S8BCP001_REV2_IMPLEMENTATION_SCIENTIFIC_REVIEW_RESOLUTION_2026-07-30.md` |
| Final verdict | **APPROVE** |

---

## 1. Reviewer role and scope

This review was performed as an **independent scientific consistency
reviewer**, per `SCIENTIFIC_RE_REVIEW_PROMPT.md`, of the corrected S8BCP-001
Revision 2 implementation. The mandate is to determine, from evidence
reproduced directly by this review (not from the prior REJECT review's
findings or the candidate's own resolution document, both treated as
unverified claims until independently re-derived), whether:

- prior findings `F1`–`F6` are genuinely resolved rather than merely
  asserted resolved;
- the ten scientific-consistency review items in the prompt hold exactly;
- no new blocking defect, evidentiary gap, or unverifiable claim has been
  introduced.

Scope boundaries observed:

- Only this package directory was used. No access to
  `/home/benja/projects/sniper-bot`, no network access, no package
  installation, and no modification of `README.md`, `SCIENTIFIC_RE_REVIEW_PROMPT.md`,
  `CHANGED_FILES.txt`, `SHA256SUMS`, `BASELINE/`, `CANDIDATE/`,
  `PRIOR_REVIEW/`, or `EVIDENCE/` occurred.
- All code execution (`sha256sum -c`, `python3 -m compileall`,
  `python3 -m unittest`, the package's own provider-verification script, and
  ad hoc reproduction scripts for golden fixtures and the `F3` counterexample)
  ran against read-only copies of `CANDIDATE/` in this session's private
  scratch directory, or directly read files without writing to them.
- Every claim in the prior review and the resolution document that could be
  independently checked from this package was re-derived from the actual
  code, tests, registries, schemas, and fixtures — not accepted at face
  value. Where noted below, this review reproduced results (golden hashes,
  reason codes, the `F3` counterexample) using code paths of its own
  construction, not merely by running the candidate's supplied tests.
- Repository-wide regression and historical-artifact verification are
  explicitly out of scope per `README.md` (deferred to the controlled-import
  gate because `run_engine` and unrelated repository components are
  intentionally excluded from this package) and are not treated as missing
  evidence.

---

## 2. Evidence inspected

### 2.1 Governance and inventory

- `README.md`, `SCIENTIFIC_RE_REVIEW_PROMPT.md`, `ARCHITECTURE_REVIEW_PROMPT.md`.
- `CHANGED_FILES.txt` — 37 entries.
- `SHA256SUMS` — 542 entries; verified with `sha256sum -c SHA256SUMS`:
  **542/542 PASS**.
- Full recursive `diff -rq BASELINE CANDIDATE`: exactly the 37 changes
  declared in `CHANGED_FILES.txt` were found (27 `MODIFIED`, 10 `ADDED`); no
  undeclared difference exists anywhere in the two trees (263 files in
  `BASELINE`, 273 in `CANDIDATE`). This directly falsifies, by
  reconstruction, the premise of the prior review's `F1`/`F2`
  ("`CHANGED_FILES.txt` … is demonstrably false") for **this** package: the
  inventory is now exhaustive and verified byte-for-byte.

### 2.2 Prior review and resolution document

- `PRIOR_REVIEW/RCC_002_S8BCP001_REV2_IMPLEMENTATION_SCIENTIFIC_REVIEW_2026-07-30.md`
  (full text; `REJECT`, findings `F1`–`F6`).
- `CANDIDATE/docs/review/RCC_002_S8BCP001_REV2_IMPLEMENTATION_SCIENTIFIC_REVIEW_RESOLUTION_2026-07-30.md`
  (full text; read as an unverified claim of resolution, verified independently below).

### 2.3 Registries, schema, and golden fixtures (ground truth used for verification)

- `CANDIDATE/registries/rcc002/source/timestamp_unit_profile.v1.json`
- `CANDIDATE/registries/rcc002/source/source_row_id_profile.v2.json`
- `CANDIDATE/registries/rcc002/source/source_snapshot_id_profile.v1.json`
- `CANDIDATE/schemas/rcc002/manifests/source-manifest/1.0.0.schema.json`
- `CANDIDATE/tests/fixtures/rcc002/source/source_identity_golden.v1.json`
- `CANDIDATE/tests/fixtures/rcc002/source/binance_spot_kline_timestamp_golden.v1.json`
  (the fixture whose absence was `F5`; now present, full text read)

### 2.4 Production code (full-text read, plus `diff -u` against `BASELINE` for every changed file)

`rcc002/s0/ingest.py`, `rcc002/s0/manifest.py`, `rcc002/s0/profiles.py`,
`rcc002/s0/source_identity.py`, `rcc002/s1/normalize.py`, `rcc002/s1/row_id.py`,
`rcc002/s1/schema.py`, `rcc002/s2/schema.py`, `rcc002/s2/validate.py`,
`rcc002/s3/compute.py`, `rcc002/s3/schema.py`, `rcc002/s3/constants.py`,
`rcc002/s4/compute.py`, `rcc002/s4/constants.py`, `rcc002/s4/schema.py`,
`rcc002/s5/constants.py`, `rcc002/s5/schema.py`, `rcc002/s6/constants.py`,
`rcc002/s6/schema.py`, `rcc002/s7/constants.py`, `rcc002/s7/schema.py`,
`rcc002/IMPLEMENTATION_BLOCKERS.md`, `scripts/rcc002/verify_source_profile_implementation.py`.

Byte-equality of the files the prior review could not obtain (`F1`/`F2`) was
directly verified, not merely asserted:

```text
rcc002/s3/constants.py  BASELINE == CANDIDATE  sha256=5758c4036df5a8570c6a7e72d1b4bb6fb10ddc548b46f94a28cd25299ad5219a
rcc002/s4/schema.py     BASELINE == CANDIDATE  sha256=391b7a940135ec0d444dcf094a57398d421f100acb612346e5d59ecda95f0296
rcc002/s5/schema.py     BASELINE == CANDIDATE  sha256=d2f875675c31b38b8d55ab8ff3f095537fb4fdd0cf17b72d5c8929747ff15bf6
rcc002/s6/schema.py     BASELINE == CANDIDATE  sha256=67f5ad46e882729089962f6dbee4621c9f26e9d6691e8eac43d458f195e96364
rcc002/s7/schema.py     BASELINE == CANDIDATE  sha256=7e0571c1d769e82193931a10e8495bba231cd9e4a15c9a786a5ffcf73f615663
```

### 2.5 Test code (full-text read for the four negative-case-bearing files; diff-read for the rest)

`tests/rcc002/s0/test_manifest.py`, `tests/rcc002/s0/test_source_identity.py`
(new), `tests/rcc002/s0/test_profiles.py` (new), `tests/rcc002/s1/test_row_id.py`,
`tests/rcc002/s1/test_schema.py`, `tests/rcc002/s1/test_normalize.py`,
`tests/rcc002/s2/test_{anomalies,duplicates,schema,segment,validate}.py`,
`tests/rcc002/s3/test_{compute,schema}.py`, `tests/rcc002/s4/test_compute.py`,
`tests/rcc002/test_s8bcp001_implementation_correction.py` (new).

### 2.6 Independent mechanical verification performed by this review

All executed read-only in a private scratch copy (`CANDIDATE/rcc002`,
`CANDIDATE/tests`, `CANDIDATE/scripts`, `CANDIDATE/schemas`,
`CANDIDATE/registries`, `CANDIDATE/docs`):

1. `sha256sum -c SHA256SUMS` — **542/542 PASS**.
2. `python3 -m compileall -q rcc002 scripts/rcc002 tests/rcc002` — **PASS**,
   all files syntactically valid (resolves the prior `ModuleNotFoundError`
   class of failure entirely: every import in every test now resolves).
3. `python3 -m unittest discover -s tests/rcc002 -p 'test_*.py'` — **Ran 627
   tests, OK** (matches the resolution document's claim exactly; not taken
   on faith — re-executed independently in this review's own scratch copy).
4. Reproduced, by writing independent Python against the imported modules
   (not by running the package's own tests), all of:
   - the Source Snapshot V1 golden preimage/hash/ID from
     `source_identity_golden.v1.json` — **exact match**
     (`3bddbcade7a268026a2912acbaf95817723ac243dfa57a77c2a75a2dae69ab32`);
   - both Source Row ID V2 golden cases from the same fixture — **exact
     match**;
   - all 6 cases in `binance_spot_kline_timestamp_golden.v1.json` (unit
     selection + ms/µs conversion across both the `DAILY` and `MONTHLY`
     archive families, both sides of the 2025-01-01 boundary) — **exact
     match**;
   - the `F3` reverse-order counterexample, called directly against
     `SourceManifest.__init__`/`__post_init__` (not via
     `dataclasses.replace`, to rule out a `replace`-specific code path) —
     **now rejected** with `reason_code == "RCC_SOURCE_FILE_ORDER_MISMATCH"`;
   - `rcc002.s7.constants.LABEL_SCHEMA_FINGERPRINT_SHA256` and
     `SEMANTIC_BUILD_CONFIGURATION_SHA256`, by direct import (now possible:
     `rcc002.s6.schema.S6Row` is present and byte-identical to `BASELINE`) —
     recomputed values
     `6fb2bcdeae2070f054fcf298693382b668ed267017f4e0f72be87615a3827bce` and
     `8ca946ee9725e6f767ff498c7d41362181f52457de7f5494a48a4b32b0806905`
     **match exactly** the values the prior review could only report as
     "taken on faith."
5. Ran the four fixture-bound negative-case tests explicitly and in
   isolation: `test_noncanonical_source_file_order_is_rejected`,
   `test_duplicate_logical_period_matches_golden_error`,
   `test_record_index_after_sort_is_rejected`,
   `test_registered_width_overflow_rejected` — **4/4 PASS**, each asserting
   `context.exception.reason_code == case["expected_error"]` read live from
   `source_identity_golden.v1.json`, not a hardcoded string.
6. Executed `scripts/rcc002/verify_source_profile_implementation.py` against
   `EVIDENCE/RCC_002_BINANCE_PROVIDER_EVIDENCE_INPUT_2026-07-30.zip`
   (4 archives: `BTCUSDT-1m-2024-12-31.zip`/`.CHECKSUM`,
   `BTCUSDT-1m-2024-12.zip`/`.CHECKSUM`, `BTCUSDT-1m-2025-01-01.zip`/`.CHECKSUM`,
   `BTCUSDT-1m-2025-01.zip`/`.CHECKSUM`) — **PASS**, reproducing exactly:
   `archive_count=4`, `record_count=92160`,
   `source_row_id_unique_count=92160` (no collisions across any of the four
   archives), 2024 archives → `MILLISECOND`, 2025 archives → `MICROSECOND`,
   S0/S1 normalization parity `PASS` for all four. This matches the
   resolution document's claimed provider-bound results exactly and was
   re-executed by this review, not copied from the document.
7. `diff -u` of every one of the 27 `MODIFIED` production files against
   `BASELINE`, confirming: `s3/compute.py` and `s4/compute.py` diffs are
   strictly additive schema/reference wiring (no indicator/signal formula
   line touched); `s5/constants.py`, `s6/constants.py`,
   `s4/constants.py`, `s7/constants.py` diffs are exactly the claimed
   patch-version bumps (`0.3.0→0.3.1`, `0.4.0→0.4.1`, `0.4.0→0.4.1`,
   `0.3.0→0.3.1`) plus, for `s7/constants.py`, the dynamic
   `fields(S6Row)`-derived `input_fields`/`input_field_order`; `s2/schema.py`
   and `s2/validate.py` diffs add exactly `source_file_ordinal`/
   `original_record_index` pass-through; `s0/ingest.py` now returns
   `LegacySourceManifest` (not `SourceManifest`), consistent with the
   resolution's claimed generic/registered split.
8. Confirmed the dataclass inheritance chain
   `S4Row(S3Row)` → `S5Row(S4Row)` → `S6Row(S5Row)` → `S7Row(S6Row)` by
   direct source inspection (`s4/schema.py:75`, `s5/schema.py:24`,
   `s6/schema.py:25`, `s7/schema.py:303`), which is why byte-identical,
   unmodified `s4/schema.py`–`s7/schema.py` files are sufficient (not
   suspicious) for the new `source_file_ordinal`/`original_record_index`/
   `indicator_schema_ref` fields introduced on `S3Row` to propagate to every
   downstream row type without editing those files — this was independently
   confirmed by a live `dataclasses.fields()` inspection, not assumed from
   the resolution document's prose.

---

## 3. Prior-finding disposition table (`F1`–`F6`)

| ID | Prior severity | Prior review's claim | This review's independent verification | Disposition |
|---|---|---|---|---|
| **F1** | Blocking | `rcc002/s3/constants.py` absent; `INDICATOR_SCHEMA_REF` value unverifiable | File present in both `BASELINE` and `CANDIDATE`, confirmed byte-identical by this review's own `sha256sum` (§2.4). `INDICATOR_SCHEMA_REF = "rcc002.stage.s3-indicators/1.0.0"` read directly from `rcc002/s3/constants.py:14` and independently asserted literal (not merely self-consistent) in `tests/rcc002/s3/test_schema.py:99-102`, executed and passing. | **RESOLVED** — minimal-package evidence gap, confirmed not an implementation defect. |
| **F2** | Blocking | `s4/schema.py`–`s7/schema.py` absent; S4–S7 field propagation and S7 identity hashes unverifiable | All four files present, confirmed byte-identical to `BASELINE` by this review. Inheritance chain (`S4Row(S3Row)`→…→`S7Row(S6Row)`) directly inspected and confirmed sufficient for field propagation without modification. `_S3_FIELD_NAMES` in `s4/compute.py:227-229` is derived dynamically from `dataclasses.fields(S3Row)`, so all S3 fields (including the three new ones) propagate into every `S4Row` construction without a hardcoded field list. `LABEL_SCHEMA_FINGERPRINT_SHA256`/`SEMANTIC_BUILD_CONFIGURATION_SHA256` independently recomputed by this review by direct import and matched exactly. | **RESOLVED** — minimal-package evidence gap and incorrect modification inference, confirmed not an implementation defect. |
| **F3** | Major — confirmed defect | `SourceManifest` accepted and re-serialized a non-canonically-ordered `source_files` array; `RCC_SOURCE_FILE_ORDER_MISMATCH` never raised | `rcc002/s0/manifest.py:326-335`: `__post_init__` now recomputes `build_source_snapshot(self.source_files, ...)` and raises `SourceProfileError("RCC_SOURCE_FILE_ORDER_MISMATCH", ...)` if `self.source_files != snapshot.source_files`. This review independently reproduced the exact reverse-order counterexample from the prior review directly against the constructor (not via `dataclasses.replace`) and confirmed the rejection and reason code (§2.6.4). The package's own regression test (`tests/rcc002/s0/test_manifest.py:219-249`) reproduces the same scenario and passed when executed. | **CORRECTED** — confirmed by independent reproduction, not merely by re-reading the diff. |
| **F4** | Major — evidence/coverage gap | Only 1 of 4 golden `negative_cases` reason codes implemented; width overflow was a bare `ValueError`; no mechanism for `RCC_SOURCE_RECORD_INDEX_NOT_ORIGINAL` | `rcc002/s1/row_id.py` now defines `SourceRowIdError` (structured, carries `reason_code`) and `validate_source_row_id_coordinates()`, which `S1Row.__post_init__` (`rcc002/s1/schema.py:130-135`) calls on every row construction — an index/ordinal mismatch between the stored V2 `source_row_id` string and the row's own stated coordinates now raises `RCC_SOURCE_RECORD_INDEX_NOT_ORIGINAL` (`row_id.py:119-124`) or `RCC_SOURCE_FILE_ORDINAL_MISMATCH`/`RCC_SOURCE_ROW_ID_COORDINATE_MISMATCH` as appropriate; width overflow raises `RCC_SOURCE_ROW_ID_WIDTH_OVERFLOW` as a `SourceRowIdError`, not a bare `ValueError` (`row_id.py:72-76`). This review ran all four fixture-bound negative-case tests directly and in isolation (§2.6.5): all 4/4 pass, each reading `expected_error` live from the fixture. | **CORRECTED** — all four registered reason codes are now implemented, fail-closed, and directly fixture-bound; independently re-executed. |
| **F5** | Minor — evidence gap | `binance_spot_kline_timestamp_golden.v1.json` referenced by tests but absent from the package | File present at `CANDIDATE/tests/fixtures/rcc002/source/binance_spot_kline_timestamp_golden.v1.json`; full text read (6 cases spanning `DAILY`/`MONTHLY` families on both sides of the 2025-01-01 boundary). This review independently recomputed all 6 cases against `rcc002.s0.profiles.resolve_timestamp_unit`/`normalize_timestamp_pair` and obtained an exact match for every case (§2.6.4), and confirmed `tests/rcc002/s0/test_profiles.py` also exercises this fixture (`test_all_registered_golden_cases`, line 94). | **RESOLVED** — minimal-package evidence gap, confirmed not an implementation defect. |
| **F6** | Minor — test-design gap | No test asserted `INDICATOR_SCHEMA_REF` against the literal string; only self-consistency was checked | `tests/rcc002/s3/test_schema.py:99-102` (`test_indicator_schema_ref_is_exact`) now asserts `self.assertEqual(INDICATOR_SCHEMA_REF, "rcc002.stage.s3-indicators/1.0.0")` directly, independent of the imported-constant self-consistency check, and independently re-executed as passing by this review. | **CORRECTED**. |

No prior `PASS` finding was contradicted by this review; each was
independently re-confirmed (not merely carried forward), as detailed in §4
below, using the now-complete evidence.

---

## 4. New findings

| ID | Severity | File / line evidence | Summary | Impact | Required correction |
|---|---|---|---|---|---|
| **N1** | **Informational — no defect, non-blocking** | `rcc002/s0/source_identity.py:427-432` (`build_source_snapshot` sorts by raw `item.provider_relative_name`) vs. `registries/rcc002/source/source_snapshot_id_profile.v1.json:24-27` (`"source_files_order": ["normalized_provider_relative_name", "source_file_ordinal"]`) | The registry names the sort key `normalized_provider_relative_name`; the implementation sorts by the raw (non-Unicode-normalized) `provider_relative_name` string. This review verified this is **not** an exploitable discrepancy for the registered profile in scope: `provider_relative_name` values are restricted, before any sort or snapshot construction, to the ASCII-only pattern enforced by `_DAILY_PATTERN`/`_MONTHLY_PATTERN` in `rcc002/s0/profiles.py:24-35` (`[A-Z0-9]+`, digits, hyphens, fixed literal path segments only) via `parse_archive_period`, and Unicode NFC normalization (the canonicalization the codebase itself applies elsewhere, in `_canonicalize_strings`, `source_identity.py:44-59`) is the identity function on pure-ASCII strings. So for every input this profile can accept, "raw name" and "NFC-normalized name" sort identically; the registry's terminology is broader than what this implementation currently needs to satisfy. | None for the currently registered Binance Vision Spot-kline profile. Would only matter if a future provider/profile permitted non-ASCII `provider_relative_name` values without updating this sort key accordingly. | Optional, non-blocking: align the code comment/variable naming in `build_source_snapshot` to note explicitly that ASCII-only enforcement upstream makes raw and NFC-normalized ordering equivalent, so a future non-ASCII profile extension does not silently reuse this sort key without re-deriving the invariant. |

No other new finding — blocking, major, or minor — was identified. In
particular, no formula, coefficient, threshold, or scientific-value
computation in S3 (`indicators`), S4 (`signals`), S5, S6 (`gate`), or S7
(`labels`/forward-return/barrier logic) differs from `BASELINE` in any
diff reviewed; every changed production line is either additive
schema/reference wiring, a patch-version bump, or the `F3`/`F4` fail-closed
corrections above.

---

## 5. Explicit disposition of review items 1–10

| # | Item | Disposition |
|---|---|---|
| 1 | Timestamp-unit selection depends only on the registered archive-period descriptor, never on timestamp magnitude | **PASS.** `rcc002/s0/profiles.py:resolve_timestamp_unit` takes only an `ArchivePeriod` (itself derived purely from the provider-relative name, before any archive byte is read, by `parse_archive_period`); no raw timestamp value is inspected before the unit is chosen. `scan_binance_vision_archive` (`source_identity.py:169-178`) calls `parse_archive_period` → `resolve_timestamp_unit` before opening the ZIP. Independently confirmed against 4 real provider archives (§2.6.6): both 2024 archives (whose file names alone determine the period) resolved `MILLISECOND`, both 2025 archives resolved `MICROSECOND`, matching the registered `2025-01-01T00:00:00Z` boundary exactly. |
| 2 | Millisecond/microsecond conversion and remainder rules remain exact | **PASS.** `normalize_timestamp_pair` (`profiles.py:207-254`) implements the registered `%1000==0`/`%1000==999` remainder checks and `//1000` floor division exactly as `timestamp_unit_profile.v1.json` specifies; independently re-derived by this review against all 6 cases of `binance_spot_kline_timestamp_golden.v1.json` (both archive families, both sides of the unit boundary) with an exact match on every case, and cross-confirmed against the live 92,160-row provider evidence run. |
| 3 | S0 and S1 retain identical conversion and coverage semantics | **PASS.** Both `rcc002/s0/source_identity.py` and `rcc002/s1/normalize.py` import and call the identical `normalize_timestamp_pair`/`reconcile_timestamp_to_period`/`resolve_timestamp_unit` functions from `rcc002.s0.profiles`; no duplicate or divergent implementation exists in either file. Confirmed by direct read of both modules' imports and by the provider-evidence run's explicit `S0/S1 normalization parity=PASS for every archive` result, independently reproduced by this review. |
| 4 | Source Snapshot V1 ordering, preimage, checksums, coverage, and identity are exact | **PASS.** Preimage structure, canonicalization, and hash reproduced bit-for-bit against the golden fixture by this review (§2.6.4). Ordering is now enforced: `SourceManifest.__post_init__` (`manifest.py:326-335`) rejects any `source_files` tuple that is not identical to the canonically re-sorted `build_source_snapshot(...)` output, raising `RCC_SOURCE_FILE_ORDER_MISMATCH`; this review independently reproduced the prior `F3` counterexample against the raw constructor and confirmed rejection. |
| 5 | Source Manifest 1.0.0 preserves S0 ownership boundaries | **PASS.** `LegacySourceManifest` (generic one-file, caller-supplied identity; still used by the legacy `ingest_source()` path, `s0/ingest.py`) and `SourceManifest` (registered, multi-file, computed identity) remain cleanly separated — confirmed by the `s0/ingest.py` diff, which now constructs a `LegacySourceManifest` (previously it incorrectly constructed the registered `SourceManifest` type). Per-file `SourceFileIdentity` records remain the sole owners of per-archive fields; the aggregate manifest only aggregates them (`source_identity.py:74-141`). Confirmed by the executed `test_materializes_exact_schema_fields` test, whose produced payload key set equals the JSON Schema's `required` set exactly. |
| 6 | Source Row ID V2 remains collision-free across files | **PASS.** `compute_source_row_id`'s encoding, width, and negative/overflow checks independently reproduced against the golden fixture and matched exactly. Enforcement is no longer merely structural/incidental: `validate_source_row_id_coordinates` (`row_id.py:85-141`), invoked from every `S1Row.__post_init__`, fail-closed rejects any row whose stored V2 `source_row_id` does not encode its own stated `source_snapshot_id`/`source_file_ordinal`/`original_record_index`, raising the registered `RCC_SOURCE_RECORD_INDEX_NOT_ORIGINAL`/`RCC_SOURCE_FILE_ORDINAL_MISMATCH`/`RCC_SOURCE_ROW_ID_COORDINATE_MISMATCH` codes. Collision-freedom across real data was independently confirmed over all 92,160 provider-evidence rows: `source_row_id_unique_count=92160` with zero collisions within or across the 4 archives. |
| 7 | `source_file_ordinal` and `original_record_index` propagate through S7 | **PASS — now fully verifiable.** Confirmed by diff and executed tests for S1→S2→S3 (as before). For S4–S7, this review independently confirmed the dataclass inheritance chain `S4Row(S3Row)`→`S5Row(S4Row)`→`S6Row(S5Row)`→`S7Row(S6Row)` (§2.6.8) makes the fields present on every downstream row type by construction, and confirmed via `dataclasses.fields()` inspection (matching the package's own `test_source_coordinates_propagate_through_s1_to_s7`, independently re-executed) that `source_snapshot_id`, `source_row_id`, `source_file_ordinal`, `original_record_index` occupy the identical four consecutive field positions on `S1Row` through `S7Row`. |
| 8 | `indicator_schema_ref` is placed and propagated exactly | **PASS — now fully verifiable.** Field *position* on `S3Row` (`s3/schema.py:79`, immediately after `indicator_schema_version`) confirmed by direct read and by the executed `test_s3_field_order_matches_normative_contract`. The field's *value* — `INDICATOR_SCHEMA_REF = "rcc002.stage.s3-indicators/1.0.0"` (`s3/constants.py:12-14`) — is now independently, literally asserted (`F6`, resolved) and confirmed present and byte-identical between `BASELINE` and `CANDIDATE`. Propagation into S4 is enforced by an explicit equality check (`s4/compute.py:306`) in addition to inheritance; propagation into S5–S7 is guaranteed by the inheritance chain confirmed in item 7 and by the executed `test_s5_to_s7_preserves_exact_ref` test. |
| 9 | S3–S7 scientific market values otherwise remain unchanged | **PASS.** Confirmed for S3 and S4 by `diff -u` (strictly additive schema/reference wiring; no formula code touched — verified line-by-line, §2.6.7). Confirmed for S5, S6, S7: `compute.py`, `formulas.py`, `leakage.py`, `planning.py` for all three stages are **absent from `CHANGED_FILES.txt` and confirmed absent from the full recursive `diff -rq BASELINE CANDIDATE`** (§2.1) — i.e., independently proven byte-identical to `BASELINE`, not merely "not listed." Only `constants.py` in each of S4–S7 changed, and each diff is exactly the claimed patch-version bump (plus, for S7, the two dynamic `fields(S6Row)`-derived lists, which do not alter any existing computed value, only how the identity-fingerprint inputs are enumerated). |
| 10 | Deterministic S7 identities follow from the corrected input contract | **PASS — now fully verifiable.** `LABEL_SCHEMA_FINGERPRINT_SHA256` and `SEMANTIC_BUILD_CONFIGURATION_SHA256` derive their `input_fields`/`input_field_order` dynamically from `dataclasses.fields(S6Row)` (`s7/constants.py:261-264`, `292-295`), so they self-update if upstream fields change. This review independently recomputed both hashes by direct import (`rcc002.s6.schema.S6Row` is now present and confirmed byte-identical to `BASELINE`) and obtained `6fb2bcdeae2070f054fcf298693382b668ed267017f4e0f72be87615a3827bce` and `8ca946ee9725e6f767ff498c7d41362181f52457de7f5494a48a4b32b0806905` — an **exact match** to the values previously reported only in the candidate's self-report and "taken on faith" by the prior review. |

---

## 6. Final verdict

```text
FINAL VERDICT: APPROVE
```

**Rationale.** All six findings from the prior `REJECT` review are resolved:
`F1`, `F2`, and `F5` are confirmed, by this review's own independent
byte-equality checks and full recursive tree diff, to have been artifacts of
an incomplete minimal package rather than implementation defects — the
complete package now supplied here contains every file the prior review
needed and none of it differs from what the prior review's own reasoning
required. `F3` and `F4` are confirmed, by this review's own independently
constructed reproductions (not by re-reading the resolution document's
prose), to be genuinely corrected: the exact reverse-order counterexample
from the prior review is now rejected with the exact registered reason code,
and all four Golden Fixture negative cases are directly, fixture-drivenly
exercised and pass. `F6` is confirmed corrected by an executed literal
assertion.

Beyond the six prior findings, this review independently re-derived every
one of the ten review items from first principles — the golden Source
Snapshot V1 hash, both Source Row ID V2 golden cases, all six timestamp
golden cases across both archive families and both sides of the unit
boundary, both S7 identity fingerprints, and the full 627-test suite — and
obtained an exact match in every case, plus a clean, independently executed
92,160-row provider-evidence run with zero `source_row_id` collisions. The
one new observation (`N1`) is confirmed non-exploitable within the current
registered profile's ASCII-only namespace and is recorded as informational
only; it does not constitute an unverified assumption, identity ambiguity,
unit-inference risk, or silent truncation, and does not block `APPROVE`.

No repository-wide regression run or historical-artifact re-verification was
performed, consistent with `README.md`'s explicit statement that these are
deferred to the controlled-import gate; this is not treated as a missing
implementation file or an unresolved finding, per the re-review instructions.

This verdict certifies that the **corrected implementation is scientifically
consistent with the registered profiles, schemas, and Golden Fixtures
supplied in this package**. Per `README.md`, this package "does not
authorize S8," and this review does not purport to authorize S8, certify the
normative bundle, or substitute for the separate architecture re-review;
those remain governed by their own review documents and gates.
