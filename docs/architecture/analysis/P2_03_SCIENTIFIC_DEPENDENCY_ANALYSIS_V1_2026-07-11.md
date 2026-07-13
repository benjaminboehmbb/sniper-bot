Document Class:
Scientific Dependency Analysis

Document ID:
P2-03-SDA

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
docs/architecture/analysis/P2_03_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-11.md

Depends On:
- docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md
- docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md
- docs/architecture/analysis/P2_03_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-11.md
- docs/architecture/certification/P2_02A_FINAL_CERTIFICATION_V1_2026-07-10.md
- docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md
- current runtime code at HEAD 815cd8a

Referenced By:
- future P2-03 Capability Gap Analysis
- future P2-03 Architecture
- future P2-03 Specification
- future P2-03 Certification

---

# P2-03 Scientific Dependency Analysis

## 1. Purpose

This document performs the Scientific Dependency Analysis for P2-03 (Financial Ownership), following directly from `P2_03_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-11.md` (Status: Draft for Internal Review, Functional Readiness: READY).

This document does not perform Capability Gap Analysis. It does not make architecture decisions. It does not select an implementation mechanism. It does not specify interfaces. It does not implement code. Its sole purpose is to determine the scientific, semantic, state-related, and architectural dependency structure among the twenty functional requirements (P2-03-FR-001 through P2-03-FR-020) already established by the FRA, and to derive the resulting logical ordering of future decisions.

No functional requirement is created, removed, or modified by this document. No Open Question already recorded by the FRA is resolved by this document; each is instead classified by its blocking effect on the dependency structure derived here.

## 2. Scope

In scope: dependency analysis of Event Realized PnL, Cumulative Realized PnL, Equity, Peak Equity, Drawdown, Drawdown Ratio, Canonical Financial State, Financial Publication, Risk Consumption, Performance Consumption, RuntimeFailureEvent non-mutation, Reset, Determinism, Replay, Canonical Ownership, Computational Authority, and Derived Views, as these relate to the twenty FRA functional requirements.

Out of scope: everything the FRA itself placed out of scope (Section 24 of that document) - full RiskEngine redesign, Risk Policy, Position Sizing, full PerformanceEngine redesign, Unrealized PnL and Mark-to-Market Portfolio Valuation unless explicitly brought into scope by a later governing document, Multi-Asset Accounting, Fees/Funding/Slippage/Tax Accounting, Persistence, Recovery, the Tick-Complete Snapshot architecture beyond what is already implemented, repository cleanup, and the automated regression test suite (TD-005). No implementation order, file order, or code change is proposed anywhere in this document.

## 3. Binding Inputs

- `docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md` - ADR-005, ADR-006, ADR-007, ADR-002, ADR-008, ADR-010, ADR-011, the Runtime Ownership Matrix, Rules OM-001 through OM-009, Architecture Invariants AI-005 and AI-010, and the "Derived View" definition ("A Derived View is reconstructed from authoritative runtime information. Derived Views possess no independent ownership. They may be regenerated at any time.").
- `docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md` - the P2-03 unit definition and Principle IP-002 (Single Logical Change; repository-wide modifications prohibited).
- `docs/architecture/analysis/P2_03_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-11.md` - the twenty functional requirements, six Required Capabilities (RC-1 through RC-6), and twelve Open Questions (OQ-001 through OQ-012), all as internally reviewed (Status: Internal Consistency Review PASS).
- `docs/architecture/certification/P2_02A_FINAL_CERTIFICATION_V1_2026-07-10.md` - the certified contract baseline this analysis treats as immutable (Cluster H, Section 15).
- `docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md` - TD-006, TD-001 through TD-005, TD-007.
- Current runtime code at HEAD `815cd8a`, relied upon only through the FRA's own repository-grounded findings (Section 4 below); no new repository claim is introduced by this document.

## 4. Verified Functional Baseline

Repository state re-verified for this analysis: branch `run-engine-consolidation-safety`, HEAD `815cd8a`, matching the FRA's own verification exactly. `run_engine/` remains clean (`git status --short run_engine/` returns no output).

This analysis relies on the FRA's Section 6 through Section 23 findings without re-deriving them from the code a second time. Every dependency record below cites the specific FRA section, requirement ID, or Architecture Baseline ADR/Invariant that grounds it, rather than re-quoting source code.

One structural observation, not present in the FRA itself but directly derived from it, governs the shape of this entire analysis: unlike P2-02A, where the scientific definition of Position-derived Exposure (OQ-001) was itself an unresolved, BLOCKING open question that gated an entire track of downstream work, P2-03 presents no such gap. The governing Architecture Baseline already establishes the intended architectural concepts for the relevant financial objects. Remaining work concerns ownership consolidation, dependency resolution and operational realization rather than semantic definition. The FRA's Section 5 (Scientific Definitions) restates these already-established concepts without needing to resolve any of them itself. Consequently, P2-03's dependency structure is not gated by any unresolved semantic-definition question of the kind that dominated P2-02A's SDA; it is instead dominated almost entirely by ownership-relocation dependencies (Computational Authority moving to `PnLEngine`, `RiskEngine`'s Peak Equity ownership being removed) among already-well-defined quantities. This finding is confirmed in Section 16 (Open Question Classification) below: no Open Question in this cycle is classified BLOCKING.

## 5. Dependency Analysis Method

Each of the eight capability clusters (A through H, mapped onto Sections 7 through 14) is analyzed using the following method, applied compactly per cluster:

1. Capability Definition
2. Prerequisites, grouped as: Scientific, Semantic, State, Ownership, Information-Flow, Determinism, Compatibility
3. Dependent Capabilities (what this cluster unlocks or constrains)
4. Failure if Introduced Too Early (concrete failure mode from wrong ordering)
5. Necessity Tests: Minimality Assessment, Removal Test, Compression Test, Counterfactual Review, combined into one judgment per cluster

A dependency is recorded in the Dependency Graph (Section 17) only when it survives its own Removal Test (removing the source requirement would make the target requirement's correct resolution impossible or unverifiable, not merely inconvenient). Two distinct relationship kinds are used throughout, consistent with the FRA's own "lock-in" language (its Sections 16, 19, 20 record requirements that are already conformant and must be preserved, not achieved): a PREREQUISITE edge (source must be resolved before target can be correctly resolved or verified) and a CONSTRAINT edge (source is already true and bounds how target may be resolved, without target having to wait for source). Constraint edges are excluded from the sequencing cycle check (Section 17.1), exactly as the P2-02A SDA excluded its cross-cutting Cluster I from its own cycle check.

## 6. Capability Cluster Catalogue

| Cluster | Name | One-line definition | FRA Requirements |
|---|---|---|---|
| A | Financial State Definition | The scientific status of each financial quantity's definition - already-settled versus genuinely open - bounded against Performance Metrics and Risk Metrics | FR-001, FR-004, FR-012, FR-020 |
| B | Financial Ownership | Relocating Computational Authority for Realized PnL (cumulative), Equity, and Peak Equity into `PnLEngine`, and removing `RiskEngine`'s competing Peak Equity tracker | FR-002, FR-005, FR-008, FR-009 |
| C | Canonical Publication | `CanonicalState` as Authoritative Owner and sole storage location for every financial value, including the one new storage location required and the single-source Initial Capital requirement | FR-003, FR-006, FR-011, FR-017 |
| D | Drawdown Correctness | Correcting `RiskEngine`'s Drawdown and Drawdown Ratio input source from its own internally-tracked copy to canonical financial state | FR-010 |
| E | Consumer Boundaries | `RiskEngine` and `PerformanceEngine` remaining strictly read-only consumers of financial state, never owners | FR-013, FR-014 |
| F | Financial Consistency | Internal consistency of the Equity formula, RuntimeFailureEvent non-mutation, and complete reset semantics across all financial-adjacent state (the AI-010 family of consistency properties) | FR-007, FR-015, FR-018 |
| G | Replay / Determinism | Deterministic, reproducible financial values for identical lifecycle histories | FR-016 |
| H | Compatibility | The frozen set of already-certified P1-03/P1-03.1/P1-04/P2-01/P2-02/P2-02A contracts constraining every other cluster, cross-cutting and non-sequential | FR-019 |

This clustering follows the task's own suggested cluster names (Financial State Definition, Financial Ownership, Canonical Publication, Consumer Boundaries, Replay / Determinism, Financial Consistency) with two scientifically-justified refinements: Drawdown Correctness (Cluster D) is separated from Financial Ownership (Cluster B) because it addresses an input-source defect in an already-correctly-assigned Computational Authority (`RiskEngine` is already the ADR-006-mandated Computational Authority for Drawdown; only its input source is wrong), a qualitatively different problem from relocating Computational Authority itself (Cluster B); and Compatibility (Cluster H) is added, mirroring the P2-02A SDA's own Cluster I, to hold FR-019's cross-cutting constraint, which does not belong thematically to any of the six build-facing clusters.

Cluster A and Cluster H are, per Sections 7 and 14 below, either already largely satisfied or a constant, non-sequential constraint layer; they function as a fixed reference frame rather than as pending sequential work, in the same sense the P2-02A SDA treated its own Cluster A and Cluster I.

## 7. Financial State Definition Dependencies (Cluster A)

Capability Definition: the scientific status of Realized PnL (event and cumulative), Equity, Peak Equity, and Drawdown as already-defined quantities (per ADR-005/ADR-006), distinguished from the two genuinely open definitional questions this document's source FRA identified: Drawdown Ratio's ADR-level ownership assignment (FR-012) and whether Unrealized PnL/Mark-to-Market Equity is in scope (FR-020).

Prerequisites: Scientific - none pending for Realized PnL (event/cumulative), Equity, and Peak Equity; ADR-005 and ADR-006 already define all four textually and completely (FRA Section 5). FR-012 (Drawdown Ratio) and FR-020 (Unrealized PnL scope) remain open, but neither is a prerequisite for anything outside this cluster to proceed, since no other FR's Validation Condition depends on either being resolved (FRA Sections 18, 26). Semantic - FR-004 (event-versus-cumulative distinguishability) is a semantic-clarity requirement that presupposes both quantities exist and are separately stored, which they do not yet (FRA Section 6, item 7); this places FR-004 in a HARD dependency on Cluster B and Cluster C (Section 17, DEP-004). State - Realized PnL (event)'s state is already fully established (`PnLEngine.last_realized_pnl`, FRA Section 7). Ownership - already correctly assigned for Realized PnL (event); not yet resolved for Realized PnL (cumulative), Equity, or Peak Equity (Cluster B's territory). Information-Flow - none new. Determinism - the already-settled definitions impose no new determinism requirement beyond Cluster G. Compatibility - FR-001's already-conformant status must not be silently regressed by any Cluster B work (Section 17, DEP-018).

Dependent Capabilities: Cluster A supplies the definitional ground truth every other cluster's Validation Conditions cite (ADR-005/ADR-006's formulas, quoted verbatim throughout FRA Sections 15-23); it does not itself depend on any other cluster being resolved first.

Failure if Introduced Too Early: not applicable in the P2-02A sense (Cluster A is not being introduced, it is re-verified and, for FR-012/FR-020, explicitly left open). The relevant failure mode is scope drift: if FR-012 or FR-020 were silently treated as resolved by a later document without explicit architectural ratification, this would violate the FRA's own scope-protection framing (FRA Sections 20, 23).

Necessity Tests: Removal Test fails to remove Cluster A - without a stable reference for what each quantity scientifically means, Clusters B through G would have no target to correctly relocate ownership toward. Compression Test - Cluster A cannot be merged into Cluster B without conflating "what a quantity means" with "who computes it," the same distinction the Architecture Baseline's own Rule OM-002 (Computational Authority may differ from Authoritative Owner) already protects structurally. Counterfactual Review - if Cluster A's already-settled definitions were treated as still-open, every other cluster's Validation Conditions (which quote ADR-005/ADR-006 verbatim) would become unverifiable. Conclusion: Cluster A is a necessary, almost entirely already-satisfied prerequisite; only FR-012 and FR-020 remain genuinely open, and neither blocks any other cluster.

## 8. Financial Ownership Dependencies (Cluster B)

Capability Definition: relocating Computational Authority for Realized PnL (cumulative) (FR-002), Equity (FR-005), and Peak Equity (FR-008) into `PnLEngine`, consistent with ADR-005's and ADR-006's explicit, repeated textual assignment, and removing `RiskEngine`'s independently-tracked Peak Equity state (FR-009).

Prerequisites: Scientific - Cluster A must be stable for the three relocated quantities (satisfied). Semantic - none pending; the target Computational Authority (`PnLEngine`) is already named by both governing ADRs, unlike P2-02A's OQ-004 (RiskEngine parameter reuse-versus-redesign), which required a choice among candidates. State - `PnLEngine`'s current instance state (`self.last_realized_pnl` only, FRA Section 7) does not yet include Equity or Peak Equity in any form; this is the precise gap FR-005/FR-008 close. Ownership - the central open question is not "which component" (already answered by ADR-005/ADR-006) but "how to relocate without breaking the already-correct storage location," addressed by Cluster C's constraint relationship (Section 17, DEP-001, DEP-002). Information-Flow - FR-009's removal of `RiskEngine`'s internal Peak Equity tracker requires, simultaneously, that Drawdown's input source be redirected to canonical state (Cluster D), or Drawdown becomes uncomputable (Section 17, DEP-008); this is the one genuine HARD internal pairing within this cluster's boundary. Determinism - relocating computation must not introduce new ordering dependency (Cluster G's validation condition, FRA FR-016). Compatibility - FR-006/FR-011 (Cluster C) already correctly assign storage location; Cluster B's relocation must preserve this, not change it (constraint, not blocking).

Dependent Capabilities: Cluster C's value-correctness half for the new cumulative-PnL storage location (FR-003) requires FR-002 to exist first (Section 17, DEP-003); Cluster F's re-verification of RuntimeFailureEvent non-mutation for the newly-relocated quantities (FR-015) requires FR-002/FR-005/FR-008 (Section 17, DEP-010, DEP-011); Cluster D's Drawdown input-source fix (FR-010) is informed, but not hard-gated, by FR-008 (Section 17, DEP-007); Cluster E's consumer-boundary verification (FR-013) requires FR-009 and FR-010 together (Section 17, DEP-009).

Failure if Introduced Too Early: not applicable in the sense of a missing prerequisite (Cluster A already supplies everything Cluster B needs); the relevant risk is the inverse - if FR-009 (removing `RiskEngine`'s own Peak Equity tracker) is implemented without FR-010 (redirecting Drawdown's input source) landing simultaneously, Drawdown becomes computable from no source at all, a functional regression more severe than the current TD-006 duplication it replaces.

Necessity Tests: Removal Test fails to remove Cluster B - without it, ADR-005's and ADR-006's Decision text ("PnLEngine SHALL become the exclusive Computational Authority for: Realized PnL, Unrealized PnL, Equity, Peak Equity") remains unmet regardless of how well Clusters C through H are resolved. Compression Test - Cluster B cannot be merged into Cluster D, since B concerns WHO computes Equity/Peak Equity while D concerns WHERE `RiskEngine` reads its Drawdown input from - the same Rule OM-002 distinction. Counterfactual Review - the relocation could in principle be implemented with `PnLEngine` gaining either a single combined method or three separate methods (OQ-001, OQ-002, OQ-004, OQ-005 remain open on this point), but Cluster B's underlying ownership requirement is unaffected by which interface shape is eventually chosen. Conclusion: Cluster B is the central, currently-unresolved cluster of this unit; hard-gated only by Cluster A (already satisfied) and internally by its own FR-008-to-FR-009 pairing.

## 9. Canonical Publication Dependencies (Cluster C)

Capability Definition: `CanonicalState` as the sole Authoritative Owner and storage location for every financial value, comprising two already-conformant lock-in requirements (FR-006 for Equity, FR-011 for Drawdown), one requirement needing a genuinely new storage location (FR-003, for Realized PnL cumulative), and one single-source consolidation requirement for the Initial Capital literal (FR-017).

Prerequisites: this cluster splits into two internally separable sub-problems with materially different prerequisite structures, mirroring the P2-02A SDA's own D1/D2 split for Canonical Position Ownership.

Sub-problem C1 (already-conformant storage, FR-006, FR-011): Scientific/Semantic - none pending; both are pure preservation requirements, not new work (FRA Sections 19, 21). State/Ownership/Information-Flow/Determinism/Compatibility - all already satisfied; no open decision blocks these.

Sub-problem C2 (new storage location, FR-003, and single-sourcing, FR-017): Scientific - FR-003's key-existence half (adding a new `CanonicalState` field, with some default value) requires no prerequisite and could be established independently of Cluster B; FR-003's value-correctness half (the published value under that key actually being `PnLEngine`'s computed cumulative sum, not a placeholder) requires FR-002 to exist first (Section 17, DEP-003) - the identical shape-versus-value distinction the P2-02A Architecture already applied to Position's own default-shape fix. FR-017 is largely ungated (a single-source Initial Capital definition can be established independently of Cluster B's relocation work), though its exact final form is informed by whether FR-008/FR-009's disposition eliminates the specific duplication FR-017 currently targets (Section 17, DEP-014, a SOFT relationship).

Dependent Capabilities: Cluster A's FR-004 (distinguishability) requires C2's FR-003 to exist (Section 17, DEP-004); no other cluster depends on Cluster C beyond respecting its already-conformant assignments as constraints (Section 17, DEP-001, DEP-002).

Failure if Introduced Too Early: attempting to resolve C2's value-correctness half (publishing a real cumulative-PnL value) before Cluster B's FR-002 exists would require either a placeholder value (reproducing exactly the kind of premature-computation risk the P2-02A SDA flagged for its own Cluster H) or an incorrect manual computation duplicated outside `PnLEngine`, which would itself constitute a new ownership violation.

Necessity Tests: Removal Test fails to remove Cluster C - even with Cluster B fully resolved, ADR-006's Acceptance Criterion ("CanonicalState contains exactly one canonical financial state") remains formally unmet without an explicit storage location for the newly-computed cumulative value. Compression Test - C1 and C2 are legitimately separable (C1 requires no open decision and could be reconfirmed immediately; C2's value-correctness half is decision-gated by Cluster B), so treating Cluster C as monolithic would overstate its blocking character; this document records the internal split explicitly, consistent with the P2-02A SDA's own precedent for its analogous cluster. Counterfactual Review - without Cluster C, Cluster B's relocated computation would have no canonical home for its new cumulative-PnL output, and the already-correct storage assignments for Equity/Drawdown (FR-006/FR-011) would have no explicit constraint protecting them from accidental relocation during Cluster B's implementation. Conclusion: Cluster C is necessary; C1 is unblocked and already satisfied, C2's shape-only portion is unblocked, and C2's value-correctness portion is hard-gated by Cluster B's FR-002.

## 10. Drawdown Correctness Dependencies (Cluster D)

Capability Definition: correcting `RiskEngine`'s Drawdown and Drawdown Ratio computation (FR-010) to read Peak Equity and Equity from canonical financial state, rather than from `RiskEngine`'s own internally-tracked copy - the Computational Authority assignment (`RiskEngine`) is already correct per ADR-006; only the input source is wrong (FRA Section 10).

Prerequisites: Scientific - none pending; ADR-006's text ("RiskEngine SHALL calculate Drawdown exclusively from canonical financial state") is unambiguous about both the correct computing component and the correct input source. Semantic - none pending. State - requires a canonically-correct, singly-owned Peak Equity value to read from; today, `CanonicalState.state["peak_equity"]` is already numerically correct (FRA Section 9, Computation 1), so FR-010 does not hard-depend on FR-008 (Cluster B) having relocated Peak Equity's Computational Authority into `PnLEngine` first - it is already reading a numerically-trustworthy value today, even though that value's own Computational Authority (currently `CanonicalState.update_equity()`) is itself non-conformant. This is recorded as a CONDITIONAL, not HARD, dependency (Section 17, DEP-007), directly analogous to the P2-02A SDA's own DEP-009 (RiskEngine's read-path fix does not strictly require its co-consumers to be migrated first). Ownership - FR-010 and FR-009 (Cluster B) form a HARD, mutual pairing: removing `RiskEngine`'s internal Peak Equity tracker (FR-009) without redirecting Drawdown's input source (FR-010) leaves Drawdown with no input at all (Section 17, DEP-008). Information-Flow - `RiskEngine.check()` already receives `state` (`canonical_state = self.cstate.get()`) as a parameter containing `peak_equity`; no new parameter or call-site change is implied. Determinism - trivially satisfied, since the corrected read remains read-only. Compatibility - must not touch `RiskEngine`'s Equity/Drawdown_ratio formula shape or its regime-dampening/`max_exposure`/`min_exposure` logic, none of which this cluster's single requirement (FR-010) implicates (FRA Section 24's explicit P2-04 scope boundary).

Dependent Capabilities: Cluster E's FR-013 (RiskEngine strictly read-only) is verifiably true only once Cluster D's FR-010 and Cluster B's FR-009 have both landed (Section 17, DEP-009); until then, "read-only consumption" cannot be distinguished from "read-only consumption of a value the same component also independently tracks," which is not the same property.

Failure if Introduced Too Early: resolving FR-010 (redirect the read) without FR-009 (remove the internal tracker) leaves a dormant, unused `self.peak_equity` attribute that could silently re-diverge if any future code path reintroduces a read of it - a smaller but structurally identical risk to TD-006 itself, only relocated rather than eliminated. Resolving FR-009 without FR-010 breaks Drawdown outright (Section 8, Section 17 DEP-008).

Necessity Tests: Removal Test fails to remove Cluster D - it is explicitly named, twice, in the P2-03 Baseline objective text itself ("Verify Equity, Peak Equity and Drawdown consistency") and in ADR-006's Decision text; without it, TD-006's Drawdown half remains unresolved regardless of how completely Cluster B relocates Equity/Peak-Equity ownership. Compression Test - Cluster D cannot be compressed into Cluster B, since B concerns Computational Authority relocation for values `RiskEngine` never owned in the target model, while D concerns correcting the input source for a value `RiskEngine` correctly does own (Drawdown itself) - the Rule OM-002 distinction applies in the opposite direction from Cluster B's own reasoning. Counterfactual Review - without Cluster D, TD-006 would remain half-resolved even after Cluster B's relocation work completes, since `RiskEngine` could still, in principle, retain its own internally-tracked Peak Equity purely for Drawdown computation, reproducing the exact duplicate-ownership pattern this unit exists to close. Conclusion: Cluster D is a small but necessary, currently-unresolved cluster, conditionally informed by Cluster B's FR-008 and hard-paired with Cluster B's FR-009.

## 11. Consumer Boundary Dependencies (Cluster E)

Capability Definition: `RiskEngine` (FR-013) and `PerformanceEngine` (FR-014) remaining strictly read-only consumers of canonical financial state, never acquiring ownership, consistent with ADR-007's "Risk Evaluation does not create runtime truth" and ADR-008/Rule OM-008's performance-evaluates-outcomes-not-state framing.

Prerequisites: Scientific - Cluster A (satisfied). Semantic - none pending. State - FR-014 is already fully satisfied today (`PerformanceEngine` has never held any financial-state-owning field, FRA Section 11); FR-013 cannot be verified as true until Cluster B's FR-009 and Cluster D's FR-010 have both landed, since `RiskEngine` currently does independently track Peak Equity, which is the precise condition FR-013 prohibits (Section 17, DEP-009). Ownership - the entire content of this cluster's still-open half (FR-013) is a restatement, from the consumer-boundary angle, of Cluster B's FR-009 and Cluster D's FR-010; this document records the relationship explicitly rather than merging the two framings into one requirement, since the FRA's own catalogue (Section 25) keeps them as separate, distinctly-IDed requirements. Information-Flow - none new; `RiskEngine.check()`'s existing `state`/`position`/`regime` parameters already carry everything FR-013 requires. Determinism - trivially satisfied for a read-only boundary. Compatibility - FR-014's already-conformant status must not be disturbed by any Cluster B/D implementation choice (constraint).

Dependent Capabilities: none further; Cluster E is a verification-only cluster with respect to FR-013, and an already-closed cluster with respect to FR-014.

Failure if Introduced Too Early: verifying FR-013 "true" before Cluster B/D actually land would produce a false-positive certification, since the read-only property cannot be meaningfully distinguished from a coincidentally-non-diverging dual-tracker arrangement (the exact situation the FRA's Section 9 already documents as presently true today, by coincidence, not by architectural guarantee).

Necessity Tests: Removal Test fails to remove Cluster E - without an explicit consumer-boundary requirement, a future implementation could satisfy Cluster B/D's letter (relocate the primary computation) while still allowing `RiskEngine` to retain a vestigial, unused tracker, which would not violate FR-009's specific wording as narrowly as intended without FR-013's independent framing reinforcing it. Compression Test - Cluster E could be merged into Cluster B/D, but is kept separate because it verifies a property (read-only consumption) rather than performing a relocation (the same Purpose-versus-Verification distinction the P2-02A SDA applied to its own Cluster F/Cluster H split). Counterfactual Review - without Cluster E, "read-only consumer" would remain an informal expectation rather than an explicitly verified requirement, weakening the audit trail TD-006's closure will require. Conclusion: Cluster E is necessary as a verification layer; FR-014 is already satisfied, FR-013 is hard-gated by Cluster B's FR-009 and Cluster D's FR-010 together.

## 12. Financial Consistency Dependencies (Cluster F)

Capability Definition: the AI-010 ("Financial Consistency") family of properties - Equity formula consistency (FR-007), RuntimeFailureEvent non-mutation extended to every financial value including the ones this unit newly relocates or newly creates (FR-015), and complete, consistent reset semantics across every component holding financial-adjacent state (FR-018).

Prerequisites: Scientific - Cluster A (satisfied for the terms FR-007's formula names; FR-020's Unrealized-PnL-scope question conditionally affects FR-007's exact validation, Section 17 DEP-013). Semantic - none pending beyond Cluster A. State - FR-007 requires Realized PnL (cumulative) to exist as a distinct, correctly-tracked value (Cluster B's FR-002) before its formula-consistency claim (`Equity == Initial Capital + Realized PnL cumulative + Unrealized PnL`) can be independently verified rather than merely assumed from the current incremental running total (Section 17, DEP-005). FR-015 requires the specific financial values it protects to exist under their new ownership before their non-mutation under `RUNTIME_FAILURE_EVENT` can be meaningfully re-verified: the new cumulative-PnL field (Cluster B's FR-002, Section 17 DEP-010) and the relocated Equity/Peak-Equity computation (Cluster B's FR-005/FR-008, Section 17 DEP-011); Realized PnL (event)'s own non-mutation is already certified and does not need re-verification. FR-018 requires knowing which components hold financial-adjacent instance state after Cluster B's FR-009 is resolved (does `RiskEngine` retain any local state at all, even transiently, per OQ-006), before the complete reset-scope can be finalized (Section 17, DEP-012). Ownership - none new; this cluster verifies consistency of state already assigned elsewhere. Information-Flow - none new. Determinism - FR-007/FR-015/FR-018's consistency properties are prerequisites for Cluster G's broader determinism claim (Section 17, DEP-015), not the reverse. Compatibility - FR-015 is itself a compatibility-preservation requirement, extending the already-certified P1-04 non-mutation contract (FRA Section 20).

Dependent Capabilities: Cluster G's determinism validation (FR-016) presupposes Cluster F's consistency properties hold, since a formula that is not internally consistent, or a reset that leaves stale state, cannot be deterministic in the sense AI-005 requires.

Failure if Introduced Too Early: attempting to verify FR-015's non-mutation contract for the new cumulative-PnL field before Cluster B's FR-002 creates it would have nothing to verify; attempting to finalize FR-018's reset scope before Cluster B's FR-009 disposition is known risks either resetting a field that no longer exists (if `RiskEngine`'s tracker is fully removed) or missing one that still does (if retained as OQ-006 permits).

Necessity Tests: Removal Test fails to remove Cluster F - without it, AI-010's "Financial runtime state SHALL remain internally consistent... at all times" invariant would not be re-verified against the specific new state Cluster B introduces, leaving a documented invariant unconnected to this unit's own changes. Compression Test - FR-007 (formula), FR-015 (failure non-mutation), and FR-018 (reset) could in principle be tracked as three separate clusters, but are compressed into one here because all three are instances of the identical underlying question - "does financial state remain internally consistent under a specific runtime condition (normal tick, rejected tick, reset)" - matching AI-010's own single-invariant framing rather than three unrelated concerns. Counterfactual Review - without Cluster F, Cluster B's relocation could be implemented in a way that is individually correct per-quantity but produces an internally inconsistent Equity formula, an unverified failure-non-mutation gap for the newly-relocated values, or a reset that leaves the system in a state no fresh initialization would ever produce. Conclusion: Cluster F is necessary, hard-gated by Cluster B's FR-002/FR-005/FR-008 and FR-009 for its three members respectively, and itself gates Cluster G.

## 13. Replay / Determinism Dependencies (Cluster G)

Capability Definition: deterministic, reproducible financial values (Realized PnL event and cumulative, Equity, Peak Equity, Drawdown, Drawdown Ratio) for identical lifecycle histories (FR-016), per ADR-005's and ADR-006's own Acceptance Criteria and AI-005 (Deterministic Execution).

Prerequisites: Scientific - Cluster A (satisfied). Semantic - none pending. State - requires every other build-facing cluster (B, C, D, E, F) to have reached a stable, internally-consistent state before a meaningful determinism claim can be evaluated across the fully-relocated system, rather than only against the currently-certified pre-P2-03 baseline (FRA Section 21 already establishes this baseline evidence; Section 17 DEP-015 records the forward-looking validation dependency). Ownership - none new; determinism is a property of already-assigned ownership, not an ownership assignment itself. Information-Flow - none new. Determinism - this cluster's own subject. Compatibility - FR-016's Validation Condition explicitly requires comparison against the certified pre-P2-03 baseline (FRA Section 21), tying this cluster to Cluster H.

Dependent Capabilities: none further within P2-03; this is a terminal validation cluster, the same role the P2-02A SDA assigned its own Cluster I (Compatibility) at Stage 6, except that here Determinism and Compatibility are kept as two distinct clusters (G and H) because they test different properties (reproducibility under identical inputs, versus preservation of already-certified specific outputs) even though both are validation-only.

Failure if Introduced Too Early: validating FR-016 before Clusters B through F have reached a stable state would test an intermediate, partially-relocated system, producing a determinism result that does not describe the system this unit is actually meant to certify.

Necessity Tests: Removal Test fails to remove Cluster G - without it, ADR-005's and ADR-006's own Acceptance Criteria ("Financial values remain reproducible from identical lifecycle history," "Financial state remains deterministic for identical lifecycle histories") would not be independently re-verified against the relocated ownership model. Compression Test - Cluster G cannot be merged into Cluster F, since F verifies consistency of a single system state at a single point in time while G verifies reproducibility of a full sequence of states across repeated execution - a different scientific question (AI-005 versus AI-010). Counterfactual Review - without Cluster G, Cluster B's relocation could in principle introduce a new hidden ordering dependency (for example, if `PnLEngine`'s new Equity-computing method were accidentally made to depend on call order relative to `RiskEngine`) without any requirement catching it. Conclusion: Cluster G is a necessary, terminal validation cluster, hard-gated by every build-facing cluster (B through F) having reached a stable state.

## 14. Compatibility Dependencies (Cluster H)

Capability Definition: the complete, already-certified set of P1-03, P1-03.1, P1-04, P2-01, P2-02, and P2-02A contracts that constrain every other cluster's eventual implementation (FR-019), cross-cutting and non-sequential, the same role the P2-02A SDA's Cluster I played for that unit.

Prerequisites: Scientific - requires the already-completed P1-03/P1-03.1/P1-04/P2-01/P2-02/P2-02A certification chain to exist as the frozen reference baseline; fully satisfied, verified present at HEAD `815cd8a` (Section 4).

Dependent Capabilities: all of Clusters A through G are constrained by Cluster H; Cluster H does not depend on any of them, since it is a validation/constraint layer defined entirely by already-certified prior work, not a new build target with its own prerequisite chain.

Failure if Introduced Too Early: not applicable in the ordering sense (Cluster H is not sequenced, it is omnipresent); the relevant failure mode is omission - implementing any of Clusters B through G without explicitly checking against Cluster H's enumerated contracts risks a silent regression, for example accidentally altering the certified `entry_basis` pre-trade handoff while relocating Equity's Computational Authority into `PnLEngine` (a component that already receives `entry_basis` today for an unrelated purpose, Realized PnL event computation).

Necessity Tests: Removal Test fails to remove Cluster H - without explicit tracking of these contracts, any implementation work in Clusters B through G risks silently violating certified behavior. Compression Test - Cluster H is deliberately kept as an explicit, cross-cutting section rather than distributed invisibly across Clusters B through G, so that each cluster's own Compatibility Prerequisites subsection (Sections 8 through 13) can reference it traceably instead of each cluster silently reinventing which contracts apply. Counterfactual Review - without Cluster H made explicit, the certified P1/P2 contract set would still exist as a fact, but would not be actively checked against during P2-03's resolution, materially increasing regression risk, exactly as the P2-02A SDA found for its own analogous cluster. Conclusion: Cluster H is necessary as an explicit, non-sequential constraint layer, already fully satisfied and requiring no new decision, only continuous verification.

## 15. Open Question Classification

**OQ-001 - PnLEngine's cumulative-PnL accumulation mechanism (internal accumulator versus CanonicalState-reconstructed running total).**
Classification: CONDITIONALLY BLOCKING.
Rationale: blocks the exact implementation shape of FR-002/FR-005/FR-007 (Cluster B, Cluster F), but does not block this document's own dependency conclusions, since the ownership-relocation requirement itself (Computational Authority must move to `PnLEngine`) holds regardless of which accumulation mechanism is eventually chosen. Referenced requirements: FR-002, FR-005, FR-007.

**OQ-002 - Interface shape for PnLEngine publishing event-PnL and cumulative-PnL (single call, two calls, or one structured object).**
Classification: NON-BLOCKING.
Rationale: a pure Specification-stage interface-shape question; does not affect the dependency structure derived in this document, since FR-002/FR-003/FR-004's underlying requirements are satisfied identically regardless of the eventual call shape. Referenced requirements: FR-002, FR-003, FR-004.

**OQ-003 - Equity as a stored canonical quantity versus a deterministic computed projection.**
Classification: CONDITIONALLY BLOCKING.
Rationale: mirrors the P2-02A SDA's own OQ-006 (Exposure storage-versus-projection) pattern, itself classified CONDITIONALLY BLOCKING there; affects the exact shape of FR-005/FR-007's implementation, but FR-006's Authoritative Owner assignment (`CanonicalState`) holds under either option. Referenced requirements: FR-005, FR-006, FR-007.

**OQ-004 - Exact Computational Authority mechanism for Equity (PnLEngine.update() returning it directly versus a dedicated compute_equity() method).**
Classification: CONDITIONALLY BLOCKING.
Rationale: a Specification-stage interface question; blocks FR-005's implementation detail only, not the ownership-relocation requirement itself, which this document's dependency conclusions do not require to be pre-resolved. Referenced requirements: FR-005.

**OQ-005 - Exact Computational Authority mechanism for Peak Equity (byproduct of Equity computation versus separate comparison).**
Classification: CONDITIONALLY BLOCKING.
Rationale: identical in kind to OQ-004, for FR-008 instead of FR-005. Referenced requirements: FR-008.

**OQ-006 - Whether RiskEngine.self.peak_equity is removed entirely or retained as a transient, per-call-scoped local variable.**
Classification: CONDITIONALLY BLOCKING.
Rationale: blocks the exact implementation detail of FR-009/FR-010's joint resolution (Section 17, DEP-008) and directly informs FR-018's reset-scope determination (Section 17, DEP-012), but does not block the underlying requirement that `RiskEngine` retain no cross-tick-persisted ownership of Equity or Peak Equity, which holds under either disposition. Referenced requirements: FR-009, FR-010, FR-018.

**OQ-007 - Whether TD-006's full closure (including any RiskEngine risk-formula implications) belongs entirely to P2-03 or is partially P2-04's.**
Classification: CONDITIONALLY BLOCKING.
Rationale: does not block this document's own dependency records, which adopt the FRA's own position (the Equity/Peak-Equity/Drawdown-input-source half is P2-03's, per the Baseline objective's explicit text); it does conditionally block the exact scope boundary the future Capability Gap Analysis must confirm or adjust before Cluster B/D's requirements can be certified closed. Referenced requirements: FR-008, FR-009, FR-010; Technical Debt: TD-006.

**OQ-008 - Whether Financial Events (ADR-002) are a required P2-03 deliverable.**
Classification: NON-BLOCKING.
Rationale: none of the twenty FRA functional requirements' Validation Conditions requires a Financial Event object to exist (confirmed by direct re-check of FRA Sections 18 through 23); the FRA's own Required Capabilities (RC-1 through RC-6, FRA Section 14) do not name Financial Events. If a future document determines they are required, this would introduce new requirements outside this SDA's current twenty-requirement scope, which this document does not anticipate or pre-empt. Referenced requirements: none (observation-only, FRA Section 11).

**OQ-009 - Exact Reset semantics for Realized PnL (cumulative) specifically (unconditional zero versus fresh-Initial-Capital-baseline interaction).**
Classification: CONDITIONALLY BLOCKING.
Rationale: blocks FR-018's exact implementation detail; the underlying dependency (FR-018 requires FR-009's disposition to be known, Section 17 DEP-012) holds regardless of how this specific sub-question is answered. Referenced requirements: FR-017, FR-018.

**OQ-010 - Naming clarity of RiskEngine.check()'s generic state parameter.**
Classification: NON-BLOCKING.
Rationale: purely cosmetic; confirmed by the FRA itself as non-functional. Referenced requirements: none.

**OQ-011 - Whether Drawdown Ratio receives its own future requirement ID distinct from FR-012's framing.**
Classification: NON-BLOCKING.
Rationale: a Specification-stage cataloging question; does not affect the dependency structure, since FR-012 already fully carries the underlying open-ownership question this document analyzes (Section 7, Cluster A). Referenced requirements: FR-012.

**OQ-012 - Whether PositionSizingEngine's confirmed-inactive equity/exposure reads require a forward-compatibility note.**
Classification: DEFERRED.
Rationale: conditional entirely on a future Architecture decision not currently anticipated by any requirement in this document (no FR renames `CanonicalState`'s `"equity"` key); consistent with the FRA's own "preliminary answer: no... currently required" framing and the P2-02A SDA's precedent of classifying comparably dormant, trigger-dependent questions as deferred rather than actively blocking or non-blocking. Referenced requirements: none directly (contextual, FRA Section 28).

No Open Question blocks the scientific progression from Scientific Dependency Analysis to Capability Gap Analysis. Several Open Questions remain conditionally blocking for subsequent Architecture decisions. This is the direct consequence of Section 4's structural observation: P2-03's governing ADRs already supply complete scientific definitions for every in-scope quantity, so no Open Question plays the role P2-02A's OQ-001 played for that unit.

## 16. Technical-Debt Dependency Classification

**Directly and immediately affected by this dependency structure:**

- TD-006 (RiskEngine Peak Equity and Drawdown Ownership Duplication) - central to Cluster B (FR-008, FR-009) and Cluster D (FR-010); its closure is the direct target of DEP-006, DEP-007, DEP-008, DEP-009, DEP-017. Confirmed still OPEN, fully untouched, at HEAD `815cd8a` (FRA Section 27, P2-02A Final Certification Section 21).

**Referenced only for compatibility preservation, not implicated by this dependency structure's own targets:**

- TD-001 (Canonical Position Source for PnLEngine) - Resolved (P2-02A); referenced only by Cluster H's FR-019 as a contract to preserve, not reopened.
- TD-003 (Document Pre-Trade Snapshot Dependency) - Partially Resolved (P2-02A); referenced only by Cluster H's FR-019, not reopened.

**Confirmed follow-on work only, outside this dependency structure entirely:**

- TD-002 (Unify `_safe_float` implementations) - `PnLEngine` has no `_safe_float` method of its own (FRA Section 27); no dependency record in this document touches it.
- TD-004 (Lifecycle-based Performance Evaluation) - unrelated to any Cluster B through H dependency; `PerformanceEngine`'s statistics model is unaffected by this document's requirements.
- TD-005 (Automated Regression Test Suite) - project-wide, explicitly out of scope (FRA Section 24); no dependency record references it as a prerequisite or target.
- TD-007 (RunLoop Lifecycle Control Surface) - unrelated to Financial Ownership; not referenced by any cluster in this document.

## 17. Dependency Graph

Directed dependencies among functional requirements and clusters, each with a stable ID. Cluster H (FR-019) is recorded separately (DEP-016) as a cross-cutting constraint applied identically to all other clusters, and Cluster A's already-conformant "fixed reference frame" members (FR-001, FR-006, FR-011, FR-014) are recorded together as DEP-018, both excluded from the cycle check in Section 17.1 for that reason, exactly as the P2-02A SDA excluded its own Cluster I.

**P2-03-DEP-001**
Source: FR-006 (Cluster C, already-conformant Equity storage). Target: FR-005 (Cluster B).
Type: OWNERSHIP. Relationship: CONSTRAINT (not sequential).
Rationale: FR-005's relocation of Equity's Computational Authority must preserve FR-006's already-correct Authoritative Owner assignment; FR-005 does not wait for FR-006, since FR-006 is already true.
Referenced FRA Requirements: FR-005, FR-006.
Blocking Effect: NON-BLOCKING as sequencing; HARD as a correctness constraint on FR-005's eventual implementation.
Evidence: FRA Section 8 ("Consumers of Equity"), Section 19 (FR-006's Existing Evidence).
Related ADR: ADR-006. Related Technical Debt: none.

**P2-03-DEP-002**
Source: FR-011 (Cluster C, already-conformant Drawdown storage). Target: FR-010 (Cluster D).
Type: OWNERSHIP. Relationship: CONSTRAINT.
Rationale: identical in kind to DEP-001, for Drawdown instead of Equity.
Referenced FRA Requirements: FR-010, FR-011.
Blocking Effect: NON-BLOCKING as sequencing; HARD as a correctness constraint.
Evidence: FRA Section 10, Section 21 (FR-011's Existing Evidence).
Related ADR: ADR-006. Related Technical Debt: TD-006.

**P2-03-DEP-003**
Source: FR-002 (Cluster B). Target: FR-003 (Cluster C, value-correctness half only).
Type: STATE. Strength: HARD for value-correctness; the key/shape-existence half of FR-003 is UNGATED and may proceed independently, mirroring the P2-02A Architecture's D1/D2 shape-versus-ownership split for Position.
Rationale: a canonical storage location cannot hold a genuinely correct cumulative-PnL value before `PnLEngine` computes one; it can hold a placeholder default key at any time.
Referenced FRA Requirements: FR-002, FR-003.
Blocking Effect: CONDITIONALLY BLOCKING (blocks only FR-003's value-correctness verification, not its key-existence half).
Evidence: FRA Section 6 item 7, Section 15 (FR-003's Existing Evidence).
Related ADR: ADR-005, ADR-006. Related Technical Debt: none.

**P2-03-DEP-004**
Source: FR-002, FR-003 (Cluster B, Cluster C). Target: FR-004 (Cluster A).
Type: SEMANTIC. Strength: HARD.
Rationale: event-versus-cumulative distinguishability cannot be verified before both quantities exist and are separately, canonically stored.
Referenced FRA Requirements: FR-002, FR-003, FR-004.
Blocking Effect: BLOCKING for FR-004's own verification.
Evidence: FRA Section 15 (FR-004's Scientific Rationale, citing "Section 13, Gap 2").
Related ADR: ADR-005, ADR-006. Related Technical Debt: none.

**P2-03-DEP-005**
Source: FR-002 (Cluster B). Target: FR-007 (Cluster F).
Type: STATE. Strength: HARD.
Rationale: Equity's formula-consistency claim (`Equity == Initial Capital + Realized PnL cumulative + Unrealized PnL`) cannot be independently verified against a "Realized PnL cumulative" term that does not yet exist as its own value.
Referenced FRA Requirements: FR-002, FR-007.
Blocking Effect: BLOCKING for FR-007's Validation Condition.
Evidence: FRA Section 16 (FR-007's Architectural Rationale, "Realized PnL (cumulative) is correctly tracked (FR-002)").
Related ADR: ADR-006. Related Technical Debt: none.

**P2-03-DEP-006**
Source: FR-008 (Cluster B). Target: FR-009 (Cluster B).
Type: OWNERSHIP. Strength: HARD.
Rationale: safely removing `RiskEngine`'s internally-tracked Peak Equity presupposes a confirmed, correctly-functioning replacement Computational Authority (`PnLEngine`) already exists.
Referenced FRA Requirements: FR-008, FR-009.
Blocking Effect: BLOCKING for FR-009.
Evidence: FRA Section 20 (FR-008, FR-009 sequential placement within Peak-Equity Requirements).
Related ADR: ADR-006, ADR-007. Related Technical Debt: TD-006.

**P2-03-DEP-007**
Source: FR-008 (Cluster B). Target: FR-010 (Cluster D).
Type: INFORMATION_FLOW. Strength: CONDITIONAL.
Rationale: `CanonicalState`'s own Peak Equity tracking is already numerically correct today (FRA Section 9, Computation 1), so FR-010's input-source redirection does not strictly require FR-008's Computational Authority relocation to land first; architectural cleanliness favors sequencing them together, but no hard functional dependency exists, directly analogous to the P2-02A SDA's own DEP-009.
Referenced FRA Requirements: FR-008, FR-010.
Blocking Effect: CONDITIONALLY BLOCKING.
Evidence: FRA Section 9 ("both trackers observe an identical Equity sequence... no numeric divergence has been observed").
Related ADR: ADR-006. Related Technical Debt: TD-006.

**P2-03-DEP-008**
Source: FR-009 (Cluster B). Target: FR-010 (Cluster D). [Mutual/joint pairing]
Type: OWNERSHIP. Strength: HARD, bidirectional.
Rationale: removing `RiskEngine`'s internal Peak Equity tracker without simultaneously redirecting Drawdown's input source leaves Drawdown uncomputable; redirecting Drawdown's input source without removing the internal tracker leaves a dormant, re-divergence-capable duplicate. The two requirements must be resolved together.
Referenced FRA Requirements: FR-009, FR-010.
Blocking Effect: BLOCKING, mutually, for both.
Evidence: FRA Section 16, Gap 3; Section 20-21 (FR-009, FR-010 both target TD-006).
Related ADR: ADR-006, ADR-007. Related Technical Debt: TD-006.

**P2-03-DEP-009**
Source: FR-009, FR-010 (Cluster B, Cluster D). Target: FR-013 (Cluster E).
Type: OWNERSHIP. Strength: HARD.
Rationale: "strictly read-only consumer" cannot be verified as true while `RiskEngine` still independently tracks the same value it reads, the exact condition FR-009/FR-010 jointly resolve.
Referenced FRA Requirements: FR-009, FR-010, FR-013.
Blocking Effect: BLOCKING for FR-013's verification.
Evidence: FRA Section 22 (FR-013's Existing Evidence, "the Peak-Equity ownership violation, FR-009, undermines the boundary in substance").
Related ADR: ADR-007. Related Technical Debt: TD-006.

**P2-03-DEP-010**
Source: FR-002 (Cluster B). Target: FR-015 (Cluster F).
Type: COMPATIBILITY. Strength: HARD.
Rationale: RuntimeFailureEvent non-mutation cannot be re-verified for a Realized-PnL-cumulative field that does not yet exist.
Referenced FRA Requirements: FR-002, FR-015.
Blocking Effect: BLOCKING for FR-015's full scope (the Realized-PnL-cumulative portion specifically; the already-certified Realized-PnL-event portion needs no re-verification).
Evidence: FRA Section 23 (FR-015's Architectural Rationale).
Related ADR: ADR-011. Related Technical Debt: none.

**P2-03-DEP-011**
Source: FR-005, FR-008 (Cluster B). Target: FR-015 (Cluster F).
Type: COMPATIBILITY. Strength: HARD.
Rationale: identical in kind to DEP-010, for the relocated Equity/Peak-Equity computation instead of the newly-created cumulative-PnL field.
Referenced FRA Requirements: FR-005, FR-008, FR-015.
Blocking Effect: BLOCKING for FR-015's Equity/Peak-Equity portion.
Evidence: FRA Section 23 (FR-015's Architectural Rationale, "for Equity/Peak Equity once their Computational Authority moves into PnLEngine").
Related ADR: ADR-011. Related Technical Debt: none.

**P2-03-DEP-012**
Source: FR-009 (Cluster B). Target: FR-018 (Cluster F).
Type: STATE. Strength: CONDITIONAL.
Rationale: the complete inventory of components holding financial-adjacent instance state (and therefore the complete reset scope) depends on whether `RiskEngine` retains any local state at all after FR-009's resolution (OQ-006).
Referenced FRA Requirements: FR-009, FR-018.
Blocking Effect: CONDITIONALLY BLOCKING.
Evidence: FRA Section 25 (FR-018's Architectural Rationale).
Related ADR: AI-010. Related Technical Debt: none.

**P2-03-DEP-013**
Source: FR-020 (Cluster A). Target: FR-007 (Cluster F).
Type: SCIENTIFIC/SCOPE. Strength: CONDITIONAL.
Rationale: FR-007's formula-consistency Validation Condition names Unrealized PnL as a term; if a future document brings Unrealized PnL into scope, FR-007's exact validation changes from "Unrealized PnL held at 0.0" to a full three-term reconstruction; if it remains out of scope, FR-007 is fully satisfiable by Cluster B alone.
Referenced FRA Requirements: FR-007, FR-020.
Blocking Effect: CONDITIONALLY BLOCKING, contingent entirely on FR-020's future disposition.
Evidence: FRA Section 16, Section 26 (FR-007's explicit caveat "with the explicit caveat that Unrealized PnL remains 0.0/absent unless a future document brings it into scope").
Related ADR: ADR-006. Related Technical Debt: none.

**P2-03-DEP-014**
Source: FR-008, FR-009 (Cluster B). Target: FR-017 (Cluster C).
Type: STATE. Strength: SOFT.
Rationale: FR-017's single-source Initial Capital requirement can be resolved independently of Cluster B, but FR-008/FR-009's disposition may reduce or eliminate the specific duplication (RiskEngine's own hardcoded `100.0`) FR-017 currently targets.
Referenced FRA Requirements: FR-008, FR-009, FR-017.
Blocking Effect: NON-BLOCKING; informational only.
Evidence: FRA Section 25 (FR-017's Validation Condition, "or the need for a second copy is eliminated by FR-008/FR-009's Peak-Equity consolidation").
Related ADR: ADR-006. Related Technical Debt: none.

**P2-03-DEP-015**
Source: Clusters B, C, D, E, F (collectively). Target: FR-016 (Cluster G).
Type: VALIDATION. Strength: HARD.
Rationale: a meaningful determinism claim about the fully-relocated system requires that system to have reached a stable, internally-consistent state first.
Referenced FRA Requirements: FR-016 (all of FR-002 through FR-018 as prerequisite state).
Blocking Effect: BLOCKING for FR-016's own final validation, not for any individual prerequisite cluster's internal resolution.
Evidence: FRA Section 21 (FR-016's Existing Evidence, citing the pre-P2-03 certified baseline as the comparison point).
Related ADR: ADR-005, ADR-006, AI-005. Related Technical Debt: none.

**P2-03-DEP-016**
Source: Cluster H (FR-019). Target: Clusters A through G (all).
Type: COMPATIBILITY. Strength: HARD as a constraint; NON-BLOCKING as a sequencing gate.
Rationale: every cluster's resolution must preserve the enumerated P1-03/P1-03.1/P1-04/P2-01/P2-02/P2-02A contracts; this is a constraint applied at every node, not a sequencing gate, exactly as the P2-02A SDA's own DEP-011 treated its Cluster I.
Referenced FRA Requirements: FR-019.
Blocking Effect: BLOCKING as a constraint (violation invalidates the cluster's resolution); NON-BLOCKING as a scheduling delay.
Evidence: FRA Section 26 (FR-019's Existing Evidence, citing P1-03.1/P1-04/P2-02A certifications).
Related ADR: ADR-004, ADR-009, ADR-011. Related Technical Debt: TD-001, TD-003.

**P2-03-DEP-017**
Source: TD-006 (external, already-logged). Target: FR-008, FR-009 (Cluster B), FR-010 (Cluster D).
Type: GOVERNANCE. Strength: HARD.
Rationale: TD-006's own recorded description ("RiskEngine independently maintains peak equity and computes drawdown instead of consuming the CanonicalState-owned values") names exactly the defect Cluster B's FR-008/FR-009 and Cluster D's FR-010 close; this SDA's dependency records for these three requirements directly operationalize TD-006's existing, already-approved disposition rather than introducing a new one.
Referenced FRA Requirements: FR-008, FR-009, FR-010.
Blocking Effect: NON-BLOCKING to this document's own conclusions (TD-006 already assigns this territory to P2-03); constrains scope only.
Evidence: `ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md`, TD-006; FRA Section 27.
Related ADR: ADR-006, ADR-007. Related Technical Debt: TD-006.

**P2-03-DEP-018**
Source: Cluster A's fixed reference frame (FR-001, FR-006, FR-011, FR-014, all already-conformant). Target: Clusters B through G (all).
Type: OWNERSHIP/COMPATIBILITY. Strength: HARD as a constraint; NON-BLOCKING as a sequencing gate.
Rationale: every relocation or correction performed by Clusters B through G must preserve these four already-correct assignments exactly as they stand today; none of the four requires any other cluster to be resolved first, since each is already true.
Referenced FRA Requirements: FR-001, FR-006, FR-011, FR-014.
Blocking Effect: BLOCKING as a constraint (regression of any of the four invalidates the responsible cluster's resolution); NON-BLOCKING as a scheduling delay.
Evidence: FRA Sections 15, 19, 21, 22 (each requirement's own "already satisfied" / "already conformant" framing).
Related ADR: ADR-005, ADR-006, ADR-008. Related Technical Debt: none.

### 17.1 Cycle Check

Topological trace of all sequential (PREREQUISITE-type, non-CONSTRAINT) edges: B(FR-002) to C(FR-003) to A(FR-004); B(FR-002) to F(FR-007); B(FR-008) to B(FR-009); B(FR-008) to D(FR-010, conditional); B(FR-009) to D(FR-010, joint) to E(FR-013); B(FR-002) to F(FR-015); B(FR-005),B(FR-008) to F(FR-015); B(FR-009) to F(FR-018); A(FR-020) to F(FR-007, conditional); B(FR-008),B(FR-009) to C(FR-017, soft); B,C,D,E,F to G(FR-016). No edge points from a later-reached node back to an earlier one in the sequential sense (G never points to any other cluster; F never points to B; E never points to B or D; D's only outbound edge is the conditional D-to-nothing-further; C's only outbound sequential edge is C(FR-003)-to-A(FR-004), and A itself has no further sequential outbound edge). No dependency cycle exists among the sequential edges. CONSTRAINT-type edges (DEP-001, DEP-002, DEP-016, DEP-018) are excluded from this check by construction, since they represent bounds on an implementation rather than participation in the ordering, exactly as the P2-02A SDA excluded its own Cluster I.

## 18. Dependency Matrix

Rows are source clusters, columns are target clusters. Cell values give the dependency ID and strength, or a dash where no dependency was found to survive its Removal Test. Cluster H applies identically to every column (DEP-016) and Cluster A's fixed reference frame applies identically to every column (DEP-018); both are given summary rows rather than repeated per cell.

| Source \ Target | A | B | C | D | E | F | G |
|---|---|---|---|---|---|---|---|
| A | - | - | - | - | - | DEP-013 (CONDITIONAL) | - |
| B | DEP-004 (HARD, joint with C) | DEP-006 (HARD, internal) | DEP-003 (HARD/UNGATED split) | DEP-007 (CONDITIONAL), DEP-008 (HARD, joint with D) | DEP-009 (HARD, joint with D) | DEP-005, DEP-010, DEP-011 (all HARD) | - |
| C | DEP-004 (HARD, joint with B) | - | - | - | - | - | - |
| D | - | - | - | - | DEP-009 (HARD, joint with B) | - | - |
| E | - | - | - | - | - | - | - |
| F | - | - | - | - | - | - | (feeds G via DEP-015) |
| G | - | - | - | - | - | - | - |
| H | DEP-016 | DEP-016 | DEP-016 | DEP-016 | DEP-016 | DEP-016 | DEP-016 |
| A (ref. frame) | DEP-018 | DEP-018 | DEP-018 | DEP-018 | DEP-018 | DEP-018 | DEP-018 |

External-facing dependencies not represented in this square matrix: DEP-017 (TD-006, external, to Cluster B and Cluster D); DEP-014 (Cluster B to Cluster C's FR-017, SOFT, informational only, omitted from the matrix's HARD/CONDITIONAL cells for that reason).

## 19. Minimal Prerequisite Capability Analysis

The hypothesis under test: relocating Computational Authority into `PnLEngine` (Cluster B) is the minimal prerequisite without which neither Canonical Publication's value-correctness half, Drawdown Correctness, Consumer Boundaries, nor Financial Consistency can be correctly closed.

**Removal Test applied to the hypothesis.** If Cluster B remains unresolved: Cluster C's value-correctness half for the new cumulative-PnL key cannot proceed (DEP-003, HARD) - confirmed. Cluster A's FR-004 (distinguishability) cannot be verified (DEP-004, HARD) - confirmed. Cluster F's FR-007 and FR-015 cannot be verified (DEP-005, DEP-010, DEP-011, all HARD) - confirmed. Cluster D's FR-010 is only conditionally affected (DEP-007), and Cluster D's own FR-009 pairing (DEP-008) is a Cluster-B-internal requirement, not an external gate on Cluster D as a whole - partially confirmed, weaker than a hard block. Cluster E's FR-013 cannot be verified (DEP-009, via the FR-009/FR-010 pairing) - confirmed, though mediated through Cluster D rather than directly. However: Cluster C's key-existence half (FR-003's shape-only portion) proceeds unaffected - hypothesis does not hold here. Cluster C's already-conformant lock-ins (FR-006, FR-011) proceed unaffected, being already satisfied - hypothesis does not hold here. Cluster E's FR-014 proceeds entirely unaffected, since it was never gated by Cluster B in the first place - hypothesis does not hold here. Cluster A's FR-012 and FR-020 proceed unaffected, being independent open questions - hypothesis does not hold here.

**Compression Test.** A more precisely scoped, still-accurate restatement of the hypothesis is available: Cluster B is the minimal prerequisite for the value-correctness and consistency-verification portions of Clusters A, C, D, E, and F (Cluster A's FR-004, Cluster C's FR-003 value-half, Cluster D's FR-009/FR-010 pairing indirectly, Cluster E's FR-013 indirectly, Cluster F's FR-007/FR-015), but is not a prerequisite for the already-conformant, ungated, or purely-open portions of the same clusters (Cluster C's FR-006/FR-011/FR-003-shape-half, Cluster E's FR-014, Cluster A's FR-012/FR-020, Cluster F's FR-018 only conditionally through FR-009 rather than directly through Cluster B).

**Counterfactual Review.** What happens if Cluster B is never resolved: the majority of this unit's Baseline objective ("Implement PnLEngine ownership") remains unmet, and TD-006 remains open indefinitely, since Cluster D's own resolution is only conditionally, not fully, independent of Cluster B (DEP-007's conditional nature notwithstanding, DEP-008's hard FR-009/FR-010 pairing still requires Cluster B's FR-009 half). Can the problem be solved equally simply without this capability: no - there is no substitute for actually relocating the Computational Authority ADR-005/ADR-006 name explicitly; this is a genuine, non-bypassable requirement, not a preference. Does resolving Cluster B create a new necessary capability, or only a different representation: it is the direct, textual fulfillment of an already-approved ADR requirement, not a new capability being invented. Can the overall P2-03 requirement set be met without Cluster B: no, not in full - the Baseline's own objective text names it directly - but Cluster A's open questions (FR-012, FR-020) and Cluster C's already-satisfied lock-ins (FR-006, FR-011) can be fully confirmed without it.

**Alternative minimal-prerequisite candidates considered and rejected as the primary answer:**
- Cluster A (Financial State Definition): already satisfied prior to this analysis for every quantity except FR-012/FR-020, neither of which gates anything else; necessary as a reference frame but not what remains missing.
- Cluster D's FR-010 in isolation: gates only Cluster E's FR-013 (via DEP-009, jointly with FR-009) and is itself only conditionally, not hard-fully, dependent on Cluster B (DEP-007); narrower in scope than the hypothesis claims for Cluster B.
- Cluster H (Compatibility): a constant, non-sequential constraint on every cluster, but supplies no new capability itself and cannot serve as a "prerequisite" in the sequential sense this analysis tests.

**Conclusion.** The hypothesis is confirmed as the dominant, though not sole, minimal prerequisite: Cluster B (Financial Ownership) directly or indirectly hard-gates the value-correctness and consistency-verification portions of five of the remaining six clusters (A, C, D, E, F), leaving only Cluster G (Replay/Determinism, itself gated by all of B through F collectively) and the already-satisfied or purely-open portions of A/C/E ungated by Cluster B specifically. Unlike P2-02A, this dependency structure does not decompose into two independent tracks; it is dominated by a single central relocation cluster (B) from which nearly every other cluster's still-open work is directly or transitively reachable, converging at Cluster G's final validation and constrained throughout by Cluster H.

## 20. Alternative Dependency Structures

**Alternative structure 1: single linear chain (A - B - C - D - E - F - G), with H applied only at the end.** Rejected. This structure is not supported by the evidence: Cluster C's already-conformant lock-ins (FR-006, FR-011) and shape-only FR-003 portion, and Cluster E's FR-014, are demonstrably unblocked by Cluster B (Section 19), and forcing a linear order would delay their reconfirmation behind Cluster B's resolution without scientific justification.

**Alternative structure 2: fully parallel, no ordering constraints.** Rejected. This structure is contradicted by the multiple confirmed HARD dependencies (DEP-004, DEP-005, DEP-006, DEP-008, DEP-009, DEP-010, DEP-011, DEP-015), each independently justified by a concrete Failure if Introduced Too Early scenario (Sections 7 through 13). Some ordering is scientifically required, not merely a matter of implementation convenience.

**Alternative structure 3 (adopted): single dominant relocation cluster (B) with radiating hard dependencies into A, C, D, E, F, converging at G, constrained throughout by H.** Supported directly by the Dependency Graph (Section 17) and the Minimal Prerequisite Analysis (Section 19): Cluster B is not one node among several equally-weighted tracks (contrast P2-02A's two-track structure, gated respectively by OQ-001 and Cluster E's temporal classification), but the single structural center of this unit's entire dependency graph, a direct consequence of Section 4's finding that no semantic-definition question of P2-02A's OQ-001 kind exists in P2-03. This structure is adopted for Section 21's Derived Dependency Stages.

## 21. Derived Dependency Stages

This ordering follows directly from the Dependency Graph (Section 17) and the single-center structure (Section 20, alternative 3). It states which requirements must be resolved or confirmed at each logical stage and why; it does not prescribe implementation order, file order, or code changes.

**Dependency Stage 0 - Foundational (already satisfied, fixed reference frame).**
Confirm: FR-001, FR-006, FR-011, FR-014 remain true and unregressed (Cluster A's already-conformant members, Cluster C's already-conformant lock-ins, Cluster E's already-conformant member); Cluster H (FR-019) remains active as a continuous constraint.
Why first: every other stage's Compatibility Prerequisites cite one or more of these as already-satisfied preconditions (Sections 8, 9, 11).
Unlocks: nothing new; establishes the constraint boundary every later stage must respect.
FRA Requirements involved: FR-001, FR-006, FR-011, FR-014, FR-019.

**Dependency Stage 1 - Core Computational Authority Relocation.**
Resolve: FR-002, FR-005, FR-008 (Cluster B's three primary relocations into `PnLEngine`), each gated only by Stage 0's constraints, not by each other.
Why first (within this stage): none of the three requires the other two to be resolved first (no HARD edge exists among FR-002/FR-005/FR-008 themselves in Section 17); all three are gated only by Cluster A (satisfied) and constrained by Cluster C's lock-ins (DEP-001).
Unlocks: Cluster C's value-correctness half (Stage 2), Cluster A's FR-004 (Stage 2), Cluster F's FR-007/FR-015 (Stage 2/3), Cluster B's own FR-009 (Stage 2).
FRA Requirements involved: FR-002, FR-005, FR-008.

**Dependency Stage 2 - Dependent Storage, Distinguishability, and Formula Consistency.**
Resolve: FR-003 (value-correctness half, DEP-003), FR-004 (DEP-004), FR-007 (DEP-005, conditionally informed by DEP-013).
Why first: each requires at least one Stage 1 requirement to exist before it can be verified, per the HARD edges in Section 17.
Unlocks: Cluster F's FR-015 (Stage 3, alongside Stage 1's outputs directly).
FRA Requirements involved: FR-003, FR-004, FR-007.

**Dependency Stage 3 - Peak-Equity Ownership Removal and Drawdown Input-Source Correction (joint resolution).**
Resolve: FR-009 and FR-010 together (DEP-008's mandatory pairing), gated by Stage 1's FR-008 (DEP-006 hard for FR-009, DEP-007 conditional for FR-010).
Why first: FR-009 cannot be safely resolved without FR-010 landing simultaneously, and vice versa (Section 10, Section 17 DEP-008); this is the direct operational closure of TD-006 (DEP-017).
Unlocks: Cluster E's FR-013 (Stage 4).
FRA Requirements involved: FR-009, FR-010.

**Dependency Stage 4 - Consumer Boundary Verification.**
Confirm: FR-013, verifiable only once Stage 3 has landed (DEP-009).
Why first: "strictly read-only consumer" cannot be distinguished from "read-only consumer of a value also independently tracked" until Stage 3 removes the independent tracking.
Unlocks: nothing further within P2-03 beyond contributing to Stage 6's determinism baseline.
FRA Requirements involved: FR-013.

**Dependency Stage 5 - Failure and Reset Consistency Re-Verification.**
Resolve: FR-015 (fully, combining Stage 1/2's DEP-010/DEP-011 prerequisites), FR-018 (gated by Stage 3's FR-009 disposition, DEP-012).
Why first: both require the specific new or relocated financial values from Stages 1 through 3 to exist under their new ownership before their consistency properties can be meaningfully re-verified rather than assumed.
Unlocks: Stage 6's determinism validation.
FRA Requirements involved: FR-015, FR-018.

**Dependency Stage 6 - Final Determinism and Compatibility Validation.**
Resolve: FR-016 (DEP-015, requiring Stages 1 through 5 collectively); re-apply Cluster H's full constraint set (FR-019) across the entire resolved system.
Why last: only after every prerequisite stage's decisions are finalized can a meaningful determinism claim be evaluated against the fully-relocated system, and only then can the complete set of already-certified P1-03/P1-03.1/P1-04/P2-01/P2-02/P2-02A scenarios be meaningfully re-verified end to end.
FRA Requirements involved: FR-016, FR-019 (re-confirmed).

**Not bound to any specific stage (ungated, may be confirmed or resolved independently at any point):** FR-012 (Drawdown Ratio ownership, Cluster A), FR-017 (Initial Capital single source, Cluster C, softly informed by Stage 3 per DEP-014), FR-020 (Unrealized PnL scope protection, Cluster A, conditionally informing FR-007's exact validation per DEP-013).

## 22. External and Deferred Dependencies

Recorded as external dependency, deferred dependency, or future compatibility constraint only, per the FRA's own scope protection (Section 24 of that document); none of the following is pulled into this document's own scope:

- P2-04 (Risk Ownership Consolidation) - external dependency for Cluster D and the RiskEngine-formula-adjacent portion of OQ-007; Cluster D must coexist with P2-04 unresolved, touching no line of `RiskEngine`'s `max_exposure`/`min_exposure`/regime-dampening logic.
- P3-03 (Performance Validation) - future compatibility constraint: whatever Cluster E's FR-014 confirms must not conflict with P3-03's eventual `PerformanceEngine` input/statistics work, though no such conflict is currently foreseeable given FR-014's narrow, already-satisfied scope.
- Unrealized PnL / Mark-to-Market Portfolio Valuation (FR-020) - deferred dependency, explicitly scope-protected; DEP-013 records its conditional effect on FR-007 without resolving FR-020 itself.
- Financial Events (ADR-002, OQ-008) - deferred dependency, not currently a P2-03 dependency; classified NON-BLOCKING (Section 15), since no FR requires it; recorded here as a future dependency risk only if a later document decides otherwise.
- Repository cleanup (`equity_stabilizer.py`, `position_sizing.py`, `run_engine/runtime/pnl_engine.py`, `run_engine/runtime/risk.py`, `run_engine/runtime/performance_analytics.py`) - deferred to Phase 6 Repository Consolidation; recorded as FRA findings only, not dependencies.
- TD-005 (automated regression test suite) - deferred, project-wide; unrelated to this analysis's dependency structure.
- TD-002, TD-004, TD-007 - confirmed follow-on only (Section 16); no dependency record in this document targets them.

## 23. Risks of Incorrect Ordering

- Resolving FR-009 before FR-010 (violating DEP-008's mandatory pairing): risk of Drawdown becoming uncomputable for at least one intermediate state, a functional regression more severe than TD-006's current duplication.
- Resolving FR-003's value-correctness half before FR-002 (violating DEP-003): risk of publishing a placeholder or incorrectly-derived cumulative-PnL value under a canonical key, creating a false impression of closure while reproducing exactly the kind of premature-computation risk the P2-02A SDA warned against for its own Cluster H.
- Verifying FR-013 "read-only" before FR-009/FR-010 land (violating DEP-009): risk of a false-positive consumer-boundary certification, since the property cannot be distinguished from today's coincidental non-divergence (FRA Section 9).
- Finalizing FR-018's reset scope before FR-009's disposition is known (violating DEP-012): risk of either resetting a field that no longer exists or omitting one that still does, depending on which side of OQ-006 is eventually chosen.
- Validating FR-016 (determinism) before Stages 1 through 5 have landed (violating DEP-015): risk of certifying determinism against an intermediate, partially-relocated system rather than the system this unit is actually meant to certify.
- Treating P2-03 as requiring Cluster A's semantic-definition work to complete before Cluster B can begin (a P2-02A-style two-track assumption that does not apply here): risk of unnecessarily delaying the entire unit behind FR-012/FR-020, when Section 4's structural finding establishes that no such gating exists.
- Expanding Cluster D into `RiskEngine`'s actual risk-limiting formula or regime-dampening logic (violating the DEP-017/external P2-04 scope boundary): risk of silently absorbing P2-04's charter into P2-03, violating Principle IP-002 and the FRA's own explicit scope-protection instruction.

## 24. Scientific Dependency Conclusions

Eighteen internal or external-facing dependencies were identified and assigned stable IDs (P2-03-DEP-001 through P2-03-DEP-018). No dependency cycle exists among the sequential (non-constraint) edges (Section 17.1). Two clusters (A, Financial State Definition, largely already satisfied; H, Compatibility, a constant non-sequential constraint) function as a fixed reference frame rather than as pending sequential work. The remaining six clusters (B through G) do not decompose into two independent tracks the way P2-02A's did; instead, a single dominant cluster (B, Financial Ownership) directly or transitively hard-gates the still-open portions of five of the remaining six clusters (A's FR-004, C's FR-003 value-half, D's FR-009/FR-010 pairing, E's FR-013, F's FR-007/FR-015/FR-018), converging at Cluster G's final determinism validation and constrained throughout by Cluster H. Of the twelve FRA Open Questions, none is classified BLOCKING; seven (OQ-001, OQ-003, OQ-004, OQ-005, OQ-006, OQ-007, OQ-009) are classified CONDITIONALLY BLOCKING with precisely scoped blocking effects limited to implementation-detail or scope-boundary questions; four (OQ-002, OQ-008, OQ-010, OQ-011) are classified NON-BLOCKING; one (OQ-012) is classified DEFERRED. All twenty FRA functional requirements (P2-03-FR-001 through P2-03-FR-020) are referenced by at least one cluster's dependency analysis (Sections 7 through 14) or dependency record (Section 17).

## 25. Readiness for Capability Gap Analysis

This analysis identified no scientific ambiguity that blocks proceeding to a Capability Gap Analysis. Every dependency recorded here traces directly to an FRA requirement, an ADR, an Architecture Invariant, or the already-logged TD-006; no new scientific claim, formula, or ownership assignment is introduced. The absence of any BLOCKING Open Question (Section 15) and the single-center dependency structure (Section 20) mean a Capability Gap Analysis can proceed directly to examining, requirement by requirement, exactly which files and code paths require change once the still-open implementation-detail questions (OQ-001 through OQ-007, OQ-009) are eventually resolved, using the Dependency Stages (Section 21) as its ordering reference and the Dependency Graph (Section 17) as its blocking reference.

Readiness: READY. This document is sufficient to proceed to the P2-03 Capability Gap Analysis. No further scientific dependency investigation is required before that step.

## 26. Internal Consistency Review

Terminology consistency - "Cluster," "Dependency," "Prerequisite," "Constraint," "Blocking," "Conditionally Blocking," "Non-Blocking," and "Deferred" are used consistently throughout this document with the definitions established in Sections 5 and 15. Every financial term used (Realized PnL event/cumulative, Equity, Peak Equity, Drawdown, Drawdown Ratio, Financial State, Financial Event, Performance Metric, Risk Metric) is used exactly as defined in the FRA's own Section 5, never redefined here.

Scope consistency - no dependency recorded in Section 17 introduces a new functional requirement, a new interface, a new formula, or a new final ownership assignment beyond what ADR-005/ADR-006/ADR-007 and the FRA already establish; every dependency describes a relationship between already-existing requirements, not a resolution of one. Section 22 confirms all P2-04/P3-03/Financial-Events/Unrealized-PnL/repository-cleanup/TD-005 topics are recorded only as external, deferred, or future-compatibility dependencies, never as in-scope work.

Dependency-cycle consistency - verified explicitly in Section 17.1; no cycle exists among sequential edges; constraint-type edges are explicitly and consistently excluded from the cycle check.

Traceability consistency - all twenty FRA functional requirements are referenced by at least one section among 7 through 14 or by at least one dependency record in Section 17; this was cross-checked requirement by requirement during drafting (FR-001 in Sections 7, 17 DEP-018; FR-002 in Sections 8, 17 DEP-003/004/005/006/007/010/017; FR-003 in Sections 9, 17 DEP-003/004; FR-004 in Sections 7, 17 DEP-004; FR-005 in Sections 8, 17 DEP-001/011; FR-006 in Sections 9, 17 DEP-001/018; FR-007 in Sections 12, 17 DEP-005/013; FR-008 in Sections 8, 17 DEP-006/007/008/011/014/017; FR-009 in Sections 8, 10, 17 DEP-006/008/009/012/014/017; FR-010 in Sections 10, 17 DEP-002/007/008/009/017; FR-011 in Sections 9, 17 DEP-002/018; FR-012 in Section 7; FR-013 in Sections 11, 17 DEP-009; FR-014 in Sections 11, 17 DEP-018; FR-015 in Sections 12, 17 DEP-010/011; FR-016 in Sections 13, 17 DEP-015; FR-017 in Sections 9, 17 DEP-014; FR-018 in Sections 12, 17 DEP-012; FR-019 in Sections 14, 17 DEP-016; FR-020 in Section 7, 17 DEP-013).

Open-Question coverage - all twelve FRA Open Questions are classified in Section 15, each with an explicit BLOCKING/CONDITIONALLY BLOCKING/NON-BLOCKING/DEFERRED rating and scientific rationale; none is left unclassified.

Technical-Debt coverage - all seven Technical Debt Register items (TD-001 through TD-007) are classified in Section 16 as directly affected, compatibility-referenced only, or follow-on only; none is left unclassified.

Dependency-ID uniqueness - P2-03-DEP-001 through P2-03-DEP-018 are each used exactly once as a definition (Section 17) and referenced only by ID thereafter (Sections 18 through 24); no ID collision or reuse was introduced.

Ordering consistency - Section 21's stages match the Dependency Graph's edges exactly; no requirement is scheduled before a requirement it has a HARD dependency on, per Section 17's Blocking Effect column.

Observation/dependency/decision separation - Sections 4 and 6 contain only repository-grounded and FRA-grounded observations; Sections 7 through 14 contain only dependency analysis derived from those observations plus the FRA and the Architecture Baseline; Section 19's Minimal Prerequisite Analysis explicitly tests rather than assumes its hypothesis; no architecture decision, formula selection, or final ownership mechanism is made anywhere in this document; no implementation order, file order, or code change is proposed anywhere in this document.

Status: Internal Consistency Review PASS.
