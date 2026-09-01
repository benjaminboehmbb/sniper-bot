# I7 R5-F2 V18 — P2C-T B1 Test Validation Evidence Proposal

Date: 2026-09-01

Classification:

`NONAUTHORITATIVE_P2C_T_B1_TEST_VALIDATION_EVIDENCE_PROPOSAL`

Status:

`B1_T_LOCALLY_VALIDATED_NOT_PUBLICATION_AUTHORITATIVE`

## 1. Authority boundary

This nonauthoritative proposal preserves the directly observed result of one
authorized local, isolated P2C-T-B1-T validation run.

It has no Evidence, Acceptance, Publication, Staging, Commit, Push,
Execution, Live, or Exchange authority. It authorizes neither B1-S, B1-C,
B1-P, B1-A, P2C-S, P2C-C, P2C-P, P2C-A, P1, nor G2. No later gate may reuse
the authorization that created this proposal.

## 2. Repository and manifest base

| Field | Bound value |
|---|---|
| Repository | `/home/benja/projects/sniper-bot` |
| Branch | `main` |
| HEAD/main/origin/main | `9efc0301c632eadc87b69f7cb4269772ca20fab5` |
| Parent | `47f0d450565ae3c791e0f0dd81726fad08752d0b` |
| Index | empty |
| Tracked unstaged | 5 |
| Untracked | 86 |
| Records | 91 |

No index lock or merge, rebase, cherry-pick, revert, or bisect state existed.

| Identity | Format | SHA-256 | Bytes | Records/lines |
|---|---|---|---:|---:|
| Status | NUL-terminated porcelain v1 | `5363ba7596358c7ed41120723cbf99daf4919b468f1720a5cf4bf41f5e5b912b` | 7887 | 91 |
| Worktree content | `<status2><TAB><sha256><TAB><path><LF>`, path-sorted | `e562c1a54d9e35f35ef8090cbf029392c81476bb832f1a11db67604d53a66d7b` | 13802 | 91 |
| Untracked | `<sha256><SPACE><bytes><SPACE><lines><SPACE><path><LF>`, path-sorted | `d25a4b225bbf9e80934ec2d545c85c8accb991560d1dd8328066dff881ceea16` | 13870 | 86 |

## 3. Governance binding

`docs/review/I7_R5_F2_V18_P2C_T_STARTUP_AUTHORITY_DEPENDENCY_CLOSURE_PROPOSAL_FILE_EXACT_2026-09-01.md`

| SHA-256 | Bytes | Lines |
|---|---:|---:|
| `2508b6abac8d3244cb1e6e33314f394ce29b9b0d5e6bf5b472e9c6ad58bd2b40` | 18853 | 460 |

Preceding decision:

`I7_R5_F2_V18_P2C_T_B1_SOURCE_SCOPE_REVIEW_READY`

Observed validation result:

`I7_R5_F2_V18_P2C_T_B1_TEST_VALIDATION_READY`

Neither decision is standalone file evidence or authority.

## 4. Isolated tree and overlay scope

The test tree was a read-only `git archive HEAD` plus exactly three
byte-exact overlays. TMPDIR and PYTHONPYCACHEPREFIX were separate children of
one bound temporary root. The governance proposal was not an overlay.

| Role/path | SHA-256 | Git blob | Bytes | Lines |
|---|---|---|---:|---:|
| `live_l1/core/paper_iu4_startup_gate.py` | `c4a1854f3b200525568a40205b39e9ce2e14c342bb860569ba7fcfe5e9c063cd` | `f7da370d9f8e3538907cf14a91d39aa538bf3462` | 37668 | 919 |
| `live_l1/state/paper_iu4_recovery_projection.py` | `b12f3ece36dea4a83faddee5db43c1964884ba25a03bacaae476d22cdea77946` | absent at HEAD | 299085 | 6033 |
| `tests/live_l1/test_paper_iu4_recovery_projection.py` | `57a45dbf6b6bc56152c8c328c0d15992ab0345278cb6fa30667b6e902183e1c9` | absent at HEAD | 255265 | 5307 |

Startup-gate HEAD:

| SHA-256 | Git blob | Bytes | Lines |
|---|---|---:|---:|
| `86b191afb7725d613898d6911b543a84e9e0ada1f9c59822e3c47107272a6753` | `faf51735cf22a1279993a735c87439f516c1d9a1` | 21869 | 600 |

`IU4RestartRecoveryAuthorizationV1` was defined at isolated line 395 and
exported at line 908.

## 5. Clean bound dependencies

Each path was byte-equal between canonical worktree and HEAD:

| Path | SHA-256 | Bytes | Lines | HEAD blob |
|---|---|---:|---:|---|
| `live_l1/core/paper_economics.py` | `a302013134d1265ac85ad10b57a67ead9e2343043f7eb499fd965a44312525ae` | 24974 | 730 | `7ccf88c814b61bbe6232cf72812f518721cb5c54` |
| `live_l1/core/paper_entry_throttle.py` | `ad5447d88a2c35c9a71a5495c61c8f08fa844daf60e79d4a872234e88037df75` | 26549 | 727 | `8570eec9102bb80bd19e78ccc834412708dc2902` |
| `live_l1/state/models.py` | `b9bc3b9a598fefeef83a2905432daf924ccf54e9701f313e2af99a6a8e833f53` | 5000 | 125 | `0da3f45f3c6e111984dc5a9a930bf5a72af462b3` |
| `live_l1/state/state_store.py` | `b742131ba8af8e9c34157244de5cd743a045b7ae985dd4b502486e71fd2011c9` | 20999 | 594 | `9b9face53b2d85b75f643ec6e2a6e5c6631971d1` |
| `live_l1/state/iu4_lifecycle_ledger.py` | `d72134195f66b1d39c09a2ca6b9919d8a9acf17c4490ab52d9abc2aebcd71337` | 18211 | 438 | `33e8209465de0b33df2db5f215d16adfdcbe00d7` |
| `live_l1/state/loss_cluster.py` | `4ce7d59f64a67de94ffc6f1d03ff4e6c8a7a590802abb003b311cd0d56cc3e55` | 18475 | 521 | `4a83b1e0b53518b16d6382adcb5a5ff5682c49b9` |
| `live_l1/state/paper_artifacts.py` | `3cd9a459e2856672bb7b318c9cdbf8f8bb52e633ee9529d74761d64928213946` | 57620 | 1575 | `ec3859f36ed4239a650fa6de1cd66e01f00c2967` |
| `live_l1/state/paper_atomic_coordinator.py` | `b8ce5ba89016cac8e34ee2646f3bf9746b2909fa3b7c9e1ef6c74557c3aaffcb` | 262786 | 6020 | `167d3a54e92bf4aeeb852126f767cee39a22a3aa` |
| `tests/live_l1/test_paper_iu4_startup_gate.py` | `29d07a9c19aabcf369de101fd9599413a7f20ee03685eb96495993cad5588034` | 20017 | 537 | `31c8ee39824f924d089e10c318b3b13defe79f3a` |

## 6. Static closure and isolated origins

Complete static live_l1 closure:

- `live_l1.core.paper_economics`
- `live_l1.core.paper_entry_throttle`
- `live_l1.core.paper_iu4_startup_gate`
- `live_l1.state.iu4_lifecycle_ledger`
- `live_l1.state.loss_cluster`
- `live_l1.state.models`
- `live_l1.state.paper_artifacts`
- `live_l1.state.paper_atomic_coordinator`
- `live_l1.state.paper_iu4_recovery_projection`
- `live_l1.state.persist`
- `live_l1.state.state_store`

All closure members resolved from overlays or archived HEAD. No excluded
tracked-unstaged or untracked path was required.

The following twelve modules loaded bytecode-free strictly from the isolated
tree:

- `live_l1.core.paper_iu4_startup_gate`
- `live_l1.state.paper_iu4_recovery_projection`
- `tests.live_l1.test_paper_iu4_startup_gate`
- `tests.live_l1.test_paper_iu4_recovery_projection`
- `live_l1.core.paper_economics`
- `live_l1.core.paper_entry_throttle`
- `live_l1.state.models`
- `live_l1.state.state_store`
- `live_l1.state.iu4_lifecycle_ledger`
- `live_l1.state.loss_cluster`
- `live_l1.state.paper_artifacts`
- `live_l1.state.paper_atomic_coordinator`

Each origin was its corresponding module path under the isolated publication
tree; none loaded from the canonical dirty worktree.

## 7. Compile and test results

Interpreter:
`/home/benja/projects/sniper-bot/.venv/bin/python`

Compile targets were startup gate, atomic coordinator, models, state store,
recovery projection, startup-gate test, and recovery-projection test.

| Compile RC | Files | PYC files | PYC scope |
|---:|---:|---:|---|
| 0 | 7 | 7 | temporary PYTHONPYCACHEPREFIX only |

No compile artifact appeared in the canonical repository.

| Test target | Tests | Failures | Errors | Skips | RC | Result | Runtime |
|---|---:|---:|---:|---:|---:|---|---:|
| `tests.live_l1.test_paper_iu4_startup_gate` | 12 | 0 | 0 | 0 | 0 | `OK` | 0.021 s |
| `tests.live_l1.test_paper_iu4_recovery_projection` | 88 | 0 | 0 | 0 | 0 | `OK` | 351.816 s |
| `tests.live_l1.test_paper_atomic_coordinator_v2` | 54 | 0 | 0 | 0 | 0 | `OK` | 0.785 s |
| `tests.live_l1.test_iu4_lifecycle_ledger` | 5 | 0 | 0 | 0 | 0 | `OK` | 0.003 s |
| `tests.live_l1.test_paper_atomic_coordinator` | 23 | 0 | 0 | 0 | 0 | `OK` | 0.073 s |
| `unittest discover -s tests/regression -p test_*.py` | 170 | 0 | 0 | 0 | 0 | `OK` | 1.663 s |

The regression closure inspected 12 matching test files before execution.
No full tests/live_l1 discovery or unlisted test ran.

### 7.1 Exact P2C class distribution

| Class | Tests |
|---|---:|
| `I6ArtifactContractTests` | 10 |
| `I6ProjectionAndStoreTests` | 22 |
| `I6MonitoringTests` | 17 |
| `I6MonitoringNamespaceBoundaryTests` | 2 |
| `I6MonitoringObservationContentBoundaryTests` | 2 |
| `I6MonitoringResultAuthorityBoundaryTests` | 2 |
| `I6MonitoringDataclassFactoryBoundaryTests` | 2 |
| `I6MonitoringFactoryExactTypeBoundaryTests` | 2 |
| `I6MonitoringBuiltinCanonicalityBoundaryTests` | 4 |
| `I6MonitoringSerializationAuthorityBoundaryTests` | 2 |
| `I6RecoveryLifecycleTests` | 23 |
| **Total** | **88** |

Observed output:

`MemoryError: secondary target cleanup`

This came from a failure path exercised inside the tests. It was not a
unittest Error or Failure: RC 0, 88 tests, zero Failures, zero Errors, zero
Skips, final `OK`. It grants no additional Acceptance.

Aggregate: 352 tests, 0 Failures, 0 Errors, 0 Skips, all test-command RCs 0.
Exact sum: 12 + 88 + 54 + 5 + 23 + 170 = 352.

## 8. Exclusions and P2A ownership

Excluded tracked-unstaged paths:

- `live_l1/core/execution.py`
- `live_l1/core/loop.py`
- `live_l1/core/paper_iu4_adapter.py`
- `live_l1/core/paper_iu4_shadow_runtime_gate.py`

The 84 untracked records outside the two P2C overlays, including the
governance proposal, were excluded.

P2A-owned evidence:

`docs/review/PRE_IU4_I6_RECOVERY_MONITORING_PROJECTION_FILE_EXACT_IMPLEMENTATION_EVIDENCE_2026-08-20.md`

| SHA-256 | Bytes | Lines | HEAD blob | Classification |
|---|---:|---:|---|---|
| `5a733d7deb9d34633bea8718bda8e0749558810426e5985f8f3335b500789834` | 89983 | 1074 | `1c521838972b6455eba97019613712350aecb0c5` | `TRACKED_AT_CURRENT_BASE_P2A_PHYSICAL_OWNERSHIP` |

It was neither overlay nor test target and gains no P2C ownership.

## 9. Post-attestation and cleanup

After all commands:

1. all overlays and dependencies retained byte-exact identities;
2. the isolated publication-tree snapshot was unchanged;
3. PYC, TMP, and test artifacts remained below the temporary root;
4. no new canonical PYC, __pycache__, TMP, or test artifact appeared;
5. the pre-existing canonical artifact set remained unchanged;
6. HEAD, main, origin/main, index, and all 91 worktree records were unchanged;
7. all three manifest identities remained exact;
8. proposal and P2A evidence remained unchanged;
9. four foreign tracked-unstaged and 84 non-overlay untracked records stayed
   excluded.

The temporary directory was removed only after realpath, `/tmp` parent,
basename-prefix, directory-type, and non-symlink checks. Afterwards it was
absent, other matching paths were unchanged, and the repository remained at
5 tracked-unstaged, 86 untracked, and 91 records.

## 10. Fail-closed decision

Observed local result:

`I7_R5_F2_V18_P2C_T_B1_TEST_VALIDATION_READY`

This only records a passed bounded local validation. B1-T remains not
publication-authoritative. Independent file-exact rereview is required
before this proposal can be governance input for later staging.

B1-S, B1-C, B1-P, B1-A, P2C-S, P2C-C, P2C-P, P2C-A, P1, and G2 remain not
authorized. G0 remains `NOT_READY`.

E1, E2, and E3 remain open. All I7 Evidence, Acceptance, Execution, Live,
and Exchange boundaries remain open and fail-closed.
