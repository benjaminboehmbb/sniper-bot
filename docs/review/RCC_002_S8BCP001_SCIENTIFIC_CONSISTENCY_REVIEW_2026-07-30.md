# RCC-002 S8BCP-001 Scientific Consistency Review

## Document Control

| Field | Value |
|---|---|
| Project | RCC-002 Scientific Data Processing Architecture |
| Review ID | `RCC-002-S8BCP001-SCR-001` |
| Review type | Focused internal scientific consistency review |
| Date | 2026-07-30 |
| Reviewed proposal | `RCC_002_S8_BLOCKER_CORRECTION_PROPOSAL_2026-07-30.md` |
| Proposal ID | `RCC-002-S8BCP-001` |
| Baseline commit | `a4b7c72b2e7a12bac139d1bfce8cb05200d6fd58` |
| Reviewer | OpenAI Codex internal review |
| Decision | **CONDITIONALLY ACCEPTABLE — REQUIRED CORRECTIONS BEFORE APPROVAL** |

## 1. Scope

This review tests whether the correction proposal is scientifically coherent,
deterministic, time-safe, leakage-safe, and suitable for a long-lived
reproducible trading-data pipeline.

The review is deliberately limited to:

- provider timestamp semantics;
- canonical time-unit normalization;
- coverage construction;
- source-format assumptions;
- downstream time and label semantics;
- scientific non-regression.

It does not certify implementation, source archives, corrected
specifications, JSON Schemas, or a final S8 build.

## 2. Executive Decision

The central millisecond/microsecond decision is scientifically sound:

1. canonical RCC-002 row timestamps remain integer UTC epoch milliseconds;
2. provider-native milliseconds are preserved exactly;
3. provider-native microseconds are converted by exact integer division;
4. remainder checks prevent silent precision loss;
5. unit guessing and floating-point conversion are prohibited;
6. one versioned provider profile owns the effective-date rule;
7. S0 coverage and S1 normalization must call the same pure conversion
   function.

This is the correct long-term design direction. It isolates provider change
from the canonical data model and makes future provider changes explicit
profile-version events.

The proposal is not yet scientifically approvable because the unit-selection
rule is circular as written and because several provider-format assumptions
are not yet bound to verified source fixtures. These findings do not invalidate
canonical milliseconds or the exact conversion rule. They require a more
precise selection and evidence contract before implementation.

## 3. Evidence Examined

Internal evidence:

- `rcc002/s1/normalize.py` currently parses raw time integers and uses them as
  milliseconds without a provider-unit conversion;
- `rcc002/s1/time.py` defines interval durations and candle close semantics in
  milliseconds;
- S2-to-S7 contracts consume canonical millisecond timestamps;
- the label and forward-return formulas use row order and canonical candle
  times and do not require provider-native sub-millisecond precision.

Provider evidence recorded by the proposal:

- Binance public market data is distributed in daily and monthly archives;
- archives have associated checksums;
- Spot kline data has a fixed 12-column order;
- Spot timestamps from 2025-01-01 onward use microseconds.

Primary provider reference:

```text
https://github.com/binance/binance-public-data
```

The provider reference supports the unit transition and broad archive
structure. It does not, by itself, certify every structural invariant added by
the proposed RCC-002 retrieval profile.

## 4. Findings

### `SCR-MAJ-001` — Timestamp-unit selection is circular

Severity: **MAJOR**

Status: **OPEN**

The proposal chooses the raw timestamp unit from "provider logical coverage"
and then computes actual coverage only after timestamp-unit normalization.
That creates a circular decision:

```text
unit -> normalized timestamps -> actual coverage -> unit
```

An implementation could accidentally resolve the cycle through timestamp
magnitude inference, filename inference without a registry contract, or
per-record guessing. All three would violate the proposal's own fail-closed
goal.

Required correction:

- select the unit profile branch exclusively from a registered,
  provider-relative archive-period descriptor obtained before parsing row
  timestamps;
- define its canonical fields, such as archive family, period start, period
  end, and provider-relative name;
- require the period descriptor to be derived and validated by the retrieval
  registry, not by local path or requested date;
- use the selected unit only to parse every row;
- afterward reconcile byte-derived normalized coverage against the registered
  archive period;
- reject boundary-crossing or contradictory archives;
- never use raw magnitude as a selection input.

Required replacement dependency:

```text
registered archive period
-> timestamp-unit branch
-> exact row conversion
-> byte-derived actual coverage
-> period/coverage reconciliation
```

### `SCR-MAJ-002` — Provider profile assumptions need byte-bound Golden fixtures

Severity: **MAJOR**

Status: **OPEN**

The proposed profile additionally asserts:

- `header_mode=ABSENT`;
- exactly one CSV member per ZIP;
- exact 12-column physical records;
- mandatory provider SHA-256 checksum compatibility;
- microsecond open-time remainder `0`;
- microsecond close-time remainder `999`.

These are plausible and internally coherent, but the cited provider overview
does not fully establish all of them for every archive family and transition
edge. A long-term profile must be based on actual immutable examples, not only
documentation prose.

Required correction:

- register at least one immutable pre-transition daily archive;
- register at least one immutable post-transition daily archive;
- register the last pre-transition and first post-transition edge examples;
- register at least one monthly archive for each applicable unit regime;
- record provider-relative names, provider checksum text, archive SHA-256,
  CSV member name, record count, first record, last record, and unit;
- verify header behavior, member count, column count, delimiter, timestamp
  remainder rules, and checksum parsing from those bytes;
- convert the verified samples into positive and negative Golden fixtures;
- fail profile acceptance if an official archive contradicts any asserted
  invariant.

The fixtures may be compact test extracts only if their lineage to the
verified full archive and its checksum is recorded.

### `SCR-MIN-001` — Boundary semantics need an archive-family rule

Severity: **MINOR**

Status: **OPEN**

"Strictly before" and "on or after" 2025-01-01 are clear for row timestamps
but not yet complete for archive selection. Daily and monthly archives require
one canonical period interpretation.

Required correction:

- define period start and period end as UTC boundaries in the retrieval
  profile;
- specify whether the branch is selected by archive-period start, archive
  family plus period token, or an explicit provider catalog attribute;
- require every selected archive to lie entirely within one registered unit
  regime;
- reject an archive whose records cross the selected regime boundary.

### `SCR-MIN-002` — Scientific invariants must be stated after conversion

Severity: **MINOR**

Status: **OPEN**

The proposal includes appropriate tests, but the normative invariant should
be stated directly.

Required correction:

For every accepted one-minute kline after conversion:

```text
open_time_ms % 60000 == 0
close_time_ms == open_time_ms + 59999
close_time_ms - open_time_ms == 59999
```

S0 verifies provider-profile timestamp structure. S1 performs canonical
conversion. S2 retains ownership of canonical interval-alignment and temporal
quality findings. The specification must distinguish these responsibilities
so the same check is not given conflicting stage semantics.

## 5. Accepted Scientific Decisions

The following proposal decisions pass this review:

| Decision | Result | Reason |
|---|---|---|
| Canonical unit is integer milliseconds | PASS | Matches all existing RCC-002 time contracts |
| Provider-native microseconds are not propagated downstream | PASS | No current RCC-002 formula requires sub-millisecond precision |
| Microseconds use exact integer conversion | PASS | Deterministic and free of floating-point error |
| Remainder mismatch fails closed | PASS | Prevents silent truncation of unexpected precision |
| No magnitude guessing | PASS | Avoids hidden behavior and future threshold bugs |
| One conversion function for S0 and S1 | PASS | Prevents source-identity/data-row divergence |
| Profile is provider- and market-specific | PASS | Avoids unsafe generalization to futures or other providers |
| Future provider changes require a new profile version | PASS | Provides durable change control |
| Indicator, signal, regime, gate, label, and barrier formulas remain unchanged | PASS | Correction changes ingestion semantics, not trading logic |

## 6. Leakage and Trading-Semantics Assessment

No new look-ahead path is introduced by canonical time conversion.

The conversion is a deterministic representation change applied before
indicator and label computation. It does not:

- shift a row to another candle;
- alter OHLCV values;
- expose future prices;
- change horizon lengths;
- change forward-return denominators;
- change barrier ordering;
- change signal or gate state.

This conclusion depends on the exact post-conversion candle invariants passing.
If a timestamp is misclassified by a factor of 1,000, all temporal ordering,
coverage, segmentation, and label timing become invalid. Therefore timestamp
profile failure must remain build-fatal.

## 7. Required Verification Matrix

Before scientific re-review, the correction cycle must produce:

| Test class | Minimum evidence |
|---|---|
| Pre-transition unit | Verified archive, checksum, first/last raw and normalized timestamps |
| Post-transition unit | Verified archive, checksum, first/last raw and normalized timestamps |
| Boundary | Last pre-transition and first post-transition registered periods |
| Archive families | Applicable daily and monthly cases |
| Structural format | Member count, member name, header mode, 12 columns, delimiter |
| Exactness | Integer-only conversion and required remainders |
| Parity | Identical S0 and S1 conversion output for the same raw values |
| Time semantics | Alignment, close convention, ordering, coverage |
| Fail closed | Wrong unit, wrong remainder, crossing boundary, unknown profile |
| Non-regression | S2-S7 scientific formulas unchanged on equivalent canonical rows |

## 8. Decision and Exit Criteria

Decision:

**CONDITIONALLY ACCEPTABLE — REQUIRED CORRECTIONS BEFORE APPROVAL**

The microsecond/millisecond architecture is accepted in principle and should
remain the foundation of the correction. Approval requires:

1. closure of `SCR-MAJ-001`;
2. closure of `SCR-MAJ-002`;
3. incorporation of both minor clarifications;
4. passing Golden fixtures and boundary tests;
5. focused scientific re-review of the corrected proposal and generated
   normative artifacts.

No corrected specification, implementation, or S8 export should be certified
from the current proposal revision.
