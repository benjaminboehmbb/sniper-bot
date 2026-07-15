# Document Metadata

Document Class: Implementation Specification
Document ID: P2-02A
Version: V1.0
Status: Implementation Preparation
Date: 2026-07-10
Project: Trading-Bot Scientific Runtime
Subsystem: Run Engine
Storage Location: docs/architecture/specifications/
Filename: P2_02_RUNTIME_STATUS_CONSOLIDATION_SPECIFICATION_V1_2026-07-10.md

Depends On:
- docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md
- docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md
- docs/architecture/analysis/P2_02_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-10.md
- docs/architecture/analysis/P2_02_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-10.md
- docs/architecture/analysis/P2_02_CAPABILITY_GAP_ANALYSIS_V1_2026-07-10.md
- docs/architecture/specifications/P2_02_RUNTIME_STATUS_CONSOLIDATION_ARCHITECTURE_V1_2026-07-10.md

Referenced By:
- P2-02 Implementation
- P2-02 Validation
- P2-02 Certification

---

# P2-02 Runtime Status Consolidation — Implementation Specification

## 1. Metadata

See Document Metadata block above.

---

## 2. Objective

This specification defines the exact, file-level implementation contract for P2-02 (Runtime Status ownership), translating the architecture decisions in `P2_02_RUNTIME_STATUS_CONSOLIDATION_ARCHITECTURE_V1_2026-07-10.md` into precise code changes.

Binding scope carried forward from the Architecture document (not renegotiated here):

- `CanonicalState` gains a `runtime_status` field.
- Valid vocabulary: `INITIALIZING`, `RUNNING`, `PAUSED`, `STOPPING`, `STOPPED`, `ERROR` — all six are valid values; only the first two are ever produced by this implementation.
- `RunLoop.__init__()` publishes `INITIALIZING` exactly once.
- `RunLoop.step()` publishes `RUNNING` as its first runtime-status action.
- No fabricated transition exists anywhere for `PAUSED`, `STOPPING`, `STOPPED`, or `ERROR`.
- `run_engine/main.py` is not modified.

---

## 3. Files in Scope

- `run_engine/core/canonical_state.py` — code change required.
- `run_engine/core/canonical_enforcer.py` — code change required.
- `run_engine/core/loop.py` — code change required (two call-site additions).

---

## 4. Files Out of Scope

- `run_engine/main.py` — explicitly unchanged (Architecture document, Section 10; Acceptance Criteria P2-02-AC-005).
- `run_engine/core/position.py`, `run_engine/core/pnl.py` — Position/financial ownership belongs to P2-02A/P2-03, not touched.
- `run_engine/core/risk.py` — `RiskEngine` ownership belongs to P2-03/P2-04 (`TD-006`), not touched.
- `run_engine/core/trade_lifecycle.py`, `run_engine/core/performance.py`, `run_engine/core/state.py`, `run_engine/core/regime.py`, `run_engine/core/strategy.py`, `run_engine/core/execution/executor.py` — none owns, computes, or consumes Runtime Status.

---

## 5. Required Code Changes

Exactly three additions, each minimal:

1. `CanonicalState.__init__` gains a `runtime_status` key (default `None`), and `CanonicalState` gains one new method, `update_runtime_status(runtime_status)`, a direct one-line assignment matching the existing `update_regime` shape.
2. `CanonicalEnforcer` gains one new method, `apply_runtime_status(runtime_status)`, following the exact existing shape used by the seven current `apply_*` methods.
3. `RunLoop.__init__()` gains one call — `self.enforcer.apply_runtime_status("INITIALIZING")` — as its last statement. `RunLoop.step()` gains one call — `self.enforcer.apply_runtime_status("RUNNING")` — as its **first** statement, before `state = self.state_engine.update(tick)`.

No other function, class, method, or file changes. No new constant module, enum class, or vocabulary-validation logic is introduced — the six values are used as plain strings, consistent with every other status-like field already in the codebase (`Position.position`, `Trade.status`, `execution["status"]`, `LifecycleEvent.event_type`, `regime`), none of which uses an enum type.

---

## 6. canonical_state.py Specification

**Current relevant lines:**

```python
            "performance_metrics": None
        }

    def update_tick(self, tick, price):
```

**Required lines:**

```python
            "performance_metrics": None,

            "runtime_status": None
        }

    def update_tick(self, tick, price):
```

**Current relevant lines:**

```python
    def update_performance_metrics(self, performance_metrics):

        self.state["performance_metrics"] = performance_metrics

    def get(self):
```

**Required lines:**

```python
    def update_performance_metrics(self, performance_metrics):

        self.state["performance_metrics"] = performance_metrics

    def update_runtime_status(self, runtime_status):

        self.state["runtime_status"] = runtime_status

    def get(self):
```

Only the `__init__` dict (one new key, appended after `"performance_metrics"`) and one new method (appended after `update_performance_metrics`) change. No existing key, method, or line is modified.

---

## 7. canonical_enforcer.py Specification

**Current relevant lines (end of file):**

```python
    def apply_performance_metrics(self, performance_metrics):

        if performance_metrics is None:
            return self.cs.get()["performance_metrics"]

        self.cs.update_performance_metrics(performance_metrics)
        return self.cs.get()["performance_metrics"]
```

**Required addition (appended after `apply_performance_metrics`):**

```python
    def apply_performance_metrics(self, performance_metrics):

        if performance_metrics is None:
            return self.cs.get()["performance_metrics"]

        self.cs.update_performance_metrics(performance_metrics)
        return self.cs.get()["performance_metrics"]

    def apply_runtime_status(self, runtime_status):

        if runtime_status is None:
            return self.cs.get()["runtime_status"]

        self.cs.update_runtime_status(runtime_status)
        return self.cs.get()["runtime_status"]
```

No existing method changes in any way. This method performs no validation of `runtime_status` against the six-value vocabulary — validation, if ever required, is a future concern outside this unit's scope (Architecture document, Section 5: `CanonicalEnforcer` is passive mediation only).

---

## 8. loop.py Specification

**Current lines (`RunLoop.__init__`):**

```python
        self.cstate = CanonicalState()
        self.enforcer = CanonicalEnforcer(self.cstate)

    def step(self, tick):

        state = self.state_engine.update(tick)
```

**Required lines:**

```python
        self.cstate = CanonicalState()
        self.enforcer = CanonicalEnforcer(self.cstate)

        self.enforcer.apply_runtime_status("INITIALIZING")

    def step(self, tick):

        self.enforcer.apply_runtime_status("RUNNING")

        state = self.state_engine.update(tick)
```

This is the only change to `loop.py`. `apply_runtime_status("INITIALIZING")` is the last statement of `__init__()`, after `self.enforcer` itself has been constructed (it must be — the call depends on it). `apply_runtime_status("RUNNING")` is the first statement of `step()`, preceding even `state = self.state_engine.update(tick)`, per the Architecture document's explicit placement justification (Section 6: recording "a running attempt is now underway" before any computation that could raise, rather than only after success).

No other line in `loop.py` changes. The `__main__` block is unmodified.

---

## 9. Validation Requirements

**Validation Group 1 — Initial State**

Verify that immediately after `RunLoop()` construction, before any `step()` call, `engine.cstate.get()["runtime_status"] == "INITIALIZING"`.

PASS Criteria: exact string match.

---

**Validation Group 2 — Running Transition**

Verify that after any `step()` call (including the first), `engine.cstate.get()["runtime_status"] == "RUNNING"`.

PASS Criteria: exact string match, on the first call and on subsequent calls.

---

**Validation Group 3 — No Fabricated Transitions**

Verify, by direct code inspection and by running a multi-tick sequence (including a tick that produces a `RUNTIME_FAILURE_EVENT`), that `runtime_status` is never observed as `PAUSED`, `STOPPING`, `STOPPED`, or `ERROR`.

PASS Criteria: `runtime_status` is `INITIALIZING` or `RUNNING` at every observation point; no other value ever appears.

---

**Validation Group 4 — Exclusive Writer**

Verify, by repository-wide search, that `update_runtime_status`/`apply_runtime_status` are called only from `RunLoop`, and that no other module reads `runtime_status` to compute any other value (confirms Architecture document INV-P2-02-002/INV-P2-02-004).

PASS Criteria: exactly two call sites (`RunLoop.__init__`, `RunLoop.step`), both in `loop.py`; zero read-dependencies from `runtime_status` elsewhere.

---

**Validation Group 5 — `main.py` Non-Regression**

Verify `run_engine/main.py` is byte-for-byte unmodified.

PASS Criteria: `git diff -- run_engine/main.py` is empty.

---

**Validation Group 6 — Full Regression (P1-04 / P2-01 scenarios)**

Re-run the P1-04 rejected/accepted transition scenarios and the P2-01 publication scenarios (`strategy_selection`, `execution_decision`, `performance_metrics`) to confirm all previously certified results are unchanged.

PASS Criteria: identical to the results certified in `P1_04_FINAL_CERTIFICATION_V1_2026-07-09.md` and `P2_01_FINAL_CERTIFICATION_V1_2026-07-10.md`.

---

**Validation Group 7 — Static Validation**

`python -m compileall run_engine/core` passes with no errors after implementation.

---

## 10. Acceptance Criteria

Restated from the Architecture document (Section 12), with implementation status:

- **P2-02-AC-001** — `runtime_status == "INITIALIZING"` after `__init__()`. *Requires the code change in Section 8.*
- **P2-02-AC-002** — `runtime_status == "RUNNING"` after any `step()` call. *Requires the code change in Section 8.*
- **P2-02-AC-003** — No component other than `RunLoop` writes `runtime_status`. *Verified by Validation Group 4.*
- **P2-02-AC-004** — No code path sets `PAUSED`/`STOPPING`/`STOPPED`/`ERROR`. *Verified by Validation Group 3.*
- **P2-02-AC-005** — `run_engine/main.py` byte-for-byte unmodified. *Verified by Validation Group 5.*
- **P2-02-AC-006** — Runtime Status never conflated with Lifecycle State/Execution Result/Position State/Risk State. *Verified by Validation Group 4 (no cross-reads) and direct diff inspection (no such logic added).*
- **P2-02-AC-007** — `python -m compileall run_engine/core` passes. *Verified by Validation Group 7.*
- **P2-02-AC-008** — No existing `CanonicalState`/`CanonicalEnforcer` member modified or removed. *Verified by direct diff inspection at implementation time (only additions, per Sections 6 and 7).*

Implementation is accepted only if all eight criteria pass and Validation Groups 1 through 7 (Section 9) all report PASS.

---

## 11. Non-Goals

- No implementation of `PAUSED`, `STOPPING`, `STOPPED`, or `ERROR` — deferred to a future runtime-control unit per `TD-007`.
- No change to `run_engine/main.py`, including no wiring of its crash-catch to `ERROR`.
- No pause/stop/shutdown control surface added to `RunLoop`.
- No enum type, constants module, or vocabulary-validation logic introduced for Runtime Status values (consistent with the codebase's existing plain-string convention for all other status-like fields).
- No change to `PositionEngine`, `PnLEngine`, `RiskEngine`, `TradeLifecycleEngine`, or `PerformanceEngine`.
- P2-02A (Position dual-state), P2-03/P2-04 (`RiskEngine` ownership, `TD-006`), and the other two P2-02 baseline objectives ("Consolidate CanonicalState implementation," "Verify Canonical Working State semantics") — all unchanged, out of scope.

---

## 12. Next Required Step

Implementation. The next step is to apply the code changes specified in Sections 6, 7, and 8 to `run_engine/core/canonical_state.py`, `run_engine/core/canonical_enforcer.py`, and `run_engine/core/loop.py`, run `python -m compileall run_engine/core`, execute Validation Groups 1 through 7 (Section 9), and then produce the P2-02 Final Certification document, following the same governance sequence used for P1-04 and P2-01.
