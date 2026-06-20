# V9F/V9G ARCHITECTURE REVIEW PATCH

Date: 2026-06-20
Device: G15 / AR15
Environment: WSL
Branch: main

## Scope

Reviewed and patched:

- tools/trade_inspector/build_v9f_experiment_portfolio_optimizer.py
- tools/trade_inspector/build_v9g_research_decision_engine.py

## Reason

The V9 architecture review identified a relevant design issue:

V9F/V9G used rank-order hypothesis IDs such as H001/H002/H003 as effective identifiers.

This was unsafe because V9D and V9E can derive hypotheses from different ordering contexts. If ordering changes, penalties or decisions can be mapped to the wrong hypothesis.

## Changes

V9F now:

- uses stable content-derived hypothesis IDs
- keeps legacy rank IDs separately as legacy_rank_id
- joins V9E conflict evidence by group_key/group natural key
- preserves V9D context columns
- writes richer portfolio context for downstream modules

V9G now:

- preserves hypothesis_id, group_key, stability, consistency and conflict context
- adds v10_readiness
- adds next_required_input
- produces clearer research decisions for V10 handoff

## Smoke Test

Executed successfully:

- V9F portfolio optimizer
- V9G research decision engine

Inputs:

- outputs/trade_inspector/v9d/smoke_consistency_2026-06-18/v9d_cross_archive_consistency.csv
- outputs/trade_inspector/v9e/smoke_conflict_engine_2026-06-18/v9e_hypothesis_conflicts.csv

Outputs:

- outputs/trade_inspector/v9_review_patch_2026-06-20/v9f_experiment_portfolio.csv
- outputs/trade_inspector/v9_review_patch_2026-06-20/v9g_research_decisions.csv

Result:

- V9F rows: 3
- V9G rows: 3
- Syntax check: PASS
- Smoke test: PASS

## Review Decision

This patch is accepted as a functional architecture correction, not a cosmetic refactor.

Remaining repeated helper code across V9-V12 should be reviewed later as a consolidated cross-version utility refactor after V10-V12 review.
