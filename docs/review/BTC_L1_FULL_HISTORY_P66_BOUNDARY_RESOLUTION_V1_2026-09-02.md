# BTC-L1 Full-History / P66 Boundary Resolution V1

Date: 2026-09-02

Status: CLOSED

## Purpose

Permanently resolve the apparent historical discrepancy between the P66 result with 556 closed trades and the current canonical full-history result with 563 closed trades.

This issue MUST NOT be re-investigated absent a documented reopen trigger.

## Canonical dataset

- Logical ID: BTC_L1_CANONICAL_V1
- Path: `data/l1_full_run.csv`
- SHA256: `530983b84c461d46a49058428b1549fa87fd320cb2f04a070eeb081275aafe1f`
- Data rows: 4374557
- Start: 2017-08-17 04:00:00+00:00
- End: 2025-12-31 23:59:00+00:00

## P66 documentation correction

P66 was historically described as a complete full-history run, but the actual runtime length was 4,300,000 ticks.

- P66 runtime ticks: 4300000
- Dataset timestamp at tick 4,300,000: 2025-11-10 05:22:00+00:00
- P66 closed trades: 556
- P66 normalized trade hash: `afd9a22de398c1673d5400da75b132cb36b12f85178f95d2534677d62c2d5226`

Therefore P66 did NOT process the final 74,557 rows of the canonical dataset.

The historical documentation statement that P66 processed the
dataset through 2025-12-31 is superseded by this resolution.

## Trade-level proof

- Historical P66-compatible trades: 556
- Current full-history trades: 563
- Shared entry keys: 556
- Historical-only entries: 0
- Current-only entries: 7
- Shared entries with changed outcomes: 0

All 556 historical trades are semantically unchanged in the current full-history result.

The seven additional trades occur only after the P66 boundary.

- First additional trade entry: 2025-11-13 23:53:00+00:00
- Dataset row of first additional trade: 4,305,431
- Combined PnL of seven additional trades: -530.79

## Current canonical full-history baseline

- Trades: 563
- Final equity: 23491.22
- Total PnL: 13491.22
- Return: 134.9122%
- Winrate: 69.8046%
- Profit Factor: 1.635604
- Max Drawdown: 15.5646%
- Average PnL/trade: 23.9631
- Average duration: 1650.59 sec

## Full A / Full B determinism

- Full A ticks: 4,374,557
- Full B ticks: 4,374,557
- Full A trades: 563
- Full B trades: 563
- Normalized trade hash A: `46706ec9f6446eb5ceecf7782199a8a7fab8a7f91c318ce560f5daa83b98646c`
- Normalized trade hash B: `46706ec9f6446eb5ceecf7782199a8a7fab8a7f91c318ce560f5daa83b98646c`
- Ordered normalized trade sequence: IDENTICAL
- Final S2 state: IDENTICAL
- Final loss-cluster state: IDENTICAL

Conclusion: current BTC-L1 main is deterministically reproducible.

## Final scientific conclusion

There is NO evidence of strategy drift in the 556-vs-563 comparison.

The complete difference is caused by the historical P66 run ending at tick 4,300,000 while the current canonical run processes all 4,374,557 rows.

The old 556-trade / approximately 140.22% result MUST NOT be used as the authoritative full-2017-to-2025 baseline.

The authoritative canonical full-history reference is the 563-trade result documented above.

## Closure policy

DO NOT reopen this investigation unless at least one trigger occurs:

1. Canonical dataset SHA256 changes.
2. Canonical row count or date range changes.
3. Current normalized full-history trade hash changes.
4. Contradictory primary execution evidence is discovered.
5. Formal scientific review explicitly requires reopening.

Absent such a trigger:

- no repeat P66 boundary analysis;
- no repeat 556-vs-563 trade forensics;
- no repeat dataset-end explanation;
- use the 563-trade canonical baseline.

## Scope

- Candidate selection: NO
- OOS claim: NO
- Holdout claim: NO
- Performance used for strategy selection: NO

## Machine-readable evidence

`docs/review/evidence/BTC_L1_FULL_HISTORY_P66_BOUNDARY_RESOLUTION_V1_2026-09-02.json`
