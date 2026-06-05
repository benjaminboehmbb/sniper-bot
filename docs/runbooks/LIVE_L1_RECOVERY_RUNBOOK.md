# LIVE L1 RECOVERY RUNBOOK

Status: Official Operator Procedure
Environment: WSL Only

## Purpose

Standardized recovery procedure after restart, interruption, or suspected state inconsistency.

## Step 1 - Do Not Start Runtime Immediately

Do not run live loop directly.

Do not bypass safe_launch.py.

## Step 2 - Run Reconciliation

Run:

python3 live_l1/tools/reconcile_runtime_state.py

Expected:

RESULT: PASS

If FAIL:

- do not start runtime
- inspect failed check
- preserve logs
- document incident

## Step 3 - Run Health Report

Run:

L1_STARTUP_RECOVERY=1 \
L1_STARTUP_RECONCILIATION_GATE=1 \
python3 live_l1/tools/operational_health_report.py

Expected:

OVERALL: PASS

If FAIL:

- do not start runtime
- archive current live_logs and live_state
- investigate before further action

## Step 4 - Recovery Startup

Run only through safe launch:

L1_STARTUP_RECOVERY=1 \
L1_STARTUP_RECONCILIATION_GATE=1 \
L1_REQUIRE_WSL=1 \
python3 live_l1/tools/safe_launch.py

Expected:

SAFE_LAUNCH: PASS

startup_recovery_applied=1

## Step 5 - Verify Recovered State

Check log:

grep -n "startup_recovery" live_logs/l1_paper.log | tail -5

Expected:

startup_recovery_applied=1

No startup_reconciliation_failed.

No startup_validation_failed.

## Recovery Success Criteria

Required:

- reconciliation PASS
- health report PASS
- safe launch PASS
- startup recovery applied
- runtime continues only after checks

## Recovery Failure Criteria

Immediate stop:

- RESULT: FAIL from reconciliation
- OVERALL: FAIL from health report
- startup_reconciliation_failed
- startup_validation_failed
- missing or corrupted audit log
- mismatch between audit and s2_position

