# Pre-IU-4 Loss-Cluster Parity Contract Evidence — 2026-08-13

## Status

**IMPLEMENTED AND LOCALLY VERIFIED — SHADOW OBSERVATION ONLY**

The user explicitly requested `LOSS_CLUSTER-Paritätsvertrag reparieren` on
2026-08-13 after the completed 100K observation had preserved the causal
divergence in commit `f8dcf15e74d663475f59ccc633333eb47e87d467`.

The repair keeps the established Legacy loss-cluster entry gate as the
behavioral authority. It changes neither Legacy execution nor the IU-4 adapter,
atomic coordinator, economics, throttle policy, source state, Exchange, or
Live boundary.

## Exact contract

The IU-4 SHADOW observer now recognizes a Legacy loss-cluster entry veto only
when all of the following are exact:

- source fused intent is `BUY` or `SELL`;
- Legacy action is `NOOP`;
- Legacy `executed` is `false`;
- Legacy position is `FLAT -> FLAT`;
- Legacy reason is exactly `LOSS_CLUSTER_GATE_BLOCKED_ENTRY`.

For that exact final Legacy result, the observer derives a state-exact IU-4
`HOLD` request and binds the Legacy veto reason into the canonical request.
The evidence continues to preserve the original `source_intent_final`, the
derived `observed_intent_final`, the exact Legacy reason, both runtime states,
and all parity flags. No evidence-schema extension is required.

A result that claims `LOSS_CLUSTER_GATE_BLOCKED_ENTRY` with any inconsistent
action, execution flag, intent, or position shape is rejected before adapter
execution with `PEE_IU4_SHADOW_OBSERVATION_EVIDENCE_INVALID`.

Other Legacy `NOOP` results are not silently converted. They continue through
the existing observation logic so unrelated divergence remains visible.
Autonomous-exit handling is unchanged.

## Causal coverage

The focused tests establish:

- blocked `BUY` remains `FLAT` in both Legacy and IU-4;
- blocked `SELL` remains `FLAT` in both Legacy and IU-4;
- the following `HOLD` tick remains position- and action-equal;
- all three parity flags remain true;
- the bound source atomic state remains byte-identical;
- a malformed loss-cluster veto fails closed;
- the pre-existing generic-divergence test remains active;
- adapter and durable Legacy loss-cluster tests remain unchanged and pass.

This directly prevents the two causal 100K failures at observations `13,219`
and `92,748`, where Legacy emitted
`NOOP / LOSS_CLUSTER_GATE_BLOCKED_ENTRY` while the former observer derived an
IU-4 `OPEN_LONG` from the unfenced fused `BUY`.

## Verification

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest \
  tests.live_l1.test_loss_cluster_state \
  tests.live_l1.test_paper_iu4_shadow_observation_gate \
  tests.live_l1.test_paper_iu4_adapter

49/49 passed
```

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover \
  -s tests/live_l1 -p 'test_*.py'

316/316 passed
```

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover \
  -s tests/regression -p 'test_*.py'

170/170 passed
```

Unique full-suite total: `486/486` passed. `py_compile` and
`git diff --check` also passed.

## Scope boundary and next gate

This unit repairs and verifies only the bounded IU-4 SHADOW observation
parity contract. It does not authorize IU4 ENFORCED, Exchange, Live, source
mutation, branch integration, or a repeat 100K run.

After branch integration, the next separately authorized gate is a fresh
hash-bound X1 100K SHADOW observation using the unchanged input and source
bindings. Its acceptance still requires zero position/action parity failures
and a final state equal to Legacy; the prior failed evidence remains preserved.
