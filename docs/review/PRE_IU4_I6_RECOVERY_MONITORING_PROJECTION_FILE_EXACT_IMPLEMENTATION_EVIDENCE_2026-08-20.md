# Pre-IU4 I6 Recovery, Monitoring and Projection — File-Exact Implementation Evidence — 2026-08-20

## 1. Result and authorization boundary

```text
WORKSTREAM:IU4-I6-REREVIEW-14-RESOLUTION
I6_RESULT:PASS
I6_IMPLEMENTATION_COMPLETE:YES
I6_INDEPENDENT_ACCEPTANCE:NOT_YET_PERFORMED
IMPLEMENTATION_REREVIEW_1_RESULT:NOT_READY
IMPLEMENTATION_REREVIEW_1_BLOCKERS_RESOLVED:B1,B2,B3,B4,B5,B6
IMPLEMENTATION_REREVIEW_2_RESULT:NOT_READY
IMPLEMENTATION_REREVIEW_2_BLOCKERS_RESOLVED:B1,B2,B3,B4
IMPLEMENTATION_REREVIEW_3_RESULT:NOT_READY
IMPLEMENTATION_REREVIEW_3_BLOCKERS_RESOLVED:B1,B2,B3,B4,B5
IMPLEMENTATION_REREVIEW_4_RESULT:NOT_READY
IMPLEMENTATION_REREVIEW_4_BLOCKERS_RESOLVED:B1,B2,B3,B4
IMPLEMENTATION_REREVIEW_5_RESULT:NOT_READY
IMPLEMENTATION_REREVIEW_5_BLOCKERS_RESOLVED:B1,B2,B3,B4
IMPLEMENTATION_REREVIEW_6_RESULT:NOT_READY
IMPLEMENTATION_REREVIEW_6_RESOLUTION_STATUS:PARTIAL_B1_B3_B4_SUPERSEDED_BY_REREVIEW_7
IMPLEMENTATION_REREVIEW_7_RESULT:NOT_READY
IMPLEMENTATION_REREVIEW_7_RESOLUTION_STATUS:PARTIAL_B1_B3_SUPERSEDED_BY_REREVIEW_8_B4_PRESERVED
IMPLEMENTATION_REREVIEW_8_RESULT:NOT_READY
IMPLEMENTATION_REREVIEW_8_RESOLUTION_STATUS:B3_PRESERVED_B1_SUPERSEDED_BY_REREVIEW_9
IMPLEMENTATION_REREVIEW_9_RESULT:NOT_READY
IMPLEMENTATION_REREVIEW_9_BLOCKERS_RESOLVED:B1
IMPLEMENTATION_REREVIEW_10_RESULT:NOT_READY_B1_B2_B3
IMPLEMENTATION_REREVIEW_10_BLOCKERS_RESOLVED:B1
IMPLEMENTATION_REREVIEW_11_RESULT:NOT_READY_HIGH_B1_TYPE_CANONICALITY_AND_SERIALIZATION_AUTHORITY
IMPLEMENTATION_REREVIEW_11_BLOCKERS_RESOLVED:B1,B2,B3
IMPLEMENTATION_REREVIEW_12_RESULT:RESOLUTION_IMPLEMENTED_AWAITING_INDEPENDENT_READONLY_FILE_EXACT_REREVIEW
IMPLEMENTATION_REREVIEW_12_BLOCKERS_RESOLVED:HIGH_B1_TYPE_CANONICALITY,HIGH_B1_SERIALIZATION_AUTHORITY
IMPLEMENTATION_REREVIEW_13_RESULT:RESOLUTION_IMPLEMENTED_AWAITING_INDEPENDENT_READONLY_FILE_EXACT_REREVIEW
IMPLEMENTATION_REREVIEW_13_BLOCKERS_RESOLVED:HIGH_B1_EXACT_TYPE_BOUNDARY,HIGH_B1_NONREPLACEABLE_REPORT_AUTHORITY,MEDIUM_EVIDENCE_SELF_BINDING
IMPLEMENTATION_REREVIEW_14_RESULT:RESOLUTION_IMPLEMENTED_AWAITING_INDEPENDENT_READONLY_FILE_EXACT_REREVIEW
IMPLEMENTATION_REREVIEW_14_BLOCKERS_RESOLVED:HIGH_B1_B_INHERITED_FACTORY_EXACT_TYPE_BOUNDARY
OPERATIONAL_ENFORCED_START_AUTHORIZED:NO
ACTIVE_V2_CONSUMER_AUTHORIZED:NO
I7_AUTHORIZED:NO
I8_AUTHORIZED:NO
ENFORCED_ACTIVATION_AUTHORIZED:NO
EXCHANGE_AUTHORIZED:NO
LIVE_AUTHORIZED:NO
```

The implementation is offline and synthetically exercised only. It creates no
Runtime Session, operational owner, live caller, launcher branch or active V2
consumer. Independent acceptance remains a separate read-only workstream.

## 2. Controlling identities

```text
CANONICAL_REPOSITORY:/home/benja/projects/sniper-bot
BRANCH:main
HEAD:c7ce0452aa2ccbf08c462784d68fa07b3dfe9595
MAIN:c7ce0452aa2ccbf08c462784d68fa07b3dfe9595
ORIGIN_MAIN:89e13fecd1ab549ca7099818b1c9ad4984cb6f7a
MAIN_AHEAD_OF_ORIGIN:6
MAIN_BEHIND_ORIGIN:0
MANDATE_SHA256:9d9bdacb5f907f9e9927dc7c7d3ecec25718ccb448b6f69acff0ad6baf1a4dc6
MANDATE_LINES:1281
MANDATE_READY_REREVIEW_SHA256:f5cd16f783322f18b98475fa9912183bc4d1f960e147eee1e1065f3aba58f9fe
MANDATE_READY_REREVIEW_LINES:268
MANDATE_READY_REREVIEW_RESULT:READY_0_0_0_0
R21_SHA256:ab8f80720a1d8fe49b9085bce63658bcaecf7f0a3ea70fb555559223090824e0
R21_LINES:4605
I2_FINAL_REREVIEW_SHA256:5a59ad8c97ebae85148661fe0e3bedab643c7f12ae2c8d4e87272447c0616679
I2_FINAL_REREVIEW_LINES:300
I3_FINAL_EVIDENCE_SHA256:20846284ffad9e8b755dd6a3b74f963d8d2c6ee1519fafdd0bc1275f2e33c390
I3_FINAL_EVIDENCE_LINES:463
I3_FINAL_REREVIEW_SHA256:03790420534e38c7e36d1824a472dfd80763340dacec8847ddf5072d55db0c9f
I3_FINAL_REREVIEW_LINES:191
I4_FINAL_EVIDENCE_SHA256:068c2ba2661031843a13dd3f2c4684f9340f432b90b192b6b7492dae8968270d
I4_FINAL_EVIDENCE_LINES:403
I4_FINAL_REREVIEW_SHA256:c6d8bbcb35572a364b74a47eb9ad817240a8b0cce70e514942bb674d3861c38b
I4_FINAL_REREVIEW_LINES:191
I5_CORRECTED_MANDATE_SHA256:a688773cc10dd6c573e7c019245639c010a3b0abb49fb301249aeebeba182a91
I5_CORRECTED_MANDATE_LINES:633
I5_FINAL_EVIDENCE_SHA256:33d18b64bc92d0f5631d3a8306010e8889bb69085d7ce4e77c36c1fd1e185b65
I5_FINAL_EVIDENCE_LINES:633
I5_FINAL_REREVIEW_SHA256:9031ec6ef31d61787d46082dab50c59823bb0ba45155cba2b9abc5928f6d96d9
I5_FINAL_REREVIEW_LINES:246
I6_IMPLEMENTATION_REREVIEW_1_SHA256:0739d61170dc84a8e1cd4d1adb78c5941560d25855c7a676f6072ebf836d3cbd
I6_IMPLEMENTATION_REREVIEW_1_LINES:191
I6_IMPLEMENTATION_REREVIEW_1_RESULT:NOT_READY_B1_B2_B3_B4_B5_B6
I6_IMPLEMENTATION_REREVIEW_2_RESULT:NOT_READY_B1_B2_B3_B4
I6_IMPLEMENTATION_REREVIEW_2_SEPARATE_ARTIFACT:NOT_CREATED_READONLY_RESULT_REPORTED_IN_TASK
I6_IMPLEMENTATION_REREVIEW_3_RESULT:NOT_READY_B1_B2_B3_B4_B5
I6_IMPLEMENTATION_REREVIEW_3_SEPARATE_ARTIFACT:NOT_CREATED_READONLY_RESULT_REPORTED_IN_TASK
I6_IMPLEMENTATION_REREVIEW_4_RESULT:NOT_READY_B1_B2_B3_B4
I6_IMPLEMENTATION_REREVIEW_4_SEPARATE_ARTIFACT:NOT_CREATED_READONLY_RESULT_REPORTED_IN_TASK
I6_IMPLEMENTATION_REREVIEW_5_RESULT:NOT_READY_B1_B2_B3_B4
I6_IMPLEMENTATION_REREVIEW_5_SEPARATE_ARTIFACT:NOT_CREATED_READONLY_RESULT_REPORTED_IN_DELEGATED_TASK
I6_IMPLEMENTATION_REREVIEW_6_RESULT:NOT_READY_B1_B3_B4
I6_IMPLEMENTATION_REREVIEW_6_SEPARATE_ARTIFACT:NOT_CREATED_READONLY_RESULT_REPORTED_IN_DELEGATED_TASK
I6_IMPLEMENTATION_REREVIEW_7_RESULT:NOT_READY_B1_B3_B4
I6_IMPLEMENTATION_REREVIEW_7_SEPARATE_ARTIFACT:NOT_CREATED_READONLY_RESULT_REPORTED_IN_DELEGATED_TASK
I6_IMPLEMENTATION_REREVIEW_8_RESULT:NOT_READY_B1_B3
I6_IMPLEMENTATION_REREVIEW_8_SEPARATE_ARTIFACT:NOT_CREATED_READONLY_RESULT_REPORTED_IN_DELEGATED_TASK
I6_IMPLEMENTATION_REREVIEW_9_RESULT:NOT_READY_B1
I6_IMPLEMENTATION_REREVIEW_9_SEPARATE_ARTIFACT:NOT_CREATED_READONLY_RESULT_REPORTED_IN_DELEGATED_TASK
I6_IMPLEMENTATION_REREVIEW_10_RESULT:NOT_READY_B1_B2_B3
I6_IMPLEMENTATION_REREVIEW_11_RESULT:NOT_READY_HIGH_B1_TYPE_CANONICALITY_AND_SERIALIZATION_AUTHORITY
I6_IMPLEMENTATION_REREVIEW_12_RESULT:RESOLUTION_IMPLEMENTED_AWAITING_INDEPENDENT_READONLY_FILE_EXACT_REREVIEW
I6_IMPLEMENTATION_REREVIEW_13_RESULT:NOT_READY_HIGH_B1_B_INHERITED_FACTORY_EXACT_TYPE_BOUNDARY
I6_IMPLEMENTATION_REREVIEW_14_RESULT:RESOLUTION_IMPLEMENTED_AWAITING_INDEPENDENT_READONLY_FILE_EXACT_REREVIEW
```

## 3. Exact six-path scope

### 3.1 Mandate-time boundary

| Operation | Path | Start identity |
|---|---|---|
| MODIFY | `live_l1/state/paper_atomic_coordinator.py` | `446ae8712d09bc52f950587a2e3ecec0c60fd21b3c9150a8886af1b3b2b4f9ec`, 5,796 |
| MODIFY | `live_l1/state/models.py` | `3254d2f1a6509ec5f8f623dd8f286f60cfcc108f66f2d8eb107338d795115c7e`, 27 |
| MODIFY | `live_l1/state/state_store.py` | `50a85cf6bd382850d39e69cd785a5dc2ded0a66a1d82856b4baa11877bdba177`, 220 |
| CREATE | `live_l1/state/paper_iu4_recovery_projection.py` | worktree absent; HEAD absent |
| CREATE | `tests/live_l1/test_paper_iu4_recovery_projection.py` | worktree absent; HEAD absent |
| CREATE | this Evidence record | worktree absent; HEAD absent |

All three CREATE paths had both worktree and `HEAD:path` absence at the start.

### 3.2 Final five non-Evidence identities

| Path | Final SHA-256 | Lines |
|---|---|---:|
| `live_l1/state/paper_atomic_coordinator.py` | `b8ce5ba89016cac8e34ee2646f3bf9746b2909fa3b7c9e1ef6c74557c3aaffcb` | 6,020 |
| `live_l1/state/models.py` | `b9bc3b9a598fefeef83a2905432daf924ccf54e9701f313e2af99a6a8e833f53` | 125 |
| `live_l1/state/state_store.py` | `b742131ba8af8e9c34157244de5cd743a045b7ae985dd4b502486e71fd2011c9` | 594 |
| `live_l1/state/paper_iu4_recovery_projection.py` | `b12f3ece36dea4a83faddee5db43c1964884ba25a03bacaae476d22cdea77946` | 6,033 |
| `tests/live_l1/test_paper_iu4_recovery_projection.py` | `57a45dbf6b6bc56152c8c328c0d15992ab0345278cb6fa30667b6e902183e1c9` | 5,307 |

No seventh I6 path was created or modified. This Evidence file's whole-file
identity is intentionally not self-claimed; it must be calculated externally.

## 4. Implemented contract surface

### 4.1 Additive Legacy and State Store boundary

- `LegacyRiskStateS4ProjectionV1` is frozen and complete for kill, cooldown,
  daily trades/loss, anomaly count, six-hour trades, last trade and reasons.
- It rejects bool-as-int, missing/unknown fields, duplicate reasons, nonfinite
  and noncanonical Decimal strings.
- Schema-1 `PositionStateS2`, `RiskStateS4`, `load_or_init_state` and
  `persist_state` retain their established behavior.
- Projection helpers use canonical create-new/readback bytes and accept only an
  identical replay. They are not called by Schema-1 recovery.

### 4.2 Content-addressed artifacts

| Artifact | Strict result |
|---|---|
| `IU4LegacySafetySnapshotV1` | exact schema/type/components/fingerprints; absolute source path; OPEN Position consistency; complete S4 required |
| `IU4StateHandoffManifestV1` | both directions; monotone Owner; exact mapping field set; source/target/schema/Generation/Approval bindings |
| `IU4CleanGenesisManifestV1` | PEE/FLAT/sequence-0/EMPTY; exact profiles/components and derived absence/inventory proofs |
| `IU4CompatibilityProjectionV1` | exact projected Snapshot path/bytes/Generation and canonical target hash; `non_authoritative_projection=true` |
| `IU4PersistenceWorkerDeathTrustAnchorV1` | exact prebound attestor/collector/Approval/registry/window |
| `IU4PersistenceWorkerExclusionProofV1` | PROCESS_DEATH only; PIDFD exit, waitid reap, closed handle, zero holders |
| `IU4ProjectionCursorV1` | immutable base; exact previous+1 ancestry/link/output/inventory |
| `IU4TerminalMonitoringObservationV1` | exact top-level plus twelve exact nested groups |
| `IU4TerminalRuntimeProfileAnchorV1` | exact content-addressed profile ID/static-binding anchor |
| `IU4TerminalRuntimeProfileRegistryV1` | immutable exact-anchor tuple and strict transport parser; explicitly untrusted as caller input |
| private `IU4TerminalRuntimeProfileTrustRootV1` | separately provisioned frozen/content-addressed Registry capability, never built from Report-caller facts |
| `IU4RecoveryMonitoringReportV1` | exact twelve results, complete content-addressed Observation record, embedded provisioned Anchor bytes/Registry binding, Close reconstruction, sentinel matrix and derived overall/capabilities/reasons; code-literal Report fields and recursively immutable nested raw storage |

All use exact primitive types, exact field sets, canonical JSON, content IDs
and fingerprints. `from_record()` requires equality with canonical
`to_record()` bytes after parsing.

Fixed vectors proven by the focused suite include:

```text
LEGACY_SNAPSHOT_ID:IU4-LEGACY-SAFETY-SNAPSHOT-V1-a7fa73618fdafe0542ac15da62667c585f60a0bca887d24e5f8090c749d8e2ee
LEGACY_SNAPSHOT_FP:8b4431737ba7f9dc2627f35aaee7326e5b433f86b7065ed39b6c70e130135257
DEATH_ANCHOR_FP:26780ee1d2dab5311e437e4da32e22a56fac26afec10c16b1aefbda033bf7619
DEATH_PROOF_FP:6073ff2e953bd69d6ecefa9417e7b1b2fbb7e204474727383405b6911cadffb2
OBSERVATION_FP:a151ff36e360960b4c8483dff1827e616e04055860e4bfbc34ef583117495bb6
TERMINAL_STATIC_BINDINGS_FP:842946705cc9fca3cb2b83beddd819ff48ea95cec6fecef153eb052e6e69285c
REPORT_FP:94e9d0e5526b0e46442ea361cae623d38f25918d14be715a41a9573d18e52462
OBSERVATION_CANONICAL_BYTES:13704
REPORT_CANONICAL_BYTES:18600
```

### 4.3 Owner, Genesis and Handoff matrix

| Owner | Legacy | Atomic | Result |
|---|---|---|---|
| LEGACY | OPEN | FLAT | `LEGACY_EXIT_ONLY` |
| LEGACY | OPEN | OPEN | `PEE_IU4_HANDOFF_DUAL_OPEN_CONFLICT` |
| LEGACY | FLAT | FLAT | `HANDOFF_REQUIRED` |
| LEGACY | FLAT | OPEN | `PEE_IU4_HANDOFF_OWNER_EPOCH_INVALID` |
| PEE | FLAT | OPEN | `PEE_RESUME_CANDIDATE` |
| PEE | FLAT | FLAT | `PEE_FLAT_CANDIDATE` |
| PEE | OPEN | OPEN/FLAT | `PEE_IU4_HANDOFF_OWNER_EPOCH_INVALID` |
| any | corrupt/missing/unknown | any | `PEE_IU4_HANDOFF_GENESIS_REQUIRED` |

DIRECT Atomic Genesis executes PREPARE → exact target → read-only readback →
COMMIT. Owner changes only at COMMIT. Identical committed readback is
idempotent. The focused grid covers before/after PREPARE, before target,
after target replace/file-sync/directory-sync, after reconciliation,
before COMMIT and after COMMIT. An open Genesis PREPARE is completed only with
a fresh exact `COMPLETE_AUTHORITY_PREPARE` Authorization, one Consumption and
one `RECOVERY_MATERIALIZATION`; the outcome is restart-only.

Both `LEGACY_TO_PEE` and `PEE_TO_LEGACY` are exercised with monotone Owner,
self-reference-free planned Generation, target readback, exact COMMIT and
idempotent committed readback. PREPARE alone never changes Owner.

### 4.4 Recovery and Authority ancestry

- `i6_validate_authority_root` walks from the committed sequence-0 target
  through every journal transition and rejects a foreign root without writes.
- `i6_materialize_durable_head` writes only an already durable `state_after`;
  it creates no transaction and performs no business redecision.
- Restart authority is exact-type, time-, Coordinator-, Ledger-tip-,
  Generation- and pre-State-bound and is consumed exactly once.
- `RECOVER_AND_RESTART` appends one bound materialization result and returns
  `RECOVERY_COMPLETE_LOOP_NOT_AUTHORIZED`.
- A consumed Authorization cannot be reused.

### 4.5 Terminal Gap and Worker exclusion

The only accepted proof mode is `PROCESS_DEATH`. Positive validation requires
prebound anchor ID/fingerprint, Approval, registry, attestor type/ID/executable,
collector/source Evidence, boot, Session/OPEN, Authority, Coordinator, journal
root, Worker, validity window, PIDFD exit, waitid reap, closed append handle and
zero surviving holders. Higher-token/fencing modes, booleans, lookalikes,
live/unreaped Worker or any surviving holder reject before mutation.

Terminal reconciliation validates journal ancestry before Snapshot. With the
Coordinator root lock already held, it acquires and retains the Lifecycle
writer lock across the final consumed-tip/Session check, exact KILL
reuse/append, post-KILL recheck and canonical create-new Gap append/readback.
Therefore a Lifecycle extension before lock acquisition rejects before any
KILL, while an extension after acquisition cannot interleave. The operation
never evaluates a market snapshot, exits a position or starts a Loop. The
focused tests prove one KILL and one Gap on success, and zero KILL/transactions
for the explicit foreign-extension-before-lock case.

### 4.6 Projection protocol and fault outcomes

Projection accepts one exact Atomic transaction at a time. It lexically
validates the absolute NFC caller root, traverses it once from `/` with
`O_DIRECTORY|O_NOFOLLOW`, binds the caller directory identity, and thereafter
uses only held directory FDs plus relative `dir_fd` operations. No
security-relevant operation re-resolves the caller, projection or records
absolute path. The layout remains:

```text
projection/.projection_v1.lock
projection/records/{sequence_20_digits}_{projection_id}.json
projection/.projection_cursor_v1.tmp.{operation_attempt_id}
projection/projection_cursor_v1.json
```

The root digest domain is exactly
`b"IU4_PROJECTION_ROOT_V1\x00" + projection_root_path.encode("utf-8", "strict")`.
Inventory entries are projection-root-relative `records/...`, UTF-8-byte
sorted, regular-file/mode/size/SHA tuples. Lock, final Cursor and exact current
temp are excluded at the fixed post-output-readback observation point.

| Fault boundary | Immediate durable state | Retry/final |
|---|---|---|
| before output create | no output, no Cursor | one output + Cursor |
| after output create | output possible, no Cursor | exact output readback + Cursor |
| after output file sync | synced output, no Cursor | one Cursor |
| after output directory sync | durable output, no Cursor | one Cursor |
| after output readback | exact output, no Cursor | one Cursor |
| after inventory | exact output/inventory, no Cursor | one Cursor |
| after Cursor temp create | exact temp, no final Cursor | same temp validated and replaced |
| after Cursor file sync | synced temp | atomic replace + readback |
| after Cursor replace | final Cursor present | identical replay |
| after Cursor directory sync | durable Cursor | identical replay |
| after Cursor readback | complete publication | identical replay |

All eleven rows end with one record, one Cursor and unchanged Atomic
Journal/State. Output-only crash advances only the exact matching Cursor.
Cursor-without-output, skip, gap, ahead, rollback, divergent same sequence,
wrong previous link, unsafe root and inventory corruption fail closed.
Two transactions catch up strictly 1 then 2; tip-only publication is rejected.
Disk-full, permission, FD exhaustion, MemoryError and nested RuntimeError
resource causes classify as `PEE_IU4_RESOURCE_EXHAUSTED`. Lock-unlock and
lock-close failure after a durable record/Cursor return the same stable code;
the record/Cursor remain exact and an identical retry creates no duplicate.
Deterministic caller/parent swaps immediately before `mkdir`, `open` and
`replace` mutate only the held caller-root inode and create nothing below the
outside symlink target.

### 4.7 Twelve-group monitoring matrix

| # | Group | Positive contract | Negative result |
|---:|---|---|---|
| 1 | role readiness | exact three roles/IDs/PIDs/start times/owners | FAIL / guardian invalid |
| 2 | lease/self death | PIDFD lease, armed BOOTTIME SIGKILL timer | FAIL / guardian invalid |
| 3 | PIDFD targets | exact target PID/start and PASS probes | FAIL / guardian invalid |
| 4 | control word/memfd | schema 3, closed state/right enums, CAS order | FAIL / control conflict |
| 5 | signal envelope | exact identities, wait-killable and locked | FAIL / signal invalid |
| 6 | runtime channels | exactly six, peer/rights/queue/OFD/lock | FAIL / channel invalid |
| 7 | seccomp/LSM | Broker listener, receive state, frozen maps, scalar matrix | FAIL / capability invalid |
| 8 | close FSM | exact phase/status/owner enum and consistency | FAIL / close family |
| 9 | heartbeat/budgets | 10/25/5/5/25/100 and latch 1..100 ms | FAIL / guardian invalid |
| 10 | failstop/Gap/Liveness | endpoint/inode/capacity/empty/HUP/fallback | FAIL / failstop pending |
| 11 | completion provenance | mutually exclusive DIRECT/RECOVERED fields | FAIL / Genesis provenance |
| 12 | safety/resource/schema | per-field exact enum/type/version/capability matrix | FAIL/WARN as specified |

The focused matrix flips every group independently and proves the exact named
result becomes FAIL without caller-supplied group results. A separately
provisioned exact content-addressed profile registry additionally binds role ownership, PID targets,
memfd/seal values, channel identities, seccomp/LSM coverage, close owners,
budget constants, Liveness endpoints, completion identity and schema versions.
The report call no longer accepts caller-selected expected-static, trusted-
profile or Runtime-profile fingerprints. The Close group embeds its exact
source record and reconstructs `CLOSE_TIMEOUT`, `CLOSE_TRANSPORT_FAILED`,
`CLOSE_INCOMPLETE` or `CLOSE_PROTOCOL_INVALID` rather than trusting a caller
reason.
Unknown enums, nested unknown fields, bool-as-int and malformed primitives
reject at schema.
Heartbeat/capability ages cover 0, 25, -1 and 26; latch covers 1, 100, 0 and
101. DIRECT first-start requires nonce match, zero prior Session and explicit
eligibility.

Report sentinel rows proven:

- Session absent is exactly `NONE/NONE` with `ABSENT`; present requires ID/hex.
- Manifest absent is exactly `NONE/NONE` only for LEGACY/MONITOR_ONLY/no PREPARE.
- Cursor absent is exactly `NONE/NONE/0/EMPTY`; present requires ID/hex/>0/hex.
- Every mixed pair and sequence/head mismatch rejects before report creation.
- Positive Projection lag yields WARN, reason `PEE_IU4_PROJECTION_LAG`, and
  Entry BLOCKED; ahead Cursor rejects.
- Root/Session/Lifecycle/group failures dominate lag/profile warnings.

### 4.8 Rereview-1 blocker resolution

| Blocker | File-exact resolution | Executed proof |
|---|---|---|
| B1 | Legacy Position/S4/Loss/Throttle/Cursor records now have exact field sets, exact primitives, canonical Decimal/time values, embedded fingerprints and cross-fingerprint equality. Genesis parses the complete `AtomicPaperStateV2` and binds exact profiles, components, paths, absence proofs and inventory. Handoff/Compatibility validate IDs, hex commits, paths and cross-bindings. | Self-consistently refingerprinted incomplete Legacy and Genesis artifacts reject; unknown/missing/bool/noncanonical/tamper and canonical round-trip rows pass. |
| B2 | Genesis is checked against the real Coordinator, target State, profiles, components, paths and absence/inventory before PREPARE. Handoff binds repository/operator/Coordinator/System/Symbol, direction-specific source and target paths/bytes/business/core, current Authority root and every mapping field before mutation. Restart requires explicit trusted operator, commit, logs, environment, last-state time and Startup attempt plus exact profiles, Ledger tip, Authority root and State triple. Resource exceptions are mapped to `PEE_IU4_RESOURCE_EXHAUSTED`. | Foreign Genesis and Handoff targets leave Ledger/State unchanged; all ten mapping fields and sixteen independent Restart trust/State divergences reject before Consumption; both directions and nine Handoff boundaries pass. |
| B3 | Terminal proof is bound to the exact accepted Runtime Session OPEN event/fingerprint/session/head. Coordinator root lock encloses Lifecycle resolution, Consumption, exact terminal KILL reuse/materialization and Gap append, with Lifecycle revalidation before and after KILL. Existing KILL reuse requires exact event/time/tick/proof/reason/EMERGENCY identity. | Forged OPEN and unrelated KILL reject. Eight isolated Terminal boundaries preserve exact Ledger/Journal/State/Session identities; post-KILL retry needs fresh authority and reuses exactly one KILL. |
| B4 | Derived projection root, records root and lock are confined and symlink-checked before any directory mutation. Inventory accepts only exact projection filenames and fully parsed projection records. Same-sequence replay recomputes and binds the current inventory. | Derived-root symlink causes no outside `records/` creation; injected `EVIL.json`, missing output and divergent replay reject; complete eleven-boundary publication/CAS grid and one-by-one catch-up pass. |
| B5 | Observation recursively validates every ID, SHA, integer/bool boundary and exact nested shape. Report binds Session OPEN, Authority root and Atomic root to trusted expected values, closes Terminal-Gap enums, derives group results/reasons and forces Entry BLOCKED on every hard failure. | Empty nested IDs, non-SHA values, unknown enums, bool subclasses, twelve independently failed groups, numeric boundary-1/boundary/boundary+1, sentinel, precedence and hard-FAIL capability rows pass. |
| B6 | The focused suite was expanded from the reviewed 34 cases to 42 test methods with parameterized full-row matrices. Evidence is regenerated only from the fresh final run and names the exact tested rows, not the rejected pre-resolution outputs. | 42/42 focused, 533/533 full Live and 170/170 Regression PASS with zero failures/errors/skips. |

### 4.9 Rereview-2 blocker resolution

| Blocker | File-exact resolution | Executed proof |
|---|---|---|
| B1 | Every previously self-consistent incomplete artifact is now cross-bound: Legacy source path and OPEN S2 time/size/side/price, nonempty Trust approval, exact Handoff mapping fields and direction/schema/source Generation, projected Snapshot path/bytes/Generation/target hash, and exact Genesis profiles/components/absence/inventory. | Six explicit self-refingerprinted adversarial rows reject during artifact construction; the canonical round-trip/fixed-vector matrix remains stable. |
| B2 | Terminal reconciliation now holds the accepted Lifecycle Ledger writer lock across pre-KILL tip/Session validation, Atomic KILL, post-KILL validation and canonical Gap append/readback, nested below the Coordinator root lock. | A foreign `RECOVERY_MATERIALIZATION` injected after Consumption and before Lifecycle-lock acquisition rejects with `PEE_IU4_LIFECYCLE_EXTENSION_INVALID`; Atomic transaction count remains 0 and kill level remains `NONE`. |
| B3 | Monitoring binds static terminal facts to a trusted fingerprint and derives cross-group Owner/PIDFD, OPEN-close, clean-failstop, DIRECT/RECOVERED provenance, owner-specific Legacy-exit and operation-specific Restart-Authorization semantics. | Wrong role, PID target, memfd flags and LSM coverage reject at the trust boundary; forged OPEN-close ID, asserted failstop, ambiguous recovered provenance, PEE/ACTIVE Legacy exit and recovery with `NOT_REQUIRED` Authorization produce hard FAIL. |
| B4 | The recorded Rereview-1 identity was corrected from the inaccurate `0739d611b905...` value to the independently recomputed whole-file SHA-256 `0739d61170dc84a8e1cd4d1adb78c5941560d25855c7a676f6072ebf836d3cbd`. | `sha256sum` and `wc -l` report the exact 191-line Rereview-1 artifact; no nonexistent Rereview-2 file identity is claimed. |

Rereview-2 resolution row totals added to the focused module:

```text
SELF_CONSISTENT_ARTIFACT_REJECTION_ROWS:6
TRUSTED_STATIC_MONITORING_REJECTION_ROWS:4
DYNAMIC_MONITORING_HARD_FAIL_ROWS:5
TERMINAL_FOREIGN_EXTENSION_BEFORE_LOCK_ROWS:1
TERMINAL_FOREIGN_EXTENSION_KILL_TRANSACTIONS:0
```

### 4.10 Rereview-3 blocker resolution

| Blocker | File-exact resolution | Executed proof |
|---|---|---|
| B1 | A FLAT Legacy Position now requires `entry_timestamp_utc=NONE`. Retained Throttle events require the exact `AcceptedEntryEventV1` field set, canonical parsing, policy binding, unique IDs, contiguous sequence/predecessor ancestry, monotone timestamps and exact count/head/day consistency. | A self-refingerprinted FLAT record with a concrete entry timestamp and a self-refingerprinted untyped Throttle event both reject during Snapshot construction. |
| B2 | Control-word/memfd flags, seals and mapping rights plus exact LSM hook coverage are derived group invariants. The close FSM now enforces phase-specific channel, evidence-ID and status tuples. Report reason codes are derived in one shared ordered function and exact-equality checked during reconstruction. | COMMITTED with three `NONE` evidence IDs produces group FAIL; a PASS report rebuilt with `ARBITRARY_REASON` rejects. |
| B3 | The trusted terminal static-bindings fingerprint must equal both the recomputed Observation binding and the trusted Runtime-profile fingerprint. A caller cannot replace the expected value to bless altered static facts. | A wrong same-shape memfd flag with a caller-recomputed expected static fingerprint rejects with `PEE_IU4_TERMINAL_CAPABILITY_ENVELOPE_INVALID`. |
| B4 | Legacy projection parents are traversed from `/` one component at a time through directory FDs with `O_DIRECTORY|O_NOFOLLOW`; missing components are created only below already verified descriptors. Targets are opened relative to the verified parent with `O_NOFOLLOW` and regular-file `fstat`. | Write through a parent symlink rejects before creating the requested outside child; read through the parent symlink also rejects. Canonical create/read/identical replay remains PASS. |
| B5 | Lifecycle publication catches now distinguish `OSError`/`MemoryError`, including wrapped Ledger causes, as `PEE_IU4_RESOURCE_EXHAUSTED`; Terminal Lifecycle initialization/lock acquisition is classified before KILL. Evidence lists only freshly executed rows and preserves all 22 read-only identities. | Synthetic ENOSPC at Restart consumption and Terminal Lifecycle initialization both map to Resource Exhausted; Ledger count or Atomic KILL transaction count remains unchanged. Focused 49/49, full Live 540/540 and Regression 170/170 PASS. |

Rereview-3 resolution rows added to the focused module:

```text
LEGACY_FLAT_TIMESTAMP_REJECTION_ROWS:1
LEGACY_UNTYPED_THROTTLE_EVENT_REJECTION_ROWS:1
COMMITTED_CLOSE_WITHOUT_EVIDENCE_FAIL_ROWS:1
CALLER_SELECTED_STATIC_TRUST_REJECTION_ROWS:1
CALLER_SELECTED_REPORT_REASON_REJECTION_ROWS:1
PARENT_SYMLINK_PREMUTATION_REJECTION_ROWS:2
LIFECYCLE_RESOURCE_CLASSIFICATION_ROWS:2
TERMINAL_RESOURCE_FAILURE_KILL_TRANSACTIONS:0
```

### 4.11 Rereview-4 blocker resolution

| Blocker | File-exact resolution | Executed proof |
|---|---|---|
| B1 | Monitoring now receives a separately trusted Runtime-profile ID/fingerprint anchor. The report profile, caller-supplied expected static fingerprint and recomputed Observation static binding must all equal that independent anchor. | A previously group-invariant `receiver_tid` is changed in a fully rebuilt Observation; both former caller-controlled fingerprints are recomputed to the forged value while the trusted profile anchor remains fixed. The report rejects with `PEE_IU4_TERMINAL_CAPABILITY_ENVELOPE_INVALID`. |
| B2 | Close FSM phase, progressive evidence IDs, close statuses, channel phase and Runtime Session status are derived as one matrix. `OPEN` through `COMMIT` require `OPEN_CLEAN`; `COMMITTED` requires `RELEASED` plus `CLOSED_CLEAN`; `FAILED` requires an error/timeout and the matching open/closed unclean channel/session row. | Eight positive phase/session rows and seven negative evidence/status/channel/session rows execute. In particular `COMMITTED+RELEASED` with `OPEN_CLEAN` and `OPEN_UNCLEAN` both produce close-group FAIL and overall FAIL. |
| B3 | Every nonempty Legacy Throttle state now requires `utc_day` to equal the UTC calendar day of the newest retained canonical `AcceptedEntryEventV1`, in addition to the existing exact head bindings. | A fully rebuilt Snapshot with a newly fingerprinted nonempty Throttle record uses `utc_day=2026-08-21` and newest event `2026-08-20T23:59:59Z`; construction rejects with `PEE_IU4_HANDOFF_SAFETY_CONFLICT`. |
| B4 | All Orchestrator Lifecycle `records()`, `view()` and `initialize()` calls route through resource-aware wrappers that traverse wrapped causes and map every `OSError`/`MemoryError` to `PEE_IU4_RESOURCE_EXHAUSTED`. No direct Orchestrator Lifecycle read/initialization call remains outside the wrappers. | Raw `OSError` and `MemoryError` are injected into the pre-Consumption Restart view, Terminal pre-Consumption records/view, and pre-KILL Lifecycle initialization. Every row preserves Ledger count, Atomic State bytes and KILL transaction count after the failing boundary. |

Rereview-4 resolution row totals added to the focused module:

```text
SELF_CONSISTENT_STATIC_PROFILE_ATTACK_ROWS:1
CLOSE_FSM_SESSION_POSITIVE_ROWS:8
CLOSE_FSM_SESSION_NEGATIVE_ROWS:7
LEGACY_THROTTLE_UTC_DAY_REJECTION_ROWS:1
PRETERMINAL_LIFECYCLE_RESOURCE_ROWS:8
PRETERMINAL_RESOURCE_LEDGER_FOLLOW_ON_MUTATIONS:0
PRETERMINAL_RESOURCE_STATE_FOLLOW_ON_MUTATIONS:0
PRETERMINAL_RESOURCE_KILL_TRANSACTIONS:0
```

### 4.12 Rereview-5 blocker resolution

| Blocker | File-exact resolution | Executed proof |
|---|---|---|
| B1 | `build_monitoring_report` no longer accepts caller-selected static/profile fingerprints. Rereview-5 established an exact outer frozen/content-addressed `IU4TerminalRuntimeProfileRegistryV1` and rejected subclasses, Mapping/lookalikes, string subclasses, duplicates and divergent same-profile bytes. It did not establish deep immutability of stored inner records; that wider claim is superseded by Section 4.13. | The accepted Registry predates the attack. A fully rebuilt/refingerprinted `receiver_tid` deviation rejects against that retained Registry. Seven outer trust-boundary adversarial rows execute. |
| B2 | One explicit Close classifier jointly validates phase, progressive Evidence-ID presence, one allowed peer/HUP/timeout terminal marker, channel phase and Runtime Session status. The report embeds the exact Close record and independently reconstructs the exact stable Close reason during `from_record()`. | Eighteen allowed FAILED rows and six prohibited rows execute, in addition to the preserved eight positive/seven negative general Close rows. `FAILED+RELEASED+CLOSED_UNCLEAN` with no IDs and timeout, plus `FAILED+OPEN_DURABLE_GRANTED+OPEN_UNCLEAN` with no PREPARE and HUP error, both produce `runtime_close_fsm_result=FAIL` and `PEE_IU4_RUNTIME_SESSION_CLOSE_PROTOCOL_INVALID`. COMMITTED/CLOSED, reason reconstruction and reason order remain PASS. |
| B3 | `_has_resource_cause` covers arbitrary `__cause__` depth at Restart Consumption and Terminal Gap publication. Rereview-5 established nested classification there and direct Projection cleanup failures, but not every nested unlock/close/finally boundary; that wider claim is superseded by Section 4.13. | Nested publication failures preserve exact preterminal state. A post-KILL publication failure leaves one durable KILL and no Gap before retry. Direct Projection unlock/close failures retain one record/Cursor and replay identically. |
| B4 | The Projection Publisher caller root is descriptor-opened component-by-component and its operations remain FD-relative. Rereview-5 did not establish equivalent confinement through the separate Legacy State Store readback, which still reopened an absolute path; that wider claim is superseded by Section 4.13. | Projection Publisher races at relative `mkdir`, lock `open` and Cursor `replace` create zero outside entries and remain below the held original inode. |

Rereview-5 resolution row totals added to the focused module:

```text
TRUSTED_PROFILE_REGISTRY_ADVERSARIAL_ROWS:7
FAILED_CLOSE_ALLOWED_ROWS:18
FAILED_CLOSE_PROHIBITED_ROWS:6
NESTED_LIFECYCLE_RESOURCE_ROWS:11
NESTED_PROJECTION_RESOURCE_ROWS:2
POSTTERMINAL_PROJECTION_CLEANUP_ROWS:2
PROJECTION_ROOT_TOCTOU_RACE_ROWS:3
OUTSIDE_RACE_MUTATIONS:0
POSTTERMINAL_GAP_KILL_TRANSACTIONS:1
POSTTERMINAL_GAP_RECORDS_BEFORE_RETRY:0
POSTTERMINAL_GAP_RECORDS_AFTER_RETRY:1
```

Fault-grid row totals executed by the focused module:

```text
GENESIS_PREPARE_TARGET_COMMIT_ROWS:9
HANDOFF_PREPARE_TARGET_COMMIT_ROWS:9
RESTART_RECOVERY_ROWS:6
TERMINAL_GAP_ROWS:8
PROJECTION_PUBLICATION_ROWS:11
HANDOFF_MAPPING_CONFLICT_ROWS:10
RESTART_TRUST_AND_STATE_DIVERGENCE_ROWS:16
MONITORING_GROUP_FAIL_ROWS:12
BUDGET_BOUNDARY_VALUES:16
LOOP_OR_START_CALLS:0
```

### 4.13 Corrected scope of the Rereview-6 resolution

The former Rereview-6 wording overstated closure. Its actual established scope
and the residual Rereview-7 blocker were:

| Blocker | What Rereview-6 actually established | Residual blocker found by Rereview-7 |
|---|---|---|
| B1 | Exact frozen Anchor tuples, deep immutability and content revalidation of public Registry transport artifacts. | The same caller could still construct the Registry passed to `build_monitoring_report()`; Report constructor/build/from_record did not bind Registry/Anchor identity to an independent root. |
| B3 | Initialization, publication-lock and Terminal-Lifecycle cleanup aggregation at the specifically tested boundaries. | `_read_regular_at()`, `read_cursor()`, `_inventory()` and related nested read/close paths still bypassed the common primary-preserving classification. |
| B4 | Held parent/root directory chain, FD-relative access and parent-swap rejection. | The current FD-relative basename was not rebound after readback to the device/inode/type/size of the descriptor whose bytes were accepted. |

Rereview-6 resolution row totals added to the focused module:

```text
DEEP_REGISTRY_IMMUTABILITY_AND_REVALIDATION_ROWS:7
PROJECTION_INITIALIZATION_CLOSE_RESOURCE_ROWS:2
PROJECTION_UNLOCK_CLOSE_RESOURCE_ROWS:4
TERMINAL_LIFECYCLE_UNLOCK_CLOSE_RESOURCE_ROWS:4
DOUBLE_FAILURE_PRIMARY_SEMANTICS_ROWS:1
LEGACY_ROOT_PARENT_READBACK_RECONCILIATION_RACE_ROWS:4
LEGACY_OUTSIDE_RACE_MUTATIONS:0
POSTTERMINAL_PROJECTION_RECORDS:1
POSTTERMINAL_PROJECTION_CURSORS:1
POSTTERMINAL_TERMINAL_KILL_TRANSACTIONS:1
POSTTERMINAL_TERMINAL_GAP_RECORDS:1
```

### 4.14 Rereview-7 blocker resolution

| Blocker | File-exact resolution | Executed proof |
|---|---|---|
| B1 | `build_monitoring_report()` no longer accepts any caller Registry as trusted. Its optional Registry input is named `untrusted_profile_registry` and is always rejected as authority. A private exact frozen/content-addressed `_IU4TerminalRuntimeProfileTrustRootV1`, provisioned from reviewed static bindings independently of every Report call, owns the Registry capability. The Report embeds canonical Anchor bytes (including Anchor ID/fingerprint) plus Registry ID/fingerprint. Direct construction, inherited `build()`, `from_record()` and normal report creation all re-resolve the profile and compare every embedded binding against that root before any PASS can exist. Public Anchor/Registry builders remain strict transport parsers only. | The authorized normal path and canonical `from_record()` pass. A caller-refingerprinted Observation plus a caller-built self-consistent Registry is rejected as explicitly untrusted. A fully re-IDed/re-fingerprinted Report containing the forged Anchor/Registry is rejected through `from_record()`, direct construction and `build()`. Same-profile divergent bytes, Mapping/subclass/lookalikes, string subclass and changed static facts fail closed without rebuilding the provisioned root from the attack facts. |
| B3 | `_has_resource_cause()` traverses complete cause/context graphs. `_cleanup_descriptors_preserving_primary()` now governs Projection tree-open, regular-file open/read, initialization, Cursor, Inventory, output/Cursor publication, lock and Terminal Lifecycle cleanup. Every cleanup attempts all remaining descriptors; an existing primary reason is retained, while a sole direct or nested resource cleanup becomes `PEE_IU4_RESOURCE_EXHAUSTED`. Legacy projection caller wrappers apply the same cause classification, and State Store descriptor cleanup preserves primary errors while never leaking raw cleanup resources. | Direct and nested Cursor read and Inventory failures, direct/nested Inventory close failures, and a nested secondary directory-close failure accompanying primary `PEE_IU4_PROJECTION_LAG` execute with zero preterminal mutation. Preserved postterminal rows still retain exactly one Projection Record/Cursor or one EMERGENCY KILL/Gap, and the Lifecycle-extension double-failure still retains its primary reason. |
| B4 | `_read_projection_bytes()` performs FD-relative no-follow basename `stat`, descriptor `fstat`, complete read, second `fstat` and final basename `stat`; device, inode, file type and size must remain exactly equal. Create/sync/readback retains the created target identity and passes it as an expected identity into readback. Public read reconciliation rechecks target identity after parent-chain revalidation. No absolute reopen or resolve fallback exists. | Deterministic `/tmp` rows replace the target inode with identical bytes during read and immediately before write-readback, then replace it with size-divergent bytes or a directory during read reconciliation. All fail closed, create zero outside entries and preserve the held original file separately. The four earlier root/parent swap rows and alternative Handoff/Completion Legacy callers remain covered. |

Rereview-7 focused additions:

```text
PROVISIONED_TRUST_ROOT_PUBLIC_REPORT_ENTRY_PATHS:4
CALLER_SELF_CONSISTENT_UNTRUSTED_REGISTRY_AUTHORIZATIONS:0
CURSOR_READ_RESOURCE_ROWS:2
INVENTORY_READ_RESOURCE_ROWS:2
INVENTORY_CLOSE_RESOURCE_ROWS:2
CURSOR_PRIMARY_PLUS_SECONDARY_CLOSE_ROWS:1
LEGACY_TARGET_READ_WRITE_RECONCILIATION_REPLACEMENT_ROWS:4
LEGACY_TARGET_OUTSIDE_RACE_MUTATIONS:0
```

### 4.15 B2 preservation

Rereview-10 does not alter the accepted Close classifier or reason derivation.
The eighteen allowed FAILED-Close rows, six prohibited FAILED rows, the eight
positive and seven negative general Close rows, COMMITTED/RELEASED with exact
`CLOSED_CLEAN` semantics, CLOSED reconstruction, exact reason-code equality,
deduplication and stable reason ordering all remain PASS in the focused 74/74
and full-live_l1 565/565 executions.

### 4.16 Rereview-8 blocker resolution and corrected Rereview-7 scope

The Rereview-7 B1 wording above overstated the trust boundary: its provisioned
Root remained stored in a rebindable module attribute, and both Report creation
and Report validation dynamically resolved that attribute through a rebindable
module resolver. The Rereview-7 B3 wording also overstated State Store cleanup:
the Parent-open exception cleanup caught only `OSError`, so `MemoryError` or a
wrapped cleanup failure could replace an active primary error.

| Blocker | File-exact Rereview-8 resolution | Executed proof |
|---|---|---|
| B1 | Superseded by Section 4.17. The closure/default binding described here remained externally writable and therefore did not close B1. | The Root/resolver/class/import-alias rows remain useful preservation coverage, but did not exercise function-metadata containers. |
| B3 | `_cleanup_projection_descriptors()` is the single State Store descriptor-cleanup boundary for held Parent chains, single target descriptors and Parent-open failure cleanup. It catches `BaseException`, attempts every remaining descriptor, retains the first deterministic cleanup error only when no primary is active, and never replaces an active primary. Public I6 wrappers classify sole direct or arbitrarily nested `OSError`/`MemoryError` cleanup causes as `PEE_IU4_RESOURCE_EXHAUSTED`; non-resource cleanup remains a stable `ValueError`. | Parent revalidation primary plus two cleanup failures covers direct memory, nested I/O and non-resource cleanup. Target-read primary plus secondary cleanup preserves exact `PEE_IU4_PROJECTION_LAG`. Sole direct/nested resource and non-resource read cleanup exercises public classification and all boundary closes. Direct/nested postterminal write cleanup reports resource exhaustion, retains the durable record and accepts an identical retry/readback. |
| B4 | No Rereview-8 production change. The accepted FD-relative no-follow target binding remains intact through Create/Sync/Readback/Reconciliation, including device, inode, type and size, with no absolute reopen/resolve fallback. | The pre-existing root/parent and target replacement matrices remain PASS in focused and full-live_l1. |

The former Rereview-8 B1 protection claim was deliberately limited to rebinding data, resolver,
class-name and import-alias symbols while the original implementation functions
and code objects remain unchanged. It does not claim that arbitrary replacement
of a Python function, method or code object can be survived.

Rereview-8 focused additions:

```text
REBIND_ATTACK_CLASSES:4
ORIGINAL_REPORT_ENTRY_PATHS_PER_ATTACK:4
AUTHORIZED_REPORT_RESULTS_UNDER_REBINDING:16
FORGED_REPORT_AUTHORIZATIONS_UNDER_REBINDING:0_OF_16
STATE_STORE_PARENT_PRIMARY_CLEANUP_ROWS:3
STATE_STORE_TARGET_PRIMARY_CLEANUP_ROWS:1
STATE_STORE_SOLE_READ_CLEANUP_ROWS:3
STATE_STORE_POSTTERMINAL_WRITE_CLEANUP_ROWS:2
RAW_RESOURCE_EXCEPTIONS_AT_PUBLIC_I6_BOUNDARY:0
```

### 4.17 Rereview-9 B1 resolution

Rereview-9 found that the former Rereview-8 B1 claim was incomplete: the
serialized authority, resolver and Report type were still reachable through
writable closure cells, and the Report validator retained the resolver in a
writable positional default. Deleting the temporary module name did not make
those metadata containers immutable.

| Blocker | File-exact Rereview-9 resolution | Executed proof |
|---|---|---|
| B1 | The exact schema, Trust-Root identity, provisioning identity, Registry identity and the two exact Anchor rows now exist only as nested immutable primitive tuples in the original validator and Builder code objects. The validator has no closure, positional default or keyword default. The Builder has no closure or positional default; its sole keyword default is the explicitly untrusted Registry input set to `None`. The public Builder is a bound class method whose read-only binding holds the exact Report type, so the implementation no longer stores the Report type in a closure/default/class attribute. Direct construction, inherited `build()`, `from_record()` and normal Builder execution compare against the same code-literal Root facts. The Root, Registry and Anchors remain exactly typed, frozen and content-addressed transport artifacts; caller artifacts never become authority. Whole-function, whole-method or code-object replacement remains outside this protection boundary. | One new focused test proves the Builder and validator carry one equal code-literal Root, independently re-derives exact frozen/content-addressed Anchor, Registry and Root artifacts from it, verifies the Builder type binding is read-only, and proves all relevant authority functions have no closure. Across closure-absence, positional-default, keyword-default, function-attribute and class-metadata boundaries, all four unchanged original entries accept the canonical row and reject a fully content-addressed divergent same-profile row. Existing Root/resolver/class/import-alias, Mapping/subclass/lookalike/string-subclass, untrusted Registry/Anchor and serialized-root tamper rows remain PASS. |

Rereview-9 focused additions:

```text
CODE_LITERAL_ROOT_BINDINGS:2_EQUAL
METADATA_BOUNDARY_CLASSES:5
ORIGINAL_REPORT_ENTRY_PATHS_PER_BOUNDARY:4
AUTHORIZED_REPORT_RESULTS_UNDER_METADATA_REBINDING:20
FORGED_REPORT_AUTHORIZATIONS_UNDER_METADATA_REBINDING:0_OF_20
BUILDER_REPORT_TYPE_BINDING:READ_ONLY_EXACT_TYPE
AUTHORITY_BEARING_CLOSURES:0
AUTHORITY_BEARING_POSITIONAL_DEFAULTS:0
AUTHORITY_BEARING_KEYWORD_DEFAULTS:0
```

### 4.18 Rereview-10 B1 resolution

The independent Rereview-9 follow-up found one remaining mutable namespace
dependency: the unchanged Builder still loaded the static-profile fingerprint
Helper from its reachable global mapping. That binding could determine whether
divergent, newly content-addressed static facts matched the pinned profile.

| Blocker | File-exact Rereview-10 resolution | Executed proof |
|---|---|---|
| B1 | The Builder no longer loads the fingerprint Helper, Observation type or Report type from any global/Builtin/import namespace. Its read-only bound-method capsule holds the exact Report and Observation identities, the immutable raw-instance accessor and the original artifact factory identity. Every authority-bearing Observation and Report Root field is read from raw exact instance storage, so later class attributes or descriptors cannot redirect the comparison. The complete accepted static profile is re-derived as local recursively immutable primitive tuples and compared with local literal facts selected by the unchanged code-literal Root profile row. The validator retains the equal code-literal Root and reads its Root fields from raw Report storage. Whole-function, whole-method or code-object replacement remains outside scope. | A separate two-test boundary class covers five namespace/metadata boundaries across all four public Report entries: 20 legitimate results and zero of 20 forged authorizations. A second matrix covers all twelve static-profile groups with divergent newly content-addressed Observations while the public Helper alias is non-authoritative: zero of twelve is authorized. The prior 20/0-of-20 metadata matrix and 16/0-of-16 Root/resolver/class/import rebinding matrix remain PASS. |

Final recursive bytecode/data-flow audit:

```text
STATIC_AUTHORITY_GLOBAL_HELPER_LOADS:0
STATIC_AUTHORITY_GLOBAL_OBSERVATION_TYPE_LOADS:0
STATIC_AUTHORITY_GLOBAL_REPORT_TYPE_LOADS:0
STATIC_AUTHORITY_BUILTIN_LOOKUPS:0
STATIC_AUTHORITY_IMPORT_ALIAS_LOOKUPS:0
STATIC_AUTHORITY_CLASS_NAMESPACE_LOOKUPS:0
STATIC_AUTHORITY_CLOSURES:0
STATIC_AUTHORITY_POSITIONAL_DEFAULTS:0
STATIC_AUTHORITY_KEYWORD_DEFAULTS:0
STATIC_AUTHORITY_NESTED_CODE_GLOBALS:0
BOUND_AUTHORITY_CAPSULE:READ_ONLY_EXACT_REPORT_EXACT_OBSERVATION_RAW_ACCESSOR_ORIGINAL_FACTORY
NAMESPACE_BOUNDARY_CLASSES:5
ORIGINAL_REPORT_ENTRY_PATHS_PER_BOUNDARY:4
AUTHORIZED_REPORT_RESULTS_UNDER_NAMESPACE_REBINDING:20
FORGED_REPORT_AUTHORIZATIONS_UNDER_NAMESPACE_REBINDING:0_OF_20
STATIC_PROFILE_GROUP_BOUNDARIES:12
FORGED_STATIC_PROFILE_AUTHORIZATIONS:0_OF_12
```

The full Builder still loads only non-profile-authority names for ordinary
schema/result validation, error construction and output content-addressing:
`AssertionError`, `IU4RecoveryProjectionError`, `NONE`,
`REPORT_GROUP_RESULT_FIELDS`, `_classify_runtime_close_fsm`,
`_derived_monitoring_reasons`, `_integer`, `_sha`,
`_validate_observation_groups`, `dict`, `set`, `type`, and `zip`. The Report
validator similarly loads ordinary validation helpers, but its Root selection,
exact anchor/registry comparison and static-profile comparison are local and
precede any possible successful return. The inherited factory and parser load
content-addressing/schema helpers, then necessarily invoke the same local Root
validator. None of these remaining names can select or replace accepted Root
facts, static profile facts or the exact Builder result type.

### 4.19 Rereview-11 B1/B2/B3 resolution

The independent read-only File-Exact Rereview of Rereview-10 rejected the last
paragraph of 4.18: the names listed there were result- and content-addressing
authority, not ordinary validation. It also found that the bound capsule held
mutable classes/factory metadata and that reconstructed Reports did not carry
the Observation content to which their Observation ID/fingerprint referred.
Rereview-11 supersedes those claims without changing B2, B3 or B4 behavior.

| Blocker | Minimal production resolution | Defensive production proof |
|---|---|---|
| B1 — Observation content | The Report now carries the complete canonical `terminal_monitoring_observation_record`. Builder, direct constructor, inherited `build()` and `from_record()` independently revalidate its exact 26-field schema, all nested exact shapes/types, ID, fingerprint, Root/Session facts, twelve groups and code-literal static profile. The Report's Observation ID/fingerprint and Close record must equal that bound record. A path without the record cannot construct an authoritative Report. | `I6MonitoringObservationContentBoundaryTests`: 2/2. Four of four entries reject a divergent but internally correctly content-addressed static Observation; all four accept and reproduce the same newly content-addressed non-static Observation. |
| B2 — result authority | The single reconstruction authority derives group PASS/WARN/FAIL, Close result/reason, operation/Owner safety override, ordered reasons, hard-fail, overall, projection lag and exact Entry/Exit capability using local code literals and nested code only. Builder result derivation calls that exact function through its read-only capsule. Constructor/parser rebuild the same result from the embedded Observation. No result path loads `_validate_observation_groups`, `_classify_runtime_close_fsm`, `_derived_monitoring_reasons`, `_sha`, `_integer`, `_hash`, `fields`, result constants, factory aliases or affected Builtins. | `I6MonitoringResultAuthorityBoundaryTests`: 2/2; 12/12 Group/Close/Reason entry rows and 20/20 Global/Builtin/Factory/Literal rows fail closed, with zero forged PASS/AVAILABLE authorizations. Existing Namespace 20 legitimate/0 forged, static 0/12 forged and Root/import Rebinding 16 legitimate/0 forged remain PASS. |
| B3 — field/hash/serialization authority | Report field order, schema/type strings, ID prefix, nested-record set and all hash material are code-literal. Report hashing uses a local deterministic SHA-256/canonical-JSON implementation. The exact raw `__dict__` key set is checked. Anchor, Observation and Close records are normalized to tagged recursively immutable tuples; `reason_codes` is already an immutable tuple. `to_record()` thaws only those exact fields in literal order. Dataclass fields, annotations, class constants, descriptors, `fields(cls)`, `__dataclass_fields__` and generic Artifact factories cannot add, omit or redirect hash/record material. | `I6MonitoringDataclassFactoryBoundaryTests`: 2/2; 20 legitimate metadata/descriptor/factory rows produce 0 ID collisions for divergent raw content. Extra raw fields, stale-ID raw changes and Report subclasses reject. Existing Metadata 20 legitimate/0 forged remains PASS. |

Final recursive bytecode/namespace/capsule audit:

```text
REPORT_RAW_FIELDS:70_EXACT_CODE_LITERAL
BOUND_OBSERVATION_TOP_LEVEL_FIELDS:26_EXACT_CODE_LITERAL
REPORT_ENTRY_FUNCTIONS:5
REPORT_ENTRY_CLOSURES:0
REPORT_ENTRY_POSITIONAL_DEFAULTS:0
AUTHORITATIVE_GLOBAL_OR_BUILTIN_LOADS:0
ONLY_REMAINING_RECURSIVE_GLOBAL_LOAD:IU4RecoveryProjectionError_FOR_REJECTION_ONLY
MUTABLE_RESULT_HELPER_LOADS:0
MUTABLE_HASH_OR_FACTORY_LOADS:0
BOUND_CAPSULE:EXACT_REPORT_IDENTITY_EXACT_OBSERVATION_IDENTITY_RAW_ACCESSOR_EXACT_AUTHORITY_FUNCTION
CAPSULE_CLASS_METADATA_CONSULTED_FOR_FIELDS_HASH_RESULTS:NO
NESTED_REPORT_STORAGE:ANCHOR_OBSERVATION_CLOSE_REASON_RECURSIVELY_IMMUTABLE
TO_RECORD_FIELD_SOURCE:CODE_LITERAL_ONLY
BUILD_FIELD_SOURCE:CODE_LITERAL_ONLY
FROM_RECORD_AUTHORITY:CONSTRUCTOR_REVALIDATION_OF_COMPLETE_RECORD
```

The exception class is resolved only after a local predicate has selected
rejection. Rebinding it can change the exception object or cause another
exception, but cannot turn any rejecting predicate into an authoritative
return. Complete entry-function/method/code-object replacement remains outside
the stated protection scope; tested namespace, Builtin, Helper, descriptor,
dataclass, class-constant and factory-container mutation is inside it.

### 4.20 Rereview-12 HIGH-B1 resolution

The independent read-only File-Exact Rereview of Rereview-11 found two HIGH
B1 boundaries. First, exact-type decisions still used untrusted
`value.__class__`/stored raw-accessor paths before iteration, mapping access,
equality, membership, ordering or formatting, and public Report inputs could
submit internal tagged tuples. Second, `to_record()` trusted the mutable
instance `__dict__` and did not independently rerun the complete 70-field
value, cross-binding, Observation/Close, ID and fingerprint authority.

| Closed blocker | Minimal production resolution | Fresh regression proof |
|---|---|---|
| HIGH B1-A/B1-B/B1-C — actual Builtin type and canonical public input | The Report authority, inherited `build()`, `from_record()` and normal Builder now derive exact tuple/dict/list/text/int/bool identities and the raw accessor locally from code literals. Every public nested value is recursively copied only after its actual Builtin identity is established. Public nested inputs accept only Dict/List/scalars; `__DICT__`/`__LIST__` tagged tuples are produced only after successful internal normalization. Observation, Close, all twelve groups, Reasons, hard-fail, overall, lag, Entry/Exit, IDs and fingerprints pass through the same normalized authority. | `I6MonitoringBuiltinCanonicalityBoundaryTests`: 2/2 PASS. Four public entries accept the canonical Dict/List record and all four reject a pretagged form. A non-Builtin recursive value whose protocol methods are unusable is rejected by all four entries without reaching those methods. Existing Close/FAILED, Reasons, descriptor/cleanup/retry and FD-relative preservation tests remain green in Focused and Full Live. |
| HIGH B1-C — independent serialization authority and immutable raw source | Report construction stores the 70 authoritative values in one recursively immutable, literal-order tuple slot. The inherited free `__dict__` is explicitly non-authoritative. `to_record()` is the same complete local authority function: it reconstructs from the tuple slot, validates exact types/tags/order, all Observation/Close/results/cross-bindings, re-derives Report ID/fingerprint, and only then emits exactly 70 fields in literal order. `from_record()` contains its own literal 70-field tuple, validates an exact Builtin dict and builds values in literal order independent of input iteration order. | `I6MonitoringSerializationAuthorityBoundaryTests`: 2/2 PASS. It proves literal 26/70 field counts/order, reverse-ordered input reconstruction to literal order, and fail-closed serialization for value, root cross-binding, Observation, Close, Report-ID and Report-fingerprint inconsistency. The updated Dataclass/Factory storage test proves `__dict__` mutation cannot alter authority and inconsistent controlled storage cannot serialize. |

```text
PUBLIC_NESTED_REPRESENTATION:DICT_LIST_SCALAR_ONLY
PUBLIC_PRETAGGED_TUPLE_ACCEPTED:0_OF_4
RECURSIVE_NONBUILTIN_PROTOCOL_USES:0
REPORT_AUTHORITY_STORAGE:ONE_LITERAL_ORDER_IMMUTABLE_TUPLE
INSTANCE_DICT_AUTHORITY:NO
TO_RECORD_COMPLETE_AUTHORITY_REVALIDATION:YES
FROM_RECORD_FIELD_AUTHORITY:70_FIELD_CODE_LITERAL
OBSERVATION_FIELDS:26_EXACT_ORDERED
REPORT_FIELDS:70_EXACT_ORDERED
BLOCKER_1_TARGETED:2_OF_2_PASS
BLOCKER_2_TARGETED:2_OF_2_PASS
```

### 4.21 Rereview-13 HIGH-B1 and Evidence resolution

The independent read-only rereview of the Rereview-12 resolution found that
`object.__getattribute__(value, "__class__")` still invoked a possible
`__class__` data descriptor and that structural `__mro__` checks participated
in Report-type decisions. It also found that the recursively immutable
70-value tuple was itself held by a replaceable instance slot. Those claims in
4.20 are superseded as follows; B2, B3 and B4 behavior is unchanged.

| Closed finding | Minimal implementation | Defensive proof |
|---|---|---|
| HIGH B1-A/B1-B — exact type boundary | Every Report authority entry derives the Builtin `type` operation and the allowed tuple/dict/list/text/int/bool identities locally from code literals. The untrusted value is passed directly to that exact operation before any attribute, descriptor, mapping, comparison, hash, iteration or formatting protocol. Report/Observation outputs are checked by direct exact-type identity; no `__mro__` decision remains. Recursive key/value/list-element normalization remains Dict/List/scalar-only before internal tags are created. | `I6MonitoringBuiltinCanonicalityBoundaryTests`: 4/4 PASS. The new descriptor-equivalence matrix covers Key, Value, Element and rejection paths through normal Builder, direct constructor, class `build()` and `from_record()` (16 rows), and bytecode checks establish the exact-type call before protocol use. |
| HIGH B1-C — non-replaceable 70-value Authority | `IU4RecoveryMonitoringReportV1` now stores all 70 literal-order recursively immutable values in its Tuple base. No instance slot, instance dictionary, descriptor, annotation, class attribute, Module global or factory metadata holds those values. The private compatibility view is derived from the Tuple base and has no setter; replacing it with either inconsistent samples or a fully consistent alternative 70-value Report is structurally rejected. `to_record()` reads the Tuple base directly, checks nonempty `__dict__` fail-closed and reruns the complete 70-field type/tag/cross-binding/Observation/Close/ID/fingerprint authority immediately before ordered output. | `I6MonitoringSerializationAuthorityBoundaryTests`: 2/2 PASS. It proves exact 26/70 order, reverse-input reconstruction, six inconsistent replacement attempts, one fully consistent alternative replacement attempt, every one of the 70 public field names as non-authoritative `__dict__` input, stable field/ID/fingerprint/record output, and fail-closed nonempty `__dict__`. A separately bound immutable constructor capsule compares `cls` directly with the exact Report identity, so direct subclass construction and inherited `build()`/`from_record()` reject without `__mro__`. |
| MEDIUM — Evidence self-binding | The final binding rule below is byte-exact and the excluded capability-file statement is corrected to distinguish import-time Module execution from CLI/Runtime execution. PYC atimes from the independent rereview are the new prestate, not retroactively restored continuity. | Two independent payload computations and CR/LF checks are recorded below. |

```text
EXACT_TYPE_OPERATION:LOCAL_LITERAL_DERIVED_BUILTIN_TYPE
UNTRUSTED_CLASS_OR_MRO_ACCESS_BEFORE_TYPE_DECISION:NO
DESCRIPTOR_EQUIVALENCE_ROWS:16_OF_16_FAIL_CLOSED
REPORT_AUTHORITY_STORAGE:IMMUTABLE_TUPLE_BASE_70_VALUES
REPLACEABLE_AUTHORITY_SLOT:NO
CONSISTENT_70_VALUE_REPLACEMENT:STRUCTURALLY_REJECTED
INSTANCE_DICT_AUTHORITY:NO_NONEMPTY_FAIL_CLOSED
BLOCKER_1_TARGETED:4_OF_4_PASS
BLOCKER_2_TARGETED:2_OF_2_PASS
```

### 4.22 Rereview-14 HIGH-B1-B inherited-Factory resolution

The independent read-only File-Exact Rereview of the Rereview-13 resolution
found that inherited `build()` and `from_record()` accepted any Builtin-type
class object and then delegated construction through `cls(**values)`. A
subclass with its own construction path could therefore bypass the pinned
base `__new__` boundary. The earlier empty-subclass row exercised only the
inherited base constructor and did not cover this equivalence class. B1-A,
B1-C, B2, B3 and B4 behavior is unchanged.

| Closed finding | Minimal implementation | Defensive proof |
|---|---|---|
| HIGH B1-B — inherited Factory exact-type boundary | `_immutable_monitoring_report_build()` and `_immutable_monitoring_report_from_record()` each receive a separate immutable Tuple capsule containing the exact `IU4RecoveryMonitoringReportV1` identity and the accepted Report authority. Their first untrusted-input decision is direct `cls is pinned_report_type`; no public argument, Mapping, Key, Value, Element, attribute, descriptor, `__class__`, `__mro__` or other protocol is consulted first. Valid base calls construct only through the capsule-pinned authority, never through `cls(**values)`, and immediately require the actual result type to be exactly the pinned Report type before return. | `I6MonitoringFactoryExactTypeBoundaryTests`: 2/2 PASS. A real subclass defines its own `__new__`/`__init__` while inheriting both Factories; `build()` and `from_record()` reject separately with zero subclass-constructor and guarded public-value protocol calls. The valid base Factory paths remain exact `IU4RecoveryMonitoringReportV1` under defensive public-constructor replacement and preserve the complete canonical record. The original empty-subclass constructor/Factory row remains PASS. |

```text
FACTORY_PINNED_IDENTITIES:SEPARATE_IMMUTABLE_TUPLE_CAPSULES
FACTORY_FIRST_UNTRUSTED_DECISION:CLS_IS_PINNED_REPORT_TYPE
FACTORY_CONSTRUCTION_PATH:PINNED_REPORT_AUTHORITY_ONLY
FACTORY_EXACT_RESULT_POSTCONDITION:YES_IMMEDIATE
OWN_CONSTRUCTOR_SUBCLASS_FACTORY_CALLS:0
OWN_CONSTRUCTOR_SUBCLASS_PUBLIC_VALUE_PROTOCOL_CALLS:0
HIGH_B1_B_TARGETED:2_OF_2_PASS
INHERITED_FACTORY_EQUIVALENCE_CLASS:1_OF_1_PASS
```

## 5. Mandatory command evidence

Every final authoritative Rereview-14 unittest command used a separately created fresh `TMPDIR`
below `/tmp`, `PYTHONDONTWRITEBYTECODE=1`, and a fresh
`PYTHONPYCACHEPREFIX` below that root. All final rows have RC 0 and
failures/errors/skips `0/0/0`; the counts below are actual final-file counts,
not copied Rereview-13 values. One earlier non-final diagnostic Focused run
reported two test-introspection Errors after the new immutable method capsule
changed the metadata shape. The existing preservation test was then directed
to the underlying function, passed 1/1, and the complete final Focused run
passed 88/88. That superseded diagnostic run is not represented as PASS.

| Command | Root | Result |
|---|---|---|
| `.venv/bin/python -m unittest tests.live_l1.test_paper_iu4_recovery_projection.I6MonitoringFactoryExactTypeBoundaryTests` | fresh `/tmp/iu4-i6-r14-high-b1b-targeted-final.*` | 2/2 PASS |
| `.venv/bin/python -m unittest tests.live_l1.test_paper_iu4_recovery_projection.I6MonitoringFactoryExactTypeBoundaryTests.test_own_constructor_subclass_inherited_factories_reject_before_values` | fresh `/tmp/iu4-i6-r14-inherited-final.*` | 1/1 PASS |
| `.venv/bin/python -m unittest tests.live_l1.test_paper_iu4_recovery_projection.I6MonitoringBuiltinCanonicalityBoundaryTests` | fresh `/tmp/iu4-i6-r14-b1a-final.*` | 4/4 PASS |
| `.venv/bin/python -m unittest tests.live_l1.test_paper_iu4_recovery_projection.I6MonitoringSerializationAuthorityBoundaryTests` | fresh `/tmp/iu4-i6-r14-b1c-final.*` | 2/2 PASS |
| `.venv/bin/python -m unittest tests.live_l1.test_paper_iu4_recovery_projection.I6MonitoringNamespaceBoundaryTests` | fresh `/tmp/iu4-i6-r14-namespace-final.*` | 2/2 PASS |
| `.venv/bin/python -m unittest tests.live_l1.test_paper_iu4_recovery_projection.I6MonitoringTests.test_code_pinned_report_authority_survives_function_metadata_rebinding` | fresh `/tmp/iu4-i6-r14-metadata-preservation.*` | 1/1 PASS |
| `.venv/bin/python -m unittest tests.live_l1.test_paper_iu4_recovery_projection` | fresh `/tmp/iu4-i6-r14-focused-final.*` | 88/88 PASS |
| `.venv/bin/python -m unittest tests.live_l1.test_paper_atomic_coordinator_v2` | fresh `/tmp/iu4-i6-r14-atomic-v2.*` | 54/54 PASS |
| `.venv/bin/python -m unittest tests.live_l1.test_iu4_lifecycle_ledger` | fresh `/tmp/iu4-i6-r14-lifecycle.*` | 5/5 PASS |
| `.venv/bin/python -m unittest tests.live_l1.test_paper_iu4_startup_gate` | fresh `/tmp/iu4-i6-r14-startup.*` | 12/12 PASS |
| `.venv/bin/python -m unittest tests.live_l1.test_paper_iu4_runtime_gate` | fresh `/tmp/iu4-i6-r14-runtime.*` | 3/3 PASS |
| `.venv/bin/python -m unittest tests.live_l1.test_paper_iu4_execution_seam_v2` | fresh `/tmp/iu4-i6-r14-execution-v2.*` | 44/44 PASS |
| `.venv/bin/python -m unittest tests.live_l1.test_paper_iu4_adapter_v2` | fresh `/tmp/iu4-i6-r14-adapter-v2.*` | 18/18 PASS |
| `.venv/bin/python -m unittest tests.live_l1.test_paper_atomic_coordinator` | fresh `/tmp/iu4-i6-r14-atomic-v1.*` | 23/23 PASS |
| `.venv/bin/python -m unittest tests.live_l1.test_paper_iu4_adapter` | fresh `/tmp/iu4-i6-r14-adapter-v1.*` | 13/13 PASS |
| AST import-closure precheck for `tests/regression` | fresh `/tmp/iu4-i6-r14-regression-ast.*` | 12 starts; 42 files; 0 forbidden edges; PASS |
| `.venv/bin/python -m unittest discover -s tests/regression -p 'test_*.py'` | fresh `/tmp/iu4-i6-r14-regression.*` | 170/170 PASS |
| `.venv/bin/python -m unittest discover -s tests/live_l1 -p 'test_*.py'` | not executed | REQUIRED EXCLUSION: known to import excluded capability Module |

Exact compile command:

```text
.venv/bin/python -m py_compile live_l1/state/paper_atomic_coordinator.py live_l1/state/models.py live_l1/state/state_store.py live_l1/state/paper_iu4_recovery_projection.py tests/live_l1/test_paper_iu4_recovery_projection.py
PYTHONPYCACHEPREFIX:/tmp/iu4-i6-r14-compile.DlngO9/pycache
RESULT:PASS_RC0
COMPILED_TARGET_PYC_COUNT:5
PYC_LOCATION:ONLY_UNDER_/tmp/iu4-i6-r14-compile.DlngO9
REPOSITORY_LOCAL_PYC_CREATED_BY_COMPILE:0
```

`git diff --check` and `git diff --cached --check` both returned RC 0.

## 6. Preservation and Freeze

| Read-only path | SHA-256 | Lines |
|---|---|---:|
| `live_l1/core/loop.py` | `e4db22642b628fe4b84cf0d2daa9ecd846208138eaa3868a02a56ddf9f75ee6c` | 1,947 |
| `live_l1/core/execution.py` | `85a9acb238dafd3adf5fd8bf57153772d3c7b41559943bdcce5336e3b60dcb5e` | 1,386 |
| `live_l1/core/paper_iu4_adapter.py` | `1fac2629a0ebdd889825f496e9273c358ffe7596c2173d307ce1d1eb7e9bd6a6` | 1,896 |
| `live_l1/state/paper_artifacts.py` | `3cd9a459e2856672bb7b318c9cdbf8f8bb52e633ee9529d74761d64928213946` | 1,575 |
| `live_l1/state/loss_cluster.py` | `4ce7d59f64a67de94ffc6f1d03ff4e6c8a7a590802abb003b311cd0d56cc3e55` | 521 |
| `tests/live_l1/test_paper_atomic_coordinator_v2.py` | `ec731c106ab23b78e482204e16d20826264cdf775f0c08c292a82bab1111ff8c` | 3,734 |
| `tests/live_l1/test_paper_iu4_execution_seam_v2.py` | `fc61404d910fe76141cba8ba54f98ea6de552664a8b21bdaa50510e33f603755` | 2,517 |
| `tests/live_l1/test_paper_iu4_adapter_v2.py` | `f71d46700a1966534429281091da32e263ac479ddf1393c5021d015eac1cd1b3` | 1,274 |
| `live_l1/core/paper_execution_control.py` | `7d3cb901c1c67c8df85e99bc579fda85d8732b634ff4747e08620b92ac1e44f7` | 257 |
| `live_l1/core/paper_iu4_runtime_gate.py` | `447573e484bc13023a118ae61bf7615657293be629c30729748e64f0af7af7c5` | 201 |
| `live_l1/core/paper_iu4_startup_gate.py` | `c4a1854f3b200525568a40205b39e9ce2e14c342bb860569ba7fcfe5e9c063cd` | 919 |
| `live_l1/core/paper_iu4_shadow_runtime_gate.py` | `98d986f3ac2e463b371998604d92b29aa113a507dd0f84bcbd3ff36a52efaf59` | 438 |
| `live_l1/core/paper_iu4_shadow_observation_gate.py` | `ed4e75fad664c68b91950e9c09e873823ebe3eb0b0062f85806daa09ce661350` | 886 |
| `live_l1/core/paper_iu4_shadow_harness.py` | `ddfb60f19a3b765a476c8de0464d583590313cdd0583391044cb338fec969f77` | 1,007 |
| `live_l1/state/iu4_lifecycle_ledger.py` | `d72134195f66b1d39c09a2ca6b9919d8a9acf17c4490ab52d9abc2aebcd71337` | 438 |
| `live_l1/core/paper_economics.py` | `a302013134d1265ac85ad10b57a67ead9e2343043f7eb499fd965a44312525ae` | 730 |
| `live_l1/core/paper_entry_throttle.py` | `ad5447d88a2c35c9a71a5495c61c8f08fa844daf60e79d4a872234e88037df75` | 727 |
| `live_l1/state/paper_entry_throttle.py` | `ce76d8430792d6de1cfdf9a55c09cb6ab501489c7610d2f78345f8d78646295b` | 586 |
| `live_l1/tools/safe_launch.py` | `cb90bd49b36de56e8ad95e9b24febb23baa0513b1ec51e7402f63a5efd6ec652` | 201 |
| `tests/live_l1/test_paper_iu4_adapter.py` | `b4947e4c03fa3b187e01c4005062337d1837b70d652243030581172dd4d2c339` | 441 |
| `tests/live_l1/test_paper_execution_control.py` | `0ae44f2d32f5f3b6affe37a258be0e6aee06790f857e4fc01628c6795bda99e5` | 843 |
| `tests/live_l1/test_paper_atomic_coordinator.py` | `a46f622f9a00e5db727ade04ece89b4deaf51347dc2d1f4d304532572b382753` | 891 |

```text
FREEZE_DIRECTORY_MODE:0555
PRESERVATION_TAR_SHA256:3af14ff2e270d7d3ca09c1279da7d64e6d720630d06a0c5f45b6786237782037
PRESERVATION_TAR_MODE:0444
PRESERVATION_TAR_ENTRIES:1318
PRESERVATION_TAR_UNIQUE_ENTRIES:1318
PRESERVATION_TAR_GZIP_TEST:PASS
FREEZE_MANIFEST_SHA256:ad154c0eda13470920878873ed170368cc8f4c43591400a07592a77b179d9e16
FREEZE_MANIFEST_MODE:0444
FREEZE_MANIFEST_LINES:60
```

## 7. Scope, purity and operational negatives

- I6 symbols occur in production only in the additive Coordinator methods,
  additive models/store helpers and the new I6 module.
- There is no import or construction from Loop, Adapter, Execution, Runtime
  Gate, Startup Gate, shadow gates, safe launch or any launcher.
- Four fresh file-exact negative `rg` searches returned RC 1 with empty output:
  I6-module imports; Publisher/Orchestrator/Report construction; and
  `RUNTIME_SESSION_OPEN` across the explicitly listed Loop, Execution, Adapter,
  Startup/Runtime/shadow-gate, paper-control and safe-launch files; plus I6
  module/orchestrator/publisher/report/builder references in the explicitly
  listed `main`, safe-launch and shadow-observation launcher files. Every
  I6-specific consumer/activation count in that declared boundary is `0`.
- The four fresh Rereview-14 results were respectively `RC 1`, `RC 1`, `RC 1`
  and `RC 1`, with no output. The explicitly bounded files were not expanded
  to the separate terminal-capability validation tool.
- No tree-wide absence is claimed. The excluded pre-existing untracked
  `live_l1/tools/validate_terminal_lease_capability.py` was not read, imported,
  executed or changed during Rereview-14 Resolution. The independent rereview
  established that the earlier Rereview-12 Full-Live discovery imported that
  Module under normal Python import semantics and therefore executed its
  Module top-level code, although it did not start the Module CLI or any
  Runtime/network function. Neither Rereview-13 nor Rereview-14 repeated Full
  Live; this resolution makes no `575/575` successor claim and leaves that
  aggregate coverage as an explicit verification boundary.
- Lifecycle Ledger and Startup Authorization definitions remain byte-identical.
- Projection output is explicitly non-authoritative and is never read by
  Atomic recovery.
- Projected Economics are copied as canonical strings and are not recalculated.
- Tests use only fresh `/tmp` roots and synthetic records; no operational
  State, logs, profile, external Authorization, process, PIDFD, socket, network,
  Exchange, Live or Production resource was accessed.
- No Git stage/commit/fetch/push and no foreign-artifact cleanup occurred. The
  authoritative compile created exactly five `.pyc` files only under its
  `/tmp` prefix and created no repository-local bytecode.
- The independent rereview's initial PYC hash reads on the `ext4,relatime`
  mount changed only access times. Those access times became the Rereview-13
  poststate and are the Rereview-14 prestate: `models`
  `2026-08-23 15:28:58.962523373 +0200`,
  `paper_atomic_coordinator` `15:28:58.966523372`,
  `paper_iu4_recovery_projection` `15:28:58.966523372`, `state_store`
  `15:28:58.970523371`, and the focused test PYC
  `15:28:59.194523337`. No metadata-exact continuity across that earlier
  rereview is claimed and no atime restoration was attempted. Rereview-14
  first captured full nanosecond metadata without hashing. Its single later
  byte verification used read-only `dd iflag=noatime` into `sha256sum` and
  compared full metadata immediately before and after every file; all five
  comparisons were exact. From this new prestate the five ignored repository
  PYC files were not opened for write, removed or replaced; every Python
  command disabled normal bytecode writes and used a fresh `/tmp` cache
  prefix.
  Their preserved SHA-256 values are: `models.cpython-314.pyc`
  `691c972b85064f9993af135a04d840ae0ad4187e0738ede98419509bba861186`,
  `paper_atomic_coordinator.cpython-314.pyc`
  `8b267c17a124615738660aed71838cd66878cf771f49fb3f438f3787974d62d9`,
  `paper_iu4_recovery_projection.cpython-314.pyc`
  `cdb5f07c3a57c2b05c793634935151ec693111408448f095a5dcf092cefb183b`,
  `state_store.cpython-314.pyc`
  `722198635b860609d3e78ca64fe93973f4561d239e036cca5999125175102c67`,
  and `test_paper_iu4_recovery_projection.cpython-314.pyc`
  `d507281874336c4337e4f9c77190d76b58b1666f8c2de0148f7280c56ed6265a`.
- Initial foreign status membership was 142 entries with NUL-delimited
  SHA-256 `b25c5f1e1244cac1c61f015e2c6a36798d5cd707cc05b8c61923c8d068c62987`.
  Final foreign status membership is also 142 entries with the identical
  SHA-256. Only the authorized I6 source, focused test and this existing
  Evidence path differ in content; no foreign membership changed.
- Foreign dirty/untracked artifacts were preserved.
- The excluded specification-bundle script was not read, executed or changed.

### 7.1 Exact initial/final foreign-status membership

The following 142 status rows are the complete explicit initial and final
membership. The NUL-delimited status hash is identical at both boundaries.
Only the three authorized I6 paths in this list changed content during this
resolution; every other row is foreign and was preserved without mutation.

```text
 M live_l1/core/execution.py
 M live_l1/core/loop.py
 M live_l1/core/paper_iu4_adapter.py
 M live_l1/core/paper_iu4_shadow_runtime_gate.py
 M live_l1/core/paper_iu4_startup_gate.py
 M live_l1/state/loss_cluster.py
 M live_l1/state/models.py
 M live_l1/state/paper_artifacts.py
 M live_l1/state/paper_atomic_coordinator.py
 M live_l1/state/state_store.py
?? docs/LIVE_DESIGN_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPEC.md
?? docs/review/PRE_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPECIFICATION_REREVIEW_RESOLUTION_2026-08-17.md
?? docs/review/PRE_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPECIFICATION_REVIEW_RESOLUTION_2026-08-17.md
?? docs/review/PRE_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPECIFICATION_REVISION_10_REREVIEW_RESOLUTION_2026-08-18.md
?? docs/review/PRE_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPECIFICATION_REVISION_11_REREVIEW_RESOLUTION_2026-08-18.md
?? docs/review/PRE_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPECIFICATION_REVISION_12_REREVIEW_RESOLUTION_2026-08-18.md
?? docs/review/PRE_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPECIFICATION_REVISION_13_INDEPENDENT_READONLY_REREVIEW_2026-08-18.md
?? docs/review/PRE_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPECIFICATION_REVISION_13_REREVIEW_RESOLUTION_2026-08-18.md
?? docs/review/PRE_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPECIFICATION_REVISION_14_INDEPENDENT_READONLY_REREVIEW_2026-08-18.md
?? docs/review/PRE_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPECIFICATION_REVISION_14_REREVIEW_RESOLUTION_2026-08-18.md
?? docs/review/PRE_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPECIFICATION_REVISION_15_INDEPENDENT_READONLY_REREVIEW_2026-08-18.md
?? docs/review/PRE_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPECIFICATION_REVISION_15_REREVIEW_RESOLUTION_2026-08-18.md
?? docs/review/PRE_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPECIFICATION_REVISION_16_INDEPENDENT_READONLY_REREVIEW_2026-08-18.md
?? docs/review/PRE_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPECIFICATION_REVISION_16_REREVIEW_RESOLUTION_2026-08-18.md
?? docs/review/PRE_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPECIFICATION_REVISION_17_INDEPENDENT_READONLY_REREVIEW_2026-08-18.md
?? docs/review/PRE_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPECIFICATION_REVISION_17_REREVIEW_RESOLUTION_2026-08-18.md
?? docs/review/PRE_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPECIFICATION_REVISION_18_INDEPENDENT_READONLY_REREVIEW_2026-08-18.md
?? docs/review/PRE_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPECIFICATION_REVISION_18_REREVIEW_RESOLUTION_2026-08-18.md
?? docs/review/PRE_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPECIFICATION_REVISION_19_INDEPENDENT_READONLY_REREVIEW_2026-08-18.md
?? docs/review/PRE_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPECIFICATION_REVISION_19_REREVIEW_RESOLUTION_2026-08-18.md
?? docs/review/PRE_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPECIFICATION_REVISION_20_INDEPENDENT_READONLY_REREVIEW_2026-08-19.md
?? docs/review/PRE_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPECIFICATION_REVISION_20_REREVIEW_RESOLUTION_2026-08-19.md
?? docs/review/PRE_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPECIFICATION_REVISION_21_FINAL_R3_ATTESTATION_2026-08-19.md
?? docs/review/PRE_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPECIFICATION_REVISION_21_INDEPENDENT_READONLY_REREVIEW_2026-08-19.md
?? docs/review/PRE_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPECIFICATION_REVISION_21_TERMINAL_R3_HANDOFF_2026-08-19.md
?? docs/review/PRE_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPECIFICATION_REVISION_3_REREVIEW_RESOLUTION_2026-08-17.md
?? docs/review/PRE_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPECIFICATION_REVISION_4_REREVIEW_RESOLUTION_2026-08-17.md
?? docs/review/PRE_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPECIFICATION_REVISION_5_REREVIEW_RESOLUTION_2026-08-17.md
?? docs/review/PRE_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPECIFICATION_REVISION_6_REREVIEW_RESOLUTION_2026-08-17.md
?? docs/review/PRE_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPECIFICATION_REVISION_7_REREVIEW_RESOLUTION_2026-08-18.md
?? docs/review/PRE_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPECIFICATION_REVISION_8_REREVIEW_RESOLUTION_2026-08-18.md
?? docs/review/PRE_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPECIFICATION_REVISION_9_REREVIEW_RESOLUTION_2026-08-18.md
?? docs/review/PRE_IU4_I1_CHARACTERIZATION_PURE_CONTROL_EXTRACTION_FILE_EXACT_MANDATE_2026-08-19.md
?? docs/review/PRE_IU4_I1_CHARACTERIZATION_PURE_CONTROL_EXTRACTION_IMPLEMENTATION_EVIDENCE_2026-08-19.md
?? docs/review/PRE_IU4_I1_CHARACTERIZATION_PURE_CONTROL_EXTRACTION_INDEPENDENT_READONLY_FILE_EXACT_REREVIEW_2026-08-19.md
?? docs/review/PRE_IU4_I1_CHARACTERIZATION_PURE_CONTROL_EXTRACTION_INDEPENDENT_READONLY_FILE_EXACT_REREVIEW_2_2026-08-19.md
?? docs/review/PRE_IU4_I1_CHARACTERIZATION_PURE_CONTROL_EXTRACTION_INDEPENDENT_READONLY_FILE_EXACT_REREVIEW_RESOLUTION_2026-08-19.md
?? docs/review/PRE_IU4_I1_CHARACTERIZATION_PURE_CONTROL_EXTRACTION_INDEPENDENT_READONLY_FILE_EXACT_REVIEW_2026-08-19.md
?? docs/review/PRE_IU4_I1_CHARACTERIZATION_PURE_CONTROL_EXTRACTION_INDEPENDENT_READONLY_FILE_EXACT_REVIEW_RESOLUTION_2026-08-19.md
?? docs/review/PRE_IU4_I2_LIFECYCLE_LEDGER_RUNTIME_GATE_AUTHORIZATION_V2_COLLECTOR_SUPPLEMENTAL_FILE_EXACT_MANDATE_DECISION_2026-08-20.md
?? docs/review/PRE_IU4_I2_LIFECYCLE_LEDGER_RUNTIME_GATE_AUTHORIZATION_V2_FILE_EXACT_MANDATE_2026-08-19.md
?? docs/review/PRE_IU4_I2_LIFECYCLE_LEDGER_RUNTIME_GATE_AUTHORIZATION_V2_IMPLEMENTATION_EVIDENCE_2026-08-19.md
?? docs/review/PRE_IU4_I2_LIFECYCLE_LEDGER_RUNTIME_GATE_AUTHORIZATION_V2_IMPLEMENTATION_INDEPENDENT_READONLY_FILE_EXACT_REREVIEW_2026-08-20.md
?? docs/review/PRE_IU4_I2_LIFECYCLE_LEDGER_RUNTIME_GATE_AUTHORIZATION_V2_IMPLEMENTATION_INDEPENDENT_READONLY_FILE_EXACT_REVIEW_2026-08-20.md
?? docs/review/PRE_IU4_I2_LIFECYCLE_LEDGER_RUNTIME_GATE_AUTHORIZATION_V2_IMPLEMENTATION_INDEPENDENT_READONLY_FILE_EXACT_REVIEW_RESOLUTION_2026-08-20.md
?? docs/review/PRE_IU4_I3_ATOMIC_STATE_TRANSACTION_V2_FILE_EXACT_MANDATE_2026-08-20.md
?? docs/review/PRE_IU4_I3_ATOMIC_STATE_TRANSACTION_V2_IMPLEMENTATION_EVIDENCE_2026-08-20.md
?? docs/review/PRE_IU4_I3_ATOMIC_STATE_TRANSACTION_V2_IMPLEMENTATION_INDEPENDENT_READONLY_FILE_EXACT_REREVIEW_2026-08-20.md
?? docs/review/PRE_IU4_I3_ATOMIC_STATE_TRANSACTION_V2_IMPLEMENTATION_INDEPENDENT_READONLY_FILE_EXACT_REREVIEW_2_2026-08-20.md
?? docs/review/PRE_IU4_I3_ATOMIC_STATE_TRANSACTION_V2_IMPLEMENTATION_INDEPENDENT_READONLY_FILE_EXACT_REREVIEW_3_2026-08-20.md
?? docs/review/PRE_IU4_I3_ATOMIC_STATE_TRANSACTION_V2_IMPLEMENTATION_INDEPENDENT_READONLY_FILE_EXACT_REREVIEW_4_2026-08-20.md
?? docs/review/PRE_IU4_I3_ATOMIC_STATE_TRANSACTION_V2_IMPLEMENTATION_INDEPENDENT_READONLY_FILE_EXACT_REREVIEW_5_2026-08-20.md
?? docs/review/PRE_IU4_I3_ATOMIC_STATE_TRANSACTION_V2_IMPLEMENTATION_INDEPENDENT_READONLY_FILE_EXACT_REREVIEW_6_2026-08-20.md
?? docs/review/PRE_IU4_I3_ATOMIC_STATE_TRANSACTION_V2_IMPLEMENTATION_REREVIEW_2_RESOLUTION_FILE_EXACT_2026-08-20.md
?? docs/review/PRE_IU4_I3_ATOMIC_STATE_TRANSACTION_V2_IMPLEMENTATION_REREVIEW_3_RESOLUTION_FILE_EXACT_2026-08-20.md
?? docs/review/PRE_IU4_I3_ATOMIC_STATE_TRANSACTION_V2_IMPLEMENTATION_REREVIEW_4_EVIDENCE_COMPLETENESS_RESOLUTION_FILE_EXACT_2026-08-20.md
?? docs/review/PRE_IU4_I3_ATOMIC_STATE_TRANSACTION_V2_IMPLEMENTATION_REREVIEW_5_EVIDENCE_PRECISION_RESOLUTION_FILE_EXACT_2026-08-20.md
?? docs/review/PRE_IU4_I3_ATOMIC_STATE_TRANSACTION_V2_IMPLEMENTATION_REREVIEW_RESOLUTION_FILE_EXACT_2026-08-20.md
?? docs/review/PRE_IU4_I4_ADAPTER_REQUEST_V2_FILE_EXACT_MANDATE_2026-08-20.md
?? docs/review/PRE_IU4_I4_ADAPTER_REQUEST_V2_FILE_EXACT_MANDATE_INDEPENDENT_READONLY_REREVIEW_2026-08-20.md
?? docs/review/PRE_IU4_I4_ADAPTER_REQUEST_V2_FILE_EXACT_MANDATE_INDEPENDENT_READONLY_REREVIEW_2_2026-08-20.md
?? docs/review/PRE_IU4_I4_ADAPTER_REQUEST_V2_FILE_EXACT_MANDATE_REREVIEW_RESOLUTION_FILE_EXACT_2026-08-20.md
?? docs/review/PRE_IU4_I4_ADAPTER_REQUEST_V2_IMPLEMENTATION_EVIDENCE_2026-08-20.md
?? docs/review/PRE_IU4_I4_ADAPTER_REQUEST_V2_IMPLEMENTATION_INDEPENDENT_READONLY_FILE_EXACT_REREVIEW_2026-08-20.md
?? docs/review/PRE_IU4_I4_ADAPTER_REQUEST_V2_IMPLEMENTATION_INDEPENDENT_READONLY_FILE_EXACT_REREVIEW_2_2026-08-20.md
?? docs/review/PRE_IU4_I4_ADAPTER_REQUEST_V2_IMPLEMENTATION_INDEPENDENT_READONLY_FILE_EXACT_REREVIEW_3_2026-08-20.md
?? docs/review/PRE_IU4_I4_ADAPTER_REQUEST_V2_IMPLEMENTATION_REREVIEW_2_EVIDENCE_PRECISION_RESOLUTION_FILE_EXACT_2026-08-20.md
?? docs/review/PRE_IU4_I4_ADAPTER_REQUEST_V2_IMPLEMENTATION_REREVIEW_RESOLUTION_FILE_EXACT_2026-08-20.md
?? docs/review/PRE_IU4_I5_ACTIVE_EXECUTION_SEAM_DURABLE_DENIAL_PROVENANCE_FILE_EXACT_MANDATE_REVISION_2026-08-20.md
?? docs/review/PRE_IU4_I5_ACTIVE_EXECUTION_SEAM_DURABLE_DENIAL_PROVENANCE_FILE_EXACT_MANDATE_REVISION_INDEPENDENT_READONLY_REREVIEW_2026-08-20.md
?? docs/review/PRE_IU4_I5_ACTIVE_EXECUTION_SEAM_DURABLE_DENIAL_PROVENANCE_FILE_EXACT_MANDATE_REVISION_INDEPENDENT_READONLY_REREVIEW_2_2026-08-20.md
?? docs/review/PRE_IU4_I5_ACTIVE_EXECUTION_SEAM_DURABLE_DENIAL_PROVENANCE_FILE_EXACT_MANDATE_REVISION_RESOLUTION_FILE_EXACT_2026-08-20.md
?? docs/review/PRE_IU4_I5_ACTIVE_EXECUTION_SEAM_DURABLE_DENIAL_PROVENANCE_IMPLEMENTATION_INDEPENDENT_READONLY_FILE_EXACT_REREVIEW_2026-08-20.md
?? docs/review/PRE_IU4_I5_ACTIVE_EXECUTION_SEAM_DURABLE_DENIAL_PROVENANCE_IMPLEMENTATION_INDEPENDENT_READONLY_FILE_EXACT_REREVIEW_2_2026-08-20.md
?? docs/review/PRE_IU4_I5_ACTIVE_EXECUTION_SEAM_DURABLE_DENIAL_PROVENANCE_IMPLEMENTATION_INDEPENDENT_READONLY_FILE_EXACT_REREVIEW_3_2026-08-20.md
?? docs/review/PRE_IU4_I5_ACTIVE_EXECUTION_SEAM_DURABLE_DENIAL_PROVENANCE_IMPLEMENTATION_REREVIEW_2_RESOLUTION_FILE_EXACT_2026-08-20.md
?? docs/review/PRE_IU4_I5_ACTIVE_EXECUTION_SEAM_DURABLE_DENIAL_PROVENANCE_IMPLEMENTATION_REREVIEW_RESOLUTION_FILE_EXACT_2026-08-20.md
?? docs/review/PRE_IU4_I5_ACTIVE_EXECUTION_SEAM_FILE_EXACT_MANDATE_2026-08-20.md
?? docs/review/PRE_IU4_I5_ACTIVE_EXECUTION_SEAM_FILE_EXACT_MANDATE_INDEPENDENT_READONLY_REREVIEW_2026-08-20.md
?? docs/review/PRE_IU4_I5_ACTIVE_EXECUTION_SEAM_FILE_EXACT_MANDATE_INDEPENDENT_READONLY_REREVIEW_2_2026-08-20.md
?? docs/review/PRE_IU4_I5_ACTIVE_EXECUTION_SEAM_FILE_EXACT_MANDATE_REREVIEW_RESOLUTION_FILE_EXACT_2026-08-20.md
?? docs/review/PRE_IU4_I5_ACTIVE_EXECUTION_SEAM_IMPLEMENTATION_EVIDENCE_2026-08-20.md
?? docs/review/PRE_IU4_I5_ACTIVE_EXECUTION_SEAM_IMPLEMENTATION_INDEPENDENT_READONLY_FILE_EXACT_REREVIEW_2026-08-20.md
?? docs/review/PRE_IU4_I5_ACTIVE_EXECUTION_SEAM_IMPLEMENTATION_INDEPENDENT_READONLY_FILE_EXACT_REREVIEW_2_2026-08-20.md
?? docs/review/PRE_IU4_I5_ACTIVE_EXECUTION_SEAM_IMPLEMENTATION_INDEPENDENT_READONLY_FILE_EXACT_REREVIEW_3_2026-08-20.md
?? docs/review/PRE_IU4_I5_ACTIVE_EXECUTION_SEAM_IMPLEMENTATION_INDEPENDENT_READONLY_FILE_EXACT_REREVIEW_4_2026-08-20.md
?? docs/review/PRE_IU4_I5_ACTIVE_EXECUTION_SEAM_IMPLEMENTATION_REREVIEW_2_RESOLUTION_FILE_EXACT_2026-08-20.md
?? docs/review/PRE_IU4_I5_ACTIVE_EXECUTION_SEAM_IMPLEMENTATION_REREVIEW_3_RESOLUTION_FILE_EXACT_2026-08-20.md
?? docs/review/PRE_IU4_I5_ACTIVE_EXECUTION_SEAM_IMPLEMENTATION_REREVIEW_4_DURABLE_DENIAL_PROVENANCE_RESOLUTION_FILE_EXACT_2026-08-20.md
?? docs/review/PRE_IU4_I5_ACTIVE_EXECUTION_SEAM_IMPLEMENTATION_REREVIEW_RESOLUTION_FILE_EXACT_2026-08-20.md
?? docs/review/PRE_IU4_I6_RECOVERY_MONITORING_PROJECTION_FILE_EXACT_IMPLEMENTATION_EVIDENCE_2026-08-20.md
?? docs/review/PRE_IU4_I6_RECOVERY_MONITORING_PROJECTION_FILE_EXACT_MANDATE_2026-08-20.md
?? docs/review/PRE_IU4_I6_RECOVERY_MONITORING_PROJECTION_FILE_EXACT_MANDATE_INDEPENDENT_READONLY_REREVIEW_2026-08-21.md
?? docs/review/PRE_IU4_I6_RECOVERY_MONITORING_PROJECTION_FILE_EXACT_MANDATE_INDEPENDENT_READONLY_REREVIEW_2_2026-08-21.md
?? docs/review/PRE_IU4_I6_RECOVERY_MONITORING_PROJECTION_FILE_EXACT_MANDATE_INDEPENDENT_READONLY_REREVIEW_3_2026-08-21.md
?? docs/review/PRE_IU4_I6_RECOVERY_MONITORING_PROJECTION_FILE_EXACT_MANDATE_INDEPENDENT_READONLY_REREVIEW_4_2026-08-21.md
?? docs/review/PRE_IU4_I6_RECOVERY_MONITORING_PROJECTION_FILE_EXACT_MANDATE_INDEPENDENT_READONLY_REREVIEW_5_2026-08-21.md
?? docs/review/PRE_IU4_I6_RECOVERY_MONITORING_PROJECTION_FILE_EXACT_MANDATE_REREVIEW_2_RESOLUTION_FILE_EXACT_2026-08-21.md
?? docs/review/PRE_IU4_I6_RECOVERY_MONITORING_PROJECTION_FILE_EXACT_MANDATE_REREVIEW_3_RESOLUTION_FILE_EXACT_2026-08-21.md
?? docs/review/PRE_IU4_I6_RECOVERY_MONITORING_PROJECTION_FILE_EXACT_MANDATE_REREVIEW_4_RESOLUTION_FILE_EXACT_2026-08-21.md
?? docs/review/PRE_IU4_I6_RECOVERY_MONITORING_PROJECTION_FILE_EXACT_MANDATE_REREVIEW_RESOLUTION_FILE_EXACT_2026-08-21.md
?? docs/review/PRE_IU4_I6_RECOVERY_MONITORING_PROJECTION_IMPLEMENTATION_INDEPENDENT_READONLY_FILE_EXACT_REREVIEW_2026-08-21.md
?? docs/review/PRE_IU4_WORKSTATION_FULL_HISTORY_SHADOW_OBSERVATION_AUTHORIZATION_2026-08-17.md
?? live_l1/core/paper_execution_control.py
?? live_l1/core/paper_iu4_runtime_gate.py
?? live_l1/core/terminal_parent_guardian.py
?? live_l1/core/terminal_persistence_worker.py
?? live_l1/core/terminal_runtime_protocol.py
?? live_l1/native/terminal_handoff_revocation_attestor.c
?? live_l1/native/terminal_kernel_lease_shim.c
?? live_l1/native/terminal_lease_fault_fixture.c
?? live_l1/native/terminal_lease_protocol_v14.h
?? live_l1/native/terminal_native_trip_broker.c
?? live_l1/native/terminal_runtime_socket_lsm_guard.bpf.c
?? live_l1/state/iu4_lifecycle_ledger.py
?? live_l1/state/paper_iu4_recovery_projection.py
?? live_l1/tools/collect_terminal_lease_host_closure.py
?? live_l1/tools/terminal_lease_side_effect_observer.py
?? live_l1/tools/validate_iu4_shadow_observation.py
?? live_l1/tools/validate_terminal_lease_capability.py
?? scripts/build_rcc002_spec_bundle.py
?? tests/live_l1/test_iu4_lifecycle_ledger.py
?? tests/live_l1/test_paper_atomic_coordinator_v2.py
?? tests/live_l1/test_paper_execution_control.py
?? tests/live_l1/test_paper_iu4_adapter_v2.py
?? tests/live_l1/test_paper_iu4_execution_seam_v2.py
?? tests/live_l1/test_paper_iu4_recovery_projection.py
?? tests/live_l1/test_paper_iu4_runtime_gate.py
?? tests/live_l1/test_terminal_lease_capability.py
?? tests/live_l1/test_terminal_parent_guardian.py
?? tests/live_l1/test_terminal_persistence_worker.py
?? tests/live_l1/test_validate_iu4_shadow_observation.py
```

## 8. Final boundary

```text
I6_RESULT:PASS
IMPLEMENTATION_REREVIEW_14_BLOCKERS_RESOLVED:HIGH_B1_B_INHERITED_FACTORY_EXACT_TYPE_BOUNDARY
REREVIEW_11_RESULT:NOT_READY_HIGH_B1_TYPE_CANONICALITY_AND_SERIALIZATION_AUTHORITY
REREVIEW_10_B1_B2_B3_STATUS:SUPERSEDED
REREVIEW_8_B1_STATUS:SUPERSEDED
REREVIEW_8_B3_PRESERVATION:PASS
REREVIEW_7_B4_PRESERVATION:PASS
REREVIEW_7_B2_PRESERVATION:PASS
EXACT_IMPLEMENTATION_PATHS:6
FOCUSED_TESTS:88_OF_88_PASS
FULL_LIVE_DISCOVERY:NOT_EXECUTED_EXCLUDED_MODULE_IMPORT_BOUNDARY
TEST_FAILURES:0
TEST_ERRORS:0
TEST_SKIPS:0
OPERATIONAL_ENFORCED_START_AUTHORIZED:NO
ACTIVE_V2_CONSUMER_AUTHORIZED:NO
I7_AUTHORIZED:NO
I8_AUTHORIZED:NO
ENFORCED_ACTIVATION_AUTHORIZED:NO
NEXT_REQUIRED_STEP:NEW_SEPARATE_INDEPENDENT_READONLY_FILE_EXACT_REREVIEW_OF_I6_REREVIEW_14_RESOLUTION
```

The whole-file SHA-256 is intentionally calculated externally and is not
meaningfully self-claimed by this document. The self-binding payload below is
defined byte-exactly: the file is UTF-8, contains no CR bytes, uses LF as its
only line ending and has exactly one final binding line. The payload is the
SHA-256 of every byte before that final binding line, including the LF that
terminates the immediately preceding line. The complete final binding line,
including its terminal LF, is excluded from the payload.

EVIDENCE_PAYLOAD_SHA256:a0681ceee96ecb22c3441ca0e225b8891f6368eb33b8d737b46f760e4c731cd7
