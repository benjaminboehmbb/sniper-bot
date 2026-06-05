# LIVE L1 P5 EXECUTION REPLAY PLAN
Date: 2026-06-05

## Objective

Introduce deterministic execution state recovery.

A running Live-L1 instance should be able to reconstruct its execution state after:

- process restart
- VM restart
- server reboot
- unexpected crash

without requiring manual intervention.

---

## Current Situation

Already available:

1. trades_l1.jsonl
2. execution_audit.jsonl
3. loss_cluster_state.json

Current limitation:

The execution state is primarily held in memory.

A restart may lose:

- open position state
- side
- entry price
- entry timestamp
- execution context

depending on restart timing.

---

## P5 Goal

Recover the last known execution state entirely from persisted artifacts.

Target properties:

- deterministic
- reproducible
- restart-safe
- audit-compatible

---

## Candidate Sources

### Source A

live_logs/trades_l1.jsonl

Provides:

- closed trades
- pnl
- timestamps
- trade lifecycle history

Limitation:

Does not represent currently open positions.

---

## Source B

live_logs/execution_audit.jsonl

Provides:

- ENTRY_ACCEPTED
- EXIT_EXECUTED
- ENTRY_BLOCKED
- LOSS_CLUSTER_* events

Can reconstruct execution timeline.

Potential primary replay source.

---

## Source C

live_state/loss_cluster_state.json

Provides:

- recent losses
- pause_entries_remaining

Required for exact gate restoration.

---

## Replay Strategy

Read execution_audit.jsonl sequentially.

Apply state transitions:

ENTRY_ACCEPTED:

FLAT -> LONG
FLAT -> SHORT

EXIT_EXECUTED:

LONG -> FLAT
SHORT -> FLAT

ENTRY_BLOCKED:

no position change

LOSS_CLUSTER_*:

restore gate state

Final state after replay becomes recovered execution state.

---

## Expected Recoverable State

position

side

entry_price

entry_timestamp_utc

loss_cluster_state

pause_entries_remaining

---

## Validation Requirement

Replay state must equal live state.

Validation method:

1. capture live state
2. replay from logs
3. compare fields
4. zero differences allowed

---

## Planned Deliverables

P5A
Replay design

P5B
replay_execution_state.py

P5C
deterministic replay validation

P5D
restart recovery documentation

---

## Success Criteria

After restart:

execution state reconstructed automatically

without manual input

and matches original runtime state exactly.
