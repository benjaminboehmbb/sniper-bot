# RCC-002 S8 Implementation Candidate Blocker Correction Proposal Independent Review

## Document control

| Field | Value |
|---|---|
| Review ID | `RCC-002-S8-CAND-BCP-CHATGPT-IR-001` |
| Review date | `2026-08-01` |
| Reviewer | Independent ChatGPT scientific and architecture reviewer |
| Review class | Read-only independent review of correction proposal |
| Repository snapshot | `8566e862e9f2d5a017d783e876711dc88f1827d2` |
| Proposal | `RCC_002_S8_IMPLEMENTATION_CANDIDATE_BLOCKER_CORRECTION_PROPOSAL_2026-08-01.md` |
| Proposal SHA-256 | `df2f48a8ceb405ef3f4ad17312fad36fc378040e2c4ce02b99c1c30fdfea2b34` |
| Review package | `RCC_002_S8_IMPLEMENTATION_CANDIDATE_CORRECTION_PROPOSAL_REVIEW_INPUT_2026-08-01.zip` |
| Review package SHA-256 | `6148d7ddd3a5dd76499104c35e92489751b3d7ddf740b44643302fd18d23c676` |
| Controlling candidate review | `RCC-002-S8-CAND-CHATGPT-IR-001` |
| Controlling candidate-review decision | `REJECT` |
| Final decision | `REJECT` |

## 1. Scope and restrictions

This review evaluates whether the proposal is sufficiently complete,
deterministic, and fail-closed to govern the required normative and
implementation correction cycles. It does not review a repaired candidate,
certify any specification change, authorize implementation, or authorize data
generation, publication, or deployment.

The review was conducted entirely against the supplied extracted snapshot.
No repository file was modified. No candidate code was executed. No dependency
was installed. No network access was used.

The protected file `scripts/build_rcc002_spec_bundle.py` was absent from the
package and was not accessed in any way.

## 2. Package integrity and evidence

The following package properties were independently verified:

- package SHA-256 matches the supplied value;
- ZIP path-safety check passes;
- the protected builder is absent;
- the package contains the committed repository snapshot plus exactly 33 S8
  candidate Python files;
- the proposal contains 752 ASCII lines and has SHA-256
  `df2f48a8ceb405ef3f4ad17312fad36fc378040e2c4ce02b99c1c30fdfea2b34`;
- the controlling review has SHA-256
  `cf82b9463b8288e7665df1dd45811c3ddd46dacd754e7825d9c973fbcc60579d`;
- RR-004 has SHA-256
  `16876c0815e3735e64b2eacfd85199b5b7c2c5046488482b51389359218d0ee3`.

Evidence inspected includes:

- the complete correction proposal;
- the controlling rejecting candidate review;
- RR-004;
- Data Pipeline Specification `0.8.0`;
- Reproducibility and Manifest Specification `0.9.0`;
- Dataset Manifest Schema `1.0.1`;
- both certified positive Dataset Manifest `1.0.1` fixtures;
- the S8 candidate implementation and tests relevant to each mapped finding;
- existing correction-scope and verification patterns in the repository.

## 3. Positive assessment

The proposal gets the central governance decision right:

1. `S8-CAND-B02` is correctly classified as a normative-contract blocker.
2. The proposal does not invent a View-schema-fingerprint formula.
3. It separates the normative Track 1 from the implementation Track 2.
4. It prohibits a repaired candidate from being re-submitted while the
   fingerprint contract remains uncertified.
5. It maps all nine controlling findings to a correction and a verification
   concept.
6. It preserves the distinction between proposal approval, normative
   certification, implementation repair, candidate certification, and dataset
   publication authority.
7. The required adverse mutations, regression suites, independent re-review,
   and protected-builder exclusion are retained.

These are necessary properties. They are not sufficient for approval because
the proposal leaves material normative and implementation scope undecided and
omits downstream artifacts that already encode the unresolved fingerprint.

## 4. Findings

### 4.1 `S8-CAND-BCP-B01` - BLOCKER - Track 1 omits existing normative examples and certified Dataset Manifest fixtures

The proposal limits the principal normative edits to Data Pipeline SS6.2 and a
new SS7.9.5, plus an RM SS8.7 cross-reference. It does not include:

- RM Section 24, whose normative Dataset Manifest example contains six
  `schema_fingerprint_sha256` values consisting entirely of zeroes;
- `schemas/rcc002/manifests/dataset-manifest/1.0.1.schema.json`;
- `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/minimal-valid.json`;
- `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/complete-valid.json`.

Both certified positive fixtures contain the same six all-zero logical-schema
fingerprints. Schema `1.0.1` accepts any 64-character digest and therefore
cannot bind the per-view values that Track 1 intends to certify.

Once six real literal fingerprints are normative, the existing example and
positive fixtures cannot remain the current positive evidence for the active
profile. They also cannot be silently overwritten because they are certified
historical artifacts.

Impact: Track 1 could complete exactly as written while the repository still
contains an authoritative example and positive fixtures carrying placeholders.
The normative and machine-readable evidence would remain contradictory, so
`S8-CAND-B02` would not be closed.

Required correction:

1. add RM Section 24 explicitly to Track 1;
2. define an exact successor Dataset Manifest schema/fixture strategy;
3. preserve Schema and fixtures `1.0.1` byte-for-byte as historical evidence;
4. create a versioned successor, expected to be Dataset Manifest Schema
   `1.0.2` unless the specification owner documents a different SemVer result;
5. bind the six exact per-view fingerprint literals structurally where
   feasible and semantically in a versioned verifier;
6. create new minimal-valid and complete-valid positive fixtures using the six
   certified fingerprints;
7. port the relevant negative-fixture ledger to the successor version;
8. update the normative RM example to the successor profile;
9. include all new artifacts in an exact correction-scope manifest and
   mechanical verifier;
10. repeat scientific, architecture, fixture, certification, and readiness
    gates against the complete successor set.

### 4.2 `S8-CAND-BCP-B02` - BLOCKER - the canonicalization authority and repair boundary remain undecided

Section 7.2 explicitly does not decide between:

- correcting the shared S0 canonicalization primitive; and
- introducing a duplicated S8-local canonicalization implementation.

This is not a presentation detail. The current S8 implementation delegates to
the S0 primitive, and that primitive is used by certified deterministic S0
identity generation. The two options change different files, different
identity domains, different regression obligations, and different normative
impact surfaces.

An approved correction proposal must select one architecture and one exact
change boundary. Leaving the choice to the later implementer would recreate
the silent normative decision that the proposal correctly forbids for the View
fingerprint.

Required correction:

1. select a single shared canonicalization authority;
2. prohibit a permanent S8-local duplicate;
3. explicitly include the shared primitive and all affected S0 identity tests
   in the authorized scope, or introduce a separately reviewed shared module
   and migrate every affected consumer;
4. enumerate every deterministic identity whose bytes can change;
5. state whether historical identity fixtures remain preserved or receive a
   versioned successor;
6. require regression and independent golden verification for S0 as well as
   S8;
7. add the resulting exact file set to the correction-scope manifest.

### 4.3 `S8-CAND-BCP-ARCH-001` - MAJOR - successor versions are not fixed and the SemVer discussion is internally ambiguous

Track 1 requires normative changes to Data Pipeline Specification `0.8.0` and
RM `0.9.0`, but it does not state their exact successor versions. It also calls
the fingerprint evidence consistent with a Minor bump while simultaneously
saying that the existing View schema versions remain unchanged. The text does
not identify which object receives that Minor bump.

This ambiguity propagates into the mandatory seven-document specification
profile, dependency references, fixture contents, and dataset identity.

Required correction:

- state the exact successor version of Data Pipeline Specification;
- state the exact successor version of RM;
- state the exact version of the new fingerprint registry/profile;
- state the exact successor Dataset Manifest schema version;
- distinguish document-version bumps, registry/profile-version bumps, and
  View-schema-version decisions;
- enumerate all dependency/profile references that must change;
- require literal hashes only after all successor bytes are finalized.

### 4.4 `S8-CAND-BCP-ARCH-002` - MAJOR - required artifact identity and scope remain optional

The proposal leaves all of the following for later choice:

- embedded normative JSON versus a standalone fingerprint registry;
- an example registry path rather than one exact path;
- the canonicalization-fixture path and format;
- one combined scope manifest versus separate Track 1 and Track 2 manifests.

Those alternatives produce different byte identities and different review
boundaries. A correction plan that requires exact, machine-readable evidence
cannot leave the evidence identity and scope topology undefined.

Required correction:

1. choose exactly one standalone, versioned fingerprint-profile artifact and
   one repository-relative path;
2. define its top-level keys, exact per-view order, allowed value types,
   additional-property policy, and canonical hashing rule;
3. choose one exact canonicalization-fixture path and schema;
4. choose one exact versioned scope-manifest arrangement;
5. define hardcoded independent expected path sets in the verifier so the
   scope file cannot authorize its own omissions;
6. require rejection of missing, extra, duplicated, reordered,
   miscategorized, unsafe, or undeclared artifacts;
7. provide an exact proposed file inventory before implementation begins.

### 4.5 `S8-CAND-BCP-IMPL-001` - MAJOR - the proposed run-ID validator is not a complete grammar

Section 6.4 describes `run:.+` as a complete ID grammar. It is not. The
normative RM format is:

```text
run:<UTC timestamp>:<UUIDv7-or-UUIDv4>
```

`run:.+` accepts `run:source`, `run:target`, controls, path separators, and
arbitrary malformed values. Existing S8 candidate tests already use
`run:source` and `run:target`, showing that this is a live negative-test gap.

Required correction:

- replace `run:.+` with the exact certified timestamp and canonical UUIDv4 or
  UUIDv7 grammar;
- define whether fractional seconds are mandatory and at what precision;
- validate UTC `Z`, calendar validity, UUID canonical form, UUID version, and
  UUID variant;
- add negative tests for `run:source`, `run:target`, non-UTC timestamps,
  invalid dates, invalid UUID versions/variants, controls, and trailing data;
- apply the same validator at every manifest and identity boundary accepting a
  run ID.

### 4.6 `S8-CAND-BCP-DOC-001` - MINOR - golden-preimage quantity is inconsistent

Section 5.5 requires at least one fully expanded preimage for one non-label
view and one label view, which is two examples. Section 7.3 reduces this to
"at least one" fully expanded example.

Required correction: use one exact requirement everywhere: two fully expanded
golden preimages, one non-label and one label view, plus the six literal final
fingerprints and the required sensitivity mutations.

## 5. Independent proposal checks

| Check | Expected | Result |
|---|---|---|
| All nine controlling findings mapped | Present | PASS |
| Normative versus implementation tracks separated | Explicit separation | PASS |
| Placeholder formula prohibited | Fail closed | PASS |
| Track 1 certification before fingerprint implementation | Mandatory gate | PASS |
| RM Section 24 included | Explicit successor correction | FAIL |
| Certified Dataset Manifest `1.0.1` fixtures addressed | Preserve plus successor | FAIL |
| Dataset Manifest successor schema/version fixed | Exact version and path | FAIL |
| Canonicalization authority fixed | One selected shared architecture | FAIL |
| Exact DP and RM successor versions fixed | Literal versions | FAIL |
| Fingerprint registry path and schema fixed | One exact artifact | FAIL |
| Canonical golden-fixture path/schema fixed | One exact artifact | FAIL |
| Correction-scope topology fixed | One exact arrangement | FAIL |
| Run-ID grammar complete | Timestamp plus UUIDv4/v7 | FAIL |
| Protected builder excluded | Absent and prohibited | PASS |
| Dataset generation/publication/deployment prohibited | Explicit prohibition | PASS |

These failures were derived by direct comparison with repository artifacts,
not only by restating the controlling review.

## 6. Fail-closed sequencing assessment

The proposal's sequencing graph is logically sound at the decision level:

1. normative drafting and certification precede fingerprint implementation;
2. independent implementation repairs may be prepared in parallel;
3. no combined candidate may be reviewed before both tracks close;
4. independent re-review precedes candidate certification;
5. dataset publication remains separately unauthorized.

However, the graph's nodes do not yet contain a closed artifact set. In
particular, the Track 1 node excludes artifacts that already carry the value
being corrected, and the Track 2 node defers its canonicalization architecture
to a future decision. Passing through the gates therefore would not prove that
all affected evidence had been updated or that one deterministic repair had
been applied.

The sequencing is approved as a conceptual pattern but not as an executable
correction contract.

## 7. Required Revision 2 boundary

A revised proposal must close all findings in Section 4 and provide, before
implementation:

1. one exact normative successor profile covering Data Pipeline, RM Section
   24, the fingerprint registry, Dataset Manifest schema, positive and negative
   fixtures, scope manifest, verifier, hashes, reviews, and certification;
2. exact successor versions and dependency/profile transitions;
3. one exact, standalone fingerprint-profile artifact with a declared schema;
4. six literal fingerprints and two fully expanded golden preimages;
5. an exact successor Dataset Manifest fixture set containing the real values;
6. one selected shared RFC 8785/JCS implementation architecture;
7. one exact external canonicalization-fixture path and schema;
8. complete ID grammars, including the normative run-ID format;
9. one exact correction-scope topology and hardcoded independent verifier
   expectations;
10. the original nine adverse mutations plus the additional scope, fixture,
    identity, path, symlink, state, and downstream-consistency mutations;
11. focused S8, complete RCC-002, S0 identity, and TD-005 regression gates;
12. a new independent proposal re-review before either correction track is
    authorized.

Track 2 code may not be modified under this rejected proposal. The existing
uncommitted S8 candidate must remain uncommitted and uncertified. No real
fingerprint, dataset, publication, or deployment is authorized.

## 8. Non-modification confirmation

The review was read-only with respect to the supplied snapshot. No source,
test, specification, schema, fixture, registry, ledger, or review file inside
the snapshot was created, modified, deleted, renamed, or moved. No candidate
module was imported or executed. No dataset was generated or published.

The protected builder was absent from the package and was never accessed.

## 9. Final decision

The proposal correctly identifies the need for a normative fingerprint cycle
and correctly separates it from implementation repair. It cannot yet be
approved because its Track 1 omits authoritative artifacts that already carry
placeholder fingerprints, while both tracks retain unresolved architecture,
versioning, artifact-identity, and ID-grammar decisions.

The proposal requires a focused Revision 2 and a new independent re-review.

REJECT
