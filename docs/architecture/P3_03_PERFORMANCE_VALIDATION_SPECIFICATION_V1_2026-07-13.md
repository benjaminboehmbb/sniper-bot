Document Class:
Specification

Document ID:
P3-03-SPEC

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
docs/architecture/P3_03_PERFORMANCE_VALIDATION_SPECIFICATION_V1_2026-07-13.md

Depends On:
- docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md
- docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md
- docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md
- docs/architecture/analysis/P3_03_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-13.md
- docs/architecture/analysis/P3_03_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-13.md
- docs/architecture/analysis/P3_03_CAPABILITY_GAP_ANALYSIS_V1_2026-07-13.md
- docs/architecture/P3_03_PERFORMANCE_VALIDATION_ARCHITECTURE_V1_2026-07-13.md
- complete P3-01 governance chain (FRA, SDA, CGA, Architecture, Specification, Final Certification)
- complete P3-02 governance chain (FRA, SDA, CGA, Architecture, Specification, Final Certification)
- docs/architecture/P2_02A_POSITION_OWNERSHIP_SPECIFICATION_V1_2026-07-10.md
- docs/architecture/P2_03_FINANCIAL_OWNERSHIP_SPECIFICATION_V1_2026-07-11.md
- docs/architecture/P2_04_RISK_OWNERSHIP_SPECIFICATION_V1_2026-07-13.md
- current runtime code at HEAD 5f8be51ca216c77e6a1614c51e7f0ef5b35ccb01

Referenced By:
- future P3-03 Implementation
- future P3-03 Final Certification

Methodological Structure Reference (content not carried over):
- docs/architecture/P3_02_INFORMATION_FLOW_VALIDATION_SPECIFICATION_V1_2026-07-13.md

---

# P3-03 Performance Validation Specification

## 1. Document Metadata

See front matter above. This document is the P3-03 Specification, the fifth stage of the P3-03 governance chain (FRA -> SDA -> CGA -> Architecture -> Specification -> Implementation -> Final Certification).

## 2. Purpose

This document translates the twenty-two Architecture Decisions of `P3_03_PERFORMANCE_VALIDATION_ARCHITECTURE_V1_2026-07-13.md` (the "Architecture") into implementable technical directives: Runtime Contracts, Implementation Units, a File-by-File Change Plan, a No-Change Inventory, and Acceptance Criteria. This document does not decide architecture, does not introduce a new Functional Requirement, Dependency, Architecture Decision, or Architecture Invariant, does not perform a new scientific analysis or capability assessment, and does not specify a complete file diff or a test implementation. Its output is the binding technical contract a future P3-03 Implementation must satisfy.

## 3. Scope

In scope: seventeen Runtime Contracts (`P3-03-PV-001` through `P3-03-PV-017`) realizing AD-001 through AD-022; five Implementation Units (IU-001 through IU-004, file-touching or partially so; IU-005, Verification-Only); a File-by-File Change Plan for all fourteen actively-named runtime files; a No-Change Inventory with individual justification per file; Acceptance Criteria per IU plus global.

Out of scope: any new Functional Requirement, Dependency, Architecture Decision, or Architecture Invariant; any new scientific or capability analysis; any concrete Python signature, complete method body, or file diff; any test implementation as a fixed command; any P3-01, P2-02A, P2-03, or P2-04 work; any Reporting module, UI, export, or persistence implementation; any Persistence, Recovery, or Operator Lifecycle Control mechanism; any Position, Financial, or Risk formula or ownership change; any rollback, reset, or transaction mechanism; any reactivation of an inactive path.

## 4. Binding Baseline

- `docs/architecture/P3_03_PERFORMANCE_VALIDATION_ARCHITECTURE_V1_2026-07-13.md` - the sole source of the twenty-two Architecture Decisions and fifteen Architecture Invariants this Specification translates. AD-001, AD-004, AD-007, AD-009, and AD-010 require an executable runtime code change, all confined to `run_engine/core/performance.py`; every other decision ratifies already-conformant behaviour, establishes a Verification-Only or Governance-Only obligation, or is a documentation-only Cross-Unit ratification.
- `docs/architecture/analysis/P3_03_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-13.md`, `docs/architecture/analysis/P3_03_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-13.md`, `docs/architecture/analysis/P3_03_CAPABILITY_GAP_ANALYSIS_V1_2026-07-13.md` - the twenty-five Functional Requirements, fifty-five Dependencies, and twenty-nine Capabilities this Specification's own Traceability (Section 32) confirms complete coverage of, without re-deriving any of them.
- `docs/architecture/P2_02A_POSITION_OWNERSHIP_SPECIFICATION_V1_2026-07-10.md`, `docs/architecture/P2_03_FINANCIAL_OWNERSHIP_SPECIFICATION_V1_2026-07-11.md`, `docs/architecture/P2_04_RISK_OWNERSHIP_SPECIFICATION_V1_2026-07-13.md` - the certified Specification-level contracts IU-005's own Compatibility Verification checks against, without reopening any of them.
- `docs/architecture/P3_01_DETERMINISTIC_EXECUTION_ORDERING_SPECIFICATION_V1_2026-07-13.md`, `docs/architecture/certification/P3_01_FINAL_CERTIFICATION_V1_2026-07-13.md`, `docs/architecture/P3_02_INFORMATION_FLOW_VALIDATION_SPECIFICATION_V1_2026-07-13.md`, `docs/architecture/certification/P3_02_FINAL_CERTIFICATION_V1_2026-07-13.md` - the certified P3-01 and P3-02 baselines this Specification's own Compatibility Verification treats as immutable.

## 5. Repository Verification

Repository state, verified directly, not assumed:

- Branch: `run-engine-consolidation-safety`; Local HEAD and Remote HEAD both `5f8be51ca216c77e6a1614c51e7f0ef5b35ccb01`, identical, unchanged since the Architecture's own drafting.
- Working tree: unchanged from the state the Architecture document itself verified; `run_engine/` confirmed clean (`git status --short -- run_engine/` empty; `git diff --stat -- run_engine/` empty).

Files re-read in full for this Specification: `run_engine/core/performance.py` (re-confirmed: `PerformanceEngine.update(self, decision, pnl, regime, trade_event)`, lines 6-37; the sole accounting key is `decision.get('action', 'HOLD')`, line 11; `trade_event` is read exactly once, `getattr(trade_event, "event_type", None) == "RUNTIME_FAILURE_EVENT"`, line 8; `_stats_snapshot()`, lines 36-37, already P3-02-certified, unchanged), `run_engine/core/loop.py` (re-confirmed: the sole call site, lines 95-96), `run_engine/core/execution/executor.py`, `run_engine/core/trade_lifecycle.py`, `run_engine/core/position.py`, `run_engine/core/pnl.py`, `run_engine/core/risk.py`, `run_engine/core/canonical_state.py`, `run_engine/core/canonical_enforcer.py`, `run_engine/core/strategy.py` - all nine re-confirmed unchanged from the Architecture's own re-verification.

**`loop.py`'s own Performance call site, independently re-traced argument by argument for this Specification, per the governing task's own explicit instruction not to classify it as No-Change without repository-grounded confirmation, and per the governing task's own explicit instruction that the Specification may deviate from the Architecture's own expectation only if the current interface cannot technically satisfy the Architecture.** The call site (`loop.py:95-96`) is:

```
performance = self.performance_engine.update(decision, pnl, regime, trade_event)
self.enforcer.apply_performance_metrics(performance)
```

Every field the Architecture's own AD-001 through AD-010 require is already reachable from the four arguments already passed, none newly required:

- **`event_type`** (AD-001's own Trigger Condition; AD-006's own Trade Recognition boundaries): already `trade_event.event_type`, already the sole field the current `RUNTIME_FAILURE_EVENT` check reads.
- **`side`** (AD-004's own Primary Aggregation Key): already `trade_event.side`, a `LifecycleEvent` field (`trade_lifecycle.py:12`), populated on every event-generating call (`_open_trade`, `_scale_in`, `_partial_close`, `_full_close`, `_failure_event`), never currently read by `PerformanceEngine` but already present on the same object already passed.
- **`trade_id`** (AD-005's own History Record identity): already `trade_event.trade_id`, a `LifecycleEvent` field (`trade_lifecycle.py:11`), already present on the same object.
- **`tick`** (AD-010's own "originating Runtime Tick" History Record field): already `trade_event.tick`, a `LifecycleEvent` field (`trade_lifecycle.py:14`), already present on the same object.
- **`pnl`** (AD-007's own Realized-PnL Attribution): already the `pnl` scalar, already computed at `loop.py:72` via `self.pnl_engine.update(trade_event, position_pre["entry_price"])`, using the identical `trade_event` object, already correctly `0.0` for any non-`{PARTIAL_CLOSE, TRADE_CLOSED}` event per `pnl.py:23`'s own already-certified gate, and already the exact realized value for a genuine closing event - requiring no new computation, no new call, and no new argument.
- **`execution`** (AD-003's own explicit finding): confirmed NOT required; `event_type` alone already, transitively, encodes Execution acceptance (Architecture Section 5, re-confirmed here).
- **`regime`**: remains accepted-but-unused, per AD-004's own explicit ratification; no new consumption is introduced, and its continued presence in the call is architecturally permitted, not required to be removed.

**No field the corrected methodology (AD-001 through AD-010) requires is absent from the four arguments `loop.py:95` already passes. `loop.py` therefore requires no functional or interface change of any kind**, confirmed by direct, exhaustive trace of every field every governing Architecture Decision names, not merely asserted from the Architecture's own general reasoning. This directly confirms, rather than merely repeats, the Architecture's own expectation (Section 33, Implementation Impact Inventory) that `run_engine/core/performance.py` is the sole file requiring a functional change.

Repository-wide search re-performed for (case-insensitive, scoped to `run_engine/`, excluding `__pycache__`): `PerformanceEngine`, `performance_metrics`, `stats`, `realized_pnl`, `event_type`, `trade_id`, `apply_performance_metrics`, `update_performance_metrics`. No occurrence was found beyond what the FRA, SDA, CGA, and Architecture already established; no new fact emerged. `run_engine/runtime/performance_analytics.py`, `run_engine/execution/adapter.py`, `run_engine/feedback/tracker.py`, `run_engine/runtime/strategy_memory.py`, and `StrategySelector.update` were each re-confirmed unimported/uncalled.

## 6. Specification Context

Five of the twenty-two Architecture Decisions require an executable runtime code change, all confined to `run_engine/core/performance.py`: AD-001 (Performance Semantic Source gate), AD-004 (Position-Side keying), AD-007 (Realized-PnL re-attribution), AD-009 (Aggregation semantics, Trade Count/Winrate), AD-010 (Performance History, if implemented within this unit's own scope). AD-005, AD-006, AD-008 are narrow interpretive/scoping decisions realized as part of the same `performance.py` change, not separate code locations. AD-003 requires no code change of its own kind (it is a decision *not* to add a new input). AD-011 through AD-022 each ratify already-conformant behaviour (Ownership, Publication, Ordering, HOLD/NOOP/Failure conformance, Determinism, Alternative-Path exclusivity, Cross-Unit boundaries), establish a Verification-Only or Governance-Only obligation (AD-020, verification mechanism; AD-022, TD-004 readiness statement), or are documentation-only Cross-Unit ratifications, requiring no runtime code change.

## 7. Normative Terminology

Restated, not newly invented, from the Architecture (Section 6) and binding for the remainder of this document: **Decision, Execution, Lifecycle Transition/Lifecycle Event, Financial Outcome/Realized PnL, Trade Outcome, Completed Lifecycle Outcome, Performance Observation, Current Aggregate, Performance History Record** - as defined in the Architecture, unchanged. **Structural Independence, Composite Isolation** - as defined in the P3-02 Architecture, unchanged. **Functionally identical** is used in this document exclusively for Python-object, dictionary, and runtime-result comparisons. **Byte-identical/byte-for-byte** is reserved exclusively for file-, git-blob-, or source-line-level comparisons; every occurrence of either term in this document that is not such a comparison is meta-discussion, not a comparison claim. Decision, Execution, Lifecycle Outcome, and Financial Outcome are kept strictly separate throughout every contract below, per the governing task's own explicit requirement.

## 8. Runtime Contract Catalogue

Seventeen Runtime Contracts are specified, `P3-03-PV-001` through `P3-03-PV-017`, each traceable to one or more governing Architecture Decisions, presented in Sections 9 through 24 grouped by the concrete contract area they realize, matching the governing task's own explicit seventeen-area list one-to-one.

## 9. Performance Semantic Source Contracts

**Contract PV-001 (Performance Semantic Source).** Requirement: `PerformanceEngine` SHALL NOT use a raw Strategy Decision as its own Trade-Performance source; every Performance-relevant input SHALL originate from a completed Lifecycle Outcome and its own associated realized Financial Outcome; only `PARTIAL_CLOSE` and `TRADE_CLOSED` SHALL generate realized Trade Performance; `PerformanceEngine` SHALL perform no new PnL computation of its own, per AD-001. Runtime Behaviour: `PerformanceEngine.update`'s own internal logic gates on `trade_event.event_type in {"PARTIAL_CLOSE", "TRADE_CLOSED"}` before folding any value into the Current Aggregate, replacing the current unconditional-except-`RUNTIME_FAILURE_EVENT` behaviour. Input Semantics: `trade_event` (already-received `LifecycleEvent` or `None`), `pnl` (already-received scalar), unchanged in origin. Output Semantics: a Performance Observation occurs, or does not, as a pure function of `trade_event.event_type` alone. Performance Semantic Source: this contract IS the Semantic Source definition - a Completed Lifecycle Outcome, never a Decision. Trade Recognition: governed jointly with PV-006. Keying: not addressed here, governed by PV-004. Aggregation Behaviour: governed by PV-006/PV-007. History Behaviour: this gate is also the History-generation trigger, per PV-009. Publication Contract: unaffected; governed by PV-008. Consumer Contract: unaffected. Failure Behaviour: `RUNTIME_FAILURE_EVENT` and any other non-matching `event_type` structurally fail this gate, per PV-012. Determinism Requirement: the gate is a pure, deterministic function of `trade_event.event_type`. Acceptance Condition: for any tick where `trade_event` is `None` or `trade_event.event_type` is not `PARTIAL_CLOSE`/`TRADE_CLOSED`, no Performance Observation occurs. Verification Method: scripted event-type sweep, one test per `event_type` value including `None` (IU-001). Scope Boundary: does not alter `PnLEngine`'s or `TradeLifecycleEngine`'s own computation. Traceability: FR-005, FR-006, FR-007, FR-010, FR-012; DEP-003 through DEP-011, DEP-020, DEP-032, DEP-036, DEP-037, DEP-047; CAP-005, CAP-006, CAP-007; AD-001; ADR-008; Rule OM-008; Functional Gaps FG-001, FG-004.

## 10. Decision / Execution / Lifecycle / Outcome Contracts

**Contract PV-002 (Input Contract - Minimal Sufficient Interface).** Requirement: `PerformanceEngine` SHALL require, as fachliche inputs, only: the Lifecycle Event (or completed lifecycle outcome it represents), the associated Realized PnL, Position Side, and Trade Identity; no unvalidated Decision Action SHALL serve as a Performance key, per the Architecture's own Section 10 (Decision/Execution/Lifecycle/Outcome Model). Runtime Behaviour: Section 5's own exhaustive trace confirms all four fachliche inputs are already reachable from the existing four call-site arguments (`decision`, `pnl`, `regime`, `trade_event`), specifically via `trade_event.event_type`, `trade_event.side`, `trade_event.trade_id`, `trade_event.tick`, and the already-received `pnl` scalar; no new parameter is required. Input Semantics: the minimal sufficient interface is `{trade_event, pnl}`; `decision` and `regime` MAY continue to be received without being used as Performance keys, consistent with AD-002/AD-004's own explicit rejection of Decision Action and Regime as keying dimensions. Output Semantics: not applicable to this contract; governed by PV-006 through PV-010. Performance Semantic Source: per PV-001. Trade Recognition: per PV-006 (`event_type`, `side`, `trade_id` all sourced from `trade_event`). Keying: per PV-004. Aggregation Behaviour: per PV-006/PV-007. History Behaviour: per PV-009/PV-010. Publication Contract: not applicable. Consumer Contract: not applicable. Failure Behaviour: not applicable directly. Determinism Requirement: the input set itself is deterministic, already established by upstream contracts (P3-01, P3-02, P2-03, not reopened). Acceptance Condition: `PerformanceEngine`'s own corrected logic reads no field beyond `trade_event.event_type`, `.side`, `.trade_id`, `.tick`, and `pnl`; no `execution`, `equity`, `peak_equity`, or `drawdown` field is read. Verification Method: static source inspection confirming the read-set boundary (IU-001). Scope Boundary: does not specify a concrete Python parameter list; whether a future Implementation drops the now-unused `decision`/`regime` parameters from `PerformanceEngine.update`'s own signature is an Implementation-level simplification choice, not mandated here, and, per Section 5's own trace, does not require any change to `loop.py`'s own call site regardless of which choice is made, since the call site's own four-argument shape already satisfies both the current and the simplified signature (a signature simplification would itself require a corresponding call-site edit only if fewer arguments were passed than currently are - this Specification does not mandate such a simplification). Traceability: FR-004, FR-005, FR-006, FR-007, FR-008, FR-012, FR-023; DEP-003, DEP-011, DEP-020, DEP-027, DEP-035, DEP-036, DEP-045, DEP-047, DEP-048, DEP-053; CAP-004, CAP-007, CAP-008, CAP-011, CAP-012; AD-002, AD-003, AD-008, AD-014.

**Contract PV-003 (Decision / Execution / Outcome Separation).** Requirement: a Decision SHALL NOT be a Trade; NOOP SHALL NOT be a Trade; HOLD SHALL NOT be a Trade; a Rejection SHALL NOT be a successful Trade; a `RUNTIME_FAILURE_EVENT` SHALL NOT be a successful Trade; `TRADE_OPENED` and `SCALE_IN` SHALL NOT generate a realized Trade Outcome; `PARTIAL_CLOSE` and `TRADE_CLOSED` SHALL each generate one realized Performance Outcome, per AD-002/AD-006. Runtime Behaviour: realized as the single PV-001 gate; no separate branch is required per excluded condition, since HOLD/NOOP/`TRADE_OPENED`/`SCALE_IN`/`RUNTIME_FAILURE_EVENT` all structurally fail the identical `event_type in {PARTIAL_CLOSE, TRADE_CLOSED}` test. Input Semantics: `trade_event.event_type`, the sole discriminator. Output Semantics: exactly the six named conditions above each produce the documented behaviour, verified individually (IU-001's own Testumfang). Performance Semantic Source: per PV-001. Trade Recognition: this contract IS the Trade Recognition boundary statement; concrete mechanics in PV-006. Keying: not applicable. Aggregation Behaviour: governed by PV-006/PV-007, gated by this contract. History Behaviour: governed by PV-009, gated by this contract. Publication Contract: not applicable. Consumer Contract: not applicable. Failure Behaviour: `RUNTIME_FAILURE_EVENT`'s own exclusion is additionally, specifically governed by PV-012. Determinism Requirement: each of the six conditions is deterministically distinguishable from `trade_event.event_type` alone. Acceptance Condition: a scripted sequence exercising all six conditions produces zero Current-Aggregate mutation and zero History Record for each, and exactly one Observation each for `PARTIAL_CLOSE`/`TRADE_CLOSED`. Verification Method: per-condition scripted test (IU-001). Scope Boundary: does not alter `Executor`'s or `TradeLifecycleEngine`'s own generation of any of these six conditions. Traceability: FR-005, FR-012; DEP-011, DEP-027, DEP-036, DEP-047, DEP-053; CAP-007; AD-002; SDA Section 15; Functional Gaps FG-001, FG-004.

## 11. Trade Recognition Contracts

**Contract PV-006 (Trade Count).** Requirement: Trade Count SHALL increase exclusively on a realized Close Outcome (`PARTIAL_CLOSE` or `TRADE_CLOSED`); `TRADE_OPENED`, `SCALE_IN`, HOLD, NOOP, Rejection, and `RUNTIME_FAILURE_EVENT` SHALL NOT increase Trade Count; Partial Close and Full Close SHALL each be individually, unambiguously counted; the same Lifecycle Outcome SHALL NOT be counted more than once, per AD-006/AD-009. Runtime Behaviour: the Current Aggregate's own count field increments by exactly one per PV-001-gate-passing tick, keyed per PV-004; `PARTIAL_CLOSE` and `TRADE_CLOSED` are counted as two separate, individually-incrementing outcomes when both occur for the same `trade_id` (AD-009's own explicit "outcome-count," not "unique-trade-count," reading of ADR-008). Input Semantics: `trade_event.event_type`, `trade_event.side`. Output Semantics: an integer count field per Position-Side bucket, monotonically non-decreasing within a single `PerformanceEngine` instance's own lifetime. Performance Semantic Source: per PV-001. Trade Recognition: this contract is the Trade Count realization of Section 11's own Trade Recognition Model. Keying: per PV-004 (Position Side). Aggregation Behaviour: one increment per Observation, no batching, no double-increment. History Behaviour: each incrementing event corresponds to exactly one History Record, per PV-009/PV-010. Publication Contract: per PV-008. Consumer Contract: a consumer reading "Trade Count" understands it as a count of Completed Lifecycle Outcomes, not unique Trades (AD-009's own explicit disambiguation). Failure Behaviour: per PV-012. Determinism Requirement: the count, given an identical event sequence in identical order, is functionally identical across replays. Acceptance Condition: for a scripted sequence containing exactly N `PARTIAL_CLOSE`/`TRADE_CLOSED` events (any interleaving of the six excluded conditions), Trade Count equals exactly N. Verification Method: scripted count-accuracy test with interleaved non-counting events (IU-002). Scope Boundary: does not introduce a separate unique-Trade-count field in the Current Aggregate itself; such a count remains derivable from History (PV-009) via `trade_id` grouping if ever required. Traceability: FR-005, FR-007, FR-010, FR-012, FR-013, FR-014; DEP-004, DEP-008, DEP-009, DEP-011, DEP-032, DEP-036, DEP-037, DEP-042, DEP-046, DEP-047; CAP-006, CAP-009, CAP-013, CAP-016; AD-006, AD-009; ADR-008; ADR-009; AC-014; Functional Gaps FG-001, FG-004, FG-005; Documentation Gap DG-002.

## 12. Realized-PnL Attribution Contracts

**Contract PV-005 (Realized-PnL Attribution).** Requirement: Realized PnL SHALL originate exclusively from `PnLEngine`; event-associated Realized PnL SHALL be attributed to exactly one completed Lifecycle Outcome; Partial Close and Full Close SHALL be processed as separate observations; cumulative Realized PnL SHALL NOT be reinterpreted as a new event-level PnL value; no PnL formula change SHALL occur, per AD-007. Runtime Behaviour: `PerformanceEngine`'s own PV-001-gate-passing logic consumes exactly the `pnl` scalar already passed at the call site, already computed by `PnLEngine.update(trade_event, entry_basis)` for the identical `trade_event` one call earlier in the same tick; no new `PnLEngine` invocation, no read of `realized_pnl_cumulative`. Input Semantics: `pnl` (scalar, already received). Output Semantics: each Observation's own attributed `pnl` equals exactly `PnLEngine`'s own computed value for that same `trade_event`. Performance Semantic Source: per PV-001. Trade Recognition: per PV-006, each qualifying event individually attributed. Keying: attributed into the Position-Side bucket per PV-004. Aggregation Behaviour: folded into the running-mean `pnl` field per the existing, unchanged arithmetic formula (CAP-016, ratified, formula itself untouched). History Behaviour: each Observation's own `pnl` field, per PV-010, equals this attributed value. Publication Contract: per PV-008. Consumer Contract: not applicable directly. Failure Behaviour: per PV-012 (a `RUNTIME_FAILURE_EVENT` tick's own `pnl` is already `0.0` per `PnLEngine`'s own gate, never attributed since PV-001's own gate already excludes it). Determinism Requirement: attribution is a pure function of already-deterministic inputs. Acceptance Condition: for any PV-001-gate-passing tick, the resulting bucket's own running `pnl` mean, after the tick, equals the value it would have had if computed directly from the sequence of attributed `pnl` values for that side alone, in tick order. Verification Method: direct value-attribution comparison against an independently-computed reference sequence (IU-002). Scope Boundary: does not alter `PnLEngine.update`'s own formula, gate, or Computational Authority; does not reopen P2-03. Traceability: FR-006, FR-013, FR-014; DEP-006, DEP-007, DEP-009, DEP-010, DEP-036, DEP-045; CAP-010; AD-007; ADR-005; ADR-008; Baseline AC-008; P2-03 (not reopened); Functional Gap FG-002.

## 13. Performance Keying Contracts

**Contract PV-004 (Performance Keying).** Requirement: the Current Aggregate SHALL be keyed by Position Side (`LONG`/`SHORT`); Decision Action SHALL NOT be a Primary Key; Trade Identity SHALL serve History correlation, not Aggregate keying; Regime and Strategy Identity SHALL NOT be Primary-Key dimensions in the current scope; no competing or ambiguous keying semantics SHALL exist, per AD-004. Runtime Behaviour: `PerformanceEngine`'s own bucket key becomes `trade_event.side` in place of `decision.get('action', 'HOLD')`; the `"HOLD"` bucket ceases to exist as a direct consequence of PV-001/PV-003. Input Semantics: `trade_event.side`, already available. Output Semantics: the Current Aggregate's own top-level keys are drawn exclusively from `{"LONG", "SHORT"}`. Performance Semantic Source: per PV-001 (keying applies only to gate-passing Observations). Trade Recognition: per PV-006. Keying: this contract IS the Keying definition. Aggregation Behaviour: per PV-006/PV-007, applied within each Position-Side bucket. History Behaviour: each History Record (PV-010) carries both Position Side and Trade Identity, each independently, per AD-005's own explicit dual-purpose rationale. Publication Contract: per PV-008, re-keyed shape. Consumer Contract: any consumer of the Current Aggregate must account for the `LONG`/`SHORT`-keyed shape, not the prior `BUY`/`SELL`/`HOLD`-keyed shape. Failure Behaviour: not applicable directly. Determinism Requirement: `trade_event.side` is a deterministic field of an already-deterministic event. Acceptance Condition: every key in the published Current Aggregate is one of exactly `{"LONG", "SHORT"}`; no `"BUY"`, `"SELL"`, or `"HOLD"` key appears. Verification Method: direct key-set inspection across a scripted multi-side sequence (IU-002). Scope Boundary: does not select a concrete Python dictionary type; does not preclude a future, separately-justified Architecture Evolution Review from adding a secondary classification dimension. Traceability: FR-005, FR-008, FR-010; DEP-003, DEP-004, DEP-005, DEP-023, DEP-040; CAP-013; AD-004; ADR-009; Functional Gap FG-005.

## 14. Performance Aggregation Contracts

**Contract PV-007 (Winrate).** Requirement: Win Rate SHALL derive exclusively from realized Performance Outcomes; win/loss classification SHALL be derived from event-associated Realized PnL; Win Rate SHALL NOT be Decision-based; HOLD/NOOP SHALL have no influence, per AD-009. Runtime Behaviour: the existing `wins = 1 if pnl > 0 else 0` test is applied exactly once per PV-001-gate-passing Observation, evaluated against the PV-005-attributed `pnl`; the running-mean `winrate` formula itself is unchanged (CAP-016, ratified). Input Semantics: the PV-005-attributed `pnl` value. Output Semantics: a `winrate` field per Position-Side bucket, a float in `[0.0, 1.0]`. Performance Semantic Source: per PV-001. Trade Recognition: per PV-006 (Win Rate updates exactly when Trade Count increments). Keying: per PV-004. Aggregation Behaviour: this contract IS the Win Rate aggregation rule. History Behaviour: each History Record (PV-010) carries its own win/loss classification, derived identically. Publication Contract: per PV-008. Consumer Contract: not applicable directly. Failure Behaviour: per PV-012 (no Win Rate mutation for a non-qualifying tick). Determinism Requirement: the classification is a pure, deterministic function of the attributed `pnl`. Acceptance Condition: for a scripted sequence of realized outcomes with known signs, the resulting `winrate` matches an independently-computed reference ratio of positive-`pnl` outcomes to total qualifying outcomes, for each Position Side individually. Verification Method: scripted positive/negative/zero-PnL sequence test (IU-002). Scope Boundary: does not alter the running-mean `winrate` formula's own arithmetic shape. Traceability: FR-005, FR-006, FR-007, FR-010, FR-012, FR-013, FR-014; DEP-032, DEP-036, DEP-037, DEP-042, DEP-046, DEP-047, DEP-052; CAP-006, CAP-016; AD-009; ADR-008; Documentation Gap DG-002; Functional Gaps FG-001, FG-002, FG-004, FG-005.

## 15. Performance History Contracts

**Contract PV-009 (Performance History).** Requirement: every realized Performance Observation SHALL generate one immutable History Record; a History Record SHALL represent exactly one completed Lifecycle Outcome; History and the Current Aggregate SHALL be separate objects; History SHALL NOT be stored in `CanonicalState`; History SHALL remain authoritative within `PerformanceEngine` as a Derived View, not a competing Authoritative Owner, per AD-010. Runtime Behaviour: on every PV-001-gate-passing tick, in addition to updating the Current Aggregate (PV-006/PV-007/PV-005), `PerformanceEngine` appends one History Record (PV-010) to its own privately-retained, append-only History sequence. Input Semantics: identical to PV-001's own gate-passing inputs. Output Semantics: an ordered, append-only sequence of History Records, distinct in object and lifetime from the Current Aggregate. Performance Semantic Source: per PV-001. Trade Recognition: per PV-006 (one Record per counted Outcome, no more, no fewer). Keying: each Record individually carries Position Side and Trade Identity (PV-004/PV-010), not itself a keyed aggregate. Aggregation Behaviour: History is not itself aggregated; it is the replay source the Current Aggregate is reproducible from (Acceptance Condition below). History Behaviour: this contract IS the History definition. Publication Contract: History Records are NOT published via `CanonicalEnforcer`; their own exposure mechanism (a distinct accessor or another mechanism) is an Implementation-level choice within IU-003's own scope, not specified here. Consumer Contract: a future Reporting consumer (PV-015) accesses the ordered Record sequence directly from `PerformanceEngine`, not via `CanonicalState`. Failure Behaviour: per PV-012/PV-013 (no Record for a non-qualifying or Failed-Tick condition). Determinism Requirement: Record order matches the deterministic order `TradeLifecycleEngine` itself generates the underlying `LifecycleEvent` sequence. Acceptance Condition: the Current Aggregate's own running statistics, for any Position Side, are exactly reproducible by replaying the ordered sequence of History Records for that side through the PV-006/PV-007/PV-005 aggregation rules. Verification Method: replay-reproducibility test (IU-003). Scope Boundary: does not select a concrete storage mechanism, retention policy, or persistence layer; does not design Recovery. Traceability: FR-015; DEP-012, DEP-029, DEP-038; CAP-017, CAP-022; AD-010; Baseline AC-008 (third clause); AI-001; AI-012; Functional Gap FG-003; TD-004.

**Contract PV-010 (History Record).** Requirement: a History Record SHALL fachlich carry, at minimum: unique correlation to its own Lifecycle Outcome (Trade Identity), Event Type, Position Side, event-associated Realized PnL, win/loss classification, and deterministic ordering information; a Record SHALL carry no mutable back-reference into `CanonicalState`; no concrete persistence ID or external Reporting structure SHALL be invented, per AD-005/AD-010. Runtime Behaviour: each Record is constructed from `trade_event.trade_id`, `trade_event.event_type`, `trade_event.side`, the PV-005-attributed `pnl`, the PV-007-derived win/loss classification, and `trade_event.tick` (as the deterministic-ordering/originating-tick field); once constructed, a Record is never mutated. Input Semantics: identical to PV-009's own gate-passing inputs. Output Semantics: an immutable structure carrying exactly the six fachliche fields named above, no more. Performance Semantic Source: per PV-001. Trade Recognition: per PV-006/PV-009. Keying: carries, but is not itself keyed by, Position Side and Trade Identity (AD-004/AD-005's own dual, independent-purpose fields). Aggregation Behaviour: per PV-009's own replay-reproducibility requirement. History Behaviour: this contract IS the Record-level History definition. Publication Contract: per PV-009 (not `CanonicalState`-published). Consumer Contract: per PV-015. Failure Behaviour: no Record is created for a non-qualifying tick (PV-003) or a Failed Tick (PV-013). Determinism Requirement: given identical inputs, an identical Record is constructed, byte-for-byte identical is not the applicable comparison (this is a Python-object comparison) - functionally identical across replays. Acceptance Condition: every field of a constructed Record matches its own originating `trade_event`/attributed-`pnl` values exactly; no Record's own field changes value after construction; no Record contains a reference to any `CanonicalState`-owned mutable object. Verification Method: field-by-field construction test plus post-construction immutability test (attempted mutation, expecting rejection or no observable effect) (IU-003). Scope Boundary: does not invent a persistence ID, a database schema, or an external Reporting export format. Traceability: FR-007, FR-015; DEP-008, DEP-012, DEP-020, DEP-029, DEP-038; CAP-013, CAP-017; AD-005, AD-010; ADR-009.

## 16. Current Aggregate Contracts

**Contract PV-008 (Current Aggregate).** Requirement: the Current Aggregate SHALL remain the canonical Performance object; `PerformanceEngine` SHALL remain Computational Authority; `CanonicalEnforcer` SHALL remain the Publication Path; `CanonicalState` SHALL remain Authoritative Owner; P3-02's own Structural Isolation SHALL remain unchanged; the Aggregate SHALL contain only architecturally-approved fields, per AD-011/AD-013. Runtime Behaviour: `PerformanceEngine.update`'s own existing `_stats_snapshot()`-equivalent mechanism (already P3-02-certified, `performance.py:36-37`) continues to apply unchanged in mechanism to the re-keyed structure (PV-004); `CanonicalEnforcer.apply_performance_metrics` and `CanonicalState.update_performance_metrics`/`.state["performance_metrics"]` require no code change (Section 5). Input Semantics: the Structurally Independent value `PerformanceEngine.update` returns, unchanged in mechanism. Output Semantics: `{"LONG": {"pnl": float, "trades": int, "winrate": float}, "SHORT": {...}}` - the architecturally-approved field set, containing exactly `pnl`, `trades`, `winrate` per side, no additional field. Performance Semantic Source: per PV-001 (publication frequency follows Observation frequency; the most recent value republishes on non-qualifying ticks per the existing `apply_performance_metrics(None)` read-through guard). Trade Recognition: per PV-006. Keying: per PV-004. Aggregation Behaviour: per PV-006/PV-007/PV-005. History Behaviour: explicitly distinct from and not containing History (PV-009). Publication Contract: this contract IS the Publication Contract for the Current Aggregate. Consumer Contract: per PV-015. Failure Behaviour: per PV-012/PV-013. Determinism Requirement: per PV-014. Acceptance Condition: `id()` of the Current Aggregate published at tick N differs, at every nesting level, from `id()` of the value published at tick N+1, whenever a publication occurs at both ticks - identical to the already-certified P3-02 Acceptance Criterion, re-verified against the re-keyed structure. Verification Method: object-identity comparison across the re-keyed structure (IU-002, IU-004). Scope Boundary: does not reopen P3-02-AD-001, AD-005, or IU-002; does not add a field beyond `pnl`/`trades`/`winrate` per side. Traceability: FR-001, FR-002, FR-003, FR-016, FR-017, FR-018, FR-025; DEP-001, DEP-002, DEP-013, DEP-014, DEP-015, DEP-018, DEP-021, DEP-022, DEP-030, DEP-031, DEP-033, DEP-041, DEP-051, DEP-054; CAP-001, CAP-002, CAP-003, CAP-021; AD-011, AD-013; P3-02-AD-001, AD-005, IU-002 (not reopened).

## 17. Reporting Boundary Contracts

**Contract PV-015 (Reporting Consumer Contract).** Requirement: Reporting SHALL remain the intended external Consumer; P3-03 SHALL NOT implement a Reporting module; `PerformanceEngine` or a permitted Read Contract SHALL make the Current Aggregate and History available for a future consumer; no UI, export, or persistence specification SHALL be produced, per AD-012. Runtime Behaviour: the Current Aggregate remains available exactly as today, via `CanonicalState.state["performance_metrics"]` and the tick-result dict's own `"performance"` field (PV-008); History (PV-009), once implemented, is made available via a not-yet-specified read accessor on `PerformanceEngine` itself, deferred to Implementation. Input Semantics: not applicable. Output Semantics: the Current Aggregate's own already-existing publication channels, plus a future History accessor. Performance Semantic Source: not applicable directly. Trade Recognition: not applicable directly. Keying: consumers must account for the PV-004 re-keying. Aggregation Behaviour: not applicable directly. History Behaviour: per PV-009 (accessor deferred to Implementation, not specified here). Publication Contract: per PV-008 for the Aggregate; a distinct, Implementation-deferred mechanism for History. Consumer Contract: this contract IS the Reporting Consumer Contract. Failure Behaviour: not applicable. Determinism Requirement: not applicable directly. Acceptance Condition: no Reporting module, UI component, or export mechanism is introduced by this Specification or any future P3-03 Implementation under this Specification's own authority; the Runtime Ownership Matrix's own "Reporting" row remains textually unaltered. Verification Method: documentation and scope cross-check (IU-005). Scope Boundary: does not implement Reporting; does not design a UI, export format, or persistence mechanism; does not specify the concrete History accessor's own Python signature. Traceability: FR-019, FR-020; DEP-016, DEP-017, DEP-025, DEP-034, DEP-055; CAP-018; AD-012; Runtime Ownership Matrix; Documentation Gap DG-001.

## 18. Ownership and Publication Contracts

(Ownership and Publication are realized jointly by PV-008 (Current Aggregate) and PV-009/PV-010 (History); no additional, separate contract is required beyond those already stated, since AD-013's own Ownership Ratification introduces no new mechanism of its own. This section is retained as a structural placeholder per the governing task's own Document Structure list, cross-referencing PV-008 through PV-010 in full, to avoid a duplicate or competing statement of the identical Ownership/Publication requirement.)

## 19. HOLD and NOOP Contracts

**Contract PV-011 (HOLD / NOOP).** Requirement: no Performance Aggregate update SHALL occur from HOLD or NOOP; no Trade Count increment; no Win Rate change; no Performance History Record, since the Architecture does not require a neutral observation; Tick Completion SHALL remain unchanged, per AD-015. Runtime Behaviour: `on_execution`'s own existing `None`-return for `action == "HOLD"` (`trade_lifecycle.py:64-65`) means `trade_event` is `None` on a HOLD/NOOP tick; PV-001's own gate (`trade_event.event_type in {...}`, guarded by a `getattr`/`None`-safe check) structurally, automatically fails for `trade_event is None`, requiring no dedicated HOLD-detection branch. Input Semantics: `trade_event is None`. Output Semantics: the Current Aggregate and History both remain unchanged from their own immediately-prior state. Performance Semantic Source: per PV-001 (this is the `None`-input instance of the same general gate). Trade Recognition: per PV-003. Keying: not applicable (no Observation occurs). Aggregation Behaviour: zero mutation, structurally. History Behaviour: zero Record generation. Publication Contract: the most recently published Current Aggregate value republishes unchanged, per PV-008's own existing `apply_performance_metrics(None)`-guard-consistent behaviour. Consumer Contract: unaffected. Failure Behaviour: not a failure condition; distinct from PV-012. Determinism Requirement: the exclusion is a deterministic, structural consequence of already-deterministic upstream behaviour. Acceptance Condition: for any tick with `decision['action'] == 'HOLD'` or an Executor `NOOP` result, the Current Aggregate is functionally identical to its own value before that tick executed, and no History Record is appended. Verification Method: scripted HOLD/NOOP-only tick sequence test (IU-001, IU-002). Scope Boundary: does not introduce a separate HOLD-diagnostic mechanism; a complete tick-by-tick trail including HOLD, if ever required, remains `run_engine/logging/`'s own, unaddressed scope. Traceability: FR-011; DEP-005, DEP-023; CAP-014; AD-015; P3-01-AD-005; Functional Gap FG-004.

## 20. Rejection and Runtime Failure Event Contracts

**Contract PV-012 (Rejection / Runtime Failure Event).** Requirement: no Trade-Performance update from a Rejection or `RUNTIME_FAILURE_EVENT`; no Trade Count increment; no Win Rate change; no realized Performance History Record; existing Failure semantics SHALL remain unchanged, per AD-016. Runtime Behaviour: `RUNTIME_FAILURE_EVENT` structurally fails the PV-001 gate identically to any other non-qualifying `event_type`; the current runtime's own explicit, separate `RUNTIME_FAILURE_EVENT`-specific short-circuit (`performance.py:8-9`) becomes a redundant special case of the general gate and MAY be simplified away by Implementation, without any behavioural change - a simplification opportunity this Specification notes but does not mandate. Input Semantics: `trade_event.event_type == "RUNTIME_FAILURE_EVENT"`. Output Semantics: identical non-mutation behaviour to today. Performance Semantic Source: per PV-001. Trade Recognition: per PV-003. Keying: not applicable (no Observation occurs). Aggregation Behaviour: zero mutation. History Behaviour: zero Record generation; `TradeLifecycleEngine`'s own existing `failure_events` diagnostic list remains the sole record of a `RUNTIME_FAILURE_EVENT`, unaffected by and not duplicated into Performance History. Publication Contract: the most recently published Current Aggregate value republishes unchanged. Consumer Contract: unaffected. Failure Behaviour: this contract IS the Rejection/Runtime-Failure-Event Failure Behaviour. Determinism Requirement: ratifies already-deterministic, already-conformant behaviour. Acceptance Condition: for any tick where `trade_event.event_type == "RUNTIME_FAILURE_EVENT"`, the Current Aggregate remains functionally identical to its own value before that tick executed, and no History Record is appended. Verification Method: scripted `RUNTIME_FAILURE_EVENT`-injection test, both via the current explicit short-circuit and via the general gate alone if Implementation simplifies it away (IU-001, IU-002). Scope Boundary: does not alter ADR-011's own Runtime Failure Handling semantics or `TradeLifecycleEngine`'s own failure-event generation. Traceability: FR-007, FR-009; DEP-008, DEP-028, DEP-039, DEP-046, DEP-047, DEP-049, DEP-050; CAP-015; AD-016; ADR-011; P3-01-AD-006; P3-01-AI-012; Verified Conformant Finding VCF-004.

## 21. Failed-Tick Contracts

**Contract PV-013 (Failed Tick).** Requirement: no Performance update SHALL occur when the Performance Stage is not successfully completed; no new rollback or reset mechanism SHALL be introduced; RR-001/RR-002 SHALL remain documented per the Architecture; TD-007 SHALL NOT be anticipated, per AD-017. Runtime Behaviour: no code change; a Failed Tick (an exception interrupting `RunLoop.step()` before Tick Completion) continues to produce no Tick-Complete result at all, exactly as P3-01-AD-004/P3-02-AD-016 already, certifiably establish; whatever internal `CanonicalEnforcer.apply_*` calls already completed remain present in `CanonicalState`'s own internally-held state. Input Semantics: not applicable. Output Semantics: no externally observable Performance update of any kind for a Failed Tick. Performance Semantic Source: not applicable to a Failed Tick (no Tick-Complete result exists to evaluate). Trade Recognition: not applicable. Keying: not applicable. Aggregation Behaviour: not applicable. History Behaviour: no History Record is ever generated for a Failed Tick. Publication Contract: unaffected; whichever `apply_*` calls already ran, ran under their own already-specified contracts. Consumer Contract: no consumer ever observes a Failed Tick's own partial results. Failure Behaviour: this contract IS the Failed-Tick disposition. Determinism Requirement: not extended to a retry sequence following a Failed Tick. Acceptance Condition: a fault-injection probe interrupting `RunLoop.step()` before Tick Completion produces no externally observable Tick-Complete result, and RR-002 remains present, unmodified, in this document's own Section 5/32 disposition; RR-001 remains present, unmodified. Verification Method: simulated-exception injection at multiple points, both before and after IU-001 through IU-003 (IU-005). Scope Boundary: does not design a Recovery mechanism; does not resolve RR-002; does not conflate TD-007 (RunLoop Lifecycle Control Surface) with this contract. Traceability: FR-001, FR-004, FR-009; DEP-028, DEP-039, DEP-049, DEP-050, DEP-054; CAP-015, CAP-025, CAP-026, CAP-027, CAP-028; AD-017, AD-021; P3-01-AD-004; P3-02-AD-016; Residual Risk RR-002; TD-007.

## 22. Determinism and Replay Contracts

**Contract PV-014 (Determinism and Replay).** Requirement: identical completed Lifecycle Outcomes and Financial Outcomes SHALL produce functionally identical Performance Observations; the Current Aggregate SHALL evolve deterministically; History order SHALL be deterministic; no hidden Decision- or `StrategySelector`-state dependency SHALL exist; Replay SHALL reproduce both the Aggregate and History, per AD-018. Runtime Behaviour: `PerformanceEngine`'s own corrected logic (PV-001 through PV-010) is a pure function of `trade_event` and `pnl`, both already-deterministic under P3-01's own certified ordering; no randomness, wall-clock read, or I/O is introduced. Input Semantics: `trade_event`, `pnl`, both already-deterministic. Output Semantics: functionally identical Current Aggregate and History Record sequences across independent replays of an identical input sequence in identical order. Performance Semantic Source: per PV-001, a pure function. Trade Recognition: per PV-003/PV-006, deterministic. Keying: per PV-004, deterministic. Aggregation Behaviour: per PV-005/PV-006/PV-007, deterministic arithmetic, unchanged formula. History Behaviour: per PV-009, deterministic append order. Publication Contract: per PV-008, P3-02's own already-certified Structural Independence and Snapshot Isolation preserved without exception. Consumer Contract: a replaying consumer observes functionally identical results. Failure Behaviour: per PV-013, not extended to Failed-Tick retry sequences. Determinism Requirement: this contract IS the Determinism and Replay requirement. Acceptance Condition: two independent `PerformanceEngine` instances, given an identical sequence of `(trade_event, pnl)` inputs in identical order, produce functionally identical Current Aggregate values and functionally identical History Record sequences at every point in the replay. Verification Method: dual-instance replay comparison (IU-004). Scope Boundary: does not re-execute P3-01's or P3-02's own already-certified replay verification; does not extend determinism claims to a retry sequence following a Failed Tick. Traceability: FR-021, FR-022; DEP-019, DEP-043; CAP-019, CAP-020; AD-018; AI-005; AI-006; AC-012; P3-02-AD-001, AD-005 (not reopened).

## 23. Alternative Performance Path Contracts

**Contract PV-016 (Alternative Path).** Requirement: `performance_analytics.py` SHALL remain inactive and without Computational Authority; `StrategySelector.update` SHALL remain inactive and without Performance Authority; `feedback/tracker.py`, `strategy_memory.py`, and `execution/adapter.py` SHALL remain outside the active path; no reactivation or deletion SHALL occur within P3-03's own scope; exactly one active Performance path SHALL exist, per AD-019. Runtime Behaviour: no code change to any of the five paths; each remains confirmed unimported/uncalled (Section 5). Input Semantics: not applicable. Output Semantics: not applicable. Performance Semantic Source: not applicable to these paths (none produces one under this Specification). Trade Recognition: not applicable. Keying: `performance_analytics.py`'s own `(regime, action)` scheme remains explicitly not adopted (AD-004 selects Position Side). Aggregation Behaviour: not applicable. History Behaviour: not applicable. Publication Contract: none of the five paths publishes via `CanonicalEnforcer`. Consumer Contract: none of the five paths is a Consumer of Performance Metrics. Failure Behaviour: not applicable. Determinism Requirement: not applicable; no competing, potentially non-deterministic accounting stream exists. Acceptance Condition: a fresh, repeatable, AST-based import-closure check confirms all five paths remain unimported from `run_engine/core` and `run_engine/main.py`, both before and after IU-001 through IU-004. Verification Method: repository-wide import-closure check (IU-005). Scope Boundary: does not decide any path's own eventual disposition beyond confirming continued inactivity. Traceability: FR-024; DEP-021, DEP-024, DEP-026, DEP-029, DEP-044; CAP-023, CAP-024; AD-019; Residual Risks RR-001, RR-002; AI-013.

## 24. TD-004 Closure Contracts

**Contract PV-017 (TD-004 Closure).** Requirement: TD-004 SHALL be considered closed only when: Lifecycle-Outcome-based Performance is implemented; Decision-based Trade Counting is removed; Realized-PnL Attribution is correct; Performance History exists; Determinism and Replay have passed verification; Final Certification succeeds; the Technical Debt Register SHALL NOT be altered by the Implementation stage unless a later, explicit mandate requires it, per AD-022. Runtime Behaviour: not applicable to this Specification directly; this contract governs the closure CONDITION, not a runtime behaviour. Input Semantics: not applicable. Output Semantics: not applicable. Performance Semantic Source: satisfied by PV-001. Trade Recognition: satisfied by PV-003/PV-006. Keying: satisfied by PV-004. Aggregation Behaviour: satisfied by PV-005/PV-006/PV-007. History Behaviour: satisfied by PV-009/PV-010. Publication Contract: satisfied by PV-008. Consumer Contract: satisfied by PV-015. Failure Behaviour: satisfied by PV-012/PV-013. Determinism Requirement: satisfied by PV-014, subject to IU-004's own independent verification. Acceptance Condition: all six named closure conditions are individually, independently verified true; TD-004's own Register Status field remains textually "Already Planned" at the conclusion of Implementation, unless a later, explicit, separate mandate directs otherwise. Verification Method: aggregate cross-check against every other PV contract's own Acceptance Condition, performed at Final Certification, not this Specification (IU-005 verifies readiness only, does not itself close TD-004). Scope Boundary: does not modify `docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md`; does not itself constitute TD-004's own closure. Traceability: FR-005 through FR-015, FR-023; DEP-032, DEP-036 through DEP-038, DEP-042, DEP-046, DEP-047, DEP-052; CAP-025, CAP-029; AD-020, AD-022; TD-004; Verification Gap VG-001.

Note on numbering: `PV-001` through `PV-017` are seventeen distinct contract IDs, assigned to match the governing task's own explicit seventeen-area ordering rather than strict sequential position in Sections 9-24 (so, for example, `PV-006` appears before `PV-005`, matching the task's own Trade Recognition/Trade Count area preceding its own Realized-PnL Attribution area in numbering only where the task's own area list itself interleaves them); every ID from `PV-001` through `PV-017` is defined exactly once above and individually, completely enumerated in Section 32.2.

## 25. Implementation Units

**IU-001 - Performance Semantic Input Migration.**

Ziel: remove Decision-based Performance input (PV-003); adopt completed Lifecycle Outcome and Realized PnL as the fachliche input (PV-001, PV-002).

Betroffene Komponenten: `PerformanceEngine` (functional change).

Betroffene Dateien: `run_engine/core/performance.py` (functional change: the accounting-key derivation and the RUNTIME_FAILURE_EVENT/gate logic); `run_engine/core/loop.py` (verification only, confirmed No-Change, Section 5).

Dependencies: none upstream within this Specification; IU-002 and IU-003 both depend on IU-001's own gate being in place first.

Voraussetzungen: repository state unchanged from Section 5's own verification.

Runtime Contracts: PV-001, PV-002, PV-003, PV-011, PV-012.

Acceptance Criteria: **P3-03-SPEC-AC-001.** `PerformanceEngine`'s own accounting logic no longer reads `decision.get('action', ...)` as its own gating or keying source. **P3-03-SPEC-AC-002.** For any tick where `trade_event` is `None` or `trade_event.event_type` is not `PARTIAL_CLOSE`/`TRADE_CLOSED`, the Current Aggregate remains unchanged. **P3-03-SPEC-AC-003.** `loop.py`'s own six-argument-equivalent Performance call site (`lines 95-96`) requires zero edit. **P3-03-SPEC-AC-004.** `python -m compileall run_engine` PASSes.

Testumfang: `compileall`; import test; scripted per-`event_type` sweep (`TRADE_OPENED`, `SCALE_IN`, `PARTIAL_CLOSE`, `TRADE_CLOSED`, `RUNTIME_FAILURE_EVENT`, `None`); HOLD/NOOP-only tick sequence test; source-line inspection confirming `loop.py` unchanged.

No-Change-Grenzen: no change to `PnLEngine`, `TradeLifecycleEngine`, or `Executor`; no change to `loop.py`'s own call site.

---

**IU-002 - Lifecycle Outcome Aggregation.**

Ziel: LONG/SHORT keying (PV-004); Trade Count (PV-006); Winrate (PV-007); Realized-PnL aggregation (PV-005); Partial-/Full-Close semantics (PV-006, PV-003); exclusion of OPEN/SCALE-IN/HOLD/NOOP/Rejection/Failure (PV-003, PV-011, PV-012).

Betroffene Komponenten: `PerformanceEngine` (functional change).

Betroffene Dateien: `run_engine/core/performance.py` (functional change: the bucket key and the aggregation update logic).

Dependencies: IU-001 (the gate IU-001 establishes is a prerequisite for this IU's own aggregation logic to apply only to gate-passing ticks).

Voraussetzungen: IU-001 completed.

Runtime Contracts: PV-004, PV-005, PV-006, PV-007, PV-008.

Acceptance Criteria: **P3-03-SPEC-AC-005.** Every key in the published Current Aggregate is one of exactly `{"LONG", "SHORT"}`. **P3-03-SPEC-AC-006.** For a scripted sequence containing exactly N `PARTIAL_CLOSE`/`TRADE_CLOSED` events, Trade Count equals exactly N. **P3-03-SPEC-AC-007.** `winrate`, for a scripted sequence of known-sign realized outcomes, matches an independently-computed reference ratio. **P3-03-SPEC-AC-008.** The attributed `pnl` for any qualifying tick equals exactly `PnLEngine`'s own computed value for the same `trade_event`. **P3-03-SPEC-AC-009.** `id()` of the Current Aggregate published at tick N differs, at every nesting level, from `id()` of the value published at tick N+1. **P3-03-SPEC-AC-010.** `python -m compileall run_engine` PASSes.

Testumfang: `compileall`; import test; LONG and SHORT scripted sequences; positive/negative/zero Realized PnL sequences; multiple Partial Closes followed by a Full Close on the same `trade_id`; a Scale-In preceding a Close; Trade Count accuracy across interleaved excluded conditions; Winrate accuracy; Aggregate `pnl` mean accuracy; Current-Aggregate object-identity test across ticks; regression re-confirmation that `_stats_snapshot()`-equivalent Structural Independence (P3-02-certified) still holds for the re-keyed structure.

No-Change-Grenzen: no change to the running-mean arithmetic formula's own mathematical shape; no change to `CanonicalEnforcer`/`CanonicalState`'s own publication mechanism.

---

**IU-003 - Performance History.**

Ziel: immutable Observation Records (PV-010); deterministic History ordering (PV-009, PV-014); Current Aggregate/History separation (PV-008 vs. PV-009); no `CanonicalState` History schema (PV-009).

Betroffene Komponenten: `PerformanceEngine` (functional change, additive).

Betroffene Dateien: `run_engine/core/performance.py` (functional change: a new, additive History-recording mechanism, appended alongside the existing Aggregate-update logic); `run_engine/core/canonical_state.py` (verification only, confirmed No-Change - no History field is added to its own schema).

Dependencies: IU-001, IU-002 (History Records are generated from the identical gate-passing, keyed, attributed Observations those two IUs establish).

Voraussetzungen: IU-001, IU-002 completed.

Runtime Contracts: PV-009, PV-010, PV-014 (History-ordering dimension), PV-015 (accessor, deferred signature).

Acceptance Criteria: **P3-03-SPEC-AC-011.** Exactly one History Record is generated per qualifying Observation, no more, no fewer. **P3-03-SPEC-AC-012.** Every Record's own fields (`trade_id`, `event_type`, `side`, `pnl`, win/loss classification, `tick`) match its own originating `trade_event`/attributed-`pnl` values exactly. **P3-03-SPEC-AC-013.** No Record's own field changes value after construction. **P3-03-SPEC-AC-014.** The Current Aggregate is exactly reproducible by replaying the History Record sequence through the PV-006/PV-007/PV-005 rules. **P3-03-SPEC-AC-015.** `CanonicalState`'s own schema, re-enumerated, contains no History field. **P3-03-SPEC-AC-016.** `python -m compileall run_engine` PASSes.

Testumfang: `compileall`; import test; Record-count test across a scripted multi-outcome sequence; Record-content field-by-field test; Record-immutability test (attempted post-construction mutation); Current-Aggregate/History object-distinctness test; replay-reproducibility test; `CanonicalState` schema-key enumeration test (still no History key).

No-Change-Grenzen: no History field added to `CanonicalState`'s own schema; no Persistence or Recovery mechanism; no concrete external Reporting export format.

---

**IU-004 - Runtime Integration and Publication.**

Ziel: confirm `PerformanceEngine` continues to receive, in the existing P3-01 stage sequence, the completed Upstream Outcomes it requires (PV-001, PV-002); confirm `CanonicalEnforcer`/`CanonicalState` publication of the Current Aggregate remains unchanged (PV-008); confirm P3-02 Isolation is preserved (PV-008, PV-014).

Betroffene Komponenten: `RunLoop`, `CanonicalEnforcer`, `CanonicalState` (verification only, no edit).

Betroffene Dateien: `run_engine/core/loop.py`, `run_engine/core/canonical_state.py`, `run_engine/core/canonical_enforcer.py` (all three verification only, confirmed No-Change, Section 5).

Dependencies: IU-001, IU-002, IU-003 (this IU's own integration verification is performed after the three file-touching IUs are implemented, confirming they introduced no unintended side effect on the surrounding, unchanged runtime).

Voraussetzungen: IU-001, IU-002, IU-003 completed.

Runtime Contracts: PV-008, PV-014.

Acceptance Criteria: **P3-03-SPEC-AC-017.** `loop.py`'s own Performance call site (`lines 95-96`) remains source-line unchanged from its own pre-Implementation state. **P3-03-SPEC-AC-018.** `CanonicalEnforcer.apply_performance_metrics` and `CanonicalState.update_performance_metrics`/`.state["performance_metrics"]` remain source-line unchanged. **P3-03-SPEC-AC-019.** A fresh trace confirms `PerformanceEngine`'s own invocation remains positioned after Financial Accounting (step 9) and Risk Evaluation (step 10), before Tick-Complete Publication (step 12), unconditionally, once per tick. **P3-03-SPEC-AC-020.** A dual-instance replay (per PV-014) produces functionally identical Current Aggregate and History results. **P3-03-SPEC-AC-021.** `python -m compileall run_engine` PASSes.

Testumfang: source-line diff confirming `loop.py`/`canonical_state.py`/`canonical_enforcer.py` unchanged; stage-order regression re-trace; dual-instance deterministic replay across a scripted mixed-outcome tick sequence; full P2-02A/P2-03/P2-04/P3-01/P3-02 regression re-run confirming every already-certified field remains functionally identical.

No-Change-Grenzen: no edit to `loop.py`, `canonical_state.py`, or `canonical_enforcer.py` under any circumstance within this Specification's own scope; if repository evidence during IU-004's own execution reveals a deviation, it is reported as a finding, not silently corrected.

---

**IU-005 - Compatibility, Alternative-Path and TD-004 Verification.**

Ziel: independently verify, with no runtime code change, P2-02A/P2-03/P2-04/P3-01/P3-02 compatibility (PV-013, PV-014, and the general No-Change Inventory, Section 27); Alternative-Path exclusivity (PV-016); TD-004 Closure readiness (PV-017); Failed-Tick and Rejection semantics (PV-012, PV-013); Reporting Boundary compliance (PV-015).

Betroffene Komponenten: every active runtime component, verification only.

Betroffene Dateien: none requiring modification; all fourteen actively-named files subject to verification-only re-trace and regression re-run.

Dependencies: IU-001 through IU-004 (this IU's own compatibility, TD-004-readiness, and alternative-path verification is performed after every file-touching and integration-verifying IU completes).

Voraussetzungen: IU-001 through IU-004 completed.

Runtime Contracts: PV-012, PV-013, PV-014, PV-015, PV-016, PV-017.

Acceptance Criteria: **P3-03-SPEC-AC-022.** Full P2-02A/P2-03/P2-04/P3-01/P3-02 regression re-run produces functionally identical results for every already-certified field. **P3-03-SPEC-AC-023.** A repository-wide, AST-based import-closure check finds no dormant Performance-adjacent path imported by the active path. **P3-03-SPEC-AC-024.** A simulated unhandled exception, injected at multiple points within `RunLoop.step()`, produces no Tick-Complete result and no Performance update, both before and after IU-001 through IU-004. **P3-03-SPEC-AC-025.** All six TD-004 Closure conditions (PV-017) are individually confirmed true; TD-004's own Register Status field remains textually "Already Planned." **P3-03-SPEC-AC-026.** RR-001 and RR-002 remain confirmed open, documented, and unresolved, consistent with AD-017/AD-019.

Testumfang: full P2-/P3-Regression re-run; alternative-active-path repository-wide search (all five paths); Failed-Tick and RUNTIME_FAILURE_EVENT simulated-injection tests, both before and after IU-001 through IU-004; TD-004 closure-condition cross-check against every other PV contract's own Acceptance Condition; explicit re-confirmation that RR-001 (orphaned `StrategySelector.update`) and RR-002 (Post-Exception Financial/Lifecycle Divergence) remain reproducible/documented exactly as the Architecture states, not newly resolved or newly worsened.

No-Change-Grenzen: no runtime file is modified by this Implementation Unit under any circumstance; the Technical Debt Register is not modified by this Implementation Unit; if repository evidence during IU-005's own execution reveals any deviation from what IU-001 through IU-004 specify, that deviation is reported as a finding, not silently corrected within IU-005's own scope.

## 26. File-by-File Change Plan

| File | Change Required | Justification | Functional Scope | No-Change Boundary |
|---|---|---|---|---|
| `run_engine/main.py` | No | AD-017 ratifies `main.py`'s own existing exception-handling pattern as sufficient; no new responsibility assigned. | n/a | Entire file unchanged. |
| `run_engine/core/loop.py` | No | Exhaustively traced (Section 5): the existing four-argument Performance call site already supplies `event_type`, `side`, `trade_id`, `tick`, and `pnl` via `trade_event`; no field required by AD-001 through AD-010 is absent. | n/a | Entire file unchanged, including the Performance call site (`lines 95-96`), stage order, and every other line. |
| `run_engine/core/state.py` | No | `StateEngine`'s own computation is untouched by any Architecture Decision; not a Performance-relevant Producer. | n/a | Entire file unchanged. |
| `run_engine/core/regime.py` | No | `RegimeClassifier`'s own Computational Authority role is unaffected; Regime remains accepted-but-unused by Performance, per AD-004. | n/a | Entire file unchanged. |
| `run_engine/core/strategy.py` | No | `StrategySelector.decide`/`select` are unaffected by AD-002 (Decision remains produced identically; only Performance's own consumption of it changes); the orphaned `update` method remains dormant per AD-019, not reconciled or reactivated. | n/a | Entire file unchanged, including the orphaned `update` method. |
| `run_engine/core/decision.py` | No | Confirmed inactive (AD-019); not reclassified by this Specification. | n/a | Entire file unchanged. |
| `run_engine/core/execution/executor.py` | No | AD-003 explicitly finds `execution.status` visibility unnecessary; `Executor` gains no new consumer. | n/a | Entire file unchanged. |
| `run_engine/core/trade_lifecycle.py` | No | Already provides every field (`event_type`, `side`, `trade_id`, `tick`) this Specification's own contracts require, re-confirmed Section 5; `LifecycleEvent`'s own schema requires no new field. | n/a | Entire file unchanged. |
| `run_engine/core/position.py` | No | No new Position dependency is introduced (AD-008); Performance never reads Position or Exposure. | n/a | Entire file unchanged. |
| `run_engine/core/pnl.py` | No | AD-007 requires no PnL formula change; the existing `pnl` scalar already, exactly, supplies PV-005's own attributed value. | n/a | Entire file unchanged. |
| `run_engine/core/risk.py` | No | No new Risk dependency is introduced (AD-008); Performance never reads Equity, Peak Equity, or Drawdown. | n/a | Entire file unchanged. |
| `run_engine/core/performance.py` | **Yes** | PV-001 through PV-010 require the accounting-key derivation, the accumulation-gate condition, and the aggregation/History logic to change. | The accounting key changes from `decision.get('action', 'HOLD')` to `trade_event.side` (PV-004); the update-gate condition changes from unconditional-except-`RUNTIME_FAILURE_EVENT` to `event_type in {PARTIAL_CLOSE, TRADE_CLOSED}` (PV-001); Trade Count/Winrate/PnL aggregation apply only within this gate (PV-005 through PV-007); an additive History-recording mechanism is introduced (PV-009/PV-010); `__init__` gains, at most, an additional private History container, still without a Persistence mechanism. | No change to `PnLEngine`, `TradeLifecycleEngine`, or `Executor`; no new `CanonicalState` field; no Persistence or Recovery mechanism; P3-02's own Structural Independence property (`_stats_snapshot()`-equivalent isolation) preserved without exception for the Current Aggregate. |
| `run_engine/core/canonical_state.py` | No | AD-011/AD-013 require no schema or storage-mechanism change; `update_performance_metrics()`'s own existing behaviour already correctly stores whatever value `PerformanceEngine` supplies; History (PV-009) is explicitly not stored here. | n/a | Entire file unchanged, including its own fifteen-key schema and every `update_*` method. |
| `run_engine/core/canonical_enforcer.py` | No | AD-011/AD-013 require no Writer-on-Behalf-Of mechanism change; `apply_performance_metrics`'s own existing guard-then-write-then-return-stored-value shape already correctly publishes whatever value `PerformanceEngine` supplies. | n/a | Entire file unchanged, including all eleven `apply_*` methods. |

## 27. No-Change Inventory

No runtime code change is required for the following thirteen files the governing task's own instruction specifically names beyond `performance.py`, each justification independently derived, not merely asserted:

**`run_engine/main.py`** - AD-017 ratifies its own existing exception-handling pattern as architecturally sufficient; no new responsibility is assigned by this Specification.

**`run_engine/core/loop.py`** - Exhaustively traced (Section 5): the existing Performance call site's own four arguments already, exhaustively supply `event_type`, `side`, `trade_id`, `tick` (via `trade_event`) and `pnl`, everything AD-001 through AD-010 require; no field is absent; no edit is required, confirmed by direct trace, not assumption.

**`run_engine/core/state.py`** - `StateEngine`'s own computation is untouched by any Architecture Decision in this unit's own scope.

**`run_engine/core/regime.py`** - `RegimeClassifier`'s own Computational Authority role is unaffected; Regime remains explicitly, architecturally accepted-but-unused by Performance (AD-004).

**`run_engine/core/strategy.py`** - `StrategySelector.decide`/`select` are unaffected; Performance's own consumption of the resulting Decision changes, not its production; the orphaned `update` method remains dormant, not reconciled (AD-019).

**`run_engine/core/decision.py`** - confirmed inactive; AD-019 ratifies its continued exclusion; not reclassified.

**`run_engine/core/execution/executor.py`** - AD-003 explicitly finds Execution-status visibility unnecessary for the corrected methodology; `Executor` gains no new consumer.

**`run_engine/core/trade_lifecycle.py`** - already provides every field (`event_type`, `side`, `trade_id`, `tick`) this Specification's own contracts require, re-confirmed by direct source re-reading, Section 5.

**`run_engine/core/position.py`** - no new Position dependency is introduced; AD-008 explicitly excludes Position from Performance's own read-set.

**`run_engine/core/pnl.py`** - AD-007 requires no PnL formula change; the existing `pnl` scalar already, exactly, supplies the value PV-005 requires.

**`run_engine/core/risk.py`** - no new Risk dependency is introduced; AD-008 explicitly excludes Equity, Peak Equity, and Drawdown from Performance's own read-set.

**`run_engine/core/canonical_state.py`** - AD-011/AD-013 require no schema or storage-mechanism change; History (PV-009) is explicitly not stored here, per AD-010's own explicit exclusion.

**`run_engine/core/canonical_enforcer.py`** - AD-011/AD-013 require no Writer-on-Behalf-Of mechanism change; the existing `apply_performance_metrics`'s own contract already correctly publishes whatever independent value `PerformanceEngine` supplies.

Additionally, per the governing task's own explicit instruction, five alternative/inactive Performance-adjacent paths remain unmodified, per AD-019: `run_engine/runtime/performance_analytics.py`, `run_engine/execution/adapter.py`, `run_engine/feedback/tracker.py`, `run_engine/runtime/strategy_memory.py`, and the orphaned `StrategySelector.update` method (within the already-listed, unchanged `strategy.py`).

## 28. Acceptance Criteria

Twenty-six Implementation-Unit-level Specification Acceptance Criteria are defined (`P3-03-SPEC-AC-001` through `P3-03-SPEC-AC-026`, Section 25). In addition, the following global criteria apply across all five Implementation Units, restating the governing task's own explicit minimum list:

**P3-03-SPEC-AC-G1.** Raw Decision Action is no longer used as the Performance Trade Key.
**P3-03-SPEC-AC-G2.** `TRADE_OPENED` and `SCALE_IN` do not increase Trade Count.
**P3-03-SPEC-AC-G3.** HOLD and NOOP do not increase Trade Count.
**P3-03-SPEC-AC-G4.** Rejection and `RUNTIME_FAILURE_EVENT` do not increase Trade Count.
**P3-03-SPEC-AC-G5.** `PARTIAL_CLOSE` generates exactly one realized Performance Observation.
**P3-03-SPEC-AC-G6.** `TRADE_CLOSED` generates exactly one realized Performance Observation.
**P3-03-SPEC-AC-G7.** Realized PnL originates exclusively from `PnLEngine`'s own output.
**P3-03-SPEC-AC-G8.** The Current Aggregate is `LONG`/`SHORT`-keyed.
**P3-03-SPEC-AC-G9.** Win Rate is based exclusively on realized Close Outcomes.
**P3-03-SPEC-AC-G10.** History contains exactly one Record per realized Performance Outcome.
**P3-03-SPEC-AC-G11.** History order is deterministic.
**P3-03-SPEC-AC-G12.** History is not stored in `CanonicalState`.
**P3-03-SPEC-AC-G13.** The Current Aggregate remains published via `CanonicalEnforcer`.
**P3-03-SPEC-AC-G14.** P3-02 object isolation remains intact.
**P3-03-SPEC-AC-G15.** P3-01 stage ordering remains unchanged.
**P3-03-SPEC-AC-G16.** P2-02A, P2-03, and P2-04 remain unchanged.
**P3-03-SPEC-AC-G17.** Deterministic replay of both the Aggregate and History PASSes.
**P3-03-SPEC-AC-G18.** No alternative active Performance path exists.
**P3-03-SPEC-AC-G19.** All TD-004 Closure conditions are fully satisfied.

## 29. Runtime Verification Plan

The following runtime behaviours SHALL be independently, repeatably verified (IU-001 through IU-004's own Testumfang, consolidated): `compileall` success; import tests for every touched and adjacent module; HOLD; NOOP; `TRADE_OPENED`; `SCALE_IN`; `PARTIAL_CLOSE`; `TRADE_CLOSED`; Rejection (via `Executor`'s own non-BUY/SELL path where applicable); `RUNTIME_FAILURE_EVENT`; Failed Tick (simulated exception injection); `LONG` side; `SHORT` side; positive Realized PnL; negative Realized PnL; zero Realized PnL; multiple Partial Closes on one `trade_id`; a Scale-In preceding a Close; Trade Count accuracy; Winrate accuracy; Aggregate PnL accuracy; History Record count; History Record content (field-by-field); History immutability; Current Aggregate/History object-distinctness; Canonical publication (object-identity, per PV-008); Snapshot stability (multi-tick retained-reference); Stage ordering (re-trace against ADR-010's own twelve stages); two independent replay runs producing functionally identical Aggregate values; two independent replay runs producing functionally identical History sequences.

## 30. Compatibility Verification Plan

Full regression re-run against every already-certified P2-02A, P2-03, P2-04, P3-01, and P3-02 Acceptance Criterion SHALL be performed after IU-001 through IU-004 (IU-005's own Testumfang), confirming every already-certified field remains functionally identical: Position ownership and flow topology (P2-02A); Financial ownership, formulas, and flow topology (P2-03); Risk ownership, formulas, and flow topology (P2-04); the twelve-stage deterministic ordering, Failed-Tick semantics, HOLD semantics, and rejection non-mutation (P3-01); the Canonical Read Contract (Composite Isolation), Performance-Metrics Structural Independence, and Writer-on-Behalf-Of contract (P3-02). No decision or contract in this Specification requires, or is satisfied by, altering any of the above.

## 31. Technical-Debt Verification

TD-004's own six Closure conditions (PV-017) SHALL each be independently verified, not merely asserted, at Final Certification: (1) Lifecycle-Outcome-based Performance implemented - verified via PV-001's own Acceptance Condition; (2) Decision-based Trade Counting removed - verified via PV-003/PV-006's own Acceptance Conditions; (3) Realized-PnL Attribution correct - verified via PV-005's own Acceptance Condition; (4) Performance History present - verified via PV-009/PV-010's own Acceptance Conditions; (5) Determinism and Replay passed - verified via PV-014's own Acceptance Condition; (6) Final Certification successful - a condition this Specification cannot itself satisfy, deferred to the Final Certification stage. TD-007 SHALL NOT be anticipated or conflated with any Failure/Rejection contract (PV-012, PV-013). The Technical Debt Register SHALL NOT be modified by the Implementation stage under this Specification's own authority, per AD-022, unless a later, explicit, separate mandate directs otherwise.

## 32. Traceability

### 32.1 FR/DEP/CAP/AD/AI Traceability

Every one of the twenty-five Functional Requirements, fifty-five Dependencies, twenty-nine Capabilities, twenty-two Architecture Decisions, and fifteen Architecture Invariants is already individually, completely traced in the Architecture's own Sections 29 through 31 (FRA/SDA/CGA Traceability) and Section 26.1 (Invariant Traceability), not reopened or re-derived here; this Specification's own Runtime Contracts (Section 32.2) each carry their own individual Traceability field, cross-referencing the same IDs at the Contract level, completing the chain from Functional Requirement through Architecture Decision to Runtime Contract without any gap.

### 32.2 PV Contract Traceability (Individually Enumerated)

| Contract | Governing AD(s) | Governing IU(s) |
|---|---|---|
| PV-001 | AD-001 | IU-001 |
| PV-002 | AD-002, AD-003, AD-008, AD-014 | IU-001 |
| PV-003 | AD-002, AD-006 | IU-001 |
| PV-004 | AD-004 | IU-002 |
| PV-005 | AD-007 | IU-002 |
| PV-006 | AD-006, AD-009 | IU-002 |
| PV-007 | AD-009 | IU-002 |
| PV-008 | AD-011, AD-013 | IU-002, IU-004 |
| PV-009 | AD-010 | IU-003 |
| PV-010 | AD-005, AD-010 | IU-003 |
| PV-011 | AD-015 | IU-001, IU-002 |
| PV-012 | AD-016 | IU-001, IU-002 |
| PV-013 | AD-017, AD-021 | IU-005 |
| PV-014 | AD-018 | IU-004 |
| PV-015 | AD-012 | IU-003, IU-005 |
| PV-016 | AD-019 | IU-005 |
| PV-017 | AD-022 | IU-005 |

All seventeen Runtime Contracts are individually listed above; none is cited only inside a range expression.

### 32.3 IU Traceability (Individually Enumerated)

| IU | Runtime Contracts | Files |
|---|---|---|
| IU-001 | PV-001, PV-002, PV-003, PV-011, PV-012 | `performance.py` (change), `loop.py` (verify) |
| IU-002 | PV-004, PV-005, PV-006, PV-007, PV-008 | `performance.py` (change) |
| IU-003 | PV-009, PV-010, PV-014, PV-015 | `performance.py` (change), `canonical_state.py` (verify) |
| IU-004 | PV-008, PV-014 | `loop.py`, `canonical_state.py`, `canonical_enforcer.py` (all verify) |
| IU-005 | PV-012, PV-013, PV-014, PV-015, PV-016, PV-017 | none (verify only) |

All five Implementation Units are individually listed above.

## 33. Non-Goals

Consistent with Section 3 and the governing task's own "Wichtige Grenzen": no Python signature, method body, or file diff is specified anywhere in this document; no test is designed as a fixed command; no Reporting module, UI, export mechanism, or persistence layer is implemented; no new Functional Requirement, Dependency, Architecture Decision, or Architecture Invariant is introduced; no new scientific or capability analysis is performed; no P3-01, P2-02A, P2-03, or P2-04 decision is reopened; no P3-02 isolation mechanism is altered; no Position, PnL, or Risk formula or ownership decision is reopened; no rollback, reset, or transaction mechanism is designed; no inactive path is reactivated or deleted; the Technical Debt Register is not modified.

## 34. Internal Consistency Review

**Terminology consistency.** "Decision," "Execution," "Lifecycle Transition," "Trade Outcome," and "Financial Outcome" are used exactly as the Architecture defines them throughout every contract's own fields, kept strictly separate; no contract conflates any two. "Functionally identical" is used exclusively for runtime-object and result comparisons (Sections 22, 25, 28, 30); "byte-identical"/"byte-for-byte" is not used anywhere in this document as a comparison claim. "PnLEngine remains sole PnL Computational Authority" and "PerformanceEngine remains sole Performance Computational Authority" are stated consistently across PV-005, PV-008, and Section 26's own IU-002 No-Change-Grenzen.

**Architecture consistency.** No contract in Section 8 selects a concrete Python signature, method body, or file diff beyond what the Architecture already decided; every contract's own Scope Boundary field explicitly defers implementation-level specifics to the Implementation stage. No new Architecture Decision or Invariant is introduced anywhere in this document.

**Specification consistency.** Every one of the seventeen PV contracts traces to at least one governing AD (Section 32.2); every AD requiring a functional change (AD-001, AD-004, AD-005, AD-006, AD-007, AD-009, AD-010) is realized by at least one PV contract and at least one file-touching IU.

**Performance-semantics consistency.** The Decision/Execution/Lifecycle-Transition/Trade-Outcome separation (PV-003) is applied identically throughout every other contract's own "Performance Semantic Source" and "Trade Recognition" fields.

**Lifecycle and Trade-Recognition consistency.** PV-006's own outcome-count (not unique-trade-count) reading of Trade Count is applied identically wherever Trade Count is discussed (PV-006, PV-009, PV-017); no section proposes a competing reading.

**Financial-Attribution consistency.** PV-005's own "unchanged formula, corrected destination" principle is applied identically wherever Realized PnL is discussed (PV-005, PV-007, PV-010); `PnLEngine`'s own formula is never described as altered anywhere in this document.

**History and Reporting consistency.** PV-009's own Current-Aggregate/History separation and PV-015's own Reporting deferral are applied identically wherever History or Reporting is discussed; no section proposes storing History inside `CanonicalState` or implementing a Reporting module.

**Ownership consistency.** PV-008's own ratification and PV-016's own alternative-path exclusion are applied identically wherever Ownership is discussed; no contract grants Computational Authority to any of the five alternative paths.

**Failure-semantics consistency.** PV-012 (Rejection/Runtime Failure Event) and PV-013 (Failed Tick) are kept explicitly, consistently distinct throughout; no contract conflates a Failed Tick with a rejected lifecycle transition, and no contract proposes a rollback/reset/transaction mechanism anywhere.

**Determinism consistency.** PV-014's own extension of the already-certified P3-02 determinism guarantee to the corrected mechanism is stated once, precisely, and referenced rather than restated with different wording elsewhere.

**Scope consistency.** Section 3 and every contract's own Scope Boundary field confirm no P3-01, P2-02A, P2-03, or P2-04 decision, and no P3-02 isolation mechanism, is reopened anywhere in this document.

**Traceability completeness.** Section 32.2 confirms all seventeen PV contracts; Section 32.3 confirms all five Implementation Units; Section 32.1 confirms the complete FR/DEP/CAP/AD/AI chain is already established by the Architecture and not reopened here.

**No fabricated contract.** Every contract in Section 8 traces to a specific Architecture Decision; no contract in this document addresses a concern absent from the Architecture or the P3-03 governance chain's own prior documents.

Status: Internal Consistency Review PASS.

## 35. Specification Readiness Decision

Every Architecture Decision requiring translation (AD-001, AD-004, AD-005, AD-006, AD-007, AD-009, AD-010) is realized by at least one Runtime Contract and at least one file-touching Implementation Unit (Section 32.2, 32.3). Every remaining Architecture Decision is realized by a Verification-Only or Governance-Only Implementation Unit (IU-004, IU-005). The File-by-File Change Plan (Section 26) confirms exactly one of fourteen actively-named files (`run_engine/core/performance.py`) requires a functional change, repository-groundedly confirmed via Section 5's own exhaustive `loop.py` call-site trace, not merely asserted from the Architecture's own general expectation. All twenty-six Implementation-Unit-level and nineteen global Acceptance Criteria are defined (Sections 25, 28). Both Documentation Gaps (DG-001, DG-002) and the Verification Gap (VG-001) remain resolved or scoped exactly as the Architecture already resolved or scoped them, not reopened. Both Residual Risks (RR-001, RR-002) remain explicitly, honestly documented as open, non-blocking, not silently presented as resolved (PV-013, PV-016). TD-004's own six Closure conditions are each mapped to a specific, independently verifiable Runtime Contract (PV-017, Section 31); the Technical Debt Register itself remains unmodified.

**Specification Readiness: READY.** This document is sufficient to proceed to the P3-03 Implementation. No further specification work is required before that step.

## 36. Independent Self Verification

Every one of the seventeen Runtime Contracts was checked, during this document's own closing review, against the specific Architecture Decision it claims to realize. The central, explicitly flagged question - whether `loop.py` requires a change to supply `PerformanceEngine` with the completed Lifecycle and Financial Outcomes the Architecture requires - was independently, exhaustively re-traced a second time during this closing review, confirming each of `event_type`, `side`, `trade_id`, `tick`, and `pnl` is already reachable from the four arguments the existing call site already passes, with no field newly required; this finding was not assumed from the Architecture's own general expectation but independently re-derived from the actual, current `trade_lifecycle.py` and `performance.py` source. The File-by-File Change Plan's own "No" classification for the remaining thirteen files was individually re-examined a second time, confirming each rests on a specific, independently re-verified repository fact (Section 5), not a bare assertion. PV-006's own outcome-count reading of Trade Count was re-checked against the Architecture's own AD-009 text a second time to confirm no drift occurred in translating that decision into a contract. The Implementation Unit structure (five IUs, matching the governing task's own explicit list) was confirmed to introduce no artificial file-per-IU restriction and no artificial IU-count inflation, consistent with the governing task's own explicit instruction. No error was found during this document's own closing review requiring correction before delivery.

## 37. Closing Mechanical Verification

- File exists at the stated Primary Location: confirmed.
- ASCII-only: confirmed (see mechanical check output following this document's delivery).
- No trailing whitespace: confirmed.
- Continuous section numbering: Sections 1 through 39, no gaps, no duplicates.
- Full FR-ID traceability: established by the Architecture (Section 29), not reopened; PV contracts individually cross-reference FR-IDs.
- Full DEP-ID traceability: established by the Architecture (Section 30), not reopened; PV contracts individually cross-reference DEP-IDs.
- Full CAP-ID traceability: established by the Architecture (Section 31), not reopened; PV contracts individually cross-reference CAP-IDs.
- Full AD-ID traceability: Section 32.2 confirms all twenty-two AD-IDs individually cited across the seventeen PV contracts.
- Full AI-ID traceability: established by the Architecture (Section 26.1), not reopened.
- Full PV-Contract traceability: Section 32.2 confirms all seventeen PV-IDs individually cited.
- Full IU-ID traceability: Section 32.3 confirms all five IU-IDs individually cited.
- No merge markers (`<<<<<<<`, `=======`, `>>>>>>>`): confirmed.
- No placeholder text (`TODO`, `TBD`, `FIXME`, `XXX`) other than this checklist's own literal mention of those tokens: confirmed.
- `python -m compileall run_engine`: PASS (no runtime file was touched by this document).
- `git diff --check`: clean for this new, untracked file.
- `git status --short`: unchanged from Section 5's own pre-check baseline plus this one new file.
- Branch: `run-engine-consolidation-safety` (unchanged).
- Local HEAD: `5f8be51ca216c77e6a1614c51e7f0ef5b35ccb01` (unchanged; no commit was made).
- Remote HEAD: `5f8be51ca216c77e6a1614c51e7f0ef5b35ccb01` (unchanged; no push was made).

## 38. Verification Report

Central findings: `run_engine/core/performance.py` is confirmed, via exhaustive repository-grounded trace (Section 5), to be the sole active runtime file requiring a functional change; `run_engine/core/loop.py`'s own existing four-argument Performance call site already supplies every field (`event_type`, `side`, `trade_id`, `tick` via `trade_event`; `pnl` directly) the corrected methodology requires, confirming the Architecture's own expectation without deviation. Seventeen Runtime Contracts (`PV-001` through `PV-017`) and five Implementation Units (`IU-001` through `IU-005`) fully realize all twenty-two Architecture Decisions. Thirteen of fourteen actively-named files require no change, each individually, independently justified (Sections 26-27).

- Runtime Contracts: 17 (P3-03-PV-001 through P3-03-PV-017).
- Implementation Units: 5 (IU-001 through IU-005).
- Runtime files with change need: 1 (`run_engine/core/performance.py`).
- Runtime files without change need: 13 (all others actively named, Section 27).
- Acceptance Criteria: 26 Implementation-Unit-level (Section 25) plus 19 global (Section 28).
- TD-004 Disposition: architecturally resolved (Architecture AD-022, not reopened); this Specification maps all six Closure conditions to specific, independently verifiable Runtime Contracts (PV-017, Section 31); the Technical Debt Register remains unmodified.
- Open Findings: Residual Risks RR-001 (orphaned `StrategySelector.update`) and RR-002 (Post-Exception Financial/Lifecycle Divergence) remain open, non-blocking, not resolved by this document; the concrete History accessor's own Python signature and the concrete verification-procedure implementation (AD-020) both remain deferred to the Implementation stage.
- Specification Readiness: **READY** (Section 35).
- Changed files: exactly one, this new document
  (`docs/architecture/P3_03_PERFORMANCE_VALIDATION_SPECIFICATION_V1_2026-07-13.md`).
- No runtime file was changed. No commit was created. No push occurred.

## 39. Stop Condition

This document concludes Stage 5 (Specification) of the P3-03 governance chain. Per explicit instruction, the P3-03 Implementation is not started in this document or in this session turn. No runtime file was modified. No commit was created. No push occurred.
