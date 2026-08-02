# RCC-002 S8 Implementation Candidate Blocker Correction Proposal - Revision 8

## Document control

| Field | Value |
|---|---|
| Proposal ID | `RCC-002-S8-CAND-BCP-001-REV8` |
| Proposal date | `2026-08-02` |
| Proposal class | Correction planning and architecture only (read-only diagnosis and design; no implementation, no repair) |
| Revision | `8` (amends Revision 7 Sections 5, 6, and parts of Section 7; restates Revision 6 Section 3/Revision 7 Section 3 unchanged; does not reopen Revision 1-6 findings) |
| Repository branch | `main` |
| Required/verified HEAD | `c225306095acf36ff115d7060c1cf3fa2d34397f` |
| Required/verified `origin/main` | `c225306095acf36ff115d7060c1cf3fa2d34397f` |
| `git diff --cached` at drafting time | Empty (verified before drafting) |
| Controlling proposal | `docs/review/RCC_002_S8_IMPLEMENTATION_CANDIDATE_BLOCKER_CORRECTION_PROPOSAL_REV7_2026-08-02.md` |
| Controlling proposal SHA-256 (independently recomputed) | `7946fff01560698294e322ecea0dec30c90f5d976b7b3805ea9161e157120ff6` |
| Controlling proposal line count (independently recomputed) | `1192` |
| Controlling independent re-review | `docs/review/RCC_002_S8_IMPLEMENTATION_CANDIDATE_BLOCKER_CORRECTION_PROPOSAL_REV7_CHATGPT_INDEPENDENT_RE_REVIEW_2026-08-02.md` |
| Controlling re-review SHA-256 (independently recomputed) | `143dbf70c1e4e464399f9a52459a0cbc3e2132ce35323d00397e86dadb50ba11` |
| Controlling re-review decision | `REJECT` |
| Findings closed by this revision | `S8-CAND-BCP-REV7-B01` (BLOCKER), `S8-CAND-BCP-REV7-B02` (BLOCKER), `S8-CAND-BCP-REV7-ARCH-001` (MAJOR), `S8-CAND-BCP-REV7-ARCH-002` (MAJOR), `S8-CAND-BCP-REV7-TEST-001` (MAJOR) |
| Findings restated, not reopened, not closed by this revision | `S8-CAND-TRACK1-GATE-B01` (BLOCKER; remains open until this revision's sequence completes and is itself independently re-reviewed and certified), `S8-CAND-TRACK1-PROC-001` (process finding; disclosure and clean-session obligation only) |
| Proposal status | **Proposal only. Not approved. Not certified. Does not authorize implementation, Track 2, dataset generation, publication, or deployment.** |

### Protected-file exclusion statement

`scripts/build_rcc002_spec_bundle.py` was not read, hashed, inspected,
opened, executed, imported, copied, renamed, deleted, modified, staged,
committed, packaged, or used as evidence in the preparation of this
revision. It appears in this document only in this explicit exclusion
statement, the process-finding restatement (Section 16), and the
restrictions section (Section 17).

## 1. Purpose and scope of Revision 8

Revision 7 was independently re-reviewed and **rejected**
(`RCC-002-S8-CAND-BCP-REV7-CHATGPT-IRR-001`, `REJECT`, 2026-08-02). Section
4 of that re-review confirms Revision 7 made "substantial progress" --
one named gate command, the three-way module classification, a
separately verified gate-scope document, an isolated subprocess replay
root for S8-RR-002, a parameterized isolated root for S8-RR-003, negative
controls, and an intended arithmetic update -- but identified five
specific, concrete defects, none of which reopens Revision 6's own closed
findings (`S8-CAND-BCP-REV6-B01/B02/ARCH-001/TEST-001` remain closed by
Revision 7's architecture in substance; what Revision 7 lacked was
completeness and one arithmetic/coverage error, not a wrong architectural
direction).

**Revision 8 corrects, in place, exactly the five defects the re-review
identified**, and changes nothing else in Revision 7's architecture that
the re-review did not fault:

1. `S8-CAND-BCP-REV7-B01`: the exact 60-module partition, absent in
   Revision 7 (placeholders only), is given in full in Section 5, with no
   ellipsis anywhere in this document.
2. `S8-CAND-BCP-REV7-B02`: `CLAUDE.md`'s adoption is brought inside the
   certified Track 1 byte set (Option A, as the task's own preference and
   the re-review's Section 5.2 both invite), eliminating the
   interim-authority contradiction (Section 6).
3. `S8-CAND-BCP-REV7-ARCH-001`: the S8-RR-003 replay adapter is redesigned
   to copy and subprocess-execute the complete, byte-identical, 41-method
   certified test module -- exactly the mechanism already used for
   S8-RR-002 -- instead of spot-checking selected result fields (Section
   7).
4. `S8-CAND-BCP-REV7-ARCH-002`: the S8-RR-002 replay's stated remainder is
   corrected from the erroneous `39` to the independently re-derived
   exact `37`, with the full 37-path enumeration and pre-copy set
   assertions (Section 8).
5. `S8-CAND-BCP-REV7-TEST-001`: direct mutation tests of
   `scripts/rcc002/run_s8candbcp_gate.py` itself are added to the
   already-proposed `tests/rcc002/test_s8candbcp_gate_scope.py`, adding no
   new artifact and changing no module count (Section 9).

This revision does not itself draft, byte-finalize, create, or modify any
artifact it specifies. It remains a plan, prepared entirely read-only,
exactly as Revisions 5, 6, and 7 were.

## 2. Baseline verified before drafting

1. `git branch --show-current` returned `main`.
2. `git rev-parse HEAD` and `git rev-parse origin/main` both returned
   `c225306095acf36ff115d7060c1cf3fa2d34397f`.
3. `git diff --cached` returned empty output.
4. `sha256sum` of the Revision 7 proposal returned
   `7946fff01560698294e322ecea0dec30c90f5d976b7b3805ea9161e157120ff6`,
   matching the controlling value; its line count independently
   recomputed to `1192`.
5. `sha256sum` of the Revision 7 re-review returned
   `143dbf70c1e4e464399f9a52459a0cbc3e2132ce35323d00397e86dadb50ba11`,
   matching the controlling value.
6. `git status --short` shows exactly the same 14 lines as at Revision 7
   drafting time: `SHA256SUMS`, the two Track 1 specification
   modifications, three untracked Track 1 evidence files, `rcc002/s8/`,
   `registries/rcc002/views/`, the Dataset Manifest `1.0.2` schema, the
   `1.0.2` fixture family, `tests/rcc002/s8/`, the two Track 1 scope/
   ledger verifiers, and the two Track 1 scope/ledger mutation-test
   modules, plus the untracked protected builder. None of Revision 7's
   Section 7.1 artifacts exist on disk: Revision 7 was correctly never
   implemented, only proposed.
7. `git log --oneline -8` confirms the exact commit sequence: `c225306`
   ("Record re-review of S8 correction proposal Revision 7") ->
   `5a15b59` ("Revise S8 correction architecture with executable gate") ->
   `28cec09` ("Record re-review of S8 correction proposal Revision 6") ->
   `b5a6aa6` -> `09bf13a` -> `01eb6aa` -> `45770a8` -> `ed57983`.
8. Every certified-file hash cited in this revision was independently
   recomputed fresh against the current tree, not copied from an earlier
   revision's text:
   - `scripts/rcc002/verify_s8rr002_artifacts.py` =
     `2c67bfddc0b99a3a07497240a2e6c26dbc2dd41674ade898eb00b25ef38d9335`
   - `tests/rcc002/test_s8rr002_manifest_correction.py` =
     `2b977dc2952058ee1381723332786fcd252534c0a8de560c64af932fb46abaf4`
   - `scripts/rcc002/verify_s8rr003_normative_ledger.py` =
     `48c92bae7c8b5bd51c965fcd48917ffe0a3ee84c9dfe32bd490abab88f9b6cea`
   - `tests/rcc002/test_s8rr003_normative_ledger.py` =
     `07afd3045f60c8b1cf8109da8b2b4162c3b4d664dfb4108662d0fec005cbdbce`
   - Data Pipeline text at commit `6f0f840` =
     `0e060d30b75082b74eb5211b1d378837aa7872d86f62e5e162586e2a2cc37fad`
   - Reproducibility and Manifest text at commit `6f0f840` =
     `23fd2fc0a0338124e9bbd9d95bf6797662d1e32012cb6247763e47a47bf61cf1`
   - `docs/review/evidence/RCC_002_S8CANDBCP_REV2_NORMATIVE_LEDGER_HISTORICAL_COPY_2026-08-01.txt`
     = `469236e8459a9ad86d3434a67a81f037a699e076c6a8af8b0a887ecb60a30302`,
     byte-identical to `git show HEAD:SHA256SUMS`.
   - `docs/review/evidence/RCC_002_S8BCP001_REV2_NORMATIVE_BUNDLE_SHA256SUMS_2026-07-30.txt`
     = `a34e5139dadfdfa9d72210ac12b733b0493b00c8396f8e48680634dfb5988e43`.
   - `git diff feb0bcc HEAD` and `git diff 6f0f840 HEAD` over all four
     certified files are empty: byte-identical since certification.
9. Static method counts were independently recomputed by counting
   `    def test_` occurrences (four-space indent, direct test-class
   methods): `tests/rcc002/test_s8rr002_manifest_correction.py` = `28`;
   `tests/rcc002/test_s8rr003_normative_ledger.py` = `41`. Both match the
   re-review's own independently reproduced AST counts (Section 3.2 of
   the re-review) exactly.
10. `CLAUDE.md` was independently confirmed: tracked (`git ls-files
    CLAUDE.md`), current SHA-256
    `26d149a0c95c50d1a9c2e4e9d28eb548ddd7195576eac86b0ca64b465f829276`,
    unmodified in the working tree (`git diff --stat -- CLAUDE.md` is
    empty), absent from the current 179-entry working-tree `SHA256SUMS`
    and absent from the committed 145-entry baseline ledger at
    `feb0bcc:SHA256SUMS` (both greps return zero matches).
11. `tests/rcc002/__init__.py` and `tests/rcc002/s0/__init__.py` through
    `tests/rcc002/s8/__init__.py` all exist; `tests/__init__.py` does not
    exist (`tests/` resolves as an implicit PEP 420 namespace package,
    compatible with `tests.rcc002` being a regular subpackage nested
    inside it -- this composition is valid and requires no change).
12. `find tests/rcc002 -name "test_*.py" | wc -l` returned `57`,
    unchanged from Revision 7's drafting-time count.

No repository file was modified by any command above. No test suite was
executed as a program (the static method-count checks used `grep`, not
Python execution; the `.venv` `jsonschema` check from Revision 7's own
Section 2 is restated, not re-run, since nothing relevant changed).
`scripts/build_rcc002_spec_bundle.py` was never named as an argument to
any command.

## 3. Restated from Revision 6 and Revision 7 (unchanged, not reopened)

- **`S8-CAND-TRACK1-GATE-B01` (BLOCKER)**, restated unchanged from
  Revision 6 Section 5.1 / Revision 7 Section 3: the mandatory gate
  fails 5/908 under flat discovery because the certified S8-RR-002/
  S8-RR-003 pairs validate the live tree with no frozen input. Closed only
  once this revision's Section 14 sequence completes, the Section 5
  authoritative gate command is run and confirmed green, and this
  revision itself passes independent re-review.
- **`S8-CAND-TRACK1-PROC-001` (process finding)**, restated in full in
  Section 16, unchanged in substance since Revision 6 Section 5.2.
- Revision 6 Sections 2-5 (baseline, five-failure evidence, root-cause
  analysis) and Revision 7 Sections 3-4 (restatement and closure mapping
  for the Revision 6 re-review's four findings) are not reproduced a
  third time; nothing in them is reopened, and the re-review's Section 4
  ("Positive architecture assessment") independently confirms Revision 7
  did not regress any of them.

## 4. Closure mapping for the five Revision 7 re-review findings

| Finding | Severity | Revision 7 gap | Revision 8 closure section |
|---|---|---|---|
| `S8-CAND-BCP-REV7-B01` | BLOCKER | Section 5.4 contained ellipsis placeholders (`[ ...56 entries... ]`) instead of the exact 60-module list; two-implementations-same-count risk. | Section 5 (full 60-entry enumeration, path-to-dotted-module rule, order/uniqueness/disjointness/union proofs) |
| `S8-CAND-BCP-REV7-B02` | BLOCKER | `CLAUDE.md`'s required change was placed after certification, outside the certified byte set, creating a self-contradictory "interim authority" claim. | Section 6 (Option A: `CLAUDE.md` inside Track 1, byte-finalized pre-certification, no post-certification mutation) |
| `S8-CAND-BCP-REV7-ARCH-001` | MAJOR | The S8-RR-003 adapter checked selected `run_verification()` result fields instead of executing all 41 certified test methods; dropped the `ResourceWarning` regression and the scope/ledger mutation battery. | Section 7 (complete 41-method test module copied and subprocess-executed against an isolated historical root, mirroring S8-RR-002) |
| `S8-CAND-BCP-REV7-ARCH-002` | MAJOR | Stated remainder of `39` files contradicted the exact set arithmetic (`41 - 4 = 37`). | Section 8 (corrected `37`-path enumeration, pre-copy set assertions, four new arithmetic-mutation cases) |
| `S8-CAND-BCP-REV7-TEST-001` | MAJOR | No direct test exercised `run_s8candbcp_gate.py`'s own behavior (ordering, exactly-once loading, audit-only exclusion, failure propagation). | Section 9 (seven runner-behavior cases added to the existing `test_s8candbcp_gate_scope.py`, no new artifact) |

## 5. Exact 60-module gate partition (closes `S8-CAND-BCP-REV7-B01`)

### 5.1 Path-to-dotted-module transformation

For a repository-relative path `p` ending in `.py`, the dotted module
name is `p` with the trailing `.py` removed and every `/` replaced by
`.`. Example: `tests/rcc002/s0/test_ingest.py` ->
`tests.rcc002.s0.test_ingest`. This transformation is valid for every
path below because `tests/rcc002/__init__.py` and
`tests/rcc002/s0/__init__.py` through `tests/rcc002/s8/__init__.py` all
exist (independently confirmed, Section 2 item 11); `tests/` itself has
no `__init__.py` and resolves as an implicit PEP 420 namespace package,
which is compatible with `tests.rcc002` being a regular subpackage
nested inside it. `scripts/rcc002/run_s8candbcp_gate.py` inserts the
repository root at `sys.path[0]` if not already present before calling
`unittest.defaultTestLoader.loadTestsFromName` on any of these dotted
names, exactly as invoking `python -m unittest <dotted name>` from the
repository root already makes `tests` importable today.

### 5.2 Exact `current_state_modules` (56 entries, `LC_ALL=C` order)

 1. `tests/rcc002/s0/test_ingest.py` -> `tests.rcc002.s0.test_ingest`
 2. `tests/rcc002/s0/test_integrity.py` -> `tests.rcc002.s0.test_integrity`
 3. `tests/rcc002/s0/test_manifest.py` -> `tests.rcc002.s0.test_manifest`
 4. `tests/rcc002/s0/test_profiles.py` -> `tests.rcc002.s0.test_profiles`
 5. `tests/rcc002/s0/test_source_identity.py` -> `tests.rcc002.s0.test_source_identity`
 6. `tests/rcc002/s1/test_normalize.py` -> `tests.rcc002.s1.test_normalize`
 7. `tests/rcc002/s1/test_numeric.py` -> `tests.rcc002.s1.test_numeric`
 8. `tests/rcc002/s1/test_row_id.py` -> `tests.rcc002.s1.test_row_id`
 9. `tests/rcc002/s1/test_schema.py` -> `tests.rcc002.s1.test_schema`
10. `tests/rcc002/s1/test_time.py` -> `tests.rcc002.s1.test_time`
11. `tests/rcc002/s2/test_anomalies.py` -> `tests.rcc002.s2.test_anomalies`
12. `tests/rcc002/s2/test_duplicates.py` -> `tests.rcc002.s2.test_duplicates`
13. `tests/rcc002/s2/test_invariants.py` -> `tests.rcc002.s2.test_invariants`
14. `tests/rcc002/s2/test_schema.py` -> `tests.rcc002.s2.test_schema`
15. `tests/rcc002/s2/test_segment.py` -> `tests.rcc002.s2.test_segment`
16. `tests/rcc002/s2/test_validate.py` -> `tests.rcc002.s2.test_validate`
17. `tests/rcc002/s3/test_compute.py` -> `tests.rcc002.s3.test_compute`
18. `tests/rcc002/s3/test_formulas.py` -> `tests.rcc002.s3.test_formulas`
19. `tests/rcc002/s3/test_golden_fixtures.py` -> `tests.rcc002.s3.test_golden_fixtures`
20. `tests/rcc002/s3/test_schema.py` -> `tests.rcc002.s3.test_schema`
21. `tests/rcc002/s3/test_segment.py` -> `tests.rcc002.s3.test_segment`
22. `tests/rcc002/s3/test_state.py` -> `tests.rcc002.s3.test_state`
23. `tests/rcc002/s4/test_compute.py` -> `tests.rcc002.s4.test_compute`
24. `tests/rcc002/s5/test_compute.py` -> `tests.rcc002.s5.test_compute`
25. `tests/rcc002/s5/test_formulas.py` -> `tests.rcc002.s5.test_formulas`
26. `tests/rcc002/s5/test_golden_fixtures.py` -> `tests.rcc002.s5.test_golden_fixtures`
27. `tests/rcc002/s5/test_schema.py` -> `tests.rcc002.s5.test_schema`
28. `tests/rcc002/s5/test_state.py` -> `tests.rcc002.s5.test_state`
29. `tests/rcc002/s6/test_compute.py` -> `tests.rcc002.s6.test_compute`
30. `tests/rcc002/s6/test_formulas.py` -> `tests.rcc002.s6.test_formulas`
31. `tests/rcc002/s6/test_golden_fixtures.py` -> `tests.rcc002.s6.test_golden_fixtures`
32. `tests/rcc002/s6/test_reason_codes.py` -> `tests.rcc002.s6.test_reason_codes`
33. `tests/rcc002/s6/test_schema.py` -> `tests.rcc002.s6.test_schema`
34. `tests/rcc002/s7/test_compute.py` -> `tests.rcc002.s7.test_compute`
35. `tests/rcc002/s7/test_formulas.py` -> `tests.rcc002.s7.test_formulas`
36. `tests/rcc002/s7/test_golden_fixtures.py` -> `tests.rcc002.s7.test_golden_fixtures`
37. `tests/rcc002/s7/test_planning.py` -> `tests.rcc002.s7.test_planning`
38. `tests/rcc002/s7/test_reason_codes.py` -> `tests.rcc002.s7.test_reason_codes`
39. `tests/rcc002/s7/test_schema.py` -> `tests.rcc002.s7.test_schema`
40. `tests/rcc002/s8/test_artifact_class.py` -> `tests.rcc002.s8.test_artifact_class`
41. `tests/rcc002/s8/test_canonical.py` -> `tests.rcc002.s8.test_canonical`
42. `tests/rcc002/s8/test_field_registry.py` -> `tests.rcc002.s8.test_field_registry`
43. `tests/rcc002/s8/test_identity.py` -> `tests.rcc002.s8.test_identity`
44. `tests/rcc002/s8/test_manifests.py` -> `tests.rcc002.s8.test_manifests`
45. `tests/rcc002/s8/test_projection.py` -> `tests.rcc002.s8.test_projection`
46. `tests/rcc002/s8/test_publication.py` -> `tests.rcc002.s8.test_publication`
47. `tests/rcc002/s8/test_reconciliation.py` -> `tests.rcc002.s8.test_reconciliation`
48. `tests/rcc002/s8/test_states.py` -> `tests.rcc002.s8.test_states`
49. `tests/rcc002/s8/test_validation.py` -> `tests.rcc002.s8.test_validation`
50. `tests/rcc002/s8/test_views.py` -> `tests.rcc002.s8.test_views`
51. `tests/rcc002/test_constants.py` -> `tests.rcc002.test_constants`
52. `tests/rcc002/test_reason_codes.py` -> `tests.rcc002.test_reason_codes`
53. `tests/rcc002/test_s8bcp001_implementation_correction.py` -> `tests.rcc002.test_s8bcp001_implementation_correction`
54. `tests/rcc002/test_s8candbcp_gate_scope.py` -> `tests.rcc002.test_s8candbcp_gate_scope`
55. `tests/rcc002/test_s8candbcp_rev2_normative_ledger.py` -> `tests.rcc002.test_s8candbcp_rev2_normative_ledger`
56. `tests/rcc002/test_s8candbcp_rev2_track1_normative_scope.py` -> `tests.rcc002.test_s8candbcp_rev2_track1_normative_scope`

### 5.3 Exact `historical_replay_adapter_modules` (2 entries)

1. `tests/rcc002/test_s8rr002_manifest_correction_historical_replay.py` -> `tests.rcc002.test_s8rr002_manifest_correction_historical_replay`
2. `tests/rcc002/test_s8rr003_normative_ledger_historical_replay.py` -> `tests.rcc002.test_s8rr003_normative_ledger_historical_replay`

### 5.4 Exact `historical_audit_only_modules` (2 entries)

1. `tests/rcc002/test_s8rr002_manifest_correction.py` -> `tests.rcc002.test_s8rr002_manifest_correction`
2. `tests/rcc002/test_s8rr003_normative_ledger.py` -> `tests.rcc002.test_s8rr003_normative_ledger`

### 5.5 Mechanical proofs

- **Lexical order**: each of the three lists above was produced by
  `sorted()` over the exact repository-relative path strings (Python's
  default string ordering is by Unicode code point, which is byte-order
  equivalent to `LC_ALL=C` for the pure-ASCII paths used throughout this
  repository); each list is independently confirmed equal to its own
  sorted form.
- **Uniqueness**: `len(list) == len(set(list))` holds for each of the
  three lists individually (`56`, `2`, `2`).
- **Category disjointness**: the pairwise intersections
  `current_state & historical_replay_adapter`,
  `current_state & historical_audit_only`, and
  `historical_replay_adapter & historical_audit_only` are each
  independently confirmed empty (set intersection, in the Python
  operator sense).
- **Exact union**: `current_state | historical_replay_adapter |
  historical_audit_only` (set union) has exactly `56 + 2 + 2 = 60`
  members (no overlap to subtract, per disjointness above).
- **Absence of unknown/missing modules**: `find tests/rcc002 -name
  "test_*.py"` independently enumerates `57` modules today (Section 2,
  item 12); adding the `3` new modules this correction family introduces
  (`test_s8candbcp_gate_scope.py`,
  `test_s8rr002_manifest_correction_historical_replay.py`,
  `test_s8rr003_normative_ledger_historical_replay.py`) yields exactly
  `60`, matching the union above member-for-member: every one of the `57`
  existing modules appears in exactly one of Sections 5.2-5.4 (the `55`
  existing modules other than the two certified predecessor tests appear
  in Section 5.2; the two certified predecessor tests appear in Section
  5.4), and every one of the `3` new modules appears in exactly one of
  Sections 5.2-5.3.

### 5.6 Independent hardcoding across four artifacts (no imported authority)

The exact three-category list above (Sections 5.2-5.4) is the single
canonical content. It is retyped, independently, into four separate
artifacts -- none derives its own copy by importing another artifact's
module-level object:

1. **`docs/review/evidence/RCC_002_S8CANDBCP_GATE_SCOPE_V1.json`** --
   the three lists as JSON string arrays (a data file; no code, no
   import).
2. **`scripts/rcc002/verify_s8candbcp_gate_scope.py`** -- the three lists
   as Python tuple literals (`EXPECTED_CURRENT_STATE_MODULES`,
   `EXPECTED_HISTORICAL_REPLAY_ADAPTER_MODULES`,
   `EXPECTED_HISTORICAL_AUDIT_ONLY_MODULES`), typed directly into the
   module, not read from the JSON manifest to define themselves (the
   JSON manifest is read only to *compare against* these already-defined
   literals, exactly as `verify_s8candbcp_rev2_track1_normative_scope.py`
   already does for the Track 1 scope contract).
3. **`scripts/rcc002/run_s8candbcp_gate.py`** -- hardcodes its own,
   independently typed integer constants
   (`EXPECTED_TOTAL_MODULES = 60`, `EXPECTED_CURRENT_STATE_COUNT = 56`,
   `EXPECTED_HISTORICAL_REPLAY_ADAPTER_COUNT = 2`,
   `EXPECTED_HISTORICAL_AUDIT_ONLY_COUNT = 2`). Full path-list
   duplication a third time was considered and rejected as
   disproportionate churn risk (three 56-entry lists to keep in sync is
   itself an error surface); instead, the runner calls
   `verify_s8candbcp_gate_scope`'s full validation (which independently
   checks the JSON manifest against its own hardcoded lists and against
   the actual `tests/rcc002/` tree, per item 2) and additionally asserts
   the *counts* of the returned, already-validated categories equal its
   own hardcoded integers before loading anything -- a second,
   independent check on the same fact, using differently-typed literals,
   not a second import of the same list object.
4. **`tests/rcc002/test_s8candbcp_gate_scope.py`** -- holds its own,
   separately typed reference copy of the three lists (used only to
   construct known-good and known-bad fixtures for its own test methods;
   Section 9.1, case 13, below), distinct from reading
   `verifier.EXPECTED_*` when the test is specifically exercising that
   verifier's own internals (Section 9.1, cases 1-12), exactly as the
   existing certified-family precedent
   (`test_s8candbcp_rev2_track1_normative_scope.py`) already reads
   `verifier.EXPECTED_ENTRIES` only when testing that specific verifier's
   own function, never to define a mutation's *expected outcome*.

This is "hardcode or compare against the same explicit policy," per the
re-review's required disposition, applied proportionately: full-list
duplication where the artifact's job is literally to hold the list
(JSON manifest, verifier, mutation-test fixture), and independent
count-level cross-checks where full duplication would itself become an
unmaintainable fourth copy (the runner). Section 9.1 case 13 adds a
cross-copy consistency mutation test proving that if any of the four
independently-typed representations ever silently drifted from the
others, at least one pairwise comparison would fail -- the actual risk
"importing one another's authority" would otherwise create.

## 6. `CLAUDE.md` adoption architecture (closes `S8-CAND-BCP-REV7-B02`)

**Option A is selected**: `CLAUDE.md` is included directly in Track 1,
byte-finalized before verification, review, and certification, exactly
as the task instruction prefers and as the re-review's Section 5.2
Option A specifies.

### 6.1 Exact insertion

`CLAUDE.md` at HEAD `c225306` is unmodified (Section 2, item 10) and its
`## Commands` section's fenced block ends, at line 63, with

```text
# Run the run_engine dry-run loop directly (synthetic price stream, Ctrl+C to stop)
python -m run_engine.main
```

immediately followed by the closing fence at line 64. The exact
Track 1 correction inserts the following text between line 63 and line
64 (a blank line, then two new named command blocks, matching the
existing file's own spacing convention exactly):

```text

# RCC-002 S8 correction-family mandatory gate (authoritative for this
# family; supersedes ad hoc tests/rcc002 flat discovery below)
PYTHONDONTWRITEBYTECODE=1 python3 scripts/rcc002/run_s8candbcp_gate.py

# tests/rcc002 flat discovery -- ad hoc / historical-audit only for the
# RCC-002 S8 correction family, NOT the authoritative gate (see command
# above); expected to remain red after any authorized Track 1 DP/RM/
# ledger advancement, by design, not as a regression
python -m unittest discover -s tests/rcc002 -p "test_*.py"
```

No other line of `CLAUDE.md` is touched. This is the complete, exact
specification of `CLAUDE.md`'s Track 1 successor content; nothing about
it is left to a later, unstated choice.

### 6.2 Track 1 inclusion

`CLAUDE.md` is added to the exact Track 1 inventory (Section 10) as
`MODIFIED` -- it is a tracked, committed file at HEAD `c225306` whose
content this correction changes, exactly like `SHA256SUMS`, the Data
Pipeline specification, and the Reproducibility and Manifest
specification. It is added to
`docs/review/evidence/RCC_002_S8CANDBCP_REV2_TRACK1_NORMATIVE_SCOPE_V1.json`
and to `scripts/rcc002/verify_s8candbcp_rev2_track1_normative_scope.py`'s
`EXPECTED_ENTRIES` (Section 10, item 1; sorts first in `LC_ALL=C` order,
ahead of `SHA256SUMS`, because uppercase `C` (`0x43`) precedes uppercase
`S` (`0x53`)).

### 6.3 Ledger inclusion, without conflating repository classification and ledger novelty

`CLAUDE.md` is `MODIFIED` in the Track 1 (repository-tracked-file) sense,
but it is a **new** entry in the ledger sense: it is absent from both the
145-entry committed baseline ledger and the current 179-entry working-tree
ledger (Section 2, item 10). The ledger's `added`/`replaced` distinction
tracks ledger membership, not git-tracked-file status; `CLAUDE.md` is
therefore counted among the ledger's `added` entries (Section 11), not
its `replaced` entries, even though it is simultaneously `MODIFIED` in
the Track 1 file-classification sense. Conflating these two, different
classification axes is exactly the error `S8-CAND-BCP-REV6-B02`
identified and this document does not repeat it.

### 6.4 Byte-finalization ordering (no post-certification mutation)

`CLAUDE.md`'s exact successor text (Section 6.1) depends only on the
fixed command string and path `scripts/rcc002/run_s8candbcp_gate.py`
(Section 5), which this document already fixes; it has no dependency on
that file's actual byte content. `CLAUDE.md` is therefore byte-finalized
in Section 14 alongside the other governance artifacts, strictly before
the successor ledger is computed (Section 14, step 9) and strictly
before verification, review, or certification (Section 14, steps 10-13).
Once byte-finalized, `CLAUDE.md` is never edited again by any later step
in this correction cycle, exactly like every other Track 1 artifact
(Revision 5 Section 6.6's governing rule, restated and applied here
without exception).

### 6.5 Elimination of the interim-authority contradiction

Revision 7 Section 5.2 called flat discovery "not the authoritative
gate" while Section 5.9 deferred the actual `CLAUDE.md` change to "once
this architecture is certified" -- a period during which nothing
written down anywhere was the authoritative gate in a way any file on
disk reflected. **There is no such interim period under this revision.**
`CLAUDE.md`'s new text becomes part of the committed repository at
exactly the same commit that records Track 1 certification (Section 14,
step 13: "committing the already-byte-finalized ledger" necessarily
commits every artifact the ledger indexes, including `CLAUDE.md`, since
its hash is one of the `188` successor entries, Section 11). Before that
commit, this document (like Revision 5's DP/RM version-bump description
and Revision 7's frozen-copy descriptions before them) is a proposal
describing future certified text, not a claim of present authority,
interim or otherwise.

### 6.6 Prohibition of post-certification repository mutation

No step in Section 14 edits `CLAUDE.md`, or any other Track 1 artifact,
after its own byte-finalization point or after certification (Section
14, steps 12-13). If a future, separate need arises to further revise
`CLAUDE.md`'s `## Commands` section, that is a new, later, independently
proposed and reviewed correction or documentation cycle -- never a
retroactive edit folded backward into this certification.

### 6.7 Recomputed counts (mechanically derived, not copied)

Adding exactly one file (`CLAUDE.md`) as `MODIFIED`, and no other path,
to Revision 7's independently-verified 45-entry, 187-entry state:

```text
Track 1 total:    45 + 1               = 46   (4 modified, 42 new)
Successor ledger: 187 + 1 (CLAUDE.md added, not a baseline path) = 188
                  = 145 baseline + 43 added - 0 removed
                  (43 = 42 Revision 7 additions + 1 CLAUDE.md addition)
                  (2 replaced -- DP, RM -- unchanged, count-neutral)
```

This independently reproduces the task's stated expected result (`46 =
4 + 42`; `188 = 145 + 43 - 0`, `2` replacements count-neutral) by exact
set derivation (Section 10, Section 11), not by copying the stated
figures; no other path changes, so no further correction is required.

## 7. S8-RR-003 historical replay, redesigned (closes `S8-CAND-BCP-REV7-ARCH-001`)

**The prior design (Revision 7 Section 6.3) is withdrawn in full** and
replaced with the mechanism below, which mirrors S8-RR-002's isolated-
root-plus-subprocess architecture exactly, so that all `41` certified
test methods -- including `ResourceHandlingRegression.test_no_resource_warning_on_successful_run`
and the complete `ScopeCategoryMutations` /
`UnsafePathMutations` / `LedgerStructureMutations` / `FilesystemMutations`
/ `ScopeMetadataContractMutations` batteries -- genuinely execute, rather
than being spot-checked through selected `run_verification()` result
fields.

New file, exact path (unchanged from Revision 7):
`tests/rcc002/test_s8rr003_normative_ledger_historical_replay.py`.

### 7.1 Exact construction

1. Create `tmp = tempfile.mkdtemp(prefix="rcc002_s8rr003_replay_")`
   outside the repository.
2. Copy, byte-for-byte, the live, certified, unmodified
   `scripts/rcc002/verify_s8rr003_normative_ledger.py` to
   `tmp/scripts/rcc002/verify_s8rr003_normative_ledger.py` and
   `tests/rcc002/test_s8rr003_normative_ledger.py` to
   `tmp/tests/rcc002/test_s8rr003_normative_ledger.py`. Before each copy,
   hash the source and require it equal
   `48c92bae7c8b5bd51c965fcd48917ffe0a3ee84c9dfe32bd490abab88f9b6cea` and
   `07afd3045f60c8b1cf8109da8b2b4162c3b4d664dfb4108662d0fec005cbdbce`
   respectively (Section 2, item 8); fail before copying on any mismatch.
3. **Static coverage assertion, before any execution**: parse the
   just-copied test-module bytes with Python's `ast` module and count
   `FunctionDef` nodes named `test_*` across every class in the module;
   assert the count equals `41` exactly. This is the mechanism that
   satisfies "a negative control proving that omission of any certified
   test method is detected by the gate policy": if a future variant of
   this file ever held fewer methods, this assertion fails closed before
   the subprocess is even started, independent of whether the reduced
   suite would otherwise still report `OK`.
4. Reconstruct `tmp/SHA256SUMS` as the certified `145`-entry ledger:
   copy `docs/review/evidence/RCC_002_S8CANDBCP_REV2_NORMATIVE_LEDGER_HISTORICAL_COPY_2026-08-01.txt`
   verbatim, re-hashed against `469236e8459a9ad86d3434a67a81f037a699e076c6a8af8b0a887ecb60a30302`
   immediately before the copy.
5. Copy `docs/review/evidence/RCC_002_S8RR003_NORMATIVE_LEDGER_SCOPE_V1.json`
   (live, tracked, unmodified since `feb0bcc`) to
   `tmp/docs/review/evidence/RCC_002_S8RR003_NORMATIVE_LEDGER_SCOPE_V1.json`,
   re-hashed against the digest recorded for that path in the step-4
   ledger before the copy.
6. Copy `docs/review/evidence/RCC_002_S8BCP001_REV2_NORMATIVE_BUNDLE_SHA256SUMS_2026-07-30.txt`
   (the `110`-entry historical-evidence bundle) to the identical relative
   path under `tmp/`, re-hashed against
   `a34e5139dadfdfa9d72210ac12b733b0493b00c8396f8e48680634dfb5988e43`
   before the copy.
7. For each of the other `143` paths declared in `CURRENT_LEDGER_PATHS`
   (the `145`-entry declared target set minus Data Pipeline and
   Reproducibility and Manifest, which already includes the scope
   manifest and the `110`-entry bundle handled explicitly in steps 5-6
   above): read the live working-tree bytes, hash each, require the
   digest equal the value recorded for that exact path in the step-4
   ledger, and fail before copying on any mismatch. Write verified bytes
   to the identical relative path under `tmp/`.
8. Write the frozen Data Pipeline and Reproducibility and Manifest copies
   (sourced from commit `6f0f840`, Section 2 item 8) to
   `tmp/docs/specifications/RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md`
   and
   `tmp/docs/specifications/RCC_002_REPRODUCIBILITY_AND_MANIFEST_2026-07-23.md`,
   each re-hashed against its Section 2 item 8 literal before the write.
9. Invoke `subprocess.run([sys.executable, "tests/rcc002/test_s8rr003_normative_ledger.py"],
   cwd=tmp, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
   capture_output=True)`. Because the copied test module's own
   `REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))`
   now resolves to `tmp`, every hardcoded read in both the copied test
   module and the copied verifier module targets the isolated root, not
   the live repository.
10. **Positive control**: assert the subprocess exit code is `0` and its
    captured output contains `Ran 41 tests` followed by `OK` -- proving
    all `41` certified methods, not a subset, executed and passed against
    frozen history, including the `ResourceWarning`-as-error regression
    and the complete scope/ledger mutation battery.
11. **Negative control**: repeat steps 1-9 with the live, post-Track-1
    working-tree `SHA256SUMS` (`179` entries at current drafting time)
    substituted for the step-4 file; assert the subprocess exits
    non-zero and its output contains `current_ledger_count_mismatch` --
    reproducing, deliberately, the exact failure Revision 6 Section 3
    diagnosed against the live tree, proving the adapter is genuinely
    pinned to history.
12. Delete `tmp` (`shutil.rmtree`, in a `finally`/`addCleanup` block)
    regardless of outcome. No file under `tmp` is ever written back into
    the repository; no `__pycache__` is created outside `tmp` (the
    subprocess environment sets `PYTHONDONTWRITEBYTECODE=1`).
13. `scripts/build_rcc002_spec_bundle.py` is never named, read, copied,
    or referenced anywhere in this adapter.

### 7.2 Correction of the end-to-end-equivalence claim

Revision 7 Section 6.4 claimed both adapters "reproduce every original
certified assertion end-to-end," which the re-review correctly found
false for the S8-RR-003 side (Section 5.3 of the re-review). Under this
redesign, the claim is true for both adapters because both now execute
the complete, unmodified, byte-identical original test module as a
subprocess against an isolated historical root: S8-RR-002's `28` methods
(Revision 7 Section 6.2, unchanged, restated) and S8-RR-003's `41`
methods (Section 7.1 above). Neither adapter reimplements, subsets, or
selectively checks certified assertions; each runs the certified file
itself.

## 8. S8-RR-002 replay arithmetic, corrected (closes `S8-CAND-BCP-REV7-ARCH-002`)

Revision 7 Section 6.2, step 4 stated "the remaining `39` files"; this
was an arithmetic error. **Independently re-derived, mechanically, from
the two certified category lists themselves:**

```text
immutable_reference_inputs (from verify_s8rr002_artifacts.py) = 11 paths
candidate_outputs          (from verify_s8rr002_artifacts.py) = 30 paths
category overlap  = immutable_reference_inputs & candidate_outputs = {} (0)
scope union       = immutable_reference_inputs | candidate_outputs   = 41 paths
separately handled (special) paths, all confirmed members of the union:
  - docs/specifications/RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md   (in immutable_reference_inputs)
  - docs/specifications/RCC_002_REPRODUCIBILITY_AND_MANIFEST_2026-07-23.md  (in candidate_outputs)
  - scripts/rcc002/verify_s8rr002_artifacts.py                              (in candidate_outputs)
  - tests/rcc002/test_s8rr002_manifest_correction.py                        (in candidate_outputs)
remaining paths = scope union - special paths = 41 - 4 = 37
```

`37`, not `39`, is the exact, correct remainder. The adapter must prove
every line of this arithmetic mechanically, in code, before copying any
file -- not merely assert the final number.

### 8.1 Exact 37-path remainder (`LC_ALL=C` order)

 1. `docs/review/RCC_002_S8RR002_BLOCKER_CORRECTION_PROPOSAL_REV2_2026-07-31.md`
 2. `docs/review/evidence/RCC_002_S8RR002_CORRECTION_VERIFIER_SCOPE_V1.json`
 3. `docs/specifications/RCC_002_DATA_VALIDATION_2026-07-23.md`
 4. `docs/specifications/RCC_002_INDICATOR_SPECIFICATION_2026-07-23.md`
 5. `docs/specifications/RCC_002_LABEL_AND_FORWARD_RETURN_SPECIFICATION_2026-07-23.md`
 6. `docs/specifications/RCC_002_REGIME_AND_GATE_SPECIFICATION_2026-07-23.md`
 7. `docs/specifications/RCC_002_SIGNAL_TRANSFORMATION_2026-07-23.md`
 8. `requirements-rcc002-review.txt`
 9. `schemas/rcc002/manifests/dataset-manifest/1.0.0.schema.json`
10. `schemas/rcc002/manifests/dataset-manifest/1.0.1.schema.json`
11. `schemas/rcc002/manifests/stage-manifest/1.0.0.schema.json`
12. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.0/complete-valid.json`
13. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.0/minimal-valid.json`
14. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/complete-valid.json`
15. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/minimal-valid.json`
16. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/negative/CASE_LEDGER.json`
17. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/negative/absolute-path.json`
18. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/negative/duplicate-specification.json`
19. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/negative/duplicate-view.json`
20. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/negative/extra-property.json`
21. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/negative/invalid-id.json`
22. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/negative/invalid-timestamp.json`
23. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/negative/missing-required-field.json`
24. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/negative/missing-specification.json`
25. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/negative/missing-view.json`
26. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/negative/path-traversal.json`
27. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/negative/reordered-specification.json`
28. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/negative/reordered-view.json`
29. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/negative/secret-like-field.json`
30. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/negative/secret-like-value.json`
31. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/negative/stale-specification-version.json`
32. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/negative/unknown-specification.json`
33. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/negative/unknown-view.json`
34. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/negative/wrong-schema-identity.json`
35. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/negative/wrong-schema-version.json`
36. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/negative/wrong-type-nullability.json`
37. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/negative/wrong-view-allowlist-hash.json`

Revision 7 Section 6.2 step 4's construction procedure is otherwise
unchanged: each of these `37` files is read from the live working tree,
hash-verified against either a literal already hardcoded in the
certified verifier (the six `NON_SELF_SPECIFICATIONS` hashes, the four
`EXPECTED_IMMUTABLE_HASHES` entries) or the digest recorded for that path
in the certified `145`-entry root ledger, and copied into the isolated
root only after that check passes.

### 8.2 Exact pre-copy set assertions (required, before any file is copied)

The adapter must execute, in this order, before copying any byte:

1. `assert len(immutable_reference_inputs) == 11`
2. `assert len(candidate_outputs) == 30`
3. `assert set(immutable_reference_inputs) & set(candidate_outputs) == set()`
4. `union = set(immutable_reference_inputs) | set(candidate_outputs);
   assert len(union) == 41`
5. `special = {DP_PATH, RM_PATH, VERIFIER_PATH, TEST_PATH}; assert
   special <= union`
6. `remainder = union - special; assert len(remainder) == 37`

Any assertion failure aborts the adapter before any read or copy of file
bytes occurs, matching the certified verifiers' own fail-closed idiom.

### 8.3 Required mutation additions (missing/extra/overlap/special-path)

Four new test methods in
`tests/rcc002/test_s8rr002_manifest_correction_historical_replay.py`,
each operating on an in-memory mutated copy of the two certified category
tuples and asserting the Section 8.2 validation helper raises:

1. **Missing path**: remove one entry from a copy of
   `immutable_reference_inputs`; assert the union-size assertion (Section
   8.2, item 4) fails (`40 != 41`).
2. **Extra/undeclared path**: append a fabricated path (for example
   `docs/specifications/RCC_002_NONEXISTENT_SPECIFICATION.md`) to a copy
   of `candidate_outputs`; assert the remainder-size assertion (Section
   8.2, item 6) fails (`38 != 37`).
3. **Overlap**: add one real `candidate_outputs` entry to a copy of
   `immutable_reference_inputs`; assert the disjointness assertion
   (Section 8.2, item 3) fails (non-empty intersection).
4. **Special path absent**: remove the Data Pipeline path from a copy of
   `immutable_reference_inputs`; assert the subset assertion (Section
   8.2, item 5) fails (`special` is no longer `<=` the mutated union).

## 9. Direct gate-runner mutation tests (closes `S8-CAND-BCP-REV7-TEST-001`)

Per the task's stated preference, these are added to the already-proposed
`tests/rcc002/test_s8candbcp_gate_scope.py`; **no new artifact is
introduced and the `60`-module partition (Section 5) is unchanged.**

### 9.1 Required internal structure of `scripts/rcc002/run_s8candbcp_gate.py`

To make the properties below independently testable without running the
real `58`-module suite in every unit test, the runner exposes three
composable functions (still one file, one path, no new module):

- `verify_scope(repo_root)` -- invokes
  `verify_s8candbcp_gate_scope`'s full validation (manifest-vs-hardcoded-
  vs-disk, Section 5.6 item 2) and returns the validated three category
  tuples, or raises `GateScopeVerificationError`.
- `build_suite(current_state, historical_replay_adapter, loader)` -- pure
  function; calls `loader.loadTestsFromName(name)` exactly once for each
  name in `current_state + historical_replay_adapter`, in that order,
  and returns the resulting `unittest.TestSuite`. `loader` defaults to
  `unittest.defaultTestLoader` but is an explicit parameter so tests can
  substitute a call-recording fake.
- `run_gate(repo_root=REPO_ROOT, loader=unittest.defaultTestLoader,
  runner=None)` -- calls `verify_scope(repo_root)` first; if it raises,
  returns `1` immediately without calling `build_suite` or `loader` at
  all; otherwise asserts the four Section 5.6 item 3 hardcoded counts
  against the validated categories' lengths, calls `build_suite`, runs
  the suite with `runner or unittest.TextTestRunner()`, and returns `0`
  if and only if the result reports zero failures and zero errors.
- `main()` -- `sys.exit(run_gate())`.

### 9.2 Exact required test cases (added to `test_s8candbcp_gate_scope.py`)

1. **Scope-before-import ordering**: patch `verify_scope` to raise;
   supply a call-recording fake `loader`; call `run_gate`; assert it
   returns non-zero and that the fake loader's `loadTestsFromName` was
   never called.
2. **Exactly 58 modules loaded once each**: supply a call-recording fake
   `loader` returning empty stub suites; call `run_gate` against the real
   repository; assert `loader.loadTestsFromName` was called exactly `58`
   times, with the exact multiset of arguments equal to
   `current_state_modules + historical_replay_adapter_modules` (Section
   5.2-5.3), each name appearing exactly once.
3. **Audit-only modules never loaded**: from the same call log as case 2,
   assert neither
   `tests.rcc002.test_s8rr002_manifest_correction` nor
   `tests.rcc002.test_s8rr003_normative_ledger` (Section 5.4) appears
   anywhere in the recorded arguments.
4. **Import failure returns non-zero**: supply a fake `loader` whose
   `loadTestsFromName` raises `ImportError` for one arbitrary name; call
   `run_gate`; assert it returns non-zero (via `unittest.TestSuite`'s own
   load-error-as-failing-test behavior, or an explicit `try/except`
   around `build_suite` -- either way, the exact required outcome is a
   non-zero result, not an uncaught exception escaping `run_gate`).
5. **Test failure/error returns non-zero**: construct a real
   `unittest.TestSuite` containing one deliberately failing synthetic
   `TestCase`; supply a `loader` stub that returns this suite regardless
   of the name requested; call `run_gate`; assert it returns non-zero.
6. **Unknown/duplicate/missing/reclassified module fails closed at the
   runner level**: build an isolated temporary directory containing a
   synthetic `tests/rcc002/`-shaped tree and a gate-scope manifest
   mutated with one of the four defect classes already covered at the
   verifier level (Section 5.6 item 2, Section 9's own cases 1-12 below);
   call `run_gate(repo_root=<that temporary directory>)` end-to-end
   (using the real `verify_scope`, not a fake); assert it returns
   non-zero and that no test was ever loaded (a call-recording fake
   `loader` again proves zero `loadTestsFromName` calls).
7. **Conforming synthetic partition succeeds**: build a second isolated
   temporary directory containing two or three trivial, always-passing
   synthetic test modules standing in for `tests/rcc002/`, together with
   a correctly matching gate-scope manifest and hardcoded expectation for
   that synthetic partition (not the real `60`-module one); call
   `run_gate(repo_root=<that directory>)` end-to-end with the real
   `loader`; assert it returns `0`.

These seven cases satisfy every property `S8-CAND-BCP-REV7-TEST-001`
required: ordering, exactly-once loading, audit-only exclusion, import-
failure propagation, test-failure propagation, fail-closed rejection, and
a genuine positive control, all exercised directly against
`run_s8candbcp_gate.py`'s own behavior rather than only against
`verify_s8candbcp_gate_scope.py` in isolation.

## 10. Exact 46-entry Track 1 inventory (`LC_ALL=C` order)

Independently computed by adding exactly one path, `CLAUDE.md`, as
`MODIFIED`, to Revision 7 Section 7.3's independently-verified 45-entry
inventory, and re-sorting the union in strict `LC_ALL=C` order. No other
path is added, removed, renamed, or reclassified relative to Revision 7.

 1. `CLAUDE.md` -- MODIFIED (Section 6)
 2. `SHA256SUMS` -- MODIFIED
 3. `docs/review/evidence/RCC_002_S8CANDBCP_GATE_SCOPE_V1.json` -- NEW (Section 5.6)
 4. `docs/review/evidence/RCC_002_S8CANDBCP_REV2_NORMATIVE_LEDGER_HISTORICAL_COPY_2026-08-01.txt` -- NEW (Revision 5)
 5. `docs/review/evidence/RCC_002_S8CANDBCP_REV2_NORMATIVE_LEDGER_SCOPE_V1.json` -- NEW (Revision 5; edited again, Section 10.1 item 3)
 6. `docs/review/evidence/RCC_002_S8CANDBCP_REV2_TRACK1_NORMATIVE_SCOPE_V1.json` -- NEW (Revision 5; edited again, Section 10.1 item 1)
 7. `docs/review/evidence/RCC_002_S8RR002_HISTORICAL_DATA_PIPELINE_SPECIFICATION_0_8_0_CERTIFIED_COPY_2026-08-02.txt` -- NEW (Revision 7)
 8. `docs/review/evidence/RCC_002_S8RR002_HISTORICAL_REPRODUCIBILITY_AND_MANIFEST_0_9_0_CERTIFIED_COPY_2026-08-02.txt` -- NEW (Revision 7)
 9. `docs/specifications/RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md` -- MODIFIED
10. `docs/specifications/RCC_002_REPRODUCIBILITY_AND_MANIFEST_2026-07-23.md` -- MODIFIED
11. `registries/rcc002/views/s8_view_schema_fingerprint_profile.v1.json` -- NEW (Revision 5)
12. `schemas/rcc002/manifests/dataset-manifest/1.0.2.schema.json` -- NEW (Revision 5)
13. `scripts/rcc002/run_s8candbcp_gate.py` -- NEW (Section 9.1)
14. `scripts/rcc002/verify_s8candbcp_gate_scope.py` -- NEW (Section 5.6)
15. `scripts/rcc002/verify_s8candbcp_rev2_normative_ledger.py` -- NEW (Revision 5; edited again, Section 10.1 item 4)
16. `scripts/rcc002/verify_s8candbcp_rev2_track1_normative_scope.py` -- NEW (Revision 5; edited again, Section 10.1 item 2)
17. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/complete-valid.json` -- NEW (Revision 5)
18. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/minimal-valid.json` -- NEW (Revision 5)
19. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/CASE_LEDGER.json` -- NEW (Revision 5)
20. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/absolute-path.json` -- NEW (Revision 5)
21. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/duplicate-specification.json` -- NEW (Revision 5)
22. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/duplicate-view.json` -- NEW (Revision 5)
23. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/extra-property.json` -- NEW (Revision 5)
24. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/invalid-id.json` -- NEW (Revision 5)
25. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/invalid-timestamp.json` -- NEW (Revision 5)
26. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/missing-required-field.json` -- NEW (Revision 5)
27. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/missing-specification.json` -- NEW (Revision 5)
28. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/missing-view.json` -- NEW (Revision 5)
29. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/path-traversal.json` -- NEW (Revision 5)
30. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/reordered-specification.json` -- NEW (Revision 5)
31. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/reordered-view.json` -- NEW (Revision 5)
32. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/secret-like-field.json` -- NEW (Revision 5)
33. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/secret-like-value.json` -- NEW (Revision 5)
34. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/stale-specification-version.json` -- NEW (Revision 5)
35. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/unknown-specification.json` -- NEW (Revision 5)
36. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/unknown-view.json` -- NEW (Revision 5)
37. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/wrong-schema-identity.json` -- NEW (Revision 5)
38. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/wrong-schema-version.json` -- NEW (Revision 5)
39. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/wrong-type-nullability.json` -- NEW (Revision 5)
40. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/wrong-view-allowlist-hash.json` -- NEW (Revision 5)
41. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/wrong-view-fingerprint-hash.json` -- NEW (Revision 5)
42. `tests/rcc002/test_s8candbcp_gate_scope.py` -- NEW (Section 5.6/9; content extended, path unchanged)
43. `tests/rcc002/test_s8candbcp_rev2_normative_ledger.py` -- NEW (Revision 5; edited again, Section 10.1 item 5)
44. `tests/rcc002/test_s8candbcp_rev2_track1_normative_scope.py` -- NEW (Revision 5; byte-unchanged since Revision 7)
45. `tests/rcc002/test_s8rr002_manifest_correction_historical_replay.py` -- NEW (Section 8)
46. `tests/rcc002/test_s8rr003_normative_ledger_historical_replay.py` -- NEW (Section 7)

**Category totals**: `4` modified (items 1, 2, 9, 10) + `42` new (all
remaining items) = **`46` total**, matching Section 6.7's independently
derived figure exactly.

### 10.1 Five existing draft artifacts whose bytes change again (carried from Revision 7, counts updated)

Repository classification relative to committed HEAD is unchanged
(`NEW`, untracked) for all five; none has ever been byte-finalized,
verified, reviewed, or certified, so editing an un-finalized draft again
is not a violation of "once byte-finalized, never edited."

1. `docs/review/evidence/RCC_002_S8CANDBCP_REV2_TRACK1_NORMATIVE_SCOPE_V1.json`
   -- `total_entries` `45 -> 46`; `modified_entries` `3 -> 4`;
   `new_entries` unchanged at `42`; `entries[]` gains `CLAUDE.md`;
   `findings_in_scope` gains
   `S8-CAND-BCP-REV7-B01`, `S8-CAND-BCP-REV7-B02`,
   `S8-CAND-BCP-REV7-ARCH-001`, `S8-CAND-BCP-REV7-ARCH-002`,
   `S8-CAND-BCP-REV7-TEST-001`; `correction_id` updated to
   `RCC-002-S8-CAND-BCP-001-REV8`.
2. `scripts/rcc002/verify_s8candbcp_rev2_track1_normative_scope.py` --
   `EXPECTED_TOTAL` `45 -> 46`; `EXPECTED_MODIFIED` `3 -> 4`;
   `EXPECTED_NEW` unchanged at `42`; `EXPECTED_ENTRIES` gains
   `("CLAUDE.md", "MODIFIED")` at position 1; `CORRECTION_ID` updated as
   in item 1.
3. `docs/review/evidence/RCC_002_S8CANDBCP_REV2_NORMATIVE_LEDGER_SCOPE_V1.json`
   -- `added_entry_count` `42 -> 43`; `successor_entry_count`
   `187 -> 188`; `baseline_entry_count`, `removed_entry_count`,
   `replaced_entry_count` unchanged at `145`, `0`, `2`; `entries[]` gains
   `./CLAUDE.md`; `correction_id` updated as in item 1.
4. `scripts/rcc002/verify_s8candbcp_rev2_normative_ledger.py` --
   `EXPECTED_ADDED` `42 -> 43`; `EXPECTED_SUCCESSOR` `187 -> 188`;
   `EXPECTED_BASELINE`, `EXPECTED_REMOVED`, `EXPECTED_REPLACED` unchanged;
   `CORRECTION_ID` updated as in item 1.
5. `tests/rcc002/test_s8candbcp_rev2_normative_ledger.py` -- docstring
   corrected a second time: "187-entry" -> "188-entry". No other line
   changes (independently reconfirmed: every arithmetic case still uses
   the synthetic `3`/`1`/`0`/`1`/`4` scale, unaffected by the real count).

`tests/rcc002/test_s8candbcp_rev2_track1_normative_scope.py` again
requires **no byte change**: it references every expected count
exclusively via `verifier.EXPECTED_TOTAL`/`EXPECTED_ENTRIES`, with zero
literal occurrence of any count anywhere in its text (reconfirmed).

`tests/rcc002/test_s8candbcp_gate_scope.py` is extended (Section 9) but
its path, and its membership as exactly one `current_state` module in
the Section 5 partition, is unchanged.

## 11. Exact successor-ledger arithmetic

```text
Baseline ledger entries (unchanged, Section 2 item 8)         = 145
Replaced entries (DP, RM; count-neutral, unchanged)            =   2
New entries already added by Revision 5 Track 1                =  34
New entries added by Revision 7 (Section 7.1 of Revision 7)     =   8
New entries added by Revision 8 (CLAUDE.md, Section 6.3)        =   1
Removed entries                                                 =   0
-------------------------------------------------------------------
Added total: 34 + 8 + 1                                         =  43
Successor ledger arithmetic: 145 + 43 - 0                       = 188
Revised successor root ledger entry count                       = 188
```

`188`, independently re-derived from the exact Section 10 inventory (not
copied from the task's stated expectation), is confirmed correct: `43`
added paths are exactly the `42` `NEW`-category Track 1 files (Section
10) plus `CLAUDE.md` (which is `MODIFIED` in Track 1 terms but a new
ledger member, Section 6.3); `2` replaced paths (DP, RM) remain
count-neutral within the `145` baseline; `0` paths are removed. Self-entry
exclusion (the root ledger does not list itself) and protected-builder
exclusion (`scripts/build_rcc002_spec_bundle.py` appears in no list
anywhere in this correction family) are unchanged from every prior
revision.

## 12. Gate-scope schema and independent verifier authority (restated, now exact)

`docs/review/evidence/RCC_002_S8CANDBCP_GATE_SCOPE_V1.json`'s exact
top-level keys are unchanged from Revision 7 Section 5.4:
`scope_schema_version`, `scope_id`, `correction_id`, `gate_id`,
`findings_in_scope`, `authoritative_command`, `path_ordering`,
`test_root`, `expected_total_modules`, `expected_current_state_count`,
`expected_historical_replay_adapter_count`,
`expected_historical_audit_only_count`, `current_state_modules`,
`historical_replay_adapter_modules`, `historical_audit_only_modules` --
except that `current_state_modules`, `historical_replay_adapter_modules`,
and `historical_audit_only_modules` now hold the exact, complete Section
5.2-5.4 lists, with no ellipsis. `correction_id` is
`RCC-002-S8-CAND-BCP-001-REV8`. `findings_in_scope` is
`["S8-CAND-BCP-REV7-B01", "S8-CAND-BCP-REV7-TEST-001"]`.
`scripts/rcc002/verify_s8candbcp_gate_scope.py`'s independent hardcoded
authority is specified in Section 5.6, item 2.

## 13. Consolidated mutation-coverage matrix

| Artifact | Battery | Status |
|---|---|---|
| `verify_s8candbcp_gate_scope.py` (gate scope) | 13 cases (Section 9.1's predecessor list, restated: missing/extra/duplicate/reordered/unsafe/wrong-category/unknown/adapter-omission/historical-in-live/live-in-historical/forged-metadata/positive-control, plus new case 13: cross-copy consistency across the four independently hardcoded representations, Section 5.6) | Extended |
| `run_s8candbcp_gate.py` (gate runner) | 7 cases (Section 9.2) | New |
| `test_s8rr002_manifest_correction_historical_replay.py` (S8-RR-002 adapter) | 1 positive control + 1 negative control (Revision 7 Section 6.2, restated) + 4 arithmetic-mutation cases (Section 8.3) | Extended |
| `test_s8rr003_normative_ledger_historical_replay.py` (S8-RR-003 adapter) | 1 positive control (all 41 methods) + 1 negative control + 1 static 41-method omission-detection assertion (Section 7.1) | Redesigned |
| `verify_s8candbcp_rev2_track1_normative_scope.py` (Track 1 scope) | 9 cases (Revision 5 Section 6.8, unchanged, byte-identical test file) | Unchanged |
| `verify_s8candbcp_rev2_normative_ledger.py` (normative ledger) | 9-case-equivalent synthetic-scale battery (Revision 3 Section 6.7 lineage, unchanged) | Unchanged (1-line docstring count update only) |

Every one of the five artifact classes the task requires explicit
mutation coverage for -- gate scope, gate runner, both historical
adapters, Track 1 scope, and normative ledger -- is accounted for above.

## 14. Acyclic drafting, finalization, verification, review, and certification sequence

Extends Revision 7 Section 11 to the Section 6-9 corrections. Steps 1-13
are new or renumbered relative to Revision 7; the pre-existing 37-file
Revision 5 Track 1 draft is presumed complete and is not reopened.

1. **Draft** content for all `8` Section-original new artifacts (Revision
   7 Section 7.1), `CLAUDE.md`'s exact new text (Section 6.1), and the
   Section 10.1 edits to the `5` existing draft artifacts. The exact
   `60`-module partition (Section 5) and the exact `37`-path S8-RR-002
   remainder (Section 8.1) are both fully determined by filename/path
   sets already fixed by this document, independent of any other new
   artifact's byte content.
2. **Byte-finalize** the two frozen historical specification copies
   (Data Pipeline `0.8.0`, Reproducibility and Manifest `0.9.0`) --
   sourced from commit `6f0f840`, no dependency on any other new item.
3. **Byte-finalize** the two historical-replay adapters
   (`test_s8rr002_manifest_correction_historical_replay.py`, Revision 7
   Section 6.2 with the Section 8 arithmetic fix and Section 8.3
   mutations;
   `test_s8rr003_normative_ledger_historical_replay.py`, redesigned per
   Section 7) -- depend on step 2's frozen copies.
4. **Byte-finalize** `scripts/rcc002/verify_s8candbcp_gate_scope.py` --
   depends only on the fixed Section 5 module partition (available since
   step 1).
5. **Byte-finalize** `docs/review/evidence/RCC_002_S8CANDBCP_GATE_SCOPE_V1.json`
   -- depends on step 4.
6. **Byte-finalize** `scripts/rcc002/run_s8candbcp_gate.py` -- depends on
   steps 4-5.
7. **Byte-finalize** `tests/rcc002/test_s8candbcp_gate_scope.py`,
   including the Section 9 runner-behavior cases -- depends on steps 4
   and 6, the two artifacts it exercises.
8. **Byte-finalize** `CLAUDE.md`'s exact new text (Section 6.1) -- depends
   only on the fixed command string and path from steps 4-6 (available
   since Section 5/6, independent of those files' actual byte content).
9. **Byte-finalize** the `5` Section 10.1 edited-in-place artifacts
   (Track 1 scope manifest and verifier, ledger scope manifest and
   verifier, ledger mutation-test docstring) -- depends on the final
   Section 10 inventory (fixed at step 1) and on steps 2-8 already
   existing as concrete paths to list and count.
10. **Recompute** the root `SHA256SUMS`: Revision 7's `8` new paths were
    already entered into the working ledger's `187`-entry state (steps
    2-7 above finalize their content, unchanged in path and count from
    Revision 7); this step enters exactly the one remaining new path,
    `CLAUDE.md`, alongside that already-established `187`-entry state,
    for the exact `188`-entry total (Section 11). The already-drafted
    `37` Revision 5 entries and the `8` Revision 7 entries are not
    touched by this step; only the ledger file itself gains `1` more
    line, and the `5` Section 10.1 files' entries change hash (still
    count-neutral: already `NEW` entries, now pointing at different bytes
    for the same declared paths).
11. **Verify**: run the Section 5 authoritative gate command
    (`scripts/rcc002/run_s8candbcp_gate.py`); run the existing Track 1
    and ledger scope verifiers against the Section 11 counts; run both
    historical-audit commands directly, for confirmation, understanding
    both are expected to fail against the live tree by design.
12. **Independently review**: perform scientific and architecture review
    of the exact byte-finalized set from steps 2-10, and of this
    Revision 8 document itself.
13. **Certify**: record, externally to every artifact reviewed in step
    12, that the exact hashes verified in step 11 and reviewed in step
    12 are approved, by committing the already-byte-finalized ledger from
    step 10 (which simultaneously commits `CLAUDE.md`'s new text,
    Section 6.5). No artifact touched in steps 2-12 is edited by this
    step or by any later step (Section 6.6).

This sequence is acyclic: every step depends only on strictly earlier
steps; the ledger (step 10) is computed only after every artifact it
indexes is byte-finalized (steps 2-9); verification, review, and
certification (steps 11-13) strictly follow finalization.

## 15. Non-reviewability and non-authorization

**The current Track 1 candidate remains not reviewable and not
certifiable.** This status persists until Section 14's sequence
completes in full, the Section 5 authoritative gate command is run and
independently confirmed to exit `0`, and this Revision 8 document itself
is independently re-reviewed and not rejected. This proposal does not
authorize Track 1 certification, Track 2 implementation start or repair,
View-schema-fingerprint formula selection or emission, corrected-candidate
resubmission, dataset generation, dataset publication, or live or paper
deployment. **This proposal does not self-authorize** the Section 5-9
architecture, which remains a cross-cutting governance redefinition
requiring the same independent re-review discipline every Revision 1-7
change has gone through before any Section 10 artifact may be drafted or
byte-finalized.

## 16. Process finding, restated (no reversal claimed)

`S8-CAND-TRACK1-PROC-001` is restated unchanged in substance from
Revision 6 Section 5.2 and Revision 7 Section 13:

1. **Disclosure.** An earlier protected-builder compliance breach
   involving `scripts/build_rcc002_spec_bundle.py` remains disclosed as a
   named finding.
2. **No claim of reversal.** No action available to this or any later
   revision could undo any prior exposure of that file's content or
   digest; it is a fact of history, not a retractable state.
3. **Clean-session requirement, restated.** All future verification of
   this candidate must occur in a session that at no point reads,
   hashes, inspects, opens, executes, imports, copies, renames, deletes,
   modifies, stages, packages, or commits
   `scripts/build_rcc002_spec_bundle.py`, exactly as this revision's own
   preparation session did (Section 2, Section 17).
4. **No evidentiary status for any digest of that file.** No hash, byte
   count, modification time, or other digest of that file is treated as
   candidate evidence, scope evidence, or ledger evidence by this or any
   future revision. It remains entirely outside the Track 1 and Track 2
   exact-scope inventories.

## 17. Restrictions honored while preparing this revision

- No repository file was created, modified, deleted, renamed, staged,
  committed, or pushed.
- The existing 37-file Revision 5/6/7 Track 1 candidate, and Revision 7's
  own (never-implemented) Section 7.1 artifacts, were treated strictly
  read-only: read for architecture and hashing purposes only.
- `rcc002/s8/` and `tests/rcc002/s8/` (the prior, separate candidate) were
  read only to enumerate `test_*.py` module paths (Section 5.2); neither
  was modified, staged, committed, or pushed.
- `CLAUDE.md` was read once, in full, to quote its exact current text
  (Section 6.1); it was not modified, staged, committed, or pushed.
- `scripts/build_rcc002_spec_bundle.py` was not read, hashed, inspected,
  opened, executed, imported, copied, renamed, deleted, modified, staged,
  committed, packaged, or used as evidence at any point during this
  drafting session, and was not named as an argument to any executed
  command.
- Every `git show`/`git diff`/`git log` command executed targeted only
  DP, RM, `SHA256SUMS`, `CLAUDE.md`, and the S8-RR-002/S8-RR-003
  certified pair's own paths, or repository metadata (branch, HEAD,
  status, log); none targeted the protected builder.
- All diagnostics were passive: branch/HEAD/origin/status checks, `git
  show`/`git diff`/`git log` against historical commits, `sha256sum` and
  `grep`/`wc -l` of existing files, and static `grep`-based test-method
  counting (no `.py` file was executed as a program). No `__pycache__` or
  other repository artifact was created (independently reconfirmed:
  `git status --short` immediately following, Section 18, is
  byte-identical to the Section 2 baseline).
- No dependency was installed. No network access was used beyond the
  local `git` object store already present in this clone.
- Repository HEAD and `origin/main` were re-verified as
  `c225306095acf36ff115d7060c1cf3fa2d34397f` after all analysis and are
  unchanged by this drafting session (Section 18).
- The only filesystem write performed while preparing this revision is
  this single output Markdown file, outside the repository, at
  `/mnt/c/Users/benja/Downloads/RCC_002_S8_IMPLEMENTATION_CANDIDATE_BLOCKER_CORRECTION_PROPOSAL_REV8_2026-08-02.md`.

## 18. Final git status and HEAD/origin confirmation

`git status --short` immediately before this document was finalized:

```text
 M SHA256SUMS
 M docs/specifications/RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md
 M docs/specifications/RCC_002_REPRODUCIBILITY_AND_MANIFEST_2026-07-23.md
?? docs/review/evidence/RCC_002_S8CANDBCP_REV2_NORMATIVE_LEDGER_HISTORICAL_COPY_2026-08-01.txt
?? docs/review/evidence/RCC_002_S8CANDBCP_REV2_NORMATIVE_LEDGER_SCOPE_V1.json
?? docs/review/evidence/RCC_002_S8CANDBCP_REV2_TRACK1_NORMATIVE_SCOPE_V1.json
?? rcc002/s8/
?? registries/rcc002/views/
?? schemas/rcc002/manifests/dataset-manifest/1.0.2.schema.json
?? scripts/build_rcc002_spec_bundle.py
?? scripts/rcc002/verify_s8candbcp_rev2_normative_ledger.py
?? scripts/rcc002/verify_s8candbcp_rev2_track1_normative_scope.py
?? tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/
?? tests/rcc002/s8/
?? tests/rcc002/test_s8candbcp_rev2_normative_ledger.py
?? tests/rcc002/test_s8candbcp_rev2_track1_normative_scope.py
```

Byte-identical in composition to the Section 2 baseline. `git rev-parse
HEAD` and `git rev-parse origin/main` both return
`c225306095acf36ff115d7060c1cf3fa2d34397f`, unchanged from Section 2,
item 2. Nothing was staged (`git diff --cached` remains empty).

## 19. Final report

- **Output path**:
  `/mnt/c/Users/benja/Downloads/RCC_002_S8_IMPLEMENTATION_CANDIDATE_BLOCKER_CORRECTION_PROPOSAL_REV8_2026-08-02.md`
  (SHA-256 and line count are reported by the preparing session outside
  this document, once writing is complete, since a file cannot state its
  own digest).
- **Closure mapping**: `S8-CAND-BCP-REV7-B01` closed by Section 5 (exact
  60-module enumeration, no placeholders); `S8-CAND-BCP-REV7-B02` closed
  by Section 6 (`CLAUDE.md` inside Track 1, Option A, no post-
  certification mutation); `S8-CAND-BCP-REV7-ARCH-001` closed by Section
  7 (complete 41-method S8-RR-003 test module subprocess-executed
  against an isolated root); `S8-CAND-BCP-REV7-ARCH-002` closed by
  Section 8 (37, not 39, with pre-copy set assertions and four new
  mutation cases); `S8-CAND-BCP-REV7-TEST-001` closed by Section 9 (seven
  direct gate-runner behavior tests, no new artifact). `S8-CAND-TRACK1-GATE-B01`
  remains open, restated, not closed by this document (Section 3, Section
  15). `S8-CAND-TRACK1-PROC-001` remains disclosed, not reversed,
  restated in Section 16.
- **Track 1 counts**: `46` total (`4` modified, `42` new).
- **Successor-ledger arithmetic**: `188 = 145` baseline `+ 43` added
  `- 0` removed, `2` replacements count-neutral.
- **Module-partition counts**: `60` total (`56` current-state, `2`
  historical-replay-adapter, `2` historical-audit-only) -- independently
  reconfirmed unchanged from Revision 7's intended figures; no correction
  to these specific counts was required (the defect was the missing
  enumeration, not a wrong count).
- **Confirmations**: repository state is unchanged (Section 18 is
  byte-identical to the Section 2 baseline); nothing was staged,
  committed, or pushed; `scripts/build_rcc002_spec_bundle.py` was never
  read, hashed, inspected, opened, executed, imported, copied, renamed,
  deleted, modified, staged, committed, packaged, or used as evidence at
  any point in the preparation of this revision.

## 20. Final statement

Revision 8 closes all five findings the Revision 7 re-review raised,
without reopening any Revision 1-6 finding and without changing any part
of Revision 7's architecture the re-review did not fault. The exact
60-module gate partition is enumerated in full (Section 5), with four
independently hardcoded, non-import-chained representations across the
manifest, verifier, runner, and mutation-test artifacts. `CLAUDE.md` is
brought inside the certified Track 1 byte set, byte-finalized before
verification and review, eliminating the prior interim-authority
contradiction and prohibiting any post-certification mutation (Section
6). The S8-RR-003 historical replay now executes the complete,
byte-identical, 41-method certified test module in an isolated root via
subprocess, exactly mirroring S8-RR-002, preserving the `ResourceWarning`
regression and the full scope/ledger mutation battery (Section 7). The
S8-RR-002 replay's remainder is corrected to the mechanically-derived
`37`, with pre-copy set assertions and four new arithmetic-mutation cases
(Section 8). `scripts/rcc002/run_s8candbcp_gate.py` itself now has seven
direct behavioral tests, added to the already-proposed
`test_s8candbcp_gate_scope.py` with no new artifact and no module-count
change (Section 9). Track 1 is independently recomputed to `46` files
(`4` modified, `42` new) and the successor ledger to `188` entries
(`145 + 43 - 0`, `2` replacements count-neutral), both derived from exact
path sets, not copied from the task's stated expectation. This document
creates, modifies, or byte-finalizes nothing itself; it does not
self-authorize the architecture it proposes; Track 1 remains not
reviewable and not certifiable; Track 2, dataset generation, publication,
and deployment remain unauthorized; and the earlier protected-builder
compliance breach (`S8-CAND-TRACK1-PROC-001`) remains disclosed, without
claim of reversal.
