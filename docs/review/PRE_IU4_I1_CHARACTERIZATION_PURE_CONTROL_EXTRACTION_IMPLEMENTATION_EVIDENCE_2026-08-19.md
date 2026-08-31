# Pre-IU4 I1 Characterization / Pure Control Extraction — Implementation Evidence — 2026-08-19

## 1. Result

I1 characterization and pure control extraction are complete within the exact
four-path mandate after resolution of `I1-M1`, `I1-RR-M1`, and `I1-RR-M2`.
Baseline characterization, pure-contract verification, action-authoritative
Legacy delegation, fail-closed mismatch handling, OFF/SHADOW preservation,
focused tests, the complete `tests/live_l1` suite, regression tests,
compilation, preservation hashes, and scope checks pass.

```text
IMPLEMENTATION_PACKAGE:I1
I1_RESULT:PASS
BASELINE_CHARACTERIZATION:PASS
PURE_CONTROL_EXTRACTION:PASS
LEGACY_DELEGATION:PASS
ACTION_AUTHORITATIVE_DISPATCH:PASS
INCONSISTENT_ACTION_REASON_FAIL_CLOSED:PASS
REASON_SPECIFIC_PRECONDITION_VALIDATION:PASS
EXACT_HEAD_DIFFERENTIAL:5120/5120_PASS
OFF_SHADOW_PARITY:PASS
PRESERVATION:PASS
SCOPE:PASS
I2_THROUGH_I8_IMPLEMENTED:NO
IMPLEMENTATION_AUTHORIZED_BEYOND_I1:NO
IU4_ENFORCED_WIRING:NO
ENFORCED_ACTIVATION_AUTHORIZED:NO
EXCHANGE_AUTHORIZED:NO
LIVE_AUTHORIZED:NO
```

The pre-resolution evidence identity was SHA-256
`7f3c2ddbe200680787e276df98f523decd075cd0f6d7c58e1d55430de3717743`,
275 lines. The first-resolution evidence identity was SHA-256
`0b4382e727c060add096984d4097d04ffc8379c0bf2650355d95e77e20ea2709`,
295 lines. Final rereview-resolution verification completed at
`2026-08-19T08:58:07Z`.

## 2. Controlling identity

```text
CANONICAL_REPOSITORY:/home/benja/projects/sniper-bot
HEAD:c7ce0452aa2ccbf08c462784d68fa07b3dfe9595
MAIN:c7ce0452aa2ccbf08c462784d68fa07b3dfe9595
ORIGIN_MAIN:89e13fecd1ab549ca7099818b1c9ad4984cb6f7a
MAIN_DIVERGENCE_BEHIND_AHEAD:0/6
```

| Artifact | SHA-256 | Lines | Status |
| --- | --- | ---: | --- |
| Revision 21 specification | `ab8f80720a1d8fe49b9085bce63658bcaecf7f0a3ea70fb555559223090824e0` | 4,605 | unchanged |
| Revision 21 independent rereview | `6618955e67bf9e11798c103eb7d01823dc2ece4c39a66575dbb668c4162c0c7c` | 752 | `READY`, `0/0/0/0` |
| Revision 21 terminal R3 handoff | `0aecf831429076a7b732ca6de2482ba02384792919c3f76a3232c1ef27863b2e` | 140 | complete |
| Revision 21 final R3 attestation | `587c5a5ffed271534d661c6c816781eb8443d5c6318fe14d26b1947d21340851` | 179 | final R3 `PASS` |
| I1 file-exact mandate | `2b235193bb7d2986cac3a42e3b078569e1c5e1070e315f6b6b99cc99823bad4a` | 296 | `AUTHORIZED` |
| I1 independent file-exact review | `bbc9a4c3dfd3f1f05528e8a28d7ae04a212442624201eaaf804bc2cf4ef380c3` | 425 | `NOT_READY`, `I1-M1` |
| I1 review resolution | `6b13b63fc7f7d6fc0b9be2fa7d65a4d6198818b0ef1dee3f3257230fc74103ee` | 221 | first resolution complete |
| I1 independent file-exact rereview | `b772483a51bf06cbec3eb93ecbbdd2ce2b074181059ebcf40d794ff8eb00d571` | 388 | `NOT_READY`, `I1-RR-M1/M2` |

No controlling artifact was modified by I1.

## 3. Exact implementation scope

| Path | Mandated operation | Starting identity | Final identity |
| --- | --- | --- | --- |
| `live_l1/core/paper_execution_control.py` | create | absent | SHA-256 `7d3cb901c1c67c8df85e99bc579fda85d8732b634ff4747e08620b92ac1e44f7`, 257 lines |
| `live_l1/core/execution.py` | modify | SHA-256 `a76f600d27feef969665bcd695ce11bc4e3abae0f25e045f7416fc78cd2513e3`, 951 lines | SHA-256 `5aed85ce2754dbb4d8984a1d699b607e3a522ed6da000df119ecd782a4e764d8`, 1,147 lines |
| `tests/live_l1/test_paper_execution_control.py` | create | absent | SHA-256 `0ae44f2d32f5f3b6affe37a258be0e6aee06790f857e4fc01628c6795bda99e5`, 843 lines |
| this evidence record | create | absent | self-hash computed externally after creation |

The tracked `execution.py` diff is `395` inserted and `199` deleted lines. No
other tracked file differs. The three mandate create-targets were confirmed
absent before I1 began.

## 4. Pre-extraction characterization

The characterization test module was created first while both production
code identities remained exact:

```text
live_l1/core/execution.py
SHA256:a76f600d27feef969665bcd695ce11bc4e3abae0f25e045f7416fc78cd2513e3

live_l1/core/loop.py
SHA256:54e9e7bc0977a9c94f2e85a3279157678249a8569cff63f7d4f29131443fd058
```

The exact baseline command was:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.live_l1.test_paper_execution_control
```

Result:

```text
Ran 13 tests in 0.011s
OK
RETURN_CODE:0
PRODUCTION_CODE_CHANGED_BEFORE_BASELINE:NO
```

### 4.1 Characterized truth table

| State/input | Exact boundary/condition | Baseline action | Baseline reason |
| --- | --- | --- | --- |
| FLAT + BUY | entry allowed | `OPEN_LONG` | `BUY_FROM_FLAT` |
| FLAT + SELL | entry allowed | `OPEN_SHORT` | `SELL_FROM_FLAT` |
| FLAT + HOLD | any non-exit price | `NOOP` | `HOLD_NO_EXECUTION` |
| FLAT + unknown | any | `NOOP` | `UNKNOWN_INTENT` |
| LONG + BUY | below exit/time boundaries | `NOOP` | `BUY_ALREADY_LONG` |
| LONG + SELL | below exit/time boundaries | `CLOSE_LONG` | `SELL_CLOSES_LONG` |
| SHORT + SELL | below exit/time boundaries | `NOOP` | `SELL_ALREADY_SHORT` |
| SHORT + BUY | below exit/time boundaries | `CLOSE_SHORT` | `BUY_CLOSES_SHORT` |
| LONG TP | immediately below | `NOOP` | `HOLD_NO_EXECUTION` |
| LONG TP | exact or above | `CLOSE_LONG` | `TP_LONG_HIT` |
| LONG SL | immediately above | `NOOP` | `HOLD_NO_EXECUTION` |
| LONG SL | exact or below | `CLOSE_LONG` | `SL_LONG_HIT` |
| SHORT TP | immediately above | `NOOP` | `HOLD_NO_EXECUTION` |
| SHORT TP | exact or below | `CLOSE_SHORT` | `TP_SHORT_HIT` |
| SHORT SL | immediately below | `NOOP` | `HOLD_NO_EXECUTION` |
| SHORT SL | exact or above | `CLOSE_SHORT` | `SL_SHORT_HIT` |
| LONG time stop | one second before | `NOOP` | `HOLD_NO_EXECUTION` |
| LONG time stop | exact | `CLOSE_LONG` | `LONG_TIME_STOP_HIT` |
| SHORT time stop | one second before | `NOOP` | `HOLD_NO_EXECUTION` |
| SHORT time stop | exact | `CLOSE_SHORT` | `SHORT_TIME_STOP_HIT` |
| price exit + time stop + opposing intent | simultaneous | side-specific close | price-exit reason |
| time stop + opposing intent | simultaneous without price exit | side-specific close | time-stop reason |
| invalid open snapshot + elapsed time | HOLD | `NOOP` | `HOLD_NO_EXECUTION` |
| invalid open snapshot + opposing intent | elapsed | side-specific close | opposing-intent reason |
| loss-cluster denial + FLAT entry | active/corrupt | `NOOP` | `LOSS_CLUSTER_GATE_BLOCKED_ENTRY` |
| autonomous price exit | HOLD | side-specific close | side-specific TP/SL reason |

No characterization contradicted Revision 21 Section 11. Extraction was
therefore permitted to continue.

## 5. Extracted pure control boundary

`paper_execution_control.py` now owns only deterministic action/reason
selection. It exposes an immutable two-field result and accepts all state,
intent, price, timestamp, thresholds, time-stop values, and the pre-resolved
loss-cluster entry permission as explicit scalar inputs.

It does not receive the runtime state object and does not import or call
Legacy loop, adapter, exchange, logging, state-store, loss-cluster store,
economics, coordinator, runtime-gate, filesystem, socket, subprocess, or
clock-now authorities. It performs no quantity, fill, fee, PnL, settlement,
throttle, persistence, logging, or state mutation.

The pure module preserves exactly these actions:

```text
NOOP
OPEN_LONG
OPEN_SHORT
CLOSE_LONG
CLOSE_SHORT
```

and the fifteen mandate-bound reason codes without alias or fallback changes.

The direct negative-capability test parses the module AST and rejects
forbidden imports plus `open`/`print` calls. A patched `builtins.open` remains
uninvoked during a direct pure evaluation. The frozen result exposes only
`action` and `reason`.

## 6. Legacy delegation and parity

`execution.py` remains the only Legacy mutation and side-effect owner. It:

1. normalizes the existing inputs and resolves the existing environment
   thresholds;
2. obtains loss-cluster entry permission only for a FLAT BUY/SELL candidate;
3. invokes `decide_paper_execution_control()` exactly once;
4. selects the major Legacy side-effect route exclusively from the returned
   `control.action`; and
5. uses `control.reason` only to select a stable, action-compatible subtype
   within that route before applying the pre-existing position, audit,
   trade-log, fee/PnL, duplicate-trade, and loss-cluster paths.

An action/reason pair that is incompatible with its major action, current
position, reason-specific Legacy precondition, or resolved entry permission
returns an
unexecuted `NOOP` with the existing `UNKNOWN_INTENT` reason. It performs no
position mutation, audit append, trade-log append, fee/PnL work, or
loss-cluster close registration. Focused mocked-resolver tests prove that a
reason such as `BUY_FROM_FLAT` cannot override `NOOP`, and that mismatched
OPEN/CLOSE action/reason pairs fail closed without mutation. The final
consumer predicate reconstructs exact Legacy priority over price exit, time
stop, opposing intent, HOLD, same-side intent, entry permission, and unknown
intent from the already captured explicit inputs; it does not call the pure
resolver a second time.

The complete adversarial matrix covers all five valid actions, an invalid
action, all fifteen stable reasons, an invalid reason, and fifteen canonical
reason/precondition scenarios. Every pair other than the single compatible
pair for each scenario returns `NOOP/UNKNOWN_INTENT` without mutation.
Same-side LONG+BUY and SHORT+SELL results restore exact HEAD
`side_after="long"` and `side_after="short"` output even when the stored side
snapshot is empty, opposite, or invalid.

The existing guard boundary in unchanged `loop.py` still blocks a denied
entry before `apply_paper_execution()` and therefore before the pure resolver.
Existing positions continue through the exit path. Tests prove both the
exactly-once call and the blocked-guard zero-call case.

Trade-log `exit_reason`, `pnl`, `pnl_net`, fee, duplicate suppression,
loss-cluster corrupt-state behavior, autonomous exits, position changes, and
audit reasons remain equal to the characterized baseline. TP/SL remains above
time stop, which remains above opposing intent. Autonomous exits use HOLD and
no synthetic opposing intent.

## 7. Final test evidence

All final commands below ran against the final source identities through the
repository `.venv`, with `PYTHONDONTWRITEBYTECODE=1`.

| Command | Tests | Result |
| --- | ---: | --- |
| `.venv/bin/python -m unittest tests.live_l1.test_paper_execution_control` | 25 | PASS |
| `.venv/bin/python -m unittest tests.live_l1.test_loss_cluster_state` | 18 | PASS |
| `.venv/bin/python -m unittest tests.live_l1.test_pre_execution_guards` | 6 | PASS |
| `.venv/bin/python -m unittest tests.live_l1.test_paper_economics_shadow_runtime` | 9 | PASS |
| `.venv/bin/python -m unittest discover -s tests/live_l1 -p 'test_*.py'` | 357 | PASS |
| `.venv/bin/python -m unittest discover -s tests/regression -p 'test_*.py'` | 170 | PASS |
| exact HEAD-baseline differential over full decisions, state, audit, trade and loss-gate calls | 5,120 | PASS, 0 mismatches |

Final aggregate command return code: `0`.

Compilation passed for all three implementation/test paths using the same
`.venv` and an isolated `PYTHONPYCACHEPREFIX` beneath `/tmp`. The initial
plain `python3 -m py_compile` attempt could not create repository-local
`__pycache__` on the read-only mount (`Errno 30`); it reported no source
syntax failure. The mandated compilation was then completed without changing
repository contents.

One preliminary regression invocation used the system Python rather than the
mandated repository `.venv`. It ran 170 tests but produced 49 environment
errors because that interpreter lacks `numpy`. The canonical `.venv`
invocation immediately afterward passed all 170 tests. No I1 assertion or
runtime behavior failed in either invocation.

`git diff --check`: PASS.

## 8. Preservation identities

| Read-only path | Mandate SHA-256 | Final SHA-256 | Result |
| --- | --- | --- | --- |
| `live_l1/core/loop.py` | `54e9e7bc0977a9c94f2e85a3279157678249a8569cff63f7d4f29131443fd058` | `54e9e7bc0977a9c94f2e85a3279157678249a8569cff63f7d4f29131443fd058` | PASS |
| `tests/live_l1/test_loss_cluster_state.py` | `0a7823175eb55d39d22d0576e1d58296d4b5123028e0fbfff561c1a6b642fe35` | `0a7823175eb55d39d22d0576e1d58296d4b5123028e0fbfff561c1a6b642fe35` | PASS |
| `tests/live_l1/test_pre_execution_guards.py` | `38192c5f96814bb0b3899e08453d3764cc1a14f9a7af52de218d4a2e0280248c` | `38192c5f96814bb0b3899e08453d3764cc1a14f9a7af52de218d4a2e0280248c` | PASS |
| `live_l1/core/paper_economics_shadow_runtime.py` | `8dbdf1ec0190e96bdb75697d1ffb25bd87784194150f674bb7e3317df6073a45` | `8dbdf1ec0190e96bdb75697d1ffb25bd87784194150f674bb7e3317df6073a45` | PASS |
| `live_l1/core/paper_iu4_adapter.py` | `d65525f31746d1edf30bf1ffc7f84a845f97b3f4120904c9910b741bc8c76a7b` | `d65525f31746d1edf30bf1ffc7f84a845f97b3f4120904c9910b741bc8c76a7b` | PASS |
| `live_l1/core/paper_iu4_startup_gate.py` | `86b191afb7725d613898d6911b543a84e9e0ada1f9c59822e3c47107272a6753` | `86b191afb7725d613898d6911b543a84e9e0ada1f9c59822e3c47107272a6753` | PASS |
| `live_l1/state/paper_atomic_coordinator.py` | `6460dbfc58acaf6ca0ac56120a1e7460e79981ead30959909f881deef563c1f5` | `6460dbfc58acaf6ca0ac56120a1e7460e79981ead30959909f881deef563c1f5` | PASS |

The Revision 21 specification and final R3 attestation also retain their
controlling hashes from Section 2.

## 9. Scope and non-mutation statement

The only I1 implementation mutations are the exact four paths in Section 3.
No `loop.py`, adapter, Atomic State/Transaction, runtime gate, lifecycle
ledger, authorization, terminal process, recovery, monitoring, profile,
configuration, launcher, scheduler, Workstation, R3, Research, GS, RCC002,
Exchange, Live, credential, state, or real-input artifact was changed.

No Workstation run, R3 run, validator run, runtime process control, real-data
test, staging, commit, fetch, push, cleanup, or deletion occurred. Foreign
untracked artifacts were left untouched. The excluded
`scripts/build_rcc002_spec_bundle.py` was not read, modified, executed,
staged, or committed.

## 10. Residual boundary

I1 proves pure control extraction and current OFF/SHADOW preservation only.
It does not implement or prove:

- an active ENFORCED consumer;
- Adapter Request V2 or explicit active control action transport;
- Atomic State/Transaction V2;
- Lifecycle Ledger, Runtime Gate, Authorization V2, terminal safety
  processes, recovery, monitoring, or activation;
- I2, I3, I4, I5, I6, I7, or I8 readiness;
- Exchange or live-trading safety or authorization.

Those remain governed by separate later packages and mandates.

## 11. Completion and next step

```text
I1_CHARACTERIZATION:PASS
I1_PURE_CONTROL_EXTRACTION:PASS
I1_LEGACY_DELEGATION:PASS
I1_ACTION_AUTHORITATIVE_DISPATCH:PASS
I1_M1_RESOLVED:PASS
I1_RR_M1_RESOLVED:PASS
I1_RR_M2_RESOLVED:PASS
I1_EXACT_HEAD_DIFFERENTIAL:5120/5120_PASS
I1_OFF_SHADOW_PARITY:PASS
I1_TESTS:PASS
I1_PRESERVATION:PASS
I1_SCOPE:PASS
I1_IMPLEMENTATION_RESULT:PASS
I2_AUTHORIZED:NO
```

The exact next governance step is:

```text
IU4-I1-CHARACTERIZATION-PURE-CONTROL-EXTRACTION-INDEPENDENT-READONLY-FILE-EXACT-REREVIEW-2
```

That review must independently inspect the complete final hashes, diff,
characterization evidence, pure negative-capability boundary, delegation, test
results, and file scope. I2 remains unauthorized until the independent I1
review passes and a separate file-exact I2 mandate is issued.
