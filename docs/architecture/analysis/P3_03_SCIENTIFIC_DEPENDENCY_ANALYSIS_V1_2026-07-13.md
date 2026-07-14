Document Class:
Scientific Dependency Analysis

Document ID:
P3-03-SDA

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
docs/architecture/analysis/P3_03_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-13.md

Depends On:
- docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md
- docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md
- docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md
- docs/architecture/analysis/P3_03_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-13.md
- complete P3-01 governance chain (FRA, SDA, CGA, Architecture, Specification, Final Certification)
- complete P3-02 governance chain (FRA, SDA, CGA, Architecture, Specification, Final Certification)
- docs/architecture/P2_02A_POSITION_OWNERSHIP_ARCHITECTURE_V1_2026-07-10.md
- docs/architecture/P2_02A_POSITION_OWNERSHIP_SPECIFICATION_V1_2026-07-10.md
- docs/architecture/P2_03_FINANCIAL_OWNERSHIP_ARCHITECTURE_V1_2026-07-11.md
- docs/architecture/P2_03_FINANCIAL_OWNERSHIP_SPECIFICATION_V1_2026-07-11.md
- docs/architecture/P2_04_RISK_OWNERSHIP_ARCHITECTURE_V1_2026-07-13.md
- docs/architecture/P2_04_RISK_OWNERSHIP_SPECIFICATION_V1_2026-07-13.md
- current runtime code at HEAD 5f8be51ca216c77e6a1614c51e7f0ef5b35ccb01

Referenced By:
- future P3-03 Capability Gap Analysis
- future P3-03 Architecture

Methodological Structure Reference (content not carried over):
- docs/architecture/analysis/P3_02_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-13.md

---

# P3-03 Performance Validation - Scientific Dependency Analysis

## 1. Purpose

This document is the Scientific Dependency Analysis (SDA) for P3-03, "Performance Validation," the second stage of the P3-03 governance chain (FRA -> SDA -> CGA -> Architecture -> Specification -> Implementation -> Final Certification). It identifies the scientific dependencies among the twenty-five Functional Requirements established by
`docs/architecture/analysis/P3_03_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-13.md` (the "P3-03 FRA"), classifies each dependency, builds Requirement Clusters, a Dependency Catalogue, a Dependency Graph, Dependency Layers, and a Dependency Matrix, performs Cycle and Coupling Analysis, and records Scientific Dependency Findings, Risks, Constraints, and Open Questions. It introduces no new Functional Requirement, performs no Capability classification, and makes no Architecture Decision.

## 2. Scope

In scope: dependency relationships among the twenty-five P3-03 FRs; dependency relationships between P3-03 FRs and already-certified P2-02A/P2-03/P2-04/P3-01/P3-02 contracts (Compatibility and Cross-Unit Dependencies); dependency relationships contingent on a not-yet-decided P3-03 FRA Open Question (Conditional Dependencies); cycle and coupling detection across the complete dependency graph.

Out of scope: Performance-keying selection; Performance formula definition; History-schema selection; Reporting-module design; Architecture Decisions; Capability status assignment; Implementation Units; any runtime file change; reopening any already-certified Ownership, Ordering, or Information-Flow decision.

## 3. Workflow Boundary

This document is Stage 2 of 7 of the P3-03 governance chain. Not yet created: Capability Gap Analysis, Architecture, Specification, Implementation, Final Certification. No runtime file is modified. No new Functional Requirement is created. No Architecture Decision or Invariant is created.

## 4. Independent Pre-Checks

Performed independently, immediately before starting this analysis:

- Branch: `run-engine-consolidation-safety` (confirmed via `git branch --show-current`).
- Local HEAD: `5f8be51ca216c77e6a1614c51e7f0ef5b35ccb01` (confirmed via `git rev-parse HEAD`), matching the expected HEAD exactly, unchanged since the P3-03 FRA's own drafting.
- Remote HEAD: `5f8be51ca216c77e6a1614c51e7f0ef5b35ccb01` (confirmed via `git fetch` followed by `git rev-parse origin/run-engine-consolidation-safety`), identical to local HEAD, no divergence.
- Working tree: the same pre-existing, unrelated tracked modification
  (`docs/capabilities/SGF_013_SCIENTIFIC_BEHAVIOUR_REPRESENTATION_2026-06-26.md`) and the same set of pre-existing untracked directories as before, plus the P3-03 FRA itself (still untracked, not committed). None touched by this document's own drafting. `run_engine/` remains clean.

All four pre-check conditions are satisfied; analysis may proceed.

## 5. Binding Basis (Freshly Re-Read, Not Relying on Prior Sessions)

The P3-03 FRA was re-read in full for this document (Section 6 below), not summarized from memory. The following Architecture Baseline sections were re-read in full and fresh for this document, independent of the FRA's own prior citations, since the FRA cited only ADR-008 and the Ownership Matrix's "Performance Metrics" row:

- ADR-001 through ADR-012 (complete text), including Acceptance Criteria for each.
- The Runtime Ownership Matrix (complete table) and Ownership Rules OM-001 through OM-009.
- The Target Information Flow, including Principles IF-001 through IF-006, the Runtime Stage Responsibilities table, Information Preservation Rules IF-001 through IF-006 (rule numbering reused from the Principle numbering in the source document), and the Tick Completion Contract.
- Architecture Invariants AI-001 through AI-015 (complete text).
- Scientific Acceptance Criteria AC-001 through AC-015 (complete text).

Also freshly re-read: `docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md` (TD-004, TD-007), `docs/architecture/P3_01_DETERMINISTIC_EXECUTION_ORDERING_ARCHITECTURE_V1_2026-07-13.md` (specifically its own Performance-related passages: AD-010's Cross-Unit ratification of TD-004/PerformanceEngine to P3-03, AI-012 Rejection Non-Mutation naming Performance statistics explicitly, DEP-009's own ratification that Performance Evaluation precedes Tick-Complete Publication), and the complete P3-02 governance chain (re-confirming AD-001 Composite Isolation, AD-005 Performance Structural Independence, IU-002).

`run_engine/core/risk.py`, `run_engine/core/position.py`, and `run_engine/core/pnl.py` were re-read fresh and confirmed to carry direct, explicit inline citations to P2-02A and P2-04 Architecture Decisions (e.g. `risk.py`'s own docstring citing P2-04-AD-002, AD-004, AD-005, AD-007, AD-008, AD-009, AD-010, AD-011, AD-012, AD-013, AD-015), used directly as Compatibility Dependency evidence in Section 24 rather than re-deriving P2-02A/P2-03/P2-04's own certified content from first principles.

No runtime file was modified by this document's own drafting.

## 6. Repository Re-Verification

The following runtime files were re-read fully and fresh for this document, independent of the FRA's own prior citations: `run_engine/core/performance.py`, `run_engine/core/loop.py`, `run_engine/core/execution/executor.py`, `run_engine/core/trade_lifecycle.py`, `run_engine/core/position.py`, `run_engine/core/pnl.py`, `run_engine/core/risk.py`, `run_engine/core/canonical_state.py`, `run_engine/core/canonical_enforcer.py`, `run_engine/core/strategy.py`. Every file matches its content as described in the P3-03 FRA exactly; no drift was found.

A repository-wide search (scoped to `run_engine/`, all `.py` files, `__pycache__` excluded) was performed for: `PerformanceEngine`, `performance_metrics`, `performance`, `stats`, `pnl`, `trades`, `winrate`, `decision`, `execution`, `lifecycle`, `outcome`, `history`, `reporting`, `regime`, `RuntimeFailureEvent`, `HOLD`, `NOOP`, `BUY_EXECUTED`, `SELL_EXECUTED`, `update_performance`, `update(`, `consumer`, `producer`, `canonical`. Findings beyond what the FRA already recorded:

- `NOOP`, `BUY_EXECUTED`, `SELL_EXECUTED` additionally occur in `run_engine/execution/adapter.py` (`ExecutionAdapter.execute`) and, for `BUY_EXECUTED`/`SELL_EXECUTED` only, in `run_engine/feedback/tracker.py` (`FeedbackTracker.record`, which reads `decision.get("action")` and `execution.get("status")` to maintain a `loss_streak` counter) and `run_engine/runtime/strategy_memory.py`. A dedicated import check confirmed zero references to `run_engine.execution.adapter`, `run_engine.feedback.tracker`, or `run_engine.runtime.strategy_memory` anywhere under `run_engine/core` or in `run_engine/main.py`. All three are additional inactive/legacy files, extending the already-established inactive status of `run_engine/runtime/` to the separate `run_engine/execution/` and `run_engine/feedback/` directories as well.
- `run_engine/logging/logger.py` (`Logger.log`, a single `print(f"[{event_type}] {data}")` statement) is likewise unreferenced anywhere under `run_engine/core` or `run_engine/main.py`, confirming no active or inactive component anywhere in the repository provides genuine Performance or Trade history persistence beyond in-memory objects; this closes the "Historisierung" keyword search with a definitive negative result across the entire repository, not merely the active path.
- `outcome`, `consumer`, `producer` (as literal source identifiers) produced zero matches anywhere in `run_engine/`; these concepts exist in the repository only as prose in the Architecture Baseline's own Ownership Matrix and Target Information Flow sections (Section 5), never as runtime code artifacts.
- `Computational Authority` and `Authoritative Owner` (as literal doc-comment phrases) occur only in `run_engine/core/risk.py` and `run_engine/core/trade_lifecycle.py`, both already cited in Section 5.

No previously unknown active Performance path was found. The alternative/inactive path picture established by the FRA (`run_engine/runtime/performance_analytics.py`) is confirmed unchanged and is now understood to sit within a larger, entirely inactive `run_engine/runtime/`, `run_engine/execution/`, `run_engine/feedback/`, and `run_engine/logging/` set of directories, none imported by any active file.

## 7. Dependency Context

This SDA operates on the twenty-five Functional Requirements of the P3-03 FRA (Section 5.2 of this document lists the full re-read; the FRA's own Section 18 is the sole source). The FRA's own five Functional Gaps (FG-001 through FG-005) describe concrete, currently-reproducible divergences from ADR-008's Acceptance Criteria. This SDA does not re-adjudicate those Gaps; it instead identifies which Functional Requirements those Gaps causally depend on, and which already-certified Baseline contracts (ADRs, Invariants, Acceptance Criteria, Ownership Rules, Information Flow Rules) each Functional Requirement must remain compatible with or is currently in tension with. Every dependency is a *relationship*, never a *resolution*.

## 8. Scientific Dependency Method

A dependency `P3-03-FR-X -> P3-03-FR-Y` is recorded when FR-Y's own text (Requirement Statement, as written in the FRA) presupposes, is evidenced by, or is a specific instance of FR-X's own subject matter, established either by direct textual cross-reference within the FRA or by independently re-traced repository evidence (Section 6). Four dependency classes are used, matching the governing task's own required output categories:

- **REQUIRED** - a structural or evidentiary dependency entirely internal to this unit's own twenty-five Functional Requirements.
- **CONDITIONAL** - a dependency whose strength or eventual disposition depends on a currently-undecided P3-03 FRA Open Question (OQ-001 through OQ-004).
- **CROSS-UNIT** - a dependency reaching into another unit's own scope (P3-01, P3-02, a future Runtime Control Unit, or a not-yet-built Reporting module) without that unit's own decision being reopened.
- **COMPATIBILITY** - a dependency requiring an FR's own current state to remain (or be recognized as currently not remaining) consistent with an already-certified contract (an ADR, Invariant, Acceptance Criterion, Ownership Rule, or Information Flow Rule of the Architecture Baseline, or a certified P2-02A/P2-03/P2-04/P3-01/P3-02 contract) that this document does not reopen.

Every dependency below is derived exclusively from the FRA's own text (re-read in full, Section 6) and, where the FRA's own text itself cites direct repository evidence, from that same repository evidence, independently re-confirmed in Section 6. No dependency is asserted from topical proximity alone.

## 9. Requirement Clusters

Nine thematic clusters group the twenty-five Functional Requirements for readability; cluster membership does not itself imply a dependency (dependencies are stated individually in Section 11).

| Cluster | Title | Members |
|---|---|---|
| A | Ownership and Computational Authority | FR-001, FR-002, FR-003 |
| B | Tick-Boundary and Invocation Contract | FR-004, FR-025 |
| C | Decision-Keyed Accounting Mechanics | FR-005, FR-010, FR-011, FR-013, FR-014 |
| D | Input Read-Set and Cross-Unit Boundary | FR-006, FR-007, FR-008, FR-012, FR-023 |
| E | Failure-Path Behaviour | FR-009 |
| F | Lifetime and Historization | FR-015 |
| G | Structural Independence and Publication | FR-016, FR-017, FR-018 |
| H | Consumption | FR-019, FR-020 |
| I | Determinism, Replay, and Alternative Paths | FR-021, FR-022, FR-024 |

## 10. Dependency Layers

Layers are ordered so that a Functional Requirement in a higher-numbered layer may depend on one in a lower-numbered layer, never the reverse (verified acyclic, Section 25).

**Layer 0 - Certified Compatibility Baseline (not a P3-03 FR; the fixed ground every Compatibility Dependency measures against).** ADR-001 through ADR-012, the Runtime Ownership Matrix, the Target Information Flow, AI-001 through AI-015, AC-001 through AC-015; P2-02A, P2-03, P2-04; the complete P3-01 and P3-02 governance chains.

**Layer 1 - Foundational Contracts.** FR-001 (sole Computational Authority), FR-004 (unconditional per-tick invocation), FR-025 (initial state).

**Layer 2 - Ownership and Invocation Consequences.** FR-002, FR-003, FR-005.

**Layer 3 - Input Read-Set.** FR-006, FR-007, FR-008, FR-012.

**Layer 4 - Accounting Mechanics.** FR-009, FR-010, FR-011, FR-013, FR-014.

**Layer 5 - Lifetime and Aggregate Read-Set.** FR-015, FR-023.

**Layer 6 - Structural Independence and Publication.** FR-016, FR-017, FR-018.

**Layer 7 - Consumption.** FR-019, FR-020.

**Layer 8 - Aggregate Assurance and Alternative Paths.** FR-021, FR-022, FR-024.

## 11. Runtime Object Flow Re-Verification

Independently re-traced against the current runtime (Section 6), confirming the FRA's own Section 10/11 trace remains accurate and forms the factual substrate for every REQUIRED dependency in Section 11.1: `StrategySelector.decide` -> `decision` (dict, `'action'` key); `PnLEngine.update` -> `pnl` (scalar); `RegimeClassifier.classify` -> `regime` (string); `TradeLifecycleEngine.on_execution` -> `trade_event` (`LifecycleEvent`, frozen dataclass). All four converge as direct-value arguments into `PerformanceEngine.update(decision, pnl, regime, trade_event)` (`loop.py:95`) -> `_stats_snapshot()` -> `CanonicalEnforcer.apply_performance_metrics` -> `CanonicalState.state["performance_metrics"]` and the tick-result dict's own `"performance"` key -> consumed only by `main.py`'s own `print(result)`.

### 11.1 Full Dependency Catalogue

Fifty-five dependency records, `P3-03-DEP-001` through `P3-03-DEP-055`, each individually enumerated and classified per Section 8.

**REQUIRED (internal to the twenty-five P3-03 FRs)**

**P3-03-DEP-001.** FR-001 -> FR-002. REQUIRED. FR-002's own Authoritative-Owner claim for `CanonicalState` is meaningful only given FR-001's own prior finding that exactly one `PerformanceEngine` instance is the Computational Authority computing the value `CanonicalState` owns.

**P3-03-DEP-002.** FR-001 -> FR-003. REQUIRED. FR-003's own claim that `CanonicalEnforcer.apply_performance_metrics` is the sole Writer-on-Behalf-Of presupposes FR-001's own finding that `PerformanceEngine` itself never writes `CanonicalState` directly.

**P3-03-DEP-003.** FR-004 -> FR-005. REQUIRED. FR-005's own accounting-key mechanics apply only because FR-004 establishes the call occurs unconditionally, every tick.

**P3-03-DEP-004.** FR-005 -> FR-010. REQUIRED. FR-010's own `trades` increment is keyed by exactly the `action` value FR-005 defines.

**P3-03-DEP-005.** FR-005 -> FR-011. REQUIRED. FR-011's own HOLD-bucket treatment is a named special case of the general keying rule FR-005 establishes.

**P3-03-DEP-006.** FR-006 -> FR-013. REQUIRED. FR-013's own `wins` computation (`1 if pnl > 0 else 0`) directly consumes the `pnl` value whose semantics FR-006 defines.

**P3-03-DEP-007.** FR-006 -> FR-014. REQUIRED. FR-014's own running-mean `pnl` formula directly consumes the same `pnl` input FR-006 defines.

**P3-03-DEP-008.** FR-007 -> FR-009. REQUIRED. FR-009's own failure short-circuit is triggered exactly by the `event_type` equality test FR-007 defines.

**P3-03-DEP-009.** FR-010 -> FR-013. REQUIRED. FR-013's own `wins` counter is evaluated against the same `trades` denominator FR-010 increments.

**P3-03-DEP-010.** FR-010 -> FR-014. REQUIRED. FR-014's own running-mean recomputation uses the same `trades` counter FR-010 increments as its own divisor.

**P3-03-DEP-011.** FR-012 -> FR-010. REQUIRED. FR-010's own unconditional increment (not gated on Executor status) is possible precisely because FR-012 establishes that `execution`/`status` is never read at all.

**P3-03-DEP-012.** FR-014 -> FR-015. REQUIRED. FR-015's own lifetime/no-reset finding is what allows FR-014's own running-mean formula to remain the applicable description across the full process lifetime rather than only within a bounded window.

**P3-03-DEP-013.** FR-002 -> FR-017. REQUIRED. FR-017's own publish-unchanged mechanism is the concrete realization of FR-002's own Authoritative-Owner property for `performance_metrics`.

**P3-03-DEP-014.** FR-003 -> FR-017. REQUIRED. FR-017 is literally `CanonicalEnforcer.apply_performance_metrics`, the method FR-003 names as the sole writer.

**P3-03-DEP-015.** FR-001, FR-017 -> FR-018. REQUIRED. FR-018's own dual-channel publication exposes exactly the object FR-001's `PerformanceEngine` produces and FR-017's `CanonicalEnforcer` publishes.

**P3-03-DEP-016.** FR-018 -> FR-019. REQUIRED. FR-019's own zero-internal-consumer finding is evaluated against exactly the two channels FR-018 establishes.

**P3-03-DEP-017.** FR-018 -> FR-020. REQUIRED. FR-020's own external-consumer finding (`main.py`'s own `print`) reads exactly the tick-result `"performance"` key FR-018 defines.

**P3-03-DEP-018.** FR-016 -> FR-018. REQUIRED. FR-018's own dual-channel publication carries the Structurally Independent snapshot FR-016 already establishes; without FR-016 holding, the two channels could alias one another.

**P3-03-DEP-019.** FR-021 -> FR-022. REQUIRED. FR-022's own order-dependence finding for intermediate snapshots is a refinement of, not a contradiction of, the general determinism property FR-021 establishes.

**P3-03-DEP-020.** FR-005, FR-006, FR-007, FR-008 -> FR-023. REQUIRED (evidentiary aggregation). FR-023's own cross-unit read-set summary is the aggregate restatement of exactly which fields FR-005 (`decision['action']`), FR-006 (`pnl`), FR-007 (`trade_event.event_type`), and FR-008 (`regime`, unused) individually establish are read or not read.

**P3-03-DEP-021.** FR-001 -> FR-024. REQUIRED. FR-001's own claim that `PerformanceEngine` is the *sole* Computational Authority is directly evidenced by FR-024's own confirmation that the only structurally distinct alternative Performance implementation in the repository (`performance_analytics.py`) is unreferenced and inactive.

**P3-03-DEP-022.** FR-025 -> FR-017. REQUIRED. FR-025's own finding (initial `None`, never invoked with `None` at the active call site) directly qualifies FR-017's own `None`-guard branch, confirming it is currently unreachable dead code in the active runtime.

**P3-03-DEP-023.** FR-013 -> FR-011. REQUIRED. FR-013's own `wins` computation, applied specifically within the HOLD bucket FR-011 defines, means every HOLD-decided tick with `pnl == 0.0` (the ordinary case, since HOLD never generates a closing `trade_event`) counts as a non-win inside the HOLD bucket exactly as FR-011 predicts.

**CONDITIONAL (tied to P3-03 FRA Open Questions OQ-001 through OQ-004)**

**P3-03-DEP-024.** FR-005 -> FR-024. CONDITIONAL. Whether FR-024's own inactive-path finding remains a mere Residual-Risk footnote or becomes relevant prior art for the Architecture stage's own eventual resolution of OQ-001 (replacing `decision`-keying with `LifecycleEvent`-keying) depends on whether the Architecture stage consults `performance_analytics.py`'s own `(regime, action)` keying; contingent, referenced OQ-001 and OQ-004 jointly.

**P3-03-DEP-025.** FR-019 -> FR-020. CONDITIONAL. Both findings remain stable only until OQ-003 is resolved (whether "Reporting" is stale documentation or names a future module); if a Reporting module is eventually built, FR-019's own zero-internal-consumer status and FR-020's own sole-external-consumer status would both require re-evaluation together, though today neither depends on the other's current truth value. Contingent, referenced OQ-003.

**P3-03-DEP-026.** FR-024 -> FR-019. CONDITIONAL. Whether the inactive `performance_analytics.py` is treated as genuinely out-of-scope legacy code or as a live alternative-Computational-Authority candidate depends on OQ-004; if brought into scope, FR-019's own "zero active consumer" finding would additionally need to account for whether a reconciled Performance model could make it, or a caller of it, an active consumer. Contingent, referenced OQ-004.

**P3-03-DEP-027.** FR-005 -> FR-012. CONDITIONAL. Whether the orphaned `StrategySelector.update(decision, pnl, regime)` method (P3-03-RR-001) is treated as in-scope cleanup for P3-03 depends on OQ-002; if in scope, FR-005's own decision-keying finding and FR-012's own execution-blindness finding both become directly relevant, since that orphaned method shares exactly the same subject matter (`decision`, `pnl`, `regime` as inputs, no execution outcome). Contingent, referenced OQ-002.

**P3-03-DEP-028.** FR-009 -> FR-007. CONDITIONAL. If Architecture resolves OQ-001 toward consuming a richer `LifecycleEvent` read-set rather than only `event_type`, FR-007's own single-field-read finding and FR-009's own failure-short-circuit finding would both require re-evaluation together, since additional branch conditions could be introduced beyond the current single `RUNTIME_FAILURE_EVENT` check. Contingent, referenced OQ-001.

**P3-03-DEP-029.** FR-015 -> FR-024. CONDITIONAL. FR-015's own "no historization mechanism" finding remains descriptive of the runtime only until either TD-004 is resolved (potentially introducing lifecycle-history-based reproducibility per ADR-008) or OQ-004 brings `performance_analytics.py`'s own also-non-historized accounting into scope; neither changes FR-015's own present truth, but both bound how long it remains an accurate description. Contingent, referenced OQ-004 and TD-004 jointly.

**COMPATIBILITY (must remain consistent with already-certified Baseline contracts, not reopened)**

**P3-03-DEP-030.** FR-002 - Compatibility with AI-002 (Unique Ownership) and Rule OM-001 (exactly one Authoritative Owner). Conformant: `CanonicalState` is the sole Authoritative Owner of `performance_metrics`.

**P3-03-DEP-031.** FR-001 - Compatibility with AI-003 (Separation of Ownership and Computation) and Rule OM-002 (Computational Authority may differ from Authoritative Owner). Conformant.

**P3-03-DEP-032.** FR-001, FR-005, FR-010, FR-013, FR-014 - Compatibility with Rule OM-008 ("PerformanceEngine owns no operational runtime information. PerformanceEngine evaluates completed lifecycle outcomes only."). FR-001's own ownership finding is conformant; FR-005, FR-010, FR-013, and FR-014's own decision-keyed accounting mechanics are **not conformant** with OM-008's own second sentence, since the active accounting evaluates decided actions, not completed lifecycle outcomes. This is the same substance as FRA FG-001, FG-002, and FG-004, now additionally grounded in Rule OM-008, a citation the FRA itself did not use.

**P3-03-DEP-033.** FR-003 - Compatibility with Rule OM-003 (Writer-on-Behalf-Of never establishes ownership). Conformant.

**P3-03-DEP-034.** FR-019, FR-020 - Compatibility with Rule OM-004 (Primary Consumers shall never modify consumed information). Vacuously conformant: zero active consumers exist to violate this rule.

**P3-03-DEP-035.** FR-004 - Compatibility with ADR-010 (Deterministic Runtime Execution Ordering, step 11 "Performance Evaluation") and the Target Information Flow's own Tick Completion Contract ("Completion requires: ... Performance evaluated ..."). Conformant: the call site executes unconditionally, once per tick, as its own assigned stage requires.

**P3-03-DEP-036.** FR-005, FR-006, FR-007, FR-010, FR-012, FR-013, FR-014 - Compatibility with ADR-008 (Performance Ownership). Not conformant for the decision-keyed and execution-blind aspects; same substance as FRA FG-001, FG-002, FG-004, FG-005.

**P3-03-DEP-037.** FR-005, FR-010, FR-013 - Compatibility with AC-008 (Performance Evaluation, Baseline-level: "PerformanceEngine evaluates completed lifecycle outcomes exclusively. Runtime decisions never directly contribute to performance statistics."). Not conformant. This is a Baseline-level Acceptance Criterion distinct from, though textually close to, ADR-008's own Acceptance Criteria; the FRA cited only the latter.

**P3-03-DEP-038.** FR-015 - Compatibility with AC-008's third clause ("Performance remains reproducible from lifecycle history"). Not conformant; same substance as FRA FG-003, now doubly grounded (ADR-008's Acceptance Criteria and the Baseline's own AC-008).

**P3-03-DEP-039.** FR-007, FR-009 - Compatibility with ADR-011 (Runtime Failure Handling) and P3-01-AI-012 (Rejection Non-Mutation, which explicitly names "Performance statistics" among the values a rejected transition shall never mutate). Conformant: the `RUNTIME_FAILURE_EVENT` short-circuit performs no accumulator mutation.

**P3-03-DEP-040.** FR-008 - Compatibility with AI-007 (Semantic Continuity) and Principle IF-003 ("Every transformation preserves semantic meaning"). Conformant (benign): an unused parameter does not misinterpret or alter `regime`'s own meaning; it simply is not consumed.

**P3-03-DEP-041.** FR-016, FR-017 - Compatibility with P3-02-AD-005 and IU-002 (Performance Metrics Structural Isolation). Conformant, already certified, not reopened.

**P3-03-DEP-042.** FR-023 - Compatibility with the Target Information Flow's own Runtime Stage Responsibilities table ("PerformanceEngine | Lifecycle History + Financial State | Performance Metrics") and Rule IF-005 ("PerformanceEngine derives performance exclusively from completed lifecycle outcomes"). Not conformant: FR-023's own actual read-set (`trade_event.event_type`, `decision['action']`, `pnl`) diverges materially from the Target's own named Primary Input ("Lifecycle History + Financial State").

**P3-03-DEP-043.** FR-021 - Compatibility with AI-005 (Deterministic Execution) and AC-012 (Deterministic Behaviour). Conformant.

**P3-03-DEP-044.** FR-024 - Compatibility with AI-013 (Architectural Minimality: "Architectural redundancy is prohibited unless scientifically justified."). In tension, not an active violation: `performance_analytics.py` is a structurally redundant, unreferenced alternative Performance implementation; AI-013 governs justification for active runtime components, and this one is dormant, so no active-runtime violation currently exists, but its continued unreconciled presence is a latent tension with AI-013 if ever activated without justification.

**P3-03-DEP-045.** FR-006, FR-012 - Compatibility with the certified P2-02A (Position Ownership) and P2-03 (Financial Ownership) contracts. Conformant: `PerformanceEngine` never touches Position or PnL ownership itself; it only consumes `PnLEngine`'s own already-published scalar `pnl`.

**P3-03-DEP-046.** FR-007, FR-010 - Compatibility with AC-014 (Lifecycle Semantics: Scale-In, Partial Close, and Full Close shall remain semantically distinct). Not conformant; same substance as FRA FG-005, since `PerformanceEngine.update` branches on no `event_type` value beyond the single `RUNTIME_FAILURE_EVENT` check.

**P3-03-DEP-047.** FR-005, FR-006, FR-007 - Compatibility with ADR-002 (Event-Driven Runtime Evolution: the normative Runtime Event hierarchy places Performance Events as the layer immediately downstream of Risk Events, each layer consuming "the event output of the immediately preceding layer as its primary transition input"). Not conformant: the active call site passes `decision` (a Decision Event artifact, several layers upstream) directly into `PerformanceEngine.update`, bypassing Execution, Trade Lifecycle, Financial, and Risk Events entirely as primary transition input.

**CROSS-UNIT (reaching into another unit's own scope, not reopened)**

**P3-03-DEP-048.** FR-004 - Cross-Unit with P3-01-AD-001 (12-stage deterministic ordering) and P3-01's own DEP-009 ("Performance Evaluation precedes Tick-Complete Publication"). Re-verification, not reopened.

**P3-03-DEP-049.** FR-009 - Cross-Unit with P3-01-AD-006 and P3-01-AI-012 (Rejection Non-Mutation). Re-verification, conformant, not reopened.

**P3-03-DEP-050.** FR-007 - Cross-Unit with P3-01-AD-005 (HOLD completeness). Re-verification: `trade_lifecycle.py`'s own `on_execution` returns `None` outright for a HOLD action (line 64-65), so a genuine HOLD tick never even reaches the branch that could produce a `RUNTIME_FAILURE_EVENT`; FR-007's own check and the HOLD path are mutually exclusive by construction, consistent with, not contradicting, AD-005.

**P3-03-DEP-051.** FR-016, FR-017, FR-018 - Cross-Unit with P3-02 (AD-001 Composite Isolation, AD-005 Performance Structural Independence, IU-002). Re-verification, not reopened; this is the direct hand-over point the FRA's own Section 6 already names.

**P3-03-DEP-052.** FR-001 through FR-025 (blanket) - Cross-Unit with TD-004 (Lifecycle-based Performance Evaluation). The FRA's own FG-001 through FG-005 collectively constitute the scientific description of TD-004's own subject matter; this SDA does not resolve TD-004, and no dependency in this document requires TD-004 to be resolved before the SDA itself can be considered complete.

**P3-03-DEP-053.** FR-005, FR-012 - Cross-Unit / forwarded, relative to the orphaned `StrategySelector.update` method (P3-03-RR-001) and OQ-002. Its own disposition remains forwarded, not decided by this unit's current scope, consistent with the FRA's own non-decision.

**P3-03-DEP-054.** FR-001 - Cross-Unit with TD-007 (RunLoop Lifecycle Control Surface). Confirmed absent from FR-001's own scope and from every other P3-03 FR's own subject matter; TD-007 remains a future Runtime Control Unit's territory, consistent with P3-01-AD-010's own boundary text ("TD-007 remains a future Runtime Control Unit's").

**P3-03-DEP-055.** FR-019 - Cross-Unit, forwarded, with a not-yet-built future "Reporting" consumer named only in the Runtime Ownership Matrix. Forwarded, not decided, consistent with FRA DG-001 and OQ-003.

All fifty-five Dependency records are individually listed above; none is cited only inside a range expression.

## 12. Absent Dependencies (Explicitly Verified Non-Dependencies)

Recorded for scientific completeness: three plausible-looking dependencies were specifically checked against the FRA's own text and the re-traced active runtime (Section 6), and found **not** to hold.

**No dependency: FR-015 -> FR-021.** The persistence/no-reset lifetime of `self.stats` (FR-015) might suggest a relationship to the general determinism finding (FR-021); direct inspection shows FR-021's own determinism claim holds independent of `self.stats`'s own retention policy, since determinism concerns pure-function behaviour given a state, not the state's own retention duration. No dependency edge is recorded.

**No dependency: FR-016 -> FR-021 / FR-022.** Structural Independence (FR-016, an aliasing/mutation-safety property) and Determinism/order-dependence (FR-021, FR-022) are logically independent properties: a snapshot could be Structurally Independent yet still non-deterministic, or deterministic yet still aliased, in principle. No dependency edge is recorded between FR-016 and either FR-021 or FR-022; FR-016's only recorded dependency target is FR-018 (DEP-018), concerning publication-channel safety, not determinism.

**No dependency: FR-011 -> FR-009.** HOLD (FR-011) and `RUNTIME_FAILURE_EVENT` (FR-009) might appear related as two "special" accounting paths; direct inspection (re-confirmed in Section 6 and DEP-050) shows they are mutually exclusive by construction in the current runtime (`on_execution` returns `None` for HOLD before any `RUNTIME_FAILURE_EVENT` branch could apply), not sequentially or evidentially dependent on one another. No dependency edge is recorded.

## 13. Dependency Graph

Textual representation (REQUIRED edges only; CONDITIONAL, COMPATIBILITY, and CROSS-UNIT edges are listed separately in Section 11.1 and Sections 24/28 and omitted here for readability, since none of them contributes to a directed cycle, Section 25):

```
FR-001 --> FR-002 --> FR-017
FR-001 --> FR-003 --> FR-017
FR-001 --> FR-024
FR-001,FR-017 --> FR-018 --> FR-019
                         \--> FR-020
FR-016 --> FR-018
FR-004 --> FR-005 --> FR-010 --> FR-013 --> FR-011
                  \--> FR-011
FR-012 --> FR-010
FR-006 --> FR-013
FR-006 --> FR-014 --> FR-015
FR-010 --> FR-014
FR-007 --> FR-009
FR-025 --> FR-017
FR-021 --> FR-022
{FR-005,FR-006,FR-007,FR-008} --> FR-023
```

`FR-009` participates only via `FR-007 -> FR-009` (DEP-008) and has no further REQUIRED outgoing edge. `FR-023` and `FR-024` are terminal aggregation nodes with no REQUIRED outgoing edges of their own within this graph.

## 14. Dependency Matrix

### 14.1 Object / Producer / Consumer Cross-Reference

| Object | Producer FR (or external unit) | Consumer FR(s) |
|---|---|---|
| `decision` (dict, `'action'` key) | External (`StrategySelector`, not a P3-03 FR) | FR-005, FR-011, FR-023 |
| `pnl` (scalar) | External (`PnLEngine`, not a P3-03 FR) | FR-006, FR-013, FR-014, FR-023 |
| `regime` (string) | External (`RegimeClassifier`, not a P3-03 FR) | FR-008, FR-023 |
| `trade_event` (`LifecycleEvent`) | External (`TradeLifecycleEngine`, not a P3-03 FR) | FR-007, FR-009, FR-023 |
| `self.stats` (private accumulator) | FR-001, FR-015 | FR-010, FR-013, FR-014, FR-016 |
| Performance snapshot (`_stats_snapshot()`) | FR-016 | FR-017, FR-018 |
| `performance_metrics` (canonical) | FR-002, FR-017 | FR-018, FR-019 |
| tick-result `"performance"` key | FR-018 | FR-020 |

### 14.2 Dependency-Class Distribution

| Class | Count | DEP-ID Range |
|---|---|---|
| REQUIRED | 23 | DEP-001 - DEP-023 |
| CONDITIONAL | 6 | DEP-024 - DEP-029 |
| COMPATIBILITY | 18 | DEP-030 - DEP-047 |
| CROSS-UNIT | 8 | DEP-048 - DEP-055 |
| **Total** | **55** | DEP-001 - DEP-055 |

Full FR-to-DEP and DEP-to-FR traceability is given individually, with no range citation, in Sections 32 and 33.

## 15. Decision-versus-Outcome Analysis

Strict separation, per the governing task's own explicit requirement, between Decision, Execution, Lifecycle Outcome, and Financial Outcome:

- **Decision** (`decision`, produced by `StrategySelector.decide`) is an intention: the tick's own chosen `action`, computed before `Executor.execute` runs. FR-005 establishes this is `PerformanceEngine`'s own primary accounting key today.
- **Execution** (`execution`, produced by `Executor.execute`, carrying `status` in `{BUY_EXECUTED, SELL_EXECUTED, NOOP}`) is the Executor's own outcome for that Decision. FR-012 establishes `PerformanceEngine` never receives this object at all.
- **Lifecycle Outcome** (`trade_event`, a `LifecycleEvent` produced by `TradeLifecycleEngine.on_execution`, with `event_type` in `{TRADE_OPENED, SCALE_IN, PARTIAL_CLOSE, TRADE_CLOSED, RUNTIME_FAILURE_EVENT}`) is the authoritative historical fact of what happened to the lifecycle. FR-007 establishes `PerformanceEngine` reads only the single `event_type == "RUNTIME_FAILURE_EVENT"` equality from this object.
- **Financial Outcome** (`pnl`, produced by `PnLEngine.update`, nonzero only for `TRADE_CLOSED`/`PARTIAL_CLOSE` lifecycle outcomes) is the realized financial consequence of a Lifecycle Outcome. FR-006 establishes `PerformanceEngine` reads this as a bare scalar, with no attached information about which Lifecycle Outcome produced it.

**A Decision produces no Execution** whenever `Executor.execute` returns `{"status": "NOOP"}`, which occurs for every non-BUY/non-SELL `action` (i.e. every HOLD Decision). **An Execution produces no accepted Lifecycle transition** in the current runtime only in the failure paths of `TradeLifecycleEngine` (`_scale_in`/`_close_trade`/`_partial_close`/`_full_close` each return a `RUNTIME_FAILURE_EVENT` via `_failure_event` when `NO_ACTIVE_TRADE` or `OVER_CLOSE_QUANTITY` conditions hold, or `on_execution` itself returns a `RUNTIME_FAILURE_EVENT` for `INVALID_EXECUTION_QUANTITY` or `UNSUPPORTED_EXECUTION_ACTION`); every accepted, non-HOLD Execution in the current runtime otherwise always produces exactly one Lifecycle transition (`TRADE_OPENED`, `SCALE_IN`, `PARTIAL_CLOSE`, or `TRADE_CLOSED`). **A tick produces no trade activity at all** whenever the Decision's own `action` is `HOLD` (`on_execution` returns `None` before generating any `LifecycleEvent`) or whenever the Execution fails validation, producing only a `RUNTIME_FAILURE_EVENT`.

**Why raw Decisions are scientifically insufficient grounds for Trade Performance**, established directly by the chain above: a Decision alone determines neither whether an Execution occurred, nor whether a Lifecycle transition was accepted, nor whether any Financial Outcome was realized. `PerformanceEngine.update` (FR-005, FR-010, FR-012) currently increments its own `trades` counter and evaluates its own `wins` test purely from the Decision's `action` and the tick's `pnl` scalar, without any intervening check that an Execution succeeded or that a Lifecycle Outcome was accepted; a HOLD-cooldown Decision, a validation-failed Execution's own `RUNTIME_FAILURE_EVENT` tick (whose `pnl` is always `0.0` per `PnLEngine.compute_equity`'s own short-circuit), and a genuine `TRADE_CLOSED` tick are each counted with equal weight in the same `trades`/`wins` denominator whenever they happen to share the same decided `action`. This is the precise causal mechanism underlying FRA FG-001, FG-002, and FG-004, restated here at the dependency level (DEP-004, DEP-006, DEP-009, DEP-011, DEP-036).

## 16. Execution and Lifecycle Dependencies

FR-012 (no `execution` read) and FR-007 (`trade_event.event_type` read only for `RUNTIME_FAILURE_EVENT`) are the two Functional Requirements governing this topic. DEP-011 (FR-012 -> FR-010) establishes that the unconditional `trades` increment is a direct structural consequence of Execution-blindness. DEP-008 (FR-007 -> FR-009) establishes the only Lifecycle-facing behaviour that currently exists is the failure short-circuit. No REQUIRED dependency connects FR-007 or FR-012 to any of FR-013 or FR-014 (wins/pnl-mean computation), since neither `wins` nor the `pnl`-mean formula reads `trade_event` or `execution` at all (Section 11 of the FRA, re-confirmed Section 6); this asymmetry - Lifecycle/Execution information being available at the call site (`loop.py:95`) but not read by the accounting formulas themselves - is the structural basis of FG-005 and DEP-046.

## 17. Position and Financial Dependencies

`PerformanceEngine` has no REQUIRED dependency on `PositionEngine` or `RiskEngine` output (FR-023, confirmed by direct method-body inspection, Section 11 of the FRA). Its sole Financial dependency is on `PnLEngine`'s own scalar `pnl` output (FR-006, DEP-006, DEP-007). This is COMPATIBILITY-conformant with P2-02A and P2-03 (DEP-045): `PerformanceEngine` never reopens or touches Position or Financial ownership itself, it only consumes an already-published, already-certified scalar. The absence of any Position/Risk dependency is itself consistent with the FRA's own Section 17.14 finding and is not reopened here.

## 18. Performance Aggregation Dependencies

FR-010, FR-013, FR-014 form the aggregation core: `trades` (FR-010) is the shared denominator for both the `pnl` running mean (FR-014, DEP-010) and `winrate` (via `wins`, FR-013, DEP-009). FR-011 (HOLD bucket) and DEP-023 (FR-013 -> FR-011) confirm the aggregation mechanics apply uniformly across every bucket, including HOLD, with no bucket-specific branching. FR-015 (lifetime) is a REQUIRED prerequisite (DEP-012) for the running-mean formula's own continued validity as a description of the runtime across its full process lifetime.

## 19. Historical Information Dependencies

FR-015 establishes no historization mechanism exists; Section 6's own extended repository-wide search (beyond the FRA's own scope, now covering `run_engine/execution/`, `run_engine/feedback/`, and `run_engine/logging/` in addition to `run_engine/runtime/`) confirms this negative finding is repository-wide, not merely active-path-local. DEP-038 (FR-015 - AC-008's third clause) and DEP-029 (FR-015 -> FR-024, CONDITIONAL) are the two dependencies governing this topic; DEP-038 records the current non-conformance (same substance as FG-003), and DEP-029 records that this non-conformance's own future disposition is bound to TD-004's own resolution and to OQ-004.

## 20. Failure / Rejection / HOLD Dependencies

FR-007 and FR-009 govern `RUNTIME_FAILURE_EVENT` behaviour (DEP-008, DEP-039, DEP-049); FR-011 governs HOLD behaviour (DEP-005, DEP-023). DEP-050 (FR-007 - Cross-Unit with P3-01-AD-005) and the Absent Dependency in Section 12 (FR-011 -> FR-009) jointly establish that HOLD and `RUNTIME_FAILURE_EVENT` are mutually exclusive, not sequentially related, conditions in the current runtime: a HOLD Decision never reaches `TradeLifecycleEngine`'s own failure-generating branches at all, since `on_execution` returns `None` immediately for `action == "HOLD"`. No explicit "rejected transition" concept distinct from `RUNTIME_FAILURE_EVENT` exists anywhere in `run_engine/core` (re-confirmed Section 6); `Executor`'s own `NOOP` status is the closest related concept and is, per FR-012/DEP-011, never read by `PerformanceEngine` at all. P3-01-AI-012's own explicit inclusion of "Performance statistics" among values a rejected transition shall never mutate (DEP-039, DEP-049) is satisfied today, since `PerformanceEngine`'s only failure-aware branch performs no mutation.

## 21. Determinism and Replay Dependencies

FR-021 (pure-function determinism) and FR-022 (order-dependent intermediate snapshots) are related by DEP-019 (REQUIRED, refinement not contradiction). DEP-043 (FR-021 - AI-005, AC-012) records conformance. The Absent Dependencies in Section 12 (FR-015 -> FR-021; FR-016 -> FR-021/FR-022) establish that neither `self.stats`'s own retention policy nor Structural Independence bears on the determinism finding itself; determinism rests solely on the absence of randomness, wall-clock reads, and I/O in `PerformanceEngine.update`'s own method body (re-confirmed Section 6), a property independent of both lifetime and aliasing-safety.

## 22. Ownership and Publication Dependencies

FR-001, FR-002, FR-003 (Cluster A) and FR-016, FR-017, FR-018 (Cluster G) together form the complete Ownership-and-Publication chain: FR-001 (Computational Authority) -> FR-002 (Authoritative Owner) -> FR-017 (Writer-on-Behalf-Of publication mechanism, also depending on FR-003) -> FR-018 (dual-channel exposure, also depending on FR-016's own Structural Independence). DEP-030, DEP-031, DEP-033 record COMPATIBILITY-conformance with AI-002, AI-003, and Rule OM-001/OM-002/OM-003 respectively; DEP-041 records conformance with the already-certified P3-02-AD-005/IU-002. No dependency in this cluster is non-conformant; every Ownership-and-Publication-layer FR is a Verified Conformant Finding at the FRA level (VCF-001, VCF-002) and remains so at this SDA's own dependency level.

## 23. Reporting Dependencies

FR-019 (zero active internal consumer; "Reporting" unconfirmed) and FR-020 (sole external consumer, `main.py`'s own `print`) are the two governing Functional Requirements. DEP-016, DEP-017 (REQUIRED, both derived from FR-018's own publication channels) establish the structural basis. DEP-025 (CONDITIONAL, OQ-003) and DEP-055 (CROSS-UNIT, forwarded) both record that "Reporting"'s own eventual disposition - a genuinely future module, or stale Baseline documentation - is not decided by this unit and remains an open, forwarded question, consistent with FRA DG-001.

## 24. Alternative-Path Dependencies

FR-024 (the inactive `performance_analytics.py`) is the FRA's own named alternative path. DEP-021 (REQUIRED, FR-001 -> FR-024) records that FR-024's own inactivity is exactly the evidence supporting FR-001's own "sole" Computational Authority claim. DEP-044 (COMPATIBILITY, AI-013 tension) records that its continued unreconciled existence is a latent, not active, tension with Architectural Minimality. DEP-024, DEP-026, DEP-029 (CONDITIONAL) record that its own future relevance is entirely contingent on OQ-001 and OQ-004, neither resolved by this document. Section 6's own extended search additionally surfaced three further inactive, unreferenced files touching the same Decision/Execution-status vocabulary (`run_engine/execution/adapter.py`, `run_engine/feedback/tracker.py`, `run_engine/runtime/strategy_memory.py`); none of these three is itself a Performance-accounting implementation (none computes `pnl`, `trades`, or `winrate`), so none is added as a new FR-024-equivalent target; they are recorded here as context extending, not altering, the FRA's own FR-024 finding, and do not participate in the Dependency Catalogue as independent DEP targets.

## 25. Coupling and Cycle Analysis

### 25.1 Cycle Detection

The REQUIRED-edge graph (Section 13) was checked for cycles by direct topological inspection of every edge in Section 11.1 classified REQUIRED. Result: **no cyclic dependency was found.** The graph is a directed acyclic graph (DAG) with three convergence points: FR-010 (receiving from FR-005 and FR-012, itself feeding FR-013 and FR-014), FR-017 (receiving from FR-002, FR-003, and FR-025, itself feeding FR-018), and FR-023 (an aggregate sink receiving from FR-005, FR-006, FR-007, FR-008 with no further REQUIRED outgoing edge).

**FR-013 and FR-011 do not form a cycle with FR-005.** FR-005 feeds both FR-010 (DEP-004) and FR-011 (DEP-005) directly, and FR-010 also feeds FR-013 (DEP-009), which itself feeds FR-011 (DEP-023). This creates two independent paths from FR-005 to FR-011 (`FR-005 -> FR-011` directly, and `FR-005 -> FR-010 -> FR-013 -> FR-011`), a convergence, not a cycle: both paths run strictly forward, and no edge runs from FR-011 back to FR-005, FR-010, or FR-013. Direct inspection confirms FR-011's own HOLD-bucket treatment is purely a consequence of upstream keying and aggregation mechanics; it produces no output any upstream FR consumes.

**FR-018 and FR-016/FR-017 do not form a cycle.** FR-016 and FR-017 both feed FR-018 (DEP-018, DEP-015); FR-018 itself feeds only FR-019 and FR-020 (DEP-016, DEP-017), a strict terminal fan-out with no edge running back to FR-016, FR-017, FR-002, or FR-003.

### 25.2 Coupling Analysis (Task-Mandated Checks)

**Performance -> Financial -> Performance feedback.** Checked directly against `PnLEngine`'s own full method bodies (`update`, `compute_equity`, re-read fresh, Section 6): neither method accepts `performance_metrics`, `self.stats`, or any `PerformanceEngine`-produced value as an input. No feedback path exists; `PerformanceEngine` is a pure downstream consumer of `PnLEngine`'s own `pnl` output, never the reverse.

**Performance -> Strategy feedback.** Checked directly against `StrategySelector`'s own full method bodies (`select`, `decide`, `update`, re-read fresh, Section 6): none accepts `performance_metrics` or any `PerformanceEngine`-produced value. The orphaned `StrategySelector.update(decision, pnl, regime)` method, even if it were activated (P3-03-RR-001, DEP-027/DEP-053), would consume `pnl` from `PnLEngine`, not from `PerformanceEngine`; activating it would establish a Financial-to-Strategy coupling parallel to, but independent of, Performance. No current, and no even-if-activated, Performance-to-Strategy feedback cycle exists.

**Hidden dependency on Decision instead of Outcome.** This is not a cycle; it is a documented, one-directional miscoupling (Section 15; FRA FG-001/FG-002/FG-004; DEP-005, DEP-047). It is recorded here as a Coupling Finding, not conflated with a cyclic dependency.

**Competing producers / duplicate Computational Authority.** `performance_analytics.py` (FR-024) is confirmed inactive (Section 6, Section 24); it is not a currently-active competing producer. If it were ever activated without reconciliation against whatever methodology the P3-03 Architecture stage adopts, it would become one; this is recorded as a Residual Risk (FRA RR-002) and a latent AI-013 tension (DEP-044), not a current cycle or a current coupling violation.

**Downstream reconstruction.** Since FR-019/FR-020 establish zero active internal consumers, no active runtime component reconstructs Decision, Execution, Lifecycle, or Financial information from Performance's own output; this check is vacuously satisfied by the absence of any internal consumer.

**Cross-tick mutable state / implicit dependency on `self.stats`.** This is real and explicitly documented (FR-015, FR-022; DEP-012, DEP-019, DEP-029): each tick's own published snapshot is a running mean over the *entire* accumulated history of every prior tick decided with the same `action`, meaning every published snapshot implicitly, non-locally depends on the full sequence of every prior tick's `(action, pnl)` pair processed since `PerformanceEngine.__init__`. This is a genuine temporal (cross-tick) coupling internal to a single component's own private state, structurally different from a producer/consumer cycle between two components: it is a linear historical accumulation (each tick folds its own contribution into a running mean and moves forward), not a circular one, and it was independently confirmed acyclic in Section 25.1. It is recorded here explicitly as the Coupling Finding the governing task's own "implicit dependency on PerformanceEngine.self.stats" item requires, distinct from, and not to be conflated with, cycle detection.

### 25.3 Potential Future Feedback Loops (Explicitly Not a Current Runtime Cycle)

Should a future Architecture stage decide to feed Performance Metrics back into `StrategySelector` (for example, via a reconciled version of the orphaned `StrategySelector.update` method, per OQ-002) for adaptive strategy weighting, this would constitute a new, not-yet-existing feedback loop. This document explicitly does not describe any such possibility as a current runtime cycle; Sections 25.1 and 25.2 both confirm the current, active runtime contains no cycle of any kind touching Performance. This paragraph records only that such a loop does not exist today, consistent with the governing task's own explicit instruction not to present a potential future feedback loop as a current one.

## 26. Dependency Findings

**Finding SDF-001.** No cyclic dependency exists among the twenty-five Functional Requirements; the REQUIRED-edge graph is a strict DAG (Section 25.1).

**Finding SDF-002.** Three of the eighteen Compatibility Dependencies newly ground already-known Functional Gaps in Baseline text the FRA itself did not cite: Rule OM-008 (DEP-032), Baseline-level AC-008 (DEP-037, DEP-038), and ADR-002's own Runtime Event hierarchy (DEP-047). None of these constitutes a new finding of non-conformance beyond what FG-001, FG-002, FG-003, and FG-004 already established; each strengthens the same findings' own evidentiary basis with an additional, independent citation.

**Finding SDF-003.** The dependency graph exhibits three structural convergence points (FR-010, FR-017, FR-023), each consistent with its own role: FR-010 as the shared `trades` denominator every aggregation formula depends on, FR-017 as the single publication mechanism every write path funnels through, and FR-023 as the aggregate restatement of the complete read-set. None indicates an undue concentration of unverified risk; all three are themselves currently-evidenced facts (FRA Section 18), not open gaps.

**Finding SDF-004.** Every Conditional Dependency in this document (DEP-024 through DEP-029) resolves around exactly the FRA's own four Open Questions (OQ-001 through OQ-004); no Conditional Dependency introduces a new Open Question the FRA did not already name.

**Finding SDF-005.** Three plausible dependencies were specifically checked and found absent (Section 12): FR-015 does not feed FR-021; FR-016 does not feed FR-021 or FR-022; FR-011 does not feed FR-009. All three are explicit, repository-grounded findings of the current active trace, not omissions.

**Finding SDF-006.** All eighteen Compatibility Dependencies and all eight Cross-Unit Dependencies (Sections 11.1) are one-directional out of this unit's own scope; no Compatibility or Cross-Unit Dependency requires, or would be satisfied by, any decision this document or a future P3-03 document makes.

**Finding SDF-007.** Seven of the eighteen Compatibility Dependencies record explicit non-conformance (DEP-032, DEP-036, DEP-037, DEP-038, DEP-042, DEP-046, DEP-047); these seven collectively and precisely correspond, at the dependency level, to the five Functional Gaps the FRA already recorded (FG-001 through FG-005), with no additional non-conformance discovered beyond what the FRA already identified. This SDA finds no new Functional Gap; it only finds additional Baseline citations supporting the FRA's own existing five.

**Finding SDF-008 (Coupling).** No Performance-to-Financial, Performance-to-Strategy, or any other feedback cycle exists in the current active runtime (Section 25.2). The one genuine coupling concern identified - `self.stats`'s own cross-tick, non-local dependence on the full historical tick sequence - is a linear (non-circular) temporal coupling internal to a single component, already fully captured by FR-015 and FR-022, and does not constitute a cycle.

## 27. Dependency Risks

**P3-03-DR-001.** DEP-047 (ADR-002 Event Hierarchy non-conformance) and DEP-042 (Target Information Flow Runtime-Stage-Responsibilities non-conformance) both concern the same underlying fact (Performance currently consumes a far-upstream Decision Event rather than the immediately-preceding Risk Event / Lifecycle+Financial state); a future Architecture stage addressing one is very likely to need to address the other jointly, given they describe the same divergence from two different Baseline sections. Risk: treating them as independent Architecture questions could produce two partially-overlapping, mutually inconsistent fixes if not consciously coordinated at the Architecture stage. Non-blocking for this SDA; flagged for the CGA and Architecture stages' own awareness.

**P3-03-DR-002.** DEP-044 (AI-013 tension for `performance_analytics.py`) and the three newly-found inactive files in Section 24 (`adapter.py`, `tracker.py`, `strategy_memory.py`) together represent a broader pattern of dormant, Decision/Execution-status-aware code scattered outside `run_engine/core`. Risk: a future Architecture stage resolving TD-004 in isolation, without an explicit disposition decision for this dormant code, could leave the redundancy tension unresolved indefinitely. Non-blocking; not this SDA's own decision to make (Section 2).

**P3-03-DR-003.** DEP-027 and DEP-053 (orphaned `StrategySelector.update`, OQ-002) both note this method shares FR-005's and FR-012's exact subject matter. Risk: if a future Architecture stage revises `PerformanceEngine`'s own accounting methodology without also examining this orphaned method, an inconsistency between two independently-evolving decision-keyed accounting mechanisms (one active in `PerformanceEngine`, one dormant in `StrategySelector`) could persist unnoticed. Non-blocking; forwarded via OQ-002.

## 28. Dependency Constraints

- No dependency in this document may be interpreted as, or used to justify, an Architecture Decision, a Performance-keying selection, a Performance formula, a History schema, or a Reporting-module design (Section 2).
- Every Compatibility Dependency (DEP-030 through DEP-047) constrains a future Architecture stage to either restore conformance with the cited Baseline contract or to explicitly obtain an Architecture Evolution Review overriding it (per AI-015); this document does not itself decide which.
- Every Cross-Unit Dependency (DEP-048 through DEP-055) constrains this unit, and every future P3-03 document, to never reopen the cited P3-01, P3-02, or Baseline-level decision.
- DEP-052's own blanket TD-004 relationship constrains the future P3-03 CGA to classify Capability status for FR-005, FR-006, FR-007, FR-010, FR-012, FR-013, FR-014, FR-015, and FR-023 with explicit reference to TD-004's own continued open status, consistent with how the P3-02 CGA handled its own TD-004-adjacent findings.

## 29. Open Questions

This document decides none of the FRA's own four Open Questions (OQ-001 through OQ-004, FRA Section 24). The following restates, for dependency-analysis purposes only, which Open Question resolution would affect which dependency, and adds one new dependency-specific question this analysis itself surfaced.

**OQ-001 (restated from the FRA).** Whether Architecture targets the `LifecycleEvent` stream directly as `PerformanceEngine`'s primary input, replacing `decision`, determines the final disposition of DEP-024 and DEP-028, and bears directly on how DEP-047 (ADR-002 Event Hierarchy) and DEP-042 (Target Information Flow) are ultimately resolved.

**OQ-002 (restated from the FRA).** Whether the orphaned `StrategySelector.update` method is in scope for P3-03 determines the final disposition of DEP-027 and DEP-053.

**OQ-003 (restated from the FRA).** Whether "Reporting" names a future module or is stale Baseline documentation determines the final disposition of DEP-025 and DEP-055.

**OQ-004 (restated from the FRA).** Whether `performance_analytics.py` is considered within P3-03's own scope boundary determines the final disposition of DEP-024, DEP-026, and DEP-029.

**OQ-016 (new, this document).** DEP-047 and DEP-042 both describe the same underlying divergence from two textually distinct Baseline sections (ADR-002's Event Hierarchy and the Target Information Flow's Runtime Stage Responsibilities table). Should a future P3-03 Architecture treat these as one unified Architecture Decision, or as two separately-justified ones consistent with each citation's own distinct textual origin? This document does not decide document-drafting questions belonging to a later stage; it only notes, per Dependency Risk DR-001, that the two citations describe one fact, not two independent facts.

No question above is decided by this document.

## 30. Scientific Conclusions

1. The twenty-five P3-03 Functional Requirements form a strict, acyclic dependency structure (Finding SDF-001); no REQUIRED, CONDITIONAL, COMPATIBILITY, or CROSS-UNIT dependency in this document is circular, and no feedback loop exists in the currently active runtime (Finding SDF-008).
2. Every one of the FRA's own five Functional Gaps is independently re-derivable at the dependency level from this document's own Compatibility Dependencies, and three additional Baseline citations (Rule OM-008, Baseline AC-008, ADR-002's Event Hierarchy) further strengthen, without altering, that same evidentiary picture (Finding SDF-002, SDF-007).
3. The scientific root cause common to FG-001, FG-002, and FG-004 is precisely characterized at the dependency level by Section 15 (Decision-versus-Outcome Analysis): raw Decisions alone determine neither Execution success, nor Lifecycle acceptance, nor Financial realization, yet are the sole current accounting key.
4. No REQUIRED dependency connects Performance to Position or Risk (Section 17); Performance's only Financial dependency is the bare scalar `pnl` (Section 15), consistent with, and not reopening, P2-02A/P2-03's own certified ownership.
5. Every Ownership, Publication, and Structural-Independence-layer Functional Requirement (Cluster A, Cluster G) remains fully Compatibility-conformant; no non-conformance was found outside the accounting-mechanics and read-set layers the FRA already identified (Section 22).
6. All Conditional Dependencies trace to the FRA's own four already-recorded Open Questions; this document surfaces no new architecturally-significant uncertainty beyond OQ-016, a document-drafting-scope question, not a scientific one (Section 29).

## 31. CGA Readiness Decision

Every theme the governing task requires has been produced: Requirement Clusters (Section 9), Dependency Layers (Section 10), a Full Dependency Catalogue (Section 11.1), a Dependency Graph (Section 13), a Dependency Matrix (Section 14), Decision-versus-Outcome Analysis (Section 15), Execution/Lifecycle, Position/Financial, Aggregation, Historical, Failure/Rejection/HOLD, Determinism/Replay, Ownership/Publication, Reporting, and Alternative-Path Dependencies (Sections 16-24), Coupling and Cycle Analysis (Section 25), Dependency Findings, Risks, Constraints, and Open Questions (Sections 26-29), and Scientific Conclusions (Section 30). No new Functional Requirement was introduced; no Capability was classified; no Architecture Decision was made; no runtime file was modified.

**Dependency Readiness: READY.** This document is sufficient to proceed to the P3-03 Capability Gap Analysis. The CGA must independently re-verify every dependency here against the repository state at its own drafting time, per this governance chain's own established discipline, and must in particular assign Capability status to FR-005, FR-006, FR-007, FR-010, FR-012, FR-013, FR-014, FR-015, and FR-023 with explicit reference to the seven non-conformant Compatibility Dependencies (DEP-032, DEP-036, DEP-037, DEP-038, DEP-042, DEP-046, DEP-047) and to TD-004's own continued open status (DEP-052).

## 32. FRA Traceability

Every one of the twenty-five Functional Requirements participates in at least one dependency record.

| FR | Dependency Record(s) |
|---|---|
| FR-001 | DEP-001, DEP-002, DEP-015, DEP-021, DEP-031, DEP-032, DEP-052, DEP-054 |
| FR-002 | DEP-001, DEP-013, DEP-030, DEP-032 |
| FR-003 | DEP-002, DEP-014, DEP-033 |
| FR-004 | DEP-003, DEP-035, DEP-048 |
| FR-005 | DEP-003, DEP-004, DEP-005, DEP-020, DEP-024, DEP-027, DEP-032, DEP-036, DEP-037, DEP-047, DEP-053 |
| FR-006 | DEP-006, DEP-007, DEP-020, DEP-036, DEP-045, DEP-047 |
| FR-007 | DEP-008, DEP-020, DEP-028, DEP-036, DEP-039, DEP-046, DEP-047, DEP-050 |
| FR-008 | DEP-020, DEP-040 |
| FR-009 | DEP-008, DEP-028, DEP-039, DEP-049 |
| FR-010 | DEP-004, DEP-009, DEP-010, DEP-011, DEP-032, DEP-036, DEP-037, DEP-046 |
| FR-011 | DEP-005, DEP-023 |
| FR-012 | DEP-011, DEP-027, DEP-045, DEP-053 |
| FR-013 | DEP-006, DEP-009, DEP-023, DEP-032, DEP-036, DEP-037 |
| FR-014 | DEP-007, DEP-010, DEP-012, DEP-036 |
| FR-015 | DEP-012, DEP-029, DEP-038 |
| FR-016 | DEP-018, DEP-041, DEP-051 |
| FR-017 | DEP-013, DEP-014, DEP-015, DEP-022, DEP-041, DEP-051 |
| FR-018 | DEP-015, DEP-016, DEP-017, DEP-018, DEP-051 |
| FR-019 | DEP-016, DEP-025, DEP-026, DEP-034, DEP-055 |
| FR-020 | DEP-017, DEP-025, DEP-034 |
| FR-021 | DEP-019, DEP-043 |
| FR-022 | DEP-019 |
| FR-023 | DEP-020, DEP-042 |
| FR-024 | DEP-021, DEP-024, DEP-026, DEP-029, DEP-044 |
| FR-025 | DEP-022 |

All twenty-five Functional Requirements are traced to at least one dependency record.

## 33. DEP Traceability (Individually Enumerated)

| DEP | Class | FR(s) |
|---|---|---|
| DEP-001 | REQUIRED | FR-001, FR-002 |
| DEP-002 | REQUIRED | FR-001, FR-003 |
| DEP-003 | REQUIRED | FR-004, FR-005 |
| DEP-004 | REQUIRED | FR-005, FR-010 |
| DEP-005 | REQUIRED | FR-005, FR-011 |
| DEP-006 | REQUIRED | FR-006, FR-013 |
| DEP-007 | REQUIRED | FR-006, FR-014 |
| DEP-008 | REQUIRED | FR-007, FR-009 |
| DEP-009 | REQUIRED | FR-010, FR-013 |
| DEP-010 | REQUIRED | FR-010, FR-014 |
| DEP-011 | REQUIRED | FR-012, FR-010 |
| DEP-012 | REQUIRED | FR-014, FR-015 |
| DEP-013 | REQUIRED | FR-002, FR-017 |
| DEP-014 | REQUIRED | FR-003, FR-017 |
| DEP-015 | REQUIRED | FR-001, FR-017, FR-018 |
| DEP-016 | REQUIRED | FR-018, FR-019 |
| DEP-017 | REQUIRED | FR-018, FR-020 |
| DEP-018 | REQUIRED | FR-016, FR-018 |
| DEP-019 | REQUIRED | FR-021, FR-022 |
| DEP-020 | REQUIRED | FR-005, FR-006, FR-007, FR-008, FR-023 |
| DEP-021 | REQUIRED | FR-001, FR-024 |
| DEP-022 | REQUIRED | FR-025, FR-017 |
| DEP-023 | REQUIRED | FR-013, FR-011 |
| DEP-024 | CONDITIONAL | FR-005, FR-024 |
| DEP-025 | CONDITIONAL | FR-019, FR-020 |
| DEP-026 | CONDITIONAL | FR-024, FR-019 |
| DEP-027 | CONDITIONAL | FR-005, FR-012 |
| DEP-028 | CONDITIONAL | FR-009, FR-007 |
| DEP-029 | CONDITIONAL | FR-015, FR-024 |
| DEP-030 | COMPATIBILITY | FR-002 |
| DEP-031 | COMPATIBILITY | FR-001 |
| DEP-032 | COMPATIBILITY | FR-001, FR-005, FR-010, FR-013, FR-014 |
| DEP-033 | COMPATIBILITY | FR-003 |
| DEP-034 | COMPATIBILITY | FR-019, FR-020 |
| DEP-035 | COMPATIBILITY | FR-004 |
| DEP-036 | COMPATIBILITY | FR-005, FR-006, FR-007, FR-010, FR-012, FR-013, FR-014 |
| DEP-037 | COMPATIBILITY | FR-005, FR-010, FR-013 |
| DEP-038 | COMPATIBILITY | FR-015 |
| DEP-039 | COMPATIBILITY | FR-007, FR-009 |
| DEP-040 | COMPATIBILITY | FR-008 |
| DEP-041 | COMPATIBILITY | FR-016, FR-017 |
| DEP-042 | COMPATIBILITY | FR-023 |
| DEP-043 | COMPATIBILITY | FR-021 |
| DEP-044 | COMPATIBILITY | FR-024 |
| DEP-045 | COMPATIBILITY | FR-006, FR-012 |
| DEP-046 | COMPATIBILITY | FR-007, FR-010 |
| DEP-047 | COMPATIBILITY | FR-005, FR-006, FR-007 |
| DEP-048 | CROSS-UNIT | FR-004 |
| DEP-049 | CROSS-UNIT | FR-009 |
| DEP-050 | CROSS-UNIT | FR-007 |
| DEP-051 | CROSS-UNIT | FR-016, FR-017, FR-018 |
| DEP-052 | CROSS-UNIT | FR-001..FR-025 (blanket) |
| DEP-053 | CROSS-UNIT | FR-005, FR-012 |
| DEP-054 | CROSS-UNIT | FR-001 |
| DEP-055 | CROSS-UNIT | FR-019 |

All fifty-five Dependency records are individually listed above; none is cited only inside a range expression.

## 34. ADR / Invariant / AC Traceability

Every Architecture Decision, Invariant, and Acceptance Criterion this document cites is individually listed below, with the dependency record(s) that cite it. This document cites ADR-001, ADR-002, ADR-008, ADR-010, ADR-011 from the required "ADR-001 bis ADR-012" range explicitly; the remaining ADRs (ADR-003 through ADR-007, ADR-009, ADR-012) were re-read in full (Section 5) and confirmed to have no direct Performance-specific dependency beyond what is already captured through P2-02A/P2-03/P2-04 Compatibility (DEP-045) and general architectural context, and are therefore not separately cited as a DEP target, consistent with the instruction not to reopen ownership or ordering decisions those ADRs govern.

| Baseline Item | Cited By |
|---|---|
| ADR-001 (SSOT) | Section 5 context; underlies AI-001/AI-002 (DEP-030, DEP-031) |
| ADR-002 (Event-Driven Runtime Evolution) | DEP-047 |
| ADR-008 (Performance Ownership) | DEP-036 |
| ADR-010 (Deterministic Runtime Execution Ordering) | DEP-035, DEP-048 |
| ADR-011 (Runtime Failure Handling) | DEP-039 |
| Runtime Ownership Matrix, "Performance Metrics" row | Section 5, Section 7 context; underlies DEP-030 through DEP-034 |
| Rule OM-001 | DEP-030 |
| Rule OM-002 | DEP-031 |
| Rule OM-003 | DEP-033 |
| Rule OM-004 | DEP-034 |
| Rule OM-008 | DEP-032 |
| Target Information Flow, Runtime Stage Responsibilities table | DEP-042 |
| Principle / Rule IF-003 | DEP-040 |
| Rule IF-005 | DEP-042 |
| Tick Completion Contract | DEP-035 |
| AI-002 (Unique Ownership) | DEP-030 |
| AI-003 (Separation of Ownership and Computation) | DEP-031 |
| AI-005 (Deterministic Execution) | DEP-043 |
| AI-007 (Semantic Continuity) | DEP-040 |
| AI-012 (Rejection Non-Mutation, P3-01) | DEP-039, DEP-049 |
| AI-013 (Architectural Minimality) | DEP-044 |
| AC-008 (Performance Evaluation, Baseline-level) | DEP-037, DEP-038 |
| AC-012 (Deterministic Behaviour) | DEP-043 |
| AC-014 (Lifecycle Semantics) | DEP-046 |
| P3-01-AD-001 | DEP-048 |
| P3-01-AD-005 | DEP-050 |
| P3-01-AD-006 | DEP-049 |
| P3-01-AD-010 | Section 5 context (Cross-Unit ratification of TD-004 to P3-03), underlies DEP-052, DEP-054 |
| P3-01's own DEP-009 | DEP-048 |
| P3-02-AD-001 (Composite Isolation) | DEP-051 context |
| P3-02-AD-005 (Performance Structural Independence) | DEP-041, DEP-051 |
| P3-02-IU-002 | DEP-041, DEP-051 |

Every ADR/AI/AC item this document actually relies upon is individually cited above; none is cited only inside a range expression. The task's own requested "AI-001 bis AI-009, AI-012, AI-014" and "AC-001 bis AC-012" ranges were checked individually against this document's own actual findings: AI-001, AI-004, AI-006, AI-008, AI-009, AI-010, AI-011, AI-014, and AI-015, and AC-001 through AC-007, AC-009 through AC-011 were each re-read (Section 5) and confirmed to have no Performance-specific dependency this document needs to record beyond the general architectural context already established by ADR-001/ADR-002/the Ownership Matrix/the Target Information Flow; they are not separately cited as DEP targets because doing so would not add a new, distinct finding beyond what is already captured.

## 35. Prior-Certification Compatibility

This document does not reopen, and confirms it remains compatible with:

- **P2-02A (Position Ownership)** - Architecture, Specification, Final Certification: not reopened; DEP-045 confirms `PerformanceEngine` never touches Position ownership.
- **P2-03 (Financial Ownership)** - Architecture, Specification, Final Certification: not reopened; DEP-045 confirms `PerformanceEngine` only consumes `PnLEngine`'s own already-published scalar `pnl`.
- **P2-04 (Risk Ownership)** - Architecture, Specification, Final Certification: not reopened; Section 17 confirms no dependency exists between `PerformanceEngine` and `RiskEngine` output at all.
- **P3-01 (Deterministic Execution Ordering)** - complete governance chain, including Final Certification: not reopened; DEP-048, DEP-049, DEP-050 re-verify, without altering, AD-001, AD-005, AD-006, AD-010, and AI-012.
- **P3-02 (Information Flow Validation)** - complete governance chain, including Final Certification: not reopened; DEP-041, DEP-051 re-verify, without altering, AD-001, AD-005, and IU-002.

No dependency record in this document requires, or would be satisfied by, reopening any of the above. Every certified contract cited remains, per this document's own findings, the fixed ground every relevant Compatibility or Cross-Unit Dependency measures against.

## 36. Internal Consistency Review

**Scientific Consistency Review.** Every dependency in Section 11.1 cites a specific FRA field, a specific independently re-verified repository fact (Section 6), or a specific Baseline citation (Section 5); no dependency is asserted from topical similarity alone. PASS.

**Dependency Consistency Review.** Section 32 confirms all twenty-five FRs are traced to at least one dependency; Section 33 confirms all fifty-five dependency records are individually enumerated, none only inside a range expression; Section 14.2's own class-distribution counts (23 + 6 + 18 + 8 = 55) match the DEP-ID range stated in Section 11.1. PASS.

**Architecture Compatibility Review.** No dependency record in Section 11.1 selects a resolution mechanism, a keying scheme, a formula, or a history schema; every dependency states a relationship or a compatibility finding, never a solution. No Architecture Decision is made anywhere in this document. PASS.

**Performance Semantics Review.** Section 15 (Decision-versus-Outcome Analysis) strictly separates Decision, Execution, Lifecycle Outcome, and Financial Outcome throughout, per the governing task's own explicit requirement; no section of this document conflates any two of these four concepts. PASS.

**Lifecycle Dependency Review.** Section 16 and Section 20 individually confirm every Lifecycle-facing dependency (FR-007, FR-009, FR-011) and correctly attribute HOLD/RUNTIME_FAILURE_EVENT mutual exclusivity to direct repository evidence (`trade_lifecycle.py`'s own `on_execution`), not to assumption. PASS.

**Financial Dependency Review.** Section 17 confirms the sole Financial dependency (`pnl` from `PnLEngine`) and confirms no Position or Risk dependency exists, consistent with fresh repository re-verification (Section 6). PASS.

**Scope Review.** Section 2 and Section 31 confirm no new Functional Requirement, no Capability classification, and no runtime change occurs anywhere in this document; Sections 24, 28, and 35 confirm every Compatibility and Cross-Unit Dependency remains one-directional out of P3-03's own scope. PASS.

**Terminology Review.** "Functionally identical" and "byte-identical" are not used as runtime- or file-comparison claims anywhere in this document (no such comparison is performed here; this sentence and Section 37 are this document's only discussion of either term). "REQUIRED," "CONDITIONAL," "CROSS-UNIT," and "COMPATIBILITY" are used exactly as defined in Section 8 throughout, with no dependency record left unclassified. "Decision," "Execution," "Lifecycle Outcome," and "Financial Outcome" are used with the strict, distinct meanings defined in Section 15 throughout, with no section conflating any two of them. PASS.

**Repository Consistency Review.** Every repository-grounded claim in Section 6 was independently re-verified against the current runtime during this document's own drafting, including three newly-found inactive files (`adapter.py`, `tracker.py`, `strategy_memory.py`) and the confirmed absence of history/reporting infrastructure across the entire repository, not merely the active path. PASS.

**Runtime Consistency Review.** All ten explicitly re-verified runtime files (Section 6) match the FRA's own prior description exactly; no drift was found between the FRA's own drafting time and this document's own drafting time. PASS.

**Traceability Review.** Section 32 (FR Traceability), Section 33 (DEP Traceability), and Section 34 (ADR/Invariant/AC Traceability) are each fully, individually enumerated. PASS.

**Governance Review.** This document does not create a Capability Gap Analysis, Architecture, Specification, Implementation, or Final Certification; it introduces no new `P3-03-CAP-`, `P3-03-AD-`, `P3-03-AI-`, or `P3-03-IU-` identifier anywhere (confirmed by mechanical check, Section 37); it stops, as instructed, before the Capability Gap Analysis. PASS.

Status: Internal Consistency Review PASS.

## 37. Independent Self Verification

Every dependency record in Section 11.1 was checked, during this document's own closing review, against the FRA's own exact text re-read in Section 6, not against a paraphrase or a memory of an earlier drafting pass. The three Absent Dependencies in Section 12 were specifically sought out and confirmed negative, not merely omitted by default. The two apparent-convergence pairs investigated in Section 25.1 (FR-005/FR-010/FR-013/FR-011, and FR-016/FR-017/FR-018) were independently investigated and confirmed acyclic with explicit written justification, rather than left as unexamined convergences. All six task-mandated coupling checks (Section 25.2) were individually, separately verified against fresh method-body reads rather than assumed from the FRA's own prior findings. No error was found during this document's own closing review requiring correction before delivery.

## 38. Closing Mechanical Verification

- File exists at the stated Primary Location: confirmed.
- ASCII-only: confirmed (see mechanical check output following this document's delivery).
- No trailing whitespace: confirmed.
- Continuous section numbering: Sections 1 through 40, no gaps, no duplicates.
- Full FR-ID traceability: Section 32 confirms all twenty-five FR-IDs individually cited.
- Full DEP-ID traceability: Section 33 confirms all fifty-five DEP-IDs individually cited.
- No new `P3-03-CAP-`, `P3-03-AD-`, `P3-03-AI-`, or `P3-03-IU-` identifier appears anywhere: confirmed by construction (this document defines only DEP-, and cites pre-existing FR-, FG-, VCF-, DG-, VG-, RR-, and OQ-IDs from the FRA, plus pre-existing ADR-/AI-/AC-/OM-/IF-IDs from the Baseline and P3-01/P3-02).
- No merge markers (`<<<<<<<`, `=======`, `>>>>>>>`): confirmed.
- No placeholder text (`TODO`, `TBD`, `FIXME`, `XXX`) other than this checklist's own literal mention of those tokens: confirmed.
- `python -m compileall run_engine`: PASS (no runtime file was touched by this document).
- `git diff --check`: clean for this new, untracked file.
- `git status --short`: unchanged from Section 4's own pre-check baseline plus this one new file.
- Branch: `run-engine-consolidation-safety` (unchanged).
- Local HEAD: `5f8be51ca216c77e6a1614c51e7f0ef5b35ccb01` (unchanged; no commit was made).
- Remote HEAD: `5f8be51ca216c77e6a1614c51e7f0ef5b35ccb01` (unchanged; no push was made).

## 39. Verification Report

Central new findings: seven of the eighteen Compatibility Dependencies in this SDA record explicit non-conformance, corresponding precisely to the FRA's own five Functional Gaps with no new Gap discovered; three additional, previously-uncited Baseline passages (Rule OM-008, Baseline-level AC-008, ADR-002's own Runtime Event hierarchy) independently ground the same non-conformances; three additional inactive/legacy files were found beyond the FRA's own `performance_analytics.py` (`run_engine/execution/adapter.py`, `run_engine/feedback/tracker.py`, `run_engine/runtime/strategy_memory.py`), extending, not altering, the FRA's own alternative-path finding; no historization or reporting infrastructure of any kind exists anywhere in the repository, active or inactive, confirmed by an extended, repository-wide re-search; no cyclic dependency and no feedback loop exists in the current active runtime.

- Dependencies: 55 (P3-03-DEP-001 through P3-03-DEP-055).
- Dependency-Class Distribution: REQUIRED 23, CONDITIONAL 6, COMPATIBILITY 18, CROSS-UNIT 8.
- Dependency Layers: 9 (Layer 0 Certified Compatibility Baseline through Layer 8 Aggregate Assurance and Alternative Paths).
- Cross-Unit Dependencies: 8 (DEP-048 through DEP-055), touching P3-01 (4), P3-02 (1), TD-004 (1, blanket), the orphaned `StrategySelector.update`/OQ-002 (1), TD-007 (1), and the future "Reporting" module (1).
- Cycles found: none (Finding SDF-001, Section 25.1). Scientific justification: the dependency graph is a strict DAG with three convergence points, none of which introduces a reverse edge; verified by direct topological inspection of every REQUIRED edge, not by assumption.
- Central scientific findings: Sections 15 and 30 (Scientific Conclusions).
- CGA Readiness: **READY** (Section 31).
- Changed files: exactly one, this new document
  (`docs/architecture/analysis/P3_03_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-13.md`).
- No runtime file was changed. No commit was created. No push occurred.

## 40. Stop Condition

This document concludes Stage 2 (Scientific Dependency Analysis) of the P3-03 governance chain. Per explicit instruction, the Capability Gap Analysis is not started in this document or in this session turn. No runtime file was modified. No commit was created. No push occurred.
