# Document Metadata

Document Class: Scientific Dependency Analysis
Document ID: P2-01-SDA
Version: V1.0
Status: Draft
Date: 2026-07-09
Project: Trading-Bot Scientific Runtime
Subsystem: Run Engine
Storage Location: docs/architecture/analysis/
Filename: P2_01_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-09.md

Depends On:
- docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md
- docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md
- docs/architecture/analysis/P2_01_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-09.md
- docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md

Referenced By:
- P2_01_CAPABILITY_GAP_ANALYSIS_V1_2026-07-09.md
- P2_01_ARCHITECTURE_V1_2026-07-09.md
- P2_01_SPECIFICATION_V1_2026-07-09.md

---

# P2-01 Scientific Dependency Analysis

## 1. Metadata

See Document Metadata block above.

---

## 2. Objective

The P2-01 Functional Requirement Analysis derived four functional requirements (P2-01-FR-001 through P2-01-FR-004) implementing P2-01's stated objectives ("Verify all Authoritative Owners. Remove duplicate ownership. Validate Ownership Matrix implementation.").

The objective of this document is to:

1. Decompose each functional requirement into its atomic scientific/technical capabilities.
2. Determine, for each atomic capability, whether it already exists as a verified output of the approved baseline and prior implementation units, or must be newly established.
3. Apply the Removal Test (as used in the P1-03 and P1-04 Scientific Dependency Analyses) to classify each candidate dependency.
4. Certify whether P2-01 may proceed directly to Capability Gap Analysis, or whether a missing prerequisite capability must first be built.

This document proposes no interfaces, no implementation, and no architecture. It uses `P2_01_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-09.md` as the primary functional input.

---

## 3. Functional Capability Decomposition

**P2-01-FR-001 (Ownership Matrix verification pass)** requires:
- A single, authoritative, complete reference table to check the implementation against.
- No runtime capability — this is a documentation/audit activity performed by direct code inspection, not by executing new code.

**P2-01-FR-002 (Performance Metrics publication into CanonicalState)** requires:
- A storage location inside `CanonicalState` capable of holding a new named field.
- A write-mediation mechanism (Writer-on-Behalf-Of) to publish a computed value into that field without granting ownership to the writer.
- The computed value itself (`PerformanceEngine`'s output), already available at the point of publication.

**P2-01-FR-003 (Runtime Status disposition decision)** requires:
- A concrete, already-defined vocabulary of Runtime Status values to decide "when" for.
- No runtime capability — this is a scoping decision, not an implementation.

**P2-01-FR-004 (Position dual-state disposition decision)** requires:
- A concrete, already-named successor unit to defer to, if deferral is chosen.
- No runtime capability — this is a scoping decision, not an implementation.

Collapsing duplicates across the four requirements yields five distinct candidate capabilities, analyzed in Section 5.

---

## 4. Scientific Dependency Graph

```text
D-001  Runtime Ownership Matrix as Definitive Reference
   │
   └──> required by FR-001 (verification pass)

D-002  CanonicalEnforcer Write-Mediation Pattern
   │
D-003  CanonicalState Extensible Storage Model
   │
   └──> D-002 + D-003 jointly required by FR-002 (Performance Metrics publication)

D-004  Named Runtime Status Vocabulary
   │
   └──> required by FR-003 (Runtime Status disposition decision)

D-005  Named Successor Unit for Position Ownership (P2-02A)
   │
   └──> required by FR-004 (Position dual-state disposition decision)
```

D-001 through D-005 are independent of one another — none derives from another, and none feeds into another. Each is a separate, freestanding prerequisite for exactly one functional requirement (D-002 and D-003 jointly serve FR-002). No circular dependency exists. No dependency inversion was identified.

---

## 5. Capability Prerequisites

**D-001 — Runtime Ownership Matrix as Definitive Reference**

Definition: A single, authoritative, complete table mapping every runtime information object to its Authoritative Owner, Computational Authority, Writer-on-Behalf-Of, and Primary Consumers.

Status: **Exists.** The Architecture Baseline's Runtime Ownership Matrix (Section "Runtime Ownership Matrix") is complete, internally reviewed (Internal Review: Ownership Review PASS, Scientific Consistency Review PASS, Architecture Integrity Review PASS, Editorial Review PASS), and already used as the reference for the concrete violations identified in the Functional Requirement Analysis (Section 4, Items 1–3).

Removal Test: If removed, FR-001 has no reference to check the implementation against — "verify all Authoritative Owners" becomes undefined, since there would be no authoritative statement of what each owner should be.

Classification: Mandatory Primary Dependency. **Already satisfied.**

---

**D-002 — CanonicalEnforcer Write-Mediation Pattern**

Definition: A uniform mechanism by which a computed value is published into `CanonicalState` on behalf of its Computational Authority, without the writer acquiring ownership (Rule OM-003: "Writer-on-Behalf-Of never establishes ownership").

Status: **Exists.** `CanonicalEnforcer` already implements this pattern identically four times — `apply_position`, `apply_pnl`, `apply_equity`, `apply_risk` — each following the same shape: `if value is None: return current; self.cs.update_<field>(value); return current`.

Removal Test: If removed, publishing Performance Metrics would require inventing a new publication mechanism rather than reusing an already-established, already-reviewed one — increasing implementation risk and creating an inconsistent pattern across `CanonicalEnforcer`'s methods.

Classification: Mandatory Dependency. **Already satisfied.**

---

**D-003 — CanonicalState Extensible Storage Model**

Definition: `CanonicalState`'s internal state representation must be capable of accepting a new named field without breaking any existing consumer.

Status: **Exists.** `CanonicalState.state` is a plain Python dictionary; every existing consumer (`CanonicalEnforcer`'s methods, `RunLoop.step()`) accesses specific keys by name rather than iterating over a fixed schema. Adding a `"performance"` key (or equivalent) is additive and does not require a schema migration.

Removal Test: If removed (i.e., if `CanonicalState` had a fixed, closed schema), adding Performance Metrics would require a breaking structural change rather than an additive one.

Classification: Mandatory Dependency. **Already satisfied.**

---

**D-004 — Named Runtime Status Vocabulary**

Definition: A concrete, already-defined enumeration of Runtime Status values, so that a disposition decision (implement now vs. defer) has a specific target.

Status: **Exists.** ADR-001 explicitly enumerates the Runtime Status values: `Initializing`, `Running`, `Paused`, `Stopping`, `Stopped`, `Error`, and declares `CanonicalState` the Authoritative Owner and `RunLoop` the Computational Authority.

Removal Test: If removed, FR-003's disposition decision would have no concrete target — "implement Runtime Status" would be undefined without a defined value set.

Classification: Mandatory Dependency (for FR-003 specifically). **Already satisfied.**

---

**D-005 — Named Successor Unit for Position Ownership (P2-02A)**

Definition: A concrete, already-scoped destination unit to defer to, if the Position dual-state pattern (Functional Requirement Analysis, Section 4, Item 1) is not resolved within P2-01 itself.

Status: **Exists.** The Implementation Baseline explicitly names `P2-02A — Position Ownership`, with stated objectives ("Implement ADR-004 Position ownership. Verify Position as the authoritative operational runtime entity. Verify that Exposure remains a Position property and never becomes an independent runtime object.").

Removal Test: If removed, FR-004's deferral option would have no principled destination — "defer" would mean "defer indefinitely," rather than "defer to a named, already-scoped unit."

Classification: Mandatory Dependency (for FR-004 specifically). **Already satisfied.**

---

## 6. Dependency Ordering

D-001 through D-005 require no ordering relative to P2-01 or to each other — all five are already satisfied, inherited unchanged from the approved Architecture Baseline and Implementation Baseline, and none derives from any of the others (Section 4).

Within P2-01's own scope, the four functional requirements may proceed independently and in any order or in parallel:

- FR-001 (matrix verification) depends only on D-001 and may begin immediately.
- FR-002 (Performance Metrics publication) depends only on D-002 and D-003 and may begin immediately, independent of FR-001, FR-003, and FR-004.
- FR-003 (Runtime Status decision) depends only on D-004 and may be resolved immediately as a documentation decision.
- FR-004 (Position dual-state decision) depends only on D-005 and may be resolved immediately as a documentation decision.

No functional requirement blocks another. This is a materially flatter dependency structure than either the P1-03 SDA (six-deep linear chain) or the P1-04 SDA (one blocking interface-wiring item plus one blocking policy decision) — consistent with P2-01 being an audit-and-conform unit rather than a behavior-implementing unit.

---

## 7. Minimal Capability Set

The minimal set of capabilities that must exist before P2-01 can be specified and implemented is:

- D-001 — Runtime Ownership Matrix as Definitive Reference
- D-002 — CanonicalEnforcer Write-Mediation Pattern
- D-003 — CanonicalState Extensible Storage Model
- D-004 — Named Runtime Status Vocabulary
- D-005 — Named Successor Unit for Position Ownership (P2-02A)

All five are **already present** in the approved baseline and current implementation as of commit `5484727` (P1-04). No capability outside this set was found to be required. Unlike P1-04 (which had one genuine interface-wiring gap, D-004 in that document's numbering), no candidate dependency in this analysis was found unsatisfied — P2-01's four functional requirements resolve entirely into audit work, one mechanical extension of an already-four-times-repeated pattern, and two scoping decisions with already-named destinations.

---

## 8. Scientific Justification

This conclusion is consistent with the Scientific Findings already recorded in the Architecture Baseline: SF-001 ("The repository already contains most major runtime capabilities") and SF-002 ("The principal architectural problem is incomplete integration rather than missing functionality") apply directly to P2-01, exactly as they applied to P1-04. P2-01 does not require building a new capability; it requires confirming that already-declared ownership assignments (Rule OM-001: "Every runtime information object possesses exactly one Authoritative Owner") are actually honored by the code, and closing the one clear, mechanical omission found (Performance Metrics publication) using a pattern (`CanonicalEnforcer`) that already exists and has already been used four times without modification.

This is also consistent with ADR-001's own framing: CanonicalState becoming the Single Source of Truth is a Phase 2 objective specifically because Phase 1 was scoped to lifecycle integration, not ownership consolidation (Implementation Dependency Graph: Phase 1 → "Certified Lifecycle Architecture"; Phase 2 → "Certified Runtime Ownership"). P2-01 beginning now, with all its prerequisite capabilities already in place, is the expected and orderly continuation of that sequencing — not an acceleration into unbuilt territory.

No Architecture Decision Record is contradicted by this conclusion. No new Authoritative Owner, Computational Authority, or canonical runtime information object is introduced by any of the five candidate dependencies — satisfying Principle IP-001 (Architecture First).

---

## 9. Risks

**R-001** — FR-001's Ownership Matrix verification is a manual, row-by-row audit. There is a risk of incompleteness if the Capability Gap Analysis does not systematically walk every row of the Matrix rather than sampling it. This should be treated as a required, not optional, methodology in the next document.

**R-002** — FR-003 and FR-004 are each genuinely open in one direction: the baseline text assigns "Verify Runtime Status ownership" to P2-02 explicitly and "Position ownership" to P2-02A explicitly, while P2-01's own objective ("Verify all Authoritative Owners") could be read as claiming both. The most internally consistent reading — that P2-01 audits and records the gap while the already-named successor units (P2-02, P2-02A) perform the fix — is not asserted here as the answer; it is left for the Architecture document, per the Functional Requirement Analysis's RQ-001/RQ-002.

**R-003** — TD-002 (unifying `_safe_float` implementations) remains adjacent to, but outside, P2-01's ownership-focused scope, per the Functional Requirement Analysis's Non-Goals. No risk of scope creep was identified in this analysis, but the Capability Gap Analysis should re-confirm this boundary explicitly.

**R-004 (carried forward)** — No automated regression test suite exists for `run_engine/core` (TD-005). Verification of FR-001 and FR-002 will be manual/interactive, consistent with the methodology already used and certified sufficient in P1-03, P1-03.1, and P1-04.

---

## 10. Conclusion

Every P2-01 functional requirement (P2-01-FR-001 through P2-01-FR-004) was decomposed into its atomic capabilities. Five distinct candidate dependencies were identified (D-001 through D-005), and all five are already satisfied by the approved Architecture Baseline, Implementation Baseline, and current implementation as of commit `5484727`. No dependency ordering constraint blocks any of the four functional requirements from proceeding immediately and independently.

**No missing prerequisite capability was identified.**

**P2-01 may proceed directly to Capability Gap Analysis.**

---

## 11. Next Document

The next document is `P2_01_CAPABILITY_GAP_ANALYSIS_V1_2026-07-09.md`.
