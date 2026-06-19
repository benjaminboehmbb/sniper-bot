# V9F EXPERIMENT PORTFOLIO OPTIMIZER PLAN

Date: 2026-06-18
Device: G15 / AR15
Environment: WSL
Scope: Trade Inspector V9F

## Objective

V9F selects the best portfolio of future validation experiments.

Instead of evaluating hypotheses independently, V9F chooses an optimized experiment portfolio.

## Inputs

V9A
- evidence

V9B
- stability

V9C
- opportunity

V9D
- consistency

V9E
- conflicts
- redundancies
- synergies

## Optimization Targets

maximize

- expected information gain
- evidence quality
- stability
- consistency
- diversity

minimize

- conflicts
- redundancy
- validation cost
- engineering effort

## Outputs

- v9f_experiment_portfolio.csv
- V9F_EXPERIMENT_PORTFOLIO_REPORT_2026-06-18.md

## Portfolio Classes

PRIORITY_1
PRIORITY_2
WATCHLIST
REJECT

## Guardrail

V9F prioritizes validation experiments.

It never changes live strategy logic.

