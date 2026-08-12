# Pre-IU-4 SHADOW Observation Gate Evidence — 2026-08-12

## Status

**IMPLEMENTED AND LOCALLY VERIFIED; BOUNDED PAPER SHADOW ONLY**

The user explicitly approved `IU4-SHADOW-OBSERVATION-GATE FREIGEBEN` on
2026-08-12.

The active PAPER loop can now evaluate every fused intent through the existing
IU-4 adapter inside a disposable sandbox cloned from the startup-bound atomic
source. The source coordinator is never opened for writing. ENFORCED,
Exchange, Live, and source-state mutation remain disabled.

## Explicit activation and bound

Observation is disabled by default and requires all of:

- a passed `SHADOW` runtime gate;
- `L1_IU4_SHADOW_OBSERVATION_ENABLED=1`;
- a new evidence path outside the atomic source tree;
- an explicit positive record limit;
- `max_ticks <= record_limit`;
- the hard implementation ceiling of 10,000 records;
- the approved economics stop-rate configuration.

An existing evidence file is never overwritten. Every evidence update is
atomic and the previous whole-file SHA-256 must match the observer's last
write. External alteration stops the run.

## Runtime contract

For each completed legacy PAPER tick, the gate:

1. revalidates the runtime-gate state binding and the byte manifest of the
   source snapshot/journal;
2. derives the deterministic IU-4 request from the fused intent and exact
   decimal reference price;
3. executes the existing `PaperIU4Adapter` only against the disposable
   sandbox;
4. records legacy and IU-4 action, position, reason, state fingerprints,
   transaction sequences, and parity flags;
5. atomically publishes fingerprinted bounded JSON evidence.

Observed divergence is evidence and does not itself stop the run. Source,
binding, sandbox, configuration, duplicate-intent, evidence-integrity, or
record-limit failures stop fail-closed before the next tick.

Autonomous legacy exits derived from `HOLD` are converted to their close intent
only when the IU-4 sandbox has the matching open side. If it does not, the
event is recorded as a suppressed autonomous exit and remains a state-exact
IU-4 `NOOP`; it can never become a new entry.

## Non-authority boundary

- adapter execution scope: `DISPOSABLE_SANDBOX_ONLY`;
- source state mutation allowed: `false`;
- IU-4 ENFORCED: disabled;
- Exchange: disabled;
- Live: disabled;
- no activation authorization is created or implied.

## Verification

```text
Focused observation/runtime-launch tests
13/13 passed

tests/live_l1
308/308 passed

tests/regression
170/170 passed

Total
478/478 passed
```

`py_compile` and `git diff --check` passed. The foreign untracked file
`scripts/build_rcc002_spec_bundle.py` was not read, modified, staged, or
committed.

## Next gate

This unit authorizes implementation only. A separately approved bounded X1
PAPER observation run is required to produce real tick evidence and evaluate
the recorded divergence set. It does not authorize a Workstation full-history
run or IU-4 ENFORCED.
