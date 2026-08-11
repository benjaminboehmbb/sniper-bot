# Pre-IU-4 Guard Blocker Fix Evidence

Date: 2026-08-09

Branch: `codex/pre-iu4-guard-blocker-fix-2026-08-09`

Source review baseline: `51a3eaa`

Status: **BLOCKER FIXED AND LOCALLY VERIFIED**

## Scope

This change addresses only the independently confirmed pre-execution guard
blocker. IU-4, Exchange access, and Live activation remain locked. The untracked
user-owned file `scripts/build_rcc002_spec_bundle.py` was not inspected,
modified, staged, or committed.

## Corrected behavior

Before this change, `apply_paper_execution()` ran before `evaluate_guards()`.
The resulting kill level was persisted and logged after execution but could not
prevent the current entry.

The active loop now evaluates and persists the guard decision before an entry
candidate reaches `apply_paper_execution()`:

| State | Result |
|---|---|
| `gate_mode=closed`, position FLAT, BUY/SELL | `NOOP`, `GUARD_GATE_CLOSED`, kill level HARD |
| kill level HARD, position FLAT, BUY/SELL | `NOOP`, `GUARD_KILL_LEVEL_HARD` |
| kill level EMERGENCY, position FLAT, BUY/SELL | `NOOP`, `GUARD_KILL_LEVEL_EMERGENCY` |
| `auto/open` with NONE/SOFT | Existing execution path unchanged |
| Existing LONG/SHORT position | Risk-reducing exit and protective TP/SL/time-stop path remains callable |

Every blocked entry emits the explicit L4 event
`guard_blocked_execution`. The S2 position is unchanged.

## Verification

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest \
  tests.live_l1.test_pre_execution_guards -v

Ran 6 tests — OK
```

The targeted suite proves:

- `closed`, HARD, and EMERGENCY do not call the legacy execution function for
  a FLAT BUY entry candidate;
- stable denial reason codes and monotone kill levels;
- `auto + NONE` calls the existing execution path exactly once;
- an existing LONG position can still reach its SELL/exit path while the gate
  is closed;
- a real one-tick loop with forced BUY and `gate_mode=closed` persists FLAT,
  persists kill level HARD, logs the L4 denial, and records execution as NOOP.

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover \
  -s tests/live_l1 -p 'test_*.py'

Ran 87 tests — OK
```

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover \
  -s tests/regression -t .

Ran 170 tests — OK
```

`py_compile` for both changed runtime modules and the new test module passed.
`git diff --check` passed.

## Remaining Pre-IU-4 gates

Closing this blocker does not authorize IU-4. The reconciled review still
requires:

1. a profile-bound decision for daily/6-hour trade-rate and cooldown safety;
2. a specified float-execution to Decimal-PEE ownership transition;
3. S2/S4/execution restart reconciliation;
4. atomic, corruption-safe loss-cluster state persistence;
5. a separate provenance-first cleanup branch for confirmed archive candidates.
