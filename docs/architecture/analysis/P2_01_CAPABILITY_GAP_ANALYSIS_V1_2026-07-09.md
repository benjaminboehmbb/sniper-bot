# Document Metadata

Document Class: Capability Gap Analysis
Document ID: P2-01-CGA
Version: V1.0
Status: Draft
Date: 2026-07-09
Project: Trading-Bot Scientific Runtime
Subsystem: Run Engine
Storage Location: docs/architecture/analysis/
Filename: P2_01_CAPABILITY_GAP_ANALYSIS_V1_2026-07-09.md

Depends On:
- docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md
- docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md
- docs/architecture/analysis/P2_01_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-09.md
- docs/architecture/analysis/P2_01_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-09.md
- docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md

Referenced By:
- P2_01_ARCHITECTURE_V1_2026-07-09.md
- P2_01_SPECIFICATION_V1_2026-07-09.md

---

# P2-01 Capability Gap Analysis

## 1. Metadata

See Document Metadata block above.

---

## 2. Objective

The Scientific Dependency Analysis certified that all five candidate capabilities underlying P2-01's four functional requirements already exist, and that P2-01 may proceed directly to Capability Gap Analysis. That document's Risk R-001 required this document to actually perform the row-by-row Ownership Matrix verification pass (P2-01-FR-001), rather than describe it abstractly.

This document performs that audit against the full 22-row Runtime Ownership Matrix (Architecture Baseline), reports every conformance result, and localizes each confirmed gap to specific files. It also reports findings surfaced by the audit that were not anticipated by the original Functional Requirement Analysis, and explicitly dispositions each one rather than silently expanding or silently dropping them.

---

## 3. Current Capability Baseline

Direct inspection of `run_engine/core/{loop,canonical_state,canonical_enforcer,state,regime,strategy,execution/executor,risk,position,pnl,trade_lifecycle,performance}.py` against the Runtime Ownership Matrix confirms the following already conform correctly:

- **Runtime Tick** — `RunLoop` computes and writes it (`self.cstate.update_tick(...)`); matches Matrix (RunLoop owns/computes/writes).
- **Execution Event** — `Executor.execute()` computes it; `TradeLifecycleEngine.on_execution()` consumes and absorbs it into lifecycle history; matches Matrix.
- **Trade Identifier, Lifecycle State, Entry Facts, Exit Facts, Lifecycle History, Runtime Failure Event** — all exclusively owned, computed, and written by `TradeLifecycleEngine`; matches Matrix (previously certified in P1-02/P1-03/P1-04).
- **Position** — `PositionEngine` computes it; published to `CanonicalState` via `CanonicalEnforcer.apply_position()`; matches Matrix. (The separate, pre-existing question of `PositionEngine.snapshot()` being read directly rather than through `CanonicalState` for certain *consumers* — TD-001 — is a distinct issue, addressed in Section 7.)
- **Realized PnL, Unrealized PnL, Equity** — `PnLEngine` computes them; published via `apply_pnl()`/`apply_equity()`; matches Matrix.
- **Peak Equity** — `CanonicalState.update_equity()` correctly tracks it (`if equity > self.state["peak_equity"]: ...`), fed from `PnLEngine`'s equity output; matches Matrix **for the CanonicalState side**. (A second, independent computation was found elsewhere — Section 7.)
- **Drawdown, Risk Metrics** — `RiskEngine.check()` computes them; published via `apply_risk()`; matches Matrix in terms of publication path.

---

## 4. Required P2-01 Capabilities

Restated from the Functional Requirement Analysis, in capability form:

- **C-1** — Perform the Ownership Matrix verification pass (P2-01-FR-001). *Performed in Section 5.*
- **C-2** — Publish `PerformanceEngine`'s metrics into `CanonicalState` (P2-01-FR-002).
- **C-3** — Record an explicit disposition for Runtime Status (P2-01-FR-003).
- **C-4** — Record an explicit disposition for the Position dual-state pattern (P2-01-FR-004).

---

## 5. Gap Analysis Table

Full row-by-row result of the Ownership Matrix verification pass (C-1):

| Runtime Information | Matrix-Declared Owner | Actual Conformance | Result |
|---|---|---|---|
| Runtime Tick | RunLoop | `RunLoop` writes directly via `cstate.update_tick()` | PASS |
| Normalized Runtime State | CanonicalState | Computed by `StateEngine`, **never written to `CanonicalState`** (only `tick`/`price` subset extracted) | **GAP** |
| Market Regime | CanonicalState | `RunLoop` writes via `cstate.update_regime()` (bypasses `CanonicalEnforcer`, unlike Position/PnL/Equity/Risk) | PASS, with a style inconsistency (Section 7) |
| Strategy Selection | CanonicalState | Computed by `StrategySelector.select()`, **never written to `CanonicalState`** | **GAP** |
| Execution Decision | CanonicalState | Computed by `StrategySelector.decide()`, **never written to `CanonicalState`** | **GAP** |
| Execution Event | TradeLifecycleEngine | `Executor` computes; `TradeLifecycleEngine` absorbs | PASS |
| Trade Identifier | TradeLifecycleEngine | Exclusive | PASS |
| Lifecycle State | TradeLifecycleEngine | Exclusive | PASS |
| Entry Facts | TradeLifecycleEngine | Exclusive | PASS |
| Exit Facts | TradeLifecycleEngine | Exclusive | PASS |
| Lifecycle History | TradeLifecycleEngine | Exclusive | PASS |
| Runtime Failure Event | TradeLifecycleEngine | Exclusive | PASS |
| Position | CanonicalState | `PositionEngine` computes; published via `apply_position()` | PASS (see TD-001 caveat, Section 7) |
| Realized PnL | CanonicalState | `PnLEngine` computes; published via `apply_pnl()` | PASS |
| Unrealized PnL | CanonicalState | Not currently computed by any component (no unrealized PnL calculation exists anywhere in `run_engine/core`) | **GAP — capability entirely absent, not just unpublished** |
| Equity | CanonicalState | `PnLEngine` output published via `apply_equity()` | PASS |
| Peak Equity | CanonicalState | `CanonicalState.update_equity()` tracks it correctly from `PnLEngine`'s output | PASS for `CanonicalState`; **duplicate independent computation found in `RiskEngine`** (Section 7) |
| Drawdown | CanonicalState | `RiskEngine` computes from **its own internal `self.peak_equity`**, not from `CanonicalState`'s | **GAP — violates ADR-006/ADR-007/Rule OM-007** (Section 7) |
| Risk Metrics | CanonicalState | `RiskEngine` computes; published via `apply_risk()` | PASS (publication path only; see Drawdown gap) |
| Runtime Status | CanonicalState | Not implemented anywhere | **GAP** (already known, P2-01-FR-003) |
| Performance Metrics | CanonicalState | `PerformanceEngine` computes; **never written to `CanonicalState`** | **GAP** (already known, P2-01-FR-002) |
| Tick-Complete CanonicalState Snapshot | CanonicalState | `RunLoop` returns `self.cstate.get()` each tick, but publication is incremental (mutated progressively through `step()`), not a single atomic publish at Step 12 | PASS for content; **timing model deferred to Phase 3 (ADR-010/P3-01)**, not P2-01 |

**Audit result: 22 rows checked. 15 PASS. 7 GAP.** Three of the seven (Runtime Status, Performance Metrics, Position/TD-001) were already anticipated by the Functional Requirement Analysis. Four (Normalized Runtime State, Strategy Selection, Execution Decision, Unrealized PnL) and one duplicate-computation finding (Drawdown/Peak Equity via `RiskEngine`) were newly surfaced by this audit and were not anticipated by the original FR doc. Each is explicitly dispositioned in Sections 6 and 7.

---

## 6. Implementation-Relevant Gaps

**Gap Cluster A — CanonicalState Publication Completeness (C-2, expanded).**

`PerformanceEngine`'s omission (P2-01-FR-002) is one instance of a broader, structurally identical pattern: three other Matrix rows (Normalized Runtime State, Strategy Selection, Execution Decision) declare `CanonicalState` as Authoritative Owner but are never published there — only `PerformanceEngine`'s omission was anticipated by the original FR doc. Fixing only `PerformanceEngine` while leaving three structurally identical omissions unaddressed would be inconsistent with P2-01's own stated objective ("Validate Ownership Matrix implementation"), since all four gaps have the same shape and the same fix: add a `CanonicalState` field and a `CanonicalEnforcer.apply_*()` method following the already-established four-times-repeated pattern (Section 5, SDA D-002/D-003), then call it from `RunLoop.step()` at the point the value already exists as a local variable.

This is flagged as a **scope recommendation, not a unilateral requirement change** — formally, extending C-2 to cover all four fields exceeds the four functional requirements defined in the Functional Requirement Analysis. This document does not modify that document; the Architecture document must explicitly ratify or reject this expansion (Section 9, Risk R-001).

Target files: `run_engine/core/canonical_state.py`, `run_engine/core/canonical_enforcer.py`, `run_engine/core/loop.py`.

**Gap Cluster B — Runtime Status (C-3).**

Unchanged from the Functional Requirement Analysis: no implementation exists. Requires a disposition decision (implement in P2-01 vs. defer to P2-02) before any code change; no code change is prescribed by this document.

---

## 7. Non-Gaps / Deferred Items

**Position dual-state (C-4, TD-001).** Unchanged disposition question from the Functional Requirement Analysis: `PositionEngine.snapshot()` is read directly by three consumers instead of through `CanonicalState`. Confirmed still present; the FR doc's recommendation (classify as in-scope-for-P2-01 or defer to P2-02A, with rationale) stands unmodified by this audit.

**RiskEngine Peak-Equity duplication and Drawdown computation (new finding).** `RiskEngine.__init__()` initializes `self.last_equity = 100.0` and `self.peak_equity = 100.0`, and `RiskEngine.check()` independently tracks peak equity (`if equity > self.peak_equity: self.peak_equity = equity`) and computes `drawdown = self.peak_equity - equity` from this **separate, internally-tracked value**, rather than reading `CanonicalState.state["peak_equity"]` (which `PnLEngine`'s output already correctly populates via `CanonicalState.update_equity()`). This directly contradicts ADR-006 ("RiskEngine SHALL calculate Drawdown exclusively from canonical financial state") and ADR-007/Rule OM-007 ("RiskEngine owns no runtime information... shall never own... Equity, Peak Equity"). Under the current single-threaded, synchronous `RunLoop.step()` model, both trackers observe an identical equity sequence and so do not currently diverge numerically — but the two hardcoded initial values (`RiskEngine`'s `100.0` and `CanonicalState`'s `100.0`) are an undeclared, silent coupling: if either is ever changed independently, or if `RiskEngine.check()` is ever invoked out of the exact lockstep `RunLoop` currently maintains, the two would silently diverge with no error. This is a real "duplicate ownership" finding matching P2-01's own objective, but its correct destination per the baseline's own sequencing is **P2-03 ("Verify Equity, Peak Equity and Drawdown consistency") and P2-04 ("Verify Risk Metrics ownership. Validate deterministic RiskEngine behaviour")**, not P2-01. Recommended: log as a new Technical Debt Register candidate (proposed `TD-006`) targeting P2-03/P2-04; not modified by this document (register file modification is out of scope for this turn).

**Unrealized PnL — capability entirely absent.** No component in `run_engine/core` computes Unrealized PnL at all (only Realized PnL, on `TRADE_CLOSED`/`PARTIAL_CLOSE`). The Ownership Matrix declares this `PnLEngine`'s responsibility. This is not an ownership-conformance gap in the P2-01 sense (there is no competing owner — the capability simply does not exist yet), so it does not violate "remove duplicate ownership" or "verify Authoritative Owners" as stated. It is out of scope for an ownership-consolidation unit and belongs to a future financial-capability unit (plausibly P2-03, or a dedicated new unit) — recorded here for completeness of the audit trail, not assigned to P2-01.

**Market Regime / Runtime Tick publication style.** `RunLoop` writes `Runtime Tick` and `Market Regime` directly via `CanonicalState.update_tick()`/`update_regime()`, bypassing `CanonicalEnforcer`, while Position/PnL/Equity/Risk are all mediated through `CanonicalEnforcer`. Both fields still end up correctly owned by `CanonicalState` with the correct value — this is a style inconsistency in *how* the Writer-on-Behalf-Of pattern is applied, not an ownership violation. Recorded as a low-priority observation; not a gap requiring action under P2-01's stated objectives.

**TD-002** (unify `_safe_float` implementations) — confirmed still outside P2-01's ownership-focused scope, per the Functional Requirement Analysis's Non-Goals. Unaffected by this audit.

---

## 8. Minimal Implementation Scope

Pending the Architecture document's ratification of the Section 6 scope recommendation, the minimal implementation footprint is:

- `run_engine/core/canonical_state.py` — add storage fields for Normalized Runtime State (or its relevant subset), Strategy Selection, Execution Decision, and Performance Metrics; add corresponding `update_*()` methods following the existing pattern.
- `run_engine/core/canonical_enforcer.py` — add corresponding `apply_*()` methods following the existing four-times-repeated pattern exactly.
- `run_engine/core/loop.py` — call the new `apply_*()` methods at the point each value already exists as a local variable in `step()`; no new computation introduced.

**Not in scope for P2-01 implementation:** `run_engine/core/position.py`, `run_engine/core/pnl.py`, `run_engine/core/risk.py`, `run_engine/core/trade_lifecycle.py`, `run_engine/core/performance.py` (its *output* is published; its *internal* computation is unchanged), `run_engine/core/state.py`, `run_engine/core/regime.py`, `run_engine/core/strategy.py`, `run_engine/core/execution/executor.py`. The `RiskEngine` Peak-Equity/Drawdown duplication finding (Section 7) is explicitly excluded from P2-01's implementation scope and routed to P2-03/P2-04.

---

## 9. Risks

**R-001** — Gap Cluster A (Section 6) recommends expanding C-2 beyond the four functional requirements formally defined in the Functional Requirement Analysis. This document does not have authority to change that document's scope; the Architecture document must explicitly ratify or reject this expansion before it becomes binding. If rejected, only `PerformanceEngine`'s publication (the originally scoped item) proceeds, and the other three publication gaps are logged as a new Technical Debt item instead.

**R-002** — The RiskEngine Peak-Equity duplication (Section 7) is a genuine ADR-006/ADR-007 non-conformance, not merely an omission. Recommending it for P2-03/P2-04 rather than fixing it immediately carries the risk that `RiskEngine`'s drawdown remains technically non-conformant for the duration of Phase 2's early units. This is judged acceptable because no numeric divergence currently exists (Section 7) and the baseline's own sequencing explicitly assigns this territory to P2-03/P2-04, not P2-01.

**R-003 (carried forward)** — FR-003/FR-004's disposition decisions remain open; this document does not resolve them, consistent with the Scientific Dependency Analysis's R-002.

**R-004 (carried forward)** — No automated regression suite exists (TD-005); verification of any Gap Cluster A implementation will be manual/interactive.

---

## 10. Conclusion

The row-by-row Ownership Matrix audit required by P2-01-FR-001 was performed in full (22 of 22 rows). Fifteen rows conform; seven show a gap. Three of the seven were already anticipated (Runtime Status, Performance Metrics, Position/TD-001). Four additional gaps were newly surfaced: three structurally identical `CanonicalState` publication omissions (Normalized Runtime State, Strategy Selection, Execution Decision), recommended for inclusion alongside Performance Metrics in a single "CanonicalState Publication Completeness" implementation cluster; and one genuine duplicate-ownership violation (`RiskEngine`'s independent Peak-Equity/Drawdown computation), which is explicitly routed to P2-03/P2-04 rather than absorbed into P2-01, consistent with the baseline's own unit sequencing and the instruction not to fold unrelated deferred work into this unit.

No capability outside what the Scientific Dependency Analysis already certified as present was required to perform this audit or to implement Gap Cluster A. The audit is complete and the implementation-relevant scope is narrow and file-localized.

---

## 11. Next Document

The next document is `P2_01_ARCHITECTURE_V1_2026-07-09.md`.
