Document Class:
Functional Requirement Analysis

Document ID:
P3-02-FRA

Version:
V1.0

Status:
Draft for Internal Review

Date:
2026-07-13

Project:
Trading-Bot Scientific Runtime

Subsystem:
Run Engine

Primary Location:
docs/architecture/analysis/P3_02_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-13.md

Depends On:
- docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md
- docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md
- docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md
- docs/architecture/analysis/P3_01_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-13.md
- docs/architecture/analysis/P3_01_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-13.md
- docs/architecture/analysis/P3_01_CAPABILITY_GAP_ANALYSIS_V1_2026-07-13.md
- docs/architecture/P3_01_DETERMINISTIC_EXECUTION_ORDERING_ARCHITECTURE_V1_2026-07-13.md
- docs/architecture/P3_01_DETERMINISTIC_EXECUTION_ORDERING_SPECIFICATION_V1_2026-07-13.md
- docs/architecture/certification/P3_01_FINAL_CERTIFICATION_V1_2026-07-13.md
- docs/architecture/P2_02A_POSITION_OWNERSHIP_ARCHITECTURE_V1_2026-07-10.md
- docs/architecture/P2_03_FINANCIAL_OWNERSHIP_ARCHITECTURE_V1_2026-07-11.md
- docs/architecture/P2_04_RISK_OWNERSHIP_ARCHITECTURE_V1_2026-07-13.md
- docs/architecture/certification/P2_03_FINAL_CERTIFICATION_V1_2026-07-11.md
- docs/architecture/certification/P2_04_FINAL_CERTIFICATION_V1_2026-07-13.md
- current runtime code at HEAD f6fb7f3911a978884ca10b22a0eef832a52f9486

Referenced By:
- future P3-02 Scientific Dependency Analysis
- future P3-02 Capability Gap Analysis
- future P3-02 Architecture

---

# P3-02 Information Flow Validation - Functional Requirement Analysis

## 1. Document Metadata

See front matter above. This document is the P3-02 Functional Requirement Analysis (FRA), the first stage of the P3-02 governance chain (FRA -> SDA -> CGA -> Architecture -> Specification -> Implementation -> Final Certification), mirroring the pipeline already completed for P3-01.

## 2. Purpose

This document identifies the functional requirements P3-02 (Information Flow Validation) must satisfy. It reconstructs the currently active runtime information flow, evaluates it against the Target Information Flow and Runtime Ownership Matrix of `RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md`, and against the Cross-Unit items P3-01 explicitly forwarded (CUO-01, and the general obligation to re-verify P3-01-AD-008, P3-01-AI-003, P3-01-AI-004, P3-01-AI-008, P3-01-AI-009, the P3-01 Cross-Unit Boundary Model, and the P3-01 Final Certification's own Findings and residual risks). It derives functional requirements, distinguishes them from Functional Gaps, Cross-Unit Observations, Verified Conformant Findings, Documentation Gaps, Verification Gaps, and Residual Risks, and records genuine Open Questions. It does not select a solution.

## 3. Scope

In scope: reference-versus-copy semantics of `CanonicalState.get()`; Canonical Working State internal visibility and isolation; Tick-Complete Snapshot object identity, stability, and external/internal observability; Producer-Consumer contracts for every Runtime Ownership Matrix row; Writer-on-Behalf-Of discipline at the information-flow level; semantic continuity and downstream reconstruction; Runtime Event integrity; Lifecycle History immutability and non-duplication; Position, Financial, Risk, and (current-state only) Performance information flow; direct mutation and aliasing; Failure and HOLD/No-Execution information flow; alternative/inactive information paths; traceability; deterministic information flow.

Out of scope, per the governing task and consistent with P3-01's own established boundary: the P3-01 execution-stage ordering itself (not reopened); Position/PnL/Risk formula or ownership changes (P2-02A/P2-03/P2-04, not reopened); Performance methodology redesign (TD-004, remains P3-03's); Persistence, Recovery, Schema Evolution (ADR-012, Deferred Scope); Operator Lifecycle Control (TD-007); parallel or asynchronous execution; concrete implementation, Python signatures, or file diffs; test specification; long-duration run execution.

## 4. Binding Baseline

- `docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md` - ADR-001 through ADR-012; the Runtime Ownership Matrix and Rules OM-001 through OM-009; the Target Information Flow, Principles IF-001 through IF-006, and Rules IF-001 through IF-006; the ownership taxonomy (Single Source of Truth, Authoritative Owner, Computational Authority, Writer-on-Behalf-Of, Canonical Storage, Derived View, Canonical Working State, Tick-Complete Snapshot); Architecture Invariants AI-001 through AI-015; Acceptance Criteria AC-001 through AC-013 (and further AC entries referenced by later sections of that document).
- `docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md` - Implementation Principles IP-001 through IP-006; the P3-02 unit definition ("Information Flow Validation - Remove hidden coupling. Validate Runtime Tick processing. Validate Market Observation processing.").
- `docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md` - TD-004 (Lifecycle-based Performance Evaluation, Target Phase P3) and TD-007 (RunLoop Lifecycle Control Surface, Target Phase Future Phase-2 Runtime Control Unit), both re-confirmed unmodified at this document's own repository verification (Section 5).
- `docs/architecture/analysis/P3_01_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-13.md`, `docs/architecture/analysis/P3_01_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-13.md`, `docs/architecture/analysis/P3_01_CAPABILITY_GAP_ANALYSIS_V1_2026-07-13.md`, `docs/architecture/P3_01_DETERMINISTIC_EXECUTION_ORDERING_ARCHITECTURE_V1_2026-07-13.md`, `docs/architecture/P3_01_DETERMINISTIC_EXECUTION_ORDERING_SPECIFICATION_V1_2026-07-13.md`, `docs/architecture/certification/P3_01_FINAL_CERTIFICATION_V1_2026-07-13.md` - the complete, certified P3-01 governance chain; the source of CUO-01 and every other P3-01 hand-over item this document re-examines (Section 8).
- `docs/architecture/P2_02A_POSITION_OWNERSHIP_ARCHITECTURE_V1_2026-07-10.md`, `docs/architecture/P2_03_FINANCIAL_OWNERSHIP_ARCHITECTURE_V1_2026-07-11.md`, `docs/architecture/P2_04_RISK_OWNERSHIP_ARCHITECTURE_V1_2026-07-13.md`, and their respective Final Certifications - the certified Position, Financial, and Risk ownership and information-flow contracts this document does not reopen.
- Current runtime code at HEAD `f6fb7f3911a978884ca10b22a0eef832a52f9486`, re-traced in full in Section 5 and Sections 7 through 24.

Methodological structure reference only, content not mechanically carried over: `docs/architecture/analysis/P3_01_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-13.md`.

## 5. Repository Verification

Repository state, verified directly, not assumed:

- Branch: `run-engine-consolidation-safety` (confirmed via `git branch --show-current`).
- Local HEAD: `f6fb7f3911a978884ca10b22a0eef832a52f9486`, matching the stated expected HEAD exactly.
- Remote HEAD: `f6fb7f3911a978884ca10b22a0eef832a52f9486`, identical to local HEAD (confirmed via `git fetch` followed by `git rev-parse origin/run-engine-consolidation-safety`).
- Working tree: one pre-existing, unrelated tracked modification (`docs/capabilities/SGF_013_SCIENTIFIC_BEHAVIOUR_REPRESENTATION_2026-06-26.md`) and a set of pre-existing untracked directories/files (`_chat_handover/`, `_sgf017_context/`, `_ssi_context/`, `backups/`, `claude_final_p1031_review/`, `claude_p1031_patch/`, `claude_p1_03b_review/`, `codex_p1_03_review/`, `engine/regime_classifier.py`, `live_logs/`, `outputs/`, `review_packages/`, `runtime_runs/`), none touched by this document's own drafting. `run_engine/` itself is clean.

Files re-read in full for this document: `run_engine/main.py`, `run_engine/core/loop.py`, `run_engine/core/state.py`, `run_engine/core/regime.py`, `run_engine/core/strategy.py`, `run_engine/core/decision.py`, `run_engine/core/execution/executor.py`, `run_engine/core/trade_lifecycle.py`, `run_engine/core/position.py`, `run_engine/core/pnl.py`, `run_engine/core/risk.py`, `run_engine/core/performance.py`, `run_engine/core/canonical_state.py`, `run_engine/core/canonical_enforcer.py`.

Additional active-path package structure confirmed: `run_engine/core/execution/__init__.py` (`from .executor import Executor`) - `run_engine/core/execution/` is a package, not a single file; its sole member is `executor.py`.

Repository-wide keyword search performed across `run_engine/` (all `.py` files, active and inactive) for the full keyword list the governing task specifies (`get(`, `return self.state`, `copy`, `deepcopy`, `dict(`, `mutation`, `mutate`, `side effect`, `shared reference`, `alias`, `reference`, `snapshot`, `Canonical Working State`, `Tick-Complete`, `publication`, `consume`, `consumer`, `producer`, `apply_`, `update_`, `lifecycle history`, `Runtime Event`, `Runtime Failure Event`, `state[`, `position[`, `risk[`, `performance[`, `execution`, `reconstruction`, `derive`, `hidden coupling`, `direct write`, `canonical`, `history`, `read-only`). Twenty-seven files matched at least one keyword: the fourteen active files listed above, plus thirteen files inside the four directories P3-01 already confirmed inactive (`run_engine/runtime/*`, `run_engine/execution/adapter.py`, `run_engine/execution/safety.py`, `run_engine/feedback/tracker.py`) and `run_engine/core/decision.py`.

An independent, static import-closure check (AST-based, re-derived for this document, not inherited from P3-01) confirms the fourteen active files import only each other and Python standard library / `numpy`; none imports from `run_engine/runtime/`, `run_engine/execution/` (top-level), `run_engine/feedback/`, `run_engine/logging/`, or `run_engine/core/decision.py`.

**New observation, not previously documented by P3-01.** Two additional files exist directly inside `run_engine/core/` - the same directory as the fourteen active files - that are referenced by no other file anywhere in `run_engine/`: `run_engine/core/position_sizing.py` (a `PositionSizingEngine` class) and `run_engine/core/state_modulation.py` (a `StateModulator` class, which internally uses Python's `random` module and is therefore non-deterministic by construction). Both are confirmed, via repository-wide text search for their own class and file names, to be imported nowhere. Unlike the four directories P3-01 Architecture Section 22 already classified as confirmed-inactive, these two files were not previously named in any P3-01 document, because they sit inside `run_engine/core/` itself rather than in a separately-named inactive directory. This is recorded as Documentation Gap DG-001 (Section 26).

`CanonicalState.get()` re-read verbatim: `def get(self): return self.state` - a direct return of the live internal dictionary, confirmed unchanged since P3-01's own re-verification.

## 6. Scientific Definitions

Restated, not newly invented, from `RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md` and the certified P3-01 governance chain, and binding for the remainder of this document:

**Single Source of Truth, Authoritative Owner, Computational Authority, Writer-on-Behalf-Of, Canonical Storage, Derived View, Canonical Working State, Tick-Complete Snapshot** - as defined in the Architecture Baseline's own ownership-taxonomy section.

**Hidden Coupling** (used descriptively in this document, not separately defined by the Baseline) - a dependency between two runtime components that is not represented by an explicit Runtime Event, an explicit Producer-Consumer contract in the Runtime Ownership Matrix, or an explicit parameter, but instead arises from shared mutable object identity (aliasing), from a component reading another component's private instance state, or from a component reconstructing information already produced elsewhere.

**Aliasing** (used descriptively in this document) - the condition in which two or more references (variables, container entries, or returned values) refer to the identical, mutable Python object, such that a mutation performed through one reference becomes observable through every other reference to the same object.

**Object-Identity Isolation** (used descriptively in this document) - the property that a value handed to a consumer or returned to a caller is not the same object as any value CanonicalState (or any other producer) will later mutate or reassign; equivalently, that later mutation of canonical state cannot become observable through a previously-returned reference.

**Functionally identical** is used in this document exclusively for Python-object, dictionary, and runtime-result comparisons. **Byte-identical** is reserved exclusively for file-, git-blob-, or byte-sequence-level comparisons; this document performs no such comparison, and the term therefore does not occur elsewhere in this document as a comparison claim.

## 7. Active Information Flow

Re-traced directly from `run_engine/core/loop.py:33-113` (`RunLoop.step()`), confirmed identical in stage order to the twelve-stage sequence P3-01-AD-001 ratifies (not reopened here):

1. `self.enforcer.apply_runtime_status("RUNNING")`.
2. `state = self.state_engine.update(tick)`.
3. `self.cstate.update_tick(runtime_tick, price)` - a direct write, Matrix-conformant per P3-01-AD-002 (Runtime Tick's own explicit exception).
4. `regime = self.regime_classifier.classify(state)`; `self.enforcer.apply_regime(regime)` - via `CanonicalEnforcer`, per the P3-01 Implementation.
5. `position_pre = self.cstate.get()["position"]` - a direct, unmediated read of `CanonicalState`'s own internally held Position object.
6. `weights = self.strategy_selector.select(state, regime, position_pre)`; `self.enforcer.apply_strategy_selection(weights)`.
7. `decision = self.strategy_selector.decide(state, regime, weights)`; `self.enforcer.apply_execution_decision(decision)`.
8. `execution = self.execution_engine.execute(decision, position_pre)`.
9. `trade_event = self.trade_lifecycle_engine.on_execution(execution, state)`.
10. `lifecycle_position = self.trade_lifecycle_engine.current_position()`.
11. `position = self.position_engine.update_post_trade(execution, state, lifecycle_position)`; `self.enforcer.apply_position(position)`.
12. `pnl = self.pnl_engine.update(trade_event, position_pre["entry_price"])`; `self.enforcer.apply_pnl(pnl)`.
13. `equity_state = self.pnl_engine.compute_equity(trade_event, pnl, prior_realized_pnl_cumulative, prior_equity, prior_peak_equity)`; `self.enforcer.apply_realized_pnl_cumulative(...)`, `apply_equity(...)`, `apply_peak_equity(...)`.
14. `canonical_state = self.cstate.get()` - a direct, unmediated read of the complete internal state dictionary.
15. `risk = self.risk_engine.check(canonical_state, position, regime)`; `self.enforcer.apply_risk(risk if isinstance(risk, dict) else {})`.
16. `performance = self.performance_engine.update(decision, pnl, regime, trade_event)`; `self.enforcer.apply_performance_metrics(performance)`.
17. `return {"tick": ..., "state": self.cstate.get(), "regime": ..., "decision": ..., "execution": ..., "trade_event": ..., "lifecycle_position": ..., "active_trade": ..., "position": ..., "risk": ..., "pnl": ..., "equity": ..., "performance": ..., "strategy_weights": ...}` - the Tick-Complete result dictionary, itself freshly constructed each call, but several of its own values are, per Sections 12-14, not freshly constructed.

`run_engine/main.py`'s own active caller does not retain any returned value beyond one `print(result)` statement per tick; `result` is reassigned, not accumulated, on each loop iteration. This is a repository-grounded fact material to Sections 12, 13, and 24: the currently active caller's own usage pattern does not itself exercise cross-tick reference retention, even where the underlying objects would permit an external caller to do so.

## 8. P3-01 Hand-Over Re-Examination

Per the governing task's own explicit instruction, the following P3-01 items are re-examined, not silently inherited:

**CUO-01.** P3-01 Architecture Section 10 and Section 22 (AD-010) explicitly forwarded `CanonicalState.get()`'s own reference-versus-copy semantics to P3-02, without deciding it. This document re-confirms, via direct source re-reading (Section 5) and direct empirical demonstration (Section 12), that `get()` still returns a live, mutable reference to `CanonicalState`'s own internal `self.state` dictionary, unchanged since P3-01. CUO-01 is no longer merely observed; it is now within this unit's own resolution scope, and this document accordingly treats its unresolved read-contract as a Functional Gap of P3-02 (FR-001, Section 26), not as an externally-forwarded observation to be repeated unchanged.

**P3-01-AD-008 (Stage Traceability).** Re-verified: every one of the twelve stages listed in Section 7 remains traceable, by file and line, to the runtime object it consumes and the runtime object it produces. This document's own traceability obligation (Section 21, Section 32) extends this file/line traceability to include object-identity and mutation status per object, which P3-01-AD-008 did not itself require.

**P3-01-AI-003 (No Future-Stage Consumption).** Re-verified: no component in the current trace consumes a Canonical Working State value corresponding to a stage not yet reached in the current tick.

**P3-01-AI-004 (No External Intermediate Observation).** Re-verified at the structural level P3-01 already checked (no concurrency construct, no generator/yield in `step()`). This document's own Section 12 and Section 13 identify a distinct concern P3-01-AI-004 does not itself cover: whether a value returned only after Tick Completion can, once returned, still be silently mutated by a later tick - a question about post-return isolation, not about intermediate observation during the same tick.

**P3-01-AI-008 (No Hidden Mutable Ordering State).** Re-verified with respect to stage ordering itself: no stage-ordering decision in the current trace depends on hidden mutable state. This document's Section 13 identifies cross-tick private instance state in `PositionEngine` (and, less critically, in `RegimeClassifier`, `StrategySelector`, and `PnLEngine`) that is legitimate per P2-02A's own already-certified reading (Section 9 below) but is not itself an ordering dependency; P3-01-AI-008's own scope (ordering) is therefore not violated, while a related but distinct information-flow question (self-consistency of that private state) is opened as FR-013.

**P3-01-AI-009 (No Unauthorized Writer-on-Behalf-Of Path).** Re-verified via a repository-wide, scope-corrected search (Section 5 methodology, Section 20): exactly one `update_regime(` call site remains inside `canonical_enforcer.py`; every other `CanonicalState.state` mutation likewise occurs only through a named `CanonicalEnforcer.apply_*` method or through Runtime Tick's own explicit Matrix exception (`update_tick`, `loop.py:42`).

**P3-01 Cross-Unit Boundary Model (Architecture Section 23, AD-010).** Re-confirmed unchanged: CUO-01 (now resolved into this document's own scope per above), `PerformanceEngine`'s internal accounting semantics together with TD-004 (Section 19, forwarded to P3-03, not redesigned here), and TD-007 (not addressed here) remain exactly as P3-01 left them.

**P3-01 Final Certification Findings and Residual Risks.** The P3-01 Final Certification (`docs/architecture/certification/P3_01_FINAL_CERTIFICATION_V1_2026-07-13.md`) recorded Finding F-001 (informational, scope-clarification, concerning untracked review/backup directories, not part of the active runtime, not re-examined here as it is unrelated to information flow) and classified Post-Exception Financial/Lifecycle Divergence as a non-blocking documented residual risk. This document re-examines the latter at the information-flow level in Section 21 and identifies a related, but distinct, second instance of the same general pattern (Section 13, FR-013): a divergence between `PositionEngine`'s own private cross-tick state and `CanonicalState`'s own published Position, following an unhandled exception during Position Update. This document does not resolve either divergence; it documents the newly-identified instance with the same discipline P3-01 applied to the first.

## 9. Runtime Object Inventory

Every runtime information object the Runtime Ownership Matrix names, re-confirmed present in the active trace (Section 7), plus two objects the Matrix does not itself name but which this document's own analysis requires distinguishing:

| Object | Matrix Row | Producer (active code) | Container Shape |
|---|---|---|---|
| Runtime Tick | Runtime Tick | `RunLoop` (`state_engine.update`, `cstate.update_tick`) | scalar (`tick`, `price`) |
| Normalized Runtime State | Normalized Runtime State | `StateEngine.update` | freshly-constructed dict, returned, not stored in `CanonicalState` |
| Market Regime | Market Regime | `RegimeClassifier.classify` | scalar string |
| Strategy Selection | Strategy Selection | `StrategySelector.select` | freshly-constructed dict |
| Execution Decision | Execution Decision | `StrategySelector.decide` | freshly-constructed dict |
| Execution Event | Execution Event | `Executor.execute` | freshly-constructed dict |
| Trade Identifier, Lifecycle State, Entry Facts, Exit Facts, Lifecycle History, Runtime Failure Event | (six Matrix rows) | `TradeLifecycleEngine` | `LifecycleEvent` (frozen dataclass) and `Trade` (mutable dataclass), both `TradeLifecycleEngine`-internal |
| Position | Position | `PositionEngine.update_post_trade`/`project`/`_set_flat` | freshly-constructed dict per call (Section 12) |
| Realized PnL, Unrealized PnL (as `pnl`), Equity, Peak Equity | (four Matrix rows) | `PnLEngine.update`/`compute_equity` | scalar float; `compute_equity` additionally returns a freshly-constructed dict |
| Drawdown, Risk Metrics (as `drawdown_ratio`, `risk_allocation_factor`) | Drawdown, Risk Metrics | `RiskEngine.check` | freshly-constructed dict of scalars |
| Runtime Status | Runtime Status | `RunLoop` via `CanonicalEnforcer.apply_runtime_status` | scalar string |
| Performance Metrics | Performance Metrics | `PerformanceEngine.update` | **the same dict object, `self.stats`, returned and mutated in place on every call** (Section 12) |
| Tick-Complete CanonicalState Snapshot | Tick-Complete CanonicalState Snapshot | `RunLoop.step`'s own `return` statement | freshly-constructed outer dict; its own `"state"` value is `CanonicalState`'s live internal `self.state` object, not a copy (Section 12) |
| PositionEngine private cross-tick state (not a Matrix row; internal Computational Authority working state per P2-02A Section 13) | n/a | `PositionEngine.__init__`, mutated by `update_post_trade` | six scalar instance attributes, mutated sequentially, not atomically (Section 13) |

## 10. Producer-Consumer Analysis

For every Matrix row exercised by the active trace, Producer and Primary Consumer match the Runtime Ownership Matrix exactly (re-confirmed by direct trace, Section 7). No additional Consumer beyond those the Matrix names was found to read any of these objects in the active path. Two observations qualify this conformant finding without contradicting it:

**Permitted and forbidden mutations are not structurally enforced.** Rule OM-004 ("Primary Consumers shall never modify consumed information") is stated as a normative rule, not as a structural guarantee; every consumed object in the active trace is an ordinary mutable Python `dict` (or, for Position/Strategy Selection/Execution Decision/Execution Event, freshly-constructed dicts passed by reference), and no consumer-side read-only wrapper, `MappingProxyType`, immutable dataclass, or copy-on-read mechanism exists anywhere in the active path. Direct inspection of every consumer (`StrategySelector.select`/`decide`, `Executor.execute`, `TradeLifecycleEngine.on_execution`, `PositionEngine.update_post_trade`, `PnLEngine.update`/`compute_equity`, `RiskEngine.check`, `PerformanceEngine.update`) found no in-place mutation of a received parameter in the current code; this is a currently-conformant observed behaviour, not a structurally-guaranteed one (Section 26, FR-017).

**`CanonicalEnforcer`'s own return-value contract is internally inconsistent.** Ten of `CanonicalEnforcer`'s eleven `apply_*` methods return the single canonical value they just wrote or confirmed (for example, `apply_pnl` returns `self.cs.get()["pnl"]`). `apply_risk` is the sole exception: it returns `self.cs.get()` - the complete, live `CanonicalState.state` dictionary, not a single key. In the active trace, this return value is discarded (`self.enforcer.apply_risk(risk if isinstance(risk, dict) else {})`, no assignment), so this inconsistency currently has no observable runtime consequence, but it is a genuine deviation from the otherwise-uniform `apply_*` contract shape (Section 26, FR-007).

## 11. Canonical Working State Analysis

Canonical Working State (the in-progress, internally-accumulating `CanonicalState.state` during one tick) is consumed internally, at its assigned execution stage, by exactly one component in the active trace: `RiskEngine.check`, via `canonical_state = self.cstate.get()` at `loop.py:90`, matching the Baseline's own statement that "RiskEngine and PerformanceEngine consume the Canonical Working State at their assigned execution stage" (though `PerformanceEngine.update` in the active trace does not itself receive `canonical_state`; it receives `decision`, `pnl`, `regime`, and `trade_event` directly - see Section 19). No component consumes Canonical Working State from a stage not yet reached (re-confirmed, Section 8). No external caller can observe Canonical Working State, since `RunLoop.step()` performs no yield and no intermediate return (re-confirmed, Section 8, inheriting P3-01's own structural check). This finding is currently evidenced.

## 12. Reference and Copy Semantics

This is the central technical analysis of this document, empirically re-derived, not merely asserted, using the currently active runtime (`RunLoop`, unmodified).

**`CanonicalState.get()` returns a live reference, confirmed by direct object-identity comparison.** `id(engine.cstate.get())` is identical across every call for the lifetime of one `CanonicalState` instance (until `reset()`, which calls `self.__init__()` and constructs a genuinely new dictionary). `get()` performs no copy of any kind - not a shallow copy, not a deep copy, not a `MappingProxyType` read-only view.

**The Tick-Complete result's own `"state"` field aliases `CanonicalState`'s internal dictionary, empirically confirmed.** A tick-result dictionary returned by `RunLoop.step()` has, at its own `"state"` key, the identical object (`is`, not merely `==`) as `engine.cstate.state`. A caller that stores `snapshot = engine.step(tick_0)["state"]` and later calls `engine.step(tick_1)` observes `snapshot["tick"]` silently change from `0` to `1`, without the caller re-reading anything - the previously-returned "Tick-Complete Snapshot" is not a point-in-time snapshot at all with respect to its own top-level container; it is a live window into whatever `CanonicalState` currently holds. This was directly reproduced and independently confirmed during this document's own drafting.

**Nested value objects currently behave differently from the top-level container, but not by structural guarantee.** A captured reference to the nested `"position"` value (`snapshot["position"]`) does *not* silently change after a subsequent tick, because `PositionEngine`'s own `snapshot()` method (Section 9) constructs a genuinely new dictionary literal on every call, and `CanonicalState.update_position()` reassigns the `"position"` key to this new object rather than mutating the previous one in place - so the previous object, once orphaned by reassignment, is never touched again. This was directly reproduced and confirmed: the captured nested Position object remains stable across a subsequent tick, and its own object identity differs from the newer tick's own Position object. This currently-conformant behaviour depends entirely on every producer's own discipline of always constructing a fresh object at publication time; no contract, type system, or runtime check enforces it, and one exception to this discipline already exists (Performance Metrics, below).

**`Performance Metrics` is not swapped; it is mutated in place, on the same object, on every tick, empirically confirmed.** `PerformanceEngine.__init__` constructs `self.stats = {}` exactly once. `PerformanceEngine.update()` mutates `self.stats[action]['trades']`, `self.stats[action]['pnl']`, and `self.stats[action]['winrate']` in place (or inserts a new inner dict for a not-yet-seen `action`) and then `return self.stats` - the identical outer dictionary object, every single call. Direct object-identity comparison confirms `id(engine.performance_engine.stats)` equals both the `"performance"` value in every tick-result dictionary and `CanonicalState.state["performance_metrics"]`, for the entire lifetime of the `PerformanceEngine` instance. A caller holding a reference to any prior tick's own `"performance"` (or `"performance_metrics"`) value observes every later tick's own mutations through that same reference, without re-reading anything. This is empirically confirmed and is a materially more severe aliasing case than the top-level `"state"` container, because it is never even nominally reassigned - it is the same object, continuously mutated, for the entire runtime session.

**`Risk Metrics` and every scalar canonical value are structurally immune to aliasing.** `drawdown`, `drawdown_ratio`, `risk_allocation_factor`, `tick`, `price`, `regime`, `pnl`, `realized_pnl_cumulative`, `equity`, and `peak_equity` are Python `float`/`str`/`int`/`None` values, which are immutable by language construction; no aliasing concern applies to them regardless of how they are stored, copied, or referenced.

**Currently observed practical impact.** The single active caller, `run_engine/main.py`, does not retain any returned value beyond one `print()` statement per tick (Section 7); no currently-active code path exercises the aliasing behaviour described above in a way that produces an observably incorrect result today. The aliasing is a structural, empirically-demonstrated property of the current implementation, not (currently) an observed production defect, since no current caller retains cross-tick references. This qualification does not reduce the property's own severity as a Functional Gap (Section 26, FR-003, FR-004); it only bounds its currently-observed consequence.

## 13. Mutation and Aliasing Analysis

**Consumer-side mutation of received parameters.** Not found in the active trace (Section 10); every consumer reads without writing back into the object it received. This is currently evidenced, not structurally enforced.

**`RunLoop`'s own mutation of engine-produced objects.** Not found; `RunLoop.step()` reads return values and forwards them as arguments; it does not itself mutate any dict or dataclass instance it receives from an engine.

**Engine-internal mutation of inputs.** Not found for `StateEngine`, `RegimeClassifier` (mutates only its own private `deque` instances, not its `state` parameter), `StrategySelector` (mutates only its own private `weights`/`last_action`/`cooldown` instance attributes; `update()`, the one method that mutates `self.weights`, is never called by `RunLoop.step()` in the active trace - `StrategySelector.select()`'s own output is therefore, in the currently active runtime, a pure function of `regime` and `position`, since `self.weights` never departs from its `__init__`-assigned values), `Executor`, `TradeLifecycleEngine` (mutates only its own `Trade`/`self.trades`/`self.active_trade` state, consistently with its own Authoritative Owner role), `PnLEngine` (mutates only its own `self.last_realized_pnl`, which is written but never read by any call site in the active trace - a write with no active consumer), or `RiskEngine` (confirmed, and already certified by P2-04, stateless beyond its three fixed Risk Policy Configuration attributes).

**`PositionEngine`'s own cross-tick private state can reach an internally self-inconsistent value after an interrupted computation - empirically confirmed, newly identified by this document.** `PositionEngine.update_post_trade` mutates six of its own instance attributes (`entry_price`, then `position`, `side`, `quantity`, `last_price`, then `exposure`, in that order) sequentially, each a separate Python statement, with no rollback, transaction, or atomicity guarantee across them, before finally returning a freshly-constructed snapshot dict (Section 12) that `RunLoop` then publishes via `CanonicalEnforcer.apply_position`. This document constructed and executed a direct probe: an exception was injected at the final mutating statement (`self.exposure = self._compute_exposure(...)`), after `entry_price`, `position`, `side`, `quantity`, and `last_price` had already been reassigned to the current tick's own new values, but before `exposure` was recomputed to match them. The result, directly observed: `PositionEngine`'s own private instance state ended the tick with `quantity` and `last_price` reflecting the new tick, `exposure` reflecting the *previous* tick's own now-stale value (no longer the correct product of the new `quantity` and `last_price`), and `CanonicalState`'s own published Position entirely unaffected (the tick's own `apply_position` call never executed, since the exception propagated out of `RunLoop.step()` before reaching it, producing a Failed Tick per P3-01-AD-004). On the following tick, `PositionEngine` would resume computation from this internally self-inconsistent private state, since nothing external to `PositionEngine` re-derives or validates its own instance attributes from `CanonicalState`'s own published Position. This is a distinct instance of the same general pattern P3-01 Architecture Section 18 named for `TradeLifecycleEngine` versus `CanonicalState` (Post-Exception Financial/Lifecycle Divergence), affecting a different pair of representations (`PositionEngine`'s own private state versus `CanonicalState`'s own published Position) and, additionally, an internal self-inconsistency *within* `PositionEngine`'s own private state alone, which the original named condition does not describe. P3-01 Architecture Section 19 named only `RegimeClassifier`'s and `StrategySelector`'s own cross-tick instance state as not reconciled after a Failed Tick; `PositionEngine`'s own cross-tick instance state was not named there, and this document's own probe demonstrates it is subject to a comparable, and in one respect more specific (internal field-to-field self-inconsistency, not merely staleness relative to `CanonicalState`), risk.

**`RegimeClassifier`'s own cross-tick private state (`market_window`, `regime_history` deques).** Re-confirmed present, consistent with P3-01's own citation; not independently re-probed for partial-mutation risk in this document, since P3-01 Architecture Section 19 already named it and no new evidence contradicts or extends that citation.

## 14. Writer-on-Behalf-Of Analysis

Every `CanonicalState.state` mutation in the active trace is re-confirmed to occur exclusively through one of `CanonicalEnforcer`'s eleven named `apply_*` methods, with the single, explicitly Matrix-named exception of Runtime Tick (`RunLoop`'s own direct `self.cstate.update_tick(...)` call, `loop.py:42`, unchanged since P3-01-AD-002). A scoped repository-wide search (Section 5 methodology, restricted to `run_engine/`) finds exactly one call site for each `CanonicalState.update_*` method, and every one of those call sites is inside `canonical_enforcer.py` except `update_tick`, whose sole call site is `loop.py:42`. No additional, previously-unknown direct write path was found. This is currently evidenced. `CanonicalEnforcer`'s own internal return-value inconsistency (`apply_risk`, Section 10) is a Publication-contract consistency concern, not a Writer-on-Behalf-Of exclusivity concern; the two are recorded separately (Section 26, FR-006 and FR-007).

## 15. Runtime Event Analysis

Explicit `LifecycleEvent` instances (`TRADE_OPENED`, `SCALE_IN`, `PARTIAL_CLOSE`, `TRADE_CLOSED`, `RUNTIME_FAILURE_EVENT`) are the only Runtime Event-shaped objects the active trade-lifecycle path produces; each `LifecycleEvent` is a frozen (`@dataclass(frozen=True)`) dataclass, structurally immutable once constructed, re-confirmed by direct source reading. Each event carries exactly one `event_type` and is generated at exactly one call site within `TradeLifecycleEngine` (`_open_trade`, `_scale_in`, `_partial_close`, `_full_close`, `_failure_event`, respectively); no code path constructs two different event types from one method, and no code path mutates an already-constructed `LifecycleEvent` (structurally prevented by `frozen=True`). This matches AI-008 ("Every runtime state transition SHALL originate from one explicit Runtime Event... implicit runtime mutations are prohibited") and is currently evidenced for the lifecycle layer specifically. The Baseline's own broader event model (ADR-002: Observation, Decision, Execution, Trade Lifecycle, Financial, Risk, and Performance Events as named categories) is realized only partially as literal, discrete event objects in the active runtime: Decision, Financial, Risk, and Performance "events" exist in the active trace only as plain return values (dicts or scalars) passed directly between stages and published via `CanonicalEnforcer`, not as any named event class or structure distinct from the published value itself. This is not treated as a Functional Gap in this document, since P3-01's own SDA and Architecture already examined and ratified this exact ordering and publication mechanism without requiring a distinct event-object representation for these layers (P3-01-AD-001, citing the observable-versus-structural normativity principle); it is recorded here only as a factual, currently-evidenced observation relevant to this unit's own "Explicit Runtime Events" theme.

## 16. Lifecycle History Analysis

`TradeLifecycleEngine.trades` (a `List[Trade]`) and `TradeLifecycleEngine.failure_events` (a `List[LifecycleEvent]`) remain the sole storage location for historical lifecycle facts; `CanonicalState.state` contains no key duplicating any lifecycle history field (re-confirmed by direct enumeration of `CanonicalState`'s own fifteen schema keys, none of which is a lifecycle-history container). No code path in the active trace reconstructs lifecycle history from `Position` or from `CanonicalState`'s own financial state; `PnLEngine.update()` and `compute_equity()` consume only the `trade_event` (a `LifecycleEvent`) and explicit scalar parameters, never `TradeLifecycleEngine.trades` directly. `Trade` instances themselves (unlike `LifecycleEvent`) are mutable dataclasses (`quantity`, `exit_price`, `exit_tick`, `status`, and `events` are all reassigned across a trade's own lifetime by `TradeLifecycleEngine`'s own internal methods); this mutability is confined to `TradeLifecycleEngine`'s own internal management of its own owned entities and does not, by itself, constitute a duplication or an external aliasing concern, since no external consumer holds a reference to a live `Trade` object in the active trace (`current_position()` returns a freshly-constructed plain dict, not the `Trade` object itself). This is currently evidenced.

## 17. Position Information Flow

Re-traced: `TradeLifecycleEngine.on_execution` -> `TradeLifecycleEngine.current_position()` (a freshly-constructed dict) -> `PositionEngine.update_post_trade` (Computational Authority, Section 13) -> a freshly-constructed Position snapshot dict -> `CanonicalEnforcer.apply_position` -> `CanonicalState.state["position"]`. Downstream: `PnLEngine.update` reads only `position_pre["entry_price"]` (a scalar, captured before Position Update in the current tick, per P2-02A's own already-certified pre-trade-view contract, Section 9 below); `RiskEngine.check` reads the post-trade `position` parameter, including its own `exposure` key. Exposure is confirmed, by direct reading of `PositionEngine._compute_exposure`, to be computed exclusively as a derived property of `side`, `quantity`, and `last_price` - no independent Exposure ownership path exists anywhere in the active trace, matching ADR-004 exactly (not reopened here). This information flow matches the Target Information Flow's own stated path (`TradeLifecycleEngine -> PositionEngine -> [Position] -> PnLEngine, RiskEngine`) and is currently evidenced, subject to the two qualifications already recorded in Sections 12 and 13 (fresh-construction-by-convention, and cross-tick private-state self-consistency).

**P2-02A's own already-certified pre-trade-view reading, re-confirmed applicable here.** P2-02A Architecture Section 13 established that `position_pre = self.cstate.get()["position"]`, captured once at the start of a tick, constitutes "an explicit, immutable pre-trade Position view... read exclusively from CanonicalState.state['position']," consumed by `StrategySelector`, `Executor`, and `PnLEngine`'s own `entry_basis` input, and that `PositionEngine`'s own internal instance state is legitimately retained, private Computational-Authority working state, not a second external read path, provided no consumer outside `PositionEngine` itself reads that internal state directly (P2-02A-AI-005). This document re-confirms, by direct trace, that no consumer outside `PositionEngine` does read its internal instance attributes directly in the active runtime - the P2-02A contract itself is not violated. This document's own Section 12 finding (that `position_pre` is, in fact, a live reference into `CanonicalState.state`, not a copy, and is only *effectively* immutable because `PositionEngine`'s own producer discipline always replaces rather than mutates the underlying object) refines, rather than contradicts, P2-02A's own characterization: P2-02A's use of "immutable" describes the currently-observed behaviour, not a structural guarantee - the same distinction this document draws generally in Section 12.

## 18. Financial Information Flow

Re-traced: `TradeLifecycleEngine` (Lifecycle Facts, via `trade_event`) + `PositionEngine` (`position_pre["entry_price"]`, the Entry Basis) -> `PnLEngine.update` (Realized PnL, Computational Authority) -> `PnLEngine.compute_equity` (Equity, Peak Equity, cumulative Realized PnL, all Computational Authority) -> `CanonicalEnforcer.apply_pnl`/`apply_realized_pnl_cumulative`/`apply_equity`/`apply_peak_equity` -> `CanonicalState.state`. Downstream: `RiskEngine.check` reads `equity` and `peak_equity` from the `canonical_state` dict (Section 11); `PerformanceEngine.update` reads `pnl` directly as its own explicit parameter, not from `CanonicalState`. Every financial value in this chain is a Python scalar `float`, structurally immune to aliasing (Section 12). This information flow matches the certified P2-03 contract exactly and is currently evidenced; not reopened here.

## 19. Risk Information Flow

Re-traced: `canonical_state = self.cstate.get()` (Canonical Financial State, read as Canonical Working State, Section 11) + `position` (post-trade, including Exposure) -> `RiskEngine.check` (Computational Authority for Drawdown, Drawdown Ratio, and `risk_allocation_factor`) -> `CanonicalEnforcer.apply_risk` -> `CanonicalState.state`. Downstream: `PerformanceEngine.update` does not itself consume any Risk Metric in the active trace (it receives `decision`, `pnl`, `regime`, `trade_event` only) - the Baseline's own Runtime Stage Responsibilities table names "Lifecycle History + Financial State" as `PerformanceEngine`'s own primary input, which is consistent with the active trace not routing Risk Metrics into `PerformanceEngine` at all. This information flow matches the certified P2-04 contract exactly and is currently evidenced; not reopened here.

## 20. Performance Information Flow

Analyzed at its current-state shape only, per the governing task's own explicit instruction; no P3-03 redesign is anticipated, and TD-004 is explicitly left at P3-03 (re-confirmed unmodified, Section 4).

Re-traced: `PerformanceEngine.update(decision, pnl, regime, trade_event)` - its own primary input is `decision` (the `StrategySelector`'s own Execution Decision, i.e. an intention, not a completed lifecycle outcome) and `pnl` (a scalar, the current tick's own realized PnL, `0.0` when no closing event occurred this tick), gated only by a check for `trade_event.event_type == "RUNTIME_FAILURE_EVENT"` (in which case `self.stats` is returned unchanged). This matches TD-004's own already-registered description ("PerformanceEngine shall later consume lifecycle/financial outcomes instead of decision ticks") exactly: the currently active implementation still keys its own statistics dictionary by `decision["action"]` (a per-tick intention) rather than by a completed lifecycle outcome, and increments `trades` on every non-rejected tick regardless of whether that tick's own action corresponds to a newly-opened, scaled, partially-closed, or fully-closed trade. This is the identical condition ADR-008 (Performance Ownership) and TD-004 already describe; this document adds no new finding on this specific point, records it only for completeness of the current-state description this section requires, and does not propose a resolution (TD-004 remains P3-03's). Object-identity note (Section 12): `PerformanceEngine.update`'s own return value is the same mutated-in-place `self.stats` object every call - a Reference and Copy Semantics finding (FR-004), not a new Performance-methodology finding, and therefore recorded there, not here, as the governing task's own boundary requires (topic 13 versus topic 4/14).

## 21. Failure Information Flow

Re-confirmed, not reopened: an unhandled exception propagating out of `RunLoop.step()` produces a Failed Tick (P3-01-AD-004); whatever subset of `CanonicalEnforcer.apply_*` calls already executed before the exception remains in `CanonicalState`, unaltered; no artificial `RUNTIME_FAILURE_EVENT` is generated for a Failed Tick; the caller (`main.py`) bears sole responsibility for catching it. A genuine `RUNTIME_FAILURE_EVENT` (rejected lifecycle transition, e.g. `OVER_CLOSE_QUANTITY`) is generated by `TradeLifecycleEngine._failure_event`, becomes part of immutable lifecycle history (Section 16), and leaves `CanonicalState`'s own Position, Financial, and Performance fields unmutated (P3-01-AD-006, re-confirmed, not reopened).

**Post-Exception Financial/Lifecycle Divergence, re-examined.** P3-01 Architecture Section 18 and the P3-01 Final Certification (Section 24) name and classify this condition (a divergence between `TradeLifecycleEngine`'s own already-recorded lifecycle event and `CanonicalState`'s own not-yet-published financial consequence, following an exception between TradeLifecycle Update and Financial Accounting) as a non-blocking documented residual risk, not resolved and not to be resolved within P3-01. This document does not reopen that classification. It records, as a distinct, information-flow-specific instance of the same general failure pattern, the `PositionEngine`-private-state divergence this document independently identified (Section 13, FR-013): unlike the P3-01-named condition, which describes a mismatch between two separately-owned representations (`TradeLifecycleEngine` history versus `CanonicalState`), the newly-identified condition additionally involves an internal self-inconsistency within one single component's own private state (`PositionEngine`'s own instance attributes no longer mutually consistent with each other). Both conditions share the same governing constraint: a general resolution would constitute Recovery architecture, explicitly Deferred Scope under ADR-012, and is not designed by this document.

## 22. HOLD and No-Execution Information Flow

Re-traced for a `HOLD` (or no-recognized-action) decision: `TradeLifecycleEngine.on_execution` returns `None` for `action == "HOLD"`; `PositionEngine.update_post_trade` receives `lifecycle_position=None` (via `current_position()`, whose own no-active-trade branch already returns a `{"position": "FLAT", ...}` dict, not `None`, so in practice `update_post_trade` receives a well-formed FLAT-shaped dict, not literally `None`, when no trade is active - re-confirmed by direct reading, a minor terminological imprecision relative to a literal reading of "receives None," recorded as Documentation Gap DG-002, Section 26) and republishes an unchanged-shape Position; `PnLEngine.update` returns `0.0` for a `None` `trade_event` (or for any `trade_event` whose `event_type` is not `TRADE_CLOSED`/`PARTIAL_CLOSE`); `PnLEngine.compute_equity` republishes the prior cumulative values unchanged in this case (its own `RUNTIME_FAILURE_EVENT`-only short-circuit does not apply to a plain `None` `trade_event`, but the arithmetic itself is a no-op addition of `0.0`, producing a numerically unchanged, freshly-computed result - not a re-publication of the identical prior object, a distinction with no numeric consequence but a genuine object-identity difference, noted for completeness); `RiskEngine.check` and `PerformanceEngine.update` both execute normally and republish (Section 12 qualifications apply identically to a HOLD tick as to any other). Every stage still executes; Tick Completion is still reached. This matches P3-01-AD-005 exactly and is currently evidenced; not reopened here.

## 23. Alternative Information Paths

Re-confirmed, extending P3-01-AD-009's own finding: `run_engine/core/decision.py` (`DecisionEngine`), `run_engine/runtime/` (thirteen files including `snapshot.py`, `position_state.py`, `pnl_engine.py`, `risk.py`, `strategy_selector.py` - alternative, non-active implementations of several active-path responsibilities, by name resemblance only, not evaluated further as their content is out of this unit's own active-path scope), `run_engine/execution/` (top-level: `adapter.py`, `safety.py`; distinct from the active `run_engine/core/execution/` package), `run_engine/feedback/tracker.py`, and `run_engine/logging/logger.py` all remain confirmed unimported by the active path (Section 5). No duplicate Producer and no duplicate Writer for any Matrix-named object was found feeding `CanonicalState` from any of these inactive locations.

**Newly identified in this document (Section 5): `run_engine/core/position_sizing.py` and `run_engine/core/state_modulation.py`.** Both are confirmed unimported anywhere in `run_engine/`, sitting directly inside the otherwise-active `run_engine/core/` directory rather than in one of the four already-named inactive directories. Neither writes to `CanonicalState`, directly or indirectly, since neither is instantiated anywhere in the active trace; they therefore do not constitute a duplicate Producer or Writer in the currently executing runtime. Their disposition (retain/integrate/archive/remove) remains, consistent with P3-01-AD-009's own treatment of the four already-named directories, a Phase 6 Repository Consolidation question, not decided here (Documentation Gap DG-001, Section 26).

## 24. Deterministic Information Flow

Every Computational Authority in the active trace is confirmed, by direct source reading, to be a pure or effectively-pure function of its own explicit parameters and its own already-certified legitimate cross-tick instance state (`RegimeClassifier`'s window/history, `StrategySelector`'s cooldown/last-action, `PositionEngine`'s own private Position state, `PnLEngine`'s unused `last_realized_pnl`), with `RiskEngine` confirmed fully stateless beyond its fixed configuration (already certified, P2-04). `StateModulator` (Section 23), had it been active, would have been the sole non-deterministic component in the repository (its own `analyze()` method calls `random.random()`); it is confirmed unimported and therefore does not affect the active runtime's own determinism.

Given identical tick inputs and an identical initial `CanonicalState`, the active trace is confirmed, by the empirical dual-instance stage-boundary replay already performed as part of the P3-01 Final Certification (Section 25 of that document, re-cited here rather than re-executed, since P3-01's own AD-007/Contract EO-013 obligation already covers full-sequence replay identity and this document does not reopen it), to produce functionally identical intermediate and final results across two independent `RunLoop` instances.

This document's own Reference and Copy Semantics findings (Section 12) introduce a distinct, additional determinism-adjacent concern the P3-01 replay evidence does not itself cover: that replay-comparison methodology's own correctness implicitly depends on comparing *values*, not object identities, at each stage boundary. Two independent `RunLoop` instances, by construction, never share any object identity with each other (each owns its own `CanonicalState`, `PerformanceEngine`, etc.), so the aliasing findings of Section 12 - which concern a *single* runtime instance's own objects being aliased *across ticks of that same instance* - do not themselves invalidate the P3-01 cross-instance replay evidence. They do, however, mean that a *single*-instance, cross-tick comparison methodology (for example, a diagnostic or monitoring consumer that retains and later re-inspects a specific tick's own returned snapshot) would not observe the value that was true at the time it was returned, but whatever value is true at the time of re-inspection - a latent, currently-unexercised risk to any future single-instance historical-comparison or auditing consumer, distinct from the already-certified cross-instance replay determinism. This is recorded as Residual Risk RR-001 (Section 26).

## 25. Current Traceability State

Every object in the Runtime Object Inventory (Section 9) is traceable, by file and line, through: originating observation (Runtime Tick / Market Observation, Section 7 Step 1-2), transformation (the Computational Authority named in Section 9), publication (the `CanonicalEnforcer.apply_*` call, or the explicit Runtime Tick exception), consumption (the Primary Consumer(s) named in the Runtime Ownership Matrix, re-confirmed in Section 10), canonical storage (the specific `CanonicalState.state` key, where applicable), historical storage (`TradeLifecycleEngine.trades`/`failure_events`, where applicable), and derived-view status (Section 12: which objects are genuinely re-derived fresh, and which - Performance Metrics - are not). This traceability is currently evidenced and is, in fact, more granular than P3-01-AD-008's own minimum requirement (file/line only), since this document additionally establishes object-identity status per object (Section 12), not previously required or produced by any prior document in this governance chain.

## 26. Functional Gaps

A Functional Gap is recorded only where an existing normative requirement (stated in this document's own Section 28, grounded in the Baseline's ADRs/AIs/Rules) is not currently met, or is not currently sufficiently evidenced to confirm it is met. Distinguished explicitly from Cross-Unit Observations, Verified Conformant Findings, Documentation Gaps, Verification Gaps, and Residual Risks (each defined and listed separately below), per the governing task's own explicit instruction not to classify every observation as a Functional Gap by default.

**Functional Gap FG-001 (traces to FR-001).** `CanonicalState.get()`'s own read-contract (reference, shallow copy, deep copy, or read-only view) is not explicitly, singularly defined by any binding document; the current implementation returns a live reference (Section 12). This is CUO-01, now owned by this unit (Section 8).

**Functional Gap FG-002 (traces to FR-003).** The Tick-Complete result's own `"state"` field is not object-identity-isolated from `CanonicalState`'s own subsequent mutation; a previously-returned reference silently reflects later ticks' own values (Section 12, empirically confirmed).

**Functional Gap FG-003 (traces to FR-004).** `Performance Metrics` is published as the same mutated-in-place object on every tick, not as a freshly-constructed value; this is inconsistent with the currently-observed (but not contractually guaranteed) fresh-construction behaviour of every other dict-shaped canonical object (Section 12, empirically confirmed).

**Functional Gap FG-004 (traces to FR-007).** `CanonicalEnforcer.apply_risk`'s own return value (the complete live state dict) is inconsistent with the single-value-return shape all ten other `apply_*` methods follow (Section 10).

**Functional Gap FG-005 (traces to FR-013).** `PositionEngine`'s own private cross-tick instance state can reach an internally self-inconsistent value if an exception interrupts its own sequential, non-atomic field mutation; this is not reconciled by any existing mechanism, and is a newly-identified instance of the general pattern P3-01 already named for a different object pair (Section 13, empirically confirmed).

## 27. Cross-Unit Observations

No new Cross-Unit Observation is raised by this document beyond CUO-01 itself, which is no longer classified as a Cross-Unit Observation with respect to P3-02 (Section 8: it is now this unit's own Functional Gap, FG-001). The Performance Information Flow finding (Section 20) is explicitly not raised as a new Cross-Unit Observation, since it restates, without extending, the already-registered TD-004 (Target Phase P3, i.e. this Phase, but explicitly reserved for the P3-03 unit specifically by the Implementation Baseline's own unit definitions, Section 4) - no new forwarding action is required.

## 28. Verified Conformant Findings

**Verified Conformant Finding VCF-001.** Position, Strategy Selection, Execution Decision, and Execution Event are each confirmed, by direct source reading of their own producers, to be freshly constructed on every producing call, never mutated in place after construction and reassignment into `CanonicalState`. This finding explicitly excludes Performance Metrics (Functional Gap FG-003).

**Verified Conformant Finding VCF-002.** Every scalar canonical value (Drawdown, Drawdown Ratio, `risk_allocation_factor`, Realized PnL, cumulative Realized PnL, Equity, Peak Equity, Runtime Status, Market Regime, Runtime Tick, Price) is structurally immune to aliasing by virtue of Python's own scalar immutability; no information-flow risk applies to these values regardless of reference-versus-copy resolution (Section 12).

**Verified Conformant Finding VCF-003.** Writer-on-Behalf-Of exclusivity (P3-01-AI-009) is re-confirmed intact at the current HEAD: exactly one direct `CanonicalState.update_*` call site exists per method, and every one is either inside `canonical_enforcer.py` or is Runtime Tick's own explicitly Matrix-named exception (Section 14).

**Verified Conformant Finding VCF-004.** No consumer-side mutation of a received parameter, and no engine-internal mutation of an input parameter, was found anywhere in the active trace (Section 13); this is a currently-conformant, though not structurally enforced, behaviour.

## 29. Documentation Gaps and Verification Gaps

**Documentation Gap DG-001.** `run_engine/core/position_sizing.py` and `run_engine/core/state_modulation.py` are confirmed-unimported, dormant files inside the active `run_engine/core/` directory, not previously named or classified by any prior governance document in this chain (Section 5, Section 23).

**Documentation Gap DG-002.** The Target Information Flow's and this unit's own informal description of HOLD-path behaviour as `TradeLifecycle Update` producing "no LifecycleEvent" for `PositionEngine` to consume is, at the precise parameter level, imprecise: `PositionEngine.update_post_trade` in practice receives a well-formed FLAT-shaped dict from `TradeLifecycleEngine.current_position()`, not a literal `None`, whenever no trade is currently active (Section 22).

**Verification Gap VG-001.** Rule OM-004 (no Primary Consumer modification of consumed information) has never been independently, systematically verified across every consumer by an automated check; its current conformance (Section 10, Section 13, VCF-004) rests on direct manual source inspection performed during this document's own drafting, not on a repeatable, independent verification procedure.

## 30. Residual Risks

**Residual Risk RR-001.** A future single-instance consumer that retains and later re-inspects a specific tick's own returned Tick-Complete result (rather than consuming it immediately, as `main.py` currently does) would observe values that have silently changed since that tick, for the `"state"` container itself (Functional Gap FG-002) and for Performance Metrics specifically (Functional Gap FG-003), even though the already-certified P3-01 cross-instance replay determinism (Section 24) remains entirely unaffected, since that evidence concerns comparison between independent `RunLoop` instances, not retained references within one instance.

**Residual Risk RR-002 (restated, not newly created).** Post-Exception Financial/Lifecycle Divergence (P3-01 Architecture Section 18, P3-01 Final Certification Section 24) remains an open, non-blocking, documented residual risk, unresolved by this document. Its newly-identified structural cousin, the `PositionEngine`-private-state self-inconsistency (Functional Gap FG-005), is recorded as a Functional Gap rather than a further Residual Risk, since - unlike the original condition, already assessed and classified as non-blocking by the P3-01 Final Certification - this specific instance has not yet been assessed by any Certification-stage review; its eventual classification (Functional Gap disposition, Minor Finding, or non-blocking documented residual risk) is left to this unit's own later CGA and Architecture stages, consistent with the FRA's own prohibition on pre-selecting a classification that belongs to a later stage.

## 31. Required Functional Capabilities

Derived directly from Sections 12 through 25, before restating them as individual normative Functional Requirements in Section 32: (1) an explicit, singular `CanonicalState.get()` read-contract; (2) object-identity isolation for the Tick-Complete result's own top-level container; (3) fresh-construction guarantee (or an explicit, documented alternative) for every dict-shaped published canonical object, including Performance Metrics; (4) a Producer-Consumer contract that is not only documented but independently verifiable; (5) Writer-on-Behalf-Of exclusivity, re-affirmed; (6) a consistent `CanonicalEnforcer` return-value contract; (7) semantic continuity, re-affirmed; (8) no downstream reconstruction, re-affirmed; (9) Runtime Event single-transition integrity, re-affirmed; (10) Lifecycle History immutability and non-duplication, re-affirmed; (11) conformant Position/Financial/Risk information flow, re-affirmed; (12) cross-tick component private-state self-consistency; (13) a current-state-only, non-redesigning description of Performance information flow; (14) no unauthorized consumer mutation, independently verifiable; (15) Failure information flow conformance, re-affirmed, including the newly-identified divergence instance; (16) HOLD/No-Execution information flow conformance, re-affirmed; (17) alternative-path exclusivity, extended to the two newly-identified dormant files; (18) complete object-level traceability; (19) deterministic information flow, re-affirmed, with the single-instance retained-reference risk explicitly bounded; (20) explicit scope boundaries against P3-01 and P3-03.

## 32. Functional Requirements

Normative language (SHALL / SHALL NOT) is used only for the requirement itself; no concrete technical solution is prescribed where that choice belongs to the Architecture stage.

---

**P3-02-FR-001 - CanonicalState.get() Read-Contract Definition**

Requirement Statement: The read-contract of `CanonicalState.get()` (reference, shallow copy, deep copy, or read-only view semantics) SHALL be explicitly and singularly defined by a binding architectural decision.

Scientific Rationale: AI-002 (Unique Ownership) and Rule OM-006 (CanonicalState exclusively owns active runtime state) presuppose that access to that owned state follows one well-defined contract; an undefined read-contract leaves every consumer's own aliasing exposure undefined by construction.

Existing Evidence: `canonical_state.py:107-109`, `def get(self): return self.state`, unchanged since the Architecture Baseline and since P3-01 (Section 5, Section 12).

Current Conformance: unresolved.

Validation Condition: a single, explicitly documented read-contract exists and every `get()` call site's own behaviour is consistent with it.

Scope Boundary: does not select which of the four candidate semantics is adopted; that is an SDA/Architecture-stage decision (CUO-01, now owned here per Section 8).

Traceability: FR domain - AI-002, Rule OM-006, Canonical Storage definition; CUO-01.

---

**P3-02-FR-002 - Canonical Working State Internal-Only Consumption**

Requirement Statement: Canonical Working State SHALL be consumed only by a component whose own execution position within the current tick has already been reached, and SHALL NOT be externally observable before Tick Completion.

Scientific Rationale: Baseline definition of Canonical Working State ("may be consumed only by components whose execution order has already been reached... not externally observable"); P3-01-AI-003, P3-01-AI-004.

Existing Evidence: Section 11 - `RiskEngine.check` is the sole internal Canonical Working State consumer in the active trace; no external observation path exists (`RunLoop.step()` contains no yield, no intermediate return).

Current Conformance: currently evidenced.

Validation Condition: a fresh trace confirms Canonical Working State is consumed only at or after its own producing stage, and remains unobservable externally before the tick's own `return` statement.

Scope Boundary: does not evaluate whether the returned Tick-Complete result is itself subsequently mutable (FR-003).

Traceability: Canonical Working State definition; P3-01-AI-003, P3-01-AI-004; AC-009, AC-010.

---

**P3-02-FR-003 - Tick-Complete Result Object-Identity Isolation**

Requirement Statement: The value returned as part of a Tick-Complete result SHALL NOT be an object that a subsequent tick's own processing will further mutate or reassign in a way observable through the previously-returned reference.

Scientific Rationale: The Baseline's own definition of Tick-Complete Snapshot ("the externally observable canonical runtime state after all mandatory runtime stages have completed") and AI-009 (Tick Completeness) presuppose a point-in-time value; a container that continues to change after being returned is not a snapshot in the sense either provision requires.

Existing Evidence: Section 12 - direct empirical demonstration that the Tick-Complete result's own `"state"` field is the identical object as `CanonicalState.state`, and that a captured reference silently reflects a later tick's own values.

Current Conformance: not currently met, at the top-level container (Functional Gap FG-002, Section 26).

Validation Condition: a captured reference to any previously-returned Tick-Complete result remains, at every subsequently-inspected field, equal to the value that was true at the moment it was returned, regardless of how many further ticks execute afterward.

Scope Boundary: does not itself decide the isolation mechanism (copy, immutable view, or otherwise); that is an Architecture-stage decision. Does not extend to Canonical Working State's own internal, intentionally non-isolated consumption during the same tick (FR-002).

Traceability: Tick-Complete Snapshot definition; AI-009; AC-009; CUO-01 (related but distinct: CUO-01 concerns the read-contract generally, FR-003 concerns the specific post-return stability property).

---

**P3-02-FR-004 - Published Object Fresh-Construction Consistency**

Requirement Statement: Every dict-shaped or otherwise mutable canonical object published via `CanonicalEnforcer` SHALL be a value distinct in object identity from the value it replaces, unless an explicit, documented exception establishes otherwise.

Scientific Rationale: Rule IF-001 (information already produced upstream shall never be reconstructed downstream) and the Derived View definition ("may be regenerated at any time") presuppose that publication yields a genuinely new value each time, not a continuously-mutated shared one; a mutated-in-place shared object cannot be safely treated as a Derived View by any consumer that retains a reference to it.

Existing Evidence: Section 12 - Position, Strategy Selection, Execution Decision, and Execution Event are all confirmed freshly constructed on every call (Verified Conformant Finding VCF-001); Performance Metrics is confirmed to be the same object, mutated in place, on every call (empirically demonstrated).

Current Conformance: not currently met, specifically for Performance Metrics (Functional Gap FG-003, Section 26); currently met for every other dict-shaped canonical object, though only by convention, not by structural guarantee.

Validation Condition: for every dict-shaped canonical object, `id()` of the value published at tick N differs from `id()` of the value published at tick N+1, whenever a publication occurs at both ticks.

Scope Boundary: does not require immutability of the object's own internals, only distinct object identity across publications. Does not decide whether this is achieved by copying, by construction discipline, or by a structural type change; that is an Architecture-stage decision.

Traceability: Rule IF-001; Derived View definition; AI-007 (Semantic Continuity, related); TD-004 (Performance Metrics' own broader redesign remains P3-03's, not reopened by this requirement, which addresses only object-identity discipline, not accounting methodology).

---

**P3-02-FR-005 - Explicit, Independently Verifiable Producer-Consumer Contracts**

Requirement Statement: For every Runtime Ownership Matrix row, the Producer, the published object, the Primary Consumer(s), and the set of permitted and forbidden mutations SHALL be independently verifiable, not solely documented.

Scientific Rationale: Rule OM-004 (Primary Consumers shall never modify consumed information) is a normative rule without a corresponding structural or automated verification mechanism in the current implementation.

Existing Evidence: Section 10 - every Matrix row's Producer/Consumer pairing matches the active trace exactly; no structural enforcement of the non-mutation rule exists; no automated verification procedure exists (Verification Gap VG-001, Section 29).

Current Conformance: partially evidenced (the pairing itself is currently evidenced; independent verifiability of the non-mutation rule is not).

Validation Condition: an independent, repeatable procedure confirms, for every Matrix row, that no consumer mutates the object it consumes.

Scope Boundary: does not require a specific enforcement mechanism (read-only wrapper, copy-on-read, or otherwise); that is an Architecture-stage decision.

Traceability: Runtime Ownership Matrix; Rule OM-004; AC-002, AC-010.

---

**P3-02-FR-006 - Writer-on-Behalf-Of Exclusivity (Information-Flow Re-Verification)**

Requirement Statement: Every mutation of `CanonicalState.state` SHALL occur exclusively through a named `CanonicalEnforcer.apply_*` method, except Runtime Tick's own explicitly Matrix-named `RunLoop`-direct exception.

Scientific Rationale: Rule OM-003 (Writer-on-Behalf-Of never establishes ownership) and P3-01-AI-009, re-verified rather than reopened at this unit's own information-flow level.

Existing Evidence: Section 14 - a scoped repository-wide search finds exactly one call site per `update_*` method, matching this contract exactly.

Current Conformance: currently evidenced.

Validation Condition: a fresh, scoped repository-wide search at any future HEAD continues to find exactly one call site per `CanonicalState.update_*` method, located as this requirement specifies.

Scope Boundary: does not extend to a full-repository (including untracked, non-runtime directories) search; that scope distinction is itself recorded (Section 5, consistent with the P3-01 Final Certification's own established practice).

Traceability: Rule OM-003; P3-01-AI-009; P3-01-AD-002.

---

**P3-02-FR-007 - CanonicalEnforcer Return-Value Contract Consistency**

Requirement Statement: Every `CanonicalEnforcer.apply_*` method SHALL follow one consistent return-value shape (the single canonical value it writes or confirms), unless an explicit, documented exception establishes otherwise.

Scientific Rationale: Consistency of a Writer-on-Behalf-Of's own publication contract is a precondition for any future consumer to rely on that contract without inspecting each method's own implementation individually; an unexplained exception increases the risk of an unintended full-state exposure to a future caller that does use the return value.

Existing Evidence: Section 10 - ten of eleven `apply_*` methods return their own single published value; `apply_risk` alone returns the complete live `CanonicalState.state` dictionary.

Current Conformance: not currently met (Functional Gap FG-004, Section 26), though currently without observable runtime consequence, since the active trace discards `apply_risk`'s own return value.

Validation Condition: every `apply_*` method's own return value matches one documented, consistent shape.

Scope Boundary: does not require a specific fix (aligning `apply_risk` to the others, or documenting it as an intentional exception); that is an Architecture-stage decision.

Traceability: CanonicalEnforcer's own Writer-on-Behalf-Of role; Rule OM-003 (related, not violated: the inconsistency is a shape concern, not an ownership concern).

---

**P3-02-FR-008 - Semantic Continuity of Upstream Information**

Requirement Statement: Information produced by an upstream runtime component SHALL remain semantically unchanged throughout downstream processing; downstream components SHALL derive new information rather than reinterpret existing information.

Scientific Rationale: AI-007 (Semantic Continuity); Principle IF-003 (every transformation preserves semantic meaning).

Existing Evidence: Sections 17-19 - Position, Financial, and Risk information flow each match the Target Information Flow's own stated path with no reinterpretation found; `entry_basis`/Entry Basis retains its P2-02A-certified meaning throughout (Section 17).

Current Conformance: currently evidenced.

Validation Condition: a fresh trace of each object named in Sections 17-19 confirms no downstream component reassigns a different meaning to a value than its own producer assigned.

Scope Boundary: does not extend to Performance Information Flow's own decision-versus-outcome distinction, which is TD-004's own, already-registered, P3-03-forwarded concern (Section 20), not a semantic-continuity violation within this unit's own scope.

Traceability: AI-007; Principle IF-003; P2-02A, P2-03, P2-04 (not reopened).

---

**P3-02-FR-009 - No Downstream Reconstruction of Already-Produced Information**

Requirement Statement: No downstream runtime component SHALL reconstruct information already produced by an upstream component; it SHALL instead consume that information directly or derive new information from it.

Scientific Rationale: Rule IF-001; Principle IF-002 (information is never reconstructed downstream); AC-010 (Information Flow).

Existing Evidence: Sections 16-19 - `PnLEngine` derives financial consequences exclusively from `trade_event` and `entry_basis`, never reconstructing trade history from `Position`; `RiskEngine` derives Risk Metrics exclusively from Canonical Working State and Position, never reconstructing financial history; Lifecycle History exists exactly once (Section 16).

Current Conformance: currently evidenced.

Validation Condition: for each object named in Sections 16-19, its sole originating computation is confirmed to be its own named Computational Authority, with no alternate derivation path found elsewhere.

Scope Boundary: does not extend to Performance Information Flow's own already-registered TD-004 concern (Section 20).

Traceability: Rule IF-001, Principle IF-002; AC-010; AI-004 (Immutable Lifecycle History, related).

---

**P3-02-FR-010 - Runtime Event Single-Transition Integrity**

Requirement Statement: Every explicit Runtime Event object SHALL represent exactly one semantic transition, SHALL be generated at exactly one call site per transition type, and SHALL NOT be mutated after construction.

Scientific Rationale: AI-008 (Explicit Runtime Events; implicit runtime mutations are prohibited); ADR-002 ("Every Runtime Event shall represent exactly one semantic transition. One Runtime Event shall never represent multiple architectural responsibilities.").

Existing Evidence: Section 15 - every `LifecycleEvent` is a frozen dataclass, structurally immutable; each `event_type` is generated at exactly one dedicated `TradeLifecycleEngine` method.

Current Conformance: currently evidenced, for the Lifecycle Event layer specifically; the Baseline's own broader Decision/Financial/Risk/Performance event categories are realized as plain values rather than distinct event objects in the active trace, a factual, already-ratified (P3-01) characteristic, not a gap this document reopens.

Validation Condition: a fresh trace of `TradeLifecycleEngine` confirms every `LifecycleEvent.event_type` still originates from exactly one call site, and the dataclass remains frozen.

Scope Boundary: does not require introducing distinct event objects for the Decision/Financial/Risk/Performance layers; that would be a P3-01-level ordering/publication-mechanism reopening, explicitly out of scope.

Traceability: AI-008; ADR-002; P3-01-AD-001 (not reopened).

---

**P3-02-FR-011 - Lifecycle History Immutability and Non-Duplication**

Requirement Statement: Lifecycle History SHALL remain exclusively owned by `TradeLifecycleEngine`, SHALL NOT be duplicated into `CanonicalState`, and completed lifecycle records SHALL remain immutable.

Scientific Rationale: AI-004 (Immutable Lifecycle History); AI-012 (Operational and Historical Separation); Rule OM-005.

Existing Evidence: Section 16 - `CanonicalState`'s own fifteen schema keys contain no lifecycle-history duplication; `LifecycleEvent` instances are structurally immutable; no reconstruction of history from Position or Financial State was found.

Current Conformance: currently evidenced.

Validation Condition: `CanonicalState`'s own schema, re-enumerated at any future HEAD, continues to contain no lifecycle-history field, and every `LifecycleEvent` remains a frozen dataclass.

Scope Boundary: does not extend to `Trade`'s own internal mutability (Section 16), which is confined to `TradeLifecycleEngine`'s own private management of its own owned entities.

Traceability: AI-004; AI-012; Rule OM-005; ADR-003.

---

**P3-02-FR-012 - Position Information Flow Conformance**

Requirement Statement: Position information SHALL flow exclusively as: Lifecycle Event/current position -> `PositionEngine` (Computational Authority) -> `CanonicalState` (Authoritative Owner, via `CanonicalEnforcer`) -> `PnLEngine`/`RiskEngine` (Primary Consumers); Exposure SHALL remain exclusively a derived property of Position, never an independently owned object.

Scientific Rationale: ADR-004; the Target Information Flow's own stated Position path; P2-02A (not reopened).

Existing Evidence: Section 17 - re-traced and confirmed exactly matching; Exposure confirmed derived exclusively from `side`, `quantity`, `last_price`.

Current Conformance: currently evidenced, subject to the qualifications recorded separately as FR-003, FR-004, and FR-013 (which concern object-identity and cross-tick self-consistency, not the flow topology itself).

Validation Condition: a fresh trace confirms the same topology, and Exposure remains absent from the Runtime Ownership Matrix as an independent row.

Scope Boundary: does not reopen P2-02A's own certified ownership, formula, or pre-trade-view contract.

Traceability: ADR-004; Target Information Flow; P2-02A (Architecture and Final Certification).

---

**P3-02-FR-013 - Cross-Tick Component Private-State Self-Consistency**

Requirement Statement: A runtime component's own legitimately-retained cross-tick private instance state SHALL NOT reach an internally self-inconsistent value (a value that could not have resulted from any single complete, uninterrupted computation) as a consequence of an exception interrupting that component's own computation.

Scientific Rationale: AI-005 (Deterministic Execution: "Deterministic behaviour shall not depend upon hidden mutable state"); the same governing concern P3-01-AD-004 and Architecture Section 19 already applied to `RegimeClassifier` and `StrategySelector`, extended here on the basis of newly-obtained evidence to `PositionEngine`.

Existing Evidence: Section 13 - a direct probe demonstrates `PositionEngine`'s own private instance state reaching exactly such a self-inconsistent value (new `quantity`/`last_price`, stale `exposure`) after an injected exception at its own final mutating statement.

Current Conformance: not currently met (Functional Gap FG-005, Section 26).

Validation Condition: for every component retaining cross-tick private instance state and performing multi-step mutation of it, an interruption at any point during that mutation leaves the component's own private state either fully updated or fully unchanged, never partially updated.

Scope Boundary: does not require a specific mechanism (atomic update, rollback, or otherwise); that is an Architecture-stage decision. Does not extend this requirement to `RegimeClassifier` or `StrategySelector` beyond what P3-01 already documented, since this document performed no new probe against those two components.

Traceability: AI-005; P3-01-AD-004; P3-01 Architecture Section 19 (extended, not reopened); Post-Exception Financial/Lifecycle Divergence (related, distinct instance).

---

**P3-02-FR-014 - Financial Information Flow Conformance**

Requirement Statement: Financial information SHALL flow exclusively as: Lifecycle Facts + Entry Basis -> `PnLEngine` (Computational Authority) -> `CanonicalState` (Authoritative Owner, via `CanonicalEnforcer`) -> `RiskEngine` (Primary Consumer for Equity/Peak Equity).

Scientific Rationale: ADR-005, ADR-006; the Target Information Flow's own stated Financial path; P2-03 (not reopened).

Existing Evidence: Section 18 - re-traced and confirmed exactly matching.

Current Conformance: currently evidenced.

Validation Condition: a fresh trace confirms the same topology.

Scope Boundary: does not reopen P2-03's own certified ownership or formulas.

Traceability: ADR-005; ADR-006; Target Information Flow; P2-03 (Architecture and Final Certification).

---

**P3-02-FR-015 - Risk Information Flow Conformance**

Requirement Statement: Risk information SHALL flow exclusively as: Canonical Financial State + Position -> `RiskEngine` (Computational Authority) -> `CanonicalState` (Authoritative Owner, via `CanonicalEnforcer`).

Scientific Rationale: ADR-007; the Target Information Flow's own stated Risk path; P2-04 (not reopened).

Existing Evidence: Section 19 - re-traced and confirmed exactly matching.

Current Conformance: currently evidenced.

Validation Condition: a fresh trace confirms the same topology.

Scope Boundary: does not reopen P2-04's own certified ownership or formulas.

Traceability: ADR-007; Target Information Flow; P2-04 (Architecture and Final Certification).

---

**P3-02-FR-016 - Performance Information Flow Current-State Description**

Requirement Statement: The current Performance information flow SHALL be documented accurately as currently implemented, without redesigning its own accounting methodology.

Scientific Rationale: ADR-008 (Performance Ownership); TD-004; the governing task's own explicit prohibition on P3-03 preemption.

Existing Evidence: Section 20 - `PerformanceEngine.update`'s own current input is `decision` (an intention) and `pnl`, not a completed lifecycle outcome, matching TD-004's own already-registered description exactly.

Current Conformance: partially evidenced (the current-state description itself is fully evidenced; TD-004's own eventual resolution remains, by design, unresolved and P3-03's).

Validation Condition: the current-state description in Section 20 matches the active trace at any future HEAD, until TD-004 is addressed by P3-03.

Scope Boundary: does not redesign `PerformanceEngine`'s own accounting methodology; does not reopen or advance TD-004.

Traceability: ADR-008; TD-004; Target Information Flow (Performance row).

---

**P3-02-FR-017 - No Unauthorized Consumer Mutation, Independently Verifiable**

Requirement Statement: No Primary Consumer SHALL mutate the runtime object it consumes; this property SHALL be independently, repeatably verifiable.

Scientific Rationale: Rule OM-004.

Existing Evidence: Section 10, Section 13 - no mutation found by direct manual inspection (Verified Conformant Finding VCF-004); no automated or independently repeatable verification procedure exists (Verification Gap VG-001).

Current Conformance: not yet independently evidenced (the property itself appears true by manual inspection; its independent verifiability is not yet established).

Validation Condition: a repeatable, independent procedure confirms, for every consumer named in the Runtime Ownership Matrix, that the object it receives is unchanged in every field after the consuming call returns.

Scope Boundary: does not require a structural enforcement mechanism; verification and enforcement are distinct, and this requirement addresses verification only.

Traceability: Rule OM-004; AC-002.

---

**P3-02-FR-018 - Failure Information Flow Conformance**

Requirement Statement: Failure information flow SHALL conform exactly to P3-01-AD-004 (Failed Tick) and P3-01-AD-006 (rejected-transition non-mutation); any newly-identified divergence condition SHALL be explicitly documented, not silently accepted or silently resolved.

Scientific Rationale: P3-01-AD-004, P3-01-AD-006 (not reopened); the governing task's own explicit instruction not to select a new failure architecture.

Existing Evidence: Section 21 - both P3-01 conditions re-confirmed unchanged; the `PositionEngine`-private-state divergence (FR-013) recorded as a distinct, newly-identified instance of the same general pattern.

Current Conformance: currently evidenced for the two already-certified conditions; the newly-identified condition's own conformance is addressed separately under FR-013.

Validation Condition: a fresh trace confirms both already-certified conditions remain exactly as P3-01 established them.

Scope Boundary: does not design a new failure architecture, a rollback mechanism, or a reconciliation mechanism.

Traceability: P3-01-AD-004; P3-01-AD-006; ADR-011; Post-Exception Financial/Lifecycle Divergence.

---

**P3-02-FR-019 - HOLD and No-Execution Information Flow Conformance**

Requirement Statement: A HOLD or no-execution tick SHALL conform exactly to P3-01-AD-005: every stage executes, every downstream stage produces a well-defined result for a no-event input, and Tick Completion is reached without an Execution Event having occurred.

Scientific Rationale: P3-01-AD-005 (not reopened).

Existing Evidence: Section 22 - re-traced and confirmed conformant, with one terminological imprecision noted (Documentation Gap DG-002) not affecting the substantive finding.

Current Conformance: currently evidenced.

Validation Condition: a fresh trace of a scripted HOLD-only tick sequence confirms the same behaviour.

Scope Boundary: does not reopen P3-01-AD-005 itself.

Traceability: P3-01-AD-005; Tick Completion Contract.

---

**P3-02-FR-020 - Alternative Information Path Exclusivity**

Requirement Statement: No inactive or dormant code path SHALL constitute an active duplicate Producer or Writer for any Matrix-named runtime object; every dormant file's own disposition SHALL be explicitly tracked, not left undocumented.

Scientific Rationale: P3-01-AD-009 (execution-path exclusivity, re-verified, not reopened); AI-013 (Architectural Minimality).

Existing Evidence: Section 23 - the four P3-01-named inactive directories re-confirmed unimported; two additional dormant files (`position_sizing.py`, `state_modulation.py`) newly identified and confirmed unimported, but not previously tracked (Documentation Gap DG-001).

Current Conformance: partially evidenced (exclusivity itself is currently evidenced; complete documentation of every dormant file's own existence is not, until this document's own Section 23/29).

Validation Condition: a fresh, repository-wide import-closure check confirms no dormant file is imported by the active path, and every dormant file's own existence is named in a governing document.

Scope Boundary: does not classify or dispose of any dormant file (retain/integrate/archive/remove); that remains Phase 6 Repository Consolidation's own scope.

Traceability: P3-01-AD-009; AI-013; Phase 6.

---

**P3-02-FR-021 - Complete Object-Level Traceability**

Requirement Statement: Every runtime object named in the Runtime Ownership Matrix SHALL be traceable through its originating observation, transformation, publication, consumption, canonical storage, historical storage (where applicable), and derived-view/object-identity status.

Scientific Rationale: AI-014 (Architectural Traceability); AC-011 (Scientific Traceability); P3-01-AD-008 (re-verified, extended with object-identity status, Section 8, Section 25).

Existing Evidence: Section 25 - complete traceability table constructed and confirmed for every object in the Runtime Object Inventory (Section 9).

Current Conformance: currently evidenced.

Validation Condition: a fresh trace at any future HEAD reproduces the same traceability path for every named object.

Scope Boundary: does not extend to a full semantic-continuity re-derivation beyond what Sections 17-19 already establish.

Traceability: AI-014; AC-011; P3-01-AD-008.

---

**P3-02-FR-022 - Deterministic Information Flow**

Requirement Statement: Given identical tick inputs and an identical initial `CanonicalState`, the active information flow SHALL produce functionally identical intermediate and final results; no aliasing SHALL introduce cross-instance nondeterminism.

Scientific Rationale: AI-005, AI-006; P3-01-AD-007/Contract EO-013 (cross-instance replay, not reopened).

Existing Evidence: Section 24 - every Computational Authority confirmed pure or effectively-pure; the sole non-deterministic component in the repository (`StateModulator`) confirmed unimported; P3-01's own already-certified dual-instance stage-boundary replay re-cited, not re-executed.

Current Conformance: currently evidenced for cross-instance determinism (inherited from P3-01, not reopened); the single-instance retained-reference risk this document additionally identifies (Residual Risk RR-001) does not contradict this finding, since it concerns a different property (post-return value stability for a retaining consumer, not cross-instance output identity).

Validation Condition: cross-instance replay determinism continues to hold at any future HEAD (inherited validation condition, P3-01-AD-007); no future single-instance retaining consumer is introduced without RR-001 being explicitly addressed.

Scope Boundary: does not re-execute P3-01's own replay verification; does not extend determinism claims to a retry sequence following a Failed Tick (P3-01's own qualification, not reopened).

Traceability: AI-005; AI-006; P3-01-AD-007; P3-01 Final Certification Section 25.

---

**P3-02-FR-023 - P3-01 Non-Reopening**

Requirement Statement: This unit SHALL NOT reopen, redecide, or alter the P3-01-ratified twelve-stage execution ordering, Tick-Complete Publication semantics, Failed-Tick semantics, or HOLD/rejection ordering.

Scientific Rationale: the governing task's own explicit scope boundary; P3-01 Final Certification's own CERTIFIED verdict.

Existing Evidence: Sections 7, 21, 22 - every P3-01-established behaviour re-traced and re-confirmed unchanged, never redecided.

Current Conformance: currently evidenced.

Validation Condition: no section of any future P3-02 document proposes a change to P3-01's own certified ordering or failure/HOLD semantics.

Scope Boundary: this requirement is itself a scope boundary, not a technical property to be further validated beyond compliance review.

Traceability: P3-01 Final Certification; P3-01-AD-001 through AD-010.

---

**P3-02-FR-024 - P3-03 Non-Preemption**

Requirement Statement: This unit SHALL NOT redesign `PerformanceEngine`'s own accounting methodology or advance TD-004's own resolution.

Scientific Rationale: the Implementation Baseline's own unit boundary (P3-02: "Remove hidden coupling... "; P3-03: "Verify PerformanceEngine inputs. Validate Performance Metrics generation."); the governing task's own explicit instruction.

Existing Evidence: Section 20 - Performance Information Flow documented at its current-state shape only, explicitly not redesigned.

Current Conformance: currently evidenced.

Validation Condition: no section of any future P3-02 document proposes a `PerformanceEngine` methodology change or a TD-004 resolution.

Scope Boundary: this requirement is itself a scope boundary.

Traceability: Implementation Baseline (P3-02/P3-03 unit definitions); TD-004.

---

## 33. Non-Goals

Consistent with Section 3 and the governing task's own explicit exclusion list: no change to the P3-01-ratified execution ordering; no strategy, regime-model, or Executor redesign; no lifecycle-semantics change; no Position, PnL, or Risk formula change; no Performance-metric redesign (TD-004 remains P3-03's); no Persistence, Recovery, or Schema Evolution design (ADR-012, Deferred Scope); no Operator Lifecycle Control design (TD-007); no parallel or asynchronous execution design; no concrete implementation, Python signature, or file diff; no test specification; no long-duration run execution.

## 34. Functional Requirement Catalogue

| ID | Title | Current Conformance |
|---|---|---|
| P3-02-FR-001 | CanonicalState.get() Read-Contract Definition | unresolved |
| P3-02-FR-002 | Canonical Working State Internal-Only Consumption | currently evidenced |
| P3-02-FR-003 | Tick-Complete Result Object-Identity Isolation | not currently met |
| P3-02-FR-004 | Published Object Fresh-Construction Consistency | not currently met (Performance Metrics) |
| P3-02-FR-005 | Explicit, Independently Verifiable Producer-Consumer Contracts | partially evidenced |
| P3-02-FR-006 | Writer-on-Behalf-Of Exclusivity (Re-Verification) | currently evidenced |
| P3-02-FR-007 | CanonicalEnforcer Return-Value Contract Consistency | not currently met |
| P3-02-FR-008 | Semantic Continuity of Upstream Information | currently evidenced |
| P3-02-FR-009 | No Downstream Reconstruction | currently evidenced |
| P3-02-FR-010 | Runtime Event Single-Transition Integrity | currently evidenced |
| P3-02-FR-011 | Lifecycle History Immutability and Non-Duplication | currently evidenced |
| P3-02-FR-012 | Position Information Flow Conformance | currently evidenced |
| P3-02-FR-013 | Cross-Tick Component Private-State Self-Consistency | not currently met |
| P3-02-FR-014 | Financial Information Flow Conformance | currently evidenced |
| P3-02-FR-015 | Risk Information Flow Conformance | currently evidenced |
| P3-02-FR-016 | Performance Information Flow Current-State Description | partially evidenced |
| P3-02-FR-017 | No Unauthorized Consumer Mutation, Independently Verifiable | not yet independently evidenced |
| P3-02-FR-018 | Failure Information Flow Conformance | currently evidenced (P3-01 portion); see FR-013 |
| P3-02-FR-019 | HOLD and No-Execution Information Flow Conformance | currently evidenced |
| P3-02-FR-020 | Alternative Information Path Exclusivity | partially evidenced |
| P3-02-FR-021 | Complete Object-Level Traceability | currently evidenced |
| P3-02-FR-022 | Deterministic Information Flow | currently evidenced (cross-instance); RR-001 noted |
| P3-02-FR-023 | P3-01 Non-Reopening | currently evidenced |
| P3-02-FR-024 | P3-03 Non-Preemption | currently evidenced |

Twenty-four Functional Requirements in total.

## 35. ADR Traceability

| ADR | Governing FR(s) |
|---|---|
| ADR-001 (CanonicalState as SSOT) | FR-001, FR-011 |
| ADR-002 (Event-Driven Runtime Evolution) | FR-009, FR-010 |
| ADR-003 (TradeLifecycle as Authoritative Trade Model) | FR-011, FR-016 |
| ADR-004 (Position Represents Current Market Exposure) | FR-012 |
| ADR-005 (Profit and Loss Accounting) | FR-014 |
| ADR-006 (Canonical Financial State Ownership) | FR-014 |
| ADR-007 (Risk Evaluation as a Pure Computational Layer) | FR-015 |
| ADR-008 (Performance Ownership) | FR-016, FR-024 |
| ADR-009 (Partial Trade Closure and Position Netting) | FR-012 (not reopened) |
| ADR-010 (Deterministic Runtime Execution Ordering) | FR-002, FR-023 |
| ADR-011 (Runtime Failure Handling) | FR-018 |
| ADR-012 (Deferred Persistence/Recovery/Schema Evolution) | Section 33 (Non-Goals); no FR reopens it |

All twelve ADRs are traced to at least one Functional Requirement or explicitly confirmed as a bounding Non-Goal.

## 36. Architecture-Invariant and Acceptance-Criteria Traceability

| Invariant | Governing FR(s) |
|---|---|
| AI-001 (Single Source of Truth) | FR-001 |
| AI-002 (Unique Ownership) | FR-001, FR-005 |
| AI-003 (Separation of Ownership and Computation) | FR-006, FR-007 |
| AI-004 (Immutable Lifecycle History) | FR-009, FR-011 |
| AI-005 (Deterministic Execution) | FR-013, FR-022 |
| AI-006 (Deterministic Information Flow) | FR-022 |
| AI-007 (Semantic Continuity) | FR-008 |
| AI-008 (Explicit Runtime Events) | FR-010 |
| AI-009 (Tick Completeness) | FR-002, FR-003 |
| AI-012 (Operational and Historical Separation) | FR-011 |
| AI-013 (Architectural Minimality) | FR-020 |
| AI-014 (Architectural Traceability) | FR-021 |

| Acceptance Criterion | Governing FR(s) |
|---|---|
| AC-001 (Canonical Runtime Ownership) | FR-001, FR-006 |
| AC-002 (Unique Information Ownership) | FR-005, FR-017 |
| AC-003 (Separation of Ownership and Computation) | FR-006, FR-007 |
| AC-004 (Lifecycle Integrity) | FR-011 |
| AC-005 (Financial Integrity) | FR-014 |
| AC-006 (Canonical Runtime State) | FR-001, FR-003 |
| AC-007 (Risk Evaluation) | FR-015 |
| AC-008 (Performance Evaluation) | FR-016 |
| AC-009 (Tick Completion) | FR-002, FR-003 |
| AC-010 (Information Flow) | FR-005, FR-008, FR-009, FR-017 |
| AC-011 (Scientific Traceability) | FR-021 |
| AC-012 (Deterministic Behaviour) | FR-022 |

Every Architecture Invariant and Acceptance Criterion named by the governing task is traced to at least one Functional Requirement.

## 37. Prior-Certification Compatibility

P2-02A, P2-03, and P2-04 (Architecture and Final Certification) are re-confirmed compatible: no Position, Financial, or Risk ownership, formula, or non-mutation contract is reopened or contradicted by any Functional Requirement in Section 32; FR-012 explicitly re-affirms P2-02A's own pre-trade-view reading rather than superseding it. P3-01 (Architecture, Specification, Final Certification) is re-confirmed compatible: no execution-ordering, Tick-Complete-Publication, Failed-Tick, or HOLD/rejection decision is reopened (FR-018, FR-019, FR-023); the P3-01-forwarded item (CUO-01) is formally received into this unit's own scope (FR-001), not reinterpreted.

## 38. Technical-Debt and Cross-Unit Traceability

- **TD-004** (Lifecycle-based Performance Evaluation, Target Phase P3): re-confirmed unmodified (Section 5); its own current-state manifestation is documented (Section 20, FR-016) without advancing its resolution (FR-024).
- **TD-007** (RunLoop Lifecycle Control Surface, Target Phase Future Phase-2 Runtime Control Unit): re-confirmed unmodified (Section 5); not addressed by any Functional Requirement in this document.
- **CUO-01**: received into this unit's own scope, converted from a Cross-Unit Observation into Functional Gap FG-001/Requirement FR-001 (Section 8, Section 26).
- **VC-01** (Tick-Complete Publication realized by aggregate incremental `apply_*` calls): not reopened; the eleven-call aggregate mechanism itself remains exactly as P3-01 certified it. This document's own FR-003 concerns the *stability of the returned reference after* Tick Completion, a distinct property VC-01 does not itself address.
- **Post-Exception Financial/Lifecycle Divergence**: re-examined, not resolved (Section 21, Section 30, RR-002); a newly-identified, structurally related, but distinct instance is recorded as Functional Gap FG-005/Requirement FR-013.

## 39. Open Questions

**OQ-001.** Soll `CanonicalState.get()` Referenz-, Shallow-Copy-, Deep-Copy- oder Read-only-View-Semantik besitzen? (CUO-01, FR-001.)

**OQ-002.** Muss ein Tick-Complete Snapshot gegen spaetere interne und externe Mutation isoliert sein? (FR-003.)

**OQ-003.** Muss Snapshot-Stabilitaet ueber nachfolgende Ticks garantiert werden? (FR-003, empirically shown currently not the case for the top-level container and for Performance Metrics.)

**OQ-004.** Muessen interne Consumer explizit Read-only Views erhalten? (FR-002, FR-005, FR-017.)

**OQ-005.** Welche direkten `CanonicalState`-Schreibpfade sind zulaessig? (FR-006; currently exactly one, Runtime Tick, already Matrix-named - this question concerns whether that remains the sole permitted exception or whether any future exception may be added.)

**OQ-006.** Welche Writer-on-Behalf-Of-Pfade muessen vollstaendig ueber `CanonicalEnforcer` laufen? (FR-006, FR-007.)

**OQ-007.** Welche Runtime-Objekte duerfen Derived Views sein? (FR-004; currently Position/Strategy Selection/Execution Decision/Execution Event behave this way by convention, Performance Metrics does not.)

**OQ-008.** Welche verschachtelten Strukturen benoetigen Isolationsgarantien? (FR-003, FR-004.)

**OQ-009.** Wie wird Post-Exception Divergence informationsseitig klassifiziert - fuer den bereits benannten TradeLifecycleEngine/CanonicalState-Fall und fuer den in diesem Dokument neu identifizierten PositionEngine-eigenen Fall (FR-013) gemeinsam oder getrennt? (Section 21, Section 30.)

**OQ-010.** Welche Information-Flow-Fragen bleiben P3-03 vorbehalten? (FR-016, FR-024; currently: `PerformanceEngine`'s own decision-versus-outcome accounting basis, TD-004.)

**OQ-011 (neu, dieses Dokument).** Soll `PerformanceEngine`'s aktueller Publikationsmechanismus (dieselbe mutable `self.stats`-Referenz bei jedem Aufruf) durch eine strukturell isolierte Publikation ersetzt werden, oder genuegt eine dokumentierte, bewusste Ausnahme vom allgemeinen Fresh-Construction-Muster? (FR-004.)

**OQ-012 (neu, dieses Dokument).** Soll fuer `PositionEngine`'s eigenen cross-tick privaten State nach einem unterbrochenen Position Update ein Konsistenzsicherungs- oder Wiederherstellungsmechanismus eingefuehrt werden, oder bleibt dies analog zu Post-Exception Financial/Lifecycle Divergence ein dokumentiertes, nicht aufgeloestes Residual Risk? (FR-013.)

**OQ-013 (neu, dieses Dokument).** Sollen `position_sizing.py` und `state_modulation.py` denselben Phase-6-Dispositionspfad erhalten wie die vier bereits von P3-01 benannten inaktiven Verzeichnisse, oder erfordert ihre Lage innerhalb von `run_engine/core/` selbst eine gesonderte Behandlung? (FR-020, DG-001.)

No question above is decided by this document.

## 40. Functional Readiness Decision

Every theme the governing task requires ("Zu analysierende Themen," 22 items) has been examined in Sections 7 through 24. Every item the governing task requires be "besonders kritisch" prueft has been addressed with direct, and in five cases newly-obtained empirical, evidence (Section 12, Section 13). Twenty-four Functional Requirements are derived (Section 32), five Functional Gaps are identified (Section 26), four Verified Conformant Findings are ratified (Section 28), two Documentation Gaps and one Verification Gap are recorded (Section 29), two Residual Risks are recorded (Section 30), and thirteen Open Questions are documented without being decided (Section 39). CUO-01 is formally received into this unit's own scope (Section 8, Section 38). No Architecture Decision is made; no runtime file is modified; no ADR is created.

**Functional Readiness: READY.** This document is sufficient to proceed to the P3-02 Scientific Dependency Analysis. No further repository investigation is required before that step, though the SDA itself must re-verify every finding here against the repository state at its own drafting time, per this governance chain's own established discipline.

## 41. Internal Consistency Review

**Scientific Consistency Review.** Every claim in Sections 7 through 25 traces to a specific, cited source-file location, a specific Baseline provision, or a specific empirical probe executed during this document's own drafting (Section 12, Section 13); no claim is asserted without one of these three groundings. PASS.

**Architecture Consistency Review.** No section of this document makes an Architecture Decision; every normative SHALL/SHALL NOT statement in Section 32 states a requirement, not a chosen mechanism; every Scope Boundary field explicitly excludes the corresponding solution choice. PASS.

**Scope Review.** Section 33 (Non-Goals) and FR-023/FR-024 jointly confirm no P3-01 ordering/failure/HOLD decision and no P3-03 Performance-methodology decision is reopened anywhere in this document. PASS.

**Information Flow Review.** Sections 17-19 confirm Position, Financial, and Risk information flow each match the Target Information Flow's own stated path exactly; Section 20 confirms Performance information flow is described, not redesigned. PASS.

**Mutation and Aliasing Review.** Section 12 and Section 13 are internally consistent with each other and with Section 26 (Functional Gaps FG-002, FG-003, FG-005 trace directly to the empirical findings of Sections 12-13); Section 28 (Verified Conformant Findings VCF-001, VCF-004) explicitly excludes the objects Section 26 names as gaps, with no contradiction between the two sections. PASS.

**Ownership Review.** No Functional Requirement in Section 32 introduces a new Authoritative Owner or Computational Authority; FR-001, FR-003, FR-004, FR-007 each concern read-contract, object-identity, or return-value-shape properties, explicitly distinct from ownership itself (re-stated in each requirement's own Scientific Rationale field). PASS.

**Terminology Review.** "Functionally identical" is used exclusively for Python-object, dictionary, and runtime-result comparisons throughout this document (Section 6, Section 24). "Byte-identical" does not occur anywhere in this document as a comparison claim; its only occurrence is this sentence's own meta-discussion of the term and Section 6's own definitional statement of the rule, since no file- or git-blob-level comparison was performed or required by this document. "Hidden Coupling" and "Aliasing" are used exactly as defined in Section 6 throughout. PASS.

**Repository Consistency Review.** Every file path, line reference, and code excerpt cited in Sections 5, 7, and 9-24 was independently re-read or re-executed during this document's own drafting, not inherited unchecked from any prior document. PASS.

**Runtime Consistency Review.** No runtime file under `run_engine/` was modified; every empirical probe in Sections 12-13 was executed against the unmodified, currently-committed runtime, via temporary in-memory monkeypatching within the probe script itself, never by editing any repository file. PASS.

**Traceability Review.** Section 35 confirms all twelve ADRs; Section 36 confirms every Architecture Invariant and Acceptance Criterion the governing task names; Section 37 confirms P2-02A/P2-03/P2-04/P3-01 compatibility; Section 38 confirms TD-004/TD-007/CUO-01/VC-01/Post-Exception Divergence disposition. PASS.

**Governance Review.** This document does not create an SDA, CGA, Architecture, Specification, Implementation, or Final Certification; it does not create a new ADR; it stops, as instructed, before the Scientific Dependency Analysis. PASS.

**Independent Self Verification.** Every empirical claim in Sections 12 and 13 was independently executed as a standalone probe against the unmodified runtime during this document's own drafting (not inherited from any P3-01 script), and each probe's own console output was directly inspected before being transcribed into this document's own prose; no probe result was assumed or extrapolated beyond what was actually observed. The two newly-identified findings this document contributes beyond P3-01's own prior work (Performance Metrics aliasing, FG-003; PositionEngine private-state self-inconsistency, FG-005) were each independently reproduced twice during drafting (once during initial investigation, once during this closing verification pass) with identical results both times. No error was found during this document's own closing review requiring correction before delivery.

Status: Internal Consistency Review PASS.
