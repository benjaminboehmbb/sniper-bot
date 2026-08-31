# Pre-IU4 I5 Active Execution Seam Durable Denial Provenance — Implementation Evidence — 2026-08-20

## 1. Result

```text
WORKSTREAM:IU4-I5-ACTIVE-EXECUTION-SEAM-DURABLE-DENIAL-PROVENANCE-IMPLEMENTATION-FILE-EXACT
I5_RESULT:PASS
I5_CORRECTIVE_IMPLEMENTATION_COMPLETE:YES
AUTHORIZED_PATHS_USED:5/5
FAILURES:0
ERRORS:0
SKIPS:0
I5_INDEPENDENT_ACCEPTANCE:PENDING
OPERATIONAL_ENFORCED_START_AUTHORIZED:NO
ACTIVE_V2_CONSUMER_AUTHORIZED:NO
I6_THROUGH_I8_AUTHORIZED:NO
ENFORCED_ACTIVATION_AUTHORIZED:NO
EXCHANGE_AUTHORIZED:NO
LIVE_AUTHORIZED:NO
```

This record supersedes the rejected mandate-time Evidence identity
`ce4e01fd1c27f15b13bda72d121eb2c08c541c956a7fc3e20d5da31464c4aa86`
and the rejected rereview-2 candidate identity
`8c315972b977b0e494d178deaf672c2e08903f5bfa1d5d5909a5f80055914341`
without changing any historical rereview or Resolution record. The corrective
package adds durable provenance only for accepted non-Loss denied
`OPEN -> PROGRESS` transactions. It does not activate ENFORCED, add a consumer,
change Loop/Execution, or authorize I6-I8.

`AGENTS.md` was read completely before implementation. The excluded
specification-bundle script was not read, executed or changed. No Git mutation,
cleanup or foreign-artifact mutation was performed.

## 2. Controlling identities

```text
CANONICAL_REPOSITORY:/home/benja/projects/sniper-bot
BRANCH:main
HEAD:c7ce0452aa2ccbf08c462784d68fa07b3dfe9595
MAIN:c7ce0452aa2ccbf08c462784d68fa07b3dfe9595
ORIGIN_MAIN:89e13fecd1ab549ca7099818b1c9ad4984cb6f7a
MAIN_AHEAD_OF_ORIGIN:6
MAIN_BEHIND_ORIGIN:0
```

| Authority | SHA-256 | Lines | Result |
|---|---|---:|---|
| Revision-21 specification | `ab8f80720a1d8fe49b9085bce63658bcaecf7f0a3ea70fb555559223090824e0` | 4,605 | controlling |
| final independent I2 rereview | `5a59ad8c97ebae85148661fe0e3bedab643c7f12ae2c8d4e87272447c0616679` | 300 | READY, 97/97 |
| final I3 Evidence | `20846284ffad9e8b755dd6a3b74f963d8d2c6ee1519fafdd0bc1275f2e33c390` | 463 | accepted |
| final independent I3 rereview 6 | `03790420534e38c7e36d1824a472dfd80763340dacec8847ddf5072d55db0c9f` | 191 | READY |
| final I4 Evidence | `068c2ba2661031843a13dd3f2c4684f9340f432b90b192b6b7492dae8968270d` | 403 | accepted |
| final independent I4 rereview 3 | `c6d8bbcb35572a364b74a47eb9ad817240a8b0cce70e514942bb674d3861c38b` | 191 | READY |
| I5 implementation rereview 4 | `15964978eeef90a9e08216beddcd0c33b9a0e37c963f911f7d64705ab52be4c6` | 330 | NOT_READY, durable denial provenance required |
| durable-provenance scope Resolution | `c08b3b98693a07bc19c2416bc45449cd5b3c8acfbd7457f07c54efa6d6d8dc2f` | 305 | revised mandate required |
| corrected durable-provenance mandate revision 4 | `a688773cc10dd6c573e7c019245639c010a3b0abb49fb301249aeebeba182a91` | 633 | authorized exact scope |
| mandate revision 3 NOT_READY rereview | `28818149ea81b7bc715d86a97ff0e05beccb2c27c66dc39fb28507b37e7d6f2b` | 278 | historical blocker |
| mandate rereview Resolution | `f1bbebd8a6cad12bbf211e275add0f16b5433bc5305ed3fc98af44744f5da80d` | 209 | blocker closed |
| mandate independent rereview 2 | `934bf4a9010aff61796cc2c7c09f54380c5527546bea6e4bc25b5a17933bfd59` | 242 | READY, 0/0/0/0 |
| first durable-provenance implementation rereview | `88fe9751f16fa0f396ba4f6d63db6aa5ad578020dd8a46ba03d3b7912606c245` | 352 | NOT_READY, 2/0/0/0 |
| first implementation Resolution | `13666d2b9a3efbee1813d4f4cf6e480a5021f0b013f8c55d20bd87e9602f5e03` | 226 | partial closure submitted |
| implementation independent rereview 2 | `ce32b2ac3add765a9794823123063e06b56f9aba31738781cd5e880f9d92561f` | 282 | NOT_READY, 2/0/0/0; closed by this correction |

## 3. Exact five-path scope and identities

| Operation | Path | Mandate-time identity | Final identity |
|---|---|---|---|
| MODIFY | `live_l1/state/paper_atomic_coordinator.py` | `d0721ae5def3551ba7281ea0e367f5347890fd4cd7187d8f2aebb98d2651e84f`, 5,489 | `446ae8712d09bc52f950587a2e3ecec0c60fd21b3c9150a8886af1b3b2b4f9ec`, 5,796 |
| MODIFY | `live_l1/core/paper_iu4_adapter.py` | `e8804916b8a2142459b661933d5582455ae52640cce9d9c4d38ad6102d641dac`, 1,710 | `1fac2629a0ebdd889825f496e9273c358ffe7596c2173d307ce1d1eb7e9bd6a6`, 1,896 |
| MODIFY | `tests/live_l1/test_paper_atomic_coordinator_v2.py` | `16d0fea6e5588cc14329ba61cfeeccb1f72478d14c358f8ed4e38c1ac3a41bb9`, 2,482 | `ec731c106ab23b78e482204e16d20826264cdf775f0c08c292a82bab1111ff8c`, 3,734 |
| MODIFY | `tests/live_l1/test_paper_iu4_execution_seam_v2.py` | `36356eec13e2b854556582a086987f719930ee9ef69672348413a5c06f94c807`, 2,051 | `fc61404d910fe76141cba8ba54f98ea6de552664a8b21bdaa50510e33f603755`, 2,517 |
| REPLACE | this Evidence path | `ce4e01fd1c27f15b13bda72d121eb2c08c541c956a7fc3e20d5da31464c4aa86`, 474 | final byte SHA-256 and stable line count bound by the companion Rereview-2 Resolution record |

Exact mutation scope:

```text
MODIFY live_l1/state/paper_atomic_coordinator.py
MODIFY live_l1/core/paper_iu4_adapter.py
MODIFY tests/live_l1/test_paper_atomic_coordinator_v2.py
MODIFY tests/live_l1/test_paper_iu4_execution_seam_v2.py
REPLACE docs/review/PRE_IU4_I5_ACTIVE_EXECUTION_SEAM_IMPLEMENTATION_EVIDENCE_2026-08-20.md
```

The Evidence path cannot contain its own post-serialization byte SHA-256
without changing that SHA-256. Its actual final byte identity and stable line
count are therefore recorded by the companion file-exact Resolution after this
Evidence is serialized. This is an explicit non-self-referential binding, not a
placeholder or omitted identity. No sixth implementation path was used.
`loop.py` and `execution.py` remain the
frozen corrected I5 inputs recorded in Section 13.

## 4. Provenance artifact schema and canonicality matrix

`AtomicEntryDenialProvenanceV1` is a frozen coordinator-owned dataclass with
exactly twelve payload fields and one derived fingerprint:

| Field | Implemented invariant | Positive/negative evidence |
|---|---|---|
| `schema_version` | exact primitive integer `1` | bool, integer subclass and `2` reject |
| `artifact_type` | exact `atomic_entry_denial_provenance_v1` | case/alternate type reject as unsupported schema |
| `transaction_event_id` | exact nonempty canonical text | empty, padding and text subclass reject |
| `snapshot_id` | exact nonempty canonical text | empty/padding reject |
| `timestamp_utc` | UTC whole seconds ending `Z` | offset spelling, fractional, naive and malformed reject |
| `tick_id` | exact primitive integer >= 0 | bool, Float, subclass and negative reject |
| `intent_id` | exact nonempty canonical text | empty/padding reject |
| `intent_action` | exact `OPEN_LONG` or `OPEN_SHORT` | case, whitespace and other Actions reject |
| `state_before_fingerprint` | exact lowercase SHA-256 | uppercase, nonhex and wrong length reject |
| `denial_origin` | one of four closed Origins | case, whitespace and unknown reject |
| `denial_reason_code` | exact `PEE_IU4_ENTRY_BLOCKED` | alternate public/Atomic reason rejects |
| `entry_capability_allowed` | exact primitive bool | integer/string/lookalike reject |
| `provenance_fingerprint` | SHA-256 of canonical JSON over exactly the twelve payload fields | field and fingerprint tamper reject |

Missing and unknown keys, explicit alternate spellings, noncanonical records,
nested Float values and raw noncanonical JSON fail closed. `from_record()`
requires exact equality to `to_record()` after strict construction. Valid
roundtrip is exact and contains 13 persisted fields.

Every identity-bearing mutable payload field changes the provenance
fingerprint. Independent valid Runtime-Gate versus Economics provenance built
over otherwise identical State/Cursor inputs produced distinct provenance
fingerprints, transaction fingerprints and journal heads.

## 5. Conditional transaction serialization and compatibility

The transaction member is exactly
`effect_entry_denial_provenance: AtomicEntryDenialProvenanceV1 | None`.

| Transaction/effect | Provenance key in record | Result |
|---|---:|---|
| mandate-time OPEN | omitted | record/fingerprint/head path unchanged |
| mandate-time CLOSE | omitted | record/fingerprint/head path unchanged |
| mandate-time ENTRY_VETO | omitted | record/fingerprint/head path unchanged |
| mandate-time KILL | omitted | record/fingerprint/head path unchanged |
| ordinary PROGRESS | omitted | exact base record roundtrip PASS |
| denied non-Loss OPEN -> PROGRESS | one strict object | transaction fingerprint and journal head bind it |

Explicit JSON null is rejected. The parser accepts exactly the base field set or
the base field set plus one mapping-valued provenance object. All pre-correction
base transactions omit the new key and the journal-head payload adds no
provenance material when the member is `None`; therefore their canonical bytes,
fingerprints and heads remain structurally byte-identical. The preserved 44
mandate-time Atomic V2 tests remain green inside the expanded 54-test module.

Provenance cannot appear on OPEN, CLOSE, ENTRY_VETO or KILL and cannot coexist
with Entry Event, Trade, Position, Quote, Throttle-policy, Entry-Veto Candidate,
Loss transition, target Kill, Control authorization or risk escalation.

## 6. Origin, capability and first-commit matrix

| First authoritative blocker | Origin | State entry capability | trusted Gate capability | Durable result |
|---|---|---:|---:|---|
| State/S4/SOFT non-Loss blocker | `STATE_CAPABILITY` | false | false or true | one rejected PROGRESS |
| Runtime Gate | `RUNTIME_GATE_CAPABILITY` | true | false | one rejected PROGRESS |
| Economics authorization/no Quote | `ECONOMICS_AUTHORIZATION` | true | true | one rejected PROGRESS |
| Account guard | `ATOMIC_ENTRY_GUARD` | true before Atomic recheck | true | one rejected PROGRESS |
| Throttle guard | `ATOMIC_ENTRY_GUARD` | true before Atomic recheck | true | one rejected PROGRESS |

The focused Seam test executes all five rows through the public Adapter API.
The Account row uses a genuine Account-day regression, the Throttle row a
genuine Throttle-day regression, and the Economics row a genuine minimum
quantity/notional denial. Each begins with the exact State facts required by
the mandate and returns:

```text
STATUS:REJECTED
PRIMARY_EFFECT:PROGRESS
REASON_CODE:PEE_IU4_ENTRY_BLOCKED
TRANSACTION_COUNT:1
CURSOR_COUNT:1
POSITION/ACCOUNT/THROTTLE/LOSS:UNCHANGED
```

The Adapter selects the first blocker once and never overwrites it with a later
origin. Direct Atomic positive tests cover both capability values for
`STATE_CAPABILITY` and every other allowed Origin/capability tuple. Origin/fact
mismatches fail as `PEE_ATOMIC_TRANSACTION_INVALID` before journal creation.

## 7. Durable replay, conflicts and zero-redecision proof

Replay lookup occurs under the existing root-exclusive lock before State load
or any authorization. For a provenance-bearing transaction, the Adapter:

1. uses the already strictly parsed transaction and journal head;
2. checks Request content ID, trusted Context, Authorization, State-before,
   profiles, timestamp, Tick, Snapshot, Intent, Action, capability, effect and
   escalation against the durable provenance;
3. invokes only existing-transaction coordinator materialization/readback; and
4. returns rejected PROGRESS with `already_committed=true` and no second Tick.

For each State, Gate, Economics, Account and Throttle denial family the second
identical call was run with failing sentinels on Adapter `_effect`, the accepted
I4 validator, economics authorization, Atomic OPEN guards and risk derivation.
Every sentinel call count remained zero and replay succeeded. The durable
transaction path preserves Risk business fields and changes only Cursor and
transaction heads; recovery validation therefore requires no Account,
Throttle, Loss, Control, Gate, Economics or State decision.

| Replay variation | Exact outcome | Mutation |
|---|---|---|
| same Request and same stored capability | rejected PROGRESS, already committed | none |
| Gate false then true | `PEE_IU4_ADAPTER_REQUEST_CONFLICT` | none |
| Gate true then false | `PEE_IU4_ADAPTER_REQUEST_CONFLICT` | none |
| same Event with different Origin/provenance | `PEE_IU4_PROGRESS_CONFLICT` | none |
| null versus non-null provenance | `PEE_IU4_PROGRESS_CONFLICT` | none |
| divergent Request/context/profile/authorization | stable Adapter binding/conflict family | none |
| journal/provenance fingerprint tamper | `PEE_ATOMIC_JOURNAL_CONFLICT` | none |

## 8. Loss exclusivity and mutation ceiling

Every provenance Origin requires both `pause_entries_remaining == 0` and absence
of `LOSS_CLUSTER_PAUSE`. Direct Atomic attempts to attach either
`STATE_CAPABILITY` or `ATOMIC_ENTRY_GUARD` provenance to active Loss State fail
as `PEE_ATOMIC_TRANSACTION_INVALID` with zero journal and zero Snapshot change.

The genuine Adapter Loss case remains an ENTRY_VETO transaction, contains no
denial provenance, decrements the Loss pause exactly once and replays without a
second decrement. Pre-accept binding, terminal and malformed failures still
write no Tick transaction.

For a provenance-bearing PROGRESS:

- Position, Account, Throttle, Loss and Entry Quote are exactly unchanged;
- Risk business values and component fingerprints remain unchanged except the
  required Progress-Cursor fingerprint;
- only sequence, journal, last-Event/time/Tick and Cursor heads advance; and
- State contains no provenance field or sidecar reference.

## 9. Fault, recovery and resource outcomes

The required seven boundaries are covered row-completely by the combined Atomic
and Seam modules. Every row asserts the result, journal count, Snapshot
sequence/head, Cursor, provenance record/fingerprint, transaction
fingerprint/head, component fingerprints, retry/replay outcome and applicable
decision-sentinel counts. Rows one and two have no durable transaction; row
three now performs a controlled retry to exactly one commit and then an exact
replay instead of terminating early. Rows four through six recover or read back
exactly one transaction. Row seven proves the public Adapter replay with six
failing decision sentinels.

The complete literal identities and outcomes are serialized in Section 15.5.

Controlled `OSError(ENOSPC)`, `PermissionError(EACCES)`, `OSError(EMFILE)` and
`MemoryError` injections at create-new publication all map to
`PEE_IU4_RESOURCE_EXHAUSTED`, leave State unchanged and create no Legacy
fallback. Snapshot publication failure leaves exactly one recoverable durable
transaction, as proven by the preserved Atomic resource test.

## 10. Stable failure codes and precedence

| Failure | Implemented code |
|---|---|
| unsupported provenance schema/artifact | `PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED` |
| malformed/canonicality/cross-binding/origin | `PEE_ATOMIC_TRANSACTION_INVALID` |
| provenance/transaction/head tamper | `PEE_ATOMIC_JOURNAL_CONFLICT` |
| same PROGRESS Event with divergent provenance | `PEE_IU4_PROGRESS_CONFLICT` |
| Adapter replay Request/capability/effect/escalation divergence | `PEE_IU4_ADAPTER_REQUEST_CONFLICT` |
| accepted first denial or exact replay | `PEE_IU4_ENTRY_BLOCKED` |
| disk/permission/FD/memory publication | `PEE_IU4_RESOURCE_EXHAUSTED` |

The enforced order is type/schema, canonicality/fingerprint, Request/trusted
binding, terminal capability, provenance/effect cross-binding, same-ID payload,
then materialization. No failure falls back to Legacy.

## 11. Focused test inventory

The Atomic V2 module contains 54 tests. Its new table-driven coverage includes:

- every provenance field and strict record/fingerprint roundtrip;
- missing/unknown, primitive subclass, bool/int/Float, UTC, SHA, enum, case,
  whitespace and tamper negatives;
- explicit-null and two-shape transaction parsing;
- base-record omission compatibility;
- fingerprint/transaction/head sensitivity;
- every allowed Origin/capability tuple and Loss-origin negatives;
- same-ID idempotence and divergent provenance conflicts;
- component/Risk mutation ceilings;
- four durable crash points, including controlled pre-journal retry, exact
  recovery/readback, per-row decision sentinels and resource classification;
- fixed non-provenance Golden record/fingerprint/head hashes for all five
  effects, every Origin/facts mismatch, direct disallowed effects,
  self-consistent refingerprinted transaction/journal tamper and stable
  multi-failure precedence.

The Seam module contains 44 tests. Its added coverage includes:

- required capability argument and exact-bool rejection before State access;
- genuine State, Gate, Economics, Account and Throttle denied OPENs;
- exact durable Origin/capability values;
- identical replay under failing business-decision sentinels;
- both capability-divergence directions;
- genuine Loss ENTRY_VETO with no provenance and exactly one decrement.
- provenance-bearing denial before accepted validation with five zero-call
  decision sentinels, after validation but before the Coordinator call with
  exact first-decision counts, and exact durable readback with six zero-call
  redecision sentinels.

No test was skipped, xfailed, reduced to manual-only evidence or permitted to
write repository State, journal, Snapshot, log, Evidence or bytecode.

## 12. Mandatory commands and exact results

Every Python run used `PYTHONDONTWRITEBYTECODE=1`, a fresh isolated `TMPDIR` and
an external `PYTHONPYCACHEPREFIX`.

### 12.1 Pre-mutation baselines

| Gate | Root | Result | RC | failures/errors/skips |
|---|---|---:|---:|---:|
| all 15 mandatory modules | `/tmp/iu4-i5-denial-impl-pre-mandatory.gVb9O1` | 249/249 PASS | 0 | 0/0/0 |
| full `tests/live_l1` | `/tmp/iu4-i5-denial-impl-pre-live.LErKWX` | 478/478 PASS | 0 | 0/0/0 |
| full `tests/regression` | `/tmp/iu4-i5-denial-impl-pre-regression.opzWpx` | 170/170 PASS | 0 | 0/0/0 |
| exact four-path compile | `/tmp/iu4-i5-denial-impl-pre-compile.Rt3sPK` | PASS, 4 `.pyc` | 0 | 0/0/0 |

The immediately preceding independent READY mandate rereview additionally ran
all 15 modules individually against the same mandate-time bytes.

### 12.2 Rereview-2 Resolution final individual modules

The obsolete 51/43 and 258/487 runs belonged to the superseded pre-Resolution
candidate and are not final results. The following are the only final
individual-module results for this Evidence identity.

| Module | Root | Result | RC | failures/errors/skips |
|---|---|---:|---:|---:|
| Atomic V2 | `/tmp/iu4-i5-dp-r2res-test_paper_atomic_coordinator_v2.Bbxkvp` | 54/54 PASS | 0 | 0/0/0 |
| I5 Seam | `/tmp/iu4-i5-dp-r2res-test_paper_iu4_execution_seam_v2.uJPDFr` | 44/44 PASS | 0 | 0/0/0 |
| I4 Adapter V2 | `/tmp/iu4-i5-dp-r2res-test_paper_iu4_adapter_v2.0fA1cm` | 18/18 PASS | 0 | 0/0/0 |
| Adapter V1 | `/tmp/iu4-i5-dp-r2res-test_paper_iu4_adapter.sYSj5d` | 13/13 PASS | 0 | 0/0/0 |
| Pure Control | `/tmp/iu4-i5-dp-r2res-test_paper_execution_control.BCRmWG` | 25/25 PASS | 0 | 0/0/0 |
| Atomic V1 | `/tmp/iu4-i5-dp-r2res-test_paper_atomic_coordinator.OVPE6x` | 23/23 PASS | 0 | 0/0/0 |
| Startup Gate | `/tmp/iu4-i5-dp-r2res-test_paper_iu4_startup_gate.lTfMsi` | 12/12 PASS | 0 | 0/0/0 |
| Runtime Gate | `/tmp/iu4-i5-dp-r2res-test_paper_iu4_runtime_gate.a3W1QK` | 3/3 PASS | 0 | 0/0/0 |
| Shadow Harness | `/tmp/iu4-i5-dp-r2res-test_paper_iu4_shadow_harness.87lx3g` | 18/18 PASS | 0 | 0/0/0 |
| Shadow Observation | `/tmp/iu4-i5-dp-r2res-test_paper_iu4_shadow_observation_gate.dpv5Yk` | 18/18 PASS | 0 | 0/0/0 |
| Replay Evidence | `/tmp/iu4-i5-dp-r2res-test_paper_iu4_replay_evidence.JAdtcK` | 10/10 PASS | 0 | 0/0/0 |
| Replay Pipeline | `/tmp/iu4-i5-dp-r2res-test_paper_iu4_replay_pipeline.cCtB1e` | 6/6 PASS | 0 | 0/0/0 |
| Economics Shadow | `/tmp/iu4-i5-dp-r2res-test_paper_economics_shadow_runtime.7htbF0` | 9/9 PASS | 0 | 0/0/0 |
| Safe Launch | `/tmp/iu4-i5-dp-r2res-test_safe_launch_iu4_shadow_runtime_gate.aN3u2P` | 3/3 PASS | 0 | 0/0/0 |
| Preexecution Guards | `/tmp/iu4-i5-dp-r2res-test_pre_execution_guards.iXsazk` | 6/6 PASS | 0 | 0/0/0 |

The literal individual commands were:

```text
PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/iu4-i5-dp-r2res-test_paper_atomic_coordinator_v2.Bbxkvp PYTHONPYCACHEPREFIX=/tmp/iu4-i5-dp-r2res-test_paper_atomic_coordinator_v2.Bbxkvp/pycache .venv/bin/python -m unittest tests.live_l1.test_paper_atomic_coordinator_v2
PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/iu4-i5-dp-r2res-test_paper_iu4_execution_seam_v2.uJPDFr PYTHONPYCACHEPREFIX=/tmp/iu4-i5-dp-r2res-test_paper_iu4_execution_seam_v2.uJPDFr/pycache .venv/bin/python -m unittest tests.live_l1.test_paper_iu4_execution_seam_v2
PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/iu4-i5-dp-r2res-test_paper_iu4_adapter_v2.0fA1cm PYTHONPYCACHEPREFIX=/tmp/iu4-i5-dp-r2res-test_paper_iu4_adapter_v2.0fA1cm/pycache .venv/bin/python -m unittest tests.live_l1.test_paper_iu4_adapter_v2
PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/iu4-i5-dp-r2res-test_paper_iu4_adapter.sYSj5d PYTHONPYCACHEPREFIX=/tmp/iu4-i5-dp-r2res-test_paper_iu4_adapter.sYSj5d/pycache .venv/bin/python -m unittest tests.live_l1.test_paper_iu4_adapter
PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/iu4-i5-dp-r2res-test_paper_execution_control.BCRmWG PYTHONPYCACHEPREFIX=/tmp/iu4-i5-dp-r2res-test_paper_execution_control.BCRmWG/pycache .venv/bin/python -m unittest tests.live_l1.test_paper_execution_control
PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/iu4-i5-dp-r2res-test_paper_atomic_coordinator.OVPE6x PYTHONPYCACHEPREFIX=/tmp/iu4-i5-dp-r2res-test_paper_atomic_coordinator.OVPE6x/pycache .venv/bin/python -m unittest tests.live_l1.test_paper_atomic_coordinator
PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/iu4-i5-dp-r2res-test_paper_iu4_startup_gate.lTfMsi PYTHONPYCACHEPREFIX=/tmp/iu4-i5-dp-r2res-test_paper_iu4_startup_gate.lTfMsi/pycache .venv/bin/python -m unittest tests.live_l1.test_paper_iu4_startup_gate
PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/iu4-i5-dp-r2res-test_paper_iu4_runtime_gate.a3W1QK PYTHONPYCACHEPREFIX=/tmp/iu4-i5-dp-r2res-test_paper_iu4_runtime_gate.a3W1QK/pycache .venv/bin/python -m unittest tests.live_l1.test_paper_iu4_runtime_gate
PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/iu4-i5-dp-r2res-test_paper_iu4_shadow_harness.87lx3g PYTHONPYCACHEPREFIX=/tmp/iu4-i5-dp-r2res-test_paper_iu4_shadow_harness.87lx3g/pycache .venv/bin/python -m unittest tests.live_l1.test_paper_iu4_shadow_harness
PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/iu4-i5-dp-r2res-test_paper_iu4_shadow_observation_gate.dpv5Yk PYTHONPYCACHEPREFIX=/tmp/iu4-i5-dp-r2res-test_paper_iu4_shadow_observation_gate.dpv5Yk/pycache .venv/bin/python -m unittest tests.live_l1.test_paper_iu4_shadow_observation_gate
PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/iu4-i5-dp-r2res-test_paper_iu4_replay_evidence.JAdtcK PYTHONPYCACHEPREFIX=/tmp/iu4-i5-dp-r2res-test_paper_iu4_replay_evidence.JAdtcK/pycache .venv/bin/python -m unittest tests.live_l1.test_paper_iu4_replay_evidence
PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/iu4-i5-dp-r2res-test_paper_iu4_replay_pipeline.cCtB1e PYTHONPYCACHEPREFIX=/tmp/iu4-i5-dp-r2res-test_paper_iu4_replay_pipeline.cCtB1e/pycache .venv/bin/python -m unittest tests.live_l1.test_paper_iu4_replay_pipeline
PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/iu4-i5-dp-r2res-test_paper_economics_shadow_runtime.7htbF0 PYTHONPYCACHEPREFIX=/tmp/iu4-i5-dp-r2res-test_paper_economics_shadow_runtime.7htbF0/pycache .venv/bin/python -m unittest tests.live_l1.test_paper_economics_shadow_runtime
PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/iu4-i5-dp-r2res-test_safe_launch_iu4_shadow_runtime_gate.aN3u2P PYTHONPYCACHEPREFIX=/tmp/iu4-i5-dp-r2res-test_safe_launch_iu4_shadow_runtime_gate.aN3u2P/pycache .venv/bin/python -m unittest tests.live_l1.test_safe_launch_iu4_shadow_runtime_gate
PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/iu4-i5-dp-r2res-test_pre_execution_guards.iXsazk PYTHONPYCACHEPREFIX=/tmp/iu4-i5-dp-r2res-test_pre_execution_guards.iXsazk/pycache .venv/bin/python -m unittest tests.live_l1.test_pre_execution_guards
```

### 12.3 Rereview-2 Resolution final combined, broad and compile gates

```text
PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/iu4-i5-dp-r2res-combined.LNeNz6 PYTHONPYCACHEPREFIX=/tmp/iu4-i5-dp-r2res-combined.LNeNz6/pycache .venv/bin/python -m unittest tests.live_l1.test_paper_atomic_coordinator_v2 tests.live_l1.test_paper_iu4_execution_seam_v2 tests.live_l1.test_paper_iu4_adapter_v2 tests.live_l1.test_paper_iu4_adapter tests.live_l1.test_paper_execution_control tests.live_l1.test_paper_atomic_coordinator tests.live_l1.test_paper_iu4_startup_gate tests.live_l1.test_paper_iu4_runtime_gate tests.live_l1.test_paper_iu4_shadow_harness tests.live_l1.test_paper_iu4_shadow_observation_gate tests.live_l1.test_paper_iu4_replay_evidence tests.live_l1.test_paper_iu4_replay_pipeline tests.live_l1.test_paper_economics_shadow_runtime tests.live_l1.test_safe_launch_iu4_shadow_runtime_gate tests.live_l1.test_pre_execution_guards
PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/iu4-i5-dp-r2res-live.Z8Ivy8 PYTHONPYCACHEPREFIX=/tmp/iu4-i5-dp-r2res-live.Z8Ivy8/pycache .venv/bin/python -m unittest discover -s tests/live_l1 -p 'test_*.py'
PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/iu4-i5-dp-r2res-regression.72dvBO PYTHONPYCACHEPREFIX=/tmp/iu4-i5-dp-r2res-regression.72dvBO/pycache .venv/bin/python -m unittest discover -s tests/regression -p 'test_*.py'
PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/iu4-i5-dp-r2res-compile.b66yjb PYTHONPYCACHEPREFIX=/tmp/iu4-i5-dp-r2res-compile.b66yjb/pycache .venv/bin/python -m py_compile live_l1/state/paper_atomic_coordinator.py live_l1/core/paper_iu4_adapter.py tests/live_l1/test_paper_atomic_coordinator_v2.py tests/live_l1/test_paper_iu4_execution_seam_v2.py
git diff --check
git diff --cached --check
```

| Gate | Root | Result | RC | failures/errors/skips |
|---|---|---:|---:|---:|
| all 15 mandatory modules | `/tmp/iu4-i5-dp-r2res-combined.LNeNz6` | 262/262 PASS | 0 | 0/0/0 |
| full `tests/live_l1` | `/tmp/iu4-i5-dp-r2res-live.Z8Ivy8` | 491/491 PASS | 0 | 0/0/0 |
| full `tests/regression` | `/tmp/iu4-i5-dp-r2res-regression.72dvBO` | 170/170 PASS | 0 | 0/0/0 |
| exact four-path compile | `/tmp/iu4-i5-dp-r2res-compile.b66yjb` | PASS, exactly 4 `.pyc` below the named root | 0 | 0/0/0 |
| `git diff --check` | canonical repository | PASS | 0 | 0/0/0 |
| `git diff --cached --check` | canonical repository | PASS | 0 | 0/0/0 |

The four compile products existed only below the named external compile root.
No repository-local bytecode was created.

## 13. Preservation and freeze identities

All 25 mandate Section-5 identities and counts were recomputed after tests.

| Path/artifact | SHA-256 | Mode / lines / entries |
|---|---|---:|
| `live_l1/core/loop.py` | `e4db22642b628fe4b84cf0d2daa9ecd846208138eaa3868a02a56ddf9f75ee6c` | 1,947 |
| `live_l1/core/execution.py` | `85a9acb238dafd3adf5fd8bf57153772d3c7b41559943bdcce5336e3b60dcb5e` | 1,386 |
| freeze directory | n/a | 0555 |
| Preservation tar | `3af14ff2e270d7d3ca09c1279da7d64e6d720630d06a0c5f45b6786237782037` | 0444 / 1,318 entries |
| Freeze manifest | `ad154c0eda13470920878873ed170368cc8f4c43591400a07592a77b179d9e16` | 0444 / 60 lines |
| `live_l1/state/paper_artifacts.py` | `3cd9a459e2856672bb7b318c9cdbf8f8bb52e633ee9529d74761d64928213946` | 1,575 |
| `live_l1/state/loss_cluster.py` | `4ce7d59f64a67de94ffc6f1d03ff4e6c8a7a590802abb003b311cd0d56cc3e55` | 521 |
| `tests/live_l1/test_paper_iu4_adapter_v2.py` | `f71d46700a1966534429281091da32e263ac479ddf1393c5021d015eac1cd1b3` | 1,274 |
| final I3 Evidence | `20846284ffad9e8b755dd6a3b74f963d8d2c6ee1519fafdd0bc1275f2e33c390` | 463 |
| final I4 Evidence | `068c2ba2661031843a13dd3f2c4684f9340f432b90b192b6b7492dae8968270d` | 403 |
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

## 14. No-consumer, no-schema-drift and non-activation closure

Static search found the provenance symbols only in the Coordinator, Adapter and
the two authorized focused tests. No State/S4/Request schema, sidecar, second
journal, cache, launcher or profile contains the new artifact.

No productive `PaperAtomicCoordinatorV2(...)` or `PaperIU4AdapterV2(...)`
construction exists in `live_l1`. The active Loop continues to select literal
`LEGACY`; the private dormant Seam remains test-only. `safe_launch.py` and the
unchanged Runtime Gate still provide no ENFORCED start path. No operational V2
journal root, Exchange, Live, I6, I7 or I8 behavior was added.

The accepted I4 Request V2 canonical fields, Request ID, trusted Context and
validator serialization are unchanged. V1 Atomic/Adapter and OFF/SHADOW behavior
remain green in the adjacent and full suites.

## 15. Rereview-resolution exact closure matrices

### 15.1 Complete schema/canonicality negative matrix

The final Atomic focused test executes every row below through strict
`from_record()` parsing. Every row rejects and leaves State/journal unchanged.

| Field | Executed invalid values |
|---|---|
| `schema_version` | `true`, exact integer subclass of `1`, integer `2` |
| `artifact_type` | uppercase spelling, exact string subclass |
| `transaction_event_id` | empty, leading padding, string subclass |
| `snapshot_id` | empty, trailing padding, string subclass |
| `timestamp_utc` | `+00:00`, fractional second, missing `Z`, malformed text, string subclass |
| `tick_id` | bool, Float, integer subclass, negative integer |
| `intent_id` | empty, trailing padding, string subclass |
| `intent_action` | lowercase, trailing padding, `CLOSE_LONG`, string subclass |
| `state_before_fingerprint` | uppercase, nonhex-64, 63 characters, string subclass |
| `denial_origin` | lowercase, trailing padding, unknown enum, string subclass |
| `denial_reason_code` | alternate Atomic code, trailing padding, string subclass |
| `entry_capability_allowed` | integer, string, lookalike object |
| record shape | missing required field, unknown field |
| fingerprint | valid payload with divergent fingerprint |

The positive record contains exactly twelve payload fields plus
`provenance_fingerprint`, roundtrips exactly and contains no Float.

### 15.2 Origin, capability and State-facts matrix

Accepted tuples:

| Origin | Capability | `state_before.risk.entry_allowed` | Result |
|---|---:|---:|---|
| `STATE_CAPABILITY` | false | false | one PROGRESS |
| `STATE_CAPABILITY` | true | false | one PROGRESS |
| `RUNTIME_GATE_CAPABILITY` | false | true | one PROGRESS |
| `ECONOMICS_AUTHORIZATION` | true | true | one PROGRESS |
| `ATOMIC_ENTRY_GUARD` | true | true | one PROGRESS |

Explicit rejected mismatches:

| Origin | Capability | State entry allowed | Code | Journal/Snapshot |
|---|---:|---:|---|---|
| `STATE_CAPABILITY` | false | true | `PEE_ATOMIC_TRANSACTION_INVALID` | 0 / unchanged |
| `STATE_CAPABILITY` | true | true | `PEE_ATOMIC_TRANSACTION_INVALID` | 0 / unchanged |
| `RUNTIME_GATE_CAPABILITY` | true | true | `PEE_ATOMIC_TRANSACTION_INVALID` | 0 / unchanged |
| `RUNTIME_GATE_CAPABILITY` | false | false | `PEE_ATOMIC_TRANSACTION_INVALID` | 0 / unchanged |
| `ECONOMICS_AUTHORIZATION` | false | true | `PEE_ATOMIC_TRANSACTION_INVALID` | 0 / unchanged |
| `ECONOMICS_AUTHORIZATION` | true | false | `PEE_ATOMIC_TRANSACTION_INVALID` | 0 / unchanged |
| `ATOMIC_ENTRY_GUARD` | false | true | `PEE_ATOMIC_TRANSACTION_INVALID` | 0 / unchanged |
| `ATOMIC_ENTRY_GUARD` | true | false | `PEE_ATOMIC_TRANSACTION_INVALID` | 0 / unchanged |

Both `STATE_CAPABILITY` and `ATOMIC_ENTRY_GUARD` with active positive Loss
pause plus `LOSS_CLUSTER_PAUSE` reject with
`PEE_ATOMIC_TRANSACTION_INVALID`, zero journal and unchanged Snapshot. The
genuine Adapter Loss path remains provenance-free ENTRY_VETO and decrements
exactly once.

### 15.3 Effect/provenance and conflict matrix

Each negative below starts from a fully valid transaction. The test first
rebuilds the complete positive payload and requires exact equality to the
already validated/committed record. It then supplies only one additional
`effect_entry_denial_provenance` argument; every other `_build_transaction()`
argument is the same object/value. This makes provenance the sole invalid
difference.

| Effect | Valid base transaction fingerprint | Valid base journal head | Only added field | Result / persistence |
|---|---|---|---|---|
| OPEN | `7495ff0a4b9e81c5a3da3e7995af41bcf5e46fd317d142599a7f9b0dde83fc55` | `fc03c8ee8d1d6e68b7e5fc15454d0b03f400f75369bbf0e48b9bd784f44c33e2` | valid exact provenance | `PEE_ATOMIC_TRANSACTION_INVALID`; State/journal unchanged |
| CLOSE | `047868fa52421e6a7b579436b4aad0fa43727f6b8c85e1a95e79b18955dc3528` | `c89412f9b423499f0ed1694436026c67a51ff4a41d9d0e898f36c2c102410539` | valid exact provenance | `PEE_ATOMIC_TRANSACTION_INVALID`; State/journal unchanged |
| ENTRY_VETO | `688061fed90e5b1aadb0899839650d3b5f2aa60404040435cb879961a4898b08` | `a102c9ec600b7273082efbdc8d0cf8e99373a348844096e12539326b6097e69f` | valid exact provenance | `PEE_ATOMIC_TRANSACTION_INVALID`; State/journal unchanged |
| KILL | `817c809ee84abd69d5430b065da3511324234ef7ab7c19e7c8cf4c31caee33db` | `e078806fdc80f5a5ef050482e7de38d5c8adca8049978aae0ec95125d57c8bca` | valid exact provenance | `PEE_ATOMIC_TRANSACTION_INVALID`; State/journal unchanged |

The PROGRESS conflict control first builds a valid provenance-bearing PROGRESS
with provenance fingerprint
`40ca90cf8ed01ccef415d8a806f484a061af9ad5ecd687814dc63560dcc32c31`,
transaction fingerprint
`cbe4d12e54fabcda14ea20842d770af97c090e93e1aeda0d68b2e1cb3e888dc4`
and journal head
`656858783d34558030a17d429ff528d9fb79225609ef7d98f24aaafa0ce508f7`.
Adding only a valid matching `AcceptedEntryEventV1` rejects as
`PEE_ATOMIC_TRANSACTION_INVALID` with zero journal and unchanged Snapshot.

The remaining conflict rows are:

| Combination | Result |
|---|---|
| PROGRESS with valid exact provenance | accepted once |
| same Event and same provenance | exact replay |
| same Event with divergent provenance | `PEE_IU4_PROGRESS_CONFLICT` |
| explicit transaction JSON null | rejected |

The refingerprinted tamper test changes a valid Runtime-Gate provenance to
`STATE_CAPABILITY`, recomputes the provenance fingerprint, recomputes the
journal head, reheads State/S4 and recomputes the transaction fingerprint.
Both direct transaction construction and journal recovery reject the resulting
self-consistent but semantically false chain with
`PEE_ATOMIC_TRANSACTION_INVALID`; the journal remains one entry and Snapshot
sequence remains one.

### 15.4 Fixed None-provenance Golden matrix

The `record_sha256` column hashes the exact canonical serialized transaction
record, including `transaction_fingerprint`. All five records omit the
provenance key.

| Effect | record_sha256 | transaction_fingerprint | journal_head |
|---|---|---|---|
| PROGRESS | `94417f540e9026241afef81ad5de318cc5c91c420575b54721474d2fdadf4e53` | `a2b2f1a303abca1512916274307e431af56aaccfc12f1d266324753ae349dfe5` | `7661715d187ed9067dc226e075f6b5b199e6a81d57cb1ad0d1834d94c9272433` |
| OPEN | `8d53c1aa950e0b440c675f6e33cdc272d78927639cf5df92a2f6233318ee5dd2` | `73cf8b8c806d877a8c39c81fe34316534e60df866dbfc6b8ce01c75b9aa1dade` | `da577fd17171d9d9796f8e0338534d126088a1c7e75c7643dc0e2587ce8b9df7` |
| CLOSE | `dc753fcdb17c303d5d4a320de5130ec98db0988ec84ca20d4d7234d008fe5f38` | `1cb4ddce86640de8ecac693510e22d5deda4555474794a937b3212db80aa3ce4` | `58eaf1c6078d79e1156262277461bbf6532221d561410f0cc351d814b8feb4ee` |
| ENTRY_VETO | `49cfeb3f0be1a8f974006c2f7aa23755a03e3cb65f461adee6bd6d0184446e28` | `55d71149582a095dc510bf917616d59f8ecdead1bded7948b0d4bf7621e4912e` | `846c4d4c26e7df2c79d2ee5f28b83e7c02bd49bed6d3e865bab200b4be3f51a8` |
| KILL | `90399c9479fff6a95bbfc5b32be99859db7a5a99691c23af81cbee7691f24ea0` | `a22f4ac2ee3bae7a60337c6a6d7b0ab6cac3234e6d53f2d7e9894da354ff68ba` | `7855847232d3895babd7db346de32a279e0248b6650f0975492a7b2eba12c4f8` |

### 15.5 Seven row-complete provenance fault/readback results

Snapshot values below are recorded immediately after the injected boundary;
the value after `->` is the controlled retry/recovery/readback result.

| Row | Boundary / result | Journal | Snapshot sequence | Snapshot head |
|---:|---|---:|---:|---|
| 1 | before accepted validation / `PEE_IU4_RUNTIME_BINDING_MISMATCH` | 0 | 0 | `EMPTY` |
| 2 | after validation, before Coordinator / `AFTER_VALIDATION_BEFORE_COORDINATOR` | 0 | 0 | `EMPTY` |
| 3 | `BEFORE_JOURNAL` / exact interruption -> controlled commit -> replay | 0 -> 1 | 0 -> 1 | `EMPTY` -> `6c3cbec98d88f9d2c645b64b52c0e85b938f9b5b6ca0ce009f621ddaba47479e` |
| 4 | `AFTER_JOURNAL` / exact interruption -> recovery -> replay | 1 | 0 -> 1 | `EMPTY` -> `c62a803e585c252838eed750b8fe374f6cc034a011ba88f6885747823f7911d8` |
| 5 | `BEFORE_SNAPSHOT` / exact interruption -> recovery -> replay | 1 | 0 -> 1 | `EMPTY` -> `edd3911174381d6f67fa282c0af9fd45483343cc36443b9dc9b1bf0d860665b6` |
| 6 | `AFTER_SNAPSHOT` / exact interruption -> readback -> replay | 1 | 1 | `527b2e0fe266a2dafc5bbf150e8fb031c0e00875ee6e5bae6df07a3a6db1b6a3` |
| 7 | identical public Adapter readback / `PEE_IU4_ENTRY_BLOCKED` | 1 | 1 | `781232c1ec4d43a32047dfbe4b50e69f77931ca22b5f59f936ea51f84ffb4870` |

| Row | Provenance record SHA / provenance fingerprint | Transaction fingerprint / journal head | Cursor fingerprint after boundary -> final |
|---:|---|---|---|
| 1 | `NONE` / `NONE` | `NONE` / `EMPTY` | `ca18a20949d5e16c3d24c24e205e9ec72113d5bc2a176ee9120f5ccfaba51301` |
| 2 | `45a7822a086baf13553869af1f361f895e5281ad6dc577e1a4899cdb864475fb` / `dba10c8b4862de8c8dae1ce45ba79269415abca7eaed2a3955846a1990b9c1bc` | `NONE` / `EMPTY` | `ca18a20949d5e16c3d24c24e205e9ec72113d5bc2a176ee9120f5ccfaba51301` |
| 3 | `ea9ebc3b0b33e6f029a5baaf22dfbd23e49e6a06957e722b8cb2fd26e9adacf2` / `9d7ea242be30db70e12bacfb9642276a0b5f1ef9928039e5265b569f1d59bcf3` | `66f466e92b0ea32ec5e442420dccb74a8ecf458c824d29578ff627754fc80444` / `6c3cbec98d88f9d2c645b64b52c0e85b938f9b5b6ca0ce009f621ddaba47479e` | `ca18a20949d5e16c3d24c24e205e9ec72113d5bc2a176ee9120f5ccfaba51301` -> `c1acbb91d46e81bce7b644568ed4b7302c040ff78fa19f28cacd263a21150d6c` |
| 4 | `25f94c03ddb618185ce8587a12958b9955bc67e935a5a8df1f30afcd01584b23` / `971d951f999f7d4f9f8b13e6934ccbe56c7d45bd9918a8f2d5adda7c81dd7a2a` | `de36dd50ea8f8841c05939d3e99e7391fe3f081b819323f404bb778bdbb206dc` / `c62a803e585c252838eed750b8fe374f6cc034a011ba88f6885747823f7911d8` | `ca18a20949d5e16c3d24c24e205e9ec72113d5bc2a176ee9120f5ccfaba51301` -> `9d50c568faf041f365a7ab3927af68aa0c60eff74021278790a2e05d212be039` |
| 5 | `0597043acd6e581204a7cc2ca8a26271981176cbd6ca1b3ce2eff3e7f368c32c` / `8edac178864ec6cb0119c986794f9dce144e8dc3af3a7ddb910cc034e8ec68c8` | `486e2d2e4cff43c5718349b154c024f5b1ca48553921c5c7c0f29702884bc497` / `edd3911174381d6f67fa282c0af9fd45483343cc36443b9dc9b1bf0d860665b6` | `ca18a20949d5e16c3d24c24e205e9ec72113d5bc2a176ee9120f5ccfaba51301` -> `9741e87d2ffd0151eb17146be4b8ad86e9e27bc429c185d56d49d4be3eb8f54c` |
| 6 | `671bcb92a77d362f8a67b4c857914d7eb594931c3de7237c33cab330dc2e2b58` / `0ee5589f20008949fd8d789dd9b24ec8eaf693717d05881a659eaf2d7a658a43` | `065b3d737556d45acad18661b5cf6cf3a5ad1ae17c948d153694a98e7f45e324` / `527b2e0fe266a2dafc5bbf150e8fb031c0e00875ee6e5bae6df07a3a6db1b6a3` | `1cdb0e27fc00085b76d0ee99bccf45c2adba6636eba358319536cd8cd047c978` |
| 7 | `45a7822a086baf13553869af1f361f895e5281ad6dc577e1a4899cdb864475fb` / `dba10c8b4862de8c8dae1ce45ba79269415abca7eaed2a3955846a1990b9c1bc` | `38650011615a99f4ec2bb2318ec10fd6c1c1ca7b91087744efc88b8414429e45` / `781232c1ec4d43a32047dfbe4b50e69f77931ca22b5f59f936ea51f84ffb4870` | `283f7705dfcbc314dadf6696c23ad626c86ce4b43fd34d65d55fe50bdf740b63` |

| Rows | Position / Account / Throttle / Loss fingerprints | Risk-business fingerprint | Retry/replay and decision-sentinel counts |
|---|---|---|---|
| 1-2 | `384e3e72...cd0d1` / `62eb8023...7d4be` / `3133b887...6d33` / `9c31752d...aa56` | `55951e2ac4696c7048ec9775ca4412f52389a95772c800add3571a8cceb3d272` | row 1 pre-accept, no replay, `effect/provenance/economics/guard/risk=0/0/0/0/0`; row 2 controlled first commit follows, `0/1/0/0/0` |
| 3-6 | same exact four full fingerprints | `ad40409763566d0f5778126a6c55937e1353127f7dbb20d1315a5a6aa2344c6c` excluding Cursor | each ends `already_committed=true`, `newly_committed=false`, journal 1; `risk/guard=0/0` per row |
| 7 | same exact four full fingerprints | `7425f8cea0e7f396162e0e910893e00d39bab6e5e6fbf87df9ef7c5dcfb6f75e` excluding Cursor | `already_committed=true`, `newly_committed=false`; `effect/provenance/validator/economics/guard/risk=0/0/0/0/0/0` |

The full common component fingerprints are Position
`384e3e72e0c128306e46fda760ab3c27267713cfc7667826bd6255944fdcd0d1`,
Account `62eb8023ce10639f2e15055e63e15a67b0205efbc8bf373e3cc1ea4f49a7d4be`,
Throttle `3133b887d9d24b66103f56852fb672a1b7fbebfee252d1292d2d322325d56d33`
and Loss `9c31752d64d9c7063d4dd93c35801fee8d6da152b7a30731130487979b53aa56`.

### 15.6 Actual per-denial first-commit/replay identities

| Family | Request ID | provenance_fp | transaction_fp | journal_head | cursor_fp |
|---|---|---|---|---|---|
| State | `PEE-IU4-V2-3452ea437c360a4a740821db0339804b0f92e2155324e3c312f33489edf82826` | `84f69b8c44b03c3630cabfafcf9fce15dfaf2ff44323780487abfa1a7db5366d` | `e8a6287999ab29ec9362d6b2900d4e3e76e90ef06da0672ebee5ee8b0800efda` | `bda1b6b33425d7aa4c3721f0c5e4e3ac8a53e1624727c340ea194992e5a93038` | `9ca042a819077f333097450f249026a7ff283ce9a64a070a72d338e638e8ac0a` |
| Runtime Gate | `PEE-IU4-V2-425314b35d6ed2b3d7698258c353acd519c17403b028eefb9853ee2ae0e529d2` | `a14bbb8052339fee578a4c1c783286d29a7c351beeddfdf6fcf3c875a6a53f16` | `4d3f40e56e0a714e6a87bc6f8cd02baf717201c8c039c474916cf95a8cc46c7b` | `104af4b6962822a1236b853676f712623a4528b0727e8dcff3f80ebd925cd782` | `45c27655394bffea319cd5196ce586f292de28b76c61e3a50b849ef3262f5224` |
| Economics | `PEE-IU4-V2-98c7095899f5951c58f29db4af5859408108ffcf63bad4b37ba19f784740b3ca` | `b8029a2c1f9bcdae0ffeabc21d27a25075f0b0b5b74f045a9ffaf27765187922` | `cf67214b307d8322477954ce4681c7dbf0882237585a60cd303b0c23d8eec5c7` | `405a9ce0f0d376d59e3ffe0bb499398381f6509048c9f0705f87f403e3690c48` | `224e40a3f3ec75eee826fef2b2436749991b7e6fffa6f28f016d1f219e034af1` |
| Account guard | `PEE-IU4-V2-2705684ea7650f6ff8b815423f2e1447ce20d1404f4e21e7488acedda97e66b9` | `b326318688cceb85808a6c1807a12742aec4658aa0a4c4e781da7e66c7715915` | `1e6d213a693e8ba9067bad73c27f6d2d2348a34ee5523e98075edb726df202e2` | `13240c209dcaaece54df3716fe49444cb0f2adafeb559b9f6f7979f1ec226af9` | `df90da551a2bfe672e52ec1e4af7e6c3116a67df3b75cc411c636030088436ad` |
| Throttle guard | `PEE-IU4-V2-6618bd297b06aa4f525ed804548835e138c7207556c6ab540605369c6d22d24e` | `bb858ae049cb9a740c52138847d8e0a8739f78061b9f79545fba97ea5010bdf9` | `6e09c8bb745d63473bc0666349e33fa14f2a801bdf810c8ba0e33de97256c58b` | `f757eaba1867d73d95814398ca8d865df22b59bc07a4e0a4991528d5c0daf5de` | `e6c3b289d736f17576e13d0b8719d6d138ccbab1f75230675010e327538cc760` |

Every first call returned `REJECTED/PROGRESS`, sequence 1, one journal and one
Cursor. Every identical replay returned the same State with
`already_committed=true`. Adapter `_effect`, accepted validator, Economics,
Atomic OPEN guard and Risk derivation sentinel counts were exactly
`0/0/0/0/0`; the exact readback row additionally proved provenance-builder
count zero. Opposite capability replay rejected with
`PEE_IU4_ADAPTER_REQUEST_CONFLICT` and no second transaction.

### 15.7 Stable multi-failure precedence

| Simultaneous faults | First code |
|---|---|
| unsupported schema plus wrong fingerprint | `PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED` |
| unknown Origin plus wrong fingerprint | `PEE_ATOMIC_TRANSACTION_INVALID` |
| canonical payload plus wrong fingerprint | `PEE_ATOMIC_JOURNAL_CONFLICT` |
| valid artifact plus false Origin/State facts | `PEE_ATOMIC_TRANSACTION_INVALID` |
| same Event plus divergent durable provenance | `PEE_IU4_PROGRESS_CONFLICT` |
| Adapter replay plus divergent capability | `PEE_IU4_ADAPTER_REQUEST_CONFLICT` |

All precedence rows assert zero additional journal and zero Snapshot mutation.

## 16. Final boundary and next step

```text
I5_RESULT:PASS
I5_CORRECTIVE_IMPLEMENTATION_COMPLETE:YES
I5_INDEPENDENT_ACCEPTANCE:PENDING
OPERATIONAL_ENFORCED_START_AUTHORIZED:NO
ACTIVE_V2_CONSUMER_AUTHORIZED:NO
I6_THROUGH_I8_AUTHORIZED:NO
ENFORCED_ACTIVATION_AUTHORIZED:NO
NEXT_REQUIRED_STEP:IU4-I5-ACTIVE-EXECUTION-SEAM-DURABLE-DENIAL-PROVENANCE-IMPLEMENTATION-INDEPENDENT-READONLY-FILE-EXACT-REREVIEW-3
```

Only the fresh independent read-only file-exact rereview named above may
follow. This
PASS claim is implementation-side Evidence, not independent acceptance and not
activation authority.
