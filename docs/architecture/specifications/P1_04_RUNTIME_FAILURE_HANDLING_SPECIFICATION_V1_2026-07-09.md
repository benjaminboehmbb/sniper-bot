# Document Metadata

Document Class: Implementation Specification
Document ID: P1-04A
Version: V1.0
Status: Implementation Preparation
Date: 2026-07-09
Project: Trading-Bot Scientific Runtime
Subsystem: Run Engine
Storage Location: docs/architecture/specifications/
Filename: P1_04_RUNTIME_FAILURE_HANDLING_SPECIFICATION_V1_2026-07-09.md

Depends On:
- docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md
- docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md
- docs/architecture/analysis/P1_04_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-09.md
- docs/architecture/analysis/P1_04_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-09.md
- docs/architecture/analysis/P1_04_CAPABILITY_GAP_ANALYSIS_V1_2026-07-09.md
- docs/architecture/specifications/P1_04_RUNTIME_FAILURE_HANDLING_ARCHITECTURE_V1_2026-07-09.md

Referenced By:
- P1-04 Implementation
- P1-04 Validation
- P1-04 Certification

---

# P1-04 Runtime Failure Handling — Implementation Specification

## 1. Metadata

See Document Metadata block above.

---

## 2. Objective

This specification defines the exact, file-level implementation contract for P1-04 (Runtime Failure Handling, ADR-011), translating the architecture decisions made in `P1_04_RUNTIME_FAILURE_HANDLING_ARCHITECTURE_V1_2026-07-09.md` into a precise code-change contract.

Binding implementation decisions carried forward from the Architecture document (not renegotiated here):

- Runtime failure recognition is **per-consumer** — no centralized rejection gate is introduced in `RunLoop`.
- `PositionEngine` continues updating `last_price` from market data after a rejected execution; `side`, `quantity`, and `entry_price` remain protected, as already implemented.
- `PnLEngine` requires **no change** — its existing event-type gate is the ratified contract.
- `PositionEngine` requires **no change** — its existing behavior already implements the ratified mark-price policy.
- Only `performance.py` and `loop.py` require code changes.

---

## 3. Files in Scope

- `run_engine/core/performance.py` — code change required.
- `run_engine/core/loop.py` — code change required (one call-site edit).

---

## 4. Required Code Changes

Exactly two changes, both minimal:

1. `PerformanceEngine.update()` gains one new parameter carrying the tick's `trade_event`, and returns `self.stats` unmodified — without incrementing `trades` or recomputing `pnl`/`winrate` — whenever `trade_event.event_type == "RUNTIME_FAILURE_EVENT"`.
2. `RunLoop.step()`'s existing call to `self.performance_engine.update(...)` is updated to pass `trade_event` as the new argument.

No other function, class, method, or file changes.

---

## 5. performance.py Specification

**Current implementation (unchanged reference):**

```python
class PerformanceEngine:

    def __init__(self):
        self.stats = {}

    def update(self, decision, pnl, regime):

        action = decision.get('action', 'HOLD')

        if action not in self.stats:
            self.stats[action] = {
                'pnl': 0.0,
                'trades': 0,
                'winrate': 0.0
            }

        self.stats[action]['trades'] += 1

        trades = self.stats[action]['trades']
        wins = 1 if pnl > 0 else 0

        self.stats[action]['pnl'] = (
            self.stats[action]['pnl'] * (trades - 1) + pnl
        ) / trades

        self.stats[action]['winrate'] = (
            (self.stats[action]['winrate'] * (trades - 1) + wins)
            / trades
        )

        return self.stats
```

**Required specification:**

- New signature: `def update(self, decision, pnl, regime, trade_event):`
- The first statement inside `update()` must check whether `trade_event` represents a rejected transition, and if so, return `self.stats` immediately, before `action`, `self.stats[action]`, `trades`, or `winrate` are read or written in any way.
- The check must use `getattr(trade_event, "event_type", None)` rather than direct attribute access, since `trade_event` is `None` on ticks where `TradeLifecycleEngine.on_execution()` itself returned `None` (the existing `HOLD` case), and `getattr` must not raise in that case.
- The comparison value is the literal string `"RUNTIME_FAILURE_EVENT"`, matching `TradeLifecycleEngine`'s existing `event_type` values exactly (no new constant is introduced elsewhere; this mirrors how `PnLEngine.update()` already compares against literal `event_type` strings).
- No other line in the method changes. `action`, the `stats` initialization, the `trades` increment, the `pnl` running average, and the `winrate` running average all remain byte-for-byte identical to the current implementation for every non-rejected tick, including `HOLD` ticks (`trade_event is None`), which continue to be counted exactly as today — this is an explicit, deliberate scope boundary, not an oversight (Architecture document, Section 13.2).

**Required resulting shape:**

```python
class PerformanceEngine:

    def __init__(self):
        self.stats = {}

    def update(self, decision, pnl, regime, trade_event):

        if getattr(trade_event, "event_type", None) == "RUNTIME_FAILURE_EVENT":
            return self.stats

        action = decision.get('action', 'HOLD')

        if action not in self.stats:
            self.stats[action] = {
                'pnl': 0.0,
                'trades': 0,
                'winrate': 0.0
            }

        self.stats[action]['trades'] += 1

        trades = self.stats[action]['trades']
        wins = 1 if pnl > 0 else 0

        self.stats[action]['pnl'] = (
            self.stats[action]['pnl'] * (trades - 1) + pnl
        ) / trades

        self.stats[action]['winrate'] = (
            (self.stats[action]['winrate'] * (trades - 1) + wins)
            / trades
        )

        return self.stats
```

This shape is prescriptive for the guard clause and signature; it is provided for direct implementation, not as an illustrative example.

---

## 6. loop.py Specification

**Current line (`run_engine/core/loop.py`):**

```python
        performance = self.performance_engine.update(decision, pnl, regime)
```

**Required line:**

```python
        performance = self.performance_engine.update(decision, pnl, regime, trade_event)
```

This is the only line in `loop.py` that changes. `trade_event` is already a local variable in `RunLoop.step()` at this point in the method (assigned earlier from `self.trade_lifecycle_engine.on_execution(execution, state)`), so no new computation, import, or variable is introduced — only an already-existing value is threaded one call further.

No other line in `loop.py` changes. In particular, the calls to `self.position_engine.update_post_trade(...)` and `self.pnl_engine.update(trade_event, position_pre["entry_price"])` remain exactly as they are today, per Sections 11 and 12 of the Architecture document.

---

## 7. Files Explicitly Out of Scope

- `run_engine/core/position.py` — no change. `update_post_trade()`'s current behavior (update `last_price` unconditionally; leave `side`/`quantity`/`entry_price` unchanged when the lifecycle position is unchanged) already implements the ratified mark-price policy (Architecture document, Section 11.2).
- `run_engine/core/pnl.py` — no change. `PnLEngine.update()`'s existing event-type gate already implements the ratified financial non-mutation contract (Architecture document, Section 12.2).
- `run_engine/core/trade_lifecycle.py` — no change. Rejection-event generation, immutability, and retrieval (`_failure_event`, `failure_events`, `get_failure_events()`) are already complete and were verified in P1-03/P1-03.1.
- `run_engine/core/canonical_state.py`, `run_engine/core/canonical_enforcer.py` — no change. Neither owns or computes any of the fields this specification touches.
- `run_engine/core/risk.py`, `run_engine/core/state.py`, `run_engine/core/regime.py`, `run_engine/core/strategy.py`, `run_engine/core/execution/executor.py` — no change. None of these components are inputs to, or consumers of, Runtime Failure Handling as scoped by ADR-011.

---

## 8. Validation Requirements

**Validation Group 1 — Performance Non-Mutation on Rejection**

Verify that a rejected transition (any of the four existing rejection reasons: `INVALID_EXECUTION_QUANTITY`, `NO_ACTIVE_TRADE`, `OVER_CLOSE_QUANTITY`, `UNSUPPORTED_EXECUTION_ACTION`) leaves `PerformanceEngine.stats` byte-for-byte identical to its pre-rejection value.

PASS Criteria: `stats` before and after a rejected tick are equal for every key.

---

**Validation Group 2 — Performance Non-Regression on Accepted Ticks**

Verify that `TRADE_OPENED`, `SCALE_IN`, `PARTIAL_CLOSE`, `TRADE_CLOSED`, and `HOLD` (`trade_event is None`) ticks continue to increment `stats[action]["trades"]` and recompute `pnl`/`winrate` exactly as before this change.

PASS Criteria: identical `stats` output to the pre-P1-04 implementation for an identical sequence of accepted ticks.

---

**Validation Group 3 — Position Mark-Price Continuity on Rejection**

Verify that `Position.last_price` updates to the current tick's market price on a rejected transition, while `Position.side`, `Position.quantity`, and `Position.entry_price` remain unchanged.

PASS Criteria: matches the empirical result already recorded in the Functional Requirement Analysis (`last_price: 100.0 → 250.0` on a rejected `BUY`; `side`/`quantity`/`entry_price` unchanged). No code change is expected to alter this result — this validation confirms non-regression of already-correct, now-ratified behavior.

---

**Validation Group 4 — Financial Non-Mutation on Rejection (Regression)**

Verify that `PnLEngine.last_realized_pnl`, `CanonicalState.state["pnl"]`, and `CanonicalState.state["equity"]` remain unchanged by a rejected transition.

PASS Criteria: identical to the result already established in the Functional Requirement Analysis. No code change is expected; this validation confirms non-regression.

---

**Validation Group 5 — Tick Completion Contract**

Verify that `RunLoop.step()` calls `PositionEngine.update_post_trade()`, `PnLEngine.update()`, and `PerformanceEngine.update()` exactly once each, on every tick, including rejected ticks.

PASS Criteria: no pipeline stage is skipped or conditionally bypassed; satisfies INV-P1-04-007 and P1-04-AC-009.

---

**Validation Group 6 — Repeated Rejection Determinism**

Verify that repeated identical rejected transitions against identical prior state produce identical `RUNTIME_FAILURE_EVENT` field values and identical `Position`/`PerformanceEngine.stats` results on every replay.

PASS Criteria: no drift across repeated invocations.

---

**Validation Group 7 — Call-Site Uniqueness**

Verify, by repository-wide search, that `run_engine/core/loop.py` remains the sole call site of `PerformanceEngine.update()` after its signature changes, so the breaking change has no other consumer (mirrors the regression check already performed for `PnLEngine.update()` in P1-03.1).

PASS Criteria: exactly one call site found.

---

**Validation Group 8 — Full Regression (P1-03 / P1-03.1 scenarios)**

Re-run the existing P1-03/P1-03.1 end-to-end scenarios (LONG scale-in/partial-close, SHORT scale-in/partial-close, two-stage partial-then-full close) to confirm realized PnL results are unchanged by this specification's changes.

PASS Criteria: identical PnL results to those certified in `P1_03_1_FINAL_CERTIFICATION_V1_2026-07-09.md`.

---

**Validation Group 9 — Static Validation**

`python -m compileall run_engine/core` passes with no errors after implementation.

---

## 9. Acceptance Criteria

Restated from the Architecture document (Section 15), with implementation status:

- **P1-04-AC-001** — Position side/quantity/entry_price protected from rejection. *Already satisfied; no code change.*
- **P1-04-AC-002** — Position last_price updates on every tick including rejected ticks. *Already satisfied; no code change; ratified policy.*
- **P1-04-AC-003** — PnLEngine/CanonicalState financial fields protected from rejection. *Already satisfied; no code change.*
- **P1-04-AC-004** — PerformanceEngine.stats protected from rejection. *Requires the code change in Section 5.*
- **P1-04-AC-005** — TradeLifecycleEngine.active_trade protected from rejection beyond history append. *Already satisfied; no code change.*
- **P1-04-AC-006** — Every rejected transition produces exactly one retrievable RUNTIME_FAILURE_EVENT. *Already satisfied; verification only.*
- **P1-04-AC-007** — Deterministic replay of rejected transitions. *Already satisfied; verification only.*
- **P1-04-AC-008** — `python -m compileall run_engine/core` passes. *Verified after implementation.*
- **P1-04-AC-009** — Every pipeline stage executes on every tick, including rejected ticks. *Verified after implementation (Validation Group 5).*

Implementation is accepted only if all nine criteria pass and Validation Groups 1 through 9 (Section 8) all report PASS.

---

## 10. Non-Goals

Carried forward unchanged from the Functional Requirement Analysis and Architecture document:

- No Phase 2 ownership consolidation (TD-001, TD-002).
- No adoption of the broader lifecycle-outcome `PerformanceEngine` redesign (TD-004) — only the narrow rejection-non-mutation behavior in Section 5 is implemented; `HOLD` handling and decision-keyed statistics remain unchanged.
- No automated regression test-suite buildout (TD-005) — validation is manual/interactive, consistent with P1-03 and P1-03.1.
- No change to `PositionEngine` or `PnLEngine` — both are explicitly out of scope (Section 7).
- No multi-asset support, portfolio accounting, or funding/fees/slippage expansion.
- No new runtime module, Authoritative Owner, or Computational Authority is introduced.

---

## 11. Next Required Step

Implementation. The next step is to apply the two code changes specified in Sections 5 and 6 to `run_engine/core/performance.py` and `run_engine/core/loop.py`, run `python -m compileall run_engine/core`, execute Validation Groups 1 through 9 (Section 8), and then produce the P1-04 Final Certification document, following the same governance sequence used for P1-03.1.
