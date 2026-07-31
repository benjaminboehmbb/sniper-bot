# RCC-002 S8-RR-002 Blocker Correction Proposal Revision 2

## Document control

| Field | Value |
|---|---|
| Proposal ID | `RCC-002-S8RR002-BCP-001-REV2` |
| Date | `2026-07-31` |
| Repository baseline | `d4b4befecc9580a175f39966f2dfc2abcb03356b` |
| Trigger | `RCC_002_S8_IMPLEMENTATION_READINESS_REVIEW_2026-07-31.md` |
| Superseded proposal | `RCC_002_S8RR002_BLOCKER_CORRECTION_PROPOSAL_2026-07-31.md` |
| Independent review | `RCC_002_S8RR002_BLOCKER_CORRECTION_PROPOSAL_INDEPENDENT_REVIEW_2026-07-31.md` |
| Prior review verdict | `REJECT` |
| Findings in scope | `S8-RR2-B01`, `S8-RR2-B02` |
| Change class | Focused normative and machine-readable contract correction |
| S8 implementation | Prohibited |
| Dataset publication | Prohibited |
| Status | Revised proposal for independent scientific and architecture re-review |

## 1. Decision requested

Approve one focused correction cycle that:

1. defines `DatasetManifest.views` as the exact ordered six-view RCC-002
   registry snapshot;
2. defines `DatasetManifest.specification_profile` as the exact ordered
   seven-document current specification profile;
3. introduces Dataset Manifest Schema `1.0.1` without modifying certified
   Schema `1.0.0` or its historical fixtures;
4. changes Reproducibility and Manifest from `0.8.0` to `0.9.0`;
5. corrects the normative example and creates valid `1.0.1` fixtures;
6. adds a versioned verifier scope, a pinned Draft 2020-12 validator and
   mechanically executable cross-document verification;
7. repeats focused review, certification and S8 readiness before any S8 code.

## 2. Revision 2 resolution summary

Revision 2 resolves every open item from the independent `REJECT` review.

| Review finding | Resolution in Revision 2 |
|---|---|
| `S8RR002-PR-SCI-001` | Reclassifies Reproducibility and Manifest `0.8.0` to `0.9.0` as a minor normative change |
| `S8RR002-PR-SCI-002` | Requires literal hashes for six non-self specifications and one labelled zero placeholder only for the RM self-entry in Section 24 |
| `S8RR002-PR-ARCH-001` | Requires a committed versioned verifier-scope manifest; prohibits unscoped traversal |
| Checklist item 7 | Pins `jsonschema==4.26.0` as a review-only dependency and requires `Draft202012Validator` |
| `S8RR002-PR-ARCH-004` | Clarifies family growth over time versus an exact closed current manifest profile |
| `S8RR002-PR-ARCH-002` | Explicitly excludes the semantically distinct Stage Manifest field |
| Historical verifier note | Documents that the old verifier is meaningful only for its curated correction-bundle scope |

The unrelated illustrative field drift in Reproducibility Section 8.5 remains
outside this correction and is reserved for a separate editorial cycle.

## 3. Problem statement

The authoritative specifications register six distinct S8 views and seven
exact specification-profile entries. In contrast:

- Reproducibility and Manifest `0.8.0`, Section 24, lists Audit View V2 six
  times;
- both positive Dataset Manifest `1.0.0` fixtures contain the same duplicate
  view array;
- those artifacts use `RCC-002-SPEC-0` through `RCC-002-SPEC-6`, each at
  `1.0.0`, instead of the mandatory current specification profile;
- Dataset Manifest Schema `1.0.0` accepts those arrays because it constrains
  only generic item structure and minimum counts;
- the historical correction verifier counts fixtures but does not validate
  their structural acceptance or semantic profile correctness.

These defects affect the positive implementation oracle for S8 manifests.
They must not be resolved through undocumented S8 code behavior.

## 4. Normative decisions

### 4.1 Meaning of `DatasetManifest.views`

`DatasetManifest.views` is the canonical registry snapshot for the declared
dataset profile. It is not the physical artifact inventory.

Physical views materialized by a particular build remain listed under
`artifacts`. A minimal build may therefore contain fewer than six physical
data artifacts while `views` records the exact six schemas that define the
current RCC-002 dataset profile.

### 4.2 Exact view order

The canonical order is:

1. `rcc002.view.research-features/1.0.0`;
2. `rcc002.view.backtest-inputs/1.0.0`;
3. `rcc002.view.paper/1.0.0`;
4. `rcc002.view.live/1.0.0`;
5. `rcc002.view.label-research/1.0.0`;
6. `rcc002.view.audit/2.0.0`.

The first four entries use:

```text
2f2fd811b5ed8754ad8b02ee2222d885d7da3e7551ecbd5cf65fe38831c0806e
```

The final two entries use:

```text
0e223d60ed4139f73194f1cb3b886a8eface9229183ad522a093e966827518cc
```

Every entry must contain the matching `schema_id`, `schema_version`,
`schema_ref` and `allowlist_sha256`. The required
`schema_fingerprint_sha256` remains a digest of the complete logical schema
contract under the existing fingerprint rules; this correction does not
invent a new registry-level constant for it.

Missing, duplicate, reordered, unknown, stale or hash-inconsistent entries
invalidate the complete Dataset Manifest.

### 4.3 Exact specification-profile order

The corrected current profile is:

1. `RCC_002_DATA_PIPELINE_SPECIFICATION` / `0.8.0`;
2. `RCC-002-DV` / `0.6.0`;
3. `RCC-002-IS` / `0.4.3`;
4. `RCC-002-ST` / `0.4.2`;
5. `RCC-002-RG` / `0.5.1`;
6. `RCC-002-LF` / `0.5.0`;
7. `RCC-002-RM` / `0.9.0`.

For the six unchanged non-self documents, Section 24 must use these literal
file hashes:

| Document ID | Version | Literal SHA-256 |
|---|---|---|
| `RCC_002_DATA_PIPELINE_SPECIFICATION` | `0.8.0` | `0e060d30b75082b74eb5211b1d378837aa7872d86f62e5e162586e2a2cc37fad` |
| `RCC-002-DV` | `0.6.0` | `459c4a99a266b420d52a69f2fb1a6b36a99529e999842bc8271f3336c444bb31` |
| `RCC-002-IS` | `0.4.3` | `0d8ad604cce88daa56193ee054f4d28237d60135a67cebbde883d2c00d18539d` |
| `RCC-002-ST` | `0.4.2` | `b3de8b4b7c69c30fd811edbeceb246b1b981d7d561c54b585535e72ca0fd8c74` |
| `RCC-002-RG` | `0.5.1` | `37ee84f1ddd86c0765e9c4df3b57aa5907472ba481f54181e8f8d6dccf354cdc` |
| `RCC-002-LF` | `0.5.0` | `526665966c83c8fc7254c663474fe08ee721125ae6cdcd88e5a4f5b80af5882f` |

The Section 24 `RCC-002-RM/0.9.0` self-entry must use exactly one all-zero
digest, explicitly labelled in adjacent normative prose as a non-literal
self-reference placeholder. No other specification-profile digest in that
example may be a placeholder.

Concrete positive machine-readable fixtures are generated only after the
`0.9.0` specification bytes are final. They must contain the actual SHA-256
for all seven documents, including `RCC-002-RM/0.9.0`.

Missing, duplicate, reordered, unknown, stale or hash-inconsistent entries
invalidate the complete Dataset Manifest.

### 4.4 Closed current profile and future family growth

The phrase "must reference at least the following documents" in
Reproducibility Section 12.3 governs completeness as the RCC-002
specification family evolves across future profile versions. It does not
permit extra entries inside one declared current profile.

For each declared Dataset Manifest profile version,
`specification_profile` is exact, ordered and closed. A future additional
specification therefore requires an explicit profile and schema revision; it
must not be appended silently to a `1.0.1` manifest.

### 4.5 Version treatment

Certified Dataset Manifest Schema `1.0.0` and its fixtures remain
byte-immutable historical artifacts.

The corrected schema identity is:

```text
schema_id=rcc002.dataset-manifest
schema_version=1.0.1
schema_ref=rcc002.dataset-manifest/1.0.1
```

Schema patch `1.0.1` repairs acceptance of payloads already invalid under the
cross-document normative contract. Dataset Manifest Schema `1.0.0` is
withdrawn for prospective S8 production and must not be emitted by new code.
Historical verification remains permitted.

Reproducibility and Manifest changes from `0.8.0` to `0.9.0`. This is a minor
normative change because it adds explicit canonical snapshot semantics,
ordered exact membership, a new schema identity and a prospective withdrawal
rule. The classification follows the document's own version-history
precedent for new normative content.

### 4.6 Same-named Stage Manifest field

Stage Manifest Schema `1.0.0` also contains a field named
`specification_profile`. That field is semantically distinct, does not
represent the exact seven-document Dataset Manifest profile and does not
exhibit either blocker. It is explicitly outside this correction scope.

## 5. Exact correction set

### 5.1 Modified normative file

```text
docs/specifications/RCC_002_REPRODUCIBILITY_AND_MANIFEST_2026-07-23.md
```

Required changes:

- version `0.8.0` to `0.9.0`;
- Section 8.6: Dataset Manifest Schema `1.0.1`;
- explicit withdrawal of Dataset Manifest Schema `1.0.0` for prospective
  production;
- explicit canonical order and exact membership rules for `views`;
- explicit canonical order and exact membership rules for
  `specification_profile`;
- Section 12.3 self-version `RCC-002-RM/0.9.0`;
- Section 12.3 clarification of future family growth versus the exact closed
  current profile;
- Section 24 Dataset Manifest Schema `1.0.1`;
- Section 24 six distinct view entries;
- Section 24 exact seven-document ID and version profile;
- Section 24 literal hashes for the six non-self documents and one labelled
  all-zero placeholder only for the RM self-entry;
- dated correction record with finding IDs and scope exclusions.

No other current specification requires a semantic version change.

### 5.2 New schema

```text
schemas/rcc002/manifests/dataset-manifest/1.0.1.schema.json
```

The schema must preserve every applicable `1.0.0` structural constraint and:

- require exactly six `views`;
- bind their exact canonical order with Draft 2020-12 `prefixItems`;
- reject additional view entries with `items: false`;
- bind each view identity, version, reference and allowlist hash;
- require exactly seven `specification_profile` entries;
- bind their exact canonical order, document IDs and versions;
- retain digest-format validation for view schema fingerprints and
  specification hashes while assigning their exact reconciliation to the
  semantic verifier;
- reject additional specification entries with `items: false`;
- preserve strict nested `additionalProperties: false`;
- use the exact new schema identity constants.

### 5.3 New fixtures

Create:

```text
tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/
```

Positive fixtures:

- `minimal-valid.json`;
- `complete-valid.json`.

Both must carry the six distinct view entries and exact seven-document
profile, including all seven actual specification hashes. If their intended
optional coverage remains identical, retain only one positive fixture or make
their difference explicit. Byte-identical duplicates are not independent
evidence.

All applicable `1.0.0` structural negative cases must be ported to `1.0.1`.
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

Each negative fixture must identify its expected rejection class in a
machine-readable case ledger.

### 5.4 Pinned review dependency

Create:

```text
requirements-rcc002-review.txt
```

It must contain:

```text
jsonschema==4.26.0
```

This is a review, test and certification dependency, not an S8 production
runtime dependency. The repository's production `requirements.txt` remains
unchanged.

Version `4.26.0` is selected because the official package declares full Draft
2020-12 support, supports the repository's Python version and is a stable,
versioned release.

The verifier must import `jsonschema.Draft202012Validator`, call
`Draft202012Validator.check_schema` on Schema `1.0.1`, and fail unless the
installed `jsonschema` distribution version is exactly `4.26.0`. Validation
must be local and network-independent after dependency installation.

### 5.5 Versioned verifier scope

Create:

```text
docs/review/evidence/RCC_002_S8RR002_CORRECTION_VERIFIER_SCOPE_V1.json
```

The file must:

- declare its own scope schema version as `1`;
- list every normative source, schema, fixture, case ledger and verifier input
  path required for the correction verification;
- use repository-relative POSIX paths in deterministic lexical order;
- contain no duplicate, absolute or parent-traversal path;
- distinguish immutable reference inputs from correction-candidate outputs;
- be consumed directly by the new verifier.

The scope manifest is a versioned path contract, not a self-hashing ledger.
Candidate byte hashes must be recorded separately after all candidate bytes
are final.

The verifier must fail on a missing, duplicate, unsafe or undeclared required
scope entry. It must not use unscoped `Path.rglob`, `os.walk`, shell `find` or
equivalent full-tree traversal. This makes the verification portable outside
a Git working tree.

### 5.6 New verifier

Create:

```text
scripts/rcc002/verify_s8rr002_artifacts.py
```

Do not modify or repurpose historical
`scripts/rcc002/verify_s8bcp001_artifacts.py`. That historical verifier is
documented as meaningful only against its curated correction-bundle input,
not an arbitrary full repository working tree.

The new verifier must:

1. load and validate the versioned scope manifest before other checks;
2. verify the expected seven specification versions and exact file hashes;
3. extract the six authoritative view contracts from Data Pipeline `0.8.0`;
4. extract the seven-document profile from Reproducibility and Manifest
   `0.9.0`;
5. prove the Section 24 example matches both extracted contracts exactly,
   applying only the declared RM self-hash placeholder exception;
6. prove every positive `1.0.1` fixture matches both contracts exactly and
   contains all seven literal hashes;
7. prove every semantic negative fixture differs in exactly its declared
   invalid dimension;
8. verify Schema `1.0.1` encodes the exact ordered contracts;
9. run Draft 2020-12 structural validation for every positive and negative
   fixture with `jsonschema==4.26.0`;
10. fail if a negative fixture is accepted or a positive fixture is rejected;
11. report actual distinct positive payload counts, not filename counts;
12. verify UTF-8 without BOM, LF endings, valid JSON and stable candidate
    SHA-256 inventory.

### 5.7 Tests

Add focused tests that independently prove:

- exact six-view order, identity and hashes;
- exact seven-document order, identity, versions and hashes;
- Reproducibility and Manifest `0.9.0` exposes only Dataset Manifest `1.0.1`
  for prospective S8 production;
- Dataset Manifest `1.0.1` accepts every positive fixture;
- every negative fixture is rejected for its declared reason;
- the verifier uses only the committed scope manifest;
- the verifier does not merely count fixture files;
- Section 24 and positive fixtures are semantically identical except for the
  explicitly declared RM self-hash placeholder;
- old `1.0.0` files remain byte-identical;
- Stage Manifest `specification_profile` remains untouched and is not treated
  as the Dataset Manifest profile.

No S8 production module or S8 implementation test is created in this
correction cycle. The later S8 implementation must add a gate test proving
that production code cannot emit Dataset Manifest `1.0.0`.

## 6. Files explicitly outside scope

- all S0-S7 production code and scientific values;
- any `rcc002/s8/` production module;
- source-provider registries and provider evidence;
- the protected untracked `scripts/build_rcc002_spec_bundle.py`;
- historical certification and review documents;
- Dataset Manifest Schema `1.0.0` and its historical fixtures;
- Stage Manifest Schema, fixtures and `specification_profile` semantics;
- pre-existing illustrative field-name drift in Reproducibility Section 8.5;
- real dataset generation or publication.

## 7. Mandatory sequence

1. Independently re-review Revision 2 for scientific consistency.
2. Independently re-review Revision 2 for architecture and identity safety.
3. Resolve every blocking or major re-review finding.
4. Approve the final correction design.
5. Generate the exact corrected normative, schema, fixture, scope, verifier
   and test candidate.
6. Run mechanical verification and focused tests.
7. Obtain independent scientific and architecture reviews of the generated
   artifacts.
8. Certify and commit the corrected candidate.
9. Regenerate the S8 implementation input from the new certified HEAD.
10. Repeat S8 readiness.
11. Begin S8 implementation only after an explicit `READY` verdict.

## 8. Re-review checklist

Independent reviewers must explicitly answer:

1. Is `views` unambiguously separated from the physical `artifacts`
   inventory?
2. Are the six view entries and canonical order complete and correct?
3. Is the seven-document profile complete, correctly ordered and updated to
   `RCC-002-RM/0.9.0`?
4. Is Dataset Manifest Schema `1.0.1` the correct non-destructive treatment?
5. Is Reproducibility and Manifest `0.9.0` consistent with its own versioning
   precedent?
6. Are the Section 24 hash rules deterministic and self-reference-safe?
7. Does the proposal preserve historical `1.0.0` bytes and evidence?
8. Can every invalid duplicate, missing, reordered, unknown, stale or
   hash-inconsistent case fail closed?
9. Is `jsonschema==4.26.0` explicit, pinned, local and review-only?
10. Does the versioned scope manifest eliminate unscoped traversal ambiguity?
11. Does any change alter S0-S7 science, leakage semantics or deterministic
    data values?
12. Does any proposed identity edge create a cycle?
13. Are the Stage Manifest field and Section 8.5 drift correctly excluded?
14. Is the correction set minimal and complete?

## 9. Required verdict

The independent re-review must end with exactly one:

```text
APPROVE
APPROVE_WITH_CONDITIONS
REJECT
```

Any unresolved manifest-validity, view-membership, specification-profile,
identity, versioning, immutability, dependency or verification-scope ambiguity
prevents `APPROVE`.
