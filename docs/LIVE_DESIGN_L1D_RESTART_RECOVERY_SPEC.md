LIVE DESIGN – L1-D Restart & Recovery Specification
Purpose

This document defines the restart and recovery behavior of the L1 paper-trading system.

Goal:

The system must be able to restart deterministically after a crash or manual restart without producing:

duplicate trades

inconsistent state

undefined risk conditions

This specification applies to L1 Paper Trading only.

Recovery Principles

The recovery design follows two strict rules:

Rule 1 — State is the source of truth for bot state

The following must always be reconstructed from live_state/:

position state

risk state

last processed snapshot marker

Rule 2 — Market feed is the source of truth for new market data

After restart:

historical decisions are not reconstructed

the system only processes new snapshots

Logs are audit only and must never be used for recovery.

Recovery Modes

Exactly two startup modes exist.

1 Clean Init

Occurs when:

live_state/ does not exist

state files are empty

state schema is incompatible

Behavior:

position = FLAT
risk_state = default
snapshot_marker = NONE

A log entry must indicate:

recovery_mode=clean_init
2 Resume Recovery

Occurs when valid state files exist.

Behavior:

position state restored

risk state restored

last snapshot marker restored

processing continues with next snapshot

Log entry:

recovery_mode=resume
State Files

The following files define the L1 system state.

Directory:

live_state/
Position State

File:

s2_position.jsonl

Required fields:

position_status
position_side
entry_price
entry_timestamp_utc
position_size
last_intent_id
snapshot_id

Allowed values:

position_status = flat | open
position_side = long | short

Recovery rule:

If file is missing or invalid:

position_status = flat

Never attempt to reconstruct position from logs.

Risk State

File:

s4_risk.jsonl

Required fields:

kill_level
trades_6h
trades_today
last_trade_timestamp_utc

Allowed kill levels:

NONE
SOFT
HARD
EMERGENCY

If risk state cannot be loaded:

kill_level = SOFT

This ensures fail-safe behavior.

Snapshot Progress Marker

To prevent duplicate processing, the system must store:

last_snapshot_id
last_timestamp_utc

These markers indicate the last successfully processed market snapshot.

A snapshot is considered processed only after state persistence.

Restart Behavior

Startup procedure must follow this exact order.

Step 1

Load state:

load_or_init_state()
Step 2

Validate state integrity.

Checks include:

valid schema

valid kill_level

position consistency

If validation fails:

fallback to clean_init
Step 3

Log recovery mode:

recovery_mode=clean_init
or
recovery_mode=resume
Step 4

Initialize market feed.

The feed must continue after the last processed snapshot marker.

Step 5

Enter normal loop processing.

No historical replay occurs.

Fail-Safe Rules

If any of the following occurs:

corrupted state file

invalid schema

missing snapshot marker

inconsistent position state

The system must fall back to:

position = FLAT
kill_level = SOFT

A warning log must be written.

The system must never guess state.

Consistency Checks

The following conditions must hold during recovery.

Position checks:

position_status=flat → entry_price must be null
position_status=open → entry_price must exist

Risk checks:

kill_level must be valid enum

Snapshot checks:

last_snapshot_id must exist
last_timestamp_utc must exist

If any check fails:

trigger clean_init
What L1-D Does NOT Implement

L1-D does not yet include:

exchange reconciliation

trade replay

order reconstruction

historical log reconstruction

Those features belong to later execution phases.

Acceptance Criteria

L1-D is considered complete when the following tests succeed.

Test 1

Start system with no state.

Expected:

clean_init
Test 2

Restart with valid state.

Expected:

resume recovery
Test 3

Restart with open position state.

Expected:

Position restored correctly.

Test 4

Restart with risk state.

Expected:

Kill level restored.

Test 5

Restart with corrupted state.

Expected:

fail-safe clean init
Test 6

Restart immediately after last tick.

Expected:

No duplicate decision.

Summary

L1-D ensures that the system:

can restart safely

restores its internal state

never creates duplicate decisions

never guesses unknown state

The design principle is:

State reconstructs bot state.
Market feed provides new data.
When uncertain → fail safe.