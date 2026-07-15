# Document Metadata

Document Class: Functional Requirement Analysis
Document ID: P2-01-FRA
Version: V1.0
Status: Draft
Date: 2026-07-09
Project: Trading-Bot Scientific Runtime
Subsystem: Run Engine
Storage Location: docs/architecture/analysis/
Filename: P2_01_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-09.md

**Provenance note:** This document was originally drafted as `P1_05_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-09.md`, before establishing (Section 2) that no P1-05 unit exists in the Implementation Baseline and that the correct next governed unit is P2-01 — Runtime Ownership Consolidation, the first unit of Phase 2. That file was deleted and this document was recreated under the corrected filename and terminology. The technical analysis is unchanged.

Depends On:
- docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md
- docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md
- docs/architecture/certification/P1_04_FINAL_CERTIFICATION_V1_2026-07-09.md
- docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md

Referenced By:
- P2_01_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-09.md
- P2_01_CAPABILITY_GAP_ANALYSIS_V1_2026-07-09.md
- P2_01_ARCHITECTURE_V1_2026-07-09.md
- P2_01_SPECIFICATION_V1_2026-07-09.md

---

# P2-01 Functional Requirement Analysis

## 1. Metadata

See Document Metadata block above.

---

## 2. Baseline Source Identification

`docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md` was searched directly (`grep -n "P1-05|P1_05"`) and returns **zero matches** anywhere in the document.

The "Phase 1 Implementation Units" section (line 716) enumerates exactly four units:

```
## P1-01   Repository Baseline Verification
## P1-02   TradeLifecycle Consolidation
## P1-03   Lifecycle Transition Implementation
## P1-04   Runtime Failure Handling
```

Immediately following P1-04, at line 813, the document begins a new section, **"Phase 2 Implementation Units,"** whose first unit (line 815) is:

```
## P2-01

Runtime Ownership Consolidation

Objectives
* Verify all Authoritative Owners.
* Remove duplicate ownership.
* Validate Ownership Matrix implementation.
```

**Exact P1-05 item found: none. P1-05 is not defined anywhere in the Implementation Baseline.** The correct next governed unit is **P2-01 — Runtime Ownership Consolidation**, the first unit of Phase 2, and this document analyzes it accordingly.

---

## 3. Current Completed Phase-1 State

All four Phase 1 Implementation Units are complete and certified:

- **P1-01** (Repository Baseline Verification) — satisfied by the Repository Validation performed at baseline creation (Architecture Baseline, "Repository Validation" section): safety branch, compilation, import validation, and Codex/architecture review all recorded PASS before implementation began.
- **P1-02** (TradeLifecycle Consolidation) — certified via `P1_02_TRADE_LIFECYCLE_CONSOLIDATION_CERTIFICATION_V1_2026-07-08.md`.
- **P1-03** (Lifecycle Transition Implementation) — implemented and validated end-to-end (commit `16765b2`, "Validate P1-03 partial close and scale-in end to end"); subsumed and re-verified by the P1-03.1 certification.
- **P1-03.1** (entry-basis ownership and quantity-validation hardening, a follow-up unit within Phase 1) — certified PASS WITH MINOR FINDINGS, officially closed, per `P1_03_1_FINAL_CERTIFICATION_V1_2026-07-09.md` (commit `57e24e6`).
- **P1-04** (Runtime Failure Handling) — certified, officially closed, per `P1_04_FINAL_CERTIFICATION_V1_2026-07-09.md` (commit `5484727`).

Phase 1's stated exit criterion — "Lifecycle implementation is fully consistent with the approved architecture" — is satisfied. The Implementation Dependency Graph records Phase 1's primary output as "Certified Lifecycle Architecture," which this state now represents.

---

## 4. Functional Problem Statement

**P1-05 is not explicitly defined in the Implementation Baseline, and this is not an ambiguity requiring interpretation.** The Phase 1 Implementation Units section is exhaustively enumerated at exactly four units (P1-01 through P1-04), all four of which are complete and certified (Section 3). There is no partial, implied, or unlabeled remainder within Phase 1 from which a "P1-05" could be derived — the section simply ends, and the document moves directly to "Phase 2 Implementation Units."

Per the Implementation Dependency Graph:

| Phase | Depends On | Primary Output |
|---|---|---|
| Phase 1 | Phase 0 | Certified Lifecycle Architecture |
| **Phase 2** | **Phase 1** | **Certified Runtime Ownership** |

and per the Phase Transition Rules ("A phase may begin only when: the previous phase has passed all validation gates, implementation certification has been completed, repository state has been committed, rollback capability has been verified"), all four conditions are satisfied for Phase 1 as of commit `5484727`.

**Conclusion: the minimal next governed implementation unit in the approved roadmap is P2-01 — Runtime Ownership Consolidation — the first unit of Phase 2, not a Phase 1 continuation.**

P2-01's stated objectives — "Verify all Authoritative Owners. Remove duplicate ownership. Validate Ownership Matrix implementation" — are an audit-and-correct unit, not a redesign. Direct inspection of the current runtime against the Runtime Ownership Matrix (Architecture Baseline) surfaces three concrete, previously unflagged violations, in addition to the one already tracked (TD-001):

1. **Position dual-state.** `RunLoop.step()` reads `position_pre = self.position_engine.snapshot()` directly from `PositionEngine`'s own instance state, not from `CanonicalState.state["position"]`. This value is then consumed by `StrategySelector`, `Executor`, and (as of P1-03.1) `PnLEngine`'s `entry_basis` input — three components reading a non-canonical copy of Position, even though `CanonicalState` is declared the Authoritative Owner. This is the general pattern of which TD-001 (`PnLEngine`'s `entry_basis` specifically) is one concrete instance.
2. **Performance Metrics are never published to CanonicalState.** The Runtime Ownership Matrix declares `CanonicalState` the Authoritative Owner of Performance Metrics and `PerformanceEngine` the Computational Authority. Direct inspection of `CanonicalState.__init__` shows no `"performance"` key in `self.state`, and `CanonicalEnforcer` has no `apply_performance` method (it defines only `apply_position`, `apply_pnl`, `apply_equity`, `apply_risk`). `PerformanceEngine.update()`'s return value is only ever placed in `RunLoop.step()`'s returned tick dictionary — it never reaches `CanonicalState`. This is a pure omission relative to the Ownership Matrix, not a design choice recorded anywhere.
3. **Runtime Status is entirely unimplemented.** ADR-001 declares `CanonicalState` the Authoritative Owner and `RunLoop` the Computational Authority for Runtime Status (`Initializing`, `Running`, `Paused`, `Stopping`, `Stopped`, `Error`). No such field exists in `CanonicalState.state`, and `RunLoop` computes no such value. This is also explicitly named as an objective of the subsequent unit P2-02 ("Verify Runtime Status ownership"), so P2-01's audit should surface it even though its resolution may belong to P2-02.

None of these three require architectural redesign — the Ownership Matrix already specifies the correct owner for each. They are omissions to be verified and, where unambiguous, closed.

---

## 5. Existing Capabilities

Verified present in the runtime as of commit `5484727` (P1-04), relevant to ownership consolidation:

- A single, explicit Runtime Ownership Matrix already exists in the Architecture Baseline and is not in dispute — this unit verifies conformance to it, not its content.
- `CanonicalEnforcer` already exists as the sole Writer-on-Behalf-Of mechanism for Position, Realized PnL, Equity, and Risk — a working, if incomplete, publication pattern that a Performance/Runtime-Status extension can follow directly.
- `PositionEngine`, `PnLEngine`, `TradeLifecycleEngine`, and `PerformanceEngine` each already have a single, unambiguous Computational Authority per the Matrix — the gap is publication into `CanonicalState`, not disputed authority over computation.
- P1-04 already established the precedent of extending an existing method's signature to carry an additional explicit value (`trade_event` into `PerformanceEngine.update()`) without introducing hidden coupling — the same pattern is directly applicable to closing the Performance Metrics publication gap.

---

## 6. Required Functional Capabilities

**RC-1** — A verification procedure that checks every row of the Runtime Ownership Matrix against the actual current implementation (which component actually writes/reads which value), producing a definitive pass/fail list rather than relying on prior partial reviews.

**RC-2** — Publication of Performance Metrics into `CanonicalState`, closing the gap identified in Section 4, Item 2.

**RC-3** — A decision on whether Runtime Status (Section 4, Item 3) is implemented within P2-01 or explicitly deferred to P2-02, since P2-02's own stated objectives already claim it.

**RC-4** — An explicit disposition (not necessarily a fix) for the Position dual-state pattern (Section 4, Item 1) and TD-001: either scoped into a dedicated follow-up unit (P2-02A, per the baseline's own sequencing) or given an interim mitigation, without attempting the full Position-ownership redesign inside P2-01 itself.

---

## 7. Functional Requirements

**P2-01-FR-001** — A verification pass shall check every row of the Runtime Ownership Matrix against the current implementation and record, for each, whether the declared Authoritative Owner is the actual sole writer of that information.

**P2-01-FR-002** — `PerformanceEngine`'s computed metrics shall be published into `CanonicalState` via a `CanonicalEnforcer`-mediated write, consistent with the existing `apply_position`/`apply_pnl`/`apply_equity`/`apply_risk` pattern.

**P2-01-FR-003** — The disposition of Runtime Status (implement now under P2-01, or formally defer to P2-02) shall be explicitly recorded, since it is currently unimplemented and claimed by both this unit's "Verify all Authoritative Owners" objective and P2-02's stated scope.

**P2-01-FR-004** — The Position dual-state pattern (Section 4, Item 1) shall be explicitly classified — as an in-scope P2-01 fix, or as scoped out to P2-02A — with a recorded rationale, since P2-01's objective is "remove duplicate ownership" but P2-02A is separately and explicitly named for Position ownership in the baseline.

---

## 8. Non-Goals

- The full Position-ownership consolidation (routing `PnLEngine`'s `entry_basis` and `StrategySelector`/`Executor`'s inputs through `CanonicalState` instead of `PositionEngine.snapshot()`) is **not** assumed to be P2-01's responsibility merely because this document surfaced it — the baseline explicitly names this as **P2-02A**, a separate unit. P2-01-FR-004 requires only a scoping decision, not the fix itself, unless that decision assigns it here.
- Financial ownership consolidation (Realized PnL cumulative tracking, Equity/Peak Equity/Drawdown consistency) is explicitly **P2-03**, not P2-01.
- Risk ownership verification is explicitly **P2-04**, not P2-01.
- TD-002 (unifying `_safe_float` implementations) remains a low-priority Phase 2 item but is not required by P2-01's stated objectives ("Verify all Authoritative Owners... Remove duplicate ownership... Validate Ownership Matrix implementation") — it concerns numeric parsing robustness, not ownership, and is not folded in here.
- TD-004 (lifecycle-based Performance evaluation, Phase 3) and TD-005 (automated test suite, project-wide) remain out of scope, unchanged from prior units.
- No redesign of `CanonicalState`'s storage model, no new persistence mechanism, no schema evolution (per ADR-012, Deferred Scope).

---

## 9. Acceptance Criteria

**P2-01-AC-001** — Every row of the Runtime Ownership Matrix has a recorded, evidence-based conformance result (PASS or FAIL) against the current implementation.

**P2-01-AC-002** — `CanonicalState.state` contains a `"performance"` (or equivalently named) key populated by `CanonicalEnforcer` from `PerformanceEngine`'s output, on every tick.

**P2-01-AC-003** — A recorded decision states explicitly whether Runtime Status is implemented in P2-01 or deferred to P2-02, with rationale.

**P2-01-AC-004** — A recorded decision states explicitly whether the Position dual-state pattern is fixed in P2-01 or deferred to P2-02A, with rationale.

**P2-01-AC-005** — No Authoritative Owner assignment in the Runtime Ownership Matrix is changed by this unit; only conformance to the existing Matrix is verified or brought into compliance.

**P2-01-AC-006** — `python -m compileall run_engine/core` passes with no errors after any implementation resulting from this analysis.

---

## 10. Risks and Open Questions

**RQ-001** — Should Runtime Status (P2-01-FR-003) be implemented now, given P2-01's own objective explicitly says "Verify all Authoritative Owners," or deferred to P2-02, which separately and explicitly claims "Verify Runtime Status ownership"? The baseline assigns this to both units' stated scope without disambiguating. This must be resolved in the P2-01 Architecture document (or its equivalent), not assumed here.

**RQ-002** — Is the Position dual-state pattern (Section 4, Item 1) severe enough to require a P2-01 interim mitigation (e.g., routing `entry_basis` through `CanonicalState` immediately) even though full Position-ownership consolidation is separately scoped to P2-02A? Under the current single-threaded, synchronous `RunLoop.step()` model, no divergence has been observed (consistent with the P1-03.1 certification's Finding 2 / TD-001), so this is a scoping risk, not a currently-active correctness defect.

**RQ-003 (resolved)** — This document was originally drafted under a "P1-05" filename while its content analyzed P2-01. The user has since confirmed the correct naming convention: `P2_01_*` for this unit. The document was deleted and recreated accordingly (see Provenance note). No further naming ambiguity remains for this unit.

**RQ-004** — No independent Codex review has been performed on the finding that P1-05 does not exist and P2-01 is the correct next unit. This is a documentation/process observation only; it does not affect the correctness of the baseline-text finding in Section 2, which is a direct, verifiable search result.

---

## 11. Next Required Document

The next document is `P2_01_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-09.md`, following the same governance sequence used for P1-03 and P1-04 (Functional Requirement Analysis → Scientific Dependency Analysis → Capability Gap Analysis → Architecture → Specification → Implementation → Certification).
