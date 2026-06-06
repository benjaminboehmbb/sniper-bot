# P28L TIME-STOP REGRESSION VALIDATION

Date: 2026-06-06
Device: G15 / AR15
Environment: WSL

## Objective

Validate the P28K time-stop state-reset fix on a newly generated runtime log segment.

## Method

A new runtime segment was extracted from live_logs/l1_paper.log after recording the pre-run line count.

Segment path:

live_logs/review_segments/p28l_after_timestop_fix_segment.log

## Run Configuration

Command:

python3 live_l1/tools/safe_launch.py --max-ticks 500

Operational profile:

PAPER

Startup flags:

- L1_STARTUP_RECOVERY=1
- L1_STARTUP_RECONCILIATION_GATE=1
- L1_REQUIRE_WSL=1

## New Segment Result

Execution actions:

- OPEN_LONG: 1
- CLOSE_LONG: 1
- NOOP: 498

Execution reasons:

- BUY_FROM_FLAT: 1
- SELL_CLOSES_LONG: 1
- HOLD_NO_EXECUTION: 498

Time-stop events:

- LONG_TIME_STOP_HIT: 0
- SHORT_TIME_STOP_HIT: 0

## Reconciliation

RESULT: PASS

Details:

- audit_json_valid: PASS
- audit_vs_s2_position: PASS
- audit_vs_trades: PASS
- trade_time_order: PASS
- loss_cluster_state: PASS

## Monitoring

RESULT: PASS

Status:

WARN

Reason:

kill_level_active

## Runtime Control

RESULT: PASS

control_state:

DEGRADED

control_action:

CONTINUE

escalation_level:

WARN

## Interpretation

The new 500-tick segment after the P28K fix did not produce repeated time-stop close events.

The observed close event was a normal SELL_CLOSES_LONG signal exit.

The runtime remained consistent after the run.

## P28L Result

Time-stop regression validation completed.

Status:

PASS
