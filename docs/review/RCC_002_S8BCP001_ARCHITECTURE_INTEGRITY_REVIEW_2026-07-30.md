# RCC-002 S8BCP-001 Architecture Integrity Review

## Document Control

| Field | Value |
|---|---|
| Project | RCC-002 Scientific Data Processing Architecture |
| Review ID | `RCC-002-S8BCP001-AIR-001` |
| Review type | Focused internal architecture integrity review |
| Date | 2026-07-30 |
| Reviewed proposal | `RCC_002_S8_BLOCKER_CORRECTION_PROPOSAL_2026-07-30.md` |
| Proposal ID | `RCC-002-S8BCP-001` |
| Baseline commit | `a4b7c72b2e7a12bac139d1bfce8cb05200d6fd58` |
| Reviewer | OpenAI Codex internal review |
| Decision | **NOT APPROVED — TWO BLOCKERS AND REQUIRED MAJOR CORRECTIONS** |

## 1. Scope

This review evaluates:

- ownership across S0, S1, S2, and S8;
- row grain and identity uniqueness;
- source snapshot aggregation;
- schema and component-version impact;
- manifest and artifact identity acyclicity;
- audit-view row safety;
- compatibility with the certified S3-to-S7 contracts.

It does not change code or specifications and does not certify implementation.

## 2. Executive Decision

The proposal correctly resolves the architectural direction of all five
readiness-review blockers:

- source retrieval and source identity become versioned;
- provider timestamps become canonical before downstream use;
- `indicator_schema_ref` is restored to the S3-to-S7 row chain;
- Audit View V2 becomes row-grain-safe;
- manifest contracts become machine-readable and strict;
- self-referential byte hashes are removed from manifest bytes.

Two unresolved architecture blockers prevent approval:

1. the current `source_row_id` profile collides when one source snapshot
   contains multiple source files;
2. the artifact-set, Dataset Manifest, and release-ledger boundary is not
   precise enough to prove a complete acyclic release identity.

The proposal also needs explicit source-profile stage ownership and migration
rules. These are correctable without changing trading formulas.

## 3. Findings

### `AIR-BLK-001` — Multi-file source snapshots produce colliding row IDs

Severity: **BLOCKER**

Status: **OPEN**

The proposed source snapshot contains an ordered `source_files` array and is
therefore explicitly multi-file. The current implementation derives:

```text
source_row_id =
RCC002_S1_SOURCE_ROW_ID_V1
+ source_snapshot_id
+ original_row_index
```

`normalize_rows()` is scoped to one source file and resets
`original_row_index` to zero for every call. Consequently, row zero of every
file in the same snapshot receives the same `source_row_id`; the same is true
for every repeated index.

This breaks:

- uniqueness of the S1 row reference;
- deterministic duplicate reports;
- S2 anomaly and gap maps keyed by `source_row_id`;
- lineage from output rows to exact source records;
- stable conflict resolution based on the minimum row ID.

Required correction:

- introduce a new canonicalization profile, not an in-place change to V1;
- recommended preimage:

```text
source_row_id_profile_id
source_snapshot_id
source_file_ordinal
original_record_index
```

- derive `source_file_ordinal` from the canonical ordered `source_files`
  sequence in the source snapshot preimage;
- use fixed-width non-negative integer encodings or an equally strict
  canonical tuple encoding;
- pass the resolved file ordinal explicitly into S1 normalization;
- retain original record index before sorting or filtering;
- add uniqueness tests across files, identical indices, reordered local input
  paths, duplicate archive names, and snapshots with changed file lists;
- record the profile ID and version in Source and Stage Manifests.

Suggested identity:

```text
RCC002_S1_SOURCE_ROW_ID_V2:
<source_snapshot_id>:
<zero-padded source_file_ordinal>:
<zero-padded original_record_index>
```

Provider-relative filenames should not be inserted unescaped into the ID.

### `AIR-BLK-002` — Release identity boundary is under-specified

Severity: **BLOCKER**

Status: **OPEN**

The proposal correctly prohibits a Dataset Manifest from inventorying its own
final bytes and correctly excludes `SHA256SUMS` from its own ledger. However,
it also states that dataset logical identity and artifact-set identity are
complete before Dataset Manifest serialization.

The existing reproducibility contract requires every build to maintain an
artifact inventory containing byte hash, size, schema, and path. Without an
explicit class boundary, at least two incompatible interpretations remain:

1. `dataset_artifact_set_id` identifies every released file, which cannot be
   complete before Dataset Manifest serialization; or
2. it identifies only data-plane artifacts, while the Dataset Manifest,
   review manifests, and checksum ledger are release-control files outside
   that identity.

Required correction:

- define the exact preimage of `dataset_artifact_set_id`;
- classify every release file as `DATA_ARTIFACT`, `CONTROL_MANIFEST`,
  `REVIEW_ARTIFACT`, `SCHEMA_ARTIFACT`, or `RELEASE_LEDGER`;
- state which classes enter `dataset_artifact_set_id`;
- define the Dataset Manifest `artifacts` array as an exact class-specific
  inventory rather than the ambiguous phrase "ordered artifacts";
- require the final `SHA256SUMS` ledger to hash every released file except
  itself, including the Dataset Manifest and review records;
- place the final ledger hash only in an external certification/distribution
  record;
- prohibit reverse references from child manifests to a parent that embeds
  their final byte identities;
- add a machine-verifiable directed-acyclic-graph test over all manifest and
  artifact references.

The preferred architecture is:

```text
data/schema artifacts
-> child manifests
-> Dataset Manifest
-> review/certification records
-> SHA256SUMS
-> external distribution record
```

The exact classes may differ, but one normative acyclic model must be selected.

### `AIR-MAJ-001` — Timestamp-unit selection must precede byte-derived coverage

Severity: **MAJOR**

Status: **OPEN**

The proposal assigns both S0 and S1 to the same conversion function, which is
correct. The decision input is not yet stage-safe because the selected unit is
described using provider logical coverage while actual coverage is created by
the conversion.

Required correction:

- S0 retrieval registry owns archive-period parsing and unit-branch selection;
- the pure conversion function accepts an already-resolved unit profile;
- S0 uses it only for identity coverage and structural validation;
- S1 uses the same function for row materialization;
- S2 retains canonical time-quality and alignment ownership;
- raw timestamp magnitude is never an architectural input.

This finding is shared with `SCR-MAJ-001`.

### `AIR-MAJ-002` — Header ownership conflicts with the current generic contract

Severity: **MAJOR**

Status: **OPEN**

The proposal registers `header_mode=ABSENT`, while the current Data Validation
specification requires a present, parseable header for every file. Current
code and tests also discard the first CSV record unconditionally.

A version bump alone does not resolve the ownership conflict.

Required correction:

- replace the generic header requirement with a retrieval-profile-driven
  `header_mode`;
- define strict behavior for `ABSENT`, `PRESENT_EXACT`, and any future mode;
- have S0 validate the selected mode;
- have S1 parsing consume the already-resolved profile and never infer header
  presence;
- require `ABSENT` to treat the first non-empty record as data;
- reject an unexpected header-like record for the Binance V1 profile;
- update row counting, truncation checks, tests, and Golden fixtures
  consistently.

### `AIR-MAJ-003` — Scalar S0 provenance needs an explicit multi-file migration

Severity: **MAJOR**

Status: **OPEN**

The current S0 contracts expose scalar fields such as `source_file_name` and
`source_byte_sha256`. The proposed source snapshot preimage and Source
Manifest require an ordered list of file records.

Required correction:

- state whether S0 remains one artifact per physical source file or becomes
  one aggregate source-snapshot artifact;
- define the canonical relationship between per-file S0 artifacts and the
  aggregate Source Manifest;
- version the affected schema or manifest contract;
- define deterministic ordering and uniqueness constraints;
- preserve each file's byte hash, provider checksum, member name, coverage,
  record count, and file ordinal;
- prohibit a lossy "first file" projection into scalar provenance fields;
- define migration handling for legacy one-file snapshots.

### `AIR-MIN-001` — Duplicate period policy needs revision semantics

Severity: **MINOR**

Status: **OPEN**

The proposal rejects duplicate logical periods with different bytes. This is
correct within one candidate snapshot but could be read as rejecting a valid
provider revision across snapshots.

Required correction:

- apply the rejection within one source snapshot candidate;
- permit a changed provider archive only as a new `source_snapshot_id`;
- require `source_revision` or a documented synthetic revision record;
- require `supersedes` and preservation of the prior snapshot.

### `AIR-MIN-002` — Dependency citation updates need one generated matrix

Severity: **MINOR**

Status: **OPEN**

The proposed semantic version changes are reasonable. Mechanical citation
changes can remain patch-neutral only if generated verification proves every
document references the new specification profile consistently.

Required correction:

- generate one document-ID/version/hash dependency matrix;
- verify all normative citations and schema references mechanically;
- fail the corrected bundle if any stale profile version remains.

## 4. Accepted Architecture Decisions

| Area | Result | Assessment |
|---|---|---|
| Canonical milliseconds | PASS | Stable downstream contract |
| Versioned provider-unit profile | PASS | Correct isolation boundary |
| Shared pure S0/S1 converter | PASS | Prevents identity/data divergence |
| `indicator_schema_ref` restoration | PASS | Repairs implementation conformance without changing the certified logical schema |
| Audit View V2 row grain | PASS | Same 534-field market-row allowlist as label research is coherent |
| Provenance outside row view | PASS | Manifests and reports are the correct owners |
| Six strict JSON Schemas | PASS IN PRINCIPLE | Required artifacts still need generation and validation |
| No manifest self byte hash | PASS | Removes direct hash self-reference |
| Versioned registries and fixtures | PASS IN PRINCIPLE | Must be released and hashed with the corrected bundle |

## 5. Identity Graph Assessment

The following directions are valid:

```text
source bytes + semantic retrieval profile
-> source_snapshot_id

source_snapshot_id + semantic build configuration + code/spec/environment
-> build_id

canonical logical data
-> dataset_id

physical data-artifact inventory
-> dataset_artifact_set_id

manifest canonical content excluding manifest_id
-> manifest_id
```

Invalid reverse dependencies include:

```text
build_id -> manifest byte hash -> manifest contains build_id
manifest file hash -> same manifest bytes contain that hash
SHA256SUMS hash -> same SHA256SUMS bytes contain that hash
child manifest -> parent final hash -> parent inventories child final hash
```

The corrected proposal must publish one complete dependency graph and prove it
acyclic mechanically.

## 6. Required Architecture Tests

Before architecture re-review:

| Test | Required result |
|---|---|
| Multi-file row IDs | Globally unique within one source snapshot |
| Local-path independence | Same source bytes/profile produce same identities |
| File-order independence | Input discovery order cannot change canonical ordering |
| Source revision | Changed bytes create a new snapshot and preserve predecessor |
| S0/S1 parity | Same profile and raw timestamp produce identical canonical time |
| Header modes | No first-row loss and no silent unexpected header |
| Manifest schemas | All six positive and negative fixture suites pass |
| Identity DAG | No cycle in manifest/artifact references |
| Release completeness | Every released file except ledger is hashed by final ledger |
| View grain | Audit V2 has exactly the certified 534 ordered row fields |
| S3-S7 propagation | `indicator_schema_ref` present and unchanged through S7 |
| Spec profile | No stale normative document or schema reference |

## 7. Decision and Next Gate

Decision:

**NOT APPROVED — TWO BLOCKERS AND REQUIRED MAJOR CORRECTIONS**

The proposal should not yet be translated into corrected specifications or
implementation. The next controlled action is to revise
`RCC-002-S8BCP-001` so that it:

1. introduces collision-free multi-file `source_row_id` V2;
2. selects timestamp units from registered archive periods;
3. defines profile-driven header handling;
4. defines scalar-to-multi-file S0 migration;
5. defines the exact artifact-set/release identity boundary;
6. incorporates the scientific review's source-fixture requirements.

After proposal revision, run focused scientific and architecture re-reviews.
Only a proposal with all blocker and major findings closed may proceed to
normative specification and schema generation.
