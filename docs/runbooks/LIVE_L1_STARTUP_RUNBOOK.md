# LIVE L1 STARTUP RUNBOOK

Status: Official Operator Procedure
Environment: WSL Only

## Purpose

Standardized startup procedure for Live L1.

This procedure must be followed before every operational run.

## Preconditions

Required:

- WSL environment
- clean repository
- valid runtime configuration
- startup validation passing
- reconciliation passing

## Step 1 - Repository Check

Run:

git status

Expected:

working tree clean

Abort if:

- unknown modifications
- unexpected runtime artifacts
- unresolved merge conflicts

## Step 2 - Startup Validation

Run:

python3 live_l1/tools/startup_validator.py

Expected:

PASS

Abort if:

FAIL

## Step 3 - Operational Health Report

Run:

python3 live_l1/tools/operational_health_report.py

Expected:

OVERALL: PASS

Abort if:

OVERALL: FAIL

## Step 4 - Safe Launch

Run:

L1_STARTUP_RECOVERY=1 \
L1_STARTUP_RECONCILIATION_GATE=1 \
L1_REQUIRE_WSL=1 \
python3 live_l1/tools/safe_launch.py

Expected:

SAFE_LAUNCH: PASS

STARTING LIVE L1

## Step 5 - Verify Runtime

Expected log events:

system_start

clock_tick

state_persisted

No startup failures.

## Startup Success Criteria

Required:

- startup validation PASS
- reconciliation PASS
- health report PASS
- safe launch PASS
- runtime running

## Startup Failure Criteria

Immediate stop:

- startup validation FAIL
- reconciliation FAIL
- startup_reconciliation_failed
- startup_validation_failed
- missing runtime files
- runtime configuration errors

## Source Of Truth

Code is source of truth.

Runbook documents approved operational procedure only.

