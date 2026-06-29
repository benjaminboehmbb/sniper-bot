# Dokumentenklasse

Scientific Capability Planning Review

# Speicherort

docs/scientific_derivation/

# Dateiname

SGF_016A_0_CAPABILITY_PLANNING_REVIEW_2026-06-29.md

# Abhaengigkeiten

- SGF_015_SCIENTIFIC_FORECAST_EVALUATION_REPRESENTATION_2026-06-28.md
- SGF_015_SCIENTIFIC_CAPABILITY_CERTIFICATION_GATE_2026-06-28.md
- MR_011_SGF_015_ARCHITECTURE_REVIEW_2026-06-28.md
- MR_011_SGF_015_META_REVIEW_2026-06-28.md

# Referenziert von

- SGF_016A_1_CAPABILITY_GAP_ANALYSIS_2026-06-29.md

# Status

DRAFT - INITIAL PLANNING REVIEW

# Scientific Capability

SGF-016 - Scientific Evaluation Representation

# 1. Purpose

The purpose of this planning review is to determine whether initiation of SGF-016 is scientifically justified after completion of SGF-015.

This review does not certify SGF-016.

This review does not define the final structure of Scientific Evaluation Representation.

This review only determines whether a scientifically legitimate planning basis exists for beginning the SGF-016 derivation process.

# 2. Current Certified Scientific Core Baseline

The currently certified Scientific Core includes the following relevant capability sequence:

1. Scientific Observation Representation
2. Scientific Property Representation
3. Scientific Property Configuration Representation
4. Scientific State Representation
5. Scientific Behaviour Representation
6. Scientific Forecast Representation
7. Scientific Forecast Evaluation Representation

SGF-015 introduced Scientific Forecast Evaluation Representation.

SGF-015 is limited to representing the scientific evaluation of Forecast Representations.

SGF-015 does not represent general scientific evaluation.

SGF-015 does not execute evaluations.

SGF-015 does not select alternatives.

SGF-015 does not make decisions.

SGF-015 does not represent reasoning chains beyond the evaluation basis required for Forecast Evaluation Representation.

# 3. Planning Question

The central planning question is:

Does the certified Scientific Core require a distinct capability for representing scientific evaluation independently of Forecast Evaluation?

# 4. Initial Scientific Observation

Scientific Forecast Evaluation Representation evaluates a specific class of scientific objects:

Forecast Representations.

However, the Scientific Core may require evaluation of scientific objects that are not Forecast Representations, including but not limited to:

- Scientific Observations
- Scientific Properties
- Property Configurations
- Scientific States
- Scientific Behaviours
- Scientific Forecasts
- Scientific Capability Candidates
- Scientific Derivation Results
- Scientific Architecture Candidates

If scientific evaluation occurs only inside Forecast Evaluation Representation, then evaluation remains limited to one object class.

This creates a potential capability gap:

The Scientific Core can represent the evaluation of forecasts, but it may not yet possess a general representation for scientific evaluation itself.

# 5. Candidate Capability Identity

The candidate capability is:

Scientific Evaluation Representation

Candidate responsibility:

Represent scientific evaluation as an objective scientific information structure independent of any single evaluated object class.

This candidate responsibility remains provisional until tested by the subsequent Capability Gap Analysis, Candidate Review and Readiness Review.

# 6. Boundary Conditions

Scientific Evaluation Representation shall not perform the following responsibilities:

- execute an evaluation process
- compute evaluation scores
- optimize alternatives
- select alternatives
- make scientific decisions
- represent decision policies
- represent implementation logic
- introduce domain-specific criteria
- introduce statistical, trading, medical, robotic or other domain knowledge

Scientific Evaluation Representation may only represent evaluation information if that information can be derived as a scientific object.

# 7. Initial Dependency Expectation

The provisional dependency chain is:

Scientific Observation Representation
-> Scientific Property Representation
-> Scientific Property Configuration Representation
-> Scientific State Representation
-> Scientific Behaviour Representation
-> Scientific Forecast Representation
-> Scientific Forecast Evaluation Representation
-> Scientific Evaluation Representation

This dependency expectation is not yet certified.

It must be tested during the Scientific Dependency Analysis.

A critical open question is whether Scientific Evaluation Representation depends on Scientific Forecast Evaluation Representation or whether Forecast Evaluation Representation should be understood as a domain-specific instance of a more general Evaluation Representation.

This question must not be answered prematurely.

# 8. Scientific Necessity Hypothesis

Hypothesis:

A general Scientific Evaluation Representation may be necessary because scientific systems require the ability to represent the evaluation of scientific information classes beyond forecasts.

If this hypothesis fails during Capability Gap Analysis or Falsification Investigation, SGF-016 must be revised, delayed or rejected.

# 9. Minimality Risk

The primary minimality risk is overgeneralization.

Scientific Evaluation Representation must not become a broad container for:

- reasoning
- selection
- decision
- judgement
- optimization
- validation
- certification
- governance

These are distinct scientific or governance responsibilities and must remain separated unless later derivation proves otherwise.

# 10. Responsibility Separation Risk

The strongest separation risk concerns SGF-015.

SGF-015 already represents Forecast Evaluation.

SGF-016 must therefore prove that general Scientific Evaluation Representation is not merely a renaming or duplication of Forecast Evaluation Representation.

The next document must explicitly test:

- whether Forecast Evaluation can be generalized without architectural conflict
- whether Scientific Evaluation has an independent scientific responsibility
- whether SGF-016 introduces genuine new capability
- whether SGF-016 can be compressed into SGF-015
- whether SGF-015 should remain unchanged under methodology evolution rules

# 11. Planning Review Criteria

## PR-016-001 - Scientific Continuity

SGF-016 follows from an explicit limitation of SGF-015:

SGF-015 represents Forecast Evaluation only.

PASS.

## PR-016-002 - Capability Candidate Plausibility

A plausible scientific capability gap exists because evaluation may apply to scientific information classes beyond forecasts.

PASS.

## PR-016-003 - Responsibility Separation Awareness

The planning review identifies explicit risks of overlap with Forecast Evaluation, Selection, Decision, Reasoning, Validation and Certification.

PASS.

## PR-016-004 - Dependency Caution

The review does not assume the final dependency structure.

The dependency relation between Forecast Evaluation Representation and general Scientific Evaluation Representation remains open.

PASS.

## PR-016-005 - Domain Independence

No domain-specific concept is introduced.

PASS.

## PR-016-006 - Minimality Preservation

The review defines overgeneralization as the primary risk and requires later Removal Test and Compression Test.

PASS.

# 12. Required Next Documents

SGF-016 shall continue with:

1. SGF_016A_1_CAPABILITY_GAP_ANALYSIS_2026-06-29.md
2. SGF_016A_2_CAPABILITY_CANDIDATE_REVIEW_2026-06-29.md
3. SGF_016A_3_CAPABILITY_READINESS_REVIEW_2026-06-29.md
4. SGF_016A_4_SCIENTIFIC_CAPABILITY_FALSIFICATION_INVESTIGATION_2026-06-29.md
5. SGF_016A_5_SCIENTIFIC_PROBLEM_ANALYSIS_2026-06-29.md
6. SGF_016A_6_SCIENTIFIC_DEPENDENCY_ANALYSIS_2026-06-29.md

# 13. Planning Decision

SGF-016 is scientifically legitimate to initiate as a candidate derivation process.

SGF-016 is not yet certified.

SGF-016 is not yet proven necessary.

SGF-016 must begin with a strict Capability Gap Analysis before any capability definition is accepted.

# 14. Final Result

CAPABILITY PLANNING REVIEW PASSED

Proceed to:

SGF_016A_1_CAPABILITY_GAP_ANALYSIS_2026-06-29.md
