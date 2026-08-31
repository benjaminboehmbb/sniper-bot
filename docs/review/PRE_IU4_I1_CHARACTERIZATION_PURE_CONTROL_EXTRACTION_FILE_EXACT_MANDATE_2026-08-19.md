# Pre-IU4 I1 Characterization / Pure Control Extraction — File-Exact Mandate — 2026-08-19

## 1. Mandate decision

This record grants the separate, file-exact mandate required by the Revision
21 specification and its final R3 attestation for implementation package I1
only.

```text
MANDATE_ID:IU4-I1-CHARACTERIZATION-PURE-CONTROL-EXTRACTION-FILE-EXACT-MANDATE
MANDATE_RESULT:AUTHORIZED
IMPLEMENTATION_PACKAGE:I1_ONLY
I1_IMPLEMENTATION_AUTHORIZED:YES_WITHIN_EXACT_FILE_SCOPE
I2_THROUGH_I8_AUTHORIZED:NO
IU4_ENFORCED_WIRING_AUTHORIZED:NO
ENFORCED_ACTIVATION_AUTHORIZED:NO
EXCHANGE_AUTHORIZED:NO
LIVE_AUTHORIZED:NO
```

The authorization is conditional on all identities and boundaries in this
record remaining exact. It authorizes no code change in this mandate-creation
turn; it authorizes the separately invoked I1 implementation workstream.

## 2. Controlling governance identity

```text
CANONICAL_REPOSITORY:/home/benja/projects/sniper-bot
HEAD:c7ce0452aa2ccbf08c462784d68fa07b3dfe9595
MAIN:c7ce0452aa2ccbf08c462784d68fa07b3dfe9595
ORIGIN_MAIN:89e13fecd1ab549ca7099818b1c9ad4984cb6f7a
MAIN_DIVERGENCE_BEHIND_AHEAD:0/6
```

| Controlling artifact | SHA-256 | Lines | Result |
| --- | --- | ---: | --- |
| `docs/LIVE_DESIGN_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPEC.md` | `ab8f80720a1d8fe49b9085bce63658bcaecf7f0a3ea70fb555559223090824e0` | 4,605 | Revision 21 complete |
| `docs/review/PRE_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPECIFICATION_REVISION_21_INDEPENDENT_READONLY_REREVIEW_2026-08-19.md` | `6618955e67bf9e11798c103eb7d01823dc2ece4c39a66575dbb668c4162c0c7c` | 752 | `READY`, findings `0/0/0/0` |
| `docs/review/PRE_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPECIFICATION_REVISION_21_TERMINAL_R3_HANDOFF_2026-08-19.md` | `0aecf831429076a7b732ca6de2482ba02384792919c3f76a3232c1ef27863b2e` | 140 | handoff complete |
| `docs/review/PRE_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPECIFICATION_REVISION_21_FINAL_R3_ATTESTATION_2026-08-19.md` | `587c5a5ffed271534d661c6c816781eb8443d5c6318fe14d26b1947d21340851` | 179 | final R3 `PASS` |

The final R3 attestation is terminal and binds the exact evidence, journal,
code, input, profile, specification, handoff, and one-shot validator
identities. I1 must not mutate, rerun, replace, or reinterpret that chain.

## 3. I1 objective and ceiling

I1 has exactly two ordered objectives:

1. characterize the current `apply_paper_execution()` control behavior before
   altering its implementation; and
2. extract only its pure action/reason selection into
   `live_l1/core/paper_execution_control.py`, with the existing Legacy
   execution function delegating to that pure result while preserving every
   current OFF/SHADOW externally observable behavior.

I1 must end with:

- unchanged OFF and SHADOW action, reason, position-transition, guard,
  trade-log, audit-log, loss-cluster, fee, PnL, and persistence behavior;
- a pure deterministic control function that returns only the action and
  stable reason code required by Revision 21 Section 11;
- no active ENFORCED consumer, adapter request V2, Atomic V2, runtime gate,
  authorization, lifecycle ledger, terminal process, recovery, monitoring, or
  activation change.

I1 is not permission to improve, normalize, repair, or reinterpret surprising
Legacy behavior. A characterization/specification conflict stops I1 as
`BLOCKED` and requires a separate governance decision.

## 4. Exact authorized file set

Only the following four paths may be created or modified by the later I1
implementation workstream.

| Path | Operation | Starting identity | Authorized purpose |
| --- | --- | --- | --- |
| `live_l1/core/paper_execution_control.py` | create | absent at mandate | pure deterministic action/reason selection only |
| `live_l1/core/execution.py` | modify | SHA-256 `a76f600d27feef969665bcd695ce11bc4e3abae0f25e045f7416fc78cd2513e3`, 951 lines | delegate control selection while preserving all existing mutations and side effects |
| `tests/live_l1/test_paper_execution_control.py` | create | absent at mandate | baseline characterization, pure-contract, delegation, and parity tests using synthetic/temp inputs only |
| `docs/review/PRE_IU4_I1_CHARACTERIZATION_PURE_CONTROL_EXTRACTION_IMPLEMENTATION_EVIDENCE_2026-08-19.md` | create after tests | absent at mandate | exact before/after identities, characterization result, commands, counts, outcomes, scope, and next decision |

No rename, alternative path, fixture file, generated source file, additional
test module, helper module, configuration file, or documentation sidecar is
authorized. If one of those becomes technically necessary, I1 stops before
creating it and requests a revised file-exact mandate.

## 5. Explicitly read-only preservation files

The following directly adjacent files are preservation inputs and must remain
byte-identical throughout I1:

| Path | Mandate-time SHA-256 | Lines |
| --- | --- | ---: |
| `live_l1/core/loop.py` | `54e9e7bc0977a9c94f2e85a3279157678249a8569cff63f7d4f29131443fd058` | 1,411 |
| `tests/live_l1/test_loss_cluster_state.py` | `0a7823175eb55d39d22d0576e1d58296d4b5123028e0fbfff561c1a6b642fe35` | 413 |
| `tests/live_l1/test_pre_execution_guards.py` | `38192c5f96814bb0b3899e08453d3764cc1a14f9a7af52de218d4a2e0280248c` | 253 |
| `live_l1/core/paper_economics_shadow_runtime.py` | `8dbdf1ec0190e96bdb75697d1ffb25bd87784194150f674bb7e3317df6073a45` | 183 |
| `live_l1/core/paper_iu4_adapter.py` | `d65525f31746d1edf30bf1ffc7f84a845f97b3f4120904c9910b741bc8c76a7b` | 641 |
| `live_l1/core/paper_iu4_startup_gate.py` | `86b191afb7725d613898d6911b543a84e9e0ada1f9c59822e3c47107272a6753` | 600 |
| `live_l1/state/paper_atomic_coordinator.py` | `6460dbfc58acaf6ca0ac56120a1e7460e79981ead30959909f881deef563c1f5` | 1,799 |

The Revision 21 specification, rereview, terminal handoff, final R3
attestation, this mandate, the frozen R3 validator, and all Workstation R3
artifacts are also immutable inputs.

## 6. Required implementation order

The later I1 workstream must execute in this order:

1. reverify repository, controlling-record, existing-file, and absent-path
   identities from Sections 2, 4, and 5;
2. create the characterization portion of
   `tests/live_l1/test_paper_execution_control.py` without changing either
   authorized code file;
3. run those characterization tests against the exact mandate-time
   `execution.py` and record their command and result before extraction;
4. if any observed priority, boundary, action, reason, or mutation differs
   from Revision 21 Section 11 or this mandate, stop `BLOCKED` without changing
   production code;
5. create the pure module;
6. minimally modify `execution.py` to delegate control selection to the pure
   module while retaining all mutation, I/O, logging, loss-cluster,
   settlement, and persistence work in `execution.py`;
7. complete pure-contract, delegation, and before/after parity tests in the
   one authorized test module;
8. run the mandatory focused and regression commands in Section 10;
9. verify the exact four-path mutation ceiling and every preservation hash;
10. create the I1 implementation evidence record only after all required
    checks pass.

The pre-extraction characterization result must be preserved in the evidence
record. Replacing it with only post-extraction assertions is insufficient.

## 7. Pure-control contract

The new module must be import-safe, deterministic, and side-effect-free. Its
public result is immutable and contains only:

- one action from `NOOP`, `OPEN_LONG`, `OPEN_SHORT`, `CLOSE_LONG`,
  `CLOSE_SHORT`; and
- one existing stable reason code.

All required inputs must be explicit values. The pure module must not:

- receive or mutate the runtime `state` object;
- import `loop.py`, adapter, exchange, logging, state-store, loss-cluster
  store, economics, coordinator, or runtime-gate modules;
- read environment variables, clocks, files, sockets, processes, or global
  mutable state;
- write logs, evidence, state, or files;
- compute or apply quantity, fill price, fee, PnL, settlement, throttle, or
  loss-cluster persistence;
- call an adapter, broker, exchange, or persistence API;
- synthesize an opposing BUY/SELL intent for TP, SL, or time-stop exits.

`execution.py` remains the Legacy side-effect owner. It may resolve the
existing environment-derived TP/SL and time-stop settings, snapshot the
current position values, obtain the existing loss-cluster entry-permission
outcome, call the pure function exactly once, and then apply the returned
action through the unchanged Legacy mutation/logging path.

The extraction must preserve these existing reason codes where applicable:

```text
TP_LONG_HIT
SL_LONG_HIT
TP_SHORT_HIT
SL_SHORT_HIT
LONG_TIME_STOP_HIT
SHORT_TIME_STOP_HIT
HOLD_NO_EXECUTION
BUY_FROM_FLAT
BUY_ALREADY_LONG
BUY_CLOSES_SHORT
SELL_FROM_FLAT
SELL_ALREADY_SHORT
SELL_CLOSES_LONG
LOSS_CLUSTER_GATE_BLOCKED_ENTRY
UNKNOWN_INTENT
```

No reason-code rename, alias, translation, or new fallback is authorized.

## 8. Mandatory characterization matrix

The pre- and post-extraction tests must cover at least:

1. `FLAT` with BUY, SELL, HOLD, and unknown intent;
2. `LONG` and `SHORT` with same-side, opposing, and HOLD intent;
3. LONG TP and SL immediately below, exactly at, and immediately above each
   boundary;
4. SHORT TP and SL immediately below, exactly at, and immediately above each
   boundary;
5. LONG and SHORT time stops immediately before and exactly at the configured
   duration;
6. price-exit priority over time stop and opposing intent;
7. time-stop priority over opposing intent;
8. valid and invalid/missing entry snapshots exactly as handled by the
   mandate-time Legacy implementation;
9. loss-cluster entry allow, active pause, corrupt-state fail-closed, and
   existing-position exit despite corrupt loss-cluster state;
10. unchanged action, reason, `executed`, position before/after, side, entry
    price, entry timestamp, audit events, trade-log records, loss-cluster
    updates, fee/PnL fields, and duplicate-trade behavior;
11. the pure call leaves every input unchanged and performs no filesystem,
    environment, logging, adapter, exchange, or persistence access;
12. Legacy delegation calls the pure resolver exactly once for each execution
    evaluation and never calls it from a blocked pre-execution entry path that
    the existing guard rejects before `apply_paper_execution()`;
13. OFF and SHADOW produce identical actions, reasons, and position
    transitions to the mandate-time baseline on synthetic bound inputs;
14. autonomous TP/SL/time-stop exits close explicitly without a synthetic
    opposing intent.

The tests must use inline synthetic objects and temporary directories only.
Real market/research inputs, the 100K artifacts, and the terminal R3 evidence
or journal must not be read.

## 9. Prohibited scope

I1 does not authorize:

- any change to `live_l1/core/loop.py`;
- any adapter V2, Atomic State/Transaction V2, runtime-gate, lifecycle-ledger,
  authorization, terminal guardian/broker/shim/worker, recovery, monitoring,
  profile, configuration, launcher, scheduler, or Workstation code;
- I2, I3, I4, I5, I6, I7, or I8 implementation;
- changes under `engine/`, `run_engine/`, `scripts/state_research/`, Research,
  GS, RCC002, Exchange, Live, credentials, or production state;
- edits to `paper_economics.py`, S2 V2, Paper Account, Trade V2, Canonical
  Price Carrier, Entry Throttle, adapter/coordinator V1 contracts, or existing
  evidence;
- an IU4 ENFORCED execution path or any change in OFF/SHADOW authority;
- a Workstation run, R3 rerun, validator rerun, scheduler mutation, runtime
  process control, real-data test, source-state mutation, Exchange connection,
  or live trading;
- staging, commit, push, fetch, cleanup, deletion, or alteration of foreign
  untracked artifacts;
- reading, modifying, executing, staging, or committing
  `scripts/build_rcc002_spec_bundle.py`.

## 10. Required verification commands

The later I1 workstream must run, with `PYTHONDONTWRITEBYTECODE=1`, at least:

```bash
python3 -m unittest tests.live_l1.test_paper_execution_control
python3 -m unittest tests.live_l1.test_loss_cluster_state
python3 -m unittest tests.live_l1.test_pre_execution_guards
python3 -m unittest tests.live_l1.test_paper_economics_shadow_runtime
python3 -m unittest discover -s tests/live_l1 -p 'test_*.py'
python3 -m unittest discover -s tests/regression -p 'test_*.py'
python3 -m py_compile live_l1/core/paper_execution_control.py live_l1/core/execution.py tests/live_l1/test_paper_execution_control.py
git diff --check
```

Tests may write only to their own temporary directories. Any failure,
unexpected skip, real-input dependency, or preservation-hash mismatch blocks
I1 completion. Passing adjacent tests does not replace the focused new-module
test.

## 11. Evidence and completion gate

The authorized implementation evidence record must contain:

- all controlling identities from Section 2;
- all mandate-time and final identities for the four authorized paths;
- proof that the three create-targets were absent at mandate time;
- the exact pre-extraction characterization command and result;
- the complete characterized priority/boundary table;
- the exact post-extraction commands, counts, outcomes, and return codes;
- explicit pure-module negative-capability results;
- exact preservation-file hashes from Section 5 after implementation;
- `git diff --check` and exact scope output;
- confirmation that no R3, Workstation, Research, Exchange, Live, state,
  scheduler, staging, commit, or push mutation occurred;
- all known residual limits and no claim of I2+ readiness;
- an unambiguous I1 `PASS` or `BLOCKED` result.

I1 is complete only if characterization, pure extraction, Legacy delegation,
OFF/SHADOW parity, focused tests, the full `tests/live_l1` suite, regression
tests, preservation hashes, and scope checks all pass.

## 12. Next governance step

The exact next workstream authorized by this mandate is:

```text
IU4-I1-CHARACTERIZATION-PURE-CONTROL-EXTRACTION-IMPLEMENTATION
```

That workstream may touch only the four paths in Section 4. After a passing I1
implementation evidence record, the next action is an independent, read-only,
file-exact I1 review. I2 remains unauthorized until that review passes and a
separate I2 mandate exists.
