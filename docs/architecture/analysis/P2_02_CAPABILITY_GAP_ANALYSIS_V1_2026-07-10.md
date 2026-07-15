# Document Metadata

Document Class: Capability Gap Analysis
Document ID: P2-02-CGA
Version: V1.0
Status: Draft
Date: 2026-07-10
Project: Trading-Bot Scientific Runtime
Subsystem: Run Engine
Storage Location: docs/architecture/analysis/
Filename: P2_02_CAPABILITY_GAP_ANALYSIS_V1_2026-07-10.md

Depends On:
- docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md
- docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md
- docs/architecture/analysis/P2_02_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-10.md
- docs/architecture/analysis/P2_02_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-10.md
- docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md

Referenced By:
- P2_02_ARCHITECTURE_V1_2026-07-10.md
- P2_02_SPECIFICATION_V1_2026-07-10.md

---

# P2-02 Capability Gap Analysis — Runtime Status Ownership

## 1. Metadata

See Document Metadata block above.

---

## 2. Objective

The Scientific Dependency Analysis certified that all five candidate capabilities underlying Runtime Status ownership already exist — three of them (CanonicalState extensibility, CanonicalEnforcer mediation, RunLoop lifecycle hook points) not merely per baseline text but empirically proven by P2-01's own implementation — and that Runtime Status ownership may proceed directly to Capability Gap Analysis.

This document performs that comparison concretely: it checks the required Runtime Status architecture (per ADR-001 and the Functional Requirement Analysis) against the actual current implementation, module by module, and localizes every gap. It also performs the explicit distinction required between Runtime Status and four adjacent, easily-confused concepts, and documents — rather than works around — the fact that `RunLoop` currently has no lifecycle control mechanism for four of the six ADR-001-named states.

---

## 3. Current Capability Baseline

Direct inspection of `run_engine/core/{loop,canonical_state,canonical_enforcer}.py` and `run_engine/main.py`, re-confirming the Scientific Dependency Analysis's D-001 through D-005:

- **`CanonicalState.state`** is a plain, additively-extensible dictionary. As of P2-01 it holds `tick`, `price`, `position`, `equity`, `peak_equity`, `pnl`, `drawdown`, `drawdown_ratio`, `exposure`, `regime`, `strategy_selection`, `execution_decision`, `performance_metrics` — no `status`/`runtime_status` key exists.
- **`CanonicalEnforcer`** mediates seven publications (`apply_position`, `apply_pnl`, `apply_equity`, `apply_risk`, `apply_strategy_selection`, `apply_execution_decision`, `apply_performance_metrics`), all via one identical shape — no `apply_status`/`apply_runtime_status` method exists.
- **`RunLoop.__init__()`** deterministically constructs `state_engine`, `regime_classifier`, `strategy_selector`, `position_engine`, `trade_lifecycle_engine`, `risk_engine`, `execution_engine`, `pnl_engine`, `performance_engine`, `cstate`, `enforcer` — one single, unambiguous construction point, with no branching and no failure path.
- **`RunLoop.step()`** is the sole per-tick entry point; a successful return is the sole "engine is operating" signal. `RunLoop` defines no `pause()`, `resume()`, `stop()`, `shutdown()`, or equivalent method anywhere.
- **`run_engine/main.py`**'s outer loop is `while True: try: ... engine.step(tick_data) ... except Exception as e: print(f"[CRASH] {e}"); tick += 1` — unconditional, non-terminating, and its exception handler is entirely outside `RunLoop`/`CanonicalState`; a caught exception is logged and the loop continues to the next tick, never treated as a terminal or error state anywhere in the data model.
- **`run_engine/core/loop.py`'s own `if __name__ == "__main__":` block** is likewise an unconditional `while True` with no termination condition.

---

## 4. Required Runtime Status Capabilities

Restated from the Functional Requirement Analysis, in capability form:

- **C-1** — `CanonicalState` storage for Runtime Status (P2-02-FR-001).
- **C-2** — `RunLoop`-exclusive computation and `CanonicalEnforcer`-mediated publication (P2-02-FR-002).
- **C-3** — `Initializing` → `Running` transition at startup (P2-02-FR-003).
- **C-4** — Recorded disposition of `Paused`/`Stopping`/`Stopped`/`Error` (P2-02-FR-004) — this document determines the evidence, not the decision.
- **C-5** — Non-conflation with Lifecycle State, Execution Result, Position State, Risk State (P2-02-FR-005).

---

## 5. Gap Analysis Table

**Part A — Storage, publication, and the two reachable transitions:**

| Capability | Required | Current Implementation | Result |
|---|---|---|---|
| C-1 (storage) | `CanonicalState.state["status"]` (or equivalent) holding one of six values | No such key exists | **GAP** |
| C-2 (publication) | `CanonicalEnforcer.apply_status()` (or equivalent), mirroring the seven existing `apply_*` methods | No such method exists | **GAP** |
| C-3, `Initializing` | Set at `RunLoop.__init__()` | `__init__()` runs to completion with no status write of any kind | **GAP — but trivially closable**: `__init__()` is a single, deterministic, already-existing point |
| C-3, `Running` | Set at/before first successful `step()` return | `step()` runs to completion with no status write of any kind | **GAP — but trivially closable**: `step()` is a single, deterministic, already-existing point |

**Part B — The four states requiring lifecycle control `RunLoop` does not have:**

| Value | Required Trigger (ADR-001 concept) | Current `RunLoop`/`main.py` Capability | Result |
|---|---|---|---|
| `Paused` | An explicit pause command/signal | No `pause()` method, no pause signal, no code path that suspends ticking | **NOT REACHABLE — no control mechanism exists to attach this state to** |
| `Stopping` | A graceful shutdown initiated | No `stop()`/`shutdown()` method; `main.py`'s loop is unconditional `while True` | **NOT REACHABLE** |
| `Stopped` | Shutdown completed | Same — the loop is designed to never terminate | **NOT REACHABLE** |
| `Error` | An unhandled fault | `main.py` catches exceptions **outside** `RunLoop`, logs them, and unconditionally continues to the next tick — a crash is never treated as a terminal or recorded state anywhere in `CanonicalState` or `RunLoop` | **NOT REACHABLE from within `RunLoop`** — the only fault-adjacent mechanism that exists is architecturally disconnected from Runtime Status entirely |

**This is documented explicitly, per instruction, rather than used to justify broadening this unit's scope to build pause/stop/error control flow.** `RunLoop` lacking lifecycle control for these four values is a real, current architectural limitation — not a P2-02 defect, since verifying ownership of a value does not require inventing the operational machinery to reach every value in its domain. Building that machinery would be new capability (a lifecycle controller), not ownership verification.

**Part C — Distinguishing Runtime Status from four adjacent concepts, per instruction:**

| Concept | Owning Module | Values / Shape | Answers |
|---|---|---|---|
| **Runtime Status** | `CanonicalState` (owner) / `RunLoop` (authority) — target of this unit | `Initializing`/`Running`/`Paused`/`Stopping`/`Stopped`/`Error` | "What operational mode is the Run Engine process itself in?" |
| **Lifecycle State** | `TradeLifecycleEngine` (`Trade.status`) | `"OPEN"`/`"CLOSED"` | "Is this individual trade open or closed?" |
| **Execution Result** | `Executor` (`execution["status"]`), absorbed by `TradeLifecycleEngine` | `"BUY_EXECUTED"`/`"SELL_EXECUTED"`/`"NOOP"` | "What was the immediate outcome of this one order attempt?" |
| **Position State** | `PositionEngine` / `CanonicalState` (`state["position"]["position"]`) | `"FLAT"`/`"LONG"`/`"SHORT"` | "What market exposure do we currently hold?" |
| **Risk State** | `RiskEngine` / `CanonicalState` (`drawdown`, `drawdown_ratio`, `exposure`) | numeric metrics, no discrete "status" field | "How risky is the current position?" |

All five are confirmed structurally distinct: different owning module, different value domain, different question answered, no code path today that reads one to compute another.

---

## 6. Implementation-Relevant Gaps

Exactly one implementation-relevant gap cluster, spanning three files, matching the pattern already used for the P2-01 publication cluster:

1. **`CanonicalState` storage (C-1).** Add a `status` field (or equivalently named) to `CanonicalState.__init__`, and an `update_status()` method, following the exact shape of `update_regime()`.
2. **`CanonicalEnforcer` publication (C-2).** Add an `apply_status()` method, following the exact shape of the seven existing `apply_*` methods.
3. **`RunLoop` transition writes (C-3).** In `RunLoop.__init__()`, after construction completes, publish `Initializing`. In `RunLoop.step()`, at or before the point of successful return, publish `Running`. No other new logic.

This is the entire implementation-relevant scope. `Paused`/`Stopping`/`Stopped`/`Error` (Part B) require no code change in this unit — they cannot be triggered by anything that currently exists, and building the triggers is out of scope (Section 7).

---

## 7. Non-Gaps / Deferred Items

- **`Paused`/`Stopping`/`Stopped`/`Error` implementation.** Not a P2-02 gap to close now. `RunLoop` has no lifecycle control surface for any of these four values — there is nothing partially built to complete, only a vocabulary with no attachment point. Recommended: the Architecture document records these four as **reserved vocabulary** (satisfying "the enum exists and `CanonicalState` is its correctly-declared owner") without implementing unreachable triggers, and recommends logging a new Technical Debt Register candidate (`TD-007`, proposed — not written to the register in this document) for "RunLoop Lifecycle Control Surface" as the actual prerequisite capability a future unit would need before those four values could ever be set.
- **`main.py` crash-catch → `Error` wiring.** Explicitly not decided or implemented here (Functional Requirement Analysis OQ-003). `main.py` is not in this unit's file scope.
- **P2-02A (Position dual-state / TD-001).** Untouched; separate named unit.
- **`RiskEngine` ownership (P2-03/P2-04, TD-006).** Untouched; separate named unit. Risk State (Part C) is confirmed correctly distinct from Runtime Status, but its internal Peak-Equity/Drawdown duplication (already logged as `TD-006`) is not re-opened or touched by this analysis.
- **The other two P2-02 objectives** ("Consolidate CanonicalState implementation," "Verify Canonical Working State semantics") — still unaddressed, per Functional Requirement Analysis OQ-001; not part of this Runtime-Status-scoped gap analysis.

---

## 8. Minimal Implementation Scope

Exactly the same three files touched by P2-01, for the same reason (one uniform, already-proven publication pattern applied to one more value):

- `run_engine/core/canonical_state.py` — add `status` field + `update_status()` method.
- `run_engine/core/canonical_enforcer.py` — add `apply_status()` method.
- `run_engine/core/loop.py` — two new call sites: one in `__init__()` (publish `Initializing`), one in `step()` (publish `Running`).

**Not in scope:** `run_engine/main.py` (no wiring required for the minimal `Initializing`/`Running` scope), and every other `run_engine/core/*.py` module (`position.py`, `pnl.py`, `risk.py`, `trade_lifecycle.py`, `performance.py`, `state.py`, `regime.py`, `strategy.py`, `execution/executor.py`) — none owns, computes, or needs to consume Runtime Status.

---

## 9. Risks

**R-001** — Building no lifecycle control surface now means `Paused`/`Stopping`/`Stopped`/`Error` remain permanently unreachable until a separate, not-yet-scoped unit builds one. This is judged the correct scope boundary (per instruction), not an oversight, but it means P2-02's Runtime Status capability will be observably incomplete relative to ADR-001's full vocabulary until that future unit exists.

**R-002** — Recommending `TD-007` (RunLoop Lifecycle Control Surface) without writing it to the register (out of scope for this document) risks the recommendation being lost before a future turn logs it, mirroring the same risk already open for `TD-006`.

**R-003 (carried forward)** — No automated regression suite exists (TD-005); verification of the `Initializing`/`Running` implementation will be manual/interactive.

**R-004 (carried forward)** — The other two P2-02 baseline objectives remain unaddressed (OQ-001, Functional Requirement Analysis); unaffected by, but not resolved by, this gap analysis.

---

## 10. Conclusion

The required Runtime Status architecture was compared against the current implementation module by module. Of the six ADR-001-named values, two (`Initializing`, `Running`) have a clean, closable gap — storage and publication are missing but the trigger points already exist unambiguously in `RunLoop`. The other four (`Paused`, `Stopping`, `Stopped`, `Error`) are not implementation gaps in the ordinary sense: `RunLoop` has no lifecycle control mechanism at all for any of them, and this is documented explicitly rather than used as a reason to build pause/stop/error control flow inside this unit. Runtime Status was also confirmed structurally distinct from Lifecycle State, Execution Result, Position State, and Risk State, with no code path today conflating any of them.

The implementation-relevant scope is narrow and file-localized: `canonical_state.py`, `canonical_enforcer.py`, `loop.py` — the same three files P2-01 touched, extended with one more value using the identical, already-proven pattern.

---

## 11. Next Required Document

The next document is `P2_02_ARCHITECTURE_V1_2026-07-10.md`.
