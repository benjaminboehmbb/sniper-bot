# Pre-IU4 I5 Active Execution Seam — Implementation Independent Read-only File-Exact Rereview 3 — 2026-08-20

## 1. Verdict

```text
WORKSTREAM:IU4-I5-ACTIVE-EXECUTION-SEAM-IMPLEMENTATION-INDEPENDENT-READONLY-FILE-EXACT-REREVIEW-3
I5_IMPLEMENTATION_REREVIEW_3_RESULT:NOT_READY
I5_INDEPENDENT_ACCEPTANCE:NOT_READY
BLOCKER:2
HIGH:0
MEDIUM:0
LOW:1
OPERATIONAL_ENFORCED_START_AUTHORIZED:NO
ENFORCED_ACTIVATION_AUTHORIZED:NO
I6_THROUGH_I8_AUTHORIZED:NO
EXCHANGE_AUTHORIZED:NO
LIVE_AUTHORIZED:NO
```

The review was performed independently and strictly read-only in the
canonical repository `/home/benja/projects/sniper-bot`. `AGENTS.md` was read
completely first. The excluded `scripts/build_rcc002_spec_bundle.py` was not
read, executed or modified. No repository, Git, cleanup or foreign-artifact
mutation was performed.

## 2. Repository and controlling chain

```text
BRANCH:main
HEAD:c7ce0452aa2ccbf08c462784d68fa07b3dfe9595
MAIN:c7ce0452aa2ccbf08c462784d68fa07b3dfe9595
ORIGIN_MAIN:89e13fecd1ab549ca7099818b1c9ad4984cb6f7a
MAIN_BEHIND_ORIGIN:0
MAIN_AHEAD_OF_ORIGIN:6
GIT_DIFF_CHECK:PASS
GIT_CACHED_DIFF_CHECK:PASS
```

| Artifact | SHA-256 | Lines | Status |
|---|---|---:|---|
| Revision 21 | `ab8f80720a1d8fe49b9085bce63658bcaecf7f0a3ea70fb555559223090824e0` | 4,605 | controlling |
| final I4 rereview 3 | `c6d8bbcb35572a364b74a47eb9ad817240a8b0cce70e514942bb674d3861c38b` | 191 | READY |
| I5 mandate | `124de947c7eebaaeffa37fb802c0bf3194b1595107628cd655bab8b833522060` | 562 | authorized |
| I5 mandate rereview 2 | `3d02b2f5791218643e7d76805701e88fbed5c121a884944a9242b31357740922` | 212 | READY |
| I5 implementation rereview 1 | `7ddd108a659a37e264b5cfb78172cd00d5d426105455b864b358756aaad57980` | 262 | NOT_READY |
| Resolution 1 | `0661aaa5193f790976ae96256cca4dc74b3c99d4533369587203dc18d76e22ff` | 233 | candidate correction |
| I5 implementation rereview 2 | `eb5886b59c09cfd3f7b797453642c40f0943666b3d9f9df7d8b45e7077bf940a` | 213 | NOT_READY |
| Resolution 2 | `4a11786ef353b84ad9384da3fd35fcb1857fc323d9f1fb963e7155dd4da0766e` | 224 | candidate correction |
| I5 Evidence | `ad303dc6b763ddf33a38ab45e9be0a728a72b5c6fa96bae175b4f24e9920a7b5` | 452 | reviewed candidate |

## 3. Exact five-path candidate

| Operation | Path | Current identity |
|---|---|---|
| MODIFY | `live_l1/core/loop.py` | `d21a422040926d86d04222168b31c780ce20a516d058e8e16ddd9c728258050b`, 1,915 |
| MODIFY | `live_l1/core/execution.py` | `85a9acb238dafd3adf5fd8bf57153772d3c7b41559943bdcce5336e3b60dcb5e`, 1,386 |
| MODIFY | `live_l1/core/paper_iu4_adapter.py` | `23442e6d943d1bde9d9b6a928d23525a4ca020a528f2a072e11d9da2df618e92`, 1,694 |
| CREATE | `tests/live_l1/test_paper_iu4_execution_seam_v2.py` | `84ce25522d868b8c998f0fbebc22ca32a82d19448d9d61efdd36a57c1a4435cf`, 1,904 |
| CREATE/REPLACE | I5 Evidence | `ad303dc6b763ddf33a38ab45e9be0a728a72b5c6fa96bae175b4f24e9920a7b5`, 452 |

Both CREATE paths are absent in `HEAD`; `git cat-file -e` returned RC 128 for
each. No sixth I5 implementation path was found. This rereview record is a
separate governance artifact and did not mutate the candidate.

## 4. Findings

### I5-IR3-B1 — BLOCKER — durable non-Loss PROGRESS replay redecides

Mandate lines 318–319 require an identical identity/payload replay to be
idempotent without redecision. Lines 366–376 require exactly one PROGRESS for
accepted Account, Throttle, SOFT and other non-Loss entry denials so a restart
cannot process them again. Line 530 makes durable redecision a stop condition.

The reviewed Adapter recognizes an existing transaction and calls
`_replay_existing()` (`paper_iu4_adapter.py:1066-1075`). That helper validates
the Request again against `transaction.state_before` (`:931-936`). For a SOFT
or other `risk.entry_allowed=false` state, this fresh business validation
raises `PEE_IU4_ENTRY_BLOCKED`. It also recalculates the effect from Request
and current Gate capability (`:937-943`); a state-denied durable PROGRESS with
`entry_capability_allowed=true` is thereby reconsidered as OPEN.

Independent reproducer:

```text
ROOT:/tmp/iu4_i5_impl_rr3_nonloss_replay.5n72XD
FIRST_STATUS:REJECTED
FIRST_EFFECT:PROGRESS
FIRST_SEQUENCE:1
SECOND_RESULT:PaperIU4AdapterError
SECOND_REASON:PEE_IU4_ENTRY_BLOCKED
RC:0
```

The existing non-Loss and SOFT tests cover the first commit only. Evidence
lines 185–189 and 283–284 overstate durable replay/no-redecision coverage.

Required correction:

1. Validate durable effect and Request/transaction binding without treating
   the already-decided business denial as a new entry decision.
2. Return a durable `REJECTED/PROGRESS` exactly as committed.
3. Continue to reject divergent Gate capability, Request binding, escalation
   or durable effect payload.
4. Add replay tests for SOFT, Account, Throttle/other non-Loss denial and Gate
   entry false: one transaction, one Cursor, no added business mutation and no
   redecision.
5. Correct Evidence.

### I5-IR3-B2 — BLOCKER — operational Shadow facade accepts lookalikes

Mandate lines 242–249 require exact `IU4ShadowRuntimeGateV1` and
`IU4ShadowObservationGateV1` types for operational SHADOW; subclasses and
lookalikes must fail closed. Lines 419–422 make exact operational Shadow
facade types mandatory focused coverage, and lines 530–531 reject a reduced
matrix.

The loop signature only annotates the types (`loop.py:1554-1560`). Before any
exact type check, operational code calls duck-typed `startup_log_fields()`
(`:1566-1575`), duck-typed `assert_current_binding()` (`:1577-1593`) and reads
duck-typed Observation-Gate attributes (`:1595-1602`). No exact
`type(value) is ...` boundary exists. The focused active SHADOW test supplies
only valid exact objects and contains no operational subclass/lookalike
negative.

Independent reproducer:

```text
ROOT:/tmp/iu4_i5_impl_rr3_shadow_lookalike.9K0dqP
LOOKALIKE_CALLS:['binding','startup']
LOOKALIKE_REACHED_STARTUP:true
RC:0
```

The literal Legacy owner prevents ENFORCED activation, but it does not satisfy
the explicit OFF/SHADOW exact-type contract.

Required correction:

1. Check both optional operational Gate arguments for exact type before the
   first method or attribute access.
2. Reject subclasses, mappings and method-compatible lookalikes without Tick
   start or side effects.
3. Add separate Runtime-Gate and Observation-Gate lookalike/subclass focused
   negatives.
4. Correct the Evidence inventory and outcome matrix.

### I5-IR3-L1 — LOW — wrong resource reason-code literal in records

The production enum is:

```text
live_l1/state/paper_atomic_coordinator.py:92
RESOURCE_EXHAUSTED = "PEE_IU4_RESOURCE_EXHAUSTED"
```

Resolution 2 line 144 and Evidence line 289 instead name the nonexistent
literal `PEE_ATOMIC_RESOURCE_EXHAUSTED`. Tests compare the enum member rather
than its serialized value and therefore remain green.

Evidence must use `PEE_IU4_RESOURCE_EXHAUSTED`. A new Resolution must
explicitly supersede the inaccurate Resolution-2 narrative; the historical
Resolution-2 record remains unchanged.

## 5. Confirmed prior closures

The independent proportional recheck confirmed:

- pure Loss observation without premature decrement or audit mutation;
- delegated Legacy application reuses the precomputed Control decision;
- Adapter validation and commit remain under one root-lock boundary;
- Gate-error normalization and session/generation/COMMIT/PREPARE/Shadow
  bindings;
- the complete active OFF/SHADOW post-Control owner seam is now inside
  `_execute_iu4_legacy_tick_branch()` (`loop.py:1287-1551`);
- the actual loop creates one Control binding (`:1860-1870`), sends that exact
  Decision and Context to the dispatcher (`:1882-1893`) and has no subsequent
  business, persistence or Shadow consumer;
- Gate entry false at Atomic NONE commits exactly one rejected PROGRESS;
- Gate exit false rejects pre-accept, SOFT permits safe CLOSE, and
  `NONE_TO_SOFT` is restricted to CLOSE;
- raw ENOSPC, EACCES, EMFILE and MemoryError cases are classified for all four
  effects without Legacy fallback; and
- fault/replay grid, cross-instance lock, configuration drift and no-fallback
  sentinels otherwise pass.

These closures do not close the newly identified state-denial replay defect or
the operational Shadow exact-type defect.

## 6. Independent verification

Every Python command used `PYTHONDONTWRITEBYTECODE=1`, an isolated `TMPDIR` and
an external `PYTHONPYCACHEPREFIX`. All standard suites completed with RC 0 and
failures/errors/skips `0/0/0`.

| Module/gate | Root | Result |
|---|---|---:|
| focused I5 | `/tmp/iu4_i5_impl_rr3_module_0.781z2C` | 38/38 |
| I4 Adapter V2 | `/tmp/iu4_i5_impl_rr3_module_1.1WLbI9` | 18/18 |
| Adapter V1 | `/tmp/iu4_i5_impl_rr3_module_2.KMsc7d` | 13/13 |
| Pure Control | `/tmp/iu4_i5_impl_rr3_module_3.DEokLN` | 25/25 |
| Atomic V2 | `/tmp/iu4_i5_impl_rr3_module_4.oOnozJ` | 44/44 |
| Atomic V1 | `/tmp/iu4_i5_impl_rr3_module_5.Mr01aZ` | 23/23 |
| Startup Gate | `/tmp/iu4_i5_impl_rr3_module_6.6bMSCI` | 12/12 |
| Runtime Gate | `/tmp/iu4_i5_impl_rr3_module_7.nA4iTS` | 3/3 |
| Shadow Harness | `/tmp/iu4_i5_impl_rr3_module_8.5VJq2n` | 18/18 |
| Shadow Observation Gate | `/tmp/iu4_i5_impl_rr3_module_9.ldnuWZ` | 18/18 |
| Replay Evidence | `/tmp/iu4_i5_impl_rr3_module_10.wHrR0z` | 10/10 |
| Replay Pipeline | `/tmp/iu4_i5_impl_rr3_module_11.dh4ypE` | 6/6 |
| Economics Shadow Runtime | `/tmp/iu4_i5_impl_rr3_module_12.ipJ1wl` | 9/9 |
| Safe Launch Shadow Gate | `/tmp/iu4_i5_impl_rr3_module_13.4igROE` | 3/3 |
| Pre-execution Guards | `/tmp/iu4_i5_impl_rr3_module_14.qbRkts` | 6/6 |
| all 15 modules | roots above | 246/246 |
| adjacent combined | `/tmp/iu4_i5_impl_rr3_adjacent.YxHYtA` | 208/208 |
| full `tests/live_l1` | `/tmp/iu4_i5_impl_rr3_live.6lLPut` | 475/475 |
| full `tests/regression` | `/tmp/iu4_i5_impl_rr3_regression.HQ7YIN` | 170/170 |
| exact four-path compile | `/tmp/iu4_i5_impl_rr3_compile.MVHEd7` | PASS, exactly 4 `.pyc` |
| `git diff --check` | repository | PASS |
| `git diff --cached --check` | repository | PASS |

Additional independent closure suites:

```text
/tmp/iu4_i5_impl_rr3_targeted_closures.zzP7Lb:6/6 PASS
/tmp/iu4_i5_impl_rr3_targeted_exactly_once.7NT6cb:4/4 PASS
```

The compile products existed only below the recorded `/tmp` pycache root. No
repository-local bytecode was created.

## 7. Non-activation

- The operational loop signature exposes no V2 Runtime-Gate, Adapter,
  ENFORCED, callback or mode-boolean parameter.
- The active loop selects literal Legacy owner at `loop.py:1857`.
- The only operational dispatcher call receives that Legacy owner.
- `_execute_iu4_enforced_seam` is private and absent from `__all__`.
- `PaperIU4AdapterV2` is absent from Adapter `__all__`.
- The ENFORCED wrapper has no call site outside the focused test.
- `safe_launch.py` passes only preserved Shadow-V1 facades.
- No launcher, Exchange, Live, I6–I8 or activation path was found.

## 8. Freeze and Preservation

```text
FREEZE_DIRECTORY_MODE:0555
PRESERVATION_TAR_SHA256:3af14ff2e270d7d3ca09c1279da7d64e6d720630d06a0c5f45b6786237782037
PRESERVATION_TAR_MODE:0444
PRESERVATION_TAR_ENTRIES:1318
FREEZE_MANIFEST_SHA256:ad154c0eda13470920878873ed170368cc8f4c43591400a07592a77b179d9e16
FREEZE_MANIFEST_MODE:0444
FREEZE_MANIFEST_LINES:60
```

All 25 Mandate Section-5 identities and counts were independently recomputed
and matched exactly. Atomic V2, lifecycle authority, accepted I3/I4 Evidence,
Runtime/Startup/Shadow gates, State Store, economics, throttles, launcher and
adjacent Legacy tests remain byte-identical.

## 9. Decision and next step

The green standard suites confirm the prior closures but do not override the
durable replay and exact-type contract violations.

```text
FINAL_VERDICT:NOT_READY
I5_INDEPENDENT_ACCEPTANCE:NOT_READY
IMPLEMENTATION_ACCEPTED:NO
OPERATIONAL_ENFORCED_START_AUTHORIZED:NO
ENFORCED_ACTIVATION_AUTHORIZED:NO
I6_AUTHORIZED:NO
NEXT_REQUIRED_STEP:IU4-I5-ACTIVE-EXECUTION-SEAM-IMPLEMENTATION-REREVIEW-3-RESOLUTION-FILE-EXACT
```

The next workstream may correct only the two blockers and Evidence precision
within the existing five I5 paths, issue a separate Resolution governance
record and then request a fresh independent read-only rereview. It does not
authorize I6 or activation.
