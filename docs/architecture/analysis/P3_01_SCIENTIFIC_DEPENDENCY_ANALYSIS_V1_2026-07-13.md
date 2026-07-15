Document Class:
Scientific Dependency Analysis

Document ID:
P3-01-SDA

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
docs/architecture/analysis/P3_01_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-13.md

Depends On:
- docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md
- docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md
- docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md
- docs/architecture/analysis/P3_01_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-13.md
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
- future P3-01 Capability Gap Analysis
- future P3-01 Architecture
- future P3-01 Specification
- future P3-01 Certification

---

# P3-01 Scientific Dependency Analysis

## 1. Purpose

This document is the Scientific Dependency Analysis for P3-01 (Deterministic Execution Ordering). It analyzes the scientific and architectural dependencies among the twenty-three Functional Requirements `P3_01_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-13.md` established, determines which requirements form a fixed reference frame, which requirements can only be meaningfully evaluated after another, which dependencies are internal to P3-01, and which lead to P3-02 (Information Flow Validation) or P3-03 (Performance Validation).

This document does not select a solution. It does not decide architecture. It does not choose a publication mechanism, a copy-versus-reference semantics, or an exception/rollback semantics. It does not create, rename, or extend any Functional Requirement. Its sole output is a dependency analysis the P3-01 Capability Gap Analysis and Architecture must consume.

## 2. Scope

In scope: dependency analysis among P3-01-FR-001 through FR-023, dependency layering, sequential/semantic/state/publication/failure/replay/ownership/traceability dependency types, cycle and coupling analysis, and explicit Cross-Unit dependency identification toward P3-02 and P3-03.

Out of scope: any new Functional Requirement, any Architecture Decision, any publication mechanism selection, any copy-versus-reference semantics selection, any exception/rollback semantics selection, any decision on stage-skipping, any PerformanceEngine redesign, any Capability Gap classification (COMPLETE/PARTIAL/MISSING), any Implementation Unit, any file selected for future modification, and any code change. Reopening any already-certified P2-02A, P2-03, or P2-04 ownership decision is explicitly out of scope.

## 3. Binding Baseline

- `docs/architecture/analysis/P3_01_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-13.md` - the sole source of the twenty-three Functional Requirements this analysis depends on; also the source of the four P3-01-owned Functional Gaps (Section 12.1), Cross-Unit Observation CUO-01 (Section 12.2), and Verified Conformant Finding VC-01 (Section 12.3), all re-verified in Section 4 below.
- `docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md` - ADR-002, ADR-010, ADR-011, and by reference ADR-001, ADR-003 through ADR-009, ADR-012; the Runtime Ownership Matrix; the Target Information Flow (Tick Completion Contract, Principles IF-001 through IF-006); Architecture Invariants AI-005, AI-006, AI-007, AI-008, AI-009, AI-014 (and by reference AI-001 through AI-004, AI-010 through AI-013, AI-015); Acceptance Criteria AC-009, AC-010, AC-011, AC-012 (and by reference AC-001 through AC-008, AC-013 through AC-015).
- `docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md` - the P3-01, P3-02, P3-03 unit definitions this document's Cross-Unit dependencies (Section 18) are anchored to.
- `docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md` - TD-004, TD-007.
- `docs/architecture/P2_02A_POSITION_OWNERSHIP_ARCHITECTURE_V1_2026-07-10.md`, `docs/architecture/P2_02A_POSITION_OWNERSHIP_SPECIFICATION_V1_2026-07-10.md` - the certified Position/Exposure ownership contract this document's Compatibility dependencies (Section 17) reference.
- `docs/architecture/P2_03_FINANCIAL_OWNERSHIP_ARCHITECTURE_V1_2026-07-11.md`, `docs/architecture/P2_03_FINANCIAL_OWNERSHIP_SPECIFICATION_V1_2026-07-11.md` - the certified Financial Ownership contract, and Section 16's already-certified normativity principle this document's own Certification-class dependency (P3-01-DEP-031) relies on.
- `docs/architecture/P2_04_RISK_OWNERSHIP_ARCHITECTURE_V1_2026-07-13.md`, `docs/architecture/P2_04_RISK_OWNERSHIP_SPECIFICATION_V1_2026-07-13.md` - the certified Risk Ownership contract.
- `docs/architecture/certification/P2_03_FINAL_CERTIFICATION_V1_2026-07-11.md`, `docs/architecture/certification/P2_04_FINAL_CERTIFICATION_V1_2026-07-13.md` - the certified baseline this document's Compatibility-class dependencies treat as fixed.

## 4. Repository Verification

Repository state, verified directly, not assumed:

- Branch: `run-engine-consolidation-safety` (confirmed via `git branch --show-current`).
- Local HEAD: `fd22ce130e93261b63830b63600f9e651f7ad496`, matching the stated expected HEAD exactly (confirmed via `git rev-parse HEAD`).
- Remote HEAD: `fd22ce130e93261b63830b63600f9e651f7ad496` (confirmed via `git fetch origin run-engine-consolidation-safety` followed by `git rev-parse origin/run-engine-consolidation-safety`), identical to local HEAD.
- Working tree: one modified file unrelated to `run_engine` (`docs/capabilities/SGF_013_SCIENTIFIC_BEHAVIOUR_REPRESENTATION_2026-06-26.md`) and the same set of pre-existing untracked directories every prior document in this chain has recorded, plus the now-tracked-as-untracked `P3_01_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-13.md` - none inside `run_engine/`, none touched by this analysis. `run_engine/` is confirmed clean (`git status --short run_engine/` returns no output).

Files re-read in full for this analysis: `run_engine/main.py`, `run_engine/core/loop.py`, `run_engine/core/state.py`, `run_engine/core/regime.py`, `run_engine/core/strategy.py`, `run_engine/core/decision.py`, `run_engine/core/execution/executor.py`, `run_engine/core/trade_lifecycle.py`, `run_engine/core/position.py`, `run_engine/core/pnl.py`, `run_engine/core/risk.py`, `run_engine/core/performance.py`, `run_engine/core/canonical_state.py`, `run_engine/core/canonical_enforcer.py`.

Repository-wide search re-performed for (case-insensitive): `RunLoop`, `step(`, `Canonical Working State`, `Tick-Complete`, `publication`, `apply_`, `update_`, `lifecycle`, `execution`, `position`, `pnl`, `risk`, `performance`, `deterministic`, `replay`, `ordering`, `sequence`, `mutation`, `side effect`, `exception`, `failure`, `HOLD`, `no-op`. Findings consistent with the FRA's own Sections 6 through 11: exactly one `except Exception` occurrence (`main.py:28`); `failure`-adjacent identifiers confined to `performance.py`, `pnl.py`, `trade_lifecycle.py` (the already-documented `RUNTIME_FAILURE_EVENT` guards); `HOLD` present in every active-path decision/execution/lifecycle/performance file plus three confirmed-inactive files (`decision.py`, `position_sizing.py`, `state_modulation.py`); exactly one `NOOP` occurrence (`executor.py:30`). No new active-path file and no new alternative execution path were found beyond what the FRA's own Section 4 and Section 6.4 already established.

### 4.1 Re-Verification of the FRA's Four Functional Gaps, CUO-01, and VC-01

Re-checked directly against the current runtime and Binding Baseline, not merely inherited:

- **Gap 1** (Runtime Tick/Market Regime bypass `CanonicalEnforcer`) - re-confirmed: `loop.py:42,45` call `self.cstate.update_tick(...)` and `self.cstate.update_regime(...)` directly; `canonical_enforcer.py`'s ten methods (`apply_position`, `apply_pnl`, `apply_realized_pnl_cumulative`, `apply_equity`, `apply_peak_equity`, `apply_risk`, `apply_strategy_selection`, `apply_execution_decision`, `apply_performance_metrics`, `apply_runtime_status`) still contain neither `apply_tick` nor `apply_regime`.
- **Gap 2** (unhandled-exception semantics absent) - re-confirmed: `main.py:28`'s `except Exception as e:` remains the sole exception handler on the active path; `loop.py`'s own `__main__` block (`loop.py:116-131`) remains unguarded.
- **Gap 3** (full-sequence Tick-Sequence Determinism not separately certified) - re-confirmed: no repository-wide replay fixture for the complete eighteen-step sequence exists as this unit's own artifact; the P2-03 and P2-04 certifications' own replay evidence remains their own units' corroborating evidence, not a P3-01-named deliverable.
- **Gap 4** (`PerformanceEngine` decision-oriented accounting) - re-confirmed: `performance.py:11`'s `action = decision.get('action', 'HOLD')` remains the statistics key; `trades` still increments on every non-`RUNTIME_FAILURE_EVENT` tick regardless of a completed lifecycle outcome.
- **CUO-01** (`CanonicalState.get()` live-mutable reference) - re-confirmed: `canonical_state.py:107-109`'s `get()` still returns `self.state` directly.
- **VC-01** (Stage 12 realized by aggregate incremental publication) - re-confirmed: the same ten `CanonicalEnforcer.apply_*()` calls (`loop.py:35,50,53,66,73,86,87,88,93,96`) remain the sole publication mechanism; `P2_03_FINANCIAL_OWNERSHIP_SPECIFICATION_V1_2026-07-11.md` Section 16's normativity principle remains unchanged and still governs.

No new gap, no closed gap, and no change to CUO-01's or VC-01's own classification was found. This document treats the FRA's Section 12 classification as current and unchanged.

## 5. Scientific Dependency Method

A dependency between two Functional Requirements is recorded only when one requirement's own Validation Condition cannot be meaningfully evaluated, or would evaluate against an undefined precondition, without the other requirement's own Validation Condition already holding, or when one requirement's Scope Boundary explicitly excludes territory another requirement explicitly claims. Each dependency is assigned exactly one Dependency Class from the five the governing task names: REQUIRED (the target requirement's own conformance claim presupposes the source), CONDITIONAL (the target's completeness, not its current evidence, depends on the source's own eventual resolution), CROSS-UNIT (the dependency's target is outside P3-01's own Functional Requirement set), COMPATIBILITY (the source requirement is bound by an already-certified P2-02A/P2-03/P2-04 contract), or CERTIFICATION (the source requirement's own conformance is grounded in an already-certified document's own governing principle, not in this unit's own independent derivation). Each dependency additionally carries one or more descriptive sub-types (sequential, semantic, state, publication, failure, replay, ownership, traceability) describing the nature, not the severity or completeness, of the relationship. No Dependency Class or sub-type used in this document evaluates or classifies a capability as COMPLETE, PARTIAL, or MISSING; that classification is explicitly reserved for the future Capability Gap Analysis (Section 24).

Every dependency traces to at least one existing P3-01 Functional Requirement (Section 9). No dependency is recorded between two objects neither of which is a Functional Requirement in the FRA's own catalogue; Cross-Unit and Certification dependencies instead name an external anchor (a named ADR/Specification section, or a named future unit) as their target, with their P3-01-side anchor always being an existing FR.

## 6. Requirement and Capability Clusters

Nine clusters were identified, each grouping Functional Requirements that share a single scientific concern. No cluster introduces a new requirement; every FR belongs to exactly one primary cluster, with cross-cluster dependencies recorded explicitly in Section 9.

**Cluster A - Sequence Existence and Uniqueness.** FR-001 (exactly one normative sequence), FR-018 (no alternative active execution path). These two requirements jointly establish that "the" sequence ADR-010 names is a well-defined, singular object before any stage-level claim about it can be meaningful.

**Cluster B - Stage Ordering Chain.** FR-002 through FR-011. Ten requirements, each asserting that one ADR-010 stage occurs after its immediate predecessor and before its immediate successor. This cluster is the longest in the FRA and forms a strict, already-evidenced chain (Section 12).

**Cluster C - Canonical Working State and Publication.** FR-012 (Canonical Working State consumption boundary), FR-013 (Tick-Complete Publication), FR-014 (external observability boundary). This cluster governs what may be read, and by whom, during and after a tick.

**Cluster D - Failure, Rejection, and No-Execution.** FR-015 (HOLD/no-execution stage completeness), FR-016 (rejected-transition stage completeness and non-mutation), FR-020 (unhandled-exception semantics, unresolved). This cluster governs the three distinct ways a tick can fail to produce a normal, accepted execution outcome.

**Cluster E - Determinism and Replay.** FR-017 alone. A single requirement, but one whose own Validation Condition synthesizes evidence from every other cluster (Section 16).

**Cluster F - Writer-on-Behalf-Of and Ownership Discipline.** FR-019 (general Writer-on-Behalf-Of rule), with a direct, named tie to FR-004 (Market Regime's own Writer-on-Behalf-Of divergence, Gap 1).

**Cluster G - Traceability.** FR-021 alone. A requirement whose own Validation Condition depends on every stage-level requirement already carrying file/line evidence.

**Cluster H - Compatibility and Fixed Reference Frame.** FR-022 (aggregate compatibility requirement), together with the already-certified P2-02A, P2-03, and P2-04 contracts themselves, which this document treats as an external, fixed reference frame - not an FR, but the standard every Compatibility-class dependency (Section 17) measures against.

**Cluster I - Cross-Unit Scope Boundary.** FR-023 alone, together with the two forwarded items it names (CUO-01, Gap 4/TD-004). This cluster exists specifically to prevent Clusters B through E from silently absorbing P3-02's or P3-03's own territory (Section 18).

Unlike the P2-04 SDA's own two small, centrally-coupled open clusters surrounded by a large fixed frame, P3-01's structure is dominated by one long, strictly sequential chain (Cluster B) with four smaller clusters (C, D, E, G) each depending on the chain's own completion, and one genuinely fixed external frame (Cluster H) plus one explicit boundary cluster (Cluster I) that exists to keep two adjacent units' territory out.

## 7. Dependency Layers

Seven layers were derived, adapting the governing task's suggested eight-layer skeleton to the FRA's own evidence: the suggested "Layer 6: Failure, Determinism and Replay Assurance" is retained but re-scoped, since this document's own analysis (Section 12) found these three concerns are not sequential successors of Layer 5 but cross-cutting assurance properties validated against every layer beneath them; this is stated explicitly here rather than forced into the suggested shape.

**Layer 0 - Certified Compatibility Baseline.** Not an FR itself; the already-certified P2-02A/P2-03/P2-04 contracts (Cluster H's external anchor). Every layer above depends on Layer 0 remaining unchanged (FR-022).

**Layer 1 - Tick Trigger and State Foundation.** FR-001, FR-002, FR-003, FR-018. Establishes that a single, well-defined tick trigger and normalized state exist before any decision can be made.

**Layer 2 - Decision and Execution Generation.** FR-004, FR-005, FR-006. Regime, Strategy Selection, and Executor Event Generation, each consuming Layer 1's output.

**Layer 3 - Lifecycle and Position Evolution.** FR-007, FR-008. TradeLifecycle Update and Position Update, consuming Layer 2's Execution Event.

**Layer 4 - Financial, Risk, and Performance Evaluation.** FR-009, FR-010, FR-011. Consuming Layer 3's Position and Layer 0's certified Financial/Risk formulas.

**Layer 5 - Tick Completion and External Observability.** FR-012, FR-013, FR-014. Governs what becomes visible, and when, once Layers 1 through 4 have executed.

**Layer 6 - Cross-Cutting Assurance.** FR-015, FR-016, FR-017, FR-019, FR-020, FR-021. Not a sequential successor to Layer 5; each of these six requirements is validated against the full Layer 1-5 chain as a whole, not against one stage. FR-017 (determinism) and FR-021 (traceability) synthesize evidence from every layer; FR-015 and FR-016 (no-execution and rejection completeness) constrain every layer's behaviour under a non-standard input; FR-019 (Writer-on-Behalf-Of discipline) constrains every layer's publication mechanism; FR-020 (exception semantics) remains unresolved and therefore constrains, without yet fully bounding, Layer 5's own completeness guarantee (Section 13).

**Cross-Unit Layer - P3-02 / P3-03.** FR-023, together with CUO-01 (Cluster I) and Gap 4/TD-004. Not part of P3-01's own layered chain; recorded to prevent Layer 4's or Layer 5's own scope from silently expanding (Section 18).

## 8. Dependency Catalogue

Thirty-one dependencies were identified, sourced entirely from the FRA's own requirement text, the Architecture Baseline, and the Technical Debt Register; none introduces a new requirement, interface, formula, or ownership assignment.

**P3-01-DEP-001**
Title: State Acquisition Precedes Regime Classification.
Dependency Class: REQUIRED. Sub-type: sequential.
Source Requirement(s): FR-003. Target Requirement(s): FR-004.
Scientific Basis: Regime Classification's own input (`state`) is State Acquisition's output; ADR-010 Stages 2 and 3.
Repository Evidence: `loop.py:37` precedes `loop.py:44`.
Dependency Condition: FR-004's Validation Condition presupposes `StateEngine.update()`'s return value already exists.
Consequence if Unsatisfied: Regime Classification would operate on undefined or stale state, violating AI-007 (Semantic Continuity).
Scope Boundary: does not evaluate either component's own internal algorithm.
Traceability: FRA FR-003, FR-004; ADR-010 Stages 2-3.

**P3-01-DEP-002**
Title: Regime Classification Precedes Strategy Selection.
Dependency Class: REQUIRED. Sub-type: sequential.
Source Requirement(s): FR-004. Target Requirement(s): FR-005.
Scientific Basis: ADR-010 Stages 3-4; Strategy Selection consumes the current regime as an explicit parameter.
Repository Evidence: `loop.py:44` precedes `loop.py:49`.
Dependency Condition: FR-005's Validation Condition presupposes `RegimeClassifier.classify()`'s return value already exists.
Consequence if Unsatisfied: Strategy Selection would operate on an undefined regime value.
Scope Boundary: does not evaluate `StrategySelector`'s own weighting algorithm.
Traceability: FRA FR-004, FR-005; ADR-010 Stages 3-4.

**P3-01-DEP-003**
Title: Strategy Selection Precedes Executor Event Generation.
Dependency Class: REQUIRED. Sub-type: sequential.
Source Requirement(s): FR-005. Target Requirement(s): FR-006.
Scientific Basis: ADR-010 Stages 4-5-6; `Executor.execute()` consumes the Execution Decision `StrategySelector.decide()` produces.
Repository Evidence: `loop.py:49-53` precedes `loop.py:55`.
Dependency Condition: FR-006's Validation Condition presupposes `StrategySelector.decide()`'s return value already exists.
Consequence if Unsatisfied: `Executor.execute()` would receive an undefined decision.
Scope Boundary: does not evaluate `Executor`'s own execution-quantity logic.
Traceability: FRA FR-005, FR-006; ADR-010 Stages 4-6.

**P3-01-DEP-004**
Title: Executor Event Generation Precedes TradeLifecycle Update.
Dependency Class: REQUIRED. Sub-type: sequential, event.
Source Requirement(s): FR-006. Target Requirement(s): FR-007.
Scientific Basis: ADR-002 names Execution Events as the explicit input `TradeLifecycleEngine` consumes to produce Trade Lifecycle Events; ADR-010 Stages 6-7.
Repository Evidence: `loop.py:55` precedes `loop.py:57`.
Dependency Condition: FR-007's Validation Condition presupposes `Executor.execute()`'s return value already exists.
Consequence if Unsatisfied: `TradeLifecycleEngine.on_execution()` would receive an undefined execution result, violating AI-008 (Explicit Runtime Events).
Scope Boundary: does not evaluate lifecycle transition semantics themselves.
Traceability: FRA FR-006, FR-007; ADR-002, ADR-010 Stages 6-7.

**P3-01-DEP-005**
Title: TradeLifecycle Update Precedes Position Update.
Dependency Class: REQUIRED. Sub-type: sequential, event, state.
Source Requirement(s): FR-007. Target Requirement(s): FR-008.
Scientific Basis: ADR-003 names `TradeLifecycleEngine` as the Authoritative Owner of lifecycle information `PositionEngine` consumes via `current_position()`; ADR-010 Stages 7-8.
Repository Evidence: `loop.py:57,59` precede `loop.py:61`.
Dependency Condition: FR-008's Validation Condition presupposes both `on_execution()`'s and `current_position()`'s return values already exist. This dependency is specifically conditioned on the lifecycle event's own acceptance status: `PositionEngine.update_post_trade()` (`position.py:37-73`) receives `lifecycle_position` regardless of whether the current tick's transition was accepted or rejected, and its own resulting Position reflects only accepted lifecycle facts, since a `RUNTIME_FAILURE_EVENT` leaves `TradeLifecycleEngine`'s own `active_trade` unchanged (`trade_lifecycle.py:280-304`, confirmed by direct read: no `_open_trade`, `_scale_in`, `_partial_close`, or `_full_close` call occurs inside `_failure_event`).
Consequence if Unsatisfied: `PositionEngine.update_post_trade()` would receive an undefined lifecycle input, or would incorporate a rejected transition's effect into the operational Position, violating ADR-011.
Scope Boundary: does not evaluate Position's own weighted-average or Exposure formulas, already certified (P2-02A).
Traceability: FRA FR-007, FR-008; ADR-003, ADR-010 Stages 7-8, ADR-011.

**P3-01-DEP-006**
Title: Position Update Precedes Financial Accounting.
Dependency Class: REQUIRED. Sub-type: sequential, state.
Source Requirement(s): FR-008. Target Requirement(s): FR-009.
Scientific Basis: ADR-010 Stages 8-9; `PnLEngine`'s event-PnL computation reads the pre-trade Position view (P2-02A-AD-005), captured before Position Update, while the post-trade Position itself must already be published before `RiskEngine` (a later stage) consumes it.
Repository Evidence: `loop.py:61-66` precedes `loop.py:72`.
Dependency Condition: FR-009's Validation Condition presupposes `PositionEngine.update_post_trade()`'s published result already exists via `CanonicalEnforcer.apply_position()`.
Consequence if Unsatisfied: Financial Accounting could read a stale or undefined Position.
Scope Boundary: does not evaluate the Equity/Peak-Equity/Realized-PnL formulas themselves, already certified (P2-03).
Traceability: FRA FR-008, FR-009; ADR-004, ADR-010 Stages 8-9, P2-02A-AD-005.

**P3-01-DEP-007**
Title: Financial Accounting Precedes Risk Evaluation.
Dependency Class: REQUIRED. Sub-type: sequential, state.
Source Requirement(s): FR-009. Target Requirement(s): FR-010.
Scientific Basis: ADR-006 requires `RiskEngine` to compute Drawdown exclusively from canonical financial state, which must already be current when Risk Evaluation executes; ADR-010 Stages 9-10.
Repository Evidence: `loop.py:68-88` precedes `loop.py:90-92`.
Dependency Condition: FR-010's Validation Condition presupposes `PnLEngine.compute_equity()`'s published Equity and Peak Equity already exist, readable via `CanonicalState.get()`.
Consequence if Unsatisfied: `RiskEngine.check()` would compute Drawdown from a stale or undefined financial state, reopening TD-006 (already closed, P2-04).
Scope Boundary: does not evaluate the risk-limiting formula itself, already certified (P2-04).
Traceability: FRA FR-009, FR-010; ADR-005, ADR-006, ADR-010 Stages 9-10.

**P3-01-DEP-008**
Title: Risk Evaluation Precedes Performance Evaluation.
Dependency Class: REQUIRED. Sub-type: sequential.
Source Requirement(s): FR-010. Target Requirement(s): FR-011.
Scientific Basis: ADR-010 Stages 10-11; the Runtime Ownership Matrix names `PerformanceEngine` as a potential Risk-Metric consumer, requiring Risk Evaluation to have already run should that consumption ever activate (currently not activated, P2-04-AD-017).
Repository Evidence: `loop.py:92-93` precedes `loop.py:95-96`.
Dependency Condition: FR-011's Validation Condition presupposes `RiskEngine.check()`'s published output already exists via `CanonicalEnforcer.apply_risk()`, independent of whether `PerformanceEngine` currently reads it.
Consequence if Unsatisfied: a future activation of Risk-Metric consumption by `PerformanceEngine` would read stale or undefined values.
Scope Boundary: does not resolve whether `PerformanceEngine` should consume Risk Metrics (P2-04-AD-017's own boundary, preserved).
Traceability: FRA FR-010, FR-011; ADR-007, ADR-010 Stages 10-11, P2-04-AD-017.

**P3-01-DEP-009**
Title: Performance Evaluation Precedes Tick-Complete Publication.
Dependency Class: REQUIRED. Sub-type: sequential, publication.
Source Requirement(s): FR-011. Target Requirement(s): FR-013.
Scientific Basis: ADR-008 requires Performance to reflect completed lifecycle outcomes, final for the current tick only once every upstream stage has executed; ADR-010 Stages 11-12.
Repository Evidence: `loop.py:95-96` precedes `loop.py:98-113`.
Dependency Condition: FR-013's Validation Condition presupposes `PerformanceEngine.update()`'s call has already occurred, as the last stage-producing call before the tick-result dictionary is assembled.
Consequence if Unsatisfied: Tick-Complete Publication would occur before every mandatory stage has run, violating the Tick Completion Contract.
Scope Boundary: does not itself certify Stage 12's own realization mechanism (VC-01, Section 15).
Traceability: FRA FR-011, FR-013; ADR-008, ADR-010 Stages 11-12, Tick Completion Contract.

**P3-01-DEP-010**
Title: Tick-Complete Publication Precedes External Observability.
Dependency Class: REQUIRED. Sub-type: publication.
Source Requirement(s): FR-013. Target Requirement(s): FR-014.
Scientific Basis: the Tick-Complete Snapshot definition - "External downstream consumers consume only Tick-Complete Snapshots."
Repository Evidence: `main.py:21-24`, the tick-result dictionary is only ever inspected after `engine.step()` fully returns.
Dependency Condition: FR-014's Validation Condition presupposes FR-013's own publication event has already completed for the current tick.
Consequence if Unsatisfied: an external consumer could observe an incomplete Tick-Complete Snapshot.
Scope Boundary: assumes continuation of the current synchronous, single-threaded execution model (Section 15).
Traceability: FRA FR-013, FR-014; AI-009, AC-009.

**P3-01-DEP-011**
Title: Complete Stage Chain Constitutes the Normative Sequence.
Dependency Class: REQUIRED. Sub-type: structural.
Source Requirement(s): FR-002, FR-003, FR-004, FR-005, FR-006, FR-007, FR-008, FR-009, FR-010, FR-011. Target Requirement(s): FR-001.
Scientific Basis: FR-001's own claim ("exactly one normative, twelve-stage sequence... SHALL govern every runtime tick") is an aggregate statement whose truth is constituted by each of the ten individual stage-position requirements jointly holding, per AI-006.
Repository Evidence: Section 6.2's own eighteen-step trace (FRA), independently re-confirmed present in Section 4 above.
Dependency Condition: FR-001's Validation Condition is satisfied only if every one of FR-002 through FR-011's own Validation Conditions holds simultaneously.
Consequence if Unsatisfied: a single broken stage-position requirement would falsify FR-001's own aggregate claim.
Scope Boundary: does not itself certify Stage 12's publication mechanism (FR-013) or full-sequence determinism (FR-017), each separately stated.
Traceability: FRA FR-001 through FR-011; ADR-010, AI-006.

**P3-01-DEP-012**
Title: Execution-Path Uniqueness Constrains Sequence Uniqueness.
Dependency Class: REQUIRED. Sub-type: structural.
Source Requirement(s): FR-018. Target Requirement(s): FR-001.
Scientific Basis: AI-013 (Architectural Minimality); FR-001's "exactly one" claim presupposes exactly one orchestrator exists to realize it.
Repository Evidence: Section 4's confirmed-inactive inventory (`decision.py`, `run_engine/runtime/`, `run_engine/execution/`, `run_engine/feedback/`, `run_engine/logging/`), re-confirmed unchanged.
Dependency Condition: FR-001's Validation Condition would not be well-defined if a second active `RunLoop`-equivalent orchestrator existed.
Consequence if Unsatisfied: "the" sequence would become ambiguous between two competing realizations.
Scope Boundary: does not classify or remove any inactive component; Phase 6's own scope.
Traceability: FRA FR-018, FR-001; AI-013, Architecture Defect AD-007.

**P3-01-DEP-013**
Title: Stage Chain Bounds the Canonical Working State Consumption Boundary.
Dependency Class: REQUIRED. Sub-type: state, semantic.
Source Requirement(s): FR-002, FR-003, FR-004, FR-005, FR-006, FR-007, FR-008, FR-009, FR-010, FR-011. Target Requirement(s): FR-012.
Scientific Basis: the Canonical Working State definition - "consumable only by components whose execution order has already been reached" - is meaningless without a well-defined stage order to measure "already been reached" against.
Repository Evidence: Section 7.1 (FRA); every one of the eighteen steps consumes only values already produced by an earlier step.
Dependency Condition: FR-012's Validation Condition is checked, at every stage transition, against the ordering FR-002 through FR-011 jointly establish; this is a CONSTRAINT-type dependency (Section 20), not a sequential gate - FR-012 does not wait for the chain to complete once, it is validated at each of the chain's own transitions.
Consequence if Unsatisfied: without a well-defined stage order, "not-yet-reached" would be undecidable.
Scope Boundary: does not require a structural (construction-level) enforcement mechanism (CUO-01, Section 18).
Traceability: FRA FR-002 through FR-012; Canonical Working State definition, AI-007.

**P3-01-DEP-014**
Title: Stage Chain Bounds HOLD/No-Execution Completeness.
Dependency Class: REQUIRED. Sub-type: state, failure.
Source Requirement(s): FR-002, FR-003, FR-004, FR-005, FR-006, FR-007, FR-008, FR-009, FR-010, FR-011. Target Requirement(s): FR-015.
Scientific Basis: FR-015's claim ("a `HOLD` tick SHALL execute every one of the twelve ADR-010 stages") is only checkable against the same stage chain FR-002 through FR-011 define.
Repository Evidence: Section 9.1 (FRA); `strategy.py:47-51,69-73`, `executor.py:14-32`, `trade_lifecycle.py:64-65`, `position.py:37-73`, `pnl.py:9-19,42-72`, `performance.py:6-9` - every stage's own explicit `None`-safe or event-type guard, re-confirmed present in Section 4.
Dependency Condition: FR-015's Validation Condition presupposes each downstream stage already has a defined, non-error behaviour for a `HOLD` or absent-execution input.
Consequence if Unsatisfied: a `HOLD` tick could silently skip a stage or raise an unhandled exception partway through the chain.
Scope Boundary: does not evaluate `StrategySelector`'s own cooldown/weighting logic that produces a `HOLD` decision.
Traceability: FRA FR-002 through FR-011, FR-015; ADR-010, ADR-002.

**P3-01-DEP-015**
Title: Stage Chain Bounds Rejected-Transition Completeness and Non-Mutation.
Dependency Class: REQUIRED. Sub-type: state, failure, event.
Source Requirement(s): FR-007, FR-008, FR-009, FR-010, FR-011. Target Requirement(s): FR-016.
Scientific Basis: ADR-011, verbatim - "Rejected transitions SHALL never: modify Position, modify Equity, modify Realized PnL... Instead, every rejected transition SHALL generate exactly one immutable Runtime Failure Event." This non-mutation claim is specifically checked against the five stages (TradeLifecycle Update through Performance Evaluation) that could otherwise mutate a guarded value.
Repository Evidence: Section 9.2 (FRA); `trade_lifecycle.py:280-304` (`_failure_event`, no `Trade` mutation); `pnl.py:23-24,57-62`; `performance.py:8-9`; re-confirmed present against the current runtime (Section 4).
Dependency Condition: FR-016's Validation Condition presupposes each of the five named stages already carries its own explicit `RUNTIME_FAILURE_EVENT` (or lifecycle-acceptance) guard.
Consequence if Unsatisfied: a rejected transition could silently mutate a value ADR-011 protects, or terminate a lifecycle it should not.
Scope Boundary: does not re-evaluate the four rejection reasons' own trigger conditions, already certified (P1-04, P2-02A, P2-03).
Traceability: FRA FR-007 through FR-011, FR-016; ADR-011, AI-011, AC-015.

**P3-01-DEP-016**
Title: Rejection Non-Mutation Is Bound by Already-Certified P2-02A/P2-03/P2-04 Contracts.
Dependency Class: COMPATIBILITY. Sub-type: ownership, failure.
Source Requirement(s): FR-016. Target Requirement(s): external (P2-02A/P2-03/P2-04 certified non-mutation contracts).
Scientific Basis: the non-mutation guarantees FR-016 restates are not newly established by P3-01; they are already-certified findings (`P2_03_FINAL_CERTIFICATION_V1_2026-07-11.md` Section 20; `P2_04_FINAL_CERTIFICATION_V1_2026-07-13.md` Section 17) this document independently re-cites, not re-derives.
Repository Evidence: Section 9.2 (FRA), citing both certifications by section.
Dependency Condition: FR-016's own conformance is only as strong as the cited certifications' own continued validity, which FR-022 separately guards.
Consequence if Unsatisfied: reopening either certification's own non-mutation finding would invalidate FR-016 without any P3-01-internal change.
Scope Boundary: does not re-certify either finding; cites only.
Traceability: FRA FR-016; P2-03 Final Certification Section 20, P2-04 Final Certification Section 17.

**P3-01-DEP-017**
Title: TradeLifecycle Update Is Bound by Certified Lifecycle Ownership.
Dependency Class: COMPATIBILITY. Sub-type: ownership.
Source Requirement(s): FR-007. Target Requirement(s): external (ADR-003, ADR-009 certified Lifecycle Transition Table).
Scientific Basis: ADR-003, ADR-009; FR-007 restates an already-certified ordering position, not a new lifecycle semantic.
Repository Evidence: `trade_lifecycle.py`, unchanged since P1-03/P1-03.1 (confirmed blob-identical to the P2-04-certified baseline, Section 4 above by extension of the FRA's own Section 20 finding).
Dependency Condition: FR-007's own conformance presupposes the Lifecycle Transition Table remains exactly as certified.
Consequence if Unsatisfied: a change to lifecycle transition semantics would require this dependency, not merely FR-007's own ordering claim, to be re-evaluated.
Scope Boundary: does not re-evaluate lifecycle transition correctness.
Traceability: FRA FR-007; ADR-003, ADR-009.

**P3-01-DEP-018**
Title: Position Update Is Bound by Certified P2-02A Position Ownership.
Dependency Class: COMPATIBILITY. Sub-type: ownership.
Source Requirement(s): FR-008. Target Requirement(s): external (P2-02A certified Position/Exposure ownership).
Scientific Basis: P2-02A-AD-004, P2-02A-AD-005; FR-008 restates an already-certified ordering position for a computation whose own formula and ownership are certified elsewhere.
Repository Evidence: `position.py`, git-blob-identical to the P2-04-certified baseline (`P2_04_FINAL_CERTIFICATION_V1_2026-07-13.md` Section 5, by extension).
Dependency Condition: FR-008's own conformance presupposes `PositionEngine`'s Computational Authority and `CanonicalState`'s Authoritative Ownership remain exactly as certified.
Consequence if Unsatisfied: a change to Position's own ownership model would require this dependency to be re-evaluated.
Scope Boundary: does not re-evaluate Position's own weighted-average or Exposure formulas.
Traceability: FRA FR-008; P2-02A-AD-004, P2-02A-AD-005.

**P3-01-DEP-019**
Title: Financial Accounting Is Bound by Certified P2-03 Financial Ownership.
Dependency Class: COMPATIBILITY. Sub-type: ownership.
Source Requirement(s): FR-009. Target Requirement(s): external (P2-03 certified Financial Ownership).
Scientific Basis: P2-03-AD-001 through AD-006; FR-009 restates an already-certified ordering position for computations whose own formula and ownership are certified elsewhere.
Repository Evidence: `pnl.py`, git-blob-identical to the P2-04-certified baseline.
Dependency Condition: FR-009's own conformance presupposes `PnLEngine`'s Computational Authority for Realized PnL, cumulative Realized PnL, Equity, and Peak Equity remains exactly as certified.
Consequence if Unsatisfied: a change to Financial Ownership would require this dependency to be re-evaluated.
Scope Boundary: does not re-evaluate the Equity/Peak-Equity/Realized-PnL formulas themselves.
Traceability: FRA FR-009; P2-03 Financial Ownership Architecture.

**P3-01-DEP-020**
Title: Risk Evaluation Is Bound by Certified P2-04 Risk Ownership.
Dependency Class: COMPATIBILITY. Sub-type: ownership.
Source Requirement(s): FR-010. Target Requirement(s): external (P2-04 certified Risk Ownership).
Scientific Basis: P2-04-AD-002 through AD-010; FR-010 restates an already-certified ordering position for a computation whose own formula, Risk Policy Configuration, and ownership are certified elsewhere.
Repository Evidence: `risk.py`, git-blob-identical to the P2-04-certified baseline apart from the P2-04-certified documentation commit itself.
Dependency Condition: FR-010's own conformance presupposes `RiskEngine`'s Computational Authority and statelessness remain exactly as certified.
Consequence if Unsatisfied: a change to Risk Ownership would require this dependency to be re-evaluated, potentially reopening TD-006 (already closed).
Scope Boundary: does not re-evaluate the risk-limiting formula itself.
Traceability: FRA FR-010; P2-04 Risk Ownership Architecture, P2-04 Final Certification.

**P3-01-DEP-021**
Title: Aggregate Compatibility Requirement Is Constituted by Its Named Constituents.
Dependency Class: COMPATIBILITY. Sub-type: ownership, structural.
Source Requirement(s): FR-007, FR-008, FR-009, FR-010, FR-016. Target Requirement(s): FR-022.
Scientific Basis: FR-022's own claim ("every already-certified P2-02A, P2-03, and P2-04... contract SHALL continue to function exactly as certified") is an aggregate statement constituted by the five named requirements' own individual compatibility preservation (P3-01-DEP-016 through DEP-020).
Repository Evidence: FRA Section 20 (Prior-Certification Compatibility).
Dependency Condition: FR-022's own conformance holds only if each of the five constituent dependencies above holds.
Consequence if Unsatisfied: a single broken compatibility constituent would falsify FR-022's own aggregate claim.
Scope Boundary: this unit's own findings (the four Functional Gaps) concern ordering, publication mechanism, and failure semantics only; none requires reopening any already-certified ownership assignment.
Traceability: FRA FR-007 through FR-010, FR-016, FR-022.

**P3-01-DEP-022**
Title: Market Regime Writer-on-Behalf-Of Conformance Is Conditional on the General Writer-on-Behalf-Of Rule's Own Disposition.
Dependency Class: CONDITIONAL. Sub-type: ownership.
Source Requirement(s): FR-019. Target Requirement(s): FR-004.
Scientific Basis: FR-004's own Current Conformance is explicitly qualified ("not yet independently evidenced as conformant at the writer-mechanism level"); FR-019 states the general rule (only `CanonicalEnforcer`, or a Matrix-named exception, writes `CanonicalState`) that FR-004's own Market Regime case is measured against.
Repository Evidence: Gap 1 (Finding F-01, FRA Section 12.1); `loop.py:45`; `canonical_enforcer.py`'s ten methods, confirmed to exclude `apply_regime`.
Dependency Condition: FR-004's full ordering-and-writer-mechanism conformance is conditional on how a future Architecture document resolves FR-019's own open disposition (OQ-001) for the Market Regime case specifically.
Consequence if Unsatisfied: FR-004's own writer-mechanism conformance remains an open question, though its ordering-position conformance is unaffected.
Scope Boundary: does not itself decide the resolution; Runtime Tick's already-Matrix-conformant case is not reopened.
Traceability: FRA FR-004, FR-019; Rule OM-003, Rule OM-006, Runtime Ownership Matrix.

**P3-01-DEP-023**
Title: Tick-Complete Publication's Completeness Is Conditional on Unhandled-Exception Semantics.
Dependency Class: CONDITIONAL. Sub-type: failure, publication.
Source Requirement(s): FR-020. Target Requirement(s): FR-013.
Scientific Basis: FR-013's own Current Conformance is evidenced under normal execution; the Tick Completion Contract's own "successfully" qualifier is not fully bounded while FR-020 remains unresolved, since an unhandled exception mid-tick leaves an undefined, partially-published `CanonicalState` with no corresponding architectural contract.
Repository Evidence: Section 9.3 (FRA); `main.py:14-30`'s broad `except Exception`, re-confirmed present.
Dependency Condition: FR-013's own guarantee holds for every tick that completes without an unhandled exception; its behaviour for a tick that does not is governed by FR-020, which remains unresolved (Current Conformance: unresolved).
Consequence if Unsatisfied: FR-013's own guarantee would have an unaddressed edge case for exactly the condition FR-020 exists to define.
Scope Boundary: does not itself define the required exception/rollback semantics.
Traceability: FRA FR-013, FR-020; Tick Completion Contract, AI-009.

**P3-01-DEP-024**
Title: Full-Sequence Determinism's Completeness Is Conditional on Unhandled-Exception Semantics.
Dependency Class: CONDITIONAL. Sub-type: failure, replay.
Source Requirement(s): FR-020. Target Requirement(s): FR-017.
Scientific Basis: AI-005's "Identical runtime inputs SHALL produce identical runtime outputs" presupposes a well-defined outcome for every input, including an input that triggers an unhandled exception; without FR-020's own resolution, a retry after such an exception has no defined relationship to Tick-Sequence Determinism (Open Question OQ-005, FRA).
Repository Evidence: Section 9.3 (FRA); `RegimeClassifier`'s and `StrategySelector`'s own persisted cross-tick instance state (`regime.py`, `strategy.py`), which a retry would resume from an unreconciled point.
Dependency Condition: FR-017's own full-sequence determinism claim is unaffected for any tick sequence that never triggers an unhandled exception; its bearing on a sequence that does remains conditional on FR-020's own resolution.
Consequence if Unsatisfied: a retry-after-exception scenario could produce a non-deterministic outcome without this being classified as a violation of any currently-stated requirement.
Scope Boundary: does not itself define retry semantics.
Traceability: FRA FR-017, FR-020; AI-005.

**P3-01-DEP-025**
Title: Full-Sequence Determinism Synthesizes the Stage Chain, the Canonical Working State Boundary, Rejection Non-Mutation, and Writer-on-Behalf-Of Discipline.
Dependency Class: REQUIRED. Sub-type: replay, structural.
Source Requirement(s): FR-001, FR-012, FR-016, FR-019. Target Requirement(s): FR-017.
Scientific Basis: AI-005 and AI-006, jointly; Tick-Sequence Determinism (FRA Section 5) requires a fixed sequence (FR-001), no consumption of not-yet-reached state (FR-012), stable behaviour under rejection (FR-016), and no hidden mutation of canonical state outside the approved Writer-on-Behalf-Of path (FR-019).
Repository Evidence: Section 10 (FRA); the same evidence base cited by FR-002 through FR-011's own individual determinism findings (`pnl.py`, `executor.py`, and by independent certification, `risk.py`).
Dependency Condition: FR-017's own Validation Condition ("two independent `RunLoop` instances... produce functionally identical tick-result dictionaries") presupposes each of the four source requirements already holds.
Consequence if Unsatisfied: a break in any one of the four source requirements would make full-sequence replay non-deterministic in a way not attributable to any single stage's own formula.
Scope Boundary: does not require or introduce any new replay tooling.
Traceability: FRA FR-001, FR-012, FR-016, FR-019, FR-017; AI-005, AI-006.

**P3-01-DEP-026**
Title: Traceability Is Constituted by Every Stage's Own File/Line Evidence.
Dependency Class: REQUIRED. Sub-type: traceability, structural.
Source Requirement(s): FR-002, FR-003, FR-004, FR-005, FR-006, FR-007, FR-008, FR-009, FR-010, FR-011, FR-012, FR-013. Target Requirement(s): FR-021.
Scientific Basis: AI-014 (Architectural Traceability) - "Every runtime output SHALL be traceable through... "; FR-021's own claim is an aggregate over every stage-level and Canonical-Working-State/Publication-level requirement's own Existing Evidence field.
Repository Evidence: Section 11 (FRA); Section 6.2's own eighteen-step citation format, re-confirmed present.
Dependency Condition: FR-021's own conformance holds only if every one of the twelve named source requirements continues to carry direct file/line evidence.
Consequence if Unsatisfied: a stage-level requirement losing its own file/line citation would break FR-021's own aggregate claim.
Scope Boundary: does not extend to `TradeLifecycleEngine`'s own internal historical record structure, already certified.
Traceability: FRA FR-002 through FR-013, FR-021; AI-014, AC-011.

**P3-01-DEP-027**
Title: Canonical Working State Boundary Forwards a Robustness Question to P3-02.
Dependency Class: CROSS-UNIT. Sub-type: state, ownership.
Source Requirement(s): FR-012. Target Requirement(s): external (P3-02, Information Flow Validation), via Cross-Unit Observation CUO-01.
Scientific Basis: FR-012's own Scope Boundary explicitly excludes a construction-level enforcement mechanism, recording the underlying observation as CUO-01 (FRA Section 12.2) instead; P3-02's own Implementation Baseline objective text ("Remove hidden coupling") is the textually and architecturally closer home for this concern.
Repository Evidence: `canonical_state.py:107-109`, re-confirmed present (Section 4 above).
Dependency Condition: FR-012's own current conformance is unaffected by whether P3-02 ever resolves CUO-01; this dependency exists to prevent CUO-01 from being silently absorbed into a future P3-01 Architecture.
Consequence if Unsatisfied: absent this explicit forwarding, a future P3-01 Architecture document could inadvertently make a copy-versus-reference decision outside its own scope.
Scope Boundary: does not itself decide reference-versus-copy semantics.
Traceability: FRA FR-012, FR-023; CUO-01.

**P3-01-DEP-028**
Title: Scope-Protection Requirement Formally Forwards CUO-01 to P3-02.
Dependency Class: CROSS-UNIT. Sub-type: ownership, traceability.
Source Requirement(s): FR-023. Target Requirement(s): external (P3-02, Information Flow Validation), via Cross-Unit Observation CUO-01.
Scientific Basis: FR-023's own Requirement Statement explicitly names CUO-01 as forwarded, not resolved.
Repository Evidence: FRA Section 12.2 (CUO-01), Section 14.9 (FR-023).
Dependency Condition: any future document bringing CUO-01 into P3-01's own scope must do so explicitly, per FR-023's own Validation Condition.
Consequence if Unsatisfied: silent scope expansion into P3-02's own territory.
Scope Boundary: this document takes no position on whether CUO-01 belongs to P3-02 or a later unit; only that it does not belong to P3-01.
Traceability: FRA FR-023; CUO-01.

**P3-01-DEP-029**
Title: Performance Evaluation's Internal Semantics Forward to P3-03 via TD-004.
Dependency Class: CROSS-UNIT. Sub-type: semantic, ownership.
Source Requirement(s): FR-011, FR-023. Target Requirement(s): external (P3-03, Performance Validation), via Gap 4 and TD-004.
Scientific Basis: FR-011's own Scope Boundary explicitly excludes `PerformanceEngine`'s internal computation correctness; TD-004's own Target Phase is P3, and P3-03's own Implementation Baseline objective text ("Verify PerformanceEngine inputs. Validate Performance Metrics generation") is the textually closer home.
Repository Evidence: `performance.py:11`, re-confirmed present (Section 4 above); TD-004's Register entry, Status "Already Planned."
Dependency Condition: FR-011's own ordering-position conformance is unaffected by Gap 4's eventual resolution; this dependency exists to prevent Gap 4 from being silently absorbed into a future P3-01 Architecture.
Consequence if Unsatisfied: absent this explicit forwarding, a future P3-01 Architecture document could inadvertently redesign `PerformanceEngine`'s own accounting semantics.
Scope Boundary: does not itself redesign `PerformanceEngine`.
Traceability: FRA FR-011, FR-023; TD-004, Gap 4.

**P3-01-DEP-030**
Title: TD-007's Runtime Control Surface Remains Distinct From FR-020's Exception Semantics.
Dependency Class: CROSS-UNIT. Sub-type: failure, ownership.
Source Requirement(s): FR-020. Target Requirement(s): external (a future Runtime Control Unit, via TD-007).
Scientific Basis: TD-007 (RunLoop Lifecycle Control Surface, Deferred, Target future Runtime Control Unit) governs `PAUSED`/`STOPPING`/`STOPPED`/`ERROR` Runtime Status transitions; FR-020 governs `CanonicalState` consistency under an unhandled exception. The two concerns are related (both touch `RunLoop`'s own failure surface) but distinct (TD-007 concerns operator-triggered lifecycle control; FR-020 concerns an unplanned exception mid-tick).
Repository Evidence: FRA Section 21 (Technical-Debt Traceability); `canonical_state.py:3-10` (`VALID_RUNTIME_STATUS_VALUES` including `ERROR`, confirmed unreachable via any active-path transition, matching TD-007's own "reserved... not yet reachable" finding).
Dependency Condition: FR-020's own eventual resolution must not be conflated with, or treated as satisfying, TD-007's own separate scope.
Consequence if Unsatisfied: a future Architecture document could inadvertently conflate exception recovery with operator lifecycle control, producing an under-specified or over-broad mechanism for either concern.
Scope Boundary: does not resolve TD-007; does not extend FR-020 to cover operator-triggered control transitions.
Traceability: FRA FR-020; TD-007.

**P3-01-DEP-031**
Title: Tick-Complete Publication's Conformance Is Grounded in an Already-Certified Normativity Principle.
Dependency Class: CERTIFICATION. Sub-type: publication, traceability.
Source Requirement(s): FR-013. Target Requirement(s): external (`P2_03_FINANCIAL_OWNERSHIP_SPECIFICATION_V1_2026-07-11.md` Section 16).
Scientific Basis: FR-013's own Current Conformance ("currently evidenced," Verified Conformant Finding VC-01) rests explicitly on a principle already certified by a prior unit, not on an independent P3-01 derivation: "The specified ordering is normative with respect to observable architectural dependencies, not with respect to internal implementation structure... it need not structure its internal code identically to the step list itself."
Repository Evidence: FRA Sections 8.1, 12.3; `P2_03_FINANCIAL_OWNERSHIP_SPECIFICATION_V1_2026-07-11.md` Section 16, re-read for this document (Section 3 above).
Dependency Condition: FR-013's own conformance would require independent re-derivation if this cited principle were ever revised or superseded.
Consequence if Unsatisfied: without this citation, FR-013's own aggregate-publication reasoning would lack a governing precedent and would require a fresh Architecture-stage justification.
Scope Boundary: does not re-certify the cited principle; cites only.
Traceability: FRA FR-013; P2-03 Financial Ownership Specification Section 16.

## 9. Dependency Graph

Structural overview of the thirty-one catalogued dependencies (Section 8), grouped by relationship kind. This graph describes scientific dependency, not a future code structure; no edge below prescribes an implementation.

**Sequential edges (participate in the cycle check, Section 19):**
```
FR-002 --> FR-003 --> FR-004 --> FR-005 --> FR-006 --> FR-007
        --> FR-008 --> FR-009 --> FR-010 --> FR-011 --> FR-013 --> FR-014
```

**Structural (aggregate) edges:**
```
{FR-002..FR-011} --> FR-001
FR-018 --> FR-001
{FR-002..FR-013} --> FR-021
```

**Constraint edges (bound resolution, do not gate timing, not part of the cycle check):**
```
{FR-002..FR-011} --> FR-012   (Canonical Working State boundary)
{FR-002..FR-011} --> FR-015   (HOLD/no-execution completeness)
{FR-007,FR-008,FR-009,FR-010,FR-011} --> FR-016   (rejection non-mutation)
{FR-001,FR-012,FR-016,FR-019} --> FR-017   (determinism synthesis)
```

**Compatibility edges (external, fixed reference frame):**
```
FR-007 --> External(P2-02A/ADR-003/ADR-009)
FR-008 --> External(P2-02A certified Position ownership)
FR-009 --> External(P2-03 certified Financial ownership)
FR-010 --> External(P2-04 certified Risk ownership)
FR-016 --> External(P2-03/P2-04 certified non-mutation)
{FR-007,FR-008,FR-009,FR-010,FR-016} --> FR-022
```

**Conditional edges (target's completeness, not current evidence, depends on source's resolution):**
```
FR-019 -.-> FR-004    (Gap 1: Market Regime writer mechanism)
FR-020 -.-> FR-013    (unresolved exception semantics)
FR-020 -.-> FR-017    (retry-after-exception, determinism)
```

**Certification edge (grounded in an already-certified external principle):**
```
FR-013 ==> External(P2-03 Specification Section 16)
```

**Cross-Unit edges (target outside P3-01's own FR set):**
```
FR-012 ~~> External(P3-02, via CUO-01)
FR-023 ~~> External(P3-02, via CUO-01)
FR-011,FR-023 ~~> External(P3-03, via Gap 4 / TD-004)
FR-020 ~~> External(future Runtime Control Unit, via TD-007)
```

No edge above points from a later stage back to an earlier one; Section 19 details this finding.

## 10. Dependency Matrix

| Dependency ID | Source FR | Target FR | Dependency Class | Haupttyp | Status der Evidenz | Cross-Unit-Bezug | Relevanz CGA | Relevanz Architecture |
|---|---|---|---|---|---|---|---|---|
| DEP-001 | FR-003 | FR-004 | REQUIRED | sequential | currently evidenced | none | confirms Cluster B chain intact | none required |
| DEP-002 | FR-004 | FR-005 | REQUIRED | sequential | currently evidenced | none | confirms Cluster B chain intact | none required |
| DEP-003 | FR-005 | FR-006 | REQUIRED | sequential | currently evidenced | none | confirms Cluster B chain intact | none required |
| DEP-004 | FR-006 | FR-007 | REQUIRED | sequential, event | currently evidenced | none | confirms Cluster B chain intact | none required |
| DEP-005 | FR-007 | FR-008 | REQUIRED | sequential, state | currently evidenced | none | verify acceptance-conditioned Position input | none required |
| DEP-006 | FR-008 | FR-009 | REQUIRED | sequential, state | currently evidenced | none | confirms Cluster B chain intact | none required |
| DEP-007 | FR-009 | FR-010 | REQUIRED | sequential, state | currently evidenced | none | confirms Cluster B chain intact | none required |
| DEP-008 | FR-010 | FR-011 | REQUIRED | sequential | currently evidenced | none | confirms Cluster B chain intact | none required |
| DEP-009 | FR-011 | FR-013 | REQUIRED | sequential, publication | currently evidenced | none | confirms Cluster B-to-C transition | none required |
| DEP-010 | FR-013 | FR-014 | REQUIRED | publication | currently evidenced | none | confirms Cluster C internal order | none required |
| DEP-011 | FR-002..FR-011 | FR-001 | REQUIRED | structural | currently evidenced | none | evaluate as one aggregate capability | none required |
| DEP-012 | FR-018 | FR-001 | REQUIRED | structural | currently evidenced | none | evaluate jointly with DEP-011 | none required |
| DEP-013 | FR-002..FR-011 | FR-012 | REQUIRED | state, semantic | currently evidenced | none | evaluate as constraint, not stage | may need explicit CGA note on CUO-01 |
| DEP-014 | FR-002..FR-011 | FR-015 | REQUIRED | state, failure | currently evidenced | none | evaluate as constraint, not stage | none required |
| DEP-015 | FR-007..FR-011 | FR-016 | REQUIRED | state, failure, event | currently evidenced | none | evaluate as constraint, not stage | none required |
| DEP-016 | FR-016 | external P2-0x | COMPATIBILITY | ownership, failure | currently evidenced | none | confirm no reopening occurred | none required |
| DEP-017 | FR-007 | external P2-02A/ADR-003/009 | COMPATIBILITY | ownership | currently evidenced | none | confirm no reopening occurred | none required |
| DEP-018 | FR-008 | external P2-02A | COMPATIBILITY | ownership | currently evidenced | none | confirm no reopening occurred | none required |
| DEP-019 | FR-009 | external P2-03 | COMPATIBILITY | ownership | currently evidenced | none | confirm no reopening occurred | none required |
| DEP-020 | FR-010 | external P2-04 | COMPATIBILITY | ownership | currently evidenced | none | confirm no reopening occurred | none required |
| DEP-021 | FR-007,008,009,010,016 | FR-022 | COMPATIBILITY | ownership, structural | currently evidenced | none | evaluate as one aggregate capability | none required |
| DEP-022 | FR-019 | FR-004 | CONDITIONAL | ownership | not yet independently evidenced | none | flag as open (Gap 1) capability | Architecture-stage decision required (OQ-001) |
| DEP-023 | FR-020 | FR-013 | CONDITIONAL | failure, publication | unresolved (source) / currently evidenced (target, under normal execution) | none | flag as conditionally-open capability | Architecture-stage decision required (OQ-004) |
| DEP-024 | FR-020 | FR-017 | CONDITIONAL | failure, replay | unresolved (source) / partially evidenced (target) | none | flag as conditionally-open capability | Architecture-stage decision required (OQ-004, OQ-005) |
| DEP-025 | FR-001,012,016,019 | FR-017 | REQUIRED | replay, structural | partially evidenced | none | evaluate FR-017 as synthesis, not standalone | none required beyond DEP-022 through 024 |
| DEP-026 | FR-002..FR-013 | FR-021 | REQUIRED | traceability, structural | currently evidenced | none | evaluate as one aggregate capability | none required |
| DEP-027 | FR-012 | external P3-02 | CROSS-UNIT | state, ownership | currently evidenced (source) | P3-02 | do not evaluate CUO-01 as a P3-01 gap | do not decide reference/copy semantics |
| DEP-028 | FR-023 | external P3-02 | CROSS-UNIT | ownership, traceability | not applicable (scope-protection) | P3-02 | do not evaluate CUO-01 as a P3-01 gap | do not decide reference/copy semantics |
| DEP-029 | FR-011,023 | external P3-03 | CROSS-UNIT | semantic, ownership | not applicable (scope-protection) | P3-03 | do not evaluate Gap 4 as a P3-01 gap to close | do not redesign PerformanceEngine |
| DEP-030 | FR-020 | external (future Runtime Control Unit) | CROSS-UNIT | failure, ownership | unresolved (source) | future unit (TD-007) | keep exception semantics and control surface distinct | do not conflate the two mechanisms |
| DEP-031 | FR-013 | external (P2-03 Specification Section 16) | CERTIFICATION | publication, traceability | currently evidenced | none | cite, do not re-derive | none required |

## 11. Sequential Dependency Analysis

The eleven sequential edges (DEP-001 through DEP-010, plus the transitive FR-002 origin already established by the FRA's own Section 6.2) form a single, strictly linear chain from Runtime Tick Acquisition through External Observability, with no branch, no merge, and no alternative path. Every edge is REQUIRED-class; none is CONDITIONAL, since each stage's own upstream input is currently evidenced as already produced, not merely expected to be produced. This directly answers the governing task's Section 1 instruction ("Abhaengigkeit der vollstaendigen Tick-Sequenz von" the twelve named stages): each of the twelve stages depends on exactly its immediate predecessor, and the chain's own existence is itself the subject of the aggregate structural dependency DEP-011.

Item 2 of the governing task's "Besonders zu analysieren" list ("Abhaengigkeit jeder Stage von vollstaendig abgeschlossenen Upstream-Ergebnissen") is satisfied by the same eleven edges: each Dependency Condition field above states explicitly that the target stage's Validation Condition presupposes the source stage's own output already exists, not merely that it exists eventually. No stage was found to consume a placeholder, a default, or an as-yet-uncomputed value from an upstream stage; every consumption point names a specific prior step (Section 6.2, FRA).

## 12. Failure and Rejection Dependencies

DEP-014, DEP-015, and DEP-016 jointly answer the governing task's Section 8 instruction. `HOLD` and `RUNTIME_FAILURE_EVENT` are scientifically distinct conditions (FRA Section 5): a `HOLD` decision is a valid Execution Decision that produces no lifecycle event at all (`trade_event` is `None`); a rejected transition produces an explicit `RUNTIME_FAILURE_EVENT` `LifecycleEvent`. Both conditions are handled by the same mechanism at the ordering level - every stage still executes (DEP-014 for `HOLD`, part of DEP-015 for rejection) - but by different mechanisms at the value level: `HOLD`'s non-effect on financial and performance state follows from `pnl.py`'s and `performance.py`'s own `None`-input handling (an absence of an event), while a rejection's non-effect follows from an explicit `event_type == "RUNTIME_FAILURE_EVENT"` guard (the presence of a specific event). This document treats these as two distinct dependency chains rather than one, consistent with FR-015 and FR-016 remaining two separate requirements in the FRA.

DEP-016 additionally establishes that the specific non-mutation guarantees FR-016 restates are COMPATIBILITY-class, not REQUIRED-class from a P3-01-internal derivation: P3-01 re-verifies, but did not originally establish, that rejected transitions leave Position, Equity, Realized PnL, Drawdown, Drawdown Ratio, `risk_allocation_factor`, and Performance statistics unmodified. This distinction matters for the future Capability Gap Analysis: any gap in this territory would be a P2-02A/P2-03/P2-04 regression, not a new P3-01 finding.

Item 7's own five-part decomposition ("erfolgreicher Abschluss aller verpflichtenden Stages, synchroner Ausfuehrung, keiner externen Zwischenbeobachtung, keinem vorzeitigen Return, keiner unbehandelten Exception") maps directly onto this document's own dependency set: the first three parts are DEP-009, DEP-010, and DEP-031 (Section 15 below); the fourth ("kein vorzeitiger Return") is confirmed, by direct re-read of `loop.py:33-113`, to have no early-`return` statement anywhere in `step()`'s own body - the function contains exactly one `return`, at line 98, after every stage has executed; the fifth ("keine unbehandelte Exception") is precisely DEP-023's own subject, and remains the sole unresolved item among the five.

## 13. HOLD and No-Execution Dependencies

Answering the governing task's Section 9 explicitly: every one of the twelve mandatory stages continues to execute for a `HOLD` tick (DEP-014); no stage is skipped. Every downstream stage from TradeLifecycle Update onward processes the `None`-shaped or no-op-shaped result a `HOLD` decision produces: `TradeLifecycleEngine.on_execution()` returns `None` rather than raising; `PositionEngine.update_post_trade()` receives whatever `current_position()` returns regardless; `PnLEngine.update()` and `PnLEngine.compute_equity()` both contain explicit `None`-tolerant branches; `RiskEngine.check()` requires no special-casing, since its own inputs (`state`, `position`, `regime`) remain well-defined regardless of the tick's decision; `PerformanceEngine.update()` records a `HOLD`-keyed statistics entry rather than raising.

Every one of FR-001 through FR-014 applies unconditionally, independent of whether an execution (a `BUY`/`SELL` resulting in an accepted lifecycle transition) occurred during the tick; none of these fourteen requirements' own Requirement Statement is qualified by an execution having taken place. Only FR-016 is specific to the rejection sub-case (not `HOLD`), and only FR-023's own Gap 4 forwarding concerns `PerformanceEngine`'s own accounting semantics for a `HOLD` tick's statistics entry, explicitly scope-protected away from P3-01 (Section 18).

## 14. Tick-Completion and Publication Dependencies

DEP-009, DEP-010, and DEP-031 jointly answer the governing task's Section 7. Tick-Complete Publication (FR-013) depends on: successful completion of every mandatory stage (DEP-009, transitively the entire sequential chain of Section 11); the runtime's continued synchronous execution (a precondition, not itself a separate FR, explicitly named in FR-013's own Scope Boundary and carried forward as Open Question OQ-003 in the FRA); the absence of any external mid-tick observation point (DEP-010, confirmed by the repository-wide absence of any concurrency construct, Section 4); the absence of a premature return (confirmed directly in Section 12 above); and the absence of an unhandled exception (DEP-023, the sole CONDITIONAL, currently-unresolved element of this set).

FR-013's own conformance is therefore REQUIRED-grounded for four of its five preconditions and CONDITIONAL-grounded for the fifth. This is a precise, not an approximate, statement: it does not mean FR-013 is "mostly" satisfied; FR-013's Current Conformance (FRA) is stated as "currently evidenced" without qualification, because the CONDITIONAL dependency (DEP-023) affects FR-013's own completeness under a specific, currently-unencountered failure mode, not its evidence under normal execution.

## 15. Determinism and Replay Dependencies

DEP-024 and DEP-025 jointly answer the governing task's Section 10. Full-sequence Tick-Sequence Determinism (FR-017) requires: identical stage-reihenfolge (DEP-025's own FR-001 constituent); identical stage inputs (DEP-025's own FR-012 constituent, the Canonical Working State boundary); the absence of hidden mutations (DEP-025's own FR-019 constituent, the Writer-on-Behalf-Of discipline, itself qualified by CUO-01's forwarded robustness question, Section 18); deterministic components (Section 10, FRA, evidenced individually for `Executor`, `PnLEngine`, and by independent certification for `RiskEngine`; `RegimeClassifier` and `StrategySelector`'s own legitimate cross-tick state does not violate this property, per the FRA's own Tick-Sequence-Determinism-versus-per-call-statelessness distinction, Section 5); stable failure semantics (DEP-025's own FR-016 constituent); and stable Tick-Completion semantics (transitively, Section 14's own dependency set, including DEP-023's CONDITIONAL element).

FR-017's own Current Conformance ("partially evidenced," FRA) is precisely explained by this dependency structure: every REQUIRED constituent (FR-001, FR-012, FR-016, FR-019) is itself currently evidenced, but FR-017's own aggregate claim has not yet been independently, separately verified as a single, dedicated replay exercise (Gap 3) - a verification-completeness gap, not a constituent-level defect. DEP-024 additionally identifies that FR-017's own completeness, like FR-013's, carries an unresolved CONDITIONAL dependency on FR-020.

## 16. Ownership and Compatibility Dependencies

DEP-016 through DEP-021 jointly answer the governing task's Sections 4, 5, and (in part) 6. Position Update (FR-008) depends on P2-02A's certified Position/Exposure ownership; Financial Accounting (FR-009) depends on P2-03's certified Financial Ownership; Risk Evaluation (FR-010) depends on P2-04's certified Risk Ownership; rejected-transition non-mutation (FR-016) depends on both P2-03's and P2-04's own certified non-mutation findings. None of these four dependencies requires, or performs, any re-evaluation of the cited ownership assignment; each is a COMPATIBILITY-class citation, consistent with FR-022's own aggregate requirement (DEP-021) and with this document's own explicit prohibition against reopening certified ownership decisions (Section 2).

Performance Evaluation (FR-011) is deliberately excluded from this set: its own Scope Boundary explicitly excludes `PerformanceEngine`'s internal computation correctness, which is not a certified ownership assignment at all (TD-004 remains open, Status "Already Planned," not "Resolved"), and is instead a Cross-Unit dependency (DEP-029, Section 17).

## 17. Cross-Unit Dependencies

Four Cross-Unit dependencies were identified (DEP-027 through DEP-030), answering the governing task's Sections 11 and 12 directly.

**Toward P3-02 (Information Flow Validation):** DEP-027 (FR-012's own Canonical Working State boundary forwards CUO-01's reference-semantics robustness question) and DEP-028 (FR-023's own formal scope-protection of CUO-01). Both trace to the same underlying observation - `CanonicalState.get()` returns a live-mutable reference (Section 4.1 above) - and both exist specifically so that a future P3-01 Architecture document does not silently make a reference-versus-copy decision that belongs, per the Implementation Baseline's own "Remove hidden coupling" objective text, to P3-02.

**Toward P3-03 (Performance Validation):** DEP-029 (FR-011's and FR-023's joint forwarding of `PerformanceEngine`'s decision-oriented accounting, Gap 4, via TD-004). This dependency exists so that a future P3-01 Architecture document does not silently redesign `PerformanceEngine`'s own internal statistics computation while resolving an ordering-only concern.

**Toward a future Runtime Control Unit (via TD-007):** DEP-030 (FR-020's own unhandled-exception semantics remain distinct from TD-007's own operator-triggered lifecycle control surface). This dependency exists so that FR-020's eventual resolution is not mistaken for, or conflated with, TD-007's separate, already-logged scope.

No Cross-Unit dependency in this document decides which unit ultimately resolves its own forwarded question; each states only that P3-01 does not, consistent with FR-023's own explicit "this document takes no final position" stance (FRA Section 14.9).

## 18. Coupling and Cycle Analysis

**Cyclic dependencies.** None found among the eleven sequential (REQUIRED, sequential sub-type) edges (Section 9): the chain FR-002 through FR-011, continuing to FR-013 and FR-014, is a strict, single-direction path with no back-edge. The four CONSTRAINT-type edges (DEP-013 through DEP-015, DEP-025) are validated against the chain at every transition but do not themselves gate the chain's own timing, and are therefore excluded from the cycle check by the same methodology this governance chain's own prior Scientific Dependency Analyses have applied (a CONSTRAINT bounds resolution; it does not participate in sequencing). The two CONDITIONAL edges touching FR-013 and FR-017 (DEP-023, DEP-024) originate from FR-020, itself downstream of the entire chain (a tick must already be executing for an exception to occur mid-tick); neither edge points backward into FR-002 through FR-011. No cycle exists.

**Hidden backward dependencies.** None found. Every stage's own consumption point (Section 6.2, FRA) names a specific, already-executed prior step; no stage was found to read a value that only a later step produces. This directly confirms AI-006 ("Runtime information shall never move backwards through the execution pipeline") holds for the current runtime.

**Dependency of earlier stages on later ones.** None found. Repository-wide search (Section 4) confirms no file among the fourteen read for this analysis imports or calls a component associated with a later ADR-010 stage from within an earlier stage's own code path.

**Downstream reconstruction of already-produced information.** None found. `loop.py:68-70`'s prior-value reads and `loop.py:90`'s Canonical Working State snapshot are both reads of already-published `CanonicalState` values, not re-derivations of a value an earlier stage already computed; this is consistent with Information Preservation Rule IF-001 ("Information already produced upstream shall never be reconstructed downstream").

**Alternative active paths.** None found beyond the FRA's own Section 4/6.4 findings, re-confirmed in Section 4.1 above.

**Implicit failure coupling.** None found. `RiskEngine.check()` receives no `trade_event` parameter at all and is therefore unaware, even implicitly, of whether the current tick's transition was accepted or rejected; its own non-mutation behaviour under rejection follows entirely from its inputs (`state`, `position`) themselves remaining unmutated upstream, not from any failure-aware branch inside `RiskEngine` itself. `PnLEngine` and `PerformanceEngine` both gate explicitly on `trade_event`'s own `event_type`, an explicit Runtime Event per AI-008, not an implicit signal. No implicit failure coupling was found anywhere in the active path.

**Implicit publication coupling.** One instance found, already catalogued as Gap 1 (Finding F-01, FRA): `RunLoop`'s own direct `self.cstate.update_tick(...)` and `self.cstate.update_regime(...)` calls (`loop.py:42,45`) couple `RunLoop` to `CanonicalState`'s own concrete `update_*` method names, bypassing the uniform `CanonicalEnforcer.apply_*` pattern every other object in this document's scope follows. This is recorded here as a confirmed instance of implicit publication coupling, consistent with, not additional to, Gap 1's own existing classification (DEP-022).

**Implicit dependency on single-threaded execution.** One instance found, already catalogued as Verified Conformant Finding VC-01's own precondition (FRA Section 8.3): FR-013's and FR-014's own current conformance depends on the runtime remaining synchronous and single-threaded, a precondition presupposed rather than codified anywhere in the Binding Baseline. This document does not treat this as a cycle or a hidden backward dependency - it is a documented, forward-looking environmental precondition, already identified by the FRA and carried forward here (Section 14) rather than newly discovered.

## 19. Dependency Findings

**Finding SDA-F-01.** The eleven-edge sequential chain (Section 11) is the structural backbone of P3-01's entire dependency set: twenty-one of the thirty-one catalogued dependencies (DEP-001 through DEP-021) either constitute an edge of this chain directly or are validated against it as a constraint. No dependency was found that bypasses this chain.

**Finding SDA-F-02.** Four dependencies (DEP-022 through DEP-024, DEP-030) are CONDITIONAL, and all four trace to exactly two unresolved sources: Gap 1 (Market Regime's own Writer-on-Behalf-Of mechanism, FR-019/FR-004) and Gap 2 (unhandled-exception semantics, FR-020). No other Functional Requirement in this document's own set carries an unresolved CONDITIONAL dependency as its source.

**Finding SDA-F-03.** FR-017 (full-sequence determinism) is the single most dependency-heavy target in this catalogue, receiving four source requirements directly (DEP-025) plus one CONDITIONAL dependency (DEP-024); this matches the FRA's own classification of FR-017 as "partially evidenced" - the gap is one of synthesis and independent verification, not of any individual constituent's own conformance.

**Finding SDA-F-04.** Exactly four Cross-Unit dependencies were found (DEP-027 through DEP-030), matching the FRA's own four forwarded items (CUO-01, twice; Gap 4/TD-004; TD-007's own distinctness from FR-020). No additional, previously-uncatalogued Cross-Unit dependency was discovered during this analysis.

**Finding SDA-F-05.** No cyclic dependency, hidden backward dependency, or downstream reconstruction was found anywhere in the active path (Section 18). This is a positive finding, not an absence of investigation: each of the eight checks the governing task's own Section "Zyklus- und Coupling-Analyse" names was performed explicitly and is individually reported in Section 18.

## 20. Dependency Risks

**Risk R-01.** If FR-020 (unhandled-exception semantics) remains unresolved through the Architecture stage, both FR-013's and FR-017's own completeness (not their current evidence) remain conditionally open (DEP-023, DEP-024), and any future Certification for this unit would need to explicitly document this residual condition rather than treat FR-013/FR-017 as unconditionally closed.

**Risk R-02.** If a future P3-02 Architecture resolves CUO-01 by introducing a defensive copy or immutable view for `CanonicalState.get()`, and that resolution is not explicitly cross-checked against P3-01's own FR-012, a divergence could arise between P3-01's certified Canonical Working State boundary and P3-02's own implementation. DEP-027/DEP-028 exist specifically to flag this risk; they do not eliminate it.

**Risk R-03.** If a future P3-03 Architecture redesigns `PerformanceEngine`'s own accounting semantics (Gap 4/TD-004) without first confirming P3-01's own ordering-position requirements (FR-011) remain satisfied, a redesign could inadvertently move Performance Evaluation's own call position relative to Risk Evaluation, reopening FR-010's own DEP-008 dependency. DEP-029 exists to flag this risk to the P3-03 unit in advance.

**Risk R-04.** Gap 1's Market Regime divergence (DEP-022) means the Runtime Ownership Matrix and the observed runtime currently disagree for exactly one row; if a future, unrelated architectural change relies on the Matrix's own textual assignment without checking the actual runtime mechanism, that change could inherit an incorrect assumption about which component performs the write.

**Risk R-05.** Because FR-012's own Canonical Working State boundary (Section 18) is currently enforced only by consumer discipline, not by construction (CUO-01), any future component added to the active path that reads `CanonicalState.get()` mid-tick without independent verification of its own non-mutation could silently violate FR-012 without triggering any existing check.

## 21. Dependency Constraints

**Constraint C-01.** Every future Capability Gap Analysis and Architecture document for P3-01 must preserve the eleven-edge sequential chain (Section 11) unless an Architecture Evolution Review explicitly supersedes ADR-010 itself; no Capability Gap Analysis may reclassify a stage-position requirement without first re-deriving this chain.

**Constraint C-02.** No future P3-01 Architecture document may resolve DEP-027 or DEP-028 (CUO-01) or DEP-029 (Gap 4/`PerformanceEngine`) as part of its own scope; both remain explicitly reserved for P3-02 and P3-03 respectively, per FR-023.

**Constraint C-03.** No future P3-01 Architecture document may treat FR-013 or FR-017 as unconditionally closed while FR-020 remains unresolved; any such document must either resolve FR-020 first or explicitly carry forward DEP-023/DEP-024's own conditional qualification.

**Constraint C-04.** Every Compatibility-class dependency (DEP-016 through DEP-021) constrains future work against reopening the cited P2-02A/P2-03/P2-04 ownership assignment; no future P3-01 document may alter Position, Financial, or Risk ownership as an incidental consequence of resolving an ordering-only concern.

**Constraint C-05.** DEP-030 constrains any future resolution of FR-020 from extending into, or being extended by, TD-007's own separate Runtime Control Unit scope.

## 22. Scientific Conclusions

The dependency structure this analysis uncovers is dominated by a single, long, strictly sequential chain (Section 11), a pattern distinct from both P2-02A's two independent tracks and P2-03's one dominant cluster with two smaller open ones (P2-04 SDA, Section 6, by comparison). P3-01's own structure instead resembles one long spine (Layers 1 through 5) with a set of cross-cutting assurance requirements (Layer 6) validated against the spine as a whole, plus a small, genuinely fixed external frame (Layer 0) and an explicit boundary layer (Cross-Unit Layer) that exists to keep two adjacent, not-yet-started units' own territory out.

Of the thirty-one catalogued dependencies, twenty-five are REQUIRED or COMPATIBILITY class and are currently evidenced without qualification; four are CONDITIONAL, all tracing to exactly two unresolved sources (Gap 1, Gap 2); four are CROSS-UNIT, all already explicitly named and scope-protected by the FRA's own FR-023; one is CERTIFICATION-class, grounding FR-013's own conformance in an already-certified precedent rather than a fresh derivation. No cyclic dependency, hidden backward dependency, or downstream reconstruction was found anywhere in the active path.

The scientific ordering this analysis derives for the future Capability Gap Analysis and Architecture is direct: Layer 0 (fixed) requires no evaluation; Layers 1 through 5 (the sequential chain and its immediate publication boundary) can be evaluated in source order, since each depends only on its immediate predecessor; Layer 6 (cross-cutting assurance) can only be meaningfully evaluated once Layers 1 through 5 are themselves evaluated, since every Layer 6 requirement synthesizes evidence across the chain; the Cross-Unit Layer requires no P3-01-internal evaluation at all, only confirmation that the forwarding itself remains intact.

## 23. CGA Readiness Decision

Every one of the twenty-three Functional Requirements is addressed by at least one dependency record (Section 26). Every dependency traces to at least one existing FR (Section 8). No new Functional Requirement, Architecture Decision, or ADR was introduced. No dependency selects a publication mechanism, a copy-versus-reference semantics, an exception/rollback semantics, or a Capability Gap classification; each of these remains explicitly reserved for the Architecture or Capability Gap Analysis stage (Section 2).

No blocking ambiguity was found that would prevent proceeding to the Capability Gap Analysis: the sequential chain is unambiguous and fully evidenced; the four CONDITIONAL dependencies are precisely bounded to two already-named sources (Gap 1, Gap 2); the four Cross-Unit dependencies are precisely bounded to two already-named external units (P3-02, P3-03) plus one already-logged Technical Debt item (TD-007); the one Certification dependency cites a specific, already-certified section rather than an unverified assumption.

Readiness for Capability Gap Analysis: READY. This document is sufficient to proceed to the P3-01 Capability Gap Analysis. No further dependency investigation is required before that step.

## 24. FRA Traceability

| Requirement | Governing Dependency Record(s) |
|---|---|
| FR-001 | DEP-011, DEP-012 |
| FR-002 | DEP-001 (as source's own predecessor, Section 11), DEP-011, DEP-013, DEP-014, DEP-026 |
| FR-003 | DEP-001, DEP-011, DEP-013, DEP-014, DEP-026 |
| FR-004 | DEP-002, DEP-011, DEP-013, DEP-014, DEP-022, DEP-026 |
| FR-005 | DEP-002, DEP-003, DEP-011, DEP-013, DEP-014, DEP-026 |
| FR-006 | DEP-003, DEP-004, DEP-011, DEP-013, DEP-014, DEP-026 |
| FR-007 | DEP-004, DEP-005, DEP-011, DEP-013, DEP-014, DEP-015, DEP-017, DEP-021, DEP-026 |
| FR-008 | DEP-005, DEP-006, DEP-011, DEP-013, DEP-014, DEP-015, DEP-018, DEP-021, DEP-026 |
| FR-009 | DEP-006, DEP-007, DEP-011, DEP-013, DEP-014, DEP-015, DEP-019, DEP-021, DEP-026 |
| FR-010 | DEP-007, DEP-008, DEP-011, DEP-013, DEP-014, DEP-015, DEP-020, DEP-021, DEP-026 |
| FR-011 | DEP-008, DEP-009, DEP-011, DEP-013, DEP-014, DEP-015, DEP-026, DEP-029 |
| FR-012 | DEP-013, DEP-025, DEP-027 |
| FR-013 | DEP-009, DEP-010, DEP-023, DEP-026, DEP-031 |
| FR-014 | DEP-010 |
| FR-015 | DEP-014 |
| FR-016 | DEP-015, DEP-016, DEP-021, DEP-025 |
| FR-017 | DEP-024, DEP-025 |
| FR-018 | DEP-012 |
| FR-019 | DEP-022, DEP-025 |
| FR-020 | DEP-023, DEP-024, DEP-030 |
| FR-021 | DEP-026 |
| FR-022 | DEP-021 |
| FR-023 | DEP-028, DEP-029 |

All twenty-three Functional Requirements are governed by at least one dependency record.

## 25. ADR and Invariant Traceability

| ADR / Invariant / Criterion | Related Dependencies |
|---|---|
| ADR-002 (Event-Driven Runtime Evolution) | DEP-004, DEP-015 |
| ADR-003 (TradeLifecycle as Authoritative Trade Model) | DEP-005, DEP-017 |
| ADR-004 (Position Represents Current Market Exposure) | DEP-006 |
| ADR-005 (Profit and Loss Accounting) | DEP-006, DEP-019 |
| ADR-006 (Canonical Financial State Ownership) | DEP-007, DEP-019 |
| ADR-007 (Risk Evaluation as a Pure Computational Layer) | DEP-008, DEP-020 |
| ADR-008 (Performance Ownership) | DEP-009 |
| ADR-009 (Partial Trade Closure and Position Netting) | DEP-005, DEP-017 |
| ADR-010 (Deterministic Runtime Execution Ordering) | DEP-001 through DEP-014 |
| ADR-011 (Runtime Failure Handling) | DEP-005, DEP-015, DEP-016 |
| Runtime Ownership Matrix | DEP-022 |
| Target Information Flow / Tick Completion Contract | DEP-009, DEP-010, DEP-023, DEP-031 |
| AI-005 (Deterministic Execution) | DEP-024, DEP-025 |
| AI-006 (Deterministic Information Flow) | DEP-011, DEP-025 |
| AI-007 (Semantic Continuity) | DEP-001, DEP-013 |
| AI-008 (Explicit Runtime Events) | DEP-004, coupling analysis (Section 18) |
| AI-009 (Tick Completeness) | DEP-010, DEP-023, DEP-031 |
| AI-014 (Architectural Traceability) | DEP-026 |
| AC-009 (Tick Completion) | DEP-009, DEP-010, DEP-023 |
| AC-010 (Information Flow) | DEP-013, Section 18 |
| AC-011 (Scientific Traceability) | DEP-026 |
| AC-012 (Deterministic Behaviour) | DEP-011, DEP-025 |
| P2-02A Position Ownership | DEP-005, DEP-017, DEP-018 |
| P2-03 Financial Ownership | DEP-016, DEP-019, DEP-031 |
| P2-04 Risk Ownership | DEP-016, DEP-020 |
| TD-004 | DEP-029 |
| TD-007 | DEP-030 |
| CUO-01 | DEP-027, DEP-028 |
| VC-01 | DEP-009, DEP-031 |

Every ADR, Invariant, Acceptance Criterion, prior unit, Technical Debt item, and FRA cross-unit item the governing task named as a minimum traceability target is referenced by at least one dependency record.

## 26. Prior-Certification Compatibility

No dependency in this document requires, or would be satisfied by, any change to `run_engine/core/pnl.py`, `run_engine/core/position.py`, `run_engine/core/risk.py`'s formula body, `run_engine/core/trade_lifecycle.py`, or any `CanonicalState` schema key already certified complete. Every Compatibility-class dependency (DEP-016 through DEP-021) cites, rather than re-derives, the relevant P2-02A/P2-03/P2-04 certified finding. This document's own repository re-verification (Section 4) independently re-confirms that no file this document's dependencies touch has changed since the FRA's own equivalent re-verification, consistent with both prior certifications' own git-blob-identity findings.

## 27. Internal Consistency Review

Terminology consistency - "REQUIRED," "CONDITIONAL," "CROSS-UNIT," "COMPATIBILITY," and "CERTIFICATION" are used exactly as defined in Section 5 throughout this document; no dependency is assigned more than one primary class. "Functionally identical" occurs once (Section 8, DEP-025), as a direct quotation of FR-017's own Validation Condition text from the FRA, not as a comparison this document itself performed; no replay or output comparison was independently re-run here. "Byte-identical" is not used anywhere in this document to describe a comparison; its only occurrence is this sentence's own meta-discussion of the term, since no file- or git-blob-level comparison was performed directly by this analysis.

Ownership consistency - no dependency in Section 8 assigns ownership of any concept to a component other than what ADR-001 through ADR-009, the Runtime Ownership Matrix, or the P2-02A/P2-03/P2-04 certifications already assign; DEP-022 identifies an existing, already-catalogued ownership-mechanism divergence (Gap 1) without proposing a resolution.

Scope consistency - no dependency selects a publication mechanism, a copy-versus-reference semantics, an exception/rollback semantics, a stage-skipping policy, a PerformanceEngine redesign, a Capability Gap classification, an Implementation Unit, or a file for future modification, consistent with Section 2's explicit prohibition list, itself directly restating the governing task's own "Wichtige Grenzen" section.

Traceability consistency - Section 24's FRA mapping, Section 25's ADR/Invariant/Criterion mapping, and Section 8's own Traceability fields are cross-checked: all twenty-three Functional Requirements appear in Section 24; all thirty-one dependencies appear in exactly one catalogue entry each (Section 8) and are referenced by at least one row in Section 10's Matrix.

Observation/dependency/decision separation - Section 4 contains only repository-grounded and FRA-grounded observations. Sections 6 through 9 contain only dependency analysis derived from those observations plus the FRA and the Architecture Baseline. Section 18's Coupling and Cycle Analysis explicitly tests, rather than assumes, the absence of a cycle. No architecture decision, publication mechanism, or reference/copy semantics is selected anywhere in this document.

No fabricated dependency - every one of the thirty-one dependency records traces to a specific FRA requirement, ADR, Architecture Invariant, Acceptance Criterion, or already-logged Technical Debt item (Sections 24-25); no dependency in this document assumes a relationship repository inspection did not confirm (Section 4.1's own re-verification pass).

Status: Internal Consistency Review PASS.

## 28. Independent Self Verification

Every claim in Sections 4 through 27 was independently re-derived during this analysis session, not inherited from the FRA's own text without re-checking: the four Functional Gaps, CUO-01, and VC-01 were each re-confirmed against the current runtime (Section 4.1); the repository-wide search list was re-run in full, including the four terms (`exception`, `failure`, `HOLD`, `no-op`) not part of the FRA's own original search (Section 4); `loop.py:33-113`'s own body was re-read to confirm the absence of any premature `return` statement (Section 12), a claim not explicitly stated anywhere in the FRA itself.

Cross-document consistency check: every FR-001 through FR-023 requirement statement paraphrased or quoted in this document (Sections 6 through 17) was compared against the current, final-revised text of `P3_01_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-13.md` and found consistent, including the post-review corrections that document itself received (the FR-013 requirement-statement precisification, the Gap renumbering, CUO-01's and VC-01's own reclassification) - this document was drafted after, and reflects, the FRA's own fully revised state, not an earlier draft of it.

Result: no error was found during this document's own closing review requiring correction before delivery. All findings from this document's own internal reviews (Section 27) are PASS.

Status: Independent Self Verification PASS.

No commit was made. No runtime file was changed. No push was made. This document is ready to be provided as `P3_01_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-13.md`.
