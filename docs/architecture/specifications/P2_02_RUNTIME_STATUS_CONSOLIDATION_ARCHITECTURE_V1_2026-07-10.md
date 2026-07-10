# Document Metadata

Document Class: Architecture Specification
Document ID: P2-02-ARCH
Version: V1.0
Status: Draft
Date: 2026-07-10
Project: Trading-Bot Scientific Runtime
Subsystem: Run Engine
Storage Location: docs/architecture/specifications/
Filename: P2_02_RUNTIME_STATUS_CONSOLIDATION_ARCHITECTURE_V1_2026-07-10.md

Depends On:
- docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md
- docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md
- docs/architecture/analysis/P2_02_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-10.md
- docs/architecture/analysis/P2_02_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-10.md
- docs/architecture/analysis/P2_02_CAPABILITY_GAP_ANALYSIS_V1_2026-07-10.md
- docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md

Referenced By:
- P2_02_SPECIFICATION_V1_2026-07-10.md

---

# P2-02 Runtime Status Consolidation — Architecture

## 1. Metadata

See Document Metadata block above.

---

## 2. Objective

The Capability Gap Analysis found a clean, closable gap for two of the six ADR-001-named Runtime Status values (`Initializing`, `Running`) and confirmed the other four (`Paused`, `Stopping`, `Stopped`, `Error`) have no attachment point in the current runtime — `RunLoop` has no lifecycle control surface at all.

The objective of this document is to make the binding architecture decision this leaves open: implement only `Initializing`/`Running` now, formally reserve the other four as valid-but-unreachable vocabulary rather than inventing fake triggers for them, and record the missing lifecycle control surface as deferred technical debt rather than building it inside this unit.

---

## 3. Scope

**In scope:** `Initializing`/`Running` publication into `CanonicalState`, via `RunLoop`, using the `CanonicalEnforcer` mediation pattern.

**Out of scope:** any trigger, control method, or state transition for `Paused`/`Stopping`/`Stopped`/`Error` (Section 9); any change to `run_engine/main.py` (Section 10); P2-02A (Position dual-state); P2-03/P2-04 (`RiskEngine` ownership, including `TD-006`); the other two P2-02 objectives ("Consolidate CanonicalState implementation," "Verify Canonical Working State semantics").

No change is proposed to `PositionEngine`, `PnLEngine`, `TradeLifecycleEngine`, `RiskEngine`, `StateEngine`, `RegimeClassifier`, `StrategySelector`, `Executor`, or `PerformanceEngine`.

---

## 4. Runtime Status Vocabulary

ADR-001 names six values. This document splits them into two disjoint groups:

**Active (implemented in this unit):**
- `INITIALIZING` — the engine has been constructed but has not yet begun ticking.
- `RUNNING` — the engine is actively processing ticks.

**Reserved (not implemented in this unit — Section 9):**
- `PAUSED`
- `STOPPING`
- `STOPPED`
- `ERROR`

The vocabulary itself is not reduced — all six remain valid, defined values per ADR-001. Only the *set of values the current implementation can actually produce* is narrowed to two, which is a statement about implementation completeness, not about the vocabulary's validity.

---

## 5. Ownership

Unchanged from ADR-001 and the Runtime Ownership Matrix: `CanonicalState` is the Authoritative Owner; `RunLoop` is the exclusive Computational Authority and Writer-on-Behalf-Of. No other component reads, writes, or derives Runtime Status. This matches the pattern already certified for every other P2-01-published field (Rule OM-001, Rule OM-003).

---

## 6. CanonicalState Publication

Following the identical, seven-times-proven `CanonicalEnforcer` mediation pattern:

- `CanonicalState` gains one new state key — `status` — initialized to `None` in `__init__` (matching the existing style of uninitialized fields prior to first write).
- `CanonicalState` gains one new method — `update_status(status)` — a direct one-line assignment, matching `update_regime`'s shape.
- `CanonicalEnforcer` gains one new method — `apply_status(status)` — following the exact existing shape (`if status is None: return current; self.cs.update_status(status); return current`).
- `RunLoop` calls `apply_status("INITIALIZING")` once, at the end of `__init__()` (after all engines/`cstate`/`enforcer` are constructed), and calls `apply_status("RUNNING")` as the **first statement inside `step()`**, before any other computation.

**Placement decision for `RUNNING`, justified:** publishing `RUNNING` as the first action inside `step()` — rather than as the last, or only once via a guarded "first call" check — is deliberate. If `RUNNING` were published only after a tick completes successfully, an exception during the very first tick (which propagates out of `step()` uncaught, per current `main.py`/`loop.py` `__main__` behavior) would leave `CanonicalState` reporting `INITIALIZING` forever, even though the engine had genuinely begun attempting to run. Publishing at the start of `step()` records the more honest signal ("a running attempt is now underway") and requires no additional state-tracking inside `RunLoop` (no `self._has_run_once` flag) — it is naturally idempotent, since every subsequent `step()` call simply re-publishes the same value.

---

## 7. Runtime Transition Model

```text
(constructed)
      │
      ▼
  INITIALIZING          ← published once, at end of RunLoop.__init__()
      │
      │  (first step() call begins)
      ▼
   RUNNING               ← published as the first statement of every step() call
      │
      │  (every subsequent step() call)
      ▼
   RUNNING               ← re-published, idempotent
```

This is the complete transition model implemented by this unit. There is no transition out of `RUNNING` into any other value — per Section 9, no code path exists to trigger one, and none is fabricated here.

---

## 8. Component Responsibilities

- **`RunLoop`** — sole computer and publisher of Runtime Status; two call sites total (`__init__()`, top of `step()`); no other new logic.
- **`CanonicalState`** — passive storage; one new key, one new method, no computation.
- **`CanonicalEnforcer`** — passive mediation; one new method, no computation, no ownership.
- **`run_engine/main.py`** — no responsibility, no change (Section 10).
- **Every other engine** (`PositionEngine`, `PnLEngine`, `TradeLifecycleEngine`, `RiskEngine`, `StateEngine`, `RegimeClassifier`, `StrategySelector`, `Executor`, `PerformanceEngine`) — no responsibility, unchanged, and none consumes Runtime Status.

---

## 9. Non-Reachable States

`PAUSED`, `STOPPING`, `STOPPED`, and `ERROR` are **not implemented** in this unit. This is a deliberate architecture decision, not an omission:

- **`PAUSED`** would require a pause command/signal. `RunLoop` has no `pause()` method and no code path that suspends ticking. None is added here.
- **`STOPPING`/`STOPPED`** would require a graceful-shutdown mechanism. `RunLoop`'s `__main__` block and `main.py`'s loop are both unconditional `while True` with no termination condition. None is added here.
- **`ERROR`** would require a fault to be recorded as a terminal or observable state. The only existing fault-adjacent mechanism — `main.py`'s `except Exception as e: print(f"[CRASH] {e}")` — is architecturally outside `RunLoop`/`CanonicalState` entirely, and swallows the exception by continuing to the next tick rather than treating it as terminal. Wiring this to `ERROR` would require `main.py` to become a Runtime Status writer-adjacent component, which is out of scope (Section 10, and Functional Requirement Analysis OQ-003, left unresolved).

Fabricating a trigger for any of these four — for example, treating a `KeyboardInterrupt` as `STOPPING`, or wrapping `step()` in a local `try/except` inside `RunLoop` to set `ERROR` — was considered and **rejected**. Each would introduce new operational behavior (interrupt handling, internal exception suppression) that no approved document specifies, and each would risk masking failures in a way that contradicts ADR-011's failure-handling philosophy (rejected/failed operations must be recorded, not silently absorbed). Per the explicit instruction governing this document, this is recorded as a documented limitation, not worked around.

**Observable behavior:** `CanonicalState.state["status"]` will only ever contain `None` (before construction — not actually observable, since it's set immediately at the end of `__init__`), `"INITIALIZING"`, or `"RUNNING"` for the lifetime of any process built on the current `RunLoop`/`main.py`. This is expected and correct given Section 9's scope decision, not a defect to be silently tolerated — it is the reason Section 10 exists.

---

## 10. Deferred Lifecycle Control Surface

The missing capability — a way for `RunLoop` to be told to pause, stop, or record a fault as a terminal state — is recorded as a new Technical Debt Register candidate, content specified here for whoever next updates that register (this document does not modify it, per this turn's constraints):

```
TD-007

Title:
RunLoop Lifecycle Control Surface

Priority:
Low

Target Phase:
P2 (or later, pending scoping)

Status:
Deferred

Source:
P2-02 Capability Gap Analysis and P2-02 Architecture

Description:
RunLoop has no pause(), stop(), or fault-recording mechanism. PAUSED, STOPPING,
STOPPED, and ERROR are valid Runtime Status vocabulary (ADR-001) but are
currently unreachable because no lifecycle control surface exists to trigger
them. main.py's existing crash-catch is architecturally disconnected from
CanonicalState and does not record faults as a Runtime Status transition.
Building this control surface — and deciding whether main.py's crash handling
should be wired into it — is a distinct capability from Runtime Status
ownership verification and should be scoped as its own unit before PAUSED,
STOPPING, STOPPED, or ERROR can be implemented.
```

This is Priority Low (not Medium/High) because the current two-value implementation (`INITIALIZING`/`RUNNING`) fully satisfies P2-02's stated objective ("verify Runtime Status ownership") for the values the runtime can actually produce; the four reserved values represent a capability gap in operational control, not an ownership-conformance defect.

---

## 11. Invariants

**INV-P2-02-001** — `CanonicalState.state["status"]` holds one of exactly two implemented values (`INITIALIZING`, `RUNNING`) for the lifetime of any process built on the current `RunLoop`; it never silently holds a value outside the ADR-001 vocabulary.

**INV-P2-02-002** — No component other than `RunLoop` computes or writes Runtime Status.

**INV-P2-02-003** — No fabricated transition exists for `PAUSED`/`STOPPING`/`STOPPED`/`ERROR`; these values are reachable only once a future unit (per `TD-007`) implements a lifecycle control surface.

**INV-P2-02-004** — Runtime Status is never derived from, or used to derive, Lifecycle State, Execution Result, Position State, or Risk State (carried forward from the Functional Requirement Analysis's RC-4/FR-005).

**INV-P2-02-005** — `RUNNING` publication in `step()` introduces no new state tracking inside `RunLoop` (no additional instance flags); it is a stateless, idempotent re-publication on every call.

---

## 12. Acceptance Criteria

**P2-02-AC-001** — `CanonicalState.state["status"] == "INITIALIZING"` immediately after `RunLoop.__init__()` returns, before any `step()` call.

**P2-02-AC-002** — `CanonicalState.state["status"] == "RUNNING"` after any `step()` call, including the first.

**P2-02-AC-003** — No component other than `RunLoop` writes `CanonicalState.state["status"]`.

**P2-02-AC-004** — No code path sets `status` to `PAUSED`, `STOPPING`, `STOPPED`, or `ERROR`.

**P2-02-AC-005** — `run_engine/main.py` is byte-for-byte unmodified by this unit.

**P2-02-AC-006** — Runtime Status is never read by, or used to compute, `Trade.status`, `execution["status"]`, `Position.position`, or any Risk Metric, and vice versa.

**P2-02-AC-007** — `python -m compileall run_engine/core` passes with no errors after implementation.

**P2-02-AC-008** — No existing `CanonicalState`/`CanonicalEnforcer` member is modified or removed; only additions are made.

---

## 13. Risks

**R-001** — `TD-007` is recommended in this document's content but not yet written to the Architecture Technical Debt Register (out of scope for modification here), mirroring the same outstanding-recommendation risk already open for `TD-006`.

**R-002** — Publishing `RUNNING` unconditionally on every `step()` call (Section 6) means `CanonicalState` cannot currently distinguish "first tick" from "tick 10,000" via Runtime Status alone — this is accepted as correct for a two-value vocabulary, but should not be mistaken for a richer signal than it is.

**R-003 (carried forward)** — No automated regression suite exists (TD-005); verification will be manual/interactive.

**R-004 (carried forward)** — The other two P2-02 baseline objectives remain unaddressed (Functional Requirement Analysis OQ-001).

---

## 14. Open Questions

**OQ-001 (carried forward, still unresolved by design)** — Should `main.py`'s crash-catch eventually be wired to `ERROR`? Explicitly deferred to `TD-007`'s future unit, not this document.

**OQ-002** — When `TD-007`'s future unit is scoped, should it also resolve `PAUSED`/`STOPPING`/`STOPPED` together, or should each reserved value be evaluated independently (e.g., a stop/shutdown mechanism might be needed sooner than a pause/resume mechanism)? Not resolved here; recommended as the first question that unit's own Functional Requirement Analysis should answer.

---

## 15. Next Document

The next document is `P2_02_SPECIFICATION_V1_2026-07-10.md`.
