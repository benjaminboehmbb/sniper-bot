# Pre-IU4 I4 Adapter Request V2 — File-Exact Mandate — 2026-08-20

## 1. Mandate decision

This record grants the separate file-exact mandate required after independent
I3 acceptance for Revision-21 implementation package I4 only.

```text
MANDATE_ID:IU4-I4-ADAPTER-REQUEST-V2-FILE-EXACT-MANDATE
MANDATE_REVISION:2
PRIOR_MANDATE_SHA256:12d5569f17f2d3eb024aafc9ace49d1c5d594b5a28a2fc991e0fac54b3297d5c
PRIOR_INDEPENDENT_REREVIEW:NOT_READY_2_BLOCKER_2_HIGH
MANDATE_RESULT:AUTHORIZED
IMPLEMENTATION_PACKAGE:I4_ONLY
I3_INDEPENDENT_ACCEPTANCE:READY
I3_REREVIEW6_FINDINGS:0/0/0/0
I4_IMPLEMENTATION_AUTHORIZED:YES_WITHIN_EXACT_FILE_SCOPE
I5_THROUGH_I8_AUTHORIZED:NO
ACTIVE_LOOP_CONSUMER_AUTHORIZED:NO
ACTIVE_EXECUTION_SEAM_AUTHORIZED:NO
ATOMIC_V2_COMMIT_FROM_ADAPTER_AUTHORIZED:NO
V1_FALLBACK_FOR_V2_AUTHORIZED:NO
ENFORCED_LOOP_AUTHORIZED:NO
ENFORCED_ACTIVATION_AUTHORIZED:NO
EXCHANGE_AUTHORIZED:NO
LIVE_AUTHORIZED:NO
```

Mandate creation does not implement I4. It authorizes only a later, separately
invoked I4 implementation workstream and only while every identity, file
boundary, preservation condition and fail-closed rule below remains exact.
Independent read-only file-exact review of this mandate is required before
that implementation begins.

## 2. Controlling identity and prerequisite closure

```text
CANONICAL_REPOSITORY:/home/benja/projects/sniper-bot
BRANCH:main
HEAD:c7ce0452aa2ccbf08c462784d68fa07b3dfe9595
MAIN:c7ce0452aa2ccbf08c462784d68fa07b3dfe9595
ORIGIN_MAIN:89e13fecd1ab549ca7099818b1c9ad4984cb6f7a
MAIN_BEHIND_ORIGIN:0
MAIN_AHEAD_OF_ORIGIN:6
```

| Controlling artifact | SHA-256 | Lines / entries | Result |
|---|---|---:|---|
| Revision-21 specification | `ab8f80720a1d8fe49b9085bce63658bcaecf7f0a3ea70fb555559223090824e0` | 4,605 | complete and controlling |
| Revision-21 independent rereview | `6618955e67bf9e11798c103eb7d01823dc2ece4c39a66575dbb668c4162c0c7c` | 752 | `READY`, findings 0/0/0/0 |
| Revision-21 final R3 attestation | `587c5a5ffed271534d661c6c816781eb8443d5c6318fe14d26b1947d21340851` | 179 | final R3 `PASS` |
| I1 independent rereview 2 | `adc13abbec3a0458d712df729c2732bce8897be7ecf991a312839616e9687804` | 391 | `READY`, findings 0/0/0/0 |
| final independent I2 rereview | `5a59ad8c97ebae85148661fe0e3bedab643c7f12ae2c8d4e87272447c0616679` | 300 | `READY`, 97/97 PASS |
| I3 file-exact mandate | `775aeb62e6ff0a1ca3af970970053b43d176f1122560774f184ecf40a8fcced5` | 558 | authorized |
| final I3 implementation Evidence | `20846284ffad9e8b755dd6a3b74f963d8d2c6ee1519fafdd0bc1275f2e33c390` | 463 | implementation-side `PASS` |
| I3 Evidence-precision resolution | `00fb12135197a5fa8aefa8bf149c03904b9440d7909eb5a218cde5cfa38f7b5d` | 156 | complete |
| final independent I3 rereview 6 | `03790420534e38c7e36d1824a472dfd80763340dacec8847ddf5072d55db0c9f` | 191 | `I3_INDEPENDENT_ACCEPTANCE:READY`, findings 0/0/0/0 |
| I4 mandate independent rereview | `5c67fb30008005e4e0b02e179c300d7ab1603ee36c1ef625e136e9e8140b8263` | 295 | `NOT_READY`, findings 2/2/0/0; all findings closed normatively by this revision |
| I2 Preservation package | `3af14ff2e270d7d3ca09c1279da7d64e6d720630d06a0c5f45b6786237782037` | 1,318 entries | immutable historical freeze |
| I2 Freeze manifest | `ad154c0eda13470920878873ed170368cc8f4c43591400a07592a77b179d9e16` | 60 | immutable historical freeze |

Revision 21 Sections 11.4, 12, 19.2 and 20 are decisive. I4 is the additive
Adapter Request V2 package: explicit Control Actions and autonomous exits are
validated against synthetic Atomic-V2 State. I5, not I4, owns the active
mode-dependent Execution Seam and every active commit delegation.

## 3. I4 objective and ceiling

I4 implements only a dormant, additive and independently testable request and
validation boundary:

1. strict, content-addressed `IU4AdapterRequestV2` serialization;
2. canonical Decimal price carriers without Float roundtrip;
3. explicit `control_action` and `control_reason_code` independent of final
   intent, so autonomous TP/SL/Time-stop exits need no fabricated opposing
   intent;
4. a frozen, in-memory `IU4AdapterTrustedControlContextV1` that carries the
   trusted Event/Intent/price identity and the already authoritative I1
   `PaperExecutionControlDecision` without duplicating Pure Control;
5. pure validation of State, profile, Authorization, Event and Control-Decision
   identities against an in-memory `AtomicPaperStateV2`, that trusted context
   and a trusted Authorization ID;
6. an exact position/intent/action/reason/trade/stop/Loss-capability matrix;
7. exact stable V2 failure-code classification; and
8. fail-closed V1/V2 type separation with unchanged V1 imports and behavior.

I4 ends before any Coordinator commit, Entry authorization, Settlement,
Journal write, Snapshot publication, audit projection, mode switch, loop
import or runtime activation. The validator may read only its explicit
request, synthetic State, trusted Authorization ID and trusted in-memory
Control context. It does not own Snapshot acceptance, `PROGRESS`,
`ENTRY_VETO`, OPEN/CLOSE construction or recovery; those active execution
decisions remain I5 and later packages. I5 must later prove that the trusted
context and its `PaperExecutionControlDecision` came from the same accepted
input, but I4 must already reject every request field that differs from that
context.

I4 is not permission to redesign Pure Control, Economics, Throttle, Atomic V2,
Lifecycle Ledger, Runtime Gate, Authorization V2, Shadow harnesses or Legacy
V1 behavior. A demonstrated need to change one of those contracts stops I4 as
`BLOCKED`; it is not silently repaired inside the adapter request package.

## 4. Exact authorized file set

### 4.1 Existing production file permitted additive modification

| Path | Mandate-time SHA-256 | Lines | Authorized change |
|---|---|---:|---|
| `live_l1/core/paper_iu4_adapter.py` | `d65525f31746d1edf30bf1ffc7f84a845f97b3f4120904c9910b741bc8c76a7b` | 641 | add only `IU4AdapterRequestV2`, frozen `IU4AdapterTrustedControlContextV1`, strict V2 record/fingerprint helpers, the exact Section-10 failure codes and a pure in-memory V2 binding/action validator importing but never modifying or recomputing `PaperExecutionControlDecision`; preserve every V1 type, execution path and export |

### 4.2 New focused test and implementation Evidence

Both paths are absent at mandate time.

| Path | Authorized purpose |
|---|---|
| `tests/live_l1/test_paper_iu4_adapter_v2.py` | one complete focused module for V2 schema, canonicality, identity, action/reason, autonomous-exit, terminal-capability, purity and V1-separation contracts |
| `docs/review/PRE_IU4_I4_ADAPTER_REQUEST_V2_IMPLEMENTATION_EVIDENCE_2026-08-20.md` | exact identities, matrices, commands, counts, preservation proof, scope and I4 result |

No other source, test, fixture, State sample, profile, Authorization, manifest,
configuration, schema sidecar, documentation or Evidence path is authorized.
If any additional path becomes necessary, I4 stops before creating or
modifying it and requests a revised file-exact mandate.

The mandate record itself is the governance artifact of this turn and is not
one of the later three implementation/Evidence paths.

## 5. Explicit read-only preservation boundary

### 5.1 Frozen I2 and accepted I3 identities

| Path | Required SHA-256 | Required mode / lines |
|---|---|---:|
| `archive/IU4_I2_FREEZE_20260820/IU4_I2_PRESERVATION_20260820.tar.gz` | `3af14ff2e270d7d3ca09c1279da7d64e6d720630d06a0c5f45b6786237782037` | `0444`, 1,318 entries |
| `archive/IU4_I2_FREEZE_20260820/FREEZE_MANIFEST.txt` | `ad154c0eda13470920878873ed170368cc8f4c43591400a07592a77b179d9e16` | `0444`, 60 lines |
| `live_l1/state/paper_atomic_coordinator.py` | `d0721ae5def3551ba7281ea0e367f5347890fd4cd7187d8f2aebb98d2651e84f` | 5,489 lines |
| `live_l1/state/paper_artifacts.py` | `3cd9a459e2856672bb7b318c9cdbf8f8bb52e633ee9529d74761d64928213946` | 1,575 lines |
| `live_l1/state/loss_cluster.py` | `4ce7d59f64a67de94ffc6f1d03ff4e6c8a7a590802abb003b311cd0d56cc3e55` | 521 lines |
| `tests/live_l1/test_paper_atomic_coordinator_v2.py` | `16d0fea6e5588cc14329ba61cfeeccb1f72478d14c358f8ed4e38c1ac3a41bb9` | 2,482 lines |
| final I3 Evidence | `20846284ffad9e8b755dd6a3b74f963d8d2c6ee1519fafdd0bc1275f2e33c390` | 463 lines |
| final I3 rereview 6 | `03790420534e38c7e36d1824a472dfd80763340dacec8847ddf5072d55db0c9f` | 191 lines |

The freeze directory remains mode `0555`. No archived I2/I3 copy, accepted
Evidence or prior governance record is rewritten or regenerated.

### 5.2 Adapter V1, Shadow and adjacent canonical inputs

| Path | Required mandate-time SHA-256 | Lines |
|---|---|---:|
| `tests/live_l1/test_paper_iu4_adapter.py` | `b4947e4c03fa3b187e01c4005062337d1837b70d652243030581172dd4d2c339` | 441 |
| `live_l1/core/paper_iu4_shadow_observation_gate.py` | `ed4e75fad664c68b91950e9c09e873823ebe3eb0b0062f85806daa09ce661350` | 886 |
| `live_l1/core/paper_iu4_shadow_harness.py` | `ddfb60f19a3b765a476c8de0464d583590313cdd0583391044cb338fec969f77` | 1,007 |
| `live_l1/tools/paper_iu4_replay_evidence.py` | `707592bdb5c6fe12ff01c8254da1f16ee5c25a049c61caef60077064ff77c000` | 849 |
| `tests/live_l1/test_paper_iu4_shadow_harness.py` | `abea98dcecf65ff741fbe9951c5986d415085051b3dd27d6750553b475f6f3a5` | 747 |
| `tests/live_l1/test_paper_iu4_replay_evidence.py` | `d5a8580f44edac6997281bcc5aa3d3ea79bd1c7e5f07f24602b029cd2cf363e2` | 488 |
| `tests/live_l1/test_paper_iu4_replay_pipeline.py` | `7f89b7ff37ad603edcfe4cf9dd5d9f12ad8270b0725708b5619854f97e4a93f9` | 316 |
| `live_l1/core/paper_execution_control.py` | `7d3cb901c1c67c8df85e99bc579fda85d8732b634ff4747e08620b92ac1e44f7` | 257 |
| `tests/live_l1/test_paper_execution_control.py` | `0ae44f2d32f5f3b6affe37a258be0e6aee06790f857e4fc01628c6795bda99e5` | 843 |
| `live_l1/core/paper_iu4_startup_gate.py` | `c4a1854f3b200525568a40205b39e9ce2e14c342bb860569ba7fcfe5e9c063cd` | 919 |
| `live_l1/core/paper_iu4_runtime_gate.py` | `447573e484bc13023a118ae61bf7615657293be629c30729748e64f0af7af7c5` | 201 |
| `live_l1/core/loop.py` | `54e9e7bc0977a9c94f2e85a3279157678249a8569cff63f7d4f29131443fd058` | 1,411 |
| `live_l1/core/execution.py` | `5aed85ce2754dbb4d8984a1d699b607e3a522ed6da000df119ecd782a4e764d8` | 1,147 |
| `live_l1/core/paper_economics.py` | `a302013134d1265ac85ad10b57a67ead9e2343043f7eb499fd965a44312525ae` | 730 |
| `live_l1/core/paper_entry_throttle.py` | `ad5447d88a2c35c9a71a5495c61c8f08fa844daf60e79d4a872234e88037df75` | 727 |

The adapter source is the only intentionally released existing file. Its V1
definitions and behavior remain preservation contracts even though additive
V2 bytes are authorized in the same module. Shadow consumers must continue to
import and execute V1 only.

## 6. Required implementation order

The later I4 workstream must:

1. reverify every controlling, authorized, absent and preservation identity;
2. rerun the mandate-time 120-test focused/adjacent baseline;
3. create the single V2 focused test module before production changes;
4. add the strict V2 value contract and canonical parser;
5. add the strict frozen trusted Control context and pure
   State/Profile/Authorization/Event/Decision binding validator;
6. complete the full action/reason/position/intent/Loss-capability matrix,
   including autonomous exits without synthetic intent;
7. implement and test the exact stable failure mapping in Section 10;
8. prove the V2 path performs no commit, economics, filesystem, clock,
   environment, network, logging or process access;
9. rerun every required test, compile, scope and preservation command;
10. reverify exactly three changed/created later-workstream paths; and
11. create implementation Evidence only after every check passes.

No later step may reinterpret a failed earlier check as an expected skip.

## 7. Exact `IU4AdapterRequestV2` record contract

The persisted record has exactly these 25 fields and no defaults:

```text
schema_version
request_id
source_intent_id
intent_final
intent_reason_code
control_action
control_reason_code
expected_atomic_state_fingerprint
expected_transaction_sequence
target_system_state_id
timestamp_utc
tick_id
snapshot_id
reference_price_text
reference_stop_price_text
trade_id
economics_profile_id
economics_model_version
economics_config_fingerprint
throttle_policy_profile_id
throttle_policy_model_version
throttle_policy_fingerprint
runtime_control_profile_id
runtime_control_fingerprint
authorization_id
```

Normative serialization rules:

- `schema_version` is integer `2`; bool is rejected;
- missing or unknown fields, disguised primitive subclasses and implicit
  defaults are rejected;
- all identifiers/reasons are nonempty stripped strings except the explicitly
  nullable/empty trade/stop cases below;
- Intent is exactly `BUY`, `SELL` or `HOLD`; Control Action is exactly `NOOP`,
  `OPEN_LONG`, `OPEN_SHORT`, `CLOSE_LONG` or `CLOSE_SHORT`;
- expected State and all profile fingerprints are lowercase 64-character
  SHA-256 values;
- Sequence and Tick are nonnegative integers and reject bool;
- Timestamp is canonical UTC whole seconds; Snapshot and source Intent IDs are
  nonempty;
- `reference_price_text` is an exact canonical finite positive Decimal string.
  Float, exponent, whitespace, sign aliases, trailing-zero aliases, nonfinite
  values and numerically equal noncanonical strings are rejected;
- `reference_price` is a derived Decimal property created only from accepted
  `reference_price_text`; it is not a second serialized authority;
- `reference_stop_price_text` is either `null` or an exact canonical finite
  positive Decimal string; its Decimal property is also derived only after
  canonical validation;
- sorted compact ASCII JSON of every field except `request_id` produces
  `request_id=PEE-IU4-V2-<sha256(payload)>`;
- a supplied ID must equal that value; same ID with divergent payload is
  rejected as conflict/tamper; and
- exact roundtrip and canonical input equality are mandatory.

No input may pass through binary Float or a lossy string/Decimal roundtrip.

## 8. Trusted Control context and pure V2 binding-validator contract

### 8.1 Exact trusted in-memory context

The additive frozen `IU4AdapterTrustedControlContextV1` is not persisted and
has no record, sidecar, cache or independent fingerprint. It has exactly these
eight required fields and no defaults:

```text
source_intent_id
intent_final
intent_reason_code
timestamp_utc
tick_id
snapshot_id
reference_price_text
control_decision
```

The first seven fields obey the same strict primitive, Intent, timestamp,
integer and canonical Decimal-text rules as the corresponding V2 Request
fields. `reference_price` is derived directly from the accepted text without
Float. `control_decision` must be an actual immutable
`PaperExecutionControlDecision` imported from the accepted I1 Pure-Control
module; subclasses, dictionaries and lookalikes are rejected. The Adapter
does not invoke or reproduce `decide_paper_execution_control()`.

The context is the I4 trust-boundary input used by synthetic tests. I5 must
later construct it from one and the same accepted Event/Intent/price input and
the Pure-Control output for that input. I4 authorizes no active construction
or consumer.

### 8.2 Exact validator inputs and comparison order

The additive public validator accepts exactly one `IU4AdapterRequestV2`, one
complete in-memory `AtomicPaperStateV2`, one already trusted nonempty
Activation Authorization ID supplied by the I2 gate boundary, and one
`IU4AdapterTrustedControlContextV1`. It returns the same validated immutable
request or the exact fail-closed error from Section 10.

It must compare before action validation:

- request Source Intent ID, final Intent, Intent Reason, Timestamp, Tick,
  Snapshot and canonical reference-price text exactly against the trusted
  Control context;
- request Control Action and Control Reason exactly against
  `trusted_context.control_decision.action` and `.reason`;
- expected Atomic State fingerprint and Transaction Sequence;
- Economics Profile ID, Model Version and Config fingerprint against Atomic
  Account/Position identities;
- Throttle Profile ID, Model Version and fingerprint against Atomic Throttle;
- Runtime-Control Profile ID and fingerprint against Atomic State/S4;
- request Authorization ID against the trusted Authorization ID.

All trusted comparisons are exact string/integer equality after strict
construction; no normalization at comparison time, implicit refresh or
fallback is permitted. A correctly refingerprinted Request with one divergent
Event, price, Intent, Action or Reason is still rejected.

The validator accepts neither V1 request/state objects nor a V1 fallback. It
does not parse, validate expiry of, consume or replace
`IU4ActivationAuthorizationV2`; I2 remains the sole Authorization authority.
Any mismatch is `REJECTED_PRE_ACCEPT`: no record, Cursor or mutation. The
validator does not decide whether an Authorization is trusted and does not
decide or recompute Control.

## 9. Exact action, reason and State matrix

### 9.1 OPEN

| State | Intent | Action | Required reason | Additional binding |
|---|---|---|---|---|
| FLAT | BUY | OPEN_LONG | `BUY_FROM_FLAT` | nonempty new Trade ID; non-null Stop |
| FLAT | SELL | OPEN_SHORT | `SELL_FROM_FLAT` | nonempty new Trade ID; non-null Stop |

OPEN is rejected for OPEN State, HOLD, side/reason mismatch, S4
`entry_allowed=false`, SOFT, HARD or EMERGENCY. Target System State ID is
nonempty. I4 calculates no Quantity, Stop, Quote or guard result.

### 9.2 CLOSE

| State | Action | Opposing-intent reason | Autonomous reasons |
|---|---|---|---|
| LONG | CLOSE_LONG | `SELL_CLOSES_LONG` requires SELL | `TP_LONG_HIT`, `SL_LONG_HIT`, `LONG_TIME_STOP_HIT` |
| SHORT | CLOSE_SHORT | `BUY_CLOSES_SHORT` requires BUY | `TP_SHORT_HIT`, `SL_SHORT_HIT`, `SHORT_TIME_STOP_HIT` |

Autonomous reasons accept the actual canonical final Intent, including HOLD;
the validator never requires or manufactures an opposing Intent. CLOSE
requires the current Trade ID and null Stop. SOFT permits CLOSE because exit
evaluation remains allowed. HARD/EMERGENCY reject every Tick request because
exit evaluation is false. Entry blockers never become a CLOSE veto.

Every accepted Action/Reason, including opposing-intent and autonomous
reasons, must already equal the trusted `PaperExecutionControlDecision`.
Position/Intent/Action/Reason validation remains an independent second check;
the trusted Decision cannot authorize an impossible State transition. The
Adapter does not recalculate TP, SL or Time-stop and does not reinterpret
their priority.

### 9.3 NOOP

Allowed pairs are exactly:

- HOLD plus `HOLD_NO_EXECUTION`;
- LONG+BUY plus `BUY_ALREADY_LONG`;
- SHORT+SELL plus `SELL_ALREADY_SHORT`; and
- FLAT+BUY/SELL plus `LOSS_CLUSTER_GATE_BLOCKED_ENTRY`.

NOOP requires target System State ID equal to the current Position System State
ID, null Stop and Trade ID empty for FLAT or equal to current Trade ID for OPEN
State. Any other combination fails closed. `UNKNOWN_INTENT` is invalid because
V2 rejects unknown Intent before action validation.

`LOSS_CLUSTER_GATE_BLOCKED_ENTRY` additionally requires all of the following:

- FLAT State with BUY or SELL and the same trusted Control Decision;
- `state.risk.entry_allowed is False`;
- `state.loss_cluster.pause_entries_remaining > 0`; and
- exact `LOSS_CLUSTER_PAUSE` membership in the bound S4 `reason_codes`.

A clean entry-allowed State and a State blocked only by Account, Throttle,
SOFT or any non-Loss reason reject this Loss-specific NOOP. SOFT does not
fabricate this reason and may validate only the Action/Reason actually supplied
by trusted Pure Control within S4 capability. HARD and EMERGENCY reject every
Tick Request regardless of Action or Decision.

The validator commits neither `PROGRESS` nor `ENTRY_VETO`. I5 must later prove
Snapshot acceptance and map a validated request to I3 without changing this
request contract.

## 10. Stable failure codes, Event replay and zero-mutation ceiling

### 10.1 Exact V2 failure-code matrix

The additive V2 reason-code namespace and validator use exactly this mapping.
Existing V1 reason constants and behavior remain unchanged.

| Failure class | Exact reason code |
|---|---|
| malformed/missing/unknown/noncanonical V2 Request field, wrong primitive, V1 Request passed to V2 validator or malformed trusted context | `PEE_IU4_ADAPTER_REQUEST_INVALID` |
| supplied Request ID differs from canonical payload | `PEE_IU4_ADAPTER_REQUEST_CONFLICT` |
| same Request ID presented with divergent payload | `PEE_IU4_ADAPTER_REQUEST_CONFLICT` |
| Atomic V1, unknown Atomic schema or non-`AtomicPaperStateV2` input | `PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED` |
| Atomic State fingerprint, Transaction Sequence, System-State binding, Event/Intent/price context or trusted Authorization-ID mismatch | `PEE_IU4_RUNTIME_BINDING_MISMATCH` |
| Economics or Throttle Profile ID, Model Version or fingerprint mismatch | `PEE_IU4_RUNTIME_BINDING_MISMATCH` |
| Runtime-Control Profile ID or fingerprint mismatch | `PEE_IU4_CONTROL_PROFILE_MISMATCH` |
| Request Action/Reason differs from trusted Pure-Control Decision | `PEE_IU4_CONTROL_ACTION_INVALID` |
| Position/Intent/Action/Reason, Stop, Trade, target-State or Loss-specific NOOP predicate mismatch | `PEE_IU4_CONTROL_ACTION_INVALID` |
| otherwise structurally valid OPEN blocked by `entry_allowed=false`, including SOFT | `PEE_IU4_ENTRY_BLOCKED` |
| HARD or EMERGENCY denies Tick evaluation | `PEE_IU4_TICK_PRE_ACCEPT_REJECTED` |

`PEE_IU4_ADAPTER_REQUEST_INVALID` and
`PEE_IU4_ADAPTER_REQUEST_CONFLICT` are precise additive Adapter-V2 codes;
the other values are the controlling Revision-21 stable families. Failure
precedence is exactly:

1. Request and trusted-context constructor/schema/canonicality checks,
   including canonical Request-ID conflict;
2. validator boundary types: Request, Atomic State, trusted context and trusted
   Authorization ID;
3. the Section-8.2 comparison bullets in their written order;
4. HARD/EMERGENCY terminal capability rejection;
5. the Section-9 State/Intent/Action/Reason/Stop/Trade/target/Loss predicates
   in subsection and table order; and
6. the otherwise structurally valid OPEN entry-capability check.

The first failure in that order is returned deterministically. No generic V1
error or arbitrary replacement code is permitted.

### 10.2 Trusted Event, replay and mutation ceiling

- Request ID content-addresses all Event, State, profile, Authorization, price,
  action and trade bindings.
- Every Event, Intent and price field must also equal the trusted Control
  context; content addressing alone is never treated as provenance.
- Action and Reason must equal the trusted Pure-Control Decision and must also
  pass the independent State matrix.
- Equal records reconstruct the same ID; divergent payload under a supplied
  existing ID is rejected before State evaluation.
- Expected Sequence is the pre-action sequence; no implicit State refresh is
  allowed.
- Snapshot, Tick, Timestamp and source Intent form one immutable Event binding.
- Validation is deterministic and creates no cache, journal or sidecar.
- No V2 request reaches `PaperIU4Adapter.execute()` and no V1 request reaches
  the V2 validator.

I4 has zero authorized State mutation. Tests use synthetic in-memory Atomic V2
objects and test-owned `/tmp` fixtures only. No real State, Journal,
Authorization or Runtime Session is used.

## 11. V1, Shadow and inactive-boundary preservation

Every V1 symbol, dataclass field, Request ID, record byte, error, result and
`PaperIU4Adapter.execute()` behavior remains unchanged. Existing Shadow and
replay consumers continue to import V1 only and must not select V2 implicitly.

Loop, Execution, Gates and launchers must not import or instantiate V2. A final
search may find V2 consumers only in the adapter module and its one focused
test. I4 creates no active ENFORCED path.

## 12. Required focused-test matrix

The single new module must cover at least:

1. exact 25 fields, schema 2 and no defaults;
2. missing/unknown, bool-as-int, wrong primitive and V1 rejection;
3. UTC, SHA, Sequence and Tick boundaries;
4. canonical Decimal text and Float/nonfinite/exponent/whitespace/sign/
   trailing-zero rejection with exact derived Decimal equality;
5. roundtrip, fingerprint and supplied-ID tamper;
6. every State/Sequence/Economics/Throttle/Runtime/Authorization mismatch;
7. full FLAT/LONG/SHORT × BUY/SELL/HOLD × five-action matrix;
8. every allowed/disallowed Control reason pair;
9. autonomous LONG/SHORT TP, SL and Time-stop with actual HOLD;
10. OPEN and CLOSE Stop/Trade/side bindings;
11. SOFT CLOSE, blocked OPEN, HARD/EMERGENCY rejection;
12. all NOOP bindings and deterministic replay;
13. same-ID divergent payload conflict;
14. exact trusted-context mismatch rejection for Source ID, final Intent,
    Intent Reason, Timestamp, Tick, Snapshot and reference price, each with a
    freshly correct Request ID;
15. exact trusted-Decision mismatch rejection for every Action and Reason,
    fake TP/SL/Time-stop, wrong trigger priority and genuine autonomous HOLD;
16. Loss-specific NOOP requires entry blocked, active pause and
    `LOSS_CLUSTER_PAUSE`; clean and non-Loss-only blockers reject;
17. every stable failure-code mapping and deterministic first-failure order;
18. proof of no Coordinator, economics, settlement, filesystem, environment,
    clock, log, network or process access;
19. V1 import/record/execute compatibility and V1/V2 separation;
20. absence of active V2 consumers; and
21. no supplied-State or trusted-context mutation on success or failure.

No skip, expected failure, reduced matrix or fixture/sidecar file is accepted.

## 13. Mandatory commands and mandate-time baseline

Every Python command uses `PYTHONDONTWRITEBYTECODE=1`, isolated cache and
test-owned temporary roots.

```text
.venv/bin/python -m unittest tests.live_l1.test_paper_iu4_adapter_v2
.venv/bin/python -m unittest tests.live_l1.test_paper_iu4_adapter
.venv/bin/python -m unittest tests.live_l1.test_paper_execution_control
.venv/bin/python -m unittest tests.live_l1.test_paper_atomic_coordinator_v2
.venv/bin/python -m unittest tests.live_l1.test_paper_atomic_coordinator
.venv/bin/python -m unittest tests.live_l1.test_paper_iu4_startup_gate
.venv/bin/python -m unittest tests.live_l1.test_paper_iu4_runtime_gate
.venv/bin/python -m unittest tests.live_l1.test_paper_iu4_shadow_harness
.venv/bin/python -m unittest tests.live_l1.test_paper_iu4_replay_evidence
.venv/bin/python -m unittest tests.live_l1.test_paper_iu4_replay_pipeline
.venv/bin/python -m unittest discover -s tests/live_l1 -p 'test_*.py'
.venv/bin/python -m unittest discover -s tests/regression -p 'test_*.py'
.venv/bin/python -m py_compile live_l1/core/paper_iu4_adapter.py tests/live_l1/test_paper_iu4_adapter_v2.py
git diff --check
```

Fresh mandate-time baseline under `/tmp/iu4-i4-mandate-baseline`:

| Target | Result | RC | failures/errors/skips |
|---|---:|---:|---:|
| Adapter V1 | 13/13 PASS | 0 | 0/0/0 |
| Pure Control | 25/25 PASS | 0 | 0/0/0 |
| Atomic V2 | 44/44 PASS | 0 | 0/0/0 |
| Atomic V1 | 23/23 PASS | 0 | 0/0/0 |
| Startup Gate | 12/12 PASS | 0 | 0/0/0 |
| Runtime Gate | 3/3 PASS | 0 | 0/0/0 |
| combined adjacent baseline | 120/120 PASS | 0 | 0/0/0 |
| complete `tests/live_l1` | 419/419 PASS | 0 | 0/0/0 |
| complete `tests/regression` | 170/170 PASS | 0 | 0/0/0 |

Implementation Evidence records exact new counts, RCs, skips, roots, compile
outputs and stable mutation-scope output. Adjacent tests do not replace the
new focused module.

## 14. Implementation Evidence completion gate

The authorized Evidence must contain:

- every Section-2 identity and prerequisite result;
- mandate-time/final identities for exactly three later paths and both CREATE
  absence proofs;
- exact commands, counts, RCs, skips and roots;
- exact schema/canonical-input, identity-mismatch and full action matrices;
- exact trusted Event/Intent/price and trusted Pure-Control-Decision mismatch
  matrices, including correctly refingerprinted negative Requests;
- autonomous-exit proof without synthetic Intent;
- S4 NONE/SOFT/HARD/EMERGENCY outcomes;
- Loss-specific NOOP positive, clean-State and non-Loss-only blocker outcomes;
- every exact Section-10 failure code and deterministic precedence outcome;
- replay/conflict and pure negative-capability evidence;
- V1/Shadow compatibility and no active V2 consumer;
- every Section-5 hash and I2 freeze identity;
- full Live-L1, regression, compile and `git diff --check` results;
- exact three-path mutation-scope output;
- no real State/Journal/Authorization/Session/Loop/Exchange/process mutation;
- no Git mutation, cleanup or foreign-artifact change; and
- residual limits plus exactly `I4_RESULT:PASS` or `I4_RESULT:BLOCKED`.

I4 PASS does not claim an active consumer, accepted Snapshot commit, I5
readiness, ENFORCED entry or activation.

## 15. Stop conditions

I4 stops as `BLOCKED`, creates no PASS Evidence and does not broaden scope if:

- any controlling/start/absence/freeze/preservation identity differs;
- another path is needed;
- any V1/Shadow/Control/Atomic/Gate/full/regression parity fails;
- Coordinator, Artifact, Loss, Control, Gate, Loop, Execution, Shadow or tool
  changes become necessary;
- defaults, Float, noncanonical Decimal or incomplete identity binding appears;
- any Request Event/Intent/price or Action/Reason is accepted without exact
  trusted-context equality;
- autonomous exits require fabricated Intent;
- Loss-specific NOOP is accepted without the exact Atomic Loss/S4 predicate;
- a failure is emitted under a code other than the Section-10 mapping;
- validation performs commit, economics, settlement or State mutation;
- V1 is usable as V2 fallback or an active module imports V2;
- real operational input is required;
- any mandatory test fails, errors or skips; or
- Git mutation, cleanup, deletion or foreign-artifact change occurs.

## 16. Prohibited scope

I4 does not authorize Atomic/I3 changes; active commits; Quantity/Quote/
Settlement/Account/Loss mutation; Snapshot/Cursor/audit/recovery; Loop or
Execution Seam wiring; Gate/Authorization/Ledger/Profile changes; Shadow
changes; I5-I8; Workstation/activation; GS/Research/RCC002/engine/run_engine;
Exchange/Live/Production; new config/fixture/sidecar/sample/manifest files;
Git mutation; or cleanup/deletion of foreign artifacts.

## 17. Mandate completion and next gate

```text
MANDATE_RESULT:AUTHORIZED
MANDATE_REVISION:2
I3_INDEPENDENT_ACCEPTANCE:READY
I4_IMPLEMENTATION_ENTERED:NO
I4_IMPLEMENTATION_AUTHORIZED:YES_WITHIN_EXACT_FILE_SCOPE
I5_AUTHORIZED:NO
ACTIVE_V2_CONSUMER_AUTHORIZED:NO
ENFORCED_ACTIVATION_AUTHORIZED:NO
NEXT_REQUIRED_STEP:IU4-I4-ADAPTER-REQUEST-V2-FILE-EXACT-MANDATE-INDEPENDENT-READONLY-REREVIEW-2
```

The mandate becomes usable only after an independent read-only file-exact
review returns `READY`. I4 implementation is then invoked separately. No I4
implementation begins in this mandate-creation turn.
