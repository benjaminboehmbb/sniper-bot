Document Class:
Scientific Dependency Analysis

Document ID:
P2-02A-SDA

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
docs/architecture/analysis/P2_02A_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-10.md

Depends On:
- docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md
- docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md
- docs/architecture/analysis/P2_02A_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-10.md
- ADR-004 (Position Represents Current Market Exposure), within the Architecture Baseline above
- docs/architecture/certification/P1_04_FINAL_CERTIFICATION_V1_2026-07-09.md
- docs/architecture/certification/P2_01_FINAL_CERTIFICATION_V1_2026-07-10.md
- docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md
- current runtime code at HEAD b88eae5

Referenced By:
- future P2-02A Capability Gap Analysis
- future P2-02A Architecture
- future P2-02A Specification
- future P2-02A Certification

---

# P2-02A Scientific Dependency Analysis

## 1. Purpose

This document performs the Scientific Dependency Analysis for P2-02A (Position Ownership), following directly from `P2_02A_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-10.md` (Status: Internal Review PASS, Functional Readiness: READY).

This document does not perform Capability Gap Analysis. It does not make architecture decisions. It does not select an Exposure formula. It does not finalize naming. It does not specify interfaces. It does not implement code. Its sole purpose is to determine the scientific, semantic, state-related, and architectural dependency structure among the twenty functional requirements (P2-02A-FR-001 through P2-02A-FR-020) and the nine capability clusters the task defines, and to derive the minimal prerequisite and the resulting ordering of future decisions.

---

## 2. Scope

In scope: dependency analysis of Position Semantics, Exposure Semantics, Exposure Derivation, Canonical Position Ownership, Pre-Trade/Post-Trade Position Semantics, Runtime Consumer Consolidation, Exposure Naming Separation, RiskEngine Consumption Boundary, and Compatibility/Invariants, as these relate to the twenty FRA functional requirements.

Out of scope: full Financial Ownership Consolidation (P2-03), full Equity/Peak-Equity/Drawdown consolidation, general RiskEngine redesign, TD-006 beyond the Exposure-consumption boundary, the Lifecycle Control Surface (TD-007), the complete Tick-Complete Snapshot architecture, activation of PositionSizingEngine without a compelling scientific reason, repository cleanup, and general test-suite implementation. Dependencies toward these topics are documented only as external dependency, deferred dependency, or future compatibility constraint (Section 25), never as part of the P2-02A scope itself.

---

## 3. Binding Inputs

- docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md - ADR-004, the Runtime Ownership Matrix, Rules OM-001 through OM-009, Architecture Invariants AI-001 through AI-015, and the "Derived View" definition ("A Derived View is reconstructed from authoritative runtime information. Derived Views possess no independent ownership. They may be regenerated at any time.").
- docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md - the P2-02A unit definition and Principle IP-002 (Single Logical Change; repository-wide modifications prohibited).
- docs/architecture/analysis/P2_02A_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-10.md - the twenty functional requirements, five Required Capabilities (RC-1 through RC-5), and six Open Questions (OQ-001 through OQ-006), all as edited and internally reviewed.
- docs/architecture/certification/P1_04_FINAL_CERTIFICATION_V1_2026-07-09.md and docs/architecture/certification/P2_01_FINAL_CERTIFICATION_V1_2026-07-10.md - the certified contract baseline this analysis treats as immutable (Cluster I).
- docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md - TD-001, TD-002, TD-003, TD-006, TD-007.
- Current runtime code at HEAD b88eae5, re-verified for this analysis where a new claim required it (Section 4).

---

## 4. Verified Functional Baseline

Repository state re-verified for this analysis: branch run-engine-consolidation-safety, HEAD b88eae5, matching the FRA's own verification exactly. run_engine/ and docs/architecture/ remain clean.

This analysis relies on the FRA's Section 4 through Section 8 findings without re-deriving them, and adds exactly one new repository-grounded fact required for Cluster C's dependency assessment (Section 9): a repository-wide search for instrument, multiplier, contract_size, tick_value, and symbol inside run_engine confirms that no immutable instrument-metadata concept exists anywhere in the active runtime (run_engine/core or run_engine/main.py). The single match found (run_engine/runtime/regime_execution_gate.py) is inside the already-confirmed-inactive run_engine/runtime/ package (FRA Section 4) and does not affect the active path. This fact is load-bearing for Dependency P2-02A-DEP-013 (Section 17).

---

## 5. Dependency Analysis Method

Each of the nine capability clusters (A through I, mapped one-to-one onto Sections 7 through 15) is analyzed using the following method, applied compactly per cluster rather than as fourteen separate subsections, to keep the analysis traceable without redundant restatement:

1. Capability Definition
2. Prerequisites, grouped as: Scientific, Semantic, State, Ownership, Information-Flow, Determinism, Compatibility
3. Dependent Capabilities (what this cluster unlocks)
4. Failure if Introduced Too Early (concrete failure mode from wrong ordering)
5. Necessity Tests: Minimality Assessment, Removal Test, Compression Test, Counterfactual Review, combined into one judgment per cluster

A dependency is recorded in the Dependency Graph (Section 17) only when it survives its own Removal Test (i.e., removing the source capability would make the target capability's correct resolution impossible or unverifiable, not merely inconvenient).

---

## 6. Capability Cluster Catalogue

| Cluster | Name | One-line definition | FRA Section mapping |
|---|---|---|---|
| A | Position Semantics | The scientific definition of operative Position (Side, Quantity, Average Entry Price, Current Exposure), bounded against Trade History, Financial State, Risk State | Section 6, FR-001, FR-002, FR-009, FR-013 |
| B | Exposure Semantics | The scientific meaning Position-derived Exposure represents | Section 7 (Gap 2), FR-004, FR-006; OQ-001 |
| C | Exposure Derivation | The deterministic, pure-function mapping from Position to the Exposure value defined by Cluster B | FR-004, FR-005, FR-015, FR-018; OQ-001, OQ-006 |
| D | Canonical Position Ownership | CanonicalState as Authoritative Owner, PositionEngine as Computational Authority, CanonicalEnforcer as Writer-on-Behalf-Of, consistent shape, exactly one authoritative value per tick | Section 6, 8; FR-003, FR-007, FR-008, FR-020; OQ-003, OQ-006 |
| E | Pre-Trade/Post-Trade Position Semantics | The temporal/ownership classification of the pre-trade Position snapshot (legitimate Derived View versus competing ownership) | Section 6 (TD-001), FR-012, FR-019; OQ-003 |
| F | Runtime Consumer Consolidation | Migrating every real Position consumer onto the single canonical read path | Section 6, FR-012, FR-016, FR-019 |
| G | Exposure Naming Separation | Ensuring Position-derived Exposure never shares a name, storage location, or computation with the existing RiskEngine allocation value without explicit decision | Section 7, FR-005, FR-006; OQ-002 |
| H | RiskEngine Consumption Boundary | RiskEngine as strict read-only consumer of Position-derived Exposure, scope-bounded against TD-006/P2-04 | Section 7, FR-010, FR-011; OQ-004 |
| I | Compatibility and Invariants | The frozen set of already-certified P1-03/P1-03.1/P1-04/P2-01 contracts constraining every other cluster | Section 6, FR-013, FR-014, FR-017, FR-019, FR-020 |

Cluster A and Cluster I are, per Section 7 and Section 15 below, already satisfied by prior certified work; they function as the fixed reference frame rather than as pending decisions.

---

## 7. Position Semantics Dependencies (Cluster A)

Capability Definition: Position is uniquely defined as containing at least Side, Quantity, Average Entry Price, and Current Exposure (FR-001), computed exclusively by PositionEngine (FR-002), and never carrying historical execution facts (FR-013), with TradeLifecycleEngine explicitly excluded from operational Position ownership (FR-009).

Prerequisites: Scientific and Semantic - none pending; ADR-004 already defines this tuple textually and Side/Quantity/Average Entry Price are already implemented exactly as required (FRA Section 6). State - PositionEngine's five-attribute model already exists, unchanged. Ownership - PositionEngine as Computational Authority is already conformant (FRA Section 8); CanonicalState as Authoritative Owner is only partially conformant due to Cluster D/E's dual-state finding, which is Cluster D/E's problem, not Cluster A's. Information-Flow - TradeLifecycleEngine.current_position() to PositionEngine.project()/update_post_trade() to snapshot() already exists and is already correct (certified P1-02/P1-03). Determinism - already satisfied (certified P1-03/P1-04). Compatibility - must not alter the already-certified Side/Quantity/Average-Entry-Price semantics or transition rules (FR-013, FR-014, FR-017).

Dependent Capabilities: Cluster B requires Cluster A to be a stable, defined tuple before Exposure can be defined as "a property of Position."

Failure if Introduced Too Early: not applicable in the ordinary sense, since Cluster A is not being introduced but re-verified. The relevant failure mode is scope drift: if FR-001's "at least" wording (already-approved editorial change) were misread as license to redefine Side, Quantity, or Average Entry Price themselves, rather than only to permit additional properties, this would violate FR-013/FR-014 and the P1-03/P1-04 certification chain.

Necessity Tests: Removal Test fails to remove Cluster A - without it, no other cluster has a defined entity to attach Exposure to, own canonically, or consolidate consumers around. Compression Test - Cluster A cannot be merged into another cluster without duplicating its definition everywhere it is referenced. Counterfactual Review - if Position Semantics were left implicit rather than explicit, Exposure risks being defined against an ambiguous notion of "position," which is exactly how Gap 2 (RiskEngine's independent exposure) originated historically. Conclusion: Cluster A is a necessary, already-satisfied prerequisite, not a pending decision.

---

## 8. Exposure Semantics Dependencies (Cluster B)

Capability Definition: The explicit scientific choice of which quantity Position-derived Exposure represents (for example market value, nominal exposure, committed capital, delta exposure, or another scientifically justified concept), including its sign/side convention, its unit and dimension, and its value at FLAT (OQ-001).

Prerequisites: Scientific - Cluster A must be stable (satisfied). Semantic - requires selecting among candidate concepts; "delta exposure" is flagged as likely inapplicable, since no options/derivatives greeks model exists anywhere in the active runtime (confirmed by the same repository search noted in Section 4); "risk exposure" is flagged as a name that, if chosen carelessly, would reintroduce the exact naming collision Cluster G exists to prevent, since it is also the informal name for RiskEngine's existing allocation value. State - none beyond Cluster A; assigning meaning is a specification act, not a state-dependent act. Ownership - none new; once defined, ownership follows automatically from ADR-004 (ready-established: CanonicalState owns, PositionEngine computes). Information-Flow - none new; depends only on which already-flowing Position fields the definition selects. Determinism - the semantic choice constrains what Cluster C may validly do (a definition that references RiskEngine state, e.g. "risk exposure" defined circularly on drawdown, would violate FR-004's exclusion). Compatibility - must not silently redefine "exposure" to mean what RiskEngine's allocation value currently means (FR-006/RC-3).

Dependent Capabilities: Cluster C (cannot select a derivation formula before knowing what the formula represents); Cluster D's exposure-specific schema decision (only knowable once B and OQ-006 are both settled); Cluster G's naming choice (benefits from, though does not strictly require, knowing the semantic identity); Cluster H (RiskEngine can only meaningfully consume a value once it is scientifically defined).

Failure if Introduced Too Early: if Cluster C's formula were selected before Cluster B's semantics, the formula might encode the wrong concept while appearing implementationally complete (for example, selecting entry_price as the basis would encode committed capital even if the intended concept was market value) - a silent semantic defect indistinguishable from a correct implementation until deliberately checked against the (still-undefined) semantic target. This is the single clearest instance in this analysis of a decision that must precede another decision (task item 2).

Necessity Tests: Minimality - Cluster B is not reducible to Cluster A (already satisfied) or to Cluster C (a different kind of question: what versus how). Removal Test fails to remove Cluster B - without it, Cluster C could still compute something, but FR-015 (pure function of a well-defined quantity) and FR-018 (well-defined at FLAT) could not be verified against any target, only asserted. Compression Test - merging B into C is rejected precisely because conflating "what it means" with "how to compute it" is the failure mode identified above. Counterfactual Review - without Cluster B, ADR-004 compliance for Exposure cannot be verified, only assumed; the requirement cannot be met without this capability. Conclusion: Cluster B is a hard, currently unresolved prerequisite for the Exposure-definition portion of P2-02A.

---

## 9. Exposure Derivation Dependencies (Cluster C)

Capability Definition: The deterministic, pure-function mapping from Position (and, where scientifically required, immutable instrument metadata) to the Exposure value defined by Cluster B (FR-004, FR-015, FR-018), including the storage-versus-projection decision (OQ-006).

Prerequisites: Scientific - Cluster B must be resolved first (hard). State - requires knowing whether Exposure will be a stored CanonicalState field or a computed projection (OQ-006); this decision can, in principle, be made independently of the exact formula (a projection or a stored value can both hold any formula's result), so this is a conditional rather than hard internal dependency, but does require Cluster B to exist at least conceptually so that "a well-defined derivable quantity" is known to exist. Ownership - none new once Cluster B is settled; Computational Authority remains PositionEngine, consistent with ADR-004. Information-Flow - must consume only already-available Position fields, plus optionally immutable instrument metadata; per Section 4, no such metadata concept exists anywhere in the active runtime today, so if Cluster B's semantic choice requires it (for example a contract multiplier for a nominal-exposure definition), a genuinely new capability must be built before Cluster C can be implemented (Dependency P2-02A-DEP-013, Section 17); if Cluster B's choice needs only Side, Quantity, Average Entry Price, or last_price, no new capability is required. Determinism - pure function requirement (FR-015); must not read Equity, Drawdown, Regime, or other RiskEngine-owned state (FR-004). Compatibility - must produce a well-defined, non-exceptional, non-NaN result at FLAT (Quantity 0.0) and at every other reachable Position state (FR-018).

Dependent Capabilities: Cluster D's exposure-specific schema decision; Cluster F (once a stable access pattern exists, whether stored-read or computed-call); Cluster G (once a concrete field or method exists, it needs a name distinct from RiskEngine's "exposure"); Cluster H (RiskEngine consumes whatever this produces).

Failure if Introduced Too Early: implementing Derivation before OQ-006 (storage versus projection) is decided risks moderate, not severe, rework - a pure function can be trivially wrapped into a cached/stored field later, or a stored field's write can be trivially replaced with a projection call later; this ordering constraint is soft/conditional, unlike the hard Cluster B to Cluster C ordering above.

Necessity Tests: Removal Test fails to remove Cluster C - ADR-004 requires Exposure to exist as a derived Position property; without a derivation, it cannot exist. Compression Test - Cluster C cannot be merged into Cluster B (semantics) without recreating the ordering failure mode above, nor into Cluster D (ownership) without blurring the Rule OM-002 distinction ("Computational Authority may differ from Authoritative Owner") the baseline already makes explicit. Counterfactual Review - the derivation could in principle be made arbitrarily simple (for example Exposure equals Quantity, a degenerate pure function satisfying FR-004/FR-015/FR-018 mechanically), but Cluster B's semantic-correctness requirement, not Cluster C's mechanics, is what would make such a degenerate choice wrong or right; the capability itself cannot be eliminated, only made trivial. Conclusion: Cluster C is a hard, currently unresolved prerequisite, itself gated by Cluster B.

---

## 10. Canonical Ownership Dependencies (Cluster D)

Capability Definition: CanonicalState as Authoritative Owner of the complete canonical Position including its derived Exposure once defined (FR-007); a consistent default and post-tick Position shape (FR-003); exactly one authoritative Position value per completed tick (FR-008); CanonicalEnforcer.apply_position() as the sole Writer-on-Behalf-Of path, unchanged (FR-020).

Prerequisites: this cluster splits into two internally separable sub-problems with different prerequisite structures.

Sub-problem D1 (shape parity, FR-003): Scientific/Semantic - none pending; this is a pure implementation-shape-consistency fix (three-key default versus five-key actual shape, FRA Section 6), independent of Exposure semantics or the dual-state question entirely. State/Ownership/Information-Flow/Determinism/Compatibility - all already satisfied or trivially achievable without any open decision.

Sub-problem D2 (dual-state consolidation mechanism, FR-008, FR-012, and the exposure-schema question tied to OQ-006): Scientific - requires Cluster E's temporal/ownership classification (legitimate Derived View versus competing ownership) to be resolved first; requires Cluster C's existence (at least conceptually) if Exposure is to be included in the canonical schema at all. Ownership - the central open question is TD-001/OQ-003, addressed jointly with Cluster E. Information-Flow - requires knowing, from Cluster F, which consumers need pre-trade timing (PnLEngine's entry_basis) and which do not (StrategySelector, Executor), so that "exactly one authoritative value per tick" (FR-008) is reconciled with the certified need for a pre-trade view (FR-019) rather than contradicting it.

Dependent Capabilities: Cluster F (consumers can only be consolidated onto a canonical source once its shape and access mechanism are defined).

Failure if Introduced Too Early: attempting to resolve D2 before Cluster E's classification question would risk "fixing" TD-001 by routing PnLEngine's entry_basis through a post-trade-only CanonicalState read, silently breaking the certified pre-trade timing contract (FR-019, TD-003) and corrupting realized PnL for Scale-In scenarios exactly like the ones certified in P1-03.1.

Necessity Tests: Removal Test fails to remove Cluster D - even with A, B, C fully resolved, ADR-004's Acceptance Criterion "CanonicalState contains the authoritative operational Position" remains formally unmet without it, since B/C define what Exposure is and how to compute it, not where it canonically lives. Compression Test - D1 and D2 are legitimately separable (D1 requires no open decision and could proceed immediately; D2 is decision-gated), so treating Cluster D as a single monolithic unit would overstate its blocking character; this document treats them as one cluster per the requested structure but records the internal split explicitly. Counterfactual Review - without Cluster D, Clusters B/C's work would have no canonical home, and Cluster A's already-certified Computational Authority (PositionEngine) would have no correspondingly complete Authoritative Owner, violating Rule OM-001. Conclusion: Cluster D is necessary; its D1 sub-problem is unblocked, its D2 sub-problem is hard-gated by Cluster E and soft-gated by Clusters B/C/OQ-006.

---

## 11. Pre-Trade/Post-Trade Temporal Dependencies (Cluster E)

Capability Definition: The scientific classification of the pre-trade Position snapshot (currently PositionEngine.snapshot(), read directly by StrategySelector, Executor, and PnLEngine's entry_basis input) as either a legitimate, explicitly documented temporal projection of the single canonical Position, or an actual second, competing ownership path (TD-001, OQ-003).

Prerequisites: Scientific - requires Cluster A (satisfied); does not require Cluster B or Cluster C at all. This is a directly verifiable, repository-grounded fact: PnLEngine's entry_basis input (position_pre["entry_price"]) only ever reads entry_price, never exposure (FRA Section 6); StrategySelector and Executor only ever read position.get("position", "FLAT") (FRA Section 6); none of the three consumers that motivate Cluster E reads or requires an Exposure value in any form. Cluster E is therefore scientifically independent of the entire Exposure track (Clusters B, C, G, H). Semantic - the key question is whether a pre-trade read, defined as "the previous tick's already-canonical Position, exposed under an explicit, documented name," satisfies Rule OM-001 ("exactly one Authoritative Owner") and the Architecture Baseline's own "Derived View" definition ("reconstructed from authoritative runtime information... possess no independent ownership... may be regenerated at any time"). Under that definition, a documented temporal view is compliant; what makes the current implementation non-compliant is not the existence of a pre-trade read, but that the pre-trade read is currently sourced from PositionEngine's raw, independently mutable instance attributes, a second physical object, rather than from the single canonical source. State - none new. Ownership - tightly coupled to Cluster D's D2 sub-problem (Section 10); this is the same underlying question viewed from the temporal-semantics side rather than the storage side. Information-Flow - PnLEngine's entry_basis must remain available with pre-trade timing (FR-019); this is a hard, already-certified compatibility constraint (P1-03.1), not open for renegotiation without formal re-certification. Determinism - unaffected either way; under the current synchronous execution model, no numeric divergence exists between the two read paths today (FRA Section 6). Compatibility - FR-019, TD-003.

Dependent Capabilities: Cluster D's D2 sub-problem; Cluster F, which operationalizes whatever Cluster E concludes across every consumer.

Failure if Introduced Too Early: not applicable to Cluster E itself (it is the gating analysis, not something gated); the relevant risk is the inverse - proceeding to Cluster F or D2 without first resolving Cluster E's classification question (see Section 10's Failure if Introduced Too Early).

Necessity Tests: Removal Test fails to remove Cluster E - without resolving whether the pre-trade read is a legitimate projection or a competing owner, any attempt to consolidate consumers (Cluster F) or finalize canonical ownership (Cluster D2) risks either breaking the certified entry_basis contract or leaving TD-001 formally unresolved. Compression Test - Cluster E is tightly coupled to Cluster D but is not identical to it: D concerns the canonical store's shape and schema in general (including Exposure); E concerns specifically the temporal legitimacy question for the already-certified pre-trade use case. The two are recorded as a hard cross-dependency (Section 17) rather than merged, since Cluster E's conclusion is a precondition for Cluster D2's specific mechanism, not a restatement of it. Counterfactual Review - if Cluster E were skipped and TD-001 were "resolved" purely at the implementation level (for example, simply deleting the pre-trade read), the certified entry_basis contract (P1-03.1, ratified P1-04) would break; the requirement cannot be met by skipping this capability. Conclusion: Cluster E is a hard, currently unresolved prerequisite, but is entirely independent of the Exposure track (Clusters B, C, G, H) and may be resolved in parallel with it.

---

## 12. Runtime Consumer Dependencies (Cluster F)

Capability Definition: Migrating every real consumer of Position - StrategySelector, Executor, PnLEngine's entry-basis input, and RiskEngine - onto the single canonical read path established by Clusters D and E, replacing the current direct reads of PositionEngine's live instance state, while preserving every certified behavior (FR-012, FR-016, FR-019).

Prerequisites: Scientific - requires Cluster D (what the canonical source and shape are) and Cluster E (how pre-trade timing is legitimately handled) to both be conceptually resolved first, for the three non-RiskEngine consumers (StrategySelector, Executor, PnLEngine). For RiskEngine specifically, consolidating its read path (fixing its ownership/sourcing) is independent of Exposure, but RiskEngine consuming a meaningful Exposure value (as opposed to merely a correctly-sourced Position) additionally requires Cluster C (Section 14). Semantic/State - none beyond what Clusters D/E already establish. Ownership - none new; each consumer's own Computational Authority (StrategySelector for weights/decision, Executor for execution, PnLEngine for pnl, RiskEngine for risk metrics) is unchanged; only the source of the Position input each already receives changes. Information-Flow - must preserve the exact temporal semantics per consumer (pre-trade for StrategySelector/Executor/PnLEngine's entry_basis, per FR-012/FR-019), even while changing the source object - exactly what Cluster E's Derived View reframing is intended to make possible without contradiction. Determinism - re-sourcing must not introduce a new ordering dependency (FR-016). Compatibility - FR-012, FR-017, FR-019.

Dependent Capabilities: Cluster G and Cluster H can proceed in parallel once Cluster F's general read-path pattern is settled for the non-RiskEngine consumers; Cluster H specifically has a conditional dependency on Cluster F's pattern being available so that RiskEngine does not become a new instance of the dual-state problem while being wired to consume Exposure.

Failure if Introduced Too Early: consolidating consumer read paths before Clusters D/E are resolved risks locking in an incorrect or premature canonical-access pattern that then requires rework once D/E's conclusions are finalized; consolidating RiskEngine's read path in a way that assumes an Exposure value before Cluster C produces one risks feeding it a placeholder, reproducing the exact "independent value" pattern this unit exists to eliminate.

Necessity Tests: Removal Test fails to remove Cluster F - without it, TD-001 remains unresolved and FR-008/FR-012 remain unmet regardless of how well Clusters A through E are resolved conceptually; F is the necessary operationalization step. Compression Test - Cluster F cannot be compressed into Cluster D, since D concerns the canonical store itself while F concerns every individual consumer's read site, a distinct (though dependent) unit of work potentially spanning several small, individually-scoped edits consistent with Principle IP-002. Counterfactual Review - without Cluster F, Clusters D and E's conclusions would remain purely conceptual, with no consumer actually benefiting from them; the overall requirement (Rule OM-001, exactly one canonical Position) cannot be met without this capability. Conclusion: Cluster F is a hard, currently unresolved prerequisite, hard-gated by D and E for its non-RiskEngine scope, and conditionally gated by Cluster C for its RiskEngine-Exposure scope specifically.

---

## 13. Naming and Schema Dependencies (Cluster G)

Capability Definition: The explicit, permanent rule (already established by FR-006/RC-3) that Position-derived Exposure and the existing RiskEngine risk-adjusted allocation value must never share a field name, storage location, or computation without an explicit, documented architectural decision, plus the eventual concrete instantiation of that rule (OQ-002).

Prerequisites: Scientific/Semantic - the rule itself requires no prerequisite; it is already fully specified by the FRA and can be treated as established immediately. Its concrete instantiation (the actual chosen name) benefits from, but does not strictly require, Cluster B's semantic definition (a well-informed name is more useful, but the anti-collision constraint itself is unconditionally already true). State - depends on OQ-006 (Cluster C): if Exposure is stored, the naming applies to a CanonicalState key; if it remains a computed projection, the naming applies to a method or property instead; either way a distinct name is required, only its application point differs. Ownership/Information-Flow/Determinism - none. Compatibility - must not repurpose or silently redefine the existing RiskEngine allocation field's current meaning or behavior; that field's own eventual disposition (rename, retain, or restructure) is not decided by this rule, only its distinctness from Position-derived Exposure is (RiskEngine's own logic remains out of scope, per Section 25's TD-006 boundary).

Dependent Capabilities: none further within P2-02A.

Failure if Introduced Too Early: choosing a concrete name before Cluster B's semantics are resolved risks a name that does not semantically fit the eventually-chosen definition (for example naming a field "market_exposure" but then defining it as committed capital), requiring a rename and re-touching every consumer and document reference that has meanwhile come to depend on it.

Necessity Tests: Removal Test - the rule survives (fails to be removed) as necessary: without it, Gap 2 (FRA Section 9) remains formally unresolved even if Clusters B/C/D are fully implemented, since a shared name would perpetuate ambiguity for any future reader regardless of the underlying values being technically distinct. Compression Test - the rule could in principle be folded as an implicit constraint inside Clusters C or D's implementation rather than tracked separately; this document keeps it explicit because it is a naming/communication concern distinct from computation (Cluster C) or ownership (Cluster D), and because the FRA itself already isolates it as FR-006, a standalone requirement. Counterfactual Review - without an explicit separation rule, a future implementer could plausibly reuse the existing "exposure" key for Position-derived Exposure "for convenience," silently perpetuating the exact collision this analysis exists to resolve; the rule is not eliminable, though its concrete instantiation can be deferred. Conclusion: the rule itself is already established and non-blocking; its concrete instantiation is conditionally blocked on Cluster B and, for its storage location specifically, on OQ-006.

---

## 14. RiskEngine Boundary Dependencies (Cluster H)

Capability Definition: RiskEngine as a strictly read-only consumer of Position-derived Exposure once it exists (FR-010), acquiring no ownership of Position or Exposure (FR-011), using or explicitly replacing its existing, currently unused position parameter (OQ-004), with an explicit scope boundary against TD-006 and P2-04.

Prerequisites: Scientific - hard dependency on Cluster C actually producing a value; RiskEngine cannot consume "Position-derived Exposure" before that quantity exists in any form. This is one of the clearest hard, blocking dependencies in this analysis, and is additionally grounded directly in ADR-004's own verbatim text ("RiskEngine SHALL consume Position-derived Exposure"), not merely inferred. Semantic - RiskEngine does not need to fully understand or apply Cluster B's semantic justification within its own risk logic for P2-02A's own scope; P2-02A's obligation on RiskEngine is narrow (accept a correctly-sourced, read-only value; do not duplicate ownership), not to change RiskEngine's actual risk-limiting formulas to meaningfully use that value, which is P2-04's territory. State - RiskEngine.check() already receives a position parameter (FRA Section 7); the wiring already exists, which substantially lowers the implementation burden and makes OQ-004 (reuse versus redesign) a low-risk, non-blocking decision, since a working fallback (reuse the existing parameter) is already structurally available. Ownership - RiskEngine must not become an Authoritative Owner or Computational Authority for Position or Exposure (FR-011); this rule is already established by ADR-004, not newly created by this cluster, only verified. Information-Flow - Position, with Exposure, must reach RiskEngine.check() via the same consolidated read path Cluster F establishes for other consumers, to avoid RiskEngine becoming a new instance of the dual-state pattern elsewhere resolved. Determinism - trivially satisfied, since consumption is read-only. Compatibility - must not touch RiskEngine's existing Peak-Equity/Drawdown computation (TD-006), a hard scope boundary on which file lines Cluster H's implementation may touch, not a sequencing dependency.

Dependent Capabilities: none further within P2-02A.

Failure if Introduced Too Early: wiring RiskEngine's exposure-consumption before Cluster C produces a real, semantically-grounded value would force a placeholder or prematurely-guessed value into RiskEngine, reproducing exactly the "independent, non-Position-derived value" pattern (TD-006's own diagnosed shape) this unit exists to prevent, only relocated rather than resolved.

Necessity Tests: Removal Test fails to remove Cluster H - it is explicitly named, verbatim, in ADR-004's Decision text and Acceptance Criteria, not merely inferred by this analysis; without it, ADR-004 compliance cannot be claimed even if every other cluster is resolved. Compression Test - Cluster H cannot be compressed into Cluster F, since F concerns correctly sourcing Position for every consumer (a Cluster A/D/E-dependent concern), while H concerns RiskEngine specifically and additionally consuming Exposure meaningfully (a Cluster C-dependent concern) - the two clusters share a consumer but not a dependency structure. Counterfactual Review - without Cluster H, TD-006's already-diagnosed pattern (RiskEngine as an unauthorized Computational Authority) would persist unaddressed for Exposure specifically, even after the Peak-Equity/Drawdown aspect is eventually resolved by P2-03/P2-04; the two are related but not substitutable for one another. Conclusion: Cluster H is a hard, currently unresolved prerequisite, gated by Cluster C (hard) and conditionally by Cluster F (soft).

---

## 15. Compatibility and Invariant Dependencies (Cluster I)

Capability Definition: The complete, already-certified set of P1-03, P1-03.1, P1-04, and P2-01 contracts - RuntimeFailureEvent determinism, rejection non-mutation of Position's Side/Quantity/Average Entry Price, Scale-In weighted-average entry price, Partial Close semantics, Full Close semantics, mark-price-on-rejection policy, and entry_basis timing - that constrain every other cluster's implementation without being a capability to be newly built.

Prerequisites: Scientific - requires the already-completed P1-03/P1-03.1/P1-04/P2-01 certification chain to exist as the frozen reference baseline; fully satisfied, verified present at HEAD b88eae5 (Section 4).

Dependent Capabilities: all of Clusters A through H are constrained by Cluster I; Cluster I does not depend on any of them, since it is a validation/constraint layer defined entirely by already-certified prior work, not a new build target with its own prerequisite chain.

Failure if Introduced Too Early: not applicable in the ordering sense (Cluster I is not sequenced, it is omnipresent); the relevant failure mode is omission - implementing any of Clusters A through H without explicitly checking against Cluster I's enumerated contracts risks a silent regression, for example accidentally altering Scale-In's weighted-average computation while restructuring Cluster D's schema.

Necessity Tests: Removal Test fails to remove Cluster I - without explicit tracking of these contracts, any implementation work in Clusters A through H risks silently violating certified behavior. Compression Test - Cluster I is deliberately kept as an explicit, cross-cutting section rather than distributed invisibly across Clusters A through H, so that each cluster's own Compatibility Prerequisites subsection (Sections 7 through 14) can reference it traceably instead of each cluster silently reinventing which contracts apply. Counterfactual Review - without Cluster I made explicit, the certified P1/P2 contract set would still exist as a fact, but would not be actively checked against during P2-02A's resolution, materially increasing regression risk. Conclusion: Cluster I is necessary as an explicit, non-sequential constraint layer, already fully satisfied and requiring no new decision, only continuous verification.

---

## 16. Open Question Classification

**OQ-001 - Scientific definition of Position-derived Exposure.**
Classification: BLOCKING.
Rationale: gates Cluster C entirely (Dependency DEP-002, hard), and transitively gates Cluster D's exposure-specific schema decision, the quality and validity of Cluster G's naming choice, and Cluster H's meaningful (as opposed to merely wired) consumption. Referenced requirements: FR-004, FR-005, FR-006, FR-010, FR-015, FR-018.

**OQ-002 - Naming and separation of the existing RiskEngine allocation value from Position-derived Exposure.**
Classification: CONDITIONALLY BLOCKING.
Rationale: the underlying rule (FR-006) is already established and blocks nothing; only the concrete name/location choice is blocked, and only on OQ-001 (soft dependency DEP-003) and, for its storage location specifically, on OQ-006. Referenced requirements: FR-005, FR-006.

**OQ-003 - Resolution mechanism for the TD-001 dual-state read pattern.**
Classification: CONDITIONALLY BLOCKING.
Rationale: blocks Cluster D's D2 sub-problem and Cluster F's consolidation of StrategySelector/Executor/PnLEngine specifically, but does not block Clusters A, B, C, G, or H, which proceed on an independent track. Referenced requirements: FR-007, FR-008, FR-012, FR-019.

**OQ-004 - Reuse or redesign of RiskEngine's existing, currently unused position parameter.**
Classification: NON-BLOCKING.
Rationale: a working, minimal-risk fallback (reuse the existing parameter) is already structurally present in the code (FRA Section 7); this question can be resolved at the Architecture/Specification stage without blocking any dependency-analysis conclusion in this document. Referenced requirements: FR-010.

**OQ-005 - Activation status of the currently inactive PositionSizingEngine.**
Classification: DEFERRED OUT OF SCOPE.
Rationale: explicitly excluded from P2-02A by the governing task's scope-protection list ("Aktivierung des PositionSizingEngine ohne zwingenden wissenschaftlichen Grund" is not to be pulled in); this analysis found no scientific necessity requiring its activation to resolve any of the twenty functional requirements. Not modeled as a graph dependency (Section 17).

**OQ-006 - Storage of Position-derived Exposure as a canonical field versus a deterministic computed projection.**
Classification: CONDITIONALLY BLOCKING.
Rationale: blocks Cluster D's exposure-specific schema decision (DEP-004) and Cluster G's naming target location (DEP-010), but does not block Cluster B's semantic definition or Cluster C's core pure-function property (FR-015), which are orthogonal to whether the result is subsequently cached or recomputed. Referenced requirements: FR-005, FR-007.

---

## 17. Dependency Graph

Directed dependencies among capability clusters, each with a stable ID. Cluster I is recorded separately (DEP-011) as a cross-cutting constraint applied identically to all other clusters, rather than as a sequential graph edge, and is excluded from the cycle check in Section 17.1 for that reason.

**P2-02A-DEP-001**
Source: A (Position Semantics). Target: B (Exposure Semantics).
Type: SCIENTIFIC. Strength: HARD.
Rationale: Exposure must attach to a stable, defined Position tuple.
Referenced FRA Requirements: FR-001, FR-004.
Blocking Effect: none currently; A is already satisfied.
Validation Condition: Position tuple (Side, Quantity, Average Entry Price) remains stable and certified.

**P2-02A-DEP-002**
Source: B (Exposure Semantics). Target: C (Exposure Derivation).
Type: SEMANTIC. Strength: HARD.
Rationale: a derivation formula cannot be correctly selected before the quantity it computes is scientifically defined; selecting the formula first risks encoding the wrong concept.
Referenced FRA Requirements: FR-004, FR-015, FR-018.
Blocking Effect: BLOCKING.
Validation Condition: a documented, approved semantic definition of Exposure exists before any derivation formula is finalized.

**P2-02A-DEP-003**
Source: B (Exposure Semantics). Target: G (Naming Separation).
Type: SEMANTIC. Strength: SOFT.
Rationale: a well-informed collision-free name benefits from knowing the semantic meaning; the anti-collision rule itself does not require it.
Referenced FRA Requirements: FR-006.
Blocking Effect: NON-BLOCKING for the rule; CONDITIONAL for the specific name choice.
Validation Condition: chosen name reflects the approved semantic definition without requiring later rework.

**P2-02A-DEP-004**
Source: C (Exposure Derivation) and OQ-006. Target: D (Canonical Ownership), D2 sub-problem.
Type: STATE. Strength: CONDITIONAL.
Rationale: whether CanonicalState needs a new key for Exposure, or no schema change at all, depends on the storage-versus-projection decision, which itself presupposes Cluster C's derivation existing at least conceptually.
Referenced FRA Requirements: FR-005, FR-007.
Blocking Effect: CONDITIONALLY BLOCKING for D2's exposure-specific schema decision only; D1 (shape parity) is unaffected.
Validation Condition: CanonicalState schema decision is documented and consistent with the OQ-006 resolution.

**P2-02A-DEP-005**
Source: E (Pre-Trade/Post-Trade Semantics). Target: D (Canonical Ownership), D2 sub-problem.
Type: OWNERSHIP. Strength: HARD.
Rationale: the classification of the pre-trade snapshot as legitimate Derived View versus competing ownership must precede finalizing the dual-state consolidation mechanism.
Referenced FRA Requirements: FR-008, FR-012, FR-019.
Blocking Effect: BLOCKING for D2; D1 unaffected.
Validation Condition: an explicit statement classifies the pre-trade read per the Architecture Baseline's Derived View definition, cross-referenced against Rule OM-001.

**P2-02A-DEP-006**
Source: E (Pre-Trade/Post-Trade Semantics). Target: F (Runtime Consumer Consolidation).
Type: TEMPORAL. Strength: HARD.
Rationale: consumers cannot be correctly re-sourced until the temporal classification is settled, or the certified entry_basis timing contract risks being broken.
Referenced FRA Requirements: FR-012, FR-019.
Blocking Effect: BLOCKING.
Validation Condition: re-run of the P1-03.1/P1-04 entry-basis and lifecycle scenarios after consolidation produces identical results.

**P2-02A-DEP-007**
Source: D (Canonical Ownership). Target: F (Runtime Consumer Consolidation).
Type: OWNERSHIP. Strength: HARD.
Rationale: consumers can only be consolidated onto "the single canonical source" once that source's shape and access mechanism are defined.
Referenced FRA Requirements: FR-007, FR-008, FR-012.
Blocking Effect: BLOCKING.
Validation Condition: exactly one Position read path exists per required consumer, traced to the canonical source defined by D.

**P2-02A-DEP-008**
Source: C (Exposure Derivation). Target: H (RiskEngine Boundary).
Type: SCIENTIFIC. Strength: HARD.
Rationale: RiskEngine cannot consume Position-derived Exposure before that value is defined and derivable; grounded directly in ADR-004's verbatim text.
Referenced FRA Requirements: FR-010.
Blocking Effect: BLOCKING.
Validation Condition: RiskEngine.check() reads a value traceable directly to Cluster C's derivation output.

**P2-02A-DEP-009**
Source: F (Runtime Consumer Consolidation). Target: H (RiskEngine Boundary).
Type: INFORMATION_FLOW. Strength: CONDITIONAL.
Rationale: RiskEngine's Position input should be sourced via the same consolidated read path established for other consumers to avoid becoming a new instance of the dual-state pattern; however RiskEngine's own read-path fix does not strictly require the other three consumers to be migrated first.
Referenced FRA Requirements: FR-008, FR-010, FR-012.
Blocking Effect: CONDITIONALLY BLOCKING.
Validation Condition: RiskEngine's position parameter traces to the same canonical source as every other consolidated consumer.

**P2-02A-DEP-010**
Source: G (Naming Separation) and OQ-006. Target: D (Canonical Ownership), D2 sub-problem.
Type: GOVERNANCE. Strength: SOFT.
Rationale: if Exposure is stored (OQ-006 resolves toward storage), the final CanonicalState key name must respect Cluster G's anti-collision rule.
Referenced FRA Requirements: FR-005, FR-006.
Blocking Effect: CONDITIONALLY BLOCKING, only if OQ-006 resolves toward storage.
Validation Condition: chosen CanonicalState key (if any) does not collide with the existing "exposure" field.

**P2-02A-DEP-011**
Source: I (Compatibility and Invariants). Target: A, B, C, D, E, F, G, H (all, cross-cutting).
Type: COMPATIBILITY. Strength: HARD.
Rationale: every cluster's resolution must preserve the enumerated P1-03/P1-03.1/P1-04/P2-01 contracts; this is a constraint applied at every node, not a sequencing gate.
Referenced FRA Requirements: FR-013, FR-014, FR-017, FR-019, FR-020.
Blocking Effect: BLOCKING as a constraint (violation invalidates the cluster's resolution), not as a scheduling delay.
Validation Condition: full regression re-run of P1-03/P1-03.1/P1-04/P2-01 certified scenarios after each cluster's resolution.

**P2-02A-DEP-012**
Source: H (RiskEngine Boundary). Target: external (TD-006 / P2-04 scope boundary).
Type: GOVERNANCE. Strength: HARD.
Rationale: Cluster H's implementation must not extend into RiskEngine's Peak-Equity/Drawdown logic; a scope boundary, not a sequencing dependency.
Referenced FRA Requirements: none direct (Section 20 scope boundary).
Blocking Effect: NON-BLOCKING to P2-02A's progress; constrains scope only.
Validation Condition: RiskEngine.check()'s Peak-Equity/Drawdown-related lines remain byte-for-byte unchanged after Cluster H's implementation, mirroring the non-regression validation pattern already used in the P2-01 governance chain.

**P2-02A-DEP-013**
Source: C (Exposure Derivation). Target: external (immutable instrument metadata capability, currently absent).
Type: STATE. Strength: CONDITIONAL.
Rationale: confirmed by repository search (Section 4) that no instrument-metadata concept exists anywhere in the active runtime; if Cluster B's semantic choice requires immutable instrument metadata not already available within the active runtime, an additional capability will be required before Exposure Derivation can be completed; if Cluster B's choice needs only already-available Position fields, this dependency resolves to none.
Referenced FRA Requirements: FR-004.
Blocking Effect: CONDITIONALLY BLOCKING, entirely contingent on Cluster B's outcome.
Validation Condition: Cluster B's semantic definition explicitly states whether instrument metadata is required; if yes, its source and storage location are identified before Cluster C proceeds.

### 17.1 Cycle Check

Topological trace of all internal (non-external, non-Cluster-I) edges: A to B to C to D to F to H; B to G to D; E to D to F; E to F (direct); C to H; F to H. No edge points from a later-reached node back to an earlier one (D never points to A, B, C, or E; F never points to D or E; H never points onward to any other cluster; G never points to A or B). No dependency cycle exists among Clusters A through H. Cluster I is excluded from this check by construction, since it is applied identically and non-sequentially to every node rather than participating in the ordering.

---

## 18. Dependency Matrix

Rows are source clusters, columns are target clusters. Cell values give the dependency ID and strength, or a dash where no dependency was found to survive its Removal Test. Cluster I applies identically to every column (see DEP-011) and is therefore given its own summary row rather than repeated in every cell.

| Source \ Target | A | B | C | D | E | F | G | H |
|---|---|---|---|---|---|---|---|---|
| A | - | DEP-001 (HARD) | - | - | - | - | - | - |
| B | - | - | DEP-002 (HARD) | - | - | - | DEP-003 (SOFT) | - |
| C | - | - | - | DEP-004 (CONDITIONAL) | - | - | - | DEP-008 (HARD) |
| D | - | - | - | - | - | DEP-007 (HARD) | - | - |
| E | - | - | - | DEP-005 (HARD) | - | DEP-006 (HARD) | - | - |
| F | - | - | - | - | - | - | - | DEP-009 (CONDITIONAL) |
| G | - | - | - | DEP-010 (SOFT) | - | - | - | - |
| H | - | - | - | - | - | - | - | - |
| I | DEP-011 | DEP-011 | DEP-011 | DEP-011 | DEP-011 | DEP-011 | DEP-011 | DEP-011 |

External-facing dependencies not represented in this square matrix: DEP-012 (H to TD-006/P2-04 boundary), DEP-013 (C to external instrument-metadata capability).

---

## 19. Minimal Prerequisite Capability Analysis

The hypothesis under test: the scientific and dimensional definition of Position-derived Exposure (Cluster B / OQ-001) is the minimal prerequisite without which neither Position schema, Exposure derivation, storage/projection, consumer contracts, nor the RiskEngine boundary can be correctly decided.

**Removal Test applied to the hypothesis.** If OQ-001 remains unresolved: Cluster C cannot proceed correctly (DEP-002, HARD) - confirmed. Cluster D's exposure-specific schema sub-decision cannot proceed (DEP-004, transitively through C) - confirmed. Cluster G's naming rule can still be established, though its concrete instantiation is degraded (DEP-003, SOFT) - partially confirmed. Cluster H cannot meaningfully consume Exposure (DEP-008, transitively through C) - confirmed. However: Cluster D's shape-parity sub-problem (D1, FR-003) proceeds unaffected - hypothesis does not hold here. Cluster E proceeds entirely unaffected, since none of its three motivating consumers (StrategySelector, Executor, PnLEngine's entry_basis) ever reads or requires Exposure (FRA Section 6, re-confirmed Section 11) - hypothesis does not hold here. Cluster F's consolidation of StrategySelector, Executor, and PnLEngine proceeds unaffected for the same reason - hypothesis does not hold here. Cluster I proceeds unaffected, being independent of all other clusters.

**Compression Test.** A more precisely scoped, still-accurate restatement of the hypothesis is available: OQ-001 is the minimal prerequisite for the Exposure-definition track of P2-02A's work (Cluster C in full, Cluster D's exposure-specific schema decision, Cluster G's naming target, and Cluster H), but is not a prerequisite for the ownership-consolidation track (Cluster E in full, Cluster F's non-RiskEngine consolidation, and Cluster D's shape-parity sub-problem), which is scientifically independent and can proceed in parallel.

**Counterfactual Review.** What happens if OQ-001 is never resolved: the Exposure-definition track cannot produce a scientifically defensible result (Section 9's Counterfactual Review); the ownership-consolidation track can still fully resolve TD-001 and consolidate three of the four real consumers, since it never touches Exposure. Can the problem be solved equally simply without this capability: no: there is no substitute for defining what a scientific quantity represents before computing it; this is a genuine, non-bypassable step for the Exposure track specifically. Does resolving OQ-001 create a new necessary capability, or only a different representation: it is a pure semantic/definitional decision, not a runtime capability by itself; Cluster C, built afterward, is the actual new runtime capability. Can the overall P2-02A requirement be met without this capability: no, not in full - Gap 2 (FRA Section 9) specifically requires it - but Gap 1 (TD-001) can be fully resolved without it.

**Alternative minimal-prerequisite candidates considered and rejected as the primary answer:**
- Cluster A (Position Semantics): already satisfied prior to this analysis, not a pending decision; necessary but not what remains missing.
- Cluster E's temporal classification: gates Cluster D2 and Cluster F, but does not gate Clusters B, C, G, or H at all; narrower in scope than the hypothesis claims for Cluster B.
- OQ-006 (storage versus projection): gates only Cluster D's schema and Cluster G's naming target, not Cluster B's core definition or Cluster C's pure-function property; narrower still.

**Conclusion.** The hypothesis is partially confirmed and requires an explicit correction, not an automatic confirmation. Position-derived Exposure's scientific and dimensional definition (OQ-001) is confirmed as the minimal prerequisite for the Exposure-definition track (Clusters B, C, G, H), directly answering task item 10: P2-02A does not reduce to one implementation unit, and does not reduce to a single minimal prerequisite either. It decomposes into two scientifically independent tracks - an Exposure-Definition Track gated by OQ-001, and an Ownership-Consolidation Track gated by Cluster E's temporal classification (OQ-003's conceptual half) - that only reconverge at Cluster H (which needs both) and at Cluster I's constant validation layer.

---

## 20. Alternative Dependency Structures

**Alternative structure 1: single linear chain (A - B - C - D - E - F - G - H).** Rejected. This structure is not supported by the evidence: Cluster E is demonstrably independent of B/C/G (Section 11), and forcing a linear order would delay the ownership-consolidation track behind the exposure-definition track without scientific justification, violating the instruction not to prescribe an order beyond what the dependency structure actually requires (task item 6).

**Alternative structure 2: fully parallel, no ordering constraints.** Rejected. This structure is contradicted by the multiple confirmed HARD dependencies (DEP-002, DEP-005, DEP-006, DEP-007, DEP-008), each independently justified by a concrete Failure if Introduced Too Early scenario (Sections 8 through 14). Some ordering is scientifically required, not merely a matter of implementation convenience.

**Alternative structure 3 (adopted): two-track structure converging at Cluster H and Cluster I.** Supported directly by the Dependency Graph (Section 17) and the Minimal Prerequisite Analysis (Section 19): an Exposure-Definition Track (A already satisfied, then B, then C, then G and the exposure-specific part of D, then H) and an Ownership-Consolidation Track (A already satisfied, then E, then the ownership-specific part of D and F), both constrained throughout by I, converging only at H (which requires both C and F's pattern) and at the final compatibility validation. This structure is adopted for Section 24's Dependency Stages.

---

## 21. Removal Test

Consolidated summary of the per-cluster Removal Test results from Sections 7 through 15: every cluster except A and I fails to be removed without leaving at least one FRA requirement unverifiable or ADR-004 non-conformant (Clusters B through H each individually confirmed necessary in their respective sections). Clusters A and I are necessary but already satisfied, not pending decisions. No cluster was found to be redundant or removable without loss of scientific or architectural correctness.

---

## 22. Compression Test

Consolidated summary: no pair of clusters was found fully compressible into one without recreating a documented Failure if Introduced Too Early scenario or blurring an already-established baseline distinction (Rule OM-002's Computational-Authority-versus-Ownership split, in particular, is what prevents compressing Cluster C into Cluster D, and Cluster B into Cluster C). One partial compression was identified and recorded rather than silently adopted: Cluster D's D1 (shape parity) and D2 (dual-state mechanism) sub-problems have materially different prerequisite structures and could be tracked as two units instead of one; this document retains them as a single cluster per the requested structure, with the internal split explicitly documented (Section 10).

---

## 23. Counterfactual Review

Consolidated summary: for every cluster B through H, the corresponding Counterfactual Review (Sections 8 through 14) found that skipping the capability either leaves a specific ADR-004 Acceptance Criterion unmet, leaves a specific FRA requirement unverifiable, or risks a concrete, previously-certified behavior regressing. No cluster was found to be eliminable in favor of an equally simple alternative solution; where a degenerate or trivial resolution is possible (for example Cluster C's derivation formula being maximally simple), the capability itself remains necessary, only its complexity is reduced.

---

## 24. Derived Dependency Stages

This ordering follows directly from the Dependency Graph (Section 17) and the two-track structure (Section 20, alternative 3). It states which capabilities must be decided or established at each stage and why; it does not prescribe code changes, file order, or interface shapes.

**Dependency Stage 1 - Foundational (already satisfied).**
Establish: nothing new; confirm Cluster A (Position Semantics) and Cluster I (Compatibility and Invariants) remain the fixed reference frame.
Why first: every other cluster's prerequisites cite one or both of these as already-satisfied preconditions.
Unlocks: both tracks in Stage 2.
FRA Requirements involved: FR-001, FR-002, FR-009, FR-013, FR-014, FR-017, FR-019, FR-020.

**Dependency Stage 2 - Parallel track entry.**
Establish: Cluster B's semantic definition of Position-derived Exposure (resolve OQ-001), on the Exposure-Definition Track; Cluster E's temporal/ownership classification of the pre-trade snapshot (resolve OQ-003's conceptual half), on the Ownership-Consolidation Track. Cluster D's D1 shape-parity sub-problem (FR-003) may also be resolved at this stage, since it is ungated.
Why first (within each track): Cluster C cannot begin without B (DEP-002); Cluster D2 and Cluster F cannot begin without E (DEP-005, DEP-006).
Unlocks: Cluster C in Stage 3 (Exposure track); Cluster D2 and Cluster F in Stage 3 (Ownership track).
FRA Requirements involved: FR-004 (semantic part), FR-006 (rule statement), FR-003, FR-008, FR-012, FR-019.

**Dependency Stage 3 - Track-specific construction.**
Establish, Exposure track: Cluster C's derivation approach, including, if required by the selected Exposure semantics, resolving OQ-006 (storage versus projection), and, if triggered, DEP-013's instrument-metadata question.
Establish, Ownership track: Cluster D2's dual-state consolidation mechanism.
Why first: Cluster G's naming target and Cluster H's meaningful consumption require Cluster C's output (DEP-002 to DEP-008 chain); Cluster F's consolidation requires Cluster D2's mechanism (DEP-007).
Unlocks: Cluster G and the RiskEngine-facing half of Cluster H (Exposure track); Cluster F (Ownership track).
FRA Requirements involved: FR-004, FR-005, FR-007, FR-008, FR-015, FR-018.

**Dependency Stage 4 - Consumer and naming consolidation.**
Establish, Exposure track: Cluster G's concrete naming instantiation (resolve OQ-002).
Establish, Ownership track: Cluster F's consolidation of StrategySelector, Executor, and PnLEngine's entry-basis input.
Why first: Cluster H's read-path pattern benefits from Cluster F's established pattern (DEP-009, conditional); Cluster G's name must exist before it can be referenced anywhere consumer-facing.
Unlocks: Cluster H, fully.
FRA Requirements involved: FR-006, FR-012, FR-016, FR-019.

**Dependency Stage 5 - Convergence.**
Establish: Cluster H, RiskEngine's read-only consumption of Position-derived Exposure, resolving OQ-004 (low-risk, reuse-favored).
Why first: requires both Cluster C's Exposure value (Stage 3) and Cluster F's consolidated read-path pattern (Stage 4).
Unlocks: nothing further within P2-02A; this is the last cluster-level decision.
FRA Requirements involved: FR-010, FR-011.

**Dependency Stage 6 - Final compatibility validation.**
Establish: nothing new; re-apply Cluster I's full constraint set across the entire resolved system.
Why last: only after every other cluster's decisions are finalized can the complete set of P1-03/P1-03.1/P1-04/P2-01 certified scenarios, plus the new FR-015/FR-016/FR-018 determinism and edge-case checks, be meaningfully re-verified end to end.
FRA Requirements involved: all twenty, with particular emphasis on FR-013, FR-014, FR-017, FR-019, FR-020.

---

## 25. External and Deferred Dependencies

Recorded as external dependency, deferred dependency, or future compatibility constraint only, per the governing scope protection; none of the following is pulled into P2-02A's own scope:

- TD-006 (RiskEngine Peak-Equity/Drawdown ownership duplication) - external dependency for Cluster H (DEP-012); Cluster H must coexist with TD-006 unresolved, touching no line of RiskEngine's drawdown logic.
- P2-03 (Financial Ownership Consolidation) - future compatibility constraint: whatever Clusters C and H produce must not conflict with P2-03's eventual Equity/PnL consolidation work, though no such conflict is currently foreseeable given Cluster C's exclusion of Equity/Drawdown as inputs (FR-004).
- P2-04 (Risk Ownership Consolidation) - deferred dependency: RiskEngine's full ADR-006/ADR-007 conformance, including TD-006 and any deeper integration of Position-derived Exposure into RiskEngine's own risk-limiting logic, remains P2-04's scope, not P2-02A's.
- TD-007 (Lifecycle Control Surface) - no dependency identified; unrelated to Position or Exposure.
- ADR-010 / Phase 3 (Tick-Complete Snapshot architecture) - future compatibility constraint on OQ-006's eventual serialization and replay implications, explicitly named in OQ-006 itself; not a P2-02A build target.
- PositionSizingEngine activation (OQ-005) - deferred dependency, not a P2-02A dependency; classified DEFERRED OUT OF SCOPE (Section 16).
- Repository cleanup (run_engine/core/position_sizing.py, run_engine/core/equity_stabilizer.py, run_engine/runtime/) - deferred to Phase 6 Repository Consolidation; recorded as findings only, not dependencies.
- TD-005 (automated regression test suite) - deferred, project-wide; unrelated to this analysis's dependency structure.

---

## 26. Risks of Incorrect Ordering

- Deciding Cluster C's derivation formula before Cluster B's semantics (violating DEP-002): risk of encoding the wrong scientific concept behind an implementation that appears complete, requiring costly rework and re-certification once discovered.
- Resolving Cluster D2 or Cluster F before Cluster E's classification (violating DEP-005/DEP-006): risk of silently breaking the certified pre-trade entry_basis contract (FR-019, TD-003), corrupting realized PnL for Scale-In scenarios identical in shape to those certified in P1-03.1.
- Wiring Cluster H before Cluster C produces a real value (violating DEP-008): risk of feeding RiskEngine a placeholder or prematurely-guessed Exposure value, reproducing TD-006's own diagnosed pattern in a new location instead of avoiding it.
- Instantiating Cluster G's concrete name before Cluster B is resolved (violating DEP-003 in its strong form): risk of choosing a name that does not fit the eventual semantic definition, requiring a rename touching every consumer and document reference.
- Expanding Cluster H into RiskEngine's actual Peak-Equity/Drawdown logic (violating the DEP-012 scope boundary): risk of silently absorbing P2-04's charter into P2-02A, violating Principle IP-002 and the explicit scope-protection instruction governing this analysis.
- Treating P2-02A as a single linear chain (Alternative Structure 1, Section 20): risk of unnecessarily delaying the entire unit behind the Exposure-Definition Track's OQ-001 resolution, when the Ownership-Consolidation Track (Cluster E, most of Cluster F, Cluster D1) could proceed independently and in parallel.

---

## 27. Scientific Dependency Conclusions

Thirteen internal or external-facing dependencies were identified and assigned stable IDs (P2-02A-DEP-001 through P2-02A-DEP-013). No dependency cycle exists among the nine capability clusters (Section 17.1). Two clusters (A, Position Semantics; I, Compatibility and Invariants) are already fully satisfied by prior certified work and function as a fixed reference frame rather than as pending decisions. The remaining seven clusters (B through H) decompose into two scientifically independent tracks - an Exposure-Definition Track (B, C, G, and the exposure-specific portion of D) gated by the scientific definition of Position-derived Exposure (OQ-001), and an Ownership-Consolidation Track (E, F, and the shape-parity portion of D) gated by the temporal/ownership classification of the pre-trade Position snapshot (OQ-003's conceptual half) - that converge only at Cluster H (RiskEngine Consumption Boundary) and at the final, cross-cutting compatibility validation (Cluster I). Of the six FRA Open Questions, one (OQ-001) is classified BLOCKING, three (OQ-002, OQ-003, OQ-006) are classified CONDITIONALLY BLOCKING with precisely scoped blocking effects, one (OQ-004) is classified NON-BLOCKING, and one (OQ-005) is classified DEFERRED OUT OF SCOPE. All twenty FRA functional requirements (P2-02A-FR-001 through P2-02A-FR-020) are referenced by at least one cluster's dependency analysis (Sections 7 through 15) or dependency record (Section 17).

---

## 28. Readiness for Capability Gap Analysis

This analysis identified no scientific ambiguity that blocks proceeding to a Capability Gap Analysis. The one BLOCKING open question (OQ-001) and the three CONDITIONALLY BLOCKING open questions (OQ-002, OQ-003, OQ-006) are properly Architecture-stage decisions, not gaps in this dependency analysis itself: their existence and their precise blocking scope are now fully characterized (Sections 16, 17, 19), which is this document's purpose. A Capability Gap Analysis can proceed to examine, cluster by cluster and consumer by consumer, exactly which files and code paths require change once each open question is eventually resolved, using the Dependency Stages (Section 24) as its ordering reference and the Dependency Graph (Section 17) as its blocking reference.

Readiness: READY. This document is sufficient to proceed to the P2-02A Capability Gap Analysis. No further scientific dependency investigation is required before that step.

---

## 29. Internal Consistency Review

Terminology consistency - "Capability," "Cluster," "Dependency," "Prerequisite," "Blocking," "Conditionally Blocking," "Non-Blocking," and "Deferred Out of Scope" are used consistently throughout this document with the definitions established in Sections 5 and 16. "Exposure" is never used ambiguously between the ADR-004 sense and the RiskEngine allocation sense without explicit qualification, consistent with the FRA's own terminology discipline.

Scope consistency - no dependency recorded in Section 17 introduces a new architecture decision, a new interface, a new formula, or a new final name; every dependency describes a relationship between capabilities, not a resolution of one. Section 25 confirms all P2-03/P2-04/TD-006/TD-007/repository-cleanup/test-suite topics are recorded only as external, deferred, or future-compatibility dependencies, never as in-scope work.

Dependency-cycle consistency - verified explicitly in Section 17.1; no cycle exists.

Traceability consistency - all twenty FRA functional requirements are referenced by at least one section among 7 through 15 or by at least one dependency record in Section 17; this was cross-checked requirement by requirement during drafting (FR-001 and FR-002 in Section 7; FR-003 in Sections 10 and 24; FR-004, FR-005, FR-006 in Sections 8, 9, 13; FR-007 in Sections 10, 17; FR-008 in Sections 10, 11, 17; FR-009 in Section 7; FR-010, FR-011 in Section 14; FR-012 in Sections 11, 12; FR-013, FR-014 in Sections 7, 15; FR-015, FR-016 in Sections 9, 12; FR-017 in Section 15; FR-018 in Section 9; FR-019 in Sections 11, 12, 15; FR-020 in Sections 10, 15).

Dependency-ID uniqueness - P2-02A-DEP-001 through P2-02A-DEP-013 are each used exactly once as a definition (Section 17) and referenced only by ID thereafter (Sections 18 through 27); no ID collision or reuse was introduced.

Ordering consistency - Section 24's stages match the Dependency Graph's edges exactly; no capability is scheduled before a cluster it has a HARD dependency on, per Section 17's Blocking Effect column.

Observation/requirement/decision separation - Sections 4 and 6 contain only repository-grounded observations; Sections 7 through 15 contain only dependency analysis derived from those observations plus the FRA and the Architecture Baseline; Section 19's Minimal Prerequisite Analysis explicitly tests rather than assumes its hypothesis; no architecture decision, formula selection, or final naming is made anywhere in this document.

Status: Internal Consistency Review PASS.
