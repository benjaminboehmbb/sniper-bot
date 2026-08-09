# Pre-IU-4 Adapter Contract Evidence — 2026-08-09

## Status

**IMPLEMENTED AND LOCALLY VERIFIED; INACTIVE PRE-IU-4 CONTRACT**

Branch: `codex/pre-iu4-adapter-contract-2026-08-09`

IU-4, Exchange, and Live remain locked. `paper_iu4_adapter.py` is not imported
by the active L1 loop and contains no exchange, network, environment, clock, or
live-order access.

## Ownership decision

`PaperIU4Adapter` is the only planned boundary from fused `BUY`/`SELL`/`HOLD`
intent into Decimal Paper Execution Economics. It does not mutate legacy S2/S4,
write an independent account, or call the legacy float execution function.
Every economic mutation is delegated to `PaperAtomicCoordinator`.

The deterministic mapping is:

| Current position | Intent | Adapter action |
|---|---|---|
| FLAT | BUY | OPEN_LONG |
| FLAT | SELL | OPEN_SHORT |
| LONG | SELL | CLOSE_LONG |
| SHORT | BUY | CLOSE_SHORT |
| Any other valid pair | BUY/SELL/HOLD | NOOP |

An opposing intent closes the current position only. It cannot close and
reverse in one request.

## Request contract

`IU4AdapterRequestV1` strictly binds:

- source intent ID and stable intent reason;
- BUY/SELL/HOLD action;
- exact expected aggregate-state fingerprint;
- target system-state ID;
- canonical UTC whole-second timestamp and non-negative tick;
- Decimal reference price and optional entry stop;
- trade identity.

Binary floats are rejected. Unknown or missing serialized fields are rejected.
The request ID is `PEE-IU4-` plus the SHA-256 of the canonical request payload;
a supplied ID with changed content is invalid.

## OPEN contract

OPEN requires an exact FLAT state fingerprint, unique trade ID, valid stop,
S4 entry permission, account guard permission, throttle permission, and a
successful Decimal `authorize_entry` decision. The adapter builds complete S2
V2 and accepted-entry artifacts and gives them to the atomic coordinator.

Any rejection leaves position, Account, throttle, S4, snapshot, and WAL
unchanged. The adapter never falls back to legacy float sizing.

## CLOSE contract

CLOSE requires an exact OPEN state and matching trade ID. The adapter
reconstructs the persisted entry economics under the same profile, settles the
exit with Decimal PEE, builds one complete V2 trade and FLAT S2 state, and gives
both to the atomic coordinator.

S4 kill levels do not block CLOSE. A tested `EMERGENCY` state preserves the
kill level while the position is settled to FLAT and `exit_allowed` remains
true.

## Idempotency and fail-closed behavior

- The coordinator journal is searched by the content-addressed request ID.
- Exact OPEN and CLOSE retries return the already-committed transaction without
  a second entry or settlement.
- A stale expected-state fingerprint is rejected without mutation.
- A request ID owned by a non-matching or non-execution transaction is a hard
  conflict.
- WAL/recovery, time/tick monotonicity, component parity, and fingerprint
  validation remain owned by the atomic coordinator.
- HOLD and same-side intents are NOOPs and do not create economic WAL entries.

## Verification

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest \
  tests.live_l1.test_paper_iu4_adapter

Ran 12 tests — OK
```

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover \
  -s tests/live_l1 -p 'test_*.py'

Ran 197 tests — OK
```

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover \
  -s tests/regression -p 'test_*.py'

Ran 170 tests — OK
```

Static import search returned no active `live_l1` importer of
`live_l1.core.paper_iu4_adapter`.

## Scope boundary

This unit defines the adapter and its atomic handoff; it does not import the
adapter into the active loop, enable IU-4, choose an operational mode, modify
the accepted PEE profile, send exchange/live orders, or certify workstation
full-history behavior. Activation requires a separate explicit startup and
mode gate plus fresh integrated workstation evidence.
