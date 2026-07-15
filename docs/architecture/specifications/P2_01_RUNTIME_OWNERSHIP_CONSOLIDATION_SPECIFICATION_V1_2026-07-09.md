# Document Metadata

Document Class: Implementation Specification
Document ID: P2-01A
Version: V1.0
Status: Implementation Preparation
Date: 2026-07-09
Project: Trading-Bot Scientific Runtime
Subsystem: Run Engine
Storage Location: docs/architecture/specifications/
Filename: P2_01_RUNTIME_OWNERSHIP_CONSOLIDATION_SPECIFICATION_V1_2026-07-09.md

Depends On:
- docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md
- docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md
- docs/architecture/analysis/P2_01_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-09.md
- docs/architecture/analysis/P2_01_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-09.md
- docs/architecture/analysis/P2_01_CAPABILITY_GAP_ANALYSIS_V1_2026-07-09.md
- docs/architecture/specifications/P2_01_RUNTIME_OWNERSHIP_CONSOLIDATION_ARCHITECTURE_V1_2026-07-09.md

Referenced By:
- P2-01 Implementation
- P2-01 Validation
- P2-01 Certification

---

# P2-01 Runtime Ownership Consolidation — Implementation Specification

## 1. Metadata

See Document Metadata block above.

---

## 2. Objective

This specification defines the exact, file-level implementation contract for the P2-01 approved cluster, translating the architecture decisions in `P2_01_RUNTIME_OWNERSHIP_CONSOLIDATION_ARCHITECTURE_V1_2026-07-09.md` into precise code changes.

Binding scope carried forward from the Architecture document (not renegotiated here):

- Implement **only** the approved cluster: Strategy Selection, Execution Decision, and Performance Metrics publication into `CanonicalState`.
- Runtime Status, Position dual-state, and the `RiskEngine` Peak-Equity/Drawdown duplication are explicitly deferred and receive no code change.
- Normalized Runtime State requires no code change (already correctly satisfied by existing `tick`/`price` publication).

---

## 3. Files in Scope

- `run_engine/core/canonical_state.py` — code change required.
- `run_engine/core/canonical_enforcer.py` — code change required.
- `run_engine/core/loop.py` — code change required (three call-site additions).

---

## 4. Files Out of Scope

- `run_engine/core/position.py`, `run_engine/core/pnl.py` — Position/financial ownership deferred to P2-02A/P2-03.
- `run_engine/core/risk.py` — `RiskEngine`'s Peak-Equity/Drawdown duplication deferred to P2-03/P2-04; no change, including no incidental change to its inputs, outputs, or internal state.
- `run_engine/core/trade_lifecycle.py` — unaffected by this unit.
- `run_engine/core/performance.py` — its *output* is published by this unit; its *internal computation* is unchanged.
- `run_engine/core/state.py`, `run_engine/core/regime.py` — Normalized Runtime State requires no change (Architecture document, Section 5); Market Regime publication already conforms.
- `run_engine/core/strategy.py` — its *outputs* (`weights`, `decision`) are published by this unit; its *internal computation* is unchanged.
- `run_engine/core/execution/executor.py` — unaffected by this unit.

---

## 5. Required Code Changes

Exactly three additions, each following the identical existing pattern, applied to three files:

1. `CanonicalState.__init__` gains three new state keys (`strategy_selection`, `execution_decision`, `performance`, each defaulting to `None`), and gains three new methods (`update_strategy_selection`, `update_execution_decision`, `update_performance`), each a direct one-line assignment matching the existing `update_pnl`/`update_regime` shape.
2. `CanonicalEnforcer` gains three new methods (`apply_strategy_selection`, `apply_execution_decision`, `apply_performance`), each following the exact existing shape used by `apply_pnl`/`apply_equity`/`apply_risk`.
3. `RunLoop.step()` gains three new call-site lines, each placed immediately after the corresponding value already exists as a local variable (`weights`, `decision`, `performance`), introducing no new computation.

No other function, class, method, or file changes.

---

## 6. CanonicalState Publication Contract

| Field | Source (Computational Authority) | Type | Written By | Placement in `RunLoop.step()` |
|---|---|---|---|---|
| `strategy_selection` | `StrategySelector.select()` | `dict` (action → score) | `CanonicalEnforcer.apply_strategy_selection()` | Immediately after `weights = self.strategy_selector.select(...)` |
| `execution_decision` | `StrategySelector.decide()` | `dict` (`action`, `confidence`, `regime`) | `CanonicalEnforcer.apply_execution_decision()` | Immediately after `decision = self.strategy_selector.decide(...)` |
| `performance` | `PerformanceEngine.update()` | `dict` (action → stats) | `CanonicalEnforcer.apply_performance()` | Immediately after `performance = self.performance_engine.update(...)` |

Ownership is unchanged by this contract: `CanonicalState` becomes the Authoritative Owner (already declared by the Matrix); `StrategySelector`/`PerformanceEngine` remain the sole Computational Authorities (Rule OM-002: Computational Authority may differ from Authoritative Owner); `CanonicalEnforcer` is Writer-on-Behalf-Of only and acquires no ownership (Rule OM-003).

**Required `CanonicalState` change:**

```python
class CanonicalState:

    def __init__(self):

        self.state = {
            "tick": None,

            "price": None,

            "position": {
                "position": "FLAT",
                "entry_price": None,
                "last_price": None
            },

            "equity": 100.0,

            "peak_equity": 100.0,

            "pnl": 0.0,

            "drawdown": 0.0,

            "drawdown_ratio": 0.0,

            "exposure": 1.0,

            "regime": "UNKNOWN",

            "strategy_selection": None,

            "execution_decision": None,

            "performance": None
        }

    def update_tick(self, tick, price):

        self.state["tick"] = tick
        self.state["price"] = price

    def update_position(self, position):

        self.state["position"] = position

    def update_equity(self, equity):

        self.state["equity"] = equity

        if equity > self.state["peak_equity"]:
            self.state["peak_equity"] = equity

    def update_pnl(self, pnl):

        self.state["pnl"] = pnl

    def update_risk(self, risk_dict):

        self.state["drawdown"] = risk_dict.get("drawdown", 0.0)
        self.state["drawdown_ratio"] = risk_dict.get("drawdown_ratio", 0.0)
        self.state["exposure"] = risk_dict.get("exposure", 1.0)

    def update_regime(self, regime):

        self.state["regime"] = regime

    def update_strategy_selection(self, weights):

        self.state["strategy_selection"] = weights

    def update_execution_decision(self, decision):

        self.state["execution_decision"] = decision

    def update_performance(self, performance):

        self.state["performance"] = performance

    def get(self):

        return self.state

    def reset(self):

        self.__init__()
```

Only the `__init__` dict (three new keys, appended after `"regime"`) and three new methods (appended after `update_regime`) change. No existing key, method, or line is modified.

---

## 7. RunLoop Specification

**Current lines (`run_engine/core/loop.py`):**

```python
        weights = self.strategy_selector.select(state, regime, position_pre)

        decision = self.strategy_selector.decide(state, regime, weights)

        execution = self.execution_engine.execute(decision, position_pre)
```

**Required lines:**

```python
        weights = self.strategy_selector.select(state, regime, position_pre)
        self.enforcer.apply_strategy_selection(weights)

        decision = self.strategy_selector.decide(state, regime, weights)
        self.enforcer.apply_execution_decision(decision)

        execution = self.execution_engine.execute(decision, position_pre)
```

**Current line:**

```python
        performance = self.performance_engine.update(decision, pnl, regime, trade_event)
```

**Required lines:**

```python
        performance = self.performance_engine.update(decision, pnl, regime, trade_event)
        self.enforcer.apply_performance(performance)
```

No other line in `loop.py` changes. In particular, the execution order established in P1-04 (`Position → PnL → Risk → Performance`) is unchanged; the three new lines are inserted immediately after their source value already exists, with no reordering of any existing statement.

---

## 8. CanonicalEnforcer Specification

**Current implementation (unchanged reference):**

```python
class CanonicalEnforcer:

    def __init__(self, canonical_state):

        self.cs = canonical_state

    def apply_position(self, position):

        if position is None:
            return self.cs.get()["position"]

        self.cs.update_position(position)
        return self.cs.get()["position"]

    def apply_pnl(self, pnl):

        if pnl is None:
            return self.cs.get()["pnl"]

        self.cs.update_pnl(pnl)
        return self.cs.get()["pnl"]

    def apply_equity(self, equity):

        if equity is None:
            return self.cs.get()["equity"]

        self.cs.update_equity(equity)
        return self.cs.get()["equity"]

    def apply_risk(self, risk):

        if risk is None:
            return self.cs.get()
        self.cs.update_risk(risk)
        return self.cs.get()
```

**Required additions (appended after `apply_risk`):**

```python
    def apply_strategy_selection(self, weights):

        if weights is None:
            return self.cs.get()["strategy_selection"]

        self.cs.update_strategy_selection(weights)
        return self.cs.get()["strategy_selection"]

    def apply_execution_decision(self, decision):

        if decision is None:
            return self.cs.get()["execution_decision"]

        self.cs.update_execution_decision(decision)
        return self.cs.get()["execution_decision"]

    def apply_performance(self, performance):

        if performance is None:
            return self.cs.get()["performance"]

        self.cs.update_performance(performance)
        return self.cs.get()["performance"]
```

No existing method (`apply_position`, `apply_pnl`, `apply_equity`, `apply_risk`) changes in any way.

---

## 9. Validation Requirements

**Validation Group 1 — Publication Correctness**

Verify that after one `RunLoop.step()` call, `CanonicalState.state["strategy_selection"]` equals the `weights` value returned by `StrategySelector.select()`, `state["execution_decision"]` equals the `decision` value returned by `StrategySelector.decide()`, and `state["performance"]` equals the `performance` value returned by `PerformanceEngine.update()` for that same tick.

PASS Criteria: all three match exactly (identity of computed value, not a copy with drift).

---

**Validation Group 2 — No Regression to Existing Fields**

Verify that `tick`, `price`, `position`, `equity`, `peak_equity`, `pnl`, `drawdown`, `drawdown_ratio`, `exposure`, and `regime` remain populated and correct exactly as before this change, across an accepted-trade tick and a rejected-transition tick.

PASS Criteria: identical results to the pre-P2-01 implementation for an identical tick sequence.

---

**Validation Group 3 — `RiskEngine` Non-Regression**

Verify that `RiskEngine.check()`'s inputs, outputs, and internal `self.peak_equity`/`self.last_equity` tracking are byte-for-byte unchanged by this implementation (confirms Architecture document AC-007; the deferred duplication is left exactly as found, not incidentally touched).

PASS Criteria: identical `risk` dict output for an identical input sequence, before and after this change.

---

**Validation Group 4 — Ownership Non-Violation**

Verify that no new Authoritative Owner, Computational Authority, or Writer-on-Behalf-Of assignment is introduced anywhere outside the three new `CanonicalEnforcer` methods, and that `StrategySelector`/`PerformanceEngine` remain the sole Computational Authorities for their respective values (i.e., `CanonicalEnforcer` only relays already-computed values, it does not recompute or alter them).

PASS Criteria: `CanonicalState.state["strategy_selection"]`/`["execution_decision"]`/`["performance"]` are reference-equal or value-equal to what `StrategySelector`/`PerformanceEngine` already returned, with no transformation applied by `CanonicalEnforcer` or `CanonicalState`.

---

**Validation Group 5 — Full Regression (P1-03 / P1-03.1 / P1-04 scenarios)**

Re-run the existing end-to-end scenarios (LONG/SHORT scale-in and partial-close, two-stage partial-then-full close, rejected-transition non-mutation of `Position`/`PnLEngine`/`PerformanceEngine`) to confirm all previously certified results are unchanged.

PASS Criteria: identical to the results certified in `P1_04_FINAL_CERTIFICATION_V1_2026-07-09.md`.

---

**Validation Group 6 — Static Validation**

`python -m compileall run_engine/core` passes with no errors after implementation.

---

## 10. Acceptance Criteria

Restated from the Architecture document (Section 10), with implementation status:

- **P2-01-AC-001** — Every Matrix row has a recorded conformance result. *Already satisfied (Capability Gap Analysis + Architecture document Section 5); no code change contributes further.*
- **P2-01-AC-002** — `strategy_selection`, `execution_decision`, `performance` populated on every tick. *Requires the code changes in Sections 6–8.*
- **P2-01-AC-003** — Runtime Status deferral recorded. *Already satisfied (Architecture document Section 7); no code change.*
- **P2-01-AC-004** — Position dual-state deferral recorded. *Already satisfied (Architecture document Section 7); no code change.*
- **P2-01-AC-005** — No Authoritative Owner assignment changed. *Verified by Validation Group 4.*
- **P2-01-AC-006** — `python -m compileall run_engine/core` passes. *Verified by Validation Group 6.*
- **P2-01-AC-007** — `RiskEngine.check()` behavior byte-for-byte unchanged. *Verified by Validation Group 3.*
- **P2-01-AC-008** — No existing `CanonicalState`/`CanonicalEnforcer` member modified or removed. *Verified by direct diff inspection at implementation time (only additions, per Sections 6 and 8).*

Implementation is accepted only if all eight criteria pass and Validation Groups 1 through 6 (Section 9) all report PASS.

---

## 11. Non-Goals

- Runtime Status implementation — deferred to P2-02 (Architecture document, Section 7). No code change in this unit.
- Position dual-state consolidation (TD-001) — deferred to P2-02A. No code change in this unit.
- `RiskEngine` Peak-Equity/Drawdown duplication fix — deferred to P2-03/P2-04. No code change in this unit; `TD-006` remains a recommendation pending a future turn that may modify the Technical Debt Register.
- Normalized Runtime State (`raw` input echo) publication — explicitly not required (Architecture document, Section 5); no code change.
- Unrealized PnL — capability entirely absent, out of scope for an ownership-consolidation unit (Capability Gap Analysis, Section 7).
- TD-002 (unify `_safe_float` implementations), TD-004 (lifecycle-based Performance evaluation), TD-005 (automated test suite) — unchanged, out of scope.
- No new runtime module, Authoritative Owner, or Computational Authority is introduced.
- No change to `ADR-010`'s execution ordering.

---

## 12. Next Required Step

Implementation. The next step is to apply the code changes specified in Sections 6, 7, and 8 to `run_engine/core/canonical_state.py`, `run_engine/core/canonical_enforcer.py`, and `run_engine/core/loop.py`, run `python -m compileall run_engine/core`, execute Validation Groups 1 through 6 (Section 9), and then produce the P2-01 Final Certification document, following the same governance sequence used for P1-03.1 and P1-04. Separately, `TD-006` (the `RiskEngine` finding) should be logged in the Architecture Technical Debt Register in a dedicated turn, since that document was out of scope for modification here.
