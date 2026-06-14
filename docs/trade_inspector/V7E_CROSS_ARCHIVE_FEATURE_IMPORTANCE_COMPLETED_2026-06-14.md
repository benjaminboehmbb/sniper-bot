# V7E CROSS-ARCHIVE FEATURE IMPORTANCE INFRASTRUCTURE - COMPLETED

Date: 2026-06-14
Device: G15 / AR15
Scope: Trade Inspector V7E
Status: Completed and validated on P79A

## Objective

V7E adds cross-archive feature importance infrastructure.

The goal is to prepare feature importance analysis for multiple archived runtime runs.

This is infrastructure preparation only.
It is not statistically robust cross-archive feature importance yet.

## Implementation

Updated file:

tools/trade_inspector/inspect_trades.py

Added CLI option:

--export-cross-archive-feature-importance-dir

Added export:

export_cross_archive_feature_importance(...)

## Method

V7E reuses the existing V5 feature importance logic:

- ML dataset rows
- model-ready rows
- leakage audit
- allowed feature selection
- absolute Pearson correlation
- target-specific feature importance

No model training is performed.

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
  --export-cross-archive-feature-importance-dir outputs/trade_inspector/v7e/P79A_2026-06-14 \
  --archive-id P79A_pre_run_2026-06-10

## Validation Result

PASS

Observed result:

- rows_total: 9
- allowed_features: 32
- targets_evaluated: 9
- importance_rows: 288
- feature_importance_status: WARN
- feature_importance_warning: dataset_too_small_for_reliable_cross_archive_feature_importance

## Output Files

Generated output files:

- cross_archive_feature_importance_v7e.csv
- cross_archive_feature_importance_v7e_manifest.csv
- target-specific cross_archive_feature_importance_v7e_*.csv files
- v7e_cross_archive_feature_importance_summary.md

## Important Limitation

Current data base:

- 1 archive
- 9 trades

Therefore this validates V7E infrastructure only.

The output explicitly marks:

statistical_interpretation_allowed = no

Cross-archive interpretation requires at least:

- 2 archives
- 30 trades

## Next Step

Once additional archives exist, rerun V7C, V7D and V7E against all available archives.

Later expansion:

- V7F cross-archive signal discovery infrastructure
