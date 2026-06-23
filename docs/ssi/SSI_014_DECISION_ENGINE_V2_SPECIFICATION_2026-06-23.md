# SSI-014 Decision Engine V2 Specification

Date:
2026-06-23

Project:
Sniper-Bot

Platform:
State Space Intelligence (SSI)

Document Type:
Specification

Status:
DRAFT

---

# Objective

Define SSI Decision Engine V2.

Decision Engine V2 improves the scientific decision layer without modifying the certified Scientific Core architecture.

The certified reasoning architecture remains:

Reality
Observation
Knowledge
Evidence
Decision
Execution Intent

---

# Scope

Decision Engine V2 belongs to the Decision layer.

It consumes validated Decision Evidence.

It produces deterministic scientific decisions.

It does not contain:

- trading logic
- broker logic
- portfolio logic
- risk management
- order management
- domain-specific action logic

---

# V2 Goals

Decision Engine V2 shall improve:

- evidence-to-decision mapping
- decision traceability
- decision explanation quality
- deterministic reproducibility
- validation clarity
- decision status consistency
- scientific auditability

---

# Non-Goals

Decision Engine V2 shall not introduce:

- new Scientific Core layers
- domain-specific decisions
- operational execution logic
- probabilistic model selection
- trading signals
- portfolio allocation
- runtime control logic

---

# Planned V2 Capabilities

## 1. Explicit Decision Policy

Decision Engine V2 shall use an explicit scientific decision policy.

The policy defines how evidence is transformed into decisions.

The policy must be deterministic.

---

## 2. Evidence Sufficiency Assessment

Decision Engine V2 shall assess whether available evidence is sufficient for a decision.

Possible outcomes:

- supported
- rejected
- insufficient

---

## 3. Decision Status Standardization

Decision statuses shall be explicit and documented.

Initial V2 candidate statuses:

- APPROVED
- REJECTED
- DEFERRED

These statuses remain scientific and domain-neutral.

---

## 4. Traceability Preservation

Every decision shall preserve references to all supporting evidence.

No decision may be created without traceable evidence references.

---

## 5. Explanation Improvement

Every decision shall include a concise explanation describing:

- evidence basis
- decision status
- sufficiency assessment
- reason for approval, rejection or deferral

---

# Engineering Constraints

Implementation must preserve:

- current package structure
- current certified architecture
- deterministic behavior
- ASCII-only output
- repository compile readiness
- Git-clean workflow

No broad refactoring shall be mixed into V2 implementation.

---

# Implementation Plan

Phase 1:
Specification and review

Phase 2:
Inspect current Decision Engine V1 implementation

Phase 3:
Define minimal V2 data model changes

Phase 4:
Implement Decision Policy V2

Phase 5:
Compile and targeted tests

Phase 6:
Document completion

Phase 7:
Commit and push

---

# Risk Review

Primary risks:

- accidental architecture change
- domain-specific leakage
- overengineering
- unclear decision status semantics
- breaking existing Execution Intelligence dependency

Mitigation:

- keep V2 minimal
- preserve existing interfaces where possible
- test downstream imports
- compile full tools/ssi after each change
- document all changes

---

# Initial Decision

Decision Engine V2 may proceed.

Only implementation-level improvements are allowed.

The Scientific Core architecture remains certified and frozen.

