# RCC-002 S8 Implementation Candidate Blocker Correction Proposal - Revision 4

## Document control

| Field | Value |
|---|---|
| Proposal ID | `RCC-002-S8-CAND-BCP-001-REV4` |
| Proposal date | `2026-08-01` |
| Proposal class | Correction planning only (no implementation) |
| Revision | `4` (supersedes Revision 3) |
| Target artifact | The rejected, uncommitted S8 implementation candidate |
| Candidate baseline (repository HEAD at drafting time) | `dca9baed0b6b13090a2080711b4105412eb2b067` |
| Candidate baseline branch | `main` |
| Candidate baseline `origin/main` | `dca9baed0b6b13090a2080711b4105412eb2b067` |
| Expected uncommitted worktree state at drafting time | `?? rcc002/s8/`, `?? scripts/build_rcc002_spec_bundle.py`, `?? tests/rcc002/s8/` |
| Superseded proposal (Revision 3) | `docs/review/RCC_002_S8_IMPLEMENTATION_CANDIDATE_BLOCKER_CORRECTION_PROPOSAL_REV3_2026-08-01.md` |
| Revision 3 SHA-256 | `a2fb61f278586c9ee14a060766a4061c59b59d3bd210a199fd43b9325cf99d00` |
| Controlling re-review (Revision 3 rejection) | `docs/review/RCC_002_S8_IMPLEMENTATION_CANDIDATE_BLOCKER_CORRECTION_PROPOSAL_REV3_CHATGPT_INDEPENDENT_RE_REVIEW_2026-08-01.md` |
| Controlling re-review SHA-256 | `6a465272360215ff7c28881189c40914bc1673cbb79e23199db1c3dc7c9dc2c0` |
| Controlling re-review decision | `REJECT` |
| Controlling candidate review | `docs/review/RCC_002_S8_IMPLEMENTATION_CANDIDATE_CHATGPT_INDEPENDENT_REVIEW_2026-08-01.md` |
| Authoritative readiness decision | `docs/review/RCC_002_S8_IMPLEMENTATION_READINESS_REVIEW_RR004_2026-08-01.md` |
| Original candidate findings addressed | `S8-CAND-B01`, `S8-CAND-B02`, `S8-CAND-B03`, `S8-CAND-ARCH-001`, `S8-CAND-ARCH-002`, `S8-CAND-IMPL-001`, `S8-CAND-TEST-001`, `S8-CAND-STATE-001`, `S8-CAND-DOC-001` |
| Revision 1 review findings addressed | `S8-CAND-BCP-B01`, `S8-CAND-BCP-B02`, `S8-CAND-BCP-ARCH-001`, `S8-CAND-BCP-ARCH-002`, `S8-CAND-BCP-IMPL-001`, `S8-CAND-BCP-DOC-001` |
| Revision 2 re-review findings addressed | `S8-CAND-BCP-REV2-B01`, `S8-CAND-BCP-REV2-B02`, `S8-CAND-BCP-REV2-ARCH-001`, `S8-CAND-BCP-REV2-ARCH-002`, `S8-CAND-BCP-REV2-ARCH-003`, `S8-CAND-BCP-REV2-ARCH-004`, `S8-CAND-BCP-REV2-DOC-001` |
| Revision 3 re-review findings addressed | `S8-CAND-BCP-REV3-B01`, `S8-CAND-BCP-REV3-B02`, `S8-CAND-BCP-REV3-ARCH-001`, `S8-CAND-BCP-REV3-TEST-001` |
| Proposal status | **Proposal only. Not approved. Not certified. Does not authorize implementation.** |

### Protected-file exclusion statement

`scripts/build_rcc002_spec_bundle.py` is a pre-existing untracked protected
file. It was not read, hashed, inspected, opened, executed, imported,
copied, renamed, deleted, modified, staged, or packaged in the preparation
of this proposal. It appears in this document only in this explicit
exclusion statement and in the passive `git status` listing reproduced
above.

## 1. Purpose and scope of Revision 4

This document is a **correction proposal**, not a repair, not a
specification amendment, and not an implementation-readiness decision. It
does not modify, create, delete, or rename any repository file. Revision 4
exists solely to close the four findings raised by the independent
re-review of Revision 3 (`RCC-002-S8-CAND-BCP-REV3-CHATGPT-IRR-001`,
`REJECT`), while preserving every decision the re-review confirmed as
already closed (Section 6 of the re-review):

1. `S8-CAND-BCP-REV2-B01` (exact 7/7/8 fingerprint-replacement counts,
   artifact-to-view semantic equality, RM self-hash distinction) --
   **CLOSED, unchanged**.
2. `S8-CAND-BCP-REV2-ARCH-001` (`run.py`/`stage.py` present in the Track 2
   scope) -- **CLOSED, unchanged**.
3. `S8-CAND-BCP-REV2-ARCH-003` (binding successor versions) -- **CLOSED,
   unchanged**.
4. `S8-CAND-BCP-REV2-DOC-001` (closed specification-profile wording,
   corrected fixture counts, const-vs-hash distinction) -- **CLOSED,
   unchanged**.
5. The six-View registry concept, the selected shared canonicalization
   architecture (`rcc002/canonical.py`), the run-ID grammar, and the
   centralized portable-path grammar are all unchanged, as the re-review's
   Section 7 explicitly confirms and Section 7 of the re-review's "Required
   Revision 4 boundary" explicitly permits leaving unchanged.

Revision 4's changes are corrective and additive only: the omitted
canonicalization golden fixture is added to the exact Track 2 inventory;
the fingerprint registry's status lifecycle is redefined so no artifact
byte changes after verification or review; both exact inventories are
rewritten as single, true `LC_ALL=C`-ordered lists with one unambiguous
ordering authority; and one dedicated mutation-test artifact is added for
each of the two new exact-scope verifiers. Every count in this document
(Track 1, Track 2, and the successor ledger) is recomputed from the final,
corrected path sets, not carried over from Revision 3.

## 2. Baseline and evidence used

- Repository branch `main`, HEAD and `origin/main` both
  `dca9baed0b6b13090a2080711b4105412eb2b067`, verified before drafting.
- Worktree state verified to contain exactly the expected three untracked
  paths, with the protected builder excluded from all analysis.
- The Revision 3 SHA-256 and the controlling re-review's own SHA-256 were
  independently recomputed and matched before any finding was transcribed
  into this revision.
- The current root `SHA256SUMS` was independently confirmed to contain
  exactly 145 entries at drafting time; this is the same baseline count
  the controlling re-review independently confirmed (Section 4.6 of the
  re-review) and this proposal's own Revision 3 (Section 2 of Revision 3);
  it is restated here, not re-derived from a different source, because no
  repository state has changed between Revision 3's drafting and this
  revision's drafting.
- All four Revision 3 inventory and lifecycle defects cited by the
  controlling re-review (Section 5 of the re-review) were independently
  re-confirmed against the actual Revision 3 document text before being
  corrected here: the golden-fixture path is absent from Revision 3's
  Section 8.3 three-item new-file list; Revision 3 Section 6.6 step 10
  does state that certification sets the registry's `status` field to
  `"certified"`, which is a byte mutation after Section 6.6 steps 8-9; and
  both Revision 3 Section 8.2 and Section 8.3, independently re-sorted in
  this revision's drafting using the same method as Revision 3's own
  drafting (Python's default string ordering, which is byte-identical to
  `LC_ALL=C` for the pure-ASCII repository-relative paths used throughout
  this proposal family), do not match the category-grouped presentation
  order Revision 3 actually printed.

No implementation file was executed, imported, or modified to prepare
this revision. Read-only inspection only.

## 3. Absolute constraint on the View-schema-fingerprint formula (unchanged)

This proposal does not invent, infer, or silently select the actual
View-schema-fingerprint preimage formula. That choice belongs exclusively
to the independently reviewed and certified Track 1 normative correction
artifact (Section 6). Revision 4 does not touch this constraint; it
corrects the inventory, lifecycle, and ordering defects surrounding it.

## 4. Revision 4 closure matrix (Revision 3 re-review findings)

| Finding | Severity | Revision 3 gap | Revision 4 closure section |
|---|---|---|---|
| `S8-CAND-BCP-REV3-B01` | BLOCKER | The mandatory canonicalization golden fixture was required by Section 7.2 but absent from the exact, closed Track 2 inventory (Section 8.3), making the contract self-contradictory. | Section 7.2, Section 8.3 |
| `S8-CAND-BCP-REV3-B02` | BLOCKER | Section 6.6 step 10 set the registry's `status` to `"certified"` after verification and review, mutating an already-verified, already-ledgered artifact. | Section 6.4, Section 6.6 |
| `S8-CAND-BCP-REV3-ARCH-001` | MAJOR | Both exact inventories claimed strict lexical order but were presented as category-grouped lists whose category boundaries broke true `LC_ALL=C` order. | Section 8 (full rewrite) |
| `S8-CAND-BCP-REV3-TEST-001` | MAJOR | The Track 1 and Track 2 exact-scope verifiers had no dedicated mutation-test artifact of their own (only the separate normative-ledger verifier did). | Section 6.8, Section 7.6, Section 8.2, Section 8.3 |

Every row above is closed by an exact decision in the section cited, not
by a restatement of the requirement.

## 5. Finding-to-correction-to-verification map (all nine original candidate findings, unchanged)

Unchanged in substance from Revision 3 Section 5 (itself unchanged from
Revision 2 Section 5 and Revision 1 Section 4). Not reproduced a fourth
time in full here. The two file-boundary corrections carried into
Revision 3 Section 8.2 (`rcc002/s8/manifests/run.py` and
`rcc002/s8/manifests/stage.py`) remain in force and are restated in this
revision's Section 8.3.

## 6. Track 1 - Normative correction track

### 6.1 Exact downstream fingerprint replacement matrix (unchanged from Revision 3 Section 6.1)

Unchanged. The independently reproduced counts -- RM Section 24: 7 total
(6 `views[]` + 1 `artifacts[]`, excluding the permanent RM self-hash
placeholder); `1.0.2/minimal-valid.json`: 7 total; `1.0.2/complete-valid.json`:
8 total (6 `views[]` + 2 `artifacts[]`, matched against
`rcc002.view.audit/2.0.0` and `rcc002.view.label-research/1.0.0`
respectively) -- and the mandatory artifact-to-view semantic-equality
rule are unchanged. The controlling re-review independently confirmed
these counts correct (Section 4.1 of the re-review) and this finding
closed (`S8-CAND-BCP-REV2-B01`, Section 6 of the re-review); Revision 4
does not reopen it.

### 6.2 Exact logical-contract dimensions required in the fingerprint preimage (unchanged)

Unchanged from Revision 3 Section 6.2.

### 6.3 Exact successor versions, binding and non-reopenable (unchanged)

Unchanged from Revision 3 Section 6.3. Data Pipeline `0.9.0`, RM `0.9.1`,
the fingerprint registry `1.0.0`, and Dataset Manifest `1.0.2` remain
binding; a different version requires a new proposal revision and
re-review. The controlling re-review independently confirmed this closed
(`S8-CAND-BCP-REV2-ARCH-003`, Section 4.5 and Section 6 of the re-review);
Revision 4 does not reopen it.

### 6.4 Exact closed fingerprint-registry contract, with a non-mutating status lifecycle (closes `S8-CAND-BCP-REV3-B02`, part 1)

Revision 3's registry container schema (path, top-level key set, the
`owning_specification` object, and the twelve-key `views[]` entry object)
is unchanged **except for the exact definition and permitted values of
the `status` key**, which Revision 4 redefines to eliminate the
post-review mutation the re-review identified.

**Corrected `status` key definition:**

| Key | Type | Exact value or constraint |
|---|---|---|
| `status` | string | `enum`: `["draft", "candidate_for_normative_review"]` -- **`"certified"` is not a permitted value of this field and never appears in the registry file at any point in its lifecycle.** |

**Rationale, grounded in existing repository precedent:** the certified
`registries/rcc002/release/release_artifact_class_registry.v1.json`
already carries the literal status value `"candidate_for_normative_review"`
as its permanent, unmutated content, including after that registry was
ledgered and treated as certified evidence throughout the S8-RR-002 and
S8-RR-003 correction chains. This repository's established convention is
therefore that a registry artifact's own `status` field records the
process stage under which its *content* was authored, not a live,
externally-mutable flag tracking whether the artifact has since been
certified. Revision 4 makes this convention explicit and binding for the
new View-schema-fingerprint registry: its `status` is fixed to
`"candidate_for_normative_review"` no later than the byte-finalization
step (Section 6.6, State 1) and is **never** edited again, by any later
step, for any reason. The registry's certification is a fact recorded
**outside** the registry file -- in the independent review document, in a
certification record, and in the successor ledger's own commit -- never
by mutating the artifact whose certification is being decided. This
removes the self-referential circularity at its source: there is no
longer any registry-internal state that must change after review, so
there is nothing left to mutate.

Every other key, type, and cardinality in the registry container
(`registry_id`, `registry_version`, `project`, `owning_specification`,
`canonicalization_profile_id`, `views[]` and its twelve-key entry object)
is unchanged from Revision 3 Section 6.4 and remains exact and closed, with
no "at minimum" wording anywhere.

### 6.5 Exact Dataset Manifest 1.0.2 fixture contract (unchanged)

Unchanged from Revision 3 Section 6.5: exactly 2 positive fixtures,
exactly 22 negative fixtures (21 ported plus `wrong-view-fingerprint-hash.json`),
exactly 22 case-ledger entries, byte-for-byte preservation of every
`1.0.0` and `1.0.1` artifact. The controlling re-review independently
confirmed this exact and correct (Section 4.3 of the re-review).

### 6.6 Acyclic byte-finalization and certification sequence, with no post-review mutation (closes `S8-CAND-BCP-REV3-B02`, part 2)

Revision 3 Section 6.6 already distinguished "byte-finalization" from
"certification" as concepts, but its step 10 then mutated the registry's
`status` field as part of certifying it -- exactly the defect Section 6.4
above closes at the artifact-content level. Revision 4 restates the
sequence using four explicitly separated, non-mutating states, matching
the exact terms required: **byte-finalized**, **verified**,
**independently reviewed**, and **certified**.

**The governing rule:** once an artifact enters the byte-finalized state,
no later state may change one byte of it, ever. "Certified" is a
statement about a byte-finalized artifact's already-fixed hash, recorded
externally; it is never a rewritten copy of the artifact, and it is never
a field mutated inside the artifact.

**Exact sequence:**

1. **Draft** the fingerprint contract and registry content (Section 6.4),
   including the two literal View-fingerprint golden preimages and the
   fingerprint-derivation algorithm (Section 3: the specification owner's
   act, not this proposal's).
2. **Byte-finalize** the registry: fix `status` permanently to
   `"candidate_for_normative_review"` (Section 6.4) and fix every other
   field's final value, including the six literal `schema_fingerprint_sha256`
   values. From this point forward, the registry file is never edited
   again by any subsequent step in this sequence, by the mechanical
   verifier, by the independent reviewer, or by the certification act.
3. **Byte-finalize** Data Pipeline `0.9.0` (new SS7.9.5, extended SS6.2
   cross-reference).
4. **Byte-finalize** RM `0.9.1` (SS8.7 cross-reference, SS24 seven-value
   View-fingerprint replacement per Section 6.1), preserving the SS24
   self-hash convention for RM's own `specification_profile` entry in the
   *prose example*, unchanged and permanent, per Section 6.1.
5. Compute the real SHA-256 document hashes of the now byte-finalized Data
   Pipeline `0.9.0` and RM `0.9.1` files (fixture document-hash inputs,
   distinct from the schema ID/version consts already available from
   Section 6.3 -- unchanged distinction from Revision 3 Section 6.6).
6. **Byte-finalize** the Dataset Manifest `1.0.2` schema (Section 6.5),
   using the fixed schema-identity ID/version consts (available since
   step 1, independent of step 5) and the six frozen View-fingerprint
   literals (available since step 2).
7. **Byte-finalize** the `1.0.2` fixtures (Section 6.1, Section 6.5), which
   require step 5's real document hashes for their `specification_profile[]`
   payloads.
8. **Byte-finalize** the successor `SHA256SUMS` and its ledger scope
   manifest (Section 6.7): compute the SHA-256 of every byte-finalized
   artifact from steps 2-7 (and of the two Track 1 mutation-test files,
   Section 6.8) and enter them into the ledger. Once entered, the ledger
   itself becomes byte-finalized and is never further edited within this
   correction cycle.
9. **Verify**: run exact-scope mechanical verification (Section 8) over
   the complete, now byte-finalized set from steps 2-8. Verification reads
   and checks; it writes nothing back into any verified artifact.
10. **Independently review**: perform scientific and architecture review
    of the exact same byte-finalized set verified in step 9. Review reads
    and evaluates; it writes nothing back into any reviewed artifact.
11. **Certify**: record, externally to every artifact reviewed in step 10
    (in a certification record document, and by the act of committing the
    already-byte-finalized ledger from step 8), that the exact hashes
    verified in step 9 and reviewed in step 10 are approved. **No artifact
    touched in steps 2-10 is edited by this step.** The registry's
    `status` field remains `"candidate_for_normative_review"`, unchanged
    from step 2, forever; the fact of certification is recorded in the
    surrounding governance documents, not in the registry.

Because no step after step 2 edits the registry (or any other
byte-finalized artifact), the verified hash, the reviewed hash, the
ledgered hash, and the final hash are, by construction, the same hash at
every step from step 2 onward. This eliminates the circularity the
controlling re-review identified: there is no ordering in which the
ledger could become stale, because nothing changes after the ledger
entry (step 8) is computed from already byte-finalized bytes (steps 2-7),
and step 11 never writes to any prior artifact.

### 6.7 Certified normative-ledger successor cycle, arithmetic recomputed (closes remainder of `S8-CAND-BCP-REV2-ARCH-004`, updates for `S8-CAND-BCP-REV3-TEST-001`)

**Exact successor-set arithmetic, recomputed from the final Section 8.2
path set, not carried over from Revision 3:**

```text
baseline entries (independently confirmed, Section 2)            = 145
replaced (same path, new hash: Data Pipeline and RM
  specification documents, Section 6.3; count-neutral)            =   2
added (new Track 1 paths, Section 8.2 -- now includes the new
  Track 1 scope-verifier mutation-test artifact required by
  S8-CAND-BCP-REV3-TEST-001, Section 6.8)                          =  34
removed                                                            =   0
-----------------------------------------------------------------------
successor entries = 145 + 34 - 0                                  = 179
```

The one-entry increase relative to Revision 3's 178 is exactly and only
the new Track 1 scope-verifier mutation-test artifact added in Section 6.8
below; every other Revision 3 ledger artifact and count is unchanged.

The historical evidence copy, its exact path
(`docs/review/evidence/RCC_002_S8CANDBCP_REV2_NORMATIVE_LEDGER_HISTORICAL_COPY_2026-08-01.txt`),
its hash-derivation requirement (mechanically computed from the
then-current root `SHA256SUMS` bytes at Track 1 drafting time, not
asserted by this proposal as a fixed literal), the ledger scope manifest
and verifier paths, the root-ledger self-entry exclusion, and the
protected-builder exclusion are all unchanged from Revision 3 Section 6.7.
The exact successor path set is the single Section 8.2 list in this
revision (Section 6.6 step 8's "steps 2-8" byte-finalized set), not a
separately maintained list.

**Scope boundary, unchanged:** this ledger successor cycle covers Track 1
(normative) artifacts only. Track 2 files -- including the golden fixture
added in Section 7.2/Section 8.3 and the new Track 2 scope-verifier
mutation-test artifact added in Section 7.6/Section 8.3 -- remain part of
the uncommitted, uncertified S8 candidate and are out of scope for this
ledger cycle, exactly as Revision 3 Section 6.7 already established; this
boundary is not changed by any Revision 4 correction.

### 6.8 Track 1 exact-scope-verifier mutation-test artifact (closes `S8-CAND-BCP-REV3-TEST-001`, Track 1 half)

**Exact path:** `tests/rcc002/test_s8candbcp_rev2_track1_normative_scope.py`
(new; added to the Section 8.2 Track 1 inventory and to the Section 6.7
ledger successor arithmetic as one of the 34 added entries).

**Purpose:** focused mutation tests for
`scripts/rcc002/verify_s8candbcp_rev2_track1_normative_scope.py`
(Section 6.4/Section 8's Track 1 scope verifier), distinct from the
already-required `tests/rcc002/test_s8candbcp_rev2_normative_ledger.py`
(which tests the *ledger* verifier, a different artifact with a different
scope).

**Required minimum cases, at least one test method each:**

1. missing entry (a required Track 1 path absent from the candidate scope
   under test);
2. extra entry (an undeclared path present in the candidate scope);
3. duplicate entry (the same path listed twice);
4. reordered (swapped) entry (two adjacent entries transposed relative to
   the true `LC_ALL=C` order, Section 8.1);
5. miscategorized entry (a path declared under the wrong category, for
   example a "new" path declared as "modified" or vice versa);
6. absolute path injected into the scope;
7. parent-traversal (`../`) path injected into the scope;
8. incorrect/forged metadata (for example a wrong `correction_id`,
   `scope_id`, or declared total count that disagrees with the actual
   listed entries);
9. **unchanged positive control**: the true, uncorrupted Section 8.2 scope
   passes verification without modification -- proving the verifier is not
   merely fail-closed but also correctly accepts the valid case.

This is the same minimum case list, applied to the Track 1 scope
verifier, that Section 7.6 applies to the Track 2 scope verifier and that
Revision 3 Section 6.7 already applied to the normative-ledger verifier;
all three exact-scope verifiers in this correction family now have a
dedicated, focused, adverse-mutation-covering test artifact.

### 6.9 Review, certification, and readiness gates (updated to reference the five-state lifecycle)

1. Section 6.6 steps 1-8 (drafting and byte-finalization of every Track 1
   artifact, including the ledger).
2. Internal review of the drafted, now byte-finalized text and artifacts
   for consistency with SS6.2, SS6.4, SS8.7, and SS13.
3. Scientific consistency review, confirming the preimage dimensions do
   not silently alter any certified scientific transformation, label, or
   leakage-classification rule.
4. Architecture review, confirming the ownership split (SS8.8), the
   Section 6.4 registry container schema and its non-mutating status
   lifecycle, and the Section 6.7 ledger successor were followed exactly
   as specified.
5. Section 6.6 step 9 (exact-scope mechanical verification), including the
   new Section 6.8 Track 1 scope-verifier mutation tests.
6. Section 6.6 step 10 (independent scientific and architecture review of
   the complete byte-finalized set).
7. Section 6.6 step 11 (certification, recorded externally, with no
   further mutation of any reviewed artifact).
8. Only after step 7 above is complete may the implementation repair
   track implement the certified formula, and only after that
   implementation is itself repaired and re-tested may a new candidate be
   submitted for the independent re-review required by Section 11.

### 6.10 Explicit prohibition on implementing an unapproved fingerprint formula (unchanged)

Unchanged from Revision 1 Section 5.7, Revision 2 Section 6.7, and
Revision 3 Section 6.9.

## 7. Track 2 - Implementation repair track

Sections 7.1 (shared canonicalization authority), 7.3 (run-ID grammar),
7.4 (portable-path grammar), and 7.5 (regression gates) are **unchanged
from Revision 3 Sections 7.1-7.5**, none of which the controlling
re-review faulted (Section 4 of the re-review lists the shared
canonicalization architecture, run-ID grammar, and portable-path grammar
among the areas Revision 3 already got right or that were already closed
in a prior cycle).

### 7.2 Canonicalization golden fixture: now explicitly part of the exact Track 2 inventory (closes `S8-CAND-BCP-REV3-B01`)

The golden fixture requirement itself is unchanged from Revision 2
Section 7.2: exact path
`tests/fixtures/rcc002/canonicalization/rcc_json_canonicalization_v1.golden.v1.json`,
exact format (top-level `fixture_id`, `fixture_version`,
`canonicalization_profile_id`, `cases[]`), and the mandatory non-BMP
UTF-16-ordering and NFC-collision cases. **What Revision 4 corrects is
that this file is now explicitly listed as a new Track 2 artifact in
Section 8.3's exact inventory and its exact count** -- Revision 3 required
the fixture in prose (Section 7, incorporated from Revision 2) while
simultaneously excluding it from the closed, exact file list that the
Track 2 verifier (Section 8.4) must accept, which was self-contradictory.
This file is the single external canonicalization-evidence authority for
both `S8-CAND-B01` and `S8-CAND-TEST-001`; it is never embedded in test
source code (unchanged rule).

### 7.6 Track 2 exact-scope-verifier mutation-test artifact (closes `S8-CAND-BCP-REV3-TEST-001`, Track 2 half)

**Exact path:** `tests/rcc002/test_s8candbcp_rev2_track2_implementation_scope.py`
(new; added to the Section 8.3 Track 2 inventory).

**Purpose:** focused mutation tests for
`scripts/rcc002/verify_s8candbcp_rev2_track2_implementation_scope.py`
(Section 8's Track 2 scope verifier).

**Required minimum cases**, the same nine-case minimum defined in
Section 6.8 for the Track 1 scope verifier, applied here to the Track 2
scope (missing, extra, duplicate, reordered, miscategorized, absolute
path, parent-traversal path, incorrect/forged metadata, and an unchanged
positive control that the true, uncorrupted Section 8.3 scope passes
verification without modification).

This artifact is Track 2 scope, not Track 1; per Section 6.7's unchanged
scope boundary, it is **not** added to the normative-ledger successor
arithmetic.

All nine original adverse mutations (Revision 1 Section 6.12), the
Revision 2 boundary-test additions (Revision 2 Section 7.6), and this
revision's two new mutation-test artifacts (Section 6.8, Section 7.6)
together constitute the complete Track 2 mutation battery required before
regression re-run (Section 7.5, unchanged).

## 8. Exact scope, path inventories, and consolidated matrix (full rewrite, closes `S8-CAND-BCP-REV3-ARCH-001`)

### 8.1 Single ordering authority (resolves the re-review's explicit question)

**The single, unambiguous ordering authority for every exact inventory in
this proposal is one flattened, combined list per track, sorted in
strict `LC_ALL=C` byte order over the full repository-relative path
string** (case-sensitive; uppercase ASCII letters sort before lowercase
ASCII letters; `/` is byte `0x2F`). This is the same ordering already
used, and correctly used, throughout the certified S8-RR-002 and
S8-RR-003 scope manifests and verifiers this correction family is modeled
on.

**This resolves the re-review's explicit question ("state unambiguously
whether scope-manifest category lists or a flattened combined list carry
the ordering requirement") in favor of the flattened combined list.**
Category and purpose annotations (`MODIFIED` vs. `NEW`; sub-purpose notes
such as "Track 1 dependency") appear **inline**, next to each entry, in
Sections 8.2 and 8.3 below; they are informational tags only and never
define, re-partition, or override the one true order. Every scope
manifest, every verifier's hardcoded expected list, and every mutation
test in this correction family must sort its category-internal arrays (if
any exist inside a scope manifest for narrative grouping) consistently
with this same single global order when flattened, and must ultimately
compare against this exact flattened sequence for exact-list equality.

### 8.2 Exact Track 1 inventory (37 files: 3 modified, 34 new; recomputed)

Numbered 1-37 in strict `LC_ALL=C` order. This is the sole authoritative
Track 1 path list; it supersedes Revision 3 Section 8.2 in full.

1. `SHA256SUMS` -- MODIFIED (root ledger successor, Section 6.7)
2. `docs/review/evidence/RCC_002_S8CANDBCP_REV2_NORMATIVE_LEDGER_HISTORICAL_COPY_2026-08-01.txt` -- NEW (ledger subtrack)
3. `docs/review/evidence/RCC_002_S8CANDBCP_REV2_NORMATIVE_LEDGER_SCOPE_V1.json` -- NEW (ledger subtrack)
4. `docs/review/evidence/RCC_002_S8CANDBCP_REV2_TRACK1_NORMATIVE_SCOPE_V1.json` -- NEW (Track 1 scope manifest)
5. `docs/specifications/RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md` -- MODIFIED (`0.8.0` -> `0.9.0`)
6. `docs/specifications/RCC_002_REPRODUCIBILITY_AND_MANIFEST_2026-07-23.md` -- MODIFIED (`0.9.0` -> `0.9.1`)
7. `registries/rcc002/views/s8_view_schema_fingerprint_profile.v1.json` -- NEW (fingerprint registry, Section 6.4)
8. `schemas/rcc002/manifests/dataset-manifest/1.0.2.schema.json` -- NEW (Dataset Manifest successor schema)
9. `scripts/rcc002/verify_s8candbcp_rev2_normative_ledger.py` -- NEW (ledger subtrack)
10. `scripts/rcc002/verify_s8candbcp_rev2_track1_normative_scope.py` -- NEW (Track 1 verifier)
11. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/complete-valid.json` -- NEW (positive fixture, 8 replacements, Section 6.1)
12. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/minimal-valid.json` -- NEW (positive fixture, 7 replacements, Section 6.1)
13. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/CASE_LEDGER.json` -- NEW (22 entries, Section 6.5)
14. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/absolute-path.json` -- NEW (ported)
15. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/duplicate-specification.json` -- NEW (ported)
16. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/duplicate-view.json` -- NEW (ported)
17. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/extra-property.json` -- NEW (ported)
18. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/invalid-id.json` -- NEW (ported)
19. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/invalid-timestamp.json` -- NEW (ported)
20. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/missing-required-field.json` -- NEW (ported)
21. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/missing-specification.json` -- NEW (ported)
22. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/missing-view.json` -- NEW (ported)
23. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/path-traversal.json` -- NEW (ported)
24. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/reordered-specification.json` -- NEW (ported)
25. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/reordered-view.json` -- NEW (ported)
26. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/secret-like-field.json` -- NEW (ported)
27. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/secret-like-value.json` -- NEW (ported)
28. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/stale-specification-version.json` -- NEW (ported)
29. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/unknown-specification.json` -- NEW (ported)
30. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/unknown-view.json` -- NEW (ported)
31. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/wrong-schema-identity.json` -- NEW (ported)
32. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/wrong-schema-version.json` -- NEW (ported)
33. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/wrong-type-nullability.json` -- NEW (ported)
34. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/wrong-view-allowlist-hash.json` -- NEW (ported)
35. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/wrong-view-fingerprint-hash.json` -- NEW (new case, Section 6.5)
36. `tests/rcc002/test_s8candbcp_rev2_normative_ledger.py` -- NEW (ledger subtrack mutation tests)
37. `tests/rcc002/test_s8candbcp_rev2_track1_normative_scope.py` -- NEW (Track 1 scope-verifier mutation tests, Section 6.8)

**Category totals:** 3 modified (items 1, 5, 6) + 34 new (all remaining
items) = **37 total**, matching Section 6.7's `added = 34` exactly.

### 8.3 Exact Track 2 inventory (25 files: 20 modified, 5 new; recomputed)

Numbered 1-25 in strict `LC_ALL=C` order. This is the sole authoritative
Track 2 path list; it supersedes Revision 3 Section 8.3 in full.

1. `docs/review/evidence/RCC_002_S8CANDBCP_REV2_TRACK2_IMPLEMENTATION_SCOPE_V1.json` -- NEW (Track 2 scope manifest)
2. `rcc002/canonical.py` -- NEW (shared canonicalization authority, Section 7.1)
3. `rcc002/s0/source_identity.py` -- MODIFIED (delegates to `rcc002/canonical.py`)
4. `rcc002/s8/artifact_class.py` -- MODIFIED
5. `rcc002/s8/canonical.py` -- MODIFIED (delegates to `rcc002/canonical.py`)
6. `rcc002/s8/identity.py` -- MODIFIED
7. `rcc002/s8/manifests/dataset.py` -- MODIFIED (Track 1 dependency, Section 6.10)
8. `rcc002/s8/manifests/run.py` -- MODIFIED (run-ID grammar, Section 7.3)
9. `rcc002/s8/manifests/stage.py` -- MODIFIED (run-ID grammar, Section 7.3)
10. `rcc002/s8/publication.py` -- MODIFIED
11. `rcc002/s8/states.py` -- MODIFIED
12. `rcc002/s8/validation.py` -- MODIFIED
13. `rcc002/s8/views.py` -- MODIFIED (Track 1 dependency, Section 6.10)
14. `scripts/rcc002/verify_s8candbcp_rev2_track2_implementation_scope.py` -- NEW (Track 2 verifier)
15. `tests/fixtures/rcc002/canonicalization/rcc_json_canonicalization_v1.golden.v1.json` -- NEW (canonicalization golden fixture, Section 7.2, closes `S8-CAND-BCP-REV3-B01`)
16. `tests/rcc002/s0/test_source_identity.py` -- MODIFIED
17. `tests/rcc002/s8/test_artifact_class.py` -- MODIFIED
18. `tests/rcc002/s8/test_canonical.py` -- MODIFIED
19. `tests/rcc002/s8/test_identity.py` -- MODIFIED
20. `tests/rcc002/s8/test_manifests.py` -- MODIFIED (Track 1 dependency for `dataset.py`/`views.py`; Track-1-independent for `run.py`/`stage.py` run-ID coverage)
21. `tests/rcc002/s8/test_publication.py` -- MODIFIED
22. `tests/rcc002/s8/test_states.py` -- MODIFIED
23. `tests/rcc002/s8/test_validation.py` -- MODIFIED
24. `tests/rcc002/s8/test_views.py` -- MODIFIED (Track 1 dependency, Section 6.10)
25. `tests/rcc002/test_s8candbcp_rev2_track2_implementation_scope.py` -- NEW (Track 2 scope-verifier mutation tests, Section 7.6)

**Category totals:** 5 new (items 1, 2, 14, 15, 25) + 20 modified (all
remaining items) = **25 total**.

**No other repository file may be modified under either track, and this
proposal does not itself modify any of them.**

### 8.4 Exact hardcoded-verifier requirements (unchanged in principle, counts updated)

Unchanged in principle from Revision 3 Section 8.4: each of the four
verifiers now in this correction family --
`scripts/rcc002/verify_s8candbcp_rev2_track1_normative_scope.py`,
`scripts/rcc002/verify_s8candbcp_rev2_track2_implementation_scope.py`,
`scripts/rcc002/verify_s8candbcp_rev2_normative_ledger.py`, and the two
new mutation-test artifacts that exercise the first two of them
(Section 6.8, Section 7.6) -- must hold their own hardcoded expected
counts (37/3/34 for Track 1; 25/5/20 for Track 2; 179/145/34/2/0 for the
ledger), compare against the scope manifest and the actual tree with
exact list equality **in the Section 8.1 flattened order**, and reject
every missing, extra, duplicated, reordered, miscategorized, unsafe, or
undeclared entry, emitting one deterministic pass/fail result identifying
the exact invariant violated on failure.

### 8.5 Consolidated version/path/artifact matrix (updated)

| Item | Exact value |
|---|---|
| Data Pipeline Specification successor version | `0.9.0` (binding, unchanged) |
| RM successor version | `0.9.1` (binding, unchanged) |
| Fingerprint registry path / identity / version | `registries/rcc002/views/s8_view_schema_fingerprint_profile.v1.json` / `RCC002_S8_VIEW_SCHEMA_FINGERPRINT_PROFILE_V1` / `1.0.0` (binding) |
| Fingerprint registry `status` lifecycle | Fixed at `"candidate_for_normative_review"` at byte-finalization; `"certified"` is never a value stored in the file (Section 6.4) |
| Dataset Manifest successor schema version / path | `1.0.2` / `schemas/rcc002/manifests/dataset-manifest/1.0.2.schema.json` (binding) |
| Dataset Manifest `1.0.2` positive / negative / case-ledger counts | 2 / 22 / 22 (unchanged) |
| View schema identities/versions | Unchanged: `research-features`/`1.0.0`, `backtest-inputs`/`1.0.0`, `paper`/`1.0.0`, `live`/`1.0.0`, `label-research`/`1.0.0`, `audit`/`2.0.0` |
| Canonicalization shared-authority module | `rcc002/canonical.py` (unchanged) |
| Canonicalization golden fixture path | `tests/fixtures/rcc002/canonicalization/rcc_json_canonicalization_v1.golden.v1.json` -- **now in the exact Track 2 inventory (Section 8.3, item 15)** |
| Run-ID grammar | Unchanged (Revision 2 Section 7.3) |
| Golden preimage example count | Exactly two, everywhere in this document (unchanged) |
| Ordering authority | One flattened, combined, `LC_ALL=C`-sorted list per track (Section 8.1) |
| Track 1 scope manifest / verifier / mutation tests | `docs/review/evidence/RCC_002_S8CANDBCP_REV2_TRACK1_NORMATIVE_SCOPE_V1.json` / `scripts/rcc002/verify_s8candbcp_rev2_track1_normative_scope.py` / `tests/rcc002/test_s8candbcp_rev2_track1_normative_scope.py` (new) |
| Track 2 scope manifest / verifier / mutation tests | `docs/review/evidence/RCC_002_S8CANDBCP_REV2_TRACK2_IMPLEMENTATION_SCOPE_V1.json` / `scripts/rcc002/verify_s8candbcp_rev2_track2_implementation_scope.py` / `tests/rcc002/test_s8candbcp_rev2_track2_implementation_scope.py` (new) |
| Ledger historical copy / scope / verifier / tests | Section 6.7, four artifacts, Section 8.2 items 2, 3, 9, 36 |
| **Track 1 exact file count** | **37 (3 modified, 34 new)** |
| **Track 2 exact file count** | **25 (20 modified, 5 new)** |
| **Successor root ledger entry count** | **179 (145 baseline + 34 added - 0 removed; 2 replaced, count-neutral)** |

## 9. Documentation corrections applied throughout

- Every count in this document (37, 34, 3, 25, 20, 5, 179, 34, 2, 0) is
  freshly recomputed from the final Section 8.2/8.3 path sets (Section 2,
  Section 6.7, Section 8), not copied forward from Revision 3.
- Overlaps between the baseline 145-entry ledger and the Track 1 new-path
  set are determined set-wise: independent inspection (Section 2,
  reaffirming the controlling re-review's own Section 4.6 finding) confirms
  none of the 34 new Track 1 paths already exists in the current 145-entry
  ledger, so the added/baseline overlap is the empty set and the successor
  count is a simple sum minus zero.
- All findings the controlling re-review marked `CLOSED`
  (`S8-CAND-BCP-REV2-B01`, `S8-CAND-BCP-REV2-ARCH-001`,
  `S8-CAND-BCP-REV2-ARCH-003`, `S8-CAND-BCP-REV2-DOC-001`) are unchanged
  in this revision and are not reopened by any Revision 4 correction.
- Dataset Manifest `1.0.0`, Dataset Manifest `1.0.1`, and their complete
  historical fixture families remain byte-immutable; no Revision 4
  correction touches any byte of them (Section 6.5, unchanged).
- No section of this document states or implies that Revision 4 itself
  authorizes Track 1 artifact generation, Track 2 implementation, S8
  candidate resubmission, S8 certification, dataset generation, dataset
  publication, or deployment (Section 12, Section 13).

## 10. Fail-closed sequencing (updated diagram)

```text
                    +-----------------------------------------------+
                    | Track 1: Normative correction                   |
                    | Sections 6.1-6.10                                |
                    | (fingerprint contract + Dataset Manifest 1.0.2   |
                    |  successor + normative-ledger successor, 179     |
                    |  entries, + Track 1 scope-verifier mutation      |
                    |  tests, Section 6.8)                             |
                    +-----------------------------------------------+
                                     |
     Draft (Section 6.6 step 1) -> Byte-finalize registry incl.
     permanent status (step 2) -> Byte-finalize Data Pipeline 0.9.0
     (step 3) -> Byte-finalize RM 0.9.1 (step 4) -> Compute document
     hashes (step 5) -> Byte-finalize Dataset Manifest 1.0.2 schema
     (step 6) -> Byte-finalize fixtures (step 7) -> Byte-finalize
     successor ledger, 179 entries (step 8) -> Verify (step 9) ->
     Independently review (step 10) -> Certify externally, zero
     further mutation (step 11)
                                     |
                                     v
                    [ GATE: Track 1 certified? ]
                     NO  -------------------------------> STOP.
                     |                                    No implementation of the
                     |                                    fingerprint formula. No
                     |                                    real schema_fingerprint_sha256
                     |                                    may be emitted (Section 6.10).
                     |                                    No successor SHA256SUMS is
                     |                                    published (Section 6.7).
                     YES
                     |
                     v
     +---------------------------------------------------------------+
     | Track 2: Implementation repair (Section 7; exact 25-file         |
     | inventory, Section 8.3, now including the canonicalization       |
     | golden fixture and the Track 2 scope-verifier mutation tests --  |
     | independent of Track 1 and MAY start in parallel with Track 1    |
     | drafting)                                                        |
     +---------------------------------------------------------------+
                     |
                     v
     [ GATE: all Track-2 findings closed AND regression re-run       ]
     [        (focused S8 / complete RCC-002 / S0 identity / TD-005)  ]
     [        all green (Section 7.5, unchanged)?                     ]
                     |
                     v
     +---------------------------------------------------------------+
     | View-schema fingerprint formula implementation (only after the |
     | Track 1 gate above is YES) in rcc002/s8/views.py and             |
     | rcc002/s8/manifests/dataset.py                                   |
     +---------------------------------------------------------------+
                     |
                     v
     [ GATE: both tracks fully closed, every finding across all four  ]
     [        review cycles satisfied?                                 ]
                     |
                     v
          New independent scientific and architecture re-review
          of the corrected candidate, including a fresh
          proposal-conformance check against this Revision 4 document
                     |
                     v
          [ Re-review decision: ACCEPT or REJECT ]
                     |
            ACCEPT --+-- REJECT --> back to the relevant track above
                     |
                     v
     Candidate certification (a separate act from this proposal and
     from the re-review itself)
                     |
                     v
     S8 implementation remains bounded by RR-004 Sections 9-10.
     Dataset generation, publication, and deployment remain
     separately unauthorized regardless of certification (Section 11).
```

## 11. Preservation, prohibition, and re-review requirements (unchanged in substance)

- **Historical preservation.** No certified historical artifact --
  including Data Pipeline `0.8.0` and RM `0.9.0` themselves (preserved via
  git history, Section 6.3), the certified Dataset Manifest `1.0.0` and
  `1.0.1` schemas and their complete fixture families (Section 6.5), the
  current 145-entry `SHA256SUMS` (preserved as an immutable historical
  evidence copy, Section 6.7), and the certified S8-RR-003 ledger
  scope/verifier -- may be modified except through an explicit versioned
  successor certified through the normal correction-cycle process. This
  proposal does not itself modify, and does not authorize modifying, any
  such artifact.
- **No dataset generation, publication, or deployment**, at any point in
  this proposal, including after both tracks close and a corrected
  candidate is certified.
- **No S8 production code from this proposal.**
- **Mandatory new independent review** after both tracks close, before
  any certification decision, re-running the complete adverse-mutation
  matrix (Revision 1 Section 6.12, Revision 2 Section 7.6, Revision 3
  Section 6.7 ledger mutations, and this revision's Section 6.8/Section 7.6
  scope-verifier mutations) outside the candidate tree.
- **Decision separation, restated.** Proposal approval (this document),
  normative contract certification (Track 1 output, Section 6.6 step 11),
  implementation repair authorization (Track 2 start), candidate
  re-certification (the required re-review's outcome), and S8/dataset
  readiness (RR-004, unaffected by this proposal in either direction)
  remain five separate decisions. Approving this proposal approves only
  the plan in Sections 5 through 10; it does not itself grant any of the
  other four.

## 12. Restrictions honored while preparing this revision

- No repository file was created, modified, deleted, renamed, staged,
  committed, or pushed.
- The existing S8 candidate (`rcc002/s8/`, `tests/rcc002/s8/`) was treated
  strictly read-only: not modified, staged, committed, or pushed.
- No implementation code was run. No test was executed.
- No dependency was installed. No network access was used.
- No dataset was generated or published.
- No S8 production code was created.
- `scripts/build_rcc002_spec_bundle.py` was not read, hashed, inspected,
  opened, executed, imported, copied, renamed, deleted, modified,
  staged, or packaged; it appears only in the document-control table's
  worktree-state row, Section 6.7's exclusion statement, and this
  restrictions section.
- All diagnostics performed to prepare this revision were passive
  (branch/HEAD/origin/status checks, read-only file inspection, and
  in-memory reasoning); none created a repository artifact.
- The only filesystem write performed while preparing this revision was
  this single output Markdown file, outside the repository, in
  `/mnt/c/Users/benja/Downloads/`.

## 13. Final statement

Revision 4 closes all four findings raised against Revision 3
(`S8-CAND-BCP-REV3-B01`, `S8-CAND-BCP-REV3-B02`,
`S8-CAND-BCP-REV3-ARCH-001`, `S8-CAND-BCP-REV3-TEST-001`) by adding the
canonicalization golden fixture to the exact, closed Track 2 inventory;
redefining the fingerprint registry's `status` lifecycle so no artifact
byte changes after verification, review, or certification; rewriting both
exact inventories as single, true `LC_ALL=C`-ordered, fully renumbered
lists with one explicit ordering authority; and adding one dedicated
mutation-test artifact for each of the Track 1 and Track 2 exact-scope
verifiers -- while leaving every already-closed finding from the three
prior review cycles unchanged and unreopened, and while continuing to
withhold the one decision that has never belonged to this proposal: the
actual View-schema-fingerprint preimage formula, reserved exclusively for
the independently reviewed and certified Track 1 normative correction
artifact (Section 3).

**This proposal, by itself, does not authorize and does not perform S8
implementation repair, View-schema-fingerprint formula selection or
emission, corrected-candidate resubmission, dataset generation, dataset
publication, or live or paper deployment. Every one of those actions
remains unauthorized unless and until the sequencing in Section 10 and
the requirements in Section 11 are satisfied in full, through acts
entirely separate from, and later than, this proposal document itself.**
