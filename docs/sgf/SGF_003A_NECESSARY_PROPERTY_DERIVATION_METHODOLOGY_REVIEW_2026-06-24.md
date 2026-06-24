# SGF-003A

## Necessary Property Derivation Methodology Review

---

Document ID:
SGF-003A

Title:
Necessary Property Derivation Methodology Review

Project:
Scientific Governance Foundation (SGF)

Methodology:
Scientific Derivation Methodology (SDM)

Methodology Status:
Working Baseline v1

Methodology References:

- SDM-001
- SDM-002
- SDM-003
- SDM-003A
- SDM-004
- SGF-002A
- SGF-002B

Document Type:
Methodology Review

Date:
2026-06-24

Version:
0.1

Scientific Status:
Review

Review Status:
Methodology Review

Certification Status:
Not Eligible

Repository:
Sniper-Bot / SSI

---

# Purpose

Review the appropriate scientific methodology for deriving Necessary Properties after successful scientific object recognition.

Determine whether the existing Scientific Derivation Methodology remains sufficient for Necessary Property Derivation or whether additional methodological stages become scientifically necessary.

No Necessary Properties shall be proposed or derived during this review.

---

# Scientific Question

Can Necessary Properties be derived using the existing Scientific Derivation Methodology after scientific object recognition without introducing additional methodological assumptions?

---

# Scientific Principle

Scientific properties shall not be introduced directly from observations.

Observed characteristics shall first be recognized as candidate properties.

Only after explicit scientific assessment may a candidate property be recognized as a Necessary Property.

This preserves epistemic separation between observation, candidate recognition and scientific object derivation.

---

# Inputs

Accepted inputs:

- SDM-001 Meta Architecture Review
- SDM-002 Cross-Application Validation
- SDM-003 Observation Quality Review Standard
- SDM-003A Observation and Relationship Quality Workflow Validation
- SDM-004 Scientific Object Assessment Workflow Review
- SGF-002A Constraint Investigation
- SGF-002B Constraint Object Assessment

Forbidden inputs:

- proposed Necessary Properties
- object definitions
- implementations
- architectures
- application-specific knowledge
- preferred solutions

---

# Review Objectives

Evaluate whether Necessary Property Derivation should:

- remain observation-driven,
- preserve epistemic separation,
- remain solution-neutral,
- remain domain-independent,
- preserve complete traceability,
- require additional methodological stages,
- determine whether candidate properties require explicit recognition before Necessary Property derivation.

---

# Review Sections

## MR-001 — Methodological Continuity

Status:
REVIEWED

Observation:

Necessary Property Derivation follows successful recognition of a scientific object.

Evidence:

SGF-002B recognized Constraint as an independent scientific object at the SDM Working Baseline level.

Assessment:

The existing SDM can continue after scientific object recognition because SDM already separates scientific object class, lifecycle phase and review perspective.

Decision:
PASS

Reviewer Reasoning:

No methodological discontinuity is identified. Necessary Property Derivation may proceed as the next SGF phase, provided it does not assume definitions, implementations or architecture.

---

## MR-002 — Scientific Input Sufficiency

Status:
REVIEWED

Observation:

SGF-003A requires explicit input boundaries before Necessary Property Derivation begins.

Evidence:

SDM-004 confirmed that SGF-002B preserved traceability from Object Assessment decisions back to validated observations, validated relationships and ONT results.

Assessment:

Validated SGF-002A and SGF-002B artifacts are sufficient as methodological inputs for beginning Necessary Property Derivation methodology review.

Decision:
PASS

Reviewer Reasoning:

The admissible inputs are sufficient for reviewing the derivation methodology. They are not sufficient to directly introduce Necessary Properties without further assessment.

---

## MR-003 — Epistemic Separation

Status:
REVIEWED

Observation:

Necessary Property Derivation risks category leakage if observed characteristics, candidate properties and recognized Necessary Properties are not explicitly separated.

Evidence:

SDM-001 established epistemic separation as a validated methodological principle. SDM-003 and SDM-003A further showed that OQR and RQR reduce interpretation leakage during derivation.

Assessment:

Necessary Property Derivation must preserve separation between observation, candidate property recognition and Necessary Property recognition.

Decision:
PASS

Reviewer Reasoning:

The existing methodology supports this separation, but SGF-003 must make the candidate-property stage explicit to avoid premature classification.

---

## MR-004 — Candidate Property Recognition

Status:
REVIEWED

Observation:

Necessary Property Derivation introduces a new scientific object category.

Evidence:

SDM-002D identified Necessary Property as a distinct epistemic object class and a strong future candidate after Constraint validation.

Assessment:

Observed properties should first be treated as candidate properties before they are assessed as Necessary Properties.

Decision:
PASS

Reviewer Reasoning:

Candidate Property recognition is scientifically justified because it prevents direct promotion from observation to Necessary Property. This preserves methodological consistency with prior SGF derivations.

---

## MR-005 — Workflow Adequacy

Status:
REVIEWED

Observation:

The SGF-002 object-assessment workflow was validated for recognizing a scientific object.

Evidence:

SDM-004 reviewed the SGF-002B workflow and retained it as a Working Baseline for scientific object assessment.

Assessment:

Necessary Property Derivation requires a related but not identical workflow. Object Necessity Test and Object Assessment addressed object recognition. For properties, the workflow should use Candidate Property Recognition and Necessary Property Assessment.

Decision:
PASS WITH MODIFICATION

Reviewer Reasoning:

The existing workflow remains scientifically useful, but its object-recognition stages must not be copied mechanically. The property-specific workflow should be:

Observation Collection

↓

Observation Quality Review

↓

Characteristics Analysis

↓

Relationship Quality Review

↓

Candidate Property Recognition

↓

Necessary Property Assessment

↓

Scientific Investigation

↓

Workflow Review

---

## MR-006 — Traceability Preservation

Status:
REVIEWED

Observation:

Necessary Properties must remain traceable to accepted prior evidence.

Evidence:

SDM-004 identified traceability as a passed workflow criterion during SGF-002B.

Assessment:

Each future Necessary Property must be traceable to validated observations, OQR decisions, validated relationships, RQR decisions, accepted object assessment results and reviewer reasoning.

Decision:
PASS

Reviewer Reasoning:

Traceability is preserved if SGF-003 records explicit links from every candidate property and recognized Necessary Property back to validated prior artifacts.

---

## MR-007 — Overall Methodology Assessment

Status:
REVIEWED

Observation:

MR-001 through MR-006 were completed.

Evidence:

- MR-001 Methodological Continuity passed.
- MR-002 Scientific Input Sufficiency passed.
- MR-003 Epistemic Separation passed.
- MR-004 Candidate Property Recognition passed.
- MR-005 Workflow Adequacy passed with modification.
- MR-006 Traceability Preservation passed.

Assessment:

The current SDM Working Baseline is sufficient for beginning Necessary Property Derivation, provided SGF-003 uses the modified property-specific workflow.

Decision:
PASS WITH MODIFICATION

Reviewer Reasoning:

No methodological redesign is required. A minimal workflow adaptation is justified because Necessary Property Derivation evaluates properties, not the existence of a new scientific object.

---

# Accepted SGF-003 Workflow

SGF-003 shall use the following workflow:

Observation Collection

↓

Observation Quality Review

↓

Characteristics Analysis

↓

Relationship Quality Review

↓

Candidate Property Recognition

↓

Necessary Property Assessment

↓

Scientific Investigation

↓

Workflow Review

---

# Acceptance Criteria

This review is complete only if:

- no Necessary Property has been introduced,
- no definition has been assumed,
- no implementation assumptions have been introduced,
- the admissible scientific inputs are explicitly defined,
- methodological limitations are documented,
- candidate properties are explicitly distinguished from recognized Necessary Properties.

---

# Reviewer Note

Recognition of a candidate property does not establish that the property is necessary.

Scientific necessity shall always be assessed explicitly before a Necessary Property may enter subsequent derivation stages.

This distinction prevents premature property classification and preserves conservative scientific reasoning.

---

# Review Status

Current Phase:
Methodology Review Completed

Next Phase:
SGF-003B Necessary Property Investigation
