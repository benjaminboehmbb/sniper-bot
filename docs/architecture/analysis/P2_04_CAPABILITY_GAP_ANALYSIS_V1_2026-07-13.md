Document Class:
Capability Gap Analysis

Document ID:
P2-04-CGA

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
docs/architecture/analysis/P2_04_CAPABILITY_GAP_ANALYSIS_V1_2026-07-13.md

Depends On:
- docs/architecture/analysis/P2_04_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-13.md
- docs/architecture/analysis/P2_04_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-13.md
- docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md
- docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md
- docs/architecture/certification/P2_03_FINAL_CERTIFICATION_V1_2026-07-11.md
- docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md
- current runtime code at HEAD a81e197

Referenced By:
- future P2-04 Architecture
- future P2-04 Specification
- future P2-04 Certification

---

# P2-04 Capability Gap Analysis

## 1. Purpose

This document performs the Capability Gap Analysis for P2-04 (Risk Ownership), following directly from `P2_04_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-13.md` (Status: Draft for Internal Review, Functional Readiness: READY, subsequently reviewed and corrected) and `P2_04_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-13.md` (Status: Draft for Internal Review, Readiness for Capability Gap Analysis: READY, subsequently reviewed and corrected).

This document determines, capability by capability, which Risk Ownership capabilities already exist in the active runtime, which exist only partially, and which are entirely missing, measured strictly against the fifteen functional requirements the FRA already established and the sixteen scientific dependencies the SDA already derived. It designs no solution, selects no interface, resolves no Open Question, and makes no architecture decision. Its sole purpose is objective capability determination, repository-grounded in every case.

## 2. Scope

In scope: gap analysis of the fifteen Risk Ownership capabilities derived directly from the FRA's fifteen functional requirements (P2-04-FR-001 through P2-04-FR-015), mapped onto the SDA's nine capability clusters and sixteen dependencies (P2-04-DEP-001 through P2-04-DEP-016), and the Architecture Baseline's ADR-004, ADR-006, ADR-007, and ADR-011.

Out of scope: the same boundaries already established by the FRA (Section 24 of that document) and the SDA (Section 2 of that document) apply unchanged - Drawdown and Drawdown Ratio's own Computational Authority/Authoritative Owner/formula (fully certified by P2-03), full `PerformanceEngine` redesign or its consumption of Risk Metrics (P3-03), `PositionSizingEngine` activation, Position/Exposure ownership itself (P2-02A, certified), Persistence and Recovery (ADR-012), repository cleanup, and the automated regression test suite (TD-005). No gap identified in these areas is treated as a P2-04 gap; each is recorded as external, deferred, or a future compatibility constraint, consistent with the FRA's and SDA's own scope protection. No architecture decision, interface shape, formula, data structure, or implementation detail is proposed anywhere in this document; no runtime file is read for new evidence beyond what the FRA and SDA already established, except for direct re-verification of unchanged repository state (Section 4).

## 3. Governing Baseline

- `docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md` - ADR-004 (Position Represents Current Market Exposure, RiskEngine consumption clause), ADR-006 (Canonical Financial State Ownership, Drawdown clause), ADR-007 (Risk Evaluation as a Pure Computational Layer), ADR-011 (Runtime Failure Handling), the Runtime Ownership Matrix's "Risk Metrics" row, Rules OM-001 through OM-009, Architecture Invariants AI-002, AI-005, AI-010, AI-013, Acceptance Criteria AC-003 and AC-007.
- `docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md` - the P2-04 unit definition ("Risk Ownership. Objectives: Verify Risk Metrics ownership. Validate deterministic RiskEngine behaviour.").
- `docs/architecture/analysis/P2_04_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-13.md` - fifteen functional requirements, seven Required Capabilities, seven Open Questions, as internally reviewed and subsequently corrected per its own Scientific Consistency Review.
- `docs/architecture/analysis/P2_04_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-13.md` - nine capability clusters, sixteen dependency records, seven classified Open Questions, five Dependency Layers, as internally reviewed and subsequently corrected per its own review.
- `docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md` - TD-001 through TD-007, in particular TD-006 (RiskEngine Peak Equity and Drawdown Ownership Duplication, Target Phase P2-03/P2-04, risk-formula half remaining after P2-03's certified closure of its Equity/Peak-Equity/Drawdown-input-source half).
- `docs/architecture/certification/P2_03_FINAL_CERTIFICATION_V1_2026-07-11.md` - the certified baseline this analysis treats as immutable evidence for RiskEngine's statelessness and Drawdown/Drawdown-Ratio ownership, HEAD `259a592` through `a81e197`.
- Current runtime code at HEAD `a81e1978cb07bbb26223c94a1b24e9220520c445`.

## 4. Verified Runtime Baseline

Repository state re-verified for this analysis: branch `run-engine-consolidation-safety`, HEAD `a81e1978cb07bbb26223c94a1b24e9220520c445`, matching the FRA's and SDA's own verification exactly (`git branch --show-current`, `git rev-parse HEAD`). `run_engine/` remains clean (`git status --short run_engine/` returns no output). `run_engine/core/risk.py`, `run_engine/core/canonical_state.py`, and `run_engine/core/canonical_enforcer.py` were re-read in full for this analysis and found unchanged from the versions the FRA and SDA analyzed; no runtime file has changed since either document was written and reviewed.

This analysis relies on the FRA's Sections 6 through 23 and the SDA's Sections 7 through 24 without re-deriving their findings from the code a second time; every capability's Runtime Coverage entry below cites the specific FRA or SDA section, requirement ID, or dependency ID that already established the underlying fact, rather than re-quoting source code beyond what is needed for direct citation.

## 5. Scientific Context and Classification Method

This analysis inherits the SDA's own structural finding (SDA Section 4) as its starting context: ten of the fifteen functional requirements are already conformant today and function as a fixed reference frame; the remaining open work concentrates in two small, narrowly-coupled clusters (Position-derived Exposure's disposition, and the risk-limiting formula's evaluation) plus two narrower naming questions and one small, conditionally-gated reset question. Consequently, this Capability Gap Analysis does not, in the main, find capabilities whose scientific definition is unsettled - ADR-004, ADR-006, and ADR-007 already establish the governing concepts for every object in scope. What it finds instead falls into two distinct kinds, both recorded explicitly per capability below.

**Runtime-object capabilities** (CAP-001 through CAP-004, CAP-006, CAP-009 through CAP-015): information objects or boundary properties that either already exist in the active runtime in some observable form, partially or fully, or do not exist at all. These are evaluated exactly per the P2-03 CGA's own method: a capability is COMPLETE when its Computational Authority, Authoritative Owner, and consumption boundary (where applicable) all conform to the FRA/SDA-derived target simultaneously; PARTIAL when at least one of these conforms while at least one does not, or when the object mechanically exists but lacks an individually-named ADR-level ownership assignment; MISSING when the underlying information object does not exist in the active runtime in any observable form.

**Decision-artifact capabilities** (CAP-005, CAP-007, CAP-008): three of the FRA's fifteen requirements (FR-005, FR-007, FR-008) are worded as explicit decision-or-evaluation obligations ("SHALL be explicitly decided and documented," "SHALL be evaluated... and either explicitly retained... or revised," "SHALL be explicitly closed or explicitly re-deferred") rather than as ownership-assignment obligations. For these, COMPLETE means the required decision or evaluation has been made and recorded by a governing document; PARTIAL means a decision framework exists but no decision has been recorded; MISSING means no decision, evaluation, or disposition has been recorded anywhere in the governance chain, regardless of whether the underlying mechanical scaffolding (a read, a formula, a Register entry) already exists. This extension is not a new classification scheme; it applies the identical three-value COMPLETE/PARTIAL/MISSING vocabulary to a different kind of underlying object, one the FRA itself already distinguished by its own SHALL-wording.

## 6. Capability Inventory

| Capability ID | Name | Current Status |
|---|---|---|
| P2-04-CAP-001 | Risk Policy Configuration Ownership | PARTIAL |
| P2-04-CAP-002 | Risk-Limiting Formula Computational Authority | COMPLETE |
| P2-04-CAP-003 | Risk Metric (`risk_allocation_factor`) Ownership Naming | PARTIAL |
| P2-04-CAP-004 | Risk Metric Canonical Storage Preservation | COMPLETE |
| P2-04-CAP-005 | Position-Derived Exposure Functional Disposition | MISSING |
| P2-04-CAP-006 | RiskEngine Read-Only Boundary (Position/Exposure) | COMPLETE |
| P2-04-CAP-007 | Risk-Limiting Formula Evaluation Disposition | MISSING |
| P2-04-CAP-008 | TD-006 Risk-Formula-Half Closure | MISSING |
| P2-04-CAP-009 | RiskEngine Determinism (Purity) | COMPLETE |
| P2-04-CAP-010 | RiskEngine Statelessness | COMPLETE |
| P2-04-CAP-011 | RiskEngine Consumer Boundary (Equity/Peak-Equity/Position) | COMPLETE |
| P2-04-CAP-012 | RuntimeFailureEvent Risk-Metric Non-Mutation | COMPLETE |
| P2-04-CAP-013 | Risk Policy Configuration Reset Consistency | PARTIAL |
| P2-04-CAP-014 | Risk-Adjacent Compatibility | COMPLETE |
| P2-04-CAP-015 | PerformanceEngine Risk-Metric Consumption Scope Protection | COMPLETE |

Fifteen capabilities were evaluated, one per FRA functional requirement (a natural 1:1 mapping, unlike P2-03's fifteen-capabilities-from-twenty-requirements consolidation, reflecting P2-04's own smaller and less redundant requirement set). Nine capabilities (CAP-002, CAP-004, CAP-006, CAP-009, CAP-010, CAP-011, CAP-012, CAP-014, CAP-015) are already COMPLETE. Three capabilities (CAP-005, CAP-007, CAP-008) are MISSING, all three being decision-artifact capabilities per Section 5, not runtime-object absences. Three capabilities (CAP-001, CAP-003, CAP-013) are PARTIAL.

## 7. Current Risk Capabilities

### P2-04-CAP-001 - Risk Policy Configuration Ownership

Scientific Purpose: an explicit, ADR-named Authoritative Owner and Computational Authority for `max_drawdown`, `max_exposure`, `min_exposure`, and the three regime-dampening multipliers, per FR-001's requirement that the parameters governing a Risk Metric's computation be as well-defined as the Risk Metric itself.
Existing Capability: the six values exist and function correctly as `RiskEngine`-private literals (`risk.py:5-7,37-44`); `RiskEngine.check()` reads and applies them deterministically every tick.
Missing Capability: no ADR, Scientific Definition, or Runtime Ownership Matrix row names these values at all (FRA Section 7, Gap 1).
Partial Capability: mechanical existence and correct runtime behavior are present; ADR-level ownership naming is absent - the same shape of gap as CAP-003 below.
Scientific Completeness: ADR-007's general "Risk Metric" category exists but does not extend to the parameters of a Risk Metric's computation; no ADR text currently could be cited as either satisfied or violated by these six values, since none names them.
Runtime Coverage: full - every value is read and applied on every `RiskEngine.check()` call (`risk.py:5-7,31,33-34,37-44`).
Ownership Coverage: none - no Authoritative Owner is named by any governing document; the values exist only as private state of the component that also happens to compute from them.
CanonicalState Coverage: absent - never published; no `CanonicalState` key holds any of the three named thresholds or the three regime multipliers (FRA Section 7, confirmed by repository-wide search of `loop.py`, `canonical_state.py`, `canonical_enforcer.py`).
Computational Authority Coverage: mechanically `RiskEngine` (the sole reader and applier); not individually confirmed by any ADR as the Computational Authority for this specific object, though consistent with ADR-007's general framing.
Writer-on-Behalf-Of Coverage: none - since the values are never published, no Writer-on-Behalf-Of path exists or is needed today.
Determinism Coverage: complete - the six values are `__init__`-time constants and inline literals, never mutated, contributing no non-determinism (FRA Section 7, Section 19 FR-010 evidence).
Repository Coverage: confirmed by direct read of `risk.py` and by repository-wide search (Section 4 of the FRA and SDA); no duplicate or competing definition exists on the active path (the confirmed-inactive `RiskLayer` uses different, unrelated numeric values, `run_engine/runtime/risk.py:5,8`).
Certification Coverage: none - no certification document has evaluated Risk Policy Configuration's ownership status; P2-03's certification scope did not include it.
Current Status: PARTIAL.
Blocking Dependencies: none upstream (SDA Section 21, Stage 1); softly, informationally fed by CAP-007's eventual disposition (SDA DEP-006).
Related Functional Requirements: FR-001.
Related Dependency IDs: DEP-006 (soft, inbound), DEP-008 (outbound, gates CAP-013).
Related ADR: ADR-007 (by proximity).
Related Technical Debt: adjacent to TD-006's risk-formula half, not identical to it (FRA Section 15).
Scope Classification: in scope; explicit Baseline objective ("Verify Risk Metrics ownership").

### P2-04-CAP-002 - Risk-Limiting Formula Computational Authority

Scientific Purpose: `RiskEngine` as the exclusive Computational Authority translating Risk Policy Configuration and canonical financial/regime state into `risk_allocation_factor`, per ADR-007's "RiskEngine computes derived Risk Metrics."
Existing Capability: `RiskEngine.check()` (`risk.py:9-55`) is the sole active-path computation of this value; repository-wide search confirms no other component computes any drawdown-ratio-and-regime-derived scaling value (FRA Section 15).
Missing Capability: none.
Partial Capability: not applicable.
Scientific Completeness: fully settled by ADR-007's Decision text, already satisfied.
Runtime Coverage: complete - `risk.py:9-55` is the only code path producing this value.
Ownership Coverage: Computational Authority role complete (`RiskEngine`); Authoritative Owner role belongs to CAP-004/CAP-003.
CanonicalState Coverage: not directly applicable to this capability (storage is CAP-004's subject); the computed value is passed to `CanonicalEnforcer.apply_risk()` for eventual storage.
Computational Authority Coverage: complete and exclusive, confirmed by direct read and by repository-wide search.
Writer-on-Behalf-Of Coverage: `CanonicalEnforcer.apply_risk()` (`canonical_enforcer.py:47-53`) is the sole publication path for this computation's result, consistent with ADR-001's general Writer-on-Behalf-Of exclusivity decision.
Determinism Coverage: complete, per CAP-009/CAP-010 below.
Repository Coverage: confirmed; no competing active-path Computational Authority found.
Certification Coverage: not directly certified by P2-03 (which certified the six *financial* objects, not `risk_allocation_factor`); this capability's conformance is established by direct FRA/SDA repository analysis, not by inherited certification.
Current Status: COMPLETE.
Blocking Dependencies: none.
Related Functional Requirements: FR-002.
Related Dependency IDs: DEP-001 (outbound constraint on CAP-003), DEP-015 (outbound constraint on CAP-007).
Related ADR: ADR-007.
Related Technical Debt: none.
Scope Classification: in scope; already satisfied, no further work required for this capability specifically.

### P2-04-CAP-003 - Risk Metric (`risk_allocation_factor`) Ownership Naming

Scientific Purpose: an individually-named ADR-level Computational Authority and Authoritative Owner assignment for `risk_allocation_factor`, mirroring Drawdown Ratio's own P2-03-AD-007 resolution, per FR-003.
Existing Capability: the object is computed, published, and stored today, mechanically conformant in every observable respect (FRA Section 9, Section 11).
Missing Capability: no ADR text names `risk_allocation_factor` individually; only the general Runtime Ownership Matrix "Risk Metrics" row covers it (FRA Section 5, Gap 2).
Partial Capability: mechanical conformance (computation, storage, publication) is complete; the individual ADR-level naming decision itself is absent - directly analogous to the P2-03 CGA's own CAP-006 (Drawdown Ratio Ownership) before P2-03-AD-007 resolved it.
Scientific Completeness: ADR-007's general Risk Metric category plausibly covers it; no ADR text names it by name.
Runtime Coverage: complete - computed at `risk.py:31-47`, stored at `canonical_state.py:40,82`.
Ownership Coverage: mechanically single (`RiskEngine`/`CanonicalState`); not individually confirmed by name.
CanonicalState Coverage: complete - `CanonicalState.state["risk_allocation_factor"]`, default `1.0` (`canonical_state.py:40`), written by `update_risk()` (`canonical_state.py:78-82`).
Computational Authority Coverage: mechanically `RiskEngine` (CAP-002); individual ADR naming absent.
Writer-on-Behalf-Of Coverage: complete - `CanonicalEnforcer.apply_risk()` (`canonical_enforcer.py:47-53`), identical mechanism to Drawdown and Drawdown Ratio.
Determinism Coverage: complete, inherited from CAP-002/CAP-009/CAP-010.
Repository Coverage: confirmed; the confirmed-inactive `PositionSizingEngine` reads a differently-sourced `risk.get("exposure", 1.0)` (`position_sizing.py:14`), unaffected by and unrelated to this capability's naming status, since it reads `RiskEngine`'s own un-prefixed return dict, not the canonical key.
Certification Coverage: none directly; P2-03's certification did not evaluate this object, since it falls outside the six financial objects that certification's own scope named (P2-03 Final Certification, Section 6).
Current Status: PARTIAL.
Blocking Dependencies: none upstream; softly, informationally fed by CAP-007's eventual disposition (SDA DEP-007).
Related Functional Requirements: FR-003.
Related Dependency IDs: DEP-001 (inbound constraint from CAP-002), DEP-002 (inbound constraint from CAP-004), DEP-007 (soft, inbound from CAP-007).
Related ADR: ADR-007.
Related Technical Debt: none directly; structurally adjacent to the already-resolved Drawdown Ratio naming gap (P2-03-AD-007).
Scope Classification: in scope, as an open naming/ownership question; not yet resolved by any document in this governance chain.

### P2-04-CAP-004 - Risk Metric Canonical Storage Preservation

Scientific Purpose: `CanonicalState` as the exclusive Authoritative Owner (storage location) of Drawdown, Drawdown Ratio, and `risk_allocation_factor`, at the general Runtime Ownership Matrix "Risk Metrics"-row level, per FR-004.
Existing Capability: all three values already reside at their correct, sole storage location (`canonical_state.py:36,38,40,78-82`), certified for Drawdown and Drawdown Ratio by P2-03 and mechanically confirmed for `risk_allocation_factor` by direct FRA/SDA analysis.
Missing Capability: none, at the storage-location level this capability's own scope covers (individual ADR-level naming for `risk_allocation_factor` specifically is CAP-003's separate subject, not this capability's).
Partial Capability: not applicable.
Scientific Completeness: fully settled - ADR-006 (Drawdown), P2-03-AD-007 (Drawdown Ratio), and the general Matrix row (`risk_allocation_factor`) all already assign `CanonicalState`.
Runtime Coverage: complete.
Ownership Coverage: complete, Authoritative Owner role only (this capability does not cover Computational Authority, which is CAP-002's/CAP-003's subject).
CanonicalState Coverage: complete - all three keys present, correctly defaulted, correctly written.
Computational Authority Coverage: not this capability's subject.
Writer-on-Behalf-Of Coverage: complete - `CanonicalEnforcer.apply_risk()`, the sole path for all three.
Determinism Coverage: not directly applicable (a storage-location property, not a computation).
Repository Coverage: confirmed by direct read of `canonical_state.py:36,38,40,78-82`.
Certification Coverage: complete for Drawdown and Drawdown Ratio (P2-03 Final Certification, Sections 7, 12); not separately certified for `risk_allocation_factor`, though mechanically identical in conformance shape.
Current Status: COMPLETE.
Blocking Dependencies: none.
Related Functional Requirements: FR-004.
Related Dependency IDs: DEP-002 (outbound constraint on CAP-003).
Related ADR: ADR-006, Rule OM-006.
Related Technical Debt: none.
Scope Classification: in scope, as a compatibility-preservation requirement; already satisfied, no further work required for this capability specifically.

### P2-04-CAP-005 - Position-Derived Exposure Functional Disposition

Scientific Purpose: an explicit, documented decision on whether Position-derived Exposure participates in RiskEngine's risk-limiting computation, per FR-005 and P2-02A-AD-008's explicit deferral of this exact decision to this unit.
Existing Capability: the mechanical read exists (`position_exposure = position.get("exposure", 0.0)`, `risk.py:10`), satisfying ADR-004's basic consumption requirement; this read is deliberate, already-certified P2-02A scaffolding, not itself a gap.
Missing Capability: no disposition of any kind - neither "confirmed permanent non-use" nor "functional incorporation" - has been decided or recorded anywhere in the governance chain; `position_exposure` is read and then never referenced again in `check()`'s remaining forty-five lines (FRA Section 6, Section 10).
Partial Capability: not applicable - unlike P2-03's own CAP-002 (Cumulative Realized PnL), where an implicit economic effect was present though unlabeled, no economic or functional effect of `position_exposure` exists anywhere in the current formula, not even implicitly; `risk_allocation_factor`'s value is provably, entirely independent of `position_exposure` for any given `drawdown_ratio`/`regime` pair (FRA Section 8). This is a cleaner, more absolute absence than the P2-03 precedent.
Scientific Completeness: ADR-004 itself is fully settled (Position-derived Exposure's own definition is certified by P2-02A); what remains open is scope, not definition - whether this already-defined value must additionally influence Risk Metric computation.
Runtime Coverage: partial in the narrow sense that the read exists but produces no observable effect; the disposition decision itself has zero runtime coverage.
Ownership Coverage: not this capability's subject (Position-derived Exposure's own ownership is fully resolved by P2-02A, unchanged).
CanonicalState Coverage: not applicable (this capability concerns a disposition decision, not a storable value).
Computational Authority Coverage: not applicable in the usual sense; whichever component eventually implements a functional incorporation (if decided) would remain `RiskEngine`, per CAP-002's already-settled Computational Authority.
Writer-on-Behalf-Of Coverage: not applicable.
Determinism Coverage: the read itself is deterministic; no disposition exists yet to evaluate for determinism.
Repository Coverage: confirmed by direct read of `risk.py:10` and cross-referenced against `P2_02A_POSITION_OWNERSHIP_ARCHITECTURE_V1_2026-07-10.md` Section 16.1-16.4, which introduced this exact line in this exact unused shape.
Certification Coverage: none - no certification document evaluates this disposition, since P2-02A's own certification explicitly scoped it out ("no functional use of it is required in this unit," P2-02A-AD-008) and P2-03's certification did not touch `risk.py`'s Position-exposure-adjacent lines at all.
Current Status: MISSING.
Blocking Dependencies: none upstream (SDA Section 21, Stage 1); CONDITIONALLY gates CAP-007's position-exposure-input dimension (SDA DEP-004); constrained by CAP-006, CAP-009, CAP-010, CAP-011, CAP-012, CAP-014, CAP-015 (SDA DEP-003, DEP-009, DEP-010, DEP-011, DEP-012, DEP-013).
Related Functional Requirements: FR-005.
Related Dependency IDs: DEP-003, DEP-004, DEP-009, DEP-010, DEP-011.
Related ADR: ADR-004, ADR-007.
Related Technical Debt: TD-006 (risk-formula half, adjacent).
Scope Classification: in scope; the unit's own named deferral target per P2-02A-AD-008.

### P2-04-CAP-006 - RiskEngine Read-Only Boundary (Position/Exposure)

Scientific Purpose: RiskEngine SHALL remain a strictly read-only consumer of Position-derived Exposure, never acquiring ownership of Position or Exposure in any form, per ADR-004, ADR-007, Rule OM-007, and FR-006.
Existing Capability: `RiskEngine.check()` never mutates its `position` parameter, never caches `position_exposure`, and never introduces an instance attribute or canonical key named `exposure` or `position` anywhere in its body (confirmed by direct read, `risk.py:9-55`), already certified by P2-02A (P2-02A-AD-008).
Missing Capability: none.
Partial Capability: not applicable.
Scientific Completeness: fully settled and already certified.
Runtime Coverage: complete.
Ownership Coverage: complete - Position and Exposure's own ownership remains exclusively `PositionEngine`/`CanonicalState` (P2-02A, unchanged); RiskEngine acquires none of it.
CanonicalState Coverage: not this capability's subject (Position's own storage is P2-02A's, unchanged).
Computational Authority Coverage: not this capability's subject.
Writer-on-Behalf-Of Coverage: not this capability's subject; RiskEngine writes nothing Position-related.
Determinism Coverage: complete, inherited from CAP-009/CAP-010.
Repository Coverage: confirmed by direct read; no mutation of `position` found anywhere in `risk.py`.
Certification Coverage: complete - P2-02A Final Certification's own boundary evidence covers this exactly.
Current Status: COMPLETE.
Blocking Dependencies: none.
Related Functional Requirements: FR-006.
Related Dependency IDs: DEP-003 (outbound constraint on CAP-005).
Related ADR: ADR-004, ADR-007, Rule OM-007.
Related Technical Debt: none.
Scope Classification: in scope, as a boundary-preservation requirement; already satisfied, no further work required for this capability specifically.

### P2-04-CAP-007 - Risk-Limiting Formula Evaluation Disposition

Scientific Purpose: an explicit evaluation and retain-or-revise disposition of the drawdown-ratio threshold check and regime-dampening multipliers, per FR-007 and AI-005/AI-010's requirement that any retained or revised formula remain deterministic and internally consistent.
Existing Capability: the formula itself exists, runs correctly, and is fully documented (`risk.py:31-47`, FRA Section 8); this is the mechanical scaffolding the evaluation would act upon, not the evaluation itself.
Missing Capability: no evaluation of any kind - neither "retain the current binary-step-function shape with recorded rationale" nor "revise it" - has been performed or recorded by any governing document.
Partial Capability: not applicable - like CAP-005, no evaluation exists even in partial or implicit form; the formula's current shape is a repository fact, not a recorded scientific judgment about whether that shape is correct.
Scientific Completeness: AI-005 and AI-010 govern the outcome any evaluation must satisfy (determinism, internal consistency); neither mandates a specific formula shape, so the evaluation's absence is a governance gap, not a scientific-definition gap.
Runtime Coverage: complete for the formula itself; zero for the evaluation.
Ownership Coverage: not this capability's subject in the ownership sense; Computational Authority for the formula's output is already settled (CAP-002).
CanonicalState Coverage: not applicable (an evaluation disposition is not a storable runtime value).
Computational Authority Coverage: not applicable to the evaluation itself.
Writer-on-Behalf-Of Coverage: not applicable.
Determinism Coverage: the current formula is deterministic (inherited from CAP-009/CAP-010); no evaluation exists to assess whether a revised formula would remain so, since no revision has been proposed.
Repository Coverage: confirmed by direct read of `risk.py:31-47`; no evaluation record found anywhere in the repository or documentation chain.
Certification Coverage: none - explicitly and by name excluded from P2-03's certification scope (P2-03-AD-015: "any change to RiskEngine's own risk-limiting formula... remains explicitly outside this decision's scope and outside P2-03 entirely, deferred to P2-04").
Current Status: MISSING.
Blocking Dependencies: CONDITIONALLY fed by CAP-005 for its position-exposure-input dimension only (SDA DEP-004); constrained by CAP-002 (SDA DEP-015), CAP-009/CAP-010 (SDA DEP-009), CAP-012 (SDA DEP-011); softly informs CAP-001 (SDA DEP-006) and CAP-003 (SDA DEP-007); directly gates CAP-008 (SDA DEP-005, HARD).
Related Functional Requirements: FR-007.
Related Dependency IDs: DEP-004, DEP-005, DEP-006, DEP-007, DEP-009, DEP-011, DEP-014, DEP-015.
Related ADR: ADR-007.
Related Technical Debt: TD-006 (risk-formula half, direct target).
Scope Classification: in scope; explicit Baseline objective ("Validate deterministic RiskEngine behaviour" bears on the formula's own determinism, though not its numeric calibration).

### P2-04-CAP-008 - TD-006 Risk-Formula-Half Closure

Scientific Purpose: explicit closure or explicit, justified re-deferral of TD-006's remaining risk-formula half, per FR-008 and P2-03-AD-015's explicit naming of this unit as the closure venue.
Existing Capability: TD-006's Equity/Peak-Equity/Drawdown-input-source half is already fully certified resolved by P2-03 (P2-03 Final Certification, Section 32); the Register entry itself still literally reads "Status: Deferred, Target Phase: P2-03/P2-04" without internal subdivision.
Missing Capability: no disposition record of any kind exists yet for the risk-formula half specifically; this capability cannot be produced without CAP-007's evaluation existing first, per its own Validation Condition ("a future Certification for this unit records an explicit TD-006 disposition").
Partial Capability: not applicable - this is entirely gated by, and has no independent content apart from, CAP-007's own outcome.
Scientific Completeness: fully settled in scope-boundary terms (P2-03-AD-015 unambiguously names this unit and this exact line range, `risk.py:5-7,33-49`, as the remaining territory); not settled in disposition terms, since no evaluation (CAP-007) yet exists to close it against.
Runtime Coverage: none directly; this capability is a governance-record capability, not a runtime object.
Ownership Coverage: not applicable.
CanonicalState Coverage: not applicable.
Computational Authority Coverage: not applicable.
Writer-on-Behalf-Of Coverage: not applicable.
Determinism Coverage: not applicable.
Repository Coverage: confirmed - the Technical Debt Register's own TD-006 entry was re-read in full; its literal text is unchanged since P2-03's certification.
Certification Coverage: none for this specific half; P2-03's own certification explicitly confirmed only its own half closed and explicitly, by name, left this half open for P2-04 (P2-03 Final Certification, Section 32).
Current Status: MISSING.
Blocking Dependencies: HARD-gated by CAP-007 (SDA DEP-005); external governance dependency on TD-006 itself (SDA DEP-014).
Related Functional Requirements: FR-008.
Related Dependency IDs: DEP-005, DEP-014.
Related ADR: ADR-006, ADR-007.
Related Technical Debt: TD-006, directly and centrally - this capability's absence is TD-006's own remaining, unclosed scope.
Scope Classification: in scope; explicit Register-named target phase.

### P2-04-CAP-009 - RiskEngine Determinism (Purity)

Scientific Purpose: `RiskEngine.check()` SHALL remain a pure, deterministic function of its three explicit parameters, with no persisted instance state contributing to its output and no non-deterministic input of any kind, per AI-005 and FR-009.
Existing Capability: confirmed by direct read - `check()`'s only reads are its three parameters and its own three `__init__`-time-only constants; no randomness, wall-clock read, or global state is referenced anywhere in the method body (`risk.py:9-55`).
Missing Capability: none.
Partial Capability: not applicable.
Scientific Completeness: fully settled, already satisfied.
Runtime Coverage: complete.
Ownership Coverage: not this capability's direct subject (a behavioral property, not an ownership assignment).
CanonicalState Coverage: not applicable.
Computational Authority Coverage: not applicable.
Writer-on-Behalf-Of Coverage: not applicable.
Determinism Coverage: complete - this capability's own subject.
Repository Coverage: confirmed by direct read; no non-deterministic input found.
Certification Coverage: partially inherited - P2-03 Final Certification Section 10 established statelessness at initialization, after a 50-tick run, a lifecycle run, and a failure-tick run, as a byproduct of its own Financial Ownership scope; Sections 18-19 of that same certification additionally exercised output-level determinism incidentally via full-system Replay/Determinism testing; no P2-04-specific, individually-named determinism certification yet exists (FRA Section 13, Gap 5; SDA Section 25).
Current Status: COMPLETE.
Blocking Dependencies: none; CONSTRAINS CAP-005 and CAP-007 (SDA DEP-009).
Related Functional Requirements: FR-009.
Related Dependency IDs: DEP-009 (outbound constraint).
Related ADR: AI-005, ADR-007.
Related Technical Debt: none.
Scope Classification: in scope; explicit Baseline objective ("Validate deterministic RiskEngine behaviour"); already satisfied, independent re-verification (not implementation) is this capability's own remaining, non-blocking work.

### P2-04-CAP-010 - RiskEngine Statelessness

Scientific Purpose: RiskEngine SHALL hold no instance attribute beyond its three Risk Policy Configuration constants, set once at initialization and never mutated thereafter, per Rule OM-007 and FR-010.
Existing Capability: confirmed by direct read of `__init__` (`risk.py:3-7`, exactly three assignments) and of `check()` (no `self.<name> = ` assignment anywhere in `risk.py:9-55`); `vars(RiskEngine())` returns exactly `{'max_drawdown': 0.2, 'max_exposure': 1.0, 'min_exposure': 0.1}`.
Missing Capability: none.
Partial Capability: not applicable.
Scientific Completeness: fully settled, already satisfied.
Runtime Coverage: complete.
Ownership Coverage: complete - Rule OM-007's "RiskEngine owns no runtime information" is directly satisfied.
CanonicalState Coverage: not applicable.
Computational Authority Coverage: not applicable.
Writer-on-Behalf-Of Coverage: not applicable.
Determinism Coverage: complete, the structural precondition for CAP-009.
Repository Coverage: confirmed by direct read.
Certification Coverage: complete - P2-03 Final Certification Section 10 established this exact fact directly (initialization, 50-tick run, lifecycle run, failure-tick run, all showing the identical three-attribute set).
Current Status: COMPLETE.
Blocking Dependencies: none; CONSTRAINS CAP-005 and CAP-007 jointly with CAP-009 (SDA DEP-009); informs CAP-013's reset-necessity determination (SDA DEP-016).
Related Functional Requirements: FR-010.
Related Dependency IDs: DEP-009, DEP-016.
Related ADR: ADR-007, Rule OM-007.
Related Technical Debt: none.
Scope Classification: in scope; already satisfied, no further work required for this capability specifically.

### P2-04-CAP-011 - RiskEngine Consumer Boundary (Equity/Peak-Equity/Position)

Scientific Purpose: RiskEngine SHALL remain a strictly read-only consumer of canonical Equity, Peak Equity, and Position; it SHALL NOT mutate, cache independently, or republish any of them under any owning name, per ADR-007 and FR-011.
Existing Capability: confirmed by direct read - no write to `state` or `position` anywhere in `check()`'s body (`risk.py:9-55`); already certified for Equity/Peak-Equity by P2-03 (Section 23, FR-013) and for Position by P2-02A.
Missing Capability: none.
Partial Capability: not applicable.
Scientific Completeness: fully settled, already satisfied.
Runtime Coverage: complete.
Ownership Coverage: complete - Equity/Peak-Equity ownership remains exclusively `PnLEngine`/`CanonicalState` (P2-03, unchanged); Position/Exposure ownership remains exclusively `PositionEngine`/`CanonicalState` (P2-02A, unchanged).
CanonicalState Coverage: not this capability's subject (Equity/Peak-Equity/Position's own storage is P2-03's/P2-02A's, unchanged).
Computational Authority Coverage: not this capability's subject.
Writer-on-Behalf-Of Coverage: not this capability's subject.
Determinism Coverage: complete, inherited from CAP-009/CAP-010.
Repository Coverage: confirmed by direct read; identity/equality of `state` and `position` preserved across the call.
Certification Coverage: complete for Equity/Peak-Equity (P2-03 Final Certification, Section 23 FR-013) and for Position (P2-02A Final Certification).
Current Status: COMPLETE.
Blocking Dependencies: none; CONSTRAINS CAP-005 (SDA DEP-010), partially overlapping with CAP-006's own Position/Exposure-specific boundary (SDA Section 25, Dependency Findings, "hidden coupling" - both bound the same `risk.py:9` `position` parameter from different value-scope angles).
Related Functional Requirements: FR-011.
Related Dependency IDs: DEP-010 (outbound constraint on CAP-005).
Related ADR: ADR-007.
Related Technical Debt: none.
Scope Classification: in scope, as a compatibility-preservation requirement; already satisfied, no further work required for this capability specifically.

### P2-04-CAP-012 - RuntimeFailureEvent Risk-Metric Non-Mutation

Scientific Purpose: rejected transitions (`RUNTIME_FAILURE_EVENT`) SHALL continue to leave Drawdown, Drawdown Ratio, and `risk_allocation_factor` unmodified, per ADR-011 and FR-012, extending the already-certified P2-03 non-mutation contract to the Risk Metric category.
Existing Capability: already correctly implemented and certified - P2-03 Final Certification Section 20 confirmed 8/8 assertions of non-mutation across a scripted `RUNTIME_FAILURE_EVENT` tick, covering `pnl`, `realized_pnl_cumulative`, `equity`, `peak_equity`, `drawdown`, `drawdown_ratio` (which includes both Risk Metrics this capability names) and `RiskEngine`'s own attribute set.
Missing Capability: none.
Partial Capability: not applicable.
Scientific Completeness: fully settled, already satisfied.
Runtime Coverage: complete; P2-04 introduces no new financial-state-mutating logic and no new mutation risk to `risk.py` beyond whatever CAP-005/CAP-007 eventually decide (FRA Section 21).
Ownership Coverage: not this capability's direct subject.
CanonicalState Coverage: not directly applicable; the non-mutation property concerns the already-established storage locations (CAP-004).
Computational Authority Coverage: not applicable.
Writer-on-Behalf-Of Coverage: not applicable.
Determinism Coverage: consistent with CAP-009/CAP-010; non-mutation across a failure tick is itself a determinism-adjacent property.
Repository Coverage: confirmed via P2-03's own certification evidence, re-cited rather than re-derived.
Certification Coverage: complete - P2-03 Final Certification Section 20, 8/8 assertions.
Current Status: COMPLETE.
Blocking Dependencies: none; CONSTRAINS CAP-005 and CAP-007 (SDA DEP-011).
Related Functional Requirements: FR-012.
Related Dependency IDs: DEP-011 (outbound constraint).
Related ADR: ADR-011.
Related Technical Debt: none.
Scope Classification: in scope, as a compatibility-preservation requirement; already satisfied, re-verification (not implementation) required once CAP-005/CAP-007 resolve.

### P2-04-CAP-013 - Risk Policy Configuration Reset Consistency

Scientific Purpose: reset semantics for Risk Policy Configuration, consistent with AI-010's "internally consistent... at all times" requirement, per FR-013, explicitly and textually conditional on CAP-001's resolution.
Existing Capability: trivially satisfied today - the three named constants are set once and never mutated (CAP-010's own evidence), so no dedicated reset logic is currently required for correctness; `CanonicalState.reset()` already correctly restores every field it owns (`canonical_state.py:111-113`), none of which currently includes Risk Policy Configuration.
Missing Capability: a finalized reset-scope determination, contingent entirely on whether CAP-001 resolves toward publication (requiring new reset logic for the new owner) or toward continued `RiskEngine`-private status (requiring none, per CAP-010's statelessness evidence).
Partial Capability: the trivial, currently-adequate case is present; the aggregate, fully-certifiable determination is not, mirroring the P2-03 CGA's own CAP-011 (Reset Consistency) precedent exactly - "the complete inventory of financial-adjacent state... is not yet finalized, so full reset consistency cannot yet be certified."
Scientific Completeness: AI-010 itself is fully settled; what remains open is entirely downstream of CAP-001, not a separate scientific question.
Runtime Coverage: complete for the current, trivial case; not yet evaluable for a not-yet-decided future owner.
Ownership Coverage: not this capability's direct subject (inherits CAP-001's open status).
CanonicalState Coverage: not applicable in the current, `RiskEngine`-private case; would become applicable only if CAP-001 resolves toward publication.
Computational Authority Coverage: not applicable.
Writer-on-Behalf-Of Coverage: not applicable in the current case.
Determinism Coverage: complete for the current, unmutated-constants case.
Repository Coverage: confirmed - `canonical_state.py:111-113` (`reset()` -> `self.__init__()`), the existing pattern any new owner would need to follow, already identified as such.
Certification Coverage: none directly; not evaluated by any prior certification, since this exact conditional relationship (Risk Policy Configuration's reset scope depending on its own ownership resolution) is P2-04's own new finding.
Current Status: PARTIAL.
Blocking Dependencies: HARD-gated (CONDITIONAL) by CAP-001 (SDA DEP-008); informed by CAP-010 (SDA DEP-016).
Related Functional Requirements: FR-013.
Related Dependency IDs: DEP-008, DEP-016.
Related ADR: AI-010.
Related Technical Debt: none.
Scope Classification: in scope, conditionally on CAP-001's resolution.

### P2-04-CAP-014 - Risk-Adjacent Compatibility

Scientific Purpose: preservation of every already-certified P1/P2-0x Risk-adjacent contract (Drawdown/Drawdown-Ratio formula, Computational Authority, Authoritative Owner, and canonical input source per P2-03; Position/Exposure separation and RiskEngine's read-only consumption boundary per P2-02A; the P1-04/P2-03 `RUNTIME_FAILURE_EVENT` non-mutation contract), a cross-cutting, continuously-reverified constraint rather than a build target, per FR-014.
Existing Capability: none of the FRA's fifteen requirements requires touching `run_engine/core/pnl.py`, `run_engine/core/canonical_state.py`'s Equity/Peak-Equity/PnL-adjacent methods, `run_engine/core/position.py`, or `run_engine/core/trade_lifecycle.py` (FRA Section 23); every already-certified contract remains fully intact at HEAD `a81e197` (unchanged since P2-03's own certification).
Missing Capability: none.
Partial Capability: not applicable.
Scientific Completeness: fully settled, already satisfied, by inheritance from P2-03 and P2-02A's own certifications.
Runtime Coverage: complete - re-verified directly in Section 4 above (`risk.py`, `canonical_state.py`, `canonical_enforcer.py` unchanged).
Ownership Coverage: complete for every named contract.
CanonicalState Coverage: complete - no schema regression found.
Computational Authority Coverage: complete - no relocation found.
Writer-on-Behalf-Of Coverage: complete - `CanonicalEnforcer` remains the sole publication path throughout.
Determinism Coverage: complete, inherited from P2-03's own Replay/Determinism certification (Sections 18-19 of that document).
Repository Coverage: confirmed directly (Section 4).
Certification Coverage: complete - P2-03 Final Certification and P2-02A Final Certification, both directly applicable and unchanged.
Current Status: COMPLETE.
Blocking Dependencies: none (this capability constrains every other capability rather than being gated by any of them).
Related Functional Requirements: FR-014.
Related Dependency IDs: DEP-012 (outbound constraint on all clusters).
Related ADR: ADR-004, ADR-006, ADR-007, ADR-011.
Related Technical Debt: none directly; TD-001, TD-003 referenced only as contracts to preserve via the FRA's own Technical-Debt Traceability (Section 27 of that document), neither reopened here.
Scope Classification: in scope, as a constraint layer continuously applied to every other capability, not a build target.

### P2-04-CAP-015 - PerformanceEngine Risk-Metric Consumption Scope Protection

Scientific Purpose: explicit scope-protection against `PerformanceEngine`'s consumption (or non-consumption) of Risk Metrics being incidentally resolved as a side effect of CAP-001 through CAP-008, pending resolution of whether that question belongs to P2-04 or P3-03, per FR-015.
Existing Capability: the protection itself holds today - `performance.py` remains entirely unchanged, and no capability's own resolution work has touched it (Section 4); the constraint FR-015 requires is, as its own object, already and continuously true.
Missing Capability: none, for the scope-protection capability itself; the underlying Gap 6 question (whether `PerformanceEngine` should consume Drawdown/Drawdown-Ratio/`risk_allocation_factor`, as the Runtime Ownership Matrix's "Risk Metrics" row names it as a Primary Consumer) remains genuinely unresolved, but that unresolved question is explicitly not this capability's own subject - it is external, deferred territory this capability exists to guard, not to close (FRA Section 13, Gap 6; Section 28, OQ-005).
Partial Capability: not applicable.
Scientific Completeness: the scope-protection requirement itself is fully settled (it is a governance constraint, not a scientific claim about `PerformanceEngine`'s eventual design); the external Gap 6 question it guards remains open, by design, outside this capability's own closure criteria.
Runtime Coverage: complete - `performance.py` verified unchanged (FRA Section 9, re-confirmed Section 4 above).
Ownership Coverage: not this capability's subject.
CanonicalState Coverage: not this capability's subject.
Computational Authority Coverage: not this capability's subject.
Writer-on-Behalf-Of Coverage: not this capability's subject.
Determinism Coverage: not applicable.
Repository Coverage: confirmed - no reference to `drawdown`, `drawdown_ratio`, or `risk_allocation_factor` anywhere in `performance.py`.
Certification Coverage: not directly certified; the underlying non-consumption fact is confirmed by direct repository read, consistent with the P2-03 FRA's own prior identical finding.
Current Status: COMPLETE.
Blocking Dependencies: none (this capability constrains CAP-001 through CAP-008 rather than being gated by any of them).
Related Functional Requirements: FR-015.
Related Dependency IDs: DEP-013 (outbound constraint on CAP-001 through CAP-008).
Related ADR: ADR-008 (by contrast), Runtime Ownership Matrix.
Related Technical Debt: none.
Scope Classification: explicitly protected against silent scope expansion; disposition of the underlying Gap 6 question deferred.

## 8. Current Runtime Deficiencies

This section synthesizes the cross-cutting deficiency patterns identified across the fifteen capabilities in Section 7, answering each question the governing task poses directly.

**Which capability already exists completely?** CAP-002, CAP-004, CAP-006, CAP-009, CAP-010, CAP-011, CAP-012, CAP-014, CAP-015 - nine of fifteen. All nine require no further implementation work; each is already conformant to its full FRA/SDA target, though CAP-009 and CAP-012's own determinism/non-mutation properties remain subject to re-verification once CAP-005/CAP-007 resolve, a re-verification obligation rather than a current gap.

**Which capability exists only partially?** CAP-001, CAP-003, CAP-013 - three of fifteen. In every one of these three, the underlying mechanical scaffolding (a runtime value or method) already exists and functions correctly; what remains is an ADR-level ownership-naming decision (CAP-001, CAP-003) or a downstream, conditionally-gated reset determination (CAP-013).

**Which capability is missing completely?** CAP-005, CAP-007, CAP-008 - three of fifteen, all three decision-artifact capabilities (Section 5). None is missing in the runtime-object sense P2-03's own CAP-002 (Cumulative Realized PnL) was: no field, method, or storage location is absent from the active runtime for any of these three. What is absent in every case is a governance-chain decision or evaluation record.

**Which capability is present only implicitly?** None. This is a material difference from the P2-03 CGA, whose own CAP-002 (Cumulative Realized PnL) had its economic effect present, though unlabeled, inside Equity's running total. No P2-04 capability exhibits this pattern: CAP-005's `position_exposure` produces zero observable effect on `risk_allocation_factor` under any input, not even implicitly (FRA Section 8, directly re-confirmed in CAP-005's own Section 7 entry above); CAP-007's formula evaluation has no implicit or partial record anywhere. Every MISSING capability in this analysis is a clean, total absence of the decision or evaluation itself, not a mislabeled or entangled partial presence.

**Which capability is jointly fulfilled by multiple components?** None, in the non-conformant, duplicate-ownership sense P2-03's own CAP-004 (Peak Equity, computed independently by two components before P2-03 resolved it) exhibited. CAP-014 (Risk-Adjacent Compatibility) is, by its own cross-cutting nature, jointly upheld by every other capability's individual conformance, the same aggregate role P2-03's CAP-015 played. No active duplicate Computational Authority was found for any P2-04 capability; the confirmed-inactive `RiskLayer` (`run_engine/runtime/risk.py`) represents a historical, dormant duplicate pattern for Equity/Peak-Equity/Drawdown (not Risk Policy Configuration or `risk_allocation_factor` specifically), already noted by the FRA and SDA (FRA Section 4) and unchanged by this analysis - not an active runtime deficiency.

**Which capability violates current Ownership rules (Rule OM-001 through OM-009)?** None. This is the single most significant difference between this analysis and the P2-03 CGA's own conclusion, which found active Rule and ADR violations (CAP-003's Computational Authority misassignment, CAP-004's duplicate ownership). Every P2-04 gap instead falls into one of three non-violating categories: (a) an absence of ADR/Matrix-level definition where none currently exists to violate (CAP-001, CAP-003 - you cannot violate a rule that has not yet been written for this object); (b) an unresolved but not-yet-mandated evaluation or decision (CAP-005, CAP-007, CAP-008); or (c) a currently-latent, not-presently-triggered consistency question (CAP-013, exactly analogous to the P2-03 CGA's own CAP-011 finding). P2-04 inherits a clean, non-violating baseline directly from P2-03's own certified closure of TD-006's ownership-duplication half.

**Which capability violates current Computational Authority assignment?** None. CAP-002 (the formula's Computational Authority) is exclusively and correctly `RiskEngine`, confirmed by repository-wide search. No capability in this analysis assigns Computational Authority to more than one component or to the wrong component.

**Which capability violates current Canonical Publication?** None. CAP-004 confirms all three storage locations (Drawdown, Drawdown Ratio, `risk_allocation_factor`) are already correct and singular. Risk Policy Configuration (CAP-001) is absent from `CanonicalState` entirely, but since no ADR mandates its publication, this is an unaddressed question, not a violation of an existing publication requirement.

**Which capability violates Determinism?** None. CAP-009 and CAP-010 both confirm `RiskEngine.check()` is currently pure and stateless; the FRA, SDA, and P2-03 Final Certification all independently corroborate this. CAP-005 and CAP-007's own eventual resolution is explicitly bounded by SDA DEP-009 to preserve this property, a forward-looking constraint, not evidence of a present violation.

**Which capability violates Writer-on-Behalf-Of exclusivity?** None. `CanonicalEnforcer.apply_risk()` remains the sole publication path for Drawdown, Drawdown Ratio, and `risk_allocation_factor` (CAP-002, CAP-003, CAP-004), consistent with ADR-001's general decision, already established and relied upon by every prior certification in this governance chain.

**Which capability violates Architecture Invariants?** None. AI-002 (Unique Ownership) is preserved throughout (Section 7's CAP-001/CAP-003/CAP-004 entries); AI-005 (Deterministic Execution) is preserved (CAP-009); AI-010 (Financial Consistency, extended by analogy) is preserved, including for CAP-013's currently-latent case; AI-013 (Architectural Minimality) was checked against this document's own fifteen-capability granularity and found justified, since each capability traces to a distinct FRA requirement with its own distinct Removal Test outcome (SDA Sections 7-15).

**Which capability violates Acceptance Criteria?** None. AC-003 ("Every runtime information object possesses exactly one Computational Authority") is preserved by CAP-002. AC-007 ("RiskEngine consumes only Canonical Working State... owns no canonical runtime information... remains deterministic") is preserved by CAP-006, CAP-009, CAP-010, CAP-011 collectively.

**Which capability violates the Runtime Ownership Matrix?** None directly. The Matrix's general "Risk Metrics" row (Authoritative Owner `CanonicalState`, Computational Authority `RiskEngine`) is preserved by CAP-004. The Matrix's naming of `PerformanceEngine` as a Primary Consumer of Risk Metrics is not currently implemented (CAP-015's own underlying Gap 6), but this is explicitly scope-protected as external, not-yet-resolved territory (CAP-015, FR-015), not a violation this document adjudicates.

**Hidden coupling structures.** One was confirmed, carried forward from the SDA (its Section 25): CAP-006 (RiskEngine's Position/Exposure-specific read-only boundary) and CAP-011 (RiskEngine's broader Equity/Peak-Equity/Position read-only boundary) both bound the same `risk.py:9` `position` parameter; any future implementation touching CAP-005's disposition must satisfy both simultaneously, a joint-verification obligation neither capability's own text states in isolation.

## 9. Capability Gap Catalogue

For every non-COMPLETE capability, Current Capability, Target Capability, Gap Description, and Scientific Consequence are recorded below. COMPLETE capabilities (CAP-002, CAP-004, CAP-006, CAP-009, CAP-010, CAP-011, CAP-012, CAP-014, CAP-015) have no gap and are omitted from this catalogue by construction; their Section 7 entries record their already-satisfied state in full.

**P2-04-CAP-001 - Risk Policy Configuration Ownership**
Current Capability: private `RiskEngine` literals, mechanically correct and deterministic, never published, never ADR-named.
Target Capability: an explicit, ADR-named Authoritative Owner and Computational Authority, whichever disposition a future Architecture document selects.
Gap Description: absence of ADR-level ownership definition, not an implementation defect.
Scientific Consequence: "Verify Risk Metrics ownership" (P2-04's own Baseline objective) is not fully satisfiable while the parameters governing that computation remain architecturally unnamed.

**P2-04-CAP-003 - Risk Metric (`risk_allocation_factor`) Ownership Naming**
Current Capability: computed, stored, and published correctly; covered only by the general Runtime Ownership Matrix "Risk Metrics" row, not individually named.
Target Capability: an individually-named Computational Authority and Authoritative Owner, mirroring Drawdown Ratio's own P2-03-AD-007 resolution.
Gap Description: absence of individual ADR-level naming, identical in shape to the pre-P2-03 Drawdown Ratio gap.
Scientific Consequence: this value cannot be certified conformant or non-conformant to any individually-named ADR text, since none currently names it by name.

**P2-04-CAP-005 - Position-Derived Exposure Functional Disposition**
Current Capability: a mechanical, already-certified read (`position_exposure`) that produces zero effect on the risk-limiting formula's output.
Target Capability: an explicit, documented disposition - either confirmed permanent non-use or functional incorporation.
Gap Description: complete absence of a decision record, not a partial or misassigned implementation.
Scientific Consequence: ADR-004's "consume Position-derived Exposure" requirement remains satisfied only in the minimal mechanical sense P2-02A-AD-008 established; full scientific closure on the intended end state does not yet exist.

**P2-04-CAP-007 - Risk-Limiting Formula Evaluation Disposition**
Current Capability: a fully functional, fully documented, but never formally evaluated formula.
Target Capability: an explicit retain-or-revise disposition, with recorded rationale.
Gap Description: absence of an evaluation record, not a defect in the formula itself.
Scientific Consequence: TD-006's remaining risk-formula half (CAP-008) cannot be closed until this evaluation exists; AI-005/AI-010's determinism and consistency requirements bound any eventual outcome but do not themselves mandate a specific formula shape.

**P2-04-CAP-008 - TD-006 Risk-Formula-Half Closure**
Current Capability: no disposition record exists; the Technical Debt Register's own TD-006 entry remains textually unchanged since P2-03's certification.
Target Capability: an explicit closure or explicit, justified re-deferral, recorded by a future Certification for this unit.
Gap Description: entirely downstream of, and without independent content apart from, CAP-007's own outcome.
Scientific Consequence: TD-006 remains open past P2-04 with no further named successor unit, since P2-03-AD-015 names this unit specifically as the closure venue.

**P2-04-CAP-013 - Risk Policy Configuration Reset Consistency**
Current Capability: trivially satisfied today, since the governing constants are never mutated.
Target Capability: a finalized reset-scope determination, consistent with whatever CAP-001 eventually decides.
Gap Description: incomplete reset-scope inventory, contingent on CAP-001's final disposition, not a currently-observable defect.
Scientific Consequence: AI-010's "at all times" invariant would be violated on the first tick following any future reset call, if Risk Policy Configuration gains a mutable owner elsewhere without corresponding reset logic - a latent, not presently-triggered, risk.

## 10. Current vs Target Matrix

| Capability ID | Current | Target | Gap | Consequence |
|---|---|---|---|---|
| CAP-001 | RiskEngine-private literals, unpublished | Explicit ADR-named ownership | Ownership-definition absent | "Verify Risk Metrics ownership" incompletely satisfied |
| CAP-003 | Computed/stored, Matrix-row-level only | Individually-named ownership | Naming absent | Uncertifiable against any individually-named ADR |
| CAP-005 | Read exists, zero formula effect | Explicit documented disposition | Decision absent | ADR-004 satisfied only minimally, no scientific closure |
| CAP-007 | Formula functions, never evaluated | Explicit retain-or-revise disposition | Evaluation absent | TD-006 risk-formula half cannot close |
| CAP-008 | No disposition record | Explicit closure or re-deferral | Downstream of CAP-007 | TD-006 remains open past P2-04 |
| CAP-013 | Trivially satisfied (no mutation occurs) | Finalized reset-scope determination | Contingent on CAP-001 | AI-010 latent violation risk if ownership relocates |

CAP-002, CAP-004, CAP-006, CAP-009, CAP-010, CAP-011, CAP-012, CAP-014, and CAP-015 are omitted from this matrix, being already at target with no recorded gap (Section 7).

## 11. Dependency Interaction

Every non-COMPLETE capability's Blocking Dependencies (Section 7) trace directly to the SDA's own Dependency Graph (SDA Section 19); no new dependency is introduced by this document. The interaction pattern confirms the SDA's own two-small-clusters structure (SDA Section 22): CAP-005 and CAP-007 are the two capabilities whose resolution most directly gates the remaining catalogue, connected by exactly one CONDITIONAL edge scoped to a single dimension, not by a full mutual gate:

- CAP-005 CONDITIONALLY gates CAP-007's position-exposure-input dimension only (via DEP-004); CAP-007's own threshold/multiplier-retention dimension proceeds independently of CAP-005.
- CAP-007 HARD-gates CAP-008 (via DEP-005); no capability in this catalogue is gated by CAP-008 in turn, since CAP-008 is terminal within its own cluster.
- CAP-001 CONDITIONALLY gates CAP-013 (via DEP-008), independent of CAP-005/CAP-007.
- CAP-009 and CAP-010 (already COMPLETE) CONSTRAIN CAP-005 and CAP-007 without gating their timing (via DEP-009); CAP-011 similarly constrains CAP-005 (via DEP-010); CAP-012 constrains both CAP-005 and CAP-007 (via DEP-011).
- CAP-014 (Risk-Adjacent Compatibility) constrains every capability above without being gated by any of them, exactly as SDA Cluster I's I1 sub-cluster describes.
- CAP-015 (PerformanceEngine Scope Protection) constrains CAP-001 through CAP-008 specifically, without being gated by any of them, exactly as SDA Cluster I's I2 sub-cluster describes.

No capability interaction was found in this analysis that contradicts or extends the SDA's own Dependency Graph; this section is a capability-level restatement of that graph, not a new derivation.

## 12. Capability Readiness

**Capabilities requiring no further work (already at target):** CAP-002, CAP-004, CAP-006, CAP-009, CAP-010, CAP-011, CAP-012, CAP-014, CAP-015. Nothing further is required for these nine specifically, beyond the ordinary re-verification CAP-009 and CAP-012 will undergo once CAP-005/CAP-007 resolve.

**Capabilities that are implementation-ready without any further Architecture-stage decision:** none. Every non-COMPLETE capability requires at least one Architecture-stage decision before implementation can begin, even where the underlying requirement itself is unambiguous (Section 5). This is a direct, capability-level restatement of the SDA's own finding that four Open Questions remain CONDITIONALLY BLOCKING (SDA Section 16): the requirement that Risk Policy Configuration possess an explicit owner (CAP-001) is not in question, but whether that owner remains `RiskEngine`-private or becomes published to `CanonicalState` (OQ-001) is.

**Capabilities that require an Architecture decision first, and which decision:** CAP-001 requires OQ-001 (publication versus private-with-rationale). CAP-003 requires an entirely new ownership-naming decision (no OQ currently proposes an answer, only records the question, FR-003, mirroring the P2-03 CGA's own treatment of Drawdown Ratio before P2-03-AD-007). CAP-005 requires OQ-002 (the intended relationship between exposure and `risk_allocation_factor`, if incorporated). CAP-007 requires OQ-002 (conditionally) and OQ-003 (binary-step versus continuous). CAP-008 requires CAP-007's own resolution first, then a governance-record decision with no further open question of its own. CAP-013 requires CAP-001's resolution first, then no further open question of its own (its Validation Condition is fully determined once CAP-001 resolves, per FR-013's own conditional framing).

**Capabilities that depend exclusively on already-known Open Questions (no new OQ required):** all six non-COMPLETE capabilities. No capability in this analysis was found to require an Open Question beyond the seven the FRA already records (Section 13 below confirms this explicitly).

**Capabilities that possess no remaining scientific blocker, only implementation-detail or governance-record questions:** CAP-001, CAP-005, CAP-007, CAP-008, CAP-013 - five of six non-COMPLETE capabilities. Every one of their governing ADRs already resolves the underlying scientific question (Section 5); only ownership-mechanism, formula-shape, or record-timing remain open. The single exception is CAP-003, whose remaining question (`risk_allocation_factor`'s individual ownership naming) is genuinely scientific/definitional in the identical sense the P2-03 CGA's own CAP-006 (Drawdown Ratio) was, since no ADR currently names an answer at all - though unlike that P2-03 precedent, this document does not resolve it either, consistent with this analysis's own governance boundary.

## 13. Open Question Interaction

Every capability's remaining work maps to at least one of the FRA's seven already-recorded Open Questions (OQ-001 through OQ-007); no new Open Question was identified by this analysis.

| Open Question | SDA Classification | Interacting Capabilities |
|---|---|---|
| OQ-001 (Risk Policy Configuration publication versus private) | CONDITIONALLY BLOCKING | CAP-001, CAP-013 |
| OQ-002 (intended exposure-to-formula relationship, if incorporated) | CONDITIONALLY BLOCKING | CAP-005, CAP-007 |
| OQ-003 (binary step function versus continuous) | CONDITIONALLY BLOCKING | CAP-007 |
| OQ-004 (numeric calibration of Risk Policy Configuration) | NON-BLOCKING | none directly (explicitly outside FRA scope; no capability's Validation Condition requires a specific numeric value) |
| OQ-005 (Gap 6 closure venue, P2-04 or P3-03) | CONDITIONALLY BLOCKING | CAP-015 |
| OQ-006 (regime-multiplier classification, Cluster A or D) | NON-BLOCKING | CAP-001, CAP-007 (classification-only, does not block either's own resolution) |
| OQ-007 (RiskEngine internal variable naming clarity) | NON-BLOCKING | none (purely cosmetic) |

No objectively new scientific question was found during this capability-level analysis beyond what the FRA and SDA already recorded. The closest candidate considered and rejected as genuinely new: whether CAP-003's naming decision should be resolved independently of or jointly with CAP-007's formula evaluation - this was found to already be implicitly covered by the FRA's own OQ-006-adjacent framing and the SDA's own SOFT, informational DEP-007 edge, and does not constitute a distinct new question.

## 14. Technical Debt Interaction

| Technical Debt Item | Interaction Classification | Rationale |
|---|---|---|
| TD-001 (Canonical Position Source for PnLEngine) | Unverandert (unchanged) | Register Status Deferred, functionally resolved per P2-02A; referenced only by CAP-014 as a contract to preserve; not reopened. |
| TD-002 (Unify `_safe_float` implementations) | Ausserhalb des Scopes | `RiskEngine` has no `_safe_float` method of any kind (FRA Section 27); no capability in this analysis implicates this item. |
| TD-003 (Document Pre-Trade Snapshot Dependency) | Unverandert (unchanged) | Partially Resolved (P2-02A recommendation, register not yet updated); referenced only by CAP-014 as a contract to preserve; not reopened. |
| TD-004 (Lifecycle-based Performance Evaluation) | Ausserhalb des Scopes | `PerformanceEngine`'s statistics model is unaffected by any capability's gap in this analysis, distinct from CAP-015's own scope-protection question. |
| TD-005 (Automated Regression Test Suite) | Ausserhalb des Scopes | Project-wide, explicitly excluded by both the FRA and SDA; no capability targets it. |
| TD-006 (RiskEngine Peak Equity and Drawdown Ownership Duplication) | Betroffen (directly affected) | See objective analysis below. |
| TD-007 (RunLoop Lifecycle Control Surface) | Ausserhalb des Scopes | Unrelated to Risk Ownership; no capability in this analysis references it. |

**Objective analysis of TD-006.** TD-006's own recorded Register description ("RiskEngine independently maintains peak equity and computes drawdown instead of consuming the CanonicalState-owned values, creating duplicate ownership contrary to ADR-006 and ADR-007") was, per P2-03-AD-015, already split into two halves: the Equity/Peak-Equity/Drawdown-input-source half, certified fully resolved by P2-03 (P2-03 Final Certification, Section 32), and the risk-formula half ("max_exposure, min_exposure, max_drawdown thresholds, or regime-dampening multipliers"), explicitly deferred to this unit. This analysis confirms, on direct comparison, that the remaining risk-formula half is an exact match for the combined non-conformance this analysis records under CAP-007 (Risk-Limiting Formula Evaluation Disposition, MISSING) and CAP-008 (TD-006 Risk-Formula-Half Closure, MISSING). No other capability in this fifteen-item catalogue implicates TD-006 directly; CAP-001's Risk Policy Configuration ownership gap is a separate, textually distinct absence (no ADR names the ownership question at all, whereas TD-006 names a specific formula-content defect), related only by proximity, exactly as the FRA's own FR-001 text states ("adjacent to TD-006's risk-formula half... not identical to it"). TD-006's Register entry currently reads "Target Phase: P2-03 / P2-04, Status: Deferred," without further internal subdivision; this analysis does not subdivide or re-scope that entry, and does not change its Status field. This document takes no position beyond what the FRA and SDA already adopted; no Technical Debt Register file edit is made by this document, consistent with the FRA's and SDA's own practice.

## 15. Capability Traceability

| Capability ID | Related FR | Related DEP | Related ADR | Related TD |
|---|---|---|---|---|
| CAP-001 | FR-001 | DEP-006, DEP-008 | ADR-007 | adjacent to TD-006, not identical |
| CAP-002 | FR-002 | DEP-001, DEP-015 | ADR-007 | none |
| CAP-003 | FR-003 | DEP-001, DEP-002, DEP-007 | ADR-007 | none |
| CAP-004 | FR-004 | DEP-002 | ADR-006, Rule OM-006 | none |
| CAP-005 | FR-005 | DEP-003, DEP-004, DEP-009, DEP-010, DEP-011 | ADR-004, ADR-007 | TD-006 (adjacent) |
| CAP-006 | FR-006 | DEP-003 | ADR-004, ADR-007, Rule OM-007 | none |
| CAP-007 | FR-007 | DEP-004, DEP-005, DEP-006, DEP-007, DEP-009, DEP-011, DEP-014, DEP-015 | ADR-007 | TD-006 (direct) |
| CAP-008 | FR-008 | DEP-005, DEP-014 | ADR-006, ADR-007 | TD-006 (direct) |
| CAP-009 | FR-009 | DEP-009 | AI-005, ADR-007 | none |
| CAP-010 | FR-010 | DEP-009, DEP-016 | ADR-007, Rule OM-007 | none |
| CAP-011 | FR-011 | DEP-010 | ADR-007 | none |
| CAP-012 | FR-012 | DEP-011 | ADR-011 | none |
| CAP-013 | FR-013 | DEP-008, DEP-016 | AI-010 | none |
| CAP-014 | FR-014 | DEP-012 | ADR-004, ADR-006, ADR-007, ADR-011 | TD-001, TD-003 (compatibility only) |
| CAP-015 | FR-015 | DEP-013 | ADR-008 (by contrast), Runtime Ownership Matrix | none |

## 16. FRA Traceability

Every one of the FRA's fifteen functional requirements is covered by exactly one capability above, a natural 1:1 mapping:

FR-001: CAP-001. FR-002: CAP-002. FR-003: CAP-003. FR-004: CAP-004. FR-005: CAP-005. FR-006: CAP-006. FR-007: CAP-007. FR-008: CAP-008. FR-009: CAP-009. FR-010: CAP-010. FR-011: CAP-011. FR-012: CAP-012. FR-013: CAP-013. FR-014: CAP-014. FR-015: CAP-015.

All fifteen FRA requirements are accounted for, each mapped to exactly one capability, consistent with Section 6's own note that P2-04's requirement set is less redundant than P2-03's and does not require the many-to-one consolidation that document's own fifteen-capabilities-from-twenty-requirements structure needed.

## 17. SDA Traceability

Every one of the SDA's sixteen dependency records is referenced by at least one capability above:

DEP-001: CAP-002, CAP-003. DEP-002: CAP-003, CAP-004. DEP-003: CAP-005, CAP-006. DEP-004: CAP-005, CAP-007. DEP-005: CAP-007, CAP-008. DEP-006: CAP-001, CAP-007. DEP-007: CAP-003, CAP-007. DEP-008: CAP-001, CAP-013. DEP-009: CAP-005, CAP-007, CAP-009, CAP-010. DEP-010: CAP-005, CAP-011. DEP-011: CAP-005, CAP-007, CAP-012. DEP-012: CAP-014. DEP-013: CAP-015. DEP-014: CAP-007, CAP-008. DEP-015: CAP-002, CAP-007. DEP-016: CAP-010, CAP-013.

All sixteen SDA dependency records are accounted for; each is referenced by at least one capability's Related Dependency IDs field (Section 7, Section 15).

## 18. ADR Traceability

| ADR / Invariant / Rule | Related Capabilities |
|---|---|
| ADR-004 (Position Represents Current Market Exposure) | CAP-005, CAP-006, CAP-014 (compatibility only) |
| ADR-006 (Canonical Financial State Ownership) | CAP-004, CAP-008, CAP-014 (compatibility only) |
| ADR-007 (Risk Evaluation as a Pure Computational Layer) | CAP-001, CAP-002, CAP-003, CAP-005, CAP-006, CAP-007, CAP-008, CAP-009, CAP-010, CAP-011, CAP-014 (compatibility only) |
| ADR-008 (Performance Ownership) | CAP-015 (by contrast only) |
| ADR-011 (Runtime Failure Handling) | CAP-012, CAP-014 (compatibility only) |
| AI-005 (Deterministic Execution) | CAP-009 |
| AI-010 (Financial Consistency, extended by analogy) | CAP-013 |
| AI-002 (Unique Ownership) | CAP-001, CAP-003 (preserved, not violated) |
| AI-013 (Architectural Minimality) | all fifteen capabilities (granularity check, Section 8) |
| AC-003 (Separation of Ownership and Computation) | CAP-002 |
| AC-007 (Risk Evaluation) | CAP-006, CAP-009, CAP-010, CAP-011 |
| Rule OM-006 (CanonicalState exclusively owns active runtime state) | CAP-004 |
| Rule OM-007 (RiskEngine owns no runtime information) | CAP-006, CAP-010 |
| Runtime Ownership Matrix ("Risk Metrics" row) | CAP-003, CAP-004, CAP-015 |

Every ADR, Invariant, Rule, and Acceptance Criterion named as binding by the FRA (Section 3 of that document) and the SDA (Section 3 of that document) is accounted for above, either by direct capability association or by an explicit note confirming it is already satisfied, out of scope, or a compatibility-only reference.

## 19. Technical Debt Traceability

All seven Technical Debt Register items are classified in Section 14: TD-001 (unverandert), TD-002 (ausserhalb des Scopes), TD-003 (unverandert), TD-004 (ausserhalb des Scopes), TD-005 (ausserhalb des Scopes), TD-006 (betroffen), TD-007 (ausserhalb des Scopes). No Technical Debt Register item is left unclassified. TD-006 additionally receives an explicit, objective, non-status-changing analysis (Section 14) as required by the governing task.

## 20. Overall Capability Readiness / Readiness Assessment for the Architecture Phase

Of fifteen Risk Ownership capabilities: nine are already COMPLETE (CAP-002, CAP-004, CAP-006, CAP-009, CAP-010, CAP-011, CAP-012, CAP-014, CAP-015), requiring no further work beyond ordinary re-verification once CAP-005/CAP-007 resolve. Three are MISSING as decision-artifact capabilities (CAP-005, CAP-007, CAP-008) - not as absent runtime objects, but as absent governance-chain decisions or evaluations, in every case built atop already-functioning, already-correct mechanical scaffolding. Three are PARTIAL (CAP-001, CAP-003, CAP-013), in every case because the underlying mechanism already exists and works correctly, and only an ADR-level ownership-naming decision or a downstream, conditionally-gated determination remains.

No capability in this analysis was found to require a new scientific investigation beyond the FRA's and SDA's own seven Open Questions (Section 13); no capability was found to require a new Technical Debt Register entry beyond TD-006, already logged (Section 14); no capability was found to contradict the SDA's own two-small-clusters dependency structure (Section 11). No capability in this analysis was found to violate any Architecture Invariant, Acceptance Criterion, Runtime Ownership Matrix row, or Ownership Rule (Section 8) - a materially cleaner baseline than the P2-03 CGA's own conclusion, directly attributable to P2-03's own certified closure of TD-006's ownership-duplication half. Exactly one capability (CAP-003, Risk Metric Ownership Naming) possesses a genuinely open scientific-definition question rather than a purely implementation-detail or governance-record question, mirroring the P2-03 CGA's own CAP-006 (Drawdown Ratio Ownership) finding in shape, though not resolved here either.

Readiness: READY. This document is sufficient to proceed to the P2-04 Architecture stage, where the four Open Questions this analysis and its predecessors have classified as CONDITIONALLY BLOCKING (OQ-001, OQ-002, OQ-003, OQ-005) must be resolved before Specification-level interface design can proceed for CAP-001, CAP-005, CAP-007, CAP-008, CAP-013, and CAP-015's own external boundary question. No further Capability Gap investigation is required before that step.

## 21. Internal Consistency Review

### 21.1 Scientific Consistency Review

Every scientific term used in this document ("Capability," "Current Status," "Gap," "Target Capability," "COMPLETE," "PARTIAL," "MISSING," "runtime-object capability," "decision-artifact capability") is used exactly as defined in Section 5, applied consistently across all fifteen capability entries. No capability entry introduces a new scientific claim, formula, or numeric value; every claim traces to an FRA requirement, an SDA dependency, an ADR/Invariant/Rule/Acceptance-Criterion citation, or the Technical Debt Register. The decision-artifact extension to the COMPLETE/PARTIAL/MISSING vocabulary (Section 5) is grounded directly in the FRA's own SHALL-wording for FR-005, FR-007, and FR-008, not independently invented. Status: PASS.

### 21.2 Architecture Integrity Review

Every capability's Related ADR/Invariant/Rule field was checked against the actual text of `RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md` and against the already-corrected citation set the SDA itself established (its own Section 29.2 review, which had found and fixed one AI-001/AC-003 mismatch): ADR-004, ADR-006, ADR-007, ADR-008, ADR-011, Rule OM-006, Rule OM-007, AI-002, AI-005, AI-010, AI-013, AC-003, and AC-007 are used identically to the SDA's own corrected set, with no new citation introduced that was not already verified there. No capability recorded in this document proposes relocating an Authoritative Owner or Computational Authority away from its currently-assigned component; every COMPLETE capability's Section 7 entry restates an already-true assignment, and every PARTIAL/MISSING capability's entry identifies an absence, never a misassignment. Status: PASS.

### 21.3 Terminology Review

"Byte-identical" and "byte-for-byte" are not used anywhere in this document to describe a comparison (their only occurrence is this sentence's own meta-discussion of the terms); no comparison of Python objects, runtime dictionaries, source files, or numeric results is described anywhere in this document, since this document performs capability-gap determination, not runtime verification. "COMPLETE," "PARTIAL," and "MISSING" are each used with exactly one fixed meaning throughout (Section 5); no capability is described using informal synonyms ("done," "finished," "broken") in place of these three values. "Runtime-object capability" and "decision-artifact capability" are each used consistently with their Section 5 definitions. Status: PASS.

### 21.4 Traceability Review

All fifteen FRA functional requirements map to exactly one capability each (Section 16), cross-checked requirement by requirement. All sixteen SDA dependency records are referenced by at least one capability (Section 17), cross-checked dependency by dependency. All seven FRA Open Questions are classified against interacting capabilities (Section 13); none is left unclassified. All seven Technical Debt Register items are classified (Section 14, Section 19); none is left unclassified. Capability-ID uniqueness: P2-04-CAP-001 through P2-04-CAP-015 are each defined exactly once (Section 7) and referenced only by ID thereafter (Sections 8 through 20); no ID collision or reuse was introduced. Status consistency: Section 6's summary table, Section 7's per-capability Current Status fields, Section 9's gap catalogue (which omits COMPLETE capabilities by construction), and Section 10's matrix (which likewise omits them) agree exactly: nine COMPLETE, three MISSING, three PARTIAL. Status: PASS.

### 21.5 Governance Review

No new functional requirement was created, removed, or modified; the fifteen FRA requirements are referenced exclusively by their existing IDs and existing text throughout this document. No architecture decision was made: every capability's eventual resolution (interface shape, formula shape, storage mechanism, publication decision) is left explicitly open, consistent with Section 7's own "not applicable" fields for Ownership/CanonicalState/Computational-Authority/Writer-on-Behalf-Of coverage wherever a decision, not a fact, remains pending. No new ADR was introduced. No implementation was performed and no code file was modified (Section 4's re-verification confirms `run_engine/` unchanged throughout drafting). No Specification-level interface detail, data structure, or formula was proposed. No Technical Debt Register status was changed (Section 14 explicitly confirms this, consistent with the FRA's and SDA's own practice). Status: PASS.

## 22. Independent Self Verification

**Repository state, re-verified at the close of drafting, not assumed carried over from Section 4:** branch `run-engine-consolidation-safety`; HEAD `a81e1978cb07bbb26223c94a1b24e9220520c445`; `run_engine/` clean; no commit made during this document's drafting; no push made.

**Mechanical checks performed (results recorded, not merely claimed - see the accompanying command output for this session):** byte-level scan for non-ASCII bytes and trailing whitespace across the full document; `python -m compileall run_engine` re-run, confirming this documentation-only work produced zero runtime effect; `git diff --check` against the new file; a grep for `FR-[0-9]{3}` confirming all fifteen IDs FR-001 through FR-015 are each referenced; a grep for `P2-04-CAP-[0-9]{3}` confirming exactly fifteen unique capability IDs, each defined exactly once (Section 7); a grep for `P2-04-DEP-[0-9]{3}` confirming all sixteen SDA dependency IDs are referenced somewhere in this document, none fabricated.

**Citation accuracy check:** every ADR, Invariant, Rule, and Acceptance Criterion cited in this document was drawn from the SDA's own already-corrected citation set (its Section 29.2), not re-derived independently, avoiding re-introduction of the AI-001/AC-003 error the SDA itself found and fixed.

**Scope-boundary check:** re-read of Sections 2, 8, and 20 confirms no capability entry pulls P2-03 (Drawdown/Drawdown-Ratio/Equity/Peak-Equity ownership), P2-02A (Position/Exposure ownership), P3-03 (PerformanceEngine redesign), TD-005 (regression suite), or repository cleanup into this document's own analytical scope; each is recorded only as an external or compatibility-preservation reference.

**Cross-document consistency check:** every FR-001 through FR-015 requirement statement paraphrased in this document (Section 7) was compared against the current, corrected text of `P2_04_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-13.md`, and every DEP-001 through DEP-016 dependency referenced was compared against the current, corrected text of `P2_04_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-13.md`; both were found consistent, since this document was drafted after, and reflects, both documents' own corrected states.

**Result:** one error was found and corrected during this final mechanical-check pass: Section 21.3's own Terminology Review had initially claimed "byte-identical" and "byte-for-byte" "do not appear anywhere in this document," which was false in the same self-referential way the SDA's own Section 29.3 first drafted and then corrected - the claiming sentence itself necessarily contains the terms it discusses. Corrected in place to state the terms are not used to describe a comparison, with the sole occurrence being that sentence's own meta-discussion. All other findings from this document's own internal reviews (Section 21) are PASS with no further correction required. This document's own citations were substantially inherited, pre-verified, from the SDA's own corrected set rather than independently re-derived from source text a third time, which reduced but did not eliminate the risk of repeating a prior drafting artifact.

**Status: Independent Self Verification PASS.**

No commit was made. No runtime file was changed. No push was made. This document is ready to be provided as `P2_04_CAPABILITY_GAP_ANALYSIS_V1_2026-07-13.md`.
