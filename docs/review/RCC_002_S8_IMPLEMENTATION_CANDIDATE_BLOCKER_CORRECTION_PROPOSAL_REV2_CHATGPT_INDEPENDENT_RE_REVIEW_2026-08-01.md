# RCC-002 S8 Implementation Candidate Blocker Correction Proposal Revision 2 - ChatGPT Independent Re-Review

## Document control

| Field | Value |
|---|---|
| Review ID | `RCC-002-S8-CAND-BCP-CHATGPT-IR-002` |
| Review date | `2026-08-01` |
| Reviewer | Independent ChatGPT scientific and architecture reviewer |
| Review class | Read-only independent re-review of correction proposal Revision 2 |
| Repository baseline represented by package | `b0fe5a70aaceeb3f918e46273e84c4b0efd22a7e` |
| Candidate package | `RCC_002_S8_IMPLEMENTATION_CANDIDATE_CORRECTION_PROPOSAL_REV2_REVIEW_INPUT_2026-08-01.zip` |
| Candidate package SHA-256 | `7d81f13309736015f639b7af7d62a683307878f641adece51f1cc78970abc4bb` |
| Proposal reviewed | `docs/review/RCC_002_S8_IMPLEMENTATION_CANDIDATE_BLOCKER_CORRECTION_PROPOSAL_REV2_2026-08-01.md` |
| Proposal SHA-256 | `8007db898b4d0ce000a82fb3a5ebaf3e6cbd6cd6895ec6ecc2c4c12b2ffe96d4` |
| Controlling prior review | `docs/review/RCC_002_S8_IMPLEMENTATION_CANDIDATE_BLOCKER_CORRECTION_PROPOSAL_CHATGPT_INDEPENDENT_REVIEW_2026-08-01.md` |
| Controlling prior review SHA-256 | `fff8902899c2d1ec4f8951159ffe6a2ece98c9adaae93c851ba02261a9370bd4` |
| Final decision | `REJECT` |

## 1. Review purpose

This review determines whether Revision 2 fully closes the six findings in
the controlling independent review:

1. `S8-CAND-BCP-B01`;
2. `S8-CAND-BCP-B02`;
3. `S8-CAND-BCP-ARCH-001`;
4. `S8-CAND-BCP-ARCH-002`;
5. `S8-CAND-BCP-IMPL-001`; and
6. `S8-CAND-BCP-DOC-001`.

The review also checks whether Revision 2 introduces any new contradiction,
unverifiable scope boundary, dependency cycle, historical-evidence problem,
or implementation authorization ambiguity.

This is a proposal review only. It is not a review of a repaired
implementation candidate, it is not certification, and it does not authorize
dataset generation, publication, deployment, or use of the proposed View
fingerprint formula.

## 2. Review restrictions and package integrity

The package was inspected in strict read-only mode after extraction to an
isolated review directory.

The following package checks passed:

- the ZIP SHA-256 equals
  `7d81f13309736015f639b7af7d62a683307878f641adece51f1cc78970abc4bb`;
- ZIP entries contain no absolute paths and no parent traversal;
- the protected `scripts/build_rcc002_spec_bundle.py` is absent;
- the proposal SHA-256 equals the document-control value above;
- the controlling prior-review SHA-256 equals the document-control value
  above;
- the package contains exactly 33 S8 candidate Python files under
  `rcc002/s8/` and `tests/rcc002/s8/`; and
- no package file was created, modified, deleted, renamed, or moved during
  review.

No dependency was installed. No network access was used. No implementation
candidate module or test suite was executed. Passive file reads, JSON parsing,
regular-expression searches, line-count checks, hash calculations, and
in-memory arithmetic were used.

## 3. Evidence inspected

The review inspected at least the following evidence:

- Revision 2 proposal;
- Revision 1 proposal;
- the controlling Revision 1 independent review;
- the original S8 implementation-candidate independent review;
- RR-004 readiness authorization;
- Data Pipeline Specification `0.8.0`;
- Reproducibility and Manifest Specification `0.9.0`;
- Dataset Manifest schemas `1.0.0` and `1.0.1`;
- Dataset Manifest `1.0.1` positive and negative fixtures;
- `RCC_002_S8RR002_CORRECTION_VERIFIER_SCOPE_V1.json`;
- `RCC_002_S8RR003_NORMATIVE_LEDGER_SCOPE_V1.json`;
- the certified root `SHA256SUMS` ledger;
- the 33 uncommitted S8 implementation-candidate Python files; and
- the current manifest and identity boundaries named by the proposal.

## 4. Executive result

Revision 2 materially improves Revision 1. It makes a defensible shared
canonicalization choice, specifies a complete run-ID grammar, fixes the golden
preimage example count, selects concrete successor versions, selects concrete
registry and fixture paths, and preserves the two-track fail-closed concept.

Those improvements are not sufficient for approval. Revision 2 still has
four blocking or major contract defects:

1. it does not require replacement of every downstream zero View fingerprint
   and contains incorrect counts for the certified positive fixtures;
2. its supposedly exact registry and scope contracts remain extensible and
   do not provide exhaustive path inventories;
3. its exact Track 2 file boundary omits two files that its own run-ID rule
   requires to be modified; and
4. its dependency order requires certified document hashes before the only
   certification step that can produce them.

It additionally omits the required successor treatment of the certified
145-entry normative ledger and reopens one supposedly exact version decision.

The proposal therefore remains non-executable as a deterministic correction
contract and must be revised again.

## 5. Closure assessment of the six controlling findings

| Prior finding | Revision 2 assessment | Result |
|---|---|---|
| `S8-CAND-BCP-B01` | Revision 2 adds RM Section 24, Dataset Manifest `1.0.2`, positive fixtures, negative fixtures, and semantic artifact binding, but does not specify replacement of every zero value and miscounts the historical fixture occurrences. | `OPEN` |
| `S8-CAND-BCP-B02` | One shared authority at `rcc002/canonical.py` is selected; S0 and S8 delegate to it; permanent local duplication is prohibited; identity regression consequences are enumerated. | `CLOSED` |
| `S8-CAND-BCP-ARCH-001` | Concrete versions are proposed, but Data Pipeline `0.9.0` remains subject to later owner confirmation and the stated certification dependency is impossible in the declared order. | `OPEN` |
| `S8-CAND-BCP-ARCH-002` | Concrete artifact and scope-manifest paths are selected, but the registry schema and the two scope inventories are not exact enough to support the mandated exact-list verifiers. | `OPEN` |
| `S8-CAND-BCP-IMPL-001` | The run-ID grammar, UUID versions and variant, UTC form, fractional-second rule, calendar parse, and positive/negative boundaries are specified precisely. | `CLOSED` |
| `S8-CAND-BCP-DOC-001` | The proposal consistently requires exactly two fully expanded fingerprint preimages. | `CLOSED` |

Three of six controlling findings are closed. Three remain open.

## 6. Material findings

### 6.1 `S8-CAND-BCP-REV2-B01` - BLOCKER - Downstream fingerprint replacement is incomplete and based on false fixture counts

#### Location

- Revision 2 Section 6.1, rows for RM Section 24 and Dataset Manifest
  positive fixtures;
- Revision 2 Section 6.4 semantic binding requirement; and
- existing Dataset Manifest `1.0.1` positive fixtures.

#### Independent evidence

Revision 2 correctly states that RM Section 24 contains seven zero
fingerprints: six in `views[]` and one in `artifacts[]`.

Its required Track 1 output then requires the six certified literals from
Data Pipeline Section 7.9.5 in the example, but it does not explicitly require
the `artifacts[].schema_fingerprint_sha256` value to be replaced with the
literal selected by that artifact's `schema_ref`.

The positive-fixture rows contain two objective count errors:

- `minimal-valid.json` is described as containing one zero fingerprint;
  independent parsing found seven: six `views[]` values and one
  `artifacts[]` value.
- `complete-valid.json` is described as containing two zero fingerprints;
  independent parsing found eight: six `views[]` values and two
  `artifacts[]` values.

The new `1.0.2/minimal-valid.json` requirement says it is structurally
identical to the `1.0.1` fixture except for version fields and its single
artifact fingerprint. That cannot satisfy the proposed `1.0.2` schema because
the schema is also required to const-bind all six `views[]` fingerprints to
non-placeholder certified literals.

The proposal therefore permits, or at minimum fails to prohibit, a Track 1
output in which:

- RM Section 24 still carries an all-zero artifact fingerprint;
- the new minimal fixture retains six zero `views[]` fingerprints; or
- a fixture's artifact fingerprint disagrees with its corresponding view
  registry entry.

#### Required correction

A Revision 3 proposal must state exact replacement counts and locations:

- RM Section 24: replace all seven fingerprint placeholders;
- `1.0.2/minimal-valid.json`: provide six real `views[]` fingerprints and
  one matching artifact fingerprint, seven replacements total;
- `1.0.2/complete-valid.json`: provide six real `views[]` fingerprints and
  two matching artifact fingerprints, eight replacements total; and
- mechanically verify, for every artifact entry, that its `schema_ref`
  resolves to exactly one registered view and its fingerprint equals that
  view's certified literal.

The proposal must retain the separate, already-certified RM self-hash rule:
the RM specification-profile self-entry in the normative example may use its
explicitly labelled zero digest to avoid recursion, while generated fixtures
must carry the real SHA-256 of the byte-finalized RM document. A View
fingerprint placeholder and the RM self-hash placeholder are different
contracts and must not be conflated.

### 6.2 `S8-CAND-BCP-REV2-B02` - BLOCKER - Registry and scope contracts are not exact

#### Location

- Revision 2 Sections 6.4, 6.6, 7.2, 8.1, and 8.2.

#### Independent evidence

Section 6.4 labels its top-level registry keys as exact, then permits the
specification owner to add fields. It likewise states that every `views[]`
entry carries certain fields "at minimum" while also requiring
`additionalProperties: false` at every object level.

Those statements cannot all be true simultaneously:

- an exact key set cannot remain open to unspecified additions;
- `additionalProperties: false` is not mechanically meaningful until the
  complete allowed key set for every object is fixed; and
- "at minimum" does not define the exact object shape an independent verifier
  must hardcode.

The new Dataset Manifest negative-fixture requirement is also open-ended:
it requires the 21 ported cases plus "at least one" new case. The resulting
case-ledger count is therefore not fixed. The natural currently-described
total is 22 negative cases, but the proposal does not bind that total.

Section 8.1 names two scope manifests and their verifier paths, but does not
enumerate the complete ordered path lists or exact category membership for
either scope. It nevertheless requires each verifier to hold independent
hardcoded expected lists and reject missing, extra, reordered, or
miscategorized paths.

The certified S8-RR-002 and S8-RR-003 precedents demonstrate why a concrete
path inventory matters: their scope manifests identify every input and output
path, and their verifiers compare the complete category lists to independent
expected lists. Naming a future scope file is not equivalent to defining its
scope.

#### Required correction

Revision 3 must define:

1. the exact top-level registry key set;
2. the exact `views[]` entry key set;
3. the exact object nesting and JSON types;
4. exact allowed-property sets at every object level;
5. exactly 22 Dataset Manifest `1.0.2` negative fixtures, unless a different
   exact list and count is explicitly enumerated;
6. the exact ordered Track 1 category lists and paths;
7. the exact ordered Track 2 category lists and paths; and
8. the exact expected file and inventory counts for both verifiers.

If the specification owner later needs a different registry field, fixture,
or scoped path, that change must require a new reviewed proposal revision
rather than being silently permitted by "at minimum" language.

### 6.3 `S8-CAND-BCP-REV2-ARCH-001` - MAJOR - Exact Track 2 boundary omits mandated run-ID consumers

#### Location

- Revision 2 Section 7.3, application boundary; and
- Revision 2 Section 8.3, exact files that may be modified.

#### Independent evidence

Section 7.3 requires the same run-ID validator at all of these boundaries:

- `rcc002/s8/identity.py`;
- `rcc002/s8/manifests/run.py`;
- `rcc002/s8/manifests/stage.py`; and
- `rcc002/s8/manifests/dataset.py`.

Section 8.3 permits modification of `identity.py` and `dataset.py`, but omits
both `manifests/run.py` and `manifests/stage.py`. Section 8.3 then says that no
other repository file may be modified.

The proposal therefore prohibits two modifications it expressly requires.
Its Track 2 verifier cannot simultaneously enforce the Section 8.3 boundary
and demonstrate the complete Section 7.3 application boundary.

#### Required correction

Add `rcc002/s8/manifests/run.py` and
`rcc002/s8/manifests/stage.py` to the exact Track 2 output set. Add the exact
test files that prove their positive and negative run-ID boundaries. Reconcile
the complete Section 8.3 list with the hardcoded Track 2 scope inventory.

### 6.4 `S8-CAND-BCP-REV2-ARCH-002` - MAJOR - Certification dependency is temporally impossible

#### Location

- Revision 2 Section 6.3 dependency consequences;
- Revision 2 Section 6.6 steps 1 through 8; and
- Revision 2 Section 9 sequencing diagram.

#### Independent evidence

Revision 2 says Dataset Manifest `1.0.2` schema and fixture drafting occurs at
Section 6.6 step 6 and consumes "now-certified" Data Pipeline `0.9.0` and RM
`0.9.1` document hashes. The only certification act in the sequence is step
8, where the specification, registry, schema, and fixtures are certified as
one correction-cycle output.

Thus step 6 requires certification evidence that step 8 has not yet produced.
Section 6.3 repeats the contradiction by saying the schema cannot be finalized
until both successor documents are certified, while the declared process
certifies the complete set together only after schema finalization and
verification.

The proposal also attributes final document hashes to the schema's
`specification_profile` consts. The schema const-binds specification IDs and
versions; the positive fixture payloads carry document hashes. Those are
different dependencies and must be described separately.

#### Required correction

Use an acyclic byte-finalization sequence:

1. draft the fingerprint contract and registry;
2. independently derive and freeze the six literals;
3. draft and byte-finalize Data Pipeline `0.9.0`;
4. draft and byte-finalize RM `0.9.1`, preserving its explicit example
   self-hash convention;
5. derive the real document hashes from those frozen bytes;
6. draft Dataset Manifest `1.0.2` schema using fixed IDs, versions, and View
   literals;
7. generate fixtures using the real frozen document hashes;
8. run exact-scope verification over the mutually consistent complete set;
9. independently review the complete set; and
10. certify the set together.

If the project instead intends separate certification acts for the two
documents before schema/fixture drafting, Revision 3 must declare those acts
explicitly and repeat review and certification after every downstream hash
change.

### 6.5 `S8-CAND-BCP-REV2-ARCH-003` - MAJOR - Exact Data Pipeline version remains nonbinding

#### Location

- Revision 2 Section 6.3 version table, Data Pipeline row.

#### Independent evidence

The table calls `0.9.0` the proposed exact successor and uses it as a hardcoded
dependency throughout the future schema, registry, fixtures, and scope
metadata. The same row says final version confirmation remains the
specification owner's decision during drafting.

That sentence reopens the version decision. If the owner chooses any other
version, every dependent value and expected scope changes. A mechanical
verifier cannot treat `0.9.0` as independent ground truth while the proposal
also permits it to change without another review.

#### Required correction

Make `0.9.0` binding for this correction contract. If the owner determines a
different version is required, require a new proposal revision and re-review
before Track 1 artifact generation.

### 6.6 `S8-CAND-BCP-REV2-ARCH-004` - MAJOR - Certified normative-ledger successor is omitted

#### Location

- Revision 2 Sections 6.1, 6.3, 6.6, 8, and 10; and
- certified root `SHA256SUMS` plus
  `RCC_002_S8RR003_NORMATIVE_LEDGER_SCOPE_V1.json`.

#### Independent evidence

The current root `SHA256SUMS` contains exactly 145 sorted, unique entries and
is mechanically bound by the certified S8-RR-003 scope and verifier. It
includes, among other items:

- the Data Pipeline Specification;
- the RM Specification;
- Dataset Manifest schemas `1.0.0` and `1.0.1`;
- all Dataset Manifest `1.0.1` fixtures;
- RCC-002 registries;
- review requirements;
- normative verification scripts; and
- their focused tests.

Track 1 changes two already-ledgered specification paths and adds a new
registry, schema, fixture family, scope, verifier, and test evidence. Those
changes necessarily make the current 145-entry ledger no longer describe the
current normative bundle.

Revision 2 says the certified ledger is preserved but defines no historical
ledger copy, no successor arithmetic, no exact successor entry set, no
successor `SHA256SUMS`, and no update or successor for the S8-RR-003 ledger
scope/verifier contract.

Preserving the old ledger's hash as historical evidence is necessary but not
sufficient. The project already established this exact principle in
S8-RR-003: preserve the old 110-entry ledger as evidence, then certify a
complete 145-entry successor.

#### Required correction

Revision 3 must add a normative-ledger subtrack or incorporate an exact ledger
successor into Track 1. It must define:

- the immutable historical copy and expected hash of the current 145-entry
  ledger;
- exact successor-set arithmetic, including overlaps and replacements;
- the exact sorted successor path set;
- updated hashes for modified paths;
- all new normative Track 1 paths;
- the root ledger self-entry exclusion;
- protected-builder exclusion;
- an exact scope manifest and independent hardcoded verifier;
- mutation tests for missing, extra, duplicate, reordered, unsafe, stale, and
  self-referential entries; and
- an independent re-review and certification step for the successor ledger.

### 6.7 `S8-CAND-BCP-REV2-DOC-001` - MINOR - Additional internal wording defects

#### Evidence

In addition to the positive-fixture count errors described in Finding 6.1:

- Section 6.3 describes the current seven-entry specification profile as
  the listed six non-RM entries plus "any future entries". Dataset Manifest
  `1.0.2` is otherwise required to preserve an exact, closed seven-entry
  profile. Future entries cannot be silently carried into the current
  profile.
- Section 6.4 says exact while retaining owner-extensible fields.
- Section 6.6 says document hashes are schema inputs when they are fixture
  inputs.

#### Required correction

Use closed-current-profile language throughout, correct the fixture counts,
remove undefined extensibility, and distinguish schema const inputs from
fixture hash inputs.

## 7. Positive determinations

The rejection does not negate the following independently confirmed
strengths:

1. The shared canonicalization authority at `rcc002/canonical.py` is a clear
   and maintainable architecture.
2. S0 compatibility is treated explicitly, including the requirement for a
   dedicated S0 regression run.
3. Permanent S8-local canonicalization duplication is prohibited.
4. The non-BMP UTF-16 ordering and NFC-collision cases are correctly required
   in an external fixture.
5. Dataset Manifest `1.0.1` and its fixtures are correctly preserved as
   historical evidence.
6. Dataset Manifest `1.0.2` is a reasonable non-destructive successor path.
7. Structural const-binding for fixed-order `views[]` and semantic binding
   for variable-order `artifacts[]` is the correct two-layer design.
8. The run-ID grammar is precise and includes real calendar validation.
9. UUID versions 4 and 7 and the RFC variant nibble are constrained.
10. Portable-path validation is correctly centralized and fail-closed.
11. Exactly two expanded View-fingerprint preimage examples are required.
12. The two-track separation correctly prevents implementation-selected
    fingerprint formulas before normative certification.
13. Dataset generation, publication, and deployment remain explicitly
    unauthorized.

## 8. Required Revision 3 acceptance checklist

Revision 3 can be approved only if all of the following are satisfied:

1. RM Section 24 replacement count is exactly seven View fingerprints.
2. Dataset Manifest `1.0.2` minimal positive fixture carries seven real View
   fingerprints.
3. Dataset Manifest `1.0.2` complete positive fixture carries eight real View
   fingerprints.
4. Every artifact fingerprint is semantically matched to its registered View.
5. The RM specification-profile self-hash exception is explicitly preserved
   and distinguished from View fingerprints.
6. The fingerprint registry has an exact closed schema and exact JSON types.
7. The registry's six `views[]` objects have exact closed key sets.
8. Dataset Manifest `1.0.2` has an exact negative-fixture list and count.
9. Both Track 1 and Track 2 have exhaustive ordered scope inventories.
10. Both verifiers have exact expected inventory counts.
11. `manifests/run.py` is present in the Track 2 modification scope.
12. `manifests/stage.py` is present in the Track 2 modification scope.
13. Run-ID tests cover both added manifest boundaries.
14. Document byte-finalization precedes dependent fixture hash generation.
15. Certification occurs only after the complete set is mutually consistent.
16. Data Pipeline `0.9.0` is binding or any change requires a new revision.
17. The certified 145-entry root ledger has a defined exact successor cycle.
18. The successor ledger has independent scope, verifier, and mutation tests.
19. Current seven-entry specification-profile closure is stated without
    "future entry" ambiguity.
20. A new independent scientific and architecture re-review returns an
    explicit approval before any correction implementation is certified.

## 9. Non-modification confirmation

I explicitly confirm that this review did not modify, create, delete, rename,
or move any file inside the extracted review package. It did not execute the
S8 implementation candidate, install dependencies, access the network,
generate a dataset, publish an artifact, stage a file, create a commit, or
push a branch.

The protected `scripts/build_rcc002_spec_bundle.py` was absent from the
package and was not accessed.

The only output of this review is this independent report outside the
extracted package.

## 10. Final decision

Revision 2 closes the canonicalization-authority, run-ID grammar, and exact
golden-example-count findings, but it does not yet define a complete,
non-contradictory, mechanically enforceable correction contract.

`S8-CAND-BCP-REV2-B01` and `S8-CAND-BCP-REV2-B02` are blocking. The Track 2
scope contradiction, certification-order contradiction, nonbinding version,
and omitted normative-ledger successor are major defects. These issues can
produce incomplete fixtures, permit undeclared scope expansion, prevent
required implementation changes, or leave the certified root ledger stale.

Proposal approval is therefore withheld. Track 1 artifact generation, Track
2 correction implementation under this proposal, corrected-candidate
resubmission, and certification remain unauthorized until a revised proposal
closes every finding above and receives a new independent review.

REJECT
