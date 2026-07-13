Document Class:
Implementation Specification

Document ID:
P2-02A-SPEC

Version:
V1.0

Status:
Draft for Internal Review

Date:
2026-07-10

Project:
Trading-Bot Scientific Runtime

Subsystem:
Run Engine

Primary Location:
docs/architecture/P2_02A_POSITION_OWNERSHIP_SPECIFICATION_V1_2026-07-10.md

Depends On:
- docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md
- docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md
- ADR-004 (Position Represents Current Market Exposure), within the Architecture Baseline above
- docs/architecture/analysis/P2_02A_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-10.md
- docs/architecture/analysis/P2_02A_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-10.md
- docs/architecture/analysis/P2_02A_CAPABILITY_GAP_ANALYSIS_V1_2026-07-10.md
- docs/architecture/P2_02A_POSITION_OWNERSHIP_ARCHITECTURE_V1_2026-07-10.md
- docs/architecture/certification/P1_04_FINAL_CERTIFICATION_V1_2026-07-09.md
- docs/architecture/certification/P2_01_FINAL_CERTIFICATION_V1_2026-07-10.md
- docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md
- current runtime code at HEAD b88eae5

Referenced By:
- future P2-02A Implementation
- future P2-02A Verification
- future P2-02A Certification

---

# P2-02A Position Ownership Specification

## 1. Purpose

This document is the P2-02A Specification. It operationalizes the nine Architecture Decisions (P2-02A-AD-001 through P2-02A-AD-009) and sixteen Architecture Invariants (P2-02A-AI-001 through P2-02A-AI-016) of the approved Architecture into an exact, file-level implementation contract: which runtime files change, what each change is, in what order, and how each change is validated.

This document makes **no new architecture decision, no new scientific claim, and no new terminology**. Every decision referenced here was already made and Accepted in the Architecture document; this document's only task is operationalization, concretization, implementation preparation, and validation preparation.

This document does not implement code. It does not write a test suite. It defines the exact contract the Implementation stage must follow.

---

## 2. Scope

In scope: the exact runtime file changes, canonical data structure definitions, consumer contracts, implementation units, sequencing, and validation strategy required to realize Architecture Decisions AD-001 through AD-009.

Out of scope, unchanged from the Architecture (Section 2) and every prior P2-02A document: P2-03, P2-04, TD-006 beyond the narrow read boundary already defined by AD-008, general RiskEngine redesign, PositionSizingEngine activation, the Lifecycle Control Surface, the Tick-Complete Snapshot architecture, repository cleanup, and the automated regression test suite.

---

## 3. Binding Inputs

- docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md - ADR-004, Rules OM-001 through OM-009.
- docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md - Principle IP-002 (Single Logical Change), the Engineering Workflow.
- docs/architecture/analysis/P2_02A_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-10.md, docs/architecture/analysis/P2_02A_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-10.md, docs/architecture/analysis/P2_02A_CAPABILITY_GAP_ANALYSIS_V1_2026-07-10.md - as edited and internally reviewed.
- docs/architecture/P2_02A_POSITION_OWNERSHIP_ARCHITECTURE_V1_2026-07-10.md - nine Architecture Decisions, sixteen Architecture Invariants, as edited and internally reviewed. This is the binding source for every decision operationalized below.
- Current runtime code at HEAD b88eae5, re-inspected in Section 6 for this document's exact file-level claims.

---

## 4. Architecture Baseline

Every technical decision in this document traces to exactly one or more of the nine Architecture Decisions. No decision below extends, reinterprets, or overrides AD-001 through AD-009. Where the Architecture explicitly delegated a mechanical detail to this document (AD-007's Consequences: "risk.py's own internal variable names are unaffected... deferred to Specification"), that delegation is resolved here (Section 7.5) as a mechanical concretization, not a new decision - the Architecture's own boundary (no change to RiskEngine's formula, no new "exposure"-named field anywhere outside Position) is preserved exactly.

---

## 5. Implementation Scope

Four runtime files require changes. Seven runtime files, and the confirmed-inactive files, require none. No new file is created. No file is deleted. This is confirmed by direct re-inspection of the current code (Section 6) against every AD's stated Consequences.

---

## 6. Runtime File Inventory

**Changed (4 files):**

| File | Class/Component | Governing Decisions |
|---|---|---|
| run_engine/core/position.py | PositionEngine | AD-001, AD-002, AD-003, AD-004 |
| run_engine/core/canonical_state.py | CanonicalState | AD-004, AD-007 |
| run_engine/core/loop.py | RunLoop | AD-005, AD-006 |
| run_engine/core/risk.py | RiskEngine | AD-008 |

**Explicitly unchanged, verified by re-inspection (11 files/paths):**

| File | Reason No Change Is Required |
|---|---|
| run_engine/core/canonical_enforcer.py | apply_position() is dict-shape-agnostic; it mediates whatever dict PositionEngine returns, so a sixth key requires no change to its four-line body. No apply_exposure() is introduced (AD-003). apply_risk() is equally shape-agnostic; the rename (AD-007) is fully contained inside CanonicalState.update_risk(). |
| run_engine/core/strategy.py | StrategySelector.select()/decide() already read only position.get("position", "FLAT") from whatever dict they are passed; a sixth key is inert to this access pattern. |
| run_engine/core/execution/executor.py | Executor.execute() reads only position.get("position", "FLAT"); identical reasoning. |
| run_engine/core/pnl.py | PnLEngine.update() already receives entry_basis as an explicit float parameter, not the Position dict itself (certified P1-03.1); unaffected by any Position schema change. |
| run_engine/core/trade_lifecycle.py | TradeLifecycleEngine has no Position or Exposure field of any kind and no CanonicalState access (confirmed unchanged, FRA/CGA/Architecture Section 15). |
| run_engine/core/performance.py | No Position or Exposure involvement of any kind. |
| run_engine/main.py | Only prints RunLoop.step()'s returned dict; unaffected by internal schema changes. |
| run_engine/core/position_sizing.py | Confirmed inactive (not imported by loop.py or main.py); not activated (explicit scope protection, Architecture Section 17.5). |
| run_engine/core/equity_stabilizer.py | Confirmed inactive; unrelated to Position/Exposure. |
| run_engine/core/state.py, run_engine/core/regime.py | No Position or Exposure involvement. |
| run_engine/runtime/ (entire package) | Confirmed inactive, outside the Verified Active Execution Path (unchanged finding, FRA Section 4). |

---

## 7. Required Runtime Changes

### 7.1 position.py (PositionEngine) - operationalizes AD-001, AD-002, AD-003, AD-004

**New instance attribute**, added to `__init__`, alongside the existing five: `self.exposure = 0.0`.

**New private computation**, a pure function taking side, quantity, and last_price and returning the signed current market value defined by AD-001/AD-002:

- If quantity equals 0.0: return 0.0 exactly (explicit, unconditional FLAT rule, per AD-002 - not an incidental consequence of multiplying by an undefined side).
- Otherwise: side factor is +1.0 for "LONG", -1.0 for "SHORT"; result is side factor times quantity times last_price.

This computation is invoked, and `self.exposure` is set, at every point `self.position`, `self.side`, `self.quantity`, and `self.last_price` are currently set together: inside `project()`, inside `update_post_trade()`'s "same position" branch, and inside `_set_flat()` (where it is trivially 0.0, consistent with quantity being 0.0 in that branch).

**snapshot()** gains a sixth key: `"exposure": self.exposure`, appended after the existing five keys, in the same dict literal.

No other method of PositionEngine changes. `_weighted_average_entry_price()`, `_extract_price()`, `_safe_float()` are untouched.

### 7.2 canonical_state.py (CanonicalState) - operationalizes AD-004, AD-007

**`__init__`'s "position" default** changes from the current three-key dict to the full six-key FLAT record, matching PositionEngine's own `__init__` values exactly: position "FLAT", side None, entry_price 0.0, quantity 0.0, last_price 0.0, exposure 0.0.

**`__init__`'s top-level "exposure" key** is renamed to "risk_allocation_factor", retaining its existing default value 1.0.

**`update_risk(risk_dict)`** changes its write target from `self.state["exposure"]` to `self.state["risk_allocation_factor"]`. Its read source is unchanged: `risk_dict.get("exposure", 1.0)` - RiskEngine's own returned dict key is not renamed (Section 7.5); only CanonicalState's own storage key changes, which is the entire and sufficient scope of AD-007's Validation Obligation ("no field named 'exposure' exists anywhere in CanonicalState's schema except inside the Position record").

No other method of CanonicalState changes. `update_tick`, `update_position`, `update_equity`, `update_pnl`, `update_regime`, `update_strategy_selection`, `update_execution_decision`, `update_performance_metrics`, `update_runtime_status`, `get`, `reset` are untouched. `reset()` requires no change, since it already delegates to `__init__()`.

### 7.3 loop.py (RunLoop) - operationalizes AD-005, AD-006

**Exactly one line changes**, at the position identified in Architecture Section 19.1 as step 6:

Current: `position_pre = self.position_engine.snapshot()`
Required: `position_pre = self.cstate.get()["position"]`

No other line of `RunLoop.step()` or `RunLoop.__init__()` changes. The full 23-step sequence traced in Architecture Section 19.1 is otherwise byte-identical in order; only the source of step 6's value changes, exactly as Architecture Section 19.2 specifies.

### 7.4 risk.py (RiskEngine) - operationalizes AD-008

**`check(self, state, position, regime)`** gains one new line, reading the Position-derived Exposure from its already-existing `position` parameter into a distinctly-named local variable:

`position_exposure = position.get("exposure", 0.0)`

This name is deliberately distinct from the method's existing local variable `exposure` (already used, unchanged, for RiskEngine's own allocation-scaling computation), to avoid a Python variable-scope collision within the same function body - a mechanical concretization of AD-008/AD-007's boundary, not a new decision.

This value is read only; per AD-008.2, no functional use of it is required in this unit. The read establishes the architectural consumption boundary only. Functional use of position_exposure for risk policy remains explicitly deferred to a future architectural unit. It is not added to `check()`'s returned dict, and the returned dict's own "exposure" key (RiskEngine's allocation value) is unchanged in name and value (Section 7.5).

No other line of `check()` changes: `self.max_drawdown`, `self.max_exposure`, `self.min_exposure`, `self.last_equity`, `self.peak_equity`, the drawdown computation, the regime-dampening computation, and the returned dict's shape are all untouched, satisfying AD-008.4's explicit TD-006 boundary.

### 7.5 Resolution of AD-007's Delegated Detail

The Architecture (AD-007 Consequences) explicitly delegates one mechanical question to this document: whether RiskEngine's own returned dict key ("exposure", denoting its allocation-scaling value) is itself renamed, or whether only CanonicalState's storage key is renamed. This Specification resolves it as follows: **RiskEngine's own returned dict key remains "exposure," unchanged.** Only `CanonicalState.update_risk()`'s write target changes (Section 7.2). This is the minimal change satisfying AD-007's stated Validation Obligation exactly as written ("no field named 'exposure' exists anywhere in CanonicalState's schema except inside the Position record") without touching risk.py's return contract, consistent with AD-008.4's explicit prohibition on any change to risk.py beyond the single read described in Section 7.4.

---

## 8. Canonical Data Structures

### 8.1 CanonicalState Schema (top level, final state after this unit)

| Key | Type | Default (pre-first-tick) | Governing Decision |
|---|---|---|---|
| tick | int or None | None | unchanged |
| price | float or None | None | unchanged |
| position | dict (Section 8.2) | six-key FLAT record | AD-004 |
| equity | float | 100.0 | unchanged |
| peak_equity | float | 100.0 | unchanged |
| pnl | float | 0.0 | unchanged |
| drawdown | float | 0.0 | unchanged |
| drawdown_ratio | float | 0.0 | unchanged |
| risk_allocation_factor | float | 1.0 | AD-007 (renamed from "exposure") |
| regime | str | "UNKNOWN" | unchanged |
| strategy_selection | dict or None | None | unchanged |
| execution_decision | dict or None | None | unchanged |
| performance_metrics | dict or None | None | unchanged |
| runtime_status | str or None | None | unchanged |

### 8.2 Position Schema (nested, published via apply_position(), and CanonicalState's default)

| Key | Type | FLAT Value | Computational Authority | Authoritative Owner | Writer-on-Behalf-Of |
|---|---|---|---|---|---|
| position | str | "FLAT" | PositionEngine | CanonicalState | CanonicalEnforcer |
| side | str or None | None | PositionEngine | CanonicalState | CanonicalEnforcer |
| quantity | float | 0.0 | PositionEngine | CanonicalState | CanonicalEnforcer |
| entry_price | float | 0.0 | PositionEngine | CanonicalState | CanonicalEnforcer |
| last_price | float | 0.0 | PositionEngine | CanonicalState | CanonicalEnforcer |
| exposure | float | 0.0 | PositionEngine | CanonicalState | CanonicalEnforcer |

This is Architecture Section 10's shape, restated here as the binding schema for implementation; no field, type, or default differs from the Architecture.

### 8.3 Exposure Field Definition

Name: exposure (nested inside the Position dict only; never at CanonicalState's top level, per AD-007).
Type: float, signed.
Formula (mathematical semantics, per Architecture Section 8, restated for implementation): side factor (+1.0 LONG, -1.0 SHORT) times quantity times last_price; exactly 0.0, unconditionally, whenever quantity is 0.0.
Unit: quote currency (USDT for the active BTCUSDT scope).
Determinism: pure function of side, quantity, last_price only; no read of equity, drawdown, regime, or any RiskEngine-owned state (AD-001, AD-002).

### 8.4 risk_allocation_factor Renaming

CanonicalState's top-level key "exposure" (default 1.0, populated by RiskEngine's allocation-scaling output) is renamed to "risk_allocation_factor". RiskEngine's own internal computation and its own returned dict key are unchanged (Section 7.5). The rename occurs exclusively inside `CanonicalState.update_risk()`'s write target and `CanonicalState.__init__`'s default key.

---

## 9. Consumer Contracts

Restated from Architecture Section 15 at implementation precision; no contract differs from the Architecture.

**StrategySelector, Executor** - read `position_pre.get("position", "FLAT")` from the RunLoop-captured pre-trade view (Section 7.3); no other field is read by current certified logic; no change to either file.

**PnLEngine** - receives `position_pre["entry_price"]` as the explicit `entry_basis` parameter (unchanged call shape); never reads `exposure`; no change to pnl.py.

**RiskEngine** - receives the post-trade `position` dict via its existing, unchanged parameter; reads `position.get("exposure", 0.0)` into `position_exposure` (Section 7.4); never owns, caches, or republishes it under any "exposure"-named key.

**RunLoop** - the sole component that computes `position_pre` (Section 7.3) and orchestrates every call in the unchanged 23-step sequence (Architecture Section 19.1); computes neither Position nor Exposure itself.

**CanonicalEnforcer** - `apply_position()` remains the sole Writer-on-Behalf-Of path for the six-key Position dict, unchanged in code; `apply_risk()` remains the sole path for the renamed `risk_allocation_factor`, unchanged in code.

**CanonicalState** - stores exactly the schema in Section 8.1/8.2; computes nothing.

**PositionEngine** - the sole Computational Authority for Position and Exposure (Section 7.1); never reads Equity, Drawdown, Regime, or RiskEngine state.

**TradeLifecycleEngine** - no Position or Exposure field, no CanonicalState access; zero changes (confirmed, Section 6).

---

## 10. Runtime Information Flow

Unchanged from Architecture Section 19, restated at implementation precision. The 23-step `RunLoop.step()` sequence changes at exactly one point: step 6's source. Step 14 (`PositionEngine.update_post_trade()`) now additionally computes `exposure` internally (Section 7.1) as part of its existing return value; step 15 (`apply_position()`) publishes the resulting six-key dict through its existing, unchanged code; step 20 (`RiskEngine.check()`) gains the internal read described in Section 7.4, with no change to its call signature at the call site.

On a rejected transition (RUNTIME_FAILURE_EVENT at step 12), step 14 still executes; Side, Quantity, and Average Entry Price remain frozen (unchanged, ADR-011); `last_price` still updates unconditionally (unchanged, ratified P1-04 policy); `exposure` is therefore recomputed from the updated `last_price` even though Side/Quantity/Average-Entry-Price are frozen, exactly as Architecture Section 19.3/20 specifies. This is confirmed here as an implementation consequence of Section 7.1's computation being invoked identically on every `update_post_trade()` call, accepted or rejected, not a new rule introduced by this document.

---

## 11. Implementation Units

### Unit P2-02A-U1: PositionEngine Exposure Computation

Unit ID: P2-02A-U1.
Goal: implement Section 7.1 in full.
Affected Files: run_engine/core/position.py.
Preconditions: none blocking; Cluster A (Position Semantics) is already satisfied (Architecture Section 7, FRA Section 6).
Changes: as Section 7.1.
Postconditions: `PositionEngine.snapshot()` returns six keys, including a correctly-computed `exposure`, for every reachable Position state (FLAT, LONG, SHORT, after Scale-In, after Partial Close, after Full Close). `CanonicalState` and `RunLoop` are not yet touched; because `apply_position()` and `update_position()` are dict-shape-agnostic (Section 6), the six-key dict already flows correctly into `CanonicalState.state["position"]` as soon as this unit lands, even before Unit U2's default-shape fix - only `CanonicalState`'s pre-first-tick default remains stale (a Unit U2 concern, not a functional regression).
Compile Point: `python -m compileall run_engine/core` passes with no errors.
Runtime Test: instantiate `PositionEngine()` directly; verify `snapshot()` has exactly six keys; verify `exposure` equals 0.0 at FLAT; verify sign and magnitude for a known LONG and a known SHORT input; re-run the existing FLAT/Open/Scale-In/Partial-Close/Full-Close scenarios already used in the P1-03/P1-03.1/P1-04 certification chain and confirm `exposure` is correctly present and correctly valued at each step, with no change to the other five keys' values.
Validation: FR-002, FR-004, FR-015, FR-018; AD-001, AD-002, AD-003; Invariants P2-02A-AI-002, AI-007, AI-008, AI-009, AI-015.
Expected Commit: "Implement PositionEngine exposure computation (P2-02A Unit 1)".

### Unit P2-02A-U2: CanonicalState Schema Update

Unit ID: P2-02A-U2.
Goal: implement Section 7.2 in full.
Affected Files: run_engine/core/canonical_state.py.
Preconditions: **Unit U1 complete.** If U2 were applied before U1, the first tick's `apply_position()` call would overwrite the newly-correct six-key default with an incomplete five-key dict (PositionEngine not yet producing `exposure`), regressing the post-tick state to missing the field entirely - worse than the pre-U2 mismatch, which only affected the pre-first-tick window. This ordering is a direct implementation-level consequence of Architecture Section 13.5's byte-identity reasoning, not a new decision.
Changes: as Section 7.2.
Postconditions: `CanonicalState()`'s default position dict has six keys matching PositionEngine's own FLAT defaults exactly, both before and after the first tick (Capability 5 fully closed, both pre- and post-tick, for the first time). `CanonicalState.state` has no top-level "exposure" key; "risk_allocation_factor" exists instead, defaulting to 1.0.
Compile Point: `python -m compileall run_engine/core` passes with no errors.
Runtime Test: `CanonicalState().get()["position"]` has six keys with the FLAT values from Section 8.2, before any `step()` call. `CanonicalState().get()` contains "risk_allocation_factor", not "exposure", at the top level. `CanonicalState().update_risk({"exposure": 0.5, "drawdown": 1.0, "drawdown_ratio": 0.01})` results in `state["risk_allocation_factor"] == 0.5`.
Validation: FR-003, FR-005, FR-006, FR-007; AD-004, AD-007; Invariants P2-02A-AI-003, AI-010, AI-016.
Regression Risk: if sequenced before U1, produces a worse (post-tick, not merely pre-tick) shape mismatch (see Preconditions). Rollback Trigger: any consumer observing a missing key in `state["position"]` after the first tick.
Expected Commit: "Implement CanonicalState Position shape parity and risk_allocation_factor rename (P2-02A Unit 2)".

### Unit P2-02A-U3: RunLoop Canonical Read Path

Unit ID: P2-02A-U3.
Goal: implement Section 7.3 in full.
Affected Files: run_engine/core/loop.py.
Preconditions: **Units U1 and U2 both complete.** U3's very first read, at tick 0, reads CanonicalState's pre-first-tick default; if U2 has not landed, this default is still the old three-key shape, and while `.get("position", "FLAT")`-style reads (StrategySelector, Executor) would not fail, `PnLEngine`'s direct-index read `position_pre["entry_price"]` would receive `None` instead of `0.0` (the old default's `"entry_price": None`) - unreachable in practice at tick 0 specifically (no active trade can be closed on the very first tick), but this document specifies the strict U1-then-U2-then-U3 ordering to eliminate the fragile edge case structurally rather than rely on that incidental non-issue, consistent with the same reasoning already applied in AD-002's explicit-FLAT-rule justification.
Changes: as Section 7.3.
Postconditions: `position_pre` is sourced exclusively from `CanonicalState` on every tick, including the first. `PositionEngine.snapshot()` remains a valid method (not deleted; still useful for direct unit-level introspection of PositionEngine's own state) but is no longer called by `RunLoop`.
Compile Point: `python -m compileall run_engine/core` passes with no errors.
Runtime Test: run `RunLoop` for multiple ticks; confirm `position_pre` at each tick equals `CanonicalState`'s published value from the end of the previous tick (or the FLAT default at tick 0); re-run the certified P1-03.1 LONG/SHORT/Scale-In/Partial-Close entry-basis scenarios and the P1-04 rejected-transition scenarios; confirm byte-identical realized PnL and Position results to the pre-Unit-U3 implementation.
Validation: FR-008, FR-012, FR-016, FR-019; AD-005, AD-006; Invariants P2-02A-AI-001, AI-005, AI-006.
Regression Risk: HIGH if sequenced before U1 or U2 (schema mismatch propagates into every consumer reading the pre-trade view); LOW if correctly sequenced. Rollback Trigger: any deviation in realized PnL, weights, or execution decisions versus the pre-Unit-U3 certified results for identical tick sequences.
Expected Commit: "Implement RunLoop canonical pre-trade read path (P2-02A Unit 3)".

### Unit P2-02A-U4: RiskEngine Exposure Consumption

Unit ID: P2-02A-U4.
Goal: implement Section 7.4 and Section 7.5 in full.
Affected Files: run_engine/core/risk.py.
Preconditions: **Unit U1 complete** (Exposure must exist in the `position` dict RiskEngine already receives). Unlike U3, this unit does **not** hard-depend on U2 or U3: `RiskEngine.check()`'s `position` parameter is always the post-trade value, already correctly sourced by the unchanged `loop.py` call site regardless of the pre-trade view's sourcing (SDA Dependency P2-02A-DEP-009 is CONDITIONAL, not HARD, for exactly this reason). This unit is therefore eligible to be sequenced immediately after U1, in parallel with U2/U3; it is **recommended**, not required, to sequence it after U3, so that verification runs against a fully-migrated pipeline rather than a partially-migrated one.
Changes: as Section 7.4 and Section 7.5.
Postconditions: `RiskEngine.check()` reads `position.get("exposure", 0.0)` without raising, without mutating it, and without introducing any "exposure"-named key into its own returned dict.
Compile Point: `python -m compileall run_engine/core` passes with no errors.
Runtime Test: call `RiskEngine.check(canonical_state, position, regime)` with a `position` dict containing a known `exposure` value; confirm no exception is raised; confirm `RiskEngine`'s own returned dict (equity, peak_equity, drawdown, drawdown_ratio, exposure - the allocation value, unrenamed per Section 7.5) is byte-for-byte identical to the pre-Unit-U4 implementation for identical `state`/`position`/`regime` inputs.
Validation: FR-010, FR-011; AD-008; Invariant P2-02A-AI-011.
Regression Risk: LOW (single, isolated, read-only addition). Rollback Trigger: any observed change in RiskEngine's Peak-Equity, Drawdown, drawdown_ratio, or allocation-exposure output (TD-006 non-regression).
Expected Commit: "Implement RiskEngine read-only exposure consumption (P2-02A Unit 4)".

### Unit P2-02A-U5: Full Regression and Certification Validation

Unit ID: P2-02A-U5.
Goal: re-run the complete existing certification suite plus this unit's own validation conditions across the fully-integrated system.
Affected Files: none (validation-only; no runtime file is modified by this unit).
Preconditions: Units U1, U2, U3, U4 all complete.
Changes: none.
Postconditions: full P2-02A certification readiness.
Compile Point: `python -m compileall run_engine` (whole tree, not core/ only, matching the governing task's own check).
Runtime Test: the complete manual validation battery (Section 13), matching the methodology already used and certified sufficient for P1-03, P1-03.1, P1-04, and P2-01 (TD-005, unautomated by design in this unit).
Validation: all twenty FRA requirements; all sixteen Architecture Invariants.
Expected Commit: none - this unit's output is the P2-02A Final Certification document, a separate governance artifact, not a code commit.

---

## 12. Implementation Sequence Justification

**U1 first**: Exposure must exist as a computed value before any other unit can publish it (U2), read it as a canonical source (U3), or consume it (U4) - the direct implementation consequence of SDA Dependencies P2-02A-DEP-002 and P2-02A-DEP-008 (both HARD, both rooted in Cluster B/C preceding D2 and H). Fulfilled dependency: Architecture AD-001/AD-002/AD-003 become concretely realized in code. Freed for later units: U2's default-shape fix can now target the true, PositionEngine-produced shape; U4's read has a real value to read. Risk of different ordering: any later unit landing first would either have nothing to publish/read (U2, U4) or would re-source a pre-trade view that still lacks the Exposure field (U3), each producing an incomplete or inconsistent intermediate state.

**U2 second**: CanonicalState's default and publication shape must match PositionEngine's now-corrected output before U3 makes CanonicalState the sole pre-trade source - the implementation consequence of SDA Dependency P2-02A-DEP-004 (C/OQ-006 to D2, CONDITIONAL) and P2-02A-DEP-010, both resolved by Architecture AD-004. Fulfilled dependency: Capability 5 (Canonical Position Shape) becomes fully closed, both pre- and post-tick. Freed for later units: U3 can safely source `position_pre` from CanonicalState without risking a stale or incomplete default at tick 0. Risk of different ordering: sequencing U2 before U1 regresses the post-tick shape (Unit U2's own Preconditions); sequencing U2 after U3 would let U3's first tick observe the still-mismatched old default.

**U3 third**: the canonical read path can only be safely established once both the value (U1) and its correct default/publication shape (U2) exist - the implementation consequence of SDA Dependencies P2-02A-DEP-005, P2-02A-DEP-006, and P2-02A-DEP-007 (all HARD), resolved by Architecture AD-005/AD-006. Fulfilled dependency: TD-001 (the dual-state read pattern) is fully resolved; FR-008 and FR-019 become simultaneously satisfied (Architecture Section 13.4). Freed for later units: U4 gains a fully-migrated pipeline to verify against, though it does not strictly require this (see U4's own Preconditions). Risk of different ordering: sequencing U3 before U1/U2 risks propagating an incomplete or stale Position view into every pre-trade consumer, including the certified PnLEngine entry_basis contract.

**U4 fourth (or in parallel with U2/U3, after U1)**: RiskEngine's consumption is the final piece required for full ADR-004 conformance (RiskEngine "SHALL consume Position-derived Exposure," a verbatim requirement) - the implementation consequence of SDA Dependency P2-02A-DEP-008 (HARD, from Cluster C) and the conditional P2-02A-DEP-009, resolved by Architecture AD-008. Fulfilled dependency: the last of the CGA's sixteen closable capability gaps (Capability 14) is closed. Freed for later units: none further within P2-02A; this is the last cluster-level unit. Risk of different ordering: sequencing U4 before U1 would have nothing valid to read (position.get("exposure", 0.0) would silently default to 0.0 for every call, masking the absence of real computation rather than failing loudly - a correctness risk, not a crash risk, and therefore a more dangerous failure mode than an exception would be).

**U5 last**: full regression validation is only meaningful once every prior unit has landed - the implementation consequence of SDA Dependency P2-02A-DEP-011 (Cluster I, cross-cutting, HARD), resolved by Architecture AD-009. Fulfilled dependency: every FRA requirement and Architecture Invariant is verified against the complete, integrated system, not a partial one. Risk of different ordering: validating before all units land would produce false-positive or false-negative results not attributable to the finished system.

This sequence is directly and exclusively derived from the FRA's requirement dependencies (Section 19), the SDA's Dependency Graph and Dependency Stages (Sections 17, 24), the CGA's Capability Gap Matrix (Section 24), and the Architecture's own nine decisions; no new ordering rationale is introduced here beyond restating these at file-level implementation precision.

---

## 13. Validation Strategy

**Compile Criteria** (every unit): `python -m compileall run_engine/core` (per-unit) and `python -m compileall run_engine` (Unit U5, whole tree) pass with no errors.

**Import Criteria** (every unit): `run_engine.core.loop.RunLoop` and every directly-touched module import without error; no circular import is introduced, since no new cross-module import is added by any of the four changes (Section 7).

**Runtime Criteria**: as specified per-unit in Section 11's Runtime Test field. Collectively, after U1 through U4: (a) `PositionEngine.snapshot()` and `CanonicalState.get()["position"]` both return the six-key schema (Section 8.2) with identical values at every observed tick; (b) `CanonicalState.get()` contains "risk_allocation_factor," not "exposure," at the top level; (c) `RiskEngine.check()` runs without exception against a six-key `position` dict; (d) a full multi-tick `RunLoop` run, covering FLAT, Open, Scale-In, Partial Close, and Full Close for both LONG and SHORT, plus at least one rejected transition (invalid quantity), completes without exception and produces the expected `exposure` values at each step.

**Invariants** (checked after U5, against the fully-integrated system): all sixteen Architecture Invariants, P2-02A-AI-001 through P2-02A-AI-016, individually re-verified (Section 14).

**Regression Risks**: enumerated per-unit in Section 11; the aggregate regression risk is the certified P1-03/P1-03.1/P1-04/P2-01 scenario suite, re-run in full after U3 (the unit most likely to affect PnL results) and again after U5 (final confirmation).

**Rollback Triggers**: any Compile, Import, or Runtime Criterion failing for a given unit halts progress to the next unit, per Principle IP-004 (Continuous Validation); the specific per-unit trigger is stated in each unit's own Regression Risk field (Section 11). No unit is committed if its own validation gate fails.

---

## 14. Runtime Invariants

All sixteen Architecture Invariants apply unchanged to this Specification; each is restated here with its concrete, post-implementation verification point.

**P2-02A-AI-001** (exactly one authoritative Position value) - verified by: `CanonicalState.state["position"]` is the only object any Unit U3-migrated consumer ultimately reads from.

**P2-02A-AI-002** (PositionEngine sole Computational Authority) - verified by: no file other than position.py computes any of the six Position fields (Section 6's file inventory).

**P2-02A-AI-003** (CanonicalState sole Authoritative Owner) - verified by: Unit U2's default/publication shape parity.

**P2-02A-AI-004** (CanonicalEnforcer sole Writer-on-Behalf-Of) - verified by: no new CanonicalEnforcer method exists (Section 7, canonical_enforcer.py unchanged).

**P2-02A-AI-005** (pre-trade view is not a second ownership path) - verified by: Unit U3's single-line change; `PositionEngine.snapshot()` no longer called externally by RunLoop.

**P2-02A-AI-006** (post-trade Position is canonical tick-end state) - verified by: Unit U1/U2's unchanged publication mechanism (apply_position(), unchanged).

**P2-02A-AI-007** (Exposure not an independent entity) - verified by: Exposure exists only nested inside the Position dict (Section 8.3), never as a sibling top-level key.

**P2-02A-AI-008** (Exposure deterministic pure function) - verified by: Unit U1's Runtime Test (identical Position inputs, identical Exposure outputs).

**P2-02A-AI-009** (Exposure exactly 0.0 at FLAT) - verified by: Unit U1's explicit quantity-equals-0.0 guard (Section 7.1).

**P2-02A-AI-010** (risk_allocation_factor semantically/nominally distinct) - verified by: Unit U2's rename; no "exposure"-named key exists outside the Position record after U2.

**P2-02A-AI-011** (RiskEngine read-only, no ownership) - verified by: Unit U4's Runtime Test (RiskEngine's own output byte-identical; no new "exposure"-named field in its return).

**P2-02A-AI-012** (TradeLifecycleEngine no operative Position/Exposure) - verified by: trade_lifecycle.py's confirmed zero changes (Section 6).

**P2-02A-AI-013** (P1-03/P1-03.1/P1-04/P2-01 contracts unchanged) - verified by: Unit U5's full regression re-run.

**P2-02A-AI-014** (no hidden mutation) - verified by: Section 7's file inventory; every change is confined to PositionEngine's own computation (U1) or CanonicalEnforcer's already-existing publication call (U2/U3 sourcing change; no new write path).

**P2-02A-AI-015** (no NaN/infinite Exposure) - verified by: Unit U1's Runtime Test; the explicit FLAT guard (Section 7.1) and the bounded, already-validated Quantity/last_price inputs (finite by construction, per P1-03.1's quantity validation) together preclude NaN or infinite results.

**P2-02A-AI-016** (identical default/published shape) - verified by: Unit U2's Runtime Test (six keys, both pre- and post-tick).

---

## 15. Migration Strategy

No data migration is required. This is a pre-release development branch (run-engine-consolidation-safety) with no external persisted state; CanonicalState is reconstructed fresh at every process start (Architecture Section 22, AD-009). No migration script, schema version flag, or converter is specified or required.

---

## 16. Backward Compatibility

No alias field is introduced for the renamed "exposure" to "risk_allocation_factor" top-level key (AD-009, Section 17.4 of the Architecture). Repository-wide search (re-confirmed unchanged since the FRA/CGA) found exactly one consumer of the old key besides CanonicalState's own internals - the confirmed-inactive PositionSizingEngine - so the rename has zero active-runtime consumer impact. Every already-certified P1-03/P1-03.1/P1-04/P2-01 consumer contract (StrategySelector, Executor, PnLEngine's entry_basis, the RUNTIME_FAILURE_EVENT machinery, the Scale-In/Partial-Close/Full-Close transitions) is preserved exactly, verified by Unit U5's regression re-run, with zero code change to trade_lifecycle.py, strategy.py, execution/executor.py, or pnl.py (Section 6).

---

## 17. Default-State and Invalid-State Rules

**Default-State Rule**: CanonicalState's pre-first-tick Position default and PositionEngine's own `__init__` instance values are defined to be identical (Section 8.2's FLAT column), for every one of the six fields, closing Capability 5 completely (Unit U2).

**Invalid-State Rule**: Exposure is defined for every reachable Position state without exception. Quantity and last_price are already guaranteed finite and non-negative by the existing, certified quantity-validation machinery (TradeLifecycleEngine's `_validate_execution_quantity`, P1-03.1) before they ever reach PositionEngine's Exposure computation; combined with the explicit quantity-equals-0.0 guard (Section 7.1), no input to the Exposure formula can produce NaN or an infinite result (Invariant P2-02A-AI-015). No new invalid-state handling, exception type, or validation function is introduced; Exposure's computation reuses the already-validated inputs it is given.

---

## 18. Acceptance Criteria

**P2-02A-AC-001** - `PositionEngine.snapshot()` returns exactly six keys (position, side, quantity, entry_price, last_price, exposure) for every reachable Position state.

**P2-02A-AC-002** - Exposure equals 0.0 exactly whenever quantity equals 0.0, for every code path, with no exception and no NaN.

**P2-02A-AC-003** - Exposure equals side factor times quantity times last_price for every non-FLAT Position state, where side factor is +1.0 for LONG and -1.0 for SHORT.

**P2-02A-AC-004** - `CanonicalState()`'s default Position dict and any tick's published Position dict have identical key sets and types.

**P2-02A-AC-005** - `CanonicalState.state` contains no top-level key named "exposure"; it contains "risk_allocation_factor" instead, with unchanged values relative to the pre-Unit-U2 "exposure" key.

**P2-02A-AC-006** - `RunLoop.step()`'s `position_pre` is sourced exclusively from `CanonicalState.get()["position"]`; no consumer reads `PositionEngine`'s live instance attributes externally.

**P2-02A-AC-007** - `RiskEngine.check()` reads `position.get("exposure", 0.0)` without raising, and its own returned dict is unchanged in shape and value relative to the pre-Unit-U4 implementation for identical inputs.

**P2-02A-AC-008** - Every already-certified P1-03/P1-03.1/P1-04/P2-01 scenario (FLAT/Open/Scale-In/Partial-Close/Full-Close, LONG and SHORT, rejected transitions) produces identical results after this unit's full implementation.

**P2-02A-AC-009** - `python -m compileall run_engine` passes with no errors after all four units are implemented.

**P2-02A-AC-010** - No runtime file outside Section 6's four-file change list is modified. Certification documents, implementation reports, verification artifacts, and other governance documents generated after implementation are excluded from this restriction.

Implementation is accepted only if all ten criteria pass and every Unit's own Compile, Import, and Runtime Criteria (Section 13) pass in sequence.

---

## 19. FRA Traceability

| Requirement | Governing Unit(s) |
|---|---|
| FR-001 | U1, U2 |
| FR-002 | U1 |
| FR-003 | U2 |
| FR-004 | U1 |
| FR-005 | U1, U2 |
| FR-006 | U2 |
| FR-007 | U2, U3 |
| FR-008 | U3 |
| FR-009 | none required (TradeLifecycleEngine unchanged, Section 6) |
| FR-010 | U4 |
| FR-011 | U4 |
| FR-012 | U3 |
| FR-013 | U5 |
| FR-014 | U5 |
| FR-015 | U1 |
| FR-016 | U3 |
| FR-017 | U5 |
| FR-018 | U1 |
| FR-019 | U3 |
| FR-020 | U2, U3 |

All twenty FRA requirements are governed by at least one Implementation Unit or explicitly confirmed as requiring no change (FR-009).

---

## 20. SDA Conformance

All thirteen SDA dependencies, already confirmed satisfied or resolved-as-not-triggered by the Architecture (Architecture Section 26), are operationalized without exception by Section 12's Implementation Sequence Justification, which restates each governing dependency at file-level implementation precision. No dependency is left unaddressed; P2-02A-DEP-013 (external instrument-metadata capability) remains resolved as not triggered, since Unit U1's formula (Section 7.1) uses no instrument metadata of any kind.

---

## 21. CGA Coverage

All seventeen CGA capabilities, already mapped to their closing Architecture Decision (Architecture Section 27), are further mapped here to the closing Implementation Unit:

| Capability | Closing Unit |
|---|---|
| 1. Position Semantics | U1 |
| 2. Position Representation | U3 |
| 3. Position Ownership | U3 |
| 4. Position Publication | none required (already satisfied) |
| 5. Canonical Position Shape | U2 |
| 6. Position-derived Exposure | U1 |
| 7. Exposure Semantics | U1 |
| 8. Exposure Derivation | U1 |
| 9. Exposure Storage / Projection | U1 |
| 10. Runtime Consumer Access | U3 |
| 11. Pre-Trade Snapshot | U3 |
| 12. Post-Trade Snapshot | none required (already satisfied) |
| 13. Canonical Read Path | U3 |
| 14. RiskEngine Consumption | U4 |
| 15. Exposure Naming Separation | U2 |
| 16. Compatibility Constraints | U5 (verification, not construction) |
| 17. Validation Infrastructure | not applicable (out of scope, unchanged) |

---

## 22. Architecture Conformance

Every one of the nine Architecture Decisions is operationalized by exactly one or more Implementation Units, with no reinterpretation: AD-001/AD-002/AD-003 by U1; AD-004 by U1 and U2 jointly; AD-005/AD-006 by U3; AD-007 by U2 (and the delegated detail resolved in Section 7.5); AD-008 by U4; AD-009 by U5. Every one of the sixteen Architecture Invariants is restated with its concrete verification point in Section 14. No Architecture Decision's Scope Boundaries field (Architecture Section 23) is exceeded by any Implementation Unit in Section 11.

---

## 23. Internal Consistency Review

**Terminology consistency** - "Position," "Exposure," "risk_allocation_factor," "Authoritative Owner," "Computational Authority," and "Writer-on-Behalf-Of" are used exactly as defined in the Architecture throughout this document; no new term is introduced.

**No new architecture decision** - every technical choice in Sections 7 through 18 traces to a specific AD or to an explicitly delegated mechanical detail (Section 7.5, delegated by AD-007's own Consequences field); no choice in this document contradicts, extends, or reinterprets any AD.

**File-inventory consistency** - Section 6's four changed files and eleven unchanged files/paths are referenced identically throughout Sections 7 through 22; no section names a fifth changed file or a twelfth unchanged one.

**Sequencing consistency** - Section 11's per-unit Preconditions and Section 12's Implementation Sequence Justification agree exactly: U1 before U2 before U3; U4 after U1 (hard) and recommended after U3 (soft); U5 last.

**Traceability completeness** - Section 19 confirms all twenty FRA requirements; Section 20 confirms all thirteen SDA dependencies; Section 21 confirms all seventeen CGA capabilities; Section 22 confirms all nine Architecture Decisions and sixteen Architecture Invariants; cross-checked against Sections 7 through 18 during drafting.

**Acceptance Criteria consistency** - all ten Acceptance Criteria (Section 18) are each traceable to at least one Implementation Unit's own Postconditions or Validation field (Section 11); none introduces a new, unvalidated requirement.

**No runtime file modified by this document** - this document is prose only; Section 7's code excerpts are specification text, not applied changes; no file under run_engine/ is altered by the creation of this document, confirmed independently in Section "Prufungen" of the closing report.

Status: Internal Consistency Review PASS.
