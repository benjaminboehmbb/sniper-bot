Document Class:
Specification

Document ID:
TD005-SPEC

Title:
TD-005 Automated Regression Test Suite - Specification

Version:
V1.1

Date:
2026-07-14

Status:
DRAFT - EDITORIAL AND SCIENTIFIC REVIEW COMPLETED

Storage Location:
docs/architecture/specifications/

Filename:
TD_005_AUTOMATED_REGRESSION_TEST_SUITE_SPECIFICATION_V1_2026-07-14.md

Technical Debt Item:
TD-005 - Automated Regression Test Suite (docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md)

Accepted Working Baselines:
docs/architecture/analysis/TD_005_AUTOMATED_REGRESSION_TEST_SUITE_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-14.md, Version V1.1, Status DRAFT - EDITORIAL AND SCIENTIFIC REVIEW COMPLETED
docs/architecture/analysis/TD_005_AUTOMATED_REGRESSION_TEST_SUITE_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-14.md, Version V1.1, Status DRAFT - CORRECTIVE SCIENTIFIC REVIEW COMPLETED
docs/architecture/analysis/TD_005_AUTOMATED_REGRESSION_TEST_SUITE_CAPABILITY_GAP_ANALYSIS_V1_2026-07-14.md, Version V1.1, Status DRAFT - EDITORIAL AND SCIENTIFIC REVIEW COMPLETED
docs/architecture/design/TD_005_AUTOMATED_REGRESSION_TEST_SUITE_ARCHITECTURE_V1_2026-07-14.md, Version V1.1, Status DRAFT - EDITORIAL AND SCIENTIFIC REVIEW COMPLETED

Scope:
Implementation-neutral specification only. No Python code, pytest tests, fixtures, CI/CD, directory implementation, storage implementation, persistence implementation, serialization implementation, APIs, or concrete algorithms.

Dependencies:
- docs/architecture/analysis/TD_005_AUTOMATED_REGRESSION_TEST_SUITE_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-14.md
- docs/architecture/analysis/TD_005_AUTOMATED_REGRESSION_TEST_SUITE_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-14.md
- docs/architecture/analysis/TD_005_AUTOMATED_REGRESSION_TEST_SUITE_CAPABILITY_GAP_ANALYSIS_V1_2026-07-14.md
- docs/architecture/design/TD_005_AUTOMATED_REGRESSION_TEST_SUITE_ARCHITECTURE_V1_2026-07-14.md
- docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md
- docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md
- docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md
- docs/architecture/REPOSITORY_CONSOLIDATION_ARCHITECTURE_V1_2026-07-14.md
- docs/architecture/REPOSITORY_CONSOLIDATION_SPECIFICATION_V1_2026-07-14.md
- docs/architecture/certification/REPOSITORY_CONSOLIDATION_FINAL_CERTIFICATION_V1_2026-07-14.md
- requirements.txt

Referenced By:
- future TD-005 Implementation (not yet created)

Supersedes:
None. This is the first Specification for TD-005.

Language:
English

Encoding:
ASCII

---

# TD-005 Automated Regression Test Suite - Specification

## 1. Metadata

See front matter above.

## 2. Executive Summary

### 2.1 Revision History

- **V1.0 (2026-07-14).** Initial Specification. Twenty-two Specification Objects, twenty-two Specification Invariants, four Specification Decisions, across twelve specification domains.
- **V1.1 (2026-07-14).** Editorial and Scientific Review. Independently re-verified repository evidence (branch, HEAD, active module set, all four accepted Working Baselines) fresh against the same evidence gathered at V1.0. Corrected a range-citation defect in TD005-SO-001's own Traceability field: an unqualified "TD005-FR-001 through TD005-FR-022 (all)" and "TD005-CON-001 through TD005-CON-004" claim was contradicted by this document's own Section 19.1/19.2 composed traceability tables, which show TD005-SO-001 as a direct governing object for only TD005-FR-001 and TD005-FR-014, and for no Constraint; replaced with an individually-supported direct citation plus an honest, qualified indirect-relationship statement mirroring TD005-SO-009's own established phrasing, and removed the unsupported Constraint claim entirely. Resolved an internal consistency gap in Evidence Specification: the eight-required-elements completeness rule (TD005-SO-016, TD005-SI-016) could never be satisfied for an Indeterminate or Invalid Comparison outcome when the very condition producing that outcome (a certification-boundary or coverage gap; an upstream component's failure to produce output) also renders one or more elements structurally unobtainable; added an explicit "reasoned unavailability marker" accommodation to TD005-SO-016, TD005-SI-016, Section 12, and TD005-SD-004's own Consequences, preserving the completeness discipline without creating an unsatisfiable requirement. Closed an Implementation Readiness registry gap: OQ-005 (regression-capability artifact/test-code location), already traced to TD005-SO-020 and TD005-SO-021 in Section 19.4, was not recorded as an explicit Open Mechanism entry in Section 18's own table, as TD005-SI-022 requires of every Implementation-stage mechanism choice; added to TD005-SO-021's own Open Mechanism cell. Corrected two state-model precision issues: removed a redundant duplicate-state listing in TD005-SO-003 ("Established (post-revision)"), already fully covered by the existing Revising -> Established transition; made the Classification re-evaluation transition (TD005-SO-013) an explicit legal transition rather than leaving it inferable only from the negation in the Illegal clause. A full Specification Object atomicity review (all twenty-two, with particular attention to the eight the governing task named) found no split scientifically necessary: every merge or non-split decision traces to an Architecture-level decision already made and reviewed (TD005-AD-003, TD005-AD-004, TD005-AD-009), which this Specification correctly preserves 1:1 rather than re-opening. A sixteen-item hidden-specification-assumption review found the great majority already adequately specified through existing state-model and invariant discipline (session-scoped bounded lifecycles, TD005-SD-003; per-comparison boundary-rule version recording, TD005-SO-002; scope re-evaluation at session start, TD005-SI-020); one item (pipeline initialization and shutdown) was confirmed correctly out of TD-005 scope, consistent with the Architecture's own explicit finding that no accepted FRA requirement, SDA dependency, or CGA capability names this concern. No Specification Object was split or merged; no Specification Invariant or Specification Decision was added or removed; the twenty-two Specification Object, twenty-two Specification Invariant, and four Specification Decision counts are unchanged. No architecture, capability, dependency, or functional requirement was reinterpreted. This document remains implementation-neutral: no Python code, pytest/unittest selection, API, concrete algorithm, concrete tolerance value, data structure, serialization format, storage technology, CI/CD design, or concrete directory implementation was introduced by this revision. **Final QA Certification Review (same V1.1, no V1.2 created).** An independent, mechanical re-verification (fresh AST-based import closure, fresh `git status --short`, fresh re-read of the FRA/SDA/CGA/Architecture and every referenced Baseline/Register/Repository-Consolidation document) found the document's own scientific content, traceability, state models, and implementation-neutrality boundary fully intact with zero objective defects, and one minor, self-contained editorial defect: Section 5, Item 1's own "shows exactly four entries" claim arithmetically contradicted its own enumeration (1 modification + 4 untracked baselines = 5, not 4). Corrected to "five entries," with a clarifying note that the Specification file's own later appearance as a sixth `git status --short` entry is expected and unrelated. No Specification Object, Invariant, or Decision was added, removed, split, or merged; no traceability mapping changed.

This Specification is the normative technical contract between the accepted TD-005 Architecture (V1.1) and a future Implementation. It defines twenty-two individually numbered Specification Objects (TD005-SO-001 through TD005-SO-022), one for each of the twenty-two accepted Architecture Components, organized into twelve specification domains - an evidence-driven extension of the eleven-domain skeleton the governing task names (A through K), with one additional domain (L, Repository Boundary Protection) added because two Architecture Components (TD005-ARC-020, TD005-ARC-021) have no coherent home in the eleven given domains, mirroring the Architecture's own precedent of extending a given skeleton when required (TD005-SD-002). Every Specification Object states its own purpose, scope, inputs, outputs, preconditions, postconditions, required and forbidden behaviour, valid and invalid states, state transitions, observable properties, and traceability. Twenty-two Specification Invariants (TD005-SI-001 through TD005-SI-022) and four Specification Decisions (TD005-SD-001 through TD005-SD-004) are derived, each individually traceable to the accepted FRA, SDA, CGA, or Architecture. Every one of the twenty-two Architecture Components is fully specified; no orphan Architecture Component exists (Section 17). This document selects no test framework, comparison algorithm, storage mechanism, persistence implementation, serialization format, or concrete numeric tolerance; every such choice remains explicitly named and deferred to Implementation (Section 18).

## 3. Accepted Inputs

Read in full and treated as binding, unmodified inputs:

- **FRA V1.1** (DRAFT - EDITORIAL AND SCIENTIFIC REVIEW COMPLETED): twenty-two Functional Requirements, four Constraints, two Deferred Specification and Coverage Obligations, six Open Questions.
- **SDA V1.1** (DRAFT - CORRECTIVE SCIENTIFIC REVIEW COMPLETED): thirty-three Scientific Dependencies.
- **CGA V1.1** (DRAFT - EDITORIAL AND SCIENTIFIC REVIEW COMPLETED): twenty-two Capabilities across ten capability classes.
- **Architecture V1.1** (DRAFT - EDITORIAL AND SCIENTIFIC REVIEW COMPLETED): twenty-two Architecture Components (TD005-ARC-001 through TD005-ARC-022) across ten architectural layers, nineteen Architecture Invariants (TD005-AI-001 through TD005-AI-019), thirteen Architecture Decisions (TD005-AD-001 through TD005-AD-013), and fifteen named Specification Inputs (Section 17 of the Architecture).

No FRA requirement, SDA dependency, CGA capability, or Architecture component, invariant, decision, layer, or traceability mapping is altered, reinterpreted, merged, removed, or added by this document. This Specification translates the accepted Architecture's own components into behaviourally complete Specification Objects; it does not re-derive the Architecture itself.

## 4. Objective

To completely specify the behaviour required to implement the accepted TD-005 Architecture, without defining implementation mechanisms. This Specification is the normative technical contract between Architecture and Implementation: every requirement in this document is either directly implementable behaviour or an explicitly named, deferred mechanism choice. It creates no Python code, pytest tests, fixtures, CI/CD configuration, directory implementation, storage implementation, persistence implementation, serialization implementation, APIs, or concrete algorithms.

## 5. Repository Evidence

Independently re-verified immediately before drafting this document, not assumed from the FRA, SDA, CGA, Architecture, or any prior analysis:

1. **Branch and HEAD.** Branch `run-engine-consolidation-safety`; HEAD `8952b1cba42506e4126e57ee89c59934f3d48b71`. `git status --short` shows exactly five entries: the pre-existing, unrelated modification to `docs/capabilities/SGF_013_SCIENTIFIC_BEHAVIOUR_REPRESENTATION_2026-06-26.md`, and the four untracked accepted TD-005 Working Baselines (FRA, SDA, CGA, Architecture). No other local change exists. (A sixth entry, this Specification file itself, is naturally added to `git status --short` as this document is created; it did not yet exist at the moment this evidence item was independently re-verified.)
2. **Active Run Engine module set.** A freshly, independently authored AST-based import closure from `run_engine.main` reproduces exactly: 18 total `.py` files under `run_engine/`, 14 active, 4 inactive RETAIN-Deferred-Scope. Identical to every prior independent derivation across the FRA, the SDA, the CGA, the Architecture, and the Repository Consolidation governance chain.
3. **`docs/architecture/specifications/`.** Re-confirmed as an established, pre-existing repository convention (already holding P1-02A, P1-03, P1-03A, P1-04, and other prior Specification documents), unlike the Architecture's own newly-introduced `docs/architecture/design/` location; this Specification's own placement at the exact path the governing task specifies is fully consistent with, not a departure from, existing repository convention.
4. **Architecture Baseline, Implementation Baseline, Technical Debt Register, Repository Consolidation documents.** Each re-opened; the specific facts this Specification's own behavioural contracts rely on (ADR-009's Lifecycle Transition Table and Scientific Definitions, ADR-010's Stage Ordering, ADR-011's Runtime Failure Handling, the Implementation Baseline's own Long-Duration-Validation six-stage sequence, RC-SPEC-001's Active Runtime Retention Contract, TD-004/005/007 Register status) are re-confirmed present and unchanged from the Architecture's own citations, which were themselves independently re-verified during the preceding Final QA Certification Review of the Architecture.
5. **`requirements.txt`, `tests/`, `tools/`.** Re-confirmed unchanged: no test framework in `requirements.txt`; zero files under `tests/` (only the empty, untracked `tests/ssi/` structure); `tools/repository_consolidation/verify_repository_consolidation.py` remains structure-only.

No Architecture statement is carried over unverified; every fact this Specification's own objects, invariants, and decisions rely on was independently re-confirmed above or is explicitly cited to its own accepted-baseline source.

## 6. Specification Principles

- **Traceability-first.** No Specification statement exists without derivation from one or more accepted FRA requirements, Constraints, Deferred Obligations, SDA Dependencies, CGA Capabilities, Architecture Components, Architecture Decisions, or Architecture Invariants (Section 19). This is itself formalized as TD005-SI-001.
- **One specification responsibility per object.** Every Specification Object corresponds to exactly one Architecture Component, preserving the Architecture's own one-primary-responsibility discipline; no Specification Object is merged, split, or newly invented beyond the twenty-two Architecture Components already establish.
- **Behaviour, not mechanism.** Every Specification Object states required and forbidden behaviour, valid and invalid states, and observable properties - never a chosen algorithm, data structure, storage technology, or framework. Where the Architecture already named a mechanism as an open Specification Input, this document states the mechanism's own required properties without selecting it (Section 18).
- **No premature narrowing.** Where a genuine range of valid mechanisms could satisfy a behavioural contract, this Specification states the contract, not the narrowest satisfying mechanism, preserving Implementation's own freedom to choose within the specified bounds.
- **State-model completeness.** Every Specification Object's own state model names every reachable state, every legal transition, and at least the most consequential illegal transitions, so Implementation can determine conformance without guessing.
- **No implicit exclusion.** Where the Architecture or CGA already named an explicit exclusion (severity, waiver, disposition, remediation priority, business acceptability; Repository Consolidation's own Executor-namespace protection), this Specification restates the exclusion at the behavioural-contract level, not merely by reference.

## 7. Specification Objects

Twenty-two individually numbered Specification Objects, one per accepted Architecture Component, across twelve specification domains. Each states: Purpose, Scope, Inputs, Outputs, Preconditions, Postconditions, Required behaviour, Forbidden behaviour, Valid states, Invalid states, State transitions, Observable properties, Traceability.

### Domain A - Certified Contract Corpus

**TD005-SO-001. Certified Contract Corpus Specification.**
Purpose: specify the behaviour required to expose the certified-contract corpus as a single, enumerable, authoritative reference.
Scope: the enumeration act itself and its own reproducibility and drift-detection behaviour; not the corpus's own storage format.
Inputs: the Architecture Baseline, the Implementation Baseline, the six certified units' own Final Certifications, the Technical Debt Register.
Outputs: an enumerable certified-contract set; a membership/exclusion determination for any candidate; a drift/ambiguity signal when the corpus's own composition changes.
Preconditions: the Architecture Baseline and the six certified units exist and are each independently CERTIFIED.
Postconditions: every enumeration act, given the same inputs, SHALL produce the same enumerable set (reproducibility); every candidate has a determinate membership status.
Required behaviour: re-derive the enumeration from primary repository evidence on every invocation, or from a cached representation whose own reproducibility against primary evidence is independently verifiable on demand (TD005-SI-002); report drift explicitly when a re-derivation differs from a prior enumeration.
Forbidden behaviour: treating a partial, filtered, or cached-and-unverifiable view as the complete corpus; silently absorbing a new certified unit into the enumeration without a corresponding drift signal.
Valid states: Uninitialized; Enumerated; Drift-Detected; Re-Enumerated.
Invalid states: Partially-Enumerated-and-Consumed (a consumer reading the corpus before enumeration completes).
State transitions: Uninitialized -> Enumerated (on successful enumeration). Enumerated -> Drift-Detected (a future certified unit is added or amended). Drift-Detected -> Re-Enumerated (a fresh enumeration is performed and reconciled). Illegal: Uninitialized -> Drift-Detected (drift cannot be detected before a first enumeration exists); Enumerated -> Uninitialized (the corpus is never un-enumerated).
Observable properties: the current enumeration; the corpus's own last-verified timestamp or provenance marker; the drift status.
Traceability: TD005-ARC-001; TD005-CAP-001; TD005-DEP-001, TD005-DEP-003; TD005-FR-001, TD005-FR-014 (direct, per Section 19.1); all twenty-two Functional Requirements (indirectly, as the foundational corpus every requirement's own regression evaluation presupposes, the same qualified form of claim TD005-SO-009 makes for the Behavioural Vocabulary).

**TD005-SO-002. Certification Boundary Specification.**
Purpose: specify the behaviour required to determine unambiguously whether a candidate behavioural contract counts as "certified."
Scope: the boundary rule's own application behaviour; not the rule's own concrete evidentiary-form list (an Implementation-adjacent refinement, Section 18).
Inputs: a candidate contract or behavioural claim; the corpus enumeration (TD005-SO-001).
Outputs: a certification-status determination (certified / not certified) for any candidate.
Preconditions: the corpus enumeration (TD005-SO-001) is in the Enumerated state.
Postconditions: the same candidate, evaluated twice against the same boundary-rule version, SHALL yield the same determination.
Required behaviour: apply exactly one boundary-rule version to any given determination; record which boundary-rule version produced a given determination.
Forbidden behaviour: applying different boundary-rule interpretations to different candidates within the same enumeration state; silently reinterpreting the rule without a recorded revision.
Valid states: Undefined; Defined; Revised.
Invalid states: Ambiguous (a candidate for which the rule yields no determinate answer under its own current definition - this SHALL NOT occur; if it does, it is a defect in the rule's own definition, not a valid outcome).
State transitions: Undefined -> Defined (the rule is first established). Defined -> Revised (a governed revision changes the rule). Illegal: Defined -> Undefined (the rule, once defined, is never un-defined); Revised -> Defined-with-prior-version (a revision is never silently reverted).
Observable properties: the current boundary-rule version; the determination history (which version produced which determination, for audit).
Traceability: TD005-ARC-002; TD005-CAP-002; TD005-DEP-002; TD005-FR-021, TD005-FR-018, TD005-FR-020.

### Domain B - Reference Baseline

**TD005-SO-003. Reference Baseline Specification.**
Purpose: specify the behaviour required to establish a scientifically valid, immutable-or-governed, reproducible reference baseline.
Scope: the establishment, governance, and reproducibility behaviour of the baseline record itself; not its own storage format or the concrete source-selection choice (Implementation-adjacent, Section 18).
Inputs: the corpus enumeration (TD005-SO-001); the boundary determination (TD005-SO-002); one Replay Session's own captured trajectory (TD005-SO-004), used exactly once as the reference capture; one Execution-Environment Identity record (TD005-SO-005).
Outputs: one authoritative reference-baseline record, including provenance metadata (source, capture conditions, active Run Engine code-version identity at capture time, environment identity, governed-revision history).
Preconditions: the corpus and boundary are each in a Defined/Enumerated state; a Replay Session has reached the Captured state for the specific execution intended as the reference.
Postconditions: exactly one reference-baseline record exists per governance epoch; the record's own provenance metadata is complete (TD005-SI-003).
Required behaviour: reject a candidate reference capture that reached the Failed state (TD005-SO-004); reject a reference capture with an incomplete provenance record; treat the established record as the sole authoritative reference for every subsequent comparison until a governed revision occurs.
Forbidden behaviour: mutating the reference-baseline record in place; establishing a new reference without an explicit, recorded governance act; treating an ordinary candidate capture (produced for a specific comparison) as if it were a new reference without that same explicit governance act.
Valid states: Unestablished; Capturing; Established; Revising. (Established is reachable by two distinct transitions, Capturing -> Established and Revising -> Established; it is one state, not two, since both paths yield the same post-condition, TD005-SI-003.)
Invalid states: Established-without-Provenance (a record lacking complete provenance metadata SHALL NOT be considered Established).
State transitions: Unestablished -> Capturing (a bootstrap Replay Session begins, TD005-SI-004). Capturing -> Established (the bootstrap capture succeeds and provenance is complete). Established -> Revising (a governed revision is initiated). Revising -> Established (the revision completes with a new, complete provenance record). Illegal: Established -> Unestablished (never un-established); Capturing -> Established without a completed, successful Replay Session; any transition into Established without complete provenance.
Observable properties: the current reference-baseline record's own provenance metadata; the governance-revision history; the current state.
Traceability: TD005-ARC-003; TD005-CAP-009; TD005-DEP-012, TD005-DEP-013, TD005-DEP-014; TD005-FR-018, TD005-FR-019, TD005-FR-021; OQ-002; TD005-AI-003, TD005-AI-018; TD005-AD-002.

### Domain C - Replay Session

**TD005-SO-004. Replay Session Specification.**
Purpose: specify the behaviour required to produce a scientifically comparable, controlled-condition execution of the active Run Engine.
Scope: the session's own lifecycle, controlled-condition enforcement, and determinism-precondition confirmation; not the concrete controlled-condition enumeration mechanism (Implementation-adjacent, Section 18).
Inputs: a controlled-condition specification (the tick sequence and initial state to replay from - either the reference's own specification, for a bootstrap capture, or a candidate specification, for a later comparison run); the active Run Engine's own runtime entry point.
Outputs: a captured execution trajectory, ready for Observation (TD005-SO-007), on success; a Failed state signal, on failure.
Preconditions: the active module set contains no wall-clock, network, or non-seeded-randomness dependency (independently reconfirmed, Section 5); a complete controlled-condition specification is available.
Postconditions: on success, the captured trajectory reflects execution under the exact controlled-condition specification provided, with no incidental non-determinism (collection-ordering artifacts) introduced; on failure, no partial or ambiguous trajectory is exposed to any downstream consumer.
Required behaviour: enforce every named controlled condition (input tick sequence, initial runtime state, initial Position, lifecycle history, regime/strategy state, configuration) for the full duration of the session; attach an Execution-Environment Identity record (TD005-SO-005) to every captured trajectory; drive the active Run Engine through its own unmodified, certified Stage Ordering (ADR-010) without altering Ownership or Information Flow.
Forbidden behaviour: altering Run Engine runtime semantics as a side effect of enabling comparability (TD005-AI-006); permitting a Replay Session to read its own captured state directly for comparison purposes (that is exclusively Observation's own role, TD005-SO-007); allowing a session that encountered an unhandled condition to silently resolve to Captured (TD005-SI-006).
Valid states: Not-Started; Configuring; Executing; Captured; Failed.
Invalid states: Executing-Indefinitely (a session SHALL reach Captured or Failed within a bounded duration; remaining in Executing without bound is invalid, TD005-SI-005).
State transitions: Not-Started -> Configuring (a controlled-condition specification is accepted). Configuring -> Executing (the specification is confirmed complete and execution begins). Executing -> Captured (the full controlled tick sequence completes without an unhandled condition). Executing -> Failed (an unhandled condition, an incomplete controlled-condition specification discovered mid-session, or a violation of a required controlled condition occurs). Illegal: Configuring -> Captured (execution SHALL occur; a session cannot be Captured without having Executed); Failed -> Captured (a failed session's own trajectory is never subsequently treated as successfully captured).
Observable properties: the current session state; the controlled-condition specification in force; the environmental-determinism confirmation; the captured trajectory (once Captured).
Traceability: TD005-ARC-011; TD005-CAP-010, TD005-CAP-011; TD005-DEP-009, TD005-DEP-010, TD005-DEP-018; TD005-FR-002, TD005-FR-013, TD005-FR-018; TD005-CON-004; TD005-AI-006, TD005-AI-010, TD005-AI-018, TD005-AI-019; TD005-AD-003.

**TD005-SO-005. Execution-Environment Identity Specification.**
Purpose: specify the behaviour required to record the execution environment's own third-party numeric-library and interpreter identity at capture time.
Scope: the identity-capture and attachment behaviour; not the concrete library/interpreter-version representation format (Implementation-adjacent, Section 18).
Inputs: the active execution environment's own interpreter identity and third-party library identity (`requirements.txt`-pinned `numpy`, `pandas`, and the interpreter itself).
Outputs: one execution-environment identity record, attachable to a Reference Baseline record (TD005-SO-003) or a Replay Session's own captured trajectory (TD005-SO-004).
Preconditions: a Replay Session or Reference Baseline capture is in progress and requires an identity record.
Postconditions: every captured trajectory and every reference-baseline record carries exactly one execution-environment identity record.
Required behaviour: capture identity at the moment of the associated Replay Session's own execution, not retroactively; expose the record to both TD005-SO-003 and TD005-SO-004 without itself deciding which of the two owns the final provenance record (that ownership decision belongs to the consuming object, TD005-SI-003).
Forbidden behaviour: reusing a stale identity record captured for a different session; omitting the identity record from any captured trajectory or reference-baseline record.
Valid states: Unrecorded; Recorded.
Invalid states: Recorded-Without-Association (a record not attached to any Replay Session or Reference Baseline SHALL NOT persist beyond the capture it was produced for).
State transitions: Unrecorded -> Recorded (identity is captured and attached). Illegal: Recorded -> Unrecorded (a recorded identity is never un-recorded; a fresh capture produces a fresh record, not a reversion of an existing one).
Observable properties: the current identity record's own library and interpreter identity values; the associated capture (Reference or Replay) it was attached to.
Traceability: TD005-ARC-012; TD005-CAP-022; TD005-CON-004 (by scientific proximity); TD005-AI-013, TD005-AI-016.

### Domain D - Observation Session

**TD005-SO-006. Observable Surface Classification Specification.**
Purpose: specify the behaviour required to classify runtime outputs into the four legitimate regression-evaluation categories.
Scope: the classification act itself; not the concrete classification-storage mechanism.
Inputs: the enumerated observable field set (the twelve CanonicalState fields, five lifecycle event types, LONG/SHORT side vocabulary, Executor status vocabulary), exposed through TD005-SO-007.
Outputs: a four-category classification (certified external output; certified internal invariant; implementation detail; incidental intermediate value) for every enumerated field.
Preconditions: the observable field set is fully enumerated (independently re-confirmed, Section 5).
Postconditions: every enumerated field carries exactly one of the four categories; no field is left unclassified (TD005-SI-008).
Required behaviour: classify every field before any Comparison-Semantics object (Domain F) consumes it; re-classify only through an explicit, recorded revision if the observable surface itself changes (for example, a future capability activates a currently-deferred module).
Forbidden behaviour: leaving a field unclassified while permitting it to be compared; assigning a field to more than one category.
Valid states: Unclassified; Classified.
Invalid states: Partially-Classified-and-Consumed.
State transitions: Unclassified -> Classified (every enumerated field receives exactly one category). Illegal: Classified -> Unclassified (classification, once complete, is not silently discarded; a revision is an explicit, recorded act, not a reversion).
Observable properties: the four-category classification map; the enumerated field set it was computed against.
Traceability: TD005-ARC-004; TD005-CAP-007; TD005-DEP-007; TD005-FR-003, TD005-FR-004, TD005-FR-005, TD005-FR-006, TD005-FR-013, TD005-FR-014, TD005-FR-015; TD005-AI-002.

**TD005-SO-007. Non-Interference Observation Specification.**
Purpose: specify the behaviour required to expose active Run Engine state without altering the behaviour being observed.
Scope: the observation act's own non-interference guarantee and boundary; not the concrete read-path implementation.
Inputs: the active Run Engine's own Tick-Complete state, at each tick boundary, during a Replay Session (TD005-SO-004).
Outputs: an observed state snapshot per tick, exposed to TD005-SO-006 and, transitively, every Comparison-Semantics object.
Preconditions: a Replay Session is Executing or has reached Captured.
Postconditions: the act of observation produces no measurable difference in the active Run Engine's own subsequent tick behaviour, compared to an unobserved run under the same controlled conditions (TD005-SI-007).
Required behaviour: expose exactly the confirmed non-interfering boundary (the Tick-Complete state as returned by the certified runtime entry point); refuse any observation request extending beyond this confirmed boundary.
Forbidden behaviour: any read that mutates, delays, or otherwise measurably alters Run Engine state or timing as a side effect; any component other than this one reading active Run Engine state directly (TD005-AD-013).
Valid states: Idle; Reading; Exposed.
Invalid states: Mutating (an observation act that alters state SHALL NOT occur; if detected, the associated Replay Session SHALL transition to Failed, per TD005-SI-005 and TD005-AI-019).
State transitions: Idle -> Reading (a tick boundary is reached and a snapshot is requested). Reading -> Exposed (the snapshot is returned, unmodified, to the requester). Exposed -> Idle (the session awaits the next tick boundary). Illegal: Reading -> Mutating (never; this transition, were it to occur, constitutes a defect, not a valid state).
Observable properties: the current session-relative tick index; the exposed snapshot; the non-interference confirmation for the observation act just performed.
Traceability: TD005-ARC-005; TD005-CAP-008; TD005-DEP-008, TD005-DEP-019; TD005-CON-001, TD005-CON-002; TD005-FR-004, TD005-FR-005, TD005-FR-006; OQ-001; TD005-AI-002; TD005-AD-013.

### Domain E - Behavioural Equivalence

**TD005-SO-008. Behavioural Equivalence Definition Specification.**
Purpose: specify the operational, formal definition of "equivalent" for regression purposes.
Scope: the definition's own structure and the principle it enforces; not the concrete comparison algorithm (Implementation-adjacent, Section 18).
Inputs: the classified observable surface (TD005-SO-006); the trajectory model (TD005-SO-010); the value-comparison rules (TD005-SO-011, TD005-SO-012).
Outputs: a formal equivalence definition, consumed by the Regression Classification Specification (TD005-SO-013).
Preconditions: the classified observable surface and the trajectory model are each defined.
Postconditions: the equivalence definition, once applied, yields the same equivalence determination for the same reference/candidate pair on repeated evaluation.
Required behaviour: define equivalence exclusively in terms of behavioural properties (trajectory-level and value-level, per TD005-SO-010 through TD005-SO-012); compose its three constituent models into one internally consistent definition.
Forbidden behaviour: defining equivalence, in whole or in part, as byte identity, source identity, or implementation identity (TD005-AI-007, TD005-SI-009); silently defaulting to a simpler notion of equivalence when a constituent model is itself unresolved.
Valid states: Undefined; Defined; Applied.
Invalid states: Partially-Defined-and-Applied (a definition missing one of its three constituent models SHALL NOT be applied to a live comparison).
State transitions: Undefined -> Defined (all three constituent models, TD005-SO-010/011/012, are individually defined and composed). Defined -> Applied (the definition is used by a specific comparison). Illegal: Applied -> Undefined (an applied definition is not retroactively undefined; a change requires an explicit, recorded revision producing a new Defined state).
Observable properties: the current definition's own composed form; which constituent models it currently incorporates.
Traceability: TD005-ARC-006; TD005-CAP-003; TD005-DEP-004; TD005-FR-020, TD005-FR-021, TD005-FR-018; OQ-006; TD005-AI-007.

**TD005-SO-009. Behavioural Vocabulary Specification.**
Purpose: specify the stability requirement for the terminology every other Specification Object's own behavioural contract is stated in.
Scope: the vocabulary's own stability and revision behaviour; not the vocabulary's own concrete representation.
Inputs: the Architecture Baseline's own Ownership Terminology section and ADR-009's own Scientific Definitions.
Outputs: the authoritative vocabulary (Position, Side, Scale-In, Partial Close, Full Close, Tick-Complete, Canonical Working State, Authoritative Owner, Computational Authority, Runtime Failure Event), consumed by every other Specification Object.
Preconditions: the Architecture Baseline is CERTIFIED.
Postconditions: every term used in any Specification Object's own behavioural contract resolves to exactly one definition from this vocabulary.
Required behaviour: expose the vocabulary as a stable, versioned reference; require an explicit, recorded revision before any term's own meaning changes.
Forbidden behaviour: permitting two Specification Objects to use the same term with different meanings; introducing a new term without adding it to this vocabulary first.
Valid states: Established; Revised.
Invalid states: Ambiguous (a term used in this Specification with more than one active meaning SHALL NOT occur).
State transitions: Established -> Revised (a governed vocabulary change occurs). Illegal: Established -> Undefined (the vocabulary, once established, is never un-established).
Observable properties: the current vocabulary's own complete term set; the revision history.
Traceability: TD005-ARC-010; TD005-CAP-021; TD005-DEP-032; all twenty-two Functional Requirements (indirectly); TD005-AI-001.

### Domain F - Comparison Semantics

**TD005-SO-010. Trajectory Comparison Specification.**
Purpose: specify whether, and how, equivalence is evaluated across the complete execution trajectory rather than the final state alone.
Scope: the trajectory-required property set and the logical-order/wall-clock distinction; not the concrete trajectory-representation format (Implementation-adjacent, Section 18).
Inputs: two observed execution trajectories (reference and candidate), each fully classified (TD005-SO-006).
Outputs: a trajectory-level comparison basis, consumed by TD005-SO-013.
Preconditions: both trajectories have reached the Captured state (TD005-SO-004) and been fully observed (TD005-SO-007).
Postconditions: every trajectory-required property (execution ordering, publication uniqueness, lifecycle transition integrity, failure-event generation, information-flow non-reconstruction) is evaluated across the complete trajectory for every Functional Requirement the CGA's own TD005-CAP-004 names as trajectory-dependent.
Required behaviour: evaluate trajectory-required properties using only logical-order semantics (the certified Stage Ordering, ADR-010), never wall-clock timing, across the complete captured trajectory (TD005-SI-010); evaluate final-state-only properties using the final observed state alone, without requiring full-trajectory comparison where the accepted FRA does not require it.
Forbidden behaviour: substituting final-state-only comparison for any Functional Requirement the CGA's own TD005-CAP-004 identifies as trajectory-dependent; treating a wall-clock timing difference as a trajectory-equivalence violation.
Valid states: Undefined; Defined; Applied.
Invalid states: Endpoint-Only-Applied-to-Trajectory-Requirement (applying final-state-only comparison to a trajectory-required property SHALL NOT occur).
State transitions: Undefined -> Defined (the trajectory-required property set and the logical-order/wall-clock distinction are both established). Defined -> Applied (used by a specific comparison). Illegal: Applied -> Undefined.
Observable properties: the trajectory-required property set currently in force; the logical-order/wall-clock distinction's own current statement.
Traceability: TD005-ARC-007; TD005-CAP-004; TD005-DEP-005, TD005-DEP-015, TD005-DEP-017; TD005-FR-001, TD005-FR-003, TD005-FR-006, TD005-FR-007, TD005-FR-008, TD005-FR-009, TD005-FR-010, TD005-FR-017, TD005-FR-022; TD005-AI-004.

**TD005-SO-011. Numeric and Categorical Comparison Specification.**
Purpose: specify the comparison-category structure for observed values, without selecting a concrete tolerance value.
Scope: the category structure (exact-equality versus tolerance-bounded) and the categorical/continuous value-set separation; not the specific tolerance value, which belongs to Implementation (Section 18, TD005-SI-011).
Inputs: individual observed values from the classified surface (TD005-SO-006).
Outputs: a per-value comparison-category assignment, consumed by TD005-SO-013.
Preconditions: the observable surface is fully classified (TD005-SO-006).
Postconditions: every observed value is assigned to exactly one comparison category before being compared.
Required behaviour: assign categorical/discrete values (`event_type`, Position Side) to the exact-equality category; assign continuous financial and risk/performance values to the tolerance-bounded category; require that every tolerance-bounded comparison cite a documented tolerance value at Implementation time (the value itself is not chosen here).
Forbidden behaviour: applying exact equality to a value in the tolerance-bounded category; applying a tolerance to a value in the exact-equality category; leaving a value's own category unassigned.
Valid states: Undefined; Defined; Applied.
Invalid states: Uncategorized-and-Compared.
State transitions: Undefined -> Defined (the category structure and the categorical/continuous separation are established). Defined -> Applied. Illegal: Applied -> Undefined.
Observable properties: the current category assignment for each observed value; the category structure itself.
Traceability: TD005-ARC-008; TD005-CAP-005; TD005-DEP-006, TD005-DEP-016; TD005-FR-007, TD005-FR-008, TD005-FR-009, TD005-FR-010, TD005-FR-011, TD005-FR-012, TD005-FR-013, TD005-FR-014, TD005-FR-015, TD005-FR-016, TD005-FR-017 (the eleven-requirement set the CGA itself names).

**TD005-SO-012. Object-Identity-Independent Comparison Specification.**
Purpose: specify that observed equivalence is evaluated by structural value equality, never by Python object identity or process-local mutable state.
Scope: the identity-independence rule itself; not its own concrete enforcement mechanism.
Inputs: individual observed values from the classified surface (TD005-SO-006).
Outputs: an identity-independent comparison rule, consumed by TD005-SO-013.
Preconditions: the observable surface is fully classified (TD005-SO-006).
Postconditions: two structurally-equal-but-not-identical observations are treated as equivalent.
Required behaviour: compare every observed value by structural value equality; treat object identity as irrelevant to every comparison outcome (TD005-SI-012).
Forbidden behaviour: any comparison outcome that depends on Python object identity, dict/list identity, or process-local mutable-state identity rather than structural value equality.
Valid states: Undefined; Defined; Applied.
Invalid states: Identity-Dependent-Applied (a comparison whose own outcome depended on object identity SHALL NOT be treated as a valid application of this rule).
State transitions: Undefined -> Defined (the rule is established). Defined -> Applied. Illegal: Applied -> Undefined.
Observable properties: the rule's own current statement; confirmation, per comparison, that only structural value equality was used.
Traceability: TD005-ARC-009; TD005-CAP-006; TD005-DEP-011; TD005-FR-002, TD005-FR-005.

### Domain G - Regression Classification

**TD005-SO-013. Regression Classification Specification.**
Purpose: specify the complete, exhaustive classification of an observed deviation against the certified-contract boundary.
Scope: the classification act's own four-outcome semantics and exclusions; not the concrete classification procedure (Implementation-adjacent, Section 18).
Inputs: an observed deviation (a candidate execution compared against the Reference Baseline's own record, TD005-SO-003); the certification-boundary determination (TD005-SO-002); the formal equivalence definition (TD005-SO-008); advisory coverage context (TD005-SO-014, TD005-SO-015).
Outputs: exactly one of four classification outcomes per evaluated deviation: Regression, Non-Regression, Indeterminate, or Invalid Comparison.
Preconditions: a candidate execution has been captured (TD005-SO-004), observed (TD005-SO-007), and compared (Domain F) against the established reference (TD005-SO-003).
Postconditions: every evaluated deviation carries exactly one of the four outcomes; no deviation remains unclassified (TD005-SI-013).
Required behaviour: classify a deviation as **Regression** only when the formal equivalence definition (TD005-SO-008) determines non-equivalence within the certified-contract boundary; classify as **Non-Regression** only when equivalence is confirmed within that boundary; classify as **Indeterminate** when the certification-boundary determination or coverage context cannot yet confidently place the deviation inside or outside the certified-contract boundary (for example, within a currently-evidenced coverage gap, TD005-CAP-002, TD005-CAP-015, TD005-CAP-016); classify as **Invalid Comparison** when any upstream Specification Object (Replay, Observation, or Comparison) failed to produce its own required output (TD005-AI-019), rather than forcing the deviation into one of the other three outcomes.
Forbidden behaviour: assigning, computing, or exposing severity ranking, business acceptability, waiver status, remediation priority, or operational disposition for any classified deviation, for any outcome (TD005-AI-009); allowing Coverage output (Domain H) to override or alter a reached classification, rather than informing it in advance (TD005-AI-014); treating a Failed Replay Session or a component-failure condition as either Regression or Non-Regression.
Valid states: Pending; Evaluating; Classified-Regression; Classified-Non-Regression; Classified-Indeterminate; Classified-Invalid-Comparison.
Invalid states: Unclassified-and-Reported (a deviation reported to Evidence, TD005-SO-016, without a completed classification SHALL NOT occur).
State transitions: Pending -> Evaluating (all mandatory upstream inputs, per Section 11 of the Architecture, are available). Evaluating -> one of the four Classified-* states (exactly one, exhaustively). A Classified-* state -> a different Classified-* state is legal only given an explicit, independently-recorded re-evaluation (for example, newly-resolved Certification Boundary or Coverage information reclassifying a previously Classified-Indeterminate deviation); the re-evaluation record itself, not merely the changed outcome, is what makes the transition legal. Illegal: Evaluating -> Pending (once evaluation begins with complete inputs, it reaches a classified state, not a reversion); any Classified-* state -> a different Classified-* state without an explicit, independently-recorded re-evaluation.
Observable properties: the classification outcome; which of the four outcome categories was reached; the specific unresolved condition, if Indeterminate or Invalid Comparison.
Traceability: TD005-ARC-017; TD005-CAP-012; TD005-DEP-002, TD005-DEP-004, TD005-DEP-020; TD005-FR-018, TD005-FR-020, TD005-FR-021; TD005-AI-007, TD005-AI-008, TD005-AI-009, TD005-AI-013, TD005-AI-014, TD005-AI-019; TD005-AD-008; TD005-SD-001.

### Domain H - Coverage

**TD005-SO-014. Contract-to-Requirement Coverage Specification.**
Purpose: specify the completeness-audit behaviour confirming every certified contract is traceable to a Functional Requirement and vice versa.
Scope: the coverage-audit act itself; not the concrete coverage-computation mechanism (Implementation-adjacent, Section 18).
Inputs: the corpus enumeration (TD005-SO-001); the FRA's own twenty-two Functional Requirements.
Outputs: a coverage-completeness report, advisory to TD005-SO-013.
Preconditions: the corpus enumeration is in the Enumerated state.
Postconditions: the report explicitly names every currently-uncovered certified contract and every currently-uncovered Functional Requirement, including the CGA's own already-evidenced gaps (AC-011's own end-to-end traceability property; AC-003's own partial RiskEngine-only instantiation).
Required behaviour: recompute the report whenever the corpus enumeration transitions to Re-Enumerated (TD005-SO-001); surface every gap explicitly rather than silently narrowing Classification's own scope to avoid reporting it.
Forbidden behaviour: altering, suppressing, or overriding a Classification outcome (TD005-AI-014, TD005-SI-015); treating an uncovered contract as implicitly excluded from the corpus.
Valid states: Not-Computed; Computed; Stale (the corpus has re-enumerated since the last computation); Recomputed.
Invalid states: Stale-and-Consulted-as-Current.
State transitions: Not-Computed -> Computed. Computed -> Stale (corpus drift, TD005-SO-001). Stale -> Recomputed. Illegal: Stale -> Computed-without-Recomputation (a stale report is never silently treated as current).
Observable properties: the current report's own gap list; the corpus-enumeration version it was computed against.
Traceability: TD005-ARC-015; TD005-CAP-015; TD005-DEP-020; all twenty-two Functional Requirements (completeness check); TD005-FR-013 (AC-003), TD005-FR-006 (AC-011 gap); TD005-AI-014.

**TD005-SO-015. Module and State-Transition Coverage Specification.**
Purpose: specify the completeness-audit behaviour confirming every active module and certified state transition is covered by the Functional Requirements.
Scope: the coverage-audit act and the coverage-concept requirement; not the concrete coverage-concept choice (Implementation-adjacent, Section 18).
Inputs: the active module set (independently re-confirmed, Section 5); the FRA's own Functional Requirements; ADR-009's own Lifecycle Transition Table.
Outputs: a module/state-transition coverage report, advisory to TD005-SO-013; the chosen coverage concept, once Implementation selects it.
Preconditions: the active module set is confirmed (Section 5).
Postconditions: the report explicitly names every currently-uncovered active module (independently re-confirmed as `run_engine/main.py`, `run_engine/core/state.py`, `run_engine/core/regime.py`, `run_engine/core/execution/__init__.py`) and every certified state transition not individually traced.
Required behaviour: re-derive module coverage from the active module set on every recomputation; treat a scope-drift event (TD005-SO-021) as a trigger for recomputation.
Forbidden behaviour: treating a RETAIN-Deferred-Scope module's own future reactivation as automatically covered without recomputation; altering a Classification outcome (TD005-AI-014).
Valid states: Not-Computed; Computed; Stale (scope drift detected, TD005-SO-021); Recomputed.
Invalid states: Stale-and-Consulted-as-Current.
State transitions: Not-Computed -> Computed. Computed -> Stale. Stale -> Recomputed. Illegal: Stale -> Computed-without-Recomputation.
Observable properties: the current report's own module and state-transition gap list; the chosen coverage concept, once selected.
Traceability: TD005-ARC-016; TD005-CAP-016; TD005-DEP-021, TD005-DEP-022; FRA Section 13.1; TD005-FR-001, TD005-FR-002, TD005-FR-007, TD005-FR-008, TD005-FR-009, TD005-FR-010; TD005-AI-014.

### Domain I - Evidence

**TD005-SO-016. Regression Evidence Composition Specification.**
Purpose: specify the complete, required content of an evidence record for every detected regression.
Scope: the evidence-composition schema and the composition act itself; not the concrete storage form (Implementation-adjacent, Section 18).
Inputs: a classification outcome (TD005-SO-013); the controlled-condition record (TD005-SO-004); the execution-environment identity record (TD005-SO-005); the certification-boundary determination (TD005-SO-002).
Outputs: one complete evidence record per Regression (and, per TD005-SD-004, per Indeterminate and Invalid Comparison) outcome.
Preconditions: a classification outcome other than Non-Regression has been reached.
Postconditions: the evidence record carries all eight required elements: affected tick; affected stage or component; expected value; actual value; input provenance; initial-state provenance; the specific certified-contract ID the deviation is attributed to; execution-environment identity. For a Regression outcome (and for a Non-Regression outcome for which evidence is optionally retained), every element SHALL carry a determinate value. For an Indeterminate or Invalid Comparison outcome, an element rendered structurally unobtainable by the very condition that produced the outcome (for example, no determinate certified-contract ID when the certification boundary itself cannot place the deviation, TD005-SO-002; no actual value when an upstream Replay or Observation object failed to produce its own required output, TD005-AI-019) SHALL instead carry an explicit, reasoned unavailability marker naming which upstream condition prevented a determinate value; a bare omission is not equivalent to a reasoned unavailability marker and does not satisfy this element.
Required behaviour: compose the complete evidence record before the associated classification outcome is considered complete (TD005-SD-004, TD005-SI-016); compose a separate evidence record for each independently-classified deviation, even if two deviations share the same underlying cause; for an Indeterminate or Invalid Comparison outcome, record an explicit, reasoned unavailability marker for any element the same outcome-producing condition renders structurally unobtainable, rather than leaving the element blank or treating the record as permanently unable to reach Composed.
Forbidden behaviour: modifying the observed behaviour, the reference baseline, or the classification outcome as a side effect of composing evidence (TD005-AI-005); omitting any of the eight required elements without either a determinate value or, where structurally unobtainable, an explicit reasoned unavailability marker; composing evidence for a Non-Regression outcome (not required, though not forbidden if Implementation chooses to retain it for audit purposes - Section 18).
Valid states: Not-Composed; Composing; Composed.
Invalid states: Composed-and-Incomplete (a record missing any of the eight required elements, with neither a determinate value nor an explicit reasoned unavailability marker, SHALL NOT be considered Composed).
State transitions: Not-Composed -> Composing (a qualifying classification outcome is reached). Composing -> Composed (all eight elements are present). Illegal: Composing -> Composed with fewer than eight elements; Composed -> Composing (a composed record is not re-opened for editing; a correction produces a new, separate record).
Observable properties: the evidence record's own eight elements; the classification outcome it documents.
Traceability: TD005-ARC-013; TD005-CAP-013; TD005-DEP-023; TD005-FR-019; TD005-AI-005; TD005-SD-004.

**TD005-SO-017. Evidence Persistence and Continuity Specification.**
Purpose: specify the persistence-and-continuity requirements for composed evidence, without defining the persistence mechanism.
Scope: the persistence-boundary and continuity requirement; not the concrete storage/serialization mechanism (Implementation-adjacent, Section 18).
Inputs: composed evidence records (TD005-SO-016).
Outputs: a persisted, continuity-linked evidence record, consumed by TD005-SO-018.
Preconditions: an evidence record has reached the Composed state.
Postconditions: every persisted record remains retrievable and unaltered (TD005-SI-017) across every subsequent Long-Duration-Validation stage transition (TD005-SO-018) until an explicit, governed retention/expiry action removes it.
Required behaviour: persist every Composed evidence record; preserve cross-stage continuity (a record persisted during one validation stage remains retrievable during every later stage); remain within Repository Consolidation's own Normative Repository Boundary (TD005-AI-015, TD005-SI-018).
Forbidden behaviour: modifying a persisted record's own content; placing a persisted record outside the governed repository locations Repository Consolidation's own boundary establishes; selecting or implying a specific storage technology, file format, or database.
Valid states: Unpersisted; Persisted; Retained; Expired (per a governed retention/expiry policy, once Implementation defines one, Section 18).
Invalid states: Persisted-and-Altered (a persisted record whose own content has changed SHALL NOT be considered valid; the alteration itself is the defect).
State transitions: Unpersisted -> Persisted (a Composed record is persisted). Persisted -> Retained (the record survives a validation-stage transition unaltered). Retained -> Expired (a governed retention/expiry policy removes it). Illegal: Persisted -> Unpersisted (a persisted record is not silently un-persisted, only expired through a governed act); Persisted -> Persisted-and-Altered.
Observable properties: the persistence status; the retention/expiry status, once Implementation defines the policy; the record's own unaltered content.
Traceability: TD005-ARC-014; TD005-CAP-014; TD005-DEP-024, TD005-DEP-027; TD005-FR-019, TD005-FR-022; TD005-CON-003; TD005-AI-005, TD005-AI-015, TD005-AI-017.

### Domain J - Governance

**TD005-SO-018. Long-Duration-Validation Integration Specification.**
Purpose: specify the invocation-contract requirements enabling the same regression capability to be used, without modification, before each of the six mandatory Long-Duration-Validation stages.
Scope: the invocation-contract requirement and the evidence-continuity requirement; not the concrete execution-time budget or pre/post-run application choice (Implementation-adjacent, Section 18).
Inputs: the six-stage Long-Duration-Validation sequence (Implementation Baseline); persisted evidence records (TD005-SO-017).
Outputs: a stage-applicable invocation contract, identical across all six stages.
Preconditions: the six-stage sequence is defined (Implementation Baseline, independently re-confirmed).
Postconditions: the invocation contract used before the Functional-smoke stage is identical, in every observable respect, to the contract used before the 30-day stage (TD005-SI-019).
Required behaviour: expose one invocation contract, not six stage-specific variants; carry evidence continuity across every stage transition (TD005-SO-017).
Forbidden behaviour: requiring a stage-specific modification to the invocation contract; losing evidence continuity across a stage transition.
Valid states: Not-Invoked; Invoked (per stage); Stage-Complete.
Invalid states: Stage-Specific-Variant-in-Use (a modified, stage-specific invocation contract SHALL NOT exist).
State transitions: Not-Invoked -> Invoked (a validation stage begins). Invoked -> Stage-Complete (the stage concludes, successfully or not, per the Implementation Baseline's own stage-completion criteria). Stage-Complete -> Invoked (the next stage begins, using the identical contract). Illegal: Invoked -> Invoked-with-a-different-contract (the contract is never varied by stage).
Observable properties: the current stage; the invocation contract in force (identical across stages); the evidence-continuity chain across completed stages.
Traceability: TD005-ARC-018; TD005-CAP-020; TD005-DEP-025, TD005-DEP-026, TD005-DEP-027; TD005-FR-022, TD005-FR-019; OQ-004.

**TD005-SO-019. Governance Sequence Conformance Specification.**
Purpose: specify the requirement that TD-005's own resolution proceeds through the established governance sequence.
Scope: the conformance-recording behaviour itself; this object owns no regression-detection runtime information.
Inputs: none (a governance-metadata object; consumes no runtime information).
Outputs: a governance-conformance record, referenced by any future review of this Specification or a downstream Implementation.
Preconditions: the FRA, SDA, CGA, and Architecture are each accepted (Section 3).
Postconditions: this Specification's own existence, scope, and refusal to select implementation content is itself the conformance evidence.
Required behaviour: record this Specification's own explicit refusal to select implementation-inappropriate content; provide a citable artifact for a future Architecture or Specification Evolution Review (Implementation Baseline Principle IP-006).
Forbidden behaviour: proceeding to Implementation-level content within this document; skipping the established sequence for any future revision of this Specification.
Valid states: Conformant.
Invalid states: Non-Conformant (this Specification, or any future revision, proceeding out of sequence).
State transitions: none (a static conformance record, re-affirmed, not transitioned, by each future governance stage's own conduct).
Observable properties: the conformance record itself.
Traceability: TD005-ARC-019; TD005-CAP-019; TD005-DEP-033; all FRA items (procedurally).

### Domain K - Extension Points

**TD005-SO-020. Specification Extension Point Registry Specification.**
Purpose: specify the requirement that every unresolved Specification-level mechanism choice is exposed explicitly to Implementation, as a named, stable contract, without this Specification choosing the mechanism itself.
Scope: the registry's own completeness and non-silent-resolution requirement; not the concrete mechanism choices themselves (Section 18).
Inputs: every Specification Object's own unresolved mechanism boundary (Section 18).
Outputs: the Implementation handover list (Section 18), the primary artifact a future Implementation stage consumes.
Preconditions: every Specification Object (TD005-SO-001 through TD005-SO-019, TD005-SO-021, TD005-SO-022) is defined.
Postconditions: the registry accurately reflects every Specification Object's own current deferral, with no silent gap.
Required behaviour: enumerate, by name, every mechanism decision this Specification leaves open; attach each to its own owning Specification Object; ensure no Implementation-stage mechanism choice is made without being recorded here first.
Forbidden behaviour: allowing an Implementation-stage mechanism choice to be made against a Specification Object without an entry in this registry; selecting a mechanism itself.
Valid states: Incomplete; Complete.
Invalid states: Complete-with-Unrecorded-Deferral (a registry claiming completeness while a Specification Object's own deferral is not listed SHALL NOT occur).
State transitions: Incomplete -> Complete (every current deferral is recorded). Complete -> Incomplete (a new Specification Object or a newly-discovered deferral is added, requiring the registry to be re-verified before being considered Complete again). Illegal: Complete -> Complete-with-Unrecorded-Deferral.
Observable properties: the registry's own current entry list; each entry's own owning Specification Object.
Traceability: TD005-ARC-022; TD005-CAP-001, TD005-CAP-002, TD005-CAP-004, TD005-CAP-005, TD005-CAP-009, TD005-CAP-011, TD005-CAP-012, TD005-CAP-013, TD005-CAP-014, TD005-CAP-016, TD005-CAP-020, TD005-CAP-022 (aggregate traceability, per the Architecture's own TD005-ARC-022 precedent); TD005-AI-016, TD005-AI-017.

### Domain L - Repository Boundary Protection

**TD005-SO-021. Active/Deferred Scope Boundary Specification.**
Purpose: specify the stability requirement for the active/inactive Run Engine module partition and the coverage mechanism's own sensitivity to a future change in that partition.
Scope: the scope-boundary requirement and drift-sensitivity trigger; not the concrete drift-detection mechanism (Implementation-adjacent, Section 18).
Inputs: the active/inactive module partition (independently re-confirmed, Section 5).
Outputs: the current scope boundary, consumed by every Specification Object whose own scope presupposes "the active Run Engine" (TD005-SO-001, TD005-SO-006, TD005-SO-011, TD005-SO-014, TD005-SO-015).
Preconditions: the active/inactive partition is independently re-confirmed at the start of every Replay Session (TD005-SO-004) and Observation Session (TD005-SO-007).
Postconditions: no RETAIN-Deferred-Scope module (`run_engine/core/config.py`, `run_engine/runtime/recovery.py`, `run_engine/runtime/snapshot.py`, `run_engine/runtime/state_memory.py`) is ever silently treated as active.
Required behaviour: re-evaluate the scope boundary at the start of every session, not assume it unchanged from a prior evaluation (TD005-SI-020); signal a Coverage recomputation (TD005-SO-015) if the partition changes.
Forbidden behaviour: caching the scope boundary indefinitely without re-evaluation; treating a future reactivation of a RETAIN-Deferred-Scope module as in-scope without a separate, governed Architecture Evolution Review (TD005-AI-011).
Valid states: Stable; Drift-Detected; Re-Confirmed.
Invalid states: Assumed-Unchanged-Without-Re-Evaluation.
State transitions: Stable -> Drift-Detected (a partition change is detected). Drift-Detected -> Re-Confirmed (the new partition is independently re-verified and a governed review, if required, is triggered). Illegal: Drift-Detected -> Stable without an intervening Re-Confirmed.
Observable properties: the current active/inactive partition; the drift status; the last re-evaluation timestamp or provenance marker.
Traceability: TD005-ARC-020; TD005-CAP-017; TD005-DEP-028, TD005-DEP-029, TD005-DEP-031; FRA Section 6.3; OQ-003. OQ-005 (test-code location) is compatible with, but not resolved by, this object's own scope boundary (Section 19.4). TD005-AI-011.

**TD005-SO-022. Executor Namespace Boundary Specification.**
Purpose: specify that this Specification does not own, extend, or duplicate Repository Consolidation's own Executor-namespace-uniqueness protection.
Scope: the boundary-exclusion record itself; this object owns no regression-detection runtime information.
Inputs: none (a boundary-marker object; consumes no runtime information).
Outputs: an explicit exclusion record.
Preconditions: Repository Consolidation's own RC-AD-004 mechanism is independently CERTIFIED (re-confirmed, Section 5).
Postconditions: no Specification Object among TD005-SO-001 through TD005-SO-021 performs Executor-namespace-uniqueness verification.
Required behaviour: record the exclusion explicitly; provide the single citable point confirming this Specification's own scope stops here.
Forbidden behaviour: any Specification Object re-implementing or duplicating Repository Consolidation's own Executor-namespace check.
Valid states: Excluded.
Invalid states: Absorbed (a future revision of this Specification silently taking on this responsibility SHALL NOT occur without an explicit, governed scope change).
State transitions: none (a static exclusion record).
Observable properties: the exclusion record itself.
Traceability: TD005-ARC-021; TD005-CAP-018; TD005-DEP-030; FRA Section 13.2; TD005-AD-009 (this object's own Architecture-level grounding as an explicit exclusion-marker component, rather than a silently omitted one).

All twenty-two Specification Objects are individually numbered with no gap; every Architecture Component (TD005-ARC-001 through TD005-ARC-022) is specified by exactly one Specification Object.

## 8. Behavioural Contracts

The normative behavioural contract for every Specification Object is stated in full within its own entry (Section 7): Required behaviour (mandatory), Forbidden behaviour (never permitted), and, where applicable, optional behaviour is named explicitly rather than left implicit (for example, TD005-SO-016's own optional retention of Non-Regression evidence for audit purposes). Undefined behaviour - behaviour this Specification does not constrain - is confined exclusively to the concrete mechanism choices Section 18 names; no Specification Object leaves its own required/forbidden behavioural boundary undefined. Every Required behaviour statement uses SHALL-equivalent normative language ("SHALL," "is required," "before... is considered complete"); every Forbidden behaviour statement uses SHALL-NOT-equivalent language. No behavioural contract in this section selects a concrete algorithm, data structure, or storage technology; each states the property Implementation's own chosen mechanism must satisfy.

## 9. State Models

Every Specification Object's own complete state model (valid states, invalid states, legal transitions, illegal transitions) is stated in full within its own Section 7 entry. Three state-model patterns recur, each independently justified from repository evidence: (1) **Authority/Registry pattern** (TD005-SO-001, TD005-SO-002, TD005-SO-006, TD005-SO-008, TD005-SO-009, TD005-SO-010, TD005-SO-011, TD005-SO-012, TD005-SO-020) - Undefined/Uninitialized -> Defined/Established -> Revised, reflecting these objects' own governed, infrequently-changing nature; (2) **Session pattern** (TD005-SO-004, TD005-SO-005, TD005-SO-007) - Not-Started -> ... -> a terminal Captured/Failed or Exposed state, reflecting per-invocation, bounded lifecycles (TD005-SD-003); (3) **Marker pattern** (TD005-SO-019, TD005-SO-022) - a single static state with no transition, reflecting these objects' own zero-owned-runtime-information role, consistent with their Architecture-level origin (TD005-ARC-019, TD005-ARC-021). TD005-SO-003 (Reference Baseline), TD005-SO-013 (Classification), TD005-SO-014/015 (Coverage), TD005-SO-016/017 (Evidence), TD005-SO-018 (Governance Integration), and TD005-SO-021 (Scope Boundary) each combine elements of more than one pattern, reflecting their own genuinely composite lifecycle; each is stated individually and completely in Section 7, not forced into a single template.

## 10. Comparison Semantics

**Behavioural equivalence** (TD005-SO-008) is defined exclusively as the composition of trajectory equivalence (TD005-SO-010) and value-level equivalence (TD005-SO-011, TD005-SO-012), never as byte, source, or implementation identity (TD005-AI-007).

**Trajectory equivalence** (TD005-SO-010) applies to every Functional Requirement the CGA's own TD005-CAP-004 identifies as trajectory-dependent (TD005-FR-001, 003, 006, 007, 008, 009, 010, 017): the complete sequence of intermediate stage transitions and events, evaluated under logical-order semantics (ADR-010's own certified Stage Ordering), never wall-clock timing.

**Endpoint equivalence** applies to every Functional Requirement not identified as trajectory-dependent: the final Tick-Complete state alone is compared.

**Numeric comparison categories** (TD005-SO-011) are exactly two: exact-equality (for categorical/discrete values - `event_type`, Position Side) and tolerance-bounded (for continuous financial and risk/performance values). No third category exists; no value is left uncategorized.

**Comparison domains** are the classified observable surface's own four categories (TD005-SO-006): certified external output and certified internal invariant are within the comparison domain; implementation detail and incidental intermediate value are excluded from comparison entirely, regardless of whether they happen to differ between reference and candidate.

**Comparison exclusions**: object identity and process-local mutable state (TD005-SO-012) are never a comparison criterion; wall-clock timing is never a comparison criterion for trajectory-required properties; any field classified as implementation detail or incidental intermediate value (TD005-SO-006) is excluded from comparison entirely.

**Tolerance values do not belong in this Specification.** They belong to Implementation, cited by name against TD005-SO-011 in the Extension Point Registry (TD005-SO-020, Section 18), since a specific tolerance value is a numeric-precision engineering choice contingent on the concrete comparison mechanism Implementation selects, not a behavioural property this Specification can state without prescribing that mechanism.

## 11. Classification Semantics

Four exhaustive, mutually exclusive outcomes (TD005-SO-013, TD005-SD-001):

- **Regression**: the formal equivalence definition (TD005-SO-008) determines non-equivalence within the certified-contract boundary (TD005-SO-002).
- **Non-Regression**: the formal equivalence definition determines equivalence within the certified-contract boundary.
- **Indeterminate**: the certified-contract boundary or Coverage context (TD005-SO-014, TD005-SO-015) cannot yet confidently place the deviation inside or outside the boundary - a scientifically honest outcome required precisely because the CGA's own TD005-CAP-002 (Certification Boundary) is currently MISSING and TD005-CAP-015/016 (Coverage) currently carry evidenced gaps (AC-011's own uncovered property; four uncovered modules).
- **Invalid Comparison**: an upstream Specification Object (Replay, Observation, or any Comparison-Semantics object) failed to produce its own required output (TD005-AI-019); the comparison itself could not validly be completed.

**Explicitly excluded** from every outcome, for every classified deviation, without exception: business severity, operational priority, waiver, and disposition (TD005-AI-009). No Specification Object in this document computes, stores, or exposes any of these four excluded properties. Any future need for them requires a new Functional Requirement and a new Architecture Component - not an extension of TD005-SO-013.

## 12. Evidence Specification

**Evidence contents** (TD005-SO-016): eight required elements per record - affected tick; affected stage or component; expected value; actual value; input provenance; initial-state provenance; the specific certified-contract ID; execution-environment identity.

**Evidence lifecycle**: Not-Composed -> Composing -> Composed (TD005-SO-016) -> Unpersisted -> Persisted -> Retained -> Expired (TD005-SO-017, once Implementation defines a retention/expiry policy). A record is immutable once Composed (TD005-AI-005); a correction produces a new, separate record, never an edit.

**Evidence ownership**: TD005-SO-016 owns the evidence-composition schema and each composed record instance until handed to TD005-SO-017; TD005-SO-017 owns the persistence-and-continuity contract and every persisted record thereafter. No other Specification Object owns evidence content.

**Evidence completeness**: a record is not considered Composed until all eight required elements are present, either as a determinate value or, for an Indeterminate or Invalid Comparison outcome, an explicit reasoned unavailability marker where the outcome-producing condition itself renders the element unobtainable (TD005-SI-016); an incomplete record SHALL NOT be persisted.

**Evidence validity**: a Composed, complete, unaltered record is valid; an altered persisted record is invalid by definition (TD005-SO-017's own Invalid states).

**Evidence exclusions**: evidence composition is required for Regression outcomes and, per TD005-SD-004, for Indeterminate and Invalid Comparison outcomes (both represent an unresolved or incomplete classification a future reviewer needs to reproduce and resolve); evidence composition is optional, not required, for Non-Regression outcomes. No persistence mechanism, storage technology, or serialization format is specified anywhere in this section (TD005-AI-017).

## 13. Coverage Specification

**Contract coverage** (TD005-SO-014): every certified contract in the corpus traceable to a Functional Requirement, and vice versa.

**Capability coverage**: every one of the twenty-two CGA Capabilities maps to at least one Specification Object (Section 17, inherited unchanged from the Architecture's own Section 16 Architecture Readiness assessment).

**Component coverage**: every one of the twenty-two Architecture Components maps to exactly one Specification Object (Section 17).

**Comparison coverage**: every classified observable-surface field (TD005-SO-006) in the comparison domain (certified external output, certified internal invariant) is actually exercised by at least one Comparison-Semantics object (Domain F); every active module and certified state transition is traceable to a Functional Requirement (TD005-SO-015).

**Evidence coverage**: every Regression, Indeterminate, and Invalid Comparison outcome produces a corresponding evidence record (TD005-SO-016, TD005-SD-004); coverage of Non-Regression outcomes by evidence is optional.

No metrics implementation (a concrete coverage-percentage calculation, a concrete coverage-reporting format) is specified anywhere in this section; each coverage category above is a completeness requirement, not a computed metric.

## 14. Extension Specification

**How extensions may participate** (TD005-SO-020): a future Implementation-stage mechanism choice against any named entry in the Extension Point Registry (Section 18) is a legitimate, anticipated form of participation, provided it is recorded in the registry before being treated as binding (TD005-SI-022).

**How they may not participate**: no extension may introduce a new classification outcome beyond the four TD005-SO-013 defines; no extension may reintroduce severity, waiver, disposition, or remediation priority (TD005-AI-009); no extension may bypass the Non-Interference Observation boundary (TD005-SO-007) to read active Run Engine state directly; no extension may alter a Coverage report's own advisory-only status into classification authority (TD005-AI-014).

**Compatibility rules**: any Implementation-stage mechanism choice SHALL satisfy the full behavioural contract (Section 8) of the Specification Object it resolves; a mechanism choice that satisfies only part of a contract, or that requires relaxing a Required/Forbidden behaviour statement, is not compatible and requires an explicit Specification amendment, not a silent extension.

**Isolation rules**: a mechanism choice for one Specification Object SHALL NOT alter the behavioural contract of any other Specification Object; TD005-SO-020's own registry entries are independently resolvable (Architecture's own TD005-ARC-012, via TD005-AD-004, remains a documented example: its own fold-in-or-remain-standalone choice does not require any other object's contract to change).

**Governance rules**: every extension-point resolution follows the same FRA -> SDA -> CGA -> Architecture -> Specification -> Implementation -> Final Certification sequence this entire governance chain has followed (TD005-SO-019); no mechanism choice bypasses Implementation Baseline Principle IP-006 (Controlled Architectural Evolution) if it would require altering a Specification Object's own contract rather than merely resolving an already-named deferral.

## 15. Specification Invariants

**TD005-SI-001.** No Specification statement SHALL exist without derivation from one or more accepted FRA requirements, Constraints, Deferred Obligations, SDA Dependencies, CGA Capabilities, Architecture Components, Architecture Decisions, or Architecture Invariants. Traceability: Section 6; Section 19.

**TD005-SI-002.** The Certified Contract Corpus (TD005-SO-001) SHALL be re-derivable from primary repository evidence on demand; a consumer SHALL NOT treat an unverifiable cached enumeration as authoritative. Traceability: TD005-ARC-001, TD005-AI-001.

**TD005-SI-003.** A Reference Baseline (TD005-SO-003) SHALL NOT be considered Established until its own provenance record is complete, including Run Engine code-version identity and execution-environment identity. Traceability: TD005-ARC-003, TD005-AI-003, TD005-AI-018.

**TD005-SI-004.** A Reference Baseline's own one-time bootstrap capture (TD005-SO-003, TD005-SO-004) SHALL be distinguished, in every provenance record, from an ordinary candidate capture. Traceability: TD005-AI-018.

**TD005-SI-005.** A Replay Session (TD005-SO-004) SHALL reach either the Captured state or the Failed state within a bounded duration; it SHALL NOT remain indefinitely in the Executing state. Traceability: TD005-ARC-011, TD005-AI-006, TD005-AI-010.

**TD005-SI-006.** A Replay Session in the Failed state SHALL NOT produce a candidate execution trajectory usable by any Observation or Comparison Specification Object. Traceability: TD005-AI-019.

**TD005-SI-007.** The Non-Interference Observation Specification (TD005-SO-007) SHALL produce no measurable difference in subsequent Run Engine behaviour as a side effect of observation. Traceability: TD005-ARC-005, TD005-AI-002.

**TD005-SI-008.** Every enumerated observable field SHALL be classified into exactly one of the four Observable Surface categories (TD005-SO-006) before being consumed by any Comparison-Semantics Specification Object. Traceability: TD005-ARC-004.

**TD005-SI-009.** Behavioural equivalence (TD005-SO-008) SHALL NEVER be evaluated as byte identity, source identity, or implementation identity. Traceability: TD005-AI-007.

**TD005-SI-010.** Trajectory-required properties (TD005-SO-010) SHALL be evaluated across the complete captured execution trajectory, not the final state alone, for every Functional Requirement the CGA's own TD005-CAP-004 identifies as trajectory-dependent. Traceability: TD005-ARC-007, TD005-CAP-004.

**TD005-SI-011.** Every numeric comparison SHALL be performed under exactly one of the two defined categories - exact-equality or tolerance-bounded - never both and never an undeclared third category; the specific tolerance value SHALL be documented at Implementation time, not chosen by this Specification. Traceability: TD005-ARC-008, Section 10.

**TD005-SI-012.** Object identity SHALL NEVER be a comparison criterion; every value comparison SHALL be evaluated by structural value equality. Traceability: TD005-ARC-009.

**TD005-SI-013.** The Regression Classification Specification (TD005-SO-013) SHALL classify every evaluated deviation into exactly one of the four defined outcomes; no deviation SHALL remain unclassified. Traceability: TD005-AI-009, TD005-AI-019, TD005-SD-001.

**TD005-SI-014.** The Regression Classification Specification SHALL NOT assign, compute, or expose severity, business acceptability, waiver status, remediation priority, or operational disposition for any classified deviation, under any of the four outcomes. Traceability: TD005-AI-009.

**TD005-SI-015.** Coverage output (TD005-SO-014, TD005-SO-015) SHALL remain advisory; no coverage report SHALL alter, override, or suppress a Classification outcome already reached. Traceability: TD005-AI-014.

**TD005-SI-016.** A Regression, Indeterminate, or Invalid Comparison outcome SHALL NOT be considered complete until its own Evidence Record (TD005-SO-016) has been composed; for an Indeterminate or Invalid Comparison outcome, an element rendered structurally unobtainable by the same condition producing the outcome SHALL be recorded as an explicit, reasoned unavailability marker rather than indefinitely blocking composition. Traceability: TD005-FR-019, TD005-SD-004.

**TD005-SI-017.** An Evidence Record, once Composed, SHALL be immutable; a subsequent independent re-evaluation of the same deviation SHALL produce a new, separate record, never an edit to the original. Traceability: TD005-AI-005.

**TD005-SI-018.** Evidence persistence (TD005-SO-017) SHALL remain within Repository Consolidation's own Normative Repository Boundary. Traceability: TD005-AI-015.

**TD005-SI-019.** The Long-Duration-Validation invocation contract (TD005-SO-018) SHALL be identical across all six mandatory validation stages; no stage-specific variant SHALL exist. Traceability: TD005-ARC-018, TD005-FR-022.

**TD005-SI-020.** The Active/Deferred Scope Boundary (TD005-SO-021) SHALL be re-evaluated, not assumed unchanged, at the start of every Replay Session and Observation Session. Traceability: TD005-AI-011.

**TD005-SI-021.** No Specification Object SHALL absorb, duplicate, or re-implement Repository Consolidation's own Executor-namespace-uniqueness protection (TD005-SO-022). Traceability: TD005-AI-012.

**TD005-SI-022.** The Specification Extension Point Registry (TD005-SO-020) SHALL record every Implementation-stage mechanism choice against a named Specification Object before that choice is considered binding. Traceability: TD005-AI-016.

All twenty-two invariants are individually numbered with no gap; none is referenced elsewhere in this document only via a compressed range.

## 16. Specification Decisions

**TD005-SD-001. Four-Outcome Classification Semantics.**
Decision: Regression Classification (TD005-SO-013) is specified with four exhaustive, mutually exclusive outcomes - Regression, Non-Regression, Indeterminate, Invalid Comparison - refining, without contradicting, TD005-ARC-017's own nominal two-outcome Purpose statement and TD005-AI-019's own separately-established failure category.
Context: the governing task's own Section 9 explicitly requires all four outcomes; the accepted Architecture named only the two nominal outcomes in TD005-ARC-017's own Purpose field, plus a separately-invariant-governed failure condition (TD005-AI-019) not framed as a classification outcome per se.
Alternatives considered: (a) retain a strictly binary classification, handling component failure entirely outside classification as Architecture's own TD005-AI-019 states, with no "Indeterminate" category; (b) the chosen four-outcome exhaustive partition, folding TD005-AI-019's failure condition into "Invalid Comparison" and adding "Indeterminate" as a genuinely new fourth category.
Scientific justification: an Indeterminate outcome is required whenever the Certification Boundary (TD005-CAP-002, MISSING) or Coverage (TD005-CAP-015, TD005-CAP-016, both carrying evidenced gaps) cannot yet confidently place a deviation inside or outside the certified-contract boundary; forcing every non-failure deviation into Regression-or-Non-Regression would manufacture false scientific confidence exactly where the CGA's own Critical- and High-risk gaps are most acute, undermining the very rigor TD005-FR-020's own behavioural-equivalence principle exists to protect.
Traceability: TD005-CAP-002, TD005-CAP-012, TD005-CAP-015, TD005-CAP-016; TD005-ARC-017; TD005-AI-009, TD005-AI-019.
Consequences: every deviation now has a scientifically honest fourth outcome available rather than being miscategorized; Evidence composition (TD005-SI-016) is correspondingly required for three of the four outcomes, not only Regression.

**TD005-SD-002. Twelfth Specification Domain Added (Repository Boundary Protection).**
Decision: the governing task's own eleven-letter domain skeleton (A through K) is extended with a twelfth domain, L, to house TD005-SO-021 and TD005-SO-022 (specifying TD005-ARC-020 and TD005-ARC-021), since no domain in A-K names this concern.
Context: mirrors the Architecture's own precedent (TD005-AD-010) of extending a given skeleton when a required Architecture Component has no coherent home within it.
Alternatives considered: (a) force TD005-SO-021/022 into an ill-fitting existing domain (for example, Governance); (b) leave TD005-ARC-020/021 unspecified, violating the governing task's own "no orphan Architecture Component" requirement; (c) the chosen new domain.
Scientific justification: Repository Boundary Protection (repository-scope stability, namespace-collision exclusion) is a scientifically distinct concern from every other domain's own subject matter; forcing it elsewhere would misrepresent its own purpose, exactly the reasoning the Architecture's own TD005-AD-010 already established for the analogous layer-extension decision.
Traceability: TD005-ARC-020, TD005-ARC-021; TD005-CAP-017, TD005-CAP-018.
Consequences: the domain count (twelve) does not match the governing task's own eleven-letter list by coincidence of naming alone; the extension is independently justified, not an unexplained deviation.

**TD005-SD-003. Per-Invocation (Session-Scoped) State Model for Replay and Observation.**
Decision: Replay (TD005-SO-004) and Observation (TD005-SO-007) are each modeled as per-invocation sessions with a bounded lifecycle (Not-Started -> ... -> a terminal state), rather than as a singleton, always-on service.
Context: the Architecture describes these components' own responsibilities but does not itself commit to a session-based versus persistent-service state model.
Alternatives considered: (a) model as a persistent, always-running service with no discrete session boundary; (b) the chosen per-invocation session model.
Scientific justification: TD005-AI-018's own "at most once per reference establishment" and "for individual comparisons" language already implies discrete, repeatable invocations, not a single continuously-running process; a session model is the only one consistent with TD005-ARC-011's own Outputs field ("a candidate execution trajectory... ready for observation," implying one trajectory produced per invocation, not a continuous stream).
Traceability: TD005-ARC-011, TD005-ARC-012, TD005-ARC-005; TD005-AI-006, TD005-AI-010, TD005-AI-018.
Consequences: every Replay and Observation state model in Section 7 defines a bounded lifecycle with explicit terminal states, enabling Implementation to reason about session boundaries, concurrency, and resource lifetime without this Specification prescribing a concrete mechanism for any of them.

**TD005-SD-004. Evidence Composition Required for Three of Four Classification Outcomes.**
Decision: a Regression, Indeterminate, or Invalid Comparison outcome (TD005-SO-013) is not considered complete until its own Evidence Record (TD005-SO-016) exists; a Non-Regression outcome does not require evidence composition.
Context: the Architecture's own Section 10 (Information Flow) places Evidence composition after Classification in the lifecycle but does not state whether an un-evidenced outcome is itself complete or merely provisional; the governing task's own four-outcome classification semantics (Section 9) newly raises the question of whether all four, or only Regression, require evidence.
Alternatives considered: (a) require evidence only for Regression, leaving Indeterminate and Invalid Comparison as bare labels; (b) require evidence for all four outcomes uniformly, including Non-Regression; (c) the chosen middle position - Regression, Indeterminate, and Invalid Comparison all require evidence; Non-Regression does not.
Scientific justification: Indeterminate and Invalid Comparison each represent an unresolved or incomplete scientific determination a future reviewer must be able to reproduce and resolve, exactly the same reproducibility need TD005-FR-019 already establishes for Regression; requiring evidence only for Regression would leave the other two "non-answers" scientifically unaccountable. Non-Regression, by contrast, is a completed, confident determination requiring no further reproduction obligation beyond what TD005-SO-003's own reference-baseline provenance already guarantees.
Traceability: TD005-FR-019; TD005-ARC-013, TD005-ARC-017; TD005-CAP-013; TD005-SD-001.
Consequences: TD005-SO-016's own Preconditions field is widened beyond a literal reading of "Regression evidence" to cover three of the four outcomes; TD005-SI-016 formalizes this precisely. This widening, in turn, requires the eight-element completeness rule itself to accommodate the reality that an Indeterminate or Invalid Comparison outcome can render specific elements (expected value, certified-contract ID, actual value) structurally unobtainable precisely because of the same condition that produced the outcome; TD005-SO-016 and TD005-SI-016 (Editorial and Scientific Review, V1.1) resolve this by requiring an explicit, reasoned unavailability marker in place of a bare omission, preserving the completeness discipline without creating an unsatisfiable requirement.

All four Specification Decisions are individually numbered with no gap; each is a genuine Specification-level decision, none merely restates an existing Architecture Decision.

## 17. Architecture Compliance

Every one of the twenty-two accepted Architecture Components is specified by exactly one Specification Object. No orphan Architecture Component exists.

| Architecture Component | Specification Object |
|---|---|
| TD005-ARC-001 | TD005-SO-001 |
| TD005-ARC-002 | TD005-SO-002 |
| TD005-ARC-003 | TD005-SO-003 |
| TD005-ARC-004 | TD005-SO-006 |
| TD005-ARC-005 | TD005-SO-007 |
| TD005-ARC-006 | TD005-SO-008 |
| TD005-ARC-007 | TD005-SO-010 |
| TD005-ARC-008 | TD005-SO-011 |
| TD005-ARC-009 | TD005-SO-012 |
| TD005-ARC-010 | TD005-SO-009 |
| TD005-ARC-011 | TD005-SO-004 |
| TD005-ARC-012 | TD005-SO-005 |
| TD005-ARC-013 | TD005-SO-016 |
| TD005-ARC-014 | TD005-SO-017 |
| TD005-ARC-015 | TD005-SO-014 |
| TD005-ARC-016 | TD005-SO-015 |
| TD005-ARC-017 | TD005-SO-013 |
| TD005-ARC-018 | TD005-SO-018 |
| TD005-ARC-019 | TD005-SO-019 |
| TD005-ARC-020 | TD005-SO-021 |
| TD005-ARC-021 | TD005-SO-022 |
| TD005-ARC-022 | TD005-SO-020 |

Every Architecture Invariant (TD005-AI-001 through TD005-AI-019) is restated or refined at the Specification-object level within at least one Specification Object's own Required/Forbidden behaviour or within a Specification Invariant (Section 15); for example, TD005-AI-004 (Comparison-layer components never mutate the reference baseline or observed candidate data) is restated within TD005-SO-008's own Forbidden behaviour and TD005-SO-010/011/012's own read-only Inputs; TD005-AI-008 (no classification outside the certified-contract boundary) is restated within TD005-SO-013's own Required behaviour governing the Regression and Non-Regression outcomes; TD005-AI-012 (no absorption of Repository Consolidation's own Executor-namespace protection) is restated within TD005-SO-022's own Forbidden behaviour and TD005-SI-021.

Every Architecture Decision (TD005-AD-001 through TD005-AD-013) is honored by the Specification Objects it governs without being repeated as a Specification Decision (Section 16's own explicit scope restriction); for example, TD005-AD-002's own separation of Reference Baseline Authority from the Certified Contract Registry is honored by TD005-SO-003's own distinct Preconditions and Outputs, never merged into TD005-SO-001 or TD005-SO-002; TD005-AD-003's own merge of Environmental Determinism into the Deterministic Replay Controller is honored by TD005-SO-004's own single Required-behaviour list, not split into two objects; TD005-AD-008's own elevation of Classification's exclusions to a binding Architecture Invariant is honored by TD005-SO-013's own Forbidden behaviour statement and TD005-SI-014.

This Specification therefore fully specifies the accepted Architecture: no Architecture Component, Invariant, or Decision is left architecturally unaddressed at the Specification level.

## 18. Implementation Readiness

For every Specification Object, this section states whether its own behavioural contract is complete and implementable as written ("Implementation Ready"), or whether a named mechanism choice remains open ("Requires Further Specification," carried forward unresolved from the Architecture's own Section 17 Specification Inputs or newly identified here). A mechanism-level gap does not mean the behavioural contract itself is incomplete; it means Implementation must still choose, and record in TD005-SO-020's own registry, a concrete realization satisfying that already-complete contract.

| Specification Object | Behavioural Contract | Implementation Readiness | Open Mechanism (if any) |
|---|---|---|---|
| TD005-SO-001 | Complete | Requires Further Specification | corpus-enumeration mechanism (format, location, maintenance process) |
| TD005-SO-002 | Complete | Requires Further Specification | per-contract-type certification-boundary application rule |
| TD005-SO-003 | Complete | Requires Further Specification | reference-reproduction mechanism (source selection; immutability-or-governed-change procedure) |
| TD005-SO-004 | Complete | Requires Further Specification | controlled-condition enumeration mechanism |
| TD005-SO-005 | Complete | Requires Further Specification | resolution of whether this remains standalone or folds into TD005-SO-003/004 (TD005-AD-004) |
| TD005-SO-006 | Complete | Implementation Ready | none |
| TD005-SO-007 | Complete | Implementation Ready | none |
| TD005-SO-008 | Complete | Implementation Ready | none (composition of TD005-SO-010/011/012 is fully specified) |
| TD005-SO-009 | Complete | Implementation Ready | none |
| TD005-SO-010 | Complete | Requires Further Specification | trajectory representation format |
| TD005-SO-011 | Complete | Requires Further Specification | tolerance value(s) and comparison implementation |
| TD005-SO-012 | Complete | Implementation Ready | none |
| TD005-SO-013 | Complete | Requires Further Specification | concrete classification procedure (the algorithm composing TD005-SO-002 and TD005-SO-008/010/011/012 into one of four outcomes) |
| TD005-SO-014 | Complete | Implementation Ready | none |
| TD005-SO-015 | Complete | Requires Further Specification | coverage mechanism and coverage-concept choice |
| TD005-SO-016 | Complete | Requires Further Specification | adoption of the SDA's own four evidence-refinement elements into a binding schema (already required by TD005-SI-003/016; the schema's own field-level format remains open) |
| TD005-SO-017 | Complete | Requires Further Specification | persistence format, retention/expiry policy, cross-stage continuity mechanism |
| TD005-SO-018 | Complete | Requires Further Specification | execution-time budget; pre-run-versus-post-run application mechanics |
| TD005-SO-019 | Complete | Implementation Ready | none |
| TD005-SO-020 | Complete | Implementation Ready | none (the registry's own structure is fully specified; its entries are the open items listed here) |
| TD005-SO-021 | Complete | Requires Further Specification | scope-drift-sensitivity mechanism; regression-capability artifact/test-code location (OQ-005), constrained to remain compatible with TD005-CON-003's own Repository-Scope Compatibility requirement |
| TD005-SO-022 | Complete | Implementation Ready | none |

Nine Specification Objects (TD005-SO-006, TD005-SO-007, TD005-SO-008, TD005-SO-009, TD005-SO-012, TD005-SO-014, TD005-SO-019, TD005-SO-020, TD005-SO-022) are fully Implementation Ready with no open mechanism. Thirteen carry an explicitly named, inherited-or-refined mechanism gap, each traceable to the Architecture's own Section 17 Specification Inputs or to a gap this Specification itself newly names (TD005-SO-016's own field-level schema format). Every open item is recorded in TD005-SO-020's own registry (Section 14); none is silently left implicit.

## 19. Traceability

Every FRA Functional Requirement, Constraint, and Deferred Obligation, every SDA Dependency, every CGA Capability, and every Open Question traces to at least one Specification Object, computed by composing the Architecture's own already-certified traceability (Architecture Section 15, five tables) with the direct Architecture-Component-to-Specification-Object mapping (Section 17 above). Each composed table is reproduced individually below, rather than left as a pointer, so every ID is directly, individually traceable within this document itself.

### 19.1 FRA Functional Requirement to Specification Object Traceability

| FRA Functional Requirement | Governing Specification Objects |
|---|---|
| TD005-FR-001 | TD005-SO-001, TD005-SO-010, TD005-SO-015 |
| TD005-FR-002 | TD005-SO-012, TD005-SO-004 |
| TD005-FR-003 | TD005-SO-010, TD005-SO-006 |
| TD005-FR-004 | TD005-SO-006, TD005-SO-007 |
| TD005-FR-005 | TD005-SO-012, TD005-SO-006, TD005-SO-007 |
| TD005-FR-006 | TD005-SO-010, TD005-SO-006, TD005-SO-007, TD005-SO-014 |
| TD005-FR-007 | TD005-SO-010, TD005-SO-011, TD005-SO-015 |
| TD005-FR-008 | TD005-SO-010, TD005-SO-011, TD005-SO-015 |
| TD005-FR-009 | TD005-SO-010, TD005-SO-011, TD005-SO-015 |
| TD005-FR-010 | TD005-SO-010, TD005-SO-011, TD005-SO-015 |
| TD005-FR-011 | TD005-SO-011 |
| TD005-FR-012 | TD005-SO-011 |
| TD005-FR-013 | TD005-SO-011, TD005-SO-006, TD005-SO-004, TD005-SO-014 |
| TD005-FR-014 | TD005-SO-001, TD005-SO-011, TD005-SO-006, TD005-SO-014 |
| TD005-FR-015 | TD005-SO-011, TD005-SO-006 |
| TD005-FR-016 | TD005-SO-011 |
| TD005-FR-017 | TD005-SO-010, TD005-SO-011 |
| TD005-FR-018 | TD005-SO-002, TD005-SO-003, TD005-SO-004, TD005-SO-013 |
| TD005-FR-019 | TD005-SO-016, TD005-SO-017, TD005-SO-018 |
| TD005-FR-020 | TD005-SO-008, TD005-SO-013 |
| TD005-FR-021 | TD005-SO-002, TD005-SO-003, TD005-SO-013 |
| TD005-FR-022 | TD005-SO-010, TD005-SO-017, TD005-SO-018 |

All twenty-two Functional Requirements individually trace to at least one Specification Object.

### 19.2 FRA Constraint to Specification Object Traceability

| FRA Constraint | Governing Specification Objects |
|---|---|
| TD005-CON-001 | TD005-SO-007 |
| TD005-CON-002 | TD005-SO-007, TD005-SO-021 |
| TD005-CON-003 | TD005-SO-017, TD005-SO-021 |
| TD005-CON-004 | TD005-SO-004, TD005-SO-005 |

All four Constraints individually trace to at least one Specification Object.

### 19.3 FRA Deferred Obligation to Specification Object Traceability

| FRA Deferred Obligation | Governing Specification Objects |
|---|---|
| Section 13.1, Active Module Coverage Obligation | TD005-SO-014, TD005-SO-015, TD005-SO-021 |
| Section 13.2, Repository-Integrity Regression Obligation | TD005-SO-022 |

Both Deferred Obligations individually trace to at least one Specification Object.

### 19.4 FRA Open Question Traceability

| Open Question | Governing Specification Object(s) |
|---|---|
| OQ-001 | TD005-SO-007 |
| OQ-002 | TD005-SO-003 |
| OQ-003 | TD005-SO-021 |
| OQ-004 | TD005-SO-018 |
| OQ-005 | TD005-SO-020, TD005-SO-021 (transferred, unresolved by this Specification, per Architecture Section 17) |
| OQ-006 | TD005-SO-008 |

All six Open Questions individually trace to at least one Specification Object; none is silently discarded.

### 19.5 SDA Dependency to Specification Object Traceability

| SDA Dependency | Governing Specification Object |
|---|---|
| TD005-DEP-001 | TD005-SO-001 |
| TD005-DEP-002 | TD005-SO-002 |
| TD005-DEP-003 | TD005-SO-001 |
| TD005-DEP-004 | TD005-SO-008 |
| TD005-DEP-005 | TD005-SO-010 |
| TD005-DEP-006 | TD005-SO-011 |
| TD005-DEP-007 | TD005-SO-006 |
| TD005-DEP-008 | TD005-SO-007 |
| TD005-DEP-009 | TD005-SO-004 |
| TD005-DEP-010 | TD005-SO-004 |
| TD005-DEP-011 | TD005-SO-012 |
| TD005-DEP-012 | TD005-SO-003 |
| TD005-DEP-013 | TD005-SO-003 |
| TD005-DEP-014 | TD005-SO-003 |
| TD005-DEP-015 | TD005-SO-010 |
| TD005-DEP-016 | TD005-SO-011 |
| TD005-DEP-017 | TD005-SO-010 |
| TD005-DEP-018 | TD005-SO-004 |
| TD005-DEP-019 | TD005-SO-007 |
| TD005-DEP-020 | TD005-SO-014 |
| TD005-DEP-021 | TD005-SO-015 |
| TD005-DEP-022 | TD005-SO-015 |
| TD005-DEP-023 | TD005-SO-016 |
| TD005-DEP-024 | TD005-SO-017 |
| TD005-DEP-025 | TD005-SO-018 |
| TD005-DEP-026 | TD005-SO-018 |
| TD005-DEP-027 | TD005-SO-017, TD005-SO-018 |
| TD005-DEP-028 | TD005-SO-021 |
| TD005-DEP-029 | TD005-SO-021 |
| TD005-DEP-030 | TD005-SO-022 |
| TD005-DEP-031 | TD005-SO-021 |
| TD005-DEP-032 | TD005-SO-009 |
| TD005-DEP-033 | TD005-SO-019 |

All thirty-three Scientific Dependencies individually trace to at least one Specification Object.

### 19.6 CGA Capability to Specification Object Traceability

| CGA Capability | Governing Specification Object |
|---|---|
| TD005-CAP-001 | TD005-SO-001 |
| TD005-CAP-002 | TD005-SO-002 |
| TD005-CAP-003 | TD005-SO-008 |
| TD005-CAP-004 | TD005-SO-010 |
| TD005-CAP-005 | TD005-SO-011 |
| TD005-CAP-006 | TD005-SO-012 |
| TD005-CAP-007 | TD005-SO-006 |
| TD005-CAP-008 | TD005-SO-007 |
| TD005-CAP-009 | TD005-SO-003 |
| TD005-CAP-010 | TD005-SO-004 |
| TD005-CAP-011 | TD005-SO-004 |
| TD005-CAP-012 | TD005-SO-013 |
| TD005-CAP-013 | TD005-SO-016 |
| TD005-CAP-014 | TD005-SO-017 |
| TD005-CAP-015 | TD005-SO-014 |
| TD005-CAP-016 | TD005-SO-015 |
| TD005-CAP-017 | TD005-SO-021 |
| TD005-CAP-018 | TD005-SO-022 |
| TD005-CAP-019 | TD005-SO-019 |
| TD005-CAP-020 | TD005-SO-018 |
| TD005-CAP-021 | TD005-SO-009 |
| TD005-CAP-022 | TD005-SO-005 (primary); TD005-SO-003, TD005-SO-004 (relationship consumers, per the Architecture's own TD005-ARC-012 precedent) |

All twenty-two Capabilities individually trace to at least one Specification Object.

Every Architecture Component traces, via Section 17 above, to exactly one Specification Object; every Architecture Decision and Architecture Invariant traces per Section 17's own worked examples and Section 15/16 above. No item at any level - Functional Requirement, Constraint, Deferred Obligation, Open Question, Dependency, Capability, Architecture Component, Architecture Decision, or Architecture Invariant - is left untraced.

## 20. Completion Criteria

This Specification is complete and ready to serve as the accepted Working Baseline for Implementation when:

- Every Specification Object is derived exclusively from the accepted FRA, SDA, CGA, and Architecture, with no object originating from an implementation idea: verified by construction (Section 7, every object's own Traceability field).
- Every object carries all thirteen required fields (Purpose, Scope, Inputs, Outputs, Preconditions, Postconditions, Required behaviour, Forbidden behaviour, Valid states, Invalid states, State transitions, Observable properties, Traceability): verified by construction (Section 7).
- Every object represents exactly one specification responsibility: verified by construction (twenty-two objects, one per Architecture Component, zero merges, zero splits beyond what the Architecture itself already established).
- At least the eleven named specification domains are analyzed, refined where evidence justified it: verified by construction (Section 7, Domains A through K represented, plus the independently-justified Domain L, TD005-SD-002).
- Behavioural contracts state required, forbidden, and (where applicable) optional behaviour, and select no implementation mechanism: verified (Section 8).
- State models are complete for every object, with valid states, invalid states, and legal/illegal transitions: verified (Section 9, Section 7).
- Comparison semantics fully specify behavioural, trajectory, and endpoint equivalence, numeric categories, comparison domains, and exclusions, without choosing a tolerance value: verified (Section 10).
- Classification semantics specify all four outcomes and explicitly exclude severity, priority, waiver, and disposition: verified (Section 11).
- Evidence specification covers contents, lifecycle, ownership, completeness, validity, and exclusions without defining a persistence mechanism: verified (Section 12).
- Coverage specification covers all five named coverage categories without defining metrics implementation: verified (Section 13).
- Extension specification covers participation, non-participation, compatibility, isolation, and governance rules: verified (Section 14).
- Specification Invariants are individually numbered, normative, and each traced to an accepted-baseline source: verified (Section 15, twenty-two invariants).
- Specification Decisions are genuine specification-level decisions, not repeated Architecture Decisions: verified (Section 16, four decisions, each with a distinct Context/Alternatives/Justification not present in any Architecture Decision).
- Every Architecture Component is fully specified, with no orphan: verified (Section 17).
- Every Specification Object's own implementation readiness is determined, with open mechanisms named explicitly: verified (Section 18).
- Every FR, Constraint, Deferred Obligation, Dependency, Capability, Architecture Component, Architecture Decision, and Architecture Invariant traces to a Specification Object, with no gap: verified (Section 19).
- No Python code, pytest test, fixture, CI/CD configuration, directory implementation, storage implementation, persistence implementation, serialization implementation, API, or concrete algorithm is created anywhere in this document: verified by construction (Section 7 through Section 19 contain no such content).

All criteria above are satisfied by this document.

## 21. Conclusion

This Specification defines twenty-two individually numbered Specification Objects (TD005-SO-001 through TD005-SO-022), one for each accepted Architecture Component, across twelve specification domains, completely specifying the behaviour required to implement the accepted TD-005 Architecture without defining implementation mechanisms. Twenty-two Specification Invariants and four genuine Specification Decisions formalize the behavioural contracts, state models, and structural refinements this Specification establishes, each individually traceable to the accepted FRA, SDA, CGA, or Architecture. The central scientific contribution of this Specification is the four-outcome Classification semantics (TD005-SD-001, TD005-SO-013) - Regression, Non-Regression, Indeterminate, Invalid Comparison - which resolves the governing task's own explicit requirement while remaining fully consistent with, and a direct refinement of, the Architecture's own TD005-ARC-017 and TD005-AI-019. Every Architecture Component is fully specified with no orphan (Section 17); every accepted-baseline requirement, dependency, capability, component, decision, and invariant traces to a Specification Object with no gap (Section 19). Nine Specification Objects are fully Implementation Ready with no remaining mechanism choice; thirteen carry an explicitly named, registry-tracked mechanism deferral (Section 18), each inherited from or refining the Architecture's own Section 17 Specification Inputs. This document selects no test framework, comparison algorithm, storage mechanism, persistence implementation, serialization format, API, or concrete numeric tolerance; every such choice is named explicitly and handed to a future Implementation stage. This document is ready to serve as the accepted Working Baseline for a future TD-005 Implementation.
