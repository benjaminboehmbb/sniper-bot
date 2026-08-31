# Pre-IU4 I4 Adapter Request V2 Implementation — Independent Read-Only File-Exact Rereview 3 — 2026-08-20

## 1. Final verdict

```text
WORKSTREAM:IU4-I4-ADAPTER-REQUEST-V2-IMPLEMENTATION-INDEPENDENT-READONLY-FILE-EXACT-REREVIEW-3
REREVIEW_RESULT:READY
I4_INDEPENDENT_ACCEPTANCE:READY
I4_RESULT_ACCEPTED:YES
BLOCKER:0
HIGH:0
MEDIUM:0
LOW:0
I5_AUTHORIZED:NO
ACTIVE_V2_CONSUMER_AUTHORIZED:NO
ATOMIC_V2_COMMIT_FROM_ADAPTER_AUTHORIZED:NO
ENFORCED_ACTIVATION_AUTHORIZED:NO
```

The corrected I4 Adapter Request V2 implementation, focused test and
Implementation Evidence satisfy the accepted file-exact mandate. Both original
technical findings and the later Evidence-precision finding are independently
closed. I4 is accepted as a dormant, pure validation capability only.

## 2. Independence and read-only method

The independent reviewer:

- worked only in `/home/benja/projects/sniper-bot`;
- read `AGENTS.md` completely before review actions;
- independently recomputed the controlling and candidate identities;
- independently reproduced the corrected technical matrices instead of
  trusting Implementation Evidence;
- ran every mandatory command with `PYTHONDONTWRITEBYTECODE=1`, isolated
  caches and review-owned `/tmp` roots;
- did not modify candidate files, Git state, frozen archives or foreign
  artifacts; and
- did not read, execute or modify the expressly excluded RCC002 bundle script.

Serialization of this READY record is a governance action after completion of
the read-only review. It does not modify the accepted three-path candidate.

## 3. Controlling chain

```text
CANONICAL_REPOSITORY:/home/benja/projects/sniper-bot
BRANCH:main
HEAD:c7ce0452aa2ccbf08c462784d68fa07b3dfe9595
MAIN:c7ce0452aa2ccbf08c462784d68fa07b3dfe9595
ORIGIN_MAIN:89e13fecd1ab549ca7099818b1c9ad4984cb6f7a
MAIN_AHEAD_OF_ORIGIN:6
MAIN_BEHIND_ORIGIN:0
```

| Artifact | SHA-256 | Lines | Result |
|---|---|---:|---|
| corrected I4 mandate | `e4039400d24781c9d1911b7b7448e49773d92e7134f8ecee1042cdf47438c3f1` | 601 | controlling |
| I4 mandate rereview 2 | `b83d869b38b0afeafaad41e98240ffec5a66af6f6175c8f0572092ad14b5ee7e` | 250 | `READY` |
| first I4 implementation rereview | `7891fa740d185c06add6b6d36dd8681edef122763d9c2797146f92a85b2f561c` | 276 | `NOT_READY`, 1/1/0/0 |
| first implementation resolution | `8e0e2f0ccc68937e426a549cbf210d32b89987ac2e18fa6eaba18b6a411007e3` | 252 | technical findings closed |
| implementation rereview 2 | `1b2fcfd38600fdf0507bc87640ce4a1c1a97b0d3b5159cf156afc27ec2fabf3e` | 210 | `NOT_READY`, 0/0/0/1 |
| Evidence-precision resolution | `e77900fae23617facaf04b2078e3a4662c8d805733a00063db1bcb4f553522d3` | 168 | LOW finding closed |

The earlier Revision-21, I2 and I3 authorities remain unchanged. In
particular, final I3 Evidence is
`20846284ffad9e8b755dd6a3b74f963d8d2c6ee1519fafdd0bc1275f2e33c390`
at 463 lines and final I3 rereview 6 is
`03790420534e38c7e36d1824a472dfd80763340dacec8847ddf5072d55db0c9f`
at 191 lines.

## 4. Accepted file-exact candidate

| Operation | Path | Mandate-time identity | Accepted identity |
|---|---|---|---|
| MODIFY | `live_l1/core/paper_iu4_adapter.py` | `d65525f31746d1edf30bf1ffc7f84a845f97b3f4120904c9910b741bc8c76a7b` / 641 | `10bca02453a67315882f30052643ee447ad1bfbbc34856d2403279670630d458` / 1,179 |
| CREATE | `tests/live_l1/test_paper_iu4_adapter_v2.py` | absent | `f71d46700a1966534429281091da32e263ac479ddf1393c5021d015eac1cd1b3` / 1,274 |
| CREATE | `docs/review/PRE_IU4_I4_ADAPTER_REQUEST_V2_IMPLEMENTATION_EVIDENCE_2026-08-20.md` | absent | `068c2ba2661031843a13dd3f2c4684f9340f432b90b192b6b7492dae8968270d` / 403 |

The Adapter diff against its mandate-time identity is additive: 538 additions
and zero deletions. V2 symbol search returns exactly the Adapter and focused
test. No fourth I4 implementation, test, fixture, sidecar, schema, profile,
configuration or Evidence path exists.

## 5. Evidence-precision closure

Implementation Evidence line 399 is byte-exact:

```text
NEXT_REQUIRED_STEP:IU4-I4-ADAPTER-REQUEST-V2-IMPLEMENTATION-INDEPENDENT-READONLY-FILE-EXACT-REREVIEW-3
```

Evidence-precision resolution line 160 contains the same value. No stale or
competing current normative next-step statement exists. The old no-suffix value
in rereview-2 line 123 is solely a historical quotation of the closed finding.

```text
I4_IRR2_L1:CLOSED
STALE_EVIDENCE_NEXT_STEP:NO
EVIDENCE_PRECISION_FINDINGS_OPEN:0
```

## 6. Independent adversarial technical results

| Contract | Independent result |
|---|---:|
| OPEN_LONG/OPEN_SHORT × Stops `95`, `100`, `105` at reference `100` | 6/6 accepted |
| Position × Intent × Action × Reason matrix | 630/630 exact; 29 accepted, 601 rejected |
| fake LONG/SHORT TP/SL/Time-stop | 6/6 rejected |
| wrong-priority/divergent Reasons | 18/18 rejected |
| stable failure-code families | 8/8 exact |
| detailed first-failure precedence stages | 13/13 exact |
| trusted Event/Decision/State/Profile/Authorization negatives | 18/18 rejected |
| individually removed Loss-NOOP predicates | 3/3 rejected |
| HARD/EMERGENCY Action matrix | 10/10 rejected pre-accept |

Adversarial roots:

```text
/tmp/iu4-i4-impl-rereview3-adversarial.HqhgOM
/tmp/iu4-i4-impl-rereview3-precedence.z1JwmH
```

The exact 25-field Request schema, strict built-in primitives, canonical UTC,
SHA and Decimal text, content-addressed Request ID/conflict behavior, frozen
eight-field trusted context, Decision/State/Profile/Authorization binding,
autonomous actual Intent, Loss-specific NOOP, SOFT/terminal ordering, purity,
V1 compatibility and inactive boundary are all independently confirmed.

The validator performs no Coordinator commit and creates no State, Journal,
Cursor, cache, sidecar or audit record. `PaperIU4Adapter.execute()` remains
V1-only. No Loop, Gate, Execution, Shadow or replay consumer imports V2.

## 7. Fresh mandatory verification

Every test command completed with RC 0 and failures/errors/skips `0/0/0`.

| Exact target | Root | Result |
|---|---|---:|
| focused Adapter V2 | `/tmp/iu4-i4-impl-rereview3-tests_live_l1_test_paper_iu4_adapter_v2.d6pO9E` | 18/18 PASS |
| Adapter V1 | `/tmp/iu4-i4-impl-rereview3-tests_live_l1_test_paper_iu4_adapter.DfOxNg` | 13/13 PASS |
| Pure Control | `/tmp/iu4-i4-impl-rereview3-tests_live_l1_test_paper_execution_control.VLqIcT` | 25/25 PASS |
| Atomic V2 | `/tmp/iu4-i4-impl-rereview3-tests_live_l1_test_paper_atomic_coordinator_v2.vHHTO0` | 44/44 PASS |
| Atomic V1 | `/tmp/iu4-i4-impl-rereview3-tests_live_l1_test_paper_atomic_coordinator.2dblqu` | 23/23 PASS |
| Startup Gate | `/tmp/iu4-i4-impl-rereview3-tests_live_l1_test_paper_iu4_startup_gate.Rvpqjv` | 12/12 PASS |
| Runtime Gate | `/tmp/iu4-i4-impl-rereview3-tests_live_l1_test_paper_iu4_runtime_gate.IwGIl3` | 3/3 PASS |
| Shadow Harness | `/tmp/iu4-i4-impl-rereview3-tests_live_l1_test_paper_iu4_shadow_harness.zpZ1Bo` | 18/18 PASS |
| Replay Evidence | `/tmp/iu4-i4-impl-rereview3-tests_live_l1_test_paper_iu4_replay_evidence.7TJwo9` | 10/10 PASS |
| Replay Pipeline | `/tmp/iu4-i4-impl-rereview3-tests_live_l1_test_paper_iu4_replay_pipeline.HOyW5q` | 6/6 PASS |
| all ten mandatory modules | `/tmp/iu4-i4-impl-rereview3-combined.nqKFu0` | 172/172 PASS |
| complete `tests/live_l1` | `/tmp/iu4-i4-impl-rereview3-live.0B1QaX` | 437/437 PASS |
| complete regression | `/tmp/iu4-i4-impl-rereview3-regression.KYTXtd` | 170/170 PASS |
| exact two-path compile | `/tmp/iu4-i4-impl-rereview3-exact-compile.o8Dwlr` | PASS; exactly two `.pyc` |
| `git diff --check` | canonical repository | PASS |

## 8. Freeze and preservation

```text
PRESERVATION_TAR_SHA256:3af14ff2e270d7d3ca09c1279da7d64e6d720630d06a0c5f45b6786237782037
PRESERVATION_TAR_MODE:0444
PRESERVATION_TAR_ENTRIES:1318
FREEZE_MANIFEST_SHA256:ad154c0eda13470920878873ed170368cc8f4c43591400a07592a77b179d9e16
FREEZE_MANIFEST_MODE:0444
FREEZE_MANIFEST_LINES:60
FREEZE_DIRECTORY_MODE:0555
SECTION_5_PRESERVATION_IDENTITIES:19/19_EXACT
```

All accepted I2/I3 artifacts and all 19 corrected I4 mandate Section-5
Source/Test identities are exact. Other pre-existing worktree artifacts were
neither cleaned nor modified.

## 9. Acceptance boundary and next governance step

```text
I4_INDEPENDENT_ACCEPTANCE:READY
I4_RESULT_ACCEPTED:YES
I4_TECHNICAL_FINDINGS_OPEN:0
I4_EVIDENCE_FINDINGS_OPEN:0
I5_AUTHORIZED:NO
ACTIVE_V2_CONSUMER_AUTHORIZED:NO
ATOMIC_V2_COMMIT_FROM_ADAPTER_AUTHORIZED:NO
ENFORCED_ACTIVATION_AUTHORIZED:NO
```

I4 is accepted only as the dormant Adapter Request V2 value and pure validation
contract. This READY record does not authorize I5, an active Adapter consumer,
Snapshot acceptance, Atomic V2 commit mapping or activation.

The only permissible next governance action is a separate I5 file-exact
mandate. No I5 implementation may begin without that mandate and its own
independent authorization.
