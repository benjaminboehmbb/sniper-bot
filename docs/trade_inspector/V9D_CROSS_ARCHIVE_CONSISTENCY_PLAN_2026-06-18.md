# V9D CROSS-ARCHIVE CONSISTENCY PLAN

Date: 2026-06-18
Device: G15 / AR15
Environment: WSL
Scope: Trade Inspector V9D

## Objective

V9D evaluates whether hypotheses behave consistently across repeated evidence or stability runs.

V9A ranks evidence.
V9B tracks evidence stability.
V9C converts hypotheses into strategy opportunities.
V9D evaluates cross-run consistency.

## Purpose

A useful strategy hypothesis should not only score well once.

It should show:

- repeated appearance
- stable evidence class
- stable recommended action
- stable warning level
- limited score volatility
- limited rank drift
- no collapse into DO_NOT_ACT

## Input

Primary input:

- v9b_evidence_stability.csv

Optional future input:

- v9a_evidence_scores.csv snapshots
- v9c_strategy_opportunities.csv snapshots

Required columns:

- group_key
- group
- observations
- mean_evidence_score
- latest_evidence_score
- evidence_score_range
- evidence_score_delta
- rank_best
- rank_worst
- rank_latest
- rank_drift
- latest_evidence_class
- latest_recommended_action
- latest_warning_level
- high_warning_count
- validation_priority_count
- stable_action_count
- stability_class

## Output

- v9d_cross_archive_consistency.csv
- V9D_CROSS_ARCHIVE_CONSISTENCY_REPORT_2026-06-18.md

## Consistency Classes

- CONSISTENT_STRONG
- CONSISTENT_MODERATE
- CONSISTENT_WATCH
- INCONSISTENT
- INSUFFICIENT_HISTORY
- REJECT

## Guardrails

V9D does not approve live strategy changes.

It only identifies hypotheses with repeatable behavior and controlled validation potential.

