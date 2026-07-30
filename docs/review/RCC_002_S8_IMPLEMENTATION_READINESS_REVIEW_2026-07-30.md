# RCC-002 S8 Implementation Readiness Review

## Document Control

| Field | Value |
|---|---|
| Document class | Implementation Readiness Review |
| Project | RCC-002 Scientific Data Processing Architecture |
| Stage | `S8_EXPORT` |
| Review date | 2026-07-30 |
| Repository baseline | `a4b7c72b2e7a12bac139d1bfce8cb05200d6fd58` |
| Input package | `RCC_002_S8_IMPLEMENTATION_INPUT_2026-07-30.zip` |
| Input package SHA-256 | `5e084dcc5688ebe45173eb9d247fa5e42ab5b1c8036a529bc409c13f7b5af0ac` |
| Verdict | **NOT READY - BLOCKED BEFORE IMPLEMENTATION** |

## 1. Executive Decision

S8 implementation must not begin from the reviewed baseline.

The normative view registry and positive allowlists are complete enough to
define the six S8 view projections. Their published hashes were independently
recomputed and all matched. However, five implementation-blocking conditions
remain:

1. two pre-existing and explicitly recorded specification gaps block automatic
   `source_snapshot_id` derivation at the reproducibility identity step;
2. the current S1 time normalization has no versioned raw timestamp-unit
   profile even though the authoritative provider format changes within the
   planned 2017-to-2026 source range;
3. the current S3-to-S7 in-memory row contract omits the mandatory
   `indicator_schema_ref` field required by every S8 data view;
4. the `audit` view combines row-preserving S7 market data with S8 artifact and
   manifest self-identities in a way that has no non-circular row-grain
   interpretation;
5. the six reserved manifest schema identities do not have complete,
   machine-readable JSON Schema contracts in the reviewed repository.

The first condition was already recorded in
`rcc002/IMPLEMENTATION_BLOCKERS.md` as blocking "Roadmap Step 13
(Reproducibility identity module)". S8 is that boundary. Implementing through
the gap would therefore violate the existing fail-closed implementation
decision.

No S8 production code or tests were created by this review.

## 2. Verified Baseline

The user-supplied repository check produced:

```text
branch: main
HEAD: a4b7c72b2e7a12bac139d1bfce8cb05200d6fd58
origin/main: a4b7c72b2e7a12bac139d1bfce8cb05200d6fd58
status: ?? scripts/build_rcc002_spec_bundle.py
```

This exactly matches the handover baseline. The untracked file
`scripts/build_rcc002_spec_bundle.py` remains protected and outside S8 scope.

The input package passed `unzip -t` with no errors and contained 173 entries.

## 3. Normative Sources

The current certified specification baseline is:

| Specification | Version | SHA-256 |
|---|---:|---|
| Data Pipeline | `0.7.1` | `529f83a27c0464af0954213ffc0e81b26819bf846a1b7a6085a6b323bddf87a2` |
| Data Validation | `0.5.0` | `bceb8e0dba5e8a71dad012499165d139dbf8a450afea2d9525a0a4d5e4cc28f1` |
| Indicator | `0.4.3` | `e0f8641cc95575338adad3e2e636740d22de1349926f80d87f03f20fb8564af5` |
| Signal Transformation | `0.4.2` | `0538a660631aad1fa73a5db72bc45eba8d0c73ce2199f96b47c264be8136b4a5` |
| Regime and Gate | `0.5.1` | `26d675e26cc5a014c962ed51910f170e3369a1e39e34ca1cfec9027ce5f5eeff` |
| Label and Forward Return | `0.4.1` | `8f6c02e13378521b4ae09b08d2ad3c610a27383a2d6a589e003e4febcacceb33` |
| Reproducibility and Manifest | `0.7.2` | `3f795db4ffb9427efa73519c8390cf21bda67e82e0313b037d59b57027dca846` |

Certified bundle:

```text
docs/review/RCC_002_DVSEV001_CORRECTED_FULL_SPEC_BUNDLE_2026-07-27.md
SHA-256: 8a6ab7d732e02727199e704313c38959161c3929441fddce34b4ee4f2586d9ee
```

Certified bundle manifest:

```text
docs/review/RCC_002_DVSEV001_CORRECTED_BUNDLE_MANIFEST_2026-07-27.md
SHA-256: 176d99582ebff741d5d45b7fccc76a49b5b1d267ce350d867d4f64c17c6a8297
```

The formal certification decision grants internal certification for these
exact hashes. Stale draft-status text and stale example version values inside
individual specification prose do not supersede the certification decision
or bundle manifest and must not be copied into generated manifests.

## 4. Exact S7 Input Contract

The intended S8 input schema is:

```text
schema_id=rcc002.stage.s7-labels
schema_version=1.0.0
schema_ref=rcc002.stage.s7-labels/1.0.0
```

The certified S7 implementation supplies `S7Row`, which inherits S0-to-S6
data and adds 302 S7 fields:

```text
14 S7 metadata fields
+ 6 horizons * 48 horizon-local fields
= 302 S7 fields
```

S7's recorded identities are:

```text
label_schema_fingerprint_sha256=
075ef38aac0a5de31eefdee6881139e2f8188e8b1722f7c577e9aaa83cad643a

semantic_build_configuration_sha256=
dcad27744de8fff0f29400d7f825ba89b6a9610f1f690449cdf6575c95bfb7b1
```

### 4.1 Cross-stage contract mismatch

Mechanical expansion of the current `S7Row` representation yields 533 unique
S0-to-S7 logical fields. The normative `label-research` view requires 534.

Exact difference:

```text
missing from current S7 row contract:
indicator_schema_ref

unexpected extra fields:
none
```

The missing field is mandatory in:

- Data Pipeline 0.7.1 sections 7.4 and 7.9;
- Indicator 0.4.3 sections 8.1 and 20.5;
- every S8 positive data-view allowlist.

The current `rcc002/s3/schema.py::S3Row` contains
`indicator_schema_id` and `indicator_schema_version`, but not
`indicator_schema_ref`. Downstream S4-to-S7 rows inherit this omission.

S8 cannot silently create an S3-owned field and claim field-value
preservation. This is an upstream implementation defect requiring an explicit,
reviewed S3-to-S7 compatibility correction before S8 projection.

## 5. Exact S8 Views and Positive Allowlists

Authoritative source:

```text
RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md
Version 0.7.1
Section 7.9.3
```

The fully expanded lists in that section are authoritative. The readiness
review independently parsed those lists, resolved every field through
`RCC002_S8_FIELD_OWNERSHIP_V1/1.0.0`, rebuilt the canonical allowlist
preimages, and recomputed the hashes.

| View | Fields | S7 allowed | Published hash | Recomputed |
|---|---:|:---:|---|:---:|
| `research-features` | 232 | No | `2f2fd811b5ed8754ad8b02ee2222d885d7da3e7551ecbd5cf65fe38831c0806e` | PASS |
| `backtest-inputs` | 232 | No | `2f2fd811b5ed8754ad8b02ee2222d885d7da3e7551ecbd5cf65fe38831c0806e` | PASS |
| `paper` | 232 | No | `2f2fd811b5ed8754ad8b02ee2222d885d7da3e7551ecbd5cf65fe38831c0806e` | PASS |
| `live` | 232 | No | `2f2fd811b5ed8754ad8b02ee2222d885d7da3e7551ecbd5cf65fe38831c0806e` | PASS |
| `label-research` | 534 | Yes | `0e223d60ed4139f73194f1cb3b886a8eface9229183ad522a093e966827518cc` | PASS |
| `audit` | 564 | Yes | `3c29f3219e65ca87df199a52dc8d15b54a6ea28884a863d1479d27e8a2401b56` | PASS |

The registry has 564 unique fields and no duplicate ownership entries:

| Owner | Leakage class | Fields |
|---|---|---:|
| `S0_SOURCE` | `POINT_IN_TIME` | 5 |
| `S1_NORMALIZED` | `POINT_IN_TIME` | 8 |
| `S2_VALIDATED` | `POINT_IN_TIME` | 14 |
| `S3_INDICATORS` | `POINT_IN_TIME` | 94 |
| `S4_SIGNALS` | `POINT_IN_TIME` | 77 |
| `S5_REGIMES` | `POINT_IN_TIME` | 21 |
| `S6_GATES` | `POINT_IN_TIME` | 13 |
| `S7_LABELS` | `FUTURE_OUTCOME` | 302 |
| `S0_SOURCE` | `PROVENANCE_METADATA` | 7 |
| `S8_EXPORT` | `AUDIT_METADATA` | 23 |

The evidence-only canonical registry digest computed by this review is:

```text
74abccf596d5c4ddeeb7d4425309ce233f70e0381408a8d7a03777a556f1bc06
```

The specification does not publish that registry digest as a normative
constant, so implementation must not elevate this review-derived value without
an explicit versioned registration decision.

### 5.1 Field-order rule

The field order in each fully materialized allowlist is the output order.
Sorting fields alphabetically, preserving dataclass order, or using set order
is forbidden.

The four point-in-time views are byte-identical at the ordered-field-list
level. `label-research` is the point-in-time list followed by the exact 302
S7 fields. `audit` adds the registered S0 provenance and S8 audit metadata
fields in the normative order.

## 6. Leakage Boundary

For `research-features`, `backtest-inputs`, `paper`, and `live`:

- allowed producer stages stop at `S6_GATES`;
- no `field_owner_stage=S7_LABELS` is allowed;
- no `leakage_class=FUTURE_OUTCOME` is allowed;
- every registered S7 field must fail when injected individually;
- fields beginning with `fwd_`, `label_`, or `barrier_` must additionally fail
  prefix checks;
- prefix checks supplement ownership checks and do not replace them;
- unknown fields, owner stages, leakage classes, schema major versions, and
  allowlist hashes fail the complete view.

S7 labels may enter only `label-research` and `audit`.

## 7. Key, Order, Segment, and Row Preservation

Canonical single-provider key:

```text
(market_type, symbol, interval, open_time)
```

Unconsolidated multi-provider key:

```text
(provider, market_type, symbol, interval, open_time)
```

For every successful S8 data view:

```text
S8_rows == S7_rows
S8_key_sequence == S7_key_sequence
```

S8 must not remove, merge, duplicate, or reorder rows. Rows with
`quality_gate_pass=false` remain present. Invalid rows are represented by
their existing fail-closed values and reason codes, not excluded.

`market_segment_id`, `indicator_segment_id`, and every S7 family-local label
segment field must be preserved exactly when present in the selected view.

## 8. Reconciliation Contract

The implementable row-level truth table is:

| Condition | Expected result |
|---|---|
| One valid S7 row, exact schema and key | One output row with same key and order |
| S7 row has `quality_gate_pass=false` | Row remains; no row exclusion |
| Empty valid S7 artifact | Empty S8 artifact is row-consistent, subject to publication policy |
| Duplicate S7 primary key | Whole artifact fails |
| Missing S7 primary-key field | Whole artifact fails |
| Input key order not canonical | Whole artifact fails |
| Missing required allowlist field | Whole artifact fails |
| Extra or unknown requested view field | Whole view fails |
| Output row missing, duplicated, merged, or reordered | Reconciliation fails; no publication |
| Field value changed during projection | Reconciliation fails; no publication |
| Unknown schema, registry, compatibility profile, or hash | Whole stage fails |

For canonical S8 views:

```text
expected_rows = len(S7 rows)
exported_rows = expected_rows
excluded_rows = 0
missing_rows = 0
duplicate_rows = 0
reordered_rows = 0
```

Invalid data rows are counted as retained invalid rows, not excluded rows.

## 9. Manifest and Identity Requirements

S8 must support:

1. Source Manifest;
2. Stage Manifest;
3. Run Manifest;
4. Dataset Manifest;
5. Review Manifest;
6. Reproduction Manifest.

Reserved schema identities are all version `1.0.0`:

```text
rcc002.source-manifest
rcc002.stage-manifest
rcc002.run-manifest
rcc002.dataset-manifest
rcc002.review-manifest
rcc002.reproduction-manifest
```

Every manifest requires:

```text
manifest_schema_id
manifest_schema_version
manifest_schema_ref
manifest_type
manifest_id
created_at_utc
producer.component
producer.version
project=RCC-002
status
```

Identity construction must remain acyclic:

- `source_snapshot_id`: source content and semantic retrieval identity;
- `build_id`: logical inputs, code, semantic configuration, specification,
  schema, environment identity, and stage range;
- `artifact_id`: schema, semantic content, physical layout, bytes, rows, and
  logical coverage;
- `dataset_id`: ordered logical dataset components and semantic build state,
  excluding physical identities;
- `dataset_artifact_set_id`: dataset identity plus ordered physical artifacts
  and layout;
- `manifest_id`: hash of canonical manifest content with `manifest_id`
  removed from its own preimage;
- `run_id`: non-deterministic runtime identity excluded from deterministic
  build identity.

The `created_at_utc` field is manifest evidence and is excluded from the
deterministic build preimage.

## 10. Serialization and Fingerprints

Manifest JSON must use `RCC_JSON_CANONICALIZATION_V1`:

- RFC 8785/JCS;
- UTF-8 without BOM;
- Unicode NFC;
- JCS object-key ordering;
- preserved schema-defined array order;
- no non-finite numbers;
- UTC timestamps ending in `Z`;
- domain decimals encoded as canonical decimal strings;
- LF for textual persistence.

Large canonical table artifacts should use Parquet. CSV is restricted to
small extracts, diagnostics, legacy compatibility, and external comparisons.

Table semantic fingerprints must include:

- exact field order;
- logical types and nullability;
- complete canonical key;
- canonical row order;
- row count;
- canonical value and null representation;
- schema version.

Physical partitioning, compression, writer metadata, row groups, and file
boundaries must not enter `semantic_sha256`.

## 11. Configuration Boundary

`semantic_build_configuration` includes every setting capable of changing
logical values, rows, keys, validity, reason codes, segments, states, labels,
schemas, allowlists, leakage classes, numeric behavior, or identities.

`physical_publication_configuration` includes only approved storage,
partition, container, compression, row-group, writer, and retention settings.

A key in both classes, in neither class, or in the wrong class is a
stage-wide failure.

Semantic configuration changes must change `build_id` and `dataset_id` even
when output values happen to remain equal. Purely physical changes must
preserve both and change physical artifact identities.

## 12. Blocking Findings

### S8-RR-B01 - Source Snapshot identity is normatively underdefined

Severity: **BLOCKER**

`rcc002/IMPLEMENTATION_BLOCKERS.md` already records two open gaps that
explicitly block the reproducibility identity module:

1. no versioned provider/source-format registry defines the canonical
   semantic retrieval parameters required by the `source_snapshot_id`
   preimage;
2. the required actual source coverage period is said to be derived from S0
   source bytes, while the architecture first defines timestamp columns at S1
   and specifies no S0 extraction rule.

Required resolution:

- adopt a reviewed registry of semantic retrieval parameters; and
- choose and normatively approve either an S0 pre-canonical coverage parser or
  an S1-derived normalized coverage term.

Automatic `source_snapshot_id` computation must not be implemented until both
decisions are certified.

### S8-RR-B05 - Provider timestamp-unit transition is not normalized

Severity: **BLOCKER**

The official Binance public-data documentation states that Spot timestamps
from 2025-01-01 onward are expressed in microseconds. The planned source
dataset spans 2017 through 2026.

The current `rcc002/s1/normalize.py` parses raw `open_time` and
`close_time` integers and passes them unchanged to fields documented and used
as milliseconds. The current `rcc002/s1/time.py` then applies a millisecond
1-minute duration contract.

Without an explicit provider/source-format timestamp-unit profile and exact
conversion rule, post-2024 rows cannot enter the same canonical millisecond
timeline as earlier rows. Magnitude guessing or silent rounding would violate
the fail-closed and reproducibility contracts.

Required resolution:

- register the provider/source-format timestamp-unit transition;
- define exact millisecond and microsecond conversion rules;
- use one pure conversion contract for S0 coverage scanning and S1
  normalization;
- add boundary, remainder, parity, and mixed-period Golden Fixtures.

### S8-RR-B02 - Mandatory `indicator_schema_ref` is absent upstream

Severity: **BLOCKER**

The normative S3 contract and all six S8 view schemas require
`indicator_schema_ref`. The current S3-to-S7 row model omits it.

Required resolution:

- add the exact deterministic field to the S3 row contract between
  `indicator_schema_version` and `indicator_segment_id`;
- propagate it unchanged through S4, S5, S6, and S7;
- update all affected constructors, fixtures, schema fingerprints, and tests;
- run S3, S4, S5, S6, S7, all RCC-002, and regression suites;
- perform a targeted independent review and certification of the correction
  before using the corrected S7 schema as S8 input.

S8 must not synthesize the missing S3-owned field as an undocumented
workaround.

### S8-RR-B03 - Audit view grain and identity are circular or ambiguous

Severity: **BLOCKER**

The `audit` allowlist is a 564-field row schema containing:

- the 534 S0-to-S7 market and label fields;
- seven S0 source-file provenance fields;
- 23 S8 artifact/manifest metadata fields, including `manifest_id`,
  `artifact_id`, `byte_sha256`, `semantic_sha256`, and
  `physical_layout_sha256`.

At the same time, section 8.7.1 requires every S8 view artifact to preserve
every S7 row and its order.

No reviewed rule defines:

- whether the S8 identity fields describe the audit artifact itself or another
  artifact;
- how a self-describing audit artifact avoids hashing bytes that contain its
  own `artifact_id` and byte/semantic hashes;
- how one S7 market row maps to one source-file provenance record when a
  source snapshot contains multiple files;
- whether the audit view is a market-row view or an artifact-inventory view.

Required resolution:

- define the audit view grain and foreign-key semantics;
- define which artifact or manifest each S8 metadata field identifies;
- remove self-reference or define a formally acyclic preimage/exclusion rule;
- define source-file-to-row provenance cardinality;
- update the audit schema/allowlist/hash if the resolved field contract
  changes.

### S8-RR-B04 - Machine-readable manifest schemas are absent

Severity: **BLOCKER**

The specification reserves six schema identities and states that every
manifest type must be validated by versioned JSON Schema. The reviewed
repository contains no released machine-readable JSON Schema documents for
those six identities. Common fields and selected type-specific examples are
documented, but exact `required`, type, nullability, enum, conditional, and
`additionalProperties` contracts are not fully materialized for all six
manifest types.

Required resolution:

- materialize versioned JSON Schema documents for all six manifest types;
- define exact required fields and conditional requirements per type;
- register immutable schema fingerprints and references;
- add positive and negative Golden Fixtures;
- review and certify the resulting contracts before S8 publication code
  relies on them.

## 13. Non-blocking Observations

### S8-RR-O01 - Stale example versions

Reproducibility section 24 contains older specification versions in its
example Dataset Manifest. Generated manifests must use the certified
DVSEV-001 version matrix from the certification decision and bundle manifest.

### S8-RR-O02 - Review-status prose is historically stale

Individual specification headers retain historical pending-review text.
The exact certified bundle hashes and formal certification decision govern
the implementation baseline.

### S8-RR-O03 - Registry digest is not published as a constant

The review can deterministically recompute the field-registry digest, but the
normative documents do not register its value. If the implementation embeds a
registry hash, that value needs a versioned registration record.

## 14. Planned Module Boundary After Blocker Closure

The following module split is recommended only after the five blockers are
closed:

```text
rcc002/s8/
  __init__.py
  canonical.py
  constants.py
  identities.py
  manifests.py
  reconciliation.py
  schema.py
  views.py
  publication.py
```

Primary responsibilities:

- `canonical.py`: JCS/RCC preprocessing and deterministic hashing;
- `constants.py`: certified schema, registry, allowlist, profile, and
  component identities;
- `identities.py`: acyclic ID preimages and validators;
- `manifests.py`: six manifest schemas, builders, and fail-closed validation;
- `reconciliation.py`: row, key, order, field, segment, count, and hash
  reconciliation;
- `schema.py`: immutable view/artifact/report objects;
- `views.py`: exact positive projections and leakage rejection;
- `publication.py`: temporary, quarantine, candidate, and atomic publication
  states.

No S0-to-S7 scientific calculation belongs in S8.

## 15. Required Test Matrix After Blocker Closure

At minimum:

1. exact 232/534/564-field order tests;
2. independent recomputation of all three published allowlist hashes;
3. unique field-owner and leakage resolution for every view field;
4. all 302 S7 fields individually rejected from each non-label view;
5. unknown field, owner, leakage class, schema, and major-version rejection;
6. prefix leakage tests for `fwd_`, `label_`, and `barrier_`;
7. `S8_rows == S7_rows`;
8. exact key-sequence and row-order preservation;
9. invalid-row retention;
10. missing, duplicate, merged, and reordered row detection;
11. exact field-value preservation;
12. independent semantic fingerprint oracle;
13. JCS/NFC/decimal/timestamp/non-finite Golden Fixtures;
14. independent identity preimage and hash oracles;
15. deterministic repeat tests;
16. semantic-versus-physical configuration identity tests;
17. all six manifest JSON Schema positive and negative fixtures;
18. secret and absolute-path rejection;
19. manifest self-ID acyclicity;
20. missing parent and lineage-cycle rejection;
21. artifact inventory and hash reconciliation;
22. partitioned-versus-unpartitioned semantic parity;
23. mutable-container isolation;
24. failed/quarantined build cannot publish;
25. no silent overwrite and atomic publication tests;
26. full S8, RCC-002, and regression suites.

## 16. Required Correction Sequence

The scientifically safe sequence is:

1. create one focused specification correction proposal covering
   S8-RR-B01, S8-RR-B05, S8-RR-B03, and S8-RR-B04;
2. run focused scientific and architecture reviews;
3. certify the corrected specification bundle;
4. implement and test the S3 `indicator_schema_ref` correction;
5. independently review and certify the affected S3-to-S7 compatibility
   correction;
6. regenerate the S8 implementation input package from the new certified
   HEAD;
7. repeat the S8 readiness review;
8. implement S8 only if the repeated review returns READY.

## 17. Final Verdict

```text
S8 IMPLEMENTATION READINESS: NOT READY
IMPLEMENTATION AUTHORIZATION: DENIED UNTIL BLOCKER CLOSURE
CRITICAL: 0
BLOCKER: 5
MAJOR: 0
MINOR: 0
OBSERVATION: 3
```

This verdict does not invalidate the certified S0-to-S7 scientific
calculations. It identifies one cross-stage schema omission, one source-time
normalization gap, and three reproducibility/export contract gaps that become
blocking at the S8 and full-build boundary.
