# Pre-IU-4 X1 Replay Restart Evidence — 2026-08-09

## Status

**10,000-TICK CONTROLLED RESTART PASSED WHILE LONG**

Branch: `codex/pre-iu4-x1-replay-restart-2026-08-09`

Restart contract commit: `52cf0eba3c67fa00f1d02ec72b94d8bd686eec56`

IU-4 ENFORCED, Exchange, Live, and the Workstation remained locked and unused.

## Restart contract

The isolated IU-4 SHADOW sandbox supports one explicit replay boundary. At the
boundary it reconciles and records the durable atomic state, discards the
active coordinator/adapter objects, reconstructs both from the sandbox
snapshot and WAL, and requires exact equality of state fingerprint and
transaction sequence before processing the next replay step.

Invalid boundaries, inconsistent atomic files, reconciliation failure, or any
restored-state difference fail closed. The restart boundary and all recovery
results are bound into immutable replay evidence and the pipeline receipt.

## X1 run

- dataset: first 10,000 valid BTCUSDT one-minute rows;
- source CSV SHA-256:
  `2896badb62e3236df301a1ccf56b878916c48b22ff57483e86b9fc32bffaf104`;
- interval: `2017-08-17T04:00:00Z` through `2017-08-24T02:39:00Z`;
- restart boundary: after replay step 5,050;
- state at restart: LONG;
- transaction sequence at restart: 15;
- restart state fingerprint:
  `c84d45e0a1a10fbf826456bf0b708e6de25e28c2ba80b58575db86e1c8c34979`;
- exact state restored: true;
- first subsequent autonomous close: step 5,082;
- sequence after that close: 16;
- legacy transitions: `9 OPEN_LONG`, `9 CLOSE_LONG`;
- IU-4 transitions: `9 OPEN_LONG`, `9 CLOSE_LONG`;
- committed transitions: 18;
- NOOP outcomes: 9,982;
- rejected outcomes: 0;
- autonomous exits committed: 9 of 9;
- final position: FLAT;
- final transaction sequence: 18;
- sidecar issues: 0;
- integrated/sidecar observation ID parity: passed.

All receipt chain checks passed. Replay ticks were exactly `1..10000`, replay
and outcome source-intent IDs matched, all canonical fingerprints revalidated,
and the source atomic snapshot, WAL, and L1 log remained unchanged.

## Whole-file hashes

- IU-3 manifest:
  `7558ab7051bfbf2fd83921cc8364d5e4467495e9b3732e54c6db9c56e5d95fa1`;
- L1 source log:
  `6e313666aa9712a809a3c60bc9ffd9b2e0789c76390be90f3f0a09077f3a928d`;
- replay JSONL:
  `71423047dc67829df3d3e495beb1d98e42b8519cc9ba57f83d602c9f40358813`;
- replay input manifest:
  `bec043699914a3411b1f53306971391c7da2fdfd27995df2db2a6b6e57aae65f`;
- replay evidence:
  `407ce7dbc028f356e812485cc2a50537118e1a21c3983f1186dddc4508ba747f`;
- pipeline receipt:
  `608d222904b5cfc0cbf3dba63488388b291585deb78c8f85a4786c5d7a9d7cb9`;
- top-level run manifest:
  `a6343ab3929813a6e0b4bf3ac8e029c7253d61a1f1f80111a112b1239445ecfb`.

## Verification

```text
Focused restart/replay tests
Ran 34 tests — OK

tests/live_l1 full suite
Ran 252 tests — OK

tests/regression full suite
Ran 170 tests — OK
```

Bytecode compilation and `git diff --check` passed. The unrelated untracked
`scripts/build_rcc002_spec_bundle.py` remained untouched.

## Scope boundary and next gate

This proves deterministic replay continuation across one controlled restart
while a LONG position is open. It does not authorize IU-4 ENFORCED, Exchange,
Live, or an operational throttle policy.

Next X1 gate: `IU4-X1-REPLAY-RESTART-FEHLERINJEKTION FREIGEBEN`.

That gate must prove fail-closed behavior for a deliberately inconsistent
restart artifact before the deferred Workstation full-history replay.
