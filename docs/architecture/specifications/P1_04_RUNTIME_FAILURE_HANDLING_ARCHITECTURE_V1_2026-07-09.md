# Document Metadata

Document Class: Architecture Specification
Document ID: P1-04-ARCH
Version: V1.0
Status: Draft
Date: 2026-07-09
Project: Trading-Bot Scientific Runtime
Subsystem: Run Engine
Storage Location: docs/architecture/specifications/
Filename: P1_04_RUNTIME_FAILURE_HANDLING_ARCHITECTURE_V1_2026-07-09.md

Depends On:
- docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md
- docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md
- docs/architecture/analysis/P1_04_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-09.md
- docs/architecture/analysis/P1_04_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-09.md
- docs/architecture/analysis/P1_04_CAPABILITY_GAP_ANALYSIS_V1_2026-07-09.md

Referenced By:
- P1_04A_RUNTIME_FAILURE_HANDLING_SPECIFICATION

---

# P1-04 Runtime Failure Handling — Architecture

## 1. Metadata

See Document Metadata block above.

---

## 2. Objective

The Capability Gap Analysis identified four implementation-relevant gaps (C-1, C-2, C-3, C-6) required to satisfy ADR-011 ("Runtime Failure Handling"), and one of them (C-3) was explicitly blocked on an architectural decision this document is required to make.

The objective of this document is to define the complete architecture for Runtime Failure Handling: how a rejected transition flows through the runtime, which component is responsible for suppressing which side effect, and — as explicitly required — to resolve the one open architectural question identified by the Capability Gap Analysis:

> Should `PositionEngine` update `last_price` after a rejected execution, or remain completely immutable?

This document selects exactly one answer, justifies it scientifically against the approved baseline, and defines the resulting component interactions precisely enough for direct translation into a specification.

---

## 3. Scope

In scope: the runtime's handling of a rejected transition (`LifecycleEvent.event_type == "RUNTIME_FAILURE_EVENT"`) as it passes through `RunLoop`, `PositionEngine`, `PnLEngine`, and `PerformanceEngine`.

Out of scope, per the Functional Requirement Analysis's Non-Goals and the Architecture Technical Debt Register: Phase 2 ownership consolidation (TD-001, TD-002), the broader lifecycle-outcome redesign of `PerformanceEngine` (TD-004), an automated test-suite buildout (TD-005), multi-asset support, portfolio accounting, and funding/fees/slippage modelling. No change is proposed to `TradeLifecycleEngine`, `CanonicalState`, `CanonicalEnforcer`, `RiskEngine`, `StateEngine`, `RegimeClassifier`, `StrategySelector`, or `Executor`.

---

## 4. Architectural Principles

The following principles, already established by the baseline, govern every decision in this document and are not renegotiated:

- CanonicalState remains the Single Source of Truth for active runtime state (ADR-001).
- Every runtime information object retains exactly one Authoritative Owner (ADR-001, Rule OM-001).
- `PnLEngine` remains the exclusive Computational Authority for financial accounting (ADR-005).
- `PositionEngine` remains the exclusive Computational Authority for Position (ADR-004).
- `RunLoop` remains the deterministic orchestration layer only; it does not acquire domain-decision responsibility belonging to another component (Principle 1 — Single Responsibility; Verified Active Runtime Modules: RunLoop's responsibility is "deterministic orchestration, execution sequencing, runtime coordination").
- Runtime evolves exclusively through explicit Runtime Events (ADR-002); a rejected transition is itself already a first-class Runtime Event (`RUNTIME_FAILURE_EVENT`), not an absence of one.
- Deterministic execution ordering (ADR-010) is preserved: every pipeline stage executes on every tick; a rejection changes a stage's *effect*, never whether the stage runs.
- Architectural simplicity is an engineering objective; equivalent capability is always implemented with the simpler architecture (Architectural Philosophy).

---

## 5. Runtime Information Flow

```text
Market Observation
        │
        ▼
StateEngine ──► Normalized State
        │
        ▼
RegimeClassifier ──► Regime
        │
        ▼
StrategySelector ──► Decision
        │
        ▼
Executor ──► Execution
        │
        ▼
TradeLifecycleEngine ──► LifecycleEvent (trade_event)
        │                       │
        │                       ├── event_type == RUNTIME_FAILURE_EVENT ?
        │                       │
        ▼                       ▼
PositionEngine            (rejection classification — already resolved
        │                  upstream by TradeLifecycleEngine; no
        ▼                  downstream component re-derives it)
PnLEngine
        │
        ▼
PerformanceEngine
        │
        ▼
CanonicalState Publication
```

The rejection classification is produced exactly once, by `TradeLifecycleEngine`, as part of `trade_event.event_type`. Per Principle IF-001 ("Information is produced exactly once") and IF-002 ("Information is never reconstructed downstream"), no downstream component re-derives whether a transition was rejected — every consumer that needs this fact receives `trade_event` itself and reads `event_type` directly.

---

## 6. Ownership Matrix

No new Authoritative Owner, Computational Authority, or canonical information object is introduced. This table restates the relevant rows from the Runtime Ownership Matrix (Architecture Baseline) and adds the two derived properties this document must clarify:

| Runtime Information | Authoritative Owner | Computational Authority | Notes |
|---|---|---|---|
| Runtime Failure Event | TradeLifecycleEngine | TradeLifecycleEngine | Unchanged. |
| Position (Side, Quantity, Average Entry Price) | CanonicalState | PositionEngine | Unchanged; protected from rejection per ADR-011. |
| Position mark price (`last_price`) | CanonicalState | PositionEngine | **Clarified by this document (Section 11): not one of ADR-004's four canonical Position properties; tracks market observation independent of trade outcome.** |
| Realized PnL | CanonicalState | PnLEngine | Unchanged; protected from rejection per ADR-011. |
| Performance Metrics | CanonicalState | PerformanceEngine | Unchanged; protected from rejection per ADR-011 within the scope defined in Section 13. |

---

## 7. Runtime Sequence

The ADR-010 sequence is unchanged and is preserved exactly as approved:

1. Runtime Tick Acquisition
2. State Acquisition and Normalization
3. Regime Classification
4. Strategy Selection
5. Execution Decision Generation
6. Executor Event Generation
7. TradeLifecycle Update
8. Position Update
9. Financial Accounting
10. Risk Evaluation
11. Performance Evaluation
12. Tick-Complete CanonicalState Publication

Runtime Failure Handling does not add, remove, or reorder any stage. Steps 8, 9, and 11 (Position Update, Financial Accounting, Performance Evaluation) each execute unconditionally on every tick; when `trade_event` is a `RUNTIME_FAILURE_EVENT`, each of these three stages produces its already-defined no-op effect (Sections 11–13) rather than being skipped. This preserves the Tick Completion Contract ("Lifecycle updated, Position updated, Financial state updated, Risk evaluated, Performance evaluated, CanonicalState published" — all six, every tick) and Principle IF-005 ("Every runtime stage produces information for downstream consumers").

---

## 8. Component Responsibilities

- **RunLoop** — orchestrates the fixed sequence; propagates `trade_event` to every consumer whose contract depends on it. RunLoop does **not** decide whether a tick's outcome is valid — that determination was already made, once, by `TradeLifecycleEngine`. RunLoop does not gain new business logic; its only change is threading an already-computed value (`trade_event`) into one additional call site (`PerformanceEngine.update`).
- **PositionEngine** — unchanged responsibility. Continues to project operational Position from `lifecycle_position`, and continues to track `last_price` from the current market observation on every tick (Section 11).
- **PnLEngine** — unchanged responsibility. Remains the sole Computational Authority deciding whether a given `trade_event` produces nonzero realized PnL (Section 12).
- **PerformanceEngine** — responsibility clarified, not redesigned. Continues to evaluate the tick's outcome, but must now recognize `RUNTIME_FAILURE_EVENT` as a non-outcome and not record it (Section 13). This does not adopt the broader lifecycle-outcome redesign tracked as TD-004.

---

## 9. Runtime Failure Processing

When `TradeLifecycleEngine.on_execution()` rejects a proposed transition, it produces exactly one immutable `LifecycleEvent` with `event_type="RUNTIME_FAILURE_EVENT"` and a populated `reason` (already implemented; unchanged by this document). This event is:

1. Appended to `TradeLifecycleEngine.failure_events` (permanent, retrievable via `get_failure_events()`).
2. Appended to the active trade's `events` history, if a trade is active.
3. Returned to `RunLoop` as `trade_event`, exactly as any other lifecycle event.

From this point, every downstream stage receives the same `trade_event` object and independently applies its own, already-scoped no-op rule (Sections 11–13). No central "rejection gate" is introduced in `RunLoop`; this is a deliberate architectural choice, justified in Section 9.1.

### 9.1 Justification: Per-Consumer Recognition, Not a Central RunLoop Gate

Two designs were available (Capability Gap Analysis Risk R-001 / Functional Requirement Analysis RQ-002):

**(A) Centralized gate** — `RunLoop` checks `trade_event.event_type` once and conditionally skips calling `PerformanceEngine.update()` (and/or `PnLEngine.update()`) for that tick.

**(B) Per-consumer recognition** — every consumer is always called, on every tick, and independently applies its own no-op rule when it recognizes a rejection.

This document selects **(B)**, for three reasons grounded directly in the baseline:

1. **ADR-002 (Event-Driven Runtime Evolution)** defines a layered event hierarchy in which "each layer consumes the event output of the immediately preceding layer as its primary transition input." Interpreting and acting on an event is the consuming layer's responsibility, not the orchestrator's. A centralized gate would move domain decision-making (what does this event mean for my output?) out of the owning component and into `RunLoop`, which Principle 1 (Single Responsibility) reserves exclusively for orchestration.
2. **ADR-010's Tick Completion Contract** requires every stage to execute and publish on every tick. Conditionally skipping a stage's invocation risks leaving its output undefined for that tick (e.g., what would `RunLoop` return for `"performance"` in its result dict if `PerformanceEngine.update()` were never called?). Per-consumer recognition keeps every stage's contract — "called every tick, returns a value every tick" — intact; only the *effect* of a rejected tick becomes a no-op.
3. **Precedent already exists in the codebase.** `PnLEngine.update()` already implements exactly this pattern (an internal event-type gate that produces a no-op return without RunLoop's involvement). Extending the same pattern to `PerformanceEngine` is the simpler architecture per the stated Architectural Philosophy ("equivalent architectural capability shall always be implemented using the simpler architecture"), and avoids introducing a second, inconsistent failure-handling mechanism.

`RunLoop`'s only required change is therefore to make `trade_event` available where it is currently missing (as an input to `PerformanceEngine.update()`); it does not gain conditional branching over which stages run.

---

## 10. State Transition Rules

The Lifecycle Transition Table (ADR-009) is unchanged:

| Current State | Event | Next State |
|---|---|---|
| No Position | Trade Opened | Open |
| Open | Scale-In | Open |
| Open | Partial Close | Open |
| Open | Full Close | Closed |
| Closed | Trade Opened | Open |

This document adds the following rule, which is new only in that it is now made explicit rather than incidental:

| Current State | Event | Next State | Side Effects |
|---|---|---|---|
| Any | Runtime Failure | **Unchanged** | Exactly one `RUNTIME_FAILURE_EVENT` recorded; `Position.side`/`quantity`/`entry_price` unchanged; `Position.last_price` updates from market observation (Section 11); `PnLEngine` produces `0.0` and does not mutate `last_realized_pnl` (Section 12); `PerformanceEngine` does not mutate `stats` (Section 13). |

All other transitions not present in the table (per ADR-009) remain invalid and continue to generate a Runtime Failure Event.

---

## 11. Interaction with PositionEngine

**Architectural Decision:** `PositionEngine.last_price` SHALL continue to update from the current tick's market observation (`state["price"]`) on every tick, **regardless of whether the tick's transition was accepted or rejected.** `Position.side`, `Position.quantity`, and `Position.entry_price` remain, as already implemented, fully protected from mutation by a rejected transition.

This is a selection between exactly two candidate architectures, both already identified as defensible by the Functional Requirement Analysis (RQ-001) and the Scientific Dependency Analysis (D-005):

- **Option A (selected): mark price tracks the market unconditionally.**
- **Option B (rejected): mark price freezes on any rejected transition.**

### 11.1 Scientific Justification

**ADR-004 defines Position as exactly four properties: Side, Quantity, Average Entry Price, Current Exposure.** `last_price` is not one of these four. It is the computational input `PositionEngine` uses to derive `Current Exposure` — it is not itself a canonical Position property, and therefore ADR-011's prohibition on rejected transitions "modifying Position" governs the four defined properties, not every internal field of the `PositionEngine` implementation. Of the four, only Side, Quantity, and Average Entry Price are trade-outcome-derived — these are exactly the three fields a rejected transition could, if implemented incorrectly, corrupt, and they are exactly the three this architecture protects.

**"Current Exposure" is explicitly named "current."** Exposure is derived from Position and must reflect present market conditions to remain meaningful to `RiskEngine`, which consumes Position-derived Exposure at its assigned execution stage (ADR-007). If `last_price` froze whenever a transition happened to be rejected, `Current Exposure` would silently stop being current for the duration of the freeze — for however many ticks rejections continued to occur — producing a materially stale risk evaluation. This would actively work against ADR-007's requirement that "Risk Evaluation is the deterministic assessment of the **current** runtime state."

**Freezing on rejection would degrade, not improve, determinism.** Invariant AI-005 requires that identical runtime inputs produce identical outputs. Market price is an independent, always-current input (already produced upstream by `StateEngine` in the same tick, before any trade acceptance/rejection is known). Making `last_price` depend on the accept/reject outcome of trade attempts — rather than purely on the sequence of market observations — would introduce path-dependence on trading *history* into what should be a pure function of *market data*, which is a strictly worse determinism property than the current behavior.

**ADR-011's own stated rationale is about protected trade facts, not passive market observation.** ADR-011's Scientific Justification reads: "Failed execution attempts are historical observations... Operational runtime state shall reflect only successfully completed runtime transitions." This is a statement about the runtime's record of *what it did* (Side, Quantity, Average Entry Price — the trade-derived identity of the Position) — not about the runtime's observation of *where the market currently is*, which was never something a rejected order attempted to change in the first place.

**Consequence for the Ownership Matrix:** this document formally splits Position's fields into (a) trade-outcome-derived identity — Side, Quantity, Average Entry Price — protected by ADR-011 from rejection, and (b) market-observation-derived mark input — `last_price`, feeding the derived Current Exposure property — which tracks the market unconditionally. This is recorded in Section 6 and constitutes this document's binding interpretation of ADR-011 for the one case the Architecture Baseline left unresolved (Rule OM-009 permits this: an interpretive clarification of existing text, not a new Authoritative Owner or new canonical object, does not require an Architecture Evolution Review).

### 11.2 Resulting Contract

`PositionEngine.update_post_trade()` requires **no code change**. Its current behavior — updating `last_price` unconditionally while leaving `side`/`quantity`/`entry_price` untouched when the lifecycle position is unchanged — already implements the architecture selected above. This gap (Capability Gap Analysis C-3) is closed by ratification, not by code modification.

---

## 12. Interaction with PnLEngine

**Architectural Decision:** `PnLEngine.update()`'s existing event-type gate — `if event_type not in {"TRADE_CLOSED", "PARTIAL_CLOSE"}: return 0.0` — is hereby formally ratified as the explicit, binding contract satisfying ADR-011's financial non-mutation requirement. `PnLEngine` remains the sole Computational Authority responsible for this decision; no redundant guard is introduced elsewhere.

### 12.1 Justification

Introducing a second, independent check (for example, a `RunLoop`-level guard that also inspects `trade_event.event_type` before calling `PnLEngine`) would duplicate a decision that already has exactly one owner, reintroducing the kind of fragmented authority AD-002 diagnosed as the dominant architectural weakness of the pre-consolidation runtime. `PnLEngine` is already, by ADR-005, the exclusive Computational Authority for financial accounting; formalizing its existing gate as the single point of truth — rather than adding a parallel check — is the simpler architecture and preserves unique ownership (Rule OM-001).

### 12.2 Resulting Contract

`PnLEngine.update()` requires **no functional code change**. This gap (Capability Gap Analysis C-6) is closed by formal specification and test coverage (deferred to the next document), not by new production logic. `Realized PnL`, `Unrealized PnL`, and `Equity` remain provably unchanged by any `trade_event` whose `event_type` is not `TRADE_CLOSED` or `PARTIAL_CLOSE` — which includes, but is not specific to, `RUNTIME_FAILURE_EVENT`.

---

## 13. Interaction with PerformanceEngine

**Architectural Decision:** `PerformanceEngine.update()` SHALL receive `trade_event` as an explicit input and SHALL NOT mutate `stats` for a tick whose `trade_event.event_type == "RUNTIME_FAILURE_EVENT"`.

### 13.1 Justification

This is the one genuine behavioral gap identified by the Capability Gap Analysis (C-2), empirically confirmed: a rejected `BUY` was observed to increment `stats["BUY"]["trades"]` identically to an accepted trade. `PerformanceEngine` currently has no way to distinguish the two, because it never receives the lifecycle outcome — only `decision`, `pnl`, and `regime`. Since `trade_event` is already computed by `RunLoop` at the point `PerformanceEngine.update()` is called, closing this gap requires only propagating an already-existing value, consistent with D-004 (Scientific Dependency Analysis) and Principle IF-002 (no downstream reconstruction of already-available information).

### 13.2 Explicit Scope Boundary

This document deliberately does **not** adopt the broader ADR-008/AC-008 lifecycle-outcome redesign tracked as TD-004 (Phase 3). Specifically:

- `PerformanceEngine` continues to be invoked once per tick and continues to key statistics by `decision["action"]`, unchanged.
- A tick whose `decision["action"] == "HOLD"` (no trade attempted at all) continues to be counted exactly as it is today. This document does not change that behavior.
- Only the narrow case — a `trade_event` that is specifically a `RUNTIME_FAILURE_EVENT` — is suppressed.

This is the minimal change that satisfies ADR-011 without pre-empting the Phase 3 redesign, consistent with the Functional Requirement Analysis's Non-Goals (Section 6) and Risk RQ-003 (Scientific Dependency Analysis), which remains open and unaffected by this document.

### 13.3 Resulting Contract

`PerformanceEngine.update()`'s signature gains one parameter carrying `trade_event`. `RunLoop`'s call site is updated to pass it. This is a breaking interface change, structurally identical to the `PnLEngine.update()` signature change certified safe in P1-03.1 (Section 16, Risk R-003 carried forward from the Capability Gap Analysis).

---

## 14. Invariants

**INV-P1-04-001** — A `RUNTIME_FAILURE_EVENT` never mutates `Position.side`, `Position.quantity`, or `Position.entry_price`.

**INV-P1-04-002** — `Position.last_price` updates from the current tick's market observation on every tick, independent of trade acceptance or rejection.

**INV-P1-04-003** — A `RUNTIME_FAILURE_EVENT` never mutates `PnLEngine.last_realized_pnl`, `CanonicalState.state["pnl"]`, or `CanonicalState.state["equity"]`.

**INV-P1-04-004** — A `RUNTIME_FAILURE_EVENT` never mutates `PerformanceEngine.stats`.

**INV-P1-04-005** — A `RUNTIME_FAILURE_EVENT` never terminates, creates, or otherwise mutates `TradeLifecycleEngine.active_trade`, beyond appending the event to its history when a trade is active.

**INV-P1-04-006** — Every rejected transition produces exactly one immutable `RUNTIME_FAILURE_EVENT`, permanently retrievable.

**INV-P1-04-007** — `RunLoop` invokes every pipeline stage on every tick regardless of trade acceptance or rejection; rejection changes a stage's effect, never whether the stage executes.

---

## 15. Acceptance Criteria

Restated and finalized from the Functional Requirement Analysis, now resolved against this architecture:

**P1-04-AC-001** — No `RUNTIME_FAILURE_EVENT` changes `Position.side`, `Position.quantity`, or `Position.entry_price` from pre-rejection values. *(No code change required — already satisfied.)*

**P1-04-AC-002** — `Position.last_price` updates on every tick, including rejected ticks, from the current market observation. *(Ratified; ADR-011 does not classify `last_price` as a protected Position property — see Section 11.)*

**P1-04-AC-003** — No `RUNTIME_FAILURE_EVENT` changes `PnLEngine.last_realized_pnl`, `CanonicalState.state["pnl"]`, or `CanonicalState.state["equity"]`. *(No code change required — already satisfied by `PnLEngine`'s existing gate, now formally ratified.)*

**P1-04-AC-004** — No `RUNTIME_FAILURE_EVENT` increments `PerformanceEngine.stats[action]["trades"]` or alters `stats[action]["pnl"]`/`stats[action]["winrate"]`. *(Requires the `PerformanceEngine.update()` change in Section 13.)*

**P1-04-AC-005** — No `RUNTIME_FAILURE_EVENT` terminates, creates, or mutates `TradeLifecycleEngine.active_trade` beyond history append. *(No code change required — already satisfied.)*

**P1-04-AC-006** — Every rejected transition produces exactly one `RUNTIME_FAILURE_EVENT`, retrievable via `get_failure_events()`, with a non-empty `reason`. *(No code change required — already satisfied; verification only.)*

**P1-04-AC-007** — Repeated replay of an identical rejected transition against identical prior state produces identical `RUNTIME_FAILURE_EVENT` field values across runs. *(No code change required — already satisfied; verification only.)*

**P1-04-AC-008** — `python -m compileall run_engine/core` passes with no errors after implementation.

**P1-04-AC-009 (new)** — `RunLoop.step()` calls `PositionEngine.update_post_trade()`, `PnLEngine.update()`, and `PerformanceEngine.update()` exactly once each on every tick, including rejected ticks (verifies INV-P1-04-007 / the Tick Completion Contract).

---

## 16. Risks

**R-001 (resolved by this document)** — The gate-vs-guard design choice (Functional Requirement Analysis RQ-002; Capability Gap Analysis R-001) is resolved: per-consumer recognition (Section 9.1). No further architectural decision is required on this point.

**R-002 (resolved by this document)** — The mark-price policy decision (Functional Requirement Analysis RQ-001; Scientific Dependency Analysis D-005) is resolved: Option A, mark price tracks the market unconditionally (Section 11). No further architectural decision is required on this point.

**R-003 (carried forward)** — Changing `PerformanceEngine.update()`'s signature is a breaking interface change. Before implementation, every call site in the live codebase must be re-confirmed (as was done for `PnLEngine.update()` in P1-03.1) to ensure `run_engine/core/loop.py` remains the sole caller.

**R-004 (carried forward)** — Verification of AC-004 through AC-009 will be manual/interactive, since no automated regression suite exists for `run_engine/core` (TD-005). This does not block P1-04; it is the same methodology already used and certified sufficient in P1-03 and P1-03.1.

---

## 17. Open Questions

No open architectural questions remain for the scope defined in Section 3. The two questions this document was required to resolve (mark-price policy, gate-vs-guard placement) are both resolved in Sections 9.1 and 11.

The following are explicitly deferred, not open within P1-04's scope:

- The exact parameter name, position, and type annotation for `PerformanceEngine.update()`'s new input is a specification-level detail, deferred to `P1_04A_RUNTIME_FAILURE_HANDLING_SPECIFICATION_V1_2026-07-09.md`.
- Scientific Dependency Analysis RQ-003 (risk that the narrow C-2 change requires rework when TD-004 is implemented in Phase 3) remains an accepted, tracked risk — not resolved here, and not required to be resolved before P1-04 proceeds.

---

## 18. Next Document

The next document is `P1_04A_RUNTIME_FAILURE_HANDLING_SPECIFICATION_V1_2026-07-09.md`.
