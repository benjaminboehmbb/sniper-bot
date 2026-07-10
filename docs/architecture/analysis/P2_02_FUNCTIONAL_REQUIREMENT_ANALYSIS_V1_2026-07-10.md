# Document Metadata

Document Class: Functional Requirement Analysis
Document ID: P2-02-FRA
Version: V1.0
Status: Draft
Date: 2026-07-10
Project: Trading-Bot Scientific Runtime
Subsystem: Run Engine
Storage Location: docs/architecture/analysis/
Filename: P2_02_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-10.md

Depends On:
- docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md
- docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md
- docs/architecture/analysis/P2_01_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-09.md
- docs/architecture/analysis/P2_01_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-09.md
- docs/architecture/analysis/P2_01_CAPABILITY_GAP_ANALYSIS_V1_2026-07-09.md
- docs/architecture/specifications/P2_01_RUNTIME_OWNERSHIP_CONSOLIDATION_ARCHITECTURE_V1_2026-07-09.md
- docs/architecture/specifications/P2_01_RUNTIME_OWNERSHIP_CONSOLIDATION_SPECIFICATION_V1_2026-07-09.md
- docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md

Referenced By:
- P2_02_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-10.md
- P2_02_CAPABILITY_GAP_ANALYSIS_V1_2026-07-10.md
- P2_02_ARCHITECTURE_V1_2026-07-10.md
- P2_02_SPECIFICATION_V1_2026-07-10.md

---

# P2-02 Functional Requirement Analysis

## 1. Metadata

See Document Metadata block above.

---

## 2. Baseline Source Identification

`docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md`, "Phase 2 Implementation Units" section, defines P2-02 explicitly (line 827):

```
## P2-02

Canonical Runtime State

Objectives
* Consolidate CanonicalState implementation.
* Verify Runtime Status ownership.
* Verify Canonical Working State semantics.
```

**Exact P2-02 item: "Canonical Runtime State," with three stated objectives.** This document — titled and structured around Runtime Status per the task that requested it — addresses **only the second objective: "Verify Runtime Status ownership."** The other two objectives ("Consolidate CanonicalState implementation" and "Verify Canonical Working State semantics") are part of the same named unit but are not exhaustively analyzed here; this is stated explicitly rather than silently narrowed, and is carried forward as Open Question OQ-001 (Section 10) so P2-02 as a whole is not prematurely considered fully scoped by this document alone.

This narrowing is judged reasonable because: (a) "Consolidate CanonicalState implementation" already received substantial treatment in P2-01 (three new fields and mediated writers added to `CanonicalState`/`CanonicalEnforcer`, following one uniform pattern); (b) "Canonical Working State semantics" (the distinction between the internal Canonical Working State during a tick and the externally observable Tick-Complete Snapshot, per ADR-001) is a distinct, separable concern from Runtime Status and was not identified as a functional gap in either the P1-04 or P2-01 governance chains; (c) Runtime Status was the one objective already explicitly identified as an unimplemented capability in both the P1-04 Final Certification (via the P2-01 chain) and the P2-01 Capability Gap Analysis (Section 4, Item 3), giving it a concrete, evidence-backed starting point that the other two objectives currently lack.

---

## 3. Current Completed Phase-2 State

- **P2-01** (Runtime Ownership Consolidation) — implemented (commit `3b936d5`, "Implement P2-01 runtime ownership consolidation") and independently verified in this session (git-diff scope check, key/method presence, publish-after-compute ordering, full call-sequence non-reordering check, P1-04 regression, `RiskEngine` non-touch — all PASS). **No dedicated `P2_01_FINAL_CERTIFICATION` document has been created yet** — unlike P1-03.1 and P1-04, which each received one. This is recorded as a gap in the certification paper trail, not a functional blocker for starting P2-02 (Section 10, OQ-002).
- P2-01 deferred three items with explicit rationale: Runtime Status → P2-02 (this document), Position dual-state/TD-001 → P2-02A, `RiskEngine` Peak-Equity/Drawdown duplication → P2-03/P2-04 (recommended as `TD-006`, not yet logged in the Technical Debt Register).
- The Runtime Ownership Matrix audit performed during P2-01 (Capability Gap Analysis, Section 5) is the most recent complete, evidence-based conformance check of the full Matrix; its "Runtime Status" row result (`GAP`) is the starting point for this document.

---

## 4. Functional Problem Statement

ADR-001 declares Runtime Status a first-class canonical concept: "Runtime Status represents the current operational execution status of the Run Engine. Examples include: Initializing, Running, Paused, Stopping, Stopped, Error. RunLoop is the exclusive Computational Authority for Runtime Status." The Runtime Ownership Matrix assigns `CanonicalState` as Authoritative Owner and `RunLoop` as both Computational Authority and Writer-on-Behalf-Of.

Direct inspection of the current runtime (`run_engine/core/*.py`, `run_engine/main.py`) confirms **no implementation of this concept exists anywhere**:

- `CanonicalState.__init__` has no `status`/`runtime_status` key (confirmed by direct reading, both before and after P2-01's additions).
- `RunLoop` computes no such value and calls no such update method.
- A repository-wide search for `Initializing|Running|Paused|Stopping|Stopped` (case-insensitive) across `run_engine/` returns no matches.

This confirms and closes out the gap the P2-01 Capability Gap Analysis identified (Section 4, Item 3) and explicitly deferred here.

**The functional problem is not ambiguous in its existence — Runtime Status is simply absent — but it is ambiguous in its required depth.** ADR-001 names six values but does not define their triggers, transitions, or which runtime events (if any) cause them. The Implementation Baseline's P2-02 objective says only "Verify Runtime Status ownership," which is consistent with a verification/audit unit (matching P2-01's own character) rather than a unit that must design a complete operational state machine from scratch. This document therefore derives the **minimal architecture-consistent scope**: establish Runtime Status as a real, owned, published, publicly observable value with a deterministic minimum transition set, without inventing operational semantics (pause/resume triggers, error-recovery policy) that no approved document currently specifies.

---

## 5. Existing Runtime Status Capabilities

**None exist.** To make this precise and to satisfy the requirement to distinguish Runtime Status from adjacent concepts, the following related-but-distinct mechanisms were found and are explicitly **not** Runtime Status:

- **Lifecycle State** (`Trade.status`, values `"OPEN"`/`"CLOSED"`, `run_engine/core/trade_lifecycle.py`) — this is the status of one individual trade, owned by `TradeLifecycleEngine`, a separate Matrix row ("Lifecycle State"). It answers "is this trade open or closed," not "is the engine running."
- **Execution Outcome Tag** (`execution["status"]`, values `"BUY_EXECUTED"`/`"SELL_EXECUTED"`/`"NOOP"`, `run_engine/core/execution/executor.py`) — this labels one order-execution attempt's immediate outcome, part of the "Execution Event" Matrix row, computed by `Executor`. It is a per-tick, per-order artifact, not a persistent engine-wide mode.
- **Position State** (`Position.position`, values `"FLAT"`/`"LONG"`/`"SHORT"`, `run_engine/core/position.py`) — this is operational market exposure, a separate Matrix row ("Position"), owned by `CanonicalState`/computed by `PositionEngine`. It answers "what market exposure do we currently hold," not "is the engine running."
- **Risk Metrics** (`drawdown`, `drawdown_ratio`, `exposure`, `run_engine/core/risk.py`) — a separate Matrix row ("Risk Metrics"/"Drawdown"), owned by `CanonicalState`/computed by `RiskEngine`. No field literally named "risk status" exists, but conceptually this answers "how risky is the current position," not "is the engine running."
- **Process-level crash handling** (`run_engine/main.py`) — the outer `while True` loop wraps `engine.step(tick)` in a bare `try/except Exception`, printing `f"[CRASH] {str(e)}"` and unconditionally continuing to the next tick on any exception. This is the only existing "is something wrong" signal in the codebase, but it is entirely external to `RunLoop`/`CanonicalState` — a crash inside `step()` is caught in `main.py`, never recorded anywhere, and has no relationship to any status concept. Whether this should ever be wired to a future `Error` Runtime Status value is a real open question (Section 10, OQ-003), not resolved by this document.

The only genuinely reusable existing capability is the `CanonicalEnforcer` Writer-on-Behalf-Of pattern established in P1-03.1 and used four additional times in P2-01 — mechanically identical to what a Runtime Status publication would need.

---

## 6. Required Runtime Status Capabilities

**RC-1** — A minimal, explicit Runtime Status vocabulary, scoped to the six values ADR-001 already names (`Initializing`, `Running`, `Paused`, `Stopping`, `Stopped`, `Error`), with no new values invented.

**RC-2** — Storage for the current Runtime Status value inside `CanonicalState`, published via the existing `CanonicalEnforcer` mediation pattern.

**RC-3** — `RunLoop` as the sole Computational Authority and Writer-on-Behalf-Of for Runtime Status, consistent with ADR-001 and the Matrix — no other component computes or writes it.

**RC-4** — Explicit non-conflation with the four adjacent concepts identified in Section 5 (Lifecycle State, Execution Outcome, Position State, Risk Metrics) and with process-level crash handling — Runtime Status answers only "what operational mode is the Run Engine itself in," never any of those.

**RC-5** — A recorded decision on the minimum viable transition set given the current runtime's actual capabilities: the current `RunLoop`/`main.py` has no pause, stop, or graceful-shutdown mechanism at all (`main.py`'s loop is unconditional `while True`, and exceptions are swallowed and looped past, not surfaced as a terminal state) — so `Paused`/`Stopping`/`Stopped`/`Error` may currently be unreachable in practice even if the vocabulary exists. This document does not resolve which values are implemented now versus reserved for a future capability (Section 10, OQ-004); it requires the decision to be made explicitly rather than left implicit.

---

## 7. Functional Requirements

**P2-02-FR-001** — `CanonicalState` shall store a `status` (or equivalently named) field holding one of the six ADR-001-defined Runtime Status values.

**P2-02-FR-002** — `RunLoop` shall be the exclusive computer and publisher of Runtime Status, via a `CanonicalEnforcer`-mediated write, following the pattern established in P1-03.1/P2-01.

**P2-02-FR-003** — Runtime Status shall transition to `Initializing` at `RunLoop.__init__()` and to `Running` at (or before) the first successful `step()` call, at minimum — this is the one transition pair unambiguously required by the current runtime's actual behavior (it does start, and it does run).

**P2-02-FR-004** — A recorded decision shall state which of `Paused`, `Stopping`, `Stopped`, `Error` are implemented now (with a concrete, evidence-based trigger) versus reserved as vocabulary for a future capability not yet present in `main.py`/`RunLoop` — no value shall be implemented with a fabricated trigger that does not correspond to real runtime behavior.

**P2-02-FR-005** — Runtime Status shall never be conflated with, computed from, or derived by reconstruction from Lifecycle State, Execution Outcome, Position State, or Risk Metrics (Rule OM-001; Principle IF-002 — no downstream reconstruction of already-available information from an unrelated source).

---

## 8. Non-Goals

- **"Consolidate CanonicalState implementation"** and **"Verify Canonical Working State semantics"** (the other two P2-02 objectives) — not addressed by this document (Section 2); may require a companion analysis before P2-02 as a whole is certified complete.
- **P2-02A** (Position dual-state / TD-001 consolidation) — explicitly a separate, already-named unit; not pulled in here.
- **P2-03/P2-04** (`RiskEngine` ownership, Equity/Peak Equity/Drawdown consistency, including the deferred `RiskEngine` Peak-Equity duplication recommended as `TD-006`) — explicitly separate, already-named units; not pulled in here.
- Designing a full operational control surface (external pause/stop commands, signal handling, graceful shutdown) for `main.py` — out of scope unless RC-5/FR-004's disposition decision requires a minimal trigger to be added; a full control surface is a distinct capability this document does not assume is needed.
- Wiring `main.py`'s existing crash-catch to an `Error` Runtime Status — an open question (OQ-003), not a requirement, since it would extend behavior beyond "verify ownership" into new error-handling design.
- TD-002, TD-004, TD-005, TD-006 — unchanged, out of scope.

---

## 9. Acceptance Criteria

**P2-02-AC-001** — `CanonicalState.state` contains a Runtime Status field populated with one of the six ADR-001-defined values at all times after `RunLoop.__init__()`.

**P2-02-AC-002** — No component other than `RunLoop` computes or writes Runtime Status.

**P2-02-AC-003** — Runtime Status is `Initializing` immediately after `RunLoop.__init__()` and `Running` by the time the first `step()` call returns.

**P2-02-AC-004** — A recorded decision (Architecture document) states explicitly which of `Paused`/`Stopping`/`Stopped`/`Error` are implemented in this unit versus reserved, with rationale grounded in actual `main.py`/`RunLoop` behavior, not speculative design.

**P2-02-AC-005** — Runtime Status is never set from, or used to derive, `Trade.status`, `execution["status"]`, `Position.position`, or any Risk Metric.

**P2-02-AC-006** — No Authoritative Owner assignment in the Runtime Ownership Matrix is changed by this unit.

**P2-02-AC-007** — `python -m compileall run_engine/core` passes with no errors after implementation.

---

## 10. Risks and Open Questions

**OQ-001** — This document scopes P2-02 down to its "Verify Runtime Status ownership" objective only (Section 2). The other two stated P2-02 objectives ("Consolidate CanonicalState implementation," "Verify Canonical Working State semantics") remain unaddressed. Before P2-02 as a named unit is considered fully certified, a decision is needed on whether those two objectives require their own analysis pass or are considered already satisfied by prior work (P2-01 for the first; no prior work identified for the second).

**OQ-002** — No `P2_01_FINAL_CERTIFICATION` document exists yet, even though P2-01 is implemented, committed, and independently verified. This does not block P2-02 functionally, but the certification paper trail has a gap that should be closed before Phase 2 as a whole is considered certified.

**OQ-003** — Should `main.py`'s existing crash-catch (`except Exception as e: print(f"[CRASH] {e}")`) ever set Runtime Status to `Error`? This would connect an existing, previously unrelated mechanism to the new capability. Not resolved here; recommended as an explicit question for the Architecture document, since answering "yes" would require `main.py` to become a Runtime Status consumer/writer-adjacent component, which is a design decision beyond "verify ownership."

**OQ-004** — Given `main.py`'s loop has no pause/stop mechanism at all today, are `Paused`, `Stopping`, and `Stopped` real requirements for P2-02, or should they be implemented as reachable-but-currently-untriggered vocabulary (satisfying "the enum exists and is owned correctly") without inventing a control surface? This is the central scope question for the Architecture document (RC-5/FR-004).

**R-001** — `TD-006` (the `RiskEngine` Peak-Equity/Drawdown duplication, recommended by the P2-01 Architecture document) still has not been logged in the Architecture Technical Debt Register. This document does not modify that register (out of scope, per this turn's constraints) but notes the recommendation remains outstanding.

**R-002 (carried forward)** — No automated regression suite exists (TD-005); verification of any P2-02 implementation will be manual/interactive, consistent with all prior units.

---

## 11. Next Required Document

The next document is `P2_02_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-10.md`.
