# Pre-IU-4 Atomic Loss-Cluster Evidence — 2026-08-09

## Status

**IMPLEMENTED AND LOCALLY VERIFIED; ACTIVE LEGACY SAFETY HARDENING**

Branch: `codex/pre-iu4-loss-cluster-atomic-2026-08-09`

IU-4, Exchange, and Live remain locked. This unit changes only legacy
loss-cluster persistence and its read-only operational validation. Entry/exit
thresholds and valid-state trading semantics are unchanged.

## Defect closed

The previous implementation wrote `loss_cluster_state.json` directly with
`open(..., "w")` and swallowed every write/load error. A truncated or corrupt
file was therefore interpreted as an empty state and could silently allow new
entries.

That unsafe behavior is removed.

## Persisted contract

`LossClusterStateV2` now requires:

- strict integer schema/version `2`;
- monotonic non-negative revision;
- at most ten finite PnL values, persisted as canonical decimal strings;
- non-negative integer `pause_entries_remaining`;
- canonical UTC whole-second update timestamp;
- SHA-256 fingerprint over the complete canonical payload;
- no missing or unknown record fields.

Existing valid V1 records are strictly readable and migrate to V2 on the next
state mutation. Invalid V1 records are not repaired by guessing.

## Atomic write boundary

Every mutation now uses:

1. a temporary file in the target directory;
2. complete JSON serialization;
3. file flush and `fsync`;
4. atomic `os.replace` of the target;
5. parent-directory `fsync`;
6. temporary-file cleanup on failure.

An injected interruption before replacement proves the prior complete snapshot
remains byte-identical and readable.

## Fail-closed behavior

- Missing state remains an allowed clean initialization condition.
- Invalid JSON, schema, values, or checksum mark persistence unhealthy.
- A persistence I/O failure after a closed trade marks persistence unhealthy.
- While unhealthy, every new entry is blocked without overwriting the corrupt
  evidence file.
- Existing LONG/SHORT positions can still exit; exits are never blocked by the
  loss-cluster persistence condition.
- A different configured state path is independently reloaded instead of
  inheriting stale process-global state.
- Stable audit events record invalid state, persistence failure, and fail-closed
  entry decisions.

Reconciliation, startup recovery, runtime schema validation, operational health,
and monitoring now use the same versioned/checksummed reader. Recovery never
reports corrupt state as successfully loaded.

The SHA-256 field is an integrity checksum, not an authentication signature. It
detects accidental corruption and uncoordinated mutation; it does not claim to
defend against an actor who deliberately rewrites both payload and checksum.

## Verification

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest \
  tests.live_l1.test_loss_cluster_state

Ran 18 tests — OK
```

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover \
  -s tests/live_l1 -p 'test_*.py'

Ran 176 tests — OK
```

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover \
  -s tests/regression -p 'test_*.py'

Ran 170 tests — OK
```

## Scope boundary

No PEE profile value, sizing rule, loss-cluster threshold, lookback, pause count,
S2 transition, exchange path, or live-order path changed. No workstation job was
run for this X1-only unit. Fresh integrated workstation evidence remains required
before any IU-4 activation decision.
