# P39 TIMING SHORT SEED DESIGN

Date: 2026-06-06
Device: G15 / AR15
Environment: WSL

## Objective

Design short-seed support for the Live L1 5m timing layer before creating or activating short timing seeds.

No runtime code is changed in P39.

## Background

P30 showed that the 5m timing layer was long-only.

P31 designed explicit timing direction.

P32 created a v2 seed file with explicit direction.

P34/P35 removed implicit long fallback.

P37 migrated runtime to the v2 seed file.

P38 validated that runtime now uses:

seeds/5m/btcusdt_5m_timing_core_v2.csv

Current v2 seed content:

- C01_rsi_stoch_06, direction=long
- C02_rsi_stoch_08, direction=long

## Current Limitation

The v2 timing seed file is explicit but still long-only.

Therefore:

- long timing votes are supported
- short timing votes are not yet represented
- short entries rely only on 1m/raw logic and other gates
- 5m confirmation is asymmetric

## Design Goal

Add short timing seeds in a controlled, testable way without changing execution, recovery, monitoring, or operational profile logic.

## Proposed Short Seed Model

Use the same v2 schema:

- seed_id
- direction
- comb_json

Short seed IDs should be explicit:

- S01_rsi_stoch_06
- S02_rsi_stoch_08

Proposed entries:

S01_rsi_stoch_06,short,"{'rsi': 0.6, 'stoch': 0.6}"
S02_rsi_stoch_08,short,"{'rsi': 0.8, 'stoch': 0.8}"

## Important Caveat

This is only a structural first version.

It does not prove that these short seeds are profitable.

It only gives the timing layer the ability to emit short votes.

## Validation Requirements Before Runtime Use

Before accepting short seeds operationally:

1. isolated timing test must show long and short are both possible

2. P30-style bias audit must show vote distribution is no longer structurally forced long

3. short seed behavior must be inspected in a mini runtime segment

4. P29 behavior metrics must be recalculated after a controlled run

5. no full run before mini validation

## Risk

Adding short timing seeds may materially change trading behavior.

Risks:

- more short trades
- fewer long confirmations
- different exit structure
- changed winrate / profit factor
- possible overtrading if short confirmation becomes too permissive

## Mitigation

Use strict sequence:

P40 create short seeds in v2 file

P41 isolated timing short-seed test

P42 mini runtime validation

P43 trading behavior reassessment

No large run before P42/P43.

## Decision

Proceed to P40 only as a controlled seed-file change.

No runtime code changes are required for P40.

## P39 Result

Short seed design completed.

Status:

PASS
