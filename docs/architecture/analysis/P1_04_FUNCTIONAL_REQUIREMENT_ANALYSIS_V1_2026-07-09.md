# Document Metadata

Document Class: Functional Requirement Analysis
Document ID: P1-04-FRA
Version: V1.0
Status: Draft
Date: 2026-07-09
Project: Trading-Bot Scientific Runtime
Subsystem: Run Engine
Storage Location: docs/architecture/analysis/
Filename: P1_04_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-09.md

Depends On:
- docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md
- docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md
- docs/architecture/certification/P1_03_1_FINAL_CERTIFICATION_V1_2026-07-09.md
- docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md

Referenced By:
- P1_04_SCIENTIFIC_DEPENDENCY_ANALYSIS
- P1_04_CAPABILITY_GAP_ANALYSIS
- P1_04_ARCHITECTURE
- P1_04_SPECIFICATION

---

# P1-04 Functional Requirement Analysis

## 1. Metadata

See Document Metadata block above.

---

## 2. Context

P1-03 (certified, commit `16765b2`) implemented Scale-In, Partial Close and Full Close as explicit, quantity-aware lifecycle transitions inside `TradeLifecycleEngine`.

P1-03.1 (certified PASS WITH MINOR FINDINGS, commit `57e24e6`) removed the hidden `execution["entry_price"]` side-channel between `PositionEngine` and `PnLEngine`, replaced it with an explicit `entry_basis` parameter on `PnLEngine.update()`, removed the dead `update_pre_trade()` method, and hardened quantity validation (`TradeLifecycleEngine._safe_float` no longer raises on non-numeric input; non-finite quantities — `nan`, `inf`, `-inf` — are explicitly rejected).

P1-04 continues the approved Phase-1 roadmap defined in `RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md`. The Phase 1 Implementation Units sequence is P1-01 → P1-02 → P1-03 → **P1-04**, and P1-04 is explicitly named **Runtime Failure Handling**, implementing ADR-011.

The Architecture Technical Debt Register (`ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md`) records five open items (TD-001 through TD-005) surfaced by the P1-03.1 certification. All five are scoped to Phase 2, Phase 3, or project-wide work, and none are prerequisites for P1-04. They are not folded into this analysis. One item, TD-004 ("Lifecycle-based Performance Evaluation", target Phase 3), is topically adjacent to a requirement identified below (Section 5, P1-04-FR-002) — this is noted explicitly in Section 8 to prevent unintentional scope merging.

**Documentation note:** `P1_03_1_FINAL_CERTIFICATION_V1_2026-07-09.md` is listed above as a dependency per its filename, but at the time of writing it contains only its own drafting instructions rather than a completed certification statement. The certification content this analysis relies on (verdict: PASS WITH MINOR FINDINGS; no Critical or Major findings; development approved to continue to P1-04) is the verdict actually delivered for commit `57e24e6`. This is a documentation-completeness gap tracked for resolution, not a functional risk for P1-04 (see Section 8, RQ-004).

---

## 3. Functional Problem Statement

**The P1-04 roadmap item was explicitly found in the Implementation Baseline — it was not derived.**

`RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md`, section "Phase 1 Implementation Units", defines:

```
## P1-04

Runtime Failure Handling

Objectives
* Implement ADR-011.
* Ensure rejected transitions never modify CanonicalState.
* Verify immutable Runtime Failure Events.

Primary Validation
* Failure handling validation
* CanonicalState validation
```

ADR-011 ("Runtime Failure Handling") requires that rejected lifecycle transitions never modify Position, Equity, Realized PnL, Unrealized PnL, or Performance, and never terminate a lifecycle; instead each rejected transition must generate exactly one immutable Runtime Failure Event.

Direct inspection and empirical testing of the current runtime (post P1-03.1) against these three objectives shows a partial, not complete, implementation:

**Objective — "Verify immutable Runtime Failure Events": substantially satisfied.**
`TradeLifecycleEngine._failure_event()` already generates a frozen (immutable) `LifecycleEvent` with `event_type="RUNTIME_FAILURE_EVENT"` for four distinct rejection reasons (`INVALID_EXECUTION_QUANTITY`, `NO_ACTIVE_TRADE`, `OVER_CLOSE_QUANTITY`, `UNSUPPORTED_EXECUTION_ACTION`), appends it to the permanent `failure_events` list, and additionally attaches it to the active trade's event history when one exists. This objective mainly requires formal verification, not new implementation.

**Objective — "Ensure rejected transitions never modify CanonicalState": not yet satisfied.**
Empirical verification (open LONG 1 @ 100, then send a rejected `BUY` with `quantity=nan` @ 250) shows:

- `Position.side`, `Position.quantity`, `Position.entry_price` are correctly left unmodified by the rejection. This part of the objective holds.
- `Position.last_price` **is** updated by the rejected transition (observed change: `100.0 → 250.0`), and this change propagates into `CanonicalState` via `CanonicalEnforcer.apply_position()`. Whether `last_price` (a mark-price field) is covered by ADR-011's "never modify Position" is not resolved by the baseline: ADR-004 defines Position as exactly four properties — Side, Quantity, Average Entry Price, Current Exposure — and does not classify mark price as one of them. This is a genuine open question, not a pre-answered one (see Section 8, RQ-001).
- `PnLEngine.last_realized_pnl`, `CanonicalState.state["pnl"]`, and `CanonicalState.state["equity"]` are numerically unaffected by rejection today, but only incidentally: a `RUNTIME_FAILURE_EVENT`'s `event_type` is simply not a member of `PnLEngine.update()`'s `{"TRADE_CLOSED", "PARTIAL_CLOSE"}` gate, so it returns `0.0`. There is no explicit, rejection-aware guard at the `RunLoop` orchestration layer — the invariant currently holds by accident of one component's internal filter, not by a documented and independently verifiable contract.
- `PerformanceEngine.stats` **is** modified by a rejected transition. Empirically confirmed: a rejected `BUY` incremented `stats["BUY"]["trades"]` from `1` to `2`, identically to how an accepted trade is counted, and recomputed `pnl`/`winrate` running averages using the rejected tick's `pnl=0.0` as if it were a real outcome. This is a direct, concrete violation of ADR-011's explicit prohibition ("Rejected transitions SHALL never... modify Performance").
- Lifecycle termination is correctly never triggered by a rejected transition (`active_trade` is left untouched by every failure path in `TradeLifecycleEngine`).

**Conclusion:** The functional gap P1-04 must close is that a Runtime Failure Event is not yet treated as a first-class signal by `RunLoop` and `PerformanceEngine`. Financial non-mutation on rejection is currently accidental (a side effect of `PnLEngine`'s event-type filter) rather than an explicit, tested contract, and `PerformanceEngine` has no rejection-awareness at all — it treats every tick, rejected or not, as a countable outcome.

---

## 4. Existing Capabilities

Verified present in the runtime as of P1-03.1 (commit `57e24e6`):

- Explicit execution quantity (`execution["quantity"]`) flows end-to-end through `TradeLifecycleEngine` and `PositionEngine`.
- Lifecycle quantity transitions (`SCALE_IN`, `PARTIAL_CLOSE`, `TRADE_CLOSED`) carry explicit `prior_quantity`, `execution_quantity`, `resulting_quantity`, `quantity_delta`, `closed_quantity`, `remaining_quantity` fields.
- Scale-In: same-direction execution against an active lifecycle increases quantity and recomputes a weighted-average entry price in `PositionEngine`.
- Partial Close: opposite-direction execution below active quantity reduces quantity, keeps the lifecycle open, and realizes PnL for the closed portion.
- Full Close: opposite-direction execution equal to active quantity terminates the lifecycle exactly once and realizes PnL for the full remaining quantity.
- Over-close rejection: opposite-direction execution above active quantity produces an `OVER_CLOSE_QUANTITY` Runtime Failure Event rather than mutating lifecycle state.
- Explicit entry_basis handoff: `RunLoop` passes `position_pre["entry_price"]` directly into `PnLEngine.update(trade_event, entry_basis)`; no hidden `execution["entry_price"]` channel remains.
- Deterministic PnL for realized close events: verified for LONG and SHORT sides, single-stage and two-stage (partial-then-full) closes, with correct weighted-average entry basis carried through Scale-In.
- Quantity validation: `TradeLifecycleEngine._safe_float` never raises (returns `nan` on unparseable input instead of throwing); `_validate_execution_quantity` rejects non-finite (`nan`, `inf`, `-inf`), zero, and negative quantities via `RUNTIME_FAILURE_EVENT`.

---

## 5. Required Functional Capabilities for P1-04

**P1-04-FR-001 — Explicit Runtime-Failure Gate in RunLoop**
`RunLoop.step()` must explicitly recognize `trade_event.event_type == "RUNTIME_FAILURE_EVENT"` as a distinct tick outcome, rather than relying on incidental zero-valued side effects propagating harmlessly through downstream stages.

**P1-04-FR-002 — Performance Non-Mutation on Rejection**
`PerformanceEngine` must not record a trade/decision outcome (must not increment `trades`, must not update the running `pnl`/`winrate` averages) for a tick whose `trade_event` is a `RUNTIME_FAILURE_EVENT`.

**P1-04-FR-003 — Position Mark-Price Update Policy on Rejection**
The architecture must explicitly decide, and `PositionEngine` must consistently implement, whether `last_price` (mark price) is permitted to update on a rejected transition. Two outcomes are both architecturally defensible given the current baseline text and must be adjudicated, not assumed: (a) mark price tracks the market regardless of trade outcome, since it is not one of ADR-004's four canonical Position properties; or (b) mark price freezes on rejection, matching a literal reading of "never modify Position."

**P1-04-FR-004 — Runtime Failure Event Traceability Verification**
Confirm, and formalize with explicit test coverage, that every rejected transition produces exactly one immutable `RUNTIME_FAILURE_EVENT`, retrievable via `TradeLifecycleEngine.get_failure_events()`, and attached to the active trade's event history when one exists — for each of the four existing rejection reasons (`INVALID_EXECUTION_QUANTITY`, `NO_ACTIVE_TRADE`, `OVER_CLOSE_QUANTITY`, `UNSUPPORTED_EXECUTION_ACTION`).

**P1-04-FR-005 — Deterministic Rejection Replay**
Identical inputs that produce a rejection (same action, quantity, price, tick, and pre-rejection runtime state) must deterministically produce an identical Runtime Failure Event and identical resulting canonical state on every replay.

**P1-04-FR-006 — Financial State Non-Mutation Contract**
Realized PnL, Unrealized PnL, and Equity must be contractually guaranteed — not merely incidentally true — to remain unchanged by a rejected transition, via an explicit guard (at `RunLoop` or at `PnLEngine`'s boundary) that survives future modification of either component.

---

## 6. Non-Goals

P1-04 explicitly excludes:

- P2 ownership consolidation (TD-001: canonical Position source for `PnLEngine`; TD-002: unifying `_safe_float` implementations) — deferred to Phase 2.
- `PerformanceEngine` lifecycle redesign (TD-004: evaluating completed lifecycle outcomes instead of runtime decisions, per ADR-008/AC-008) — deferred to Phase 3, **except** for the narrow rejection-non-mutation requirement in P1-04-FR-002, which is directly required by ADR-011 and does not require adopting the broader lifecycle-outcome redesign.
- Full automated test-suite buildout (TD-005) — out of scope; P1-04 requires only the targeted failure-handling validation described in Section 7.
- Multi-asset support.
- Portfolio accounting.
- Funding/fees/slippage expansion, unless a specific ADR-011 requirement is later found to directly depend on it (none identified at this time).

---

## 7. Acceptance Criteria

**P1-04-AC-001** — No rejected transition (`RUNTIME_FAILURE_EVENT`) changes `Position.side`, `Position.quantity`, or `Position.entry_price` from their pre-rejection values.

**P1-04-AC-002** — The architecture's decision on `Position.last_price` update-on-rejection (P1-04-FR-003) is implemented consistently and verified by a passing test for both an active and a flat position.

**P1-04-AC-003** — No rejected transition changes `PnLEngine.last_realized_pnl`, `CanonicalState.state["pnl"]`, or `CanonicalState.state["equity"]` from their pre-rejection values.

**P1-04-AC-004** — No rejected transition increments `PerformanceEngine.stats[action]["trades"]` or alters `stats[action]["pnl"]` / `stats[action]["winrate"]`.

**P1-04-AC-005** — No rejected transition terminates, creates, or otherwise mutates `TradeLifecycleEngine.active_trade`, beyond appending the Runtime Failure Event to its history when one exists.

**P1-04-AC-006** — Every rejected transition produces exactly one `RUNTIME_FAILURE_EVENT`, retrievable via `get_failure_events()`, with a non-empty `reason` field.

**P1-04-AC-007** — Repeated replay of an identical rejected transition against identical prior state produces identical Runtime Failure Event field values across runs.

**P1-04-AC-008** — `python -m compileall run_engine/core` passes with no errors after implementation.

---

## 8. Risks and Open Questions

**RQ-001** — Is `Position.last_price` within scope of ADR-011's "never modify Position," or is it outside the four ADR-004-defined Position properties and therefore permitted to track market price regardless of trade outcome? The baseline does not resolve this explicitly. P1-04 must make and record this decision (feeds P1-04-FR-003 / P1-04-AC-002).

**RQ-002** — Should the RunLoop-level fix (P1-04-FR-001) be implemented as an explicit early-return/branch in `RunLoop.step()`, or as an independent guard inside each downstream consumer (`PerformanceEngine`, `PnLEngine`)? Both approaches can satisfy the stated acceptance criteria; the choice affects whether future runtime components inherit rejection-safety by default or must each opt in individually. This is a design decision for the forthcoming P1-04 Architecture document, not resolved here.

**RQ-003** — TD-004 anticipates a full lifecycle-based Performance redesign in Phase 3. P1-04-FR-002 makes a narrow, ADR-011-scoped change to `PerformanceEngine` (suppress updates on rejection only) without adopting the broader decision-to-lifecycle-outcome redesign. There is a risk that this narrow change requires rework when TD-004 is eventually implemented; this is an accepted, tracked risk, not a blocker for P1-04.

**RQ-004** — `P1_03_1_FINAL_CERTIFICATION_V1_2026-07-09.md`, listed as a dependency of this document, currently contains only its own drafting instructions rather than a completed certification statement (see Section 2). This analysis relies on the certification verdict actually delivered for commit `57e24e6` (PASS WITH MINOR FINDINGS) rather than on the file's written content. This is a documentation-completeness gap that should be resolved before Final Scientific Certification, but does not block P1-04 functional analysis.

---

## 9. Next Required Document

The next document is `P1_04_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-09.md`.
