Document Class:
Architecture Decision Document

Document ID:
P3-01-ARCH

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
docs/architecture/P3_01_DETERMINISTIC_EXECUTION_ORDERING_ARCHITECTURE_V1_2026-07-13.md

Depends On:
- docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md
- docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md
- docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md
- docs/architecture/analysis/P3_01_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-13.md
- docs/architecture/analysis/P3_01_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-13.md
- docs/architecture/analysis/P3_01_CAPABILITY_GAP_ANALYSIS_V1_2026-07-13.md
- docs/architecture/P2_02A_POSITION_OWNERSHIP_ARCHITECTURE_V1_2026-07-10.md
- docs/architecture/P2_03_FINANCIAL_OWNERSHIP_ARCHITECTURE_V1_2026-07-11.md
- docs/architecture/P2_04_RISK_OWNERSHIP_ARCHITECTURE_V1_2026-07-13.md
- docs/architecture/P2_02A_POSITION_OWNERSHIP_SPECIFICATION_V1_2026-07-10.md
- docs/architecture/P2_03_FINANCIAL_OWNERSHIP_SPECIFICATION_V1_2026-07-11.md
- docs/architecture/P2_04_RISK_OWNERSHIP_SPECIFICATION_V1_2026-07-13.md
- docs/architecture/certification/P2_03_FINAL_CERTIFICATION_V1_2026-07-11.md
- docs/architecture/certification/P2_04_FINAL_CERTIFICATION_V1_2026-07-13.md
- current runtime code at HEAD fd22ce130e93261b63830b63600f9e651f7ad496

Referenced By:
- future P3-01 Specification
- future P3-01 Implementation
- future P3-01 Certification

---

# P3-01 Deterministic Execution Ordering Architecture

## 1. Purpose

This document is the P3-01 Architecture. It converts the twenty-three Functional Requirements of `P3_01_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-13.md`, the thirty-one Dependency records of `P3_01_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-13.md`, and the twenty-three Capability classifications of `P3_01_CAPABILITY_GAP_ANALYSIS_V1_2026-07-13.md` into binding architecture decisions. Every remaining P3-01-owned capability gap (CAP-004/CAP-019, CAP-020, CAP-017) is decided explicitly in this document. Cross-Unit Observation CUO-01 and Gap 4 (forwarded via CAP-023) remain explicitly out of scope, ratified as belonging to P3-02 and P3-03 respectively, not resolved here.

This document does not write a Specification. It does not define Python signatures, method bodies, or file diffs. It does not implement code, and it does not build a test suite. Its output is the binding target architecture the Specification stage must translate into an exact implementation contract.

## 2. Scope

In scope: the ten architectural questions the governing task names - the normative runtime-tick sequence, the Market Regime publication path, Tick-Complete Publication semantics, unhandled-exception and partial-publication semantics, HOLD/no-execution ordering, rejection/Runtime Failure Event ordering, full-sequence determinism, stage traceability, alternative execution paths, and Cross-Unit boundaries.

Out of scope, per the FRA (Section 15), the SDA (Section 2), and the CGA (Section 2): strategy logic, regime model, Executor, and lifecycle-semantics redesign; Position, PnL, and Risk formula changes; Performance metric redesign (TD-004, P3-03); Persistence, Recovery, and Schema Evolution (ADR-012, Deferred Scope); parallel or asynchronous execution; a copy-versus-reference decision for `CanonicalState.get()` (CUO-01, P3-02); TD-007's own operator-triggered lifecycle control surface; concrete Python signatures, file diffs, Implementation Units, or tests.

## 3. Binding Inputs

- `docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md` - ADR-002, ADR-010, ADR-011, and by reference ADR-001, ADR-003 through ADR-009, ADR-012; the Runtime Ownership Matrix; the Target Information Flow; Architecture Invariants AI-001 through AI-015 (baseline-level, distinct from this document's own P3-01-AI series); Scientific Acceptance Criteria AC-001 through AC-015.
- `docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md` - the P3-01 unit definition, Principle IP-002, IP-006.
- `docs/architecture/analysis/P3_01_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-13.md` - twenty-three functional requirements, four P3-01-owned Functional Gaps, Cross-Unit Observation CUO-01, Verified Conformant Finding VC-01, as finally revised.
- `docs/architecture/analysis/P3_01_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-13.md` - thirty-one dependencies, nine Requirement/Capability Clusters, seven Dependency Layers, no cyclic dependency found.
- `docs/architecture/analysis/P3_01_CAPABILITY_GAP_ANALYSIS_V1_2026-07-13.md` - twenty-three capabilities, nineteen COMPLETE, three PARTIAL (CAP-004, CAP-017, CAP-019), one MISSING (CAP-020).
- `docs/architecture/P2_02A_POSITION_OWNERSHIP_ARCHITECTURE_V1_2026-07-10.md`, `docs/architecture/P2_03_FINANCIAL_OWNERSHIP_ARCHITECTURE_V1_2026-07-11.md`, `docs/architecture/P2_04_RISK_OWNERSHIP_ARCHITECTURE_V1_2026-07-13.md` and their Specifications - the certified contract baseline this architecture must preserve without exception.
- `docs/architecture/certification/P2_03_FINAL_CERTIFICATION_V1_2026-07-11.md`, `docs/architecture/certification/P2_04_FINAL_CERTIFICATION_V1_2026-07-13.md` - the certified ordering evidence (P2-03's own eighteen-step Runtime Ordering Specification, Section 16) this document independently re-verifies and formally ratifies.
- Current runtime code at HEAD `fd22ce130e93261b63830b63600f9e651f7ad496`, re-traced in Section 4 against the exact `RunLoop.step()` sequence.

## 4. Repository-Grounded Current State

Repository state re-verified: branch `run-engine-consolidation-safety`, local HEAD and remote HEAD both `fd22ce130e93261b63830b63600f9e651f7ad496`, identical. `run_engine/` confirmed clean. This architecture relies on the FRA's, SDA's, and CGA's own repository findings without re-deriving them from the code a second time; the specific facts each Architecture Decision (Section 23) turns on were individually re-confirmed:

- `canonical_enforcer.py`'s ten `apply_*` methods (`apply_position`, `apply_pnl`, `apply_realized_pnl_cumulative`, `apply_equity`, `apply_peak_equity`, `apply_risk`, `apply_strategy_selection`, `apply_execution_decision`, `apply_performance_metrics`, `apply_runtime_status`) - `apply_tick` and `apply_regime` both confirmed absent.
- `loop.py:42,45` - `self.cstate.update_tick(...)` and `self.cstate.update_regime(...)`, both confirmed as direct writes bypassing `CanonicalEnforcer`.
- `main.py:14-30` - the sole `try: ... except Exception as e: print(f"[CRASH] {str(e)}")` handler on the active path, re-confirmed present, unchanged.
- `loop.py:116-131` - the unguarded `__main__` block, re-confirmed present, unchanged.

## 5. Scientific Definitions

These definitions are restated from the FRA (Section 5), not newly invented, and govern the rest of this document.

**Deterministic Runtime Execution Ordering**, **Canonical Working State**, **Tick-Complete Snapshot**, **Tick-Sequence Determinism**, **per-call statelessness**, **Runtime Failure Event**, **Writer-on-Behalf-Of Path** - as defined in the FRA, Section 5.

**Failed Tick** (introduced by this document) - a runtime tick during which an unhandled exception propagates out of `RunLoop.step()` before that method's own `return` statement executes. A Failed Tick is, by construction, never Tick-Complete (Section 12) and never produces a Tick-Complete Snapshot. Distinct from a tick containing a rejected lifecycle transition (`RUNTIME_FAILURE_EVENT`), which does complete all twelve stages and does produce a Tick-Complete Snapshot (Section 17).

**Post-Exception Financial/Lifecycle Divergence** (introduced by this document, Section 18) - the residual condition in which `TradeLifecycleEngine`'s own immutable historical record already reflects a lifecycle transition whose corresponding financial consequence was never published to `CanonicalState`, because an unhandled exception interrupted the same tick between TradeLifecycle Update and Financial Accounting. This document names, but does not resolve, this condition (Section 18).

## 6. Architecture Problem Statement

The CGA found four capabilities open (three PARTIAL, one MISSING), all traceable to exactly two Architecture-stage questions the SDA identified: the Market Regime Writer-on-Behalf-Of mechanism (CAP-004, CAP-019; Open Question OQ-001) and unhandled-exception/partial-publication semantics (CAP-020; Open Question OQ-004), plus one Verification-only gap (CAP-017; Open Question OQ-006) that requires no Architecture Decision to close, only a future dedicated verification exercise this document formally requires. This document exists to resolve OQ-001 and OQ-004, to formally require CAP-017's own closing verification, and to ratify the nineteen already-COMPLETE capabilities as a binding architectural contract, converting the CGA's four open items into a single, internally consistent target architecture.

## 7. Architecture Objectives

1. Ratify the twelve-stage normative execution ordering ADR-010 already establishes, confirming it is normative with respect to observable dependencies, not internal code structure (closing CAP-001 through CAP-003, CAP-005 through CAP-010, CAP-014, CAP-015, CAP-016, CAP-018, CAP-021).
2. Resolve Market Regime's Writer-on-Behalf-Of mechanism (OQ-001), closing CAP-004 and CAP-019.
3. Formally ratify Tick-Complete Publication's own realization (VC-01) as sufficient, and protect its governing precondition with an explicit Architecture Constraint, closing the FRA's own residual Open Question OQ-003.
4. Resolve unhandled-exception and partial-publication semantics (OQ-004), closing CAP-020 - the only MISSING capability in this governance chain's own P3-01 catalogue.
5. Ratify HOLD/no-execution and rejection ordering exactly as currently evidenced (CAP-015, CAP-016).
6. Require a dedicated, independent full-sequence determinism verification (OQ-006), closing CAP-017.
7. Ratify stage traceability (CAP-021) and execution-path exclusivity (CAP-018) exactly as currently evidenced.
8. Formally ratify the Cross-Unit boundary (CAP-023): CUO-01 remains P3-02's; `PerformanceEngine`'s internal semantics and TD-004 remain P3-03's; TD-007 remains a future Runtime Control Unit's.
9. Preserve every already-certified P2-02A/P2-03/P2-04 contract without exception.

## 8. Normative Execution Ordering Model

The runtime executes exactly one, twelve-stage sequence per tick (AD-001): Runtime Tick Acquisition, State Acquisition and Normalization, Regime Classification, Strategy Selection, Execution Decision Generation, Executor Event Generation, TradeLifecycle Update, Position Update, Financial Accounting, Risk Evaluation, Performance Evaluation, Tick-Complete CanonicalState Publication. This ordering is normative with respect to the dependencies, temporal semantics, consumer contracts, and observable results between stages - not with respect to how many internal calls realize a given stage, matching the governing normativity principle `P2_03_FINANCIAL_OWNERSHIP_SPECIFICATION_V1_2026-07-11.md` Section 16 already established and this governance chain has already relied upon for ADR-010 Stage 9 (Financial Accounting, four internal calls) and, per the FRA's own Verified Conformant Finding VC-01, Stage 12 (ten internal calls). An implementation realizing this ordering with a different internal call count than the current eighteen-step trace remains conformant provided the same stage-to-stage dependencies and observable results are preserved.

## 9. Stage Dependency Model

Each of the eleven inter-stage sequential dependencies the SDA catalogued (DEP-001 through DEP-010, transitively DEP-026) remains binding: each stage's own Validation Condition presupposes its immediate predecessor's output already exists, not merely that it will exist. No dependency in this model is newly introduced; this section ratifies the SDA's own eleven-edge chain (`P3_01_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-13.md`, Section 11) as architecturally binding, not merely observed. The four CONSTRAINT-type dependencies the SDA identified (Canonical Working State boundary, HOLD completeness, rejection non-mutation, determinism synthesis) remain validated against this same chain at every transition, per AD-001.

## 10. Canonical Working State Model

Canonical Working State remains consumable only by a component whose own ADR-010 execution position has already been reached in the current tick (AD-001, ratifying FR-012/CAP-012). `RiskEngine.check()` remains the sole mid-tick consumer of a Canonical Working State snapshot, taken after Financial Accounting and before Performance Evaluation, matching ADR-010's Stage 10 position exactly. This model does not decide, and explicitly defers to P3-02, whether `CanonicalState.get()`'s own reference-versus-copy semantics require a construction-level enforcement mechanism (CUO-01, ratified out of scope by AD-010, Section 22).

## 11. Tick-Completion Model

A runtime tick reaches Tick Completion exactly when all twelve mandatory ADR-010 stages have executed to completion within a single, uninterrupted `RunLoop.step()` invocation (AD-003). Tick Completion is realized by the aggregate, cumulative effect of that tick's own incremental `CanonicalEnforcer.apply_*()` calls, not by a single, distinct, dedicated publish action (AD-003, ratifying Verified Conformant Finding VC-01). A tick in which an unhandled exception interrupts `RunLoop.step()` before its own `return` statement executes never reaches Tick Completion (AD-004); such a tick is a Failed Tick (Section 5), architecturally distinct from a tick containing a rejected lifecycle transition, which does reach Tick Completion (Section 17).

## 12. External Observability Model

External downstream consumers observe only Tick-Complete Snapshots (AD-003, ratifying FR-014/CAP-014). This guarantee holds under, and only under, three explicit preconditions this architecture now protects as binding Constraints (Section 25): synchronous tick execution, absence of concurrent or asynchronous stage execution, and absence of any external mid-tick read access to `CanonicalState`. No external consumer observes a Failed Tick's own partial state, since `RunLoop.step()`'s own `return` statement - the sole point at which a Tick-Complete Snapshot becomes available to a caller - never executes for a Failed Tick (AD-004).

## 13. Publication Model

`CanonicalEnforcer` remains the exclusive Writer-on-Behalf-Of publication path for every canonical object this document's scope covers, with exactly two named exceptions, both explicitly ratified, not incidental: Runtime Tick, whose own Runtime Ownership Matrix row explicitly and uniquely names `RunLoop` itself as Writer-on-Behalf-Of (AD-001, unchanged); and, until this architecture's own AD-002 is implemented, Market Regime, whose divergence from the Matrix's general convention this document now resolves (Section 14). Every other canonical object this document's scope covers (Position, Realized PnL, cumulative Realized PnL, Equity, Peak Equity, Risk Metrics, Strategy Selection, Execution Decision, Performance Metrics, Runtime Status) is already, and remains, published exclusively through one of `CanonicalEnforcer`'s ten named `apply_*` methods.

## 14. Market Regime Publication Model

Market Regime's Computational Authority remains `RegimeClassifier` (AD-002, unchanged - `RegimeClassifier.classify()` is the sole component computing the regime value). Market Regime's Authoritative Owner remains `CanonicalState` (AD-002, unchanged). Market Regime's Writer-on-Behalf-Of mechanism changes from `RunLoop`'s own direct `CanonicalState.update_regime()` call to `RunLoop` invoking a new `CanonicalEnforcer.apply_regime()` method, mirroring the shape of `CanonicalEnforcer`'s ten existing `apply_*` methods exactly (AD-002). Market Regime's Primary Consumer remains `StrategySelector` (unchanged). This closes Gap 1 for Market Regime specifically; Runtime Tick's own already-Matrix-conformant `RunLoop`-direct pattern is explicitly not reopened (AD-001, AD-002).

## 15. HOLD and No-Execution Model

A `HOLD` or no-execution tick executes all twelve ADR-010 stages, in the same order as any other tick (AD-005, ratifying FR-015/CAP-015). `TradeLifecycle Update` returns no `LifecycleEvent` (Python `None`) for a `HOLD` action; `Position Update`, `Financial Accounting`, `Risk Evaluation`, and `Performance Evaluation` each already handle this `None` input via an explicit guard, producing a numerically-unchanged, well-formed result. Tick Completion is reachable, and is reached, without any Execution Event having occurred. Determinism and Traceability are preserved because every stage's own `None`-handling behaviour is itself deterministic and already independently evidenced (FRA Section 10).

## 16. Rejection and Runtime Failure Event Model

A tick containing a rejected lifecycle transition executes all twelve ADR-010 stages, in the same order as any other tick, while leaving Position identity fields, Realized PnL, Equity, Peak Equity, cumulative Realized PnL, Drawdown, Drawdown Ratio, `risk_allocation_factor`, and Performance statistics unmodified (AD-006, ratifying FR-016/CAP-016, and the already-certified P2-03/P2-04 non-mutation contracts, not reopened). `TradeLifecycleEngine` generates exactly one immutable `RUNTIME_FAILURE_EVENT` `LifecycleEvent` for the rejected transition; this event becomes part of the immutable lifecycle history (ADR-011, unchanged). Tick Completion is reached for a rejected-transition tick - this is architecturally distinct from a Failed Tick (Section 11), since every one of the twelve stages executes to completion; only specific values are guarded to remain unmutated.

## 17. Unhandled-Exception Model

An unhandled exception propagating out of `RunLoop.step()` produces a Failed Tick (Section 5, AD-004). A Failed Tick SHALL NOT be treated as successful; no Tick-Complete Snapshot SHALL be returned for it; whatever subset of that tick's own `CanonicalEnforcer.apply_*()` calls executed before the exception remain in `CanonicalState`, unmodified by any rollback or reset mechanism, since no such mechanism is architecturally required (AD-004). No `RUNTIME_FAILURE_EVENT` SHALL be generated for a Failed Tick, since a `RUNTIME_FAILURE_EVENT` is, by ADR-002's and ADR-011's own definition, a lifecycle-transition-rejection concept, categorically distinct from an unhandled technical exception (AD-004). The caller of `RunLoop.step()` (currently `main.py`) bears sole responsibility for catching the exception, treating the tick as failed, and continuing to the next tick; `RunLoop`, `CanonicalState`, and `CanonicalEnforcer` bear no special responsibility beyond their own already-defined roles. This model explicitly names, but does not resolve, Post-Exception Financial/Lifecycle Divergence (Section 5, Section 18) as a residual, documented risk.

## 18. Post-Exception Financial/Lifecycle Divergence

If an unhandled exception interrupts `RunLoop.step()` after TradeLifecycle Update (Stage 7) has already recorded an immutable lifecycle event but before Financial Accounting (Stage 9) has published that event's corresponding financial consequence, `CanonicalState`'s own cumulative financial values permanently diverge from `TradeLifecycleEngine`'s own historical record: the next tick's own Financial Accounting computes only its own new event's consequence, from the still-valid prior canonical values, with no mechanism reprocessing the interrupted tick's own already-recorded event. This document names this condition explicitly (AD-004) rather than silently accepting it. A general resolution - reconstructing financial state from `TradeLifecycleEngine`'s own complete history after a failure - would constitute a Recovery mechanism, explicitly Deferred Scope under ADR-012; this architecture does not design one. This finding is recorded as a documented recommendation (Section 27), not a new Technical Debt Register entry, consistent with the governing task's own explicit instruction.

## 19. Determinism Model

Tick-Sequence Determinism (FRA Section 5) requires, jointly: a fixed, single sequence (AD-001); no consumption of not-yet-reached Canonical Working State (Section 10); stable behaviour under rejection (Section 16); and no hidden mutation of canonical state outside the ratified Writer-on-Behalf-Of paths (Section 13, Section 14). Every constituent is currently evidenced (FRA Section 10; SDA DEP-025). Full-sequence determinism, as this unit's own dedicated, independently-certified finding, remains open (AD-007) - the constituent properties are not in question; only their independent, joint verification as a single exercise is required. This model's own completeness is conditionally qualified by Section 17's Failed-Tick semantics: a retry after a Failed Tick is not architecturally guaranteed to be deterministic relative to a run that never failed, since `RegimeClassifier`'s and `StrategySelector`'s own cross-tick instance state is not reconciled by any mechanism this architecture introduces (AD-004, explicitly not extended to cover this case).

## 20. Replay Model

Deterministic replay of the complete twelve-stage sequence requires an identical ordered sequence of tick inputs, from an identical initial `CanonicalState`, to produce an identical ordered sequence of runtime outputs and Tick-Complete Snapshots (AI-005, AI-006). This architecture requires (AD-007) that a future Verification Obligation - not a Runtime Contract, and not an Implementation Unit defined here - independently exercise this property as P3-01's own dedicated finding, distinct from the incidental replay evidence the P2-03 and P2-04 certifications already produced for their own narrower scopes. No new replay tooling is designed by this document.

## 21. Traceability Model

Every one of the twelve ADR-010 stages remains traceable, by file and line, to the specific runtime object it consumes and produces (AD-008, ratifying FR-021/CAP-021). `Runtime Events` (ADR-002), `Canonical Working State` (Section 10), and the `Tick-Complete Snapshot` (Section 11) relate as follows: Runtime Events are the causal record of each stage transition; Canonical Working State is the in-progress accumulation of those transitions' published effects during one tick; the Tick-Complete Snapshot is Canonical Working State's own value at the instant Tick Completion is reached. P3-01's own minimum traceability requirement is file/line evidence per stage, already satisfied; a deeper Information-Flow analysis - tracing semantic continuity, hidden coupling, and reconstruction risk across stage boundaries in full - remains explicitly reserved for P3-02 (AD-010), consistent with that unit's own "Remove hidden coupling" objective text.

## 22. Alternative Execution Path Model

Exactly one active runtime execution path is architecturally permitted: `run_engine/main.py` invoking `RunLoop.step()` (AD-009, ratifying FR-018/CAP-018). `run_engine/core/decision.py`'s `DecisionEngine`, and the four confirmed-inactive directories (`run_engine/runtime/`, `run_engine/execution/`, `run_engine/feedback/`, `run_engine/logging/`), remain classified exactly as the FRA's own Section 4 established - inactive, structurally isolated, and reserved for Phase 6 Repository Consolidation's own future classification (retain/integrate/archive/remove), not decided here. No alternative active path may bypass any of the twelve ADR-010 stages; this constraint is inherited from AD-001, not independently re-derived.

## 23. Cross-Unit Boundary Model

Four items are formally ratified as outside P3-01's own resolution scope (AD-010): Cross-Unit Observation CUO-01 (`CanonicalState.get()`'s reference-versus-copy semantics), remaining P3-02's; `PerformanceEngine`'s internal, decision-oriented accounting semantics (Gap 4) together with TD-004, remaining P3-03's, most plausibly, per TD-004's own Target Phase and P3-03's own Implementation Baseline objective text, though the final P3-02-versus-P3-03 boundary for this specific item is not settled by this document (FRA OQ-007, not resolved here); and TD-007's own operator-triggered Runtime Status control surface, remaining a future Runtime Control Unit's, explicitly distinguished from this document's own AD-004 (Section 17). This architecture proposes no resolution, mechanism, or preference for any of the four.

## 24. Architecture Decisions

### P3-01-AD-001 - Normative Execution Ordering Ratification

**Motivation.** The FRA and SDA independently re-confirmed, by direct trace against the current HEAD, that the current runtime realizes ADR-010's twelve named stages in strictly correct relative order, with no stage skipped, reordered, or duplicated (CAP-001 through CAP-003, CAP-005 through CAP-010, CAP-018, all COMPLETE). No architectural gap exists in the ordering itself; what remains is formal ratification, converting an observed, evidenced fact into a binding architectural contract for this unit's own governance chain.

**Decision.** The twelve-stage sequence ADR-010 defines - Runtime Tick Acquisition, State Acquisition and Normalization, Regime Classification, Strategy Selection, Execution Decision Generation, Executor Event Generation, TradeLifecycle Update, Position Update, Financial Accounting, Risk Evaluation, Performance Evaluation, Tick-Complete CanonicalState Publication - SHALL remain the sole normative runtime tick execution sequence. This ordering is normative with respect to observable dependencies, temporal semantics, and consumer contracts between stages; it is NOT normative with respect to internal code structure. An implementation MAY realize any stage through multiple internal calls, provided the same inter-stage dependencies and the same observable results are preserved, per the governing normativity principle `P2_03_FINANCIAL_OWNERSHIP_SPECIFICATION_V1_2026-07-11.md` Section 16 already established. Exactly one active orchestrator (`RunLoop.step()`) SHALL realize this sequence.

**Scientific Justification.** AI-006 - "Runtime information SHALL propagate through one deterministic execution sequence." The already-certified precedent (P2-03 Specification Section 16) already applies this exact observable-versus-structural distinction to Stage 9; extending it formally to the complete sequence is the minimal, already-evidenced generalization, not a new architectural principle.

**Ownership Consequences.** No change. Every stage's own Computational Authority, Authoritative Owner, and (subject to AD-002) Writer-on-Behalf-Of assignment remains exactly as already certified or as this document separately decides.

**Runtime Consequences.** None. This decision ratifies already-conformant behaviour; no executable code changes as a result of this decision alone.

**Compatibility Constraints.** Preserves the P2-03-certified eighteen-step Runtime Ordering Specification and the P2-04-certified Risk Evaluation position exactly.

**Failure Consequences.** Not applicable to this decision directly; governed by AD-004 through AD-006.

**Determinism Consequences.** Establishes the fixed-sequence constituent of full-sequence Tick-Sequence Determinism (Section 19); AD-007 requires this property's own independent verification.

**Acceptance Criteria.** Exactly one execution sequence exists, matching ADR-010's own twelve stages, verified by fresh trace at any future HEAD; no stage skipped, reordered, or duplicated; no alternative active orchestrator exists.

**Traceability.** FR-001 through FR-011, FR-021; DEP-001 through DEP-014, DEP-026; CAP-001 through CAP-003, CAP-005 through CAP-010, CAP-018, CAP-021.

**Scope Boundary.** Does not itself certify Tick-Complete Publication's own mechanism (AD-003) or full-sequence determinism (AD-007), each separately decided.

---

### P3-01-AD-002 - Market Regime Publication Path

**Motivation.** The FRA's Gap 1 and the CGA's CAP-004/CAP-019 identified that `RunLoop` writes Market Regime directly into `CanonicalState` (`loop.py:45`), bypassing `CanonicalEnforcer`, while the Runtime Ownership Matrix's own "Market Regime" row names `RegimeClassifier` as Writer-on-Behalf-Of - a value that, per this governance chain's own already-established reading (first applied in the P2-04 FRA to the "Risk Metrics" row, and relied upon without exception by every subsequent unit in this chain), is itself superseded in practice by `CanonicalEnforcer`'s uniform role as the actual Writer-on-Behalf-Of for every canonical object except Runtime Tick, whose own Matrix row uniquely and explicitly names `RunLoop` by name rather than following the general CA-naming convention. Market Regime's own row follows the general convention, not the Runtime-Tick-style explicit exception; under the already-established reading, its actual Writer-on-Behalf-Of should therefore be `CanonicalEnforcer`, matching every other CA-naming-convention row's own actual, already-implemented behaviour (Position, Realized PnL, Equity, Peak Equity, Risk Metrics, Strategy Selection, Execution Decision, Performance Metrics all already route through `CanonicalEnforcer` despite their own Matrix rows likewise naming only the CA).

**Decision.** Market Regime's Computational Authority SHALL remain `RegimeClassifier`. Market Regime's Authoritative Owner SHALL remain `CanonicalState`. Market Regime's Writer-on-Behalf-Of mechanism SHALL become `CanonicalEnforcer`, via a new method matching the structural shape of `CanonicalEnforcer`'s ten existing `apply_*` methods exactly (same `None`-guard pattern, same single-key write, same return-the-stored-value shape); `RunLoop`'s own current direct `CanonicalState.update_regime()` call SHALL be replaced by an equivalent call through this new `CanonicalEnforcer` method. Market Regime's Primary Consumer SHALL remain `StrategySelector`. Runtime Tick's own existing, Matrix-conformant `RunLoop`-direct write pattern is explicitly NOT reopened or altered by this decision.

**Scientific Justification.** Rule OM-003 - "Writer-on-Behalf-Of never establishes ownership" - implies a Writer-on-Behalf-Of role is assignable and traceable, not incidental; treating Market Regime identically to every other CA-naming-convention row (all of which already route through `CanonicalEnforcer`) removes the one confirmed outlier without introducing a new principle, consistent with this project's own "no speculation absent governing-document evidence, minimal already-evidenced option" methodology.

**Ownership Consequences.** No Computational Authority or Authoritative Owner changes; only the Writer-on-Behalf-Of mechanism changes, from a direct `RunLoop`-to-`CanonicalState` call to a `RunLoop`-to-`CanonicalEnforcer`-to-`CanonicalState` call, mirroring nine of the ten already-conformant canonical objects.

**Runtime Consequences.** This decision requires an executable runtime code change: one new `CanonicalEnforcer` method, structurally identical to its ten existing methods, and one changed call site in `RunLoop.step()`. This is the sole Architecture Decision in this document requiring an executable code change; every other decision in this document ratifies already-conformant behaviour or a Verification-Only obligation.

**Compatibility Constraints.** `CanonicalState`'s own `"regime"` schema key, default value, and read contract for every existing consumer (`StrategySelector`, and any other future reader) remain unchanged; only the write path changes. No P2-02A, P2-03, or P2-04 contract is affected.

**Failure Consequences.** Not applicable; Market Regime is never subject to rejection or non-mutation guards (it is a Decision-Event-preceding value, not a lifecycle-transition-derived one).

**Determinism Consequences.** None; `RegimeClassifier.classify()`'s own computation and its published value are unchanged; only the mechanism carrying that value into `CanonicalState` changes.

**Acceptance Criteria.** `CanonicalEnforcer` exposes a Market-Regime-publishing method matching its existing ten methods' own shape; `RunLoop.step()` no longer calls `CanonicalState.update_regime()` directly; `CanonicalState`'s own `"regime"` key, default value, and read contract remain unchanged in shape for every existing consumer.

**Traceability.** FR-004, FR-019; DEP-002, DEP-022, DEP-025; CAP-004, CAP-019; Runtime Ownership Matrix ("Market Regime," "Runtime Tick" rows), Rule OM-003.

**Scope Boundary.** Does not reopen Runtime Tick's own already-Matrix-conformant pattern; does not alter `RegimeClassifier`'s own classification algorithm; does not introduce a new canonical schema key.

---

### P3-01-AD-003 - Tick-Complete Publication Realization

**Motivation.** The FRA's Verified Conformant Finding VC-01 established that ADR-010's Stage 12 is realized by the aggregate, cumulative effect of the tick's own ten already-executed `CanonicalEnforcer.apply_*()` calls, not by one distinct, dedicated publish action, and that this realization is conformant under the already-certified P2-03 Specification's own governing normativity principle. The governing task requires this finding be formally ratified, not re-opened as a gap, and requires its own governing precondition (synchronous execution) to be explicitly addressed.

**Decision.** Tick Completion SHALL be defined as the state reached when all twelve mandatory ADR-010 stages have executed to completion within a single, uninterrupted `RunLoop.step()` invocation. Tick-Complete Publication SHALL NOT require a single, atomic, dedicated publish/commit action distinct from the tick's own incremental `CanonicalEnforcer.apply_*()` calls, PROVIDED the three preconditions Constraint C-001 through C-003 (Section 25) name continue to hold: synchronous tick execution, no concurrent or asynchronous stage execution, and no external mid-tick read access to `CanonicalState`. Exactly one Tick-Complete Snapshot SHALL exist per successfully completed tick (P3-01-AI-005). No Tick-Complete Snapshot SHALL exist for a Failed Tick (P3-01-AI-006, AD-004).

**Scientific Justification.** AC-009's and the Tick Completion Contract's own requirement is stated in terms of observable outcome, not internal mechanism; the already-certified P2-03 Specification Section 16 normativity principle, already relied upon for Stage 9, applies identically to Stage 12.

**Ownership Consequences.** None.

**Runtime Consequences.** None. This decision ratifies already-conformant behaviour; the three governing preconditions are newly protected as explicit Constraints (Section 25), a documentation, not a runtime, consequence.

**Compatibility Constraints.** Preserves the existing, unchanged ten-call incremental publication mechanism exactly.

**Failure Consequences.** A Failed Tick (AD-004) never reaches Tick Completion under this definition; this is a direct, intended consequence, not an exception to it.

**Determinism Consequences.** Establishes the Tick-Completion constituent of full-sequence Tick-Sequence Determinism (Section 19).

**Acceptance Criteria.** Every successfully completed tick produces exactly one Tick-Complete Snapshot, verifiable by inspecting `RunLoop.step()`'s own return path; no external caller observes `CanonicalState` mid-tick, verifiable by the continued absence of any concurrency construct in `run_engine/core/`.

**Traceability.** FR-013, FR-014; DEP-009, DEP-010, DEP-023, DEP-026, DEP-031; CAP-013, CAP-014; ADR-010 Stage 12, AI-009, AC-009, Tick Completion Contract, VC-01.

**Scope Boundary.** Does not require or propose an atomic publish/commit mechanism; does not decide any future concurrency model.

---

### P3-01-AD-004 - Unhandled-Exception and Partial-Publication Semantics

**Motivation.** The FRA's Gap 2 and the CGA's CAP-020 - the only MISSING capability in this unit's own catalogue - identified that no governing document defines the runtime's required behaviour when an unhandled exception propagates out of `RunLoop.step()` mid-tick. The governing task requires this question be fully, explicitly decided, without conflating it with ADR-011's own, narrower, already-defined `RUNTIME_FAILURE_EVENT` concept, and without designing Persistence/Recovery (ADR-012, Deferred Scope) or Operator Lifecycle Control (TD-007).

**Decision.** A tick during which an unhandled exception propagates out of `RunLoop.step()` before that method's own `return` statement executes SHALL be classified a Failed Tick (Section 5). A Failed Tick SHALL NOT be considered successful. A Failed Tick SHALL NOT produce a Tick-Complete Snapshot; this guarantee is already structurally satisfied by the current runtime, since Python's own exception-propagation semantics prevent `step()`'s own `return` statement from executing when an exception is raised, and this document formally ratifies that structural guarantee as binding, not incidental. Whatever subset of a Failed Tick's own `CanonicalEnforcer.apply_*()` calls already executed before the exception SHALL remain in `CanonicalState`, unaltered by any automatic rollback or reset mechanism; no such mechanism is architecturally required. No `RUNTIME_FAILURE_EVENT` SHALL be generated for a Failed Tick; a `RUNTIME_FAILURE_EVENT` remains exclusively a lifecycle-transition-rejection concept (ADR-002, ADR-011), categorically distinct from an unhandled technical exception, and SHALL NOT be extended to cover this condition. The caller of `RunLoop.step()` (currently `main.py`) SHALL bear sole responsibility for catching the exception, treating the current tick as failed, and continuing execution with the next tick; this responsibility is not assigned to `RunLoop`, `CanonicalState`, or `CanonicalEnforcer`. Post-Exception Financial/Lifecycle Divergence (Section 18) SHALL be explicitly documented as a residual, named, unresolved risk, not silently accepted; resolving it with a general reconciliation mechanism would constitute Recovery architecture and is explicitly out of this decision's scope.

**Scientific Justification.** The Tick Completion Contract's own "successfully" qualifier, read together with AI-009, already logically entails that an interrupted tick cannot be complete; this decision makes explicit what AI-009 already implies rather than introducing a new principle. The Counterfactual Review performed for this decision (worst case: an exception between TradeLifecycle Update and Financial Accounting) confirmed that no external observability guarantee is violated by the current mechanism, and that any residual internal inconsistency self-heals within at most one subsequent tick for every canonical value except the specific, narrow Post-Exception Financial/Lifecycle Divergence case this decision names explicitly rather than papering over.

**Ownership Consequences.** None. No Authoritative Owner, Computational Authority, or Writer-on-Behalf-Of assignment changes.

**Runtime Consequences.** None. This decision ratifies the current `main.py`-level exception-handling pattern as architecturally sufficient; no executable code change results from this decision alone.

**Compatibility Constraints.** Does not alter any already-certified P2-02A/P2-03/P2-04 non-mutation contract; Post-Exception Financial/Lifecycle Divergence is a distinct, newly-named condition, not a reopening of any certified finding.

**Failure Consequences.** This decision is, in its entirety, a Failure Consequence definition. It explicitly distinguishes a Failed Tick from a rejected-transition tick (Section 16, Section 17): the former never reaches Tick Completion; the latter always does.

**Determinism Consequences.** A retry following a Failed Tick is explicitly not guaranteed deterministic relative to an uninterrupted run, since `RegimeClassifier`'s and `StrategySelector`'s own cross-tick instance state is not reconciled by this decision; this qualification is recorded, not resolved, here (Section 19).

**Acceptance Criteria.** No Tick-Complete Snapshot is ever returned for a tick whose `step()` invocation raised an unhandled exception, verifiable by direct inspection of `RunLoop.step()`'s own control flow; no `RUNTIME_FAILURE_EVENT` is generated for such a tick, verifiable by confirming no code path outside `TradeLifecycleEngine`'s own lifecycle-transition-rejection logic constructs one.

**Traceability.** FR-020; DEP-023, DEP-024, DEP-030; CAP-020; Tick Completion Contract, AI-009, ADR-011 (by contrast), TD-007 (by contrast).

**Scope Boundary.** Does not extend to `main.py`'s own broader process-level error-reporting or logging strategy. Does not design a Persistence or Recovery mechanism (ADR-012). Does not design or extend TD-007's own operator-triggered Runtime Status control surface. Does not resolve Post-Exception Financial/Lifecycle Divergence; names it only.

---

### P3-01-AD-005 - HOLD and No-Execution Ordering Ratification

**Motivation.** The FRA's Section 9.1 and the CGA's CAP-015 (COMPLETE) established, by direct trace, that a `HOLD` tick executes every one of the twelve ADR-010 stages, with no stage skipped. This decision formally ratifies that finding.

**Decision.** A `HOLD` or no-execution tick SHALL execute all twelve ADR-010 stages, in the same order as any other tick. `TradeLifecycle Update` MAY return no `LifecycleEvent` for such a tick. Every downstream stage SHALL produce a well-defined, non-error result for this input. Tick Completion SHALL remain reachable, and SHALL be reached, without any Execution Event having occurred during the tick.

**Scientific Justification.** ADR-010 names no conditional or skippable stage; a `HOLD` decision is itself a valid Execution Decision (ADR-002), not the absence of one.

**Ownership Consequences.** None.

**Runtime Consequences.** None; ratifies already-conformant behaviour.

**Compatibility Constraints.** Preserves every already-certified `None`-input guard in `PnLEngine`, `PerformanceEngine`, and `PositionEngine` exactly.

**Failure Consequences.** Not applicable; `HOLD` is not a failure condition.

**Determinism Consequences.** Confirms `HOLD`'s own deterministic, guard-based handling contributes to, and does not threaten, full-sequence determinism.

**Acceptance Criteria.** A scripted `HOLD`-only tick sequence produces a complete, well-formed tick-result dictionary at every tick, with every financial and risk key numerically unchanged from the prior tick.

**Traceability.** FR-015; DEP-014; CAP-015; ADR-010, ADR-002, Tick Completion Contract.

**Scope Boundary.** Does not evaluate `StrategySelector`'s own cooldown/weighting logic that produces a `HOLD` decision.

---

### P3-01-AD-006 - Rejection and Runtime Failure Event Ordering Ratification

**Motivation.** The FRA's Section 9.2 and the CGA's CAP-016 (COMPLETE) established, by direct trace, that a tick containing a rejected lifecycle transition executes every one of the twelve ADR-010 stages while leaving the ADR-011-named values unmodified. This decision formally ratifies that finding and explicitly distinguishes it from AD-004's own Failed Tick concept.

**Decision.** A tick containing a rejected lifecycle transition (`RUNTIME_FAILURE_EVENT`) SHALL execute all twelve ADR-010 stages, in the same order as any other tick. Position identity fields (Side, Quantity, Average Entry Price), Realized PnL, Equity, Peak Equity, cumulative Realized PnL, Drawdown, Drawdown Ratio, `risk_allocation_factor`, and Performance statistics SHALL remain unmodified across such a tick. Exactly one immutable `RUNTIME_FAILURE_EVENT` SHALL be generated per rejected transition. Tick Completion SHALL be reached for a rejected-transition tick, in every case; this is architecturally distinct from a Failed Tick (AD-004), which never reaches Tick Completion.

**Scientific Justification.** ADR-011, verbatim - "Rejected transitions SHALL never: modify Position, modify Equity, modify Realized PnL... Instead, every rejected transition SHALL generate exactly one immutable Runtime Failure Event."

**Ownership Consequences.** None.

**Runtime Consequences.** None; ratifies already-conformant, already-certified behaviour.

**Compatibility Constraints.** Explicitly preserves, without reopening, the already-certified P2-03 and P2-04 non-mutation findings (`P2_03_FINAL_CERTIFICATION_V1_2026-07-11.md` Section 20, `P2_04_FINAL_CERTIFICATION_V1_2026-07-13.md` Section 17).

**Failure Consequences.** Defines the complete rejected-transition failure model, explicitly distinct from AD-004's unhandled-exception model.

**Determinism Consequences.** Confirms rejection's own deterministic, guard-based handling contributes to, and does not threaten, full-sequence determinism.

**Acceptance Criteria.** A scripted tick sequence including each of the four named rejection reasons produces functionally identical financial, risk, and performance values immediately before and immediately after each failure tick, with every stage still executing and Tick Completion still reached.

**Traceability.** FR-016; DEP-015, DEP-016, DEP-021, DEP-025; CAP-016; ADR-011, AI-011, AC-015.

**Scope Boundary.** Does not re-evaluate the four rejection reasons' own trigger conditions, already certified.

---

### P3-01-AD-007 - Full-Sequence Determinism Verification Obligation

**Motivation.** The CGA's CAP-017 (PARTIAL) found that every individual constituent of full-sequence Tick-Sequence Determinism is currently evidenced, but that the aggregate, full-sequence property has not been independently, separately verified as this unit's own dedicated finding, distinct from the incidental replay evidence the P2-03 and P2-04 certifications already produced for their own narrower scopes.

**Decision.** A future Specification and Implementation stage for this unit SHALL include a dedicated Verification Obligation - not a Runtime Contract, and not a behavior-modifying Implementation Unit - independently exercising complete twelve-stage sequence replay: two independent `RunLoop` instances, each driven through an identical scripted tick sequence from a fresh `CanonicalState`, MUST produce functionally identical tick-result dictionaries and functionally identical final `CanonicalState` snapshots at every tick. This Verification Obligation SHALL be recorded and reported as P3-01's own dedicated finding at Certification time, distinct from, though it may reuse evidence already produced by, P2-03's and P2-04's own certifications.

**Scientific Justification.** AI-005 - "Identical runtime inputs SHALL produce identical runtime outputs" - and AI-006, jointly, require this property; the FRA's own Tick-Sequence Determinism definition (Section 5) requires it be independently exercisable, not merely inferred from adjacent units' incidental evidence.

**Ownership Consequences.** None.

**Runtime Consequences.** None. This decision requires a verification exercise, not a runtime code change.

**Compatibility Constraints.** May reuse, but does not require re-deriving, the scripted sequences P2-03's and P2-04's own certifications already used.

**Failure Consequences.** Not applicable directly; this decision's own Verification Obligation must itself account for AD-004's own Failed-Tick qualification (Section 19) when scoping its scripted sequence.

**Determinism Consequences.** This decision is, in its entirety, a Determinism Consequence: it closes the sole remaining gap in this unit's own determinism evidence.

**Acceptance Criteria.** A dedicated, independently-run replay comparison, distinct from P2-03's and P2-04's own, is performed and reported at Certification time, with a functionally identical result across both runs.

**Traceability.** FR-017; DEP-024, DEP-025; CAP-017; AI-005, AI-006, ADR-010, AC-012.

**Scope Boundary.** Does not require or introduce any new replay tooling design; the mechanism, if any beyond a scripted comparison, is a Specification-stage decision.

---

### P3-01-AD-008 - Stage Traceability Ratification

**Motivation.** The FRA's Section 11 and the CGA's CAP-021 (COMPLETE) established that every one of the twelve ADR-010 stages remains traceable, by file and line, to the specific runtime object it consumes and produces. This decision formally ratifies that finding and explicitly bounds P3-01's own traceability scope against P3-02's deeper Information Flow analysis.

**Decision.** Every one of the twelve ADR-010 stages SHALL remain traceable, by file and line, to the specific runtime object it consumes and the specific runtime object it produces or publishes. This is P3-01's own complete traceability obligation. A deeper Information-Flow analysis - tracing semantic continuity, hidden coupling, and downstream-reconstruction risk across stage boundaries in full generality - is explicitly reserved for P3-02, consistent with that unit's own "Remove hidden coupling. Validate Runtime Tick processing. Validate Market Observation processing" objective text, and is not attempted by this decision.

**Scientific Justification.** AI-014 - "Every runtime output SHALL be traceable through: originating observation, runtime state, execution decision, lifecycle event, financial accounting, risk evaluation, resulting runtime state."

**Ownership Consequences.** None.

**Runtime Consequences.** None; ratifies already-conformant behaviour.

**Compatibility Constraints.** None beyond what AD-001 through AD-006 already establish.

**Failure Consequences.** Not applicable.

**Determinism Consequences.** Traceability is a precondition for, not itself a component of, determinism verification (AD-007).

**Acceptance Criteria.** A fresh trace of `RunLoop.step()` at any future HEAD continues to name, for each stage, the exact line(s) producing and the exact line(s) consuming its associated runtime object.

**Traceability.** FR-021; DEP-026; CAP-021; AI-014, AC-011.

**Scope Boundary.** Does not extend to `TradeLifecycleEngine`'s own internal historical record structure. Does not perform P3-02's own Information Flow analysis.

---

### P3-01-AD-009 - Execution Path Exclusivity Ratification

**Motivation.** The FRA's Section 4/6.4 and the CGA's CAP-018 (COMPLETE) established that exactly one active execution path exists. This decision formally ratifies that finding and confirms the disposition of every confirmed-inactive component.

**Decision.** Exactly one active runtime execution path SHALL exist: `run_engine/main.py` invoking `RunLoop.step()`. `run_engine/core/decision.py`'s `DecisionEngine`, `run_engine/runtime/`, `run_engine/execution/` (top-level), `run_engine/feedback/`, and `run_engine/logging/` SHALL remain classified as confirmed-inactive, reserved for Phase 6 Repository Consolidation's own future retain/integrate/archive/remove decision, not decided here. No alternative active execution path SHALL bypass any of the twelve ADR-010 stages.

**Scientific Justification.** AI-013 (Architectural Minimality) - "Architectural redundancy is prohibited unless scientifically justified"; Architecture Defect AD-007 (Baseline) requires every competing implementation to eventually receive an explicit classification, which this decision defers, not omits.

**Ownership Consequences.** None.

**Runtime Consequences.** None; no inactive component is removed, integrated, or archived by this decision.

**Compatibility Constraints.** None.

**Failure Consequences.** Not applicable.

**Determinism Consequences.** Confirms the sequence-uniqueness constituent of full-sequence determinism (Section 19).

**Acceptance Criteria.** A repository-wide import search from `run_engine/main.py` and `run_engine/core/loop.py` continues to reach exactly the eleven active collaborators already established, with no import edge into any confirmed-inactive component.

**Traceability.** FR-018; DEP-012; CAP-018; AI-013, Architecture Defect AD-007, Phase 6.

**Scope Boundary.** Does not classify or remove any inactive component; classification is Phase 6 Repository Consolidation's own scope.

---

### P3-01-AD-010 - Cross-Unit Boundary Ratification

**Motivation.** The FRA's FR-023, the SDA's DEP-027 through DEP-030, and the CGA's CAP-023 (COMPLETE, Cross-Unit Capability) jointly established four items outside P3-01's own resolution scope. This decision formally ratifies that boundary as binding for this Architecture and any future Specification derived from it.

**Decision.** Cross-Unit Observation CUO-01 (`CanonicalState.get()`'s reference-versus-copy semantics) SHALL remain P3-02's (Information Flow Validation) own resolution scope; no P3-01 Specification or Implementation SHALL introduce a defensive copy, an immutable view, or any other structural enforcement mechanism for `CanonicalState.get()` as a consequence of this Architecture. `PerformanceEngine`'s internal, decision-oriented accounting semantics (Gap 4), together with TD-004, SHALL remain out of P3-01's own resolution scope, most plausibly P3-03's (Performance Validation), though this document does not finally settle the P3-02-versus-P3-03 boundary for this specific item (FRA OQ-007). TD-007's own operator-triggered Runtime Status control surface SHALL remain a future Runtime Control Unit's own scope, explicitly distinguished from AD-004's unhandled-exception semantics. No future P3-01 Specification or Implementation SHALL resolve any of these four items as an incidental consequence of implementing AD-001 through AD-009.

**Scientific Justification.** The Implementation Baseline's own P3-02 ("Remove hidden coupling. Validate Runtime Tick processing. Validate Market Observation processing.") and P3-03 ("Verify PerformanceEngine inputs. Validate Performance Metrics generation.") objective text is, in each case, textually closer to the forwarded item's own substance than P3-01's own "Implement ADR-010 execution sequence. Verify Executor integration. Verify Tick-Complete Snapshot publication."

**Ownership Consequences.** None.

**Runtime Consequences.** None.

**Compatibility Constraints.** None beyond what AD-001 through AD-009 already establish.

**Failure Consequences.** Not applicable.

**Determinism Consequences.** Not applicable.

**Acceptance Criteria.** No future P3-01 Specification or Implementation document introduces a `CanonicalState.get()` copy/reference mechanism, a `PerformanceEngine` internal-semantics change, or an operator-triggered control-surface transition as a consequence of this Architecture.

**Traceability.** FR-023; DEP-027, DEP-028, DEP-029, DEP-030; CAP-023; TD-004, TD-007, CUO-01, Implementation Baseline (P3-01/P3-02/P3-03 unit definitions).

**Scope Boundary.** Proposes no P3-02 or P3-03 solution, mechanism, or preference for any of the four forwarded items.

## 25. Architecture Invariants

**P3-01-AI-001 - Exactly One Active Execution Path.** Exactly one active runtime orchestrator (`RunLoop.step()`) shall exist at any point in this unit's own scope; no competing active orchestrator may be introduced without an Architecture Evolution Review. Established by AD-009.

**P3-01-AI-002 - Fixed Observable Stage Ordering.** The twelve ADR-010 stages shall execute in strictly increasing, unreordered, unduplicated relative order for every tick, observable independent of internal code structure. Established by AD-001.

**P3-01-AI-003 - No Future-Stage Consumption.** No component shall consume a Canonical Working State value corresponding to a stage whose own execution position has not yet been reached in the current tick. Established by AD-001, Section 10.

**P3-01-AI-004 - No External Intermediate Observation.** No external downstream consumer shall observe any runtime state other than a completed tick's own Tick-Complete Snapshot. Established by AD-003.

**P3-01-AI-005 - Exactly One Tick-Complete Result per Successful Tick.** Every tick that reaches Tick Completion shall produce exactly one Tick-Complete Snapshot. Established by AD-003.

**P3-01-AI-006 - No Tick-Complete Result for a Failed Tick.** A tick during which an unhandled exception propagates out of `RunLoop.step()` shall never produce a Tick-Complete Snapshot. Established by AD-004.

**P3-01-AI-007 - Deterministic Full-Sequence Replay.** An identical ordered sequence of tick inputs, from an identical initial `CanonicalState`, shall produce an identical ordered sequence of runtime outputs and Tick-Complete Snapshots, independently verified per AD-007. Established by AD-001, AD-007.

**P3-01-AI-008 - No Hidden Mutable Ordering State.** No stage-ordering decision shall depend on hidden mutable state outside each component's own already-certified, legitimate cross-tick instance state (Tick-Sequence Determinism, distinct from per-call statelessness, FRA Section 5). Established by AD-001.

**P3-01-AI-009 - No Unauthorized Writer-on-Behalf-Of Path.** No runtime component other than `CanonicalEnforcer`'s named `apply_*` methods shall write to `CanonicalState`, except Runtime Tick's own explicitly Matrix-named `RunLoop`-direct exception. Established by AD-002, Section 13.

**P3-01-AI-010 - Certified Ownership Compatibility.** No decision in this document, and no future implementation of it, may alter any P2-02A-certified, P2-03-certified, or P2-04-certified ownership, formula, or non-mutation contract. Established by AD-001 through AD-010, jointly.

**P3-01-AI-011 - HOLD Completeness.** A `HOLD` or no-execution tick shall execute all twelve ADR-010 stages, in order, without exception. Established by AD-005.

**P3-01-AI-012 - Rejection Non-Mutation.** A rejected lifecycle transition shall never mutate Position identity fields, Realized PnL, Equity, Peak Equity, cumulative Realized PnL, Drawdown, Drawdown Ratio, `risk_allocation_factor`, or Performance statistics, while still executing all twelve stages and reaching Tick Completion. Established by AD-006.

Every Architecture Invariant above is directly traceable to one or more ADs in Section 24; no invariant is asserted without a corresponding decision establishing it. None of the twelve invariants above contradicts or redefines any Architecture Baseline-level Invariant (AI-001 through AI-015); each is a P3-01-specific specialization of the general principle the corresponding Baseline Invariant already establishes.

## 26. Architecture Constraints

**Constraint C-001.** Tick execution SHALL remain synchronous and single-threaded within this unit's own current scope; no future Specification or Implementation for this unit may introduce concurrent tick processing without an Architecture Evolution Review. This constraint is the explicit codification of the precondition AD-003 and P3-01-AI-004/AI-005 rely upon (FRA Open Question OQ-003, now resolved: yes, explicitly protected).

**Constraint C-002.** No stage within a single tick may execute in parallel with, or asynchronously relative to, any other stage of the same tick.

**Constraint C-003.** No external component may read `CanonicalState` while `RunLoop.step()` is executing for the current tick.

**Constraint C-004.** No Persistence or Recovery semantics (ADR-012, Deferred Scope) shall be introduced by any future P3-01 Specification or Implementation, including as a resolution to Post-Exception Financial/Lifecycle Divergence (Section 18).

**Constraint C-005.** No Operator Lifecycle Control semantics (TD-007) shall be introduced by any future P3-01 Specification or Implementation, including as a resolution to AD-004's own unhandled-exception semantics.

**Constraint C-006.** No future P3-01 Specification or Implementation shall redefine `PerformanceEngine`'s own internal accounting semantics (Gap 4, TD-004); this remains P3-03's own scope per AD-010.

**Constraint C-007.** No future P3-01 Specification or Implementation shall decide `CanonicalState.get()`'s own copy-versus-reference semantics (CUO-01); this remains P3-02's own scope per AD-010.

## 27. Technical-Debt Disposition

TD-004 (Lifecycle-based Performance Evaluation) remains explicitly out of this unit's own scope, ratified as P3-03's territory by AD-010; this document does not close it, does not partially close it, and does not alter its Register status.

TD-007 (RunLoop Lifecycle Control Surface) remains explicitly out of this unit's own scope, ratified as a future Runtime Control Unit's territory by AD-010; this document explicitly distinguishes it from AD-004's own unhandled-exception semantics (Section 17) and does not conflate the two.

**Recommended Technical Debt Candidate (not registered, no ID assigned, per the governing task's own explicit instruction).** Post-Exception Financial/Lifecycle Divergence (Section 18) is recommended, but not required by this document, as a future Technical Debt Register candidate, for consideration alongside the eventual Persistence/Recovery unit (ADR-012). This document does not modify `ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md`.

## 28. FRA Traceability

| Requirement | Governing Architecture Decision(s) |
|---|---|
| FR-001 | AD-001 |
| FR-002 | AD-001 |
| FR-003 | AD-001 |
| FR-004 | AD-002 |
| FR-005 | AD-001 |
| FR-006 | AD-001 |
| FR-007 | AD-001 |
| FR-008 | AD-001 |
| FR-009 | AD-001 |
| FR-010 | AD-001 |
| FR-011 | AD-001, AD-010 |
| FR-012 | AD-001, AD-010 |
| FR-013 | AD-003 |
| FR-014 | AD-003 |
| FR-015 | AD-005 |
| FR-016 | AD-006 |
| FR-017 | AD-007 |
| FR-018 | AD-009 |
| FR-019 | AD-002 |
| FR-020 | AD-004 |
| FR-021 | AD-008 |
| FR-022 | AD-001 through AD-010, jointly (P3-01-AI-010) |
| FR-023 | AD-010 |

All twenty-three FRA requirements are governed by at least one Architecture Decision.

## 29. SDA Dependency Traceability

Every one of the thirty-one Dependency records is individually resolved by the Architecture Decision governing its own source Functional Requirement (Section 28); no dependency remains without an explicit Architecture-stage disposition.

| Dependency | Disposition |
|---|---|
| DEP-001 | Ratified - AD-001 (sequential chain). |
| DEP-002 | Ratified - AD-001 (sequential chain); Gap 1 aspect closed separately by DEP-022/AD-002. |
| DEP-003 | Ratified - AD-001. |
| DEP-004 | Ratified - AD-001. |
| DEP-005 | Ratified - AD-001. |
| DEP-006 | Ratified - AD-001. |
| DEP-007 | Ratified - AD-001. |
| DEP-008 | Ratified - AD-001. |
| DEP-009 | Ratified - AD-001, AD-003 (Performance Evaluation precedes Tick-Complete Publication). |
| DEP-010 | Ratified - AD-003 (Publication precedes external observability). |
| DEP-011 | Ratified - AD-001 (aggregate sequence-uniqueness). |
| DEP-012 | Ratified - AD-001, AD-009 (execution-path exclusivity). |
| DEP-013 | Ratified - AD-001, Section 10 (Canonical Working State boundary). |
| DEP-014 | Ratified - AD-005 (HOLD completeness). |
| DEP-015 | Ratified - AD-006 (rejection completeness and non-mutation). |
| DEP-016 | Ratified - AD-006 (compatibility with P2-03/P2-04 non-mutation findings, not reopened). |
| DEP-017 | Ratified - AD-001 (compatibility with P2-02A/ADR-003/ADR-009, not reopened). |
| DEP-018 | Ratified - AD-001 (compatibility with P2-02A, not reopened). |
| DEP-019 | Ratified - AD-001 (compatibility with P2-03, not reopened). |
| DEP-020 | Ratified - AD-001 (compatibility with P2-04, not reopened). |
| DEP-021 | Ratified - P3-01-AI-010 (aggregate compatibility, jointly established by AD-001 through AD-010). |
| DEP-022 | Closed - AD-002 (Market Regime Writer-on-Behalf-Of, Gap 1). |
| DEP-023 | Closed - AD-004 (Failed Tick never reaches Tick Completion). |
| DEP-024 | Closed - AD-004, AD-007 (Failed-Tick determinism qualification; dedicated verification required). |
| DEP-025 | Closed - AD-007 (determinism synthesis, Verification Obligation required). |
| DEP-026 | Ratified - AD-008 (stage traceability). |
| DEP-027 | Ratified, not resolved - AD-010 (CUO-01 remains P3-02's). |
| DEP-028 | Ratified, not resolved - AD-010 (CUO-01 forwarding formally confirmed). |
| DEP-029 | Ratified, not resolved - AD-010 (Gap 4/TD-004 remains P3-03's, most plausibly). |
| DEP-030 | Closed - AD-004's own explicit distinction from TD-007, ratified by AD-010. |
| DEP-031 | Ratified - AD-003 (Tick-Complete Publication grounded in the already-certified P2-03 Specification Section 16 principle). |

## 30. CGA Capability Traceability

| Capability | Prior Status | Disposition |
|---|---|---|
| CAP-001 | COMPLETE | Ratified unchanged - AD-001. |
| CAP-002 | COMPLETE | Ratified unchanged - AD-001. |
| CAP-003 | COMPLETE | Ratified unchanged - AD-001. |
| CAP-004 | PARTIAL | Closed - AD-002. |
| CAP-005 | COMPLETE | Ratified unchanged - AD-001. |
| CAP-006 | COMPLETE | Ratified unchanged - AD-001. |
| CAP-007 | COMPLETE | Ratified unchanged - AD-001. |
| CAP-008 | COMPLETE | Ratified unchanged - AD-001. |
| CAP-009 | COMPLETE | Ratified unchanged - AD-001. |
| CAP-010 | COMPLETE | Ratified unchanged - AD-001. |
| CAP-011 | COMPLETE (ordering); Cross-Unit Relevance noted | Ratified - AD-001; Gap 4 forwarding ratified - AD-010. |
| CAP-012 | COMPLETE; Cross-Unit Relevance noted | Ratified - AD-001, Section 10; CUO-01 forwarding ratified - AD-010. |
| CAP-013 | COMPLETE (VC-01) | Ratified, not reopened - AD-003. |
| CAP-014 | COMPLETE | Ratified unchanged - AD-003. |
| CAP-015 | COMPLETE | Ratified unchanged - AD-005. |
| CAP-016 | COMPLETE | Ratified unchanged - AD-006. |
| CAP-017 | PARTIAL | Verification Obligation required - AD-007. |
| CAP-018 | COMPLETE | Ratified unchanged - AD-009. |
| CAP-019 | PARTIAL | Closed jointly with CAP-004 - AD-002. |
| CAP-020 | MISSING | Closed - AD-004. |
| CAP-021 | COMPLETE | Ratified unchanged - AD-008. |
| CAP-022 | COMPLETE | Ratified - AI-010. |
| CAP-023 | COMPLETE (Cross-Unit Capability) | Ratified - AD-010. |

Twenty-two of twenty-three capabilities are ratified unchanged or closed by this Architecture; CAP-017 requires a future Verification Obligation (AD-007), not a further Architecture Decision, to reach COMPLETE.

## 31. Acceptance Criteria

**P3-01-AC-001.** The twelve-stage sequence remains normative with respect to observable dependencies at any future HEAD, independent of internal call count.
**P3-01-AC-002.** Market Regime is published exclusively via `CanonicalEnforcer` after this Architecture's own future Implementation, with Runtime Tick's own pattern unchanged.
**P3-01-AC-003.** No Tick-Complete Snapshot is observed by any external caller before Tick Completion is reached.
**P3-01-AC-004.** No Tick-Complete Snapshot is ever returned for a Failed Tick.
**P3-01-AC-005.** No `RUNTIME_FAILURE_EVENT` is generated for a Failed Tick.
**P3-01-AC-006.** A `HOLD` tick executes all twelve stages without exception.
**P3-01-AC-007.** A rejected-transition tick executes all twelve stages, reaches Tick Completion, and leaves every ADR-011-named value unmutated.
**P3-01-AC-008.** A dedicated, independent full-sequence replay verification is performed and reported at Certification time.
**P3-01-AC-009.** Every stage remains traceable by file and line at any future HEAD.
**P3-01-AC-010.** Exactly one active execution path exists at any future HEAD.
**P3-01-AC-011.** No P3-01 Specification or Implementation resolves CUO-01, Gap 4/TD-004, or TD-007.
**P3-01-AC-012.** No already-certified P2-02A, P2-03, or P2-04 contract is altered by any future P3-01 Specification or Implementation.

## 32. Implementation Impact Inventory

Nine of ten Architecture Decisions (AD-001, AD-003 through AD-010) require no executable runtime code change; each ratifies already-conformant behaviour or establishes a Verification-Only or documentation-only obligation. AD-002 alone requires an executable runtime code change: one new `CanonicalEnforcer` method (structurally identical in shape to its ten existing methods) and one changed call site in `RunLoop.step()` (replacing a direct `CanonicalState.update_regime()` call with the new `CanonicalEnforcer` method call). No other file is implicated. This inventory is a high-level disposition only; exact method signatures, parameter names, and file line ranges are explicitly deferred to the Specification stage, consistent with this document's own prohibition against specifying concrete Python signatures.

## 33. Non-Goals

Consistent with Section 2 and the governing task's own "Wichtige Grenzen": no Python signature, method body, or file diff is specified anywhere in this document; no Implementation Unit is defined; no test is designed; no P3-02 or P3-03 analysis is performed or anticipated beyond the explicit boundary-setting of AD-010; no Persistence or Recovery mechanism is designed (Constraint C-004); no Operator Lifecycle Control mechanism is designed (Constraint C-005); no `PerformanceEngine` redesign is performed (Constraint C-006); no `CanonicalState.get()` copy-versus-reference decision is made (Constraint C-007); no already-certified P2-02A, P2-03, or P2-04 ownership decision is reopened.

## 34. Internal Consistency Review

**Terminology consistency.** "Computational Authority," "Authoritative Owner," "Writer-on-Behalf-Of," "Publication," and "Consumption" are used exactly as defined in the Architecture Baseline throughout this document and are kept strictly separate in every Architecture Decision's own "Ownership Consequences" field; no decision conflates any two of the four. "Failed Tick" and "Post-Exception Financial/Lifecycle Divergence" are used exactly as defined in Section 5 throughout. "Functionally identical" is used exclusively for runtime-object, Python-dictionary, and replay-result comparisons (Sections 20, 24 AD-006/AD-007 Acceptance Criteria). "Byte-identical" is not used anywhere in this document to describe a comparison; its only occurrence is this sentence's own meta-discussion of the term, since no file- or git-blob-level comparison was performed or required by this Architecture. AD-002's own Acceptance Criteria describes `CanonicalState`'s schema-shape preservation in plain terms ("unchanged in shape"), since a schema-key/default/type comparison is a structural comparison, not a byte-sequence one, and does not warrant that term.

**Ownership consistency.** No Architecture Decision in Section 24 introduces a new Authoritative Owner or Computational Authority anywhere in this document; AD-002 changes only a Writer-on-Behalf-Of mechanism, explicitly stated as such in its own "Ownership Consequences" field, satisfying Rule OM-009 (no new Authoritative Owner without an Architecture Evolution Review - none is proposed).

**Scope consistency.** No decision in Section 24 specifies a Python signature, a file diff, an Implementation Unit, or a test. Section 2 confirms strategy, regime, executor, lifecycle-semantics, Position, PnL, Risk, and Performance-formula changes, Persistence/Recovery, Operator Control, and the `CanonicalState.get()` copy/reference question all remain untouched by any decision in this document.

**Ordering consistency.** AD-001's own ratification of the twelve-stage sequence is applied identically in every subsequent Model section (Sections 8 through 23); no section describes a different or competing ordering anywhere in this document.

**Failure-semantics consistency.** AD-004 (Failed Tick) and AD-006 (rejected-transition tick) are kept explicitly, repeatedly distinct throughout Sections 11, 16, 17, and 19; no section conflates the two, and each Model section that discusses failure explicitly cross-references which of the two conditions it addresses.

**Determinism consistency.** Section 19's own four-constituent decomposition (fixed sequence, no future-stage consumption, rejection stability, no hidden mutation) is applied identically wherever full-sequence determinism is discussed (Sections 19, 20, AD-001, AD-007); the Failed-Tick qualification is stated once, precisely, and referenced rather than restated with different wording elsewhere.

**Traceability completeness.** Section 28 confirms all twenty-three FRA requirements; Section 29 confirms all thirty-one SDA dependencies; Section 30 confirms all twenty-three CGA capabilities; cross-checked against Sections 8 through 24 during drafting.

**No fabricated decision.** Every decision in Section 24 traces to a specific FRA requirement, SDA dependency, CGA capability, or Baseline ADR/Invariant/Rule text; no decision in this document addresses a concern absent from the governing baseline or the P3-01 governance chain's own prior documents.

Status: Internal Consistency Review PASS.

## 35. Architecture Readiness Decision

Every Open Question the FRA identified as requiring Architecture-stage resolution has been explicitly decided: OQ-001 (AD-002), OQ-003 (AD-003, Constraint C-001), OQ-004 (AD-004). OQ-006 is not decided here, since its own nature is a Verification Obligation, not an Architecture Decision; AD-007 formally requires it. OQ-005, OQ-007, and OQ-008 remain explicitly and correctly unresolved, consistent with their own SDA/CGA classification as non-blocking or Cross-Unit. All twenty-three FRA requirements, all thirty-one SDA dependencies, and all twenty-three CGA capabilities are traced to at least one Architecture Decision or explicitly confirmed as ratified.

**Architecture Readiness: READY.** This document is sufficient to proceed to the P3-01 Specification. No further architectural investigation, and no additional Open Question resolution, is required before that step.
