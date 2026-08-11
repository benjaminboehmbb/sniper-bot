# Pre-IU-4 S4 Kill-Transition Evidence — 2026-08-09

## Status

**IMPLEMENTED AND LOCALLY VERIFIED; INACTIVE PRE-IU-4 CONTRACT**

Branch: `codex/pre-iu4-s4-kill-transition-2026-08-09`

IU-4, Exchange, and Live remain locked. The atomic coordinator remains absent
from the active L1 loop. This X1-only unit sends no orders and changes no
accepted PEE profile value.

## Contract added

`S4KillTransitionV1` makes every S4 kill-level change an explicit atomic
transaction. A transition requires:

- unique transition event ID;
- exact expected current and target kill levels;
- non-empty reason code;
- non-empty authorization reference;
- canonical UTC whole-second timestamp;
- non-negative tick ID.

`NONE`, `SOFT`, `HARD`, and `EMERGENCY` are the only accepted levels. A
same-level event is rejected because it is not a state transition.

Escalation and de-escalation use the same durable path. De-escalation is never
implicit: the caller must name the expected current level and provide a new
reason and authorization reference.

## Atomic and recovery boundary

The `KILL` transaction is written to the existing immutable coordinator WAL
before the aggregate snapshot advances. Its complete before/after states prove
that position, Paper Account, and throttle are byte-logically unchanged while
the S4 state and transaction head advance together.

- interruption after WAL write blocks entries until recovery;
- recovery publishes the recorded complete state exactly once;
- an identical retry is idempotent;
- a changed retry with the same event ID is a journal conflict;
- stale expected kill level, time/tick regression, corrupt transition payload,
  broken journal chain, and inconsistent S4 reproduction fail closed.

The aggregate schema remains V1. `kill_transition_count` is derived as total
atomic transactions minus accepted entries minus settlements, so no redundant
counter or snapshot migration was introduced. The transaction V1 record gains
an optional `kill_transition` object; older OPEN/CLOSE records without that key
remain readable as `None`.

## Safety invariants

- OPEN and CLOSE still cannot silently change the kill level.
- KILL cannot change S2 position, Paper Account, or throttle.
- Any non-`NONE` kill level blocks entries with a stable S4 reason code.
- S4 always permits exits, including while a kill transition occurs with an
  open position and while reconciliation is unhealthy.
- Clearing a kill does not override other blockers: Account, throttle, and
  open-position reasons are deterministically recomputed.
- Every state binds the exact S2, Account, throttle, transaction sequence, and
  journal head fingerprints/identities.

## Verification

```text
python3 -m unittest tests.live_l1.test_paper_atomic_coordinator

Ran 23 tests — OK
```

```text
python3 -m unittest discover -s tests/live_l1 -p 'test_*.py'

Ran 185 tests — OK
```

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover \
  -s tests/regression -p 'test_*.py'

Ran 170 tests — OK
```

Static import search returned no active `live_l1` importer of
`live_l1.state.paper_atomic_coordinator`.

The new cases cover escalation, authorized de-escalation, transition while
OPEN, missing authorization/reason, same-level rejection, stale expected
state, crash recovery, idempotent retry, conflicting duplicate, and corrupt
WAL evidence.

## Scope boundary

This contract does not select when a kill should fire, grant runtime authority
to change it, connect the coordinator to the active loop, authorize IU-4, or
send exchange/live orders. Fresh integrated workstation validation remains a
separate gate before any activation decision.
