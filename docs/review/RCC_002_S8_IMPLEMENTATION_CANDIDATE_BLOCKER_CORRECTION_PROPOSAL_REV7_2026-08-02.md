# RCC-002 S8 Implementation Candidate Blocker Correction Proposal - Revision 7

## Document control

| Field | Value |
|---|---|
| Proposal ID | `RCC-002-S8-CAND-BCP-001-REV7` |
| Proposal date | `2026-08-02` |
| Proposal class | Correction planning and architecture only (read-only diagnosis and design; no implementation, no repair) |
| Revision | `7` (amends Revision 6 Section 6 only; does not reopen Revision 1-5 findings or Revision 6 Sections 2-5) |
| Target artifact | The approved, uncommitted Revision 5 Track 1 candidate (37 files), the untouched prior separate candidate (`rcc002/s8/`, `tests/rcc002/s8/`), and the mandatory `tests/rcc002` gate architecture that must exist, execute, and pass before Track 1 is reviewable |
| Repository branch | `main` |
| Required/verified HEAD | `28cec09fb22a93ff8e3263d85f1f21bcc83d52da` |
| Required/verified `origin/main` | `28cec09fb22a93ff8e3263d85f1f21bcc83d52da` |
| `git diff --cached` at drafting time | Empty (verified before drafting) |
| Superseded proposal section | `docs/review/RCC_002_S8_IMPLEMENTATION_CANDIDATE_BLOCKER_CORRECTION_PROPOSAL_REV6_2026-08-02.md`, Section 6 only (Sections 1-5, 7-12 are restated unchanged, not reopened) |
| Revision 6 SHA-256 (independently recomputed, matches controlling value) | `60ea3152b1446218d7754611f31a9460bb2a94fee3f7395d10dfdedefde30955` |
| Revision 6 line count (independently recomputed) | `529` |
| Controlling Revision 6 re-review | `docs/review/RCC_002_S8_IMPLEMENTATION_CANDIDATE_BLOCKER_CORRECTION_PROPOSAL_REV6_CHATGPT_INDEPENDENT_RE_REVIEW_2026-08-02.md` |
| Revision 6 re-review SHA-256 (independently recomputed, matches controlling value) | `be576d0c3c132602fddcc9196f703c58a8f0b94611152f28d56665cf8d9f082f` |
| Revision 6 re-review decision | `REJECT` |
| Revision 5 SHA-256 (independently recomputed) | `977568eef7b4ea3c09480a0c57f52c1b5a3dfc733e9e019b2468ab9e1fd43b03` |
| Revision 5 re-review SHA-256 (independently recomputed) | `17fc7480c2878cd71fc0ebc29789b05263b904f50702d1192f5a479f8b682f7a` |
| Revision 5 re-review decision | `APPROVE` (of the correction plan only; does not certify Track 1 artifacts) |
| Findings closed by this revision | `S8-CAND-BCP-REV6-B01` (BLOCKER), `S8-CAND-BCP-REV6-B02` (BLOCKER), `S8-CAND-BCP-REV6-ARCH-001` (MAJOR), `S8-CAND-BCP-REV6-TEST-001` (MAJOR) |
| Findings restated, not reopened, not closed by this revision | `S8-CAND-TRACK1-GATE-B01` (BLOCKER; remains open until Section 11's sequence completes and this revision itself is independently re-reviewed and certified), `S8-CAND-TRACK1-PROC-001` (process finding; disclosure and clean-session obligation only, no reversal claimed) |
| Proposal status | **Proposal only. Not approved. Not certified. Does not authorize implementation, Track 2, dataset generation, publication, or deployment.** |

### Protected-file exclusion statement

`scripts/build_rcc002_spec_bundle.py` was not read, hashed, inspected,
opened, executed, imported, copied, renamed, deleted, modified, staged,
packaged, or used as evidence in the preparation of this revision. It
appears in this document only in this explicit exclusion statement, the
process-finding restatement (Section 13), and the restrictions section
(Section 14). Every command run while preparing this revision was checked
against this path before execution; none targeted it.

## 1. Purpose and scope of Revision 7

Revision 6 was independently re-reviewed and **rejected**
(`RCC-002-S8-CAND-BCP-REV6-CHATGPT-IRR-001`, `REJECT`, 2026-08-02). The
re-review's Section 3 confirms that Revision 6's *diagnosis* is correct in
full: the five `tests/rcc002` failures are real and correctly attributed
(Section 3.1 of the re-review), and the four certified predecessor files
(`verify_s8rr002_artifacts.py`, `test_s8rr002_manifest_correction.py`,
`verify_s8rr003_normative_ledger.py`, `test_s8rr003_normative_ledger.py`)
remain byte-identical to their certifying commits and are correctly not
proposed for editing (Section 3.2 of the re-review). Revision 6's Sections
1-5 (purpose, baseline, five-failure evidence table, root-cause analysis,
and the findings `S8-CAND-TRACK1-GATE-B01` and `S8-CAND-TRACK1-PROC-001`)
are therefore **restated unchanged by reference** in this revision and are
not re-derived, re-litigated, or reopened here.

What the re-review rejected is Revision 6 **Section 6**, the proposed
correction architecture, on four grounds: no executable mechanism
redefines what `tests/rcc002` discovery actually runs
(`S8-CAND-BCP-REV6-B01`); the claimed `37 -> 42` / `179 -> 184` transition
contradicts the candidate's own already-hardcoded `37`/`179` verifier
contracts (`S8-CAND-BCP-REV6-B02`); the proposed S8-RR-003 replay omits
required historical inputs and the S8-RR-002 interface was not
demonstrably retargeted (`S8-CAND-BCP-REV6-ARCH-001`); and the gate-scope
declaration had no independent mechanical authority or mutation coverage
(`S8-CAND-BCP-REV6-TEST-001`).

**Revision 7 replaces Revision 6 Section 6 in full** with one selected,
executable, versioned gate architecture (Section 5), an exact historical
replay-root construction for both predecessor suites (Section 6), a
complete recomputed Track 1 and ledger inventory that accounts for every
required modification, not merely an additive file list (Sections 7-8),
an independently hardcoded gate-scope verifier with a full mutation
battery (Sections 9-10), and an explicit acyclic drafting/finalization
sequence (Section 11). This revision does not itself draft, byte-finalize,
create, or modify any of the artifacts it specifies: exactly as Revision 5
Section 6.6 and Revision 6 Section 6.5 were plans, not repairs, this is a
plan, prepared entirely read-only.

## 2. Baseline verified before drafting

The following were independently verified, in this order, before any
analysis began, using only passive read-only commands:

1. `git branch --show-current` returned `main`.
2. `git rev-parse HEAD` and `git rev-parse origin/main` both returned
   `28cec09fb22a93ff8e3263d85f1f21bcc83d52da`.
3. `git diff --cached` returned empty output (nothing staged).
4. `sha256sum` of
   `docs/review/RCC_002_S8_IMPLEMENTATION_CANDIDATE_BLOCKER_CORRECTION_PROPOSAL_REV6_2026-08-02.md`
   returned
   `60ea3152b1446218d7754611f31a9460bb2a94fee3f7395d10dfdedefde30955`,
   matching the controlling value exactly.
5. `sha256sum` of
   `docs/review/RCC_002_S8_IMPLEMENTATION_CANDIDATE_BLOCKER_CORRECTION_PROPOSAL_REV6_CHATGPT_INDEPENDENT_RE_REVIEW_2026-08-02.md`
   returned
   `be576d0c3c132602fddcc9196f703c58a8f0b94611152f28d56665cf8d9f082f`,
   matching the controlling value exactly.
6. `sha256sum` of the Revision 5 proposal and its controlling re-review
   independently recomputed to
   `977568eef7b4ea3c09480a0c57f52c1b5a3dfc733e9e019b2468ab9e1fd43b03` and
   `17fc7480c2878cd71fc0ebc29789b05263b904f50702d1192f5a479f8b682f7a`
   respectively, matching the values Revision 6 itself cites.
7. `git status --short` was inspected in full and shows exactly:
   - `SHA256SUMS` modified (Track 1, unchanged from Revision 5/6);
   - `docs/specifications/RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md`
     modified (Track 1, unchanged);
   - `docs/specifications/RCC_002_REPRODUCIBILITY_AND_MANIFEST_2026-07-23.md`
     modified (Track 1, unchanged);
   - three untracked evidence files under `docs/review/evidence/`
     (`RCC_002_S8CANDBCP_REV2_NORMATIVE_LEDGER_HISTORICAL_COPY_2026-08-01.txt`,
     `RCC_002_S8CANDBCP_REV2_NORMATIVE_LEDGER_SCOPE_V1.json`,
     `RCC_002_S8CANDBCP_REV2_TRACK1_NORMATIVE_SCOPE_V1.json`), unchanged;
   - `rcc002/s8/` (21 files) and `registries/rcc002/views/` (1 file) and
     `schemas/rcc002/manifests/dataset-manifest/1.0.2.schema.json` and
     `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/` (24 files)
     and `tests/rcc002/s8/` (12 files), all untouched, all read-only;
   - `scripts/build_rcc002_spec_bundle.py`, untracked, excluded from all
     analysis;
   - `scripts/rcc002/verify_s8candbcp_rev2_normative_ledger.py`,
     `scripts/rcc002/verify_s8candbcp_rev2_track1_normative_scope.py`,
     `tests/rcc002/test_s8candbcp_rev2_normative_ledger.py`,
     `tests/rcc002/test_s8candbcp_rev2_track1_normative_scope.py`, all
     read for architecture purposes, not modified.
8. `git merge-base --is-ancestor` confirmed both certifying commits
   (`6f0f84087eed666678892f67530287f71c791e1d`,
   `feb0bcccb36f61e9616d9755f286e66e687a2375`) are ancestors of HEAD.
9. `git show 6f0f840:docs/specifications/RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md
   | sha256sum` = `0e060d30b75082b74eb5211b1d378837aa7872d86f62e5e162586e2a2cc37fad`;
   `git show 6f0f840:docs/specifications/RCC_002_REPRODUCIBILITY_AND_MANIFEST_2026-07-23.md
   | sha256sum` = `23fd2fc0a0338124e9bbd9d95bf6797662d1e32012cb6247763e47a47bf61cf1`.
   The same two commands run against `feb0bcc` return the identical two
   digests; `git diff 6f0f840 feb0bcc -- <DP path> <RM path>` is empty.
   Both certifying commits therefore share byte-identical DP and RM text,
   and a single frozen copy of each, sourced from either commit, serves
   both predecessor suites' replay needs.
10. `git diff feb0bcc HEAD -- SHA256SUMS` is empty: the committed root
    ledger is unchanged since S8-RR-003's certification and still holds
    exactly 145 entries (`git show HEAD:SHA256SUMS | wc -l` = `145`).
    `git show HEAD:SHA256SUMS | sha256sum` =
    `469236e8459a9ad86d3434a67a81f037a699e076c6a8af8b0a887ecb60a30302`,
    identical to `sha256sum` of the existing uncommitted evidence file
    `docs/review/evidence/RCC_002_S8CANDBCP_REV2_NORMATIVE_LEDGER_HISTORICAL_COPY_2026-08-01.txt`
    and to the `HISTORICAL_LEDGER_SHA256`... no -- to the certified
    145-entry committed ledger digest (not to be confused with the
    110-entry `HISTORICAL_LEDGER_SHA256` constant inside
    `verify_s8rr003_normative_ledger.py`, which is a different, older
    bundle; both are accounted for separately in Section 6.3).
11. `git diff feb0bcc HEAD --stat` over `docs/specifications`,
    `docs/review/evidence`, `registries`, `schemas`, `scripts/rcc002`,
    and the S8-RR-002/S8-RR-003 test files shows only new files added
    after `feb0bcc` (the Revision 1-6 proposal/re-review documents); no
    byte of any of the 145 certified target paths was modified at the
    committed-HEAD level between `feb0bcc` and `28cec09`, other than the
    two Track 1 modifications (DP, RM) present only in the working tree,
    uncommitted.
12. `sha256sum` of the six other `NON_SELF_SPECIFICATIONS` documents
    (`RCC-002-DV`, `RCC-002-IS`, `RCC-002-ST`, `RCC-002-RG`,
    `RCC-002-LF`, and DP itself) was not independently recomputed a
    second time in this section beyond item 9 above (DP); the other five
    are unchanged since `6f0f840` per item 11's directory-level diff and
    remain subject to the same hash-gate the certified verifier itself
    applies at replay time (Section 6.2).
13. The local `.venv` was checked, informationally, for `jsonschema`:
    version `4.26.0` is installed, exactly the pinned
    `REQUIRED_JSONSCHEMA_VERSION` the certified S8-RR-002 verifier and
    test module require. The S8-RR-002 replay adapter (Section 6.2) is
    therefore not environment-skipped in this repository's own `.venv`.

No repository file was modified by any command above. No test suite was
executed. `scripts/build_rcc002_spec_bundle.py` was never named as an
argument to any command.

## 3. Restated from Revision 6 (unchanged, not reopened)

- **`S8-CAND-TRACK1-GATE-B01` (BLOCKER).** The mandatory complete
  `tests/rcc002` gate fails 5/908 because the certified S8-RR-002
  (`6f0f840`) and S8-RR-003 (`feb0bcc`) predecessor verifier/test pairs
  validate the live repository tree with no versioned or frozen input, and
  therefore necessarily diverge from their own certified literal
  expectations once Track 1's authorized DP/RM/ledger advancement is
  applied to the same live paths those pairs read. This renders the
  current Track 1 candidate **not reviewable and not certifiable**. This
  finding is not closed by this revision; it is closed only once Section
  11's sequence completes, the gate in Section 5 is run and reported
  green, and this revision itself passes independent re-review (Section
  12).
- **`S8-CAND-TRACK1-PROC-001` (process finding, disclosure).** Restated
  in full in Section 13, unchanged in substance from Revision 6 Section
  5.2: an earlier protected-builder compliance breach involving
  `scripts/build_rcc002_spec_bundle.py` is disclosed, without claim of
  reversal, with a binding clean-session requirement, and with the file's
  digest given no evidentiary status in this or any future revision.
- The five-failure evidence table, root-cause analysis, and "what this is
  not" clarifications (Revision 6 Sections 3-4) are correct as
  independently re-confirmed by the controlling re-review (Section 3 of
  the re-review) and are not reproduced a second time in this document;
  they remain the evidentiary basis for `S8-CAND-TRACK1-GATE-B01` above.

## 4. Closure mapping for the four Revision 6 re-review findings

| Finding | Severity | Revision 6 gap | Revision 7 closure section |
|---|---|---|---|
| `S8-CAND-BCP-REV6-B01` | BLOCKER | No executable routing mechanism; a JSON declaration and two added tests do not change what `unittest discover` executes. | Section 5 (single selected executable gate architecture, exact command, exact rejection rules) |
| `S8-CAND-BCP-REV6-B02` | BLOCKER | The claimed `37 -> 42` / `179 -> 184` transition contradicted the unchanged hardcoded `37`/`179` Track 1 and ledger scope-verifier contracts. | Section 7 (exact inventory, distinguishing repository classification from byte changes), Section 8 (recomputed counts and arithmetic) |
| `S8-CAND-BCP-REV6-ARCH-001` | MAJOR | The S8-RR-003 replay lacked the full historical target tree the certified verifier's `run_verification` actually reads; the S8-RR-002 interface (module-level `REPO` constant) was not demonstrably retargeted. | Section 6 (exact deterministic replay-root construction for both predecessor suites, with provenance and hash checks for every replayed file) |
| `S8-CAND-BCP-REV6-TEST-001` | MAJOR | The gate-scope declaration was unauthenticated policy: no independent hardcoded consumer, no exact-schema verifier, no mutation-test contract. | Section 9 (gate-scope schema and independent verifier authority), Section 10 (twelve-case mutation-test requirement) |

Every row is closed by an exact decision in the section cited, not by a
restatement of the requirement.

## 5. Selected executable gate architecture

Exactly one gate architecture is selected below. No alternative is
offered. This architecture is a cross-cutting redefinition of what "the
mandatory `tests/rcc002` gate is green" means for this correction family;
per this repository's working rules ("architecture authority is never
self-granted"; Section 12), it is **proposed** here and requires
independent re-review and, separately, certification before adoption. It
does not take effect merely by this document existing.

### 5.1 Naming

The new gate authority is named `RCC-002-S8-CAND-BCP-001-REV7-GATE-V1`.
It is deliberately not named with the `REV2` artifact-family tag already
used by the Track 1 and ledger scope manifests/verifiers (Section 7),
because it is a new, third governed sub-system within this correction
family (after the Track 1 scope contract and the ledger scope contract),
introduced at proposal Revision 7, not a revision of either existing one.

### 5.2 Exact authoritative command

```text
PYTHONDONTWRITEBYTECODE=1 python3 scripts/rcc002/run_s8candbcp_gate.py
```

This single command, run from the repository root, **replaces**

```text
python -m unittest discover -s tests/rcc002 -p "test_*.py"
```

as the authoritative statement of "the mandatory `tests/rcc002` gate is
green" for this correction family, effective only once this architecture
is independently re-reviewed, certified, and the governance update in
Section 5.9 is made. Flat discovery remains physically runnable at any
time (nothing removes it, and no certified file is edited), but it is, as
of this proposal, explicitly **not** the authoritative gate: it has no
mechanism to exclude the two historical-audit-only modules (Section 5.3)
from its aggregate result, so it necessarily remains red after any
authorized future advancement of DP, RM, or the root ledger, by the exact
structural mechanism Revision 6 Section 4.2 already diagnosed. This is a
property of flat discovery itself, not a defect newly introduced by
Revision 7, and it is not required to turn green for Track 1 to be
reviewable once the gate above is adopted.

### 5.3 Exact module partition

Every `test_*.py` module reachable under `tests/rcc002/` (recursive,
including the untouched prior candidate under `tests/rcc002/s8/`) belongs
to exactly one of three categories. `find tests/rcc002 -name "test_*.py"`
independently enumerates exactly `57` such modules today; Revision 7 adds
`3` new ones (Section 7), for an exact total of `60`.

1. **`current_state`** (`56` modules after Revision 7): every module that
   validates the live/current repository tree and must pass against it.
   This is every existing module under `tests/rcc002/` **except** the two
   named in category 3 below, plus the one new gate-scope mutation-test
   module this revision adds (Section 7, item `test_s8candbcp_gate_scope.py`).
2. **`historical_replay_adapter`** (`2` modules): the two new replay
   adapters this revision adds (Section 6):
   `tests/rcc002/test_s8rr002_manifest_correction_historical_replay.py`
   and
   `tests/rcc002/test_s8rr003_normative_ledger_historical_replay.py`.
   These run against the live tree's own source files, but internally
   construct and validate against a frozen, isolated historical replay
   root (Section 6); they are current-tree code, listed separately only
   because they are the mandatory-gate's substitute obligation for
   category 3.
3. **`historical_audit_only`** (`2` modules, byte-identical, unmodified,
   certified): `tests/rcc002/test_s8rr002_manifest_correction.py` and
   `tests/rcc002/test_s8rr003_normative_ledger.py`. These remain present,
   unmodified, and directly runnable (Section 5.8), but are **not** loaded
   into the authoritative gate's test suite by `run_s8candbcp_gate.py`
   (Section 5.6): there is no code path in that script that references
   either module's dotted name, so they cannot be run by the gate, by
   omission, not by a bypassable flag.

`56 + 2 + 2 = 60`, matching the exact enumerated total.

### 5.4 Gate-scope manifest

New file, exact path
`docs/review/evidence/RCC_002_S8CANDBCP_GATE_SCOPE_V1.json`. Exact
top-level keys (no more, no fewer):

```text
scope_schema_version            "1"
scope_id                        "RCC002_S8CANDBCP_GATE_SCOPE_V1"
correction_id                   "RCC-002-S8-CAND-BCP-001-REV7"
gate_id                         "RCC-002-S8-CAND-BCP-001-REV7-GATE-V1"
findings_in_scope                ["S8-CAND-BCP-REV6-B01", "S8-CAND-BCP-REV6-TEST-001"]
authoritative_command            "PYTHONDONTWRITEBYTECODE=1 python3 scripts/rcc002/run_s8candbcp_gate.py"
path_ordering                    "LC_ALL=C lexical order, repository-relative POSIX paths"
test_root                        "tests/rcc002"
expected_total_modules           60
expected_current_state_count     56
expected_historical_replay_adapter_count   2
expected_historical_audit_only_count       2
current_state_modules            [ ...56 entries, LC_ALL=C order... ]
historical_replay_adapter_modules [ ...2 entries, LC_ALL=C order... ]
historical_audit_only_modules    [ ...2 entries, LC_ALL=C order... ]
```

The exact `56`-entry `current_state_modules` list, the exact `2`-entry
`historical_replay_adapter_modules` list, and the exact `2`-entry
`historical_audit_only_modules` list are given in Section 5.3 and Section
7; they are not repeated a third time here in prose.

### 5.5 Independent gate-scope verifier

New file, exact path `scripts/rcc002/verify_s8candbcp_gate_scope.py`.
Mirrors the existing, uncommitted Track 1 and ledger scope-verifier
pattern (`scripts/rcc002/verify_s8candbcp_rev2_track1_normative_scope.py`,
`scripts/rcc002/verify_s8candbcp_rev2_normative_ledger.py`): independent
hardcoded `EXPECTED_TOTAL_MODULES = 60`, `EXPECTED_CURRENT_STATE = 56`,
`EXPECTED_HISTORICAL_REPLAY_ADAPTER = 2`,
`EXPECTED_HISTORICAL_AUDIT_ONLY = 2`, and three hardcoded exact tuples
(one per category, in strict `LC_ALL=C` order), compared with exact list
equality against three independent sources: (1) the hardcoded tuples
themselves (self-check), (2) the gate-scope manifest file (Section 5.4),
and (3) a bounded, scoped enumeration of the actual `tests/rcc002/`
subtree on disk. Unlike the certified S8-RR-002/S8-RR-003 verifiers' "no
`rglob`" idiom (which exists to avoid unscoped *whole-repository*
traversal), this verifier's entire purpose is to enumerate one named
subtree exhaustively; its traversal is therefore intentionally bounded to
exactly `tests/rcc002/` and nothing else, with every discovered entry
checked for symlinks and unsafe path components before being compared.

Exact rejection classes, each raising a distinct
`GateScopeVerificationError` before any test is loaded or run:

- `gate_scope_unknown_module`: a `test_*.py` file exists on disk under
  `tests/rcc002/` that is not present in the union of all three hardcoded
  categories (this is the mechanism that satisfies "newly added test
  modules cause fail-closed inventory rejection until explicitly
  reviewed": a new test file added without updating this verifier and its
  manifest is neither silently run nor silently ignored -- the gate
  refuses to execute anything until the omission is resolved);
- `gate_scope_missing_module`: a module hardcoded or manifest-declared in
  any category is absent from disk;
- `gate_scope_duplicate_module`: the same module path appears in more
  than one category, or twice within one category;
- `gate_scope_reordered_category`: any category's list, hardcoded or
  manifest-declared, is not in strict `LC_ALL=C` order;
- `gate_scope_unsafe_path`: any declared or discovered path is absolute,
  contains `..`, contains a backslash, or resolves (via `os.path.islink`)
  to a symlink;
- `gate_scope_misclassified_module`: a module physically present under
  `tests/rcc002/s8/` or elsewhere is declared in a category inconsistent
  with Section 5.3's fixed assignment (for example, either of the two
  certified predecessor modules declared as `current_state`, or any
  `current_state` module declared as `historical_audit_only`);
- `gate_scope_extra_top_level_key` / `gate_scope_missing_top_level_key`:
  the manifest's key set is not exactly the Section 5.4 set;
- `gate_scope_manifest_mismatch`: the manifest's declared lists do not
  equal the hardcoded tuples, entry-for-entry.

### 5.6 Executable gate runner

New file, exact path `scripts/rcc002/run_s8candbcp_gate.py`. Sets
`sys.dont_write_bytecode = True` at import time (defense in depth; the
authoritative command in Section 5.2 also sets the environment variable).
Exact execution semantics:

1. Import `verify_s8candbcp_gate_scope` and run its full verification. If
   it raises, print the failed invariant and exit non-zero. **No test
   module is loaded or executed if this step fails.**
2. Build one `unittest.TestSuite` by calling
   `unittest.defaultTestLoader.loadTestsFromName(name)` exactly once for
   each of the `56` `current_state` dotted module names and exactly once
   for each of the `2` `historical_replay_adapter` dotted module names --
   `58` `loadTestsFromName` calls in total, each against a distinct name
   drawn from a set step 1 has already proven has no duplicate and no
   unknown or misclassified entry. Every in-scope module therefore
   executes exactly once, by construction: the scope verifier proves the
   name set is exact and duplicate-free, and the loader is called exactly
   once per name.
3. The `2` `historical_audit_only` dotted names are never passed to
   `loadTestsFromName` anywhere in this script. There is no flag, no
   commented-out call, and no conditional path that would include them;
   their exclusion is structural, not configurable.
4. Run the suite with `unittest.TextTestRunner`, and exit `0` only if
   every loaded test passes; otherwise exit non-zero with the standard
   `unittest` failure/error summary.

### 5.7 Historical-audit preservation

The two historical-audit-only modules remain physically present,
byte-identical, and directly runnable at any time, unaffected by this
architecture:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.rcc002.test_s8rr002_manifest_correction -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.rcc002.test_s8rr003_normative_ledger -v
```

Both commands remain expected to fail against the live tree after Track
1's authorized DP/RM/ledger advancement, by the exact mechanism Revision
6 Section 4.2 diagnosed; that failure is historical fact, not a
regression, and is never counted toward the Section 5.2 authoritative
gate.

### 5.8 Rejection summary (cross-reference)

The exact rejection classes for missing, extra, duplicate, reordered,
unsafe, unknown, or misclassified modules are given in Section 5.5; this
is the single, complete list satisfying the Section 4
`S8-CAND-BCP-REV6-B01` disposition item 5 and the
`S8-CAND-BCP-REV6-TEST-001` disposition's category-coverage requirement,
cross-checked against Section 10's mutation-test battery.

### 5.9 Required governance/documentation update

`CLAUDE.md`, as it stands at HEAD `28cec09`, does not mention RCC-002,
`tests/rcc002`, or any flat-discovery command anywhere (independently
confirmed: zero matches for `rcc002` in `CLAUDE.md`). The flat-discovery
command's de facto "authoritative" status for this correction family
comes instead from its repeated, informal use across roughly twenty prior
`docs/review/` and `docs/certification/` records (S5-S8 implementation
records, corrected re-reviews, and certification decisions) and from
Revision 6 Section 2's own characterization of it as run "per this
repository's ordinary validation discipline." No single existing
governance document makes a binding normative claim that this exact
command is authoritative; the risk is that, absent a written correction,
a future session (including a future Claude Code session reading
`CLAUDE.md`) would keep defaulting to it by convention alone.

**Required disposition, once this architecture is independently
re-reviewed and certified (not by this proposal itself):**
`CLAUDE.md`'s `## Commands` section must gain one new entry naming
`PYTHONDONTWRITEBYTECODE=1 python3 scripts/rcc002/run_s8candbcp_gate.py`
as the authoritative RCC-002 S8 correction-family gate, and explicitly
noting that flat `unittest discover -s tests/rcc002 -p "test_*.py"` is
retained only for ad hoc/historical-audit use and is expected to remain
red for this family after any authorized DP/RM/ledger advancement. Until
that `CLAUDE.md` update is made, this Revision 7 document itself is the
interim authoritative statement of which command governs this family's
gate, exactly as Revision 5 Section 6.4 and Revision 6 Section 6.4 were
each, in their turn, the interim authoritative statement of their own
narrower redefinitions before any adoption.

## 6. Historical replay architecture for both predecessor suites

Both replay mechanisms below construct an isolated directory outside the
repository (`tempfile.mkdtemp()` or `tempfile.TemporaryDirectory()`, never
under the repository root), populate it exclusively with files whose
bytes are independently verified against a certified digest before being
written, run the certified predecessor pair against that isolated root
only, and delete the directory afterward. Neither certified file
(`verify_s8rr002_artifacts.py`, `test_s8rr002_manifest_correction.py`,
`verify_s8rr003_normative_ledger.py`, `test_s8rr003_normative_ledger.py`)
is read from, or executed against, the live repository tree by either
adapter; both are copied byte-for-byte into the isolated root and, in the
S8-RR-003 case, additionally invoked directly in-process against that
root's path.

### 6.1 Shared provenance facts

- S8-RR-002 certifying commit: `6f0f84087eed666678892f67530287f71c791e1d`
  ("Certify RCC-002 S8 manifest corrections").
- S8-RR-003 certifying commit: `feb0bcccb36f61e9616d9755f286e66e687a2375`
  ("Certify RCC-002 S8 normative-ledger correction").
- Data Pipeline text is byte-identical at both commits, SHA-256
  `0e060d30b75082b74eb5211b1d378837aa7872d86f62e5e162586e2a2cc37fad`.
- Reproducibility and Manifest text is byte-identical at both commits,
  SHA-256 `23fd2fc0a0338124e9bbd9d95bf6797662d1e32012cb6247763e47a47bf61cf1`.
- A single frozen pair, sourced via `git show 6f0f840:<path>` (item
  `RCC_002_S8RR002_HISTORICAL_DATA_PIPELINE_SPECIFICATION_0_8_0_CERTIFIED_COPY_2026-08-02.txt`
  and
  `RCC_002_S8RR002_HISTORICAL_REPRODUCIBILITY_AND_MANIFEST_0_9_0_CERTIFIED_COPY_2026-08-02.txt`,
  Section 7), therefore correctly serves both predecessor suites' need
  for frozen DP and RM bytes; no second frozen copy at `feb0bcc` is
  required or created.
- Every other file either predecessor suite reads is, at the committed-HEAD
  level, unchanged since its own certifying commit (Section 2, item 11):
  it is therefore safe to source such a file's bytes from the current
  working tree, provided its hash is checked against the certified digest
  (either a literal already hardcoded in the certified verifier itself, or
  the digest recorded in the certified 145-entry root ledger) immediately
  before it is written into the isolated replay root, and the read fails
  closed on any mismatch.

### 6.2 S8-RR-002 replay adapter

New file, exact path
`tests/rcc002/test_s8rr002_manifest_correction_historical_replay.py`.

**Why a full isolated root, not "import pure functions."** Both
`scripts/rcc002/verify_s8rr002_artifacts.py` and
`tests/rcc002/test_s8rr002_manifest_correction.py` compute
`REPO = Path(__file__).resolve().parents[2]` as a module-level constant
derived from each file's own on-disk location, and every other path
constant (`SCOPE_PATH`, `RM_PATH`, `DATA_PIPELINE_PATH`,
`DATASET_MANIFEST_SCHEMA_PATH`, `FIXTURE_ROOT`, `NEGATIVE_ROOT`) is
derived from that `REPO` constant. Neither `REPO` nor any function in
either file accepts a repository-root parameter. Importing the module and
monkeypatching `REPO` after import (as the certified module's own
mutation tests do, in-process, for narrow unit-level assertions) does not
retarget the *test class's own* `RM_PATH`/`DP_PATH`/etc. class
attributes, which are computed independently at class-body evaluation
time from the *test file's* `REPO`. The only mechanism that retargets
every hardcoded path read by both files simultaneously, without editing
either byte-for-byte, is to place byte-identical copies of both files at
their correct relative locations inside a fabricated root, so that each
file's own `Path(__file__).resolve().parents[2]` naturally resolves to
that root.

**Exact construction, every step read-only against the live tree except
the final writes into the isolated temporary directory:**

1. Create `tmp = tempfile.mkdtemp(prefix="rcc002_s8rr002_replay_")`
   outside the repository.
2. Copy, byte-for-byte, the live (certified, unmodified) files
   `scripts/rcc002/verify_s8rr002_artifacts.py` to
   `tmp/scripts/rcc002/verify_s8rr002_artifacts.py` and
   `tests/rcc002/test_s8rr002_manifest_correction.py` to
   `tmp/tests/rcc002/test_s8rr002_manifest_correction.py`. Before copying,
   hash each and require the result equals the value independently
   recomputed in Section 2, item 7 of Revision 6's own re-review
   (`2c67bfddc0b99a3a07497240a2e6c26dbc2dd41674ade898eb00b25ef38d9335` and
   `2b977dc2952058ee1381723332786fcd252534c0a8de560c64af932fb46abaf4`
   respectively); fail before copying on any mismatch.
3. Write the frozen DP copy (Section 6.1) to
   `tmp/docs/specifications/RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md`
   and the frozen RM copy to
   `tmp/docs/specifications/RCC_002_REPRODUCIBILITY_AND_MANIFEST_2026-07-23.md`,
   each re-hashed against the two Section 6.1 literals immediately before
   the write.
4. For each of the remaining `39` files the certified verifier's own
   `EXPECTED_IMMUTABLE_REFERENCE_INPUTS` (`11` entries) and
   `EXPECTED_CANDIDATE_OUTPUTS` (`30` entries) declare -- the five other
   `NON_SELF_SPECIFICATIONS` documents, the S8-RR-002 proposal document,
   `requirements-rcc002-review.txt`, the `1.0.0` and `1.0.1` Dataset
   Manifest schemas, the Stage Manifest `1.0.0` schema, the `1.0.0` and
   `1.0.1` fixture families (positive, negative, and `CASE_LEDGER.json`),
   and the scope manifest itself -- read the live working-tree bytes,
   hash each, and require the digest equal either (a) the literal already
   hardcoded in the certified verifier for that exact path (the six
   `NON_SELF_SPECIFICATIONS` hashes and the four
   `EXPECTED_IMMUTABLE_HASHES` entries), or (b) the digest recorded for
   that exact path in the certified 145-entry root ledger (Section 6.3),
   for every file the verifier's own literals do not separately pin. Fail
   before writing on any mismatch. On success, write the verified bytes
   to the identical relative path under `tmp/`.
5. Invoke, via `subprocess.run([sys.executable,
   "tests/rcc002/test_s8rr002_manifest_correction.py"], cwd=tmp,
   env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}, capture_output=True)`.
   Because the copied test file's own `REPO = Path(__file__).resolve().parents[2]`
   now resolves to `tmp`, every one of its hardcoded relative reads
   targets the isolated root, not the live repository.
6. **Positive control**: assert the subprocess exit code is `0` and its
   captured stdout/stderr shows every certified test method passing
   (`OK` summary; no `FAIL`/`ERROR`), reproducing the original certified
   assertions end-to-end against frozen history.
7. **Negative control**: repeat steps 1-5 with one substitution -- the
   live working-tree Data Pipeline text (post-Track-1, version `0.9.0`)
   is written in place of the frozen `0.8.0` copy at step 3 -- and assert
   the subprocess exits non-zero with output containing
   `does not match Revision 2 literal hash`, proving the adapter is
   genuinely pinned to history and would fail, not silently pass, if it
   ever degraded into re-testing the live tree.
8. Delete `tmp` (`shutil.rmtree`) in a `finally`/`addCleanup` block
   regardless of outcome. No file under `tmp` is ever written back into
   the repository.
9. `scripts/build_rcc002_spec_bundle.py` is never named, read, or copied
   anywhere in this adapter.

### 6.3 S8-RR-003 replay adapter

New file, exact path
`tests/rcc002/test_s8rr003_normative_ledger_historical_replay.py`.

**Why importing the pure function is sufficient here.**
`scripts/rcc002/verify_s8rr003_normative_ledger.py`'s `run_verification(repo_root)`
takes `repo_root` as an explicit parameter, and every file it reads --
`LEDGER_PATH`, `SCOPE_MANIFEST_PATH`, `HISTORICAL_EVIDENCE_PATH`, and
every one of the `145` `CURRENT_LEDGER_PATHS` targets -- is joined against
that parameter with `os.path.join(repo_root, ...)`. Calling
`run_verification(tmp)` therefore demonstrably retargets every hardcoded
read this module performs, without editing one byte of the certified
module, exactly as `S8-CAND-BCP-REV6-ARCH-001`'s required disposition
permits ("do not merely say 'import pure functions' unless every
hardcoded path read is demonstrably retargeted" -- here it is,
parameter-by-parameter). This module is loaded via
`importlib.util.spec_from_file_location`, exactly as the certified
`test_s8rr003_normative_ledger.py` already loads it in-process; the
adapter is not a second, different loading mechanism.

**Exact construction:**

1. Create `tmp = tempfile.mkdtemp(prefix="rcc002_s8rr003_replay_")`
   outside the repository.
2. Load the certified verifier module via `importlib.util.spec_from_file_location`
   against the live, unmodified
   `scripts/rcc002/verify_s8rr003_normative_ledger.py` (hash-checked
   first against `48c92bae7c8b5bd51c965fcd48917ffe0a3ee84c9dfe32bd490abab88f9b6cea`,
   the value independently recomputed in Revision 6's re-review Section
   2, item 7). Importing, not editing, this certified file.
3. Reconstruct, at `tmp/SHA256SUMS`, the certified `145`-entry ledger
   exactly as it stood at `feb0bcc`: this is byte-identical to the
   already-existing, unmodified Track 1 evidence file
   `docs/review/evidence/RCC_002_S8CANDBCP_REV2_NORMATIVE_LEDGER_HISTORICAL_COPY_2026-08-01.txt`
   (independently confirmed in Section 2, item 10, to hash to
   `469236e8459a9ad86d3434a67a81f037a699e076c6a8af8b0a887ecb60a30302`,
   identical to `git show HEAD:SHA256SUMS`); copy it verbatim, re-hashed
   before the copy.
4. Copy, to `tmp/docs/review/evidence/RCC_002_S8RR003_NORMATIVE_LEDGER_SCOPE_V1.json`,
   the live, tracked, unmodified scope manifest (confirmed unchanged
   since `feb0bcc` in Section 2, item 11), re-hashed against the digest
   recorded for that path in the `145`-entry ledger from step 3 before
   the copy.
5. For each of the other `143` paths declared in the certified
   `CURRENT_LEDGER_PATHS` tuple (the `145`-entry union minus the ledger's
   own two already-handled special files is not the right count -- the
   ledger does not list itself, so all `145` declared target paths,
   including the scope manifest from step 4 and the `110`-entry
   historical-evidence bundle from step 6, are targets; step 4 and step 6
   are singled out here only because they are separately read by name
   before the generic target-hashing pass): read the live working-tree
   bytes (or, for Data Pipeline and RM, the two Section 6.1 frozen
   copies), hash each, require the digest equal the value recorded for
   that exact path in the step-3 ledger, and fail before copying on any
   mismatch. Write verified bytes to the identical relative path under
   `tmp/`.
6. Copy, to
   `tmp/docs/review/evidence/RCC_002_S8BCP001_REV2_NORMATIVE_BUNDLE_SHA256SUMS_2026-07-30.txt`,
   the live, tracked, unmodified `110`-entry historical-evidence bundle
   (confirmed unchanged since `feb0bcc` in Section 2, item 11), re-hashed
   against the certified verifier's own hardcoded
   `HISTORICAL_LEDGER_SHA256` literal
   (`a34e5139dadfdfa9d72210ac12b733b0493b00c8396f8e48680634dfb5988e43`)
   before the copy.
7. Call `verifier_module.run_verification(tmp)` directly, in-process (no
   subprocess needed; the function is already parameterized).
8. **Positive control**: assert the returned dict has
   `result == "PASS"`, `historical_entry_count == 110`,
   `s8rr002_output_count == 30`, `s8rr003_output_count == 6`,
   `current_ledger_entry_count == 145`,
   `current_rm_sha256 == "23fd2fc0a0338124e9bbd9d95bf6797662d1e32012cb6247763e47a47bf61cf1"`
   -- reproducing every field the certified
   `Case01ValidPositiveControl.test_full_repo_state_passes` and
   `ResourceHandlingRegression.test_no_resource_warning_on_successful_run`
   assert, against frozen history instead of the live tree.
9. **Negative control**: build a second temporary root identically,
   except substitute the live, post-Track-1 working-tree `SHA256SUMS`
   (`179` entries at Revision 5/6 draft time) for the step-3 file; assert
   `verifier_module.run_verification(tmp2)` raises `VerificationError`
   with `invariant == "current_ledger_count_mismatch"` -- the exact
   failure mode Revision 6 Section 3 (table row 1-2) reported against the
   live tree, now reproduced deliberately as proof the adapter
   distinguishes frozen history from the live tree rather than silently
   accepting either.
10. Delete both temporary roots in `finally`/`addCleanup` blocks
    regardless of outcome.
11. `scripts/build_rcc002_spec_bundle.py` is never named, read, or copied
    anywhere in this adapter.

### 6.4 Common constraints (both adapters)

- Both adapters run with `PYTHONDONTWRITEBYTECODE=1` (set in the
  environment for the Section 6.2 subprocess call; set at the process
  level, per Section 5.6, for the Section 6.3 in-process call).
- Both adapters use only `tempfile`-created directories outside the
  repository; neither ever creates a file, a `__pycache__` directory, or
  any other artifact inside the repository.
- Both adapters reproduce every original certified assertion end-to-end
  (Section 6.2 via subprocess exit code and captured output; Section 6.3
  via the returned result dict's exact fields), not a reimplemented
  subset.
- Neither adapter reads, hashes, imports, executes, or otherwise
  references `scripts/build_rcc002_spec_bundle.py` at any point.
- Neither adapter edits, in any way, the four certified files it copies
  or imports; both are read-only sources for the copy/import operations
  described above.

## 7. Exact new and changed artifact inventory (`LC_ALL=C` order)

### 7.1 Eight new artifacts introduced by Revision 7

Numbered continuing from Revision 5's 1-37 (Revision 6's rejected items
38-42 are superseded in full and do not exist in this revision's
inventory):

38. `docs/review/evidence/RCC_002_S8CANDBCP_GATE_SCOPE_V1.json` -- NEW
    (Section 5.4)
39. `docs/review/evidence/RCC_002_S8RR002_HISTORICAL_DATA_PIPELINE_SPECIFICATION_0_8_0_CERTIFIED_COPY_2026-08-02.txt`
    -- NEW (Section 6.1/6.2)
40. `docs/review/evidence/RCC_002_S8RR002_HISTORICAL_REPRODUCIBILITY_AND_MANIFEST_0_9_0_CERTIFIED_COPY_2026-08-02.txt`
    -- NEW (Section 6.1/6.2)
41. `scripts/rcc002/run_s8candbcp_gate.py` -- NEW (Section 5.6)
42. `scripts/rcc002/verify_s8candbcp_gate_scope.py` -- NEW (Section 5.5)
43. `tests/rcc002/test_s8candbcp_gate_scope.py` -- NEW (Section 10)
44. `tests/rcc002/test_s8rr002_manifest_correction_historical_replay.py`
    -- NEW (Section 6.2)
45. `tests/rcc002/test_s8rr003_normative_ledger_historical_replay.py` --
    NEW (Section 6.3)

None of these 8 paths collides with any of the 145 baseline ledger
entries or any of the 34 Revision 5 additions; all 8 are novel paths,
independently confirmed absent from every list read during this revision.

### 7.2 Five existing draft artifacts whose bytes change again

**Repository classification relative to committed HEAD is unchanged for
all five**: none of them is tracked at HEAD `28cec09`; all five remain
`NEW` (untracked, uncommitted) both before and after this revision, exactly
as they were under Revision 5 and Revision 6. **What changes is their
byte content relative to the Revision 5/6 candidate's own already-drafted
text**, because none of the five has ever been byte-finalized, verified,
reviewed, or certified (Track 1 remains, throughout Revisions 5, 6, and
7, in the "not reviewable, not certifiable" state of Section 3): editing
an un-finalized draft again is not a violation of "once byte-finalized,
never edited" (Revision 5 Section 6.6's governing rule), because none of
these five has ever reached that state.

1. `docs/review/evidence/RCC_002_S8CANDBCP_REV2_TRACK1_NORMATIVE_SCOPE_V1.json`
   -- add the 8 Section 7.1 entries to `entries[]`; `total_entries`
   `37 -> 45`; `new_entries` `34 -> 42`; `modified_entries` unchanged at
   `3`; `findings_in_scope` gains
   `S8-CAND-BCP-REV6-B01`, `S8-CAND-BCP-REV6-B02`,
   `S8-CAND-BCP-REV6-ARCH-001`, `S8-CAND-BCP-REV6-TEST-001`;
   `correction_id` `RCC-002-S8-CAND-BCP-001-REV5` ->
   `RCC-002-S8-CAND-BCP-001-REV7` (the file name's `REV2` artifact-family
   tag is unchanged; only the internal `correction_id` metadata field,
   which tracks the most recent revision to touch this artifact's
   contract, is updated, exactly as Revision 5 already updated fields
   last touched by an earlier revision without renaming the file).
2. `scripts/rcc002/verify_s8candbcp_rev2_track1_normative_scope.py` --
   `EXPECTED_TOTAL` `37 -> 45`; `EXPECTED_NEW` `34 -> 42`;
   `EXPECTED_MODIFIED` unchanged at `3`; `EXPECTED_ENTRIES` gains the 8
   Section 7.1 tuples, inserted at their correct `LC_ALL=C` positions
   (Section 7.3); `CORRECTION_ID` updated as in item 1.
3. `docs/review/evidence/RCC_002_S8CANDBCP_REV2_NORMATIVE_LEDGER_SCOPE_V1.json`
   -- `added_entry_count` `34 -> 42`; `successor_entry_count`
   `179 -> 187`; `baseline_entry_count` unchanged at `145`;
   `removed_entry_count` unchanged at `0`; `replaced_entry_count`
   unchanged at `2`; `entries[]` gains the 8 Section 7.1 paths,
   `./`-prefixed, inserted at their correct `LC_ALL=C` positions;
   `correction_id` updated as in item 1.
4. `scripts/rcc002/verify_s8candbcp_rev2_normative_ledger.py` --
   `EXPECTED_ADDED` `34 -> 42`; `EXPECTED_SUCCESSOR` `179 -> 187`;
   `EXPECTED_BASELINE`, `EXPECTED_REMOVED`, `EXPECTED_REPLACED` unchanged
   at `145`, `0`, `2` respectively; `CORRECTION_ID` updated as in item 1.
5. `tests/rcc002/test_s8candbcp_rev2_normative_ledger.py` -- one-line
   docstring correction: "so these tests never depend on the real
   179-entry successor ledger existing yet" -> "...real 187-entry
   successor ledger...". Independently confirmed (full read of this
   file) that **no other line requires a change**: every arithmetic case
   in this file patches `verifier.EXPECTED_BASELINE/ADDED/REMOVED/REPLACED/SUCCESSOR`
   to a synthetic `3`/`1`/`0`/`1`/`4` scale in `setUp`/`tearDown` and
   never depends on the real `145`/`179`/`187` values; only the prose
   comment names the real count.

**One existing draft artifact requires no byte change at all**:
`tests/rcc002/test_s8candbcp_rev2_track1_normative_scope.py`, independently
confirmed (full read) to reference every expected count exclusively via
`verifier.EXPECTED_TOTAL`/`verifier.EXPECTED_ENTRIES`/`verifier.SCOPE_ID`
dynamically, with zero literal occurrence of `37`, `34`, `42`, or `45`
anywhere in its text. It is reused byte-identical, and is listed in
Section 7.4's total only because it is still part of the Track 1
inventory, not because it changes.

### 7.3 Complete 45-entry Track 1 inventory, exact `LC_ALL=C` order

Independently computed by merging Revision 5 Section 8.2's 37 entries
with Section 7.1's 8 new entries and sorting the union in strict
`LC_ALL=C` byte order over the full repository-relative path string.

 1. `SHA256SUMS` -- MODIFIED
 2. `docs/review/evidence/RCC_002_S8CANDBCP_GATE_SCOPE_V1.json` -- NEW (Revision 7)
 3. `docs/review/evidence/RCC_002_S8CANDBCP_REV2_NORMATIVE_LEDGER_HISTORICAL_COPY_2026-08-01.txt` -- NEW (Revision 5)
 4. `docs/review/evidence/RCC_002_S8CANDBCP_REV2_NORMATIVE_LEDGER_SCOPE_V1.json` -- NEW (Revision 5; edited again, Section 7.2 item 3)
 5. `docs/review/evidence/RCC_002_S8CANDBCP_REV2_TRACK1_NORMATIVE_SCOPE_V1.json` -- NEW (Revision 5; edited again, Section 7.2 item 1)
 6. `docs/review/evidence/RCC_002_S8RR002_HISTORICAL_DATA_PIPELINE_SPECIFICATION_0_8_0_CERTIFIED_COPY_2026-08-02.txt` -- NEW (Revision 7)
 7. `docs/review/evidence/RCC_002_S8RR002_HISTORICAL_REPRODUCIBILITY_AND_MANIFEST_0_9_0_CERTIFIED_COPY_2026-08-02.txt` -- NEW (Revision 7)
 8. `docs/specifications/RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md` -- MODIFIED
 9. `docs/specifications/RCC_002_REPRODUCIBILITY_AND_MANIFEST_2026-07-23.md` -- MODIFIED
10. `registries/rcc002/views/s8_view_schema_fingerprint_profile.v1.json` -- NEW (Revision 5)
11. `schemas/rcc002/manifests/dataset-manifest/1.0.2.schema.json` -- NEW (Revision 5)
12. `scripts/rcc002/run_s8candbcp_gate.py` -- NEW (Revision 7)
13. `scripts/rcc002/verify_s8candbcp_gate_scope.py` -- NEW (Revision 7)
14. `scripts/rcc002/verify_s8candbcp_rev2_normative_ledger.py` -- NEW (Revision 5; edited again, Section 7.2 item 4)
15. `scripts/rcc002/verify_s8candbcp_rev2_track1_normative_scope.py` -- NEW (Revision 5; edited again, Section 7.2 item 2)
16. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/complete-valid.json` -- NEW (Revision 5)
17. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/minimal-valid.json` -- NEW (Revision 5)
18. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/CASE_LEDGER.json` -- NEW (Revision 5)
19. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/absolute-path.json` -- NEW (Revision 5)
20. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/duplicate-specification.json` -- NEW (Revision 5)
21. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/duplicate-view.json` -- NEW (Revision 5)
22. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/extra-property.json` -- NEW (Revision 5)
23. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/invalid-id.json` -- NEW (Revision 5)
24. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/invalid-timestamp.json` -- NEW (Revision 5)
25. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/missing-required-field.json` -- NEW (Revision 5)
26. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/missing-specification.json` -- NEW (Revision 5)
27. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/missing-view.json` -- NEW (Revision 5)
28. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/path-traversal.json` -- NEW (Revision 5)
29. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/reordered-specification.json` -- NEW (Revision 5)
30. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/reordered-view.json` -- NEW (Revision 5)
31. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/secret-like-field.json` -- NEW (Revision 5)
32. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/secret-like-value.json` -- NEW (Revision 5)
33. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/stale-specification-version.json` -- NEW (Revision 5)
34. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/unknown-specification.json` -- NEW (Revision 5)
35. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/unknown-view.json` -- NEW (Revision 5)
36. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/wrong-schema-identity.json` -- NEW (Revision 5)
37. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/wrong-schema-version.json` -- NEW (Revision 5)
38. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/wrong-type-nullability.json` -- NEW (Revision 5)
39. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/wrong-view-allowlist-hash.json` -- NEW (Revision 5)
40. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/wrong-view-fingerprint-hash.json` -- NEW (Revision 5)
41. `tests/rcc002/test_s8candbcp_gate_scope.py` -- NEW (Revision 7)
42. `tests/rcc002/test_s8candbcp_rev2_normative_ledger.py` -- NEW (Revision 5; edited again, Section 7.2 item 5)
43. `tests/rcc002/test_s8candbcp_rev2_track1_normative_scope.py` -- NEW (Revision 5; byte-unchanged, Section 7.2)
44. `tests/rcc002/test_s8rr002_manifest_correction_historical_replay.py` -- NEW (Revision 7)
45. `tests/rcc002/test_s8rr003_normative_ledger_historical_replay.py` -- NEW (Revision 7)

**Category totals**: 3 modified (items 1, 8, 9) + 42 new (all remaining
items) = **45 total**. This `42` is the Track 1 `new`-category subtotal
(`34` from Revision 5 plus `8` from Revision 7); it is not the same
quantity as Revision 6's rejected, differently-derived total-file count
of `42`, and the two must not be conflated.

### 7.4 Exact scope-artifact naming note

The Track 1 scope manifest itself (item 5 above) and its verifier (item
15) list themselves as entries within their own inventory, exactly as
Revision 5 Section 8.2 items 4/10 already did; this is safe and
unchanged: a scope manifest's own final bytes are hashed into the ledger
like any other artifact, and doing so does not create a self-referential
cycle (the manifest declares *paths*, not its own future hash).

## 8. Recomputed Track 1 and ledger arithmetic

```text
Track 1 file count before Revision 7                 = 37  (3 modified, 34 new)
Track 1 additions in Revision 7 (Section 7.1)         =  8  (all NEW)
Revised Track 1 file count                            = 45  (3 modified, 42 new)

Baseline ledger entries (unchanged, independently
  reconfirmed, Section 2 item 10)                      = 145
Replaced entries (DP, RM; count-neutral, unchanged
  from Revision 5)                                      =   2
New entries already added by Revision 5 Track 1        =  34
New entries added by Revision 7 (Section 7.1)           =   8
Removed entries                                         =   0
---------------------------------------------------------------
Revised successor ledger arithmetic: 145 + 34 + 8 - 0   = 187
Revised successor root ledger entry count               = 187
```

`187`, not Revision 6's rejected `184`, is the correct successor count,
because Revision 7 introduces `8` new Track 1 paths (Section 7.1), not
Revision 6's insufficient `5`. This count is independently re-derived
from the actual Section 7.3 inventory, not carried over from either
Revision 5 or Revision 6, and it accounts for the executable gate
authority (Section 5), its independent verifier and mutation tests
(Sections 5.5, 10), its scope manifest (Section 5.4), and the complete
replay infrastructure (Section 6) -- every one of the conditions
`S8-CAND-BCP-REV6-B02`'s required disposition names.

Self-entry exclusion (the root ledger does not list itself), protected-
builder exclusion (`scripts/build_rcc002_spec_bundle.py` appears in no
list, hardcoded or manifest, anywhere in this correction family), and
scope-overlap accounting (Section 7.1: none of the 8 new paths collides
with the 145 baseline or the 34 Revision 5 additions) are all unchanged
from Revision 5 Section 6.7 and independently reconfirmed here.

## 9. Gate-scope schema and independent verifier authority

Given in full in Section 5.4 (exact schema) and Section 5.5 (independent
hardcoded verifier). The verifier's hardcoded `EXPECTED_*` tuples are the
authority; the JSON manifest is a mutable, human-readable declaration that
must equal the hardcoded tuples exactly, mirroring the existing Track 1
scope verifier's own `EXPECTED_ENTRIES` vs. scope-manifest-file
relationship (Section 7.2 item 2). Neither is trusted alone: the manifest
without the verifier would be `S8-CAND-BCP-REV6-TEST-001`'s
"unauthenticated policy" again; the verifier without the manifest would
have no externally auditable, versioned declaration of scope.

## 10. Mutation-test requirements

### 10.1 Gate-scope verifier mutation tests (new)

New file, exact path `tests/rcc002/test_s8candbcp_gate_scope.py`. Exact
minimum required cases, each a distinct test method exercising
`verify_s8candbcp_gate_scope`'s functions directly against crafted
mutated category tuples or isolated temporary directories, never against
the live repository tree, mirroring the existing Track 1/ledger mutation-
test style (Section 7.2's byte-unchanged file):

1. missing module (a hardcoded `current_state` entry absent from the
   discovered set);
2. extra module (an undeclared `test_*.py` file present under
   `tests/rcc002/`, in an isolated temporary mirror of the tree);
3. duplicate module (the same module path listed in two categories);
4. reordered module (two adjacent entries transposed relative to true
   `LC_ALL=C` order within one category);
5. unsafe/absolute/parent-traversal path (an entry rewritten to
   `/etc/passwd` or `tests/rcc002/../../etc/passwd`);
6. wrong category (a real `current_state` module re-declared as
   `historical_audit_only`, or vice versa);
7. unknown module (a plausible-looking but nonexistent module name added
   to a category, absent from disk);
8. omitted replay adapter (one of the two
   `historical_replay_adapter` entries removed from the hardcoded tuple
   or the manifest, while the file itself remains on disk -- must be
   rejected as a category-count mismatch, not silently tolerated);
9. original historical module incorrectly placed in the `current_state`
   category (`test_s8rr002_manifest_correction.py` or
   `test_s8rr003_normative_ledger.py` moved out of
   `historical_audit_only`);
10. current-state module incorrectly placed in the
    `historical_audit_only` category (an arbitrary real `current_state`
    module, for example `tests/rcc002/test_constants.py`, moved into
    `historical_audit_only`);
11. forged metadata/count (`expected_total_modules`,
    `expected_current_state_count`,
    `expected_historical_replay_adapter_count`, or
    `expected_historical_audit_only_count` set to a value inconsistent
    with the actual category list lengths);
12. valid unchanged positive control: the true, uncorrupted `60`-module
    partition passes verification without modification, proving the
    verifier is fail-closed but not merely fail-closed -- it also
    correctly accepts the valid case.

This is a `12`-case minimum, one case more than the `9`-case minimum
Revision 5 Section 6.8 established for the Track 1 and ledger scope
verifiers, because `S8-CAND-BCP-REV6-TEST-001`'s required disposition
names three additional classes specific to a module-execution gate
(adapter omission, historical-module-in-live-category,
live-module-in-historical-category) that have no equivalent in a pure
file-scope verifier.

### 10.2 Historical replay adapter test requirements (restated)

Given in full in Section 6.2 (steps 6-7) and Section 6.3 (steps 8-9):
each adapter requires exactly one positive control (frozen inputs pass)
and exactly one negative control (live-tree substitution fails). Per
Revision 6 Section 7 (unchanged, not reopened): the full nine-case
scope-verifier mutation battery does not apply to either adapter, because
neither adapter is a new verifier with its own hardcoded scope logic --
both are thin replay harnesses over the already-certified, already-
mutation-tested S8-RR-002/S8-RR-003 verifier functions themselves. This
scoping judgment is confirmed, not merely asserted, by this revision's own
independent architecture analysis (Section 6.2/6.3), consistent with what
Revision 6 Section 7 flagged for independent-review confirmation.

## 11. Acyclic drafting, finalization, verification, review, and certification sequence

Extends Revision 5 Section 6.6's discipline (draft, then byte-finalize in
dependency order, then verify, then review, then certify -- never mutate
after finalization) to the Section 7.1 additions and Section 7.2 edits.
Steps 1-9 below are new relative to Revision 5/6; the pre-existing
37-file Track 1 draft (Revision 5 Section 6.6 steps 1-9, already applied
in the working tree per Revision 6 Section 2) is presumed complete and is
not repeated or reopened.

1. **Draft** content for all 8 Section 7.1 artifacts and the Section 7.2
   edits to the 5 existing draft artifacts (nothing byte-finalized yet).
   The exact 60-module partition (Section 5.3) is fully determined by
   filename alone, fixed by this proposal's Section 7.3 inventory; it has
   no dependency on any other new artifact's byte content, so it may be
   drafted first.
2. **Byte-finalize** the two frozen historical specification copies
   (Section 7.1 items 39-40; Section 6.1) -- mechanically sourced from
   commit `6f0f840`, no dependency on any other new item.
3. **Byte-finalize** the two historical-replay adapters (Section 7.1
   items 44-45; Section 6.2, Section 6.3) -- depend on step 2's frozen
   copies for their embedded provenance/hash-check logic.
4. **Byte-finalize** `scripts/rcc002/verify_s8candbcp_gate_scope.py`
   (Section 7.1 item 42) -- depends only on the fixed Section 7.3 module
   partition (available since step 1), not on steps 2-3.
5. **Byte-finalize** `docs/review/evidence/RCC_002_S8CANDBCP_GATE_SCOPE_V1.json`
   (Section 7.1 item 38) -- depends on step 4, so it can name the exact
   consuming verifier path and mirror its hardcoded categories exactly.
6. **Byte-finalize** `scripts/rcc002/run_s8candbcp_gate.py` (Section 7.1
   item 41) -- depends on steps 4-5 both existing.
7. **Byte-finalize** `tests/rcc002/test_s8candbcp_gate_scope.py` (Section
   7.1 item 43) -- depends on step 4, the verifier it exercises.
8. **Byte-finalize** the 5 Section 7.2 edited-in-place artifacts (Track 1
   scope manifest and verifier, ledger scope manifest and verifier, and
   the ledger mutation-test docstring correction) -- depends on the final
   Section 7.3 inventory (fixed at step 1) and on steps 2-7 already
   existing as concrete new paths to list and count.
9. **Recompute** the root `SHA256SUMS`: enter the 8 Section 7.1 paths as
   8 new entries alongside the already-established 179-entry state from
   the Revision 5/6 working tree, for the exact 187-entry total (Section
   8). The already-drafted 37 Revision 5 entries and their content are
   not touched by this step; only the ledger file itself gains 8 more
   lines and the 5 Section 7.2 files' already-listed entries change hash
   (still count-neutral: they were already `NEW` entries, now pointing at
   different bytes for the same declared paths).
10. **Verify**: run the Section 5.2 authoritative gate command; run the
    existing Track 1 and ledger scope verifiers
    (`verify_s8candbcp_rev2_track1_normative_scope.py`,
    `verify_s8candbcp_rev2_normative_ledger.py`) against the Section 8
    counts; run the Section 5.7 historical-audit commands directly, for
    confirmation, understanding both are expected to fail against the
    live tree by design.
11. **Independently review**: perform scientific and architecture review
    of the exact byte-finalized set from steps 2-9, and of this Revision
    7 document itself, exactly as `S8-CAND-TRACK1-GATE-B01`'s disposition
    (Section 3) requires.
12. **Certify**: record, externally to every artifact reviewed in step
    11 (in a certification record document, and by the act of committing
    the already-byte-finalized ledger from step 9), that the exact hashes
    verified in step 10 and reviewed in step 11 are approved. No artifact
    touched in steps 2-11 is edited by this step.

This sequence is acyclic: every step depends only on strictly earlier
steps; the ledger (step 9) is computed only after every artifact it
indexes is already byte-finalized (steps 2-8); verification, review, and
certification (steps 10-12) strictly follow finalization, and nothing
after step 9 edits any byte-finalized artifact.

## 12. Non-reviewability and non-authorization

**The current Track 1 candidate remains not reviewable and not
certifiable.** This status is unchanged by this document's existence and
persists until: Section 11's sequence completes in full; the Section 5.2
authoritative gate command is run and independently confirmed to exit
`0`; and this Revision 7 document itself is independently re-reviewed and
not rejected. This proposal does not authorize, and no artifact within it
performs, any of the following: Track 1 certification; Track 2
implementation start or repair; View-schema-fingerprint formula selection
or emission; corrected-candidate resubmission; dataset generation; dataset
publication; or live or paper deployment. Track 2, dataset generation,
publication, and deployment remain exactly as unauthorized as under every
prior revision in this family (Revision 5 Section 11, Revision 6 Section
10, both unchanged).

**This proposal does not self-authorize.** The Section 5 gate
architecture is a cross-cutting redefinition of a governance success
criterion; per this repository's working rule that architecture authority
is never self-granted, it is proposed, not adopted, by this document, and
requires the same independent re-review discipline every Revision 1-6
change has gone through (Section 11, step 11) before any Section 7.1
artifact may be drafted or byte-finalized.

## 13. Process finding, restated (no reversal claimed)

`S8-CAND-TRACK1-PROC-001` is restated here, unchanged in substance from
Revision 6 Section 5.2, and is **not** closed, reopened, reinterpreted, or
claimed reversible by this document:

1. **Disclosure.** An earlier protected-builder compliance breach
   involving `scripts/build_rcc002_spec_bundle.py` remains disclosed as a
   named finding, not omitted or silently absorbed into any other section.
2. **No claim of reversal.** This proposal does not claim, and no action
   available to it could accomplish, that the breach can be undone. Any
   prior exposure of that file's content or digest to any process is a
   fact of history, not a state this or any later revision can retract.
3. **Clean-session requirement, restated.** All future verification of
   this candidate (Track 1 finalization, gate-architecture drafting,
   Track 2 repair, mechanical verification, independent review,
   certification) must occur in a session that at no point reads,
   hashes, inspects, opens, executes, imports, copies, renames, deletes,
   modifies, stages, or packages `scripts/build_rcc002_spec_bundle.py`,
   exactly as this revision's own preparation session did (Section 2,
   Section 14).
4. **No evidentiary status for any digest of that file.** No hash, byte
   count, modification time, or other digest of that file, however
   obtained, is treated as candidate evidence, scope evidence, or ledger
   evidence by this or any future revision. It remains, as in every prior
   revision, entirely outside the Track 1 and Track 2 exact-scope
   inventories.

## 14. Restrictions honored while preparing this revision

- No repository file was created, modified, deleted, renamed, staged,
  committed, or pushed.
- The existing 37-file Revision 5/6 Track 1 candidate was treated
  strictly read-only throughout: read for architecture and hashing
  purposes only, never modified, staged, committed, or pushed;
  independently reconfirmed present and unchanged (Section 2) throughout
  this drafting session.
- `rcc002/s8/` and `tests/rcc002/s8/` (the prior, separate candidate) were
  read only to enumerate the exact `test_*.py` module count (Section 5.3);
  neither was modified, staged, committed, or pushed.
- `scripts/build_rcc002_spec_bundle.py` was not read, hashed, inspected,
  opened, executed, imported, copied, renamed, deleted, modified, staged,
  packaged, or used as evidence at any point during this drafting session.
  It was not named as an argument to any executed command.
- Every `git show <commit>:<path>` and `git diff` command executed
  targeted only DP, RM, `SHA256SUMS`, and the S8-RR-002/S8-RR-003
  certified pair's own paths, for provenance verification (Section 2,
  Section 6.1); none targeted the protected builder.
- All diagnostics were passive: branch/HEAD/origin/status checks,
  `git show`/`git diff` against historical commits, `sha256sum` of
  existing files, and one informational `import jsonschema` version
  check in the local `.venv`. `PYTHONDONTWRITEBYTECODE=1` was not
  required for any of these (none executed a `.py` file as a program;
  the `jsonschema` check imported an already-installed package only), and
  no `__pycache__` or other repository artifact was created by any of
  them (independently reconfirmed: `git status --short` immediately
  following is byte-identical to the Section 2 baseline).
- No dependency was installed. No network access was used beyond the
  local `git` object store already present in this clone.
- Repository HEAD and `origin/main` were re-verified as
  `28cec09fb22a93ff8e3263d85f1f21bcc83d52da` after all analysis and are
  unchanged by this drafting session (Section 15).
- The only filesystem write performed while preparing this revision is
  this single output Markdown file, outside the repository, at
  `/mnt/c/Users/benja/Downloads/RCC_002_S8_IMPLEMENTATION_CANDIDATE_BLOCKER_CORRECTION_PROPOSAL_REV7_2026-08-02.md`.

## 15. Final git status and HEAD/origin confirmation

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

Byte-identical in composition to the baseline captured in Section 2, item
7. `git rev-parse HEAD` and `git rev-parse origin/main` both return
`28cec09fb22a93ff8e3263d85f1f21bcc83d52da`, unchanged from Section 2, item
2. Nothing was staged (`git diff --cached` remains empty).

## 16. Final report

- **Output path**:
  `/mnt/c/Users/benja/Downloads/RCC_002_S8_IMPLEMENTATION_CANDIDATE_BLOCKER_CORRECTION_PROPOSAL_REV7_2026-08-02.md`
  (this file cannot state its own SHA-256 or line count within itself;
  both are reported by the preparing session, outside this document, once
  writing is complete).
- **Closure summary**: `S8-CAND-BCP-REV6-B01` closed by Section 5 (single
  selected executable gate architecture); `S8-CAND-BCP-REV6-B02` closed by
  Sections 7-8 (exact inventory and recomputed arithmetic); `S8-CAND-BCP-REV6-ARCH-001`
  closed by Section 6 (exact historical replay-root construction for both
  predecessor suites); `S8-CAND-BCP-REV6-TEST-001` closed by Sections 9-10
  (independent gate-scope verifier authority and twelve-case mutation
  battery). `S8-CAND-TRACK1-GATE-B01` remains open, restated, not closed
  by this document (Section 3, Section 12). `S8-CAND-TRACK1-PROC-001`
  remains disclosed, not reversed, restated in Section 13.
- **Counts**: Track 1 `45` files (`3` modified, `42` new); successor
  ledger `187` entries (`145` baseline + `42` added - `0` removed, `2`
  replaced count-neutral); `tests/rcc002` module partition `60` total
  (`56` current-state, `2` historical-replay-adapter, `2`
  historical-audit-only).
- **Confirmations**: no repository file was created, modified, deleted,
  renamed, staged, committed, or pushed (Section 14); repository HEAD and
  `origin/main` remain `28cec09fb22a93ff8e3263d85f1f21bcc83d52da`
  throughout (Section 15); `scripts/build_rcc002_spec_bundle.py` was never
  read, hashed, inspected, opened, executed, imported, copied, renamed,
  deleted, modified, staged, packaged, or used as evidence at any point in
  the preparation of this revision (Section 2, Section 14).

## 17. Final statement

Revision 7 replaces Revision 6's rejected Section 6 correction
architecture with one selected, executable, versioned gate authority
(`RCC-002-S8-CAND-BCP-001-REV7-GATE-V1`, Section 5): an exact authoritative
command (`scripts/rcc002/run_s8candbcp_gate.py`), an exact `60`-module
partition into `56` current-state, `2` historical-replay-adapter, and `2`
historical-audit-only modules, an independent hardcoded gate-scope
verifier with a twelve-case mutation battery (Sections 9-10), and an
exact, deterministic historical replay-root construction for both
predecessor suites, accounting for every file each certified verifier
actually reads and including explicit negative controls (Section 6). It
provides one exhaustive, lexically ordered, 45-entry Track 1 inventory
that distinguishes repository classification from byte changes within an
uncommitted candidate (Section 7), recomputes the ledger arithmetic to an
independently re-derived `187` entries (Section 8), and lays out a fully
acyclic drafting-to-certification sequence (Section 11). It does not
create, modify, or byte-finalize any artifact itself; it does not
self-authorize the gate architecture it proposes; Track 1 remains not
reviewable and not certifiable; and Track 2, dataset generation,
publication, and deployment remain unauthorized. The earlier
protected-builder compliance breach (`S8-CAND-TRACK1-PROC-001`) remains
disclosed, without claim of reversal, unchanged from Revision 6.
