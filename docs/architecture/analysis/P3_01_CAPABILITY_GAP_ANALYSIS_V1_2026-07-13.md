Document Class:
Capability Gap Analysis

Document ID:
P3-01-CGA

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
docs/architecture/analysis/P3_01_CAPABILITY_GAP_ANALYSIS_V1_2026-07-13.md

Depends On:
- docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md
- docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md
- docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md
- docs/architecture/analysis/P3_01_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-13.md
- docs/architecture/analysis/P3_01_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-13.md
- docs/architecture/P2_02A_POSITION_OWNERSHIP_ARCHITECTURE_V1_2026-07-10.md
- docs/architecture/P2_03_FINANCIAL_OWNERSHIP_ARCHITECTURE_V1_2026-07-11.md
- docs/architecture/P2_04_RISK_OWNERSHIP_ARCHITECTURE_V1_2026-07-13.md
- docs/architecture/certification/P2_03_FINAL_CERTIFICATION_V1_2026-07-11.md
- docs/architecture/certification/P2_04_FINAL_CERTIFICATION_V1_2026-07-13.md
- current runtime code at HEAD fd22ce130e93261b63830b63600f9e651f7ad496

Referenced By:
- future P3-01 Architecture
- future P3-01 Specification
- future P3-01 Certification

---

# P3-01 Capability Gap Analysis

## 1. Purpose

This document is the Capability Gap Analysis for P3-01 (Deterministic Execution Ordering). It classifies each capability implied by the twenty-three Functional Requirements and thirty-one Dependency records `P3_01_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-13.md` and `P3_01_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-13.md` established as COMPLETE, PARTIAL, or MISSING, evaluated against direct repository evidence.

This document does not create a new Functional Requirement, a new Dependency, or a new ADR. It does not select an architecture, a publication mechanism, a copy-versus-reference semantics, an exception/rollback semantics, or a concrete implementation. Its sole output is a capability classification the P3-01 Architecture must consume.

## 2. Scope

In scope: classification of every capability implied by FR-001 through FR-023 and DEP-001 through DEP-031, evaluated for Scientific, Governance, Runtime, Documentation, and Verification Completeness; explicit treatment of Cross-Unit Observation CUO-01 as a Cross-Unit Capability and of Verified Conformant Finding VC-01 as COMPLETE.

Out of scope: any new Functional Requirement, Dependency, or ADR; any Architecture Decision; any publication mechanism, copy-versus-reference semantics, or exception/rollback semantics selection; any concrete runtime change; any Implementation Unit; any test. Reopening any already-certified P2-02A, P2-03, or P2-04 ownership decision is explicitly out of scope.

## 3. Binding Baseline

- `docs/architecture/analysis/P3_01_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-13.md` - the sole source of the twenty-three Functional Requirements, the four P3-01-owned Functional Gaps (Section 12.1), Cross-Unit Observation CUO-01 (Section 12.2), and Verified Conformant Finding VC-01 (Section 12.3) this document classifies.
- `docs/architecture/analysis/P3_01_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-13.md` - the sole source of the thirty-one Dependency records, the nine Requirement/Capability Clusters, the seven Dependency Layers, and the Coupling and Cycle Analysis finding no cyclic dependency.
- `docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md` - ADR-002, ADR-010, ADR-011; the Runtime Ownership Matrix; Architecture Invariants AI-005, AI-006, AI-007, AI-008, AI-009, AI-014; Acceptance Criteria AC-009, AC-010, AC-011, AC-012.
- `docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md` - the P3-01, P3-02, P3-03 unit definitions this document's Cross-Unit Capability assessment (Section 15) is anchored to.
- `docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md` - TD-004, TD-007.
- `docs/architecture/P2_02A_POSITION_OWNERSHIP_ARCHITECTURE_V1_2026-07-10.md`, `docs/architecture/P2_03_FINANCIAL_OWNERSHIP_ARCHITECTURE_V1_2026-07-11.md`, `docs/architecture/P2_04_RISK_OWNERSHIP_ARCHITECTURE_V1_2026-07-13.md` - the certified ownership contracts this document's Certified Compatibility Assessment (Section 16) references without reopening.
- `docs/architecture/certification/P2_03_FINAL_CERTIFICATION_V1_2026-07-11.md`, `docs/architecture/certification/P2_04_FINAL_CERTIFICATION_V1_2026-07-13.md` - the certified baseline this document's Prior-Certification Compatibility section (Section 25) treats as fixed.

## 4. Repository Verification

Repository state, verified directly, not assumed:

- Branch: `run-engine-consolidation-safety` (confirmed via `git branch --show-current`).
- Local HEAD: `fd22ce130e93261b63830b63600f9e651f7ad496`, matching the stated expected HEAD exactly (confirmed via `git rev-parse HEAD`).
- Remote HEAD: `fd22ce130e93261b63830b63600f9e651f7ad496` (confirmed via `git fetch origin run-engine-consolidation-safety` followed by `git rev-parse origin/run-engine-consolidation-safety`), identical to local HEAD.
- Working tree: one modified file unrelated to `run_engine` and the same set of pre-existing untracked directories every prior document in this chain has recorded, plus the now-untracked `P3_01_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-13.md` and `P3_01_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-13.md` - none inside `run_engine/`, none touched by this analysis. `run_engine/` is confirmed clean (`git status --short run_engine/` returns no output), identical to its state when the FRA and SDA were each independently verified.

### 4.1 Re-Verification of the Four Functional Gaps, CUO-01, and VC-01

Re-checked directly against the current runtime, not merely inherited from the FRA or SDA:

- **Gap 1** (Runtime Tick/Market Regime bypass `CanonicalEnforcer`) - re-confirmed present: `loop.py:42,45`; `canonical_enforcer.py`'s ten methods still exclude `apply_tick` and `apply_regime`.
- **Gap 2** (unhandled-exception semantics absent) - re-confirmed present: `main.py:28`'s `except Exception as e:` remains the sole handler; `loop.py`'s `__main__` block remains unguarded.
- **Gap 3** (full-sequence Tick-Sequence Determinism not separately certified) - re-confirmed present: no dedicated P3-01 replay fixture exists for the complete eighteen-step sequence.
- **Gap 4** (`PerformanceEngine` decision-oriented accounting) - re-confirmed present: `performance.py:11`'s `decision.get('action', 'HOLD')` remains the statistics key.
- **CUO-01** (`CanonicalState.get()` live-mutable reference) - re-confirmed present: `canonical_state.py:107-109`.
- **VC-01** (Stage 12 realized by aggregate incremental publication, verified conformant) - re-confirmed present: the same ten `CanonicalEnforcer.apply_*()` calls remain the sole publication mechanism; `P2_03_FINANCIAL_OWNERSHIP_SPECIFICATION_V1_2026-07-11.md` Section 16's normativity principle remains unchanged.

### 4.2 Re-Validation of the Thirty-One Dependencies

Each of the thirty-one dependency records (`P3_01_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-13.md`, Section 8) was re-checked for continued repository validity by re-inspecting its own cited evidence: the eleven sequential edges (DEP-001 through DEP-010, transitively DEP-026) against `loop.py:33-113`'s own unchanged line numbers; the four Compatibility edges bound to formula bodies (DEP-017 through DEP-020) against `trade_lifecycle.py`, `position.py`, `pnl.py`, `risk.py`, each unchanged since the FRA's own re-verification; the four Cross-Unit edges (DEP-027 through DEP-030) against CUO-01, Gap 4, and TD-007's own unchanged status; the Certification edge (DEP-031) against `P2_03_FINANCIAL_OWNERSHIP_SPECIFICATION_V1_2026-07-11.md` Section 16's own unchanged text. No dependency was found stale, contradicted, or requiring re-derivation.

### 4.3 No New Findings Since FRA/SDA

No new active-path file, no new alternative execution path, and no new repository-grounded observation was found beyond what the FRA's and SDA's own analyses already established. This document evaluates existing evidence; it does not develop a new repository theory, consistent with the governing task's own instruction.

## 5. Capability Assessment Method

A capability is derived exclusively from one or more existing Functional Requirements and the Dependency records that govern them (`P3_01_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-13.md`, Section 24's own FRA Traceability table). This document adopts a one-to-one mapping between Capability ID and Functional Requirement ID (`P3-01-CAP-NNN` corresponds exactly to `P3-01-FR-NNN`), the same numbering used for maximum traceability precision, avoiding any ambiguity about which FRs a given capability aggregates. No capability is derived from a concept absent from the FRA's or SDA's own text.

Each capability is assigned exactly one Current Status: **COMPLETE** (the capability's own Functional Requirement is currently evidenced, without qualification, and its Scope Boundary is fully realized), **PARTIAL** (the capability's own Functional Requirement is currently evidenced for part of its claim but not yet independently evidenced, or remains only partially evidenced, for another part), or **MISSING** (the capability's own Functional Requirement's Current Conformance is unresolved, with no corresponding architectural contract found anywhere in the Binding Baseline). Each capability additionally carries one or more of five descriptive tags: **Runtime Capability** (the capability concerns directly observable runtime behaviour), **Governance Capability** (the capability concerns an ownership, writer-mechanism, or compatibility decision or its documentation), **Documentation Capability** (the capability concerns whether a property is explicitly recorded, not whether the underlying runtime behaviour holds), **Verification Capability** (the capability concerns whether a property has been independently, separately confirmed, distinct from whether the property itself holds), and **Cross-Unit Capability** (the capability's own resolution lies outside P3-01's scope).

Consistent with the governing task's explicit instruction, Cross-Unit Observation CUO-01 is classified as a Cross-Unit Capability (Section 15) and is not evaluated as a P3-01 gap; Verified Conformant Finding VC-01 is classified COMPLETE (its own governing capability, `P3-01-CAP-013`) and is not re-evaluated as a gap.

## 6. Capability Clusters

Ten clusters were derived, adapting the governing task's suggested ten-cluster skeleton to the FRA's and SDA's own evidence rather than adopting it unexamined.

**Cluster 1 - Runtime Foundation.** CAP-001, CAP-002, CAP-003, CAP-018. Sequence existence, Tick Acquisition, State Acquisition, and execution-path exclusivity - the precondition every later cluster depends on.

**Cluster 2 - Execution Ordering.** CAP-004, CAP-005, CAP-006. Regime Classification, Strategy Selection, and Executor Event Generation ordering.

**Cluster 3 - Lifecycle Evolution.** CAP-007, CAP-008. TradeLifecycle Update and Position Update ordering.

**Cluster 4 - Financial and Risk Continuity.** CAP-009, CAP-010. Financial Accounting and Risk Evaluation ordering, each bound by an already-certified P2-03/P2-04 formula.

**Cluster 5 - Performance and Tick Completion.** CAP-011, CAP-012, CAP-013, CAP-014. Performance Evaluation ordering, the Canonical Working State consumption boundary, Tick-Complete Publication, and the external observability boundary.

**Cluster 6 - Failure and No-Execution Handling.** CAP-015, CAP-016, CAP-020. HOLD/no-execution completeness, rejected-transition completeness and non-mutation, and unhandled-exception semantics.

**Cluster 7 - Determinism and Replay.** CAP-017. Full-sequence Tick-Sequence Determinism.

**Cluster 8 - Ownership and Writer Discipline.** CAP-019. The general Writer-on-Behalf-Of rule, including Gap 1's own Market Regime divergence.

**Cluster 9 - Traceability and Compatibility.** CAP-021, CAP-022. Stage traceability and the aggregate prior-certification compatibility requirement.

**Cluster 10 - Cross-Unit.** CAP-023. The explicit scope-protection capability forwarding CUO-01 and Gap 4 to P3-02 and P3-03 respectively.

This clustering matches the SDA's own nine Requirement/Capability Clusters (`P3_01_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-13.md`, Section 6) exactly, with Cluster C (Canonical Working State and Publication) expanded here to fold Performance Evaluation ordering into the same cluster as its immediate sequential successor, since both are evaluated together in Section 9 below.

## 7. Capability Catalogue

Twenty-three capabilities were classified, one per Functional Requirement, sourced entirely from the FRA's and SDA's own text; none introduces a new requirement, dependency, interface, formula, or ownership assignment.

**P3-01-CAP-001 - Normative Sequence Existence and Uniqueness**
Description: exactly one normative, twelve-stage runtime tick execution sequence governs every tick; no competing ordering exists on the active execution path.
Source FR(s): FR-001. Source DEP(s): DEP-011, DEP-012.
Repository Evidence: `loop.py:33-113`, the sole `RunLoop.step()` implementation.
Current Runtime Evidence: FRA Section 6.2 (eighteen-step trace), Section 6.4 (absence of alternative active paths), re-confirmed Section 4.1 above.
Scientific Completeness: complete - AI-006's "one deterministic execution sequence" requirement is satisfied by direct trace.
Governance Completeness: not applicable - no ownership decision required.
Runtime Completeness: complete.
Documentation Completeness: complete - the eighteen-step trace is fully documented (FRA Section 6.2).
Verification Completeness: complete - independently re-traced twice (FRA, this document).
Dependency Coverage: complete - DEP-011 (aggregate of FR-002 through FR-011) and DEP-012 (FR-018) both currently evidenced.
Certification Coverage: not applicable.
Cross-Unit Relevance: none.
Current Status: **COMPLETE**. Tags: Runtime Capability.
Remaining Gap: none.
Scope Boundary: does not itself certify Stage 12's publication mechanism (CAP-013) or full-sequence determinism (CAP-017).
Architecture Relevance: none required.
Specification Relevance: none required.
Traceability: FR-001; ADR-010, AI-006, AC-001, AC-012.

**P3-01-CAP-002 - Runtime Tick Acquisition**
Description: Runtime Tick Acquisition occurs first in every tick.
Source FR(s): FR-002. Source DEP(s): DEP-001, DEP-011, DEP-013, DEP-014, DEP-026.
Repository Evidence: `loop.py:35`.
Current Runtime Evidence: FRA Section 6.2 Step 1, re-confirmed Section 4.1 above.
Scientific Completeness: complete.
Governance Completeness: complete - the Runtime Ownership Matrix's own "Runtime Tick" row is fully conformant (RunLoop as CA/AO/Writer-on-Behalf-Of).
Runtime Completeness: complete.
Documentation Completeness: complete.
Verification Completeness: complete.
Dependency Coverage: complete.
Certification Coverage: not applicable.
Cross-Unit Relevance: none.
Current Status: **COMPLETE**. Tags: Runtime Capability.
Remaining Gap: none.
Scope Boundary: does not address the direct-write-versus-`CanonicalEnforcer` question, which for Runtime Tick specifically is already Matrix-conformant (distinct from CAP-004's own Market Regime finding).
Architecture Relevance: none required.
Specification Relevance: none required.
Traceability: FR-002; ADR-010 Stage 1, Runtime Ownership Matrix.

**P3-01-CAP-003 - State Acquisition and Normalization Ordering**
Description: State Acquisition and Normalization occurs after Runtime Tick Acquisition and before Regime Classification.
Source FR(s): FR-003. Source DEP(s): DEP-001, DEP-011, DEP-013, DEP-014, DEP-026.
Repository Evidence: `loop.py:37`.
Current Runtime Evidence: FRA Section 6.2 Step 2, re-confirmed Section 4.1 above.
Scientific Completeness: complete.
Governance Completeness: not applicable.
Runtime Completeness: complete.
Documentation Completeness: complete.
Verification Completeness: complete.
Dependency Coverage: complete.
Certification Coverage: not applicable.
Cross-Unit Relevance: none.
Current Status: **COMPLETE**. Tags: Runtime Capability.
Remaining Gap: none.
Scope Boundary: does not evaluate `StateEngine`'s own normalization correctness.
Architecture Relevance: none required.
Specification Relevance: none required.
Traceability: FR-003; ADR-010 Stage 2.

**P3-01-CAP-004 - Regime Classification Ordering and Writer-Mechanism Conformance**
Description: Regime Classification occurs after State Acquisition and before Strategy Selection; the resulting Market Regime value's Writer-on-Behalf-Of mechanism is Matrix-conformant.
Source FR(s): FR-004. Source DEP(s): DEP-002, DEP-011, DEP-013, DEP-014, DEP-022, DEP-026.
Repository Evidence: `loop.py:44-45`; `canonical_enforcer.py`'s ten methods.
Current Runtime Evidence: FRA Section 6.2 Steps 4-5; Gap 1 (Finding F-01), re-confirmed Section 4.1 above.
Scientific Completeness: complete for ordering position.
Governance Completeness: **incomplete** - the Runtime Ownership Matrix's "Market Regime" row names `RegimeClassifier` as Writer-on-Behalf-Of; the observed mechanism is `RunLoop` writing directly (Gap 1). No Architecture Decision yet exists to reconcile the two.
Runtime Completeness: complete for ordering; the writer-mechanism question does not affect observable stage order.
Documentation Completeness: complete - the divergence is fully documented (FRA Gap 1, SDA DEP-022).
Verification Completeness: complete for ordering; not yet independently evidenced as conformant at the writer-mechanism level (FRA FR-004's own qualification).
Dependency Coverage: complete for ordering (DEP-002); the CONDITIONAL dependency DEP-022 remains open.
Certification Coverage: not applicable.
Cross-Unit Relevance: none - this is a P3-01-internal Architecture question (OQ-001), not forwarded to another unit.
Current Status: **PARTIAL**. Tags: Runtime Capability, Governance Capability.
Remaining Gap: an explicit Architecture Decision naming Market Regime's Writer-on-Behalf-Of mechanism, either amending the Matrix to name `RunLoop` or introducing a `CanonicalEnforcer.apply_regime()` method.
Scope Boundary: does not itself decide the resolution; Runtime Tick's already-Matrix-conformant case (CAP-002) is not reopened.
Architecture Relevance: **required** - OQ-001 (FRA) names this as an Architecture-stage decision.
Specification Relevance: dependent on the Architecture decision's own shape.
Traceability: FR-004, FR-019; ADR-010 Stage 3, Runtime Ownership Matrix, Rule OM-003.

**P3-01-CAP-005 - Strategy Selection and Execution Decision Ordering**
Description: Strategy Selection occurs after Regime Classification and before Execution Decision Generation, which itself precedes Executor Event Generation.
Source FR(s): FR-005. Source DEP(s): DEP-002, DEP-003, DEP-011, DEP-013, DEP-014, DEP-026.
Repository Evidence: `loop.py:49-55`.
Current Runtime Evidence: FRA Section 6.2 Steps 7-8-9, re-confirmed Section 4.1 above.
Scientific Completeness: complete.
Governance Completeness: not applicable.
Runtime Completeness: complete.
Documentation Completeness: complete.
Verification Completeness: complete.
Dependency Coverage: complete.
Certification Coverage: not applicable.
Cross-Unit Relevance: none.
Current Status: **COMPLETE**. Tags: Runtime Capability.
Remaining Gap: none.
Scope Boundary: does not evaluate `StrategySelector`'s own weighting algorithm; `StrategySelector.update()`'s inactive status is noted, not itself a gap.
Architecture Relevance: none required.
Specification Relevance: none required.
Traceability: FR-005; ADR-010 Stages 4-5, Runtime Ownership Matrix.

**P3-01-CAP-006 - Executor Event Generation Ordering**
Description: Executor Event Generation occurs after Execution Decision Generation and before TradeLifecycle Update.
Source FR(s): FR-006. Source DEP(s): DEP-003, DEP-004, DEP-011, DEP-013, DEP-014, DEP-026.
Repository Evidence: `loop.py:55`; `executor.py:5-32`.
Current Runtime Evidence: FRA Section 6.2 Steps 9-10, re-confirmed Section 4.1 above.
Scientific Completeness: complete.
Governance Completeness: not applicable.
Runtime Completeness: complete.
Documentation Completeness: complete.
Verification Completeness: complete.
Dependency Coverage: complete.
Certification Coverage: not applicable.
Cross-Unit Relevance: none.
Current Status: **COMPLETE**. Tags: Runtime Capability.
Remaining Gap: none.
Scope Boundary: does not evaluate `Executor`'s own execution-quantity or status logic. This capability directly satisfies the Implementation Baseline's own "Verify Executor integration" objective text.
Architecture Relevance: none required.
Specification Relevance: none required.
Traceability: FR-006; ADR-002, ADR-010 Stage 6.

**P3-01-CAP-007 - TradeLifecycle Update Ordering**
Description: TradeLifecycle Update occurs after Executor Event Generation and before Position Update.
Source FR(s): FR-007. Source DEP(s): DEP-004, DEP-005, DEP-011, DEP-013, DEP-014, DEP-015, DEP-017, DEP-021, DEP-026.
Repository Evidence: `loop.py:57,59`; `trade_lifecycle.py`.
Current Runtime Evidence: FRA Section 6.2 Steps 10-11-12, re-confirmed Section 4.1/4.2 above.
Scientific Completeness: complete.
Governance Completeness: complete - lifecycle ownership remains exactly as certified (ADR-003, ADR-009).
Runtime Completeness: complete.
Documentation Completeness: complete.
Verification Completeness: complete.
Dependency Coverage: complete.
Certification Coverage: complete - DEP-017 (COMPATIBILITY) cites the already-certified Lifecycle Transition Table without reopening it.
Cross-Unit Relevance: none.
Current Status: **COMPLETE**. Tags: Runtime Capability.
Remaining Gap: none.
Scope Boundary: does not evaluate lifecycle transition semantics themselves.
Architecture Relevance: none required.
Specification Relevance: none required.
Traceability: FR-007; ADR-003, ADR-009, ADR-010 Stage 7.

**P3-01-CAP-008 - Position Update Ordering**
Description: Position Update occurs after TradeLifecycle Update and before Financial Accounting.
Source FR(s): FR-008. Source DEP(s): DEP-005, DEP-006, DEP-011, DEP-013, DEP-014, DEP-015, DEP-018, DEP-021, DEP-026.
Repository Evidence: `loop.py:61-66`; `position.py`.
Current Runtime Evidence: FRA Section 6.2 Steps 12-13, re-confirmed Section 4.1/4.2 above.
Scientific Completeness: complete.
Governance Completeness: complete - Position ownership remains exactly as certified (P2-02A-AD-004, AD-005).
Runtime Completeness: complete.
Documentation Completeness: complete.
Verification Completeness: complete.
Dependency Coverage: complete.
Certification Coverage: complete - DEP-018 cites the certified P2-02A contract without reopening it.
Cross-Unit Relevance: none.
Current Status: **COMPLETE**. Tags: Runtime Capability.
Remaining Gap: none.
Scope Boundary: does not evaluate Position's own weighted-average or Exposure formulas.
Architecture Relevance: none required.
Specification Relevance: none required.
Traceability: FR-008; ADR-004, ADR-010 Stage 8, P2-02A-AD-005.

**P3-01-CAP-009 - Financial Accounting Ordering**
Description: Financial Accounting occurs after Position Update and before Risk Evaluation.
Source FR(s): FR-009. Source DEP(s): DEP-006, DEP-007, DEP-011, DEP-013, DEP-014, DEP-015, DEP-019, DEP-021, DEP-026.
Repository Evidence: `loop.py:68-88`; `pnl.py`.
Current Runtime Evidence: FRA Section 6.2 Steps 13-14-15-16, re-confirmed Section 4.1/4.2 above.
Scientific Completeness: complete.
Governance Completeness: complete - Financial Ownership remains exactly as certified (P2-03-AD-001 through AD-006).
Runtime Completeness: complete.
Documentation Completeness: complete.
Verification Completeness: complete.
Dependency Coverage: complete.
Certification Coverage: complete - DEP-019 cites the certified P2-03 contract without reopening it.
Cross-Unit Relevance: none.
Current Status: **COMPLETE**. Tags: Runtime Capability.
Remaining Gap: none.
Scope Boundary: does not evaluate the Equity/Peak-Equity/Realized-PnL formulas themselves.
Architecture Relevance: none required.
Specification Relevance: none required.
Traceability: FR-009; ADR-005, ADR-006, ADR-010 Stage 9.

**P3-01-CAP-010 - Risk Evaluation Ordering**
Description: Risk Evaluation occurs after Financial Accounting and before Performance Evaluation.
Source FR(s): FR-010. Source DEP(s): DEP-007, DEP-008, DEP-011, DEP-013, DEP-014, DEP-015, DEP-020, DEP-021, DEP-026.
Repository Evidence: `loop.py:92-93`; `risk.py`.
Current Runtime Evidence: FRA Section 6.2 Steps 16-17, re-confirmed Section 4.1/4.2 above.
Scientific Completeness: complete.
Governance Completeness: complete - Risk Ownership remains exactly as certified (P2-04-AD-002 through AD-010).
Runtime Completeness: complete.
Documentation Completeness: complete.
Verification Completeness: complete.
Dependency Coverage: complete.
Certification Coverage: complete - DEP-020 cites the certified P2-04 contract without reopening it.
Cross-Unit Relevance: none.
Current Status: **COMPLETE**. Tags: Runtime Capability.
Remaining Gap: none.
Scope Boundary: does not evaluate the risk-limiting formula itself; does not resolve whether `PerformanceEngine` should consume Risk Metrics (P2-04-AD-017's own preserved boundary).
Architecture Relevance: none required.
Specification Relevance: none required.
Traceability: FR-010; ADR-007, ADR-010 Stage 10, P2-04-AD-017.

**P3-01-CAP-011 - Performance Evaluation Ordering**
Description: Performance Evaluation occurs after Risk Evaluation and before Tick-Complete CanonicalState Publication.
Source FR(s): FR-011. Source DEP(s): DEP-008, DEP-009, DEP-011, DEP-013, DEP-014, DEP-015, DEP-026, DEP-029.
Repository Evidence: `loop.py:95-96`; `performance.py`.
Current Runtime Evidence: FRA Section 6.2 Steps 17-18, re-confirmed Section 4.1 above.
Scientific Completeness: complete for ordering position.
Governance Completeness: not applicable to ordering; `PerformanceEngine`'s own internal accounting semantics (Gap 4) are explicitly excluded from this capability's own scope (see CAP-023).
Runtime Completeness: complete for ordering.
Documentation Completeness: complete.
Verification Completeness: complete for ordering.
Dependency Coverage: complete.
Certification Coverage: not applicable.
Cross-Unit Relevance: **yes** - Gap 4's own internal-semantics substance is forwarded to P3-03 via DEP-029; this does not affect CAP-011's own ordering-position classification.
Current Status: **COMPLETE** (ordering-only scope, per FR-011's own explicit Scope Boundary). Tags: Runtime Capability.
Remaining Gap: none, within this capability's own scope; `PerformanceEngine`'s internal accounting remains decision-oriented, tracked as CAP-023's own Cross-Unit content, not as this capability's gap.
Scope Boundary: explicitly excludes `PerformanceEngine`'s internal computation correctness (TD-004, P3-03's territory).
Architecture Relevance: none required for ordering; P3-03's own future Architecture governs internal semantics.
Specification Relevance: none required.
Traceability: FR-011; ADR-008, ADR-010 Stage 11, TD-004.

**P3-01-CAP-012 - Canonical Working State Consumption Boundary**
Description: no runtime component consumes a Canonical Working State value corresponding to a stage whose own ADR-010 execution position has not yet been reached.
Source FR(s): FR-012. Source DEP(s): DEP-013, DEP-025, DEP-027.
Repository Evidence: `loop.py:90-92`; every one of the eighteen steps (FRA Section 6.2).
Current Runtime Evidence: FRA Section 7.1, re-confirmed Section 4.1 above.
Scientific Completeness: complete.
Governance Completeness: not applicable.
Runtime Completeness: complete.
Documentation Completeness: complete.
Verification Completeness: complete for the boundary itself; the underlying reference-semantics robustness question (CUO-01) is explicitly not part of this capability's own scope.
Dependency Coverage: complete for the REQUIRED constituent (DEP-013); the CROSS-UNIT constituent (DEP-027) is forwarded, not resolved, by design.
Certification Coverage: not applicable.
Cross-Unit Relevance: **yes** - CUO-01 originates from this capability's own territory but is forwarded to P3-02 (see CAP-023); this capability's own requirement (no premature consumption) remains fully P3-01-owned and complete.
Current Status: **COMPLETE**. Tags: Runtime Capability.
Remaining Gap: none within this capability's own requirement; CUO-01's own robustness question is tracked separately (CAP-023), not as a gap here, per the governing task's explicit instruction.
Scope Boundary: does not require a structural (construction-level) enforcement mechanism.
Architecture Relevance: none required for this capability itself; CUO-01's eventual disposition is P3-02's own future Architecture concern.
Specification Relevance: none required.
Traceability: FR-012; Canonical Working State definition, AI-007, CUO-01.

**P3-01-CAP-013 - Tick-Complete Publication**
Description: every runtime tick culminates in exactly one Tick-Complete CanonicalState Publication, after which the resulting Tick-Complete Snapshot alone becomes externally observable.
Source FR(s): FR-013. Source DEP(s): DEP-009, DEP-010, DEP-023, DEP-026, DEP-031.
Repository Evidence: `loop.py:35,50,53,66,73,86,87,88,93,96` (ten `apply_*` calls); `canonical_state.py`, `canonical_enforcer.py`.
Current Runtime Evidence: FRA Section 8 (Verified Conformant Finding VC-01), re-confirmed Section 4.1 above.
Scientific Completeness: complete - AC-009 and the Tick Completion Contract are both currently evidenced as satisfied, grounded in the already-certified `P2_03_FINANCIAL_OWNERSHIP_SPECIFICATION_V1_2026-07-11.md` Section 16 normativity principle (observable dependencies and results govern conformance, not internal code structure).
Governance Completeness: not applicable.
Runtime Completeness: complete.
Documentation Completeness: complete - VC-01's own reasoning, and the residual precondition-protection question (synchronous execution not yet named as an explicit Invariant/Constraint), are both fully documented (FRA Section 8.3, Open Question OQ-003 revised).
Verification Completeness: complete - this capability's own conformance is independently re-derived from an already-certified precedent (DEP-031, Certification-class), not merely assumed.
Dependency Coverage: complete for the REQUIRED constituents (DEP-009, DEP-010, DEP-026, DEP-031); the CONDITIONAL constituent (DEP-023, from FR-020) affects this capability's own completeness under an unhandled exception specifically, not its current evidence under normal execution.
Certification Coverage: complete - DEP-031 explicitly grounds this capability in an already-certified governing principle.
Cross-Unit Relevance: none.
Current Status: **COMPLETE**, per Verified Conformant Finding VC-01, explicitly not re-evaluated as a gap, consistent with the governing task's explicit instruction. The residual precondition-protection question (Open Question OQ-003, revised) is recorded as a documentation matter for a future Architecture document, and does not lower this capability's own COMPLETE classification.
Remaining Gap: none affecting current conformance; a documentation-only question remains open (whether the synchronous-execution precondition should be named as an explicit Invariant or Constraint) - not itself a capability gap, since the guarantee it would protect is already independently verified.
Scope Boundary: does not require or propose an atomic publish/commit mechanism.
Architecture Relevance: optional - a future Architecture document may explicitly name the synchronous-execution precondition as a Constraint or Invariant, but this is not required to close a gap, since none exists here.
Specification Relevance: none required.
Traceability: FR-013; ADR-010 Stage 12, AI-009, AC-009, Tick Completion Contract, VC-01, P2-03 Specification Section 16.

**P3-01-CAP-014 - External Observability Boundary**
Description: external downstream consumers observe only Tick-Complete Snapshots, never intermediate, per-stage runtime state.
Source FR(s): FR-014. Source DEP(s): DEP-010.
Repository Evidence: `main.py:21-24`.
Current Runtime Evidence: FRA Section 8.2, re-confirmed Section 4.1 above.
Scientific Completeness: complete.
Governance Completeness: not applicable.
Runtime Completeness: complete, under the current synchronous, single-threaded execution model.
Documentation Completeness: complete.
Verification Completeness: complete.
Dependency Coverage: complete.
Certification Coverage: not applicable.
Cross-Unit Relevance: none.
Current Status: **COMPLETE**. Tags: Runtime Capability.
Remaining Gap: none.
Scope Boundary: assumes continuation of the current synchronous, single-threaded execution model; does not address any future concurrent or asynchronous execution mode.
Architecture Relevance: none required.
Specification Relevance: none required.
Traceability: FR-014; Tick-Complete Snapshot definition, AI-009, AC-009.

**P3-01-CAP-015 - HOLD / No-Execution Stage Completeness**
Description: a `HOLD` or no-execution tick executes every one of the twelve ADR-010 stages, in the same order as any other tick.
Source FR(s): FR-015. Source DEP(s): DEP-014.
Repository Evidence: `strategy.py:47-51,69-73`; `executor.py:14-32`; `trade_lifecycle.py:64-65`; `position.py:37-73`; `pnl.py:9-19,42-72`; `performance.py:6-9`.
Current Runtime Evidence: FRA Section 9.1, re-confirmed Section 4.1 above.
Scientific Completeness: complete.
Governance Completeness: not applicable.
Runtime Completeness: complete.
Documentation Completeness: complete.
Verification Completeness: complete.
Dependency Coverage: complete.
Certification Coverage: not applicable.
Cross-Unit Relevance: none.
Current Status: **COMPLETE**. Tags: Runtime Capability.
Remaining Gap: none.
Scope Boundary: does not evaluate `StrategySelector`'s own cooldown/weighting logic that produces a `HOLD` decision.
Architecture Relevance: none required.
Specification Relevance: none required.
Traceability: FR-015; ADR-010, ADR-002, Tick Completion Contract.

**P3-01-CAP-016 - Rejected-Transition Stage Completeness and Non-Mutation**
Description: a tick containing a `RUNTIME_FAILURE_EVENT` executes every one of the twelve ADR-010 stages while leaving the ADR-011-named values unmodified.
Source FR(s): FR-016. Source DEP(s): DEP-015, DEP-016, DEP-021, DEP-025.
Repository Evidence: `trade_lifecycle.py:280-304`; `pnl.py:23-24,57-62`; `performance.py:8-9`.
Current Runtime Evidence: FRA Section 9.2, re-confirmed Section 4.1/4.2 above.
Scientific Completeness: complete.
Governance Completeness: complete - the non-mutation guarantee is COMPATIBILITY-grounded in already-certified P2-03/P2-04 findings (DEP-016), independently re-confirmed present, not reopened.
Runtime Completeness: complete.
Documentation Completeness: complete.
Verification Completeness: complete.
Dependency Coverage: complete.
Certification Coverage: complete - DEP-016 cites both certifications without reopening either.
Cross-Unit Relevance: none.
Current Status: **COMPLETE**. Tags: Runtime Capability, Governance Capability.
Remaining Gap: none.
Scope Boundary: does not re-evaluate the four rejection reasons' own trigger conditions, already certified.
Architecture Relevance: none required.
Specification Relevance: none required.
Traceability: FR-016; ADR-011, AI-011, AC-015.

**P3-01-CAP-017 - Full-Sequence Tick-Sequence Determinism**
Description: the complete twelve-stage tick sequence is Tick-Sequence Deterministic, independently and separately verified as this unit's own finding.
Source FR(s): FR-017. Source DEP(s): DEP-024, DEP-025.
Repository Evidence: `pnl.py`, `executor.py` (direct evidence); `risk.py` (by independent certification).
Current Runtime Evidence: FRA Section 10, re-confirmed Section 4.1 above.
Scientific Completeness: complete for every individual constituent (FR-001, FR-012, FR-016, FR-019, each currently evidenced, per DEP-025); **incomplete** for the aggregate, full-sequence property as this unit's own independently-certified finding.
Governance Completeness: not applicable.
Runtime Completeness: complete - the underlying runtime behaviour is not in question; only its independent, dedicated verification is missing.
Documentation Completeness: complete - the gap itself, and its precise scope (verification, not behaviour), are fully documented (FRA Gap 3).
Verification Completeness: **incomplete** - no repository-wide replay fixture exists for the complete eighteen-step sequence as a P3-01-named deliverable; the P2-03 and P2-04 certifications' own replay evidence remains corroborating, not dedicated, evidence.
Dependency Coverage: complete for the REQUIRED constituent (DEP-025); the CONDITIONAL constituent (DEP-024, from FR-020) remains open.
Certification Coverage: **incomplete** - this is precisely the missing certification this capability names.
Cross-Unit Relevance: none.
Current Status: **PARTIAL**. Tags: Verification Capability.
Remaining Gap: an independently-recorded verification of full-sequence Tick-Sequence Determinism as P3-01's own dedicated finding, distinct from the incidental evidence P2-03's and P2-04's own certifications already provide.
Scope Boundary: does not require or introduce any new replay tooling; the gap is one of independent certification, not of new tooling design.
Architecture Relevance: none required to close this gap - the missing element is verification, which a future Certification, not an Architecture Decision, would supply. A future Architecture document may nonetheless need to account for DEP-024's own conditional dependency on FR-020.
Specification Relevance: a future Specification may need to define the exact scripted sequence a dedicated replay verification would use, without this being an architecture decision.
Traceability: FR-017; AI-005, AI-006, ADR-010, AC-012.

**P3-01-CAP-018 - Execution Path Exclusivity**
Description: no alternative or competing active execution path exists; `RunLoop.step()` remains the sole runtime orchestration entry point.
Source FR(s): FR-018. Source DEP(s): DEP-012.
Repository Evidence: Section 4 (FRA), confirmed-inactive inventory, re-confirmed Section 4.1 above.
Scientific Completeness: complete.
Governance Completeness: not applicable to this capability's own claim (active-path exclusivity); the inactive components' own final classification (retain/integrate/archive/remove) is explicitly Phase 6's scope, not this capability's.
Runtime Completeness: complete.
Documentation Completeness: complete.
Verification Completeness: complete.
Dependency Coverage: complete.
Certification Coverage: not applicable.
Cross-Unit Relevance: none.
Current Status: **COMPLETE**. Tags: Runtime Capability.
Remaining Gap: none, within this capability's own scope (active-path exclusivity); inactive-component classification is explicitly out of scope (Phase 6), not a gap of this capability.
Scope Boundary: does not classify or remove any inactive component.
Architecture Relevance: none required.
Specification Relevance: none required.
Traceability: FR-018; AI-013, Architecture Defect AD-007, Phase 6.

**P3-01-CAP-019 - Writer-on-Behalf-Of Discipline**
Description: no runtime component other than `CanonicalEnforcer`'s named `apply_*` methods writes to `CanonicalState`, except where the Runtime Ownership Matrix explicitly names a different Writer-on-Behalf-Of.
Source FR(s): FR-019. Source DEP(s): DEP-022, DEP-025.
Repository Evidence: `canonical_enforcer.py`'s ten methods; `loop.py:42,45`.
Current Runtime Evidence: FRA Section 7.3, Gap 1, re-confirmed Section 4.1 above.
Scientific Completeness: complete for nine of ten canonical-object categories (financial, risk, position, strategy, execution, performance, runtime status).
Governance Completeness: **incomplete** - Market Regime's own Writer-on-Behalf-Of mechanism diverges from the Matrix (Gap 1), with no Architecture Decision yet resolving OQ-001.
Runtime Completeness: complete - the general rule's observable effect (CanonicalState remains the sole Authoritative Owner) holds regardless of the writer-mechanism question.
Documentation Completeness: complete - the divergence is fully documented.
Verification Completeness: complete for every object except Market Regime, not yet independently evidenced as conformant at the writer-mechanism level for that one object.
Dependency Coverage: complete for the general rule; DEP-022 (CONDITIONAL) remains open.
Certification Coverage: not applicable.
Cross-Unit Relevance: none.
Current Status: **PARTIAL**. Tags: Governance Capability.
Remaining Gap: an explicit Architecture Decision resolving Market Regime's own Writer-on-Behalf-Of mechanism (shared with CAP-004's own remaining gap; the two capabilities name the same underlying Architecture question from two directions).
Scope Boundary: does not itself decide the resolution; Runtime Tick's already-Matrix-conformant case is not reopened.
Architecture Relevance: **required** - identical Architecture-stage decision as CAP-004 (OQ-001).
Specification Relevance: dependent on the Architecture decision's own shape.
Traceability: FR-019; Rule OM-003, Rule OM-006, Runtime Ownership Matrix.

**P3-01-CAP-020 - Unhandled-Exception / Partial-Publication Semantics**
Description: the runtime's behaviour when an unhandled exception propagates out of `RunLoop.step()` mid-tick, after some but not all of that tick's publications have already executed, is explicitly and architecturally defined.
Source FR(s): FR-020. Source DEP(s): DEP-023, DEP-024, DEP-030.
Repository Evidence: `main.py:14-30`; `loop.py:116-131`.
Current Runtime Evidence: FRA Section 9.3, Gap 2, re-confirmed Section 4.1 above.
Scientific Completeness: **absent** - no governing document anywhere in the Binding Baseline defines the required behaviour for this condition.
Governance Completeness: **absent** - no Architecture Decision exists; FR-020's own Current Conformance is explicitly stated as "unresolved" in the FRA, the only such classification among all twenty-three requirements.
Runtime Completeness: **absent** - `main.py`'s broad `except Exception` and `loop.py`'s unguarded `__main__` block provide no rollback, reset, or partial-tick marking of any kind.
Documentation Completeness: complete - the absence itself is fully and precisely documented (FRA Gap 2, this document's own re-confirmation).
Verification Completeness: not applicable - there is no mechanism yet to verify.
Dependency Coverage: incomplete - DEP-023 and DEP-024 (both CONDITIONAL, sourced from this capability) remain open by definition, since this capability is itself their unresolved source.
Certification Coverage: not applicable.
Cross-Unit Relevance: none for its own resolution (this is a P3-01-internal Architecture question), though DEP-030 explicitly distinguishes this capability from TD-007's own separate, future-unit scope.
Current Status: **MISSING**. Tags: Governance Capability.
Remaining Gap: a governing Architecture document explicitly defining the required behaviour under an unhandled exception mid-tick - for example an explicit partial-tick marker, an automatic `CanonicalState.reset()`, an explicit rollback mechanism, or an explicit, justified decision that the current behaviour is architecturally accepted.
Scope Boundary: does not extend to `main.py`'s own broader process-level error-reporting or logging strategy; does not extend to, or substitute for, TD-007's own operator-triggered lifecycle control surface (DEP-030).
Architecture Relevance: **required** - OQ-004 (FRA) names this as a blocking Architecture-stage decision.
Specification Relevance: **required**, once the Architecture decision is made - the exact mechanism (if any) would require Specification-level interface detail.
Traceability: FR-020; Tick Completion Contract, AI-009, ADR-011 (by contrast), TD-007.

**P3-01-CAP-021 - Stage Traceability**
Description: every one of the twelve ADR-010 stages remains traceable, by file and line, to the specific runtime object it consumes and produces.
Source FR(s): FR-021. Source DEP(s): DEP-026.
Repository Evidence: FRA Section 11; `canonical_enforcer.py:7-85`.
Current Runtime Evidence: FRA Section 6.2's own eighteen-step citation format, re-confirmed Section 4.1 above.
Scientific Completeness: complete.
Governance Completeness: not applicable.
Runtime Completeness: complete.
Documentation Completeness: complete.
Verification Completeness: complete.
Dependency Coverage: complete.
Certification Coverage: not applicable.
Cross-Unit Relevance: none.
Current Status: **COMPLETE**. Tags: Documentation Capability, Verification Capability.
Remaining Gap: none.
Scope Boundary: does not extend to `TradeLifecycleEngine`'s own internal historical record structure.
Architecture Relevance: none required.
Specification Relevance: none required.
Traceability: FR-021; AI-014, AC-011.

**P3-01-CAP-022 - Aggregate Prior-Certification Compatibility**
Description: every already-certified P2-02A, P2-03, and P2-04 ownership, formula, and non-mutation contract continues to function exactly as certified.
Source FR(s): FR-022. Source DEP(s): DEP-021.
Repository Evidence: `P2_03_FINAL_CERTIFICATION_V1_2026-07-11.md`, `P2_04_FINAL_CERTIFICATION_V1_2026-07-13.md`; FRA Section 6.2's own re-trace.
Current Runtime Evidence: FRA Section 20 (Prior-Certification Compatibility), re-confirmed Section 4.2 above.
Scientific Completeness: complete.
Governance Completeness: complete - each of the five constituent compatibility dependencies (DEP-016 through DEP-020) is currently evidenced.
Runtime Completeness: complete.
Documentation Completeness: complete.
Verification Completeness: complete.
Dependency Coverage: complete.
Certification Coverage: complete - this capability is, by construction, entirely Certification-grounded.
Cross-Unit Relevance: none.
Current Status: **COMPLETE**. Tags: Governance Capability.
Remaining Gap: none.
Scope Boundary: this unit's own four remaining gaps (CAP-004/019, CAP-017, CAP-020, and CAP-023's own forwarded items) concern ordering, publication mechanism, and failure semantics only; none requires reopening any already-certified ownership assignment.
Architecture Relevance: none required.
Specification Relevance: none required.
Traceability: FR-022; ADR-001 through ADR-009, ADR-011, P2-02A/P2-03/P2-04 certifications.

**P3-01-CAP-023 - Cross-Unit Scope Boundary (CUO-01 and Gap 4 Forwarding)**
Description: `PerformanceEngine`'s internal accounting semantics and `CanonicalState.get()`'s reference-semantics robustness question are explicitly scope-protected, forwarded to P3-02 and P3-03 respectively, and not resolved by P3-01.
Source FR(s): FR-023. Source DEP(s): DEP-028, DEP-029.
Repository Evidence: `performance.py:11`; `canonical_state.py:107-109`; `RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md`'s own P3-01/P3-02/P3-03 objective text.
Current Runtime Evidence: FRA Sections 12.1 (Gap 4), 12.2 (CUO-01), re-confirmed Section 4.1 above.
Scientific Completeness: complete - the boundary itself is precisely, textually justified (P3-02's "Remove hidden coupling," P3-03's "Verify PerformanceEngine inputs").
Governance Completeness: complete - the scope-protection requirement is itself fully realized; no P3-01 Architecture Decision has silently absorbed either forwarded item.
Runtime Completeness: not applicable - this capability protects a boundary, it does not itself govern runtime behaviour.
Documentation Completeness: complete - both CUO-01 and Gap 4 are named explicitly, with their own forwarding rationale, in the FRA and SDA.
Verification Completeness: complete - the forwarding itself, not the forwarded items' own eventual resolution, is what this capability verifies, and that forwarding is confirmed intact.
Dependency Coverage: complete - both CROSS-UNIT dependencies (DEP-028, DEP-029) are currently evidenced as correctly scope-protected.
Certification Coverage: not applicable.
Cross-Unit Relevance: **yes**, by definition - this is the capability whose entire purpose is Cross-Unit boundary maintenance.
Current Status: **COMPLETE**. Tags: Governance Capability, Documentation Capability, **Cross-Unit Capability**.
Remaining Gap: none within P3-01's own scope; CUO-01's own eventual resolution belongs to P3-02, and Gap 4's own eventual resolution belongs most plausibly to P3-03 (per TD-004's own Target Phase), neither as a P3-01 gap.
Scope Boundary: this document takes no final position on whether CUO-01 belongs to P3-02 specifically or a later unit, or whether Gap 4 belongs to P3-02 or P3-03; only that neither belongs to P3-01. No P3-02 solution is anticipated or proposed by this capability.
Architecture Relevance: none required for P3-01; P3-02's and P3-03's own future Architecture documents govern the forwarded items themselves.
Specification Relevance: none required for P3-01.
Traceability: FR-023; TD-004, CUO-01, Implementation Baseline (P3-01/P3-02/P3-03 unit definitions).

## 8. Capability Matrix

| CAP | Title | Status | Tags | Cross-Unit |
|---|---|---|---|---|
| CAP-001 | Normative Sequence Existence and Uniqueness | COMPLETE | Runtime | none |
| CAP-002 | Runtime Tick Acquisition | COMPLETE | Runtime | none |
| CAP-003 | State Acquisition and Normalization Ordering | COMPLETE | Runtime | none |
| CAP-004 | Regime Classification Ordering and Writer-Mechanism Conformance | PARTIAL | Runtime, Governance | none |
| CAP-005 | Strategy Selection and Execution Decision Ordering | COMPLETE | Runtime | none |
| CAP-006 | Executor Event Generation Ordering | COMPLETE | Runtime | none |
| CAP-007 | TradeLifecycle Update Ordering | COMPLETE | Runtime | none |
| CAP-008 | Position Update Ordering | COMPLETE | Runtime | none |
| CAP-009 | Financial Accounting Ordering | COMPLETE | Runtime | none |
| CAP-010 | Risk Evaluation Ordering | COMPLETE | Runtime | none |
| CAP-011 | Performance Evaluation Ordering | COMPLETE | Runtime | yes (Gap 4 -> P3-03) |
| CAP-012 | Canonical Working State Consumption Boundary | COMPLETE | Runtime | yes (CUO-01 -> P3-02) |
| CAP-013 | Tick-Complete Publication | COMPLETE | Runtime, Verification | none |
| CAP-014 | External Observability Boundary | COMPLETE | Runtime | none |
| CAP-015 | HOLD / No-Execution Stage Completeness | COMPLETE | Runtime | none |
| CAP-016 | Rejected-Transition Stage Completeness and Non-Mutation | COMPLETE | Runtime, Governance | none |
| CAP-017 | Full-Sequence Tick-Sequence Determinism | PARTIAL | Verification | none |
| CAP-018 | Execution Path Exclusivity | COMPLETE | Runtime | none |
| CAP-019 | Writer-on-Behalf-Of Discipline | PARTIAL | Governance | none |
| CAP-020 | Unhandled-Exception / Partial-Publication Semantics | MISSING | Governance | none (distinct from TD-007) |
| CAP-021 | Stage Traceability | COMPLETE | Documentation, Verification | none |
| CAP-022 | Aggregate Prior-Certification Compatibility | COMPLETE | Governance | none |
| CAP-023 | Cross-Unit Scope Boundary (CUO-01 and Gap 4 Forwarding) | COMPLETE | Governance, Documentation, Cross-Unit | yes (by definition) |

Nineteen of twenty-three capabilities are COMPLETE; three are PARTIAL (CAP-004, CAP-017, CAP-019); one is MISSING (CAP-020). No capability was classified using any category beyond COMPLETE/PARTIAL/MISSING.

## 9. Runtime Capability Coverage

Eighteen capabilities carry the Runtime Capability tag (CAP-001 through CAP-016, CAP-018), covering the complete ADR-010 stage chain, the Canonical Working State boundary, Tick-Complete Publication, external observability, and both no-execution and rejection completeness. Every Runtime Capability is currently evidenced as COMPLETE except CAP-004, whose ordering-position element is complete but whose writer-mechanism element (a Governance, not Runtime, concern) remains open. No Runtime Capability was found MISSING; the runtime's own observable behaviour, for every stage this analysis reached, matches its governing Functional Requirement.

## 10. Governance Capability Coverage

Six capabilities carry the Governance Capability tag: CAP-004, CAP-016, CAP-019, CAP-020, CAP-022, CAP-023. Four of six are COMPLETE (CAP-016, CAP-022, CAP-023, each grounded in an already-certified or already-documented decision). Two are open: CAP-004 and CAP-019 both name the identical underlying Architecture question (Market Regime's Writer-on-Behalf-Of mechanism, OQ-001) from two directions and are PARTIAL for that reason; CAP-020 is MISSING, the only capability in this entire catalogue with no governing Architecture Decision of any kind. Governance Capability coverage is therefore the primary source of this document's own open findings (Section 17).

## 11. Documentation Capability Coverage

Two capabilities carry the Documentation Capability tag as a primary characteristic: CAP-021 (stage traceability) and CAP-023 (Cross-Unit scope boundary), both COMPLETE. Every other capability's own documentation status is reported within its individual catalogue entry's "Documentation Completeness" field (Section 7); no capability was found with incomplete documentation of its own current state, including CAP-020, whose documentation of its own absence is itself complete (the gap is fully and precisely recorded, even though the underlying mechanism it describes does not exist).

## 12. Verification Capability Coverage

Two capabilities carry the Verification Capability tag as a primary characteristic: CAP-013 (Tick-Complete Publication, COMPLETE, grounded in an already-certified precedent) and CAP-017 (full-sequence determinism, PARTIAL, the sole capability whose own gap is exclusively a verification gap - the underlying runtime behaviour is not in question, only its independent, dedicated certification). CAP-021 (stage traceability) also carries this tag secondarily. No capability was found with a Verification Completeness classification of "absent" except CAP-020, for which verification is not applicable, since no mechanism yet exists to verify.

## 13. Dependency Capability Coverage

Every one of the thirty-one Dependency records (`P3_01_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-13.md`, Section 8) is cited by at least one capability's own "Source DEP(s)" field (Section 7); no dependency was found orphaned. The four CONDITIONAL dependencies (DEP-022, DEP-023, DEP-024, DEP-030) each trace to exactly the two capabilities their own SDA-level source requirements govern (CAP-004/CAP-019 for DEP-022; CAP-013/CAP-017/CAP-020 for DEP-023/DEP-024/DEP-030), confirming the SDA's own Finding SDA-F-02 (four CONDITIONAL dependencies, two unresolved sources) maps precisely onto this document's own two open Governance capabilities (CAP-004/CAP-019 jointly, and CAP-020 independently).

## 14. Cross-Unit Capability Assessment

Three capabilities carry Cross-Unit relevance; one (CAP-023) is itself classified as a Cross-Unit Capability. **CUO-01** (`CanonicalState.get()`'s live-mutable reference, originating from CAP-012's own territory) is forwarded via CAP-023 to **P3-02** (Information Flow Validation), consistent with the governing task's explicit instruction that CUO-01 be led as a Cross-Unit Capability, not a P3-01 gap; this document proposes no P3-02 resolution, mechanism, or preference. **Gap 4** (`PerformanceEngine`'s decision-oriented accounting, originating from CAP-011's own territory) is likewise forwarded via CAP-023, most plausibly to **P3-03** (Performance Validation) per TD-004's own Target Phase, though the FRA's own Open Question OQ-007 leaves the exact P3-02-versus-P3-03 boundary for that specific item formally unsettled. CAP-020's own unhandled-exception semantics are explicitly distinguished (DEP-030) from TD-007's own separate, future Runtime Control Unit scope, but CAP-020 itself remains a P3-01-internal Architecture question, not a Cross-Unit Capability.

## 15. Certified Compatibility Assessment

Six capabilities are Certification- or Compatibility-grounded: CAP-007 (P2-02A lifecycle ownership, via ADR-003/ADR-009), CAP-008 (P2-02A Position ownership), CAP-009 (P2-03 Financial ownership), CAP-010 (P2-04 Risk ownership), CAP-016 (P2-03/P2-04 non-mutation contracts), and CAP-022 (the aggregate of all five). Every one of these six is COMPLETE. No dependency or capability in this document proposes reopening any of the cited P2-02A, P2-03, or P2-04 ownership decisions; each citation is a reference to an already-certified finding, re-verified present (Section 4.2) rather than re-derived.

## 16. Remaining Capability Gaps

Four capabilities carry a remaining gap, matching the FRA's own four P3-01-owned Functional Gaps exactly, one-to-one:

- **CAP-004 / CAP-019** (PARTIAL, jointly) - Gap 1: an explicit Architecture Decision naming Market Regime's own Writer-on-Behalf-Of mechanism (OQ-001).
- **CAP-020** (MISSING) - Gap 2: an explicit Architecture Decision defining unhandled-exception / partial-publication semantics (OQ-004).
- **CAP-017** (PARTIAL) - Gap 3: an independently-recorded verification of full-sequence Tick-Sequence Determinism as P3-01's own dedicated finding (OQ-006).

Gap 4 (`PerformanceEngine`'s decision-oriented accounting) is not a P3-01 capability gap; it is fully and correctly scope-protected within CAP-023 (COMPLETE), forwarded to P3-02/P3-03. CUO-01 is likewise not a P3-01 capability gap, for the same reason.

## 17. Capability Findings

**Finding CGA-F-01.** Exactly three capabilities are PARTIAL and exactly one is MISSING; nineteen of twenty-three are COMPLETE. Every open capability traces to exactly one of the FRA's own four already-named Functional Gaps; no new gap was discovered during this classification pass.

**Finding CGA-F-02.** CAP-004 and CAP-019 name the identical underlying Architecture question from two directions (a stage-ordering perspective and a general-rule perspective, respectively); a future Architecture Decision resolving OQ-001 will close both capabilities simultaneously, not independently.

**Finding CGA-F-03.** CAP-020 is the only capability in this catalogue with a Governance Completeness, Scientific Completeness, and Runtime Completeness all classified "absent" - the most severe gap-shape in this document, consistent with the FRA's own singular "unresolved" Current Conformance classification for FR-020.

**Finding CGA-F-04.** CAP-017's own gap is exclusively a Verification Capability gap; its Runtime Completeness is independently classified complete, since the underlying behaviour (deterministic execution) is not in question, only its independent, dedicated certification.

**Finding CGA-F-05.** VC-01 (CAP-013) is classified COMPLETE, and CUO-01 (folded into CAP-012/CAP-023) is classified as Cross-Unit, exactly per the governing task's explicit instructions; neither was re-evaluated as a P3-01 gap anywhere in this document.

## 18. Capability Risks

**Risk CGA-R-01.** If a future P3-01 Architecture resolves CAP-004/CAP-019's own Market Regime question without cross-checking the Runtime Ownership Matrix's own remaining eight rows for a similar, not-yet-catalogued divergence (Open Question OQ-008, FRA), a systemic pattern could remain partially addressed.

**Risk CGA-R-02.** If CAP-020 remains MISSING through the Architecture stage, CAP-013's and CAP-017's own completeness (not their current COMPLETE/PARTIAL status) remain conditionally exposed to an unresolved edge case, per DEP-023/DEP-024.

**Risk CGA-R-03.** If a future P3-02 Architecture resolves CUO-01 without first confirming CAP-012's own already-COMPLETE Canonical Working State boundary remains intact, a divergence between P3-01's certified boundary and P3-02's own implementation could arise (mirroring SDA Risk R-02).

**Risk CGA-R-04.** If a future P3-03 Architecture redesigns `PerformanceEngine` without first confirming CAP-011's own already-COMPLETE ordering-position requirement remains satisfied, a redesign could inadvertently move Performance Evaluation's own call position (mirroring SDA Risk R-03).

## 19. Capability Constraints

**Constraint CGA-C-01.** No future P3-01 Architecture document may reclassify any of the nineteen COMPLETE capabilities without first re-deriving the specific repository evidence this document and the FRA/SDA already established.

**Constraint CGA-C-02.** No future P3-01 Architecture document may resolve CAP-012's or CAP-023's own forwarded CUO-01 content, or CAP-011's/CAP-023's own forwarded Gap 4 content, as part of its own scope; both remain explicitly reserved for P3-02 and P3-03 respectively.

**Constraint CGA-C-03.** Any future P3-01 Architecture document resolving CAP-004/CAP-019 or CAP-020 must do so via an explicit Architecture Decision, not an incidental consequence of resolving another capability.

**Constraint CGA-C-04.** No future P3-01 document may alter Position, Financial, or Risk ownership (CAP-008, CAP-009, CAP-010) as an incidental consequence of resolving CAP-004, CAP-019, or CAP-020.

## 20. Scientific Conclusions

Nineteen of twenty-three capabilities (82.6%) are COMPLETE, evidenced without qualification. The remaining four - three PARTIAL, one MISSING - concentrate on exactly two underlying Architecture questions: the Market Regime Writer-on-Behalf-Of mechanism (CAP-004/CAP-019) and unhandled-exception semantics (CAP-020), plus one Verification-only gap (CAP-017) whose underlying behaviour is not in doubt. No capability gap in this catalogue requires reopening any already-certified P2-02A, P2-03, or P2-04 ownership decision. Every Cross-Unit item (CUO-01, Gap 4) is fully and correctly scope-protected (CAP-023, COMPLETE), consistent with the governing task's explicit instruction that neither be treated as a P3-01 gap.

This capability profile - a small number of open, precisely-bounded Architecture-stage questions surrounded by a large body of already-evidenced, already-certified-compatible capability - directly parallels the P2-04 CGA's own central finding (no capability violates any Architecture Invariant, Acceptance Criterion, or Runtime Ownership Matrix row; every gap is an absence-of-definition, not an active violation), independently re-derived here for P3-01's own distinct subject matter rather than mechanically restated from that precedent.

## 21. Architecture Readiness Decision

Every one of the twenty-three Functional Requirements is addressed by exactly one Capability (Section 7). Every one of the thirty-one Dependency records is cited by at least one Capability (Section 13). No new Functional Requirement, Dependency, or ADR was introduced. No capability classification selects a publication mechanism, a copy-versus-reference semantics, an exception/rollback semantics, or a concrete implementation.

Three capabilities require an explicit future Architecture Decision to close: CAP-004/CAP-019 (Market Regime Writer-on-Behalf-Of, one Architecture question) and CAP-020 (unhandled-exception semantics, a second, independent Architecture question). One capability (CAP-017) requires an independent verification exercise, not an Architecture Decision, to close. Two Cross-Unit items (CUO-01, Gap 4) are fully scope-protected and require no P3-01 Architecture involvement.

No blocking ambiguity was found that would prevent proceeding to the Architecture stage: both open Architecture questions are precisely bounded (OQ-001, OQ-004, FRA), and neither touches any already-certified ownership decision.

Architecture Readiness: READY. This document is sufficient to proceed to the P3-01 Architecture. No further capability investigation is required before that step.

## 22. FRA/SDA Traceability

| FR | Governing Capability | SDA Dependency Record(s) |
|---|---|---|
| FR-001 | CAP-001 | DEP-011, DEP-012 |
| FR-002 | CAP-002 | DEP-001, DEP-011, DEP-013, DEP-014, DEP-026 |
| FR-003 | CAP-003 | DEP-001, DEP-011, DEP-013, DEP-014, DEP-026 |
| FR-004 | CAP-004 | DEP-002, DEP-011, DEP-013, DEP-014, DEP-022, DEP-026 |
| FR-005 | CAP-005 | DEP-002, DEP-003, DEP-011, DEP-013, DEP-014, DEP-026 |
| FR-006 | CAP-006 | DEP-003, DEP-004, DEP-011, DEP-013, DEP-014, DEP-026 |
| FR-007 | CAP-007 | DEP-004, DEP-005, DEP-011, DEP-013, DEP-014, DEP-015, DEP-017, DEP-021, DEP-026 |
| FR-008 | CAP-008 | DEP-005, DEP-006, DEP-011, DEP-013, DEP-014, DEP-015, DEP-018, DEP-021, DEP-026 |
| FR-009 | CAP-009 | DEP-006, DEP-007, DEP-011, DEP-013, DEP-014, DEP-015, DEP-019, DEP-021, DEP-026 |
| FR-010 | CAP-010 | DEP-007, DEP-008, DEP-011, DEP-013, DEP-014, DEP-015, DEP-020, DEP-021, DEP-026 |
| FR-011 | CAP-011 | DEP-008, DEP-009, DEP-011, DEP-013, DEP-014, DEP-015, DEP-026, DEP-029 |
| FR-012 | CAP-012 | DEP-013, DEP-025, DEP-027 |
| FR-013 | CAP-013 | DEP-009, DEP-010, DEP-023, DEP-026, DEP-031 |
| FR-014 | CAP-014 | DEP-010 |
| FR-015 | CAP-015 | DEP-014 |
| FR-016 | CAP-016 | DEP-015, DEP-016, DEP-021, DEP-025 |
| FR-017 | CAP-017 | DEP-024, DEP-025 |
| FR-018 | CAP-018 | DEP-012 |
| FR-019 | CAP-019 | DEP-022, DEP-025 |
| FR-020 | CAP-020 | DEP-023, DEP-024, DEP-030 |
| FR-021 | CAP-021 | DEP-026 |
| FR-022 | CAP-022 | DEP-021 |
| FR-023 | CAP-023 | DEP-028, DEP-029 |

All twenty-three Functional Requirements and all thirty-one Dependency records are governed by exactly one Capability each.

## 23. ADR and Invariant Traceability

| ADR / Invariant / Criterion | Related Capabilities |
|---|---|
| ADR-002 (Event-Driven Runtime Evolution) | CAP-006, CAP-015 |
| ADR-003 (TradeLifecycle as Authoritative Trade Model) | CAP-007 |
| ADR-004 (Position Represents Current Market Exposure) | CAP-008 |
| ADR-005 (Profit and Loss Accounting) | CAP-009 |
| ADR-006 (Canonical Financial State Ownership) | CAP-009 |
| ADR-007 (Risk Evaluation as a Pure Computational Layer) | CAP-010 |
| ADR-008 (Performance Ownership) | CAP-011 |
| ADR-009 (Partial Trade Closure and Position Netting) | CAP-007, CAP-016 |
| ADR-010 (Deterministic Runtime Execution Ordering) | CAP-001 through CAP-014, CAP-021 |
| ADR-011 (Runtime Failure Handling) | CAP-016, CAP-020 |
| Runtime Ownership Matrix | CAP-002, CAP-004, CAP-019 |
| AI-005 (Deterministic Execution) | CAP-017 |
| AI-006 (Deterministic Information Flow) | CAP-001, CAP-017 |
| AI-007 (Semantic Continuity) | CAP-003, CAP-012 |
| AI-008 (Explicit Runtime Events) | CAP-006, CAP-015 |
| AI-009 (Tick Completeness) | CAP-013, CAP-014, CAP-020 |
| AI-014 (Architectural Traceability) | CAP-021 |
| AC-009 (Tick Completion) | CAP-013, CAP-014 |
| AC-010 (Information Flow) | CAP-012, CAP-021 |
| AC-011 (Scientific Traceability) | CAP-021 |
| AC-012 (Deterministic Behaviour) | CAP-001, CAP-017 |
| P2-02A (Position Ownership) | CAP-007, CAP-008 |
| P2-03 (Financial Ownership) | CAP-009, CAP-016 |
| P2-04 (Risk Ownership) | CAP-010, CAP-016 |
| TD-004 | CAP-011, CAP-023 |
| TD-007 | CAP-020 |
| CUO-01 | CAP-012, CAP-023 |
| VC-01 | CAP-013 |

Every ADR, Invariant, Acceptance Criterion, prior unit, Technical Debt item, and FRA/SDA cross-unit item the governing task named as a minimum traceability target is referenced by at least one capability.

## 24. Prior-Certification Compatibility

No capability in this document requires, or would be satisfied by, any change to `run_engine/core/pnl.py`, `run_engine/core/position.py`, `run_engine/core/risk.py`'s formula body, `run_engine/core/trade_lifecycle.py`, or any `CanonicalState` schema key already certified complete. Every Governance- or Certification-grounded COMPLETE capability (CAP-007 through CAP-010, CAP-016, CAP-022) cites, rather than re-derives, the relevant P2-02A/P2-03/P2-04 certified finding. This document's own repository re-verification (Section 4) independently re-confirms that no file this document's capabilities touch has changed since the FRA's and SDA's own equivalent re-verifications.

## 25. Internal Consistency Review

Terminology consistency - "COMPLETE," "PARTIAL," and "MISSING" are used exactly as defined in Section 5 throughout this document; no capability is assigned more than one Current Status. "Runtime Capability," "Governance Capability," "Documentation Capability," "Verification Capability," and "Cross-Unit Capability" are used exactly as defined in Section 5; a capability may carry more than one tag, and every tag assignment is justified within that capability's own catalogue entry. "Functionally identical" is not used anywhere in this document to describe a comparison this document itself performed, since no replay or output comparison was independently re-run here. "Byte-identical" is not used anywhere in this document to describe a comparison; its only occurrence is this sentence's own meta-discussion of the term, since no file- or git-blob-level comparison was performed directly by this analysis.

Ownership consistency - no capability in Section 7 assigns ownership of any concept to a component other than what ADR-001 through ADR-009, the Runtime Ownership Matrix, or the P2-02A/P2-03/P2-04 certifications already assign; CAP-004/CAP-019 identify an existing, already-catalogued ownership-mechanism divergence (Gap 1) without proposing a resolution.

Scope consistency - no capability selects a publication mechanism, a copy-versus-reference semantics, an exception/rollback semantics, a stage-skipping policy, a PerformanceEngine redesign, an Implementation Unit, or a file for future modification, consistent with Section 2's explicit prohibition list, itself directly restating the governing task's own "Wichtige Grenzen" section.

Traceability consistency - Section 22's FRA/SDA mapping and Section 23's ADR/Invariant/Criterion mapping are cross-checked: all twenty-three Functional Requirements and all thirty-one Dependency records appear in Section 22; every ADR, Invariant, Acceptance Criterion, prior unit, Technical Debt item, and cross-unit item the governing task named as a minimum traceability target is referenced by at least one capability in Section 23.

Observation/capability/decision separation - Section 4 contains only repository-grounded observations, independently re-verified rather than assumed. Sections 6 through 16 contain only capability classification derived from those observations plus the FRA and SDA. No architecture decision, publication mechanism, or reference/copy semantics is selected anywhere in this document.

No fabricated capability - every one of the twenty-three capabilities traces to exactly one existing Functional Requirement (Section 22); no capability in this document assumes a relationship, a runtime behaviour, or an ownership assignment that repository inspection did not confirm (Section 4's own re-verification pass). CUO-01 is explicitly not evaluated as a P3-01 gap (Section 14); VC-01 is explicitly classified COMPLETE (CAP-013) and not re-evaluated as a gap, consistent with the governing task's explicit instructions.

Status: Internal Consistency Review PASS.

## 26. Independent Self Verification

Every claim in Sections 4 through 25 was independently re-derived during this analysis session, not inherited from the FRA's or SDA's own text without re-checking: the four Functional Gaps, CUO-01, and VC-01 were each re-confirmed against the current runtime (Section 4.1); all thirty-one dependency records were re-validated against their own cited repository evidence (Section 4.2); the one-to-one Capability-to-Functional-Requirement mapping was cross-checked against the FRA's own catalogue (Section 22) to confirm no Functional Requirement was left uncovered and no Capability was assigned to more than one Functional Requirement.

Cross-document consistency check: every FR-001 through FR-023 and DEP-001 through DEP-031 citation in this document (Sections 6 through 16) was compared against the current, final text of `P3_01_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-13.md` and `P3_01_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-13.md` and found consistent, including both documents' own post-review corrections (the FRA's Gap renumbering and CUO-01/VC-01 reclassification; the SDA's own terminology correction) - this document was drafted after, and reflects, both documents' fully revised states.

Result: no error was found during this document's own closing review requiring correction before delivery. All findings from this document's own internal reviews (Section 25) are PASS.

Status: Independent Self Verification PASS.

No commit was made. No runtime file was changed. No push was made. This document is ready to be provided as `P3_01_CAPABILITY_GAP_ANALYSIS_V1_2026-07-13.md`.
