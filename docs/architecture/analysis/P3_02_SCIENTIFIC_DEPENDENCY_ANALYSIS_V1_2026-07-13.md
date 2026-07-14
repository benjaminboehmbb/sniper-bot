Document Class:
Scientific Dependency Analysis

Document ID:
P3-02-SDA

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
docs/architecture/analysis/P3_02_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-13.md

Depends On:
- docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md
- docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md
- docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md
- docs/architecture/analysis/P3_02_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-13.md
- docs/architecture/analysis/P3_01_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-13.md
- docs/architecture/analysis/P3_01_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-13.md
- docs/architecture/analysis/P3_01_CAPABILITY_GAP_ANALYSIS_V1_2026-07-13.md
- docs/architecture/P3_01_DETERMINISTIC_EXECUTION_ORDERING_ARCHITECTURE_V1_2026-07-13.md
- docs/architecture/P3_01_DETERMINISTIC_EXECUTION_ORDERING_SPECIFICATION_V1_2026-07-13.md
- docs/architecture/certification/P3_01_FINAL_CERTIFICATION_V1_2026-07-13.md
- docs/architecture/P2_02A_POSITION_OWNERSHIP_ARCHITECTURE_V1_2026-07-10.md
- docs/architecture/P2_02A_POSITION_OWNERSHIP_SPECIFICATION_V1_2026-07-10.md
- docs/architecture/P2_03_FINANCIAL_OWNERSHIP_ARCHITECTURE_V1_2026-07-11.md
- docs/architecture/P2_03_FINANCIAL_OWNERSHIP_SPECIFICATION_V1_2026-07-11.md
- docs/architecture/P2_04_RISK_OWNERSHIP_ARCHITECTURE_V1_2026-07-13.md
- docs/architecture/P2_04_RISK_OWNERSHIP_SPECIFICATION_V1_2026-07-13.md
- current runtime code at HEAD f6fb7f3911a978884ca10b22a0eef832a52f9486

Referenced By:
- future P3-02 Capability Gap Analysis
- future P3-02 Architecture

Methodological Structure Reference (content not carried over):
- docs/architecture/analysis/P3_01_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-13.md

---

# P3-02 Information Flow Validation - Scientific Dependency Analysis

## 1. Document Metadata

See front matter above. This document is the P3-02 Scientific Dependency Analysis (SDA), the second stage of the P3-02 governance chain (FRA -> SDA -> CGA -> Architecture -> Specification -> Implementation -> Final Certification), following the methodology already established by P2-02A, P2-03, P2-04, and P3-01.

## 2. Purpose

This document identifies the scientific dependencies among the twenty-four Functional Requirements `docs/architecture/analysis/P3_02_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-13.md` (the "P3-02 FRA") establishes. It classifies each dependency, builds Capability Clusters, a Dependency Catalogue, a Dependency Graph, Dependency Layers, and a Dependency Matrix, performs Cycle Detection, and records Scientific Dependency Findings and Open Questions. It introduces no new Functional Requirement, performs no Capability Gap classification (COMPLETE/PARTIAL/MISSING), and makes no Architecture Decision.

## 3. Scope

In scope: dependency relationships among the twenty-four P3-02 FRs; dependency relationships between P3-02 FRs and already-certified P2-02A/P2-03/P2-04/P3-01 contracts (Compatibility Dependencies); dependency relationships between P3-02 FRs and items explicitly forwarded to another unit or a future phase (Cross-Unit Dependencies); dependency relationships contingent on a not-yet-decided Open Question (Conditional Dependencies); cycle detection across the complete dependency graph.

Out of scope: any Capability classification; any Architecture Decision; any new Functional Requirement; any resolution of an Open Question the FRA left open; any Position/Financial/Risk/Performance formula or ownership change; any P3-01 ordering reopening; any concrete implementation.

## 4. Binding Baseline

- `docs/architecture/analysis/P3_02_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-13.md` - the sole source of the twenty-four Functional Requirements this document analyzes; re-read in full for this document (Section 5), not summarized from memory.
- `docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md` - ADR-001 through ADR-012, the Runtime Ownership Matrix, Rules OM-001 through OM-009, the Target Information Flow, Principles IF-001 through IF-006, Rules IF-001 through IF-006, Architecture Invariants AI-001 through AI-015, Acceptance Criteria AC-001 through AC-013; already fully re-read and cited by the P3-02 FRA, re-confirmed unchanged for this document.
- `docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md` - Implementation Principles IP-001 through IP-006; the P3-02 and P3-03 unit definitions.
- `docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md` - TD-004 and TD-007, re-confirmed unmodified (Section 5).
- `docs/architecture/P2_02A_POSITION_OWNERSHIP_ARCHITECTURE_V1_2026-07-10.md`, `docs/architecture/P2_02A_POSITION_OWNERSHIP_SPECIFICATION_V1_2026-07-10.md`, `docs/architecture/P2_03_FINANCIAL_OWNERSHIP_ARCHITECTURE_V1_2026-07-11.md`, `docs/architecture/P2_03_FINANCIAL_OWNERSHIP_SPECIFICATION_V1_2026-07-11.md`, `docs/architecture/P2_04_RISK_OWNERSHIP_ARCHITECTURE_V1_2026-07-13.md`, `docs/architecture/P2_04_RISK_OWNERSHIP_SPECIFICATION_V1_2026-07-13.md` - the certified Position, Financial, and Risk contracts every Compatibility Dependency in Section 14 is measured against, not reopened.
- The complete, certified P3-01 governance chain (FRA, SDA, CGA, Architecture, Specification, Final Certification) - the source of every Cross-Unit Dependency in Section 15 that touches P3-01, not reopened.
- Current runtime code at HEAD `f6fb7f3911a978884ca10b22a0eef832a52f9486`, independently re-verified in Section 5, not assumed from the FRA's own prior text.

Methodological structure reference only, content not mechanically carried over: `docs/architecture/analysis/P3_01_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-13.md`.

## 5. Repository Verification

Repository state, verified directly, not assumed:

- Branch: `run-engine-consolidation-safety` (confirmed via `git branch --show-current`).
- Local HEAD: `f6fb7f3911a978884ca10b22a0eef832a52f9486`, matching the stated expected HEAD exactly, unchanged since the FRA's own drafting.
- Remote HEAD: `f6fb7f3911a978884ca10b22a0eef832a52f9486`, identical to local HEAD (confirmed via `git fetch` followed by `git rev-parse origin/run-engine-consolidation-safety`).
- Working tree: the same pre-existing, unrelated tracked modification (`docs/capabilities/SGF_013_SCIENTIFIC_BEHAVIOUR_REPRESENTATION_2026-06-26.md`) and the same set of pre-existing untracked directories/files as at FRA drafting time, plus the FRA itself (still untracked, not committed). None touched by this document's own drafting. `run_engine/` itself remains clean.

The P3-02 FRA was re-read in full for this document (not summarized from memory); every Functional Requirement's own Requirement Statement, Scientific Rationale, Existing Evidence, Current Conformance, Scope Boundary, and Traceability field was re-examined directly from the FRA's own text to derive the dependencies in Section 11.

The following runtime files were re-read fresh for this document, independent of the FRA's own prior citations: `run_engine/core/canonical_enforcer.py` (re-confirmed: eleven `apply_*` methods; `apply_risk` alone returns `self.cs.get()` rather than a single key), `run_engine/core/canonical_state.py` (re-confirmed: `get()` returns `self.state` directly), `run_engine/core/performance.py` (re-confirmed: `self.stats` mutated in place, returned unchanged in object identity across calls), `run_engine/core/position.py` (re-confirmed: `snapshot()` constructs a fresh dict on every call; `update_post_trade` mutates six instance attributes sequentially without atomicity).

**Correction to the governing task's own component list.** The governing task names a component "StateManager." No class of that name exists anywhere in `run_engine/`, confirmed by repository-wide search. The active component performing this role is `StateEngine` (`run_engine/core/state.py`), already named correctly throughout the FRA. This document uses `StateEngine`, the actual repository-grounded name, and records the naming discrepancy here rather than silently substituting one term for the other without comment.

No runtime file was modified by this document's own drafting.

## 6. Scientific Dependency Method

A dependency `P3-02-FR-X -> P3-02-FR-Y` is recorded when FR-Y's own Requirement Statement, Existing Evidence, Current Conformance, or Scope Boundary field, as written in the FRA, presupposes, is evidenced by, or is explicitly qualified by FR-X's own subject matter. Four dependency classes are used, matching the governing task's own required output categories:

- **REQUIRED** - a structural or evidentiary dependency entirely internal to this unit's own twenty-four Functional Requirements: FR-Y's own conformance claim cannot be evaluated, or was in fact evidenced, independently of FR-X.
- **CONDITIONAL** - a dependency that exists only if a specific, currently-undecided Open Question is resolved a particular way; the dependency's own strength or direction may change depending on that resolution.
- **CROSS-UNIT** - a dependency reaching into another unit's own scope (P3-01, P3-03, a future Runtime Safety/Control Unit, or Phase 6 Repository Consolidation) without that unit's own decision being reopened.
- **COMPATIBILITY** - a dependency requiring FR-X's own resolution to remain consistent with an already-certified contract (P2-02A, P2-03, P2-04, P3-01, or a Baseline ADR/AI/Rule) that this document does not reopen.

Every dependency below is derived exclusively from the FRA's own text (Section 5) and, where the FRA's own text itself cites direct repository evidence, from that same repository evidence, independently re-confirmed in Section 5. No dependency is asserted from methodological precedent alone.

## 7. Capability Clusters

Twelve thematic clusters group the twenty-four Functional Requirements for readability; cluster membership does not itself imply a dependency (dependencies are stated individually in Section 11).

| Cluster | Title | Members |
|---|---|---|
| A | Read-Contract and Snapshot Isolation | FR-001, FR-002, FR-003, FR-004 |
| B | Producer-Consumer Verifiability | FR-005, FR-017 |
| C | Writer-on-Behalf-Of and Publication Contract | FR-006, FR-007 |
| D | Semantic Continuity and Reconstruction | FR-008, FR-009 |
| E | Runtime Event and Lifecycle Integrity | FR-010, FR-011 |
| F | Domain Information Flow (Position/Financial/Risk) | FR-012, FR-014, FR-015 |
| G | Cross-Tick Private-State Safety | FR-013 |
| H | Performance Flow (Current-State Only) | FR-016 |
| I | Failure and HOLD Information Flow | FR-018, FR-019 |
| J | Alternative Paths and Traceability | FR-020, FR-021 |
| K | Deterministic Information Flow | FR-022 |
| L | Scope Boundaries | FR-023, FR-024 |

## 8. Dependency Layers

Layers are ordered so that a Functional Requirement in a higher-numbered layer may depend on one in a lower-numbered layer, never the reverse (verified acyclic, Section 16).

**Layer 0 - Certified Compatibility Baseline (not a P3-02 FR; the fixed ground every Compatibility Dependency measures against).** P2-02A, P2-03, P2-04, and the complete P3-01 governance chain.

**Layer 1 - Foundational Contracts.** FR-001 (read-contract), FR-006 (write-contract), FR-010 (event integrity).

**Layer 2 - Structural Consumption and Verification Capability.** FR-002, FR-005, FR-011.

**Layer 3 - Object-Identity and Publication Consistency.** FR-003, FR-004, FR-007, FR-017.

**Layer 4 - Domain Information Flow.** FR-012, FR-013, FR-014, FR-015, FR-016.

**Layer 5 - Cross-Cutting Principles (evidentially downstream of Layer 4).** FR-008, FR-009, FR-018, FR-019, FR-020.

**Layer 6 - Aggregate Assurance.** FR-021, FR-022.

**Cross-Unit Layer (parallel to all layers, not sequential).** FR-023, FR-024.

## 9. Runtime Object Flow Re-Verification

Independently re-traced against the current runtime (Section 5), confirming the FRA's own Section 7 trace remains accurate and forms the factual substrate every information-flow-topology dependency in Section 11 (FR-012, FR-014, FR-015, FR-019) is derived from: `TradeLifecycleEngine` (Lifecycle Facts/current position) -> `PositionEngine` (Position) -> {`PnLEngine` (Entry Basis input), `RiskEngine` (Exposure input)}; `PositionEngine` + `TradeLifecycleEngine` -> `PnLEngine` (Realized PnL, Equity, Peak Equity) -> `RiskEngine` (Equity/Peak Equity input); `PnLEngine` + `Position` -> `RiskEngine` (Drawdown, Drawdown Ratio, `risk_allocation_factor`); `StrategySelector` + `PnLEngine` (`pnl`) + `TradeLifecycleEngine` (`trade_event`) -> `PerformanceEngine`. This linear-with-fan-out topology (no object consumed before its own producer's stage, confirmed by the twelve-stage order P3-01-AD-001 ratifies, not reopened) is the structural basis for every REQUIRED dependency among FR-012, FR-013, FR-014, FR-015, FR-016, FR-019 in Section 11.

## 10. Producer-Object-Consumer Cross-Reference

| Object | Producer FR | Consumer FR(s) |
|---|---|---|
| `CanonicalState.get()`'s own read value | FR-001 | FR-002, FR-003, FR-005, FR-017, FR-022 (all consume or are qualified by the read-contract) |
| Canonical Working State | FR-002 | FR-015 (RiskEngine's own input) |
| Tick-Complete result `"state"` field | FR-001, FR-003 | FR-021 (traceability), FR-022 (determinism qualification) |
| Performance Metrics object | FR-004, FR-016 | FR-021, FR-022 |
| `CanonicalState.state` write path | FR-006 | FR-007, FR-012, FR-014, FR-015, FR-016 (every publication step in each flow) |
| Lifecycle Event / Lifecycle History | FR-010, FR-011 | FR-012, FR-014, FR-018, FR-019 |
| Position | FR-012 | FR-013, FR-014, FR-015, FR-019 |
| Realized PnL / Equity / Peak Equity | FR-014 | FR-015, FR-019 |
| Risk Metrics | FR-015 | (no active consumer among the twenty-four FRs; Section 12) |
| Execution Decision / `pnl` / `trade_event` | (FR-006 write path) | FR-016 |

## 11. Dependency Catalogue

Fifty-two dependency records, `P3-02-DEP-001` through `P3-02-DEP-052`, each individually enumerated, classified per Section 6, and traceable to specific FRA text.

**P3-02-DEP-001.** FR-001 -> FR-003. REQUIRED. FR-003's own Scope Boundary states its own isolation mechanism "is an Architecture-stage decision," but its own Requirement Statement (post-return stability of the Tick-Complete result's own `"state"` field, which is literally `CanonicalState.get()`'s own return value per `loop.py:100`) cannot be finalized independently of FR-001's own read-contract resolution.

**P3-02-DEP-002.** FR-001 -> FR-002. CONDITIONAL. FR-002's own Current Conformance is "currently evidenced" today, but a future resolution of FR-001 that altered `get()`'s own repeated-call behaviour (for example, a single-use or invalidating view) could affect FR-002's own continued internal-consumption evidence; contingent on the FR-001 resolution chosen, referenced by OQ-001.

**P3-02-DEP-003.** FR-001 -> FR-005. CONDITIONAL. FR-005's own Validation Condition ("an independent, repeatable procedure confirms... no consumer mutates the object it consumes") is easier or harder to satisfy depending on whether FR-001 resolves toward a structurally-enforced read-only view or remains a live reference; contingent, referenced by OQ-004.

**P3-02-DEP-004.** FR-001 -> FR-017. CONDITIONAL. Same reasoning as DEP-003, applied to FR-017's own specific OM-004 verifiability requirement; contingent, referenced by OQ-004.

**P3-02-DEP-005.** FR-001 -> FR-022. CONDITIONAL. FR-022's own Current Conformance explicitly notes Residual Risk RR-001 (itself downstream of FR-001's own unresolved read-contract) "does not contradict" cross-instance determinism today; a future FR-001 resolution could either close or leave open this qualification.

**P3-02-DEP-006.** FR-002 -> FR-015. REQUIRED. FR-015's own Requirement Statement names "Canonical Financial State" as `RiskEngine`'s own input, read as Canonical Working State (FRA Section 11, Section 19); FR-015's own conformance directly presupposes FR-002's own internal-consumption contract holding.

**P3-02-DEP-007.** FR-003 -> FR-022. REQUIRED. FR-022's own text (FRA Section 24) states its own Reference and Copy Semantics findings "introduce a distinct, additional determinism-adjacent concern" via Residual Risk RR-001, directly derived from FR-003's own finding.

**P3-02-DEP-008.** FR-004 -> FR-022. REQUIRED. Same mechanism as DEP-007, for Performance Metrics specifically (RR-001's own second named object).

**P3-02-DEP-009.** FR-003 <-> FR-004. COMPATIBILITY (sibling-consistency). Both FRs concern object-identity/Derived-View stability for canonical publications and must be resolved under one mutually consistent answer to Open Question OQ-007 ("Welche Runtime-Objekte duerfen Derived Views sein?"); neither is a sequential prerequisite of the other.

**P3-02-DEP-010.** FR-005 -> FR-017. REQUIRED. FR-017's own Requirement Statement is a named special case of FR-005's own general Producer-Consumer verifiability requirement, applied specifically to Rule OM-004; FR-017's own Traceability field cites Rule OM-004 exactly as FR-005's own Scientific Rationale does.

**P3-02-DEP-011.** FR-005 -> FR-012. CONDITIONAL. FR-012's own flow-conformance claim would gain independent verifiability, not merely manual-inspection evidence, once FR-005's own general verification methodology exists; not required for FR-012's own current evidenced status, which rests on direct trace, not on FR-005.

**P3-02-DEP-012.** FR-005 -> FR-014. CONDITIONAL. Same reasoning as DEP-011, applied to FR-014.

**P3-02-DEP-013.** FR-005 -> FR-015. CONDITIONAL. Same reasoning as DEP-011, applied to FR-015.

**P3-02-DEP-014.** FR-005 -> FR-016. CONDITIONAL. Same reasoning as DEP-011, applied to FR-016's own current-state description.

**P3-02-DEP-015.** FR-006 -> FR-007. REQUIRED. FR-007's own Requirement Statement (consistent `apply_*` return-value shape) presupposes FR-006's own finding that every write already occurs through a named `apply_*` method; FR-007 refines a contract FR-006 first establishes exists.

**P3-02-DEP-016.** FR-006 -> FR-012. REQUIRED. FR-012's own Requirement Statement's final step ("`CanonicalState` (Authoritative Owner, via `CanonicalEnforcer`)") is literally FR-006's own Writer-on-Behalf-Of exclusivity applied to Position.

**P3-02-DEP-017.** FR-006 -> FR-014. REQUIRED. Same mechanism as DEP-016, applied to Financial state (`apply_pnl`, `apply_realized_pnl_cumulative`, `apply_equity`, `apply_peak_equity`).

**P3-02-DEP-018.** FR-006 -> FR-015. REQUIRED. Same mechanism as DEP-016, applied to Risk Metrics (`apply_risk`).

**P3-02-DEP-019.** FR-006 -> FR-016. REQUIRED. Same mechanism as DEP-016, applied to Performance Metrics (`apply_performance_metrics`).

**P3-02-DEP-020.** FR-012, FR-014, FR-015 -> FR-008. REQUIRED (evidentiary aggregation, direction: specific instances ground the general principle). FR-008's own Existing Evidence field cites "Sections 17-19" - the Position, Financial, and Risk flow analyses that are FR-012, FR-014, and FR-015's own subject matter - as the direct source of its own "currently evidenced" conformance.

**P3-02-DEP-021.** FR-011, FR-014, FR-015 -> FR-009. REQUIRED (evidentiary aggregation). FR-009's own Existing Evidence field cites "Sections 16-19" - Lifecycle History (FR-011) plus Financial and Risk flow (FR-014, FR-015) - as its own direct evidentiary source.

**P3-02-DEP-022.** FR-008 <-> FR-009. COMPATIBILITY (sibling-consistency). Both are general Target-Information-Flow principles (IF-003 versus IF-001/IF-002) typically co-validated by the same underlying flow evidence (DEP-020, DEP-021 share Sections 17-19); neither is sequentially prior to the other.

**P3-02-DEP-023.** FR-010 -> FR-011. REQUIRED. FR-011's own immutability claim ("completed lifecycle records SHALL remain immutable") presupposes FR-010's own finding that each `LifecycleEvent` is a frozen dataclass generated at exactly one call site; if FR-010's own frozen-dataclass property failed, FR-011's own claim would not hold.

**P3-02-DEP-024.** FR-010 -> FR-018. REQUIRED. FR-018's own Failure Information Flow conformance for the rejected-transition case presupposes FR-010's own single-call-site guarantee for `RUNTIME_FAILURE_EVENT` generation (`_failure_event`, FRA Section 15).

**P3-02-DEP-025.** FR-011 -> FR-012. REQUIRED. FR-012's own Requirement Statement's first step ("Lifecycle Event/current position -> `PositionEngine`") presupposes FR-011's own Lifecycle History integrity.

**P3-02-DEP-026.** FR-011 -> FR-014. REQUIRED. FR-014's own Requirement Statement's first step ("Lifecycle Facts + Entry Basis -> `PnLEngine`") presupposes FR-011's own Lifecycle History integrity, identically to DEP-025.

**P3-02-DEP-027.** FR-011 -> FR-019. REQUIRED. FR-019's own HOLD-path conformance presupposes `TradeLifecycleEngine.on_execution`'s own well-defined `None`-return behaviour for a HOLD action, which is part of FR-011's own Lifecycle History production contract.

**P3-02-DEP-028.** FR-012 -> FR-014. REQUIRED. FR-014's own Requirement Statement names "Entry Basis" as an explicit input; the FRA's own Section 17 confirms Entry Basis is `position_pre["entry_price"]`, sourced directly from Position (FR-012's own subject).

**P3-02-DEP-029.** FR-012 -> FR-015. REQUIRED. FR-015's own Requirement Statement names "Position" as an explicit input, including Exposure, which FR-012's own text confirms is derived exclusively within Position (`_compute_exposure`), not independently owned.

**P3-02-DEP-030.** FR-012 -> FR-013. REQUIRED. FR-013's own subject (`PositionEngine`'s own private cross-tick state) is the same component FR-012 traces as Position's own Computational Authority; FR-012's own Current Conformance field explicitly cross-references FR-013 as a qualification of its own topology-level finding.

**P3-02-DEP-031.** FR-012 -> FR-019. REQUIRED. FR-019's own HOLD-path conformance presupposes `PositionEngine._set_flat`'s own well-defined no-op behaviour, part of FR-012's own production contract.

**P3-02-DEP-032.** FR-013 -> FR-018. REQUIRED. FR-018's own Requirement Statement explicitly requires "any newly-identified divergence condition SHALL be explicitly documented"; FR-013 is precisely such a newly-identified divergence condition, and FR-018's own fulfillment for this specific instance depends on FR-013 remaining properly and separately documented (FRA Section 21, cross-referencing Section 13).

**P3-02-DEP-033.** FR-014 -> FR-015. REQUIRED. FR-015's own Requirement Statement names "Canonical Financial State" as an explicit input; the FRA's own Section 19 confirms `RiskEngine.check` reads `equity` and `peak_equity`, both FR-014's own Computational Authority output.

**P3-02-DEP-034.** FR-014 -> FR-019. REQUIRED. FR-019's own HOLD-path conformance presupposes `PnLEngine.update`'s own well-defined `0.0`-return behaviour for a `None`/non-closing `trade_event`, part of FR-014's own production contract.

**P3-02-DEP-035.** FR-016 <-> FR-004. REQUIRED (shared-object). FR-004's own Existing Evidence field and FR-016's own Requirement Statement both concern `PerformanceEngine.update`'s own return value; FR-004 concerns its object-identity property, FR-016 concerns its current-state accounting shape - the same underlying object, two distinct, individually-tracked properties of it.

**P3-02-DEP-036.** FR-001 through FR-020 -> FR-021. REQUIRED (aggregate). FR-021's own Requirement Statement ("Every runtime object... SHALL be traceable through...") and its own Existing Evidence ("Section 25 - complete traceability table constructed... for every object in the Runtime Object Inventory") aggregate the individual traceability findings every other information-flow-topology and object-identity FR in this document already establishes; FR-021 adds no new evidence of its own beyond restating theirs in one table.

**P3-02-DEP-037.** FR-022 -> FR-013. CONDITIONAL. FR-013's own Traceability field cites "P3-01 Architecture Section 19 (extended, not reopened)," the same section FR-022's own P3-01-inherited Failed-Tick-retry qualification cites; a future resolution of FR-013 (Section 17 of this document) could narrow or widen FR-022's own inherited qualification, depending on which classification FR-013 ultimately receives.

**P3-02-DEP-038.** FR-012 - Compatibility with P2-02A. COMPATIBILITY. FR-012's own Scope Boundary: "does not reopen P2-02A's own certified ownership, formula, or pre-trade-view contract."

**P3-02-DEP-039.** FR-014 - Compatibility with P2-03. COMPATIBILITY. FR-014's own Scope Boundary: "does not reopen P2-03's own certified ownership or formulas."

**P3-02-DEP-040.** FR-015 - Compatibility with P2-04. COMPATIBILITY. FR-015's own Scope Boundary: "does not reopen P2-04's own certified ownership or formulas."

**P3-02-DEP-041.** FR-011 - Compatibility with ADR-003 (Baseline). COMPATIBILITY. FR-011's own Traceability cites ADR-003 (TradeLifecycle as the Authoritative Trade Model) as the governing, not-reopened, certified basis for Lifecycle History ownership.

**P3-02-DEP-042.** FR-002 - Compatibility/Cross-Unit with P3-01-AI-003, P3-01-AI-004. COMPATIBILITY and CROSS-UNIT jointly. FR-002 re-verifies, without reopening, two P3-01-established invariants (FRA Section 8).

**P3-02-DEP-043.** FR-006 - Compatibility/Cross-Unit with P3-01-AI-009, P3-01-AD-002. COMPATIBILITY and CROSS-UNIT jointly. FR-006 re-verifies, without reopening, P3-01's own Writer-on-Behalf-Of migration (FRA Section 8, Section 14).

**P3-02-DEP-044.** FR-010 - Compatibility with Baseline AI-008 / ADR-002. COMPATIBILITY. FR-010's own Traceability cites AI-008 and ADR-002 directly, both Baseline-level, not reopened.

**P3-02-DEP-045.** FR-013 - Cross-Unit with P3-01-AD-004. CROSS-UNIT. P3-01-AD-004 already established, and the P3-01 Architecture's own Section 19 already accepted without resolving, the general risk category (non-reconciled cross-tick private state after a Failed Tick) FR-013 extends with new evidence to `PositionEngine`; FR-013 does not reopen AD-004's own decision not to require a rollback mechanism.

**P3-02-DEP-046.** FR-018 - Cross-Unit with P3-01-AD-004, P3-01-AD-006. CROSS-UNIT. FR-018's own Requirement Statement requires exact conformance to both, not reopened.

**P3-02-DEP-047.** FR-019 - Cross-Unit with P3-01-AD-005. CROSS-UNIT. FR-019's own Requirement Statement requires exact conformance, not reopened.

**P3-02-DEP-048.** FR-020 - Cross-Unit with P3-01-AD-009 and Phase 6 Repository Consolidation. CROSS-UNIT. FR-020's own Scope Boundary: disposition of any dormant file "remains Phase 6 Repository Consolidation's own scope," not decided here; ordering-exclusivity itself re-verifies P3-01-AD-009 without reopening it.

**P3-02-DEP-049.** FR-022 - Cross-Unit with P3-01-AD-007 / Contract EO-013. CROSS-UNIT. FR-022's own Traceability cites both directly as the source of its own cross-instance determinism evidence, re-cited, not re-executed, not reopened.

**P3-02-DEP-050.** FR-004, FR-016 - Cross-Unit with TD-004 / P3-03. CROSS-UNIT. Both FRs' own Traceability fields cite TD-004 explicitly; FR-016's own Scope Boundary additionally states it "does not reopen or advance TD-004."

**P3-02-DEP-051.** FR-023 - Cross-Unit/Compatibility blanket constraint over FR-001 through FR-022. CROSS-UNIT and COMPATIBILITY jointly. FR-023 is itself a scope-boundary requirement ("This unit SHALL NOT reopen, redecide, or alter the P3-01-ratified... ordering... semantics") that every other Functional Requirement's own resolution must remain compatible with; not a specific pairwise technical dependency, but a governing constraint over the whole set.

**P3-02-DEP-052.** FR-024 - Cross-Unit/Compatibility blanket constraint over FR-004 and FR-016 specifically. CROSS-UNIT and COMPATIBILITY jointly. FR-024's own Requirement Statement ("SHALL NOT redesign `PerformanceEngine`'s own accounting methodology or advance TD-004's own resolution") constrains specifically the two FRs (FR-004, FR-016) whose own subject matter is Performance Metrics.

## 12. Absent Dependencies (Explicitly Verified Non-Dependencies)

Recorded for scientific completeness, consistent with the governing task's own instruction to derive dependencies exclusively from repository evidence rather than from topical proximity: two plausible-looking dependencies were specifically checked against the FRA's own text and the active trace, and found **not** to hold.

**No dependency: FR-015 -> FR-016.** The Baseline's own Runtime Stage Responsibilities table lists Risk Metrics and Performance Metrics as topically adjacent rows, which could suggest a flow dependency; the FRA's own Section 19 states explicitly, and this document re-confirms by direct trace, that "`PerformanceEngine.update` does not itself consume any Risk Metric in the active trace (it receives `decision`, `pnl`, `regime`, `trade_event` only)." No dependency edge is recorded between FR-015 and FR-016.

**No dependency: FR-009 -> FR-016.** FR-009's own Scope Boundary explicitly excludes Performance Information Flow's own reconstruction question from its own evidentiary base ("does not extend to Performance Information Flow's own already-registered TD-004 concern"). No dependency edge is recorded between FR-009 and FR-016.

## 13. Dependency Graph

Textual representation (REQUIRED edges only; CONDITIONAL, COMPATIBILITY, and CROSS-UNIT edges are listed separately in Sections 11, 14, 15 and omitted here for readability, since none of them contributes to a directed cycle, Section 16):

```
FR-001 --> FR-003 --> FR-022
FR-006 --> FR-007
FR-006 --> FR-012 --> FR-014 --> FR-015
                  \--> FR-013 --> FR-018
                  \--> FR-019
FR-010 --> FR-011 --> FR-012
FR-010 --> FR-018
FR-011 --> FR-014
FR-011 --> FR-019
FR-014 --> FR-019
FR-006 --> FR-014
FR-006 --> FR-015
FR-006 --> FR-016 <--> FR-004 --> FR-022
{FR-012, FR-014, FR-015} --> FR-008
{FR-011, FR-014, FR-015} --> FR-009
{FR-001 .. FR-020} --> FR-021
```

`FR-023` and `FR-024` are drawn as a governing frame around the entire graph (Cross-Unit Layer, Section 8), not as graph nodes with their own outgoing REQUIRED edges. `FR-002`, `FR-005`, `FR-017` participate only via CONDITIONAL edges (Section 11, DEP-002 through DEP-005, DEP-010 through DEP-014) and are omitted from the REQUIRED-only graph above; their own CONDITIONAL relationships are listed in full in Section 11.

## 14. Compatibility Dependencies

Consolidated from Section 11 (DEP-038 through DEP-044) for direct visibility, per the governing task's own required output category:

| FR | Certified Baseline | Dependency |
|---|---|---|
| FR-011 | ADR-003 (Baseline) | DEP-041 |
| FR-012 | P2-02A (Architecture, Specification, Final Certification) | DEP-038 |
| FR-014 | P2-03 (Architecture, Specification, Final Certification) | DEP-039 |
| FR-015 | P2-04 (Architecture, Specification, Final Certification) | DEP-040 |
| FR-002 | P3-01-AI-003, P3-01-AI-004 | DEP-042 |
| FR-006 | P3-01-AI-009, P3-01-AD-002 | DEP-043 |
| FR-010 | Baseline AI-008, ADR-002 | DEP-044 |
| FR-023 (blanket) | Complete P3-01 governance chain | DEP-051 |

No Compatibility Dependency requires reopening any cited contract; each is a "must remain consistent with" relationship, verified, not decided, by this document.

## 15. Cross-Unit Dependencies

Consolidated from Section 11 (DEP-042, DEP-043, DEP-045 through DEP-052) for direct visibility:

| FR | Target Unit / Phase | Dependency | Nature |
|---|---|---|---|
| FR-002 | P3-01 (AI-003, AI-004) | DEP-042 | re-verification, not reopened |
| FR-006 | P3-01 (AI-009, AD-002) | DEP-043 | re-verification, not reopened |
| FR-013 | P3-01 (AD-004) | DEP-045 | extension of an already-accepted risk category |
| FR-018 | P3-01 (AD-004, AD-006) | DEP-046 | exact-conformance requirement |
| FR-019 | P3-01 (AD-005) | DEP-047 | exact-conformance requirement |
| FR-020 | P3-01 (AD-009); Phase 6 | DEP-048 | re-verification plus a forwarded disposition question |
| FR-022 | P3-01 (AD-007 / EO-013) | DEP-049 | re-citation of certified replay evidence |
| FR-004, FR-016 | TD-004 / P3-03 | DEP-050 | forwarded, unresolved by design |
| FR-023 | P3-01 (blanket) | DEP-051 | scope-boundary constraint |
| FR-024 | P3-03 (blanket) | DEP-052 | scope-boundary constraint |

No Cross-Unit Dependency requires this document, or any future P3-02 document, to make a decision belonging to another unit; each is either a re-verification of an already-settled fact or an explicit forwarding, consistent with the P3-02 FRA's own Section 8 and Section 33.

## 16. Cycle Detection

The REQUIRED-edge graph (Section 13) was checked for cycles by direct topological inspection of every edge in Section 11 classified REQUIRED. Result: **no cyclic dependency was found.** The graph is a directed acyclic graph (DAG) with two convergence points (FR-012 receiving from FR-006 and FR-011; FR-021 receiving from the entire FR-001 through FR-020 set) and one bidirectional-looking pair that was specifically resolved to a single direction after inspection:

**FR-012 and FR-013 do not form a cycle.** FR-012's own Current Conformance field cross-references FR-013 ("subject to the qualifications recorded separately as FR-003, FR-004, and FR-013"), which could suggest a reverse edge FR-013 -> FR-012. Direct inspection shows this cross-reference is a caveat/annotation, not an evidentiary dependency: FR-012's own "currently evidenced" status for flow *topology* does not rest on FR-013's own outcome; only FR-012's own *object* (`PositionEngine`) is shared with FR-013, which studies that object's own failure-mode behaviour, a separate property. The dependency is recorded one-directionally, FR-012 -> FR-013 (DEP-030): FR-012 establishes the topology `PositionEngine` occupies before FR-013 can meaningfully analyze a failure mode within it.

**FR-016 and FR-004 do not form a cycle.** Both concern the same object (Performance Metrics) but different properties of it (accounting shape versus object identity); recorded as a single REQUIRED shared-object dependency (DEP-035), not two opposing directional edges.

**FR-003/FR-004 and FR-022 do not form a cycle.** FR-022 depends on FR-003 and FR-004 (DEP-007, DEP-008); no edge runs the other way - FR-003's and FR-004's own conformance does not depend on FR-022's own determinism finding.

## 17. Scientific Dependency Findings

**Finding SDF-001.** No cyclic dependency exists among the twenty-four Functional Requirements; the REQUIRED-edge graph is a strict DAG (Section 16).

**Finding SDF-002.** The dependency graph exhibits two structural convergence points: FR-012 (receiving REQUIRED edges from FR-006 and FR-011, and itself feeding FR-013, FR-014, FR-015, FR-019, FR-008) and FR-021 (an aggregate sink receiving from the entire FR-001 through FR-020 set). Both are consistent with Position's own central role in the Target Information Flow (the sole object every one of Financial, Risk, and HOLD-path conformance directly consumes) and with Traceability's own inherently aggregate nature, respectively; neither convergence point indicates an undue concentration of unverified risk, since both FR-012 and FR-021 are themselves independently, currently evidenced (FRA Section 34).

**Finding SDF-003.** Five of the twenty-four Functional Requirements (FR-001, FR-003, FR-004, FR-007, FR-013) sit at the origin of at least one REQUIRED edge whose own target FR currently carries a "not currently met" or "not yet independently evidenced" Current Conformance value (FR-003, FR-004, FR-007, FR-013, FR-017, FR-022's own RR-001 qualification); this means the five open Functional Gaps the FRA records (FG-001 through FG-005) are not isolated - FG-002 (FR-003) and FG-003 (FR-004) both propagate into FR-022's own determinism finding (DEP-007, DEP-008) as an already-bounded Residual Risk (RR-001), and FG-005 (FR-013) propagates into FR-018's own documentation obligation (DEP-032) and FR-022's own inherited qualification (DEP-037). No propagation was found to reach FR-012, FR-014, or FR-015's own flow-topology conformance itself (each remains "currently evidenced" independent of the five gaps, per DEP-030's own one-directional resolution, Section 16).

**Finding SDF-004.** Every Conditional Dependency in this document (DEP-002 through DEP-005, DEP-011 through DEP-014, DEP-037) resolves around exactly two Open Questions the FRA already records without deciding: OQ-001/OQ-004 (`CanonicalState.get()`'s own eventual read-contract) and the eventual classification of FR-013's own finding (OQ-012, and this document's own independent review of FG-005/FR-013, referenced in Section 18). No Conditional Dependency in this document introduces a new Open Question beyond what the FRA already named; Section 18 restates, and does not add to, that set, except where explicitly marked new.

**Finding SDF-005.** Two plausible dependencies were specifically checked and found absent (Section 12): FR-015 does not feed FR-016, and FR-009 does not draw evidence from FR-016. Both absences are explicit, repository-grounded findings of the current active trace, not omissions.

**Finding SDF-006.** All eight Compatibility Dependencies (Section 14) and all ten Cross-Unit Dependencies (Section 15) are one-directional out of this unit's own scope (P3-02 depends on the cited baseline remaining fixed; the cited baseline does not depend on P3-02). No Compatibility or Cross-Unit Dependency requires, or would be satisfied by, any decision this document or a future P3-02 document makes.

## 18. Open Questions

This document decides none of the FRA's own thirteen Open Questions (OQ-001 through OQ-013, FRA Section 39). The following restates, for dependency-analysis purposes only, which Open Question resolution would affect which dependency, and adds two new dependency-specific questions this analysis itself surfaced.

**OQ-001/OQ-004 (restated from the FRA).** `CanonicalState.get()`'s own eventual read-contract resolution determines the final strength and direction of DEP-002, DEP-003, DEP-004, DEP-005.

**OQ-007 (restated from the FRA).** Which Runtime Objects may be Derived Views determines whether DEP-009 (FR-003/FR-004 sibling-consistency) is satisfied by one unified mechanism or by two independently-justified ones.

**OQ-012 (restated from the FRA).** FR-013's own eventual classification (Functional Gap disposition retained, or reclassified as a Residual Risk consistent with the already-accepted P3-01-AD-004 risk category, per this session's own separate targeted review of FG-005) determines the final strength of DEP-030, DEP-032, and DEP-037.

**OQ-014 (new, this document).** Should FR-021 (Complete Object-Level Traceability, an aggregate sink per DEP-036) be re-evaluated once, after every other Functional Requirement reaches its own final CGA classification, or is per-object traceability already fully and independently verifiable before the CGA runs? This document does not decide the CGA's own sequencing; it only notes that DEP-036's own aggregate nature makes FR-021's own eventual CGA classification mechanically dependent on the classification of every one of FR-001 through FR-020.

**OQ-015 (new, this document).** Do the two Compatibility Dependencies that are also Cross-Unit Dependencies (DEP-042 for FR-002, DEP-043 for FR-006) warrant a distinct, third joint category in a future SDA revision, or does recording them under both existing categories (as this document does) suffice? This document does not decide document-taxonomy questions beyond what the governing task specifies.

No question above is decided by this document.

## 19. FR Traceability

Every one of the twenty-four Functional Requirements participates in at least one dependency record.

| FR | Dependency Record(s) |
|---|---|
| FR-001 | DEP-001, DEP-002, DEP-003, DEP-004, DEP-005 |
| FR-002 | DEP-002, DEP-006, DEP-042 |
| FR-003 | DEP-001, DEP-007, DEP-009 |
| FR-004 | DEP-008, DEP-009, DEP-035, DEP-050 |
| FR-005 | DEP-003, DEP-010, DEP-011, DEP-012, DEP-013, DEP-014 |
| FR-006 | DEP-015, DEP-016, DEP-017, DEP-018, DEP-019, DEP-043 |
| FR-007 | DEP-015 |
| FR-008 | DEP-020, DEP-022 |
| FR-009 | DEP-021, DEP-022 |
| FR-010 | DEP-023, DEP-024, DEP-044 |
| FR-011 | DEP-023, DEP-025, DEP-026, DEP-027, DEP-041 |
| FR-012 | DEP-011, DEP-016, DEP-020, DEP-025, DEP-028, DEP-029, DEP-030, DEP-031, DEP-038 |
| FR-013 | DEP-030, DEP-032, DEP-037, DEP-045 |
| FR-014 | DEP-012, DEP-017, DEP-020, DEP-021, DEP-026, DEP-028, DEP-033, DEP-034, DEP-039 |
| FR-015 | DEP-006, DEP-013, DEP-018, DEP-020, DEP-021, DEP-029, DEP-033, DEP-040 |
| FR-016 | DEP-014, DEP-019, DEP-035, DEP-050 |
| FR-017 | DEP-004, DEP-010 |
| FR-018 | DEP-024, DEP-032, DEP-046 |
| FR-019 | DEP-027, DEP-031, DEP-034, DEP-047 |
| FR-020 | DEP-048 |
| FR-021 | DEP-036 |
| FR-022 | DEP-005, DEP-007, DEP-008, DEP-037, DEP-049 |
| FR-023 | DEP-051 |
| FR-024 | DEP-052 |

All twenty-four Functional Requirements are traced to at least one dependency record.

## 20. DEP Traceability (Individually Enumerated)

| DEP | Class | FR(s) |
|---|---|---|
| DEP-001 | REQUIRED | FR-001, FR-003 |
| DEP-002 | CONDITIONAL | FR-001, FR-002 |
| DEP-003 | CONDITIONAL | FR-001, FR-005 |
| DEP-004 | CONDITIONAL | FR-001, FR-017 |
| DEP-005 | CONDITIONAL | FR-001, FR-022 |
| DEP-006 | REQUIRED | FR-002, FR-015 |
| DEP-007 | REQUIRED | FR-003, FR-022 |
| DEP-008 | REQUIRED | FR-004, FR-022 |
| DEP-009 | COMPATIBILITY | FR-003, FR-004 |
| DEP-010 | REQUIRED | FR-005, FR-017 |
| DEP-011 | CONDITIONAL | FR-005, FR-012 |
| DEP-012 | CONDITIONAL | FR-005, FR-014 |
| DEP-013 | CONDITIONAL | FR-005, FR-015 |
| DEP-014 | CONDITIONAL | FR-005, FR-016 |
| DEP-015 | REQUIRED | FR-006, FR-007 |
| DEP-016 | REQUIRED | FR-006, FR-012 |
| DEP-017 | REQUIRED | FR-006, FR-014 |
| DEP-018 | REQUIRED | FR-006, FR-015 |
| DEP-019 | REQUIRED | FR-006, FR-016 |
| DEP-020 | REQUIRED | FR-012, FR-014, FR-015, FR-008 |
| DEP-021 | REQUIRED | FR-011, FR-014, FR-015, FR-009 |
| DEP-022 | COMPATIBILITY | FR-008, FR-009 |
| DEP-023 | REQUIRED | FR-010, FR-011 |
| DEP-024 | REQUIRED | FR-010, FR-018 |
| DEP-025 | REQUIRED | FR-011, FR-012 |
| DEP-026 | REQUIRED | FR-011, FR-014 |
| DEP-027 | REQUIRED | FR-011, FR-019 |
| DEP-028 | REQUIRED | FR-012, FR-014 |
| DEP-029 | REQUIRED | FR-012, FR-015 |
| DEP-030 | REQUIRED | FR-012, FR-013 |
| DEP-031 | REQUIRED | FR-012, FR-019 |
| DEP-032 | REQUIRED | FR-013, FR-018 |
| DEP-033 | REQUIRED | FR-014, FR-015 |
| DEP-034 | REQUIRED | FR-014, FR-019 |
| DEP-035 | REQUIRED | FR-016, FR-004 |
| DEP-036 | REQUIRED | FR-001..FR-020, FR-021 |
| DEP-037 | CONDITIONAL | FR-022, FR-013 |
| DEP-038 | COMPATIBILITY | FR-012 |
| DEP-039 | COMPATIBILITY | FR-014 |
| DEP-040 | COMPATIBILITY | FR-015 |
| DEP-041 | COMPATIBILITY | FR-011 |
| DEP-042 | COMPATIBILITY / CROSS-UNIT | FR-002 |
| DEP-043 | COMPATIBILITY / CROSS-UNIT | FR-006 |
| DEP-044 | COMPATIBILITY | FR-010 |
| DEP-045 | CROSS-UNIT | FR-013 |
| DEP-046 | CROSS-UNIT | FR-018 |
| DEP-047 | CROSS-UNIT | FR-019 |
| DEP-048 | CROSS-UNIT | FR-020 |
| DEP-049 | CROSS-UNIT | FR-022 |
| DEP-050 | CROSS-UNIT | FR-004, FR-016 |
| DEP-051 | CROSS-UNIT / COMPATIBILITY | FR-023 |
| DEP-052 | CROSS-UNIT / COMPATIBILITY | FR-024 |

All fifty-two Dependency records are individually listed above; none is cited only inside a range expression.

## 21. Dependency Readiness Decision

Every theme the governing task requires has been produced: Capability Clusters (Section 7), a Dependency Matrix in cross-reference form (Section 10) and traceability-table form (Sections 19-20), a Dependency Catalogue (Section 11), a Dependency Graph (Section 13), Dependency Layers (Section 8), Cross-Unit Dependencies (Section 15), Conditional Dependencies (embedded in Section 11, cross-referenced in Section 18), Compatibility Dependencies (Section 14), Cycle Detection (Section 16), Scientific Dependency Findings (Section 17), and Open Questions (Section 18). No new Functional Requirement was introduced; no Capability was classified COMPLETE/PARTIAL/MISSING; no Architecture Decision was made; no runtime file was modified.

**Dependency Readiness: READY.** This document is sufficient to proceed to the P3-02 Capability Gap Analysis. The CGA must independently re-verify every dependency here against the repository state at its own drafting time, per this governance chain's own established discipline, and must in particular re-examine FG-005/FR-013's own classification (Section 18, OQ-012) before assigning Capability status to FR-013 and the dependencies it participates in (DEP-030, DEP-032, DEP-037, DEP-045).

## 22. Internal Consistency Review

**Scientific Consistency Review.** Every dependency in Section 11 cites a specific FRA field (Requirement Statement, Scientific Rationale, Existing Evidence, Current Conformance, or Scope Boundary) or a specific, independently re-verified repository fact (Section 5); no dependency is asserted from topical similarity alone. PASS.

**Architecture Consistency Review.** No dependency record in Section 11 selects a resolution mechanism, a copy strategy, or an enforcement design; every dependency states a relationship, not a solution. No Architecture Decision is made anywhere in this document. PASS.

**Scope Review.** Section 3 (Scope) and Section 21 confirm no new Functional Requirement, no Capability classification, and no runtime change occurs anywhere in this document. Sections 14-15 confirm every Compatibility and Cross-Unit Dependency is one-directional out of P3-02's own scope, never requiring a decision this document is not authorized to make. PASS.

**Graph Consistency Review.** Section 13's own textual graph, Section 16's own cycle-detection narrative, and Section 11's own individual REQUIRED-class entries were cross-checked entry-by-entry during drafting; every REQUIRED edge drawn in Section 13 corresponds to exactly one DEP-ID in Section 11, and no DEP-ID classified REQUIRED is missing from Section 13's own diagram. PASS.

**Terminology Review.** "Functionally identical" and "byte-identical" are not used as comparison claims anywhere in this document (no such comparison is performed here); this sentence is this document's only discussion of either term. "REQUIRED," "CONDITIONAL," "CROSS-UNIT," and "COMPATIBILITY" are used exactly as defined in Section 6 throughout, with no dependency record left unclassified. PASS.

**Repository Consistency Review.** Every repository-grounded claim in Section 5 and Section 9 was independently re-verified against the current runtime during this document's own drafting, including the correction of the governing task's own "StateManager" reference to the repository-grounded `StateEngine` (Section 5). PASS.

**Traceability Review.** Section 19 confirms all twenty-four Functional Requirements are traced to at least one dependency record; Section 20 confirms all fifty-two dependency records are individually enumerated, none only inside a range expression. PASS.

**Governance Review.** This document does not create a Capability Gap Analysis, Architecture, Specification, Implementation, or Final Certification; it introduces no new `P3-02-CAP-`, `P3-02-AD-`, `P3-02-AI-`, or `P3-02-IU-` identifier anywhere (confirmed by mechanical check, Section 23); it stops, as instructed, before the Capability Gap Analysis. PASS.

**Independent Self Verification.** Every dependency record in Section 11 was checked, during this document's own closing review, against the FRA's own exact text re-read in Section 5, not against a paraphrase or a memory of an earlier drafting pass. The two Absent Dependencies in Section 12 were specifically sought out and confirmed negative, not merely omitted by default. The FR-012/FR-013 apparent-bidirectionality (Section 16) was independently investigated and resolved to a single direction with an explicit written justification, rather than being left as an unexamined pair. No error was found during this document's own closing review requiring correction before delivery.

Status: Internal Consistency Review PASS.
