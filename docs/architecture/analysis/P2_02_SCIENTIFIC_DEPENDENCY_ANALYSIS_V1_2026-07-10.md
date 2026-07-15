# Document Metadata

Document Class: Scientific Dependency Analysis
Document ID: P2-02-SDA
Version: V1.0
Status: Draft
Date: 2026-07-10
Project: Trading-Bot Scientific Runtime
Subsystem: Run Engine
Storage Location: docs/architecture/analysis/
Filename: P2_02_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-10.md

Depends On:
- docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md
- docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md
- docs/architecture/analysis/P2_02_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-10.md
- docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md

Referenced By:
- P2_02_CAPABILITY_GAP_ANALYSIS_V1_2026-07-10.md
- P2_02_ARCHITECTURE_V1_2026-07-10.md
- P2_02_SPECIFICATION_V1_2026-07-10.md

---

# P2-02 Scientific Dependency Analysis — Runtime Status Ownership

## 1. Metadata

See Document Metadata block above.

---

## 2. Objective

The P2-02 Functional Requirement Analysis derived five functional requirements (P2-02-FR-001 through P2-02-FR-005) addressing the "Verify Runtime Status ownership" objective of the P2-02 unit, and left two other P2-02 objectives, P2-02A, P2-03/P2-04, and the FR-004 implementation-vs-reserved disposition decision explicitly out of scope.

The objective of this document is to:

1. Decompose the five Runtime Status functional requirements into their atomic scientific/technical capabilities.
2. Determine, for each atomic capability, whether it already exists as a verified output of P2-01 (or earlier baseline text), or must be newly established.
3. Apply the Removal Test (as used in the P1-03, P1-04, and P2-01 Scientific Dependency Analyses) to classify each candidate dependency.
4. Explicitly determine whether Runtime Status ownership requires any missing scientific prerequisite beyond the completed P2-01 ownership consolidation, and certify readiness for Capability Gap Analysis if not.

This document analyzes **only** Runtime Status ownership. It does not include Runtime Status implementation, P2-02A Position dual-state, or `RiskEngine` ownership (P2-03/P2-04), consistent with the Functional Requirement Analysis's Non-Goals.

---

## 3. Functional Capability Decomposition

**P2-02-FR-001 (CanonicalState storage for Runtime Status)** requires:
- A concrete, already-defined vocabulary of values to store.
- A storage location inside `CanonicalState` capable of holding a new named field.

**P2-02-FR-002 (RunLoop as exclusive computer/publisher)** requires:
- A write-mediation mechanism (Writer-on-Behalf-Of) to publish a value into `CanonicalState` without granting ownership to the writer.

**P2-02-FR-003 (Initializing → Running transition at startup)** requires:
- An identifiable point in `RunLoop`'s existing code corresponding to "the engine has just started" (construction).
- An identifiable point in `RunLoop`'s existing code corresponding to "the engine is now running" (first successful tick).

**P2-02-FR-004 (recorded disposition of Paused/Stopping/Stopped/Error)** requires:
- Evidence of what `RunLoop`/`main.py` actually do today, so the decision is grounded rather than speculative. *(This document does not make the decision — Functional Requirement Analysis Non-Goals and this document's own scope explicitly exclude it — but records whether the evidence needed to make it already exists.)*

**P2-02-FR-005 (non-conflation with adjacent concepts)** requires:
- Independent, already-correct ownership of Lifecycle State, Execution Outcome, Position State, and Risk Metrics elsewhere in the system, so that Runtime Status has nothing to (incorrectly) derive from them.

Collapsing duplicates across the five requirements yields five distinct candidate capabilities, analyzed in Section 5.

---

## 4. Scientific Dependency Graph

```text
D-001  Named Runtime Status Vocabulary (ADR-001)
   │
   └──> required by FR-001, FR-004

D-002  CanonicalState Extensible Storage Model
   │
   └──> required by FR-001

D-003  CanonicalEnforcer Write-Mediation Pattern
   │
   └──> required by FR-002

D-004  RunLoop Lifecycle Hook Points (__init__, step())
   │
   └──> required by FR-003

D-005  Independently-Owned Adjacent Concepts
   │
   └──> required by FR-005 (as a non-dependency: their independence is what FR-005 relies on)
```

D-001 through D-005 are independent of one another — none derives from another, and none feeds into another. Each is a separate, freestanding prerequisite for exactly one functional requirement (D-001 serves both FR-001 and FR-004). No circular dependency exists. No dependency inversion was identified. This graph is structurally identical in shape to the P2-01 Scientific Dependency Analysis's graph (five independent, flat dependencies), and is even more mechanical, since three of the five (D-002, D-003, D-004) were not merely declared in the baseline but were actually exercised and proven correct by the P2-01 implementation itself.

---

## 5. Capability Prerequisites

**D-001 — Named Runtime Status Vocabulary**

Definition: A concrete, already-defined enumeration of Runtime Status values.

Status: **Exists.** ADR-001 explicitly enumerates: `Initializing`, `Running`, `Paused`, `Stopping`, `Stopped`, `Error`, and declares `CanonicalState` the Authoritative Owner and `RunLoop` the Computational Authority.

Removal Test: If removed, FR-001 has nothing concrete to store and FR-004's disposition decision has no defined target set to decide over.

Classification: Mandatory Primary Dependency. **Already satisfied.**

---

**D-002 — CanonicalState Extensible Storage Model**

Definition: `CanonicalState`'s internal state representation must be capable of accepting a new named field without breaking any existing consumer.

Status: **Exists, and proven three additional times.** `CanonicalState.state` is a plain Python dictionary; P2-01 already added three new keys (`strategy_selection`, `execution_decision`, `performance_metrics`) additively, with zero breakage, confirmed by full regression testing at the time.

Removal Test: If removed, adding a Runtime Status field would require a breaking schema change rather than an additive one.

Classification: Mandatory Dependency. **Already satisfied — empirically re-confirmed by P2-01, not merely asserted from the baseline.**

---

**D-003 — CanonicalEnforcer Write-Mediation Pattern**

Definition: A uniform mechanism by which a computed value is published into `CanonicalState` on behalf of its Computational Authority, without the writer acquiring ownership (Rule OM-003).

Status: **Exists, and now used seven times.** `CanonicalEnforcer` implements this pattern identically for `apply_position`, `apply_pnl`, `apply_equity`, `apply_risk` (established through P1-03.1), and `apply_strategy_selection`, `apply_execution_decision`, `apply_performance_metrics` (added in P2-01). All seven follow the same shape.

Removal Test: If removed, publishing Runtime Status would require inventing a new publication mechanism rather than reusing an already-established, seven-times-proven one.

Classification: Mandatory Dependency. **Already satisfied.**

---

**D-004 — RunLoop Lifecycle Hook Points**

Definition: Identifiable, already-existing points in `RunLoop`'s code corresponding to "just constructed" and "first tick completed," at which Runtime Status could be set without inventing new control flow.

Status: **Exists.** `RunLoop.__init__()` is the unambiguous construction point (already where `state_engine`, `regime_classifier`, `cstate`, `enforcer`, and all other engines are instantiated). `RunLoop.step()` is the unambiguous per-tick execution point; its successful return is the unambiguous "now running" signal. Neither point needs to be created — both already exist and are already the natural, sole entry points for `RunLoop`'s entire behavior.

Removal Test: If removed (i.e., if `RunLoop` had no single, deterministic construction/first-tick boundary — for example, if ticks could be processed by multiple independent entry points), FR-003's transition trigger would be ambiguous or need new orchestration machinery.

Classification: Mandatory Dependency. **Already satisfied.**

---

**D-005 — Independently-Owned Adjacent Concepts**

Definition: Lifecycle State, Execution Outcome, Position State, and Risk Metrics must each already have their own correct, independent Computational Authority and Authoritative Owner, so that Runtime Status has no incorrect incentive or shortcut to derive its value from any of them.

Status: **Exists.** The P2-01 Capability Gap Analysis's full 22-row Ownership Matrix audit (Section 5) confirms all four are independently and correctly owned today: Lifecycle State by `TradeLifecycleEngine`, Execution Outcome as part of the Execution Event row (`Executor`/`TradeLifecycleEngine`), Position by `PositionEngine`/`CanonicalState`, and Risk Metrics by `RiskEngine`/`CanonicalState`. None of them currently references or depends on any status-like field.

Removal Test: If any of the four were themselves ownership-ambiguous, a future Runtime Status implementation might be tempted to reuse or derive from that ambiguous source rather than compute status independently — this dependency is protective (its satisfaction prevents a bad shortcut), not generative.

Classification: Mandatory Dependency (as a protective precondition). **Already satisfied**, re-confirmed by the P2-01 audit rather than merely assumed.

---

## 6. Dependency Ordering

D-001 through D-005 require no ordering relative to P2-02 or to each other — all five are already satisfied, and none derives from any of the others (Section 4).

Within P2-02's Runtime Status scope, the three implementation-relevant functional requirements may proceed independently and in any order once the FR-004 disposition decision (explicitly out of scope for this document) is made:

- FR-001 (storage) depends only on D-001 and D-002.
- FR-002 (publication) depends only on D-003.
- FR-003 (Initializing/Running transition) depends only on D-001 and D-004.
- FR-005 (non-conflation) depends only on D-005, and is a constraint on how FR-001–FR-003 are implemented rather than a separate build step.

FR-004's decision does not block FR-001, FR-002, FR-003, or FR-005 — the minimal transition pair (Initializing → Running) required by FR-003 is independent of whether `Paused`/`Stopping`/`Stopped`/`Error` are ever triggered. This mirrors the P2-01 Scientific Dependency Analysis's finding of a flat, non-blocking structure.

---

## 7. Minimal Capability Set

The minimal set of capabilities that must exist before Runtime Status ownership can be specified and implemented is:

- D-001 — Named Runtime Status Vocabulary
- D-002 — CanonicalState Extensible Storage Model
- D-003 — CanonicalEnforcer Write-Mediation Pattern
- D-004 — RunLoop Lifecycle Hook Points
- D-005 — Independently-Owned Adjacent Concepts

All five are **already present**, as of commit `3b936d5` (P2-01). No capability outside this set was found to be required for the scope this document analyzes (Runtime Status ownership; not the FR-004 disposition decision, not implementation).

**Explicit determination:** Runtime Status ownership requires **no missing scientific prerequisite beyond the completed P2-01 ownership consolidation.** D-002 and D-003 are not merely present in the baseline text — they were mechanically exercised and validated three and four times respectively by P2-01's own implementation, which is stronger evidence of readiness than the P1-04 or original P2-01 analyses had available at their own time of writing (each of which found at least one item requiring net-new wiring). No such item exists here.

---

## 8. Scientific Justification

This conclusion follows directly from Scientific Findings SF-001 ("The repository already contains most major runtime capabilities") and SF-002 ("The principal architectural problem is incomplete integration rather than missing functionality"), and extends the pattern already established for P1-04 and P2-01: each successive Phase 1/Phase 2 unit has required progressively less new capability-building and progressively more mechanical application of already-proven patterns. P2-01 specifically established, tested, and certified the exact `CanonicalState`/`CanonicalEnforcer` publication mechanism (D-002, D-003) that Runtime Status now needs — this is not a coincidence but the intended effect of Phase 2's own sequencing (Runtime Ownership Consolidation, then Canonical Runtime State, in that order).

This is also consistent with ADR-001's own text, which already fully specifies Runtime Status's ownership assignment (`CanonicalState` owns, `RunLoop` computes and writes) without requiring any architectural interpretation or extension — unlike the Strategy Selection/Execution Decision case in P2-01, which required resolving an apparent tension between the Matrix and ADR-001's narrative text (P2-01 Architecture document, Section 5). No such tension exists for Runtime Status: the Matrix and the narrative agree completely.

No Architecture Decision Record is contradicted by this conclusion. No new Authoritative Owner, Computational Authority, or canonical runtime information object is introduced by any of the five candidate dependencies — satisfying Principle IP-001 (Architecture First).

---

## 9. Risks

**R-001** — This analysis's "no missing prerequisite" conclusion is scoped strictly to the minimal FR-003 transition pair (`Initializing` → `Running`) and to FR-001/FR-002/FR-005's storage/publication/non-conflation requirements. It does **not** extend to whatever the Architecture document eventually decides for `Paused`/`Stopping`/`Stopped`/`Error` (FR-004). If that decision requires, for example, wiring `main.py`'s existing crash-catch to an `Error` transition (Functional Requirement Analysis, OQ-003), a new capability — a way for `main.py` to signal into `RunLoop`/`CanonicalState`, which does not currently exist in any form — would need its own dependency analysis at that time. This is explicitly a contingent, not-yet-triggered risk, not a gap in the current certification.

**R-002** — D-005's "independently-owned adjacent concepts" status relies on the P2-01 Capability Gap Analysis's audit remaining valid. Since P2-01 introduced no changes to Lifecycle State, Execution Outcome, Position State, or Risk Metrics ownership, this reliance is judged safe, but it is a dependency on a prior document's findings rather than a fresh re-audit in this document.

**R-003 (carried forward)** — No automated regression suite exists (TD-005); verification of any future Runtime Status implementation will be manual/interactive, consistent with all prior units.

**R-004 (carried forward)** — Two of P2-02's three stated baseline objectives ("Consolidate CanonicalState implementation," "Verify Canonical Working State semantics") remain unaddressed by this document, per the Functional Requirement Analysis's Open Question OQ-001. This does not affect the Runtime Status dependency conclusion but remains open for P2-02 as a whole.

---

## 10. Conclusion

Every Runtime Status functional requirement in scope (P2-02-FR-001, FR-002, FR-003, FR-005) was decomposed into its atomic capabilities, plus the evidentiary prerequisite for FR-004's future decision. Five distinct candidate dependencies were identified (D-001 through D-005), and all five are already satisfied — three of them (D-002, D-003, D-004) not merely by baseline text but by direct mechanical proof from the P2-01 implementation itself.

**No missing scientific prerequisite beyond the completed P2-01 ownership consolidation was identified.**

**Runtime Status ownership is certified ready to proceed to Capability Gap Analysis.**

---

## 11. Next Required Document

The next document is `P2_02_CAPABILITY_GAP_ANALYSIS_V1_2026-07-10.md`.
