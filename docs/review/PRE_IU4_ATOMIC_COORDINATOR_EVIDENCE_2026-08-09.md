# Pre-IU-4 Atomic Coordinator Evidence — 2026-08-09

## Status

**IMPLEMENTED AND LOCALLY VERIFIED; INACTIVE PRE-IU-4 CONTRACT**

Branch: `codex/pre-iu4-atomic-coordinator-2026-08-09`

IU-4, Exchange, and Live remain locked. The coordinator is not imported by the
active L1 loop and does not mutate the legacy runtime stores.

## Atomic ownership decision

The coordinator uses one canonical aggregate snapshot,
`paper_atomic_state.json`, rather than independently publishing S2, Paper
Account, S4, and throttle files. Immutable transaction records are written to
`paper_atomic_transactions/` before that aggregate snapshot advances.

This establishes one logical commit point:

- before the snapshot replacement, only the complete pre-transaction state is
  published;
- after the snapshot replacement, only the complete post-transaction state is
  published;
- after a crash between WAL and snapshot, entries remain blocked until exact
  recovery publishes the recorded complete post-transaction state;
- no recovery value is reconstructed from a legacy float.

The existing standalone S2, Paper Account, and throttle stores remain inactive
contracts. The coordinator deliberately does not double-write them because two
independent publication owners would recreate the divergence being removed.

## Cross-component transactions

**OPEN** atomically contains:

- complete FLAT S2 before and complete LONG/SHORT S2 after;
- unchanged Paper Account;
- accepted entry event and reproducible throttle state after;
- S4 after, bound to exact S2, Account, and throttle fingerprints.

**CLOSE** atomically contains:

- complete LONG/SHORT S2 before and complete FLAT S2 after;
- complete V2 settlement trade;
- reproducible Paper Account state after exactly one settlement;
- unchanged throttle state;
- S4 after, bound to exact S2, Account, and throttle fingerprints.

Every WAL record contains the complete aggregate before and after state.

## Enforced invariants

- Transaction sequence equals accepted-entry count plus settled-trade count.
- FLAT requires accepted-entry count = settlement count and exact last closed
  trade parity between S2 and Paper Account.
- OPEN requires accepted-entry count = settlement count + 1.
- Settlement trade ID, symbol, side, quantity, entry prices, fee, risk, stop,
  timestamp, tick, and PEE identity must exactly match the OPEN S2 state.
- Account state after CLOSE must be reproducible from the complete V2 trade.
- Throttle state after OPEN must be reproducible from the accepted entry event.
- S4 entry permission is deterministically recomputed from Account guard,
  throttle, current position, and the preserved kill level.
- S4 always permits exits and binds all component fingerprints.
- OPEN/CLOSE cannot silently alter the S4 kill level.
- Transaction event IDs and trade IDs are unique; time and tick never regress.
- Repeated identical calls are idempotent; changed duplicates are conflicts.
- Snapshot-ahead, WAL-ahead, corrupt JSON, broken chains, identity mismatches,
  and fingerprint tampering block entries while retaining exit permission.

## Verification

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest \
  tests.live_l1.test_paper_atomic_coordinator \
  tests.live_l1.test_paper_position \
  tests.live_l1.test_paper_account \
  tests.live_l1.test_paper_entry_throttle

Ran 83 tests — OK
```

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover \
  -s tests/live_l1 -p 'test_*.py'

Ran 158 tests — OK
```

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover \
  -s tests/regression -p 'test_*.py'

Ran 170 tests — OK
```

Static import search returned no active `live_l1` importer of
`live_l1.state.paper_atomic_coordinator`.

## Scope boundary and remaining gates

This unit defines persistence and recovery ownership. It does not connect the
coordinator to the active loop, send orders, alter the accepted PEE profile, or
authorize IU-4. External risk/kill-level transitions require their own explicit
transaction type before activation; OPEN/CLOSE cannot change them implicitly.

The integrated future candidate still requires fresh full-history workstation
validation. Older IU-3 output hashes do not certify this commit.
