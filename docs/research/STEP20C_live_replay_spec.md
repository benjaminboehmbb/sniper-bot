# STEP20C Live Replay Specification

## Purpose

STEP20A demonstrated strong performance improvements when using shadow_risk_score for position sizing.

However:

STEP20A used information accumulated during the full trade lifetime.

This creates future-information leakage and cannot be used as a direct basis for live implementation.

STEP20C exists to remove this limitation.

## Objective

Build a fully live-compatible replay.

The replay must only use information that is available at the moment a position is opened.

No future trade information may be used.

## Comparison Framework

Three systems will be compared.

### Baseline

Original strategy

Characteristics:

- no position sizing adjustment
- current production reference

### STEP20A

Research replay

Characteristics:

- uses mean_shadow_risk across full trade lifetime
- contains future information
- research reference only

### STEP20C

Live-compatible replay

Characteristics:

- uses only entry-time information
- no future information
- candidate for production integration

## Allowed Inputs

At entry time only:

- shadow_risk_score
- regime_mismatch_score
- atr_stress_score
- adverse_score_pressure
- market_regime
- current_score

No post-entry data may be used.

## Forbidden Inputs

Not allowed:

- mean_shadow_risk over trade
- max_shadow_risk over trade
- high_risk_count over trade
- high_risk_pct over trade
- trade outcome
- future snapshots
- future lifecycle information

## Initial Position Sizing Model

Version C1

Entry shadow risk:

- risk <= 0.30 -> 1.00x
- risk <= 0.50 -> 0.50x
- risk > 0.50 -> 0.25x

This mirrors STEP20A as closely as possible while remaining live-compatible.

## Required Output Metrics

For each replay:

- final_equity
- total_pnl
- return_pct
- winrate
- profit_factor
- avg_pnl
- max_drawdown_abs
- max_drawdown_pct
- trade_count

## Validation Sequence

Mandatory order:

1. 200k @ offset 1000000
2. 200k @ offset 0
3. 200k @ offset 500000
4. 500k @ offset 1500000
5. 1M @ offset 2500000
6. 4.3M full-history

Same validation standard as previous research phases.

## Success Criteria

STEP20C should be compared against:

- Original
- STEP20A

Desired outcome:

- retain majority of STEP20A drawdown reduction
- retain majority of STEP20A profit factor improvement
- avoid major profit degradation

No requirement exists to fully match STEP20A.

## Failure Criteria

STEP20C is considered unsuccessful if:

- performance collapses toward baseline
- drawdown reduction disappears
- profit factor improvement disappears
- results become inconsistent across validation windows

## Integration Gate

No production implementation is allowed until:

- STEP20C replay completed
- validation sequence completed
- results documented
- dedicated implementation review completed

## Current Status

STEP20A

- validated

STEP20B

- design completed

STEP20C

- specification completed
- replay not yet implemented

## Next Step

Create:

scripts/state_research/analyze_step20C_live_replay.py

and perform the first live-compatible replay on:

200k @ offset 1000000

