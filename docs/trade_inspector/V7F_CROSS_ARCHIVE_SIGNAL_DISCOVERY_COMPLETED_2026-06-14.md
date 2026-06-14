# V7F CROSS-ARCHIVE SIGNAL DISCOVERY INFRASTRUCTURE - COMPLETED

Date: 2026-06-14
Device: G15 / AR15
Scope: Trade Inspector V7F
Status: Completed and validated on P79A

## Objective

V7F adds cross-archive signal discovery infrastructure.

The goal is to prepare predictive signal discovery for multiple archived runtime runs.

This is infrastructure preparation only.
It is not statistically robust cross-archive signal discovery yet.

## Implementation

Updated file:

tools/trade_inspector/inspect_trades.py

Added CLI option:

--export-cross-archive-signal-discovery-dir

Added export:

export_cross_archive_signal_discovery(...)

## Method

V7F reuses the existing V6/V6A signal discovery logic:

- group edge vs global baseline
- pair-group discovery
- support classification
- reliability classification
- warning-level assignment

## Validation Archive

Archive:

live_logs/archive/P79A_pre_run_2026-06-10

Known contents:

- 9 trades
- 18 audit events
- 4,330,970 regime snapshots

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
- signal_discovery_status: WARN
- signal_discovery_warning: dataset_too_small_for_reliable_cross_archive_signal_discovery

## Output Files

Generated output files:

- cross_archive_signal_discovery_v7f_all.csv
- cross_archive_signal_discovery_v7f_top.csv
- cross_archive_signal_discovery_v7f_manifest.csv
- cross_archive_signal_discovery_v7f_by_*.csv
- v7f_cross_archive_signal_discovery_summary.md

## Important Interpretation

The top observed candidates remain:

- good_atr
- risk_good_at_entry
- entry_atr_signal = 1
- aligned_good_risk

But all are correctly marked as:

- reliability_class = NOT_ACTIONABLE
- warning_level = DATASET_TOO_SMALL
- statistical_interpretation_allowed = no

Therefore these are observations only and not confirmed alpha signals.

## Important Limitation

Current data base:

- 1 archive
- 9 trades

Therefore this validates V7F infrastructure only.

Cross-archive interpretation requires at least:

- 2 archives
- 30 trades

## Current Cross-Archive Coverage

The Trade Inspector now has:

- V7A Cross-Archive Plan
- V7B Archive Registry
- V7C Global Trade Database
- V7D Cross-Archive Root Cause Infrastructure
- V7E Cross-Archive Feature Importance Infrastructure
- V7F Cross-Archive Signal Discovery Infrastructure

## Next Step

Do not add further statistical layers before new Workstation archives exist.

Once additional archives are available, rerun V7C-V7F against all available archives.
