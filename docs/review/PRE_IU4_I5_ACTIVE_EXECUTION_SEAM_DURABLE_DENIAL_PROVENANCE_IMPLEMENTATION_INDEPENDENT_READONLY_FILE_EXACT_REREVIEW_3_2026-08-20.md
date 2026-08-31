# Pre-IU4 I5 Active Execution Seam Durable Denial Provenance — Implementation Independent Read-only File-exact Rereview 3 — 2026-08-20

## 1. Decision

```text
WORKSTREAM:IU4-I5-ACTIVE-EXECUTION-SEAM-DURABLE-DENIAL-PROVENANCE-IMPLEMENTATION-INDEPENDENT-READONLY-FILE-EXACT-REREVIEW-3
FINAL_VERDICT:READY
BLOCKER:0
HIGH:0
MEDIUM:0
LOW:0
I5_INDEPENDENT_ACCEPTANCE:READY
OPERATIONAL_ENFORCED_START_AUTHORIZED:NO
ACTIVE_V2_CONSUMER_AUTHORIZED:NO
I6_THROUGH_I8_AUTHORIZED:NO
ENFORCED_ACTIVATION_AUTHORIZED:NO
EXCHANGE_AUTHORIZED:NO
LIVE_AUTHORIZED:NO
```

The rereview was performed strictly independently and read-only in the
canonical repository `/home/benja/projects/sniper-bot`. `AGENTS.md` was read
completely first. No candidate, Git, cleanup or foreign-artifact mutation was
made. The excluded specification-bundle script was not read, executed or
changed.

## 2. Repository and authority identities

```text
BRANCH:main
HEAD:c7ce0452aa2ccbf08c462784d68fa07b3dfe9595
MAIN:c7ce0452aa2ccbf08c462784d68fa07b3dfe9595
ORIGIN_MAIN:89e13fecd1ab549ca7099818b1c9ad4984cb6f7a
MAIN_AHEAD_OF_ORIGIN:6
MAIN_BEHIND_ORIGIN:0
```

| Authority | SHA-256 | Lines | Result |
|---|---|---:|---|
| corrected durable-provenance mandate revision 4 | `a688773cc10dd6c573e7c019245639c010a3b0abb49fb301249aeebeba182a91` | 633 | controlling |
| mandate independent rereview 2 | `934bf4a9010aff61796cc2c7c09f54380c5527546bea6e4bc25b5a17933bfd59` | 242 | READY, 0/0/0/0 |
| implementation independent rereview 2 | `ce32b2ac3add765a9794823123063e06b56f9aba31738781cd5e880f9d92561f` | 282 | NOT_READY, 2/0/0/0 |
| implementation rereview-2 Resolution | `4512288b16541f659b434000114853f05e457acf5df4e3e779c14b03d44b2985` | 237 | submitted closure |

All identities are exact.

## 3. Exact five-path candidate

| Path | SHA-256 | Lines |
|---|---|---:|
| `live_l1/state/paper_atomic_coordinator.py` | `446ae8712d09bc52f950587a2e3ecec0c60fd21b3c9150a8886af1b3b2b4f9ec` | 5,796 |
| `live_l1/core/paper_iu4_adapter.py` | `1fac2629a0ebdd889825f496e9273c358ffe7596c2173d307ce1d1eb7e9bd6a6` | 1,896 |
| `tests/live_l1/test_paper_atomic_coordinator_v2.py` | `ec731c106ab23b78e482204e16d20826264cdf775f0c08c292a82bab1111ff8c` | 3,734 |
| `tests/live_l1/test_paper_iu4_execution_seam_v2.py` | `fc61404d910fe76141cba8ba54f98ea6de552664a8b21bdaa50510e33f603755` | 2,517 |
| `docs/review/PRE_IU4_I5_ACTIVE_EXECUTION_SEAM_IMPLEMENTATION_EVIDENCE_2026-08-20.md` | `33d18b64bc92d0f5631d3a8306010e8889bb69085d7ce4e77c36c1fd1e185b65` | 633 |

There are exactly five candidate paths. Both production-source identities are
unchanged from rereview 2. The Evidence identity is bound exactly by the
rereview-2 Resolution.

## 4. Independent closure of rereview-2 findings

### 4.1 RR2-B1 closed — discriminating Effect controls

Atomic focused test lines 3075-3273 derive complete arguments from already
publicly committed and valid OPEN, CLOSE, ENTRY_VETO and KILL transactions. For
each row, rebuilding without provenance is record-identical to the positive
transaction. Adding only one valid provenance object then rejects as
`PEE_ATOMIC_TRANSACTION_INVALID`, leaving the persisted journal and State
unchanged. PROGRESS first builds a valid provenance-bearing transaction and
then adds only an Accepted Entry Event, which also rejects.

Independent focused root `/tmp/iu4-i5-dp-rr3-effect.CtpW4f` passed 1/1. The
independent traced-identity root
`/tmp/iu4-i5-dp-rr3-effect-identities.Afnn3A` returned RC 0 and reproduced:

```text
OPEN_TRANSACTION_FP:7495ff0a4b9e81c5a3da3e7995af41bcf5e46fd317d142599a7f9b0dde83fc55
OPEN_JOURNAL_HEAD:fc03c8ee8d1d6e68b7e5fc15454d0b03f400f75369bbf0e48b9bd784f44c33e2
CLOSE_TRANSACTION_FP:047868fa52421e6a7b579436b4aad0fa43727f6b8c85e1a95e79b18955dc3528
CLOSE_JOURNAL_HEAD:c89412f9b423499f0ed1694436026c67a51ff4a41d9d0e898f36c2c102410539
ENTRY_VETO_TRANSACTION_FP:688061fed90e5b1aadb0899839650d3b5f2aa60404040435cb879961a4898b08
ENTRY_VETO_JOURNAL_HEAD:a102c9ec600b7273082efbdc8d0cf8e99373a348844096e12539326b6097e69f
KILL_TRANSACTION_FP:817c809ee84abd69d5430b065da3511324234ef7ab7c19e7c8cf4c31caee33db
KILL_JOURNAL_HEAD:e078806fdc80f5a5ef050482e7de38d5c8adca8049978aae0ec95125d57c8bca
PROGRESS_TRANSACTION_FP:cbe4d12e54fabcda14ea20842d770af97c090e93e1aeda0d68b2e1cb3e888dc4
PROGRESS_JOURNAL_HEAD:656858783d34558030a17d429ff528d9fb79225609ef7d98f24aaafa0ce508f7
```

These identities match the corrected Evidence exactly.

### 4.2 RR2-B1 closed — seven row-complete boundaries

Atomic focused test lines 3391-3556 contain no early `continue`.
`BEFORE_JOURNAL` proves the immediate zero-journal, sequence-zero, initial-head
and initial-Cursor boundary, then performs one controlled commit and an
identical replay. `AFTER_JOURNAL`, `BEFORE_SNAPSHOT` and `AFTER_SNAPSHOT` prove
the immediate boundary, recovery/readback, exact transaction, provenance,
Cursor, head and business identities, one journal, replay flags and per-row
Risk/guard sentinel counts `0/0`.

Seam focused test lines 2100-2357 complete the pre-validation,
post-validation/pre-Coordinator and public durable-readback rows with the exact
boundary and sentinel assertions.

Focused roots:

```text
ATOMIC_FAULT_ROOT:/tmp/iu4-i5-dp-rr3-fault.ov5zum
ATOMIC_FAULT_RESULT:1/1_PASS
SEAM_ROWS_ROOT:/tmp/iu4-i5-dp-rr3-seamrows.gDz9ga
SEAM_ROWS_RESULT:1/1_PASS
```

Independent traced root `/tmp/iu4-i5-dp-rr3-fault-identities2.Yo99d1`
returned RC 0 and reproduced:

| Boundary | Provenance fingerprint | Transaction fingerprint | Journal head | Cursor fingerprint | Risk/guard sentinels |
|---|---|---|---|---|---:|
| BEFORE_JOURNAL | `9d7ea242be30db70e12bacfb9642276a0b5f1ef9928039e5265b569f1d59bcf3` | `66f466e92b0ea32ec5e442420dccb74a8ecf458c824d29578ff627754fc80444` | `6c3cbec98d88f9d2c645b64b52c0e85b938f9b5b6ca0ce009f621ddaba47479e` | `c1acbb91d46e81bce7b644568ed4b7302c040ff78fa19f28cacd263a21150d6c` | 0/0 |
| AFTER_JOURNAL | `971d951f999f7d4f9f8b13e6934ccbe56c7d45bd9918a8f2d5adda7c81dd7a2a` | `de36dd50ea8f8841c05939d3e99e7391fe3f081b819323f404bb778bdbb206dc` | `c62a803e585c252838eed750b8fe374f6cc034a011ba88f6885747823f7911d8` | `9d50c568faf041f365a7ab3927af68aa0c60eff74021278790a2e05d212be039` | 0/0 |
| BEFORE_SNAPSHOT | `8edac178864ec6cb0119c986794f9dce144e8dc3af3a7ddb910cc034e8ec68c8` | `486e2d2e4cff43c5718349b154c024f5b1ca48553921c5c7c0f29702884bc497` | `edd3911174381d6f67fa282c0af9fd45483343cc36443b9dc9b1bf0d860665b6` | `9741e87d2ffd0151eb17146be4b8ad86e9e27bc429c185d56d49d4be3eb8f54c` | 0/0 |
| AFTER_SNAPSHOT | `0ee5589f20008949fd8d789dd9b24ec8eaf693717d05881a659eaf2d7a658a43` | `065b3d737556d45acad18661b5cf6cf3a5ad1ae17c948d153694a98e7f45e324` | `527b2e0fe266a2dafc5bbf150e8fb031c0e00875ee6e5bae6df07a3a6db1b6a3` | `1cdb0e27fc00085b76d0ee99bccf45c2adba6636eba358319536cd8cd047c978` | 0/0 |

Corrected Evidence lines 549-584 serialize all seven immediate and final
results, identities, business fingerprints, sentinel counts and replay
outcomes. Row one explicitly records pre-accept with no replay; row two records
the controlled commit that follows; rows three through seven contain exact
controlled commit, recovery or readback outcomes. No material reduction
remains.

### 4.3 RR2-B2 closed — Evidence

The Evidence removes or explicitly supersedes obsolete results, contains only
the current final 54/44 and 262/491 tables, literal commands, roots, RCs,
counts and zero-skip data, discriminating Effect controls, all seven complete
rows, per-Origin identities, precedence, Preservation and nonactivation. No
overstatement or contradiction remains.

## 5. Other contract verification

Earlier independently verified production properties remain exact because the
production hashes did not change: strict twelve-field provenance plus derived
fingerprint; two-shape absent-versus-object parser and explicit-null rejection;
transaction and journal binding; root-lock lookup/replay; four Origins and Loss
exclusivity; same-ID capability and payload conflicts; no redecision, TOCTOU or
fallback; resource classification; None Goldens; self-consistent refingerprinted
tamper rejection; and State, Gate, Economics, Account and Throttle first
commit/replay. No production-source defect was reproduced.

## 6. Fresh mandatory gates

Every Python run used `PYTHONDONTWRITEBYTECODE=1`, a unique existing `TMPDIR`
and `PYTHONPYCACHEPREFIX=<root>/pycache`. Every run returned RC 0 with
failures/errors/skips `0/0/0`.

| Module/gate | Root | Result |
|---|---|---:|
| Atomic V2 | `/tmp/iu4-i5-dp-rr3-atomic.pW6nKF` | 54/54 PASS |
| I5 Seam | `/tmp/iu4-i5-dp-rr3-seam.M5Yrck` | 44/44 PASS |
| Adapter V2 | `/tmp/iu4-i5-dp-rr3-adapterv2.L7QNah` | 18/18 PASS |
| Adapter V1 | `/tmp/iu4-i5-dp-rr3-adapterv1.5iX0FB` | 13/13 PASS |
| Pure Control | `/tmp/iu4-i5-dp-rr3-control.CStRH5` | 25/25 PASS |
| Atomic V1 | `/tmp/iu4-i5-dp-rr3-atomicv1.aFjnDr` | 23/23 PASS |
| Startup Gate | `/tmp/iu4-i5-dp-rr3-startup.sBZXaF` | 12/12 PASS |
| Runtime Gate | `/tmp/iu4-i5-dp-rr3-runtime.I5Lmku` | 3/3 PASS |
| Shadow Harness | `/tmp/iu4-i5-dp-rr3-shadowh.KKypph` | 18/18 PASS |
| Shadow Observation | `/tmp/iu4-i5-dp-rr3-shadowo.hgh3zZ` | 18/18 PASS |
| Replay Evidence | `/tmp/iu4-i5-dp-rr3-replayev.CUsotF` | 10/10 PASS |
| Replay Pipeline | `/tmp/iu4-i5-dp-rr3-replaypipe.AXJw61` | 6/6 PASS |
| Economics Shadow | `/tmp/iu4-i5-dp-rr3-econ.eBNX1z` | 9/9 PASS |
| Safe Launch | `/tmp/iu4-i5-dp-rr3-safe.4rEyE2` | 3/3 PASS |
| Preexecution Guards | `/tmp/iu4-i5-dp-rr3-guards.Lxs5Lh` | 6/6 PASS |
| combined exact 15-module order | `/tmp/iu4-i5-dp-rr3-combined.nXeyhE` | 262/262 PASS |
| full `tests/live_l1` | `/tmp/iu4-i5-dp-rr3-live.0Nmjtk` | 491/491 PASS |
| full `tests/regression` | `/tmp/iu4-i5-dp-rr3-regression.ZttB1q` | 170/170 PASS |
| exact four-path compile | `/tmp/iu4-i5-dp-rr3-compile.jd7akO` | PASS, exactly four external `.pyc` |
| `git diff --check` | canonical repository | PASS |
| `git diff --cached --check` | canonical repository | PASS |

## 7. Preservation and Freeze

All 25 exact mandate identities and counts match.

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

## 8. Scope and nonactivation

- exactly five candidate paths;
- only the two focused tests and Evidence changed in the rereview-2 Resolution;
- provenance production occurrences only in Coordinator and Adapter;
- no State, S4, Cursor or accepted I4 Request schema drift;
- no sidecar, second journal, new module, fixture or consumer;
- active Loop remains literal `LEGACY`;
- ENFORCED seam remains private and test-only;
- no productive V2 construction; and
- no launcher, Exchange, Live, I6-I8 or activation behavior.

Freeze and all preserved bytes remain unchanged.

## 9. Final authorization boundary

```text
I5_INDEPENDENT_ACCEPTANCE:READY
OPERATIONAL_ENFORCED_START_AUTHORIZED:NO
ACTIVE_V2_CONSUMER_AUTHORIZED:NO
I6_THROUGH_I8_AUTHORIZED:NO
ENFORCED_ACTIVATION_AUTHORIZED:NO
NEXT_REQUIRED_STEP:SEPARATE_FILE_EXACT_AUTHORITY_REQUIRED_BEFORE_ANY_I6_OR_ACTIVATION_WORK
```

No further mutation is authorized by this workstream. A separate explicit
file-exact authority is required before any I6 work, active consumer,
operational ENFORCED start or activation.
