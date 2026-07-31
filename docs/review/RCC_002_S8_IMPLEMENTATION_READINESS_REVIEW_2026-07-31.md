# RCC-002 S8 Implementation Readiness Review

## Document control

| Field | Value |
|---|---|
| Review ID | `RCC-002-S8-RR-002` |
| Review date | `2026-07-31` |
| Stage | `S8_EXPORT` |
| Repository baseline | `fd0a8aa0231c6e2e72f4616be9c154febe5ab26a` |
| Baseline commit | `Implement and certify RCC-002 S8 blocker corrections` |
| Source archive SHA-256 | `742a87c945635eba3cba907de74815e0bf0d54bb18ab8fb5bd6078735a4ed6e5` |
| Input package | `RCC_002_S8_IMPLEMENTATION_INPUT_2026-07-31.zip` |
| Prior readiness review | `RCC_002_S8_IMPLEMENTATION_READINESS_REVIEW_2026-07-30.md` |
| Review class | Repeated internal implementation-readiness review |

## 1. Executive decision

The five blockers reported by the historical S8 readiness review are closed
at the certified normative and S0-S7 implementation levels.

The repeated review nevertheless identified two new blocking contradictions
inside the certified Dataset Manifest artifacts:

1. the two positive Dataset Manifest fixtures and the normative Section 24
   example list Audit View V2 six times instead of listing the six distinct
   registered S8 views;
2. the same artifacts use placeholder specification IDs and versions instead
   of the mandatory current seven-document specification profile.

Both defects affect manifest validity and deterministic dataset identity.
They cannot be silently repaired in S8 code because the affected files belong
to the certified normative and fixture baseline.

No S8 production code was created.

## 2. Evidence inspected

The review inspected:

- all seven current RCC-002 specifications;
- the corrected normative-candidate ledger and root normative ledger;
- the S8 blocker-correction proposal, dependency matrix and identity graph;
- both S8BCP-001 Revision 2 certification decisions;
- the historical S8 readiness review;
- the complete S0-S7 implementation and test tree;
- all six manifest JSON Schemas;
- all 12 positive and 66 negative manifest fixtures;
- `scripts/rcc002/verify_s8bcp001_artifacts.py`;
- the S8BCP-001 implementation scientific and architecture review chains.

## 3. Mechanical verification

| Gate | Result |
|---|---|
| Uploaded archive SHA-256 | PASS |
| ZIP integrity | PASS |
| Protected untracked builder absent | PASS |
| Repository root `SHA256SUMS` | PASS |
| Corrected normative candidate ledger | PASS |
| Compileall | PASS |
| RCC-002 unit tests | 631/631 PASS |
| Regression tests | 170/170 PASS |
| Package inventory ledger | PASS |

These passing gates establish byte integrity and the certified S0-S7
baseline. They do not resolve semantic contradictions in certified S8
manifest examples and fixtures.

## 4. Prior blocker disposition

| Historical finding | Current disposition | Evidence |
|---|---|---|
| `S8-RR-B01` Source Snapshot identity underdefined | CLOSED | Registered retrieval, column, timestamp, Source Snapshot V1 and Source Row ID V2 profiles; certified S0 implementation |
| `S8-RR-B02` `indicator_schema_ref` absent upstream | CLOSED | Exact S3 field and literal; propagation through S7; independent review and implementation certification |
| `S8-RR-B03` Audit grain and identity circular | CLOSED | Audit V1 withdrawn; Audit V2 exactly equals the 534-field Label Research row view and contains no S8/manifest self-identities |
| `S8-RR-B04` Machine-readable manifest schemas absent | PARTIALLY CLOSED | Six schemas exist and compile, but the Dataset Manifest positive fixtures expose unresolved semantic-contract defects described below |
| `S8-RR-B05` Timestamp-unit transition unnormalized | CLOSED | Registered period-selected millisecond/microsecond profile, exact conversion and evidence-bound S0/S1 parity |

## 5. New blocking findings

### S8-RR2-B01 — Dataset Manifest view inventory contradicts the S8 registry

Severity: **BLOCKER**

#### Evidence

The authoritative view contracts define six distinct views:

| Schema reference | Field count | Allowlist SHA-256 |
|---|---:|---|
| `rcc002.view.research-features/1.0.0` | 232 | `2f2fd811b5ed8754ad8b02ee2222d885d7da3e7551ecbd5cf65fe38831c0806e` |
| `rcc002.view.backtest-inputs/1.0.0` | 232 | `2f2fd811b5ed8754ad8b02ee2222d885d7da3e7551ecbd5cf65fe38831c0806e` |
| `rcc002.view.paper/1.0.0` | 232 | `2f2fd811b5ed8754ad8b02ee2222d885d7da3e7551ecbd5cf65fe38831c0806e` |
| `rcc002.view.live/1.0.0` | 232 | `2f2fd811b5ed8754ad8b02ee2222d885d7da3e7551ecbd5cf65fe38831c0806e` |
| `rcc002.view.label-research/1.0.0` | 534 | `0e223d60ed4139f73194f1cb3b886a8eface9229183ad522a093e966827518cc` |
| `rcc002.view.audit/2.0.0` | 534 | `0e223d60ed4139f73194f1cb3b886a8eface9229183ad522a093e966827518cc` |

This exact inventory appears in:

- Data Pipeline 0.8.0, Section 7.9.3;
- Label and Forward Return 0.5.0, Section 26.1;
- Reproducibility and Manifest 0.8.0, Section 8.7;
- `RCC_002_S8BCP001_REV2_DEPENDENCY_MATRIX_2026-07-30.md`.

In contradiction, Reproducibility and Manifest 0.8.0, Section 24, contains
six identical `rcc002.view.audit/2.0.0` entries.

The same invalid six-entry array occurs in both certified positive fixtures:

- `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.0/minimal-valid.json`;
- `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.0/complete-valid.json`.

The Dataset Manifest JSON Schema requires only `minItems: 6` for `views`.
It does not require uniqueness or the exact six registered schema
identities. Consequently the six-duplicate array passes the structural
schema.

`scripts/rcc002/verify_s8bcp001_artifacts.py` counts positive and negative
fixture files but does not execute schema validation or verify Dataset
Manifest view-inventory semantics.

#### Impact

An S8 implementation following the certified positive fixtures can:

- omit five mandatory registered views;
- accept six duplicate Audit View references;
- publish a structurally valid but semantically invalid Dataset Manifest;
- compute `manifest_id`, `dataset_id` lineage and release evidence from the
  wrong view inventory;
- pass the current mechanical correction verifier.

This directly affects manifest validity, leakage-bound view registration,
identity preimages and reproducibility. Readiness therefore cannot be granted.

#### Required correction

1. Decide and state explicitly whether `DatasetManifest.views` inventories
   the exact registered six-view profile or only physically produced views.
2. Align Section 24, both positive Dataset Manifest fixtures and the Dataset
   Manifest schema/semantic validator with that single rule.
3. If the intended contract is the full profile already implied by
   `minItems: 6`, replace the duplicate array with the exact six registered
   schema references, versions and allowlist hashes.
4. Add negative fixtures for duplicate, missing, unknown and wrong-hash view
   entries.
5. Make the committed verifier actually validate positive and negative
   fixtures and the cross-document view inventory; counting files is
   insufficient.
6. Determine whether the released `1.0.0` schema requires a corrected version
   identity before modifying its acceptance behavior.
7. Perform focused scientific and architecture re-review and certification.

### S8-RR2-B02 — Positive fixtures violate the mandatory specification profile

Severity: **BLOCKER**

#### Evidence

Reproducibility and Manifest 0.8.0, Section 12.3, requires:

| Document ID | Version |
|---|---:|
| `RCC_002_DATA_PIPELINE_SPECIFICATION` | `0.8.0` |
| `RCC-002-DV` | `0.6.0` |
| `RCC-002-IS` | `0.4.3` |
| `RCC-002-ST` | `0.4.2` |
| `RCC-002-RG` | `0.5.1` |
| `RCC-002-LF` | `0.5.0` |
| `RCC-002-RM` | `0.8.0` |

Section 24 and both positive Dataset Manifest fixtures instead contain
placeholder IDs `RCC-002-SPEC-0` through `RCC-002-SPEC-6`, all at version
`1.0.0`.

The Dataset Manifest JSON Schema requires only seven generic
`versioned_reference` entries. It does not bind them to the current canonical
profile. The current mechanical verifier checks the seven specification
files' headers but does not cross-check the Dataset Manifest fixtures'
`specification_profile`.

#### Impact

The positive fixtures do not represent a valid current RCC-002 Dataset
Manifest. Copying them into S8 would manifest the wrong normative baseline
and make the resulting dataset knowledge lineage and identity evidence false.

#### Required correction

1. Replace placeholder specification references in Section 24 and both
   positive fixtures with the exact Section 12.3 profile.
2. Add semantic validation requiring each mandatory document exactly once at
   the certified version.
3. Add negative fixtures for missing, duplicate, unknown and stale
   specification references.
4. Extend the committed verifier to cross-check the fixtures against Section
   12.3 and the certified dependency matrix.
5. Include the correction in the same focused re-review and certification
   cycle as `S8-RR2-B01`.

## 6. Non-blocking observations

### S8-RR2-O01 — Positive fixture pairs are byte-identical

For every manifest type, `minimal-valid.json` and `complete-valid.json` have
the same SHA-256. This is not independently blocking if the schema has no
meaningful optional positive branch, but it means the reported 12 positive
fixtures represent only six distinct payloads. The correction cycle should
either make the pairs exercise distinct valid branches or document why one
positive payload per manifest type is sufficient.

### S8-RR2-O02 — Field-registry digest remains derivable but unpublished

The exact field ownership registry and all view allowlist hashes are
deterministically derivable, but no versioned literal
`field_registry_sha256` was found. This remains non-blocking only if S8
derives and independently verifies the value from the certified registry
preimage rather than inventing a local value.

### S8-RR2-O03 — Physical serialization is profile-selectable

Parquet is preferred but not mandated as the only S8 physical format. This is
not a normative ambiguity: semantic and physical identities are explicitly
separated. The initial implementation must keep serialization behind an
explicit physical publication profile and must not claim dataset publication.

## 7. Confirmed S8 scope after correction

Once the two blockers are closed, S8 remains limited to:

- six exact positive view projections;
- S7 row/key/order/value reconciliation;
- leakage rejection;
- canonicalization and deterministic identity builders;
- six manifest builders and structural plus semantic validators;
- artifact inventory and lineage validation;
- temporary, quarantine, candidate and atomic publication state handling;
- release-ledger generation.

S8 must not change any S0-S7 scientific value or publish a real dataset during
the implementation and review cycle.

## 8. Final verdict

```text
S8 IMPLEMENTATION READINESS: NOT READY
IMPLEMENTATION AUTHORIZATION: DENIED UNTIL BLOCKER CLOSURE
PRIOR BLOCKERS CLOSED: 4
PRIOR BLOCKERS PARTIALLY CLOSED: 1
NEW BLOCKERS: 2
NON-BLOCKING OBSERVATIONS: 3
S8 PRODUCTION CODE CREATED: NO
DATASET PUBLICATION AUTHORIZED: NO
```
