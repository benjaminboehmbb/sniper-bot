# Document Metadata

Document Class: Capability Gap Analysis
Document ID: P1-04-CGA
Version: V1.0
Status: Draft
Date: 2026-07-09
Project: Trading-Bot Scientific Runtime
Subsystem: Run Engine
Storage Location: docs/architecture/analysis/
Filename: P1_04_CAPABILITY_GAP_ANALYSIS_V1_2026-07-09.md

Depends On:
- docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md
- docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md
- docs/architecture/analysis/P1_04_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-09.md
- docs/architecture/analysis/P1_04_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-09.md

Referenced By:
- P1_04_ARCHITECTURE
- P1_04_SPECIFICATION

---

# P1-04 Capability Gap Analysis

## 1. Metadata

See Document Metadata block above.

---

## 2. Objective

The Scientific Dependency Analysis certified that all P1-04 functional requirements depend only on capabilities already established through P1-01 through P1-03.1, and that no prerequisite capability is missing. It identified two remaining items — consumer-side interface wiring (D-004) and an explicit mark-price policy decision (D-005) — as P1-04's own scope rather than external blockers.

The objective of this document is to convert that dependency-level conclusion into a precise, file-level gap analysis: for each of the six functional requirements, determine exactly what exists in the current runtime, what is missing, and where the missing behavior must be implemented. This document does not propose interfaces or write specifications; it identifies and localizes gaps only.

---

## 3. Current Capability Baseline

Verified present in the runtime as of commit `57e24e6` (P1-03.1), consistent with Section 4 of the Functional Requirement Analysis and Section 5 (D-001/D-002/D-003) of the Scientific Dependency Analysis:

- **Rejection signal generation** — `TradeLifecycleEngine._failure_event()` produces a `LifecycleEvent` with `event_type="RUNTIME_FAILURE_EVENT"` and a populated `reason` field for four rejection classes: `INVALID_EXECUTION_QUANTITY`, `NO_ACTIVE_TRADE`, `OVER_CLOSE_QUANTITY`, `UNSUPPORTED_EXECUTION_ACTION`.
- **Rejection immutability & retrieval** — `LifecycleEvent` is a frozen dataclass; instances are appended to `TradeLifecycleEngine.failure_events` and, when applicable, to the active trade's `events` history; retrievable via `get_failure_events()`.
- **Lifecycle non-termination on rejection** — none of the four failure paths touch `self.active_trade`; verified empirically that `active_trade` is unchanged after a rejected transition.
- **Deterministic active execution path** — no hidden randomness in `run_engine/core` modules that are actually imported by `RunLoop` (the one remaining `random.random()` usage, in `state_modulation.py`, is dead code not imported anywhere in `run_engine/core`).
- **`trade_event` availability in `RunLoop.step()`** — `RunLoop.step()` already holds `trade_event` as a local variable after calling `self.trade_lifecycle_engine.on_execution(execution, state)`, and already passes it explicitly into `PnLEngine.update()`.
- **`PnLEngine` incidental non-mutation on rejection** — `PnLEngine.update()`'s event-type gate (`{"TRADE_CLOSED", "PARTIAL_CLOSE"}`) causes a `RUNTIME_FAILURE_EVENT` to return `0.0` without touching `self.last_realized_pnl`, so realized PnL and equity are numerically unaffected by rejection today — as a side effect of this filter, not as an explicit, tested contract.
- **`PositionEngine` behavior on rejection (baseline, unmodified)** — `update_post_trade()` is called unconditionally every tick; when the lifecycle position is unchanged (as it is after a rejection), `Position.side`, `Position.quantity`, and `Position.entry_price` are correctly left unchanged, but `Position.last_price` is unconditionally set to the current tick's price regardless of whether the transition was accepted or rejected.
- **`PerformanceEngine` behavior on rejection (baseline, unmodified)** — `update(decision, pnl, regime)` has no parameter carrying the lifecycle outcome; it unconditionally increments `stats[action]["trades"]` and recomputes the running `pnl`/`winrate` averages every tick, whether or not `trade_event` was a `RUNTIME_FAILURE_EVENT`.

---

## 4. Required P1-04 Capabilities

Restated from the Functional Requirement Analysis, in capability form:

- **C-1** — RunLoop must be able to explicitly recognize a rejected tick (FR-001).
- **C-2** — PerformanceEngine must not record an outcome for a rejected tick (FR-002).
- **C-3** — A single, adjudicated policy must govern `Position.last_price` on rejection, and PositionEngine must implement it (FR-003).
- **C-4** — Runtime Failure Event generation and retrieval must be formally verified against all four rejection reasons (FR-004).
- **C-5** — Rejection behavior must be verified deterministic under replay (FR-005).
- **C-6** — Financial-state non-mutation on rejection must be an explicit, tested contract rather than an incidental filter side effect (FR-006).

---

## 5. Gap Analysis Table

| Requirement | Baseline Capability | Status | Gap Description |
|---|---|---|---|
| C-1 (FR-001) | `trade_event.event_type` available in `RunLoop.step()` | **Gap** | No branch in `RunLoop.step()` consumes the rejection signal explicitly; it is currently ignored at the orchestration layer. |
| C-2 (FR-002) | Rejection signal exists; not passed to `PerformanceEngine` | **Gap** | `PerformanceEngine.update()` has no rejection-aware input and unconditionally counts every tick. Empirically confirmed: a rejected `BUY` incremented `stats["BUY"]["trades"]` from 1 to 2. |
| C-3 (FR-003) | `PositionEngine.update_post_trade()` always updates `last_price` | **Gap — blocked on specification decision (D-005)** | No policy has been adjudicated; current behavior (always update) is one of two defensible outcomes, neither yet formally chosen. |
| C-4 (FR-004) | Generation, immutability, retrieval all implemented | **No implementation gap — verification gap only** | Behavior exists and is individually spot-checked in this analysis chain, but no committed, repeatable test enumerates all four rejection reasons systematically. |
| C-5 (FR-005) | Active path is deterministic (no hidden randomness) | **No implementation gap — verification gap only** | Determinism holds today; no replay harness/test exists to make this a standing, repeatable guarantee. |
| C-6 (FR-006) | `PnLEngine`'s event-type gate incidentally prevents mutation | **Gap — formalization gap** | Correct today by construction of one filter, not by an explicit, independently testable contract. No guard exists that would remain correct if `PnLEngine`'s internals changed. |

---

## 6. Implementation-Relevant Gaps

Four gaps require an actual code change:

1. **RunLoop rejection recognition (C-1).** `run_engine/core/loop.py` — `RunLoop.step()` must explicitly branch on `trade_event.event_type == "RUNTIME_FAILURE_EVENT"`, or equivalently make the rejection outcome available to the components that need it (design choice deferred to the Architecture document per SDA Risk R-001 / FR doc RQ-002).

2. **PerformanceEngine non-mutation (C-2).** `run_engine/core/performance.py` and its call site in `run_engine/core/loop.py` — `PerformanceEngine.update()` must gain a way to know the tick was rejected (either an added parameter, or the call must be skipped by `RunLoop` on rejection) and must not mutate `stats` in that case.

3. **PositionEngine mark-price policy (C-3).** `run_engine/core/position.py` — implementation is blocked until the Architecture document adjudicates the policy question (RQ-001 / D-005). No code change should be made ahead of that decision.

4. **Financial non-mutation contract (C-6).** `run_engine/core/loop.py` and/or `run_engine/core/pnl.py` — an explicit guard (exact placement is a design choice for the Architecture document, per SDA Risk R-001) must replace the current incidental behavior, so the invariant survives future changes to either component.

Two items (C-4, C-5) require verification work only — no production code path needs to change for either, since the underlying behavior is already correct.

---

## 7. Non-Gaps / Deferred Items

The following are explicitly confirmed as **not** gaps for P1-04:

- `TradeLifecycleEngine` — no changes required. Rejection-event generation, immutability, and retrieval (D-001, D-002) are already complete; `trade_lifecycle.py` is not expected to require modification for P1-04.
- Lifecycle non-termination on rejection — already correct and verified; not a gap.
- Determinism of the active execution path — already correct; `state_modulation.py`'s dormant randomness is a repository-hygiene item (SDA Risk R-003), not a P1-04 gap.

The following are explicitly out of scope, per the Functional Requirement Analysis's Non-Goals (Section 6) and the Architecture Technical Debt Register:

- TD-001 (canonical Position source for `PnLEngine`) — Phase 2.
- TD-002 (unifying `_safe_float` implementations) — Phase 2.
- TD-004 (full lifecycle-based Performance redesign) — Phase 3; only the narrow C-2 rejection-non-mutation behavior is in scope for P1-04.
- TD-005 (automated regression test suite) — project-wide; P1-04 requires only the targeted verification described in Section 6 for C-4/C-5, not a general test-suite buildout.
- Multi-asset support, portfolio accounting, funding/fees/slippage expansion — unrelated to ADR-011.

---

## 8. Minimal Implementation Scope

The minimal set of files that P1-04 implementation is expected to touch:

- `run_engine/core/loop.py` — required (C-1, C-6, and the call-site change for C-2).
- `run_engine/core/performance.py` — required (C-2).
- `run_engine/core/position.py` — required, but **blocked** until the Architecture document resolves the mark-price policy decision (C-3).
- `run_engine/core/pnl.py` — conditionally required, only if the Architecture document places the C-6 guard at the `PnLEngine` boundary rather than at `RunLoop`.

Not expected to require changes: `run_engine/core/trade_lifecycle.py`, `run_engine/core/risk.py`, `run_engine/core/canonical_state.py`, `run_engine/core/canonical_enforcer.py`, `run_engine/core/state.py`, `run_engine/core/regime.py`, `run_engine/core/strategy.py`, `run_engine/core/execution/executor.py`.

No new runtime module is required. No new Authoritative Owner or Computational Authority is introduced. This is consistent with the Scientific Dependency Analysis's conclusion that P1-04 is integration work on an already-complete capability base.

---

## 9. Risks

**R-001** — C-1's and C-6's exact implementation shape (RunLoop-level gate vs. per-consumer guard) is not yet decided; both satisfy the same Acceptance Criteria but produce different code footprints. Carried forward from SDA Risk R-001; must be resolved in the Architecture document before Specification.

**R-002** — C-3 is fully blocked on a specification decision (D-005 / RQ-001) that this document does not make. Implementation must not proceed on `position.py` until that decision is recorded.

**R-003** — Changing `PerformanceEngine.update()`'s signature (C-2) is a breaking interface change, analogous to the `PnLEngine.update()` signature change made in P1-03.1. That change was verified safe because `run_engine/core/loop.py` was confirmed as the sole call site; the same verification must be repeated for `PerformanceEngine.update()` before implementation.

**R-004** — C-4 and C-5's verification work will be manual/interactive, since no automated regression suite exists (TD-005). This is a carried-forward methodology risk, not new to this document.

---

## 10. Conclusion

Six required capabilities (C-1 through C-6) were checked against the current runtime baseline. Four gaps require an actual code change (C-1, C-2, C-3, C-6); two require verification only, with no code change (C-4, C-5). Of the four implementation-relevant gaps, three (C-1, C-2, C-6) are unblocked and require only interface wiring on top of already-existing data; one (C-3) is explicitly blocked on a specification decision that must be made in the Architecture document before its implementation can begin.

No capability outside the six required capabilities was found necessary. No gap requires modification of `TradeLifecycleEngine` or any component outside the four files identified in Section 8. This is consistent with, and confirms, the Scientific Dependency Analysis's certification that P1-04 requires no missing prerequisite capability.

---

## 11. Next Document

The next document is `P1_04_ARCHITECTURE_V1_2026-07-09.md`.
