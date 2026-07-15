Document Class:
Architecture Analysis

Document ID:
TD005-ARCH

Title:
TD-005 Automated Regression Test Suite - Architecture Analysis / Architecture Design

Version:
V1.1

Date:
2026-07-14

Status:
DRAFT - EDITORIAL AND SCIENTIFIC REVIEW COMPLETED

Storage Location:
docs/architecture/design/

Filename:
TD_005_AUTOMATED_REGRESSION_TEST_SUITE_ARCHITECTURE_V1_2026-07-14.md

Technical Debt Item:
TD-005 - Automated Regression Test Suite (docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md)

Accepted Working Baselines:
docs/architecture/analysis/TD_005_AUTOMATED_REGRESSION_TEST_SUITE_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-14.md, Version V1.1, Status DRAFT - EDITORIAL AND SCIENTIFIC REVIEW COMPLETED
docs/architecture/analysis/TD_005_AUTOMATED_REGRESSION_TEST_SUITE_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-14.md, Version V1.1, Status DRAFT - CORRECTIVE SCIENTIFIC REVIEW COMPLETED
docs/architecture/analysis/TD_005_AUTOMATED_REGRESSION_TEST_SUITE_CAPABILITY_GAP_ANALYSIS_V1_2026-07-14.md, Version V1.1, Status DRAFT - EDITORIAL AND SCIENTIFIC REVIEW COMPLETED

Scope:
Architecture analysis and design only. No implementation, test scripts, pytest code, fixtures, CI/CD, directory implementation, concrete algorithms, or configuration files.

Dependencies:
- docs/architecture/analysis/TD_005_AUTOMATED_REGRESSION_TEST_SUITE_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-14.md
- docs/architecture/analysis/TD_005_AUTOMATED_REGRESSION_TEST_SUITE_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-14.md
- docs/architecture/analysis/TD_005_AUTOMATED_REGRESSION_TEST_SUITE_CAPABILITY_GAP_ANALYSIS_V1_2026-07-14.md
- docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md
- docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md
- docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md
- docs/architecture/REPOSITORY_CONSOLIDATION_ARCHITECTURE_V1_2026-07-14.md
- docs/architecture/REPOSITORY_CONSOLIDATION_SPECIFICATION_V1_2026-07-14.md
- docs/architecture/certification/REPOSITORY_CONSOLIDATION_FINAL_CERTIFICATION_V1_2026-07-14.md
- requirements.txt

Referenced By:
- future TD-005 Specification (not yet created)

Supersedes:
None. This is the first Architecture Analysis for TD-005.

Language:
English

Encoding:
ASCII

---

# TD-005 Automated Regression Test Suite - Architecture Analysis / Architecture Design

## 1. Metadata

See front matter above.

### 1.1 Revision History

- **V1.0 (2026-07-14).** Initial Architecture Analysis. Twenty-two components, ten layers, seventeen invariants, thirteen decisions. TD005-ARC-011's own External dependencies field incorrectly listed TD005-ARC-005 (Layer 4) as a dependency of a Layer 3 component, contradicting the document's own Layer ordering and its own closing acyclicity claim. TD005-ARC-003's own genuine, necessary one-time bootstrap dependency on TD005-ARC-011/012 (Layer 3) was left unexplained against that same closing acyclicity claim. Several components' own Owned Information fields were incomplete or inconsistent with their own Outputs fields (TD005-ARC-003, TD005-ARC-011, TD005-ARC-013, TD005-ARC-019, TD005-ARC-021). No invariant addressed component-failure propagation.
- **V1.1 (2026-07-14).** Editorial and Scientific Review. (1) Corrected TD005-ARC-011's own External dependencies field: removed the erroneous TD005-ARC-005 dependency - Replay drives execution and does not need to read state to do so; Observation instead reads FROM Replay's own output, per Section 9, Section 10, and Section 11's own already-consistent interaction description - a genuine Layer 3 -> Layer 4 forward-reference violation, now resolved. (2) Corrected Section 9's Layer 2 and Layer 3 descriptions and its own closing acyclicity sentence to explicitly acknowledge and justify TD005-ARC-003's own one-time reference-capture bootstrap dependency on TD005-ARC-011/012, rather than asserting a blanket claim the document's own Section 8 and Section 11 already contradicted; added TD005-AI-018 (Reference-Capture Bootstrap Invariant) to formalize this as a one-time, non-recurring exception, not a per-comparison cycle. (3) Added TD005-AI-019 (Component-Failure Non-Classification Invariant), grounded by analogy in the certified corpus's own ADR-011 (Runtime Failure Handling) pattern, closing a genuine hidden-assumption gap this review's own Hidden Architecture Assumption Review identified (component-failure propagation and isolation were previously unaddressed). (4) Widened TD005-ARC-011's own Owned Information field to include the captured execution trajectory; TD005-ARC-013's to include composed evidence-record instances, not only the schema; TD005-ARC-003's own provenance metadata to explicitly include Run Engine code-version identity at capture time; TD005-ARC-019's and TD005-ARC-021's own Owned Information fields reworded from bare "none" to explicitly name the metadata-only record each produces, for consistency with their own Outputs fields. (5) Added an explicit documentation-time-only clarification to TD005-ARC-022's own Architectural constraints, to preempt a hidden-runtime-coupling misreading of its own maximal external-dependency fan-in. (6) Corrected Section 9's Layer 6 (Coverage) description, which previously stated both TD005-ARC-015 and TD005-ARC-016 "Depend on Foundational and Comparison components" - a description matching TD005-ARC-016 but not TD005-ARC-015, whose own sole dependency is TD005-ARC-001 (Foundational only). (7) Added one named Specification Input (pipeline initialization and shutdown lifecycle) and widened TD005-ARC-014's own existing Specification Input bullet to explicitly include retention/expiry policy, both surfaced by this review's own Hidden Architecture Assumption Review and confirmed unsupported by any accepted FRA requirement, SDA dependency, or CGA capability - recorded as named gaps rather than silently left implicit, consistent with TD005-AI-016. No component, layer, Architecture Decision, capability mapping, or traceability table was added, removed, renamed, or renumbered; the component count (22), layer count (10), and Architecture Decision count (13) are unchanged; the invariant count increased from seventeen to nineteen (TD005-AI-018, TD005-AI-019 added).

## 2. Executive Summary

This Architecture Analysis defines the architecture required to close every capability gap identified by the accepted TD-005 Capability Gap Analysis (CGA, V1.1), grounded in the accepted Functional Requirement Analysis (FRA, V1.1) and Scientific Dependency Analysis (SDA, V1.1). Twenty-two individually numbered architectural components (TD005-ARC-001 through TD005-ARC-022) are derived, one for each of the twenty-two accepted capabilities plus one additional component (TD005-ARC-022) that formalizes the recurring "deferred to Specification" pattern the CGA itself names across twelve capabilities into an explicit Extension architecture, rather than leaving it implicit. The components are organized into ten architectural layers - an evidence-driven extension of the seven-layer skeleton the governing task names (Foundational, Reference, Observation, Comparison, Classification, Evidence, Governance), with three additional layers (Replay, Coverage, Extension) introduced because the governing task's own required domains (Replay Control Architecture, Coverage Architecture, Architecture Extension Points) have no coherent home in the seven-layer skeleton and each is independently justified from repository evidence (Section 9, Architecture Decision TD005-AD-010). Nineteen Architecture Invariants (TD005-AI-001 through TD005-AI-019) and thirteen Architecture Decisions (TD005-AD-001 through TD005-AD-013) are derived, each individually traceable to specific FRA requirements, SDA dependencies, or CGA capabilities. Every one of the twenty-two accepted capabilities maps to at least one architectural component; no orphan capability exists (Section 16). This document selects no test framework, comparison algorithm, storage mechanism, persistence implementation, or concrete configuration; every such choice is explicitly named and handed to a future Specification stage (Section 17). A subsequent Editorial and Scientific Review (V1.1) independently rebuilt the component-dependency graph and found, and corrected, two genuine Layer-ordering inconsistencies (TD005-ARC-011, TD005-ARC-003), added two invariants closing a reference-bootstrap ambiguity and a component-failure-propagation gap, and tightened several components' own ownership fields, without changing the component count, layer count, Architecture Decision count, or any capability mapping.

## 3. Accepted Inputs

Read in full and treated as binding, unmodified inputs:

- **FRA V1.1** (DRAFT - EDITORIAL AND SCIENTIFIC REVIEW COMPLETED): twenty-two Functional Requirements (TD005-FR-001 through TD005-FR-022), four Constraints (TD005-CON-001 through TD005-CON-004), two Deferred Specification and Coverage Obligations (Section 13.1, Section 13.2), six Open Questions (OQ-001 through OQ-006).
- **SDA V1.1** (DRAFT - CORRECTIVE SCIENTIFIC REVIEW COMPLETED): thirty-three Scientific Dependencies (TD005-DEP-001 through TD005-DEP-033).
- **CGA V1.1** (DRAFT - EDITORIAL AND SCIENTIFIC REVIEW COMPLETED): twenty-two Capabilities (TD005-CAP-001 through TD005-CAP-022) across ten capability classes, a capability dependency graph (5 Foundational, 9 Intermediate, 8 Derived), a maturity distribution (3 AVAILABLE, 7 PARTIALLY AVAILABLE, 11 MISSING, 1 OUTSIDE TD-005 SCOPE), a risk distribution (1 Low, 8 Medium, 6 High, 3 Critical), Architecture Readiness (14 Mandatory, 4 Optional, 4 Deferred), and Specification Readiness (twelve named deferred mechanism decisions).

No FRA requirement, SDA dependency, or CGA capability, status, or traceability is altered, reinterpreted, merged, removed, or added by this document. This Architecture translates the accepted CGA's capability-level gaps into architecture-level components, layers, invariants, and decisions; it does not re-derive the capabilities themselves.

## 4. Objective

To produce the complete Architecture Analysis / Architecture Design for TD-005, closing every accepted capability gap named by the CGA without introducing architecture unjustified by the accepted baselines. Every architectural component traces to one or more FRA Functional Requirements, one or more SDA Dependencies, and one or more CGA Capabilities. This document defines architecture only: components, responsibilities, interfaces (logical, not API-level), information flow, ownership boundaries, lifecycle, dependencies, and invariants. It does not create implementation, test scripts, pytest code, fixtures, CI/CD configuration, directory implementation, concrete algorithms, or configuration files.

## 5. Repository Evidence

Independently re-verified immediately before drafting this document, not assumed from the FRA, SDA, CGA, or any prior analysis:

1. **Branch and HEAD.** Branch `run-engine-consolidation-safety`; HEAD `8952b1cba42506e4126e57ee89c59934f3d48b71`. `git status --short` shows exactly three entries: the pre-existing, unrelated modification to `docs/capabilities/SGF_013_SCIENTIFIC_BEHAVIOUR_REPRESENTATION_2026-06-26.md`, and the three untracked accepted TD-005 Working Baselines (FRA, SDA, CGA). No other local change exists.
2. **Active Run Engine module set.** A freshly, independently authored AST-based import closure from `run_engine.main` reproduces exactly: 18 total `.py` files under `run_engine/`, 14 active (`run_engine/main.py`, `run_engine/core/loop.py`, `run_engine/core/state.py`, `run_engine/core/regime.py`, `run_engine/core/strategy.py`, `run_engine/core/position.py`, `run_engine/core/risk.py`, `run_engine/core/execution/__init__.py`, `run_engine/core/execution/executor.py`, `run_engine/core/performance.py`, `run_engine/core/pnl.py`, `run_engine/core/trade_lifecycle.py`, `run_engine/core/canonical_state.py`, `run_engine/core/canonical_enforcer.py`), 4 inactive RETAIN-Deferred-Scope (`run_engine/core/config.py`, `run_engine/runtime/recovery.py`, `run_engine/runtime/snapshot.py`, `run_engine/runtime/state_memory.py`). Identical to every prior independent derivation across the FRA, the SDA, the CGA, and the Repository Consolidation governance chain.
3. **Architecture Baseline and Implementation Baseline.** Re-opened; the Architecture Baseline's own Ownership Terminology, ADR-001 through ADR-012, and AC-001 through AC-015 remain the authoritative source this Architecture's own Reference and Comparison layers depend on (Section 8). The Implementation Baseline's own four-layer Validation Strategy (Static, Architectural, Runtime, Regression) and Long-Duration-Validation six-stage sequence (Functional smoke, 1-hour, 6-hour, 24-hour, 7-day, 30-day) remain the authoritative source this Architecture's own Governance layer depends on.
4. **Technical Debt Register.** Re-confirmed: TD-004 `Closed (certified by P3-03 Final Certification)`; TD-005 `Open`; TD-007 `Deferred`. This Architecture's own scope is exactly TD-005's own Register description ("Create an automated regression test suite for run_engine/core") and does not reopen TD-001, TD-002, TD-003, TD-006, or TD-007.
5. **Repository Consolidation Architecture, Specification, and Final Certification.** Re-confirmed present and CERTIFIED. RC-AD-004 (Executor path-collision resolution), RC-AI-004/RC-AI-005 (no archive/scratch import), and RC-SPEC-001 (Active Runtime Retention Contract, an absolute no-change boundary on the same fourteen active files) are directly load-bearing for this Architecture's own AI-011, AI-012, and AD-013 (Section 12, Section 13).
6. **`requirements.txt`, `tests/`, `tools/`.** Re-confirmed unchanged: no test framework in `requirements.txt`; zero files under `tests/` (only the empty, untracked `tests/ssi/` structure); `tools/repository_consolidation/verify_repository_consolidation.py` remains structure-only and is not a reusable component for this Architecture.
7. **No conflicting `docs/architecture/design/` content.** The directory did not exist prior to this document; this is the first file placed there. The repository's own established convention places earlier Architecture/Specification pairs (P2-02A through Repository Consolidation) directly under `docs/architecture/`, not in a `design/` subdirectory; this Architecture is placed at the exact path the governing task specifies, a deliberate, explicitly-authorized departure from that convention for this governance unit, not an inconsistency this document silently introduces.

No CGA statement is carried over unverified; every fact this Architecture's own components, invariants, and decisions rely on was independently re-confirmed above or is explicitly cited to its own accepted-baseline source (Sections 8, 12, 13).

## 6. Architecture Methodology

This Architecture answers, for every accepted capability gap: what components must exist; what responsibilities belong to each; what interfaces (logical) exist between them; what information flows between them; what ownership boundaries apply to each piece of information; what lifecycle each component's own owned information follows; what dependencies exist between components; and what invariants must always hold. The method applied: (1) take the CGA's own twenty-two capabilities as the complete, closed input set - no capability is re-derived, added, or removed; (2) for every capability, derive exactly one architectural component with one primary responsibility, merging only where two capabilities produce architecturally identical footprint (Section 13, TD005-AD-003) and splitting never, since the CGA's own Section 7.1 atomicity audit already confirmed every capability is atomic; (3) add exactly one component (TD005-ARC-022) not sourced from a single capability but from the aggregate "Required before: Specification" pattern the CGA names across twelve capabilities (CGA Section 11), since leaving this pattern architecturally implicit would violate the governing task's own Architecture Extension Points domain requirement; (4) assign every component to a layer using a structural criterion (Section 9), independent of the component's own current maturity; (5) derive information flow and ownership from the components' own Owned Information fields, not invented separately; (6) derive invariants from the FRA's own Constraints, the SDA's own risk findings, and the CGA's own explicit exclusions, never from architectural convenience; (7) derive every Architecture Decision from a genuine alternative this Architecture considered and rejected, with an explicit scientific justification; (8) verify, mechanically, that every capability maps to at least one component, with no orphan (Section 16); (9) select no implementation, test framework, comparison algorithm, storage mechanism, or configuration at any step.

## 7. Architectural Principles

- **Traceability-first.** No architectural component exists solely because it appears convenient. Every component traces to one or more FRA requirements, one or more SDA dependencies, and one or more CGA capabilities (Section 15). This is itself formalized as TD005-AI-013.
- **One primary responsibility per component.** Every component has exactly one primary responsibility, stated in its own Purpose field; where two capabilities would otherwise produce two components with overlapping responsibility, they are merged only when architecturally indistinguishable (TD005-AD-003), never merely for document brevity.
- **No implementation leakage.** No component's own description selects a test framework, comparison algorithm, storage technology, persistence mechanism, or configuration format. Every such choice is named explicitly as a Specification input (Section 17) and enforced by TD005-AI-017.
- **No new runtime coupling.** No component modifies, wraps, instruments, or subclasses any of the fourteen active Run Engine modules; all observation occurs through one explicitly non-interfering gateway (TD005-ARC-005, TD005-AI-002, TD005-AD-013).
- **Boundary preservation.** Where a capability is explicitly OUTSIDE TD-005 SCOPE (TD005-CAP-018) or governed by a separate, already-certified unit (Repository Consolidation), this Architecture represents that boundary explicitly rather than silently omitting it (TD005-ARC-021, TD005-AI-012, TD005-AD-009).
- **Conservative layering.** A component's layer reflects its own structural prerequisite position (what it presupposes, what presupposes it), not its current maturity, its scientific importance, or its risk rating - the same discipline the CGA itself established for capability-layer placement (TD005-AD-010).
- **No premature resolution.** Where the CGA left a capability's own exact mechanism to Specification, this Architecture defines the component's contract (inputs, outputs, owned information, constraints) without choosing the mechanism, and records the deferral explicitly (TD005-ARC-022).

## 8. Architecture Components

Twenty-two individually numbered components. Each states: ID, Name, Purpose, Responsibilities, Inputs, Outputs, Owned information, External dependencies, Architectural constraints, Scientific justification, Source capabilities, Source dependencies, Source requirements.

### Domain A - Reference Contract Architecture

**TD005-ARC-001. Certified Contract Registry.**
Purpose: expose the certified-contract corpus as a single, enumerable, authoritative reference.
Responsibilities: identify the authoritative behavioural contract set across the Architecture Baseline, the Implementation Baseline, and the six certified units; enumerate that set reproducibly; determine membership and exclusion for any candidate contract, including open Technical Debt Register entries; detect drift or ambiguity as future units are certified.
Inputs: the Architecture Baseline, the Implementation Baseline, the six certified units' own Final Certifications, the Technical Debt Register.
Outputs: an enumerable certified-contract set, consumable by every downstream component that needs to know "what is certified."
Owned information: the certified-contract corpus enumeration; the Technical-Debt-Register-scope position (whether a given TD entry is corpus-member or tracked exception).
External dependencies: read-only access to the Architecture Baseline, Implementation Baseline, six certified units, and Technical Debt Register; no write access to any of them.
Architectural constraints: TD005-AI-001, TD005-AI-013; does not itself decide the certification-status boundary (TD005-ARC-002's own responsibility).
Scientific justification: a regression capability cannot determine deviation from "certified behaviour" without a single, enumerable representation of that behaviour (CGA Section 7, TD005-CAP-001).
Source capabilities: TD005-CAP-001.
Source dependencies: TD005-DEP-001, TD005-DEP-003.
Source requirements: TD005-FR-001 through TD005-FR-022 (all); TD005-CON-001 through TD005-CON-004.

**TD005-ARC-002. Certification Boundary Authority.**
Purpose: determine unambiguously whether a given behavioural contract counts as "certified."
Responsibilities: state which evidentiary forms (source code alone, certification narrative prose, Architecture/Specification text, Implementation Baseline general methodology) qualify as certified; apply this rule consistently whenever the Certified Contract Registry or the Regression Classification Engine needs a certification-status determination.
Inputs: a candidate contract or behavioural claim; the Certified Contract Registry's own enumeration.
Outputs: a certification-status determination (certified / not certified) for any candidate.
Owned information: the certification-status boundary rule itself.
External dependencies: TD005-ARC-001 (consumes the Registry's own enumeration as the candidate space this rule is applied over).
Architectural constraints: TD005-AI-001, TD005-AI-008; the boundary rule itself, once set, must not be silently reinterpreted by any downstream component.
Scientific justification: without this boundary, incidental source-code behaviour could be silently treated as certified, or genuine certified behaviour silently excluded (CGA Section 7, TD005-CAP-002).
Source capabilities: TD005-CAP-002.
Source dependencies: TD005-DEP-002.
Source requirements: TD005-FR-021, TD005-FR-018, TD005-FR-020.

**TD005-ARC-003. Reference Baseline Authority.**
Purpose: establish a scientifically valid, immutable-or-governed, reproducible provenance for "previously-certified behaviour" against which future runs are compared.
Responsibilities: select the reference source (historical Implementation/Certification commit, or a baseline freshly established at TD-005 Implementation time); govern any change to the reference (immutability, or an explicit, recorded revision); guarantee the reference is reproducible from the certified corpus, not an opaque frozen artifact.
Inputs: the Certified Contract Registry's own enumeration; the Certification Boundary Authority's own boundary rule; a candidate execution trajectory captured under the Deterministic Replay Controller.
Outputs: one authoritative reference-baseline record, consumable by the Regression Classification Engine.
Owned information: the reference-baseline record itself; its own provenance metadata (source, capture conditions, governed-revision history, and the active Run Engine's own code-version identity at capture time).
External dependencies: TD005-ARC-001, TD005-ARC-002; and, for its own one-time reference-capture bootstrap only (not a recurring dependency, TD005-AI-018), TD005-ARC-011 (Deterministic Replay Controller, for capturing a reference execution under controlled conditions) and TD005-ARC-012 (Execution-Environment Identity Recorder, for the environment-identity fact attached to this record, Section 10). This component's own separateness from TD005-ARC-001/002 is TD005-AD-002.
Architectural constraints: TD005-AI-003, TD005-AI-004, TD005-AI-013; this component never mutates the certified corpus it derives from.
Scientific justification: without a defined provenance, "previously-certified behaviour" is not a reproducible scientific object; an unreproducible reference cannot itself be certified (CGA Section 7, TD005-CAP-009, Critical risk).
Source capabilities: TD005-CAP-009.
Source dependencies: TD005-DEP-012, TD005-DEP-013, TD005-DEP-014.
Source requirements: TD005-FR-018, TD005-FR-019, TD005-FR-021; OQ-002.

### Domain D - Replay Control Architecture

**TD005-ARC-011. Deterministic Replay Controller.**
Purpose: ensure two executions of the active Run Engine are scientifically comparable.
Responsibilities: confirm the active module set contains no wall-clock, network, or non-seeded-randomness dependency (an already-AVAILABLE, zero-missing-element precondition this component enforces rather than re-derives); enumerate the complete set of conditions that must be held equal across two executions (input tick sequence, initial runtime state, initial Position, lifecycle history, regime/strategy state, configuration); confirm no Python collection's incidental iteration order introduces spurious non-determinism.
Inputs: a controlled-condition specification (tick sequence and initial state to replay from); the active Run Engine's own runtime entry point.
Outputs: a candidate execution trajectory, captured under confirmed controlled conditions, ready for observation.
Owned information: the controlled-condition enumeration; the environmental-determinism confirmation; the captured execution trajectory itself (Section 10, Ownership).
External dependencies: the active Run Engine (`run_engine.main` and its own fourteen-module closure), driven directly to produce the captured trajectory; TD005-ARC-012 (environment-identity fact recorded alongside each captured trajectory). This component does not depend on TD005-ARC-005: Replay drives execution, it does not itself read state for comparison purposes; TD005-ARC-005 subsequently exposes the resulting trajectory to Observation-layer and downstream components (Section 9, Section 10, Section 11), consistent with the Layer 3 -> Layer 4 information flow.
Architectural constraints: TD005-AI-006, TD005-AI-010, TD005-AI-013; never alters Run Engine runtime semantics (Stage Ordering, Ownership, Information Flow) as a side effect of enabling comparability.
Scientific justification: tick sequence alone is insufficient without also controlling initial Position, lifecycle history, and regime/strategy state; an incomplete controlled-condition set would allow a comparison to run under silently unequal conditions (CGA Section 7, TD005-CAP-011, High risk). TD005-CAP-010 (Environmental Determinism, AVAILABLE, zero missing elements) is merged into this component rather than given its own, since its entire content is one condition among several this component already enforces (TD005-AD-003).
Source capabilities: TD005-CAP-010, TD005-CAP-011.
Source dependencies: TD005-DEP-009, TD005-DEP-010, TD005-DEP-018.
Source requirements: TD005-FR-002, TD005-FR-013, TD005-FR-018; TD005-CON-004.

**TD005-ARC-012. Execution-Environment Identity Recorder.**
Purpose: determine whether the execution environment's own third-party numeric libraries and Python interpreter identity is a precondition for reproducible floating-point regression comparison across time.
Responsibilities: record the execution-environment identity (library and interpreter versions, including numeric-backend/BLAS identity) under which a reference baseline or a candidate execution was captured; expose this fact to TD005-ARC-003 (Reference Baseline Authority) and TD005-ARC-011 (Deterministic Replay Controller) without itself deciding which of the two owns the final provenance record.
Inputs: the active execution environment's own interpreter and third-party library identity (`requirements.txt`-pinned `numpy`, `pandas`, and the interpreter itself).
Outputs: an execution-environment identity record, attachable to a reference-baseline record (TD005-ARC-003) or a candidate-execution record (TD005-ARC-011).
Owned information: the execution-environment identity record.
External dependencies: none upstream; consumed by TD005-ARC-003 and TD005-ARC-011.
Architectural constraints: TD005-AI-013, TD005-AI-016; remains a distinct component rather than being silently subsumed by either consumer (TD005-AD-004).
Scientific justification: a numeric library's internal algorithm, its own numeric backend, or the interpreter's own numeric/hash behavior can change between versions even when the calling code and its inputs are unchanged, which would manifest as an apparent regression that is in fact an environment change (CGA Section 7, TD005-CAP-022, Medium risk, newly surfaced hidden capability).
Source capabilities: TD005-CAP-022.
Source dependencies: none directly (anchored to TD005-DEP-010 and TD005-DEP-014 by scientific proximity, per CGA Section 7).
Source requirements: TD005-CON-004 (by scientific proximity, not shared normative text, per CGA Section 7).

### Domain C - Observable Behaviour Architecture (Observation Layer)

**TD005-ARC-004. Observable Surface Classifier.**
Purpose: classify which runtime outputs and internal observations are scientifically legitimate candidates for regression evaluation.
Responsibilities: classify each already-enumerated field (the twelve CanonicalState fields, five lifecycle event types, LONG/SHORT side vocabulary, Executor status vocabulary) into one of four categories: certified external output, certified internal invariant, implementation detail, or incidental intermediate value.
Inputs: the enumerated field set, exposed through TD005-ARC-005 (Non-Interference Observation Gateway).
Outputs: a four-category classification of the observable surface, consumed by every Comparison-layer component.
Owned information: the four-category field classification.
External dependencies: TD005-ARC-005 (its own exclusive read path into the active Run Engine).
Architectural constraints: TD005-AI-002, TD005-AI-013.
Scientific justification: treating an implementation detail as a certified output would create a brittle, over-constrained regression capability; treating a certified output as incidental would leave a real regression undetected (CGA Section 7, TD005-CAP-007, Medium risk).
Source capabilities: TD005-CAP-007.
Source dependencies: TD005-DEP-007.
Source requirements: TD005-FR-003, TD005-FR-004, TD005-FR-005, TD005-FR-006, TD005-FR-013, TD005-FR-014, TD005-FR-015.

**TD005-ARC-005. Non-Interference Observation Gateway.**
Purpose: provide the sole, authoritative, non-interfering boundary through which any other component may observe active Run Engine behaviour.
Responsibilities: expose the confirmed non-interfering read path (`RunLoop.step()`'s own return value, a Tick-Complete state); state a single, authoritative boundary for where observation may legitimately occur; refuse any observation request that would read beyond the confirmed non-interfering boundary.
Inputs: the active Run Engine's own Tick-Complete state, at each tick boundary.
Outputs: an observed state snapshot, provided to TD005-ARC-004 and, transitively, every Comparison-layer component.
Owned information: the authoritative observation-boundary statement.
External dependencies: the active Run Engine (read-only, non-interfering).
Architectural constraints: TD005-AI-002 (never alters runtime behaviour as a side effect of observation); this is the exclusive read path - no other component reads the active Run Engine directly (TD005-AD-013).
Scientific justification: an observation mechanism that reads beyond a confirmed non-interfering boundary could itself violate TD005-CON-001, invalidating the very regression result it produces (CGA Section 7, TD005-CAP-008, Medium risk; FRA OQ-001).
Source capabilities: TD005-CAP-008.
Source dependencies: TD005-DEP-008, TD005-DEP-019.
Source requirements: TD005-CON-001, TD005-CON-002, TD005-FR-004, TD005-FR-005, TD005-FR-006; OQ-001.

### Domain C - Behavioural Equivalence Architecture (Comparison Layer)

**TD005-ARC-006. Behavioural Equivalence Authority.**
Purpose: formally define what "equivalent" means for regression purposes.
Responsibilities: hold the operational, formal definition of behavioural equivalence (as distinct from implementation, source, or byte identity); expose this definition to every other Comparison-layer component so each applies a consistent notion of "equivalent."
Inputs: the observable-surface classification (TD005-ARC-004); the trajectory model (TD005-ARC-007); the value-comparison policies (TD005-ARC-008, TD005-ARC-009).
Outputs: a formal equivalence definition, consumed by the Regression Classification Engine.
Owned information: the formal behavioural-equivalence definition.
External dependencies: TD005-ARC-001, TD005-ARC-002, TD005-ARC-004.
Architectural constraints: TD005-AI-007 (regression classification uses behavioural equivalence exclusively, never byte/source/implementation identity).
Scientific justification: TD005-FR-020 establishes the principle but does not define the algorithm; without an operational definition, "equivalence" risks silently collapsing into byte or source identity (CGA Section 7, TD005-CAP-003, Critical risk).
Source capabilities: TD005-CAP-003.
Source dependencies: TD005-DEP-004.
Source requirements: TD005-FR-020, TD005-FR-021, TD005-FR-018; OQ-006.

**TD005-ARC-007. Trajectory Comparison Model.**
Purpose: determine whether equivalence is defined over the final Tick-Complete state alone or over the complete execution trajectory.
Responsibilities: hold the trajectory-required property set (execution ordering, publication uniqueness, lifecycle transition integrity, failure-event generation, information-flow non-reconstruction); hold the logical-order-versus-wall-clock-timing distinction (already fully settled, no wall-clock or latency language governs comparison, only sequence language).
Inputs: two observed execution trajectories (reference and candidate), from TD005-ARC-005 by way of TD005-ARC-003 and TD005-ARC-011.
Outputs: a trajectory-level comparison basis, consumed by the Regression Classification Engine.
Owned information: the trajectory-required property set; the logical-order/wall-clock distinction.
External dependencies: TD005-ARC-006.
Architectural constraints: TD005-AI-004, TD005-AI-013.
Scientific justification: eight Functional Requirements are properties of the trajectory, not the final state, and cannot be validated by endpoint-only comparison; a future default to final-state-only comparison would leave them unprotected while appearing superficially complete (CGA Section 7, TD005-CAP-004, High risk).
Source capabilities: TD005-CAP-004.
Source dependencies: TD005-DEP-005, TD005-DEP-015, TD005-DEP-017.
Source requirements: TD005-FR-001, TD005-FR-003, TD005-FR-006, TD005-FR-007, TD005-FR-008, TD005-FR-009, TD005-FR-010, TD005-FR-017, TD005-FR-022.

**TD005-ARC-008. Numeric and Categorical Value Comparator.**
Purpose: define whether floating-point-derived quantities require exact equality, tolerance-bounded, or normalized comparison, and separately confirm which values are categorical/discrete.
Responsibilities: hold the numeric-versus-categorical comparison-policy question (not the specific tolerance value, a Specification concern); hold the formal separation of the categorical/discrete value set (`event_type`, Position Side) from the continuous financial and risk/performance value set.
Inputs: individual observed values from TD005-ARC-004's own classified surface.
Outputs: a per-value comparison-policy classification, consumed by the Regression Classification Engine.
Owned information: the numeric/categorical comparison-policy statement.
External dependencies: TD005-ARC-004, TD005-ARC-006.
Architectural constraints: TD005-AI-013; does not select a tolerance value (TD005-ARC-022, Specification input). Remains a separate component from TD005-ARC-009 (TD005-AD-005).
Scientific justification: applying a single uniform comparison policy across categorical and continuous values would produce false positives or false negatives (CGA Section 7, TD005-CAP-005, Medium risk).
Source capabilities: TD005-CAP-005.
Source dependencies: TD005-DEP-006, TD005-DEP-016.
Source requirements: TD005-FR-007, TD005-FR-008, TD005-FR-009, TD005-FR-010, TD005-FR-011, TD005-FR-012, TD005-FR-013, TD005-FR-014, TD005-FR-015, TD005-FR-016, TD005-FR-017 (the eleven-requirement set the CGA itself names).

**TD005-ARC-009. Object-Identity-Independent Comparator.**
Purpose: ensure observed equivalence is independent of Python object identity and process-local mutable state.
Responsibilities: hold the value-equality-only comparison rule (dict/list identity is never itself a comparison criterion; structural value equality is).
Inputs: individual observed values from TD005-ARC-004's own classified surface.
Outputs: an identity-independent comparison rule, consumed by the Regression Classification Engine.
Owned information: the value-equality-only rule.
External dependencies: TD005-ARC-004, TD005-ARC-006.
Architectural constraints: TD005-AI-013.
Scientific justification: an equivalence check relying inadvertently on object identity rather than value equality would produce false-positive regressions for benign refactors (CGA Section 7, TD005-CAP-006, Medium risk).
Source capabilities: TD005-CAP-006.
Source dependencies: TD005-DEP-011.
Source requirements: TD005-FR-002, TD005-FR-005.

**TD005-ARC-010. Behavioural Vocabulary Authority.**
Purpose: ensure the terms used throughout the certified corpus have stable, unambiguous, cross-document-consistent definitions.
Responsibilities: hold the authoritative vocabulary (Position, Side, Scale-In, Partial Close, Full Close, Tick-Complete, Canonical Working State, Authoritative Owner, Computational Authority, Runtime Failure Event); expose this vocabulary to every other component whose own scientific rationale is stated in these terms.
Inputs: the Architecture Baseline's own Ownership Terminology section and ADR-009's own Scientific Definitions.
Outputs: the authoritative vocabulary, consumed by every other component.
Owned information: the vocabulary itself.
External dependencies: none (Foundational; reads only the already-certified Architecture Baseline).
Architectural constraints: TD005-AI-001, TD005-AI-013.
Scientific justification: no equivalence or comparison model can be built on top of an unstable vocabulary (CGA Section 7, TD005-CAP-021, AVAILABLE). Represented as a first-class component (TD005-AD-012) despite already being fully available, since every dependent component's own scientific rationale presupposes it.
Source capabilities: TD005-CAP-021.
Source dependencies: TD005-DEP-032.
Source requirements: all twenty-two Functional Requirements (indirectly, as the vocabulary every requirement is stated in).

### Domain G - Regression Classification Architecture (Classification Layer)

**TD005-ARC-017. Regression Classification Engine.**
Purpose: given an observed deviation, evaluate it against the certified-contract boundary and determine whether it constitutes a genuine behavioural regression or a non-regression.
Responsibilities: consume the certification boundary (TD005-ARC-002), the formal equivalence definition and its three constituent models (TD005-ARC-006, TD005-ARC-007, TD005-ARC-008, TD005-ARC-009), and coverage-completeness context (TD005-ARC-015, TD005-ARC-016, advisory only) to produce exactly one of two outcomes per observed deviation: regression, or non-regression.
Inputs: an observed deviation (a candidate execution compared against the Reference Baseline Authority's own reference record); the certification boundary; the formal equivalence definition.
Outputs: a regression/non-regression classification, consumed by TD005-ARC-013 (Regression Evidence Composer).
Owned information: the classification verdict for each evaluated deviation.
External dependencies: TD005-ARC-002, TD005-ARC-003, TD005-ARC-006, TD005-ARC-007, TD005-ARC-008, TD005-ARC-009; advisory input from TD005-ARC-015, TD005-ARC-016 (TD005-AI-014).
Architectural constraints: TD005-AI-007, TD005-AI-008, TD005-AI-009, TD005-AI-013, TD005-AI-014; explicitly excludes severity ranking, business acceptability, waiver decisions, remediation priority, and operational disposition (TD005-AD-008); treats a failure of any upstream component to produce its own stated Output as a distinct condition, never as a regression or non-regression verdict (TD005-AI-019).
Scientific justification: this is the capability that directly answers TD-005's own governing scientific question, and it is the point at which the certified-contract boundary, the formal equivalence definition, and coverage completeness must jointly operate (CGA Section 7, TD005-CAP-012, Critical risk, TD-005's own central deliverable capability).
Source capabilities: TD005-CAP-012.
Source dependencies: TD005-DEP-002, TD005-DEP-004, TD005-DEP-020.
Source requirements: TD005-FR-018, TD005-FR-020, TD005-FR-021.

### Domain F - Coverage Architecture (Coverage Layer)

**TD005-ARC-015. Contract-to-Requirement Coverage Auditor.**
Purpose: confirm every certified contract in the corpus is traceable to at least one Functional Requirement, and every Functional Requirement is traceable to at least one certified contract.
Responsibilities: maintain the citation-frequency-based coverage check that identified AC-003's own partial instantiation and AC-011's own uncovered end-to-end traceability property; surface any coverage gap explicitly to Governance (TD005-ARC-018), never resolve it by itself narrowing the Classification Engine's own scope.
Inputs: the Certified Contract Registry's own enumeration; the FRA's own twenty-two Functional Requirements.
Outputs: a coverage-completeness report, advisory to the Regression Classification Engine.
Owned information: the coverage-completeness report.
External dependencies: TD005-ARC-001.
Architectural constraints: TD005-AI-014 (advisory only, never alters an individual classification verdict).
Scientific justification: an uncovered certified contract could regress without any Functional Requirement detecting it (CGA Section 7, TD005-CAP-015, High risk).
Source capabilities: TD005-CAP-015.
Source dependencies: TD005-DEP-020.
Source requirements: all twenty-two Functional Requirements (completeness check spans the whole set); TD005-FR-013 (AC-003), TD005-FR-006 (AC-011 gap).

**TD005-ARC-016. Module and State-Transition Coverage Auditor.**
Purpose: confirm all fourteen active modules and the certified state-transition table are covered by the Functional Requirements, and hold the chosen coverage concept.
Responsibilities: maintain the explicit, individually-traced requirement-to-module mapping (closing the four-module gap: `run_engine/main.py`, `run_engine/core/state.py`, `run_engine/core/regime.py`, `run_engine/core/execution/__init__.py`); hold whichever coverage concept (module, contract, domain, state-transition, event, requirement, path, risk-based, or a combination) Specification ultimately adopts, as an explicit, named contract this component enforces.
Inputs: the active module set (TD005-ARC-005's own scope); the FRA's own Functional Requirements.
Outputs: a module/state-transition coverage report, advisory to the Regression Classification Engine.
Owned information: the module/state-transition coverage report; the chosen coverage concept.
External dependencies: TD005-ARC-005, TD005-ARC-007 (state-transition coverage depends on the trajectory model).
Architectural constraints: TD005-AI-014.
Scientific justification: module coverage alone does not guarantee state-transition coverage of ADR-009's own five-row Lifecycle Transition Table; a genuine regression confined to one of the four gap modules could occur without any Functional Requirement explicitly designed to detect it (CGA Section 7, TD005-CAP-016, High risk).
Source capabilities: TD005-CAP-016.
Source dependencies: TD005-DEP-021, TD005-DEP-022.
Source requirements: FRA Section 13.1 (Active Module Coverage Obligation); TD005-FR-001, TD005-FR-002, TD005-FR-007, TD005-FR-008, TD005-FR-009, TD005-FR-010.

### Domain E - Evidence Collection Architecture (Evidence Layer)

**TD005-ARC-013. Regression Evidence Composer.**
Purpose: define and produce the complete set of evidence elements a detected regression must carry for independent reproduction and certification.
Responsibilities: compose the FRA's own four minimum elements (affected tick, affected stage or component, expected value, actual value) together with the SDA's own four refinement elements (input provenance, initial-state provenance, the specific certified-contract ID, execution-environment identity) into one evidence record per detected regression.
Inputs: a regression classification (TD005-ARC-017); the controlled-condition record (TD005-ARC-011); the execution-environment identity record (TD005-ARC-012); the certification boundary (TD005-ARC-002).
Outputs: a complete regression-evidence record, consumed by TD005-ARC-014.
Owned information: the evidence-composition schema (the set of required elements, not their storage form); each composed evidence-record instance, from composition until handed to TD005-ARC-014 for persistence.
External dependencies: TD005-ARC-017, TD005-ARC-011, TD005-ARC-012, TD005-ARC-002.
Architectural constraints: TD005-AI-005 (never modifies the observed behaviour, the reference baseline, or the classification outcome it documents).
Scientific justification: incomplete evidence composition would defeat TD005-FR-019's own independent-reproduction purpose even if a regression is correctly detected (CGA Section 7, TD005-CAP-013, Medium risk).
Source capabilities: TD005-CAP-013.
Source dependencies: TD005-DEP-023.
Source requirements: TD005-FR-019.

**TD005-ARC-014. Evidence Persistence and Continuity Authority.**
Purpose: define whether detected-regression evidence must be persisted consistent with this project's own established governance-document conventions, and how evidence carries across Long-Duration-Validation stages.
Responsibilities: hold the persistence-format decision boundary (not the format itself, a Specification concern); hold the continuity mechanism required across the six Long-Duration-Validation stages.
Inputs: regression-evidence records from TD005-ARC-013.
Outputs: a persisted, continuity-linked evidence record, consumed by TD005-ARC-018 (Long-Duration-Validation Integration Adapter).
Owned information: the persistence-and-continuity contract.
External dependencies: TD005-ARC-013.
Architectural constraints: TD005-AI-005, TD005-AI-015 (never extends, contradicts, or bypasses Repository Consolidation's own Normative Repository Boundary), TD005-AI-017 (selects no storage mechanism).
Scientific justification: unmanaged evidence persistence could lose regression evidence needed for a later Final Certification or accumulate governance-document sprawl; without continuity, a regression introduced between validation stages could be harder to attribute to a specific stage transition (CGA Section 7, TD005-CAP-014, Medium risk).
Source capabilities: TD005-CAP-014.
Source dependencies: TD005-DEP-024, TD005-DEP-027.
Source requirements: TD005-FR-019, TD005-FR-022; TD005-CON-003.

### Domain H - Governance Integration Architecture (Governance Layer)

**TD005-ARC-018. Long-Duration-Validation Integration Adapter.**
Purpose: determine the regression capability's own feasible application model across the six mandatory Long-Duration-Validation stages.
Responsibilities: hold the execution-time-feasibility tension (a single capability must serve both Functional-smoke's fast-turnaround expectation and 30-day validation's own tolerance for longer execution); hold the pre-run-versus-post-run application-model choice; hold the evidence-continuity mechanism shared with TD005-ARC-014.
Inputs: the six-stage Long-Duration-Validation sequence (Implementation Baseline); persisted evidence records (TD005-ARC-014).
Outputs: a stage-applicable invocation contract, usable without modification before each of the six stages.
Owned information: the execution-time-feasibility resolution; the application-model choice.
External dependencies: TD005-ARC-014.
Architectural constraints: TD005-AI-013; does not itself select a concrete execution-time budget (Specification input).
Scientific justification: TD005-FR-022 requires the same capability to be usable, without modification, before each of the six stages; an execution-time profile or application model incompatible with the fastest stage would delay or discourage its use exactly where early regression detection matters most (CGA Section 7, TD005-CAP-020, Medium risk).
Source capabilities: TD005-CAP-020.
Source dependencies: TD005-DEP-025, TD005-DEP-026, TD005-DEP-027.
Source requirements: TD005-FR-022, TD005-FR-019; OQ-004.

**TD005-ARC-019. Governance Sequence Conformance Marker.**
Purpose: ensure TD-005's own resolution proceeds through the established FRA, SDA, CGA, Architecture, Specification, Implementation, Final Certification sequence.
Responsibilities: record this Architecture's own explicit refusal to select architecture-inappropriate content (framework, implementation); provide a citable artifact for any future Architecture Evolution Review (Implementation Baseline Principle IP-006) to check against, rather than requiring re-derivation from narrative alone.
Inputs: none (a governance-metadata component; consumes no runtime information).
Outputs: a governance-conformance record, referenced by any future review of this Architecture.
Owned information: the governance-conformance record itself (metadata only; not consumed by any regression-detection pipeline component - a marker component, by design; TD005-AD-011).
External dependencies: none.
Architectural constraints: TD005-AI-013.
Scientific justification: skipping ahead of the governance sequence would produce architecture decisions ungrounded in a completed scientific analysis, exactly the failure this repository's own governance discipline exists to prevent (CGA Section 7, TD005-CAP-019, AVAILABLE).
Source capabilities: TD005-CAP-019.
Source dependencies: TD005-DEP-033.
Source requirements: all FRA items (procedurally).

### Domain I - Repository Boundary Protection

**TD005-ARC-020. Active/Deferred Scope Boundary Authority.**
Purpose: maintain a stable, independently-reproducible definition of "the active Run Engine," and ensure the coverage mechanism remains sensitive to any future change in the active/inactive partition.
Responsibilities: hold the current, correctly-justified exclusion of the four RETAIN-Deferred-Scope files; hold the (currently unresolved, Optional-priority) scope-drift-sensitivity requirement for TD005-ARC-016's own future coverage mechanism.
Inputs: the active/inactive module partition (Section 5, Item 2).
Outputs: the current scope boundary, consumed by every component whose own scope presupposes "the active Run Engine" (TD005-ARC-001, TD005-ARC-004, TD005-ARC-011, TD005-ARC-015, TD005-ARC-016).
Owned information: the active/inactive scope boundary; the scope-drift-sensitivity requirement (unresolved).
External dependencies: none (Foundational).
Architectural constraints: TD005-AI-011.
Scientific justification: every other component in this Architecture presupposes a stable definition of what is currently in scope; a scope-blind coverage mechanism would silently miss a future reactivation of a currently-deferred module (CGA Section 7, TD005-CAP-017, Low risk).
Source capabilities: TD005-CAP-017.
Source dependencies: TD005-DEP-028, TD005-DEP-029, TD005-DEP-031.
Source requirements: FRA Section 6.3 (evidence); OQ-003. OQ-005 (test-code location) is compatible with, but not resolved by, this component's own scope boundary (Section 17).

**TD005-ARC-021. Executor Namespace Boundary Marker.**
Purpose: explicitly confirm this Architecture does not own, extend, or duplicate Repository Consolidation's own Executor-namespace-uniqueness protection.
Responsibilities: record the boundary exclusion; provide the single citable point confirming this Architecture's own scope stops here, should any future reviewer ask why no Executor-namespace component exists among TD005-ARC-001 through TD005-ARC-020.
Inputs: none (a boundary-marker component; consumes no runtime information).
Outputs: an explicit exclusion record.
Owned information: the explicit exclusion record itself (metadata only; not consumed by any regression-detection pipeline component - by design; TD005-AD-009).
External dependencies: none; references, but does not consume or duplicate, Repository Consolidation's own already-certified RC-AD-004 mechanism.
Architectural constraints: TD005-AI-012.
Scientific justification: conflating this with general behavioral regression could cause a future Architecture to over-scope TD-005 into Repository Consolidation's own separate, already-certified governance concern (CGA Section 7, TD005-CAP-018, OUTSIDE TD-005 SCOPE as a behavioral capability, AVAILABLE as a repository-integrity fact).
Source capabilities: TD005-CAP-018.
Source dependencies: TD005-DEP-030.
Source requirements: FRA Section 13.2 (Repository-Integrity Regression Obligation).

### Domain J - Architecture Extension Points

**TD005-ARC-022. Specification Extension Point Registry.**
Purpose: expose every unresolved Architecture-level choice explicitly, as a named, stable contract Specification must satisfy, without this Architecture choosing the mechanism itself.
Responsibilities: enumerate, by name, every mechanism decision this Architecture leaves open (the twelve named in Section 17); attach each to its own governing component (TD005-ARC-001 through TD005-ARC-021); ensure no Specification-stage mechanism choice is made silently within a component's own future implementation without being recorded here first.
Inputs: every component's own unresolved mechanism boundary (Section 17).
Outputs: the Specification handover list (Section 17), the primary artifact a future Specification stage consumes.
Owned information: the extension-point registry itself (the list of named, open decisions and their owning components).
External dependencies: all twenty-one other components (reads their own stated constraints; writes nothing back).
Architectural constraints: TD005-AI-016, TD005-AI-017. This component's own "External dependencies: all twenty-one other components" (below) is a documentation-time, read-only relationship (Section 11); it introduces no runtime coupling, and no component is required to invoke TD005-ARC-022 as part of its own runtime behavior.
Scientific justification: the CGA's own Section 11 (Specification Readiness) names twelve distinct deferred mechanism decisions spanning nearly every capability; without an explicit architectural home, these deferrals risk becoming silent assumptions baked into component design rather than explicit, governed extension contracts (TD005-AD-007).
Source capabilities: TD005-CAP-001, TD005-CAP-002, TD005-CAP-004, TD005-CAP-005, TD005-CAP-009, TD005-CAP-011, TD005-CAP-012, TD005-CAP-013, TD005-CAP-014, TD005-CAP-016, TD005-CAP-020, TD005-CAP-022 (the twelve capabilities the CGA's own Section 11 names; aggregate traceability, not single-capability derivation, exactly as CAP-022 itself was traced by scientific proximity rather than direct SDA citation).
Source dependencies: none directly (aggregate origin, per above).
Source requirements: none directly (aggregate origin; each constituent capability's own Source requirements apply transitively).

## 9. Layered Architecture

The governing task's own seven-layer skeleton (Foundational, Reference, Observation, Comparison, Classification, Evidence, Governance) is extended to ten layers, since three of the governing task's own required architectural domains - Replay Control Architecture (D), Coverage Architecture (F), and Architecture Extension Points (J) - have no coherent home within the seven-layer skeleton and each carries genuinely distinct scientific content (Section 8). This extension is itself Architecture Decision TD005-AD-010.

**Layer 1 - Foundational.** No architectural prerequisite; establishes authority, vocabulary, scope, or governance conditions required by multiple downstream layers. Components: TD005-ARC-001 (Certified Contract Registry), TD005-ARC-010 (Behavioural Vocabulary Authority), TD005-ARC-019 (Governance Sequence Conformance Marker), TD005-ARC-020 (Active/Deferred Scope Boundary Authority), TD005-ARC-021 (Executor Namespace Boundary Marker). Belongs here because: each presupposes nothing else in this Architecture, and each is a direct prerequisite - authority, vocabulary, scope, or governance-boundary - for components in every other layer.

**Layer 2 - Reference.** Depends on Foundational components, with one explicit, one-time exception (below). Components: TD005-ARC-002 (Certification Boundary Authority, depends on TD005-ARC-001), TD005-ARC-003 (Reference Baseline Authority, depends on TD005-ARC-001, TD005-ARC-002, and, for its own one-time reference-capture bootstrap only, TD005-ARC-011 and TD005-ARC-012 in Layer 3 - TD005-AI-018). Belongs here because: both define "what is the authoritative reference" without yet performing any ongoing replay, observation, or comparison; TD005-ARC-003's own bootstrap dependency establishes the reference exactly once and is not a recurring, per-comparison dependency.

**Layer 3 - Replay.** Depends on Foundational components. Components: TD005-ARC-011 (Deterministic Replay Controller), TD005-ARC-012 (Execution-Environment Identity Recorder). Belongs here because: replay produces the concrete execution data consumed in two distinct roles - (a) a one-time reference capture, bootstrapped into TD005-ARC-003's own record before any comparison exists (TD005-AI-018), and (b) a repeated candidate capture, produced for every subsequent comparison, strictly downstream of the already-established reference. Only role (b) is the ordinary Layer 3 -> Layer 4 forward flow; role (a) is the sole, explicitly-recorded exception to this Architecture's own layer ordering (below).

**Layer 4 - Observation.** Depends on Foundational and Replay components. Components: TD005-ARC-004 (Observable Surface Classifier), TD005-ARC-005 (Non-Interference Observation Gateway). Belongs here because: both operate on a captured execution (from Replay) to produce a classified, non-interfering observation, prior to any comparison.

**Layer 5 - Comparison.** Depends on Foundational, Reference, and Observation components. Components: TD005-ARC-006 (Behavioural Equivalence Authority), TD005-ARC-007 (Trajectory Comparison Model), TD005-ARC-008 (Numeric and Categorical Value Comparator), TD005-ARC-009 (Object-Identity-Independent Comparator). Belongs here because: each defines a facet of "what counts as equivalent" applied to the Observation layer's own classified surface, prior to any classification verdict.

**Layer 6 - Coverage.** Depends on Foundational components directly (TD005-ARC-015, via TD005-ARC-001 only) or on Foundational, Observation, and Comparison components (TD005-ARC-016, via TD005-ARC-005 and TD005-ARC-007); audits the pipeline's own completeness rather than producing a verdict. Components: TD005-ARC-015 (Contract-to-Requirement Coverage Auditor), TD005-ARC-016 (Module and State-Transition Coverage Auditor). Belongs here because: coverage answers "can Classification ever detect a regression here at all," a completeness question about the whole pipeline, categorically distinct from Classification's own "is this specific deviation a regression" question (TD005-AD-006); positioned immediately before Classification since its own advisory output is consumed there.

**Layer 7 - Classification.** Depends on Reference, Comparison, and Coverage components. Component: TD005-ARC-017 (Regression Classification Engine). Belongs here because: it is the single point composing every upstream layer's own output into one verdict, and nothing downstream informs it back (TD005-AI-014).

**Layer 8 - Evidence.** Depends on Replay and Classification components. Components: TD005-ARC-013 (Regression Evidence Composer), TD005-ARC-014 (Evidence Persistence and Continuity Authority). Belongs here because: evidence is composed only after a classification verdict exists, and never feeds back into it (TD005-AI-005).

**Layer 9 - Governance.** Depends on Foundational and Evidence components. Component: TD005-ARC-018 (Long-Duration-Validation Integration Adapter). Belongs here because: it governs how the whole pipeline is invoked across the six validation stages, consuming persisted evidence (Evidence layer) without itself participating in any single comparison.

**Layer 10 - Extension.** Cross-cutting; reads every other layer's own unresolved mechanism boundary without participating in the regression-detection data flow itself. Component: TD005-ARC-022 (Specification Extension Point Registry). Belongs here because: it is the layer through which every other layer's own unresolved Specification-level choice is exposed, positioned last as the Architecture's own explicit handover surface (Section 17).

No component appears in more than one layer; no layer is empty. With one explicit, scientifically-justified exception - TD005-ARC-003's own one-time bootstrap dependency on TD005-ARC-011 and TD005-ARC-012 for its initial reference capture (TD005-AI-018) - every component's own External dependencies (Section 8) resolve to a layer at or below its own. This exception does not constitute a cycle: it is a single, one-time act (establishing the reference) that precedes, and is never repeated by, the ongoing per-comparison flow every other dependency in this Architecture follows (Section 12, TD005-AI-013 verified by construction).

## 10. Information Flow

**Ownership.** Every piece of information has exactly one owning component (Section 8, "Owned information" field for each). No two components own the same information; where two components jointly require the same fact (for example, execution-environment identity, owned solely by TD005-ARC-012 but consumed by both TD005-ARC-003 and TD005-ARC-011), the consuming components hold a reference to the owning component's own record, never a copy they could independently mutate.

**Allowed flow.** Foundational -> Reference -> Replay -> Observation -> Comparison -> Coverage -> Classification -> Evidence -> Governance, with Extension reading (never writing into) every other layer. Within a layer, components may read siblings' own outputs (for example, TD005-ARC-008 and TD005-ARC-009 both read TD005-ARC-004's own classified surface) but never write to a sibling's owned information. One explicit exception to this ordering exists: TD005-ARC-003's own one-time reference-capture bootstrap consumes Replay-layer output before any ongoing comparison begins (Section 9, TD005-AI-018); this occurs exactly once per reference establishment or governed revision, never per comparison.

**Forbidden flow.** No component below Classification (Layers 1-7) may read a Classification, Evidence, or Governance-layer output - the pipeline is strictly forward, never back-influencing an earlier layer's own determination (this is what makes TD005-ARC-015/TD005-ARC-016's own Coverage output "advisory," TD005-AI-014: it flows into Classification, but nothing flows back out of Classification into Coverage). No component of any layer writes to the active Run Engine; the only permitted read path into the active Run Engine is TD005-ARC-005 (TD005-AI-002, TD005-AD-013). No component in the Evidence or Governance layer writes to the Reference or Comparison layers' own owned information (TD005-AI-004, TD005-AI-005).

**Information lifecycle.** (1) Reference establishment: TD005-ARC-001/002 define the certified corpus and its boundary; TD005-ARC-003 selects and records a reference-baseline instance, attaching TD005-ARC-012's own environment-identity fact. (2) Replay: TD005-ARC-011 captures a candidate execution under controlled conditions equivalent to the reference's own capture conditions, attaching a fresh TD005-ARC-012 environment-identity fact. (3) Observation: TD005-ARC-005 exposes the candidate trajectory non-interferingly; TD005-ARC-004 classifies its own observable fields. (4) Comparison: TD005-ARC-006 through TD005-ARC-009 jointly determine equivalence between the reference and the candidate, field by field and trajectory-wide. (5) Coverage: TD005-ARC-015/016 independently confirm the comparison's own completeness, advisory to (6) Classification: TD005-ARC-017 produces exactly one verdict per evaluated deviation. (7) Evidence: TD005-ARC-013 composes a complete evidence record for any regression verdict; TD005-ARC-014 governs its persistence and cross-stage continuity. (8) Governance: TD005-ARC-018 governs when and how this entire lifecycle is invoked across the six Long-Duration-Validation stages.

**Immutability.** The certified-contract corpus (TD005-ARC-001), the certification boundary (TD005-ARC-002), and the reference-baseline record (TD005-ARC-003) are immutable once established, or changed only through an explicit, governed revision (TD005-AI-003); no component in Layers 3-10 may alter any of the three. Observed candidate data (Layer 4) is immutable once captured; Comparison-layer components (Layer 5) read it, they do not transform it in place. Evidence records (Layer 8) are immutable once composed (TD005-AI-005): a regression's own evidence record is never edited after the fact, only ever superseded by a new, separately-composed record if the underlying comparison is independently re-run.

**Reference creation, comparison, classification, evidence persistence** are each the responsibility of exactly one layer (Reference, Comparison, Classification, Evidence respectively), per the lifecycle above; no component outside its own designated layer performs another layer's own information-producing act.

No storage technology is specified for any stage of this lifecycle; "record," "persist," and "expose" above denote logical information transfer, not a chosen mechanism (TD005-AI-017, Section 17).

## 11. Component Interaction

Interactions are described logically (provided/required interface, preconditions, postconditions, sequencing); no API is defined.

- **TD005-ARC-001 -> TD005-ARC-002.** Provided: an enumerable candidate-contract space. Required: none (TD005-ARC-002 requires only a candidate to classify). Precondition: the corpus enumeration exists. Postcondition: every candidate has a certification-status determination. Sequencing: TD005-ARC-002 may be invoked any time after TD005-ARC-001's own enumeration is available; no per-tick ordering is implied.
- **TD005-ARC-001, TD005-ARC-002 -> TD005-ARC-003.** Provided: the certified corpus and its boundary. Required: a captured candidate/reference execution (from TD005-ARC-011) and an environment-identity fact (from TD005-ARC-012). Precondition: corpus and boundary are established. Postcondition: exactly one reference-baseline record exists, immutable or governed. Sequencing: TD005-ARC-003 cannot complete before TD005-ARC-011 and TD005-ARC-012 have each produced their own output for the capture in question.
- **TD005-ARC-003, TD005-ARC-012 -> TD005-ARC-011.** Provided: the reference-baseline record's own controlled-condition specification (what to replay). Required: none additional. Precondition: a controlled-condition specification exists (either the reference's own, for a first capture, or a candidate specification, for a later comparison run). Postcondition: a captured execution trajectory exists, environment-identity-tagged. Sequencing: one invocation per comparison; the reference capture and the candidate capture are two independent invocations of the same controller, not a shared single run.
- **TD005-ARC-011 -> TD005-ARC-005 -> TD005-ARC-004.** Provided: a captured execution trajectory (Replay), exposed non-interferingly (Observation Gateway), classified (Surface Classifier). Required: none additional. Precondition: a trajectory has been captured. Postcondition: a classified observation exists for the trajectory. Sequencing: strictly after Replay, strictly before Comparison.
- **TD005-ARC-004, TD005-ARC-001, TD005-ARC-002 -> TD005-ARC-006, TD005-ARC-007, TD005-ARC-008, TD005-ARC-009.** Provided: a classified observation, the certified corpus, and the certification boundary. Required: none additional. Precondition: both a reference observation and a candidate observation exist for the same comparison. Postcondition: a per-facet equivalence determination exists (trajectory-level, numeric/categorical, identity-independent), unified under TD005-ARC-006's own formal definition. Sequencing: the four Comparison-layer components may execute in any order relative to each other; all four must complete before Classification proceeds.
- **TD005-ARC-006 through TD005-ARC-009, TD005-ARC-015, TD005-ARC-016 -> TD005-ARC-017.** Provided: the joint equivalence determination (required) and the coverage-completeness report (advisory, per TD005-AI-014). Required: the equivalence determination is mandatory; the coverage report is consulted but its own absence or incompleteness does not block a classification verdict. Precondition: Comparison-layer output exists for the deviation under evaluation. Postcondition: exactly one verdict (regression / non-regression) exists for the deviation. Sequencing: Classification is the single synchronization point of the pipeline; it does not proceed until every mandatory upstream input is available.
- **TD005-ARC-017, TD005-ARC-011, TD005-ARC-012, TD005-ARC-002 -> TD005-ARC-013.** Provided: the classification verdict, the controlled-condition record, the environment-identity record, the certification boundary. Required: none additional. Precondition: a regression verdict exists. Postcondition: a complete, immutable evidence record exists. Sequencing: strictly after Classification.
- **TD005-ARC-013 -> TD005-ARC-014 -> TD005-ARC-018.** Provided: a composed evidence record, then a persisted, continuity-linked record. Required: none additional. Precondition: an evidence record exists. Postcondition: the record is retrievable across Long-Duration-Validation stage transitions. Sequencing: strictly after Evidence Composition; Governance-layer invocation of the whole pipeline may recur once per validation stage, per TD005-ARC-018's own stage-applicable invocation contract.
- **All components -> TD005-ARC-022.** Provided: each component's own stated, unresolved mechanism boundary (Section 8, "Architectural constraints" and Section 17). Required: none (read-only). Precondition: none. Postcondition: the Specification Extension Point Registry accurately reflects every component's own current deferral. Sequencing: continuous; not part of the per-comparison data flow.

## 12. Architecture Invariants

**TD005-AI-001.** The Certified Contract Registry (TD005-ARC-001) and the Behavioural Vocabulary Authority (TD005-ARC-010) SHALL remain the sole authoritative sources of, respectively, certified behavioural contracts and behavioural vocabulary; no component SHALL treat any other document or artifact as authoritative for either. Traceability: TD005-CAP-001, TD005-CAP-021; TD005-FR-021.

**TD005-AI-002.** The Non-Interference Observation Gateway (TD005-ARC-005) SHALL NEVER alter the runtime behaviour of the active Run Engine as a side effect of observation. Traceability: TD005-CON-001, TD005-CAP-008.

**TD005-AI-003.** The Reference Baseline Authority's own reference-baseline record (TD005-ARC-003) SHALL be immutable once established, or changed only through a governed, explicitly recorded revision. Traceability: TD005-CAP-009.

**TD005-AI-004.** Comparison-layer components (TD005-ARC-006 through TD005-ARC-009) SHALL NEVER mutate the reference baseline or the observed candidate data they compare. Traceability: TD005-CAP-003, TD005-CAP-009 (task-named example invariant).

**TD005-AI-005.** The Regression Evidence Composer and the Evidence Persistence and Continuity Authority (TD005-ARC-013, TD005-ARC-014) SHALL NEVER modify the observed behaviour, the reference baseline, or the classification outcome they document. Traceability: TD005-CAP-013, TD005-CAP-014 (task-named example invariant).

**TD005-AI-006.** The Deterministic Replay Controller (TD005-ARC-011) SHALL NEVER alter Run Engine runtime semantics (Stage Ordering, Ownership, Information Flow) as a consequence of enabling comparability. Traceability: TD005-CON-002, TD005-CAP-011 (task-named example invariant).

**TD005-AI-007.** Regression classification SHALL be based exclusively on behavioural equivalence as defined by the Behavioural Equivalence Authority (TD005-ARC-006), never on byte identity, source identity, or implementation identity. Traceability: TD005-FR-020, TD005-CAP-003.

**TD005-AI-008.** No component SHALL classify a deviation as a regression, or as a non-regression, outside the certified-contract boundary established by the Certification Boundary Authority (TD005-ARC-002). Traceability: TD005-CAP-002, TD005-CAP-012.

**TD005-AI-009.** The Regression Classification Engine (TD005-ARC-017) SHALL NOT perform severity ranking, business-acceptability determination, waiver decisions, remediation-priority assignment, or operational disposition. Traceability: TD005-CAP-012 (CGA V1.1 Atomicity Review, Option B).

**TD005-AI-010.** Every regression-check execution SHALL occur under the Deterministic Replay Controller's own enforced controlled-condition set; no comparison SHALL be performed under uncontrolled or partially-controlled conditions. Traceability: TD005-CAP-011.

**TD005-AI-011.** The active/inactive Run Engine module partition (TD005-ARC-020) SHALL remain the sole authoritative scope definition for TD-005; no component SHALL treat a RETAIN-Deferred-Scope module as in-scope without a separate, governed Architecture Evolution Review. Traceability: TD005-CAP-017, ADR-012, RC-AD-005.

**TD005-AI-012.** This Architecture SHALL NOT absorb, duplicate, or re-implement Repository Consolidation's own Executor-namespace-uniqueness protection; that protection remains owned exclusively by Repository Consolidation's own already-certified mechanism. Traceability: TD005-CAP-018, RC-AD-004.

**TD005-AI-013.** Every architectural component SHALL remain traceable to at least one accepted FRA requirement, one or more SDA dependencies, and one or more CGA capabilities; no component SHALL be introduced solely for implementation convenience. Traceability: this Architecture's own Section 2 (Architectural Principle), verified in Section 15.

**TD005-AI-014.** Coverage-layer output (TD005-ARC-015, TD005-ARC-016) SHALL be advisory to, and SHALL NOT itself alter, the Regression Classification Engine's own verdict for any individual comparison. Traceability: TD005-CAP-015, TD005-CAP-016.

**TD005-AI-015.** Evidence persistence (TD005-ARC-014) SHALL NOT extend, contradict, or bypass Repository Consolidation's own Normative Repository Boundary. Traceability: TD005-CON-003, TD005-CAP-014.

**TD005-AI-016.** The Specification Extension Point Registry (TD005-ARC-022) SHALL expose every unresolved Architecture-level choice explicitly; no Specification-stage mechanism choice SHALL be made silently within this Architecture. Traceability: TD005-CAP-022, CGA Section 11.

**TD005-AI-017.** No architectural component SHALL select a test framework, comparison algorithm, storage mechanism, or persistence implementation; every such choice remains exclusively a Specification-stage responsibility. Traceability: this document's own Section 1 scope restriction (governing task Section 1).

**TD005-AI-018.** The Reference Baseline Authority's (TD005-ARC-003) own reference-capture dependency on the Deterministic Replay Controller and the Execution-Environment Identity Recorder (TD005-ARC-011, TD005-ARC-012) SHALL occur at most once per reference establishment or governed revision (TD005-AI-003); it SHALL NOT recur for, and SHALL NOT be conflated with, the ongoing candidate captures TD005-ARC-011 produces for individual comparisons. Traceability: TD005-CAP-009, TD005-CAP-010, TD005-CAP-011 (bootstrap relationship, Section 9).

**TD005-AI-019.** A failure of any Foundational, Reference, Replay, Observation, or Comparison-layer component to produce its own stated Output (Section 8) SHALL NOT be classified by the Regression Classification Engine (TD005-ARC-017) as either a regression or a non-regression; it SHALL be surfaced as a distinct failure condition, outside the two-outcome classification TD005-AI-009 defines. Traceability: TD005-CAP-012; ADR-011 (Runtime Failure Handling), by analogy - the certified corpus's own established pattern of treating a failed transition as a distinct, immutable Runtime Failure Event rather than forcing it into an existing outcome category.

All nineteen invariants are individually numbered with no gap; none is referenced elsewhere in this document only via a compressed range.

## 13. Architecture Decisions

**TD005-AD-001. Separate Certified Contract Registry from Certification Boundary Authority.**
Decision: TD005-CAP-001 and TD005-CAP-002 are realized as two distinct components (TD005-ARC-001, TD005-ARC-002), not one.
Context: both concern "what counts as certified," and could plausibly be combined into a single "Corpus Authority" component.
Alternatives considered: (a) a single combined component owning both enumeration and boundary; (b) the chosen two-component split.
Scientific justification: the one-primary-responsibility principle (Section 7); the boundary rule (what evidentiary forms qualify) and the corpus enumeration (which specific contracts currently qualify) are independently evolvable properties - the CGA itself rated both capabilities High risk but tracked their own missing elements independently (assembly mechanism versus boundary rule).
Traceability: TD005-CAP-001, TD005-CAP-002; TD005-FR-021.
Consequences: two components must stay consistent with each other (TD005-ARC-002 consumes TD005-ARC-001's own enumeration as its candidate space); a future change to the boundary rule does not require re-deriving the corpus enumeration, and vice versa.

**TD005-AD-002. Reference Baseline Authority Is Distinct From, Though Dependent On, the Certified Contract Registry.**
Decision: TD005-ARC-003 (Reference Baseline Authority) is a separate component from TD005-ARC-001/002, positioned in its own Reference layer.
Context: a "corpus" (what is certified) and a "reference instance" (one concrete execution/record representing certified behaviour for comparison) could be folded together.
Alternatives considered: (a) fold reference-baseline provenance into the Registry itself; (b) the chosen separate component.
Scientific justification: CAP-009's own Critical risk rating and independently unresolved status (source selection, immutability, reproducibility, none of which CAP-001 shares) show these mature independently; a corpus can be PARTIALLY AVAILABLE while a reference baseline built from it is entirely MISSING, as the CGA's own maturity assignments confirm.
Traceability: TD005-CAP-009; TD005-FR-018, TD005-FR-019, TD005-FR-021; OQ-002.
Consequences: Reference Baseline Authority may resolve at a different pace than the Registry; Architecture Readiness (Section 16) tracks each independently.

**TD005-AD-003. Deterministic Replay Controller Merges TD005-CAP-010 and TD005-CAP-011.**
Decision: TD005-ARC-011 realizes both TD005-CAP-010 (Environmental Determinism) and TD005-CAP-011 (Controlled-Condition and Replay Stability) as one component.
Context: this is the one deliberate capability-to-component merge in this Architecture (Section 6, methodology step 2).
Alternatives considered: (a) two separate components (an Environmental Determinism Monitor and a Controlled-Condition Enumerator); (b) the chosen single component.
Scientific justification: TD005-CAP-010 is fully AVAILABLE with zero missing elements and functions purely as one of several conditions TD005-CAP-011's own broader controlled-condition set must enforce; a standalone component for TD005-CAP-010 would be architecturally hollow (nothing left to architect), while TD005-CAP-011's own responsibility already subsumes it as one enforced condition among several.
Traceability: TD005-CAP-010, TD005-CAP-011; TD005-DEP-009, TD005-DEP-010, TD005-DEP-018.
Consequences: this is the only capability-count-to-component-count reduction in this Architecture; it is offset by the addition of TD005-ARC-022 (Section 8), keeping the total component count at twenty-two.

**TD005-AD-004. Execution-Environment Identity Recorder Remains Separate From the Deterministic Replay Controller.**
Decision: TD005-ARC-012 (sourced from TD005-CAP-022) is not folded into TD005-ARC-011, despite the CGA's own Section 10 noting Architecture "may reasonably choose" to do so.
Context: TD005-CAP-022 is explicitly cross-cutting, related to both TD005-CAP-009 (Reference) and TD005-CAP-011 (Replay) by the CGA's own Relationship subsections.
Alternatives considered: (a) fold into TD005-ARC-011 (Replay); (b) fold into TD005-ARC-003 (Reference); (c) the chosen standalone component.
Scientific justification: folding into either consumer would silently subordinate a capability the CGA itself deliberately left open (Optional Architecture priority, explicitly not decided in the CGA); a standalone component keeps the eventual fold-in-or-remain-standalone choice genuinely available to Specification rather than foreclosing it here.
Traceability: TD005-CAP-022; TD005-CON-004 (by scientific proximity).
Consequences: TD005-ARC-003 and TD005-ARC-011 each hold a reference to TD005-ARC-012's own output rather than owning a copy of it (Section 10, Ownership); Specification may still choose to physically co-locate this capability's own eventual mechanism with either consumer without an Architecture change.

**TD005-AD-005. Numeric/Categorical Comparator and Object-Identity Comparator Remain Two Separate Components.**
Decision: TD005-CAP-005 and TD005-CAP-006 are realized as two components (TD005-ARC-008, TD005-ARC-009), not merged.
Context: both concern "how are two observed values judged equal," a plausible merge candidate.
Alternatives considered: (a) a single "Value Comparator" component; (b) the chosen two-component split.
Scientific justification: the CGA's own Section 7.1 atomicity audit independently confirmed both capabilities are atomic and answer different scientific questions (per-value-type comparison policy versus identity-independence-in-general); merging would combine two independently-resolvable MISSING capabilities into one component whose own completion criteria would be conflated, violating the one-primary-responsibility principle.
Traceability: TD005-CAP-005, TD005-CAP-006; TD005-DEP-006, TD005-DEP-011, TD005-DEP-016.
Consequences: each component's own Specification-stage resolution (tolerance value; identity-independence enforcement mechanism) proceeds independently.

**TD005-AD-006. Coverage Constituted as Its Own Layer, Not Folded Into Classification.**
Decision: TD005-ARC-015 and TD005-ARC-016 occupy a distinct Coverage layer (Layer 6), positioned before, and advisory to, Classification (Layer 7), per TD005-AI-014.
Context: coverage auditing could plausibly be treated as an internal sub-responsibility of the Classification Engine.
Alternatives considered: (a) fold coverage auditing into the Classification Engine's own responsibilities; (b) the chosen distinct layer.
Scientific justification: coverage answers "can Classification ever detect a regression here at all" (a completeness question about the whole pipeline), categorically different from Classification's own "is this specific deviation a regression" question; conflating them would let a coverage gap silently masquerade as a classification non-finding rather than being surfaced as its own distinct, evidenced gap (the CGA's own AC-011 and four-module findings).
Traceability: TD005-CAP-015, TD005-CAP-016.
Consequences: a coverage gap is always independently visible in this Architecture's own output, never silently absorbed into an individual classification verdict.

**TD005-AD-007. Extension Points Formalized as an Explicit Architecture Layer.**
Decision: TD005-ARC-022 (Specification Extension Point Registry) exists as a dedicated Layer 10 component, aggregating every component's own Specification-deferred mechanism boundary.
Context: the CGA's own Section 11 names twelve distinct deferred mechanism decisions; these could be left implicit within each component's own description, as the CGA itself did.
Alternatives considered: (a) no dedicated extension architecture, leaving deferrals implicit in prose; (b) the chosen explicit registry component.
Scientific justification: without an explicit architectural home, Specification-deferred decisions risk becoming silent assumptions baked into a future component's own implementation rather than explicit, governed extension contracts; the governing task's own Domain J (Architecture Extension Points) explicitly requires this analysis.
Traceability: aggregate, twelve capabilities named in CGA Section 11 (Section 8, TD005-ARC-022's own Source capabilities field).
Consequences: this is the one component in this Architecture not sourced from a single capability; its own traceability is explicitly aggregate, stated as such rather than concealed (Section 15).

**TD005-AD-008. Regression Classification Engine's Exclusions Encoded as a Binding Invariant, Not Only Capability-Level Prose.**
Decision: CAP-012's own explicit exclusions (severity, waiver, disposition, remediation priority, business acceptability) are encoded as TD005-AI-009, a binding Architecture Invariant, not left as CGA-level documentation alone.
Context: the CGA already states these exclusions in its own TD005-CAP-012 entry; this Architecture could simply inherit that text without elevating it to invariant status.
Alternatives considered: (a) rely on the CGA's own prose alone; (b) elevate to a binding Architecture Invariant.
Scientific justification: an invariant, unlike prose, requires an explicit, governed Architecture Evolution Review (Implementation Baseline Principle IP-006) before any future stage may expand the Classification Engine's scope, closing a route by which scope creep could otherwise occur silently during Specification or Implementation.
Traceability: TD005-CAP-012 (CGA V1.1 Atomicity Review, Option B); TD005-AI-009.
Consequences: any future proposal to add severity ranking, waiver, or disposition to TD-005 requires an explicit Architecture amendment, not a Specification-level addition.

**TD005-AD-009. Repository Boundary Protection Retained as an Explicit Exclusion Component.**
Decision: TD005-ARC-021 exists as a zero-owned-information marker component, rather than omitting TD005-CAP-018 from this Architecture entirely.
Context: TD005-CAP-018 is OUTSIDE TD-005 SCOPE as a behavioral capability; a plausible alternative is to simply not architect it.
Alternatives considered: (a) omit entirely, since it is out of scope; (b) the chosen explicit marker component.
Scientific justification: the governing task's own Architecture Readiness requirement (Section 14) mandates every capability map to at least one component with no orphan; an explicit, empty-responsibility marker satisfies this without incorrectly implying TD-005 owns Repository Consolidation's own certified mechanism.
Traceability: TD005-CAP-018; RC-AD-004.
Consequences: Section 16 (Architecture Readiness) shows zero orphan capabilities, including the one OUTSIDE-TD-005-SCOPE capability, without this Architecture incorrectly absorbing Repository Consolidation's own scope.

**TD005-AD-010. Ten-Layer Architecture Extends the Seven-Layer Skeleton.**
Decision: the governing task's own seven layers (Foundational, Reference, Observation, Comparison, Classification, Evidence, Governance) are extended to ten by inserting Replay (between Reference and Observation), Coverage (between Comparison and Classification), and Extension (as a terminal, cross-cutting layer).
Context: the governing task's own required domains include Replay Control Architecture (D), Coverage Architecture (F), and Architecture Extension Points (J), none of which maps cleanly onto the seven-layer skeleton as given.
Alternatives considered: (a) retain exactly seven layers, folding Replay into Observation, Coverage into Classification, and Extension implicitly into Governance; (b) the chosen ten-layer extension.
Scientific justification: each of the three additional layers has genuinely distinct scientific content (Section 9) and is independently traceable to a required governing-task domain; folding them into adjacent layers would obscure, not clarify, their distinct architectural role, and the governing task's own instruction ("derive the final layering from repository evidence... do not assume this list is complete") explicitly authorizes this refinement.
Traceability: governing task Section 6 (Domains D, F, J), Section 8 (layer instruction).
Consequences: the layer count (ten) does not match the capability-class count (ten) by coincidence alone - both stem from the same underlying ten-domain requirement, but the two enumerations are independently derived (Section 9 layers from component prerequisite structure; CGA classes from capability-content grouping) and are not claimed to be identical in composition.

**TD005-AD-011. Governance Sequence Conformance Represented as a Component, Not Only as Narrative.**
Decision: TD005-ARC-019 exists as a component with zero owned runtime information.
Context: TD005-CAP-019 is fully AVAILABLE with no missing elements; a plausible alternative is to mention governance-sequence conformance in prose only, without a dedicated component.
Alternatives considered: (a) omit as a component, describe only in prose; (b) the chosen lightweight component.
Scientific justification: the same Architecture Readiness "no orphan capability" requirement as TD005-AD-009; a dedicated component also gives a future Architecture Evolution Review an explicit artifact to check against.
Traceability: TD005-CAP-019.
Consequences: Layer 1 (Foundational) includes one component (TD005-ARC-019) whose own primary output is a governance record rather than information consumed by the regression-detection data flow itself.

**TD005-AD-012. Behavioural Vocabulary Authority Represented as a Foundational Component Despite Being Fully Available.**
Decision: TD005-ARC-010 is a first-class Foundational-layer component, not implicit background context.
Context: TD005-CAP-021 is fully AVAILABLE; vocabulary could plausibly be treated as unstated shared assumption rather than an explicit component.
Alternatives considered: (a) leave vocabulary implicit; (b) the chosen explicit component.
Scientific justification: every Comparison-layer and Reference-layer component's own scientific rationale is stated in this vocabulary (Position, Side, Scale-In, Tick-Complete, and so on); an explicit, citable, versioned authority prevents a future component from silently drifting to an inconsistent term, directly extending TD005-AI-001's "sole authoritative source" pattern to terminology.
Traceability: TD005-CAP-021.
Consequences: any future vocabulary change requires an explicit update to TD005-ARC-010, triggering a review of every component whose own justification cites the changed term.

**TD005-AD-013. No New Runtime Coupling Introduced Into the Active Run Engine.**
Decision: every component observes the active Run Engine exclusively through TD005-ARC-005 (Non-Interference Observation Gateway); no component modifies, wraps, instruments, or subclasses any of the fourteen active modules.
Context: an alternative architecture could instrument active modules directly (for example, adding hooks inside `RunLoop.step()`) for richer observation.
Alternatives considered: (a) direct instrumentation of active modules; (b) the chosen single non-interfering gateway.
Scientific justification: TD005-CON-001 (Non-Interference) and TD005-CON-002 (No Alternative Runtime Path) both prohibit direct instrumentation; Repository Consolidation's own RC-SPEC-001 (Active Runtime Retention Contract) independently establishes a zero-tolerance no-change boundary for the same fourteen files from a second, independently-governed source, reinforcing rather than merely repeating the FRA's own constraint.
Traceability: TD005-CON-001, TD005-CON-002; RC-SPEC-001.
Consequences: any future observation need beyond what `RunLoop.step()`'s own return value exposes requires an explicit Architecture amendment (extending TD005-ARC-005's own boundary statement, per OQ-001's own continued Architecture-level disposition, Section 8), not an ad hoc instrumentation add.

All thirteen Architecture Decisions are individually numbered with no gap.

## 14. Architecture Risks

| Risk | Severity | Justification |
|---|---|---|
| Reference Baseline Authority (TD005-ARC-003) remains architecturally under-specified at the mechanism level | Critical | TD005-CAP-009 is Critical-risk MISSING; if Specification does not rigorously resolve source selection, immutability, and reproducibility, every downstream Classification result is invalid regardless of how well the rest of the Architecture is realized. |
| Behavioural Equivalence Authority and its dependents (TD005-ARC-006 through TD005-ARC-009) remain the Architecture's own most under-resolved cluster | Critical | If Specification defaults to the simplest available definition (byte/source identity) rather than genuine behavioural equivalence, TD005-AI-007 would be technically satisfied by a degenerate implementation, defeating the Architecture's own central scientific purpose (TD005-FR-020). |
| Regression Classification Engine (TD005-ARC-017) has no independent content of its own | Critical | It is wholly derived from TD005-ARC-002, TD005-ARC-006 through TD005-ARC-009, and TD005-ARC-015/016; any weakness in any one prerequisite propagates directly into the Classification verdict with no independent check. |
| Coverage layer (TD005-ARC-015, TD005-ARC-016) is advisory-only by design | High | If a future Specification or Implementation silently promotes coverage findings into classification authority, TD005-AI-014 would be violated without an explicit Architecture change being visible to review. |
| Execution-Environment Identity Recorder (TD005-ARC-012) remains Optional-priority | Medium | If Architecture Evolution defers it indefinitely, TD005-CAP-022's own narrow-but-real exposure (library/interpreter version drift misclassified as behavioural regression) persists unmitigated. |
| Specification Extension Point Registry (TD005-ARC-022) depends on Specification-stage discipline this Architecture cannot itself enforce mechanically | Medium | A future Specification could make an unrecorded mechanism choice directly inside a component's own future implementation, bypassing the registry; this Architecture provides the contract, not an enforcement mechanism. |
| Governance Sequence Conformance Marker (TD005-ARC-019) and Behavioural Vocabulary Authority (TD005-ARC-010) own no missing elements today | Medium | A future repository change (vocabulary drift, governance-sequence skip) would silently invalidate either without this Architecture defining its own re-verification trigger, since that trigger is itself deferred to Specification (TD005-AI-016). |
| Ten-layer extension of the seven-layer skeleton could be misread as architectural over-design by a future reviewer | Low | Mitigated by this document's own explicit TD005-AD-010 justification; a documentation-clarity risk only, not a scientific-correctness risk. |

## 15. Traceability

### 15.1 Capability-to-Component Traceability

| CGA Capability | Architecture Component |
|---|---|
| TD005-CAP-001 | TD005-ARC-001 |
| TD005-CAP-002 | TD005-ARC-002 |
| TD005-CAP-003 | TD005-ARC-006 |
| TD005-CAP-004 | TD005-ARC-007 |
| TD005-CAP-005 | TD005-ARC-008 |
| TD005-CAP-006 | TD005-ARC-009 |
| TD005-CAP-007 | TD005-ARC-004 |
| TD005-CAP-008 | TD005-ARC-005 |
| TD005-CAP-009 | TD005-ARC-003 |
| TD005-CAP-010 | TD005-ARC-011 |
| TD005-CAP-011 | TD005-ARC-011 |
| TD005-CAP-012 | TD005-ARC-017 |
| TD005-CAP-013 | TD005-ARC-013 |
| TD005-CAP-014 | TD005-ARC-014 |
| TD005-CAP-015 | TD005-ARC-015 |
| TD005-CAP-016 | TD005-ARC-016 |
| TD005-CAP-017 | TD005-ARC-020 |
| TD005-CAP-018 | TD005-ARC-021 |
| TD005-CAP-019 | TD005-ARC-019 |
| TD005-CAP-020 | TD005-ARC-018 |
| TD005-CAP-021 | TD005-ARC-010 |
| TD005-CAP-022 | TD005-ARC-012 (primary); TD005-ARC-003, TD005-ARC-011 (relationship consumers, Section 8) |

All twenty-two capabilities map to at least one component; TD005-ARC-022 additionally traces to twelve capabilities in aggregate (Section 8, Section 13, TD005-AD-007), not shown as a row above since it is not that table's own single-capability format.

### 15.2 FRA Functional Requirement to Component Traceability

| FRA Functional Requirement | Governing Components |
|---|---|
| TD005-FR-001 | TD005-ARC-001, TD005-ARC-007, TD005-ARC-016 |
| TD005-FR-002 | TD005-ARC-009, TD005-ARC-011 |
| TD005-FR-003 | TD005-ARC-007, TD005-ARC-004 |
| TD005-FR-004 | TD005-ARC-004, TD005-ARC-005 |
| TD005-FR-005 | TD005-ARC-009, TD005-ARC-004, TD005-ARC-005 |
| TD005-FR-006 | TD005-ARC-007, TD005-ARC-004, TD005-ARC-005, TD005-ARC-015 |
| TD005-FR-007 | TD005-ARC-007, TD005-ARC-008, TD005-ARC-016 |
| TD005-FR-008 | TD005-ARC-007, TD005-ARC-008, TD005-ARC-016 |
| TD005-FR-009 | TD005-ARC-007, TD005-ARC-008, TD005-ARC-016 |
| TD005-FR-010 | TD005-ARC-007, TD005-ARC-008, TD005-ARC-016 |
| TD005-FR-011 | TD005-ARC-008 |
| TD005-FR-012 | TD005-ARC-008 |
| TD005-FR-013 | TD005-ARC-008, TD005-ARC-004, TD005-ARC-011, TD005-ARC-015 |
| TD005-FR-014 | TD005-ARC-001, TD005-ARC-008, TD005-ARC-004, TD005-ARC-015 |
| TD005-FR-015 | TD005-ARC-008, TD005-ARC-004 |
| TD005-FR-016 | TD005-ARC-008 |
| TD005-FR-017 | TD005-ARC-007, TD005-ARC-008 |
| TD005-FR-018 | TD005-ARC-002, TD005-ARC-003, TD005-ARC-011, TD005-ARC-017 |
| TD005-FR-019 | TD005-ARC-013, TD005-ARC-014, TD005-ARC-018 |
| TD005-FR-020 | TD005-ARC-006, TD005-ARC-017 |
| TD005-FR-021 | TD005-ARC-002, TD005-ARC-003, TD005-ARC-017 |
| TD005-FR-022 | TD005-ARC-007, TD005-ARC-014, TD005-ARC-018 |

All twenty-two Functional Requirements individually trace to at least one component.

### 15.3 FRA Constraint to Component Traceability

| FRA Constraint | Governing Components |
|---|---|
| TD005-CON-001 | TD005-ARC-005 |
| TD005-CON-002 | TD005-ARC-005, TD005-ARC-020 |
| TD005-CON-003 | TD005-ARC-014, TD005-ARC-020 |
| TD005-CON-004 | TD005-ARC-011, TD005-ARC-012 |

All four Constraints individually trace to at least one component.

### 15.4 FRA Deferred Obligation to Component Traceability

| FRA Deferred Obligation | Governing Components |
|---|---|
| Section 13.1, Active Module Coverage Obligation | TD005-ARC-015, TD005-ARC-016, TD005-ARC-020 |
| Section 13.2, Repository-Integrity Regression Obligation | TD005-ARC-021 |

Both Deferred Obligations individually trace to at least one component.

### 15.5 SDA Dependency to Component Traceability

| SDA Dependency | Governing Component |
|---|---|
| TD005-DEP-001 | TD005-ARC-001 |
| TD005-DEP-002 | TD005-ARC-002 |
| TD005-DEP-003 | TD005-ARC-001 |
| TD005-DEP-004 | TD005-ARC-006 |
| TD005-DEP-005 | TD005-ARC-007 |
| TD005-DEP-006 | TD005-ARC-008 |
| TD005-DEP-007 | TD005-ARC-004 |
| TD005-DEP-008 | TD005-ARC-005 |
| TD005-DEP-009 | TD005-ARC-011 |
| TD005-DEP-010 | TD005-ARC-011 |
| TD005-DEP-011 | TD005-ARC-009 |
| TD005-DEP-012 | TD005-ARC-003 |
| TD005-DEP-013 | TD005-ARC-003 |
| TD005-DEP-014 | TD005-ARC-003 |
| TD005-DEP-015 | TD005-ARC-007 |
| TD005-DEP-016 | TD005-ARC-008 |
| TD005-DEP-017 | TD005-ARC-007 |
| TD005-DEP-018 | TD005-ARC-011 |
| TD005-DEP-019 | TD005-ARC-005 |
| TD005-DEP-020 | TD005-ARC-015 |
| TD005-DEP-021 | TD005-ARC-016 |
| TD005-DEP-022 | TD005-ARC-016 |
| TD005-DEP-023 | TD005-ARC-013 |
| TD005-DEP-024 | TD005-ARC-014 |
| TD005-DEP-025 | TD005-ARC-018 |
| TD005-DEP-026 | TD005-ARC-018 |
| TD005-DEP-027 | TD005-ARC-014, TD005-ARC-018 |
| TD005-DEP-028 | TD005-ARC-020 |
| TD005-DEP-029 | TD005-ARC-020 |
| TD005-DEP-030 | TD005-ARC-021 |
| TD005-DEP-031 | TD005-ARC-020 |
| TD005-DEP-032 | TD005-ARC-010 |
| TD005-DEP-033 | TD005-ARC-019 |

All thirty-three Scientific Dependencies individually trace to at least one component.

## 16. Architecture Readiness

Every one of the twenty-two accepted CGA capabilities maps to at least one architectural component (Section 15.1). No orphan capability exists. Specifically:

- The three AVAILABLE capabilities (TD005-CAP-010, TD005-CAP-019, TD005-CAP-021) each map to a component (TD005-ARC-011 in part, TD005-ARC-019, TD005-ARC-010) that formalizes the already-satisfied property as a stable architectural interface, per TD005-AD-003, TD005-AD-011, TD005-AD-012.
- The seven PARTIALLY AVAILABLE capabilities (TD005-CAP-001, TD005-CAP-004, TD005-CAP-007, TD005-CAP-008, TD005-CAP-013, TD005-CAP-015, TD005-CAP-017) each map to a component whose own Missing Elements (CGA Section 9) are carried forward explicitly as unresolved fields in that component's own description (Section 8) or as a named Specification input (Section 17).
- The eleven MISSING capabilities (TD005-CAP-002, TD005-CAP-003, TD005-CAP-005, TD005-CAP-006, TD005-CAP-009, TD005-CAP-011, TD005-CAP-012, TD005-CAP-014, TD005-CAP-016, TD005-CAP-020, TD005-CAP-022) each map to a component whose own architecture (responsibilities, inputs, outputs, owned information, constraints) is fully defined by this document even though the underlying capability itself remains unresolved at the mechanism level - this is precisely what "the Architecture closes the gap" means at this stage: the component's own contract exists, its own mechanism does not yet.
- The one OUTSIDE-TD-005-SCOPE capability (TD005-CAP-018) maps to an explicit boundary-marker component (TD005-ARC-021, TD005-AD-009) rather than being silently omitted.

Every capability the CGA's own Section 10 (Architecture Readiness) marked Mandatory is realized by a fully-specified component in this Architecture (Section 8). Every capability marked Optional is realized by a component whose own constraints explicitly permit Specification-stage resolution without an Architecture amendment (TD005-ARC-012, TD005-ARC-013, TD005-ARC-014, TD005-ARC-020's own drift-sensitivity portion). Every capability marked Deferred (already AVAILABLE or OUTSIDE SCOPE) is realized as described above. This Architecture is therefore complete relative to the accepted CGA: it closes every gap the CGA identified, at the architecture level, without prematurely resolving any Specification-level mechanism choice (Section 17).

## 17. Specification Inputs

Architecture -> Specification handover. Each item below is a named, open decision this Architecture deliberately does not resolve, each attached to its own owning component (TD005-ARC-022, Section 8):

- TD005-ARC-001's exact corpus-enumeration mechanism (format, location, maintenance process).
- TD005-ARC-002's per-contract-type certification-boundary application rule.
- TD005-ARC-003's exact reference-reproduction mechanism (source selection between historical commit and freshly-established baseline; immutability-or-governed-change procedure).
- TD005-ARC-007's exact trajectory representation format.
- TD005-ARC-008's exact tolerance value(s) and comparison implementation.
- TD005-ARC-011's exact controlled-condition enumeration mechanism.
- TD005-ARC-012's exact resolution (whether it remains standalone or is folded into TD005-ARC-003 or TD005-ARC-011's own future mechanism, per TD005-AD-004).
- TD005-ARC-013's exact adoption of the SDA's own four evidence-refinement elements into a binding schema.
- TD005-ARC-014's exact persistence format, retention/expiry policy, and cross-stage continuity mechanism.
- TD005-ARC-016's exact coverage mechanism and coverage-concept choice (module, contract, domain, state-transition, event, requirement, path, risk-based, or combination).
- TD005-ARC-017's exact classification procedure (the concrete algorithm composing TD005-ARC-002 and TD005-ARC-006 through TD005-ARC-009 into one verdict).
- TD005-ARC-018's exact application mechanics (execution-time budget; pre-run-versus-post-run invocation) across the six Long-Duration-Validation stages (OQ-004, transferred unresolved from the SDA and CGA).
- TD005-ARC-020's scope-drift-sensitivity mechanism (Optional priority; currently unresolved; OQ-003's own unresolved half, transferred unchanged).
- OQ-005 (test-code location), unchanged from the SDA's and CGA's own disposition, transferred to Specification via TD005-ARC-022.
- Pipeline initialization and shutdown lifecycle (which component, if any, starts and stops the regression-detection pipeline itself, as distinct from the already-governed active Run Engine lifecycle); no accepted FRA requirement, SDA dependency, or CGA capability currently names this concern, and this Architecture does not invent a new component for it (Section 6, Hidden Architecture Assumption Review, this review's own V1.1 finding).

None of these is solved in this document; each is named so it is not silently lost between governance stages, per TD005-AI-016.

## 18. Completion Criteria

This Architecture Analysis is complete and ready to serve as the accepted Working Baseline for Specification when:

- Every architectural component is derived exclusively from the accepted FRA, SDA, and CGA, with no component originating from an implementation idea: verified by construction (Section 8, every component's own Source capabilities/dependencies/requirements fields; TD005-ARC-022's own aggregate origin explicitly disclosed rather than concealed, TD005-AD-007).
- Every component carries all twelve required fields (ID, Name, Purpose, Responsibilities, Inputs, Outputs, Owned information, External dependencies, Architectural constraints, Scientific justification, Source capabilities, Source dependencies, Source requirements): verified by construction (Section 8).
- Every component has one primary responsibility: verified by construction; the one merge (TD005-AD-003) and the one aggregate-origin component (TD005-AD-007) are each explicitly justified, not silent.
- At least the ten named architectural domains are analyzed, refined where evidence justified it: verified by construction (Section 8, Domains A through J each represented).
- The layered architecture is acyclic and every component's layer placement is justified: verified (Section 9, explicit belongs-here justification per layer; External dependencies in Section 8 resolve only to the same or a lower layer).
- Information flow, ownership, allowed/forbidden flow, lifecycle, and immutability are fully specified without naming a storage technology: verified (Section 10).
- Component interaction is described logically (interfaces, preconditions, postconditions, sequencing) without defining an API: verified (Section 11).
- Architecture Invariants are individually numbered, derived from FRA Constraints, SDA risk findings, and CGA exclusions, not from convenience: verified (Section 12, nineteen invariants, each individually traced).
- Architecture Decisions are individually numbered, each with a genuine rejected alternative and scientific justification: verified (Section 13, thirteen decisions).
- Architecture Risks are classified and justified: verified (Section 14, eight risks, Low through Critical).
- Every FRA Functional Requirement, Constraint, and Deferred Obligation, every SDA Dependency, and every CGA Capability traces to at least one architectural component, with no gap: verified (Section 15, five traceability tables).
- Every capability gap is closed at the architecture level, with no orphan capability: verified (Section 16).
- Specification Inputs are a concise list directly originating from architecture-level deferrals, not new content: verified (Section 17).
- No implementation, test script, pytest code, fixture, CI/CD configuration, directory implementation, concrete algorithm, or configuration file is created anywhere in this document: verified by construction (Section 8 through Section 17 contain no such content).

All criteria above are satisfied by this document.

## 19. Conclusion

This Architecture Analysis defines twenty-two individually numbered architectural components (TD005-ARC-001 through TD005-ARC-022) across ten architectural domains and ten architectural layers, closing every one of the twenty-two capability gaps the accepted CGA identified without introducing architecture unjustified by the accepted baselines. Nineteen Architecture Invariants and thirteen Architecture Decisions formalize the scientific constraints and design choices this Architecture depends on, each individually traceable to the accepted FRA, SDA, or CGA. The central scientific risk this Architecture inherits from the CGA - the Regression Classification Engine's own dependence on the Reference Baseline Authority and the Behavioural Equivalence Authority, both still MISSING at the mechanism level - is represented explicitly (TD005-ARC-003, TD005-ARC-006 through TD005-ARC-009, TD005-ARC-017; Section 14, both rated Critical) rather than concealed by premature architectural completeness. Repository boundaries are explicitly preserved: this Architecture does not absorb Repository Consolidation's own certified Executor-namespace mechanism (TD005-ARC-021, TD005-AI-012), and no component introduces new coupling into the fourteen active Run Engine modules beyond the single Non-Interference Observation Gateway (TD005-ARC-005, TD005-AD-013). This document selects no test framework, comparison algorithm, storage mechanism, persistence implementation, or configuration; fifteen distinct Specification-level decisions are named explicitly and handed to a future Specification stage (Section 17) rather than resolved here. Every FRA requirement, Constraint, Deferred Obligation, SDA dependency, and CGA capability traces to at least one architectural component, with no gap (Section 15), and no capability gap remains architecturally unaddressed (Section 16). A targeted Editorial and Scientific Review (V1.1) independently rebuilt the full component-dependency graph, found and corrected two genuine Layer-ordering inconsistencies, added two invariants closing a reference-bootstrap ambiguity and a component-failure-propagation gap, and tightened several components' own ownership fields, without altering the component count, layer count, Architecture Decision count, or any capability mapping. This document is ready to serve as the accepted Working Baseline for a future TD-005 Specification.
