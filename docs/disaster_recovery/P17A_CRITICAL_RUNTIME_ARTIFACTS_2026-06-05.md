# P17A CRITICAL RUNTIME ARTIFACTS

Date: 2026-06-05
Device: G15 / AR15
Environment: WSL

## Purpose

Identify runtime artifacts required for backup, restore and disaster recovery planning.

## Current State Check

Current reconciliation result:

PASS

Current operational health result:

OVERALL: PASS

Current recoverable runtime position:

FLAT

Current trade log count:

2

Current loss cluster status:

valid

## Tier 1 - Critical Recovery Artifacts

These files are required to reconstruct and validate runtime state.

- live_logs/execution_audit.jsonl
- live_logs/trades_l1.jsonl
- live_state/s2_position.jsonl
- live_state/loss_cluster_state.json
- live_state/s4_risk.jsonl

Policy:

- must be included in every operational backup
- must be restored together
- must pass reconciliation after restore
- must not be edited manually without archived copy and documentation

## Tier 2 - Diagnostic Artifacts

These files are not strictly required for state recovery but are important for incident analysis.

- live_logs/l1_paper.log
- live_logs/trade_lifecycle_snapshots.csv
- live_logs/passive_shadow_close_accounting.csv
- live_logs/passive_shadow_entry_multipliers.csv
- live_logs/passive_shadow_risk_snapshots.csv
- live_logs/trades_l1_auto_analysis.csv

Policy:

- should be included in diagnostic backups
- useful for post-incident analysis
- not authoritative for recovery state

## Tier 3 - Local Archives

Directory:

- live_logs/archive/

Policy:

- local long-term run archive
- not committed to Git
- not used as current source of truth
- may be copied to external storage manually

## Recovery Source Of Truth

Primary recovery chain:

execution_audit.jsonl
-> replay_execution_state.py
-> recovered position

Consistency validation:

execution_audit.jsonl
+ s2_position.jsonl
+ trades_l1.jsonl
+ loss_cluster_state.json
-> reconcile_runtime_state.py

## P17A Result

Critical runtime artifacts identified.

Status:

PASS

