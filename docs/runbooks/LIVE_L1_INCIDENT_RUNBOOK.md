# LIVE L1 INCIDENT RUNBOOK

Status: Official Operator Procedure
Environment: WSL Only

## Purpose

Standardized procedure for handling Live L1 incidents.

Incident examples:

- startup_validation_failed
- startup_reconciliation_failed
- reconciliation RESULT: FAIL
- health report OVERALL: FAIL
- corrupted audit log
- mismatched s2_position
- missing trades_l1
- impossible trade timing
- unexpected runtime stop

## Rule 1 - Stop First

If an incident is detected:

- do not continue runtime
- do not start another run
- do not delete logs
- do not manually edit state files

## Rule 2 - Preserve Evidence

Create an incident archive:

mkdir -p live_logs/archive/YYYY-MM-DD_incident_name

cp live_logs/execution_audit.jsonl live_logs/archive/YYYY-MM-DD_incident_name/ 2>/dev/null || true
cp live_logs/trades_l1.jsonl live_logs/archive/YYYY-MM-DD_incident_name/ 2>/dev/null || true
cp live_logs/l1_paper.log live_logs/archive/YYYY-MM-DD_incident_name/ 2>/dev/null || true
cp live_state/s2_position.jsonl live_logs/archive/YYYY-MM-DD_incident_name/ 2>/dev/null || true
cp live_state/loss_cluster_state.json live_logs/archive/YYYY-MM-DD_incident_name/ 2>/dev/null || true
cp live_state/s4_risk.jsonl live_logs/archive/YYYY-MM-DD_incident_name/ 2>/dev/null || true

## Rule 3 - Run Diagnostics

Run:

python3 live_l1/tools/reconcile_runtime_state.py

Then run:

L1_STARTUP_RECOVERY=1 \
L1_STARTUP_RECONCILIATION_GATE=1 \
python3 live_l1/tools/operational_health_report.py

## Rule 4 - Interpret Result

If reconciliation PASS and health report PASS:

- incident may be external or already resolved
- start only through safe_launch.py

If reconciliation FAIL or health report FAIL:

- do not start runtime
- inspect failed check
- document the issue
- only change code after the cause is understood

## Rule 5 - No Manual State Repair Without Documentation

Do not manually edit:

- execution_audit.jsonl
- s2_position.jsonl
- trades_l1.jsonl
- loss_cluster_state.json

unless:

- cause is understood
- original files are archived
- repair is documented
- post-repair reconciliation passes

## Incident Success Criteria

Incident is resolved only if:

- evidence archived
- root cause documented
- reconciliation PASS
- health report PASS
- safe launch PASS

