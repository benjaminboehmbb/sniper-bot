# RCC-002 S8 Track 2 Correction Architecture Proposal

| Field | Value |
|---|---|
| Proposal ID | `RCC-002-S8-TRACK2-CAP-001` |
| Proposal date | `2026-08-04` |
| Proposal class | Bounded Track 2 correction architecture proposal |
| Repository baseline | `7ab00e06e91c35e5738698c25fa941fa50516fa0` |
| Inspection authorization proposal | `RCC-002-S8-TRACK2-IAP-001` |
| Inspection package SHA-256 | `eab9fe29ae592f8d13b30eb44642c37872d707c1597e5fbd640259256c3bc432` |
| Inspection inventory SHA-256 | `c5925ad40fb6609f60fb98a6afcf482b31463a3e65858e4e1c3e22adb7b9b885` |
| Inspection ledger SHA-256 | `47ef3f5aa9cd573cb9c7188192e2cb5755022c38e0c1d5730c1417be1e014d27` |
| Inspection summary SHA-256 | `47caaf9d74530e89d3e3d1eeda595a4f9a15e1379329dcd43169aa76e2c7311c` |
| Inspection report SHA-256 | `b6df563815d1fc077f585511f9a9e779793e9869acb9ca8830d426d1a23b1ec1` |
| Inspection status | `COMPLETE` |
| Inspection determination | `CORRECTION_PROPOSAL_REQUIRED` |
| Current implementation authority | `None` |
| Proposed next action | One independent scientific and architecture proposal review |
| Status | `PROPOSED FOR ONE INDEPENDENT SCIENTIFIC AND ARCHITECTURE REVIEW` |

## 1. Purpose

The controlled read-only inspection of the exact 33-file RCC-002 S8 Track 2
candidate completed successfully against repository baseline
`7ab00e06e91c35e5738698c25fa941fa50516fa0`.

The inspection verified:

- exactly 33 authorized Track 2 files;
- 21 source files under `rcc002/s8/`;
- 12 test files under `tests/rcc002/s8/`;
- deterministic candidate identity through the bound inventory and SHA-256
  ledger;
- exclusion of the protected builder;
- no mutation of inspected Track 2 bytes or file modes.

The inspection returned:

    INSPECTION_STATUS=COMPLETE
    CORRECTION_DETERMINATION=CORRECTION_PROPOSAL_REQUIRED
    BLOCKER_FINDINGS=2
    MAJOR_FINDINGS=1
    MINOR_FINDINGS=2
    OBSERVATION_FINDINGS=1

This proposal defines the minimum bounded correction architecture required to
resolve the demonstrated findings.

This proposal does not authorize implementation, import, execution, testing,
mutation, staging, commit, push, builder access, dataset activity, deployment,
or production use.

## 2. Controlling evidence

The correction architecture is controlled by these exact evidence identities:

1. Track 2 read-only inventory:

   Path:
   `docs/review/evidence/RCC_002_S8_TRACK2_READONLY_INVENTORY_2026-08-04.txt`

   SHA-256:
   `c5925ad40fb6609f60fb98a6afcf482b31463a3e65858e4e1c3e22adb7b9b885`

2. Track 2 read-only SHA-256 ledger:

   Path:
   `docs/review/evidence/RCC_002_S8_TRACK2_READONLY_SHA256_LEDGER_2026-08-04.txt`

   SHA-256:
   `47ef3f5aa9cd573cb9c7188192e2cb5755022c38e0c1d5730c1417be1e014d27`

3. Track 2 inventory summary:

   Path:
   `docs/review/evidence/RCC_002_S8_TRACK2_READONLY_INVENTORY_SUMMARY_2026-08-04.json`

   SHA-256:
   `47caaf9d74530e89d3e3d1eeda595a4f9a15e1379329dcd43169aa76e2c7311c`

4. Controlled read-only inspection report:

   Path:
   `docs/review/RCC_002_S8_TRACK2_CONTROLLED_READONLY_INSPECTION_REPORT_2026-08-04.md`

   SHA-256:
   `b6df563815d1fc077f585511f9a9e779793e9869acb9ca8830d426d1a23b1ec1`

5. Track 2 inspection authorization:

   `RCC-002-S8-TRACK2-IAP-001`

6. Controlling Track 1 architecture and certification:

   `RCC-002-S8-CAND-BCP-001-REV9`

   `RCC-002-S8-TRACK1-REV9-CERT-001`

Where any older document differs, the certified Track 1 baseline and the
bound Track 2 inspection evidence control.

## 3. Findings requiring disposition

### 3.1 F-001 - BLOCKER

Affected files:

- `rcc002/s8/manifests/common.py`
- `rcc002/s8/manifests/dataset.py`
- `tests/rcc002/s8/test_manifests.py`

Demonstrated defect:

The Dataset Manifest builder emits schema version `1.0.1` instead of the
prospective production version `1.0.2`.

The prohibited-version logic rejects `1.0.0` but does not reject withdrawn
version `1.0.1`.

Required correction objective:

1. prospective Dataset Manifest production must emit exactly version `1.0.2`;
2. versions `1.0.0` and `1.0.1` must both be rejected for prospective
   production;
3. schema identity, schema version, and schema reference must agree exactly;
4. historical evidence using an older immutable schema must not be rewritten;
5. tests must verify positive `1.0.2` production and negative rejection of both
   withdrawn versions.

### 3.2 F-002 - BLOCKER

Affected files:

- `rcc002/s8/views.py`
- `tests/rcc002/s8/test_views.py`

Demonstrated defect:

`ViewDefinition.schema_fingerprint_sha256` uses a placeholder preimage instead
of the exact fingerprint construction required by Data Pipeline Specification
version `0.9.0`, Section `7.9.5`.

Required correction objective:

1. remove the placeholder fingerprint construction;
2. construct the exact normative 11-key preimage defined by DP `0.9.0`,
   Section `7.9.5`;
3. serialize the preimage using the required RFC 8785/JCS canonicalization;
4. hash the exact canonical bytes using SHA-256;
5. ensure deterministic field ordering, type treatment, nullability treatment,
   and view-definition binding;
6. add exact positive-vector and negative-variation tests;
7. prohibit fallback to an incomplete or locally invented fingerprint profile.

### 3.3 F-003 - MAJOR

Affected files:

- `rcc002/s8/specification_profile.py`
- `tests/rcc002/s8/test_manifests.py`

Demonstrated defect:

The specification profile binds outdated versions:

- Data Pipeline Specification: `0.8.0`
- Reproducibility and Manifest Specification: `0.9.0`

Required correction objective:

1. bind Data Pipeline Specification version `0.9.0`;
2. bind Reproducibility and Manifest Specification version `0.9.1`;
3. ensure every associated path, identifier, version, and content hash matches
   the certified repository baseline;
4. prohibit a mixed profile containing current paths with obsolete versions or
   hashes;
5. add deterministic tests for the exact certified profile.

### 3.4 F-004 - MINOR

Affected files:

- `rcc002/s8/reconciliation.py`
- `tests/rcc002/s8/test_reconciliation.py`

Demonstrated defect:

`PRIMARY_KEY_FIELDS` hardcodes `provider` as the first field and therefore does
not demonstrate correct treatment of consolidated dataset schemas where
`provider` is not part of the evaluated primary key.

Required correction objective:

1. derive the reconciliation primary-key fields from the evaluated schema or
   controlling schema metadata;
2. include `provider` only where the evaluated schema requires it;
3. prohibit silent fallback to the hardcoded five-field key;
4. preserve deterministic primary-key ordering;
5. test both provider-specific and consolidated dataset schemas;
6. test rejection of missing, duplicated, or reordered required key fields.

### 3.5 F-005 - MINOR

Affected file:

- `tests/rcc002/s8/test_manifests.py`

Demonstrated defect:

A test uses `inspect.getsource()` and a source-string assertion instead of
testing normative behavior.

Required correction objective:

1. remove the source-string assertion;
2. replace it with behavioral assertions over produced or rejected manifest
   structures;
3. prove that withdrawn versions cannot be produced through the public builder
   behavior;
4. avoid tests that pass or fail solely because of source-code spelling.

### 3.6 F-006 - OBSERVATION

Affected file:

- `rcc002/s8/identity.py`

Inspection observation:

`DatasetComponent` serializes `schema_ref` instead of separate `schema_id` and
`schema_version` properties.

Disposition:

`NO REQUIRED CORRECTION`

The inspection report classified the behavior as functionally equivalent and
did not require correction.

`rcc002/s8/identity.py` therefore remains outside the proposed mutation scope.

Any later claim that F-006 requires code modification would require a new
demonstrated normative contradiction, a proposal revision, and a new
independent proposal review.

## 4. Proposed maximum correction path scope

A later implementation authorization may cover no more than these eight paths:

- `rcc002/s8/manifests/common.py`
- `rcc002/s8/manifests/dataset.py`
- `rcc002/s8/reconciliation.py`
- `rcc002/s8/specification_profile.py`
- `rcc002/s8/views.py`
- `tests/rcc002/s8/test_manifests.py`
- `tests/rcc002/s8/test_reconciliation.py`
- `tests/rcc002/s8/test_views.py`

The five source paths contain the demonstrated normative defects.

The three test paths are the existing test locations required to provide
behavioral evidence for the corresponding corrections.

No additional Track 2 path may be modified unless:

1. a concrete necessity is demonstrated;
2. this proposal is revised;
3. the revision receives a new independent scientific and architecture review;
4. separate implementation authority is issued for the revised exact scope.

The remaining 25 files in the original 33-file Track 2 inventory must remain
byte-identical unless a separately reviewed proposal revision states otherwise.

## 5. Explicit exclusions

This proposal does not authorize:

- modification of any file;
- import of any Track 2 module;
- execution of any Track 2 module;
- execution of any test;
- compilation;
- creation of a correction candidate;
- creation or mutation of schemas, registries, fixtures, datasets, or
  publication artifacts;
- modification of certified Track 1 files;
- repository-wide traversal of untracked content;
- access to unrelated untracked paths;
- staging;
- commit;
- push;
- dataset generation or publication;
- paper deployment;
- live deployment;
- production use.

The protected builder remains outside every scope:

`scripts/build_rcc002_spec_bundle.py`

It must not be opened, read, hashed, imported, executed, modified, staged,
committed, packaged, or used as evidence.

## 6. Required candidate identity controls

Before any later correction implementation begins, a separate implementation
authorization must bind:

1. repository baseline;
2. exact authorized mutation paths;
3. exact pre-correction SHA-256 for every authorized path;
4. exact original 33-file Track 2 inventory;
5. exact original 33-file Track 2 ledger;
6. expected unchanged-path set;
7. allowed new governance evidence paths;
8. protected-builder exclusion;
9. unrelated-untracked-path exclusion;
10. prohibition of staging, commit, and push until later gates approve them.

A later byte-finalized candidate must provide:

1. an `LC_ALL=C`-ordered 33-file Track 2 path inventory;
2. a SHA-256 ledger covering all 33 Track 2 files;
3. exact identification of modified and unchanged Track 2 files;
4. proof that every path outside the authorized correction scope is
   byte-identical to the inspected baseline;
5. proof that no Track 1 payload byte changed;
6. proof that the protected builder was not accessed;
7. proof that no unrelated untracked path was accessed;
8. a deterministic staged patch SHA-256;
9. a deterministic staged file-list SHA-256;
10. a clean unstaged diff for every candidate path.

## 7. Required correction evidence

### 7.1 Dataset Manifest evidence

- builder output uses schema version `1.0.2`;
- schema ID, version, and reference agree;
- version `1.0.0` is rejected;
- version `1.0.1` is rejected;
- historical immutable evidence is not rewritten;
- no public builder path can emit a withdrawn prospective version.

### 7.2 View fingerprint evidence

- exact DP `0.9.0`, Section `7.9.5` 11-key preimage;
- exact RFC 8785/JCS canonical bytes;
- exact expected SHA-256 for at least one independently derived golden vector;
- negative controls demonstrating that a change to a normative preimage field
  changes or invalidates the fingerprint as specified;
- no placeholder or fallback fingerprint path.

### 7.3 Specification-profile evidence

- DP version exactly `0.9.0`;
- RM version exactly `0.9.1`;
- exact certified specification identities and hashes;
- deterministic profile ordering;
- rejection of obsolete or mixed-version profiles.

### 7.4 Reconciliation evidence

- provider-specific primary-key behavior;
- consolidated primary-key behavior without `provider`;
- deterministic key-field order;
- rejection of missing key fields;
- rejection of duplicate key fields;
- rejection of invalid key-field ordering where ordering is normative.

### 7.5 Test-quality evidence

- removal of the `inspect.getsource()` source-string assertion;
- behavioral replacement tests;
- positive and negative normative assertions;
- no assertion whose result depends only on source-code spelling.

## 8. Required gate architecture

A later correction candidate must pass a deterministic, non-circular gate with
these ordered stages:

1. baseline identity verification;
2. exact path-scope verification;
3. original inventory and ledger verification;
4. protected-builder exclusion verification;
5. unrelated-untracked-path exclusion verification;
6. ASCII and formatting checks for controlled evidence documents;
7. Python compilation checks for the authorized Track 2 source and test scope;
8. import checks for the authorized Track 2 modules;
9. focused behavioral tests for F-001 through F-005;
10. all Track 2 unit tests;
11. Track 2 integration tests;
12. full RCC-002 regression tests against certified Track 1;
13. positive scope control;
14. negative out-of-scope control;
15. negative candidate-ledger control;
16. negative protected-builder-path control using path-policy evidence only,
    without accessing the builder;
17. final 33-file inventory verification;
18. final 33-file SHA-256 ledger verification;
19. changed-path and unchanged-path proof;
20. clean candidate identity capture.

Every executable stage must report:

- `exit_code=0`
- `failure_count=0`
- `error_count=0`

No failed stage may be waived by narrative interpretation.

## 9. Independent review and certification sequence

The required sequence is:

1. independently review this correction architecture proposal;
2. if the proposal review returns `REJECT`, stop after diagnosis;
3. if the proposal review returns `APPROVE`, prepare a separate exact
   implementation-authorization decision;
4. only after that decision may the authorized correction paths be modified;
5. execute the complete correction gate;
6. byte-finalize the correction candidate;
7. capture exact candidate identities and verification evidence;
8. perform one independent implementation-candidate review;
9. if that review returns `REJECT`, stop after diagnosis;
10. if that review returns `APPROVE`, create a certification decision bound to
    the exact candidate bytes;
11. obtain separate explicit authorization for staging and commit;
12. verify the controlled commit;
13. obtain separate explicit authorization for push;
14. verify `HEAD == origin/main == remote main`.

No authority is inherited automatically across these gates.

## 10. Proposal-review acceptance gate

This proposal may receive `APPROVE` only if the independent reviewer confirms:

1. the inspection evidence identities are complete and internally consistent;
2. the inspection report supports all five required correction findings;
3. F-006 is correctly excluded from required mutation;
4. the proposed correction objectives match the controlling specifications;
5. the maximum correction path scope is sufficiently narrow and test-complete;
6. no unrelated Track 2 path may be modified;
7. the remaining Track 2 files must remain byte-identical;
8. the protected builder remains completely excluded;
9. imports, execution, testing, and mutation remain unauthorized at the
   proposal stage;
10. implementation requires a separate explicit authorization;
11. the candidate identity controls are deterministic and independently
    verifiable;
12. the executable gate covers focused, Track 2, integration, and Track 1
    regression boundaries;
13. positive and negative controls are sufficient to detect scope or identity
    failure;
14. independent implementation review precedes certification;
15. certification precedes commit authorization;
16. commit authorization and push authorization remain separate;
17. the architecture introduces no unrelated design or refactoring scope;
18. no unresolved ambiguity permits scope expansion.

Any failed or not-demonstrated condition requires `REJECT`.

## 11. Authorization boundary

This proposal authorizes no implementation by itself.

Its only permitted next action is one independent scientific and architecture
review of this exact proposal.

An `APPROVE` verdict would not itself authorize mutation. It would only permit
preparation of a separate implementation-authorization decision bound to the
exact reviewed architecture and path scope.

Until that later decision is explicitly issued, all of the following remain
unauthorized:

- Track 2 repair;
- import;
- execution;
- compilation;
- testing;
- mutation;
- staging;
- commit;
- push;
- protected-builder access;
- dataset activity;
- deployment;
- production use.

If the independent review returns `REJECT`, work stops after diagnosis of the
specific demonstrated defect.

PROPOSED FOR ONE INDEPENDENT SCIENTIFIC AND ARCHITECTURE REVIEW
