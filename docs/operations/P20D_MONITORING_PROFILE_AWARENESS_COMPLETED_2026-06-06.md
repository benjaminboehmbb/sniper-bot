# P20D MONITORING PROFILE AWARENESS - COMPLETED

Date: 2026-06-06
Device: G15 / AR15
Environment: WSL

## Objective

Make Live L1 monitoring aware of operational profiles.

## Modified File

live_l1/tools/monitor_runtime.py

## Implemented Behavior

monitor_runtime.py now includes the active operational profile in monitor_status.json.

The active profile is read from:

L1_OPERATIONAL_PROFILE

Default:

PAPER

## Validated Behavior

### PAPER

Command:

L1_OPERATIONAL_PROFILE=PAPER python3 live_l1/tools/monitor_runtime.py

Observed:

status: WARN
status_reason: warn_alert_present

Reason:

kill_level=SOFT

Profile output:

profile: PAPER

Result:

PASS

### PRODUCTION

Command:

L1_OPERATIONAL_PROFILE=PRODUCTION python3 live_l1/tools/monitor_runtime.py

Observed:

status: FAIL
status_reason: fail_alert_present

Alert:

production_profile_not_enabled

Profile output:

profile: PRODUCTION

Result:

PASS

## Safety Note

PRODUCTION remains blocked and is not enabled for operation.

## P20D Result

Monitoring profile awareness implemented and tested.

Status:

PASS
