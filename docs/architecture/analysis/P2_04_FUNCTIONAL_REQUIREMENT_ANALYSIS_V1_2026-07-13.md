Document Class:
Functional Requirement Analysis

Document ID:
P2-04-FRA

Version:
V1.0

Status:
Draft for Internal Review

Date:
2026-07-13

Project:
Trading-Bot Scientific Runtime

Subsystem:
Run Engine

Primary Location:
docs/architecture/analysis/P2_04_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-13.md

Depends On:
- docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md
- docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md
- docs/architecture/certification/P2_03_FINAL_CERTIFICATION_V1_2026-07-11.md
- docs/architecture/P2_03_FINANCIAL_OWNERSHIP_ARCHITECTURE_V1_2026-07-11.md
- docs/architecture/analysis/P2_03_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-11.md
- docs/architecture/P2_02A_POSITION_OWNERSHIP_ARCHITECTURE_V1_2026-07-10.md
- docs/architecture/P2_02A_POSITION_OWNERSHIP_SPECIFICATION_V1_2026-07-10.md
- docs/architecture/certification/P2_02A_FINAL_CERTIFICATION_V1_2026-07-10.md
- docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md
- current runtime code at HEAD a81e197

Referenced By:
- future P2-04 Scientific Dependency Analysis
- future P2-04 Capability Gap Analysis
- future P2-04 Architecture
- future P2-04 Specification
- future P2-04 Certification

---

# P2-04 Functional Requirement Analysis

## 1. Purpose

This document performs the Functional Requirement Analysis for P2-04 (Risk Ownership), the implementation unit named directly after P2-03 (Financial Ownership, certified complete) in the approved Phase 2 sequence of `RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md`. The Implementation Baseline names P2-04's objectives verbatim as: "Verify Risk Metrics ownership. Validate deterministic RiskEngine behaviour."

This document does not decide architecture. It does not define interfaces. It does not implement code. Its sole purpose is to establish, from direct repository inspection, the verified current state of Risk Ownership (Risk Policy configuration, Drawdown, Drawdown Ratio, the risk-limiting formula, Position-derived Exposure consumption, and RiskEngine's determinism), and to derive the functional requirements that a later Scientific Dependency Analysis, Capability Gap Analysis, Architecture, and Specification must satisfy.

## 2. Scope

In scope: RiskEngine's Risk Policy configuration ownership, the risk-limiting formula (drawdown-ratio threshold check, regime-dampening multipliers), the resulting Risk Metric (`risk_allocation_factor`) ownership and naming, Position-derived Exposure's architectural disposition inside RiskEngine, RiskEngine's determinism and statelessness, and TD-006's remaining risk-formula-adjacent scope as bounded by `P2_03_FINANCIAL_OWNERSHIP_ARCHITECTURE_V1_2026-07-11.md`'s AD-015.

Out of scope (Section 24 for full detail): Drawdown and Drawdown Ratio's Computational Authority, Authoritative Owner, and input-source correctness (already fully certified by P2-03, not reopened here except as a compatibility-preservation constraint), full PerformanceEngine redesign or its consumption of Risk Metrics (P3-03), PositionSizingEngine activation, Position/Exposure ownership itself (P2-02A, certified), Persistence and Recovery (ADR-012), repository cleanup, and the automated regression test suite (TD-005).

## 3. Binding Architectural Baseline

- `docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md` - ADR-007 (Risk Evaluation as a Pure Computational Layer), ADR-004 (Position Represents Current Market Exposure, RiskEngine consumption clause), ADR-006 (Canonical Financial State Ownership, Drawdown clause), ADR-011 (Runtime Failure Handling), the Runtime Ownership Matrix's "Risk Metrics" row, Rules OM-001 through OM-009 (in particular OM-006, OM-007), Architecture Invariants AI-001 through AI-015 (in particular AI-005, AI-010), Acceptance Criteria AC-007 (Risk Evaluation); AC-002 (Unique Information Ownership) and AC-003 (Separation of Ownership and Computation) are also relevant by general applicability to Gap 1/Gap 2's ownership-naming findings (Sections 13, 15-16), though not individually quoted.
- `docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md` - Phase 2 Implementation Units, specifically the P2-04 entry: "Risk Ownership. Objectives: Verify Risk Metrics ownership. Validate deterministic RiskEngine behaviour."
- `docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md` - TD-006 (RiskEngine Peak Equity and Drawdown Ownership Duplication, Target Phase P2-03/P2-04, Status Deferred at the time of the Register's own text, though its Equity/Peak-Equity/Drawdown-input-source half is now certified resolved by P2-03; Section 27 below).
- `docs/architecture/certification/P2_03_FINAL_CERTIFICATION_V1_2026-07-11.md` - certified baseline HEAD `259a592` through `a81e197`, confirming RiskEngine holds zero financial instance state and Drawdown/Drawdown Ratio are correctly canonical-sourced (Sections 10, 23 FR-009/FR-010 of that certification).
- `docs/architecture/P2_03_FINANCIAL_OWNERSHIP_ARCHITECTURE_V1_2026-07-11.md` - P2-03-AD-007 (Drawdown Ratio Ownership Assignment) and P2-03-AD-015 (TD-006 Architectural Closure Boundary), both quoted below for traceability.
- `docs/architecture/P2_02A_POSITION_OWNERSHIP_ARCHITECTURE_V1_2026-07-10.md` - P2-02A-AD-007 (Exposure Naming Separation), which established the `risk_allocation_factor` naming this document relies on as background (Section 5, Section 6), and P2-02A-AD-008 (RiskEngine Consumption Boundary), which introduced the currently-unused `position_exposure` read and explicitly deferred its functional use to this unit.

ADR-007's binding text, quoted for traceability:

"RiskEngine SHALL operate exclusively as a Computational Layer. RiskEngine SHALL consume only Canonical Working State at its assigned execution stage. RiskEngine SHALL never own: Position, Exposure, Trade, Trade History, Equity, Peak Equity, Canonical Runtime State. RiskEngine computes derived Risk Metrics. CanonicalState stores the resulting canonical Risk Metrics." "A Risk Metric is a derived quantity calculated from canonical runtime state. Examples include: Drawdown, Exposure Utilization, Position Risk, Portfolio Risk, Margin Utilization, Risk Level. Risk Metrics are derived values. They are not primary runtime entities."

ADR-004's binding text (RiskEngine clause), quoted for traceability:

"Exposure SHALL always be derived from Position. RiskEngine SHALL consume Position-derived Exposure. RiskEngine SHALL never maintain an independent canonical Exposure representation."

P2-03-AD-015's binding text (TD-006 Architectural Closure Boundary), quoted for traceability:

"Any change to RiskEngine's own risk-limiting formula - max_exposure, min_exposure, max_drawdown thresholds, or regime-dampening multipliers (run_engine/core/risk.py:5-7,33-49) - remains explicitly outside this decision's scope and outside P2-03 entirely, deferred to P2-04 ('Verify Risk Metrics ownership. Validate deterministic RiskEngine behaviour,' Implementation Baseline)."

P2-02A-AD-008's binding text (RiskEngine Consumption Boundary), quoted for traceability:

"This value is read only; per AD-008.2, no functional use of it is required in this unit. The read establishes the architectural consumption boundary only. Functional use of position_exposure for risk policy remains explicitly deferred to a future architectural unit."

## 4. Verified Repository and Runtime Baseline

Repository state, verified directly, not assumed:

- Branch: `run-engine-consolidation-safety` (confirmed via `git branch --show-current`).
- HEAD: `a81e1978cb07bbb26223c94a1b24e9220520c445` ("Add P2-03 final certification"), matching the stated starting point exactly (confirmed via `git rev-parse HEAD`).
- Working tree: one modified file unrelated to `run_engine` (`docs/capabilities/SGF_013_SCIENTIFIC_BEHAVIOUR_REPRESENTATION_2026-06-26.md`) and a set of pre-existing untracked directories (`_chat_handover/`, `_sgf017_context/`, `_ssi_context/`, `backups/`, `claude_final_p1031_review/`, `claude_p1031_patch/`, `claude_p1_03b_review/`, `codex_p1_03_review/`, `engine/regime_classifier.py`, `live_logs/`, `outputs/`, `review_packages/`, `runtime_runs/`), plus several untracked P2-02A/P2-03 governing documents already present under `docs/architecture/` - none of these are inside `run_engine/`, none are touched by this analysis. `run_engine/` is confirmed clean (`git status --short run_engine/` returns no output).
- All governing documents named in Section 3 confirmed present at their stated paths.

Files read in full for this analysis: `run_engine/core/risk.py`, `run_engine/core/loop.py`, `run_engine/core/canonical_state.py`, `run_engine/core/canonical_enforcer.py`, `run_engine/core/position.py`, `run_engine/core/performance.py`, `run_engine/core/position_sizing.py`, `run_engine/core/equity_stabilizer.py`, `run_engine/runtime/risk.py`, `run_engine/main.py`.

Repository-wide search performed for (case-insensitive): `drawdown`, `exposure`, `risk_allocation`, `max_drawdown`, `max_exposure`, `min_exposure`, `RiskEngine`, `RiskLayer`, `RiskPolicy`, `regime.*damp` under `run_engine/`. Six files matched (`run_engine/core/risk.py`, `run_engine/core/loop.py`, `run_engine/core/canonical_state.py`, `run_engine/core/position.py`, `run_engine/core/position_sizing.py`, `run_engine/runtime/risk.py`); every match is accounted for in Sections 6 through 11 below.

Confirmed inactive (not imported by `run_engine/core/*.py` or `run_engine/main.py`, verified by direct repository-wide import search, unchanged classification from the P2-03 FRA's own Section 4):

- `run_engine/runtime/risk.py` (`RiskLayer`) - a third, independent Equity/Peak-Equity/Drawdown/Exposure computation (`update_equity()`, `drawdown()`, `allow_trade()`, `apply_trade()`, `release_exposure()`), structurally unrelated to `run_engine/core/risk.py`'s `RiskEngine`. Uses different numeric scale for its thresholds (`max_exposure = 3.0`, `max_drawdown = 50.0`, absolute currency units) than the active `RiskEngine` (`max_exposure = 1.0`, `max_drawdown = 0.2`, a ratio). Not on the active path; not treated as an active Risk Ownership gap by this document.
- `run_engine/core/position_sizing.py` (`PositionSizingEngine`) - reads `risk.get("exposure", 1.0)` (`position_sizing.py:14`) as a consumer input only; computes no Risk Metric itself. This reads `RiskEngine.check()`'s own returned dict (not `CanonicalState`), so it is unaffected by the `CanonicalState`-side `risk_allocation_factor` rename already completed in P2-02A. Not on the active path.
- `run_engine/core/equity_stabilizer.py` (`EquityStabilizer`) - an independent, smoothing-based equity computation; not Risk-Metric-shaped (no drawdown, exposure, or regime-dampening logic of any kind) and therefore scope-irrelevant to Risk Ownership; its inactive classification is inherited from the P2-03 FRA's own Section 4 rather than independently re-discovered by this document's own repository-wide search (Section 4's ten risk-related search terms do not match it); recorded here only for completeness.

## 5. Scientific Definitions

These definitions are restated from ADR-004/ADR-006/ADR-007 and the Architecture Baseline, not newly invented, and govern the rest of this document. Where the current runtime does not implement a concept with an explicit name, this is stated explicitly rather than presented as existing.

**Risk Metric** - per ADR-007: "a derived quantity calculated from canonical runtime state," not "a primary runtime entity." Named examples: Drawdown, Exposure Utilization, Position Risk, Portfolio Risk, Margin Utilization, Risk Level. Drawdown and Drawdown Ratio are both explicitly named Risk Metrics, now individually assigned a Computational Authority and Authoritative Owner by P2-03-AD-006/AD-007 (Section 6). No named example in ADR-007's list textually matches `risk_allocation_factor` as currently computed (Section 9).

**Risk Policy Configuration** - the set of threshold and multiplier values (`max_drawdown`, `max_exposure`, `min_exposure`, and the per-regime dampening multipliers) that parameterize RiskEngine's risk-limiting computation. Not named or defined anywhere in the Architecture Baseline's Scientific Definitions, ADRs, or Runtime Ownership Matrix; exists today exclusively as private `RiskEngine.__init__` literals and inline literals inside `check()`.

**Risk-Limiting Formula** - the deterministic computation, internal to `RiskEngine.check()`, that derives a bounded scaling value (`exposure`, published as `risk_allocation_factor`) from Drawdown Ratio and Regime, subject to Risk Policy Configuration's thresholds. Distinct from Drawdown and Drawdown Ratio, which are themselves named Risk Metrics; the Risk-Limiting Formula consumes Drawdown Ratio as one of its own inputs.

**Position-Derived Exposure** - per ADR-004, the signed market value of the current Position (`Position.exposure`), owned by `PositionEngine`/`CanonicalState` (P2-02A, certified). Distinct from `risk_allocation_factor`; the naming collision between the two was already resolved by P2-02A-AD-007 (Section 4 above).

**RiskEngine Determinism** - per AI-005 and ADR-007, the property that `RiskEngine.check(state, position, regime)` returns identical output for identical input, with no dependency on call history, wall-clock time, or any other non-explicit input. Not previously certified as its own, individually named finding; certified only as a byproduct of P2-03's `vars()`-based statelessness checks (`docs/architecture/certification/P2_03_FINAL_CERTIFICATION_V1_2026-07-11.md`, Section 10).

**Financial State** and **Financial Ownership** - as defined and fully certified by P2-03; not redefined here. Equity, Peak Equity, and Realized PnL (event and cumulative) are explicitly out of this document's scope (Section 24).

## 6. Current RiskEngine Representation

`run_engine/core/risk.py`, class `RiskEngine`, fifty-five lines, unchanged in every line relevant to Drawdown/Drawdown-Ratio/Equity/Peak-Equity since the P2-03 Final Certification (`docs/architecture/certification/P2_03_FINAL_CERTIFICATION_V1_2026-07-11.md`, Section 6-14):

- `__init__(self)` (lines 3-7): sets exactly three instance attributes - `self.max_drawdown = 0.2`, `self.max_exposure = 1.0`, `self.min_exposure = 0.1` - and nothing else. No financial state of any kind is retained (confirmed unchanged from the P2-03 certification's own `vars()` inspection).
- `check(self, state, position, regime)` (lines 9-55): a single public method, called once per tick from `run_engine/core/loop.py:92`.
  - Line 10: `position_exposure = position.get("exposure", 0.0)` - reads Position-derived Exposure into a local variable.
  - Lines 12-20: reads `equity` and `peak_equity` from `state` (the canonical financial state, per P2-03), with `None`-guards defaulting both to `0.0`.
  - Line 23: `drawdown = peak_equity - equity`.
  - Lines 26-28: `drawdown_ratio = 0.0; if peak_equity > 0: drawdown_ratio = drawdown / peak_equity`.
  - Line 31: `exposure = self.max_exposure` (local variable, distinct from `position_exposure`).
  - Lines 33-34: `if drawdown_ratio > self.max_drawdown: exposure = self.min_exposure` - the risk-limiting formula's threshold check.
  - Lines 37-44: regime-dampening multipliers - `CHOP` multiplies `exposure` by `0.7`; `TREND` multiplies by `1.0` (a no-op); `VOLATILE` multiplies by `0.5`. No other `regime` value is handled; an unrecognized `regime` string leaves `exposure` unmultiplied.
  - Line 47: `exposure = max(self.min_exposure, min(self.max_exposure, exposure))` - final clamp.
  - Lines 49-55: returns `{"equity": equity, "peak_equity": peak_equity, "drawdown": drawdown, "drawdown_ratio": drawdown_ratio, "exposure": exposure}`.

`position_exposure` (line 10) is read once and never referenced again anywhere in the method body. This is confirmed, by direct re-inspection, to be the exact and only state left by P2-02A-AD-008's own explicit decision (Section 3 above): the read establishes the architectural consumption boundary; functional use is explicitly and by name deferred to this unit.

The returned dict's `"exposure"` key is RiskEngine's own, internal, unrenamed name for its risk-limiting output (distinct from `position_exposure`); `CanonicalState.update_risk()` remaps it to the top-level `risk_allocation_factor` key (Section 9), per P2-02A-AD-007's already-certified naming separation.

## 7. Current Risk Policy Configuration

The three values `self.max_drawdown = 0.2`, `self.max_exposure = 1.0`, `self.min_exposure = 0.1` (`risk.py:5-7`) exist exclusively as `RiskEngine.__init__` literals:

- Never published to `CanonicalState`; no `CanonicalState` key holds any of the three.
- Never read by any other active-path component; confirmed by repository-wide search, no occurrence of `max_drawdown`, `max_exposure`, or `min_exposure` exists anywhere in `run_engine/core/loop.py`, `run_engine/core/canonical_state.py`, or `run_engine/core/canonical_enforcer.py`.
- Never named by any ADR, Scientific Definition, or Runtime Ownership Matrix row in `RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md`.
- Not duplicated inside any active-path file (unlike Initial Capital's pre-P2-03 duplication, P2-03-FR-017); the only other occurrence of comparably-named values is inside the confirmed-inactive `run_engine/runtime/risk.py`'s `RiskLayer` (`max_exposure = 3.0`, `max_drawdown = 50.0`), which uses a different numeric scale and is not on the active path (Section 4).

The regime-dampening multipliers (`0.7`, `1.0`, `0.5`, lines 38, 41, 44) are inline literals, not named instance attributes; they possess even less structural visibility than the three named Risk Policy attributes, since they cannot be inspected via `vars(RiskEngine())` at all.

No mechanism exists anywhere in the active runtime to read, override, or externally configure any of these six values (three thresholds, three regime multipliers) without editing `risk.py`'s own source.

## 8. Current Risk-Limiting Formula

Traced directly from `risk.py:31-47` (Section 6):

1. Start from `max_exposure` (`1.0`).
2. If `drawdown_ratio > max_drawdown` (`0.2`), drop to `min_exposure` (`0.1`) - a binary step function, not a continuous scaling relationship between drawdown severity and allocation.
3. Multiply by the regime-dampening multiplier (`0.7` CHOP, `1.0` TREND, `0.5` VOLATILE, unmultiplied for any other regime string).
4. Clamp the result to `[min_exposure, max_exposure]`.

This formula's only two inputs are `drawdown_ratio` (itself derived from canonical `equity`/`peak_equity`, Section 6) and `regime`. Neither `position_exposure` (Section 6, line 10) nor any Position-derived quantity participates in this computation at any step. The formula therefore currently produces the same `risk_allocation_factor` value regardless of whether the current Position's actual market exposure is small, large, zero, or absent, for any given `drawdown_ratio`/`regime` pair.

No occurrence of `_safe_float` exists anywhere in `risk.py` (confirmed by direct read); TD-002 ("Unify `_safe_float` implementations") is therefore confirmed, by direct repository inspection, to not implicate this unit's own files, consistent with the same finding already made by the P2-03 FRA for `pnl.py`.

## 9. Current Risk Metric Publication

`run_engine/core/canonical_enforcer.py:47-53`, `apply_risk(risk)`: dict-shape-agnostic Writer-on-Behalf-Of, calls `CanonicalState.update_risk(risk)` when `risk` is not `None`, matching the pattern already certified for every other financial/risk value.

`run_engine/core/canonical_state.py:78-82`, `update_risk(risk_dict)`:
```
self.state["drawdown"] = risk_dict.get("drawdown", 0.0)
self.state["drawdown_ratio"] = risk_dict.get("drawdown_ratio", 0.0)
self.state["risk_allocation_factor"] = risk_dict.get("exposure", 1.0)
```
Three of the returned dict's five keys (`drawdown`, `drawdown_ratio`, `exposure`) are written to `CanonicalState`; the remaining two (`equity`, `peak_equity`) are ignored by `update_risk()`, since `CanonicalState` already owns them via `CanonicalEnforcer.apply_equity()`/`apply_peak_equity()`, with `PnLEngine` as their Computational Authority per P2-03.

`CanonicalState.__init__` (`canonical_state.py:36,38,40`): `"drawdown": 0.0`, `"drawdown_ratio": 0.0`, `"risk_allocation_factor": 1.0` - the schema's three Risk-Metric-category default values, confirmed present among the fifteen top-level keys already certified complete by P2-03 (`docs/architecture/certification/P2_03_FINAL_CERTIFICATION_V1_2026-07-11.md`, Section 12).

Storage location for all three values matches the Runtime Ownership Matrix's general "Risk Metrics" row Authoritative Owner assignment (`CanonicalState`). Drawdown and Drawdown Ratio additionally now have an individually-named Computational Authority/Authoritative Owner assignment (P2-03-AD-006, P2-03-AD-007); `risk_allocation_factor` does not (Section 5, Section 11 Gap 2). The Runtime Ownership Matrix's own "Risk Metrics" row names `RiskEngine` (not `CanonicalEnforcer`) in its Writer-on-Behalf-Of column, consistent with that Matrix's general convention of repeating the Computational Authority in every row's Writer-on-Behalf-Of column; this is superseded in practice by ADR-001's Decision text, which designates `CanonicalEnforcer` as the sole Writer-on-Behalf-Of publication path for every canonical value, a substitution already established and relied upon by every prior certification in this governance chain (`docs/architecture/certification/P2_03_FINAL_CERTIFICATION_V1_2026-07-11.md`, Section 8).

Consumer confirmation: `run_engine/core/performance.py`'s `PerformanceEngine.update(decision, pnl, regime, trade_event)` does not accept, read, or reference `drawdown`, `drawdown_ratio`, or `risk_allocation_factor` anywhere in its body (confirmed by direct read, unchanged since the P2-03 FRA's own Section 10 finding). The Runtime Ownership Matrix's "Risk Metrics" row names `PerformanceEngine` as a Primary Consumer; this is not currently implemented. This is recorded as an observed Matrix-versus-implementation gap (Section 13, Gap 6), not assigned a resolution by this document (Section 28, Open Question).

## 10. Current Position-Derived Exposure Consumption

`run_engine/core/position.py:75-83`, `PositionEngine.snapshot()`: the canonical Position record's `"exposure"` key - signed market value, `side_factor * quantity * last_price` (`position.py:94-99`) - is the sole Computational Authority output for Position-derived Exposure, certified complete by P2-02A.

`run_engine/core/loop.py:92`: `risk = self.risk_engine.check(canonical_state, position, regime)` - `position` is the full, post-trade six-key Position dict (`position.py:75-83`'s `snapshot()` return shape), including `"exposure"`.

`run_engine/core/risk.py:10`: `position_exposure = position.get("exposure", 0.0)` - the sole read of Position-derived Exposure inside `RiskEngine`. As established in Section 6, this value is read and then never referenced again in `check()`'s remaining forty-five lines.

This is not a newly discovered defect. `docs/architecture/P2_02A_POSITION_OWNERSHIP_ARCHITECTURE_V1_2026-07-10.md`'s own AD-008 (Section 3 above) introduced this exact line, in this exact unused shape, as a deliberate architectural boundary: "no functional use of it is required in this unit... Functional use of position_exposure for risk policy remains explicitly deferred to a future architectural unit." That future unit is this one, by name, per the same document's Section 28 ("P2-04 (Risk Ownership Consolidation) - deferred; RiskEngine's functional use of Exposure in its own risk-limiting logic... remain P2-04's scope").

RiskEngine's consumption of Position-derived Exposure is, in its current mechanical form, already read-only and already free of any ownership acquisition (no mutation, no caching, no republication under any Position-owning or Exposure-owning name) - confirmed by direct re-read of `check()`'s full body. The open question this document identifies is not about the read's correctness, but about whether the read's result must ever influence the returned `risk_allocation_factor` for P2-04's Baseline objectives ("Verify Risk Metrics ownership. Validate deterministic RiskEngine behaviour") to be satisfied.

## 11. Current Risk Ownership Summary

Restated compactly from Sections 6 through 10; the full per-object table is given below.

Drawdown: Computational Authority `RiskEngine` (P2-03-AD-006, conformant, certified). Authoritative Owner `CanonicalState.state["drawdown"]` (conformant, certified). Not reopened by this document except as a compatibility constraint (Section 24).

Drawdown Ratio: Computational Authority `RiskEngine` (P2-03-AD-007, conformant, certified). Authoritative Owner `CanonicalState.state["drawdown_ratio"]` (conformant, certified). Not reopened by this document except as a compatibility constraint (Section 24).

`risk_allocation_factor`: Computational Authority `RiskEngine` (mechanically true today; not individually named by any ADR - Gap 2, Section 13). Authoritative Owner `CanonicalState.state["risk_allocation_factor"]` (mechanically true today, per the general Runtime Ownership Matrix "Risk Metrics" row; not individually named by any ADR).

Risk Policy Configuration (`max_drawdown`, `max_exposure`, `min_exposure`, regime multipliers): no Computational Authority or Authoritative Owner named anywhere in the Architecture Baseline; exists exclusively as `RiskEngine`-private literals (Gap 1, Section 13).

Position-derived Exposure, as consumed inside `RiskEngine`: Computational Authority and Authoritative Owner both remain `PositionEngine`/`CanonicalState` (P2-02A, unchanged, not reopened); `RiskEngine`'s own consumption is read-only and currently non-functional (Gap 3, Section 13).

**Risk Ownership Table.**

| Information Object | Current Computational Authority | ADR-Named Computational Authority | Current Authoritative Owner | ADR-Named Authoritative Owner | Writer-on-Behalf-Of | Readers | Conformance Status | Evidence |
|---|---|---|---|---|---|---|---|---|
| Drawdown | `RiskEngine.check()` | `RiskEngine` (P2-03-AD-006) | `CanonicalState.state["drawdown"]` | `CanonicalState` (ADR-006, P2-03-AD-006) | `CanonicalEnforcer.apply_risk()` | external result consumers; `PerformanceEngine` per Matrix, not implemented (Gap 6) | Conformant, certified (P2-03) | `risk.py:23`; P2-03 Final Certification Section 23 FR-010 |
| Drawdown Ratio | `RiskEngine.check()` | `RiskEngine` (P2-03-AD-007) | `CanonicalState.state["drawdown_ratio"]` | `CanonicalState` (P2-03-AD-007) | `CanonicalEnforcer.apply_risk()` | external result consumers; `PerformanceEngine` per Matrix, not implemented (Gap 6) | Conformant, certified (P2-03) | `risk.py:26-28`; P2-03 Final Certification Section 26 AD-007 |
| `risk_allocation_factor` | `RiskEngine.check()` | not individually named by any ADR (Gap 2) | `CanonicalState.state["risk_allocation_factor"]` | not individually named by any ADR (Gap 2) | `CanonicalEnforcer.apply_risk()` | external result consumers; confirmed-inactive `PositionSizingEngine` | Partially Defined (mechanically conformant, ownership not ADR-named) | `risk.py:31-47`; `canonical_state.py:40,82`; P2-02A-AD-007 (rename only) |
| Risk Policy Configuration (`max_drawdown`/`max_exposure`/`min_exposure`/regime multipliers) | `RiskEngine.__init__` (constants); inline literals (multipliers) | not named by any ADR (Gap 1) | `RiskEngine` (private, unpublished) | not named by any ADR (Gap 1) | none; never published | `RiskEngine.check()` internally only | Undefined (no ADR-level ownership exists to conform to or violate) | `risk.py:5-7,37-44` |
| Position-derived Exposure (as read inside RiskEngine) | `PositionEngine` (unchanged) | `PositionEngine` (ADR-004, unchanged) | `CanonicalState.state["position"]["exposure"]` (unchanged) | `CanonicalState` (ADR-004, unchanged) | `CanonicalEnforcer.apply_position()` (unchanged) | `RiskEngine` (read-only, non-functional, Gap 3) | Conformant boundary; non-functional consumption (P2-02A-AD-008, deliberate) | `risk.py:10`; P2-02A Architecture Section 16 |

## 12. Current Risk Information Flow

Traced through `RunLoop.step()` (`run_engine/core/loop.py:33-113`), risk-relevant steps only:

1. `position = self.position_engine.update_post_trade(...); self.enforcer.apply_position(position)` - Position, including Exposure, computed and published (unchanged, P2-02A/P2-03 certified).
2. `pnl = ...; equity_state = self.pnl_engine.compute_equity(...); ... self.enforcer.apply_equity(equity); self.enforcer.apply_peak_equity(peak_equity)` - Equity and Peak Equity computed and published by `PnLEngine`, before Risk Evaluation (P2-03 certified).
3. `canonical_state = self.cstate.get()` (`loop.py:90`) - the Canonical Working State snapshot `RiskEngine` will consume, taken after Equity/Peak-Equity publication.
4. `risk = self.risk_engine.check(canonical_state, position, regime)` (`loop.py:92`) - `RiskEngine` reads canonical Equity/Peak-Equity (via `canonical_state`) and Position-derived Exposure (via `position`, the same post-trade dict from step 1), computes Drawdown, Drawdown Ratio, and `risk_allocation_factor`.
5. `self.enforcer.apply_risk(risk if isinstance(risk, dict) else {})` (`loop.py:93`) - all three values published atomically via `CanonicalEnforcer`.
6. `performance = self.performance_engine.update(decision, pnl, regime, trade_event)` (`loop.py:95`) - `PerformanceEngine` runs after Risk Evaluation but does not read any of `risk`'s output (Section 9, Gap 6).

This sequence matches ADR-010's mandated ordering (Financial Accounting precedes Risk Evaluation precedes Performance Evaluation) exactly, unchanged since P2-03's own certified sequence. The ordering itself is conformant; this document's findings concern ownership naming and formula scope, not sequence.

## 13. Functional Problem Statement

Six distinct findings exist, all within or immediately adjacent to P2-04's stated Baseline objectives ("Verify Risk Metrics ownership. Validate deterministic RiskEngine behaviour."):

**Gap 1 - Risk Policy Configuration has no ADR-level Authoritative Owner or Computational Authority.** `max_drawdown`, `max_exposure`, `min_exposure`, and the three regime-dampening multipliers exist exclusively as private `RiskEngine` literals (Section 7), named by no ADR, Scientific Definition, or Runtime Ownership Matrix row. "Verify Risk Metrics ownership" plausibly requires the values that parameterize a Risk Metric's own computation to be at least as well-defined as the Risk Metric itself; this document takes no position on whether the resolution is publication, formal naming-in-place, or something else (Section 28, Open Question).

**Gap 2 - `risk_allocation_factor` is not individually named by any ADR.** Unlike Drawdown and Drawdown Ratio, both now individually assigned by P2-03-AD-006/AD-007, `risk_allocation_factor` is covered only by the Runtime Ownership Matrix's general "Risk Metrics" row. This is structurally the same shape of gap Drawdown Ratio had before P2-03 resolved it (P2-03 FRA FR-012, resolved by P2-03-AD-007).

**Gap 3 - Position-derived Exposure is read but not functionally used by the risk-limiting formula.** This is not a newly discovered defect; it is P2-02A-AD-008's own, explicit, named deferral to this unit (Section 10). The risk-limiting formula currently derives `risk_allocation_factor` exclusively from Drawdown Ratio and Regime, independent of the Position's actual current market exposure.

**Gap 4 - TD-006's risk-formula half remains open.** P2-03-AD-015 explicitly and by name deferred "any change to RiskEngine's own risk-limiting formula - max_exposure, min_exposure, max_drawdown thresholds, or regime-dampening multipliers" to this unit (Section 3). No governing document has yet evaluated whether this formula requires change, or whether it may be explicitly retained as-is.

**Gap 5 - RiskEngine's determinism has not been individually, separately verified as its own named finding.** P2-03's certification verified statelessness as a byproduct of its own Financial Ownership scope (`vars(RiskEngine())` checks, Section 10 of that certification), and additionally exercised RiskEngine's output-level determinism incidentally, as part of the full-system Replay and Determinism Certification (Sections 18-19 of that certification, comparing per-tick canonical state including `drawdown`, `drawdown_ratio`, and `risk_allocation_factor` across independent runs); this document's own Baseline objective text names "Validate deterministic RiskEngine behaviour" as a distinct deliverable, and no individually-named, RiskEngine-focused determinism finding yet exists independent of that incidental full-system evidence.

**Gap 6 - The Runtime Ownership Matrix names `PerformanceEngine` as a Primary Consumer of Risk Metrics; this is not implemented.** `performance.py` reads no Risk Metric of any kind (Section 9). Whether closing this belongs to P2-04 or to P3-03 ("Verify PerformanceEngine inputs. Validate Performance Metrics generation") is not decided by this document (Section 28, Open Question); the Implementation Baseline's own objective text for each unit suggests P3-03, since P2-04's text concerns `RiskEngine`'s own ownership and determinism, not downstream consumption, but this document takes no final position.

None of the six findings requires reopening P2-03 (Equity/Peak-Equity/Drawdown ownership, already certified), P2-02A (Position/Exposure ownership, already certified), or TD-005 (automated regression suite, project-wide) - those remain distinct, separately-scoped, already-certified or already-named concerns (Section 24).

## 14. Required Functional Capabilities

RC-1 - An explicit, ADR-named Authoritative Owner and Computational Authority for Risk Policy Configuration (`max_drawdown`, `max_exposure`, `min_exposure`, regime-dampening multipliers), closing Gap 1.

RC-2 - An explicit, individually-named Computational Authority (`RiskEngine`) and Authoritative Owner (`CanonicalState`) assignment for `risk_allocation_factor`, closing Gap 2, mirroring P2-03-AD-007's resolution for Drawdown Ratio.

RC-3 - An explicit architectural decision on Position-derived Exposure's role inside RiskEngine's risk-limiting formula - continued non-use with documented rationale, or functional incorporation - closing Gap 3.

RC-4 - An explicit evaluation and closure (or explicit, justified re-deferral) of TD-006's risk-formula half, closing Gap 4.

RC-5 - An explicit, independently recorded verification of RiskEngine's determinism and statelessness, closing Gap 5.

RC-6 - An explicit disposition (in scope for this unit, or explicitly assigned elsewhere) of the Runtime Ownership Matrix's `PerformanceEngine`-consumes-Risk-Metrics gap, addressing Gap 6 without necessarily resolving it inside this unit.

RC-7 - Preservation of every already-certified P1/P2-0x Risk-adjacent contract (Drawdown/Drawdown-Ratio formula, ownership, and canonical input source per P2-03; Position/Exposure separation and RiskEngine's read-only boundary per P2-02A; RUNTIME_FAILURE_EVENT non-mutation per P1-04/P2-03) unless this unit's own governance chain explicitly re-certifies a change.

## 15. Risk Policy Configuration Requirements

P2-04-FR-001 - Risk Policy Configuration (`max_drawdown`, `max_exposure`, `min_exposure`, and the per-regime dampening multipliers) SHALL possess an explicit, ADR-named Authoritative Owner and Computational Authority, rather than existing solely as unnamed `RiskEngine` literals.

Scientific Rationale: values that parameterize a named Risk Metric's computation are themselves scientifically significant; "Verify Risk Metrics ownership" (this unit's own Baseline objective text) is not fully satisfiable while the parameters governing that computation remain architecturally unnamed.
Architectural Rationale: currently violated by omission - no ADR, Scientific Definition, or Runtime Ownership Matrix row names any of these six values (Section 7, Section 13 Gap 1).
Existing Evidence: `run_engine/core/risk.py:5-7,37-44`.
Validation Condition: a governing Architecture document explicitly states Risk Policy Configuration's Authoritative Owner and Computational Authority, whether that remains `RiskEngine` alone (a documented decision) or is formally published.
Related ADR: ADR-007 (general Risk Metric framing, by proximity).
Related Technical Debt: adjacent to TD-006's risk-formula half (Gap 4), not identical to it.
Scope Classification: in scope (P2-04); explicit Baseline objective ("Verify Risk Metrics ownership").

P2-04-FR-002 - RiskEngine SHALL remain the exclusive Computational Authority translating Risk Policy Configuration and canonical financial/regime state into the resulting Risk Metric (`risk_allocation_factor`), consistent with ADR-007's "RiskEngine computes derived Risk Metrics."

Scientific Rationale: this restates the already-conformant state (Section 6) so it is not silently regressed by this unit's own implementation.
Architectural Rationale: ADR-007, verbatim - "RiskEngine computes derived Risk Metrics."
Existing Evidence: `run_engine/core/risk.py:9-55`; repository-wide search confirms no other active-path component computes any drawdown-ratio-and-regime-derived scaling value.
Validation Condition: repository-wide search confirms no component other than `RiskEngine` computes `risk_allocation_factor`.
Related ADR: ADR-007.
Related Technical Debt: none.
Scope Classification: in scope (P2-04); already satisfied, no implementation required for this specific requirement.

## 16. Risk Metric Ownership Requirements

P2-04-FR-003 - `risk_allocation_factor`'s Computational Authority (`RiskEngine`) and Authoritative Owner (`CanonicalState`) SHALL be explicitly, individually named by a governing Architecture document, closing Gap 2.

Scientific Rationale: mirrors P2-03-AD-007's own resolution for Drawdown Ratio, which faced the identical shape of gap (computed and stored, but not individually ADR-named) before P2-03 closed it.
Architectural Rationale: ADR-007's general "Risk Metric" category plausibly covers `risk_allocation_factor`, but no ADR text names it individually, unlike Drawdown and Drawdown Ratio (Section 5, Section 11).
Existing Evidence: `run_engine/core/risk.py:31-47`; `run_engine/core/canonical_state.py:40,82`; absence of "risk_allocation_factor," "allocation factor," or an equivalent term in ADR-007's Scientific Definitions and in the Runtime Ownership Matrix's individual row list (only the general "Risk Metrics" row exists).
Validation Condition: a future Architecture document explicitly states `risk_allocation_factor`'s Computational Authority and Authoritative Owner, using that name or an explicitly adopted successor name.
Related ADR: ADR-007.
Related Technical Debt: none directly; structurally adjacent to the already-resolved Drawdown Ratio naming gap (P2-03-AD-007).
Scope Classification: in scope (P2-04) as an open naming/ownership question; not yet resolved.

P2-04-FR-004 - `CanonicalState` SHALL remain the exclusive Authoritative Owner of Drawdown, Drawdown Ratio, and `risk_allocation_factor` (at the general Runtime Ownership Matrix "Risk Metrics"-row level; individual ADR-level naming for `risk_allocation_factor` specifically remains FR-003's open item).

Scientific Rationale: storage location is already conformant for all three (Section 9); this requirement locks in the already-correct state so it is not silently regressed by this unit.
Architectural Rationale: ADR-006 (Drawdown), P2-03-AD-007 (Drawdown Ratio), Rule OM-006 (CanonicalState exclusively owns active runtime state).
Existing Evidence: `run_engine/core/canonical_state.py:36,38,40,78-82`.
Validation Condition: `CanonicalState.state["drawdown"]`, `state["drawdown_ratio"]`, and `state["risk_allocation_factor"]` remain the sole storage locations after any change made by this unit's eventual implementation.
Related ADR: ADR-006, Rule OM-006.
Related Technical Debt: none.
Scope Classification: in scope (P2-04) as a compatibility-preservation requirement.

## 17. Position-Derived Exposure Consumption Requirements

P2-04-FR-005 - The architectural disposition of `position_exposure` (read at `risk.py:10`, currently unused after being read) SHALL be explicitly decided and documented: either (a) explicitly and permanently confirmed as read-only, non-functional consumption, with a stated scientific rationale, or (b) functionally incorporated into RiskEngine's risk-limiting computation.

Scientific Rationale: ADR-004 requires RiskEngine to "consume Position-derived Exposure," a requirement already mechanically satisfied by the read itself (P2-02A, certified); P2-02A-AD-008 explicitly named this exact decision as deferred to this unit (Section 3, Section 10).
Architectural Rationale: leaving the value permanently read-but-unused without an explicit decision record would leave ADR-004's consumption requirement satisfied only in the most minimal mechanical sense, with no scientific closure on whether that is the intended end state.
Existing Evidence: `run_engine/core/risk.py:10`; `docs/architecture/P2_02A_POSITION_OWNERSHIP_ARCHITECTURE_V1_2026-07-10.md` Section 16.1-16.4.
Validation Condition: a governing Architecture document for this unit explicitly states whether `position_exposure` participates in the risk-limiting formula's output, and if so, how.
Related ADR: ADR-004, ADR-007.
Related Technical Debt: TD-006 (risk-formula half).
Scope Classification: in scope (P2-04); the unit's own named deferral target per P2-02A-AD-008.

P2-04-FR-006 - Whatever disposition FR-005 selects, RiskEngine SHALL remain a strictly read-only consumer of Position-derived Exposure; it SHALL NOT acquire ownership of Position or Exposure in any form.

Scientific Rationale: ADR-007 - "RiskEngine SHALL never own: Position, Exposure..."; Rule OM-007 - "RiskEngine owns no runtime information. RiskEngine computes derived quantities only."
Architectural Rationale: matches the already-certified P2-02A boundary (`docs/architecture/certification/P2_02A_FINAL_CERTIFICATION_V1_2026-07-10.md`); functionally using `position_exposure` (per FR-005 option (b)) does not require or permit caching it, mutating it, or republishing it under any Position-owning or Exposure-owning name.
Existing Evidence: `run_engine/core/risk.py:9-55` (no mutation of `position` anywhere in the current method body).
Validation Condition: `RiskEngine.check()` never mutates its `position` parameter and never introduces an instance attribute or canonical key named `exposure` or `position` at any point.
Related ADR: ADR-004, ADR-007, Rule OM-007.
Related Technical Debt: none.
Scope Classification: in scope (P2-04) as a boundary-preservation requirement.

## 18. Risk-Limiting Formula Requirements

P2-04-FR-007 - The regime-dampening multipliers and the drawdown-ratio threshold check SHALL be evaluated against the Architecture Baseline's scientific requirements and either explicitly retained with documented rationale or revised through an explicit Architecture Decision.

Scientific Rationale: AI-005 (Deterministic Execution) and AI-010 (Financial Consistency, by extension to Risk Metric consistency) require that any retained or revised formula remain deterministic and internally consistent; this document does not itself evaluate whether the specific numeric thresholds (`0.2`, `0.7`, `0.5`) are scientifically justified, since that evaluation belongs to the Architecture stage.
Architectural Rationale: the formula (Section 8) is currently a binary step function (full allocation until the drawdown-ratio threshold, then a fixed reduced allocation) rather than a continuous or Exposure-aware function; this document records the formula's current shape as a finding, not a defect, since no ADR specifies what shape is required.
Existing Evidence: `run_engine/core/risk.py:31-47`.
Validation Condition: a governing Architecture document for this unit explicitly states whether the current formula is retained, and if retained, records the rationale.
Related ADR: ADR-007.
Related Technical Debt: TD-006 (risk-formula half).
Scope Classification: in scope (P2-04); explicit Baseline objective ("Validate deterministic RiskEngine behaviour" bears on the formula's own determinism, though not on its numeric calibration).

P2-04-FR-008 - TD-006's risk-formula half (regime-dampening multipliers, `max_drawdown`/`max_exposure`/`min_exposure` thresholds) SHALL be explicitly closed or explicitly re-deferred with stated justification by this unit's own governance chain.

Scientific Rationale: P2-03-AD-015 named this unit, by name, as the closure venue for TD-006's remaining scope (Section 3); leaving it unaddressed through this unit's own Architecture stage would leave TD-006 permanently open with no further named successor.
Architectural Rationale: P2-03-AD-015, verbatim (Section 3 above).
Existing Evidence: `docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md`, TD-006; `docs/architecture/P2_03_FINANCIAL_OWNERSHIP_ARCHITECTURE_V1_2026-07-11.md`, P2-03-AD-015.
Validation Condition: a future Certification for this unit records an explicit TD-006 disposition, in the same style already established by the P2-03 Final Certification's own Section 32.
Related ADR: ADR-006, ADR-007.
Related Technical Debt: TD-006.
Scope Classification: in scope (P2-04); explicit Register-named target phase.

## 19. Determinism Requirements

P2-04-FR-009 - `RiskEngine.check()` SHALL remain a pure, deterministic function of its three explicit parameters (`state`, `position`, `regime`), with no persisted instance state contributing to its output and no non-deterministic input of any kind.

Scientific Rationale: AI-005 - "Identical runtime inputs SHALL produce identical runtime outputs... Deterministic behaviour shall not depend upon hidden mutable state."
Architectural Rationale: already correctly satisfied (Section 6); `check()`'s only reads are its three parameters and its own three `__init__`-time-only constants; no randomness, wall-clock read, or global state is referenced anywhere in the method body (confirmed by direct read).
Existing Evidence: `run_engine/core/risk.py:9-55`; `docs/architecture/certification/P2_03_FINAL_CERTIFICATION_V1_2026-07-11.md`, Section 10 (statelessness confirmed at initialization, after a 50-tick run, after a lifecycle run, and after a failure-tick run), and Sections 18-19 (output-level determinism already exercised incidentally via full-system Replay and Determinism Certification, including `drawdown`, `drawdown_ratio`, and `risk_allocation_factor`).
Validation Condition: two independent calls to `check()` with identical `state`/`position`/`regime` arguments produce functionally identical returned dicts, verified at least once independently by this unit's own future certification rather than solely inherited from P2-03's.
Related ADR: AI-005, ADR-007.
Related Technical Debt: none.
Scope Classification: in scope (P2-04); explicit Baseline objective ("Validate deterministic RiskEngine behaviour"); already satisfied, verification (not implementation) required.

P2-04-FR-010 - RiskEngine SHALL hold no instance attribute beyond its three Risk Policy configuration constants, set once at initialization and never mutated thereafter.

Scientific Rationale: Rule OM-007 - "RiskEngine owns no runtime information. RiskEngine computes derived quantities only."
Architectural Rationale: already correctly satisfied, re-confirmed by direct read of `__init__` (lines 3-7, exactly three assignments) and of `check()` (no `self.<name> = ` assignment anywhere in lines 9-55).
Existing Evidence: `run_engine/core/risk.py:1-55`; `docs/architecture/certification/P2_03_FINAL_CERTIFICATION_V1_2026-07-11.md`, Section 10.
Validation Condition: `vars(RiskEngine())` returns exactly `{'max_drawdown': 0.2, 'max_exposure': 1.0, 'min_exposure': 0.1}` before and after any sequence of `check()` calls, re-verified independently by this unit.
Related ADR: ADR-007, Rule OM-007.
Related Technical Debt: none.
Scope Classification: in scope (P2-04); already satisfied, no implementation required for this specific requirement.

## 20. Consumer Boundary Requirements

P2-04-FR-011 - RiskEngine SHALL remain a strictly read-only consumer of canonical Equity, Peak Equity, and Position (including Position-derived Exposure); it SHALL NOT mutate, cache independently, or republish any of them under any owning name.

Scientific Rationale: ADR-007 - "Risk Evaluation does not create runtime truth. Risk Evaluation derives quantitative metrics from already established runtime information."
Architectural Rationale: restates and locks in the already-certified P2-03 boundary (Equity, Peak Equity) and the already-certified P2-02A boundary (Position, Exposure) for this unit's own scope, so neither is silently regressed by any change this unit introduces.
Existing Evidence: `run_engine/core/risk.py:9-55` (no write to `state` or `position` anywhere in the method body); `docs/architecture/certification/P2_03_FINAL_CERTIFICATION_V1_2026-07-11.md`, Section 23 FR-013.
Validation Condition: `RiskEngine.check()`'s `state` and `position` parameters remain unmutated across the call, verified by identity/equality comparison before and after.
Related ADR: ADR-007.
Related Technical Debt: none.
Scope Classification: in scope (P2-04) as a compatibility-preservation requirement.

## 21. Failure and Invalid-State Requirements

P2-04-FR-012 - Rejected transitions (`RUNTIME_FAILURE_EVENT`) SHALL continue to leave Drawdown, Drawdown Ratio, and `risk_allocation_factor` unmodified, consistent with the already-certified P2-03 non-mutation contract.

Scientific Rationale: ADR-011 - "Rejected transitions SHALL never: ... modify Risk..." (by extension of the named financial values to the Risk Metric category, consistent with how P2-03 FR-015 extended the same principle).
Architectural Rationale: already correctly implemented and certified (`docs/architecture/certification/P2_03_FINAL_CERTIFICATION_V1_2026-07-11.md`, Section 20, 8/8 assertions); this unit re-verifies rather than re-establishes this contract, since P2-04 introduces no new financial-state-mutating logic and no new mutation risk to `risk.py` beyond whatever FR-005/FR-007 eventually decide.
Existing Evidence: `docs/architecture/certification/P2_03_FINAL_CERTIFICATION_V1_2026-07-11.md`, Section 20.
Validation Condition: a scripted `RUNTIME_FAILURE_EVENT` tick produces functionally identical Drawdown/Drawdown-Ratio/`risk_allocation_factor` values before and after the tick, re-verified once this unit's own implementation (if any) lands.
Related ADR: ADR-011.
Related Technical Debt: none.
Scope Classification: in scope (P2-04) as a compatibility-preservation requirement.

## 22. Reset and Initial-State Requirements

P2-04-FR-013 - If Risk Policy Configuration gains an explicit Authoritative Owner outside `RiskEngine`'s own `__init__` (per FR-001), reset semantics for that owner SHALL be defined consistently with `CanonicalState.reset()`'s existing pattern; if Risk Policy Configuration remains `RiskEngine`-private, no reset mechanism is required, since `__init__`-time constants are never mutated (FR-010).

Scientific Rationale: AI-010 (Financial Consistency, extended by analogy to Risk Metric consistency) requires internal consistency "at all times," including immediately following a reset; a value that is never mutated after initialization trivially satisfies this without any dedicated reset logic.
Architectural Rationale: conditional on FR-001's eventual resolution; recorded here so the Specification stage does not have to separately rediscover this conditionality.
Existing Evidence: `run_engine/core/risk.py:3-7` (constants set once, never reassigned, confirmed by FR-010's own evidence); `run_engine/core/canonical_state.py:111-113` (`reset()` -> `self.__init__()`, the existing pattern any new owner would need to follow).
Validation Condition: after a full reset sequence, Risk Policy Configuration's values remain identical to their pre-reset values (since they are constants, not runtime-accumulated state), verified once FR-001's resolution is known.
Related ADR: AI-010.
Related Technical Debt: none.
Scope Classification: in scope (P2-04), conditionally on FR-001.

## 23. Compatibility Requirements

P2-04-FR-014 - Every already-certified P1/P2-0x Risk-adjacent contract (Drawdown/Drawdown-Ratio formula, Computational Authority, Authoritative Owner, and canonical input source per P2-03; Position/Exposure separation and RiskEngine's read-only consumption boundary per P2-02A; the P1-04/P2-03 `RUNTIME_FAILURE_EVENT` non-mutation contract) SHALL continue to function exactly as certified, unless this unit's own governance chain explicitly re-certifies a change.

Scientific Rationale: Cluster-I-style compatibility constraint, established precedent from every prior P2-0x Functional Requirement Analysis in this governance chain.
Architectural Rationale: none of FR-001/FR-003/FR-005/FR-007/FR-008 require touching `run_engine/core/pnl.py`, `run_engine/core/canonical_state.py`'s Equity/Peak-Equity/PnL-adjacent methods, `run_engine/core/position.py`, or `run_engine/core/trade_lifecycle.py`; any implementation that does touch those files or reopen those already-certified formulas requires explicit justification at the Architecture stage.
Existing Evidence: `docs/architecture/certification/P2_03_FINAL_CERTIFICATION_V1_2026-07-11.md`; `docs/architecture/certification/P2_02A_FINAL_CERTIFICATION_V1_2026-07-10.md`.
Validation Condition: full regression re-run of the P2-03/P2-02A certified scenarios after any P2-04 implementation produces functionally identical results for every already-certified field.
Related ADR: ADR-004, ADR-006, ADR-007, ADR-011.
Related Technical Debt: none.
Scope Classification: in scope (P2-04) as a constraint layer, not a build target.

P2-04-FR-015 - `PerformanceEngine`'s consumption (or non-consumption) of Risk Metrics (Drawdown, Drawdown Ratio, `risk_allocation_factor`) is explicitly scope-protected pending resolution of whether this belongs to P2-04 or P3-03 (Section 28, Open Question); this document does not mandate any change to `performance.py`.

Scientific Rationale: the Runtime Ownership Matrix's "Risk Metrics" row names `PerformanceEngine` as a Primary Consumer (Gap 6, Section 13), creating a plausible textual argument that closing this gap is within "Verify Risk Metrics ownership"; the governing task's own scope-protection instructions simultaneously caution against silent scope expansion.
Architectural Rationale: this tension is not resolved by this document (Section 28); recording it as a scope-protected item prevents silent scope expansion while preserving the question for explicit future disposition, following the identical pattern the P2-03 FRA used for its own FR-020 (Unrealized PnL scope protection).
Existing Evidence: Section 9 (confirmed absent); Runtime Ownership Matrix, "Risk Metrics" row.
Validation Condition: any future document that brings `PerformanceEngine`'s Risk-Metric consumption into P2-04's scope does so explicitly, not as an incidental side effect of FR-001 through FR-008.
Related ADR: ADR-008 (by contrast), Runtime Ownership Matrix.
Related Technical Debt: none.
Scope Classification: explicitly protected against silent scope expansion; disposition deferred.

## 24. Explicit Non-Goals and Deferred Scope

- Drawdown and Drawdown Ratio's Computational Authority, Authoritative Owner, formula, and canonical input source - fully certified by P2-03 (`docs/architecture/certification/P2_03_FINAL_CERTIFICATION_V1_2026-07-11.md`); not reopened here except as the compatibility-preservation requirements of FR-004, FR-011, FR-012, FR-014.
- Equity, Peak Equity, and Realized PnL (event and cumulative) - P2-03's stated and certified scope; not addressed here in any capacity beyond being read-only inputs to Drawdown (unchanged).
- Full `PerformanceEngine` redesign or its consumption of Risk Metrics - P3-03's stated scope ("Verify PerformanceEngine inputs. Validate Performance Metrics generation"); this document records only the observed gap (Gap 6) and an explicit scope-protection requirement (FR-015), neither of which redesigns `PerformanceEngine`.
- `PositionSizingEngine` activation - confirmed inactive (Section 4); not activated by this document; if a future unit reactivates it, that unit is responsible for reconciling its `risk.get("exposure", 1.0)` read against whatever this unit's eventual Architecture decides for `risk_allocation_factor`'s naming (FR-003).
- Position and Position-derived Exposure's own ownership (Computational Authority, Authoritative Owner, formula) - fully certified by P2-02A; not reopened here except as the compatibility-preservation requirement of FR-006, FR-011, FR-014.
- Persistence, Recovery - explicitly deferred by ADR-012 ("Persistence, Recovery and Schema Evolution are explicitly classified as Deferred Scope"); unaffected by this document.
- Repository cleanup - the confirmed-inactive `run_engine/runtime/risk.py` (`RiskLayer`), `run_engine/core/position_sizing.py`, and `run_engine/core/equity_stabilizer.py` are recorded as findings only (Section 4); their classification (retain/integrate/archive/remove) belongs to Phase 6 Repository Consolidation, not P2-04.
- Automated regression test suite - TD-005, project-wide, unaffected; validation of any future P2-04 implementation will be manual/interactive, consistent with every prior unit's precedent.
- No new architecture decision is proposed by this document. Section 13's six gaps and Sections 15 through 23's requirements describe what must become true; how (the exact Risk Policy Configuration ownership mechanism, whether `position_exposure` is functionally incorporated and in what formula shape, the exact `risk_allocation_factor` naming resolution) is explicitly deferred to the P2-04 Scientific Dependency Analysis, Capability Gap Analysis, Architecture, and Specification documents.

## 25. Functional Requirement Catalogue

P2-04-FR-001 - Risk Policy Configuration SHALL possess an explicit, ADR-named Authoritative Owner and Computational Authority. Source: ADR-007 (by proximity), Section 13 Gap 1.
P2-04-FR-002 - RiskEngine remains exclusive Computational Authority for `risk_allocation_factor`; already conformant. Source: ADR-007.
P2-04-FR-003 - `risk_allocation_factor`'s Computational Authority and Authoritative Owner SHALL be explicitly, individually named. Source: ADR-007, Section 13 Gap 2.
P2-04-FR-004 - CanonicalState remains exclusive Authoritative Owner of Drawdown, Drawdown Ratio, and `risk_allocation_factor`. Source: ADR-006, P2-03-AD-007, Rule OM-006.
P2-04-FR-005 - Position-derived Exposure's disposition inside RiskEngine's formula SHALL be explicitly decided. Source: ADR-004, P2-02A-AD-008.
P2-04-FR-006 - RiskEngine remains a strictly read-only consumer of Position-derived Exposure. Source: ADR-004, ADR-007, Rule OM-007.
P2-04-FR-007 - The risk-limiting formula (regime multipliers, drawdown-ratio threshold) SHALL be explicitly evaluated and either retained or revised. Source: AI-005, AI-010, Section 13 Gap 4.
P2-04-FR-008 - TD-006's risk-formula half SHALL be explicitly closed or re-deferred. Source: P2-03-AD-015.
P2-04-FR-009 - RiskEngine.check() remains a pure, deterministic function of its three parameters. Source: AI-005, ADR-007.
P2-04-FR-010 - RiskEngine holds no instance attribute beyond its three Risk Policy constants. Source: ADR-007, Rule OM-007.
P2-04-FR-011 - RiskEngine remains a strictly read-only consumer of Equity, Peak Equity, and Position. Source: ADR-007.
P2-04-FR-012 - RuntimeFailureEvent non-mutation extended to Drawdown, Drawdown Ratio, `risk_allocation_factor`. Source: ADR-011.
P2-04-FR-013 - Reset semantics for Risk Policy Configuration, conditional on FR-001. Source: AI-010.
P2-04-FR-014 - All prior-certified Risk-adjacent contracts preserved unless explicitly re-certified. Source: Cluster-I-style compatibility constraint.
P2-04-FR-015 - PerformanceEngine's Risk-Metric consumption explicitly scope-protected, not assumed in or out of scope. Source: Runtime Ownership Matrix, governing task scope protection.

## 26. ADR Traceability

| ADR | Related Requirements |
|---|---|
| ADR-004 (Position Represents Current Market Exposure) | FR-005, FR-006, FR-014 |
| ADR-006 (Canonical Financial State Ownership) | FR-004, FR-008, FR-014 |
| ADR-007 (Risk Evaluation as a Pure Computational Layer) | FR-001, FR-002, FR-003, FR-006, FR-007, FR-008, FR-009, FR-010, FR-011, FR-014 |
| ADR-008 (Performance Ownership) | FR-015 (by contrast only) |
| ADR-011 (Runtime Failure Handling) | FR-012 |
| AI-005 (Deterministic Execution) | FR-007, FR-009 |
| AI-010 (Financial Consistency, extended by analogy) | FR-007, FR-013 |
| Rule OM-006 (CanonicalState exclusively owns active runtime state) | FR-004 |
| Rule OM-007 (RiskEngine owns no runtime information) | FR-006, FR-009, FR-010, FR-011 |
| Runtime Ownership Matrix ("Risk Metrics" row) | FR-003, FR-015 |
| P2-03-AD-006, P2-03-AD-007 (Drawdown, Drawdown Ratio Ownership) | FR-004, FR-011, FR-014 (compatibility only) |
| P2-03-AD-015 (TD-006 Architectural Closure Boundary) | FR-005, FR-007, FR-008 |
| P2-02A-AD-007 (Exposure Naming Separation) | FR-003 (background/compatibility context only) |
| P2-02A-AD-008 (RiskEngine Consumption Boundary) | FR-005, FR-006 |

All requirement-relevant ADRs and Invariants named in Section 3 are referenced by at least one requirement above.

## 27. Technical-Debt Traceability

| Technical Debt Item | Status Before This Document | Relation to P2-04-FRA |
|---|---|---|
| TD-001 (Canonical Position Source for PnLEngine) | Register Status: Deferred; functionally resolved per P2-02A Final Certification | Not reopened; unrelated to Risk Ownership. |
| TD-002 (Unify `_safe_float` implementations) | Open, Target Phase 2 | Confirmed still outside this document's scope; `RiskEngine` has no `_safe_float` method of any kind (confirmed by direct read of `run_engine/core/risk.py`), so this item does not directly implicate P2-04's own file scope; not reopened or resolved here. |
| TD-003 (Document Pre-Trade Snapshot Dependency) | Partially Resolved (P2-02A recommendation, register not yet updated) | Not reopened; unrelated to Risk Ownership. |
| TD-004 (Lifecycle-based Performance Evaluation) | Already Planned, Target P3 | Not reopened; unrelated to RiskEngine's own ownership or determinism. |
| TD-005 (Automated Regression Test Suite) | Open, Target Project-wide | Confirmed still outside this document's scope (Section 24); validation of any future P2-04 implementation remains manual. |
| TD-006 (RiskEngine Peak Equity and Drawdown Ownership Duplication) | Deferred, Target P2-03/P2-04; Equity/Peak-Equity/Drawdown-input-source half certified resolved by P2-03 (P2-03 Final Certification Section 32); risk-formula half explicitly and by name remaining, per P2-03-AD-015 | This document's central subject. Gap 3, Gap 4, FR-005, FR-007, FR-008 directly address the remaining risk-formula half; this document does not itself resolve it (no architecture decision is made here), but confirms it is squarely within P2-04's scope and provides the repository-grounded evidence a future Capability Gap Analysis and Architecture document will need to close it. |
| TD-007 (RunLoop Lifecycle Control Surface) | Deferred, Target future Runtime Control Unit | Unrelated to Risk Ownership; not referenced by any requirement in this document, consistent with every prior unit's own finding (P2-02A Architecture Section 28: "no dependency identified; unrelated"). |

No Technical Debt Register file edit is made by this document (register modification is out of scope for a Functional Requirement Analysis, consistent with every prior unit's practice).

## 28. Open Questions

OQ-001 - Does Risk Policy Configuration require publication to `CanonicalState` (making it externally observable and consistent with how Initial Capital's single-source requirement was eventually satisfied for Equity, P2-03-FR-017), or is an explicit ADR-level statement that it remains `RiskEngine`-private, with documented rationale, sufficient to close Gap 1? Not resolved here; both options satisfy "ownership is explicitly named," which is this document's own requirement (FR-001).

Blocking Effect: blocks FR-001's exact implementation shape; does not block the underlying naming requirement.

OQ-002 - If `position_exposure` is functionally incorporated into the risk-limiting formula (FR-005 option (b)), what is the intended relationship - does higher current market exposure reduce `risk_allocation_factor` (a de-risking signal), increase it (a momentum-following signal), or leave it unaffected in most regimes but bound it in extreme cases? This document takes no position; the current formula's complete independence from `position_exposure` (Section 8) is a finding, not a recommendation for or against any particular incorporation.

Blocking Effect: blocking for FR-005/FR-007 implementation; not blocking for this document's own conclusions, since the gap itself is independently established regardless of the eventual formula shape.

OQ-003 - Is `risk_allocation_factor`'s current binary step function (full allocation until a drawdown-ratio threshold, then a fixed reduced allocation) the scientifically intended shape, or should it become a continuous function of drawdown severity? Not resolved here (Section 8, FR-007).

Blocking Effect: conditionally blocking for FR-007's exact resolution; not blocking for this document's own findings.

OQ-004 - Are the specific numeric values (`max_drawdown = 0.2`, `max_exposure = 1.0`, `min_exposure = 0.1`, regime multipliers `0.7`/`1.0`/`0.5`) themselves correct, or only their ownership/naming status under review by this document? This document takes no position on numeric calibration; FR-001 and FR-007 concern ownership and explicit-decision status only, not whether `0.2` is the right drawdown threshold.

Blocking Effect: non-blocking for this document; a numeric-calibration question is explicitly outside a Functional Requirement Analysis's own scope (observation and requirement derivation, not formula design).

OQ-005 - Does closing Gap 6 (`PerformanceEngine`'s non-consumption of Risk Metrics) belong to P2-04 or to P3-03? This document's own position (Section 13, Section 24) favors P3-03, by analogy to how P2-03-AD-015 assigned TD-006's boundary based on each unit's own named Baseline objective text, but does not treat this as a settled decision.

Blocking Effect: conditionally blocking for FR-015's exact closure venue; the Scientific Dependency Analysis or Capability Gap Analysis stage should confirm or adjust this positioning, consistent with how the P2-03 FRA's own OQ-007 was later resolved by P2-03-AD-015.

OQ-006 - Should the regime-dampening multipliers (`0.7`, `1.0`, `0.5`) be treated as part of "Risk Policy Configuration" (FR-001) for ownership purposes, or as part of the "Risk-Limiting Formula" (FR-007) for formula-shape purposes, given that they are currently inline literals rather than named instance attributes like the three threshold values? This document classifies them under both (Section 7, Section 8) since they are relevant to each concern from a different angle; a future document may need to draw a sharper line.

Blocking Effect: non-blocking; a classification question only, not a functional requirement in itself.

OQ-007 - Is there a documented, intentional reason `RiskEngine.check()`'s local variable is named `exposure` (colliding, in concept though not in Python scope, with `position_exposure` and with `CanonicalState`'s `position.exposure` field), given that P2-02A-AD-007 already deliberately renamed the *canonical* storage key to `risk_allocation_factor` specifically to avoid this exact naming collision at the architecture level? Purely a naming-clarity question internal to `risk.py`, not a functional one; recorded for completeness, not blocking.

Blocking Effect: non-blocking.

## 29. Functional Readiness Decision

This analysis finds six confirmed, repository-grounded findings (Section 13), all directly within or immediately adjacent to P2-04's stated Baseline objectives, and one already-logged Technical Debt item (TD-006) whose remaining, explicitly-named scope is centrally implicated by three of the six findings. All six findings are localized to a small, already-understood set of files (`run_engine/core/risk.py`, with `run_engine/core/canonical_state.py` and `run_engine/core/canonical_enforcer.py` implicated only for any eventual publication mechanism), consistent with P2-03-AD-015's own explicit line-level citation of `run_engine/core/risk.py:5-7,33-49` as this unit's remaining territory.

No blocking ambiguity was found in the existing baseline text that would prevent proceeding: ADR-007's Decision and Acceptance Criteria sections are unambiguous regarding RiskEngine's read-only consumption boundary and its status as a pure computational layer; P2-03-AD-015 and P2-02A-AD-008 both unambiguously and explicitly name this unit as the venue for the risk-formula and Position-Exposure-functional-use decisions respectively. Only the exact resolution mechanism (OQ-001 through OQ-004, OQ-006) and the PerformanceEngine-consumption boundary question (OQ-005) require architecture-stage decisions, consistent with how every prior P2-0x unit in this governance chain has left comparable decisions to its own Architecture document.

Functional Readiness: READY. This document is sufficient to proceed to the P2-04 Scientific Dependency Analysis. No further repository investigation is required before that step.

## 30. Internal Consistency Review

Terminology consistency - "Risk Metric," "Risk Policy Configuration," "Risk-Limiting Formula," "Position-Derived Exposure," and "RiskEngine Determinism" are used exactly as defined in Section 5 throughout this document; no term is used ambiguously or interchangeably with another. "Byte-identical" is not used anywhere in this document to describe a Python-object, runtime-dictionary, or numeric comparison; where such a comparison is anticipated (Section 19, Section 20, Section 21), "functionally identical" is used instead, consistent with the terminology rule established in the P2-02A Final Certification and reaffirmed throughout the P2-03 governance chain.

Ownership consistency - no requirement in Sections 15 through 23 assigns ownership of any concept to a component other than what ADR-004/ADR-006/ADR-007, P2-03-AD-006/AD-007, or the Runtime Ownership Matrix already assigns, or explicitly identifies as currently unassigned (Gap 1, Gap 2). No new Authoritative Owner or Computational Authority is proposed; every requirement either restates an already-correct assignment (FR-002, FR-004, FR-009, FR-010, FR-011) or names an already-identified naming gap for future architecture-stage resolution (FR-001, FR-003, FR-005, FR-007).

Scope consistency - every requirement traces to either ADR-004/006/007/011 text directly, a Section 6 through 13 repository finding, or an already-logged Technical Debt Register item explicitly targeted at P2-04 (TD-006's remaining half). No requirement duplicates P2-03, P2-02A, or P3-03 scope; Section 24 explicitly excludes all three, along with Persistence/Recovery (ADR-012), repository cleanup, and the automated regression suite (TD-005).

Traceability consistency - Section 25's catalogue and Section 26's ADR mapping are cross-checked: all fifteen functional requirements appear in exactly one catalogue row each; every ADR named in Section 3 as binding is referenced by at least one requirement.

Observation/requirement/decision separation - Sections 6 through 12 contain only observations, each with a direct file/line/method citation. Section 13 synthesizes those observations into a problem statement. Sections 15 through 23 contain only requirements derived from those observations plus the binding baseline. Section 28 contains only open questions explicitly deferred to a future Scientific Dependency Analysis, Capability Gap Analysis, or Architecture document; no architecture decision, formula design, or numeric calibration is finalized anywhere in this document.

No fabricated capability - `risk_allocation_factor`'s ADR-level naming gap and Risk Policy Configuration's unowned status are each explicitly and repeatedly documented as absent (Sections 5, 7, 9, 11) rather than described as existing in any partial or approximate form; the `position_exposure` non-use is documented as a deliberate, already-recorded deferral (Section 10), not misrepresented as a newly discovered defect; no requirement in this document assumes a capability exists that repository inspection did not confirm.

Status: Internal Consistency Review PASS.
