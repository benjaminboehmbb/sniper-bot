Document Class:
Scientific Dependency Analysis

Document ID:
P2-04-SDA

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
docs/architecture/analysis/P2_04_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-13.md

Depends On:
- docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md
- docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md
- docs/architecture/analysis/P2_04_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-13.md
- docs/architecture/certification/P2_03_FINAL_CERTIFICATION_V1_2026-07-11.md
- docs/architecture/certification/P2_02A_FINAL_CERTIFICATION_V1_2026-07-10.md
- docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md
- current runtime code at HEAD a81e197

Referenced By:
- future P2-04 Capability Gap Analysis
- future P2-04 Architecture
- future P2-04 Specification
- future P2-04 Certification

---

# P2-04 Scientific Dependency Analysis

## 1. Purpose

This document performs the Scientific Dependency Analysis for P2-04 (Risk Ownership), following directly from `P2_04_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-13.md` (Status: Draft for Internal Review, Functional Readiness: READY, Internal Consistency Review PASS, subsequently reviewed and revised per its own Scientific Consistency Review).

This document does not perform Capability Gap Analysis. It does not make architecture decisions. It does not select an implementation mechanism. It does not specify interfaces, formulas, or storage locations. It does not implement code. Its sole purpose is to determine the scientific, semantic, state-related, and architectural dependency structure among the fifteen functional requirements (P2-04-FR-001 through P2-04-FR-015) already established by the FRA, and to derive the resulting logical ordering of future decisions.

No functional requirement is created, removed, or modified by this document. No Open Question already recorded by the FRA is resolved by this document; each is instead classified by its blocking effect on the dependency structure derived here.

## 2. Scope

In scope: dependency analysis of Risk Policy Configuration ownership, Risk Metric ownership (`risk_allocation_factor`), Position-derived Exposure's disposition inside `RiskEngine`, the risk-limiting formula's evaluation, TD-006's remaining risk-formula-adjacent scope, RiskEngine determinism, consumer-boundary preservation, RuntimeFailureEvent non-mutation, reset semantics, and compatibility preservation, as these relate to the fifteen FRA functional requirements.

Out of scope: everything the FRA itself placed out of scope (Section 24 of that document) - Drawdown and Drawdown Ratio's Computational Authority/Authoritative Owner/formula (fully certified by P2-03), full `PerformanceEngine` redesign or its consumption of Risk Metrics (P3-03), `PositionSizingEngine` activation, Position/Exposure ownership itself (P2-02A, certified), Persistence and Recovery (ADR-012), repository cleanup, and the automated regression test suite (TD-005). No implementation order, file order, interface shape, formula shape, or code change is proposed anywhere in this document.

## 3. Binding Inputs

- `docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md` - ADR-004, ADR-006, ADR-007, ADR-011, the Runtime Ownership Matrix's "Risk Metrics" row, Rules OM-001 through OM-009 (in particular OM-002, OM-006, OM-007), Architecture Invariants AI-001, AI-005, AI-010, AI-013, and the "Derived View" and "Constraint" concepts already established by the P2-03 SDA's own methodology (Section 5 below).
- `docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md` - the P2-04 unit definition and Principle IP-002 (Single Logical Change; repository-wide modifications prohibited).
- `docs/architecture/analysis/P2_04_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-13.md` - the fifteen functional requirements, seven Required Capabilities (RC-1 through RC-7), and seven Open Questions (OQ-001 through OQ-007), all as internally reviewed (Status: Internal Consistency Review PASS) and subsequently corrected per its own Scientific Consistency Review.
- `docs/architecture/certification/P2_03_FINAL_CERTIFICATION_V1_2026-07-11.md` - the certified contract baseline this analysis treats as immutable for Equity, Peak Equity, Realized PnL, Drawdown, and Drawdown Ratio.
- `docs/architecture/certification/P2_02A_FINAL_CERTIFICATION_V1_2026-07-10.md` - the certified contract baseline this analysis treats as immutable for Position and Position-derived Exposure, including `RiskEngine`'s already-certified read-only consumption boundary (P2-02A-AD-008).
- `docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md` - TD-001 through TD-007, in particular TD-006's remaining, explicitly-named risk-formula half.
- Current runtime code at HEAD `a81e197`, relied upon only through the FRA's own repository-grounded findings (Sections 6 through 13 of that document); no new repository claim is introduced by this document beyond re-verification (Section 4 below).

## 4. Verified Functional Baseline

Repository state re-verified for this analysis: branch `run-engine-consolidation-safety`, HEAD `a81e1978cb07bbb26223c94a1b24e9220520c445`, matching the FRA's own verification exactly (`git branch --show-current`, `git rev-parse HEAD`). `run_engine/` remains clean (`git status --short run_engine/` returns no output). `run_engine/core/risk.py`, `run_engine/core/canonical_state.py`, and `run_engine/core/loop.py` were re-read in full and found byte-for-byte unchanged from the versions the FRA analyzed; no runtime file has been modified since the FRA's own certification-style review and revision.

This analysis relies on the FRA's Section 6 through Section 23 findings without re-deriving them from the code a second time. Every dependency record below cites the specific FRA section, requirement ID, or Architecture Baseline ADR/Invariant/Rule that grounds it, rather than re-quoting source code.

One structural observation, not present in the FRA itself but directly derived from it, governs the shape of this entire analysis. Unlike P2-02A (two independent tracks, one gated by a genuinely open semantic-definition question, OQ-001) and P2-03 (a single dominant relocation cluster from which nearly every other cluster's still-open work was directly or transitively reachable), P2-04 presents neither shape. Ten of the fifteen functional requirements (FR-002, FR-004's storage-location half, FR-006, FR-009, FR-010, FR-011, FR-012, FR-014, and the compatibility half of FR-015) are already conformant today and function as a fixed reference frame or cross-cutting constraint layer, not as pending sequential work. The remaining work is concentrated in two small, tightly-coupled, mutually-informing open clusters - Position-derived Exposure's disposition inside `RiskEngine` (FR-005) and the risk-limiting formula's own evaluation (FR-007, FR-008) - surrounded by two narrower, largely-independent naming questions (FR-001, FR-003) and one small, conditionally-gated terminal question (FR-013, Reset). This finding is confirmed in Section 16 (Open Question Classification) below: no Open Question in this cycle is classified BLOCKING, and the two central clusters' mutual coupling is the only genuinely HARD forward dependency this analysis identifies among still-open work.

## 5. Dependency Analysis Method

Each of the nine capability clusters (A through I, mapped onto Sections 7 through 15) is analyzed using the following method, applied compactly per cluster, identical in structure to the method the P2-03 SDA established for this governance chain:

1. Capability Definition
2. Prerequisites, grouped as: Scientific, Semantic, State, Ownership, Information-Flow, Determinism, Compatibility
3. Dependent Capabilities (what this cluster unlocks or constrains)
4. Failure if Introduced Too Early (concrete failure mode from wrong ordering)
5. Necessity Tests: Minimality Assessment, Removal Test, Compression Test, Counterfactual Review, combined into one judgment per cluster

A dependency is recorded in the Dependency Catalogue (Section 18) only when it survives its own Removal Test (removing the source requirement would make the target requirement's correct resolution impossible or unverifiable, not merely inconvenient or stylistically preferable). Two distinct relationship kinds are used throughout, consistent with the FRA's own "lock-in" language (its Sections 16, 19-23 record requirements that are already conformant and must be preserved, not achieved): a PREREQUISITE edge (source must be resolved before target can be correctly resolved or verified; may carry strength HARD, CONDITIONAL, or SOFT) and a CONSTRAINT edge (source is already true and bounds how target may be resolved, without target having to wait for source). CONSTRAINT edges are excluded from the sequencing cycle check (Section 19.1), exactly as the P2-03 SDA excluded its own Cluster H and fixed-reference-frame constraint edges.

## 6. Capability Cluster Catalogue

| Cluster | Name | One-line definition | FRA Requirements |
|---|---|---|---|
| A | Risk Policy Configuration Ownership | Ownership status of the Risk Policy Configuration values (`max_drawdown`, `max_exposure`, `min_exposure`, regime-dampening multipliers) that parameterize RiskEngine's risk-limiting computation, and confirmation of RiskEngine's already-conformant Computational Authority for the resulting Risk Metric | FR-001, FR-002 |
| B | Risk Metric Ownership | Individually-named ADR-level Computational Authority/Authoritative Owner assignment for `risk_allocation_factor`, and preservation of its already-conformant storage location alongside Drawdown/Drawdown Ratio | FR-003, FR-004 |
| C | Position-Derived Exposure Disposition | Whether Position-derived Exposure, already mechanically consumed but functionally unused (`position_exposure`, `risk.py:10`), is incorporated into RiskEngine's risk-limiting computation, bounded by RiskEngine's already-certified read-only boundary | FR-005, FR-006 |
| D | Risk-Limiting Formula Evaluation | Evaluation and explicit retain-or-revise disposition of the drawdown-ratio threshold check and regime-dampening multipliers, and the resulting closure of TD-006's remaining risk-formula half | FR-007, FR-008 |
| E | Determinism | RiskEngine.check()'s purity and statelessness as a function of its three explicit parameters | FR-009, FR-010 |
| F | Consumer Boundary | RiskEngine's strictly read-only consumption of canonical Equity, Peak Equity, and Position | FR-011 |
| G | Failure Handling | RUNTIME_FAILURE_EVENT non-mutation of Drawdown, Drawdown Ratio, and `risk_allocation_factor` | FR-012 |
| H | Reset | Reset semantics for Risk Policy Configuration, conditionally gated by Cluster A | FR-013 |
| I | Compatibility | The frozen set of already-certified P1/P2-0x Risk-adjacent contracts, and explicit scope-protection against incidental resolution of the PerformanceEngine/Risk-Metric consumption boundary question | FR-014, FR-015 |

This clustering follows the FRA's own nine requirement-section groupings (its Sections 15 through 23) directly, since - unlike P2-03, which received externally suggested cluster names from its own governing task - no external cluster-naming instruction exists for P2-04, and the FRA's own section boundaries already correspond to nine thematically distinct, Runtime-Ownership-Matrix-adjacent capabilities, each independently surviving its own Compression Test (Sections 7 through 15 below). Clusters E, F, and G are each kept separate despite all three being "already satisfied, verify only" clusters, because each verifies a scientifically distinct property (RiskEngine's own internal statelessness; RiskEngine's non-mutation of external inputs; RiskEngine's non-mutation across a specific event-conditioned tick type) that a single component could in principle satisfy independently of the other two, a distinction confirmed directly in the FRA's own prior Scientific Consistency Review (Terminology Consistency finding TC-2's discussion of FR-011).

Clusters E, F, G, and the already-conformant halves of Clusters A (FR-002) and B (FR-004's storage-location half) function as a fixed reference frame; Cluster I functions as a cross-cutting, non-sequential constraint layer. Neither functions as pending sequential work, in the same sense the P2-03 SDA treated its own Cluster A and Cluster H.

## 7. Risk Policy Configuration Ownership Dependencies (Cluster A)

Capability Definition: the ADR-level Authoritative Owner and Computational Authority status of `max_drawdown`, `max_exposure`, `min_exposure`, and the three regime-dampening multipliers (FR-001, open), and RiskEngine's already-conformant status as exclusive Computational Authority translating these values into `risk_allocation_factor` (FR-002, satisfied).

Prerequisites: Scientific - ADR-007's general Risk Metric framing exists but does not individually name Risk Policy Configuration (FRA Section 7, Gap 1); no other ADR text bears on this cluster. Semantic - none pending beyond the FRA's own Section 5 definition of "Risk Policy Configuration," which is self-derived from repository observation, not from any ADR requiring further semantic resolution. State - none; the three named values are static `__init__`-time constants and the three regime multipliers are inline literals, none of which is ever mutated by any runtime event (FRA Section 7). Ownership - FR-001 is itself the open question this cluster exists to resolve. Information-Flow - none new; these values never flow anywhere outside `RiskEngine.check()` (FRA Section 7: "Never published... Never read by any other active-path component"). Determinism - trivially satisfied; FR-002 confirms RiskEngine is sole Computational Authority and no alternative computation exists anywhere in the repository (FRA Section 15, Existing Evidence). Compatibility - FR-002's already-conformant status must not be regressed by whatever FR-001 or Cluster D eventually decide (Section 24 below, Cluster I).

Dependent Capabilities: Cluster H's FR-013 (Reset) is explicitly, textually conditional on FR-001's resolution ("Architectural Rationale: conditional on FR-001's eventual resolution," FRA Section 22). Cluster D's FR-007 (formula evaluation) may inform FR-001's exact scope if the evaluation changes which values parameterize the formula, a SOFT, informational relationship only (Section 10 below).

Failure if Introduced Too Early: not applicable to FR-001 itself (nothing gates its own resolution beyond Cluster A's own already-satisfied prerequisites); the relevant risk lies downstream - finalizing Cluster H's reset design before FR-001 is resolved risks designing a reset mechanism for a Risk Policy Configuration ownership model that is not the one eventually adopted.

Necessity Tests: Removal Test fails to remove Cluster A - without it, "Verify Risk Metrics ownership" (P2-04's own Baseline objective text) remains unmet for the parameters governing that computation, regardless of how completely Clusters B through I are resolved. Compression Test - Cluster A cannot be merged into Cluster B (Risk Metric Ownership), since A concerns the input parameters governing a computation while B concerns the output value that computation produces - the same Rule OM-002-style distinction the P2-03 SDA applied between its own Computational-Authority-relocation and input-source-correction clusters, here extended from "who computes" versus "where inputs come from" to "what parameterizes the computation" versus "what the computation produces." Counterfactual Review - if FR-001 were never resolved, Cluster H's reset design would remain indefinitely conditional, and P2-04's own named objective would remain only partially satisfied even after every other cluster closes. Conclusion: Cluster A is necessary; FR-002 is already fully satisfied, and FR-001 is ungated, ready for resolution independent of every other cluster except as a soft input from Cluster D.

## 8. Risk Metric Ownership Dependencies (Cluster B)

Capability Definition: the individually-named ADR-level Computational Authority and Authoritative Owner assignment for `risk_allocation_factor` (FR-003, open), and preservation of its already-conformant storage location inside `CanonicalState` at the general Runtime Ownership Matrix "Risk Metrics"-row level (FR-004, satisfied on the storage-location half, open only on the individual-naming half that FR-003 itself carries).

Prerequisites: Scientific - ADR-007's general Risk Metric category plausibly covers `risk_allocation_factor` but does not name it individually, structurally the same shape of gap Drawdown Ratio had before P2-03-AD-007 resolved it (FRA Section 5, Gap 2). Semantic - none pending; the object itself already exists, is already computed, and is already stored today (FRA Section 9). State - already exists (`CanonicalState.state["risk_allocation_factor"]`, default `1.0`, FRA Section 9). Ownership - FR-004 is an already-conformant CONSTRAINT on FR-003: the storage location (`CanonicalState`) and the mechanical Computational Authority (`RiskEngine`) are both already correct and must not be relocated while FR-003's naming decision is made, mirroring the P2-03 SDA's own DEP-001/DEP-002 pattern of an already-conformant assignment constraining an open-naming decision for the same object. Information-Flow - none new. Determinism - not directly implicated. Compatibility - FR-004's already-conformant status must be preserved as FR-003 resolves.

Dependent Capabilities: none forward within P2-04; Cluster D's FR-007 (formula evaluation) may inform FR-003's naming description if the formula's output shape changes, a SOFT, informational relationship only (Section 10 below), not a prerequisite for FR-003's own resolution, since the ownership CATEGORY (RiskEngine/CanonicalState) is already stable independent of formula shape.

Failure if Introduced Too Early: naming `risk_allocation_factor`'s ownership (FR-003) before Cluster D's formula evaluation (FR-007) completes risks the naming decision's descriptive text referring to a formula that is about to change, requiring a second naming pass for editorial consistency - an efficiency risk, not a correctness-blocking one, since the ownership category itself does not depend on the formula's exact shape.

Necessity Tests: Removal Test fails to remove Cluster B - without it, `risk_allocation_factor` remains the sole Risk Metric without individual ADR-level naming, an asymmetry against Drawdown and Drawdown Ratio's now-complete naming (P2-03-AD-006, P2-03-AD-007), regardless of how completely every other cluster resolves. Compression Test - FR-003 (the open naming decision) cannot be merged with FR-004 (the already-settled storage-location preservation) despite both concerning the same object, since one is an open decision and the other is an already-true constraint bounding it - the identical Rule OM-002-style distinction applied throughout this document. Counterfactual Review - if FR-003 is never resolved, `risk_allocation_factor` remains "Partially Defined" (FRA Section 11) indefinitely, an asymmetry with every other named Risk Metric in this unit's scope. Conclusion: Cluster B is necessary; FR-004's storage-location half is already satisfied and constrains FR-003; FR-003 is ungated for its own resolution, softly informed only by Cluster D.

## 9. Position-Derived Exposure Disposition Dependencies (Cluster C)

Capability Definition: the explicit architectural disposition of `position_exposure` (`risk.py:10`, read every tick, never referenced again) - either permanent, documented read-only non-use (FR-005 option a) or functional incorporation into the risk-limiting computation (FR-005 option b) - bounded throughout by RiskEngine's already-certified strict read-only consumption of Position-derived Exposure (FR-006).

Prerequisites: Scientific - ADR-004 requires RiskEngine to "consume Position-derived Exposure," already mechanically satisfied by the existing read (FRA Section 6, Section 10); the genuinely open question is functional use, not consumption itself. Semantic - none pending; Position-derived Exposure is already fully and completely defined by P2-02A (FRA Section 5), not reopened here. State - `position_exposure` is already available as a read, every tick, at `risk.py:10`; no new state is required to begin resolving FR-005. Ownership - FR-006 is a CONSTRAINT on FR-005: whatever FR-005 eventually decides, RiskEngine must never acquire ownership of Position or Exposure in any form, the already-certified P2-02A boundary (P2-02A-AD-008), mirroring the P2-03 SDA's DEP-001/DEP-002 constraint pattern once more. Information-Flow - if FR-005 resolves toward functional incorporation (option b), Cluster D's risk-limiting formula (FR-007) gains a new information-flow path from `position_exposure` into `risk_allocation_factor`'s computation, a direct downstream consequence recorded as a PREREQUISITE edge (Section 10, Section 18). Determinism - any functional incorporation of `position_exposure` must preserve Cluster E's purity requirement (FR-009): the resulting formula must remain a deterministic function of `state`/`position`/`regime` only, introducing no new non-deterministic dependency; this is recorded as a CONSTRAINT running from Cluster E into Cluster C (Section 11, Section 18). Compatibility - FR-006's already-certified read-only boundary is a hard bound on FR-005's eventual implementation, not merely a stylistic preference.

Dependent Capabilities: Cluster D's FR-007 (risk-limiting formula evaluation) is CONDITIONALLY dependent on FR-005 for its position-exposure-input dimension specifically; the formula's other dimension (whether the existing drawdown-ratio threshold and regime multipliers themselves are retained or revised) is independent of FR-005 and may proceed on its own timeline.

Failure if Introduced Too Early: finalizing Cluster D's formula shape (FR-007) before FR-005 is resolved risks either omitting `position_exposure` from the formula when the eventual Architecture decision required its inclusion, or requiring a second, avoidable revision once FR-005 is separately decided later - a rework risk this document records as CONDITIONAL rather than HARD, since FR-007's threshold/multiplier dimension does not itself require FR-005 to be resolved first.

Necessity Tests: Removal Test fails to remove Cluster C - without its resolution, ADR-004's "consume Position-derived Exposure" requirement remains satisfied only in the minimal mechanical sense P2-02A-AD-008 established, which that same document's own text explicitly frames as insufficient for full scientific closure ("no functional use of it is required in this unit... deferred to a future architectural unit"). Compression Test - FR-005 (the open disposition decision) and FR-006 (the already-certified read-only boundary preserving it) cannot be merged, the same WHAT-versus-HOW-bounded distinction used throughout this document. Counterfactual Review - if FR-005 is never resolved, `position_exposure` remains permanently read-but-unused with no scientific closure on whether that is the intended end state, Gap 3 remaining open indefinitely. Conclusion: Cluster C is one of this unit's two central, currently-unresolved clusters; FR-006 is already satisfied and constrains FR-005; FR-005 is ungated for its own resolution but conditionally feeds Cluster D and is constrained by Clusters E, F, G, and I.

## 10. Risk-Limiting Formula Evaluation Dependencies (Cluster D)

Capability Definition: evaluation and explicit retain-or-revise disposition of the drawdown-ratio threshold check (`risk.py:33-34`) and the regime-dampening multipliers (`risk.py:37-44`) (FR-007), and the resulting explicit closure or justified re-deferral of TD-006's remaining risk-formula half (FR-008), per P2-03-AD-015's explicit naming of this unit as the closure venue.

Prerequisites: Scientific - AI-005 and AI-010 require any retained or revised formula to remain deterministic and internally consistent (FR-007's own Scientific Rationale); this bounds the evaluation's outcome, it does not block the evaluation from beginning. Semantic - none pending; the formula's current shape is already fully and completely documented (FRA Section 8). State - none new required to begin; FR-007 requires no state beyond what Cluster A, B, and C already establish or leave open. Ownership - none new; RiskEngine's Computational Authority for the formula's output is already settled (FR-002, Cluster A), a CONSTRAINT on any revision Cluster D might eventually adopt. Information-Flow - CONDITIONALLY depends on Cluster C's FR-005 for whether `position_exposure` becomes a new formula input (Section 9 above); independent of Cluster C for the threshold/multiplier-retention dimension. Determinism - any revision must preserve Cluster E's FR-009/FR-010 (CONSTRAINT, Section 11). Compatibility - explicitly bounded against reopening P2-03 (Drawdown/Drawdown-Ratio's own formula, already certified) and against reopening P2-02A (Position/Exposure ownership itself), per Cluster I's constraint (Section 15).

Dependent Capabilities: FR-008 (TD-006 closure) is HARD-dependent on FR-007: a Certification cannot record TD-006's risk-formula-half disposition (FR-008's Validation Condition, "a future Certification for this unit records an explicit TD-006 disposition") before the formula evaluation itself (FR-007) has produced a retain-or-revise outcome to record. Cluster A's FR-001 and Cluster B's FR-003 are each SOFTLY, informationally affected by FR-007's outcome (Sections 7, 8 above), neither blocked by it.

Failure if Introduced Too Early: attempting to close TD-006 (FR-008) before FR-007's evaluation completes would produce an unsupported closure claim, the same shape of risk the P2-03 SDA identified for publishing a computed value before its Computational Authority exists (that document's own DEP-003 finding).

Necessity Tests: Removal Test fails to remove Cluster D - without it, TD-006's own recorded Register description ("any change to RiskEngine's own risk-limiting formula... deferred to P2-04") remains textually unaddressed regardless of how completely Clusters A, B, and C are resolved. Compression Test - FR-007 (the scientific/architectural evaluation) and FR-008 (the governance/certification-record disposition operating on FR-007's outcome) are kept distinct rather than merged, a Purpose-versus-Verification-style separation analogous to the P2-03 SDA's own reasoning for keeping its relocation and consumer-boundary-verification clusters separate. Counterfactual Review - without Cluster D, TD-006 remains permanently open past this unit, with no further named successor unit to close it, since P2-03-AD-015 names P2-04 specifically as the closure venue. Conclusion: Cluster D is this unit's second central, currently-unresolved cluster, conditionally fed by Cluster C's FR-005 for one dimension only, internally hard-sequenced (FR-007 before FR-008), and constrained by Clusters A (FR-002), E, F, G, and I.

## 11. Determinism Dependencies (Cluster E)

Capability Definition: `RiskEngine.check()`'s purity and statelessness as a function of its three explicit parameters (`state`, `position`, `regime`) (FR-009), and the confirmation that RiskEngine holds no instance attribute beyond its three Risk Policy Configuration constants, set once and never mutated (FR-010).

Prerequisites: Scientific - AI-005 (Deterministic Execution), already fully satisfied (FRA Section 19, "already correctly satisfied"). Semantic/State/Ownership/Information-Flow - none pending; this cluster requires nothing further to become true, only independent re-verification. Determinism - this cluster's own subject. Compatibility - must not be disturbed by Cluster C or D's eventual resolution.

Dependent Capabilities: none forward; Cluster E instead CONSTRAINS Cluster C and Cluster D (any functional incorporation of `position_exposure`, FR-005 option b, or any revision of the risk-limiting formula, FR-007, must remain a pure, deterministic function of `state`/`position`/`regime` only, per FR-009's own Validation Condition, and must introduce no new persisted instance attribute, per FR-010's).

Failure if Introduced Too Early: not applicable in the missing-prerequisite sense (already satisfied); the inverse risk is regression - an incorrectly implemented functional incorporation of `position_exposure` that caches a value across calls, or a formula revision that reads wall-clock time or global state, would violate FR-009/FR-010 without any other requirement in this document independently catching it, which is precisely why this cluster's constraint edges into Clusters C and D are recorded explicitly rather than left implicit.

Necessity Tests: Removal Test fails to remove Cluster E - without independent re-verification, "Validate deterministic RiskEngine behaviour" (P2-04's own named Baseline objective) would rely solely on inherited P2-03 evidence never re-confirmed for this unit specifically, the exact gap the FRA's own Gap 5 identifies. Compression Test - Cluster E cannot be merged into Cluster F (Consumer Boundary) despite both being "already satisfied, verify only" clusters, since E concerns RiskEngine's own internal state while F concerns RiskEngine's treatment of externally-owned inputs - a component could in principle satisfy one while violating the other. Counterfactual Review - without Cluster E, no independently-recorded, RiskEngine-focused determinism finding would exist, and Cluster C/D's eventual implementation would have no explicit statelessness bound recorded against it. Conclusion: Cluster E is necessary, already satisfied, and functions purely as a constraint on Clusters C and D going forward.

## 12. Consumer Boundary Dependencies (Cluster F)

Capability Definition: RiskEngine's strictly read-only consumption of canonical Equity, Peak Equity, and Position (including Position-derived Exposure) (FR-011).

Prerequisites: Scientific - ADR-007 ("Risk Evaluation does not create runtime truth"), already satisfied. State/Ownership - the already-certified P2-03 boundary (Equity, Peak Equity) and the already-certified P2-02A boundary (Position, Exposure), unchanged. Compatibility - must be preserved by Cluster C's eventual implementation of FR-005.

Dependent Capabilities: none forward; Cluster F CONSTRAINS Cluster C (FR-005's eventual disposition must not turn RiskEngine into anything other than a read-only consumer of Equity, Peak Equity, and Position collectively). This constraint partially overlaps in subject matter with Cluster C's own internal FR-006 (RiskEngine remains read-only specifically toward Position-derived Exposure); the FRA deliberately keeps FR-006 and FR-011 as two distinct, separately-scoped requirements rather than one, since FR-011's scope (Equity, Peak Equity, Position collectively) is broader than FR-006's (Position/Exposure specifically) - this document records the overlap explicitly as a Dependency Finding (Section 22) rather than treating it as duplication, since any single future implementation change to `RiskEngine.check()`'s parameter handling must satisfy both simultaneously.

Failure if Introduced Too Early: not applicable (already satisfied); the inverse risk is regression during Cluster C's implementation of FR-005, specifically a broader regression than FR-006 alone would catch, since FR-011 additionally covers Equity and Peak Equity.

Necessity Tests: Removal Test fails to remove Cluster F - without it, no explicit compatibility-preservation requirement would exist for Equity and Peak Equity collectively (FR-006 alone covers only Position and Exposure, not Equity or Peak Equity). Compression Test - kept separate from Cluster C's FR-006 per the FRA's own requirement catalogue, which assigns them distinct IDs and distinct sections. Counterfactual Review - without Cluster F, Cluster C's eventual implementation of FR-005 could inadvertently affect RiskEngine's Equity/Peak-Equity consumption boundary, a different value set than Position/Exposure, with no explicit requirement catching it. Conclusion: Cluster F is necessary, already satisfied, and functions purely as a constraint on Cluster C going forward, partially and non-redundantly overlapping with Cluster C's own internal FR-006.

## 13. Failure Handling Dependencies (Cluster G)

Capability Definition: RUNTIME_FAILURE_EVENT non-mutation of Drawdown, Drawdown Ratio, and `risk_allocation_factor`, consistent with the already-certified P2-03 non-mutation contract, extended by analogy to the Risk Metric category (FR-012).

Prerequisites: Scientific - ADR-011, and the already-certified P2-03 non-mutation contract (P2-03 Final Certification, Section 20). State/Ownership - none new. Compatibility - the central content of this cluster.

Dependent Capabilities: none forward; Cluster G CONSTRAINS Cluster C and Cluster D (any eventual implementation of FR-005 or FR-007 must preserve non-mutation of Drawdown, Drawdown Ratio, and `risk_allocation_factor` across RUNTIME_FAILURE_EVENT ticks, since P2-04 "introduces no new financial-state-mutating logic and no new mutation risk to `risk.py` beyond whatever FR-005/FR-007 eventually decide," FRA Section 21).

Failure if Introduced Too Early: not applicable (already satisfied); the inverse risk is that a future FR-005/FR-007 implementation introduces a new mutation path (for example, if a `position_exposure` incorporation added a new code branch) without an explicit non-mutation check catching a regression across failure ticks.

Necessity Tests: Removal Test fails to remove Cluster G - without it, a future FR-005/FR-007 implementation could introduce a new mutation path with no explicit non-mutation requirement catching a regression. Compression Test - could in principle be merged into Cluster F (both are "read-only under some condition" properties), but FR-012 concerns temporal, event-conditioned non-mutation (a specific tick type, governed by AI-010/ADR-011) while FR-011 concerns unconditional per-call non-mutation (governed by ADR-007) - different scientific conditions, kept separate per the FRA's own section boundary. Counterfactual Review - without Cluster G, the P1-04/P2-03 non-mutation precedent chain would have an unverified gap at exactly the unit where the formula might change. Conclusion: Cluster G is necessary, already satisfied, and functions purely as a constraint on Clusters C and D going forward.

## 14. Reset Dependencies (Cluster H)

Capability Definition: reset semantics for Risk Policy Configuration, explicitly and textually conditional on Cluster A's FR-001 (FR-013).

Prerequisites: Scientific - AI-010 ("Financial Consistency... at all times," extended by analogy to Risk Metric consistency), no pending scientific requirement beyond Cluster A. State - explicitly conditional on Cluster A's FR-001 (FRA Section 22, Architectural Rationale: "conditional on FR-001's eventual resolution"). Ownership - if Cluster A resolves to keep Risk Policy Configuration `RiskEngine`-private, no reset mechanism is needed, since the three constants are never mutated after initialization (FR-010, Cluster E, a CONSTRAINT supplying this cluster's own Existing Evidence: "confirmed by FR-010's own evidence"); if Cluster A resolves toward publication elsewhere, reset semantics for that new owner become necessary. Information-Flow/Determinism - none new. Compatibility - must not disturb `CanonicalState.reset()`'s existing, already-certified behavior (Cluster I constraint).

Dependent Capabilities: none forward; Cluster H is terminal within this unit's own dependency structure.

Failure if Introduced Too Early: finalizing FR-013's reset design before FR-001 is resolved risks either designing a reset mechanism for a Risk Policy Configuration ownership model that is not the one eventually adopted, or overlooking the need for one entirely.

Necessity Tests: Removal Test fails to remove Cluster H - without it, AI-010's "at all times" consistency requirement would not be explicitly re-verified against whatever Cluster A eventually decides. Compression Test - cannot be merged into Cluster A, since A concerns who owns the configuration while H concerns what happens to it on reset, a downstream consequence rather than the same question. Counterfactual Review - without Cluster H, a future Architecture decision for Cluster A could omit reset semantics entirely, an AI-010 violation risk. Conclusion: Cluster H is necessary, small, and hard-gated (CONDITIONAL) by Cluster A's FR-001, additionally constrained by Cluster E's FR-010.

## 15. Compatibility Dependencies (Cluster I)

Capability Definition: the complete, already-certified set of P1-03, P1-03.1, P1-04, P2-01, P2-02, P2-02A, and P2-03 contracts that constrain every other cluster's eventual resolution (FR-014, Sub-cluster I1), and explicit scope-protection against `PerformanceEngine`'s consumption (or non-consumption) of Risk Metrics being incidentally resolved as a side effect of Clusters A through D, pending resolution of whether that question belongs to P2-04 or P3-03 (FR-015, Sub-cluster I2) - the same cross-cutting, non-sequential role the P2-03 SDA's own Cluster H played for that unit, split internally here because I1 preserves already-certified behavior while I2 protects against expansion into genuinely undecided, cross-unit-boundary territory, a distinction with no counterpart in P2-03's own Cluster H.

Prerequisites: Sub-cluster I1 (FR-014) - Scientific: requires the already-completed P1/P2-0x certification chain to exist as the frozen reference baseline; fully satisfied, verified present at HEAD `a81e197` (Section 4). Sub-cluster I2 (FR-015) - Scientific: requires no prerequisite of its own; its Validation Condition ("any future document that brings PerformanceEngine's Risk-Metric consumption into P2-04's scope does so explicitly, not as an incidental side effect of FR-001 through FR-008") is itself a CONSTRAINT on Clusters A through D, not a target awaiting their resolution.

Dependent Capabilities: all of Clusters A through H are constrained by Cluster I; Cluster I does not depend on any of them, since I1 is a validation/constraint layer defined entirely by already-certified prior work and I2 is a scope-protection requirement bounding the other clusters' resolution rather than awaiting it.

Failure if Introduced Too Early: not applicable in the ordering sense (Cluster I is not sequenced, it is omnipresent); the relevant failure mode is omission - implementing any of Clusters A through D without explicitly checking against Cluster I1's enumerated contracts risks a silent regression of already-certified P2-03/P2-02A behavior, and resolving Cluster D's FR-007 in a way that happens to also determine `PerformanceEngine`'s Risk-Metric consumption boundary would violate I2 even if no single line of `performance.py` were touched, since the violation is about incidental scope determination, not code modification.

Necessity Tests: Removal Test fails to remove Cluster I - without I1 made explicit, implementation work in Clusters A through D risks silently violating certified behavior; without I2 made explicit, the Gap 6 boundary question (P2-04 or P3-03) could be silently settled by omission rather than by an explicit future document. Compression Test - I1 and I2 are legitimately separable (I1 requires no open decision and is already fully satisfied; I2 is itself an open scope-boundary question, Section 16, OQ-005), so treating Cluster I as monolithic would understate its internal heterogeneity; this document records the split explicitly, consistent with the P2-03 SDA's own precedent of recording internal cluster splits where scientifically warranted. Counterfactual Review - without Cluster I made explicit, the certified P1/P2-0x contract set and the Gap 6 boundary question would still exist as facts, but would not be actively checked against during P2-04's resolution, materially increasing both regression risk and scope-creep risk. Conclusion: Cluster I is necessary as an explicit, non-sequential, dual-purpose constraint layer; I1 is already fully satisfied and requires no new decision; I2 is itself conditionally open (Section 16, OQ-005) and constrains Clusters A through D without waiting for their resolution.

## 16. Open Question Classification

**OQ-001 - Whether Risk Policy Configuration requires publication to `CanonicalState` or may remain explicitly, documentedly `RiskEngine`-private.**
Classification: CONDITIONALLY BLOCKING.
Rationale: blocks FR-001's exact implementation shape and, transitively, Cluster H's reset-design shape; does not block the underlying requirement that ownership be explicitly named, which holds under either option. Referenced requirements: FR-001, FR-013.

**OQ-002 - If `position_exposure` is functionally incorporated (FR-005 option b), what is the intended relationship between current market exposure and `risk_allocation_factor`.**
Classification: CONDITIONALLY BLOCKING.
Rationale: blocks Cluster D's exact formula shape only if Cluster C resolves toward option (b); does not block Cluster C's own disposition decision, which could still resolve toward option (a) without this question ever needing resolution. Referenced requirements: FR-005, FR-007.

**OQ-003 - Whether `risk_allocation_factor`'s current binary step function is the scientifically intended shape, or should become continuous.**
Classification: CONDITIONALLY BLOCKING.
Rationale: blocks FR-007's exact resolution shape, not the requirement that an explicit evaluation occur; FR-007 is satisfiable by an explicit "retain as-is, with recorded rationale" outcome without this question being separately resolved. Referenced requirements: FR-007.

**OQ-004 - Whether the specific numeric values of the Risk Policy Configuration are themselves correct.**
Classification: NON-BLOCKING.
Rationale: explicitly and repeatedly stated by the FRA itself as outside its own scope (numeric calibration, not ownership); does not affect any dependency recorded in this document, since every dependency here concerns ownership, naming, or evaluation status, never a specific threshold value. Referenced requirements: none directly (FRA Section 28, explicit non-scope note).

**OQ-005 - Whether closing Gap 6 (`PerformanceEngine`'s non-consumption of Risk Metrics) belongs to P2-04 or to P3-03.**
Classification: CONDITIONALLY BLOCKING.
Rationale: blocks Cluster I's I2 sub-cluster's exact closure venue; does not block I2's scope-protection function itself (FR-015), which holds as a constraint regardless of which unit eventually resolves Gap 6. Referenced requirements: FR-015.

**OQ-006 - Whether the regime-dampening multipliers belong to "Risk Policy Configuration" (Cluster A) or to the "Risk-Limiting Formula" (Cluster D) for classification purposes.**
Classification: NON-BLOCKING.
Rationale: a classification-only question; the FRA itself classifies the multipliers under both clusters simultaneously (its Sections 7 and 8), and this document's own Cluster A and Cluster D analyses do the same (Sections 7, 10 above) without requiring the ambiguity to be resolved first; no dependency recorded in this document is contingent on this classification being sharpened. Referenced requirements: FR-001, FR-007.

**OQ-007 - Naming clarity of `RiskEngine.check()`'s internal `exposure` local variable relative to `position_exposure`.**
Classification: NON-BLOCKING.
Rationale: purely cosmetic, confirmed non-functional by the FRA itself; no dependency in this document is affected by this variable's name. Referenced requirements: none.

No Open Question blocks the scientific progression from Scientific Dependency Analysis to Capability Gap Analysis. Four Open Questions remain conditionally blocking for subsequent Architecture-stage decisions, each with a precisely scoped blocking effect limited to an implementation-detail or scope-boundary question, never to this document's own dependency conclusions. This is the direct consequence of Section 4's structural observation: P2-04's genuinely open work is concentrated in two small, mutually-informing clusters (C, D), each of which is independently resolvable in outline (an explicit disposition or evaluation can be recorded) even where its exact implementation detail remains open.

## 17. Technical-Debt Dependency Classification

**Directly and immediately affected by this dependency structure:**

- TD-006 (RiskEngine Peak Equity and Drawdown Ownership Duplication) - its Equity/Peak-Equity/Drawdown-input-source half is fully certified resolved by P2-03 (P2-03 Final Certification, Section 32) and is not reopened by any dependency recorded in this document; its remaining risk-formula half is the direct target of Cluster D (FR-007, FR-008), per P2-03-AD-015's explicit naming of this unit as the closure venue. Confirmed unchanged, risk-formula half still open, at HEAD `a81e197` (FRA Section 27).

**Adjacent but not identical, referenced for scope-boundary precision only:**

- TD-006's risk-formula half, as distinct from Cluster A's FR-001 (Risk Policy Configuration ownership-naming) - the FRA's own FR-001 text states this distinction explicitly ("Related Technical Debt: adjacent to TD-006's risk-formula half (Gap 4), not identical to it"); Cluster A concerns WHO owns the configuration values, Cluster D concerns WHETHER and HOW the formula itself changes, a distinction this document's Cluster A/Cluster D Compression Tests (Sections 7, 10) independently confirm.

**Referenced only for compatibility preservation, not implicated by this dependency structure's own targets:**

- TD-001 (Canonical Position Source for PnLEngine) - functionally resolved per P2-02A Final Certification (Register Status: Deferred); referenced only by Cluster I's FR-014 as a contract to preserve, not reopened.
- TD-003 (Document Pre-Trade Snapshot Dependency) - Partially Resolved (P2-02A recommendation, register not yet updated); referenced only by Cluster I's FR-014, not reopened.

**Confirmed follow-on work only, outside this dependency structure entirely:**

- TD-002 (Unify `_safe_float` implementations) - `RiskEngine` has no `_safe_float` method of any kind (FRA Section 27); no dependency record in this document touches it.
- TD-004 (Lifecycle-based Performance Evaluation) - unrelated to any Cluster A through I dependency; `PerformanceEngine`'s statistics model is unaffected by this document's requirements, distinct from Cluster I's FR-015 scope-protection question, which concerns Risk-Metric consumption, not statistics-model design.
- TD-005 (Automated Regression Test Suite) - project-wide, explicitly out of scope (FRA Section 24); no dependency record references it as a prerequisite or target.
- TD-007 (RunLoop Lifecycle Control Surface) - unrelated to Risk Ownership; not referenced by any cluster in this document.

## 18. Dependency Catalogue

Sixteen dependencies were identified and assigned stable IDs, sourced entirely from the FRA's own requirement text, the Architecture Baseline, and the Technical Debt Register; none introduces a new requirement, interface, formula, or ownership assignment.

**P2-04-DEP-001**
Source: FR-002 (Cluster A, already-conformant Computational Authority). Target: FR-003 (Cluster B).
Type: OWNERSHIP. Relationship: CONSTRAINT (not sequential).
Rationale: FR-003's individual naming of `risk_allocation_factor`'s Computational Authority must name `RiskEngine`, since FR-002 already establishes this mechanically; FR-003 does not wait for FR-002, since FR-002 is already true.
Referenced FRA Requirements: FR-002, FR-003.
Blocking Effect: NON-BLOCKING as sequencing; HARD as a correctness constraint on FR-003's eventual resolution.
Evidence: FRA Section 15 (FR-002's Existing Evidence), Section 16 (FR-003's Scientific Rationale).
Related ADR: ADR-007. Related Technical Debt: none.

**P2-04-DEP-002**
Source: FR-004 (Cluster B, already-conformant storage location). Target: FR-003 (Cluster B).
Type: OWNERSHIP. Relationship: CONSTRAINT.
Rationale: FR-003's individual naming of `risk_allocation_factor`'s Authoritative Owner must name `CanonicalState`, since FR-004 already establishes this storage location mechanically; FR-003 does not wait for FR-004.
Referenced FRA Requirements: FR-003, FR-004.
Blocking Effect: NON-BLOCKING as sequencing; HARD as a correctness constraint.
Evidence: FRA Section 9, Section 16 (FR-004's Existing Evidence).
Related ADR: ADR-006, Rule OM-006. Related Technical Debt: none.

**P2-04-DEP-003**
Source: FR-006 (Cluster C, already-certified read-only boundary). Target: FR-005 (Cluster C).
Type: OWNERSHIP. Relationship: CONSTRAINT.
Rationale: whatever disposition FR-005 selects, it must preserve RiskEngine's already-certified read-only, non-owning consumption of Position and Exposure; FR-005 does not wait for FR-006, since FR-006 is already true (P2-02A-AD-008).
Referenced FRA Requirements: FR-005, FR-006.
Blocking Effect: NON-BLOCKING as sequencing; HARD as a correctness constraint.
Evidence: FRA Section 10, Section 17 (FR-006's Existing Evidence).
Related ADR: ADR-004, ADR-007, Rule OM-007. Related Technical Debt: none.

**P2-04-DEP-004**
Source: FR-005 (Cluster C). Target: FR-007 (Cluster D).
Type: INFORMATION_FLOW. Strength: CONDITIONAL.
Rationale: if FR-005 resolves toward functional incorporation (option b), the risk-limiting formula gains a new input path from `position_exposure`; if FR-005 resolves toward option (a), FR-007's threshold/multiplier-retention dimension is unaffected and may proceed independently.
Referenced FRA Requirements: FR-005, FR-007.
Blocking Effect: CONDITIONALLY BLOCKING (blocks only FR-007's position-exposure-input dimension, not its threshold/multiplier dimension).
Evidence: FRA Section 17 (FR-005's Existing Evidence and Validation Condition), Section 18 (FR-007's Architectural Rationale).
Related ADR: ADR-004, ADR-007. Related Technical Debt: TD-006 (risk-formula half).

**P2-04-DEP-005**
Source: FR-007 (Cluster D). Target: FR-008 (Cluster D).
Type: GOVERNANCE. Strength: HARD.
Rationale: TD-006's risk-formula-half disposition cannot be recorded before the formula evaluation itself has produced a retain-or-revise outcome to record.
Referenced FRA Requirements: FR-007, FR-008.
Blocking Effect: BLOCKING for FR-008.
Evidence: FRA Section 18 (FR-007, FR-008 sequential placement within Risk-Limiting Formula Requirements).
Related ADR: ADR-006, ADR-007. Related Technical Debt: TD-006.

**P2-04-DEP-006**
Source: FR-007 (Cluster D). Target: FR-001 (Cluster A).
Type: SCIENTIFIC/SCOPE. Strength: SOFT.
Rationale: if the formula evaluation changes which values parameterize the risk-limiting computation, FR-001's ownership-naming scope may need to describe a different or extended value set; FR-001's own underlying requirement (that some explicit ownership exist) does not depend on FR-007's outcome.
Referenced FRA Requirements: FR-001, FR-007.
Blocking Effect: NON-BLOCKING; informational only.
Evidence: FRA Section 15 (FR-001's Existing Evidence), Section 18 (FR-007's Scope Classification).
Related ADR: ADR-007. Related Technical Debt: none.

**P2-04-DEP-007**
Source: FR-007 (Cluster D). Target: FR-003 (Cluster B).
Type: SCIENTIFIC/SCOPE. Strength: SOFT.
Rationale: if the formula evaluation changes `risk_allocation_factor`'s computation, FR-003's eventual naming description may need to reflect the revised formula; FR-003's underlying ownership-category assignment (RiskEngine/CanonicalState) does not depend on FR-007's outcome.
Referenced FRA Requirements: FR-003, FR-007.
Blocking Effect: NON-BLOCKING; informational only.
Evidence: FRA Section 16 (FR-003's Existing Evidence), Section 18 (FR-007's Existing Evidence).
Related ADR: ADR-007. Related Technical Debt: none.

**P2-04-DEP-008**
Source: FR-001 (Cluster A). Target: FR-013 (Cluster H).
Type: STATE. Strength: CONDITIONAL.
Rationale: FR-013's reset-scope determination is explicitly, textually conditional on FR-001's eventual resolution ("conditional on FR-001's eventual resolution," FRA Section 22).
Referenced FRA Requirements: FR-001, FR-013.
Blocking Effect: CONDITIONALLY BLOCKING for FR-013's exact implementation.
Evidence: FRA Section 22 (FR-013's Architectural Rationale, verbatim).
Related ADR: AI-010. Related Technical Debt: none.

**P2-04-DEP-009**
Source: FR-009, FR-010 (Cluster E). Target: FR-005 (Cluster C), FR-007 (Cluster D).
Type: DETERMINISM. Relationship: CONSTRAINT.
Rationale: any eventual implementation of FR-005 (functional incorporation) or FR-007 (formula revision) must remain a pure, deterministic function of `state`/`position`/`regime` and must introduce no new persisted instance attribute, per FR-009's and FR-010's own Validation Conditions.
Referenced FRA Requirements: FR-005, FR-007, FR-009, FR-010.
Blocking Effect: NON-BLOCKING as sequencing; HARD as a correctness constraint.
Evidence: FRA Section 19 (FR-009, FR-010 Validation Conditions).
Related ADR: AI-005, ADR-007, Rule OM-007. Related Technical Debt: none.

**P2-04-DEP-010**
Source: FR-011 (Cluster F). Target: FR-005 (Cluster C).
Type: OWNERSHIP. Relationship: CONSTRAINT.
Rationale: FR-005's eventual disposition must not turn RiskEngine into anything other than a strictly read-only consumer of Equity, Peak Equity, and Position collectively, a broader bound than FR-006/DEP-003 alone (Position/Exposure only).
Referenced FRA Requirements: FR-005, FR-011.
Blocking Effect: NON-BLOCKING as sequencing; HARD as a correctness constraint.
Evidence: FRA Section 20 (FR-011's Existing Evidence and Validation Condition).
Related ADR: ADR-007. Related Technical Debt: none.

**P2-04-DEP-011**
Source: FR-012 (Cluster G). Target: FR-005 (Cluster C), FR-007 (Cluster D).
Type: COMPATIBILITY. Relationship: CONSTRAINT.
Rationale: any eventual implementation of FR-005 or FR-007 must preserve RUNTIME_FAILURE_EVENT non-mutation of Drawdown, Drawdown Ratio, and `risk_allocation_factor`, per FR-012's own Architectural Rationale ("P2-04 introduces no new financial-state-mutating logic and no new mutation risk to `risk.py` beyond whatever FR-005/FR-007 eventually decide").
Referenced FRA Requirements: FR-005, FR-007, FR-012.
Blocking Effect: NON-BLOCKING as sequencing; HARD as a correctness constraint.
Evidence: FRA Section 21 (FR-012's Architectural Rationale, verbatim).
Related ADR: ADR-011. Related Technical Debt: none.

**P2-04-DEP-012**
Source: FR-014 (Cluster I1). Target: Clusters A through H (all).
Type: COMPATIBILITY. Relationship: CONSTRAINT.
Rationale: every cluster's resolution must preserve the enumerated P1/P2-0x Risk-adjacent contracts (Drawdown/Drawdown-Ratio formula, ownership, and canonical input source per P2-03; Position/Exposure separation and RiskEngine's read-only boundary per P2-02A); this is a constraint applied at every node, not a sequencing gate.
Referenced FRA Requirements: FR-014.
Blocking Effect: BLOCKING as a constraint (violation invalidates the responsible cluster's resolution); NON-BLOCKING as a scheduling delay.
Evidence: FRA Section 23 (FR-014's Existing Evidence, citing P2-03/P2-02A certifications).
Related ADR: ADR-004, ADR-006, ADR-007, ADR-011. Related Technical Debt: none.

**P2-04-DEP-013**
Source: FR-015 (Cluster I2). Target: FR-001 through FR-008 (Clusters A, B, C, D).
Type: GOVERNANCE. Relationship: CONSTRAINT.
Rationale: FR-015's own Validation Condition explicitly requires that any future document bringing `PerformanceEngine`'s Risk-Metric consumption into P2-04's scope do so explicitly, "not as an incidental side effect of FR-001 through FR-008"; this bounds those eight requirements' resolution without gating their timing.
Referenced FRA Requirements: FR-001 through FR-008, FR-015.
Blocking Effect: BLOCKING as a constraint (an incidental resolution of Gap 6 by any of FR-001 through FR-008 would violate FR-015); NON-BLOCKING as a scheduling delay.
Evidence: FRA Section 23 (FR-015's Validation Condition, verbatim).
Related ADR: ADR-008 (by contrast), Runtime Ownership Matrix. Related Technical Debt: none.

**P2-04-DEP-014** (external)
Source: TD-006 (external, already-logged, risk-formula half). Target: FR-007, FR-008 (Cluster D).
Type: GOVERNANCE. Strength: HARD.
Rationale: TD-006's own recorded description, as bounded by P2-03-AD-015 ("any change to RiskEngine's own risk-limiting formula... deferred to P2-04"), names exactly the defect Cluster D's FR-007/FR-008 close; this document's dependency records for these two requirements directly operationalize TD-006's already-approved, already-existing disposition rather than introducing a new one.
Referenced FRA Requirements: FR-007, FR-008.
Blocking Effect: NON-BLOCKING to this document's own conclusions (TD-006 already assigns this territory to P2-04); constrains scope only.
Evidence: `ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md`, TD-006; `P2_03_FINANCIAL_OWNERSHIP_ARCHITECTURE_V1_2026-07-11.md`, P2-03-AD-015; FRA Section 27.
Related ADR: ADR-006, ADR-007. Related Technical Debt: TD-006.

**P2-04-DEP-015**
Source: FR-002 (Cluster A). Target: FR-007 (Cluster D).
Type: OWNERSHIP. Relationship: CONSTRAINT.
Rationale: any revision Cluster D eventually adopts must preserve RiskEngine as sole Computational Authority for `risk_allocation_factor`, since FR-002 already establishes this exclusively; a revision introducing a second computing component for any part of the formula would violate FR-002.
Referenced FRA Requirements: FR-002, FR-007.
Blocking Effect: NON-BLOCKING as sequencing; HARD as a correctness constraint.
Evidence: FRA Section 15 (FR-002's Validation Condition).
Related ADR: ADR-007. Related Technical Debt: none.

**P2-04-DEP-016**
Source: FR-010 (Cluster E). Target: FR-013 (Cluster H).
Type: STATE. Relationship: CONSTRAINT.
Rationale: FR-013's own Existing Evidence directly cites FR-010's finding (Risk Policy Configuration constants "set once, never reassigned, confirmed by FR-010's own evidence") as the basis for its claim that no dedicated reset logic is required if Risk Policy Configuration remains RiskEngine-private.
Referenced FRA Requirements: FR-010, FR-013.
Blocking Effect: NON-BLOCKING as sequencing; supplies evidentiary and correctness grounding for FR-013's conditional resolution.
Evidence: FRA Section 22 (FR-013's Existing Evidence, verbatim cross-reference to FR-010).
Related ADR: AI-010, ADR-007. Related Technical Debt: none.

### 18.1 Dependency Findings Preview

Two of the sixteen catalogued dependencies (DEP-006, DEP-007) were explicitly tested against the Removal Test and found not to meet the HARD or CONDITIONAL bar: removing either would not make its target's resolution impossible or unverifiable, only potentially require an editorial revision later. Both are recorded as SOFT, informational-only dependencies rather than omitted entirely, consistent with the P2-03 SDA's own precedent (its DEP-014) of recording genuine-but-non-blocking relationships explicitly rather than silently dropping them. This finding, and seven others, are consolidated in Section 22 (Dependency Findings) below.

## 19. Dependency Graph

Structural overview of the sixteen catalogued dependencies (Section 18), grouped by relationship kind.

**PREREQUISITE edges (sequential, participate in the cycle check):**
```
C(FR-005) --CONDITIONAL--> D(FR-007)
D(FR-007) --HARD--> D(FR-008)
D(FR-007) --SOFT--> A(FR-001)
D(FR-007) --SOFT--> B(FR-003)
A(FR-001) --CONDITIONAL--> H(FR-013)
```

**CONSTRAINT edges (non-sequential, bound resolution without gating timing, excluded from the cycle check):**
```
A(FR-002) -----> B(FR-003)        [DEP-001]
B(FR-004) -----> B(FR-003)        [DEP-002]
C(FR-006) -----> C(FR-005)        [DEP-003]
E(FR-009,FR-010) -----> C(FR-005), D(FR-007)   [DEP-009]
F(FR-011) -----> C(FR-005)        [DEP-010]
G(FR-012) -----> C(FR-005), D(FR-007)   [DEP-011]
I(FR-014) -----> A,B,C,D,E,F,G,H (all)  [DEP-012]
I(FR-015) -----> A,B,C,D (FR-001..FR-008)  [DEP-013]
A(FR-002) -----> D(FR-007)        [DEP-015]
E(FR-010) -----> H(FR-013)        [DEP-016]
```

**External-facing edge (governance, not part of either check):**
```
TD-006 (risk-formula half, external) -----> D(FR-007, FR-008)   [DEP-014]
```

### 19.1 Cycle Check

Topological trace of all sequential (PREREQUISITE-type, non-CONSTRAINT) edges: C(FR-005) to D(FR-007); D(FR-007) to D(FR-008); D(FR-007) to A(FR-001, soft); D(FR-007) to B(FR-003, soft); A(FR-001) to H(FR-013, conditional). Every terminal node reached (FR-008, FR-001-to-FR-013's own terminus, FR-003) has no further outbound sequential edge: FR-008 is terminal within Cluster D; FR-013 is terminal within Cluster H; FR-003 has no outbound sequential edge, only inbound CONSTRAINT edges (DEP-001, DEP-002). No edge points from a later-reached node back to FR-005 or to any earlier node in the sequential sense. No dependency cycle exists among the sequential edges. CONSTRAINT-type edges (DEP-001, DEP-002, DEP-003, DEP-009, DEP-010, DEP-011, DEP-012, DEP-013, DEP-015, DEP-016) are excluded from this check by construction, since they represent bounds on an implementation rather than participation in the ordering, exactly as the P2-03 SDA excluded its own Cluster H and fixed-reference-frame constraint edges.

## 20. Dependency Matrix

Rows are source clusters, columns are target clusters. Cell values give the dependency ID and strength, or a dash where no dependency was found to survive its Removal Test. Cluster I applies identically to most columns (DEP-012, DEP-013) and is given a summary row rather than repeated per cell.

| Source \ Target | A | B | C | D | E | F | G | H |
|---|---|---|---|---|---|---|---|---|
| A | - | DEP-001 (CONSTRAINT) | - | DEP-015 (CONSTRAINT) | - | - | - | DEP-008 (CONDITIONAL) |
| B | - | DEP-002 (internal, CONSTRAINT) | - | - | - | - | - | - |
| C | - | - | DEP-003 (internal, CONSTRAINT) | DEP-004 (CONDITIONAL) | - | - | - | - |
| D | DEP-006 (SOFT) | DEP-007 (SOFT) | - | DEP-005 (internal, HARD) | - | - | - | - |
| E | - | - | DEP-009 (CONSTRAINT) | DEP-009 (CONSTRAINT) | - | - | - | DEP-016 (CONSTRAINT) |
| F | - | - | DEP-010 (CONSTRAINT) | - | - | - | - | - |
| G | - | - | DEP-011 (CONSTRAINT) | DEP-011 (CONSTRAINT) | - | - | - | - |
| H | - | - | - | - | - | - | - | - |
| I | DEP-013 | DEP-013 | DEP-013 | DEP-012, DEP-013 | - | - | - | DEP-012 |

External-facing dependency not represented in this square matrix: DEP-014 (TD-006, external, to Cluster D), recorded separately in Section 18 and Section 19 since it originates outside the FRA's own fifteen-requirement set.

## 21. Minimal Prerequisite Capability Analysis

The hypothesis under test: Cluster C's FR-005 (Position-derived Exposure disposition) is the minimal prerequisite without which Cluster D's Risk-Limiting Formula Evaluation (FR-007, FR-008) cannot be correctly closed.

**Removal Test applied to the hypothesis.** If FR-005 remains unresolved: FR-007's position-exposure-input dimension cannot be finalized (DEP-004, CONDITIONAL) - confirmed, but only for that one dimension. FR-007's threshold/multiplier-retention dimension proceeds unaffected - hypothesis does not hold here. FR-008 (TD-006 closure) is gated by FR-007 (DEP-005, HARD) regardless of FR-005's status, so FR-005's unresolved state only indirectly, partially delays FR-008, through FR-007's own incompleteness rather than through any direct edge - hypothesis holds only in this weaker, mediated sense. Cluster A's FR-001 and Cluster B's FR-003 proceed unaffected by FR-005 directly (no edge exists from C to A or C to B) - hypothesis does not hold here. Clusters E, F, G, and I proceed entirely unaffected, being already satisfied or purely constraint-supplying - hypothesis does not hold here.

**Compression Test.** A more precisely scoped, still-accurate restatement of the hypothesis is available: FR-005 is the minimal prerequisite for exactly one dimension of FR-007 (whether `position_exposure` becomes a formula input), not for FR-007's full scope, and not directly for FR-008, FR-001, or FR-003 at all.

**Counterfactual Review.** What happens if FR-005 is never resolved: FR-007 can still be explicitly evaluated and its threshold/multiplier dimension explicitly retained or revised, and FR-008 can still record TD-006's disposition on that basis; the resulting closure would be scientifically complete for the threshold/multiplier question but would leave the position-exposure-input question permanently open, which is itself already Gap 3's own permanent-open-question framing (FRA Section 13) rather than a new failure this analysis introduces. Can the problem be solved equally simply without FR-005: partially - FR-007/FR-008's threshold/multiplier dimension can close independently, but the position-exposure-input dimension cannot, by definition. Does resolving FR-005 create a new necessary capability, or only a different representation: it is the direct, textual fulfillment of P2-02A-AD-008's own explicit deferral, not a new capability being invented. Can the overall P2-04 requirement set be met without FR-005: no, not in full - FR-005 is itself one of the fifteen requirements and must be resolved on its own terms regardless of its effect on FR-007.

**Alternative minimal-prerequisite candidates considered and rejected as the primary answer:**
- Cluster A (Risk Policy Configuration Ownership): already largely independent of every other cluster except a soft, informational inbound edge from Cluster D; necessary as its own requirement but does not gate Cluster D or C in either direction.
- Cluster E (Determinism): already fully satisfied and functions only as a constraint on Clusters C and D, never as a prerequisite gating their timing.
- Cluster I (Compatibility): a constant, non-sequential constraint on every cluster, but supplies no new capability itself and cannot serve as a "prerequisite" in the sequential sense this analysis tests.

**Conclusion.** The hypothesis is confirmed only in a narrowed, precisely-scoped form: FR-005 is the minimal prerequisite for exactly one dimension of FR-007 (the position-exposure-input question), not for Cluster D's full scope, and not for any other cluster in this document. Unlike P2-03, where a single cluster hard-gated the value-correctness or consistency-verification portions of five of the remaining six clusters, P2-04's dependency structure does not decompose around one dominant node; its only genuinely HARD forward-sequential dependencies are internal to Cluster D itself (FR-007 before FR-008) and the FR-001-to-FR-013 conditional pairing, with Cluster C's contribution to Cluster D being real but narrower than a full gate.

## 22. Alternative Dependency Structures

**Alternative structure 1: single linear chain (A - B - C - D - E - F - G - H), with I applied only at the end.** Rejected. Not supported by the evidence: Clusters E, F, and G are demonstrably already satisfied and unblocked by any prior cluster (Sections 11-13), and Cluster B's FR-004 half and Cluster A's FR-002 half are likewise already satisfied; forcing a linear order would delay their reconfirmation behind Clusters A through D's resolution without scientific justification.

**Alternative structure 2: fully parallel, no ordering constraints.** Rejected. Contradicted by the confirmed HARD/CONDITIONAL dependencies within Cluster D (DEP-005) and between Clusters A and H (DEP-008) and C and D (DEP-004), each independently justified by a concrete Failure if Introduced Too Early scenario (Sections 10, 14, 9). Some ordering is scientifically required, not merely a matter of implementation convenience.

**Alternative structure 3 (adopted): two small, loosely-coupled open clusters (C, D) with a narrow, single-dimension bridge between them, surrounded by a large fixed reference frame (A's FR-002 half, B's FR-004 half, E, F, G) that constrains but never gates them, one small conditionally-gated terminal cluster (H), and a cross-cutting constraint layer (I).** Supported directly by the Dependency Graph (Section 19) and the Minimal Prerequisite Analysis (Section 21): unlike P2-02A's two-independent-tracks structure and P2-03's single-dominant-cluster structure, P2-04 has no node from which the majority of remaining open work is transitively reachable; Cluster D's own internal FR-007-to-FR-008 pairing and Cluster A's FR-001-to-FR-013 pairing are the only HARD sequential edges in the entire graph, both narrowly scoped and both internal to a single cluster's own two requirements. This structure is adopted for Section 23's Derived Dependency Stages.

## 23. Dependency Layers (Derived Dependency Stages)

This ordering follows directly from the Dependency Graph (Section 19) and the adopted structure (Section 22, alternative 3). It states which requirements must be resolved or confirmed at each logical stage and why; it does not prescribe implementation order, file order, interface shape, or code changes.

**Dependency Stage 0 - Foundational (already satisfied, fixed reference frame).**
Confirm: FR-002, FR-004 (storage-location half), FR-009, FR-010, FR-011, FR-012 remain true and unregressed; Cluster I's FR-014 remains active as a continuous constraint.
Why first: every later stage's Compatibility Prerequisites cite one or more of these as already-satisfied preconditions (Sections 7-15).
Unlocks: nothing new; establishes the constraint boundary every later stage must respect.
FRA Requirements involved: FR-002, FR-004, FR-009, FR-010, FR-011, FR-012, FR-014.

**Dependency Stage 1 - Central Open Decisions (independently resolvable).**
Resolve: FR-005 (Cluster C) and FR-007's threshold/multiplier dimension (Cluster D), each gated only by Stage 0's constraints, not by each other for this dimension.
Why first (within this stage): FR-005 and FR-007's threshold/multiplier dimension share no HARD edge between them in Section 19; both are gated only by Stage 0 (already satisfied) and bounded by Cluster I's FR-014/FR-015 (constraint, not gate).
Unlocks: FR-007's full resolution (Stage 2, once FR-005's outcome is known for the position-exposure-input dimension), FR-013's conditional resolution path (Stage 3, via FR-001).
FRA Requirements involved: FR-005, FR-007 (partial).

**Dependency Stage 2 - Formula Finalization and TD-006 Closure.**
Resolve: FR-007 (fully, incorporating Stage 1's FR-005 outcome for its position-exposure-input dimension, DEP-004), FR-008 (DEP-005, requiring FR-007's completion).
Why first: FR-008's Validation Condition requires FR-007's evaluation outcome to exist before a disposition can be recorded; this is the direct operational closure of TD-006's remaining risk-formula half (DEP-014).
Unlocks: nothing further within P2-04 beyond contributing to Cluster B's and Cluster A's soft, informational naming descriptions (DEP-006, DEP-007).
FRA Requirements involved: FR-007, FR-008.

**Dependency Stage 3 - Independent Naming Confirmations.**
Confirm or resolve: FR-001 (Cluster A), FR-003 (Cluster B), each softly informed by Stage 2's FR-007 outcome (DEP-006, DEP-007) but not blocked by it, and each bounded by Cluster I's FR-014/FR-015 (DEP-012, DEP-013).
Why first (relative to Stage 4): FR-013's conditional resolution (Stage 4) requires FR-001 specifically, not FR-003; FR-003 has no further downstream dependent within P2-04.
Unlocks: FR-013 (Stage 4).
FRA Requirements involved: FR-001, FR-003.

**Dependency Stage 4 - Reset Finalization.**
Resolve: FR-013, gated by Stage 3's FR-001 (DEP-008, CONDITIONAL) and informed by Stage 0's FR-010 (DEP-016).
Why last: FR-013's own text is explicitly conditional on FR-001's resolution; resolving it earlier risks designing reset semantics for an ownership model not yet adopted.
Unlocks: nothing further within P2-04; terminal stage.
FRA Requirements involved: FR-013.

**Not bound to any specific stage (already satisfied, may be reconfirmed at any point without gating anything):** FR-002, FR-004 (storage-location half), FR-009, FR-010, FR-011, FR-012 (Stage 0's own members, restated here for completeness since "not gated" and "not gating" are distinct properties this document tracks separately). FR-014 and FR-015 (Cluster I) apply continuously across every stage and are not themselves staged.

## 24. Dependency Constraints

Consolidated list of every CONSTRAINT-type relationship recorded in this document (Section 18), together with external and deferred constraints the FRA itself already established (its Section 24). Constraints bound how a target requirement may be resolved without gating when it may be resolved.

**Internal constraints (already-conformant source, bounding an open target):**
- DEP-001: FR-002 bounds FR-003's Computational Authority naming.
- DEP-002: FR-004 bounds FR-003's Authoritative Owner naming.
- DEP-003: FR-006 bounds FR-005's disposition.
- DEP-009: FR-009/FR-010 bound FR-005's and FR-007's determinism.
- DEP-010: FR-011 bounds FR-005's disposition (Equity/Peak-Equity/Position collectively).
- DEP-011: FR-012 bounds FR-005's and FR-007's non-mutation behavior.
- DEP-015: FR-002 bounds FR-007's Computational Authority preservation.
- DEP-016: FR-010 informs FR-013's reset-necessity determination.

**Cross-cutting constraints (apply to every cluster, not sourced from a single already-conformant requirement):**
- DEP-012: FR-014 (the complete, already-certified P1/P2-0x Risk-adjacent contract set) bounds every cluster (A through H).
- DEP-013: FR-015 (scope-protection against incidental Gap-6 resolution) bounds Clusters A through D specifically (FR-001 through FR-008).

**External and deferred constraints (per the FRA's own Section 24 scope protection, none pulled into this document's own scope):**
- P2-03 (Financial Ownership) - frozen reference baseline; Drawdown, Drawdown Ratio, Equity, Peak Equity, and Realized PnL's own ownership, formula, and input source are not reopened by any dependency recorded in this document.
- P2-02A (Position Ownership) - frozen reference baseline; Position and Position-derived Exposure's own ownership and formula are not reopened; only RiskEngine's already-certified consumption of the resulting value (FR-006) is within this document's scope.
- P3-03 (Performance Validation) - external boundary constraint for Cluster I's FR-015 (Section 16, OQ-005); whatever Cluster D eventually resolves must not incidentally determine `PerformanceEngine`'s Risk-Metric consumption boundary.
- TD-005 (Automated Regression Test Suite) - deferred, project-wide; unrelated to this analysis's dependency structure.
- TD-002, TD-004, TD-007 - confirmed follow-on only (Section 17); no dependency record in this document targets them.
- Repository cleanup (`run_engine/runtime/risk.py`, `run_engine/core/position_sizing.py`, `run_engine/core/equity_stabilizer.py`) - deferred to Phase 6 Repository Consolidation; recorded as FRA findings only (its Section 4), not dependencies.

## 25. Dependency Findings

Each of the nine check categories named by the governing task is addressed explicitly below, grounded in the analysis performed in Sections 7 through 24.

**Cyclic dependencies.** None found. Section 19.1's topological trace of all five sequential (PREREQUISITE-type) edges terminates at FR-008, FR-013, and FR-003 without any edge returning to an earlier node. No CONSTRAINT-type edge participates in sequencing, so none can contribute to a cycle by construction.

**Implicit dependencies made explicit.** Three were identified and converted into explicit dependency records rather than left as unstated assumptions: (1) Clusters E, F, and G's "already satisfied" status implicitly depends on Clusters C and D's eventual implementation not regressing them - the FRA states each requirement's already-satisfied status independently, without cross-referencing that future work in `risk.py` could break it; this document makes the relationship explicit via DEP-009, DEP-010, DEP-011. (2) FR-013's reset-necessity determination implicitly depends on FR-010's own finding (that Risk Policy Configuration constants are never mutated); the FRA's own FR-013 text already cites this connection in its Existing Evidence field, and this document formalizes it as DEP-016. (3) FR-007's formula evaluation implicitly depends on FR-002's already-conformant Computational Authority not being disturbed by any revision considered; this document makes this explicit via DEP-015.

**Hidden coupling structures.** One was identified: FR-006 (Cluster C, RiskEngine read-only toward Position/Exposure) and FR-011 (Cluster F, RiskEngine read-only toward Equity/Peak-Equity/Position) overlap on the shared term "Position." Both requirements bound the same `RiskEngine.check()` parameter (`position`), from different value-scope angles. This is not duplication - the FRA correctly assigns them distinct IDs covering distinct value sets - but it is a coupling point: any single future implementation change to how `RiskEngine.check()` handles its `position` parameter must satisfy both FR-006 and FR-011 simultaneously, a joint-verification obligation not stated explicitly by either requirement's own text in isolation. Recorded here as a finding, not resolved architecturally.

**Unnecessary dependencies avoided.** DEP-006 and DEP-007 (FR-007 to FR-001, FR-007 to FR-003) were explicitly tested against the Removal Test during drafting and found not to survive as HARD or CONDITIONAL: removing either does not make its target's resolution impossible or unverifiable, only potentially subject to a later editorial revision. Both are recorded as SOFT rather than omitted or inflated to a blocking status, consistent with this document's own Section 5 discipline that only Removal-Test-surviving relationships are catalogued as PREREQUISITE or CONSTRAINT edges of blocking strength.

**Missing dependencies checked and not found.** Two candidate edges were specifically tested and rejected: (1) a direct edge from Cluster A (FR-001) to Cluster B (FR-003) - both are ownership-naming questions but for different objects (input parameters versus output value); no FR-003 Validation Condition cites FR-001, and no FR-001 Validation Condition cites FR-003; rejected. (2) a direct edge from Cluster C (FR-005) to Cluster B (FR-003) - functional incorporation of `position_exposure` would change the formula's inputs, not `risk_allocation_factor`'s own identity or storage location, which FR-003 concerns; rejected, consistent with FR-003's own Scope Classification treating the naming question as independent of the formula's internal composition.

**Violations of ADRs.** None found among the sixteen catalogued dependencies. Every CONSTRAINT edge exists specifically to enforce, not circumvent, an ADR: DEP-003/DEP-010 enforce ADR-004's Position/Exposure ownership boundary; DEP-009 enforces AI-005/ADR-007's determinism requirement; DEP-011 enforces ADR-011's non-mutation requirement; DEP-001/DEP-002/DEP-015 enforce ADR-007's and ADR-006's already-settled ownership assignments against silent relocation.

**Violations of Architecture Invariants.** None found. AI-002 ("Unique Ownership" - "Every runtime information object SHALL possess exactly one Authoritative Owner... Duplicate ownership is prohibited") is preserved, not threatened, by DEP-001 and DEP-002, which bind FR-003's naming decision to the already-single Authoritative Owner (`CanonicalState`) rather than permitting a second one. AI-013 (Architectural Minimality) was specifically checked against this document's own nine-cluster granularity: each cluster's Compression Test (Sections 7-15) independently justifies why it was not merged into an adjacent cluster; no cluster exists solely for documentary symmetry.

**Violations of Acceptance Criteria.** None found. AC-007 ("RiskEngine consumes only Canonical Working State... owns no canonical runtime information... remains deterministic") is directly enforced, not violated, by DEP-009, DEP-010, and DEP-011's constraint structure. AC-003 ("Separation of Ownership and Computation" - "Every runtime information object possesses exactly one Computational Authority") is likewise preserved: DEP-015 explicitly bounds Cluster D against introducing a second Computational Authority for `risk_allocation_factor`.

**Violations of the Runtime Ownership Matrix.** None found. The Matrix's general "Risk Metrics" row (Authoritative Owner `CanonicalState`, Computational Authority `RiskEngine`) is preserved as a constraint (DEP-001, DEP-002, DEP-015), never relocated, by every dependency recorded in this document.

## 26. Dependency Risks

- Resolving FR-008 (TD-006 closure) before FR-007 (formula evaluation) completes (violating DEP-005): risk of an unsupported or premature TD-006 closure claim, unable to cite an actual evaluation outcome.
- Finalizing FR-013's reset design before FR-001 is resolved (violating DEP-008): risk of designing reset semantics for a Risk Policy Configuration ownership model that is not the one eventually adopted.
- Expanding Cluster C's or Cluster D's resolution into Drawdown, Drawdown Ratio, Equity, or Peak Equity's own already-certified ownership, formula, or input source (violating DEP-012/Cluster I1): risk of reopening P2-03's certified work without justification.
- Resolving FR-015 by allowing `PerformanceEngine`'s Risk-Metric consumption boundary to be silently settled as an incidental side effect of Clusters A through D (violating DEP-013): risk of scope creep into P3-03's territory without an explicit governing decision.
- Treating FR-005's functional-incorporation option as automatically requiring FR-007's formula to become continuous rather than retaining a step function: conflates two independent formula-shape questions (input-set composition versus threshold-shape), risking an over-scoped Architecture-stage decision space not supported by any dependency this document records.
- Implementing FR-005 option (b) without immediately re-verifying FR-009, FR-010, and FR-011 (violating DEP-009/DEP-010): risk of silently regressing RiskEngine's already-certified statelessness and read-only-consumer properties.
- Treating P2-04 as requiring TD-006's Equity/Peak-Equity/Drawdown-input-source half (already resolved by P2-03) to be reopened: risk of duplicating certified P2-03 work, explicitly guarded against by DEP-012 and by TD-006's own Section 17 classification (already-resolved half excluded from this document's active targets).
- Treating Cluster A's FR-001 and Cluster B's FR-003 as requiring Cluster D's FR-007 to complete first (over-applying DEP-006/DEP-007's SOFT status as if it were HARD): risk of unnecessarily delaying two independently-resolvable naming questions behind a formula evaluation neither strictly requires.

## 27. Scientific Dependency Conclusions

Sixteen internal or external-facing dependencies were identified and assigned stable IDs (P2-04-DEP-001 through P2-04-DEP-016). No dependency cycle exists among the sequential (non-constraint) edges (Section 19.1). Ten of the fifteen FRA functional requirements (FR-002, FR-004's storage-location half, FR-006, FR-009, FR-010, FR-011, FR-012, and the compatibility half of FR-014/FR-015) function as a fixed reference frame or cross-cutting constraint layer rather than as pending sequential work. The remaining genuinely open work is concentrated in two small clusters (C's FR-005, D's FR-007/FR-008) connected by exactly one CONDITIONAL edge scoped to a single dimension (DEP-004), plus two narrower, largely independent naming questions (A's FR-001, B's FR-003, each only softly and informationally touched by Cluster D), plus one small, conditionally-gated terminal question (H's FR-013). This is a materially different shape from both P2-02A's two-independent-tracks structure and P2-03's single-dominant-cluster structure (Section 4, Section 22). Of the seven FRA Open Questions, none is classified BLOCKING; four (OQ-001, OQ-002, OQ-003, OQ-005) are classified CONDITIONALLY BLOCKING with precisely scoped blocking effects limited to implementation-detail or scope-boundary questions; three (OQ-004, OQ-006, OQ-007) are classified NON-BLOCKING. All fifteen FRA functional requirements (P2-04-FR-001 through P2-04-FR-015) are referenced by at least one cluster's dependency analysis (Sections 7 through 15) or dependency record (Section 18).

## 28. Readiness for Capability Gap Analysis

This analysis identified no scientific ambiguity that blocks proceeding to a Capability Gap Analysis. Every dependency recorded here traces directly to an FRA requirement, an ADR, an Architecture Invariant, a Rule, or the already-logged TD-006; no new scientific claim, formula, or ownership assignment is introduced. The absence of any BLOCKING Open Question (Section 16) and the two-small-clusters-with-a-narrow-bridge structure (Section 22) mean a Capability Gap Analysis can proceed directly to examining, requirement by requirement, exactly which files and code paths require change once the still-open implementation-detail questions (OQ-001, OQ-002, OQ-003, OQ-005) are eventually resolved, using the Dependency Layers (Section 23) as its ordering reference and the Dependency Graph (Section 19) as its blocking reference.

Readiness: READY. This document is sufficient to proceed to the P2-04 Capability Gap Analysis. No further scientific dependency investigation is required before that step.

## 29. Internal Consistency Review

### 29.1 Scientific Consistency Review

Every scientific term used in this document ("Risk Metric," "Risk Policy Configuration," "Risk-Limiting Formula," "Position-Derived Exposure," "RiskEngine Determinism") is used exactly as defined in the FRA's own Section 5, never redefined here. No dependency record introduces a new scientific claim, formula, or numeric value; every claim traces to an FRA requirement, an ADR/Invariant/Rule/Acceptance-Criterion quotation, or the Technical Debt Register. PREREQUISITE and CONSTRAINT are used with the precise, distinct meanings Section 5 establishes throughout Sections 7 through 24, never interchangeably; every CONSTRAINT edge is sourced from an already-conformant requirement (FR-002, FR-004's storage-location half, FR-006, FR-009, FR-010, FR-011, FR-012, FR-014, FR-015) and every PREREQUISITE edge is sourced from a still-open requirement (FR-001, FR-005, FR-007). Status: PASS.

### 29.2 Architecture Integrity Review

Every dependency record's Related ADR/Invariant/Rule field was checked against the actual text of `RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md` rather than assumed: ADR-004, ADR-006, ADR-007, ADR-011, Rule OM-002, Rule OM-006, Rule OM-007, AI-002, AI-005, AI-010, AI-013, AC-003, and AC-007 were each independently re-verified against their source text during drafting of Section 25 (one citation error, an incorrect "AI-001" attribution, was found and corrected to AI-002/AC-003 during this review pass itself, recorded transparently here rather than silently fixed). No dependency recorded in this document proposes relocating an Authoritative Owner or Computational Authority away from its currently-assigned component; every CONSTRAINT edge exists to preserve an existing assignment, never to change one. The Runtime Ownership Matrix's general "Risk Metrics" row is treated consistently throughout as the current, correct assignment for Drawdown, Drawdown Ratio, and `risk_allocation_factor`'s Authoritative Owner and Computational Authority, matching the FRA's own Section 9/Section 11 treatment exactly. Status: PASS (one error found and corrected during this review; see Section 30 for disposition).

### 29.3 Terminology Review

"Byte-identical" is not used anywhere in this document to describe a Python-object, runtime-dictionary, or numeric comparison (its only occurrence is this sentence's own meta-discussion of the term). "Byte-for-byte" appears once (Section 4), describing the direct re-read comparison of `risk.py`, `canonical_state.py`, and `loop.py` against the versions the FRA itself analyzed - a genuine source-file comparison, the same legitimate category the P2-02A Architecture document itself used the phrase for ("RiskEngine.check()'s Peak-Equity/Drawdown-related lines remain byte-for-byte unchanged"), not a Python-object, runtime-dictionary, or numeric-result comparison, so it does not fall under the reserved "functionally identical" register the FRA's own terminology rule governs. No comparison of Python objects, runtime dictionaries, or numeric results is described anywhere in this document, since this document performs dependency analysis, not runtime verification; the FRA's own terminology rule is therefore inherited but not itself invoked in that narrower sense. "BLOCKING," "CONDITIONALLY BLOCKING," "NON-BLOCKING," "DEFERRED," "PREREQUISITE," "CONSTRAINT," "HARD," "CONDITIONAL," and "SOFT" are each used with one fixed meaning, established in Section 5 and Section 16, throughout every subsequent section. "Cluster" always refers to one of the nine groupings defined in Section 6; no other grouping term is used interchangeably with it. Status: PASS.

### 29.4 Traceability Review

All fifteen FRA functional requirements are referenced by at least one cluster analysis (Sections 7 through 15) and by at least one dependency record (Section 18), cross-checked requirement by requirement: FR-001 in Sections 7, 18 (DEP-006, DEP-008); FR-002 in Sections 7, 18 (DEP-001, DEP-015); FR-003 in Sections 8, 18 (DEP-001, DEP-002, DEP-007); FR-004 in Sections 8, 18 (DEP-002); FR-005 in Sections 9, 18 (DEP-003, DEP-004, DEP-009, DEP-010, DEP-011); FR-006 in Sections 9, 18 (DEP-003); FR-007 in Sections 10, 18 (DEP-004, DEP-005, DEP-006, DEP-007, DEP-009, DEP-011, DEP-014, DEP-015); FR-008 in Sections 10, 18 (DEP-005, DEP-014); FR-009 in Sections 11, 18 (DEP-009); FR-010 in Sections 11, 18 (DEP-009, DEP-016); FR-011 in Sections 12, 18 (DEP-010); FR-012 in Sections 13, 18 (DEP-011); FR-013 in Sections 14, 18 (DEP-008, DEP-016); FR-014 in Sections 15, 18 (DEP-012); FR-015 in Sections 15, 18 (DEP-013). All seven FRA Open Questions are classified in Section 16, each with an explicit rating and rationale; none is left unclassified. All seven Technical Debt Register items are classified in Section 17; none is left unclassified. Dependency-ID uniqueness: P2-04-DEP-001 through P2-04-DEP-016 are each defined exactly once (Section 18) and referenced only by ID thereafter (Sections 19 through 27); no ID collision or reuse was introduced. Status: PASS.

### 29.5 Governance Review

No new functional requirement was created, removed, or modified; the fifteen FRA requirements (FR-001 through FR-015) are referenced exclusively by their existing IDs and existing text throughout this document, never restated with altered wording that would change their meaning. No architecture decision was made: every requirement's eventual resolution (interface shape, formula shape, storage mechanism, publication decision) is left explicitly open, consistent with Sections 7 through 15's own "this document does not decide" framing. No new ADR was introduced. No implementation was performed and no code file was modified (Section 4's re-verification confirms `run_engine/` unchanged throughout drafting). No Specification-level interface detail was proposed. No Capability Gap Analysis content (COMPLETE/PARTIAL/MISSING capability labeling, or file-by-file change enumeration) was introduced; Sections 7 through 26 consistently use dependency-relationship language only. Status: PASS.

## 30. Independent Self Verification

**Repository state, re-verified at the close of drafting, not assumed carried over from Section 4:** branch `run-engine-consolidation-safety`; HEAD `a81e1978cb07bbb26223c94a1b24e9220520c445`; `run_engine/` clean; no commit made during this document's drafting; no push made.

**Mechanical checks performed:** byte-level scan confirming zero non-ASCII bytes and zero lines with trailing whitespace across all 643 lines; `python -m compileall run_engine` re-run, PASS, confirming this documentation-only work produced zero runtime effect; a case-insensitive grep for `FR-[0-9]{3}` confirming all fifteen IDs FR-001 through FR-015 are each referenced multiple times (16 to 83 occurrences per ID, in both the fully-prefixed `P2-04-FR-XXX` form used in front matter and the bare `FR-XXX` form used throughout the cluster analyses and Dependency Catalogue, consistent with the FRA's own mixed-form citation style), none added, none removed, none renumbered relative to the FRA's own fifteen-requirement set; a grep for `P2-04-DEP-[0-9]{3}` confirming exactly sixteen unique dependency IDs, each defined exactly once (Section 18) and referenced only by ID thereafter.

**Citation accuracy check:** every ADR, Invariant, Rule, and Acceptance Criterion cited in this document (ADR-004, ADR-006, ADR-007, ADR-008, ADR-011, Rule OM-002, Rule OM-006, Rule OM-007, AI-002, AI-005, AI-010, AI-013, AC-003, AC-007) was checked against the Architecture Baseline's actual text during Section 29.2's Architecture Integrity Review; one error (an incorrect "AI-001" attribution for Computational-Authority uniqueness, which is properly AC-003, with AI-002 substituted as the correct Architecture-Invariant-level citation for ownership uniqueness) was found and corrected in place in Section 25 before this document's delivery, not left for a future reviewer to catch.

**Scope-boundary check:** re-read of Sections 2, 24, and 25 confirms no dependency record pulls P2-03 (Drawdown/Drawdown-Ratio/Equity/Peak-Equity ownership), P2-02A (Position/Exposure ownership), P3-03 (PerformanceEngine redesign), TD-005 (regression suite), or repository cleanup into this document's own analytical scope; each is recorded only as an external or deferred constraint (Section 24).

**Cross-document consistency check:** every FR-001 through FR-015 requirement statement paraphrased or quoted in this document (Sections 7 through 15, Section 18) was compared against the current, revised text of `P2_04_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-13.md` and found consistent, including the post-review corrections that document itself received (FR-004's Matrix-row-level qualifier, FR-009's "functionally identical" terminology, FR-011's unmutated phrasing) - this document was drafted after, and reflects, the FRA's own corrected state, not an earlier draft of it.

**Result:** all findings from this document's own internal reviews (Section 29) are either PASS or, in the one case where an error was found (Section 29.2), corrected within this same drafting pass and disclosed here rather than silently fixed. No open item remains for a future reviewer to independently re-check beyond the ordinary Architecture-stage decisions this document deliberately leaves open (Section 16, Section 28).

**Status: Independent Self Verification PASS.**

No commit was made. No runtime file was changed. No push was made. This document is ready to be provided as `P2_04_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-13.md`.
