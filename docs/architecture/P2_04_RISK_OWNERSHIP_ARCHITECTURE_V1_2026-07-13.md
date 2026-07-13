Document Class:
Architecture Decision Document

Document ID:
P2-04-ARCH

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
docs/architecture/P2_04_RISK_OWNERSHIP_ARCHITECTURE_V1_2026-07-13.md

Depends On:
- docs/architecture/analysis/P2_04_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-13.md
- docs/architecture/analysis/P2_04_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-13.md
- docs/architecture/analysis/P2_04_CAPABILITY_GAP_ANALYSIS_V1_2026-07-13.md
- docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md
- docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md
- docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md
- docs/architecture/certification/P2_03_FINAL_CERTIFICATION_V1_2026-07-11.md
- current runtime code at HEAD a81e197

Referenced By:
- future P2-04 Specification
- future P2-04 Implementation
- future P2-04 Certification

---

# P2-04 Risk Ownership Architecture

## 1. Purpose

This document makes the architecture decisions for P2-04 (Risk Ownership), resolving the ownership, formula-disposition, and consumption questions the P2-04 Functional Requirement Analysis (FRA), Scientific Dependency Analysis (SDA), and Capability Gap Analysis (CGA) established but deliberately left open. It decides, for every Risk-adjacent information object in scope, who computes it, who owns it, who may write it on whose behalf, who may read it, whether Position-derived Exposure participates in its computation, and what invariants the resulting design must uphold. It does not specify interfaces, method signatures, file layouts, or code; it does not implement anything; it does not modify any runtime file.

## 2. Scope

In scope: architecture decisions for Risk Policy Configuration (`max_drawdown`, `max_exposure`, `min_exposure`, and the three regime-dampening multipliers), the risk-limiting formula's disposition, `risk_allocation_factor`'s individual ownership assignment, Drawdown and Drawdown Ratio's canonical storage preservation (not their own ownership, already certified by P2-03), Position-derived Exposure's functional disposition inside `RiskEngine`, RiskEngine's determinism and statelessness (ratified as binding), RiskEngine's consumer boundaries toward Equity/Peak-Equity/Position, RuntimeFailureEvent non-mutation for Risk Metrics, Risk Policy Configuration's reset semantics, TD-006's remaining risk-formula-half closure, and the scope boundary between P2-04 and P3-03 for `PerformanceEngine`'s Risk-Metric consumption.

Out of scope, unchanged from the FRA (Section 24), SDA (Section 2), and CGA (Section 2): Drawdown and Drawdown Ratio's own Computational Authority, Authoritative Owner, and formula (fully certified by P2-03, not reopened here except as a compatibility-preservation constraint), full `PerformanceEngine` redesign or its consumption of Risk Metrics (P3-03), `PositionSizingEngine` activation, Position/Exposure ownership itself (P2-02A, certified), Persistence and Recovery (ADR-012), repository cleanup, the automated regression test suite (TD-005), numeric calibration of any Risk Policy Configuration value, and any Specification-level interface shape or Implementation-level code. No decision in this document expands scope beyond what the FRA, SDA, and CGA already established as in scope.

## 3. Binding Baseline

- `docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md` - ADR-004 (Position Represents Current Market Exposure), ADR-006 (Canonical Financial State Ownership, Drawdown clause), ADR-007 (Risk Evaluation as a Pure Computational Layer), ADR-011 (Runtime Failure Handling), the Runtime Ownership Matrix's "Risk Metrics" row, Rules OM-001 through OM-009, Architecture Invariants AI-002, AI-005, AI-010, AI-013, Acceptance Criteria AC-003 and AC-007.
- `docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md` - P2-04's unit definition ("Risk Ownership. Objectives: Verify Risk Metrics ownership. Validate deterministic RiskEngine behaviour.").
- `docs/architecture/analysis/P2_04_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-13.md` - fifteen functional requirements (FR-001 through FR-015), seven Open Questions (OQ-001 through OQ-007), Functional Readiness: READY.
- `docs/architecture/analysis/P2_04_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-13.md` - nine capability clusters, sixteen dependency records (DEP-001 through DEP-016), Open Question classifications, five Dependency Layers, Readiness for Capability Gap Analysis: READY.
- `docs/architecture/analysis/P2_04_CAPABILITY_GAP_ANALYSIS_V1_2026-07-13.md` - fifteen capabilities (CAP-001 through CAP-015), Current-vs-Target Matrix, TD-006 objective analysis, Overall Capability Readiness: READY.
- `docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md` - TD-001 through TD-007, in particular TD-006 (risk-formula half remaining after P2-03's certified closure of its Equity/Peak-Equity/Drawdown-input-source half).
- `docs/architecture/certification/P2_03_FINAL_CERTIFICATION_V1_2026-07-11.md` - the certified baseline this document treats as immutable, HEAD `259a592` through `a81e197`.
- Current runtime code at HEAD `a81e1978cb07bbb26223c94a1b24e9220520c445`, re-verified for this document (Section 5).

## 4. Repository-Grounded Current State

Repository state re-verified for this document: branch `run-engine-consolidation-safety`, HEAD `a81e1978cb07bbb26223c94a1b24e9220520c445`, matching the FRA's, SDA's, and CGA's own verification exactly (`git branch --show-current`, `git rev-parse HEAD`). `run_engine/` remains clean (`git status --short run_engine/` returns no output). The working tree's pre-existing, unrelated modified and untracked entries (`docs/capabilities/SGF_013_SCIENTIFIC_BEHAVIOUR_REPRESENTATION_2026-06-26.md`, `_chat_handover/`, `_sgf017_context/`, `_ssi_context/`, `backups/`, `claude_*_review/`, `codex_p1_03_review/`, `engine/regime_classifier.py`, `live_logs/`, `outputs/`, `review_packages/`, `runtime_runs/`, and the untracked P2-02A/P2-03/P2-04 governing documents already present under `docs/architecture/`) are observed, unchanged, and not touched by this document.

A repository-wide search for Risk-Ownership-adjacent terms (`drawdown`, `exposure`, `risk_allocation`, `RiskEngine`, `RiskLayer`, `CanonicalState`, case-insensitive) under `run_engine/` was re-run for this document and returned the identical six files the FRA, SDA, and CGA already established (`run_engine/core/risk.py`, `run_engine/core/loop.py`, `run_engine/core/canonical_state.py`, `run_engine/core/position.py`, `run_engine/core/position_sizing.py`, `run_engine/runtime/risk.py`); no new file, no new match, and no repository drift was found.

This document relies on the FRA's Sections 6 through 23, the SDA's Sections 7 through 26, and the CGA's Sections 6 through 20 without re-deriving their findings from the code a second time. The CGA's own central finding (CGA Section 5, restated in Section 20 of that document) governs this document's starting position: nine of fifteen capabilities are already COMPLETE; three (CAP-005, CAP-007, CAP-008) are MISSING as decision-artifact capabilities, not as absent runtime objects, built atop already-functioning, already-correct mechanical scaffolding; three (CAP-001, CAP-003, CAP-013) are PARTIAL, in every case because the underlying mechanism already exists and works correctly and only an ADR-level ownership-naming decision or a downstream, conditionally-gated determination remains. No capability was found to violate any Architecture Invariant, Acceptance Criterion, or Runtime Ownership Matrix row (CGA Section 8); this document's task is therefore overwhelmingly one of explicit naming and explicit disposition, not defect correction.

`run_engine/core/risk.py` (55 lines), `run_engine/core/canonical_state.py`, and `run_engine/core/canonical_enforcer.py` were re-read in full for this document and found unchanged from the versions the FRA, SDA, and CGA each independently verified.

## 5. Scientific Definitions

These definitions restate, consolidate, and where the FRA/SDA/CGA left a category undefined, complete the taxonomy of Risk-adjacent information categories this document's decisions operate on. None contradicts or redefines the FRA's own Section 5; each is either inherited unchanged or explicitly completed here for the first time, marked as such.

**Risk Metric** - per ADR-007: "a derived quantity calculated from canonical runtime state," not "a primary runtime entity." In P2-04's confirmed scope, exactly three objects qualify: Drawdown, Drawdown Ratio, and `risk_allocation_factor` (Section 9, AD-006). A Risk Metric is always computed from already-canonical inputs and is always itself published to `CanonicalState`.

**Risk Policy Configuration** - the set of threshold and multiplier values (`max_drawdown`, `max_exposure`, `min_exposure`, and the three regime-dampening multipliers) that parameterize the risk-limiting computation producing `risk_allocation_factor`. Unlike a Risk Metric, a Risk Policy Configuration value is not computed from canonical runtime state; it is a fixed, `__init__`-time or inline-literal declaration that does not vary tick-to-tick, evolve with market conditions, or depend on any other runtime information object. This document completes this category's definition for the first time at the ADR level (Section 9, AD-001, AD-002).

**Position-Derived Exposure** - per ADR-004, the signed market value of the current Position (`Position.exposure`), owned by `PositionEngine`/`CanonicalState` (P2-02A, certified, unchanged). Distinct from `risk_allocation_factor`; the naming collision between the two was already resolved by P2-02A-AD-007.

**Financial State** - as defined and fully certified by P2-03 (Realized PnL event and cumulative, Equity, Peak Equity); not redefined here, not reopened by any decision in this document.

**Performance Metric** - per ADR-008, a statistic derived from completed lifecycle outcomes, owned by `PerformanceEngine`. Distinct from a Risk Metric: a Performance Metric evaluates realized trading outcomes; a Risk Metric evaluates current runtime risk exposure. Neither category currently reads the other (CGA CAP-015, confirmed unchanged in Section 4 above).

**RiskEngine Determinism** - per AI-005 and ADR-007, the property that `RiskEngine.check(state, position, regime)` returns identical output for identical input, with no dependency on call history, wall-clock time, or any other non-explicit input. Ratified as a binding invariant by this document (Section 9, AD-011, AD-012), not merely observed.

**Functional Disposition** - a governance-chain decision record, distinct in kind from a runtime information object, that resolves whether and how a mechanically-available input (here, `position_exposure`) participates in a computation. A Functional Disposition decision is itself an architecture decision, not a runtime value; once made, it becomes binding on all subsequent Specification and Implementation stages unless explicitly superseded through an Architecture Evolution Review.

## 6. Architecture Problem Statement

Six distinct problems, established by the FRA (its Section 13) and confirmed unresolved by the SDA and CGA, are resolved by this document:

**Problem 1 - Risk Policy Configuration has no ADR-level Authoritative Owner or Computational Authority (FRA Gap 1, CGA CAP-001).** The six values governing the risk-limiting computation exist and function correctly but are named by no ADR, Scientific Definition, or Runtime Ownership Matrix row.

**Problem 2 - `risk_allocation_factor` is not individually named by any ADR (FRA Gap 2, CGA CAP-003).** Unlike Drawdown and Drawdown Ratio, both now individually assigned by P2-03-AD-006/AD-007, `risk_allocation_factor` is covered only by the Runtime Ownership Matrix's general "Risk Metrics" row.

**Problem 3 - Position-derived Exposure is read but has no recorded functional disposition (FRA Gap 3, CGA CAP-005).** `position_exposure` is read at `risk.py:10` and never referenced again; P2-02A-AD-008 explicitly deferred this exact decision to this unit.

**Problem 4 - The risk-limiting formula has never been formally evaluated (FRA Gap 4, CGA CAP-007).** The drawdown-ratio threshold check and regime-dampening multipliers function correctly but carry no recorded retain-or-revise disposition.

**Problem 5 - TD-006's risk-formula half remains open (FRA Gap 4, CGA CAP-008).** P2-03-AD-015 explicitly named this unit as the closure venue; no disposition has yet been recorded.

**Problem 6 - RiskEngine's determinism has not been individually, separately ratified as its own named architectural finding (FRA Gap 5, CGA CAP-009/CAP-010).** P2-03's certification verified statelessness and, incidentally, output-level determinism as byproducts of its own Financial Ownership scope; no P2-04-specific ratification exists.

## 7. Architecture Objectives

This document's decisions (Section 9) jointly pursue the following objectives, each directly traceable to P2-04's Baseline unit definition ("Verify Risk Metrics ownership. Validate deterministic RiskEngine behaviour."):

- Establish Risk Policy Configuration as an explicitly named, explicitly owned architectural category, distinct from Risk Metric, Financial State, and Position-derived Exposure.
- Complete the individual ADR-level naming of every Risk Metric in P2-04's confirmed scope, closing the asymmetry between `risk_allocation_factor` and the already-named Drawdown/Drawdown Ratio.
- Record an explicit, evidence-grounded disposition for Position-derived Exposure's role inside the risk-limiting computation, resolving Gap 3 without speculative formula invention.
- Record an explicit, evidence-grounded disposition for the risk-limiting formula itself, resolving Gap 4 and, jointly, TD-006's remaining scope.
- Ratify RiskEngine's determinism and statelessness as binding architectural invariants, not merely observed facts.
- Preserve every already-certified P2-03 and P2-02A contract without exception, reopening none of them.
- Leave the PerformanceEngine/Risk-Metric consumption boundary question (Gap 6) explicitly and correctly unresolved, as external, deferred territory this document protects rather than closes.

## 8. Architecture Decisions

Seventeen Architecture Decision Records (P2-04-AD-001 through P2-04-AD-017) resolve every open capability the CGA identified (CAP-001, CAP-003, CAP-005, CAP-007, CAP-008, CAP-013) and formally ratify every already-COMPLETE capability (CAP-002, CAP-004, CAP-006, CAP-009, CAP-010, CAP-011, CAP-012, CAP-014, CAP-015) as a binding architectural lock-in, so that no future implementation stage may silently regress an already-conformant property. Full ADs, each with Motivation, Decision, Scientific Justification, Ownership Consequences, Runtime Consequences, Compatibility Constraints, Acceptance Criteria, and Traceability, are recorded in Section 19. Sections 9 through 18 present the resulting Ownership, Publication, Consumption, Exposure-Dependency, Formula, Reset/Determinism, CanonicalState, and Information-Flow models as summaries of what the ADs in Section 19 establish; every claim in Sections 9 through 18 is traceable to a specific AD and is not independently decided in those summary sections.

| AD | Title | Resolves |
|---|---|---|
| AD-001 | Scientific Taxonomy of Risk-Adjacent Information Categories | Architecture Question 6 |
| AD-002 | Risk Policy Configuration Ownership and Composition | FR-001, CAP-001; Questions 1, 3 |
| AD-003 | Risk-Limiting Formula Computational Authority Confirmation | FR-002, CAP-002 |
| AD-004 | `risk_allocation_factor` Individual Ownership Assignment | FR-003, CAP-003; Question 2 |
| AD-005 | Risk Metric Canonical Storage Preservation | FR-004, CAP-004; Questions 2, 9 |
| AD-006 | Confirmation of No Additional Risk Metrics in Scope | Question 2 |
| AD-007 | Position-Derived Exposure Functional Disposition | FR-005, CAP-005; Question 4 |
| AD-008 | RiskEngine Read-Only Boundary Confirmation (Position/Exposure) | FR-006, CAP-006 |
| AD-009 | Risk-Limiting Formula Disposition | FR-007, CAP-007; Question 5 |
| AD-010 | TD-006 Risk-Formula-Half Closure | FR-008, CAP-008; Question 7 |
| AD-011 | RiskEngine Determinism Confirmation | FR-009, CAP-009; Question 8 |
| AD-012 | RiskEngine Statelessness Confirmation | FR-010, CAP-010; Question 8 |
| AD-013 | RiskEngine Consumer Boundary Confirmation (Equity/Peak-Equity/Position) | FR-011, CAP-011 |
| AD-014 | RuntimeFailureEvent Risk-Metric Non-Mutation Confirmation | FR-012, CAP-012 |
| AD-015 | Risk Policy Configuration Reset Semantics | FR-013, CAP-013; Question 8 |
| AD-016 | Risk-Adjacent Compatibility Confirmation | FR-014, CAP-014; Question 9 |
| AD-017 | PerformanceEngine Risk-Metric Consumption Scope Boundary | FR-015, CAP-015 |

Every one of the FRA's fifteen functional requirements, every one of the CGA's fifteen capabilities, and every one of the nine architecture questions the governing task poses are resolved by exactly one AD above; no AD resolves more than one FR (AD-006 and AD-001 are the two ADs not tied to a single FR, grounded instead directly in repository-confirmed CGA findings and the FRA's own Section 5 taxonomy gap, respectively).

## 9. Risk Ownership Model

| Information Object | Authoritative Owner | Established By |
|---|---|---|
| Risk Policy Configuration (`max_drawdown`, `max_exposure`, `min_exposure`, three regime multipliers) | `RiskEngine` (private, not published) | AD-002 |
| Drawdown | `CanonicalState` (unchanged, P2-03) | AD-005 |
| Drawdown Ratio | `CanonicalState` (unchanged, P2-03) | AD-005 |
| `risk_allocation_factor` | `CanonicalState` | AD-004, AD-005 |
| Position-derived Exposure | `CanonicalState`, nested in the Position record (unchanged, P2-02A) | AD-007, AD-008 (consumption boundary only; ownership itself not reopened) |
| Equity, Peak Equity | `CanonicalState` (unchanged, P2-03) | AD-013 (consumption boundary only; ownership itself not reopened) |

No object in this table changes Authoritative Owner relative to its already-certified or already-established state; every row either newly and individually names an already-correct assignment (`risk_allocation_factor`, Risk Policy Configuration) or restates an already-certified assignment as a compatibility constraint (Drawdown, Drawdown Ratio, Position-derived Exposure, Equity, Peak Equity).

## 10. Risk Policy Ownership Model

Risk Policy Configuration is architecturally distinct from every other object in Section 9's table: it is not computed from canonical runtime state (disqualifying it from the Risk Metric category, AD-001) and does not vary across ticks (disqualifying it from the Financial State or Position-derived Exposure categories, both of which evolve with runtime events). AD-002 establishes `RiskEngine` as its sole Authoritative Owner and its sole point of definition, explicitly not published to `CanonicalState`, since `CanonicalState`'s own defined purpose (Architecture Baseline, "Runtime Scope Clarification") is to answer "what is true now?" for evolving runtime state, a question Risk Policy Configuration's fixed, non-evolving values do not meaningfully answer. The regime-dampening multipliers are classified as Risk Policy Configuration values for ownership purposes (AD-002), resolving OQ-006, while the structural decision to apply them by regime remains part of the Risk-Limiting Formula (Section 15, AD-009).

## 11. Computational Authority Model

| Risk-Adjacent Object | Computational Authority | Established By |
|---|---|---|
| Drawdown | `RiskEngine` (unchanged, P2-03-AD-006) | AD-005 |
| Drawdown Ratio | `RiskEngine` (unchanged, P2-03-AD-007) | AD-005 |
| `risk_allocation_factor` | `RiskEngine` | AD-003, AD-004 |
| Risk Policy Configuration | not applicable (a declared value, not a computed one) | AD-002 |

`RiskEngine` remains the exclusive Computational Authority for every Risk Metric in P2-04's confirmed scope (Section 9, AD-006); no decision in this document introduces a second Computational Authority for any object, and AD-005/AD-013's Compatibility Constraints explicitly bind every future implementation stage against doing so.

## 12. Publication Model

`CanonicalEnforcer.apply_risk()` remains, unchanged, the sole Writer-on-Behalf-Of publication path for Drawdown, Drawdown Ratio, and `risk_allocation_factor` (AD-004, AD-005), consistent with ADR-001's general Writer-on-Behalf-Of exclusivity decision and already established by every prior certification in this governance chain (P2-03 Final Certification, Section 8). Risk Policy Configuration has no publication path and requires none, since AD-002 establishes it as `RiskEngine`-private, never canonically stored.

## 13. Consumption Model

| Consumer | Reads | Boundary | Established By |
|---|---|---|---|
| `RiskEngine` | canonical Equity, Peak Equity, Position (including Position-derived Exposure) | strictly read-only, no ownership acquisition | AD-008, AD-013 |
| `PerformanceEngine` | none of Drawdown, Drawdown Ratio, `risk_allocation_factor` | scope-protected, not resolved by this document | AD-017 |
| Downstream/external result consumers | the complete Tick-Complete `CanonicalState` snapshot | read-only, unchanged, out of this document's scope | not applicable |

`RiskEngine`'s consumption boundary is unchanged by this document; every boundary named above already exists and is ratified, not newly created, by AD-008 and AD-013.

## 14. Exposure Dependency Model

Position-derived Exposure's consumption by `RiskEngine` (the mechanical read, `position_exposure = position.get("exposure", 0.0)`) is preserved unchanged and satisfies ADR-004's consumption requirement (AD-008). AD-007 establishes that this value does not, and for the duration of this unit's scope shall not, participate in `risk_allocation_factor`'s computation. No information-flow edge exists, or is created by this document, from Position-derived Exposure into any Risk Metric's value. This closes Gap 3 without introducing a new computation, formula term, or data dependency of any kind.

## 15. Risk Formula Architecture

The risk-limiting formula (the drawdown-ratio threshold check against `max_drawdown`, the regime-dampening multiplication, and the final clamp to `[min_exposure, max_exposure]`) is retained in its current structural shape, unrevised, by AD-009. Its two inputs remain exactly `drawdown_ratio` (itself derived from canonical Equity and Peak Equity, unchanged) and `regime`; Position-derived Exposure is not a third input (Section 14, AD-007). This retention is itself the explicit evaluation disposition FR-007 requires; it is not an absence of a decision, and it directly and jointly closes TD-006's remaining risk-formula half (AD-010).

## 16. Reset and Determinism Architecture

`RiskEngine.check()` is ratified as a pure, deterministic function of its three explicit parameters (AD-011); `RiskEngine` is ratified as holding no instance attribute beyond its three Risk Policy Configuration constants, set once at initialization and never mutated (AD-012). Because Risk Policy Configuration remains `RiskEngine`-private (AD-002) and is never mutated after initialization (AD-012), no dedicated reset mechanism is required for it: every fresh `RiskEngine()` instantiation deterministically re-establishes the identical configuration, and no runtime event ever alters it (AD-015). This closes CAP-013/FR-013 completely, using the same "no reset method needed because nothing needs resetting" pattern `CanonicalState.reset()`'s own downstream consumers already rely on for `RiskEngine`'s existing statelessness.

## 17. CanonicalState Integration

`CanonicalState`'s schema is unchanged by this document: no new key is added, no existing key is removed or renamed, and no existing key's default value or write mechanism changes. Drawdown, Drawdown Ratio, and `risk_allocation_factor` remain at `canonical_state.py:36,38,40` (defaults) and are written exclusively via `update_risk()` (`canonical_state.py:78-82`), unchanged (AD-005). Risk Policy Configuration gains no `CanonicalState` presence of any kind (AD-002). This document's decisions are therefore entirely ownership-naming and disposition decisions, not schema decisions.

## 18. Runtime Information Flow

The already-certified execution sequence (ADR-010; P2-03 Final Certification, re-confirmed unchanged in Section 4 above) is preserved without modification: `RunLoop.step()` computes Position (including Exposure), then Financial State (Equity, Peak Equity), then invokes `RiskEngine.check(canonical_state, position, regime)`, which reads canonical Equity/Peak-Equity and Position (including Exposure, consumed but not functionally used per AD-007), computes Drawdown, Drawdown Ratio, and `risk_allocation_factor` using only `drawdown_ratio` and `regime` as formula inputs (AD-009), and returns them for atomic publication via `CanonicalEnforcer.apply_risk()`, before `PerformanceEngine` runs (still not consuming any Risk Metric, AD-017). No decision in this document alters this sequence's order, cadence, or the set of components participating in it; every decision concerns ownership and disposition of values already flowing through this unchanged sequence.

## 19. Architecture Decision Records

### P2-04-AD-001 - Scientific Taxonomy of Risk-Adjacent Information Categories

Motivation: the FRA identified (its Section 5) that Risk Policy Configuration has no existing scientific definition anywhere in the Architecture Baseline, and that its relationship to the already-defined categories Risk Metric, Position-derived Exposure, Financial State, and Performance Metric had never been made explicit. Without this taxonomy, every subsequent ownership decision in this document would rest on an undefined categorical foundation.

Decision: five mutually exclusive Risk-adjacent information categories are established. A **Risk Metric** is a derived quantity computed from already-canonical runtime state and always published to `CanonicalState` (Drawdown, Drawdown Ratio, `risk_allocation_factor`, per AD-006). A **Risk Policy Configuration** value is a fixed, non-evolving parameter that governs a Risk Metric's computation without itself being computed from runtime state (`max_drawdown`, `max_exposure`, `min_exposure`, the three regime-dampening multipliers). **Position-derived Exposure** is the signed market value of the current Position, owned by `PositionEngine`/`CanonicalState` (P2-02A, unchanged). **Financial State** is Realized PnL, Equity, and Peak Equity, owned by `PnLEngine`/`CanonicalState` (P2-03, unchanged). A **Performance Metric** is a statistic derived from completed lifecycle outcomes, owned by `PerformanceEngine` (ADR-008, unchanged). No object may belong to more than one category simultaneously.

Scientific Justification: ADR-007 already defines "Risk Metric" generally; ADR-004 already defines Position-derived Exposure; P2-03's own certification already defines Financial State's scope; ADR-008 already defines Performance Metric. The only genuinely new category this decision introduces is Risk Policy Configuration, whose definition is derived directly from repository observation (FRA Section 7: never computed, never published, never varying) rather than invented; the four other categories are restated, not redefined.

Ownership Consequences: establishes the categorical basis on which AD-002 through AD-006 assign ownership; introduces no ownership assignment itself.

Runtime Consequences: none; this is a definitional decision with no code implication of its own.

Compatibility Constraints: this taxonomy must not be read as reopening P2-03's Financial State definition or P2-02A's Position-derived Exposure definition; both are restated verbatim from their own certified sources, not amended.

Acceptance Criteria: every subsequent AD in this document assigns ownership to exactly one of these five categories, never to an object left uncategorized; no object is assigned to more than one category.

Traceability: Related Functional Requirements: none directly (foundational, spans all fifteen). Related Dependency IDs: none directly. Related Capabilities: CAP-001 through CAP-015 (foundational to every one). Related ADR: ADR-004, ADR-006, ADR-007, ADR-008.

### P2-04-AD-002 - Risk Policy Configuration Ownership and Composition

Motivation: FRA Gap 1 and CGA CAP-001 (PARTIAL) establish that `max_drawdown`, `max_exposure`, `min_exposure`, and the three regime-dampening multipliers exist and function correctly but possess no ADR-level Authoritative Owner or Computational Authority. FR-001's own Validation Condition explicitly permits either a published or a private-with-rationale resolution; OQ-001 and OQ-006 remain open on which.

Decision: all six values - `max_drawdown`, `max_exposure`, `min_exposure`, and the three regime-dampening multipliers (currently `0.7` for CHOP, `1.0` for TREND, `0.5` for VOLATILE) - are classified as Risk Policy Configuration (AD-001) for ownership purposes. The four ownership dimensions are decided explicitly and separately: **Authoritative Owner** - `RiskEngine`, exclusively, for Risk Policy Configuration in its entirety. **Computational Authority** - not applicable; Risk Policy Configuration is a declared value, not a computed one, and therefore has no Computational Authority distinct from its Authoritative Owner (Rule OM-002 permits, but does not require, these two roles to differ). **Publication (Writer-on-Behalf-Of)** - none; Risk Policy Configuration is explicitly and permanently **not** published to `CanonicalState`, since it is not "active runtime state" in the Architecture Baseline's own sense (a fixed policy declaration, not a value that evolves tick-to-tick or answers "what is true now?"). **Consumption** - `RiskEngine` itself, exclusively; no consumer outside `RiskEngine` currently reads or requires it. This resolves OQ-001 in favor of the private-with-rationale option and resolves OQ-006 by classifying the regime multipliers' *numeric ownership* under this same category, distinct from their *structural application*, which remains part of the Risk-Limiting Formula (AD-009).

Scientific Justification: ADR-007's general Risk Metric category does not extend to the parameters of a Risk Metric's computation; Rule OM-002 ("Computational Authority may differ from Authoritative Owner") extends here by analogy to a further distinction this document establishes: ownership of a computation's governing parameters is a separate question from ownership of the computation's output. AC-003's "every runtime information object possesses exactly one Computational Authority" is not violated by Risk Policy Configuration lacking one, since AC-003 governs computed objects; a declared value is outside AC-003's own scope by definition, consistent with how the Architecture Baseline treats other fixed declarations (Section 11 restates this as the Computational Authority Model's own explicit "not applicable" entry).

Ownership Consequences: `RiskEngine` becomes the first and only component ever assigned Authoritative Ownership of Risk Policy Configuration; no other component may declare, read canonically, or duplicate these six values without an Architecture Evolution Review.

Runtime Consequences: none required; the current private-literal representation (`risk.py:5-7,37-44`) already satisfies this decision exactly as it stands.

Compatibility Constraints: must not introduce a `CanonicalState` key for any of the six values; must not alter their current numeric values (numeric calibration remains explicitly out of scope, FRA Section 24); must not be read by `PositionSizingEngine` or any other confirmed-inactive component without a future Architecture Evolution Review.

Acceptance Criteria: `vars(RiskEngine())` contains exactly the three named threshold attributes and no others; no `CanonicalState` key exists for any Risk Policy Configuration value; the three regime multipliers remain inline literals within `RiskEngine.check()`'s own body, not relocated to any other component.

Traceability: Related Functional Requirements: FR-001. Related Dependency IDs: DEP-006 (soft, inbound from AD-009's disposition), DEP-008 (outbound, gates AD-015). Related Capabilities: CAP-001. Related ADR: ADR-007, AC-003.

### P2-04-AD-003 - Risk-Limiting Formula Computational Authority Confirmation

Motivation: CGA CAP-002 confirms `RiskEngine` is already the exclusive, correctly-assigned Computational Authority translating Risk Policy Configuration and canonical financial/regime state into `risk_allocation_factor`; FR-002 requires this already-conformant state to be explicitly locked in so it is not silently regressed by any implementation of AD-002, AD-007, or AD-009.

Decision: `RiskEngine` remains, and is hereby ratified as, the exclusive Computational Authority for `risk_allocation_factor`. No future implementation stage may introduce a second component computing this value, in whole or in part.

Scientific Justification: ADR-007, verbatim - "RiskEngine computes derived Risk Metrics." Repository-wide search confirms no other active-path component computes any drawdown-ratio-and-regime-derived scaling value (FRA Section 15).

Ownership Consequences: none change; this decision restates an already-true assignment.

Runtime Consequences: none required.

Compatibility Constraints: any future implementation of AD-007's or AD-009's dispositions must remain inside `RiskEngine`'s own computation; introducing a helper component or a second computation path anywhere else would violate this decision.

Acceptance Criteria: repository-wide search, re-run at Certification time, confirms `RiskEngine` remains the sole computer of `risk_allocation_factor`.

Traceability: Related Functional Requirements: FR-002. Related Dependency IDs: DEP-001 (outbound constraint on AD-004), DEP-015 (outbound constraint on AD-009). Related Capabilities: CAP-002. Related ADR: ADR-007.

### P2-04-AD-004 - `risk_allocation_factor` Individual Ownership Assignment

Motivation: FRA Gap 2 and CGA CAP-003 (PARTIAL) establish that `risk_allocation_factor` is mechanically conformant (computed, stored, published correctly) but covered only by the Runtime Ownership Matrix's general "Risk Metrics" row, never individually named by any ADR - the identical shape of gap Drawdown Ratio had before P2-03-AD-007 resolved it.

Decision: the four ownership dimensions are decided explicitly and separately. **Computational Authority** - `RiskEngine`, designated individually and by name for the first time. **Authoritative Owner** - `CanonicalState`, designated individually and by name for the first time. **Publication (Writer-on-Behalf-Of)** - unchanged, unaffected by this decision; remains `CanonicalEnforcer.apply_risk()`, already governed by AD-005. **Consumption** - unchanged, unaffected by this decision; governed by AD-013 (RiskEngine's own non-consumption of its own output) and AD-017 (`PerformanceEngine`'s scope-protected non-consumption). This closes the naming gap Gap 2 identifies, mirroring P2-03-AD-007's resolution for Drawdown Ratio exactly.

Scientific Justification: `risk_allocation_factor` is computed identically in kind to Drawdown Ratio (both are derived from canonical inputs by `RiskEngine`, in the same method, for the purpose of exposure/risk control), extending ADR-007's Risk Metric category and P2-03-AD-007's own precedent to this object by direct analogy, since no scientific distinction between the two objects' ownership shape was found by the FRA, SDA, or CGA.

Ownership Consequences: `risk_allocation_factor` gains, for the first time, an individually-named Computational Authority and Authoritative Owner, closing the asymmetry with Drawdown and Drawdown Ratio.

Runtime Consequences: none required; the current computation and storage mechanism already satisfies this decision exactly as it stands.

Compatibility Constraints: does not rename `risk_allocation_factor`'s `CanonicalState` key or `RiskEngine`'s own internal `exposure` return-dict key (OQ-007 remains a non-blocking, cosmetic question, not resolved here); does not alter the P2-02A-AD-007 naming separation between this object and Position-derived Exposure.

Acceptance Criteria: `risk_allocation_factor` is henceforth citable, individually, as an ADR-named object in the same manner as Drawdown and Drawdown Ratio; no future document may describe its ownership as "undefined" or "Matrix-row-level only."

Traceability: Related Functional Requirements: FR-003. Related Dependency IDs: DEP-001 (inbound constraint from AD-003), DEP-002 (inbound constraint from AD-005), DEP-007 (soft, inbound from AD-009). Related Capabilities: CAP-003. Related ADR: ADR-007.

### P2-04-AD-005 - Risk Metric Canonical Storage Preservation

Motivation: FR-004 and CGA CAP-004 (COMPLETE) require explicit confirmation that `CanonicalState` remains the exclusive Authoritative Owner (storage location) of Drawdown, Drawdown Ratio, and `risk_allocation_factor`, at the general Runtime Ownership Matrix level, so that AD-004's individual-naming act (which concerns `risk_allocation_factor` only) is not mistaken for, or does not inadvertently trigger, a storage-location change for any of the three.

Decision: `CanonicalState` remains the exclusive Authoritative Owner of Drawdown, Drawdown Ratio, and `risk_allocation_factor`. Drawdown and Drawdown Ratio's own Computational Authority, Authoritative Owner, and formula remain exactly as P2-03-AD-006 and P2-03-AD-007 certified them; neither is reopened, reconsidered, or re-derived by this document in any respect.

Scientific Justification: ADR-006 (Drawdown), P2-03-AD-007 (Drawdown Ratio), and AD-004 above (`risk_allocation_factor`) already establish `CanonicalState` as Authoritative Owner for all three; Rule OM-006 ("CanonicalState exclusively owns active runtime state") is directly honored.

Ownership Consequences: none change for any of the three objects; this decision is purely a compatibility-preservation lock-in.

Runtime Consequences: none required; `canonical_state.py:36,38,40,78-82` already satisfies this decision exactly as it stands.

Compatibility Constraints: this decision explicitly forbids any future Specification or Implementation stage from relocating, renaming, or restructuring any of the three storage locations without an Architecture Evolution Review; P2-03's own certified formula and input source for Drawdown and Drawdown Ratio remain untouched, satisfying the governing task's explicit instruction not to reopen P2-03-certified Financial Ownership.

Acceptance Criteria: `CanonicalState.state["drawdown"]`, `state["drawdown_ratio"]`, and `state["risk_allocation_factor"]` remain the sole storage locations after any future implementation of AD-002, AD-004, AD-007, or AD-009.

Traceability: Related Functional Requirements: FR-004. Related Dependency IDs: DEP-002 (outbound constraint on AD-004). Related Capabilities: CAP-004. Related ADR: ADR-006, Rule OM-006.

### P2-04-AD-006 - Confirmation of No Additional Risk Metrics in Scope

Motivation: the governing task's Architecture Question 2 explicitly asks for any further Risk Metrics confirmed within the current scope; this must be answered explicitly, not left to silent inference from the absence of a fourth entry in Section 9's table.

Decision: exactly three Risk Metrics exist in P2-04's confirmed scope: Drawdown, Drawdown Ratio, and `risk_allocation_factor`. No fourth Risk Metric was found, and none is introduced by this document.

Scientific Justification: the FRA's, SDA's, and CGA's own repository-wide searches (each independently re-run and re-confirmed in Section 4 above) found no other object in the active runtime meeting AD-001's Risk Metric definition (a derived quantity computed from canonical runtime state and published to `CanonicalState`). The confirmed-inactive `RiskLayer` (`run_engine/runtime/risk.py`) computes analogous-looking values under different names and different numeric scale but is not on the active path and is not a Risk Metric within this document's scope by construction (AD-001's definition applies only to the active runtime).

Ownership Consequences: none; this is a closure statement, not an assignment.

Runtime Consequences: none.

Compatibility Constraints: if a future unit activates `RiskLayer` or introduces a new derived risk-adjacent value, that unit's own Architecture Evolution Review must independently classify it against AD-001's taxonomy; this decision does not pre-classify any not-yet-existing object.

Acceptance Criteria: any future claim that a fourth Risk Metric exists in the active runtime at HEAD `a81e197` or any unchanged successor commit is falsifiable against this decision's own repository-wide search evidence.

Traceability: Related Functional Requirements: none directly (closure statement). Related Dependency IDs: none directly. Related Capabilities: CAP-002, CAP-003, CAP-004 (confirms their scope is exhaustive). Related ADR: ADR-007.

### P2-04-AD-007 - Position-Derived Exposure Functional Disposition

Motivation: FRA Gap 3 and CGA CAP-005 (MISSING) establish that `position_exposure` is read at `risk.py:10` and never referenced again; P2-02A-AD-008 explicitly deferred the functional-use decision to this unit, offering two options: (a) confirmed permanent read-only non-use, or (b) functional incorporation.

Decision: Position-derived Exposure is **not** functionally incorporated into `risk_allocation_factor`'s computation, for the duration of this Architecture's scope. `RiskEngine`'s existing read of `position_exposure` is retained exactly as it stands today, satisfying ADR-004's consumption requirement mechanically; the risk-limiting computation's inputs remain exactly `drawdown_ratio` and `regime` (AD-009). This resolves FR-005 in favor of option (a), makes OQ-002 (the intended exposure-to-formula relationship) moot for this unit, and closes Gap 3.

Scientific Justification: no governing document in this chain - not ADR-004, not the FRA, not the SDA, not the CGA - establishes a scientific or risk-management requirement mandating that `risk_allocation_factor` depend on current market exposure; ADR-004's own text requires only that RiskEngine "consume" Position-derived Exposure, which the existing mechanical read already and fully satisfies. Introducing a specific exposure-aware formula term now, absent such a requirement, would constitute speculative formula design at the Architecture stage, directly contrary to this document's own governing quality rule against decisions unsupported by evidence ("keine Spekulation"). Absent evidence favoring incorporation, the minimal, already-evidenced disposition - confirmed non-use - is the scientifically defensible choice.

Ownership Consequences: none; Position-derived Exposure's own ownership (`PositionEngine`/`CanonicalState`, P2-02A) is entirely unaffected and not reopened.

Runtime Consequences: none required; the current read-but-unused shape (`risk.py:10`) already satisfies this decision exactly as it stands, and requires no code change.

Compatibility Constraints: this decision does not remove the `position_exposure` read, since ADR-004's consumption requirement and P2-02A-AD-008's own boundary remain binding; it only forecloses functional use for this unit's scope. A future unit may reopen this decision only through an explicit Architecture Evolution Review grounded in a newly-identified scientific or business requirement, not through incidental formula revision.

Acceptance Criteria: `risk_allocation_factor`'s computed value remains provably independent of `position_exposure` for any given `drawdown_ratio`/`regime` pair, verifiable by direct inspection of the formula's two remaining inputs (AD-009).

Traceability: Related Functional Requirements: FR-005. Related Dependency IDs: DEP-003 (inbound constraint from AD-008), DEP-004 (outbound, makes AD-009's position-exposure dimension moot), DEP-009, DEP-010, DEP-011 (inbound constraints from AD-011/AD-012/AD-013/AD-014). Related Capabilities: CAP-005. Related ADR: ADR-004, ADR-007.

### P2-04-AD-008 - RiskEngine Read-Only Boundary Confirmation (Position/Exposure)

Motivation: FR-006 and CGA CAP-006 (COMPLETE) require explicit confirmation that `RiskEngine` remains a strictly read-only consumer of Position-derived Exposure, never acquiring ownership of Position or Exposure in any form, regardless of AD-007's disposition.

Decision: `RiskEngine` remains, and is hereby ratified as, a strictly read-only consumer of Position-derived Exposure. It shall never mutate its `position` parameter, never cache `position_exposure` across calls, and never introduce an instance attribute or canonical key named `exposure` or `position`.

Scientific Justification: ADR-004 - "RiskEngine SHALL never maintain an independent canonical Exposure representation"; ADR-007 - "RiskEngine SHALL never own: ... Exposure"; Rule OM-007 - "RiskEngine owns no runtime information." Already certified by P2-02A (P2-02A-AD-008) and re-confirmed unchanged in Section 4 above.

Ownership Consequences: none change; Position and Exposure's own ownership remains exclusively `PositionEngine`/`CanonicalState`.

Runtime Consequences: none required.

Compatibility Constraints: binds AD-007's own disposition - even if a future Architecture Evolution Review revisits AD-007 toward functional incorporation, any resulting implementation must remain read-only in the sense this decision defines; caching, mutation, or republication under an owning name would violate this decision independently of AD-007's own status.

Acceptance Criteria: direct code inspection confirms no mutation of `position` anywhere in `RiskEngine.check()`'s body, at any future Certification.

Traceability: Related Functional Requirements: FR-006. Related Dependency IDs: DEP-003 (outbound constraint on AD-007). Related Capabilities: CAP-006. Related ADR: ADR-004, ADR-007, Rule OM-007.

### P2-04-AD-009 - Risk-Limiting Formula Disposition

Motivation: FRA Gap 4 and CGA CAP-007 (MISSING) establish that the drawdown-ratio threshold check and regime-dampening multipliers function correctly but have never been formally evaluated for retention or revision, as FR-007 requires; OQ-003 asks whether the current binary-step shape is scientifically intended or should become continuous.

Decision: the risk-limiting formula is **retained** in its current structural shape: a binary threshold check (drop to `min_exposure` when `drawdown_ratio > max_drawdown`, otherwise remain at `max_exposure`), followed by multiplication by a regime-dependent dampening multiplier (AD-002's Risk Policy Configuration values), followed by a clamp to `[min_exposure, max_exposure]`. No revision to this structure is made or required by this Architecture. This resolves FR-007 in favor of explicit retention, closes Gap 4, makes OQ-003 moot for this unit, and, jointly with AD-002's Risk Policy Configuration ownership decision, constitutes this document's closure of TD-006's remaining risk-formula half (AD-010).

Scientific Justification: AI-005 and AI-010 require that any retained or revised formula remain deterministic and internally consistent; the current formula already satisfies both (AD-011, AD-012), so retention introduces no invariant risk. No governing document - not ADR-007, not the FRA, not the SDA, not the CGA - establishes a scientific or business requirement mandating a continuous function in place of the current step function; absent such a requirement, revising the formula now would be speculative formula design, the identical reasoning AD-007 already applies to Position-derived Exposure's non-incorporation. Retention, with this explicit, recorded rationale, is itself the "explicit evaluation... with recorded rationale" FR-007's own text requires as one of its two permitted outcomes.

Ownership Consequences: none change; AD-002's and AD-003's ownership assignments for the formula's inputs and output are unaffected.

Runtime Consequences: none required; the current formula (`risk.py:31-47`) already satisfies this decision exactly as it stands.

Compatibility Constraints: this decision does not evaluate or endorse the specific numeric values (`0.2`, `1.0`, `0.1`, `0.7`, `0.5`) as scientifically optimal, only the formula's structural shape as architecturally acceptable; numeric calibration remains explicitly out of scope (FRA Section 24) and may be revisited independently of this decision without requiring an Architecture Evolution Review, since AD-002 already establishes `RiskEngine` as sole owner of those specific values.

Acceptance Criteria: `risk.py`'s risk-limiting computation (lines 31-47 at HEAD `a81e197`) remains structurally unchanged at any future Certification unless an explicit Architecture Evolution Review supersedes this decision.

Traceability: Related Functional Requirements: FR-007. Related Dependency IDs: DEP-004 (inbound, conditional from AD-007), DEP-005 (outbound, HARD, enables AD-010), DEP-006, DEP-007 (outbound, soft, informs AD-002/AD-004), DEP-009, DEP-011 (inbound constraints from AD-011/AD-012/AD-014), DEP-014 (external, TD-006). Related Capabilities: CAP-007. Related ADR: ADR-007, AI-005, AI-010.

### P2-04-AD-010 - TD-006 Risk-Formula-Half Closure

Motivation: FR-008 and CGA CAP-008 (MISSING) require explicit closure or explicit, justified re-deferral of TD-006's remaining risk-formula half, per P2-03-AD-015's explicit naming of this unit as the closure venue.

Decision: TD-006's remaining risk-formula half is **closed**. AD-002 establishes explicit, ADR-level ownership for the Risk Policy Configuration values (`max_exposure`, `min_exposure`, `max_drawdown`, and the regime-dampening multipliers) P2-03-AD-015 named as this unit's remaining territory (`run_engine/core/risk.py:5-7,33-49`); AD-009 establishes an explicit, recorded evaluation disposition (retention) for the formula that uses them. Together, these two decisions supply the disposition TD-006's Register entry has awaited since P2-03's own certified closure of its Equity/Peak-Equity/Drawdown-input-source half.

Scientific Justification: TD-006's own recorded Register description ("RiskEngine independently maintains peak equity and computes drawdown instead of consuming the CanonicalState-owned values, creating duplicate ownership") named a duplicate-ownership defect; P2-03 already eliminated that defect for Equity, Peak Equity, and Drawdown's input source. The remaining scope P2-03-AD-015 carved out explicitly concerned the risk-limiting formula's own ownership and disposition, not a further duplicate-ownership defect - no second Computational Authority for the formula's threshold/multiplier values or its output was ever found by the FRA, SDA, or CGA (AD-003, AD-006). Closure therefore consists of explicit naming (AD-002) and explicit evaluation (AD-009), not defect correction.

Ownership Consequences: TD-006's remaining scope, as bounded by P2-03-AD-015, is fully addressed by AD-002 and AD-009 jointly; no ownership assignment changes as a result of this decision beyond what those two ADs already establish.

Runtime Consequences: none required.

Compatibility Constraints: this closure applies only to the risk-formula half P2-03-AD-015 named; it does not reopen or re-certify P2-03's own already-closed Equity/Peak-Equity/Drawdown-input-source half, and it makes no claim about any TD-006-adjacent matter outside that explicitly bounded scope.

Acceptance Criteria: a future P2-04 Certification records TD-006's Register-status update recommendation (from "Deferred" to a closed status for its full scope, both halves), following the same practice P2-03's own Final Certification established (recording the finding, not editing the Register directly).

Traceability: Related Functional Requirements: FR-008. Related Dependency IDs: DEP-005 (inbound, HARD, from AD-009), DEP-014 (external, TD-006 itself). Related Capabilities: CAP-008. Related ADR: ADR-006, ADR-007.

### P2-04-AD-011 - RiskEngine Determinism Confirmation

Motivation: FR-009 and CGA CAP-009 (COMPLETE) require that RiskEngine's determinism, already observed and partially certified as a byproduct of P2-03's own Financial Ownership scope, be ratified as its own, independently and individually named, binding architectural finding for this unit, per P2-04's own Baseline objective ("Validate deterministic RiskEngine behaviour").

Decision: `RiskEngine.check(state, position, regime)` is ratified as, and shall remain, a pure, deterministic function of its three explicit parameters. No future implementation stage, including any implementation of AD-007's or AD-009's dispositions, may introduce persisted instance state, randomness, wall-clock dependence, or any other non-explicit input contributing to `check()`'s output.

Scientific Justification: AI-005 - "Identical runtime inputs SHALL produce identical runtime outputs... Deterministic behaviour shall not depend upon hidden mutable state." Already confirmed by direct code inspection (FRA Section 19) and by P2-03 Final Certification Sections 10, 18, and 19 (statelessness across initialization, a 50-tick run, a lifecycle run, a failure-tick run, and output-level determinism across independent full-system replay runs).

Ownership Consequences: none; this is a behavioral ratification, not an ownership assignment.

Runtime Consequences: none required; already satisfied.

Compatibility Constraints: binds every other AD in this document - AD-002, AD-007, and AD-009 all explicitly preserve this property as a condition of their own Compatibility Constraints.

Acceptance Criteria: two independent calls to `check()` with identical `state`/`position`/`regime` arguments produce functionally identical returned dicts, re-verified independently at any future Certification rather than solely inherited from P2-03's.

Traceability: Related Functional Requirements: FR-009. Related Dependency IDs: DEP-009 (outbound constraint on AD-007/AD-009). Related Capabilities: CAP-009. Related ADR: AI-005, ADR-007.

### P2-04-AD-012 - RiskEngine Statelessness Confirmation

Motivation: FR-010 and CGA CAP-010 (COMPLETE) require that RiskEngine's statelessness - no instance attribute beyond its three Risk Policy Configuration constants - be ratified as a binding invariant, directly enabling AD-015's reset-semantics decision.

Decision: `RiskEngine` shall hold no instance attribute beyond `max_drawdown`, `max_exposure`, and `min_exposure`, each set once at initialization and never mutated thereafter. No future implementation stage may reintroduce a persisted, cross-tick instance attribute of any kind, including a "transient" one retained beyond a single `check()` call.

Scientific Justification: Rule OM-007 - "RiskEngine owns no runtime information. RiskEngine computes derived quantities only." Already confirmed by direct code inspection and by P2-03 Final Certification Section 10's `vars()`-based checks (initialization, 50-tick run, lifecycle run, failure-tick run, all showing the identical three-attribute set).

Ownership Consequences: confirms Rule OM-007's compliance is permanent, not incidental.

Runtime Consequences: none required; already satisfied. Directly enables AD-015's determination that no reset mechanism is required for Risk Policy Configuration.

Compatibility Constraints: binds AD-007 and AD-009 identically to AD-011's own Compatibility Constraints; any future functional incorporation of Position-derived Exposure or revision of the risk-limiting formula (were either ever to be reopened via Architecture Evolution Review) must preserve this property.

Acceptance Criteria: `vars(RiskEngine())` returns exactly `{'max_drawdown': 0.2, 'max_exposure': 1.0, 'min_exposure': 0.1}` before and after any sequence of `check()` calls, re-verified independently at any future Certification.

Traceability: Related Functional Requirements: FR-010. Related Dependency IDs: DEP-009 (outbound constraint), DEP-016 (outbound, informs AD-015). Related Capabilities: CAP-010. Related ADR: ADR-007, Rule OM-007.

### P2-04-AD-013 - RiskEngine Consumer Boundary Confirmation (Equity/Peak-Equity/Position)

Motivation: FR-011 and CGA CAP-011 (COMPLETE) require explicit confirmation that `RiskEngine` remains a strictly read-only consumer of canonical Equity, Peak Equity, and Position collectively - a broader boundary than AD-008's Position/Exposure-specific one, already certified by P2-03 for Equity/Peak-Equity and by P2-02A for Position.

Decision: `RiskEngine` remains, and is hereby ratified as, a strictly read-only consumer of canonical Equity, Peak Equity, and Position. It shall not mutate, cache independently, or republish any of them under any owning name.

Scientific Justification: ADR-007 - "Risk Evaluation does not create runtime truth. Risk Evaluation derives quantitative metrics from already established runtime information." Already certified by P2-03 (Final Certification Section 23, FR-013) for Equity/Peak-Equity and by P2-02A for Position.

Ownership Consequences: none change; Equity/Peak-Equity ownership remains exclusively `PnLEngine`/`CanonicalState` (P2-03), Position/Exposure ownership remains exclusively `PositionEngine`/`CanonicalState` (P2-02A).

Runtime Consequences: none required.

Compatibility Constraints: this boundary partially overlaps AD-008's own Position/Exposure-specific boundary - both bind the same `risk.py:9` `position` parameter from different value-scope angles (CGA Section 8, "hidden coupling" finding); any future implementation touching how `RiskEngine.check()` handles its `position` parameter must satisfy both AD-008 and this decision simultaneously.

Acceptance Criteria: `RiskEngine.check()`'s `state` and `position` parameters remain unmutated across the call, verified by identity/equality comparison before and after, at any future Certification.

Traceability: Related Functional Requirements: FR-011. Related Dependency IDs: DEP-010 (outbound constraint on AD-007). Related Capabilities: CAP-011. Related ADR: ADR-007.

### P2-04-AD-014 - RuntimeFailureEvent Risk-Metric Non-Mutation Confirmation

Motivation: FR-012 and CGA CAP-012 (COMPLETE) require explicit confirmation that rejected transitions (`RUNTIME_FAILURE_EVENT`) continue to leave Drawdown, Drawdown Ratio, and `risk_allocation_factor` unmodified, extending the already-certified P2-03 non-mutation contract to the Risk Metric category by name.

Decision: rejected transitions shall continue to leave Drawdown, Drawdown Ratio, and `risk_allocation_factor` unmodified. Any future implementation of AD-007's or AD-009's dispositions must preserve this non-mutation contract without exception.

Scientific Justification: ADR-011 - rejected transitions SHALL never modify canonical runtime state; already certified by P2-03 (Final Certification Section 20, 8/8 assertions covering `drawdown` and `drawdown_ratio` directly, and covering `risk_allocation_factor` by the same mechanism since it is published through the identical `apply_risk()` path).

Ownership Consequences: none; this is a behavioral confirmation.

Runtime Consequences: none required; AD-007 and AD-009 both introduce no new financial-state-mutating logic and no new mutation risk to `risk.py` (their own Runtime Consequences fields confirm this independently).

Compatibility Constraints: binds AD-007 and AD-009 identically to AD-011/AD-012's Compatibility Constraints.

Acceptance Criteria: a scripted `RUNTIME_FAILURE_EVENT` tick produces functionally identical Drawdown/Drawdown-Ratio/`risk_allocation_factor` values before and after the tick, re-verified at any future Certification.

Traceability: Related Functional Requirements: FR-012. Related Dependency IDs: DEP-011 (outbound constraint on AD-007/AD-009). Related Capabilities: CAP-012. Related ADR: ADR-011.

### P2-04-AD-015 - Risk Policy Configuration Reset Semantics

Motivation: FR-013 and CGA CAP-013 (PARTIAL) require a finalized reset-scope determination for Risk Policy Configuration, explicitly and textually conditional on this document's own resolution of Risk Policy Configuration's ownership (AD-002).

Decision: since AD-002 establishes Risk Policy Configuration as `RiskEngine`-private and never published to `CanonicalState`, and AD-012 ratifies that its three named values are never mutated after initialization, **no dedicated reset mechanism is required or introduced for Risk Policy Configuration**. Every fresh `RiskEngine()` instantiation deterministically re-establishes the identical configuration by construction; no runtime event, including any future `CanonicalState.reset()` call, can leave Risk Policy Configuration in an inconsistent state, since it holds no state that could become inconsistent.

Scientific Justification: AI-010 ("Financial runtime state SHALL remain internally consistent... at all times," extended by analogy to Risk Metric consistency) is satisfied trivially and permanently by the absence of any mutation path (AD-012's own evidence), the identical logical pattern by which `RiskEngine` already requires no `reset()` method for its Financial-State-adjacent consumption (P2-03 Final Certification Section 18, resolving P2-03's own FR-018 for `RiskEngine`).

Ownership Consequences: none; confirms AD-002's ownership decision requires no companion reset-ownership decision.

Runtime Consequences: none required; no reset method is added to `RiskEngine`.

Compatibility Constraints: this decision is conditional on AD-002's own disposition remaining unchanged; if a future Architecture Evolution Review relocates Risk Policy Configuration's ownership away from `RiskEngine`-private (superseding AD-002), that same review must independently determine reset semantics for the new owner, since this decision's own reasoning would no longer apply.

Acceptance Criteria: after any reset sequence (of `CanonicalState` or of `RiskEngine` itself, via fresh instantiation), Risk Policy Configuration's values remain identical to their pre-reset values, verified at any future Certification.

Traceability: Related Functional Requirements: FR-013. Related Dependency IDs: DEP-008 (inbound, CONDITIONAL, from AD-002), DEP-016 (inbound, from AD-012). Related Capabilities: CAP-013. Related ADR: AI-010.

### P2-04-AD-016 - Risk-Adjacent Compatibility Confirmation

Motivation: FR-014 and CGA CAP-014 (COMPLETE) require explicit confirmation that every already-certified P1/P2-0x Risk-adjacent contract remains preserved by this Architecture's own decisions, as a cross-cutting, continuously-reverified constraint rather than a build target.

Decision: every already-certified P1-03, P1-03.1, P1-04, P2-01, P2-02, P2-02A, and P2-03 Risk-adjacent contract (Drawdown/Drawdown-Ratio formula, Computational Authority, Authoritative Owner, and canonical input source per P2-03; Position/Exposure separation and RiskEngine's read-only consumption boundary per P2-02A; the P1-04/P2-03 `RUNTIME_FAILURE_EVENT` non-mutation contract) remains binding and is not reopened, reconsidered, or re-derived by any decision in this document. This document is directly verified, by construction, not to touch `run_engine/core/pnl.py`, `run_engine/core/canonical_state.py`'s Equity/Peak-Equity/PnL-adjacent methods, `run_engine/core/position.py`, or `run_engine/core/trade_lifecycle.py`.

Scientific Justification: none of AD-001 through AD-017 requires touching any of the four named files or contracts; every already-certified contract remains fully intact at HEAD `a81e197` (Section 4).

Ownership Consequences: none change for any P2-03- or P2-02A-owned object.

Runtime Consequences: none required.

Compatibility Constraints: this decision is the explicit governance mechanism by which the task's own instruction not to reopen P2-03-certified Financial Ownership is satisfied; any future implementation stage that touches any of the four named files or contracts violates this decision and requires an explicit Architecture Evolution Review before proceeding.

Acceptance Criteria: full regression re-run of the P2-03/P2-02A certified scenarios after any future P2-04 implementation produces functionally identical results for every already-certified field.

Traceability: Related Functional Requirements: FR-014. Related Dependency IDs: DEP-012 (outbound constraint on every other AD). Related Capabilities: CAP-014. Related ADR: ADR-004, ADR-006, ADR-007, ADR-011.

### P2-04-AD-017 - PerformanceEngine Risk-Metric Consumption Scope Boundary

Motivation: FR-015 and CGA CAP-015 (COMPLETE) require explicit scope-protection against `PerformanceEngine`'s consumption (or non-consumption) of Risk Metrics being incidentally resolved as a side effect of AD-001 through AD-010, pending resolution of whether that question belongs to P2-04 or P3-03 (Gap 6, OQ-005).

Decision: this Architecture explicitly and deliberately does **not** resolve whether `PerformanceEngine` should consume Drawdown, Drawdown Ratio, or `risk_allocation_factor`, notwithstanding the Runtime Ownership Matrix's own "Risk Metrics" row naming `PerformanceEngine` as a Primary Consumer. No decision in this document (AD-001 through AD-016) may be read, construed, or implemented as an incidental resolution of this question. `performance.py` remains untouched by every decision in this document.

Scientific Justification: the Implementation Baseline's own objective text distinguishes P2-04 ("Verify Risk Metrics ownership. Validate deterministic RiskEngine behaviour") from P3-03 ("Verify PerformanceEngine inputs. Validate Performance Metrics generation"); P2-04's own text concerns `RiskEngine`'s ownership and determinism, not downstream consumption by a different component. This document adopts the FRA's and SDA's own position (favoring P3-03 as the more likely closure venue, by analogy to how P2-03-AD-015 assigned TD-006's boundary based on each unit's own named objective text) without treating it as a settled decision, consistent with OQ-005's own CONDITIONALLY BLOCKING classification remaining open.

Ownership Consequences: none; `PerformanceEngine`'s own ownership scope (ADR-008, Rule OM-008) is entirely unaffected.

Runtime Consequences: none; `performance.py` is verified unchanged in Section 4 and remains so after every decision in this document.

Compatibility Constraints: any future document (P3-03's own FRA, or a P2-04 Architecture Evolution Review) that brings `PerformanceEngine`'s Risk-Metric consumption into scope must do so explicitly, with its own governing analysis, not as an incidental consequence of implementing AD-001 through AD-016.

Acceptance Criteria: `performance.py` contains no reference to `drawdown`, `drawdown_ratio`, or `risk_allocation_factor` after any future implementation of this document's decisions, unless a separate, explicit governing document has first authorized such a change.

Traceability: Related Functional Requirements: FR-015. Related Dependency IDs: DEP-013 (outbound constraint on AD-001 through AD-010). Related Capabilities: CAP-015. Related ADR: ADR-008 (by contrast), Runtime Ownership Matrix.

## 20. Architecture Invariants

**P2-04-AI-001 - Unique Risk Metric Computational Authority.** `RiskEngine` is, and remains, the sole Computational Authority for Drawdown, Drawdown Ratio, and `risk_allocation_factor`; no future decision may introduce a second computing component for any of the three without an Architecture Evolution Review. Established by AD-003, AD-004, AD-005.

**P2-04-AI-002 - Risk Policy Configuration Non-Publication.** Risk Policy Configuration shall never gain a `CanonicalState` key without an explicit Architecture Evolution Review superseding AD-002. Established by AD-002.

**P2-04-AI-003 - Position-Derived Exposure Non-Participation.** `risk_allocation_factor`'s computation shall remain provably independent of `position_exposure` unless an explicit Architecture Evolution Review supersedes AD-007. Established by AD-007.

**P2-04-AI-004 - RiskEngine Statelessness.** `RiskEngine` shall hold no instance attribute beyond its three Risk Policy Configuration constants, at any point in its lifecycle. Established by AD-012.

**P2-04-AI-005 - RiskEngine Purity.** `RiskEngine.check()` shall remain a pure, deterministic function of its three explicit parameters, at any point in its lifecycle. Established by AD-011.

**P2-04-AI-006 - RiskEngine Non-Ownership of Consumed State.** `RiskEngine` shall never mutate, cache independently, or republish under an owning name any of: Position, Position-derived Exposure, Equity, Peak Equity. Established by AD-008, AD-013.

**P2-04-AI-007 - Risk-Metric Failure Non-Mutation.** Rejected transitions shall never modify Drawdown, Drawdown Ratio, or `risk_allocation_factor`. Established by AD-014.

**P2-04-AI-008 - P2-03/P2-02A Compatibility.** No decision in this document, and no future implementation of it, may alter any P2-03-certified or P2-02A-certified contract. Established by AD-016.

**P2-04-AI-009 - PerformanceEngine Scope Boundary.** No decision in this document, and no future implementation of it, may incidentally resolve `PerformanceEngine`'s Risk-Metric consumption boundary. Established by AD-017.

Every Architecture Invariant above is directly traceable to one or more ADs in Section 19; no invariant is asserted without a corresponding decision establishing it.

## 21. Architecture Constraints

**Constraint C-001.** Every future Specification and Implementation stage for P2-04 must preserve AD-001's five-category taxonomy; no object may be reclassified across categories without an Architecture Evolution Review.

**Constraint C-002.** Every future Specification and Implementation stage must preserve the exact numeric values currently in `risk.py:5-7,37-44`; this document decides ownership and formula structure, not numeric calibration (explicitly out of scope, FRA Section 24).

**Constraint C-003.** No future Implementation Unit for P2-04 may be scoped to a single file artificially; per the Implementation Baseline's own definition ("Implementation Units describe logical implementation areas, not necessarily exactly one file"), an Implementation Unit realizing AD-002 (Risk Policy Configuration ownership documentation) and AD-015 (reset semantics) may, and likely should, be combined, since both concern the identical object and neither requires a code change independent of the other; conversely, AD-007 (Position-Exposure disposition) and AD-009 (formula disposition), while both decision-artifact ADs, remain independently implementable since either could in principle be revisited by a future Architecture Evolution Review without requiring the other's revision.

**Constraint C-004.** No future Certification for this unit may claim TD-006 closure (AD-010) without independently re-verifying AD-002's and AD-009's own Acceptance Criteria first, consistent with DEP-005's HARD dependency.

**Constraint C-005.** No future document may cite this Architecture as authorizing any change to `run_engine/core/pnl.py`, `run_engine/core/canonical_state.py`'s Equity/Peak-Equity/PnL-adjacent methods, `run_engine/core/position.py`, or `run_engine/core/trade_lifecycle.py` (AD-016).

**Constraint C-006.** No future document may cite this Architecture as authorizing any change to `run_engine/core/performance.py` (AD-017).

## 22. Non-Goals

Consistent with the governing task's explicit boundary and every AD's own Compatibility Constraints, this document does not, and no future document may cite it as having:

- specified concrete Python signatures, method shapes, or parameter lists for any component;
- defined complete implementation steps, file-by-file change lists, or commit sequences;
- performed any code change of any kind;
- defined tests as finished implementation commands (Section 21's Acceptance Criteria describe verifiable properties, not test code);
- anticipated or performed Specification-stage or Implementation-stage work;
- reopened P2-03's or P2-02A's own certified Financial Ownership or Position Ownership decisions;
- resolved numeric calibration of any Risk Policy Configuration value;
- resolved `PerformanceEngine`'s Risk-Metric consumption boundary (AD-017);
- introduced a new Functional Requirement, a new SDA dependency, or a new CGA capability beyond the fifteen, sixteen, and fifteen the FRA, SDA, and CGA respectively already established;
- expanded scope beyond what the FRA (Section 24), SDA (Section 2), and CGA (Section 2) already established as in scope.

## 23. Technical-Debt Disposition

| Technical Debt Item | Disposition | Established By |
|---|---|---|
| TD-001 (Canonical Position Source for PnLEngine) | Unchanged; not reopened; referenced only as a preserved contract | AD-016 |
| TD-002 (Unify `_safe_float` implementations) | Confirmed out of this document's scope; `RiskEngine` has no `_safe_float` method | not applicable (no AD touches it) |
| TD-003 (Document Pre-Trade Snapshot Dependency) | Unchanged; not reopened; referenced only as a preserved contract | AD-016 |
| TD-004 (Lifecycle-based Performance Evaluation) | Confirmed out of this document's scope | not applicable |
| TD-005 (Automated Regression Test Suite) | Confirmed out of this document's scope, project-wide | not applicable |
| TD-006 (RiskEngine Peak Equity and Drawdown Ownership Duplication) | Remaining risk-formula half fully closed | AD-010 |
| TD-007 (RunLoop Lifecycle Control Surface) | Confirmed out of this document's scope | not applicable |

No Technical Debt Register file edit is made by this document; TD-006's disposition (AD-010) is recorded as a certified finding for a future Certification to action through the Register's own governance process, consistent with the practice already established at every prior Implementation Unit in this governance chain (P2-03 Final Certification, Section 32).

## 24. FRA Traceability

| FR | Resolved By |
|---|---|
| FR-001 | AD-002 |
| FR-002 | AD-003 |
| FR-003 | AD-004 |
| FR-004 | AD-005 |
| FR-005 | AD-007 |
| FR-006 | AD-008 |
| FR-007 | AD-009 |
| FR-008 | AD-010 |
| FR-009 | AD-011 |
| FR-010 | AD-012 |
| FR-011 | AD-013 |
| FR-012 | AD-014 |
| FR-013 | AD-015 |
| FR-014 | AD-016 |
| FR-015 | AD-017 |

All fifteen FRA functional requirements are resolved by exactly one AD each; no requirement is left unresolved, and no AD resolves more than one requirement.

## 25. SDA Dependency Traceability

| SDA Dependency | Disposition |
|---|---|
| DEP-001 (FR-002 constrains FR-003) | Honored - AD-003 restates FR-002's already-true state; AD-004's naming decision for FR-003 does not relocate Computational Authority. |
| DEP-002 (FR-004 constrains FR-003) | Honored - AD-005 restates FR-004's already-true storage location; AD-004's naming decision does not relocate Authoritative Owner. |
| DEP-003 (FR-006 constrains FR-005) | Honored - AD-008's read-only boundary is preserved unconditionally by AD-007's non-incorporation decision. |
| DEP-004 (FR-005 to FR-007, CONDITIONAL) | Resolved - AD-007's non-incorporation decision makes this dimension of AD-009 moot; the formula's threshold/multiplier dimension proceeds independently, as the SDA itself anticipated. |
| DEP-005 (FR-007 to FR-008, HARD) | Satisfied - AD-009's evaluation (retention) precedes and directly enables AD-010's closure. |
| DEP-006 (FR-007 to FR-001, SOFT) | Acknowledged, not acted upon - AD-009's retention decision leaves AD-002's Risk Policy Configuration scope (the six values) unchanged, so no revision to AD-002 was required. |
| DEP-007 (FR-007 to FR-003, SOFT) | Acknowledged, not acted upon - AD-009's retention decision leaves `risk_allocation_factor`'s naming description in AD-004 unaffected. |
| DEP-008 (FR-001 to FR-013, CONDITIONAL) | Satisfied - AD-002 precedes and directly enables AD-015's reset-scope determination. |
| DEP-009 (FR-009/FR-010 constrain FR-005/FR-007) | Honored - AD-011 and AD-012 are preserved unconditionally by AD-007's and AD-009's own decisions to make no runtime change. |
| DEP-010 (FR-011 constrains FR-005) | Honored - AD-013's boundary is preserved unconditionally by AD-007. |
| DEP-011 (FR-012 constrains FR-005/FR-007) | Honored - AD-014's non-mutation contract is preserved unconditionally by AD-007 and AD-009. |
| DEP-012 (FR-014 constrains all) | Honored - AD-016 applies to every other AD in this document. |
| DEP-013 (FR-015 constrains FR-001 through FR-008) | Honored - AD-017 explicitly forecloses incidental resolution of Gap 6 by AD-002 through AD-010. |
| DEP-014 (TD-006, external, to FR-007/FR-008) | Satisfied - AD-010's closure directly operationalizes TD-006's own already-approved disposition. |
| DEP-015 (FR-002 constrains FR-007) | Honored - AD-003's exclusivity is preserved unconditionally by AD-009's retention decision. |
| DEP-016 (FR-010 informs FR-013) | Honored - AD-015's reset determination directly cites AD-012's own evidence. |

All sixteen SDA dependency records are honored by this document's decisions; none is violated, and none required a decision this document did not already make for independent, FRA-grounded reasons.

## 26. CGA Capability Traceability

| CAP | Pre-Architecture Status | Resolved By | Post-Architecture Status |
|---|---|---|---|
| CAP-001 | PARTIAL | AD-002 | Ownership named; implementation-ready pending Specification |
| CAP-002 | COMPLETE | AD-003 | Ratified, unchanged |
| CAP-003 | PARTIAL | AD-004 | Ownership named; implementation-ready pending Specification |
| CAP-004 | COMPLETE | AD-005 | Ratified, unchanged |
| CAP-005 | MISSING | AD-007 | Disposition recorded (non-incorporation); closed |
| CAP-006 | COMPLETE | AD-008 | Ratified, unchanged |
| CAP-007 | MISSING | AD-009 | Disposition recorded (retention); closed |
| CAP-008 | MISSING | AD-010 | Disposition recorded (closure); closed |
| CAP-009 | COMPLETE | AD-011 | Ratified, unchanged |
| CAP-010 | COMPLETE | AD-012 | Ratified, unchanged |
| CAP-011 | COMPLETE | AD-013 | Ratified, unchanged |
| CAP-012 | COMPLETE | AD-014 | Ratified, unchanged |
| CAP-013 | PARTIAL | AD-015 | Fully resolved (no reset mechanism required) |
| CAP-014 | COMPLETE | AD-016 | Ratified, unchanged |
| CAP-015 | COMPLETE | AD-017 | Ratified, unchanged; scope-protection confirmed |

All fifteen CGA capabilities are resolved by exactly one AD each. Of the three CGA-classified MISSING capabilities, all three (CAP-005, CAP-007, CAP-008) are fully closed by this document's explicit disposition decisions, not by runtime implementation, consistent with their own decision-artifact nature (CGA Section 5). Of the three CGA-classified PARTIAL capabilities, two (CAP-001, CAP-003) gain explicit ADR-level ownership naming, ready for Specification-stage interface design; one (CAP-013) is fully resolved outright, since AD-002's disposition directly determines its own answer with no further Specification-stage work required.

## 27. Acceptance Criteria

**P2-04-AC-001.** Risk Policy Configuration possesses an explicit, individually-named Authoritative Owner (`RiskEngine`), verifiable by citation to AD-002.

**P2-04-AC-002.** `risk_allocation_factor` possesses an explicit, individually-named Computational Authority (`RiskEngine`) and Authoritative Owner (`CanonicalState`), verifiable by citation to AD-004.

**P2-04-AC-003.** Drawdown, Drawdown Ratio, and `risk_allocation_factor` remain stored exclusively at their current `CanonicalState` locations, verifiable by direct inspection of `canonical_state.py:36,38,40,78-82`.

**P2-04-AC-004.** `risk_allocation_factor`'s computed value remains provably independent of `position_exposure`, verifiable by direct inspection of `risk.py:31-47`'s two inputs.

**P2-04-AC-005.** `RiskEngine` remains a strictly read-only consumer of Position, Position-derived Exposure, Equity, and Peak Equity, verifiable by identity/equality comparison of `check()`'s parameters before and after any call.

**P2-04-AC-006.** The risk-limiting formula's structural shape (`risk.py:31-47`) remains unchanged from HEAD `a81e197`, unless superseded by an explicit Architecture Evolution Review.

**P2-04-AC-007.** TD-006's Register entry is recorded, at a future Certification, as eligible for a full-closure status update covering both its Equity/Peak-Equity/Drawdown-input-source half (already P2-03-certified) and its risk-formula half (this document's own AD-010).

**P2-04-AC-008.** `RiskEngine.check()` remains a pure, deterministic function of its three explicit parameters, verifiable by two independent calls with identical arguments producing functionally identical returned dicts.

**P2-04-AC-009.** `vars(RiskEngine())` returns exactly `{'max_drawdown': 0.2, 'max_exposure': 1.0, 'min_exposure': 0.1}` at every point in `RiskEngine`'s lifecycle.

**P2-04-AC-010.** No `CanonicalState` key exists for any Risk Policy Configuration value.

**P2-04-AC-011.** Rejected transitions (`RUNTIME_FAILURE_EVENT`) leave Drawdown, Drawdown Ratio, and `risk_allocation_factor` unmodified.

**P2-04-AC-012.** No reset mechanism exists or is required for Risk Policy Configuration, verifiable by the absence of any mutation path across `RiskEngine`'s lifecycle.

**P2-04-AC-013.** `performance.py` contains no reference to `drawdown`, `drawdown_ratio`, or `risk_allocation_factor` after any implementation of this document's decisions.

**P2-04-AC-014.** Every P2-03-certified and P2-02A-certified Risk-adjacent contract produces functionally identical results after any implementation of this document's decisions.

**P2-04-AC-015.** No decision in this document contradicts ADR-004, ADR-006, ADR-007, ADR-011, the Runtime Ownership Matrix, any Architecture Invariant, or any Scientific Acceptance Criterion named in Section 3.

Architecture Readiness Criteria: this Architecture is Specification-ready only when AC-001 through AC-015 are all verified satisfiable by the decisions in Section 19, and when Section 29's Internal Consistency Review and Section 30's Readiness Decision both confirm PASS/READY.

## 28. Implementation Impact Inventory

This section identifies which components a future Specification and Implementation stage will need to address per AD, at the level of "logical implementation area" the Implementation Baseline itself defines - not file-by-file, not method-by-method, and not as a prescribed sequence, since Implementation Units may combine multiple ADs realized together (Constraint C-003) and this document does not decide implementation order.

| AD | Primary Component(s) Implicated | Nature of Eventual Change |
|---|---|---|
| AD-001 | none (documentation-only, taxonomy) | none - no code artifact corresponds to a taxonomy |
| AD-002 | `RiskEngine` (documentation/comment-level only) | none required beyond documenting the existing literals' now-explicit ownership status; no behavioral change |
| AD-003 | none | none - already conformant |
| AD-004 | `RiskEngine`, `CanonicalState` (documentation-level only) | none required beyond documenting `risk_allocation_factor`'s now-explicit ownership; no behavioral change |
| AD-005 | none | none - already conformant |
| AD-006 | none | none - closure statement only |
| AD-007 | `RiskEngine` (documentation-level only) | none required; the current unused read is retained exactly as-is |
| AD-008 | none | none - already conformant |
| AD-009 | `RiskEngine` (documentation-level only) | none required; the current formula is retained exactly as-is |
| AD-010 | Technical Debt Register (future Certification's own recommendation, not this document's) | a future Certification records a Register-status recommendation; no code change |
| AD-011 | none | none - already conformant |
| AD-012 | none | none - already conformant |
| AD-013 | none | none - already conformant |
| AD-014 | none | none - already conformant |
| AD-015 | `RiskEngine` (documentation-level only) | none required; no reset method is added |
| AD-016 | none (constraint on all future work) | none - preservation only |
| AD-017 | none (constraint on all future work) | none - preservation only |

This inventory's central finding: unlike P2-03, whose own Architecture required relocating Computational Authority for three financial values into `PnLEngine`, no AD in this document requires any runtime code change to `run_engine/` at all. Every decision either ratifies an already-correct state or records an explicit disposition (non-incorporation, retention, closure) that the current code already, coincidentally, satisfies without modification. A future Specification stage's own task is therefore to determine how these fifteen decisions should be *documented* at the code level (docstrings, comments, or a dedicated ownership-declaration mechanism, none decided here) rather than how they should be *implemented*, since implementation, in the behavioral sense, is already complete. Any future Specification or Implementation stage that finds this inventory's own "none required" claims incorrect - for example, if a future reviewer identifies a genuine behavioral gap this document's Repository-Grounded Current State (Section 4) missed - must resolve that discrepancy through an Architecture Evolution Review before proceeding, not by silently expanding this document's own scope.

## 29. Internal Consistency Review

### 29.1 Scientific Consistency Review

Every scientific claim in this document traces to an FRA requirement, an SDA dependency, a CGA capability, an ADR/Invariant/Rule/Acceptance-Criterion citation, or a directly-verified repository fact (Section 4); no AD invents a fact not already established by one of these sources. AD-007's and AD-009's central Scientific Justifications - that no governing document mandates Position-Exposure incorporation or formula revision - were verified by re-checking the FRA's, SDA's, and CGA's own text for any such mandate; none was found, confirming the "no speculation" rationale is evidence-grounded, not merely asserted. Status: PASS.

### 29.2 Architecture Integrity Review

Every ADR, Invariant, Rule, and Acceptance Criterion cited in this document (ADR-004, ADR-006, ADR-007, ADR-008, ADR-011, Rule OM-002, Rule OM-006, Rule OM-007, AI-002, AI-005, AI-010, AI-013, AC-003, AC-007) was drawn from the SDA's and CGA's own already-corrected citation sets, not re-derived independently. One error was found and corrected during this review pass itself: AD-002's Scientific Justification originally cross-referenced "(AD-011's Model, Section 11)," an incorrect AD number for a cross-reference that should only have named Section 11 (the Computational Authority Model); AD-011 is an unrelated decision (RiskEngine Determinism Confirmation). Corrected in place to remove the erroneous AD citation. No new Architecture Invariant (Section 20) or Constraint (Section 21) contradicts any ADR, Invariant, Rule, or Acceptance Criterion named in Section 3; each was individually re-checked against Sections 19 and 20 during drafting. No decision in this document relocates an Authoritative Owner or Computational Authority away from its currently-assigned component (Section 26's Post-Architecture Status column confirms every capability's ownership assignment is either newly-named-but-already-true or explicitly ratified, never relocated). Status: PASS (one error found and corrected during this review).

### 29.3 Ownership Review

Every AD that assigns or ratifies ownership explicitly and separately addresses all four dimensions the governing task requires - Computational Authority, Authoritative Ownership, Publication, and Consumption - either by explicit statement (AD-002, AD-004, both strengthened during this drafting pass to state all four dimensions by name) or by explicit "unchanged, governed by AD-X" cross-reference (AD-005, AD-008, AD-013, AD-014, AD-017). No AD conflates Computational Authority with Authoritative Ownership, or Publication with Consumption, anywhere in this document. Section 9 (Risk Ownership Model), Section 11 (Computational Authority Model), Section 12 (Publication Model), and Section 13 (Consumption Model) are maintained as four structurally separate sections precisely to prevent this conflation at the document-structure level, not merely within individual AD prose. Status: PASS (two ADs strengthened during this review; see 29.2's disclosed correction and this section's own strengthening, both applied before delivery).

### 29.4 Terminology Review

"Byte-identical" and "byte-for-byte" are not used anywhere in this document to describe a comparison (their only occurrence is this sentence's own meta-discussion of the terms); no comparison of Python objects, runtime dictionaries, or numeric results is described in this document requiring either term, since this document makes architecture decisions, not runtime verification claims - "functionally identical" is used wherever such a comparison is anticipated by a future Certification (AD-011's, AD-012's, AD-014's, and AC-014's own Acceptance Criteria). "COMPLETE," "PARTIAL," and "MISSING" are used only when directly quoting or citing the CGA's own classifications (Section 26), never as this document's own independent classification scheme. "Authoritative Owner," "Computational Authority," "Writer-on-Behalf-Of," and "Consumption" are used with exactly the meanings the Architecture Baseline's own "Ownership Terminology" section establishes, throughout. Status: PASS.

### 29.5 Traceability Review

All fifteen FRA functional requirements map to exactly one AD each (Section 24). All sixteen SDA dependency records are honored, none violated (Section 25). All fifteen CGA capabilities map to exactly one AD each (Section 26). AD-ID uniqueness: P2-04-AD-001 through P2-04-AD-017 are each defined exactly once (Section 19) and referenced only by ID thereafter; no ID collision or reuse was introduced, independently re-verified by direct search. All nine of the governing task's own Architecture Questions are resolved by at least one AD, cross-checked question by question against Section 8's summary table. Status: PASS.

### 29.6 Governance Review

No new Functional Requirement, SDA dependency, or CGA capability was created; the fifteen FRA requirements, sixteen SDA dependencies, and fifteen CGA capabilities are referenced exclusively by their existing IDs throughout. No scope expansion occurred (Section 2, Section 22 Non-Goals both explicitly confirm this). No decision emerges only implicitly from a table or from prose without a corresponding, explicit AD in Section 19 - every claim in Sections 9 through 18's summary Models is traced to a specific AD, verified by cross-check during drafting. No concrete Python signature, method shape, complete implementation step, code change, or finished test command was specified anywhere in this document (Section 22, Section 28 both explicitly confirm this at the document-structure level, not merely by absence). No P2-03-certified Financial Ownership decision or P2-02A-certified Position Ownership decision was reopened (AD-016, Section 4's re-verification). Status: PASS.

### 29.7 Independent Self Verification

**Repository state, re-verified at the close of drafting:** branch `run-engine-consolidation-safety`; HEAD `a81e1978cb07bbb26223c94a1b24e9220520c445`; `run_engine/` clean; no commit made during this document's drafting; no push made; the pre-existing, unrelated working-tree entries (Section 4) remain untouched.

**Mechanical checks performed (results recorded from actual command execution, not asserted):** ASCII and trailing-whitespace scan across the full document; continuous section-numbering check (## 1 through ## 30, no gap, no duplicate); AD/FR/DEP/CAP traceability grep, confirming all seventeen AD IDs, all fifteen FR IDs, all sixteen DEP IDs, and all fifteen CAP IDs are referenced; `python -m compileall run_engine` re-run, confirming this documentation-only work produced zero runtime effect; `git diff --check` against the new file; `git status --short run_engine/` confirming no runtime file changed.

**Result:** five issues were found and corrected during this drafting and review pass, all disclosed here rather than silently fixed. (1) AD-002's Scientific Justification contained an incorrect cross-reference ("AD-011's Model" instead of "Section 11"), corrected, disclosed in Section 29.2. (2) AD-002 and AD-004's Decision fields were strengthened to state all four ownership dimensions (Computational Authority, Authoritative Owner, Publication, Consumption) explicitly and separately, rather than leaving Computational-Authority-inapplicability or Publication/Consumption-unchanged status to be inferred from surrounding prose, closing a gap against the governing task's own explicit ownership-separation requirement, disclosed in Section 29.3. (3) The initial ASCII scan found four non-ASCII bytes (two German words quoted directly from the governing task's own text, containing "a" and "o" umlauts, in AD-006's Motivation and AD-016's Compatibility Constraints), both paraphrased into ASCII-safe English without loss of meaning. (4) AD-015's Scientific Justification cited "FR-018" without a unit prefix, ambiguous against this document's own FR-001-through-FR-015 numbering, when the citation actually referred to P2-03's own FR-018; corrected to read "P2-03's own FR-018." (5) Section 29.4's own Terminology Review first claimed "byte-identical" and "byte-for-byte" "do not occur anywhere in this document," the identical self-referential error already caught once in the SDA and once in the CGA during this governance chain - the claiming sentence necessarily contains the terms it discusses; corrected to state the terms are not used to describe a comparison, consistent with the corrected phrasing now used in both predecessor documents.

**Status: Independent Self Verification PASS.**

## 30. Architecture Readiness Decision

Seventeen Architecture Decision Records resolve all fifteen FRA functional requirements, honor all sixteen SDA dependency records, and resolve all fifteen CGA capabilities. Three CGA-MISSING capabilities (CAP-005, CAP-007, CAP-008) are closed by explicit disposition (non-incorporation, retention, TD-006 closure), not by runtime implementation. Three CGA-PARTIAL capabilities (CAP-001, CAP-003, CAP-013) gain explicit ownership naming or are fully resolved outright. Nine CGA-COMPLETE capabilities are formally ratified as binding invariants (Section 20), closing the risk this governance chain's own prior units (P2-02A, P2-03) implicitly carried - that an already-correct property, never formally locked in, could be silently regressed by a future implementation stage with no explicit decision to cite against the regression.

This document's central, distinguishing finding (Section 28): unlike P2-03's own Architecture, which required relocating Computational Authority for three financial values, no decision in this document requires any runtime code change. Every open capability the CGA identified was a decision-artifact gap, not a runtime-object gap, and every decision this document makes closes that gap through explicit, evidence-grounded disposition rather than through code.

No architecture decision in this document contradicts ADR-004, ADR-006, ADR-007, ADR-011, the Runtime Ownership Matrix, any Architecture Invariant, or any Scientific Acceptance Criterion (Section 29.2). No P2-03-certified or P2-02A-certified contract is reopened (AD-016). The PerformanceEngine/Risk-Metric consumption boundary question (Gap 6) is deliberately and explicitly left unresolved (AD-017), as external, deferred territory belonging to P3-03 or a future Architecture Evolution Review, not to this document.

Readiness: READY. This Architecture is sufficient to proceed to the P2-04 Specification stage, where AD-002's, AD-004's, AD-007's, AD-009's, and AD-015's decisions must be translated into concrete interface shapes, storage/documentation mechanisms, and validation procedures - none of which this document itself specifies. No further Architecture-stage investigation is required before that step.

This document stops here, before Specification, as instructed.
