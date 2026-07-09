# Document Metadata

Document Class: Final Implementation Certification
Document ID: P1-03-1-CERT
Version: V1.0
Status: Final
Date: 2026-07-09
Project: Trading-Bot Scientific Runtime
Subsystem: Run Engine
Storage Location: docs/architecture/certification/
Filename: P1_03_1_FINAL_CERTIFICATION_V1_2026-07-09.md

Repository: sniper-bot
Branch: run-engine-consolidation-safety
Certified Commit: 57e24e6 ("Fix P1-03.1 entry basis handoff and quantity validation")

Depends On:
- docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md
- docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md

Referenced By:
- docs/architecture/analysis/P1_04_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-09.md
- docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md

---

# P1-03.1 Final Implementation Certification

## 1. Scope

P1-03.1 closed the ownership-boundary and quantity-integrity gaps identified after P1-03 (Partial Close and Scale-In). The certified scope is:

- Explicit `entry_basis` handoff from `RunLoop` to `PnLEngine`, replacing an implicit side-channel.
- Removal of all `execution["entry_price"]` mutation from `PositionEngine`.
- Explicit `PnLEngine` ownership of the realized-PnL entry price input, with no read of `execution["entry_price"]` remaining anywhere in `run_engine/core`.
- Quantity validation hardening in `TradeLifecycleEngine`: rejection of non-finite quantities (`nan`, `inf`, `-inf`) and elimination of unhandled exceptions on non-numeric input.
- Removal of the legacy, unused `PositionEngine.update_pre_trade()` method.

## 2. Implemented Changes

**Entry-basis ownership handoff.** `RunLoop.step()` now captures `position_pre = self.position_engine.snapshot()` before the tick's lifecycle/position update, and passes `position_pre["entry_price"]` explicitly into `PnLEngine.update(trade_event, entry_basis)`. `PnLEngine.update()`'s signature changed from `update(trade_event, execution: Dict)` to `update(trade_event, entry_basis: float)`; it computes `entry_price = float(entry_basis)` directly and no longer reads `execution.get("entry_price", ...)`.

**Elimination of the entry-price side-channel.** `PositionEngine.update_post_trade()` no longer writes `execution["entry_price"] = self.entry_price` in any branch (previously written in three places: on flat-transition, on full-close, and on partial-close). The weighted-average entry price computed by `PositionEngine` is now consumed by `PnLEngine` solely through the explicit `entry_basis` parameter.

**Removal of dead code.** `PositionEngine.update_pre_trade()`, which was no longer called anywhere in `run_engine/core`, was deleted in full.

**Quantity validation hardening.** `TradeLifecycleEngine._validate_execution_quantity()` now rejects non-finite values via `math.isfinite()` before the epsilon comparison. `TradeLifecycleEngine._safe_float()` was changed from an unguarded `float(value)` call to a `try/except (TypeError, ValueError)` that returns `float("nan")` on unparseable input, so `on_execution()` can no longer raise an unhandled exception from malformed execution data — malformed quantities are instead surfaced as a `RUNTIME_FAILURE_EVENT` with reason `INVALID_EXECUTION_QUANTITY`.

**Lifecycle documentation.** `LifecycleEvent.entry_price` now carries an explicit comment clarifying that it holds the trade's original open entry price, not the weighted-average entry basis after Scale-In — that weighted-average value is owned and computed exclusively by `PositionEngine`/`PnLEngine`.

## 3. Files Modified

- `run_engine/core/loop.py`
- `run_engine/core/pnl.py`
- `run_engine/core/position.py`
- `run_engine/core/trade_lifecycle.py`

No other runtime files were modified. No test files existed prior to this unit and none were added.

## 4. Validation Results

- `python -m compileall run_engine/core` — PASS, no errors, across all validation rounds.
- `execution["entry_price"]` write/read elimination — PASS. Repository-wide search confirms zero remaining occurrences in `run_engine/core`.
- `update_pre_trade` removal — PASS. Repository-wide search confirms zero remaining occurrences in `run_engine/core`.
- Quantity validation — PASS for all tested invalid inputs: `"abc"`, `nan`, `inf`, `-inf`, `None`, `0`, and negative values each produced exactly one `RUNTIME_FAILURE_EVENT` with reason `INVALID_EXECUTION_QUANTITY`, with no exception raised in any case.
- Valid quantity acceptance — PASS. A valid finite quantity (`1.0`) produced a correct `TRADE_OPENED` event.
- End-to-end LONG scenario (Open 1 @ 100 → Scale-In 1 @ 200 → Partial Close 1 @ 250) — PASS. Realized PnL = 100, matching the weighted-average entry basis of 150 computed by `PositionEngine`.
- End-to-end SHORT scenario (Open 1 @ 100 → Scale-In 1 @ 200 → Partial Close 1 @ 50) — PASS. Realized PnL = 100, symmetric to the LONG case.
- Two-stage close scenario (Open 2 @ 100 → Partial Close 1 @ 200 → Full Close 1 @ 300) — PASS. Realized PnL = 100 then 200; lifecycle terminated exactly once; `active_trade` correctly `None` after full close; `Position` correctly reset to `FLAT` with `entry_price = 0.0`.
- Regression check — PASS. Repository-wide search confirms `run_engine/core/loop.py` is the sole call site of `PnLEngine.update()`; the breaking signature change has no other consumer in the live codebase.

## 5. Codex Review Summary

No independent Codex technical repository review was performed specifically for P1-03.1. Verification of this unit was carried out through direct repository inspection, static compilation, targeted runtime validation, and repository-wide regression search, as recorded in Section 4. This is recorded explicitly rather than presumed, so the certification record does not overstate independent-review coverage. Independent Codex review remains available to be commissioned separately if required before Final Scientific Certification of the Run Engine as a whole.

## 6. Claude Final Review Summary

An independent architecture and implementation review was performed against `RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md` and `RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md`, covering ownership boundaries, information flow, hidden coupling, layer separation, lifecycle correctness, position ownership, PnL correctness, performance interaction, regression risks, and architectural consistency, across the five in-scope files (`loop.py`, `pnl.py`, `position.py`, `trade_lifecycle.py`, `performance.py`).

**Final Verdict: PASS WITH MINOR FINDINGS.**

No Critical findings. No Major findings. The entry-basis handoff was confirmed to correctly implement ADR-004 and ADR-005 (PnLEngine consumes Position for cost-basis valuation, matching the Runtime Stage Responsibilities table's declared "Lifecycle Events + Position" input), verified correct for LONG, SHORT, single-stage, and two-stage close scenarios.

## 7. Remaining Minor Findings

Five Minor/Observation-level findings were identified during review. None block certification; all are logged in the Architecture Technical Debt Register:

- **TD-001** — `PnLEngine` receives `entry_basis` from `PositionEngine`'s live snapshot rather than from `CanonicalState`. Pre-existing pattern, scoped to Phase 2 (Ownership Consolidation).
- **TD-002** — `TradeLifecycleEngine._safe_float` and `PositionEngine._safe_float` have inconsistent defensive hardening (only the former guards against exceptions). Not currently reachable as a live bug. Scoped to Phase 2.
- **TD-003** — The reason `PnLEngine` must consume the pre-trade (not post-trade) Position snapshot is functionally load-bearing but undocumented in code. Scoped to a Phase-1 follow-up.
- **TD-004** — `PerformanceEngine` remains decision-oriented rather than lifecycle-outcome-oriented (pre-existing AD-005 finding, unrelated to this unit's diff). Scoped to Phase 3.
- **TD-005** — No automated regression test suite exists for `run_engine/core`; all verification to date has been manual/interactive. Scoped project-wide.

## 8. Reference to the Architecture Technical Debt Register

The full record of these items, including priority, target phase, and status, is maintained in `docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md`. That register is the authoritative tracking location for all deferred findings from this certification; this document does not duplicate their status beyond the summary in Section 7.

## 9. Final Certification Statement

P1-03.1 has been successfully completed.

No Critical Findings remain.

No Major Findings remain.

Remaining Minor Findings are tracked in the Architecture Technical Debt Register.

The Phase-1 acceptance criteria applicable to this implementation unit are satisfied.

**P1-03.1 is officially closed.**

**Development is approved to proceed with P1-04.**
