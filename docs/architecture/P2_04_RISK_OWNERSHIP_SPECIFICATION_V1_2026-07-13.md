Document Class:
Specification

Document ID:
P2-04-SPEC

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
docs/architecture/P2_04_RISK_OWNERSHIP_SPECIFICATION_V1_2026-07-13.md

Depends On:
- docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md
- docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md
- docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md
- docs/architecture/certification/P2_03_FINAL_CERTIFICATION_V1_2026-07-11.md
- docs/architecture/analysis/P2_04_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-13.md
- docs/architecture/analysis/P2_04_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-13.md
- docs/architecture/analysis/P2_04_CAPABILITY_GAP_ANALYSIS_V1_2026-07-13.md
- docs/architecture/P2_04_RISK_OWNERSHIP_ARCHITECTURE_V1_2026-07-13.md
- current runtime code at HEAD a81e197

Referenced By:
- future P2-04 Implementation
- future P2-04 Certification

---

# P2-04 Risk Ownership Specification

## 1. Purpose

This document specifies, in complete and implementable detail, how the seventeen Architecture Decisions of `P2_04_RISK_OWNERSHIP_ARCHITECTURE_V1_2026-07-13.md` are to be realized. It defines the precise runtime contracts of every component P2-04 touches, the exact normative content of the documentation additions AD-002, AD-004, AD-007, and AD-009 require, the validation procedures the ratification decisions (AD-003, AD-005, AD-008, AD-011 through AD-014, AD-016, AD-017) require, the Implementation Units a future implementation must proceed through, the complete runtime file inventory, and objectively checkable Acceptance Criteria. It contains no Python code and no pseudocode; it modifies no runtime file.

## 2. Scope

In scope: complete specification of Risk Policy Configuration's ownership documentation, `risk_allocation_factor`'s ownership documentation, Position-derived Exposure's functional-disposition documentation, the risk-limiting formula's evaluation-disposition documentation, and the validation procedures ratifying RiskEngine's determinism, statelessness, consumer boundaries, RuntimeFailureEvent non-mutation, reset semantics, TD-006 closure, and compatibility - for `RiskEngine`, `CanonicalState`, `CanonicalEnforcer`, `RunLoop`, and `PerformanceEngine`.

Out of scope, unchanged from the FRA, SDA, CGA, and Architecture: Drawdown and Drawdown Ratio's own Computational Authority, Authoritative Owner, and formula (fully certified by P2-03), `PositionSizingEngine` activation, Position/Exposure ownership itself (P2-02A), `PnLEngine`, `TradeLifecycleEngine`, `main.py`, Persistence, Recovery, repository cleanup, the automated regression test suite (TD-005), numeric calibration of any Risk Policy Configuration value, and `PerformanceEngine`'s Risk-Metric consumption boundary (AD-017). This document makes no architecture decision; every specification choice below cites the Architecture Decision it implements, and none introduces a decision the Architecture document did not already authorize.

## 3. Binding Baseline

- `docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md` - ADR-004, ADR-006, ADR-007, ADR-011, the Runtime Ownership Matrix's "Risk Metrics" row, Rules OM-001 through OM-009, AI-002, AI-005, AI-010, AI-013, AC-003, AC-007.
- `docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md` - P2-04's unit definition and this Specification's place in the governance sequence.
- `docs/architecture/analysis/P2_04_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-13.md` - fifteen functional requirements (FR-001 through FR-015).
- `docs/architecture/analysis/P2_04_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-13.md` - sixteen dependency records (DEP-001 through DEP-016).
- `docs/architecture/analysis/P2_04_CAPABILITY_GAP_ANALYSIS_V1_2026-07-13.md` - fifteen capabilities (CAP-001 through CAP-015).
- `docs/architecture/P2_04_RISK_OWNERSHIP_ARCHITECTURE_V1_2026-07-13.md` - seventeen Architecture Decisions (AD-001 through AD-017), nine Architecture Invariants (P2-04-AI-001 through AI-009), six Architecture Constraints, fifteen Acceptance Criteria, Readiness: READY.
- `docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md` - TD-001 through TD-007, in particular TD-006.
- `docs/architecture/certification/P2_03_FINAL_CERTIFICATION_V1_2026-07-11.md` - the certified baseline this document treats as immutable.
- Current runtime code at HEAD `a81e1978cb07bbb26223c94a1b24e9220520c445`, re-verified for this document (Section 5).

## 4. Repository Current State

Branch `run-engine-consolidation-safety`, HEAD `a81e1978cb07bbb26223c94a1b24e9220520c445`, matching the FRA's, SDA's, CGA's, and Architecture document's own verification exactly (`git branch --show-current`, `git rev-parse HEAD`). `run_engine/` remains clean (`git status --short run_engine/` returns no output). `run_engine/core/risk.py` and `run_engine/core/loop.py` were re-read in full immediately before drafting this document and found unchanged from every prior verification in this governance chain. A repository-wide search for Risk-Ownership-adjacent terms (`drawdown`, `exposure`, `risk_allocation`, `RiskEngine`, `RiskLayer`, `CanonicalState`, case-insensitive) under `run_engine/` was re-run and returned the identical six files every predecessor document established (`run_engine/core/risk.py`, `run_engine/core/loop.py`, `run_engine/core/canonical_state.py`, `run_engine/core/position.py`, `run_engine/core/position_sizing.py`, `run_engine/runtime/risk.py`); no drift found. The working tree's pre-existing, unrelated modified and untracked entries (Architecture Section 4) remain observed, unchanged, and untouched by this document.

This document specifies against exactly this unchanged code. `risk.py`'s full current content (55 lines) and `loop.py`'s full current content (132 lines) are the baseline every contract in Sections 9 through 18 below is stated relative to.

## 5. Normative Terminology

This document uses "SHALL" for a mandatory, verifiable contract; "SHALL NOT" for a mandatory prohibition; "MAY" for an explicitly permitted but non-mandatory option. These match the Architecture Baseline's own normative vocabulary and are not redefined here.

**Runtime Contract** - a precisely stated input/output/precondition/postcondition relationship for one runtime component's one responsibility, expressed in prose and set/tuple notation, never as Python syntax.

**Documentation Contract** - a specification of the exact normative content (not the literal wording) an in-code comment or docstring SHALL convey, realizing an Architecture Decision's disposition without altering runtime behavior. Distinct from a Runtime Contract: a Documentation Contract constrains what a human reader of the source must be able to learn from it; it constrains no program behavior.

**Verification Obligation** - a specification of an objectively checkable procedure a future Implementation or Certification stage SHALL execute to confirm an already-true property remains true, distinct from an implementation task, since no code change is its subject.

**Implementation Unit (IU)** - a logically scoped body of work, realizing one or more Architecture Decisions, that MAY span multiple files or MAY require no file at all (a Verification-Only Implementation Unit), per the Implementation Baseline's own definition that Implementation Units describe logical implementation areas, not individual files.

All other terms (Risk Metric, Risk Policy Configuration, Position-Derived Exposure, Financial State, Performance Metric, Functional Disposition) are inherited unchanged from the Architecture document's own Section 5 and are not redefined here.

## 6. Specification Principles

This document resolves no Architecture Question; the Architecture document (its Section 8 summary table) already resolved all nine. Where an AD's own Compatibility Constraints left a documentation-wording or verification-procedure detail unstated, this document resolves that detail (Sections 9 through 19), citing the AD it implements in every case; it introduces no decision the Architecture document did not already authorize.

This document's central organizing fact, inherited directly from the Architecture document's own Implementation Impact Inventory (Architecture Section 28): no Architecture Decision in this unit requires a runtime behavior change. Four ADs (AD-002, AD-004, AD-007, AD-009) require a Documentation Contract only. Nine ADs (AD-003, AD-005, AD-008, AD-011 through AD-014, AD-016, AD-017) require a Verification Obligation only. Four ADs (AD-001, AD-006, AD-010, AD-015) require neither, being closure or taxonomy statements already fully satisfied by the Architecture document's own text. This Specification is therefore, in character, a documentation-and-verification specification, not a behavior-change specification, and Sections 22 through 26 (Implementation Units, File Inventory, Change Plan, No-Change Inventory) reflect this directly rather than manufacturing behavioral work the Architecture did not require.

Runtime contracts in this document are described in terms of named inputs, named outputs, preconditions, and postconditions, stated in prose and mathematical/set notation. Mathematical formulas use algebraic notation (`+`, `-`, `*`, `MAX`, `>`) consistent with the notation the FRA, SDA, CGA, and Architecture already use; this is specification notation, not a code fragment, and defines no programming-language-specific construct. Where this document quotes an exact existing code line for precise identification (for example, to state which line a Documentation Contract's comment attaches to), the quotation identifies a location, not a proposed replacement.

## 7. Runtime Components

Five runtime components are specified in this document: `RiskEngine`, `CanonicalState`, `CanonicalEnforcer`, `RunLoop`, `PerformanceEngine`. `PnLEngine`, `PositionEngine`, `TradeLifecycleEngine`, `StateEngine`, `RegimeClassifier`, `StrategySelector`, `Executor`, and `main.py` are consulted for context and runtime-ordering placement (Section 17) but are not modified by any decision in this unit and receive no contract here, consistent with AD-016's compatibility-preservation decision.

| Component | File | Role in P2-04 | Change Category |
|---|---|---|---|
| `RiskEngine` | `run_engine/core/risk.py` | Computational Authority for `risk_allocation_factor`; Authoritative Owner of Risk Policy Configuration; consumer of Position, Equity, Peak Equity | Documentation Contracts (Section 12); Verification Obligations |
| `CanonicalState` | `run_engine/core/canonical_state.py` | Authoritative Owner of Drawdown, Drawdown Ratio, `risk_allocation_factor` | Verification Obligation only; no schema change |
| `CanonicalEnforcer` | `run_engine/core/canonical_enforcer.py` | Writer-on-Behalf-Of for Drawdown, Drawdown Ratio, `risk_allocation_factor` | Verification Obligation only; no interface change |
| `RunLoop` | `run_engine/core/loop.py` | Orchestrates the unchanged tick sequence; invokes `RiskEngine.check()` | Verification Obligation only; no sequence change |
| `PerformanceEngine` | `run_engine/core/performance.py` | Confirmed non-consumer of Risk Metrics (AD-017) | Verification Obligation only; no interface change |

## 8. Runtime Interfaces

The following interfaces are specified as existing, ratified contracts (AD-003, AD-008, AD-011 through AD-014); none is newly introduced or altered by this document.

**`RiskEngine.check`** - accepts exactly three positional inputs, in this order: the canonical financial/regime state (a mapping containing at minimum `equity` and `peak_equity`), the canonical Position record (a mapping containing at minimum `exposure`), and the current market regime (one of `"CHOP"`, `"TREND"`, `"VOLATILE"`, or an unrecognized value). Returns exactly one mapping containing five entries: `equity` (echoed input), `peak_equity` (echoed input), `drawdown`, `drawdown_ratio`, `exposure` (the internal name for `risk_allocation_factor`, per P2-02A-AD-007, unrenamed by this unit).

**`CanonicalState.update_risk`** - accepts exactly one mapping input (the shape `RiskEngine.check`'s return value already has) and writes exactly three canonical keys: `drawdown`, `drawdown_ratio`, `risk_allocation_factor` (sourced from the input mapping's `exposure` entry). The input mapping's `equity` and `peak_equity` entries are read by no code path in this method and are not written to any canonical key by it.

**`CanonicalEnforcer.apply_risk`** - accepts exactly one input, either a mapping or `None`. When `None`, returns the current, unmodified canonical state without calling `CanonicalState.update_risk`. When a mapping, calls `CanonicalState.update_risk` with it, then returns the resulting canonical state.

**`RunLoop.step`**'s risk-relevant call sequence - retrieves the current canonical state (post-Financial-State-publication), invokes `RiskEngine.check` with that state, the current tick's Position, and the current tick's regime, then invokes `CanonicalEnforcer.apply_risk` with `check`'s return value (or an empty mapping if the return value is not a mapping).

No interface listed above changes shape, parameter count, parameter order, or return shape as a result of any decision in this document; every AD in Section 19 of the Architecture document that touches one of these interfaces (AD-002, AD-004, AD-007, AD-009) requires only a Documentation Contract (Section 12) attached to the existing interface, never an interface modification.

## 9. Runtime Contracts

This section states the cross-cutting contract every component-specific contract in Sections 10 through 16 must jointly satisfy, synthesized from the Architecture document's own Sections 9 through 18.

**Contract RC-001 (Ownership Uniqueness).** For every Risk Metric (Drawdown, Drawdown Ratio, `risk_allocation_factor`), exactly one Computational Authority and exactly one Authoritative Owner SHALL exist at all times, per AD-003, AD-004, AD-005, AD-006.

**Contract RC-002 (Configuration Non-Publication).** Risk Policy Configuration SHALL possess no `CanonicalState` key at any time, per AD-002.

**Contract RC-003 (Exposure Non-Participation).** `risk_allocation_factor`'s value SHALL be computable, for any given `RiskEngine` instance, from `drawdown_ratio` and `regime` alone, without reference to `position_exposure`, per AD-007.

**Contract RC-004 (Formula Stability).** The risk-limiting formula's structural shape SHALL remain exactly as specified in Section 15 unless superseded by an Architecture Evolution Review, per AD-009.

**Contract RC-005 (Purity and Statelessness).** `RiskEngine.check` SHALL be a pure function of its three parameters; `RiskEngine` SHALL hold no instance attribute beyond its three Risk Policy Configuration constants, at any point in its lifecycle, per AD-011, AD-012.

**Contract RC-006 (Read-Only Consumption).** `RiskEngine` SHALL NOT mutate, cache across calls, or republish under an owning name any of: Position, Position-derived Exposure, Equity, Peak Equity, per AD-008, AD-013.

**Contract RC-007 (Failure Non-Mutation).** Rejected transitions SHALL leave Drawdown, Drawdown Ratio, and `risk_allocation_factor` unmodified, per AD-014.

**Contract RC-008 (Compatibility).** No contract in this document SHALL require any change to `run_engine/core/pnl.py`, `run_engine/core/canonical_state.py`'s Equity/Peak-Equity/PnL-adjacent methods, `run_engine/core/position.py`, `run_engine/core/trade_lifecycle.py`, or `run_engine/core/performance.py`, per AD-016, AD-017.

## 10. CanonicalState Contracts

The complete `CanonicalState` schema (fifteen top-level keys, unchanged) is specified below for the three keys this unit's scope covers; the remaining twelve keys are unaffected and are not respecified here (P2-03 Specification Section 8 remains the governing specification for the Financial-State-adjacent keys).

| Key | Type | Default | Risk Metric | Change in This Unit |
|---|---|---|---|---|
| `drawdown` | float | `0.0` | Drawdown | unchanged (AD-005) |
| `drawdown_ratio` | float | `0.0` | Drawdown Ratio | unchanged (AD-005) |
| `risk_allocation_factor` | float | `1.0` | `risk_allocation_factor` | unchanged storage; individually named ownership (AD-004) |

**Contract CS-001 (Schema Stability).** `CanonicalState.__init__`'s default dictionary SHALL continue to define exactly these three keys, at exactly these default values, with no fourth Risk-Metric-category key added, per AD-006.

**Contract CS-002 (Write Path Exclusivity).** `CanonicalState.update_risk` SHALL remain the exclusive method writing any of these three keys; no other `CanonicalState` method SHALL write `drawdown`, `drawdown_ratio`, or `risk_allocation_factor`, per AD-005.

**Contract CS-003 (Reset Behavior).** `CanonicalState.reset()` SHALL continue to restore all three keys to their default values (via its existing `self.__init__()` delegation), unchanged by this unit, per AD-005 (compatibility preservation; not itself an AD-015 subject, since AD-015 concerns Risk Policy Configuration, not Risk Metrics).

## 11. RiskEngine Contracts

**Contract RE-001 (Instance State).** `RiskEngine.__init__` SHALL continue to define exactly three instance attributes - `max_drawdown` (`0.2`), `max_exposure` (`1.0`), `min_exposure` (`0.1`) - and no others, per AD-012, RC-005.

**Contract RE-002 (Input Contract).** `RiskEngine.check` SHALL read `equity` and `peak_equity` exclusively from its `state` parameter, and `exposure` exclusively from its `position` parameter, with no other source for any of the three, per AD-013, RC-006.

**Contract RE-003 (Output Contract).** `RiskEngine.check` SHALL return a mapping with exactly the five keys named in Section 8; `drawdown` SHALL equal `peak_equity - equity`; `drawdown_ratio` SHALL equal `drawdown / peak_equity` when `peak_equity > 0`, otherwise `0.0`; `exposure` SHALL be computed per Section 15's formula contract, per AD-003, AD-004, AD-009.

**Contract RE-004 (Non-Mutation Contract).** `RiskEngine.check` SHALL NOT assign to any attribute of its `state` or `position` parameters, at any point in its execution, per AD-008, AD-013, RC-006.

**Contract RE-005 (Determinism Contract).** `RiskEngine.check`'s return value SHALL depend only on the values of its three parameters at call time; two calls with parameters that are themselves equal (though not necessarily identical objects) SHALL produce functionally identical return values, per AD-011, RC-005.

## 12. Publication Contracts

**Contract PC-001 (Writer-on-Behalf-Of Exclusivity).** `CanonicalEnforcer.apply_risk` SHALL remain the sole code path by which any of `drawdown`, `drawdown_ratio`, or `risk_allocation_factor` is written to `CanonicalState`, per AD-005, Contract CS-002.

**Contract PC-002 (Atomicity).** `RunLoop.step`'s single call to `CanonicalEnforcer.apply_risk` per tick SHALL remain the only point at which these three keys are updated within a tick; no partial or staged update of any of the three SHALL occur, per AD-005, AD-011 (Deterministic Runtime Execution Ordering, unchanged).

**Contract PC-003 (Risk Policy Configuration Non-Publication).** No future implementation of any AD in this unit SHALL introduce a Writer-on-Behalf-Of path for any Risk Policy Configuration value, per AD-002, Contract RC-002.

## 13. Consumption Contracts

| Consumer | Reads | Contract |
|---|---|---|
| `RiskEngine` | canonical `equity`, `peak_equity` (via `state`); `exposure` (via `position`) | RE-002; read-only (RE-004) |
| `PerformanceEngine` | none of `drawdown`, `drawdown_ratio`, `risk_allocation_factor` | AD-017; verified unchanged (Section 19) |
| External/downstream result consumers | the complete Tick-Complete `CanonicalState` snapshot, via `RunLoop.step`'s own return mapping | unchanged; out of this document's scope |

**Contract CC-001 (PerformanceEngine Non-Consumption).** `performance.py` SHALL contain no reference to `drawdown`, `drawdown_ratio`, or `risk_allocation_factor` as a result of any implementation of this document, per AD-017.

**Contract CC-002 (No New Consumer).** No component other than `RiskEngine` (for Equity, Peak Equity, Position-derived Exposure) SHALL be introduced as a consumer of any Risk Metric or Risk Policy Configuration value by any implementation of this document.

## 14. Risk Policy Configuration Contracts

| Value | Type | Current Value | Authoritative Owner | Publication |
|---|---|---|---|---|
| `max_drawdown` | float | `0.2` | `RiskEngine` (AD-002) | none |
| `max_exposure` | float | `1.0` | `RiskEngine` (AD-002) | none |
| `min_exposure` | float | `0.1` | `RiskEngine` (AD-002) | none |
| CHOP regime multiplier | float | `0.7` | `RiskEngine` (AD-002) | none |
| TREND regime multiplier | float | `1.0` | `RiskEngine` (AD-002) | none |
| VOLATILE regime multiplier | float | `0.5` | `RiskEngine` (AD-002) | none |

**Contract RP-001 (Immutability).** No Risk Policy Configuration value SHALL be reassigned anywhere in `RiskEngine`'s lifecycle after `__init__` completes, per AD-012, RE-001.

**Contract RP-002 (Single Declaration Point).** `RiskEngine.__init__` (for the three named thresholds) and `RiskEngine.check`'s own body (for the three inline regime multipliers) SHALL remain the sole declaration points for these six values; no duplicate declaration SHALL exist anywhere in the active runtime path, per AD-002, AD-006 (repository-wide search confirms the confirmed-inactive `RiskLayer`'s own, differently-scaled values do not constitute a duplicate on the active path).

**Contract RP-003 (Documentation Requirement).** `RiskEngine`'s source SHALL carry a Documentation Contract (Section 20, IU-001) stating that these six values constitute Risk Policy Configuration, that `RiskEngine` is their Authoritative Owner per AD-002, and that they are deliberately not published to `CanonicalState`.

## 15. Exposure Contracts

**Contract EX-001 (Consumption Preservation).** `RiskEngine.check`'s existing read, `position.get("exposure", 0.0)`, SHALL be preserved exactly as it stands, satisfying ADR-004's consumption requirement, per AD-007, AD-008.

**Contract EX-002 (Non-Participation).** The local variable this read populates SHALL NOT be referenced by any subsequent line computing `drawdown`, `drawdown_ratio`, or `exposure` (the `risk_allocation_factor` return value), per AD-007, Contract RC-003.

**Contract EX-003 (Documentation Requirement).** The line implementing Contract EX-001 SHALL carry a Documentation Contract (Section 20, IU-001) stating that Position-derived Exposure is read to satisfy ADR-004's consumption requirement, that its functional non-incorporation is a deliberate, recorded architecture decision (AD-007), and that reactivating its functional use requires an Architecture Evolution Review, not an incidental code change.

**Contract EX-004 (Naming Preservation).** The internal local-variable name distinguishing this read from `RiskEngine`'s own allocation-scaling local variable (`exposure`, Section 8) SHALL be preserved, since P2-02A-AD-007 already establishes this distinction is required to avoid a naming collision within the same method body.

## 16. Runtime Behaviour

The normative runtime ordering below describes observable behavior, not internal code structure, per the Architecture Baseline's own distinction between the two.

**Tick-level sequence, risk-relevant steps only (unchanged from Architecture Section 18, itself unchanged from the certified P2-03 sequence):**

1. `RunLoop` obtains the current, post-Financial-State-publication canonical state.
2. `RunLoop` invokes `RiskEngine.check`, passing the canonical state, the current tick's Position (including Position-derived Exposure), and the current tick's regime.
3. `RiskEngine.check` reads canonical `equity` and `peak_equity`, and Position's `exposure`; computes `drawdown`, `drawdown_ratio`, and `exposure` (`risk_allocation_factor`) per Section 15's formula contract; returns all five values in one mapping.
4. `RunLoop` invokes `CanonicalEnforcer.apply_risk` with that mapping (or an empty mapping, per Contract RE-003's isinstance guard, if the return value is not a mapping).
5. `CanonicalEnforcer.apply_risk` invokes `CanonicalState.update_risk`, which writes `drawdown`, `drawdown_ratio`, and `risk_allocation_factor`.
6. `RunLoop` invokes `PerformanceEngine.update`, which reads none of the three values just published.

**Contract RB-001 (Sequence Preservation).** This six-step sequence SHALL execute, in this order, exactly once per tick, with no step skipped, reordered, or duplicated, per AD-011 (Deterministic Runtime Execution Ordering, cited by reference, unchanged by this unit).

**Contract RB-002 (No Intermediate Observation).** No component downstream of step 5 SHALL observe a Risk Metric value from any tick other than the one currently completing step 5, per the Architecture Baseline's own Tick-Complete Snapshot invariant (AI-009, cited by reference, unaffected by this unit).

## 17. Determinism Requirements

**Requirement DET-001.** `RiskEngine.check(state, position, regime)` SHALL return functionally identical output for functionally identical input, for any two calls, regardless of call history, per AD-011, Contract RE-005.

**Requirement DET-002.** `RiskEngine` SHALL reference no wall-clock value, no random-number source, and no global mutable state anywhere in `check`'s execution, per AD-011.

**Requirement DET-003.** `vars(RiskEngine())` SHALL return exactly `{'max_drawdown': 0.2, 'max_exposure': 1.0, 'min_exposure': 0.1}`, both immediately after initialization and after any number of subsequent `check()` calls, per AD-012, Contract RE-001.

**Verification Procedure for DET-001 through DET-003 (Section 22, IU-002):** two independent `RiskEngine` instances, each driven through an identical scripted tick/decision sequence, SHALL produce functionally identical per-tick `drawdown`, `drawdown_ratio`, and `risk_allocation_factor` sequences; `vars()` SHALL be inspected at initialization and after the full sequence completes for each instance.

## 18. Reset Requirements

**Requirement RST-001.** No dedicated reset method SHALL be added to `RiskEngine`, per AD-015: since Risk Policy Configuration is never mutated after `__init__` (Contract RP-001) and is never published to `CanonicalState` (Contract RC-002), no state exists anywhere that a reset could need to restore.

**Requirement RST-002.** `CanonicalState.reset()` SHALL continue to restore `drawdown`, `drawdown_ratio`, and `risk_allocation_factor` to their default values via its existing `self.__init__()` delegation, unaffected by any decision in this unit, per Contract CS-003.

**Requirement RST-003.** A fresh `RiskEngine()` instantiation SHALL deterministically re-establish the identical Risk Policy Configuration values as every prior instantiation, per Contract RP-001, RP-002.

**Verification Procedure for RST-001 through RST-003 (Section 22, IU-002):** instantiate `RiskEngine` twice, independently; confirm `vars()` is identical across both instances; confirm no `reset`-named method exists on the class; confirm `CanonicalState().reset()` restores all three Risk-Metric-category keys to their documented defaults (Section 10).

## 19. Runtime Constraints

**Constraint RTC-001.** No file other than `run_engine/core/risk.py` SHALL require any modification as a result of this document (Section 25).

**Constraint RTC-002.** Any modification to `run_engine/core/risk.py` under this document SHALL be limited to comment or docstring content; no line of executable code SHALL be added, removed, or reordered, per Section 6's central organizing fact.

**Constraint RTC-003.** No numeric value in `risk.py:5-7,37-44` SHALL change as a result of this document, per AD-009's Compatibility Constraints (numeric calibration remains explicitly out of scope).

**Constraint RTC-004.** No new import, dependency, or cross-module reference SHALL be introduced by any Implementation Unit in this document.

## 20. Compatibility Requirements

**Requirement COMPAT-001.** Full regression re-run of the P2-03-certified and P2-02A-certified scenarios (the deterministic OPEN/HOLD/SCALE_IN/PARTIAL_CLOSE/FULL_CLOSE sequence; the RUNTIME_FAILURE_EVENT non-mutation scenario; the replay/determinism double-run) SHALL produce functionally identical results for every already-certified field, after any implementation of this document, per AD-016.

**Requirement COMPAT-002.** `python -m compileall run_engine` SHALL PASS after any implementation of this document.

**Requirement COMPAT-003.** Every import in `run_engine/core/loop.py` (eleven imports, unchanged since before P2-03) SHALL remain byte-for-byte identical after any implementation of this document, since this is a genuine source-file-line comparison, not a runtime-object comparison.

**Requirement COMPAT-004.** `git diff --stat` against HEAD `a81e197`, restricted to `run_engine/`, SHALL show only `run_engine/core/risk.py` as changed, and only in comment/docstring lines, after any implementation of this document.

## 21. Acceptance Criteria

**P2-04-SPEC-AC-001.** `risk.py` carries a Documentation Contract (IU-001) stating Risk Policy Configuration's ownership per AD-002, verifiable by direct read.

**P2-04-SPEC-AC-002.** `risk.py` carries a Documentation Contract (IU-001) stating `risk_allocation_factor`'s individually-named ownership per AD-004, verifiable by direct read.

**P2-04-SPEC-AC-003.** `risk.py` carries a Documentation Contract (IU-001) stating Position-derived Exposure's non-incorporation disposition per AD-007, verifiable by direct read.

**P2-04-SPEC-AC-004.** `risk.py` carries a Documentation Contract (IU-001) stating the risk-limiting formula's retention disposition per AD-009, verifiable by direct read.

**P2-04-SPEC-AC-005.** `vars(RiskEngine())` returns exactly `{'max_drawdown': 0.2, 'max_exposure': 1.0, 'min_exposure': 0.1}`, verified per Section 17's Verification Procedure (IU-002).

**P2-04-SPEC-AC-006.** Two independent `RiskEngine.check()` call sequences over an identical scripted input produce functionally identical output sequences, verified per Section 17 (IU-002).

**P2-04-SPEC-AC-007.** `RiskEngine.check()`'s `state` and `position` parameters remain unmutated across the call, verified by identity/equality comparison (IU-002).

**P2-04-SPEC-AC-008.** A scripted `RUNTIME_FAILURE_EVENT` tick produces functionally identical `drawdown`/`drawdown_ratio`/`risk_allocation_factor` values before and after the tick (IU-002).

**P2-04-SPEC-AC-009.** `CanonicalState().reset()` restores `drawdown`, `drawdown_ratio`, and `risk_allocation_factor` to their documented defaults; `RiskEngine` requires and receives no `reset()` method (IU-002).

**P2-04-SPEC-AC-010.** Full regression re-run (Requirement COMPAT-001) passes, and a future Certification records TD-006's full-closure eligibility, both halves (IU-003).

**P2-04-SPEC-AC-011.** `performance.py` remains byte-for-byte unchanged after every Implementation Unit in this document (IU-003).

**P2-04-SPEC-AC-012.** `git diff --stat` against HEAD `a81e197`, restricted to `run_engine/`, shows only `run_engine/core/risk.py` changed, comment/docstring lines only (Requirement COMPAT-004, IU-001).

**P2-04-SPEC-AC-013.** `python -m compileall run_engine` PASSes after every Implementation Unit (Requirement COMPAT-002).

Specification Readiness Criteria: this Specification is Implementation-ready only when AC-001 through AC-013 are all verified satisfiable by Sections 9 through 20, and when Section 27's Internal Consistency Review and Section 28's Readiness Decision both confirm PASS/READY.

## 22. Implementation Units

Three Implementation Units realize this document's contracts. Each is a logically scoped body of work, not a per-file division; IU-001 is the sole Implementation Unit touching any runtime file, and it touches exactly one.

### P2-04-IU-001 - Risk Ownership Documentation

Ziel (Goal): attach Documentation Contracts (Section 5) to `run_engine/core/risk.py`, recording AD-001's taxonomy, AD-002's Risk Policy Configuration ownership, AD-004's `risk_allocation_factor` ownership, AD-007's Position-derived Exposure non-incorporation disposition, and AD-009's risk-limiting formula retention disposition, directly in the source a future reader encounters, without altering any executable line.

Betroffene Runtime-Komponenten (Affected Runtime Components): `RiskEngine`.

Betroffene Dateien (Affected Files): `run_engine/core/risk.py` (comment/docstring lines only, per Constraint RTC-002).

Abhaengigkeiten (Dependencies): none upstream; this Implementation Unit may proceed independently of IU-002 and IU-003.

Voraussetzungen (Preconditions): Architecture Decisions AD-001, AD-002, AD-004, AD-007, AD-009 are READY (confirmed, Architecture Section 30); `risk.py` remains unchanged at HEAD `a81e197` (confirmed, Section 4).

Acceptance Criteria: P2-04-SPEC-AC-001, AC-002, AC-003, AC-004, AC-012, AC-013 (Section 21).

Testumfang (Test Scope): `python -m compileall run_engine` (confirms the file remains syntactically valid); `git diff --stat` restricted to `run_engine/` (confirms only `risk.py` changed); a line-level diff review confirming every changed line is a comment or docstring, none executable; the full P2-02A/P2-03 regression suite (confirming zero behavioral change, since none was made).

### P2-04-IU-002 - RiskEngine Behavioral Re-Verification

Ziel (Goal): independently re-verify, and record as this unit's own individually-named finding, RiskEngine's determinism (AD-011), statelessness (AD-012), read-only consumer boundaries toward Position/Exposure (AD-008) and Equity/Peak-Equity/Position (AD-013), RuntimeFailureEvent non-mutation (AD-014), and reset semantics (AD-015) - properties already true today but not yet individually certified for this unit.

Betroffene Runtime-Komponenten (Affected Runtime Components): `RiskEngine`, `CanonicalState` (verification target only).

Betroffene Dateien (Affected Files): none; this is a Verification-Only Implementation Unit.

Abhaengigkeiten (Dependencies): none upstream; may proceed independently of IU-001, though logically follows it if a single Certification session addresses both.

Voraussetzungen (Preconditions): Architecture Decisions AD-008, AD-011 through AD-015 are READY; `risk.py` and `canonical_state.py` remain unchanged at HEAD `a81e197`, or, if IU-001 has already landed, unchanged beyond IU-001's own comment/docstring-only diff.

Acceptance Criteria: P2-04-SPEC-AC-005, AC-006, AC-007, AC-008, AC-009 (Section 21).

Testumfang (Test Scope): the Verification Procedures specified in Section 17 (Determinism) and Section 18 (Reset), executed against a real `RunLoop`-driven scripted tick sequence, not a mock; a scripted `RUNTIME_FAILURE_EVENT` scenario (over-close or invalid-quantity rejection); `vars()` inspection at initialization, after a multi-tick run, and after the failure-tick scenario.

### P2-04-IU-003 - Compatibility, TD-006 Closure, and Scope-Boundary Verification

Ziel (Goal): execute the full regression suite confirming AD-016's compatibility preservation and AD-003/AD-005's already-conformant Computational-Authority/storage-location lock-ins; confirm `performance.py`'s continued non-consumption of Risk Metrics (AD-017); record TD-006's full-closure eligibility for a future Certification (AD-010).

Betroffene Runtime-Komponenten (Affected Runtime Components): `RiskEngine`, `CanonicalState`, `CanonicalEnforcer`, `RunLoop`, `PerformanceEngine` (all verification targets only).

Betroffene Dateien (Affected Files): none; this is a Verification-Only Implementation Unit.

Abhaengigkeiten (Dependencies): logically follows IU-001 and IU-002, since a meaningful regression re-run and TD-006 closure record should reflect IU-001's own documentation state and IU-002's own re-verified properties, though no HARD technical dependency prevents earlier execution against the pre-IU-001 baseline.

Voraussetzungen (Preconditions): Architecture Decisions AD-003, AD-005, AD-010, AD-016, AD-017 are READY; the P2-03-certified and P2-02A-certified regression scenarios remain available for re-execution.

Acceptance Criteria: P2-04-SPEC-AC-010, AC-011 (Section 21); Requirement COMPAT-001 through COMPAT-004 (Section 20).

Testumfang (Test Scope): the complete P2-03/P2-02A regression suite (the OPEN/HOLD/SCALE_IN/PARTIAL_CLOSE/FULL_CLOSE sequence, the RUNTIME_FAILURE_EVENT scenario, the replay/determinism double-run); a repository-wide search of `performance.py` for `drawdown`, `drawdown_ratio`, `risk_allocation_factor`; `git diff --stat` against HEAD `a81e197` restricted to `run_engine/`.

No Implementation Unit in this document is artificially scoped to a single file where a logical grouping spans more than one concern; conversely, IU-001 is correctly scoped to one file because every Documentation Contract it realizes concerns the identical file and the identical non-behavioral change category.

## 23. Runtime File Inventory

Every file under `run_engine/` bearing any relationship to P2-04's scope, established by the repository-wide search re-run in Section 4.

| File | Relationship to P2-04 | On Active Path |
|---|---|---|
| `run_engine/core/risk.py` | Primary subject; `RiskEngine`'s own definition | Yes |
| `run_engine/core/loop.py` | Invokes `RiskEngine.check`; orchestrates the tick sequence | Yes |
| `run_engine/core/canonical_state.py` | Stores Drawdown, Drawdown Ratio, `risk_allocation_factor` | Yes |
| `run_engine/core/canonical_enforcer.py` | Publishes Risk Metrics via `apply_risk` | Yes |
| `run_engine/core/performance.py` | Confirmed non-consumer of Risk Metrics (AD-017) | Yes |
| `run_engine/core/position.py` | Produces Position-derived Exposure, consumed by `RiskEngine` | Yes (unchanged, P2-02A scope) |
| `run_engine/core/pnl.py` | Produces Equity/Peak-Equity, consumed by `RiskEngine` | Yes (unchanged, P2-03 scope) |
| `run_engine/core/position_sizing.py` | Reads `RiskEngine`'s own un-prefixed return dict | No (confirmed inactive) |
| `run_engine/runtime/risk.py` | Structurally similar, independent, differently-scaled risk computation (`RiskLayer`) | No (confirmed inactive) |
| `run_engine/core/equity_stabilizer.py` | Equity-smoothing, not Risk-Metric-shaped | No (confirmed inactive; not risk-relevant) |

## 24. File-by-File Change Plan

| File | Change Required | Justification | Scope of Change |
|---|---|---|---|
| `run_engine/core/risk.py` | **YES** | IU-001's four Documentation Contracts (AD-002, AD-004, AD-007, AD-009) attach here; this is the sole file any AD requires touching | Comment/docstring lines only, per Constraint RTC-002; zero executable-line change; zero numeric-value change (Constraint RTC-003) |
| `run_engine/core/loop.py` | NO | Contract RB-001 requires the existing six-step risk-relevant sequence to remain exactly as it stands; no AD alters it | not applicable |
| `run_engine/core/canonical_state.py` | NO | Contract CS-001 requires the existing three-key Risk-Metric schema to remain exactly as it stands; AD-002 explicitly forbids adding a Risk Policy Configuration key here | not applicable |
| `run_engine/core/canonical_enforcer.py` | NO | Contract PC-001 requires `apply_risk`'s existing sole-Writer-on-Behalf-Of role to remain unchanged | not applicable |
| `run_engine/core/performance.py` | NO | Contract CC-001 (AD-017) explicitly forbids any Risk-Metric reference being introduced here by this document | not applicable |
| `run_engine/core/position.py` | NO | Out of scope; P2-02A-certified, not reopened (AD-016) | not applicable |
| `run_engine/core/pnl.py` | NO | Out of scope; P2-03-certified, not reopened (AD-016) | not applicable |
| `run_engine/core/trade_lifecycle.py` | NO | Out of scope; P2-02A/P1-adjacent, not reopened (AD-016) | not applicable |
| `run_engine/main.py` | NO | Out of scope; not named by any FR, DEP, CAP, or AD in this unit | not applicable |
| `run_engine/core/position_sizing.py` | NO | Confirmed inactive; repository cleanup out of scope (FRA Section 24) | not applicable |
| `run_engine/runtime/risk.py` | NO | Confirmed inactive; repository cleanup out of scope (FRA Section 24) | not applicable |
| `run_engine/core/equity_stabilizer.py` | NO | Confirmed inactive; not risk-relevant; repository cleanup out of scope | not applicable |

Exactly one file requires a change under this Specification; every other file in the active runtime, and every confirmed-inactive file, requires none.

## 25. No-Change Inventory

Restated explicitly, per the governing task's own requirement, as a positive inventory of files this Specification affirmatively leaves untouched, not merely an absence from Section 24's "YES" column.

**Files explicitly confirmed unchanged by every Implementation Unit in this document:** `run_engine/core/loop.py`, `run_engine/core/canonical_state.py`, `run_engine/core/canonical_enforcer.py`, `run_engine/core/performance.py`, `run_engine/core/position.py`, `run_engine/core/pnl.py`, `run_engine/core/trade_lifecycle.py`, `run_engine/core/state.py`, `run_engine/core/regime.py`, `run_engine/core/strategy.py`, `run_engine/core/execution/executor.py`, `run_engine/main.py`.

**Confirmed-inactive files explicitly confirmed unchanged, their classification not revisited by this document:** `run_engine/core/position_sizing.py`, `run_engine/runtime/risk.py`, `run_engine/core/equity_stabilizer.py`, and every other file under `run_engine/runtime/`, `run_engine/execution/`, `run_engine/feedback/`, `run_engine/logging/` not already named above.

**Non-runtime artifacts explicitly confirmed unchanged:** every file under `docs/`, `_chat_handover/`, `_sgf017_context/`, `_ssi_context/`, `backups/`, `claude_*_review/`, `codex_p1_03_review/`, `live_logs/`, `outputs/`, `review_packages/`, `runtime_runs/`, and `engine/regime_classifier.py` - all pre-existing, unrelated working-tree entries this document does not touch (Section 4).

No Technical Debt Register file edit is authorized by this document; AD-010's TD-006 disposition is recorded by IU-003 as a finding for a future Certification to action, consistent with every prior unit's own practice.

## 26. Traceability

### 26.1 FR to Specification

| FR | Specification Coverage |
|---|---|
| FR-001 | Section 14 (Risk Policy Configuration Contracts), Contract RP-003, IU-001 |
| FR-002 | Contract RC-001, RE-003 (already conformant, ratified) |
| FR-003 | Section 10 (`risk_allocation_factor` naming), Contract PC-001, IU-001 |
| FR-004 | Section 10 (Contract CS-001, CS-002) |
| FR-005 | Section 15 (Exposure Contracts), Contract EX-002, EX-003, IU-001 |
| FR-006 | Contract RE-004, RC-006 (already conformant, ratified) |
| FR-007 | Section 15/16 formula retention, Contract RC-004, IU-001 |
| FR-008 | IU-003, Requirement COMPAT-001/AC-010 |
| FR-009 | Section 17 (Determinism Requirements), IU-002 |
| FR-010 | Section 17, Contract RE-001, IU-002 |
| FR-011 | Contract RE-004, RC-006 (already conformant, ratified) |
| FR-012 | Contract RC-007, IU-002 |
| FR-013 | Section 18 (Reset Requirements), IU-002 |
| FR-014 | Contract RC-008, Section 19-20, IU-003 |
| FR-015 | Contract CC-001, IU-003 |

### 26.2 SDA Dependency to Specification

All sixteen SDA dependency records are honored by this Specification's own contract and Implementation Unit structure: DEP-001/DEP-002 (Contract CS-002 preserves the already-conformant storage AD-004's naming decision is bound by); DEP-003 (Contract RE-004 preserves AD-008's boundary unconditionally of AD-007's disposition); DEP-004 (Section 15's Contract EX-002 records the resolved, moot status); DEP-005 (IU-003's dependency on IU-001/IU-002 reflects AD-009-before-AD-010 sequencing); DEP-006/DEP-007 (acknowledged, non-blocking, as in the Architecture); DEP-008 (IU-001's and IU-002's shared grounding in AD-002 reflects this); DEP-009 (Contract RE-005/RE-001 constrain Section 15's contracts); DEP-010 (Contract RE-004 constrains Section 15); DEP-011 (Contract RC-007 constrains Section 15); DEP-012 (Contract RC-008 applies to every Section); DEP-013 (Contract CC-001 constrains Sections 10-16); DEP-014 (IU-003's TD-006 finding); DEP-015 (Contract RC-001 constrains formula contracts); DEP-016 (Section 18's RST-003 cites Section 17's RE-001 evidence directly).

### 26.3 CGA Capability to Specification

| CAP | Specification Coverage |
|---|---|
| CAP-001 | Section 14, IU-001 |
| CAP-002 | Section 11 (Contract RE-003, ratified) |
| CAP-003 | Section 10-11 (Contract PC-001), IU-001 |
| CAP-004 | Section 10 (Contract CS-001), ratified |
| CAP-005 | Section 15, IU-001 |
| CAP-006 | Contract RE-004, ratified |
| CAP-007 | Section 15-16, IU-001 |
| CAP-008 | IU-003 |
| CAP-009 | Section 17, IU-002 |
| CAP-010 | Section 17, IU-002 |
| CAP-011 | Contract RE-004, ratified |
| CAP-012 | Contract RC-007, IU-002 |
| CAP-013 | Section 18, IU-002 |
| CAP-014 | Section 19-20, IU-003 |
| CAP-015 | Contract CC-001, IU-003 |

### 26.4 Architecture Decision to Specification

| AD | Specification Section(s) | Implementation Unit |
|---|---|---|
| AD-001 | Section 5 (Normative Terminology, inherited) | none (already fully satisfied by Architecture text) |
| AD-002 | Section 14, Contract RC-002, RP-001 through RP-003 | IU-001 |
| AD-003 | Section 11, Contract RE-003 | none (ratified, IU-003 re-verifies) |
| AD-004 | Section 10-12, Contract PC-001 | IU-001 |
| AD-005 | Section 10, Contract CS-001 through CS-003 | none (ratified, IU-003 re-verifies) |
| AD-006 | Section 14 (Contract RP-002), Section 23 | none (closure statement) |
| AD-007 | Section 15, Contract EX-001 through EX-003 | IU-001 |
| AD-008 | Section 11 (Contract RE-002, RE-004) | none (ratified, IU-002 re-verifies) |
| AD-009 | Section 15-16, Contract RC-004 | IU-001 |
| AD-010 | Section 25 (Technical Debt disposition) | IU-003 |
| AD-011 | Section 17 (Contract RE-005) | none (ratified, IU-002 re-verifies) |
| AD-012 | Section 17 (Contract RE-001), Section 18 (RST-001) | none (ratified, IU-002 re-verifies) |
| AD-013 | Section 11 (Contract RE-004), Section 13 | none (ratified, IU-002 re-verifies) |
| AD-014 | Contract RC-007 | none (ratified, IU-002 re-verifies) |
| AD-015 | Section 18 (Requirement RST-001 through RST-003) | none (ratified, IU-002 re-verifies) |
| AD-016 | Section 20 (Compatibility Requirements) | IU-003 |
| AD-017 | Section 13 (Contract CC-001) | IU-003 |

All fifteen FRA requirements, all sixteen SDA dependencies, all fifteen CGA capabilities, and all seventeen Architecture Decisions are covered by this Specification; none is left unaddressed.

## 27. Internal Consistency Review

### 27.1 Scientific Consistency Review

Every contract in Sections 9 through 20 traces to a specific AD, FR, DEP, or CAP; no contract introduces a scientific claim absent from those sources. Section 15's Exposure Contracts and Section 16's formula-retention framing were re-checked against the Architecture's own AD-007 and AD-009 text and found consistent, including the "no speculation" evidentiary basis both ADs state. Status: PASS.

### 27.2 Architecture Consistency Review

Every Architecture Decision (AD-001 through AD-017) is addressed by exactly one row in Section 26.4; no Specification contract contradicts an AD's own Decision, Ownership Consequences, or Compatibility Constraints fields, individually re-checked during drafting. Section 19's Runtime Constraints (RTC-001 through RTC-004) directly restate Architecture Constraints C-002 through C-006 at Specification-actionable granularity, introducing no new constraint the Architecture did not already establish. Status: PASS.

### 27.3 Specification Consistency Review

Sections 9 through 20's contracts are internally consistent with each other: Contract RC-002 (Section 9) and Contract RP-003 (Section 14) agree that Risk Policy Configuration is never published; Contract RC-003 (Section 9) and Contract EX-002 (Section 15) agree that `position_exposure` never participates in the formula; Contract RC-004 (Section 9) and Section 16's Runtime Behaviour agree the six-step sequence and the formula's shape are both unchanged. No contract in Section 10 through 16 is contradicted by any Implementation Unit in Section 22, cross-checked IU by IU during drafting: IU-001's Testumfang exercises exactly the Documentation Contracts Sections 14-15 define; IU-002's exercises exactly Sections 17-18's Requirements; IU-003's exercises exactly Section 20's Requirements. Status: PASS.

### 27.4 Ownership Review

Sections 10 through 13 (CanonicalState, RiskEngine, Publication, Consumption Contracts) maintain the identical four-way separation (Computational Authority, Authoritative Ownership, Publication, Consumption) the Architecture document established, never conflating any two: Section 10 addresses Authoritative Ownership and write-path exclusivity only; Section 11 addresses Computational Authority and read/output contracts only; Section 12 addresses Publication (Writer-on-Behalf-Of) only; Section 13 addresses Consumption only. No contract in this document reassigns any ownership role the Architecture already decided. Status: PASS.

### 27.5 Terminology Review

"Byte-identical" is not used anywhere in this document to describe a Python-object, runtime-dictionary, or numeric comparison; its only appropriate use, "byte-for-byte," is reserved for Requirement COMPAT-003's own genuine source-file-line comparison (the eleven imports in `loop.py`) and Section 22's own file-diff review language, both legitimate file-level comparisons, not runtime-object comparisons. "Functionally identical" is used throughout Sections 17, 20, and 21 wherever a Python-object or runtime-result comparison is specified. "SHALL," "SHALL NOT," and "MAY" are used with exactly the meanings Section 5 establishes, throughout. Status: PASS.

### 27.6 Traceability Review

Section 26's four subsections independently confirm full coverage of all fifteen FRs, all sixteen DEPs, all fifteen CAPs, and all seventeen ADs; cross-checked against Sections 9 through 22 during drafting, with no contract or Implementation Unit found unreferenced by any traceability table. IU-numbering is confirmed sequential and unique: IU-001, IU-002, IU-003, no gap, no duplicate. Status: PASS.

### 27.7 Governance Review

No new Functional Requirement, SDA dependency, CGA capability, or Architecture Decision was created; all references are by existing ID only. No architecture decision was made: every Specification choice in Sections 9 through 20 cites the AD it implements rather than introducing an independent rationale. No Python code, pseudocode, or executable-line change was written anywhere in this document, including within Section 22's Implementation Unit descriptions, which describe Testumfang and Acceptance Criteria, never code. No commit, push, or runtime file modification was made during this document's drafting (Section 4's re-verification, repeated at Section 27.8 below). Status: PASS.

### 27.8 Independent Self Verification

**Repository state, re-verified at the close of drafting:** branch `run-engine-consolidation-safety`; HEAD `a81e1978cb07bbb26223c94a1b24e9220520c445`; `run_engine/` clean; no commit made during this document's drafting; no push made.

**Mechanical checks performed (results recorded from actual command execution):** ASCII and trailing-whitespace scan across the full document; continuous section-numbering check (## 1 through ## 28, no gap, no duplicate); FR/DEP/CAP/AD-ID traceability grep, confirming all fifteen FR IDs, all sixteen DEP IDs, all fifteen CAP IDs, and all seventeen AD IDs referenced; IU-numbering check confirming IU-001 through IU-003 sequential and unique; `python -m compileall run_engine` re-run, confirming zero runtime effect from this documentation-only work; `git diff --check` against the new file; `git status --short run_engine/` confirming no runtime file changed.

**Result:** one issue was found and corrected during this drafting and review pass, disclosed here rather than silently fixed. The initial ASCII scan found six non-ASCII bytes: three occurrences of the German field label "Abhaengigkeiten," used with an "a" umlaut in Section 22's three Implementation Unit entries (mirroring the governing task's own German field name), corrected to its ASCII-safe transliteration without loss of meaning, consistent with the label's own accompanying English gloss, "(Dependencies)." The specific self-referential terminology trap that recurred in the SDA, CGA, and Architecture documents (a Terminology Review sentence claiming a reserved term "does not occur anywhere in this document" while itself containing that term) was avoided in this document's own Section 27.5 by drafting it, from the outset, in the already-corrected form ("is not used anywhere in this document to describe a comparison"), rather than repeating the error a fourth time and correcting it after the fact.

**Status: Independent Self Verification PASS.**

## 28. Specification Readiness Decision

Twenty-nine contracts and requirements (Sections 9 through 20) and three Implementation Units (Section 22) fully translate all seventeen Architecture Decisions into implementable technical directives. Exactly one file (`run_engine/core/risk.py`) requires any change, and that change is limited to comment/docstring content, per this document's own central organizing fact (Section 6): P2-04's Architecture required no runtime behavior change, so this Specification's own implementation surface is documentation-and-verification, not behavior modification.

This Specification is fully consistent with the Architecture document (Section 27.2), makes no new architecture decision (Section 27.7), and maintains complete traceability to all fifteen FRA requirements, sixteen SDA dependencies, fifteen CGA capabilities, and seventeen Architecture Decisions (Section 26).

Readiness: READY. This Specification is sufficient to proceed to the P2-04 Implementation stage, where IU-001 through IU-003 must be executed in the dependency order Section 22 establishes (IU-001 and IU-002 independently, IU-003 following both), each validated against its own Acceptance Criteria and Testumfang before certification. No further Specification-stage investigation is required before that step.

This document stops here, before Implementation, as instructed.
