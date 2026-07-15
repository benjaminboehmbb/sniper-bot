Document Class:
Scientific Dependency Analysis

Document ID:
TD005-SDA

Title:
TD-005 Automated Regression Test Suite - Scientific Dependency Analysis

Version:
V1.1

Date:
2026-07-14

Status:
DRAFT - CORRECTIVE SCIENTIFIC REVIEW COMPLETED

Storage Location:
docs/architecture/analysis/

Filename:
TD_005_AUTOMATED_REGRESSION_TEST_SUITE_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-14.md

Technical Debt Item:
TD-005 - Automated Regression Test Suite (docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md)

Accepted Input Baseline:
docs/architecture/analysis/TD_005_AUTOMATED_REGRESSION_TEST_SUITE_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-14.md, Version V1.1, Status DRAFT - EDITORIAL AND SCIENTIFIC REVIEW COMPLETED

Scope:
Scientific dependency analysis only. No capability gap analysis, architecture decision, specification, test design, or implementation content.

Dependencies:
- docs/architecture/analysis/TD_005_AUTOMATED_REGRESSION_TEST_SUITE_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-14.md
- docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md
- docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md
- docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md
- docs/architecture/certification/P1_03_1_FINAL_CERTIFICATION_V1_2026-07-09.md
- docs/architecture/certification/P2_02A_FINAL_CERTIFICATION_V1_2026-07-10.md
- docs/architecture/certification/P2_03_FINAL_CERTIFICATION_V1_2026-07-11.md
- docs/architecture/certification/P2_04_FINAL_CERTIFICATION_V1_2026-07-13.md
- docs/architecture/certification/P3_01_FINAL_CERTIFICATION_V1_2026-07-13.md
- docs/architecture/certification/P3_02_FINAL_CERTIFICATION_V1_2026-07-13.md
- docs/architecture/certification/P3_03_FINAL_CERTIFICATION_V1_2026-07-13.md
- docs/architecture/REPOSITORY_CONSOLIDATION_ARCHITECTURE_V1_2026-07-14.md
- docs/architecture/REPOSITORY_CONSOLIDATION_SPECIFICATION_V1_2026-07-14.md
- docs/architecture/certification/REPOSITORY_CONSOLIDATION_FINAL_CERTIFICATION_V1_2026-07-14.md

Referenced By:
- future TD-005 Capability Gap Analysis (not yet created)

Supersedes:
None. This is the first Scientific Dependency Analysis for TD-005.

Language:
English

Encoding:
ASCII

---

# TD-005 Automated Regression Test Suite - Scientific Dependency Analysis

## 1. Metadata Header

See front matter above.

## 2. Document Control

This document is a Scientific Dependency Analysis (SDA). It identifies scientific dependencies only. It does not perform Capability Gap Analysis, Architecture, or Specification work, and it does not select a test framework, directory layout, harness structure, comparison algorithm, tolerance scheme, or baseline-storage format. No architecture or implementation decision is made anywhere in this document. All findings are grounded in repository evidence independently inspected on 2026-07-14 against branch run-engine-consolidation-safety.

### 2.1 Revision History

- **V1.0 (2026-07-14).** Initial Scientific Dependency Analysis. Thirty-three dependencies; certified-governance-unit evidence for P2-02A, P2-03, and P2-04 cited by name only, without their own direct document paths in metadata, Section 8, or the affected dependency evidence fields.
- **V1.1 (2026-07-14).** Corrective Scientific Review. Two correction areas addressed: (1) Executor package path consistency - a full, independent search of this document found zero occurrences of any incorrect `run_engine/core/execution/init.py` variant; all five occurrences of the executor package initializer path were already, correctly, `run_engine/core/execution/__init__.py`; this finding is recorded rather than a fix being fabricated for a defect that does not exist in the current file. (2) Certified governance-unit evidence - the authoritative P2-02A, P2-03, and P2-04 Final Certifications were located, inspected in full, and confirmed CERTIFIED; their exact repository-relative paths were added to the metadata `Dependencies` list and to Section 8; TD005-DEP-001, TD005-DEP-014, and TD005-DEP-033's own `Repository evidence` fields were updated to cite all six certified units by exact document path rather than by name only; the "six certified units" phrasing is retained where used, since it is now directly, individually evidenced for all six, not merely asserted. No dependency ID, dependency type, status assignment, dependency graph position, critical dependency chain, minimal-prerequisite-capability derivation, FRA/Constraint/Deferred-Obligation traceability, Open Question mapping, CGA input list, or previously-identified gap finding (four-module traceability gap, AC-011 gap, AC-003 partial-coverage finding, AC-013 out-of-scope classification) was altered; the core dependency model is unchanged, since neither correction required renumbering or re-statusing any dependency.

## 3. Executive Summary

This SDA analyzes what must be scientifically defined, observable, stable, and authoritative before an automated regression capability can validly determine whether the active Run Engine still conforms to its certified behavioural contracts. The central scientific problem is not repeatability alone; it is the formal determination of behavioural equivalence under certified-contract boundaries, without confusing that equivalence with implementation equivalence, source identity, byte identity, or incidental undocumented behaviour. Thirty-three individually numbered scientific dependencies (TD005-DEP-001 through TD005-DEP-033) are identified across ten dependency types, organized into a three-layer dependency graph (Foundational, Intermediate, Derived) and five critical dependency chains. Six dependencies are SATISFIED, eight are PARTIALLY SATISFIED, eighteen are UNRESOLVED, and one is correctly classified OUTSIDE TD-005 SCOPE as a general behavioral dependency (repository-integrity, not runtime-behavioral), while independently satisfied as a currently-holding repository-integrity fact. Independent re-verification during this analysis produced two new, concrete, evidence-based findings not present in the accepted FRA: first, four of the fourteen active modules (`run_engine/main.py`, `run_engine/core/state.py`, `run_engine/core/regime.py`, `run_engine/core/execution/__init__.py`) have no direct file-level citation in the FRA's own Requirement Traceability table; second, three Architecture Baseline Acceptance Criteria (AC-003, AC-011, AC-013) have zero citation anywhere in the FRA, of which AC-011 (Scientific Traceability) represents a genuine, currently uncovered dependency requiring resolution, while AC-013 (Architecture Consistency) is correctly outside TD-005's own runtime-behavioral scope, being a document-consistency criterion rather than a runtime property. All FRA Functional Requirements, Constraints, and Deferred Obligations are traced to at least one dependency; all six FRA Open Questions are mapped to their governing dependencies, with none prematurely resolved.

## 4. Accepted Input Baseline

Read in full: docs/architecture/analysis/TD_005_AUTOMATED_REGRESSION_TEST_SUITE_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-14.md, Version V1.1, Status DRAFT - EDITORIAL AND SCIENTIFIC REVIEW COMPLETED. Its content is treated as the direct, authoritative input to this SDA: twenty-two Functional Requirements (TD005-FR-001 through TD005-FR-022) across six capability domains, four Constraints (TD005-CON-001 through TD005-CON-004), two Deferred Specification and Coverage Obligations (Section 13.1, Section 13.2), and six Open Questions (OQ-001 through OQ-006). No FRA requirement, constraint, deferred obligation, or open question is altered, reinterpreted, merged, removed, or added by this document. Where a dependency in this SDA derives from a specific FRA item, that item is cited explicitly (Section 15 through Section 18).

## 5. SDA Objective

To answer, from repository evidence and from the accepted FRA alone: what scientific dependencies must be satisfied before an automated regression capability can validly determine whether the active Run Engine still conforms to its certified behavioural contracts. This document identifies dependencies; it does not propose architecture or implementation solutions, and it does not select a test framework, harness, comparison algorithm, tolerance scheme, or baseline-storage format.

## 6. Scientific Scope

In scope: the scientific dependencies underlying every FRA Functional Requirement, Constraint, and Deferred Obligation; the formal determination of behavioural equivalence under certified-contract boundaries; the observable behavioural surface of the active Run Engine; input equivalence and controlled conditions; reference-baseline provenance; trajectory-versus-endpoint comparison; numeric semantics; temporal and ordering semantics; observability without interference; the coverage model; failure evidence and reproducibility; Long-Duration-Validation integration; active-versus-deferred module scope; and the repository-integrity regression obligation.

Out of scope: Capability Gap Analysis, Architecture Decisions, Specification content, test design, test cases, fixtures, scripts, CI/CD configuration, any dependency or runtime change, and any implementation. This document does not select a test framework, directory layout, harness structure, comparison algorithm, tolerance scheme, or baseline-storage format; every such choice is identified as a dependency requiring future resolution, not resolved here.

## 7. Dependency Analysis Method

The method applied, per the governing task: (1) start from each accepted FRA Functional Requirement, Constraint, Deferred Obligation, and Open Question; (2) identify what must already be scientifically defined, observable, stable, and authoritative for that item to be validly specified; (3) distinguish direct dependencies from derived dependencies; (4) identify prerequisite ordering between dependencies; (5) identify dependencies shared across multiple requirements; (6) identify minimal foundational dependencies without which downstream dependencies cannot be resolved; (7) identify circular dependencies or hidden assumptions; (8) classify each dependency as SATISFIED, PARTIALLY SATISFIED, UNRESOLVED, DEFERRED, or OUTSIDE TD-005 SCOPE; (9) determine which unresolved dependencies must pass into the Capability Gap Analysis; (10) propose no architecture or implementation solution at any step.

## 8. Authoritative Repository Evidence

Independently re-verified for this document, not assumed from the FRA or from any handover text:

- **Active Run Engine module set.** A sixth independent AST-based import closure from `run_engine.main`, freshly re-run for this document, reproduces exactly the FRA's own Section 6.3 result: 18 total `.py` files under `run_engine/`, 14 active, 4 inactive. Active set: `run_engine/main.py`, `run_engine/core/loop.py`, `run_engine/core/state.py`, `run_engine/core/regime.py`, `run_engine/core/strategy.py`, `run_engine/core/position.py`, `run_engine/core/risk.py`, `run_engine/core/execution/__init__.py`, `run_engine/core/execution/executor.py`, `run_engine/core/performance.py`, `run_engine/core/pnl.py`, `run_engine/core/trade_lifecycle.py`, `run_engine/core/canonical_state.py`, `run_engine/core/canonical_enforcer.py`. Inactive RETAIN-Deferred-Scope: `run_engine/core/config.py`, `run_engine/runtime/recovery.py`, `run_engine/runtime/snapshot.py`, `run_engine/runtime/state_memory.py`.
- **Zero non-determinism sources.** Direct inspection of all 14 active files for `import random`, `from random`, `import time` used for control flow, or `datetime.now()`: zero matches, re-confirming FRA Section 6.8.
- **P1-03.1 Final Certification, TD-005's own origin (verbatim, newly inspected for this SDA).** "TD-005 - No automated regression test suite exists for `run_engine/core`; all verification to date has been manual/interactive. Scoped project-wide." (docs/architecture/certification/P1_03_1_FINAL_CERTIFICATION_V1_2026-07-09.md, Section 7). This is direct evidence that the certified-contract corpus has, to date, only ever been verified manually, never via a persistent, reusable mechanism.
- **ADR-009 (Partial Trade Closure and Position Netting), newly inspected in full for this SDA.** Provides formal Scientific Definitions for Scale-In ("Increase of exposure within an already active Position"), Partial Close ("Reduction of exposure while the lifecycle remains active... realizes a portion of accumulated profit or loss... lifecycle remains active"), and Full Close ("Remaining Position reaches zero... lifecycle terminates exactly once"), plus an explicit five-row Lifecycle Transition Table (No Position/Open/Closed states; Trade Opened/Scale-In/Partial Close/Full Close events) with the rule "All other transitions are invalid and SHALL generate a Runtime Failure Event."
- **ADR-011 (Runtime Failure Handling), newly inspected in full for this SDA.** Confirms rejected transitions "SHALL never" modify Position, Equity, Realized PnL, Unrealized PnL, Performance, or terminate a lifecycle, and "SHALL generate exactly one immutable Runtime Failure Event," which "become[s] part of the immutable lifecycle history."
- **AC-001 through AC-015 (Scientific Acceptance Criteria) and ADR-001 through ADR-012 citation frequency in the accepted FRA, computed for this SDA.** AC-003, AC-011, and AC-013 have zero citations anywhere in the FRA; ADR-002 through ADR-009 and ADR-011 have zero literal citations (their substance is nonetheless present in the FRA via AC-014 and AC-015, which restate the same lifecycle-distinctness and failure-handling principles respectively - a citation-precision observation, not necessarily a substantive gap, analyzed in Section 10, TD005-DEP-001 and TD005-DEP-020).
- **FRA Requirement Traceability module-citation count, computed for this SDA.** Of the fourteen active modules, four (`run_engine/main.py`, `run_engine/core/state.py`, `run_engine/core/regime.py`, `run_engine/core/execution/__init__.py`) appear zero times in the FRA's own Section 17.1 traceability table's File(s) column.
- **`tests/`, `requirements.txt`, `README.md`, `tools/`.** Re-confirmed unchanged from the FRA's own Section 6.2 findings: `tests/` holds only an empty, untracked `tests/ssi/`; no test framework in `requirements.txt`; no testing instructions in `README.md`. `tools/repository_consolidation/verify_repository_consolidation.py` (newly inspected for this SDA) is confirmed to check repository structure (active/inactive module set, namespace collisions, archive non-importability) exclusively; it contains no comparison of runtime behavioural output, financial values, lifecycle events, or performance statistics, and is therefore not a reusable scientific dependency for TD-005's own behavioural-regression purpose, consistent with the FRA's own Section 6.6 finding.
- **Repository Consolidation Architecture and Final Certification, re-confirmed.** RC-AI-004 (No Import from Archive), RC-AI-005 (No Runtime Import from Scratch or Review Areas), and RC-AD-004 (path-collision resolution, exactly one `Executor` reachable) all independently re-verified unchanged.
- **P2-02A, P2-03, and P2-04 Final Certifications, newly located and inspected in full for this corrective review (V1.1).** All three exist at exact, verified repository-relative paths - `docs/architecture/certification/P2_02A_FINAL_CERTIFICATION_V1_2026-07-10.md`, `docs/architecture/certification/P2_03_FINAL_CERTIFICATION_V1_2026-07-11.md`, `docs/architecture/certification/P2_04_FINAL_CERTIFICATION_V1_2026-07-13.md` - none inferred from filename convention alone. Each was read in full, not sampled. Verified directly from each: **P2-02A** (Position Ownership) reaches Final Verdict "CERTIFIED" (Section 25), with all twenty FRA requirements, nine Architecture Decisions, sixteen Architecture Invariants, and ten Acceptance Criteria individually PASS, and explicitly documents "No P2-02 Final Certification document exists in the repository" (its own Section 24) - confirming P2-02A, not a separate "P2-02," is the correct certified-unit name. **P2-03** (Financial Ownership) reaches Final Verdict "P2-03 FINANCIAL OWNERSHIP: CERTIFIED" (Section 33), with all twenty FRA requirements, eighteen Scientific Dependencies, fifteen Capabilities, sixteen Architecture Decisions, twelve Architecture Invariants, and twenty-three Acceptance Criteria individually CERTIFIED, and explicitly uses the identical "functionally identical" precision terminology this SDA and the accepted FRA both rely on (its own Section 5). **P2-04** (Risk Ownership) reaches a final "CERTIFIED" verdict (its own closing section), with all fifteen FRA requirements, sixteen Scientific Dependencies, fifteen Capabilities, seventeen Architecture Decisions, nine Architecture Invariants, and combined Architecture/Specification Acceptance Criteria individually CERTIFIED, and independently re-confirms git-blob-identical compatibility with the P2-03-certified baseline (its own Section 4). All three are therefore directly inspected and verified, not referenced only indirectly through the later P3-0x documents; the phrase "six certified units" used elsewhere in this document (Section 10, TD005-DEP-001, TD005-DEP-014, TD005-DEP-033) is accurate on this basis, not an unsupported generalization.

## 9. Dependency Classification Model

Ten dependency types are used, per the governing task's own taxonomy, applied without collapsing materially different types into one category:

- **A. Normative dependency.** A certified contract, approved baseline, or binding invariant must exist and be authoritative.
- **B. Semantic dependency.** A term, event, state, outcome, or behavioural property must have an unambiguous meaning.
- **C. Observability dependency.** The required behaviour must be externally or internally observable without altering the behaviour being observed.
- **D. Reference dependency.** An authoritative comparison reference or certified expected behaviour must exist.
- **E. Equivalence dependency.** The meaning of behavioural equivalence must be formally defined.
- **F. Determinism dependency.** Equivalent inputs and controlled conditions must support reproducible behavioural outcomes.
- **G. Boundary dependency.** The scientific scope of what is and is not a regression contract must be explicit.
- **H. Evidence dependency.** A detected deviation must produce sufficient evidence for independent reproduction and certification.
- **I. Coverage dependency.** The relationship between certified contracts and the active module/behavioural surface must be complete.
- **J. Governance dependency.** The dependency must align with FRA, SDA, CGA, Architecture, Specification, Implementation, and Certification sequencing.

Several dependencies below carry more than one type where the underlying scientific concern genuinely spans two categories (for example, a dependency may be simultaneously a Determinism dependency and a Reference dependency); this is stated explicitly per dependency rather than forcing an artificial single classification.

## 10. Scientific Dependency Inventory

**TD005-DEP-001. Authoritative Certified-Contract Corpus Existence.**
Statement: A regression capability requires an authoritative, enumerable corpus of certified behavioural contracts to compare observed runtime behaviour against.
Type: A (Normative).
Status: PARTIALLY SATISFIED.
Rationale: The corpus exists and is authoritative in substance (Architecture Baseline ADR-001 through ADR-012, AC-001 through AC-015; six certified units: P2-02A, P2-03, P2-04, P3-01, P3-02, P3-03), but has never been assembled into a single enumerable reference for regression purposes; it is distributed across at least eleven separate documents. A citation-precision observation (Section 8) further shows that ADR-002 through ADR-009 and ADR-011 are never literally cited in the FRA, even where their own substance (for example, ADR-009's Scale-In/Partial-Close/Full-Close definitions, ADR-011's failure-handling rules) is clearly present via AC-014 and AC-015.
Upstream dependencies: none (foundational).
Downstream affected FRA items: TD005-FR-001 through TD005-FR-022 (all), TD005-CON-001 through TD005-CON-004 (all, since every constraint is stated relative to certified behaviour).
Repository evidence: docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md (ADR-001 through ADR-012, AC-001 through AC-015); docs/architecture/certification/P2_02A_FINAL_CERTIFICATION_V1_2026-07-10.md; docs/architecture/certification/P2_03_FINAL_CERTIFICATION_V1_2026-07-11.md; docs/architecture/certification/P2_04_FINAL_CERTIFICATION_V1_2026-07-13.md; docs/architecture/certification/P3_01_FINAL_CERTIFICATION_V1_2026-07-13.md; docs/architecture/certification/P3_02_FINAL_CERTIFICATION_V1_2026-07-13.md; docs/architecture/certification/P3_03_FINAL_CERTIFICATION_V1_2026-07-13.md (all six directly inspected in full, Section 8).
Resolution stage: Capability Gap Analysis (assessing whether corpus assembly is a capability gap) and Architecture (deciding the corpus representation).
Scientific risk if unresolved: a regression capability without an enumerable corpus cannot state, for any given check, which certified contract it protects, undermining TD005-FR-021's own certified-contract boundary.

**TD005-DEP-002. Certification-Status Boundary of "Certified".**
Statement: Whether a behavioural contract counts as certified when it appears only in source code, only in certification narrative prose, only in Architecture or Specification text, or only in the Implementation Baseline's own general methodology, must be unambiguous.
Type: B, G (Semantic, Boundary).
Status: UNRESOLVED.
Rationale: TD005-FR-021 (Certified-Contract Boundary for Regression Evaluation) requires this boundary but does not itself resolve which document types qualify; the FRA explicitly defers the exact algorithm to Architecture and Specification.
Upstream dependencies: TD005-DEP-001.
Downstream affected FRA items: TD005-FR-021, TD005-FR-018, TD005-FR-020.
Repository evidence: docs/architecture/analysis/TD_005_AUTOMATED_REGRESSION_TEST_SUITE_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-14.md (TD005-FR-021).
Resolution stage: Architecture.
Scientific risk if unresolved: without this boundary, incidental source-code behaviour could be silently treated as certified, exactly the risk TD005-FR-021 exists to prevent.

**TD005-DEP-003. Technical Debt Register Scope Boundary.**
Statement: Whether Technical Debt Register entries themselves constitute part of the certified-contract corpus, or are explicitly excluded as tracked deviations, must be defined.
Type: A, G.
Status: PARTIALLY SATISFIED.
Rationale: TD-004's own recent closure (cited with an explicit certification reference in its Register `Status` field) demonstrates one precedent for a TD entry becoming certified; TD-001, TD-002, TD-003, TD-006, TD-007 remain open or deferred with no explicit statement of whether their own described behaviour is itself a certified contract or merely a documented deviation from one.
Upstream dependencies: TD005-DEP-001.
Downstream affected FRA items: TD005-FR-014 (performance gating, directly tied to TD-004's own closure), TD005-FR-021.
Repository evidence: docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md.
Resolution stage: Capability Gap Analysis.
Scientific risk if unresolved: an open TD entry describing a known deviation could be misclassified as either a certified contract (freezing a known defect) or entirely ignored (missing a documented, intentional exception).

**TD005-DEP-004. Formal Definition of Behavioural Equivalence.**
Statement: The exact meaning of "equivalent" (exact value, numeric tolerance, normalized, state, event-sequence, temporal/order, contract-conformance, or observational equivalence) must be formally defined before regression can be determined.
Type: E (Equivalence).
Status: UNRESOLVED.
Rationale: TD005-FR-020 establishes the principle that regression is behavioural, not implementation, source, or byte-level, but explicitly does not define the algorithm; this is the FRA's own OQ-006, restated as a dependency.
Upstream dependencies: TD005-DEP-001, TD005-DEP-002, TD005-DEP-007.
Downstream affected FRA items: TD005-FR-020, TD005-FR-021, TD005-FR-018.
Repository evidence: docs/architecture/analysis/TD_005_AUTOMATED_REGRESSION_TEST_SUITE_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-14.md (TD005-FR-020, OQ-006); analytical derivation.
Resolution stage: Architecture and Specification (per the FRA's own OQ-006 disposition).
Scientific risk if unresolved: without a formal definition, "equivalence" risks silently collapsing into byte or source identity, exactly the failure mode TD005-FR-020 exists to prevent.

**TD005-DEP-005. Final-State Versus Full-Trajectory Equivalence Distinction.**
Statement: Whether equivalence is defined over the final Tick-Complete state alone, or over the complete execution trajectory (the sequence of intermediate stage transitions and events within and across ticks), must be resolved.
Type: E.
Status: UNRESOLVED.
Rationale: Several FRA requirements are inherently trajectory properties, not final-state properties (Section 10 of this document, TD005-DEP-015); a purely final-state equivalence definition would be insufficient for them, but the FRA itself does not choose between the two models.
Upstream dependencies: TD005-DEP-004.
Downstream affected FRA items: TD005-FR-001, TD005-FR-003, TD005-FR-006, TD005-FR-007, TD005-FR-008, TD005-FR-009, TD005-FR-010, TD005-FR-017.
Repository evidence: analytical derivation from Architecture Baseline ADR-010 (Section 8) and AC-014 (Section 8).
Resolution stage: Architecture.
Scientific risk if unresolved: choosing final-state-only comparison would silently fail to detect an ordering, publication-count, or intermediate-observation regression even when the final CanonicalState happens to match.

**TD005-DEP-006. Numeric Equivalence Policy.**
Statement: Whether floating-point-derived quantities (realized and unrealized PnL, equity, peak equity, drawdown, risk metrics, performance metrics) require exact equality, a tolerance-bounded comparison, or a normalized comparison must be defined.
Type: E.
Status: UNRESOLVED.
Rationale: The FRA (Section 15, Non-Goals) explicitly excludes selecting a tolerance value; the underlying policy question (not the value) remains an open scientific dependency distinct from, and prerequisite to, any future tolerance selection.
Upstream dependencies: TD005-DEP-004.
Downstream affected FRA items: TD005-FR-011, TD005-FR-012, TD005-FR-013, TD005-FR-014.
Repository evidence: run_engine/core/pnl.py; run_engine/core/canonical_state.py; run_engine/core/performance.py; analytical derivation.
Resolution stage: Architecture and Specification.
Scientific risk if unresolved: applying exact-equality comparison to a value with genuine, benign floating-point representation variance would produce false-positive regressions; applying an unbounded tolerance would mask genuine regressions.

**TD005-DEP-007. Enumerated Observable Behavioural Surface.**
Statement: Which runtime outputs and internal observations are scientifically legitimate candidates for regression evaluation must be enumerated and classified as certified external output, certified internal invariant, implementation detail, or incidental intermediate value.
Type: C (Observability).
Status: PARTIALLY SATISFIED.
Rationale: The FRA (Section 6.8) and this SDA (Section 8) together already enumerate the concrete fields precisely (twelve CanonicalState fields, five lifecycle event types, LONG/SHORT side vocabulary, Executor status vocabulary), but no document has yet classified each field into the four categories above; for example, `runtime_status` and `strategy_selection` are both CanonicalState fields, but whether both are equally "certified external output" for regression purposes, as opposed to one being an internal implementation detail incidentally exposed through the same structure, is unresolved.
Upstream dependencies: TD005-DEP-001, TD005-DEP-031.
Downstream affected FRA items: TD005-FR-003, TD005-FR-004, TD005-FR-005, TD005-FR-006, TD005-FR-013, TD005-FR-014, TD005-FR-015.
Repository evidence: run_engine/core/canonical_state.py; run_engine/core/trade_lifecycle.py; run_engine/core/performance.py; run_engine/core/position.py.
Resolution stage: Architecture.
Scientific risk if unresolved: treating an implementation detail as a certified output would create a brittle, over-constrained regression capability; treating a certified output as incidental would leave a real regression undetected.

**TD005-DEP-008. Observation Non-Interference Boundary.**
Statement: An authoritative boundary must exist defining how the observable surface (TD005-DEP-007) can be read without altering the runtime behaviour being observed, consistent with TD005-CON-001.
Type: C.
Status: PARTIALLY SATISFIED.
Rationale: `RunLoop.step()`'s own return value already exposes a Tick-Complete state as a read path (confirmed by direct inspection, Section 8), which satisfies non-interference for the fields it contains; whether this single read path exposes every field the observable surface (TD005-DEP-007) will ultimately require, or whether additional non-interfering observation points (for example, complete lifecycle history beyond what a single tick's snapshot contains) are also needed, is unresolved.
Upstream dependencies: TD005-DEP-007.
Downstream affected FRA items: TD005-CON-001, TD005-FR-004, TD005-FR-005, TD005-FR-006.
Repository evidence: run_engine/core/loop.py.
Resolution stage: Architecture.
Scientific risk if unresolved: an observation mechanism that reads beyond the confirmed non-interfering boundary could itself violate TD005-CON-001, invalidating the very regression result it produces.

**TD005-DEP-009. Controlled-Condition Set for Comparability.**
Statement: The complete set of conditions that must be held equal across two executions for their outputs to be scientifically comparable (input tick sequence, initial runtime state, initial position, lifecycle history, strategy/regime state, configuration) must be enumerated.
Type: F (Determinism).
Status: UNRESOLVED.
Rationale: AC-012 (Deterministic Behaviour) implies that identical inputs produce identical outputs, but no document enumerates the complete set of "inputs" this implies for the Run Engine's own multi-field state (tick sequence alone is insufficient without also controlling initial Position, lifecycle history, and regime/strategy state, each of which the active RunLoop consumes).
Upstream dependencies: TD005-DEP-010, TD005-DEP-031.
Downstream affected FRA items: TD005-FR-002, TD005-CON-004, TD005-FR-018.
Repository evidence: run_engine/core/loop.py; run_engine/core/state.py; analytical derivation from Architecture Baseline AC-012 (Section 8).
Resolution stage: Architecture and Specification.
Scientific risk if unresolved: an incomplete controlled-condition set would allow a comparison to be run under silently unequal conditions, producing a spurious regression or a false pass.

**TD005-DEP-010. Environmental Determinism Precondition.**
Statement: The active module set must contain no wall-clock, network, or non-seeded-randomness dependency for repeated-run comparison to be valid.
Type: F.
Status: SATISFIED.
Rationale: Independently re-confirmed a sixth time for this document (Section 8): zero `random`, `time`-for-control-flow, or `datetime.now()` usage across all 14 active modules. This precondition is fully, currently, evidentially satisfied and requires no further scientific work before Architecture may rely on it.
Upstream dependencies: none (foundational).
Downstream affected FRA items: TD005-FR-002, TD005-FR-013, TD005-CON-004.
Repository evidence: run_engine/main.py; run_engine/core/loop.py; run_engine/core/state.py; run_engine/core/regime.py; run_engine/core/strategy.py; run_engine/core/position.py; run_engine/core/risk.py; run_engine/core/execution/__init__.py; run_engine/core/execution/executor.py; run_engine/core/performance.py; run_engine/core/pnl.py; run_engine/core/trade_lifecycle.py; run_engine/core/canonical_state.py; run_engine/core/canonical_enforcer.py.
Resolution stage: none required; available immediately to Architecture as a settled precondition.
Scientific risk if unresolved: not applicable (satisfied); future risk only if a later change introduces non-determinism into an active module without a corresponding regression check (TD005-DEP-021, module coverage).

**TD005-DEP-011. Object-Identity and Process-Local Mutable-State Independence.**
Statement: Whether observed equivalence must be independent of Python object identity and process-local mutable state (for example, dict/list identity versus value equality) must be defined.
Type: F.
Status: UNRESOLVED.
Rationale: No document addresses whether two structurally-equal-but-not-identical Python objects (for example, two separately-constructed dicts with the same key/value pairs) are considered equivalent observations; this is a genuine, unaddressed scientific question distinct from the numeric policy (TD005-DEP-006) and from the trajectory model (TD005-DEP-005).
Upstream dependencies: TD005-DEP-004, TD005-DEP-007.
Downstream affected FRA items: TD005-FR-005, TD005-FR-002.
Repository evidence: analytical derivation; run_engine/core/canonical_state.py.
Resolution stage: Architecture.
Scientific risk if unresolved: an equivalence check that inadvertently relies on object identity rather than value equality would produce false-positive regressions for benign refactors (for example, replacing a mutable dict with an equivalent immutable structure).

**TD005-DEP-012. Reference-Baseline Source Identification.**
Statement: A scientifically valid reference for "previously-certified behaviour" requires a defined provenance: the certified units' own historical Implementation/Certification commits, or a baseline freshly established at TD-005 Implementation time.
Type: D (Reference).
Status: UNRESOLVED.
Rationale: This is the FRA's own OQ-002, restated as a dependency; both candidate sources are consistent with the FRA's own requirement text (TD005-FR-018), and neither is chosen here.
Upstream dependencies: TD005-DEP-001, TD005-DEP-002.
Downstream affected FRA items: TD005-FR-018.
Repository evidence: docs/architecture/analysis/TD_005_AUTOMATED_REGRESSION_TEST_SUITE_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-14.md (OQ-002); docs/architecture/certification/P3_01_FINAL_CERTIFICATION_V1_2026-07-13.md; docs/architecture/certification/P3_02_FINAL_CERTIFICATION_V1_2026-07-13.md; docs/architecture/certification/P3_03_FINAL_CERTIFICATION_V1_2026-07-13.md.
Resolution stage: Architecture.
Scientific risk if unresolved: without a defined provenance, "previously-certified behaviour" is not itself a reproducible scientific object, undermining TD005-FR-018's own regression-detection purpose.

**TD005-DEP-013. Reference-Baseline Immutability and Drift Detection.**
Statement: Once a reference baseline is chosen (TD005-DEP-012), it must be immutable, or its own changes must themselves be governed, to avoid the reference silently drifting away from the certified corpus (TD005-DEP-001) without triggering re-certification.
Type: D.
Status: UNRESOLVED.
Rationale: No document addresses what happens to the reference baseline when a certified unit is itself later re-certified or amended; this is a genuine, currently unaddressed scientific dependency.
Upstream dependencies: TD005-DEP-012, TD005-DEP-001.
Downstream affected FRA items: TD005-FR-018, TD005-FR-021.
Repository evidence: analytical derivation.
Resolution stage: Architecture.
Scientific risk if unresolved: an unmanaged reference could become inconsistent with the current certified corpus, causing the regression capability to protect stale, no-longer-authoritative behaviour.

**TD005-DEP-014. Reference-Baseline Reproducibility.**
Statement: The reference baseline itself must be reproducible from the certified corpus rather than being an opaque, frozen artifact whose own derivation cannot be independently re-verified.
Type: D, F.
Status: UNRESOLVED.
Rationale: This is a direct consequence of TD005-DEP-012 and TD005-DEP-013: if the reference cannot itself be regenerated and independently checked against the certified corpus, the regression capability's own foundation is unverifiable, which is inconsistent with this project's own established Independent Self Verification culture (evidenced throughout the P2-0x/P3-0x/Repository Consolidation governance chain).
Upstream dependencies: TD005-DEP-012, TD005-DEP-013.
Downstream affected FRA items: TD005-FR-018, TD005-FR-019.
Repository evidence: analytical derivation from the six certified units' own Final Certification methodology, directly inspected for this document (Section 8): docs/architecture/certification/P2_02A_FINAL_CERTIFICATION_V1_2026-07-10.md; docs/architecture/certification/P2_03_FINAL_CERTIFICATION_V1_2026-07-11.md; docs/architecture/certification/P2_04_FINAL_CERTIFICATION_V1_2026-07-13.md; docs/architecture/certification/P3_01_FINAL_CERTIFICATION_V1_2026-07-13.md; docs/architecture/certification/P3_02_FINAL_CERTIFICATION_V1_2026-07-13.md; docs/architecture/certification/P3_03_FINAL_CERTIFICATION_V1_2026-07-13.md.
Resolution stage: Architecture and Specification.
Scientific risk if unresolved: an unreproducible reference cannot itself be certified, creating a foundation the rest of TD-005 cannot scientifically stand on.

**TD005-DEP-015. Trajectory-Required Property Set.**
Statement: Specific FRA requirements are properties of the execution trajectory, not the final state, and cannot be validated by endpoint-only comparison: execution ordering (TD005-FR-001), publication uniqueness (TD005-FR-003), lifecycle transition integrity (TD005-FR-007, TD005-FR-008, TD005-FR-009, TD005-FR-010), failure-event generation (TD005-FR-017), and information-flow non-reconstruction (TD005-FR-006).
Type: E.
Status: PARTIALLY SATISFIED.
Rationale: This SDA itself identifies and enumerates the complete trajectory-required set (an analytical contribution of this document), but no formal trajectory representation or comparison model yet exists to act on this finding; the identification is complete, the formalization is not.
Upstream dependencies: TD005-DEP-005.
Downstream affected FRA items: TD005-FR-001, TD005-FR-003, TD005-FR-006, TD005-FR-007, TD005-FR-008, TD005-FR-009, TD005-FR-010, TD005-FR-017.
Repository evidence: docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md (ADR-009, ADR-010, ADR-011, Section 8); docs/architecture/analysis/TD_005_AUTOMATED_REGRESSION_TEST_SUITE_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-14.md.
Resolution stage: Architecture.
Scientific risk if unresolved: without a trajectory model, eight of twenty-two Functional Requirements could not be validly verified by any endpoint-only comparison mechanism, regardless of how the mechanism is later implemented.

**TD005-DEP-016. Exact-Equality-Required Value Set.**
Statement: Certain values (event_type strings, Position Side, lifecycle event counts, canonical field write-counts) are categorical or discrete and require exact equality, distinct from continuous financial and risk/performance values (TD005-DEP-006), to avoid applying a single uniform comparison policy incorrectly.
Type: B, E.
Status: PARTIALLY SATISFIED.
Rationale: The categorical/discrete value set is directly distinguishable from source inspection (Section 8: `event_type` in `{TRADE_OPENED, SCALE_IN, PARTIAL_CLOSE, TRADE_CLOSED, RUNTIME_FAILURE_EVENT}`; Position Side in `{LONG, SHORT}`), but no document has yet formally separated this set from the continuous-value set as two distinct comparison-policy domains.
Upstream dependencies: TD005-DEP-006, TD005-DEP-007.
Downstream affected FRA items: TD005-FR-007, TD005-FR-008, TD005-FR-009, TD005-FR-010, TD005-FR-015, TD005-FR-016, TD005-FR-017.
Repository evidence: run_engine/core/trade_lifecycle.py; run_engine/core/position.py; run_engine/core/execution/executor.py.
Resolution stage: Architecture.
Scientific risk if unresolved: applying a numeric tolerance policy to a categorical value (or exact equality to a genuinely tolerant numeric value) would produce an incorrect comparison outcome.

**TD005-DEP-017. Logical-Order Versus Wall-Clock-Timing Distinction.**
Statement: ADR-010's own stage ordering and AC-009's own exactly-once publication requirement are logical ordering guarantees (the sequence of operations within a tick), not wall-clock timing guarantees.
Type: B, F.
Status: SATISFIED.
Rationale: Directly and adequately established by existing Baseline text: ADR-010's own Decision, Scientific Justification, and Acceptance Criteria (Section 8) contain no wall-clock, latency, or timing language of any kind, only sequence language ("Only after completion of Step 12 may..."). This distinction is already fully available to Architecture without further scientific work; downstream formalization of how the future capability preserves this distinction remains an Architecture-stage task, but the distinction itself is settled.
Upstream dependencies: TD005-DEP-032.
Downstream affected FRA items: TD005-FR-001, TD005-FR-003, TD005-FR-022.
Repository evidence: docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md (ADR-010, Section 8).
Resolution stage: none required for the distinction itself; Architecture must still decide how the future capability preserves it.
Scientific risk if unresolved: not applicable (satisfied); the residual risk lies entirely in a future Architecture failing to honor this already-settled distinction, not in the distinction being scientifically undefined.

**TD005-DEP-018. Repeated-Run Output-Order Stability.**
Statement: For TD005-FR-002 (Repeated-Run Determinism) to be valid, the internal iteration order of any Python collection whose own ordering is not explicitly guaranteed by the certified contract must not introduce spurious non-determinism into a comparison.
Type: F.
Status: UNRESOLVED.
Rationale: Not yet verified whether any active module's own observable output relies on a collection whose ordering is an implementation artifact (for example, dict insertion order) rather than a certified property; this has not been checked field-by-field against the observable surface (TD005-DEP-007).
Upstream dependencies: TD005-DEP-010, TD005-DEP-007.
Downstream affected FRA items: TD005-FR-002.
Repository evidence: run_engine/core/canonical_state.py; run_engine/core/performance.py.
Resolution stage: Capability Gap Analysis or Architecture.
Scientific risk if unresolved: an incidental ordering artifact could cause a comparison to report a false regression despite genuinely equivalent behaviour.

**TD005-DEP-019. Authoritative Observation Boundary Definition.**
Statement: A single, authoritative statement of where observation may legitimately occur is required to keep TD005-CON-001 and TD005-CON-002 simultaneously satisfiable.
Type: C.
Status: UNRESOLVED.
Rationale: This refines TD005-DEP-008 into the specific question the FRA's own OQ-001 raises: whether observation occurs only via `RunLoop.step()`'s own return value, or whether some other certified public or internal boundary is also legitimate; not resolved here, consistent with the FRA's own explicit deferral.
Upstream dependencies: TD005-DEP-008.
Downstream affected FRA items: TD005-CON-001, TD005-CON-002.
Repository evidence: docs/architecture/analysis/TD_005_AUTOMATED_REGRESSION_TEST_SUITE_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-14.md (OQ-001, TD005-CON-002).
Resolution stage: Architecture (per the FRA's own OQ-001 disposition).
Scientific risk if unresolved: without an authoritative boundary, different future implementers could choose incompatible observation points, producing inconsistent regression results across implementations.

**TD005-DEP-020. Contract-to-Requirement Coverage Completeness.**
Statement: Every certified contract in the corpus (TD005-DEP-001) must be traceable to at least one FRA Functional Requirement, and every FRA Functional Requirement must be traceable to at least one certified contract, or the gap must be explicitly identified.
Type: I (Coverage).
Status: PARTIALLY SATISFIED.
Rationale: A citation-frequency check performed for this SDA (Section 8) found: AC-003 (Separation of Ownership and Computation) is only partially instantiated - TD005-FR-013 covers this principle for RiskEngine specifically, but AC-003's own general principle across all components is not explicitly verified by any FR; AC-011 (Scientific Traceability, requiring every runtime output to be completely traceable through its full originating chain) has no corresponding FR at all - TD005-FR-006 (Information Flow Non-Reconstruction) is related but narrower, addressing non-reconstruction only, not full end-to-end traceability; AC-013 (Architecture Consistency, requiring no contradiction between governance documents themselves) is correctly outside TD-005's own runtime-behavioral scope, since it is a document-level consistency criterion no runtime regression check could evaluate.
Upstream dependencies: TD005-DEP-001, TD005-DEP-031.
Downstream affected FRA items: all twenty-two Functional Requirements (as the completeness check spans the whole set); specifically implicates TD005-FR-013 (AC-003) and TD005-FR-006 (AC-011 gap).
Repository evidence: docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md (AC-003, AC-011, AC-013, Section 8); docs/architecture/analysis/TD_005_AUTOMATED_REGRESSION_TEST_SUITE_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-14.md.
Resolution stage: Capability Gap Analysis (the AC-011 gap must be assessed there as a candidate new capability need; AC-013 should be recorded as explicitly out of scope, not silently dropped).
Scientific risk if unresolved: AC-011's own uncovered end-to-end traceability property could regress without any FRA requirement detecting it.

**TD005-DEP-021. Module Coverage Completeness.**
Statement: The Active Module Coverage Obligation (FRA Section 13.1) requires all fourteen active modules to be covered by the Functional Requirements; whether the current twenty-two Functional Requirements, taken together, actually reach all fourteen modules by direct file-level traceability must be checked.
Type: I.
Status: UNRESOLVED.
Rationale: A direct count performed for this SDA (Section 8) found that four of the fourteen active modules - `run_engine/main.py`, `run_engine/core/state.py`, `run_engine/core/regime.py`, `run_engine/core/execution/__init__.py` - have zero direct citations in the FRA's own Section 17.1 traceability table. Functional coverage may still be implied (every requirement necessarily exercises `main.py` and `state.py` as pipeline entry/normalization stages whenever `RunLoop.step()` executes, and `regime.py` is exercised by TD005-FR-001's own ordering requirement covering the full twelve-stage sequence, including Regime Classification), but this is an inference, not an explicit, individually-traced requirement-to-module mapping, which the Active Module Coverage Obligation itself calls for.
Upstream dependencies: TD005-DEP-031, TD005-DEP-020.
Downstream affected FRA items: Section 13.1 (Active Module Coverage Obligation), and indirectly TD005-FR-001, TD005-FR-002 (the ordering/determinism requirements that most plausibly imply the four modules' own coverage).
Repository evidence: docs/architecture/analysis/TD_005_AUTOMATED_REGRESSION_TEST_SUITE_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-14.md, Section 17.1 (computed count, Section 8 of this document).
Resolution stage: Capability Gap Analysis.
Scientific risk if unresolved: a genuine regression confined to `run_engine/main.py`, `state.py`, `regime.py`, or the `execution` package's own `__init__.py` could occur without any Functional Requirement explicitly designed to detect it.

**TD005-DEP-022. Domain, State-Transition, and Event Coverage Model Definition.**
Statement: Which coverage concept (module, contract, domain, state-transition, event, requirement, path, or risk-based coverage) is the scientifically appropriate unit of coverage for TD-005 has not been chosen; multiple concepts may be simultaneously necessary.
Type: I.
Status: UNRESOLVED.
Rationale: Module coverage alone (TD005-DEP-021) does not guarantee state-transition coverage of ADR-009's own five-row Lifecycle Transition Table (Section 8), since a module could be "covered" by a requirement that exercises only one of its several certified transitions; no document has yet determined which coverage concept, or combination, TD-005 scientifically requires.
Upstream dependencies: TD005-DEP-020, TD005-DEP-021, TD005-DEP-015.
Downstream affected FRA items: Section 13.1 (Active Module Coverage Obligation), TD005-FR-007, TD005-FR-008, TD005-FR-009, TD005-FR-010.
Repository evidence: docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md (ADR-009's own Lifecycle Transition Table, Section 8).
Resolution stage: Architecture.
Scientific risk if unresolved: choosing an inadequate coverage concept (for example, module coverage alone) could certify TD-005 as "complete" while leaving specific certified state transitions unprotected.

**TD005-DEP-023. Evidence Composition for Reproducibility.**
Statement: TD005-FR-019 requires sufficient detail for independent reproduction of a detected regression; the individually necessary evidence elements must be identified.
Type: H (Evidence).
Status: PARTIALLY SATISFIED.
Rationale: The FRA's own TD005-FR-019 already names four minimum elements (affected tick, affected stage or component, expected value, actual value). This SDA identifies four further elements necessary for genuine independent reproducibility, not yet named in the FRA: input provenance (which controlled-condition set, TD005-DEP-009, produced the observation), initial-state provenance, the specific certified-contract ID the deviation is attributed to (TD005-DEP-002), and execution-environment identity (confirming TD005-CON-004 held during the run). This is a refinement identified by dependency analysis, not a new Functional Requirement, and is passed to Capability Gap Analysis rather than resolved here.
Upstream dependencies: TD005-DEP-009, TD005-DEP-002, TD005-DEP-012.
Downstream affected FRA items: TD005-FR-019.
Repository evidence: docs/architecture/analysis/TD_005_AUTOMATED_REGRESSION_TEST_SUITE_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-14.md (TD005-FR-019).
Resolution stage: Capability Gap Analysis.
Scientific risk if unresolved: a reported regression missing input or initial-state provenance could be technically detected but practically unreproducible, defeating TD005-FR-019's own purpose.

**TD005-DEP-024. Evidence Persistence and Governance Alignment.**
Statement: Whether detected-regression evidence must be persisted in a form consistent with this project's own established governance-document conventions, or is a transient artifact, must be defined.
Type: H, J.
Status: UNRESOLVED.
Rationale: No FRA item or Baseline text addresses evidence persistence; this project's own established convention (docs/architecture/certification/) exists for governance-level certification evidence, but whether individual regression-check evidence must follow the same convention, a lighter-weight convention, or none at all, is undefined.
Upstream dependencies: TD005-DEP-023, TD005-DEP-033.
Downstream affected FRA items: TD005-FR-019.
Repository evidence: docs/architecture/certification/ (directory convention, observed across this repository's own governance chain); analytical derivation.
Resolution stage: Architecture and Specification.
Scientific risk if unresolved: unmanaged evidence persistence could either lose regression evidence needed for a later Final Certification, or accumulate governance-document sprawl inconsistent with Repository Consolidation's own Normative Repository Boundary (TD005-CON-003).

**TD005-DEP-025. Execution-Time Feasibility Across Validation Stages.**
Statement: The same capability (TD005-FR-022) must be usable before Functional-smoke validation (implying a fast execution budget) through 30-day validation (where a longer budget may be tolerable); whether a single execution-time profile can satisfy both is unresolved.
Type: J (Governance).
Status: UNRESOLVED.
Rationale: This is the FRA's own OQ-004, restated as a dependency; the FRA explicitly declines to resolve it, classifying it as an Architecture-level tradeoff.
Upstream dependencies: TD005-DEP-009, TD005-DEP-033.
Downstream affected FRA items: TD005-FR-022.
Repository evidence: docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md (Long Duration Validation section, Section 8); docs/architecture/analysis/TD_005_AUTOMATED_REGRESSION_TEST_SUITE_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-14.md (OQ-004).
Resolution stage: Architecture.
Scientific risk if unresolved: a capability whose own execution time is incompatible with Functional-smoke validation's own fast-turnaround expectation could delay or discourage its use exactly where early regression detection matters most.

**TD005-DEP-026. Pre-Run Versus Post-Run Application Model.**
Statement: Whether the capability is intended to run before a validation stage begins (gating), after it completes (confirming no regression occurred during the run), or both, is not defined by the FRA and affects what "usable before each stage" scientifically requires.
Type: J.
Status: UNRESOLVED.
Rationale: TD005-FR-022's own text ("usable, without modification, before each of the six mandatory stages") is compatible with a gating-only interpretation, but the Implementation Baseline's own "Regression Validation" layer (Section 8, Section 6.5 of the FRA) describes verifying "that previously validated functionality remains correct," which is agnostic to timing relative to a specific run.
Upstream dependencies: TD005-DEP-025.
Downstream affected FRA items: TD005-FR-022.
Repository evidence: docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md (Validation Layer 4, Section 8).
Resolution stage: Architecture.
Scientific risk if unresolved: an unstated application model could result in the capability being used inconsistently across the six validation stages, undermining comparability of results across stages.

**TD005-DEP-027. Evidence Continuity Across Validation Stages.**
Statement: Whether evidence and results from one Long-Duration-Validation stage must be preserved and cross-referenced when the capability is re-applied at the next stage is undefined.
Type: H, J.
Status: UNRESOLVED.
Rationale: The Implementation Baseline requires "every validation stage shall complete successfully before the next duration is attempted" (Section 8), which implies some continuity of evidence across stages, but no document defines what that continuity requires.
Upstream dependencies: TD005-DEP-024, TD005-DEP-026.
Downstream affected FRA items: TD005-FR-022, TD005-FR-019.
Repository evidence: docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md (Long Duration Validation section, Section 8).
Resolution stage: Architecture.
Scientific risk if unresolved: without evidence continuity, a regression introduced between stages could be harder to attribute to a specific validation-stage transition.

**TD005-DEP-028. RETAIN-Deferred-Scope Exclusion Justification.**
Statement: The four inactive RETAIN-Deferred-Scope files must be currently, justifiably excluded from TD-005's own active scope.
Type: G (Boundary).
Status: SATISFIED.
Rationale: The exclusion is directly and currently justified by the independently, repeatedly reproduced import closure (Section 8, sixth independent re-derivation with an identical result): `run_engine/core/config.py`, `run_engine/runtime/recovery.py`, `run_engine/runtime/snapshot.py`, `run_engine/runtime/state_memory.py` hold no active Computational Authority today, consistent with Repository Consolidation's own RC-AD-005 (ADR-012 Deferred-Scope tie).
Upstream dependencies: TD005-DEP-031.
Downstream affected FRA items: Section 6.3 (evidence), OQ-003.
Repository evidence: run_engine/core/config.py; run_engine/runtime/recovery.py; run_engine/runtime/snapshot.py; run_engine/runtime/state_memory.py; docs/architecture/REPOSITORY_CONSOLIDATION_ARCHITECTURE_V1_2026-07-14.md (RC-AD-005).
Resolution stage: none required; available immediately.
Scientific risk if unresolved: not applicable (satisfied).

**TD005-DEP-029. Scope-Drift Detection Condition.**
Statement: The regression capability's own module-coverage check (TD005-DEP-021) must itself be sensitive to a future change in the active/inactive partition, not hard-coded to the current fourteen-module set, so that the four RETAIN-Deferred-Scope files' own future re-entry into active scope (via a future, separate governance chain) is detectable rather than silently missed.
Type: G, I.
Status: UNRESOLVED.
Rationale: This is the FRA's own OQ-003, restated as a dependency on the coverage model (TD005-DEP-021, TD005-DEP-022); no mechanism-independent scientific requirement for automatic drift detection has yet been stated, only the underlying condition (TD005-DEP-028) that currently makes it moot.
Upstream dependencies: TD005-DEP-028, TD005-DEP-021.
Downstream affected FRA items: OQ-003, Section 13.1.
Repository evidence: docs/architecture/analysis/TD_005_AUTOMATED_REGRESSION_TEST_SUITE_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-14.md (OQ-003).
Resolution stage: Capability Gap Analysis and Architecture.
Scientific risk if unresolved: a future governance chain that activates one of the four RETAIN-Deferred-Scope files could silently fall outside TD-005's own protection if the coverage model is not itself scope-aware.

**TD005-DEP-030. Executor Namespace Uniqueness as a Repository-Integrity Dependency.**
Statement: FRA Section 13.2's own deferred obligation must be classified precisely as a repository-integrity dependency (namespace-collision avoidance under Repository Consolidation RC-AD-004), not a Run Engine behavioral semantic dependency, to avoid TD-005 silently absorbing Repository Consolidation's own scope.
Type: G.
Status: OUTSIDE TD-005 SCOPE (as a general behavioral dependency); SATISFIED (as a currently-holding repository-integrity fact).
Rationale: The classification itself is clear and already stated correctly in the FRA (Section 13.2); the underlying fact (exactly one `Executor` reachable from `run_engine.main`) is independently re-verified as currently true (Section 8), but the check protecting it going forward is historically specific to a Repository Consolidation defect, not a general Run Engine behavioural semantic, and this SDA does not convert it into one.
Upstream dependencies: TD005-DEP-031.
Downstream affected FRA items: Section 13.2 (Repository-Integrity Regression Obligation).
Repository evidence: run_engine/core/execution/executor.py; docs/architecture/REPOSITORY_CONSOLIDATION_ARCHITECTURE_V1_2026-07-14.md (RC-AD-004); docs/architecture/certification/REPOSITORY_CONSOLIDATION_FINAL_CERTIFICATION_V1_2026-07-14.md.
Resolution stage: Capability Gap Analysis (whether to formalize a lightweight repository-integrity check alongside, not inside, TD-005's own behavioral scope).
Scientific risk if unresolved: conflating this with general behavioral regression could cause a future Architecture to over-scope TD-005 into Repository Consolidation's own separate governance concern.

**TD005-DEP-031. Active Runtime Scope Stability.**
Statement: A stable, independently-reproducible definition of "the active Run Engine" must exist and remain the shared reference for every other dependency.
Type: A, F.
Status: SATISFIED.
Rationale: Independently re-derived a sixth time for this document (Section 8), identical result each time across the FRA, this SDA, and the entire governance chain's own prior re-derivations (CGA, Architecture, Specification, Implementation, Final Certification of Repository Consolidation). This is the single most foundational dependency in the graph, since the observable surface (TD005-DEP-007), module coverage (TD005-DEP-021), and scope dependencies (TD005-DEP-028, TD005-DEP-029, TD005-DEP-030) all presuppose it.
Upstream dependencies: none (foundational).
Downstream affected FRA items: all twenty-two Functional Requirements (indirectly, as the scope every requirement operates within).
Repository evidence: run_engine/main.py and the thirteen other active files listed in Section 8; docs/architecture/certification/REPOSITORY_CONSOLIDATION_FINAL_CERTIFICATION_V1_2026-07-14.md.
Resolution stage: none required; available immediately.
Scientific risk if unresolved: not applicable (satisfied).

**TD005-DEP-032. Behavioural Vocabulary Stability.**
Statement: The terms used throughout the certified corpus (Position, Side, Scale-In, Partial Close, Full Close, Tick-Complete, Canonical Working State, Authoritative Owner, Computational Authority, Runtime Failure Event) must have stable, unambiguous, cross-document-consistent definitions before any equivalence or comparison model can be built on top of them.
Type: B.
Status: SATISFIED.
Rationale: The Architecture Baseline's own Ownership Terminology section and ADR-009's own Scientific Definitions subsection (Section 8, newly inspected in full for this SDA) together establish this vocabulary formally; independently cross-checked against actual source code vocabulary (`event_type` strings, `side` values in `run_engine/core/trade_lifecycle.py` and `run_engine/core/position.py`) with exact match.
Upstream dependencies: none (foundational).
Downstream affected FRA items: all twenty-two Functional Requirements (indirectly, as the vocabulary every requirement is stated in).
Repository evidence: docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md (Ownership Terminology, ADR-009); run_engine/core/trade_lifecycle.py; run_engine/core/position.py.
Resolution stage: none required; available immediately.
Scientific risk if unresolved: not applicable (satisfied).

**TD005-DEP-033. Governance-Sequence Alignment.**
Statement: TD-005's own resolution must proceed through the established FRA, SDA, CGA, Architecture, Specification, Implementation, Final Certification sequence, consistent with every other unit in this repository.
Type: J.
Status: SATISFIED.
Rationale: This SDA's own existence, scope, and explicit refusal to make architecture or implementation decisions is itself direct evidence this dependency is being honored; the same sequence was independently followed for P2-02A, P2-03, P2-04, P3-01, P3-02, P3-03, and Repository Consolidation, each reaching a CERTIFIED verdict, directly confirmed by inspection of all seven Final Certifications for this corrective review (Section 8).
Upstream dependencies: none (foundational).
Downstream affected FRA items: all FRA items (procedurally, as the governance sequence within which every item will eventually be resolved).
Repository evidence: docs/architecture/certification/P2_02A_FINAL_CERTIFICATION_V1_2026-07-10.md; docs/architecture/certification/P2_03_FINAL_CERTIFICATION_V1_2026-07-11.md; docs/architecture/certification/P2_04_FINAL_CERTIFICATION_V1_2026-07-13.md; docs/architecture/certification/P3_01_FINAL_CERTIFICATION_V1_2026-07-13.md; docs/architecture/certification/P3_02_FINAL_CERTIFICATION_V1_2026-07-13.md; docs/architecture/certification/P3_03_FINAL_CERTIFICATION_V1_2026-07-13.md; docs/architecture/certification/REPOSITORY_CONSOLIDATION_FINAL_CERTIFICATION_V1_2026-07-14.md.
Resolution stage: none required; available immediately, and continuously re-affirmed by each future stage's own conduct.
Scientific risk if unresolved: not applicable (satisfied); the risk would only materialize if a future stage skipped ahead of this sequence, which this document does not do.

All thirty-three dependencies are individually numbered with no gap; none is referenced elsewhere in this document only via a compressed range.

## 11. Dependency Graph

Three layers, derived from the upstream/downstream relationships stated in Section 10, not reproduced from the governing task's own illustrative suggestion.

**Foundational layer** (no upstream dependencies; every other dependency ultimately rests on these):
TD005-DEP-001 (Certified-Contract Corpus Existence), TD005-DEP-010 (Environmental Determinism Precondition), TD005-DEP-031 (Active Runtime Scope Stability), TD005-DEP-032 (Behavioural Vocabulary Stability), TD005-DEP-033 (Governance-Sequence Alignment).

**Intermediate layer** (depend only on the Foundational layer, or on other Intermediate-layer dependencies):
TD005-DEP-002, TD005-DEP-003, TD005-DEP-006, TD005-DEP-007, TD005-DEP-008, TD005-DEP-009, TD005-DEP-011, TD005-DEP-012, TD005-DEP-013, TD005-DEP-014, TD005-DEP-016, TD005-DEP-017, TD005-DEP-018, TD005-DEP-019, TD005-DEP-028, TD005-DEP-030.

**Derived layer** (depend on one or more Intermediate-layer dependencies, and represent the scientific outcomes Architecture and Specification will directly consume):
TD005-DEP-004 (Behavioural Equivalence), TD005-DEP-005 (Final-State vs Trajectory), TD005-DEP-015 (Trajectory-Required Property Set), TD005-DEP-020 (Contract-to-Requirement Coverage), TD005-DEP-021 (Module Coverage), TD005-DEP-022 (Coverage Model), TD005-DEP-023 (Evidence Composition), TD005-DEP-024 (Evidence Persistence), TD005-DEP-025 (Execution-Time Feasibility), TD005-DEP-026 (Pre-Run/Post-Run Model), TD005-DEP-027 (Evidence Continuity), TD005-DEP-029 (Scope-Drift Detection).

No circular dependency was found: every dependency's own upstream list (Section 10) resolves, through a finite chain, to one or more Foundational-layer dependencies with no cycle back. The nearest structural pattern to a cycle is the mutual reinforcement between TD005-DEP-020 (Contract-to-Requirement Coverage) and TD005-DEP-021 (Module Coverage) with TD005-DEP-022 (Coverage Model) - each is informed by the others - but all three remain strictly downstream of the Foundational layer and do not depend on each other in a closed loop; TD005-DEP-022 depends on TD005-DEP-020 and TD005-DEP-021, not the reverse.

## 12. Critical Dependency Chains

**Chain A: Certified contract to regression decision.**
TD005-DEP-001 (certified-contract corpus) -> TD005-DEP-007 (observable behavioural surface) -> TD005-DEP-006 and TD005-DEP-016 (numeric and exact-equality comparison semantics) -> TD005-DEP-004 and TD005-DEP-005 (equivalence determination, final-state vs. trajectory) -> regression classification (TD005-FR-018, TD005-FR-020, TD005-FR-021). Every link in this chain is currently UNRESOLVED or PARTIALLY SATISFIED except its own origin (TD005-DEP-001, PARTIALLY SATISFIED) and TD005-DEP-007 (PARTIALLY SATISFIED); this is the single most consequential chain in the graph, since TD-005's own governing scientific question depends on its full resolution.

**Chain B: Deterministic replay.**
TD005-DEP-010 (environmental determinism, SATISFIED) -> TD005-DEP-009 (controlled-condition set, UNRESOLVED) -> TD005-DEP-011 (object-identity independence, UNRESOLVED) -> TD005-DEP-018 (repeated-run output-order stability, UNRESOLVED) -> comparable, reproducible result (TD005-FR-002). The chain's own foundation is solid (TD005-DEP-010), but every downstream link required for TD005-FR-002's own full validity remains unresolved.

**Chain C: Lifecycle and financial correctness.**
TD005-DEP-032 (behavioural vocabulary, SATISFIED) -> TD005-DEP-017 (logical ordering, SATISFIED) -> TD005-DEP-015 (trajectory-required properties, PARTIALLY SATISFIED) -> TD005-DEP-006 (numeric equivalence for financial values, UNRESOLVED) -> risk/performance consequence (TD005-FR-013, TD005-FR-014, TD005-FR-015) -> TD005-DEP-004 (equivalence determination) -> behavioural regression decision. This chain's own foundation (vocabulary, ordering) is the strongest in the entire graph, directly reflecting ADR-009's and ADR-010's own precise Scientific Definitions; the weakest link is the numeric-equivalence policy shared with Chain A.

**Chain D: Evidence and certification.**
Detected deviation (TD005-FR-018) -> TD005-DEP-002 (certification-status boundary, required for contract attribution) -> TD005-DEP-023 (expected/actual evidence composition, PARTIALLY SATISFIED) -> TD005-DEP-014 (reference-baseline reproducibility, UNRESOLVED, required for deterministic reproduction) -> TD005-DEP-024 (evidence persistence and governance alignment, UNRESOLVED) -> independent review and certification impact. This chain most directly determines whether TD-005's own eventual output can itself support a future Final Certification, consistent with this repository's own established certification methodology (Section 8).

**Chain E: Scope and coverage.**
TD005-DEP-001 (normative contract corpus) -> TD005-DEP-031 (active behavioural surface, SATISFIED) -> TD005-DEP-022 (coverage model, UNRESOLVED) -> TD005-DEP-021 and TD005-DEP-020 (module and contract coverage, both revealing concrete gaps: four modules, AC-011) -> specification completeness. This chain's own concrete findings (the four-module gap, the AC-011 gap) are the most actionable, immediately CGA-relevant output of this entire SDA.

## 13. Minimal Prerequisite Scientific Capability

Derived from the dependency graph (Section 11), not copied from the governing task's own illustrative example: the minimal scientific capability that must exist before TD-005 Architecture work can begin is an authoritative, enumerable, and boundary-defined certified-behavioural-contract corpus (TD005-DEP-001, TD005-DEP-002), expressed in a stable and unambiguous behavioural vocabulary (TD005-DEP-032, SATISFIED), applicable to a stable and independently-reproducible active runtime scope (TD005-DEP-031, SATISFIED), observable through a defined non-interfering boundary (TD005-DEP-008, TD005-DEP-019), under confirmed deterministic execution conditions (TD005-DEP-010, SATISFIED), together with an explicit principle - even where not yet algorithmically resolved - that comparison is performed at the level of behavioural equivalence rather than implementation, source, or byte identity (TD005-DEP-004).

Three of these five prerequisite elements are already SATISFIED (behavioural vocabulary, active runtime scope, environmental determinism); two remain unresolved at the level required for Architecture to proceed rigorously (the corpus's own enumeration and certification-status boundary, TD005-DEP-001/TD005-DEP-002; the formal equivalence definition, TD005-DEP-004). Without both of these two, no later Architecture decision about comparison mechanism, tolerance policy, or invocation boundary could be scientifically grounded, since each would be deciding "how to compare" before "what counts as certified" and "what equivalence means" are themselves defined.

## 14. Dependency Status Assessment

| Status | Count | Dependency IDs |
|---|---|---|
| SATISFIED | 6 | TD005-DEP-010, TD005-DEP-017, TD005-DEP-028, TD005-DEP-031, TD005-DEP-032, TD005-DEP-033 |
| PARTIALLY SATISFIED | 8 | TD005-DEP-001, TD005-DEP-003, TD005-DEP-007, TD005-DEP-008, TD005-DEP-015, TD005-DEP-016, TD005-DEP-020, TD005-DEP-023 |
| UNRESOLVED | 18 | TD005-DEP-002, TD005-DEP-004, TD005-DEP-005, TD005-DEP-006, TD005-DEP-009, TD005-DEP-011, TD005-DEP-012, TD005-DEP-013, TD005-DEP-014, TD005-DEP-018, TD005-DEP-019, TD005-DEP-021, TD005-DEP-022, TD005-DEP-024, TD005-DEP-025, TD005-DEP-026, TD005-DEP-027, TD005-DEP-029 |
| OUTSIDE TD-005 SCOPE | 1 (as a behavioral dependency; also independently SATISFIED as a repository-integrity fact) | TD005-DEP-030 |
| DEFERRED | 0 | none (every dependency identified here is either currently resolvable in status, or explicitly assigned to a future resolution stage in Section 10; none is assigned a bare "deferred" status without an owning future stage) |

Total: 33 dependencies (6 SATISFIED + 8 PARTIALLY SATISFIED + 18 UNRESOLVED + 1 OUTSIDE TD-005 SCOPE = 33), individually re-verified against every dependency's own Status line in Section 10.

## 15. FRA Requirement-to-Dependency Traceability

| FRA Functional Requirement | Governing Dependencies |
|---|---|
| TD005-FR-001 | TD005-DEP-001, TD005-DEP-005, TD005-DEP-015, TD005-DEP-017, TD005-DEP-020, TD005-DEP-021 |
| TD005-FR-002 | TD005-DEP-009, TD005-DEP-010, TD005-DEP-011, TD005-DEP-018 |
| TD005-FR-003 | TD005-DEP-005, TD005-DEP-007, TD005-DEP-008, TD005-DEP-015, TD005-DEP-017 |
| TD005-FR-004 | TD005-DEP-007, TD005-DEP-008 |
| TD005-FR-005 | TD005-DEP-007, TD005-DEP-008, TD005-DEP-011 |
| TD005-FR-006 | TD005-DEP-005, TD005-DEP-015, TD005-DEP-020 |
| TD005-FR-007 | TD005-DEP-015, TD005-DEP-016, TD005-DEP-022 |
| TD005-FR-008 | TD005-DEP-015, TD005-DEP-016, TD005-DEP-022 |
| TD005-FR-009 | TD005-DEP-015, TD005-DEP-016, TD005-DEP-022 |
| TD005-FR-010 | TD005-DEP-015, TD005-DEP-016, TD005-DEP-022 |
| TD005-FR-011 | TD005-DEP-006 |
| TD005-FR-012 | TD005-DEP-006 |
| TD005-FR-013 | TD005-DEP-006, TD005-DEP-009, TD005-DEP-020 |
| TD005-FR-014 | TD005-DEP-003, TD005-DEP-006, TD005-DEP-020 |
| TD005-FR-015 | TD005-DEP-016 |
| TD005-FR-016 | TD005-DEP-016 |
| TD005-FR-017 | TD005-DEP-005, TD005-DEP-015, TD005-DEP-016 |
| TD005-FR-018 | TD005-DEP-002, TD005-DEP-012, TD005-DEP-013, TD005-DEP-014 |
| TD005-FR-019 | TD005-DEP-023, TD005-DEP-024, TD005-DEP-027 |
| TD005-FR-020 | TD005-DEP-004, TD005-DEP-002 |
| TD005-FR-021 | TD005-DEP-002, TD005-DEP-013 |
| TD005-FR-022 | TD005-DEP-025, TD005-DEP-026, TD005-DEP-027 |

All twenty-two Functional Requirements individually trace to at least one dependency.

## 16. Constraint-to-Dependency Traceability

| FRA Constraint | Governing Dependencies |
|---|---|
| TD005-CON-001 | TD005-DEP-008, TD005-DEP-019 |
| TD005-CON-002 | TD005-DEP-019, TD005-DEP-031 |
| TD005-CON-003 | TD005-DEP-031, TD005-DEP-024 |
| TD005-CON-004 | TD005-DEP-010, TD005-DEP-009 |

All four Constraints individually trace to at least one dependency.

## 17. Deferred Obligation-to-Dependency Traceability

| FRA Deferred Obligation | Governing Dependencies |
|---|---|
| Section 13.1, Active Module Coverage Obligation | TD005-DEP-021, TD005-DEP-022, TD005-DEP-020 |
| Section 13.2, Repository-Integrity Regression Obligation | TD005-DEP-030 |

Both Deferred Obligations individually trace to at least one dependency.

## 18. Open Question Resolution Mapping

**OQ-001** (invocation boundary). Governing dependencies: TD005-DEP-008, TD005-DEP-019. Disposition: this SDA partially resolves OQ-001 by identifying that the boundary question decomposes into two distinct dependencies (a general non-interference boundary, TD005-DEP-008, and its specific refinement to an authoritative single boundary statement, TD005-DEP-019), but does not choose the boundary itself. Transferred to: Architecture.

**OQ-002** (reference-baseline source). Governing dependencies: TD005-DEP-012, TD005-DEP-013, TD005-DEP-014. Disposition: this SDA partially resolves OQ-002 by decomposing it into three distinct dependencies (source identification, immutability/drift, reproducibility) not previously distinguished in the FRA. Transferred to: Architecture.

**OQ-003** (RETAIN-Deferred-Scope coverage). Governing dependencies: TD005-DEP-028 (SATISFIED), TD005-DEP-029 (UNRESOLVED). Disposition: this SDA fully resolves the "why currently excluded" portion of OQ-003 (TD005-DEP-028, SATISFIED: the exclusion is currently, correctly justified) but does not resolve the "how would scope-drift be detected" portion (TD005-DEP-029). Transferred to: Capability Gap Analysis and Architecture.

**OQ-004** (execution-time budget). Governing dependency: TD005-DEP-025. Disposition: this SDA does not resolve OQ-004; it confirms the tension is real (a single capability serving both Functional-smoke and 30-day validation) and restates it as a dependency without proposing a resolution. Transferred to: Architecture.

**OQ-005** (test-code location). Governing dependency: TD005-DEP-031 (active scope must not be disturbed), via TD005-CON-003 (Repository-Scope Compatibility). Disposition: this SDA does not resolve OQ-005; the location choice itself is not a scientific dependency in the sense this document analyzes (it requires no formal definition, observability, or equivalence determination), only compatibility with an already-SATISFIED scope dependency. Transferred to: Capability Gap Analysis and Specification.

**OQ-006** (scientific definition of regression equivalence). Governing dependencies: TD005-DEP-004, TD005-DEP-005, TD005-DEP-006, TD005-DEP-011, TD005-DEP-015, TD005-DEP-016. Disposition: this is the central scientific question this SDA analyzes most extensively (Section 12, Chain A and Chain C); it is deliberately not resolved here, consistent with the FRA's own explicit instruction that OQ-006 spans SDA (identifying what the comparison depends on - performed here), Architecture (deciding the comparison model), and Specification (defining the exact comparison contract). Transferred to: Architecture and Specification, per the FRA's own disposition, with the six dependencies above now available as the SDA's own concrete contribution to that future work.

All six Open Question IDs are individually mapped above with no gap; none is prematurely resolved beyond what the available evidence supports.

## 19. Dependency Risks and Failure Modes

- **Premature collapse to byte or source identity.** If TD005-DEP-004 and TD005-DEP-005 remain unresolved into Architecture, there is a concrete risk that an implementer defaults to the simplest available comparison (byte or source identity), exactly the failure mode TD005-FR-020 exists to prevent; this risk is elevated because byte/source comparison is trivial to implement while behavioural equivalence is not.
- **Silent coverage gaps.** TD005-DEP-020 and TD005-DEP-021 each identified a concrete, currently real gap (AC-011's own absent coverage; four modules' own absent direct traceability); if these are not carried forward into the Capability Gap Analysis with their own specific evidence, they risk being silently lost between governance stages.
- **Reference-baseline drift.** Absent resolution of TD005-DEP-012 through TD005-DEP-014, a reference baseline chosen ad hoc at Implementation time, without governed immutability or reproducibility, could drift from the certified corpus without detection, producing a regression capability that protects stale rather than current certified behaviour.
- **Trajectory-blind comparison.** Absent resolution of TD005-DEP-005 and TD005-DEP-015, an Architecture that defaults to final-state-only comparison (the simpler of the two models) would leave eight Functional Requirements' own trajectory properties unprotected while appearing, superficially, to satisfy TD-005's own purpose.
- **Numeric-policy misapplication.** Absent resolution of TD005-DEP-006 and TD005-DEP-016, applying a single uniform comparison policy across both categorical and continuous values (Section 10) would produce either false positives (exact equality applied to genuinely tolerant values) or false negatives (tolerance applied to categorical values that must match exactly).
- **Scope creep into Repository Consolidation.** Absent the explicit classification in TD005-DEP-030, a future Architecture could over-generalize the Executor-namespace obligation into a general behavioural semantic, inappropriately expanding TD-005's own scope into a different governance unit's own already-certified concern.

## 20. Inputs Required by Capability Gap Analysis

The following UNRESOLVED and PARTIALLY SATISFIED dependencies, together with their own concrete evidence, are the direct inputs a future TD-005 Capability Gap Analysis must assess:

- TD005-DEP-001, TD005-DEP-002, TD005-DEP-003 (certified-contract corpus assembly and boundary).
- TD005-DEP-004, TD005-DEP-005, TD005-DEP-006, TD005-DEP-011, TD005-DEP-015, TD005-DEP-016 (behavioural-equivalence formalization, including the trajectory-required property set this SDA newly enumerates).
- TD005-DEP-007, TD005-DEP-008, TD005-DEP-019 (observable surface classification and observation-boundary authority).
- TD005-DEP-009, TD005-DEP-018 (controlled-condition enumeration and output-order stability).
- TD005-DEP-012, TD005-DEP-013, TD005-DEP-014 (reference-baseline provenance, immutability, reproducibility).
- TD005-DEP-020 (the AC-011 coverage gap and the AC-003 partial-instantiation finding, both newly identified by this SDA).
- TD005-DEP-021 (the four-module traceability gap newly identified by this SDA).
- TD005-DEP-022 (coverage-model selection).
- TD005-DEP-023, TD005-DEP-024, TD005-DEP-027 (evidence composition, persistence, and continuity).
- TD005-DEP-025, TD005-DEP-026 (Long-Duration-Validation execution-time and application-model tension).
- TD005-DEP-029 (scope-drift detection mechanism).

Twenty-six of thirty-three dependencies (Section 14: eighteen UNRESOLVED plus eight PARTIALLY SATISFIED) require Capability Gap Analysis or later-stage attention; six are already SATISFIED and require no further action before Architecture may rely on them; one (TD005-DEP-030) is correctly OUTSIDE TD-005's own behavioural scope as a general behavioral dependency, while independently SATISFIED as a currently-holding repository-integrity fact.

## 21. SDA Completion Criteria

This Scientific Dependency Analysis is complete and ready for a future Capability Gap Analysis when:

- Every accepted FRA Functional Requirement, Constraint, and Deferred Obligation has been individually traced to at least one governing dependency (Section 15, Section 16, Section 17), with no compressed range used anywhere.
- Every dependency is individually numbered, typed against the ten-category taxonomy without collapsing materially different types, and assigned an evidence-based status (Section 10, Section 14).
- No dependency statement is a disguised architecture decision: verified by construction, since every dependency in Section 10 states what must be true or defined, never how it will be achieved, and every dependency whose own resolution would require a concrete mechanism explicitly defers that mechanism to Architecture or Specification (TD005-DEP-004, TD005-DEP-020, and others state this deferral explicitly).
- No dependency duplicates a Functional Requirement: verified by construction, since every dependency in Section 10 is stated as a precondition for one or more Functional Requirements, not as a restatement of a Functional Requirement's own text.
- No dependency is merely a future test case: verified by construction, since Section 10 contains no concrete input value, fixture description, or expected-output value anywhere.
- No test framework or implementation mechanism is selected anywhere in this document.
- Behavioural equivalence is not reduced to byte or source identity: TD005-DEP-004 explicitly distinguishes all four notions (behavioural, implementation, byte, source), consistent with the accepted FRA's own TD005-FR-020.
- The certified-contract boundary remains explicit and unresolved rather than assumed (TD005-DEP-002).
- Active and deferred runtime scope remain distinct (TD005-DEP-028, TD005-DEP-029, TD005-DEP-031) and are not conflated anywhere in this document.
- Logical ordering is not confused with wall-clock timing (TD005-DEP-017 states this distinction explicitly).
- Final-state and trajectory equivalence are not conflated (TD005-DEP-005, TD005-DEP-015 state this distinction explicitly).
- Numeric semantics are not falsely resolved: TD005-DEP-006 and TD005-DEP-016 identify the policy question without selecting a tolerance value or resolution method.
- Reference provenance is not assumed: TD005-DEP-012 explicitly identifies this as unresolved rather than presupposing a specific source.
- No circular dependency was found (Section 11's own explicit check); the closest structural pattern (TD005-DEP-020/021/022's own mutual informativeness) was verified to be strictly layered, not cyclic.
- The minimal prerequisite scientific capability (Section 13) is explicitly derived from, and justified against, the completed dependency graph, not assumed or copied from the governing task's own illustrative example.
- Every FRA item has complete dependency coverage (Section 15 through Section 17, each table showing zero gaps).
- All unresolved dependencies are passed explicitly to the Capability Gap Analysis or a later governance stage, individually, with no dependency left unassigned to any future resolution stage (Section 10's own "Resolution stage" field for every dependency; Section 20's own consolidated list).

All criteria above are satisfied by this document.

## 22. Conclusion

This Scientific Dependency Analysis answers the governing scientific question - what scientific dependencies must be satisfied before an automated regression capability can validly determine whether the active Run Engine still conforms to its certified behavioural contracts - by identifying thirty-three individually numbered dependencies across ten types, organized into a three-layer, cycle-free dependency graph and five critical dependency chains. Six dependencies are already SATISFIED (environmental determinism, active runtime scope stability, behavioural vocabulary stability, logical-versus-wall-clock-timing distinction, the current RETAIN-Deferred-Scope exclusion justification, and governance-sequence alignment), providing a genuinely solid foundation; eight are PARTIALLY SATISFIED, requiring targeted rather than wholesale further work; eighteen are UNRESOLVED and are individually passed to the Capability Gap Analysis with their own specific evidence; one is correctly classified OUTSIDE TD-005's own behavioural scope as a general behavioral dependency, while independently SATISFIED as a repository-integrity fact. The central scientific problem - formal determination of behavioural equivalence under certified-contract boundaries, without confusing it with implementation equivalence, source identity, byte identity, or incidental undocumented behaviour - is analyzed in depth (TD005-DEP-004 through TD005-DEP-006, TD005-DEP-011, TD005-DEP-015 through TD005-DEP-016) but deliberately not resolved, consistent with the accepted FRA's own explicit deferral of this question to Architecture and Specification. Two new, concrete, evidence-based findings emerged from this document's own independent re-verification, not present in the accepted FRA: a four-module traceability gap and an AC-011 coverage gap, both carried forward to the Capability Gap Analysis rather than silently absorbed or ignored. This document makes no architecture or implementation decision, selects no test framework, harness, comparison algorithm, tolerance scheme, or baseline-storage format, and is ready for a future TD-005 Capability Gap Analysis.
