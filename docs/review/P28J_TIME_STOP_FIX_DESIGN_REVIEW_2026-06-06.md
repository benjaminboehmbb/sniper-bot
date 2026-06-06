# P28J TIME-STOP FIX DESIGN REVIEW

Date: 2026-06-06
Device: G15 / AR15
Environment: WSL

## Objective

Design the fix for repeated LONG_TIME_STOP_HIT / SHORT_TIME_STOP_HIT close events before changing code.

No runtime code is changed in this step.

## Background

P28F reconstructed 559 paper trades from live_logs/l1_paper.log.

P28G detected 37 bad close events.

P28H narrowed the issue to time-stop close events.

P28I inspected source code and found that the time-stop branches in live_l1/core/execution.py return close decisions without resetting the persisted S2 position to FLAT.

## Root Cause

The function _reset_to_flat(state) exists in live_l1/core/execution.py.

It correctly resets:

- position
- side
- size
- position_size
- entry_price
- entry_timestamp_utc

However, the LONG_TIME_STOP_HIT and SHORT_TIME_STOP_HIT branches do not call _reset_to_flat(state) before returning CLOSE_LONG / CLOSE_SHORT.

As a result:

- state.s2_position.position may remain LONG or SHORT
- entry_timestamp_utc may remain set
- duration remains above the time-stop threshold
- the same time-stop condition can fire again on the next tick

## Affected Code Areas

File:

live_l1/core/execution.py

Affected branches:

- LONG_TIME_STOP_HIT
- SHORT_TIME_STOP_HIT

Approximate source locations from P28I:

- LONG_TIME_STOP_HIT block around line 610
- SHORT_TIME_STOP_HIT block around line 655

## Proposed Fix

Add:

_reset_to_flat(state)

inside both time-stop close branches after:

- _log_closed_trade(...)
- _append_audit_event(...)

and before:

- return ExecutionDecision(...)

## Fix Scope

Minimal.

Only modify:

live_l1/core/execution.py

Do not modify:

- strategy logic
- signal logic
- monitoring logic
- recovery logic
- reconciliation logic
- runtime control logic

## Expected Behavior After Fix

After a LONG_TIME_STOP_HIT:

- trade is logged
- audit event is written
- S2 position becomes FLAT
- side becomes empty
- size becomes 0.0
- position_size becomes 0.0
- entry_price becomes None
- entry_timestamp_utc becomes empty
- next tick cannot repeat LONG_TIME_STOP_HIT unless a new long position is opened

After a SHORT_TIME_STOP_HIT:

- same behavior for short positions

## Regression Risk

Low.

Reason:

The patch uses an existing internal reset function.

The same reset behavior is already required by the logical semantics of a close event.

## Validation Plan

### Step 1

Static compile:

python3 -m py_compile live_l1/core/execution.py

### Step 2

Targeted source check:

grep -n "_reset_to_flat(state)" live_l1/core/execution.py

Expected:

_reset_to_flat(state) appears in both time-stop branches.

### Step 3

Short safe-launch smoke test:

python3 live_l1/tools/safe_launch.py --max-ticks 20

Expected:

RUNTIME_RC: 0

### Step 4

Reconciliation:

python3 live_l1/tools/reconcile_runtime_state.py

Expected:

RESULT: PASS

### Step 5

Monitoring:

python3 live_l1/tools/monitor_runtime.py

Expected:

RESULT: PASS

### Step 6

Repeat P28H audit on current log or targeted test log.

Expected after new runtime segment:

No new repeated time-stop close sequence.

## Acceptance Criteria

P28K implementation is accepted only if:

- code compiles
- safe launch passes
- reconciliation passes
- monitoring passes
- no repeated time-stop close behavior appears in newly generated runtime segment
- no unrelated files are modified

## Decision

Fix is approved for implementation.

Proceed to:

P28K Time-Stop Fix Implementation

## P28J Result

Design review completed.

Status:

PASS
