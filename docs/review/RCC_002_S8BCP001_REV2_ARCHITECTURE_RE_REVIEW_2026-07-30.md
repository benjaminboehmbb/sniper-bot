# RCC-002 S8BCP-001 Revision 2 Architecture Re-Review

## Document Control

| Field | Value |
|---|---|
| Review ID | `RCC-002-S8BCP001-REV2-ARR-001` |
| Date | 2026-07-30 |
| Reviewed proposal | `RCC_002_S8_BLOCKER_CORRECTION_PROPOSAL_2026-07-30.md` |
| Proposal ID/revision | `RCC-002-S8BCP-001`, revision 2 |
| Proposal SHA-256 | `f3adb44c16b9927275d10baee410154fb2e7b4075309a8b56fec985afedd8706` |
| Prior review | `RCC-002-S8BCP001-AIR-001` |
| Decision | **PASS FOR NORMATIVE ARTIFACT GENERATION** |
| Limitation | **NOT A SPECIFICATION OR IMPLEMENTATION CERTIFICATION** |

## 1. Scope

This re-review tests whether revision 2 closes the first architecture review's
blocker, major, and minor design findings. It does not certify artifacts that
have not yet been generated.

## 2. Finding Resolution

| Finding | Result | Evidence in revision 2 |
|---|---|---|
| `AIR-BLK-001` | CLOSED IN DESIGN | `source_row_id` V2 includes snapshot ID, canonical file ordinal, and original record index |
| `AIR-BLK-002` | CLOSED IN DESIGN | Exact release classes, artifact-set preimage, serialization order, and DAG verification are defined |
| `AIR-MAJ-001` | CLOSED | Archive-period selection precedes timestamp conversion and coverage |
| `AIR-MAJ-002` | CLOSED | Header handling is retrieval-profile-owned and non-inferential |
| `AIR-MAJ-003` | CLOSED | S0 remains per physical archive; Source Manifest owns the aggregate ordered snapshot |
| `AIR-MIN-001` | CLOSED | In-candidate duplicate rejection is separated from preserved cross-snapshot provider revision |
| `AIR-MIN-002` | CLOSED | A generated document/schema dependency matrix is mandatory |

## 3. Multi-file Row Identity

The new semantic tuple is:

```text
source_snapshot_id
source_file_ordinal
original_record_index
```

The file ordinal is derived from the canonical provider-relative source-file
order, not local discovery order. This removes the demonstrated collision
where every source file previously restarted its row index at zero.

The V2 profile preserves:

- uniqueness within a multi-file snapshot;
- deterministic original-record ordering;
- exact source-record lineage;
- stable S2 duplicate, anomaly, gap, and segment maps;
- historical V1 read-only compatibility.

The new profile must be implemented as V2; changing V1 in place remains
prohibited.

## 4. S0 and Header Ownership

Revision 2 selects one coherent model:

- one immutable S0 artifact per physical provider archive;
- one aggregate Source Manifest per ordered source snapshot;
- no lossy scalar projection for new multi-file snapshots;
- registered `ABSENT` or `PRESENT_EXACT` header behavior;
- S0 validates the selected behavior;
- S1 consumes it without inference;
- S2 retains canonical temporal-quality ownership.

This removes the earlier scalar-versus-array ambiguity and the current
generic-header conflict.

## 5. Identity Acyclicity

Revision 2 defines:

- `dataset_artifact_set_id` over ordered `DATA_ARTIFACT` records only;
- `SCHEMA_ARTIFACT`, `CONTROL_MANIFEST`, `REVIEW_ARTIFACT`, and
  `RELEASE_LEDGER` as excluded release-control classes;
- Dataset Manifest inventory of data, schemas, and already-final
  pre-Dataset child manifests;
- post-Dataset Reproduction and Review Manifests referencing the Dataset
  Manifest in one direction only;
- final `SHA256SUMS` containing every released file except itself;
- an external distribution record as the only owner of the ledger's final
  byte hash.

The permitted order is:

```text
data/schema bytes
-> Source/Stage/Run child manifests
-> Dataset Manifest
-> post-Dataset Reproduction/Review/certification records
-> SHA256SUMS
-> external distribution record
```

No `artifact_id` dependency on `dataset_artifact_set_id` exists in the
baseline identity model; therefore the proposed artifact-set preimage does
not introduce a reverse edge.

## 6. Mandatory Artifact-Generation Gates

The generated correction set must still prove:

1. all V2 row IDs are unique and source-resolvable;
2. archive discovery order cannot change identities;
3. all six manifest JSON Schemas fail closed;
4. every release file has exactly one release class;
5. the generated identity/reference graph is acyclic;
6. the Dataset Manifest inventories every data and schema artifact but not
   itself or post-Dataset controls;
7. the final ledger is complete and self-excluding;
8. all document, schema, registry, and view references resolve with exact
   versions and hashes;
9. Audit View V2 reproduces exactly the certified 534-field allowlist;
10. `indicator_schema_ref` propagates unchanged from S3 through S7.

## 7. Decision

**PASS FOR NORMATIVE ARTIFACT GENERATION**

All first-review architecture findings are closed at proposal-design level.
Revision 2 may proceed to corrected specification, schema, registry, fixture,
dependency-matrix, and identity-graph generation.

Implementation remains unauthorized until those generated artifacts pass
mechanical verification, focused scientific and architecture review, and
bundle certification.
