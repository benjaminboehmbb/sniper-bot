# V7D CROSS-ARCHIVE ROOT CAUSE SKELETON - COMPLETED

Date: 2026-06-14
Device: G15 / AR15
Scope: Trade Inspector V7D
Status: Completed and validated on P79A

## Objective

V7D adds the first cross-archive root cause infrastructure layer.

The goal is to prepare root cause analysis for multiple archived runtime runs.

This is infrastructure preparation only.
It is not statistically robust cross-archive analysis yet.

## Implementation

Updated file:

tools/trade_inspector/inspect_trades.py

Added CLI option:

--export-cross-archive-root-cause-dir

Added export:

export_cross_archive_root_cause(...)

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
  --export-cross-archive-root-cause-dir outputs/trade_inspector/v7d/P79A_2026-06-14 \
  --archive-id P79A_pre_run_2026-06-10

## Validation Result

PASS

Observed result:

- trades: 9
- root_cause_groups: 4
- cross_archive_root_cause_trades_v7d.csv created
- cross_archive_root_cause_attribution_v7d.csv created
- cross_archive_root_cause_v7d_manifest.csv created
- v7d_cross_archive_root_cause_summary.md created

## Root Cause Groups Observed

Observed groups on P79A:

- early_exit
- entry_filter_quality
- risk_management
- high_adverse_move

## Important Fix During Validation

Initial V7D output created an empty attribution file because the export did not include:

- cause_weights
- opportunity_loss_24h_pct

The export was corrected by carrying these fields into the V7D enriched trade rows.

After the fix, attribution produced 4 root cause groups.

## Important Limitation

Current data base:

- 1 archive
- 9 trades

Therefore this validates V7D infrastructure only.

The output explicitly marks:

statistical_interpretation_allowed = no

Cross-archive interpretation requires at least:

- 2 archives
- 30 trades

## Next Step

Once additional archives exist, rerun V7C and V7D against all available archives.

Later expansion:

- V7E cross-archive feature importance infrastructure
- V7F cross-archive signal discovery infrastructure
