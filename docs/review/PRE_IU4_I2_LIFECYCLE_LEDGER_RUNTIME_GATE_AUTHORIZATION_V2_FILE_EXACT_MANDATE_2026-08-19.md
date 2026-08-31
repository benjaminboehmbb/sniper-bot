# Pre-IU4 I2 Lifecycle Ledger / Runtime Gate / Authorization V2 — File-Exact Mandate — 2026-08-19

## 1. Mandate decision

This record grants the separate file-exact mandate required after independent
I1 acceptance for Revision 21 implementation package I2 only.

```text
MANDATE_ID:IU4-I2-LIFECYCLE-LEDGER-RUNTIME-GATE-AUTHORIZATION-V2-FILE-EXACT-MANDATE
MANDATE_RESULT:AUTHORIZED
IMPLEMENTATION_PACKAGE:I2_ONLY
I2_IMPLEMENTATION_AUTHORIZED:YES_WITHIN_EXACT_FILE_SCOPE
I1_ACCEPTED:YES
I3_THROUGH_I8_AUTHORIZED:NO
ADAPTER_REQUEST_V2_AUTHORIZED:NO
ATOMIC_STATE_TRANSACTION_V2_AUTHORIZED:NO
ACTIVE_EXECUTION_SEAM_AUTHORIZED:NO
ENFORCED_LOOP_AUTHORIZED:NO
ENFORCED_ACTIVATION_AUTHORIZED:NO
EXCHANGE_AUTHORIZED:NO
LIVE_AUTHORIZED:NO
```

This mandate creation does not implement I2. It authorizes only the later,
separately invoked I2 implementation workstream and only while every identity,
file boundary and fail-closed condition below remains exact.

## 2. Controlling identity

```text
CANONICAL_REPOSITORY:/home/benja/projects/sniper-bot
HEAD:c7ce0452aa2ccbf08c462784d68fa07b3dfe9595
MAIN:c7ce0452aa2ccbf08c462784d68fa07b3dfe9595
ORIGIN_MAIN:89e13fecd1ab549ca7099818b1c9ad4984cb6f7a
MAIN_DIVERGENCE_BEHIND_AHEAD:0/6
```

| Controlling artifact | SHA-256 | Lines | Result |
| --- | --- | ---: | --- |
| Revision 21 specification | `ab8f80720a1d8fe49b9085bce63658bcaecf7f0a3ea70fb555559223090824e0` | 4,605 | complete and controlling |
| Revision 21 independent rereview | `6618955e67bf9e11798c103eb7d01823dc2ece4c39a66575dbb668c4162c0c7c` | 752 | `READY`, `0/0/0/0` |
| Revision 21 terminal R3 handoff | `0aecf831429076a7b732ca6de2482ba02384792919c3f76a3232c1ef27863b2e` | 140 | complete |
| Revision 21 final R3 attestation | `587c5a5ffed271534d661c6c816781eb8443d5c6318fe14d26b1947d21340851` | 179 | final R3 `PASS` |
| I1 file-exact mandate | `2b235193bb7d2986cac3a42e3b078569e1c5e1070e315f6b6b99cc99823bad4a` | 296 | authorized |
| I1 implementation evidence | `24328abbb0e918b0ff5009e32cb026b8624c26dd2bc66fcae49789df55f4b856` | 318 | final I1 identity |
| I1 independent rereview 2 | `adc13abbec3a0458d712df729c2732bce8897be7ecf991a312839616e9687804` | 391 | `READY`, `0/0/0/0`, I1 accepted |

Revision 21 Section 20 is decisive: I2 is Lifecycle Ledger, Runtime Gate and
Authorization V2. Adapter Request V2 remains I4 and is not pulled forward by
this mandate.

## 3. I2 objective and ceiling

I2 implements only the dormant, additive control-plane and terminal-safety
foundation required before Atomic V2 or an active adapter can exist:

1. Authorization V2, Restart/Recovery Authorization V1, strict external
   loaders and independent trust-anchor validation;
2. append-only Lifecycle Ledger V1, self-reference-free Authority
   PREPARE/target/COMMIT generations, one-time authorization consumption,
   Runtime Session records and read-only derived views;
3. the single mode-neutral runtime gate, including strict mode, profile, Git,
   authorization, reconciliation, owner and handoff classification;
4. additive OFF/SHADOW delegation without changing current behavior;
5. Terminal Parent Guardian V13, Native Trip Broker V10, Kernel Lease Shim
   V11, Handoff Revocation Attestor V1, Socket LSM Guard V3, Persistence
   Worker V8 and Capability Profile V14 validation; and
6. an additive safe-launch preflight that refuses ENFORCED loop entry while
   I3, I4 and I5 are absent.

I2 does not create Atomic V2 state, execute Genesis or a real owner handoff,
send Adapter V2 requests, enter an ENFORCED loop or activate a profile. Tests
use only synthetic payloads, test-owned child processes and temporary roots.

## 4. Exact authorized file set

### 4.1 New production, native and validation files

All paths below are absent at mandate time.

| Path | Authorized purpose |
| --- | --- |
| `live_l1/core/paper_iu4_runtime_gate.py` | sole mode-neutral gate and immutable binding result |
| `live_l1/core/terminal_runtime_protocol.py` | versioned Python terminal/session/channel/close protocol records |
| `live_l1/core/terminal_parent_guardian.py` | Guardian V13 and test-owned process supervision |
| `live_l1/core/terminal_persistence_worker.py` | isolated Persistence Worker V8 |
| `live_l1/state/iu4_lifecycle_ledger.py` | Ledger V1, manifests, PREPARE/COMMIT, sessions and reconciliation |
| `live_l1/native/terminal_lease_protocol_v14.h` | shared native ABI and compile-time assertions |
| `live_l1/native/terminal_native_trip_broker.c` | Native Trip Broker V10 and sole runtime Control Word writer |
| `live_l1/native/terminal_kernel_lease_shim.c` | Kernel Lease Shim V11 and PIDFD fail-stop fallback |
| `live_l1/native/terminal_handoff_revocation_attestor.c` | disjoint Handoff Revocation Attestor V1 |
| `live_l1/native/terminal_runtime_socket_lsm_guard.bpf.c` | six-hook Socket LSM Guard V3 and phase CMPXCHG |
| `live_l1/native/terminal_lease_fault_fixture.c` | test-only native fault fixture |
| `live_l1/tools/validate_terminal_lease_capability.py` | Capability Profile V14 validator and evidence serializer |
| `live_l1/tools/terminal_lease_side_effect_observer.py` | external signal/syscall/channel/reference observer |

Native outputs and BPF pins/maps/links must stay under a unique test-owned
temporary root. No generated source, object, binary or build artifact may be
added to the repository.

### 4.2 Existing files permitted additive modification

| Path | Mandate-time SHA-256 | Lines | Authorized change |
| --- | --- | ---: | --- |
| `live_l1/core/paper_iu4_startup_gate.py` | `86b191afb7725d613898d6911b543a84e9e0ada1f9c59822e3c47107272a6753` | 600 | Authorization V2/restart contracts and strict loaders; preserve V1 behavior |
| `live_l1/core/paper_iu4_shadow_runtime_gate.py` | `f81045347e82b981bd721bf1c4bbe0133feb8a36146f6440358983cac2ad6d4e` | 403 | thin OFF/SHADOW facade to sole mode-neutral gate |
| `live_l1/core/paper_iu4_shadow_observation_gate.py` | `ed4e75fad664c68b91950e9c09e873823ebe3eb0b0062f85806daa09ce661350` | 886 | type-safe delegation, no parallel authority |
| `live_l1/tools/safe_launch.py` | `cb90bd49b36de56e8ad95e9b24febb23baa0513b1ec51e7402f63a5efd6ec652` | 201 | strict preflight and gate invocation; no ENFORCED loop start |
| `tests/live_l1/test_paper_iu4_startup_gate.py` | `29d07a9c19aabcf369de101fd9599413a7f20ee03685eb96495993cad5588034` | 537 | additive V2/loader/trust/tamper tests |
| `tests/live_l1/test_paper_iu4_shadow_runtime_gate.py` | `645634609464fb6d7d43c3b46d85292d48a2666f897d27b58fb2966c1fc43b05` | 287 | delegation and exact parity tests |
| `tests/live_l1/test_paper_iu4_shadow_observation_gate.py` | `1309febdabfb4fac7a6fd800d312733f451485a95d705bcbea14d5bc8315f7aa` | 782 | facade and no-parallel-authority tests |
| `tests/live_l1/test_safe_launch_iu4_shadow_runtime_gate.py` | `388b1f9764a55c341f40a2df318670843610bc055221c0608a3600d754460cf0` | 165 | strict preflight, parity and ENFORCED fail-closed tests |

### 4.3 New focused tests and evidence

All paths below are absent at mandate time.

| Path | Authorized purpose |
| --- | --- |
| `tests/live_l1/test_iu4_lifecycle_ledger.py` | chain, lock, fsync, views, PREPARE/COMMIT, consumption and crash matrix |
| `tests/live_l1/test_paper_iu4_runtime_gate.py` | mode/profile/Git/auth/owner/handoff/session decisions |
| `tests/live_l1/test_terminal_parent_guardian.py` | Guardian, control word, heartbeat, PIDFD and close/kill FSM |
| `tests/live_l1/test_terminal_persistence_worker.py` | worker peer, binding, idempotence, deadline, fencing and gap tests |
| `tests/live_l1/test_terminal_lease_capability.py` | native ABI, broker, shim, attestor, Socket LSM and Capability V14 |
| `docs/review/PRE_IU4_I2_LIFECYCLE_LEDGER_RUNTIME_GATE_AUTHORIZATION_V2_IMPLEMENTATION_EVIDENCE_2026-08-19.md` | exact identities, tests, capability evidence and scope |

No additional source, test, fixture, header, manifest, configuration,
documentation or evidence path is authorized. A necessary extra path stops I2
and requires a revised mandate.

## 5. Explicitly read-only preservation boundary

| Path | Required SHA-256 | Lines |
| --- | --- | ---: |
| `live_l1/core/paper_iu4_adapter.py` | `d65525f31746d1edf30bf1ffc7f84a845f97b3f4120904c9910b741bc8c76a7b` | 641 |
| `live_l1/state/paper_atomic_coordinator.py` | `6460dbfc58acaf6ca0ac56120a1e7460e79981ead30959909f881deef563c1f5` | 1,799 |
| `live_l1/state/paper_artifacts.py` | `673d7d254c2b3a9b7b5aba8652aae04d6b5411d5a3079cedb9d23602a283d94f` | 1,136 |
| `live_l1/core/loop.py` | `54e9e7bc0977a9c94f2e85a3279157678249a8569cff63f7d4f29131443fd058` | 1,411 |
| `live_l1/state/loss_cluster.py` | `a82259e91df12191f2775584094b2febbe7a5efb7a0107dd642e55b37cca1bb6` | 406 |
| `live_l1/state/state_store.py` | `50a85cf6bd382850d39e69cd785a5dc2ded0a66a1d82856b4baa11877bdba177` | 220 |
| `live_l1/state/models.py` | `3254d2f1a6509ec5f8f623dd8f286f60cfcc108f66f2d8eb107338d795115c7e` | 27 |
| `live_l1/core/paper_economics.py` | `a302013134d1265ac85ad10b57a67ead9e2343043f7eb499fd965a44312525ae` | 730 |
| `live_l1/core/paper_entry_throttle.py` | `ad5447d88a2c35c9a71a5495c61c8f08fa844daf60e79d4a872234e88037df75` | 727 |
| `live_l1/core/paper_execution_control.py` | `7d3cb901c1c67c8df85e99bc579fda85d8732b634ff4747e08620b92ac1e44f7` | 257 |
| `live_l1/core/execution.py` | `5aed85ce2754dbb4d8984a1d699b607e3a522ed6da000df119ecd782a4e764d8` | 1,147 |
| `tests/live_l1/test_paper_execution_control.py` | `0ae44f2d32f5f3b6affe37a258be0e6aee06790f857e4fc01628c6795bda99e5` | 843 |

Revision 21, R3, I1 governance, the frozen validator and Workstation R3
artifacts are immutable inputs.

## 6. Authorization and loader contract

I2 must preserve `IU4ActivationAuthorizationV1` and add V2 exactly as
Revision 21 Sections 7.1–7.5 require. V2 rejects missing/unknown fields,
noncanonical values, incomplete commits, payload/hash mismatch, non-ENFORCED
approval, profile/control/R3/evidence/authority mismatch and invalid windows.

The loader requires one explicit absolute regular-file path outside checkout,
state, logs and bot-writable outputs; rejects symlinks, unsafe ownership or
permissions, fallback search and multiple candidates; and never infers the
independent trust anchor from payload or filename.

`IU4RestartRecoveryAuthorizationV1` implements all four operations and exact
sentinels from Section 7.6. Recovery, PREPARE completion and terminal-gap
reconciliation never become loop starts. The Ledger consumes authorization
exactly once before the operation.

## 7. Lifecycle Ledger contract

`IU4LifecycleLedgerV1` is append-only, monotonic, hash-chained and the sole
owner-epoch/lifecycle authority. It must use exclusive locking, create-new
publication, full write, file and directory fsync and readback; reject
truncation, unknown records, gaps, forks, duplicates and reused authorization;
derive ledger tip, authority commit anchor and generation separately; implement
all Section 7.7 records; preserve the acyclic business→generation→core→
PREPARE→target→COMMIT order and DIRECT/RECOVERED provenance; and classify open
PREPAREs or unclosed sessions fail-closed. Real Atomic materialization remains
absent until I3. All write tests use fresh temporary roots.

## 8. Mode-neutral Runtime Gate contract

`paper_iu4_runtime_gate.py` is the sole Revision 21 Section 8 gate truth.
It owns strict raw mode/profile parsing, repository/profile/control binding,
Authorization V2, reconciliation, owner/handoff classification, session
status, stable reasons and `assert_current_binding()`.

- OFF remains Legacy-only; SHADOW remains Legacy plus read-only observation.
- ENFORCED remains `passed=false`, adapter/state mutation disabled until
  separately accepted I3/I4/I5 identities and activation exist.
- V1 authorization is rejected for ENFORCED but existing V1 tests remain.
- Git/import/profile/trust/owner/PREPARE/session/handoff ambiguity fails closed.
- Shadow facades contain no second profile, Git, coordinator or owner truth.
- `safe_launch.py` cannot mutate by preflight or enter ENFORCED in I2.

## 9. Terminal capability contract

Every field, length, peer direction, FD, nonce, fingerprint, deadline, state
transition and failure classification in Revision 21 Sections 7.8.1 and 7.8.2
is mandatory. Partial broker/shim/guardian/worker/channel/LSM implementations
cannot pass.

The implementation proves the single-writer lock-free Control Word V3; exact
memfd creation/sealing/mappings; fixed SelfKill/signal/seccomp/PIDFD fallback;
separate bound roles; six channels, three disjoint grant sockets and twelve
sealed endpoints; six LSM hooks with pre-visibility tags and hook-only atomic
phase transitions; exactly ordered listener/revocation/bootstrap/durable-open/
release states; PREPARE→Broker-CLOSED→durable COMMIT clean close; no terminal
pipe transfer or post-trip renewal; isolated blocking persistence; and an exact
Linux/WSL environment binding. Unsupported platforms fail closed.

Test-owned children, namespaces, cgroups, sockets, BPF objects, memfds, pidfds,
timers and eventfds are authorized only under unique temporary roots and may
target no existing process/session. Elevated Linux capabilities require
explicit execution approval at test time; this mandate grants scope, not
privilege escalation.

## 10. Mandatory fault and test matrix

The implementation covers every applicable Revision 21 Section 21.5–21.7 case:
authorization/trust/path/time/tamper/consumption; ledger fork/crash/fsync/
provenance/session; synthetic handoff; all close message errors/peers/retries/
duplicates; listener/Yama/FD/revocation; every LSM/tag/options/SCM_RIGHTS/map/
CMPXCHG/send-gate adversary and reference cleanup; role death/stop/suspend/
signal/PIDFD/timer/clock/resource/deadline; terminal-gap idempotence; and exact
Capability V14 with 10,000 trials per certification scenario plus 32 startup
probes per required scenario.

No skip, xfail, mocked-kernel PASS, downgrade or reduced trial count can pass.
Unsupported capability blocks I2.

## 11. Required implementation order

1. Reverify identities/absence/preservation and record existing baselines.
2. Implement protocol records and authorization/loaders.
3. Implement/test Lifecycle Ledger in temporary roots.
4. Implement mode-neutral gate without ENFORCED loop.
5. Convert Shadow gates to thin delegation and prove exact parity.
6. Implement native ABI, broker, shim, attestor, LSM, guardian and worker.
7. Implement validator, observer and all native/kernel fault tests.
8. Modify safe launch last; prove side-effect-free preflight/fail-closed I2.
9. Run all focused/full/regression/native/capability gates.
10. Reverify preservation/scope and only then create implementation evidence.

## 12. Required verification commands

All commands use the repository `.venv`, `PYTHONDONTWRITEBYTECODE=1`,
isolated pycache and temporary roots. At minimum:

```bash
.venv/bin/python -m unittest tests.live_l1.test_paper_iu4_startup_gate
.venv/bin/python -m unittest tests.live_l1.test_iu4_lifecycle_ledger
.venv/bin/python -m unittest tests.live_l1.test_paper_iu4_runtime_gate
.venv/bin/python -m unittest tests.live_l1.test_paper_iu4_shadow_runtime_gate
.venv/bin/python -m unittest tests.live_l1.test_paper_iu4_shadow_observation_gate
.venv/bin/python -m unittest tests.live_l1.test_safe_launch_iu4_shadow_runtime_gate
.venv/bin/python -m unittest tests.live_l1.test_terminal_parent_guardian
.venv/bin/python -m unittest tests.live_l1.test_terminal_persistence_worker
.venv/bin/python -m unittest tests.live_l1.test_terminal_lease_capability
.venv/bin/python -m unittest discover -s tests/live_l1 -p 'test_*.py'
.venv/bin/python -m unittest discover -s tests/regression -p 'test_*.py'
.venv/bin/python -m py_compile <all-authorized-python-paths>
.venv/bin/python live_l1/tools/validate_terminal_lease_capability.py --certification-trials 10000 --startup-probes 32 --output-root <unique-temporary-root>
git diff --check
```

Native compilation uses explicit recorded compiler/target/include/warning/
standard/optimization/reproducibility flags and temporary outputs. Evidence
binds compiler/linker, kernel/config/BTF/JIT/LSM/Yama/cgroup/namespace/clock/
signal/page/atomic, binary/object/BPF/map/link and profile fingerprints.

Mandate-time baselines:

```text
test_paper_iu4_startup_gate:12/12_PASS
test_paper_iu4_shadow_runtime_gate:10/10_PASS
test_paper_iu4_shadow_observation_gate:18/18_PASS
test_safe_launch_iu4_shadow_runtime_gate:3/3_PASS
```

## 13. Evidence and completion gate

Evidence must bind all starting/final identities, absent/create claims, exact
commands/counts/return codes/skips, authorization and ledger matrices, OFF/
SHADOW parity and ENFORCED non-entry, native ABI/binaries, full Capability V14
environment/trials/probes, all terminal fault/reference-cleanup outcomes,
preservation/scope, no real-state mutation and residual I3/I4/I5 boundaries.
It reports exactly `I2_RESULT:PASS` or `I2_RESULT:BLOCKED`.

I2 passes only if the entire finite native/kernel Capability V14 passes.
Contract-only success with missing capability evidence is insufficient.

## 14. Prohibited scope

I2 does not authorize files outside Section 4; I3 Atomic V2/S4V2/Entry Quote/
Progress/Loss migration; I4 Adapter V2 or Adapter V1 modification; I5 loop/
execution wiring or I1 changes; real ENFORCED entry, handoff, Genesis/recovery,
activation, Exchange or Live; Research/GS/RCC002/engine/run_engine; Workstation/
R3/validator/scheduler/launcher rerun or existing process/state mutation; Git
stage/commit/fetch/push/cleanup; foreign artifact changes; or reading,
modifying, executing, staging or committing
`scripts/build_rcc002_spec_bundle.py`.

## 15. Exact next governance step

```text
IU4-I2-LIFECYCLE-LEDGER-RUNTIME-GATE-AUTHORIZATION-V2-IMPLEMENTATION
```

That workstream may touch only Section 4 paths. After passing evidence, the
next action is an independent read-only file-exact I2 review. I3 remains
unauthorized until I2 receives independent `READY` and a separate I3 mandate.
