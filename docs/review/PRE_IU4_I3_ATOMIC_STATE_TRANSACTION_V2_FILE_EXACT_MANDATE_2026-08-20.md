# Pre-IU4 I3 Atomic State / Transaction V2 — File-Exact Mandate — 2026-08-20

## 1. Mandate decision

This record grants the separate file-exact mandate required after independent
I2 acceptance for Revision 21 implementation package I3 only.

```text
MANDATE_ID:IU4-I3-ATOMIC-STATE-TRANSACTION-V2-FILE-EXACT-MANDATE
MANDATE_RESULT:AUTHORIZED
IMPLEMENTATION_PACKAGE:I3_ONLY
I2_INDEPENDENT_ACCEPTANCE:READY
I2_REVISION21_LEDGER:97/97_PASS
I3_IMPLEMENTATION_AUTHORIZED:YES_WITHIN_EXACT_FILE_SCOPE
I4_THROUGH_I8_AUTHORIZED:NO
ACTIVE_LOOP_CONSUMER_AUTHORIZED:NO
ADAPTER_REQUEST_V2_AUTHORIZED:NO
ACTIVE_EXECUTION_SEAM_AUTHORIZED:NO
ENFORCED_LOOP_AUTHORIZED:NO
ENFORCED_ACTIVATION_AUTHORIZED:NO
EXCHANGE_AUTHORIZED:NO
LIVE_AUTHORIZED:NO
```

This mandate creation does not implement I3. It authorizes only the later,
separately invoked I3 implementation workstream and only while every identity,
file boundary, preservation condition and fail-closed rule below remains
exact.

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
| Revision 21 specification | `ab8f80720a1d8fe49b9085bce63658bcaecf7f0a3ea70fb555559223090824e0` | 4,605 | complete and controlling |
| Revision 21 independent rereview | `6618955e67bf9e11798c103eb7d01823dc2ece4c39a66575dbb668c4162c0c7c` | 752 | `READY`, findings `0/0/0/0` |
| Revision 21 terminal R3 handoff | `0aecf831429076a7b732ca6de2482ba02384792919c3f76a3232c1ef27863b2e` | 140 | complete |
| Revision 21 final R3 attestation | `587c5a5ffed271534d661c6c816781eb8443d5c6318fe14d26b1947d21340851` | 179 | final R3 `PASS` |
| I1 file-exact mandate | `2b235193bb7d2986cac3a42e3b078569e1c5e1070e315f6b6b99cc99823bad4a` | 296 | authorized |
| I1 implementation evidence | `24328abbb0e918b0ff5009e32cb026b8624c26dd2bc66fcae49789df55f4b856` | 318 | final I1 identity |
| I1 independent rereview 2 | `adc13abbec3a0458d712df729c2732bce8897be7ecf991a312839616e9687804` | 391 | `READY`, findings `0/0/0/0` |
| I2 file-exact mandate | `bbf2968cfc1de02edb54e1c6ed47951818f7fd6840b10b5d0b7c6ef652eb0517` | 311 | authorized |
| I2 implementation evidence | `950b5b2aa11f3163f0aa1f49f03528ce688de1a5c7506cd12b905dadc55bd516` | 1,215 | final I2 identity |
| initial independent I2 review | `5655a1761ab65f29a7d91099e93342999af54468eac299ecd63b11d42e225dda` | 359 | finding history preserved |
| I2 independent-review resolution | `fbaf549867ea70ef1214204851da52b530bbf47e80762bd37086cdedec86ba53` | 158 | complete |
| supplemental collector mandate decision | `a69bced4751ebbd608b0ff081079f5021c5f57430ec93c478e6b0b90c6c76228` | 171 | one frozen identity authorized |
| final independent I2 rereview | `5a59ad8c97ebae85148661fe0e3bedab643c7f12ae2c8d4e87272447c0616679` | 300 | `I2_INDEPENDENT_ACCEPTANCE:READY`, `97/97 PASS` |
| I2 Preservation package | `3af14ff2e270d7d3ca09c1279da7d64e6d720630d06a0c5f45b6786237782037` | 1,318 | immutable historical freeze |
| I2 Freeze manifest | `ad154c0eda13470920878873ed170368cc8f4c43591400a07592a77b179d9e16` | 60 | immutable historical freeze |

Revision 21 Section 20 is decisive: I3 is Atomic State/Transaction V2 with
S4V2, Entry Quote, Progress Cursor, authoritative Loss Cluster, the separate
Tick/Control ordering spaces, `PROGRESS`, `ENTRY_VETO`, offline V1-to-V2
migration and fault injection. There is no active loop consumer in I3.

## 3. I3 objective and ceiling

I3 implements only a dormant, additive and independently testable Atomic V2
state authority:

1. `EntryEconomicsQuoteArtifactV1`, preserving every field of the original
   `EntryEconomicsQuote` without recomputation or Float conversion;
2. pure deterministic Loss-Cluster transitions over `LossClusterStateV2`,
   with the existing Legacy store and its persistence behavior unchanged;
3. `AtomicProgressCursorV1`, `PaperRiskStateS4V2`, `AtomicPaperStateV2` and
   `AtomicPaperTransactionV2`;
4. exactly-once OPEN, CLOSE, ENTRY_VETO and PROGRESS Tick transactions plus
   separately ordered KILL Control transactions;
5. authority-generation/root preservation, journal-first recovery and all
   required V2 cross-state invariants; and
6. an offline, synthetic, lifecycle-ledger-bound Atomic V1-to-V2 migration
   contract and its crash/fault matrix.

I3 must end with no active adapter, no active runtime-gate identity change, no
loop or execution wiring and no owner activation. It must not execute Genesis,
handoff, migration, restart, recovery or terminal-gap reconciliation against
any real state. All write and fault tests use fresh test-owned temporary roots.

I3 is not permission to redesign Economics, Throttle, S2 V2, Trade V2,
Lifecycle Ledger, Authorization, Runtime Gate, terminal capability or Legacy
V1 behavior. A demonstrated conflict between the exact current V1 contracts
and Revision 21 stops I3 as `BLOCKED`; it is not silently repaired or
reinterpreted.

## 4. Exact authorized file set

### 4.1 Existing production files permitted additive modification

| Path | Mandate-time SHA-256 | Lines | Authorized change |
|---|---|---:|---|
| `live_l1/state/paper_artifacts.py` | `673d7d254c2b3a9b7b5aba8652aae04d6b5411d5a3079cedb9d23602a283d94f` | 1,136 | add only `EntryEconomicsQuoteArtifactV1`, `PaperRiskStateS4V2`, strict serialization/deserialization and fingerprint/cross-field validation |
| `live_l1/state/loss_cluster.py` | `a82259e91df12191f2775584094b2febbe7a5efb7a0107dd642e55b37cca1bb6` | 406 | add pure CLOSE-update and ENTRY_VETO-decrement transitions; preserve `LossClusterStateStore` and existing schemas |
| `live_l1/state/paper_atomic_coordinator.py` | `6460dbfc58acaf6ca0ac56120a1e7460e79981ead30959909f881deef563c1f5` | 1,799 | add Progress Cursor, Atomic State/Transaction V2, V2 coordinator/journal/recovery/migration behavior and reason codes without changing V1 contracts |

### 4.2 New focused tests and implementation evidence

All paths below are absent at mandate time.

| Path | Authorized purpose |
|---|---|
| `tests/live_l1/test_paper_atomic_coordinator_v2.py` | complete Entry Quote, S4V2, pure Loss transition, State/Transaction V2, ordering, migration, recovery, idempotence and fault matrix |
| `docs/review/PRE_IU4_I3_ATOMIC_STATE_TRANSACTION_V2_IMPLEMENTATION_EVIDENCE_2026-08-20.md` | exact identities, matrices, commands, counts, preservation proof, scope and I3 result |

No other source, test, fixture, migration data file, state sample, manifest,
configuration, schema sidecar, documentation or evidence path is authorized.
No generated source or repository-local runtime artifact is authorized. If an
additional path becomes technically necessary, I3 stops before creating or
modifying it and requests a revised file-exact mandate.

## 5. Explicit read-only preservation boundary

### 5.1 Frozen I2 package

The following historical I2 freeze must remain byte- and mode-identical:

| Path | Required SHA-256 | Required mode |
|---|---|---:|
| `archive/IU4_I2_FREEZE_20260820/IU4_I2_PRESERVATION_20260820.tar.gz` | `3af14ff2e270d7d3ca09c1279da7d64e6d720630d06a0c5f45b6786237782037` | `0444` |
| `archive/IU4_I2_FREEZE_20260820/FREEZE_MANIFEST.txt` | `ad154c0eda13470920878873ed170368cc8f4c43591400a07592a77b179d9e16` | `0444` |

`archive/IU4_I2_FREEZE_20260820` remains mode `0555`. The freeze is the
immutable historical I2 identity. This later I3 mandate explicitly permits
changes only to the three canonical files in Section 4.1; it does not rewrite,
normalize or regenerate the archived I2 copies or any I2 evidence.

### 5.2 Directly adjacent canonical files

| Path | Required mandate-time SHA-256 | Lines |
|---|---|---:|
| `live_l1/state/iu4_lifecycle_ledger.py` | `d72134195f66b1d39c09a2ca6b9919d8a9acf17c4490ab52d9abc2aebcd71337` | 438 |
| `live_l1/core/paper_iu4_runtime_gate.py` | `447573e484bc13023a118ae61bf7615657293be629c30729748e64f0af7af7c5` | 201 |
| `live_l1/core/paper_iu4_startup_gate.py` | `c4a1854f3b200525568a40205b39e9ce2e14c342bb860569ba7fcfe5e9c063cd` | 919 |
| `live_l1/core/paper_iu4_shadow_runtime_gate.py` | `98d986f3ac2e463b371998604d92b29aa113a507dd0f84bcbd3ff36a52efaf59` | 438 |
| `live_l1/core/paper_iu4_shadow_observation_gate.py` | `ed4e75fad664c68b91950e9c09e873823ebe3eb0b0062f85806daa09ce661350` | 886 |
| `live_l1/core/paper_iu4_adapter.py` | `d65525f31746d1edf30bf1ffc7f84a845f97b3f4120904c9910b741bc8c76a7b` | 641 |
| `live_l1/core/loop.py` | `54e9e7bc0977a9c94f2e85a3279157678249a8569cff63f7d4f29131443fd058` | 1,411 |
| `live_l1/core/execution.py` | `5aed85ce2754dbb4d8984a1d699b607e3a522ed6da000df119ecd782a4e764d8` | 1,147 |
| `live_l1/core/paper_execution_control.py` | `7d3cb901c1c67c8df85e99bc579fda85d8732b634ff4747e08620b92ac1e44f7` | 257 |
| `live_l1/state/state_store.py` | `50a85cf6bd382850d39e69cd785a5dc2ded0a66a1d82856b4baa11877bdba177` | 220 |
| `live_l1/state/models.py` | `3254d2f1a6509ec5f8f623dd8f286f60cfcc108f66f2d8eb107338d795115c7e` | 27 |
| `live_l1/core/paper_economics.py` | `a302013134d1265ac85ad10b57a67ead9e2343043f7eb499fd965a44312525ae` | 730 |
| `live_l1/core/paper_entry_throttle.py` | `ad5447d88a2c35c9a71a5495c61c8f08fa844daf60e79d4a872234e88037df75` | 727 |
| `live_l1/state/paper_entry_throttle.py` | `ce76d8430792d6de1cfdf9a55c09cb6ab501489c7610d2f78345f8d78646295b` | 586 |
| `tests/live_l1/test_paper_atomic_coordinator.py` | `a46f622f9a00e5db727ade04ece89b4deaf51347dc2d1f4d304532572b382753` | 891 |
| `tests/live_l1/test_loss_cluster_state.py` | `0a7823175eb55d39d22d0576e1d58296d4b5123028e0fbfff561c1a6b642fe35` | 413 |
| `tests/live_l1/test_paper_execution_control.py` | `0ae44f2d32f5f3b6affe37a258be0e6aee06790f857e4fc01628c6795bda99e5` | 843 |
| `tests/live_l1/test_iu4_lifecycle_ledger.py` | `f01c2eda7ceec56fad18acec20a09afaa187b4fd4850ab17a974e6bfe8200093` | 50 |
| `tests/live_l1/test_paper_iu4_runtime_gate.py` | `c1137ddcdec7f40ccf463cfc28719d92ea4d766b5be81e6129f6e7bd174f500d` | 24 |

Revision 21, all R3 records, all I1/I2 governance and evidence, all other I2
implementation/test/native/tool files, the supplemental collector identity,
Workstation R3 artifacts and the frozen validator are immutable inputs.

## 6. Required implementation order

The later I3 workstream must execute in this order:

1. reverify repository, controlling-record, freeze, authorized-file,
   preservation-file and absent-path identities from Sections 2, 4 and 5;
2. rerun and record the mandate-time V1/adjacent baseline from Section 13;
3. create the one focused V2 test module with schema, pure-transition,
   cross-state, transaction-order, authority-root, migration and crash cases;
4. add `EntryEconomicsQuoteArtifactV1` and `PaperRiskStateS4V2` and pass their
   focused tests before any coordinator V2 commit path is added;
5. add pure Loss-Cluster transitions and prove they perform no filesystem,
   environment, clock or Legacy-store access;
6. add V2 value types and strict serializers, then cross-state validation;
7. add the V2 coordinator Tick/Control journal and recovery paths, keeping all
   V1 types, paths, formats and behavior intact;
8. add offline V1-to-V2 migration last, reusing the read-only I2 Lifecycle
   Ledger contract without changing it;
9. run every focused, preservation, full-suite, regression, compile and scope
   command in Section 13;
10. reverify the exact five-path later-implementation mutation ceiling and
    every preservation/freeze identity; and
11. create the I3 implementation evidence record only after all required
    checks pass.

Failure at any step prevents later steps from claiming success. A durable
journal record must never be deleted or rewritten to make a fault test pass.

## 7. Versioned artifact and aggregate-state contract

### 7.1 `EntryEconomicsQuoteArtifactV1`

The artifact is immutable, import-safe and strict. It must:

- serialize every field of `EntryEconomicsQuote` exactly once;
- encode every Decimal as its canonical Decimal string and reject binary
  Float input at the artifact boundary;
- bind Economics Profile ID, Economics Model Version and Config Fingerprint;
- use a canonical self-excluding quote fingerprint;
- reject missing fields, unknown fields, invalid side, non-finite/noncanonical
  numbers, invalid fingerprint and any round-trip value change; and
- recreate an equal `EntryEconomicsQuote` for unchanged `settle_trade()` use,
  without calling `authorize_entry()` or recomputing any quote field.

S2 OPEN requires exactly one quote and S2 FLAT requires `entry_quote=null`.
Side, Quantity, reference/modeled entry values, fees, Economics identities and
all other common S2/Quote fields must match exactly. CLOSE uses only the quote
committed with OPEN.

### 7.2 `AtomicProgressCursorV1`

The cursor binds at least the last completely processed Snapshot ID,
Timestamp UTC, Tick ID and Intent ID plus a canonical cursor fingerprint. Empty
initial values are explicit and versioned. Snapshot/Tick replay with the same
identity and payload is idempotent; the same identity with a different payload
is `PEE_IU4_PROGRESS_CONFLICT`. A Control transaction never owns or advances a
Tick cursor.

### 7.3 `PaperRiskStateS4V2`

S4V2 binds, without defaults:

- schema 2, System State ID, Kill Level, Cooldown, `trades_today`, canonical
  Decimal `loss_today`, `anomaly_counter`, `trades_6h` and last-trade UTC;
- `entry_allowed`, `exit_evaluation_allowed`, `runtime_directive` and ordered,
  unique deterministic reason codes;
- Position, Account, Throttle, Loss Cluster, Progress Cursor, Runtime Control
  and Loss-Cluster Policy identities/fingerprints;
- Authority Generation ID, Transaction Sequence, Journal Head, last event/time
  identities and its own self-excluding S4 fingerprint.

The capability matrix is exact:

| Kill level | Entry | Exit evaluation | Runtime directive |
|---|---:|---:|---|
| `NONE` | according to guards | yes | `CONTINUE` |
| `SOFT` | no | yes | `CONTINUE` |
| `HARD` | no | no | `STOP_LOOP` |
| `EMERGENCY` | no | no | `EXIT_PROCESS` |

S4V1 remains valid only in Atomic V1 and is rejected inside Atomic V2 with
`PEE_IU4_S4_SCHEMA_UNSUPPORTED`. `exit_evaluation_allowed` is a capability,
never an automatic exit command. No Tick, restart or date change may
deescalate KILL.

### 7.4 `AtomicPaperStateV2`

Atomic V2 strictly and canonically binds:

- Coordinator and System State identities, schema 2, Transaction Sequence and
  Journal Head/event identity;
- complete S2 V2, Paper Account, Entry Throttle, LossClusterStateV2,
  AtomicProgressCursorV1, PaperRiskStateS4V2 and the optional complete Entry
  Quote;
- Economics, Throttle, Runtime-Control and Loss-Cluster Policy IDs and
  fingerprints;
- `state_owner_epoch=PEE`, Authority Generation ID, Authority PREPARE Record
  Fingerprint and the exact Genesis/Handoff/Migration Manifest ID; and
- every component and cross-state fingerprint in one aggregate fingerprint.

Ledger Tip and Authority-COMMIT Fingerprint are expressly excluded from the
State fingerprint. Every transition preserves Authority Generation and
PREPARE fingerprint exactly. The first V2 transaction's `state_before` equals
the full target State bound by the valid Authority COMMIT; every later State
must have a gap-free journal ancestry from that root. A self-consistent journal
with a wrong Authority root is invalid.

Atomic V1 remains readable only by its existing V1 consumers and the explicit
offline migration input. It is never silently parsed or activated as V2.

## 8. Tick, Control and Lifecycle ordering contract

V2 keeps three disjoint ordering spaces:

1. one cursor-owning Tick transaction per `ACCEPTED` non-terminally-discarded
   Snapshot, with exactly one `primary_effect` of `OPEN`, `CLOSE`,
   `ENTRY_VETO` or `PROGRESS`;
2. KILL as a Control transaction with its own Control Event ID and no Progress
   Cursor, optionally referencing the causal Tick ID; and
3. Genesis, handoff, migration, authorization consumption and recovery
   materialization only as Lifecycle Ledger records, never Tick/Control
   transactions.

The atomic Tick effects are exact:

- OPEN: FLAT-to-OPEN S2, complete Entry Quote, accepted Throttle event,
  Progress Cursor and bound S4; Account and Loss Cluster unchanged;
- CLOSE: Trade V2, Paper Account, OPEN-to-FLAT S2, Quote-to-null, Loss Cluster,
  Progress Cursor and bound S4; accepted Throttle unchanged;
- ENTRY_VETO: exactly one reproducible Loss-Cluster pause decrement, Progress
  Cursor and derived S4; S2, Account and accepted Throttle unchanged; and
- PROGRESS: only Progress Cursor and the necessarily rebound S4/Aggregate
  identities; no Economics, S2, Account, Throttle or Loss mutation.

ENTRY_VETO is legal only for the established active Loss-Cluster pause that
blocks an actual Entry candidate and decrements `pause_entries_remaining`.
Every other Entry denial leaves all business components unchanged and commits
PROGRESS only after the Snapshot is `ACCEPTED`.

The optional Tick `risk_escalation` is absent without transition and otherwise
exactly `NONE_TO_SOFT`. `NONE_TO_NONE`, `SOFT_TO_SOFT`, every deescalation and
every HARD/EMERGENCY Tick transition are rejected. CLOSE plus SOFT is one
CLOSE Tick transaction. Terminal KILL before durable Tick journal discards the
uncommitted Tick; durable Tick journal first remains authoritative and is
materialized before one separate KILL Control transaction. The same rule
orders ENTRY_VETO plus terminal KILL. OPEN is forbidden once terminal KILL is
pending or known.

Every journal record contains complete strict before/after V2 State, sequence,
previous head, unique Event ID, canonical timestamp, effect-specific payload
and self-excluding transaction fingerprint. Same Event ID with byte-equivalent
payload is idempotent; divergent payload, gap, fork, regression, unknown field
or root change fails closed. Journal write is durable before atomic Snapshot
replace; recovery materializes only an already durable record and never
redecides business behavior.

## 9. Loss-Cluster and Economics contract

The new Loss-Cluster functions are pure value transitions. All inputs,
including canonical UTC, policy values, Policy ID and Policy Fingerprint, are
explicit. They do not access environment, clock, filesystem, store, logs,
adapter, loop or global mutable state.

- CLOSE appends exactly the canonical Decimal net PnL from committed
  `TradeRecordV2`, applies the established lookback/loss-threshold/pause policy
  once, advances Revision once and returns a new `LossClusterStateV2`.
- ENTRY_VETO is legal only when `pause_entries_remaining > 0`, decrements it
  exactly once, advances Revision once and changes no other business State.
- PROGRESS, other Entry denials and KILL never apply either Loss transition.
- A duplicate committed Event never repeats a transition.

Legacy `LossClusterStateStore`, V1-to-V2 Legacy parsing and all existing
OFF/SHADOW persistence semantics remain byte-compatible and are not used as a
second ENFORCED state truth. New PEE PnL accepts Decimal/canonical Decimal
strings only; Legacy Float compatibility is not a new economic boundary.

CLOSE deserializes exactly the committed Entry Quote, invokes unchanged
`settle_trade()` once, builds Trade V2 from committed Decimal artifacts and
uses its canonical net PnL for both Account and Loss Cluster. Fees, slippage or
settlement are never recomputed or applied twice.

## 10. Offline Atomic V1-to-V2 migration contract

Migration is a separate, offline lifecycle operation over synthetic/temp test
roots in I3. It is never an import-time or Startup auto-migration. The
implementation must:

1. require an explicit strict migration artifact binding source V1 path,
   schema and full fingerprint; validated Legacy Loss-Cluster source path,
   schema, checksum and fingerprint; target V2 path/core/business identity;
   all profiles/policies; complete S4V2 Safety Heads; Progress Cursor; Owner
   Epoch; source Authority Generation/Anchor; Manifest and Approval;
2. reject an OPEN or contradictory V1 position, missing/conflicting state,
   `missing_allowed`, unsafe path, schema/checksum mismatch, partial S4,
   defaulted `loss_today`/`anomaly_counter` or positions-only migration;
3. reuse the unchanged `IU4LifecycleLedgerV1` and its existing
   `ATOMIC_V1_TO_V2_MIGRATION_PREPARE/COMMIT` record types;
4. compute business payload, Authority Generation, Target Core, durable
   PREPARE, PREPARE-bound full Target State and reconciled COMMIT in the
   self-reference-free Revision 21 order;
5. keep the source bytes unchanged and publish no target before durable
   PREPARE; and
6. leave a post-PREPARE/pre-COMMIT interruption as one open Authority PREPARE,
   requiring the already specified manual `COMPLETE_AUTHORITY_PREPARE`
   operation. I3 does not execute that operation against real state and does
   not modify its I2 authorization/consumption contract.

Migration success creates no Runtime Session, starts no loop, consumes no
Activation Authorization and does not activate ENFORCED. Tests may only use
synthetic records and fresh temporary roots.

## 11. Mandatory focused and fault matrix

The new focused V2 test module must cover at least:

1. strict round trips and tamper/unknown/missing/noncanonical/Float rejection
   for Entry Quote, Cursor, S4V2, Atomic State V2 and Transaction V2;
2. every Entry Quote field, direct equal reconstruction and absence of
   `authorize_entry()` during CLOSE;
3. FLAT/null-Quote and OPEN/exact-Quote cross-state parity, including every
   common field and all profile identities;
4. complete S4V2 NONE/SOFT/HARD/EMERGENCY capability matrix, all Legacy S4
   fields without defaults, S4V1 rejection and forbidden deescalations;
5. aggregate component fingerprints, exclusion of Ledger Tip/COMMIT from the
   State fingerprint and preservation of Authority Generation/PREPARE root;
6. exactly one Tick transaction/cursor for OPEN, CLOSE, ENTRY_VETO and
   PROGRESS, plus KILL without a cursor;
7. OPEN/CLOSE/ENTRY_VETO/PROGRESS exact mutation allowlists and rejected
   cross-component changes;
8. pure Loss CLOSE and ENTRY_VETO transitions, threshold boundaries, Decimal
   PnL, Revision, duplicate idempotence and no environment/I/O/store access;
9. CLOSE uses the stored Quote, settles once, updates Account/Loss/S2/Quote/S4
   together and never repeats PnL, fee, slippage or pause effects;
10. no-ENTRY_VETO denials commit only PROGRESS after acceptance and mutate no
    S2, Account, Throttle or Loss State;
11. CLOSE+SOFT, terminal KILL before/after durable CLOSE or ENTRY_VETO,
    pending-KILL OPEN rejection and exact Tick/Control Event IDs;
12. repeated equal Snapshot/Tick/Event idempotence; changed duplicate, gap,
    fork, sequence/time/tick regression, corrupt journal and wrong root fail
    closed;
13. interruption before journal write, after durable journal write, before
    Snapshot replace and after replace for every OPEN, CLOSE, ENTRY_VETO,
    PROGRESS and KILL path;
14. recovery from durable journal only, stale/missing Snapshot materialization,
    snapshot-ahead rejection and no second business decision;
15. Atomic V1 remains round-trip and behavior compatible under the complete
    existing V1 test module;
16. V1-to-V2 migration before/after PREPARE, before/after Target publication
    and before/after COMMIT; source immutability, open-position rejection,
    missing/corrupt Loss rejection, wrong Authority binding and idempotent
    target reconciliation;
17. open PREPARE remains non-active and completion-required; COMMIT binds the
    exact PREPARE and full target State without a hash cycle;
18. disk-full, permission, file-descriptor, short/truncated/corrupt JSON and
    simulated resource errors at every durable boundary, with no partial
    authoritative State claim; and
19. every persisted V2 aggregate, transaction, quote, Decimal and fingerprint
    is deterministic, canonical and contains no binary Float.

No test may read or mutate real trading/research inputs, production State,
existing Atomic/Lifecycle roots, the I2 freeze, Workstation/R3 evidence or any
foreign process. Fault tests use only their own temporary directories and
synthetic objects.

## 12. Stable failure and stop conditions

Existing precise reason codes remain controlling. I3 must use the applicable
Revision 21 families, including:

```text
PEE_IU4_AUTHORITY_PREPARE_INCOMPLETE
PEE_IU4_AUTHORITY_COMMIT_MISMATCH
PEE_IU4_AUTHORITY_ROOT_MISMATCH
PEE_IU4_LIFECYCLE_OPERATION_INCOMPLETE
PEE_IU4_S4_SCHEMA_UNSUPPORTED
PEE_IU4_ENTRY_QUOTE_REQUIRED
PEE_IU4_PROGRESS_CONFLICT
PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED
PEE_IU4_RESOURCE_EXHAUSTED
```

I3 stops `BLOCKED` without expanding scope if any required starting identity or
freeze hash differs; a create-target already exists; the 114-test baseline
fails; an I2/I1/I4/I5/I6 file change becomes necessary; a real-state write or
active consumer is required; a required field cannot be derived from
Revision 21/current contracts; an extra path is needed; V1 compatibility
fails; a mandatory fault cannot be exercised in temporary scope; or any
required test, preservation hash or scope check fails.

## 13. Required verification commands

All commands use the repository `.venv`, `PYTHONDONTWRITEBYTECODE=1`, isolated
cache/temp roots and no network or real inputs. At minimum:

```bash
.venv/bin/python -m unittest tests.live_l1.test_paper_atomic_coordinator_v2
.venv/bin/python -m unittest tests.live_l1.test_paper_atomic_coordinator
.venv/bin/python -m unittest tests.live_l1.test_loss_cluster_state
.venv/bin/python -m unittest tests.live_l1.test_paper_account
.venv/bin/python -m unittest tests.live_l1.test_paper_economics
.venv/bin/python -m unittest tests.live_l1.test_paper_entry_throttle
.venv/bin/python -m unittest tests.live_l1.test_iu4_lifecycle_ledger
.venv/bin/python -m unittest tests.live_l1.test_paper_iu4_runtime_gate
.venv/bin/python -m unittest discover -s tests/live_l1 -p 'test_*.py'
.venv/bin/python -m unittest discover -s tests/regression -p 'test_*.py'
.venv/bin/python -m py_compile live_l1/state/paper_artifacts.py live_l1/state/loss_cluster.py live_l1/state/paper_atomic_coordinator.py tests/live_l1/test_paper_atomic_coordinator_v2.py
git diff --check
```

Every Python command above is run with `PYTHONDONTWRITEBYTECODE=1` in the
environment. Exact scope is checked against the five later-implementation
paths in Section 4; the mandate file itself is the sole artifact of this
mandate-creation workstream and is not an I3 implementation mutation.

Mandate-time adjacent baseline:

```text
test_paper_atomic_coordinator
+ test_loss_cluster_state
+ test_paper_account
+ test_paper_economics
+ test_paper_entry_throttle
+ test_iu4_lifecycle_ledger:114/114_PASS
```

Any failure, error, unexpected skip, repository-local bytecode, real-input
dependency, freeze/preservation mismatch or out-of-scope path blocks I3.
Passing adjacent tests does not replace any focused new-module test.

## 14. Evidence and I3 completion gate

The authorized implementation evidence record must contain:

- all controlling identities and prerequisite results from Section 2;
- mandate-time and final identities for all five authorized paths, including
  proof that the two create-targets were absent;
- exact commands, counts, return codes, skips and temporary-root identities;
- complete schema/field/cross-state and effect mutation-allowlist matrices;
- complete Tick/Control/Lifecycle ordering and risk-escalation matrices;
- all fault points and exact before/journal/snapshot/after/recovery outcomes;
- Entry Quote equal-roundtrip and no-reauthorization evidence;
- pure Loss-transition negative-capability evidence;
- Authority-root/generation/PREPARE ancestry and migration source-immutability
  evidence;
- V1 compatibility, full `tests/live_l1`, regression and compile results;
- final I2 freeze modes/hashes and every Section-5 preservation hash;
- `git diff --check` and exact mutation-scope output;
- confirmation that no real Genesis, migration, handoff, restart, recovery,
  Runtime Session, terminal-gap operation, State, journal, R3/Workstation,
  Research, Exchange, Live, scheduler or process mutation occurred;
- confirmation that no Git stage, commit, fetch, push, cleanup or foreign
  artifact change occurred; and
- all residual limits plus exactly `I3_RESULT:PASS` or `I3_RESULT:BLOCKED`.

I3 passes only if the entire State/Transaction V2 contract, migration/fault
matrix, V1 preservation, full suites, freeze hashes and file-exact scope pass.
An I3 PASS does not claim an active consumer, I4 readiness, ENFORCED entry or
activation.

## 15. Prohibited scope

I3 does not authorize:

- any file outside Section 4, including changes to Lifecycle Ledger, Runtime
  Gate, Authorization, terminal/native capability, supplemental collector,
  adapter, loop, execution, Legacy state store/models, monitoring, recovery or
  projection tools;
- I1 or I2 reimplementation, evidence regeneration or freeze regeneration;
- I4 Adapter Request V2 or Adapter V1 modification;
- I5 Active Execution Seam, active loop consumer or Legacy side-effect change;
- I6 recovery/monitoring/projection, I7 validation or I8 activation review;
- real Atomic Genesis, V1-to-V2 migration, handoff, Restart/Recovery
  Authorization consumption, PREPARE completion or owner transition;
- ENFORCED loop entry, runtime activation, profile activation, Exchange, Live,
  credentials or production State;
- changes under `engine/`, `run_engine/`, `scripts/state_research/`, Research,
  GS or RCC002;
- Workstation/R3/validator/scheduler/launcher rerun, existing process control
  or real-data test;
- staging, commit, fetch, push, cleanup, deletion, archive mutation or
  alteration of foreign tracked/untracked artifacts; or
- reading, executing, modifying, staging or committing
  `scripts/build_rcc002_spec_bundle.py`.

## 16. Exact next governance step

The only implementation workstream authorized by this mandate is:

```text
IU4-I3-ATOMIC-STATE-TRANSACTION-V2-IMPLEMENTATION
```

That later workstream may touch only the five paths in Section 4 and must
follow Sections 6 through 15. After passing I3 evidence, the next action is an
independent, read-only, file-exact I3 implementation review. I4 remains
unauthorized until I3 receives independent `READY` and a separate I4 mandate.
