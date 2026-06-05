# P17B BACKUP POLICY

Date: 2026-06-05
Device: G15 / AR15
Environment: WSL

## Purpose

Define the backup policy for Live L1 runtime and disaster recovery artifacts.

## Backup Scope

Every operational backup must include Tier 1 artifacts:

- live_logs/execution_audit.jsonl
- live_logs/trades_l1.jsonl
- live_state/s2_position.jsonl
- live_state/loss_cluster_state.json
- live_state/s4_risk.jsonl

Diagnostic backups should include Tier 2 artifacts:

- live_logs/l1_paper.log
- live_logs/trade_lifecycle_snapshots.csv
- live_logs/passive_shadow_close_accounting.csv
- live_logs/passive_shadow_entry_multipliers.csv
- live_logs/passive_shadow_risk_snapshots.csv
- live_logs/trades_l1_auto_analysis.csv

## Backup Timing

Create a backup:

- before every intentional reset
- after every important operational drill
- after every incident
- before any manual state repair
- before switching devices
- before longer paper/live operation

## Backup Location

Primary local backup location:

backups/live_l1/YYYY-MM-DD_HH-MM-SS_label/

## Backup Rules

- backups are local runtime artifacts
- backups are not committed to Git
- backups must preserve original filenames
- backups must include a manifest file
- backups must include backup timestamp
- backups must include source paths
- backups must be validated after creation

## Restore Rule

A backup is only valid if restored files pass:

- reconcile_runtime_state.py
- operational_health_report.py

## P17B Result

Backup policy defined.

Status:

PASS

