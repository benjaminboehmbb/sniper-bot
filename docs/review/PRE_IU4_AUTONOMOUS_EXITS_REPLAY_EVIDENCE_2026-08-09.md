# Pre-IU-4 Autonomous Exit Replay Evidence — 2026-08-09

## Status

**AUTONOMOUS EXIT CONTRACT PASSED; 10,000-TICK TRANSITION PARITY PASSED**

Branch: `codex/pre-iu4-autonomous-exits-replay-2026-08-09`

Contract commit: `f3209ea92d7be5b45de5e59ae8f12070f43b1de3`

IU-4 ENFORCED, Exchange, Live, and the Workstation remained locked and unused.

## Contract

Replay schema version 2 distinguishes ordinary fused intents from proven
autonomous exit executions. A source `HOLD` is converted into an exit replay
only when the same `(system_state_id, tick, intent_id)` has an L5 execution
event with `executed=1` and `action=CLOSE_LONG|CLOSE_SHORT`.

Every autonomous exit step binds:

- the original fused `HOLD`;
- the exact execution action and log sequence;
- the execution reason;
- the canonical market price and timestamp;
- the complete source-log SHA-256.

An autonomous close is exit-only. If its declared LONG/SHORT side does not
match the isolated atomic position, replay fails closed. It cannot open or
reverse a position from FLAT. Ordinary HOLD events remain HOLD.

## X1 dataset result

The first 10,000 valid BTCUSDT one-minute rows were replayed from
`2017-08-17T04:00:00Z` through `2017-08-24T02:39:00Z`.

- complete source CSV SHA-256:
  `2896badb62e3236df301a1ccf56b878916c48b22ff57483e86b9fc32bffaf104`;
- commit bound into the run:
  `f3209ea92d7be5b45de5e59ae8f12070f43b1de3`;
- source events: 10,000 market, 10,000 intent, 10,000 execution;
- legacy transitions: `9 OPEN_LONG`, `9 CLOSE_LONG`;
- replay provenance: 9,991 intent steps, 9 autonomous exit steps;
- replay intents: `9 BUY`, `9 SELL`, `9,982 HOLD`;
- IU-4 outcomes: `9 OPEN_LONG`, `9 CLOSE_LONG`, `9,982 NOOP`;
- committed atomic transitions: 18;
- rejected outcomes: 0;
- autonomous exits committed: 9 of 9;
- final isolated position: FLAT;
- sidecar issues: 0;
- integrated/sidecar observation ID parity: passed.

All receipt chain checks passed. Tick sequence was exactly `1..10000`, replay
and outcome source-intent IDs matched, the source atomic state remained at
transaction sequence zero, and its snapshot/WAL/log bytes remained unchanged.
All canonical manifest, evidence, and receipt fingerprints independently
revalidated.

## Whole-file hashes

- IU-3 manifest:
  `d8295a5f603e5410ba4f74cc96245f6d6f4064dcf6b848b7595fb390d4fdbb4a`;
- L1 source log:
  `ecd1cf6fe6ad532bef6948c292777d1c5f6b7dc86a4e8badfefb991685d0cf3c`;
- replay JSONL:
  `fddb96a27d408b35ad3d0ad96267b6327e29f93194d32971e622c2daf28c2e13`;
- replay input manifest:
  `850f0763001e0df4ee2f3b71ef2ed4b36c8905652d6bab306ba2b78a09e98f20`;
- replay evidence:
  `1b6ca540bd253fbbb85e83585ff05edfc2e3196ed72704a21f22f1355f516141`;
- pipeline receipt:
  `0a5ab710e07d29e2b3f6906db2739cc62c343a3cda3211ba678395c9504d0452`;
- top-level run manifest:
  `bb4d6916168597cfe62ebe192451c677a22072dee21dd3b97b07bbaff4194c00`.

## Verification

```text
Focused autonomous-exit/replay tests
Ran 38 tests — OK

tests/live_l1 full suite
Ran 247 tests — OK

tests/regression full suite
Ran 170 tests — OK
```

Bytecode compilation and `git diff --check` passed. The unrelated untracked
`scripts/build_rcc002_spec_bundle.py` remained untouched.

## Scope boundary and next gate

This closes the execution-exit parity blocker discovered by the first X1
dataset replay. It does not authorize IU-4 ENFORCED, Exchange, Live, or an
operational throttle policy.

Next gate: `IU4-X1-REPLAY-RESTART FREIGEBEN`.

That gate must prove the same 9/9 transition chain across a controlled replay
restart before any Workstation full-history replay is attempted.
