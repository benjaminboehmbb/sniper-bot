# P19A MONITORING STATE MODEL

Date: 2026-06-06
Device: G15 / AR15
Environment: WSL
Status: Draft / P19A

## Objective

Define the machine-readable Live L1 monitoring state model before implementing continuous monitoring.

P19A introduces no runtime behavior change.

## Source Systems

The monitoring state must be derived from existing validated infrastructure only:

- startup_validator.py
- operational_health_report.py
- reconcile_runtime_state.py
- replay_execution_state.py
- validate_runtime_schema.py
- live_state/s2_position.jsonl
- live_state/s4_risk.jsonl
- live_logs/execution_audit.jsonl
- live_logs/trades_l1.jsonl
- live_state/loss_cluster_state.json

## Output File

Planned monitoring status file:

live_state/monitor_status.json

This file is a runtime artifact and must not be committed to Git.

## Schema Version

Initial monitoring schema:

schema_version: 1

## Top-Level Fields

Required fields:

- schema_version
- generated_utc
- status
- status_reason
- checks
- runtime
- alerts
- source_files

## Status Values

Allowed status values:

- PASS
- WARN
- FAIL

Meaning:

PASS:
All required safety checks passed.

WARN:
Runtime is usable, but non-critical degradation or missing optional data was detected.

FAIL:
Runtime must not be trusted for unattended operation.

## Required Checks

The checks object must contain:

startup_validation:
- status: PASS/WARN/FAIL
- detail: text

reconciliation:
- status: PASS/WARN/FAIL
- detail: text

schema_validation:
- status: PASS/WARN/FAIL
- detail: text

execution_replay:
- status: PASS/WARN/FAIL
- detail: text

s2_state:
- status: PASS/WARN/FAIL
- detail: text

s4_risk:
- status: PASS/WARN/FAIL
- detail: text

trades_log:
- status: PASS/WARN/FAIL
- detail: text

loss_cluster_state:
- status: PASS/WARN/FAIL
- detail: text

## Runtime Fields

The runtime object must contain:

- position
- side
- entry_price
- entry_timestamp_utc
- trade_count
- last_trade_timestamp_utc
- last_tick_id
- last_timestamp_utc
- kill_level
- cooldown_until_utc
- loss_cluster_pause_entries_remaining

## Alert Model

The alerts field must be a list.

Each alert must contain:

- severity
- code
- detail

Allowed severities:

- INFO
- WARN
- FAIL

Initial alert codes:

- startup_validation_failed
- reconciliation_failed
- schema_validation_failed
- execution_replay_failed
- bad_json_detected
- missing_required_runtime_file
- runtime_position_mismatch
- unsupported_schema_version
- loss_cluster_active
- kill_level_active
- stale_runtime_state

## Source Files

The source_files object must contain absolute or repo-relative paths for:

- execution_audit
- trades
- s2_position
- s4_risk
- loss_cluster_state
- monitor_status

## Initial PASS Criteria

monitor_status.json may only report status PASS if:

- startup validation passes
- reconciliation passes
- schema validation passes
- execution replay has zero bad JSON lines
- s2_position is readable
- s4_risk is readable
- trades_l1 is readable
- loss_cluster_state is readable or missing_allowed according to current policy

## Initial FAIL Criteria

monitor_status.json must report status FAIL if:

- startup validation fails
- reconciliation fails
- schema validation fails
- execution replay detects bad JSON lines
- required runtime state contains malformed JSON
- unsupported schema_version is detected
- audit and s2 position disagree

## Design Decision

P19A intentionally avoids:

- background daemons
- external services
- Prometheus
- Grafana
- databases
- multithreading
- broker/exchange integration

Reason:

The current Live L1 infrastructure is file-based, deterministic and already validated through recovery, reconciliation, backup and schema-versioning.

The first monitoring layer should therefore remain simple, deterministic, local and testable.

## Planned Next Step

P19B Monitoring Snapshot Generator

Planned implementation file:

live_l1/tools/monitor_runtime.py

Planned output:

live_state/monitor_status.json

## P19A Result

Monitoring state model defined.

Status:

PASS
