# STEP20 Position Sizing Hypothesis

## Background

STEP19 demonstrated:

- shadow_risk_score contains predictive information
- shadow_risk_score is not currently a robust entry gate
- shadow_risk_score is not currently a robust dynamic exit rule

However:

- mean_shadow_risk vs pnl ≈ -0.42
- mean_shadow_risk vs win ≈ -0.57

These are among the strongest relationships observed during the state-research phase.

## New Hypothesis

Do not block trades.

Do not force exits.

Instead:

Reduce exposure when risk is elevated.

Example:

Low risk:
- position size = 100%

Medium risk:
- position size = 50%

High risk:
- position size = 25%

## Research Goal

Evaluate whether shadow_risk_score is more effective as:

- exposure control
- risk scaling
- capital allocation

than as:

- entry gate
- exit trigger

## Method

Replay existing trade history using dynamic position multipliers.

No new market runs required for initial validation.

