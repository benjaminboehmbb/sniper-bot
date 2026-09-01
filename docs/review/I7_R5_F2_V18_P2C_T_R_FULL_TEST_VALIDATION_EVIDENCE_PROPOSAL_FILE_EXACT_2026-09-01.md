# I7 R5-F2 V18 — P2C-T-R Full Test Validation Evidence Proposal

```text
CLASSIFICATION: NONAUTHORITATIVE_P2C_T_R_FULL_TEST_VALIDATION_EVIDENCE_PROPOSAL
P2C_T_R_FULL_TEST_VALIDATION_RESULT: PASS
P2C_T_R_FULL_TEST_VALIDATION_EVIDENCE_STATUS: NONAUTHORITATIVE_PROPOSAL
```

Date: 2026-09-01  
Repository: `/home/benja/projects/sniper-bot`

## 1. Status and authority boundary

This document records the observed result of one expressly authorized local,
isolated P2C-T-R validation. It is a nonauthoritative evidence proposal. It is
not an independent review, Acceptance, Publication, Execution, Live, or
Exchange authorization. No earlier decision is standalone file evidence for
this proposal.

```text
G0: NOT_READY
P2C_S_AUTHORIZED: NO
P2C_C_AUTHORIZED: NO
P2C_P_AUTHORIZED: NO
P2C_A_AUTHORIZED: NO
P1_AUTHORIZED: NO
G2_AUTHORIZED: NO
```

E1–E3 and every I7 Evidence, Acceptance, Execution, Live, and Exchange
boundary remain open and fail-closed.

## 2. Canonical pre-validation base

| Binding | Value |
|---|---|
| Branch | `main` |
| HEAD | `0fc004572c0359aeb89185f5fdc4ba2dedcd47ed` |
| main | `0fc004572c0359aeb89185f5fdc4ba2dedcd47ed` |
| origin/main | `0fc004572c0359aeb89185f5fdc4ba2dedcd47ed` |
| Index | empty |
| Tracked unstaged | 4 |
| Untracked before proposal creation | 85 |
| Worktree records before proposal creation | 89 |

### 2.1 NUL-terminated porcelain-v1 status identity

```text
SHA-256: 0daa5619b7a779283baf5655883c02bf8e119c1441244a1d8d0833b8c77f5885
Bytes: 7740
Records: 89
```

### 2.2 Path-sorted worktree-content manifest

Format: `<status2><TAB><sha256><TAB><path><LF>`.

```text
SHA-256: 79529c9911d888c4a9092dd9484ce41cb14a5cc00ac806a468a80be47b1d9545
Bytes: 13525
Lines: 89
```

### 2.3 Path-sorted untracked manifest

Format: `<sha256><SPACE><bytes><SPACE><lines><SPACE><path><LF>`.

```text
SHA-256: 453f074942afbffa6197ea50fe20a46c0f228f61747d793b35e8753449ec1b5a
Bytes: 13693
Lines: 85
```

## 3. File-exact P2C and prerequisite identities

| Role | Path | SHA-256 | Bytes | Lines | Mode | UID:GID | Device/Inode | Links | Type | Encoding/BOM | Terminal LF | Git/Base |
|---|---|---|---:|---:|---|---|---|---:|---|---|---|---|
| P2C implementation overlay | `live_l1/state/paper_iu4_recovery_projection.py` | `b12f3ece36dea4a83faddee5db43c1964884ba25a03bacaae476d22cdea77946` | 299085 | 6033 | `0444` | `1000:1000` | `2096/10750` | 1 | regular, not symlink | UTF-8/no BOM | exactly present | untracked/ABSENT |
| P2C test overlay | `tests/live_l1/test_paper_iu4_recovery_projection.py` | `57a45dbf6b6bc56152c8c328c0d15992ab0345278cb6fa30667b6e902183e1c9` | 255265 | 5307 | `0444` | `1000:1000` | `2096/10749` | 1 | regular, not symlink | UTF-8/no BOM | exactly present | untracked/ABSENT |

The published Startup-Gate prerequisite came from archived Base, not from a
worktree overlay:

| Path | SHA-256 | Git blob | Bytes | Lines |
|---|---|---|---:|---:|
| `live_l1/core/paper_iu4_startup_gate.py` | `c4a1854f3b200525568a40205b39e9ce2e14c342bb860569ba7fcfe5e9c063cd` | `f7da370d9f8e3538907cf14a91d39aa538bf3462` | 37668 | 919 |

The shared I6 evidence remains physically P2A-owned and was neither overlay
nor test target:

| Path | SHA-256 | Git blob | Bytes | Lines | Classification |
|---|---|---|---:|---:|---|
| `docs/review/PRE_IU4_I6_RECOVERY_MONITORING_PROJECTION_FILE_EXACT_IMPLEMENTATION_EVIDENCE_2026-08-20.md` | `5a733d7deb9d34633bea8718bda8e0749558810426e5985f8f3335b500789834` | `1c521838972b6455eba97019613712350aecb0c5` | 89983 | 1074 | `TRACKED_AT_BASE_P2A_PHYSICAL_OWNERSHIP_ONLY` |

This validation creates no P2C publication ownership for that I6 evidence.

## 4. Isolated construction

The single temporary root was:

```text
/tmp/i7-p2c-t-r.ab2FZw72
```

It was created with `mktemp -d` below `/tmp`. Before use, its realpath,
`/tmp` parent, `i7-p2c-t-r.` basename prefix, directory type, and non-symlink
property were checked. Separate `tree`, `tmp`, `pycache`, and `logs`
subdirectories were created below that bound root.

The isolated tree was extracted exclusively from a local `git archive` of:

```text
0fc004572c0359aeb89185f5fdc4ba2dedcd47ed
```

Exactly two canonical worktree files were copied as overlays:

1. `live_l1/state/paper_iu4_recovery_projection.py`
2. `tests/live_l1/test_paper_iu4_recovery_projection.py`

Their SHA-256, byte, and line identities were rechecked after copying. The
Startup-Gate file remained the archived Base blob and was rechecked against
its bound identity. No other tracked-unstaged or untracked canonical file was
copied into the isolated tree.

Execution used only:

```text
Interpreter: /home/benja/projects/sniper-bot/.venv/bin/python
PYTHONDONTWRITEBYTECODE: 1
PYTHONPATH: /tmp/i7-p2c-t-r.ab2FZw72/tree
TMPDIR: /tmp/i7-p2c-t-r.ab2FZw72/tmp
PYTHONPYCACHEPREFIX: /tmp/i7-p2c-t-r.ab2FZw72/pycache
Working directory: /tmp/i7-p2c-t-r.ab2FZw72/tree
```

## 5. Compilation and isolated origins

The seven compile targets were:

1. `live_l1/core/paper_iu4_startup_gate.py`
2. `live_l1/state/paper_atomic_coordinator.py`
3. `live_l1/state/models.py`
4. `live_l1/state/state_store.py`
5. `live_l1/state/paper_iu4_recovery_projection.py`
6. `tests/live_l1/test_paper_iu4_startup_gate.py`
7. `tests/live_l1/test_paper_iu4_recovery_projection.py`

| Compile RC | Targets | PYC files | PYC outside temporary prefix | Canonical compile artifacts |
|---:|---:|---:|---:|---:|
| 0 | 7 | 7 | 0 | 0 |

The following twelve modules were loaded bytecode-free from file origins
strictly beneath `/tmp/i7-p2c-t-r.ab2FZw72/tree`:

1. `live_l1.core.paper_iu4_startup_gate`
2. `live_l1.state.paper_iu4_recovery_projection`
3. `tests.live_l1.test_paper_iu4_startup_gate`
4. `tests.live_l1.test_paper_iu4_recovery_projection`
5. `live_l1.core.paper_economics`
6. `live_l1.core.paper_entry_throttle`
7. `live_l1.state.models`
8. `live_l1.state.state_store`
9. `live_l1.state.iu4_lifecycle_ledger`
10. `live_l1.state.loss_cluster`
11. `live_l1.state.paper_artifacts`
12. `live_l1.state.paper_atomic_coordinator`

No repository module loaded from the canonical dirty worktree or another
unbound origin.

## 6. Exact test results

| Test target | Tests | Failures | Errors | Skips | RC | Result | Runtime |
|---|---:|---:|---:|---:|---:|---|---:|
| `tests.live_l1.test_paper_iu4_startup_gate` | 12 | 0 | 0 | 0 | 0 | `OK` | 0.024 s |
| `tests.live_l1.test_paper_iu4_recovery_projection` | 88 | 0 | 0 | 0 | 0 | `OK` | 172.715 s |
| `tests.live_l1.test_paper_atomic_coordinator_v2` | 54 | 0 | 0 | 0 | 0 | `OK` | 0.786 s |
| `tests.live_l1.test_iu4_lifecycle_ledger` | 5 | 0 | 0 | 0 | 0 | `OK` | 0.003 s |
| `tests.live_l1.test_paper_atomic_coordinator` | 23 | 0 | 0 | 0 | 0 | `OK` | 0.072 s |
| `unittest discover -s tests/regression -p test_*.py` | 170 | 0 | 0 | 0 | 0 | `OK` | 1.661 s |

Exactly twelve `tests/regression/test_*.py` files matched before regression
execution. No complete `tests/live_l1` discovery and no unlisted suite ran.

```text
12 + 88 + 54 + 5 + 23 + 170 = 352
Tests: 352
Failures: 0
Errors: 0
Skips: 0
Test commands with RC 0: 6/6
Aggregate result: PASS
```

### 6.1 Expected failure-path output

The focused P2C suite emitted exactly twice:

```text
MemoryError: secondary target cleanup
```

Both emissions came from the deliberately exercised `close_during_primary`
failure path during `IU4ProjectionPublisherV1` destructor cleanup and were
reported as `Exception ignored while calling deallocator`. They were not
unittest Failures, Errors, or Skips. The same P2C command completed with RC 0,
88 tests, zero Failures, zero Errors, zero Skips, and final `OK`. These
observations grant no additional Acceptance or Runtime authority.

### 6.2 P2C test-class distribution

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

## 7. Explicit exclusions

The four tracked-unstaged foreign paths were not copied, imported, tested,
staged, or changed:

- `live_l1/core/execution.py`
- `live_l1/core/loop.py`
- `live_l1/core/paper_iu4_adapter.py`
- `live_l1/core/paper_iu4_shadow_runtime_gate.py`

Of the 85 pre-creation untracked records, only the two bound P2C files were
overlays. The remaining 83 untracked records were not copied, imported,
tested, staged, or changed. The P2A-owned I6 evidence was neither overlay nor
test target and gains no P2C publication ownership.

## 8. Post-test and cleanup attestation

After all six commands:

1. the temporary overlay and Base identities remained byte-exact;
2. all PYC, TMP, log, and test artifacts remained beneath the bound root;
3. no new canonical PYC, `__pycache__`, TMP, log, or test artifact appeared;
4. HEAD, main, and origin/main remained `0fc004572c0359aeb89185f5fdc4ba2dedcd47ed`;
5. the index remained empty;
6. all 89 canonical worktree records remained unchanged;
7. all three pre-validation manifest identities remained exact;
8. the I6 evidence remained at SHA-256 `5a733d7deb9d34633bea8718bda8e0749558810426e5985f8f3335b500789834`.

Before deletion, the temporary root was revalidated by realpath, `/tmp`
parent, basename prefix, directory type, and non-symlink property. Only
`/tmp/i7-p2c-t-r.ab2FZw72` was removed. It was subsequently absent, and the
set of other matching temporary paths was unchanged.

## 9. Final proposal decision

```text
P2C_T_R_FULL_TEST_VALIDATION_RESULT: PASS
P2C_T_R_FULL_TEST_VALIDATION_EVIDENCE_STATUS: NONAUTHORITATIVE_PROPOSAL
G0: NOT_READY
P2C_S_AUTHORIZED: NO
P2C_C_AUTHORIZED: NO
P2C_P_AUTHORIZED: NO
P2C_A_AUTHORIZED: NO
P1_AUTHORIZED: NO
G2_AUTHORIZED: NO
```

This proposal asserts no standalone Evidence, Acceptance, Publication,
Execution, Live, or Exchange authority. E1–E3 and all I7 Evidence,
Acceptance, Execution, Live, and Exchange boundaries remain open and
fail-closed.
