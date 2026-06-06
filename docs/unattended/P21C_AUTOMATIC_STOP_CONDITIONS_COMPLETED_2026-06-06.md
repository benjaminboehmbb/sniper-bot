# P21C AUTOMATIC STOP CONDITIONS - COMPLETED

Date: 2026-06-06
Device: G15 / AR15
Environment: WSL

## Objective

Add automatic stop-condition classification to the Live L1 runtime control loop.

## Modified File

live_l1/tools/runtime_control_loop.py

## Behavior

The control loop now maps selected FAIL alerts to:

control_state: RECOVERY_REQUIRED
control_action: STOP

## Stop Alert Codes

The following alert codes trigger STOP:

- startup_validation_failed
- reconciliation_failed
- schema_validation_failed
- execution_replay_failed
- bad_json_detected
- missing_required_runtime_file
- runtime_position_mismatch
- unsupported_schema_version
- production_profile_not_enabled

## Validation

### PAPER Test

Expected:

- monitor_status: WARN
- control_state: DEGRADED
- control_action: CONTINUE

Result:

PASS

### PRODUCTION Stop Test

Expected:

- monitor_status: FAIL
- control_state: RECOVERY_REQUIRED
- control_action: STOP
- control_reason: production_profile_not_enabled

Observed:

- monitor_status: FAIL
- control_state: RECOVERY_REQUIRED
- control_action: STOP
- control_reason: production_profile_not_enabled

Result:

PASS

## Safety Note

P21C does not directly terminate a running process.

It writes the required control decision to:

live_state/runtime_control.json

Actual runtime integration is reserved for a later block.

## P21C Result

Automatic stop-condition classification implemented and tested.

Status:

PASS
