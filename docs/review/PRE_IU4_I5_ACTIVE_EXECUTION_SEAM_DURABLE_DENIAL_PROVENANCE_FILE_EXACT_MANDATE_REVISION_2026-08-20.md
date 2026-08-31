# Pre-IU4 I5 Active Execution Seam Durable Denial Provenance — File-Exact Mandate Revision — 2026-08-20

## 1. Mandate decision

```text
MANDATE_ID:IU4-I5-ACTIVE-EXECUTION-SEAM-DURABLE-DENIAL-PROVENANCE-FILE-EXACT-MANDATE-REVISION
MANDATE_REVISION:4
PRIOR_MANDATE_ID:IU4-I5-ACTIVE-EXECUTION-SEAM-DURABLE-DENIAL-PROVENANCE-FILE-EXACT-MANDATE-REVISION
PRIOR_MANDATE_REVISION:3
PRIOR_MANDATE_SHA256:39f1d09b5a86e0882dce017b4c88594fe0e24fbd2a1f1c31d38ba26a9c088b5f
PRIOR_MANDATE_LINES:609
PRIOR_REVISION_REREVIEW_SHA256:28818149ea81b7bc715d86a97ff0e05beccb2c27c66dc39fb28507b37e7d6f2b
PRIOR_REVISION_REREVIEW_LINES:278
PRIOR_REVISION_REREVIEW_RESULT:NOT_READY_1_BLOCKER
REREVIEW_4_RESULT:NOT_READY
REREVIEW_4_FINDINGS:1/0/0/0
SCOPE_RESOLUTION_RESULT:BLOCKED_REVISED_FILE_EXACT_MANDATE_REQUIRED
MANDATE_RESULT:AUTHORIZED_PENDING_INDEPENDENT_REREVIEW
CORRECTIVE_PACKAGE:I5_DURABLE_DENIAL_PROVENANCE_ONLY
CORRECTIVE_IMPLEMENTATION_AUTHORIZED:YES_WITHIN_EXACT_SCOPE_AFTER_READY_REREVIEW
CURRENT_CANDIDATE_ACCEPTED:NO
I5_INDEPENDENT_ACCEPTANCE:NOT_READY
OPERATIONAL_ENFORCED_START_AUTHORIZED:NO
ACTIVE_V2_CONSUMER_AUTHORIZED:NO
I6_THROUGH_I8_AUTHORIZED:NO
ENFORCED_ACTIVATION_AUTHORIZED:NO
EXCHANGE_AUTHORIZED:NO
LIVE_AUTHORIZED:NO
```

This record revises only the later implementation authority needed to close
finding `I5-IR4-B1`. It does not implement the correction. It intentionally
releases the accepted Atomic V2 Coordinator and its focused test as correction
inputs, replaces the prior corrective path set with the exact five paths in
Section 4, and freezes the already-corrected Loop and Execution bytes.

Independent read-only file-exact rereview of this exact mandate identity is
required next. No source, test or Evidence mutation may begin before that
rereview returns `READY`.

## 2. Controlling identity and authority chain

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
| final I3 Evidence | `20846284ffad9e8b755dd6a3b74f963d8d2c6ee1519fafdd0bc1275f2e33c390` | 463 | accepted historical start authority |
| final independent I3 rereview 6 | `03790420534e38c7e36d1824a472dfd80763340dacec8847ddf5072d55db0c9f` | 191 | READY |
| final I4 Evidence | `068c2ba2661031843a13dd3f2c4684f9340f432b90b192b6b7492dae8968270d` | 403 | accepted |
| final independent I4 rereview 3 | `c6d8bbcb35572a364b74a47eb9ad817240a8b0cce70e514942bb674d3861c38b` | 191 | READY |
| base I5 mandate revision 2 | `124de947c7eebaaeffa37fb802c0bf3194b1595107628cd655bab8b833522060` | 562 | authorized original I5 scope |
| base I5 mandate independent rereview 2 | `3d02b2f5791218643e7d76805701e88fbed5c121a884944a9242b31357740922` | 212 | READY |
| I5 implementation rereview 1 | `7ddd108a659a37e264b5cfb78172cd00d5d426105455b864b358756aaad57980` | 262 | NOT_READY |
| I5 implementation Resolution 1 | `0661aaa5193f790976ae96256cca4dc74b3c99d4533369587203dc18d76e22ff` | 233 | historical correction |
| I5 implementation rereview 2 | `eb5886b59c09cfd3f7b797453642c40f0943666b3d9f9df7d8b45e7077bf940a` | 213 | NOT_READY |
| I5 implementation Resolution 2 | `4a11786ef353b84ad9384da3fd35fcb1857fc323d9f1fb963e7155dd4da0766e` | 224 | historical correction |
| I5 implementation rereview 3 | `5b825372b313ead079ef0680e8410a552a2e72d05a0f4abb7e1fa88739212496` | 277 | NOT_READY |
| I5 implementation Resolution 3 | `3827b7e00db22df28a600dff6a776e0ac2c49a7a7a058b307d9c973aef6fe309` | 225 | candidate correction |
| I5 implementation rereview 4 | `15964978eeef90a9e08216beddcd0c33b9a0e37c963f911f7d64705ab52be4c6` | 330 | NOT_READY, 1/0/0/0 |
| durable-provenance scope Resolution | `c08b3b98693a07bc19c2416bc45449cd5b3c8acfbd7457f07c54efa6d6d8dc2f` | 305 | revised mandate required |
| durable-provenance mandate revision 3 independent rereview | `28818149ea81b7bc715d86a97ff0e05beccb2c27c66dc39fb28507b37e7d6f2b` | 278 | NOT_READY, 1/0/0/0; finding closed by this revision |
| current I5 Evidence | `ce4e01fd1c27f15b13bda72d121eb2c08c541c956a7fc3e20d5da31464c4aa86` | 474 | PASS claim not accepted |
| I2 Preservation package | `3af14ff2e270d7d3ca09c1279da7d64e6d720630d06a0c5f45b6786237782037` | 1,318 entries | immutable |
| I2 Freeze manifest | `ad154c0eda13470920878873ed170368cc8f4c43591400a07592a77b179d9e16` | 60 | immutable |

Revision 21 Sections 12, 13.4, 16, 18, 20 and 21 control. The accepted I3
transaction owns the single durable Tick journal truth; the accepted I4 Request
remains content-addressed and unchanged; I5 remains a dormant isolated seam
without operational ENFORCED authority.

## 3. Confirmed defect, objective and hard ceiling

### 3.1 Confirmed defect

Rereview 4 proved that genuine Account-, Throttle- and Economics-denied OPEN
requests can begin with `state_before.risk.entry_allowed=true`, correctly commit
one rejected `PROGRESS`, and then fail identical replay as
`PEE_IU4_ADAPTER_REQUEST_CONFLICT`. The transaction stores no denial origin or
trusted Gate capability. Re-evaluating the business decision during replay is
forbidden; treating every OPEN+PROGRESS as equivalent would accept a divergent
Gate capability.

### 3.2 Objective

The correction adds one strict, optional, transaction-owned
`AtomicEntryDenialProvenanceV1` artifact and uses it only for accepted non-Loss
OPEN denials that commit `PROGRESS`. It binds the once-decided denial and trusted
entry capability into canonical transaction serialization, transaction
fingerprint, journal head, recovery and replay.

The correction must make these cases restart-idempotent without another
Control, Gate decision, State-capability decision, economics authorization,
Account guard, Throttle guard or other business decision.

### 3.3 Hard ceiling

The package does not add a State field, S4 field, Request field, sidecar, second
journal, new source module, new test module or new Evidence path. PROGRESS still
changes only the Progress Cursor and bound aggregate identity. Provenance is
transaction effect metadata and never business State.

The package does not change Loop/Execution behavior, I4 Request serialization,
Runtime/Startup/Shadow gates, launcher closure, lifecycle authority, profiles,
operational modes or activation. Any need for a sixth path blocks the package.

## 4. Exact authorized later correction file set

Exactly five existing paths may change after independent mandate readiness.

| Operation | Path | Mandate-time SHA-256 | Lines | Authorized correction only |
|---|---|---|---:|---|
| MODIFY | `live_l1/state/paper_atomic_coordinator.py` | `d0721ae5def3551ba7281ea0e367f5347890fd4cd7187d8f2aebb98d2651e84f` | 5,489 | define strict provenance artifact; add conditional transaction metadata; bind canonical record/fingerprint/journal/recovery/effect validation; typed optional `commit_progress` input and same-ID comparison |
| MODIFY | `live_l1/core/paper_iu4_adapter.py` | `e8804916b8a2142459b661933d5582455ae52640cce9d9c4d38ad6102d641dac` | 1,710 | select exact denial origin once, pass provenance on first rejected PROGRESS, and replay only from the durable transaction binding |
| MODIFY | `tests/live_l1/test_paper_atomic_coordinator_v2.py` | `16d0fea6e5588cc14329ba61cfeeccb1f72478d14c358f8ed4e38c1ac3a41bb9` | 2,482 | strict artifact/transaction schema, compatibility, effect ceiling, journal, tamper, conflict, fault and recovery matrix |
| MODIFY | `tests/live_l1/test_paper_iu4_execution_seam_v2.py` | `36356eec13e2b854556582a086987f719930ee9ef69672348413a5c06f94c807` | 2,051 | actual Account/Throttle/Economics/State/Gate denial replay, divergence and zero-redecision matrix |
| REPLACE | `docs/review/PRE_IU4_I5_ACTIVE_EXECUTION_SEAM_IMPLEMENTATION_EVIDENCE_2026-08-20.md` | `ce4e01fd1c27f15b13bda72d121eb2c08c541c956a7fc3e20d5da31464c4aa86` | 474 | corrected final identities, commands, complete matrices, preservation, scope and result |

No other source, test, fixture, State sample, profile, Authorization, manifest,
configuration, schema sidecar, launcher, documentation or Evidence path is
authorized. The mandate itself is the only governance artifact created in this
turn and is not part of the later five-path correction.

The base mandate's five-path implementation authority is not cumulative with
this correction scope. For the next implementation workstream, Section 4 above
is the complete and exclusive mutation set. In particular, `loop.py` and
`execution.py` are no longer writable inputs.

## 5. Explicit read-only Preservation boundary

### 5.1 Corrected I5 production bytes now frozen

| Path | Required SHA-256 | Lines |
|---|---|---:|
| `live_l1/core/loop.py` | `e4db22642b628fe4b84cf0d2daa9ecd846208138eaa3868a02a56ddf9f75ee6c` | 1,947 |
| `live_l1/core/execution.py` | `85a9acb238dafd3adf5fd8bf57153772d3c7b41559943bdcce5336e3b60dcb5e` | 1,386 |

### 5.2 Frozen I2 and accepted I3/I4 remainder

| Path | Required SHA-256 | Required mode / lines |
|---|---|---:|
| `archive/IU4_I2_FREEZE_20260820/IU4_I2_PRESERVATION_20260820.tar.gz` | `3af14ff2e270d7d3ca09c1279da7d64e6d720630d06a0c5f45b6786237782037` | `0444`, 1,318 entries |
| `archive/IU4_I2_FREEZE_20260820/FREEZE_MANIFEST.txt` | `ad154c0eda13470920878873ed170368cc8f4c43591400a07592a77b179d9e16` | `0444`, 60 lines |
| `live_l1/state/paper_artifacts.py` | `3cd9a459e2856672bb7b318c9cdbf8f8bb52e633ee9529d74761d64928213946` | 1,575 |
| `live_l1/state/loss_cluster.py` | `4ce7d59f64a67de94ffc6f1d03ff4e6c8a7a590802abb003b311cd0d56cc3e55` | 521 |
| `tests/live_l1/test_paper_iu4_adapter_v2.py` | `f71d46700a1966534429281091da32e263ac479ddf1393c5021d015eac1cd1b3` | 1,274 |
| final I3 Evidence | `20846284ffad9e8b755dd6a3b74f963d8d2c6ee1519fafdd0bc1275f2e33c390` | 463 |
| final I4 Evidence | `068c2ba2661031843a13dd3f2c4684f9340f432b90b192b6b7492dae8968270d` | 403 |

The Atomic Coordinator and Atomic V2 focused test are the only intentionally
released I3 bytes. Historical I3 Evidence and rereview records remain immutable
and continue to identify the accepted start point; the new I5 Evidence must
record the final corrected identities and the additive compatibility proof.

### 5.3 Runtime, gate, Legacy and adjacent inputs

| Path | Required SHA-256 | Lines |
|---|---|---:|
| `live_l1/core/paper_execution_control.py` | `7d3cb901c1c67c8df85e99bc579fda85d8732b634ff4747e08620b92ac1e44f7` | 257 |
| `live_l1/core/paper_iu4_runtime_gate.py` | `447573e484bc13023a118ae61bf7615657293be629c30729748e64f0af7af7c5` | 201 |
| `live_l1/core/paper_iu4_startup_gate.py` | `c4a1854f3b200525568a40205b39e9ce2e14c342bb860569ba7fcfe5e9c063cd` | 919 |
| `live_l1/core/paper_iu4_shadow_runtime_gate.py` | `98d986f3ac2e463b371998604d92b29aa113a507dd0f84bcbd3ff36a52efaf59` | 438 |
| `live_l1/core/paper_iu4_shadow_observation_gate.py` | `ed4e75fad664c68b91950e9c09e873823ebe3eb0b0062f85806daa09ce661350` | 886 |
| `live_l1/core/paper_iu4_shadow_harness.py` | `ddfb60f19a3b765a476c8de0464d583590313cdd0583391044cb338fec969f77` | 1,007 |
| `live_l1/state/iu4_lifecycle_ledger.py` | `d72134195f66b1d39c09a2ca6b9919d8a9acf17c4490ab52d9abc2aebcd71337` | 438 |
| `live_l1/state/state_store.py` | `50a85cf6bd382850d39e69cd785a5dc2ded0a66a1d82856b4baa11877bdba177` | 220 |
| `live_l1/state/models.py` | `3254d2f1a6509ec5f8f623dd8f286f60cfcc108f66f2d8eb107338d795115c7e` | 27 |
| `live_l1/core/paper_economics.py` | `a302013134d1265ac85ad10b57a67ead9e2343043f7eb499fd965a44312525ae` | 730 |
| `live_l1/core/paper_entry_throttle.py` | `ad5447d88a2c35c9a71a5495c61c8f08fa844daf60e79d4a872234e88037df75` | 727 |
| `live_l1/state/paper_entry_throttle.py` | `ce76d8430792d6de1cfdf9a55c09cb6ab501489c7610d2f78345f8d78646295b` | 586 |
| `live_l1/tools/safe_launch.py` | `cb90bd49b36de56e8ad95e9b24febb23baa0513b1ec51e7402f63a5efd6ec652` | 201 |
| `tests/live_l1/test_paper_iu4_adapter.py` | `b4947e4c03fa3b187e01c4005062337d1837b70d652243030581172dd4d2c339` | 441 |
| `tests/live_l1/test_paper_execution_control.py` | `0ae44f2d32f5f3b6affe37a258be0e6aee06790f857e4fc01628c6795bda99e5` | 843 |
| `tests/live_l1/test_paper_atomic_coordinator.py` | `a46f622f9a00e5db727ade04ece89b4deaf51347dc2d1f4d304532572b382753` | 891 |

The freeze directory remains mode `0555`. Every archived copy and every prior
mandate, Resolution, Evidence and rereview other than the one Evidence path
explicitly authorized for replacement remains byte-identical.

## 6. Required implementation order

The later correction workstream must:

1. reverify every controlling, start and Preservation identity;
2. rerun all mandate-time baselines before mutation;
3. extend the Atomic V2 focused test first with strict artifact, compatibility,
   transaction, fault and recovery negatives;
4. extend the I5 focused test with genuine downstream denial reproducers and
   zero-redecision sentinels;
5. add the strict provenance artifact and conditional transaction binding;
6. add exact first-decision origin selection and durable Adapter replay;
7. rerun all focused, adjacent, broad, compile and scope gates;
8. verify every non-provenance transaction record/fingerprint/head fixture is
   byte-identical to the mandate-time result;
9. replace Evidence only after every row passes; and
10. stop without PASS Evidence if any mandate condition fails.

No skip, xfail, reduced matrix, hand-edited journal or manual-only assertion is
accepted.

## 7. Exact `AtomicEntryDenialProvenanceV1` contract

The new class is a frozen dataclass defined in
`live_l1/state/paper_atomic_coordinator.py`. It has exactly these canonical
payload fields:

| Field | Exact contract |
|---|---|
| `schema_version` | exact primitive integer `1`; bool and subclasses rejected |
| `artifact_type` | exact canonical text `atomic_entry_denial_provenance_v1` |
| `transaction_event_id` | nonempty canonical Request/Event ID |
| `snapshot_id` | nonempty exact Snapshot ID |
| `timestamp_utc` | canonical UTC seconds with trailing `Z` |
| `tick_id` | exact primitive integer, minimum 0 |
| `intent_id` | nonempty exact source Intent ID |
| `intent_action` | exactly `OPEN_LONG` or `OPEN_SHORT` |
| `state_before_fingerprint` | exact lowercase 64-character SHA-256 |
| `denial_origin` | one closed value from Section 9 |
| `denial_reason_code` | exactly `PEE_IU4_ENTRY_BLOCKED` |
| `entry_capability_allowed` | exact primitive bool; no integer/subclass coercion |

`provenance_fingerprint` is the lowercase SHA-256 of canonical JSON over exactly
the payload above. The persisted record contains exactly the twelve payload
fields plus `provenance_fingerprint`. Unknown, missing, duplicate, noncanonical,
case-normalized-on-read, whitespace-padded, bool-as-int, Float, nonhex,
self-inconsistent or tampered input fails closed. `from_record()` must require
exact equality to `to_record()` after strict construction.

No default supplies a business value. The containing transaction may default
its optional Python reference to `None` solely for source compatibility; a
present provenance record has no optional field and no default.

## 8. Conditional transaction serialization and compatibility

The transaction member is named exactly
`effect_entry_denial_provenance: AtomicEntryDenialProvenanceV1 | None`.

Compatibility is mandatory:

1. When the member is `None`, `AtomicPaperTransactionV2.canonical_payload()`,
   `to_record()`, `transaction_fingerprint` and `journal_head_for()` omit the
   provenance key/material completely and remain byte-for-byte identical to the
   mandate-time implementation for the same transaction.
2. Explicit JSON `null` is not a second spelling. A record either omits the key
   or contains one strict provenance object.
3. `from_record()` accepts exactly two field sets: the mandate-time base set
   without the key, or the base set plus one mapping-valued
   `effect_entry_denial_provenance`. Any other shape fails closed.
4. When present, the complete provenance record participates in canonical
   transaction serialization and transaction fingerprint; its fingerprint
   participates in journal-head material.
5. All transaction reconstruction, `_build_transaction`, `_validate_effect`,
   `commit_progress`, `_commit`, journal parsing, recovery and reconciliation
   preserve and validate the exact value.
6. Existing mandate-time OPEN, CLOSE, ENTRY_VETO, KILL and ordinary PROGRESS
   records, fingerprints and heads remain exact. No migration or silent rewrite
   of a pre-correction record is allowed.

There is no operational V2 journal consumer or authorized production V2 root.
If later implementation discovers any non-temporary persisted V2 journal that
would require migration, the correction stops and requires separate authority.

## 9. Closed denial-origin and precedence contract

| `denial_origin` | Selection point | Required State/capability facts |
|---|---|---|
| `STATE_CAPABILITY` | accepted Request validation returns the non-Loss `PEE_IU4_ENTRY_BLOCKED` State/S4/SOFT result before the Gate capability branch | `state_before.risk.entry_allowed is False`; `state_before.loss_cluster.pause_entries_remaining == 0`; `LOSS_CLUSTER_PAUSE` is absent from `state_before.risk.reason_codes`; trusted capability is stored exactly and may be either bool because State precedence wins |
| `RUNTIME_GATE_CAPABILITY` | Request/Context/State validation passed, then trusted `entry_capability_allowed is False` | State entry capability is true; stored capability is exactly false |
| `ECONOMICS_AUTHORIZATION` | Request/Context/State and Gate capability passed, then the one allowed `authorize_entry()` decision denied or supplied no quote | State entry capability is true; stored capability is exactly true |
| `ATOMIC_ENTRY_GUARD` | Request/Context/State, Gate and Economics passed, then `commit_open()` returned exact Atomic `ENTRY_BLOCKED` from authoritative Account/Throttle/Control guards | State entry capability is true; stored capability is exactly true |

The Adapter selects exactly one origin at the first authoritative blocker. A
later blocker may not overwrite it. Account and Throttle deliberately share the
Atomic origin because the current Coordinator exposes one authoritative
`ENTRY_BLOCKED` result; both remain separate mandatory behavioral cases.

Every provenance Origin additionally requires
`state_before.loss_cluster.pause_entries_remaining == 0` and absence of
`LOSS_CLUSTER_PAUSE` from `state_before.risk.reason_codes`. A present provenance
artifact with either positive pause or active Loss reason is always
`PEE_ATOMIC_TRANSACTION_INVALID` before journal creation, regardless of the
claimed Origin or other State facts. Active Loss pause belongs exclusively to
`ENTRY_VETO`.

Any other claimed origin or any origin/fact mismatch is
`PEE_ATOMIC_TRANSACTION_INVALID` before durable journal creation. A new denial
family may not silently map to an existing origin; it blocks and requires a new
mandate.

## 10. Effect and cross-binding invariants

### 10.1 Provenance-bearing transaction

A present provenance artifact requires all of:

- ordering space `TICK`;
- primary effect `PROGRESS`;
- exact FLAT State before and after;
- one complete Progress Cursor;
- no accepted Entry Event, Trade, Position effect, Entry Quote effect, Throttle
  policy, Entry-Veto Candidate, Loss transition, target Kill or Control
  authorization;
- empty `risk_escalation`;
- `state_before.loss_cluster.pause_entries_remaining == 0` and no
  `LOSS_CLUSTER_PAUSE` Risk reason;
- unchanged Position, Account, Throttle, Loss and Entry Quote;
- transaction Event ID equals provenance Event ID;
- transaction timestamp and causal Tick equal provenance and Cursor;
- Cursor Snapshot/Intent equal provenance Snapshot/Intent; and
- `state_before.state_fingerprint` equals the stored State fingerprint.

### 10.2 Null provenance

OPEN, CLOSE, ENTRY_VETO and KILL require `None`. Accepted HOLD,
already-positioned NOOP and every ordinary non-denial PROGRESS require `None`.
The Adapter may not return rejected OPEN/PROGRESS without a present artifact.

Atomic direct callers may still commit ordinary `PROGRESS` with `None`; they may
not fabricate a provenance object whose invariants do not hold. Same Event ID
with null versus non-null, or any different provenance field, is an exact
conflict and writes no second journal record or Snapshot.

### 10.3 State mutation ceiling

Denial provenance is not added to `AtomicPaperStateV2`, S4, Cursor, Loss,
Position, Account, Throttle or Entry Quote. The State-after fingerprint changes
only through the already-required sequence/event/journal/Cursor heads. Business
payloads remain equal before and after.

## 11. First-commit Adapter contract

The exact `entry_capability_allowed` argument remains a trusted execution input,
becomes a required keyword with no default, must be `type(value) is bool`, and
is not added to `IU4AdapterRequestV2`. Omission or a bool lookalike/subclass
fails before State load or mutation.
Accepted I4 Request fields, canonical payload, Request ID and validator remain
byte-compatible.

For rejected OPEN/PROGRESS, the Adapter constructs provenance directly from the
already-bound Request, current State-before and once-selected origin and passes
it to `commit_progress()`. It does not derive identity from mutable post-denial
State. The transaction Event ID remains exactly the Request ID.

The four first-commit paths are:

| First blocker | Result | Transaction | Provenance |
|---|---|---|---|
| State/S4/SOFT capability | `REJECTED / PEE_IU4_ENTRY_BLOCKED` | one `PROGRESS` | `STATE_CAPABILITY` |
| Runtime Gate entry capability false | same | one `PROGRESS` | `RUNTIME_GATE_CAPABILITY` |
| Economics authorization denial | same | one `PROGRESS` | `ECONOMICS_AUTHORIZATION` |
| Coordinator Account/Throttle authoritative denial | same | one `PROGRESS` | `ATOMIC_ENTRY_GUARD` |

Loss-pause denial remains `ENTRY_VETO`, not this provenance contract. Binding,
schema, profile, authorization, terminal and resource failures before accepted
business denial remain `REJECTED_PRE_ACCEPT` with no Tick transaction.

## 12. Durable replay and conflict contract

Replay executes under the existing Atomic root-exclusive lock. It loads the
existing transaction by Request/Event ID before any business authorization.

For a provenance-bearing transaction it must:

1. strictly parse and validate the transaction, journal head and provenance;
2. verify Request ID/content, trusted Context, Authorization, Event, State-before
   fingerprint, Snapshot/time/Tick/Intent/action and original escalation;
3. compare incoming exact `entry_capability_allowed` to the stored value;
4. require `PROGRESS`, rejected OPEN disposition and exact public reason;
5. invoke only existing-transaction `_commit()` materialization/readback; and
6. return `REJECTED/PROGRESS/PEE_IU4_ENTRY_BLOCKED`,
   `newly_committed=false`, `already_committed=true`.

It must not call `_effect()` to rederive OPEN/PROGRESS and must not call Control,
Gate decision logic, Request construction, `authorize_entry()`, Account,
Throttle, Loss, State capability or another business guard.

Divergent Request payload, capability, origin, reason, provenance identity,
State-before, Cursor, effect, escalation or transaction bytes fails closed
without journal/Snapshot/State mutation. Gate false followed by true conflicts;
Gate true followed by false conflicts. Same capability plus the exact existing
transaction replays once regardless of current external guard conditions.

## 13. Failure-code and precedence matrix

| Failure | Exact required family |
|---|---|
| unsupported provenance schema/artifact type | `PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED` |
| malformed/noncanonical/cross-binding/origin mismatch | `PEE_ATOMIC_TRANSACTION_INVALID` |
| provenance or transaction fingerprint/head tamper | `PEE_ATOMIC_JOURNAL_CONFLICT` |
| same PROGRESS Event ID with divergent provenance payload | `PEE_IU4_PROGRESS_CONFLICT` |
| Adapter replay Request/capability/effect/escalation divergence | `PEE_IU4_ADAPTER_REQUEST_CONFLICT` |
| accepted non-Loss denial first result or identical replay | `PEE_IU4_ENTRY_BLOCKED` |
| resource/disk/permission/FD/memory publication or lock fault | `PEE_IU4_RESOURCE_EXHAUSTED`; no Legacy fallback |

Precedence remains exact: type/schema -> canonicality/fingerprint -> Request and
trusted binding -> State/terminal -> provenance/effect cross-binding -> same-ID
payload/capability -> materialization. The focused tests must prove every row and
representative multi-failure first-code ordering.

## 14. Fault, crash and recovery matrix

For provenance-bearing PROGRESS, inject each point using only unique temporary
roots:

1. before accepted validation completes;
2. after validation/before Coordinator call;
3. before durable journal create-new;
4. after durable journal/before Snapshot;
5. before Snapshot publication;
6. after Snapshot/before readback; and
7. during identical recovery/readback.

For each point record result code, journal count, Snapshot sequence/head, Cursor,
provenance record/fingerprint, transaction fingerprint/head, component business
fingerprints, replay result and decision-sentinel counts. Before journal there
is no transaction/Cursor; after journal there is exactly one recoverable
transaction whose provenance survives exact readback; no case reruns a business
decision.

Disk-full, permission, FD exhaustion and memory failure are classified through
controlled mocks or temporary roots. No real repository State, process,
network, Exchange or production resource is touched.

## 15. Mandatory focused test matrix

The two authorized existing focused modules must cover without reduction:

1. all provenance fields: valid construction, strict type, missing/unknown,
   case, whitespace, canonical UTC, integer/bool boundary, SHA, enum, reason,
   record and fingerprint tampering;
2. explicit-null rejection and exact base-record versus provenance-record field
   sets;
3. byte-identical mandate-time record, transaction fingerprint and journal head
   for OPEN, CLOSE, ENTRY_VETO, KILL and ordinary PROGRESS with `None`;
4. fingerprint/head sensitivity to every provenance field;
5. every allowed and disallowed effect/provenance combination;
6. all transaction/Cursor/State/action/origin/capability cross-bindings;
7. same-ID exact idempotence and null/non-null or field-divergent conflicts;
8. canonical journal create-new, sequence, root lock, recovery and tamper
   rejection with provenance;
9. the complete seven-point provenance fault grid and resource classification;
10. genuine Account denial while `state_before.risk.entry_allowed=true`, first
    commit plus identical replay, one transaction/Cursor, business unchanged;
11. the same genuine matrix for Throttle denial;
12. the same genuine matrix for Economics denial;
13. State/SOFT capability denial with capability true and false variants;
14. Runtime Gate false at Atomic NONE: same-false replay succeeds, divergent
    true conflicts;
15. Gate true plus each downstream denial: same-true replay succeeds,
    divergent false conflicts;
16. required explicit Gate-capability argument, missing argument and exact-bool
    lookalike/subclass rejection before State access;
17. failing sentinels proving zero second Control, Gate decision, `_effect`,
    Request construction, economics, Account, Throttle, Loss or State decision;
18. direct Atomic active Loss pause plus `STATE_CAPABILITY` provenance rejects
    as `PEE_ATOMIC_TRANSACTION_INVALID` before journal creation;
19. direct Atomic active Loss pause plus `ATOMIC_ENTRY_GUARD` provenance rejects
    identically with no journal or Snapshot;
20. genuine Adapter Loss pause maps only to ENTRY_VETO and decrements exactly
    once;
21. V1 Atomic/Adapter behavior and accepted I4 Request V2 canonical bytes;
22. current OFF/SHADOW/Loop/Execution behavior using their preserved bytes; and
23. no operational ENFORCED consumer, launcher exposure, I6 behavior, sidecar,
    second journal, State schema change, Exchange, Live or activation.

Tests may build transactions through public/authorized constructors and fault
hooks; acceptance may not rely on a hand-edited record as its only positive
proof. Adversarial record edits are permitted only for negative tamper tests.

## 16. Mandatory commands and mandate-time baselines

Every Python command uses `PYTHONDONTWRITEBYTECODE=1`, a unique temporary
`TMPDIR` and `PYTHONPYCACHEPREFIX` outside the repository.

```text
.venv/bin/python -m unittest tests.live_l1.test_paper_atomic_coordinator_v2
.venv/bin/python -m unittest tests.live_l1.test_paper_iu4_execution_seam_v2
.venv/bin/python -m unittest tests.live_l1.test_paper_iu4_adapter_v2
.venv/bin/python -m unittest tests.live_l1.test_paper_iu4_adapter
.venv/bin/python -m unittest tests.live_l1.test_paper_execution_control
.venv/bin/python -m unittest tests.live_l1.test_paper_atomic_coordinator
.venv/bin/python -m unittest tests.live_l1.test_paper_iu4_startup_gate
.venv/bin/python -m unittest tests.live_l1.test_paper_iu4_runtime_gate
.venv/bin/python -m unittest tests.live_l1.test_paper_iu4_shadow_harness
.venv/bin/python -m unittest tests.live_l1.test_paper_iu4_shadow_observation_gate
.venv/bin/python -m unittest tests.live_l1.test_paper_iu4_replay_evidence
.venv/bin/python -m unittest tests.live_l1.test_paper_iu4_replay_pipeline
.venv/bin/python -m unittest tests.live_l1.test_paper_economics_shadow_runtime
.venv/bin/python -m unittest tests.live_l1.test_safe_launch_iu4_shadow_runtime_gate
.venv/bin/python -m unittest tests.live_l1.test_pre_execution_guards
```

Fresh mandate-time results are:

| Gate | Result | Temporary root |
|---|---:|---|
| Atomic V2 focused | 44/44 PASS, RC 0, `0/0/0` | `/tmp/iu4-i5-denial-mandate-atomic` |
| I5 seam focused | 41/41 PASS, RC 0, `0/0/0` | `/tmp/iu4-i5-denial-mandate-seam` |
| I4 Adapter V2 | 18/18 PASS, RC 0, `0/0/0` | `/tmp/iu4-i5-denial-mandate-adapter` |
| all 15 mandatory modules | 249/249 PASS, RC 0, `0/0/0` | `/tmp/iu4-i5-denial-mandate-mandatory` |
| full `tests/live_l1` | 478/478 PASS, RC 0, `0/0/0` | `/tmp/iu4-i5-denial-mandate-live` |
| full `tests/regression` | 170/170 PASS, RC 0, `0/0/0` | `/tmp/iu4-i5-denial-mandate-regression` |

After correction run the same individual and combined gates, then:

```text
.venv/bin/python -m unittest discover -s tests/live_l1 -p 'test_*.py'
.venv/bin/python -m unittest discover -s tests/regression -p 'test_*.py'
.venv/bin/python -m py_compile live_l1/state/paper_atomic_coordinator.py live_l1/core/paper_iu4_adapter.py tests/live_l1/test_paper_atomic_coordinator_v2.py tests/live_l1/test_paper_iu4_execution_seam_v2.py
git diff --check
git diff --cached --check
```

Mandate-time exact four-path compile passed and created exactly four `.pyc`
files only under `/tmp/iu4-i5-denial-mandate-compile`. Both diff checks passed.
Tests created no repository-local State, journal, Snapshot, log, Evidence or
bytecode.

Final mutation scope is exactly:

```text
MODIFY live_l1/state/paper_atomic_coordinator.py
MODIFY live_l1/core/paper_iu4_adapter.py
MODIFY tests/live_l1/test_paper_atomic_coordinator_v2.py
MODIFY tests/live_l1/test_paper_iu4_execution_seam_v2.py
REPLACE docs/review/PRE_IU4_I5_ACTIVE_EXECUTION_SEAM_IMPLEMENTATION_EVIDENCE_2026-08-20.md
```

No staging, commit, fetch, push, cleanup or foreign-artifact mutation.

## 17. Evidence completion gate

The replaced Evidence record itself must contain:

- all Section-2 identities including this mandate and its independent READY
  rereview;
- mandate-time and final SHA/count for every Section-4 path;
- exact commands, RCs, counts, failures/errors/skips and temporary-root IDs;
- the complete artifact schema/canonicality/tamper matrix;
- exact conditional-serialization compatibility bytes, fingerprints and heads
  for every non-provenance effect;
- complete provenance/effect/origin/capability/cross-binding matrices;
- genuine Account, Throttle and Economics first-commit/replay outputs with
  `state_before.risk.entry_allowed=true`;
- State/SOFT and Runtime-Gate capability same/divergent replay outputs;
- direct active-Loss plus `STATE_CAPABILITY` and `ATOMIC_ENTRY_GUARD`
  provenance rejection with `PEE_ATOMIC_TRANSACTION_INVALID`, zero journal and
  zero Snapshot mutation, plus genuine Adapter ENTRY_VETO/decrement output;
- zero-redecision sentinel call counts for every replay family;
- complete seven-point fault/recovery and resource outcomes;
- failure-code and precedence results;
- all Section-5 hashes/counts and freeze modes/entry count;
- exact five-path mutation output and explicit Loop/Execution preservation;
- no-sidecar/no-State-schema/no-I4-Request-change/no-consumer/no-activation
  searches; and
- `I5_RESULT:PASS` only when every mandatory row passes with zero skips.

The Evidence must explicitly supersede the rejected `ce4e01fd...` PASS claim
without rewriting that historical start record elsewhere. Incomplete or
overstated Evidence is an I5 blocker even when tests are green.

## 18. Stop conditions

The correction stops `BLOCKED` and writes no PASS Evidence if:

- any controlling, start or Preservation identity differs;
- a sixth path is needed;
- conditional omission cannot preserve all non-provenance transaction bytes,
  fingerprints and journal heads;
- accepted I4 Request V2 serialization or test must change;
- Loop or Execution must change;
- a State/S4/Cursor/Loss/Position/Account/Throttle/Quote field changes to carry
  provenance;
- a sidecar, second journal, cache-only truth or ID encoding is proposed;
- any denial origin is ambiguous, defaulted, inferred after commit or accepted
  with inconsistent State/capability facts;
- a denied OPEN/PROGRESS lacks provenance or another effect carries it;
- any provenance Origin is accepted while Loss pause is positive or
  `LOSS_CLUSTER_PAUSE` is active;
- provenance is not transaction-fingerprint and journal-head bound;
- replay calls any business decision, accepts divergent capability or creates a
  second transaction/Cursor;
- genuine Account, Throttle or Economics denial fails exact replay;
- any pre-accept/terminal failure gains PROGRESS or Loss denial stops using
  ENTRY_VETO;
- V1, I4, OFF/SHADOW, non-provenance Atomic V2 or resource semantics drift;
- a non-temporary V2 journal requires migration;
- any test fails, errors, skips, reduces the matrix or writes outside temp;
- real State/process/network/Exchange access is required;
- Git mutation, cleanup or foreign-artifact mutation occurs; or
- an operational ENFORCED consumer, I6 behavior or activation appears.

## 19. Explicit non-scope

No change to `loop.py`, `execution.py`, accepted I4 Request V2 serialization,
`paper_artifacts.py`, `loss_cluster.py`, Runtime/Startup/Shadow gates,
`safe_launch.py`, Ledger, State Store, models, profiles, Authorizations,
manifests, terminal/native, Exchange or Live paths. No new module, sidecar,
journal, fixture or Evidence path. No I6 Recovery/Monitoring/Projection/Handoff,
I7 workstation validation or I8 activation decision. No operational mode switch
or launcher wiring. No GS, Research, RCC002, `engine/`, `run_engine/`, Git
mutation or cleanup. The excluded specification-bundle script is not read,
executed or changed.

## 20. Mandate result and exact next step

```text
MANDATE_RESULT:AUTHORIZED_PENDING_INDEPENDENT_REREVIEW
AUTHORIZED_LATER_PATHS:5
AUTHORIZED_MODIFY_PATHS:4
AUTHORIZED_REPLACE_PATHS:1
I5_CORRECTIVE_IMPLEMENTATION_ENTERED:NO
I5_EVIDENCE_REPLACED:NO
I5_INDEPENDENT_ACCEPTANCE:NOT_READY
OPERATIONAL_ENFORCED_START_AUTHORIZED:NO
ACTIVE_V2_CONSUMER_AUTHORIZED:NO
I6_THROUGH_I8_AUTHORIZED:NO
ENFORCED_ACTIVATION_AUTHORIZED:NO
NEXT_REQUIRED_STEP:IU4-I5-ACTIVE-EXECUTION-SEAM-DURABLE-DENIAL-PROVENANCE-FILE-EXACT-MANDATE-REVISION-INDEPENDENT-READONLY-REREVIEW-2
```

Only the independent read-only file-exact rereview named above may follow.
Implementation begins only after `READY` for this exact mandate identity. This
mandate does not authorize activation under any outcome.
