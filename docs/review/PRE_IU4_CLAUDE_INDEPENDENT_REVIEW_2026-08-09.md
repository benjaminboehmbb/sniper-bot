# Pre-IU-4 Claude Independent Review

Date: 2026-08-09

Reviewer/tool: Claude Sonnet 5 (`claude-sonnet-5`) via Claude Code CLI

Reviewed code commit: `263049df549cc9c9ef2698c983cd0b87590f596b`

Audit context commit: `ea19fa75931b83a8409f4c36f7ec9bec27f96b3d`

Verdict: **READY_WITH_CONDITIONS**

## Review controls

Claude was invoked non-interactively with only `Read`, `Glob`, and `Grep` tools.
Edit, Write, NotebookEdit, Bash, WebFetch, and WebSearch were disabled. The
untracked user-owned file `scripts/build_rcc002_spec_bundle.py` was explicitly
excluded and was not inspected. Claude reported that no file was modified,
moved, or deleted.

The user explicitly approved the external read-only transmission to Claude and
Antigravity before the successful external invocation.

## Findings

### 1. BLOCKER — kill switch and `gate_mode` are not enforced before execution

Paths:

- `live_l1/core/loop.py:1065`
- `live_l1/core/loop.py:1121`
- `live_l1/guards/guards.py:37`
- `live_l1/guards/guards.py:70`

`apply_paper_execution()` is called before `evaluate_guards()`. The returned
kill level is assigned and logged after execution, but is not used to block the
current entry. The stricter `apply_guards()` function is never imported or
called. Consequently, `L1_GATE_MODE=closed` and an existing `HARD` or
`EMERGENCY` kill level do not prevent BUY/SELL execution in the active loop.

Smallest safe correction: enforce one authoritative pre-execution guard before
`apply_paper_execution()` and return a stable NOOP/denial reason. Add regression
tests proving that `closed`, `HARD`, and `EMERGENCY` block BUY/SELL.

Local reconciliation: **CONFIRMED**. A fresh source inspection and repository
search reproduced the call ordering and found no consumer of `apply_guards()`.

### 2. HIGH — active execution is float-based and detached from Decimal PEE

Paths:

- `live_l1/core/execution.py:346`
- `live_l1/core/execution.py:721`
- `live_l1/core/paper_economics.py:60`

The active execution path stores and calculates price, size, and PnL as floats.
The PEE contract explicitly rejects float boundary inputs and uses Decimal
arithmetic. IU-4 therefore cannot be implemented as a simple import or feature
switch; the architecture must state how the legacy sizing/PnL owner is replaced
or bridged without producing two economic truths.

Smallest safe correction: make the replacement/bridge and its ownership an
explicit IU-4 prerequisite, with parity tests during transition.

### 3. HIGH — `cost_guards.py` contains safety rules missing from the new guard

Paths:

- `live_l1/guards/cost_guards.py:30`
- `live_l1/guards/cost_guards.py:37`
- `live_l1/state/paper_artifacts.py:56`
- `live_l1/state/paper_artifacts.py:773`

The legacy module contains daily/6-hour trade caps and cooldown rules. The new
profile-bound account guard contains equity, daily loss, drawdown, and fee
limits, but no trade-count or time-based reason codes. Archiving the legacy file
as-is could silently remove overtrading protection.

Smallest safe correction: decide explicitly whether these three protections are
ported into the profile-bound guard with stable PEE reason codes or superseded
by a documented alternative. Do not archive the file before that decision.

### 4. MEDIUM — S2/S4 persistence has no cross-file transaction or parity check

Paths:

- `live_l1/state/state_store.py:190`
- `live_l1/state/state_store.py:220`

S2 and S4 are appended through two independent operations. A crash between them
can persist a position change without corresponding risk counters. Startup
loads the two last records independently and does not prove their shared tick or
execution identity.

Smallest safe correction: extend the existing recovery/reconciliation tools to
cross-check S2, S4, and the execution audit trail during startup.

### 5. MEDIUM — loss-cluster safety state is written non-atomically

Paths:

- `live_l1/core/execution.py:90`
- `live_l1/core/execution.py:106`

`loss_cluster_state.json` is written directly with `open(..., "w")`. A corrupt
file is swallowed during load and resets the pause state to zero.

Smallest safe correction: reuse the existing temporary-file, `fsync`, and
`os.replace` pattern from `live_l1/state/paper_account.py` and fail closed or
emit a stable recovery error for corrupt safety state.

### 6. LOW — atomic-append comment overstates the implementation

Path: `live_l1/state/persist.py:22`

The comment claims a temporary-file append, while the function appends directly
to the destination and `fsync`s it. The downstream reader can discard a partial
trailing line, but this is a different guarantee.

Smallest safe correction: correct the comment to describe the actual safety
property.

## File decisions

| Path | Claude decision | Reason |
|---|---|---|
| `live_l1/state/paper_account.py` | KEEP | Decimal-exact, atomic, idempotent, tested, and not yet wired into the active loop. |
| `live_l1/state/paper_artifacts.py` | KEEP | Strict versioned contracts; correct authority basis after resolving rate/cooldown protection. |
| `live_l1/core/paper_economics.py` | KEEP | Pure, deterministic, and float-boundary-safe. |
| `live_l1/core/paper_economics_shadow.py` | KEEP | Read-only fail-safe bridge. |
| `live_l1/core/paper_economics_shadow_runtime.py` | KEEP | Read-only fail-safe runtime integration. |
| `live_l1/guards/cost_guards.py` | REFACTOR | Do not archive before trade-rate/cooldown protections are decided. |
| `live_l1/guards/guards.py` | REFACTOR | Enforcing function is dead; wired function does not enforce execution. |
| `live_l1/core/loop.py` | REFACTOR | Must enforce the guard before execution. |
| `live_l1/core/execution.py` | REFACTOR | Reconcile float economics and make loss-cluster persistence atomic. |
| `live_l1/state/state_store.py` | REFACTOR | Add S2/S4/execution cross-file recovery validation. |
| `live_l1/state/persist.py` | REFACTOR | Correct the misleading guarantee comment. |
| Four online builders | KEEP_FUTURE_ISOLATED | No active runtime references found. |

## Ordered prerequisites before IU-4

1. Enforce `gate_mode` and kill level before execution, with denial tests.
2. Decide and preserve or replace trade-rate and cooldown protections.
3. Specify the Decimal PEE takeover/bridge from the float execution owner.
4. Add S2/S4/execution restart reconciliation.
5. Make loss-cluster safety-state persistence atomic and corruption-safe.
6. Correct the persistence comment.

## Explicitly reviewed without a finding

- `paper_account.py`: atomic write pattern, idempotent commit, journal-chain
  validation, and recovery behavior.
- `paper_artifacts.py`: Decimal boundaries, schema versions, and accounting
  identities.
- `paper_economics.py`: deterministic pure calculations and float rejection.
- PEE shadow bridge/runtime: fail-safe observation without legacy-state
  mutation.
- The four online builders: still isolated from the active runtime.

## Interpretation

The BLOCKER is a pre-existing active-runtime safety defect, not a defect created
by the Pre-IU-4 audit. IU-4 and Live remain locked. No recommendation from this
review is implemented automatically; the independent Antigravity review and
local verification must be reconciled first.
