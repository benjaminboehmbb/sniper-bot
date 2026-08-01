# RCC-002 S8 Implementation Candidate Blocker Correction Proposal Revision 3 - ChatGPT Independent Re-Review

## Document control

| Field | Value |
|---|---|
| Review ID | `RCC-002-S8-CAND-BCP-REV3-CHATGPT-IRR-001` |
| Review date | `2026-08-01` |
| Reviewer | ChatGPT independent scientific and architecture reviewer |
| Review class | Strict read-only independent re-review of proposal Revision 3 |
| Repository baseline | `29b3a0c8e2fbba5fbf196271e95ebd294a56f446` |
| Review package | `RCC_002_S8_IMPLEMENTATION_CANDIDATE_CORRECTION_PROPOSAL_REV3_REVIEW_INPUT_2026-08-01.zip` |
| Review package SHA-256 | `ca6c3f720cb948c1f90308a565b10ac548814d2d4f1bc14ee87975bd601c4cb1` |
| Proposal reviewed | `RCC_002_S8_IMPLEMENTATION_CANDIDATE_BLOCKER_CORRECTION_PROPOSAL_REV3_2026-08-01.md` |
| Proposal SHA-256 | `a2fb61f278586c9ee14a060766a4061c59b59d3bd210a199fd43b9325cf99d00` |
| Controlling prior re-review | `RCC_002_S8_IMPLEMENTATION_CANDIDATE_BLOCKER_CORRECTION_PROPOSAL_REV2_CHATGPT_INDEPENDENT_RE_REVIEW_2026-08-01.md` |
| Controlling prior re-review SHA-256 | `99b686c21025e1a2f49a456fd4d5852437b61b5098df8674d50b548037e6a51a` |
| Final decision | **REJECT** |

## 1. Review scope and restrictions

This review asks one question only: does Revision 3 close all seven findings
from the controlling Revision 2 re-review with an exact, deterministic, and
executable correction contract, without creating a new blocker or major
architecture defect?

The review was read-only with respect to the supplied snapshot. No project
file in the snapshot was created, modified, deleted, renamed, staged,
committed, or pushed. No dependency was installed. No network access was
used. No dataset was generated or published. The protected file
`scripts/build_rcc002_spec_bundle.py` was confirmed absent from the review
package and was not accessed.

## 2. Package and baseline verification

The following checks passed independently:

1. The package SHA-256 is exactly
   `ca6c3f720cb948c1f90308a565b10ac548814d2d4f1bc14ee87975bd601c4cb1`.
2. The ZIP contains no absolute path and no parent-traversal component.
3. The protected builder is absent.
4. The extracted snapshot contains 1,669 files.
5. The candidate boundary contains exactly 33 Python files under
   `rcc002/s8/` and `tests/rcc002/s8/`.
6. The Revision 3 proposal hash is exactly
   `a2fb61f278586c9ee14a060766a4061c59b59d3bd210a199fd43b9325cf99d00`.
7. The controlling prior re-review hash is exactly
   `99b686c21025e1a2f49a456fd4d5852437b61b5098df8674d50b548037e6a51a`.
8. The proposal is ASCII, LF-only, has no BOM, has one trailing newline,
   has no trailing horizontal whitespace, has balanced code fences, and has
   exactly 1,039 lines.

## 3. Evidence inspected

The review inspected at least the following evidence:

- Revision 3 and its controlling Revision 2 re-review;
- Revision 2 where Revision 3 incorporates requirements by reference;
- the original S8 implementation candidate review and all nine original
  candidate findings;
- the current Data Pipeline and Reproducibility and Manifest specifications;
- Dataset Manifest schemas `1.0.0` and `1.0.1`;
- both positive Dataset Manifest `1.0.1` fixtures;
- the 21 negative Dataset Manifest `1.0.1` fixtures and their case ledger;
- the current 145-entry root `SHA256SUMS`;
- the current S8 candidate and its focused tests;
- the existing S8-RR-002 and S8-RR-003 scope/verifier/test precedent.

The exact Track 1 and Track 2 inventories were also extracted from the
proposal and compared programmatically for count, sequence numbering,
uniqueness, path safety, lexical order, baseline-ledger overlap, and required
artifact coverage.

## 4. Independently confirmed positive results

Revision 3 makes substantial and useful progress.

### 4.1 Fingerprint replacement counts are now correct

Independent JSON parsing confirmed:

| Artifact | Views | Artifacts | Zero View fingerprints | Zero artifact fingerprints | Total View-fingerprint replacements |
|---|---:|---:|---:|---:|---:|
| `1.0.1/minimal-valid.json` | 6 | 1 | 6 | 1 | 7 |
| `1.0.1/complete-valid.json` | 6 | 2 | 6 | 2 | 8 |

The complete fixture's two artifacts reference different schemas:
`rcc002.view.audit/2.0.0` and `rcc002.view.label-research/1.0.0`.
Revision 3 correctly requires two independently matched fingerprint literals.

The RM Section 24 example contains exactly seven zero-valued
`schema_fingerprint_sha256` occurrences: six in `views[]` and one in
`artifacts[]`. Revision 3 correctly separates these from the RM
`specification_profile[]` self-hash placeholder.

### 4.2 The artifact-to-view semantic equality rule is explicit

Section 6.1 now requires every
`artifacts[].schema_fingerprint_sha256` to equal the registered literal for
the artifact's own `schema_ref`. This correctly closes the prior ambiguity
created by the variable-length artifact array.

### 4.3 Historical Dataset Manifest evidence is preserved

Revision 3 correctly introduces Schema `1.0.2` and new fixtures while
preserving Schema `1.0.0`, Schema `1.0.1`, and their historical fixtures.
The exact 22-file negative-fixture list is the 21 existing cases plus
`wrong-view-fingerprint-hash.json`, with an exact 22-entry case ledger.

### 4.4 The registry container is materially more exact

Section 6.4 specifies:

- an exact path and identity;
- seven top-level keys;
- a closed three-key `owning_specification` object;
- a closed twelve-key View object;
- six ordered View entries;
- exact cardinalities and types; and
- `additionalProperties: false` at every described object boundary.

The proposal also preserves the necessary separation between defining the
registry container and selecting the normative fingerprint algorithm.

### 4.5 Version decisions are now binding

The proposal unambiguously binds:

- Data Pipeline `0.9.0`;
- RM `0.9.1`;
- fingerprint registry `1.0.0`;
- Dataset Manifest `1.0.2`; and
- unchanged View schema versions.

Any version change requires a new proposal revision and independent review.
This closes `S8-CAND-BCP-REV2-ARCH-003`.

### 4.6 Ledger arithmetic is numerically correct

Independent inspection confirmed that the root ledger has 145 entries and
already contains both specification paths that Track 1 will modify. None of
the 33 paths classified as new in Section 8.2 is already in the ledger.
Therefore the path-count arithmetic is correct:

```text
145 baseline paths + 33 genuinely new paths - 0 removed paths = 178 paths
```

The two specification replacements are count-neutral. Root self-entry and
protected-builder exclusions are also correctly stated.

### 4.7 The omitted Run and Stage builders are now present

The Track 2 inventory includes both:

- `rcc002/s8/manifests/run.py`; and
- `rcc002/s8/manifests/stage.py`.

This closes the narrow omission in `S8-CAND-BCP-REV2-ARCH-001`.

### 4.8 Documentation cleanup is correct

The specification profile is now stated as exactly seven closed entries,
the fixture counts are corrected, and schema consts are distinguished from
fixture document hashes. `S8-CAND-BCP-REV2-DOC-001` is closed.

## 5. Material findings

### 5.1 `S8-CAND-BCP-REV3-B01` - BLOCKER - the exact Track 2 inventory omits its mandatory canonicalization golden fixture

**Locations:** Revision 3 Sections 7, 8.3, and 8.5; incorporated Revision 2
Section 7.2.

Revision 3 says Revision 2 Section 7.2 remains mandatory and repeats the
exact required new path in Section 8.5:

`tests/fixtures/rcc002/canonicalization/rcc_json_canonicalization_v1.golden.v1.json`

That file does not exist in the baseline snapshot. It must therefore be a new
Track 2 output. However, Section 8.3 declares a closed, exact Track 2
inventory of 23 files, with exactly three new files, and the golden fixture
is not one of them.

The contradiction is fail-closed:

- creating the mandatory fixture violates the exact 23-file scope and the
  instruction that no other repository file may be modified;
- omitting it violates the mandatory external-evidence requirement used to
  close `S8-CAND-B01` and `S8-CAND-TEST-001`; and
- the Track 2 verifier is required to reject every undeclared file, so it
  must reject a candidate that correctly creates the fixture.

This is not a presentation issue. It makes the correction contract
impossible to satisfy.

**Required correction:** add the golden fixture to the exact Track 2 new-file
inventory, update Track 2 totals, and update the Track 2 scope/verifier
expectations. The fixture must remain the single external authority described
in Revision 2 Section 7.2.

### 5.2 `S8-CAND-BCP-REV3-B02` - BLOCKER - certification changes registry bytes after verification and independent review

**Locations:** Revision 3 Sections 6.4 and 6.6, especially step 10.

Section 6.6 correctly tries to make all payload bytes final before exact-scope
verification and independent review. But step 10 then says certification
updates the fingerprint registry's `status` from its pre-certification value
to `"certified"`.

That update changes the registry bytes after:

1. the Track 1 verification in step 8;
2. the independent review in step 9; and
3. preparation of the successor ledger entry for the registry.

Consequently the final registry SHA-256 differs from the value reviewed and
from the value recorded in the 178-entry `SHA256SUMS`. There is no valid
ordering that satisfies the current text:

- if the ledger records the pre-certification bytes, it is stale after step
  10;
- if it records the future post-certification bytes, `sha256sum -c` cannot
  pass during step 8; and
- if `status` is set to `"certified"` before step 8, the registry claims a
  certification that has not yet occurred and contradicts the stated status
  transition.

Thus the circularity identified in `S8-CAND-BCP-REV2-ARCH-002` is reduced but
not eliminated. It has moved from document-hash availability to a
post-review byte mutation.

**Required correction:** define one byte-final registry payload and prohibit
all payload mutation after exact verification begins. Certification must be
represented by an external decision over those exact bytes, or the proposal
must define another non-circular lifecycle mechanism. In either case, the
final registry digest must be the digest verified, reviewed, and entered into
the successor ledger.

### 5.3 `S8-CAND-BCP-REV3-ARCH-001` - MAJOR - both inventories falsely claim strict lexical order

**Locations:** Revision 3 Sections 8.2, 8.3, and 8.4.

Both exact inventories are sequentially numbered and unique, and all listed
paths are safe. Neither inventory is in the strict lexical order it claims.

For Track 1, the first inversion is:

```text
tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/wrong-view-fingerprint-hash.json
docs/review/evidence/RCC_002_S8CANDBCP_REV2_TRACK1_NORMATIVE_SCOPE_V1.json
```

For Track 2, the first inversion is:

```text
scripts/rcc002/verify_s8candbcp_rev2_track2_implementation_scope.py
rcc002/s0/source_identity.py
```

Section 8.4 simultaneously requires the verifiers to compare exact lists and
reject reordered entries. Therefore an implementation has two incompatible
authorities: the displayed exact order and actual `LC_ALL=C` order.

**Required correction:** rewrite both exact inventories in true
`LC_ALL=C` order, and state unambiguously whether scope-manifest category
lists or a flattened combined list carry the ordering requirement. The
hardcoded verifier constants, scope manifests, and tests must use the same
one rule.

### 5.4 `S8-CAND-BCP-REV3-TEST-001` - MAJOR - the two new exact-scope verifiers have no mutation-test artifacts

**Locations:** Revision 3 Sections 8.2-8.4.

Revision 3 requires both the Track 1 and Track 2 scope verifiers to reject
missing, extra, duplicate, reordered, miscategorized, unsafe, undeclared, and
truncated entries. Yet the closed inventories contain no focused test module
for either verifier. Only the separate normative-ledger verifier has a named
mutation-test file.

A successful verifier run against one valid scope proves only acceptance of
the positive control. It does not prove fail-closed behavior for the required
adverse mutations. This repository's own S8-RR-002 and S8-RR-003 corrections
established the opposite precedent: scope/ledger verifiers are accompanied by
focused mutation tests because prior defects survived positive-only checks.

The omission is especially material here because Section 8.4 makes exact
ordering and categorization part of the correction's security boundary.

**Required correction:** add one focused mutation-test artifact per new scope
verifier, enumerate the exact adverse cases, update both track inventories and
counts, and update the Track 1 successor-ledger arithmetic for any new Track 1
test path.

## 6. Closure assessment of the seven controlling findings

| Controlling finding | Assessment | Rationale |
|---|---|---|
| `S8-CAND-BCP-REV2-B01` | **CLOSED** | Exact 7/7/8 replacements, artifact-to-view equality, and self-hash distinction are now correct. |
| `S8-CAND-BCP-REV2-B02` | **NOT CLOSED** | Structural contracts are much more exact, but the exact Track 2 inventory omits a mandatory file and both inventories contradict their stated order. |
| `S8-CAND-BCP-REV2-ARCH-001` | **CLOSED** | `run.py` and `stage.py` are included. |
| `S8-CAND-BCP-REV2-ARCH-002` | **NOT CLOSED** | Step 10 still mutates a reviewed and ledgered artifact. |
| `S8-CAND-BCP-REV2-ARCH-003` | **CLOSED** | All successor versions are binding and non-reopenable. |
| `S8-CAND-BCP-REV2-ARCH-004` | **PARTIALLY CLOSED** | 145+33=178 arithmetic and ledger artifacts are defined, but the post-review registry mutation prevents a stable final ledger, and additional verifier tests would change the exact count. |
| `S8-CAND-BCP-REV2-DOC-001` | **CLOSED** | Profile wording, fixture counts, and const/hash distinction are corrected. |

## 7. Required Revision 4 boundary

A focused Revision 4 can close the remaining issues without reopening the
scientific decisions already fixed by Revision 3. It must, at minimum:

1. add the canonicalization golden fixture to the exact Track 2 inventory;
2. make the registry byte-final before exact verification and prohibit any
   post-review mutation;
3. place both inventories in one explicitly defined true lexical order;
4. add focused mutation tests for both exact-scope verifiers;
5. update Track 1 and Track 2 counts and the successor-ledger count as
   mechanically implied by the corrected inventories;
6. re-run exact inventory, scope, ledger, and mutation verification; and
7. repeat independent re-review before any Track 1 generation or Track 2
   corrected-candidate resubmission.

Revision 4 need not change the already-correct 7/7/8 replacement counts, the
six-View registry concept, the binding successor versions, or the selected
shared canonicalization module architecture unless its own corrections make
such a change unavoidable.

## 8. Confirmation of non-modification

No file inside the supplied review snapshot was created, modified, deleted,
renamed, or moved during this review. No repository command that stages,
commits, or pushes was executed. No production code was authorized or
written. No dataset was generated or published. The protected builder was
absent and was not accessed.

## 9. Final decision

Revision 3 closes four of the seven controlling findings and correctly fixes
several important scientific and manifest-contract details. It does not yet
define an executable deterministic correction cycle. The mandatory golden
fixture is outside the exact Track 2 scope, the registry changes after its
reviewed hash should already be final, and both exact inventories contradict
their own ordering rule. These defects prevent reliable generation,
verification, review, and certification of the proposed artifacts.

No Track 1 generation, Track 2 corrected-candidate resubmission, S8
certification, dataset generation, publication, or deployment is authorized
by this review.

REJECT
