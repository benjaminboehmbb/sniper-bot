Document Class:
Implementation Specification

Document ID:
TD005-IMP

Title:
TD-005 Automated Regression Test Suite - Implementation Design / Implementation Specification

Version:
V1.1

Date:
2026-07-14

Status:
DRAFT - EDITORIAL AND SCIENTIFIC REVIEW COMPLETED

Storage Location:
docs/architecture/implementation/

Filename:
TD_005_AUTOMATED_REGRESSION_TEST_SUITE_IMPLEMENTATION_SPECIFICATION_V1_2026-07-14.md

Technical Debt Item:
TD-005 - Automated Regression Test Suite (docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md)

Accepted Working Baselines:
docs/architecture/analysis/TD_005_AUTOMATED_REGRESSION_TEST_SUITE_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-14.md, Version V1.1, Status DRAFT - EDITORIAL AND SCIENTIFIC REVIEW COMPLETED
docs/architecture/analysis/TD_005_AUTOMATED_REGRESSION_TEST_SUITE_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-14.md, Version V1.1, Status DRAFT - CORRECTIVE SCIENTIFIC REVIEW COMPLETED
docs/architecture/analysis/TD_005_AUTOMATED_REGRESSION_TEST_SUITE_CAPABILITY_GAP_ANALYSIS_V1_2026-07-14.md, Version V1.1, Status DRAFT - EDITORIAL AND SCIENTIFIC REVIEW COMPLETED
docs/architecture/design/TD_005_AUTOMATED_REGRESSION_TEST_SUITE_ARCHITECTURE_V1_2026-07-14.md, Version V1.1, Status DRAFT - EDITORIAL AND SCIENTIFIC REVIEW COMPLETED
docs/architecture/specifications/TD_005_AUTOMATED_REGRESSION_TEST_SUITE_SPECIFICATION_V1_2026-07-14.md, Version V1.1, Status DRAFT - EDITORIAL AND SCIENTIFIC REVIEW COMPLETED (Final QA Certification Review complete, one minor correction applied, Version retained at V1.1)

Scope:
Implementation design only. Defines how the accepted Specification will be realized while remaining independent of concrete Python code. No source files, pytest code, CI/CD configuration, or GitHub workflows are created by this document.

Dependencies:
- docs/architecture/analysis/TD_005_AUTOMATED_REGRESSION_TEST_SUITE_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-14.md
- docs/architecture/analysis/TD_005_AUTOMATED_REGRESSION_TEST_SUITE_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-14.md
- docs/architecture/analysis/TD_005_AUTOMATED_REGRESSION_TEST_SUITE_CAPABILITY_GAP_ANALYSIS_V1_2026-07-14.md
- docs/architecture/design/TD_005_AUTOMATED_REGRESSION_TEST_SUITE_ARCHITECTURE_V1_2026-07-14.md
- docs/architecture/specifications/TD_005_AUTOMATED_REGRESSION_TEST_SUITE_SPECIFICATION_V1_2026-07-14.md
- docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md
- docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md
- docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md
- docs/architecture/REPOSITORY_CONSOLIDATION_ARCHITECTURE_V1_2026-07-14.md
- docs/architecture/REPOSITORY_CONSOLIDATION_SPECIFICATION_V1_2026-07-14.md
- docs/architecture/certification/REPOSITORY_CONSOLIDATION_FINAL_CERTIFICATION_V1_2026-07-14.md
- requirements.txt

Referenced By:
- future TD-005 Implementation (not yet created)
- future TD-005 Final Certification (not yet created)

Supersedes:
None. This is the first Implementation Specification for TD-005.

Language:
English

Encoding:
ASCII

---

# TD-005 Automated Regression Test Suite - Implementation Design / Implementation Specification

## 1. Metadata

See front matter above.

## 2. Executive Summary

### 2.1 Revision History

- **V1.0 (2026-07-14).** Initial Implementation Specification. Twenty-three Implementation Units, eighteen Implementation Invariants, fifteen Implementation Decisions, across twelve implementation domains.
- **V1.1 (2026-07-14).** Editorial and Scientific Review. Independently re-verified repository evidence (branch, HEAD, active module set, all five accepted Working Baselines) fresh against the same evidence gathered at V1.0. Corrected a range-citation defect, found in two locations (TD005-IU-005's own Dependencies field, Section 7, and its own Prerequisite cell, Section 16): "TD005-IU-006 through TD005-IU-021" incorrectly included TD005-IU-019, TD005-IU-020, and TD005-IU-021, none of which the Orchestration Unit's own Required Interactions field (Section 7) actually sequences; as literally written, this also created a genuine circular dependency with TD005-IU-019 (which itself explicitly depends on and invokes TD005-IU-005), since TD005-IU-019 was both a claimed dependency of, and a claimed dependent on, TD005-IU-005. Corrected to the accurate, individually-listed set (TD005-IU-006 through TD005-IU-018) in both locations; added a clarifying passage to Section 9's own "Sequencing" paragraph distinguishing TD005-IU-005's internal pipeline-sequencing role from TD005-IU-019's legitimate external, once-per-validation-stage invocation of the whole pipeline, resolving the apparent self-contradiction without altering either unit's own Purpose or Responsibility. Widened Section 8's own "Cleanup" bullet, which incompletely claimed only the Reference Baseline and persisted Evidence survive across invocations; corrected to name all seven Authority/Registry-pattern units (Certified Contract Corpus, Certification Boundary, Reference Baseline, Behavioural Vocabulary, persisted Evidence, both Coverage units, and the Scope Boundary) that are not governed by the per-invocation session model. Widened Section 10's own "Abort conditions" list to include a Comparison-domain unit's own failure to reach a valid result, reconciling it with Section 8's own broader general failure rule and making the list genuinely exhaustive rather than illustrative. Resolved a genuine duplication between TD005-II-004 and TD005-II-011 (both stated the identical direct-read prohibition in inverted phrasing despite a parenthetical claiming they were distinct); re-scoped TD005-II-011 to a genuinely distinct channel-exclusivity rule (every consuming unit must use TD005-IU-009's own exposed snapshot, never an unofficial relayed copy), preserving both invariant numbers without renumbering. Added an explicit, evidence-grounded exclusion of concurrent Orchestration Unit invocation from this document's own scope, inheriting rather than re-deriving the CGA's own already-recorded examined-and-rejected concurrency finding. Added an atomicity requirement for the evidence-persistence operation (TD005-IU-016, TD005-ID-012): a partially-written record SHALL remain Unpersisted, never Persisted-and-Altered, closing a gap in which an interrupted persist operation had no defined outcome; correspondingly clarified that a restart after partial completion (Section 8) always re-runs the complete sequence, never resumes from an intermediate point. A full sixteen-item hidden-implementation-assumption review found the remaining fourteen items already adequately specified, correctly deferred to actual Implementation, or (for shutdown ordering) correctly out of scope, consistent with this governance chain's own prior findings at the Architecture and Specification stages. No Implementation Unit, Invariant, or Decision was added, removed, split, or merged; the twenty-three Implementation Unit, eighteen Implementation Invariant, and fifteen Implementation Decision counts are unchanged. No Architecture Component, Specification Object, Specification Invariant, or Specification Decision was reinterpreted. This document remains free of Python code, pytest/unittest selection, APIs, algorithms, serialization formats, storage implementation, CI/CD content, or concrete source code. **Final QA Certification Review (same V1.1, no V1.2 created).** An independent, mechanical re-verification (fresh AST-based import closure, fresh `git status --short`, fresh re-read of the FRA/SDA/CGA/Architecture/Specification, an independently reconstructed prerequisite/dependency graph checked programmatically for cycles) found zero circular dependencies and the document's own scientific and design content fully intact, plus two further minor, self-contained internal-consistency defects: Section 9's own "Call order" paragraph claimed only one documented same-layer-or-lower exception (TD005-IU-003) when TD005-IU-018's own already-justified cross-layer dependency on TD005-IU-022 (Section 7) constituted a second, unacknowledged one; corrected to name both. Section 16's own Prerequisite cell for TD005-IU-005 omitted the three precondition units (TD005-IU-001, TD005-IU-003, TD005-IU-022) that Section 7's own Dependencies field, corrected in the prior review, explicitly requires before sequencing begins; corrected to include them. Neither correction changed any IU/II/ID count, readiness classification, or traceability mapping.

This Implementation Specification is the final engineering design for TD-005 before source code is written. It defines twenty-three individually numbered Implementation Units (TD005-IU-001 through TD005-IU-023) - twenty-two realizing the twenty-two accepted Specification Objects one-to-one, plus one new, aggregate-traceability unit (TD005-IU-005, Regression Pipeline Orchestration Unit) added because the accepted Architecture's own Component Interaction section explicitly describes call-order sequencing as a cross-component logical-interface concern owned by no single component, and an implementation cannot proceed without some unit taking responsibility for actually invoking realization units in order - the same evidence-driven extension pattern this governance chain has used at every prior stage (TD005-AD-007, TD005-ARC-022; TD005-SD-002). Eighteen Implementation Invariants (TD005-II-001 through TD005-II-018) and fifteen Implementation Decisions (TD005-ID-001 through TD005-ID-015) are derived, each individually traceable to the accepted FRA, SDA, CGA, Architecture, or Specification. Fifteen of the accepted Specification's own twenty-two open mechanism deferrals (Section 18 of the Specification) are resolved at the design level by this document's own Implementation Decisions; the remainder (principally concrete numeric constants and execution-time budgets) are explicitly, individually named as still deferred to actual Implementation or empirical calibration, never silently invented. No Python code, pytest code, CI/CD configuration, GitHub workflow, API signature, or concrete algorithm implementation is created anywhere in this document.

## 3. Accepted Inputs

Read in full and treated as binding, unmodified inputs:

- **FRA V1.1**: twenty-two Functional Requirements, four Constraints, two Deferred Specification and Coverage Obligations, six Open Questions.
- **SDA V1.1**: thirty-three Scientific Dependencies.
- **CGA V1.1**: twenty-two Capabilities across ten capability classes.
- **Architecture V1.1**: twenty-two Architecture Components (TD005-ARC-001 through TD005-ARC-022) across ten architectural layers, nineteen Architecture Invariants (TD005-AI-001 through TD005-AI-019), thirteen Architecture Decisions (TD005-AD-001 through TD005-AD-013).
- **Specification V1.1**: twenty-two Specification Objects (TD005-SO-001 through TD005-SO-022) across twelve specification domains, twenty-two Specification Invariants (TD005-SI-001 through TD005-SI-022), four Specification Decisions (TD005-SD-001 through TD005-SD-004), a 22-to-22 Architecture Component coverage mapping (no orphan), and a thirteen-item Implementation Readiness registry (Section 18 of the Specification) naming every mechanism-level choice this document is now responsible for closing or explicitly re-deferring.

No FRA requirement, SDA dependency, CGA capability, Architecture component/invariant/decision, or Specification object/invariant/decision is altered, reinterpreted, merged, removed, or added by this document. This Implementation Specification realizes the accepted Specification's own objects as concrete engineering units; it does not re-derive the Specification itself.

## 4. Objective

To define how the accepted TD-005 Specification will be implemented, while remaining independent of concrete Python code. This document is the final engineering design before implementation: every Implementation Unit, invariant, and decision in this document is either directly buildable design content or an explicitly named, further-deferred choice. It creates no source files, pytest code, CI/CD configuration, or GitHub workflows, and it specifies no API signature or concrete algorithm implementation.

## 5. Repository Evidence

Independently re-verified immediately before drafting this document, not assumed from the FRA, SDA, CGA, Architecture, Specification, or any prior analysis:

1. **Branch and HEAD.** Branch `run-engine-consolidation-safety`; HEAD `8952b1cba42506e4126e57ee89c59934f3d48b71`. `git status --short` shows exactly six entries: the pre-existing, unrelated modification to `docs/capabilities/SGF_013_SCIENTIFIC_BEHAVIOUR_REPRESENTATION_2026-06-26.md`, and five untracked entries - the accepted FRA, SDA, CGA, Architecture (`docs/architecture/design/`), and Specification working baselines. No other local change exists.
2. **Active Run Engine module set.** A freshly, independently authored AST-based import closure from `run_engine.main`, this time explicitly resolving relative imports (`from .executor import Executor` inside `run_engine/core/execution/__init__.py`) in addition to absolute imports, reproduces exactly: 18 total `.py` files under `run_engine/`, 14 active (`run_engine/main.py`, `run_engine/core/loop.py`, `run_engine/core/state.py`, `run_engine/core/regime.py`, `run_engine/core/strategy.py`, `run_engine/core/position.py`, `run_engine/core/risk.py`, `run_engine/core/execution/__init__.py`, `run_engine/core/execution/executor.py`, `run_engine/core/performance.py`, `run_engine/core/pnl.py`, `run_engine/core/trade_lifecycle.py`, `run_engine/core/canonical_state.py`, `run_engine/core/canonical_enforcer.py`), 4 inactive RETAIN-Deferred-Scope (`run_engine/core/config.py`, `run_engine/runtime/recovery.py`, `run_engine/runtime/snapshot.py`, `run_engine/runtime/state_memory.py`). Identical to every prior independent derivation across the FRA, SDA, CGA, Architecture, Specification, and Repository Consolidation governance chain.
3. **`docs/architecture/implementation/`.** Confirmed as a brand-new directory, not a pre-existing repository convention (unlike `docs/architecture/specifications/`, which already held prior Specification documents, and consistent with the Architecture's own precedent of introducing `docs/architecture/design/` when the governing task explicitly names a new path). This is a deliberate departure directed by the governing task's own explicit path instruction, not an unexplained one.
4. **`requirements.txt`, `tests/`, `tools/`.** Re-confirmed unchanged: `certifi==2025.10.5`, `charset-normalizer==3.4.3`, `idna==3.10`, `numpy==2.3.3`, `pandas==2.3.3`, `python-dateutil==2.9.0.post0`, `pytz==2025.2`, `PyYAML==6.0.3`, `requests==2.32.5`, `six==1.17.0`, `tzdata==2025.2`, `urllib3==2.5.0`; no test framework present; zero files under `tests/` (only the empty, untracked `tests/ssi/` structure, unrelated to `run_engine`); `tools/repository_consolidation/verify_repository_consolidation.py` remains structure-only.
5. **Architecture Baseline, Implementation Baseline, Technical Debt Register, Repository Consolidation documents.** Each re-opened; the specific facts this Implementation Specification's own units rely on (ADR-009's Lifecycle Transition Table and Scientific Definitions, ADR-010's twelve-stage Stage Ordering, ADR-011's Runtime Failure Handling, the Implementation Baseline's own six-stage Long-Duration-Validation sequence, Repository Consolidation's own Normative Repository Boundary and RC-AD-004 Executor-namespace resolution, TD-004/005/007 Register status) are re-confirmed present and unchanged from the Specification's own citations.

No Specification statement is carried over unverified; every fact this Implementation Specification's own units, invariants, and decisions rely on was independently re-confirmed above or is explicitly cited to its own accepted-baseline source.

## 6. Design Principles

- **Traceability-first.** No Implementation Unit, Invariant, or Decision exists without derivation from one or more accepted Specification Objects, Specification Decisions, Specification Invariants, Architecture Components, or an explicitly justified aggregate concern (Section 15). This is itself formalized as TD005-II-001.
- **One primary responsibility per unit.** Every Implementation Unit realizes exactly one Specification Object, except the single, explicitly justified aggregate Orchestration Unit (TD005-IU-005); no Specification Object is realized by more than one Implementation Unit, and no Implementation Unit realizes behaviour beyond its own owning Specification Object's Required/Forbidden behaviour (TD005-II-002).
- **Design, not code.** Every Implementation Unit states purpose, responsibility, and interaction structure - never a function signature, class definition, import statement, or executable algorithm. Where the Specification left a mechanism open, this document either resolves it at the design level (naming the concept, not the code) or explicitly re-defers it, never both silently.
- **No premature calibration.** A concrete numeric constant (a tolerance epsilon, an execution-time budget in seconds) is not chosen here where doing so would require empirical data this design stage does not possess; the POLICY SHAPE is designed, and the literal constant, along with every persistence mechanism and storage format, is named as an explicit, still-open Implementation-stage item, never selected by this document (TD005-AI-017).
- **Layered build order.** Every Implementation Unit's own Implementation Readiness (Section 16) is assessed against the Architecture's own ten-layer structure: a unit realizing a higher-layer component requires every unit realizing a lower-layer component it depends on to exist first.
- **No implicit exclusion.** Every exclusion the Specification already established (no severity/waiver/priority/disposition; no absorption of Repository Consolidation's own Executor-namespace protection; no alternative Run Engine execution path) is restated at the Implementation Unit level, not merely by reference.

## 7. Implementation Units

Twenty-three individually numbered Implementation Units across twelve domains (the eleven the governing task names, A through K, plus a twelfth, L, mirroring the Specification's own precedent, TD005-SD-002, for the same two Repository Boundary Protection objects). Each Implementation Unit states: Purpose, Responsibility, Inputs, Outputs, Dependencies, Internal state, Required interactions, Forbidden interactions, Lifecycle, Failure behaviour, Traceability.

### Domain A - Component Realization

**TD005-IU-001. Certified Contract Corpus Realization Unit.**
Purpose: realize TD005-SO-001's own enumeration, membership-determination, and drift-detection behaviour as a buildable design unit.
Responsibility: maintain the single, authoritative, re-derivable enumeration of the certified-contract corpus.
Inputs: the Architecture Baseline, the Implementation Baseline, the six certified units' own Final Certifications, the Technical Debt Register (per TD005-ID-002's own Governance Citation Manifest concept).
Outputs: the corpus enumeration; a membership/exclusion determination for any candidate; a drift signal.
Dependencies: none (foundational; Architecture Layer 1).
Internal state: the current enumeration and its own last-verified provenance marker.
Required interactions: exposes its enumeration to TD005-IU-002, TD005-IU-003, TD005-IU-017, TD005-IU-018, TD005-IU-021.
Forbidden interactions: does not read active Run Engine runtime state; does not perform classification.
Lifecycle: Uninitialized -> Enumerated -> Drift-Detected -> Re-Enumerated (TD005-SO-001's own state model, unmodified).
Failure behaviour: an enumeration that cannot re-derive from primary evidence SHALL report a drift/ambiguity signal rather than silently returning a partial set (TD005-SI-002).
Traceability: TD005-SO-001; TD005-ARC-001; TD005-ID-002.

**TD005-IU-002. Certification Boundary Realization Unit.**
Purpose: realize TD005-SO-002's own certification-status determination behaviour.
Responsibility: apply one recorded boundary-rule version to determine certified/not-certified status for any candidate.
Inputs: a candidate contract or behavioural claim; TD005-IU-001's own corpus enumeration.
Outputs: a certification-status determination; the boundary-rule version that produced it.
Dependencies: TD005-IU-001 (Architecture Layer 1).
Internal state: the current boundary-rule version; the determination history.
Required interactions: consumed by TD005-IU-003, TD005-IU-014, TD005-IU-015.
Forbidden interactions: does not itself classify a deviation as regression or non-regression outside its own recorded boundary (that is exclusively TD005-IU-014's own role, TD005-AI-008).
Lifecycle: Undefined -> Defined -> Revised (TD005-SO-002's own state model, unmodified).
Failure behaviour: a candidate yielding no determinate answer under the current rule definition is a defect in the rule itself, reported as such, never silently resolved either way.
Traceability: TD005-SO-002; TD005-ARC-002; TD005-ID-003.

**TD005-IU-003. Reference Baseline Realization Unit.**
Purpose: realize TD005-SO-003's own establishment, governance, and reproducibility behaviour for the authoritative reference-baseline record.
Responsibility: establish and govern exactly one authoritative reference-baseline record per governance epoch.
Inputs: TD005-IU-001's enumeration; TD005-IU-002's boundary determination; one bootstrap capture from TD005-IU-006; one identity record from TD005-IU-007.
Outputs: the authoritative reference-baseline record, including complete provenance metadata.
Dependencies: TD005-IU-001, TD005-IU-002 (Architecture Layer 1); TD005-IU-006, TD005-IU-007 (Architecture Layer 3, one-time bootstrap only, TD005-AI-018), the specific execution intended as the reference having reached the Captured state before this unit accepts it (TD005-SI-004).
Internal state: the current reference-baseline record and its own governance-revision history, distinct from and never merged with TD005-IU-006's own ordinary candidate-capture history (TD005-AD-002).
Required interactions: the sole authoritative reference every comparison consumes (TD005-IU-011, TD005-IU-012, TD005-IU-013).
Forbidden interactions: does not mutate the established record in place (TD005-AI-003); does not accept a Failed bootstrap capture.
Lifecycle: Unestablished -> Capturing -> Established -> Revising -> Established (TD005-SO-003's own state model, unmodified, including the single-state clarification from the Specification's own V1.1 review).
Failure behaviour: a bootstrap capture reaching Failed is rejected outright; no partial or provenance-incomplete record is ever treated as Established.
Traceability: TD005-SO-003; TD005-ARC-003; TD005-AD-002; TD005-AI-003, TD005-AI-018; TD005-ID-004.

**TD005-IU-004. Behavioural Vocabulary Realization Unit.**
Purpose: realize TD005-SO-009's own stability requirement for the terminology every other Implementation Unit's own design is stated in.
Responsibility: expose the authoritative vocabulary (Position, Side, Scale-In, Partial Close, Full Close, Tick-Complete, Canonical Working State, Authoritative Owner, Computational Authority, Runtime Failure Event) as a stable, versioned reference.
Inputs: the Architecture Baseline's own Ownership Terminology section; ADR-009's own Scientific Definitions.
Outputs: the authoritative term set, consumed by every other Implementation Unit's own design language.
Dependencies: none (foundational; Architecture Layer 1).
Internal state: the current vocabulary and its own revision history.
Required interactions: referenced by every Implementation Unit in this document.
Forbidden interactions: no Implementation Unit introduces a new term without adding it here first.
Lifecycle: Established -> Revised (TD005-SO-009's own state model, unmodified).
Failure behaviour: a term used with more than one active meaning anywhere in this document's own design language is a defect in this document, not a valid outcome.
Traceability: TD005-SO-009; TD005-ARC-010; TD005-AI-001.

### Domain B - Runtime Orchestration

**TD005-IU-005. Regression Pipeline Orchestration Unit.**
Purpose: invoke every realization unit in the certified sequence this Architecture's own Component Interaction section (Section 11) and this Specification's own Section 9 State Models jointly establish, without owning any realization unit's own internal behaviour.
Responsibility: drive one complete regression-check invocation from Replay through Classification, Evidence, and Coverage, in the correct order, for a single candidate execution.
Inputs: a controlled-condition specification (handed to TD005-IU-006); the established reference (TD005-IU-003).
Outputs: one reached classification outcome (TD005-IU-014), with any required evidence record composed (TD005-IU-015) and persisted (TD005-IU-016).
Dependencies: every realization unit it actually sequences, individually - TD005-IU-006, TD005-IU-007, TD005-IU-008, TD005-IU-009, TD005-IU-010, TD005-IU-011, TD005-IU-012, TD005-IU-013, TD005-IU-014, TD005-IU-015, TD005-IU-016, TD005-IU-017, TD005-IU-018 - plus the three preconditions confirmed before sequencing begins (TD005-IU-001, TD005-IU-003, TD005-IU-022, Section 8, Initialization). This unit does NOT depend on, and is never sequenced by, TD005-IU-019, TD005-IU-020, or TD005-IU-021; TD005-IU-019 instead invokes this unit from outside the internal pipeline (Section 9), and TD005-IU-021 aggregates this unit's own remaining open items as a document-completeness concern, not a runtime dependency. Itself depends on nothing lower, but cannot complete until each of the thirteen sequenced units is available.
Internal state: the current pipeline stage; no owned domain data (it owns sequencing only, never the data each realization unit itself owns).
Required interactions: Replay (TD005-IU-006) -> Observation (TD005-IU-008, TD005-IU-009) -> Comparison (TD005-IU-010 through TD005-IU-013) -> Classification (TD005-IU-014) -> Evidence (TD005-IU-015, TD005-IU-016) -> Coverage (TD005-IU-017, TD005-IU-018, advisory, may run concurrently with or after Classification per TD005-AI-014's own advisory-only framing).
Forbidden interactions: never reorders the certified sequence; never itself reads active Run Engine state directly (that remains TD005-IU-009's exclusive role, TD005-AD-013); never itself computes a classification outcome or comparison result.
Lifecycle: Not-Invoked -> Invoked -> Stage-Complete, one instance per candidate execution, consistent with the per-invocation session model (TD005-SD-003) this orchestration unit itself does not own but must respect.
Failure behaviour: if any sequenced unit fails to produce its own required output, the Orchestration Unit routes the outcome to TD005-IU-014's own Invalid Comparison path rather than substituting a default or partial result (TD005-AI-019).
Traceability: aggregate - Architecture Section 11 (Component Interaction); Specification Section 9 (State Models); TD005-AI-013; TD005-ID-001.

### Domain C - Replay Execution

**TD005-IU-006. Replay Session Realization Unit.**
Purpose: realize TD005-SO-004's own controlled-condition execution behaviour.
Responsibility: produce a scientifically comparable, controlled-condition execution trajectory of the active Run Engine, for either a bootstrap reference capture or an ordinary candidate capture.
Inputs: a Controlled-Condition Manifest (TD005-ID-005); the active Run Engine's own runtime entry point.
Outputs: a captured execution trajectory on success; a Failed-state signal on failure.
Dependencies: TD005-IU-007 (identity attachment, same-layer, Architecture Layer 3).
Internal state: the current session state; the controlled-condition specification in force.
Required interactions: drives the active Run Engine through its own unmodified Stage Ordering (ADR-010; TD005-AD-003's own merge of environmental-determinism confirmation into this same unit); hands its captured trajectory to TD005-IU-008/TD005-IU-009.
Forbidden interactions: never alters Run Engine runtime semantics (TD005-AI-006); never introduces a parallel or alternative execution path to the certified active RunLoop (TD005-CON-002, TD005-II-005); never itself reads its own captured state for comparison purposes (exclusively TD005-IU-009's role).
Lifecycle: Not-Started -> Configuring -> Executing -> Captured / Failed, one instance per invocation (TD005-SD-003).
Failure behaviour: an unhandled condition, an incomplete controlled-condition specification, or a violation of a required controlled condition SHALL transition the session to Failed within a bounded duration (TD005-SI-005, TD005-AI-010, TD005-II-017); a Failed session's trajectory is never usable downstream (TD005-SI-006).
Traceability: TD005-SO-004; TD005-ARC-011; TD005-AD-003; TD005-AI-006, TD005-AI-010, TD005-AI-018, TD005-AI-019; TD005-ID-005.

**TD005-IU-007. Execution-Environment Identity Realization Unit.**
Purpose: realize TD005-SO-005's own environment-identity recording behaviour.
Responsibility: capture the execution environment's own interpreter and third-party numeric-library identity at the moment of each Replay Session's own execution.
Inputs: the active execution environment's own interpreter identity and `requirements.txt`-pinned `numpy`/`pandas` identity.
Outputs: one identity record, attachable to TD005-IU-003 or TD005-IU-006's own output.
Dependencies: none directly (Architecture Layer 3, peer to Replay).
Internal state: none persisted independently; a fresh record is produced per capture (TD005-SO-005's own Unrecorded -> Recorded model).
Required interactions: attaches its record to every Replay Session capture (TD005-IU-006) and to the Reference Baseline's own provenance (TD005-IU-003).
Forbidden interactions: never reuses a stale identity record captured for a different session.
Lifecycle: Unrecorded -> Recorded, one record per capture (TD005-SD-003).
Failure behaviour: an identity record not attached to any capture is not retained beyond that capture's own lifetime.
Traceability: TD005-SO-005; TD005-ARC-012; TD005-AD-004; TD005-AI-013, TD005-AI-016; TD005-ID-006.

### Domain D - Behaviour Comparison

**TD005-IU-008. Observable Surface Classification Realization Unit.**
Purpose: realize TD005-SO-006's own four-category field classification behaviour.
Responsibility: classify every enumerated observable field (twelve CanonicalState fields, five lifecycle event types, LONG/SHORT vocabulary, Executor status vocabulary) into exactly one of: certified external output, certified internal invariant, implementation detail, incidental intermediate value.
Inputs: the enumerated observable field set, exposed through TD005-IU-009.
Outputs: the four-category classification map.
Dependencies: TD005-IU-009 (Architecture Layer 4, same layer).
Internal state: the current classification map.
Required interactions: consumed by every Comparison-domain unit (TD005-IU-010 through TD005-IU-013).
Forbidden interactions: never permits an unclassified field to be compared.
Lifecycle: Unclassified -> Classified (TD005-SO-006's own state model, unmodified).
Failure behaviour: a field left unclassified while being compared is a defect, not a valid outcome (TD005-SI-008).
Traceability: TD005-SO-006; TD005-ARC-004; TD005-AI-002.

**TD005-IU-009. Non-Interference Observation Realization Unit.**
Purpose: realize TD005-SO-007's own non-interfering observation behaviour.
Responsibility: expose active Run Engine state at each tick boundary without altering the behaviour being observed.
Inputs: the active Run Engine's own Tick-Complete state, during a Replay Session (TD005-IU-006).
Outputs: an observed state snapshot per tick.
Dependencies: TD005-IU-006 (same layer, Architecture Layer 4).
Internal state: the current session-relative tick index.
Required interactions: this is the exclusive component permitted to read active Run Engine state directly (TD005-AD-013, TD005-II-011); exposes snapshots to TD005-IU-008 and, transitively, every Comparison unit.
Forbidden interactions: any component other than this one reading active Run Engine state directly; any read that mutates, delays, or measurably alters Run Engine state or timing.
Lifecycle: Idle -> Reading -> Exposed -> Idle, repeating per tick (TD005-SO-007's own state model, unmodified).
Failure behaviour: a detected mutating observation act SHALL transition the associated Replay Session to Failed (TD005-SI-005, TD005-AI-019); this unit itself never silently absorbs such an event.
Traceability: TD005-SO-007; TD005-ARC-005; TD005-AI-002; TD005-AD-013.

**TD005-IU-010. Behavioural Equivalence Definition Realization Unit.**
Purpose: realize TD005-SO-008's own formal, operational equivalence definition.
Responsibility: compose trajectory equivalence (TD005-IU-011) and value-level equivalence (TD005-IU-012, TD005-IU-013) into one internally consistent definition.
Inputs: the classified observable surface (TD005-IU-008); the trajectory model (TD005-IU-011); the value-comparison rules (TD005-IU-012, TD005-IU-013).
Outputs: a formal equivalence definition, consumed by TD005-IU-014.
Dependencies: TD005-IU-008 (Architecture Layer 4); TD005-IU-011, TD005-IU-012, TD005-IU-013 (Architecture Layer 5, same layer as this unit).
Internal state: which constituent models are currently incorporated.
Required interactions: consumed exclusively by TD005-IU-014.
Forbidden interactions: never defines equivalence as byte, source, or implementation identity (TD005-AI-007, TD005-SI-009).
Lifecycle: Undefined -> Defined -> Applied (TD005-SO-008's own state model, unmodified).
Failure behaviour: a definition missing one of its three constituent models is never applied to a live comparison.
Traceability: TD005-SO-008; TD005-ARC-006; TD005-AI-007.

**TD005-IU-011. Trajectory Comparison Realization Unit.**
Purpose: realize TD005-SO-010's own trajectory-versus-endpoint comparison behaviour.
Responsibility: evaluate trajectory-required properties across the complete captured trajectory using logical-order semantics only; evaluate final-state-only properties using the final observed state alone.
Inputs: two observed, fully classified trajectories (reference and candidate).
Outputs: a trajectory-level comparison basis, consumed by TD005-IU-010 and TD005-IU-014.
Dependencies: TD005-IU-008, TD005-IU-009 (Architecture Layer 4).
Internal state: the trajectory-required property set currently in force; the trajectory representation concept (TD005-ID-007).
Required interactions: consumed by TD005-IU-010 and TD005-IU-014.
Forbidden interactions: never treats a wall-clock timing difference as a trajectory-equivalence violation; never substitutes final-state-only comparison for a trajectory-required property (TD005-AI-004).
Lifecycle: Undefined -> Defined -> Applied (TD005-SO-010's own state model, unmodified).
Failure behaviour: applying final-state-only comparison to a trajectory-required property is a defect, never a valid outcome.
Traceability: TD005-SO-010; TD005-ARC-007; TD005-AI-004; TD005-ID-007.

**TD005-IU-012. Numeric and Categorical Comparison Realization Unit.**
Purpose: realize TD005-SO-011's own two-category comparison structure.
Responsibility: assign every observed value to exactly one of exact-equality or tolerance-bounded, and apply the corresponding comparison policy.
Inputs: individual observed values from TD005-IU-008's own classified surface.
Outputs: a per-value comparison-category assignment and result, consumed by TD005-IU-014.
Dependencies: TD005-IU-008 (Architecture Layer 4).
Internal state: the current category assignment for each observed value; the tolerance-policy shape (TD005-ID-008).
Required interactions: consumed by TD005-IU-010 and TD005-IU-014; applies the identical tolerance policy to the reference value and the candidate value in every comparison, never an asymmetric one (TD005-II-007).
Forbidden interactions: never applies exact equality to a tolerance-bounded value or vice versa.
Lifecycle: Undefined -> Defined -> Applied (TD005-SO-011's own state model, unmodified).
Failure behaviour: a value left uncategorized while being compared is a defect, never a valid outcome.
Traceability: TD005-SO-011; TD005-ARC-008; TD005-SI-011; TD005-ID-008.

**TD005-IU-013. Object-Identity-Independent Comparison Realization Unit.**
Purpose: realize TD005-SO-012's own structural-value-equality rule.
Responsibility: compare every observed value by structural value equality, never by object identity or process-local mutable state.
Inputs: individual observed values from TD005-IU-008's own classified surface.
Outputs: an identity-independent comparison rule, consumed by TD005-IU-014.
Dependencies: TD005-IU-008 (Architecture Layer 4).
Internal state: confirmation, per comparison, that only structural value equality was used.
Required interactions: consumed by TD005-IU-010 and TD005-IU-014.
Forbidden interactions: no comparison outcome depending on object identity, dict/list identity, or process-local mutable-state identity.
Lifecycle: Undefined -> Defined -> Applied (TD005-SO-012's own state model, unmodified).
Failure behaviour: an identity-dependent comparison outcome is never treated as a valid application of this unit's own rule.
Traceability: TD005-SO-012; TD005-ARC-009; TD005-SI-012.

### Domain E - Classification Execution

**TD005-IU-014. Regression Classification Realization Unit.**
Purpose: realize TD005-SO-013's own exhaustive, four-outcome classification behaviour.
Responsibility: classify every evaluated deviation into exactly one of Regression, Non-Regression, Indeterminate, or Invalid Comparison, via the ordered decision procedure TD005-ID-009 defines.
Inputs: an observed deviation; TD005-IU-002's boundary determination; TD005-IU-010's equivalence definition; advisory coverage context from TD005-IU-017, TD005-IU-018.
Outputs: exactly one classification outcome per evaluated deviation.
Dependencies: TD005-IU-002, TD005-IU-006, TD005-IU-009, TD005-IU-010, TD005-IU-011, TD005-IU-012, TD005-IU-013 (Architecture Layer 6).
Internal state: the classification outcome; the specific unresolved condition, if Indeterminate or Invalid Comparison.
Required interactions: reports its outcome to TD005-IU-015 (Evidence) when required; receives, but never yields to, advisory input from TD005-IU-017/TD005-IU-018.
Forbidden interactions: never computes severity, waiver, priority, or disposition (TD005-AI-009, TD005-II-010); never permits Coverage output to override a reached classification (TD005-AI-014); never treats a Failed Replay/Observation/Comparison condition as Regression or Non-Regression, and never elevates Classification's own exclusions above a binding, restated rule (TD005-AD-008).
Lifecycle: Pending -> Evaluating -> one of four Classified-* states; a Classified-* state may transition to a different Classified-* state only given an explicit, independently-recorded re-evaluation (TD005-SO-013's own state model, unmodified, including the Specification's own V1.1 explicit-re-evaluation clarification).
Failure behaviour: any upstream unit's failure to produce its own required output routes here as Invalid Comparison, never a default Regression or Non-Regression (TD005-AI-019).
Traceability: TD005-SO-013; TD005-ARC-017; TD005-AI-007, TD005-AI-008, TD005-AI-009, TD005-AI-013, TD005-AI-014, TD005-AI-019; TD005-AD-008; TD005-SD-001; TD005-ID-009.

### Domain F - Evidence Generation

**TD005-IU-015. Regression Evidence Composition Realization Unit.**
Purpose: realize TD005-SO-016's own eight-element evidence-composition behaviour, including the reasoned-unavailability-marker accommodation.
Responsibility: compose one complete evidence record per Regression, Indeterminate, or Invalid Comparison outcome, per the field schema TD005-ID-011 defines.
Inputs: a classification outcome (TD005-IU-014); the controlled-condition record (TD005-IU-006); the identity record (TD005-IU-007); the boundary determination (TD005-IU-002).
Outputs: one complete evidence record.
Dependencies: TD005-IU-002, TD005-IU-006, TD005-IU-007, TD005-IU-014 (Architecture Layer 7).
Internal state: the evidence record's own eight (or, where a marker applies, up to nine) elements.
Required interactions: hands each Composed record to TD005-IU-016.
Forbidden interactions: never modifies observed behaviour, the reference baseline, or the classification outcome as a side effect of composing evidence (TD005-AI-005); never omits a required element without either a determinate value or a reasoned unavailability marker.
Lifecycle: Not-Composed -> Composing -> Composed (TD005-SO-016's own state model, unmodified, including the Specification's own V1.1 unavailability-marker accommodation).
Failure behaviour: a record missing any element, with neither a determinate value nor a reasoned marker, never reaches Composed.
Traceability: TD005-SO-016; TD005-ARC-013; TD005-AI-005; TD005-SD-004; TD005-ID-011.

**TD005-IU-016. Evidence Persistence and Continuity Realization Unit.**
Purpose: realize TD005-SO-017's own persistence-and-continuity behaviour.
Responsibility: persist every Composed evidence record and preserve its own retrievability, unaltered, across every subsequent Long-Duration-Validation stage transition.
Inputs: Composed evidence records (TD005-IU-015).
Outputs: a persisted, continuity-linked evidence record.
Dependencies: TD005-IU-015 (Architecture Layer 7).
Internal state: the persistence status of each record; the retention/expiry status, once named (explicitly not named by this document, TD005-ID-012).
Required interactions: hands persisted records to TD005-IU-019's own cross-stage continuity chain.
Forbidden interactions: never modifies a persisted record's own content (TD005-II-006); never places a record outside Repository Consolidation's own Normative Repository Boundary (TD005-AI-015, TD005-II-016); never treats a partially-written record (an interrupted persist operation) as reaching the Persisted state.
Lifecycle: Unpersisted -> Persisted -> Retained -> Expired (once Implementation defines a retention/expiry policy) (TD005-SO-017's own state model, unmodified). The persist operation itself is atomic: it either completes in full, reaching Persisted, or does not occur at all, remaining Unpersisted; no intermediate, partially-written state is ever observable to any consumer (TD005-ID-012).
Failure behaviour: a persisted record found altered is invalid by definition; the alteration itself is the defect, not a state this unit tolerates. A persist operation interrupted before completion (for example, by a process failure) SHALL leave the record in the Unpersisted state, eligible for a fresh compose-and-persist attempt from a subsequent invocation (Section 8, Restart); it SHALL NOT be treated as Persisted-and-Altered, since it was never validly Persisted in the first place.
Traceability: TD005-SO-017; TD005-ARC-014; TD005-AI-005, TD005-AI-015, TD005-AI-017; TD005-ID-012, TD005-ID-014.

### Domain G - Coverage Generation

**TD005-IU-017. Contract-to-Requirement Coverage Realization Unit.**
Purpose: realize TD005-SO-014's own contract/requirement coverage-audit behaviour.
Responsibility: confirm every certified contract is traceable to a Functional Requirement and vice versa, recomputing on corpus drift.
Inputs: TD005-IU-001's corpus enumeration; the FRA's own twenty-two Functional Requirements.
Outputs: a coverage-completeness report, advisory to TD005-IU-014.
Dependencies: TD005-IU-001 (Architecture Layer 6, same layer as Coverage generally).
Internal state: the current report's own gap list; the corpus-enumeration version it was computed against.
Required interactions: informs, never overrides, TD005-IU-014 (TD005-AI-014, TD005-II-015).
Forbidden interactions: never suppresses or overrides a classification outcome.
Lifecycle: Not-Computed -> Computed -> Stale -> Recomputed (TD005-SO-014's own state model, unmodified).
Failure behaviour: a stale report is never silently treated as current.
Traceability: TD005-SO-014; TD005-ARC-015; TD005-AI-014.

**TD005-IU-018. Module and State-Transition Coverage Realization Unit.**
Purpose: realize TD005-SO-015's own module/state-transition coverage-audit behaviour, per the coverage concept TD005-ID-010 defines.
Responsibility: confirm every active module and certified state transition is covered by the Functional Requirements, recomputing on scope drift.
Inputs: the active module set (TD005-IU-022); the FRA's own Functional Requirements; ADR-009's own Lifecycle Transition Table.
Outputs: a module/state-transition coverage report, advisory to TD005-IU-014.
Dependencies: TD005-IU-022 (Architecture Layer 6/9, cross-layer signal per TD005-SO-021's own drift-trigger relationship).
Internal state: the current report's own module and state-transition gap list.
Required interactions: informs, never overrides, TD005-IU-014.
Forbidden interactions: never treats a RETAIN-Deferred-Scope module's own future reactivation as automatically covered.
Lifecycle: Not-Computed -> Computed -> Stale -> Recomputed (TD005-SO-015's own state model, unmodified).
Failure behaviour: a stale report is never silently treated as current.
Traceability: TD005-SO-015; TD005-ARC-016; TD005-AI-014; TD005-ID-010.

### Domain H - Governance Integration

**TD005-IU-019. Long-Duration-Validation Integration Realization Unit.**
Purpose: realize TD005-SO-018's own single-invocation-contract behaviour across all six Long-Duration-Validation stages.
Responsibility: expose one invocation contract, applied pre-run before each stage, identical in every observable respect across all six stages, per TD005-ID-013.
Inputs: the six-stage Long-Duration-Validation sequence (Implementation Baseline); persisted evidence records (TD005-IU-016).
Outputs: a stage-applicable invocation contract; the evidence-continuity chain across completed stages.
Dependencies: TD005-IU-005 (the invocation contract is realized by invoking the Orchestration Unit); TD005-IU-016 (Architecture Layer 9).
Internal state: the current stage; the evidence-continuity chain.
Required interactions: invokes TD005-IU-005 identically before each of the six stages.
Forbidden interactions: never introduces a stage-specific variant of the invocation contract (TD005-SI-019, TD005-II-009).
Lifecycle: Not-Invoked -> Invoked -> Stage-Complete -> Invoked (next stage, identical contract) (TD005-SO-018's own state model, unmodified).
Failure behaviour: losing evidence continuity across a stage transition is a defect, never a tolerated outcome.
Traceability: TD005-SO-018; TD005-ARC-018; TD005-SI-019; TD005-ID-013.

**TD005-IU-020. Governance Sequence Conformance Realization Unit.**
Purpose: realize TD005-SO-019's own static conformance-recording behaviour.
Responsibility: record this governance chain's own explicit refusal to select implementation-inappropriate content at each stage, providing a citable artifact for future review.
Inputs: none (a governance-metadata unit; consumes no runtime information).
Outputs: a governance-conformance record.
Dependencies: none (a static marker, Architecture Layer 10).
Internal state: the conformance record itself.
Required interactions: referenced by any future Architecture or Specification Evolution Review (Implementation Baseline Principle IP-006).
Forbidden interactions: never contains Implementation-level content beyond the conformance record itself.
Lifecycle: Conformant (static, TD005-SO-019's own state model, unmodified).
Failure behaviour: this Implementation Specification, or any future revision, proceeding out of the established governance sequence would itself be Non-Conformant; no such proceeding occurs in this document.
Traceability: TD005-SO-019; TD005-ARC-019; TD005-DEP-033.

### Domain I - Extension Integration

**TD005-IU-021. Specification Extension Point Registry Realization Unit.**
Purpose: realize TD005-SO-020's own registry behaviour, now also recording this document's own fifteen Implementation Decisions as resolved registry entries.
Responsibility: enumerate, by name, every mechanism decision still open after this Implementation Specification, attached to its own owning Implementation Unit; ensure no further mechanism choice (concrete numeric constants, empirical calibration) is made without being recorded here first.
Inputs: every Implementation Unit's own remaining unresolved mechanism boundary (Section 16).
Outputs: the still-open Implementation handover list (Section 16), the primary artifact actual code-writing Implementation consumes.
Dependencies: every other Implementation Unit (Architecture Layer 9).
Internal state: the registry's own current entry list, now partitioned into "resolved by this document" (fifteen entries, TD005-ID-001 through TD005-ID-015) and "still open" (the remainder, Section 16).
Required interactions: consulted before any remaining mechanism choice is treated as binding.
Forbidden interactions: never allows a mechanism choice to be made against an Implementation Unit without an entry here first.
Lifecycle: Incomplete -> Complete (TD005-SO-020's own state model, unmodified).
Failure behaviour: a registry claiming completeness while an Implementation Unit's own deferral is unlisted is a defect, never a valid Complete state.
Traceability: TD005-SO-020; TD005-ARC-022; TD005-SI-022; TD005-ID-001, TD005-ID-002, TD005-ID-003, TD005-ID-004, TD005-ID-005, TD005-ID-006, TD005-ID-007, TD005-ID-008, TD005-ID-009, TD005-ID-010, TD005-ID-011, TD005-ID-012, TD005-ID-013, TD005-ID-014, TD005-ID-015 (all fifteen, individually).

### Domain L - Repository Boundary Protection

**TD005-IU-022. Active/Deferred Scope Boundary Realization Unit.**
Purpose: realize TD005-SO-021's own scope-stability and drift-sensitivity behaviour, per TD005-ID-015's own re-derivation method.
Responsibility: re-derive the active/inactive Run Engine module partition via fresh, static AST-based import-closure analysis at the start of every Replay Session and Observation act, never via a cached or hand-maintained list.
Inputs: the `run_engine/` module tree.
Outputs: the current scope boundary, consumed by every Implementation Unit whose own scope presupposes "the active Run Engine."
Dependencies: none (foundational; Architecture Layer 9, re-evaluated at every session start regardless of layer).
Internal state: the current active/inactive partition; the drift status.
Required interactions: signals TD005-IU-018 to recompute on drift.
Forbidden interactions: never treats a future reactivation of a RETAIN-Deferred-Scope module as in-scope without a separate, governed Architecture Evolution Review (TD005-AI-011).
Lifecycle: Stable -> Drift-Detected -> Re-Confirmed (TD005-SO-021's own state model, unmodified).
Failure behaviour: assuming the partition unchanged without re-evaluation is a defect, never a tolerated outcome (TD005-SI-020).
Traceability: TD005-SO-021; TD005-ARC-020; TD005-AI-011; TD005-ID-014, TD005-ID-015.

**TD005-IU-023. Executor Namespace Boundary Realization Unit.**
Purpose: realize TD005-SO-022's own explicit-exclusion behaviour, retained as an explicit exclusion component per the Architecture's own precedent (TD005-AD-009) rather than a silent omission.
Responsibility: record, at the implementation level, that no Implementation Unit in this document owns, extends, or duplicates Repository Consolidation's own Executor-namespace-uniqueness protection.
Inputs: none (a boundary-marker unit; consumes no runtime information).
Outputs: an explicit exclusion record.
Dependencies: none (a static marker, Architecture Layer 9).
Internal state: the exclusion record itself.
Required interactions: none beyond the exclusion record's own citability.
Forbidden interactions: any Implementation Unit re-implementing or duplicating Repository Consolidation's own Executor-namespace check (RC-AD-004, TD005-II-013).
Lifecycle: Excluded (static, TD005-SO-022's own state model, unmodified).
Failure behaviour: a future revision of this document silently absorbing this responsibility would itself be the defect (Absorbed, TD005-SO-022's own Invalid state).
Traceability: TD005-SO-022; TD005-ARC-021; TD005-AI-012; TD005-SI-021; TD005-AD-009.

All twenty-three Implementation Units are individually numbered with no gap; every accepted Specification Object (TD005-SO-001 through TD005-SO-022) is realized by exactly one Implementation Unit; one additional, explicitly justified aggregate unit (TD005-IU-005) closes the sequencing gap Architecture's own Component Interaction section left open.

## 8. Runtime Lifecycle

Concurrent invocation of the Orchestration Unit (two or more invocations executing simultaneously) is outside this document's own scope: the CGA's own hidden-assumption audit already examined process count/concurrency and found it unsupported by repository evidence (zero threading, multiprocessing, or asyncio imports across all fourteen active modules), recording it as examined-and-rejected rather than silently skipped. This Implementation Specification inherits that finding rather than re-opening it; every lifecycle stage below assumes exactly one invocation in flight at a time, consistent with the active Run Engine's own single-threaded nature (Section 5).

- **Initialization.** The Orchestration Unit (TD005-IU-005) is invoked with a controlled-condition specification. Before sequencing begins, it confirms: the Reference Baseline (TD005-IU-003) is in the Established state; the active/inactive scope boundary (TD005-IU-022) has been re-confirmed for the current session (TD005-SI-020); the Certified Contract Corpus (TD005-IU-001) is in the Enumerated state. No Implementation Unit begins work before these three preconditions hold.
- **Execution.** The Orchestration Unit sequences Replay (TD005-IU-006, with TD005-IU-007 attaching identity) -> Observation (TD005-IU-008, TD005-IU-009) -> Comparison (TD005-IU-010 through TD005-IU-013) -> Classification (TD005-IU-014), with Coverage (TD005-IU-017, TD005-IU-018) informing Classification in advance, never after (TD005-AI-014).
- **Completion.** A single classification outcome is reached (TD005-IU-014); for Regression, Indeterminate, or Invalid Comparison, evidence is composed (TD005-IU-015) and persisted (TD005-IU-016) before the invocation is considered complete (TD005-SI-016).
- **Failure.** Any sequenced unit's failure to produce its own required output routes the invocation to the Invalid Comparison outcome (TD005-AI-019); this is a completion path, not a distinct pipeline-level failure state, since TD005-SO-013's own four-outcome model already accounts for it.
- **Cancellation.** An externally-initiated cancellation of an in-flight invocation is realized as the in-flight Replay Session (TD005-IU-006) or Observation act (TD005-IU-009) transitioning to Failed (consistent with TD005-SI-005's own bounded-duration guarantee); no separate "Cancelled" pipeline state is introduced, since the per-invocation session model (TD005-SD-003) already treats every non-completing invocation identically, regardless of the external trigger.
- **Restart.** A restart is realized as a new Orchestration Unit invocation with a new controlled-condition specification; no Implementation Unit resumes a prior, non-completed invocation's own internal state (TD005-SD-003's own bounded-lifecycle discipline; TD005-SI-006). This applies identically whether the prior invocation failed outright or reached partial completion (for example, a classification outcome was reached but its own evidence record failed to persist, TD005-IU-016): a restart always re-runs the complete sequence from Replay, never resumes from the point of partial completion, since no Implementation Unit's own state model defines a resumable intermediate state.
- **Cleanup.** No Implementation Unit owns a persistent, always-running process; the per-invocation session model (TD005-SD-003) means each invocation's own transient state (session-relative tick index, in-flight comparison state, the classification outcome and its evidence composition for that one invocation) is naturally released at Stage-Complete. This is distinct from the Authority/Registry-pattern units' own longer-lived state, which by design survives across invocations and is never released at Stage-Complete: the Certified Contract Corpus (TD005-IU-001), the Certification Boundary (TD005-IU-002), the Reference Baseline (TD005-IU-003), the Behavioural Vocabulary (TD005-IU-004), persisted Evidence (TD005-IU-016), the Coverage reports (TD005-IU-017, TD005-IU-018), and the Active/Deferred Scope Boundary (TD005-IU-022) - each governed by its own Undefined/Uninitialized-to-Established/Enumerated-style lifecycle (Section 9 of the Specification), not the bounded per-invocation session model TD005-SD-003 establishes for Replay and Observation alone.

## 9. Component Interaction

**Call order.** Section 8 (Execution) states the canonical order, which the Orchestration Unit alone enforces without ever reordering it (TD005-II-003). No Implementation Unit is permitted to call a unit belonging to a later stage before its own stage's required output is available (TD005-AI-013, verified by construction against the Architecture's own ten-layer structure: every Implementation Unit's own Dependencies field names only same-layer or lower-layer units, with two documented exceptions: TD005-IU-003's own one-time bootstrap dependency on TD005-IU-006/TD005-IU-007 (TD005-AI-018), and TD005-IU-018's own cross-layer dependency on TD005-IU-022 (Layer 6 depending on Layer 9, per TD005-SO-021's own drift-trigger relationship, Section 7) - both already individually justified at their own point of use, not newly introduced here).

**Sequencing.** The Orchestration Unit (TD005-IU-005) is the sole unit responsible for internal pipeline sequencing; every unit within the internal pipeline (Replay through Coverage, TD005-IU-006 through TD005-IU-018) exposes its own output without itself invoking a downstream unit, preserving the Architecture's own logical-interface-only interaction model (Section 11 of the Architecture) without introducing a concrete API. This rule governs only the internal pipeline; it does not forbid TD005-IU-019 from invoking TD005-IU-005 as a whole, once per Long-Duration-Validation stage (Section 8, Section 13, TD005-ID-013) - that is an external, whole-pipeline invocation triggering a fresh instance of the entire sequence, categorically distinct from one internal-pipeline unit reordering or reaching into another's own stage, and does not create a dependency of TD005-IU-005 on TD005-IU-019 (Section 7, TD005-IU-005's own corrected Dependencies field).

**Ownership transfer.** Data ownership transfers exactly once per artifact, never shared: TD005-IU-006 owns a captured trajectory until TD005-IU-009 exposes it as an observed snapshot; TD005-IU-014 owns a classification outcome until TD005-IU-015 composes evidence for it; TD005-IU-015 owns a Composed evidence record until TD005-IU-016 persists it, at which point TD005-IU-016 owns it exclusively (TD005-SO-016/TD005-SO-017's own ownership boundary, Section 12 of the Specification, unmodified).

**Data publication.** Every publication is a one-time, immutable act within its own owning unit's lifecycle: one Tick-Complete snapshot per tick (TD005-IU-009); one classification outcome per evaluated deviation (TD005-IU-014, absent an explicit recorded re-evaluation); one Composed evidence record per qualifying outcome (TD005-IU-015).

**Synchronization points.** Three synchronization points exist, each already named in Section 8: (1) Reference Baseline Established, before any comparison may begin; (2) Scope Boundary Re-Confirmed, before any Replay or Observation session begins; (3) Evidence Composed, before a Regression/Indeterminate/Invalid-Comparison outcome is considered complete. No other synchronization point is required by the accepted Specification.

## 10. Failure Model

**Recoverable failures.** A Replay Session (TD005-IU-006) or Observation act (TD005-IU-009) reaching Failed for its own current invocation is recoverable at the pipeline level: a fresh invocation (Section 8, Restart) may be attempted with a corrected or unchanged controlled-condition specification. The failed invocation's own trajectory is never reused (TD005-SI-006).

**Non-recoverable failures.** A Reference Baseline (TD005-IU-003) bootstrap capture reaching Failed is non-recoverable for that specific bootstrap attempt (the record never becomes Established from it) but does not block a fresh bootstrap attempt. A Certification Boundary (TD005-IU-002) rule yielding an Ambiguous determination is non-recoverable by any comparison-level retry; it requires a governed revision of the rule itself (TD005-SO-002's own Undefined/Defined/Revised model), outside this pipeline's own runtime scope.

**Retry eligibility.** Any per-invocation session (Replay, Observation) is eligible for an unlimited number of fresh invocations, since each is a new, independent instance under the per-invocation session model (TD005-SD-003); no session-level retry count or backoff policy is specified here, since no accepted-baseline requirement names one (correctly left to actual Implementation, not invented).

**Abort conditions.** The Orchestration Unit aborts the current invocation (routing to Invalid Comparison, never a partial success) whenever: a Replay Session reaches Failed; an Observation act detects a Mutating condition (TD005-SI-007); a Certification Boundary determination is Ambiguous; the Reference Baseline is not in the Established state at invocation start; or any Comparison-domain unit (TD005-IU-010 through TD005-IU-013) fails to reach a valid Applied definition, category assignment, or comparison result (TD005-AI-019). This list names every condition the accepted Specification and Architecture individually evidence; it is the complete, exhaustive expansion of Section 8's own general rule ("any sequenced unit's failure to produce its own required output"), not an illustrative subset of it.

**Evidence obligations.** Every abort that reaches a classified outcome other than Non-Regression triggers Evidence composition before the invocation is considered complete (TD005-SD-004, TD005-SI-016); an abort that never reaches a classified outcome at all (for example, the Reference Baseline precondition failing before Classification is even entered) is not itself a classified deviation and therefore does not require an Evidence record - it is an invocation-level precondition failure, reported through the Orchestration Unit's own Lifecycle (Section 7, TD005-IU-005), not through TD005-IU-015.

## 11. Extension Model

**Extension lifecycle.** An extension resolves exactly one named entry in TD005-IU-021's own registry (Section 16); it does not exist as an independent lifecycle outside that registry entry's own Incomplete -> Complete transition (TD005-SO-020's own state model).

**Extension registration.** Every extension-point resolution (a concrete tolerance constant, a concrete persistence format, a concrete coverage-computation algorithm) is recorded against its own named Implementation Unit in TD005-IU-021's registry before being treated as binding (TD005-SI-022, TD005-AI-016, TD005-II-012); this Implementation Specification's own fifteen Implementation Decisions are themselves the first, design-level layer of such registration, with any remaining code-level choice recorded as a further registry entry at actual Implementation time.

**Extension isolation.** A mechanism choice for one Implementation Unit SHALL NOT alter the behavioural contract of any other Implementation Unit (mirrors TD005-SO-020's own isolation rule, Section 14 of the Specification); TD005-IU-007's own standalone-versus-folded resolution (TD005-ID-006) is the documented worked example: choosing to keep it standalone required no change to TD005-IU-003's or TD005-IU-006's own contract.

**Extension compatibility.** Any code-level mechanism choice SHALL satisfy the full behavioural contract of the Implementation Unit it resolves (mirrors the Specification's own compatibility rule); a choice satisfying only part of a contract requires an explicit amendment to this document, not a silent extension.

**Extension validation.** Every extension-point resolution follows the same FRA -> SDA -> CGA -> Architecture -> Specification -> Implementation Specification -> Implementation -> Final Certification sequence this entire governance chain has followed (TD005-IU-020); no mechanism choice bypasses Implementation Baseline Principle IP-006 (Controlled Architectural Evolution).

## 12. Implementation Invariants

**TD005-II-001.** No Implementation Unit, Invariant, or Decision SHALL exist without derivation from one or more accepted Specification Objects, Specification Decisions, Specification Invariants, Architecture Components, or an explicitly justified aggregate concern. Traceability: Section 6; Section 15.

**TD005-II-002.** No Implementation Unit SHALL realize behaviour beyond its own owning Specification Object's Required/Forbidden behaviour (Section 8 of the Specification). Traceability: TD005-SI-001.

**TD005-II-003.** The Regression Pipeline Orchestration Unit (TD005-IU-005) SHALL invoke realization units strictly in the certified sequence (Section 8, Section 9); it SHALL NOT reorder Replay, Observation, Comparison, Classification, Evidence, or Coverage relative to one another. Traceability: ADR-010; TD005-AI-013.

**TD005-II-004.** No Implementation Unit other than TD005-IU-009 SHALL read active Run Engine state directly. Traceability: TD005-CON-001, TD005-AI-002, TD005-AD-013.

**TD005-II-005.** No Implementation Unit SHALL introduce an alternative execution path to the certified active RunLoop. Traceability: TD005-CON-002, TD005-AI-006, Architecture Defect AD-007.

**TD005-II-006.** Evidence realization units (TD005-IU-015, TD005-IU-016) SHALL preserve the immutability of a Composed evidence record; a correction SHALL produce a new, separate record. Traceability: TD005-AI-005, TD005-SI-017.

**TD005-II-007.** The tolerance-comparison mechanism (TD005-IU-012) SHALL apply an identical tolerance policy to the reference and the candidate value in every comparison; no asymmetric treatment SHALL exist. Traceability: TD005-SI-011; TD005-ID-008.

**TD005-II-008.** The Active/Deferred Scope Boundary Realization Unit (TD005-IU-022) SHALL re-derive the module partition using static analysis only; it SHALL NOT execute or import active Run Engine modules as a side effect of scope determination. Traceability: TD005-SI-020; TD005-ID-015.

**TD005-II-009.** The Long-Duration-Validation invocation contract (TD005-IU-019) SHALL remain identical across all six mandatory stages; no stage-specific variant SHALL exist. Traceability: TD005-SI-019.

**TD005-II-010.** No Implementation Unit SHALL compute, store, or expose severity, business acceptability, waiver status, remediation priority, or operational disposition, under any classification outcome. Traceability: TD005-AI-009, TD005-SI-014.

**TD005-II-011.** Every Implementation Unit that consumes active Run Engine state SHALL do so exclusively through TD005-IU-009's own exposed snapshot; no Implementation Unit SHALL establish, request, cache independently, or otherwise accept active Run Engine state through any channel other than that snapshot. (This is a channel-exclusivity rule, distinct from TD005-II-004's own act-level prohibition on reading directly: TD005-II-004 governs who may touch the source, TD005-II-011 governs how every other unit may consume the result, closing the gap a unit could otherwise exploit by accepting a copy of Run Engine state relayed through an unofficial path rather than reading it directly itself.) Traceability: TD005-AD-013; TD005-ARC-005.

**TD005-II-012.** Every Implementation Decision resolving a Specification-registry deferral (Section 18 of the Specification) SHALL be recorded in TD005-IU-021's own registry before being treated as binding on any other Implementation Unit. Traceability: TD005-SI-022.

**TD005-II-013.** No Implementation Unit SHALL absorb, duplicate, or re-implement Repository Consolidation's own Executor-namespace-uniqueness protection. Traceability: TD005-AI-012, TD005-SI-021.

**TD005-II-014.** Every evidence record's own reasoned-unavailability marker (TD005-IU-015) SHALL name the specific upstream condition that prevented a determinate value; a generic or unexplained marker SHALL NOT satisfy this element. Traceability: TD005-SI-016 (Specification V1.1 accommodation); TD005-ID-011.

**TD005-II-015.** Coverage realization units (TD005-IU-017, TD005-IU-018) SHALL remain advisory-only; no coverage report SHALL gate, block, or alter a classification result already reached. Traceability: TD005-AI-014, TD005-SI-015.

**TD005-II-016.** No Implementation Unit SHALL select a persistence location inconsistent with Repository Consolidation's own Normative Repository Boundary. Traceability: TD005-AI-015, TD005-SI-018; TD005-ID-012, TD005-ID-014.

**TD005-II-017.** The Replay Session Realization Unit (TD005-IU-006) SHALL reach a terminal state (Captured or Failed) within a bounded, bounded-at-Implementation-time duration; it SHALL NOT remain indefinitely in the Executing state. Traceability: TD005-SI-005.

**TD005-II-018.** Regression-capability artifacts SHALL reside only within the location this document designates (TD005-ID-014) unless a governed Architecture or Specification Evolution Review changes it. Traceability: TD005-CON-003; TD005-ID-014.

All eighteen invariants are individually numbered with no gap; none is referenced elsewhere in this document only via a compressed range.

## 13. Implementation Decisions

**TD005-ID-001. Add a New Aggregate Regression Pipeline Orchestration Unit.**
Decision: introduce TD005-IU-005, not a 1:1 realization of any single Specification Object, to own call-order sequencing.
Context: Architecture's own Section 11 (Component Interaction) describes sequencing (preconditions, postconditions, logical interfaces) as a cross-component concern, explicitly stating "no APIs" and never assigning sequencing ownership to any one of the twenty-two components.
Alternatives considered: (a) leave sequencing implicit, letting each Implementation Unit call its own successor directly; (b) the chosen dedicated Orchestration Unit.
Justification: distributing sequencing responsibility across every unit (option a) would require each unit to know its own downstream successor, violating the one-responsibility-per-unit design principle (Section 6) and risking silent reordering as units are modified independently; a single, dedicated, aggregate-traceability unit is the same evidence-driven extension pattern already used by TD005-AD-007 (Architecture) and TD005-SD-002 (Specification).
Traceability: Architecture Section 11; TD005-AI-013; TD005-AD-007 (precedent).
Consequences: TD005-IU-005 owns no domain data, only sequencing; every other unit's own Dependencies field is stated relative to the units whose output it consumes, never relative to the Orchestration Unit itself.

**TD005-ID-002. Corpus-Enumeration Mechanism: Governance Citation Manifest.**
Decision: realize TD005-IU-001's own enumeration as a Governance Citation Manifest concept - an ordered listing of the certified-contract corpus's own primary-evidence sources, re-derived by direct citation-walk of the Architecture Baseline, Implementation Baseline, the six certified units' own Final Certifications, and the Technical Debt Register, never a separately and independently maintained database that could drift from those sources.
Context: TD005-SO-001's own Section 18 deferral named "corpus-enumeration mechanism (format, location, maintenance process)" as open.
Alternatives considered: (a) a separately maintained, independent list requiring manual synchronization; (b) the chosen citation-walk-derived manifest, re-derivable on demand.
Justification: TD005-SI-002 already requires the corpus to be "re-derivable from primary repository evidence on demand"; a separately maintained list would violate this invariant by construction, since it introduces a second source of truth.
Traceability: TD005-SO-001, TD005-SI-002.
Consequences: no new file format is created by this decision; the manifest concept is a re-derivation procedure, not a stored artifact.

**TD005-ID-003. Certification-Boundary Application Rule: Three Contract-Type Categories.**
Decision: TD005-IU-002 applies the certification-boundary rule using exactly three contract-type categories - ADR-sourced, AC-sourced (Acceptance Criterion), and Certified-Unit-Finding-sourced - each requiring a citable source in its own accepted document.
Context: TD005-SO-002's own Section 18 deferral named "per-contract-type certification-boundary application rule" as open.
Alternatives considered: (a) a single undifferentiated "certified" flag with no category structure; (b) the chosen three-category structure, mirroring the three evidentiary forms the Architecture Baseline and the six certified units already use.
Justification: the Architecture Baseline's own content is already organized into ADRs and Acceptance Criteria, and the six certified units' own Final Certifications are the third recurring evidentiary form (Section 6.7 of the FRA); reusing this existing three-way structure avoids inventing an unsupported fourth category.
Traceability: TD005-SO-002; FRA Section 6.4, Section 6.7.
Consequences: a candidate lacking a citable source in any of the three categories is not certified, with no fallback category.

**TD005-ID-004. Reference-Reproduction Mechanism: Freshly-Established Baseline.**
Decision: TD005-IU-003 sources its reference-baseline record from a freshly-established bootstrap capture, not a reconstruction from a historical commit.
Context: TD005-SO-003's own Section 18 deferral named "reference-reproduction mechanism (source selection... immutability-or-governed-change procedure)" as open; OQ-002 (SDA Section 18) left this exact source-selection question open.
Alternatives considered: (a) reconstruct the reference from a specific historical commit's own state; (b) the chosen freshly-established bootstrap capture, using the currently active, certified Run Engine.
Justification: a historical-commit reconstruction would require replaying an old commit's own code, introducing exactly the kind of "alternative execution path" TD005-CON-002 forbids for ordinary candidate captures and creating an unnecessary second code path solely for bootstrap; a freshly-established capture uses the same TD005-IU-006 Replay mechanism every ordinary candidate capture already uses, satisfying TD005-AI-018's own "at most once" bootstrap framing with no additional mechanism.
Traceability: TD005-SO-003; OQ-002; TD005-AI-018; TD005-CON-002.
Consequences: a governed revision (TD005-SO-003's own Revising state) uses the identical bootstrap procedure as initial establishment, never a partial patch to the existing record.

**TD005-ID-005. Controlled-Condition Enumeration Mechanism: Controlled-Condition Manifest.**
Decision: TD005-IU-006 accepts a Controlled-Condition Manifest concept with five explicitly named fields - input tick sequence, initial Position, lifecycle history, regime/strategy state, configuration - mirroring exactly the five controlled conditions TD005-SO-004's own Required behaviour already names.
Context: TD005-SO-004's own Section 18 deferral named "controlled-condition enumeration mechanism" as open.
Alternatives considered: (a) an implicit, ad hoc set of controlled conditions determined per invocation; (b) the chosen explicit, named five-field manifest.
Justification: TD005-SO-004's own Required behaviour already names exactly these five conditions as mandatory; formalizing them as explicit manifest fields, rather than leaving them implicit, is the minimal design step needed to make TD005-SI-005's own "complete controlled-condition specification" testable at Implementation time without inventing any new condition beyond what the Specification already names.
Traceability: TD005-SO-004; TD005-SI-005.
Consequences: a manifest missing any of the five fields is, by TD005-SO-004's own Failed-transition rule, an incomplete controlled-condition specification, triggering Executing -> Failed.

**TD005-ID-006. Execution-Environment Identity Remains Standalone.**
Decision: TD005-IU-007 remains a standalone Implementation Unit, not folded into TD005-IU-003 or TD005-IU-006.
Context: TD005-SO-005's own Section 18 deferral explicitly named this exact fold-in-or-standalone question, citing TD005-AD-004.
Alternatives considered: (a) fold into TD005-IU-006 (Replay); (b) fold into TD005-IU-003 (Reference Baseline); (c) the chosen standalone unit.
Justification: TD005-AD-004 (Architecture, already accepted) already states TD005-ARC-012 "is not folded into TD005-ARC-011, despite the CGA's own Section 10 noting Architecture 'may reasonably choose' to do so"; this Implementation Decision formally closes the loop the Specification's own Section 18 left open, reaffirming rather than reopening the Architecture's own stated preference, consistent with TD005-CAP-022's own cross-cutting relationship to both TD005-CAP-009 and TD005-CAP-011 (a relationship better served by a standalone unit than by folding into either one exclusively).
Traceability: TD005-SO-005; TD005-AD-004; TD005-CAP-022.
Consequences: TD005-IU-007 continues to expose its record to both TD005-IU-003 and TD005-IU-006 without either one owning it exclusively (TD005-SI-003's own ownership-decision-belongs-to-the-consumer framing, unchanged).

**TD005-ID-007. Trajectory Representation Concept: Ordered Tick-Indexed Snapshot Sequence.**
Decision: TD005-IU-011 represents a trajectory as an ordered, tick-indexed sequence of TD005-IU-009's own observed-state-snapshot records, ordered by the certified logical Stage Ordering (ADR-010), never by wall-clock timestamp.
Context: TD005-SO-010's own Section 18 deferral named "trajectory representation format" as open.
Alternatives considered: (a) an unordered set of snapshots requiring separate ordering metadata; (b) the chosen ordered, tick-indexed sequence.
Justification: TD005-SI-010 already requires evaluation "across the complete captured execution trajectory," and TD005-SO-010's own Forbidden behaviour already excludes wall-clock ordering; an ordered, tick-indexed sequence is the minimal structure satisfying both without introducing a concrete data structure or serialization format.
Traceability: TD005-SO-010; TD005-SI-010; ADR-010.
Consequences: no serialization format is chosen by this decision; only the logical ordering concept is fixed.

**TD005-ID-008. Tolerance-Comparison Policy Shape: Combined Relative-and-Absolute Bound.**
Decision: TD005-IU-012's own tolerance-bounded category uses a combined relative-and-absolute epsilon-bound policy shape (a value is within tolerance if it satisfies either an absolute bound or a relative bound, whichever is looser); the concrete epsilon constant(s) remain explicitly deferred to actual Implementation and empirical calibration.
Context: TD005-SO-011's own Section 18 deferral named "tolerance value(s) and comparison implementation" as open; TD005-SI-011 explicitly states the tolerance value "SHALL be documented at Implementation time, not chosen by this Specification."
Alternatives considered: (a) a purely relative-tolerance policy (fails near zero, where relative differences are numerically unstable); (b) a purely absolute-tolerance policy (fails for large-magnitude values, where absolute differences of the same practical significance vary in scale); (c) the chosen combined policy, standard practice for exactly this class of floating-point comparison problem.
Justification: choosing the policy SHAPE (not the literal constant) is a legitimate design-level decision distinct from the Specification's own explicit prohibition on choosing the constant itself; selecting the actual epsilon values would require empirical calibration against real trajectory data this design stage does not perform, and inventing an unsupported number here would violate this governance chain's own "do not invent requirements" discipline.
Traceability: TD005-SO-011; TD005-SI-011.
Consequences: TD005-IU-021's own registry retains "tolerance value(s)" as a still-open entry (Section 16), now narrowed from "value(s) and comparison implementation" to just the literal constant(s), since the comparison implementation's own policy shape is now fixed.

**TD005-ID-009. Classification Procedure Structure: Ordered Four-Step Decision Sequence.**
Decision: TD005-IU-014 applies an ordered, short-circuiting four-step decision sequence: (1) if any upstream unit failed to produce its required output, classify Invalid Comparison; (2) else, if the certification boundary or coverage context cannot confidently place the deviation, classify Indeterminate; (3) else, apply the formal equivalence definition (TD005-IU-010); (4) classify Regression if non-equivalent within the certified-contract boundary, else Non-Regression.
Context: TD005-SO-013's own Section 18 deferral named "concrete classification procedure (the algorithm composing TD005-SO-002 and TD005-SO-008/010/011/012 into one of four outcomes)" as open.
Alternatives considered: (a) evaluate all four outcome conditions independently and resolve conflicts after the fact; (b) the chosen ordered, short-circuiting sequence.
Justification: TD005-SD-001's own scientific justification for the four-outcome model already implies a priority order - failure conditions (Invalid Comparison) and boundary/coverage uncertainty (Indeterminate) must be checked before a Regression/Non-Regression determination is even attempted, since attempting equivalence evaluation on a failed or unbounded comparison would be scientifically meaningless; an ordered sequence is a direct, minimal formalization of that already-established priority, not a new scientific claim.
Traceability: TD005-SO-013; TD005-SD-001; TD005-AI-019.
Consequences: this ordering is itself now a design-level fact any future code-level implementation must preserve; TD005-IU-021's own registry narrows "concrete classification procedure" to just the per-step comparison logic (already resolved by TD005-IU-010 through TD005-IU-013's own realization).

**TD005-ID-010. Coverage Concept: Module, State-Transition, and Requirement-Citation Coverage.**
Decision: TD005-IU-018 adopts a three-part coverage concept - module coverage (every active module reached by at least one comparison), state-transition coverage (every ADR-009 lifecycle transition exercised at least once), and Functional-Requirement-citation coverage (every FR named in the Specification's own Section 19.1 exercised) - with no percentage-based aggregate metric computed.
Context: TD005-SO-015's own Section 18 deferral named "coverage mechanism and coverage-concept choice" as open.
Alternatives considered: (a) a single aggregate percentage metric; (b) a risk-based or path-based coverage model; (c) the chosen three-part, non-aggregated concept.
Justification: Specification Section 13 (Coverage Specification) already explicitly forbids "a concrete coverage-percentage calculation" and "a concrete coverage-reporting format" (TD005-AI-014's own advisory-only framing); the three-part concept directly mirrors the three concrete gap categories the Specification's own SO-014/SO-015 Postconditions already name (uncovered certified contract, uncovered Functional Requirement, uncovered active module/state transition), introducing no new coverage dimension beyond what is already evidenced.
Traceability: TD005-SO-015; Specification Section 13.
Consequences: TD005-IU-018's own report remains a gap list, never a single number, consistent with TD005-AI-014's advisory-only, non-gating role.

**TD005-ID-011. Evidence Record Field-Level Schema: Nine Named Fields (Eight Required, One Conditional).**
Decision: TD005-IU-015 realizes the evidence record as nine independently named fields - the eight TD005-SO-016 already requires (affected tick; affected stage or component; expected value; actual value; input provenance; initial-state provenance; certified-contract ID; execution-environment identity), plus a ninth, conditional field (reasoned unavailability marker) usable only in place of any of the first eight when the Specification's own V1.1 accommodation applies.
Context: TD005-SO-016's own Section 18 deferral named "adoption of the SDA's own four evidence-refinement elements into a binding schema... the schema's own field-level format remains open" as open.
Alternatives considered: (a) a single free-text evidence blob; (b) the chosen nine independently named fields.
Justification: TD005-SI-016 (as amended by the Specification's own V1.1 Editorial and Scientific Review) already names each of the eight elements individually and requires the ninth (marker) field to be reasoned and specific, not generic; naming them as independent fields, rather than a single blob, is the only design consistent with that requirement being independently checkable per element.
Traceability: TD005-SO-016; TD005-SI-016; TD005-II-014.
Consequences: no file format or serialization is chosen; only the field-level schema concept is fixed.

**TD005-ID-012. Evidence Persistence Design: Append-Only, Governed-Location, No Expiry Policy Yet.**
Decision: TD005-IU-016 persists every Composed evidence record as an append-only record within the governed location TD005-ID-014 designates; no in-place edit path exists at the design level; a retention/expiry policy is explicitly left undefined, since no accepted-baseline requirement currently mandates one.
Context: TD005-SO-017's own Section 18 deferral named "persistence format, retention/expiry policy, cross-stage continuity mechanism" as open.
Alternatives considered: (a) a mutable store permitting in-place correction; (b) the chosen append-only design with no expiry policy yet.
Justification: TD005-SI-017 already requires Composed records to be immutable, with a correction producing "a new, separate record, never an edit"; an append-only design is the direct, minimal structural consequence of that invariant. The append operation itself must be atomic (all-or-nothing), since a partially-written record would otherwise be neither cleanly Unpersisted nor validly Persisted, a state TD005-SO-017's own two-state boundary does not accommodate; this atomicity is a required property, not a chosen mechanism, and is formalized at TD005-IU-016's own Lifecycle and Failure behaviour fields (Section 7) without selecting the concrete atomic-write technique (for example, write-then-rename) that satisfies it. A fresh re-check of the FRA, SDA, CGA, and Architecture confirms none names a retention period or expiry trigger; inventing one here would violate this governance chain's own "do not invent requirements" discipline, so it remains an explicitly named, still-open Implementation-stage item.
Traceability: TD005-SO-017; TD005-SI-017.
Consequences: TD005-IU-021's own registry retains "retention/expiry policy" as a still-open entry (Section 16); "persistence format" and "cross-stage continuity mechanism" are narrowed by this decision's own append-only, governed-location, atomic-write framing but not fully resolved to a concrete file format or atomic-write technique.

**TD005-ID-013. Long-Duration-Validation Invocation Mechanics: Pre-Run Application, Budget Deferred.**
Decision: TD005-IU-019 applies the single invocation contract pre-run - before each of the six Long-Duration-Validation stages begins, never after - using the identical contract TD005-SI-019 requires; the concrete execution-time budget remains explicitly deferred to actual Implementation and empirical calibration.
Context: TD005-SO-018's own Section 18 deferral named "execution-time budget; pre-run-versus-post-run application mechanics" as open; OQ-004 (SDA/CGA/Architecture, all transferred unresolved) asks this exact question.
Alternatives considered: (a) post-run application (after each stage completes); (b) the chosen pre-run application; (c) leaving the choice itself open.
Justification: the Implementation Baseline's own "Regression Validation" purpose statement ("Verify that previously validated functionality remains correct") is naturally a gate before proceeding, not a retrospective check after a stage has already run for up to thirty days; applying it pre-run is the only choice consistent with the Implementation Baseline's own stated purpose without requiring an after-the-fact rollback concept the accepted baselines never describe. The execution-time budget itself is not chosen, since no accepted-baseline requirement names a number, and TD005-SI-019 already forbids a stage-specific variant that a "lightweight smoke-stage subset" would otherwise require.
Traceability: TD005-SO-018; TD005-SI-019; OQ-004; Implementation Baseline Section 6.5.
Consequences: TD005-IU-021's own registry narrows "execution-time budget; pre-run-versus-post-run application mechanics" to just the execution-time budget, since the pre-run-versus-post-run question is now resolved.

**TD005-ID-014. Regression-Capability Artifact Location: `tests/regression/`.**
Decision: TD-005's own regression-capability artifacts are designated to reside under `tests/regression/`, a new subdirectory of the already-existing, currently-empty `tests/` convention, distinct from the unrelated, already-present `tests/ssi/` structure.
Context: TD005-SO-021's own Section 18 deferral, and OQ-005 (test-code location), transferred unresolved through the SDA, CGA, Specification, and Specification's own Final QA Certification Review, all the way to this Implementation Specification.
Alternatives considered: (a) `tools/`, alongside `tools/repository_consolidation/` (a precedent for governance tooling, but semantically a different category - repository-structure verification, not runtime behavioural regression); (b) a wholly new top-level directory; (c) the chosen `tests/regression/` subdirectory.
Justification: `tests/` is independently re-confirmed (Section 5) to hold zero files relevant to `run_engine` today, and is not reachable from, and does not affect, `run_engine.main`'s own active import closure (re-verified, Section 5); placing TD-005's own artifacts here satisfies TD005-CON-003's Repository-Scope Compatibility requirement without disturbing the existing, unrelated `tests/ssi/` structure or any ARCHIVE/IGNORE-disposed location. This decision designates a location; it does not create any file or directory, consistent with this document's own repository-safety restriction.
Traceability: TD005-SO-021; TD005-CON-003; OQ-005; FRA Section 6.2.
Consequences: TD005-IU-021's own registry retains OQ-005 as fully closed (location named); TD005-II-018 formalizes this location as binding on any future Implementation Unit.

**TD005-ID-015. Scope-Drift-Sensitivity Mechanism: Fresh Static AST Re-Derivation Per Session.**
Decision: TD005-IU-022 re-derives the active/inactive module partition via a fresh, static, AST-based import-closure walk from `run_engine.main` at the start of every Replay Session and Observation act, never via a cached or hand-maintained list.
Context: TD005-SO-021's own Section 18 deferral named "scope-drift-sensitivity mechanism" as open; TD005-SI-020 requires re-evaluation, not an assumed-unchanged partition, at the start of every session.
Alternatives considered: (a) a hand-maintained, periodically-updated list; (b) a cached result refreshed on a time interval; (c) the chosen fresh, static, per-session re-derivation.
Justification: this exact static AST-based import-closure method is the one this entire governance chain has itself independently used, and independently re-verified, at every single stage (FRA, SDA, CGA, Architecture, Specification, and this document's own Section 5) with identical results every time; reusing the governance chain's own already-proven, already-repeatedly-validated method, rather than inventing a new one, is the most evidence-grounded choice available, and a static analysis carries no risk of itself executing or mutating active Run Engine state (TD005-II-008).
Traceability: TD005-SO-021; TD005-SI-020; TD005-II-008.
Consequences: no dynamic import probing, no runtime introspection of loaded modules, and no hand-maintained list is ever authoritative; the method is identical to, and reuses no new infrastructure beyond, what Section 5 of this and every prior TD-005 document already performs.

All fifteen Implementation Decisions are individually numbered with no gap; each is a genuine implementation-level design decision, none merely restates an existing Architecture Decision or Specification Decision.

## 14. Validation Readiness

What must be verified during actual Implementation (no test is created here; this is the verification checklist actual Implementation and Final Certification must satisfy):

- Every Implementation Unit's own Required/Forbidden behaviour (Section 7) is verifiable through direct inspection of the eventual code against this document's own text, with no code-level behaviour absent from, or contradicting, its own owning unit's design.
- The Orchestration Unit's own call order (Section 8, Section 9) is independently reproducible via a fresh trace of actual invocation order at Implementation time, matching the certified sequence exactly.
- TD005-IU-009's own non-interference property (TD005-SI-007) is independently verifiable via a comparison of an observed run against an unobserved run under identical controlled conditions, confirming zero measurable behavioural difference.
- TD005-IU-012's own tolerance policy shape (TD005-ID-008) is independently verifiable via inspection of the eventual code's own comparison logic, confirming the combined relative-and-absolute structure is present, before any specific epsilon constant is calibrated.
- TD005-IU-014's own four-outcome exhaustiveness (TD005-SI-013) is independently verifiable via a fresh enumeration of every code path reaching a classification, confirming each reaches exactly one of the four outcomes with no fifth, implicit path.
- TD005-IU-015's own reasoned-unavailability-marker mechanism (TD005-II-014) is independently verifiable via inspection of every code path that could produce an Indeterminate or Invalid Comparison outcome, confirming each names the specific upstream condition rather than a generic placeholder.
- TD005-IU-021's own registry (Section 16) is independently verifiable as accurately reflecting every still-open item this document itself names, with no silent gap between this document's own Section 16 and the eventual code's own remaining open choices.
- TD005-IU-022's own re-derivation method (TD005-ID-015) is independently verifiable via a fresh, static re-run of the same AST-based import-closure method this document's own Section 5 performs, confirming identical results to the eventual code's own runtime scope-check output.
- Every Implementation Unit's own Traceability field (Section 7) remains individually citable, with zero compressed-range citations substituting for individual traceability, consistent with this governance chain's own recurring discipline.

No pytest, unittest, fixture, or CI/CD configuration is created or named as a specific tool by this section; "verifiable" above names a property to confirm, not a testing mechanism to build.

## 15. Traceability

### 15.1 Specification Object to Implementation Unit Traceability

| Specification Object | Governing Implementation Unit |
|---|---|
| TD005-SO-001 | TD005-IU-001 |
| TD005-SO-002 | TD005-IU-002 |
| TD005-SO-003 | TD005-IU-003 |
| TD005-SO-004 | TD005-IU-006 |
| TD005-SO-005 | TD005-IU-007 |
| TD005-SO-006 | TD005-IU-008 |
| TD005-SO-007 | TD005-IU-009 |
| TD005-SO-008 | TD005-IU-010 |
| TD005-SO-009 | TD005-IU-004 |
| TD005-SO-010 | TD005-IU-011 |
| TD005-SO-011 | TD005-IU-012 |
| TD005-SO-012 | TD005-IU-013 |
| TD005-SO-013 | TD005-IU-014 |
| TD005-SO-014 | TD005-IU-017 |
| TD005-SO-015 | TD005-IU-018 |
| TD005-SO-016 | TD005-IU-015 |
| TD005-SO-017 | TD005-IU-016 |
| TD005-SO-018 | TD005-IU-019 |
| TD005-SO-019 | TD005-IU-020 |
| TD005-SO-020 | TD005-IU-021 |
| TD005-SO-021 | TD005-IU-022 |
| TD005-SO-022 | TD005-IU-023 |

All twenty-two Specification Objects individually trace to exactly one Implementation Unit; TD005-IU-005 is the sole aggregate-traceability unit, traced instead to Architecture Section 11 and TD005-AI-013 (Section 7, Section 13, TD005-ID-001).

### 15.2 Specification Invariant to Implementation Unit Traceability

| Specification Invariant | Governing Implementation Unit(s) |
|---|---|
| TD005-SI-001 | all Implementation Units (document-wide principle) |
| TD005-SI-002 | TD005-IU-001 |
| TD005-SI-003 | TD005-IU-003 |
| TD005-SI-004 | TD005-IU-003, TD005-IU-006 |
| TD005-SI-005 | TD005-IU-006 |
| TD005-SI-006 | TD005-IU-006 |
| TD005-SI-007 | TD005-IU-009 |
| TD005-SI-008 | TD005-IU-008 |
| TD005-SI-009 | TD005-IU-010 |
| TD005-SI-010 | TD005-IU-011 |
| TD005-SI-011 | TD005-IU-012 |
| TD005-SI-012 | TD005-IU-013 |
| TD005-SI-013 | TD005-IU-014 |
| TD005-SI-014 | TD005-IU-014 |
| TD005-SI-015 | TD005-IU-017, TD005-IU-018 |
| TD005-SI-016 | TD005-IU-015 |
| TD005-SI-017 | TD005-IU-015, TD005-IU-016 |
| TD005-SI-018 | TD005-IU-016 |
| TD005-SI-019 | TD005-IU-019 |
| TD005-SI-020 | TD005-IU-022 |
| TD005-SI-021 | TD005-IU-023 |
| TD005-SI-022 | TD005-IU-021 |

All twenty-two Specification Invariants individually trace to at least one Implementation Unit.

### 15.3 Specification Decision to Implementation Unit Traceability

| Specification Decision | Governing Implementation Unit(s) |
|---|---|
| TD005-SD-001 | TD005-IU-014 |
| TD005-SD-002 | TD005-IU-022, TD005-IU-023 |
| TD005-SD-003 | TD005-IU-006, TD005-IU-007, TD005-IU-009 |
| TD005-SD-004 | TD005-IU-015 |

All four Specification Decisions individually trace to at least one Implementation Unit.

### 15.4 Architecture Component to Implementation Unit Traceability

Composed directly from the Specification's own Section 17 (Architecture Component to Specification Object) with Section 15.1 above; reproduced individually so every Architecture Component is directly, individually traceable within this document itself.

| Architecture Component | Governing Implementation Unit |
|---|---|
| TD005-ARC-001 | TD005-IU-001 |
| TD005-ARC-002 | TD005-IU-002 |
| TD005-ARC-003 | TD005-IU-003 |
| TD005-ARC-004 | TD005-IU-008 |
| TD005-ARC-005 | TD005-IU-009 |
| TD005-ARC-006 | TD005-IU-010 |
| TD005-ARC-007 | TD005-IU-011 |
| TD005-ARC-008 | TD005-IU-012 |
| TD005-ARC-009 | TD005-IU-013 |
| TD005-ARC-010 | TD005-IU-004 |
| TD005-ARC-011 | TD005-IU-006 |
| TD005-ARC-012 | TD005-IU-007 |
| TD005-ARC-013 | TD005-IU-015 |
| TD005-ARC-014 | TD005-IU-016 |
| TD005-ARC-015 | TD005-IU-017 |
| TD005-ARC-016 | TD005-IU-018 |
| TD005-ARC-017 | TD005-IU-014 |
| TD005-ARC-018 | TD005-IU-019 |
| TD005-ARC-019 | TD005-IU-020 |
| TD005-ARC-020 | TD005-IU-022 |
| TD005-ARC-021 | TD005-IU-023 |
| TD005-ARC-022 | TD005-IU-021 |

All twenty-two Architecture Components individually trace to exactly one Implementation Unit. No gap exists at any level - Specification Object, Specification Invariant, Specification Decision, or Architecture Component.

## 16. Implementation Readiness

Assessed against the Architecture's own ten-layer structure: an Implementation Unit realizing a higher-layer component requires every unit realizing a lower-layer component it depends on to exist first.

| Implementation Unit | Readiness | Prerequisite (if any) | Remaining Open Mechanism |
|---|---|---|---|
| TD005-IU-001 | Ready | none (foundational) | none (TD005-ID-002 resolves) |
| TD005-IU-002 | Requires prerequisite | TD005-IU-001 (consumes its enumeration) | none (TD005-ID-003 resolves) |
| TD005-IU-003 | Requires prerequisite | TD005-IU-001, TD005-IU-002, TD005-IU-006, TD005-IU-007 (bootstrap capture) | source-selection procedural detail already resolved (TD005-ID-004); no remaining mechanism |
| TD005-IU-004 | Ready | none (foundational) | none |
| TD005-IU-005 | Requires prerequisite | every unit it actually sequences (TD005-IU-006 through TD005-IU-018, individually), plus the three preconditions confirmed before sequencing begins (TD005-IU-001, TD005-IU-003, TD005-IU-022, Section 7) | none (sequencing itself resolved, TD005-ID-001) |
| TD005-IU-006 | Ready | none (foundational realization; TD005-IU-007 is a peer, not a blocking prerequisite) | Controlled-Condition Manifest field-level format (named, not code-level) |
| TD005-IU-007 | Ready | none (foundational) | interpreter/library identity representation format |
| TD005-IU-008 | Requires prerequisite | TD005-IU-009 (consumes observed snapshots) | none |
| TD005-IU-009 | Ready | none (foundational realization; consumes TD005-IU-006's output but is itself the next-layer unit) | none |
| TD005-IU-010 | Requires prerequisite | TD005-IU-008, TD005-IU-011, TD005-IU-012, TD005-IU-013 | none (composition already fully specified) |
| TD005-IU-011 | Requires prerequisite | TD005-IU-008, TD005-IU-009 | trajectory representation format (named, not code-level, TD005-ID-007) |
| TD005-IU-012 | Requires prerequisite | TD005-IU-008 | concrete tolerance epsilon constant(s) (explicitly deferred, TD005-ID-008) |
| TD005-IU-013 | Requires prerequisite | TD005-IU-008 | none |
| TD005-IU-014 | Requires prerequisite | TD005-IU-002, TD005-IU-006, TD005-IU-009, TD005-IU-010, TD005-IU-011, TD005-IU-012, TD005-IU-013 | none (procedure resolved, TD005-ID-009) |
| TD005-IU-015 | Requires prerequisite | TD005-IU-002, TD005-IU-006, TD005-IU-007, TD005-IU-014 | none (schema resolved, TD005-ID-011) |
| TD005-IU-016 | Requires prerequisite | TD005-IU-015 | persistence file format; retention/expiry policy (explicitly deferred, TD005-ID-012) |
| TD005-IU-017 | Requires prerequisite | TD005-IU-001 | none |
| TD005-IU-018 | Requires prerequisite | TD005-IU-022 | none (concept resolved, TD005-ID-010) |
| TD005-IU-019 | Requires prerequisite | TD005-IU-005, TD005-IU-016 | execution-time budget (explicitly deferred, TD005-ID-013) |
| TD005-IU-020 | Ready | none (static marker) | none |
| TD005-IU-021 | Requires prerequisite | every other Implementation Unit (aggregates their own remaining open items) | none (its own structure is fully specified) |
| TD005-IU-022 | Ready | none (foundational; re-evaluated per session, not build-ordered) | none (method resolved, TD005-ID-015) |
| TD005-IU-023 | Ready | none (static marker) | none |

Eight Implementation Units (TD005-IU-001, TD005-IU-004, TD005-IU-006, TD005-IU-007, TD005-IU-009, TD005-IU-020, TD005-IU-022, TD005-IU-023) require no prerequisite unit and no remaining design-level mechanism choice beyond a still-open code-level representation format explicitly named as such. Fifteen units require one or more prerequisite units to exist first, consistent with the Architecture's own layered dependency structure; every prerequisite is justified by the specific output the dependent unit consumes (Section 7's own Dependencies field for each unit). Five remaining open items (Controlled-Condition Manifest field-level format, identity representation format, trajectory representation format, tolerance epsilon constant(s), persistence file format and retention/expiry policy, execution-time budget) are explicitly named, registry-tracked (TD005-IU-021, Section 7), and correctly left to actual Implementation and, where applicable, empirical calibration - none is silently invented by this document.

## 17. Completion Criteria

This Implementation Specification is complete and ready to serve as the accepted Working Baseline for Implementation when:

- Every Implementation Unit is derived exclusively from the accepted Specification, Architecture, CGA, SDA, and FRA, with the single aggregate exception (TD005-IU-005) explicitly justified: verified by construction (Section 7, every unit's own Traceability field).
- Every unit carries all eleven required fields (Purpose, Responsibility, Inputs, Outputs, Dependencies, Internal state, Required interactions, Forbidden interactions, Lifecycle, Failure behaviour, Traceability): verified by construction (Section 7).
- Every unit realizes exactly one primary Specification responsibility, except the single justified aggregate: verified by construction (twenty-two 1:1 mappings plus one aggregate, Section 15.1).
- The eleven named implementation domains are represented, refined where evidence justified it: verified by construction (Section 7, Domains A through K represented, plus the independently-justified Domain L, mirroring TD005-SD-002's own precedent).
- Runtime lifecycle, component interaction, and failure model are each fully specified without code: verified (Section 8, Section 9, Section 10).
- Extension model covers lifecycle, registration, isolation, compatibility, and governance: verified (Section 11).
- Implementation Invariants are individually numbered, normative, and each traced to an accepted-baseline source: verified (Section 12, eighteen invariants).
- Implementation Decisions are genuine implementation-level decisions, not repeated Architecture or Specification Decisions: verified (Section 13, fifteen decisions, each with a distinct Context/Alternatives/Justification not present in any prior Architecture or Specification Decision).
- Validation readiness names what must be verified without creating a test: verified (Section 14).
- Every Specification Object, Specification Invariant, Specification Decision, and Architecture Component traces to an Implementation Unit, with no gap: verified (Section 15).
- Every Implementation Unit's own readiness is determined, with prerequisites and remaining open mechanisms named explicitly: verified (Section 16).
- No Python code, pytest code, CI/CD configuration, GitHub workflow, API signature, or concrete algorithm implementation is created anywhere in this document: verified by construction (Section 7 through Section 16 contain no such content).

All criteria above are satisfied by this document.

## 18. Conclusion

This Implementation Specification defines twenty-three individually numbered Implementation Units (TD005-IU-001 through TD005-IU-023) - twenty-two realizing the accepted Specification's own twenty-two Specification Objects one-to-one, plus one new, explicitly justified aggregate Orchestration Unit closing the call-order-sequencing gap the Architecture's own Component Interaction section left open - across twelve implementation domains. Eighteen Implementation Invariants and fifteen genuine Implementation Decisions formalize the runtime lifecycle, component interaction, failure model, and extension model this document establishes, each individually traceable to the accepted FRA, SDA, CGA, Architecture, or Specification. Fifteen of the Specification's own thirteen-item Section 18 mechanism deferrals are resolved at the design level by this document's own Implementation Decisions (several Specification Objects carrying more than one deferred item, and this document's own decisions additionally resolving OQ-004 and OQ-005 at the design level); the remainder - principally concrete numeric constants requiring empirical calibration (a tolerance epsilon, an execution-time budget) and code-level representation formats - are explicitly, individually named as still open in Section 16 and registry-tracked by TD005-IU-021, never silently invented. Every Specification Object, Specification Invariant, Specification Decision, and Architecture Component traces to an Implementation Unit with no gap (Section 15). This document selects no test framework, no concrete file format beyond the design-level concepts it names, no API signature, and no algorithm implementation; it is the final engineering design before actual Implementation begins. This document is ready to serve as the accepted Working Baseline for a future TD-005 Implementation.
