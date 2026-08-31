# Pre-IU4 I5 Active Execution Seam — Implementation Rereview 2 Resolution — File Exact — 2026-08-20

## 1. Resolution status

```text
WORKSTREAM:IU4-I5-ACTIVE-EXECUTION-SEAM-IMPLEMENTATION-REREVIEW-2-RESOLUTION-FILE-EXACT
RESOLUTION_RESULT:READY_FOR_INDEPENDENT_REREVIEW_3
REREVIEW_2_BLOCKERS_CLOSED:3/3
BLOCKER_OPEN:0
HIGH_OPEN:0
MEDIUM_OPEN:0
LOW_OPEN:0
I5_INDEPENDENT_ACCEPTANCE:PENDING
I6_THROUGH_I8_AUTHORIZED:NO
OPERATIONAL_ENFORCED_START_AUTHORIZED:NO
ENFORCED_ACTIVATION_AUTHORIZED:NO
EXCHANGE_AUTHORIZED:NO
LIVE_AUTHORIZED:NO
```

This record resolves only the three findings in the second independent I5
implementation rereview. It does not grant independent acceptance, I6 work,
an active ENFORCED consumer, launcher authority or activation authority.

## 2. Controlling authority chain

| Artifact | SHA-256 | Lines | Status |
|---|---|---:|---|
| Revision-21 specification | `ab8f80720a1d8fe49b9085bce63658bcaecf7f0a3ea70fb555559223090824e0` | 4,605 | controlling |
| final I4 independent rereview 3 | `c6d8bbcb35572a364b74a47eb9ad817240a8b0cce70e514942bb674d3861c38b` | 191 | READY |
| I5 file-exact mandate revision 2 | `124de947c7eebaaeffa37fb802c0bf3194b1595107628cd655bab8b833522060` | 562 | authorized |
| I5 mandate independent rereview 2 | `3d02b2f5791218643e7d76805701e88fbed5c121a884944a9242b31357740922` | 212 | READY |
| first I5 implementation rereview | `7ddd108a659a37e264b5cfb78172cd00d5d426105455b864b358756aaad57980` | 262 | NOT_READY |
| first I5 implementation resolution | `0661aaa5193f790976ae96256cca4dc74b3c99d4533369587203dc18d76e22ff` | 233 | superseded candidate correction |
| second I5 implementation rereview | `eb5886b59c09cfd3f7b797453642c40f0943666b3d9f9df7d8b45e7077bf940a` | 213 | NOT_READY, 3/0/0/0 |
| corrected I5 Evidence | `ad303dc6b763ddf33a38ab45e9be0a728a72b5c6fa96bae175b4f24e9920a7b5` | 452 | PASS candidate |

```text
CANONICAL_REPOSITORY:/home/benja/projects/sniper-bot
BRANCH:main
HEAD:c7ce0452aa2ccbf08c462784d68fa07b3dfe9595
MAIN:c7ce0452aa2ccbf08c462784d68fa07b3dfe9595
ORIGIN_MAIN:89e13fecd1ab549ca7099818b1c9ad4984cb6f7a
MAIN_AHEAD_OF_ORIGIN:6
MAIN_BEHIND_ORIGIN:0
```

`AGENTS.md` was read completely. The excluded
`scripts/build_rcc002_spec_bundle.py` was not read, executed or modified. No
Git mutation, cleanup or foreign-artifact mutation was performed.

## 3. File-exact candidate transition

Exactly the five I5 implementation/Evidence paths remain in scope. This
Resolution is a separate governance record.

| Operation | Path | Rereview-2 identity | Resolved identity |
|---|---|---|---|
| MODIFY | `live_l1/core/loop.py` | `da21732a8af5f38ae56af5fb0ffcabe554e6abd26af09a40fa959560469159a2`, 1,825 | `d21a422040926d86d04222168b31c780ce20a516d058e8e16ddd9c728258050b`, 1,915 |
| MODIFY | `live_l1/core/execution.py` | `85a9acb238dafd3adf5fd8bf57153772d3c7b41559943bdcce5336e3b60dcb5e`, 1,386 | `85a9acb238dafd3adf5fd8bf57153772d3c7b41559943bdcce5336e3b60dcb5e`, 1,386 |
| MODIFY | `live_l1/core/paper_iu4_adapter.py` | `38c16063de882005c6a22392b474f94b7c981c897e20ae130bad2dafff50dd7e`, 1,646 | `23442e6d943d1bde9d9b6a928d23525a4ca020a528f2a072e11d9da2df618e92`, 1,694 |
| CREATE | `tests/live_l1/test_paper_iu4_execution_seam_v2.py` | `7728b7d7712f2af09d10b44c28afadcd6fc4c26d9e8d2a7fd22f232b13e5b0d2`, 1,628 | `84ce25522d868b8c998f0fbebc22ca32a82d19448d9d61efdd36a57c1a4435cf`, 1,904 |
| CREATE/REPLACE | `docs/review/PRE_IU4_I5_ACTIVE_EXECUTION_SEAM_IMPLEMENTATION_EVIDENCE_2026-08-20.md` | `f1053fd4e38e49333e8bbc32d14ed052bf9e4e5439f0704b7dfc8e35835613f1`, 430 | `ad303dc6b763ddf33a38ab45e9be0a728a72b5c6fa96bae175b4f24e9920a7b5`, 452 |

The mandate-time identities and CREATE-absence proofs remain those bound by
the authorized mandate. No sixth implementation path was introduced.

## 4. Resolution of I5-IR2-B1 — complete active owner seam

Status: **CLOSED**.

- The active loop computes one pure Control binding after fused Intent and
  before every post-Control side effect.
- It constructs an exact frozen `_IU4LegacyTickContext` containing the
  lifecycle/risk/shadow inputs needed by the accepted Legacy path.
- The common dispatcher now receives that exact context for the literal
  Legacy owner. The ENFORCED owner rejects any Legacy context.
- `_execute_iu4_legacy_tick_branch()` owns the complete active OFF/SHADOW
  post-Control sequence: lifecycle sidecar, passive risk, PEE shadow attempt,
  typed Legacy execution, guard/execution/accounting logs, State-last/S2/S4
  mutation, persistence, persisted log and optional Shadow observation.
- No Legacy, State, persistence, accounting or Shadow consumer remains after
  the dispatcher returns. The caller handles only the branch return code.
- The private ENFORCED wrapper remains dormant and has no operational call
  site, launcher parameter or public export.

Focused active one-Tick OFF and SHADOW runs call the actual loop, capture the
dispatcher, prove exact Control-object identity, prove the execution → State
update → persistence → Shadow-observation order and compare byte-equal Legacy
S2/S4 results. This closes the authority-boundary and active-loop proof gaps.

## 5. Resolution of I5-IR2-B2 — Gate capabilities and escalation

Status: **CLOSED**.

### 5.1 Entry capability

The seam passes the exact Runtime Gate `entry_allowed` capability into the V2
Adapter. The Adapter checks an exact bool while holding the Atomic root lock.
For an otherwise valid OPEN request with `entry_allowed=false`, it commits
exactly one rejected PROGRESS transaction with `PEE_IU4_ENTRY_BLOCKED`:

- one Cursor;
- no OPEN;
- no Position, Account, Throttle or Loss business mutation;
- no Legacy fallback; and
- deterministic replay of the existing transaction.

The focused test covers this at Atomic risk NONE, so a Gate denial cannot be
silently overridden by the Atomic State capability.

### 5.2 Exit capability and SOFT

A CLOSE request with Gate `exit_allowed=false` is rejected pre-accept with no
Cursor or State mutation. SOFT with `exit_allowed=true` still permits the safe
CLOSE, preserving the mandated terminal capability behavior.

### 5.3 `NONE_TO_SOFT`

Both the seam and Adapter reject `NONE_TO_SOFT` unless the exact effect is
CLOSE. OPEN, ENTRY_VETO and PROGRESS cannot publish a simultaneous SOFT
escalation. The focused OPEN reproducer now fails before mutation; CLOSE plus
`NONE_TO_SOFT` remains one Atomic Tick transaction.

## 6. Resolution of I5-IR2-B3 — focused matrix and Evidence

Status: **CLOSED**.

The single focused module now contains 38 tests and includes the previously
missing independent cases:

1. actual one-Tick OFF and SHADOW loop executions through the complete Legacy
   owner branch;
2. exact reuse of the same Control object inside that active loop;
3. same exact Control → trusted Context → Request → Atomic Cursor binding;
4. Gate entry denial at Atomic NONE;
5. Gate exit denial and SOFT safe-CLOSE behavior;
6. OPEN plus `NONE_TO_SOFT` rejection without mutation; and
7. raw `OSError(ENOSPC)`, `PermissionError(EACCES)`, `OSError(EMFILE)` and
   `MemoryError` injection at the unchanged Atomic create-new boundary for all
   four effects using unique roots.

The raw resource exceptions are classified by production coordinator code as
`PEE_ATOMIC_RESOURCE_EXHAUSTED`; the test no longer injects already-classified
coordinator exceptions. The corrected 452-line Evidence records the exact
38/38, 246/246, 475/475 and 170/170 results, all temporary roots, the updated
fault matrix and the Rereview-3 next step.

## 7. Mandatory verification

All Python commands used `PYTHONDONTWRITEBYTECODE=1`, isolated `TMPDIR` and an
external `PYTHONPYCACHEPREFIX`. Every run completed with RC 0 and
failures/errors/skips `0/0/0`.

| Gate | Result | Root |
|---|---:|---|
| focused I5 | 38/38 PASS | `/tmp/iu4-i5-r2-resolution-focused.2Y6MHO` |
| I4 Adapter V2 | 18/18 PASS | `/tmp/iu4-i5-r2-resolution-module-0.PtT4i3` |
| Adapter V1 | 13/13 PASS | `/tmp/iu4-i5-r2-resolution-module-1.LJI4Qo` |
| Pure Control | 25/25 PASS | `/tmp/iu4-i5-r2-resolution-module-2.OF4Z3i` |
| Atomic V2 | 44/44 PASS | `/tmp/iu4-i5-r2-resolution-module-3.xtyeEa` |
| Atomic V1 | 23/23 PASS | `/tmp/iu4-i5-r2-resolution-module-4.UDyq36` |
| Startup Gate | 12/12 PASS | `/tmp/iu4-i5-r2-resolution-module-5.g8XAmj` |
| Runtime Gate | 3/3 PASS | `/tmp/iu4-i5-r2-resolution-module-6.NImvwF` |
| Shadow Harness | 18/18 PASS | `/tmp/iu4-i5-r2-resolution-module-7.PYRyg9` |
| Shadow Observation Gate | 18/18 PASS | `/tmp/iu4-i5-r2-resolution-module-8.YlqvFb` |
| Replay Evidence | 10/10 PASS | `/tmp/iu4-i5-r2-resolution-module-9.sykf79` |
| Replay Pipeline | 6/6 PASS | `/tmp/iu4-i5-r2-resolution-module-10.rywhQV` |
| Economics Shadow Runtime | 9/9 PASS | `/tmp/iu4-i5-r2-resolution-module-11.ivpVCb` |
| Safe Launch Shadow Gate | 3/3 PASS | `/tmp/iu4-i5-r2-resolution-module-12.I8xCMt` |
| Pre-execution Guards | 6/6 PASS | `/tmp/iu4-i5-r2-resolution-module-13.qeWDPp` |
| all 15 mandatory modules | 246/246 PASS | focused plus individual roots above |
| adjacent combined, excluding I5 | 208/208 PASS | `/tmp/iu4-i5-r2-resolution-adjacent.paa3ze` |
| full `tests/live_l1` | 475/475 PASS | `/tmp/iu4-i5-r2-resolution-live.TgHuFB` |
| full `tests/regression` | 170/170 PASS | `/tmp/iu4-i5-r2-resolution-regression.pKf1di` |
| exact four-path `py_compile` | PASS, exactly four `.pyc` | `/tmp/iu4-i5-r2-resolution-final-compile.eK9NX7` |
| `git diff --check` | PASS | canonical repository |

The four compile products existed only under the recorded `/tmp` pycache
root. No repository-local bytecode was created.

## 8. Preservation and non-activation

```text
FREEZE_DIRECTORY_MODE:0555
PRESERVATION_TAR_SHA256:3af14ff2e270d7d3ca09c1279da7d64e6d720630d06a0c5f45b6786237782037
PRESERVATION_TAR_MODE:0444
PRESERVATION_TAR_ENTRIES:1318
FREEZE_MANIFEST_SHA256:ad154c0eda13470920878873ed170368cc8f4c43591400a07592a77b179d9e16
FREEZE_MANIFEST_MODE:0444
FREEZE_MANIFEST_LINES:60
```

All 25 Mandate Section-5 preservation identities and counts remain exact.
Atomic V2, lifecycle authority, accepted I3/I4 artifacts, runtime/startup/
shadow gates, State Store, economics, throttle, launcher and adjacent Legacy
tests remain byte-identical. Only the three authorized I5 sources, one focused
test and one Evidence record form the implementation candidate.

The active loop still selects only the literal Legacy owner. The private
ENFORCED wrapper remains test-only. The loop signature has no runtime Gate,
Adapter, callback, owner or ENFORCED parameter. No launcher, environment,
Exchange, Live or production consumer was added. The current production Gate
continues to reject ENFORCED.

## 9. Resolution decision

```text
REREVIEW_2_FINDING_I5_IR2_B1:CLOSED
REREVIEW_2_FINDING_I5_IR2_B2:CLOSED
REREVIEW_2_FINDING_I5_IR2_B3:CLOSED
REREVIEW_2_BLOCKERS_CLOSED:3/3
RESOLUTION_RESULT:READY_FOR_INDEPENDENT_REREVIEW_3
I5_INDEPENDENT_ACCEPTANCE:PENDING
I6_AUTHORIZED:NO
OPERATIONAL_ENFORCED_START_AUTHORIZED:NO
ENFORCED_ACTIVATION_AUTHORIZED:NO
NEXT_REQUIRED_STEP:IU4-I5-ACTIVE-EXECUTION-SEAM-IMPLEMENTATION-INDEPENDENT-READONLY-FILE-EXACT-REREVIEW-3
```

Independent Rereview 3 must recompute every final identity, rerun the required
tests in fresh temporary roots, verify the complete active Legacy owner branch,
Gate denial and escalation ceilings, raw resource classification, exact scope,
Freeze and Preservation. This Resolution does not predetermine that verdict.
