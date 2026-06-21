# V13A HYPOTHESIS INTELLIGENCE ENGINE - SPEC

Date: 2026-06-20
Device: G15 / AR15
Environment: WSL
Project: Sniper-Bot / Trade Inspector

## Objective

V13A transforms the Trade Inspector from research management into research intelligence.

It does not only report hypotheses.
It evaluates their scientific value, relationships, conflicts, novelty, evidence quality, and next best research action.

## Inputs

Primary inputs:

- V11 knowledge base
- V11 hypothesis priorities
- V12 research memory
- V12 autonomous research directives

Expected source files may include:

- v11c_research_knowledge_base.csv
- v11f_hypothesis_priorities.csv
- v12f_research_memory.csv
- v12g_autonomous_research_directives.csv

## Outputs

V13A produces:

- v13a_hypothesis_intelligence.csv
- v13a_relationship_graph.csv
- v13a_dependency_graph.csv
- v13a_conflict_network.csv
- v13a_research_gaps.csv
- v13a_summary.csv
- v13a_manifest.csv
- V13A_HYPOTHESIS_INTELLIGENCE_ENGINE_REPORT_YYYY-MM-DD.md

## Core Concepts

Each hypothesis receives a full intelligence profile:

- identity
- evidence strength
- evidence diversity
- evidence stability
- confidence
- novelty
- information gain
- research coverage
- dependency risk
- conflict severity
- redundancy risk
- recommended next action
- global intelligence score

## Relationship Classes

Allowed relationship classes:

- duplicate
- similar
- parent
- child
- complementary
- contradictory
- dependency
- independent

## Recommendation Classes

Allowed recommendations:

- run_now
- prepare_validation
- collect_more_archives
- merge_with_related
- discard_for_now
- watchlist
- blocked_by_dependency
- resolve_conflict_first
- needs_new_regime_evidence

## Global Intelligence Score

The global intelligence score should combine:

- evidence strength
- evidence stability
- novelty
- expected information gain
- research coverage
- confidence
- relationship quality
- conflict severity
- dependency risk
- estimated research cost

This score is not a trading-performance score.
It is a research-prioritization score.

## Guardrails

V13A must not:

- modify strategy logic
- execute trades
- execute validation runs
- alter V9-V12 outputs
- replace human approval

V13A may only analyze, score, cluster, and recommend.

## Quality Requirements

- Use tools/trade_inspector/common helpers.
- No duplicated CSV helper logic.
- Stable IDs only.
- No position-based IDs.
- ASCII-only.
- Full smoke test required.
- No V13B work before V13A is tested and documented.

## Implementation Decision

V13A should be implemented as:

tools/trade_inspector/build_v13a_hypothesis_intelligence_engine.py

