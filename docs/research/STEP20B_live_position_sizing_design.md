# STEP20B Live Position Sizing Design

## Goal

Design a safe live-compatible position sizing layer based on the validated STEP20A research result.

STEP20A result:

- shadow_risk_score can improve risk-adjusted performance when used for position sizing.
- It should not be used as an entry gate.
- It should not be used as a forced dynamic exit.

## Validated STEP20A Rule

Position multiplier:

- mean_shadow_risk <= 0.30 -> 1.00x
- mean_shadow_risk <= 0.50 -> 0.50x
- mean_shadow_risk > 0.50 -> 0.25x

Important:

The research replay used mean shadow risk over trade lifetime.
Live implementation cannot know future mean risk.

Therefore STEP20B must not directly copy the replay rule.

## Live-Compatible Principle

For live operation, use only current known state:

- current shadow_risk_score
- current regime mismatch
- current ATR stress
- current adverse score pressure

No future information may be used.

## Proposed Live Multiplier

Initial candidate:

- shadow_risk_score <= 0.30 -> 1.00x
- shadow_risk_score <= 0.50 -> 0.50x
- shadow_risk_score > 0.50 -> 0.25x

This is only a candidate and must be validated with live-compatible replay before production use.

## Integration Location

Do not integrate directly into entry logic.

Preferred architecture:

1. Compute shadow_risk_score in live_l1/core/loop.py
2. Pass risk state to position sizing layer
3. Apply multiplier only to calculated position size
4. Keep entry/exit decision logic unchanged

## Candidate Files

Likely affected files:

- live_l1/core/loop.py
- live_l1/core/execution.py
- live_l1/meta_state/meta_state_shadow.py
- possibly live_l1/meta_state/meta_state_runtime.py

## Safety Rules

STEP20B must obey:

- no entry blocking
- no forced exit
- no hidden leverage increase
- multiplier may only reduce or preserve size
- multiplier must never exceed 1.00
- fallback multiplier must be conservative
- all multipliers must be logged

## Required Logging

Every trade entry must log:

- raw position size
- shadow_risk_score
- regime_mismatch_score
- atr_stress_score
- adverse_score_pressure
- applied_position_multiplier
- final_position_size
- reason code

## Required Validation Before Live Use

Before any production/live activation:

1. Mini-run 200k @ offset 1000000
2. 200k @ offset 0
3. 200k @ offset 500000
4. 500k @ offset 1500000
5. 1M @ offset 2500000
6. 4.3M full-history validation

Validation must compare:

- original
- STEP20A research replay
- STEP20B live-compatible replay

## Current Status

STEP20A:

- validated research candidate

STEP20B:

- design phase
- not implemented
- not live-ready

## Next Step

Build STEP20B live-compatible replay before modifying production position sizing.

