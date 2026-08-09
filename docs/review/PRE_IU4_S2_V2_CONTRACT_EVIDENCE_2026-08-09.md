# Pre-IU-4 S2 V2 Contract Evidence — 2026-08-09

## Status

**IMPLEMENTED AND LOCALLY VERIFIED; INACTIVE PRE-IU-4 CONTRACT**

Branch: `codex/pre-iu4-s2-v2-contract-2026-08-09`

IU-4, Exchange, and Live remain locked. The new store is not imported by the
active L1 loop and does not replace the legacy S2 owner.

## Implemented contract

- `PositionStateS2FlatV2` represents an explicit economics-free FLAT state.
- `PositionStateS2V2` represents a complete LONG/SHORT OPEN state with Decimal
  entry economics and the immutable PEE profile/model/fingerprint identity.
- Schema versions are strict integers; booleans and floats are rejected.
- Entry timestamps are canonical UTC timestamps with whole-second resolution.
- Entry notional, adverse/non-favourable entry fill, stop direction, and risk
  budget identities are validated before persistence.
- FLAT and OPEN records have deterministic canonical SHA-256 fingerprints.
- The versioned reader still recognizes legacy S2 schemas as incomplete legacy
  artifacts; it never silently upgrades legacy float state into V2 economics.

## Persistence and restart contract

`PaperPositionStore` provides a separate inactive V2 snapshot and immutable
transition journal:

- initialization is FLAT-only and idempotent;
- OPEN is FLAT -> complete LONG/SHORT;
- CLOSE is complete LONG/SHORT -> FLAT with the exact closed trade ID;
- every transition contains complete before/after states;
- journal write is durable and precedes the atomic snapshot replacement;
- an interrupted transition is recovered exactly once from recorded values;
- event IDs and trade IDs cannot be reused with different or later trades;
- transition timestamps and tick IDs cannot regress;
- OPEN event time/tick must equal persisted entry time/tick;
- CLOSE cannot precede its OPEN time/tick;
- an OPEN snapshot without its journal is inconsistent and fails closed;
- configuration, symbol, broken-chain, corrupt-JSON, and legacy-state mismatches
  deny entries while retaining exit permission.

The store is single-writer by contract. Cross-artifact atomic coordination with
Paper Account, trade settlement, and S4 is intentionally not claimed here.

## Non-interference boundary

- No active-loop module was modified.
- No active-loop module imports `live_l1.state.paper_position`.
- No exchange or live path was enabled.
- No accepted PEE profile value or fingerprint was changed.
- No workstation execution or evidence was performed for this X1-only unit.

## Verification

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest \
  tests.live_l1.test_paper_position \
  tests.live_l1.test_paper_account

Ran 45 tests — OK
```

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover \
  -s tests/live_l1 -p 'test_*.py'

Ran 144 tests — OK
```

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover \
  -s tests/regression -p 'test_*.py'

Ran 170 tests — OK
```

## Remaining gate

This commit defines and proves the isolated S2 V2 state boundary. It does not
authorize IU-4. Before activation, a separate atomic coordinator must define
and prove one recovery sequence across S2, Paper Account, trade/settlement, S4,
and throttle effects. The integrated candidate must then receive a fresh IU-3
full-history workstation run; older output hashes do not certify this commit.
