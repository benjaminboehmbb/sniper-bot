# V9G RESEARCH DECISION ENGINE PLAN

Date: 2026-06-18
Device: G15 / AR15
Environment: WSL
Scope: Trade Inspector V9G

## Objective

V9G converts the V9F experiment portfolio into concrete research decisions.

V9A scores evidence.
V9B checks stability.
V9C scores opportunity.
V9D checks consistency.
V9E detects conflicts.
V9F optimizes the experiment portfolio.
V9G decides what should happen next.

## Decision Classes

- RUN_CONTROLLED_VALIDATION
- PREPARE_VALIDATION_DESIGN
- COLLECT_MORE_ARCHIVES
- KEEP_ON_WATCHLIST
- REJECT_FOR_NOW

## Inputs

Primary input:

- v9f_experiment_portfolio.csv

Required columns:

- hypothesis_id
- group
- consistency_score
- conflict_penalty
- portfolio_score
- portfolio_class

## Outputs

- v9g_research_decisions.csv
- V9G_RESEARCH_DECISION_REPORT_2026-06-18.md

## Guardrail

V9G does not change strategy code.

It produces prioritized research decisions only.

