# Pre-IU4 I5 Active Execution Seam Durable Denial Provenance — File-Exact Mandate Revision — Independent Read-Only Rereview 2 — 2026-08-20

## 1. Decision

```text
WORKSTREAM:IU4-I5-ACTIVE-EXECUTION-SEAM-DURABLE-DENIAL-PROVENANCE-FILE-EXACT-MANDATE-REVISION-INDEPENDENT-READONLY-REREVIEW-2
FINAL_VERDICT:READY
BLOCKER:0
HIGH:0
MEDIUM:0
LOW:0
I5_INDEPENDENT_ACCEPTANCE:READY
CORRECTIVE_IMPLEMENTATION_AUTHORIZED:YES_WITHIN_EXACT_FIVE_PATH_SCOPE
OPERATIONAL_ENFORCED_START_AUTHORIZED:NO
ACTIVE_V2_CONSUMER_AUTHORIZED:NO
I6_THROUGH_I8_AUTHORIZED:NO
ENFORCED_ACTIVATION_AUTHORIZED:NO
EXCHANGE_AUTHORIZED:NO
LIVE_AUTHORIZED:NO
```

The corrected mandate is internally consistent, file-exact and sufficient to
authorize only the later durable-denial-provenance correction within its exact
five-path boundary. This record authorizes neither implementation in this turn
nor an operational ENFORCED start, active V2 consumer, I6-I8 work, Exchange,
Live or activation.

The rereview was performed independently and strictly read-only in the canonical
repository. `AGENTS.md` was read completely before review. No repository, Git,
cleanup or foreign-artifact mutation was performed. The excluded specification-
bundle script was not read, executed or changed.

## 2. Exact reviewed identities

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
| corrected durable-provenance mandate revision 4 | `a688773cc10dd6c573e7c019245639c010a3b0abb49fb301249aeebeba182a91` | 633 | exact candidate |
| mandate revision 3 independent rereview | `28818149ea81b7bc715d86a97ff0e05beccb2c27c66dc39fb28507b37e7d6f2b` | 278 | NOT_READY, one blocker |
| mandate rereview Resolution | `f1bbebd8a6cad12bbf211e275add0f16b5433bc5305ed3fc98af44744f5da80d` | 209 | exact corrective authority |
| Revision-21 specification | `ab8f80720a1d8fe49b9085bce63658bcaecf7f0a3ea70fb555559223090824e0` | 4,605 | controlling |
| final independent I2 rereview | `5a59ad8c97ebae85148661fe0e3bedab643c7f12ae2c8d4e87272447c0616679` | 300 | READY, 97/97 |
| final I3 Evidence | `20846284ffad9e8b755dd6a3b74f963d8d2c6ee1519fafdd0bc1275f2e33c390` | 463 | accepted historical start |
| final independent I3 rereview 6 | `03790420534e38c7e36d1824a472dfd80763340dacec8847ddf5072d55db0c9f` | 191 | READY |
| final I4 Evidence | `068c2ba2661031843a13dd3f2c4684f9340f432b90b192b6b7492dae8968270d` | 403 | accepted |
| final independent I4 rereview 3 | `c6d8bbcb35572a364b74a47eb9ad817240a8b0cce70e514942bb674d3861c38b` | 191 | READY |
| I5 implementation rereview 4 | `15964978eeef90a9e08216beddcd0c33b9a0e37c963f911f7d64705ab52be4c6` | 330 | NOT_READY, 1/0/0/0 |
| durable-provenance scope Resolution | `c08b3b98693a07bc19c2416bc45449cd5b3c8acfbd7457f07c54efa6d6d8dc2f` | 305 | revised mandate required |
| current I5 Evidence | `ce4e01fd1c27f15b13bda72d121eb2c08c541c956a7fc3e20d5da31464c4aa86` | 474 | rejected PASS claim; later replacement target |

All identities and line counts were independently recomputed and matched.

## 3. Closure of the prior blocker

The former Loss-origin ambiguity is closed completely and redundantly at the
origin, effect, test, Evidence and stop-condition layers:

1. `STATE_CAPABILITY` requires all of `risk.entry_allowed is False`,
   `loss_cluster.pause_entries_remaining == 0` and absence of
   `LOSS_CLUSTER_PAUSE` from the Risk reasons.
2. `ATOMIC_ENTRY_GUARD` is limited to Account, Throttle and Control guards. Loss
   is no longer part of that origin.
3. Every provenance origin rejects a positive Loss pause or active
   `LOSS_CLUSTER_PAUSE` as `PEE_ATOMIC_TRANSACTION_INVALID` before journal
   creation, regardless of any other claimed facts.
4. The transaction cross-bindings repeat the same Loss absence requirement.
5. Direct Atomic negative tests are mandatory for active Loss combined with both
   `STATE_CAPABILITY` and `ATOMIC_ENTRY_GUARD` provenance.
6. Genuine Adapter Loss pause remains exclusively `ENTRY_VETO` and decrements
   exactly once.
7. The replaced Evidence must contain the exact rejection, zero-journal,
   zero-Snapshot and genuine ENTRY_VETO/decrement outputs.
8. Acceptance of any provenance while Loss pause is positive or
   `LOSS_CLUSTER_PAUSE` is active is an explicit blocking stop condition.

There is therefore no remaining overlap between non-Loss rejected
`OPEN -> PROGRESS` provenance and the accepted Loss `ENTRY_VETO` path.

## 4. Full contract assessment

The remaining mandate contract is complete and implementable within the released
paths:

- one strict `AtomicEntryDenialProvenanceV1` artifact with closed field set,
  canonical primitives, exact fingerprint and no defaults;
- exactly two transaction record shapes: the mandate-time base shape with the
  provenance key omitted, or the base shape plus one strict provenance object;
- explicit JSON null, unknown fields, alternate spellings, subclasses,
  lookalikes and tampered fingerprints fail closed;
- when provenance is `None`, canonical payload, record, transaction fingerprint
  and journal head remain byte-for-byte identical for existing OPEN, CLOSE,
  ENTRY_VETO, KILL and ordinary PROGRESS transactions;
- when present, the complete artifact is transaction-fingerprint bound and its
  fingerprint is journal-head bound;
- provenance is transaction effect metadata only and cannot change Position,
  Account, Throttle, Loss, Quote, S4, Cursor business payload or State schema;
- provenance is permitted only for rejected non-Loss OPEN requests whose sole
  durable effect is PROGRESS;
- Event, State, Snapshot, timestamp, Tick, Intent, action, Cursor, origin,
  capability and empty-escalation bindings are exact;
- same-ID exact replay is idempotent; null/non-null or any field divergence is a
  conflict with no second journal transaction or Snapshot;
- replay loads the existing durable transaction under the established Atomic
  root lock before any business decision and performs no second Control, Gate,
  State-capability, economics, Account, Throttle, Loss or `_effect` decision;
- genuine Account, Throttle, Economics, State/SOFT and Runtime-Gate denial
  families have explicit same-capability replay and divergent-capability
  conflict requirements;
- the seven-point fault/recovery grid, resource classifications, stable failure
  codes, mutation ceilings and Evidence completion gate are explicit;
- no sidecar, second journal, migration, State field, I4 Request field, cache-only
  truth, ID encoding or sixth path is permitted.

No contradiction with Revision 21, the accepted I3 transaction authority, the
accepted I4 Request contract or the frozen corrected I5 Loop/Execution bytes was
found.

## 5. Exact later correction scope

Exactly the following five existing paths are authorized for the separately
invoked corrective implementation workstream:

| Operation | Path | Mandate-time SHA-256 | Lines |
|---|---|---|---:|
| MODIFY | `live_l1/state/paper_atomic_coordinator.py` | `d0721ae5def3551ba7281ea0e367f5347890fd4cd7187d8f2aebb98d2651e84f` | 5,489 |
| MODIFY | `live_l1/core/paper_iu4_adapter.py` | `e8804916b8a2142459b661933d5582455ae52640cce9d9c4d38ad6102d641dac` | 1,710 |
| MODIFY | `tests/live_l1/test_paper_atomic_coordinator_v2.py` | `16d0fea6e5588cc14329ba61cfeeccb1f72478d14c358f8ed4e38c1ac3a41bb9` | 2,482 |
| MODIFY | `tests/live_l1/test_paper_iu4_execution_seam_v2.py` | `36356eec13e2b854556582a086987f719930ee9ef69672348413a5c06f94c807` | 2,051 |
| REPLACE | `docs/review/PRE_IU4_I5_ACTIVE_EXECUTION_SEAM_IMPLEMENTATION_EVIDENCE_2026-08-20.md` | `ce4e01fd1c27f15b13bda72d121eb2c08c541c956a7fc3e20d5da31464c4aa86` | 474 |

No sixth implementation path is authorized or required. In particular,
`live_l1/core/loop.py` and `live_l1/core/execution.py` are read-only inputs.

## 6. Preservation and freeze verification

All 25 Section-5 preservation identities and counts matched exactly. The key
frozen identities are:

```text
LOOP_SHA256:e4db22642b628fe4b84cf0d2daa9ecd846208138eaa3868a02a56ddf9f75ee6c
LOOP_LINES:1947
EXECUTION_SHA256:85a9acb238dafd3adf5fd8bf57153772d3c7b41559943bdcce5336e3b60dcb5e
EXECUTION_LINES:1386
FREEZE_DIRECTORY_MODE:0555
PRESERVATION_TAR_SHA256:3af14ff2e270d7d3ca09c1279da7d64e6d720630d06a0c5f45b6786237782037
PRESERVATION_TAR_MODE:0444
PRESERVATION_TAR_ENTRIES:1318
FREEZE_MANIFEST_SHA256:ad154c0eda13470920878873ed170368cc8f4c43591400a07592a77b179d9e16
FREEZE_MANIFEST_MODE:0444
FREEZE_MANIFEST_LINES:60
```

The exact preserved identities were also confirmed for `paper_artifacts.py`,
`loss_cluster.py`, the Adapter V2 test, accepted I3/I4 Evidence, Pure Control,
Runtime/Startup/Shadow gates, Shadow Harness, Lifecycle Ledger, State Store,
models, economics, both throttle modules, Safe Launch and the three listed
Legacy/adjacent tests.

## 7. Fresh mandatory verification

Every Python run used `PYTHONDONTWRITEBYTECODE=1`, a fresh isolated `TMPDIR` and
an external `PYTHONPYCACHEPREFIX`. Every run completed with RC 0 and
failures/errors/skips `0/0/0`.

| Gate | Result | Temporary root |
|---|---:|---|
| Atomic V2 focused | 44/44 PASS | `/tmp/iu4-i5-denial-rereview2-individual.47wqK7` |
| I5 seam focused | 41/41 PASS | `/tmp/iu4-i5-denial-rereview2-individual.Akit13` |
| I4 Adapter V2 | 18/18 PASS | `/tmp/iu4-i5-denial-rereview2-individual.JKtCSt` |
| Adapter V1 | 13/13 PASS | `/tmp/iu4-i5-denial-rereview2-individual.2OID6n` |
| Pure Control | 25/25 PASS | `/tmp/iu4-i5-denial-rereview2-individual.mWBsZP` |
| Atomic V1 | 23/23 PASS | `/tmp/iu4-i5-denial-rereview2-individual.G9u6N4` |
| Startup Gate | 12/12 PASS | `/tmp/iu4-i5-denial-rereview2-individual.n5K4tK` |
| Runtime Gate | 3/3 PASS | `/tmp/iu4-i5-denial-rereview2-individual.RG1Jpj` |
| Shadow Harness | 18/18 PASS | `/tmp/iu4-i5-denial-rereview2-individual.bBMOsJ` |
| Shadow Observation | 18/18 PASS | `/tmp/iu4-i5-denial-rereview2-individual.1cO5kO` |
| Replay Evidence | 10/10 PASS | `/tmp/iu4-i5-denial-rereview2-individual.wzKXgH` |
| Replay Pipeline | 6/6 PASS | `/tmp/iu4-i5-denial-rereview2-individual.sWSHrQ` |
| Economics Shadow | 9/9 PASS | `/tmp/iu4-i5-denial-rereview2-individual.FUASZG` |
| Safe Launch | 3/3 PASS | `/tmp/iu4-i5-denial-rereview2-individual.DK6ifQ` |
| Preexecution Guards | 6/6 PASS | `/tmp/iu4-i5-denial-rereview2-individual.0nhevj` |
| all 15 mandatory modules | 249/249 PASS | `/tmp/iu4-i5-denial-rereview2-mandatory.mQrExs` |
| full `tests/live_l1` | 478/478 PASS | `/tmp/iu4-i5-denial-rereview2-live.ebsgTP` |
| full `tests/regression` | 170/170 PASS | `/tmp/iu4-i5-denial-rereview2-regression.ClUg7B` |

Exact four-path compile:

```text
ROOT:/tmp/iu4-i5-denial-rereview2-compile.lvceKL
COMPILE_RESULT:PASS
COMPILE_RC:0
PYC_COUNT:4
PYC_LOCATION:ONLY_UNDER_EXTERNAL_PYTHONPYCACHEPREFIX
GIT_DIFF_CHECK:PASS
GIT_CACHED_DIFF_CHECK:PASS
```

No test created repository-local State, journal, Snapshot, log, Evidence or
bytecode.

## 8. Scope and non-activation findings

- The five mandate-time implementation identities remain exact.
- The provenance class and transaction member do not yet exist; implementation
  has not begun.
- The active Loop continues to select literal `LEGACY`.
- No productive construction or active consumer of `PaperAtomicCoordinatorV2`
  or `PaperIU4AdapterV2` exists.
- No operational V2 journal root, launcher exposure, I6 behavior, Exchange,
  Live or activation path was found.
- Existing foreign dirty/untracked worktree artifacts were preserved and not
  cleaned or changed.

## 9. Final authorization boundary and next step

```text
PRIOR_REREVIEW_BLOCKER:CLOSED
MANDATE_READY:YES
I5_INDEPENDENT_ACCEPTANCE:READY
CORRECTIVE_IMPLEMENTATION_AUTHORIZED:YES_WITHIN_EXACT_FIVE_PATH_SCOPE
I5_CORRECTIVE_IMPLEMENTATION_ENTERED:NO
I5_EVIDENCE_REPLACED:NO
OPERATIONAL_ENFORCED_START_AUTHORIZED:NO
ACTIVE_V2_CONSUMER_AUTHORIZED:NO
I6_THROUGH_I8_AUTHORIZED:NO
ENFORCED_ACTIVATION_AUTHORIZED:NO
NEXT_REQUIRED_STEP:IU4-I5-ACTIVE-EXECUTION-SEAM-DURABLE-DENIAL-PROVENANCE-IMPLEMENTATION-FILE-EXACT
```

Only the separate corrective implementation workstream named above may follow,
and it may mutate only the exact five paths in Section 5. This READY decision
does not authorize operational ENFORCED start, an active V2 consumer, I6-I8,
Exchange, Live or activation.
