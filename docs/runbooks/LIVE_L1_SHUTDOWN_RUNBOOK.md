# LIVE L1 SHUTDOWN RUNBOOK

Status: Official Operator Procedure
Environment: WSL Only

## Purpose

Standardized shutdown procedure for Live L1.

## Step 1 - Stop Runtime Cleanly

Preferred:

- allow configured max run limit to stop the loop
- avoid forced termination when possible

Abort unsafe shutdown if:

- state is currently being written
- logs are mid-write
- recovery test is running

## Step 2 - Confirm Stop Event

Run:

grep -n "system_stop" live_logs/l1_paper.log | tail -5

Expected:

system_stop

## Step 3 - Run Health Report

Run:

L1_STARTUP_RECOVERY=1 \
L1_STARTUP_RECONCILIATION_GATE=1 \
python3 live_l1/tools/operational_health_report.py

Expected:

OVERALL: PASS

## Step 4 - Archive Important Trade Logs If Needed

If the run produced important trade data, archive before the next run.

Example:

mkdir -p live_logs/archive/YYYY-MM-DD_run_name

cp live_logs/trades_l1.jsonl live_logs/archive/YYYY-MM-DD_run_name/
cp live_logs/execution_audit.jsonl live_logs/archive/YYYY-MM-DD_run_name/
cp live_state/s2_position.jsonl live_logs/archive/YYYY-MM-DD_run_name/

## Step 5 - Git Check

Run:

git status --short

Expected:

no unexpected source-code changes

Runtime artifacts should be ignored.

## Shutdown Success Criteria

Required:

- system_stop observed
- health report PASS
- important logs archived if needed
- no unexpected source-code changes

