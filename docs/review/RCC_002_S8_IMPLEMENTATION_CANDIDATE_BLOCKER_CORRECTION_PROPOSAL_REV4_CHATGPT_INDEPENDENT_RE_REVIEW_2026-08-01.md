# RCC-002 S8 Implementation Candidate Blocker Correction Proposal Revision 4 - ChatGPT Independent Re-Review

## Document control

| Field | Value |
|---|---|
| Review ID | `RCC-002-S8-CAND-BCP-REV4-CHATGPT-IRR-001` |
| Review date | `2026-08-01` |
| Reviewer | ChatGPT independent scientific and architecture reviewer |
| Review class | Strict read-only independent re-review of proposal Revision 4 |
| Repository baseline | `ed57983f27678222e59148db1cda188e9b2c7d77` |
| Review package | `RCC_002_S8_IMPLEMENTATION_CANDIDATE_CORRECTION_PROPOSAL_REV4_REVIEW_INPUT_2026-08-01.zip` |
| Review package SHA-256 | `2cf3ad4fe44f6752d0e97d82cb664b88cedd12f255e987475b3106fafec88227` |
| Proposal reviewed | `RCC_002_S8_IMPLEMENTATION_CANDIDATE_BLOCKER_CORRECTION_PROPOSAL_REV4_2026-08-01.md` |
| Proposal SHA-256 | `c6599223d16aff064ee442a7df3a2da3ec9b766d636369328a1b30321939398c` |
| Controlling prior re-review | `RCC_002_S8_IMPLEMENTATION_CANDIDATE_BLOCKER_CORRECTION_PROPOSAL_REV3_CHATGPT_INDEPENDENT_RE_REVIEW_2026-08-01.md` |
| Controlling prior re-review SHA-256 | `6a465272360215ff7c28881189c40914bc1673cbb79e23199db1c3dc7c9dc2c0` |
| Final decision | **REJECT** |

## 1. Review question and restrictions

This review asks whether Revision 4 closes the four findings from the
controlling Revision 3 re-review with one exact, internally consistent,
deterministic, and executable correction contract, without introducing a new
blocker or major architecture defect.

The review was read-only with respect to the supplied snapshot. No project
file in the snapshot was created, modified, deleted, renamed, or moved. No
dependency was installed. No network access was used. No dataset was generated
or published. No repository command that stages, commits, or pushes was run.
The protected file `scripts/build_rcc002_spec_bundle.py` was absent from the
review package and was not accessed.

## 2. Package and baseline verification

The following checks passed independently:

1. The package SHA-256 is exactly
   `2cf3ad4fe44f6752d0e97d82cb664b88cedd12f255e987475b3106fafec88227`.
2. The ZIP contains no absolute path and no parent-traversal component.
3. The protected builder is absent.
4. The extracted snapshot contains exactly 1,671 files.
5. The candidate boundary contains exactly 33 Python files under
   `rcc002/s8/` and `tests/rcc002/s8/`, and no non-Python candidate file.
6. The Revision 4 proposal SHA-256 is exactly
   `c6599223d16aff064ee442a7df3a2da3ec9b766d636369328a1b30321939398c`.
7. The controlling Revision 3 re-review SHA-256 is exactly
   `6a465272360215ff7c28881189c40914bc1673cbb79e23199db1c3dc7c9dc2c0`.
8. The proposal is ASCII, LF-only, has no BOM, has no CR, has no trailing
   horizontal whitespace, has exactly one trailing newline, has balanced code
   fences, and contains exactly 772 lines.
9. The current root `SHA256SUMS` contains exactly 145 unique paths in
   `LC_ALL=C` order.

## 3. Evidence inspected

The review inspected at least the following evidence:

- Revision 4 and its controlling Revision 3 re-review;
- Revision 3 and Revision 2 where Revision 4 incorporates requirements by
  reference;
- the original S8 implementation candidate review;
- the current Data Pipeline and Reproducibility and Manifest specifications;
- Dataset Manifest schemas `1.0.0` and `1.0.1`;
- the complete Dataset Manifest `1.0.1` positive and negative fixture family;
- the current 145-entry root `SHA256SUMS`;
- the existing S8-RR-002 and S8-RR-003 scope, verifier, and mutation-test
  precedent;
- the existing release artifact registry used by Revision 4 as lifecycle
  precedent; and
- the uncommitted 33-file S8 candidate boundary.

The two Revision 4 inventories were extracted programmatically and checked for
sequence numbering, total count, change-category count, uniqueness, path
safety, true `LC_ALL=C` order, baseline existence classification, and overlap
with the current root ledger.

## 4. Independent verification results

### 4.1 Track 1 inventory

The Track 1 list contains exactly 37 unique paths:

- 3 paths classified as `MODIFIED`;
- 34 paths classified as `NEW`;
- all 37 paths in true `LC_ALL=C` order;
- no duplicate, absolute, parent-traversal, or backslash path;
- all 3 modified paths present in the snapshot; and
- all 34 new paths absent from the snapshot and absent from the current
  145-entry ledger.

The path-count arithmetic is therefore numerically correct:

```text
145 baseline paths + 34 genuinely new paths - 0 removed paths = 179 paths
```

The two specification replacements are count-neutral. The root ledger does not
list itself, and the protected-builder path is absent from every inventory.

### 4.2 Track 2 inventory

The Track 2 list contains exactly 25 unique paths:

- 20 paths classified as `MODIFIED`;
- 5 paths classified as `NEW`;
- all 25 paths in true `LC_ALL=C` order;
- no duplicate, absolute, parent-traversal, or backslash path;
- all 20 modified paths present in the supplied candidate snapshot; and
- all 5 new paths absent from the supplied baseline.

The mandatory external canonicalization fixture is now present as exact item
15:

`tests/fixtures/rcc002/canonicalization/rcc_json_canonicalization_v1.golden.v1.json`

Its location, role, and single-authority requirement remain consistent with
the incorporated Revision 2 contract.

### 4.3 Registry lifecycle

Revision 4 eliminates the post-review registry mutation. The exact registry
contract now permits only `"draft"` and
`"candidate_for_normative_review"`; the byte-final artifact is fixed at
`"candidate_for_normative_review"`, and `"certified"` is not a stored registry
value.

This is consistent with the repository precedent cited by the proposal:
`registries/rcc002/release/release_artifact_class_registry.v1.json` permanently
contains `"candidate_for_normative_review"` and is already represented in the
certified root ledger. Certification is correctly moved outside the registry
payload, so certification does not change the reviewed registry hash.

### 4.4 Scope-verifier mutation contracts

Revision 4 adds one exact focused test artifact per new scope verifier:

- `tests/rcc002/test_s8candbcp_rev2_track1_normative_scope.py`; and
- `tests/rcc002/test_s8candbcp_rev2_track2_implementation_scope.py`.

Each contract requires the nine requested classes:

1. missing entry;
2. extra entry;
3. duplicate entry;
4. reordered entry;
5. miscategorized entry;
6. absolute path;
7. parent traversal;
8. incorrect or forged metadata; and
9. unchanged positive control.

Both test artifacts are in their respective exact inventories. The Track 1
test is also included in the recomputed successor-ledger arithmetic.

### 4.5 Historical Dataset Manifest preservation and prior closures

Revision 4 preserves the already-correct contracts for:

- exact 7/7/8 fingerprint replacement counts;
- artifact-to-view fingerprint semantic equality;
- the permanent RM specification-profile self-hash placeholder distinction;
- exact Dataset Manifest `1.0.2` positive, negative, and case-ledger counts;
- byte-immutable Dataset Manifest `1.0.0` and `1.0.1` artifacts;
- binding successor versions;
- inclusion of `run.py` and `stage.py` in Track 2;
- the shared `rcc002/canonical.py` architecture;
- the run-ID grammar; and
- the closed seven-entry specification profile.

No contradiction was found in these carried-forward decisions.

## 5. Closure assessment of the four controlling findings

| Controlling finding | Assessment | Rationale |
|---|---|---|
| `S8-CAND-BCP-REV3-B01` | **CLOSED** | The mandatory canonicalization golden fixture is now a declared Track 2 output, and the 25/20/5 counts agree. |
| `S8-CAND-BCP-REV3-B02` | **CLOSED narrowly** | The registry itself is byte-final before verification and is never mutated after review or certification. A broader Track 1 finalization defect is recorded separately below. |
| `S8-CAND-BCP-REV3-ARCH-001` | **CLOSED** | Both flattened inventories are actually in strict `LC_ALL=C` order and are the stated ordering authority. |
| `S8-CAND-BCP-REV3-TEST-001` | **CLOSED** | Both scope verifiers now have dedicated mutation-test artifacts with the required adverse cases and positive control. |

## 6. New material findings

### 6.1 `S8-CAND-BCP-REV4-ARCH-001` - MAJOR - the exact ledger sequence does not byte-finalize every ledgered Track 1 artifact

**Locations:** Revision 4 Sections 6.6-6.8 and 8.2, especially Section 6.6
step 8.

Revision 4 establishes a correct governing principle: every artifact must be
byte-final before its digest is entered into the root ledger, and no later
state may change it. Section 6.7 also correctly requires the successor ledger
to contain every one of the 34 new Track 1 paths in Section 8.2.

The exact eleven-step sequence does not finalize that complete set. Step 8
says to hash the artifacts byte-finalized in steps 2-7, plus the two Track 1
mutation-test files, while byte-finalizing the successor ledger and its ledger
scope manifest. Four other new paths that Section 6.7 and Section 8.2 require
in the successor ledger have no explicit byte-finalization point before their
digests are required:

1. `docs/review/evidence/RCC_002_S8CANDBCP_REV2_NORMATIVE_LEDGER_HISTORICAL_COPY_2026-08-01.txt`;
2. `docs/review/evidence/RCC_002_S8CANDBCP_REV2_TRACK1_NORMATIVE_SCOPE_V1.json`;
3. `scripts/rcc002/verify_s8candbcp_rev2_normative_ledger.py`; and
4. `scripts/rcc002/verify_s8candbcp_rev2_track1_normative_scope.py`.

This creates two incompatible operational descriptions:

- Section 6.6 step 8 names a proper subset of the new files whose hashes are
  available for entry into the ledger; but
- Section 6.7 and the exact Section 8.2 inventory require all 34 new paths in
  that ledger.

The omitted files are not merely explanatory documents. Two are the exact
mechanical verifiers that govern acceptance, one is the exact Track 1 scope
manifest, and one is the immutable historical ledger evidence. If any is
edited after its digest is entered, the 179-entry ledger becomes stale. The
proposal's no-post-finalization-mutation rule cannot protect an artifact that
the exact sequence never places into the byte-finalized state.

The contract is repairable and non-circular, but the missing order must be
stated rather than inferred. Before the successor root ledger is finalized,
the sequence must explicitly byte-finalize every non-ledger Track 1 artifact,
including both scope manifests, both verifier scripts, both focused test
modules, the historical copy, registry, specifications, schema, case ledger,
and fixtures. The ledger scope manifest must be finalized before its digest is
entered into the root ledger. Only then may the root `SHA256SUMS` be
byte-finalized. Verification, independent review, and external certification
must remain strictly later and read-only.

Until that complete ordering exists, the proposal does not define one exact
stable 179-entry payload for verification and review. This is a major
architecture defect in the correction contract.

### 6.2 `S8-CAND-BCP-REV4-DOC-001` - MINOR - Section 8.4 miscounts verifiers and conflates them with test artifacts

**Location:** Revision 4 Section 8.4.

The section says there are "four verifiers" but names only three verifier
scripts:

1. Track 1 exact-scope verifier;
2. Track 2 exact-scope verifier; and
3. normative-ledger verifier.

It then joins the two mutation-test modules into the same grammatical subject
and says each must hold verifier expectations. The exact inventory elsewhere
is clear, so this does not change path arithmetic, but it obscures whether the
hardcoded expectation obligation applies to three verifier scripts, five
artifacts, or a nonexistent fourth verifier.

**Required correction:** state "three verifiers" and separately require the
two test modules to hold independent mutated expectations or fixtures as
needed to exercise those three verifiers. Preserve the existing exact paths
and counts.

## 7. Required Revision 5 boundary

A focused Revision 5 can close the remaining defects without reopening any
scientific or implementation decision. It must:

1. keep the exact 37-path Track 1 and 25-path Track 2 inventories unless the
   correction itself necessarily changes a path;
2. explicitly byte-finalize all non-ledger Track 1 artifacts before computing
   their root-ledger entries;
3. place ledger-scope finalization before root-ledger finalization;
4. state that all 34 added paths receive fixed hashes in the 179-entry root
   ledger, while `SHA256SUMS` remains self-excluded;
5. leave verification, independent review, and external certification after
   finalization, with zero mutation of reviewed artifacts;
6. correct Section 8.4 to identify exactly three verifier scripts and two
   separate mutation-test modules; and
7. repeat independent re-review before Track 1 generation or Track 2
   corrected-candidate resubmission.

No change is required to the registry lifecycle, canonicalization fixture,
inventory ordering, successor counts, scope-test paths, fingerprint counts,
Dataset Manifest versions, run-ID grammar, or already-closed scientific
contracts.

## 8. Execution evidence versus static evidence

The proposed Track 1 and repaired Track 2 artifacts do not yet exist, so their
future verifiers and mutation tests cannot be executed in this review. The
review therefore used passive static validation of the proposal and supplied
repository evidence, including direct programmatic extraction and comparison
of both exact inventories and the existing ledger.

No claim is made that future code passes tests. This decision concerns only
whether Revision 4 is a complete, deterministic plan for producing that code
and evidence.

## 9. Confirmation of non-modification

No file inside the supplied snapshot was created, modified, deleted, renamed,
or moved during this review. No dependency was installed. No network access
was used. No staging, commit, push, S8 implementation, dataset generation,
publication, or deployment occurred. The protected builder was absent and was
not accessed.

## 10. Final decision

Revision 4 closes all four findings raised directly against Revision 3. Its
inventories, counts, lexical ordering, canonicalization-fixture inclusion,
registry status lifecycle, and two new scope-verifier mutation-test contracts
are independently verified as correct.

However, the eleven-step sequence still does not explicitly byte-finalize four
new Track 1 artifacts whose hashes the exact 179-entry ledger must contain.
That omission conflicts with the otherwise exact Section 6.7 union and leaves
the final ledger payload insufficiently determined. Because the purpose of
this proposal cycle is a deterministic, fail-closed normative correction and
ledger certification contract, this new major defect prevents approval.

No Track 1 generation, Track 2 corrected-candidate resubmission, S8
certification, dataset generation, publication, or deployment is authorized
by this review.

REJECT
