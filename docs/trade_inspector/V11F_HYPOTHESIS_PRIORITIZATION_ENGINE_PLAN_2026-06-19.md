# V11F HYPOTHESIS PRIORITIZATION ENGINE PLAN

Date: 2026-06-19
Device: G15 / Workstation
Environment: WSL
Scope: Trade Inspector V11F

## Objective

V11F prioritizes hypotheses using knowledge consistency and knowledge evolution.

V11D reviews internal knowledge consistency.
V11E tracks knowledge maturity and trend.
V11F converts both into a prioritized research queue.

## Input

Primary inputs:

- v11d_knowledge_consistency.csv
- v11e_knowledge_evolution.csv

## Output

- v11f_hypothesis_priorities.csv
- V11F_HYPOTHESIS_PRIORITIZATION_ENGINE_REPORT_2026-06-19.md

## Prioritization Factors

Positive factors:

- consistent knowledge
- improving trend
- validated or developing maturity
- positive knowledge score
- successful validations

Negative factors:

- blocked conflict
- contradiction
- pending replay
- insufficient evidence
- degraded maturity
- declining trend

## Priority Classes

- PRIORITY_HIGH
- PRIORITY_MEDIUM
- WATCHLIST
- DEPRIORITIZE
- BLOCKED

## Guardrail

V11F does not modify strategy logic.
V11F only creates a prioritized research queue.

