# V6A SIGNAL DISCOVERY RELIABILITY LAYER - COMPLETED

Date: 2026-06-14
Device: G15 / AR15
Scope: Trade Inspector V6A
Status: Completed and validated on P79A

## Objective

V6A adds a reliability layer to the existing V6 Predictive Signal Discovery Engine.

The goal is to prevent weak-sample observations from being misinterpreted as actionable trading signals.

## Implementation

Updated file:

tools/trade_inspector/inspect_trades.py

Added helper functions:

- classify_signal_support(...)
- classify_signal_reliability(...)

Added output fields:

- support_count
- minimum_required_support
- support_class
- reliability_score
- reliability_class
- warning_level

## Validation Archive

Archive:

live_logs/archive/P79A_pre_run_2026-06-10

Known contents:

- 9 trades
- 18 audit events
- 4,330,970 regime snapshots

## Validation Command

python3 tools/trade_inspector/inspect_trades.py \
  --archive-dir live_logs/archive/P79A_pre_run_2026-06-10 \
  --market-csv data/l1_full_run.csv \
  --export-signal-discovery-dir outputs/trade_inspector/v6a/P79A_2026-06-14

## Validation Result

PASS

Observed result:

- rows_total: 9
- groups_evaluated: 57
- promising_groups: 0
- watch_groups: 6
- low_support_groups: 36
- not_actionable_groups: 57
- watch_only_groups: 0
- actionable_candidate_groups: 0
- high_warning_groups: 57

## Interpretation

All 57 evaluated groups are correctly classified as:

NOT_ACTIONABLE

Reason:

The dataset is too small for reliable signal discovery.

This is the desired behavior.

The V6 observations such as:

- good_atr
- risk_good_at_entry
- entry_atr_signal = 1
- aligned_good_risk

remain observations only.

They must not be interpreted as confirmed alpha signals.

## Important Limitation

Current data base:

- 1 archive
- 9 trades

Therefore V6A validates reliability handling only.

It does not create statistically reliable trading conclusions.

## Next Step

Once the Workstation run creates additional archives and more trades, rerun V6A and verify whether any groups move from:

NOT_ACTIONABLE

to:

WATCH_ONLY

or:

ACTIONABLE_CANDIDATE
