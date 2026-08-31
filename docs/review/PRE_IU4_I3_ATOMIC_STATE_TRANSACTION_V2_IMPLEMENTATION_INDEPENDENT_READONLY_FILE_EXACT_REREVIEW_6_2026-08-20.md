# PRE-IU4 I3 Atomic State/Transaction V2 Implementation — Independent Read-only File-exact Rereview 6

Date: 2026-08-20  
Repository: `/home/benja/projects/sniper-bot`  
Workstream: `IU4-I3-ATOMIC-STATE-TRANSACTION-V2-IMPLEMENTATION-INDEPENDENT-READONLY-FILE-EXACT-REREVIEW-6`

```text
REREVIEW_RESULT:READY
I3_INDEPENDENT_ACCEPTANCE:READY
I3_RESULT_ACCEPTED:YES
BLOCKER:0
HIGH:0
MEDIUM:0
LOW:0
I4_AUTHORIZED:NO
ENFORCED_ACTIVATION_AUTHORIZED:NO
```

## 1. Independence and read-only boundary

The reviewer did not implement the I3 candidate or either Evidence resolution.
Source, tests, Evidence, prior governance, Revision-21 authority and the I2
freeze were reviewed read-only. Submitted completion claims were not accepted
as proof. Independent commands and adversarial checks used synthetic isolated
roots below `/tmp` and `PYTHONDONTWRITEBYTECODE=1`.

No reviewed candidate, Evidence, resolution, Git state, freeze or foreign
artifact was changed during review. This record is the sole post-verdict
governance write. The excluded
`scripts/build_rcc002_spec_bundle.py` was not read, executed or modified.

## 2. Recomputed controlling identities

| Item | Independent identity/result |
|---|---|
| Repository / HEAD / `main` | `/home/benja/projects/sniper-bot`; `c7ce0452aa2ccbf08c462784d68fa07b3dfe9595` |
| `origin/main`; divergence | `89e13fecd1ab549ca7099818b1c9ad4984cb6f7a`; ahead 6, behind 0 |
| Revision-21 specification | `ab8f80720a1d8fe49b9085bce63658bcaecf7f0a3ea70fb555559223090824e0`, 4,605 lines |
| Binding I2 rereview | `5a59ad8c97ebae85148661fe0e3bedab643c7f12ae2c8d4e87272447c0616679`, 300 lines, `READY`, 97/97 |
| I3 file-exact mandate | `775aeb62e6ff0a1ca3af970970053b43d176f1122560774f184ecf40a8fcced5`, 558 lines, `READY` |
| Independent I3 rereview 5 | `8222228de88b9a63d570852ba3eaa32cb86244b24fc53ea0c013fb87ffbcf65e`, 224 lines, `NOT_READY`, findings 1/0/0/1 |
| Corrected implementation Evidence | `20846284ffad9e8b755dd6a3b74f963d8d2c6ee1519fafdd0bc1275f2e33c390`, 463 lines, implementation-side `PASS` |
| Rereview-5 Evidence-precision resolution | `00fb12135197a5fa8aefa8bf149c03904b9440d7909eb5a218cde5cfa38f7b5d`, 156 lines, implementation-side complete |

All Section-2 prerequisite identities serialized in the corrected Evidence
were independently recomputed and match the mandate.

## 3. Exact five-path candidate

| Authorized path | SHA-256 | Lines | Result |
|---|---|---:|---|
| `live_l1/state/paper_artifacts.py` | `3cd9a459e2856672bb7b318c9cdbf8f8bb52e633ee9529d74761d64928213946` | 1,575 | exact |
| `live_l1/state/loss_cluster.py` | `4ce7d59f64a67de94ffc6f1d03ff4e6c8a7a590802abb003b311cd0d56cc3e55` | 521 | exact |
| `live_l1/state/paper_atomic_coordinator.py` | `d0721ae5def3551ba7281ea0e367f5347890fd4cd7187d8f2aebb98d2651e84f` | 5,489 | exact |
| `tests/live_l1/test_paper_atomic_coordinator_v2.py` | `16d0fea6e5588cc14329ba61cfeeccb1f72478d14c358f8ed4e38c1ac3a41bb9` | 2,482 | exact |
| I3 implementation Evidence | `20846284ffad9e8b755dd6a3b74f963d8d2c6ee1519fafdd0bc1275f2e33c390` | 463 | exact |

The three mandate-time MODIFY hashes and both mandate-bound CREATE-ABSENT
proofs are exact. Source and focused test are unchanged from rereviews 4 and 5.
No additional I3 implementation path exists.

## 4. Rereview-5 finding closure

### 4.1 I3-RR5-B1 — exact regression skip value

Corrected Evidence lines 315-326 define the final column as
`failures/errors/skips` and contain in the authorized Evidence path itself:

```text
170/170 PASS | RC 0 | 0/0/0
```

The independent regression run reproduced 170/170 PASS, return code 0, zero
failures, zero errors and zero skips. The current Evidence SHA and line count
are exactly bound by the Rereview-5 precision resolution at its lines 45 and
63. Finding `I3-RR5-B1` is closed.

### 4.2 I3-RR5-L1 — bytecode search scope and UTC precision

Corrected Evidence lines 349-357 distinguish both searches exactly:

| Search scope | Count | Latest local value | Exact UTC value |
|---|---:|---|---|
| `live_l1/state` plus `tests/live_l1` | 46 | `2026-08-19T20:45:56.784098687+0200` | `2026-08-19T18:45:56.784098687Z` |
| repository-wide excluding `.venv` | 942 | `2026-08-19T21:45:12.486706300+0200` | `2026-08-19T19:45:12.486706300Z` |

Independent `find` and UTC conversion reproduced both counts and timestamps
exactly. Counts remained 46 and 942 after all review commands. The exact four
compile products existed only below the independent `/tmp` compile root.
Finding `I3-RR5-L1` is closed.

## 5. Section-14 and technical proportional rereview

The corrected 463-line Evidence contains every mandate Section-14 item:

- all controlling identities and prerequisite results;
- mandate-time and final identities for all five paths plus CREATE absence;
- exact commands, counts, return codes, skips and temporary roots;
- complete schema, canonical-input, cross-State and effect allowlist matrices;
- Tick, Control and Lifecycle ordering plus risk/capability escalation;
- all five effects across all four durability boundaries and resource faults;
- Entry Quote equal-roundtrip and no-reauthorization evidence;
- pure Loss-transition negative capabilities;
- Authority root, Generation and PREPARE ancestry;
- direct/recovered migration faults and source immutability;
- V1 compatibility, full Live-L1, regression and compile results;
- freeze modes/hashes and every Section-5 preservation identity;
- exact mutation-scope output and operational/Git negatives; and
- residual limits and exact implementation-side result.

The unchanged source/test hashes and the focused suite proportionally re-cover
the earlier causal OPEN/CLOSE, strict ENTRY_VETO, completion-chain/freshness,
Decimal/Float, single-writer/fork, recovery and migration-tamper findings. No
new technical defect or Evidence inconsistency was found.

## 6. Independent verification results

Every Python command used `PYTHONDONTWRITEBYTECODE=1`, a dedicated `TMPDIR`
and an isolated Python cache. All return codes were 0; no failure, error or
skip occurred.

| Target | Result | Independent temporary root |
|---|---:|---|
| focused Atomic V2 | 44/44 PASS | `/tmp/iu4-i3-r6-focused.8TIZU3` |
| Atomic V1 | 23/23 PASS | `/tmp/iu4-i3-r6-v1.y0o2ST` |
| Loss Cluster | 18/18 PASS | `/tmp/iu4-i3-r6-loss.2UaQ83` |
| Paper Account | 24/24 PASS | `/tmp/iu4-i3-r6-account.ZJE685` |
| Paper Economics | 20/20 PASS | `/tmp/iu4-i3-r6-economics.LVrxQh` |
| Entry Throttle | 24/24 PASS | `/tmp/iu4-i3-r6-throttle.53wg4b` |
| I2 Lifecycle Ledger | 5/5 PASS | `/tmp/iu4-i3-r6-ledger.PcXLXr` |
| fail-closed Runtime Gate | 3/3 PASS | `/tmp/iu4-i3-r6-gate.xn6YYs` |
| combined eight required modules | 161/161 PASS | `/tmp/iu4-i3-r6-eight.K4vXkp` |
| complete `tests/live_l1` | 419/419 PASS | `/tmp/iu4-i3-r6-live.ofmyZg` |
| complete `tests/regression` | 170/170 PASS | `/tmp/iu4-i3-r6-reg.R9gnPM` |
| exact four-path `py_compile` | PASS; exactly four `.pyc` | `/tmp/iu4-i3-r6-compile.Bda2O3/pycache` |
| `git diff --check` | PASS; RC 0 | canonical repository |

## 7. I2 freeze and preservation

| Frozen item | Independent result |
|---|---|
| I2 preservation tar | `3af14ff2e270d7d3ca09c1279da7d64e6d720630d06a0c5f45b6786237782037`; mode `0444`; 1,318 entries |
| I2 freeze manifest | `ad154c0eda13470920878873ed170368cc8f4c43591400a07592a77b179d9e16`; mode `0444`; 60 lines |
| I2 freeze directory | mode `0555` |

All 19 mandate Section-5 identities were independently recomputed:

| Preserved path | SHA-256 | Lines |
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

## 8. Inactive boundary and authorization decision

Search outside the coordinator and focused test finds only the expected
`PaperRiskStateS4V2` definition/export in `paper_artifacts.py`. There is no
active V2 consumer and no Adapter, loop, execution, I4 or activation handoff.

```text
REREVIEW_RESULT:READY
I3_INDEPENDENT_ACCEPTANCE:READY
I3_RESULT_ACCEPTED:YES
BLOCKER_OPEN:0
HIGH_OPEN:0
MEDIUM_OPEN:0
LOW_OPEN:0
I4_AUTHORIZED:NO
ENFORCED_ACTIVATION_AUTHORIZED:NO
```

I3 is independently accepted at the exact five-path identities in Section 3.
The only permissible next governance step is a separate I4 File-Exact Mandate.
This READY result does not itself authorize I4 implementation, an active V2
consumer, ENFORCED entry or activation.
