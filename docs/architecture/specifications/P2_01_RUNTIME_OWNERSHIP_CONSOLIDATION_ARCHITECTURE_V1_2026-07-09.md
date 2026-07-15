# Document Metadata

Document Class: Architecture Specification
Document ID: P2-01-ARCH
Version: V1.0
Status: Draft
Date: 2026-07-09
Project: Trading-Bot Scientific Runtime
Subsystem: Run Engine
Storage Location: docs/architecture/specifications/
Filename: P2_01_RUNTIME_OWNERSHIP_CONSOLIDATION_ARCHITECTURE_V1_2026-07-09.md

Depends On:
- docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md
- docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md
- docs/architecture/analysis/P2_01_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-09.md
- docs/architecture/analysis/P2_01_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-09.md
- docs/architecture/analysis/P2_01_CAPABILITY_GAP_ANALYSIS_V1_2026-07-09.md

Referenced By:
- P2_01_SPECIFICATION_V1_2026-07-09.md

---

# P2-01 Runtime Ownership Consolidation — Architecture

## 1. Metadata

See Document Metadata block above.

---

## 2. Objective

The Capability Gap Analysis found seven Ownership Matrix non-conformances: three already anticipated (Runtime Status, Performance Metrics, Position/TD-001), and four newly surfaced during the row-by-row audit (Normalized Runtime State, Strategy Selection, Execution Decision, and a `RiskEngine` Peak-Equity/Drawdown duplication). It explicitly deferred disposition of the four new findings to this document.

The objective of this document is to decide, for each of the four newly discovered gaps, whether it is implemented in P2-01, deferred to P2-03/P2-04, or split across units — with every decision justified explicitly against the approved Architecture Baseline — and to define the resulting `CanonicalState` publication architecture precisely enough for direct translation into a specification.

---

## 3. Scope

**In scope for P2-01 implementation:** publication of Strategy Selection, Execution Decision, and Performance Metrics into `CanonicalState` (the "CanonicalState Publication Completeness" cluster — see Sections 5, 6, 8).

**Out of scope, deferred with explicit rationale (Section 7):** Runtime Status (→ P2-02), Position dual-state / TD-001 (→ P2-02A), `RiskEngine` Peak-Equity/Drawdown duplication (→ P2-03/P2-04).

**Out of scope, not part of this unit at all:** Unrealized PnL (capability entirely absent, not an ownership conflict — Section 7 of the Capability Gap Analysis), TD-002, TD-004, TD-005, and everything already excluded by the Functional Requirement Analysis's Non-Goals.

No change is proposed to `PositionEngine`, `PnLEngine`, `TradeLifecycleEngine`, or `RiskEngine`'s internal computation logic.

---

## 4. Runtime Ownership Principles

Governing the decisions in this document, unchanged from the baseline:

- **Rule OM-001** — Every runtime information object possesses exactly one Authoritative Owner.
- **Rule OM-003** — Writer-on-Behalf-Of never establishes ownership.
- **Rule OM-006** — `CanonicalState` exclusively owns active runtime state.
- **Rule OM-009** — No runtime component may introduce additional Authoritative Owners without an approved Architecture Evolution Review.
- **The Runtime Ownership Matrix's own precedence rule** — "This matrix is the authoritative reference for ownership responsibilities throughout the complete runtime architecture. Whenever implementation behaviour conflicts with this matrix, the matrix takes precedence."
- **Principle IP-002 (Single Logical Change)** — "Every implementation step shall modify one logical implementation unit only. Repository-wide modifications are prohibited."
- **ADR-001's scope-limiting text** — "Only information required to reconstruct the current operational runtime state shall be stored within CanonicalState," and "Strategy Context and Execution Context are transient runtime artefacts... not required to become part of the canonical operational runtime state."

The last two principles are in apparent tension for two of the four findings (Section 5), and are explicitly reconciled there rather than silently resolved in one direction.

---

## 5. Ownership Matrix Resolution

**Normalized Runtime State — resolved, no gap remains.** The Capability Gap Analysis flagged this as unpublished. On closer reading, only the *raw external input echo* (`state["raw"]`) is unpublished — the operationally relevant fields (`tick`, `price`) are already published via `CanonicalState.update_tick()`. ADR-001 explicitly limits `CanonicalState` to "information required to reconstruct the current operational runtime state," and raw input provenance is not operational state — it is the external observation the operational state was derived from. **Decision: no code change. This is not a gap.**

**Strategy Selection and Execution Decision — apparent baseline tension, resolved in favor of the Matrix.** ADR-001's narrative text states "Strategy Context and Execution Context are transient runtime artefacts... not required to become part of the canonical operational runtime state," which reads, on its face, as exempting exactly this category. However, the Runtime Ownership Matrix — a separate, more specific table in the same Architecture Baseline — explicitly lists both **"Strategy Selection"** and **"Execution Decision"** as named rows with `CanonicalState` as Authoritative Owner. These are not the same concept as the narrative's "Strategy Context"/"Execution Context": the Matrix rows name the concrete *output values* (`weights`, `decision`), not the internal computational scaffolding (e.g., `StrategySelector`'s internal `cooldown`/`last_action` state, which has no Matrix row and remains correctly non-canonical). Per the Matrix's own stated precedence rule (Section 4) and the fact that these are named, enumerated rows rather than an unnamed general category, **the Matrix governs: Strategy Selection and Execution Decision shall be published.** This apparent baseline tension is recorded as Open Question OQ-001 (Section 12) for future editorial reconciliation of the baseline text — it does not block this decision, which follows the Matrix's own explicit precedence instruction.

**Performance Metrics — confirmed gap, implement.** Unchanged from the Functional Requirement Analysis; no baseline tension.

**Decision for the publication cluster: Strategy Selection, Execution Decision, and Performance Metrics are implemented together in P2-01, as one logical change (Section 6). Normalized Runtime State requires no change.**

**Runtime Status, Position dual-state, and the `RiskEngine` duplication are each deferred — see Section 7.**

---

## 6. CanonicalState Publication Strategy

Each new publication follows the existing four-times-repeated pattern (`apply_position`/`apply_pnl`/`apply_equity`/`apply_risk`) exactly, with no structural deviation:

- `CanonicalState` gains three new state keys — `strategy_selection`, `execution_decision`, `performance` — each initialized to a neutral default (`{}` or `None`) in `__init__`, matching the existing style of `"position"`/`"pnl"` initialization.
- `CanonicalState` gains three new methods — `update_strategy_selection(weights)`, `update_execution_decision(decision)`, `update_performance(performance)` — each a direct, one-line assignment, matching `update_pnl`/`update_regime`'s existing shape.
- `CanonicalEnforcer` gains three new methods — `apply_strategy_selection(weights)`, `apply_execution_decision(decision)`, `apply_performance(performance)` — each following the exact existing shape: `if value is None: return current; self.cs.update_<field>(value); return current`.
- `RunLoop.step()` calls each new `apply_*()` method immediately after the corresponding value already exists as a local variable (`weights`, `decision`, `performance`), introducing no new computation and no reordering of the ADR-010 execution sequence.

This is purely additive: no existing `CanonicalState` key, method, or `CanonicalEnforcer` method is modified or removed.

---

## 7. Deferred Ownership Items

**Runtime Status → deferred to P2-02.** Implementing Runtime Status requires designing net-new behavior (what triggers `Paused`, `Stopping`, `Error`; whether `RunLoop` needs an explicit state machine) — this is substantive new capability, not a mechanical publication of an already-computed value, and P2-02's stated objectives explicitly and specifically claim "Verify Runtime Status ownership." Implementing it inside P2-01 would duplicate a named successor unit's charter and violate Principle IP-002 (single logical change per unit). **No code change in P2-01; disposition recorded (P2-01-AC-003 satisfied by this decision).**

**Position dual-state / TD-001 → deferred to P2-02A.** P2-02A's stated objectives explicitly claim "Implement ADR-004 Position ownership. Verify Position as the authoritative operational runtime entity." TD-001 is already logged in the Technical Debt Register with Target Phase P2, Priority Medium, Status Deferred — consistent with this decision, not contradicted by it. No divergence has been observed under the current synchronous execution model. **No code change in P2-01; disposition recorded (P2-01-AC-004 satisfied by this decision).**

**`RiskEngine` Peak-Equity/Drawdown duplication → deferred to P2-03/P2-04, not split.** This is categorically different from the publication cluster: it is a competing *computation* (a second, unauthorized Computational Authority for Peak Equity), not a missing *publication* of an already-single-sourced value. Fixing it requires touching `RiskEngine`'s internal drawdown/exposure computation logic — exactly the substance P2-03 ("Verify Equity, Peak Equity and Drawdown consistency") and P2-04 ("Verify Risk Metrics ownership. Validate deterministic RiskEngine behaviour") are named to own. A partial fix inside P2-01 (e.g., only removing the duplicate tracking without validating the full downstream exposure/drawdown-ratio consequences) risks leaving `RiskEngine` in an inconsistent intermediate state, which is worse than the current, at-least-internally-consistent duplication. **Splitting was considered and rejected**: there is no clean sub-boundary within this single defect that would leave a coherent partial state — the fix is one indivisible logical change belonging entirely to P2-03/P2-04. **No code change in P2-01.** Recommended: log as Technical Debt Register candidate `TD-006` (not written to the register in this document, per this turn's "do not modify previous documents" constraint) — target phase P2 (P2-03/P2-04), priority Medium (no current numeric divergence, but a real ADR-006/ADR-007 non-conformance).

---

## 8. Architecture Decisions

**AD-P2-01-001 — CanonicalState Publication Completeness is implemented as one cluster in P2-01.**
Motivation: three Matrix rows (Strategy Selection, Execution Decision, Performance Metrics) share an identical non-conformance shape (value computed by a single unambiguous authority, never published) and have no other named successor unit claiming them. Decision: implement all three together, using the existing `CanonicalEnforcer` pattern, with no new mechanism invented. Justification: Rule OM-001, Rule OM-006, and the Matrix's own precedence rule all require these already-Matrix-assigned owners to be honored; Principle IP-002 is satisfied because this is one logical change (uniform application of one existing pattern), not three unrelated changes.

**AD-P2-01-002 — Normalized Runtime State requires no change.**
Motivation: re-reading ADR-001's operational-state scope limit against the actual unpublished content (`raw` input echo only) shows no gap once correctly scoped. Decision: no code change. Justification: ADR-001 explicitly excludes non-operational information from `CanonicalState`.

**AD-P2-01-003 — Runtime Status, Position dual-state, and `RiskEngine` duplication are deferred, not split.**
Motivation: each has an explicit, named successor unit (P2-02, P2-02A, P2-03/P2-04 respectively) whose stated objectives directly claim the relevant scope. Decision: defer all three in full; implement none of them, even partially, in P2-01. Justification: Principle IP-002 (single logical change; repository-wide modifications prohibited) and the Implementation Baseline's Phase Transition Rules (units proceed through the approved dependency graph in sequence) both argue against reaching into another named unit's charter.

---

## 9. Invariants

**INV-P2-01-001** — Every Runtime Ownership Matrix row whose Authoritative Owner is `CanonicalState`, and whose Computational Authority already produces a value in the active execution path, is either published into `CanonicalState` via a `CanonicalEnforcer`-mediated write, or has an explicit, recorded deferral to a named successor unit. No row is left silently unresolved.

**INV-P2-01-002** — No component computes a value that another component's Computational Authority already exclusively owns, per the Matrix, without an explicit, recorded deferral (the `RiskEngine` finding is the reason this invariant is now made explicit, not a new rule).

**INV-P2-01-003** — `CanonicalState` publication changes introduced by P2-01 are purely additive; no ADR-010 execution-order change accompanies this unit.

**INV-P2-01-004** — Deferred items (Runtime Status, Position dual-state, `RiskEngine` duplication) retain their current behavior unchanged by P2-01; P2-01 does not silently alter behavior it has deferred.

---

## 10. Acceptance Criteria

**P2-01-AC-001** — Every row of the Runtime Ownership Matrix has a recorded, evidence-based conformance result (satisfied by the Capability Gap Analysis's Section 5 table plus this document's Section 5 resolution).

**P2-01-AC-002** — `CanonicalState.state` contains populated `strategy_selection`, `execution_decision`, and `performance` keys, written by `CanonicalEnforcer`, on every tick.

**P2-01-AC-003** — A recorded decision states that Runtime Status is deferred to P2-02, with rationale (Section 7).

**P2-01-AC-004** — A recorded decision states that the Position dual-state pattern is deferred to P2-02A, with rationale (Section 7).

**P2-01-AC-005** — No Authoritative Owner assignment in the Runtime Ownership Matrix is changed by this unit; only conformance to the existing Matrix is verified or brought into compliance.

**P2-01-AC-006** — `python -m compileall run_engine/core` passes with no errors after implementation.

**P2-01-AC-007 (new)** — `RiskEngine.check()`'s behavior (inputs, outputs, internal `self.peak_equity` tracking) is byte-for-byte unchanged by P2-01, confirming the deferral in Section 7 introduced no incidental modification.

**P2-01-AC-008 (new)** — No existing `CanonicalState` key, `update_*` method, or `CanonicalEnforcer` method is modified or removed by this unit; only new keys/methods are added.

---

## 11. Risks

**R-001** — The Strategy Selection / Execution Decision publication decision (Section 5) resolves an apparent tension in the approved baseline text (ADR-001 narrative vs. Runtime Ownership Matrix) in favor of the Matrix. This is the textually correct resolution per the Matrix's own precedence rule, but it means this document is making a judgment call the baseline itself does not fully disambiguate. Recorded as Open Question OQ-001 for future baseline editorial review.

**R-002** — Deferring the `RiskEngine` duplication (rather than fixing it now) leaves a real ADR-006/ADR-007 non-conformance in place through P2-01, P2-02, and P2-02A. This is judged acceptable because no numeric divergence currently exists under the synchronous execution model (Capability Gap Analysis, Section 7), and because the baseline's own sequencing explicitly assigns this territory elsewhere.

**R-003 (carried forward)** — No automated regression suite exists (TD-005); verification of the publication cluster will be manual/interactive.

**R-004** — `TD-006` (the `RiskEngine` finding) is recommended but not yet written to the Architecture Technical Debt Register, since modifying that document is out of scope for this turn. Until logged, there is a risk this finding is not tracked persistently beyond this document chain.

---

## 12. Open Questions

**OQ-001** — ADR-001's narrative text ("Strategy Context and Execution Context... not required to become part of the canonical operational runtime state") and the Runtime Ownership Matrix (which assigns `CanonicalState` as Authoritative Owner of "Strategy Selection" and "Execution Decision") are in apparent tension. This document resolves the tension in favor of the Matrix for implementation purposes (Section 5), but recommends the Architecture Baseline itself be editorially reconciled in a future Architecture Evolution Review, so the two sections no longer read as contradictory to a future reader.

**OQ-002** — Should `TD-006` (the `RiskEngine` Peak-Equity/Drawdown duplication) be logged in the Architecture Technical Debt Register now, in a dedicated follow-up action, or at the start of P2-03/P2-04? This document recommends logging it as soon as a turn is available to modify that register, so it is not lost between now and P2-03/P2-04's own governance chain.

---

## 13. Next Document

The next document is `P2_01_SPECIFICATION_V1_2026-07-09.md`.
