Document Class:
Functional Requirement Analysis

Document ID:
P2-03-FRA

Version:
V1.0

Status:
Draft for Internal Review

Date:
2026-07-11

Project:
Trading-Bot Scientific Runtime

Subsystem:
Run Engine

Primary Location:
docs/architecture/analysis/P2_03_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-11.md

Depends On:
- docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md
- docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md
- docs/architecture/certification/P2_02A_FINAL_CERTIFICATION_V1_2026-07-10.md
- docs/architecture/certification/P1_03_1_FINAL_CERTIFICATION_V1_2026-07-09.md
- docs/architecture/certification/P1_04_FINAL_CERTIFICATION_V1_2026-07-09.md
- docs/architecture/certification/P2_01_FINAL_CERTIFICATION_V1_2026-07-10.md
- docs/architecture/analysis/P2_01_CAPABILITY_GAP_ANALYSIS_V1_2026-07-09.md
- docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md
- current runtime code at HEAD 815cd8a

Referenced By:
- future P2-03 Scientific Dependency Analysis
- future P2-03 Capability Gap Analysis
- future P2-03 Architecture
- future P2-03 Specification
- future P2-03 Certification

---

# P2-03 Functional Requirement Analysis

## 1. Purpose


This document performs the Functional Requirement Analysis for P2-03 (Financial Ownership), the implementation unit named directly after P2-02A (Position Ownership, certified complete) in the approved Phase 2 sequence of `RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md`.

This document does not decide architecture. It does not define interfaces. It does not implement code. Its sole purpose is to establish, from direct repository inspection, the verified current state of Financial Ownership (Realized PnL, Realized PnL cumulative, Equity, Peak Equity, Drawdown, Drawdown Ratio), and to derive the functional requirements that a later Scientific Dependency Analysis, Capability Gap Analysis, Architecture, and Specification must satisfy.

## 2. Scope


In scope: PnL Ownership, Realized PnL (cumulative) semantics, Equity, Peak Equity, Drawdown, Drawdown Ratio, canonical Financial State ownership, and the necessary consumer boundaries for RiskEngine and PerformanceEngine with respect to financial values.

Out of scope (Section 24 for full detail): full RiskEngine redesign, Risk Policy, Position Sizing, full PerformanceEngine redesign, Unrealized PnL and Mark-to-Market Portfolio Valuation unless explicitly brought into scope by a later governing document, Multi-Asset Accounting, Fees/Funding/Slippage/Tax Accounting, Persistence, Recovery, the Tick-Complete Snapshot architecture beyond what is already implemented, repository cleanup, and the automated regression test suite (TD-005).

## 3. Binding Architectural Baseline


- `docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md` - ADR-005 (Profit and Loss Accounting), ADR-006 (Canonical Financial State Ownership), ADR-007 (Risk Evaluation as a Pure Computational Layer), ADR-002 (Event-Driven Runtime Evolution, Financial Events), ADR-008 (Performance Ownership), ADR-010 (Deterministic Runtime Execution Ordering), ADR-011 (Runtime Failure Handling), the Runtime Ownership Matrix, Rules OM-001 through OM-009, Architecture Invariants AI-001 through AI-015, Acceptance Criteria AC-001 through AC-015.
- `docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md` - Phase 2 Implementation Units, specifically the P2-03 entry: "Financial Ownership. Objectives: Implement PnLEngine ownership. Verify Realized PnL (cumulative). Verify Equity, Peak Equity and Drawdown consistency."
- `docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md` - TD-006 (RiskEngine Peak Equity and Drawdown Ownership Duplication, Target Phase P2-03/P2-04, Status Deferred).
- `docs/architecture/certification/P2_02A_FINAL_CERTIFICATION_V1_2026-07-10.md` - certified baseline HEAD `48daf17` through `815cd8a`, confirming Position/Exposure ownership consolidated and TD-001 resolved; explicitly confirms TD-006 remains "still OPEN, fully untouched."
- `docs/architecture/analysis/P2_01_CAPABILITY_GAP_ANALYSIS_V1_2026-07-09.md` Section 7 - the original repository-grounded finding that produced TD-006, quoted and re-verified in Section 9 below.

ADR-005's binding text, quoted for traceability:

"PnLEngine SHALL become the exclusive Computational Authority for financial accounting. PnLEngine computes: Realized PnL, Unrealized PnL, Realized PnL (cumulative), Equity, Peak Equity. TradeLifecycleEngine SHALL provide immutable lifecycle facts only. TradeLifecycleEngine SHALL never calculate financial values. CanonicalState SHALL store the resulting canonical financial runtime state."

ADR-006's binding text, quoted for traceability:

"Equity = Initial Capital + Realized PnL (cumulative) + Current Unrealized PnL." "Peak Equity: Highest Equity observed since runtime initialization." "Drawdown = Peak Equity - Current Equity." "PnLEngine SHALL become the exclusive Computational Authority for: Realized PnL, Unrealized PnL, Equity, Peak Equity. CanonicalState SHALL become the Authoritative Owner of all financial runtime state. RiskEngine SHALL calculate Drawdown exclusively from canonical financial state. RiskEngine SHALL never own financial runtime information. CanonicalState SHALL store the canonical Drawdown value. Equity SHALL be recomputed whenever: Realized PnL changes, or Unrealized PnL changes."

ADR-007's binding text, quoted for traceability:

"RiskEngine SHALL operate exclusively as a Computational Layer. RiskEngine SHALL never own: Position, Exposure, Trade, Trade History, Equity, Peak Equity, Canonical Runtime State. RiskEngine computes derived Risk Metrics. CanonicalState stores the resulting canonical Risk Metrics."

Acceptance Criteria (ADR-005/ADR-006, quoted): "Realized PnL originates exclusively from PnLEngine." "Unrealized PnL originates exclusively from PnLEngine." "TradeLifecycleEngine performs no financial computation." "CanonicalState contains exactly one canonical financial state." "Financial values remain reproducible from identical lifecycle history." "Exactly one authoritative Equity exists." "Exactly one authoritative Peak Equity exists." "Exactly one authoritative Drawdown exists." "RiskEngine owns no financial runtime state." "Financial state remains deterministic for identical lifecycle histories."

## 4. Verified Repository and Runtime Baseline


Repository state, verified directly, not assumed:

- Branch: `run-engine-consolidation-safety` (confirmed via `git branch --show-current`).
- HEAD: `815cd8a` ("Clarify certification comparison terminology"), matching the stated starting point exactly (confirmed via `git rev-parse HEAD`).
- Working tree: one modified file unrelated to `run_engine` (`docs/capabilities/SGF_013_SCIENTIFIC_BEHAVIOUR_REPRESENTATION_2026-06-26.md`) and a set of pre-existing untracked directories (`_chat_handover/`, `_sgf017_context/`, `_ssi_context/`, `backups/`, `claude_final_p1031_review/`, `claude_p1031_patch/`, `claude_p1_03b_review/`, `codex_p1_03_review/`, `engine/regime_classifier.py`, `live_logs/`, `outputs/`, `review_packages/`, `runtime_runs/`) - all pre-existing from prior sessions, none inside `run_engine/`, none touched by this analysis. `run_engine/` is confirmed clean (`git status --short run_engine/` returns no output).
- All governing documents named in Section 3 confirmed present at their stated paths.
- No `P2_02_FINAL_CERTIFICATION` document exists in `docs/architecture/certification/`; P2-02 (Runtime Status Consolidation) was implemented at commit `b88eae5` and is used throughout the P2-02A governance chain as a certified baseline reference, but has no dedicated certification file. This predates P2-03 entirely and is recorded here as a factual observation, not a P2-03 gap.

Files read in full for this analysis: `run_engine/core/pnl.py`, `run_engine/core/loop.py`, `run_engine/core/canonical_state.py`, `run_engine/core/canonical_enforcer.py`, `run_engine/core/risk.py`, `run_engine/core/performance.py`, `run_engine/core/position.py`, `run_engine/core/trade_lifecycle.py`, `run_engine/main.py`, `run_engine/core/strategy.py`, `run_engine/core/equity_stabilizer.py`, `run_engine/core/position_sizing.py`, `run_engine/runtime/pnl_engine.py`, `run_engine/runtime/risk.py`, `run_engine/runtime/performance_analytics.py`.

Repository-wide search performed for: `pnl`, `equity`, `drawdown`, `realized`, `cumulative` (case-insensitive) under `run_engine/`. Thirteen files matched; every match is accounted for in Sections 6 through 10 below.

Confirmed inactive (not imported by `run_engine/core/*.py` or `run_engine/main.py`, verified by direct repository-wide import search):

- `run_engine/core/equity_stabilizer.py` (`EquityStabilizer`) - a fourth, independent, smoothing-based "stabilized_equity" computation, distinct in formula from every active computation.
- `run_engine/core/position_sizing.py` (`PositionSizingEngine`) - reads `state.get("equity", 100.0)` and `risk.get("exposure", 1.0)` as consumer inputs only; computes no financial value itself.
- `run_engine/runtime/pnl_engine.py` (`PnLEngine`, same class name as the active `run_engine/core/pnl.py` class but a structurally different, price-delta "reward" computation, not lifecycle-based).
- `run_engine/runtime/risk.py` (`RiskLayer`) - a third, independent Equity/Peak-Equity/Drawdown computation (`update_equity()`, `drawdown()`), separate in mechanism from both `run_engine/core/canonical_state.py` and `run_engine/core/risk.py`.
- `run_engine/runtime/performance_analytics.py` (`PerformanceAnalytics`) - an independent per-regime PnL/win-rate aggregation, structurally unrelated to `run_engine/core/performance.py`.

These five confirmed-inactive files are recorded as evidence that "Equity"/"PnL" have repeatedly acquired independent, competing implementations across this repository's history - the same historical pattern already diagnosed for "Exposure" in the P2-02A Functional Requirement Analysis (Section 7 of that document) - but none of the five participates in the active runtime execution path and none is treated as an active Financial Ownership gap by this document.

`run_engine/core/strategy.py`'s `StrategySelector.update(self, decision, pnl, regime)` accepts a `pnl` parameter but never reads it inside the method body (confirmed by direct read); this method is additionally never called anywhere in `run_engine/core/loop.py` (confirmed by repository-wide search for `strategy_selector.update(`), so it is dead code with respect to financial information, not an active consumer.

## 5. Scientific Definitions


These definitions are restated from ADR-005/ADR-006/ADR-007 and the Architecture Baseline, not newly invented, and govern the rest of this document. Where the current runtime does not implement a concept, this is stated explicitly rather than presented as existing.

**Realized PnL for current event** - the financial consequence of exactly one completed lifecycle event (`TRADE_CLOSED` or `PARTIAL_CLOSE`), computed once per occurrence. Exists in the current runtime (`run_engine/core/pnl.py`).

**Realized PnL cumulative** - the running total of every Realized PnL (event) value since runtime initialization. Named explicitly in ADR-005 and ADR-006's Equity formula. Does not exist as a separately observable, canonically owned value anywhere in the current runtime (Section 7).

**Unrealized PnL** - the mark-to-market financial consequence of the currently open Position, not yet realized through a closing lifecycle event. Named explicitly in ADR-005 and ADR-006's Equity formula. Does not exist anywhere in the current runtime (confirmed absent, matching the P2-01 Capability Gap Analysis's prior finding, Section 7).

**Equity** - per ADR-006: `Initial Capital + Realized PnL (cumulative) + Current Unrealized PnL`. Exists in the current runtime as a stored, incrementally-updated running total (Section 8), not as a value reconstructed from the three named terms of this formula, since neither Realized PnL (cumulative) nor Unrealized PnL is separately observable.

**Peak Equity** - per ADR-006: "Highest Equity observed since runtime initialization." Exists in the current runtime, computed independently in two separate locations (Section 9).

**Absolute Drawdown** - per ADR-006: `Peak Equity - Current Equity`. Exists in the current runtime (`run_engine/core/risk.py`), computed from a non-canonical, internally-tracked Peak Equity value rather than from canonical financial state (Section 10).

**Relative Drawdown / Drawdown Ratio** - `drawdown / peak_equity`, a normalized ratio. Exists in the current runtime (`run_engine/core/risk.py`), computed alongside Absolute Drawdown from the same internally-tracked value. Not separately named anywhere in ADR-006's Scientific Definitions or in the Runtime Ownership Matrix; its ownership assignment is therefore not explicitly traceable to a named ADR term (Section 28, Open Question).

**Financial State** - the complete set of canonical financial runtime values (Realized PnL, Realized PnL cumulative, Unrealized PnL, Equity, Peak Equity, Drawdown, Drawdown Ratio) as stored by `CanonicalState`.

**Financial Event** - per ADR-002's normative event hierarchy: "Realized PnL Updated, Unrealized PnL Updated, Equity Updated, Peak Equity Updated, Drawdown Updated." Architecturally named in ADR-002 but not implemented as an explicit event object anywhere in the current runtime (Section 11); financial values currently propagate as plain return values (`float`, `dict`), not as a `LifecycleEvent`-shaped object with an `event_type` discriminator.

**Financial Derived View** - a read-only reconstruction of a financial value from already-canonical state, possessing no independent ownership (per the Architecture Baseline's general "Derived View" definition, Section 3 above). No component in the current runtime is documented as consuming financial state through an explicitly-labeled Derived View mechanism; every current reader accesses `CanonicalState.state` (or, for `RiskEngine`, its own internally-tracked copy) directly.

**Performance Metric** - a statistic derived from completed lifecycle outcomes (per ADR-008), owned by `PerformanceEngine`. Distinct from Financial State; `PerformanceEngine.stats` aggregates per-action `pnl`/`trades`/`winrate` but does not itself compute Realized PnL, Equity, Peak Equity, or Drawdown (Section 11).

**Risk Metric** - a derived quantity computed by `RiskEngine` from canonical runtime state (per ADR-007), a distinct category from Financial State. Drawdown and Drawdown Ratio are Risk Metrics by this definition, but ADR-006 additionally and specifically assigns their *input source* to canonical financial state, not to RiskEngine's own tracked state (Section 10).

## 6. Current Financial Information Objects


Direct inspection of the active runtime confirms the following distinct financial information objects exist, in some form, at HEAD `815cd8a`:

1. Realized PnL (event) - `run_engine/core/pnl.py`, `PnLEngine.update()`'s return value.
2. Equity - `run_engine/core/canonical_state.py:28`, `CanonicalState.state["equity"]`.
3. Peak Equity - `run_engine/core/canonical_state.py:30`, `CanonicalState.state["peak_equity"]`, and independently `run_engine/core/risk.py:10`, `RiskEngine.self.peak_equity`.
4. Drawdown - `run_engine/core/canonical_state.py:34`, `CanonicalState.state["drawdown"]`, computed by `run_engine/core/risk.py:25`.
5. Drawdown Ratio - `run_engine/core/canonical_state.py:36`, `CanonicalState.state["drawdown_ratio"]`, computed by `run_engine/core/risk.py:28-30`.
6. `PnLEngine.last_realized_pnl` - an instance attribute holding the most recent event's Realized PnL value, overwritten every call to `update()` (not accumulated).

Confirmed absent anywhere in the active runtime:

7. Realized PnL (cumulative) - no field, method, or instance attribute anywhere computes or stores a running sum of Realized PnL events.
8. Unrealized PnL - no field, method, or instance attribute anywhere computes a mark-to-market valuation of the open Position.
9. Initial Capital / Initial Equity as a named, documented constant - only an undocumented literal `100.0`, independently duplicated in `CanonicalState.__init__` (`run_engine/core/canonical_state.py:28,30`) and in `RiskEngine.__init__` (`run_engine/core/risk.py:9-10`), and additionally in the confirmed-inactive `EquityStabilizer.__init__` (`run_engine/core/equity_stabilizer.py:13`) and `RiskLayer.__init__` (`run_engine/runtime/risk.py:9-10`).
10. A Financial Event object of any kind (Section 11).

## 7. Current PnL Representation


`run_engine/core/pnl.py`, class `PnLEngine`:

- Instance state: `self.last_realized_pnl = 0.0`, initialized once, one attribute only.
- `update(trade_event, entry_basis)`: returns `0.0` if `trade_event is None`; returns `0.0` if `event_type` is not `"TRADE_CLOSED"` or `"PARTIAL_CLOSE"`; otherwise computes `pnl = (exit_price - entry_price) * quantity` for LONG or `(entry_price - exit_price) * quantity` for SHORT, sets `self.last_realized_pnl = pnl`, and returns `pnl`.
- This is a per-event (tick-bound) computation. Every call to `update()` either returns the current event's realized PnL or `0.0`; there is no accumulation of prior calls' results anywhere inside `PnLEngine`.
- `self.last_realized_pnl` is set (overwritten, not summed) on every call, including calls that return `0.0` for non-closing events - this attribute therefore tracks "the most recent event's realized PnL" (which decays to `0.0` on the very next non-closing tick), not a cumulative total. `get_last_realized_pnl()` exposes this same non-cumulative value; confirmed by repository-wide search that no active caller invokes `get_last_realized_pnl()` anywhere in `run_engine/core` or `run_engine/main.py`.

`run_engine/core/loop.py:68-69`: `pnl = self.pnl_engine.update(trade_event, position_pre["entry_price"]); self.enforcer.apply_pnl(pnl)`. The tick-local `pnl` value is published, unmodified, into `CanonicalState.state["pnl"]` via `CanonicalEnforcer.apply_pnl()` -> `CanonicalState.update_pnl()` (`run_engine/core/canonical_state.py:67-69`), which performs a direct overwrite (`self.state["pnl"] = pnl`), not an accumulation.

`run_engine/core/loop.py:71`: `equity = self.cstate.get()["equity"] + pnl`. This is the only place in the entire active runtime where the current tick's Realized PnL contributes to a running total. The addition is performed by `RunLoop`, not by `PnLEngine`, and the running total is `Equity`, not a dedicated "Realized PnL (cumulative)" field. Consequently, the cumulative effect of Realized PnL is present in the runtime (Equity does grow and shrink correctly, tick over tick, by the confirmed-correct per-event PnL amounts) but is entangled inside `Equity` and is not separately observable, auditable, or owned as its own canonical value.

Behavior on `TRADE_CLOSED`: `pnl` computed from `entry_basis` (the pre-trade view's `entry_price`, certified P1-03.1/P2-02A-U3 mechanism) and the closing event's `price`/`closed_quantity`; nonzero whenever `exit_price != entry_price`.

Behavior on `PARTIAL_CLOSE`: identical formula, using `closed_quantity` (the reduced quantity), confirmed already certified in P1-03.1 for weighted-average Scale-In interaction.

Behavior on `SCALE_IN`: `event_type == "SCALE_IN"` is not in `{"TRADE_CLOSED", "PARTIAL_CLOSE"}`; `update()` returns `0.0`. No PnL realized. Confirmed unchanged since P1-03.1.

Behavior on `RuntimeFailureEvent`: `event_type == "RUNTIME_FAILURE_EVENT"` is not in `{"TRADE_CLOSED", "PARTIAL_CLOSE"}`; `update()` returns `0.0`. Confirmed still correctly excluded, matching the ADR-011 non-mutation contract already certified in P1-04 (`docs/architecture/certification/P1_04_FINAL_CERTIFICATION_V1_2026-07-09.md`, AC-003).

Behavior with no trade event (`HOLD` ticks, `trade_event is None`): `update()` returns `0.0` immediately at the first guard clause.

## 8. Current Equity Representation


`run_engine/core/loop.py:71-72`: `equity = self.cstate.get()["equity"] + pnl; self.enforcer.apply_equity(equity)`. This is the sole computation site for Equity in the active runtime. `RunLoop` reads the previous tick's canonical Equity value directly out of `CanonicalState`, adds the current tick's Realized PnL, and republishes the sum. This observation describes the current computational path only and does not constitute a conclusion regarding the intended Computational Authority. This computation runs unconditionally, once per tick, regardless of whether a trade event occurred (`pnl` is `0.0` on non-closing ticks, so Equity is republished unchanged in value but the write still executes).

`run_engine/core/canonical_enforcer.py:23-29`, `apply_equity(equity)`: dict-shape-agnostic Writer-on-Behalf-Of, calls `CanonicalState.update_equity(equity)`, matching the pattern already established and certified for Position/PnL/Risk in prior units.

`run_engine/core/canonical_state.py:60-65`, `update_equity(equity)`: `self.state["equity"] = equity; if equity > self.state["peak_equity"]: self.state["peak_equity"] = equity`. This single method performs two distinct responsibilities: storing Equity (an Authoritative Owner responsibility, conformant with ADR-006) and computing Peak Equity (a Computational Authority responsibility that ADR-006 explicitly assigns to `PnLEngine`, not to `CanonicalState`).

Initial Equity: `CanonicalState.__init__`, `"equity": 100.0` (`run_engine/core/canonical_state.py:28`) - an undocumented literal, not a named constant.

Reset behavior: `CanonicalState.reset()` calls `self.__init__()`, restoring `equity` to `100.0`. No other active component holds Equity-adjacent state requiring reset (`RunLoop` holds none; `PnLEngine` holds none).

Deterministic reconstruction: because `Equity` is a stored running total rather than a value computed from `Initial Capital + Realized PnL (cumulative) + Unrealized PnL` at read time, its correctness for any given tick depends on every prior tick's addition having executed correctly and in order - it is reproducible under the current single-threaded, synchronous `RunLoop.step()` execution model (confirmed by the P2-02A regression evidence, `docs/architecture/certification/P2_02A_FINAL_CERTIFICATION_V1_2026-07-10.md` Section 16), but it is not independently re-derivable from a snapshot of `Realized PnL (cumulative)` and `Unrealized PnL` alone, since neither of those two terms is separately stored (Section 7, Section 6 item 7-8).

Consumers of Equity: `RiskEngine.check()` reads `state.get("equity", self.last_equity)` (`run_engine/core/risk.py:15`); `RunLoop` itself reads the prior value to compute the next (`run_engine/core/loop.py:71`); the confirmed-inactive `PositionSizingEngine.size()` reads `state.get("equity", 100.0)` (`run_engine/core/position_sizing.py:9`); the confirmed-inactive `EquityStabilizer.update(equity, raw_pnl)` accepts an externally-supplied `equity` but is never called.

## 9. Current Peak-Equity Representation


Two independent, non-communicating computations of Peak Equity exist in the active runtime.

**Computation 1 - `CanonicalState.update_equity()`** (`run_engine/core/canonical_state.py:64-65`): `if equity > self.state["peak_equity"]: self.state["peak_equity"] = equity`. Reactive to whatever `equity` value `RunLoop` passes in (Section 8); correctly reflects the canonical Equity's own high-water mark, since it is triggered by the same value that is stored as canonical Equity.

**Computation 2 - `RiskEngine.check()`** (`run_engine/core/risk.py:9-10,21-22,51`): `self.peak_equity = 100.0` (instance initialization); `equity = state.get("equity", self.last_equity)`; `if equity > self.peak_equity: self.peak_equity = equity`; `self.last_equity = equity`. This is a second, entirely separate tracker, initialized independently of `CanonicalState`'s own `peak_equity` default, and never reads `state["peak_equity"]` at any point (confirmed by direct repository search: `risk.py` contains no occurrence of `state.get("peak_equity"` or `state["peak_equity"]`).

Under the current synchronous, single-threaded `RunLoop.step()` execution model, both trackers observe an identical Equity sequence each tick (`RiskEngine.check()` is always called with the same-tick `canonical_state = self.cstate.get()`, `run_engine/core/loop.py:74,76`, immediately after `apply_equity()` has already published the current tick's Equity), and both are seeded with the same hardcoded `100.0` literal, so no numeric divergence has been observed or is currently reachable through the active execution path. This exactly reproduces the finding already logged by the P2-01 Capability Gap Analysis (`docs/architecture/analysis/P2_01_CAPABILITY_GAP_ANALYSIS_V1_2026-07-09.md`, Section 7, quoted): "the two hardcoded initial values (RiskEngine's 100.0 and CanonicalState's 100.0) are an undeclared, silent coupling: if either is ever changed independently, or if RiskEngine.check() is ever invoked out of the exact lockstep RunLoop currently maintains, the two would silently diverge with no error." This finding is re-verified, unchanged, at HEAD `815cd8a` and constitutes Technical Debt Register item TD-006.

Reset behavior: `RiskEngine` has no `reset()` method of any kind (confirmed by repository-wide search for `def reset` under `run_engine/core/`, which returns only `CanonicalState.reset()`). If `CanonicalState.reset()` is ever invoked mid-run (there is currently no active caller of `CanonicalState.reset()` anywhere in `run_engine/core` or `run_engine/main.py`, confirmed by search, so this is a latent rather than presently-triggered defect), `CanonicalState.state["peak_equity"]` would return to `100.0` while `RiskEngine.self.peak_equity` would retain its pre-reset value, producing an immediately-inconsistent Drawdown on the very next `check()` call.

Peak Equity's storage location, `CanonicalState.state["peak_equity"]`, matches the Runtime Ownership Matrix's Authoritative Owner assignment. Its Computational Authority does not match ADR-006 ("PnLEngine SHALL become the exclusive Computational Authority for: ... Peak Equity") in either of the two current implementations, since neither `CanonicalState` nor `RiskEngine` is `PnLEngine`.

## 10. Current Drawdown Representation


`run_engine/core/risk.py:24-30`:

```
drawdown = self.peak_equity - equity

drawdown_ratio = 0.0
if self.peak_equity > 0:
    drawdown_ratio = drawdown / self.peak_equity
```

Both values are computed exclusively from `RiskEngine`'s own internally-tracked `self.peak_equity` (Section 9, Computation 2) and the tick-local `equity` value read from `state.get("equity", ...)`. Neither value is computed from `CanonicalState.state["peak_equity"]`.

This directly contradicts ADR-006's explicit text: "RiskEngine SHALL calculate Drawdown exclusively from canonical financial state." The Computational Authority assignment (`RiskEngine`) is itself correct per ADR-006; the input source is not, since "canonical financial state" names `CanonicalState`'s own stored values, not `RiskEngine`'s private, independently-tracked copy.

Publication: `run_engine/core/canonical_enforcer.py:31-37`, `apply_risk(risk)` -> `CanonicalState.update_risk(risk_dict)` (`run_engine/core/canonical_state.py:71-75`): `self.state["drawdown"] = risk_dict.get("drawdown", 0.0); self.state["drawdown_ratio"] = risk_dict.get("drawdown_ratio", 0.0)`. Storage location matches the Runtime Ownership Matrix's Authoritative Owner assignment (`CanonicalState`) for the `Drawdown` row.

Sign and zero semantics: `drawdown` is non-negative under normal operation (`peak_equity` is by construction always `>= equity` immediately after the `if equity > self.peak_equity` update, so `drawdown >= 0`); `drawdown_ratio` defaults to `0.0` only via the `self.peak_equity > 0` guard (never triggered under current hardcoded-positive initialization, but present as a defensive branch). No case was found producing a negative Drawdown or Drawdown Ratio under the current implementation.

Drawdown Ratio's ownership is not independently named in ADR-006's Scientific Definitions (only `Equity`, `Peak Equity`, and `Drawdown` are explicitly defined there); it is reasonably classified under ADR-007's general "Risk Metric" category (Section 5), but no ADR text explicitly assigns it a Computational Authority or Authoritative Owner by name. This is recorded as an Open Question (Section 28), not resolved here.

Consumer confirmation: `run_engine/core/performance.py`'s `PerformanceEngine.update(decision, pnl, regime, trade_event)` does not accept, read, or reference `drawdown`, `drawdown_ratio`, `equity`, or `peak_equity` anywhere in its four-line body (confirmed by direct read). The Runtime Ownership Matrix's `Drawdown` row names `PerformanceEngine` as a Primary Consumer; this is not currently implemented. This is recorded as an observed Matrix-versus-implementation gap, not assigned a resolution by this document (Section 19).

## 11. Current Financial Ownership

Financial Events (ADR-002) are architecturally named but not implemented anywhere in the active runtime; this bears directly on Financial Ownership, since no Financial Event object currently carries a Computational Authority or Authoritative Owner of its own to evaluate.

ADR-002 (`docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md`) names, as part of its normative Runtime Event hierarchy: "Realized PnL Updated, Unrealized PnL Updated, Equity Updated, Peak Equity Updated, Drawdown Updated" under the category "Financial Events," positioned between "Trade Lifecycle Events" and "Risk Events."

No object, class, dataclass, or discriminated-union value matching this description exists anywhere in the active runtime. This is confirmed by contrast with `run_engine/core/trade_lifecycle.py`'s `LifecycleEvent` dataclass (`event_type: str`, `TRADE_OPENED`/`SCALE_IN`/`PARTIAL_CLOSE`/`TRADE_CLOSED`/`RUNTIME_FAILURE_EVENT`), which is the only Runtime Event category from ADR-002's hierarchy that is actually implemented as an explicit event object in the current runtime. Financial values currently propagate as plain Python primitives: `PnLEngine.update()` returns a `float`; `RiskEngine.check()` returns an untyped `dict`; `CanonicalState.update_equity()`/`update_pnl()`/`update_risk()` perform direct key assignment with no event wrapper of any kind.

Whether Financial Events are a required deliverable of P2-03, or whether P2-03's Baseline objectives ("Implement PnLEngine ownership. Verify Realized PnL (cumulative). Verify Equity, Peak Equity and Drawdown consistency.") can be satisfied without introducing an explicit Financial Event object, is not decided by this document (Section 28, Open Question). This document records only that Financial Events are architecturally named but not implemented, and takes no position on whether their implementation is in scope.


**PerformanceEngine's relationship to Financial Ownership.**


`run_engine/core/performance.py`, class `PerformanceEngine`:

- Instance state: `self.stats = {}`, a `dict` keyed by `action` (`"BUY"`/`"SELL"`/`"HOLD"`), each value a `dict` with keys `pnl`, `trades`, `winrate`.
- `update(decision, pnl, regime, trade_event)`: first guards `if getattr(trade_event, "event_type", None) == "RUNTIME_FAILURE_EVENT": return self.stats` unmodified - confirmed correctly excluding rejected transitions, matching the ADR-011 contract already certified in P1-04.
- The `pnl` parameter received is the same tick-local Realized PnL (event) value `RunLoop` already computed via `PnLEngine.update()` (`run_engine/core/loop.py:79`, `performance = self.performance_engine.update(decision, pnl, regime, trade_event)`); `PerformanceEngine` does not itself call `PnLEngine`, does not recompute Realized PnL, and holds no Equity, Peak Equity, or Drawdown state of any kind.
- `self.stats[action]["pnl"]` is an incrementally-averaged per-action mean of received `pnl` values (`(prior_mean * (trades - 1) + pnl) / trades`), a Performance Metric (per-action average realized outcome) distinct from - and not a duplicate of - canonical cumulative Realized PnL, since it is grouped by `action` and expressed as a running mean, not a running sum, and is never republished under a `pnl`-named `CanonicalState` key.
- `PerformanceEngine` therefore currently behaves as a pure consumer of the tick-local Realized PnL value with respect to financial ownership: it does not own, does not independently compute, and does not duplicate any canonical Financial State value. Its own `stats["*"]["pnl"]` field is a distinct Performance Metric, not a second Realized PnL representation.
- `PerformanceEngine` has no `reset()` method (Section 9); `self.stats` therefore persists indefinitely across any `CanonicalState.reset()` call, identical in kind to the `RiskEngine` reset gap already identified in Section 9, though `PerformanceEngine`'s own stale-state risk is scoped to Performance Metrics, not Financial State, and is therefore outside this document's Financial Ownership scope (recorded here only for completeness; full disposition belongs to P3-03 Performance Validation, per the Implementation Baseline's own phase assignment).


**Ownership Summary.**


Restated compactly from Sections 7 through 10; the full per-object table is given in Section 11.

Realized PnL (event): Computational Authority `PnLEngine` (conformant with ADR-005). Authoritative Owner `CanonicalState.state["pnl"]` (conformant). Writer-on-Behalf-Of `CanonicalEnforcer.apply_pnl()` (conformant).

Realized PnL (cumulative): no Computational Authority, no Authoritative Owner, no Writer-on-Behalf-Of exist, because the value itself does not exist (Section 6, item 7).

Equity: Computational Authority `RunLoop` (non-conformant; ADR-005/ADR-006 require `PnLEngine`). Authoritative Owner `CanonicalState.state["equity"]` (conformant on storage location). Writer-on-Behalf-Of `CanonicalEnforcer.apply_equity()` (conformant mechanism).

Peak Equity: Computational Authority split between `CanonicalState.update_equity()` and `RiskEngine.check()` (both non-conformant; ADR-006 requires `PnLEngine` exclusively; ADR-007/Rule OM-007 additionally prohibit `RiskEngine` from owning Peak Equity in any form). Authoritative Owner `CanonicalState.state["peak_equity"]` (conformant on storage location, but not exclusively populated by the intended Computational Authority).

Drawdown: Computational Authority `RiskEngine` (conformant component per ADR-006, non-conformant input source - Section 10). Authoritative Owner `CanonicalState.state["drawdown"]` (conformant on storage location).

Drawdown Ratio: same structure as Drawdown; ownership assignment not independently named by any ADR (Open Question, Section 28).


**Financial Ownership Table.**


| Information Object | Current Computational Authority | Intended Computational Authority | Current Authoritative Owner | Intended Authoritative Owner | Writer-on-Behalf-Of | Readers | Writers | Storage Locations | Temporal Semantics | Conformance Status | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Realized PnL (event) | `PnLEngine.update()` | `PnLEngine` (ADR-005) | `CanonicalState.state["pnl"]` | `CanonicalState` (ADR-006) | `CanonicalEnforcer.apply_pnl()` | `RunLoop` (local var, feeds Equity), `PerformanceEngine.update()` | `PnLEngine` (compute); `CanonicalEnforcer` (publish) | `CanonicalState.state["pnl"]`; `PnLEngine.last_realized_pnl` (non-canonical, overwritten each call) | per-tick event value; `0.0` on non-closing ticks | Conformant | `pnl.py:9-40`; `loop.py:68-69`; `canonical_state.py:67-69` |
| Realized PnL (cumulative) | none exists | `PnLEngine` (ADR-005, ADR-006) | none exists | `CanonicalState` (ADR-006) | none exists | none exists | none exists | none exists; running-sum effect entangled inside `equity` | not implemented | Missing | `pnl.py` (no accumulator field); `loop.py:71` (addition performed outside `PnLEngine`, result stored as `equity` not as a distinct cumulative-PnL field) |
| Equity | `RunLoop.step()` (`loop.py:71`) | `PnLEngine` (ADR-005, ADR-006) | `CanonicalState.state["equity"]` | `CanonicalState` (ADR-006) | `CanonicalEnforcer.apply_equity()` | `RiskEngine.check()`; `RunLoop` (reads prior value); inactive: `PositionSizingEngine`, `EquityStabilizer` | `RunLoop` (compute); `CanonicalEnforcer` (publish); `CanonicalState.update_equity()` (peak side-effect) | `CanonicalState.state["equity"]` | cumulative running total, updated every tick unconditionally | Non-Conformant (Computational Authority) | `loop.py:71-72`; `canonical_state.py:60-65`; `risk.py:15` |
| Peak Equity | `CanonicalState.update_equity()` and, independently, `RiskEngine.check()` | `PnLEngine` (ADR-006) | `CanonicalState.state["peak_equity"]` | `CanonicalState` (ADR-006) | none dedicated (side effect of `apply_equity()`) | none reads `CanonicalState.state["peak_equity"]` directly except external result consumers (`main.py` print, `RunLoop`'s own return dict) | `CanonicalState.update_equity()`; `RiskEngine.check()` (separate, un-synchronized copy) | `CanonicalState.state["peak_equity"]`; `RiskEngine.self.peak_equity` (duplicate) | cumulative high-water mark since initialization; two trackers, no cross-check | Non-Conformant (duplicate Computational Authority; TD-006) | `canonical_state.py:64-65`; `risk.py:9-10,21-22,51`; `ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md` TD-006 |
| Drawdown | `RiskEngine.check()` | `RiskEngine`, from canonical financial state (ADR-006) | `CanonicalState.state["drawdown"]` | `CanonicalState` (ADR-006) | `CanonicalEnforcer.apply_risk()` | `PerformanceEngine` per Matrix (not implemented, Section 10); external result consumers | `RiskEngine` (compute); `CanonicalEnforcer` (publish) | `CanonicalState.state["drawdown"]` | recomputed every tick from `RiskEngine`'s own tracked Peak Equity | Non-Conformant (input source; TD-006) | `risk.py:24-25`; `canonical_state.py:73` |
| Drawdown Ratio | `RiskEngine.check()` | not explicitly named by any ADR (Open Question) | `CanonicalState.state["drawdown_ratio"]` | not explicitly named by any ADR (Open Question) | `CanonicalEnforcer.apply_risk()` | external result consumers only | `RiskEngine` (compute); `CanonicalEnforcer` (publish) | `CanonicalState.state["drawdown_ratio"]` | recomputed every tick alongside Drawdown | Partially Defined (ownership not ADR-named) | `risk.py:27-30`; `canonical_state.py:74` |

## 12. Current Financial Information Flow


Traced through `RunLoop.step()` (`run_engine/core/loop.py:33-97`):

1. `position_pre = self.cstate.get()["position"]` (step 6, unrelated to financial state, listed for sequence context).
2. `execution = self.execution_engine.execute(decision, position_pre)`.
3. `trade_event = self.trade_lifecycle_engine.on_execution(execution, state)`.
4. `lifecycle_position = self.trade_lifecycle_engine.current_position()`.
5. `position = self.position_engine.update_post_trade(execution, state, lifecycle_position); self.enforcer.apply_position(position)`.
6. `pnl = self.pnl_engine.update(trade_event, position_pre["entry_price"]); self.enforcer.apply_pnl(pnl)` - Realized PnL (event) computed and published.
7. `equity = self.cstate.get()["equity"] + pnl; self.enforcer.apply_equity(equity)` - Equity computed (by `RunLoop`, not `PnLEngine`) and published; Peak Equity side-effect occurs inside `CanonicalState.update_equity()` during this same call.
8. `canonical_state = self.cstate.get()`.
9. `risk = self.risk_engine.check(canonical_state, position, regime); self.enforcer.apply_risk(risk if isinstance(risk, dict) else {})` - Drawdown and Drawdown Ratio computed (from `RiskEngine`'s own internally-tracked Peak Equity, not from `canonical_state["peak_equity"]`) and published; `RiskEngine`'s own second Peak Equity tracker is also updated during this call.
10. `performance = self.performance_engine.update(decision, pnl, regime, trade_event); self.enforcer.apply_performance_metrics(performance)` - `PerformanceEngine` consumes the same tick-local `pnl` value already used in step 6/7.

This sequence matches ADR-010's mandated ordering (Financial Accounting precedes Risk Evaluation precedes Performance Evaluation) exactly, and matches the Target Information Flow diagram's `PnLEngine -> RiskEngine -> PerformanceEngine` ordering. The ordering itself is conformant; the ownership of the values flowing through it is not, for Equity, Peak Equity, and Drawdown (Sections 8 through 10).

## 13. Functional Problem Statement


Three distinct functional gaps exist, all within P2-03's stated Baseline objectives ("Implement PnLEngine ownership. Verify Realized PnL (cumulative). Verify Equity, Peak Equity and Drawdown consistency."):

**Gap 1 - PnLEngine is not yet the Computational Authority for Equity or Peak Equity.** ADR-005 and ADR-006 both explicitly and repeatedly assign Equity and Peak Equity computation to `PnLEngine`. The current runtime computes Equity inside `RunLoop.step()` and computes Peak Equity inside `CanonicalState.update_equity()` (with a second, independent computation inside `RiskEngine.check()`). `PnLEngine` itself has no knowledge of Equity or Peak Equity in any form. This is a direct, textual, repeated ADR non-conformance, not merely an unconsolidated read path.

**Gap 2 - No explicit cumulative realized PnL information object currently exists. The cumulative financial effect is presently represented implicitly through Equity.** ADR-005 names Realized PnL (cumulative) explicitly as one of five values `PnLEngine` must compute; ADR-006's Equity formula names it as one of three additive terms. The current runtime's cumulative effect is real (Equity does correctly accumulate PnL tick over tick) but is entirely implicit, entangled inside `Equity`'s own running total, with no separately-owned, separately-verifiable "Realized PnL (cumulative)" field anywhere. This is a capability-absence gap, matching the same shape already identified for Unrealized PnL by the P2-01 Capability Gap Analysis, not a partial implementation.

**Gap 3 - RiskEngine independently owns Peak Equity and computes Drawdown from it, contrary to ADR-006 and ADR-007.** This is TD-006, already logged, already confirmed unchanged through P2-02A's own certification (`docs/architecture/certification/P2_02A_FINAL_CERTIFICATION_V1_2026-07-10.md`, Section 21: "TD-006 ... unchanged, still OPEN, fully untouched"), and re-confirmed by direct code inspection in this document (Section 9, Section 10). Under the current synchronous execution model this produces no observable numeric divergence, but it is an unenforced coincidence, not an architectural guarantee, and it directly contradicts two separate ADRs (ADR-006's "RiskEngine SHALL calculate Drawdown exclusively from canonical financial state" and ADR-007's "RiskEngine SHALL never own: ... Equity, Peak Equity").

None of the three gaps requires reopening P2-04 (RiskEngine's own risk-limiting policy), TD-005 (automated regression suite), or the currently-inactive `PositionSizingEngine`/`EquityStabilizer`/`run_engine/runtime/` implementations - those remain distinct, separately-scoped, already-named concerns (Section 24).

## 14. Required Functional Capabilities


RC-1 - Exactly one Computational Authority (`PnLEngine`) for Realized PnL (event), Realized PnL (cumulative), Equity, and Peak Equity, consistent with ADR-005 and ADR-006's explicit assignment.

RC-2 - A canonical, separately-owned, separately-observable Realized PnL (cumulative) value, distinct from per-event Realized PnL and from Equity.

RC-3 - Exactly one canonical Equity value, deterministically consistent with its ADR-006-defined formula, owned by `CanonicalState`.

RC-4 - Exactly one canonical Peak Equity value, with no independently-tracked competing copy anywhere in the runtime (in particular, not inside `RiskEngine`).

RC-5 - `RiskEngine`'s Drawdown and Drawdown Ratio computation sourced exclusively from canonical financial state, with `RiskEngine` retaining no owned Equity or Peak Equity state of its own.

RC-6 - Preservation of every already-certified P1-03/P1-03.1/P1-04/P2-01/P2-02/P2-02A financial-adjacent contract (entry_basis pre-trade timing, weighted-average Scale-In entry price, RUNTIME_FAILURE_EVENT non-mutation of Realized PnL/Equity/Peak Equity/Drawdown/PerformanceEngine.stats, Position-Exposure separation) unless this unit's own governance chain explicitly re-certifies a change.

## 15. PnL Requirements


P2-03-FR-001 - `PnLEngine` SHALL remain the exclusive Computational Authority for Realized PnL (event); no other component SHALL compute the financial consequence of a `TRADE_CLOSED` or `PARTIAL_CLOSE` lifecycle event.

Scientific Rationale: Realized PnL (event) is already correctly and exclusively computed by `PnLEngine` (Section 7); this requirement records the already-conformant state so it is not silently regressed by later units.
Architectural Rationale: ADR-005, verbatim - "PnLEngine SHALL become the exclusive Computational Authority for financial accounting."
Existing Evidence: `run_engine/core/pnl.py:9-40`.
Validation Condition: repository-wide search confirms no component other than `PnLEngine` computes a `(exit_price - entry_price) * quantity`-shaped financial consequence.
Related ADR: ADR-005.
Related Technical Debt: none.
Scope Classification: in scope (P2-03); already satisfied, no implementation required for this specific requirement.

P2-03-FR-002 - `PnLEngine` SHALL become the exclusive Computational Authority for Realized PnL (cumulative), which SHALL exist as a canonical value separate from Realized PnL (event) and separate from Equity.

Scientific Rationale: ADR-005 names Realized PnL (cumulative) as a distinct value `PnLEngine` must compute; ADR-006's Equity formula treats it as a distinct additive term. Currently absent (Section 6, item 7; Section 13, Gap 2).
Architectural Rationale: ADR-005, ADR-006.
Existing Evidence: `run_engine/core/pnl.py` (no accumulator exists); `run_engine/core/loop.py:71` (cumulative effect entangled inside `equity` instead).
Validation Condition: a canonical Realized PnL (cumulative) value exists, is computed exclusively by `PnLEngine`, and its value at any tick equals the sum of every prior Realized PnL (event) value.
Related ADR: ADR-005, ADR-006.
Related Technical Debt: none directly logged; this capability's absence is a newly confirmed finding of this document.
Scope Classification: in scope (P2-03); this is the unit's Baseline-named objective ("Verify Realized PnL (cumulative)").

P2-03-FR-003 - `CanonicalState` SHALL be the exclusive Authoritative Owner of both Realized PnL (event) and Realized PnL (cumulative), each stored under its own distinct key, with no shared storage location and no implicit derivation of one from the other's absence.

Scientific Rationale: ADR-006 - "CanonicalState SHALL become the Authoritative Owner of all financial runtime state." Two distinct temporal semantics (per-event vs. cumulative) require two distinct storage locations to remain independently auditable.
Architectural Rationale: Rule OM-006, ADR-006.
Existing Evidence: `run_engine/core/canonical_state.py:32` (`"pnl": 0.0`, per-event only; no cumulative key exists).
Validation Condition: `CanonicalState.state` contains two distinct, independently-inspectable keys for event-PnL and cumulative-PnL.
Related ADR: ADR-006.
Related Technical Debt: none.
Scope Classification: in scope (P2-03).

P2-03-FR-004 - Event-PnL versus cumulative-PnL semantics SHALL remain explicitly distinguishable by every consumer; no consumer SHALL be required to infer cumulative PnL from Equity's own running total.

Scientific Rationale: conflating a per-tick event value with a running total inside a third concept (Equity) obscures both concepts' individual verifiability (Section 13, Gap 2).
Architectural Rationale: ADR-005/ADR-006's explicit five-value/three-term decomposition.
Existing Evidence: Section 7, Section 8 (current entanglement).
Validation Condition: a consumer can read cumulative Realized PnL without also reading or reconstructing Equity.
Related ADR: ADR-005, ADR-006.
Related Technical Debt: none.
Scope Classification: in scope (P2-03).

## 16. Equity Requirements


P2-03-FR-005 - `PnLEngine` SHALL become the exclusive Computational Authority for Equity; `RunLoop` SHALL NOT perform the Equity addition itself.

Scientific Rationale: ADR-005 - "PnLEngine computes: ... Equity"; ADR-006 - "PnLEngine SHALL become the exclusive Computational Authority for: ... Equity."
Architectural Rationale: currently violated by `run_engine/core/loop.py:71` (Section 8, Section 11); this is the single most severe finding in this document.
Existing Evidence: `run_engine/core/loop.py:71`; `run_engine/core/pnl.py` (no Equity-related method or attribute exists anywhere).
Validation Condition: `RunLoop.step()` no longer contains an Equity-computing expression; the value it publishes originates from a `PnLEngine` method call.
Related ADR: ADR-005, ADR-006.
Related Technical Debt: none directly logged; newly confirmed finding of this document.
Scope Classification: in scope (P2-03); central to the Baseline's own stated objective ("Verify Equity ... consistency").

P2-03-FR-006 - `CanonicalState` SHALL remain the exclusive Authoritative Owner of Equity.

Scientific Rationale: storage location is already conformant (Section 8); this requirement locks in the already-correct half of Equity ownership so that fixing FR-005 does not inadvertently relocate storage.
Architectural Rationale: ADR-006, Rule OM-006.
Existing Evidence: `run_engine/core/canonical_state.py:28,60-62`.
Validation Condition: `CanonicalState.state["equity"]` remains the sole storage location for canonical Equity after any Computational Authority change.
Related ADR: ADR-006.
Related Technical Debt: none.
Scope Classification: in scope (P2-03).

P2-03-FR-007 - Equity SHALL be recomputed whenever Realized PnL (cumulative) or Unrealized PnL changes, and SHALL be internally consistent with `Initial Capital + Realized PnL (cumulative) + Unrealized PnL` at every tick for which all three terms are defined.

Scientific Rationale: ADR-006's Equity formula and its explicit recomputation rule; AI-010 (Financial Consistency).
Architectural Rationale: currently Equity is recomputed every tick via incremental addition (Section 8), which is consistent with this rule only so long as Unrealized PnL remains `0.0` everywhere (its current, confirmed-absent state, Section 6 item 8) and Realized PnL (cumulative) is correctly tracked (FR-002).
Existing Evidence: `run_engine/core/loop.py:71`; AI-010 (`RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md`).
Validation Condition: for any tick, `Equity == Initial Capital + Realized PnL (cumulative) + Unrealized PnL`, verified by independent reconstruction from the three named terms, not merely by trusting the incremental running total.
Related ADR: ADR-006.
Related Technical Debt: none.
Scope Classification: in scope (P2-03), with the explicit caveat that Unrealized PnL remains `0.0`/absent unless a future document brings it into scope (Section 24).

## 17. Peak-Equity Requirements


P2-03-FR-008 - `PnLEngine` SHALL become the exclusive Computational Authority for Peak Equity; neither `CanonicalState` nor `RiskEngine` SHALL independently compute it.

Scientific Rationale: ADR-006 - "PnLEngine SHALL become the exclusive Computational Authority for: ... Peak Equity."
Architectural Rationale: currently violated in two separate locations (Section 9); this is TD-006's Peak-Equity half.
Existing Evidence: `run_engine/core/canonical_state.py:64-65`; `run_engine/core/risk.py:9-10,21-22,51`.
Validation Condition: exactly one code location computes Peak Equity, and that location is inside `PnLEngine`.
Related ADR: ADR-006, ADR-007.
Related Technical Debt: TD-006.
Scope Classification: in scope (P2-03); explicit Baseline objective ("Verify ... Peak Equity ... consistency").

P2-03-FR-009 - `RiskEngine` SHALL NOT own Peak Equity in any form, including as private, internally-tracked instance state used only for its own subsequent computation.

Scientific Rationale: ADR-007 - "RiskEngine SHALL never own: ... Equity, Peak Equity"; Rule OM-007 - "RiskEngine owns no runtime information. RiskEngine computes derived quantities only."
Architectural Rationale: `RiskEngine.self.peak_equity`/`self.last_equity` constitute ownership (a component-local, persisted-across-ticks source of truth that other code implicitly depends on) even though never published under those names - this is the precise distinction ADR-007 draws between "consuming" and "owning."
Existing Evidence: `run_engine/core/risk.py:9-10`.
Validation Condition: `RiskEngine` retains no instance attribute that independently tracks Equity or Peak Equity across calls to `check()`.
Related ADR: ADR-007.
Related Technical Debt: TD-006.
Scope Classification: in scope (P2-03).

## 18. Drawdown Requirements


P2-03-FR-010 - `RiskEngine` SHALL calculate Drawdown exclusively from canonical financial state (`CanonicalState`'s own Equity and Peak Equity), not from any internally-tracked copy.

Scientific Rationale: ADR-006, verbatim - "RiskEngine SHALL calculate Drawdown exclusively from canonical financial state."
Architectural Rationale: currently violated (Section 10); `RiskEngine` is the correct Computational Authority component but reads the wrong input source.
Existing Evidence: `run_engine/core/risk.py:24-25`.
Validation Condition: `RiskEngine.check()`'s Drawdown computation reads `state["peak_equity"]` (or an equivalent canonical-financial-state-derived value), not `self.peak_equity`.
Related ADR: ADR-006.
Related Technical Debt: TD-006.
Scope Classification: in scope (P2-03).

P2-03-FR-011 - `CanonicalState` SHALL remain the exclusive Authoritative Owner of Drawdown.

Scientific Rationale: storage location is already conformant (Section 10); this requirement locks in the already-correct half.
Architectural Rationale: ADR-006, Rule OM-006.
Existing Evidence: `run_engine/core/canonical_state.py:34,73`.
Validation Condition: `CanonicalState.state["drawdown"]` remains the sole storage location after any input-source correction.
Related ADR: ADR-006.
Related Technical Debt: none.
Scope Classification: in scope (P2-03).

P2-03-FR-012 - Drawdown Ratio's Computational Authority and Authoritative Owner SHALL be explicitly and consistently assigned by the governing Architecture document, since no current ADR names it independently.

Scientific Rationale: Section 5, Section 10, Section 28 - Drawdown Ratio is currently computed and stored alongside Drawdown, by the same component, but has no dedicated ADR-level definition distinguishing it from the general "Risk Metric" category.
Architectural Rationale: ADR-007's general Risk Metric framing plausibly covers it, but this document does not decide the question (no formula or ownership solution is anticipated here, per this document's own quality requirements).
Existing Evidence: `run_engine/core/risk.py:27-30`; `run_engine/core/canonical_state.py:36,74`; absence of "Drawdown Ratio" in ADR-006's Scientific Definitions and in the Runtime Ownership Matrix's row list.
Validation Condition: a future Architecture document explicitly states Drawdown Ratio's Computational Authority and Authoritative Owner.
Related ADR: ADR-006 (by proximity), ADR-007 (by category).
Related Technical Debt: none directly; adjacent to TD-006 only in the sense that both concern `RiskEngine`'s current Drawdown-adjacent computation.
Scope Classification: in scope (P2-03) as an open naming/ownership question; not yet resolved.

## 19. Consumer Boundary Requirements


P2-03-FR-013 - `RiskEngine` SHALL remain a strictly read-only consumer of canonical financial state for every value it does not itself own as a Risk Metric (i.e., Equity and Peak Equity as inputs); it SHALL NOT mutate, cache independently, or republish them under any financial-state-owning name.

Scientific Rationale: ADR-007 - "Risk Evaluation does not create runtime truth. Risk Evaluation derives quantitative metrics from already established runtime information."
Architectural Rationale: matches the already-certified P2-02A pattern for `RiskEngine`'s read-only consumption of Position-derived Exposure (`position_exposure = position.get("exposure", 0.0)`, `docs/architecture/certification/P2_02A_FINAL_CERTIFICATION_V1_2026-07-10.md`).
Existing Evidence: `run_engine/core/risk.py:12-58` (current read of `state.get("equity", ...)` is already read-only in mechanism, though the Peak-Equity ownership violation, FR-009, undermines the boundary in substance).
Validation Condition: `RiskEngine.check()` reads Equity/Peak Equity from its `state` parameter only, with no independent instance-level tracking surviving across calls.
Related ADR: ADR-007.
Related Technical Debt: TD-006.
Scope Classification: in scope (P2-03).

P2-03-FR-014 - `PerformanceEngine` SHALL remain a strictly read-only consumer of Realized PnL (event); it SHALL NOT independently compute, own, or duplicate any canonical Financial State value (Realized PnL cumulative, Equity, Peak Equity, Drawdown, Drawdown Ratio).

Scientific Rationale: ADR-008 - PerformanceEngine evaluates completed lifecycle outcomes, not financial state ownership; Rule OM-008 - "PerformanceEngine owns no operational runtime information."
Architectural Rationale: `PerformanceEngine.stats["*"]["pnl"]` is a distinct Performance Metric (a per-action running mean), already structurally distinct from canonical Financial State (Section 11); this requirement records the already-conformant boundary explicitly so it is not blurred by any P2-03 implementation choice.
Existing Evidence: `run_engine/core/performance.py:1-35` (no Equity/Peak-Equity/Drawdown reference anywhere).
Validation Condition: `PerformanceEngine` continues to receive Realized PnL (event) as an explicit parameter, never re-deriving it, and never gains an Equity/Peak-Equity/Drawdown-named field.
Related ADR: ADR-008.
Related Technical Debt: none.
Scope Classification: in scope (P2-03) as a boundary-preservation requirement; full PerformanceEngine redesign remains P3-03's scope (Section 24).

## 20. Failure and Invalid-State Requirements


P2-03-FR-015 - Rejected transitions (`RUNTIME_FAILURE_EVENT`) SHALL continue to leave Realized PnL (event), Realized PnL (cumulative), Equity, Peak Equity, Drawdown, and Drawdown Ratio unmodified, exactly as already certified for Realized PnL (event) and `PerformanceEngine.stats` in P1-04.

Scientific Rationale: ADR-011 - "Rejected transitions SHALL never: ... modify Equity, modify Realized PnL, modify Unrealized PnL, modify Performance."
Architectural Rationale: already correctly implemented for Realized PnL (event) (`PnLEngine.update()`'s `event_type` guard, Section 7) and `PerformanceEngine.stats` (`docs/architecture/certification/P1_04_FINAL_CERTIFICATION_V1_2026-07-09.md`, AC-003/AC-004); must be explicitly re-verified for the new Realized PnL (cumulative) field once it exists (FR-002), and for Equity/Peak Equity once their Computational Authority moves into `PnLEngine` (FR-005, FR-008), since a `RUNTIME_FAILURE_EVENT` tick still calls `RunLoop.step()`'s full sequence including the (to-be-relocated) Equity computation.
Existing Evidence: `run_engine/core/pnl.py:23-24` (existing guard); `run_engine/core/performance.py:8-9` (existing guard); `docs/architecture/certification/P1_04_FINAL_CERTIFICATION_V1_2026-07-09.md`.
Validation Condition: a scripted `RUNTIME_FAILURE_EVENT` tick (e.g. over-close or invalid-quantity rejection) produces byte-identical Realized PnL (cumulative)/Equity/Peak Equity/Drawdown/Drawdown Ratio values before and after the tick.
Related ADR: ADR-011.
Related Technical Debt: none.
Scope Classification: in scope (P2-03).

## 21. Determinism and Replay Requirements


P2-03-FR-016 - Financial values (Realized PnL event and cumulative, Equity, Peak Equity, Drawdown, Drawdown Ratio) SHALL remain deterministic and reproducible for identical lifecycle histories: identical input sequences SHALL always produce identical output sequences.

Scientific Rationale: ADR-005 Acceptance Criterion - "Financial values remain reproducible from identical lifecycle history"; ADR-006 Acceptance Criterion - "Financial state remains deterministic for identical lifecycle histories"; AI-005 (Deterministic Execution).
Architectural Rationale: any relocation of Equity/Peak-Equity computation into `PnLEngine` (FR-005, FR-008) must not introduce a new ordering dependency or hidden state relative to the current, already-deterministic (though non-conformant) behavior confirmed across the P1-03.1/P1-04/P2-01/P2-02A regression chain.
Existing Evidence: `docs/architecture/certification/P2_02A_FINAL_CERTIFICATION_V1_2026-07-10.md`, Section 16 (existing determinism evidence for the current, pre-P2-03 implementation).
Validation Condition: an identical scripted tick/decision sequence run twice produces functionally identical Realized-PnL/Equity/Peak-Equity/Drawdown/Drawdown-Ratio sequences.
Related ADR: ADR-005, ADR-006, AI-005.
Related Technical Debt: none.
Scope Classification: in scope (P2-03).

## 22. Reset and Initial-State Requirements


P2-03-FR-017 - A well-defined Initial Equity / Initial Capital value SHALL exist as a single, explicitly documented source, rather than as an undeclared literal independently duplicated across multiple components.

Scientific Rationale: ADR-006's Equity formula names "Initial Capital" as its own explicit term; a value that exists only as a repeated magic number cannot be independently verified or safely changed.
Architectural Rationale: currently duplicated, unlinked, in `CanonicalState.__init__` and `RiskEngine.__init__` (both hardcoded `100.0`), and additionally in the confirmed-inactive `EquityStabilizer.__init__` and `RiskLayer.__init__` (Section 6, item 9).
Existing Evidence: `run_engine/core/canonical_state.py:28,30`; `run_engine/core/risk.py:9-10`.
Validation Condition: exactly one source defines the Initial Capital value; every component that needs it derives it from that one source (or the need for a second copy is eliminated by FR-008/FR-009's Peak-Equity consolidation).
Related ADR: ADR-006.
Related Technical Debt: none directly; related in kind to TD-006's "undeclared, silent coupling" framing.
Scope Classification: in scope (P2-03).

P2-03-FR-018 - Reset semantics for all Financial State SHALL be complete and consistent: no runtime component holding financial-adjacent instance state (in particular `RiskEngine`, given FR-008/FR-009's disposition) SHALL retain stale values across a `CanonicalState.reset()` call.

Scientific Rationale: AI-010 (Financial Consistency) requires internal consistency "at all times," which a reset that only partially clears state would violate on the very next tick.
Architectural Rationale: currently, `CanonicalState.reset()` correctly restores its own `equity`/`peak_equity`/`pnl`/`drawdown`/`drawdown_ratio` defaults, but `RiskEngine` has no `reset()` method at all and would retain a stale `self.peak_equity` across any reset (Section 9); there is currently no active caller of `CanonicalState.reset()` anywhere in `run_engine/core` or `run_engine/main.py`, so this is a latent, not presently-triggered, defect.
Existing Evidence: `run_engine/core/canonical_state.py:101-106` (`reset()` exists); repository-wide search confirms no `reset()` method exists on `RiskEngine`, `PnLEngine`, or `PerformanceEngine`.
Validation Condition: after a full reset sequence, every component holding financial-adjacent state (canonical or instance-local) reports values consistent with a freshly-initialized runtime.
Related ADR: AI-010.
Related Technical Debt: none directly logged; newly confirmed finding of this document.
Scope Classification: in scope (P2-03), scoped narrowly to financial-adjacent state; `PerformanceEngine`'s own reset gap (Section 11) is recorded but not claimed as P2-03 scope, since it concerns Performance Metrics, not Financial State.

## 23. Compatibility Requirements


P2-03-FR-019 - Every already-certified P1-03/P1-03.1/P1-04/P2-01/P2-02/P2-02A contract that touches financial-adjacent behavior (the explicit `entry_basis` pre-trade handoff into `PnLEngine.update()`, weighted-average Scale-In entry price, the P1-04 `RUNTIME_FAILURE_EVENT` non-mutation contract for Realized PnL and `PerformanceEngine.stats`, and the P2-02A Position/Exposure separation, including `RiskEngine`'s already-certified read-only `position_exposure` consumption) SHALL continue to function exactly as certified, unless this unit's own governance chain explicitly re-certifies a change.

Scientific Rationale: Cluster-I-style compatibility constraint, established precedent from every prior P2-0x Functional Requirement Analysis in this governance chain.
Architectural Rationale: none of FR-002/FR-005/FR-008/FR-009/FR-010 require touching `run_engine/core/position.py`, `run_engine/core/trade_lifecycle.py`, or the `entry_basis` parameter shape; any implementation that does touch those files or that shape requires explicit justification at the Architecture stage.
Existing Evidence: `docs/architecture/certification/P1_03_1_FINAL_CERTIFICATION_V1_2026-07-09.md`; `docs/architecture/certification/P1_04_FINAL_CERTIFICATION_V1_2026-07-09.md`; `docs/architecture/certification/P2_02A_FINAL_CERTIFICATION_V1_2026-07-10.md`.
Validation Condition: full regression re-run of the P1-03.1/P1-04/P2-02A certified scenarios after any P2-03 implementation produces functionally identical results for every already-certified field.
Related ADR: ADR-011, ADR-004, ADR-009.
Related Technical Debt: none.
Scope Classification: in scope (P2-03) as a constraint layer, not a build target.

P2-03-FR-020 - Unrealized PnL and Mark-to-Market Equity valuation SHALL remain explicitly out of scope for P2-03 unless a future governing document (Scientific Dependency Analysis, Capability Gap Analysis, or Architecture) explicitly and formally brings them into scope; this document takes no position on whether they are required.

Scientific Rationale: ADR-006's Equity formula names "Unrealized PnL" as a term, creating a plausible textual argument that it is required for full ADR-006 conformance; the governing task's own scope-protection instructions simultaneously list it as excludable "sofern nicht bereits verbindlich vorgesehen" (unless already bindingly provided for).
Architectural Rationale: this tension is not resolved by this document (Section 28, Open Question); recording it as a scope-protected item prevents silent scope expansion while preserving the question for explicit future disposition.
Existing Evidence: Section 6 item 8 (confirmed absent); ADR-006's formula text (Section 3).
Validation Condition: any future document that brings Unrealized PnL into scope does so explicitly, with its own scientific definition and dependency analysis, not as an incidental side effect of an Equity or Peak-Equity fix.
Related ADR: ADR-006.
Related Technical Debt: none.
Scope Classification: explicitly protected against silent scope expansion; disposition deferred.

## 24. Explicit Non-Goals and Deferred Scope


- Full RiskEngine redesign, Risk Policy, and Position Sizing - P2-04's stated scope ("Verify Risk Metrics ownership. Validate deterministic RiskEngine behaviour."); not addressed here beyond the narrow Equity/Peak-Equity/Drawdown ownership boundary named in ADR-006/ADR-007 (FR-009, FR-010, FR-013).
- Full PerformanceEngine redesign - P3-03's stated scope ("Verify PerformanceEngine inputs. Validate Performance Metrics generation."); this document records only the consumer-boundary requirement (FR-014) and the observed reset gap (Section 11), neither of which requires redesigning `PerformanceEngine`'s own statistics model.
- Unrealized PnL, Mark-to-Market Portfolio Valuation - explicitly scope-protected (FR-020); not assumed required, not assumed excluded.
- Multi-Asset Accounting, Fees, Funding, Slippage, Tax Accounting - not named by ADR-005/ADR-006/ADR-007 or by the P2-03 Baseline objectives; no evidence found that any of these concepts exist anywhere in the active runtime; not pulled into scope.
- Persistence, Recovery - explicitly deferred by ADR-012 ("Persistence, Recovery and Schema Evolution are explicitly classified as Deferred Scope"); unaffected by this document.
- Tick-Complete Snapshot architecture beyond what is already implemented - ADR-010's existing 12-step sequence (Section 12) already correctly orders financial accounting before risk evaluation before performance evaluation before publication; no change to this ordering is implied by any requirement in this document.
- Repository cleanup - the five confirmed-inactive files identified in Section 4 (`equity_stabilizer.py`, `position_sizing.py`, `run_engine/runtime/pnl_engine.py`, `run_engine/runtime/risk.py`, `run_engine/runtime/performance_analytics.py`) are recorded as findings only; their classification (retain/integrate/archive/remove) belongs to Phase 6 Repository Consolidation, not P2-03.
- Automated regression test suite - TD-005, project-wide, unaffected; validation of any future P2-03 implementation will be manual/interactive, consistent with every prior unit's precedent.
- Drawdown Ratio's formula and ownership resolution itself (as opposed to the observation that it is currently undefined) - deferred to the Architecture stage (FR-012).
- Financial Events (ADR-002) as an implemented object - their absence is recorded (Section 11); whether P2-03 must introduce them is an explicit Open Question (Section 28), not decided here.
- No new architecture decision is proposed by this document. Section 13's three gaps and Sections 15 through 23's requirements describe what must become true; how (exact `PnLEngine` interface shape, exact Realized-PnL-cumulative storage key, exact mechanism for `RiskEngine` to read canonical Peak Equity, whether Financial Events are introduced) is explicitly deferred to the P2-03 Scientific Dependency Analysis, Capability Gap Analysis, Architecture, and Specification documents.

## 25. Functional Requirement Catalogue


P2-03-FR-001 - PnLEngine remains exclusive Computational Authority for Realized PnL (event); already conformant. Source: ADR-005.
P2-03-FR-002 - PnLEngine becomes exclusive Computational Authority for Realized PnL (cumulative), currently missing. Source: ADR-005, ADR-006.
P2-03-FR-003 - CanonicalState owns both Realized PnL (event) and (cumulative) under distinct keys. Source: ADR-006.
P2-03-FR-004 - Event-PnL and cumulative-PnL remain explicitly distinguishable to every consumer. Source: ADR-005, ADR-006.
P2-03-FR-005 - PnLEngine becomes exclusive Computational Authority for Equity; RunLoop no longer computes it. Source: ADR-005, ADR-006.
P2-03-FR-006 - CanonicalState remains exclusive Authoritative Owner of Equity. Source: ADR-006.
P2-03-FR-007 - Equity recomputed and internally consistent with Initial Capital + Realized PnL cumulative + Unrealized PnL. Source: ADR-006, AI-010.
P2-03-FR-008 - PnLEngine becomes exclusive Computational Authority for Peak Equity; no duplicate computation. Source: ADR-006.
P2-03-FR-009 - RiskEngine owns no Peak Equity, including as private instance state. Source: ADR-007, Rule OM-007.
P2-03-FR-010 - RiskEngine calculates Drawdown exclusively from canonical financial state. Source: ADR-006.
P2-03-FR-011 - CanonicalState remains exclusive Authoritative Owner of Drawdown. Source: ADR-006.
P2-03-FR-012 - Drawdown Ratio ownership explicitly assigned by a future Architecture document. Source: Section 5/10 finding.
P2-03-FR-013 - RiskEngine remains strictly read-only consumer of Equity/Peak Equity. Source: ADR-007.
P2-03-FR-014 - PerformanceEngine remains strictly read-only consumer of Realized PnL (event); no Financial State duplication. Source: ADR-008, Rule OM-008.
P2-03-FR-015 - RuntimeFailureEvent non-mutation extended to Realized PnL cumulative, Equity, Peak Equity, Drawdown, Drawdown Ratio. Source: ADR-011.
P2-03-FR-016 - Financial values remain deterministic and reproducible for identical lifecycle histories. Source: ADR-005, ADR-006, AI-005.
P2-03-FR-017 - Single, explicit Initial Capital / Initial Equity source, no undeclared duplication. Source: ADR-006.
P2-03-FR-018 - Complete, consistent reset semantics across all financial-adjacent state. Source: AI-010.
P2-03-FR-019 - All prior-certified financial-adjacent contracts preserved unless explicitly re-certified. Source: Cluster-I-style compatibility constraint.
P2-03-FR-020 - Unrealized PnL / Mark-to-Market Equity explicitly scope-protected, not assumed in or out of scope. Source: ADR-006, governing task scope protection.

## 26. ADR Traceability


| ADR | Related Requirements |
|---|---|
| ADR-002 (Event-Driven Runtime Evolution / Financial Events) | Section 11 (observation only, no FR mandates implementation) |
| ADR-004 (Position Represents Current Market Exposure) | FR-019 (compatibility preservation only) |
| ADR-005 (Profit and Loss Accounting) | FR-001, FR-002, FR-003, FR-004, FR-005, FR-016 |
| ADR-006 (Canonical Financial State Ownership) | FR-002, FR-003, FR-004, FR-005, FR-006, FR-007, FR-008, FR-010, FR-011, FR-012, FR-016, FR-017, FR-020 |
| ADR-007 (Risk Evaluation as a Pure Computational Layer) | FR-009, FR-012, FR-013 |
| ADR-008 (Performance Ownership) | FR-014 |
| ADR-009 (Partial Trade Closure and Position Netting) | FR-019 (compatibility preservation only) |
| ADR-010 (Deterministic Runtime Execution Ordering) | Section 12 (existing ordering already conformant; no new FR required) |
| ADR-011 (Runtime Failure Handling) | FR-015, FR-019 |
| ADR-012 (Persistence, Recovery, Schema Evolution) | Section 24 (deferred scope confirmation only) |
| AI-005 (Deterministic Execution) | FR-016 |
| AI-010 (Financial Consistency) | FR-007, FR-018 |
| Rule OM-006 (CanonicalState exclusively owns active runtime state) | FR-003, FR-006, FR-011 |
| Rule OM-007 (RiskEngine owns no runtime information) | FR-009, FR-013 |
| Rule OM-008 (PerformanceEngine owns no operational runtime information) | FR-014 |

All requirement-relevant ADRs and Invariants named in Section 3 are referenced by at least one requirement above or by an explicit Section 24/Section 11 scope note.

## 27. Technical-Debt Traceability


| Technical Debt Item | Status Before This Document | Relation to P2-03-FRA |
|---|---|---|
| TD-001 (Canonical Position Source for PnLEngine) | Resolved (P2-02A) | Not reopened; `entry_basis` handoff preserved unmodified (FR-019). |
| TD-002 (Unify `_safe_float` implementations) | Open, Target Phase 2 | Confirmed still outside this document's scope; `PnLEngine` has no `_safe_float` method of its own (confirmed by direct read of `run_engine/core/pnl.py`), so this item does not directly implicate P2-03's own file scope; not reopened or resolved here. |
| TD-003 (Document Pre-Trade Snapshot Dependency) | Partially Resolved (P2-02A recommendation, register not yet updated) | Not reopened; `entry_basis` timing preserved unmodified (FR-019). |
| TD-004 (Lifecycle-based Performance Evaluation) | Already Planned, Target P3 | Not reopened; `PerformanceEngine`'s decision-oriented statistics model is unaffected by this document's requirements (FR-014 preserves the current consumer boundary, does not redesign the statistics model). |
| TD-005 (Automated Regression Test Suite) | Open, Target Project-wide | Confirmed still outside this document's scope (Section 24); validation of any future P2-03 implementation remains manual. |
| TD-006 (RiskEngine Peak Equity and Drawdown Ownership Duplication) | Deferred, Target P2-03/P2-04 | Directly addressed by this document's central findings (Section 9, Section 10, Section 13 Gap 3) and by FR-008, FR-009, FR-010; this document does not resolve TD-006 (no architecture decision is made here), but confirms it is squarely within P2-03's scope, re-verifies it is unchanged at HEAD `815cd8a`, and provides the repository-grounded evidence a future Capability Gap Analysis and Architecture document will need to close it. |
| TD-007 (RunLoop Lifecycle Control Surface) | Deferred, Target future Runtime Control Unit | Unrelated to Financial Ownership; not referenced by any requirement in this document. |

No Technical Debt Register file edit is made by this document (register modification is out of scope for a Functional Requirement Analysis, consistent with every prior unit's practice).

## 28. Open Questions


OQ-001 - Is `PnLEngine`'s Realized PnL, once Equity/Peak-Equity ownership is relocated into it, tick-bound (as it is today) or does it require an internal cumulative accumulator, or should the cumulative value be reconstructed by `CanonicalState` from a stored running total published by `PnLEngine` each tick? The scientific requirement (FR-002) is clear that a cumulative value must exist and must be owned computationally by `PnLEngine`; the exact storage/computation mechanism is an Architecture-stage decision, not resolved here.

Blocking Effect: blocks any implementation of FR-002/FR-005/FR-007 until resolved.

OQ-002 - Should `PnLEngine` publish event-PnL and cumulative-PnL as two separate return values from one method call, as two separate methods, or as a single structured return object? Not resolved here; an interface-shape decision belongs to the Specification stage.

Blocking Effect: blocks Specification-stage interface design only; does not block the underlying ownership requirement.

OQ-003 - Is Equity a stored canonical quantity (as it is today, and as FR-006 requires it to remain) or should it become a deterministic computed projection derived on demand from Realized PnL (cumulative) and Unrealized PnL, mirroring the storage-versus-projection question P2-02A resolved for Exposure (Option C, stored-with-binding-reconstruction-rule)? Not resolved here.

Blocking Effect: conditionally blocks the exact shape of FR-005/FR-007's implementation; does not block the underlying Computational Authority requirement.

OQ-004 - Who is the Computational Authority for Equity, precisely, once relocated: does `PnLEngine.update()` itself compute and return an updated Equity value (requiring `PnLEngine` to receive the prior Equity as an input, mirroring how `PositionEngine` receives prior state), or does `PnLEngine` gain a dedicated `compute_equity()`-shaped method called separately by `RunLoop`? Not resolved here; this is the central architecture question this document's findings feed into.

Blocking Effect: blocking for FR-005 implementation; not blocking for this document's own conclusions, since the ownership violation itself is independently established regardless of the eventual interface shape.

OQ-005 - Who is the Computational Authority for Peak Equity, precisely: does `PnLEngine` compute it as a byproduct of its own Equity computation (natural, since Peak Equity is defined purely in terms of Equity's own history), or does it remain a `CanonicalState`-side comparison against a `PnLEngine`-supplied Equity value (as `CanonicalState.update_equity()` already does today, minus the `RiskEngine` duplicate)? Not resolved here.

Blocking Effect: blocking for FR-008 implementation.

OQ-006 - Must `RiskEngine.self.peak_equity` be removed entirely, or may it be retained as a transient, per-call-scoped local variable (no longer an instance attribute persisted across ticks) purely for internal computation convenience within a single `check()` invocation? Not resolved here; FR-009 requires no cross-tick ownership, which is compatible with either disposition.

Blocking Effect: blocking for FR-009/FR-010 implementation detail; not blocking for the underlying requirement.

OQ-007 - Is TD-006 fully P2-03's responsibility, or does its Drawdown-computation half belong partly to P2-04 ("Verify Risk Metrics ownership. Validate deterministic RiskEngine behaviour")? The Implementation Baseline's own Validation Traceability Matrix assigns ADR-006 to "Phase 2" generally (not specifically to P2-03 or P2-04) and ADR-007 likewise to "Phase 2"; the P2-01 Capability Gap Analysis explicitly recommended TD-006 for "P2-03 and P2-04" jointly. This document takes the position (consistent with the P2-03 Baseline objective's explicit text, "Verify Equity, Peak Equity and Drawdown consistency") that the Equity/Peak-Equity/Drawdown-input-source half of TD-006 is P2-03's responsibility (FR-008, FR-009, FR-010), while any change to `RiskEngine`'s own risk-limiting formula, `max_exposure`/`min_exposure`/`max_drawdown` policy, or regime-dampening logic remains P2-04's, but does not treat this position as a settled architecture decision.

Blocking Effect: conditionally blocking for the exact TD-006 closure boundary; the Capability Gap Analysis stage must confirm or adjust this positioning.

OQ-008 - Are Financial Events (ADR-002) a required deliverable of P2-03, given the Baseline objectives name only "PnLEngine ownership," "Realized PnL (cumulative)," and "Equity, Peak Equity and Drawdown consistency," none of which explicitly requires an event object? Not resolved here (Section 11).

Blocking Effect: conditionally blocking; if a future document determines Financial Events are required, this expands P2-03's (or a successor unit's) implementation footprint significantly beyond the four core ownership fixes.

OQ-009 - What is the correct Reset semantics for Realized PnL (cumulative) specifically: does a `CanonicalState.reset()` zero it unconditionally (mirroring `equity`'s reset to `100.0`), and does this imply Equity's post-reset value must also return to a fresh `Initial Capital` baseline consistent with FR-017's single-source requirement? Not resolved here (Section 22).

Blocking Effect: conditionally blocking for FR-018's exact implementation.

OQ-010 - Is there a documented, intentional reason `RiskEngine.check()`'s `state` parameter is named generically (rather than, for example, `canonical_state` or `financial_state`), given that `RunLoop` already binds it to the literal variable name `canonical_state` at the call site (`run_engine/core/loop.py:74,76`)? Purely a naming-clarity question, not a functional one; recorded for completeness, not blocking.

Blocking Effect: non-blocking.

OQ-011 - Should Drawdown Ratio be assigned its own P2-03-FR-level requirement number distinct from FR-012's "ownership TBD" framing once the Architecture stage resolves OQ for it, or does it remain permanently subsumed under the general "Risk Metrics" Matrix row? Not resolved here.

Blocking Effect: conditionally blocking for Specification-stage completeness only.

OQ-012 - Does `PositionSizingEngine`'s confirmed-inactive read of `state.get("equity", 100.0)` and `risk.get("exposure", 1.0)` require any forward-compatibility note analogous to the one already recorded for it in the P2-02A Architecture document (regarding its `risk.get("exposure", ...)` -> `risk.get("risk_allocation_factor", ...)` rename), given that this document's Equity/Peak-Equity ownership changes do not rename any `CanonicalState` key `PositionSizingEngine` currently reads? Preliminary answer: no rename is anticipated by any requirement in this document, so no forward-compatibility note is currently required; recorded as an Open Question only in case the eventual Architecture decision changes `CanonicalState`'s `"equity"` key name or shape.

Blocking Effect: non-blocking; conditional only on a future Architecture decision not currently anticipated.

## 29. Functional Readiness Decision


This analysis finds three confirmed, repository-grounded functional gaps (Section 13), all directly within P2-03's stated Baseline objectives, and one already-logged Technical Debt item (TD-006) directly and centrally implicated by two of the three gaps. All three gaps are localized to a small, already-understood set of files (`run_engine/core/pnl.py`, `run_engine/core/loop.py`, `run_engine/core/canonical_state.py`, `run_engine/core/risk.py`), consistent with the Implementation Baseline's own Phase 4 ("Financial Consolidation") primary-component list (`pnl.py`, `risk.py`, `canonical_state.py`).

No blocking ambiguity was found in the existing baseline text that would prevent proceeding: ADR-005 and ADR-006's Decision and Acceptance Criteria sections are unambiguous regarding Computational Authority assignment (`PnLEngine` for Realized PnL/cumulative/Equity/Peak Equity; `RiskEngine` for Drawdown, from canonical financial state only); only the exact interface shape (OQ-001 through OQ-006, OQ-009) and the Financial-Events and Unrealized-PnL scope questions (OQ-008, FR-020) require architecture-stage decisions, consistent with how every prior P2-0x unit in this governance chain has left comparable decisions to its own Architecture document.

Functional Readiness: READY. This document is sufficient to proceed to the P2-03 Scientific Dependency Analysis. No further repository investigation is required before that step.

## 30. Internal Consistency Review


Terminology consistency - "Realized PnL (event)," "Realized PnL (cumulative)," "Unrealized PnL," "Equity," "Peak Equity," "Absolute Drawdown," "Relative Drawdown / Drawdown Ratio," "Financial State," "Financial Event," "Financial Derived View," "Performance Metric," and "Risk Metric" are used exactly as defined in Section 5 throughout this document; no term is used ambiguously or interchangeably with another. "Byte-identical" is not used anywhere in this document to describe a Python-object or numeric comparison; where such a comparison is anticipated (Section 21, Section 23), "functionally identical" is used instead, consistent with the terminology rule established in `docs/architecture/certification/P2_02A_FINAL_CERTIFICATION_V1_2026-07-10.md`'s corrected terminology.

Ownership consistency - no requirement in Sections 18 through 26 assigns ownership of any concept to a component other than what ADR-005/ADR-006/ADR-007 or the Runtime Ownership Matrix already assigns. No new Authoritative Owner or Computational Authority is proposed; every requirement either restates an already-correct assignment (FR-001, FR-003, FR-006, FR-011) or names the ADR-mandated correction for an already-identified violation (FR-005, FR-008, FR-009, FR-010).

Scope consistency - every requirement traces to either ADR-005/006/007/008/011 text directly, a Section 6 through 13 repository finding, or an already-logged Technical Debt Register item explicitly targeted at P2-03 (TD-006). No requirement duplicates P2-04, P3-03, or Repository Consolidation scope; Section 24 explicitly excludes all three, along with Unrealized PnL/Mark-to-Market Valuation (FR-020), Persistence/Recovery (ADR-012), and the automated regression suite (TD-005).

Traceability consistency - Section 25's catalogue and Section 26's ADR mapping are cross-checked: all twenty functional requirements appear in exactly one catalogue row each; every ADR named in Section 3 as binding is referenced by at least one requirement or an explicit scope note.

Observation/requirement/decision separation - Sections 6 through 12 contain only observations, each with a direct file/line/method citation. Section 13 synthesizes those observations into a problem statement. Sections 15 through 23 contain only requirements derived from those observations plus the binding baseline. Section 28 contains only open questions explicitly deferred to a future Scientific Dependency Analysis, Capability Gap Analysis, or Architecture document; no architecture decision, formula selection, or interface shape is finalized anywhere in this document.

No fabricated capability - Realized PnL (cumulative), Unrealized PnL, and Financial Events are each explicitly and repeatedly documented as absent (Sections 6, 7, 8, 11) rather than described as existing in any partial or approximate form; no requirement in this document assumes a capability exists that repository inspection did not confirm.

Status: Internal Consistency Review PASS.
