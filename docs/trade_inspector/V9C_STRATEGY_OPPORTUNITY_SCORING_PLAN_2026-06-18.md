# V9C STRATEGY OPPORTUNITY SCORING PLAN

Date: 2026-06-18
Device: G15 / AR15
Environment: WSL
Scope: Trade Inspector V9C

## Objective

V9C converts evidence-ranked hypotheses into strategy-development opportunities.

V9A answers:

Which hypotheses have evidence?

V9B answers:

Which hypotheses are stable?

V9C answers:

Which hypotheses are worth turning into controlled strategy experiments?

## Core Idea

A hypothesis is not automatically useful just because it has evidence.

V9C evaluates practical opportunity value using:

- evidence strength
- stability class
- support count
- warning level
- expected benefit proxy
- implementation complexity
- risk penalty
- validation priority

## Inputs

Primary input:

- v9a_evidence_scores.csv

Optional future input:

- v9b_evidence_stability.csv

Required V9A columns:

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

## Outputs

- v9c_strategy_opportunities.csv
- V9C_STRATEGY_OPPORTUNITY_REPORT_2026-06-18.md

## Opportunity Classes

- HIGH_VALUE_EXPERIMENT
- MEDIUM_VALUE_EXPERIMENT
- WATCH_ONLY
- REJECT

## Experiment Types

V9C maps hypotheses to experiment types:

- exit_logic_review
- entry_filter_review
- risk_filter_review
- regime_alignment_review
- atr_context_review
- score_threshold_review
- generic_hypothesis_review

## Guardrails

V9C does not modify trading logic.

V9C only recommends controlled validation priorities.

Any recommended opportunity must still be tested through replay or archive validation before live changes.

