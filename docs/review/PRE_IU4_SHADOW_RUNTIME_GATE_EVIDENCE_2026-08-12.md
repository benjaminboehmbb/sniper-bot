# Pre-IU-4 SHADOW Runtime Gate Evidence — 2026-08-12

## Status

**IMPLEMENTED AND LOCALLY VERIFIED; SHADOW STARTUP ONLY**

The user explicitly approved `IU4-SHADOW-RUNTIME-GATE FREIGEBEN` on
2026-08-12.

The authoritative operational entry point `live_l1/tools/safe_launch.py` now
evaluates the IU-4 startup contract before starting the active loop. The safe
default remains `OFF`. The bridge accepts only `OFF` or `SHADOW`; `ENFORCED`
fails closed before the loop starts.

IU4 ENFORCED, Exchange, Live, adapter execution, state mutation, and entry
authority remain disabled.

## Exact approved identities

SHADOW startup is pinned to:

- throttle approval ID:
  `IU4-THROTTLE-PROFIL-OBSERVED-BOUNDARY-2026-08-11`;
- throttle profile SHA-256:
  `b16566970a3d7db4b038085d0b8601e24721fae572fbe7d3159c071680cd91e7`;
- throttle policy ID: `PEE_RATE_OBSERVED_BOUNDARY_001`;
- throttle policy fingerprint:
  `ed6e55744ce76d4f2e159832a2aeebcd4dbeb0f5dc1cdbbfda6177af119d1ada`;
- economics profile ID: `PEE_V1_PAPER_CONSERVATIVE_CANDIDATE_001`;
- economics model: `PEE_V1`;
- economics configuration fingerprint:
  `ac4cc746b57c2b802cf765c9c102f9921858c4d3cde2040f452b69ba1e6b14e1`.

The approved throttle loader is now shared by offline replay and active
startup, removing the prior duplicate validation implementation.

## Fail-closed startup contract

`SHADOW` requires all of the following:

- operational profile exactly `PAPER`;
- full authorized commit SHA equal to the running checkout commit;
- no tracked changes outside that commit;
- exact approved economics and throttle artifact identities;
- existing, non-symlink atomic state tree;
- exact coordinator ID and symbol;
- enabled reconciliation gate;
- consistent snapshot/WAL chain;
- exact aggregate-state fingerprint and transaction sequence.

The startup decision is passed directly to the active loop. The loop re-reads
and re-reconciles the atomic source immediately on entry. A changed snapshot or
WAL between `safe_launch.py` and loop entry stops startup.

## Active-loop boundary

The loop receives only the read-only startup decision and emits bound startup
fields. It does not instantiate or call `PaperIU4Adapter`, does not run the
SHADOW harness per tick, and does not write the atomic IU-4 source.

The decision invariants are:

- `shadow_observation_enabled=true`;
- `adapter_execution_enabled=false`;
- `state_mutation_allowed=false`;
- `entry_allowed=false`;
- `exit_allowed=true`;
- `exchange_enabled=false`;
- `live_enabled=false`.

## Verification

```text
Focused IU4 profile/startup/replay/safe-launch tests
43/43 passed

tests/live_l1
297/297 passed

tests/regression
170/170 passed

Total
467/467 passed
```

`py_compile` and `git diff --check` passed. The foreign untracked file
`scripts/build_rcc002_spec_bundle.py` was not read, modified, staged, or
committed.

## Scope boundary and next gate

This gate authorizes only fail-closed startup binding for read-only IU-4
SHADOW state. It does not yet produce per-tick live-loop IU-4 shadow outcomes.
That requires a separate, explicitly approved observation gate with bounded
evidence before any workstation run. ENFORCED, Exchange, and Live remain
separate locked gates.
