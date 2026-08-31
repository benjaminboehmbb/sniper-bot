# PRE-IU4 I3 Atomic State/Transaction V2 — Section-14 Complete Implementation Evidence

Date: 2026-08-20  
Repository: `/home/benja/projects/sniper-bot`  
Workstream: `IU4-I3-ATOMIC-STATE-TRANSACTION-V2-IMPLEMENTATION-REREVIEW-5-EVIDENCE-PRECISION-RESOLUTION-FILE-EXACT`

```text
I3_RESULT:PASS
I3_IMPLEMENTATION_COMPLETE:YES_IMPLEMENTATION_SIDE
I3_REREVIEW_4_EVIDENCE_BLOCKER_RESOLVED_IMPLEMENTATION_SIDE:YES
I3_REREVIEW_5_EVIDENCE_PRECISION_FINDINGS_RESOLVED_IMPLEMENTATION_SIDE:YES
EVIDENCE_SECTION_14_COMPLETE:YES
I3_SELF_CERTIFIED:NO
I3_INDEPENDENT_ACCEPTANCE:PENDING
I4_AUTHORIZED:NO
ENFORCED_ACTIVATION_AUTHORIZED:NO
```

This record supersedes the 452-line evidence rejected by independent rereview
5 solely for an omitted regression skip value and imprecise bytecode scope/UTC
serialization. It remains self-contained for every I3 mandate Section-14
requirement. Source and tests are unchanged from rereviews 4 and 5. A fresh
independent read-only file-exact rereview 6 is required before I3 acceptance.

## 1. Complete controlling identity and prerequisite closure

```text
CANONICAL_REPOSITORY:/home/benja/projects/sniper-bot
BRANCH:main
HEAD:c7ce0452aa2ccbf08c462784d68fa07b3dfe9595
MAIN:c7ce0452aa2ccbf08c462784d68fa07b3dfe9595
ORIGIN_MAIN:89e13fecd1ab549ca7099818b1c9ad4984cb6f7a
MAIN_BEHIND_ORIGIN:0
MAIN_AHEAD_OF_ORIGIN:6
```

Every controlling artifact from mandate Section 2 was recomputed:

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
| supplemental collector mandate decision | `a69bced4751ebbd608b0ff081079f5021c5f57430ec93c478e6b0b90c6c76228` | 171 | frozen identity authorized |
| final independent I2 rereview | `5a59ad8c97ebae85148661fe0e3bedab643c7f12ae2c8d4e87272447c0616679` | 300 | `I2_INDEPENDENT_ACCEPTANCE:READY`, `97/97 PASS` |
| I2 Preservation package | `3af14ff2e270d7d3ca09c1279da7d64e6d720630d06a0c5f45b6786237782037` | 1,318 entries | immutable historical freeze |
| I2 Freeze manifest | `ad154c0eda13470920878873ed170368cc8f4c43591400a07592a77b179d9e16` | 60 | immutable historical freeze |

I3 governance chain after the mandate:

| Artifact | SHA-256 | Lines | Result |
|---|---|---:|---|
| I3 file-exact mandate | `775aeb62e6ff0a1ca3af970970053b43d176f1122560774f184ecf40a8fcced5` | 558 | `READY` |
| initial independent I3 rereview | `149102087a918121098aaf72c71d73a4150e631837a5fa8d671204a9b473a9dc` | 234 | historical `NOT_READY` |
| first corrective resolution | `12ad2d647443a22a7684be1a6f598caba17dfff13c87717b6aecbc14318d4f01` | 206 | implementation-side |
| independent I3 rereview 2 | `b33bd8efb7c4d82c8a4889c74a845911a0207a7d1e921375f8df6651d8e4847c` | 240 | historical `NOT_READY` |
| corrective resolution 2 | `2c90b342264dffe197cc94a2d500310c6b29cc28e83172fccf9460b26792523d` | 181 | implementation-side |
| independent I3 rereview 3 | `341261848f45acf31abb3a7c9ac552d407aabf4ac3fcbdb5519ceb7051d217a8` | 238 | historical `NOT_READY` |
| corrective resolution 3 | `ebaf066ada49afc3d20753cd8b15bdc587f74761dfa99d293bc8c8d3dccc3fd5` | 194 | implementation-side |
| independent I3 rereview 4 | `2b5c17626762e3aece9ddc052655881f1af81889cfaf4debb2fea1d894bdd84c` | 227 | `NOT_READY`, Evidence-only blocker 1/0/0/0; code technically green |
| superseded 192-line Evidence | `c1d98ecae5fe432cf65bdd49b4ed254f7819a31cc3fd0c37a95258c7f3e16dcb` | 192 | replaced by this complete record |
| rereview-4 Evidence-completeness resolution | `5456d3af5d0ec0767814107f2701c8fdcb202f9455767a40a8616d2f9bf4fe5f` | 157 | implementation-side closure; superseded identity binding |
| superseded 452-line Evidence | `02c8cca35fae068579fb54486c6894754d2d948352f47457a3bd72722a246d4e` | 452 | rejected only for precision serialization |
| independent I3 rereview 5 | `8222228de88b9a63d570852ba3eaa32cb86244b24fc53ea0c013fb87ffbcf65e` | 224 | `NOT_READY`, findings 1/0/0/1; no technical defect |

## 2. Five-path mandate-time, rereview-5 pre-resolution and final identities

The two CREATE paths were absent at mandate time. This fact is bound by the
file-exact mandate SHA above, Section 4.2 line 106, before either file existed.

| Operation | Authorized path | Mandate-time identity | Rereview-5/pre-resolution identity | Final identity |
|---|---|---|---|---|
| MODIFY | `live_l1/state/paper_artifacts.py` | `673d7d254c2b3a9b7b5aba8652aae04d6b5411d5a3079cedb9d23602a283d94f`, 1,136 lines | `3cd9a459e2856672bb7b318c9cdbf8f8bb52e633ee9529d74761d64928213946`, 1,575 | same as rereview 4 |
| MODIFY | `live_l1/state/loss_cluster.py` | `a82259e91df12191f2775584094b2febbe7a5efb7a0107dd642e55b37cca1bb6`, 406 lines | `4ce7d59f64a67de94ffc6f1d03ff4e6c8a7a590802abb003b311cd0d56cc3e55`, 521 | same as rereview 4 |
| MODIFY | `live_l1/state/paper_atomic_coordinator.py` | `6460dbfc58acaf6ca0ac56120a1e7460e79981ead30959909f881deef563c1f5`, 1,799 lines | `d0721ae5def3551ba7281ea0e367f5347890fd4cd7187d8f2aebb98d2651e84f`, 5,489 | same as rereview 4 |
| CREATE | `tests/live_l1/test_paper_atomic_coordinator_v2.py` | `ABSENT`, proven by mandate `775aeb62...` Section 4.2 | `16d0fea6e5588cc14329ba61cfeeccb1f72478d14c358f8ed4e38c1ac3a41bb9`, 2,482 | same as rereview 4 |
| CREATE/REPLACE | this Evidence path | `ABSENT`, proven by mandate `775aeb62...` Section 4.2 | `02c8cca35fae068579fb54486c6894754d2d948352f47457a3bd72722a246d4e`, 452 | 463 lines; standard whole-file SHA-256 is necessarily computed after serialization and recorded in the immediately following Evidence-precision resolution |

The final Evidence-row identity cannot contain its own whole-file SHA-256
without changing that SHA. The companion resolution therefore supplies the
post-serialization whole-file identity; this record supplies every substantive
proof and explicitly identifies that deterministic binding mechanism.

## 3. Complete schema and field matrix

### 3.1 Exact persisted field sets

| Artifact | Exact persisted fields |
|---|---|
| Entry Quote V1 | `schema_version`, `artifact_type`; all 22 original fields: `side`, `reference_entry_price`, `reference_stop_price`, `modeled_entry_fill_price`, `modeled_stop_fill_price`, `realized_equity_quote`, `risk_budget_quote`, `modeled_stop_loss_per_unit_quote`, `risk_quantity`, `notional_cap_quote`, `notional_cap_quantity`, `raw_quantity`, `quantity_step`, `quantity`, `entry_notional_quote`, `entry_fee_quote`, `expected_stop_notional_quote`, `expected_stop_fee_quote`, `modeled_stop_loss_quote`, `economics_profile_id`, `economics_model_version`, `config_fingerprint`; `quote_fingerprint` |
| Progress Cursor V1 | `schema_version`, `snapshot_id`, `timestamp_utc`, `tick_id`, `intent_id`, `cursor_fingerprint` |
| Entry-veto Candidate V1 | `schema_version`, deterministic `candidate_id`, `entry_veto_event_id`, `snapshot_id`, `timestamp_utc`, `tick_id`, `intent_id`, `intent_action`, `symbol`, `side`, pre-veto `loss_cluster_state_fingerprint`, `denial_reason_code`, `candidate_fingerprint` |
| Paper Risk S4V2 | `schema_version`, `system_state_id`, `kill_level`, `cooldown_until_utc`, `trades_today`, `loss_today`, `anomaly_counter`, `trades_6h`, `last_trade_timestamp_utc`, `entry_allowed`, `exit_evaluation_allowed`, `runtime_directive`, `reason_codes`; Position/Account/Throttle/Loss/Cursor fingerprints; Runtime-Control/Loss/Economics/Throttle policy IDs and fingerprints; `authority_generation_id`, transaction sequence/head/event/time/tick; `state_fingerprint` |
| Atomic State V2 | schema/coordinator/system/transaction head; complete Position, Account, Throttle, Loss, Cursor, S4 and nullable Quote; Runtime-Control/Loss policy; owner epoch; Authority Generation/PREPARE ancestry; Manifest ID/fingerprint; `state_fingerprint` |
| Atomic Transaction V2 | schema/sequence/Event/previous head/ordering/effect/time/tick; complete before/after State; optional Accepted Event/Trade; risk/control fields; independent Position/Quote/Cursor/Throttle-policy/Entry-veto-Candidate effect payload; explicit Loss transition inputs; KILL target; `transaction_fingerprint` |
| Migration Artifact V1 | schema/type/ID; source State path/fingerprint/SHA; source Loss path/fingerprint/SHA; target path/Business/Core/System and all six component/business fingerprints; owner/profile/policy/economics/throttle bindings; previous/new owner epoch; Manifest/Approval/source Authority/operator/time; `artifact_fingerprint` |

### 3.2 Parser and canonical-input outcomes

| Artifact | Exact fields | Missing | Unknown | bool-as-int | Float/nonfinite | noncanonical Decimal | tamper/fingerprint | exact roundtrip |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Entry Quote V1 | PASS | reject | reject | reject | reject | reject | reject | equal Quote/record |
| S4V2, no defaults | PASS | reject | reject | reject | reject | reject | reject | equal State/record |
| Progress Cursor V1 | PASS | reject | reject | reject | n/a | n/a | reject | equal Cursor/record |
| Entry-veto Candidate V1 | PASS | reject | reject | reject | n/a | n/a | reject | equal Candidate/record |
| Loss Cluster V2 persisted record | PASS | reject | reject | reject | reject | reject | reject | equal Loss/record |
| Atomic State V2 aggregate | PASS | reject | reject | reject | nested reject | nested reject | root/component reject | equal aggregate/record |
| Atomic Transaction V2 | PASS | reject | reject | reject | nested reject | nested reject | effect/head reject | equal transaction/record |
| Migration Artifact V1 | PASS | reject | reject | reject | n/a | n/a | reject | equal artifact/record |

## 4. Complete cross-state invariant matrix

| Invariant | Required equality / exclusion | Observed result |
|---|---|---|
| System identity | Aggregate `system_state_id` = Position = S4 | PASS; mismatch rejects |
| Position head | S4 Position fingerprint = complete S2 fingerprint | PASS; tamper rejects |
| Account head | S4 Account fingerprint = Account State fingerprint | PASS; stale/tamper rejects |
| Throttle head | S4 Throttle fingerprint = Throttle State; OPEN after-State exactly `apply_accepted_entry(before, bound_policy, accepted_event)` | PASS; caller-selected head rejects |
| Loss head | S4 Loss fingerprint = Loss State; CLOSE/VETO exactly pure derivation from before-State and effect inputs | PASS; unchanged/stale Loss rejects |
| Cursor head | S4 Cursor fingerprint = one complete effect Cursor for Tick; unchanged for Control | PASS; reuse/divergence rejects |
| Quote/S2 | OPEN exactly one Quote matching side, quantity, entry prices/fees and Economics identities; FLAT exactly null | PASS; null OPEN/tamper rejects |
| Account/Throttle counts | FLAT accepted count = closed count; OPEN accepted count = closed count + 1 | PASS; inconsistent aggregate rejects |
| Authority | before/after Generation, PREPARE fingerprint, Manifest and `state_owner_epoch=PEE` identical | PASS; wrong root rejects |
| Aggregate fingerprint | binds every business component and Authority envelope above | PASS; nested tamper rejects |
| Excluded circular authority | Ledger Tip and Authority COMMIT fingerprint not in State fingerprint | PASS; explicit absence asserted by focused test |
| Journal ancestry | after sequence = before + 1; previous head exact; first before-State equals committed target root | PASS; gap/fork/root mismatch rejects |
| Causal OPEN | outer Event = Accepted Event; transaction/Cursor/Accepted Event/Position time equal; transaction/Cursor/Position Tick equal | PASS; refingerprinted/public divergence rejects |
| Causal CLOSE | outer Event = Settlement Event; transaction/Cursor/Trade exit time and Tick equal | PASS; divergence rejects |
| Causal VETO | outer Event/Snapshot/time/Tick/Intent = strict OPEN candidate = Cursor; candidate Loss fingerprint = before Loss | PASS; HOLD/stale/divergent rejects |

## 5. Complete effect mutation allowlist

| Effect | Ordering | Required mutation | Explicitly immutable / forbidden |
|---|---|---|---|
| OPEN | Tick; one new Cursor | FLAT→OPEN S2, exact persisted Quote, one accepted Throttle event, Cursor, derived S4, sequence/head | Account, Loss, Authority, Manifest, profiles; no stale guard or caller-selected Throttle |
| CLOSE | Tick; one new Cursor | Trade-derived OPEN→FLAT S2 with `last_closed_trade_id=trade_id`; Account settlement; Decimal Loss CLOSE transition; Quote→null; Cursor; derived S4 | accepted Throttle, Authority, profiles; no reauthorization/requote/double settlement |
| ENTRY_VETO | Tick; one new Cursor and strict OPEN candidate | exactly one active Loss pause decrement/revision; Cursor; derived S4 | S2, Account, accepted Throttle, Quote, Authority; HOLD/missing/stale/divergent candidate forbidden |
| PROGRESS | Tick; one new Cursor | Cursor and necessarily rebound S4/aggregate fingerprints | S2, Account, Throttle, Loss, Quote, S4 economic counters |
| KILL | Control Event; no Cursor | monotone KILL/capability/reason plus transaction metadata | all Tick components and S4 economic counters; no Tick risk escalation field |
| other Entry denial | no VETO transition | no business mutation; after accepted Snapshot, PROGRESS only | Loss decrement, accepted Throttle, Account, Position, Quote |

Same Event plus byte-equivalent payload is idempotent. Same Event with another
payload, same Snapshot/Tick under another Event, sequence/time regression,
unknown field, fork, gap or root change fails closed. Duplicate CLOSE or VETO
does not repeat Account, Loss or Throttle effects.

## 6. Complete Tick, Control, Lifecycle and risk matrix

### 6.1 Ordering spaces

| Space | Authorized records | Cursor | Identity/order result |
|---|---|---:|---|
| Tick | exactly one of OPEN, CLOSE, ENTRY_VETO, PROGRESS per accepted Snapshot | exactly one new complete Cursor | Snapshot/Tick monotone; equal replay idempotent; divergence conflict |
| Control | KILL only, independent Control Event ID and optional causal Tick | none | does not consume/reuse/advance Tick Cursor |
| Lifecycle | PREPARE, COMMIT, authorization consumption, recovery materialization | n/a | Ledger only; never an Atomic Tick/Control record |

### 6.2 S4 capability and escalation

| Kill level | Entry | Exit evaluation | Runtime directive | Tick behavior |
|---|---:|---:|---|---|
| NONE | according to guards | yes | `CONTINUE` | OPEN/CLOSE/VETO/PROGRESS allowed by guards |
| SOFT | no | yes | `CONTINUE` | only already-required non-entry behavior; no deescalation |
| HARD | no | no | `STOP_LOOP` | every later Tick transaction rejected |
| EMERGENCY | no | no | `EXIT_PROCESS` | every later Tick transaction rejected |

| Requested Tick escalation | Result |
|---|---|
| absent with unchanged KILL | accepted |
| `NONE_TO_SOFT` with before NONE / after SOFT | accepted atomically, including CLOSE+SOFT |
| `NONE_TO_NONE`, `SOFT_TO_SOFT` | rejected as an escalation payload |
| any deescalation | rejected |
| HARD/EMERGENCY Tick transition | rejected; only separate Control KILL |
| terminal KILL before durable Tick journal | uncommitted Tick discarded; KILL authoritative |
| terminal KILL after durable Tick journal | durable Tick recovered/materialized first, then separate KILL |

## 7. Complete durable transaction fault/outcome matrix

The focused suite executes all 20 effect/boundary combinations. `B` is the
baseline sequence (`0`, or `1` for CLOSE after its OPEN).

| Effect | BEFORE_JOURNAL | AFTER_JOURNAL | BEFORE_SNAPSHOT | AFTER_SNAPSHOT |
|---|---|---|---|---|
| OPEN | journal `B`, Snapshot `B`, no recovery | journal `B+1`, Snapshot `B`, recover 1→`B+1` | journal `B+1`, Snapshot `B`, recover 1→`B+1` | journal/Snapshot `B+1`, recover 0 |
| CLOSE | journal `B`, Snapshot `B`, no settlement/Loss effect | journal `B+1`, Snapshot `B`, recover 1 exactly once | journal `B+1`, Snapshot `B`, recover 1 exactly once | journal/Snapshot `B+1`, recover 0 |
| ENTRY_VETO | journal `B`, Snapshot `B`, no decrement | journal `B+1`, Snapshot `B`, recover 1 decrement | journal `B+1`, Snapshot `B`, recover 1 decrement | journal/Snapshot `B+1`, recover 0; one decrement total |
| PROGRESS | journal `B`, Snapshot `B`, no Cursor | journal `B+1`, Snapshot `B`, recover 1 Cursor | journal `B+1`, Snapshot `B`, recover 1 Cursor | journal/Snapshot `B+1`, recover 0 |
| KILL | journal `B`, Snapshot `B`, no KILL | journal `B+1`, Snapshot `B`, recover 1 KILL, no Cursor | journal `B+1`, Snapshot `B`, recover 1 KILL | journal/Snapshot `B+1`, recover 0 |

### 7.1 Resource and structural faults

| Fault | Boundary | Durable result | Classification/recovery |
|---|---|---|---|
| `ENOSPC` | journal create/write | no journal, unchanged Snapshot | `PEE_IU4_RESOURCE_EXHAUSTED` |
| `EACCES` | journal create/write | no journal, unchanged Snapshot | `PEE_IU4_RESOURCE_EXHAUSTED` |
| `EMFILE` | journal create/write | no journal, unchanged Snapshot | `PEE_IU4_RESOURCE_EXHAUSTED` |
| `MemoryError` | journal create/write | no journal, unchanged Snapshot | `PEE_IU4_RESOURCE_EXHAUSTED` |
| `ENOSPC` | Snapshot publication | one durable journal, old Snapshot | `PEE_IU4_RESOURCE_EXHAUSTED`; recovery materializes 1 |
| corrupt/truncated/noncanonical journal | read/recovery | no publication | fail closed |
| journal gap/fork/create-new collision | read/commit | no overwrite/publication | fail closed |
| Snapshot ahead of journal | recovery | no backward claim | fail closed |
| wrong Authority root/self-consistent reheading | parser/recovery | no publication | fail closed |
| two root-sharing writers | complete operation | exactly one success, one journal, sequence 1 | root-exclusive `flock`; loser fails closed |

Journal creation uses `O_EXCL`, full-write verification, file `fsync` and
directory `fsync`; only then may atomic Snapshot replacement occur. Recovery
materializes durable bytes and never reruns authorization or business logic.

## 8. Entry Quote equal-roundtrip and no-reauthorization evidence

| Proof | Exact outcome |
|---|---|
| original Quote coverage | all 22 `EntryEconomicsQuote` fields serialized once plus schema/type/fingerprint |
| Decimal boundary | every Decimal stored as canonical finite string; binary Float and noncanonical spelling reject |
| identity | Economics Profile, Model Version and Config fingerprint exact |
| equal roundtrip | `from_record(to_record(artifact)) == artifact`; `artifact.to_quote() == original_quote` |
| S2 binding | side, quantity, reference/modeled entry prices, notional, fee, risk budget/stop loss and Economics identities match |
| OPEN/FLAT | OPEN exactly one complete Quote; FLAT exactly null |
| CLOSE | deserializes the committed Quote and uses unchanged settlement result; no new quote |
| no reauthorization | CLOSE/recovery never call `authorize_entry()`; journal carries exact Trade/effect and recovery does not redecide |
| exactly once economics | Account and Loss use the same committed Trade V2 net PnL; duplicate Event repeats neither |

## 9. Pure Loss-transition negative-capability matrix

| Capability/input | CLOSE transition | ENTRY_VETO transition |
|---|---|---|
| explicit before-State | required | required |
| explicit canonical UTC | required | required |
| explicit Policy ID/fingerprint | required | required |
| explicit lookback/threshold/pause | required | n/a; uses active pause only |
| Decimal/canonical Decimal-string PnL | accepted | n/a |
| binary Float/nonfinite PnL | rejected | n/a |
| filesystem/store access | none; static function body uses values/helpers only | none |
| environment/global mutable state | none | none |
| clock/time lookup | none; UTC is caller input | none |
| logs/adapter/loop/network | none | none |
| Legacy Store second truth | none; `LossClusterStateStore` unchanged | none |
| input mutation | none; frozen value object returns new State | none |
| revision/effect | +1; append canonical net PnL; apply policy once | +1; decrement active pause exactly once |
| invalid inactive pause | n/a | reject without mutation |
| duplicate committed Event | transition not re-invoked | transition not re-invoked |

## 10. Authority, root and migration evidence

### 10.1 Root/generation/PREPARE ancestry

| Binding | Exact result |
|---|---|
| Authority Generation | derived from source Generation/COMMIT anchor, Manifest, Approval and self-reference-free Target Business |
| Target Core | binds Target Business plus derived Generation |
| Target State | binds Generation and durable PREPARE record fingerprint |
| Transaction continuity | every Tick/Control preserves Generation, PREPARE, Manifest and owner exactly |
| root tamper | wrong Generation/PREPARE/Manifest/component or self-consistent wrong-root journal rejects |
| Ledger circular fields | Ledger Tip and COMMIT fingerprint excluded from State fingerprint |
| owner | migration advances Lifecycle owner epoch exactly once; target State owner remains `PEE` |

### 10.2 Direct and recovered migration outcome matrix

| Case | Ledger records after event | Target | Required next/result |
|---|---:|---:|---|
| direct success | PREPARE→COMMIT (2) | exact V2 | PASS; source bytes unchanged |
| before PREPARE interruption | 0 | absent | no effect; fresh direct attempt allowed |
| after PREPARE interruption | 1 open PREPARE | absent | silent retry reject; exact consumed completion authorization required |
| after Target interruption | 1 open PREPARE | exact present | silent retry reject; explicit reconciliation required |
| after direct COMMIT interruption | 2 committed | exact present | explicit readback returns same COMMIT; no append |
| recovered completion | PREPARE→Consumption→Materialization→COMMIT (4) | exact | provenance `RECOVERED_AFTER_PREPARE`; all bindings exact |
| after completion claim | 3 through Materialization | absent | consumed auth stale; fresh auth/attempt required |
| after recovered Target | 3 through Materialization | exact present | consumed auth stale; fresh auth/attempt required |
| before recovered COMMIT | 3 through Materialization | exact present | consumed auth stale; fresh auth/attempt required |
| fresh completion after claimed crash | old claim + fresh Consumption/Materialization/COMMIT (6 total) | same exact Generation/Target | PASS |
| recovered COMMIT readback repeated three times | remains 4 records | unchanged | same Target/COMMIT identity; no append |
| Consumption before PREPARE | one Consumption only | absent | reject; no PREPARE/Target |
| recovered COMMIT without Materialization | synthetic chain rejected | no accepted readback | `PEE_IU4_AUTHORITY_COMMIT_MISMATCH` |
| tampered/reordered Materialization | synthetic chain rejected | no accepted readback | exact payload and Consumption→Materialization→COMMIT edges required |

### 10.3 Migration negative/source-immutability matrix

| Input condition | Result before COMMIT |
|---|---|
| source V1 byte SHA mismatch | reject before PREPARE |
| source V1 noncanonical/corrupt/missing | reject before PREPARE |
| OPEN V1 source | reject before PREPARE |
| source Loss missing/corrupt/SHA/fingerprint mismatch | reject before PREPARE |
| missing explicit clean Loss Genesis | reject; never inferred |
| wrong source Authority Generation/anchor | reject before PREPARE |
| wrong Manifest/Approval/Profile/Policy identity | reject before PREPARE |
| wrong Target component, Cursor, S4 Business or Core fingerprint | reject before PREPARE |
| non-disjoint/relative/symlink path | reject |
| unknown/missing/tampered migration artifact field | strict parser reject |
| existing Target differs from exact PREPARE-bound State | reject; no COMMIT |
| tampered published Target during reconciliation | reject; PREPARE remains open |
| source byte immutability | source Atomic V1 and Loss bytes compared before/after; exact equality PASS |
| Startup/import/loop auto-migration | absent; migration callable only explicitly offline |

## 11. Exact commands, roots, counts, RCs and skips

Global isolated root created for this Evidence run:

```text
EVIDENCE_TEMP_ROOT:/tmp/iu4-i3-r5-precision.g53M2m
PYCACHE_ROOT:/tmp/iu4-i3-r5-precision.g53M2m/pycache
```

Every Python command set `PYTHONDONTWRITEBYTECODE=1` and
`PYTHONPYCACHEPREFIX=/tmp/iu4-i3-r5-precision.g53M2m/pycache`. Each unittest
command additionally set the exact `TMPDIR` below.

| Exact command target | TMPDIR | Count | RC | failures/errors/skips |
|---|---|---:|---:|---:|
| `.venv/bin/python -m unittest tests.live_l1.test_paper_atomic_coordinator_v2` | `/tmp/iu4-i3-r5-precision.g53M2m/focused` | 44/44 PASS | 0 | 0/0/0 |
| `.venv/bin/python -m unittest tests.live_l1.test_paper_atomic_coordinator` | `/tmp/iu4-i3-r5-precision.g53M2m/v1` | 23/23 PASS | 0 | 0/0/0 |
| `.venv/bin/python -m unittest tests.live_l1.test_loss_cluster_state` | `/tmp/iu4-i3-r5-precision.g53M2m/loss` | 18/18 PASS | 0 | 0/0/0 |
| `.venv/bin/python -m unittest tests.live_l1.test_paper_account` | `/tmp/iu4-i3-r5-precision.g53M2m/account` | 24/24 PASS | 0 | 0/0/0 |
| `.venv/bin/python -m unittest tests.live_l1.test_paper_economics` | `/tmp/iu4-i3-r5-precision.g53M2m/economics` | 20/20 PASS | 0 | 0/0/0 |
| `.venv/bin/python -m unittest tests.live_l1.test_paper_entry_throttle` | `/tmp/iu4-i3-r5-precision.g53M2m/throttle` | 24/24 PASS | 0 | 0/0/0 |
| `.venv/bin/python -m unittest tests.live_l1.test_iu4_lifecycle_ledger` | `/tmp/iu4-i3-r5-precision.g53M2m/ledger` | 5/5 PASS | 0 | 0/0/0 |
| `.venv/bin/python -m unittest tests.live_l1.test_paper_iu4_runtime_gate` | `/tmp/iu4-i3-r5-precision.g53M2m/gate` | 3/3 PASS; fail-closed | 0 | 0/0/0 |
| `.venv/bin/python -m unittest discover -s tests/live_l1 -p 'test_*.py'` | `/tmp/iu4-i3-r5-precision.g53M2m/live_l1` | 419/419 PASS | 0 | 0/0/0 |
| `.venv/bin/python -m unittest discover -s tests/regression -p 'test_*.py'` | `/tmp/iu4-i3-r5-precision.g53M2m/regression` | 170/170 PASS | 0 | 0/0/0 |
| `.venv/bin/python -m py_compile live_l1/state/paper_artifacts.py live_l1/state/loss_cluster.py live_l1/state/paper_atomic_coordinator.py tests/live_l1/test_paper_atomic_coordinator_v2.py` | pycache root above | PASS; 4 isolated `.pyc` | 0 | n/a |

Raw RC output:

```text
RC_FOCUSED:0
RC_V1:0
RC_LOSS:0
RC_ACCOUNT:0
RC_ECONOMICS:0
RC_THROTTLE:0
RC_LEDGER:0
RC_GATE:0
RC_LIVE_L1:0
RC_REGRESSION:0
RC_PY_COMPILE:0
PYC_FILES:4
```

The adjacent six-module baseline is 114/114 PASS; adding the runtime gate is
117/117; all eight required modules including focused I3 are 161/161 PASS.

The originally searched `live_l1/state` plus `tests/live_l1` scope contained
46 pre-existing `.pyc` files; its latest mtime was
`2026-08-19T20:45:56.784098687+0200`, exactly
`2026-08-19T18:45:56.784098687Z`. A separate repository-wide audit excluding
`.venv` found 942 pre-existing `.pyc` files; its latest mtime was
`2026-08-19T19:45:12.486706300Z`. Every timestamp predates this 2026-08-20
workstream. The isolated run created zero repository-local bytecode and left
both foreign sets untouched. The exact four new compile products exist only
below the isolated `/tmp` pycache root.

## 12. Complete I2 freeze and 19-path preservation table

| Frozen item | SHA-256 / mode / result |
|---|---|
| I2 preservation tar | `3af14ff2e270d7d3ca09c1279da7d64e6d720630d06a0c5f45b6786237782037`; mode `0444`; 1,318 entries |
| I2 freeze manifest | `ad154c0eda13470920878873ed170368cc8f4c43591400a07592a77b179d9e16`; mode `0444`; 60 lines |
| I2 freeze directory | mode `0555` |

| Preserved path | Required/final SHA-256 | Lines | Result |
|---|---|---:|---|
| `live_l1/state/iu4_lifecycle_ledger.py` | `d72134195f66b1d39c09a2ca6b9919d8a9acf17c4490ab52d9abc2aebcd71337` | 438 | exact |
| `live_l1/core/paper_iu4_runtime_gate.py` | `447573e484bc13023a118ae61bf7615657293be629c30729748e64f0af7af7c5` | 201 | exact |
| `live_l1/core/paper_iu4_startup_gate.py` | `c4a1854f3b200525568a40205b39e9ce2e14c342bb860569ba7fcfe5e9c063cd` | 919 | exact |
| `live_l1/core/paper_iu4_shadow_runtime_gate.py` | `98d986f3ac2e463b371998604d92b29aa113a507dd0f84bcbd3ff36a52efaf59` | 438 | exact |
| `live_l1/core/paper_iu4_shadow_observation_gate.py` | `ed4e75fad664c68b91950e9c09e873823ebe3eb0b0062f85806daa09ce661350` | 886 | exact |
| `live_l1/core/paper_iu4_adapter.py` | `d65525f31746d1edf30bf1ffc7f84a845f97b3f4120904c9910b741bc8c76a7b` | 641 | exact |
| `live_l1/core/loop.py` | `54e9e7bc0977a9c94f2e85a3279157678249a8569cff63f7d4f29131443fd058` | 1,411 | exact |
| `live_l1/core/execution.py` | `5aed85ce2754dbb4d8984a1d699b607e3a522ed6da000df119ecd782a4e764d8` | 1,147 | exact |
| `live_l1/core/paper_execution_control.py` | `7d3cb901c1c67c8df85e99bc579fda85d8732b634ff4747e08620b92ac1e44f7` | 257 | exact |
| `live_l1/state/state_store.py` | `50a85cf6bd382850d39e69cd785a5dc2ded0a66a1d82856b4baa11877bdba177` | 220 | exact |
| `live_l1/state/models.py` | `3254d2f1a6509ec5f8f623dd8f286f60cfcc108f66f2d8eb107338d795115c7e` | 27 | exact |
| `live_l1/core/paper_economics.py` | `a302013134d1265ac85ad10b57a67ead9e2343043f7eb499fd965a44312525ae` | 730 | exact |
| `live_l1/core/paper_entry_throttle.py` | `ad5447d88a2c35c9a71a5495c61c8f08fa844daf60e79d4a872234e88037df75` | 727 | exact |
| `live_l1/state/paper_entry_throttle.py` | `ce76d8430792d6de1cfdf9a55c09cb6ab501489c7610d2f78345f8d78646295b` | 586 | exact |
| `tests/live_l1/test_paper_atomic_coordinator.py` | `a46f622f9a00e5db727ade04ece89b4deaf51347dc2d1f4d304532572b382753` | 891 | exact; 23/23 PASS |
| `tests/live_l1/test_loss_cluster_state.py` | `0a7823175eb55d39d22d0576e1d58296d4b5123028e0fbfff561c1a6b642fe35` | 413 | exact; 18/18 PASS |
| `tests/live_l1/test_paper_execution_control.py` | `0ae44f2d32f5f3b6affe37a258be0e6aee06790f857e4fc01628c6795bda99e5` | 843 | exact |
| `tests/live_l1/test_iu4_lifecycle_ledger.py` | `f01c2eda7ceec56fad18acec20a09afaa187b4fd4850ab17a974e6bfe8200093` | 50 | exact; 5/5 PASS |
| `tests/live_l1/test_paper_iu4_runtime_gate.py` | `c1137ddcdec7f40ccf463cfc28719d92ea4d766b5be81e6129f6e7bd174f500d` | 24 | exact; 3/3 fail-closed PASS |

## 13. Exact mutation-scope output

The final scope command and its raw output are recorded after serialization in
this stable boolean form; the companion resolution binds this file's whole-file
SHA and line count.

```text
CANONICAL_ROOT:/home/benja/projects/sniper-bot
HEAD:c7ce0452aa2ccbf08c462784d68fa07b3dfe9595
AUTHORIZED_I3_PATH_COUNT:5
PAPER_ARTIFACTS_FINAL_MATCH:YES
LOSS_CLUSTER_FINAL_MATCH:YES
ATOMIC_COORDINATOR_FINAL_MATCH:YES
FOCUSED_TEST_FINAL_MATCH:YES
EVIDENCE_DIFFERS_FROM_REREVIEW5_START:YES
SOURCE_OR_TEST_CHANGE_IN_EVIDENCE_RESOLUTION:NO
UNAUTHORIZED_I3_IMPLEMENTATION_PATH_CHANGE:NO
ACTIVE_V2_CONSUMER_OUTSIDE_COORDINATOR_TEST:NO
I4_OR_ACTIVATION_PATH_CHANGE:NO
GIT_DIFF_CHECK_RC:0
```

The canonical worktree contains unrelated accepted/foreign dirty and untracked
artifacts predating I3. They were neither normalized nor cleaned. Scope is
therefore proven by the mandate-time/final hash table and stable preservation
identities rather than by assuming a clean Git index.

## 14. V1 compatibility, inactive boundary and residual limits

| Requirement | Exact result |
|---|---|
| Atomic V1 import/behavior | unchanged; 23/23 PASS |
| Legacy Loss store/schema | unchanged; 18/18 PASS adjacent suite |
| full Live-L1 | 419/419 PASS |
| regression | 170/170 PASS |
| active imports | no `PaperAtomicCoordinatorV2`, `AtomicPaperStateV2` or Entry-veto Candidate consumer outside inactive coordinator/test |
| Adapter Request V2 | not implemented; I4 remains separate |
| loop/execution seam | not implemented |
| active Recovery/Projection/Handoff | not implemented |
| real migration/Genesis | not executed or authorized |
| ENFORCED start/activation | not authorized |

Residual limits are explicit: I3 is a dormant additive State/Transaction
authority with synthetic offline migration tests. It does not prove an active
consumer, I4 readiness, loop integration, production Recovery/Projection,
Workstation operation or activation. Those remain I4-I8 work.

## 15. Negative operational and Git statement

No real Genesis, migration, handoff, restart, recovery, Runtime Session,
terminal-gap operation, production State, production journal, R3/Workstation,
Research, Exchange, Live, scheduler, network or process mutation occurred.
Every I3 write/fault operation used the exact test-owned `/tmp` roots in
Section 11.

No Git stage, commit, fetch, push, branch mutation, cleanup, deletion or
foreign-artifact modification occurred. No loop, adapter, execution, runtime
gate, Lifecycle Ledger implementation, launcher, State Store, model, native,
tool, I1/I2 freeze or prior governance artifact was changed. The only
repository writes were this authorized Evidence replacement and its companion
precision resolution. The excluded RCC002 bundle script was not read,
executed or modified.

## 16. Completion result and next gate

```text
I3_RESULT:PASS
EVIDENCE_SECTION_14_COMPLETE:YES
I3_REREVIEW_5_EVIDENCE_PRECISION_FINDINGS_RESOLVED_IMPLEMENTATION_SIDE:YES
I3_SELF_CERTIFIED:NO
I3_INDEPENDENT_ACCEPTANCE:PENDING
NEXT_REQUIRED_STEP:IU4-I3-ATOMIC-STATE-TRANSACTION-V2-IMPLEMENTATION-INDEPENDENT-READONLY-FILE-EXACT-REREVIEW-6
I4_AUTHORIZED:NO
ENFORCED_ACTIVATION_AUTHORIZED:NO
```
