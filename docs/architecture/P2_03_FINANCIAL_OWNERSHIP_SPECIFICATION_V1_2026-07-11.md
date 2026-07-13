Document Class:
Specification

Document ID:
P2-03-SPEC

Version:
V1.0

Status:
Draft for Internal Review

Date:
2026-07-11

Project:
Trading-Bot Scientific Runtime

Subsystem:
Run Engine

Primary Location:
docs/architecture/P2_03_FINANCIAL_OWNERSHIP_SPECIFICATION_V1_2026-07-11.md

Depends On:
- docs/architecture/analysis/P2_03_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-11.md
- docs/architecture/analysis/P2_03_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-11.md
- docs/architecture/analysis/P2_03_CAPABILITY_GAP_ANALYSIS_V1_2026-07-11.md
- docs/architecture/P2_03_FINANCIAL_OWNERSHIP_ARCHITECTURE_V1_2026-07-11.md
- docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md
- docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md
- docs/architecture/certification/P2_02A_FINAL_CERTIFICATION_V1_2026-07-10.md
- docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md
- current runtime code at HEAD 815cd8a

Referenced By:
- future P2-03 Implementation
- future P2-03 Certification

---

# P2-03 Financial Ownership Specification

## 1. Purpose

This document specifies, in complete and implementable detail, how the sixteen Architecture Decisions of `P2_03_FINANCIAL_OWNERSHIP_ARCHITECTURE_V1_2026-07-11.md` are to be realized. It defines the Canonical State schema, the interface contract of every runtime component this unit touches, the exact normative runtime ordering, reset and runtime-failure behaviour, replay and determinism requirements, the Implementation Units a future implementation must proceed through, the validation strategy, and objectively checkable Acceptance Criteria. It contains no code, no pseudocode, and no implementation; it modifies no runtime file.

## 2. Scope

In scope: complete specification of Realized PnL (event), Realized PnL (cumulative), Equity, Peak Equity, Drawdown, and Drawdown Ratio's runtime representation, computation contract, and publication, for `PnLEngine`, `CanonicalState`, `CanonicalEnforcer`, `RunLoop`, `RiskEngine`, and `PerformanceEngine`.

Out of scope, unchanged from the FRA, SDA, CGA, and Architecture: `RiskEngine`'s risk-limiting formula (`max_exposure`, `min_exposure`, `max_drawdown`, regime-dampening multipliers), Position Sizing, `PerformanceEngine`'s statistics model, Unrealized PnL, Multi-Asset Accounting, Fees/Funding/Slippage/Tax Accounting, Persistence, Recovery, `TradeLifecycleEngine`, `PositionEngine`, `main.py`, repository cleanup, and the automated regression test suite (TD-005). This document makes no architecture decision; where the Architecture document explicitly deferred a literal interface-shape question to this stage, this document resolves it (Section 5); it introduces no decision the Architecture document did not already authorize.

## 3. Governing Baseline

- `docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md` - ADR-005, ADR-006, ADR-007, ADR-002, ADR-008, ADR-010, ADR-011, the Runtime Ownership Matrix, Rules OM-001 through OM-009, AI-005, AI-010.
- `docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md` - P2-03's unit definition and the P2-03 Specification's place in the governance sequence.
- `docs/architecture/analysis/P2_03_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-11.md` - twenty functional requirements (FR-001 through FR-020).
- `docs/architecture/analysis/P2_03_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-11.md` - eighteen dependency records (DEP-001 through DEP-018).
- `docs/architecture/analysis/P2_03_CAPABILITY_GAP_ANALYSIS_V1_2026-07-11.md` - fifteen capabilities (CAP-001 through CAP-015).
- `docs/architecture/P2_03_FINANCIAL_OWNERSHIP_ARCHITECTURE_V1_2026-07-11.md` - sixteen Architecture Decisions (AD-001 through AD-016) and twelve Architectural Invariants (INV-001 through INV-012), Readiness: READY.
- `docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md` - TD-001 through TD-007.
- Current runtime code at HEAD `815cd8a`, re-verified for this document (Section 4).

## 4. Repository Verification

Branch `run-engine-consolidation-safety`, HEAD `815cd8a`, matching the FRA's, SDA's, CGA's, and Architecture document's own verification exactly. `run_engine/` remains clean. The nine runtime files (`pnl.py`, `loop.py`, `canonical_state.py`, `canonical_enforcer.py`, `risk.py`, `performance.py`, `trade_lifecycle.py`, `position.py`, `main.py`) were re-read in full immediately before drafting the Architecture document in this same session and have not changed since (confirmed by the repeated clean-tree check); this document specifies against that same, unchanged code.

## 5. Specification Principles

This document resolves exactly the interface-shape questions the Architecture document explicitly and repeatedly deferred to this stage (Architecture Section 21, Section 7's per-decision "Consequences" fields): the literal `CanonicalState` schema key name for cumulative Realized PnL (Section 8), `PnLEngine`'s exact computation-responsibility shape and return structure (Section 9), and `CanonicalEnforcer`'s new Writer-on-Behalf-Of responsibilities (Section 10). It makes no decision the Architecture document did not already authorize; every specification choice below cites the Architecture Decision it implements.

This document describes interface contracts in terms of named inputs, named outputs, preconditions, and postconditions, stated in prose and mathematical notation. It does not write Python method signatures, class definitions, or control-flow code. Mathematical formulas use algebraic notation (`+`, `-`, `=`, `MAX`) consistent with the notation ADR-006 and the FRA already use for the Equity formula; this is specification notation, not a code fragment, and defines no programming-language-specific construct.

## 6. Runtime Components

Six runtime components are specified in this document: `PnLEngine`, `CanonicalState`, `CanonicalEnforcer`, `RunLoop`, `RiskEngine`, `PerformanceEngine`. `TradeLifecycleEngine`, `PositionEngine`, `StateEngine`, `RegimeClassifier`, `StrategySelector`, `Executor`, and `main.py` are consulted for context and runtime-ordering placement (Section 16) but are not modified by any decision in this unit and receive no interface contract here, consistent with FR-019's compatibility protection.

## 7. Financial Information Objects

| Object | Computational Authority | Authoritative Owner | Formula |
|---|---|---|---|
| Realized PnL (event) | PnLEngine | CanonicalState (`pnl` key, unchanged) | LONG: (Exit Price - Entry Price) * Quantity; SHORT: (Entry Price - Exit Price) * Quantity; 0.0 on any tick whose lifecycle event is not TRADE_CLOSED or PARTIAL_CLOSE |
| Realized PnL (cumulative) | PnLEngine | CanonicalState (new key, Section 8) | Realized PnL (cumulative, new) = Realized PnL (cumulative, prior) + Realized PnL (event) |
| Equity | PnLEngine | CanonicalState (`equity` key, unchanged) | Equity (new) = Equity (prior) + Realized PnL (event), equivalently Initial Capital + Realized PnL (cumulative, new) + Unrealized PnL (definitionally 0 in this unit's scope) |
| Peak Equity | PnLEngine | CanonicalState (`peak_equity` key, unchanged) | Peak Equity (new) = MAX(Peak Equity (prior), Equity (new)) |
| Drawdown | RiskEngine | CanonicalState (`drawdown` key, unchanged) | Drawdown = Peak Equity - Equity, both read from canonical state |
| Drawdown Ratio | RiskEngine | CanonicalState (`drawdown_ratio` key, unchanged) | Drawdown Ratio = Drawdown / Peak Equity if Peak Equity > 0, otherwise 0.0, both terms read from canonical state |

Every formula above is the exact, unchanged arithmetic already present in the current runtime (Realized PnL event: `run_engine/core/pnl.py:31-36`; Equity: `run_engine/core/loop.py:71`; Peak Equity: `run_engine/core/canonical_state.py:64-65`; Drawdown/Drawdown Ratio: `run_engine/core/risk.py:24-30`), relocated to its Architecture-decided owner (AD-001, AD-003, AD-004, AD-006, AD-007) without alteration, per AD-016's numeric-equivalence-preservation requirement.

## 8. Canonical State Specification

### Complete Schema

| Key | Type | Financial Object | Owner | Change in This Unit |
|---|---|---|---|---|
| `tick` | integer or null | not financial | CanonicalState | unchanged |
| `price` | float or null | not financial | CanonicalState | unchanged |
| `position` (nested: `position`, `side`, `entry_price`, `quantity`, `last_price`, `exposure`) | dict | not financial (Position, P2-02A scope) | CanonicalState | unchanged |
| `equity` | float | Equity | CanonicalState | value now supplied by PnLEngine, unchanged key and storage semantics |
| `peak_equity` | float | Peak Equity | CanonicalState | value now supplied by PnLEngine directly; CanonicalState's own internal comparison logic is removed (Section 8, Storage Behaviour) |
| `pnl` | float | Realized PnL (event) | CanonicalState | unchanged |
| `realized_pnl_cumulative` | float | Realized PnL (cumulative) | CanonicalState | new key, this unit |
| `drawdown` | float | Drawdown | CanonicalState | unchanged (value continues to originate from RiskEngine, now from canonical-only inputs) |
| `drawdown_ratio` | float | Drawdown Ratio | CanonicalState | unchanged |
| `risk_allocation_factor` | float | not in this unit's scope (Exposure, P2-02A) | CanonicalState | unchanged |
| `regime` | string | not financial | CanonicalState | unchanged |
| `strategy_selection` | dict or null | not financial | CanonicalState | unchanged |
| `execution_decision` | dict or null | not financial | CanonicalState | unchanged |
| `performance_metrics` | dict or null | not financial | CanonicalState | unchanged |
| `runtime_status` | string or null | not financial | CanonicalState | unchanged |

`realized_pnl_cumulative` is specified as a new top-level key, a sibling of `equity`, `peak_equity`, `pnl`, `drawdown`, and `drawdown_ratio`, not nested under any existing key. The key name is part of the canonical runtime schema and SHALL remain stable unless changed through the architectural governance process. This resolves the schema-shape half of AD-002 that the Architecture document left open: uniform top-level placement for every financial value keeps the Consumer Boundary Matrix (Architecture AD-011) expressible in terms of top-level keys only, with no special case for a nested financial value.

### Runtime Lifetime

`CanonicalState` is instantiated exactly once per `RunLoop` instance and persists for the full lifetime of that `RunLoop` instance, across every tick, until an explicit reset occurs (Section 14). No financial key is ever re-instantiated mid-lifetime outside of `reset()`.

### Initialization

At instantiation, every financial key initializes as follows: `equity` = Initial Capital (a configuration value, AD-009; currently `100.0`); `peak_equity` = Initial Capital (identical value, since Peak Equity at initialization equals Equity at initialization); `pnl` = `0.0`; `realized_pnl_cumulative` = `0.0`; `drawdown` = `0.0`; `drawdown_ratio` = `0.0`. This is unchanged from today's existing `equity`/`peak_equity`/`pnl`/`drawdown`/`drawdown_ratio` initialization values (`run_engine/core/canonical_state.py:28-36`), extended by exactly one new key at the identical initial value pattern already used for `pnl`.

### Storage Behaviour

`CanonicalState`'s storage responsibility for `equity` becomes unconditional assignment of the value it receives via its Writer-on-Behalf-Of path (Section 10) - no internal comparison, no derived computation. `CanonicalState`'s storage responsibility for `peak_equity` becomes unconditional assignment of the value it receives via its Writer-on-Behalf-Of path; the internal `if equity > peak_equity` comparison currently performed at `run_engine/core/canonical_state.py:64-65` is removed from `CanonicalState`, since AD-004 relocates this comparison to `PnLEngine`. `CanonicalState`'s storage responsibility for `realized_pnl_cumulative` is unconditional assignment, identical in kind to `pnl`'s existing storage pattern. `CanonicalState` performs no arithmetic, comparison, or derivation on any financial value under any circumstance (INV-002, INV-003).

### Reset

Specified in full at Section 14.

## 9. PnLEngine Specification

`PnLEngine` exposes exactly two computation responsibilities, per AD-003's explicit separation of event-PnL computation from Equity computation.

### Responsibility 1 - Realized PnL (Event) Computation

Unchanged from the current, already-conformant behaviour (CAP-001, COMPLETE; `run_engine/core/pnl.py:9-40`). Inputs: the current tick's lifecycle event (or its absence), and the pre-trade entry basis (the weighted-average entry price `PositionEngine` maintains, unchanged per FR-019/TD-001). Output: the Realized PnL (event) value for the current tick, `0.0` on any tick whose lifecycle event is not `TRADE_CLOSED` or `PARTIAL_CLOSE`, and `0.0` (non-mutation) on `RUNTIME_FAILURE_EVENT` (Section 15). This responsibility requires no specification change beyond restating it as one of `PnLEngine`'s two responsibilities.

### Responsibility 2 - Realized PnL (Cumulative), Equity, and Peak Equity Computation

New, per AD-001, AD-003, AD-004. Runs every tick, regardless of lifecycle event type, mirroring the fact that Equity must remain current even on ticks with no closing event.

Inputs: the prior canonical value of Realized PnL (cumulative), read from `CanonicalState`; the prior canonical value of Equity, read from `CanonicalState`; the prior canonical value of Peak Equity, read from `CanonicalState`; the current tick's Realized PnL (event) value, the output of Responsibility 1 for the same tick.

Outputs: the new Realized PnL (cumulative) value; the new Equity value; the new Peak Equity value. These three outputs are returned together, as a single structured result of one logical computation step, not as three separate calls and not interleaved with Responsibility 1's own return - resolving OQ-002's remaining literal-interface question in favor of a single structured return, since `RunLoop` requires all three values from one internally-consistent computation before publishing any of them (Section 16).

Postconditions: Realized PnL (cumulative, new) equals Realized PnL (cumulative, prior) plus Realized PnL (event); Equity (new) equals Equity (prior) plus Realized PnL (event); Peak Equity (new) equals the greater of Peak Equity (prior) and Equity (new). On `RUNTIME_FAILURE_EVENT`, all three outputs equal their respective prior values unchanged (Section 15), consistent with Realized PnL (event) itself being `0.0` on that same tick.

### Interface Contract Fields

Purpose: exclusive Computational Authority for Realized PnL (event), Realized PnL (cumulative), Equity, and Peak Equity.

Required Preconditions: the entry basis supplied to Responsibility 1 is a finite float; the prior canonical values supplied to Responsibility 2 are the exact values most recently published to `CanonicalState` for the same `RunLoop` instance, with no staleness introduced by caching outside `CanonicalState` itself.

Required Postconditions: as stated per responsibility above.

Forbidden Responsibilities: `PnLEngine` SHALL NOT write to `CanonicalState` directly, under any circumstance (AD-010); SHALL NOT retain its own persisted copy of Realized PnL (cumulative), Equity, or Peak Equity as instance state surviving across ticks (AD-001's non-duplication principle, INV-004); SHALL NOT read or compute Drawdown, Drawdown Ratio, Position, or any non-financial runtime value.

Runtime Guarantees: deterministic given identical inputs (INV-006); every output is a pure function of the inputs listed above, with no dependency on wall-clock time, randomness, or any value not explicitly listed as an input.

Related Architecture Decisions: AD-001, AD-003, AD-004, AD-005 (non-duplication principle), AD-016.
Related FRA: FR-001, FR-002, FR-003, FR-004, FR-005, FR-006, FR-007, FR-008, FR-009, FR-015.
Related SDA: DEP-001, DEP-003, DEP-004, DEP-005, DEP-006, DEP-007, DEP-008, DEP-009, DEP-010, DEP-011, DEP-013, DEP-015, DEP-018.
Related Capability: CAP-001, CAP-002, CAP-003, CAP-004, CAP-010.

## 10. CanonicalEnforcer Specification

Purpose: exclusive Writer-on-Behalf-Of path for every field of `CanonicalState`, including every financial value (AD-010).

`CanonicalEnforcer` retains its four existing financial Writer-on-Behalf-Of responsibilities unchanged in contract shape: the Realized PnL (event) writer (currently `apply_pnl`), the Equity writer (currently `apply_equity`, its contract narrowed per Section 8 to unconditional storage, since the comparison it indirectly triggered inside `CanonicalState.update_equity` is removed), the risk-values writer (currently `apply_risk`, covering Drawdown and Drawdown Ratio, unchanged), and the position writer (currently `apply_position`, unchanged, out of this unit's scope).

`CanonicalEnforcer` gains exactly two new Writer-on-Behalf-Of responsibilities, both following the identical contract shape already established by the four existing financial writers (accept a value or `None`; if `None`, return the current stored value unchanged; otherwise store the value via `CanonicalState` and return the confirmed stored value):

- a Realized-PnL-Cumulative writer, storing the value `PnLEngine` Responsibility 2 returns into the new `realized_pnl_cumulative` key (Section 8).
- a Peak-Equity writer, storing the value `PnLEngine` Responsibility 2 returns into the existing `peak_equity` key, now written explicitly rather than derived internally by `CanonicalState`'s own comparison (Section 8, Storage Behaviour).

### Interface Contract Fields

Inputs: values returned by `PnLEngine` (Realized PnL event, Realized PnL cumulative, Equity, Peak Equity), by `RiskEngine` (Drawdown, Drawdown Ratio, exposure), and by `PositionEngine` (Position) - each passed by `RunLoop`, never computed by `CanonicalEnforcer` itself.

Outputs: the confirmed, stored value for each field, read back from `CanonicalState` immediately after storage, matching the existing pattern's return-the-stored-value contract.

Required Preconditions: the value passed for each financial field is either the exact value its Computational Authority returned for the current tick, or `None` (no-op, current value preserved).

Required Postconditions: after a non-`None` call, `CanonicalState`'s corresponding key holds exactly the value passed in, with no transformation.

Forbidden Responsibilities: `CanonicalEnforcer` SHALL NOT compute, derive, or transform any financial value; SHALL NOT compare, accumulate, or apply any conditional logic to a financial value beyond the `None`-check already established by its existing pattern.

Runtime Guarantees: every write is atomic with respect to a single financial key; no partial-write state is observable between two `CanonicalEnforcer` calls within the same tick.

Failure Behaviour: not independently applicable; `CanonicalEnforcer` stores whatever `PnLEngine` and `RiskEngine` return, and their own `RUNTIME_FAILURE_EVENT` non-mutation contract (Section 15) is what guarantees financial-state non-mutation on that tick, not any special-case logic within `CanonicalEnforcer` itself.

Related Architecture Decisions: AD-002, AD-004, AD-008, AD-010.
Related FRA: FR-003, FR-006, FR-011, FR-017.
Related SDA: DEP-001, DEP-002, DEP-003, DEP-014, DEP-018.
Related Capability: CAP-002, CAP-004, CAP-007, CAP-014.

## 11. RunLoop Specification

Purpose: pure orchestration of the tick sequence; `RunLoop` performs no computation on any financial value (AD-003, AD-011).

Inputs: the current tick's raw tick data (unchanged shape, `{"tick": ..., "price": ...}`).

Outputs: the unchanged tick-result dictionary shape (`run_engine/core/loop.py:82-97`), with `"equity"` and `"pnl"` continuing to reflect the values `PnLEngine` returned for the tick, now sourced from `PnLEngine`'s two responsibilities instead of from `RunLoop`'s own arithmetic.

Required Preconditions: `CanonicalState` has already been initialized (via `RunLoop.__init__`, unchanged) before `step()` is first called.

Required Postconditions: after `step()` returns, every financial `CanonicalState` key reflects exactly the values `PnLEngine` and `RiskEngine` computed for the tick just processed, published via `CanonicalEnforcer` with no intervening arithmetic performed by `RunLoop`.

Forbidden Responsibilities: `RunLoop` SHALL NOT perform addition, subtraction, comparison, or any other arithmetic operation on Realized PnL (event or cumulative), Equity, Peak Equity, Drawdown, or Drawdown Ratio; the line `equity = self.cstate.get()["equity"] + pnl` (`run_engine/core/loop.py:71`) is specified to be removed in its current form (Section 22, Implementation Units), replaced by orchestration calls only.

Runtime Guarantees: `RunLoop` invokes `PnLEngine`'s two responsibilities and `RiskEngine` in the exact order specified in Section 16, every tick, with no conditional skipping based on financial-value content.

Failure Behaviour: `RunLoop` itself performs no failure handling specific to financial values; it forwards whatever `PnLEngine`, `RiskEngine`, and `PerformanceEngine` return, and their own non-mutation contracts (Section 15) govern the outcome on a `RUNTIME_FAILURE_EVENT` tick.

Related Architecture Decisions: AD-003, AD-004, AD-010, AD-011, AD-016.
Related FRA: FR-005, FR-006, FR-007, FR-008, FR-009, FR-016.
Related SDA: DEP-001, DEP-005, DEP-011, DEP-013, DEP-015.
Related Capability: CAP-003, CAP-004, CAP-012, CAP-013.

## 12. RiskEngine Specification

Purpose: exclusive Computational Authority for Drawdown and Drawdown Ratio (AD-006, AD-007); strictly read-only consumer of Equity and Peak Equity (AD-011).

Allowed Inputs: the full canonical state dictionary (read-only access to every key, but financial usage restricted to `equity` and `peak_equity`); the current tick's Position dictionary (unchanged, out of this unit's scope); the current tick's regime classification (unchanged, out of this unit's scope).

Outputs: Drawdown, Drawdown Ratio, and exposure (the risk-limiting formula's output, unchanged arithmetic, out of this unit's scope), returned together as the existing risk dictionary shape.

Forbidden Responsibilities: `RiskEngine` SHALL NOT retain `equity`, `peak_equity`, `drawdown`, or `drawdown_ratio` as instance state surviving across ticks, in any form, including a transient per-call local reused across calls (AD-005); SHALL NOT read `CanonicalState`'s financial values from any source other than the `state` parameter passed to it for the current tick; SHALL NOT write to `CanonicalState` directly, under any circumstance.

Consumer Boundary: read-only for Equity and Peak Equity; Computational Authority (write, via `RunLoop`/`CanonicalEnforcer`) for Drawdown and Drawdown Ratio only.

Runtime Guarantees: `RiskEngine` is fully stateless with respect to every financial value in this unit's scope; two consecutive calls with identical `state`, `position`, and `regime` arguments produce identical Drawdown and Drawdown Ratio outputs (INV-006).

Failure Behaviour: `RiskEngine` is not directly gated by `RUNTIME_FAILURE_EVENT` today and this document introduces no such gate; Drawdown and Drawdown Ratio remain correct by construction on a failure tick because they are always recomputed fresh from whatever Equity and Peak Equity `CanonicalState` currently holds, and those two inputs are themselves protected from mutation by `PnLEngine`'s non-mutation contract (Section 15) for that same tick.

Related Architecture Decisions: AD-005, AD-006, AD-007, AD-011, AD-015.
Related FRA: FR-009, FR-010, FR-011, FR-012, FR-013, FR-018.
Related SDA: DEP-002, DEP-007, DEP-008, DEP-009, DEP-012, DEP-017.
Related Capability: CAP-004, CAP-005, CAP-006, CAP-008, CAP-011.

## 13. PerformanceEngine Specification

Purpose: strictly read-only consumer of Realized PnL (event) only (AD-011, already COMPLETE, CAP-009).

Allowed Inputs: the current tick's execution decision, the current tick's Realized PnL (event) value, the current tick's regime classification, the current tick's lifecycle event (for the existing `RUNTIME_FAILURE_EVENT` guard) - unchanged from today.

Consumer Boundary: no access, of any kind, to Realized PnL (cumulative), Equity, Peak Equity, Drawdown, or Drawdown Ratio. This document introduces no change to `PerformanceEngine` and specifies no Implementation Unit for it (Section 22), since CAP-009 is already COMPLETE.

Related Architecture Decisions: AD-011, AD-012.
Related FRA: FR-014.
Related SDA: DEP-018.
Related Capability: CAP-009.

## 14. Reset Behaviour

`CanonicalState.reset()` (the existing `self.__init__()` mechanism, `run_engine/core/canonical_state.py:104-106`) is specified to reinitialize the full schema defined in Section 8, including the new `realized_pnl_cumulative` key, to the exact Initialization values stated in Section 8. `equity` and `peak_equity` reset to Initial Capital together with `realized_pnl_cumulative` resetting to `0.0`, consistent with Equity's reconstruction rule (Section 7) evaluated at the reset boundary: Initial Capital plus zero cumulative Realized PnL plus zero Unrealized PnL.

`RiskEngine` requires no reset mechanism of any kind. After AD-005's removal of its `self.last_equity` and `self.peak_equity` instance attributes, `RiskEngine` holds no persisted state relevant to this unit's scope; every value it produces is computed fresh from its `state` parameter on every call, so no reset boundary has any observable effect on it.

`PnLEngine` requires no reset mechanism for the financial values in this unit's scope, since Responsibility 2 (Section 9) receives every prior value as an explicit input from `CanonicalState` rather than retaining one internally; a `CanonicalState.reset()` call is immediately reflected on `PnLEngine`'s next invocation without any action on `PnLEngine`'s part.

## 15. Runtime Failure Behaviour

A tick whose lifecycle event is `RUNTIME_FAILURE_EVENT` leaves every financial object in this unit's scope unmodified, extending the existing, already-certified guard pattern (`run_engine/core/pnl.py:23-24`, `run_engine/core/performance.py:8-9`) to the two newly-relocated and newly-created values.

Specification: `PnLEngine`'s Responsibility 1 already returns `0.0` when the lifecycle event's type is not in `{TRADE_CLOSED, PARTIAL_CLOSE}`, which includes `RUNTIME_FAILURE_EVENT`; this guard requires no change. `PnLEngine`'s Responsibility 2 is specified to apply the identical guard: when the current tick's lifecycle event is `RUNTIME_FAILURE_EVENT`, Responsibility 2 returns the three prior canonical values (Realized PnL cumulative, Equity, Peak Equity) unchanged, rather than applying its normal postconditions (Section 9); this is consistent with Realized PnL (event) being `0.0` on the same tick, since `0.0` added to any prior value under the normal postcondition formula would already produce the unchanged value - Responsibility 2's explicit guard exists to make this non-mutation an explicit postcondition rather than an incidental arithmetic coincidence, and to remain correct even if a future unit changes the underlying formula. `RiskEngine` requires no explicit `RUNTIME_FAILURE_EVENT` guard, since Drawdown and Drawdown Ratio are always freshly recomputed from Equity and Peak Equity, both already protected by `PnLEngine`'s guard for the same tick. `PerformanceEngine`'s existing guard (`run_engine/core/performance.py:8-9`) is unchanged.

This closes CAP-010's pending-re-verification status once implemented and certified (Section 23, Failure Validation).

## 16. Runtime Ordering Specification

The following is the complete, normative per-tick ordering. It is a specification of required call sequence, not an implementation; no step below is code. The specified ordering is normative with respect to observable architectural dependencies, not with respect to internal implementation structure: an implementation remains conformant so long as it preserves the same dependencies, the same temporal semantics, the same consumer contracts, and the same observable runtime results as the eighteen steps below; it need not structure its internal code identically to the step list itself.

1. `RunLoop` sets `runtime_status` to `RUNNING`, via `CanonicalEnforcer` (unchanged).
2. `StateEngine.update(tick)` produces the current tick's state (unchanged).
3. `CanonicalState` records the current tick and price (unchanged).
4. `RegimeClassifier.classify(state)` produces the current regime; `CanonicalState` records it (unchanged).
5. The pre-trade Position snapshot is read from `CanonicalState` (unchanged).
6. `StrategySelector.select(...)` produces strategy weights; published via `CanonicalEnforcer` (unchanged).
7. `StrategySelector.decide(...)` produces the execution decision; published via `CanonicalEnforcer` (unchanged).
8. `Executor.execute(decision, position_pre)` produces the execution result (unchanged).
9. `TradeLifecycleEngine.on_execution(execution, state)` produces the current tick's lifecycle event, or its absence (unchanged).
10. `TradeLifecycleEngine.current_position()` produces the current lifecycle-tracked position (unchanged).
11. `PositionEngine.update_post_trade(...)` produces the new Position; published via `CanonicalEnforcer` (unchanged).
12. `RunLoop` retrieves the prior canonical Realized PnL (cumulative), Equity, and Peak Equity from `CanonicalState` (new step, AD-001/AD-003/AD-004).
13. `PnLEngine` Responsibility 1 computes Realized PnL (event) from the current tick's lifecycle event and the pre-trade entry basis (unchanged computation, now explicitly ordered before Responsibility 2); published via `CanonicalEnforcer`'s Realized-PnL-event writer (unchanged key).
14. `PnLEngine` Responsibility 2 computes Realized PnL (cumulative), Equity, and Peak Equity from the prior canonical values (step 12) and the current tick's Realized PnL (event) (step 13); each published via `CanonicalEnforcer`'s corresponding writer - the Realized-PnL-Cumulative writer (new), the existing Equity writer, and the new Peak-Equity writer (new step, AD-001/AD-003/AD-004).
15. `RunLoop` retrieves the full, now-current canonical state from `CanonicalState`.
16. `RiskEngine.check(canonical_state, position, regime)` computes Drawdown, Drawdown Ratio, and exposure, reading Equity and Peak Equity exclusively from the canonical state retrieved in step 15 (unchanged call, canonical-only input source per AD-006); published via `CanonicalEnforcer`'s existing risk writer.
17. `PerformanceEngine.update(decision, event_pnl, regime, trade_event)` computes updated performance statistics from the current tick's Realized PnL (event) only (unchanged); published via `CanonicalEnforcer`'s existing performance writer.
18. `RunLoop` returns the unchanged tick-result dictionary shape.

This ordering preserves every existing step's relative position (`run_engine/core/loop.py:33-97`) and inserts exactly two new steps (12, 14's Peak-Equity/cumulative-PnL publication) at the point currently occupied by `RunLoop`'s own Equity arithmetic (`run_engine/core/loop.py:71-72`), consistent with AD-016's determinism-preservation requirement and ADR-010's already-established Deterministic Runtime Execution Ordering.

## 17. Canonical Publication Rules

Every financial object is published exactly once per tick, exclusively through `CanonicalState`, exclusively via `CanonicalEnforcer` (AD-002, AD-008, AD-010). No financial value is published through any other channel; no component other than `CanonicalEnforcer` writes to `CanonicalState`; no financial value has more than one storage location (Section 8, complete schema). Publication for a given tick is complete once step 17 of Section 16 has executed; no financial value is read by any consumer before its Computational Authority has published it for the current tick.

## 18. Consumer Rules

Restating the Architecture document's Consumer Boundary Matrix (AD-011) as a binding Specification rule: `PnLEngine` writes (via `CanonicalEnforcer`) Realized PnL (event, cumulative), Equity, and Peak Equity only; `RiskEngine` writes (via `CanonicalEnforcer`) Drawdown, Drawdown Ratio, and exposure only, and reads Equity and Peak Equity only, read-only; `PerformanceEngine` reads Realized PnL (event) only, read-only, and writes no financial value; `RunLoop` writes no financial value and reads only what it must pass through to a Computational Authority or `CanonicalEnforcer`; `CanonicalState` computes no financial value; `CanonicalEnforcer` computes no financial value. No component in this unit's scope reads or writes any financial value outside this matrix.

## 19. Compatibility Rules

The following contracts, already certified by P1-03, P1-03.1, P1-04, P2-01, P2-02, and P2-02A, remain unchanged by every specification in this document (FR-019, AD-016): the `entry_basis` pre-trade handoff from `PositionEngine`'s pre-trade snapshot to `PnLEngine`'s Responsibility 1 (unchanged parameter, unchanged source); `PositionEngine`'s weighted-average Scale-In entry price computation (untouched, out of scope); the `RUNTIME_FAILURE_EVENT` non-mutation contract for `PerformanceEngine.stats` (unchanged); the P2-02A Position/Exposure separation (`risk_allocation_factor`, `exposure` keys, untouched, out of scope). No decision or specification in this document renames, reshapes, or removes any `CanonicalState` key that existed before this unit, other than changing `peak_equity`'s and `equity`'s storage semantics from internally-derived to externally-supplied (Section 8), which does not change either key's name, type, or read contract for any existing consumer.

Related SDA: DEP-016 (the Compatibility cluster's own dependency record, requiring every P2-03 decision to coexist with these pre-existing contracts unchanged).

## 20. Determinism Requirements

Per AD-016 and INV-006: an identical sequence of lifecycle events and tick inputs, replayed through the runtime ordering specified in Section 16, produces an identical sequence of values for every financial object in Section 7, on every replay. No specification in this document introduces randomness, wall-clock dependence, or any input to a financial computation beyond the explicit inputs named in Sections 9 and 12. `PnLEngine`'s Responsibility 2 and `RiskEngine`'s computation are both specified as pure functions of their named inputs (Sections 9, 12); no hidden instance state participates in the output of either.

## 21. Interface Contracts

The complete, formal interface contract for each of the six runtime components in scope, consolidating Sections 9 through 13.

### P2-03-IC-001 - PnLEngine

Purpose: exclusive Computational Authority for Realized PnL (event), Realized PnL (cumulative), Equity, Peak Equity.
Inputs: lifecycle event (or absence), entry basis, prior canonical Realized PnL (cumulative), prior canonical Equity, prior canonical Peak Equity.
Outputs: Realized PnL (event); structured result of Realized PnL (cumulative), Equity, Peak Equity.
Required Preconditions: Section 9.
Required Postconditions: Section 9.
Forbidden Responsibilities: Section 9.
Runtime Guarantees: deterministic, stateless with respect to canonical values.
Failure Behaviour: Section 15.
Related Architecture Decisions: AD-001, AD-003, AD-004, AD-005, AD-016.
Related FRA: FR-001 through FR-009, FR-015.
Related SDA: DEP-001, DEP-003 through DEP-011, DEP-013, DEP-015, DEP-018.
Related Capability: CAP-001, CAP-002, CAP-003, CAP-004, CAP-010.

### P2-03-IC-002 - CanonicalState

Purpose: sole Authoritative Owner of all six financial objects in scope.
Inputs: values passed by `CanonicalEnforcer` only.
Outputs: the current canonical state dictionary, readable by any component with read access under Section 18.
Required Preconditions: only `CanonicalEnforcer` calls any storage-mutating responsibility.
Required Postconditions: every stored value is exactly the value most recently passed by `CanonicalEnforcer`, with no transformation.
Forbidden Responsibilities: no computation, comparison, or derivation of any financial value (Section 8, Storage Behaviour).
Runtime Guarantees: single storage location per financial value (Section 8); reset restores the full schema (Section 14).
Failure Behaviour: not independently applicable; governed by its writers' own non-mutation contracts.
Related Architecture Decisions: AD-002, AD-004, AD-008, AD-009, AD-014.
Related FRA: FR-003, FR-006, FR-011, FR-017.
Related SDA: DEP-001, DEP-002, DEP-003, DEP-012, DEP-014, DEP-018.
Related Capability: CAP-002, CAP-007, CAP-011, CAP-014.

### P2-03-IC-003 - CanonicalEnforcer

Purpose: exclusive Writer-on-Behalf-Of path for all `CanonicalState` fields.
Inputs: Section 10.
Outputs: Section 10.
Required Preconditions: Section 10.
Required Postconditions: Section 10.
Forbidden Responsibilities: Section 10.
Runtime Guarantees: atomic single-key writes.
Failure Behaviour: Section 10.
Related Architecture Decisions: AD-002, AD-004, AD-008, AD-010.
Related FRA: FR-003, FR-006, FR-011, FR-017.
Related SDA: DEP-001, DEP-002, DEP-003, DEP-014, DEP-018.
Related Capability: CAP-002, CAP-004, CAP-007, CAP-014.

### P2-03-IC-004 - RunLoop

Purpose: pure orchestration; performs no financial computation.
Inputs: raw tick data.
Outputs: unchanged tick-result dictionary.
Required Preconditions: Section 11.
Required Postconditions: Section 11.
Forbidden Responsibilities: Section 11.
Runtime Guarantees: invokes Section 16's ordering unconditionally, every tick.
Failure Behaviour: forwards `PnLEngine`/`RiskEngine`/`PerformanceEngine`'s own non-mutation outcomes.
Related Architecture Decisions: AD-003, AD-004, AD-010, AD-011, AD-016.
Related FRA: FR-005 through FR-009, FR-016.
Related SDA: DEP-001, DEP-005, DEP-011, DEP-013, DEP-015.
Related Capability: CAP-003, CAP-004, CAP-012, CAP-013.

### P2-03-IC-005 - RiskEngine

Purpose: exclusive Computational Authority for Drawdown, Drawdown Ratio; read-only consumer of Equity, Peak Equity.
Inputs: canonical state (read-only), Position, regime.
Outputs: Drawdown, Drawdown Ratio, exposure.
Required Preconditions: Section 12.
Required Postconditions: Section 12.
Forbidden Responsibilities: Section 12.
Runtime Guarantees: fully stateless with respect to this unit's financial values.
Failure Behaviour: Section 12.
Related Architecture Decisions: AD-005, AD-006, AD-007, AD-011, AD-015.
Related FRA: FR-009 through FR-013, FR-018.
Related SDA: DEP-002, DEP-007, DEP-008, DEP-009, DEP-012, DEP-017.
Related Capability: CAP-004, CAP-005, CAP-006, CAP-008, CAP-011.

### P2-03-IC-006 - PerformanceEngine

Purpose: read-only consumer of Realized PnL (event) only.
Inputs: decision, Realized PnL (event), regime, lifecycle event.
Outputs: updated performance statistics (unchanged).
Required Preconditions: none beyond today's existing contract.
Required Postconditions: no financial value beyond Realized PnL (event) is read or written.
Forbidden Responsibilities: no access to cumulative PnL, Equity, Peak Equity, Drawdown, Drawdown Ratio.
Runtime Guarantees: unchanged from today's already-COMPLETE state.
Failure Behaviour: unchanged existing guard (`run_engine/core/performance.py:8-9`).
Related Architecture Decisions: AD-011, AD-012.
Related FRA: FR-014.
Related SDA: DEP-018.
Related Capability: CAP-009.

## 22. Implementation Units

Five Implementation Units are derived, matching this unit's five components requiring a code change; `PerformanceEngine` receives no Implementation Unit, since CAP-009 is already COMPLETE and no decision in the Architecture requires modifying it (Section 13). Each implementation unit represents one logically cohesive implementation scope. A unit may affect one or more runtime files where required by the approved Architecture; for the five units derived below, exactly one runtime file each currently satisfies this scope. No sequence or commit order is asserted between units; each unit's Preconditions field states the technical prerequisite, if any, a future implementation must satisfy before that unit's own Compile Point is meaningful.

### P2-03-IU-001 - PnLEngine Extension

Purpose: implement Responsibility 2 (Section 9) alongside the existing, unchanged Responsibility 1.
Scope: AD-001, AD-003, AD-004.
Runtime Files: `run_engine/core/pnl.py`.
Preconditions: none beyond the current, verified HEAD `815cd8a` state.
Expected Runtime Behaviour: `PnLEngine` produces, for a scripted lifecycle-event sequence, a Realized PnL (cumulative) sequence equal to the running sum of the corresponding Realized PnL (event) sequence, an Equity sequence equal to Initial Capital plus that running sum, and a Peak Equity sequence equal to the running maximum of that Equity sequence.
Validation Goals: numeric equivalence with the current system's Equity/Peak-Equity sequence for an identical scripted sequence (Section 23, Determinism Validation).
Compile Point: `python -m compileall run_engine` succeeds with this unit's change applied, in isolation from IU-002 through IU-005.
Runtime Validation: `PnLEngine`'s two responsibilities invoked directly against a scripted sequence of lifecycle events and prior-value inputs, independent of `RunLoop`.
Acceptance Criteria: P2-03-AC-001 through AC-004 (Section 24).

### P2-03-IU-002 - CanonicalState Schema Extension

Purpose: add the `realized_pnl_cumulative` key; remove the internal Peak-Equity comparison from storage behaviour; extend `reset()`.
Scope: AD-002, AD-008, AD-009, AD-014.
Runtime Files: `run_engine/core/canonical_state.py`.
Preconditions: none beyond the current, verified HEAD `815cd8a` state.
Expected Runtime Behaviour: `CanonicalState`'s schema contains fifteen top-level keys (Section 8) after initialization; `reset()` restores every financial key to its Initialization value (Section 8).
Validation Goals: schema completeness; reset correctness.
Compile Point: `python -m compileall run_engine` succeeds with this unit's change applied.
Runtime Validation: instantiate `CanonicalState`, verify the full key set and initial values; call `reset()` after simulated mutation, verify full restoration.
Acceptance Criteria: P2-03-AC-005 through AC-008.

### P2-03-IU-003 - CanonicalEnforcer Extension

Purpose: add the two new Writer-on-Behalf-Of responsibilities (Realized-PnL-Cumulative, Peak-Equity).
Scope: AD-010.
Runtime Files: `run_engine/core/canonical_enforcer.py`.
Preconditions: IU-002's Compile Point achieved (the new `CanonicalState` key must exist for this unit's new writer to have a storage target).
Expected Runtime Behaviour: each new writer, called with a value, stores it and returns the confirmed stored value; called with `None`, returns the current stored value unchanged.
Validation Goals: contract-shape consistency with the four existing financial writers.
Compile Point: `python -m compileall run_engine` succeeds with this unit's change applied.
Runtime Validation: call each new writer directly against a `CanonicalState` instance, with both a value and `None`.
Acceptance Criteria: P2-03-AC-009 through AC-011.

### P2-03-IU-004 - RunLoop Orchestration Realignment

Purpose: remove `RunLoop`'s own Equity arithmetic; insert the two new orchestration steps (Section 16, steps 12 and 14).
Scope: AD-003, AD-010, AD-011.
Runtime Files: `run_engine/core/loop.py`.
Preconditions: IU-001, IU-002, and IU-003's Compile Points achieved (RunLoop's new orchestration calls `PnLEngine`'s new Responsibility 2 and `CanonicalEnforcer`'s two new writers, both of which must already exist).
Expected Runtime Behaviour: `RunLoop.step()` follows the exact ordering of Section 16, with no arithmetic performed by `RunLoop` itself on any financial value.
Validation Goals: ordering conformance; absence of financial arithmetic in `RunLoop`.
Compile Point: `python -m compileall run_engine` succeeds with this unit's change applied, together with IU-001 through IU-003.
Runtime Validation: run a scripted tick sequence through `RunLoop.step()` end to end; verify the returned tick-result dictionary's financial values against the expected sequence from IU-001's validation.
Acceptance Criteria: P2-03-AC-012 through AC-015.

### P2-03-IU-005 - RiskEngine Canonical-Only Input Source

Purpose: remove `self.last_equity` and `self.peak_equity` instance attributes; read Equity and Peak Equity exclusively from the `state` parameter.
Scope: AD-005, AD-006, AD-007.
Runtime Files: `run_engine/core/risk.py`.
Preconditions: IU-002's Compile Point achieved (RiskEngine's canonical-only read source requires `CanonicalState`'s `peak_equity` key to be reliably populated by `PnLEngine` via IU-001/IU-004, not merely present at initialization).
Expected Runtime Behaviour: `RiskEngine.check()` produces identical Drawdown and Drawdown Ratio values to today's system for an identical canonical-state/position/regime input, with no instance attribute surviving between calls.
Validation Goals: numeric equivalence with the current system's Drawdown/Drawdown-Ratio sequence; absence of persisted instance state.
Compile Point: `python -m compileall run_engine` succeeds with this unit's change applied, together with IU-001 through IU-004.
Runtime Validation: call `RiskEngine.check()` twice with different `state` arguments in sequence; verify the second call's output depends only on the second call's `state`, not on the first call's `state`.
Acceptance Criteria: P2-03-AC-016 through AC-019.

## 23. Validation Strategy

### P2-03-VAL-001 - Compile Validation

`python -m compileall run_engine` succeeds with zero errors, for the full `run_engine` package, after all five Implementation Units are applied together.

### P2-03-VAL-002 - Import Validation

Every modified module (`pnl.py`, `canonical_state.py`, `canonical_enforcer.py`, `loop.py`, `risk.py`) imports successfully in isolation and as part of `run_engine.main`, with no import-time error or circular-import introduced by any new responsibility.

### P2-03-VAL-003 - Runtime Validation

A scripted sequence of ticks, including at least one `TRADE_OPENED`, one `SCALE_IN`, one `PARTIAL_CLOSE`, and one `TRADE_CLOSED` lifecycle event, is run through `RunLoop.step()` end to end; every financial `CanonicalState` key after each tick matches the expected value computed from Section 7's formulas applied to the scripted sequence.

### P2-03-VAL-004 - Regression Validation

The full scripted sequence used in P2-03-VAL-003 is also run through an isolated, unmodified copy of the pre-P2-03 system (loaded via the same historical-module-isolation technique the P2-02A Final Certification already used), and the two systems' Equity, Peak Equity, Drawdown, and Drawdown Ratio sequences are compared value-by-value for functional identity, per FR-016's Validation Condition.

### P2-03-VAL-005 - Determinism Validation

The scripted sequence from P2-03-VAL-003 is run twice through the post-P2-03 system; the two resulting financial-value sequences are compared value-by-value and must be functionally identical, per AD-016/INV-006.

### P2-03-VAL-006 - Replay Validation

The scripted sequence from P2-03-VAL-003 is replayed from a fresh `RunLoop` instance a third time, after an intervening `CanonicalState.reset()` call between the second and third run; the third run's sequence must be functionally identical to the first two, confirming Reset Consistency (Section 14) does not disturb Replay Consistency.

### P2-03-VAL-007 - Compatibility Validation

The full P2-02A Final Certification's own validation scenarios (weighted-average Scale-In entry price, `entry_basis` handoff, Position/Exposure separation) are re-run unmodified against the post-P2-03 system and produce functionally identical results to the P2-02A Final Certification's own recorded output, per FR-019.

### P2-03-VAL-008 - Failure Validation

A scripted sequence including at least one `RUNTIME_FAILURE_EVENT` (via `INVALID_EXECUTION_QUANTITY`, `NO_ACTIVE_TRADE`, `OVER_CLOSE_QUANTITY`, or `UNSUPPORTED_EXECUTION_ACTION`) is run through `RunLoop.step()`; every financial `CanonicalState` key immediately before and immediately after the failure tick is identical, per Section 15.

## 24. Acceptance Criteria

- P2-03-AC-001: `PnLEngine` Responsibility 2, given a prior cumulative value and an event-PnL value, returns a new cumulative value equal to their sum.
- P2-03-AC-002: `PnLEngine` Responsibility 2, given a prior Equity value and an event-PnL value, returns a new Equity value equal to their sum.
- P2-03-AC-003: `PnLEngine` Responsibility 2, given a prior Peak Equity value and a new Equity value, returns a new Peak Equity value equal to the greater of the two.
- P2-03-AC-004: `PnLEngine` Responsibility 2, invoked with a `RUNTIME_FAILURE_EVENT` lifecycle event, returns all three prior values unchanged.
- P2-03-AC-005: `CanonicalState.get()` returns a dictionary containing exactly the fifteen top-level keys specified in Section 8, immediately after initialization.
- P2-03-AC-006: `CanonicalState`'s `realized_pnl_cumulative` key initializes to `0.0`.
- P2-03-AC-007: `CanonicalState.reset()`, called after any sequence of mutations, restores every financial key to its Section 8 Initialization value.
- P2-03-AC-008: `CanonicalState`'s storage responsibility for `peak_equity` performs no comparison; the stored value after a write equals exactly the value passed in.
- P2-03-AC-009: `CanonicalEnforcer`'s new Realized-PnL-Cumulative writer, called with a numeric value, results in `CanonicalState.get()["realized_pnl_cumulative"]` equal to that value.
- P2-03-AC-010: `CanonicalEnforcer`'s new Peak-Equity writer, called with a numeric value, results in `CanonicalState.get()["peak_equity"]` equal to that value.
- P2-03-AC-011: `CanonicalEnforcer`'s new writers, called with `None`, leave the corresponding `CanonicalState` key unchanged.
- P2-03-AC-012: `RunLoop.step()`'s source contains no arithmetic operator applied to any financial value.
- P2-03-AC-013: `RunLoop.step()`, for a scripted sequence, produces a tick-result dictionary whose `"equity"` and `"pnl"` values match the values `PnLEngine` computed for that tick.
- P2-03-AC-014: `RunLoop.step()` invokes `PnLEngine`'s Responsibility 1 before Responsibility 2, and Responsibility 2 before `RiskEngine.check()`, on every tick.
- P2-03-AC-015: `RunLoop.step()`'s returned tick-result dictionary shape is unchanged from the pre-P2-03 system's own shape (same key set).
- P2-03-AC-016: `RiskEngine.__init__` defines no `self.last_equity` or `self.peak_equity` instance attribute.
- P2-03-AC-017: `RiskEngine.check()`, called twice in sequence with different `state` arguments, produces a second-call output that depends only on the second call's `state` argument.
- P2-03-AC-018: `RiskEngine.check()`'s Drawdown output equals `state["peak_equity"] - state["equity"]` for any given `state`.
- P2-03-AC-019: `RiskEngine.check()`'s Drawdown Ratio output equals Drawdown divided by `state["peak_equity"]` when `state["peak_equity"] > 0`, and `0.0` otherwise.
- P2-03-AC-020: P2-03-VAL-004 (Regression Validation) reports functional identity between the pre-P2-03 and post-P2-03 systems for the full scripted sequence.
- P2-03-AC-021: P2-03-VAL-005 (Determinism Validation) reports functional identity between two runs of the post-P2-03 system for the identical scripted sequence.
- P2-03-AC-022: P2-03-VAL-008 (Failure Validation) reports zero financial-key differences across the `RUNTIME_FAILURE_EVENT` tick boundary.
- P2-03-AC-023: TD-006's Equity/Peak-Equity/Drawdown-input-source scope (AD-004, AD-005, AD-006) is fully implemented, with no `RiskEngine`-side instance tracking of any financial value remaining.

Twenty-three Acceptance Criteria are defined, each objectively checkable against a specific, named runtime behaviour or validation result, with no criterion requiring subjective judgment.

## 25. Traceability

### FRA Traceability

All twenty FRA requirements are addressed: FR-001 through FR-009 (Sections 7, 9, 16), FR-010 through FR-013 (Sections 7, 12), FR-014 (Section 13), FR-015 (Section 15), FR-016 (Sections 20, 23), FR-017 and FR-018 (Section 14), FR-019 (Section 19), FR-020 (respected as a non-goal; Section 7's Equity formula explicitly notes Unrealized PnL remains definitionally zero, no specification implements it).

### SDA Traceability

All eighteen SDA dependency records are addressed, each cited in at least one of Sections 9 through 13 or Section 21's Interface Contracts, matching the Architecture document's own SDA Traceability (Architecture Section 20) unchanged, since this document implements the Architecture's decisions without altering their dependency grounding.

### CGA Traceability

All fifteen CGA capabilities are addressed: CAP-001 (Section 9, Responsibility 1, unchanged), CAP-002 (Sections 8, 9, 22 IU-001/IU-002), CAP-003 (Sections 9, 11, 22 IU-001/IU-004), CAP-004 (Sections 9, 12, 22 IU-001/IU-005), CAP-005 (Section 12, 22 IU-005), CAP-006 (Section 12, Architecture AD-007, no code change beyond IU-005's instance-state removal), CAP-007 (Sections 8, 9, 10), CAP-008 (Section 12, 18), CAP-009 (Section 13, no Implementation Unit), CAP-010 (Section 15), CAP-011 (Section 14), CAP-012 and CAP-013 (Sections 20, 23 VAL-005/VAL-006), CAP-014 (Sections 8, 17), CAP-015 (Section 19).

### Architecture Traceability

All sixteen Architecture Decisions are implemented: AD-001 (Sections 8, 9, 16), AD-002 (Section 8), AD-003 (Sections 9, 11, 16), AD-004 (Sections 9, 10, 16), AD-005 (Sections 12, 14, 22 IU-005), AD-006 (Section 12), AD-007 (Section 12), AD-008 (Section 8), AD-009 (Section 8, Initialization), AD-010 (Sections 10, 17), AD-011 (Sections 12, 13, 18), AD-012 (Section 13, no Event Model introduced), AD-013 (Section 7, Drawdown/Drawdown-Ratio as the only Derived Views), AD-014 (Section 14), AD-015 (Sections 12, 22, TD-006 Section restated), AD-016 (Sections 16, 20, 23).

### ADR Traceability

ADR-002 (Section 6, no Financial Event object specified), ADR-004 (Section 19), ADR-005 (Sections 7, 9), ADR-006 (Sections 7, 8, 9, 10, 12), ADR-007 (Section 12), ADR-008 (Section 13), ADR-009 (Section 19), ADR-010 (Section 16), ADR-011 (Section 15), AI-005 (Section 20), AI-010 (Sections 8, 14), Rule OM-006 (Sections 8, 17), Rule OM-007 (Section 12), Rule OM-008 (Section 13).

### Technical Debt Traceability

TD-006 (Sections 12, 22 IU-005, 24 AC-023 - specified for full closure within this unit's P2-03 boundary); TD-001, TD-003 (Section 19, compatibility preservation, unchanged); TD-002, TD-004, TD-005, TD-007 (out of scope, not referenced by any specification in this document).

## 26. Readiness Assessment

Six runtime components are specified (`PnLEngine`, `CanonicalState`, `CanonicalEnforcer`, `RunLoop`, `RiskEngine`, `PerformanceEngine`); six Interface Contracts are defined (P2-03-IC-001 through IC-006); five Implementation Units are derived (P2-03-IU-001 through IU-005); eight Validation Strategy categories are defined (P2-03-VAL-001 through VAL-008); twenty-three Acceptance Criteria are defined (P2-03-AC-001 through AC-023). Every specification traces to at least one Architecture Decision, and through it to the FRA, SDA, and CGA (Section 25).

No specification in this document contains executable code, pseudocode, a Python method signature, a commit order, or a test implementation; every validation activity in Section 23 is described as a procedure to be performed, not as test code itself.

Readiness: READY. This document is sufficient to proceed to P2-03 Implementation, applying Implementation Units IU-001 through IU-005 against the Interface Contracts and Runtime Ordering this document specifies. This readiness assessment applies to the current scientific, architectural, and specification baseline (Sections 3 through 25); it does not preclude a future revision under the normal governance process should new evidence or a conflict emerge before or during Implementation.

## 27. Internal Consistency Review

Terminology consistency - "Computational Authority," "Authoritative Owner," "Writer-on-Behalf-Of," and "canonical" are used exactly as defined by the Architecture Baseline and inherited unchanged through the FRA, SDA, CGA, and Architecture document; no term is redefined here.

Scope consistency - no section contains a Python method signature, a code block, a control-flow keyword used as code, or a commit/file-order instruction; Section 22's Implementation Units explicitly state that no sequence or commit order is asserted between them, only technical Preconditions where a real dependency exists. Section 2 confirms every previously-established out-of-scope topic remains untouched.

Decision fidelity - every specification choice in Sections 8 through 16 cites the specific Architecture Decision it implements; no specification in this document introduces a decision the Architecture document did not already authorize (Section 5).

Formula consistency - Section 7's six formulas are cross-checked against Section 9's `PnLEngine` postconditions and Section 12's `RiskEngine` outputs; all three sections state the identical arithmetic with no contradiction.

Ordering consistency - Section 16's eighteen-step ordering is cross-checked against Sections 9 through 13's individual component contracts; each component's specified inputs are available from an earlier step in Section 16 in every case.

Traceability consistency - all twenty FRA requirements, eighteen SDA dependencies, fifteen CGA capabilities, sixteen Architecture Decisions, and every governing ADR/Invariant/Rule are accounted for in Section 25; every Technical Debt Register item is classified.

Specification-ID uniqueness - P2-03-IC-001 through IC-006, P2-03-IU-001 through IU-005, P2-03-VAL-001 through VAL-008, and P2-03-AC-001 through AC-023 are each defined exactly once and referenced only by ID thereafter.

No fabricated specification - every Interface Contract, Implementation Unit, Validation category, and Acceptance Criterion traces to a specific Architecture Decision, FRA requirement, or governing ADR; no specification in this document addresses a concern absent from the governing baseline documents.

Status: Internal Consistency Review PASS.
