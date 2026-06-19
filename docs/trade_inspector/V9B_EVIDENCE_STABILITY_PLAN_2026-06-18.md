# V9B EVIDENCE STABILITY PLAN

Date: 2026-06-18
Device: G15 / AR15
Environment: WSL
Scope: Trade Inspector V9B

## Objective

V9B extends V9A by evaluating whether evidence-ranked hypotheses remain stable across multiple archives or repeated evidence runs.

V9A answers:

Which hypotheses are currently strongest?

V9B answers:

Which hypotheses remain consistently strong over time and across archives?

## Why V9B Matters

A hypothesis should not be promoted only because it scores well once.

For strategy development, a useful hypothesis must show:

- repeated support
- stable ranking
- stable evidence score
- low warning level
- consistent actionability
- no collapse across new archives

## Inputs

V9B should consume multiple V9A evidence score CSV files.

Required input format:

- v9a_evidence_scores.csv

Required columns:

- group_key
- group
- count
- evidence_score
- evidence_class
- recommended_action
- warning_level
- reliability_class
- discovery_status
- winrate_edge
- pnl_edge

## Core Outputs

V9B should produce:

- v9b_evidence_stability.csv
- V9B_EVIDENCE_STABILITY_REPORT_2026-06-18.md

## Stability Metrics

For each hypothesis:

- observations
- first_seen_run
- last_seen_run
- mean_evidence_score
- min_evidence_score
- max_evidence_score
- evidence_score_range
- latest_evidence_score
- rank_best
- rank_worst
- rank_latest
- rank_drift
- stable_action_count
- warning_high_count
- validation_priority_count

## Stability Classes

- STABLE_STRONG
- STABLE_MODERATE
- IMPROVING
- DECLINING
- EMERGING
- VANISHED
- UNSTABLE
- INSUFFICIENT_HISTORY

## Interpretation Rules

A hypothesis can only be considered robust if it appears repeatedly.

Single-run evidence remains provisional.

No live strategy modification is allowed from V9B alone.

V9B is a prioritization and research-control layer.

