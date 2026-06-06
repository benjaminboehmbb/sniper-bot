# P31 5M TIMING DIRECTION MODEL DESIGN

Date: 2026-06-06
Device: G15 / AR15
Environment: WSL

## Objective

Design a clean direction model for the Live L1 5m timing layer before changing runtime behavior.

No code is changed in P31.

## Background

P29 showed that Live L1 trading behavior is highly selective.

P30 showed that the 5m timing layer emits only long votes.

Observed runtime distribution:

- vote_5m_direction=long: 4,300,720
- vote_5m_direction=short: 0
- vote_5m_direction=none: 0

Current default seed file:

seeds/5m/btcusdt_5m_long_timing_core_v1.csv

Seed file columns:

- seed_id
- comb_json

Seed file rows:

- C01_rsi_stoch_06
- C02_rsi_stoch_08

No explicit direction or side column exists.

## Root Cause

The current 5m timing model has an implicit long bias.

Reasons:

1. The default seed path is long-specific.

2. The seed file has no direction column.

3. timing_5m.py normalizes missing direction to long.

Result:

All loaded seeds become long seeds.

## Current Behavior

If direction is missing:

direction = long

This creates permanent long-only timing behavior.

## Design Principle

Direction must be explicit.

A seed must not silently become long because a direction field is missing.

## Proposed Direction Model

Allowed directions:

- long
- short
- none

Meaning:

long:

Seed confirms or supports long entries.

short:

Seed confirms or supports short entries.

none:

Seed is neutral or invalid for directional confirmation.

## New Seed Schema

Required columns:

- seed_id
- direction
- comb_json

Example:

seed_id,direction,comb_json
C01_rsi_stoch_06,long,"{...}"
C02_rsi_stoch_08,long,"{...}"
S01_rsi_stoch_06,short,"{...}"
S02_rsi_stoch_08,short,"{...}"

## Backward Compatibility

Old seed files with only:

- seed_id
- comb_json

should not be silently treated as long in future strict mode.

Transition rule:

For legacy mode only:

- missing direction may be treated as long
- but only if explicitly enabled

Recommended future environment option:

L1_TIMING_ALLOW_LEGACY_LONG_DEFAULT=1

Default future behavior:

missing direction -> none or validation failure

## Runtime Behavior

compute_5m_timing_vote should:

1. read all seeds

2. require explicit direction in strict mode

3. normalize direction

4. score long and short seeds independently

5. choose best seed by absolute or direction-aware score

6. return:

TimingVote(direction, strength, seed_id)

## Short Support

Short timing requires one of the following:

Option A:

Create a separate short seed file.

Example:

seeds/5m/btcusdt_5m_short_timing_core_v1.csv

Option B:

Create one combined seed file.

Example:

seeds/5m/btcusdt_5m_timing_core_v2.csv

with both long and short seeds.

Recommended:

Option B

Reason:

A single file with explicit direction prevents configuration mismatch.

## Proposed New File

seeds/5m/btcusdt_5m_timing_core_v2.csv

Required columns:

- seed_id
- direction
- comb_json

## Migration Plan

P31:

Design direction model.

P32:

Create v2 timing seed file with explicit direction.

P33:

Implement strict direction handling in timing_5m.py.

P34:

Run timing bias regression audit.

P35:

Run short operational validation.

## Acceptance Criteria

The timing direction model is accepted only if:

- no silent long fallback remains in strict mode
- seed direction is explicit
- long and short seeds are both representable
- legacy seed behavior is documented
- runtime logs can show long, short or none timing votes
- no production behavior changes happen without validation

## Risk Assessment

Risk:

Changing timing direction may alter trade distribution.

Mitigation:

- Mini-test first
- Short controlled run
- Compare P29 metrics before and after
- Do not run full validation before smoke tests pass

## Decision

Do not patch timing_5m.py yet.

First create explicit v2 timing seed schema.

Proceed to:

P32 5m Timing Seed v2 Creation

## P31 Result

5m timing direction model designed.

Status:

PASS
