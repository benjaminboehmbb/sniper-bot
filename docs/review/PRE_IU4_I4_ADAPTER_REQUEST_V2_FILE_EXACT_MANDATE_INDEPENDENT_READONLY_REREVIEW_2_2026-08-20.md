# Pre-IU4 I4 Adapter Request V2 File-Exact Mandate — Independent Read-Only Rereview 2 — 2026-08-20

## 1. Decision

This record is the fresh independent, strictly read-only rereview of the
corrected I4 File-Exact Mandate and its mandate-side Resolution.

```text
WORKSTREAM:IU4-I4-ADAPTER-REQUEST-V2-FILE-EXACT-MANDATE-INDEPENDENT-READONLY-REREVIEW-2
MANDATE_REREVIEW_RESULT:READY
MANDATE_REVISION:2
BLOCKER:0
HIGH:0
MEDIUM:0
LOW:0
I3_INDEPENDENT_ACCEPTANCE_PRESERVED:READY
I4_IMPLEMENTATION_ENTERED:NO
I4_IMPLEMENTATION_AUTHORIZED_AFTER_REVIEW:YES_WITHIN_EXACT_THREE_PATH_SCOPE
I5_THROUGH_I8_AUTHORIZED:NO
ACTIVE_V2_CONSUMER_AUTHORIZED:NO
ATOMIC_V2_COMMIT_FROM_ADAPTER_AUTHORIZED:NO
ENFORCED_ACTIVATION_AUTHORIZED:NO
```

The corrected mandate closes every finding from the first independent
rereview. It is usable only for a separately invoked I4 implementation and
only within its exact three-path boundary. This decision does not implement
I4 and does not authorize I5, an active consumer or activation.

## 2. Independence and read-only method

The independent reviewer:

- worked only in `/home/benja/projects/sniper-bot`;
- read `AGENTS.md` completely before review work;
- recomputed identities, line counts, modes and archive entry counts;
- checked Revision 2 directly against Revision 21, I3 READY rereview 6, the
  prior I4 `NOT_READY` record and the Resolution;
- adversarially reconsidered all four prior findings rather than trusting the
  Resolution's closure claims;
- ran all mandate-time baselines with `PYTHONDONTWRITEBYTECODE=1`, isolated
  cache and temporary roots under `/tmp`;
- performed no source, test, mandate, Resolution, Git or cleanup mutation;
- did not read, execute or modify the expressly excluded RCC002 bundle script;
  and
- left all foreign tracked and untracked artifacts untouched.

Creation of this record is the sole post-verdict governance write.

## 3. Controlling identities

```text
CANONICAL_REPOSITORY:/home/benja/projects/sniper-bot
BRANCH:main
HEAD:c7ce0452aa2ccbf08c462784d68fa07b3dfe9595
MAIN:c7ce0452aa2ccbf08c462784d68fa07b3dfe9595
ORIGIN_MAIN:89e13fecd1ab549ca7099818b1c9ad4984cb6f7a
MAIN_AHEAD_OF_ORIGIN:6
MAIN_BEHIND_ORIGIN:0
```

| Artifact | Recomputed SHA-256 | Lines | Result |
|---|---|---:|---|
| Revision-21 specification | `ab8f80720a1d8fe49b9085bce63658bcaecf7f0a3ea70fb555559223090824e0` | 4,605 | controlling |
| final I2 independent rereview | `5a59ad8c97ebae85148661fe0e3bedab643c7f12ae2c8d4e87272447c0616679` | 300 | `READY`, 97/97 |
| I3 file-exact mandate | `775aeb62e6ff0a1ca3af970970053b43d176f1122560774f184ecf40a8fcced5` | 558 | authorized |
| final I3 Evidence | `20846284ffad9e8b755dd6a3b74f963d8d2c6ee1519fafdd0bc1275f2e33c390` | 463 | accepted |
| final independent I3 rereview 6 | `03790420534e38c7e36d1824a472dfd80763340dacec8847ddf5072d55db0c9f` | 191 | `READY`, 0/0/0/0 |
| prior I4 mandate | `12d5569f17f2d3eb024aafc9ace49d1c5d594b5a28a2fc991e0fac54b3297d5c` | 462 | superseded candidate |
| first independent I4 mandate rereview | `5c67fb30008005e4e0b02e179c300d7ab1603ee36c1ef625e136e9e8140b8263` | 295 | `NOT_READY`, 2/2/0/0 |
| corrected I4 mandate Revision 2 | `e4039400d24781c9d1911b7b7448e49773d92e7134f8ecee1042cdf47438c3f1` | 601 | `READY` by this rereview |
| mandate rereview Resolution | `bdee1e49f92de0b4b14438e3aade37db50108a4987043d50c2b617f133543d89` | 234 | complete |

## 4. Exact later implementation scope

The accepted mandate authorizes exactly these three later paths:

| Operation | Path | Mandate-time identity |
|---|---|---|
| MODIFY | `live_l1/core/paper_iu4_adapter.py` | `d65525f31746d1edf30bf1ffc7f84a845f97b3f4120904c9910b741bc8c76a7b`, 641 lines |
| CREATE | `tests/live_l1/test_paper_iu4_adapter_v2.py` | independently confirmed absent |
| CREATE | `docs/review/PRE_IU4_I4_ADAPTER_REQUEST_V2_IMPLEMENTATION_EVIDENCE_2026-08-20.md` | independently confirmed absent |

Exactly one existing production file is released additively. The trusted
context, Request V2, strict helpers, stable V2 reason codes and pure validator
are implementable in that Adapter module. One focused test can cover all
required matrices, and one Evidence record can carry the completion proof.
No fourth source, test, fixture, sidecar or governance path is needed.

The I4 ceiling is correct: phase I4 defines only an in-memory, synthetic,
no-commit validation boundary. Phase I5 remains the sole future owner of
active context construction, Snapshot acceptance, execution-seam delegation
and Atomic-V2 commit mapping. No V2 implementation or active consumer exists
at review time.

## 5. Prior-finding closure

### 5.1 `I4-MR-B1` — Event, Intent and price provenance — CLOSED

Mandate lines 254-284 define exactly one frozen, non-persisted, eight-field
`IU4AdapterTrustedControlContextV1`. Lines 286-311 require exact equality of
Request Source ID, final Intent, Intent Reason, Timestamp, Tick, Snapshot and
canonical reference-price text against that trusted context. Lines 423-436
state explicitly that content addressing alone is not provenance.

The focused matrix at lines 472-474 requires each trusted field to diverge
independently under a freshly correct Request ID and still be rejected with
zero mutation. This closes the self-authentication defect and satisfies
Revision-21 lines 2965-2987 for synthetic I4 validation.

### 5.2 `I4-MR-B2` — Pure-Control Action/Reason authority — CLOSED

Mandate lines 273-284 require an exact `PaperExecutionControlDecision` object,
reject subclasses and lookalikes, and prohibit Adapter recomputation or
duplication of Pure Control. Lines 294-311 require Request Action and Reason
to equal the trusted Decision before independent State-matrix validation.

Lines 346-351 retain a second fail-closed position/intent/action/reason check,
so a trusted Decision cannot authorize an impossible transition. Lines
475-476 mandate fake TP/SL/Time-stop, wrong-priority and genuine autonomous
HOLD cases with correctly refingerprinted Requests. No synthetic opposing
Intent is required or permitted.

### 5.3 `I4-MR-H1` — Loss-specific NOOP predicate — CLOSED

Mandate lines 367-378 require cumulatively:

- FLAT plus BUY/SELL and the same trusted Decision;
- `state.risk.entry_allowed is False`;
- `state.loss_cluster.pause_entries_remaining > 0`; and
- bound S4 reason `LOSS_CLUSTER_PAUSE`.

Clean entry-allowed and Account-/Throttle-/SOFT-/other non-Loss-only blocked
States are explicit negative cases. HARD and EMERGENCY reject every Tick
Request. The focused matrix at lines 477-478 makes these outcomes mandatory.

### 5.4 `I4-MR-H2` — stable failure mapping — CLOSED

Mandate lines 390-421 fix every precise or Revision-21-family reason code and
the full deterministic precedence:

1. constructor/schema/canonicality and Request-ID conflict;
2. validator boundary types;
3. trusted comparisons in written Section-8 order;
4. HARD/EMERGENCY capability;
5. written State/action predicates; and
6. otherwise-valid OPEN entry capability.

The focused test matrix and Evidence gate require each code, precedence pair
and zero-mutation result. V1 error behavior remains unchanged.

## 6. Adversarial new-gap review

The following plausible ambiguity classes were independently challenged and
did not produce a finding:

- Constructor versus validator classification is fully ordered and
  implementable without fallback.
- Trusted Event and Decision share one frozen context; proof that I5 creates
  both from the same accepted input correctly remains an I5 active-seam duty,
  not an omitted I4 mutation.
- `PaperExecutionControlDecision` is imported from the accepted I1 authority;
  the Adapter neither invokes nor reimplements control policy.
- Terminal binding occurs after trusted identity checks but before the State
  action matrix. HARD/EMERGENCY reject all Tick Requests; SOFT permits only a
  trusted, capability-valid CLOSE and blocks OPEN.
- SOFT cannot fabricate `LOSS_CLUSTER_GATE_BLOCKED_ENTRY`; the Loss predicate
  is independently bound to Atomic Loss and S4.
- The trusted context remains deliberately non-persisted and therefore does
  not change the exact 25-field persisted Request contract.
- A separately trusted Authorization ID is sufficient at I4 because I2 owns
  Authorization parsing, expiry and consumption; I4 compares the exact ID.
- The additive Adapter import of the existing Decision type requires no
  modification to Pure Control, Atomic V2, Gate, Loop, Execution or Shadow.

## 7. Fresh independent verification

Every Python command used `PYTHONDONTWRITEBYTECODE=1`, an isolated
`PYTHONPYCACHEPREFIX` and a test-owned `/tmp` root.

| Check | Result | RC | failures/errors/skips | Independent root |
|---|---:|---:|---:|---|
| combined six-module baseline | 120/120 PASS | 0 | 0/0/0 | `/tmp/iu4-i4-mandate-rereview2-base120.guTsP9` |
| complete `tests/live_l1` | 419/419 PASS | 0 | 0/0/0 | `/tmp/iu4-i4-mandate-rereview2-live419.3Ko1QV` |
| complete `tests/regression` | 170/170 PASS | 0 | 0/0/0 | `/tmp/iu4-i4-mandate-rereview2-reg170.J6IJ9z` |
| Adapter-only `py_compile` | PASS; exactly one `.pyc` under `/tmp` | 0 | n/a | `/tmp/iu4-i4-mandate-rereview2-compile.51YTN6/pycache` |
| `git diff --check` | PASS | 0 | n/a | canonical repository |

The later two-path compile is intentionally unavailable because the mandated
focused V2 test has not yet been created. No test was skipped or replaced.

## 8. Preservation verification

| Path | Recomputed SHA-256 | Lines |
|---|---|---:|
| `tests/live_l1/test_paper_iu4_adapter.py` | `b4947e4c03fa3b187e01c4005062337d1837b70d652243030581172dd4d2c339` | 441 |
| `live_l1/core/paper_iu4_shadow_observation_gate.py` | `ed4e75fad664c68b91950e9c09e873823ebe3eb0b0062f85806daa09ce661350` | 886 |
| `live_l1/core/paper_iu4_shadow_harness.py` | `ddfb60f19a3b765a476c8de0464d583590313cdd0583391044cb338fec969f77` | 1,007 |
| `live_l1/tools/paper_iu4_replay_evidence.py` | `707592bdb5c6fe12ff01c8254da1f16ee5c25a049c61caef60077064ff77c000` | 849 |
| `tests/live_l1/test_paper_iu4_shadow_harness.py` | `abea98dcecf65ff741fbe9951c5986d415085051b3dd27d6750553b475f6f3a5` | 747 |
| `tests/live_l1/test_paper_iu4_replay_evidence.py` | `d5a8580f44edac6997281bcc5aa3d3ea79bd1c7e5f07f24602b029cd2cf363e2` | 488 |
| `tests/live_l1/test_paper_iu4_replay_pipeline.py` | `7f89b7ff37ad603edcfe4cf9dd5d9f12ad8270b0725708b5619854f97e4a93f9` | 316 |
| `live_l1/core/paper_execution_control.py` | `7d3cb901c1c67c8df85e99bc579fda85d8732b634ff4747e08620b92ac1e44f7` | 257 |
| `tests/live_l1/test_paper_execution_control.py` | `0ae44f2d32f5f3b6affe37a258be0e6aee06790f857e4fc01628c6795bda99e5` | 843 |
| `live_l1/core/paper_iu4_startup_gate.py` | `c4a1854f3b200525568a40205b39e9ce2e14c342bb860569ba7fcfe5e9c063cd` | 919 |
| `live_l1/core/paper_iu4_runtime_gate.py` | `447573e484bc13023a118ae61bf7615657293be629c30729748e64f0af7af7c5` | 201 |
| `live_l1/core/loop.py` | `54e9e7bc0977a9c94f2e85a3279157678249a8569cff63f7d4f29131443fd058` | 1,411 |
| `live_l1/core/execution.py` | `5aed85ce2754dbb4d8984a1d699b607e3a522ed6da000df119ecd782a4e764d8` | 1,147 |
| `live_l1/core/paper_economics.py` | `a302013134d1265ac85ad10b57a67ead9e2343043f7eb499fd965a44312525ae` | 730 |
| `live_l1/core/paper_entry_throttle.py` | `ad5447d88a2c35c9a71a5495c61c8f08fa844daf60e79d4a872234e88037df75` | 727 |
| `live_l1/state/paper_atomic_coordinator.py` | `d0721ae5def3551ba7281ea0e367f5347890fd4cd7187d8f2aebb98d2651e84f` | 5,489 |
| `live_l1/state/paper_artifacts.py` | `3cd9a459e2856672bb7b318c9cdbf8f8bb52e633ee9529d74761d64928213946` | 1,575 |
| `live_l1/state/loss_cluster.py` | `4ce7d59f64a67de94ffc6f1d03ff4e6c8a7a590802abb003b311cd0d56cc3e55` | 521 |
| `tests/live_l1/test_paper_atomic_coordinator_v2.py` | `16d0fea6e5588cc14329ba61cfeeccb1f72478d14c358f8ed4e38c1ac3a41bb9` | 2,482 |

Freeze verification:

```text
I2_PRESERVATION_TAR_SHA256:3af14ff2e270d7d3ca09c1279da7d64e6d720630d06a0c5f45b6786237782037
I2_PRESERVATION_TAR_MODE:0444
I2_PRESERVATION_TAR_ENTRIES:1318
I2_FREEZE_MANIFEST_SHA256:ad154c0eda13470920878873ed170368cc8f4c43591400a07592a77b179d9e16
I2_FREEZE_MANIFEST_MODE:0444
I2_FREEZE_MANIFEST_LINES:60
I2_FREEZE_DIRECTORY_MODE:0555
```

All accepted I3 source, test, Evidence and rereview identities remain exact.

## 9. Final authorization and next step

```text
MANDATE_REREVIEW_RESULT:READY
MANDATE_REVISION:2
BLOCKER:0
HIGH:0
MEDIUM:0
LOW:0
I4_IMPLEMENTATION_ENTERED:NO
I4_IMPLEMENTATION_AUTHORIZED_AFTER_REVIEW:YES_WITHIN_EXACT_THREE_PATH_SCOPE
I5_AUTHORIZED:NO
ACTIVE_V2_CONSUMER_AUTHORIZED:NO
ENFORCED_ACTIVATION_AUTHORIZED:NO
NEXT_PERMITTED_STEP:IU4-I4-ADAPTER-REQUEST-V2-IMPLEMENTATION
```

The next workstream may implement I4 only in the exact three paths named in
Section 4 and must satisfy the complete focused/Evidence matrices in corrected
Mandate Revision 2. I5, an active consumer, Adapter-to-Atomic commit and
ENFORCED activation remain unauthorized.
