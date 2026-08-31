# Pre-IU4 I6 Recovery, Monitoring and Projection — Mandate Independent Read-only Rereview 5 — 2026-08-21

## 1. Decision

```text
WORKSTREAM:IU4-I6-RECOVERY-MONITORING-PROJECTION-FILE-EXACT-MANDATE-INDEPENDENT-READONLY-REREVIEW-5
REVIEW_MODE:STRICT_INDEPENDENT_READONLY_FILE_EXACT
REVIEW_RESULT:READY
FINDINGS_BLOCKER:0
FINDINGS_HIGH:0
FINDINGS_MEDIUM:0
FINDINGS_LOW:0
I6_INDEPENDENT_ACCEPTANCE:READY
I6_IMPLEMENTATION_AUTHORIZED:YES_WITHIN_EXACT_SIX_PATH_SCOPE
I6_IMPLEMENTATION_ENTERED:NO
I6_EVIDENCE_CREATED:NO
OPERATIONAL_ENFORCED_START_AUTHORIZED:NO
ACTIVE_V2_CONSUMER_AUTHORIZED:NO
I7_AUTHORIZED:NO
I8_AUTHORIZED:NO
ENFORCED_ACTIVATION_AUTHORIZED:NO
```

Mandate revision 5 closes the final Report-sentinel blocker. The resulting
contract is file-exact, internally consistent, implementable within exactly
six later paths and does not authorize operational activation.

## 2. Review boundary

```text
CANONICAL_REPOSITORY:/home/benja/projects/sniper-bot
AGENTS_MD_READ_FULLY:YES
AGENTS_MD_LINES:162
REVIEW_MODE:STRICT_INDEPENDENT_READONLY_FILE_EXACT
REPOSITORY_MUTATION:NO
GIT_MUTATION:NO
CLEANUP_MUTATION:NO
FOREIGN_ARTIFACT_MUTATION:NO
I6_IMPLEMENTATION_ENTERED:NO
EXCLUDED_SPECIFICATION_BUNDLE_SCRIPT_READ:NO
EXCLUDED_SPECIFICATION_BUNDLE_SCRIPT_EXECUTED:NO
EXCLUDED_SPECIFICATION_BUNDLE_SCRIPT_CHANGED:NO
```

## 3. Repository and authority identities

```text
BRANCH:main
HEAD:c7ce0452aa2ccbf08c462784d68fa07b3dfe9595
MAIN:c7ce0452aa2ccbf08c462784d68fa07b3dfe9595
ORIGIN_MAIN:89e13fecd1ab549ca7099818b1c9ad4984cb6f7a
MAIN_AHEAD_OF_ORIGIN:6
MAIN_BEHIND_ORIGIN:0
FOREIGN_PREEXISTING_DIRTY_WORKTREE:PRESERVED_UNCHANGED
```

| Artifact | Recomputed identity |
|---|---|
| Revision 21 | `ab8f80720a1d8fe49b9085bce63658bcaecf7f0a3ea70fb555559223090824e0`, 4,605 |
| final I2 rereview | `5a59ad8c97ebae85148661fe0e3bedab643c7f12ae2c8d4e87272447c0616679`, 300 |
| final I3 Evidence | `20846284ffad9e8b755dd6a3b74f963d8d2c6ee1519fafdd0bc1275f2e33c390`, 463 |
| final I3 rereview 6 | `03790420534e38c7e36d1824a472dfd80763340dacec8847ddf5072d55db0c9f`, 191 |
| final I4 Evidence | `068c2ba2661031843a13dd3f2c4684f9340f432b90b192b6b7492dae8968270d`, 403 |
| final I4 rereview 3 | `c6d8bbcb35572a364b74a47eb9ad817240a8b0cce70e514942bb674d3861c38b`, 191 |
| corrected I5 mandate | `a688773cc10dd6c573e7c019245639c010a3b0abb49fb301249aeebeba182a91`, 633 |
| I5 mandate READY rereview 2 | `934bf4a9010aff61796cc2c7c09f54380c5527546bea6e4bc25b5a17933bfd59`, 242 |
| final I5 Resolution 2 | `4512288b16541f659b434000114853f05e457acf5df4e3e779c14b03d44b2985`, 237 |
| final I5 Evidence | `33d18b64bc92d0f5631d3a8306010e8889bb69085d7ce4e77c36c1fd1e185b65`, 633 |
| final I5 rereview 3 | `9031ec6ef31d61787d46082dab50c59823bb0ba45155cba2b9abc5928f6d96d9`, 246, READY |
| prior I6 rereview 4 | `bb2d4364eed87dcaf01f1f5a84039ad36519ed4bcbf7bd6b425892d780c56971`, 250, NOT_READY 1/0/0/0 |
| I6 Resolution 4 | `170ca41222b57b55371105d920128c65a62d5c00f1c0d3fa5346f35a176a69c0`, 251 |
| reviewed I6 mandate revision 5 | `9d9bdacb5f907f9e9927dc7c7d3ecec25718ccb448b6f69acff0ad6baf1a4dc6`, 1,281 |

Mandate and Resolution are UTF-8 and end with LF.

## 4. Final RR4 blocker closure — PASS

Mandate lines 784–798 define the general Report primitive and enum domain,
including explicit exceptions only for the paired sentinel rows.

Lines 800–809 define the exhaustive bidirectional matrix:

- absent Session: status `ABSENT`, ID `NONE`, OPEN fingerprint `NONE`, and no
  current-Generation Ledger OPEN;
- present Session: nonempty ID, hex64 OPEN fingerprint and concrete OPEN
  binding;
- absent manifest: only `LEGACY`, `MONITOR_ONLY`, zero open PREPAREs and no
  selected-Generation Genesis/Handoff PREPARE or COMMIT;
- present manifest: nonempty ID and hex64 fingerprint;
- absent Cursor: durable Cursor absent, ID/fingerprint `NONE`, sequence `0`,
  head `EMPTY`; and
- present Cursor: nonempty ID, hex64 fingerprint, positive sequence and hex64
  head.

Lines 811–823 make the rules iff/bidirectional and reject every mixed pair
before Report derivation. They preserve output-only crash semantics: a durable
output is never silently treated as a Cursor.

Lines 825–860 bind Owner Epoch, operation, Ledger state, Projection lag and
fixed canonical vectors for:

- DIRECT first-start without a prior Session;
- permitted absent manifest;
- absent Cursor;
- output-only crash;
- fully present Session/manifest/Cursor; and
- every mixed-pair/status/sequence/head negative.

No sentinel value must be invented by the implementation. RR4-B1 is fully
closed.

## 5. Earlier closure recheck

### 5.1 PROCESS_DEATH and Trust Anchor — PASS

The mandate permits only confirmed process death plus reap and rejects
higher-token publication, post-write conflict detection and fixture-only
fencing. The proof and separately prebound Trust Anchor remain exact-type,
canonical, Session/OPEN/Worker/Authority/root-bound and zero-mutation on
failure. Real accepted `TerminalPersistenceWorkerV8` live/unreaped/
surviving-holder characterization remains mandatory.

### 5.2 Cursor ancestry and Projection root — PASS

The contract retains:

- immutable sequence-zero/`EMPTY` Authority base;
- exact `previous + 1` progression;
- state-before/head ancestry;
- one-by-one catch-up;
- no skip, gap, fork or batch-tip publication;
- exact caller-root/Projection-root derivation;
- exact domain bytes
  `b"IU4_PROJECTION_ROOT_V1\x00" + projection_root_path.encode("utf-8", "strict")`;
- Projection-root-relative UTF-8/NFC inventory names;
- fixed inventory bytes and noncyclic observation before Cursor-temp creation;
  and
- CAS, sync/readback and crash reconciliation.

### 5.3 Observation and Report — PASS

The contract consistently requires:

- exactly twelve Observation groups;
- exactly twelve named Report group results;
- no thirteenth group;
- exact Report field list and hash domains;
- exact Group-12 field-specific primitive types, enums and PASS/WARN/FAIL
  rules;
- derived, never caller-selected group/capability/overall results; and
- complete R21 Listener, Liveness, scalar-authority, heartbeat/budget and
  DIRECT eligibility matrices.

### 5.4 Evidence — PASS

The Evidence payload fingerprint remains noncyclic: the final
`EVIDENCE_PAYLOAD_SHA256` line hashes all preceding UTF-8/LF bytes and excludes
itself. Whole-file Evidence SHA/count is externally bound by the later
independent implementation rereview. No seventh path is needed.

## 6. Exact six-path boundary

| Operation | Path | Recomputed start |
|---|---|---|
| MODIFY | `live_l1/state/paper_atomic_coordinator.py` | `446ae8712d09bc52f950587a2e3ecec0c60fd21b3c9150a8886af1b3b2b4f9ec`, 5,796 |
| MODIFY | `live_l1/state/models.py` | `3254d2f1a6509ec5f8f623dd8f286f60cfcc108f66f2d8eb107338d795115c7e`, 27 |
| MODIFY | `live_l1/state/state_store.py` | `50a85cf6bd382850d39e69cd785a5dc2ded0a66a1d82856b4baa11877bdba177`, 220 |
| CREATE | `live_l1/state/paper_iu4_recovery_projection.py` | worktree absent; HEAD absent |
| CREATE | `tests/live_l1/test_paper_iu4_recovery_projection.py` | worktree absent; HEAD absent |
| CREATE | `docs/review/PRE_IU4_I6_RECOVERY_MONITORING_PROJECTION_FILE_EXACT_IMPLEMENTATION_EVIDENCE_2026-08-20.md` | worktree absent; HEAD absent |

```text
AUTHORIZED_LATER_PATHS:6
AUTHORIZED_MODIFY_PATHS:3
AUTHORIZED_CREATE_PATHS:3
SEVENTH_PATH_REQUIRED:NO
THREE_CREATE_TARGETS_WORKTREE_ABSENT:YES
THREE_CREATE_TARGETS_HEAD_ABSENT:YES
```

The Lifecycle Ledger supplies authority pairs, durable append, Restart
consumption, recovery materialization and Terminal-Gap records. The Startup
Gate supplies the strict Restart/Recovery Authorization type and operations.
Both remain read-only and sufficient.

## 7. Fresh read-only gates

All Python runs used `PYTHONDONTWRITEBYTECODE=1`, unique existing `TMPDIR`
roots and external `PYTHONPYCACHEPREFIX` roots below `/tmp`.

| Gate | Root | Result |
|---|---|---|
| exact accepted I5 15-module set | `/tmp/iu4-i6-mandate-rr5-i5exact.PHX0eE` | 262/262 PASS, RC 0, failures/errors/skips 0/0/0 |
| full `tests/live_l1` | `/tmp/iu4-i6-mandate-rr5-live.yrjmlK` | 491/491 PASS, RC 0, failures/errors/skips 0/0/0 |
| full regression | `/tmp/iu4-i6-mandate-rr5-regression.9lAUhH` | 170/170 PASS, RC 0, failures/errors/skips 0/0/0 |
| current three-MODIFY-path compile | `/tmp/iu4-i6-mandate-rr5-compile.CtDgnt` | PASS, RC 0, exactly 3 external `.pyc` |
| `git diff --check` | canonical worktree | PASS, RC 0 |
| `git diff --cached --check` | canonical index | PASS, RC 0 |

Compile products:

```text
/tmp/iu4-i6-mandate-rr5-compile.CtDgnt/pycache/home/benja/projects/sniper-bot/live_l1/state/paper_atomic_coordinator.cpython-314.pyc
/tmp/iu4-i6-mandate-rr5-compile.CtDgnt/pycache/home/benja/projects/sniper-bot/live_l1/state/models.cpython-314.pyc
/tmp/iu4-i6-mandate-rr5-compile.CtDgnt/pycache/home/benja/projects/sniper-bot/live_l1/state/state_store.cpython-314.pyc
```

## 8. Preservation and Freeze

All 22 source/test identities match:

```text
loop:e4db22642b628fe4b84cf0d2daa9ecd846208138eaa3868a02a56ddf9f75ee6c/1947
execution:85a9acb238dafd3adf5fd8bf57153772d3c7b41559943bdcce5336e3b60dcb5e/1386
adapter:1fac2629a0ebdd889825f496e9273c358ffe7596c2173d307ce1d1eb7e9bd6a6/1896
paper_artifacts:3cd9a459e2856672bb7b318c9cdbf8f8bb52e633ee9529d74761d64928213946/1575
loss_cluster:4ce7d59f64a67de94ffc6f1d03ff4e6c8a7a590802abb003b311cd0d56cc3e55/521
atomic_v2_test:ec731c106ab23b78e482204e16d20826264cdf775f0c08c292a82bab1111ff8c/3734
seam_v2_test:fc61404d910fe76141cba8ba54f98ea6de552664a8b21bdaa50510e33f603755/2517
adapter_v2_test:f71d46700a1966534429281091da32e263ac479ddf1393c5021d015eac1cd1b3/1274
execution_control:7d3cb901c1c67c8df85e99bc579fda85d8732b634ff4747e08620b92ac1e44f7/257
runtime_gate:447573e484bc13023a118ae61bf7615657293be629c30729748e64f0af7af7c5/201
startup_gate:c4a1854f3b200525568a40205b39e9ce2e14c342bb860569ba7fcfe5e9c063cd/919
shadow_runtime_gate:98d986f3ac2e463b371998604d92b29aa113a507dd0f84bcbd3ff36a52efaf59/438
shadow_observation_gate:ed4e75fad664c68b91950e9c09e873823ebe3eb0b0062f85806daa09ce661350/886
shadow_harness:ddfb60f19a3b765a476c8de0464d583590313cdd0583391044cb338fec969f77/1007
lifecycle_ledger:d72134195f66b1d39c09a2ca6b9919d8a9acf17c4490ab52d9abc2aebcd71337/438
economics:a302013134d1265ac85ad10b57a67ead9e2343043f7eb499fd965a44312525ae/730
core_throttle:ad5447d88a2c35c9a71a5495c61c8f08fa844daf60e79d4a872234e88037df75/727
state_throttle:ce76d8430792d6de1cfdf9a55c09cb6ab501489c7610d2f78345f8d78646295b/586
safe_launch:cb90bd49b36de56e8ad95e9b24febb23baa0513b1ec51e7402f63a5efd6ec652/201
adapter_v1_test:b4947e4c03fa3b187e01c4005062337d1837b70d652243030581172dd4d2c339/441
execution_control_test:0ae44f2d32f5f3b6affe37a258be0e6aee06790f857e4fc01628c6795bda99e5/843
atomic_v1_test:a46f622f9a00e5db727ade04ece89b4deaf51347dc2d1f4d304532572b382753/891
```

```text
FREEZE_DIRECTORY_MODE:0555
PRESERVATION_TAR_SHA256:3af14ff2e270d7d3ca09c1279da7d64e6d720630d06a0c5f45b6786237782037
PRESERVATION_TAR_MODE:0444
PRESERVATION_TAR_ENTRIES:1318
FREEZE_MANIFEST_SHA256:ad154c0eda13470920878873ed170368cc8f4c43591400a07592a77b179d9e16
FREEZE_MANIFEST_MODE:0444
FREEZE_MANIFEST_LINES:60
```

## 9. Scope and non-activation

No CREATE target exists and no I6 source, focused test or Evidence was entered.
No active I6 consumer exists; the Startup-Gate `RECONCILE_TERMINAL_GAP`
literal is accepted I2 authority, not an operational caller.

No Loop, Adapter, Execution, Gate, launcher, Runtime Session, process probe,
network, Exchange, Live, Production, I7/I8 or ENFORCED activation was
introduced.

## 10. Exact next step

```text
I6_INDEPENDENT_ACCEPTANCE:READY
NEXT_REQUIRED_STEP:IU4-I6-RECOVERY-MONITORING-PROJECTION-IMPLEMENTATION
```

Only a separately invoked I6 implementation may now modify the exact six
authorized paths under mandate SHA-256
`9d9bdacb5f907f9e9927dc7c7d3ecec25718ccb448b6f69acff0ad6baf1a4dc6`.
This READY result does not authorize an active consumer, operational ENFORCED
start, I7, I8 or activation.
