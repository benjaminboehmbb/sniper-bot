# RCC-002 S8 Blocker Correction Proposal

## Document Control

| Field | Value |
|---|---|
| Document class | Focused normative correction proposal |
| Project | RCC-002 Scientific Data Processing Architecture |
| Proposal ID | `RCC-002-S8BCP-001` |
| Proposal revision | `2` |
| Date | 2026-07-30 |
| Baseline commit | `a4b7c72b2e7a12bac139d1bfce8cb05200d6fd58` |
| Baseline bundle | `RCC_002_DVSEV001_CORRECTED_FULL_SPEC_BUNDLE_2026-07-27.md` |
| Baseline bundle SHA-256 | `8a6ab7d732e02727199e704313c38959161c3929441fddce34b4ee4f2586d9ee` |
| Trigger | `RCC_002_S8_IMPLEMENTATION_READINESS_REVIEW_2026-07-30.md` |
| Revision inputs | `RCC-002-S8BCP001-SCR-001`; `RCC-002-S8BCP001-AIR-001` |
| Supersedes | `RCC-002-S8BCP-001`, revision 1 |
| Proposal status | **REVISED - FOCUSED RE-REVIEW REQUIRED - NOT YET NORMATIVE** |

## 1. Purpose

This proposal defines one focused correction cycle required before
`S8_EXPORT` implementation can begin.

It resolves:

1. the two pre-existing `source_snapshot_id` blockers recorded in
   `rcc002/IMPLEMENTATION_BLOCKERS.md`;
2. the Binance Spot timestamp-unit transition that the current S1
   implementation cannot normalize;
3. the missing upstream `indicator_schema_ref` implementation field;
4. the circular and ambiguous `rcc002.view.audit/1.0.0` contract;
5. the absence of released machine-readable JSON Schemas for the six
   manifest types.

Revision 2 additionally resolves all findings from the first scientific and
architecture reviews:

- timestamp units are selected from a registered archive-period descriptor
  before any row timestamp is interpreted;
- provider-format claims require immutable byte-bound Golden evidence;
- multi-file snapshots use collision-free `source_row_id` V2;
- S0 per-file and aggregate provenance ownership is explicit;
- header behavior is profile-driven;
- dataset-artifact-set identity is separated from release-control files by
  an exact acyclic release-class model.

No correction in this proposal changes indicator formulas, signal formulas,
regime logic, gate logic, forward-return formulas, label logic, barrier
logic, or trading strategy.

## 2. Evidence

### 2.1 Certified internal evidence

The readiness review mechanically confirmed:

- all three published S8 positive allowlist hashes are reproducible;
- `S7Row` materializes 533 of the 534 fields required by
  `label-research`;
- the sole missing field is `indicator_schema_ref`;
- the 564-field audit allowlist mixes S7 market-row data, source-file
  provenance, and S8 self-identities;
- no released JSON Schema files for the six reserved manifest schema
  identities are present;
- `rcc002/IMPLEMENTATION_BLOCKERS.md` explicitly defers two
  `source_snapshot_id` questions to the reproducibility identity step.

### 2.2 Provider evidence

The official Binance public-data documentation states:

- public market data is distributed as daily or monthly archives;
- each ZIP has an accompanying checksum;
- Spot kline files use a fixed 12-column order;
- Spot timestamps from 2025-01-01 onward are expressed in microseconds.

Primary source:

```text
https://github.com/binance/binance-public-data
```

The current `rcc002/s1/normalize.py` parses raw `open_time` and `close_time`
integers and passes them through unchanged as milliseconds. Therefore a
mixed 2017-to-2026 Binance Spot dataset cannot satisfy one canonical
millisecond time contract without a registered unit-normalization rule.

The provider overview is sufficient evidence for the existence of the unit
transition and the broad archive structure. It is not treated as complete
evidence for header mode, member count, checksum-file grammar, timestamp
remainders, or every archive family. Those invariants become acceptable only
through the byte-bound Golden evidence required in section 4.5.

## 3. Correction Summary

| ID | Correction | Class |
|---|---|---|
| `S8BCP-C01` | Versioned source-retrieval and source-format registry | Normative |
| `S8BCP-C02` | Deterministic S0 coverage scan and source snapshot preimage | Normative |
| `S8BCP-C03` | Explicit millisecond/microsecond S1 normalization | Normative and implementation |
| `S8BCP-C04` | Restore mandatory `indicator_schema_ref` in S3-to-S7 rows | Implementation conformance |
| `S8BCP-C05` | Replace circular Audit View V1 with row-safe Audit View V2 | Normative |
| `S8BCP-C06` | Release six strict machine-readable manifest JSON Schemas | Normative |
| `S8BCP-C07` | Define non-self-referential manifest and checksum recording | Normative |
| `S8BCP-C08` | Introduce collision-free multi-file `source_row_id` V2 | Normative and implementation |

## 4. S8BCP-C01 - Source Retrieval Registry

### 4.1 New registry

Introduce:

```text
registry_id=RCC002_SOURCE_RETRIEVAL_REGISTRY_V1
registry_version=1.0.0
```

Every source snapshot must reference exactly one registered retrieval
profile. Unknown profiles, versions, providers, source formats, dataset
families, timestamp units, or effective-date rules fail the full S0
artifact.

### 4.2 Initial registered profile

The first profile is:

```text
source_retrieval_profile_id=RCC002_BINANCE_VISION_SPOT_KLINES_V1
source_retrieval_profile_version=1.0.0
provider=BINANCE_VISION
market_type=spot
dataset_kind=klines
source_container=zip_with_single_csv_member
column_profile_id=BINANCE_SPOT_KLINE_12_COLUMN_V1
header_mode=ABSENT
checksum_profile=PROVIDER_SHA256_CHECKSUM_REQUIRED
archive_period_profile_id=BINANCE_VISION_KLINE_ARCHIVE_PERIOD_V1
```

Canonical 12-column order:

```text
0  open_time
1  open
2  high
3  low
4  close
5  volume
6  close_time
7  quote_asset_volume
8  number_of_trades
9  taker_buy_base_asset_volume
10 taker_buy_quote_asset_volume
11 ignore
```

The source profile is a structural and identity contract. It does not make
columns 7-to-11 canonical S1 fields.

### 4.3 Exact semantic retrieval parameters

For V1 the only registered semantic retrieval keys are:

```text
provider
market_type
dataset_kind
symbol
interval
column_profile_id
timestamp_unit_profile_id
source_revision
```

`source_revision` is present with an explicit JSON `null` when the provider
publishes no revision identifier. A documented synthetic revision record may
be used for a later provider byte revision only under a versioned revision
profile; it must never reuse the prior revision identity.

The normalized source-file list, file byte hashes, provider checksums,
provider-relative archive names, and actual byte-derived coverage are
separate mandatory preimage fields.

Daily versus monthly archive packaging is represented by each registered
archive-period descriptor and by the exact file list and hashes. It is not a
free-form caller parameter.

No unregistered parameter may enter the source snapshot preimage. No
registered semantic parameter may be omitted.

### 4.4 Archive-period descriptor and header modes

Before timestamp bytes are interpreted, S0 must parse each
`provider_relative_name` against the registered
`BINANCE_VISION_KLINE_ARCHIVE_PERIOD_V1` grammar and produce:

```text
archive_family=DAILY|MONTHLY
period_token=<canonical provider token>
period_start_utc=<inclusive UTC boundary>
period_end_utc=<exclusive UTC boundary>
```

The descriptor is derived only from the normalized provider-relative archive
name and the registered grammar. It is not derived from:

- raw timestamp magnitude;
- normalized row coverage;
- requested dates;
- local path;
- retrieval time;
- archive discovery order.

An unparseable or ambiguous provider-relative name fails the complete source
snapshot candidate.

Header handling is owned by the retrieval profile. The registry reserves:

```text
ABSENT
PRESENT_EXACT
```

For `ABSENT`, the first non-empty CSV record is data. A header-like record is
a structural failure. For `PRESENT_EXACT`, the first non-empty record must
byte-match the registered canonical header after the explicitly registered
line-ending normalization and is excluded from the data-record count. No
caller or parser may infer a header mode from record contents.

### 4.5 Required byte-bound provider evidence

The initial Binance profile remains `candidate` until immutable evidence
records exist for:

- at least one pre-transition daily archive;
- the last registered pre-transition daily archive;
- the first registered post-transition daily archive;
- at least one post-transition daily archive;
- at least one applicable pre-transition monthly archive;
- at least one applicable post-transition monthly archive.

Every evidence record must contain:

```text
provider_relative_name
archive_family
period_start_utc
period_end_utc
provider_checksum_text_sha256
provider_checksum_sha256
archive_byte_sha256
archive_size_bytes
csv_member_name
csv_member_count
record_count
first_record_utf8
last_record_utf8
observed_column_count
observed_header_mode
selected_timestamp_unit
first_raw_open_time
first_raw_close_time
last_raw_open_time
last_raw_close_time
```

Full archive bytes need not be committed to the repository, but their
provider-relative identity, checksums, extraction evidence, and compact
lineage-preserving fixtures must be. Positive and negative Golden fixtures
must cover the registered member count, header mode, column count, delimiter,
checksum grammar, unit branch, and timestamp remainders.

Any verified official archive that contradicts the profile blocks profile
release. The contradiction must be resolved by a new profile version or by
rejecting the proposed invariant; it may not be waived per run.

## 5. S8BCP-C02 - Deterministic S0 Coverage Scan

### 5.1 Architectural decision

Adopt the former Blocker 2 Option A in a restricted form:

S0 may perform a structural coverage scan over the registered timestamp
columns solely to construct and verify source identity. This scan:

- does not create an S0 market-row schema;
- does not normalize OHLCV values;
- does not emit canonical S1 rows;
- does not detect or repair gaps;
- does not sort or deduplicate data;
- must inspect every non-empty CSV record in every registered archive;
- fails the source artifact on any structurally invalid record.

This is consistent with S0's existing archive-open, header, row-count, and
checksum duties while preserving S1 ownership of canonical rows.

### 5.2 Header rule

`BINANCE_SPOT_KLINE_12_COLUMN_V1` has:

```text
header_mode=ABSENT
```

The first non-empty record is data and must never be discarded as a header.
Any alphabetic header-like record fails this exact profile instead of being
silently accepted.

Other provider or source-format profiles may register a different header
mode only under a different versioned profile.

The generic Data Validation rule that every file has a present header is
replaced by the registered `header_mode` contract from section 4.4. S0
validates that mode. S1 consumes the resolved mode and must not infer or
override it. Row counts, truncation checks, and extraction reports must all
use the same resolved header mode.

### 5.3 S0 per-file and aggregate ownership

S0 remains one immutable verified artifact per physical provider archive.
Each per-file S0 record owns exactly one archive's:

```text
provider_relative_name
archive_byte_sha256
provider_checksum_sha256
archive_size_bytes
csv_member_name
source_file_ordinal
archive_period_descriptor
selected_timestamp_unit
record_count
min_open_time_utc_ms
max_close_time_utc_ms
integrity_status
```

The Source Manifest is the aggregate owner of one ordered `source_files`
array and the resulting `source_snapshot_id`. It references every per-file S0
artifact and must reconcile their byte identities, coverage, counts, and
ordinals exactly.

The current scalar `source_file_name` and `source_byte_sha256` representation
is valid only for legacy one-file source snapshots. The corrected contracts
must:

- version the affected S0/Source-Manifest schema boundary;
- migrate a legacy one-file snapshot to a one-element `source_files` array
  without changing its stored historical identity;
- prohibit a lossy first-file projection for new multi-file snapshots;
- prohibit one aggregate S0 record from hiding individual archive identities.

### 5.4 Coverage result

After timestamp-unit normalization, S0 computes:

```text
actual_coverage_min_open_time_utc_ms
actual_coverage_max_close_time_utc_ms
source_record_count
```

The minimum and maximum are derived from all source records, not inferred
from filenames, requested dates, expected dates, or archive cadence.

Each file's normalized coverage must be reconciled against its registered
archive-period descriptor. Coverage may be narrower because the provider has
no records for part of the logical period only when a documented provider
exception exists. Coverage outside the registered period is always fatal.

### 5.5 Exact source snapshot preimage

The V1 preimage is:

```json
{
  "identity_profile_id": "RCC002_SOURCE_SNAPSHOT_ID_V1",
  "source_retrieval_profile_id": "RCC002_BINANCE_VISION_SPOT_KLINES_V1",
  "source_retrieval_profile_version": "1.0.0",
  "provider": "BINANCE_VISION",
  "market_type": "spot",
  "dataset_kind": "klines",
  "symbol": "<canonical symbol>",
  "interval": "<registered interval>",
  "column_profile_id": "BINANCE_SPOT_KLINE_12_COLUMN_V1",
  "timestamp_unit_profile_id": "BINANCE_SPOT_TIMESTAMP_UNITS_V1",
  "source_revision": "<provider revision or null>",
  "source_files": [
    {
      "provider_relative_name": "<portable archive name>",
      "byte_sha256": "<64 lowercase hex>",
      "provider_checksum_sha256": "<64 lowercase hex>",
      "size_bytes": 0,
      "csv_member_name": "<portable member name>",
      "source_file_ordinal": 0,
      "archive_period": {
        "archive_family": "DAILY|MONTHLY",
        "period_token": "<canonical provider token>",
        "period_start_utc": "<inclusive UTC Z timestamp>",
        "period_end_utc": "<exclusive UTC Z timestamp>"
      },
      "record_count": 0,
      "min_open_time_utc_ms": 0,
      "max_close_time_utc_ms": 0,
      "timestamp_unit": "MILLISECOND|MICROSECOND"
    }
  ],
  "actual_coverage": {
    "min_open_time_utc_ms": 0,
    "max_close_time_utc_ms": 0,
    "record_count": 0
  }
}
```

`source_files` is ordered by normalized `provider_relative_name`, then assigned
zero-based `source_file_ordinal` values in that exact order. Local discovery
order cannot influence the array or the ordinals.

Within one source snapshot candidate, duplicate names, duplicate logical
periods with different bytes, path traversal, absolute paths, missing provider
checksums, and unexplained coverage overlap fail closed.

A provider revision with changed bytes is permitted only as a new
`source_snapshot_id`. It must reference the preserved prior snapshot through
`supersedes` and must carry either the provider revision or a registered
synthetic revision record with reason and evidence. It cannot replace bytes
inside an existing snapshot.

The preimage is normalized with `RCC_JSON_CANONICALIZATION_V1` and hashed:

```text
source_snapshot_id=source:sha256:<digest>
```

### 5.6 Explicit exclusions

The source snapshot preimage must not contain:

- retrieval time;
- local path;
- cache path;
- hostname;
- username;
- transport retries;
- temporary extraction path;
- `expected_start`;
- `expected_end`;
- build timezone.

The final three remain exclusively in
`semantic_build_configuration.source_expectations`.

## 6. S8BCP-C03 - Timestamp Unit Normalization

### 6.1 Registered unit profile

Introduce:

```text
timestamp_unit_profile_id=BINANCE_SPOT_TIMESTAMP_UNITS_V1
timestamp_unit_profile_version=1.0.0
```

Rules:

| Registered archive period | Raw unit |
|---|---|
| `period_end_utc <= 2025-01-01T00:00:00Z` | `MILLISECOND` |
| `period_start_utc >= 2025-01-01T00:00:00Z` | `MICROSECOND` |

The branch is selected from the registered archive-period descriptor before
any row timestamp is interpreted. A source archive whose registered period
crosses the effective boundary, or whose rows contradict the selected raw-unit
rule, is rejected.

The dependency order is normative:

```text
provider-relative archive name
-> registered archive-period descriptor
-> timestamp-unit branch
-> exact row conversion
-> byte-derived normalized coverage
-> period/coverage reconciliation
```

Raw timestamp magnitude, per-record automatic detection, requested dates, and
already-normalized coverage are prohibited unit-selection inputs.

The rule is provider-profile specific and must not be generalized to futures
or another provider.

### 6.2 Conversion to canonical milliseconds

For `MILLISECOND`:

```text
open_time_ms = raw_open_time
close_time_ms = raw_close_time
```

For `MICROSECOND`:

```text
raw_open_time % 1000 == 0
open_time_ms = raw_open_time // 1000

raw_close_time % 1000 == 999
close_time_ms = raw_close_time // 1000
```

Any remainder mismatch is a structural timestamp-profile failure. No
round-to-nearest, floating-point conversion, magnitude guessing, or
per-record automatic unit detection is allowed.

S0 coverage scanning and S1 row normalization must use the same pure
conversion function and the same already-resolved versioned unit profile.

### 6.3 Post-conversion invariants and stage ownership

For every accepted one-minute Binance Spot kline:

```text
open_time_ms % 60000 == 0
close_time_ms == open_time_ms + 59999
close_time_ms - open_time_ms == 59999
```

Ownership is:

- S0 parses the registered archive period, resolves the unit branch, verifies
  provider-profile timestamp structure, and computes identity coverage;
- S1 applies the same pure conversion while materializing canonical rows;
- S2 owns canonical interval alignment, temporal quality findings, gap
  detection, and segment consequences.

S0 structural verification does not authorize S0 to sort, deduplicate, repair,
or emit canonical market rows. S1 conversion does not remove S2's independent
quality-gate responsibility.

### 6.4 Required tests

Tests must include:

- registered daily and monthly period parsing;
- last registered millisecond archive before the transition;
- first registered microsecond archive after the transition;
- exact open-time and close-time conversion;
- wrong open-time remainder;
- wrong close-time remainder;
- archive crossing the transition;
- unit/profile mismatch;
- timestamp magnitude inconsistent with the preselected unit;
- S0/S1 conversion parity;
- post-conversion 1-minute alignment and close-time convention.

## 7. S8BCP-C08 - Collision-free Multi-file `source_row_id` V2

### 7.1 New canonicalization profile

The current implementation profile is retained only for historical one-file
artifacts:

```text
RCC002_S1_SOURCE_ROW_ID_V1
```

All new builds use:

```text
source_row_id_profile_id=RCC002_S1_SOURCE_ROW_ID_V2
source_row_id_profile_version=2.0.0
```

Its exact semantic preimage tuple is:

```text
source_snapshot_id
source_file_ordinal
original_record_index
```

`source_file_ordinal` is the zero-based ordinal from the canonical ordered
`source_files` array in section 5.5. `original_record_index` is the zero-based
data-record position within the original CSV member after applying the
registered header mode, before sorting, filtering, or deduplication.

### 7.2 Exact UTF-8 encoding

The output encoding is:

```text
RCC002_S1_SOURCE_ROW_ID_V2:
<source_snapshot_id>:
<source_file_ordinal as 8 decimal digits>:
<original_record_index as 20 decimal digits>
```

Both integer components are non-negative. Overflow beyond the registered
width is fatal; values are never truncated. Provider-relative names and local
paths are not embedded in the ID.

Example:

```text
RCC002_S1_SOURCE_ROW_ID_V2:source:sha256:<digest>:00000003:00000000000000000427
```

The profile ID and version must be recorded in Source and S1 Stage Manifests.
Every S1 row must be traceable to exactly one per-file S0 artifact and original
CSV data record.

### 7.3 Required tests

- same snapshot, file ordinal, and record index produce the same ID;
- different file ordinals with the same record index produce different IDs;
- local file discovery order does not change canonical ordinals or IDs;
- changing the canonical source-file list changes the snapshot and descendant
  row IDs;
- negative or width-overflowing integers fail;
- headerless record zero is retained as record index zero;
- all S1 IDs are unique within a multi-file source snapshot;
- S2 duplicate, anomaly, gap, and lineage maps remain collision-free;
- historical V1 identities are read-only and never silently rewritten.

## 8. S8BCP-C04 - `indicator_schema_ref` Conformance Repair

This is an implementation correction against an already unambiguous
normative contract. No Indicator Specification semantic change is required.

Required implementation:

1. Add `indicator_schema_ref` to `S3Row` immediately after
   `indicator_schema_version`.
2. Require the exact value:

```text
rcc002.stage.s3-indicators/1.0.0
```

3. Populate it in S3.
4. Preserve it unchanged through S4, S5, S6, and S7.
5. Include it in every physical schema expansion and fingerprint.
6. Update S3-to-S7 fixtures and constructor helpers.
7. Run targeted and complete regression suites.

The logical S3 schema remains `1.0.0` because the normative schema already
contained the field. The implementation had failed to materialize it.

Downstream component versions must receive patch increments because their
pass-through implementation changes without changing scientific semantics:

| Component | Current | Proposed |
|---|---:|---:|
| S4 signal transformer | `0.3.0` | `0.3.1` |
| S5 regime classifier | `0.4.0` | `0.4.1` |
| S6 gate evaluator | `0.4.0` | `0.4.1` |
| S7 label builder | `0.3.0` | `0.3.1` |

S7's implementation schema fingerprint and semantic build configuration
hash must be recomputed and recorded. Existing label values must remain
bitwise unchanged.

## 9. S8BCP-C05 - Audit View V2

### 9.1 Problem

`rcc002.view.audit/1.0.0` combines:

- 534 row-grain S0-to-S7 fields;
- seven source-file-grain provenance fields;
- 23 artifact/manifest-grain S8 fields, including self-identities and
  hashes.

This conflicts with row preservation and produces ambiguous or circular
identity semantics.

### 9.2 Replacement contract

Deprecate V1 before any implementation or publication:

```text
schema_id=rcc002.view.audit
schema_version=1.0.0
publication_status=withdrawn_before_first_release
```

Register:

```text
schema_id=rcc002.view.audit
schema_version=2.0.0
schema_ref=rcc002.view.audit/2.0.0
s7_fields_allowed=true
```

Audit View V2 is a row-preserving data view. Its ordered fields are exactly
the 534 ordered fields of:

```text
rcc002.view.label-research/1.0.0
```

Its allowed producer stages are exactly:

```text
S0_SOURCE
S1_NORMALIZED
S2_VALIDATED
S3_INDICATORS
S4_SIGNALS
S5_REGIMES
S6_GATES
S7_LABELS
```

Because the allowlist hash preimage excludes `schema_id`,
`schema_version`, and `schema_ref`, Audit View V2 has:

```text
allowlist_sha256=
0e223d60ed4139f73194f1cb3b886a8eface9229183ad522a093e966827518cc
```

This value must be mechanically regenerated during the correction cycle,
not copied without verification.

### 9.3 Provenance and S8 metadata placement

The seven `PROVENANCE_METADATA` fields remain only in Source Manifests and
lineage records keyed by `source_snapshot_id`.

The 23 `AUDIT_METADATA` fields remain only in:

- artifact inventory records;
- Stage, Run, Dataset, Review, and Reproduction Manifests;
- generated human-readable audit reports.

They are not repeated as market-row columns.

### 9.4 Human-readable audit report

The Release Audit Report is generated from validated manifests and
reconciliation records. It is not a seventh row data view and is not subject
to S7 row preservation.

## 10. S8BCP-C06 - Machine-readable Manifest Schemas

### 10.1 Standard and location

Release immutable JSON Schema Draft 2020-12 documents:

```text
schemas/rcc002/manifests/source-manifest/1.0.0.schema.json
schemas/rcc002/manifests/stage-manifest/1.0.0.schema.json
schemas/rcc002/manifests/run-manifest/1.0.0.schema.json
schemas/rcc002/manifests/dataset-manifest/1.0.0.schema.json
schemas/rcc002/manifests/review-manifest/1.0.0.schema.json
schemas/rcc002/manifests/reproduction-manifest/1.0.0.schema.json
```

Each schema must contain:

```text
$schema=https://json-schema.org/draft/2020-12/schema
$id=urn:rcc002:schema:<manifest-type>:1.0.0
title
type=object
required
properties
additionalProperties=false
```

The RCC `manifest_schema_ref` remains the registered project reference such
as `rcc002.source-manifest/1.0.0`; it is not replaced by `$id`.

### 10.2 Common strict rules

All six schemas must enforce:

- exact manifest type and schema identity constants;
- `project="RCC-002"`;
- lowercase 64-hex digest patterns;
- prefixed deterministic-ID patterns;
- UTC `Z` timestamps;
- non-empty portable strings;
- no absolute paths;
- no `..` path traversal;
- registered status enums;
- explicit nullability;
- closed nested objects wherever the contract is complete;
- no secret-like field names or values.

### 10.3 Type-specific minimum contracts

Source Manifest:

- common fields;
- exact canonical S0 provenance;
- retrieval, column, timestamp-unit, and identity profiles;
- ordered source-file records;
- coverage reconciliation;
- source snapshot preimage hash evidence.

Stage Manifest:

- common fields;
- stage/component identity;
- build/run IDs;
- exact input/output schema triples and fingerprints;
- ordered parents and outputs;
- semantic and physical configuration references;
- row/key/order/segment/validity reconciliation;
- validation, warning, failure, and publication state.

Run Manifest:

- common fields;
- run/build IDs;
- start/end timestamps;
- code provenance;
- full environment evidence;
- effective execution parameters;
- validation and publication outcome.

Dataset Manifest:

- common fields;
- dataset and artifact-set IDs;
- build and publication run IDs;
- source snapshots;
- ordered `DATA_ARTIFACT` inventory in `artifacts`;
- ordered `SCHEMA_ARTIFACT` inventory in `schema_artifacts`;
- ordered pre-Dataset child manifests in `child_manifests`;
- stages, registries, and views;
- semantic/physical configurations;
- code/environment/specification profiles;
- quality, lineage, candidate publication state, and review requirements;
- no final review-artifact identity and no self-inventory.

Review Manifest:

- common fields;
- exact review record fields from section 21.1;
- reviewed artifact identities and hashes;
- findings, resolutions, reviewer system, dates, and status;
- no successful Claude or Gemini state without an attached real review
  artifact.

Reproduction Manifest:

- common fields;
- source and target run/build identities;
- environment differences;
- byte, semantic, tolerance, and classification comparisons;
- E0-to-E3 equality result;
- deviations and final status.

### 10.4 Golden Fixtures

Each schema requires:

- one minimal valid fixture;
- one complete valid fixture;
- missing-field negative fixtures;
- wrong type/nullability fixtures;
- extra-property fixture;
- invalid ID and timestamp fixtures;
- absolute/path-traversal fixtures;
- secret-leakage fixtures;
- wrong schema identity and version fixtures.

The canonical schema bytes and SHA-256 are registered in the corrected
bundle manifest.

## 11. S8BCP-C07 - Non-self-referential Manifest Recording

### 11.1 Manifest self-ID

`manifest_id` remains computed from the canonical manifest with its own
`manifest_id` field removed.

### 11.2 Prohibited self-fields

A manifest must not contain its own:

- final file `byte_sha256`;
- final file `artifact_id`;
- final file `size_bytes`;
- physical layout identity.

Those values can only be computed after final serialization.

### 11.3 Release classes and identity boundary

Every released file has exactly one class:

| Release class | Meaning | Enters `dataset_artifact_set_id` | Dataset Manifest placement |
|---|---|:---:|---|
| `DATA_ARTIFACT` | Published S8 data/view files | Yes | `artifacts` |
| `SCHEMA_ARTIFACT` | Schemas, registries, allowlists, and immutable support contracts | No | `schema_artifacts` |
| `CONTROL_MANIFEST` | Source, Stage, Run, Dataset, and Reproduction Manifests | No | Pre-Dataset children only in `child_manifests`; never self or a post-Dataset control |
| `REVIEW_ARTIFACT` | Review Manifests and human review/certification records | No | Not referenced by Dataset Manifest |
| `RELEASE_LEDGER` | Final `SHA256SUMS` | No | Not referenced by Dataset Manifest |

The exact `dataset_artifact_set_id` preimage is:

```json
{
  "identity_profile_id": "RCC002_DATASET_ARTIFACT_SET_ID_V1",
  "dataset_id": "dataset:sha256:<digest>",
  "physical_publication_configuration_sha256": "<64 lowercase hex>",
  "data_artifacts": [
    {
      "logical_name": "<registered name>",
      "relative_path": "<portable path>",
      "artifact_id": "artifact:sha256:<digest>",
      "byte_sha256": "<64 lowercase hex>",
      "semantic_sha256": "<64 lowercase hex>",
      "physical_layout_sha256": "<64 lowercase hex>",
      "size_bytes": 0,
      "schema_ref": "<schema_id>/<schema_version>",
      "schema_fingerprint_sha256": "<64 lowercase hex>",
      "view_allowlist_sha256": "<64 lowercase hex or null>"
    }
  ]
}
```

`data_artifacts` is ordered by normalized `relative_path`, then
`logical_name`. Only `DATA_ARTIFACT` entries are permitted. The canonical JSON
is hashed:

```text
dataset_artifact_set_id=dataset-artifact-set:sha256:<digest>
```

This identity is complete before Dataset Manifest serialization because the
Dataset Manifest and all other control-plane files are explicitly outside its
preimage.

### 11.4 Acyclic serialization order

The only permitted release order is:

```text
DATA_ARTIFACT + SCHEMA_ARTIFACT bytes
-> Source/Stage/Run child manifests
-> Dataset Manifest
-> post-Dataset Reproduction Manifests, Review Manifests, and certification records
-> final SHA256SUMS
-> external distribution record
```

The Dataset Manifest:

- inventories every `DATA_ARTIFACT`;
- inventories every released `SCHEMA_ARTIFACT`;
- may inventory only already-final pre-Dataset child manifests;
- does not inventory itself;
- does not inventory a Reproduction Manifest that references the Dataset
  Manifest or its descendants;
- does not contain final Review Manifest identities;
- records review requirements and candidate status, not a later final review
  decision.

Post-Dataset Reproduction and Review Manifests reference the exact Dataset
Manifest ID and byte hash. The Dataset Manifest never references those
manifests in return.

Final manifest byte hashes and optional manifest artifact IDs are recorded in
the first later object allowed by this order or in the final release ledger.

The `SHA256SUMS` ledger lists every released file except itself. Its own byte
hash may be reported by the distribution channel or certification record,
but must not be inserted into its own bytes.

No child manifest may reference a parent final hash when that parent embeds
the child's final identity. No manifest-to-manifest or artifact-to-manifest
reference cycle is permitted.

### 11.5 Required graph verification

The correction cycle must generate a directed graph with one node per released
artifact and one edge per identity or final-byte-hash reference. Mechanical
verification must prove:

- the graph is acyclic;
- every edge follows the permitted serialization order;
- every `DATA_ARTIFACT` and `SCHEMA_ARTIFACT` is reachable from the Dataset
  Manifest;
- every released file except `SHA256SUMS` is present in `SHA256SUMS`;
- every final review decision resolves to the exact reviewed Dataset Manifest;
- no final release identity depends on retrieval time, local path, or host.

## 12. Revision 2 Review-Finding Resolution

All first-review findings are addressed textually in revision 2 but remain
pending until focused re-review confirms closure:

| Finding | Revision 2 resolution | Proposed status |
|---|---|---|
| `SCR-MAJ-001` | Unit selected from registered archive-period descriptor before row parsing | Addressed; re-review required |
| `SCR-MAJ-002` | Immutable byte-bound provider evidence and Golden fixtures required | Addressed; evidence generation required |
| `SCR-MIN-001` | Inclusive-start/exclusive-end daily/monthly period semantics defined | Addressed |
| `SCR-MIN-002` | Exact post-conversion one-minute invariants and stage ownership defined | Addressed |
| `AIR-BLK-001` | Collision-free `RCC002_S1_SOURCE_ROW_ID_V2` defined | Addressed; re-review required |
| `AIR-BLK-002` | Exact release classes, artifact-set preimage, and acyclic order defined | Addressed; re-review required |
| `AIR-MAJ-001` | Same resolution as `SCR-MAJ-001`; S0/S1/S2 ownership explicit | Addressed |
| `AIR-MAJ-002` | Header mode moved from generic inference to registered profile | Addressed |
| `AIR-MAJ-003` | Per-file S0 artifacts and aggregate Source Manifest defined | Addressed |
| `AIR-MIN-001` | In-candidate duplicate rejection separated from cross-snapshot revision | Addressed |
| `AIR-MIN-002` | Generated dependency matrix added as a mandatory artifact | Addressed |

No finding is declared closed by proposal authorship alone.

## 13. Version and Impact Matrix

Proposed semantic specification versions:

| Specification | Current | Proposed | Reason |
|---|---:|---:|---|
| Data Pipeline | `0.7.1` | `0.8.0` | multi-file S0 profile, row-ID V2, Audit View V2, S8 placement |
| Data Validation | `0.5.0` | `0.6.0` | timestamp units, header profiles, row-ID V2, S0/S1 normalization |
| Indicator | `0.4.3` | `0.4.3` | contract already correct; code conformance only |
| Signal Transformation | `0.4.2` | `0.4.2` | mechanical dependency citation only |
| Regime and Gate | `0.5.1` | `0.5.1` | mechanical dependency citation only |
| Label and Forward Return | `0.4.1` | `0.5.0` | Audit View V2 table and boundary |
| Reproducibility and Manifest | `0.7.2` | `0.8.0` | identities, manifests, audit, acyclicity |

Mechanical dependency-citation updates do not independently change a
document's semantic version.

New normative artifacts:

```text
6 manifest JSON Schemas
1 source retrieval registry
1 source column-profile registry
1 timestamp-unit profile
1 source-row-ID profile
JSON/ID/manifest Golden Fixtures
provider archive evidence registry
generated document/schema dependency matrix
generated identity dependency graph
corrected full specification bundle
corrected bundle manifest
```

The dependency matrix must contain every normative document, schema, registry,
and view with its ID, version, relative path, and SHA-256. Mechanical
verification must fail on a stale citation, unresolved reference, duplicate
identity, or hash mismatch.

## 14. Required Review Sequence

Before implementation:

1. focused scientific re-review of proposal revision 2;
2. focused architecture re-review of proposal revision 2;
3. proposal acceptance only if every blocker and major finding is closed;
4. corrected specification, registry, fixture, and schema generation;
5. mechanical hash, dependency-matrix, and identity-graph verification;
6. focused scientific review of the generated normative artifacts;
7. focused architecture review of the generated normative artifacts;
8. editorial pass;
9. internal certification decision for the corrected bundle.

Only after that certification:

10. S0/S1 timestamp and source identity implementation;
11. S3-to-S7 `indicator_schema_ref` conformance repair;
12. full affected-stage test and review cycle;
13. regenerated S8 input package;
14. repeated S8 Implementation Readiness Review;
15. S8 implementation if and only if the verdict is READY.

## 15. Required Tests for the Correction Cycle

### 15.1 Source identity and timestamp tests

- same bytes and semantic parameters produce same source snapshot ID;
- changed provider revision changes the ID;
- changed semantic retrieval profile changes the ID;
- retrieval time and local path do not change the ID;
- expected date range does not change the source ID but changes semantic
  build configuration identity;
- provider checksum mismatch fails;
- ZIP member mismatch fails;
- headerless first data row is preserved;
- registered archive periods select the unit before timestamp parsing;
- raw timestamp magnitude cannot select or change the unit;
- daily and monthly byte-bound evidence fixtures pass;
- millisecond and microsecond conversion Golden Fixtures;
- S0 coverage scan and S1 normalization parity;
- mixed 2017-to-2026 input produces canonical millisecond timestamps.

### 15.2 Multi-file row-identity tests

- same record index in different file ordinals yields different IDs;
- canonical archive ordering is independent of local discovery order;
- every multi-file S1 `source_row_id` is unique;
- every S1 row resolves to one source archive and one original record;
- V1 historical identities remain readable but cannot be emitted by new builds.

### 15.3 Audit and manifest tests

- Audit V1 cannot publish;
- Audit V2 has exactly 534 ordered fields;
- Audit V2 hash independently equals the registered value;
- no provenance or S8 metadata appears as Audit V2 row fields;
- every manifest validates against its exact schema;
- every manifest fails all wrong-schema fixtures;
- `manifest_id` is acyclic;
- no manifest inventories itself;
- final checksum ledger excludes itself;
- release classes match Dataset Manifest placement;
- `dataset_artifact_set_id` contains only ordered `DATA_ARTIFACT` entries;
- every released non-ledger file appears exactly once in `SHA256SUMS`;
- identity/reference graph is acyclic and source-resolvable.

### 15.4 Cross-stage conformance tests

- `indicator_schema_ref` exists at S3;
- exact field position and value;
- unchanged propagation through S4-to-S7;
- S3-to-S7 output values otherwise bitwise unchanged;
- new S7 implementation fingerprint recorded;
- full S3, S4, S5, S6, S7, RCC-002, and regression suites pass.

### 15.5 Bundle dependency tests

- every normative document ID/version/hash appears exactly once;
- every schema, registry, fixture set, and view reference resolves;
- no stale version citation remains;
- generated bundle and manifest hashes reproduce;
- identity dependency graph passes directed-acyclic-graph verification.

## 16. Acceptance Criteria

This proposal may be accepted only if independent review confirms:

1. source identity is fully deterministic and free of local/run metadata;
2. provider timestamp precision is explicit and correctly normalized;
3. S0 coverage extraction does not usurp S1 market-row ownership;
4. the S3 conformance repair introduces no scientific value change;
5. Audit View V2 has one unambiguous row grain;
6. artifact and manifest identities are acyclic;
7. all six manifest schemas are complete and fail closed;
8. multi-file row identities are unique and source-resolvable;
9. provider-format claims are supported by immutable byte-bound evidence;
10. release classes and the artifact-set preimage are exact;
11. no open decision can still change logical values, schemas, allowlists,
   leakage boundaries, or deterministic IDs.

## 17. Proposal Decision Requested

```text
REQUESTED DECISION:
APPROVE RCC-002-S8BCP-001 REVISION 2 FOR FOCUSED SCIENTIFIC AND
ARCHITECTURE RE-REVIEW

THIS DOCUMENT IS NOT A SPECIFICATION AMENDMENT.
NO IMPLEMENTATION IS AUTHORIZED BY THIS PROPOSAL ALONE.
```
