# Pre-IU4 I1 Characterization / Pure Control Extraction — Independent Read-Only File-Exact Rereview 2 — 2026-08-19

## 1. Independent decision

The final I1 package is **ready** for independent acceptance. This second
rereview independently reconstructed the exact `HEAD` baseline, the complete
consumer compatibility boundary and the previously failing malformed-snapshot
surface. It found no remaining defect.

```text
REREVIEW_ID:IU4-I1-CHARACTERIZATION-PURE-CONTROL-EXTRACTION-INDEPENDENT-READONLY-FILE-EXACT-REREVIEW-2
REREVIEW_RESULT:READY
BLOCKER:0
HIGH:0
MEDIUM:0
LOW:0
I1_RR_M1_INDEPENDENTLY_CLOSED:YES
I1_RR_M2_INDEPENDENTLY_CLOSED:YES
I1_IMPLEMENTATION_ACCEPTED:YES
I2_IMPLEMENTATION_AUTHORIZED:NO
IU4_ENFORCED_WIRING_AUTHORIZED:NO
ENFORCED_ACTIVATION_AUTHORIZED:NO
EXCHANGE_AUTHORIZED:NO
LIVE_AUTHORIZED:NO
```

No acceptance credit was taken from the resolution or implementation
evidence. The final code, test module, tracked diff and exact `HEAD` baseline
were inspected and exercised independently before this record was created.

## 2. Repository and controlling identity

```text
CANONICAL_REPOSITORY:/home/benja/projects/sniper-bot
BRANCH:main
HEAD:c7ce0452aa2ccbf08c462784d68fa07b3dfe9595
MAIN:c7ce0452aa2ccbf08c462784d68fa07b3dfe9595
ORIGIN_MAIN:89e13fecd1ab549ca7099818b1c9ad4984cb6f7a
MAIN_BEHIND_ORIGIN:0
MAIN_AHEAD_OF_ORIGIN:6
```

| Controlling artifact | SHA-256 | Lines | Independent result |
| --- | --- | ---: | --- |
| Revision 21 specification, `docs/LIVE_DESIGN_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPEC.md` | `ab8f80720a1d8fe49b9085bce63658bcaecf7f0a3ea70fb555559223090824e0` | 4,605 | MATCH |
| Revision 21 independent rereview | `6618955e67bf9e11798c103eb7d01823dc2ece4c39a66575dbb668c4162c0c7c` | 752 | MATCH / `READY` |
| Revision 21 terminal R3 handoff | `0aecf831429076a7b732ca6de2482ba02384792919c3f76a3232c1ef27863b2e` | 140 | MATCH |
| Revision 21 final R3 attestation | `587c5a5ffed271534d661c6c816781eb8443d5c6318fe14d26b1947d21340851` | 179 | MATCH / final R3 `PASS` |
| I1 file-exact mandate | `2b235193bb7d2986cac3a42e3b078569e1c5e1070e315f6b6b99cc99823bad4a` | 296 | MATCH / `AUTHORIZED` |
| first independent I1 review | `bbc9a4c3dfd3f1f05528e8a28d7ae04a212442624201eaaf804bc2cf4ef380c3` | 425 | MATCH / `NOT_READY`, `I1-M1` |
| first review resolution | `6b13b63fc7f7d6fc0b9be2fa7d65a4d6198818b0ef1dee3f3257230fc74103ee` | 221 | MATCH |
| independent I1 rereview | `b772483a51bf06cbec3eb93ecbbdd2ce2b074181059ebcf40d794ff8eb00d571` | 388 | MATCH / `NOT_READY`, `I1-RR-M1/M2` |
| rereview resolution | `9f310be5e8143d7f2f0aeeff81b568e92dfcc9a1884373e53a0fd099522b9e6c` | 217 | MATCH |
| final I1 implementation evidence | `24328abbb0e918b0ff5009e32cb026b8624c26dd2bc66fcae49789df55f4b856` | 318 | MATCH |

The terminal R3 chain remained unchanged. It was not rerun, mutated or
reinterpreted by this rereview.

## 3. Exact reviewed implementation identity

| Path | Mandate operation | Exact reviewed identity | Result |
| --- | --- | --- | --- |
| `live_l1/core/paper_execution_control.py` | create | `7d3cb901c1c67c8df85e99bc579fda85d8732b634ff4747e08620b92ac1e44f7`, 257 lines | MATCH |
| `live_l1/core/execution.py` | modify | `5aed85ce2754dbb4d8984a1d699b607e3a522ed6da000df119ecd782a4e764d8`, 1,147 lines | MATCH |
| `tests/live_l1/test_paper_execution_control.py` | create/update | `0ae44f2d32f5f3b6affe37a258be0e6aee06790f857e4fc01628c6795bda99e5`, 843 lines | MATCH |
| I1 implementation evidence | create/update | `24328abbb0e918b0ff5009e32cb026b8624c26dd2bc66fcae49789df55f4b856`, 318 lines | MATCH |

The mandate-time `live_l1/core/execution.py` baseline was obtained directly
from `HEAD` in memory and independently hashed as
`a76f600d27feef969665bcd695ce11bc4e3abae0f25e045f7416fc78cd2513e3`,
951 lines.

The complete tracked worktree diff contains only
`live_l1/core/execution.py`, with 395 inserted and 199 deleted lines. The pure
module, I1 test module and governance records are untracked workstream files.
Foreign untracked artifacts were excluded and left untouched.

## 4. Independent rereview method

The rereview performed the following work without trusting claimed results:

1. read `AGENTS.md` completely and verified the canonical WSL-native root;
2. verified `HEAD`, `main`, observed `origin/main`, divergence and every
   supplied artifact identity without fetching;
3. read the I1 mandate, prior findings and resolutions, final evidence,
   complete pure module, complete 1,147-line consumer, complete 843-line test
   module and exact 951-line `HEAD` baseline;
4. reconstructed Revision 21 Section 11 directly, including pure authority,
   price-before-time-before-intent priority and OFF/SHADOW parity;
5. traced every action route, stable reason subtype, compatibility check,
   state mutation, audit, trade close, fee/PnL, duplicate and loss-cluster
   interaction in the final consumer;
6. independently injected all action/reason families over a complete set of
   valid, invalid and priority-sensitive precondition scenarios;
7. independently executed the exact `HEAD` baseline and final consumer over
   5,120 synthetic open-position cases and compared every observed surface;
8. directly probed same-side malformed snapshots, the TP/SL invalid-trade-
   snapshot exception, guard zero-call, duplicate suppression and ordered
   loss/audit interactions;
9. statically and dynamically checked the pure module over 24,576 inputs;
10. reran every mandated focused, complete Live-L1 and regression suite plus
    isolated compilation and `git diff --check`; and
11. rehashed every mandated preservation path and rechecked the exact scope.

All behavioral inputs were in-memory synthetic objects. Test filesystem use
was confined to test-created temporary directories. No real market, Research,
R3, Workstation, Exchange, Live or production-state input was used.

## 5. Consumer authority and complete compatibility predicate

The final consumer invokes `decide_paper_execution_control()` exactly once at
the decision seam. Its major dispatch is selected exclusively from
`control.action`. `control.reason` selects only a compatible subtype inside
that action route.

Immediately after the resolver call and before any execution mutation, the
consumer reconstructs the exact Legacy priority result from the explicit
input snapshot. The compatibility predicate covers:

| Priority or decision family | Independently verified required inputs |
| --- | --- |
| LONG TP then SL | LONG, positive entry price, exact inclusive boundary and TP-before-SL subtype |
| SHORT TP then SL | SHORT, positive entry price, exact inclusive boundary and TP-before-SL subtype |
| LONG/SHORT time stop | no price exit, complete valid trade snapshot and elapsed side-specific duration |
| opposing close | no price/time exit, matching open position and exact opposing final intent |
| OPEN LONG/SHORT | normalized FLAT, exact BUY/SELL intent and allowed entry permission |
| blocked entry | normalized FLAT, BUY/SELL intent and denied entry permission |
| same-side NOOP | no higher-priority exit, matching open position and exact same-side intent |
| HOLD/unknown NOOP | no higher-priority exit and exact intent classification |

An unknown action, unknown reason or any incompatible combination returns an
unexecuted `NOOP/UNKNOWN_INTENT` without position, reset, audit, trade, fee,
PnL, duplicate or loss-close-registration mutation.

The price-exit exception is preserved exactly: a valid TP/SL boundary closes
when position and positive entry price are available even if side, size or
entry timestamp make the complete trade-log snapshot invalid. Only the trade
log and consequent loss registration are omitted, matching exact `HEAD`.

## 6. Independent adversarial matrix

The independent matrix did not call the repository test helper. It injected a
fresh `PaperExecutionControlDecision` at the resolver seam for every pair in:

```text
ACTIONS:NOOP,OPEN_LONG,OPEN_SHORT,CLOSE_LONG,CLOSE_SHORT,INVALID_ACTION
REASONS:15_STABLE_REASONS_PLUS_INVALID_REASON
SCENARIOS:24
TOTAL_PAIRS_PER_SCENARIO:96
EXPECTED_COMPATIBLE_PAIRS_EXCLUDED_PER_SCENARIO:1
INCOMPATIBLE_TUPLES_TESTED:2280
```

The 24 scenarios independently covered:

- allowed and denied BUY/SELL entries from FLAT;
- FLAT HOLD and unknown intent with malformed stored fields;
- LONG/SHORT same-side intent with malformed side snapshots;
- LONG/SHORT opposing intent with invalid trade-log snapshots;
- all four TP/SL subtypes at exact inclusive boundaries;
- price exit over simultaneous time stop and opposing intent;
- both time stops over simultaneous opposing intent;
- LONG/SHORT HOLD and unknown intent below exit boundaries;
- LONG TP and SHORT SL with invalid complete trade snapshots;
- invalid time-stop snapshots falling through to same-side or opposing intent.

For every injected incompatible tuple the rereview captured the complete
position object before and after, resolver count, returned decision and calls
to audit, trade log, reset and loss registration.

```text
INDEPENDENT_ADVERSARIAL_SCENARIOS:24
INDEPENDENT_INCOMPATIBLE_TUPLES:2280
INDEPENDENT_INCOMPATIBLE_FAIL_CLOSED:2280
INDEPENDENT_ADVERSARIAL_FAILURES:0
RESOLVER_CALLS_PER_EVALUATION:1
I1_RR_M1_RESULT:PASS
```

## 7. Exact `HEAD` differential

The exact baseline was compiled in memory directly from
`HEAD:live_l1/core/execution.py`. The matrix was the Cartesian product:

| Axis | Values | Count |
| --- | --- | ---: |
| normalized position | `LONG`, `SHORT` | 2 |
| stored side | `long`, `short`, empty, invalid | 4 |
| stored entry price | missing, zero, 100, negative, invalid text | 5 |
| stored entry timestamp | empty, valid past, invalid, valid future | 4 |
| stored size | zero, positive | 2 |
| final intent | BUY, SELL, HOLD, unknown | 4 |
| price | 94, 100, 102, 106 | 4 |

The common evaluation timestamp was exactly one hour after the valid past
entry timestamp. The values exercise TP, SL, time-stop, opposing, same-side,
HOLD, unknown and invalid-snapshot branches.

For each case the comparison included:

- every `ExecutionDecision` field;
- every final `s2_position` field;
- ordered audit payloads;
- full trade JSONL payloads, including side, entry/exit, duration, size,
  gross/net PnL, gross/net PnL percentage and fee;
- loss-close registration value and call count;
- entry-gate call count; and
- final-consumer resolver call count.

```text
INDEPENDENT_HEAD_DIFFERENTIAL_CASES:5120
INDEPENDENT_HEAD_DIFFERENTIAL_MATCHES:5120
INDEPENDENT_HEAD_DIFFERENTIAL_MISMATCHES:0
RESOLVER_EXACTLY_ONCE_CASES:5120
I1_RR_M2_RESULT:PASS
```

This includes the previously failing LONG+BUY and SHORT+SELL malformed-side
cases. The returned `side_after` is now the exact Legacy canonical `long` or
`short`, while the stored position object remains unmodified.

## 8. Side-effect, ordering, duplicate and guard probes

Independent targeted probes produced:

```text
FLAT_ALLOWED_ENTRY_ORDER:loss_gate,resolver,audit
VALID_EXISTING_EXIT_ORDER:resolver,trade_jsonl,loss_register,audit
EXISTING_POSITION_EXIT_ENTRY_GATE_CALLS:0
DUPLICATE_CLOSE_DECISION:CLOSE_LONG/SELL_CLOSES_LONG/executed
DUPLICATE_TRADE_JSONL_CALLS:0
DUPLICATE_LOSS_REGISTER_CALLS:0
DUPLICATE_EXIT_AUDIT_CALLS:1
BLOCKED_PRE_EXECUTION_GUARD_RESOLVER_CALLS:0
BLOCKED_PRE_EXECUTION_GUARD_RESULT:NOOP/GUARD_GATE_CLOSED/guard_gate_closed/HARD
```

Thus the entry permission is resolved before the pure call only where Legacy
requires it, existing-position exits do not consult the entry gate, valid
trade/loss/audit ordering is unchanged, duplicates neither write a second
trade nor register a second loss, and the unchanged guard blocks before the
pure resolver.

## 9. Pure boundary

Static inspection found imports only from `__future__`, `dataclasses`,
`datetime` and `typing`. There are no `global` or `nonlocal` declarations and
no imports of runtime state, loop, adapter, exchange, logging, filesystem,
loss-cluster, economics, coordinator or gate authorities.

Dynamic evaluation used a 24,576-case Cartesian grid with mutable argument
dictionaries copied before every call. Every case was executed twice.

```text
PURE_RESULT_FROZEN:YES
PURE_RESULT_FIELDS:action,reason
PURE_ACTION_SET:NOOP,OPEN_LONG,OPEN_SHORT,CLOSE_LONG,CLOSE_SHORT
PURE_REASON_SET:EXACT_15_STABLE_REASONS
PURE_EXPLICIT_INPUT_PARAMETERS:13
PURE_RUNTIME_STATE_OBJECT_INPUT:NO
PURE_FORBIDDEN_IMPORTS:0
PURE_GLOBAL_OR_NONLOCAL_DECLARATIONS:0
PURE_GRID_CASES:24576
PURE_NONDETERMINISTIC_OR_INVALID_RESULTS:0
PURE_INPUT_MUTATIONS:0
PURE_OPEN_CALLS:0
PURE_NEGATIVE_CAPABILITY:PASS
```

No quantity, fill, fee, PnL, settlement, persistence, logging, adapter,
exchange or loss-cluster authority moved into the pure module. Autonomous
TP/SL/time-stop exits use explicit close actions and do not synthesize an
opposing BUY or SELL intent.

## 10. Independent test execution

Every Python command used the repository `.venv`, synthetic or temporary
inputs and no real runtime source. The mandatory suites used
`PYTHONDONTWRITEBYTECODE=1`.

| Command | Tests | Result |
| --- | ---: | --- |
| `.venv/bin/python -m unittest tests.live_l1.test_paper_execution_control` | 25 | PASS |
| `.venv/bin/python -m unittest tests.live_l1.test_loss_cluster_state` | 18 | PASS |
| `.venv/bin/python -m unittest tests.live_l1.test_pre_execution_guards` | 6 | PASS |
| `.venv/bin/python -m unittest tests.live_l1.test_paper_economics_shadow_runtime` | 9 | PASS |
| `.venv/bin/python -m unittest discover -s tests/live_l1 -p 'test_*.py'` | 357 | PASS |
| `.venv/bin/python -m unittest discover -s tests/regression -p 'test_*.py'` | 170 | PASS |
| isolated `.venv/bin/python -m py_compile` on all three I1 source/test paths | n/a | PASS / return code 0 |
| `git diff --check` | n/a | PASS / return code 0 |

There were no failures, errors or skips and no repository-local bytecode
write. Passing repository tests were treated only as supporting evidence; the
independent adversarial and differential results above control the finding
closure.

## 11. Preservation and scope

| Read-only preservation path | Required and observed SHA-256 | Lines | Result |
| --- | --- | ---: | --- |
| `live_l1/core/loop.py` | `54e9e7bc0977a9c94f2e85a3279157678249a8569cff63f7d4f29131443fd058` | 1,411 | PASS |
| `tests/live_l1/test_loss_cluster_state.py` | `0a7823175eb55d39d22d0576e1d58296d4b5123028e0fbfff561c1a6b642fe35` | 413 | PASS |
| `tests/live_l1/test_pre_execution_guards.py` | `38192c5f96814bb0b3899e08453d3764cc1a14f9a7af52de218d4a2e0280248c` | 253 | PASS |
| `live_l1/core/paper_economics_shadow_runtime.py` | `8dbdf1ec0190e96bdb75697d1ffb25bd87784194150f674bb7e3317df6073a45` | 183 | PASS |
| `live_l1/core/paper_iu4_adapter.py` | `d65525f31746d1edf30bf1ffc7f84a845f97b3f4120904c9910b741bc8c76a7b` | 641 | PASS |
| `live_l1/core/paper_iu4_startup_gate.py` | `86b191afb7725d613898d6911b543a84e9e0ada1f9c59822e3c47107272a6753` | 600 | PASS |
| `live_l1/state/paper_atomic_coordinator.py` | `6460dbfc58acaf6ca0ac56120a1e7460e79981ead30959909f881deef563c1f5` | 1,799 | PASS |

The Revision 21 specification, independent rereview, terminal handoff, final
R3 attestation, I1 mandate, prior I1 reviews/resolutions, final evidence and
all three final I1 code/test identities retained their controlling hashes
through the substantive review.

No tracked path other than `live_l1/core/execution.py` differs from `HEAD`.
This rereview created only this uniquely named record after all substantive
read-only checks. It made no source, test, configuration, runtime, R3,
Workstation, scheduler, process, Research, Exchange, Live, production-state,
staging, commit, fetch, push, cleanup or deletion mutation. Foreign untracked
artifacts were left untouched. The expressly excluded build script was not
read, executed, modified, staged or committed.

## 12. Findings

### BLOCKER

None.

### HIGH

None.

### MEDIUM

None.

### LOW

None.

The prior findings are independently closed:

- `I1-M1`: PASS — the major execution route is controlled by action;
- `I1-RR-M1`: PASS — the complete reason-specific compatibility boundary
  rejects all independently tested impossible tuples before execution side
  effects; and
- `I1-RR-M2`: PASS — all 5,120 exact-baseline cases, including malformed
  same-side snapshots, are byte-for-value behaviorally equal.

## 13. Acceptance boundary and exact next step

This `READY` verdict accepts only I1 Characterization / Pure Control
Extraction. It does not authorize an I2 implementation, Adapter V2 code,
Atomic V2 code, an ENFORCED consumer, active wiring, activation, Exchange or
Live operation. The terminal R3 result remains separate and unchanged.

The exact next governance workstream is the creation and review of the
separate file-exact mandate:

```text
IU4-I2-ADAPTER-REQUEST-V2-FILE-EXACT-MANDATE
```

No I2 implementation may begin until that separate mandate exists and passes
its own identity, scope and governance gates.

## 14. Final verdict

```text
I1_MAJOR_ACTION_AUTHORITY:PASS
I1_COMPLETE_COMPATIBILITY_PREDICATE:PASS
I1_INDEPENDENT_ADVERSARIAL_MATRIX:2280/2280_PASS
I1_EXACT_HEAD_DIFFERENTIAL:5120/5120_PASS
I1_SAME_SIDE_MALFORMED_SNAPSHOT_PARITY:PASS
I1_TP_SL_INVALID_TRADE_SNAPSHOT_EXCEPTION:PASS
I1_PURE_NEGATIVE_CAPABILITY:PASS
I1_RESOLVER_EXACTLY_ONCE:PASS
I1_GUARD_ZERO_CALL:PASS
I1_LOSS_CLUSTER_ORDERING:PASS
I1_DUPLICATE_FEE_PNL_AUDIT_PARITY:PASS
I1_TEST_SUITES:PASS
I1_COMPILATION:PASS
I1_PRESERVATION:PASS
I1_FILE_EXACT_SCOPE:PASS
I1_INDEPENDENT_ACCEPTANCE:READY
BLOCKER:0
HIGH:0
MEDIUM:0
LOW:0
I2_IMPLEMENTATION_AUTHORIZED:NO
NEXT_STEP:IU4-I2-ADAPTER-REQUEST-V2-FILE-EXACT-MANDATE
```
