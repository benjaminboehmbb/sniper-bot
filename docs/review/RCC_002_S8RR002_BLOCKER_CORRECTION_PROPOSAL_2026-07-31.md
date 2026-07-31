# RCC-002 S8-RR-002 Blocker Correction Proposal

## Document control

| Field | Value |
|---|---|
| Proposal ID | `RCC-002-S8RR002-BCP-001` |
| Date | `2026-07-31` |
| Repository baseline | `d2a51ed13d1a054d7e60796689397aaac1bea5bf` |
| Trigger | `RCC_002_S8_IMPLEMENTATION_READINESS_REVIEW_2026-07-31.md` |
| Findings in scope | `S8-RR2-B01`, `S8-RR2-B02` |
| Change class | Focused normative and machine-readable contract correction |
| S8 implementation | Prohibited |
| Dataset publication | Prohibited |
| Status | Proposed for independent scientific and architecture review |

## 1. Decision requested

Approve one focused correction cycle that:

1. defines `DatasetManifest.views` as the exact ordered six-view RCC-002
   registry snapshot;
2. defines `DatasetManifest.specification_profile` as the exact ordered
   seven-document current specification profile;
3. introduces Dataset Manifest Schema `1.0.1` without modifying the certified
   `1.0.0` schema or its historical fixtures;
4. corrects the normative example and creates valid `1.0.1` fixtures;
5. adds mechanically executable cross-document and fixture verification;
6. repeats focused review, certification and S8 readiness before any S8 code.

## 2. Problem statement

The current authoritative specifications register six distinct S8 views and
seven exact specification-profile entries. In contrast:

- Reproducibility and Manifest 0.8.0, Section 24, lists Audit View V2 six
  times;
- both positive Dataset Manifest 1.0.0 fixtures contain the same duplicate
  view array;
- those three artifacts use `RCC-002-SPEC-0` through `RCC-002-SPEC-6`, each
  at `1.0.0`, instead of the mandatory current specification profile;
- Dataset Manifest Schema 1.0.0 permits those arrays because it constrains
  only generic item structure and minimum counts;
- the committed correction verifier counts fixtures but does not validate
  their structural acceptance or cross-document semantic correctness.

The defects affect the positive implementation oracle for S8 manifests. They
must not be resolved through undocumented S8 code behavior.

## 3. Normative decisions

### 3.1 Meaning of `DatasetManifest.views`

`DatasetManifest.views` is the canonical registry snapshot for the dataset
profile. It is not the physical artifact inventory.

The physical views actually materialized by a particular build remain listed
under `artifacts`. Therefore a minimal build may contain fewer than six data
artifacts while `views` still records the exact six schemas that define the
RCC-002 dataset profile.

### 3.2 Exact view order

The canonical order is:

1. `rcc002.view.research-features/1.0.0`
2. `rcc002.view.backtest-inputs/1.0.0`
3. `rcc002.view.paper/1.0.0`
4. `rcc002.view.live/1.0.0`
5. `rcc002.view.label-research/1.0.0`
6. `rcc002.view.audit/2.0.0`

The first four entries use:

```text
2f2fd811b5ed8754ad8b02ee2222d885d7da3e7551ecbd5cf65fe38831c0806e
```

The final two entries use:

```text
0e223d60ed4139f73194f1cb3b886a8eface9229183ad522a093e966827518cc
```

Every entry must contain the matching `schema_id`, `schema_version`,
`schema_ref`, `schema_fingerprint_sha256` and `allowlist_sha256`.

Missing, duplicate, reordered, unknown, stale or hash-inconsistent entries
invalidate the complete Dataset Manifest.

### 3.3 Exact specification-profile order

The canonical order is:

1. `RCC_002_DATA_PIPELINE_SPECIFICATION` / `0.8.0`
2. `RCC-002-DV` / `0.6.0`
3. `RCC-002-IS` / `0.4.3`
4. `RCC-002-ST` / `0.4.2`
5. `RCC-002-RG` / `0.5.1`
6. `RCC-002-LF` / `0.5.0`
7. `RCC-002-RM` / `0.8.1`

Each entry in a concrete generated Dataset Manifest must contain the exact
current document hash. Missing, duplicate, reordered, unknown, stale or
hash-inconsistent entries invalidate the complete Dataset Manifest.

The normative Section 24 example cannot embed the byte hash of its own
Reproducibility specification without creating self-reference. It therefore
uses explicitly marked non-literal zero-digest placeholders while preserving
the exact document IDs, versions and order. Positive machine-readable fixtures
created after the specification is finalized must contain the actual hashes.

### 3.4 Version treatment

The certified Dataset Manifest Schema `1.0.0` and its fixtures remain
byte-immutable historical artifacts.

The corrected schema is:

```text
schema_id=rcc002.dataset-manifest
schema_version=1.0.1
schema_ref=rcc002.dataset-manifest/1.0.1
```

Patch version `1.0.1` is selected because the change repairs acceptance of
payloads that were already invalid under the cross-document normative
contract. It does not change the accepted domain of valid RCC-002 Dataset
Manifests.

Dataset Manifest Schema 1.0.0 is withdrawn for new S8 implementation and must
not be produced. Historical verification remains permitted.

Reproducibility and Manifest changes from `0.8.0` to `0.8.1`. This is a patch
correction: it makes the existing six-view and seven-specification contracts
consistent in the example, schema reference and fixtures without changing
scientific data semantics or S0-S7 behavior.

## 4. Exact correction set

### 4.1 Modified normative file

```text
docs/specifications/RCC_002_REPRODUCIBILITY_AND_MANIFEST_2026-07-23.md
```

Required changes:

- version `0.8.0` to `0.8.1`;
- Section 8.6: Dataset Manifest Schema `1.0.1`;
- explicit withdrawal of Dataset Manifest Schema `1.0.0` for new builds;
- explicit canonical order and exact membership rules for `views`;
- explicit canonical order and exact membership rules for
  `specification_profile`;
- Section 12.3: self-version `RCC-002-RM/0.8.1`;
- Section 24: Dataset Manifest Schema `1.0.1`, six distinct view entries and
  the exact seven-document ID/version profile, with zero digests explicitly
  identified as non-literal example placeholders;
- dated correction record with finding IDs and scope exclusions.

No other current specification requires a semantic version change.

### 4.2 New schema

```text
schemas/rcc002/manifests/dataset-manifest/1.0.1.schema.json
```

The schema must preserve all 1.0.0 structural constraints and additionally:

- require exactly six `views`;
- bind their exact canonical order through Draft 2020-12 `prefixItems`;
- reject additional view entries;
- bind each view's schema identity, version, reference and allowlist hash;
- require exactly seven `specification_profile` entries;
- bind their exact canonical order, document IDs and versions;
- retain digest-format validation in JSON Schema while leaving exact
  document-hash reconciliation to the cross-document semantic validator;
- reject additional specification entries;
- preserve strict nested `additionalProperties: false`;
- use the new exact schema identity constants.

### 4.3 New fixtures

Create:

```text
tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/
```

Positive fixtures:

- `minimal-valid.json`;
- `complete-valid.json`.

Both must carry the six distinct view entries and the exact seven-document
profile. If their intended optional coverage remains identical, retain only
one positive fixture or make their difference explicit; do not count
byte-identical duplicates as independent evidence.

All applicable 1.0.0 structural negative cases must be ported to 1.0.1.
Additional mandatory semantic negative cases:

- `duplicate-view.json`;
- `missing-view.json`;
- `reordered-view.json`;
- `unknown-view.json`;
- `wrong-view-allowlist-hash.json`;
- `duplicate-specification.json`;
- `missing-specification.json`;
- `reordered-specification.json`;
- `unknown-specification.json`;
- `stale-specification-version.json`.

Each negative fixture must identify its expected rejection class in the
correction verification record or a separate machine-readable case ledger.

### 4.4 New verifier

Create:

```text
scripts/rcc002/verify_s8rr002_artifacts.py
```

Do not repurpose the historical
`verify_s8bcp001_artifacts.py`.

The new verifier must:

1. verify the expected seven specification versions and exact file hashes;
2. extract the six authoritative view contracts from Data Pipeline 0.8.0;
3. extract the seven-document profile from Reproducibility and Manifest
   0.8.1;
4. prove the Section 24 example matches both extracted contracts exactly;
5. prove every positive 1.0.1 fixture matches both contracts exactly;
6. prove every semantic negative fixture differs in exactly its declared
   invalid dimension;
7. verify the 1.0.1 schema encodes the exact ordered contracts;
8. run structural schema validation for every positive and negative fixture,
   using a documented validator and pinned version;
9. fail if a negative fixture is accepted or a positive fixture is rejected;
10. report actual distinct positive-payload counts instead of filename counts;
11. verify UTF-8 without BOM, LF endings, valid JSON and stable SHA-256
    inventory.

If a new runtime dependency is proposed for Draft 2020-12 validation, it must
be separately justified, pinned and reviewed. A hidden or network-dependent
runtime validator is not acceptable.

### 4.5 Tests

Add focused tests that independently prove:

- exact six-view order, identity and hashes;
- exact seven-document order, identity, versions and hashes;
- Dataset Manifest 1.0.0 cannot be produced by new S8 code;
- Dataset Manifest 1.0.1 accepts both positive fixtures;
- every negative fixture is rejected for the intended reason;
- the verifier does not merely count fixture files;
- the Section 24 example and positive fixtures are semantically identical in
  their registered profiles;
- old 1.0.0 files remain byte-identical.

## 5. Files explicitly outside scope

- all S0-S7 production code;
- all S0-S7 scientific formulas, values and fingerprints;
- any `rcc002/s8/` production module;
- source-provider registries and provider evidence;
- the protected untracked
  `scripts/build_rcc002_spec_bundle.py`;
- historical certification and review documents;
- Dataset Manifest Schema 1.0.0 and its historical fixtures;
- real dataset generation or publication.

## 6. Mandatory sequence

1. Independently review this proposal for scientific consistency.
2. Independently review this proposal for architecture and identity safety.
3. Resolve every blocking or major review finding.
4. Approve the final correction design.
5. Generate the exact corrected normative/schema/fixture/verifier candidate.
6. Run mechanical verification and focused tests.
7. Obtain independent scientific and architecture reviews of the generated
   artifacts.
8. Certify and commit the corrected candidate.
9. Regenerate the S8 implementation input from the new certified HEAD.
10. Repeat S8 readiness.
11. Begin S8 implementation only after an explicit `READY` verdict.

## 7. Review checklist

Independent reviewers must explicitly answer:

1. Is `views` unambiguously separated from the physical `artifacts`
   inventory?
2. Are the six view entries and their canonical order complete and correct?
3. Is the seven-document specification profile complete and correctly
   ordered?
4. Is `1.0.1` the correct non-destructive schema version treatment?
5. Does the proposal preserve historical `1.0.0` bytes and certification
   evidence?
6. Can every invalid duplicate, missing, reordered, unknown, stale or
   hash-inconsistent case fail closed?
7. Is structural validation reproducible without an undeclared dependency?
8. Does any proposed change alter S0-S7 science, leakage semantics or
   deterministic data values?
9. Does any proposed identity edge create a cycle?
10. Is the correction set minimal and complete?

## 8. Required verdict

The independent review must end with exactly one:

```text
APPROVE
APPROVE_WITH_CONDITIONS
REJECT
```

Any unresolved manifest-validity, view-membership, specification-profile,
identity, immutability or verification ambiguity prevents `APPROVE`.
