Document Class:
Functional Requirement Analysis

Document ID:
P3-01-FRA

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
docs/architecture/analysis/P3_01_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-13.md

Depends On:
- docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md
- docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md
- docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md
- docs/architecture/P2_02A_POSITION_OWNERSHIP_ARCHITECTURE_V1_2026-07-10.md
- docs/architecture/P2_02A_POSITION_OWNERSHIP_SPECIFICATION_V1_2026-07-10.md
- docs/architecture/P2_03_FINANCIAL_OWNERSHIP_ARCHITECTURE_V1_2026-07-11.md
- docs/architecture/P2_03_FINANCIAL_OWNERSHIP_SPECIFICATION_V1_2026-07-11.md
- docs/architecture/P2_04_RISK_OWNERSHIP_ARCHITECTURE_V1_2026-07-13.md
- docs/architecture/P2_04_RISK_OWNERSHIP_SPECIFICATION_V1_2026-07-13.md
- docs/architecture/certification/P2_03_FINAL_CERTIFICATION_V1_2026-07-11.md
- docs/architecture/certification/P2_04_FINAL_CERTIFICATION_V1_2026-07-13.md
- current runtime code at HEAD fd22ce130e93261b63830b63600f9e651f7ad496

Referenced By:
- future P3-01 Scientific Dependency Analysis
- future P3-01 Capability Gap Analysis
- future P3-01 Architecture
- future P3-01 Specification
- future P3-01 Certification

---

# P3-01 Functional Requirement Analysis

## 1. Purpose

This document is the Functional Requirement Analysis for P3-01 (Deterministic Execution Ordering), the first Phase 3 implementation unit named in `RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md`. The Implementation Baseline names P3-01's objectives verbatim as: "Implement ADR-010 execution sequence. Verify Executor integration. Verify Tick-Complete Snapshot publication."

This document does not decide architecture. It does not define interfaces. It does not implement code. Its sole purpose is to establish, from direct repository inspection, the verified current state of the Run Engine's tick execution ordering, its Canonical Working State behaviour, its Tick-Complete publication behaviour, its failure and no-execution behaviour, and its determinism evidence, and to derive the functional requirements a later Scientific Dependency Analysis, Capability Gap Analysis, Architecture, and Specification must satisfy.

## 2. Scope

In scope: the single normative per-tick execution sequence (ADR-010), each named stage's ordering position and the ordering dependencies between them, the Canonical Working State concept during a tick, the Tick-Complete CanonicalState Snapshot concept at tick boundaries, HOLD/no-execution and rejected/failed lifecycle transition behaviour with respect to stage ordering (not with respect to the financial or risk formulas themselves, already certified), the absence or presence of alternative active execution paths, the absence or presence of hidden mutation or side effects outside the approved publication path, deterministic replay of the complete stage sequence, and compatibility with every already-certified P2-02A, P2-03, and P2-04 ownership contract.

Out of scope (Section 15 for full detail): strategy logic changes, regime model changes, Executor redesign, lifecycle semantics changes, Position formula changes, PnL formula changes, Risk formula changes, Performance metric redesign (TD-004, P3-03), Persistence, Recovery, Schema Evolution (ADR-012, Deferred Scope), parallel or asynchronous execution, concrete implementation, test specification, and long-duration run execution. P3-02 (Information Flow Validation) and P3-03 (Performance Validation) are named, adjacent, not-yet-started units; this document establishes an explicit boundary against each (Section 23.9) but does not perform either unit's own analysis.

## 3. Binding Baseline

- `docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md` - ADR-002 (Event-Driven Runtime Evolution), ADR-010 (Deterministic Runtime Execution Ordering), ADR-011 (Runtime Failure Handling), and by reference ADR-001, ADR-003 through ADR-009, ADR-012; the Runtime Ownership Matrix; the Target Information Flow (Principles IF-001 through IF-006, the Tick Completion Contract); Architecture Invariants AI-001 through AI-015 (in particular AI-005, AI-006, AI-007, AI-008, AI-009, AI-014); Scientific Acceptance Criteria AC-001 through AC-015 (in particular AC-009, AC-010, AC-011, AC-012); the "Canonical Working State" and "Tick-Complete Snapshot" Scientific Definitions.
- `docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md` - the P3-01 unit entry ("Deterministic Execution Ordering. Objectives: Implement ADR-010 execution sequence. Verify Executor integration. Verify Tick-Complete Snapshot publication."), naming ADR-002, ADR-008, ADR-010 as Phase 3's primary ADR dependencies.
- `docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md` - TD-004 (Lifecycle-based Performance Evaluation, Target Phase P3, Status "Already Planned"), TD-007 (RunLoop Lifecycle Control Surface, Deferred, Target future Runtime Control Unit).
- `docs/architecture/P2_02A_POSITION_OWNERSHIP_ARCHITECTURE_V1_2026-07-10.md` - Section 19 (Information Flow), re-tracing `RunLoop.step()`'s exact call order at a prior HEAD; the pre-trade/post-trade temporal model (P2-02A-AD-005).
- `docs/architecture/P2_03_FINANCIAL_OWNERSHIP_ARCHITECTURE_V1_2026-07-11.md` and `docs/architecture/P2_03_FINANCIAL_OWNERSHIP_SPECIFICATION_V1_2026-07-11.md` - Section 6 (Financial Information Flow) and Section 16 (Runtime Ordering Specification), the currently governing, certified eighteen-step ordering that this document independently re-verifies against the present runtime (Section 6 below).
- `docs/architecture/P2_04_RISK_OWNERSHIP_ARCHITECTURE_V1_2026-07-13.md` and `docs/architecture/P2_04_RISK_OWNERSHIP_SPECIFICATION_V1_2026-07-13.md` - confirmation that Risk Evaluation's ordering position (after Financial Accounting, before Performance Evaluation) was preserved unchanged through P2-04's own certified implementation.
- `docs/architecture/certification/P2_03_FINAL_CERTIFICATION_V1_2026-07-11.md` and `docs/architecture/certification/P2_04_FINAL_CERTIFICATION_V1_2026-07-13.md` - the certified baseline this document treats as immutable except where this document's own findings identify a gap not previously certified.

ADR-010's binding text, quoted for traceability:

"The runtime SHALL execute the following deterministic processing sequence during every runtime tick. 1. Runtime Tick Acquisition 2. State Acquisition and Normalization 3. Regime Classification 4. Strategy Selection 5. Execution Decision Generation 6. Executor Event Generation 7. TradeLifecycle Update 8. Position Update 9. Financial Accounting 10. Risk Evaluation 11. Performance Evaluation 12. Tick-Complete CanonicalState Publication. Only after completion of Step 12 may external downstream consumers observe the resulting Tick-Complete CanonicalState Snapshot. Intermediate runtime state shall remain internal to the execution pipeline."

The Architecture Baseline's Tick Completion Contract, quoted for traceability:

"A runtime tick is complete only when all mandatory runtime stages have executed successfully. Completion requires: Lifecycle updated, Position updated, Financial state updated, Risk evaluated, Performance evaluated, CanonicalState published. Only after successful completion shall the Tick-Complete Snapshot become externally observable. No downstream runtime component may consume intermediate runtime state."

The Architecture Baseline's Canonical Working State and Tick-Complete Snapshot definitions, quoted for traceability:

"Canonical Working State is the internal canonical state under construction during one runtime tick. It may be consumed only by components whose execution order has already been reached. It is not externally observable." "A Tick-Complete Snapshot is the externally observable canonical runtime state after all mandatory runtime stages have completed for the current tick. RiskEngine and PerformanceEngine consume the Canonical Working State at their assigned execution stage. External downstream consumers consume only Tick-Complete Snapshots. No component may consume state from a future or incomplete execution stage."

## 4. Repository Verification

Repository state, verified directly, not assumed:

- Branch: `run-engine-consolidation-safety` (confirmed via `git branch --show-current`).
- Local HEAD: `fd22ce130e93261b63830b63600f9e651f7ad496` ("Add P2 governance documentation"), matching the stated expected HEAD exactly (confirmed via `git rev-parse HEAD`).
- Remote HEAD: `fd22ce130e93261b63830b63600f9e651f7ad496` (confirmed via `git fetch origin run-engine-consolidation-safety` followed by `git rev-parse origin/run-engine-consolidation-safety`), identical to local HEAD.
- Working tree: one modified file unrelated to `run_engine` (`docs/capabilities/SGF_013_SCIENTIFIC_BEHAVIOUR_REPRESENTATION_2026-06-26.md`) and a set of pre-existing untracked directories (`_chat_handover/`, `_sgf017_context/`, `_ssi_context/`, `backups/`, `claude_final_p1031_review/`, `claude_p1031_patch/`, `claude_p1_03b_review/`, `codex_p1_03_review/`, `engine/regime_classifier.py`, `live_logs/`, `outputs/`, `review_packages/`, `runtime_runs/`) - none inside `run_engine/`, none touched by this analysis. `run_engine/` is confirmed clean (`git status --short run_engine/` returns no output).
- All governing documents named in Section 3 confirmed present at their stated paths.

Files read in full for this analysis: `run_engine/main.py`, `run_engine/core/loop.py`, `run_engine/core/state.py`, `run_engine/core/regime.py`, `run_engine/core/strategy.py`, `run_engine/core/execution/executor.py`, `run_engine/core/trade_lifecycle.py`, `run_engine/core/position.py`, `run_engine/core/pnl.py`, `run_engine/core/risk.py`, `run_engine/core/performance.py`, `run_engine/core/canonical_state.py`, `run_engine/core/canonical_enforcer.py`, `run_engine/core/decision.py`.

Repository-wide search performed for (case-insensitive): `RunLoop`, `step(`, `Canonical Working State`, `Tick-Complete`, `publication`, `apply_`, `update_`, `lifecycle`, `execution`, `position`, `pnl`, `risk`, `performance`, `deterministic`, `replay`, `ordering`, `sequence`, `mutation`, `side effect`. Findings that bear directly on this document's conclusions are cited by file and line throughout Sections 6 through 11; the complete inactive-path classification is given in Section 6.4.

Confirmed inactive (not imported by `run_engine/core/loop.py` or any of its own active-path dependencies, verified by direct repository-wide import search):

- `run_engine/core/decision.py` (`DecisionEngine`) - a second, structurally competing decision-generation class (`decide(state)`, deterministic price-parity signal), never imported anywhere in the repository (confirmed: zero occurrences of `DecisionEngine` or `from run_engine.core.decision` outside its own definition line).
- `run_engine/runtime/` (`recovery.py`, `snapshot.py`, `state_memory.py`, `strategy_memory.py`, `strategy_weights.py`, `pnl_engine.py`, `position_state.py`, `risk.py`, `performance_analytics.py`, `regime_stability.py`, `strategy_selector.py`, `regime_execution_gate.py`) - a parallel runtime implementation tree, explicitly named as Phase 6 (Repository Consolidation) territory by the Architecture Baseline's own Implementation Governance section; confirmed not imported by any file under `run_engine/core/`.
- `run_engine/execution/` (`executor.py`, `adapter.py`, `safety.py`) - a second, top-level Executor implementation, distinct from the active `run_engine/core/execution/executor.py`; confirmed not imported by any file under `run_engine/core/`.
- `run_engine/feedback/tracker.py` and `run_engine/logging/logger.py` - confirmed not imported by any file under `run_engine/core/`.
- `run_engine/core/config.py`, `run_engine/core/state_modulation.py`, `run_engine/core/features.py`, `run_engine/core/position_sizing.py`, `run_engine/core/equity_stabilizer.py` - confirmed not imported by `run_engine/core/loop.py` or by any of the eleven modules `loop.py` itself imports (Section 6.1); `position_sizing.py` and `equity_stabilizer.py` carry the same inactive classification already established by the P2-02A and P2-03 Functional Requirement Analyses.

This inactive-path classification directly answers the governing task's instruction to check whether alternative or inactive execution paths exist: one alternative decision-generation path and four entire alternative runtime-implementation directories exist in the repository; none participates in the active `RunLoop.step()` execution path; all remain correctly out of P3-01's scope as Phase 6 Repository Consolidation territory (Section 15).

## 5. Scientific Definitions

These definitions are restated from the Architecture Baseline, not newly invented, and govern the rest of this document.

**Deterministic Runtime Execution Ordering** - per ADR-010: the single, twelve-stage processing sequence the runtime SHALL execute during every runtime tick, terminating in a Tick-Complete CanonicalState Publication step, after which alone external downstream consumers may observe the resulting Tick-Complete CanonicalState Snapshot.

**Canonical Working State** - per the Architecture Baseline: the internal canonical state under construction during one runtime tick, consumable only by components whose execution order has already been reached, not externally observable.

**Tick-Complete Snapshot** - per the Architecture Baseline: the externally observable canonical runtime state after all mandatory runtime stages have completed for the current tick; no component may consume state from a future or incomplete execution stage.

**Tick-Sequence Determinism** (this document's own working definition, not previously separately named) - the property that an identical ordered sequence of runtime tick inputs, processed from an identical initial state, produces an identical ordered sequence of runtime outputs and an identical final Tick-Complete Snapshot at every tick boundary, per AI-005 and AI-006. This is distinct from **per-call statelessness** (the property, required only of specific components such as `RiskEngine` under ADR-007/Rule OM-007, that a single method call's output depends only on its explicit parameters, not on any instance state). Components such as `RegimeClassifier` and `StrategySelector` legitimately hold cross-tick instance state (a rolling market window, a cooldown counter) without violating Tick-Sequence Determinism, provided their output remains a deterministic function of the complete input sequence observed so far. This document treats the two properties as scientifically distinct and does not conflate a component's cross-tick statefulness with a violation of ADR-010 or AI-005.

**Runtime Failure Event** (already defined by ADR-002/ADR-011, restated here for this document's own scope) - the immutable lifecycle record generated when a lifecycle transition is rejected (`INVALID_EXECUTION_QUANTITY`, `NO_ACTIVE_TRADE`, `OVER_CLOSE_QUANTITY`, `UNSUPPORTED_EXECUTION_ACTION`). Distinct from an **unhandled runtime exception** (a Python exception propagating out of `RunLoop.step()` itself), which ADR-011 does not name and which this document treats as a separate concern (Section 9.3, Section 16).

**Writer-on-Behalf-Of Path** - per the Architecture Baseline: the mechanism by which a computed value is published into `CanonicalState`. This document distinguishes, for the first time as an explicit finding rather than an assumption, between values published via `CanonicalEnforcer`'s named `apply_*` methods and values written by direct `CanonicalState.update_*()` calls made by `RunLoop` itself without an intervening `CanonicalEnforcer` method (Section 7.3).

## 6. Current Runtime Execution Path

### 6.1 Verified Active Path

Exactly one `RunLoop` class and exactly one `step()` method exist in the repository (confirmed: `run_engine/core/loop.py` is the sole file matching a repository-wide search for `class RunLoop` or `def step(`). `run_engine/main.py` is the sole runtime entry point, importing only `RunLoop` and invoking `engine.step(tick_data)` in an unconditional loop (`main.py:1,6,21`). `RunLoop.__init__` (`loop.py:16-31`) instantiates exactly eleven collaborator objects - `StateEngine`, `RegimeClassifier`, `StrategySelector`, `PositionEngine`, `TradeLifecycleEngine`, `RiskEngine`, `Executor` (from `run_engine.core.execution`), `PnLEngine`, `PerformanceEngine`, `CanonicalState`, `CanonicalEnforcer` - matching exactly the eleven-import set every prior certification in this governance chain (P2-03, P2-04) has already confirmed unchanged.

### 6.2 Verified Current Sequence

Traced directly from `run_engine/core/loop.py:33-113` (`RunLoop.step()`), independently re-derived line by line for this document rather than inherited from any prior document's account:

1. `self.enforcer.apply_runtime_status("RUNNING")` (`loop.py:35`) - Runtime Tick Acquisition begins; Runtime Status set via `CanonicalEnforcer`.
2. `state = self.state_engine.update(tick)` (`loop.py:37`) - State Acquisition and Normalization.
3. `self.cstate.update_tick(runtime_tick, price)` (`loop.py:42`) - tick and price recorded directly into `CanonicalState`, not via `CanonicalEnforcer` (Section 7.3, Finding F-01).
4. `regime = self.regime_classifier.classify(state)` (`loop.py:44`) - Regime Classification.
5. `self.cstate.update_regime(regime)` (`loop.py:45`) - regime recorded directly into `CanonicalState`, not via `CanonicalEnforcer` (Section 7.3, Finding F-01).
6. `position_pre = self.cstate.get()["position"]` (`loop.py:47`) - pre-trade Position view read, per the certified P2-02A-AD-005 temporal model.
7. `weights = self.strategy_selector.select(state, regime, position_pre)` (`loop.py:49`); `self.enforcer.apply_strategy_selection(weights)` (`loop.py:50`) - Strategy Selection, part 1.
8. `decision = self.strategy_selector.decide(state, regime, weights)` (`loop.py:52`); `self.enforcer.apply_execution_decision(decision)` (`loop.py:53`) - Execution Decision Generation.
9. `execution = self.execution_engine.execute(decision, position_pre)` (`loop.py:55`) - Executor Event Generation.
10. `trade_event = self.trade_lifecycle_engine.on_execution(execution, state)` (`loop.py:57`) - TradeLifecycle Update, part 1.
11. `lifecycle_position = self.trade_lifecycle_engine.current_position()` (`loop.py:59`) - TradeLifecycle Update, part 2.
12. `position = self.position_engine.update_post_trade(execution, state, lifecycle_position)` (`loop.py:61-65`); `self.enforcer.apply_position(position)` (`loop.py:66`) - Position Update.
13. Prior canonical financial values read (`loop.py:68-70`); `pnl = self.pnl_engine.update(trade_event, position_pre["entry_price"])` (`loop.py:72`); `self.enforcer.apply_pnl(pnl)` (`loop.py:73`) - Financial Accounting, part 1 (Realized PnL, event).
14. `equity_state = self.pnl_engine.compute_equity(...)` (`loop.py:75-81`); `self.enforcer.apply_realized_pnl_cumulative(...)`, `apply_equity(...)`, `apply_peak_equity(...)` (`loop.py:86-88`) - Financial Accounting, part 2 (cumulative Realized PnL, Equity, Peak Equity).
15. `canonical_state = self.cstate.get()` (`loop.py:90`) - the Canonical Working State snapshot `RiskEngine` consumes.
16. `risk = self.risk_engine.check(canonical_state, position, regime)` (`loop.py:92`); `self.enforcer.apply_risk(...)` (`loop.py:93`) - Risk Evaluation.
17. `performance = self.performance_engine.update(decision, pnl, regime, trade_event)` (`loop.py:95`); `self.enforcer.apply_performance_metrics(performance)` (`loop.py:96`) - Performance Evaluation.
18. `return {...}` (`loop.py:98-113`) - a tick-result dictionary composed partly of a fresh `self.cstate.get()` read (`loop.py:100`) and partly of local variables already produced in steps above; not itself a distinct publication action - Stage 12 is instead realized by the aggregate effect of steps 1 through 17's own already-executed publications (Section 8, Verified Conformant Finding VC-01).

This eighteen-step trace is independently confirmed, by direct source comparison, to match `P2_03_FINANCIAL_OWNERSHIP_SPECIFICATION_V1_2026-07-11.md`'s own Section 16 Runtime Ordering Specification exactly, step for step. Since `P2_04_FINAL_CERTIFICATION_V1_2026-07-13.md` (Section 5) already independently confirmed `run_engine/core/loop.py` is git-blob-identical to the P2-03-certified baseline, this document's own fresh trace against the current HEAD constitutes independent re-confirmation, not mere inheritance, that the certified ordering remains exactly as certified.

### 6.3 Mapping to ADR-010's Twelve Named Stages

| ADR-010 Stage | Realized By (Section 6.2 steps) | Ordering Conformance |
|---|---|---|
| 1. Runtime Tick Acquisition | Step 1 | currently evidenced |
| 2. State Acquisition and Normalization | Step 2 | currently evidenced |
| 3. Regime Classification | Step 4 | currently evidenced |
| 4. Strategy Selection | Step 7 | currently evidenced |
| 5. Execution Decision Generation | Step 8 | currently evidenced |
| 6. Executor Event Generation | Step 9 | currently evidenced |
| 7. TradeLifecycle Update | Steps 10-11 | currently evidenced |
| 8. Position Update | Step 12 | currently evidenced |
| 9. Financial Accounting | Steps 13-14 | currently evidenced |
| 10. Risk Evaluation | Step 16 | currently evidenced |
| 11. Performance Evaluation | Step 17 | currently evidenced |
| 12. Tick-Complete CanonicalState Publication | Step 18, realized as the aggregate effect of Steps 1-17's publications (Section 8, VC-01) | currently evidenced |

All twelve named ADR-010 stages are realized, in strictly increasing source order, by exactly one corresponding block of `RunLoop.step()`, with no stage skipped, reordered, or duplicated. Stage 12's own realization differs from a single, distinct, dedicated call, but is verified conformant with the governing normativity principle already established by `P2_03_FINANCIAL_OWNERSHIP_SPECIFICATION_V1_2026-07-11.md`'s own Section 16 (observable dependencies and results govern conformance, not internal code structure); Section 8 documents this precisely.

### 6.4 Absence of Alternative Active Paths

Confirmed by Section 4's repository-wide import search: no second `RunLoop`-equivalent orchestrator exists on the active path; `run_engine/core/decision.py`'s `DecisionEngine` and the four inactive directories (Section 4) are structurally isolated from `run_engine/core/loop.py` and its eleven active collaborators. No implicit reordering dependency was found that exists only because of internal code structure rather than the ADR-010 sequence itself: every ordering dependency identified in Section 6.2 (for example, step 6 reading `position_pre` before step 12 computes the post-trade `position`) is traceable to an explicit ADR (ADR-004, P2-02A-AD-005) rather than to an accidental artifact of source-line order.

## 7. Current Canonical Working State Behaviour

### 7.1 Consumption Boundary

`RiskEngine.check()` (Step 16) is the sole component that consumes a Canonical Working State snapshot mid-tick (`canonical_state = self.cstate.get()` at `loop.py:90`, immediately before the call at `loop.py:92`) rather than a value passed directly from an upstream step's return value. This snapshot is taken after Financial Accounting (Step 13-14) has already published Equity and Peak Equity, and before Performance Evaluation (Step 17) runs, matching ADR-010's Stage 10 position exactly. No component reads a Canonical Working State snapshot before its own ADR-010 stage has been reached; no component reads a snapshot corresponding to a future, not-yet-executed stage. This is currently evidenced by direct trace (Section 6.2) for every one of the eighteen steps.

### 7.2 Reference Semantics of `CanonicalState.get()` - a Cross-Unit Observation, Not a P3-01 Functional Gap

`CanonicalState.get()` (`canonical_state.py:107-109`) returns `self.state` directly - the same live dictionary object `CanonicalState` itself mutates on every subsequent `update_*()` call - not a copy, not a read-only view, and not a distinct object per call. Consequently, the Canonical Working State a mid-tick consumer (`RiskEngine`, Step 16) receives and the eventual Tick-Complete Snapshot returned to the tick's caller (Step 18) are, at the Python object-identity level, the same underlying dictionary at different points in its own mutation history, not two structurally distinct representations.

This observation does not, by itself, constitute a currently unmet P3-01 requirement. No ADR, Architecture Invariant, or Acceptance Criterion in the Binding Baseline (Section 3) requires `CanonicalState.get()` to return a defensive copy. The governing normative rule is Rule OM-004 ("Primary Consumers shall never modify consumed information"), which is a consumer-behaviour obligation, not a producer-side structural obligation on `CanonicalState.get()`'s own return mechanism. Every consumer this analysis reached was independently checked against Rule OM-004: `RiskEngine`'s non-mutation is independently certified (`P2_04_FINAL_CERTIFICATION_V1_2026-07-13.md`, Sections 15-16); `StrategySelector.select()` and `Executor.execute()` - both consumers of the equally live-referenced `position_pre` sub-dictionary (`loop.py:47`) - read their Position argument exclusively via `.get(...)`, with no assignment into it anywhere in either method body (confirmed by direct source read); the tick-result dictionary's own embedded `CanonicalState.get()` read (`loop.py:100`) is only ever printed by `main.py`, never mutated. Rule OM-004 is therefore currently evidenced as upheld by every consumer this analysis reached; no violation exists today.

What remains unaddressed is the robustness of this conformance against a future consumer that does not uphold Rule OM-004 - a data-flow/coupling question, not an ordering question, and therefore outside this document's own scope (Section 2). This is recorded as Cross-Unit Observation CUO-01 (Section 12.2), directed to the P3-02 (Information Flow Validation) unit, whose own Baseline objective text ("Remove hidden coupling") is the more precise textual and architectural home for a shared-mutable-reference concern of this kind. A secondary, general Runtime Safety dimension (robustness against a hypothetical future non-compliant consumer) is noted but not evaluated further here. This document takes no position on whether `CanonicalState.get()` should return a reference or a copy in the future; the existing Architecture Baseline decides neither explicitly, and no such decision is made here.

## 8. Current Tick-Complete Publication Behaviour

### 8.1 Incremental Realization of Stage 12, Consistent With Governing Methodology

Ten distinct `CanonicalEnforcer.apply_*()` calls occur across a single tick (`loop.py:35,50,53,66,73,86,87,88,93,96`), each immediately and individually mutating `CanonicalState`'s live dictionary at the moment it executes, not deferred to a single, final, atomic commit at Step 18. No staging area, no working copy distinct from `CanonicalState.state` itself, and no explicit "publish" or "commit" action distinct from these ten already-incremental writes exists anywhere in `run_engine/core/loop.py`, `canonical_state.py`, or `canonical_enforcer.py` (confirmed: zero occurrences of "commit," "stage," "buffer," or "atomic" as identifiers anywhere in these three files). Step 18's `return {...}` block performs one additional `self.cstate.get()` read (`loop.py:100`) but writes nothing; it is a read and repackage of already-published state, not itself a twelfth, distinct publication action.

This divergence from a literal, single-call realization of ADR-010's Stage 12 label is not, by itself, a departure from this governance chain's own already-certified interpretive methodology. `P2_03_FINANCIAL_OWNERSHIP_SPECIFICATION_V1_2026-07-11.md`, Section 16, states, as a binding, already-certified principle governing every ADR-010 stage: "The specified ordering is normative with respect to observable architectural dependencies, not with respect to internal implementation structure: an implementation remains conformant so long as it preserves the same dependencies, the same temporal semantics, the same consumer contracts, and the same observable runtime results ... it need not structure its internal code identically to the step list itself." That same certified Specification applies this exact principle to ADR-010 Stage 9 (Financial Accounting), realized in its own Section 16 through four separate calls (retrieval of prior values, event-PnL computation and publication, cumulative-PnL/Equity/Peak-Equity computation, and three further separate publications) without this ever being treated as a departure from Stage 9's own single-line naming. Applying the identical, already-governing principle to Stage 12, its realization as the aggregate, cumulative effect of the tick's own ten already-executed `apply_*()` calls is the same class of internal-structure divergence from a single-line ADR-010 label as Stage 9's, not a distinguishable case warranting a different classification.

### 8.2 Observable Guarantee, Verified

No concurrency, threading, multiprocessing, or asynchronous execution construct exists anywhere in `run_engine/core/` (confirmed: zero occurrences of `threading`, `asyncio`, `multiprocessing`, or `concurrent.futures` imports in any active-path file, Section 4). `main.py`'s own driving loop (`main.py:12-30`) calls `engine.step(tick_data)` synchronously and waits for it to return before any subsequent code executes. Under this synchronous, single-threaded execution model, no external actor has any opportunity to call `CanonicalState.get()` while a tick's own incremental publications are still in progress, since nothing else runs concurrently with `step()`. AC-009 ("Every runtime tick produces exactly one externally observable Tick-Complete CanonicalState Snapshot. No downstream runtime component observes partially updated runtime state.") and the Tick Completion Contract's externally-observable-only-after-completion requirement are therefore both currently evidenced as satisfied, independent of Section 8.1's own internal-structure observation.

### 8.3 Residual, Non-Blocking Documentation Question

The guarantee verified in Section 8.2 depends on a precondition - synchronous execution, absence of concurrency, absence of any external mid-tick read path - that is not itself named as an explicit Architecture Invariant or Constraint anywhere in the Binding Baseline (Section 3); it is presupposed rather than codified. This does not affect the guarantee's current validity, independently verified in Section 8.2, and does not by itself constitute an unmet requirement. It is recorded as a residual, non-blocking Open Question (OQ-003, revised, Section 22) for a future Architecture document to consider - specifically, whether this precondition should be explicitly protected by a named Invariant or Constraint, given that P3-01's own Non-Goals (Section 15) already exclude any change to the current synchronous execution model. This document does not decide whether such protection is required, and does not require or propose any atomic publish/commit mechanism.

## 9. Current Failure and No-Execution Behaviour

### 9.1 HOLD / No-Execution Ticks

`StrategySelector.decide()` may return `{"action": "HOLD", ...}` (`strategy.py:47-51,69-73`, either via an active cooldown or as the naturally highest-weighted action). `Executor.execute()` (`executor.py:14-32`) has an explicit `HOLD` branch producing `{"action": "HOLD", "status": "NOOP", "quantity": 0.0}` - a well-formed, non-`None` result. `TradeLifecycleEngine.on_execution()` (`trade_lifecycle.py:64-65`) returns Python `None` for a `HOLD` action, not a `LifecycleEvent`. Every downstream step still executes unconditionally: `PositionEngine.update_post_trade()` (`position.py:37-73`), `PnLEngine.update()` (`pnl.py:9-19`, explicit `trade_event is None` guard returning `0.0`), `PnLEngine.compute_equity()` (`pnl.py:42-72`, falls through its `RUNTIME_FAILURE_EVENT` guard since `getattr(None, "event_type", None)` is `None`, and computes a numerically-unchanged result since `event_pnl` is `0.0`), `RiskEngine.check()` (unconditional), and `PerformanceEngine.update()` (`performance.py:6-9`, `getattr(None, "event_type", None)` again does not match `"RUNTIME_FAILURE_EVENT"`, so a `HOLD`-keyed statistics entry is recorded). No stage is skipped for a `HOLD` tick; every stage runs, with `None`-safe guards at each point that would otherwise require a value derived from a rejected or absent execution. This is currently evidenced by direct source trace of all six affected files.

### 9.2 Rejected Lifecycle Transitions (`RUNTIME_FAILURE_EVENT`)

`TradeLifecycleEngine` generates a `RUNTIME_FAILURE_EVENT` `LifecycleEvent` for four named reasons (`trade_lifecycle.py:56-62,73-78,156-162,189-195,200-205,213-219,246-252`: `INVALID_EXECUTION_QUANTITY`, `UNSUPPORTED_EXECUTION_ACTION`, `NO_ACTIVE_TRADE`, `OVER_CLOSE_QUANTITY`). As with `HOLD`, every subsequent stage still executes unconditionally: `PositionEngine.update_post_trade()` is still called with whatever `lifecycle_position` `current_position()` returns; `PnLEngine.update()`'s `event_type not in {"TRADE_CLOSED", "PARTIAL_CLOSE"}` guard (`pnl.py:23-24`) returns `0.0`; `PnLEngine.compute_equity()`'s explicit `event_type == "RUNTIME_FAILURE_EVENT"` guard (`pnl.py:57-62`) returns the three prior canonical values unchanged; `RiskEngine.check()` runs unconditionally (its own non-mutation of `state`/`position` is independently certified, `P2_04_FINAL_CERTIFICATION_V1_2026-07-13.md` Section 17); `PerformanceEngine.update()`'s explicit `event_type == "RUNTIME_FAILURE_EVENT"` guard (`performance.py:8-9`) returns `self.stats` unchanged. This reproduces, and this document independently re-confirms rather than merely cites, the already-certified P2-03 non-mutation contract (`P2_03_FINAL_CERTIFICATION_V1_2026-07-11.md`, Section 20). No stage is skipped for a rejected transition; only specific financial and performance values are guarded to remain unmodified.

### 9.3 Unhandled Runtime Exceptions

`main.py:14-30` wraps its single call to `engine.step(tick_data)` in a bare `try: ... except Exception as e: print(f"[CRASH] {str(e)}")`, after which the loop unconditionally increments `tick` and continues to the next iteration. No rollback, no `CanonicalState` reset, no partial-publication check, and no distinction between an exception raised before any `apply_*` call and one raised after several `apply_*` calls have already executed (for example, after Step 12's `apply_position` but before Step 16's `apply_risk`) exists anywhere in `main.py` or `loop.py`. If such an exception occurred, `CanonicalState` would retain whatever subset of that tick's ten `apply_*` calls had already executed, with no explicit record that the tick as a whole did not complete, and the next `step()` call would proceed from this state without any special handling. `run_engine/core/loop.py`'s own `if __name__ == "__main__":` block (`loop.py:116-131`) contains no exception handling at all, an even narrower guarantee than `main.py`'s. This condition is not hypothetical in the sense of requiring speculation about whether an exception can occur; it is a structural absence, confirmed by direct reading of both entry points, of any explicit mechanism addressing partial per-tick publication under an unhandled exception, independent of how likely such an exception is under any particular input (Finding F-02, Section 12.1).

## 10. Current Determinism Evidence

`RiskEngine`'s own determinism and statelessness are independently certified (`P2_04_FINAL_CERTIFICATION_V1_2026-07-13.md`, Sections 13-14). `PnLEngine.update()` and `PnLEngine.compute_equity()` are both pure functions of their explicit parameters, holding no instance state that participates in either method's output (confirmed by direct read of `pnl.py`; `self.last_realized_pnl` is written but never read back into either computation, `pnl.py:38,74-75`). `Executor.execute()` is a pure function of its two parameters (`executor.py:5-32`, no instance attribute is read or written anywhere in the class body). `PositionEngine`, `RegimeClassifier`, and `StrategySelector` each hold legitimate cross-tick instance state (Section 5's Tick-Sequence Determinism definition); none of the three was found, by direct read, to reference any non-deterministic input (no random-number source, no wall-clock read, confirmed by repository-wide search for `random`, `time.time`, `datetime.now` within `run_engine/core/` - no occurrence in any active-path file).

No repository-wide replay test, deterministic-output comparison, or golden-output fixture exists for the complete eighteen-step sequence as a whole (only `TD-005`, the project-wide automated regression suite, remains open, unrelated specifically to this unit). `P2_03_FINAL_CERTIFICATION_V1_2026-07-11.md` (Sections 18-19) and `P2_04_FINAL_CERTIFICATION_V1_2026-07-13.md` (Section 18) each independently exercised a full-system replay (fifty-tick and comparable scripted sequences) and found functionally identical results across independent runs, but each did so as corroborating evidence for its own unit's narrower ownership scope (Financial Ownership, Risk Ownership respectively), not as a dedicated, individually-named certification of the complete twelve-stage ADR-010 sequence's own determinism as P3-01's own subject matter. This document therefore classifies full-sequence Tick-Sequence Determinism as **partially evidenced**: individually, every stage's own determinism is evidenced; the composed, full-sequence property has been incidentally exercised twice by adjacent units' own certifications, but has not yet been independently, separately certified as this unit's own finding.

## 11. Current Traceability State

Every one of the eighteen steps in Section 6.2 names, by file and line, the runtime object it consumes and the runtime object it produces or publishes. `CanonicalEnforcer`'s ten `apply_*` methods (Section 8.1) each name, in their own method body, the exact `CanonicalState` key they write (`canonical_enforcer.py:7-85`). No step was found whose consumed or produced object could not be traced to a specific prior step's output or to `CanonicalState`'s own schema. The two exceptions - Runtime Tick and Market Regime, written directly by `RunLoop` rather than through a named `CanonicalEnforcer.apply_*` method (Section 7.3 -> Section 12.1, Finding F-01) - remain fully traceable to their producing line (`loop.py:42,45`); traceability itself is not broken, only the Writer-on-Behalf-Of mechanism differs from the pattern used for every other object.

## 12. Functional Gaps

This section was revised following a targeted Scientific Consistency Review of the original Gap 2 and Gap 3 findings. That review found neither to be a currently unmet P3-01 requirement; both are reclassified below (Sections 12.2, 12.3) rather than carried as Functional Gaps. Four Functional Gaps remain within P3-01's own scope (Section 12.1).

### 12.1 P3-01-Owned Functional Gaps

**Gap 1 (Finding F-01) - Two canonical objects bypass `CanonicalEnforcer`.** `RunLoop` writes Runtime Tick and Market Regime directly via `self.cstate.update_tick(...)` and `self.cstate.update_regime(...)` (`loop.py:42,45`); `CanonicalEnforcer` exposes no `apply_tick()` or `apply_regime()` method (confirmed: `canonical_enforcer.py`'s ten methods do not include either). For Runtime Tick, this is Matrix-conformant: the Runtime Ownership Matrix's own "Runtime Tick" row names `RunLoop` as its own Writer-on-Behalf-Of. For Market Regime, this diverges from the Matrix, whose "Market Regime" row names `RegimeClassifier` as the Writer-on-Behalf-Of, not `RunLoop`. Neither case is a violation of Rule OM-001 (unique Authoritative Owner) or Rule OM-006 (`CanonicalState` exclusively owns active runtime state) - `CanonicalState` remains the sole Authoritative Owner in both cases - but the Market Regime case is a divergence between the Matrix's documented Writer-on-Behalf-Of assignment and the observed runtime mechanism.

**Gap 2 (Finding F-02, renumbered from Finding F-04) - No explicit runtime-failure (unhandled exception) semantics exist for partially-published ticks.** `main.py`'s broad `except Exception` (Section 9.3) provides no rollback, no reset, and no distinction between a tick that failed before any publication and one that failed after several. `run_engine/core/loop.py`'s own `__main__` block provides no exception handling whatsoever. ADR-011 defines non-mutation semantics for rejected lifecycle transitions (`RUNTIME_FAILURE_EVENT`, a `LifecycleEvent`) but does not address an unhandled Python exception propagating out of `RunLoop.step()` itself; this is a distinct condition (Section 5) with no corresponding architectural contract found anywhere in the Binding Baseline (Section 3).

**Gap 3 - Full-sequence Tick-Sequence Determinism has not been individually, separately certified as this unit's own finding.** Section 10's evidence is real but incidental to two adjacent units' own narrower certifications, not yet independently established as P3-01's own named deliverable, mirroring the same shape of gap the P2-04 FRA identified and closed for RiskEngine's own determinism (P2-04-FR-009/Gap 5).

**Gap 4 - `PerformanceEngine`'s internal accounting remains decision-oriented, not lifecycle-oriented.** `PerformanceEngine.update()` keys its statistics by `decision["action"]` (`performance.py:11`), incrementing `trades` on every non-`RUNTIME_FAILURE_EVENT` tick regardless of whether a lifecycle transition actually closed a trade, reproducing exactly the Architecture Baseline's own already-diagnosed "Decision-Oriented Performance Evaluation" defect (Architecture Defect AD-005) and matching TD-004's still-open description. This gap is confirmed still present by direct source read; it is a compatibility/scope-boundary finding for P3-01, since TD-004's Target Phase is P3, most plausibly P3-03 ("Verify PerformanceEngine inputs. Validate Performance Metrics generation"), not P3-01, whose own Baseline objective text concerns `PerformanceEngine`'s ordering position, not its internal computation.

None of these four gaps requires reopening P2-02A (Position Ownership, certified), P2-03 (Financial Ownership, certified), or P2-04 (Risk Ownership, certified) - each concerns ordering, publication mechanism, or failure semantics, not the ownership assignments those three units already closed.

### 12.2 Cross-Unit Observations (Not P3-01 Functional Gaps)

**CUO-01 - `CanonicalState.get()` returns a live-mutable reference.** Confirmed by Section 7.2: `CanonicalState.get()` returns its internal dictionary directly, not a copy. No ADR, Architecture Invariant, or Acceptance Criterion requires a defensive copy; Rule OM-004 governs consumer behaviour, not `CanonicalState`'s own return mechanism, and is currently evidenced as upheld by every consumer this analysis reached (Section 7.2). This is not a currently unmet P3-01 requirement. It is recorded here as a Cross-Unit Observation, directed to the P3-02 (Information Flow Validation) unit, whose own Baseline objective text ("Remove hidden coupling") is the more precise textual and architectural home for a shared-mutable-reference concern of this kind. A secondary, general Runtime Safety dimension (robustness against a hypothetical future non-compliant consumer) is noted but not evaluated further here. This document takes no position on whether reference or copy semantics should govern `CanonicalState.get()` in the future; the existing Architecture Baseline decides neither explicitly.

### 12.3 Verified Conformant Findings

**VC-01 - ADR-010 Stage 12 ("Tick-Complete CanonicalState Publication") is realized by the aggregate effect of the tick's incremental `CanonicalEnforcer.apply_*()` calls, consistent with the already-certified P2-03 Specification's own governing normativity principle (Section 8.1).** The externally observable guarantee AC-009 and the Tick Completion Contract require is currently evidenced as satisfied (Section 8.2). This is not a P3-01 functional gap. A residual, non-blocking documentation question - whether the guarantee's synchronous-execution precondition should be explicitly protected by a named Invariant or Constraint - remains open (OQ-003, revised, Section 22) but does not affect this finding's own current conformance.

## 13. Required Functional Capabilities

RC-1 - An explicit, ADR-traceable statement that exactly one normative tick execution sequence exists and is realized by the current runtime, closing the verification half of the Baseline objective ("Implement ADR-010 execution sequence").

RC-2 - An explicit, individually-named ordering conformance finding for each of ADR-010's twelve stages, distinguishing stage-position conformance (currently evidenced, Section 6.3) from Stage 12's own verified conformance (Section 8, VC-01).

RC-3 - An explicit disposition of the two `CanonicalEnforcer`-bypassing writes (Gap 1): whether Market Regime's Writer-on-Behalf-Of assignment should be corrected to match the Matrix, whether the Matrix should be amended to reflect `RunLoop`'s role for both objects, or whether the divergence is architecturally acceptable as-is.

RC-4 - Forwarding of Cross-Unit Observation CUO-01 (Section 12.2, `CanonicalState.get()`'s reference semantics) to the P3-02 Scientific Dependency Analysis or Capability Gap Analysis, without independent P3-01 resolution; no P3-01 capability requires closing CUO-01 itself.

RC-5 - An explicit disposition, at a future Architecture stage, of whether the synchronous-execution precondition underlying VC-01's already-verified conformance (Section 8.3) should be protected by a named Invariant or Constraint; no atomic publish/commit mechanism is required by this capability.

RC-6 - An explicit decision on runtime-failure (unhandled exception) semantics for partially-published ticks (Gap 2): whether a rollback, a partial-tick marker, a `CanonicalState` reset, or another mechanism is required, or whether the current behaviour is accepted with documented rationale.

RC-7 - An explicit, independently-recorded verification of full-sequence Tick-Sequence Determinism as this unit's own finding, closing Gap 3.

RC-8 - An explicit disposition (in scope for P3-01, or explicitly assigned to P3-03) of Gap 4, consistent with TD-004's own Target Phase and this document's own Baseline objective text, without resolving Gap 4's substance here.

RC-9 - Preservation of every already-certified P2-02A/P2-03/P2-04 ownership, formula, and non-mutation contract unless this unit's own governance chain explicitly re-certifies a change.

## 14. Functional Requirements

### 14.1 Normative Sequence Requirements

**P3-01-FR-001** - Exactly one normative, twelve-stage runtime tick execution sequence, matching ADR-010's own enumeration, SHALL govern every runtime tick; no competing or alternative ordering SHALL exist on the active execution path.

Scientific Rationale: AI-006 - "Runtime information SHALL propagate through one deterministic execution sequence." AC-001's Baseline objective text ("Implement ADR-010 execution sequence") requires the sequence's existence to be verified, not merely assumed.
Existing Evidence: Section 6.2 (eighteen-step trace), Section 6.3 (mapping table), Section 6.4 (absence of alternative active paths).
Current Conformance: currently evidenced.
Validation Condition: a fresh, line-by-line re-trace of `RunLoop.step()` at any future HEAD reproduces the same eleven ADR-010-mapped stage boundaries in the same relative order, with no alternative `RunLoop`-equivalent class found active.
Scope Boundary: does not itself certify Stage 12's publication mechanism (FR-013) or full-sequence determinism (FR-017), each separately stated.
Traceability: ADR-010, AI-006, AC-001, AC-012.

### 14.2 Stage-Position Requirements

**P3-01-FR-002** - Runtime Tick Acquisition SHALL occur first in every tick, producing the tick's own identity and price before any other stage executes.

Scientific Rationale: ADR-010 Stage 1; the Runtime Ownership Matrix names `RunLoop` as Runtime Tick's exclusive Computational Authority, Authoritative Owner, and Writer-on-Behalf-Of.
Existing Evidence: `loop.py:35` (Runtime Status set to `RUNNING`, the first statement in `step()`); Section 6.2 Step 1.
Current Conformance: currently evidenced.
Validation Condition: `RunLoop.step()`'s first executable statement remains Runtime Tick/Status acquisition, preceding every other stage in source order.
Scope Boundary: does not address the direct-write-versus-`CanonicalEnforcer` question for Runtime Tick specifically (FR-011).
Traceability: ADR-010 Stage 1, Runtime Ownership Matrix ("Runtime Tick" row).

**P3-01-FR-003** - State Acquisition and Normalization SHALL occur after Runtime Tick Acquisition and before Regime Classification.

Scientific Rationale: ADR-010 Stage 2; Regime Classification's own input (`state`) is State Acquisition's output.
Existing Evidence: `loop.py:37` (State Acquisition) precedes `loop.py:44` (Regime Classification); Section 6.2 Steps 2, 4.
Current Conformance: currently evidenced.
Validation Condition: `StateEngine.update()`'s return value remains the sole input `RegimeClassifier.classify()` consumes for its own state-derived features.
Scope Boundary: does not evaluate `StateEngine`'s own normalization correctness, only its ordering position.
Traceability: ADR-010 Stage 2, Runtime Ownership Matrix ("Normalized Runtime State" row).

**P3-01-FR-004** - Regime Classification SHALL occur after State Acquisition and before Strategy Selection.

Scientific Rationale: ADR-010 Stage 3; Strategy Selection's own input includes the current regime.
Existing Evidence: `loop.py:44` precedes `loop.py:49`; Section 6.2 Steps 4, 7.
Current Conformance: currently evidenced for ordering position; the Writer-on-Behalf-Of mechanism for the resulting Market Regime value diverges from the Runtime Ownership Matrix's own "Market Regime" row (Gap 1, Finding F-01) - not yet independently evidenced as conformant at the writer-mechanism level.
Validation Condition: `RegimeClassifier.classify()`'s return value remains available to `StrategySelector.select()` and `StrategySelector.decide()` before either executes.
Scope Boundary: does not evaluate `RegimeClassifier`'s own classification algorithm; addresses ordering position and Writer-on-Behalf-Of conformance only.
Traceability: ADR-010 Stage 3, Runtime Ownership Matrix ("Market Regime" row), Rule OM-003.

**P3-01-FR-005** - Strategy Selection SHALL occur after Regime Classification and before Execution Decision Generation, and SHALL itself precede Executor Event Generation.

Scientific Rationale: ADR-010 Stages 4 and 5; the Runtime Ownership Matrix names `StrategySelector` as Computational Authority for both Strategy Selection and Execution Decision.
Existing Evidence: `loop.py:49-53` (`select()` then `decide()`, both via `StrategySelector`) precede `loop.py:55` (`Executor.execute()`); Section 6.2 Steps 7-8-9.
Current Conformance: currently evidenced.
Validation Condition: `StrategySelector.select()`'s output remains the explicit input to `StrategySelector.decide()`, and `decide()`'s output remains the explicit input to `Executor.execute()`, in strictly increasing source order.
Scope Boundary: does not evaluate `StrategySelector`'s own weighting or decision algorithm; `StrategySelector.update()` (an adaptive-weight method never invoked anywhere in `loop.py`) is noted as present but inactive, not itself a P3-01 finding requiring resolution.
Traceability: ADR-010 Stages 4-5, Runtime Ownership Matrix ("Strategy Selection," "Execution Decision" rows).

**P3-01-FR-006** - Executor Event Generation SHALL occur after Execution Decision Generation and before TradeLifecycle Update.

Scientific Rationale: ADR-010 Stage 6; ADR-002 names Execution Events as the input `TradeLifecycleEngine` consumes to produce Trade Lifecycle Events.
Existing Evidence: `loop.py:55` precedes `loop.py:57`; Section 6.2 Steps 9-10; `Executor.execute()` (`executor.py:5-32`) confirmed a pure function of its two parameters, holding no instance state.
Current Conformance: currently evidenced.
Validation Condition: `Executor.execute()`'s return value remains the explicit input to `TradeLifecycleEngine.on_execution()`.
Scope Boundary: does not evaluate `Executor`'s own execution-quantity or status logic.
Traceability: ADR-010 Stage 6, ADR-002 (Execution Events), Runtime Ownership Matrix ("Execution Event" row).

**P3-01-FR-007** - TradeLifecycle Update SHALL occur after Executor Event Generation and before Position Update.

Scientific Rationale: ADR-010 Stage 7; ADR-003 names `TradeLifecycleEngine` as the Authoritative Owner of lifecycle information that `PositionEngine` consumes (via `current_position()`) to compute the post-trade Position.
Existing Evidence: `loop.py:57,59` precede `loop.py:61`; Section 6.2 Steps 10-11-12.
Current Conformance: currently evidenced.
Validation Condition: `TradeLifecycleEngine.on_execution()`'s and `current_position()`'s outputs remain available to `PositionEngine.update_post_trade()` before it executes.
Scope Boundary: does not evaluate lifecycle transition semantics themselves (Scale-In/Partial-Close/Full-Close correctness), already certified.
Traceability: ADR-010 Stage 7, ADR-003, ADR-009 (Lifecycle Transition Table).

**P3-01-FR-008** - Position Update SHALL occur after TradeLifecycle Update and before Financial Accounting.

Scientific Rationale: ADR-010 Stage 8; ADR-004 requires Position to reflect the current tick's lifecycle outcome before `RiskEngine` (a later stage) consumes Position-derived Exposure, and before `PnLEngine`'s own event-PnL computation, which reads the pre-trade Position view captured earlier in the same tick (P2-02A-AD-005), not the post-trade value.
Existing Evidence: `loop.py:61-66` precedes `loop.py:72`; Section 6.2 Steps 12-13.
Current Conformance: currently evidenced.
Validation Condition: `PositionEngine.update_post_trade()`'s published result remains available, via `CanonicalEnforcer.apply_position()`, before Financial Accounting's own computation begins.
Scope Boundary: does not evaluate Position's own weighted-average or Exposure formulas, already certified (P2-02A).
Traceability: ADR-010 Stage 8, ADR-004, P2-02A-AD-005.

**P3-01-FR-009** - Financial Accounting SHALL occur after Position Update and before Risk Evaluation.

Scientific Rationale: ADR-010 Stage 9; ADR-006 requires `RiskEngine` to compute Drawdown exclusively from canonical financial state, which therefore must already be current when Risk Evaluation executes.
Existing Evidence: `loop.py:68-88` precedes `loop.py:90-92`; Section 6.2 Steps 13-14-15-16; independently re-confirmed present and unchanged from the P2-03-certified ordering (`P2_03_FINAL_CERTIFICATION_V1_2026-07-11.md`).
Current Conformance: currently evidenced.
Validation Condition: `PnLEngine.compute_equity()`'s published Equity and Peak Equity values remain available, via `CanonicalState.get()`, before `RiskEngine.check()` executes.
Scope Boundary: does not evaluate the Equity/Peak-Equity/Realized-PnL formulas themselves, already certified (P2-03).
Traceability: ADR-010 Stage 9, ADR-005, ADR-006.

**P3-01-FR-010** - Risk Evaluation SHALL occur after Financial Accounting and before Performance Evaluation.

Scientific Rationale: ADR-010 Stage 10; the Runtime Ownership Matrix names `PerformanceEngine` as a potential consumer of Risk Metrics, requiring Risk Evaluation to have already run if that consumption were ever activated (currently not activated, P2-04-AD-017).
Existing Evidence: `loop.py:92-93` precedes `loop.py:95-96`; Section 6.2 Steps 16-17; independently re-confirmed present and unchanged from the P2-04-certified ordering (`P2_04_FINAL_CERTIFICATION_V1_2026-07-13.md`).
Current Conformance: currently evidenced.
Validation Condition: `RiskEngine.check()`'s published Drawdown, Drawdown Ratio, and `risk_allocation_factor` values remain available, via `CanonicalEnforcer.apply_risk()`, before `PerformanceEngine.update()` executes, regardless of whether `PerformanceEngine` currently reads any of them.
Scope Boundary: does not evaluate the risk-limiting formula itself, already certified (P2-04); does not resolve whether `PerformanceEngine` should consume Risk Metrics (P2-04-AD-017's own scope boundary, preserved unchanged).
Traceability: ADR-010 Stage 10, ADR-007, P2-04-AD-017.

**P3-01-FR-011** - Performance Evaluation SHALL occur after Risk Evaluation and before Tick-Complete CanonicalState Publication.

Scientific Rationale: ADR-010 Stage 11; ADR-008 requires Performance to reflect completed lifecycle outcomes, which are already final for the current tick only once every upstream stage, including Risk Evaluation, has executed.
Existing Evidence: `loop.py:95-96` precedes `loop.py:98-113`; Section 6.2 Steps 17-18.
Current Conformance: currently evidenced for ordering position; `PerformanceEngine`'s own internal accounting remains decision-oriented, not lifecycle-oriented (Gap 4), a distinct, explicitly out-of-scope finding (Section 15) that does not affect this requirement's own ordering-position conformance.
Validation Condition: `PerformanceEngine.update()`'s call remains the last stage-producing call in `RunLoop.step()` before the tick-result dictionary is assembled and returned.
Scope Boundary: explicitly excludes `PerformanceEngine`'s internal computation correctness (Gap 4, TD-004, most plausibly P3-03's territory).
Traceability: ADR-010 Stage 11, ADR-008, TD-004.

### 14.3 Canonical Working State and Publication Requirements

**P3-01-FR-012** - No runtime component SHALL consume a Canonical Working State value corresponding to a stage whose own ADR-010 execution position has not yet been reached in the current tick.

Scientific Rationale: the Architecture Baseline's Canonical Working State definition - "It may be consumed only by components whose execution order has already been reached."
Existing Evidence: Section 7.1; every one of the eighteen steps in Section 6.2 consumes only values already produced by an earlier step or by `CanonicalState`'s own already-current schema.
Current Conformance: currently evidenced.
Validation Condition: for every consumer identified in Section 6.2, the value it reads was itself published, directly or via `CanonicalEnforcer`, at an earlier step than the consumer's own step number.
Scope Boundary: does not require a structural (construction-level) enforcement mechanism; the underlying reference-semantics observation is recorded separately as Cross-Unit Observation CUO-01 (Section 12.2), directed to P3-02, not as a P3-01 requirement gap.
Traceability: Canonical Working State definition (Architecture Baseline), AI-007.

**P3-01-FR-013** - Every runtime tick SHALL culminate in exactly one Tick-Complete CanonicalState Publication, after which the resulting Tick-Complete Snapshot alone becomes externally observable.

Scientific Rationale: ADR-010 Stage 12, verbatim; the Tick Completion Contract's "Only after successful completion shall the Tick-Complete Snapshot become externally observable."
Existing Evidence: Section 8.1 (incremental publication, ten separate `apply_*` calls, verified conformant with `P2_03_FINANCIAL_OWNERSHIP_SPECIFICATION_V1_2026-07-11.md` Section 16's own governing normativity principle - observable dependencies and results govern conformance, not internal code structure); Section 8.2 (external observability currently verified, under the runtime's synchronous, single-threaded execution model).
Current Conformance: currently evidenced (Section 8, Verified Conformant Finding VC-01).
Validation Condition: a fresh trace confirms that after the last of the tick's ten `apply_*` calls (Section 8.1) executes, `CanonicalState` reflects every value produced during the tick, and no external caller observes `CanonicalState` before that point.
Scope Boundary: does not require or propose an atomic publish/commit mechanism; does not decide whether the synchronous-execution precondition underlying this conformance (Section 8.3) should be protected by a new Invariant or Constraint - recorded as a residual, non-blocking Open Question (OQ-003, revised).
Traceability: ADR-010 Stage 12, AI-009, AC-009, Tick Completion Contract, `P2_03_FINANCIAL_OWNERSHIP_SPECIFICATION_V1_2026-07-11.md` Section 16.

**P3-01-FR-014** - External downstream consumers SHALL observe only Tick-Complete Snapshots, never intermediate, per-stage runtime state.

Scientific Rationale: the Tick-Complete Snapshot definition - "External downstream consumers consume only Tick-Complete Snapshots. No component may consume state from a future or incomplete execution stage."
Existing Evidence: Section 8.2; `main.py`'s own driving loop only ever inspects `result` (`main.py:23-24`) after `engine.step()` has fully returned; no other external caller of `CanonicalState.get()` or `RunLoop.step()` exists anywhere in the active-path repository (confirmed by Section 4's import search).
Current Conformance: currently evidenced (Section 8, VC-01), under the same synchronous-execution precondition noted for FR-013.
Validation Condition: no code path outside `RunLoop.step()`'s own body reads `CanonicalState.get()` or any of its sub-keys while `step()` is executing.
Scope Boundary: assumes continuation of the current synchronous, single-threaded execution model; does not address any future concurrent or asynchronous execution mode (explicitly out of scope, Section 15).
Traceability: Tick-Complete Snapshot definition, AI-009, AC-009.

### 14.4 Failure, Rejection, and No-Execution Requirements

**P3-01-FR-015** - A `HOLD` or no-execution tick SHALL execute every one of the twelve ADR-010 stages, in the same order as any other tick, producing well-defined, non-error results at every stage.

Scientific Rationale: ADR-010 does not name any conditional or skippable stage; a `HOLD` decision is itself a valid Execution Decision (ADR-002), not the absence of one.
Existing Evidence: Section 9.1, full six-file trace confirming no stage is skipped for `HOLD`.
Current Conformance: currently evidenced.
Validation Condition: a scripted `HOLD`-only tick sequence produces a complete, well-formed tick-result dictionary (Section 6.2 Step 18's shape) at every tick, with `CanonicalState`'s financial and risk keys numerically unchanged from the prior tick.
Scope Boundary: does not evaluate `StrategySelector`'s own cooldown/weighting logic that produces a `HOLD` decision.
Traceability: ADR-010, ADR-002 (Decision Events), Tick Completion Contract.

**P3-01-FR-016** - A tick containing a rejected lifecycle transition (`RUNTIME_FAILURE_EVENT`) SHALL execute every one of the twelve ADR-010 stages, in the same order as any other tick, while leaving Position identity fields, Realized PnL, Equity, Peak Equity, cumulative Realized PnL, Drawdown, Drawdown Ratio, `risk_allocation_factor`, and Performance statistics unmodified.

Scientific Rationale: ADR-011, verbatim - "Rejected transitions SHALL never: modify Position, modify Equity, modify Realized PnL, modify Unrealized PnL, modify Performance, terminate a lifecycle... Instead, every rejected transition SHALL generate exactly one immutable Runtime Failure Event."
Existing Evidence: Section 9.2, full trace across `pnl.py`, `performance.py`, and (by independent citation) the already-certified `RiskEngine`/`Position` non-mutation contracts (`P2_03_FINAL_CERTIFICATION_V1_2026-07-11.md` Section 20, `P2_04_FINAL_CERTIFICATION_V1_2026-07-13.md` Section 17).
Current Conformance: currently evidenced.
Validation Condition: a scripted tick sequence including at least one occurrence of each of the four named rejection reasons produces functionally identical financial, risk, and performance values immediately before and immediately after the failure tick, with every stage still executing.
Scope Boundary: does not re-evaluate the four rejection reasons' own trigger conditions, already certified (P1-04, P2-02A, P2-03).
Traceability: ADR-011, AI-011 (Lifecycle Consistency), AC-015 (Runtime Failure Handling).

### 14.5 Determinism and Replay Requirements

**P3-01-FR-017** - The complete twelve-stage tick sequence SHALL be Tick-Sequence Deterministic: an identical ordered sequence of tick inputs, from an identical initial state, SHALL produce an identical ordered sequence of runtime outputs and Tick-Complete Snapshots.

Scientific Rationale: AI-005 - "Identical runtime inputs SHALL produce identical runtime outputs. Deterministic behaviour shall not depend upon hidden mutable state." AI-006 - "Runtime information SHALL propagate through one deterministic execution sequence."
Existing Evidence: Section 10 - individually, every stage's own determinism is evidenced (directly, for `Executor` and `PnLEngine`; by independent certification, for `RiskEngine`); the composed, full-sequence property has been incidentally exercised by two adjacent units' own certifications (P2-03 Sections 18-19, P2-04 Section 18) but not yet separately certified as this unit's own named finding.
Current Conformance: partially evidenced.
Validation Condition: two independent `RunLoop` instances, each driven through an identical scripted tick sequence from a fresh `CanonicalState`, produce functionally identical tick-result dictionaries and functionally identical final `CanonicalState` snapshots at every tick, verified once independently by this unit's own future certification rather than solely inherited from P2-03's or P2-04's.
Scope Boundary: does not require or introduce any new replay tooling; documents the currently available evidence and its gap only.
Traceability: AI-005, AI-006, ADR-010, AC-012.

### 14.6 Execution Path Integrity Requirements

**P3-01-FR-018** - No alternative or competing active execution path SHALL exist; `run_engine/core/loop.py`'s `RunLoop.step()` SHALL remain the sole runtime orchestration entry point.

Scientific Rationale: AI-013 (Architectural Minimality) - "Architectural redundancy is prohibited unless scientifically justified"; Architecture Defect AD-007 (Parallel Runtime Architectures) requires every competing implementation to eventually receive an explicit classification.
Existing Evidence: Section 4 (confirmed-inactive inventory), Section 6.4.
Current Conformance: currently evidenced for the active path's exclusivity; the inactive components' own final classification (retain/integrate/archive/remove) remains explicitly unresolved, correctly deferred to Phase 6 (Section 15).
Validation Condition: a repository-wide import search from `run_engine/main.py` and `run_engine/core/loop.py` continues to reach exactly the eleven active collaborators named in Section 6.1, with no import edge into `run_engine/core/decision.py`, `run_engine/runtime/`, `run_engine/execution/` (top-level), `run_engine/feedback/`, or `run_engine/logging/`.
Scope Boundary: does not classify or remove any inactive component; classification is Phase 6 Repository Consolidation's own scope.
Traceability: AI-013, Architecture Defect AD-007, Phase 6 (Repository Consolidation).

**P3-01-FR-019** - No runtime component other than `CanonicalEnforcer`'s named `apply_*` methods SHALL write to `CanonicalState`, except where the Runtime Ownership Matrix explicitly names a different Writer-on-Behalf-Of.

Scientific Rationale: Rule OM-003 - "Writer-on-Behalf-Of never establishes ownership," implying a Writer-on-Behalf-Of role must be assignable and traceable, not incidental; Rule OM-006 - "CanonicalState exclusively owns active runtime state" (an ownership, not a write-mechanism, guarantee, distinct from this requirement).
Existing Evidence: Section 7.3, Gap 1 (Finding F-01) - Runtime Tick and Market Regime are written directly by `RunLoop`, bypassing `CanonicalEnforcer`; Runtime Tick's case matches the Matrix's own "RunLoop" Writer-on-Behalf-Of assignment, Market Regime's does not (the Matrix names `RegimeClassifier`).
Current Conformance: currently evidenced for every financial, risk, position, strategy, execution, and performance object (all ten `CanonicalEnforcer.apply_*` methods, Section 8.1); not yet independently evidenced as conformant for Market Regime specifically.
Validation Condition: a governing Architecture document for this unit explicitly states whether Market Regime's Writer-on-Behalf-Of mechanism should change to match the Matrix, or whether the Matrix's own row should be amended to reflect the observed, `RunLoop`-mediated mechanism.
Scope Boundary: does not itself decide the resolution; Runtime Tick's already-Matrix-conformant case is not reopened.
Traceability: Rule OM-003, Rule OM-006, Runtime Ownership Matrix ("Runtime Tick," "Market Regime" rows).

### 14.7 Runtime Failure (Exception) Semantics Requirements

**P3-01-FR-020** - The runtime's behaviour when an unhandled exception propagates out of `RunLoop.step()` mid-tick, after some but not all of that tick's `CanonicalEnforcer.apply_*` calls have already executed, SHALL be explicitly and architecturally defined.

Scientific Rationale: the Tick Completion Contract - "A runtime tick is complete only when all mandatory runtime stages have executed successfully... Only after successful completion shall the Tick-Complete Snapshot become externally observable"; no governing document currently defines what "successful" excludes with respect to an unhandled exception, as distinct from a `RUNTIME_FAILURE_EVENT` (ADR-011's own, narrower, already-defined concern).
Existing Evidence: Section 9.3, Gap 2 (Finding F-02) - `main.py`'s broad `except Exception` and `loop.py`'s own unguarded `__main__` block, neither providing rollback, reset, or partial-tick marking.
Current Conformance: unresolved.
Validation Condition: a governing Architecture document for this unit explicitly states the required behaviour (for example: an explicit partial-tick marker, a `CanonicalState.reset()` invocation, an explicit rollback mechanism, or an explicit, justified decision that the current behaviour is architecturally accepted).
Scope Boundary: does not extend to `main.py`'s own broader process-level error-reporting or logging strategy, only to `CanonicalState`'s consistency guarantee under this specific condition.
Traceability: Tick Completion Contract, AI-009, ADR-011 (by contrast - a related but distinct concern).

### 14.8 Traceability Requirements

**P3-01-FR-021** - Every one of the twelve ADR-010 stages SHALL remain traceable, by file and line, to the specific runtime object it consumes and the specific runtime object it produces or publishes.

Scientific Rationale: AI-014 (Architectural Traceability) - "Every runtime output SHALL be traceable through: originating observation, runtime state, execution decision, lifecycle event, financial accounting, risk evaluation, resulting runtime state."
Existing Evidence: Section 11; Section 6.2's own eighteen-step citation format.
Current Conformance: currently evidenced.
Validation Condition: a fresh trace of `RunLoop.step()` at any future HEAD continues to name, for each stage, the exact line(s) producing and the exact line(s) consuming its associated runtime object.
Scope Boundary: does not extend to `TradeLifecycleEngine`'s own internal historical record structure, already certified.
Traceability: AI-014, AC-011 (Scientific Traceability).

### 14.9 Compatibility and Scope Boundary Requirements

**P3-01-FR-022** - Every already-certified P2-02A, P2-03, and P2-04 ownership, formula, and non-mutation contract SHALL continue to function exactly as certified, unless this unit's own governance chain explicitly re-certifies a change.

Scientific Rationale: Cluster-I-style compatibility constraint, established precedent from every prior P2-0x Functional Requirement Analysis in this governance chain.
Existing Evidence: `docs/architecture/certification/P2_03_FINAL_CERTIFICATION_V1_2026-07-11.md`; `docs/architecture/certification/P2_04_FINAL_CERTIFICATION_V1_2026-07-13.md`; Section 6.2's independent re-trace, confirming the eighteen-step ordering these two certifications rely upon remains unchanged.
Current Conformance: currently evidenced.
Validation Condition: full regression re-run of the P2-02A/P2-03/P2-04 certified scenarios after any P3-01 implementation produces functionally identical results for every already-certified field.
Scope Boundary: this unit's own findings (Gaps 1 through 6) concern ordering, publication mechanism, and failure semantics only; none requires reopening any already-certified ownership assignment.
Traceability: ADR-001 through ADR-009, ADR-011, P2-02A/P2-03/P2-04 certifications.

**P3-01-FR-023** - `PerformanceEngine`'s internal accounting semantics (decision-oriented versus lifecycle-oriented, Gap 4) and any hidden coupling beyond stage ordering - including Cross-Unit Observation CUO-01 (Section 12.2) - are explicitly scope-protected pending disposition by P3-02 (Information Flow Validation) or P3-03 (Performance Validation); this document does not mandate any change to `performance.py`, `canonical_state.py`, or any other file's internal computation.

Scientific Rationale: the Implementation Baseline names P3-02's objectives as "Remove hidden coupling. Validate Runtime Tick processing. Validate Market Observation processing," and P3-03's as "Verify PerformanceEngine inputs. Validate Performance Metrics generation," each textually closer to Gap 4's and CUO-01's substance than P3-01's own "Implement ADR-010 execution sequence. Verify Executor integration. Verify Tick-Complete Snapshot publication."
Existing Evidence: Section 12.1 Gap 4; Section 12.2 CUO-01; `RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md`'s own P3-01/P3-02/P3-03 objective text.
Current Conformance: not applicable (a scope-protection requirement, not a conformance-evaluable one).
Validation Condition: any future document that brings `PerformanceEngine`'s internal accounting semantics, or any hidden-coupling finding beyond stage ordering (including CUO-01), into P3-01's scope does so explicitly, not as an incidental side effect of FR-002 through FR-021.
Scope Boundary: this document takes no final position on whether Gap 4 or CUO-01 belongs to P3-02 or P3-03; only that neither belongs to P3-01, consistent with the governing task's own explicit instruction to establish this boundary.
Traceability: Implementation Baseline (P3-01, P3-02, P3-03 unit definitions), TD-004.

## 15. Non-Goals

Explicitly excluded from this document and from P3-01's own scope, consistent with the governing task's instruction:

- Strategy logic changes - `StrategySelector`'s own weighting, cooldown, or regime-bias algorithm is not evaluated for correctness, only for its ordering position (FR-005).
- Regime model changes - `RegimeClassifier`'s own classification, smoothing, or hysteresis algorithm is not evaluated for correctness, only for its ordering position (FR-004).
- Executor redesign - `Executor`'s own execution-quantity or status logic is not evaluated for correctness, only for its ordering position (FR-006).
- Lifecycle semantics changes - the Lifecycle Transition Table (ADR-009), Scale-In/Partial-Close/Full-Close formulas, already certified, are not reopened.
- Position formula changes - Exposure, weighted-average entry price, already certified (P2-02A), not reopened.
- PnL formula changes - Realized PnL, Equity, Peak Equity reconstruction rules, already certified (P2-03), not reopened.
- Risk formula changes - the risk-limiting formula, Risk Policy Configuration, already certified (P2-04), not reopened.
- Performance metric redesign - Gap 4's substance is explicitly scope-protected to P3-02/P3-03 (FR-023), not resolved here.
- Persistence, Recovery, Schema Evolution - ADR-012, Deferred Scope, unaffected by any finding in this document.
- Parallel or asynchronous execution - Section 8.2's finding assumes, and does not propose changing, the current synchronous, single-threaded execution model; any future concurrent execution mode is explicitly out of scope.
- Concrete implementation - no Python signature, method body, or file diff is proposed anywhere in this document.
- Test specification - no test suite, test framework, or specific test case is designed here; TD-005 (automated regression suite) remains project-wide and out of scope.
- Long-duration run execution - the Implementation Baseline's own 1-hour through 30-day validation sequence is a Final Scientific Certification concern, not this Functional Requirement Analysis's.
- Repository cleanup / Phase 6 classification of confirmed-inactive components (Section 4) - recorded as findings only; retain/integrate/archive/remove disposition belongs to Phase 6.
- `PositionSizingEngine` activation, `EquityStabilizer`, `run_engine/runtime/` directory disposition - unchanged inactive classification, inherited from prior units' own findings, not reopened.

## 16. Functional Requirement Catalogue

P3-01-FR-001 - Exactly one normative twelve-stage sequence governs every tick; no competing ordering exists. Source: ADR-010, AI-006.
P3-01-FR-002 - Runtime Tick Acquisition occurs first. Source: ADR-010 Stage 1.
P3-01-FR-003 - State Acquisition and Normalization precedes Regime Classification. Source: ADR-010 Stage 2.
P3-01-FR-004 - Regime Classification precedes Strategy Selection. Source: ADR-010 Stage 3.
P3-01-FR-005 - Strategy Selection precedes Execution Decision Generation and Executor Event Generation. Source: ADR-010 Stages 4-5.
P3-01-FR-006 - Executor Event Generation precedes TradeLifecycle Update. Source: ADR-010 Stage 6.
P3-01-FR-007 - TradeLifecycle Update precedes Position Update. Source: ADR-010 Stage 7.
P3-01-FR-008 - Position Update precedes Financial Accounting. Source: ADR-010 Stage 8.
P3-01-FR-009 - Financial Accounting precedes Risk Evaluation. Source: ADR-010 Stage 9.
P3-01-FR-010 - Risk Evaluation precedes Performance Evaluation. Source: ADR-010 Stage 10.
P3-01-FR-011 - Performance Evaluation precedes Tick-Complete Publication. Source: ADR-010 Stage 11.
P3-01-FR-012 - No component consumes a not-yet-reached stage's Canonical Working State. Source: Canonical Working State definition.
P3-01-FR-013 - Exactly one Tick-Complete Publication event per tick, verified conformant (VC-01). Source: ADR-010 Stage 12.
P3-01-FR-014 - External consumers observe only Tick-Complete Snapshots. Source: Tick-Complete Snapshot definition.
P3-01-FR-015 - HOLD/no-execution ticks execute every stage, in order. Source: ADR-010, ADR-002.
P3-01-FR-016 - Rejected-transition ticks execute every stage, in order, with named values unmutated. Source: ADR-011.
P3-01-FR-017 - The complete sequence is Tick-Sequence Deterministic. Source: AI-005, AI-006.
P3-01-FR-018 - No alternative active execution path exists. Source: AI-013, Architecture Defect AD-007.
P3-01-FR-019 - Only CanonicalEnforcer (or the Matrix-named exception) writes CanonicalState. Source: Rule OM-003, Rule OM-006.
P3-01-FR-020 - Unhandled-exception, partial-publication semantics SHALL be explicitly defined. Source: Tick Completion Contract.
P3-01-FR-021 - Every stage remains traceable to its consumed/produced object. Source: AI-014.
P3-01-FR-022 - All prior-certified P2-02A/P2-03/P2-04 contracts preserved unless explicitly re-certified. Source: Cluster-I-style compatibility constraint.
P3-01-FR-023 - PerformanceEngine's internal semantics and further hidden-coupling findings scope-protected to P3-02/P3-03. Source: Implementation Baseline unit definitions, TD-004.

## 17. ADR Traceability

| ADR | Related Requirements |
|---|---|
| ADR-001 (CanonicalState as SSOT) | FR-012, FR-019 |
| ADR-002 (Event-Driven Runtime Evolution) | FR-006, FR-015 |
| ADR-003 (TradeLifecycle as Authoritative Trade Model) | FR-007 |
| ADR-004 (Position Represents Current Market Exposure) | FR-008 |
| ADR-005 (Profit and Loss Accounting) | FR-009 |
| ADR-006 (Canonical Financial State Ownership) | FR-009, FR-010 |
| ADR-007 (Risk Evaluation as a Pure Computational Layer) | FR-010 |
| ADR-008 (Performance Ownership) | FR-011, FR-023 |
| ADR-009 (Partial Trade Closure and Position Netting) | FR-007, FR-016 |
| ADR-010 (Deterministic Runtime Execution Ordering) | FR-001 through FR-014, FR-021 |
| ADR-011 (Runtime Failure Handling) | FR-016, FR-020 (by contrast) |
| ADR-012 (Persistence, Recovery, Schema Evolution) | Section 15 (Non-Goal only) |

All twelve ADRs named in Section 3 are referenced by at least one requirement or an explicit Non-Goal note.

## 18. Architecture-Invariant Traceability

| Invariant | Related Requirements |
|---|---|
| AI-001 (Single Source of Truth) | FR-012, FR-019 |
| AI-002 (Unique Ownership) | FR-019 |
| AI-003 (Separation of Ownership and Computation) | FR-010 (by proximity) |
| AI-005 (Deterministic Execution) | FR-017 |
| AI-006 (Deterministic Information Flow) | FR-001, FR-017 |
| AI-007 (Semantic Continuity) | FR-012 |
| AI-008 (Explicit Runtime Events) | FR-006, FR-015 |
| AI-009 (Tick Completeness) | FR-013, FR-014 |
| AI-011 (Lifecycle Consistency) | FR-016 |
| AI-013 (Architectural Minimality) | FR-018 |
| AI-014 (Architectural Traceability) | FR-021 |

AI-004, AI-010, AI-012, AI-015 govern object-specific properties (Lifecycle History immutability, Financial Consistency, Operational/Historical Separation, Scientific Evolution) already certified by P2-02A/P2-03/P2-04 and preserved unchanged by FR-022; not independently re-derived here.

## 19. Acceptance-Criteria Traceability

| Acceptance Criterion | Related Requirements |
|---|---|
| AC-001 (Canonical Runtime Ownership) | FR-012, FR-019 |
| AC-007 (Risk Evaluation) | FR-010 |
| AC-008 (Performance Evaluation) | FR-011, FR-023 |
| AC-009 (Tick Completion) | FR-013, FR-014 |
| AC-010 (Information Flow) | FR-012, FR-021 |
| AC-011 (Scientific Traceability) | FR-021 |
| AC-012 (Deterministic Behaviour) | FR-001, FR-017 |
| AC-015 (Runtime Failure Handling) | FR-016 |

AC-002 through AC-006, AC-013, AC-014 govern ownership, lifecycle, and financial-integrity properties already certified by prior units and preserved unchanged by FR-022; not independently re-derived here.

## 20. Prior-Certification Compatibility

`P2_03_FINAL_CERTIFICATION_V1_2026-07-11.md` and `P2_04_FINAL_CERTIFICATION_V1_2026-07-13.md` each independently confirmed the complete `run_engine/` tree, apart from their own unit's single documentation-only commit, git-blob-identical to their respective certified baselines. This document's own Section 6.2 re-trace, performed fresh against the current HEAD rather than inherited from either certification, independently reproduces the identical eighteen-step ordering both certifications already relied upon. No finding in this document (Section 12) requires any change to `run_engine/core/pnl.py`, `run_engine/core/position.py`, `run_engine/core/risk.py`'s formula body, `run_engine/core/trade_lifecycle.py`, or any `CanonicalState` schema key already certified complete. FR-022 states this compatibility requirement explicitly as a binding constraint on any future P3-01 Architecture or Specification.

## 21. Technical-Debt Traceability

| Technical Debt Item | Status Before This Document | Relation to P3-01-FRA |
|---|---|---|
| TD-001 (Canonical Position Source for PnLEngine) | Functionally resolved per P2-02A Final Certification | Not reopened; unrelated to execution ordering. |
| TD-002 (Unify `_safe_float` implementations) | Open, Target Phase 2 | Not reopened; outside this document's scope. |
| TD-003 (Document Pre-Trade Snapshot Dependency) | Partially Resolved | Not reopened; unrelated to execution ordering. |
| TD-004 (Lifecycle-based Performance Evaluation) | Already Planned, Target P3 | Directly relevant to Gap 4; this document confirms the defect remains present and explicitly scope-protects its resolution to P3-02/P3-03 (FR-023), consistent with TD-004's own Target Phase. Not resolved here. |
| TD-005 (Automated Regression Test Suite) | Open, Target Project-wide | Confirmed still outside this document's scope (Section 15); any future P3-01 validation remains manual, consistent with every prior unit's precedent. |
| TD-006 (RiskEngine Peak Equity and Drawdown Ownership Duplication) | Certified fully closed (P2-04 Final Certification, Section 21) | Not reopened; the risk-limiting formula and Risk Policy Configuration ownership are compatibility-preserved (FR-022), not re-evaluated. |
| TD-007 (RunLoop Lifecycle Control Surface) | Deferred, Target future Runtime Control Unit | Not reopened; PAUSED/STOPPING/STOPPED/ERROR remain unreachable Runtime Status vocabulary, unaffected by any finding in this document. Gap 2's unhandled-exception finding (Section 12.1) is a distinct concern from TD-007's own pause/stop/shutdown control-surface scope and does not extend or substitute for it. |

No Technical Debt Register file edit is made by this document, consistent with every prior unit's own practice.

## 22. Open Questions

OQ-001 - Should Market Regime's Writer-on-Behalf-Of mechanism be changed to route through a new `CanonicalEnforcer.apply_regime()` method, matching the Matrix's own "RegimeClassifier" assignment, or should the Runtime Ownership Matrix instead be amended to name `RunLoop` (mirroring Runtime Tick's already-conformant row)? Not resolved here (Gap 1, FR-004, FR-019, RC-3).

Blocking Effect: blocks FR-019's exact resolution shape; does not block the underlying finding.

OQ-002 - [RESOLVED BY TARGETED SCIENTIFIC CONSISTENCY REVIEW, this revision] Originally framed as: does the Canonical Working State / Tick-Complete Snapshot distinction require a construction-level enforcement mechanism (a defensive copy, an immutable view, a distinct staging object), or does per-consumer discipline remain the accepted architectural approach? Disposition: this is not a P3-01 Open Question. Rule OM-004 is currently evidenced as upheld by every consumer this analysis reached (Section 7.2); no P3-01 requirement is currently unmet. The underlying observation is retained as Cross-Unit Observation CUO-01 (Section 12.2), directed to the P3-02 (Information Flow Validation) unit. Not further tracked as a P3-01 Open Question; no P3-01 decision is required or was made here.

Blocking Effect: none, for P3-01. Any resolution mechanism, if one is ever adopted, is a P3-02-stage decision.

OQ-003 - [REVISED BY TARGETED SCIENTIFIC CONSISTENCY REVIEW, this revision] Originally framed as: does ADR-010's Stage 12 require its own distinct, explicit realization? Disposition: resolved in the affirmative for observable conformance - Stage 12 is verified conformant (VC-01, Section 12.3), realized by the aggregate effect of the tick's ten incremental publications (Section 8.1), consistent with the already-certified `P2_03_FINANCIAL_OWNERSHIP_SPECIFICATION_V1_2026-07-11.md` Section 16 normativity principle. The sole remaining question, retained here: should the guarantee's synchronous-execution precondition (no concurrency, no external mid-tick read path, Section 8.3) be explicitly protected by a named Invariant or Constraint at a future Architecture stage? Not resolved here; no atomic publication mechanism is required or proposed by this document.

Blocking Effect: non-blocking for FR-013/FR-014, both currently evidenced; conditionally relevant only to a future Architecture document's own decision on whether to add explicit precondition protection.

OQ-004 - What specific mechanism, if any, should govern `CanonicalState`'s consistency when an unhandled exception propagates out of `RunLoop.step()` after some but not all of a tick's publications have already executed - an explicit partial-tick marker, an automatic `CanonicalState.reset()`, an explicit rollback to the prior tick's snapshot, or an explicit, justified decision that the current behaviour (no special handling) is architecturally accepted? Not resolved here (Gap 2, FR-020, RC-6).

Blocking Effect: blocking for FR-020's exact resolution; this document's own finding (the current absence of any such mechanism) is independently established regardless of the eventual answer.

OQ-005 - Is repeated invocation of a failed tick (retry) after an unhandled exception architecturally meaningful, given `RunLoop`'s and its collaborators' own persisted cross-tick instance state (for example, `RegimeClassifier`'s rolling window, `StrategySelector`'s cooldown counter), or does any such retry require those components' own state to first be explicitly reconciled? Not resolved here; a direct consequence of OQ-004 remaining open.

Blocking Effect: conditionally blocking for OQ-004's own resolution; not independently blocking.

OQ-006 - Does full-sequence Tick-Sequence Determinism (FR-017) require a dedicated, newly-authored replay validation distinct from the scripted sequences P2-03's and P2-04's own certifications already used, or does re-analysis of their existing evidence, framed explicitly as this unit's own finding, suffice to close Gap 3? Not resolved here.

Blocking Effect: conditionally blocking for FR-017's exact validation shape at the Specification stage; not blocking for this document's own conclusions.

OQ-007 - Does Gap 4 (`PerformanceEngine`'s decision-oriented accounting) belong to P3-02 (Information Flow Validation) or P3-03 (Performance Validation)? This document's own position (Section 14.9, FR-023) favors P3-03, by direct textual match to TD-004's own Target Phase description and to P3-03's own Implementation Baseline objective text ("Verify PerformanceEngine inputs. Validate Performance Metrics generation"), but does not treat this as a settled decision.

Blocking Effect: conditionally blocking for FR-023's exact closure venue; the Scientific Dependency Analysis or Capability Gap Analysis stage should confirm or adjust this positioning, consistent with how the P2-03 FRA's own comparable open question was later resolved by P2-03-AD-015.

OQ-008 - Is the observed divergence between the Runtime Ownership Matrix's "Market Regime" row (Writer-on-Behalf-Of: `RegimeClassifier`) and the actual runtime mechanism (`RunLoop` writes directly) itself evidence of a broader, not-yet-fully-catalogued pattern of Matrix-versus-implementation drift for other objects, or is it isolated to this one row? This document confirmed only the two objects Section 6.2's own trace directly implicated (Runtime Tick, Market Regime); a systematic, row-by-row Matrix audit was not performed, since it exceeds this unit's own scope (Section 2).

Blocking Effect: non-blocking for this document's own conclusions; recorded for a future Scientific Dependency Analysis or Capability Gap Analysis to consider.

## 23. Functional Readiness Decision

This analysis finds four confirmed, repository-grounded functional gaps within P3-01's own scope (Section 12.1), one Cross-Unit Observation forwarded to P3-02 (Section 12.2), and one Verified Conformant Finding (Section 12.3), following a targeted Scientific Consistency Review of the two findings originally numbered Gap 2 and Gap 3. All findings are directly within or immediately adjacent to P3-01's stated Baseline objectives ("Implement ADR-010 execution sequence. Verify Executor integration. Verify Tick-Complete Snapshot publication."). All twelve of ADR-010's named stages are confirmed, by independent, fresh re-trace against the current HEAD, to be realized in strictly correct relative order; the twelfth (Tick-Complete Publication) is confirmed both observably satisfied and verified conformant (VC-01), consistent with the already-certified P2-03 Specification's own governing normativity principle. Two of the four remaining gaps (unhandled-exception semantics, `CanonicalEnforcer`-bypassing writes) are structural findings not previously documented anywhere in this governance chain. All findings are localized to a small, already-understood set of files (`run_engine/core/loop.py`, `run_engine/main.py`, `run_engine/core/canonical_state.py`, `run_engine/core/canonical_enforcer.py`), with `run_engine/core/performance.py`'s Gap 4 explicitly scope-protected away from this unit.

No blocking ambiguity was found in the existing baseline text that would prevent proceeding: ADR-010's own Decision and Acceptance Criteria sections unambiguously enumerate the twelve stages and their required order; the Tick Completion Contract unambiguously states the externally-observable-only-after-completion requirement. Only the exact resolution mechanism for the remaining open items (OQ-001, OQ-003's residual precondition-protection question, OQ-004, OQ-006) and the P3-02/P3-03 boundary question (OQ-007) require architecture-stage decisions, consistent with how every prior P2-0x and P1-0x unit in this governance chain has left comparable decisions to its own Architecture document.

Functional Readiness: READY. This document is sufficient to proceed to the P3-01 Scientific Dependency Analysis. No further repository investigation is required before that step.

## 24. Internal Consistency Review

Terminology consistency - "Deterministic Runtime Execution Ordering," "Canonical Working State," "Tick-Complete Snapshot," "Tick-Sequence Determinism," "per-call statelessness," "Writer-on-Behalf-Of Path," and "Runtime Failure Event" are used exactly as defined in Section 5 throughout this document; no term is used ambiguously or interchangeably with another. "Functionally identical" is used for every Python-object, runtime-dictionary, or numeric comparison in this document (Sections 10, 14.3, 14.5, 20). "Byte-identical" is not used anywhere in this document to describe a comparison; its only occurrence is this sentence's own meta-discussion of the term, since no file- or git-blob-level comparison was performed directly by this analysis (Section 20 relies on the two prior certifications' own already-performed blob comparisons by citation, not by re-performing one here).

Ownership consistency - no requirement in Section 14 assigns ownership of any concept to a component other than what ADR-001 through ADR-009, the Runtime Ownership Matrix, or the P2-02A/P2-03/P2-04 certifications already assign; FR-019 identifies an observed Writer-on-Behalf-Of mechanism divergence (Gap 1) without proposing a new Authoritative Owner for either affected object.

Scope consistency - every requirement traces to either ADR-002/ADR-008/ADR-010/ADR-011 text directly, a Section 6 through 11 repository finding, or an already-logged Technical Debt Register item explicitly relevant to P3 (TD-004). No requirement duplicates P2-02A, P2-03, or P2-04 scope (FR-022 explicitly locks this in as a compatibility constraint); Section 15 explicitly excludes strategy, regime, executor, lifecycle, position, PnL, risk, and performance formula changes, persistence/recovery/schema evolution, parallel execution, implementation, testing, and long-duration validation.

Traceability consistency - Section 16's catalogue, Section 17's ADR mapping, Section 18's Invariant mapping, and Section 19's Acceptance-Criteria mapping are cross-checked: all twenty-three functional requirements appear in exactly one catalogue row each; every ADR, Invariant, and Acceptance Criterion the governing task named as a minimum traceability target (Section 3) is referenced by at least one requirement or explicitly noted as governed by a prior certification and preserved unchanged.

Observation/requirement/decision separation - Sections 6 through 11 contain only observations, each with a direct file/line/method citation. Section 12 synthesizes those observations into six named gaps. Section 14 contains only requirements derived from those gaps plus the binding baseline. Section 22 contains only open questions explicitly deferred to a future Scientific Dependency Analysis, Capability Gap Analysis, or Architecture document; no architecture decision, publication-mechanism design, or failure-handling mechanism is finalized anywhere in this document.

No fabricated capability - the `CanonicalEnforcer`-bypassing writes (Gap 1) and the absence of unhandled-exception semantics (Gap 2) are each explicitly and repeatedly documented as absent, not described as existing in any partial or approximate form; the `CanonicalState.get()` reference-semantics observation (CUO-01) and ADR-010 Stage 12's realization (VC-01) are each documented precisely as what a targeted Scientific Consistency Review determined them to be - a cross-unit forwarding item and a verified-conformant finding, respectively - neither overstated as a P3-01 functional defect; `PerformanceEngine`'s decision-oriented accounting (Gap 4) is documented as a confirmed, still-present, already-diagnosed defect, not misrepresented as new; no requirement in this document assumes a capability exists that repository inspection did not confirm.

Revision note - this document was revised following a targeted Scientific Consistency Review of the findings originally numbered Gap 2 (`CanonicalState.get()`'s reference semantics) and Gap 3 (ADR-010 Stage 12's realization). That review found neither to be a currently unmet P3-01 requirement: Gap 2 is reclassified as Cross-Unit Observation CUO-01 (Section 12.2), directed to P3-02; Gap 3 is reclassified as Verified Conformant Finding VC-01 (Section 12.3), grounded in `P2_03_FINANCIAL_OWNERSHIP_SPECIFICATION_V1_2026-07-11.md` Section 16's own already-certified normativity principle. The former Gap 4, Gap 5, and Gap 6 were renumbered to Gap 2, Gap 3, and Gap 4 respectively (Section 12.1); every cross-reference to these labels throughout Sections 6 through 23 was updated accordingly. No Functional Requirement was added or removed. FR-012's Scope Boundary, FR-013's Requirement Statement/Existing Evidence/Current Conformance/Validation Condition/Scope Boundary/Traceability, and FR-014's Current Conformance were precisified to reflect the revised classification; FR-013's content (the requirement that every tick culminate in exactly one Tick-Complete Publication) was retained, only the now-superseded "architectural mechanism SHALL be explicitly decided" clause was removed, since that clause was itself an artifact of the now-refuted gap framing. FR-011's and FR-023's cross-references to the renumbered Gap 4 were updated. Open Questions OQ-002 and OQ-003 were revised in place (not deleted, to preserve traceability) to record their disposition; OQ-004, OQ-006, and OQ-007's gap-number cross-references were updated. Section 23's Functional Readiness Decision and this section's own consistency findings were updated to reflect the revised gap count and classification. No architecture decision was made in the course of this revision; no P3-02 or P3-03 analysis was performed or anticipated beyond the explicit forwarding already recorded in FR-023.

Status: Internal Consistency Review PASS.
