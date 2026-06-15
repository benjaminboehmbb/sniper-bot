# V7H BUILT-IN REGRESSION VALIDATION - COMPLETED

Date: 2026-06-15
Device: G15 / AR15
Scope: Trade Inspector V7H
Status: Completed and validated on P79A

## Objective

V7H adds built-in regression validation to the Trade Inspector without introducing external dependencies.

This replaces the need for pytest in the current environment.

## Reason

pytest is not installed in the current virtual environment.

Observed:

python3 -m pytest tests/tools/test_trade_inspector_regression_p79a.py

Result:

No module named pytest

Decision:

Do not add a new dependency.

Use built-in regression validation inside tools/trade_inspector/inspect_trades.py.

## Implementation

Updated file:

tools/trade_inspector/inspect_trades.py

Added CLI option:

--run-regression-tests

Added function:

run_builtin_regression_validation(...)

## Validation Target

Reference archive:

live_logs/archive/P79A_pre_run_2026-06-10

Known baseline:

- trades: 9
- built rows: 9
- signal groups evaluated: 57
- NOT_ACTIONABLE signal groups: 57
- high warning signal groups: 57
- WATCH groups: 6
- global trade rows: 9
- global trade IDs: 9
- root cause groups: 4

## Validation Command

python3 tools/trade_inspector/inspect_trades.py \
  --archive-dir live_logs/archive/P79A_pre_run_2026-06-10 \
  --market-csv data/l1_full_run.csv \
  --archive-id P79A_pre_run_2026-06-10 \
  --run-regression-tests

## Expected Result

REGRESSION: PASS

## Purpose

This check protects the Trade Inspector against accidental regressions in:

- trade loading
- row building
- V6A reliability classification
- V7 global trade ID generation
- root cause attribution

## Current Limitation

The regression baseline is based on P79A only.

It validates reproducibility of the current known reference archive.

It does not validate statistical quality.
