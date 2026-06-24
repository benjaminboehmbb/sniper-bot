# SSI-017 SCIENTIFIC DECISION INTELLIGENCE V2 - ARCHITECTURE REVIEW

Date:
2026-06-24

Project:
Sniper-Bot

Platform:
State Space Intelligence (SSI)

Layer:
Decision Engine / Scientific Decision Intelligence V2

Document Type:
Architecture Review

Status:
DRAFT

---

# Objective

Define the architecture for SSI-017 Scientific Decision Intelligence V2.

The objective is to improve the scientific quality of Decision Engine decisions without modifying the certified SSI core architecture.

---

# Current Architecture

Decision Engine V1 uses the following structure:

DecisionEvidenceResult

↓

DecisionValidator

↓

ScientificDecision

↓

DecisionResult

DecisionValidator contains all decision logic.

ScientificDecision is a passive scientific data object.

DecisionResult transports generated decisions and statistics.

This architecture is valid and shall be preserved.

---

# Architectural Decision

SSI-017 shall not introduce a new public scientific layer.

SSI-017 shall remain an internal evolution of the Decision Engine layer.

The certified SSI reasoning chain remains:

Observation

↓

Knowledge

↓

Evidence

↓

Decision

↓

Execution Intent

---

# Internal SSI-017 Processing Model

SSI-017 extends the internal logic of DecisionValidator.

The validator shall evaluate evidence through deterministic private assessment phases:

1. validate input
2. collect evidence
3. assess evidence sufficiency
4. assess evidence consistency
5. assess evidence completeness
6. assess scientific confidence
7. generate scientific recommendation
8. build ScientificDecision
9. build DecisionStatistics

These phases may be implemented as private methods.

They shall not become separate public components unless a later architecture review proves that separation is necessary.

---

# Proposed Internal Flow

DecisionEvidenceResult

↓

DecisionValidator.validate()

↓

_validate_input()

↓

_collect_evidence()

↓

_assess_sufficiency()

↓

_assess_consistency()

↓

_assess_completeness()

↓

_assess_confidence()

↓

_generate_recommendation()

↓

_build_decisions()

↓

DecisionResult

---

# Public API Decision

The existing public API shall remain unchanged:

DecisionEngineProcessor.process(DecisionEvidenceResult) -> DecisionResult

No additional public processor, runner, analyzer, aggregator or assessor shall be introduced in SSI-017.

Reason:

The current architecture already assigns evidence-to-decision logic to DecisionValidator.

Adding public components such as EvidenceAggregator, ConflictDetector or ConfidenceAssessor would increase API surface without clear immediate benefit.

This would weaken the Minimal Public API principle.

---

# Data Model Evolution

ScientificDecision may be extended with additional passive fields if required.

Candidate fields:

- evidence_sufficiency
- evidence_consistency
- evidence_completeness
- scientific_confidence
- scientific_recommendation

These fields describe the scientific quality assessment behind the decision.

They do not introduce execution behaviour.

They do not introduce trading behaviour.

---

# Status Model

Decision Engine V1 currently supports:

- SUPPORTED
- NOT_SUPPORTED
- UNDECIDED

SSI-017 may introduce a more precise scientific recommendation model:

- STRONGLY_SUPPORTED
- WEAKLY_SUPPORTED
- CONTRADICTORY
- INSUFFICIENT_EVIDENCE
- REVIEW_REQUIRED

Architectural note:

These should be treated as scientific recommendations or assessment outputs.

They should not be confused with execution states.

---

# Boundary to Execution Intelligence

Execution Intelligence consumes ScientificDecision objects.

Therefore SSI-017 must preserve compatibility with Execution Intelligence.

Any change to decision_status must be reviewed carefully because Execution Intelligence V1 currently maps:

SUPPORTED -> EXECUTION_APPROVED

NOT_SUPPORTED -> EXECUTION_REJECTED

UNDECIDED -> EXECUTION_DEFERRED

To avoid breaking downstream compatibility, SSI-017 should initially preserve decision_status semantics and add richer scientific assessment fields separately.

This allows Execution Intelligence to continue working while Decision Engine scientific depth improves.

---

# Compression Test

Question:

Can SSI-017 achieve the desired scientific evaluation without new public components?

Answer:

Yes.

The DecisionValidator can perform all required deterministic assessment phases internally.

Result:

PASS

---

# Removal Test

Question:

Would removing separate public evaluator classes reduce required capability?

Answer:

No, because the required capability can be implemented as private validator logic.

Result:

PASS

---

# Architectural Risks

1. Breaking Execution Intelligence dependency

Mitigation:
Preserve existing decision_status values initially.

2. Overengineering

Mitigation:
Keep assessment phases private inside DecisionValidator.

3. Domain leakage

Mitigation:
Use only scientific and domain-neutral assessment terms.

4. Hidden probabilistic interpretation

Mitigation:
Use deterministic confidence assessment only. Do not claim statistical probability.

5. Premature public API expansion

Mitigation:
Do not add public evaluator classes in SSI-017.

---

# Architecture Decision

SSI-017 shall be implemented as an internal Decision Engine V2 evolution.

The public layer architecture remains unchanged.

DecisionValidator becomes the central scientific evidence evaluation component.

ScientificDecision may be extended with passive assessment fields.

DecisionResult remains the output container.

Execution Intelligence compatibility must be preserved.

---

# Review Result

Architecture Review:

PASS

SSI-017 may proceed to Evolution Review.

