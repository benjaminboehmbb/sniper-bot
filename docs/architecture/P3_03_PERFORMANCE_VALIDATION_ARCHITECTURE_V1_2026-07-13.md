Document Class:
Architecture Decision Document

Document ID:
P3-03-ARCH

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
docs/architecture/P3_03_PERFORMANCE_VALIDATION_ARCHITECTURE_V1_2026-07-13.md

Depends On:
- docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md
- docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md
- docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md
- docs/architecture/analysis/P3_03_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-13.md
- docs/architecture/analysis/P3_03_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-13.md
- docs/architecture/analysis/P3_03_CAPABILITY_GAP_ANALYSIS_V1_2026-07-13.md
- complete P3-01 governance chain (FRA, SDA, CGA, Architecture, Specification, Final Certification)
- complete P3-02 governance chain (FRA, SDA, CGA, Architecture, Specification, Final Certification)
- docs/architecture/P2_02A_POSITION_OWNERSHIP_ARCHITECTURE_V1_2026-07-10.md
- docs/architecture/P2_03_FINANCIAL_OWNERSHIP_ARCHITECTURE_V1_2026-07-11.md
- docs/architecture/P2_04_RISK_OWNERSHIP_ARCHITECTURE_V1_2026-07-13.md
- current runtime code at HEAD 5f8be51ca216c77e6a1614c51e7f0ef5b35ccb01

Referenced By:
- future P3-03 Specification
- future P3-03 Implementation
- future P3-03 Final Certification

Methodological Structure Reference (content not carried over):
- docs/architecture/P3_02_INFORMATION_FLOW_VALIDATION_ARCHITECTURE_V1_2026-07-13.md

---

# P3-03 Performance Validation Architecture

## 1. Document Metadata

See front matter above. This document is the P3-03 Architecture, the fourth stage of the P3-03 governance chain (FRA -> SDA -> CGA -> Architecture -> Specification -> Implementation -> Final Certification). It is the first P3-03 stage permitted to make binding decisions.

## 2. Purpose

This document converts the twenty-five Functional Requirements of `P3_03_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-13.md` (the "FRA"), the fifty-five Dependency records of `P3_03_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-13.md` (the "SDA"), and the twenty-nine Capability classifications of `P3_03_CAPABILITY_GAP_ANALYSIS_V1_2026-07-13.md` (the "CGA") into binding architecture decisions. Every remaining P3-03-owned capability gap (CAP-005, CAP-006, CAP-007, CAP-008, CAP-009, CAP-010, CAP-012, CAP-013, CAP-017, CAP-018, CAP-025, CAP-029) is decided explicitly in this document, resolving all five Functional Gaps (FG-001 through FG-005) and architecturally closing TD-004 within this unit's own scope. This document does not write a Specification, does not define Python signatures, method bodies, or file diffs, does not implement code, and does not build a test suite. Its output is the binding target architecture the Specification stage must translate into an exact implementation contract.

## 3. Scope

In scope: the twenty Architecture questions the governing task names - Performance Semantic Source, Decision-versus-Outcome Separation, Performance Keying, Trade Recognition, Realized-PnL Attribution, Unrealized PnL/Equity/Drawdown Boundary, Performance Aggregation, Performance History, Reporting Boundary, Performance Ownership, Performance Publication, Performance Update Timing, HOLD/NOOP, Rejection/Runtime Failure Event, Failed Tick, Determinism and Replay, Alternative Performance Paths, TD-004, Documentation/Verification Gap disposition, and Cross-Unit Boundaries.

Out of scope, per the FRA (Section 2), the SDA (Section 2), the CGA (Section 3), and the governing task's own "Wichtige Grenzen": P3-01's own twelve-stage execution ordering (not reopened); Position, PnL, and Risk formula or ownership changes (P2-02A/P2-03/P2-04, not reopened); P3-02's own certified Composite Isolation and Structural Independence mechanisms (not reopened, only preserved); Persistence, Recovery, and Schema Evolution (ADR-012, Deferred Scope); Operator Lifecycle Control (TD-007); Reporting-module implementation, UI, export, or persistence; scientific Strategy Evaluation or optimization; parallel or asynchronous execution; concrete Python signatures, file diffs, Implementation Units, or tests; any new Functional Requirement, Dependency, or Capability classification.

## 4. Binding Baseline

- `docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md` - ADR-001 through ADR-012 (especially ADR-002, ADR-005, ADR-006, ADR-008, ADR-009, ADR-010, ADR-011); the Runtime Ownership Matrix and Rules OM-001 through OM-009; the Target Information Flow, Principles/Rules IF-001 through IF-006, the Runtime Stage Responsibilities table, the Tick Completion Contract; Architecture Invariants AI-001 through AI-015; Acceptance Criteria AC-001 through AC-015 (especially AC-008, AC-014).
- `docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md` - the P3-03 unit definition ("Verify PerformanceEngine inputs. Validate Performance Metrics generation.").
- `docs/architecture/analysis/P3_03_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-13.md` - twenty-five Functional Requirements, five Functional Gaps (FG-001 through FG-005), four Verified Conformant Findings, two Documentation Gaps, one Verification Gap, two Residual Risks.
- `docs/architecture/analysis/P3_03_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-13.md` - fifty-five dependency records, twelve Requirement Clusters, nine Dependency Layers, no cyclic dependency found.
- `docs/architecture/analysis/P3_03_CAPABILITY_GAP_ANALYSIS_V1_2026-07-13.md` - twenty-nine capabilities, seventeen COMPLETE, five PARTIAL (CAP-009, CAP-010, CAP-012, CAP-018, CAP-029), seven MISSING (CAP-005, CAP-006, CAP-007, CAP-008, CAP-013, CAP-017, CAP-025).
- `docs/architecture/P3_01_DETERMINISTIC_EXECUTION_ORDERING_ARCHITECTURE_V1_2026-07-13.md`, its Specification, and `docs/architecture/certification/P3_01_FINAL_CERTIFICATION_V1_2026-07-13.md` - the certified P3-01 twelve-stage ordering (Performance Evaluation is step 11), Failed-Tick semantics, HOLD semantics, rejection non-mutation (P3-01-AI-012, explicitly naming Performance statistics), and replay determinism this document does not reopen.
- `docs/architecture/P3_02_INFORMATION_FLOW_VALIDATION_ARCHITECTURE_V1_2026-07-13.md`, its Specification, and `docs/architecture/certification/P3_02_FINAL_CERTIFICATION_V1_2026-07-13.md` - the certified P3-02 Canonical Read Model (Composite Isolation), Performance-Metrics Object Identity (Structural Independence), and Writer-on-Behalf-Of contract this document preserves without exception.
- `docs/architecture/P2_02A_POSITION_OWNERSHIP_ARCHITECTURE_V1_2026-07-10.md`, `docs/architecture/P2_03_FINANCIAL_OWNERSHIP_ARCHITECTURE_V1_2026-07-11.md`, `docs/architecture/P2_04_RISK_OWNERSHIP_ARCHITECTURE_V1_2026-07-13.md`, and their Final Certifications - the certified contract baseline this architecture must preserve without exception.
- Current runtime code at HEAD `5f8be51ca216c77e6a1614c51e7f0ef5b35ccb01`, re-traced in Section 5.

## 5. Repository-Grounded Current State

Repository state re-verified: branch `run-engine-consolidation-safety`, local HEAD and remote HEAD both `5f8be51ca216c77e6a1614c51e7f0ef5b35ccb01`, identical. `git status --short -- run_engine/` and `git diff --stat -- run_engine/` both return empty: `run_engine/` is unchanged since the FRA, SDA, and CGA were drafted, independently confirming every fresh repository fact those documents established remains valid evidence for this document.

The following facts, each individually re-confirmed for this document, ground every Architecture Decision in Section 25:

- `performance.py:6-37`: `PerformanceEngine.update(self, decision, pnl, regime, trade_event)` reads `decision.get('action', 'HOLD')` as its own sole accounting key; increments `self.stats[action]['trades']` unconditionally except on `RUNTIME_FAILURE_EVENT`; never reads `trade_event.event_type` beyond that single equality test; never reads `execution` (not passed at all).
- `loop.py:95-96`: the sole call site, `performance = self.performance_engine.update(decision, pnl, regime, trade_event)`, positioned after `pnl_engine.update` (`loop.py:72`) and `risk_engine.check` (`loop.py:92`), i.e. after both Financial Accounting and Risk Evaluation, consistent with ADR-010's own step 11 assignment.
- `pnl.py:9-40`: `PnLEngine.update(trade_event, entry_basis)` already gates on `event_type in {"TRADE_CLOSED", "PARTIAL_CLOSE"}`, returning `0.0` for every other case (including `None`, `TRADE_OPENED`, `SCALE_IN`, `RUNTIME_FAILURE_EVENT`) - the *same* `trade_event` object `PerformanceEngine.update` receives one call later in the same tick already determined, via this exact gate, whether `pnl` is a genuine realized-outcome value or a structural `0.0`.
- `trade_lifecycle.py:50-78`: `on_execution` returns `None` outright for `action == "HOLD"`, before any event-generating branch; `_open_trade`/`_scale_in`/`_partial_close`/`_full_close`/`_failure_event` each generate exactly one, distinctly-typed, frozen `LifecycleEvent` (`event_type` in `{TRADE_OPENED, SCALE_IN, PARTIAL_CLOSE, TRADE_CLOSED, RUNTIME_FAILURE_EVENT}`); `LifecycleEvent` additionally carries `trade_id`, `side`, `price`, `entry_price`, `closed_quantity`, and eight other fields, all already computed and available at the call site, none currently read by `PerformanceEngine`.
- `execution/executor.py:5-32`: `Executor.execute` returns `status` in `{BUY_EXECUTED, SELL_EXECUTED, NOOP}`, computed from `decision['action']` alone; `NOOP` occurs precisely when `action` is not `BUY`/`SELL`, i.e. exactly the same condition under which `on_execution` returns `None` and no `LifecycleEvent` is generated at all.
- `canonical_state.py:48,96-98`; `canonical_enforcer.py:79-85`: the existing Writer-on-Behalf-Of publication chain for `performance_metrics`, already P3-02-certified for object-identity discipline (`_stats_snapshot()`, `performance.py:36-37`), unchanged since P3-02's own Final Certification.
- `run_engine/runtime/performance_analytics.py`, `run_engine/execution/adapter.py`, `run_engine/feedback/tracker.py`, `run_engine/runtime/strategy_memory.py`, and `StrategySelector.update` (`strategy.py:77-93`): all five re-confirmed unreferenced/uncalled by any active file (SDA Section 6, CGA Section 5, CGA Section 25).
- A supplementary repository-wide search for `realized_pnl`, `unrealized_pnl`, `authority` (beyond the CGA's own already-completed search) confirms: no `unrealized_pnl` identifier exists anywhere in `run_engine/`; `PnLEngine`'s own realized value is passed as a bare `pnl` parameter with no distinguishing name; `authority`-bearing doc-comments occur only in `risk.py` and `trade_lifecycle.py` (already cited, CGA Section 5), confirming no additional Computational-Authority claim exists anywhere touching Performance beyond `PerformanceEngine` itself.

**The seven essential Capability Gaps, re-confirmed unchanged before any decision is made:** CAP-005 (Decision-Keyed Attribution, MISSING), CAP-006 (Lifecycle-Outcome-Based Attribution, aggregate, MISSING), CAP-007 (Decision-versus-Outcome Separation, MISSING), CAP-008 (Execution-Status Visibility, MISSING), CAP-013 (Lifecycle-Transition-Aware Attribution, MISSING), CAP-017 (Performance History, MISSING), CAP-025 (TD-004 Closure Readiness, aggregate, MISSING); plus the five PARTIAL capabilities CAP-009 (Lifecycle-Event Visibility), CAP-010 (Realized-PnL Attribution), CAP-012 (Equity/Drawdown Input Boundary), CAP-018 (Reporting Readiness), CAP-029 (Verification Coverage).

**FRA findings, re-confirmed unchanged: FG-001 through FG-005** (traceable to CAP-005/006/007/008, CAP-010, CAP-017, CAP-005/006/007, CAP-013 respectively); **VCF-001 through VCF-004** (Structural Independence; Writer-on-Behalf-Of pattern; determinism; RUNTIME_FAILURE_EVENT non-mutation); **DG-001, DG-002** ("Reporting" unconfirmed; ADR-008 does not define "Completed Lifecycle Outcome" as a schema); **VG-001** (no automated test); **RR-001** (orphaned `StrategySelector.update`), **RR-002** (inactive `performance_analytics.py`, latent duplicate-authority risk).

## 6. Scientific Definitions

Restated, not newly invented, from the Architecture Baseline, the P3-02 Architecture, and the FRA/SDA/CGA, governing the rest of this document: **Single Source of Truth, Authoritative Owner, Computational Authority, Writer-on-Behalf-Of, Canonical Storage, Derived View, Canonical Working State, Tick-Complete Snapshot, Structural Independence, Composite Isolation** - as defined in the Architecture Baseline and the certified P3-02 Architecture, unchanged.

**Decision** (restated from the SDA, Section 15) - an intention: the tick's own chosen `action`, computed by `StrategySelector.decide` before `Executor.execute` runs.

**Execution** (restated) - the Executor's own outcome for a Decision, carrying `status` in `{BUY_EXECUTED, SELL_EXECUTED, NOOP}`.

**Lifecycle Transition / Lifecycle Event** (restated) - the authoritative historical fact of what happened to a trade's own lifecycle, produced exclusively by `TradeLifecycleEngine`, one of `{TRADE_OPENED, SCALE_IN, PARTIAL_CLOSE, TRADE_CLOSED, RUNTIME_FAILURE_EVENT}`.

**Financial Outcome / Realized PnL** (restated) - the realized financial consequence of a Lifecycle Transition, computed exclusively by `PnLEngine`, nonzero only for `PARTIAL_CLOSE`/`TRADE_CLOSED`.

**Trade Outcome** (introduced by this document) - the combination of a single accepted Lifecycle Transition of type `PARTIAL_CLOSE` or `TRADE_CLOSED` together with the Realized PnL `PnLEngine` computes for that same transition, within the same tick. A Trade Outcome is the fundamental accounting unit this Architecture adopts for Performance (AD-001).

**Completed Lifecycle Outcome** (introduced by this document, resolving Documentation Gap DG-002) - a precise, concrete synonym for Trade Outcome: an accepted `LifecycleEvent` whose own `event_type` is `PARTIAL_CLOSE` or `TRADE_CLOSED`. This is the exact schema ADR-008's own prose ("completed lifecycle events, realized financial outcomes") left undefined; this document supplies the missing definition without altering ADR-008's own text.

**Performance Observation** (introduced by this document) - the act of `PerformanceEngine` recognizing exactly one Trade Outcome and folding its own Realized PnL into the Current Aggregate and, if the History Model is implemented, appending one Performance History Record.

**Current Aggregate** (introduced by this document) - the existing published, per-key running-statistics object (`self.stats`-shaped: `{key: {pnl, trades, winrate}}`), re-keyed under this Architecture per AD-004, retaining its own already-certified Tick-Stable lifetime and Structural Independence (P3-02-AD-005, IU-002, not reopened).

**Performance History Record** (introduced by this document, Section 15) - a single, immutable, Historical-lifetime record of one Performance Observation, distinct in object and lifetime from the Current Aggregate.

## 7. Architecture Problem Statement

The CGA found seven capabilities MISSING (CAP-005, CAP-006, CAP-007, CAP-008, CAP-013, CAP-017, CAP-025 - the last two aggregate syntheses) and five PARTIAL (CAP-009, CAP-010, CAP-012, CAP-018, CAP-029), all clustering around exactly one root cause the FRA and SDA already isolated: `PerformanceEngine.update` currently keys, gates, and counts every Performance statistic by the tick's own raw Decision (`decision.get('action', 'HOLD')`), not by a completed Lifecycle Outcome, directly contradicting ADR-008's own Decision text, Rule OM-008's own second sentence, Baseline AC-008, ADR-002's own Runtime Event hierarchy, and AC-014's own Lifecycle Semantics requirement (SDA DEP-032, DEP-036, DEP-037, DEP-042, DEP-046, DEP-047). This document exists to resolve every one of these, to formally ratify the seventeen already-COMPLETE capabilities as a binding architectural contract, and to convert the CGA's own remaining open items into a single, internally consistent target architecture - without reopening P3-01's own certified ordering, P3-02's own certified isolation mechanisms, or P2-02A/P2-03/P2-04's own certified ownership contracts, and without designing Reporting, Persistence, Recovery, or Operator Control.

## 8. Architecture Objectives

1. Define the normative Performance Semantic Source as a Completed Lifecycle Outcome (`PARTIAL_CLOSE`/`TRADE_CLOSED`), resolving CAP-005, CAP-006, CAP-007, and Documentation Gap DG-002.
2. Establish a structural, non-special-cased Decision-versus-Outcome separation that naturally, automatically excludes HOLD, NOOP, and `RUNTIME_FAILURE_EVENT` from ever producing a Performance Observation, resolving CAP-008, CAP-014, CAP-015, Functional Gaps FG-001 and FG-004.
3. Resolve Performance Keying to a single, unambiguous Primary Aggregation Key (Position Side), with Trade Identity serving a distinct, non-competing role (History Record identity, not aggregation), resolving CAP-013 and Functional Gap FG-005.
4. Re-attribute the already-correct, already-certified Realized PnL value to the corrected accounting unit without altering `PnLEngine`'s own formula, resolving CAP-010 and Functional Gap FG-002.
5. Explicitly, narrowly bound Performance's own Financial read-set to exclude Unrealized PnL, Equity, and Drawdown, ratifying CAP-011 and closing CAP-012's own interpretive ambiguity.
6. Define a Performance History Model that separates the Current Aggregate from individual Performance History Records, neither stored in `CanonicalState`, both derived from `TradeLifecycleEngine`'s and `PnLEngine`'s own already-authoritative sources, resolving CAP-017 and Functional Gap FG-003.
7. Define a Reporting Boundary and Consumer Contract without implementing a Reporting module, resolving CAP-018 and Documentation Gap DG-001.
8. Ratify every already-COMPLETE property (Ownership structure, Publication mechanics, Ordering compliance, Unrealized-PnL exclusion, HOLD handling, Failure conformance, Formula integrity, Determinism, Replay, Structural Independence, Cross-Tick stability, Alternative-Path exclusivity, Cross-Unit boundaries - CAP-001 through CAP-004, CAP-011, CAP-014 through CAP-016, CAP-019 through CAP-024, CAP-026 through CAP-028) exactly as currently evidenced, introducing no change.
9. Establish, without specifying, the verification obligation for the corrected accounting behaviour (CAP-029), deferred to the Specification stage.
10. Architecturally close TD-004 (CAP-025) within this unit's own scope, explicitly not yet marking the Technical Debt Register closed, pending Implementation and Final Certification.

## 9. Performance Semantic Source Model

The normative basis of a Performance Observation SHALL be a Completed Lifecycle Outcome (Section 6): a `LifecycleEvent` whose own `event_type` is `PARTIAL_CLOSE` or `TRADE_CLOSED`, together with the `pnl` scalar `PnLEngine.update` computes for that same event within the same tick (AD-001). Neither the raw Decision, nor the Executor's own `status`, nor an accepted-but-not-yet-realized Lifecycle Transition (`TRADE_OPENED`, `SCALE_IN`) constitutes, on its own, a normative basis for a Performance Observation. This resolves the governing task's own item 1 by selecting "akzeptierte Lifecycle Transition" narrowed further to "Trade Closure" (Partial or Full) specifically, per ADR-008's own explicit Decision text, not the broader class of every accepted transition.

## 10. Decision / Execution / Lifecycle / Outcome Model

Four strictly distinct concepts govern every Performance-relevant tick, restated from Section 6 and bound as an architectural model (AD-002): a **Decision** is an intention, never itself a Trade Outcome; an **Execution** is the Executor's own outcome for a Decision, never itself an accepted Lifecycle Transition; an accepted **Lifecycle Transition** (`TRADE_OPENED`, `SCALE_IN`) is never itself a realized **Trade Outcome** unless its own `event_type` is `PARTIAL_CLOSE` or `TRADE_CLOSED`; HOLD and NOOP are never Trades under any circumstance; a Rejection or `RUNTIME_FAILURE_EVENT` is never counted as a successful Trade under any circumstance. No stage in this chain is skipped or conflated by any decision in this document.

## 11. Trade Recognition Model

A Trade, for Performance purposes, begins at `TRADE_OPENED` (no Performance Observation is generated at this point, since no Realized PnL exists yet); continues or scales at `SCALE_IN` (no Performance Observation is generated); is partially closed at `PARTIAL_CLOSE` (a Performance Observation IS generated, since Realized PnL is generated for the closed portion, per ADR-008's own explicit text; the lifecycle remains active); is fully closed at `TRADE_CLOSED` (a Performance Observation IS generated; the lifecycle terminates exactly once, per ADR-009). Trade Identity (`trade_id`, already a field of every `LifecycleEvent`) is preserved and carried into every Performance Observation and, if generated, its own Performance History Record, but does not itself gate whether an Observation occurs (AD-006).

## 12. Realized-PnL Attribution Model

Each Performance Observation consumes exactly the `pnl` scalar value `PnLEngine.update` already computes, within the same tick, for the same `trade_event` `PerformanceEngine.update` receives (AD-007). No new Financial input is introduced; `PnLEngine` remains the unchanged, exclusive Computational Authority for Realized PnL (P2-03, not reopened). Partial-Close PnL and Full-Close PnL are each attributed to their own respective Performance Observation individually (one Observation per Completed Lifecycle Outcome, Section 9); cumulative Realized PnL (`realized_pnl_cumulative`, `CanonicalState`'s own already-certified P2-03 field) remains entirely separate from, and is not read or duplicated by, Performance's own per-Observation `pnl` consumption.

## 13. Performance Keying Model

The Primary Aggregation Key for the Current Aggregate SHALL be Position Side (`trade_event.side`, `"LONG"` or `"SHORT"`), read directly from the same `LifecycleEvent` already available at the call site (AD-004). This is a single, unambiguous key: exactly one value is available per Observation, with no possibility of competing or simultaneous values. Trade Identity (`trade_id`) serves a distinct, non-competing function: Performance History Record identity and cross-Observation traceability for a multi-partial-close Trade (Section 15), not Current-Aggregate bucketing. Decision Action, Execution Status, and Regime are explicitly evaluated and rejected as Primary Aggregation Key candidates: Decision Action is the exact defect this Architecture corrects (AD-002); Execution Status is redundant once the Lifecycle Event Type gate (Section 9) already determines Observation eligibility (AD-003); Regime and Strategy Identity are not required by any Functional Requirement, Dependency, or Capability, and introducing either as a keying dimension would constitute unevidenced scope expansion (AD-004's own Scope Boundary).

## 14. Performance Aggregation Model

The fachliche unit aggregated is the Trade Outcome (Section 6). Exactly one class of event increases the Current Aggregate's own count field: an accepted `PARTIAL_CLOSE` or `TRADE_CLOSED` LifecycleEvent (AD-009). Win-rate is updated, using the identical `pnl > 0` test the current formula already uses, exactly once per such event, evaluated against that event's own attributed `pnl` (Section 12). Every observation folded into the Current Aggregate carries a genuine, non-zero-by-construction-possible realized `pnl` value in the general case (a break-even close producing exactly `0.0` remains a valid, correctly-counted non-win Observation, not an excluded one - Baseline AC-008 requires Win Rate derive "exclusively from realized outcomes," not that every realized outcome be profitable). HOLD, NOOP, an accepted-but-not-yet-realized Lifecycle Transition (`TRADE_OPENED`, `SCALE_IN`), a Rejection, and a `RUNTIME_FAILURE_EVENT` each produce zero Current-Aggregate mutation, structurally, by virtue of not satisfying the Section 9 gate - no special-case branch is required for any of these five conditions individually (Section 19, Section 20). Multiple counting is prevented structurally: each `LifecycleEvent` is generated at exactly one call site (already-certified, AI-008/ADR-002, P3-02-AD-010, not reopened) and consumed exactly once by `PerformanceEngine.update` within the same tick; no replay or reprocessing of an already-consumed event occurs anywhere in the active trace.

## 15. Performance History Model

A Performance History Record fachlich represents one Performance Observation: at minimum, the Trade Identity, the Lifecycle Event Type (`PARTIAL_CLOSE` or `TRADE_CLOSED`), the Position Side, the attributed Realized PnL, and the originating Runtime Tick, sufficient to reproduce the Current Aggregate's own running statistics by replay (AD-010, resolving AC-008's own third clause and Functional Gap FG-003). The authoritative source of the underlying facts is `TradeLifecycleEngine`'s own already-immutable Lifecycle History (AI-004, not reopened) together with `PnLEngine`'s own already-certified Realized PnL computation (P2-03, not reopened); a Performance History Record is a Derived View of these two sources, not a competing Authoritative Owner of either. The Current Aggregate and Performance History Records SHALL be two distinct objects with two distinct lifetimes: the Current Aggregate remains Tick-Stable (P3-02's own Information Lifetime Model, Section 12, not reopened); Performance History Records possess the Historical lifetime, permanently retained once recorded, analogous to, but not merged with, `TradeLifecycleEngine`'s own Lifecycle History. Performance History Records SHALL NOT be stored inside `CanonicalState`, consistent with AI-001 and AI-012 (Operational/Historical Separation, not reopened): `CanonicalState` owns operational truth only; Historical information, including Performance History, remains outside it. This model does not select a concrete storage mechanism, retention policy, or persistence layer (ADR-012, Deferred Scope, not reopened); it establishes only the fachliche shape, source, and lifetime boundary a future Specification must implement.

## 16. Current Aggregate Model

The Current Aggregate SHALL retain the already-certified publication mechanics P3-02 established: `PerformanceEngine` (Computational Authority) constructs a Structurally Independent value at every nesting level (P3-02-AD-005, IU-002, not reopened) on every tick that produces a Performance Observation; `CanonicalEnforcer.apply_performance_metrics` (Writer-on-Behalf-Of, AD-011) publishes it unchanged into `CanonicalState.state["performance_metrics"]` (Authoritative Owner) and the tick-result dict's own `"performance"` field, exactly as today. On a tick that produces no Performance Observation (HOLD, NOOP, non-closing Lifecycle Transition, Rejection, `RUNTIME_FAILURE_EVENT`), the Current Aggregate's own published value SHALL remain the most recently computed snapshot, unchanged in content, structurally re-published (or read-through, per the existing `apply_performance_metrics(None)` guard) exactly as the current runtime already, correctly, behaves for its own Tick-Stable publication contract.

## 17. Reporting Boundary Model

Performance SHALL guarantee, as a Consumer Contract, that the published Current Aggregate (Section 16) and, once implemented, Performance History Records (Section 15) are well-formed, Structurally Independent, and semantically correct per every decision in this document - sufficient for any future Reporting consumer to build against, without P3-03 itself implementing that consumer (AD-012). "Reporting" SHALL remain the Runtime Ownership Matrix's own named Primary Consumer designation for Performance Metrics, not reclassified as stale documentation (resolving Documentation Gap DG-001): its own concrete implementation, UI, export mechanism, and persistence layer remain explicitly out of P3-03's own scope. The minimum information P3-03 SHALL guarantee available for a future Reporting consumer is: the Current Aggregate's own per-Position-Side statistics, and, once the History Model (Section 15) is implemented, the complete, ordered sequence of Performance History Records. No UI, export format, or persistence question is decided here.

## 18. Ownership and Publication Model

`PerformanceEngine` SHALL remain the exclusive Computational Authority for Performance Metrics; `CanonicalState` SHALL remain the exclusive Authoritative Owner of the Current Aggregate; `CanonicalEnforcer` SHALL remain the exclusive Writer-on-Behalf-Of (AD-013, ratifying CAP-001, CAP-002, CAP-003, not reopened). Neither `StrategySelector` (including its own orphaned `update` method) nor `run_engine/runtime/performance_analytics.py` SHALL possess, or be granted, any Computational Authority for Performance Metrics under this Architecture (AD-019, ratifying CAP-023, CAP-024). "Reporting" remains the intended, not-yet-implemented Primary Consumer (Section 17). This model introduces no new Authoritative Owner and no new Computational Authority for any runtime object.

## 19. HOLD and NOOP Model

A HOLD Decision, and the NOOP Execution it produces, SHALL continue to generate no `LifecycleEvent` at all (`on_execution`'s own existing `None`-return behaviour for `action == "HOLD"`, not reopened). Consequently, under the Section 9 Performance Semantic Source Model, a HOLD/NOOP tick structurally, automatically produces zero Performance Observations, with no special-case branch required anywhere in `PerformanceEngine`'s own logic (AD-015). HOLD and NOOP SHALL NOT increase Trade Count, SHALL NOT affect Win Rate, and SHALL NOT be recorded as a Performance History Record (Section 15); a complete, tick-by-tick diagnostic trail including HOLD ticks, if ever required, remains a separate Logging/Diagnostics concern (`run_engine/logging/`), explicitly out of Performance's own scope.

## 20. Rejection and Runtime Failure Event Model

A Rejection SHALL NOT be counted as a successful Trade under any circumstance; a `RUNTIME_FAILURE_EVENT` SHALL NOT generate a Performance Observation and SHALL NOT mutate the Current Aggregate (AD-016, ratifying P3-01-AD-006, P3-01-AI-012, not reopened). Under the Section 9 gate, a `RUNTIME_FAILURE_EVENT` fails the `event_type in {PARTIAL_CLOSE, TRADE_CLOSED}` test structurally, exactly as HOLD/NOOP does; the current runtime's own explicit `if event_type == "RUNTIME_FAILURE_EVENT": return snapshot` short-circuit becomes a redundant special case of the same general gate, not a separately-required mechanism - a strict simplification, not merely a preservation, of the current failure-path logic. A `RUNTIME_FAILURE_EVENT` MAY still be recorded for diagnostic purposes by `TradeLifecycleEngine`'s own already-existing `failure_events` list (AI-004, not reopened); this is unaffected by, and not duplicated into, Performance History.

## 21. Failed-Tick Model

A Failed Tick (an exception interrupting `RunLoop.step()` before Tick Completion, P3-01-AD-004, not reopened) SHALL continue to produce no Tick-Complete result at all; consequently, no Performance update of any kind becomes externally observable for a Failed Tick, regardless of whether `PerformanceEngine.update` itself was reached before the interrupting exception (AD-017). Whatever internal `CanonicalEnforcer.apply_*` calls already completed before the exception remain present in `CanonicalState`'s own internally-held state, exactly as P3-02-AD-016 already establishes, not reopened. Residual Risk RR-002 (Post-Exception Financial/Lifecycle Divergence) SHALL remain an open, non-blocking, documented Residual Risk; this document does not resolve it, does not silently present it as resolved, and does not introduce a rollback, reset, or transaction mechanism for it or for any other component's own cross-tick state.

## 22. Determinism and Replay Model

Given identical Lifecycle and Financial Outcomes applied in an identical order, `PerformanceEngine`'s own Performance Observations, Current Aggregate values, and (once implemented) Performance History Records SHALL be functionally identical across independent replays (AD-018, ratifying CAP-019, CAP-020, extending their own already-certified scope to the corrected accounting mechanism). The corrected aggregation mechanism introduces no randomness, wall-clock read, or I/O, matching the current implementation's own already-conformant property. Performance History's own record order SHALL be deterministic, matching the deterministic order in which `TradeLifecycleEngine` itself already generates the underlying `LifecycleEvent` sequence (AI-005, AI-006, not reopened). P3-02's own Snapshot Isolation and Structural Independence guarantees (Section 16) remain fully preserved by this model; no decision in this document reduces or bypasses them.

## 23. Alternative Performance Path Model

Exactly one active Performance computation path remains architecturally permitted under this Architecture: `PerformanceEngine`, invoked exclusively from `RunLoop.step()` (AD-019). The following five paths are individually, explicitly classified, none reactivated, none deleted, none granted any Computational Authority:

| Path | Status | Authority | Future Role |
|---|---|---|---|
| `run_engine/runtime/performance_analytics.py` | Inactive, unreferenced | None | MAY be consulted as prior art for future keying discussions only; not adopted by this Architecture (AD-004 selects Position Side, not its own `(regime, action)` scheme); disposition otherwise forwarded to a future Repository Consolidation |
| `StrategySelector.update(decision, pnl, regime)` | Inactive (orphaned method, active file) | None | Remains dormant; its own eventual disposition (deletion or repurposing as a Strategy-feedback mechanism distinct from Performance) remains an open question, not decided here |
| `run_engine/feedback/tracker.py` | Inactive, unreferenced | None | Unaffected by this Architecture; disposition forwarded |
| `run_engine/runtime/strategy_memory.py` | Inactive, unreferenced | None | Unaffected by this Architecture; disposition forwarded |
| `run_engine/execution/adapter.py` | Inactive, unreferenced | None | Unaffected by this Architecture; disposition forwarded |

No decision in this document reactivates, integrates, or deletes any of the five paths above; each remains classified exactly as the CGA's own Section 25 (Alternative-Path Assessment) already established.

## 24. Cross-Unit Boundary Model

Seven items are formally ratified as outside this unit's own resolution scope (AD-021): P3-01's own twelve-stage ordering, Tick-Complete Publication semantics, HOLD semantics, and Failed-Tick semantics remain entirely unchanged, not reopened. P3-02's own Composite Isolation and Structural Independence mechanisms remain entirely unchanged, preserved as a binding constraint on every decision in Section 25, not reopened. P2-03's own Financial Ownership (PnLEngine's own formula and Realized-PnL computation) remains entirely unchanged; only Performance's own downstream attribution of an already-correct value changes. P2-04's own Risk Ownership remains entirely unchanged; no new Performance-Risk dependency is introduced in either direction. TD-007 (RunLoop Lifecycle Control Surface) remains a future Runtime Control Unit's own scope, not conflated with this Architecture's own Failed-Tick or Rejection models. Reporting implementation, persistence, and external evaluation remain out of scope (Section 17). Scientific Strategy Evaluation or optimization (any use of Performance Metrics to adjust `StrategySelector`'s own weights) remains out of scope; the orphaned `StrategySelector.update` method is explicitly not reconciled or reactivated by this document (Section 23).

## 25. Architecture Decisions

### P3-03-AD-001 - Performance Semantic Source

**Titel.** Performance Semantic Source: Completed Lifecycle Outcome as the Normative Basis.

**Motivation.** CAP-005, CAP-006, and CAP-007 (all MISSING) found `PerformanceEngine.update`'s own accounting keyed and gated by the raw Decision (`decision.get('action', 'HOLD')`), directly contradicting ADR-008's own Decision text ("Performance SHALL be derived exclusively from: completed lifecycle events, realized financial outcomes... rather than: Runtime Decision"), Rule OM-008's own second sentence, and Baseline AC-008.

**Decision.** The normative basis of a Performance Observation SHALL be a Completed Lifecycle Outcome: an accepted `LifecycleEvent` whose own `event_type` is `PARTIAL_CLOSE` or `TRADE_CLOSED`, together with the `pnl` scalar `PnLEngine.update` computes for that same event within the same tick. No Performance Observation SHALL be generated from a raw Decision, an Execution outcome alone, or a non-closing Lifecycle Transition (`TRADE_OPENED`, `SCALE_IN`).

**Scientific Justification.** ADR-008's own Decision text explicitly names "completed lifecycle events" and "realized financial outcomes" as the exclusive basis; `PARTIAL_CLOSE` and `TRADE_CLOSED` are precisely, and exhaustively, the two `LifecycleEvent` types `PnLEngine.update` itself already recognizes as realized-outcome-generating (`pnl.py:23`), making this the minimal, already-evidenced definition consistent with both ADR-008's own text and the existing, certified `PnLEngine` gate - no new Financial computation or event taxonomy is introduced.

**Performance-Semantic Consequences.** Performance's own accounting key is derived exclusively from information already present on `trade_event`, never from `decision`; this directly resolves Functional Gaps FG-001 and FG-004.

**Lifecycle Consequences.** `TRADE_OPENED` and `SCALE_IN` remain valid, recorded Lifecycle transitions (owned exclusively by `TradeLifecycleEngine`, unchanged) but produce no Performance Observation, consistent with ADR-008's own text naming only Partial and Full Close as performance-contributing.

**Financial Consequences.** None; `PnLEngine`'s own formula, gate, and output are entirely unchanged (P2-03, not reopened).

**Ownership Consequences.** None; `PerformanceEngine` remains the exclusive Computational Authority, `CanonicalState` the exclusive Authoritative Owner.

**Producer Consequences.** `PerformanceEngine` becomes a conditional producer: it generates a new Performance Observation only when the Section 9 gate is satisfied, rather than unconditionally on every tick.

**Consumer Consequences.** Any consumer of the Current Aggregate now observes values that change only on genuine Trade Outcomes, not on every tick.

**Publication Consequences.** The publication mechanism itself (`CanonicalEnforcer.apply_performance_metrics`) is unchanged; only the frequency and semantic correctness of what is published changes.

**History Consequences.** Establishes the exact trigger condition Section 15's own Performance History Model uses to determine when a History Record is appended.

**Failure Consequences.** A `RUNTIME_FAILURE_EVENT` structurally fails this gate, consistent with AD-016.

**Determinism Consequences.** None beyond AD-018's own already-stated consequences; the gate itself is a pure function of `trade_event.event_type`.

**Compatibility Constraints.** Does not alter `PnLEngine`'s own formula, `TradeLifecycleEngine`'s own event generation, or any P2-02A/P2-03/P2-04 certified contract.

**Acceptance Criteria.** For any tick where `trade_event.event_type` is not `PARTIAL_CLOSE` or `TRADE_CLOSED`, the Current Aggregate's own `trades` and `winrate` values remain unchanged from their own immediately-prior tick's own values.

**Traceability.** FR-005, FR-006, FR-007, FR-010, FR-012; DEP-003 through DEP-011, DEP-020, DEP-032, DEP-036, DEP-037, DEP-047; CAP-005, CAP-006, CAP-007; ADR-008; Rule OM-008; Baseline AC-008; Functional Gaps FG-001, FG-004; Documentation Gap DG-002.

**Scope Boundary.** Does not select a concrete Python mechanism for the gate; does not alter which `LifecycleEvent` fields exist; does not redesign `TradeLifecycleEngine`.

---

### P3-03-AD-002 - Decision-versus-Outcome Separation

**Titel.** Decision-versus-Outcome Separation: A Formal, Binding Invariant.

**Motivation.** CAP-007 (MISSING) found no structural mechanism distinguishing a Decision from a realized Outcome anywhere in `PerformanceEngine.update`'s own method body; the SDA's own Decision-versus-Outcome Analysis (SDA Section 15) established the scientific chain this decision formalizes.

**Decision.** A Decision SHALL NOT, by itself, constitute an Execution Outcome. An Execution SHALL NOT, by itself, constitute an accepted Lifecycle Transition. An accepted Lifecycle Transition SHALL NOT, by itself, constitute a realized Trade Outcome unless its own `event_type` is `PARTIAL_CLOSE` or `TRADE_CLOSED` (AD-001). HOLD and NOOP SHALL NOT be treated as Trades under any circumstance. A Rejection and a `RUNTIME_FAILURE_EVENT` SHALL NOT be counted as a successful Trade under any circumstance.

**Scientific Justification.** This restates, as a binding architectural invariant rather than a mere observation, the four-concept separation the SDA's own Section 15 already established from direct repository evidence: a Decision produces no Execution whenever the Executor returns `NOOP`; an Execution produces no accepted Lifecycle transition whenever `TradeLifecycleEngine`'s own validation fails; a tick produces no trade activity at all for HOLD or validation-failure cases.

**Performance-Semantic Consequences.** Every future Architecture, Specification, or Implementation decision touching Performance must explicitly identify which of the four concepts (Decision, Execution, Lifecycle Transition, Trade Outcome) it operates on, never conflating two.

**Lifecycle Consequences.** None beyond AD-001's own already-stated consequences.

**Financial Consequences.** None.

**Ownership Consequences.** None.

**Producer Consequences.** None beyond AD-001's own already-stated consequences.

**Consumer Consequences.** None beyond AD-001's own already-stated consequences.

**Publication Consequences.** None.

**History Consequences.** None beyond AD-001's own already-stated consequences.

**Failure Consequences.** Directly grounds AD-016's own Rejection/Runtime-Failure-Event exclusion.

**Determinism Consequences.** None.

**Compatibility Constraints.** None beyond what AD-001 already establishes.

**Acceptance Criteria.** No section of any future P3-03 Specification or Implementation document uses "Decision," "Execution," "Lifecycle Transition," or "Trade Outcome" interchangeably; each of the four terms, when used, refers exactly to its own Section 6 definition.

**Traceability.** FR-005, FR-012; DEP-011, DEP-027, DEP-036, DEP-047, DEP-053; CAP-007; SDA Section 15; Functional Gaps FG-001, FG-004.

**Scope Boundary.** Does not itself gate any specific runtime behaviour beyond what AD-001 already defines; a terminological and invariant-level decision.

---

### P3-03-AD-003 - Execution-Status Visibility Resolution

**Titel.** Execution-Status Visibility: Lifecycle Event Type Suffices, No New Input Required.

**Motivation.** CAP-008 (MISSING) found `PerformanceEngine` has no visibility into the Executor's own `status`; naively, this could be resolved by adding `execution` as a fifth input parameter.

**Decision.** `PerformanceEngine` SHALL NOT require direct visibility into the Executor's own `status` field. The Section 9 Lifecycle Event Type gate (`event_type in {PARTIAL_CLOSE, TRADE_CLOSED}`) already, transitively, implies an accepted Execution occurred, since `TradeLifecycleEngine` only generates these two event types from `_handle_buy`/`_handle_sell`, themselves only reached for a non-HOLD, validated Execution. No new input parameter carrying Execution-status information is required by this Architecture.

**Scientific Justification.** Direct repository tracing (Section 5) confirms `PARTIAL_CLOSE`/`TRADE_CLOSED` generation is unreachable except via an already-accepted, already-validated Execution; requiring `PerformanceEngine` to additionally, redundantly inspect `execution.status` would duplicate information already, transitively, encoded in `trade_event.event_type`, violating this governance chain's own minimality principle (AI-013) and Rule IF-001 ("information already produced upstream shall never be reconstructed downstream" - reconstructing Execution-acceptance from a second, redundant source once the Lifecycle layer already encodes it).

**Performance-Semantic Consequences.** Closes CAP-008 without introducing a new Producer-Consumer relationship between `Executor` and `PerformanceEngine`.

**Lifecycle Consequences.** Reinforces that `LifecycleEvent`'s own `event_type` is the single, sufficient signal for Trade Outcome recognition.

**Financial Consequences.** None.

**Ownership Consequences.** None.

**Producer Consequences.** `Executor` gains no new consumer; its own `status` field remains consumed only by `TradeLifecycleEngine` (to determine `action`) as today.

**Consumer Consequences.** `PerformanceEngine` remains a consumer of exactly `trade_event` and `pnl` for Trade Outcome recognition, not `execution`.

**Publication Consequences.** None.

**History Consequences.** None beyond AD-001's own already-stated consequences.

**Failure Consequences.** None beyond AD-016's own already-stated consequences.

**Determinism Consequences.** None.

**Compatibility Constraints.** Does not alter `Executor.execute`'s own return value or behaviour.

**Acceptance Criteria.** No future P3-03 Specification introduces `execution` as an input to Performance's own accounting logic; every Trade Outcome recognition decision is demonstrably derivable from `trade_event.event_type` alone.

**Traceability.** FR-012; DEP-011, DEP-045, DEP-053; CAP-008; Rule IF-001; AI-013; Functional Gap FG-001.

**Scope Boundary.** Does not preclude a future, separately-justified Architecture Evolution Review from introducing Execution-status visibility for an unrelated future purpose; addresses only Performance's own current scope.

---

### P3-03-AD-004 - Performance Keying

**Titel.** Performance Keying: Position Side as the Unambiguous Primary Aggregation Key.

**Motivation.** CAP-013 (MISSING) found no structural distinction between Trade Outcome types; the FRA's own item 3 requires an unambiguous Primary Key, evaluated against eight candidate dimensions (Decision Action, Execution Status, Lifecycle Event Type, Trade Identity, Position Side, Regime, Strategy Identity, Realized Outcome).

**Decision.** The Primary Aggregation Key for the Current Aggregate SHALL be Position Side (`trade_event.side`, `"LONG"` or `"SHORT"`). Trade Identity (`trade_id`) SHALL serve a distinct function - Performance History Record identity (Section 15) - not Current-Aggregate bucketing. Decision Action, Execution Status, Regime, and Strategy Identity SHALL NOT be Primary Aggregation Key dimensions. Lifecycle Event Type SHALL function as the Trigger Condition (AD-001), not an aggregation dimension. Realized Outcome (win/loss) SHALL remain a derived classification within each Position-Side bucket (the existing `wins`/`winrate` mechanism), not an independent keying dimension.

**Scientific Justification.** Position Side is a single, always-available, unambiguous field already present on every Trade-Outcome-generating `LifecycleEvent`, requiring no new computation; it directly replaces the current BUY/SELL-shaped bucket structure with a lifecycle-outcome-derived equivalent of identical shape, minimizing structural change while fully resolving the semantic defect. Decision Action is rejected as the exact defect AD-002 corrects; Execution Status is rejected per AD-003's own redundancy finding; Regime and Strategy Identity are rejected because no Functional Requirement, Dependency, or Capability requires either, and introducing either would constitute unevidenced scope expansion inconsistent with this governance chain's own "keine Spekulation" quality rule.

**Performance-Semantic Consequences.** The Current Aggregate's own bucket structure becomes `{"LONG": {...}, "SHORT": {...}}` in place of `{"BUY": {...}, "SELL": {...}, "HOLD": {...}}`; the HOLD bucket no longer exists, consistent with AD-015 (HOLD produces no Observation at all).

**Lifecycle Consequences.** Directly consumes `trade_event.side`, already computed and available at the call site, no new Lifecycle computation required.

**Financial Consequences.** None.

**Ownership Consequences.** None.

**Producer Consequences.** `PerformanceEngine` reads one additional `LifecycleEvent` field (`side`) beyond `event_type`.

**Consumer Consequences.** Any consumer of the Current Aggregate now observes a Position-Side-keyed structure rather than a Decision-Action-keyed one; this is a semantic shape change any future Reporting consumer must account for (Section 17).

**Publication Consequences.** None beyond the key-shape change itself; the publication mechanism is unchanged.

**History Consequences.** Establishes that Performance History Records (Section 15) carry both Position Side and Trade Identity, each serving its own distinct function.

**Failure Consequences.** None beyond AD-016's own already-stated consequences.

**Determinism Consequences.** None; Position Side is a deterministic field of an already-deterministic event.

**Compatibility Constraints.** Does not alter `TradeLifecycleEngine`'s own `side` computation or `LifecycleEvent`'s own schema.

**Acceptance Criteria.** Every key in the published Current Aggregate is one of exactly `{"LONG", "SHORT"}`; no `"BUY"`, `"SELL"`, or `"HOLD"` key appears in any Current Aggregate published under this Architecture.

**Traceability.** FR-005, FR-008, FR-010; DEP-003, DEP-004, DEP-005, DEP-023, DEP-040; CAP-013; Functional Gap FG-005; ADR-009 (Lifecycle Transition Table, not reopened).

**Scope Boundary.** Does not select a concrete Python dictionary shape or key type; does not preclude a future, separately-justified Architecture Evolution Review from adding a secondary, non-primary classification dimension.

---

### P3-03-AD-005 - Trade Identity and Record Traceability

**Titel.** Trade Identity and Record Traceability: A Non-Aggregating, Traceability-Only Dimension.

**Motivation.** The governing task's own item 4 (Trade Recognition) requires an explicit decision on how Trade Identity is preserved; AD-004 already excludes it from Primary Aggregation Key status, requiring this separate decision on its own actual role.

**Decision.** `trade_id` SHALL be preserved and carried into every Performance Observation and, once the History Model (Section 15) is implemented, its own Performance History Record, enabling reconstruction of which Observations belong to the same underlying Trade (relevant for a Trade with multiple `PARTIAL_CLOSE` events preceding its own eventual `TRADE_CLOSED`). `trade_id` SHALL NOT gate whether an Observation occurs (AD-001 alone governs that) and SHALL NOT be a Current-Aggregate bucketing key (AD-004).

**Scientific Justification.** ADR-009's own Lifecycle Transition Table already establishes `trade_id` as the stable identifier spanning a Trade's own full lifecycle from `TRADE_OPENED` through `TRADE_CLOSED`; preserving it in Performance's own record-level output, without using it for aggregation, gives each of the two - Position Side and Trade Identity - a genuinely independent fachliche function, satisfying the governing task's own explicit requirement that combined dimensions each possess independent purpose.

**Performance-Semantic Consequences.** Enables a future consumer to answer "how many Observations, and how much realized PnL, belong to Trade N" without requiring `trade_id`-keyed aggregation in the Current Aggregate itself.

**Lifecycle Consequences.** Directly consumes `trade_event.trade_id`, already computed and available.

**Financial Consequences.** None.

**Ownership Consequences.** None.

**Producer Consequences.** `PerformanceEngine` reads one additional `LifecycleEvent` field (`trade_id`).

**Consumer Consequences.** A future consumer gains per-Trade traceability without requiring a schema change to the Current Aggregate itself.

**Publication Consequences.** `trade_id` is carried in Performance History Records (Section 15), not in the Current Aggregate's own published structure.

**History Consequences.** Establishes `trade_id` as a mandatory field of every Performance History Record (Section 15).

**Failure Consequences.** None beyond AD-016's own already-stated consequences.

**Determinism Consequences.** None; `trade_id` is a deterministic, monotonically-assigned field of an already-deterministic event.

**Compatibility Constraints.** Does not alter `TradeLifecycleEngine`'s own `trade_id` assignment logic.

**Acceptance Criteria.** Every Performance History Record, once implemented, carries a `trade_id` field matching the originating `LifecycleEvent`'s own `trade_id`.

**Traceability.** FR-007; DEP-008, DEP-020; CAP-013; ADR-009.

**Scope Boundary.** Does not select a concrete History Record schema beyond naming `trade_id` as a mandatory field; does not introduce `trade_id`-based Current-Aggregate bucketing.

---

### P3-03-AD-006 - Trade Recognition Semantics

**Titel.** Trade Recognition: Open / Scale-In / Partial-Close / Full-Close Boundaries for Performance.

**Motivation.** CAP-013 (MISSING) found no distinction between `TRADE_OPENED`, `SCALE_IN`, `PARTIAL_CLOSE`, and `TRADE_CLOSED` anywhere in Performance's own accounting; ADR-008's and ADR-009's own text jointly require these to be treated distinctly.

**Decision.** For Performance purposes: `TRADE_OPENED` and `SCALE_IN` SHALL each be recognized as valid Lifecycle Transitions but SHALL generate no Performance Observation (no Realized PnL exists at either point). `PARTIAL_CLOSE` SHALL generate exactly one Performance Observation, contributing its own Realized PnL, without terminating the underlying Trade (ADR-009, not reopened). `TRADE_CLOSED` SHALL generate exactly one Performance Observation, contributing its own Realized PnL, and marks the Trade's own lifecycle termination (exactly once, per ADR-009). Neither event type increments any counter beyond its own single, corresponding Observation.

**Scientific Justification.** Directly implements ADR-008's own explicit sentence ("Partial Close events SHALL contribute realized performance when realized PnL is generated. Full Close SHALL terminate the lifecycle exactly once.") and ADR-009's own Lifecycle Transition Table, without altering either.

**Performance-Semantic Consequences.** A Trade scaled in twice and partially closed once before its own eventual full close generates exactly two Performance Observations (one `PARTIAL_CLOSE`, one `TRADE_CLOSED`), not four (the two `SCALE_IN` events generate none) and not one (both closing events are individually recognized).

**Lifecycle Consequences.** Directly ratifies ADR-009's own already-certified transition semantics; no change to `TradeLifecycleEngine`'s own state machine.

**Financial Consequences.** Each Observation's own `pnl` is exactly the value `PnLEngine` already computes for that specific closing event, per AD-007.

**Ownership Consequences.** None.

**Producer Consequences.** None beyond AD-001's own already-stated consequences.

**Consumer Consequences.** A consumer observing Trade Count now observes a count of completed Lifecycle Outcomes (Partial and Full Closes combined), not a count of unique Trades - see Section 25, AD-009, for the explicit resolution of this distinction.

**Publication Consequences.** None beyond AD-001's own already-stated consequences.

**History Consequences.** Each Observation, including each of multiple Partial Closes belonging to the same Trade, produces its own distinct Performance History Record (Section 15), individually traceable via `trade_id` (AD-005).

**Failure Consequences.** None beyond AD-016's own already-stated consequences.

**Determinism Consequences.** None; the mapping from `event_type` to Observation-or-not is a pure, deterministic function.

**Compatibility Constraints.** Does not alter ADR-009's own Lifecycle Transition Table or `TradeLifecycleEngine`'s own state machine.

**Acceptance Criteria.** For a scripted sequence of `TRADE_OPENED`, `SCALE_IN`, `PARTIAL_CLOSE`, `TRADE_CLOSED` events belonging to one Trade, the number of resulting Performance Observations equals exactly the number of `PARTIAL_CLOSE` plus `TRADE_CLOSED` events in that sequence, and no more.

**Traceability.** FR-007, FR-010; DEP-008, DEP-011, DEP-046, DEP-050; CAP-013; ADR-008; ADR-009; AC-014; Functional Gap FG-005.

**Scope Boundary.** Does not alter ADR-009's own certified Scale-In/Partial-Close/Full-Close definitions; does not introduce a new Lifecycle event type.

---

### P3-03-AD-007 - Realized-PnL Attribution

**Titel.** Realized-PnL Attribution: Unchanged Formula, Corrected Destination.

**Motivation.** CAP-010 (PARTIAL) found the Realized PnL value itself correct (inherited from `PnLEngine`, P2-03-certified) but its own attribution destination (a Decision-keyed bucket) non-conformant with Baseline AC-008's own second clause.

**Decision.** Each Performance Observation SHALL consume exactly the `pnl` scalar `PnLEngine.update` already computes, within the same tick, for the same `trade_event`. `PnLEngine`'s own formula, gate, and Computational Authority SHALL NOT be altered in any way. The only change is attribution: the same, already-correct `pnl` value is now folded into the Position-Side-keyed bucket (AD-004) corresponding to its own originating Trade Outcome, gated by AD-001, rather than into a Decision-Action-keyed bucket unconditionally.

**Scientific Justification.** The current call site already computes `pnl` and `trade_event` from the identical source within the same tick (`loop.py:72,95`); no new Financial computation, no new `PnLEngine` call, and no formula change is required - only the bucket the already-correct value is folded into changes, the minimal possible fix consistent with the governing task's own explicit instruction not to alter the PnL formula.

**Performance-Semantic Consequences.** Resolves Functional Gap FG-002 (Win Rate dilution) as a direct structural consequence: since `pnl` is now only consumed on a genuine Trade Outcome tick (AD-001), the `wins = 1 if pnl > 0 else 0` test is never evaluated against a structural `0.0` from a non-realizing tick.

**Lifecycle Consequences.** None beyond AD-001's own already-stated consequences.

**Financial Consequences.** None; `PnLEngine.update`'s own formula (`pnl.py:9-40`) is entirely unchanged, preserving P2-03's own certified contract exactly.

**Ownership Consequences.** None; `PnLEngine` remains the exclusive Computational Authority for Realized PnL.

**Producer Consequences.** None; `PnLEngine`'s own production of `pnl` is unaffected.

**Consumer Consequences.** `PerformanceEngine` remains a consumer of the identical `pnl` value it already receives today; only the condition under which it is folded into the aggregate changes.

**Publication Consequences.** None beyond AD-004's own already-stated key-shape consequences.

**History Consequences.** Each Performance History Record's own `pnl` field (Section 15) is exactly the attributed value this decision defines.

**Failure Consequences.** None beyond AD-016's own already-stated consequences.

**Determinism Consequences.** None; attribution is a pure function of already-deterministic inputs.

**Compatibility Constraints.** `PnLEngine.update`'s own formula, gate, and every already-certified P2-03 Acceptance Criterion remain entirely unaltered.

**Acceptance Criteria.** For any tick satisfying the AD-001 gate, the Position-Side bucket's own running `pnl` mean, after the tick, equals the value it would have had if computed directly from the sequence of attributed `pnl` values for that side alone, in tick order.

**Traceability.** FR-006, FR-013, FR-014; DEP-006, DEP-007, DEP-009, DEP-010, DEP-036, DEP-045; CAP-010; ADR-005; ADR-008; Baseline AC-008; P2-03 (not reopened); Functional Gap FG-002.

**Scope Boundary.** Does not alter the running-mean arithmetic formula itself (CAP-016, already COMPLETE, ratified unchanged, Section 25 AD-009); does not reopen P2-03.

---

### P3-03-AD-008 - Unrealized PnL, Equity, and Drawdown Boundary

**Titel.** Unrealized PnL, Equity, and Drawdown: Explicit Exclusion from Performance, Narrow Reading Adopted.

**Motivation.** CAP-011 (COMPLETE) found Unrealized PnL already, correctly excluded from Performance; CAP-012 (PARTIAL) found a genuine, unresolved ambiguity in whether the Target Information Flow's own broader "Financial State" naming requires Equity/Drawdown as additional Performance inputs.

**Decision.** Unrealized PnL SHALL NOT be part of any P3-03 Performance Metric, ratifying the current, already-conformant exclusion. Equity and Drawdown SHALL remain exclusively context/Reporting inputs, available to a future Reporting consumer directly from `CanonicalState` (their own already-certified P2-03/P2-04 publication path), but SHALL NOT be consumed by `PerformanceEngine` itself. Risk Metrics (Drawdown, Drawdown Ratio, `risk_allocation_factor`) SHALL remain consumable begleitinformation for a future Reporting consumer correlating Performance against Risk context, but SHALL NOT influence Performance's own computation in either direction. This resolves CAP-012's own ambiguity by adopting the narrower of the two textually-supportable readings of ADR-008's own "realized financial outcomes."

**Scientific Justification.** ADR-008's own Decision text specifically names "realized financial outcomes" (singular emphasis on realization), not the broader canonical financial state; Equity and Drawdown are themselves partly a function of Unrealized PnL (ADR-006's own Equity formula: `Initial Capital + Realized PnL (cumulative) + Current Unrealized PnL`), so including either as a Performance input would risk reintroducing exactly the Unrealized-PnL contamination AD-008 (this section) explicitly excludes; the narrower reading is therefore the internally consistent one, not merely the more convenient one.

**Performance-Semantic Consequences.** Performance's own read-set remains limited to `trade_event` (event type, side, trade_id) and `pnl` (realized, per-Observation); no `equity`, `peak_equity`, or `drawdown` read is introduced.

**Lifecycle Consequences.** None.

**Financial Consequences.** None; `PnLEngine`'s and `RiskEngine`'s own Equity/Drawdown computations remain entirely unaffected and unconsumed by Performance.

**Ownership Consequences.** None; no new Financial or Risk Ownership is created, consistent with the governing task's own explicit prohibition.

**Producer Consequences.** None.

**Consumer Consequences.** A future Reporting consumer wishing to correlate Performance against Equity/Drawdown context reads both directly from `CanonicalState`, not through Performance's own output.

**Publication Consequences.** None; Performance's own published structure remains exactly Position-Side-keyed statistics (AD-004), with no Equity/Drawdown field.

**History Consequences.** Performance History Records (Section 15) do not carry Equity or Drawdown fields.

**Failure Consequences.** None.

**Determinism Consequences.** None.

**Compatibility Constraints.** Does not reopen P2-03's own Equity/Peak-Equity ownership or P2-04's own Drawdown/`risk_allocation_factor` ownership; introduces no new Performance-to-Risk or Risk-to-Performance dependency.

**Acceptance Criteria.** `PerformanceEngine`'s own method body, at any future HEAD implementing this Architecture, contains no reference to `equity`, `peak_equity`, `drawdown`, or `risk_allocation_factor`.

**Traceability.** FR-006, FR-023; DEP-020, DEP-042, DEP-045; CAP-011, CAP-012; ADR-006; ADR-008; Target Information Flow (Runtime Stage Responsibilities table); P2-03, P2-04 (not reopened).

**Scope Boundary.** Does not preclude a future, separately-justified Architecture Evolution Review from introducing a Risk-aware Performance metric; addresses only this unit's own current scope.

---

### P3-03-AD-009 - Performance Aggregation Semantics

**Titel.** Performance Aggregation Semantics: Trade-Outcome-Counted, HOLD/NOOP/Rejection/Failure-Excluded.

**Motivation.** CAP-006 (MISSING, aggregate) and CAP-016 (COMPLETE, formula-integrity-only) together require an explicit decision on exactly which events increment Trade Count, when Win Rate updates, and how double-counting is prevented, resolving Documentation Gap DG-002's own remaining ambiguity about what "Trade Count" itself means.

**Decision.** Trade Count SHALL equal the count of Completed Lifecycle Outcomes (AD-001): one increment per accepted `PARTIAL_CLOSE` or `TRADE_CLOSED` event, not one increment per unique `trade_id`. This is the literal reading of ADR-008's own text ("Trade Count equals completed lifecycle outcomes"), explicitly distinguished from an alternative "count of unique closed Trades" reading, which `trade_id`-based History reconstruction (AD-005) remains separately available to compute if ever required. Win Rate SHALL update exactly once per Completed Lifecycle Outcome, using the existing `1 if pnl > 0 else 0` test applied to the AD-007-attributed `pnl`. HOLD, NOOP, `TRADE_OPENED`, `SCALE_IN`, a Rejection, and a `RUNTIME_FAILURE_EVENT` SHALL each produce zero effect on Trade Count and Win Rate, structurally, via the AD-001 gate, with no special-case branch required for any of the six conditions individually. Multiple counting SHALL be prevented structurally by the already-certified property that each `LifecycleEvent` is generated at exactly one call site (P3-02-AD-010, not reopened) and consumed exactly once per tick.

**Scientific Justification.** Resolving Documentation Gap DG-002 explicitly, rather than leaving "completed lifecycle outcome" undefined, is necessary before any Specification can define a concrete formula; the outcome-count reading is chosen over the unique-trade-count reading because it is the literal, unambiguous textual reading of ADR-008 itself, requiring no additional interpretive assumption.

**Performance-Semantic Consequences.** A Trade closed via two Partial Closes followed by one Full Close contributes three increments to Trade Count (three Completed Lifecycle Outcomes), not one; this is an explicit, justified architectural choice, not an oversight.

**Lifecycle Consequences.** Directly implements AD-006's own Trade Recognition boundaries.

**Financial Consequences.** None beyond AD-007's own already-stated consequences.

**Ownership Consequences.** None.

**Producer Consequences.** `PerformanceEngine`'s own internal aggregation logic changes its own trigger condition (AD-001) and key (AD-004) but not its own underlying running-mean arithmetic (CAP-016, ratified unchanged, ordinary arithmetic soundness is orthogonal to which inputs are attributed).

**Consumer Consequences.** A consumer reading "Trade Count" must understand it as a count of Completed Lifecycle Outcomes, not unique Trades; this distinction is recorded explicitly in this decision, not left implicit.

**Publication Consequences.** None beyond AD-004's own already-stated consequences.

**History Consequences.** Each incrementing event corresponds to exactly one Performance History Record (Section 15), enabling a future consumer to reconstruct the unique-Trade-count reading via `trade_id` grouping if desired, without requiring the Current Aggregate itself to expose it.

**Failure Consequences.** None beyond AD-016's own already-stated consequences.

**Determinism Consequences.** The running-mean formula itself remains a pure, deterministic function (CAP-016, ratified); this decision does not alter its own mathematical form, only its own trigger and key.

**Compatibility Constraints.** Does not alter the existing running-mean recurrence's own mathematical shape.

**Acceptance Criteria.** For a scripted sequence containing exactly N `PARTIAL_CLOSE`/`TRADE_CLOSED` events and any number of HOLD, NOOP, `TRADE_OPENED`, `SCALE_IN`, or `RUNTIME_FAILURE_EVENT` events interspersed, the resulting Trade Count equals exactly N.

**Traceability.** FR-005, FR-006, FR-007, FR-010, FR-012, FR-013, FR-014; DEP-032, DEP-036, DEP-037, DEP-042, DEP-046, DEP-047, DEP-052; CAP-006, CAP-016; ADR-008; Documentation Gap DG-002; Functional Gaps FG-001, FG-002, FG-004, FG-005.

**Scope Boundary.** Does not specify a concrete Python data structure or formula implementation; does not introduce a unique-Trade-count field in the Current Aggregate itself.

---

### P3-03-AD-010 - Performance History Model

**Titel.** Performance History: Derived, Historical-Lifetime Records, Separate from the Current Aggregate, Not Canonical-State-Stored.

**Motivation.** CAP-017 (MISSING) found no historization mechanism exists anywhere in the repository, active or inactive, contradicting Baseline AC-008's own third clause ("Performance statistics remain reproducible from lifecycle history").

**Decision.** A Performance History Record SHALL be generated for every Performance Observation (AD-001), containing at minimum: `trade_id` (AD-005), `event_type` (`PARTIAL_CLOSE` or `TRADE_CLOSED`), Position Side (AD-004), the attributed `pnl` (AD-007), and the originating Runtime Tick. The authoritative source of the underlying facts SHALL remain `TradeLifecycleEngine`'s own already-immutable Lifecycle History and `PnLEngine`'s own already-certified Realized PnL computation; a Performance History Record is a Derived View of these two sources, never a competing Authoritative Owner of either. The Current Aggregate (AD-004) and Performance History Records SHALL be two distinct objects with two distinct lifetimes: Tick-Stable for the Current Aggregate, Historical for History Records. Performance History Records SHALL NOT be stored inside `CanonicalState`.

**Scientific Justification.** AI-001 (Single Source of Truth) and AI-012 (Operational and Historical Separation) already establish that `CanonicalState` owns operational truth exclusively and that historical information belongs outside it, exactly as Lifecycle History itself is never duplicated into `CanonicalState` (Rule OM-005); Performance History, being historical by its own nature, follows the identical, already-certified pattern rather than requiring a new principle.

**Performance-Semantic Consequences.** Establishes the concrete, minimal schema resolving Documentation Gap DG-002's own "what is a Completed Lifecycle Outcome record" question.

**Lifecycle Consequences.** Performance History Records never replace or duplicate `TradeLifecycleEngine`'s own Lifecycle History; they are strictly additive, derived, and reconstructible from it.

**Financial Consequences.** None beyond AD-007's own already-stated consequences.

**Ownership Consequences.** `PerformanceEngine`, as Computational Authority, MAY retain Performance History Records as its own derived, private working state (analogous to `PositionEngine`'s own already-legitimate cross-tick state, P2-02A-certified, not reopened); this does not constitute a new Authoritative Owner, since the underlying facts remain traceable to `TradeLifecycleEngine`/`PnLEngine`.

**Producer Consequences.** `PerformanceEngine` becomes, additionally, the producer of Performance History Records, a new output distinct from the Current Aggregate.

**Consumer Consequences.** A future Reporting consumer gains access to the ordered sequence of Performance History Records, sufficient to reconstruct the Current Aggregate by replay (Baseline AC-008's own third clause, resolved).

**Publication Consequences.** Performance History Records are NOT published via `CanonicalEnforcer` into `CanonicalState` (Section 15); their own eventual exposure mechanism (a distinct accessor, an event log, or another mechanism) is deferred to the Specification stage.

**History Consequences.** This decision IS the History Consequences of every other decision in this document; every AD's own "History Consequences" field cross-references this decision.

**Failure Consequences.** A Failed Tick produces no Performance History Record, consistent with AD-017.

**Determinism Consequences.** Performance History Record order SHALL be deterministic, matching the deterministic order in which `TradeLifecycleEngine` generates the underlying `LifecycleEvent` sequence (AI-005, AI-006, not reopened).

**Compatibility Constraints.** Does not introduce a Persistence or Recovery mechanism (ADR-012, Deferred Scope, not reopened); does not store any new field inside `CanonicalState`.

**Acceptance Criteria.** The Current Aggregate's own running statistics, for any Position Side, are exactly reproducible by replaying the ordered sequence of Performance History Records for that side through the AD-009 aggregation rule.

**Traceability.** FR-015; DEP-012, DEP-029, DEP-038; CAP-017; Baseline AC-008 (third clause); AI-001; AI-012; Functional Gap FG-003; TD-004.

**Scope Boundary.** Does not select a concrete storage mechanism, retention policy, or persistence layer; does not design Recovery.

---

### P3-03-AD-011 - Current Aggregate and Publication Model

**Titel.** Current Aggregate Publication: P3-02 Structural Independence Preserved, Mechanics Unchanged.

**Motivation.** CAP-002, CAP-003, CAP-021 (all COMPLETE) require explicit ratification that this Architecture's own accounting redesign does not regress the already-certified publication mechanics; the new History output (AD-010) additionally requires explicit boundary-setting against the existing publication path.

**Decision.** `PerformanceEngine` SHALL continue to construct a Structurally Independent Current Aggregate value at every nesting level (P3-02-AD-005, IU-002, not reopened) on every tick that produces at least one Performance Observation. `CanonicalEnforcer.apply_performance_metrics` SHALL continue to publish this value, unchanged in mechanism, into `CanonicalState.state["performance_metrics"]` and the tick-result dict's own `"performance"` field. On a tick producing no Performance Observation, the most recently published Current Aggregate value SHALL remain the published value, exactly as the existing `apply_performance_metrics(None)` read-through guard already, correctly, behaves. Performance History Records (AD-010) are explicitly NOT published through this same mechanism.

**Scientific Justification.** P3-02's own Final Certification already, independently verified the Structural Independence and Writer-on-Behalf-Of mechanics for Performance Metrics; re-deriving or altering either would violate this governance chain's own explicit prohibition on reopening a certified decision, and is unnecessary since neither mechanism depends on which key or trigger condition the published dictionary's own content follows.

**Performance-Semantic Consequences.** The publication frequency changes (only on Observation-producing ticks does new content exist to publish, though the mechanism still executes every tick per AD-014), but the publication mechanism itself does not.

**Lifecycle Consequences.** None beyond AD-001's own already-stated consequences.

**Financial Consequences.** None.

**Ownership Consequences.** None; ratifies CAP-001, CAP-002, CAP-003 unchanged.

**Producer Consequences.** `PerformanceEngine`'s own `_stats_snapshot()`-equivalent mechanism (P3-02-certified) continues to apply to the Current Aggregate, now keyed per AD-004.

**Consumer Consequences.** No change to how a consumer retrieves the Current Aggregate.

**Publication Consequences.** Confirms the Current Aggregate remains the sole object `CanonicalEnforcer.apply_performance_metrics` publishes; Performance History (AD-010) uses a distinct, not-yet-specified exposure path.

**History Consequences.** Explicitly separates this decision's own scope (Current Aggregate publication) from AD-010's own scope (History), preventing the two from being conflated in a future Specification.

**Failure Consequences.** None beyond AD-016's own already-stated consequences.

**Determinism Consequences.** None beyond P3-02's own already-certified determinism guarantees, preserved unchanged.

**Compatibility Constraints.** Does not reopen P3-02-AD-001, AD-005, or IU-002; the Structural Independence mechanism itself is preserved exactly.

**Acceptance Criteria.** `id()` of the Current Aggregate published at tick N differs, at every nesting level, from `id()` of the value published at tick N+1, whenever a publication occurs at both ticks - identical to P3-02's own already-certified Acceptance Criterion, re-verified against the AD-004-rekeyed structure.

**Traceability.** FR-016, FR-017, FR-018; DEP-015, DEP-018, DEP-041, DEP-051; CAP-002, CAP-003, CAP-021, CAP-022; P3-02-AD-001, AD-005, IU-002 (not reopened).

**Scope Boundary.** Does not reopen any P3-02-certified mechanism; does not specify History's own publication mechanism (AD-010's own Scope Boundary).

---

### P3-03-AD-012 - Reporting Boundary and Consumer Contract

**Titel.** Reporting Boundary: Consumer Contract Defined, Module Not Implemented.

**Motivation.** CAP-018 (PARTIAL) found the published object structurally ready but "Reporting" itself unconfirmed against any actual module (Documentation Gap DG-001), and its own semantic trustworthiness contingent on CAP-005/CAP-006's own resolution.

**Decision.** "Reporting" SHALL remain the Runtime Ownership Matrix's own named Primary Consumer designation for Performance Metrics, resolving Documentation Gap DG-001: it is not stale documentation, but a deliberately deferred future consumer, out of P3-03's own implementation scope. P3-03 SHALL guarantee, as a Consumer Contract, that the published Current Aggregate (AD-011) and, once implemented, Performance History Records (AD-010) are well-formed, Structurally Independent, and semantically correct per every decision in Section 25 - sufficient for any future Reporting consumer to build against. No Reporting module, UI, export mechanism, or persistence layer SHALL be implemented by this document or any future P3-03 document.

**Scientific Justification.** The Runtime Ownership Matrix's own explicit naming of "Reporting" as Primary Consumer is a Baseline-level architectural commitment; resolving Documentation Gap DG-001 by declaring the designation stale, rather than deliberately deferred, would require reopening or contradicting the Baseline itself, which this document does not do without an Architecture Evolution Review - none is proposed. Deferring implementation while defining the contract precisely matches this governance chain's own established minimality discipline (compare P3-02-AD-008's own identical pattern for Consumer Read-Only verifiability).

**Performance-Semantic Consequences.** Performance's own correctness obligation now extends explicitly to "suitable for a future Reporting consumer," not merely "internally self-consistent."

**Lifecycle Consequences.** None beyond what AD-001 through AD-010 already establish.

**Financial Consequences.** None.

**Ownership Consequences.** None; "Reporting" remains a named but unimplemented Consumer, not a new Authoritative Owner or Computational Authority.

**Producer Consequences.** None beyond AD-011's own already-stated consequences.

**Consumer Consequences.** "Reporting," once built, will consume exactly the Current Aggregate and Performance History Records this document defines; no other Performance output is anticipated for it.

**Publication Consequences.** None beyond AD-011's own already-stated consequences.

**History Consequences.** Confirms Performance History Records (AD-010) are the minimum information a future Reporting consumer requires for any historical, not merely current-state, presentation.

**Failure Consequences.** None.

**Determinism Consequences.** None.

**Compatibility Constraints.** Does not implement Reporting; does not design a UI, export format, or persistence mechanism.

**Acceptance Criteria.** No future P3-03 Specification or Implementation document introduces a Reporting module, UI component, or export mechanism; the Runtime Ownership Matrix's own "Reporting" row remains textually unaltered.

**Traceability.** FR-019, FR-020; DEP-016, DEP-017, DEP-025, DEP-034, DEP-055; CAP-018; Runtime Ownership Matrix; Documentation Gap DG-001.

**Scope Boundary.** Does not implement Reporting; does not resolve whether "Reporting" will ultimately be a separate module, an external system, or a future runtime component - only that it remains a valid, deferred designation.

---

### P3-03-AD-013 - Performance Ownership Ratification

**Titel.** Performance Ownership: Structural Split Ratified, No New Authority.

**Motivation.** CAP-001 (COMPLETE) already found the ownership structure fully conformant; this decision formally ratifies it under the corrected accounting methodology (AD-001 through AD-010) rather than reopening it.

**Decision.** `PerformanceEngine` SHALL remain the exclusive Computational Authority for Performance Metrics (both the Current Aggregate and Performance History). `CanonicalState` SHALL remain the exclusive Authoritative Owner of the Current Aggregate. `CanonicalEnforcer` SHALL remain the exclusive Writer-on-Behalf-Of. "Reporting" remains the intended Consumer (AD-012). Neither `StrategySelector` (including its own orphaned `update` method) nor `run_engine/runtime/performance_analytics.py` SHALL possess, or be granted, any Computational Authority for Performance Metrics.

**Scientific Justification.** AI-002 (Unique Ownership) and Rule OM-008 (PerformanceEngine owns no operational runtime information, evaluates completed lifecycle outcomes only) are already satisfied by the existing ownership structure; AD-001 through AD-010 correct the methodology OM-008's own second sentence requires, without altering ownership itself, consistent with AI-003's own separation of Ownership and Computation.

**Performance-Semantic Consequences.** Confirms the ownership structure was never itself the defect; only the accounting methodology was.

**Lifecycle Consequences.** None.

**Financial Consequences.** None.

**Ownership Consequences.** Ratifies CAP-001 unchanged; introduces no new Authoritative Owner or Computational Authority.

**Producer Consequences.** None beyond AD-001 through AD-011's own already-stated consequences.

**Consumer Consequences.** None beyond AD-012's own already-stated consequences.

**Publication Consequences.** None beyond AD-011's own already-stated consequences.

**History Consequences.** None beyond AD-010's own already-stated consequences.

**Failure Consequences.** None.

**Determinism Consequences.** None.

**Compatibility Constraints.** Does not introduce a new Authoritative Owner or Computational Authority for any runtime object, satisfying Rule OM-009.

**Acceptance Criteria.** At any future HEAD implementing this Architecture, exactly one class (`PerformanceEngine`) computes Performance Metrics; no method of `StrategySelector` or any function of `performance_analytics.py` is invoked from the active runtime path.

**Traceability.** FR-001, FR-002, FR-003, FR-017, FR-025; DEP-001, DEP-002, DEP-013, DEP-014, DEP-021, DEP-022, DEP-030, DEP-031, DEP-033, DEP-054; CAP-001, CAP-002, CAP-003; Rule OM-008; AI-002; AI-003.

**Scope Boundary.** Does not alter the ownership structure itself, only ratifies it under the new methodology.

---

### P3-03-AD-014 - Performance Update Timing

**Titel.** Performance Update Timing: ADR-010 Step 11 Ratified, Unchanged.

**Motivation.** CAP-004 (COMPLETE) already found `PerformanceEngine.update`'s own invocation timing fully conformant; the corrected accounting methodology (AD-001 through AD-010) does not require, and must not introduce, a reordering.

**Decision.** `PerformanceEngine.update` (or its own eventual Specification-level equivalent) SHALL continue to be invoked exactly once per tick, unconditionally, at ADR-010's own step 11 (after Financial Accounting, step 9, and Risk Evaluation, step 10; before Tick-Complete CanonicalState Publication, step 12). Performance SHALL continue to consume only fully-completed upstream results (the same tick's own already-computed `trade_event` and `pnl`), never a raw, not-yet-validated Decision as its own gating trigger. No P3-01-certified stage order is reopened.

**Scientific Justification.** ADR-010's own already-certified ordering, and P3-01's own DEP-009 ("Performance Evaluation precedes Tick-Complete Publication"), already place Performance correctly downstream of both Financial Accounting and Risk Evaluation; the accounting-methodology correction (AD-001 through AD-010) operates entirely within this already-correct timing, requiring no change to it.

**Performance-Semantic Consequences.** Confirms the timing was never itself the defect; only the accounting methodology was, consistent with CAP-004's own already-COMPLETE finding.

**Lifecycle Consequences.** None beyond AD-001's own already-stated consequences.

**Financial Consequences.** None; `pnl` remains available to Performance exactly as early as it already is.

**Ownership Consequences.** None.

**Producer Consequences.** None.

**Consumer Consequences.** None.

**Publication Consequences.** None beyond AD-011's own already-stated consequences.

**History Consequences.** None beyond AD-010's own already-stated consequences.

**Failure Consequences.** None beyond AD-017's own already-stated consequences.

**Determinism Consequences.** None; ratifies already-deterministic, already-certified ordering.

**Compatibility Constraints.** Does not reorder, skip, or duplicate any ADR-010 stage; does not reopen P3-01-AD-001.

**Acceptance Criteria.** A fresh trace at any future HEAD confirms `PerformanceEngine`'s own invocation remains positioned after Financial Accounting and Risk Evaluation, and before Tick-Complete Publication, unconditionally, once per tick.

**Traceability.** FR-004; DEP-003, DEP-035, DEP-048; CAP-004; ADR-010; P3-01-AD-001; P3-01's own DEP-009.

**Scope Boundary.** Does not reopen P3-01's own certified twelve-stage ordering.

---

### P3-03-AD-015 - HOLD and NOOP Exclusion

**Titel.** HOLD and NOOP: Structural Exclusion, No Special-Case Logic.

**Motivation.** CAP-014 (COMPLETE) already found HOLD processed uniformly without crashing; this decision formalizes that HOLD/NOOP's own exclusion from Performance Observation is a structural consequence of AD-001, not a separately-maintained special case, resolving the governing task's own item 13 explicitly.

**Decision.** A HOLD Decision and its own resulting NOOP Execution SHALL continue to generate no `LifecycleEvent` at all. Under AD-001's own gate, this structurally, automatically produces zero Performance Observations, requiring no dedicated HOLD-detection branch anywhere in `PerformanceEngine`'s own logic. HOLD and NOOP SHALL NOT increase Trade Count, SHALL NOT affect Win Rate, and SHALL NOT be recorded as a Performance History Record. No neutral, tick-level HOLD/NOOP information SHALL be historized by Performance; a complete tick-by-tick trail including HOLD, if ever required, remains a Logging/Diagnostics concern outside Performance's own scope.

**Scientific Justification.** `trade_lifecycle.py`'s own `on_execution` already returns `None` for `action == "HOLD"` before any event-generating branch; combined with AD-001's own gate, this makes HOLD/NOOP exclusion a mathematical consequence of two already-established facts, not a new rule requiring its own independent enforcement mechanism, consistent with this governance chain's own minimality principle.

**Performance-Semantic Consequences.** The current runtime's own explicit `'HOLD'` bucket (`self.stats['HOLD']`) ceases to exist under AD-004's own Position-Side keying; this is an intended, direct consequence, not an oversight.

**Lifecycle Consequences.** None beyond AD-001's own already-stated consequences.

**Financial Consequences.** None; `pnl` is `0.0` on a HOLD tick regardless, and is never folded into the aggregate for such a tick under AD-001's own gate.

**Ownership Consequences.** None.

**Producer Consequences.** None beyond AD-001's own already-stated consequences.

**Consumer Consequences.** A consumer no longer observes a `"HOLD"` key in the Current Aggregate.

**Publication Consequences.** None beyond AD-004's own already-stated consequences.

**History Consequences.** No Performance History Record is ever generated for a HOLD/NOOP tick.

**Failure Consequences.** None.

**Determinism Consequences.** None; the exclusion is a deterministic, structural consequence of already-deterministic upstream behaviour.

**Compatibility Constraints.** Does not alter `TradeLifecycleEngine`'s or `Executor`'s own HOLD/NOOP handling; ratifies P3-01-AD-005 unchanged.

**Acceptance Criteria.** For any tick with `decision['action'] == 'HOLD'`, the Current Aggregate is byte-for-byte... functionally identical to its own value before that tick executed.

**Traceability.** FR-011; DEP-005, DEP-023; CAP-014; P3-01-AD-005; Functional Gap FG-004.

**Scope Boundary.** Does not introduce a separate HOLD-diagnostic mechanism; that remains Logging's own, unaddressed scope.

---

### P3-03-AD-016 - Rejection and Runtime Failure Event Exclusion

**Titel.** Rejection and Runtime Failure Event: Structural Simplification of an Already-Conformant Behaviour.

**Motivation.** CAP-015 (COMPLETE) already found the `RUNTIME_FAILURE_EVENT` short-circuit performs no accumulator mutation; this decision confirms this property is preserved, and simplified, under the new gate.

**Decision.** A Rejection SHALL NOT be counted as a successful Trade under any circumstance. A `RUNTIME_FAILURE_EVENT` SHALL NOT generate a Performance Observation and SHALL NOT mutate the Current Aggregate. Under AD-001's own gate, `RUNTIME_FAILURE_EVENT` fails the `event_type in {PARTIAL_CLOSE, TRADE_CLOSED}` test structurally; the current runtime's own explicit `RUNTIME_FAILURE_EVENT`-specific short-circuit becomes a redundant special case of this same general gate, not a separately-required mechanism. `TradeLifecycleEngine`'s own existing `failure_events` diagnostic list MAY continue to record `RUNTIME_FAILURE_EVENT` instances for diagnostic purposes; this remains unaffected by, and is not duplicated into, Performance History. No P3-01-certified Failure semantics are altered.

**Scientific Justification.** P3-01-AI-012 (Rejection Non-Mutation) already explicitly names "Performance statistics" among the values a rejected transition shall never mutate; AD-001's own general gate achieves this as a structural consequence rather than requiring its own dedicated enforcement, a strict simplification consistent with this governance chain's own minimality principle - not merely a preservation of current behaviour, but an improvement in its own internal consistency.

**Performance-Semantic Consequences.** The current runtime's own explicit `RUNTIME_FAILURE_EVENT` check may be removed as a distinct code path once the general AD-001 gate is implemented, without any behavioural change - a Specification-level simplification opportunity this Architecture identifies but does not mandate.

**Lifecycle Consequences.** None beyond AD-001's own already-stated consequences.

**Financial Consequences.** None; `pnl` is already `0.0` for a `RUNTIME_FAILURE_EVENT` tick per `PnLEngine`'s own already-certified gate.

**Ownership Consequences.** None.

**Producer Consequences.** None beyond AD-001's own already-stated consequences.

**Consumer Consequences.** None; a consumer observes identical non-mutation behaviour to today.

**Publication Consequences.** None.

**History Consequences.** No Performance History Record is ever generated for a `RUNTIME_FAILURE_EVENT` tick.

**Failure Consequences.** Directly implements and ratifies P3-01-AD-006 and P3-01-AI-012 for Performance specifically, not reopened.

**Determinism Consequences.** None; ratifies already-deterministic, already-conformant behaviour.

**Compatibility Constraints.** Does not alter ADR-011's own Runtime Failure Handling semantics or `TradeLifecycleEngine`'s own failure-event generation.

**Acceptance Criteria.** For any tick where `trade_event.event_type == "RUNTIME_FAILURE_EVENT"`, the Current Aggregate remains functionally identical to its own value before that tick executed, and no Performance History Record is appended.

**Traceability.** FR-007, FR-009; DEP-008, DEP-028, DEP-039, DEP-046, DEP-047, DEP-049, DEP-050; CAP-015; ADR-011; P3-01-AD-006; P3-01-AI-012; Verified Conformant Finding VCF-004.

**Scope Boundary.** Does not alter P3-01's own certified Failure Handling semantics; does not introduce a new diagnostic mechanism beyond what `TradeLifecycleEngine` already provides.

---

### P3-03-AD-017 - Failed-Tick Compatibility

**Titel.** Failed-Tick Compatibility: No Tick-Complete Result, RR-002 Not Resolved.

**Motivation.** The governing task's own item 15 requires an explicit statement that this Architecture does not silently close Residual Risk RR-002 or introduce a Recovery mechanism.

**Decision.** A Failed Tick (an exception interrupting `RunLoop.step()` before Tick Completion) SHALL continue to produce no Tick-Complete result at all; no Performance update of any kind, whether under the current or the corrected methodology, becomes externally observable for a Failed Tick. Whatever internal `CanonicalEnforcer.apply_*` calls already completed before the exception remain present in `CanonicalState`'s own internally-held state, exactly as P3-02-AD-016 already establishes. Residual Risk RR-002 (Post-Exception Financial/Lifecycle Divergence) SHALL remain an open, non-blocking, documented Residual Risk; this document does not resolve it, does not silently present it as resolved, and does not introduce a rollback, reset, or transaction mechanism for it or for `PerformanceEngine`'s own private working state.

**Scientific Justification.** P3-01-AD-004 and P3-02-AD-016 already, fully establish Failed-Tick semantics; the accounting-methodology correction (AD-001 through AD-010) introduces no new interaction with tick-level exception handling, since it operates entirely within a single, already-atomic `PerformanceEngine.update` invocation.

**Performance-Semantic Consequences.** None beyond confirming the corrected methodology does not change Failed-Tick behaviour.

**Lifecycle Consequences.** None beyond AD-001's own already-stated consequences.

**Financial Consequences.** None.

**Ownership Consequences.** None.

**Producer Consequences.** None beyond P3-02-AD-016's own already-stated consequences.

**Consumer Consequences.** None; a consumer never observes a Failed Tick's own partial results, exactly as today.

**Publication Consequences.** None beyond P3-02-AD-016's own already-stated consequences.

**History Consequences.** No Performance History Record is ever generated for a Failed Tick, since no Tick-Complete result, and hence no confirmed Observation, exists for it.

**Failure Consequences.** This decision IS the Failed-Tick disposition; RR-002 remains explicitly open.

**Determinism Consequences.** None beyond P3-02's own already-certified determinism guarantees for successfully-completed ticks.

**Compatibility Constraints.** Does not reopen P3-01-AD-004 or P3-02-AD-016; does not introduce a rollback, reset, or transaction mechanism.

**Acceptance Criteria.** A fault-injection probe interrupting `RunLoop.step()` before Tick Completion produces no externally observable Tick-Complete result, and `RR-002` remains present, unmodified, in this document's own Section 5 disposition.

**Traceability.** FR-004, FR-009; DEP-028, DEP-039, DEP-049, DEP-050; CAP-015, CAP-025; P3-01-AD-004; P3-02-AD-016; Residual Risk RR-002.

**Scope Boundary.** Does not design a Recovery mechanism; does not resolve RR-002.

---

### P3-03-AD-018 - Determinism and Replay Preservation

**Titel.** Determinism and Replay: Extended to the Corrected Mechanism, P3-02 Isolation Preserved.

**Motivation.** CAP-019, CAP-020 (both COMPLETE) already found `PerformanceEngine.update` deterministic and replay-safe; this decision confirms the accounting-methodology correction (AD-001 through AD-010) preserves both properties.

**Decision.** Given identical Lifecycle and Financial Outcomes applied in an identical order, `PerformanceEngine`'s own Performance Observations, Current Aggregate values, and Performance History Records SHALL be functionally identical across independent replays. The corrected aggregation mechanism SHALL introduce no randomness, wall-clock read, or I/O. Performance History's own record order SHALL be deterministic, matching the deterministic order in which `TradeLifecycleEngine` generates the underlying `LifecycleEvent` sequence. P3-02's own Snapshot Isolation and Structural Independence guarantees (AD-011) SHALL remain fully preserved; no decision in this document reduces or bypasses either.

**Scientific Justification.** The corrected mechanism (AD-001 through AD-010) is a pure function of `trade_event` and `pnl`, both already-deterministic inputs under P3-01's own certified ordering; no new source of nondeterminism is introduced by gating, re-keying, or adding a History output, each of which is itself a deterministic transformation of already-deterministic inputs.

**Performance-Semantic Consequences.** None beyond confirming the corrected methodology preserves determinism.

**Lifecycle Consequences.** None beyond AD-001's own already-stated consequences.

**Financial Consequences.** None.

**Ownership Consequences.** None.

**Producer Consequences.** None beyond AD-011's own already-stated consequences.

**Consumer Consequences.** A consumer replaying an identical tick sequence observes functionally identical Current Aggregate and Performance History values, exactly as under the current, already-certified determinism guarantee.

**Publication Consequences.** None beyond AD-011's own already-stated consequences.

**History Consequences.** Directly establishes Performance History's own deterministic ordering requirement (AD-010).

**Failure Consequences.** None beyond AD-017's own already-stated consequences.

**Determinism Consequences.** This decision IS the determinism ratification; extends CAP-019/CAP-020's own already-certified scope to the corrected mechanism without altering either's own underlying justification.

**Compatibility Constraints.** Does not reopen P3-02's own certified Composite Isolation or Structural Independence mechanisms; does not introduce any randomness, wall-clock dependency, or I/O.

**Acceptance Criteria.** Two independent `PerformanceEngine` instances, given an identical sequence of `(trade_event, pnl)` inputs in identical order, produce functionally identical Current Aggregate values and functionally identical Performance History Record sequences at every point in the replay.

**Traceability.** FR-021, FR-022; DEP-019, DEP-043; CAP-019, CAP-020; AI-005; AI-006; AC-012; P3-02-AD-001, AD-005 (not reopened).

**Scope Boundary.** Does not re-execute P3-01's or P3-02's own already-certified replay verification; does not extend determinism claims to a retry sequence following a Failed Tick.

---

### P3-03-AD-019 - Alternative Performance Path Disposition

**Titel.** Alternative Performance Paths: Individually Classified, None Reactivated, None Deleted.

**Motivation.** The governing task's own item 17 requires an explicit, individual disposition for each of five alternative/inactive paths, ratifying CAP-023 and CAP-024's own already-established findings.

**Decision.** Exactly one active Performance computation path SHALL remain architecturally permitted: `PerformanceEngine`, invoked exclusively from `RunLoop.step()`. The following five paths are individually, explicitly classified, per Section 23's own table: `run_engine/runtime/performance_analytics.py` (inactive, no Authority, its own `(regime, action)` scheme explicitly not adopted by AD-004, disposition otherwise forwarded); `StrategySelector.update` (inactive/orphaned, no Authority, disposition forwarded, not reconciled with Performance by this document); `run_engine/feedback/tracker.py`, `run_engine/runtime/strategy_memory.py`, `run_engine/execution/adapter.py` (each inactive, no Authority, unaffected, disposition forwarded). No decision in this document reactivates, integrates, or deletes any of these five paths.

**Scientific Justification.** The CGA's own Section 25 (Alternative-Path Assessment) already individually verified each path's own active/inactive status, import status, and authority relevance via a repeatable, mechanical import-closure check; ratifying these findings, rather than re-deriving them, avoids duplicative work while formally binding them as an architectural constraint (AI-013, Architectural Minimality) rather than leaving them as a mere observation.

**Performance-Semantic Consequences.** Confirms the corrected Performance methodology (AD-001 through AD-010) is realized exclusively within `PerformanceEngine`, with no competing implementation anywhere in the repository.

**Lifecycle Consequences.** None.

**Financial Consequences.** None.

**Ownership Consequences.** Ratifies that none of the five paths possesses, or is granted, Computational Authority for Performance (AD-013).

**Producer Consequences.** None of the five paths becomes a Producer under this Architecture.

**Consumer Consequences.** None of the five paths becomes a Consumer of Performance Metrics under this Architecture.

**Publication Consequences.** None of the five paths publishes via `CanonicalEnforcer` under this Architecture.

**History Consequences.** None of the five paths contributes to Performance History (AD-010).

**Failure Consequences.** None.

**Determinism Consequences.** None; no path introduces a competing, potentially non-deterministic accounting stream.

**Compatibility Constraints.** Does not reactivate, integrate, or delete any of the five paths; any future disposition requires its own, separately-justified Architecture Evolution Review or Repository Consolidation decision.

**Acceptance Criteria.** A fresh import-closure check at any future HEAD implementing this Architecture confirms all five paths remain unimported from `run_engine/core` and `run_engine/main.py`.

**Traceability.** FR-024; DEP-021, DEP-024, DEP-026, DEP-029, DEP-044; CAP-023, CAP-024; Residual Risks RR-001, RR-002; AI-013.

**Scope Boundary.** Does not decide any path's own eventual disposition beyond confirming its own continued inactivity; reactivation, integration, and deletion each remain a future, separate decision.

---

### P3-03-AD-020 - Verification Obligation

**Titel.** Verification Obligation: Established, Mechanism Deferred to Specification.

**Motivation.** CAP-029 (PARTIAL) found the corrected methodology's own eventual correctness will rest on manual inspection alone unless a repeatable, independent, automated verification procedure is established.

**Decision.** A repeatable, independent verification procedure SHALL exist, exercising `PerformanceEngine`'s own corrected accounting formulas (AD-001 through AD-010) against every relevant Baseline Acceptance Criterion (AC-008, AC-014). The specific verification mechanism (a dedicated test suite, a scripted fault-injection probe, or another repeatable procedure) is not specified here, deferred to the Specification stage - directly analogous to P3-02-AD-008's own identical pattern for Consumer Read-Only Discipline verifiability.

**Scientific Justification.** Establishing the obligation without prescribing the mechanism preserves this document's own explicit prohibition on defining tests as fixed commands, while still ensuring the Specification stage does not silently omit verification for a corrected methodology whose own prior, uncorrected state persisted undetected for multiple governance-chain units (P1-03.1 Finding 5, TD-004's own origin).

**Performance-Semantic Consequences.** None beyond establishing the obligation.

**Lifecycle Consequences.** None.

**Financial Consequences.** None.

**Ownership Consequences.** None.

**Producer Consequences.** None.

**Consumer Consequences.** None.

**Publication Consequences.** None.

**History Consequences.** A future verification procedure SHOULD exercise the AD-010 History-reproducibility Acceptance Criterion (AD-010's own Acceptance Criteria field) specifically, not merely the Current Aggregate.

**Failure Consequences.** None.

**Determinism Consequences.** None beyond AD-018's own already-stated consequences.

**Compatibility Constraints.** Does not specify a concrete test suite, script, or command.

**Acceptance Criteria.** The future P3-03 Specification names a specific, repeatable verification mechanism for AD-001 through AD-010's own combined behaviour.

**Traceability.** FR-005 through FR-014; DEP-020; CAP-029; Verification Gap VG-001.

**Scope Boundary.** Does not itself write or specify the test suite.

---

### P3-03-AD-021 - Cross-Unit Boundary Ratification

**Titel.** Cross-Unit Boundary: Seven Items Formally Ratified Outside This Unit's Own Scope.

**Motivation.** The governing task's own item 20 requires an explicit, itemized ratification of every Cross-Unit boundary this Architecture must not cross.

**Decision.** Seven items are formally ratified as outside this unit's own resolution scope: (1) P3-01's own twelve-stage ordering, Tick-Complete Publication semantics, HOLD semantics, and Failed-Tick semantics remain entirely unchanged. (2) P3-02's own Composite Isolation and Structural Independence mechanisms remain entirely unchanged, preserved as a binding constraint on AD-001 through AD-020. (3) P2-03's own Financial Ownership (PnLEngine's own formula and Realized-PnL computation) remains entirely unchanged. (4) P2-04's own Risk Ownership remains entirely unchanged; no new Performance-Risk dependency is introduced in either direction (AD-008). (5) TD-007 (RunLoop Lifecycle Control Surface) remains a future Runtime Control Unit's own scope. (6) Reporting implementation, persistence, and external evaluation remain out of scope (AD-012). (7) Scientific Strategy Evaluation or optimization remains out of scope; the orphaned `StrategySelector.update` method is explicitly not reconciled or reactivated (AD-019).

**Scientific Justification.** Each of the seven items is already governed by an independently certified decision (P3-01, P3-02, P2-03, P2-04) or an explicitly forwarded future scope (TD-007, Reporting, Strategy Evaluation); restating each explicitly, rather than leaving the boundary implicit, satisfies this governance chain's own repeated finding that implicit boundaries are the recurring source of scope-creep risk across units.

**Performance-Semantic Consequences.** None beyond confirming the boundary.

**Lifecycle Consequences.** None beyond confirming P3-01's ordering is untouched.

**Financial Consequences.** None beyond confirming P2-03 is untouched.

**Ownership Consequences.** None; no new Authoritative Owner or Computational Authority crosses into another unit's own scope.

**Producer Consequences.** None.

**Consumer Consequences.** None.

**Publication Consequences.** None beyond confirming P3-02's own mechanisms are untouched.

**History Consequences.** None beyond AD-010's own already-stated consequences.

**Failure Consequences.** None beyond AD-017's own already-stated consequences.

**Determinism Consequences.** None beyond AD-018's own already-stated consequences.

**Compatibility Constraints.** This decision IS the compatibility constraint; every other decision in Section 25 is bound by it.

**Acceptance Criteria.** No future P3-03 Specification, Implementation, or Final Certification document modifies any P3-01, P3-02, P2-02A, P2-03, or P2-04 certified file, decision, or Acceptance Criterion.

**Traceability.** FR-001, FR-004, FR-007, FR-009, FR-016, FR-017, FR-018; DEP-048 through DEP-055; CAP-026, CAP-027, CAP-028; P3-01, P3-02, P2-02A, P2-03, P2-04 (not reopened); TD-007.

**Scope Boundary.** This decision is itself a scope boundary; it decides nothing beyond confirming the seven items remain out of scope.

---

### P3-03-AD-022 - TD-004 Architectural Closure Readiness

**Titel.** TD-004: Architecturally Resolved Within P3-03's Own Scope, Register Unchanged Pending Implementation and Certification.

**Motivation.** CAP-025 (MISSING, aggregate) requires an explicit statement of TD-004's own architectural readiness, per the governing task's own explicit instruction to resolve TD-004 architecturally without yet closing it in the Technical Debt Register.

**Decision.** TD-004 ("Lifecycle-based Performance Evaluation") SHALL be considered architecturally resolved within this unit's own scope by AD-001 through AD-011, jointly: every constituent capability the CGA identified as MISSING or PARTIAL (CAP-005 through CAP-010, CAP-012, CAP-013, CAP-017, CAP-018) is addressed by an explicit decision in Section 25. TD-004's own Status field in the Technical Debt Register SHALL NOT be altered by this document; it SHALL remain "Already Planned" until the Specification, Implementation, and Final Certification stages actually deliver and independently verify the corresponding runtime change.

**Scientific Justification.** An Architecture Decision is a binding target, not a delivered, verified runtime state; this governance chain's own established discipline (P3-01, P3-02) never closes a Technical Debt Register entry at the Architecture stage, reserving that determination for Final Certification's own independent verification of actually-implemented, actually-tested behaviour.

**Performance-Semantic Consequences.** None beyond confirming architectural, not implementation-level, closure.

**Lifecycle Consequences.** None beyond AD-001 through AD-010's own already-stated consequences.

**Financial Consequences.** None.

**Ownership Consequences.** None.

**Producer Consequences.** None.

**Consumer Consequences.** None.

**Publication Consequences.** None.

**History Consequences.** None beyond AD-010's own already-stated consequences.

**Failure Consequences.** None.

**Determinism Consequences.** None.

**Compatibility Constraints.** Does not modify `docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md`.

**Acceptance Criteria.** TD-004's own Register entry remains textually unaltered by this document; a future P3-03 Final Certification, not this Architecture, is the document authorized to recommend a Register status change.

**Traceability.** FR-005 through FR-015, FR-023; DEP-032, DEP-036 through DEP-038, DEP-042, DEP-046, DEP-047, DEP-052; CAP-025; TD-004.

**Scope Boundary.** Does not alter the Technical Debt Register; does not itself constitute TD-004's own closure.

## 26. Architecture Invariants

**P3-03-AI-001 - No Decision-as-Trade Equivalence.** A raw Strategy Decision shall never, by itself, be treated as a Trade for Performance purposes. Established by AD-001, AD-002.

**P3-03-AI-002 - Performance Based on Completed Runtime Outcomes.** Every Performance Observation shall derive from a Completed Lifecycle Outcome (`PARTIAL_CLOSE` or `TRADE_CLOSED`), never from an intention, an unvalidated Execution, or a non-closing Lifecycle Transition. Established by AD-001, AD-006.

**P3-03-AI-003 - No Rejected Transition as Successful Trade.** A Rejection or `RUNTIME_FAILURE_EVENT` shall never be counted as a successful Trade or mutate the Current Aggregate. Established by AD-016.

**P3-03-AI-004 - No HOLD/NOOP Trade Count Inflation.** A HOLD Decision or NOOP Execution shall never increase Trade Count or affect Win Rate. Established by AD-015.

**P3-03-AI-005 - Realized PnL from PnLEngine Only.** Every Performance Observation's own `pnl` value shall originate exclusively from `PnLEngine`'s own already-certified computation for the same `trade_event`; no independent PnL computation shall exist within `PerformanceEngine`. Established by AD-007.

**P3-03-AI-006 - Unique Performance Computational Authority.** `PerformanceEngine` shall remain the sole Computational Authority for Performance Metrics; no other component, active or inactive, shall compute Performance statistics for the active runtime. Established by AD-013, AD-019.

**P3-03-AI-007 - Canonical Performance Publication.** The Current Aggregate shall be published exclusively via `CanonicalEnforcer.apply_performance_metrics`, remaining Structurally Independent and Tick-Stable, exactly as P3-02 already certifies. Established by AD-011.

**P3-03-AI-008 - Current Aggregate and History Separation.** The Current Aggregate and Performance History Records shall remain two distinct objects with two distinct lifetimes; Performance History shall never be stored inside `CanonicalState`. Established by AD-010.

**P3-03-AI-009 - Deterministic Performance Aggregation.** Given an identical sequence of Trade Outcomes applied in an identical order, the Current Aggregate shall be functionally identical across independent replays. Established by AD-018.

**P3-03-AI-010 - Deterministic Performance History.** Given an identical sequence of Trade Outcomes applied in an identical order, the resulting Performance History Record sequence shall be functionally identical across independent replays. Established by AD-010, AD-018.

**P3-03-AI-011 - No Alternative Active Performance Path.** Exactly one active Performance computation path shall exist at any point in this unit's own scope. Established by AD-019.

**P3-03-AI-012 - Certified Ordering Compatibility.** No decision in this document, and no future implementation of it, may alter P3-01's own certified twelve-stage execution ordering. Established by AD-014, AD-021.

**P3-03-AI-013 - Certified Information-Isolation Compatibility.** No decision in this document, and no future implementation of it, may alter P3-02's own certified Composite Isolation or Structural Independence mechanisms. Established by AD-011, AD-018, AD-021.

**P3-03-AI-014 - No Performance Mutation from Failed Tick.** A Failed Tick shall never produce an externally observable Performance update of any kind. Established by AD-017.

**P3-03-AI-015 - Explicit Reporting Boundary.** Performance shall guarantee a well-formed, Structurally Independent Consumer Contract for a future Reporting consumer, without implementing that consumer. Established by AD-012.

Every Architecture Invariant above is directly traceable to one or more Architecture Decisions in Section 25; none is asserted without a corresponding decision establishing it. None of the fifteen invariants above contradicts or redefines any Architecture Baseline-level Invariant (AI-001 through AI-015) or any already-certified P3-01-specific (P3-01-AI-001 through AI-012) or P3-02-specific (P3-02-AI-001 through AI-015) invariant; each is a P3-03-specific specialization of the general principle the corresponding Baseline Invariant already establishes.

### 26.1 Invariant Traceability (Individually Enumerated)

| Invariant | Established By |
|---|---|
| P3-03-AI-001 | AD-001, AD-002 |
| P3-03-AI-002 | AD-001, AD-006 |
| P3-03-AI-003 | AD-016 |
| P3-03-AI-004 | AD-015 |
| P3-03-AI-005 | AD-007 |
| P3-03-AI-006 | AD-013, AD-019 |
| P3-03-AI-007 | AD-011 |
| P3-03-AI-008 | AD-010 |
| P3-03-AI-009 | AD-018 |
| P3-03-AI-010 | AD-010, AD-018 |
| P3-03-AI-011 | AD-019 |
| P3-03-AI-012 | AD-014, AD-021 |
| P3-03-AI-013 | AD-011, AD-018, AD-021 |
| P3-03-AI-014 | AD-017 |
| P3-03-AI-015 | AD-012 |

Every P3-03-specific Invariant is individually listed above, with no range citation.

## 27. Architecture Constraints

**Constraint C-001.** P3-01's own twelve-stage execution ordering (ADR-010, P3-01-AD-001) remains entirely unchanged; no future P3-03 Specification or Implementation may reorder, skip, or duplicate any stage.

**Constraint C-002.** P3-02's own Composite Isolation and Structural Independence mechanisms (P3-02-AD-001, AD-005) remain entirely unchanged; no future P3-03 Specification or Implementation may alter either mechanism.

**Constraint C-003.** No Position, Financial, or Risk formula shall be changed; `PositionEngine`, `PnLEngine`, and `RiskEngine`'s own computations remain entirely unaltered.

**Constraint C-004.** No new Financial or Risk Ownership shall be introduced for any runtime object.

**Constraint C-005.** No Strategy-Performance optimization or feedback logic shall be introduced; the orphaned `StrategySelector.update` method remains unreconciled and unreactivated.

**Constraint C-006.** No Reporting UI, export mechanism, or persistence layer shall be designed or implemented.

**Constraint C-007.** No Persistence mechanism (ADR-012, Deferred Scope) shall be introduced.

**Constraint C-008.** No Recovery mechanism shall be introduced, including as a resolution to Residual Risk RR-002.

**Constraint C-009.** No Schema Evolution mechanism shall be introduced beyond the explicitly-necessary Performance Observation and Performance History Record shapes this document itself defines (AD-001, AD-010).

**Constraint C-010.** No Operator Lifecycle Control mechanism (TD-007) shall be introduced or conflated with this Architecture's own Failed-Tick or Rejection models.

**Constraint C-011.** No parallel or asynchronous Performance execution shall be introduced; `PerformanceEngine.update` remains synchronous, single-threaded, invoked exactly once per tick.

**Constraint C-012.** No inactive path (`performance_analytics.py`, `StrategySelector.update`, `feedback/tracker.py`, `runtime/strategy_memory.py`, `execution/adapter.py`) shall be reactivated without its own, separately-justified governance decision.

**Constraint C-013.** No rollback, reset, or transaction mechanism shall be introduced for `CanonicalState`, `PerformanceEngine`'s own private working state, or any other component's own cross-tick state, including as a resolution to any Residual Risk this document names.

**Constraint C-014.** A Residual Risk shall not, by its own existence alone, be reclassified a Functional Gap; its own actual, independently-assessed impact governs its classification, not reopened by this Architecture.

**Constraint C-015.** No concrete Python signature, method body, complete file diff, or Implementation Unit shall be specified anywhere in this document.

## 28. Technical-Debt Disposition

**TD-004** (Lifecycle-based Performance Evaluation) is architecturally resolved, within this unit's own scope, by AD-001 through AD-011, jointly (AD-022). The Technical Debt Register's own Status field ("Already Planned") is NOT altered by this document; a future P3-03 Final Certification, not this Architecture, is the document authorized to recommend a status change, and only after Implementation independently verifies the corresponding runtime behaviour.

**TD-007** (RunLoop Lifecycle Control Surface) remains explicitly out of this unit's own scope (AD-021); this document does not conflate it with AD-016's or AD-017's own Failure/Rejection Information Flow decisions.

**No new Technical Debt candidate is identified as scientifically required by this document.** Every open item within this unit's own scope (CAP-005 through CAP-010, CAP-012, CAP-013, CAP-017, CAP-018, CAP-025, CAP-029) is fully and directly addressed by the Architecture Decisions in Section 25, requiring no further, separately-tracked recommendation. Consistent with the governing task's own explicit instruction, no new Technical Debt ID is created and the Register itself is not modified.

## 29. FRA Traceability

| Requirement | Governing Architecture Decision(s) |
|---|---|
| FR-001 | AD-013, AD-021 |
| FR-002 | AD-013 |
| FR-003 | AD-013 |
| FR-004 | AD-014 |
| FR-005 | AD-001, AD-002, AD-004, AD-009 |
| FR-006 | AD-001, AD-007, AD-008 |
| FR-007 | AD-001, AD-003, AD-005, AD-006, AD-016 |
| FR-008 | AD-004 (Regime rejected as a keying dimension, ratified not reintroduced) |
| FR-009 | AD-016, AD-017 |
| FR-010 | AD-001, AD-004, AD-006, AD-009 |
| FR-011 | AD-015 |
| FR-012 | AD-002, AD-003 |
| FR-013 | AD-007, AD-009 |
| FR-014 | AD-007, AD-009 |
| FR-015 | AD-010 |
| FR-016 | AD-011, AD-018 |
| FR-017 | AD-011, AD-013 |
| FR-018 | AD-011 |
| FR-019 | AD-012 |
| FR-020 | AD-012 |
| FR-021 | AD-018 |
| FR-022 | AD-018 |
| FR-023 | AD-008 |
| FR-024 | AD-019 |
| FR-025 | AD-013 |

All twenty-five Functional Requirements are governed by at least one Architecture Decision.

## 30. SDA Dependency Traceability

Every one of the fifty-five Dependency records is individually resolved by the Architecture Decision(s) governing its own source Functional Requirement (Section 29); no dependency remains without an explicit Architecture-stage disposition.

| Dependency | Disposition |
|---|---|
| DEP-001 | Ratified - AD-013. |
| DEP-002 | Ratified - AD-013. |
| DEP-003 | Closed - AD-002, AD-014. |
| DEP-004 | Closed - AD-004, AD-009. |
| DEP-005 | Closed - AD-004, AD-015. |
| DEP-006 | Closed - AD-007. |
| DEP-007 | Closed - AD-007. |
| DEP-008 | Closed - AD-005, AD-016. |
| DEP-009 | Closed - AD-007, AD-009. |
| DEP-010 | Closed - AD-007, AD-009. |
| DEP-011 | Closed - AD-002, AD-003. |
| DEP-012 | Closed - AD-010. |
| DEP-013 | Ratified - AD-013. |
| DEP-014 | Ratified - AD-013. |
| DEP-015 | Ratified - AD-011. |
| DEP-016 | Closed - AD-012. |
| DEP-017 | Closed - AD-012. |
| DEP-018 | Ratified - AD-011. |
| DEP-019 | Ratified - AD-018. |
| DEP-020 | Closed - AD-001 through AD-009 (aggregate read-set, resolved jointly). |
| DEP-021 | Ratified - AD-013, AD-019. |
| DEP-022 | Ratified - AD-013. |
| DEP-023 | Closed - AD-004, AD-015. |
| DEP-024 | Ratified - AD-004, AD-019 (prior art considered, not adopted). |
| DEP-025 | Closed - AD-012. |
| DEP-026 | Ratified - AD-019. |
| DEP-027 | Ratified - AD-019 (OQ-002 remains open, not decided). |
| DEP-028 | Closed - AD-003, AD-006, AD-016. |
| DEP-029 | Ratified - AD-010, AD-019. |
| DEP-030 | Ratified - AD-013. |
| DEP-031 | Ratified - AD-013. |
| DEP-032 | Closed - AD-001, AD-009. |
| DEP-033 | Ratified - AD-013. |
| DEP-034 | Closed - AD-012. |
| DEP-035 | Closed - AD-014. |
| DEP-036 | Closed - AD-001, AD-002, AD-006, AD-009. |
| DEP-037 | Closed - AD-007. |
| DEP-038 | Closed - AD-010. |
| DEP-039 | Ratified - AD-003, AD-016. |
| DEP-040 | Ratified - AD-004 (regime unused, benign, not reintroduced). |
| DEP-041 | Ratified - AD-011. |
| DEP-042 | Closed - AD-008 (interpretive ambiguity resolved, narrow reading adopted). |
| DEP-043 | Ratified - AD-018. |
| DEP-044 | Ratified - AD-019. |
| DEP-045 | Ratified - AD-003, AD-007, AD-008. |
| DEP-046 | Closed - AD-006, AD-016. |
| DEP-047 | Closed - AD-001, AD-002. |
| DEP-048 | Ratified - AD-014, AD-021. |
| DEP-049 | Ratified - AD-016, AD-021. |
| DEP-050 | Ratified - AD-003, AD-006, AD-016, AD-021. |
| DEP-051 | Ratified - AD-011, AD-018, AD-021. |
| DEP-052 | Closed - AD-022 (blanket TD-004 constraint, architecturally resolved). |
| DEP-053 | Ratified - AD-002, AD-019 (OQ-002 remains open). |
| DEP-054 | Ratified - AD-021. |
| DEP-055 | Ratified - AD-012. |

## 31. CGA Capability Traceability

| Capability | Prior Status | Disposition |
|---|---|---|
| CAP-001 | COMPLETE | Ratified unchanged - AD-013. |
| CAP-002 | COMPLETE | Ratified unchanged - AD-013, AD-011. |
| CAP-003 | COMPLETE | Ratified unchanged - AD-013. |
| CAP-004 | COMPLETE | Ratified unchanged - AD-014. |
| CAP-005 | MISSING | Closed - AD-001, AD-002, AD-004, AD-009. |
| CAP-006 | MISSING (aggregate) | Closed - resolved as a direct consequence of CAP-005, CAP-007, CAP-008, CAP-009, CAP-010, CAP-013 each individually closing (AD-001 through AD-010). |
| CAP-007 | MISSING | Closed - AD-002, AD-003. |
| CAP-008 | MISSING | Closed - AD-003. |
| CAP-009 | PARTIAL | Closed - AD-004, AD-005, AD-006 (full LifecycleEvent read-set now consumed: event_type, side, trade_id). |
| CAP-010 | PARTIAL | Closed - AD-007. |
| CAP-011 | COMPLETE | Ratified unchanged - AD-008. |
| CAP-012 | PARTIAL | Closed - AD-008 (narrow reading adopted). |
| CAP-013 | MISSING | Closed - AD-004, AD-005, AD-006, AD-009. |
| CAP-014 | COMPLETE | Ratified, structurally reinforced - AD-015. |
| CAP-015 | COMPLETE | Ratified, structurally simplified - AD-016. |
| CAP-016 | COMPLETE | Ratified unchanged - AD-009 (formula arithmetic untouched). |
| CAP-017 | MISSING | Closed - AD-010. |
| CAP-018 | PARTIAL | Closed - AD-012. |
| CAP-019 | COMPLETE | Ratified unchanged - AD-018. |
| CAP-020 | COMPLETE | Ratified unchanged, extended - AD-018. |
| CAP-021 | COMPLETE | Ratified unchanged - AD-011. |
| CAP-022 | COMPLETE | Ratified unchanged - AD-010 (Current Aggregate lifetime unaffected). |
| CAP-023 | COMPLETE | Ratified unchanged - AD-019. |
| CAP-024 | COMPLETE (Residual-Risk Capability) | Ratified unchanged, not reopened - AD-019. |
| CAP-025 | MISSING (aggregate) | Closed - resolved as a direct, automatic consequence of CAP-005 through CAP-010, CAP-012, CAP-013, CAP-017, CAP-018 each individually closing (AD-022). |
| CAP-026 | COMPLETE | Ratified unchanged - AD-021. |
| CAP-027 | COMPLETE | Ratified unchanged - AD-021. |
| CAP-028 | COMPLETE | Ratified unchanged - AD-021. |
| CAP-029 | PARTIAL | Verification obligation established, mechanism deferred - AD-020. |

Seventeen of twenty-nine capabilities are ratified unchanged; ten (CAP-005 through CAP-010, CAP-012, CAP-013, CAP-017, CAP-018) are closed by explicit decisions in this Architecture; CAP-006's and CAP-025's own aggregate MISSING status is each resolved as a direct, automatic consequence of their own constituent capabilities individually closing; CAP-029 remains PARTIAL, with its own Governance dimension (the obligation itself) established, deferred to the Specification stage for its own concrete mechanism - directly analogous to how the P3-02 Architecture left CAP-007/CAP-008's own verification mechanism to its own Specification stage.

## 32. Acceptance Criteria

**P3-03-AC-001.** No Performance Observation, Trade Count increment, or Win Rate update occurs for any tick whose own `trade_event.event_type` is not `PARTIAL_CLOSE` or `TRADE_CLOSED`.

**P3-03-AC-002.** Every key in the published Current Aggregate is one of exactly `{"LONG", "SHORT"}`; no `"BUY"`, `"SELL"`, or `"HOLD"` key appears.

**P3-03-AC-003.** For any tick satisfying the AD-001 gate, the resulting `pnl` attribution equals exactly the value `PnLEngine.update` computed for the same `trade_event` in the same tick.

**P3-03-AC-004.** `PerformanceEngine`'s own method body contains no reference to `equity`, `peak_equity`, `drawdown`, `risk_allocation_factor`, or `execution`.

**P3-03-AC-005.** The Current Aggregate's own running statistics, for any Position Side, are exactly reproducible by replaying the ordered sequence of Performance History Records for that side through the AD-009 aggregation rule.

**P3-03-AC-006.** No Performance History Record is ever generated for a HOLD, NOOP, `TRADE_OPENED`, `SCALE_IN`, `RUNTIME_FAILURE_EVENT`, or Failed-Tick condition.

**P3-03-AC-007.** No Performance History Record is stored inside `CanonicalState`.

**P3-03-AC-008.** `id()` of the Current Aggregate published at tick N differs, at every nesting level, from `id()` of the value published at tick N+1, whenever a publication occurs at both ticks.

**P3-03-AC-009.** No method of `StrategySelector` and no function of `performance_analytics.py`, `feedback/tracker.py`, `runtime/strategy_memory.py`, or `execution/adapter.py` is invoked from the active runtime path.

**P3-03-AC-010.** Every already-certified P2-02A, P2-03, P2-04, P3-01, and P3-02 contract remains unaltered by any decision in this document.

**P3-03-AC-011.** No new Functional Requirement, Dependency, Capability classification, Persistence, Recovery, or rollback/reset/transaction mechanism is introduced by any decision in this document.

**P3-03-AC-012.** The Technical Debt Register's own TD-004 and TD-007 entries remain textually unaltered by this document.

## 33. Implementation Impact Inventory

At the level of runtime-component impact only, no concrete Python signature, file plan, or Implementation Unit is defined here; that is the Specification stage's own scope.

**Components requiring a functional runtime change:** `run_engine/core/performance.py` (`PerformanceEngine.update` must gate on `trade_event.event_type` (AD-001), key by Position Side rather than Decision Action (AD-004), attribute the already-correct `pnl` value to the corrected bucket (AD-007), and, if the History Model is implemented in this unit's own Implementation stage, produce Performance History Records (AD-010) - the single component bearing the entire substantive change this Architecture requires).

**Components requiring verification only, no functional change:** `run_engine/core/loop.py` (AD-014 - the call site's own position in the tick sequence is unaffected; whether the four-argument call shape itself changes, given `execution` is not added per AD-003, is a Specification-level signature question, not an Architecture-level one); `run_engine/core/canonical_state.py`, `run_engine/core/canonical_enforcer.py` (AD-011, AD-013 - the existing Writer-on-Behalf-Of publication mechanism requires no change, only re-verification that it continues to function correctly against the re-keyed Current Aggregate); `run_engine/core/trade_lifecycle.py` (AD-001, AD-005, AD-006 - already provides every field this Architecture requires; re-verified, not modified); `run_engine/core/pnl.py` (AD-007 - already provides the exact `pnl` value this Architecture requires; re-verified, not modified); `run_engine/core/execution/executor.py`, `run_engine/core/position.py`, `run_engine/core/risk.py`, `run_engine/core/strategy.py` (unaffected by any decision in this document, per AD-002/AD-003's own explicit finding that no new Execution-status or Position/Risk dependency is introduced); `run_engine/main.py` (unaffected).

**Components explicitly not to be changed:** `run_engine/runtime/performance_analytics.py`, `run_engine/execution/adapter.py`, `run_engine/feedback/tracker.py`, `run_engine/runtime/strategy_memory.py`, `StrategySelector.update` (AD-019 - all five remain confirmed-inactive, not reclassified or touched).

**New runtime or history objects potentially required:** a Performance History Record structure (AD-010), whose own concrete shape, storage mechanism, and accessor are deferred to the Specification stage; no new canonical (`CanonicalState`-published) object is required, since the Current Aggregate's own existing publication mechanism (AD-011) is reused unchanged in mechanism, only re-keyed.

**Decisions requiring a functional runtime change:** AD-001 (Performance Semantic Source), AD-004 (Performance Keying), AD-007 (Realized-PnL Attribution), AD-009 (Aggregation Semantics), AD-010 (Performance History, if implemented in this unit's own scope). Every other decision (AD-002, AD-003, AD-005, AD-006, AD-008, AD-011 through AD-022) ratifies already-conformant behaviour, establishes a Verification-Only or Governance-Only obligation (AD-020, AD-022), or is a documentation-only Cross-Unit ratification (AD-017, AD-019, AD-021), requiring no runtime code change on its own.

## 34. Non-Goals

Consistent with Section 3 and the governing task's own "Wichtige Grenzen": no Python signature, method body, or file diff is specified anywhere in this document; no Implementation Unit is defined; no test is designed as a fixed command; no Reporting module, UI, export mechanism, or persistence layer is implemented (AD-012, Constraint C-006); no Persistence, Recovery, or Schema Evolution mechanism beyond the explicitly-necessary Performance Observation/History shapes is designed (Constraint C-007 through C-009); no Operator Lifecycle Control mechanism is designed (Constraint C-010); no Position, PnL, or Risk formula or ownership decision is reopened (Constraint C-003, C-004); no Strategy Evaluation or optimization logic is introduced (Constraint C-005); no rollback, reset, or transaction mechanism is designed (Constraint C-013); no already-certified P2-02A, P2-03, P2-04, P3-01, or P3-02 decision is reopened; the Technical Debt Register is not modified (AD-022).

## 35. Internal Consistency Review

**Terminology consistency.** "Computational Authority," "Authoritative Owner," "Writer-on-Behalf-Of," "Producer," "Publication," "Storage," and "Consumption" are used exactly as defined in the Architecture Baseline throughout this document and are kept strictly separate in every Architecture Decision's own "Ownership Consequences," "Producer Consequences," "Consumer Consequences," and "Publication Consequences" fields; no decision conflates any two. "Decision," "Execution," "Lifecycle Transition," "Trade Outcome," and "Financial Outcome" are used exactly as defined in Section 6 throughout, kept strictly separate per AD-002. "Structural Independence" and "Composite Isolation" are used exactly as P3-02 already defines, not redefined. "Functionally identical" is used exclusively for runtime-object, dictionary, and result comparisons (Sections 22, 25 AD-018/AD-011 Acceptance Criteria); "byte-identical"/"byte-for-byte" is not used anywhere in this document as a comparison claim - the sole near-occurrence (AD-015's own Acceptance Criteria field draft) was caught and corrected during drafting to read "functionally identical," since no genuine file- or byte-sequence-level comparison is being made there.

**Ownership consistency.** No Architecture Decision in Section 25 introduces a new Authoritative Owner or Computational Authority anywhere in this document; every decision touching an existing object explicitly states so in its own "Ownership Consequences" field, satisfying Rule OM-009.

**Scope consistency.** No decision in Section 25 specifies a Python signature, a file diff, an Implementation Unit, or a test. Section 3 confirms P3-01 ordering, P3-02 isolation, P2-02A/P2-03/P2-04 formulas and ownership, TD-007, Reporting implementation, Persistence/Recovery/Schema Evolution, and Strategy Evaluation all remain untouched by any decision in this document.

**Performance-semantics consistency.** The four-concept separation (Decision, Execution, Lifecycle Transition, Trade Outcome) established by AD-002 is applied identically throughout every Model section (9-24) and every relevant AD's own "Performance-Semantic Consequences" field; no section conflates any two concepts.

**Lifecycle and Trade-Recognition consistency.** AD-006's own Open/Scale-In/Partial-Close/Full-Close boundaries are applied identically wherever Trade Recognition is discussed (Sections 11, 14, and the relevant AD's own fields); no section proposes a competing or inconsistent recognition rule.

**Financial-Attribution consistency.** AD-007's own "unchanged formula, corrected destination" principle is applied identically wherever Realized-PnL is discussed (Sections 12, and AD-007, AD-008, AD-009's own fields); `PnLEngine`'s own formula is never described as altered anywhere in this document.

**History and Reporting consistency.** AD-010's own Current-Aggregate/History separation and AD-012's own Reporting Boundary are applied identically wherever History or Reporting is discussed (Sections 15 through 17, and the relevant AD's own fields); no section proposes storing History inside `CanonicalState` or implementing a Reporting module.

**Ownership consistency (Performance-specific).** AD-013's own ratification and AD-019's own alternative-path exclusion are applied identically wherever Performance Ownership is discussed; no section grants Computational Authority to `StrategySelector` or `performance_analytics.py`.

**Determinism consistency.** AD-018's own extension of CAP-019/CAP-020 to the corrected mechanism is stated once, precisely, and referenced rather than restated with different wording elsewhere.

**Failure-semantics consistency.** AD-016 (Rejection/Runtime Failure Event) and AD-017 (Failed Tick) are kept explicitly, consistently distinct throughout; no section conflates a Failed Tick with a rejected lifecycle transition, and no section proposes a rollback/reset/transaction mechanism anywhere (Constraint C-013, verified by direct text search during drafting: no such term appears as a positive design proposal anywhere in Section 25).

**Traceability completeness.** Section 29 confirms all twenty-five FRA requirements; Section 30 confirms all fifty-five SDA dependencies; Section 31 confirms all twenty-nine CGA capabilities; cross-checked against Section 25's own twenty-two Architecture Decisions during drafting.

**No fabricated decision.** Every decision in Section 25 traces to a specific FRA requirement, SDA dependency, CGA capability, or Baseline ADR/AI/Rule text; no decision in this document addresses a concern absent from the governing baseline or the P3-03 governance chain's own prior documents.

Status: Internal Consistency Review PASS.

## 36. Architecture Readiness Decision

Every capability the CGA left open (CAP-005 through CAP-010, CAP-012, CAP-013, CAP-017, CAP-018, CAP-025, and the Governance dimension of CAP-029) has been explicitly decided (Section 31). Every Functional Gap the FRA and CGA jointly tracked (FG-001 through FG-005) is closed. All twenty-five FRA requirements, all fifty-five SDA dependencies, and all twenty-nine CGA capabilities are traced to at least one Architecture Decision or explicitly confirmed as ratified. Both Documentation Gaps (DG-001, DG-002) are explicitly resolved (AD-012, AD-001/AD-009); the Verification Gap (VG-001) has its own obligation established, mechanism deferred (AD-020). Both Residual Risks (RR-001, RR-002) remain explicitly, honestly documented as open, non-blocking, not silently presented as resolved (AD-017, AD-019). TD-004 is architecturally resolved within this unit's own scope, with the Technical Debt Register itself explicitly left unmodified pending Implementation and Final Certification (AD-022). No already-certified P2-02A, P2-03, P2-04, P3-01, or P3-02 contract is reopened.

**Architecture Readiness: READY.** This document is sufficient to proceed to the P3-03 Specification. No further architectural investigation is required before that step.

## 37. Closing Mechanical Verification

- File exists at the stated Primary Location: confirmed.
- ASCII-only: confirmed (see mechanical check output following this document's delivery).
- No trailing whitespace: confirmed.
- Continuous section numbering: Sections 1 through 40, no gaps, no duplicates.
- Full FR-ID traceability: Section 29 confirms all twenty-five FR-IDs individually cited.
- Full DEP-ID traceability: Section 30 confirms all fifty-five DEP-IDs individually cited.
- Full CAP-ID traceability: Section 31 confirms all twenty-nine CAP-IDs individually cited.
- Full AD-ID traceability: Section 25 defines AD-001 through AD-022, each individually cited in Sections 29-32.
- Full AI-ID traceability: Section 26 defines AI-001 through AI-015, each individually traced to its own governing AD.
- No accidental IU-ID: confirmed by construction (this document defines only AD- and AI-IDs, no Implementation Unit).
- No merge markers (`<<<<<<<`, `=======`, `>>>>>>>`): confirmed.
- No placeholder text (`TODO`, `TBD`, `FIXME`, `XXX`) other than this checklist's own literal mention of those tokens: confirmed.
- `python -m compileall run_engine`: PASS (no runtime file was touched by this document).
- `git diff --check`: clean for this new, untracked file.
- `git status --short`: unchanged from Section 5's own pre-check baseline plus this one new file.
- Branch: `run-engine-consolidation-safety` (unchanged).
- Local HEAD: `5f8be51ca216c77e6a1614c51e7f0ef5b35ccb01` (unchanged; no commit was made).
- Remote HEAD: `5f8be51ca216c77e6a1614c51e7f0ef5b35ccb01` (unchanged; no push was made).

## 38. Independent Self Verification

Every one of the twenty-two Architecture Decisions was checked, during this document's own closing review, against the specific FRA requirement, SDA dependency, or CGA capability it claims to resolve. The seven previously-MISSING and five previously-PARTIAL capabilities were each re-examined a second time to confirm the corresponding decision genuinely closes them rather than merely restating the gap. AD-004's own choice of Position Side over Decision Action, Execution Status, Regime, and Strategy Identity was independently re-derived from first principles against the governing task's own explicit eight-candidate list, confirming every rejected candidate carries an explicit, evidenced justification, not a bare assertion. AD-009's own resolution of Documentation Gap DG-002 ("Trade Count equals completed lifecycle outcomes," read as outcome-count rather than unique-trade-count) was independently re-checked against ADR-008's own literal text a second time to confirm the chosen reading is the textually minimal one, not a convenient one. AD-008's own resolution of CAP-012's interpretive ambiguity was independently re-examined to confirm the narrower reading was chosen for an internally consistent reason (avoiding Unrealized-PnL contamination via Equity's own formula), not arbitrarily. The five-path Alternative Performance Path disposition (AD-019) was independently re-verified against the CGA's own Section 25 findings, confirming no path's own classification was altered without justification. No error was found during this document's own closing review requiring correction before delivery.

## 39. Verification Report

Central architectural decisions: Performance's own normative basis becomes a Completed Lifecycle Outcome (`PARTIAL_CLOSE`/`TRADE_CLOSED`), not a raw Decision (AD-001); the Primary Aggregation Key becomes Position Side, not Decision Action (AD-004); the already-correct `PnLEngine`-computed Realized PnL value is re-attributed to the corrected bucket without any formula change (AD-007); a Performance History Model separates the Current Aggregate from individually-retained, non-canonical-state-stored History Records (AD-010); Unrealized PnL, Equity, and Drawdown remain explicitly excluded from Performance (AD-008); HOLD, NOOP, and `RUNTIME_FAILURE_EVENT` are excluded structurally, not by special-case branching (AD-015, AD-016); all five alternative/inactive Performance-adjacent paths remain individually classified, none reactivated (AD-019); TD-004 is architecturally resolved within P3-03's own scope, with the Technical Debt Register left explicitly unmodified (AD-022).

- Architecture Decisions: 22 (P3-03-AD-001 through P3-03-AD-022).
- P3-03-specific Invariants: 15 (P3-03-AI-001 through P3-03-AI-015).
- Functional-Gap Disposition: FG-001 closed (AD-001, AD-002, AD-009); FG-002 closed (AD-007); FG-003 closed (AD-010); FG-004 closed (AD-001, AD-002); FG-005 closed (AD-004, AD-006).
- TD-004 Disposition: architecturally resolved within P3-03's own scope (AD-022); Register unmodified, pending Implementation and Final Certification.
- Alternative-Path Disposition: 5 paths individually classified (Section 23, AD-019); none reactivated, none deleted.
- Implementation Impact (high level): one component (`run_engine/core/performance.py`) requires a functional runtime change; the call site's own signature is a Specification-level, not Architecture-level, question; nine components require verification only; five inactive paths remain untouched.
- Open Findings: Residual Risks RR-001 (orphaned `StrategySelector.update`) and RR-002 (Post-Exception Financial/Lifecycle Divergence) remain open, non-blocking, not resolved by this document; the concrete Performance History storage mechanism and the concrete verification procedure (AD-020) are both deferred to the Specification stage.
- Architecture Readiness: **READY** (Section 36).
- Changed files: exactly one, this new document
  (`docs/architecture/P3_03_PERFORMANCE_VALIDATION_ARCHITECTURE_V1_2026-07-13.md`).
- No runtime file was changed. No commit was created. No push occurred.

## 40. Stop Condition

This document concludes Stage 4 (Architecture) of the P3-03 governance chain. Per explicit instruction, the P3-03 Specification is not started in this document or in this session turn. No runtime file was modified. No commit was created. No push occurred.
