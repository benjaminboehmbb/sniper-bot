# SSI DECISION EVIDENCE V1 SPECIFICATION

Date:
2026-06-23

Project:
Sniper-Bot

Platform:
State Space Intelligence (SSI)

Layer:
Decision Evidence V1

Document Type:
Scientific Specification

Status:
APPROVED

---

# Purpose

Decision Evidence V1 transforms validated scientific knowledge into validated scientific evidence.

The layer does not generate decisions.

It only produces scientifically explainable evidence that may later be consumed by the Decision Engine.

---

# Input

KnowledgeExtractionResult

---

# Output

DecisionEvidenceResult

---

# Scientific Responsibility

Decision Evidence V1 shall:

* consume validated Knowledge objects
* identify scientifically meaningful knowledge combinations
* validate these combinations using deterministic rules
* generate validated DecisionEvidence objects
* produce deterministic and reproducible outputs

Decision Evidence V1 shall NOT:

* make decisions
* execute trades
* optimize behaviour
* estimate probabilities
* apply machine learning

---

# Architecture

```text
KnowledgeExtractionResult
            │
            ▼
EvidenceValidator
            │
            ▼
DecisionEvidence
            │
            ▼
DecisionEvidenceResult
```

---

# Processing Model

The EvidenceValidator evaluates all Knowledge objects.

Scientifically meaningful combinations are grouped into a single DecisionEvidence object.

Every identical input must always produce identical evidence.

---

# DecisionEvidence

Fields:

* evidence_id
* knowledge_ids
* evidence_type
* explanation
* supporting_knowledge_count
* metadata

DecisionEvidence is a passive scientific data object.

It contains no business logic.

---

# Evidence Types

Decision Evidence V1 supports:

* RepeatedStateEvidence
* NonRepeatedStateEvidence
* ForecastEvidence
* BehaviourEvidence
* CompositeEvidence

Additional evidence types may be introduced in future versions without modifying the public architecture.

---

# EvidenceValidator

Responsibilities:

* evaluate Knowledge objects
* apply deterministic evidence rules
* group compatible Knowledge objects
* create DecisionEvidence objects
* reject invalid evidence combinations

All validation rules shall remain deterministic.

---

# DecisionEvidenceResult

Contains:

* DecisionEvidence objects
* processing statistics
* validation summary

---

# Public Components

* processor.py
* validator.py
* models.py
* result.py
* renderer.py
* persistence.py
* runner.py

---

# Public API

DecisionEvidenceProcessor

process(
KnowledgeExtractionResult
)

↓

DecisionEvidenceResult

---

# Engineering Principles

* deterministic
* reproducible
* explainable
* minimal public API
* single responsibility
* compression test
* removal test

---

# Success Criteria

* all Knowledge objects processed
* deterministic evidence generation
* reproducible output
* zero validation failures
* successful end-to-end execution

---

# Out of Scope

The following belong to future SSI layers:

* Decision Engine
* Execution Intelligence
* Risk Management
* Bayesian Evidence
* Machine Learning
* Evidence Weighting
* Evidence Fusion
* Portfolio Allocation
