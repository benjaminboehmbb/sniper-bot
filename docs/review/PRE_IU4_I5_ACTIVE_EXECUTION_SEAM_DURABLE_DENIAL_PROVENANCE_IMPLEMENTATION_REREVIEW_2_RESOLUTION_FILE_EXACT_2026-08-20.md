# Pre-IU4 I5 Active Execution Seam Durable Denial Provenance — Implementation Rereview 2 Resolution — File-Exact — 2026-08-20

## 1. Resolution decision

```text
WORKSTREAM:IU4-I5-ACTIVE-EXECUTION-SEAM-DURABLE-DENIAL-PROVENANCE-IMPLEMENTATION-REREVIEW-2-RESOLUTION-FILE-EXACT
RESOLUTION_RESULT:READY_FOR_INDEPENDENT_REREVIEW_3
REREVIEW_2_BLOCKER_CLOSED:2/2
BLOCKER_OPEN:0
HIGH_OPEN:0
MEDIUM_OPEN:0
LOW_OPEN:0
I5_RESULT:PASS_IMPLEMENTATION_SIDE
I5_INDEPENDENT_ACCEPTANCE:PENDING
OPERATIONAL_ENFORCED_START_AUTHORIZED:NO
ACTIVE_V2_CONSUMER_AUTHORIZED:NO
I6_THROUGH_I8_AUTHORIZED:NO
ENFORCED_ACTIVATION_AUTHORIZED:NO
EXCHANGE_AUTHORIZED:NO
LIVE_AUTHORIZED:NO
```

This Resolution closes only the two focused-test/Evidence blockers from the
second independent durable-denial-provenance implementation rereview. It does
not alter either production source. It does not accept I5 independently and
does not authorize an operational consumer, ENFORCED start, activation, I6-I8,
Exchange or Live behavior.

`AGENTS.md` was read completely before correction. Work occurred only in the
canonical repository `/home/benja/projects/sniper-bot`. No Git mutation,
cleanup or foreign-artifact mutation was performed. The excluded
specification-bundle script was not read, executed or changed.

## 2. Controlling authority and repository identity

```text
CANONICAL_REPOSITORY:/home/benja/projects/sniper-bot
BRANCH:main
HEAD:c7ce0452aa2ccbf08c462784d68fa07b3dfe9595
MAIN:c7ce0452aa2ccbf08c462784d68fa07b3dfe9595
ORIGIN_MAIN:89e13fecd1ab549ca7099818b1c9ad4984cb6f7a
MAIN_AHEAD_OF_ORIGIN:6
MAIN_BEHIND_ORIGIN:0
```

| Authority | SHA-256 | Lines | Result |
|---|---|---:|---|
| Revision-21 specification | `ab8f80720a1d8fe49b9085bce63658bcaecf7f0a3ea70fb555559223090824e0` | 4,605 | controlling |
| final I2 independent rereview | `5a59ad8c97ebae85148661fe0e3bedab643c7f12ae2c8d4e87272447c0616679` | 300 | READY, 97/97 |
| corrected durable-provenance mandate revision 4 | `a688773cc10dd6c573e7c019245639c010a3b0abb49fb301249aeebeba182a91` | 633 | controlling scope |
| mandate independent rereview 2 | `934bf4a9010aff61796cc2c7c09f54380c5527546bea6e4bc25b5a17933bfd59` | 242 | READY, 0/0/0/0 |
| first implementation rereview | `88fe9751f16fa0f396ba4f6d63db6aa5ad578020dd8a46ba03d3b7912606c245` | 352 | NOT_READY, 2/0/0/0 |
| first implementation Resolution | `13666d2b9a3efbee1813d4f4cf6e480a5021f0b013f8c55d20bd87e9602f5e03` | 226 | partial closure |
| implementation independent rereview 2 | `ce32b2ac3add765a9794823123063e06b56f9aba31738781cd5e880f9d92561f` | 282 | NOT_READY, 2/0/0/0 |

## 3. Exact five-path candidate after correction

| Operation | Path | Rereview-2 start identity | Corrected final identity |
|---|---|---|---|
| PRESERVE | `live_l1/state/paper_atomic_coordinator.py` | `446ae8712d09bc52f950587a2e3ecec0c60fd21b3c9150a8886af1b3b2b4f9ec`, 5,796 | same exact bytes |
| PRESERVE | `live_l1/core/paper_iu4_adapter.py` | `1fac2629a0ebdd889825f496e9273c358ffe7596c2173d307ce1d1eb7e9bd6a6`, 1,896 | same exact bytes |
| MODIFY | `tests/live_l1/test_paper_atomic_coordinator_v2.py` | `3385a35581346cc7dfd2ade68714304a03cd7ece5bba604f4785b2651594b622`, 3,468 | `ec731c106ab23b78e482204e16d20826264cdf775f0c08c292a82bab1111ff8c`, 3,734 |
| MODIFY | `tests/live_l1/test_paper_iu4_execution_seam_v2.py` | `af81c777ade0c387d6303c8df0a6a6f21f5f9099623a08c06b6836ed3404e462`, 2,399 | `fc61404d910fe76141cba8ba54f98ea6de552664a8b21bdaa50510e33f603755`, 2,517 |
| REPLACE | `docs/review/PRE_IU4_I5_ACTIVE_EXECUTION_SEAM_IMPLEMENTATION_EVIDENCE_2026-08-20.md` | `8c315972b977b0e494d178deaf672c2e08903f5bfa1d5d5909a5f80055914341`, 623 | `33d18b64bc92d0f5631d3a8306010e8889bb69085d7ce4e77c36c1fd1e185b65`, 633 |

The mandate-time identities remain recorded in the corrected Evidence. This
Resolution binds the Evidence byte identity non-self-referentially. No sixth
implementation path was used. This governance Resolution is separate from the
five-path implementation candidate.

## 4. Closure of I5-DP-IR2-B1

### 4.1 Discriminating Effect/provenance negatives

The Atomic focused test now creates fully valid OPEN, CLOSE, ENTRY_VETO and KILL
transactions through their public commit APIs. For each Effect it then:

1. reconstructs the full transaction from the exact before-State and complete
   effect-specific positive payload;
2. requires the reconstructed record to equal the already validated committed
   record exactly;
3. repeats the build with only one additional valid
   `effect_entry_denial_provenance` argument; and
4. requires `PEE_ATOMIC_TRANSACTION_INVALID` with the persisted State and
   journal unchanged.

| Effect | Positive transaction fingerprint | Positive journal head | Provenance-only delta |
|---|---|---|---|
| OPEN | `7495ff0a4b9e81c5a3da3e7995af41bcf5e46fd317d142599a7f9b0dde83fc55` | `fc03c8ee8d1d6e68b7e5fc15454d0b03f400f75369bbf0e48b9bd784f44c33e2` | rejected, no mutation |
| CLOSE | `047868fa52421e6a7b579436b4aad0fa43727f6b8c85e1a95e79b18955dc3528` | `c89412f9b423499f0ed1694436026c67a51ff4a41d9d0e898f36c2c102410539` | rejected, no mutation |
| ENTRY_VETO | `688061fed90e5b1aadb0899839650d3b5f2aa60404040435cb879961a4898b08` | `a102c9ec600b7273082efbdc8d0cf8e99373a348844096e12539326b6097e69f` | rejected, no mutation |
| KILL | `817c809ee84abd69d5430b065da3511324234ef7ab7c19e7c8cf4c31caee33db` | `e078806fdc80f5a5ef050482e7de38d5c8adca8049978aae0ec95125d57c8bca` | rejected, no mutation |

The PROGRESS control first validates a complete provenance-bearing transaction
(`cbe4d12e...e888dc4` / head `65685878...e508f7`) and then adds only a valid
matching Accepted Entry Event. That sole delta rejects with
`PEE_ATOMIC_TRANSACTION_INVALID`, zero journal and unchanged Snapshot.

### 4.2 Row-complete seven-point fault matrix

The `BEFORE_JOURNAL` branch no longer exits early. It proves zero journal,
sequence zero, `EMPTY` head and initial Cursor immediately after the injected
interruption, then performs a controlled first commit and identical durable
replay. `AFTER_JOURNAL`, `BEFORE_SNAPSHOT` and `AFTER_SNAPSHOT` each prove the
immediate Snapshot/journal boundary, exact recovery/readback and replay.

Every Atomic row now asserts:

- exact interruption text and immediate journal/Snapshot result;
- final sequence/head and exact Cursor fingerprint;
- exact provenance record and fingerprint;
- transaction fingerprint and journal head;
- Position, Account, Throttle, Loss and Risk-business fingerprints;
- `already_committed=true`, `newly_committed=false`, one final journal; and
- per-row `_risk_after` and `_validate_open_guards` sentinel counts `0/0`.

The Seam test completes rows one, two and seven. Row one proves five zero-call
business sentinels before accepted validation. Row two records the one initial
provenance construction and zero Economics/Atomic-guard/Risk calls before the
Coordinator. Row seven records all durable identities and six zero-call replay
sentinels. Corrected Evidence Section 15.5 serializes every exact row value.

## 5. Closure of I5-DP-IR2-B2

The replaced Evidence now:

- claims Effect rejection only from the positive-control/one-field-delta tests;
- contains the complete seven-row result, journal, Snapshot, Cursor,
  provenance, transaction, component, replay and sentinel matrices;
- removes the obsolete 51/43 and 258/487 tables from final status and names the
  current 54/44, 262/491 runs as the only final results;
- contains the exact individual, combined, broad and compile roots, RCs,
  counts and `0/0/0` failure/error/skip values; and
- advances only to independent read-only file-exact rereview 3.

The Evidence PASS is an implementation-side claim only. Independent acceptance
remains pending.

## 6. Fresh final verification

Every Python command used `PYTHONDONTWRITEBYTECODE=1`, a unique temporary
`TMPDIR` and an external `PYTHONPYCACHEPREFIX`. Every run returned RC 0 with
failures/errors/skips `0/0/0`.

| Module | Root | Result |
|---|---|---:|
| Atomic V2 | `/tmp/iu4-i5-dp-r2res-test_paper_atomic_coordinator_v2.Bbxkvp` | 54/54 PASS |
| I5 Seam | `/tmp/iu4-i5-dp-r2res-test_paper_iu4_execution_seam_v2.uJPDFr` | 44/44 PASS |
| Adapter V2 | `/tmp/iu4-i5-dp-r2res-test_paper_iu4_adapter_v2.0fA1cm` | 18/18 PASS |
| Adapter V1 | `/tmp/iu4-i5-dp-r2res-test_paper_iu4_adapter.sYSj5d` | 13/13 PASS |
| Pure Control | `/tmp/iu4-i5-dp-r2res-test_paper_execution_control.BCRmWG` | 25/25 PASS |
| Atomic V1 | `/tmp/iu4-i5-dp-r2res-test_paper_atomic_coordinator.OVPE6x` | 23/23 PASS |
| Startup | `/tmp/iu4-i5-dp-r2res-test_paper_iu4_startup_gate.lTfMsi` | 12/12 PASS |
| Runtime | `/tmp/iu4-i5-dp-r2res-test_paper_iu4_runtime_gate.a3W1QK` | 3/3 PASS |
| Shadow Harness | `/tmp/iu4-i5-dp-r2res-test_paper_iu4_shadow_harness.87lx3g` | 18/18 PASS |
| Shadow Observation | `/tmp/iu4-i5-dp-r2res-test_paper_iu4_shadow_observation_gate.dpv5Yk` | 18/18 PASS |
| Replay Evidence | `/tmp/iu4-i5-dp-r2res-test_paper_iu4_replay_evidence.JAdtcK` | 10/10 PASS |
| Replay Pipeline | `/tmp/iu4-i5-dp-r2res-test_paper_iu4_replay_pipeline.cCtB1e` | 6/6 PASS |
| Economics Shadow | `/tmp/iu4-i5-dp-r2res-test_paper_economics_shadow_runtime.7htbF0` | 9/9 PASS |
| Safe Launch | `/tmp/iu4-i5-dp-r2res-test_safe_launch_iu4_shadow_runtime_gate.aN3u2P` | 3/3 PASS |
| Guards | `/tmp/iu4-i5-dp-r2res-test_pre_execution_guards.iXsazk` | 6/6 PASS |
| combined exact 15-module order | `/tmp/iu4-i5-dp-r2res-combined.LNeNz6` | 262/262 PASS |
| full `tests/live_l1` | `/tmp/iu4-i5-dp-r2res-live.Z8Ivy8` | 491/491 PASS |
| full `tests/regression` | `/tmp/iu4-i5-dp-r2res-regression.72dvBO` | 170/170 PASS |
| exact four-path compile | `/tmp/iu4-i5-dp-r2res-compile.b66yjb` | PASS, exactly 4 `.pyc` |
| both Git diff checks | canonical repository | PASS |

The exact commands are serialized in corrected Evidence Section 12. No test
wrote repository State, journal, Snapshot, log, Evidence or bytecode.

## 7. Preservation and Freeze

All 25 mandate Preservation identities and counts were recomputed after the
final gates and remain exact.

```text
LOOP:e4db22642b628fe4b84cf0d2daa9ecd846208138eaa3868a02a56ddf9f75ee6c/1947
EXECUTION:85a9acb238dafd3adf5fd8bf57153772d3c7b41559943bdcce5336e3b60dcb5e/1386
FREEZE_DIRECTORY_MODE:0555
PRESERVATION_TAR:3af14ff2e270d7d3ca09c1279da7d64e6d720630d06a0c5f45b6786237782037/0444/1318
FREEZE_MANIFEST:ad154c0eda13470920878873ed170368cc8f4c43591400a07592a77b179d9e16/0444/60
```

Remaining exact SHA/count pairs:

```text
paper_artifacts:3cd9a459e2856672bb7b318c9cdbf8f8bb52e633ee9529d74761d64928213946/1575
loss_cluster:4ce7d59f64a67de94ffc6f1d03ff4e6c8a7a590802abb003b311cd0d56cc3e55/521
adapter_v2_test:f71d46700a1966534429281091da32e263ac479ddf1393c5021d015eac1cd1b3/1274
I3_Evidence:20846284ffad9e8b755dd6a3b74f963d8d2c6ee1519fafdd0bc1275f2e33c390/463
I4_Evidence:068c2ba2661031843a13dd3f2c4684f9340f432b90b192b6b7492dae8968270d/403
control:7d3cb901c1c67c8df85e99bc579fda85d8732b634ff4747e08620b92ac1e44f7/257
runtime:447573e484bc13023a118ae61bf7615657293be629c30729748e64f0af7af7c5/201
startup:c4a1854f3b200525568a40205b39e9ce2e14c342bb860569ba7fcfe5e9c063cd/919
shadow_runtime:98d986f3ac2e463b371998604d92b29aa113a507dd0f84bcbd3ff36a52efaf59/438
observation:ed4e75fad664c68b91950e9c09e873823ebe3eb0b0062f85806daa09ce661350/886
harness:ddfb60f19a3b765a476c8de0464d583590313cdd0583391044cb338fec969f77/1007
ledger:d72134195f66b1d39c09a2ca6b9919d8a9acf17c4490ab52d9abc2aebcd71337/438
state_store:50a85cf6bd382850d39e69cd785a5dc2ded0a66a1d82856b4baa11877bdba177/220
models:3254d2f1a6509ec5f8f623dd8f286f60cfcc108f66f2d8eb107338d795115c7e/27
economics:a302013134d1265ac85ad10b57a67ead9e2343043f7eb499fd965a44312525ae/730
core_throttle:ad5447d88a2c35c9a71a5495c61c8f08fa844daf60e79d4a872234e88037df75/727
state_throttle:ce76d8430792d6de1cfdf9a55c09cb6ab501489c7610d2f78345f8d78646295b/586
safe_launch:cb90bd49b36de56e8ad95e9b24febb23baa0513b1ec51e7402f63a5efd6ec652/201
adapter_v1_test:b4947e4c03fa3b187e01c4005062337d1837b70d652243030581172dd4d2c339/441
control_test:0ae44f2d32f5f3b6affe37a258be0e6aee06790f857e4fc01628c6795bda99e5/843
atomic_v1_test:a46f622f9a00e5db727ade04ece89b4deaf51347dc2d1f4d304532572b382753/891
```

## 8. Scope and non-activation

- exactly the existing five candidate paths remain the implementation scope;
- only the two authorized focused tests and the authorized Evidence changed in
  this narrow Resolution;
- Coordinator and Adapter production bytes are unchanged from rereview 2;
- Loop, Execution, gates, accepted I4 Request, State/S4/Cursor/Loss schemas,
  launcher, Ledger, profiles and Freeze remain unchanged;
- no sidecar, second journal, fixture, module or operational consumer exists;
- active Loop owner remains literal `LEGACY` and the private ENFORCED seam
  remains test-only; and
- no productive V2 Coordinator/Adapter construction, Exchange, Live, I6-I8 or
  activation was added.

## 9. Exact next step

```text
I5_RESULT:PASS_IMPLEMENTATION_SIDE
I5_INDEPENDENT_ACCEPTANCE:PENDING
OPERATIONAL_ENFORCED_START_AUTHORIZED:NO
ACTIVE_V2_CONSUMER_AUTHORIZED:NO
I6_THROUGH_I8_AUTHORIZED:NO
ENFORCED_ACTIVATION_AUTHORIZED:NO
NEXT_REQUIRED_STEP:IU4-I5-ACTIVE-EXECUTION-SEAM-DURABLE-DENIAL-PROVENANCE-IMPLEMENTATION-INDEPENDENT-READONLY-FILE-EXACT-REREVIEW-3
```

Only the independent read-only file-exact rereview 3 above may follow. This
Resolution is not independent acceptance and cannot authorize activation.
