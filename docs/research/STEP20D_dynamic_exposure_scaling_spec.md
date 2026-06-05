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


---

## STEP20D v1 Result

The first STEP20D proof-of-concept replay showed strong results on the 4.3M full-history run.

Original:

- pnl: 14022.01
- pf: 1.6859
- max_dd_pct: 0.1556

STEP20D v1:

- pnl: 19564.81
- pf: 4.1823
- max_dd_pct: 0.0283

Sensitivity:

D1:
- pnl: 19564.81
- pf: 4.1823
- max_dd_pct: 0.0283

D2:
- pnl: 19051.15
- pf: 2.9016
- max_dd_pct: 0.0437

D3:
- pnl: 19670.07
- pf: 2.6093
- max_dd_pct: 0.0634

## Methodological Limitation

STEP20D v1 applies the final multiplier retroactively to the full trade.

This is not live-accurate.

A correct live-compatible replay must simulate exposure reductions over time during the trade.

## Next Step

Create STEP20E:

scripts/state_research/analyze_step20E_true_dynamic_exposure_replay.py

Goal:

- start every trade at 1.00x
- reduce exposure only after risk thresholds are triggered
- never increase exposure again during the same trade
- calculate realized PnL segment by segment using lifecycle prices

---

## STEP20E True Dynamic Exposure Replay Result

STEP20E corrected the methodological limitation of STEP20D v1.

Instead of applying the final multiplier retroactively to the full trade, STEP20E simulated exposure reductions over time using lifecycle prices.

4.3M full-history result:

Original

- pnl: 14022.01
- pf: 1.6859
- max_dd_pct: 0.1556

STEP20E

- pnl: 9597.75
- pf: 1.5180
- max_dd_pct: 0.1084

Result

- pnl worse
- pf worse
- drawdown improved but not enough
- winrate reduced

Conclusion

The naive true dynamic exposure scaling model is not validated.

Key interpretation:

shadow_risk_score contains useful trade-quality information, but the current live-compatible scaling mechanics reduce too much profitable exposure.

Current status:

- STEP20A: validated research result, but not live-compatible
- STEP20C: live-compatible entry sizing, not sufficient
- STEP20D v1: proof of concept, methodologically optimistic
- STEP20E: true dynamic replay, not validated

Next research direction should focus on selective scaling, not broad automatic scaling.
