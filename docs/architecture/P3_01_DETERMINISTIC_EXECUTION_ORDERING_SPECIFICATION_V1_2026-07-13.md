Document Class:
Specification

Document ID:
P3-01-SPEC

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
docs/architecture/P3_01_DETERMINISTIC_EXECUTION_ORDERING_SPECIFICATION_V1_2026-07-13.md

Depends On:
- docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md
- docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md
- docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md
- docs/architecture/analysis/P3_01_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-13.md
- docs/architecture/analysis/P3_01_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-13.md
- docs/architecture/analysis/P3_01_CAPABILITY_GAP_ANALYSIS_V1_2026-07-13.md
- docs/architecture/P3_01_DETERMINISTIC_EXECUTION_ORDERING_ARCHITECTURE_V1_2026-07-13.md
- docs/architecture/P2_02A_POSITION_OWNERSHIP_SPECIFICATION_V1_2026-07-10.md
- docs/architecture/P2_03_FINANCIAL_OWNERSHIP_SPECIFICATION_V1_2026-07-11.md
- docs/architecture/P2_04_RISK_OWNERSHIP_SPECIFICATION_V1_2026-07-13.md
- docs/architecture/certification/P2_03_FINAL_CERTIFICATION_V1_2026-07-11.md
- docs/architecture/certification/P2_04_FINAL_CERTIFICATION_V1_2026-07-13.md
- current runtime code at HEAD fd22ce130e93261b63830b63600f9e651f7ad496

Referenced By:
- future P3-01 Implementation
- future P3-01 Certification

---

# P3-01 Deterministic Execution Ordering Specification

## 1. Purpose

This document is the P3-01 Specification. It translates the ten Architecture Decisions of `P3_01_DETERMINISTIC_EXECUTION_ORDERING_ARCHITECTURE_V1_2026-07-13.md` into implementable technical directives: Runtime Contracts, Implementation Units, Acceptance Criteria, a No-Change Inventory, and a Runtime Impact statement.

This document does not decide architecture. It does not introduce a new Functional Requirement, Dependency, Architecture Decision, or Architecture Invariant. It does not perform a new scientific analysis or a new capability assessment. It does not specify a concrete Python signature, a complete file diff, or a test implementation. Its output is the binding technical contract a future P3-01 Implementation must satisfy.

## 2. Scope

In scope: Runtime Contracts realizing AD-001 through AD-010; three Implementation Units (IU-001, a file-touching migration; IU-002 and IU-003, Verification-Only); Acceptance Criteria for each IU and globally; a No-Change Inventory naming every runtime file this unit's own scope touches without requiring modification; a Runtime Impact statement naming the one new runtime method this unit's own scope requires, at the functional-responsibility level only.

Out of scope: any new Functional Requirement, Dependency, Architecture Decision, or Architecture Invariant; any new scientific or capability analysis; any concrete Python signature, method body, or file diff; any test implementation; any P3-02 or P3-03 work; any Persistence, Recovery, or Operator Lifecycle Control mechanism; any copy-versus-reference decision for `CanonicalState.get()`; any change to Position, Financial, or Risk formulas or ownership.

## 3. Binding Baseline

- `docs/architecture/P3_01_DETERMINISTIC_EXECUTION_ORDERING_ARCHITECTURE_V1_2026-07-13.md` - the sole source of the ten Architecture Decisions, twelve Architecture Invariants, and seven Architecture Constraints this Specification translates. AD-002 is the sole decision requiring a runtime code change; AD-007 requires a Verification Obligation; the remaining eight decisions are ratifications requiring no runtime change (Implementation Impact Inventory, Architecture Section 32).
- `docs/architecture/analysis/P3_01_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-13.md`, `docs/architecture/analysis/P3_01_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-13.md`, `docs/architecture/analysis/P3_01_CAPABILITY_GAP_ANALYSIS_V1_2026-07-13.md` - the twenty-three Functional Requirements, thirty-one Dependencies, and twenty-three Capabilities this Specification's own Traceability (Section 16) confirms complete coverage of, without re-deriving any of them.
- `docs/architecture/P2_02A_POSITION_OWNERSHIP_SPECIFICATION_V1_2026-07-10.md`, `docs/architecture/P2_03_FINANCIAL_OWNERSHIP_SPECIFICATION_V1_2026-07-11.md`, `docs/architecture/P2_04_RISK_OWNERSHIP_SPECIFICATION_V1_2026-07-13.md` - the certified Specification-level contracts IU-003's own Compatibility Verification (Section 12) checks against, without reopening any of them.
- `docs/architecture/certification/P2_03_FINAL_CERTIFICATION_V1_2026-07-11.md`, `docs/architecture/certification/P2_04_FINAL_CERTIFICATION_V1_2026-07-13.md` - the certified baseline this Specification's own Compatibility Verification treats as immutable.

## 4. Repository Verification

Repository state, verified directly, not assumed:

- Branch: `run-engine-consolidation-safety` (confirmed via `git branch --show-current`).
- Local HEAD: `fd22ce130e93261b63830b63600f9e651f7ad496`, matching the stated expected HEAD exactly.
- Remote HEAD: `fd22ce130e93261b63830b63600f9e651f7ad496`, identical to local HEAD (confirmed via `git fetch` followed by `git rev-parse origin/run-engine-consolidation-safety`).
- Working tree: unchanged from the state the Architecture document itself verified; `run_engine/` confirmed clean.

Files re-read in full for this Specification: `run_engine/core/canonical_enforcer.py` (re-confirmed: ten `apply_*` methods, each following the identical shape - a `None`-guard returning the currently stored value, otherwise an `update_*` call followed by returning the newly stored value; `apply_tick` and `apply_regime` both confirmed absent). `run_engine/core/canonical_state.py:84-86` (`update_regime(self, regime): self.state["regime"] = regime`, confirmed unchanged, confirmed reusable without modification by IU-001). `run_engine/core/regime.py:27` (`classify(self, state)`, confirmed unchanged, confirmed unaffected by AD-002 - only the Writer-on-Behalf-Of mechanism changes, not the Computational Authority). `run_engine/main.py` and `run_engine/core/loop.py` re-confirmed unchanged from the Architecture document's own re-verification (`loop.py:42,45` still the direct-write call sites; `main.py:14-30` still the sole exception handler).

Repository-wide search re-performed for (case-insensitive): `apply_`, `regime`, `CanonicalEnforcer`, `CanonicalState`, `step(`, `Tick-Complete`, `publication`, `deterministic`, `replay`, `failure`. No occurrence was found beyond what the FRA, SDA, CGA, and Architecture already established; no new fact emerged.

## 5. Specification Context

Nine of the ten Architecture Decisions require no runtime code change; this Specification's own Runtime Contracts (Section 6) formalize each as a binding, verifiable statement about already-conformant or newly-ratified behaviour, closing the gap between "the Architecture ratifies this" and "a Verification Obligation confirms it remains true." One Architecture Decision, AD-002, requires an executable runtime code change; this Specification's own Implementation Unit IU-001 (Section 7) is the sole file-touching unit in this document. One Architecture Decision, AD-007, requires a dedicated Verification Obligation, not a Runtime Contract in the ordinary sense; IU-002 (Section 8) carries this obligation. IU-003 (Section 9) verifies that IU-001's own change, once implemented, disturbs no already-certified P2-02A, P2-03, or P2-04 contract.

## 6. Runtime Contracts

Sixteen Runtime Contracts are specified, `P3-01-EO-001` through `P3-01-EO-016`, each traceable to exactly one governing Architecture Decision.

**Contract EO-001 (Fixed Twelve-Stage Sequence).** Requirement: `RunLoop.step()` SHALL realize the twelve ADR-010 stages in strictly increasing, unreordered, unduplicated relative order, per AD-001. Runtime Behaviour: the current eighteen-step call sequence already realizes this; no change required. Acceptance Condition: a fresh trace of `RunLoop.step()` reproduces the same eleven ADR-010-mapped stage boundaries in the same relative order. Verification Method: static re-trace against source line numbers (IU-002). Scope Boundary: normative with respect to observable order only, not internal call count. Traceability: FR-001 through FR-011; DEP-001 through DEP-014, DEP-026; CAP-001 through CAP-003, CAP-005 through CAP-010, CAP-018, CAP-021; AD-001.

**Contract EO-002 (Observable-Versus-Structural Conformance).** Requirement: an implementation realizing a stage through multiple internal calls remains conformant provided the same inter-stage dependencies, temporal semantics, and observable results are preserved, per AD-001, citing `P2_03_FINANCIAL_OWNERSHIP_SPECIFICATION_V1_2026-07-11.md` Section 16. Runtime Behaviour: unchanged; this contract governs interpretation, not code. Acceptance Condition: any future internal restructuring of a stage's own call count does not, by itself, constitute non-conformance. Verification Method: documentation review (IU-002). Scope Boundary: does not license reordering, skipping, or duplicating a stage; only its own internal call count is free. Traceability: FR-001; AD-001.

**Contract EO-003 (Market Regime Writer-on-Behalf-Of Migration).** Requirement: Market Regime's Writer-on-Behalf-Of mechanism SHALL become `CanonicalEnforcer`, per AD-002. Runtime Behaviour: `RunLoop` SHALL invoke a `CanonicalEnforcer`-mediated call to publish the current tick's regime value, rather than calling `CanonicalState.update_regime()` directly. Acceptance Condition: no code path outside `CanonicalEnforcer` writes `CanonicalState`'s own `"regime"` key. Verification Method: static source search for `update_regime` call sites (IU-001, IU-002). Scope Boundary: does not change `RegimeClassifier`'s own Computational Authority role or its own `classify()` computation. Traceability: FR-004, FR-019; DEP-002, DEP-022; CAP-004, CAP-019; AD-002.

**Contract EO-004 (Runtime Tick Exception Preservation).** Requirement: Runtime Tick's own existing, Matrix-conformant `RunLoop`-direct write pattern SHALL remain unchanged, per AD-002. Runtime Behaviour: `RunLoop`'s own direct `CanonicalState.update_tick()` call remains untouched by IU-001. Acceptance Condition: `loop.py`'s own Runtime Tick write call site is unmodified by any IU-001 change. Verification Method: diff inspection (IU-001). Scope Boundary: this contract exists only to confirm AD-002 does not inadvertently extend to Runtime Tick. Traceability: FR-002; DEP-001; CAP-002; AD-002.

**Contract EO-005 (Tick Completion Definition).** Requirement: a runtime tick reaches Tick Completion exactly when all twelve mandatory ADR-010 stages have executed to completion within a single, uninterrupted `RunLoop.step()` invocation, per AD-003. Runtime Behaviour: unchanged; already satisfied by the current sequential call structure. Acceptance Condition: every successfully completed tick has executed all twelve stages before its own tick-result dictionary is assembled. Verification Method: behavioural trace (IU-002). Scope Boundary: does not require a distinct, dedicated publish action. Traceability: FR-013; DEP-009, DEP-010, DEP-026, DEP-031; CAP-013; AD-003.

**Contract EO-006 (Aggregate Publication Sufficiency).** Requirement: Tick-Complete Publication SHALL be realized by the aggregate, cumulative effect of a tick's own incremental `CanonicalEnforcer.apply_*()` calls, without requiring a single, atomic, dedicated publish action, PROVIDED Constraints C-001 through C-003 (Architecture Section 26) continue to hold, per AD-003. Runtime Behaviour: the existing ten (becoming eleven after IU-001) incremental `apply_*` calls remain the sole publication mechanism. Acceptance Condition: no external caller observes `CanonicalState` between the first and last of a tick's own `apply_*` calls. Verification Method: absence-of-concurrency re-confirmation; absence of any external mid-tick read path (IU-002). Scope Boundary: does not require or introduce a staging area, buffer, or commit action. Traceability: FR-013, FR-014; DEP-009, DEP-010, DEP-031; CAP-013, CAP-014; AD-003.

**Contract EO-007 (Failed Tick Classification).** Requirement: a tick during which an unhandled exception propagates out of `RunLoop.step()` before that method's own `return` statement executes SHALL be classified a Failed Tick, per AD-004. Runtime Behaviour: unchanged; Python's own exception-propagation semantics already realize this classification structurally. Acceptance Condition: no Tick-Complete Snapshot is ever returned for a tick whose `step()` invocation raised. Verification Method: simulated-exception behavioural test (IU-002). Scope Boundary: does not require a new marker object, flag, or return value; the classification is behavioural, not a new data structure. Traceability: FR-020; DEP-023, DEP-024, DEP-030; CAP-020; AD-004.

**Contract EO-008 (No Rollback or Reset).** Requirement: no automatic rollback or reset mechanism SHALL be introduced for `CanonicalState` following a Failed Tick, per AD-004. Runtime Behaviour: whatever subset of a Failed Tick's own `apply_*()` calls already executed remains in `CanonicalState`, unaltered. Acceptance Condition: `CanonicalState.reset()`'s own existing behaviour and call sites are unmodified by any P3-01 Implementation. Verification Method: diff inspection confirming `canonical_state.py` is untouched (IU-001, IU-002). Scope Boundary: does not preclude a future, separately-decided Recovery mechanism (Constraint C-004); only forecloses one as part of this unit. Traceability: FR-020; DEP-023; CAP-020; AD-004.

**Contract EO-009 (No Runtime Failure Event for a Failed Tick).** Requirement: no `RUNTIME_FAILURE_EVENT` SHALL be generated as a consequence of an unhandled exception, per AD-004. Runtime Behaviour: `TradeLifecycleEngine`'s own `RUNTIME_FAILURE_EVENT` generation remains scoped exclusively to lifecycle-transition rejection (`trade_lifecycle.py`'s own `_failure_event` method and its four call sites), unmodified. Acceptance Condition: `trade_lifecycle.py` is not modified by any P3-01 Implementation. Verification Method: diff inspection (IU-001, IU-002). Scope Boundary: does not extend or redefine ADR-011's own `RUNTIME_FAILURE_EVENT` concept. Traceability: FR-020; DEP-023, DEP-030; CAP-020; AD-004.

**Contract EO-010 (Caller-Side Failure Responsibility).** Requirement: the caller of `RunLoop.step()` SHALL bear sole responsibility for catching an unhandled exception, treating the current tick as failed, and continuing execution with the next tick, per AD-004. Runtime Behaviour: `main.py`'s own existing `try`/`except Exception`/continue pattern already realizes this responsibility; no change required. Acceptance Condition: `main.py`'s own exception-handling block remains present and unmodified. Verification Method: diff inspection (IU-001, IU-002). Scope Boundary: does not extend to `main.py`'s own broader process-level logging or reporting strategy; does not assign this responsibility to `RunLoop`, `CanonicalState`, or `CanonicalEnforcer`. Traceability: FR-020; DEP-023; CAP-020; AD-004.

**Contract EO-011 (HOLD/No-Execution Stage Completeness).** Requirement: a `HOLD` or no-execution tick SHALL execute all twelve ADR-010 stages, per AD-005. Runtime Behaviour: unchanged; every already-certified `None`-input guard in `PnLEngine`, `PerformanceEngine`, and `PositionEngine` remains untouched. Acceptance Condition: a scripted `HOLD`-only tick sequence produces a complete, well-formed tick-result dictionary at every tick, with every financial and risk key numerically unchanged from the prior tick. Verification Method: scripted behavioural test (IU-002). Scope Boundary: does not evaluate `StrategySelector`'s own cooldown/weighting logic. Traceability: FR-015; DEP-014; CAP-015; AD-005.

**Contract EO-012 (Rejection Stage Completeness and Non-Mutation).** Requirement: a tick containing a rejected lifecycle transition SHALL execute all twelve ADR-010 stages while leaving the ADR-011-named values unmodified, and SHALL reach Tick Completion, per AD-006. Runtime Behaviour: unchanged; every already-certified `RUNTIME_FAILURE_EVENT` guard in `pnl.py` and `performance.py` remains untouched. Acceptance Condition: a scripted tick sequence including each of the four named rejection reasons produces functionally identical financial, risk, and performance values immediately before and immediately after each failure tick, with every stage still executing and Tick Completion reached. Verification Method: scripted behavioural test (IU-002). Scope Boundary: does not re-evaluate the four rejection reasons' own trigger conditions. Traceability: FR-016; DEP-015, DEP-016, DEP-021, DEP-025; CAP-016; AD-006.

**Contract EO-013 (Full-Sequence Determinism Verification Obligation).** Requirement: a dedicated, independent verification of full-sequence Tick-Sequence Determinism SHALL be performed and reported at Certification time, per AD-007. Runtime Behaviour: not applicable; this is a Verification Obligation, not a runtime behaviour requirement. Acceptance Condition: two independent `RunLoop` instances, each driven through an identical scripted tick sequence from a fresh `CanonicalState`, produce functionally identical tick-result dictionaries and functionally identical final `CanonicalState` snapshots at every tick. Verification Method: dual independent replay comparison (IU-002). Scope Boundary: does not require new replay tooling design; may reuse the scripted sequences P2-03's and P2-04's own certifications already used. Traceability: FR-017; DEP-024, DEP-025; CAP-017; AD-007.

**Contract EO-014 (Stage Traceability).** Requirement: every one of the twelve ADR-010 stages SHALL remain traceable, by file and line, to the specific runtime object it consumes and produces, per AD-008. Runtime Behaviour: unchanged; already satisfied. Acceptance Condition: a fresh trace of `RunLoop.step()` continues to name, for each stage, the exact line(s) producing and consuming its associated runtime object. Verification Method: static re-trace (IU-002). Scope Boundary: does not extend to `TradeLifecycleEngine`'s own internal historical record structure; does not perform P3-02's own Information Flow analysis. Traceability: FR-021; DEP-026; CAP-021; AD-008.

**Contract EO-015 (Execution Path Exclusivity).** Requirement: exactly one active runtime execution path SHALL exist, per AD-009. Runtime Behaviour: unchanged; `run_engine/core/decision.py` and the four confirmed-inactive directories remain unimported by the active path. Acceptance Condition: a repository-wide import search from `run_engine/main.py` and `run_engine/core/loop.py` continues to reach exactly the eleven (unchanged in count by IU-001, since `CanonicalEnforcer` is already an active collaborator) active collaborators, with no import edge into any confirmed-inactive component. Verification Method: repository-wide import search (IU-002). Scope Boundary: does not classify or remove any inactive component. Traceability: FR-018; DEP-012; CAP-018; AD-009.

**Contract EO-016 (Cross-Unit Non-Resolution).** Requirement: no P3-01 Implementation SHALL resolve CUO-01, `PerformanceEngine`'s internal semantics (Gap 4/TD-004), or TD-007's own control surface, per AD-010. Runtime Behaviour: `canonical_state.py`'s own `get()` method, `performance.py`'s own internal accounting, and `canonical_state.py`'s own `VALID_RUNTIME_STATUS_VALUES` handling all remain untouched by this Specification's own Implementation Units. Acceptance Condition: no P3-01 Implementation introduces a `CanonicalState.get()` copy/reference mechanism, a `PerformanceEngine` internal-semantics change, or an operator-triggered control-surface transition. Verification Method: diff inspection confirming `canonical_state.py`'s own `get()` method and `performance.py` are both untouched (IU-001, IU-003). Scope Boundary: proposes no P3-02 or P3-03 solution. Traceability: FR-023; DEP-027 through DEP-030; CAP-023; AD-010.

## 7. IU-001 - Market Regime Publication Migration

**Goal.** Migrate Market Regime's publication path from a direct `RunLoop`-to-`CanonicalState` write to a `RunLoop`-to-`CanonicalEnforcer`-to-`CanonicalState` write, realizing AD-002/Contracts EO-003, EO-004.

**Affected Runtime Files.** `run_engine/core/canonical_enforcer.py` (gains one new method); `run_engine/core/loop.py` (one call site changes).

**Not Affected.** Every other runtime file in `run_engine/core/`, `run_engine/main.py`, and every confirmed-inactive file; see Section 13 (No-Change Inventory) for the complete, individually justified list.

**Functional Responsibility of the New Method (no concrete Python signature specified).** `CanonicalEnforcer` gains exactly one new method whose functional responsibility mirrors its ten existing `apply_*` methods exactly: it accepts a regime value; if that value is not absent, it writes the value into `CanonicalState` via the already-existing `update_regime()` method and returns the newly stored value; if the value is absent, it returns the currently stored value without writing. This method introduces no new computation, no new validation beyond what its ten siblings already perform, and no new canonical schema key.

**RunLoop's Sole Functional Change.** `RunLoop.step()`'s own direct `CanonicalState.update_regime()` call is replaced by an equivalent call routed through `CanonicalEnforcer`'s new method. No other line in `RunLoop.step()` changes as a consequence of this Implementation Unit. Runtime Tick's own direct-write call site (`CanonicalState.update_tick()`) remains untouched (Contract EO-004).

**Preconditions.** None beyond the current, already-verified repository state (Section 4).

**Acceptance Criteria (IU-001).**
- **P3-01-SPEC-AC-001.** `CanonicalEnforcer` exposes exactly eleven `apply_*`-shaped methods after this Implementation Unit, the ten existing ones unchanged plus the one new Market-Regime-publishing method.
- **P3-01-SPEC-AC-002.** No code path outside the new method writes `CanonicalState`'s own `"regime"` key.
- **P3-01-SPEC-AC-003.** `CanonicalState`'s own `"regime"` schema key, default value (`"UNKNOWN"`), and read contract for every existing consumer remain unchanged in shape.
- **P3-01-SPEC-AC-004.** `RunLoop.step()`'s own Runtime Tick write call site (`CanonicalState.update_tick()`) is byte-identical to its pre-Implementation state (a genuine source-line comparison).
- **P3-01-SPEC-AC-005.** `python -m compileall run_engine` PASSes after this Implementation Unit.

**Testumfang.** `compileall`; import test confirming `CanonicalEnforcer` and `RunLoop` both import without error; Stage Ordering re-trace confirming Regime Classification's own relative position in the twelve-stage sequence is unchanged; Market Regime Publication test confirming the new method is invoked exactly once per tick, at the same relative position the direct write previously occupied; Writer-on-Behalf-Of test confirming no other code path writes `CanonicalState`'s own `"regime"` key; `CanonicalEnforcer` unit-level test confirming the new method's own `None`-guard and stored-value-return behaviour matches its ten siblings'; full regression re-run of the already-certified P2-02A/P2-03/P2-04 scenarios confirming every already-certified field remains functionally identical.

## 8. IU-002 - Execution Ordering Behavioral Verification

**Goal.** Independently verify, with no runtime code change, that the execution-ordering behaviour AD-001, AD-003 through AD-007, and AD-009 ratify remains true after IU-001 has landed.

**Runtime Code Change.** None. This is a Verification-Only Implementation Unit.

**Verification Scope (minimum, per the governing task).** Stage Ordering (Contract EO-001, EO-002); Tick Completion (EO-005, EO-006); HOLD (EO-011); Rejection (EO-012); Runtime Failure Event (EO-009, EO-012); Failed Tick (EO-007, EO-008, EO-010); Determinism (EO-013); Replay (EO-013); Alternative Execution Paths (EO-015).

**Acceptance Criteria (IU-002).**
- **P3-01-SPEC-AC-006.** A fresh trace of `RunLoop.step()` reproduces the same twelve-stage relative order as the Architecture's own Section 4 re-verification, with Regime Classification's own new writer mechanism (IU-001) not altering its ordering position.
- **P3-01-SPEC-AC-007.** A scripted `HOLD`-only tick sequence produces a complete, well-formed tick-result dictionary at every tick, with every financial and risk key numerically unchanged from the prior tick.
- **P3-01-SPEC-AC-008.** A scripted tick sequence including each of the four named rejection reasons produces functionally identical financial, risk, and performance values immediately before and immediately after each failure tick, with Tick Completion reached in every case.
- **P3-01-SPEC-AC-009.** A simulated unhandled exception, injected at each of several distinct points within `RunLoop.step()`'s own body, in each case produces no Tick-Complete Snapshot and no `RUNTIME_FAILURE_EVENT`.
- **P3-01-SPEC-AC-010.** Two independent `RunLoop` instances, driven through an identical scripted tick sequence from a fresh `CanonicalState`, produce functionally identical tick-result dictionaries and functionally identical final `CanonicalState` snapshots at every tick.
- **P3-01-SPEC-AC-011.** A repository-wide import search from `run_engine/main.py` and `run_engine/core/loop.py` reaches exactly the same set of active collaborators as before IU-001, with no import edge into any confirmed-inactive component.

**Testumfang.** Replay (dual independent scripted-sequence comparison); Determinism (per-component and full-sequence); HOLD (scripted no-execution sequence); Failed Tick (simulated exception injection at multiple points); Runtime Failure Event (scripted rejection sequence, confirmed absent for the Failed-Tick case); Alternative Execution Path (repository-wide import search); Tick Completion (behavioural trace confirming exactly one Tick-Complete Snapshot per successfully completed tick and none for a Failed Tick).

## 9. IU-003 - Compatibility Verification

**Goal.** Independently verify, with no runtime code change, that IU-001's own migration disturbs no already-certified P2-02A, P2-03, or P2-04 contract, and that the Cross-Unit boundary (AD-010) remains intact.

**Runtime Code Change.** None. This is a Verification-Only Implementation Unit.

**Verification Scope (minimum, per the governing task).** P2-02A, P2-03, P2-04 (compatibility, not reopened); Ownership (Runtime Ownership Matrix, Rule OM-003, Rule OM-006); Architecture Invariants (this unit's own P3-01-AI-001 through AI-012, and by reference the Baseline's own AI-series); Acceptance Criteria (AC-009 through AC-012, and this unit's own P3-01-AC-series); TD-004; TD-007; CUO-01; VC-01.

**Acceptance Criteria (IU-003).**
- **P3-01-SPEC-AC-012.** Full regression re-run of the P2-02A/P2-03/P2-04 certified scenarios, after IU-001's own implementation, produces functionally identical results for every already-certified field.
- **P3-01-SPEC-AC-013.** `run_engine/core/pnl.py`, `run_engine/core/position.py`, `run_engine/core/risk.py`, `run_engine/core/trade_lifecycle.py`, and `run_engine/core/performance.py` are each confirmed git-blob-identical to their pre-IU-001 state.
- **P3-01-SPEC-AC-014.** `run_engine/core/canonical_state.py` is confirmed git-blob-identical to its pre-IU-001 state (only `canonical_enforcer.py` and `loop.py` change, per IU-001's own scope).
- **P3-01-SPEC-AC-015.** TD-004 and TD-007 remain unaddressed by this unit, confirmed by the absence of any change to `performance.py` (TD-004) or to `canonical_state.py`'s own `VALID_RUNTIME_STATUS_VALUES` handling (TD-007).
- **P3-01-SPEC-AC-016.** CUO-01 remains unaddressed, confirmed by `canonical_state.py`'s own `get()` method remaining git-blob-identical to its pre-IU-001 state.
- **P3-01-SPEC-AC-017.** VC-01 remains valid after IU-001, confirmed by the tick's own Publication mechanism still consisting of an aggregate of incremental `CanonicalEnforcer.apply_*()` calls (now eleven, not ten), with no atomic publish/commit action introduced.

**Testumfang.** Compatibility (full P2-02A/P2-03/P2-04 regression re-run); Ownership (confirmation that Market Regime's Computational Authority and Authoritative Owner are unchanged, only the Writer-on-Behalf-Of mechanism); Architecture Invariant re-check (all twelve P3-01-AI-series invariants, plus the Baseline's own relevant AI-series); Acceptance Criteria re-check (all twelve Architecture-level P3-01-AC-series criteria); TD-004/TD-007 non-reopening confirmation; CUO-01 non-resolution confirmation; VC-01 continued-validity confirmation.

## 10. Acceptance Criteria

Seventeen Specification-level Acceptance Criteria are defined (`P3-01-SPEC-AC-001` through `P3-01-SPEC-AC-017`, Sections 7 through 9). In addition, the following global criteria apply across all three Implementation Units:

**P3-01-SPEC-AC-G1.** `python -m compileall run_engine` PASSes after every Implementation Unit.
**P3-01-SPEC-AC-G2.** `git diff --check` reports no new finding beyond the already-documented, pre-existing CRLF-blob artifact this governance chain has repeatedly confirmed for `run_engine/core/*.py`.
**P3-01-SPEC-AC-G3.** Exactly two runtime files (`canonical_enforcer.py`, `loop.py`) show any diff after IU-001; every other runtime file remains git-blob-identical to its pre-Implementation state.
**P3-01-SPEC-AC-G4.** No Implementation Unit in this document introduces a new canonical schema key, a new Runtime Event type, or a new Authoritative Owner.

## 11. Runtime Verification

This section states the detailed verification procedure IU-002 (Section 8) carries out, organized by the governing task's own nine-item minimum checklist.

**Stage Ordering.** Re-trace `RunLoop.step()`'s own source line by line; confirm the twelve ADR-010 stages remain in strictly increasing relative order; confirm Regime Classification's own new writer-mechanism call (IU-001) occupies the identical relative position the direct write previously occupied.

**Tick Completion.** Confirm every successfully completed tick executes all twelve stages before its own tick-result dictionary is assembled; confirm no code path returns a tick-result dictionary before all eleven (post-IU-001) `CanonicalEnforcer.apply_*()` calls have executed.

**HOLD.** Run a scripted sequence of `HOLD`-only ticks; confirm every stage executes; confirm every financial and risk key remains numerically unchanged tick over tick.

**Rejection.** Run a scripted sequence including each of the four named rejection reasons; confirm every stage executes; confirm the ADR-011-named values remain unmutated; confirm Tick Completion is reached in every case.

**Runtime Failure Event.** Confirm exactly one `RUNTIME_FAILURE_EVENT` is generated per rejected transition; confirm zero `RUNTIME_FAILURE_EVENT`s are generated for a simulated unhandled exception (Failed Tick).

**Failed Tick.** Inject a simulated exception at several distinct points within a scripted `RunLoop.step()` invocation (for example, immediately after Position Update, immediately after Financial Accounting); confirm no Tick-Complete Snapshot is returned in any case; confirm `CanonicalState` retains whichever subset of that tick's own `apply_*` calls executed before the injected exception, unaltered by any rollback.

**Determinismus (Determinism).** Confirm each individually-deterministic component (`Executor`, `PnLEngine`, and, by independent citation, `RiskEngine`) remains so after IU-001; confirm the new Market-Regime-publishing method is itself a pure function of its own explicit input, holding no instance state.

**Replay.** Run two independent `RunLoop` instances through an identical scripted tick sequence from a fresh `CanonicalState`; compare tick-result dictionaries and final `CanonicalState` snapshots for functional identity at every tick.

**Alternative Execution Paths.** Re-run the repository-wide import search from `run_engine/main.py` and `run_engine/core/loop.py`; confirm the same active-collaborator set as before IU-001; confirm no import edge into `run_engine/core/decision.py`, `run_engine/runtime/`, `run_engine/execution/` (top-level), `run_engine/feedback/`, or `run_engine/logging/`.

## 12. Compatibility Verification

This section states the detailed verification procedure IU-003 (Section 9) carries out, organized by the governing task's own nine-item minimum checklist.

**P2-02A.** Full regression re-run of the P2-02A-certified Position/Exposure scenarios; confirm `position.py` remains git-blob-identical to its pre-IU-001 state.

**P2-03.** Full regression re-run of the P2-03-certified Financial Ownership scenarios; confirm `pnl.py` remains git-blob-identical to its pre-IU-001 state.

**P2-04.** Full regression re-run of the P2-04-certified Risk Ownership scenarios; confirm `risk.py` remains git-blob-identical to its pre-IU-001 state.

**Ownership.** Confirm Market Regime's Computational Authority (`RegimeClassifier`) and Authoritative Owner (`CanonicalState`) are unchanged after IU-001; confirm only the Writer-on-Behalf-Of mechanism changed.

**Runtime Ownership Matrix.** Confirm the Matrix's own "Market Regime" row (`CanonicalState` | `RegimeClassifier` | `RegimeClassifier` | `StrategySelector`) is now more precisely realized in practice (Writer-on-Behalf-Of routed through `CanonicalEnforcer`, matching the Matrix's general CA-naming-convention reading this governance chain has already established); confirm the Matrix's own "Runtime Tick" row remains unaffected.

**AI (Architecture Invariants).** Re-check all twelve P3-01-AI-series invariants (Architecture Section 25) against the post-IU-001 runtime; re-confirm no Baseline-level Architecture Invariant (AI-001 through AI-015) is contradicted.

**AC (Acceptance Criteria).** Re-check all twelve Architecture-level P3-01-AC-series criteria (Architecture Section 31) against the post-IU-001 runtime.

**TD (Technical Debt).** Confirm TD-004 and TD-007 remain unaddressed and unreopened; confirm the Recommended Technical Debt Candidate the Architecture named (Post-Exception Financial/Lifecycle Divergence, Architecture Section 27) remains a documented recommendation only, not implemented or registered by this Specification.

**CUO (Cross-Unit Observation CUO-01).** Confirm `CanonicalState.get()`'s own reference-versus-copy semantics remain unaddressed; confirm `canonical_state.py`'s own `get()` method is git-blob-identical to its pre-IU-001 state.

**VC (Verified Conformant Finding VC-01).** Confirm Tick-Complete Publication's own aggregate-incremental-call realization remains valid after IU-001 adds an eleventh `apply_*` call; confirm no atomic publish/commit mechanism was introduced.

## 13. No-Change Inventory

No runtime code change is required for the following files; each justification is independently derived from the governing Architecture Decisions, not merely asserted.

**`run_engine/main.py`** - AD-004 ratifies `main.py`'s own existing `try`/`except Exception`/continue pattern as the architecturally sufficient realization of caller-side Failed-Tick responsibility (Contract EO-010); no new responsibility is assigned to it.

**`run_engine/core/state.py`** - State Acquisition and Normalization's own ordering position is ratified unchanged by AD-001 (Contract EO-001); `StateEngine`'s own internal computation is untouched by any Architecture Decision.

**`run_engine/core/regime.py`** - `RegimeClassifier`'s own Computational Authority role (its `classify()` computation) is explicitly unchanged by AD-002; only the Writer-on-Behalf-Of mechanism carrying its already-computed value into `CanonicalState` changes, and that change is entirely `RunLoop`'s and `CanonicalEnforcer`'s own responsibility (Contract EO-003).

**`run_engine/core/decision.py`** - confirmed inactive; AD-009 ratifies its continued exclusion from the active path (Contract EO-015); not reclassified by this Specification.

**`run_engine/core/trade_lifecycle.py`** - TradeLifecycle Update's own ordering position is ratified unchanged by AD-001; `RUNTIME_FAILURE_EVENT` generation remains scoped exclusively to lifecycle-transition rejection, explicitly not extended to cover a Failed Tick (AD-004, Contract EO-009).

**`run_engine/core/position.py`** - Position Update's own ordering position is ratified unchanged by AD-001; Position ownership remains exactly as certified by P2-02A, not reopened (AI-010).

**`run_engine/core/pnl.py`** - Financial Accounting's own ordering position is ratified unchanged by AD-001; Financial Ownership remains exactly as certified by P2-03, not reopened (AI-010).

**`run_engine/core/risk.py`** - Risk Evaluation's own ordering position is ratified unchanged by AD-001; Risk Ownership remains exactly as certified by P2-04, not reopened (AI-010).

**`run_engine/core/performance.py`** - Performance Evaluation's own ordering position is ratified unchanged by AD-001; its own internal accounting semantics (Gap 4/TD-004) are explicitly forwarded to P3-03 by AD-010, not addressed here (Contract EO-016).

**`run_engine/core/canonical_state.py`** - `update_regime()`, the method IU-001's own new `CanonicalEnforcer` method reuses unchanged, already exists and requires no modification; `CanonicalState`'s own schema, default values, and `get()` method (CUO-01, explicitly not addressed here per AD-010) all remain untouched.

## 14. Runtime Impact

**New Runtime Method: `CanonicalEnforcer.apply_regime(...)`** (name illustrative, matching the existing `apply_*` naming convention; no concrete Python signature is specified by this document). Functional responsibility only: accept a regime value; if the value is not absent, write it into `CanonicalState` via the already-existing `update_regime()` method and return the newly stored value; if the value is absent, return the currently stored value without writing. This mirrors, without deviation, the shape every one of `CanonicalEnforcer`'s ten existing `apply_*` methods already follows.

**`RunLoop`'s Sole Functional Change.** `RunLoop.step()`'s own direct `CanonicalState.update_regime()` call is removed; a call to the new `CanonicalEnforcer` method is introduced at the identical relative position within the tick sequence. No other functional change occurs anywhere in `RunLoop.step()`'s own body as a consequence of this Specification.

**No Other Runtime Impact.** No other file, method, schema key, or Runtime Event is added, removed, or modified by this Specification's own scope.

## 15. Constraints

Restating the Architecture's own seven Constraints (Section 26) as binding Specification-level directives, none independently decided here:

**Implementation Constraint IC-001.** No Implementation Unit in this document shall change the runtime ordering established by AD-001/Contract EO-001.

**Implementation Constraint IC-002.** No Implementation Unit in this document shall change Tick Completion semantics established by AD-003/Contracts EO-005, EO-006.

**Implementation Constraint IC-003.** No Implementation Unit in this document shall change Failure semantics established by AD-004/AD-006, Contracts EO-007 through EO-012.

**Implementation Constraint IC-004.** No Implementation Unit in this document shall change Replay semantics established by AD-007/Contract EO-013.

**Implementation Constraint IC-005.** No Implementation Unit in this document shall change any already-certified Ownership assignment (Computational Authority, Authoritative Owner) for any object this unit's scope touches; only Market Regime's own Writer-on-Behalf-Of mechanism changes (AD-002).

**Implementation Constraint IC-006.** No Implementation Unit in this document shall alter the Risk, Financial, or Position architecture certified by P2-04, P2-03, or P2-02A respectively.

**Implementation Constraint IC-007.** No Implementation Unit in this document shall make a copy-versus-reference decision for `CanonicalState.get()` (CUO-01, AD-010, Contract EO-016).

**Implementation Constraint IC-008.** No Implementation Unit in this document shall implement any P3-02 or P3-03 work.

## 16. Traceability

### 16.1 Functional Requirement Traceability (Individually Enumerated)

| FR | Governing Contract(s) |
|---|---|
| FR-001 | EO-001, EO-002 |
| FR-002 | EO-001, EO-004 |
| FR-003 | EO-001 |
| FR-004 | EO-001, EO-003 |
| FR-005 | EO-001 |
| FR-006 | EO-001 |
| FR-007 | EO-001 |
| FR-008 | EO-001 |
| FR-009 | EO-001 |
| FR-010 | EO-001 |
| FR-011 | EO-001 |
| FR-012 | EO-001 (No-Change Inventory, Section 13) |
| FR-013 | EO-005, EO-006 |
| FR-014 | EO-006 |
| FR-015 | EO-011 |
| FR-016 | EO-012 |
| FR-017 | EO-013 |
| FR-018 | EO-015 |
| FR-019 | EO-003 |
| FR-020 | EO-007, EO-008, EO-009, EO-010 |
| FR-021 | EO-014 |
| FR-022 | No-Change Inventory (Section 13), Implementation Constraint IC-005/IC-006 |
| FR-023 | EO-016 |

All twenty-three Functional Requirements are governed by at least one Runtime Contract or explicit Specification-level provision.

### 16.2 SDA Dependency Traceability (Individually Enumerated)

| DEP | Governing Contract(s) |
|---|---|
| DEP-001 | EO-001 |
| DEP-002 | EO-003 |
| DEP-003 | EO-001 |
| DEP-004 | EO-001 |
| DEP-005 | EO-001 |
| DEP-006 | EO-001 |
| DEP-007 | EO-001 |
| DEP-008 | EO-001 |
| DEP-009 | EO-005, EO-006 |
| DEP-010 | EO-006 |
| DEP-011 | EO-001 |
| DEP-012 | EO-015 |
| DEP-013 | EO-001 |
| DEP-014 | EO-011 |
| DEP-015 | EO-012 |
| DEP-016 | EO-012 |
| DEP-017 | Implementation Constraint IC-006 (No-Change Inventory, Section 13) |
| DEP-018 | Implementation Constraint IC-006 (No-Change Inventory, Section 13) |
| DEP-019 | Implementation Constraint IC-006 (No-Change Inventory, Section 13) |
| DEP-020 | Implementation Constraint IC-006 (No-Change Inventory, Section 13) |
| DEP-021 | Implementation Constraint IC-005/IC-006 |
| DEP-022 | EO-003 |
| DEP-023 | EO-007, EO-008, EO-009, EO-010 |
| DEP-024 | EO-013 |
| DEP-025 | EO-013 |
| DEP-026 | EO-014 |
| DEP-027 | EO-016, Implementation Constraint IC-007 |
| DEP-028 | EO-016, Implementation Constraint IC-007 |
| DEP-029 | EO-016, Implementation Constraint IC-006/IC-008 |
| DEP-030 | EO-009, EO-016 |
| DEP-031 | EO-006 |

All thirty-one Dependency records are governed by at least one Runtime Contract or explicit Implementation Constraint.

### 16.3 CGA Capability Traceability (Individually Enumerated)

| CAP | Governing Contract(s) |
|---|---|
| CAP-001 | EO-001 |
| CAP-002 | EO-004 |
| CAP-003 | EO-001 |
| CAP-004 | EO-003 |
| CAP-005 | EO-001 |
| CAP-006 | EO-001 |
| CAP-007 | EO-001 |
| CAP-008 | EO-001 |
| CAP-009 | EO-001 |
| CAP-010 | EO-001 |
| CAP-011 | EO-001, EO-016 |
| CAP-012 | EO-001, EO-016 |
| CAP-013 | EO-005, EO-006 |
| CAP-014 | EO-006 |
| CAP-015 | EO-011 |
| CAP-016 | EO-012 |
| CAP-017 | EO-013 |
| CAP-018 | EO-015 |
| CAP-019 | EO-003 |
| CAP-020 | EO-007 through EO-010 |
| CAP-021 | EO-014 |
| CAP-022 | Implementation Constraint IC-005/IC-006 |
| CAP-023 | EO-016 |

All twenty-three Capabilities are governed by at least one Runtime Contract or explicit Implementation Constraint.

### 16.4 Architecture Decision, Invariant, and Remaining Traceability

| Category | Coverage |
|---|---|
| Architecture Decisions | AD-001 through AD-010, each realized by at least one Runtime Contract (Section 6) and at least one Implementation Unit (Sections 7 through 9). |
| Architecture Invariants | P3-01-AI-001, AI-002, AI-003, AI-004, AI-005, AI-006, AI-007, AI-008, AI-009, AI-010, AI-011, AI-012, each individually re-checked by IU-003's own Compatibility Verification (Section 12). |
| Runtime Ownership Matrix | Re-checked by IU-003 (Section 12); Market Regime and Runtime Tick rows both explicitly addressed. |
| ADR-002, ADR-010, ADR-011 | Governing every Runtime Contract in Section 6 by inheritance from the Architecture's own Section 3. |
| AC-009, AC-010, AC-011, AC-012 | Re-checked by IU-003 (Section 12), inherited from the Architecture's own Baseline-level citations. |
| P2-02A, P2-03, P2-04 | Compatibility re-verified by IU-003 (Section 9, Section 12); no contract reopened. |
| TD-004, TD-007 | Confirmed unaddressed by IU-003 (Section 12); Recommended Technical Debt Candidate (Post-Exception Financial/Lifecycle Divergence) confirmed not implemented or registered. |
| CUO-01, VC-01 | Confirmed unaddressed (CUO-01) and confirmed still valid (VC-01) by IU-003 (Section 12) and Contracts EO-006, EO-016. |

## 17. Non-Goals

Consistent with Section 2 and the governing task's own explicit prohibition list: no new architecture, no new scientific analysis, no new capability assessment, no new Functional Requirement, Dependency, Architecture Decision, or Architecture Invariant is introduced anywhere in this document; no concrete Python signature, complete file diff, or test implementation is specified; no P3-02 or P3-03 work is performed or anticipated beyond Contract EO-016's own explicit non-resolution statement; no Persistence, Recovery, or Operator Lifecycle Control mechanism is designed; no `CanonicalState.get()` copy-versus-reference decision is made; no Position, Financial, or Risk formula or ownership is altered.

## 18. Internal Consistency Review

**Terminology consistency.** "Computational Authority," "Authoritative Owner," "Writer-on-Behalf-Of," "Publication," and "Consumption" are used exactly as defined in the Architecture Baseline and inherited unchanged from the Architecture document throughout this Specification; every Runtime Contract's own Requirement field keeps the four concepts explicitly separate wherever Market Regime's ownership is discussed (Contract EO-003). "Functionally identical" is used exclusively for runtime-object, tick-result-dictionary, and `CanonicalState`-snapshot comparisons (Sections 7 through 9, Section 11). "Byte-identical" occurs exactly once in this document (P3-01-SPEC-AC-004, Section 7), describing a genuine single-source-line comparison (`RunLoop.step()`'s own Runtime Tick write call site, before and after IU-001), not a runtime-value or schema-shape comparison. The term "byte-for-byte" is never used in this document to describe a comparison this document itself performs; every occurrence of that term anywhere in this document (including this sentence's own mention of it, and Section 19's own quoted citation of a correction made in a different document) is meta-discussion or citation, not a comparison claim.

**Specification consistency.** Every Runtime Contract in Section 6 traces to exactly one governing Architecture Decision; no contract introduces a requirement absent from the Architecture's own Section 24. Every Implementation Unit (Sections 7 through 9) is either the sole file-touching unit (IU-001) or explicitly Verification-Only (IU-002, IU-003), consistent with the Architecture's own Implementation Impact Inventory (Architecture Section 32).

**Architecture consistency.** No decision in this document contradicts or extends AD-001 through AD-010; every Runtime Contract restates, at the implementation-directive level, a decision the Architecture already made, without introducing a new one.

**Ownership consistency.** No Runtime Contract or Implementation Unit assigns a new Authoritative Owner or Computational Authority; Contract EO-003 changes only Market Regime's Writer-on-Behalf-Of mechanism, explicitly stated as such.

**Runtime consistency.** The No-Change Inventory's own ten justifications (Section 13) are each independently derived from a specific Architecture Decision, not merely asserted; the Runtime Impact statement (Section 14) names exactly one new method and one changed call site, matching the Architecture's own Implementation Impact Inventory exactly.

**Traceability completeness.** Section 16 confirms all twenty-three Functional Requirements, all thirty-one Dependencies, all twenty-three Capabilities, all ten Architecture Decisions, and all twelve Architecture Invariants are referenced by at least one Runtime Contract, Implementation Unit, or No-Change Inventory entry.

**No fabricated contract.** Every one of the sixteen Runtime Contracts traces to a specific Architecture Decision's own Motivation, Decision, and Acceptance Criteria fields; no contract in this document addresses a concern absent from the Architecture.

Status: Internal Consistency Review PASS.

## 19. Independent Self Verification

Every claim in Sections 4 through 18 was independently re-derived during this Specification session, not inherited from the Architecture's own text without re-checking: `canonical_enforcer.py`'s ten existing methods were re-read in full (Section 4), confirming the exact shape Contract EO-003's own new-method functional responsibility (Section 7) must mirror; `canonical_state.py`'s own `update_regime()` method and `regime.py`'s own `classify()` method were re-confirmed unchanged and reusable without modification.

Cross-document consistency check: every AD-001 through AD-010 citation in this document (Section 6, Sections 7 through 9) was compared against the current, final text of `P3_01_DETERMINISTIC_EXECUTION_ORDERING_ARCHITECTURE_V1_2026-07-13.md`, including that document's own post-review corrections (the DEP-/CAP-ID traceability expansion, the "byte-for-byte" terminology correction), and found consistent - this document was drafted after, and reflects, the Architecture's own fully revised state.

Result: no error was found during this document's own closing review requiring correction before delivery. All findings from this document's own internal reviews (Section 18) are PASS.

Status: Independent Self Verification PASS.

No commit was made. No runtime file was changed. No push was made. This document is ready to be provided as `P3_01_DETERMINISTIC_EXECUTION_ORDERING_SPECIFICATION_V1_2026-07-13.md`.
