# RCC-002 S8BCP-001 Revision 2 Scientific Re-Review

## Document Control

| Field | Value |
|---|---|
| Review ID | `RCC-002-S8BCP001-REV2-SRR-001` |
| Date | 2026-07-30 |
| Reviewed proposal | `RCC_002_S8_BLOCKER_CORRECTION_PROPOSAL_2026-07-30.md` |
| Proposal ID/revision | `RCC-002-S8BCP-001`, revision 2 |
| Proposal SHA-256 | `f3adb44c16b9927275d10baee410154fb2e7b4075309a8b56fec985afedd8706` |
| Prior review | `RCC-002-S8BCP001-SCR-001` |
| Decision | **PASS FOR NORMATIVE ARTIFACT GENERATION** |
| Limitation | **NOT A SPECIFICATION OR IMPLEMENTATION CERTIFICATION** |

## 1. Scope

This re-review determines whether proposal revision 2 resolves the design
findings from the first scientific review. It does not claim that provider
archives, Golden fixtures, corrected specifications, or implementation tests
already exist.

## 2. Finding Resolution

| Finding | Result | Evidence in revision 2 |
|---|---|---|
| `SCR-MAJ-001` | CLOSED IN DESIGN | Unit branch is selected from a registered provider-relative archive-period descriptor before any row timestamp is interpreted |
| `SCR-MAJ-002` | CLOSED AS PROPOSAL FINDING | Byte-bound daily/monthly evidence and transition-edge Golden fixtures are mandatory profile-release gates |
| `SCR-MIN-001` | CLOSED | Archive periods use inclusive UTC start and exclusive UTC end; boundary-crossing periods fail |
| `SCR-MIN-002` | CLOSED | Exact one-minute post-conversion invariants and S0/S1/S2 ownership are stated |

The empirical work required by `SCR-MAJ-002` remains an execution gate. The
finding is closed at proposal level because revision 2 no longer assumes the
untested structure is true merely from documentation; it requires immutable
source evidence before profile release.

## 3. Timestamp Decision

The accepted dependency is:

```text
registered provider archive name
-> registered UTC archive period
-> preselected provider timestamp unit
-> exact integer conversion
-> byte-derived normalized coverage
-> period/coverage reconciliation
```

This removes the earlier circularity. Raw magnitude, requested dates, local
paths, and normalized coverage cannot select the timestamp unit.

Canonical RCC-002 timestamps remain integer UTC epoch milliseconds. For the
registered microsecond branch:

```text
raw_open_time % 1000 == 0
open_time_ms = raw_open_time // 1000

raw_close_time % 1000 == 999
close_time_ms = raw_close_time // 1000
```

No rounding, floating point, or per-record unit guessing is permitted.

## 4. Scientific Non-Regression

Revision 2 does not alter:

- OHLCV values;
- indicator formulas;
- signal formulas;
- regime or gate logic;
- forward-return horizons or denominators;
- label thresholds;
- barrier order;
- leakage classes;
- decision-time semantics.

The change is restricted to source interpretation, identity, provenance, and
manifest architecture. No new look-ahead path is introduced.

## 5. Mandatory Execution Gates

Before scientific certification of corrected normative artifacts:

1. verify immutable pre-transition, boundary, post-transition, daily, and
   monthly provider archives;
2. reproduce provider checksums and record archive byte hashes;
3. prove header mode, member count, 12-column records, delimiter, and
   timestamp remainders;
4. pass positive and negative Golden fixtures;
5. prove S0/S1 conversion parity;
6. prove the post-conversion one-minute invariants;
7. run S2-to-S7 non-regression checks on equivalent canonical rows.

Any verified provider archive contradicting the registered profile blocks
profile release and requires a corrected profile version.

## 6. Decision

**PASS FOR NORMATIVE ARTIFACT GENERATION**

Proposal revision 2 is scientifically coherent and may proceed to corrected
specification, registry, evidence-record, fixture, and schema generation.

This decision does not authorize implementation and does not certify the
future generated artifacts. Those artifacts require their own scientific
review after mechanical verification.
