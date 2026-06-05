# LIVE L1 P6 STARTUP RECOVERY PLAN
Date: 2026-06-05

## Objective

Introduce automatic runtime state recovery during startup.

The system should resume operation after:

- process restart
- terminal restart
- VM restart
- machine reboot
- unexpected crash

without manual state reconstruction.

---

## Current Capabilities

Already implemented:

P3
Persistent loss cluster state

P4
Execution audit trail

P5
Deterministic execution replay

Current limitation:

Recovery exists as a standalone tool only.

No automatic integration into runtime startup sequence.

---

## Desired Startup Sequence

Current:

startup
    ->
initialize runtime state
    ->
start loop

Target:

startup
    ->
recover execution state
    ->
recover loss cluster state
    ->
initialize runtime state
    ->
start loop

---

## Recovery Sources

Primary:

live_logs/execution_audit.jsonl

Provides:

- position
- side
- entry_price
- entry_timestamp_utc

Secondary:

live_state/loss_cluster_state.json

Provides:

- recent losses
- pause_entries_remaining

---

## Recovery Scope P6

Recover:

position

side

entry_price

entry_timestamp_utc

loss cluster state

Do not recover:

trade history

analytics

reports

snapshots

historical metrics

---

## Runtime Integration Strategy

New startup helper:

recover_runtime_state.py

Responsibilities:

1. replay execution state
2. load loss cluster state
3. populate runtime structures
4. return recovered state

No execution logic.

No trading logic.

No order generation.

---

## Validation Requirement

Validation must prove:

Recovered runtime state
==
Original runtime state

Differences allowed:

none

---

## Planned Deliverables

P6A
Startup recovery design

P6B
recover_runtime_state.py

P6C
Standalone recovery validation

P6D
loop.py integration

P6E
End-to-end restart simulation

---

## Success Criteria

Bot restart.

State recovered automatically.

No manual intervention.

Open position preserved.

Loss cluster state preserved.

System continues operation safely.

