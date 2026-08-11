# Pre-IU-4 Startup Mode Gate Evidence — 2026-08-09

## Status

**IMPLEMENTED AND LOCALLY VERIFIED; INACTIVE PRE-IU-4 CONTRACT**

Branch: `codex/pre-iu4-startup-mode-gate-2026-08-09`

IU-4, Exchange, and Live remain locked. The gate is not imported by the active
L1 loop or `safe_launch.py`. No existing environment setting or operational
profile was changed.

## Mode contract

The contract recognizes exactly three modes:

| Mode | Coordinator required | Observation | Adapter execution | State mutation |
|---|---:|---:|---:|---:|
| `OFF` | No | No | No | No |
| `SHADOW` | Yes, healthy | Yes | No | No |
| `ENFORCED` | Yes, healthy and authorized | No | Yes | Yes |

`IU4StartupModeRequestV1.off()` is the safe default and can be evaluated
without a coordinator or identity configuration. Invalid mode names and
non-boolean safety flags are rejected rather than normalized to a more
permissive state.

## Identity and reconciliation gate

`SHADOW` and `ENFORCED` require an exact match for:

- coordinator ID and symbol;
- economics profile ID and model version;
- economics configuration SHA-256;
- throttle policy profile ID and model version;
- throttle policy SHA-256;
- full 40-character authorized repository commit SHA;
- separately supplied running-checkout commit matching that authorized SHA.

Both modes require the explicit reconciliation gate and a consistent atomic
snapshot/WAL chain. Corrupt component fingerprints and WAL-ahead interrupted
transactions fail closed. `SHADOW` receives only a state fingerprint and
transaction sequence; it cannot enable the adapter or authorize mutation.

## ENFORCED prerequisites

`ENFORCED` additionally requires:

- operational profile exactly `PAPER`;
- startup recovery enabled;
- `IU4ActivationAuthorizationV1` bound to all identities and the exact commit;
- a strictly increasing UTC validity window containing the startup time;
- a separate externally supplied trusted authorization ID matching the
  content-addressed authorization artifact.

The external trust anchor prevents an authorization from approving itself by
merely carrying its own checksum. Missing or mismatched trust anchors keep
adapter execution and state mutation disabled.

The authorization ID is an integrity/audit hash, not a digital signature. The
trusted authorization ID must eventually be provisioned by a separate launch
authority outside runtime-controlled request content.

## Entry and exit behavior

A healthy, authorized `ENFORCED` gate enables only the Paper IU-4 adapter. It
does not enable exchange/live execution.

S4 entry blockers remain effective after startup. A tested `EMERGENCY` kill
state still allows the gate to serve the exit path while reporting
`entry_allowed=false` and `exit_allowed=true`. A kill therefore cannot be
mistaken for startup corruption and cannot disable exits.

All denied and non-ENFORCED decisions report `state_mutation_allowed=false`.
The decision contract retains `exit_allowed=true` as the invariant policy; an
invalid startup does not silently authorize state mutation and must use a
separately governed recovery/emergency-exit path.

## Verification

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest \
  tests.live_l1.test_paper_iu4_startup_gate

Ran 12 tests — OK
```

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover \
  -s tests/live_l1 -p 'test_*.py'

Ran 209 tests — OK
```

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover \
  -s tests/regression -p 'test_*.py'

Ran 170 tests — OK
```

Static import search returned no active `live_l1` importer of
`live_l1.core.paper_iu4_startup_gate`.

## Scope boundary

This unit defines the startup/mode decision only. It does not wire the gate
into startup, create a trusted authorization file, enable `ENFORCED`, invoke
the IU-4 adapter, modify the accepted SHADOW profile, or send exchange/live
orders. Wiring and any activation decision require separate explicit approval
and fresh integrated workstation evidence.
