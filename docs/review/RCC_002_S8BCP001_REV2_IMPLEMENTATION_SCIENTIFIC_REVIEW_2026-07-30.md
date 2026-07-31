# RCC-002 S8BCP-001 Revision 2 Implementation — Independent Scientific Consistency Review

## Document Control

| Field | Value |
|---|---|
| Review ID | `RCC-002-S8BCP001-REV2-IMPL-SCI-001` |
| Date | 2026-07-30 |
| Review class | Independent scientific consistency review (post-implementation) |
| Reviewed package | Compact minimal scientific review package, this directory |
| Prior artifacts referenced but not trusted uncritically | `RCC_002_S8BCP001_REV2_IMPLEMENTATION_CORRECTION_VERIFICATION_2026-07-30.md` (candidate self-report), certification decision, mechanical/identity-graph/provider-evidence review docs |
| Final verdict | **REJECT** |

---

## 1. Reviewer role and scope

This review was performed as an **independent scientific consistency
reviewer** for the S8BCP-001 Revision 2 implementation correction, per the
instructions in `SCIENTIFIC_REVIEW_PROMPT.md`. The mandate is narrow and
specific: determine whether the *implementation* (not the already-certified
normative bundle) correctly and exactly realizes ten specific properties of
the corrected source-identity, timestamp-unit, and `indicator_schema_ref`
contracts, using only the evidence supplied in this compact package.

Scope boundaries observed:

- Only this directory (`/home/benja/rcc002-reviews/2026-07-30/scientific-review`)
  was used. No external repository, no network access, no installation of
  packages, and no access to `/home/benja/projects/sniper-bot` occurred.
- No input file in `BASELINE_CHANGED/`, `CANDIDATE_CHANGED/`,
  `NORMATIVE_REFERENCE/`, `TEST_EVIDENCE/`, `CHANGED_FILES.txt`,
  `README.md`, `SCIENTIFIC_REVIEW_PROMPT.md`, or `SHA256SUMS` was modified.
  All local commands executed (`sha256sum -c`, `py_compile`, `python3 -m
  unittest`, ad-hoc reproduction scripts) were read-only against copies made
  in a private scratch directory, or non-modifying in place.
- Claims already made by prior reviews or by the candidate's own
  `IMPLEMENTATION_TEST_SUMMARY.txt` were **not** accepted at face value;
  every claim checked below was re-derived directly from the supplied
  source code, registries, schemas, and fixtures, or explicitly marked as
  unverifiable from this package.
- No implementation detail was invented. Where the package does not contain
  the evidence needed to confirm a claim, this is stated explicitly rather
  than assumed in the candidate's favor.

---

## 2. Evidence inspected

### 2.1 Governance and inventory

- `README.md`, `SCIENTIFIC_REVIEW_PROMPT.md`
- `CHANGED_FILES.txt` (34 entries; treated as the declared "complete change
  inventory")
- `SHA256SUMS` (86 entries covering this package's own files; verified with
  `sha256sum -c SHA256SUMS` — **all 86 entries PASS**, confirming the
  package was not corrupted in transit; this does **not** establish that the
  inventory is complete, only that what is present is byte-intact)

### 2.2 Normative reference material (`NORMATIVE_REFERENCE/`)

- `docs/review/RCC_002_S8_BLOCKER_CORRECTION_PROPOSAL_2026-07-30.md` (full text)
- `docs/certification/RCC_002_S8BCP001_REV2_CORRECTED_NORMATIVE_BUNDLE_CERTIFICATION_DECISION_2026-07-30.md` (full text)
- `docs/review/RCC_002_S8BCP001_REV2_MECHANICAL_VERIFICATION_2026-07-30.md` (full text)
- `docs/review/RCC_002_S8BCP001_REV2_PROVIDER_EVIDENCE_VERIFICATION_2026-07-30.md` (full text)
- `docs/review/RCC_002_S8BCP001_REV2_IDENTITY_GRAPH_2026-07-30.md` (full text)
- `registries/rcc002/source/timestamp_unit_profile.v1.json`
- `registries/rcc002/source/source_row_id_profile.v2.json`
- `registries/rcc002/source/source_snapshot_id_profile.v1.json`
- `registries/rcc002/source/source_retrieval_registry.v1.json`
- `registries/rcc002/source/source_column_profile_registry.v1.json`
- `schemas/rcc002/manifests/source-manifest/1.0.0.schema.json`
- `tests/fixtures/rcc002/source/source_identity_golden.v1.json`
- Specification documents present but only spot-checked for cross-reference
  (§6.2 JSON canonicalization in `RCC_002_REPRODUCIBILITY_AND_MANIFEST_2026-07-23.md`,
  used to validate the canonicalization implementation)

### 2.3 Baseline vs. candidate diffs (`BASELINE_CHANGED/` vs `CANDIDATE_CHANGED/`)

Full `diff -u` performed for every one of the 34 changed-file pairs listed
in `CHANGED_FILES.txt`, including all `rcc002/s0`–`s7` production files and
all `tests/rcc002` files. Full-text reads performed (not diff-only) for:
`rcc002/s0/profiles.py`, `rcc002/s0/source_identity.py`,
`rcc002/s0/manifest.py`, `rcc002/s1/normalize.py`, `rcc002/s1/row_id.py`,
`rcc002/s1/schema.py`, `rcc002/s3/schema.py`, `rcc002/s7/constants.py`,
`scripts/rcc002/verify_source_profile_implementation.py`,
`tests/rcc002/s0/test_profiles.py`, `tests/rcc002/s0/test_manifest.py`,
`tests/rcc002/s0/test_source_identity.py`, `tests/rcc002/s1/test_row_id.py`,
`tests/rcc002/test_s8bcp001_implementation_correction.py`.

### 2.4 Test evidence (`TEST_EVIDENCE/`)

- `IMPLEMENTATION_TEST_SUMMARY.txt` (candidate self-report; treated as an
  unverified claim, not evidence, except where independently reproduced)
- `PROVIDER_IMPLEMENTATION_VERIFICATION.json`

### 2.5 Independent mechanical verification performed by this review

All commands below were executed locally, read-only, against this package
or private copies of it:

1. `sha256sum -c SHA256SUMS` — PASS (86/86).
2. Reproduced the Source Snapshot V1 golden hash from
   `source_identity_golden.v1.json` using RFC 8785-equivalent canonical JSON
   (`sort_keys=True, separators=(",", ":")`, UTF-8, no NaN) — **matched**
   `expected_sha256` exactly.
3. Imported `rcc002.s1.row_id.compute_source_row_id` and reproduced both
   positive Source Row ID V2 golden cases and the width-overflow negative
   case from the same fixture — **all matched**.
4. `python3 -m py_compile` over every `*.py` file in `CANDIDATE_CHANGED/` —
   **all files syntactically valid**.
5. Copied `CANDIDATE_CHANGED/rcc002` and `CANDIDATE_CHANGED/tests` plus the
   Source Manifest JSON Schema and the Source Snapshot golden fixture into a
   scratch directory and ran, via `python3 -m unittest`:
   - `tests.rcc002.s0.test_manifest` — 23/23 PASS
   - `tests.rcc002.s0.test_source_identity` — 13/13 PASS
   - `tests.rcc002.s1.test_row_id` — 12/12 PASS
   - `tests.rcc002.s1.test_schema` — 9/9 PASS
   - `tests.rcc002.s2.test_schema` — 5/5 PASS
   - `tests.rcc002.s1.test_normalize` — **ImportError**:
     `No module named 'rcc002.s1.numeric'` (module not in package; expected,
     pre-existing dependency not part of this correction)
   - `tests.rcc002.s3.test_schema` — **ImportError**:
     `No module named 'rcc002.s3.constants'` (see Finding `F1`)
   - `import rcc002.s3.compute` directly — same `ModuleNotFoundError`
6. Constructed a reproducible counter-example against
   `rcc002.s0.manifest.SourceManifest` demonstrating that a `source_files`
   tuple in non-canonical (reverse-sorted) order is accepted and serialized
   as-is by `as_dict()` (see Finding `F3`; script and full output captured
   in this review's working transcript).
7. `grep -rn` across the entirety of `CANDIDATE_CHANGED/` for the four
   reason codes prescribed by `source_identity_golden.v1.json`'s
   `negative_cases` (`RCC_SOURCE_FILE_ORDER_MISMATCH`,
   `RCC_SOURCE_DUPLICATE_PERIOD_CONFLICT`,
   `RCC_SOURCE_RECORD_INDEX_NOT_ORIGINAL`, `RCC_SOURCE_ROW_ID_WIDTH_OVERFLOW`)
   — only `RCC_SOURCE_DUPLICATE_PERIOD_CONFLICT` is implemented.

No repository-wide regression run, no full 623/573/170-test suite run, and
no re-derivation of `LABEL_SCHEMA_FINGERPRINT_SHA256` /
`SEMANTIC_BUILD_CONFIGURATION_SHA256` were possible from this package (the
modules required to do so are absent — see §3 findings).

---

## 3. Findings

| ID | Severity | File / Line evidence | Summary | Impact | Required correction |
|---|---|---|---|---|---|
| **F1** | **Blocking** | `CANDIDATE_CHANGED/rcc002/s3/compute.py:44-49` imports `INDICATOR_SCHEMA_REF` from `rcc002.s3.constants`; `CANDIDATE_CHANGED/tests/rcc002/s3/test_schema.py:5-9`, `test_compute.py:14-18`, and `tests/rcc002/test_s8bcp001_implementation_correction.py:8` all depend on the same module. **`rcc002/s3/constants.py` does not appear in `CHANGED_FILES.txt`, `BASELINE_CHANGED/`, or `CANDIDATE_CHANGED/` anywhere.** | The module that must define the mandated literal `indicator_schema_ref` value (`rcc002.stage.s3-indicators/1.0.0`, proposal §8 item 2) is entirely absent from the package. Reproduced directly: `import rcc002.s3.compute` and `python3 -m unittest tests.rcc002.s3.test_schema` both fail with `ModuleNotFoundError: No module named 'rcc002.s3.constants'` when run against exactly the files this package supplies. | **Review item 8 cannot be verified.** The actual value assigned to `INDICATOR_SCHEMA_REF` — the single normative fact this correction exists to fix — is not present anywhere in the evidence. | Include `rcc002/s3/constants.py` in the change package (as MODIFIED or as supporting unmodified context, whichever is accurate) so the literal value can be independently confirmed. |
| **F2** | **Blocking** | `CANDIDATE_CHANGED/rcc002/s4/compute.py:53` imports `S4Row` from `rcc002.s4.schema`; `_copy_s3_values()` (line ~755) spreads every `dataclasses.fields(S3Row)` name — including the new `source_file_ordinal`, `original_record_index`, `indicator_schema_ref` — as constructor keywords into `S4Row(...)`. `CANDIDATE_CHANGED/tests/rcc002/test_s8bcp001_implementation_correction.py:32-54` (`test_source_coordinates_propagate_through_s1_to_s7`) asserts these fields exist at an exact position on `S4Row`, `S5Row`, `S6Row`, `S7Row`. **None of `rcc002/s4/schema.py`, `s5/schema.py`, `s6/schema.py`, `s7/schema.py` appear in `CHANGED_FILES.txt` or the package.** | For the `S4Row(**_copy_s3_values(source), ...)` call to type-check at all, `S4Row.__init__` must already accept these three new keyword parameters — i.e. `s4/schema.py` was necessarily modified. The same reasoning, reinforced by the cross-stage test, applies to `s5/schema.py`, `s6/schema.py`, `s7/schema.py`. None of these four files — which define the very row types review items 7–10 are about — are in the evidence package. | **Review item 7 cannot be verified for S4–S7** (field presence, exact position, and validation logic for `source_file_ordinal`/`original_record_index`/`indicator_schema_ref` on `S4Row`–`S7Row` are asserted only by a test whose subject files are missing). Item 9 ("S3–S7 scientific market values otherwise unchanged") cannot be confirmed for S5–S7 beyond the fact that `s5/compute.py`, `s6/compute.py`, `s7/compute.py` are absent from the inventory (consistent with, but not proof of, an unmodified generic-copy design). Item 10 cannot be independently recomputed (`rcc002.s6.schema.S6Row`, imported by `s7/constants.py` line 12, is unavailable). | Include `rcc002/s4/schema.py`, `s5/schema.py`, `s6/schema.py`, `s7/schema.py` in the change package. |
| **F3** | **Major — confirmed defect** | `CANDIDATE_CHANGED/rcc002/s0/manifest.py`, `SourceManifest.__post_init__` (lines ~200–260, the `build_source_snapshot(...)` recomputation-and-compare block) | **Reproduced directly (§2.5.6):** `SourceManifest` accepts a `source_files` tuple that is *not* in canonical `normalized_provider_relative_name` order (files supplied as `[2024-12-31, 2024-12-30]` instead of the required `[2024-12-30, 2024-12-31]`), provided the tuple's own `source_file_ordinal` values and the declared `source_snapshot_id`/`preimage_sha256` were computed consistently. `__post_init__` only compares the *recomputed summary identity* (`source_snapshot_id`, `preimage_sha256`, `symbol`, `interval`, coverage aggregates) against `build_source_snapshot(self.source_files, ...)`'s output — it never compares `self.source_files` (the array that becomes the literal, schema-validated `as_dict()["source_files"]` payload) against the canonically-sorted array. `as_dict()` returns `self.source_files` unchanged. | Violates the exact ordering rule in `source_snapshot_id_profile.v1.json` (`"source_files_order": ["normalized_provider_relative_name", "source_file_ordinal"]`) and the Source Manifest schema's own `$comment` ("Semantic validation enforces canonical portable-name ordering..."). A Source Manifest can be published with a `source_files` array in the wrong order while still passing all of the module's own checks and the JSON Schema's structural validation (which cannot express array ordering). Directly corresponds to `source_identity_golden.v1.json`'s `negative_cases[0]` (`noncanonical_source_file_order` → `RCC_SOURCE_FILE_ORDER_MISMATCH`), which is not raised — the string `RCC_SOURCE_FILE_ORDER_MISMATCH` does not exist anywhere in the codebase. | Add an explicit check in `SourceManifest.__post_init__` (or in `build_source_snapshot`'s validation path) that `self.source_files == snapshot.source_files` (i.e. the stored array is byte-for-byte the canonically re-derived one, not just identity-equivalent), raising a dedicated `RCC_SOURCE_FILE_ORDER_MISMATCH`-class error otherwise. Add the corresponding negative test. |
| **F4** | **Major — evidence/coverage gap** | `CANDIDATE_CHANGED/rcc002/s1/row_id.py` (`compute_source_row_id`), `CANDIDATE_CHANGED/rcc002/s1/normalize.py` (`normalize_rows`, `original_record_index` loop) vs. `NORMATIVE_REFERENCE/tests/fixtures/rcc002/source/source_identity_golden.v1.json` `negative_cases[2]` and `[3]` | Of the four `negative_cases` reason codes prescribed by the golden fixture, only `RCC_SOURCE_DUPLICATE_PERIOD_CONFLICT` is implemented and tested. `RCC_SOURCE_RECORD_INDEX_NOT_ORIGINAL` has **no implementing mechanism at all** — `original_record_index` correctness (that it reflects file position *before* sorting) is guaranteed only by the call-site structure of `normalize_rows` (index assigned via `enumerate(raw_rows)` before the later `sorted(...)` call), with no independent, testable safeguard or reason code if that invariant were ever violated. `RCC_SOURCE_ROW_ID_WIDTH_OVERFLOW` is functionally caught (`compute_source_row_id` raises on overflow) but as a bare `ValueError` with no `reason_code`, not the registered code. | §7.3 and §15.2 of the correction proposal require these as mandatory tests; §4.5 requires "positive and negative Golden fixtures" to "cover ... the registered ... unit branch". Two of four prescribed negative evidence classes are unimplemented or only incidentally satisfied. | Implement dedicated fail-closed checks for both remaining reason codes (or provide a documented, reviewed justification for relying on structural-only enforcement), and add tests iterating `fixture["negative_cases"]` directly rather than ad hoc equivalents. |
| **F5** | **Minor — evidence gap** | `CANDIDATE_CHANGED/tests/rcc002/s0/test_profiles.py:84-117` reads `tests/fixtures/rcc002/source/binance_spot_kline_timestamp_golden.v1.json` | This fixture is referenced by the candidate's own test suite but is not present anywhere in `NORMATIVE_REFERENCE/` or elsewhere in the package. The §6.4-mandated golden ms/µs conversion case table (registered daily/monthly period parsing, last pre-transition / first post-transition archive, etc.) cannot be independently reproduced by this review. | Lowered confidence on review items 1–2, partially offset by (a) direct code-level verification that `rcc002/s0/profiles.py`'s `resolve_timestamp_unit`/`normalize_timestamp_pair` match the registered `timestamp_unit_profile.v1.json` branch conditions and remainder rules exactly, and (b) independent cross-confirmation via `RCC_002_S8BCP001_REV2_PROVIDER_EVIDENCE_VERIFICATION_2026-07-30.md`, whose byte-bound archive results (checksums, record counts, first/last raw timestamps) are internally consistent with `TEST_EVIDENCE/PROVIDER_IMPLEMENTATION_VERIFICATION.json`. | Include the missing fixture file in `NORMATIVE_REFERENCE/tests/fixtures/rcc002/source/`. |
| **F6** | **Minor — test-design gap** | `CANDIDATE_CHANGED/tests/rcc002/s3/test_schema.py:99-100` (`test_indicator_schema_ref_is_exact`); `tests/rcc002/test_s8bcp001_implementation_correction.py:68-83` | No test in the package asserts `INDICATOR_SCHEMA_REF == "rcc002.stage.s3-indicators/1.0.0"` as a literal string. Existing tests only assert that a constructed row's field equals the *imported constant*, which is a self-consistency check that would pass unchanged even if the constant itself held an incorrect value. Independent of `F1` (the module being absent) — this would remain true even if `s3/constants.py` were supplied. | Weakens confidence in review item 8 even setting `F1` aside. | Add an explicit literal-value assertion, e.g. `self.assertEqual(INDICATOR_SCHEMA_REF, "rcc002.stage.s3-indicators/1.0.0")`. |

No findings were identified regarding: the timestamp-unit branch-selection
order (strictly period-before-row, confirmed in `profiles.py` and
`source_identity.py`); the millisecond/microsecond integer conversion and
remainder arithmetic (confirmed exact against the registered profile and
independently recomputed); the S1–S3 propagation of
`source_file_ordinal`/`original_record_index` (confirmed by diff and
executed tests); the S3 field-placement of `indicator_schema_ref`
immediately after `indicator_schema_version` (confirmed by an executed
test); the S4–S7 component patch-version bumps (`0.3.0→0.3.1`,
`0.4.0→0.4.1`, `0.4.0→0.4.1`, `0.3.0→0.3.1`, all matching the proposal's
table exactly); or the absence of any change to indicator/signal/regime/
gate/label formula code in every diff reviewed.

---

## 4. Explicit disposition of review items 1–10

| # | Item | Disposition |
|---|---|---|
| 1 | Timestamp units selected only from the registered archive period | **PASS.** `rcc002/s0/profiles.py:resolve_timestamp_unit` takes only an `ArchivePeriod` (itself derived purely from the provider-relative name via `parse_archive_period`, before any archive byte is read). `scan_binance_vision_archive` calls `parse_archive_period` → `resolve_timestamp_unit` before opening the ZIP. Confirmed by code reading and by executed tests (`test_transition_branches`, `test_boundary_crossing_period_rejected`). Weakened only by `F5` (fixture gap), not contradicted. |
| 2 | Millisecond/microsecond conversion and remainder rules exact | **PASS**, with the caveat in `F5`. `normalize_timestamp_pair` implements the registered `%1000==0` / `%1000==999` remainder checks and `// 1000` floor division exactly as specified in `timestamp_unit_profile.v1.json`; independently re-derived by this review and cross-confirmed against `RCC_002_S8BCP001_REV2_PROVIDER_EVIDENCE_VERIFICATION_2026-07-30.md`'s byte-bound transition table. |
| 3 | S0 and S1 use the same conversion and coverage semantics | **PASS.** Both `rcc002/s0/source_identity.py` and `rcc002/s1/normalize.py` import and call the identical `normalize_timestamp_pair`/`reconcile_timestamp_to_period` functions from `rcc002.s0.profiles`; no duplicate or divergent implementation exists in either changed file. |
| 4 | Source Snapshot V1 ordering, preimage, checksums, coverage, and identity are exact | **FAIL.** Preimage structure, canonicalization, and hash are exact (golden fixture reproduced bit-for-bit by this review). However, `F3` is a confirmed, reproduced defect: the canonical *ordering* of the stored `source_files` array is not independently enforced by `SourceManifest`, only by the (separate, always-resorting) `build_source_snapshot` path — a manifest with a non-canonically-ordered array can be constructed and serialized without error. |
| 5 | Source Manifest 1.0.0 preserves S0 ownership boundaries | **PASS, with the same caveat as item 4.** `LegacySourceManifest` (generic one-file, caller-supplied identity) and `SourceManifest` (registered, multi-file, computed identity) are cleanly separated; per-file `SourceFileIdentity` records are the sole owners of per-archive fields, and the aggregate manifest only aggregates them. Confirmed by an executed test (`test_materializes_exact_schema_fields`) that the produced payload's key set equals the JSON Schema's `required` set exactly. Ordering enforcement gap per `F3` applies here too. |
| 6 | Source Row ID V2 is collision-free and uses the original data-record index | **PASS on the encoding and collision-avoidance mechanics**; **PARTIAL on enforcement**. `compute_source_row_id`'s encoding, width, and negative/overflow checks were independently reproduced against the golden fixture and match exactly. `original_record_index` is demonstrably assigned before the later sort in `normalize_rows`. However, per `F4`, there is no independent, testable mechanism (and no `RCC_SOURCE_RECORD_INDEX_NOT_ORIGINAL` reason code) that would catch a violation of this invariant if one were ever introduced — the guarantee is structural/incidental, not enforced. |
| 7 | `source_file_ordinal` and `original_record_index` propagate through S7 | **FAIL — cannot be verified.** Confirmed by diff and executed tests for S1→S2→S3. **Unverifiable for S4, S5, S6, S7** per `F2`: the schema files that would declare these fields on `S4Row`–`S7Row` are absent from the package. |
| 8 | `indicator_schema_ref` is placed and propagated exactly | **FAIL — cannot be verified.** Field *position* on `S3Row` (immediately after `indicator_schema_version`) is confirmed by an executed test. The field's *value* cannot be confirmed at all (`F1`: `rcc002/s3/constants.py` is absent; `F6`: no test asserts the literal value even in principle). Propagation into S4 is confirmed at the code level (explicit equality checks added in `s4/compute.py`); propagation into S5–S7 is unverifiable (`F2`). |
| 9 | S3–S7 scientific market values otherwise remain unchanged | **PARTIAL.** Confirmed for S3 (`compute.py`, `schema.py` diffs contain only additive field wiring; no formula code touched) and S4 (`compute.py` diff is limited to schema-ref validation and pass-through; `formulas` import list and all signal-computation code paths are untouched in the diff). S5, S6, S7 `compute.py` are not listed as modified at all (consistent with, but not proven by this package to be, an unmodified generic pass-through design) and their `schema.py` files are entirely absent (`F2`), so this cannot be affirmatively confirmed for those three stages. |
| 10 | Recomputed deterministic S7 identities follow from the corrected input contract | **PARTIAL.** The *mechanism* is sound and well-designed: `LABEL_SCHEMA_FINGERPRINT_SHA256` and `SEMANTIC_BUILD_CONFIGURATION_SHA256` in `rcc002/s7/constants.py` now derive their `input_fields`/`input_field_order` dynamically from `dataclasses.fields(S6Row)` rather than a hardcoded list, so they self-update when upstream fields change — a robust pattern, confirmed by reading the diff. However, this review cannot independently recompute either hash (their inputs depend on `rcc002.s6.schema.S6Row`, which is not in the package per `F2`), so the specific hash values reported in `TEST_EVIDENCE/IMPLEMENTATION_TEST_SUMMARY.txt` (`6fb2bcde...`, `8ca946ee...`) are taken on faith, not independently confirmed. |

---

## 5. Verdict

```text
FINAL VERDICT: REJECT
```

**Rationale.** Every part of the implementation this review could fully
inspect and execute — the S0 archive-period/timestamp-unit machinery, the
Source Snapshot V1 preimage and hash, the Source Row ID V2 encoding, the S1
row schema and normalization ordering, the S2 pass-through, the S3 field
placement, and the S4 patch-level wiring and version bump — is precise,
internally consistent, and matches the registered profiles and the
correction proposal exactly wherever it could be checked, including two
independently reproduced golden-hash matches and 62 independently executed
unit tests (all passing).

The verdict is nonetheless `REJECT`, not `APPROVE_WITH_CONDITIONS`, because
this review identified:

1. **Two blocking evidentiary gaps (`F1`, `F2`)** that make two of the ten
   mandatory review items (7 and 8) — and parts of two more (9, 10) —
   *impossible to verify at all* from the supplied package, not merely
   inconvenient to verify. `CHANGED_FILES.txt` is explicitly described by
   `README.md` as "the complete change inventory," and this claim is
   demonstrably false: `rcc002/s3/constants.py`, `rcc002/s4/schema.py`,
   `rcc002/s5/schema.py`, `rcc002/s6/schema.py`, and `rcc002/s7/schema.py`
   are all necessarily modified (proven by direct execution —
   `ModuleNotFoundError` — and by the package's own cross-stage test
   asserting fields on schemas it does not supply) yet are absent from both
   the inventory and the package.
2. **One confirmed, reproduced implementation defect (`F3`)** directly
   contradicting the "exact" requirement of review item 4: `SourceManifest`
   accepts and re-serializes a non-canonically-ordered `source_files` array,
   which the normative registry and the golden fixture's own negative-case
   inventory require to fail closed.
3. **Incomplete conformance to the mandated Golden Fixture negative-case
   evidence (`F4`)**, itself an explicit acceptance criterion of the
   correction proposal (§4.5, §7.3, §15.1–15.2).

Per the review instructions, an unresolved blocking finding and any
unconfirmed assumption must prevent `APPROVE`. Because the defect in `F3`
and the missing-evidence findings in `F1`/`F2` are concrete, specific, and
narrowly scoped — not indicative of a wrong scientific approach — this is
recorded as `REJECT` rather than a wholesale rejection of the design;
resubmission with the five missing files, the `F3` ordering check, and the
`F4`/`F5`/`F6` test additions would very plausibly allow a future review of
the same design to reach `APPROVE`.

### Required corrections before resubmission

1. Include `rcc002/s3/constants.py`, `rcc002/s4/schema.py`,
   `rcc002/s5/schema.py`, `rcc002/s6/schema.py`, and `rcc002/s7/schema.py`
   in the change package with accurate `CHANGED_FILES.txt` entries.
2. Fix `SourceManifest` to reject a `source_files` array that is not
   byte-identical to its canonically re-sorted form (`F3`), with a
   dedicated `RCC_SOURCE_FILE_ORDER_MISMATCH`-class error and a regression
   test using the reproduction in this review.
3. Implement or explicitly justify the remaining Golden Fixture negative
   cases (`RCC_SOURCE_RECORD_INDEX_NOT_ORIGINAL`,
   `RCC_SOURCE_ROW_ID_WIDTH_OVERFLOW` reason code) (`F4`).
4. Include `tests/fixtures/rcc002/source/binance_spot_kline_timestamp_golden.v1.json`
   in `NORMATIVE_REFERENCE/` (`F5`).
5. Add an explicit literal-value assertion for `INDICATOR_SCHEMA_REF`
   (`F6`).
6. Re-run the full local (`tests/rcc002`) and repository-wide regression
   suites after the above and resubmit for independent re-review; this
   review's `PASS` findings should be re-confirmed rather than carried
   forward unchecked, since several of them are adjacent to the fields
   introduced in the now-missing files.
