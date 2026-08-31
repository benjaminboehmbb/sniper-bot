# I7 R5-F2 V18 - P2B Path A A10 Test Validation Evidence

## 1. Classification and authority boundary

Classification:

`NONAUTHORITATIVE_P2B_TEST_VALIDATION_EVIDENCE_PROPOSAL`

This record reports locally observed A10 validation evidence only. It grants no Acceptance, Staging, Commit, Push, Publication, P2C, Execution, Live, or Exchange authority. No result in this record may be promoted into such authority by implication.

## 2. File-exact A10 base binding

| Binding | Value |
|---|---|
| Branch | `main` |
| HEAD | `47f0d450565ae3c791e0f0dd81726fad08752d0b` |
| main | `47f0d450565ae3c791e0f0dd81726fad08752d0b` |
| origin/main | `47f0d450565ae3c791e0f0dd81726fad08752d0b` |
| Tree | `2587a2a42520d2d0e84ef033c9ceae576ae11189` |
| Parent | `a67b3da6661512d0e9177cc30badb3aa5fab5989` |
| Index | empty |
| Tracked unstaged | 8 |
| Untracked before candidate creation | 86 |
| Working-tree records before candidate creation | 94 |

### 2.1 Pre-creation manifests

| Manifest | Format | SHA-256 | Bytes | Records/lines |
|---|---|---|---:|---:|
| Status | Git porcelain status record stream | `4e83069505f6cbd4d96d95828e16fa4abd7a8ee866009947babab1bd3e826361` | 7939 | 94 records |
| Worktree content | `<status2><TAB><whole-file-sha256><TAB><path><LF>`, paths sorted lexicographically | `7f32f271dd707ddd741293e81437cb99b6b0e532f1c0b1051dd57f7e489ed473` | 14049 | 94 lines |
| Untracked | `<whole-file-sha256><SPACE><bytes><SPACE><lines><SPACE><path><LF>`, paths sorted lexicographically | `192a7c6e39600cc640234efa0263dfdbf366574db1fa3f4645250e287ed93a2b` | 13820 | 86 lines |
| Path-A commit | canonical ten-path commit manifest | `9242b01517d80d686d43acb2d95b887bea5072022f166d14250f44f1d023969b` | 1405 | 10 lines |

## 3. P2B source identities and diff

| Path | SHA-256 | Bytes | Lines | Git status |
|---|---|---:|---:|---|
| `live_l1/state/paper_atomic_coordinator.py` | `b8ce5ba89016cac8e34ee2646f3bf9746b2909fa3b7c9e1ef6c74557c3aaffcb` | 262786 | 6020 | modified tracked unstaged |
| `live_l1/state/models.py` | `b9bc3b9a598fefeef83a2905432daf924ccf54e9701f313e2af99a6a8e833f53` | 5000 | 125 | modified tracked unstaged |
| `live_l1/state/state_store.py` | `b742131ba8af8e9c34157244de5cd743a045b7ae985dd4b502486e71fd2011c9` | 20999 | 594 | modified tracked unstaged |

For each source, A10 observed: mode `0444`; UID/GID `1000:1000`; device `2096`; regular file; link count `1`; UTF-8 without BOM; LF-only line endings; exactly one terminal LF.

The complete source diff covered exactly three files, 4695 insertions, and 3 deletions:

| Path | Insertions | Deletions |
|---|---:|---:|
| `live_l1/state/models.py` | 99 | 1 |
| `live_l1/state/paper_atomic_coordinator.py` | 4222 | 1 |
| `live_l1/state/state_store.py` | 374 | 1 |

`git diff --check` returned no finding.

## 4. Launcher-context incident

The first T1 invocation was mistakenly started outside `/home/benja/projects/sniper-bot`. Consequently, `unittest` could not find package `tests` and reported `ModuleNotFoundError: No module named 'tests'`, two unittest loader records, and exit code 1.

No repository test was loaded or executed, no repository module was imported, and no file was created or changed. Immediately afterward, the status identity remained `4e83069505f6cbd4d96d95828e16fa4abd7a8ee866009947babab1bd3e826361`, and the index remained empty.

The same authorized T1 scope was then run from the canonical repository and passed 77 tests with exit code 0. The incident is classified exactly as:

`NONTEST_LAUNCHER_CONTEXT_ERROR_RESOLVED`

It is neither a passing test nor a source-test failure and is excluded from the 260 passing repository tests.

## 5. A10 test-group results

### 5.1 P2B-T1 - coordinator tests

Correctly executed modules:

- `tests.live_l1.test_paper_atomic_coordinator`
- `tests.live_l1.test_paper_atomic_coordinator_v2`

| Tests | Failures | Errors | Skips | Exit code | Status |
|---:|---:|---:|---:|---:|---|
| 77 | 0 | 0 | 0 | 0 | PASS |

### 5.2 P2B-T2 - focused models/state-store tests

Exactly these methods were executed:

1. `tests.live_l1.test_paper_iu4_recovery_projection.I6ArtifactContractTests.test_legacy_risk_roundtrip_and_exact_types`
2. `tests.live_l1.test_paper_iu4_recovery_projection.I6ProjectionAndStoreTests.test_legacy_projection_store_create_read_replay_conflict`
3. `tests.live_l1.test_paper_iu4_recovery_projection.I6ProjectionAndStoreTests.test_state_store_parent_cleanup_preserves_primary_and_attempts_every_descriptor`
4. `tests.live_l1.test_paper_iu4_recovery_projection.I6ProjectionAndStoreTests.test_state_store_read_cleanup_classification_and_complete_cleanup_matrix`
5. `tests.live_l1.test_paper_iu4_recovery_projection.I6ProjectionAndStoreTests.test_state_store_target_primary_and_postterminal_write_cleanup_semantics`
6. `tests.live_l1.test_paper_iu4_recovery_projection.I6ProjectionAndStoreTests.test_legacy_projection_store_rejects_parent_symlink_before_creation`
7. `tests.live_l1.test_paper_iu4_recovery_projection.I6ProjectionAndStoreTests.test_legacy_projection_fd_chain_rejects_root_or_parent_swap_at_readback`
8. `tests.live_l1.test_paper_iu4_recovery_projection.I6ProjectionAndStoreTests.test_legacy_projection_target_identity_is_bound_during_all_readbacks`
9. `tests.live_l1.test_paper_iu4_recovery_projection.I6ProjectionAndStoreTests.test_schema1_models_and_state_store_behavior_remain_unchanged`

| Tests | Failures | Errors | Skips | Exit code | Status |
|---:|---:|---:|---:|---:|---|
| 9 | 0 | 0 | 0 | 0 | PASS |

### 5.3 P2B-T3 - Path-A dependency regression

Executed modules:

- `tests.live_l1.test_paper_artifacts_i6_dependencies`
- `tests.live_l1.test_loss_cluster_i6_transitions`
- `tests.live_l1.test_iu4_lifecycle_ledger`

| Tests | Failures | Errors | Skips | Exit code | Status |
|---:|---:|---:|---:|---:|---|
| 25 | 0 | 0 | 0 | 0 | PASS |

### 5.4 P2B-T4 - consumer/effect closure

Executed modules:

- `tests.live_l1.test_paper_iu4_adapter`
- `tests.live_l1.test_paper_iu4_adapter_v2`
- `tests.live_l1.test_paper_iu4_execution_seam_v2`
- `tests.live_l1.test_paper_iu4_startup_gate`
- `tests.live_l1.test_paper_iu4_shadow_runtime_gate`
- `tests.live_l1.test_paper_iu4_shadow_observation_gate`
- `tests.live_l1.test_paper_iu4_shadow_harness`
- `tests.live_l1.test_paper_iu4_replay_evidence`
- `tests.live_l1.test_paper_iu4_replay_pipeline`

| Tests | Failures | Errors | Skips | Exit code | Status |
|---:|---:|---:|---:|---:|---|
| 149 | 0 | 0 | 0 | 0 | PASS |

### 5.5 Repository-test aggregate

| Tests | Failures | Errors | Skips | Status |
|---:|---:|---:|---:|---|
| 260 | 0 | 0 | 0 | PASS |

This aggregate counts only repository tests actually executed in T1-T4 and excludes the resolved non-test launcher-context incident.

## 6. P2B-T5 - import closure

Only these modules were imported:

- `live_l1.state.paper_atomic_coordinator`
- `live_l1.state.models`
- `live_l1.state.state_store`
- `live_l1.state.paper_artifacts`
- `live_l1.state.loss_cluster`
- `live_l1.state.iu4_lifecycle_ledger`
- `live_l1.core.paper_economics`
- `live_l1.core.paper_entry_throttle`
- `live_l1.state.persist`

Result: exit code 0, PASS. No function was called and no runtime was started.

## 7. P2B-T6 - static closure

| Check | Result |
|---|---|
| `git diff --check` | PASS |
| Diff paths | exactly the three bound P2B source files |
| Path-A manifest SHA-256 | `9242b01517d80d686d43acb2d95b887bea5072022f166d14250f44f1d023969b` |
| Path-A manifest bytes/lines | 1405 / 10 |
| BOM check | PASS |
| CRLF check | PASS |
| terminal LF check | PASS |
| P2C scope overlap in possible three-source publication scope | 0 |
| Overall T6 status | PASS |

## 8. File-exact test-input identities

| Test input | SHA-256 |
|---|---|
| `tests/live_l1/test_paper_atomic_coordinator.py` | `a46f622f9a00e5db727ade04ece89b4deaf51347dc2d1f4d304532572b382753` |
| `tests/live_l1/test_paper_atomic_coordinator_v2.py` | `ec731c106ab23b78e482204e16d20826264cdf775f0c08c292a82bab1111ff8c` |
| `tests/live_l1/test_paper_iu4_recovery_projection.py` | `57a45dbf6b6bc56152c8c328c0d15992ab0345278cb6fa30667b6e902183e1c9` |
| `tests/live_l1/test_paper_artifacts_i6_dependencies.py` | `5a268abd386de90ec3ba1ce7c9b98f847494814ee66fc04d31c1fcc4e8caa53e` |
| `tests/live_l1/test_loss_cluster_i6_transitions.py` | `fff45d2dfa972a8a820a2a9deba4535927dea9847af54395153ee98fb69ecd13` |
| `tests/live_l1/test_iu4_lifecycle_ledger.py` | `f01c2eda7ceec56fad18acec20a09afaa187b4fd4850ab17a974e6bfe8200093` |
| `tests/live_l1/test_paper_iu4_adapter.py` | `b4947e4c03fa3b187e01c4005062337d1837b70d652243030581172dd4d2c339` |
| `tests/live_l1/test_paper_iu4_adapter_v2.py` | `f71d46700a1966534429281091da32e263ac479ddf1393c5021d015eac1cd1b3` |
| `tests/live_l1/test_paper_iu4_execution_seam_v2.py` | `fc61404d910fe76141cba8ba54f98ea6de552664a8b21bdaa50510e33f603755` |
| `tests/live_l1/test_paper_iu4_startup_gate.py` | `29d07a9c19aabcf369de101fd9599413a7f20ee03685eb96495993cad5588034` |
| `tests/live_l1/test_paper_iu4_shadow_runtime_gate.py` | `645634609464fb6d7d43c3b46d85292d48a2666f897d27b58fb2966c1fc43b05` |
| `tests/live_l1/test_paper_iu4_shadow_observation_gate.py` | `1309febdabfb4fac7a6fd800d312733f451485a95d705bcbea14d5bc8315f7aa` |
| `tests/live_l1/test_paper_iu4_shadow_harness.py` | `abea98dcecf65ff741fbe9951c5986d415085051b3dd27d6750553b475f6f3a5` |
| `tests/live_l1/test_paper_iu4_replay_evidence.py` | `d5a8580f44edac6997281bcc5aa3d3ea79bd1c7e5f07f24602b029cd2cf363e2` |
| `tests/live_l1/test_paper_iu4_replay_pipeline.py` | `7f89b7ff37ad603edcfe4cf9dd5d9f12ad8270b0725708b5619854f97e4a93f9` |

## 9. P2C separation

The following P2C module and test remained read-only test inputs:

| P2C input | SHA-256 | Classification |
|---|---|---|
| `live_l1/state/paper_iu4_recovery_projection.py` | `b12f3ece36dea4a83faddee5db43c1964884ba25a03bacaae476d22cdea77946` | P2C read-only test input |
| `tests/live_l1/test_paper_iu4_recovery_projection.py` | `57a45dbf6b6bc56152c8c328c0d15992ab0345278cb6fa30667b6e902183e1c9` | P2C read-only test input |

No P2C review, Acceptance, Staging, or Publication authority follows from their use in A10.

## 10. Non-authoritative later scope proposals

### 10.1 P2B-SOURCE-MODIFICATION-CANDIDATE

- `live_l1/state/paper_atomic_coordinator.py`
- `live_l1/state/models.py`
- `live_l1/state/state_store.py`

### 10.2 P2B-DIRECT-TEST-ADD-CANDIDATE

- `tests/live_l1/test_paper_atomic_coordinator_v2.py`

The test-add candidate is not automatically included in the source-staging scope. It requires its own independent review and staging decision.

The following untracked consumer tests remain outside the direct P2B source-publication scope:

- `tests/live_l1/test_paper_iu4_adapter_v2.py`
- `tests/live_l1/test_paper_iu4_execution_seam_v2.py`

They are derived consumer evidence and must not be published without their associated, currently excluded consumer source files. The P2C test remains wholly P2C-separated.

## 11. Unchanged closing state observed after A10

| Binding | SHA-256 | Bytes | Records/lines |
|---|---|---:|---:|
| Status | `4e83069505f6cbd4d96d95828e16fa4abd7a8ee866009947babab1bd3e826361` | 7939 | 94 records |
| Worktree content manifest | `7f32f271dd707ddd741293e81437cb99b6b0e532f1c0b1051dd57f7e489ed473` | 14049 | 94 lines |
| Untracked manifest | `192a7c6e39600cc640234efa0263dfdbf366574db1fa3f4645250e287ed93a2b` | 13820 | 86 lines |

The index was empty. A10 created no repository file, bytecode, coverage, log, or other test artifact. A10 performed no Git or network action.

This candidate is the single additional working-tree record created after A10. The required post-creation state is therefore: 8 tracked-unstaged records, 87 untracked records, 95 working-tree records, and an empty index. All prior 94 records remain excluded and unchanged.

## 12. Fail-closed decision and remaining gates

The recorded T1-T6 evidence is PASS within its explicitly bound validation scope. This evidentiary statement remains nonauthoritative and is not an Acceptance decision.

`G0: NOT_READY`

The following remain not authorized:

- P2B-S
- P2B-C
- P2B-P
- P2C
- P1
- G2

E1-E3 and every I7 Evidence, Acceptance, Execution, Live, and Exchange boundary remain open and fail-closed.

No Staging, Commit, Push, Publication, P2C, Execution, Live, or Exchange action is authorized by this candidate. Any later action requires a new, explicit, scope-exact human authorization based on an independent file-exact rereview.
