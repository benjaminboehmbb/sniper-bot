# RCC-002 S8BCP-001 Revision 2 Corrected-Artifact Scientific Re-Review

## Document Control

| Field | Value |
|---|---|
| Review ID | `RCC-002-S8BCP001-REV2-ART-SRR-001` |
| Date | 2026-07-30 |
| Reviewer system | ChatGPT |
| Reviewed proposal | `RCC-002-S8BCP-001`, Revision 2 |
| Proposal SHA-256 | `f3adb44c16b9927275d10baee410154fb2e7b4075309a8b56fec985afedd8706` |
| Reviewed candidate inventory | `RCC_002_S8BCP001_REV2_CORRECTED_CANDIDATE_SHA256SUMS_2026-07-30.txt` |
| Candidate inventory SHA-256 | `2808bafe8cc182e7f9e76bb801b6e25f5bc96e8836691260bf3c49c3bd0814f9` |
| Candidate files covered | 107 |
| Decision | **PASS — CORRECTED NORMATIVE ARTIFACTS ACCEPTED** |
| Limitation | **NOT AN IMPLEMENTATION OR DATASET CERTIFICATION** |

## 1. Scope

This review evaluates the corrected specifications, Source registries,
byte-bound provider evidence, Golden Fixtures, Manifest Schemas, dependency
matrix, identity graph and deterministic verification tools. It does not
evaluate an S0-to-S8 production build or the future S3-to-S7 implementation
patch.

## 2. Empirical Timestamp Evidence

The evidence verifier independently scanned all 92,160 records in four
immutable Binance Vision archives:

| Evidence branch | Daily | Monthly | Result |
|---|---:|---:|---|
| Pre-boundary milliseconds | 1,440 rows | 44,640 rows | PASS |
| Post-boundary microseconds | 1,440 rows | 44,640 rows | PASS |

Provider checksums, ZIP integrity, one-member structure, header absence,
twelve-column layout, UTF-8/LF/comma encoding, timestamp remainders,
one-minute continuity and exact period coverage all passed.

The unit dependency is non-circular:

```text
registered provider-relative archive name
-> registered inclusive/exclusive UTC archive period
-> preselected timestamp unit
-> exact integer conversion
-> byte-derived coverage
-> period/coverage reconciliation
```

No raw magnitude, requested date, normalized coverage, local path or
retrieval time can select the unit.

## 3. Scientific Contract Review

| Criterion | Result | Evidence |
|---|---|---|
| Source identity is deterministic and local/run independent | PASS | Exact Source Snapshot V1 JCS preimage; Golden SHA-256 `3bddbcad…ab32`; explicit exclusions |
| Provider precision is explicit and correctly normalized | PASS | Period-selected unit registry plus complete 92,160-row evidence scan |
| S0 coverage does not usurp S1 market-row ownership | PASS | S0 records byte-derived coverage and per-file evidence; S1 alone emits normalized market rows |
| S3 conformance repair changes no scientific value | PASS AT CONTRACT LEVEL | `indicator_schema_ref` is metadata pass-through; formulas, OHLCV, indicators, signals, regimes, gates and labels are unchanged |
| Audit V2 has one row grain | PASS | Exact equality with the 534 ordered Label Research fields; no S8 or manifest columns |
| Manifest/artifact identities are acyclic | PASS | Candidate-before-review order, prohibited self-fields and self-excluding ledger |
| Six Manifest Schemas are strict and fail closed | PASS | Draft 2020-12 compile; 12/12 positive and 66/66 negative fixture results |
| Multi-file row identities are unique and source-resolvable | PASS IN SPECIFICATION | Injective V2 tuple of snapshot, canonical file ordinal and original record index; width/overflow rules and Golden cases |
| Provider-format claims are byte-bound | PASS | Four archive hashes, four provider checksums and four CSV hashes registered |
| Release classes and artifact-set preimage are exact | PASS | Five-class registry and exact ordered `DATA_ARTIFACT` preimage |
| No S8BCP decision remains open | PASS | Profiles, schemas, allowlists, deterministic IDs and release boundaries are materialized and versioned |

## 4. Scientific Non-Regression

The correction changes source interpretation, lineage and release-control
contracts. It does not change:

- OHLCV numerical values;
- canonical millisecond timestamps after exact conversion;
- indicator or signal formulas;
- regime or gate rules;
- forward-return denominators or horizons;
- label or barrier thresholds;
- leakage classes;
- decision-time semantics.

The pre/post-transition boundary is supported by both daily and monthly
provider bytes. The claim remains deliberately scoped to registered Binance
Vision BTCUSDT Spot 1m archive families.

## 5. Remaining Implementation Gates

The following are not findings against the normative artifacts and remain
mandatory before implementation certification:

1. implement S0/S1 profile consumption and Source Row ID V2;
2. implement the S3-to-S7 `indicator_schema_ref` pass-through patch;
3. prove S3-to-S7 scientific values otherwise bitwise unchanged;
4. run full S0-to-S7, RCC-002 and regression suites;
5. generate a real Dataset Manifest candidate and prove its concrete release
   graph and ledger.

## 6. Decision

**PASS — CORRECTED NORMATIVE ARTIFACTS ACCEPTED**

The reviewed 107-file candidate closes the scientific artifact-generation
gates of `RCC-002-S8BCP-001` Revision 2. It may proceed to focused
architecture review and controlled repository import. This decision does not
certify code, a dataset or a production release.
