# RCC-002 S8 Implementation Candidate Blocker Correction Proposal - Revision 6

## Document control

| Field | Value |
|---|---|
| Proposal ID | `RCC-002-S8-CAND-BCP-001-REV6` |
| Proposal date | `2026-08-02` |
| Proposal class | Correction planning only (read-only diagnosis; no implementation) |
| Revision | `6` (supersedes nothing in Revision 5; amends it narrowly, adds one new blocking finding) |
| Target artifact | The approved, uncommitted Revision 5 Track 1 candidate, and the mandatory complete `tests/rcc002` gate it must pass before it is reviewable |
| Repository branch | `main` |
| Required/verified HEAD | `09bf13ab46d7c66ec08d0fd1186847a4f279bc93` |
| Required/verified `origin/main` | `09bf13ab46d7c66ec08d0fd1186847a4f279bc93` |
| Uncommitted worktree state at drafting time | Exactly 37 Track 1 files modified/new (Revision 5 Section 8.2, byte-finalized), plus the untouched prior candidate (`rcc002/s8/`, 21 files; `tests/rcc002/s8/`, 12 files) and the pre-existing untracked protected file `scripts/build_rcc002_spec_bundle.py` |
| Superseded proposal | None. This is not a Revision 5 rewrite. |
| Amended proposal | `docs/review/RCC_002_S8_IMPLEMENTATION_CANDIDATE_BLOCKER_CORRECTION_PROPOSAL_REV5_2026-08-01.md` |
| Revision 5 SHA-256 (independently recomputed, matches) | `977568eef7b4ea3c09480a0c57f52c1b5a3dfc733e9e019b2468ab9e1fd43b03` |
| Controlling Revision 5 re-review | `docs/review/RCC_002_S8_IMPLEMENTATION_CANDIDATE_BLOCKER_CORRECTION_PROPOSAL_REV5_CHATGPT_INDEPENDENT_RE_REVIEW_2026-08-02.md` |
| Revision 5 re-review SHA-256 (independently recomputed) | `17fc7480c2878cd71fc0ebc29789b05263b904f50702d1192f5a479f8b682f7a` |
| Revision 5 re-review decision | `APPROVE` (of the correction *plan*; it does not certify Track 1 artifacts and did not run any test) |
| New finding addressed | `S8-CAND-TRACK1-GATE-B01` (BLOCKER) |
| New process finding disclosed | `S8-CAND-TRACK1-PROC-001` |
| Proposal status | **Proposal only. Not approved. Not certified. Does not authorize implementation, Track 2, dataset generation, publication, or deployment.** |

### Protected-file exclusion statement

`scripts/build_rcc002_spec_bundle.py` was not read, hashed, inspected, opened,
executed, imported, copied, renamed, deleted, modified, staged, or packaged in
the preparation of this revision. It appears in this document only in this
explicit exclusion statement, the document-control worktree-state row, the
process-finding section (Section 5), and the restrictions section (Section
11).

## 1. Purpose and scope of Revision 6

Revision 5 was independently re-reviewed and **approved** as a *plan*
(`S8-CAND-BCP-REV5-CHATGPT-IRR-001`, `APPROVE`, 2026-08-02). Its own Section 8
of that re-review is explicit that approval "does not certify the future
normative artifacts" and that "no claim is made that future Track 1 ... code
already passes tests" (re-review Section 8). Acting on that plan, the 37-file
Track 1 candidate in Revision 5 Section 8.2 has since been drafted and
byte-finalized in the working tree (Revision 5 Section 6.6 steps 1-9 have
executed; the root `SHA256SUMS` in the working tree now contains 179 entries,
matching Revision 5 Section 6.7 exactly). Step 10 of that same sequence --
"exact-scope mechanical verification" -- was then run, at the *complete*
`tests/rcc002` suite level, per this repository's ordinary validation
discipline. It is not green: 903 of 908 tests pass; 5 fail.

This is a **new** blocker, discovered only by actually running the mandatory
complete-suite gate, not a defect in the Revision 5 correction plan itself and
not a reopening of any finding Revision 5 or its re-review closed. Revision 6
amends Revision 5 only to the minimum extent necessary to close this new
gate blocker: it adds one new finding (`S8-CAND-TRACK1-GATE-B01`), one new
process finding (`S8-CAND-TRACK1-PROC-001`), and a narrow, additive extension
to the Track 1 exact-scope inventory and successor-ledger arithmetic. It does
not touch, reopen, or contradict any Revision 1-5 finding, count, version,
grammar, or architectural decision. It does not repair anything: **it is a
diagnosis and a plan, prepared entirely read-only.**

## 2. Baseline and candidate state verified before drafting

- Repository branch `main`, HEAD and `origin/main` both
  `09bf13ab46d7c66ec08d0fd1186847a4f279bc93`, verified by `git rev-parse`
  before and during drafting; unchanged throughout.
- `git status --porcelain=v1 -uall` was inspected in full (not summarized by
  directory) and contains exactly 71 changed/untracked paths, decomposing
  exactly as expected:
  - 37 Track 1 paths (Revision 5 Section 8.2: `SHA256SUMS` plus the two
    modified specifications, modified; 34 new paths) -- unchanged from
    Revision 5, not touched by this diagnosis;
  - 21 untouched prior-candidate production files under `rcc002/s8/`;
  - 12 untouched prior-candidate test files under `tests/rcc002/s8/`;
  - 1 pre-existing untracked protected file,
    `scripts/build_rcc002_spec_bundle.py`, excluded from all analysis.
  `37 + 21 + 12 + 1 = 71`, matching the observed count exactly.
- The root `SHA256SUMS` in the working tree independently re-parsed to
  exactly 179 lines, all matching `^[0-9a-f]{64}  ./...`; `git diff
  SHA256SUMS` independently confirmed exactly 36 added lines and 2 replaced
  lines, with the 2 replacements being exactly the Data Pipeline and RM
  specification entries (Section 4 below), matching Revision 5 Section 6.7's
  `145 + 34 - 0 = 179` arithmetic exactly.
- `tests/rcc002` was executed with `PYTHONDONTWRITEBYTECODE=1 python -m
  unittest discover -s tests/rcc002 -p "test_*.py"`. Result: **`Ran 908
  tests ... FAILED (failures=3, errors=2)`**, i.e. 903 passed, 5 failed,
  matching the task's reported baseline exactly. No `__pycache__` directory
  or other repository artifact was created (`PYTHONDONTWRITEBYTECODE=1`
  suppresses `.pyc` writes; no other file write occurs during `unittest`
  discovery/execution of these modules).
- TD-005 (`python -m unittest discover -s tests/regression -p "test_*.py"`)
  was **not** re-run during this diagnosis; its reported 170/170 state is
  restated from the task's own baseline, not independently re-derived, and
  is out of scope for a `tests/rcc002`-only gate blocker.
- `scripts/build_rcc002_spec_bundle.py` was not accessed at any point during
  this diagnosis (Section 11).

## 3. Five-failure evidence table

All five failures were reproduced with the exact command in Section 2. Test
IDs are unittest dotted IDs (`module.TestClass.test_method`).

| # | Test ID | File | Result | Exact assertion/error |
|---|---|---|---|---|
| 1 | `test_s8rr003_normative_ledger.Case01ValidPositiveControl.test_full_repo_state_passes` | `tests/rcc002/test_s8rr003_normative_ledger.py:78` | ERROR | `verify_s8rr003_normative_ledger.VerificationError: current_ledger_count_mismatch`, raised at `scripts/rcc002/verify_s8rr003_normative_ledger.py:734` |
| 2 | `test_s8rr003_normative_ledger.ResourceHandlingRegression.test_no_resource_warning_on_successful_run` | `tests/rcc002/test_s8rr003_normative_ledger.py:465` | ERROR | Identical: `VerificationError: current_ledger_count_mismatch`, same raise site, line 734 |
| 3 | `test_s8rr002_manifest_correction.S8RR002ManifestCorrectionTests.test_non_self_specification_hashes_are_literal_and_match_disk` | `tests/rcc002/test_s8rr002_manifest_correction.py:141` | FAIL | `AssertionError: '98608db199c525a2a7fcd05f2bff29c73ccad135b02fc0cd10fe180ca03b2e13' != '0e060d30b75082b74eb5211b1d378837aa7872d86f62e5e162586e2a2cc37fad'` (message: `RCC_002_DATA_PIPELINE_SPECIFICATION/0.8.0`) |
| 4 | `test_s8rr002_manifest_correction.S8RR002ManifestCorrectionTests.test_rm_specification_profile_exact_seven_order` | `tests/rcc002/test_s8rr002_manifest_correction.py:123` | FAIL | `AssertionError: Lists differ` -- first differing element `('RCC_002_DATA_PIPELINE_SPECIFICATION', '0.9.0')` vs expected `(..., '0.8.0')`; also differs on `('RCC-002-RM', '0.9.1')` vs expected `(..., '0.9.0')` |
| 5 | `test_s8rr002_manifest_correction.S8RR002ManifestCorrectionTests.test_verifier_end_to_end_passes` | `tests/rcc002/test_s8rr002_manifest_correction.py:233` | FAIL | `rcc002_s8rr002_verifier.VerificationError: RCC_002_DATA_PIPELINE_SPECIFICATION/0.8.0: on-disk sha256 98608db1... does not match Revision 2 literal hash 0e060d30...`, raised at `scripts/rcc002/verify_s8rr002_artifacts.py:384`, reached via `main()` at line 641 |

**Involved files (all four pre-existing, tracked, committed, and
independently confirmed certified):**

| Path | Certifying commit | Certification title |
|---|---|---|
| `scripts/rcc002/verify_s8rr002_artifacts.py` | `6f0f840` | "Certify RCC-002 S8 manifest corrections" |
| `tests/rcc002/test_s8rr002_manifest_correction.py` | `6f0f840` | "Certify RCC-002 S8 manifest corrections" |
| `scripts/rcc002/verify_s8rr003_normative_ledger.py` | `feb0bcc` | "Certify RCC-002 S8 normative-ledger correction" |
| `tests/rcc002/test_s8rr003_normative_ledger.py` | `feb0bcc` | "Certify RCC-002 S8 normative-ledger correction" |

None of these four files is in the Revision 5 Track 1 or Track 2 inventory.
None was modified by the Track 1 candidate. `git ls-files` confirms all four
are tracked; `git log --oneline` confirms both certifying commits are
ancestors of the current HEAD.

## 4. Root-cause analysis

### 4.1 Cause classification per failure

| # | Test ID | Cause |
|---|---|---|
| 1 | `test_full_repo_state_passes` | Successor-ledger count change (authorized: 145 -> 179, Revision 5 Section 6.7) |
| 2 | `test_no_resource_warning_on_successful_run` | Successor-ledger count change (authorized, identical to #1) |
| 3 | `test_non_self_specification_hashes_are_literal_and_match_disk` | Authorized DP hash replacement (0.8.0 -> 0.9.0, Revision 5 Section 6.3/6.6 step 4) |
| 4 | `test_rm_specification_profile_exact_seven_order` | Authorized DP hash/version replacement **and** authorized RM hash/version replacement (0.9.0 -> 0.9.1, Revision 5 Section 6.3/6.6 step 5), both surfaced in one tuple-list comparison |
| 5 | `test_verifier_end_to_end_passes` | Authorized DP hash replacement (same as #3; the verifier's own `main()` raises before it can reach the equivalent RM-side check) |

**All five failures are caused exclusively by the authorized Revision 5
Track 1 changes, applied exactly as specified. No failure is caused by any
defect in the 37-file Track 1 inventory, by an unauthorized or accidental
change, or by any cause external to Sections 6.3/6.6/6.7 of Revision 5.**
This was independently confirmed three ways: (a) `git diff SHA256SUMS`
shows exactly 2 replaced lines, both the DP and RM specification entries,
plus exactly 36 added lines, with no unexpected line; (b) the on-disk DP
text hashes to `98608db1...`, which is not an arbitrary corruption but
exactly the byte content produced by the authorized `0.8.0 -> 0.9.0` edit
(Revision 5 Section 8.2 item 5); (c) independently checking out the DP text
at the S8-RR-002 certifying commit `6f0f840` and hashing it in isolation
reproduces the hardcoded literal `0e060d30b75082b74eb5211b1d378837aa7872d86f62e5e162586e2a2cc37fad`
exactly, proving that literal is a correct historical fact, not a stale or
wrong value.

### 4.2 Structural mechanism (why "authorized" changes break "passing" certified tests)

`scripts/rcc002/verify_s8rr002_artifacts.py` and
`scripts/rcc002/verify_s8rr003_normative_ledger.py`, together with their
certified test modules, were built at S8-RR-002/S8-RR-003 certification time
to validate **the live, current repository tree directly**, using
un-versioned, in-place paths:

- `verify_s8rr002_artifacts.py` reads `docs/specifications/
  RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md` and
  `docs/specifications/RCC_002_REPRODUCIBILITY_AND_MANIFEST_2026-07-23.md`
  directly (module-level `RM_PATH`/`DP_PATH` constants, `verify.py:29-31`,
  mirrored in the test module), and hardcodes the exact bytes those files
  held **at S8-RR-002's own certification**: `NON_SELF_SPECIFICATIONS`
  (`verify_s8rr002_artifacts.py:41-60`) fixes DP at literal version `0.8.0`
  and literal SHA-256 `0e060d30...`; `SELF_SPECIFICATION`
  (line 61) fixes RM's declared version at `0.9.0`.
- `verify_s8rr003_normative_ledger.py` reads the root `SHA256SUMS` directly
  (`LEDGER_PATH = "SHA256SUMS"`, resolved against `REPO_ROOT`, line 18-25),
  and hardcodes `EXPECTED_CURRENT_ENTRY_COUNT = 145` (line 29) and
  `CURRENT_RM_SHA256 = "23fd2fc0..."` (line 38) -- the exact ledger-entry
  count and RM digest recorded in the ledger **at S8-RR-003's own
  certification**.

Both hardcoded literal sets are, independently verified, **correct
historical facts** -- not bugs -- about the repository as it stood at commits
`6f0f840` and `feb0bcc` respectively. The design implicitly assumed the live
paths it reads (`docs/specifications/.../*.md`, root `SHA256SUMS`) would not
be advanced again before the S8 candidate was certified. Revision 5 Track 1
is the first correction cycle since those two certifications to legitimately
advance exactly those same live paths (DP to `0.9.0`, RM to `0.9.1`, the
root ledger to 179 entries) -- which is precisely what Revision 5 Section 6.3
and Section 6.7 require and what its re-review approved. Because the
certified verifiers/tests bind themselves to the live tree with no
versioned or frozen input, and because a live path cannot simultaneously
equal both its old and new certified value, **these two predecessor
suites cannot both remain green against the live tree and let Track 1's own
authorized advancement proceed** -- this is a structural, foreseeable
consequence of an unversioned "current tree" test contract, not a defect
introduced by this candidate.

### 4.3 What this is not

- Not a case where DP/RM hashes should be "corrected" back -- the literals
  are historically true and must not be edited (Section 5.2).
- Not a case where the Track 1 candidate's own new verifiers
  (`verify_s8candbcp_rev2_normative_ledger.py`,
  `verify_s8candbcp_rev2_track1_normative_scope.py`) are wrong -- those
  target the successor state correctly and are not among the 5 failures.
- Not a scope-manifest or ordering defect (Revision 5 Section 8.1/8.2) -- the
  37-file inventory and 179-entry ledger arithmetic are independently
  reconfirmed exact and untouched by this diagnosis (Section 2).

## 5. Findings

### 5.1 `S8-CAND-TRACK1-GATE-B01` (BLOCKER)

**Statement.** The mandatory complete `tests/rcc002` gate fails 5/908
because the certified S8-RR-002 (`6f0f840`) and S8-RR-003 (`feb0bcc`)
predecessor verifier/test pairs validate the live repository tree with no
versioned or frozen input, and therefore necessarily diverge from their own
certified literal expectations once Track 1's authorized DP/RM/ledger
advancement is applied to the same live paths those pairs read. This
renders the current 37-file Track 1 candidate **not reviewable and not
certifiable**: Revision 5 Section 6.9 gate item 5 requires "exact-scope
mechanical verification," and this repository's ordinary validation
discipline (CLAUDE.md, "Validation after implementation") requires the
complete relevant test suite to be green before a candidate proceeds to
independent review; neither condition is met while these 5 failures stand.

**Severity rationale.** BLOCKER: it stops Track 1 certification (Revision 5
Section 6.9 items 6-7) and therefore Track 2 authorization (Revision 5
Section 10 gate), exactly as the "Fail-closed sequencing" diagram in
Revision 5 Section 10 requires -- no downstream step may proceed while an
upstream gate is red.

**Disposition required.** Closed only by Section 6 below (a new,
additive, non-mutating correction architecture), followed by a fresh
independent re-review of this Revision 6, before any of Section 6's new
artifacts may be drafted or byte-finalized.

### 5.2 `S8-CAND-TRACK1-PROC-001` (process finding, disclosure)

Per explicit task instruction, an earlier protected-builder compliance
breach involving `scripts/build_rcc002_spec_bundle.py` is disclosed here as
a process finding. This diagnosis independently searched the repository's
own review trail (every Revision 1-5 proposal and re-review document, the
original candidate review, and RR004) for a documented account of that
breach; every one of those documents' own protected-file sections records
only "absent" / "excluded from all analysis" / "not accessed" outcomes --
none records an actual access. This diagnosis therefore cannot
independently verify or characterize the specifics of the breach from the
repository's own paper trail, and does not attempt to invent details beyond
what was stipulated.

Consistent with the required disposition:

1. **Disclosure.** The breach is disclosed here, in this proposal, as a
   named finding (`S8-CAND-TRACK1-PROC-001`), rather than omitted or
   silently absorbed into Section 5.1.
2. **No claim of reversal.** This proposal does not claim, and no action
   available to it could accomplish, that the breach can be undone. Any
   prior exposure of `scripts/build_rcc002_spec_bundle.py`'s content or
   digest to any process is a fact of history, not a state that a
   read-only diagnosis or a later proposal revision can retract.
3. **Clean-session requirement, going forward.** All future verification of
   this candidate (Track 1 finalization, Track 2 repair, mechanical
   verification, independent review, certification) must occur in a
   session that at no point reads, hashes, inspects, opens, executes,
   imports, copies, renames, deletes, modifies, stages, or packages
   `scripts/build_rcc002_spec_bundle.py`, exactly as this diagnosis session
   itself did (Section 2, Section 11).
4. **No evidentiary status for any digest of that file.** No hash, byte
   count, modification time, or other digest of `scripts/build_rcc002_
   spec_bundle.py`, however obtained, is treated as candidate evidence,
   scope evidence, or ledger evidence by this or any future revision in
   this correction family. The file remains, as in every prior revision,
   entirely outside the Track 1 and Track 2 exact-scope inventories.

## 6. Correction architecture (plan only; nothing below is created by this proposal)

### 6.1 Governing constraints

1. The four certified files identified in Section 3 (`verify_s8rr002_
   artifacts.py`, `test_s8rr002_manifest_correction.py`, `verify_s8rr003_
   normative_ledger.py`, `test_s8rr003_normative_ledger.py`) are certified
   historical evidence (Revision 5 Section 11, "Historical preservation").
   **No byte of any of these four files may be edited, and this proposal
   does not propose editing any of them.**
2. No test may be skipped, `xfail`ed, weakened, deleted, or relabeled to
   reach a green gate (task restriction, restated as binding here).
3. No hardcoded literal in the four certified files may be changed to match
   the live tree -- those literals are correct historical facts about the
   state DP/RM/the root ledger held at `6f0f840`/`feb0bcc` respectively
   (Section 4.2), and changing them would falsify what S8-RR-002/S8-RR-003
   actually certified.
4. Historical verification capability must be preserved: it must remain
   possible, indefinitely, to mechanically prove that the DP/RM/root-ledger
   bytes S8-RR-002 and S8-RR-003 certified are exactly what those
   certifications say they are -- this is the entire point of a ledger-based
   certification scheme and must not be lost merely because Track 1 has
   since moved the live tree forward.

### 6.2 Resolution of the four open questions (task item 8)

1. **Should existing historical tests use frozen historical inputs?** Yes.
   The four certified files themselves stay byte-unmodified (6.1.1); what
   must change is that their *invocation for the purpose of the mandatory
   gate* is retargeted to frozen, versioned historical byte sources instead
   of the live working tree, via new, additive adapter modules (6.3) that
   call the certified files' already-certified pure functions without
   editing them.
2. **Are successor verifier/test versions required?** No new successor
   *verifiers* are required for DP/RM/root-ledger -- Revision 5's own new
   Track 1 verifiers (`verify_s8candbcp_rev2_normative_ledger.py`,
   `verify_s8candbcp_rev2_track1_normative_scope.py`) already are the
   successor verification path for the live/current state. What is missing
   is not a successor verifier but a **historical-replay adapter** for the
   two *predecessor* verifiers, so their certified assertions can still be
   exercised against frozen bytes.
3. **Must current-suite routing become version-aware?** Yes. The mandatory
   "complete `tests/rcc002` gate is green" criterion, as currently
   operationalized by flat `unittest discover`, does not distinguish
   "validates the live/current tree" test modules from "replays a
   certified historical point-in-time claim" test modules. This proposal
   requires an explicit, declared partition (6.3, item 3) and a redefinition
   of the gate criterion (6.4) so that the two kinds of obligation are each
   evaluated against the correct input.
4. **Is another explicit versioned solution necessary?** The combination of
   (a) frozen historical byte copies, (b) new non-mutating replay adapters,
   and (c) an explicit gate-scope declaration is the versioned solution;
   nothing further (e.g. rewriting the ledger scheme itself) is proposed.

### 6.3 New artifacts (plan only; not yet drafted, not yet byte-finalized)

| # | Exact path | Classification | Purpose |
|---|---|---|---|
| 38 | `docs/review/evidence/RCC_002_S8RR002_HISTORICAL_DATA_PIPELINE_SPECIFICATION_0_8_0_CERTIFIED_COPY_2026-08-02.txt` | NEW | Frozen byte-for-byte copy of `docs/specifications/RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md` exactly as it stood at S8-RR-002's certifying commit `6f0f840` (mechanically sourced via `git show 6f0f840:<path>`; independently confirmed during this diagnosis to hash to the certified literal `0e060d30b75082b74eb5211b1d378837aa7872d86f62e5e162586e2a2cc37fad`, Section 4.1) |
| 39 | `docs/review/evidence/RCC_002_S8RR002_HISTORICAL_REPRODUCIBILITY_AND_MANIFEST_0_9_0_CERTIFIED_COPY_2026-08-02.txt` | NEW | Frozen byte-for-byte copy of the RM specification at the same S8-RR-002 certifying commit `6f0f840` (RM `0.9.0`) |
| 40 | `docs/review/evidence/RCC_002_S8CANDBCP_REV2_HISTORICAL_REPLAY_GATE_SCOPE_V1.json` | NEW | Gate-scope declaration: enumerates which `tests/rcc002` modules are "current-state" (must pass against the live tree) versus "certified historical replay" (S8-RR-002/S8-RR-003 originals, permanently pinned to their certifying commit; expected to diverge from the live tree after any later authorized advancement of DP/RM/root-ledger, by design, not as a regression), and names the two new adapters (below) as the actual mandatory-gate obligation standing in for each historical-replay pair |
| 41 | `tests/rcc002/test_s8rr002_manifest_correction_historical_replay.py` | NEW | Adapter: imports the certified `verify_s8rr002_artifacts` module's functions (unmodified) and exercises them against items 38-39 instead of the live tree, reproducing every S8-RR-002 assertion against frozen history |
| 42 | `tests/rcc002/test_s8rr003_normative_ledger_historical_replay.py` | NEW | Adapter: imports the certified `verify_s8rr003_normative_ledger` module's functions (unmodified) and exercises them against the **already-existing** Track 1 item 2 (`docs/review/evidence/RCC_002_S8CANDBCP_REV2_NORMATIVE_LEDGER_HISTORICAL_COPY_2026-08-01.txt`) instead of the live root `SHA256SUMS`. No new frozen ledger copy is needed: this diagnosis independently confirmed that file is byte-identical both to the current `HEAD:SHA256SUMS` and to `feb0bcc:SHA256SUMS` (the exact S8-RR-003 certifying-commit ledger, 145 entries, no diff) |

No path is removed. No existing Track 1 path (items 1-37) or Track 2 path
is renamed, reclassified, or edited. Items 38-42 are purely additive.

### 6.4 Redefinition of the mandatory-gate criterion (proposed, not self-authorized)

Going forward, "the mandatory complete `tests/rcc002` gate is green" is
proposed to mean: every current-state test module passes against the live
tree, **and** both new historical-replay adapters (items 41-42) pass against
their frozen inputs (items 38-39 and the existing item 2). The two original
certified predecessor suites (`test_s8rr002_manifest_correction.py`,
`test_s8rr003_normative_ledger.py`) remain present and byte-unmodified for
direct historical audit, but are excluded from the live-tree pass/fail gate
given their documented, permanent, expected post-advancement divergence --
exactly the same relationship Revision 5's own `HISTORICAL_EVIDENCE_PATH`
pattern already establishes for the ledger's own predecessor-bundle
comparison.

**This is a binding, cross-cutting redefinition of a governance success
criterion, not merely a file addition.** Per this repository's own working
rules (architecture authority is never self-granted; this proposal does not
certify itself), Revision 6 **proposes** this redefinition and flags it for
the same independent re-review discipline every other Revision 1-5 change
has gone through -- it is not adopted merely by this document existing.

### 6.5 Deterministic sequencing and byte-finalization order

Applying the same discipline as Revision 5 Section 6.6 (draft, then
byte-finalize in dependency order, then verify, then review, then certify --
never mutate after finalization):

1. **Draft** items 38-42 (content only; nothing byte-finalized yet).
2. **Byte-finalize** items 38-39 (frozen DP/RM copies) -- mechanically
   sourced from commit `6f0f840`, no dependency on any other new item.
3. **Byte-finalize** item 41 (S8-RR-002 replay adapter) -- depends on items
   38-39 being fixed.
4. **Byte-finalize** item 42 (S8-RR-003 replay adapter) -- depends on the
   already-byte-finalized existing Track 1 item 2 only; no new ledger copy
   required (Section 6.3).
5. **Byte-finalize** item 40 (gate-scope declaration) -- depends on items
   41-42 existing, so it can name their exact paths and the exact set of
   current-state versus historical-replay modules.
6. **Recompute** the root `SHA256SUMS`: enter items 38-42 as 5 new entries
   alongside the already-byte-finalized 179-entry state (Section 6.6 below).
   The already-finalized 37 Track 1 entries and their content are not
   touched; only the ledger file itself gains 5 more lines, since -- per
   Section 4 of Revision 5's own re-review and per this proposal's Section
   5.1 -- the Track 1 candidate was never actually verified (step 10 never
   passed), so its ledger was never reviewed or certified in its 179-entry
   form; extending it to 184 before verification is not a mutation of a
   certified artifact.
7. **Verify**: re-run the complete `tests/rcc002` gate as redefined in
   Section 6.4.
8. **Independently review**, then **certify**, exactly as Revision 5
   Section 6.6 steps 11-12 require -- externally, with no further mutation
   of any item above.

### 6.6 Revised Track 1 inventory and ledger arithmetic

| Item | Value |
|---|---|
| Track 1 file count before Revision 6 | 37 (3 modified, 34 new) |
| Track 1 additions in Revision 6 | 5 (items 38-42, all NEW) |
| **Revised Track 1 file count** | **42 (3 modified, 39 new)** |
| Baseline ledger entries (unchanged, independently reconfirmed) | 145 |
| Replaced entries (DP, RM; count-neutral, unchanged) | 2 |
| New entries already added by Revision 5 Track 1 | 34 |
| New entries added by Revision 6 (items 38-42) | 5 |
| Removed entries | 0 |
| **Revised successor ledger arithmetic** | `145 + 34 + 5 - 0 = 184` |
| **Revised successor root ledger entry count** | **184** |

## 7. Test and mutation requirements for the two new adapters

Each of items 41-42 must, at minimum:

1. Reproduce, in intent, every assertion made by its corresponding certified
   test class (`S8RR002ManifestCorrectionTests` / the `test_s8rr003_
   normative_ledger.py` test classes), substituting only the byte source
   (frozen copy instead of live path) -- not inventing new assertions and not
   dropping any existing one.
2. Include an explicit **positive control**: the adapter passes when run
   against the frozen inputs (items 38-39, or existing item 2), proving the
   certified historical claim still holds against its own frozen record.
3. Include an explicit **negative control**: the adapter is proven to
   **fail** if it is (in a throwaway, in-test copy) pointed at the *current
   live* DP/RM text or the current live root `SHA256SUMS` instead of the
   frozen input -- proving the adapter is genuinely pinned to history and has
   not silently degraded into re-testing the live tree (which would defeat
   its entire purpose and reintroduce the exact failure mode in Section 4).
4. Never import, execute, modify, or otherwise touch `scripts/build_
   rcc002_spec_bundle.py` (Section 5.2, Section 11).

Full mutation-battery case design (missing/extra/duplicate/reordered/
forged-metadata, per the nine-case minimum Revision 5 Section 6.8 applies to
the Track 1 and Track 2 scope verifiers) is **not** prescribed here for
items 41-42, because they are thin replay adapters over already-certified,
already-mutation-tested verifier functions (Revision 5 Section 8.4), not new
verifiers with their own hardcoded scope logic; independent review should
confirm this scoping judgment before implementation.

## 8. Independent re-review requirement before any repair

**No artifact in Section 6.3 may be drafted, byte-finalized, or committed
until this Revision 6 document itself has been independently re-reviewed
and a decision recorded**, exactly as every Revision 1-5 change was gated.
The re-review must independently:

1. Re-verify all five failures reproduce exactly as reported in Section 3;
2. Re-verify the DP/RM/root-ledger literals in the four certified files are
   correct historical facts (Section 4.2), not defects;
3. Re-verify the four certified files remain byte-identical to their
   certifying commits (`6f0f840`, `feb0bcc`) throughout this diagnosis and
   are not proposed for modification anywhere in this document;
4. Assess whether the Section 6.4 gate-criterion redefinition is
   architecturally sound and whether it requires escalation to a full
   Architecture/Specification/Certification chain rather than being decided
   inside a "focused" correction-proposal revision; and
5. Confirm `scripts/build_rcc002_spec_bundle.py` was not accessed in the
   preparation of this revision.

## 9. Explicit statement of non-reviewability

**The current 37-file Track 1 candidate, as it stands in the working tree at
the time of this diagnosis, is not reviewable and is not certifiable.** It
fails the mandatory complete `tests/rcc002` gate (5/908 failing, Section 3).
No Track 1 certification (Revision 5 Section 6.9 items 6-7), no Track 2
implementation start (Revision 5 Section 10 gate), no View-schema-fingerprint
formula selection or emission, no corrected-candidate resubmission, no
dataset generation, no dataset publication, and no live or paper deployment
is authorized by this proposal or by the current candidate state. This
status persists until `S8-CAND-TRACK1-GATE-B01` is closed through the
Section 6 architecture, re-reviewed per Section 8, and the complete
`tests/rcc002` gate (as redefined in Section 6.4, or as otherwise decided by
that re-review) is independently confirmed green.

## 10. No Track 2, dataset, publication, or deployment authority

Consistent with every prior revision in this family: this proposal grants no
authority over Track 2 implementation repair, dataset generation, dataset
publication, or live/paper deployment, in either direction. Revision 5
Section 11's decision-separation principle (proposal approval, normative
contract certification, implementation repair authorization, candidate
re-certification, and S8/dataset readiness remain five separate decisions)
applies unchanged to this revision; approving this Revision 6 approves only
the diagnosis and plan in Sections 3-8, nothing else.

## 11. Restrictions honored while preparing this revision

- No repository file was created, modified, deleted, renamed, staged,
  committed, or pushed.
- The existing 37-file Revision 5 Track 1 candidate was treated strictly
  read-only: not modified, staged, committed, or pushed; independently
  reconfirmed present and unchanged (Section 2) throughout this diagnosis.
- `rcc002/s8/` and `tests/rcc002/s8/` (the prior, separate candidate) were
  not read, modified, staged, committed, or pushed.
- `scripts/build_rcc002_spec_bundle.py` was not read, hashed, inspected,
  opened, executed, imported, copied, renamed, deleted, modified, staged,
  or packaged at any point during this diagnosis.
- All test execution used `PYTHONDONTWRITEBYTECODE=1`; no `__pycache__`
  directory or other repository artifact was created.
- No dependency was installed. No network access was used.
- Repository HEAD and `origin/main` were re-verified as
  `09bf13ab46d7c66ec08d0fd1186847a4f279bc93` before drafting and are
  unchanged by this diagnosis (this diagnosis performs no commit).
- Nothing was staged (`git status` composition is unchanged from the
  documented starting state, modulo this diagnosis's own read-only
  commands, none of which alter tracked or untracked file bytes).
- The only filesystem write performed while preparing this revision was
  this single output Markdown file, outside the repository, at
  `/mnt/c/Users/benja/Downloads/RCC_002_S8_IMPLEMENTATION_CANDIDATE_BLOCKER_CORRECTION_PROPOSAL_REV6_2026-08-02.md`.

## 12. Final statement

Revision 6 diagnoses, exactly and completely, the new mandatory-gate
blocker discovered after Revision 5's approved Track 1 candidate was
byte-finalized: 5 of 908 `tests/rcc002` failures, all traced to two
certified predecessor verifier/test pairs (S8-RR-002, S8-RR-003) that bind
themselves to the live repository tree with no frozen or versioned input,
and therefore necessarily diverge from their own correct, historical,
literal expectations once Track 1's authorized DP/RM/root-ledger
advancement is applied. No historical literal is wrong. No certified file is
proposed for modification. The correction is additive only: two frozen
historical-copy artifacts, two non-mutating replay adapters, and one
gate-scope declaration (items 38-42), extending the Track 1 inventory from
37 to 42 files and the successor-ledger arithmetic from 179 to 184 entries,
with deterministic byte-finalization sequencing (Section 6.5) and explicit
test/mutation requirements (Section 7). The earlier protected-builder
compliance breach is disclosed as a process finding (`S8-CAND-TRACK1-
PROC-001`, Section 5.2), without claim of reversal, with a binding
clean-session requirement for all future verification, and with the file's
digest given no evidentiary status. **The current Track 1 candidate is not
reviewable and is not certifiable until `S8-CAND-TRACK1-GATE-B01` is closed
and this revision itself passes independent re-review; this proposal
authorizes no repair, no Track 2 work, no dataset activity, and no
deployment.**
