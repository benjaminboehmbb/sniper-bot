# Pre-IU4 I6 Recovery, Monitoring and Projection — File-Exact Mandate — 2026-08-20

## 1. Authority decision

```text
REQUESTED_AUTHORITY:SEPARATE_FILE_EXACT_AUTHORITY_REQUIRED_BEFORE_ANY_I6_OR_ACTIVATION_WORK
MANDATE_ID:IU4-I6-RECOVERY-MONITORING-PROJECTION-FILE-EXACT-MANDATE
MANDATE_REVISION:5
PRIOR_MANDATE_SHA256:a5856d61b1450e9563a266abdc1abcbd0cd8cdd0f3538f804aa5ade10fe551f8
PRIOR_MANDATE_LINES:1242
PRIOR_MANDATE_REREVIEW_SHA256:bb2d4364eed87dcaf01f1f5a84039ad36519ed4bcbf7bd6b425892d780c56971
PRIOR_MANDATE_REREVIEW_LINES:250
PRIOR_MANDATE_REREVIEW_RESULT:NOT_READY_1_BLOCKER
MANDATE_RESULT:AUTHORIZED_PENDING_INDEPENDENT_REREVIEW
I6_IMPLEMENTATION_AUTHORIZED:YES_WITHIN_EXACT_SCOPE_AFTER_READY_REREVIEW
I6_IMPLEMENTATION_ENTERED:NO
I6_EVIDENCE_CREATED:NO
I6_INDEPENDENT_ACCEPTANCE:NOT_READY
OPERATIONAL_ENFORCED_START_AUTHORIZED:NO
ACTIVE_V2_CONSUMER_AUTHORIZED:NO
I7_AUTHORIZED:NO
I8_AUTHORIZED:NO
ENFORCED_ACTIVATION_AUTHORIZED:NO
EXCHANGE_AUTHORIZED:NO
LIVE_AUTHORIZED:NO
```

This record is the separate file-exact authority required by the accepted I5
boundary. It authorizes only a later, separately invoked I6 implementation
package after an independent read-only rereview of this exact mandate returns
`READY`. It does not implement I6, create an owner, consume an authorization,
materialize State, publish a projection, start a Loop or activate ENFORCED.

The I6 package is an offline and synthetically testable implementation of the
Revision-21 package named **Recovery, Monitoring and Projection**. It includes
manual Restart/Recovery, Owner-Epoch Handoffs, Clean Genesis contracts,
journal-first Terminal-Gap Reconciliation, Authority-Root Reconciliation,
version-aware monitoring and idempotent post-commit compatibility projection.
No operational caller is authorized in I6.

## 2. Controlling identity and accepted chain

```text
CANONICAL_REPOSITORY:/home/benja/projects/sniper-bot
BRANCH:main
HEAD:c7ce0452aa2ccbf08c462784d68fa07b3dfe9595
MAIN:c7ce0452aa2ccbf08c462784d68fa07b3dfe9595
ORIGIN_MAIN:89e13fecd1ab549ca7099818b1c9ad4984cb6f7a
MAIN_AHEAD_OF_ORIGIN:6
MAIN_BEHIND_ORIGIN:0
```

| Controlling artifact | SHA-256 | Lines / entries | Status |
|---|---|---:|---|
| Revision-21 specification | `ab8f80720a1d8fe49b9085bce63658bcaecf7f0a3ea70fb555559223090824e0` | 4,605 | controlling |
| final independent I2 rereview | `5a59ad8c97ebae85148661fe0e3bedab643c7f12ae2c8d4e87272447c0616679` | 300 | READY, 97/97 |
| final I3 Evidence | `20846284ffad9e8b755dd6a3b74f963d8d2c6ee1519fafdd0bc1275f2e33c390` | 463 | accepted |
| final independent I3 rereview 6 | `03790420534e38c7e36d1824a472dfd80763340dacec8847ddf5072d55db0c9f` | 191 | READY |
| final I4 Evidence | `068c2ba2661031843a13dd3f2c4684f9340f432b90b192b6b7492dae8968270d` | 403 | accepted |
| final independent I4 rereview 3 | `c6d8bbcb35572a364b74a47eb9ad817240a8b0cce70e514942bb674d3861c38b` | 191 | READY |
| corrected I5 durable-provenance mandate | `a688773cc10dd6c573e7c019245639c010a3b0abb49fb301249aeebeba182a91` | 633 | controlling I5 authority |
| I5 mandate independent rereview 2 | `934bf4a9010aff61796cc2c7c09f54380c5527546bea6e4bc25b5a17933bfd59` | 242 | READY |
| final I5 Resolution 2 | `4512288b16541f659b434000114853f05e457acf5df4e3e779c14b03d44b2985` | 237 | closed final test/Evidence findings |
| final I5 Evidence | `33d18b64bc92d0f5631d3a8306010e8889bb69085d7ce4e77c36c1fd1e185b65` | 633 | accepted candidate Evidence |
| final independent I5 rereview 3 | `9031ec6ef31d61787d46082dab50c59823bb0ba45155cba2b9abc5928f6d96d9` | 246 | READY, 0/0/0/0 |
| I6 mandate revision 1 independent rereview | `85667a19f4e9a354439ee4557ee81d581b25a10427ce111422c32a2654b08d08` | 309 | NOT_READY, 4/0/0/0; all findings resolved by revision 2 |
| I6 mandate revision 1 Resolution | `1ca8a849199e5f5f35923c64dd8e9ba96068233361a790180b208b9fb55e0ae6` | 320 | produced mandate revision 2 |
| I6 mandate revision 2 independent rereview | `ac9b33ff269d5e87d5b658dd4a7ca84258e3c51cfb4bd6a6282cfaa607c942d8` | 270 | NOT_READY, 3/0/0/0; all findings resolved by revision 3 |
| I6 mandate revision 2 Resolution | `9e428c3ad582a2ef3140faea8da22d6349652fe84565bbf189da9256d5a3c031` | 363 | produced mandate revision 3 |
| I6 mandate revision 3 independent rereview | `98f110ac62727c3c07c83fc585c1de0684a6739d32af7652647e3f51f031e168` | 286 | NOT_READY, 2/0/0/0; all findings resolved by revision 4 |
| I6 mandate revision 3 Resolution | `f0cd24007ae27232c1fe5c206a04dbbd91f664aa9f71dd0dc3b7052c40bc0e40` | 337 | produced mandate revision 4 |
| I6 mandate revision 4 independent rereview | `bb2d4364eed87dcaf01f1f5a84039ad36519ed4bcbf7bd6b425892d780c56971` | 250 | NOT_READY, 1/0/0/0; all findings resolved by revision 5 |
| I2 Preservation package | `3af14ff2e270d7d3ca09c1279da7d64e6d720630d06a0c5f45b6786237782037` | 1,318 entries | immutable |
| I2 Freeze manifest | `ad154c0eda13470920878873ed170368cc8f4c43591400a07592a77b179d9e16` | 60 | immutable |

Revision 21 Sections 7.6–7.7, 9, 14–18, 19.2, 20 I6 and 21.5–21.7
control. The accepted I2 Ledger and authorization types remain the sole
Lifecycle authority; the accepted I3 Coordinator journal remains the sole
Atomic recovery authority; accepted I4/I5 semantics remain unchanged.

## 3. Objective and hard ceiling

### 3.1 Objective

The later I6 implementation must provide one strict, versioned and
content-addressed boundary that can, only under explicit caller-supplied
authority and only on caller-supplied roots:

1. classify Legacy and Atomic heads without defaults;
2. build and validate Clean-Genesis and two-direction Handoff artifacts;
3. execute self-referentially safe PREPARE → target publication → read-only
   reconciliation → COMMIT operations;
4. consume a matching Restart/Recovery Authorization exactly once before any
   authorized materialization;
5. rematerialize only an already durable Atomic journal head;
6. reconcile an unclosed Runtime Session journal-first and conservatively;
7. prove the current Atomic State descends from the committed Authority root;
8. generate idempotent, explicitly non-authoritative Legacy compatibility
   projections only after commit; and
9. produce a strict read-only health result including Projection lag and all
   I6 safety/authority bindings.

### 3.2 Hard ceiling

I6 adds no Loop branch, Runtime-Gate decision, Adapter action, Execution
consumer, launcher command, profile, Authorization payload, credential, daemon,
network endpoint or operating-system process. The new I6 API is callable only
by tests or a future separately authorized I7/I8 integration. All mutation
tests use fresh temporary roots. No command in this package may point at
`live_state`, `live_logs`, an operational journal, an external Authorization or
an Exchange.

The package does not implement I7 workstation validation or I8 activation. It
does not authorize `RUNTIME_SESSION_OPEN`, operational ENFORCED start, Legacy
exit-only execution, automatic owner switching or automatic Recovery.

## 4. Exact authorized later implementation file set

Exactly six paths may change after this mandate receives independent `READY`.

| Operation | Path | Mandate-time SHA-256 / status | Lines | Authorized I6 content only |
|---|---|---|---:|---|
| MODIFY | `live_l1/state/paper_atomic_coordinator.py` | `446ae8712d09bc52f950587a2e3ecec0c60fd21b3c9150a8886af1b3b2b4f9ec` | 5,796 | additive typed lifecycle publication/materialization primitives, Authority-root ancestry validation and journal-first Terminal-Gap operations; no Tick/Control effect change |
| MODIFY | `live_l1/state/models.py` | `3254d2f1a6509ec5f8f623dd8f286f60cfcc108f66f2d8eb107338d795115c7e` | 27 | additive full Legacy S4/Handoff projection model only; existing `PositionStateS2` and `RiskStateS4` byte/behavior compatibility |
| MODIFY | `live_l1/state/state_store.py` | `50a85cf6bd382850d39e69cd785a5dc2ded0a66a1d82856b4baa11877bdba177` | 220 | strict explicit Legacy safety snapshot/projection read/write helpers; never an ENFORCED recovery authority and no change to Schema-1 `load_or_init_state`/`persist_state` behavior |
| CREATE | `live_l1/state/paper_iu4_recovery_projection.py` | absent in worktree and HEAD | 0 | strict I6 artifacts, pure classifiers, lifecycle orchestration, Recovery, Handoff/Genesis, reconciliation, projection and monitoring result |
| CREATE | `tests/live_l1/test_paper_iu4_recovery_projection.py` | absent in worktree and HEAD | 0 | the single focused I6 schema, lifecycle, handoff, recovery, projection, monitoring, fault and no-activation matrix |
| CREATE | `docs/review/PRE_IU4_I6_RECOVERY_MONITORING_PROJECTION_FILE_EXACT_IMPLEMENTATION_EVIDENCE_2026-08-20.md` | absent in worktree and HEAD | 0 | final exact identities, commands, matrices, Preservation, scope and result after all tests pass |

No seventh path is authorized. The mandate file itself is the only artifact
created in this turn and is governance, not part of the later six-path package.

The three modified source paths were previously Preservation inputs and are
intentionally released only for the exact I6 additions above. Historical I3–I5
Evidence and rereviews remain byte-identical. The accepted Ledger, Startup
Gate, Runtime Gate, Adapter, Loop and Execution bytes remain read-only inputs.

## 5. Explicit read-only Preservation boundary

| Path | Required SHA-256 | Lines / mode |
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
| `archive/IU4_I2_FREEZE_20260820/IU4_I2_PRESERVATION_20260820.tar.gz` | `3af14ff2e270d7d3ca09c1279da7d64e6d720630d06a0c5f45b6786237782037` | `0444`, 1,318 entries |
| `archive/IU4_I2_FREEZE_20260820/FREEZE_MANIFEST.txt` | `ad154c0eda13470920878873ed170368cc8f4c43591400a07592a77b179d9e16` | `0444`, 60 lines |

The Freeze directory remains mode `0555`. All prior mandates, Resolutions,
Evidence and rereviews remain immutable. No archived copy is regenerated.

## 6. Required implementation order

The later I6 implementation workstream must:

1. reverify every Section-2, Section-4 and Section-5 identity and absence;
2. rerun all mandate-time baselines before mutation;
3. create the focused I6 test first with strict schemas and negative matrices;
4. add the complete Legacy S4 projection model without changing V1 models;
5. add strict State Store projection helpers without changing Legacy V1 paths;
6. add only the lifecycle-safe Coordinator primitives required by the tests;
7. implement the versioned I6 artifacts and orchestrator;
8. prove Genesis, both Handoffs, Recovery, Terminal Gap, root ancestry,
   Projection and monitoring entirely on fresh temporary roots;
9. rerun focused, adjacent, broad, compile, Preservation and scope gates;
10. create Evidence only after every required row passes; and
11. stop without PASS Evidence if any condition in Section 18 fails.

No skip, xfail, reduced matrix, fixture-only proof, mocked successful durable
write without readback, hand-edited Ledger/Journal or real runtime root is
accepted.

## 7. Strict I6 artifact contracts

All I6 artifacts are frozen dataclasses with exact primitive types, no
subclasses, no bool-as-int, no unknown or missing fields, canonical UTC, exact
lowercase 64-hex SHA-256 values, finite canonical Decimal strings and
content-addressed IDs/fingerprints. `from_record()` must reject any input that
is not byte-semantically equal to `to_record()` after parsing.

### 7.1 `IU4LegacySafetySnapshotV1`

The artifact binds schema/artifact type, System-State ID, symbol, source path
and checksum, Owner Epoch and Authority Generation; complete Legacy S2;
complete S4 `kill_level`, cooldown, `trades_today`, canonical `loss_today`,
`anomaly_counter`, `trades_6h`, last-trade timestamp and reason codes;
Loss-Cluster State/fingerprint; Throttle State/fingerprint; Progress Cursor;
all component fingerprints; and its own fingerprint. No field has a runtime
default. Missing `loss_today` or `anomaly_counter` is invalid.

### 7.2 `IU4StateHandoffManifestV1`

The manifest binds exactly one direction `LEGACY_TO_PEE` or `PEE_TO_LEGACY`;
repository commit, symbol, Coordinator and System-State ID; source and
competing State paths/schemas/checksums/fingerprints; complete source safety
snapshot and target business/core fingerprints; previous/new Owner Epoch;
source Authority Generation/Commit Anchor; planned Generation; full
deterministic S2/S4/Loss/Throttle/Cursor mapping; operator, UTC and Approval
reference/fingerprint; unique operation attempt ID; and manifest fingerprint.
The post-PREPARE full Target-State fingerprint is not a manifest field and is
bound only by COMMIT.

### 7.3 `IU4CleanGenesisManifestV1`

The manifest binds symbol, Starting Equity, all profile IDs/fingerprints,
Coordinator/System-State ID, `state_owner_epoch=PEE`, S2 FLAT, complete S4V2,
explicit empty Loss V2 with revision/fingerprint, initial Throttle/Cooldown,
initial Cursor, sequence `0`, journal head `EMPTY`, empty journal-directory
inventory fingerprint, all component/cross-State fingerprints and paths,
absence proofs for competing Legacy/Atomic heads, operator, UTC, separate
Approval reference/fingerprint, process/operation attempt IDs, and manifest
fingerprint. No value is inferred from a runtime default.

### 7.4 `IU4CompatibilityProjectionV1`

The record binds `non_authoritative_projection=true`, projection schema/type,
projection ID, Atomic transaction event/fingerprint/sequence/journal head,
Atomic State fingerprint and Authority Generation/PREPARE fingerprint,
complete projected Legacy safety payload, source and target paths/checksums,
projected-at UTC and projection fingerprint. Economics are copied as canonical
strings and never recalculated. The projection contains no owner claim and is
never a Recovery input.

### 7.5 `IU4PersistenceWorkerDeathTrustAnchorV1` and
`IU4PersistenceWorkerExclusionProofV1`

I6 Terminal-Gap reconciliation supports exactly one exclusion mechanism:
confirmed process death plus reap. `HIGHER_DURABLE_FENCING_TOKEN`, publication
of a replacement token, post-write conflict detection and any fixture-only
fencing substitute are explicitly unsupported and invalid. This restriction
matches the frozen `TerminalPersistenceWorkerV8`, which does not consult an
external durable fence register. I6 must never claim that publishing a higher
token prevented an old writer append.

The caller supplies exactly one frozen trust anchor of exact type
`IU4PersistenceWorkerDeathTrustAnchorV1`. Its canonical record has exactly:

```text
schema_version
artifact_type
trust_anchor_id
allowed_attestor_type
trusted_attestor_id
trusted_attestor_executable_sha256
trusted_collector_id
trusted_source_evidence_sha256
expected_boot_id
expected_runtime_session_id
approval_reference
approval_fingerprint
trusted_anchor_registry_id
trusted_anchor_registry_fingerprint
valid_from_utc
valid_until_utc
trust_anchor_fingerprint
```

Schema is primitive integer `1`; artifact type is exactly
`iu4_persistence_worker_death_trust_anchor_v1`; `allowed_attestor_type` is
exactly `TERMINAL_PARENT_GUARDIAN_V13` or `NATIVE_TRIP_BROKER_V10`.
`valid_from_utc < valid_until_utc` and the proof observation must fall inside
that closed interval. Approval and registry identities/fingerprints are
nonempty and exact. The anchor ID hashes the canonical sorted-key payload
excluding anchor ID/fingerprint; its fingerprint hashes the complete canonical
record excluding only its fingerprint. No proof is trusted from its own
content address alone.

The exact-type `IU4PersistenceWorkerExclusionProofV1` canonical record has
exactly:

```text
schema_version
artifact_type
worker_exclusion_proof_id
proof_mode
runtime_session_id
runtime_session_open_event_id
runtime_session_open_record_fingerprint
authority_generation_id
authority_commit_anchor
coordinator_id
journal_root_fingerprint
old_worker_id
old_worker_boot_id
old_worker_pid
old_worker_start_time_ns
old_broker_generation_id
old_worker_generation_id
attestor_type
attestor_id
attestor_executable_sha256
collector_id
source_evidence_id
source_evidence_sha256
observed_at_utc
death_evidence_kind
observed_pidfd_id
pidfd_exit_observed
waitid_reaped
death_exit_status_class
reap_evidence_fingerprint
death_observation_sequence
worker_append_handle_closed
surviving_writer_holder_count
append_handle_inventory_fingerprint
proof_fingerprint
```

Schema is primitive integer `1`; artifact type is exactly
`iu4_persistence_worker_exclusion_proof_v1`; `proof_mode` is exactly
`PROCESS_DEATH`; `death_evidence_kind` is exactly
`PIDFD_EXIT_AND_REAP_ATTESTATION`; `death_exit_status_class` is exactly
`EXITED` or `SIGNALED`. PID, start time, generations and observation sequence
are primitive positive integers except a broker generation may be zero.
`pidfd_exit_observed`, `waitid_reaped` and `worker_append_handle_closed` are
exact primitive `True`; `surviving_writer_holder_count` is exact primitive
integer `0`. The proof ID hashes the canonical sorted-key payload excluding
proof ID/fingerprint; its fingerprint hashes the complete canonical record
excluding only the fingerprint.

Validation accepts no mapping, subclass, lookalike or Boolean-as-integer. It
first checks exact proof and anchor types/schemas, then canonical IDs and
fingerprints. The validator also requires separate exact primitive
`expected_death_trust_anchor_id`, `expected_death_trust_anchor_fingerprint`,
`expected_approval_fingerprint` and `expected_trusted_anchor_registry_fingerprint`
arguments from the prebound out-of-band Approval boundary; none is derived
from either artifact. It next checks those four values against the anchor,
then exact trust-anchor equality for attestor type/ID/executable,
collector, source-Evidence SHA, boot ID and Runtime Session, then the validity
window, then Session/OPEN, Worker/Broker, Authority, Coordinator and Journal
bindings, and finally the three death/reap/handle-closure facts. Any failure is
`PEE_IU4_TERMINAL_GUARDIAN_INVALID` before State, Journal, Ledger, Projection
or other I6 mutation. Reuse is idempotent only for identical proof bytes and
the same Terminal-Gap attempt; same ID with divergent bytes is conflict.

Focused tests must instantiate the accepted `TerminalPersistenceWorkerV8`
class directly: a live/unreaped instance or any surviving append-handle holder
must make the proof fail before reconciliation, and the class must demonstrate
that an old live writer could otherwise append. Only a separately trusted,
exactly bound death-and-reap attestation with zero surviving holders can permit
Terminal-Gap reconciliation. I6 itself launches, probes, kills or reaps no
operational process and never uses a real operational runtime root.

### 7.6 `IU4ProjectionCursorV1`

This is the sole durable Projection progress authority and is explicitly
non-authoritative for trading State and Recovery. Its canonical record has
exactly:

```text
schema_version
artifact_type
projection_cursor_id
authority_generation_id
authority_prepare_record_fingerprint
projection_base_sequence
projection_base_journal_head
projection_base_state_fingerprint
previous_atomic_transaction_sequence
previous_atomic_journal_head
previous_atomic_state_fingerprint
atomic_transaction_event_id
atomic_transaction_fingerprint
atomic_transaction_sequence
atomic_journal_head
atomic_state_fingerprint
projection_id
projection_fingerprint
projection_output_bytes_sha256
previous_projection_cursor_id
previous_projection_cursor_fingerprint
published_at_utc
projection_root_inventory_fingerprint
projection_cursor_fingerprint
```

Schema is primitive integer `1`; artifact type is exactly
`iu4_projection_cursor_v1`; sequences are primitive nonnegative integers.
Cursor ID hashes the canonical sorted-key payload excluding Cursor ID and
fingerprint; Cursor fingerprint hashes the full canonical record excluding
only its fingerprint.

The immutable Projection base is the accepted Authority-COMMIT target State:
sequence `0`, journal head `EMPTY`, and exact target State fingerprint. The
first Cursor must project Atomic transaction sequence `1`, use `NONE` for both
previous-Cursor fields, and bind its previous Atomic sequence/head/state to
that base. Every later Cursor must satisfy all of the following without
exception: `atomic_transaction_sequence == previous_cursor.atomic_transaction_sequence + 1`;
its previous-Atomic triple equals the previous Cursor current-Atomic triple;
the transaction `state_before` and previous journal head equal that triple;
its previous-Cursor ID/fingerprint equal the observed Cursor; and the new
transaction/head/state form the exact next hash-valid Coordinator transition.
Catch-up replays every transaction in ascending order. It may never jump from
sequence 1 to 10, batch-publish only the tip or suppress Projection Lag until
all intervening outputs and Cursors have been durably published.

The I6 Projection API receives exactly one built-in `str` argument named
`caller_root_path`; string subclasses and path-like lookalikes are rejected.
It must be an absolute POSIX path in Unicode NFC, encode with strict UTF-8,
contain no NUL, `.` or `..` component, not equal `/`, and contain no trailing
slash. `caller_root_realpath` is exactly `os.path.realpath(caller_root_path)`;
the original `caller_root_path`, `os.path.abspath(caller_root_path)` and
`caller_root_realpath` must be three byte-equal strings. They retain the same
NFC/UTF-8/no-trailing-slash form, identify an existing directory and contain
no symlink component. Repeated separators and any other spelling normalized by
`abspath`/`realpath` therefore reject. Non-UTF-8 filesystem names are
unsupported and fail closed.

`projection_root_path` is not a second input. It is derived exactly by the
literal concatenation `caller_root_realpath + "/projection"`. After its
root-confined creation/readback it must itself equal its absolute realpath and
contain no symlink component. The caller-root-relative layout is exactly:

```text
projection/.projection_v1.lock
projection/records/{transaction_sequence_20_digits}_{projection_id}.json
projection/.projection_cursor_v1.tmp.{operation_attempt_id}
projection/projection_cursor_v1.json
```

All paths are root-confined, regular and contain no symlink component. Under
the sole exclusive root lock, the implementation validates the reconciled
current committable Atomic head, writes each next Projection record create-new,
file-syncs, directory-syncs and byte/hash-readbacks it, then publishes its
Cursor by same-directory temporary create-new, file sync, atomic replace,
directory sync and byte/hash readback. Cursor publication is CAS-bound to the
observed previous Cursor fingerprint.

`projection_root_realpath_sha256` is SHA-256 over the exact byte domain
`b"IU4_PROJECTION_ROOT_V1\x00" + projection_root_path.encode("utf-8", "strict")`.
The path bytes contain neither trailing slash nor newline. No URI escaping,
case folding, platform separator conversion or alternative Unicode
normalization is permitted.

`projection_root_inventory_fingerprint` is SHA-256 of canonical sorted-key
JSON bytes with exactly:

```json
{"entries":[],"observation_point":"AFTER_OUTPUT_READBACK_BEFORE_CURSOR_TEMP_CREATE","projection_root_realpath_sha256":"<lowerhex64>","schema_version":1}
```

Every `relative_path` is computed relative to `projection_root_path`, never
relative to `caller_root_path`; therefore the first durable record is spelled
`records/...`, never `projection/records/...`. Separators are literal `/`,
components are strict UTF-8 NFC without `.` or `..`, and no relative path has a
leading or trailing slash. `entries` is a lexicographically UTF-8-byte-sorted
array. Each entry is
exactly `[relative_path,"REGULAR",mode_4_octal_string,size_decimal_string,sha256]`.
It includes every durable `records/*.json`, including the newly
read-back output. It excludes exactly directories,
`.projection_v1.lock`, `projection_cursor_v1.json` and
the single exact current-lock-owned
`.projection_cursor_v1.tmp.{operation_attempt_id}`. The operation
attempt ID is the canonical caller-supplied attempt bound to the held lock; a
second, stale or malformed temporary name is rejected. A symlink, non-regular
file or unknown regular file is rejected rather than silently excluded.
The inventory is observed only after output readback and before Cursor temp
creation, so the Cursor and its temp file cannot create a hash cycle. The test
matrix includes fixed bytes and a fixed inventory fingerprint.

Focused tests and Evidence must include fixed vectors for caller root,
projection root, domain-separated realpath bytes/hash, relative record names,
complete inventory JSON bytes and fingerprint. Parent-root versus child-root,
leading/trailing slash, alternate relative base, `.`/`..`, symlink component,
non-NFC, strict-UTF-8 failure and platform-separator variants are mandatory
negative rows. Cursor validation and every Projection fault row use this same
single definition.

Identical transaction/projection/output bytes replay idempotently. Divergent
bytes, concurrent Cursor change, skipped/gapped/forked/out-of-order sequence,
stale/ahead/rollback State, wrong previous link or Authority change is a stable
conflict with no Projection or Atomic mutation. After crash, a durable output
without advanced Cursor may advance only the exact next matching Cursor; a
Cursor without its exact output is corruption and is never guessed or rolled
back.

### 7.7 `IU4TerminalMonitoringObservationV1`

Monitoring accepts exactly one frozen, content-addressed caller-supplied
terminal observation and never probes a real process, PIDFD, socket, BPF object
or operational runtime root. The exact top-level fields remain:

```text
schema_version artifact_type terminal_monitoring_observation_id
runtime_session_id runtime_session_open_record_fingerprint
authority_generation_id authority_commit_anchor atomic_root_fingerprint
source_collector_id source_evidence_id source_evidence_sha256
observation_sequence observed_at_utc role_readiness lease_and_self_death
pidfd_targets control_word_and_memfd signal_envelope runtime_channels
seccomp_lsm_capability runtime_close_fsm heartbeat_and_budgets
failstop_and_terminal_gap completion_provenance safety_resource_schema
observation_fingerprint
```

Schema is exact primitive integer `1`; artifact type is exactly
`iu4_terminal_monitoring_observation_v1`; observation sequence is primitive
nonnegative integer. Observation ID hashes the canonical payload excluding ID
and fingerprint; observation fingerprint hashes the full canonical record
excluding only fingerprint. All IDs are nonempty canonical ASCII strings,
all SHA/fingerprint fields are lowercase hex64, all PIDs/TIDs and monotonic-ns
times are primitive positive integers, all counts/sequences and millisecond
values are primitive nonnegative integers, all booleans are exact primitive
booleans, and all tuples are immutable canonically serialized arrays. No
subclass, mapping lookalike, coercion, unknown/missing field or unknown enum is
accepted.

The twelve nested records have the following exact fields, types, closed
values and PASS invariants. A named boolean must have the stated PASS value;
status values outside the listed enum are schema errors.

1. `role_readiness`: the three `{parent_guardian,native_trip_broker,
   persistence_worker}_{ready,id,pid,start_time_ns}` quartets; and
   `listener_owner_role`, `worker_ack_receiver_role`, `renewal_sender_role`,
   `close_approval_sender_role`, `worker_request_sender_role`. Ready values
   must be `True`; IDs/PIDs/start times must exactly match the OPEN record.
   Roles are only `PARENT_GUARDIAN_V13`, `NATIVE_TRIP_BROKER_V10`,
   `TERMINAL_PERSISTENCE_WORKER_V8` or `TRADING_CHILD` and must match the
   accepted OPEN ownership matrix.
2. `lease_and_self_death`: `os_lease_type`, `os_lease_identifier`,
   `credentials_capability_fingerprint`, `lease_nonce_sha256`,
   `self_death_timer_armed`, `self_death_timer_id`, `self_death_timer_clock`,
   `self_death_timer_signal`, `self_death_timer_expiry_monotonic_ns`,
   `native_shim_fingerprint`. PASS requires exact `PIDFD_KERNEL_SELF_DEATH`,
   `True`, `CLOCK_BOOTTIME`, `SIGKILL`, positive expiry and exact OPEN/profile
   identities.
3. `pidfd_targets`: exactly `trading_self`, `guardian`, `broker`; each contains
   only `pidfd_id`, `target_pid`, `target_start_time_ns`,
   `sigkill_probe_result`. Probe enum is `PASS|FAIL`; PASS requires `PASS` and
   exact role PID/start-time binding.
4. `control_word_and_memfd`: `control_word_schema`, `control_word_state`,
   `trip_sequence`, `renewal_sequence`, `broker_cas_sequence`,
   `memfd_create_flags`, `initial_seals`, `intermediate_seals`, `final_seals`,
   and `{trading,guardian,broker,worker}_mapping_rights`.
   Schema is primitive integer `3`; state enum is
   `RUNNING|CLOSING|TERMINATING|CLOSED`; rights enum is
   `NONE|READ_ONLY|READ_WRITE`; flag/seal tuples and rights must exactly equal
   the accepted OPEN/profile matrix; sequences are nondecreasing and the
   broker CAS sequence may not exceed the trip sequence.
5. `signal_envelope`: `signal_envelope_id`, `signal_envelope_fingerprint`,
   `signal_mask_fingerprint`, `signal_disposition_fingerprint`,
   `wait_killable_recv`, `later_signal_change_locked`; both booleans are exact
   `True` and all identities equal the accepted `TerminalTradingSignalEnvelopeV1`.
6. `runtime_channels`: `channel_records` is exactly six records, each with
   `channel_id`, `direction`, `sender_role`, `receiver_role`, `so_peercred`,
   `peer_binding_fingerprint`, `so_passcred`, `so_passrights`, `receiver_tid`,
   `receiver_files_table_fingerprint`, `receiver_tsync_filter_fingerprint`,
   `final_role_filter_fingerprint`, `scm_fds`, `control_buffer_bytes`,
   `queue_inventory_fingerprint`, `fd_inventory_fingerprint`,
   `fdinfo_inventory_fingerprint`, `ofd_inventory_fingerprint`,
   `lock_inventory_fingerprint`, `rights_reject_result`; plus
   `guardian_notification_eventfd_id` and `broker_notification_eventfd_id`.
   Direction is `A_TO_B|B_TO_A`; roles use the Section-7.7 role enum;
   `so_peercred` is exact `{pid:positive int,uid:nonnegative int,gid:nonnegative int}`;
   `so_passcred=0`, `so_passrights=0`, `scm_fds=0`,
   `control_buffer_bytes=0`, `rights_reject_result=EPERM`; all six channel and
   ownership/inventory bindings equal OPEN/profile.
7. `seccomp_lsm_capability`: `seccomp_listener_id`,
   `seccomp_notification_id`, `seccomp_listener_owner`,
   `seccomp_listener_receive_error_status`, `seccomp_filter_hash`, `btf_id`,
   `program_ids`, `map_ids`, `link_ids`, `pin_paths`, `cgroup_ids`,
   `lsm_hook_coverage`, `socket_cookie_tag_inventory_fingerprint`,
   `phase_map_frozen`, `config_map_frozen`, `bpf_cmpxchg_proof_fingerprint`,
   `scalar_seccomp_userspace_authority_matrix`,
   `scalar_seccomp_userspace_authority_matrix_fingerprint`,
   `capability_envelope_fingerprint`. Owner must be
   `NATIVE_TRIP_BROKER_V10`; receive status enum is
   `NONE|EINTR_RETRIED|FATAL` and PASS requires `NONE`; both frozen booleans
   are `True`; `lsm_hook_coverage` is the exact accepted six-hook tuple. The
   scalar matrix is an immutable ordered tuple whose exact records contain only
   `protocol_struct`, `operation`, `seccomp_owner_role`,
   `userspace_owner_role`, `sender_role`, `receiver_role` and
   `scalar_payload_layout_fingerprint`; every value and the aggregate matrix
   fingerprint equal the accepted Section-7.8.1 OPEN/profile binding. All
   other tuples/IDs/fingerprints also equal OPEN/profile.
8. `runtime_close_fsm`: `channel_phase`, `close_fsm_phase`,
   `close_prepare_event_id`, `broker_closed_evidence_id`,
   `close_commit_event_id`, `close_peer_status`, `close_hup_status`,
   `close_timeout_status`, `request_owner_role`, `ack_owner_role`.
   Channel phase enum is
   `LISTENER_HANDOFF|LISTENER_RECEIVED|HANDOFF_REVOKED_GRANTED|BOOTSTRAP|OPEN_DURABLE_GRANTED|RELEASED`;
   close phase enum is `OPEN|CLOSING|PREPARE|BROKER_CLOSED|COMMIT|COMMITTED|FAILED`;
   status enum is `NONE|OK|HUP|TIMEOUT|ERROR`. IDs use `NONE` exactly when the
   corresponding phase has not begun; phase, IDs, statuses and exclusive
   owner roles must be mutually consistent with the Runtime Session record.
9. `heartbeat_and_budgets`: `heartbeat_interval_ms`,
   `heartbeat_last_sequence`, `heartbeat_age_ms`, `capability_probe_age_ms`,
   `capability_probe_expiry_ms`, `clock_source`,
   `terminal_guardian_lease_max_ms`, `terminal_broker_trip_cas_max_ms`,
   `terminal_guardian_trip_dispatch_max_ms`,
   `terminal_kernel_signal_generation_budget_ms`,
   `terminal_failstop_max_ms`, `termination_latch_deadline_ms`. PASS requires
   interval `10`, heartbeat and capability ages `0..25`, capability expiry
   `0..25`, `CLOCK_BOOTTIME`, Guardian lease maximum `25`, Broker Trip-CAS
   maximum `5`, Guardian Trip dispatch maximum `5`, kernel Signal generation
   budget `25`, Fail-stop maximum `100`, and termination latch `1..100`, all in
   primitive integer milliseconds.
10. `failstop_and_terminal_gap`: `failstop_asserted`,
    `pending_signal_status`, `reap_status`, `runtime_session_unclean`,
    `terminal_gap_status`, `liveness_pipe_read_endpoint_id`,
    `liveness_pipe_write_endpoint_id`, `liveness_pipe_inode`,
    `liveness_pipe_capacity_bytes`, `liveness_pipe_exclusive_owner_role`,
    `liveness_pipe_write_forbidden`, `liveness_pipe_payload_bytes`,
    `liveness_pipe_empty`, `liveness_pipe_hup_status`,
    `liveness_pipe_fallback_status`. Pending/reap/terminal statuses use
    `NONE|PENDING|COMPLETE|FAILED`; HUP uses `OBSERVED|NOT_OBSERVED`; fallback
    uses `NOT_REQUIRED|ARMED|TRIPPED|FAILED`; payload bytes is primitive `0`
    and empty/write-forbidden are `True` for PASS; inode and capacity are
    primitive positive integers and exclusive owner equals the accepted OPEN
    role. Fail-stop, unclean Session and Terminal-Gap combinations must equal
    Lifecycle/close state; no unclosed Session may be reported clean.
11. `completion_provenance`: `completion_provenance`,
    `completion_authorization_id`, `completion_consumption_event_id`,
    `completion_startup_attempt_id`, `direct_process_instance_id`,
    `genesis_operation_attempt_id`, `direct_continuation_nonce_hash`,
    `direct_continuation_nonce_preimage_match`, `prior_runtime_session_count`,
    `direct_first_start_eligible`. Provenance is
    `DIRECT|RECOVERED_AFTER_PREPARE`. DIRECT requires the three completion
    fields `NONE`, positive direct/Genesis IDs, exact nonce hash with primitive
    `True` preimage match, prior Session count `0` and eligibility `True`.
    RECOVERED requires exact Authorization/Consumption/Startup bindings and
    uses `NONE`, `False`, nonnegative prior count and eligibility `False` for
    the DIRECT-only fields. This is the complete Clean-Genesis first-start
    admissibility decision; provenance text alone is insufficient.
12. `safety_resource_schema`: `kill_level`, `entry_allowed`,
    `exit_evaluation_allowed`, `runtime_directive`, `reason_codes`,
    `activation_authorization_valid`, `restart_authorization_status`,
    `profile_binding_status`, `resource_reserve_status`, `io_status`,
    `atomic_schema_version`, `lifecycle_schema_version`,
    `projection_schema_version`, `legacy_exit_only_status`. Each field is
    assigned independently and no collective “as applicable” rule exists:
    - `kill_level` is exact built-in `str` enum
      `NONE|SOFT|HARD|EMERGENCY` and must equal S4V2;
    - `entry_allowed` and `exit_evaluation_allowed` are exact primitive
      booleans and must equal S4V2; exit is `True` for `NONE|SOFT` and `False`
      for `HARD|EMERGENCY`, while any non-`NONE` level forces Entry `False`;
    - `runtime_directive` is exact built-in `str` enum
      `CONTINUE|STOP_LOOP|EXIT_PROCESS`, with exact level matrix
      `NONE/SOFT→CONTINUE`, `HARD→STOP_LOOP`,
      `EMERGENCY→EXIT_PROCESS`;
    - `reason_codes` is an immutable ordered tuple of nonempty canonical ASCII
      strings, contains no duplicate and must byte-equal the S4V2 reason tuple;
    - `activation_authorization_valid` is an exact primitive boolean; `True`
      is PASS and `False` is FAIL;
    - `restart_authorization_status` is exact built-in `str` enum
      `NOT_REQUIRED|VALID|MISSING|CONSUMED|MISMATCH`; `NOT_REQUIRED` is PASS
      only for a monitoring-only operation, `VALID` only when the requested
      recovery operation requires and matches fresh authority, and the other
      three values are FAIL;
    - `profile_binding_status` is exact built-in `str` enum
      `MATCH|MISMATCH|MISSING|UNKNOWN_SCHEMA`; only `MATCH` is PASS;
    - `resource_reserve_status` is exact built-in `str` enum
      `PASS|EXHAUSTED|BELOW_MINIMUM|UNKNOWN`; only `PASS` is PASS;
    - `io_status` is exact built-in `str` enum
      `PASS|READ_ERROR|WRITE_ERROR|SYNC_ERROR|PERMISSION_DENIED|UNKNOWN`; only
      `PASS` is PASS;
    - `atomic_schema_version`, `lifecycle_schema_version` and
      `projection_schema_version` are exact primitive integers `2`, `1`, `1`;
      bool and integer subclasses are invalid; and
    - `legacy_exit_only_status` is exact built-in `str` enum
      `NOT_APPLICABLE|REQUIRED|ACTIVE|COMPLETE|INVALID`. PEE Owner requires
      `NOT_APPLICABLE` and PASS; LEGACY OPEN requires `REQUIRED|ACTIVE` and
      yields WARN while Entry remains blocked; completed Legacy exit requires
      `COMPLETE` and PASS; `INVALID` or any Owner/S2 mismatch is FAIL.

    The Group-12 result is FAIL on any failed field, otherwise WARN only for
    valid `REQUIRED|ACTIVE` Legacy exit-only state, otherwise PASS.

The validator checks top-level schema/canonicality, then exact Session,
Generation, Anchor, root and source-Evidence bindings, then groups 1 through 12
in order. The first failure maps deterministically: groups 1-3 and 9 to
`PEE_IU4_TERMINAL_GUARDIAN_INVALID`; group 4 to
`PEE_IU4_TERMINAL_CONTROL_WORD_CONFLICT`; group 5 to
`PEE_IU4_TERMINAL_SIGNAL_ENVELOPE_INVALID`; group 6 to
`PEE_IU4_TERMINAL_TRIP_CHANNEL_INVALID`; group 7 to
`PEE_IU4_TERMINAL_CAPABILITY_ENVELOPE_INVALID`; group 8 to the applicable
`PEE_IU4_RUNTIME_SESSION_CLOSE_*` family; group 10 to
`PEE_IU4_TERMINAL_FAILSTOP_REAP_PENDING`; group 11 to
`PEE_IU4_GENESIS_PROVENANCE_INVALID`; group 12 to the applicable Runtime
Binding/Profile/Schema code. Missing, stale, lookalike, mismatched,
unknown-schema or internally inconsistent observations can never PASS.

Focused tests and Evidence must cover every enum, exact primitive/subclass
boundary, every numeric `boundary-1/boundary/boundary+1`, unknown enum, stale
observation, same-ID divergent bytes, each cross-field inconsistency, every
first-failure precedence row and a fixed complete canonical record/fingerprint.

### 7.8 `IU4RecoveryMonitoringReportV1`

The read-only report is a frozen exact-type artifact. Its canonical record has
exactly these fields and no others:

```text
schema_version
artifact_type
monitoring_report_id
runtime_session_id
runtime_session_open_record_fingerprint
authority_generation_id
authority_commit_anchor
owner_epoch
report_operation
atomic_root_fingerprint
lifecycle_root_inventory_fingerprint
atomic_root_inventory_fingerprint
projection_root_inventory_fingerprint
authorization_valid
runtime_profile_id
runtime_profile_fingerprint
economics_profile_id
economics_profile_fingerprint
entry_throttle_profile_id
entry_throttle_profile_fingerprint
runtime_control_fingerprint
lifecycle_ledger_tip_event_id
lifecycle_ledger_tip_fingerprint
open_prepare_count
runtime_session_status
handoff_or_genesis_manifest_id
handoff_or_genesis_manifest_fingerprint
atomic_journal_sequence
atomic_journal_head
atomic_snapshot_fingerprint
authority_root_ancestry_result
projection_cursor_id
projection_cursor_fingerprint
projection_cursor_sequence
projection_cursor_journal_head
projection_lag_transactions
s2_fingerprint
account_fingerprint
throttle_fingerprint
loss_cluster_fingerprint
s4_fingerprint
entry_quote_fingerprint
progress_cursor_fingerprint
terminal_gap_status
terminal_monitoring_observation_id
terminal_monitoring_observation_fingerprint
role_readiness_result
lease_and_self_death_result
pidfd_targets_result
control_word_and_memfd_result
signal_envelope_result
runtime_channels_result
seccomp_lsm_capability_result
runtime_close_fsm_result
heartbeat_and_budgets_result
failstop_and_terminal_gap_result
completion_provenance_result
safety_resource_schema_result
entry_capability_result
exit_capability_result
overall_result
reason_codes
reported_at_utc
report_fingerprint
```

Schema is exact primitive integer `1`; artifact type is exactly
`iu4_recovery_monitoring_report_v1`. The report ID is SHA-256 of canonical
sorted-key JSON excluding report ID and report fingerprint; report fingerprint
hashes the complete canonical record excluding only report fingerprint.
Unknown/missing fields, subclasses, bool-as-int, noncanonical UTC and
self-consistently refingerprinted divergent inputs are rejected.

All IDs are canonical nonempty ASCII strings and all fingerprints are
lowercase hex64 except only the exact paired absence sentinels defined below.
Journal heads are lowercase hex64 except only the exact initial/absent Cursor
head `EMPTY`. Counts and sequences are primitive nonnegative integers.
`authorization_valid` is exact primitive boolean. `runtime_session_status` is
exact enum
`ABSENT|OPEN_CLEAN|OPEN_UNCLEAN|CLOSED_CLEAN|CLOSED_UNCLEAN`;
`owner_epoch` is exact enum `LEGACY|PEE`; `report_operation` is exact enum
`MONITOR_ONLY|ATOMIC_GENESIS|LEGACY_TO_PEE|PEE_TO_LEGACY|RECOVER_AND_RESTART|COMPLETE_AUTHORITY_PREPARE|RECONCILE_TERMINAL_GAP`;
`authority_root_ancestry_result` is `PASS|FAIL`; each of the exactly twelve
named group-result fields is `PASS|WARN|FAIL`; there is no thirteenth group and
the observation fingerprint is not a group. `entry_capability_result` and
`exit_capability_result` are exact enum
`AVAILABLE|BLOCKED|NOT_APPLICABLE`; `overall_result` is
`PASS|WARN|FAIL`.

The following paired sentinel matrix is exhaustive and bidirectional:

| Object state | ID | Fingerprint | Sequence | Head |
|---|---|---|---:|---|
| Runtime Session `ABSENT`, with no current-Generation `RUNTIME_SESSION_OPEN` in the accepted Ledger | `runtime_session_id=NONE` | `runtime_session_open_record_fingerprint=NONE` | n/a | n/a |
| Runtime Session present | nonempty canonical ASCII | lowercase hex64 | n/a | n/a |
| Handoff/Genesis manifest absent only for `owner_epoch=LEGACY`, `report_operation=MONITOR_ONLY`, `open_prepare_count=0` and no accepted Ledger PREPARE/COMMIT for `ATOMIC_GENESIS|LEGACY_TO_PEE|PEE_TO_LEGACY` in the selected Generation | `handoff_or_genesis_manifest_id=NONE` | `handoff_or_genesis_manifest_fingerprint=NONE` | n/a | n/a |
| Handoff/Genesis manifest present | nonempty canonical ASCII | lowercase hex64 | n/a | n/a |
| Projection Cursor absent before first projection | `projection_cursor_id=NONE` | `projection_cursor_fingerprint=NONE` | exactly `0` | exactly `EMPTY` |
| Projection Cursor present | nonempty canonical ASCII | lowercase hex64 | primitive integer `> 0` | lowercase hex64 |

Runtime Session status `ABSENT` is valid if and only if both Session fields are
`NONE` and the accepted Ledger has no current-Generation Session OPEN; every
other Runtime Session status requires both concrete values and the exact OPEN
record. An absent manifest is valid only under the exact LEGACY/MONITOR_ONLY/
zero-PREPARE/no-operation row above; otherwise both concrete values are
required. An absent Cursor means the durable Cursor file itself is absent and
is valid before its first publication, including an output-only crash row;
durable output is never silently treated as a Cursor. `NONE` is never a valid
fingerprint outside these three paired rows, and `EMPTY` is never a present
Cursor head. Mixed pairs, a concrete ID with `NONE`, `NONE` with a hex64
fingerprint, absent Cursor with nonzero sequence/non-`EMPTY` head, present
Cursor with zero sequence/`EMPTY` head, or `ABSENT` Session with a concrete
OPEN fingerprint are schema errors before report derivation.

The report cross-binds exact observed roots/inventories, Authorization,
profiles/commit, Ledger tip, Authority Generation/Anchor, Owner Epoch,
operation, open PREPARE count,
Runtime Session, Handoff/Genesis manifest, complete Journal/Snapshot ancestry,
Projection Cursor/lag, every business-component fingerprint, Terminal Gap and
the exact Observation ID/fingerprint. Cursor fields use the exact paired row
above only before the first projection. Projection lag is the exact
primitive count `atomic_journal_sequence - projection_cursor_sequence`; a
negative value is invalid.

Group results are derived in the exact Section-7.7 order and may not be caller
chosen. `overall_result=FAIL` if Authorization/root ancestry fails, an open
PREPARE or unclean Session exists, Projection is corrupt/ahead, or any group
is FAIL. Otherwise it is WARN if Projection lag is positive or any group is
WARN; otherwise PASS. Positive lag adds `PEE_IU4_PROJECTION_LAG`, forces Entry
`BLOCKED`, and never grants Recovery authority. Entry and Exit capability
results must equal the complete S4V2/Owner/lag/terminal matrix; HARD or
EMERGENCY makes Exit `BLOCKED`, and an inapplicable capability uses
`NOT_APPLICABLE` only where the Owner matrix expressly has no such capability.

`reason_codes` is an immutable unique tuple ordered by Section-12 precedence:
schema/canonicality, typed input, Session/Authority/root, terminal fail-stop or
unclean Session, open PREPARE/Lifecycle, Atomic ancestry/components,
Projection lag, profile/Authorization, nonterminal warnings. It contains every
and only applicable stable reason. A later WARN/PASS never removes or
downgrades an earlier FAIL. The report only reports; it never mutates, repairs,
deescalates, consumes authority or starts anything.

Focused tests and Evidence must include fixed complete Observation and Report
canonical bytes, IDs and fingerprints; exactly twelve result fields; every
Group-12 per-field enum/type/PASS-WARN-FAIL row; missing/unknown fields;
same-ID divergent bytes; group/report cross-field mismatch; capability and
overall derivation; every first-failure precedence row; fixed Report vectors
for DIRECT first-start without prior Session, permitted absent manifest,
absent Cursor and fully present Session/manifest/Cursor; and every mixed-pair,
sequence/head and status-sentinel negative from the matrix above.

## 8. Owner classification and Handoff matrix

Owner Epoch is derived only from the last valid Authority-COMMIT in the
accepted Lifecycle Ledger. Environment, mode, Legacy State and Atomic Snapshot
are never owner authority.

The exact matrix is mandatory:

| Owner | Legacy S2 | Atomic S2 | Result |
|---|---|---|---|
| LEGACY | OPEN | FLAT | `LEGACY_EXIT_ONLY`; no PEE Entry |
| LEGACY | OPEN | OPEN | `PEE_IU4_HANDOFF_DUAL_OPEN_CONFLICT` |
| LEGACY | FLAT | FLAT | Handoff only with exact `LEGACY_TO_PEE` manifest |
| LEGACY | FLAT | OPEN | `PEE_IU4_HANDOFF_OWNER_EPOCH_INVALID` |
| PEE | FLAT | OPEN | manual PEE Resume candidate after all other gates |
| PEE | FLAT | FLAT | PEE FLAT candidate after all other gates |
| PEE | OPEN | any | `PEE_IU4_HANDOFF_OWNER_EPOCH_INVALID` |
| any | corrupt/missing/unknown | any | `PEE_IU4_HANDOFF_GENESIS_REQUIRED`, except exact Genesis |
| any | any | corrupt/missing/unknown | fail closed |

The effective Kill level is the maximum `NONE < SOFT < HARD < EMERGENCY`; the
latest valid cooldown wins; stricter Loss pause is never silently reset; and
all Trade/Loss/Throttle/Cursor/S4 heads, including `loss_today` and
`anomaly_counter`, map losslessly. `HARD`/`EMERGENCY` never permit Loop start.
Invalid cooldown or any non-lossless mapping returns
`PEE_IU4_HANDOFF_SAFETY_CONFLICT` without mutation.

Both Handoff directions use an exclusive lifecycle/state lock and the exact
self-reference-free order: source reconciliation, target business → planned
Generation → target core, durable PREPARE plus file/directory sync, target
publication plus file/directory sync, read-only target reconciliation, then
exactly one COMMIT. PREPARE alone changes no Owner. A partial operation requires
new `COMPLETE_AUTHORITY_PREPARE`; it is never retried silently.

## 9. Clean Genesis and Authority root

Atomic Genesis is a Lifecycle operation, not a Tick transaction. It validates
empty journal, sequence `0`, head `EMPTY` and absence of competing State under
the exclusive root lock, then follows PREPARE → State → reconcile → COMMIT.
Only COMMIT establishes PEE Owner Epoch.

`DIRECT` COMMIT binds the originating operation/process, Approval,
`direct_process_instance_id`, `genesis_operation_attempt_id` and in-memory
continuation nonce hash. `RECOVERED_AFTER_PREPARE` instead binds the exact fresh
Completion Authorization, Consumption event, Startup Attempt and pre-tip. The
two provenances are mutually exclusive. Completion never starts a Loop and the
next process requires a new `RESTART_ONLY` Authorization.

Reconciliation starts at the Authority-COMMIT-bound Target State. Current
State is accepted only when a complete Journal ancestry reaches the current
head and every transition preserves the same Generation and PREPARE
fingerprint. Ledger tip and COMMIT fingerprint are never inserted into the
Atomic State fingerprint. A locally consistent foreign root returns
`PEE_IU4_AUTHORITY_ROOT_MISMATCH`.

## 10. Manual Restart/Recovery

The exact accepted `IU4RestartRecoveryAuthorizationV1` from the Startup Gate
is a typed input; mappings, subclasses and lookalikes are rejected. Activation
Authorization alone is insufficient.

Before Recovery, PREPARE completion or any future startup release, the I6
orchestrator validates operation, responsible operator, time window, log and
environment manifests, profiles/commit, pre-State, sequence/head/snapshot,
Authority Generation/Anchor, exact pre-attempt Ledger tip and Startup Attempt.
It then appends exactly one durable `RESTART_AUTH_CONSUME` via the accepted
Ledger. Crash before Consumption leaves the Authorization reusable; crash
after Consumption requires a new Authorization. Same ID with divergent payload
is a hard conflict.

`RECOVER_AND_RESTART` may only materialize the `state_after` of an already
durable valid Journal head and then append one bound
`RECOVERY_MATERIALIZATION`. It never creates or changes a transaction or
business value. In I6 the result is `RECOVERY_COMPLETE_LOOP_NOT_AUTHORIZED`;
there is no start call.

`COMPLETE_AUTHORITY_PREPARE` validates/materializes only the exact open
PREPARE target, reconciles it, writes one exact COMMIT with
`RECOVERED_AFTER_PREPARE`, and exits without a Loop. An existing COMMIT, wrong
PREPARE, Target path/schema/core, Generation, Sentinel or stale Consumption is
rejected.

## 11. Journal-first Terminal-Gap Reconciliation

`RECONCILE_TERMINAL_GAP` is allowed only after a fresh matching Consumption,
an exact trusted `IU4PersistenceWorkerDeathTrustAnchorV1` and an exact
`IU4PersistenceWorkerExclusionProofV1` whose sole mode is `PROCESS_DEATH`.
Untyped, stale, wrong-Session, wrong-Worker, live, unreaped,
surviving-handle, replay-conflicting or divergent proof is rejected before
mutation. No higher-token publication or post-append detection is an exclusion
proof. Under both the Coordinator root lock and Lifecycle recovery lock it
must:

1. validate the Journal from the Session-OPEN-bound head before trusting the
   Snapshot;
2. if exactly one valid durable terminal KILL exists, materialize precisely
   its `state_after` and never append a second KILL;
3. if no KILL exists, require exact last-head/Snapshot agreement, append one
   conservative EMERGENCY KILL, then materialize it;
4. reject ambiguous/multiple terminal records, invalid tail or missing
   State-before with zero mutation; and
5. only after full reconciliation append one bound
   `TERMINAL_GAP_RECONCILIATION` record.

The operation never evaluates a market Snapshot, never exits a position,
never deescalates and never starts a Loop. Crash after KILL but before Snapshot
replace re-materializes only the same KILL. Crash after Snapshot replace but
before Gap record binds the same KILL and writes at most one Gap record.

## 12. Projection and monitoring

Projection occurs only from a durable, recovered/reconciled commit and follows
the exact record-then-`IU4ProjectionCursorV1` protocol in Section 7.6. It is
idempotent by Atomic transaction identity, projection fingerprint, output
checksum and Cursor link. Same ID with divergent content, stale/ahead/rollback
or failed CAS is a conflict. Projection failure never rolls back the Atomic
commit, never changes the Journal and never becomes Recovery truth.

Until the projection cursor equals the current committable Atomic head, the
health result includes `PEE_IU4_PROJECTION_LAG` and `entry_allowed=false`.
Nonterminal risk-reducing Exit capability may be reported as remaining
available; the I6 package does not execute it. `HARD`/`EMERGENCY` report no
Exit evaluation and the accepted runtime directive.

Monitoring is read-only and version-aware. It requires the exact terminal
observation, all twelve nested groups and all twelve explicitly named Report
results from Sections 7.7–7.8. The Observation fingerprint is not a group.
Unknown/V1 Atomic State,
`missing_allowed`, malformed Legacy projection, wrong Authority root, open
PREPARE, unclean Session, component mismatch, stale/missing terminal group or
resource failure is never reported PASS. Stable reason precedence is:
schema/canonicality → typed input → Session/Authority/root → terminal fail-stop
or unclean Session → open PREPARE/Lifecycle → Atomic ancestry/components →
Projection lag → profile/Authorization → nonterminal warnings. A FAIL cannot
be downgraded by a later WARN/PASS.

## 13. Stable error and outcome mapping

| Failure / outcome | Exact family |
|---|---|
| missing/consumed Restart authority | `PEE_IU4_RESTART_AUTHORIZATION_REQUIRED` / `PEE_IU4_RESTART_AUTHORIZATION_CONSUMED` |
| typed Authorization or Pre-State mismatch | `PEE_IU4_RECOVERY_AUTHORIZATION_MISMATCH` |
| Ledger sequence/hash/event conflict | `PEE_IU4_LIFECYCLE_LEDGER_CONFLICT` |
| foreign post-consumption extension | `PEE_IU4_LIFECYCLE_EXTENSION_INVALID` |
| incomplete Lifecycle operation | `PEE_IU4_LIFECYCLE_OPERATION_INCOMPLETE` |
| open PREPARE needing completion | `PEE_IU4_AUTHORITY_PREPARE_COMPLETION_REQUIRED` |
| PREPARE/COMMIT/target mismatch | `PEE_IU4_AUTHORITY_COMMIT_MISMATCH` |
| Journal not descended from Authority target | `PEE_IU4_AUTHORITY_ROOT_MISMATCH` |
| invalid DIRECT/RECOVERED provenance | `PEE_IU4_GENESIS_PROVENANCE_INVALID` |
| completion followed by unapproved start | `PEE_IU4_POST_COMPLETION_RESTART_REQUIRED` |
| unclean Runtime Session | `PEE_IU4_RUNTIME_SESSION_UNCLEAN` |
| terminal reconciliation required | `PEE_IU4_TERMINAL_GAP_RECONCILIATION_REQUIRED` |
| ambiguous terminal Journal | `PEE_IU4_TERMINAL_JOURNAL_AMBIGUOUS` |
| invalid Worker death/reap trust anchor or proof | `PEE_IU4_TERMINAL_GUARDIAN_INVALID` |
| live/unreaped Worker or surviving append holder | `PEE_IU4_TERMINAL_GUARDIAN_INVALID` |
| dual open / safety / owner conflict | exact `PEE_IU4_HANDOFF_*` family |
| missing State without Genesis | `PEE_IU4_HANDOFF_GENESIS_REQUIRED` |
| Atomic V1/unknown | `PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED` |
| lagging projection | `PEE_IU4_PROJECTION_LAG` |
| Disk/FD/Memory/OS exhaustion | `PEE_IU4_RESOURCE_EXHAUSTED` |

Constructor/schema/canonicality failures precede typed-boundary failures;
Authorization and Ledger bindings precede materialization; Authority root
precedes projection; terminal ambiguity precedes any compensating write.

## 14. Mandatory focused test matrix

The single new focused test module must cover without reduction:

1. strict missing/unknown/type/subclass/bool/nonfinite/noncanonical/tamper and
   round-trip tests for every I6 artifact;
2. fixed canonical fingerprints and self-consistently refingerprinted negative
   records;
3. the complete Owner × Legacy S2 × Atomic S2 matrix;
4. every S4/Loss/Throttle/Cooldown/Cursor mapping field in both directions;
5. higher Kill, later cooldown, stricter pause and every non-lossless conflict;
6. Legacy V1 behavior unchanged and no silent defaults for I6 views;
7. Atomic Genesis DIRECT success, absent-state proof and exact initial root;
8. Genesis PREPARE/target/COMMIT crash rows and recovered Completion;
9. both Handoff directions with source/target/core/Generation/root checks;
10. PREPARE alone changes no Owner; COMMIT changes it exactly once;
11. missing/corrupt/unknown/dual-open/stale competing State negatives;
12. strict typed Restart Authorization and separate Trust binding;
13. Consumption exactly once, divergent same-ID conflict and fresh-auth rule;
14. `RECOVER_AND_RESTART` journal-only materialization with no new transaction;
15. current-State Authority ancestry from initial target through multiple
    Tick/Control records and foreign-root rejection;
16. `COMPLETE_AUTHORITY_PREPARE` missing/existing target and COMMIT readback;
17. DIRECT versus RECOVERED provenance, NONE sentinels and post-completion
    `RESTART_ONLY` requirement;
18. Terminal Gap with existing KILL, without KILL, ambiguous tail, stale
    Snapshot and exact PROCESS_DEATH Worker-exclusion proof plus separately
    trusted death anchor;
19. Worker proof/anchor exact-type and canonicality, stale/wrong Session,
    Worker, boot, root, attestor, executable, collector, Evidence and validity
    window; live/unreaped/surviving-handle/replayed/divergent negatives; direct
    accepted-`TerminalPersistenceWorkerV8` live-writer characterization; and
    explicit rejection of every higher-token/fencing mode or field;
20. exactly-once terminal KILL and Gap record across every crash boundary;
21. post-commit projection for OPEN/CLOSE/PROGRESS/ENTRY_VETO/KILL;
22. complete Projection Cursor schema/base/link/CAS/path/order/readback,
    sequence+1 and Journal/state ancestry, one-by-one catch-up, skip/gap/fork/
    out-of-order negatives, exact caller-root→projection-root derivation,
    domain-separated realpath bytes/hash, projection-root-relative UTF-8/NFC
    record names, exact noncyclic inventory bytes/fixed fingerprint, root/
    slash/symlink/encoding negatives, identical replay, divergent/stale/ahead/
    rollback conflict, lag and crash reconcile;
23. no Economics recomputation and canonical Decimal compatibility output;
24. complete twelve-group terminal Observation plus exact twelve-result
    Monitoring Report PASS/WARN/FAIL matrix, fixed Observation/Report bytes,
    IDs and fingerprints, every Group-12 field-specific enum/type/result,
    every primitive/enum/cross-field invariant, every numeric boundary-1/
    boundary/boundary+1, Clean-Genesis DIRECT admissibility, Listener/
    Liveness/scalar authority details, missing/stale/lookalike/mismatch
    negatives and exact reason precedence;
25. component, Quote, Cursor, Session, PREPARE, Ledger and root tamper;
26. Disk-full, permission, FD and memory/resource classification at every
    durable publication family;
27. all writes confined to a unique temporary root;
28. exact unchanged V1 Coordinator/State Store/models behavior; and
29. no Loop/Adapter/Execution/Gate/launcher import or active consumer.

## 15. Mandatory fault grid

For each PREPARE-based Genesis/Handoff operation test independently:

- before and after durable PREPARE;
- before and after target replace;
- before and after target file/directory sync;
- before and after read-only reconciliation;
- before and after durable COMMIT; and
- identical committed readback.

For Restart/Recovery test before/after Consumption, before/after Snapshot
materialization, before/after `RECOVERY_MATERIALIZATION`, conflicting Ledger
append and identical readback.

For Terminal Gap test before/after trust-anchor and PROCESS_DEATH exclusion
proof validation, before KILL, after durable KILL, before/after Snapshot
replace, before/after Gap record and identical readback. Every stale, live,
unreaped, surviving-handle, untrusted and divergent proof/anchor row is
isolated; every higher-token/fencing record is rejected as unsupported. Every
row records RC,
Ledger count/tip, Authority Generation/Anchor, Journal count/head/sequence,
Snapshot fingerprint, Owner, projection cursor, business component
fingerprints and whether a Loop/start call occurred. Expected Loop/start calls
are always zero.

For Projection test before/after output create-new, file sync, output-directory
sync/readback, inventory observation, Cursor temporary create-new, Cursor file
sync, atomic replace, Cursor-directory sync and Cursor readback. Include
output-only crash recovery, Cursor-without-output corruption, failed CAS,
stale/ahead/rollback, concurrent previous-link, skip/gap/fork/out-of-order and
multi-transaction one-by-one catch-up rows. Each row records exact base,
previous/current Atomic triples, Cursor links, inventory fingerprint and lag;
Atomic Journal/State/Authority identities remain unchanged.

## 16. Mandatory commands and mandate-time baseline

All Python commands use `PYTHONDONTWRITEBYTECODE=1`, a unique existing
`TMPDIR` and `PYTHONPYCACHEPREFIX` below `/tmp`. Tests must not read or write
operational State, Logs, profiles or Authorization files.

Mandatory later commands include:

```text
.venv/bin/python -m unittest tests.live_l1.test_paper_iu4_recovery_projection
.venv/bin/python -m unittest tests.live_l1.test_paper_atomic_coordinator_v2
.venv/bin/python -m unittest tests.live_l1.test_iu4_lifecycle_ledger
.venv/bin/python -m unittest tests.live_l1.test_paper_iu4_startup_gate
.venv/bin/python -m unittest tests.live_l1.test_paper_iu4_runtime_gate
.venv/bin/python -m unittest tests.live_l1.test_paper_iu4_execution_seam_v2
.venv/bin/python -m unittest tests.live_l1.test_paper_iu4_adapter_v2
.venv/bin/python -m unittest tests.live_l1.test_paper_atomic_coordinator
.venv/bin/python -m unittest tests.live_l1.test_paper_iu4_adapter
.venv/bin/python -m unittest discover -s tests/live_l1 -p 'test_*.py'
.venv/bin/python -m unittest discover -s tests/regression -p 'test_*.py'
.venv/bin/python -m py_compile live_l1/state/paper_atomic_coordinator.py live_l1/state/models.py live_l1/state/state_store.py live_l1/state/paper_iu4_recovery_projection.py tests/live_l1/test_paper_iu4_recovery_projection.py
git diff --check
git diff --cached --check
```

Mandate-time read-only baseline on 2026-08-21:

| Gate | Result | Temporary root |
|---|---|---|
| exact accepted I5 15-module neighbor set | 262/262 PASS, RC 0, 0 failures/errors/skips | `/tmp/iu4-i6-mandate-i5exact.dju3Zq` |
| full `tests/live_l1` | 491/491 PASS, RC 0, 0 failures/errors/skips | `/tmp/iu4-i6-mandate-live.6HVxTU` |
| full `tests/regression` | 170/170 PASS, RC 0, 0 failures/errors/skips | `/tmp/iu4-i6-mandate-regression.53DeNY` |
| `git diff --check` | PASS, RC 0 | canonical worktree |
| `git diff --cached --check` | PASS, RC 0 | canonical index |

The later Evidence must include individual module counts, exact commands,
roots, RCs, failures/errors/skips, exact five-Python-path compile output and
the count/location of compile products.

## 17. Evidence completion gate

The I6 Evidence record itself must contain:

- every Section-2 authority identity, this mandate identity and its independent
  READY rereview identity;
- mandate-time and final SHA/count for the five non-Evidence Section-4 paths;
- for the Evidence path, mandate-time worktree and HEAD absence plus the exact
  self-content fingerprint defined below; its actual file SHA-256 and line
  count are bound externally by the independent implementation rereview;
- all Section-5 SHA/count/mode/entry identities;
- exact commands, roots, RCs, counts and skip values;
- complete artifact canonicality and fingerprint matrices;
- complete Handoff, Genesis, Restart/Recovery, Terminal-Gap, Authority-root,
  Projection and monitoring matrices;
- every fault-row immediate and final identity listed in Section 15;
- exact stable reason-code and precedence results;
- proof that Projection is non-authoritative and Economics were not
  recomputed;
- proof that no real runtime root, process, network or external Authorization
  was used;
- exact six-path mutation output and all three CREATE paths, each with
  worktree-absence and HEAD-absence start proofs;
- searches proving no active caller, Loop/Adapter/Gate/launcher integration,
  I7/I8 behavior or activation; and
- `I6_RESULT:PASS` only if every row passes with zero skips.

Incomplete, contradictory or overstated Evidence is an I6 blocker even when
tests are green.

The Evidence file is UTF-8 with LF and a final newline. Its final line is
exactly `EVIDENCE_PAYLOAD_SHA256:<lowercase-64-hex>`. The payload fingerprint is
SHA-256 over every byte before that final line, including the newline ending
the preceding line, and excludes the complete final line and its newline. The
Evidence may record its own total line count, but must not claim its actual
whole-file SHA-256 internally. The independent implementation rereview computes
and binds the actual whole-file SHA-256 and line count. This rule is
non-self-referential and requires no seventh path.

## 18. Stop conditions

The later implementation stops `I6_RESULT:BLOCKED` and writes no PASS Evidence
if:

- any controlling, start, absence or Preservation identity differs;
- a seventh path is required;
- Ledger, Startup Gate, Runtime Gate, Adapter, Loop, Execution or launcher must
  change;
- V1 Coordinator, models or State Store behavior changes;
- any State/S4/Loss/Throttle/Cursor field is defaulted, dropped or converted
  through binary float;
- Owner is derived from anything except the valid Authority-COMMIT chain;
- PREPARE changes Owner or target publication precedes durable PREPARE;
- any Target/COMMIT introduces a hash cycle or State binds Ledger tip/COMMIT;
- Recovery creates/redecides a transaction or business value;
- consumed Authorization can be reused or a post-consumption crash can retry
  without fresh authority;
- DIRECT and RECOVERED provenance are ambiguous or incomplete;
- a foreign but internally valid Journal root is accepted;
- terminal ambiguity causes a compensating KILL or other mutation;
- Worker exclusion is accepted from a boolean/mapping/subclass/lookalike,
  self-authenticating or untrusted source, is stale, lacks exact PIDFD death,
  reap, handle closure or zero surviving holders, or accepts a higher-token/
  fencing mode;
- Projection becomes Recovery input, recomputes Economics or rolls back State;
- Projection output/Cursor sequence+1 ancestry, base, inventory domain,
  caller-root/projection-root derivation, realpath hash byte domain, relative
  path base/encoding, ordering, CAS, sync/readback, crash reconstruction,
  one-by-one catch-up or stale/ahead/rollback/skip/gap/fork behavior is
  ambiguous;
- monitoring repairs State, starts a Loop or reports missing/unknown as PASS;
- monitoring omits any Section-7.7 terminal field/type/enum/range/invariant,
  accepted budget boundary, Listener/Liveness/scalar-authority or DIRECT
  first-start eligibility proof, or accepts missing, stale, lookalike,
  wrong-Session, wrong-Authority or wrong-root observation as PASS;
- monitoring has any group/result cardinality other than twelve, omits any
  exact Section-7.8 Report field/hash domain/derivation, uses a collective
  status enum instead of the field-specific Group-12 matrix, or lets a caller
  choose group, capability or overall results;
- monitoring accepts an absence sentinel outside the three exact paired rows,
  accepts a mixed Session/manifest/Cursor ID-fingerprint pair, or permits a
  Cursor sequence/head or Runtime Session status inconsistent with its pair;
- any write escapes a test-owned temporary root;
- real State, Logs, process, network, Exchange, profile or external
  Authorization access is required;
- any test fails, errors, skips or reduces a mandated matrix;
- an operational consumer, `RUNTIME_SESSION_OPEN`, ENFORCED start, I7/I8 or
  activation behavior appears;
- Git staging/commit/fetch/push, cleanup or foreign-artifact mutation occurs;
  or
- the excluded specification-bundle script is read, executed or changed.

## 19. Explicit non-scope

No change to Lifecycle Ledger, Startup/Runtime/Shadow gates, Adapter, Loop,
Execution, safe launch, terminal/native closure, profiles, Authorizations,
credentials, Economics, Throttle, accepted artifacts/Loss code or I3–I5
focused tests. No active Runtime Session, operational manual-recovery CLI,
daemon, scheduler, Workstation run, launcher exposure, Exchange, Live or
Production. No automatic Handoff, Genesis, Recovery, deescalation, cleanup,
archive rewrite or migration of real data. No GS, Research, RCC002, `engine/`
or `run_engine/`. No I7 or I8 work.

## 20. Mandate result and exact next step

```text
MANDATE_RESULT:AUTHORIZED_PENDING_INDEPENDENT_REREVIEW
AUTHORIZED_LATER_PATHS:6
AUTHORIZED_MODIFY_PATHS:3
AUTHORIZED_CREATE_PATHS:3
I6_IMPLEMENTATION_ENTERED:NO
I6_EVIDENCE_CREATED:NO
I6_INDEPENDENT_ACCEPTANCE:NOT_READY
OPERATIONAL_ENFORCED_START_AUTHORIZED:NO
ACTIVE_V2_CONSUMER_AUTHORIZED:NO
I7_AUTHORIZED:NO
I8_AUTHORIZED:NO
ENFORCED_ACTIVATION_AUTHORIZED:NO
NEXT_REQUIRED_STEP:IU4-I6-RECOVERY-MONITORING-PROJECTION-FILE-EXACT-MANDATE-INDEPENDENT-READONLY-REREVIEW-5
```

Only the named independent read-only file-exact mandate rereview may follow.
Implementation begins only after `READY` for this exact mandate identity. No
outcome of this mandate or its rereview authorizes operational activation.
