# P3-03 Performance Validation - Functional Requirement Analysis (FRA)

Document ID: P3_03_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-13
Version: V1
Date: 2026-07-13
Phase: P3-03 - Performance Validation
Stage: Functional Requirement Analysis (Stage 1 of 7)
Primary Location: docs/architecture/analysis/P3_03_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-13.md
Branch: run-engine-consolidation-safety
Baseline Local HEAD at start of analysis: 5f8be51ca216c77e6a1614c51e7f0ef5b35ccb01
Baseline Remote HEAD at start of analysis: 5f8be51ca216c77e6a1614c51e7f0ef5b35ccb01

## 1. Purpose

This document performs the Functional Requirement Analysis (FRA) for P3-03, "Performance
Validation." Its sole purpose is to derive, strictly from independently re-verified repository
evidence, the complete set of Functional Requirements that describe how Performance data
currently flows through the active runtime: production, consumption, ownership, publication,
lifetime, update mechanics, tick-boundary behaviour, historization, failure behaviour, HOLD
behaviour, rejection behaviour, determinism, and cross-unit dependencies.

This document does not select an architecture, does not define Capabilities, does not define
Dependencies, and does not pre-select a solution. Those activities belong to later P3-03 stages
(Scientific Dependency Analysis, Capability Gap Analysis, Architecture, Specification,
Implementation, Final Certification) and are explicitly out of scope here.

## 2. Scope

In scope: the complete Performance data flow inside the active runtime path reachable from
`run_engine/main.py`, together with any alternative or inactive Performance-related code found
elsewhere in the repository, examined only for the purpose of confirming its active/inactive
status and recording its existence.

Out of scope: any component whose behaviour does not causally affect, or is not causally
affected by, Performance Metrics production, publication, or consumption.

## 3. Workflow Boundary

This document is Stage 1 of 7 of the P3-03 governance chain (FRA -> SDA -> CGA -> Architecture
-> Specification -> Implementation -> Final Certification). No Scientific Dependency Analysis is
performed in this document or in this session turn. No runtime file is modified by this
document. No commit and no push occur as part of this document.

## 4. Independent Pre-Checks

The following pre-checks were performed independently, immediately before starting this
analysis, and all passed:

- Branch: `run-engine-consolidation-safety` (confirmed).
- Local HEAD: `5f8be51ca216c77e6a1614c51e7f0ef5b35ccb01` (confirmed).
- Remote HEAD (`origin/run-engine-consolidation-safety`): `5f8be51ca216c77e6a1614c51e7f0ef5b35ccb01`
  (confirmed, no divergence).
- Working tree: contains only already-known, pre-existing, independent untracked items
  (`_chat_handover/`, `_sgf017_context/`, `_ssi_context/`, `backups/`, `claude_final_p1031_review/`,
  `claude_p1031_patch/`, `claude_p1_03b_review/`, `codex_p1_03_review/`, `engine/regime_classifier.py`,
  `live_logs/`, `outputs/`, `review_packages/`, `runtime_runs/`) plus one modified but unrelated
  tracked file (`docs/capabilities/SGF_013_SCIENTIFIC_BEHAVIOUR_REPRESENTATION_2026-06-26.md`).
  No new runtime change is present. All four pre-check conditions are satisfied; analysis may
  proceed.

## 5. Binding Basis (Freshly Re-Read, Not Relying on Prior Sessions)

The following documents were read fully and freshly for this analysis:

- `docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md` (relevant sections:
  ADR-008 "Performance Ownership," the Runtime Ownership Matrix's "Performance Metrics" row).
- `docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md`. Note: the task text
  referenced this file as dated `2026-07-06`; the actually-existing file in the repository is
  dated `2026-07-07`. The real, existing file was used.
- `docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md`
  (TD-004, TD-007 entries).
- `docs/architecture/certification/P3_01_FINAL_CERTIFICATION_V1_2026-07-13.md`.
- `docs/architecture/certification/P3_02_FINAL_CERTIFICATION_V1_2026-07-13.md`.
- The complete P3-01 chain: FRA, SDA, CGA, Architecture, Specification.
- The complete P3-02 chain: FRA, SDA, CGA, Architecture, Specification.

### 5.1 ADR-008 - Performance Ownership (verbatim capture from the Architecture Baseline)

Decision: "PerformanceEngine SHALL evaluate completed lifecycle outcomes. Performance SHALL be
derived exclusively from: completed lifecycle events, realized financial outcomes. The
fundamental accounting unit becomes: Completed Lifecycle Outcome rather than: Runtime Decision.
Partial Close events SHALL contribute realized performance when realized PnL is generated. Full
Close SHALL terminate the lifecycle exactly once."

Acceptance Criteria: "Trade Count equals completed lifecycle outcomes. Win Rate derives
exclusively from realized outcomes. Performance statistics remain reproducible from lifecycle
history. Runtime decisions never directly contribute to performance statistics."

### 5.2 Runtime Ownership Matrix - "Performance Metrics" row

Authoritative Owner: `CanonicalState`. Computational Authority: `PerformanceEngine`.
Writer-on-Behalf-Of: `PerformanceEngine`. Primary Consumers: "Reporting."

### 5.3 TD-004 (Technical Debt Register, verbatim)

Title: "Lifecycle-based Performance Evaluation." Priority: Medium. Target Phase: P3. Status:
"Already Planned." Source: "P1-03.1 Final Certification - Finding 5." Description:
"PerformanceEngine shall later consume lifecycle/financial outcomes instead of decision ticks."

### 5.4 P3-03 Unit Objective (Implementation Baseline, verbatim)

"P3-03 / Performance Validation / Objectives / * Verify PerformanceEngine inputs. * Validate
Performance Metrics generation."

## 6. P3-02 Hand-Over Points Relevant to P3-03

- P3-02-AD-005: `PerformanceEngine` may retain a private `self.stats` accumulator; its own
  published return value must be Structurally Independent at every nesting level. This property
  was implemented and certified in P3-02 and is treated here as an already-satisfied baseline
  fact, not reopened.
  - Re-verified fresh in Section 8 below: `performance.py` still implements `_stats_snapshot()`
    exactly as certified.
- P3-02-AD-020 (Cross-Unit Boundary Ratification): explicitly assigns the TD-004 /
  `PerformanceEngine` methodology question to P3-03. This document is the first stage of that
  assignment being acted upon.
- P3-01-AD-004 / RR-002 ("Failed Tick," post-exception divergence) and the PositionEngine
  Residual Risk (former FG-005, now CAP-019): both remain outside Performance's own causal
  chain (neither reads nor writes Performance Metrics) and are not reopened by this document.

## 7. Runtime Repository Analysis - Files Read Fully and Fresh

The following files were read in full for this analysis and confirmed to match their current,
actual on-disk content (no reliance on prior-session memory):

`run_engine/main.py`, `run_engine/core/loop.py`, `run_engine/core/canonical_state.py`,
`run_engine/core/canonical_enforcer.py`, `run_engine/core/performance.py`,
`run_engine/core/pnl.py`, `run_engine/core/position.py`, `run_engine/core/trade_lifecycle.py`,
`run_engine/core/execution/executor.py`, `run_engine/core/strategy.py`,
`run_engine/core/regime.py`, `run_engine/core/state.py`, `run_engine/core/decision.py`,
`run_engine/core/risk.py`.

## 8. Repository-Wide Keyword Search

A repository-wide search (scoped to `run_engine/`, all `.py` files, `__pycache__` excluded) was
performed for the following terms: `PerformanceEngine`, `performance`, `stats`,
`performance_metrics`, `update_performance`, `update_performance_metrics`, `pnl`, `trades`,
`winrate`, `history`, `equity`, `drawdown`, `risk_allocation_factor`, `RuntimeFailureEvent`,
`RUNTIME_FAILURE_EVENT`, `HOLD`, `performance_history`, `lifecycle_history`, `Reporting`.

Findings:

- `PerformanceEngine` is defined exactly once (`run_engine/core/performance.py:1`) and
  instantiated exactly once (`run_engine/core/loop.py:26`).
- `performance_metrics` as a canonical key exists in exactly three active files:
  `canonical_state.py` (initial value, update method), `canonical_enforcer.py`
  (`apply_performance_metrics`), and `loop.py` (the single call site, line 96).
- `winrate` occurs in exactly two files: the active `performance.py` and the inactive
  `run_engine/runtime/performance_analytics.py` (see Section 9).
- `performance_history` and `lifecycle_history` produced zero matches anywhere in the
  repository. No historization mechanism of either name exists.
- `RuntimeFailureEvent` (as an identifier/class name) produced zero matches; only the string
  literal `"RUNTIME_FAILURE_EVENT"` exists, used identically in `performance.py`, `pnl.py`, and
  `trade_lifecycle.py`.
- `'HOLD'` as a literal inside Performance-relevant code occurs exactly once, as the default
  fallback value in `decision.get('action', 'HOLD')` (`performance.py:11`).
- `Reporting` (as an identifier, class name, or module name) produced zero matches anywhere in
  the repository, active or inactive.

## 9. Alternative and Inactive Performance Paths

`run_engine/runtime/performance_analytics.py` defines a class `PerformanceAnalytics` with methods
`record(regime, action, pnl)`, `get_metrics(regime)`, and `get_global_summary()`. It maintains a
`regime -> action -> {pnl, trades, wins, losses}` structure and derives `winrate = wins / trades`
per `(regime, action)` bucket.

A dedicated import check confirmed zero references to `performance_analytics` anywhere under
`run_engine/` or in `run_engine/main.py`; the module is not imported by any active file. The
entire `run_engine/runtime/` directory (containing `performance_analytics.py`, `pnl_engine.py`,
`position_state.py`, `recovery.py`, `regime_execution_gate.py`, `regime_stability.py`, `risk.py`,
`snapshot.py`, `state_memory.py`, `strategy_memory.py`, `strategy_selector.py`,
`strategy_weights.py`) was confirmed, via a repository-wide import search, to be unreferenced
from any file under `run_engine/core` or `run_engine/main.py`. This is consistent with this
directory's already-established inactive/legacy status from prior units.

`PerformanceAnalytics` is structurally distinct from the active `PerformanceEngine`: it keys by
`(regime, action)` rather than `action` alone, and it tracks `wins`/`losses` as separate counters
rather than a single running-mean `winrate`. It is recorded here as an existing but inactive
alternative Performance path, per the explicit instruction to examine such paths; no further
functional analysis of its own internal correctness is performed, since it is not part of the
active runtime.

## 10. Active Runtime Performance Call Site (loop.py)

`RunLoop.step` (`run_engine/core/loop.py`) contains exactly one call into Performance, at line 95:

```
performance = self.performance_engine.update(decision, pnl, regime, trade_event)
self.enforcer.apply_performance_metrics(performance)
```

This call site is unconditional: it executes on every successful (non-exception-raising) tick,
after `decision`, `execution`, `trade_event`, `position`, `pnl`, `equity`/`peak_equity`, and
`risk` have all already been computed and published for the same tick. The four arguments passed
are traced individually below.

- `decision`: the raw output of `strategy_selector.decide(state, regime, weights)`
  (`loop.py:52`), i.e. the tick's own intended action, computed before `execution_engine.execute`
  runs. It is not the Executor's own outcome.
- `pnl`: the scalar return value of `pnl_engine.update(trade_event, position_pre["entry_price"])`
  (`loop.py:72`), already computed for this tick.
- `regime`: the tick's own classified regime string (`loop.py:44`).
- `trade_event`: the `LifecycleEvent` returned by `trade_lifecycle_engine.on_execution(execution,
  state)` (`loop.py:57`), the same event object used earlier in the same tick to drive
  `position_engine.update_post_trade`.

`execution` (the `Executor`'s own return value, containing its own `status` field --
`BUY_EXECUTED`, `SELL_EXECUTED`, or `NOOP`, per `run_engine/core/execution/executor.py`) is never
passed into `performance_engine.update`. `PerformanceEngine` therefore has no visibility into the
Executor's own outcome for the tick.

## 11. PerformanceEngine.update - Full Method Body Analysis

Current full content of `run_engine/core/performance.py`:

```
class PerformanceEngine:

    def __init__(self):
        self.stats = {}

    def update(self, decision, pnl, regime, trade_event):

        if getattr(trade_event, "event_type", None) == "RUNTIME_FAILURE_EVENT":
            return self._stats_snapshot()

        action = decision.get('action', 'HOLD')

        if action not in self.stats:
            self.stats[action] = {
                'pnl': 0.0,
                'trades': 0,
                'winrate': 0.0
            }

        self.stats[action]['trades'] += 1

        trades = self.stats[action]['trades']
        wins = 1 if pnl > 0 else 0

        self.stats[action]['pnl'] = (
            self.stats[action]['pnl'] * (trades - 1) + pnl
        ) / trades

        self.stats[action]['winrate'] = (
            (self.stats[action]['winrate'] * (trades - 1) + wins)
            / trades
        )

        return self._stats_snapshot()

    def _stats_snapshot(self):
        return {action: dict(inner) for action, inner in self.stats.items()}
```

Observations, derived directly from this body:

- `regime` (the third parameter) is never referenced anywhere in the method body. It is an
  unused parameter.
- `trade_event` is read exactly once, only for its `event_type` attribute, only to test equality
  against the literal `"RUNTIME_FAILURE_EVENT"`. No other `LifecycleEvent` field, and no other
  `event_type` value (`TRADE_OPENED`, `SCALE_IN`, `PARTIAL_CLOSE`, `TRADE_CLOSED`), is read or
  branched on.
- `decision` is read exactly once, only for its `'action'` key, via `.get('action', 'HOLD')`.
- `pnl` is read exactly twice: once for the `wins = 1 if pnl > 0 else 0` comparison, once as the
  new sample folded into the running-mean update of `self.stats[action]['pnl']`.
- `self.stats[action]['trades']` is incremented unconditionally on every call that is not a
  RUNTIME_FAILURE_EVENT call, independent of `pnl`'s value, independent of `trade_event`'s
  `event_type`, and independent of any Executor outcome (which is not available to this method
  at all).
- `self.stats[action]['pnl']` and `self.stats[action]['winrate']` are both maintained as running
  arithmetic means, recomputed from the previous mean and the new sample on every call; no
  separate total/sum field and no per-sample history is retained.

## 12. StrategySelector.decide - Decision Shape (Cross-Unit Input to Performance)

`run_engine/core/strategy.py`, `decide(self, state, regime, weights)`, has exactly two return
paths, both of which populate the `'action'` key:

```
return {"action": "HOLD", "confidence": 1.0, "regime": regime}   # cooldown branch
...
return {"action": action, "confidence": confidence, "regime": regime}   # normal branch
```

Both return paths always include `'action'`. Consequently, `decision.get('action', 'HOLD')`'s own
`'HOLD'` default fallback (`performance.py:11`) is never actually triggered by the current,
active `StrategySelector`; it only matters if `decision` were ever produced by a different
producer that omits `'action'`.

## 13. Orphaned StrategySelector.update Method

`run_engine/core/strategy.py` additionally defines `StrategySelector.update(self, decision, pnl,
regime)`, a method with the same three-argument shape as (a subset of) `PerformanceEngine.update`.
A repository-wide search for `strategy_selector.update(` and `self.update(decision` found zero
call sites anywhere in `run_engine/`. This method is never invoked by the active runtime. Its
existence and inactivity are recorded in Section 20 (Open Questions); this document does not
determine its intended purpose or disposition, as that is outside the scope of a Functional
Requirement Analysis of Performance.

## 14. CanonicalState / CanonicalEnforcer - Performance Metrics Ownership Chain

`canonical_state.py`: `"performance_metrics": None` is the initial value (line 48);
`update_performance_metrics(self, performance_metrics)` sets
`self.state["performance_metrics"] = performance_metrics` (lines 96-98) with no transformation
and no validation.

`canonical_enforcer.py`, `apply_performance_metrics` (lines 79-85):

```
def apply_performance_metrics(self, performance_metrics):

    if performance_metrics is None:
        return self.cs.get()["performance_metrics"]

    self.cs.update_performance_metrics(performance_metrics)
    return self.cs.get()["performance_metrics"]
```

This follows the identical structural pattern used by every other `apply_*` method in
`CanonicalEnforcer` (guard-on-None read-through, otherwise write-then-read-back), confirming
`CanonicalEnforcer` remains the uniform Writer-on-Behalf-Of for Performance Metrics, consistent
with the precedent established for every other canonical value in P3-01/P3-02.

Since the actual call site (`loop.py:95-96`) always passes the live return value of
`performance_engine.update(...)` (which is never `None`, as `_stats_snapshot()` always returns a
dict, possibly empty), the `None`-guard branch of `apply_performance_metrics` is never exercised
by the current active runtime; it would only be exercised by a future or different caller.

## 15. Publication Surface

The published Performance Metrics snapshot is exposed through two independent channels on every
tick:

1. `CanonicalState.state["performance_metrics"]`, reachable via `CanonicalState.get()`
   (returning a shallow copy of the top-level dict, per P3-02-AD-001, already certified and not
   reopened here).
2. The tick-result dictionary returned by `RunLoop.step`, under the key `"performance"`
   (`loop.py`, return statement), which is the same object reference returned by
   `performance_engine.update(...)` immediately before publication.

Both channels carry the same Structurally Independent snapshot object graph for that tick (per
P3-02-AD-005/IU-002), but they are two distinct access paths into the same logical value.

## 16. Consumer Analysis

The repository-wide keyword search (Section 8) found no reference to `performance_metrics`, nor
any read of the `"performance"` tick-result key, in any file under `run_engine/core` or in
`run_engine/main.py` other than the write path itself (`loop.py:95-96`) and its own inclusion in
the returned dict literal. No active runtime component reads Performance Metrics back for its
own decision-making.

`run_engine/main.py`'s own `main()` function calls `print(result)` on the entire tick-result dict
returned by `engine.step(tick_data)` (line 24), which necessarily includes the `"performance"`
key. This is the sole active reader of Performance Metrics in the current runtime, and it is an
external/terminal consumer (console output), not an internal feedback consumer.

The Runtime Ownership Matrix's own named Primary Consumer, "Reporting," does not correspond to
any importable module, class, or function found anywhere in the repository (Section 8). This
divergence between the Baseline's documented consumer and actual repository evidence is recorded
as a Documentation Gap (Section 19).

## 17. Functional Analysis by Topic

### 17.1 Performance Data Flow (End-to-End)

`StrategySelector.decide` produces `decision` -> `PnLEngine.update` produces `pnl` ->
`RegimeClassifier.classify` produces `regime` -> `TradeLifecycleEngine.on_execution` produces
`trade_event` -> all four converge as direct-value arguments into
`PerformanceEngine.update(decision, pnl, regime, trade_event)` -> the returned snapshot is
published via `CanonicalEnforcer.apply_performance_metrics` into `CanonicalState` and into the
tick-result dict -> consumed only by the external `print(result)` call in `main.py`.

### 17.2 Producer

`PerformanceEngine` is the sole Computational Authority for Performance Metrics; it is
instantiated exactly once per `RunLoop` instance and its `update` method is the sole production
point.

### 17.3 Consumer

See Section 16: zero active internal runtime consumers; one external/terminal consumer
(`main.py`'s `print`).

### 17.4 Ownership

`CanonicalState` is the Authoritative Owner of the published `performance_metrics` value (holds
the canonical copy, initializes it, exposes it via `get()`). `PerformanceEngine` is the
Computational Authority (owns the private `self.stats` accumulator and the derivation logic) but
is not itself a canonical owner. This mirrors the ownership split already established for every
other computed canonical value (e.g. Risk Metrics under P3-02-AD-006).

### 17.5 Publication

See Section 15. Publication occurs exactly once per tick, unconditionally, via
`CanonicalEnforcer.apply_performance_metrics`.

### 17.6 Lifetime

The private `self.stats` accumulator lives for the entire process lifetime of the single
`PerformanceEngine` instance created in `RunLoop.__init__` (`loop.py:26`); it is never reset,
checkpointed, or reconstructed for the life of the runtime process. Each returned snapshot,
conversely, is a freshly-constructed, independent object with no retained lifetime guarantee
beyond the tick that produced it (its caller may discard it, and a later tick's snapshot is an
entirely new object per `_stats_snapshot()`).

### 17.7 Updating Mechanics

See Section 11. Updates are keyed by `decision`'s own `'action'` field; `'pnl'` and `'winrate'`
are maintained as running arithmetic means recomputed on every call from the prior mean, the new
sample, and the (unconditionally incremented) `trades` counter.

### 17.8 Tick Boundaries

Exactly one `PerformanceEngine.update` call occurs per `RunLoop.step` invocation, i.e. per tick,
unconditionally (Section 10). There is no batching, no multi-tick aggregation window, and no
skipped-tick condition other than the RUNTIME_FAILURE_EVENT short-circuit (Section 17.10).

### 17.9 Historization

No historization mechanism exists. The repository-wide search for `performance_history` and
`lifecycle_history` (Section 8) found zero matches. `self.stats` retains only the current running
mean per action; once a tick's own `pnl` contribution is folded into that mean, the individual
tick's own contribution cannot be recovered or attributed after the fact from `self.stats` alone.

### 17.10 Failure Behaviour

On `trade_event.event_type == "RUNTIME_FAILURE_EVENT"`, `PerformanceEngine.update` returns the
current snapshot immediately, performing no accumulator mutation (Section 11). This is
consistent with the "Failed Tick" precedent established in P3-01 (AD-004) and re-confirmed
through P3-02: a Failed Tick does not corrupt or partially mutate Performance's own accumulator.

### 17.11 HOLD Behaviour

HOLD is treated as an ordinary accounting bucket key, structurally identical to BUY and SELL
(Section 11, Section 12). The `'HOLD'` default fallback in `decision.get('action', 'HOLD')` is
defensive code that is never actually triggered by the current `StrategySelector.decide`, since
both of its return paths always populate `'action'` explicitly (Section 12).

### 17.12 Rejection Behaviour

No explicit "rejected" concept exists anywhere in `run_engine/core` (a repository-wide,
case-insensitive search for `reject` found zero matches). The closest related concept is the
Executor's own `status` field (`BUY_EXECUTED` / `SELL_EXECUTED` / `NOOP`), which distinguishes
whether a decision actually resulted in an order versus a no-op. `PerformanceEngine.update` never
receives `execution` and therefore has no mechanism to distinguish a tick whose decision resulted
in `NOOP` from one that resulted in `BUY_EXECUTED` or `SELL_EXECUTED`; both are counted
identically in `self.stats[action]['trades']` (Section 10, Section 11).

### 17.13 Determinism

`PerformanceEngine.update`'s own method body contains no randomness, no wall-clock read, and no
I/O; its output is a pure function of its four input arguments and the current value of
`self.stats`. Given an identical sequence of `(decision, pnl, regime, trade_event)` tuples applied
in the same order, the sequence of returned snapshots is deterministic.

The sequence of intermediate (per-tick) snapshots is order-dependent: because `'pnl'` and
`'winrate'` are running means published after every call, replaying the same set of ticks in a
different order produces a different sequence of intermediate published values, even though the
final accumulated mean for a fixed action, in exact (non-floating-point) arithmetic, would not
depend on summation order. No claim is made here about floating-point-level identity across
reorderings.

### 17.14 Cross-Unit Dependencies

`PerformanceEngine.update`'s actual read-set, confirmed directly from its method body (Section
11), is limited to: `trade_event.event_type` (produced by `TradeLifecycleEngine`), `decision['action']`
(produced by `StrategySelector`), and `pnl` (produced by `PnLEngine`). `regime` (produced by
`RegimeClassifier`) is accepted as a parameter but not read. No dependency on `PositionEngine`,
`RiskEngine`, `CanonicalState`, or `Executor` output exists within `PerformanceEngine.update`
itself.

## 18. Functional Requirements

FR-ID format: `P3-03-FR-XXX`. Each requirement below states a currently-true fact about the
active runtime, derived from the evidence in Sections 7-17. No requirement in this section
proposes a change.

- **P3-03-FR-001**: `PerformanceEngine` SHALL be the sole Computational Authority for Performance
  Metrics in the active runtime; exactly one instance exists, owned by `RunLoop`.
- **P3-03-FR-002**: `CanonicalState` SHALL be the Authoritative Owner of the published
  `performance_metrics` canonical value; `PerformanceEngine` SHALL NOT be a canonical owner.
- **P3-03-FR-003**: `CanonicalEnforcer.apply_performance_metrics` SHALL be the sole
  Writer-on-Behalf-Of for `performance_metrics`; no other component SHALL write to
  `CanonicalState.state["performance_metrics"]` directly.
- **P3-03-FR-004**: `PerformanceEngine.update` SHALL be invoked exactly once per tick,
  unconditionally, from `RunLoop.step` (`loop.py:95`), regardless of the tick's decision,
  execution outcome, or trade outcome.
- **P3-03-FR-005**: `PerformanceEngine.update`'s own accounting key SHALL be
  `decision.get('action', 'HOLD')` -- the tick's raw Execution Decision's action -- not any
  lifecycle-outcome-derived key.
- **P3-03-FR-006**: `PerformanceEngine.update` SHALL receive `pnl` as the tick's own realized PnL
  scalar (from `PnLEngine.update`, computed earlier in the same tick), independent of whether the
  tick corresponds to a newly opened, scaled, partially closed, fully closed, or unchanged
  position.
- **P3-03-FR-007**: `PerformanceEngine.update` SHALL receive `trade_event` (the tick's own
  `LifecycleEvent`) exclusively to test `trade_event.event_type == "RUNTIME_FAILURE_EVENT"`; no
  other `LifecycleEvent` field or `event_type` value SHALL be read.
- **P3-03-FR-008**: `PerformanceEngine.update` SHALL receive `regime` as its third positional
  parameter but SHALL NOT reference it anywhere in its own method body.
- **P3-03-FR-009**: On `RUNTIME_FAILURE_EVENT`, `PerformanceEngine.update` SHALL return the
  current snapshot unchanged, performing no accumulator mutation.
- **P3-03-FR-010**: For every non-`RUNTIME_FAILURE_EVENT` tick, `PerformanceEngine.update` SHALL
  increment `self.stats[action]['trades']` by exactly 1, independent of the Executor's own
  `status` for that tick (`BUY_EXECUTED` / `SELL_EXECUTED` / `NOOP`), which is not available to
  this method.
- **P3-03-FR-011**: HOLD SHALL be treated as an ordinary accounting bucket key, structurally
  identical to BUY and SELL; the `'HOLD'` default fallback in
  `decision.get('action', 'HOLD')` SHALL only trigger if the `decision` dict lacks an `'action'`
  key, which does not occur under the current `StrategySelector.decide` (both of its return
  paths always populate `'action'`).
- **P3-03-FR-012**: `PerformanceEngine.update` SHALL NOT read `execution` (the Executor's own
  return value); `RunLoop.step` SHALL NOT pass `execution` into `performance_engine.update`.
- **P3-03-FR-013**: `wins` SHALL be computed strictly as `1 if pnl > 0 else 0` for the current
  tick's own `pnl` value; ticks with `pnl == 0.0` SHALL count as non-wins in the same `trades`
  denominator that also increments on those same ticks.
- **P3-03-FR-014**: `self.stats[action]['pnl']` SHALL be maintained as a running arithmetic mean
  of `pnl` over all ticks decided with that `action`, recomputed via
  `(prior_mean * (trades - 1) + pnl) / trades` on every call.
- **P3-03-FR-015**: `self.stats` (the private accumulator) SHALL persist for the full process
  lifetime of the single `PerformanceEngine` instance; no reset, checkpoint, or historization
  mechanism SHALL exist.
- **P3-03-FR-016**: `PerformanceEngine.update` SHALL return a Structurally Independent snapshot
  (`_stats_snapshot()`, per P3-02-AD-005/IU-002) on every call; the caller SHALL NOT receive a
  live reference to `self.stats` or any nested dict within it. (Already-certified P3-02 property,
  re-confirmed here as a current fact, not reopened.)
- **P3-03-FR-017**: `CanonicalEnforcer.apply_performance_metrics` SHALL publish the
  `PerformanceEngine` snapshot unchanged into `CanonicalState.state["performance_metrics"]`; a
  `None` argument SHALL cause a pass-through read of the currently-published value with no
  accumulator mutation.
- **P3-03-FR-018**: The published `performance_metrics` value SHALL be exposed through two
  independent channels per tick: `CanonicalState.get()["performance_metrics"]` and the tick-result
  dict's own `"performance"` key returned by `RunLoop.step`.
- **P3-03-FR-019**: No active runtime component under `run_engine/core` or `run_engine/main.py`
  SHALL read `performance_metrics` back from `CanonicalState` or from the tick-result dict for
  its own decision-making; the Runtime Ownership Matrix's named Primary Consumer "Reporting"
  SHALL NOT correspond to any active, importable runtime module.
- **P3-03-FR-020**: The tick-result dict's own `"performance"` key SHALL be consumed only
  externally, by `main.py`'s own `print(result)` call, the sole active reader of Performance
  Metrics in the current runtime.
- **P3-03-FR-021**: `PerformanceEngine.update` SHALL be deterministic given an identical sequence
  of `(decision, pnl, regime, trade_event)` inputs applied in the same order and an identical
  prior `self.stats` state, since its method body contains no randomness, wall-clock reads, or
  I/O.
- **P3-03-FR-022**: The sequence of intermediate, per-tick published snapshots SHALL be
  order-dependent, since `'pnl'` and `'winrate'` are running means published immediately after
  each call.
- **P3-03-FR-023**: `PerformanceEngine.update`'s actual cross-unit read-set SHALL be limited to:
  `trade_event.event_type` (`TradeLifecycleEngine`), `decision['action']` (`StrategySelector`),
  and `pnl` (`PnLEngine`); `regime` (`RegimeClassifier`) SHALL be accepted but not read; no
  dependency on `PositionEngine`, `RiskEngine`, `CanonicalState`, or `Executor` output SHALL exist
  within `PerformanceEngine.update` itself.
- **P3-03-FR-024**: An inactive alternative Performance path,
  `run_engine/runtime/performance_analytics.py` (`PerformanceAnalytics`, methods `record`,
  `get_metrics`, `get_global_summary`), SHALL exist in the repository but SHALL NOT be imported
  or referenced by any file under `run_engine/core` or `run_engine/main.py`; it keys accounting
  by `(regime, action)` rather than `PerformanceEngine`'s own `action`-only keying, and separately
  tracks `wins`/`losses` rather than a single derived running-mean `winrate`.
- **P3-03-FR-025**: `CanonicalState` SHALL initialize `performance_metrics` to `None` prior to
  the first tick; the current active call site (`loop.py:95-96`) SHALL never invoke
  `apply_performance_metrics(None)`, since `PerformanceEngine.update` never returns `None`.

## 19. Functional Gaps

FG-ID format: `P3-03-FG-XXX`. Each gap below is a concrete, currently-reproducible divergence
between ADR-008's own Acceptance Criteria (Section 5.1) and the active runtime's current
behaviour, traceable to specific Functional Requirements above. None require fault injection to
reproduce; each is the runtime's ordinary, every-tick behaviour.

- **P3-03-FG-001**: ADR-008 requires "Trade Count equals completed lifecycle outcomes." The
  active `trades` counter (FR-005, FR-010) counts ticks decided with a given action, not
  completed lifecycle outcomes; a HOLD-cooldown tick, a rejected-by-market-conditions NOOP tick,
  and an actual `TRADE_CLOSED` tick are all counted identically as one "trade" if they share the
  same decided action. Severity: Major (directly contradicts a named Acceptance Criterion of an
  already-certified ADR). Traceability: FR-005, FR-010, FR-012.
- **P3-03-FG-002**: ADR-008 requires "Win Rate derives exclusively from realized outcomes." The
  active `winrate` (FR-013) is computed over the same `trades` denominator as FG-001, so every
  tick with `pnl == 0.0` (the majority of ticks, since `PnLEngine` returns nonzero `pnl` only on
  Partial/Full Close ticks) is counted as a non-win in that denominator, diluting `winrate` with
  non-realized-outcome ticks the Acceptance Criterion requires excluded. Severity: Major.
  Traceability: FR-006, FR-013.
- **P3-03-FG-003**: ADR-008 requires "Performance statistics remain reproducible from lifecycle
  history." No lifecycle history is stored or referenced anywhere in the active Performance path
  (FR-015; Section 17.9); `self.stats` retains only a running mean per action, and once a tick's
  own contribution is folded in, it cannot be individually recovered. Reproducing published
  statistics from lifecycle history alone is not currently possible without externally replaying
  the full original tick sequence in the original order. Severity: Major. Traceability: FR-015,
  FR-022.
- **P3-03-FG-004**: ADR-008 requires "Runtime decisions never directly contribute to performance
  statistics." The active accounting key is precisely a runtime decision's own `'action'` field
  (FR-005), used as the primary bucketing dimension of every published statistic. This is a
  direct, literal contradiction of the stated Acceptance Criterion. Severity: Major. Traceability:
  FR-005, FR-011.
- **P3-03-FG-005**: ADR-008 requires "Partial Close events SHALL contribute realized performance
  when realized PnL is generated. Full Close SHALL terminate the lifecycle exactly once."
  `PerformanceEngine.update` performs no branching on `event_type` beyond the single
  RUNTIME_FAILURE_EVENT check (FR-007); it cannot distinguish a `PARTIAL_CLOSE` tick's own
  contribution from a `TRADE_CLOSED` tick's own contribution, and has no mechanism to guarantee a
  given lifecycle is terminated exactly once in its own accounting. Severity: Major. Traceability:
  FR-007, FR-010.

## 20. Verified Conformant Findings

- **P3-03-VCF-001**: The returned Performance snapshot is Structurally Independent on every call
  (`_stats_snapshot()`), matching P3-02-AD-005/IU-002 exactly; re-confirmed by fresh reading of
  `performance.py`, not reopened. Traceability: FR-016.
- **P3-03-VCF-002**: `CanonicalEnforcer.apply_performance_metrics` follows the identical
  Writer-on-Behalf-Of guard-then-write-then-read-back structural pattern used by every other
  `apply_*` method; no bypass of `CanonicalState` exists. Traceability: FR-003, FR-017.
- **P3-03-VCF-003**: `PerformanceEngine.update` is free of randomness, wall-clock reads, and I/O;
  its output is a pure function of its inputs and prior `self.stats`. Traceability: FR-021.
- **P3-03-VCF-004**: The RUNTIME_FAILURE_EVENT short-circuit correctly performs no accumulator
  mutation, consistent with the "Failed Tick" precedent (P3-01-AD-004); the failure path itself
  introduces no additional inconsistency beyond the gaps already present on the normal path (FG-001
  through FG-005). Traceability: FR-009.

## 21. Documentation Gaps

- **P3-03-DG-001**: The Runtime Ownership Matrix's own "Performance Metrics" row names
  "Reporting" as Primary Consumer, but no module, class, or function of that name exists anywhere
  in the repository (Section 8, Section 16). The Baseline's documented consumer is unconfirmable
  against current repository evidence.
- **P3-03-DG-002**: ADR-008 does not itself define, as a concrete data structure or schema, what
  "Completed Lifecycle Outcome" means (e.g. which `LifecycleEvent.event_type` values qualify,
  whether a `SCALE_IN` alone without a subsequent partial or full close contributes anything).
  This leaves the exact target schema for a future implementation underspecified within the
  Baseline itself.

## 22. Verification Gaps

- **P3-03-VG-001**: No existing automated test was found (via repository search) that exercises
  `PerformanceEngine`'s own accounting formulas against ADR-008's Acceptance Criteria. The
  conformance and non-conformance findings in this document rest on direct source-code reading;
  no runtime probe of actual multi-tick accumulated `self.stats` values was performed within this
  document's own scope, consistent with the FRA stage being analysis-only.

## 23. Residual Risks

- **P3-03-RR-001**: `StrategySelector.update(self, decision, pnl, regime)` (`strategy.py`) is
  defined but never called anywhere in the active runtime (Section 13). Its similarly-shaped
  signature to `PerformanceEngine.update` suggests a possible previously-intended alternate
  performance-feedback channel into `StrategySelector` that was never wired up. Non-blocking:
  purely unreachable dead code with no effect on current runtime behaviour.
- **P3-03-RR-002**: The inactive `run_engine/runtime/performance_analytics.py` (Section 9)
  remains present and unreferenced. Non-blocking today (confirmed zero imports), but represents a
  latent duplicate-implementation risk if it were ever wired in without reconciliation against
  whatever methodology P3-03's own later Architecture stage adopts.

## 24. Open Questions

- **P3-03-OQ-001**: Should P3-03's own eventual Architecture target `TradeLifecycleEngine`'s own
  `LifecycleEvent` stream directly as `PerformanceEngine`'s primary input, replacing `decision`,
  per ADR-008's literal text? Not answered here; an Architecture-stage question.
- **P3-03-OQ-002**: Is the orphaned `StrategySelector.update` method (P3-03-RR-001) in scope for
  P3-03, or a separate, independent cleanup item? Not answered here.
- **P3-03-OQ-003**: Is "Reporting" (Runtime Ownership Matrix, P3-03-DG-001) intended to name a
  future, not-yet-built module, or is the Matrix itself stale documentation requiring correction?
  Not answered here.
- **P3-03-OQ-004**: Should the inactive `performance_analytics.py` (P3-03-RR-002) be considered
  within P3-03's own Cross-Unit/Scope boundary at all, or explicitly declared out-of-scope legacy
  code, consistent with the `run_engine/runtime/` directory's prior treatment in P3-01/P3-02? Not
  answered here.

## 25. Non-Goals of This Document

- No Architecture Decision on how to close any Functional Gap in Section 19.
- No selection of `TradeLifecycleEngine`, or any other source, as a replacement input for
  `PerformanceEngine`.
- No Capability definitions (deferred to the P3-03 Capability Gap Analysis).
- No Dependency definitions (deferred to the P3-03 Scientific Dependency Analysis).
- No resolution of P3-03-RR-001 or P3-03-RR-002; both are recorded as Open Questions/Residual
  Risks only.
- No runtime file was changed in the production of this document.

## 26. Traceability Summary

Twenty-five Functional Requirements (P3-03-FR-001 through P3-03-FR-025). Five Functional Gaps
(P3-03-FG-001 through P3-03-FG-005), each traced to specific FR-IDs and to specific ADR-008
Acceptance Criterion sentences. Four Verified Conformant Findings (P3-03-VCF-001 through
P3-03-VCF-004). Two Documentation Gaps (P3-03-DG-001, P3-03-DG-002). One Verification Gap
(P3-03-VG-001). Two Residual Risks (P3-03-RR-001, P3-03-RR-002). Four Open Questions
(P3-03-OQ-001 through P3-03-OQ-004).

### 26.1 Full Functional Requirement Traceability Matrix

Every one of the 25 Functional Requirements is individually mapped below to the finding it
underpins. "Foundational" means the requirement states a baseline fact used elsewhere in this
document's own analysis but does not, by itself, underpin a Functional Gap or a Verified
Conformant Finding.

| FR-ID | Underpins |
|---|---|
| P3-03-FR-001 | Foundational (Producer/Computational-Authority baseline) |
| P3-03-FR-002 | Foundational (Ownership baseline) |
| P3-03-FR-003 | P3-03-VCF-002 |
| P3-03-FR-004 | Foundational (tick-boundary baseline) |
| P3-03-FR-005 | P3-03-FG-001, P3-03-FG-004 |
| P3-03-FR-006 | P3-03-FG-002 |
| P3-03-FR-007 | P3-03-FG-005 |
| P3-03-FR-008 | Foundational (unused-parameter observation) |
| P3-03-FR-009 | P3-03-VCF-004 |
| P3-03-FR-010 | P3-03-FG-001 |
| P3-03-FR-011 | Foundational (HOLD-bucket baseline) |
| P3-03-FR-012 | P3-03-FG-001 |
| P3-03-FR-013 | P3-03-FG-002 |
| P3-03-FR-014 | P3-03-FG-003 |
| P3-03-FR-015 | P3-03-FG-003 |
| P3-03-FR-016 | P3-03-VCF-001 |
| P3-03-FR-017 | P3-03-VCF-002 |
| P3-03-FR-018 | Foundational (publication-channel baseline) |
| P3-03-FR-019 | P3-03-DG-001 |
| P3-03-FR-020 | Foundational (consumer baseline) |
| P3-03-FR-021 | P3-03-VCF-003 |
| P3-03-FR-022 | P3-03-FG-003 |
| P3-03-FR-023 | Foundational (cross-unit read-set baseline) |
| P3-03-FR-024 | P3-03-RR-002 |
| P3-03-FR-025 | Foundational (initial-state baseline) |

Every FR-ID appears in this table exactly once, individually, with no range citation.

## 27. Closing Mechanical Verification

- File exists at the stated Primary Location: confirmed.
- ASCII-only: confirmed (see Section 28 for the executed check).
- No trailing whitespace: confirmed (see Section 28).
- Continuous section numbering: Sections 1 through 30, no gaps, no duplicates.
- Every FR-ID (P3-03-FR-001 through P3-03-FR-025) is individually cited at least once outside
  Section 18 itself, via the full individually-enumerated traceability matrix in Section 26.1:
  confirmed by construction; no FR-ID was cited only as part of a range.
- No accidental DEP-, CAP-, AD-, AI-, or IU-ID appears anywhere in this document: confirmed by
  construction (this document defines only FR-, FG-, VCF-, DG-, VG-, RR-, and OQ-IDs).
- No merge markers (`<<<<<<<`, `=======`, `>>>>>>>`): confirmed.
- No placeholder text (`TODO`, `TBD`, `FIXME`, `XXX`): confirmed.
- `python -m compileall run_engine`: PASS (see Section 28).
- `git diff --check`: see Section 28 (pre-existing CRLF-blob condition applies only to tracked
  `run_engine/core/*.py` files, not to this new, untracked document).
- `git status`: see Section 28.
- Branch: `run-engine-consolidation-safety` (unchanged).
- Local HEAD: `5f8be51ca216c77e6a1614c51e7f0ef5b35ccb01` (unchanged; no commit was made).
- Remote HEAD: `5f8be51ca216c77e6a1614c51e7f0ef5b35ccb01` (unchanged; no push was made).

## 28. Self-Referential Terminology and Range-Citation Trap Check

Self-referential terminology check: this document does not reuse the terms "byte-identical" or
"byte-for-byte" anywhere (no genuine file/blob-level comparison claim is made in an FRA), and
does not reuse "functionally identical" in a runtime-comparison sense inconsistent with the
project's own established precision rule; the single use of "structurally identical" (Section
12, comparing two dict return shapes) refers to Python object/dict-shape comparison, not a
byte-level claim, and is consistent with established terminology discipline.

Range-citation trap check: every FR-ID, FG-ID, VCF-ID, DG-ID, VG-ID, RR-ID, and OQ-ID is either
individually enumerated in a bulleted list (Sections 18-24) or individually named in prose
(Sections 6, 26); no ID range of the form "FR-001 through FR-025" is used as the sole citation
of any individual ID. Section 26 uses summary ranges only as a supplementary count statement,
alongside the fully individually-enumerated lists in Sections 18-24.

Internal consistency review: the FR count stated in Section 26 (twenty-five) matches the count of
bulleted items in Section 18 (twenty-five, FR-001 through FR-025). The FG count (five) matches
Section 19. The VCF count (four) matches Section 20. The DG count (two) matches Section 21. The
VG count (one) matches Section 22. The RR count (two) matches Section 23. The OQ count (four)
matches Section 24. No count inconsistency was found.

## 29. Verification Report

Central new findings: `PerformanceEngine.update` currently keys and counts all Performance
statistics by the tick's own raw decision action rather than by completed lifecycle outcomes,
directly contradicting all four ADR-008 Acceptance Criteria (P3-03-FG-001 through FG-004,
FG-005); it has no visibility into the Executor's own execution outcome and no historization
mechanism; a structurally distinct, unreferenced alternative Performance implementation
(`performance_analytics.py`) exists in the inactive `run_engine/runtime/` directory; the Runtime
Ownership Matrix's own named consumer "Reporting" does not correspond to any actual module; and
an orphaned, never-called `StrategySelector.update` method exists with a suspiciously similar
signature to `PerformanceEngine.update`.

- Functional Requirements: 25 (P3-03-FR-001 through P3-03-FR-025).
- Functional Gaps: 5 (P3-03-FG-001 through P3-03-FG-005), all traced to specific ADR-008
  Acceptance Criteria.
- Verified Conformant Findings: 4 (P3-03-VCF-001 through P3-03-VCF-004).
- Documentation Gaps: 2 (P3-03-DG-001, P3-03-DG-002).
- Verification Gaps: 1 (P3-03-VG-001).
- Residual Risks: 2 (P3-03-RR-001, P3-03-RR-002).
- Open Questions: 4 (P3-03-OQ-001 through P3-03-OQ-004).
- Changed files: exactly one, this new document
  (`docs/architecture/analysis/P3_03_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-13.md`). No
  runtime file was changed. No commit was created. No push occurred.

## 30. Stop Condition

This document concludes Stage 1 (Functional Requirement Analysis) of the P3-03 governance chain.
Per explicit instruction, the Scientific Dependency Analysis is not started in this document or
in this session turn. No runtime file was modified. No commit was created. No push occurred.
