# STEP20D Dynamic Exposure Scaling Specification

## Background

STEP20A produced strong results.

However:

STEP20A uses trade-lifetime information and is not live-compatible.

STEP20C attempted entry-time sizing only.

Result:

- small PF improvement
- small drawdown improvement
- large profit reduction

Conclusion:

Entry-time shadow risk alone is insufficient.

## Core Hypothesis

Risk information becomes meaningful after trade entry.

Therefore:

Do not reduce position size aggressively at entry.

Instead:

Dynamically reduce exposure when risk increases during trade lifetime.

## Design Principle

Trade opens normally.

Initial exposure:

- 100%

After entry:

Exposure may only decrease.

Exposure may never increase.

## Candidate Scaling Model

Level 0

shadow_risk_score <= 0.30

Exposure:

- 100%

Level 1

shadow_risk_score > 0.30

for 3 consecutive snapshots

Exposure:

- 50%

Level 2

shadow_risk_score > 0.50

for 3 consecutive snapshots

Exposure:

- 25%

Level 3

shadow_risk_score > 0.70

for 3 consecutive snapshots

Exposure:

- 10%

## Safety Rules

Exposure may only move:

100 -> 50 -> 25 -> 10

Never:

10 -> 25
25 -> 50
50 -> 100

within the same trade.

## Live Compatibility

Allowed:

- current shadow_risk_score
- current regime mismatch
- current atr stress
- current adverse pressure

Forbidden:

- future snapshots
- future trade information
- mean trade risk
- max trade risk

## Replay Requirements

STEP20D replay must compare:

- Original
- STEP20A
- STEP20C
- STEP20D

Metrics:

- pnl
- profit_factor
- drawdown
- winrate
- exposure reductions
- capital preserved

## Success Criteria

Desired outcome:

- closer to STEP20A than STEP20C
- substantial drawdown reduction
- limited profit degradation
- fully live-compatible

## Current Status

STEP20A

- validated

STEP20B

- design completed

STEP20C

- tested
- insufficient

STEP20D

- specification completed
- replay not implemented

## Next Step

Create:

scripts/state_research/analyze_step20D_dynamic_exposure_scaling.py

