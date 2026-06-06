# P19C ALERT RULES

Date: 2026-06-06
Device: G15 / AR15
Environment: WSL
Status: Draft / P19C

## Objective

Define deterministic alert rules for Live L1 monitoring.

P19C defines alert semantics before extending monitor_runtime.py.

## Alert Severity Levels

Allowed severities:

INFO
WARN
FAIL

## Severity Meaning

INFO:

Informational runtime condition. No operator action required.

WARN:

Runtime is usable, but operator review is required before unattended operation.

FAIL:

Runtime state must not be trusted. Do not start or continue unattended operation.

## FAIL Alerts

The following alerts must produce overall status FAIL:

startup_validation_failed

Triggered when startup_validator.py fails.

reconciliation_failed

Triggered when reconcile_runtime_state.py fails.

schema_validation_failed

Triggered when validate_runtime_schema.py fails.

execution_replay_failed

Triggered when execution replay detects bad JSON or invalid replay state.

bad_json_detected

Triggered when required JSON/JSONL runtime files contain malformed records.

missing_required_runtime_file

Triggered when required runtime files are missing or empty.

runtime_position_mismatch

Triggered when audit replay and persisted S2 position disagree.

unsupported_schema_version

Triggered when a runtime artifact contains an unsupported schema_version.

## WARN Alerts

The following alerts must produce overall status WARN if no FAIL alert exists:

loss_cluster_active

Triggered when loss_cluster_state.pause_entries_remaining > 0.

kill_level_active

Triggered when s4_risk.kill_level is not NONE.

stale_runtime_state

Triggered when runtime state has not advanced beyond a defined freshness threshold.

monitoring_degraded

Triggered when optional diagnostic fields are missing but core safety checks still pass.

## INFO Alerts

The following alerts may be emitted without changing overall status from PASS:

runtime_flat

Triggered when position is FLAT.

no_recent_trade

Triggered when no recent trade is present but this is not a safety issue.

legacy_schema_v0_present

Triggered when legacy_v0 rows are detected but still supported.

## Initial Rule Priority

Overall status resolution:

1. Any FAIL alert -> FAIL
2. Else any failed required check -> FAIL
3. Else any WARN alert -> WARN
4. Else any WARN check -> WARN
5. Else PASS

## Required Initial Implementation

Extend monitor_runtime.py to make alert rules explicit and centralized.

Required functions:

- add_alert()
- classify_status()
- evaluate_alert_rules()

The tool must continue to write:

live_state/monitor_status.json

The tool must remain:

- local
- deterministic
- file-based
- ASCII-only
- read-only for source runtime files

## P19C Acceptance Criteria

P19C is accepted when:

- alert rules are documented
- monitor_runtime.py contains explicit alert classification logic
- current runtime produces WARN because kill_level=SOFT
- all core checks remain PASS
- monitor_status.json is written successfully
- no runtime behavior outside monitoring is changed

## P19C Result

Alert rules defined.

Status:

PASS
