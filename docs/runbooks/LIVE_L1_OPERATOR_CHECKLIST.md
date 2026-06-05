# LIVE L1 OPERATOR CHECKLIST

Status: Official Operator Checklist

## Before Startup

[ ] Running in WSL

[ ] Repository clean

Command:

git status

Expected:

working tree clean

[ ] Startup validator PASS

Command:

python3 live_l1/tools/startup_validator.py

[ ] Health report PASS

Command:

L1_STARTUP_RECOVERY=1 \
L1_STARTUP_RECONCILIATION_GATE=1 \
python3 live_l1/tools/operational_health_report.py

Expected:

OVERALL: PASS

[ ] Reconciliation PASS

Command:

python3 live_l1/tools/reconcile_runtime_state.py

Expected:

RESULT: PASS

## Startup

[ ] Start only through safe_launch.py

Command:

L1_STARTUP_RECOVERY=1 \
L1_STARTUP_RECONCILIATION_GATE=1 \
L1_REQUIRE_WSL=1 \
python3 live_l1/tools/safe_launch.py

[ ] SAFE_LAUNCH: PASS

[ ] STARTING LIVE L1 observed

## During Runtime

[ ] No startup_validation_failed

[ ] No startup_reconciliation_failed

[ ] state_persisted events continue

[ ] No unexpected runtime stop

## Shutdown

[ ] system_stop observed

[ ] Health report PASS

[ ] Important logs archived if required

## Recovery

[ ] Reconciliation PASS

[ ] Health report PASS

[ ] startup_recovery_applied=1

[ ] Safe launch used

## Incident Handling

[ ] Preserve evidence

[ ] Archive logs and state

[ ] Run diagnostics

[ ] Document root cause

[ ] Reconciliation PASS before restart

