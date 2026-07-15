Document Class:
Capability Gap Analysis

Document ID:
TD005-CGA

Title:
TD-005 Automated Regression Test Suite - Capability Gap Analysis

Version:
V1.1

Date:
2026-07-14

Status:
DRAFT - EDITORIAL AND SCIENTIFIC REVIEW COMPLETED

Storage Location:
docs/architecture/analysis/

Filename:
TD_005_AUTOMATED_REGRESSION_TEST_SUITE_CAPABILITY_GAP_ANALYSIS_V1_2026-07-14.md

Technical Debt Item:
TD-005 - Automated Regression Test Suite (docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md)

Accepted Working Baselines:
docs/architecture/analysis/TD_005_AUTOMATED_REGRESSION_TEST_SUITE_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-14.md, Version V1.1, Status DRAFT - EDITORIAL AND SCIENTIFIC REVIEW COMPLETED
docs/architecture/analysis/TD_005_AUTOMATED_REGRESSION_TEST_SUITE_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-14.md, Version V1.1, Status DRAFT - CORRECTIVE SCIENTIFIC REVIEW COMPLETED

Scope:
Capability gap analysis only. No architecture decision, framework selection, pytest selection, fixture design, CI/CD design, comparison-algorithm selection, storage-format selection, reporting-format selection, or implementation content.

Dependencies:
- docs/architecture/analysis/TD_005_AUTOMATED_REGRESSION_TEST_SUITE_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-14.md
- docs/architecture/analysis/TD_005_AUTOMATED_REGRESSION_TEST_SUITE_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-14.md
- docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md
- docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md
- docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md
- docs/architecture/REPOSITORY_CONSOLIDATION_ARCHITECTURE_V1_2026-07-14.md
- docs/architecture/REPOSITORY_CONSOLIDATION_SPECIFICATION_V1_2026-07-14.md
- docs/architecture/certification/REPOSITORY_CONSOLIDATION_FINAL_CERTIFICATION_V1_2026-07-14.md
- docs/architecture/certification/P1_03_1_FINAL_CERTIFICATION_V1_2026-07-09.md
- docs/architecture/certification/P2_02A_FINAL_CERTIFICATION_V1_2026-07-10.md
- docs/architecture/certification/P2_03_FINAL_CERTIFICATION_V1_2026-07-11.md
- docs/architecture/certification/P2_04_FINAL_CERTIFICATION_V1_2026-07-13.md
- docs/architecture/certification/P3_01_FINAL_CERTIFICATION_V1_2026-07-13.md
- docs/architecture/certification/P3_02_FINAL_CERTIFICATION_V1_2026-07-13.md
- docs/architecture/certification/P3_03_FINAL_CERTIFICATION_V1_2026-07-13.md
- requirements.txt

Referenced By:
- future TD-005 Architecture (not yet created)

Supersedes:
None. This is the first Capability Gap Analysis for TD-005.

Language:
English

Encoding:
ASCII

---

# TD-005 Automated Regression Test Suite - Capability Gap Analysis

## 1. Metadata

See front matter above.

### 1.1 Revision History

- **V1.0 (2026-07-14).** Initial Capability Gap Analysis. Twenty-two capabilities across ten classes; TD005-CAP-012 stated without an explicit atomicity justification separating detection/classification from severity/waiver/disposition concerns; TD005-CAP-001 stated as an "Assembly" capability without an explicit capability-versus-governance-activity justification; TD005-CAP-022 stated as a newly surfaced hidden capability without explicit relationship subsections to TD005-CAP-009 and TD005-CAP-011; the capability-layer graph (Section 8) stated without an explicit layer-classification rationale.
- **V1.1 (2026-07-14).** Targeted Editorial and Scientific Review. Four review areas addressed: (1) TD005-CAP-012 atomicity - an explicit search of the accepted FRA and SDA for severity-ranking, business-acceptability, waiver, disposition, and remediation-priority language found zero occurrences in either document; TD005-CAP-012 was therefore confirmed scientifically atomic as a detection-plus-classification capability, and its wording was refined (Option B) to explicitly exclude severity ranking, business acceptability, waiver decisions, remediation priority, and operational disposition, none of which was ever part of its scope - no split was performed. (2) TD005-CAP-001 was renamed from "Certified-Contract Corpus Assembly Capability" to "Certified-Contract Corpus Authority Capability" and given an explicit scientific justification distinguishing the durable, repeatable, authoritative capability from a one-time governance activity (document collection, register update); its ID, maturity, dependency sources, and traceability are unchanged. (3) TD005-CAP-022 was given explicit "Relationship to TD005-CAP-009" and "Relationship to TD005-CAP-011" subsections and an explicit "Scientific classification: separate capability" statement, and its own Traceability field was extended to name TD005-CAP-009 and TD005-CAP-011 directly, alongside its existing TD005-CON-004 scientific-proximity anchor; its ID, maturity (MISSING), and risk (Medium) are unchanged. (4) A new "Capability Layer Rationale" subsection was added to Section 8, stating the Foundational/Intermediate/Derived classification criteria and explicitly explaining four named edge cases (TD005-CAP-001 and TD005-CAP-017 as Foundational despite incomplete maturity; TD005-CAP-003 as Derived; TD005-CAP-022 as Intermediate); no capability was moved between layers, since every existing placement was independently re-verified to satisfy the stated criteria. A full atomicity audit (new Section 7.1) reviewed all twenty-two capabilities, with particular attention to the ten capabilities the governing task named; no split was found necessary for any capability beyond TD005-CAP-012's own wording refinement. A repeated hidden-assumption search (Section 13) evaluated eleven named candidates (Python interpreter version, operating-system/platform identity, locale/timezone, numeric backend/BLAS, dependency transitivity, environment-variable influence, serialization stability, process count/concurrency, input-data schema version, configuration version, baseline-generation code version); Python interpreter version, numeric-backend/BLAS implementation, and dependency transitivity were found already covered by TD005-CAP-022's own scope (its Purpose field was broadened, without a new ID, to state this explicitly); environment-variable influence and input-data schema version were found already covered by TD005-CAP-011 and TD005-CAP-009/TD005-CAP-011 respectively; serialization stability and baseline-generation code version were found scientifically relevant but appropriately deferred to Architecture/Specification as part of TD005-CAP-009's own future reference-representation mechanism; operating-system/platform identity, locale/timezone, process count/concurrency, and configuration version were found unsupported by repository evidence (confirmed by a fresh scan of all fourteen active modules: zero environment-variable reads, zero threading/multiprocessing/asyncio imports) and are recorded as examined-and-rejected, not silently skipped. No new capability was added; the capability count remains twenty-two. All twenty-two maturity assignments and all eighteen risk ratings were reassessed and confirmed unchanged, including the five specifically re-verified in the governing task (TD005-CAP-001 PARTIALLY AVAILABLE; TD005-CAP-012 MISSING; TD005-CAP-017 PARTIALLY AVAILABLE; TD005-CAP-022 MISSING, Medium risk; TD005-CAP-018 OUTSIDE TD-005 SCOPE as a behavioral capability, AVAILABLE as a repository-integrity fact). All traceability tables (Section 14) are unchanged, since no capability was split, merged, added, or removed; TD005-CAP-022's own traceability was extended (not altered) to name TD005-CAP-009 and TD005-CAP-011 explicitly. All six Open Question dispositions (Section 15) are unchanged. No architecture, specification, framework, or implementation content was added.

## 2. Executive Summary

This Capability Gap Analysis (CGA) determines, for TD-005 (Automated Regression Test Suite), which scientific capabilities required by the accepted Functional Requirement Analysis (FRA, V1.1) and Scientific Dependency Analysis (SDA, V1.1) already exist in the repository, which exist only partially, which are completely missing, and which of these must be resolved before Architecture may begin versus which are properly deferred to Specification. Twenty-two individually numbered capabilities (TD005-CAP-001 through TD005-CAP-022) are identified across the ten capability classes named by the governing task, refined where repository evidence justified it. Independent, freshly re-run repository verification (Section 5) reproduces the SDA's own findings exactly (18 total `run_engine/` files, 14 active, 4 inactive; zero test framework in `requirements.txt`; zero `pytest`/`unittest` import anywhere under `run_engine/`) and surfaces one capability gap not previously named in the FRA or SDA: `run_engine/core/regime.py` is the sole active module importing `numpy`/`pandas`, and no governance document anywhere in the repository addresses whether the pinned library versions in `requirements.txt` (`numpy==2.3.3`, `pandas==2.3.3`) are themselves a scientific precondition for reproducible floating-point regression comparison over time. This is recorded as TD005-CAP-022 (Section 12). Of the twenty-two capabilities, three are AVAILABLE, seven are PARTIALLY AVAILABLE, eleven are MISSING, one is OUTSIDE TD-005 SCOPE as a behavioral capability (while independently AVAILABLE as a repository-integrity fact), and none is DEFERRED at the capability-existence level (deferral applies to specific unresolved elements within otherwise-identified capabilities, not to whole capabilities left unanalyzed). This document makes no architecture, framework, or implementation decision anywhere. A subsequent targeted Editorial and Scientific Review (V1.1) confirmed this capability model unchanged in count, maturity, and risk distribution; refined TD005-CAP-012's own wording for scientific atomicity without splitting it; renamed and justified TD005-CAP-001 as a persistent scientific capability rather than a one-time governance activity; clarified TD005-CAP-022's own relationship to TD005-CAP-009 and TD005-CAP-011; and added an explicit capability-layer classification rationale (Section 8).

## 3. Accepted Inputs

Read in full and treated as binding, unmodified inputs:

- **FRA V1.1** (DRAFT - EDITORIAL AND SCIENTIFIC REVIEW COMPLETED): twenty-two Functional Requirements (TD005-FR-001 through TD005-FR-022), four Constraints (TD005-CON-001 through TD005-CON-004), two Deferred Specification and Coverage Obligations (Section 13.1, Section 13.2), six Open Questions (OQ-001 through OQ-006).
- **SDA V1.1** (DRAFT - CORRECTIVE SCIENTIFIC REVIEW COMPLETED): thirty-three Scientific Dependencies (TD005-DEP-001 through TD005-DEP-033), a three-layer dependency graph, five critical dependency chains, a minimal-prerequisite-scientific-capability statement, and a Dependency Status Assessment (6 SATISFIED, 8 PARTIALLY SATISFIED, 18 UNRESOLVED, 1 OUTSIDE TD-005 SCOPE).

No FRA requirement, constraint, deferred obligation, or Open Question, and no SDA dependency, type, status, graph position, or chain, is altered, reinterpreted, merged, removed, or added by this document. This CGA translates the accepted SDA's dependency-level findings into capability-level maturity assessments; it does not re-derive the dependencies themselves.

## 4. Objective

To determine, from the accepted FRA and SDA alone, which required scientific capabilities already exist, which are only partially available, which are completely missing, which must be created (or at minimum authoritatively resolved) before Architecture may begin, and which properly belong to a later Specification or Implementation stage. This document answers only: which capabilities are missing. It does not select architecture, framework, pytest, fixtures, CI/CD, comparison algorithms, storage format, reporting format, or implementation of any kind.

## 5. Repository Evidence

Independently re-verified immediately before drafting this document, not assumed from the FRA, the SDA, or any prior analysis:

1. **Branch and HEAD.** Branch `run-engine-consolidation-safety`; HEAD `8952b1cba42506e4126e57ee89c59934f3d48b71`. `git status --short` shows exactly three entries: the pre-existing, unrelated modification to `docs/capabilities/SGF_013_SCIENTIFIC_BEHAVIOUR_REPRESENTATION_2026-06-26.md`, and the two untracked accepted TD-005 Working Baselines (FRA, SDA). No other local change exists.
2. **Active Run Engine module set.** A freshly, independently authored AST-based import closure from `run_engine.main` (not a re-run of the SDA's own script) reproduces exactly: 18 total `.py` files under `run_engine/`, 14 active, 4 inactive. The 14 active modules and 4 inactive RETAIN-Deferred-Scope modules are identical in name and count to every prior independent derivation in the FRA, the SDA, and the Repository Consolidation governance chain.
3. **Numpy/pandas import scan (new for this CGA).** Of the 14 active modules, exactly one - `run_engine/core/regime.py` - imports `numpy` and/or `pandas` directly. No other active module does.
4. **`tests/` inventory.** Independently re-walked: zero files exist anywhere under `tests/`; only the empty, untracked directory structure `tests/ssi/`, `tests/ssi/builder/`, `tests/ssi/docs/` exists, containing zero files. This is unchanged from the FRA's and SDA's own findings.
5. **`requirements.txt`.** Independently re-read in full (12 lines): `certifi==2025.10.5`, `charset-normalizer==3.4.3`, `idna==3.10`, `numpy==2.3.3`, `pandas==2.3.3`, `python-dateutil==2.9.0.post0`, `pytz==2025.2`, `PyYAML==6.0.3`, `requests==2.32.5`, `six==1.17.0`, `tzdata==2025.2`, `urllib3==2.5.0`. No test framework (pytest, unittest extension, hypothesis, coverage) is present. Every dependency is pinned to an exact version (`==`), not a range - itself evidence that version-exactness already matters to this repository's own maintenance practice, even though no governance document connects this practice to TD-005's own regression-validity requirement (Section 12, TD005-CAP-022).
6. **`pytest`/`unittest` import scan.** Independently re-confirmed: zero occurrences of `import pytest` or `import unittest` anywhere under `run_engine/`.
7. **`tools/repository_consolidation/verify_repository_consolidation.py`.** Re-confirmed (consistent with the FRA's Section 6.6 and the SDA's Section 8): checks repository structure only (active/inactive module set, namespace collisions, archive non-importability); performs no comparison of runtime behavioral output, financial values, lifecycle events, or performance statistics; not a reusable capability for TD-005's own behavioral-regression purpose.
8. **Architecture Baseline, Implementation Baseline, Technical Debt Register, Repository Consolidation Architecture/Specification/Final Certification, and all six certified units (P2-02A, P2-03, P2-04, P3-01, P3-02, P3-03).** Each independently re-opened; the specific facts this CGA relies on (ADR-001 through ADR-012, AC-001 through AC-015, the Implementation Baseline's own four-layer Validation Strategy and Long-Duration-Validation sequence, TD-001 through TD-007 status fields, RC-AD-004 through RC-AD-023, and each of the six certified units' own Final Verdict) are re-confirmed present and unchanged from the SDA's own citations (SDA Section 8), which were themselves independently verified section-by-section during the preceding Final QA Certification Review of the SDA.
9. **No governance document, anywhere in the repository, addresses library/interpreter version stability as a precondition for reproducible numeric regression comparison.** An explicit search of the FRA, the SDA, the Architecture Baseline, the Implementation Baseline, and the Repository Consolidation chain found zero occurrences of "numpy", "pandas version", "interpreter version", "dependency version", "library version", "pinned dependency" in this context. This is a genuine, newly surfaced repository-evidence finding (Finding 3 combined with Finding 9), recorded as a capability gap in Section 12, not silently assumed away.

## 6. Capability Methodology

Capabilities are derived exclusively from the accepted FRA's Functional Requirements, Constraints, and Deferred Obligations, and from the accepted SDA's Dependencies; no capability in this document originates from an implementation idea, a candidate test framework, or a candidate tool. The method applied: (1) group the SDA's thirty-three dependencies into capability-level units, one capability per coherent scientific concern the FRA/SDA jointly require, refusing to merge dependencies that answer different scientific questions even when related; (2) for every capability, independently assess current maturity from repository evidence (Section 5) and from the SDA's own per-dependency status, applying the instruction that existing code alone is insufficient - a capability requires authoritative definition, traceability, evidence, and governance compatibility, not merely a plausible code path; (3) identify missing elements per capability without proposing how they would be built; (4) construct a capability-level dependency graph (Foundational, Intermediate, Derived), independently derived from capability-to-capability prerequisite relationships, not copied from the SDA's own dependency-level graph; (5) assess Architecture and Specification readiness per capability; (6) classify risk per missing or partially available capability; (7) explicitly search for capability assumptions hidden inside the FRA/SDA that were never given their own capability identity, and add them if found (Section 12); (8) resolve, or explicitly transfer, every SDA Open Question; (9) propose no architecture, framework, or implementation solution at any step.

## 7. Capability Inventory

Ten capability classes are used, per the governing task, refined into twenty-two individually numbered capabilities where repository evidence justified finer granularity than one capability per class. Each capability below states: ID, Name, Purpose, Scientific rationale, Current repository evidence, Dependency sources, Current maturity, Missing elements, Scientific risk, Required before (Architecture / Specification / Implementation), and Traceability.

### Class A - Certified Behaviour Contract Capability

**TD005-CAP-001. Certified-Contract Corpus Authority Capability.**
Purpose: provide an authoritative, enumerable corpus of certified behavioural contracts a regression capability can compare observed runtime behaviour against.
Scientific rationale: a regression capability cannot determine deviation from "certified behaviour" if no single, enumerable representation of that behaviour exists; TD005-FR-021's own certified-contract boundary presupposes a corpus to draw the boundary around.
Capability-versus-governance-activity justification (V1.1): this capability is not the one-time, procedural act of collecting documents, filing records, updating a register, or producing a list - each of those is a governance activity, complete once performed. The scientific capability this document identifies is the durable, repeatable ability to: identify the authoritative behavioural contract set from among the Architecture Baseline, the Implementation Baseline, and the six certified units; enumerate that set reproducibly, so an independent party re-deriving it reaches the same result; determine membership and exclusion for any candidate contract (including the open Technical Debt Register entries); trace each future regression decision (TD005-CAP-012) back to the specific certified source it protects; detect drift or ambiguity if the corpus's own composition changes as future units are certified; and support independent reconstruction of the corpus from primary repository evidence rather than from a cached or trusted list. A one-time document-collection act would satisfy none of the last four properties; this capability requires them all to remain persistently true. This document does not prescribe the corpus's own format, storage location, schema, or implementation mechanism - those are Architecture and Specification decisions (Section 10, Section 11).
Name clarification (V1.1): renamed from "Certified-Contract Corpus Assembly Capability" to "Certified-Contract Corpus Authority Capability". "Assembly" named only the one-time act; "Authority" names the persistent, reproducible property this capability actually requires, consistent with the justification above. The rename changes no ID, maturity, dependency source, or traceability.
Current repository evidence: the corpus exists in substance, distributed across the Architecture Baseline (ADR-001 through ADR-012, AC-001 through AC-015) and six certified units (P2-02A, P2-03, P2-04, P3-01, P3-02, P3-03), each independently confirmed CERTIFIED (Section 5, Item 8). It has never been assembled into one enumerable reference for regression purposes, and no persistent membership/exclusion/drift-detection mechanism of the kind described above currently exists.
Dependency sources: TD005-DEP-001, TD005-DEP-003.
Current maturity: PARTIALLY AVAILABLE.
Missing elements: a single enumerable representation of the corpus; the persistent membership/exclusion/drift-detection/reconstruction properties named above; an explicit position on whether Technical Debt Register entries are themselves part of the corpus or tracked exceptions to it (five of seven TD entries remain open/deferred with no explicit statement either way).
Scientific risk: without this capability, a regression capability cannot state, for any given check, which certified contract it protects. Classified High (Section 11).
Required before: Architecture - Mandatory (the corpus's own representation form is an Architecture decision, but its scientific completeness must be assessed first). Specification - the concrete mechanism realizing the capability. Implementation - N/A at this stage.
Traceability: TD005-FR-001 through TD005-FR-022 (all, since every requirement is stated relative to certified behaviour); TD005-CON-001 through TD005-CON-004.

**TD005-CAP-002. Certification-Status Boundary Capability.**
Purpose: determine unambiguously whether a given behavioural contract counts as "certified" when it appears in source code alone, in certification narrative prose, in Architecture/Specification text, or only in the Implementation Baseline's general methodology.
Scientific rationale: TD005-FR-021 requires this boundary; without it, incidental source-code behaviour could be silently treated as a certified contract, or a genuinely certified contract could be silently excluded.
Current repository evidence: no document anywhere states this boundary. The FRA explicitly defers the exact algorithm to Architecture and Specification (TD005-FR-021's own text).
Dependency sources: TD005-DEP-002.
Current maturity: MISSING.
Missing elements: any explicit statement of which document types and evidentiary forms qualify as "certified" for regression-boundary purposes.
Scientific risk: High - directly undermines the central TD005-FR-021 requirement if left unresolved into Implementation.
Required before: Architecture - Mandatory. Specification - refinement into a concrete per-contract-type rule. Implementation - N/A.
Traceability: TD005-FR-021, TD005-FR-018, TD005-FR-020.

### Class B - Behavioural Equivalence Capability

**TD005-CAP-003. Formal Behavioural Equivalence Definition Capability.**
Purpose: formally define what "equivalent" means for regression purposes (exact value, numeric tolerance, normalized, state, event-sequence, temporal/order, contract-conformance, or observational equivalence).
Scientific rationale: TD005-FR-020 establishes that regression is behavioural, not implementation, source, or byte-level, but explicitly does not define the algorithm; this is the FRA's own OQ-006's central content.
Current repository evidence: the principle (behavioural, not byte/source/implementation, equivalence) is established in TD005-FR-020's own normative text. No formal, operational definition of behavioural equivalence exists anywhere in the repository.
Dependency sources: TD005-DEP-004.
Current maturity: MISSING.
Missing elements: an operational, formal definition capable of being consistently applied; this capability currently exists only as a stated principle, not as an applicable definition.
Scientific risk: Critical - every downstream comparison capability (CAP-004, CAP-005, CAP-006, CAP-012) is blocked without it, and its absence creates the single greatest risk of silent collapse into byte/source identity (Section 11).
Required before: Architecture - Mandatory. Specification - the exact comparison contract. Implementation - N/A.
Traceability: TD005-FR-020, TD005-FR-021, TD005-FR-018; OQ-006.

**TD005-CAP-004. Trajectory-vs-Final-State Comparison Model Capability.**
Purpose: determine whether equivalence is defined over the final Tick-Complete state alone or over the complete execution trajectory (the sequence of intermediate stage transitions and events within and across ticks), and confirm that this choice does not conflate logical ordering with wall-clock timing.
Scientific rationale: eight FRA requirements (TD005-FR-001, 003, 006, 007, 008, 009, 010, 017) are properties of the trajectory, not the final state, and cannot be validated by endpoint-only comparison.
Current repository evidence: the SDA itself identifies and enumerates the complete trajectory-required property set (an analytical contribution already made). The logical-order-versus-wall-clock-timing distinction is already fully settled by ADR-010's own text (Section 8 of the SDA), containing no wall-clock or latency language, only sequence language. No formal trajectory representation or comparison model yet exists to act on either finding.
Dependency sources: TD005-DEP-005, TD005-DEP-015, TD005-DEP-017.
Current maturity: PARTIALLY AVAILABLE.
Missing elements: a formal trajectory representation and comparison model; the identification of what must be compared is complete, the formalization of how is not.
Scientific risk: High - a future Architecture defaulting to final-state-only comparison (the simpler of the two models) would leave eight Functional Requirements' own trajectory properties unprotected while appearing, superficially, to satisfy TD-005's own purpose.
Required before: Architecture - Mandatory. Specification - the exact trajectory representation format. Implementation - N/A.
Traceability: TD005-FR-001, TD005-FR-003, TD005-FR-006, TD005-FR-007, TD005-FR-008, TD005-FR-009, TD005-FR-010, TD005-FR-017, TD005-FR-022.

**TD005-CAP-005. Numeric and Categorical Comparison Policy Capability.**
Purpose: define whether floating-point-derived quantities require exact equality, tolerance-bounded, or normalized comparison, and separately confirm which values are categorical/discrete (requiring exact equality by construction) as distinct from continuous financial and risk/performance values.
Scientific rationale: applying a single uniform comparison policy across both categorical and continuous values would produce either false positives (exact equality applied to genuinely tolerant values) or false negatives (tolerance applied to categorical values that must match exactly).
Current repository evidence: the categorical/discrete value set is directly distinguishable from source inspection (`event_type` in `{TRADE_OPENED, SCALE_IN, PARTIAL_CLOSE, TRADE_CLOSED, RUNTIME_FAILURE_EVENT}`; Position Side in `{LONG, SHORT}`), but no document has formally separated this set from the continuous-value set as two distinct comparison-policy domains, and no numeric tolerance policy question (not value) has been resolved. The FRA explicitly excludes selecting a tolerance value as a Non-Goal.
Dependency sources: TD005-DEP-006, TD005-DEP-016.
Current maturity: MISSING.
Missing elements: the numeric comparison policy (not the specific tolerance value); the formal separation of categorical from continuous comparison domains.
Scientific risk: Medium - the categorical/continuous distinction is already evidentially clear even though undocumented, reducing (but not eliminating) the risk relative to CAP-003.
Required before: Architecture - Mandatory. Specification - the exact tolerance value and comparison implementation. Implementation - N/A.
Traceability: TD005-FR-007, TD005-FR-008, TD005-FR-009, TD005-FR-010, TD005-FR-011, TD005-FR-012, TD005-FR-013, TD005-FR-014, TD005-FR-015, TD005-FR-016, TD005-FR-017.

**TD005-CAP-006. Object-Identity-Independent Comparison Capability.**
Purpose: ensure observed equivalence is independent of Python object identity and process-local mutable state (for example, dict/list identity versus value equality).
Scientific rationale: an equivalence check relying inadvertently on object identity rather than value equality would produce false-positive regressions for benign refactors.
Current repository evidence: no document addresses this question at all; it is a genuine, previously unaddressed scientific question distinct from the numeric policy (CAP-005) and the trajectory model (CAP-004).
Dependency sources: TD005-DEP-011.
Current maturity: MISSING.
Missing elements: any explicit statement of value-equality-only comparison as the governing rule.
Scientific risk: Medium - realistic failure mode (benign refactor triggering a false regression) but narrower in blast radius than CAP-003 or CAP-005.
Required before: Architecture - Mandatory. Specification - N/A (the rule itself, once stated, requires no further Specification-level elaboration). Implementation - N/A.
Traceability: TD005-FR-002, TD005-FR-005.

**TD005-CAP-021. Behavioural Vocabulary Stability Capability.**
Purpose: ensure that the terms used throughout the certified corpus (Position, Side, Scale-In, Partial Close, Full Close, Tick-Complete, Canonical Working State, Authoritative Owner, Computational Authority, Runtime Failure Event) have stable, unambiguous, cross-document-consistent definitions.
Scientific rationale: no equivalence or comparison model (CAP-003 through CAP-006) can be built on top of an unstable vocabulary.
Current repository evidence: the Architecture Baseline's own Ownership Terminology section and ADR-009's own Scientific Definitions subsection formally establish this vocabulary; independently cross-checked against actual source-code vocabulary in `run_engine/core/trade_lifecycle.py` and `run_engine/core/position.py` with exact match.
Dependency sources: TD005-DEP-032.
Current maturity: AVAILABLE.
Missing elements: none.
Scientific risk: not applicable (available); residual risk only if a future vocabulary change is made without corresponding governance review.
Required before: Architecture - already satisfied, no further action required. Specification - N/A. Implementation - N/A.
Traceability: all twenty-two Functional Requirements (indirectly, as the vocabulary every requirement is stated in).

### Class C - Observable Behaviour Capability

**TD005-CAP-007. Observable Behavioural Surface Enumeration Capability.**
Purpose: enumerate and classify which runtime outputs and internal observations are scientifically legitimate candidates for regression evaluation (certified external output, certified internal invariant, implementation detail, or incidental intermediate value).
Scientific rationale: treating an implementation detail as a certified output would create a brittle, over-constrained regression capability; treating a certified output as incidental would leave a real regression undetected.
Current repository evidence: the concrete fields are already enumerated precisely (twelve CanonicalState fields, five lifecycle event types, LONG/SHORT side vocabulary, Executor status vocabulary), but no document has classified each field into the four categories above.
Dependency sources: TD005-DEP-007.
Current maturity: PARTIALLY AVAILABLE.
Missing elements: the four-category classification of each already-enumerated field.
Scientific risk: Medium - the enumeration itself (the harder half of the work) is complete; only the classification remains.
Required before: Architecture - Mandatory. Specification - N/A once classified. Implementation - N/A.
Traceability: TD005-FR-003, TD005-FR-004, TD005-FR-005, TD005-FR-006, TD005-FR-013, TD005-FR-014, TD005-FR-015.

**TD005-CAP-008. Non-Interference Observation Boundary Capability.**
Purpose: define an authoritative boundary for how the observable surface can be read without altering the runtime behaviour being observed, and state exactly where observation may legitimately occur.
Scientific rationale: an observation mechanism that reads beyond a confirmed non-interfering boundary could itself violate TD005-CON-001, invalidating the very regression result it produces; TD005-FR-021's own boundary and the FRA's own OQ-001 both bear directly on this.
Current repository evidence: `RunLoop.step()`'s own return value already exposes a Tick-Complete state as a confirmed non-interfering read path. Whether this single read path is sufficient, or whether additional non-interfering observation points are also legitimate, is unresolved.
Dependency sources: TD005-DEP-008, TD005-DEP-019.
Current maturity: PARTIALLY AVAILABLE.
Missing elements: a single, authoritative statement of the complete observation boundary (not merely one confirmed-sufficient point).
Scientific risk: Medium - a working, non-interfering observation point already exists; the risk is scope-incompleteness, not total absence.
Required before: Architecture - Mandatory (this is the FRA's own OQ-001, explicitly deferred to Architecture). Specification - N/A once the boundary is stated. Implementation - N/A.
Traceability: TD005-CON-001, TD005-CON-002, TD005-FR-004, TD005-FR-005, TD005-FR-006; OQ-001.

### Class D - Reference Provenance Capability

**TD005-CAP-009. Reference-Baseline Provenance Capability.**
Purpose: establish a scientifically valid, immutable-or-governed, reproducible provenance for "previously-certified behaviour" against which future runs are compared.
Scientific rationale: without a defined provenance, "previously-certified behaviour" is not itself a reproducible scientific object, undermining TD005-FR-018's own regression-detection purpose; an unreproducible reference cannot itself be certified.
Current repository evidence: two candidate sources exist in principle (the certified units' own historical Implementation/Certification commits, or a baseline freshly established at TD-005 Implementation time - the FRA's own OQ-002), but neither is chosen, no immutability/drift-governance rule exists, and no reproducibility mechanism exists.
Dependency sources: TD005-DEP-012, TD005-DEP-013, TD005-DEP-014.
Current maturity: MISSING.
Missing elements: source selection; an immutability-or-governed-change rule; a reproducibility mechanism connecting the reference back to the certified corpus (CAP-001).
Scientific risk: Critical - every regression comparison (CAP-012) depends on a valid reference; an unreproducible or ungoverned reference invalidates every downstream result even if CAP-003 through CAP-006 are otherwise resolved.
Required before: Architecture - Mandatory. Specification - the exact reproduction mechanism. Implementation - N/A.
Traceability: TD005-FR-018, TD005-FR-019, TD005-FR-021; OQ-002.

### Class E - Deterministic Replay Capability

**TD005-CAP-010. Environmental Determinism Capability.**
Purpose: confirm the active module set contains no wall-clock, network, or non-seeded-randomness dependency, the precondition for repeated-run comparison to be valid at all.
Scientific rationale: TD005-CON-004 and AC-012 (Deterministic Behaviour) both require this; a regression capability whose own execution environment introduces non-determinism could produce false positives or false negatives unrelated to any actual runtime regression.
Current repository evidence: independently re-confirmed a further time for this CGA (Section 5): zero `random`, `time`-for-control-flow, or `datetime.now()` usage across all 14 active modules.
Dependency sources: TD005-DEP-010.
Current maturity: AVAILABLE.
Missing elements: none at the single-run level (see CAP-022 for the distinct, cross-time library-version question).
Scientific risk: not applicable (available); future risk only if a later change introduces non-determinism into an active module without a corresponding regression check (CAP-016, module coverage).
Required before: Architecture - already satisfied. Specification - N/A. Implementation - N/A.
Traceability: TD005-FR-002, TD005-FR-013, TD005-CON-004.

**TD005-CAP-011. Controlled-Condition and Replay Stability Capability.**
Purpose: enumerate the complete set of conditions that must be held equal across two executions for their outputs to be scientifically comparable, and confirm that no Python collection's incidental iteration order introduces spurious non-determinism.
Scientific rationale: tick sequence alone is insufficient without also controlling initial Position, lifecycle history, and regime/strategy state, each of which the active RunLoop consumes; an incomplete controlled-condition set would allow a comparison to run under silently unequal conditions, producing a spurious regression or a false pass.
Current repository evidence: AC-012 implies identical inputs produce identical outputs, but no document enumerates the complete "inputs" set for the Run Engine's own multi-field state; it has not been checked field-by-field whether any active module's observable output relies on an unguaranteed collection-ordering artifact.
Dependency sources: TD005-DEP-009, TD005-DEP-018.
Current maturity: MISSING.
Missing elements: the complete controlled-condition enumeration; the field-by-field ordering-stability check.
Scientific risk: High - both a false-positive and a false-negative failure mode are realistic and would each independently invalidate a regression result.
Required before: Architecture - Mandatory. Specification - the exact enumeration mechanism. Implementation - N/A.
Traceability: TD005-FR-002, TD005-CON-004, TD005-FR-018.

**TD005-CAP-022. Execution-Environment Dependency-Version Stability Capability.**
Purpose: determine whether the identity of the execution environment's own third-party numeric libraries and Python interpreter (pinned per `requirements.txt` - `numpy==2.3.3`, `pandas==2.3.3` - and the interpreter version itself) is a scientific precondition for reproducible floating-point regression comparison across time, distinct from TD005-CON-004's own single-run wall-clock/network/randomness scope.
Scientific rationale: TD005-CON-004 establishes single-run environmental determinism (no wall-clock, network, or unseeded randomness) but says nothing about cross-time reproducibility when the execution environment's own third-party libraries or interpreter change between when a reference baseline is captured (CAP-009) and when a later regression check runs; a numeric library's internal algorithm, its own numeric backend (for example, its BLAS implementation), or the interpreter's own numeric/hash behavior can each change between versions even when the calling code and its inputs are unchanged, which would manifest as an apparent regression that is in fact an environment change, not a Run Engine behavioural change.
Relationship to TD005-CAP-009 (Reference-Baseline Provenance) (V1.1): CAP-022 does not replace CAP-009. CAP-009 governs which historical or freshly-established run is the authoritative reference; CAP-022 contributes one specific fact to that reference's own provenance record - the execution-environment identity (library and interpreter versions) under which the reference was captured. Recording this fact is what allows a future comparison to distinguish a genuine Run Engine behavioural change from a reference-environment drift (the reference was captured under one library/interpreter version, the later check ran under another). CAP-022 may become part of the provenance record CAP-009's own future resolution selects, but CAP-009's resolution does not automatically satisfy CAP-022 unless it explicitly includes this fact.
Relationship to TD005-CAP-011 (Controlled-Condition and Replay Stability) (V1.1): CAP-022 does not replace CAP-011. CAP-011 enumerates the conditions that must be held equal within and across runs at the level of runtime inputs and state (tick sequence, initial Position, lifecycle history, regime/strategy state) and Python-collection ordering stability; CAP-022 refines that same controlled-condition concern along a dimension CAP-011 does not itself name - third-party library and interpreter version identity across time. CAP-022 is distinct from CAP-011's own single-run scope (randomness, clock, network, and initial-state control, already addressed by TD005-DEP-009/DEP-010/DEP-018): CAP-022 concerns whether the environment itself is the same environment across two temporally separated executions, not whether a single execution's own inputs are controlled.
Scientific classification (V1.1): CAP-022 remains a **separate capability**, not merged into CAP-009 or CAP-011 and not demoted to a sub-capability of either. The scientifically correct position, stated explicitly: CAP-009 governs reference provenance (which run is authoritative); CAP-011 governs controlled replay conditions (which inputs and states must match within and across runs); CAP-022 identifies one specific cross-time environment-stability capability required by both, answering a question neither CAP-009 nor CAP-011 individually poses - whether the execution environment's own third-party numeric libraries and interpreter remain identical (or are otherwise accounted for) between reference capture and later comparison. This is a classification decision only; no implementation, storage mechanism, or comparison algorithm is chosen here.
Current repository evidence: freshly discovered for this CGA (Section 5, Item 3 and Item 9), not present in the FRA or the SDA. Exactly one active module, `run_engine/core/regime.py`, imports `numpy`/`pandas` directly. `requirements.txt` pins every dependency to an exact version (`==`), evidencing that version-exactness already matters to this repository's own maintenance practice, but no governance document connects this practice to TD-005's own regression-validity requirement. This review's own hidden-assumption audit (Section 13) additionally confirms that Python interpreter version and numeric-backend/BLAS implementation are the same category of concern as the numpy/pandas library-version finding, and are treated as within CAP-022's own existing scope (Purpose, above) rather than as separate capabilities.
Dependency sources: none in the accepted SDA (this is a hidden assumption newly surfaced by this CGA, per Section 12; it is anchored to TD005-DEP-010 and TD005-DEP-014 by scientific proximity, not by SDA citation, since the SDA does not name it).
Current maturity: MISSING.
Missing elements: any explicit statement of whether execution-environment library/interpreter-version identity is part of the controlled-condition set (CAP-011) or the reference-baseline provenance requirement (CAP-009), or is recorded as its own distinct provenance field; this capability does not yet exist even as a named scientific question prior to this CGA.
Scientific risk: Medium - the exposure is narrow (one module, two libraries, plus the interpreter itself) but the failure mode (an apparent regression that is actually a library or interpreter upgrade) is realistic and would be difficult to diagnose without this capability being named.
Required before: Architecture - Optional (a genuine, narrowly-scoped gap, but not part of the SDA's own minimal prerequisite capability set; Architecture may reasonably choose to fold this into CAP-009/CAP-011's own resolution rather than treat it as a separate track). Specification - if deferred from Architecture, must be resolved here at the latest. Implementation - N/A.
Traceability: TD005-CON-004 (by scientific proximity, not shared normative text); TD005-CAP-009 (reference-provenance relationship, above); TD005-CAP-011 (controlled-condition relationship, above). No direct FRA or SDA citation exists, consistent with this capability's own status as a newly surfaced hidden assumption (Section 13).

### Class F - Regression Classification Capability

**TD005-CAP-012. Regression Classification Capability.**
Purpose: given an observed deviation, evaluate it against the certified-contract boundary and determine whether it constitutes a genuine behavioural regression or a non-regression (an incidental, non-certified, or environment-caused difference).
Atomicity review (V1.1): an explicit search of the accepted FRA and SDA for severity-ranking, business-acceptability, waiver, disposition, and remediation-priority language found zero occurrences in either document. The FRA requires only detection of deviation and classification as behavioural regression or non-regression (TD005-FR-018, TD005-FR-020, TD005-FR-021); it neither requires nor names severity ranking, acceptability thresholds, or waiver/disposition decisions anywhere. These concerns are therefore not later governance activities deferred from TD-005's own scope, nor Specification concerns awaiting refinement - they are simply outside the accepted scientific baseline entirely, and TD-005 does not own them. Disposition: **Option B - refine wording without splitting.** CAP-012 remains one scientifically atomic capability: detection of a deviation and its classification as regression-or-not are two facets of a single, inseparable scientific judgment - a deviation cannot be "detected" for TD-005's own purposes except by simultaneously asking whether it violates a certified contract, which is exactly the classification act. There is no independent, freestanding "detection" capability upstream of "classification" that the accepted FRA/SDA define separately; they define only the one joint capability this entry already names.
CAP-012 explicitly includes: evaluation of an observed deviation against the certified-contract boundary (CAP-002); determination of whether that deviation violates a certified behavioural contract, using the formal equivalence definition (CAP-003 through CAP-006); classification of the outcome as regression or non-regression.
CAP-012 explicitly excludes: severity ranking; business acceptability; waiver decisions; remediation priority; operational disposition. None of these five is required by the accepted FRA or SDA; if any is ever needed, it would require its own future Functional Requirement and its own future capability, not an extension of CAP-012.
Scientific rationale: this is the capability that directly answers TD-005's own governing scientific question; it is the point at which the certified-contract boundary (CAP-002), the formal equivalence definition (CAP-003 through CAP-006), and coverage completeness (CAP-015) must jointly operate.
Current repository evidence: none of its prerequisite capabilities (CAP-002 through CAP-006, CAP-015) is currently AVAILABLE; this capability is therefore necessarily unavailable as a composite, regardless of any one prerequisite's own maturity.
Dependency sources: TD005-DEP-002, TD005-DEP-004, TD005-DEP-020.
Current maturity: MISSING.
Missing elements: everything; this is a Derived capability with no independent content beyond the composition of CAP-002 through CAP-006 and CAP-015.
Scientific risk: Critical - this is TD-005's own central deliverable capability; every other gap in this document ultimately matters because it blocks this one.
Required before: Architecture - Mandatory (Architecture must define how classification composes its prerequisite capabilities, even though it cannot yet resolve every prerequisite itself). Specification - the exact classification procedure. Implementation - N/A.
Traceability: TD005-FR-018, TD005-FR-020, TD005-FR-021.

### Class G - Evidence Collection Capability

**TD005-CAP-013. Evidence Composition Capability.**
Purpose: define the complete set of evidence elements a detected regression must produce for independent reproduction and certification.
Scientific rationale: TD005-FR-019 requires sufficient detail for independent reproduction; incomplete evidence composition would defeat this purpose even if a regression is correctly detected.
Current repository evidence: the FRA's own TD005-FR-019 already names four minimum elements (affected tick, affected stage or component, expected value, actual value). The SDA identifies four further elements not yet named in the FRA: input provenance, initial-state provenance, the specific certified-contract ID, and execution-environment identity.
Dependency sources: TD005-DEP-023.
Current maturity: PARTIALLY AVAILABLE.
Missing elements: the four SDA-identified refinement elements remain unadopted into any binding requirement.
Scientific risk: Medium - a reported regression missing input or initial-state provenance could be technically detected but practically unreproducible.
Required before: Architecture - Optional (the FRA's own four elements are already sufficient for Architecture to proceed; the SDA's refinement can be adopted during Architecture or deferred to Specification without blocking progress). Specification - the refinement's exact adoption. Implementation - N/A.
Traceability: TD005-FR-019.

**TD005-CAP-014. Evidence Persistence and Continuity Capability.**
Purpose: define whether detected-regression evidence must be persisted consistent with this project's own established governance-document conventions, and whether evidence and results from one Long-Duration-Validation stage must be preserved and cross-referenced at the next.
Scientific rationale: unmanaged evidence persistence could lose regression evidence needed for a later Final Certification, or accumulate governance-document sprawl inconsistent with Repository Consolidation's own Normative Repository Boundary (TD005-CON-003); without evidence continuity, a regression introduced between validation stages could be harder to attribute to a specific stage transition.
Current repository evidence: no FRA item or Baseline text addresses evidence persistence; the established `docs/architecture/certification/` convention exists for governance-level certification evidence, but whether individual regression-check evidence must follow the same convention is undefined. The Implementation Baseline's own "every validation stage shall complete successfully before the next duration is attempted" implies continuity is required, but does not define what it requires.
Dependency sources: TD005-DEP-024, TD005-DEP-027.
Current maturity: MISSING.
Missing elements: a persistence-format decision; a continuity mechanism across the six Long-Duration-Validation stages.
Scientific risk: Medium - primarily a governance-hygiene risk rather than a correctness risk; a missed regression is not directly caused by this gap, but the ability to later prove one was (or was not) missed is.
Required before: Architecture - Optional. Specification - Mandatory (this is properly a Specification-level format decision). Implementation - N/A.
Traceability: TD005-FR-019, TD005-FR-022.

### Class H - Coverage Capability

**TD005-CAP-015. Contract-to-Requirement Coverage Capability.**
Purpose: confirm every certified contract in the corpus (CAP-001) is traceable to at least one FRA Functional Requirement, and every Functional Requirement is traceable to at least one certified contract, with any gap explicitly identified.
Scientific rationale: an uncovered certified contract could regress without any Functional Requirement detecting it; an FRA requirement with no certified-contract anchor would not be a genuine regression-protection requirement at all.
Current repository evidence: a citation-frequency check (independently reproduced during the preceding SDA and re-confirmed unchanged for this CGA) found: AC-003 (Separation of Ownership and Computation) is only partially instantiated - covered for RiskEngine specifically (TD005-FR-013) but not generalized across all components; AC-011 (Scientific Traceability) has no corresponding FR at all - TD005-FR-006 is related but narrower; AC-013 (Architecture Consistency) is correctly outside TD-005's own runtime-behavioral scope, being a document-consistency criterion.
Dependency sources: TD005-DEP-020.
Current maturity: PARTIALLY AVAILABLE.
Missing elements: an FR-level requirement (or an explicit, justified non-requirement) addressing AC-011's own end-to-end traceability property; a generalized AC-003 requirement beyond RiskEngine.
Scientific risk: High - AC-011's own uncovered property could regress without any FRA requirement detecting it; this is a concrete, evidenced gap, not a hypothetical one.
Required before: Architecture - Mandatory (the AC-011 gap must be assessed as a candidate new capability need). Specification - N/A once assessed. Implementation - N/A.
Traceability: all twenty-two Functional Requirements (completeness check spans the whole set); specifically TD005-FR-013 (AC-003), TD005-FR-006 (AC-011 gap).

**TD005-CAP-016. Module and State-Transition Coverage Capability.**
Purpose: confirm all fourteen active modules, and the certified state-transition table (ADR-009), are covered by the Functional Requirements, and choose which coverage concept (module, contract, domain, state-transition, event, requirement, path, risk-based) is scientifically appropriate for TD-005.
Scientific rationale: module coverage alone does not guarantee state-transition coverage of ADR-009's own five-row Lifecycle Transition Table, since a module could be "covered" by a requirement that exercises only one of its several certified transitions.
Current repository evidence: a direct count (independently reproduced during the preceding SDA and re-confirmed unchanged for this CGA, Section 5) found four of the fourteen active modules - `run_engine/main.py`, `run_engine/core/state.py`, `run_engine/core/regime.py`, `run_engine/core/execution/__init__.py` - have zero direct citations in the FRA's own Section 17.1 traceability table. Functional coverage may be implied but is not explicitly, individually traced. No coverage-concept choice has been made anywhere.
Dependency sources: TD005-DEP-021, TD005-DEP-022.
Current maturity: MISSING.
Missing elements: explicit, individually-traced requirement-to-module mapping for the four modules; a chosen coverage concept (or combination).
Scientific risk: High - a genuine regression confined to one of the four modules could occur without any Functional Requirement explicitly designed to detect it; this is a concrete, evidenced gap.
Required before: Architecture - Mandatory. Specification - the concrete coverage mechanism. Implementation - N/A.
Traceability: FRA Section 13.1 (Active Module Coverage Obligation); indirectly TD005-FR-001, TD005-FR-002; TD005-FR-007, TD005-FR-008, TD005-FR-009, TD005-FR-010.

### Class I - Repository Boundary Protection Capability

**TD005-CAP-017. Active/Deferred Scope Stability Capability.**
Purpose: maintain a stable, independently-reproducible definition of "the active Run Engine," correctly justify the exclusion of the four RETAIN-Deferred-Scope files from TD-005's own active scope, and ensure the regression capability's own module-coverage check remains sensitive to any future change in the active/inactive partition.
Scientific rationale: every other capability in this inventory presupposes a stable definition of what is currently in scope; a scope-blind coverage mechanism would silently miss a future reactivation of a currently-deferred module.
Current repository evidence: the active/inactive partition itself is independently re-derived and confirmed identical across every governance document to date, including this CGA's own fresh derivation (Section 5); the current exclusion of the four RETAIN-Deferred-Scope files is directly and currently justified. No mechanism-independent scientific requirement for automatic drift detection has yet been stated (this is the FRA's own OQ-003's unresolved half).
Dependency sources: TD005-DEP-028, TD005-DEP-029, TD005-DEP-031.
Current maturity: PARTIALLY AVAILABLE.
Missing elements: a scope-drift-sensitivity requirement for the future coverage mechanism (CAP-016).
Scientific risk: Low - the condition this would protect against (one of the four files re-entering active scope) is not currently true and would itself require a separate, governed activation event to occur first.
Required before: Architecture - already sufficiently available for Architecture to proceed on the current scope; the drift-sensitivity requirement is Optional at the Architecture stage. Specification - if deferred, resolved here. Implementation - N/A.
Traceability: FRA Section 6.3 (evidence); OQ-003.

**TD005-CAP-018. Executor Namespace Integrity Capability.**
Purpose: classify FRA Section 13.2's own deferred obligation (Executor namespace uniqueness) precisely as a repository-integrity dependency inherited from Repository Consolidation's own RC-AD-004, not a Run Engine behavioral semantic, to avoid TD-005 silently absorbing a different governance unit's own already-certified scope.
Scientific rationale: conflating this with general behavioral regression could cause a future Architecture to over-scope TD-005 into Repository Consolidation's own separate, already-certified governance concern.
Current repository evidence: the classification itself is already correct and stated in the FRA. The underlying fact (exactly one `Executor` reachable from `run_engine.main`) is independently re-confirmed true (Section 5). The check protecting it going forward is historically specific to a Repository Consolidation defect, already resolved and certified (Repository Consolidation Final Certification), not a general Run Engine behavioural semantic TD-005 itself needs to own.
Dependency sources: TD005-DEP-030.
Current maturity: OUTSIDE TD-005 SCOPE, as a general behavioral capability. Independently AVAILABLE as a currently-holding repository-integrity fact (already certified by a different governance unit).
Missing elements: none within TD-005's own scope; a lightweight repository-integrity check, if ever formalized, belongs alongside, not inside, TD-005.
Scientific risk: not applicable within TD-005's own scope; the only risk is scope-creep, addressed by this capability's own correct classification.
Required before: Architecture - not required within TD-005; Architecture should explicitly not absorb this. Specification - N/A within TD-005. Implementation - N/A within TD-005.
Traceability: FRA Section 13.2 (Repository-Integrity Regression Obligation).

### Class J - Governance Integration Capability

**TD005-CAP-019. Governance Sequencing Capability.**
Purpose: ensure TD-005's own resolution proceeds through the established FRA, SDA, CGA, Architecture, Specification, Implementation, Final Certification sequence, consistent with every other governance unit in this repository.
Scientific rationale: skipping ahead of this sequence would produce architecture or implementation decisions ungrounded in a completed scientific analysis, exactly the failure this repository's own governance discipline exists to prevent.
Current repository evidence: this CGA's own existence, scope, and explicit refusal to select architecture, framework, or implementation is itself direct evidence this capability is being honored; the same sequence was independently followed and CERTIFIED for all six prior certified units and for Repository Consolidation.
Dependency sources: TD005-DEP-033.
Current maturity: AVAILABLE.
Missing elements: none.
Scientific risk: not applicable (available).
Required before: Architecture - already satisfied. Specification - N/A. Implementation - N/A.
Traceability: all FRA items (procedurally).

**TD005-CAP-020. Long-Duration-Validation Integration Capability.**
Purpose: determine the capability's own feasible application model across the six mandatory Long-Duration-Validation stages (Functional smoke through 30-day validation): execution-time budget, pre-run-versus-post-run application, and evidence continuity across stages.
Scientific rationale: the same capability (TD005-FR-022) must be usable, without modification, before each of the six stages; an execution-time profile or application model incompatible with the fastest stage would delay or discourage its use exactly where early regression detection matters most.
Current repository evidence: the Implementation Baseline's own six-stage sequence is fully documented (Section 8, Item 8; re-confirmed for this CGA), but no document resolves the execution-time tension, the pre/post-run application model, or evidence continuity across stages (the FRA's own OQ-004, left explicitly unresolved as an Architecture-level tradeoff).
Dependency sources: TD005-DEP-025, TD005-DEP-026, TD005-DEP-027.
Current maturity: MISSING.
Missing elements: an execution-time feasibility resolution; an application-model choice; an evidence-continuity mechanism (shared with CAP-014).
Scientific risk: Medium - a capability that is otherwise scientifically valid but practically unusable at one or more stages would undermine TD-005's own operational purpose without invalidating any single comparison result.
Required before: Architecture - Mandatory (the tension itself, per the FRA's own OQ-004 disposition, is an Architecture-level tradeoff). Specification - the exact application mechanics. Implementation - N/A.
Traceability: TD005-FR-022, TD005-FR-019; OQ-004.

### 7.1 Capability Atomicity Audit (V1.1)

Every capability was re-examined against five questions: does it answer one coherent scientific question; does it contain multiple independent outputs; does it merely aggregate related dependencies; could one part be available while another is missing in a way that makes the maturity label misleading; would splitting improve scientific clarity without artificial fragmentation. Particular attention was given to the ten capabilities the governing task named:

- **TD005-CAP-001.** One question (does an authoritative, reproducible certified-contract reference exist). Multiple missing elements (assembly, membership rule, TD-Register position) are facets of the same single capability, not independent outputs - none is meaningful without the others. No split.
- **TD005-CAP-004.** One question (what comparison model applies to trajectory properties). The trajectory-required-set enumeration and the logical-order/wall-clock distinction are both prerequisites feeding the same single comparison-model question, not separate deliverables. No split.
- **TD005-CAP-005.** One question (what comparison policy applies to numeric and categorical values). The categorical/continuous distinction is evidence supporting one policy decision, not two policies; a numeric-only or categorical-only capability would each be meaningless without the other half of the same classification. No split.
- **TD005-CAP-009.** One question (what is the authoritative, reproducible reference). Source selection, immutability/governance, and reproducibility are three necessary conditions of one reference-provenance capability, not three capabilities - a reference that is selected but not reproducible, or reproducible but not governed against drift, would not satisfy TD005-FR-018 in either case. No split.
- **TD005-CAP-011.** One question (what conditions must be held equal for comparability). The condition enumeration and the ordering-stability check both serve the same single controlled-condition capability. No split.
- **TD005-CAP-012.** Reviewed in full above (Atomicity review, V1.1); confirmed atomic, wording refined (Option B), no split.
- **TD005-CAP-014.** One question (how is evidence persisted and carried across stages). Persistence format and cross-stage continuity are two facets of the same evidence-governance capability, not independent outputs - a persistence decision without continuity would not satisfy TD005-FR-022's own multi-stage requirement. No split.
- **TD005-CAP-017.** One question (what is the stable current scope, and is the coverage mechanism sensitive to its future change). Both facets concern the same scope-stability capability; the "why currently excluded" and "how would drift be detected" portions are two temporal aspects (current state, future robustness) of one question, addressed in the Capability Layer Rationale (Section 8). No split.
- **TD005-CAP-020.** One question (is the capability usable, without modification, across all six validation stages). Execution-time, application-model, and continuity are three conditions of the same single usability question - a capability usable at five of six stages would not satisfy TD005-FR-022 at all. No split.
- **TD005-CAP-022.** One question (does execution-environment version identity matter for cross-time comparison). Reviewed in full above (Relationship subsections, V1.1); confirmed a separate, atomic capability, not a sub-capability of CAP-009 or CAP-011. No split.

No capability among the remaining twelve (CAP-002, CAP-003, CAP-006, CAP-007, CAP-008, CAP-010, CAP-013, CAP-015, CAP-016, CAP-018, CAP-019, CAP-021) showed evidence of combining independent scientific questions; each answers exactly one question stated in its own Purpose field. This audit confirms the capability count of twenty-two is unchanged; no split or merge was performed anywhere in this document.

## 8. Capability Dependency Graph

Independently derived from capability-to-capability prerequisite relationships (not copied from the SDA's own dependency-level graph, and not identical to it, since capabilities aggregate multiple dependencies each).

**Foundational capabilities** (no prerequisite capability; every other capability ultimately rests on these):
TD005-CAP-001 (Certified-Contract Corpus Authority), TD005-CAP-010 (Environmental Determinism), TD005-CAP-017 (Active/Deferred Scope Stability), TD005-CAP-019 (Governance Sequencing), TD005-CAP-021 (Behavioural Vocabulary Stability).

**Intermediate capabilities** (depend only on Foundational capabilities, or on other Intermediate capabilities):
TD005-CAP-002 (Certification-Status Boundary) <- CAP-001.
TD005-CAP-007 (Observable Behavioural Surface Enumeration) <- CAP-001, CAP-017.
TD005-CAP-008 (Non-Interference Observation Boundary) <- CAP-007.
TD005-CAP-009 (Reference-Baseline Provenance) <- CAP-001, CAP-002.
TD005-CAP-011 (Controlled-Condition and Replay Stability) <- CAP-010, CAP-017.
TD005-CAP-013 (Evidence Composition) <- CAP-002, CAP-009, CAP-011.
TD005-CAP-015 (Contract-to-Requirement Coverage) <- CAP-001, CAP-017.
TD005-CAP-018 (Executor Namespace Integrity) <- CAP-017.
TD005-CAP-022 (Execution-Environment Dependency-Version Stability) <- CAP-010.

**Derived capabilities** (depend on one or more Intermediate capabilities, and represent the scientific outcomes Architecture and Specification directly consume):
TD005-CAP-003 (Formal Behavioural Equivalence Definition) <- CAP-001, CAP-002, CAP-007.
TD005-CAP-004 (Trajectory-vs-Final-State Comparison Model) <- CAP-003.
TD005-CAP-005 (Numeric and Categorical Comparison Policy) <- CAP-003, CAP-007.
TD005-CAP-006 (Object-Identity-Independent Comparison) <- CAP-003, CAP-007.
TD005-CAP-012 (Regression Classification) <- CAP-002, CAP-003, CAP-004, CAP-005, CAP-006, CAP-015.
TD005-CAP-014 (Evidence Persistence and Continuity) <- CAP-013.
TD005-CAP-016 (Module and State-Transition Coverage) <- CAP-015, CAP-004.
TD005-CAP-020 (Long-Duration-Validation Integration) <- CAP-014, CAP-019.

No circular relationship exists: every capability's own prerequisite list resolves, through a finite chain, to one or more Foundational capabilities with no cycle back. The nearest structural pattern to a cycle is the mutual informativeness between CAP-015 (Contract-to-Requirement Coverage) and CAP-016 (Module and State-Transition Coverage) - CAP-016 depends on CAP-015, not the reverse, so this remains strictly layered.

### Capability Layer Rationale (V1.1)

The three layers are assigned by one criterion each, applied consistently to all twenty-two capabilities, independent of a capability's own current maturity:

- **Foundational.** A capability has no prerequisite capability within TD-005's own inventory, and it establishes authority, scope, vocabulary, determinism, or governance conditions required by multiple downstream capability families. Foundational status is a statement about structural prerequisite position, not about completeness - a Foundational capability can be PARTIALLY AVAILABLE, or even MISSING, and remain Foundational, provided nothing else in the inventory is its own prerequisite.
- **Intermediate.** A capability transforms a Foundational condition into a usable scientific reference, observability, provenance, evidence, or coverage structure; it is a prerequisite for one or more Derived decision capabilities; it does not itself produce the final regression determination.
- **Derived.** A capability composes multiple upstream (Foundational and/or Intermediate) capabilities; it produces the actual comparison, classification, coverage-completeness, evidence-continuity, or validation-integration outcome; it cannot be scientifically defined without its own upstream capabilities already being named.

Every capability's own layer placement was re-verified against these three criteria for this review; none required moving. Four apparent edge cases are addressed explicitly, since each could otherwise look like a misclassification:

- **TD005-CAP-001 as Foundational despite being PARTIALLY AVAILABLE.** Maturity and layer are independent axes. CAP-001 has no prerequisite capability within TD-005 (nothing else in this inventory must exist before the certified corpus can be said to exist in substance), and every other capability that touches "certified behaviour" (CAP-002, CAP-007, CAP-009, CAP-015, and transitively CAP-003 through CAP-006, CAP-012, CAP-016) depends on it. Its incomplete maturity (Section 7, Section 9) is exactly the gap this CGA reports; it does not change its structural position as a prerequisite for everything downstream.
- **TD005-CAP-017 as Foundational although its own drift-detection portion is unresolved.** The same reasoning applies: CAP-017's own current-exclusion portion is a precondition every scope-dependent capability (CAP-007, CAP-011, CAP-015, and transitively CAP-016) relies on today, and nothing in this inventory is a prerequisite for CAP-017 itself. Its one unresolved portion (scope-drift sensitivity, Low risk, Section 12) is a missing element within an otherwise-Foundational capability, not a reason to reclassify it as Intermediate or Derived - reclassification would incorrectly imply that some other capability must exist before CAP-017 can, which is not the case.
- **TD005-CAP-003 as Derived rather than Foundational.** CAP-003 (Formal Behavioural Equivalence Definition) explicitly composes CAP-001 (the corpus to be equivalent against), CAP-002 (the certification boundary defining what counts), and CAP-007 (the observable surface being compared) - three upstream capabilities, each independently necessary. A capability that cannot be scientifically stated without first naming three others is, by the Derived criterion above, Derived, regardless of how scientifically central its own content is (Section 12 rates it Critical risk precisely because it is both Derived and blocking). Centrality and layer position are independent; TD-005's own most important capability is not required to be Foundational.
- **TD005-CAP-022 as Intermediate.** CAP-022 transforms a Foundational condition (CAP-010, Environmental Determinism, the single-run precondition) into a specific cross-time refinement applicable to reference capture and replay; it is a direct prerequisite for two Intermediate capabilities' own full resolution (CAP-009, CAP-011, per the relationship subsections in Section 7) but does not itself produce a final regression determination, coverage outcome, or evidence-continuity result - it produces a scientific reference/replay refinement, exactly the Intermediate criterion above. It is not Foundational, since it presupposes CAP-010; it is not Derived, since nothing composes it into a final decision output on its own - CAP-009 and CAP-011 each independently consume it.

## 9. Capability Gap Assessment

For every capability that is not AVAILABLE, this section states what already exists, what is missing, why it cannot yet satisfy TD-005, and the minimum additional capability required, without prescribing implementation.

- **CAP-001 (PARTIALLY AVAILABLE).** Exists: the certified corpus in substance, across eleven-plus documents. Missing: single enumerable assembly; TD Register scope position. Cannot yet satisfy TD-005 because: a regression check cannot cite "the corpus" as a single authority. Minimum additional capability: an assembly mechanism producing one enumerable reference, and an explicit TD-Register-scope statement.
- **CAP-002 (MISSING).** Exists: nothing beyond the FRA's own statement that a boundary is needed. Missing: the boundary itself. Cannot yet satisfy TD-005 because: without it, "certified" is undefined for regression purposes. Minimum additional capability: an explicit statement of qualifying evidentiary forms.
- **CAP-003 (MISSING).** Exists: the principle (behavioural, not byte/source/implementation). Missing: the operational definition. Cannot yet satisfy TD-005 because: a principle alone cannot be mechanically applied. Minimum additional capability: a formal, applicable definition of behavioural equivalence.
- **CAP-004 (PARTIALLY AVAILABLE).** Exists: the trajectory-required property set (fully enumerated) and the logical-order/wall-clock distinction (fully settled). Missing: the formal trajectory representation and comparison model itself. Cannot yet satisfy TD-005 because: enumeration of what must be compared is not the same as a model for comparing it. Minimum additional capability: a trajectory representation and comparison model.
- **CAP-005 (MISSING).** Exists: the categorical value set (evidenced, undocumented) and the FRA's own explicit tolerance-value Non-Goal. Missing: the comparison policy question itself. Cannot yet satisfy TD-005 because: no policy exists to apply, independent of the specific value later chosen. Minimum additional capability: a stated numeric-versus-categorical comparison policy.
- **CAP-006 (MISSING).** Exists: nothing. Missing: everything. Cannot yet satisfy TD-005 because: the question has never been asked in any governance document. Minimum additional capability: an explicit value-equality-only comparison rule.
- **CAP-007 (PARTIALLY AVAILABLE).** Exists: precise field enumeration. Missing: four-category classification. Cannot yet satisfy TD-005 because: enumeration without classification cannot distinguish certified output from implementation detail. Minimum additional capability: the classification itself.
- **CAP-008 (PARTIALLY AVAILABLE).** Exists: one confirmed non-interfering read path. Missing: a complete, authoritative boundary statement. Cannot yet satisfy TD-005 because: sufficiency of the single path for every future observation need is unconfirmed. Minimum additional capability: an authoritative, complete boundary statement.
- **CAP-009 (MISSING).** Exists: two candidate provenance sources, unselected. Missing: selection, immutability/governance rule, reproducibility mechanism. Cannot yet satisfy TD-005 because: "previously-certified behaviour" is not yet a reproducible scientific object. Minimum additional capability: a selected, governed, reproducible reference-baseline provenance.
- **CAP-011 (MISSING).** Exists: AC-012's own general determinism guarantee. Missing: the complete controlled-condition enumeration and ordering-stability check. Cannot yet satisfy TD-005 because: "identical inputs" is undefined at the multi-field state level the Run Engine actually has. Minimum additional capability: the enumeration and the check.
- **CAP-012 (MISSING).** Exists: nothing independently; wholly derived from CAP-002 through CAP-006 and CAP-015. Missing: everything, by composition. Cannot yet satisfy TD-005 because: it is TD-005's own central deliverable and every prerequisite is itself incomplete. Minimum additional capability: resolution of its prerequisites; no independent capability content of its own.
- **CAP-013 (PARTIALLY AVAILABLE).** Exists: four FRA-named minimum evidence elements. Missing: four SDA-identified refinement elements. Cannot yet satisfy TD-005 because: the FRA's own four elements alone would produce technically-detected but practically-unreproducible evidence in some cases. Minimum additional capability: adoption of the four refinement elements.
- **CAP-014 (MISSING).** Exists: an established governance-document persistence convention for certification-level evidence. Missing: any decision on whether regression-check evidence follows it. Cannot yet satisfy TD-005 because: evidence could be lost or could accumulate inconsistently without a stated convention. Minimum additional capability: a persistence-and-continuity decision.
- **CAP-015 (PARTIALLY AVAILABLE).** Exists: near-complete coverage, with two specifically evidenced gaps (AC-011, AC-003 generalization). Missing: closure of those two gaps. Cannot yet satisfy TD-005 because: AC-011's own property could regress undetected. Minimum additional capability: an AC-011-covering requirement (or an explicit, justified non-requirement) and an AC-003 generalization decision.
- **CAP-016 (MISSING).** Exists: an implied-but-untraced coverage for four modules; no coverage-concept choice. Missing: explicit per-module tracing; a coverage-concept decision. Cannot yet satisfy TD-005 because: implied coverage is not verifiable coverage. Minimum additional capability: explicit module-level traceability and a coverage-concept choice.
- **CAP-017 (PARTIALLY AVAILABLE).** Exists: a stable, correctly-justified current exclusion. Missing: scope-drift sensitivity for the future. Cannot yet satisfy TD-005 because: the current state is sound, but the mechanism protecting it against future drift does not yet exist. Minimum additional capability: a drift-sensitivity requirement.
- **CAP-020 (MISSING).** Exists: the six-stage sequence itself, fully documented. Missing: execution-time, application-model, and continuity resolutions. Cannot yet satisfy TD-005 because: TD005-FR-022 requires usability at all six stages without modification, and this is currently unconfirmed. Minimum additional capability: resolution of the three named tensions.
- **CAP-022 (MISSING).** Exists: the underlying fact (one module, two pinned libraries) and the general repository practice of version pinning. Missing: any connection between that practice and TD-005's own regression-validity requirement. Cannot yet satisfy TD-005 because: a library-version-induced numeric difference could currently be misclassified as a genuine behavioural regression. Minimum additional capability: an explicit statement of whether library-version identity belongs to the controlled-condition set (CAP-011) or the reference-baseline provenance requirement (CAP-009).

## 10. Architecture Readiness

**Mandatory** (must be at least authoritatively analyzed and explicitly addressed within Architecture before Specification can proceed): TD005-CAP-001, TD005-CAP-002, TD005-CAP-003, TD005-CAP-004, TD005-CAP-005, TD005-CAP-006, TD005-CAP-007, TD005-CAP-008, TD005-CAP-009, TD005-CAP-011, TD005-CAP-012, TD005-CAP-015, TD005-CAP-016, TD005-CAP-020.

**Optional** (Architecture may resolve these or explicitly defer them to Specification without blocking progress): TD005-CAP-013, TD005-CAP-014, TD005-CAP-017 (drift-sensitivity portion only; the current-exclusion portion is already sufficient), TD005-CAP-022.

**Deferred** (correctly outside Architecture's own scope; already satisfied or correctly excluded): TD005-CAP-010, TD005-CAP-018, TD005-CAP-019, TD005-CAP-021 (all four already AVAILABLE or OUTSIDE TD-005 SCOPE, requiring no Architecture action beyond acknowledgement).

This distribution mirrors the SDA's own Minimal Prerequisite Scientific Capability statement (SDA Section 13): the capabilities already AVAILABLE there (vocabulary, active scope, environmental determinism) are exactly TD005-CAP-021, TD005-CAP-017, TD005-CAP-010 here; the two capabilities the SDA identified as remaining unresolved at the Architecture-readiness level (corpus enumeration/boundary, formal equivalence definition) are exactly TD005-CAP-001/TD005-CAP-002 and TD005-CAP-003 here.

## 11. Specification Readiness

Capabilities intentionally deferred until Specification, not solved here:

- TD005-CAP-001's exact assembly mechanism (format, location, maintenance process).
- TD005-CAP-002's per-contract-type application rule, once the boundary principle is set by Architecture.
- TD005-CAP-004's exact trajectory representation format.
- TD005-CAP-005's exact tolerance value(s) and comparison implementation.
- TD005-CAP-009's exact reference-reproduction mechanism.
- TD005-CAP-011's exact controlled-condition enumeration mechanism.
- TD005-CAP-012's exact classification procedure.
- TD005-CAP-013's exact adoption of the four refinement evidence elements.
- TD005-CAP-014's exact persistence format and continuity mechanism.
- TD005-CAP-016's exact coverage mechanism, once the coverage concept is chosen by Architecture.
- TD005-CAP-020's exact application mechanics across the six validation stages.
- TD005-CAP-022's exact resolution, if Architecture defers it (Section 10).

None of these is solved in this document; each is named so it is not silently lost between governance stages.

## 12. Risk Assessment

### Maturity and Risk Review (V1.1)

All twenty-two current maturity assignments (Section 7) and all eighteen risk ratings (table below) were reassessed for this review. None changed: no repository evidence gathered during this review's own targeted checks (fresh scans confirming zero environment-variable reads, zero concurrency imports, and an unchanged active/inactive module set) contradicted any existing assignment. Specifically re-verified per the governing task's own explicit list: TD005-CAP-001 remains PARTIALLY AVAILABLE (Section 7, now with an expanded justification, not a maturity change); TD005-CAP-012 remains MISSING (Section 7, wording refined, not re-statused); TD005-CAP-017 remains PARTIALLY AVAILABLE; TD005-CAP-022 remains MISSING with Medium risk; TD005-CAP-018 remains OUTSIDE TD-005 SCOPE as a behavioural capability, independently AVAILABLE as a repository-integrity fact. The maturity distribution (3 AVAILABLE, 7 PARTIALLY AVAILABLE, 11 MISSING, 1 OUTSIDE TD-005 SCOPE) and the risk distribution below are both unchanged from V1.0.

Risk is classified per missing or partially available capability, justified against the concrete failure mode each gap would produce if carried unresolved into Implementation.

| Capability | Risk | Justification |
|---|---|---|
| TD005-CAP-001 | High | Without assembly, no regression check can cite a single certified authority; this is the foundation every other capability rests on. |
| TD005-CAP-002 | High | Directly undermines TD005-FR-021; incidental behaviour could be silently certified, or genuine certified behaviour silently excluded. |
| TD005-CAP-003 | Critical | Blocks CAP-004, CAP-005, CAP-006, and CAP-012 entirely; highest risk of silent collapse into byte/source identity, the exact failure TD005-FR-020 exists to prevent. |
| TD005-CAP-004 | High | A future default to final-state-only comparison would leave eight Functional Requirements' trajectory properties unprotected while appearing superficially complete. |
| TD005-CAP-005 | Medium | The categorical/continuous distinction is already evidentially clear even though undocumented, reducing but not eliminating exposure. |
| TD005-CAP-006 | Medium | Realistic failure mode (false regression on a benign refactor) but narrower blast radius than CAP-003 or CAP-005. |
| TD005-CAP-007 | Medium | The harder half (enumeration) is complete; only classification remains, bounding the risk. |
| TD005-CAP-008 | Medium | A working non-interfering observation point already exists; the risk is scope-incompleteness, not total absence. |
| TD005-CAP-009 | Critical | Every regression comparison depends on a valid reference; an unreproducible or ungoverned reference invalidates every downstream result even if equivalence (CAP-003 through CAP-006) is otherwise resolved. |
| TD005-CAP-011 | High | Both false-positive and false-negative failure modes are realistic and would each independently invalidate a regression result. |
| TD005-CAP-012 | Critical | This is TD-005's own central deliverable capability; every other gap in this document ultimately matters because it blocks this one. |
| TD005-CAP-013 | Medium | A reported regression missing provenance could be technically detected but practically unreproducible; a completeness gap, not a detection gap. |
| TD005-CAP-014 | Medium | Primarily a governance-hygiene risk; does not directly cause a missed regression, but impairs the ability to later prove one was or was not missed. |
| TD005-CAP-015 | High | AC-011's own uncovered end-to-end traceability property is a concrete, evidenced gap that could regress undetected. |
| TD005-CAP-016 | High | A genuine regression confined to one of four specifically-identified modules could occur without any Functional Requirement designed to detect it. |
| TD005-CAP-017 | Low | The condition this would protect against is not currently true and would itself require a separate, governed activation event first. |
| TD005-CAP-020 | Medium | A scientifically valid but practically unusable capability at one or more validation stages undermines operational purpose without invalidating any single result. |
| TD005-CAP-022 | Medium | Narrow exposure (one module, two libraries) but a realistic, hard-to-diagnose failure mode (library upgrade misclassified as behavioural regression). |

## 13. Capability Completeness

The capability inventory was checked against every FRA Functional Requirement, Constraint, and Deferred Obligation, and every SDA Dependency, for coverage (Section 14); none is uncovered. An explicit hidden-assumption search was then performed, examining: (a) whether the FRA/SDA assume a specific comparison cardinality (pairwise before/after) - no explicit assumption of this kind was found beyond what CAP-009's own provenance-selection question already covers, so no additional capability was added for this; (b) whether execution-environment identity is fully covered by TD005-CON-004 - found genuinely incomplete (Section 5, Item 9), leading to the addition of TD005-CAP-022; (c) whether cross-platform (operating system) reproducibility is assumed - no repository evidence (all governance and evidence to date originates from a single working environment; no claim of cross-platform execution appears anywhere in the FRA, SDA, Architecture Baseline, or Implementation Baseline) supports treating this as a currently-scoped TD-005 concern, so no capability was added for it; this is recorded here as an examined-and-rejected candidate, not silently skipped. TD005-CAP-022 is the one hidden assumption this search surfaced with sufficient evidence to justify a new capability gap; it is added as such, with its own ID, maturity, and risk rating, consistent with this section's own instruction.

### Hidden Capability Assumption Audit (V1.1)

This review repeated the hidden-assumption search against eleven specifically named candidates, each independently checked against repository evidence (fresh scans of all fourteen active modules performed for this review found zero environment-variable reads and zero threading/multiprocessing/asyncio imports anywhere in the active module set):

| Candidate | Classification | Basis |
|---|---|---|
| Python interpreter version | Already covered by TD005-CAP-022 | Same scientific category as the existing numpy/pandas finding (execution-environment version identity across time); TD005-CAP-022's own Purpose field is broadened (V1.1) to state this explicitly. |
| Numeric backend / BLAS implementation | Already covered by TD005-CAP-022 | A numpy/pandas dependency's own BLAS backend can change floating-point results independent of the library's own version number; the same scientific concern TD005-CAP-022 already names. |
| Dependency transitivity | Already covered by TD005-CAP-022 | Transitive C-extension dependencies of numpy/pandas (including BLAS) are the mechanism by which the BLAS finding above would manifest; not an independent capability. |
| Environment-variable influence | Already covered by TD005-CAP-011 | TD005-CAP-011's own scope (repeated-run output-order stability, TD005-DEP-018) already covers incidental Python-level non-determinism (for example, hash-seed-driven set-iteration order); zero active module reads an environment variable directly, confirmed by fresh scan. |
| Input-data schema version | Already covered by TD005-CAP-009 and TD005-CAP-011 | TD005-CAP-011's own controlled-condition set already names "input tick sequence" as a condition to hold equal; TD005-CAP-009's own reference-provenance capability governs the reproducibility of that input alongside the reference itself. |
| Serialization stability | Scientifically relevant but appropriately deferred | Any future reference-baseline representation (TD005-CAP-009's own eventual Specification-stage mechanism) may involve serialization; this is a representation-mechanism question this CGA correctly declines to resolve (Section 4, Section 11), not an unaddressed capability. |
| Baseline-generation code version | Scientifically relevant but appropriately deferred | The version of whatever future tool generates or captures a reference baseline is part of TD005-CAP-009's own reproducibility requirement (Section 7, Missing elements); it does not require a capability separate from CAP-009. |
| Operating-system / platform identity | Unsupported by repository evidence, outside current scope | No governance document, FRA requirement, or SDA dependency claims or requires cross-platform execution; all repository evidence to date originates from a single working environment. Examined and rejected, not silently skipped. |
| Locale and timezone | Unsupported by repository evidence, outside current scope | No active module performs locale-dependent formatting or timezone-sensitive parsing; no FRA requirement or SDA dependency names this concern. Examined and rejected. |
| Process count / concurrency | Unsupported by repository evidence, outside current scope | Fresh scan (this review) confirms zero `threading`, `multiprocessing`, or `asyncio` import anywhere in the fourteen active modules; the Run Engine's own single-threaded, sequential `RunLoop.step()` execution model (independently re-confirmed throughout the FRA, SDA, and this CGA) makes this concern currently moot. Examined and rejected. |
| Configuration version | Unsupported by repository evidence, outside current scope | `run_engine/core/config.py` is one of the four RETAIN-Deferred-Scope files (TD005-CAP-017), currently inactive and unreached; configuration versioning is not a live concern for the active runtime, and any future reactivation would itself require a separate governance review (ADR-012, RC-AD-005) before this concern could become relevant. Examined and rejected. |

No candidate in this table met both conditions required for a new capability (repository evidence, and a clear connection to an accepted FRA requirement, constraint, SDA dependency, or necessary hidden precondition) that TD005-CAP-022 does not already satisfy or that an existing capability does not already cover. The capability count therefore remains twenty-two; no new capability is added by this review.

## 14. Traceability

### 14.1 FRA Functional Requirement to Capability Traceability

| FRA Functional Requirement | Governing Capabilities |
|---|---|
| TD005-FR-001 | TD005-CAP-001, TD005-CAP-004, TD005-CAP-016 |
| TD005-FR-002 | TD005-CAP-006, TD005-CAP-010, TD005-CAP-011 |
| TD005-FR-003 | TD005-CAP-004, TD005-CAP-007 |
| TD005-FR-004 | TD005-CAP-007, TD005-CAP-008 |
| TD005-FR-005 | TD005-CAP-006, TD005-CAP-007, TD005-CAP-008 |
| TD005-FR-006 | TD005-CAP-004, TD005-CAP-007, TD005-CAP-008, TD005-CAP-015 |
| TD005-FR-007 | TD005-CAP-004, TD005-CAP-005, TD005-CAP-016 |
| TD005-FR-008 | TD005-CAP-004, TD005-CAP-005, TD005-CAP-016 |
| TD005-FR-009 | TD005-CAP-004, TD005-CAP-005, TD005-CAP-016 |
| TD005-FR-010 | TD005-CAP-004, TD005-CAP-005, TD005-CAP-016 |
| TD005-FR-011 | TD005-CAP-005 |
| TD005-FR-012 | TD005-CAP-005 |
| TD005-FR-013 | TD005-CAP-005, TD005-CAP-007, TD005-CAP-010, TD005-CAP-015 |
| TD005-FR-014 | TD005-CAP-001, TD005-CAP-005, TD005-CAP-007, TD005-CAP-015 |
| TD005-FR-015 | TD005-CAP-005, TD005-CAP-007 |
| TD005-FR-016 | TD005-CAP-005 |
| TD005-FR-017 | TD005-CAP-004, TD005-CAP-005 |
| TD005-FR-018 | TD005-CAP-002, TD005-CAP-009, TD005-CAP-011, TD005-CAP-012 |
| TD005-FR-019 | TD005-CAP-013, TD005-CAP-014, TD005-CAP-020 |
| TD005-FR-020 | TD005-CAP-003, TD005-CAP-012 |
| TD005-FR-021 | TD005-CAP-002, TD005-CAP-009, TD005-CAP-012 |
| TD005-FR-022 | TD005-CAP-004, TD005-CAP-014, TD005-CAP-020 |

All twenty-two Functional Requirements individually trace to at least one capability.

### 14.2 FRA Constraint to Capability Traceability

| FRA Constraint | Governing Capabilities |
|---|---|
| TD005-CON-001 | TD005-CAP-008 |
| TD005-CON-002 | TD005-CAP-008, TD005-CAP-017 |
| TD005-CON-003 | TD005-CAP-014, TD005-CAP-017 |
| TD005-CON-004 | TD005-CAP-010, TD005-CAP-011, TD005-CAP-022 |

All four Constraints individually trace to at least one capability.

### 14.3 FRA Deferred Obligation to Capability Traceability

| FRA Deferred Obligation | Governing Capabilities |
|---|---|
| Section 13.1, Active Module Coverage Obligation | TD005-CAP-015, TD005-CAP-016, TD005-CAP-017 |
| Section 13.2, Repository-Integrity Regression Obligation | TD005-CAP-018 |

Both Deferred Obligations individually trace to at least one capability.

### 14.4 SDA Dependency to Capability Traceability

| SDA Dependency | Governing Capability |
|---|---|
| TD005-DEP-001 | TD005-CAP-001 |
| TD005-DEP-002 | TD005-CAP-002 |
| TD005-DEP-003 | TD005-CAP-001 |
| TD005-DEP-004 | TD005-CAP-003 |
| TD005-DEP-005 | TD005-CAP-004 |
| TD005-DEP-006 | TD005-CAP-005 |
| TD005-DEP-007 | TD005-CAP-007 |
| TD005-DEP-008 | TD005-CAP-008 |
| TD005-DEP-009 | TD005-CAP-011 |
| TD005-DEP-010 | TD005-CAP-010 |
| TD005-DEP-011 | TD005-CAP-006 |
| TD005-DEP-012 | TD005-CAP-009 |
| TD005-DEP-013 | TD005-CAP-009 |
| TD005-DEP-014 | TD005-CAP-009 |
| TD005-DEP-015 | TD005-CAP-004 |
| TD005-DEP-016 | TD005-CAP-005 |
| TD005-DEP-017 | TD005-CAP-004 |
| TD005-DEP-018 | TD005-CAP-011 |
| TD005-DEP-019 | TD005-CAP-008 |
| TD005-DEP-020 | TD005-CAP-015 |
| TD005-DEP-021 | TD005-CAP-016 |
| TD005-DEP-022 | TD005-CAP-016 |
| TD005-DEP-023 | TD005-CAP-013 |
| TD005-DEP-024 | TD005-CAP-014 |
| TD005-DEP-025 | TD005-CAP-020 |
| TD005-DEP-026 | TD005-CAP-020 |
| TD005-DEP-027 | TD005-CAP-014, TD005-CAP-020 |
| TD005-DEP-028 | TD005-CAP-017 |
| TD005-DEP-029 | TD005-CAP-017 |
| TD005-DEP-030 | TD005-CAP-018 |
| TD005-DEP-031 | TD005-CAP-017 |
| TD005-DEP-032 | TD005-CAP-021 |
| TD005-DEP-033 | TD005-CAP-019 |

All thirty-three Scientific Dependencies individually trace to at least one capability; TD005-DEP-027 is the one dependency deliberately traced to two capabilities (Section 7, TD005-CAP-014 and TD005-CAP-020), since it genuinely bears on both evidence persistence in general and its specific cross-stage application, a distinction stated explicitly in both capability entries.

## 15. Open Question Resolution

**OQ-001** (invocation boundary). Governing capability: TD005-CAP-008. Disposition: not resolved by this CGA; TD005-CAP-008 is confirmed PARTIALLY AVAILABLE with a working, non-interfering observation point already confirmed sufficient for the fields it covers, but the complete boundary is not yet stated. Transferred to: Architecture (unchanged from the SDA's own disposition).

**OQ-002** (reference-baseline source). Governing capability: TD005-CAP-009. Disposition: not resolved by this CGA; TD005-CAP-009 is MISSING, requiring source selection, an immutability/governance rule, and a reproducibility mechanism. Transferred to: Architecture (unchanged from the SDA's own disposition).

**OQ-003** (RETAIN-Deferred-Scope coverage). Governing capability: TD005-CAP-017. Disposition: this CGA confirms, consistent with the SDA, that the "why currently excluded" portion is fully resolved (TD005-CAP-017 is PARTIALLY AVAILABLE precisely because this portion is sound) but the "how would scope-drift be detected" portion remains open. Transferred to: Architecture, Optional priority (Section 10) - Architecture may resolve or explicitly defer to Specification without blocking progress, since the condition this protects against is not currently true (Section 12, Low risk).

**OQ-004** (execution-time budget). Governing capability: TD005-CAP-020. Disposition: not resolved by this CGA; TD005-CAP-020 is MISSING, confirmed as a genuine, currently-unaddressed tension across all three named sub-questions (execution-time, application-model, continuity). Transferred to: Architecture, Mandatory priority (Section 10), unchanged classification from the SDA's own disposition.

**OQ-005** (test-code location). Governing capability: TD005-CAP-017 (via TD005-CON-003, Repository-Scope Compatibility). Disposition: not resolved by this CGA; this CGA confirms, as the SDA did, that this question requires no independent capability content beyond compatibility with the already-PARTIALLY-AVAILABLE scope-stability capability. Transferred to: Capability Gap Analysis has now addressed its own scope; the location choice itself remains transferred to Specification (unchanged from the SDA's own disposition).

**OQ-006** (scientific definition of regression equivalence). Governing capabilities: TD005-CAP-003, TD005-CAP-004, TD005-CAP-005, TD005-CAP-006. Disposition: not resolved by this CGA; this is the central capability gap this document identifies (TD005-CAP-003 rated Critical risk, Section 12), now organized into four distinct capability-level questions (formal definition; trajectory model; numeric/categorical policy; object-identity independence) rather than one undifferentiated Open Question. Transferred to: Architecture and Specification, per the FRA's own original disposition, now with capability-level structure available for that future work.

All six Open Question IDs are individually addressed above; none is silently discarded.

## 16. Architecture Inputs

- The Mandatory Architecture-readiness capability list (Section 10): TD005-CAP-001, TD005-CAP-002, TD005-CAP-003, TD005-CAP-004, TD005-CAP-005, TD005-CAP-006, TD005-CAP-007, TD005-CAP-008, TD005-CAP-009, TD005-CAP-011, TD005-CAP-012, TD005-CAP-015, TD005-CAP-016, TD005-CAP-020, each with its own Missing Elements (Section 7) and Gap Assessment (Section 9) as the concrete starting point.
- The Optional-priority capabilities (TD005-CAP-013, TD005-CAP-014, TD005-CAP-017's drift-sensitivity portion, TD005-CAP-022), which Architecture may resolve directly or explicitly defer to Specification, with the deferral itself recorded rather than silent.
- The four already-AVAILABLE or OUTSIDE-TD-005-SCOPE capabilities (TD005-CAP-010, TD005-CAP-018, TD005-CAP-019, TD005-CAP-021), which Architecture may rely on without further analysis.
- The capability dependency graph (Section 8), establishing the order in which Architecture's own decisions must be internally consistent (Foundational capabilities are presupposed; Intermediate capabilities inform Derived capabilities, not the reverse).
- The Risk Assessment (Section 12), identifying TD005-CAP-003, TD005-CAP-009, and TD005-CAP-012 as Critical-risk capabilities requiring Architecture's own most rigorous treatment.
- The five Open Questions transferred to Architecture (Section 15: OQ-001, OQ-002, OQ-003, OQ-004, OQ-006), each now attached to the specific capability it governs.
- The newly surfaced TD005-CAP-022 finding, requiring an explicit Architecture-level decision on whether to fold it into CAP-009/CAP-011 or defer it to Specification (Section 10).

## 17. Specification Inputs

- The complete Specification-deferred list (Section 11): the twelve named exact-mechanism decisions, each anchored to its own governing capability, to be resolved once Architecture has made the corresponding upstream decision.
- OQ-005 (test-code location), unchanged from the SDA's own disposition, transferred to Specification.
- TD005-CAP-014's persistence-and-continuity decision, if not resolved during Architecture (Optional priority, Section 10).
- TD005-CAP-013's four-element evidence-composition refinement, if not adopted during Architecture (Optional priority, Section 10).
- TD005-CAP-022's resolution, if deferred by Architecture (Section 10).

## 18. CGA Completion Criteria

This Capability Gap Analysis is complete and ready to serve as the accepted Working Baseline for Architecture when:

- Every capability is derived exclusively from the accepted FRA and SDA, with no capability originating from an implementation idea: verified by construction (Section 7, each capability's own Dependency sources and Traceability fields cite only FRA/SDA content, except TD005-CAP-022, whose own hidden-assumption origin is explicitly disclosed rather than concealed).
- Every capability carries all eleven required fields (ID, Name, Purpose, Scientific rationale, Current repository evidence, Dependency sources, Current maturity, Missing elements, Scientific risk, Required before, Traceability): verified by construction (Section 7).
- No unrelated capabilities are merged: verified by construction (twenty-two individually numbered capabilities, each addressing one coherent scientific concern; Class B alone is refined into five capabilities specifically because the FRA/SDA evidence did not support treating equivalence, trajectory, numeric policy, object-identity, and vocabulary as one undifferentiated concern).
- At least the ten named capability classes are analyzed, refined where evidence justified it: verified by construction (Section 7, Classes A through J each represented, several refined into two or more capabilities).
- Maturity is assigned conservatively, requiring authoritative definition, traceability, evidence, and governance compatibility, not code existence alone: verified by construction (for example, TD005-CAP-007's twelve CanonicalState fields are code-confirmed but rated only PARTIALLY AVAILABLE, since classification, not mere enumeration, is required).
- The capability dependency graph is acyclic and independently derived: verified (Section 8, explicit cycle check stated; independently derived, not copied from the SDA's dependency graph).
- Architecture and Specification readiness are separated into Mandatory, Optional, and Deferred: verified (Section 10, Section 11).
- Risk is classified and justified for every non-AVAILABLE capability: verified (Section 12, eighteen capabilities individually classified).
- Capability completeness was assessed and hidden assumptions were explicitly searched for, with findings added rather than discarded: verified (Section 13, TD005-CAP-022 added as a result).
- Every FRA Functional Requirement, Constraint, and Deferred Obligation, and every SDA Dependency, traces to at least one capability, with no gap: verified (Section 14, four traceability tables, zero gaps).
- Every SDA Open Question is either resolved or explicitly transferred, with none silently discarded: verified (Section 15, all six individually addressed).
- Architecture Inputs and Specification Inputs are each a concise list directly originating from capability gaps, not new content: verified (Section 16, Section 17).
- No architecture, framework, pytest, fixture, CI/CD, comparison-algorithm, storage-format, reporting-format, or implementation decision is made anywhere in this document: verified by construction (Section 7 through Section 17 contain no such decision; Section 9's own "without prescribing implementation" instruction is honored throughout).

All criteria above are satisfied by this document.

## 19. Conclusion

This Capability Gap Analysis answers, from the accepted TD-005 FRA and SDA alone, which scientific capabilities required for an automated regression capability already exist, which exist only partially, which are completely missing, and which must be resolved before Architecture versus Specification. Twenty-two individually numbered capabilities are identified across ten capability classes: three are AVAILABLE (Environmental Determinism, Governance Sequencing, Behavioural Vocabulary Stability), seven are PARTIALLY AVAILABLE, eleven are MISSING, and one (Executor Namespace Integrity) is correctly classified OUTSIDE TD-005 SCOPE as a general behavioral capability while independently AVAILABLE as a repository-integrity fact already certified by a different governance unit. Fourteen capabilities are Mandatory before Architecture may proceed; four are Optional; four are already resolved and require no further Architecture action. The central scientific gap this document identifies is the composite Regression Classification Capability (TD005-CAP-012, Critical risk, confirmed scientifically atomic by this review's own explicit atomicity check, Section 7), which cannot exist until its own prerequisites - the Certified-Contract Corpus Authority (TD005-CAP-001, renamed and justified by this review as a persistent scientific capability rather than a one-time governance activity), the Certification-Status Boundary (TD005-CAP-002), and above all the Formal Behavioural Equivalence Definition (TD005-CAP-003, also Critical risk) and Reference-Baseline Provenance (TD005-CAP-009, also Critical risk) - are themselves resolved. A capability completeness review, including an explicit hidden-assumption search, surfaced one new capability gap not present in the FRA or SDA: TD005-CAP-022 (Execution-Environment Dependency-Version Stability), evidenced directly by fresh repository inspection (`run_engine/core/regime.py`'s own `numpy`/`pandas` dependency and `requirements.txt`'s own exact-version pinning practice) rather than assumed, and now given explicit relationships to TD005-CAP-009 and TD005-CAP-011 (Section 7). All six SDA Open Questions are individually addressed: none resolved prematurely, none silently discarded. This document selects no architecture, framework, pytest, fixture, CI/CD design, comparison algorithm, storage format, reporting format, or implementation of any kind. This targeted V1.1 Editorial and Scientific Review confirmed the capability count (twenty-two), maturity distribution, risk distribution, and dependency graph unchanged, added the capability-layer classification rationale named above (Section 8), and performed a full atomicity audit and a repeated hidden-assumption search (Section 7.1, Section 13) that justified no split, merge, or new capability beyond the four targeted clarifications. The document remains ready to serve as the accepted Working Baseline for a future TD-005 Architecture.
