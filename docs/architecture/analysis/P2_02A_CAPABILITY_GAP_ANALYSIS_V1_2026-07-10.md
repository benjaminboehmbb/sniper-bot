Document Class:
Capability Gap Analysis

Document ID:
P2-02A-CGA

Version:
V1.0

Status:
Draft for Internal Review

Date:
2026-07-10

Project:
Trading-Bot Scientific Runtime

Subsystem:
Run Engine

Primary Location:
docs/architecture/analysis/P2_02A_CAPABILITY_GAP_ANALYSIS_V1_2026-07-10.md

Depends On:
- docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md
- docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md
- ADR-004 (Position Represents Current Market Exposure), within the Architecture Baseline above
- docs/architecture/analysis/P2_02A_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-10.md
- docs/architecture/analysis/P2_02A_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-10.md
- docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md
- current runtime code at HEAD b88eae5

Referenced By:
- future P2-02A Architecture
- future P2-02A Specification
- future P2-02A Certification

---

# P2-02A Capability Gap Analysis

## 1. Purpose

This document performs the Capability Gap Analysis for P2-02A (Position Ownership), following directly from the Functional Requirement Analysis (Status: Internal Review PASS) and the Scientific Dependency Analysis (Status: Internal Review PASS, Readiness: READY).

This document determines, capability by capability, which scientific, architectural, implementation, and validation capabilities already exist, which exist only partially, and which are entirely missing. It designs no solution, selects no Exposure formula, decides no storage-versus-projection question, chooses no name, and specifies no interface. Its sole purpose is objective capability determination, repository-grounded in every case.

---

## 2. Scope

In scope: gap analysis of the seventeen capabilities listed in Section 7, each mapped onto the nine Scientific Dependency Analysis clusters (A through I) and the twenty Functional Requirement Analysis requirements (P2-02A-FR-001 through P2-02A-FR-020).

Out of scope: the same boundaries already established by the FRA (Section 20) and the SDA (Section 2) apply unchanged - full Financial Ownership Consolidation (P2-03), full Equity/Peak-Equity/Drawdown consolidation, general RiskEngine redesign, TD-006 beyond the Exposure-consumption boundary, the Lifecycle Control Surface (TD-007), the complete Tick-Complete Snapshot architecture, PositionSizingEngine activation without a compelling scientific reason, repository cleanup, and general test-suite implementation. No gap identified in these areas is treated as a P2-02A gap; each is recorded as external, deferred, or a future compatibility constraint, consistent with the SDA's own Section 25.

---

## 3. Binding Inputs

- docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md - ADR-004, the Runtime Ownership Matrix, Rules OM-001 through OM-009.
- docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md - the P2-02A unit definition.
- docs/architecture/analysis/P2_02A_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-10.md - twenty functional requirements, five Required Capabilities, six Open Questions, as edited and internally reviewed.
- docs/architecture/analysis/P2_02A_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-10.md - nine capability clusters, thirteen dependency records (P2-02A-DEP-001 through P2-02A-DEP-013), Open Question blocking classification, six Dependency Stages, as edited and internally reviewed.
- docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md - TD-001, TD-002, TD-003, TD-005, TD-006, TD-007.
- Current runtime code at HEAD b88eae5.

---

## 4. Verified Functional Baseline

Repository state re-verified for this analysis: branch run-engine-consolidation-safety, HEAD b88eae5, matching the FRA's and SDA's own verification exactly. run_engine/ and docs/architecture/ remain clean.

This analysis relies on the FRA's repository findings (Sections 4, 6, 7, 8) and the SDA's dependency findings (Sections 7 through 19) without re-deriving them from the code a second time; every capability's Existing Evidence entry below cites the FRA or SDA section that already established the underlying fact, rather than re-quoting source code.

---

## 5. Method

Each capability is evaluated across four dimensions, each independently assigned one of four statuses:

- COMPLETE - the capability, at this dimension, is fully established, correct, and requires no further work.
- PARTIAL - the capability, at this dimension, is established in part, or is fully established for a subset of its scope but not for the whole, or exists but does not yet conform to the target requirement.
- MISSING - the capability, at this dimension, does not exist at all.
- NOT APPLICABLE - the dimension cannot yet be meaningfully evaluated, because a hard prerequisite (per the SDA's Dependency Graph) at an earlier dimension or an earlier capability is itself MISSING, making the question premature rather than answerable.

The four dimensions are applied in the order Scientific, Architectural, Implementation, Validation, reflecting that each later dimension presupposes the one before it (a capability cannot be architected before its scientific basis exists, cannot be implemented before its architecture is decided, and cannot be validated before it is implemented). A NOT APPLICABLE at one dimension typically propagates NOT APPLICABLE to every dimension after it, unless repository evidence shows otherwise.

Each capability entry documents: Purpose, Current State, Existing Evidence, Missing Capability, Blocking Dependencies (SDA), Related FRA Requirements, Related Technical Debt, Scope Classification, and Readiness Assessment, followed by the four-dimension rating.

---

## 6. Capability Catalogue

| # | Capability | SDA Cluster | Primary FRA Requirements |
|---|---|---|---|
| 1 | Position Semantics | A | FR-001, FR-002, FR-009, FR-013 |
| 2 | Position Representation | A, D | FR-001, FR-003 |
| 3 | Position Ownership | D | FR-007, FR-008, FR-012, FR-020 |
| 4 | Position Publication | D | FR-020 |
| 5 | Canonical Position Shape | D | FR-003 |
| 6 | Position-derived Exposure | A, B, C | FR-001, FR-004 |
| 7 | Exposure Semantics | B | FR-004, FR-006 |
| 8 | Exposure Derivation | C | FR-004, FR-005, FR-015, FR-018 |
| 9 | Exposure Storage / Projection | C, D | FR-005, FR-007 |
| 10 | Runtime Consumer Access | F | FR-012, FR-016, FR-019 |
| 11 | Pre-Trade Snapshot | E | FR-012, FR-019 |
| 12 | Post-Trade Snapshot | D | FR-007, FR-020 |
| 13 | Canonical Read Path | D, E, F | FR-007, FR-008, FR-012 |
| 14 | RiskEngine Consumption | H | FR-010, FR-011 |
| 15 | Exposure Naming Separation | G | FR-005, FR-006 |
| 16 | Compatibility Constraints | I | FR-013, FR-014, FR-017, FR-019, FR-020 |
| 17 | Validation Infrastructure | (cross-cutting) | none direct |

---

## 7. Capability 1: Position Semantics

Purpose: the scientific definition of operative Position as containing at least Side, Quantity, Average Entry Price, and Current Exposure (FR-001), bounded against Trade History, Financial State, and Risk State.

Current State: three of the four tuple members (Side, Quantity, Average Entry Price) are fully defined and implemented; the fourth (Current Exposure) is entirely undefined and unimplemented, tracked separately as Capabilities 6 through 8.

Existing Evidence: FRA Section 6 confirms PositionEngine's five instance attributes (position, side, entry_price, quantity, last_price) and snapshot()'s five-key return value; FRA Section 6 confirms the boundary against Trade History (TradeLifecycleEngine holds no operational Position state) and against Financial/Risk State (PnLEngine, RiskEngine each own separate, already-certified domains, ADR-005 through ADR-007).

Missing Capability: only the Current Exposure member; the tuple's other three members and the boundary-drawing against adjacent domains are already complete.

Blocking Dependencies (SDA): P2-02A-DEP-001 (A to B, HARD), currently non-blocking since Cluster A is satisfied.

Related FRA Requirements: FR-001, FR-002, FR-009, FR-013, FR-014, FR-017.

Related Technical Debt: none directly attached to this capability.

Scope Classification: in scope (P2-02A).

Readiness Assessment: ready as far as this capability's own scope extends; the remaining gap belongs to Capabilities 6 through 8, not to this one.

- Scientific Capability: COMPLETE.
- Architectural Capability: COMPLETE.
- Implementation Capability: PARTIAL (three of four members implemented).
- Validation Capability: PARTIAL (three of four members validated across the P1-03/P1-03.1/P1-04 certification chain; the fourth member has nothing to validate yet).

---

## 8. Capability 2: Position Representation

Purpose: the concrete runtime data structure representing Position (PositionEngine's internal attributes, snapshot()'s dict shape, CanonicalState's position dict).

Current State: two physically distinct representations exist and are used concurrently: PositionEngine's live instance attributes (read directly by three consumers) and CanonicalState.state["position"] (the published representation). Under the current synchronous execution model the two do not diverge in value, only in which object is read and at what point in the tick.

Existing Evidence: FRA Section 6, direct code trace of RunLoop.step(): position_pre = self.position_engine.snapshot() versus self.enforcer.apply_position(position).

Missing Capability: a single, unified representation with no second physical read path; this is the TD-001 finding, addressed operationally by Capability 13 (Canonical Read Path).

Blocking Dependencies (SDA): P2-02A-DEP-005, P2-02A-DEP-006, P2-02A-DEP-007 (all HARD, gated by Cluster E's classification).

Related FRA Requirements: FR-001, FR-003, FR-008, FR-012.

Related Technical Debt: TD-001.

Scope Classification: in scope (P2-02A).

Readiness Assessment: blocked pending Cluster E's temporal/ownership classification (SDA Section 11); the representation itself (the dict shape) is not in question, only its singularity.

- Scientific Capability: COMPLETE (Rule OM-001 already specifies the requirement unambiguously).
- Architectural Capability: PARTIAL (functions today, does not yet conform to "exactly one canonical Position").
- Implementation Capability: PARTIAL (both physical representations are implemented and functioning; only their consolidation is missing).
- Validation Capability: PARTIAL (current, non-conformant behavior is fully validated; the target, conformant behavior has no validation yet, since it does not exist).

---

## 9. Capability 3: Position Ownership

Purpose: CanonicalState as Authoritative Owner and PositionEngine as Computational Authority for Position (ADR-004, Rule OM-001, Rule OM-002).

Current State: PositionEngine's Computational Authority role is fully conformant. CanonicalState's Authoritative Owner role is undermined in practice by the same dual-state pattern described in Capability 2: three consumers do not read Position through CanonicalState at all.

Existing Evidence: FRA Section 8 ownership table: "Authoritative Owner (actual): CanonicalState (post-tick) / PositionEngine (pre-tick, via position_pre) - dual-state."

Missing Capability: full, exclusive Authoritative Owner status for CanonicalState, i.e. no consumer that requires the authoritative value reading anything other than CanonicalState (directly or via an explicitly documented Derived View).

Blocking Dependencies (SDA): P2-02A-DEP-005 (E to D2, HARD).

Related FRA Requirements: FR-007, FR-008, FR-012, FR-020.

Related Technical Debt: TD-001, TD-003 (context for why the current pattern exists).

Scope Classification: in scope (P2-02A); this is the operational half of the unit's own stated objective ("Verify Position as the authoritative operational runtime entity").

Readiness Assessment: blocked pending Cluster E and Cluster D2 (SDA Sections 10, 11).

- Scientific Capability: COMPLETE.
- Architectural Capability: PARTIAL.
- Implementation Capability: PARTIAL.
- Validation Capability: MISSING (no test currently exists that checks "exactly one authoritative Position value per tick" across all consumers; the current absence of divergence is an artifact of the synchronous execution model, not a verified guarantee).

---

## 10. Capability 4: Position Publication

Purpose: CanonicalEnforcer.apply_position() as the sole Writer-on-Behalf-Of path publishing Position into CanonicalState (Rule OM-003).

Current State: fully implemented and already conformant; this is the one Position-related mechanism the FRA and SDA found to already fully satisfy ADR-004 without qualification.

Existing Evidence: FRA Section 6/8; the apply_position() pattern is identical in shape to the seven other CanonicalEnforcer methods already certified through P1-03.1 and P2-01.

Missing Capability: none.

Blocking Dependencies (SDA): none.

Related FRA Requirements: FR-020.

Related Technical Debt: none.

Scope Classification: in scope, already satisfied; no further P2-02A work required for this capability specifically.

Readiness Assessment: ready; already complete.

- Scientific Capability: COMPLETE.
- Architectural Capability: COMPLETE.
- Implementation Capability: COMPLETE.
- Validation Capability: COMPLETE (exercised across every certified P1-03.1/P1-04/P2-01 regression run).

---

## 11. Capability 5: Canonical Position Shape

Purpose: a single, consistent Position key-set at all times, including before the first tick (FR-003).

Current State: a confirmed shape mismatch exists: CanonicalState's default dict has three keys (position, entry_price, last_price); PositionEngine.snapshot()'s actual return value has five keys (position, side, entry_price, quantity, last_price). Any code reading CanonicalState.get()["position"] before the first step() call observes a dict missing side and quantity.

Existing Evidence: FRA Section 6, direct quotation of both dict literals.

Missing Capability: a corrected default dict matching the true five-key (or, once Exposure exists, six-key) shape; this is a narrow, well-understood defect, not an open scientific question.

Blocking Dependencies (SDA): none hard; this is Cluster D's D1 sub-problem, explicitly identified in SDA Section 10 as ungated and separable from D2.

Related FRA Requirements: FR-003.

Related Technical Debt: none currently logged; this is a newly confirmed finding from the FRA, not yet assigned its own Technical Debt Register entry.

Scope Classification: in scope (P2-02A); independently resolvable, does not require the Exposure track to be resolved first (though the final key count depends on Capability 9's storage-versus-projection outcome for Exposure specifically).

Readiness Assessment: ready; this is the one capability in the entire catalogue confirmed unblocked by any dependency, hard or conditional.

- Scientific Capability: COMPLETE (the requirement is a straightforward consistency constraint, not an open question).
- Architectural Capability: PARTIAL (the defect is understood, but the exact target shape depends in part on whether Exposure becomes a stored key, Capability 9).
- Implementation Capability: MISSING (the mismatch is a confirmed, unaddressed code defect).
- Validation Capability: MISSING (no test currently checks shape parity before versus after the first tick).

---

## 12. Capability 6: Position-derived Exposure

Purpose: Exposure as the fourth Position property required by ADR-004; the umbrella capability Gap 2 (FRA Section 9) addresses.

Current State: confirmed entirely absent from the runtime; no field named exposure exists anywhere inside PositionEngine or inside the Position representation.

Existing Evidence: FRA Section 7, direct code search: "No field named exposure exists anywhere inside PositionEngine or inside the Position representation."

Missing Capability: the entire capability, across all four dimensions; this is the deepest gap in the catalogue and the central objective of P2-02A's second gap.

Blocking Dependencies (SDA): P2-02A-DEP-001, P2-02A-DEP-002 (both HARD).

Related FRA Requirements: FR-001, FR-004, FR-005, FR-006, FR-010, FR-015, FR-018.

Related Technical Debt: none directly; this capability's absence is the reason P2-02A exists, not a logged debt item.

Scope Classification: in scope (P2-02A); this is the unit's primary objective.

Readiness Assessment: blocked on OQ-001 (BLOCKING per SDA Section 16); this capability cannot proceed until Capability 7 (Exposure Semantics) is resolved.

- Scientific Capability: MISSING.
- Architectural Capability: MISSING.
- Implementation Capability: MISSING.
- Validation Capability: MISSING.

---

## 13. Capability 7: Exposure Semantics

Purpose: the explicit scientific choice of which quantity Position-derived Exposure represents (market value, nominal exposure, committed capital, delta exposure, or another scientifically justified concept), its sign convention, its unit and dimension, and its value at FLAT (OQ-001).

Current State: no definition of any kind exists; this is the single open scientific question this entire governance chain has repeatedly identified as the critical path item.

Existing Evidence: FRA Section 23 (OQ-001, as edited); SDA Section 8 (Cluster B analysis) and Section 16 (BLOCKING classification, the only such classification among the six Open Questions).

Missing Capability: the semantic definition itself. SDA Section 8 additionally notes that "delta exposure" is likely inapplicable (no options/derivatives model exists anywhere in the active runtime) and that "risk exposure" risks reintroducing the naming collision (Capability 15) if chosen without care - these are constraints on the answer space, not answers.

Blocking Dependencies (SDA): this capability is itself the source of P2-02A-DEP-002 (to Capability 8), P2-02A-DEP-003 (to Capability 15), and transitively P2-02A-DEP-008 (to Capability 14); it has no dependency of its own beyond Capability 1 (satisfied).

Related FRA Requirements: FR-004, FR-006.

Related Technical Debt: none.

Scope Classification: in scope (P2-02A); this is the Architecture-stage decision this Capability Gap Analysis explicitly does not make.

Readiness Assessment: this is the critical-path gap; every capability downstream of it in the Exposure-Definition Track (Capabilities 8, 9, 15, and the Exposure half of 14) remains NOT APPLICABLE at every dimension until this is resolved.

- Scientific Capability: MISSING.
- Architectural Capability: NOT APPLICABLE (cannot be architected before the scientific question is answered).
- Implementation Capability: NOT APPLICABLE.
- Validation Capability: NOT APPLICABLE.

---

## 14. Capability 8: Exposure Derivation

Purpose: the deterministic, pure-function mapping from Position (and, where scientifically required, immutable instrument metadata) to the Exposure value Capability 7 defines (FR-004, FR-015, FR-018).

Current State: cannot exist independent of Capability 7; zero code exists in any form.

Existing Evidence: FRA Section 7 (no exposure computation of any kind exists in PositionEngine); SDA Section 9 (Cluster C analysis), SDA Section 4 (confirms no immutable instrument-metadata concept exists anywhere in the active runtime, relevant if Capability 7's answer requires it).

Missing Capability: the derivation function itself, and, contingently, an instrument-metadata capability that does not currently exist anywhere in run_engine (SDA Dependency P2-02A-DEP-013).

Blocking Dependencies (SDA): P2-02A-DEP-002 (HARD, from Capability 7); P2-02A-DEP-013 (CONDITIONAL, external, contingent entirely on Capability 7's outcome).

Related FRA Requirements: FR-004, FR-005, FR-015, FR-018.

Related Technical Debt: none.

Scope Classification: in scope (P2-02A), with one conditional external dependency (instrument metadata) that may fall outside P2-02A's currently understood file scope if triggered.

Readiness Assessment: blocked on Capability 7.

- Scientific Capability: MISSING (specific derivation cannot be scientifically grounded without Capability 7).
- Architectural Capability: NOT APPLICABLE.
- Implementation Capability: NOT APPLICABLE.
- Validation Capability: NOT APPLICABLE.

---

## 15. Capability 9: Exposure Storage / Projection

Purpose: the choice between storing Exposure as a canonical CanonicalState field or deriving it as a deterministic computed projection whenever required (OQ-006).

Current State: pure open question; no implementation exists in either form.

Existing Evidence: FRA Section 23 (OQ-006, as edited); SDA Section 9 (Cluster C, noting this is a conditional rather than hard internal dependency on the exact formula) and Section 16 (CONDITIONALLY BLOCKING classification).

Missing Capability: the decision itself; unlike Capability 7, this is explicitly an architecture/implementation trade-off, not a scientific definition question.

Blocking Dependencies (SDA): P2-02A-DEP-004 (CONDITIONAL, blocks only Capability 3's exposure-specific schema decision and Capability 5's final key count for Exposure); P2-02A-DEP-010 (SOFT, to Capability 15's naming target location).

Related FRA Requirements: FR-005, FR-007.

Related Technical Debt: none; relevant future compatibility constraint noted in SDA Section 25 toward ADR-010/Phase 3 Tick-Complete Snapshot serialization.

Scope Classification: in scope (P2-02A).

Readiness Assessment: conditionally blocked; per SDA Section 9, this does not need to wait for Capability 8's exact formula, only for Capability 7's semantic definition to exist conceptually.

- Scientific Capability: NOT APPLICABLE (a storage-versus-computation trade-off is not itself a scientific definition question).
- Architectural Capability: MISSING.
- Implementation Capability: MISSING.
- Validation Capability: MISSING.

---

## 16. Capability 10: Runtime Consumer Access

Purpose: the general pattern by which StrategySelector, Executor, PnLEngine, and RiskEngine access Position (Cluster F).

Current State: all four consumers function correctly today and are fully certified (P1-03, P1-03.1, P1-04); three of them (StrategySelector, Executor, PnLEngine's entry_basis) read PositionEngine.snapshot() directly rather than through CanonicalState; RiskEngine receives a position parameter it does not read at all.

Existing Evidence: FRA Section 6, direct call-site trace of all four consumers.

Missing Capability: a single, consolidated access pattern for the three non-RiskEngine consumers, and a functioning (currently unused) read for RiskEngine.

Blocking Dependencies (SDA): P2-02A-DEP-006, P2-02A-DEP-007 (both HARD, from Clusters E and D).

Related FRA Requirements: FR-012, FR-016, FR-019.

Related Technical Debt: TD-001.

Scope Classification: in scope (P2-02A).

Readiness Assessment: blocked pending Capability 3/11's resolution (Clusters D2 and E).

- Scientific Capability: COMPLETE (Rule OM-001 already specifies the target unambiguously).
- Architectural Capability: PARTIAL (functions today in a non-conformant shape).
- Implementation Capability: PARTIAL (fully implemented for current behavior; not implemented for the target, conformant behavior).
- Validation Capability: PARTIAL (current behavior fully validated across four certification cycles; target behavior has no validation, since it does not yet exist).

---

## 17. Capability 11: Pre-Trade Snapshot

Purpose: the pre-trade Position read (position_pre) consumed by StrategySelector, Executor, and PnLEngine's entry_basis input; the specific subject of Cluster E's classification question.

Current State: fully implemented, functioning, and certified (P1-03.1, P1-04); currently sourced from PositionEngine's raw instance attributes rather than from CanonicalState.

Existing Evidence: FRA Section 6; SDA Section 11, which additionally establishes that the underlying concept - "the previous tick's already-canonical Position, exposed under an explicit, documented name" - already satisfies the Architecture Baseline's own Derived View definition and Rule OM-001, once correctly re-sourced. SDA Section 11 also confirms, by direct citation, that none of this capability's three consumers ever reads or requires Exposure.

Missing Capability: only the re-sourcing (reading from CanonicalState's prior-tick value rather than from PositionEngine's live attributes); the conceptual classification work is, per the SDA's own analysis, already substantially complete.

Blocking Dependencies (SDA): none upstream; this capability requires only Capability 1 (satisfied). It is itself the source of P2-02A-DEP-005 and P2-02A-DEP-006 toward Capabilities 3 and 10.

Related FRA Requirements: FR-012, FR-019.

Related Technical Debt: TD-001, TD-003.

Scope Classification: in scope (P2-02A); explicitly independent of the Exposure track (SDA Section 11, Section 19).

Readiness Assessment: ready; of all capabilities gating other work, this one has the least remaining open question, since the SDA's Derived View reframing already resolves its central classification question in substance, leaving only its formal architectural ratification.

- Scientific Capability: COMPLETE.
- Architectural Capability: PARTIAL (the concept is sound; the source object is not yet conformant).
- Implementation Capability: PARTIAL. The current behaviour is fully implemented and validated; however, the target behaviour defined by the P2-02A architectural objective (canonical sourcing through the approved ownership model) is not yet implemented. Therefore the implementation status is PARTIAL.
- Validation Capability: COMPLETE (P1-03.1 entry-basis scenarios, P1-04 rejection scenarios, P2-01 regression, all already exercised and certified).

---

## 18. Capability 12: Post-Trade Snapshot

Purpose: the post-trade Position value, computed by update_post_trade() and published via apply_position().

Current State: fully implemented, correct, and already conformant to ADR-004; this is the already-satisfied half of Position ownership.

Existing Evidence: FRA Section 6, Section 8; matches the Runtime Ownership Matrix's Position row exactly.

Missing Capability: none.

Blocking Dependencies (SDA): none.

Related FRA Requirements: FR-007, FR-020.

Related Technical Debt: none.

Scope Classification: in scope, already satisfied.

Readiness Assessment: ready; already complete.

- Scientific Capability: COMPLETE.
- Architectural Capability: COMPLETE.
- Implementation Capability: COMPLETE.
- Validation Capability: COMPLETE.

---

## 19. Capability 13: Canonical Read Path

Purpose: the single, unified Position read path all required consumers use once Capabilities 3, 10, and 11 are resolved (the operational target of Cluster F, informed by Clusters D and E).

Current State: does not exist as a unified mechanism; multiple ad hoc access patterns currently coexist, per Capability 2 and Capability 10.

Existing Evidence: FRA Section 6 (four distinct consumer call sites, three of them non-conformant); SDA Sections 10 through 12.

Missing Capability: the unified mechanism itself, which cannot be designed by this document (that is an Architecture-stage decision), only recognized as absent.

Blocking Dependencies (SDA): P2-02A-DEP-005, P2-02A-DEP-006, P2-02A-DEP-007 (all HARD).

Related FRA Requirements: FR-007, FR-008, FR-012.

Related Technical Debt: TD-001.

Scope Classification: in scope (P2-02A); this is the operational convergence point of the Ownership-Consolidation Track.

Readiness Assessment: blocked pending Cluster E's classification and Cluster D2's mechanism.

- Scientific Capability: COMPLETE (Rule OM-001 already specifies the requirement).
- Architectural Capability: MISSING.
- Implementation Capability: MISSING.
- Validation Capability: MISSING.

---

## 20. Capability 14: RiskEngine Consumption

Purpose: RiskEngine as a strictly read-only consumer of Position-derived Exposure (FR-010, FR-011), using or replacing its existing, currently unused position parameter.

Current State: RiskEngine.check() already receives a position parameter at its call site, but its method body never reads it; no Exposure-consumption logic exists anywhere, since Exposure itself does not exist.

Existing Evidence: FRA Section 7, direct citation: "the method body never reads this parameter. It is accepted and silently discarded." SDA Section 14 (Cluster H analysis).

Missing Capability: the actual consumption logic; the parameter-passing wiring already exists and lowers the implementation burden once Capability 6 exists.

Blocking Dependencies (SDA): P2-02A-DEP-008 (HARD, from Capability 6/8); P2-02A-DEP-009 (CONDITIONAL, from Capability 10).

Related FRA Requirements: FR-010, FR-011.

Related Technical Debt: TD-006 (explicitly bounded out of this capability's scope; TD-006 concerns RiskEngine's separate Peak-Equity/Drawdown duplication, not Exposure consumption).

Scope Classification: in scope (P2-02A), narrowly - read-only consumption only, not RiskEngine's internal risk-limiting logic (P2-04's territory) and not TD-006.

Readiness Assessment: blocked on Capability 8 (hard) and conditionally on Capability 10.

- Scientific Capability: COMPLETE (ADR-004's verbatim text already specifies the requirement).
- Architectural Capability: PARTIAL (the parameter-passing wiring already exists; the consumption architecture does not).
- Implementation Capability: MISSING.
- Validation Capability: MISSING.

---

## 21. Capability 15: Exposure Naming Separation

Purpose: ensuring Position-derived Exposure never shares a field name, storage location, or computation with the existing RiskEngine risk-adjusted allocation value without an explicit, documented decision (FR-006, RC-3, OQ-002).

Current State: the anti-collision rule is established and already internally reviewed (FR-006); the concrete instantiation (the actual distinct name) cannot exist yet, since Position-derived Exposure itself does not exist.

Existing Evidence: FRA Section 7, direct confirmation that the collision is real: RiskEngine.check()'s allocation value and CanonicalState.state["exposure"] currently occupy the only meaning "exposure" has anywhere in the active runtime.

Missing Capability: the concrete name and storage location for Position-derived Exposure; the rule itself is not missing.

Blocking Dependencies (SDA): P2-02A-DEP-003 (SOFT, from Capability 7); P2-02A-DEP-010 (SOFT, from Capability 9).

Related FRA Requirements: FR-005, FR-006.

Related Technical Debt: none directly; adjacent to TD-006 only in the sense that both concern RiskEngine's existing allocation value, without overlapping in scope.

Scope Classification: in scope (P2-02A).

Readiness Assessment: the rule is ready and requires no further work; the instantiation is conditionally blocked on Capability 7 and, for its storage location, Capability 9.

- Scientific Capability: COMPLETE.
- Architectural Capability: PARTIAL (the rule is architecturally established; the concrete application is not).
- Implementation Capability: MISSING.
- Validation Capability: MISSING (though the collision risk itself - the fact that "exposure" is already claimed by RiskEngine's allocation value - is already confirmed and documented, which is the evidence this rule exists to act on).

---

## 22. Capability 16: Compatibility Constraints

Purpose: the frozen set of already-certified P1-03, P1-03.1, P1-04, and P2-01 contracts that constrain every other capability's eventual implementation (Cluster I).

Current State: fully certified, fully documented, and currently intact at HEAD b88eae5; re-verified as unaffected throughout this entire P2-02A governance chain to date (FRA, SDA, this document).

Existing Evidence: docs/architecture/certification/P1_04_FINAL_CERTIFICATION_V1_2026-07-09.md, docs/architecture/certification/P2_01_FINAL_CERTIFICATION_V1_2026-07-10.md; SDA Section 15.

Missing Capability: none; this capability's job is continuous verification, not construction.

Blocking Dependencies (SDA): P2-02A-DEP-011 (cross-cutting, applies identically to every other capability).

Related FRA Requirements: FR-013, FR-014, FR-017, FR-019, FR-020.

Related Technical Debt: none.

Scope Classification: in scope as a constraint layer; not a build target.

Readiness Assessment: ready; requires re-application at the conclusion of every other capability's resolution (SDA Dependency Stage 6), not new work now.

- Scientific Capability: COMPLETE.
- Architectural Capability: COMPLETE.
- Implementation Capability: COMPLETE.
- Validation Capability: COMPLETE.

---

## 23. Capability 17: Validation Infrastructure

Purpose: the ability to test and validate P2-02A's eventual implementation against the FRA's Section 19 validation conditions and the SDA's per-dependency validation conditions.

Current State: no automated regression suite exists anywhere in run_engine/core (TD-005); all validation across P1-03, P1-03.1, P1-04, P2-01, and P2-02 to date has been manual, interactive, ad hoc scripting, re-run once per governance cycle rather than persisted as a re-runnable suite.

Existing Evidence: FRA Section 4 ("No test coverage of run_engine/core exists anywhere in the repository, consistent with TD-005"); confirmed independently at every certification turn in this governance chain to date.

Missing Capability: an automated, persisted regression suite; explicitly a project-wide item (TD-005), not a P2-02A deliverable.

Blocking Dependencies (SDA): none; not modeled as a P2-02A dependency in the SDA, since every validation condition defined in the FRA and SDA is executable manually, exactly as every prior unit's validation was.

Related FRA Requirements: none direct; referenced contextually by every validation condition in FRA Section 19.

Related Technical Debt: TD-005.

Scope Classification: out of scope for P2-02A itself (project-wide); the manual validation methodology needed to certify P2-02A's eventual implementation is in scope and already proven sufficient by five prior units' precedent.

Readiness Assessment: ready, via manual methodology; the automated-suite gap is real but does not block P2-02A.

- Scientific Capability: COMPLETE (the validation methodology - which conditions must hold, how to check them - is already fully defined across the FRA and SDA).
- Architectural Capability: NOT APPLICABLE (no automated-suite architecture is in scope to evaluate).
- Implementation Capability: MISSING (TD-005, project-wide, explicitly out of scope for this unit).
- Validation Capability: NOT APPLICABLE (validating the validation infrastructure itself is out of scope).

---

## 24. Capability Gap Matrix

| Capability | Scientific | Architecture | Implementation | Validation | Overall Status | Priority | Blocking OQ | Target Future Phase |
|---|---|---|---|---|---|---|---|---|
| 1. Position Semantics | COMPLETE | COMPLETE | PARTIAL | PARTIAL | PARTIAL | Medium | none (self) | P2-02A |
| 2. Position Representation | COMPLETE | PARTIAL | PARTIAL | PARTIAL | PARTIAL | Low | OQ-003 | P2-02A |
| 3. Position Ownership | COMPLETE | PARTIAL | PARTIAL | MISSING | PARTIAL | High | OQ-003 | P2-02A |
| 4. Position Publication | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | N/A | none | already satisfied |
| 5. Canonical Position Shape | COMPLETE | PARTIAL | MISSING | MISSING | MISSING | Low | none (unblocked) | P2-02A |
| 6. Position-derived Exposure | MISSING | MISSING | MISSING | MISSING | MISSING | High | OQ-001 | P2-02A |
| 7. Exposure Semantics | MISSING | NOT APPLICABLE | NOT APPLICABLE | NOT APPLICABLE | MISSING | High | OQ-001 | P2-02A |
| 8. Exposure Derivation | MISSING | NOT APPLICABLE | NOT APPLICABLE | NOT APPLICABLE | MISSING | High | OQ-001 | P2-02A |
| 9. Exposure Storage / Projection | NOT APPLICABLE | MISSING | MISSING | MISSING | MISSING | Medium | OQ-006 | P2-02A |
| 10. Runtime Consumer Access | COMPLETE | PARTIAL | PARTIAL | PARTIAL | PARTIAL | High | OQ-003 | P2-02A |
| 11. Pre-Trade Snapshot | COMPLETE | PARTIAL | PARTIAL | COMPLETE | PARTIAL | Medium | OQ-003 (conceptually near-resolved) | P2-02A |
| 12. Post-Trade Snapshot | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | N/A | none | already satisfied |
| 13. Canonical Read Path | COMPLETE | MISSING | MISSING | MISSING | MISSING | High | OQ-003 | P2-02A |
| 14. RiskEngine Consumption | COMPLETE | PARTIAL | MISSING | MISSING | MISSING | High | OQ-001 (+ OQ-003 conditional) | P2-02A |
| 15. Exposure Naming Separation | COMPLETE | PARTIAL | MISSING | MISSING | PARTIAL | Medium | OQ-001, OQ-002, OQ-006 | P2-02A |
| 16. Compatibility Constraints | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | High (ongoing) | none | continuous |
| 17. Validation Infrastructure | COMPLETE | NOT APPLICABLE | MISSING | NOT APPLICABLE | NOT APPLICABLE (to P2-02A) | Low | none | Project-wide (TD-005) |

---

## 25. Priority Summary of Gaps

**High priority, currently blocked, on the critical path (Exposure-Definition Track):** Capabilities 6, 7, and 8 form a single blocked chain, all gated by OQ-001. No implementation-relevant work can begin on any of the three until the Architecture stage resolves Exposure's scientific definition.

**High priority, currently blocked, on the critical path (Ownership-Consolidation Track):** Capabilities 3, 10, and 13 form a second blocked chain, gated by Cluster E's temporal/ownership classification (OQ-003's conceptual half). Per Capability 11's finding, this classification is already substantially resolved in substance by the SDA's Derived View reframing; what remains is formal architectural ratification, not open investigation.

**High priority, convergence point:** Capability 14 (RiskEngine Consumption) requires both tracks' output and is therefore the last capability that can be resolved.

**Medium priority, narrower scope:** Capabilities 9 (Storage/Projection) and 15 (Naming Separation) are real gaps but each has a bounded, well-understood resolution space once Capability 7 is settled.

**Low priority, unblocked, independently resolvable now:** Capability 5 (Canonical Position Shape) is the only capability in the entire catalogue confirmed to have no blocking dependency of any kind; it could be resolved at the Architecture/Specification stage without waiting for any Open Question.

**Already satisfied, no gap:** Capabilities 4 (Position Publication), 12 (Post-Trade Snapshot), and 16 (Compatibility Constraints) require no further work, only continued non-regression.

**Explicitly out of P2-02A's own scope:** Capability 17 (Validation Infrastructure) is a confirmed, real gap (TD-005) but is project-wide and does not block this unit, consistent with every prior unit's precedent.

---

## 26. Readiness Assessment

Of seventeen capabilities: three are already fully satisfied (Capabilities 4, 12, 16); one is confirmed unblocked and independently resolvable (Capability 5); one is out of scope for this unit specifically (Capability 17), but is explicitly documented as a future architectural compatibility constraint through TD-005 and therefore intentionally preserved for later project-wide implementation; the remaining twelve are gapped to varying degrees, all traceable to one of the two tracks and one of the two primary blocking Open Questions (OQ-001, OQ-003) already characterized in full by the Scientific Dependency Analysis.

No capability was found in this analysis that was not already anticipated by the FRA's twenty requirements or the SDA's nine clusters and thirteen dependencies; this Capability Gap Analysis did not surface a new scientific question beyond what the SDA already identified, only localized each already-known gap to a specific, named capability with an explicit four-dimension status.

This document identifies gaps; it does not close them. The next document (P2-02A Architecture) must resolve OQ-001 (Exposure Semantics) and formally ratify Cluster E's Derived View classification (OQ-003's conceptual half) before Capabilities 6 through 9, 13, 14, and 15 can move beyond their current MISSING or PARTIAL status.

Readiness for Architecture stage: READY. This document is sufficient to proceed to the P2-02A Architecture document. No further capability investigation is required before that step.

---

## 27. Internal Consistency Review

Terminology consistency - COMPLETE, PARTIAL, MISSING, and NOT APPLICABLE are applied consistently across all seventeen capabilities per the definitions in Section 5; NOT APPLICABLE is used only where a hard upstream MISSING makes a dimension premature to evaluate (Capabilities 7, 8, 9, 17), never as a substitute for MISSING.

Scope consistency - no capability entry proposes a formula, a storage decision, a name, an interface, or a runtime design; every Missing Capability description states what is absent, not what should replace it. Section 2 confirms all P2-03/P2-04/TD-006/TD-007/repository-cleanup/test-suite topics remain external, deferred, or future-compatibility items, consistent with the FRA and SDA.

Traceability consistency - all seventeen capabilities map to at least one SDA cluster (Section 6) and at least one FRA requirement (Section 6, and individually in Sections 7 through 23); all thirteen SDA dependency IDs referenced (DEP-001 through DEP-013, plus the cross-cutting DEP-011) correspond exactly to their SDA definitions, with no new dependency invented by this document.

Open Question coverage - all six FRA Open Questions are referenced by at least one capability: OQ-001 by Capabilities 6, 7, 8, 14, 15; OQ-002 by Capability 15; OQ-003 by Capabilities 2, 3, 10, 11, 13, 14; OQ-004 by Capability 14 (as non-blocking, per SDA); OQ-005 is not referenced by any capability, consistent with its SDA classification as DEFERRED OUT OF SCOPE and its explicit exclusion from this analysis's Section 2; OQ-006 by Capabilities 8, 9, 15.

FRA requirement coverage - all twenty FRA functional requirements (P2-02A-FR-001 through P2-02A-FR-020) are referenced by at least one capability entry, cross-checked during drafting against Section 6's summary table and each capability's own Related FRA Requirements field.

Runtime-file consistency - no runtime file was read for new evidence beyond what the FRA and SDA already established; every Existing Evidence citation in Sections 7 through 23 points to a specific FRA or SDA section rather than re-deriving a claim independently, preventing drift between the three documents.

Status: Internal Consistency Review PASS.
