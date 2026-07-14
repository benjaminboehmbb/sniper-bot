Document Class:
Capability Gap Analysis

Document ID:
P3-03-CGA

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
docs/architecture/analysis/P3_03_CAPABILITY_GAP_ANALYSIS_V1_2026-07-13.md

Depends On:
- docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md
- docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md
- docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md
- docs/architecture/analysis/P3_03_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-13.md
- docs/architecture/analysis/P3_03_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-13.md
- complete P3-01 governance chain (FRA, SDA, CGA, Architecture, Specification, Final Certification)
- complete P3-02 governance chain (FRA, SDA, CGA, Architecture, Specification, Final Certification)
- docs/architecture/P2_02A_POSITION_OWNERSHIP_ARCHITECTURE_V1_2026-07-10.md
- docs/architecture/P2_03_FINANCIAL_OWNERSHIP_ARCHITECTURE_V1_2026-07-11.md
- docs/architecture/P2_04_RISK_OWNERSHIP_ARCHITECTURE_V1_2026-07-13.md
- current runtime code at HEAD 5f8be51ca216c77e6a1614c51e7f0ef5b35ccb01

Referenced By:
- future P3-03 Architecture

Methodological Structure Reference (content not carried over):
- docs/architecture/analysis/P3_02_CAPABILITY_GAP_ANALYSIS_V1_2026-07-13.md

---

# P3-03 Performance Validation - Capability Gap Analysis

## 1. Document Metadata

See front matter above. This document is the P3-03 Capability Gap Analysis (CGA), the third stage of the P3-03 governance chain (FRA -> SDA -> CGA -> Architecture -> Specification -> Implementation -> Final Certification), following the methodology already established by P2-02A, P2-03, P2-04, P3-01, and P3-02.

## 2. Purpose

This document classifies every capability derivable from the twenty-five Functional Requirements of `P3_03_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-13.md` (the "P3-03 FRA") and the fifty-five Dependency records of `P3_03_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-13.md` (the "P3-03 SDA") as COMPLETE, PARTIAL, or MISSING, and types each as a Runtime, Governance, Documentation, Verification, Cross-Unit, or Residual-Risk Capability. No new capability concept is introduced beyond what the FRA and SDA already establish; no Architecture Decision is made; no Performance keying, formula, or history schema is selected.

## 3. Scope

In scope: capability classification for every FR-001 through FR-025 and every DEP-001 through DEP-055; explicit assessment of the thirty "besonders bewerten" items the governing task names; explicit assessment of every alternative/inactive path; explicit TD-004 and TD-007 readiness assessment.

Out of scope: Performance-keying selection; Performance formula definition; History-schema selection; Reporting-module design; Architecture Decisions; concrete runtime changes; Implementation Units; new Functional Requirements or Dependencies; reopening any already-certified Ownership, Ordering, or Information-Flow decision; reactivation or deletion decisions for any inactive path.

## 4. Binding Baseline

- `docs/architecture/analysis/P3_03_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-13.md` - sole source of the twenty-five Functional Requirements, re-read in full for this document.
- `docs/architecture/analysis/P3_03_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-13.md` - sole source of the fifty-five Dependency records, re-read in full for this document.
- `docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md` - ADR-001 through ADR-012, the Runtime Ownership Matrix, the Target Information Flow, AI-001 through AI-015, AC-001 through AC-015; already fully re-read and cited by the P3-03 SDA, re-confirmed unchanged for this document.
- `docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md`, `docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md` (TD-004, TD-007).
- The complete, certified P2-02A, P2-03, P2-04, P3-01, and P3-02 governance chains - the fixed ground every Compatibility and Cross-Unit capability in this document measures against, not reopened.
- Current runtime code at HEAD `5f8be51ca216c77e6a1614c51e7f0ef5b35ccb01`, independently re-verified in Section 5.

Methodological structure reference only, content not mechanically carried over: `docs/architecture/analysis/P3_02_CAPABILITY_GAP_ANALYSIS_V1_2026-07-13.md`.

## 5. Repository Verification

Independently re-verified for this document, not assumed from the FRA or SDA:

- Branch `run-engine-consolidation-safety`; local HEAD and remote HEAD both `5f8be51ca216c77e6a1614c51e7f0ef5b35ccb01`, identical, no divergence; working tree unchanged since FRA/SDA drafting except for the FRA and SDA files themselves (still untracked, not committed).
- `git status --short -- run_engine/` returns empty: no runtime file has changed since the FRA and SDA were drafted, independently confirming every fresh repository read performed during this session's FRA and SDA remains valid evidence for this document.
- `git diff --stat run_engine/core/performance.py` returns empty: the single most Performance-relevant file is bit-for-bit unchanged since its own last fresh read.
- A supplementary repository-wide search (scoped to `run_engine/`, `__pycache__` excluded) for the CGA's own additionally-required terms not covered by the SDA's own search (`trade_id`, `action`, `feedback`, `reconstruction`, `PARTIAL_CLOSE`, `FULL_CLOSE`) confirmed: `trade_id` is a well-defined field on `LifecycleEvent`/`Trade` (six occurrences in `trade_lifecycle.py`), never read by `PerformanceEngine.update` at all; `"PARTIAL_CLOSE"` occurs as both an `event_type` value (`trade_lifecycle.py`) and a `pnl.py`-recognized closing event; `"FULL_CLOSE"` occurs only as an internal `action` label passed to `_failure_event`'s own failure-reason construction (`trade_lifecycle.py:248`) - the actual `event_type` value for a completed Full Close remains `"TRADE_CLOSED"`, not `"FULL_CLOSE"`, a terminology mapping already implicit in ADR-009's own prose-versus-code naming and not itself a new finding; `reconstruction` and `feedback` (as bare identifiers) produce zero matches in `run_engine/` (the `run_engine/feedback/` directory name is a path component, already accounted for by the SDA's own Section 6 finding regarding `feedback/tracker.py`).
- All ten explicitly-named runtime files (`performance.py`, `loop.py`, `execution/executor.py`, `trade_lifecycle.py`, `position.py`, `pnl.py`, `risk.py`, `canonical_state.py`, `canonical_enforcer.py`, `strategy.py`) and the four explicitly-named alternative/inactive files (`runtime/performance_analytics.py`, `execution/adapter.py`, `feedback/tracker.py`, `runtime/strategy_memory.py`) were freshly, fully read during this session's own FRA and SDA drafting (both completed immediately prior to this document, within the same session) and are confirmed unchanged by the empty `git status --short -- run_engine/` result above; no re-transcription of their full content is repeated here, consistent with the SDA's own established practice of not re-reading files already confirmed unchanged.

No runtime file was modified by this document's own drafting.

## 6. Capability Assessment Method

Each capability is derived directly from one or more Functional Requirements and, where applicable, the Dependency records touching them. Classification follows exactly the governing task's own rules: **COMPLETE** requires runtime behaviour satisfying the requirement, sufficient governance, sufficient evidence, and no open normative gap. **PARTIAL** applies when part of the required capability is present but semantics, governance, historization, verification, or cross-unit boundary definition is incomplete. **MISSING** applies when a required runtime or governance capability does not exist at all, or a normative requirement is demonstrably unmet. A documented Residual Risk alone never justifies a MISSING status. An inactive alternative path is never counted as an existing active capability.

This document introduces no new fachliche capability concept; every capability below is directly traceable to one or more of the twenty-five existing P3-03 FRs and, where applicable, the fifty-five existing P3-03 DEPs. No FRA finding (Functional Gap, Verified Conformant Finding, Documentation Gap, Verification Gap, Residual Risk) is silently reclassified into a different finding category anywhere in this document; each is explicitly carried into its own governing capability under its own original name (Sections 26-30).

## 7. Capability Context

The P3-03 FRA established that the active `PerformanceEngine` accounts for Performance by the tick's own raw decision action, not by completed lifecycle outcomes, directly contradicting all four of ADR-008's own Acceptance Criteria (FG-001 through FG-004) and additionally failing to distinguish Partial Close from Full Close outcomes in its own accounting (FG-005). The P3-03 SDA independently re-grounded these same five findings against three additional Baseline citations the FRA itself did not cite (Rule OM-008, Baseline-level AC-008, ADR-002's own Runtime Event hierarchy), found no new Functional Gap beyond the FRA's own five, and confirmed no cyclic dependency and no feedback loop exists in the current runtime. This CGA's own task is to translate that dependency-level picture into a capability-level COMPLETE/PARTIAL/MISSING classification, cluster it, and assess TD-004's own readiness for architectural resolution - without itself selecting that resolution.

## 8. Capability Clusters

| Cluster | Title | Capabilities |
|---|---|---|
| 1 | Ownership, Publication, and Storage | CAP-001, CAP-002, CAP-003, CAP-004 |
| 2 | Performance Input Semantics (Decision / Execution / Lifecycle Separation) | CAP-005, CAP-007, CAP-008, CAP-009 |
| 3 | Financial Outcome Attribution | CAP-010, CAP-011, CAP-012 |
| 4 | Trade Outcome Recognition | CAP-013 |
| 5 | Failure / HOLD / Rejection | CAP-014, CAP-015 |
| 6 | Performance Aggregation | CAP-016 |
| 7 | Performance History and Reporting | CAP-017, CAP-018 |
| 8 | Determinism and Replay | CAP-019, CAP-020 |
| 9 | Object-Identity and Cross-Tick Stability | CAP-021, CAP-022 |
| 10 | Alternative Paths and Duplicate Authority | CAP-023, CAP-024 |
| 11 | Technical-Debt Synthesis | CAP-006, CAP-025 |
| 12 | Cross-Unit and Documentation/Verification | CAP-026, CAP-027, CAP-028, CAP-029 |

Twelve clusters, adapted from the governing task's own suggested list: CAP-006 (Lifecycle-Outcome-Based Performance Attribution, the aggregate TD-004-core capability) is placed in Cluster 11 alongside its own synthesis sibling CAP-025 (TD-004 Closure Readiness), rather than in Cluster 2, since both are aggregate/synthesis capabilities drawing on Cluster 2-3's own constituent findings rather than an independent primary finding of their own - directly analogous to how the P3-02 CGA placed its own synthesis capability CAP-018 (Hidden Coupling) outside the clusters of its own constituent capabilities.

## 9. Capability Catalogue

Twenty-nine capabilities, `P3-03-CAP-001` through `P3-03-CAP-029`, derived exclusively from the twenty-five existing Functional Requirements and fifty-five existing Dependency records. Two capabilities (CAP-006, CAP-025) are aggregate synthesis capabilities, directly analogous to the P3-02 CGA's own CAP-018; every other capability maps to one primary FR-cluster. No capability introduces a concept absent from the FRA or SDA.

---

**P3-03-CAP-001 - Performance Ownership Structural Compliance**

Capability Type: Governance Capability.

Description: whether the structural split between Computational Authority (`PerformanceEngine`) and Authoritative Owner (`CanonicalState`) for `performance_metrics` conforms to AI-002, AI-003, Rule OM-001, and Rule OM-002 - a narrowly-scoped ownership-structure question, explicitly distinct from whether the accounting methodology itself is correct (CAP-006).

Source FR(s): FR-001, FR-002. Source DEP(s): DEP-001, DEP-002, DEP-021, DEP-030, DEP-031, DEP-054.

Repository Evidence: `performance.py:1` (`class PerformanceEngine`), `canonical_state.py:48,96-98` (`CanonicalState` holds and exposes `performance_metrics`).

Runtime Evidence: exactly one `PerformanceEngine` instance exists per `RunLoop` (`loop.py:26`); `PerformanceEngine` never writes `CanonicalState` directly (Section 5).

Scientific Completeness: high - the ownership split is fully, precisely characterized. Runtime Completeness: complete. Governance Completeness: complete (AI-002, AI-003, OM-001, OM-002 all satisfied by the structural split itself). Documentation Completeness: complete. Verification Completeness: complete (structural, directly re-traceable).

Dependency Coverage: DEP-001, DEP-002, DEP-021, DEP-030, DEP-031 (structural ownership dependencies), DEP-054 (TD-007 absence confirmed within FR-001's own scope).

Certification Coverage: none yet at this unit's own level; the structural pattern itself mirrors every other already-certified canonical value's own ownership split (P2-02A, P2-03, P2-04, P3-02).

Cross-Unit Relevance: none beyond the general Ownership Matrix pattern, not reopened.

Current Status: **COMPLETE**. The ownership-*structure* question (who computes versus who owns) is fully satisfied; this is explicitly and strictly separate from Rule OM-008's own second sentence ("evaluates completed lifecycle outcomes only"), a *methodology* question tracked under CAP-006, not this capability.

Remaining Gap: none at the structural level.

Scope Boundary: does not assess accounting methodology (CAP-006); does not assess publication mechanics (CAP-002).

Architecture Relevance: none required; ratification only.

Specification Relevance: none required.

Traceability: AI-002; AI-003; Rule OM-001; Rule OM-002; Runtime Ownership Matrix; FR-001, FR-002; DEP-001, DEP-002, DEP-021, DEP-030, DEP-031, DEP-054.

---

**P3-03-CAP-002 - Writer-on-Behalf-Of Publication Discipline**

Capability Type: Runtime Capability.

Description: whether `CanonicalEnforcer.apply_performance_metrics` is the sole Writer-on-Behalf-Of for `performance_metrics`, publishing the `PerformanceEngine` snapshot unchanged, with a well-defined `None`-guard behaviour.

Source FR(s): FR-003, FR-017. Source DEP(s): DEP-013, DEP-014, DEP-022, DEP-033, DEP-041.

Repository Evidence: `canonical_enforcer.py:79-85` (`apply_performance_metrics`); `canonical_state.py:96-98` (`update_performance_metrics`).

Runtime Evidence: the active call site (`loop.py:95-96`) always passes the live, non-`None` return value of `performance_engine.update(...)`; the `None`-guard branch is currently unreachable dead code at this call site (FR-025, DEP-022), though structurally correct.

Scientific/Runtime/Governance/Documentation/Verification Completeness: all complete.

Dependency Coverage: DEP-013, DEP-014 (structural realization of CAP-001's own ownership split), DEP-022 (initial-state qualification), DEP-033 (Rule OM-003 conformance), DEP-041 (P3-02-AD-005/IU-002 conformance, not reopened).

Certification Coverage: identical structural pattern to every other already-certified `apply_*` method (P3-01, P3-02).

Cross-Unit Relevance: P3-02-AD-005, IU-002 (re-verified, not reopened).

Current Status: **COMPLETE**.

Remaining Gap: none.

Scope Boundary: does not reopen P3-02's own Structural Independence certification.

Architecture Relevance: none required.

Specification Relevance: none required.

Traceability: Rule OM-003; P3-02-AD-005; P3-02-IU-002; FR-003, FR-017; DEP-013, DEP-014, DEP-022, DEP-033, DEP-041.

---

**P3-03-CAP-003 - Canonical Storage Initialization and Lifetime**

Capability Type: Runtime Capability.

Description: whether `performance_metrics` is correctly initialized to `None` prior to the first tick and correctly stored, without transformation, by `CanonicalState`.

Source FR(s): FR-002, FR-025. Source DEP(s): DEP-001, DEP-013, DEP-022, DEP-030.

Repository Evidence: `canonical_state.py:48` (`"performance_metrics": None`).

Runtime Evidence: the active call site never invokes `apply_performance_metrics(None)` (FR-025, re-confirmed Section 5).

Scientific/Runtime/Governance/Documentation/Verification Completeness: all complete.

Dependency Coverage: DEP-001, DEP-013, DEP-022, DEP-030, all fully accounted for.

Certification Coverage: identical structural pattern to every other canonical value's own initialization.

Cross-Unit Relevance: none.

Current Status: **COMPLETE**.

Remaining Gap: none.

Scope Boundary: does not assess the *content* of the stored value once populated (CAP-005 through CAP-013).

Architecture Relevance: none required.

Specification Relevance: none required.

Traceability: Rule OM-006; FR-002, FR-025; DEP-001, DEP-013, DEP-022, DEP-030.

---

**P3-03-CAP-004 - Unconditional Per-Tick Invocation (Ordering Compliance)**

Capability Type: Runtime Capability.

Description: whether `PerformanceEngine.update` is invoked exactly once per tick, unconditionally, at its own ADR-010-assigned execution stage (step 11, after Financial Accounting and Risk Evaluation, before Tick-Complete Publication).

Source FR(s): FR-004. Source DEP(s): DEP-003, DEP-035, DEP-048.

Repository Evidence: `loop.py:95-96`, the sole call site, unconditional, positioned after `risk = self.risk_engine.check(...)` (`loop.py:92`) and before the `return` statement (`loop.py:98`).

Runtime Evidence: Tick Completion Contract requires "Performance evaluated" among its own six mandatory completion conditions (Baseline, Target Information Flow section); satisfied on every tick.

Scientific/Runtime/Governance/Documentation/Verification Completeness: all complete.

Dependency Coverage: DEP-003 (feeds accounting-key mechanics), DEP-035 (ADR-010/Tick Completion Contract conformance), DEP-048 (P3-01-AD-001/P3-01-DEP-009 re-verification).

Certification Coverage: P3-01 Final Certification, ADR-010's own already-certified 12-stage ordering, not reopened.

Cross-Unit Relevance: P3-01-AD-001, P3-01's own DEP-009 ("Performance Evaluation precedes Tick-Complete Publication").

Current Status: **COMPLETE**.

Remaining Gap: none.

Scope Boundary: does not reopen P3-01's own certified 12-stage ordering.

Architecture Relevance: none required; ratification only.

Specification Relevance: none required.

Traceability: ADR-010; Tick Completion Contract; P3-01-AD-001; P3-01's own DEP-009; FR-004; DEP-003, DEP-035, DEP-048.

---

**P3-03-CAP-005 - Decision-Keyed Performance Attribution (Performance Keying)**

Capability Type: Runtime Capability.

Description: whether `PerformanceEngine`'s own accounting key is derived from a completed lifecycle outcome (per ADR-008, Rule OM-008, and Baseline AC-008) rather than from the tick's own raw Decision.

Source FR(s): FR-005. Source DEP(s): DEP-003, DEP-004, DEP-005, DEP-020, DEP-024, DEP-027, DEP-032, DEP-036, DEP-037, DEP-047, DEP-053.

Repository Evidence: `performance.py:11`, `action = decision.get('action', 'HOLD')` - the accounting key is read directly from the tick's own `decision` dict, produced by `StrategySelector.decide` before `Executor.execute` even runs.

Runtime Evidence: re-confirmed Section 5; no `trade_id`, `event_type`, or any other lifecycle-outcome-derived field participates in the key.

Scientific Completeness: high - the violation is fully, precisely characterized. Runtime Completeness: the current behaviour is stable and well-understood, but does not satisfy the requirement. Governance Completeness: none - Rule OM-008's own second sentence, ADR-008's own Decision text, and Baseline AC-008 are each directly contradicted. Documentation Completeness: complete (FG-004, DEP-047). Verification Completeness: complete (the divergence is 100% reproducible on every tick, requiring no fault injection).

Dependency Coverage: DEP-003 through DEP-005 (internal mechanics), DEP-020 (aggregate read-set), DEP-024/DEP-027 (Conditional, OQ-001/OQ-002), DEP-032/DEP-036/DEP-037/DEP-047 (Compatibility non-conformance), DEP-053 (Cross-Unit, orphaned `StrategySelector.update`).

Certification Coverage: none; this is the FRA's own central, already-registered TD-004 finding (FG-004).

Cross-Unit Relevance: TD-004, P3-03's own primary subject matter.

Current Status: **MISSING**. The requirement - accounting keyed by completed lifecycle outcome, not by raw Decision - does not exist at all in the current runtime; this is not a partial or degraded state of an existing mechanism, it is the complete absence of one.

Remaining Gap: a lifecycle-outcome-derived (or otherwise Decision-independent) accounting key; an Architecture Decision, not selected here.

Scope Boundary: does not select the replacement key (`trade_id`, `event_type`, or another lifecycle-derived dimension); that is reserved for the Architecture stage.

Architecture Relevance: highest priority - this is the single capability every accounting-methodology-dependent capability in Clusters 2-3 (CAP-007, CAP-008, CAP-010, CAP-013, CAP-016) either directly or conditionally depends on.

Specification Relevance: a future Specification cannot define Performance's own Runtime Contract until this capability closes.

Traceability: ADR-008; Rule OM-008; Baseline AC-008; ADR-002 (Event Hierarchy); Functional Gap FG-004; TD-004; FR-005; DEP-003, DEP-004, DEP-005, DEP-020, DEP-024, DEP-027, DEP-032, DEP-036, DEP-037, DEP-047, DEP-053.

---

**P3-03-CAP-006 - Lifecycle-Outcome-Based Performance Attribution (Aggregate, TD-004 Core)**

Capability Type: Runtime Capability (aggregate synthesis).

Description: whether Performance, taken as a whole, is derived exclusively from completed lifecycle events and realized financial outcomes, per ADR-008's own Decision text in full - the single aggregate question the governing task's own "besonders bewerten" item 1 names, synthesizing CAP-005, CAP-007, CAP-008, CAP-009, CAP-010, and CAP-013.

Source FR(s): FR-005, FR-006, FR-007, FR-010, FR-012, FR-013, FR-014 (synthesis across every capability bearing directly on lifecycle-outcome attribution). Source DEP(s): all dependencies feeding CAP-005, CAP-007, CAP-008, CAP-009, CAP-010, CAP-013.

Repository Evidence: consolidated from CAP-005 (MISSING), CAP-007 (MISSING), CAP-008 (MISSING), CAP-009 (PARTIAL), CAP-010 (PARTIAL), CAP-013 (MISSING).

Runtime Evidence: `PerformanceEngine.update`'s own complete method body (`performance.py:6-37`) contains exactly one lifecycle-outcome-aware branch (the `RUNTIME_FAILURE_EVENT` short-circuit); no other `event_type`, no `execution.status`, and no `trade_id` participates in its own accounting.

Scientific Completeness: complete - every sub-finding this synthesis draws on is itself independently, precisely characterized (Sections above). Governance Completeness: none - no unified "Performance derives exclusively from lifecycle outcomes" decision exists anywhere in the runtime. Documentation Completeness: complete (FG-001, FG-002, FG-004, FG-005 jointly and completely describe this gap). Verification Completeness: complete for the negative finding (100% reproducible); no automated regression test exists to detect a future regression toward this same defect (VG-001, CAP-029).

Dependency Coverage: aggregates the full dependency set of CAP-005, CAP-007, CAP-008, CAP-009, CAP-010, CAP-013, plus DEP-052 (blanket TD-004 Cross-Unit relationship).

Certification Coverage: none; this synthesis capability is newly constructed by this document from already-existing sub-findings, introducing no new fact, directly analogous to the P3-02 CGA's own CAP-018 (Hidden Coupling).

Cross-Unit Relevance: this capability *is* TD-004's own scientific description at the capability level.

Current Status: **MISSING**. As a synthesis property ("Performance is derived exclusively from completed lifecycle outcomes"), this is a binary claim, and it is demonstrably false: the accounting key, the trades counter, the wins test, and the running-mean formula are all currently derived from the raw Decision and a bare `pnl` scalar, not from any lifecycle-outcome-specific field.

Remaining Gap: resolution of CAP-005 (keying), CAP-007 (Decision/Outcome separation), CAP-008 (Execution-status visibility), CAP-013 (transition-type awareness), and a corresponding update to CAP-010 (Realized-PnL attribution).

Scope Boundary: does not itself add any new finding beyond what CAP-005, CAP-007, CAP-008, CAP-009, CAP-010, CAP-013 already establish; a synthesis view only.

Architecture Relevance: this synthesis capability's own resolution is entirely a function of its constituent capabilities' own resolutions; no independent Architecture Decision is needed for CAP-006 itself beyond what those constituents already require.

Specification Relevance: none beyond what CAP-005, CAP-007, CAP-008, CAP-009, CAP-010, CAP-013 individually require.

Traceability: ADR-008 (Decision text in full); TD-004; Functional Gaps FG-001, FG-002, FG-004, FG-005; FR-005, FR-006, FR-007, FR-010, FR-012, FR-013, FR-014; all dependencies of CAP-005, CAP-007, CAP-008, CAP-009, CAP-010, CAP-013; DEP-052.

---

**P3-03-CAP-007 - Decision-versus-Outcome Separation**

Capability Type: Runtime Capability.

Description: whether `PerformanceEngine` maintains a structural distinction between a Decision (intention) and a realized Outcome (Execution result, accepted Lifecycle transition, realized Financial consequence), consuming only the latter.

Source FR(s): FR-005, FR-012. Source DEP(s): DEP-011, DEP-027, DEP-036, DEP-047, DEP-053.

Repository Evidence: `performance.py:11`, `decision.get('action', 'HOLD')` is read directly, with no intervening check of `execution.status`, `trade_event.event_type` (beyond the single `RUNTIME_FAILURE_EVENT` test), or any Outcome-confirming field.

Runtime Evidence: the SDA's own Decision-versus-Outcome Analysis (SDA Section 15) directly traced this: a HOLD-cooldown Decision, a validation-failed Execution's own `RUNTIME_FAILURE_EVENT` tick, and a genuine `TRADE_CLOSED` tick are each counted with equal weight whenever they share the same decided `action`.

Scientific Completeness: high - fully characterized. Runtime Completeness: no structural separation exists. Governance Completeness: none. Documentation Completeness: complete (FG-001, FG-004). Verification Completeness: complete (reproducible on demand).

Dependency Coverage: DEP-011 (Execution-blindness enables unconditional increment), DEP-027 (Conditional, OQ-002), DEP-036 (ADR-008 non-conformance), DEP-047 (ADR-002 Event Hierarchy non-conformance), DEP-053 (Cross-Unit, orphaned method).

Certification Coverage: none.

Cross-Unit Relevance: TD-004.

Current Status: **MISSING**. No structural mechanism distinguishes a Decision from a realized Outcome anywhere in `PerformanceEngine.update`'s own method body.

Remaining Gap: an explicit Decision/Outcome distinction in the accounting logic; Architecture-stage scope.

Scope Boundary: does not select the mechanism.

Architecture Relevance: high priority, directly coupled to CAP-005's own resolution.

Specification Relevance: a future Runtime Contract cannot define Performance's own input semantics until this capability closes.

Traceability: ADR-008; ADR-002; SDA Section 15 (Decision-versus-Outcome Analysis); Functional Gaps FG-001, FG-004; FR-005, FR-012; DEP-011, DEP-027, DEP-036, DEP-047, DEP-053.

---

**P3-03-CAP-008 - Execution-Status Visibility**

Capability Type: Runtime Capability.

Description: whether `PerformanceEngine` has any visibility into the Executor's own outcome (`status` in `{BUY_EXECUTED, SELL_EXECUTED, NOOP}`) for the tick it is accounting for.

Source FR(s): FR-012. Source DEP(s): DEP-011, DEP-045, DEP-053.

Repository Evidence: `loop.py:95`, `performance_engine.update(decision, pnl, regime, trade_event)` - `execution` is not among the four passed arguments; confirmed via `run_engine/core/execution/executor.py`'s own full re-read (Section 5).

Runtime Evidence: `execution`'s own `status` field is computed at `loop.py:55` but never referenced again after `trade_lifecycle_engine.on_execution(execution, state)` (`loop.py:57`) consumes it; `PerformanceEngine` has no path to it.

Scientific/Runtime Completeness: the absence is fully, precisely characterized. Governance Completeness: none (Rule OM-008 and ADR-008 both, by requiring outcome-based attribution, implicitly require some visibility into whether an Execution actually occurred). Documentation Completeness: complete (FG-001). Verification Completeness: complete.

Dependency Coverage: DEP-011 (structural consequence, unconditional `trades` increment), DEP-045 (Compatibility with P2-02A/P2-03, conformant in the narrow sense that Performance never touches Position/Financial ownership, though this does not resolve the visibility gap itself), DEP-053 (Cross-Unit, orphaned method).

Certification Coverage: none.

Cross-Unit Relevance: TD-004.

Current Status: **MISSING**. No mechanism exists, active or latent, for `PerformanceEngine` to observe Execution outcome.

Remaining Gap: either pass `execution` into `PerformanceEngine.update`, or route Execution-outcome information through the Lifecycle Event layer instead (an Architecture-stage choice, not made here).

Scope Boundary: does not select the mechanism; does not require `PerformanceEngine` to gain direct Position or Risk visibility (CAP-011, CAP-012 remain separately scoped).

Architecture Relevance: high priority, directly coupled to CAP-005 and CAP-007.

Specification Relevance: a future Runtime Contract for Performance's own input parameters cannot be finalized until this capability closes.

Traceability: ADR-008; Rule OM-008; Functional Gap FG-001; FR-012; DEP-011, DEP-045, DEP-053.

---

**P3-03-CAP-009 - Lifecycle-Event Visibility**

Capability Type: Runtime Capability.

Description: whether `PerformanceEngine` reads a sufficient portion of the `LifecycleEvent` it receives to distinguish the outcomes ADR-008/ADR-009 require distinguished (Open, Scale-In, Partial Close, Full Close, Runtime Failure).

Source FR(s): FR-007. Source DEP(s): DEP-008, DEP-020, DEP-028, DEP-039, DEP-046, DEP-047, DEP-050.

Repository Evidence: `performance.py:8`, `getattr(trade_event, "event_type", None) == "RUNTIME_FAILURE_EVENT"` is the *sole* field access on `trade_event` anywhere in the method body; `LifecycleEvent`'s own remaining ten fields (`trade_id`, `side`, `price`, `tick`, `entry_price`, `prior_quantity`, `execution_quantity`, `resulting_quantity`, `quantity_delta`, `closed_quantity`, `remaining_quantity`, `reason`) are never read.

Runtime Evidence: `trade_event` is a fully-populated, already-available object at the call site (`loop.py:95`), carrying every field `PnLEngine.update` itself already reads (`side`, `price`, `closed_quantity`) to compute realized PnL two lines earlier (`loop.py:72`); the information is present and already used by a sibling engine, simply not read by `PerformanceEngine`.

Scientific Completeness: high. Runtime Completeness: partial - the single most important distinguishing field (`event_type`) *is* read, but only for one of its five possible values. Governance Completeness: none. Documentation Completeness: complete (FG-005). Verification Completeness: complete.

Dependency Coverage: DEP-008 (the sole branch that exists), DEP-020 (aggregate read-set), DEP-028 (Conditional, OQ-001), DEP-039/DEP-050 (Compatibility/Cross-Unit conformance for the one branch that does exist), DEP-046/DEP-047 (Compatibility non-conformance for the branches that do not).

Certification Coverage: none.

Cross-Unit Relevance: TD-004; ADR-009 (Partial Trade Closure and Position Netting, not reopened).

Current Status: **PARTIAL**. One of five relevant `event_type` values is read and correctly acted upon (`RUNTIME_FAILURE_EVENT`); the remaining four (`TRADE_OPENED`, `SCALE_IN`, `PARTIAL_CLOSE`, `TRADE_CLOSED`) are received but never distinguished, and every other `LifecycleEvent` field is entirely unread.

Remaining Gap: read and branch upon the remaining four `event_type` values, and any other `LifecycleEvent` fields an eventual Architecture decision requires (e.g. `trade_id` for per-trade attribution, `closed_quantity` for partial-outcome weighting).

Scope Boundary: does not select which additional fields to read; does not redesign `LifecycleEvent` itself.

Architecture Relevance: high priority, directly coupled to CAP-013.

Specification Relevance: a future Runtime Contract must specify exactly which `LifecycleEvent` fields Performance consumes.

Traceability: ADR-008; ADR-009; Functional Gap FG-005; FR-007; DEP-008, DEP-020, DEP-028, DEP-039, DEP-046, DEP-047, DEP-050.

---

**P3-03-CAP-010 - Realized-PnL Attribution**

Capability Type: Runtime Capability.

Description: whether Realized PnL, once received, is attributed to the correct accounting unit (a completed lifecycle outcome) rather than to a Decision-keyed bucket.

Source FR(s): FR-006, FR-013, FR-014. Source DEP(s): DEP-006, DEP-007, DEP-009, DEP-010, DEP-036, DEP-045.

Repository Evidence: `performance.py:22-27`, the running-mean `pnl` formula is folded into `self.stats[action]`, where `action` is the Decision-derived key (CAP-005), not a lifecycle-outcome-derived one.

Runtime Evidence: the scalar `pnl` itself is correctly sourced from `PnLEngine.update` (`loop.py:72`), a certified P2-03 computation, not reopened; only its own subsequent *attribution* (which bucket receives it) is in question.

Scientific/Runtime Completeness: the PnL value's own correctness is fully intact (inherited from P2-03); its own attribution destination is not conformant. Governance Completeness: none (Baseline AC-008's own second clause, "Win Rate derives exclusively from realized outcomes," is directly contradicted by the attribution mechanism). Documentation Completeness: complete (FG-002). Verification Completeness: complete.

Dependency Coverage: DEP-006, DEP-007 (pnl consumed by wins/mean formulas), DEP-009, DEP-010 (shared `trades` denominator), DEP-036 (ADR-008 non-conformance), DEP-045 (Compatibility with P2-03, conformant for the value itself).

Certification Coverage: P2-03 (Financial Ownership) remains fully compatible and not reopened for the PnL value itself; only its own downstream attribution is at issue, which is P3-03's own scope, not P2-03's.

Cross-Unit Relevance: TD-004; P2-03 (compatible, not reopened).

Current Status: **PARTIAL**. The Realized PnL *value* Performance receives is correct and uncorrupted (inherited, certified); its own *attribution* to an accounting bucket is not conformant with ADR-008/AC-008, since that bucket is Decision-keyed, not Outcome-keyed.

Remaining Gap: re-attribute the same, already-correct `pnl` value to a lifecycle-outcome-derived bucket once CAP-005 resolves.

Scope Boundary: does not reopen P2-03's own certified PnL formula.

Architecture Relevance: high priority, directly downstream of CAP-005.

Specification Relevance: a future Runtime Contract for PnL attribution cannot be finalized until CAP-005 resolves.

Traceability: ADR-005; ADR-008; Baseline AC-008; P2-03; Functional Gap FG-002; FR-006, FR-013, FR-014; DEP-006, DEP-007, DEP-009, DEP-010, DEP-036, DEP-045.

---

**P3-03-CAP-011 - Unrealized-PnL Exclusion Compliance**

Capability Type: Runtime Capability.

Description: whether Performance correctly excludes Unrealized PnL from its own accounting, per ADR-008's own Decision text limiting Performance exclusively to "completed lifecycle events, realized financial outcomes."

Source FR(s): FR-006, FR-023. Source DEP(s): DEP-020, DEP-045.

Repository Evidence: `performance.py`'s own full method body never references Unrealized PnL, `equity`, or `peak_equity` in any form; `PerformanceEngine.update`'s own four parameters (`decision`, `pnl`, `regime`, `trade_event`) contain no Unrealized-PnL-derived value.

Runtime Evidence: `pnl` itself is `PnLEngine.update`'s own *realized*-only return value (nonzero only for `TRADE_CLOSED`/`PARTIAL_CLOSE`, per `pnl.py:23`), never Unrealized PnL.

Scientific/Runtime/Governance/Documentation/Verification Completeness: all complete - this is a correctly-conformant exclusion, not an oversight, distinct in kind from CAP-005 through CAP-010's own non-conformances.

Dependency Coverage: DEP-020 (aggregate read-set, confirming the absence), DEP-045 (Compatibility with P2-02A/P2-03, conformant).

Certification Coverage: consistent with P2-03's own certified Realized-versus-Unrealized PnL separation.

Cross-Unit Relevance: P2-03 (compatible, not reopened).

Current Status: **COMPLETE**. This is a Verified Conformant finding at the capability level: ADR-008 explicitly requires Performance be limited to realized outcomes, and the current runtime already, correctly, never incorporates Unrealized PnL.

Remaining Gap: none.

Scope Boundary: does not extend to Realized-PnL attribution correctness itself (CAP-010).

Architecture Relevance: none required; this exclusion should be explicitly preserved, not revisited, by any future Architecture Decision.

Specification Relevance: a future Runtime Contract should explicitly state this exclusion as a binding constraint, but no new mechanism is required.

Traceability: ADR-008; P2-03; FR-006, FR-023; DEP-020, DEP-045.

---

**P3-03-CAP-012 - Equity and Drawdown Input Boundary**

Capability Type: Runtime Capability, jointly Documentation Capability.

Description: whether Performance's own actual read-set boundary (excluding Equity, Peak Equity, and Drawdown entirely) is consistent with the Target Information Flow's own named Primary Input for `PerformanceEngine` ("Lifecycle History + Financial State").

Source FR(s): FR-023. Source DEP(s): DEP-020, DEP-042.

Repository Evidence: `performance.py`'s own method body never reads `equity`, `peak_equity`, or `drawdown`; the Target Information Flow's own Runtime Stage Responsibilities table names `PerformanceEngine`'s own Primary Input as "Lifecycle History + Financial State" (Baseline), a broader term than the single realized-`pnl` scalar currently consumed.

Runtime Evidence: re-confirmed Section 5; no dependency path exists between `RiskEngine`'s own output and `PerformanceEngine`.

Scientific Completeness: the divergence itself is fully characterized. Runtime Completeness: not applicable in a binary sense - whether Equity/Drawdown *should* be a Performance input is genuinely ambiguous in the Baseline's own text (ADR-008's own Decision text specifically says "realized financial outcomes," which could be read either as exactly the bare realized-PnL scalar already consumed, or as the broader canonical financial state the Target Information Flow's own table names). Governance Completeness: none - this ambiguity is not resolved by any existing document. Documentation Completeness: partial (the ambiguity itself is newly identified and documented here; the Baseline does not resolve it). Verification Completeness: not applicable pending the ambiguity's own resolution.

Dependency Coverage: DEP-020 (aggregate read-set), DEP-042 (Compatibility non-conformance against the Target Information Flow's own broader "Financial State" naming).

Certification Coverage: none.

Cross-Unit Relevance: TD-004.

Current Status: **PARTIAL**. This document does not resolve whether the narrower (realized-PnL-only) or broader (full canonical financial state) reading of ADR-008/the Target Information Flow is correct; it records the ambiguity itself as an open, unresolved boundary question, neither a proven MISSING capability nor a confirmed COMPLETE one.

Remaining Gap: an explicit Architecture-stage clarification of whether "Financial State" as Performance's own named Primary Input requires more than the currently-consumed realized-`pnl` scalar.

Scope Boundary: does not itself resolve the ambiguity; does not select Equity/Drawdown as required inputs.

Architecture Relevance: moderate priority - should be explicitly resolved alongside CAP-005 to avoid a second, uncoordinated read-set change.

Specification Relevance: a future Runtime Contract must state Performance's own complete Financial-State read-set explicitly, once resolved.

Traceability: ADR-008; ADR-006; Target Information Flow (Runtime Stage Responsibilities table); FR-023; DEP-020, DEP-042.

---

**P3-03-CAP-013 - Lifecycle-Transition-Aware Attribution (Trade-Closure Recognition; Open / Scale-In / Partial-Close / Full-Close Semantics)**

Capability Type: Runtime Capability.

Description: whether Performance's own accounting distinguishes a Trade Opened, Scale-In, Partial Close, and Full Close outcome from one another, per ADR-008's own explicit requirement ("Partial Close events SHALL contribute realized performance when realized PnL is generated. Full Close SHALL terminate the lifecycle exactly once.") and ADR-009's own Lifecycle Transition Table.

Source FR(s): FR-007, FR-010. Source DEP(s): DEP-008, DEP-011, DEP-046, DEP-050.

Repository Evidence: `performance.py`'s own method body contains exactly one `event_type` branch (`RUNTIME_FAILURE_EVENT`); `TRADE_OPENED`, `SCALE_IN`, `PARTIAL_CLOSE`, and `TRADE_CLOSED` are never individually distinguished.

Runtime Evidence: `trade_lifecycle.py`'s own `_open_trade`, `_scale_in`, `_partial_close`, `_full_close` methods each generate a distinctly-typed `LifecycleEvent`, fully available at the call site but unread by `PerformanceEngine` (CAP-009).

Scientific Completeness: high. Runtime Completeness: none for this specific distinction. Governance Completeness: none (AC-014, Lifecycle Semantics, is directly contradicted). Documentation Completeness: complete (FG-005). Verification Completeness: complete.

Dependency Coverage: DEP-008 (the sole branch that exists, unrelated to this distinction), DEP-011 (unconditional-increment consequence), DEP-046 (AC-014 non-conformance), DEP-050 (HOLD/Failure mutual-exclusivity, tangential context).

Certification Coverage: none.

Cross-Unit Relevance: TD-004; ADR-009 (not reopened).

Current Status: **MISSING**. No mechanism exists to recognize a completed Trade Closure, or to distinguish it from a Scale-In or an unrelated HOLD tick sharing the same decided action.

Remaining Gap: `event_type`-aware branching for `TRADE_OPENED`, `SCALE_IN`, `PARTIAL_CLOSE`, `TRADE_CLOSED`, coupled to CAP-009's own broader read-set resolution.

Scope Boundary: does not redesign `TradeLifecycleEngine` or `LifecycleEvent`; does not select the specific attribution formula.

Architecture Relevance: high priority, directly coupled to CAP-005, CAP-007, CAP-009.

Specification Relevance: a future Runtime Contract must define exactly how each `event_type` value maps to a Performance contribution.

Traceability: ADR-008; ADR-009 (Lifecycle Transition Table); AC-014; Functional Gap FG-005; FR-007, FR-010; DEP-008, DEP-011, DEP-046, DEP-050.

---

**P3-03-CAP-014 - HOLD Bucket Handling Uniformity**

Capability Type: Runtime Capability.

Description: whether a HOLD-decided tick is processed uniformly, without special-case failure, as an ordinary accounting bucket.

Source FR(s): FR-011. Source DEP(s): DEP-005, DEP-023.

Repository Evidence: `performance.py:11,13-18`, HOLD is treated identically to BUY/SELL as a `self.stats` key.

Runtime Evidence: `strategy.py`'s own `decide` always populates `'action'` explicitly (both return paths), so the `'HOLD'` default fallback is defensive, never triggered, code (re-confirmed Section 5).

Scientific/Runtime/Governance/Documentation/Verification Completeness: all complete for this narrow uniformity property.

Dependency Coverage: DEP-005 (HOLD as a specific instance of the general keying rule), DEP-023 (wins/HOLD-bucket interaction).

Certification Coverage: none required beyond general robustness.

Cross-Unit Relevance: none.

Current Status: **COMPLETE**. Whether HOLD is processed without crashing or requiring special-case logic is fully satisfied; this is explicitly distinct from, and does not imply anything about, whether the underlying keying scheme itself is correct (CAP-005, MISSING).

Remaining Gap: none at this narrow scope.

Scope Boundary: does not assess whether Decision-keying itself (of which HOLD-bucketing is one instance) is correct; see CAP-005.

Architecture Relevance: none required.

Specification Relevance: none required.

Traceability: FR-011; DEP-005, DEP-023.

---

**P3-03-CAP-015 - Failure and Rejection Information Flow Conformance**

Capability Type: Runtime Capability.

Description: whether the `RUNTIME_FAILURE_EVENT` short-circuit correctly performs no accumulator mutation, conforming to ADR-011 and P3-01-AI-012's own explicit naming of "Performance statistics" among the values a rejected transition shall never mutate, and whether HOLD and `RUNTIME_FAILURE_EVENT` remain mutually exclusive as the current runtime constructs them (Failed-Tick Behaviour).

Source FR(s): FR-007, FR-009. Source DEP(s): DEP-008, DEP-028, DEP-039, DEP-049, DEP-050.

Repository Evidence: `performance.py:8-9`, `if ... == "RUNTIME_FAILURE_EVENT": return self._stats_snapshot()` - no mutation of `self.stats` on this path.

Runtime Evidence: `trade_lifecycle.py`'s own `on_execution` returns `None` outright for `action == "HOLD"` (lines 64-65), before any failure-generating branch could apply, confirming HOLD and `RUNTIME_FAILURE_EVENT` are mutually exclusive by construction, not merely by convention.

Scientific/Runtime/Governance/Documentation/Verification Completeness: all complete.

Dependency Coverage: DEP-008 (the mechanism itself), DEP-028 (Conditional, OQ-001 - richer future Lifecycle consumption could add branches), DEP-039 (ADR-011/P3-01-AI-012 conformance), DEP-049 (P3-01-AD-006 re-verification), DEP-050 (P3-01-AD-005 HOLD-completeness re-verification).

Certification Coverage: P3-01-AD-004, P3-01-AD-005, P3-01-AD-006, P3-01-AI-012, not reopened.

Cross-Unit Relevance: P3-01-AD-004, P3-01-AD-005, P3-01-AD-006, P3-01-AI-012.

Current Status: **COMPLETE**. Both the non-mutation property and the Failed-Tick/HOLD mutual-exclusivity property are fully, independently confirmed.

Remaining Gap: none.

Scope Boundary: does not reopen P3-01's own certified Failure/HOLD/Rejection semantics; does not extend the failure-path check to any richer `LifecycleEvent` consumption (CAP-009's own separate, PARTIAL concern).

Architecture Relevance: none required; ratification only.

Specification Relevance: none required.

Traceability: ADR-011; P3-01-AD-004; P3-01-AD-005; P3-01-AD-006; P3-01-AI-012; Verified Conformant Finding VCF-004; FR-007, FR-009; DEP-008, DEP-028, DEP-039, DEP-049, DEP-050.

---

**P3-03-CAP-016 - Performance Aggregation Formula Integrity (Narrow, Mathematical)**

Capability Type: Runtime Capability.

Description: whether the running-mean aggregation formula itself (`pnl` mean, `winrate` mean, `trades` counter) is mathematically well-formed, division-by-zero-free, and internally self-consistent, independent of whether its own inputs represent the correct accounting unit (CAP-005/CAP-006's own separate concern).

Source FR(s): FR-013, FR-014. Source DEP(s): DEP-006, DEP-007, DEP-009, DEP-010, DEP-012.

Repository Evidence: `performance.py:20-32`, `trades` is incremented before being used as a divisor on every path, guaranteeing `trades >= 1` whenever division occurs; no `ZeroDivisionError` path exists.

Runtime Evidence: the running-mean recurrence `(prior_mean * (trades - 1) + sample) / trades` is a standard, numerically well-defined incremental-mean formula.

Scientific/Runtime/Governance/Documentation/Verification Completeness: all complete for this narrow, formula-only property.

Dependency Coverage: DEP-006, DEP-007 (formula inputs), DEP-009, DEP-010 (shared denominator), DEP-012 (lifetime prerequisite for continued formula validity).

Certification Coverage: none required.

Cross-Unit Relevance: none.

Current Status: **COMPLETE**. The formula itself is mathematically sound; this classification makes no claim about, and must not be read as endorsing, the correctness of what the formula's own inputs represent (CAP-005, CAP-006, CAP-010, each separately MISSING or PARTIAL).

Remaining Gap: none at the formula-integrity level.

Scope Boundary: strictly excludes accounting-key correctness (CAP-005), Decision/Outcome separation (CAP-007), and lifecycle-transition awareness (CAP-013); assesses only the arithmetic mechanism.

Architecture Relevance: none required; a future Architecture Decision may reuse this same running-mean mechanism once its own inputs are corrected, or may replace it - either is compatible with this capability's own COMPLETE status, since it concerns only the current formula's own internal soundness.

Specification Relevance: none required for the formula itself; a new Runtime Contract would only be needed if the formula's own shape changes.

Traceability: FR-013, FR-014; DEP-006, DEP-007, DEP-009, DEP-010, DEP-012.

---

**P3-03-CAP-017 - Performance History (Historization)**

Capability Type: Runtime Capability.

Description: whether individual Performance observations (per-tick or per-outcome contributions) are retained in a form that allows published statistics to be reproduced from lifecycle history, per Baseline AC-008's own third clause.

Source FR(s): FR-015. Source DEP(s): DEP-012, DEP-029, DEP-038.

Repository Evidence: `performance.py`'s own `self.stats` retains only the current running mean per action; no per-tick or per-outcome record is kept anywhere.

Runtime Evidence: the SDA's own extended repository-wide search (covering `run_engine/execution/`, `run_engine/feedback/`, `run_engine/logging/`, and `run_engine/runtime/`) confirmed zero historization mechanism exists anywhere in the repository, active or inactive.

Scientific/Runtime Completeness: the absence is fully, repository-wide confirmed. Governance Completeness: none (Baseline AC-008's own third clause, "Performance remains reproducible from lifecycle history," is directly contradicted). Documentation Completeness: complete (FG-003). Verification Completeness: complete.

Dependency Coverage: DEP-012 (lifetime prerequisite), DEP-029 (Conditional, OQ-004/TD-004), DEP-038 (Compatibility non-conformance, Baseline AC-008).

Certification Coverage: none.

Cross-Unit Relevance: TD-004.

Current Status: **MISSING**. No historization mechanism of any kind exists.

Remaining Gap: a history-schema decision (per-tick log, per-outcome log, or derivation from `TradeLifecycleEngine`'s own already-immutable Lifecycle History); explicitly not selected here.

Scope Boundary: does not select a history schema, storage medium, or retention policy.

Architecture Relevance: high priority, though independently schedulable from CAP-005 (a history mechanism could in principle be added without first resolving the accounting key, though the two are naturally coordinated).

Specification Relevance: a future Runtime Contract must define the history schema, once selected.

Traceability: Baseline AC-008; Functional Gap FG-003; TD-004; FR-015; DEP-012, DEP-029, DEP-038.

---

**P3-03-CAP-018 - Reporting Readiness**

Capability Type: Cross-Unit Capability, jointly Documentation Capability.

Description: whether the published `performance_metrics` structure is suitable for eventual consumption by "Reporting," the Runtime Ownership Matrix's own named Primary Consumer, and whether that consumer's own status (future module versus stale documentation) is resolved.

Source FR(s): FR-019, FR-020. Source DEP(s): DEP-016, DEP-017, DEP-025, DEP-034, DEP-055.

Repository Evidence: `performance_metrics`'s own published shape (`{action: {pnl, trades, winrate}}`) is a well-formed, JSON-serializable dict, structurally consumable by any future reader; no module, class, or function named "Reporting" exists anywhere in the repository (FRA Section 8, re-confirmed Section 5).

Runtime Evidence: the sole active reader of `performance_metrics` today is `main.py`'s own `print(result)` (FR-020), an external/terminal consumer, not an internal one.

Scientific Completeness: high. Runtime Completeness: structurally ready (a well-formed, serializable object is published every tick) but semantically not yet trustworthy for genuine reporting, since the underlying accounting itself (CAP-005 through CAP-013) does not yet satisfy ADR-008. Governance Completeness: none - "Reporting"'s own status (future module or stale documentation) is unresolved (DG-001). Documentation Completeness: partial (DG-001 records the ambiguity but does not resolve it). Verification Completeness: not applicable - no actual Reporting consumer exists to verify against.

Dependency Coverage: DEP-016, DEP-017 (publication-channel structure), DEP-025 (Conditional, OQ-003), DEP-034 (Rule OM-004, vacuously conformant), DEP-055 (Cross-Unit, forwarded).

Certification Coverage: none.

Cross-Unit Relevance: a not-yet-built future Reporting module, forwarded, not decided.

Current Status: **PARTIAL**. The publication channel and object shape are structurally ready; the semantic trustworthiness of that published content (given CAP-005/CAP-006's own MISSING status) and "Reporting"'s own very existence are both unresolved.

Remaining Gap: resolve CAP-005/CAP-006 before any genuine Reporting consumer could rely on the published values; separately, clarify whether "Reporting" names a real, planned future module.

Scope Boundary: does not design a Reporting module; does not resolve DG-001's own ambiguity.

Architecture Relevance: low priority for P3-03 itself; primarily a documentation/scope clarification, with the underlying semantic dependency on CAP-005/CAP-006 noted for awareness.

Specification Relevance: none required for P3-03 unless a Reporting module is explicitly brought into scope.

Traceability: Runtime Ownership Matrix ("Reporting" row); Documentation Gap DG-001; FR-019, FR-020; DEP-016, DEP-017, DEP-025, DEP-034, DEP-055.

---

**P3-03-CAP-019 - Replay Compatibility**

Capability Type: Runtime Capability.

Description: whether `PerformanceEngine.update` is a pure function of its own inputs and prior `self.stats` state, free of randomness, wall-clock reads, or I/O, and therefore safe for deterministic replay.

Source FR(s): FR-021. Source DEP(s): DEP-019, DEP-043.

Repository Evidence: `performance.py:6-37`'s own complete method body contains no `random`, `time`, `datetime`, file, or network access of any kind.

Runtime Evidence: re-confirmed Section 5, consistent with the FRA's own Section 17.13 finding.

Scientific/Runtime/Governance/Documentation/Verification Completeness: all complete.

Dependency Coverage: DEP-019 (order-dependence refinement, not a contradiction), DEP-043 (AI-005/AC-012 conformance).

Certification Coverage: consistent with P3-01's own already-certified cross-instance replay evidence, not reopened.

Cross-Unit Relevance: P3-01-AD-007/Contract EO-013 (general replay precedent, not reopened).

Current Status: **COMPLETE**.

Remaining Gap: none.

Scope Boundary: does not re-execute P3-01's own replay verification; does not extend to a future accounting methodology's own determinism, which any Architecture-stage redesign would need to independently preserve.

Architecture Relevance: none required; a future Architecture Decision should explicitly preserve this property, not merely inherit it by accident.

Specification Relevance: none required.

Traceability: AI-005; AC-012; P3-01-AD-007; FR-021; DEP-019, DEP-043.

---

**P3-03-CAP-020 - Deterministic Performance Aggregation**

Capability Type: Runtime Capability.

Description: whether, given an identical sequence of tick inputs applied in the same order, the sequence of published Performance snapshots is functionally identical across replays, with any order-dependence of intermediate snapshots correctly understood as expected behaviour, not nondeterminism.

Source FR(s): FR-021, FR-022. Source DEP(s): DEP-019, DEP-043.

Repository Evidence: identical to CAP-019's own evidence base.

Runtime Evidence: the running-mean formula's own order-dependence (SDA Section 21) reflects that each snapshot publishes the mean *as of that point*, a correct and expected property of any running aggregate, not a violation of determinism, since determinism requires identical-inputs-in-identical-order to produce functionally identical outputs, which holds; it does not require order-independence, which no running aggregate provides or needs to provide.

Scientific/Runtime/Governance/Documentation/Verification Completeness: all complete, including the explicit terminological distinction between order-dependence and nondeterminism.

Dependency Coverage: DEP-019, DEP-043, both fully accounted for.

Certification Coverage: consistent with P3-01's own certified cross-instance determinism findings.

Cross-Unit Relevance: P3-01-AD-007/Contract EO-013.

Current Status: **COMPLETE**. Cross-instance determinism (identical replay of an identical tick sequence in identical order produces functionally identical results) is fully intact; the correctly-expected order-dependence of intermediate snapshots does not reduce this classification.

Remaining Gap: none at the Capability level.

Scope Boundary: does not extend determinism claims to a retry sequence following a Failed Tick; does not evaluate whether a future accounting methodology's own aggregation would preserve this property (a future Architecture/Specification obligation).

Architecture Relevance: none required; ratification and explicit terminological clarification only.

Specification Relevance: none required.

Traceability: AI-005; AI-006; AC-012; FR-021, FR-022; DEP-019, DEP-043.

---

**P3-03-CAP-021 - Producer Isolation (Structural Independence)**

Capability Type: Runtime Capability.

Description: whether `PerformanceEngine.update`'s own returned snapshot is Structurally Independent (no nested object the producer will later mutate is reachable through the returned reference), per the already-certified P3-02-AD-005/IU-002.

Source FR(s): FR-016. Source DEP(s): DEP-018, DEP-041, DEP-051.

Repository Evidence: `performance.py:36-37`, `_stats_snapshot()`, `{action: dict(inner) for action, inner in self.stats.items()}` - a freshly-constructed, one-level-deep copy on every call.

Runtime Evidence: re-confirmed Section 5, unchanged since P3-02's own Implementation and Final Certification.

Scientific/Runtime/Governance/Documentation/Verification Completeness: all complete, already certified.

Dependency Coverage: DEP-018, DEP-041, DEP-051, all fully accounted for.

Certification Coverage: P3-02 Final Certification, CERTIFIED verdict, not reopened.

Cross-Unit Relevance: P3-02-AD-005, IU-002 (re-verified, not reopened).

Current Status: **COMPLETE**.

Remaining Gap: none.

Scope Boundary: does not reopen P3-02's own certification.

Architecture Relevance: none required; a future Architecture Decision must explicitly preserve this property if the accounting methodology changes.

Specification Relevance: none required.

Traceability: P3-02-AD-005; P3-02-IU-002; P3-02 Final Certification; Verified Conformant Finding VCF-001; FR-016; DEP-018, DEP-041, DEP-051.

---

**P3-03-CAP-022 - Cross-Tick Object Stability**

Capability Type: Runtime Capability.

Description: whether `self.stats`'s own cross-tick persistence remains stable, uncorrupted, and free of unintended reset or race condition across the full process lifetime of a single `PerformanceEngine` instance.

Source FR(s): FR-015. Source DEP(s): DEP-012, DEP-029.

Repository Evidence: `performance.py:3-4`, `self.stats = {}` constructed exactly once in `__init__`; no `reset` method exists or is called anywhere in `run_engine/`.

Runtime Evidence: single-threaded, synchronous `RunLoop.step` execution (re-confirmed via `loop.py`'s own full re-read, Section 5) excludes any race condition; `self.stats` is mutated in place consistently across every call.

Scientific/Runtime/Governance/Documentation/Verification Completeness: all complete.

Dependency Coverage: DEP-012 (lifetime prerequisite for the running-mean formula), DEP-029 (Conditional, bounding how long this description remains accurate pending TD-004/OQ-004).

Certification Coverage: none required; a stability property, not previously certified elsewhere since `PerformanceEngine.stats` was not itself the subject of any prior unit's own certification beyond P3-02's own separate aliasing finding (CAP-021, a distinct property).

Cross-Unit Relevance: none.

Current Status: **COMPLETE**. This is explicitly distinct from CAP-017 (Performance History, MISSING): CAP-022 concerns whether the *existing* single running-mean accumulator remains internally stable and uncorrupted, not whether *individual historical observations* are additionally retained.

Remaining Gap: none.

Scope Boundary: does not extend to historization (CAP-017); does not extend to the accumulator's own accounting-key correctness (CAP-005).

Architecture Relevance: none required.

Specification Relevance: none required.

Traceability: FR-015; DEP-012, DEP-029.

---

**P3-03-CAP-023 - Alternative Performance Path Exclusivity (Duplicate Computational Authority Risk)**

Capability Type: Runtime Capability, jointly Documentation Capability.

Description: whether no inactive or dormant Performance-adjacent code path constitutes an active, competing Computational Authority.

Source FR(s): FR-024. Source DEP(s): DEP-021, DEP-024, DEP-026, DEP-029, DEP-044.

Repository Evidence: `run_engine/runtime/performance_analytics.py`, `run_engine/execution/adapter.py`, `run_engine/feedback/tracker.py`, `run_engine/runtime/strategy_memory.py` each confirmed unimported anywhere under `run_engine/core` or `run_engine/main.py` (Section 5, SDA Section 6). Full per-path assessment: Section 25.

Runtime Evidence: an import-closure check re-confirms zero active reference to any of the four files.

Scientific/Runtime Completeness: complete (exclusivity itself). Governance Completeness: complete (no competing production occurs). Documentation Completeness: complete (all four paths now individually named and assessed, Section 25). Verification Completeness: complete (repeatable, mechanical import-closure check).

Dependency Coverage: DEP-021 (the inactive path as evidence for CAP-001/CAP-005's own "sole" claim), DEP-024/DEP-026 (Conditional, OQ-001/OQ-004), DEP-029 (Conditional, OQ-004/TD-004), DEP-044 (AI-013 tension, latent not active).

Certification Coverage: none required; consistent with the already-established inactive status of `run_engine/runtime/` from P3-01/P3-02.

Cross-Unit Relevance: none beyond the general dormant-file disposition question, forwarded to a future Phase 6 Repository Consolidation, consistent with the P3-02 CGA's own precedent (CAP-023).

Current Status: **COMPLETE**. Exclusivity is fully confirmed today; an inactive alternative is correctly not counted as an existing active capability, per the governing task's own explicit classification rule.

Remaining Gap: none at the P3-03 level; the retain/integrate/archive/remove disposition for all four dormant files remains a future Repository Consolidation's own scope, not a P3-03 capability gap.

Scope Boundary: does not classify or dispose of any dormant file; does not decide reactivation or deletion.

Architecture Relevance: none required for exclusivity itself; a future Architecture Decision resolving CAP-005/CAP-006 should explicitly note whether it draws on `performance_analytics.py`'s own `(regime, action)` keying as prior art (DEP-024).

Specification Relevance: none required for P3-03.

Traceability: AI-013; Residual Risk RR-002; FR-024; DEP-021, DEP-024, DEP-026, DEP-029, DEP-044.

---

**P3-03-CAP-024 - Orphaned StrategySelector.update Path**

Capability Type: Residual-Risk Capability.

Description: whether the orphaned `StrategySelector.update(decision, pnl, regime)` method (never called anywhere in the active runtime) represents a bounded, documented, non-blocking condition rather than a silently-accepted one.

Source FR(s): FR-005, FR-012 (shared subject matter). Source DEP(s): DEP-027, DEP-053.

Repository Evidence: `strategy.py:77-93`, a fully-implemented, well-formed method with the identical `(decision, pnl, regime)` input shape as (a subset of) `PerformanceEngine.update`'s own inputs; a repository-wide search for its own call sites (`strategy_selector.update(`, `self.update(decision`) found zero matches anywhere in `run_engine/` (re-confirmed Section 5).

Runtime Evidence: dead code, unreachable from any active execution path; no effect on current runtime behaviour of any kind.

Scientific Completeness: complete - the condition, its exact scope, and its complete inactivity are all precisely characterized. Governance Completeness: complete, per direct analogy to how this same governance chain (P3-01-AD-004, P3-02-CAP-019) has already treated other bounded, documented residual conditions as capability-level COMPLETE rather than MISSING. Documentation Completeness: complete (Residual Risk RR-001). Verification Completeness: complete (the absence of any call site is mechanically, repeatably verifiable).

Dependency Coverage: DEP-027 (Conditional, OQ-002), DEP-053 (Cross-Unit, forwarded).

Certification Coverage: none required; a Residual Risk, not a certified contract.

Cross-Unit Relevance: none beyond the general orphaned-code disposition question, forwarded via OQ-002.

Current Status: **COMPLETE**. A documented Residual Risk alone does not justify a MISSING status, per the governing task's own explicit classification rule; this condition is fully bounded (dead code with zero runtime effect), fully documented (RR-001), and its own eventual disposition is explicitly forwarded (OQ-002), not silently ignored.

Remaining Gap: none at the Capability level; the orphaned method's own eventual disposition (delete, reconcile with a future Performance methodology, or leave dormant) remains an Open Question, not a capability gap.

Scope Boundary: does not decide the method's own disposition; does not reactivate or delete it.

Architecture Relevance: low priority; a future Architecture stage resolving CAP-005/CAP-006 should explicitly note whether this orphaned method is examined alongside `PerformanceEngine`'s own redesign (DEP-027).

Specification Relevance: none required.

Traceability: Residual Risk RR-001; Open Question OQ-002; FR-005, FR-012; DEP-027, DEP-053.

---

**P3-03-CAP-025 - TD-004 Closure Readiness (Aggregate Synthesis)**

Capability Type: Governance Capability (aggregate synthesis).

Description: whether TD-004 ("Lifecycle-based Performance Evaluation") is ready to be closed, given the complete capability picture established above - the single aggregate governance question the governing task's own dedicated "TD-004" section requires.

Source FR(s): FR-005, FR-006, FR-007, FR-010, FR-012, FR-013, FR-014, FR-015, FR-023 (every FR feeding CAP-005 through CAP-013, CAP-017). Source DEP(s): DEP-032, DEP-036, DEP-037, DEP-038, DEP-042, DEP-046, DEP-047, DEP-052.

Repository Evidence: consolidated from CAP-005 (MISSING), CAP-006 (MISSING), CAP-007 (MISSING), CAP-008 (MISSING), CAP-009 (PARTIAL), CAP-010 (PARTIAL), CAP-012 (PARTIAL), CAP-013 (MISSING), CAP-017 (MISSING).

Runtime Evidence: none of the nine constituent capabilities above is fully COMPLETE; seven of nine are open (MISSING or PARTIAL).

Scientific Completeness: complete - this document's own analysis is exhaustive over every FR/DEP TD-004 touches. Governance Completeness: none - no Architecture Decision anywhere resolves TD-004. Documentation Completeness: complete (this document, the FRA, and the SDA jointly and completely document TD-004's own current state). Verification Completeness: complete for the negative finding (TD-004 is definitively not yet closed); VG-001 (CAP-029) separately notes no regression-test exists to detect backsliding once it eventually is.

Dependency Coverage: aggregates the full dependency set of CAP-005 through CAP-013 and CAP-017, plus DEP-052 (blanket TD-004 relationship).

Certification Coverage: none; TD-004 remains open in the Technical Debt Register, Status "Already Planned," Target Phase P3 - this unit's own scope.

Cross-Unit Relevance: this capability *is* the readiness question the Technical Debt Register's own TD-004 entry ultimately resolves against.

Current Status: **MISSING**. TD-004 is not ready to be closed; the majority of its own constituent capabilities remain open.

Remaining Gap: resolution of CAP-005 (keying), CAP-006/CAP-007/CAP-008 (Decision/Outcome separation and Execution visibility), CAP-009/CAP-013 (Lifecycle-Event and transition-type visibility), CAP-010 (re-attribution), CAP-012 (Financial-State boundary clarification), CAP-017 (historization schema) - see Sections 31, 33 for the full readiness breakdown.

Scope Boundary: does not select any resolution mechanism for any constituent capability; a readiness assessment only, per the governing task's own explicit instruction ("Nur Readiness und Capability-Stand bewerten").

Architecture Relevance: this is the single most important synthesis finding for the future P3-03 Architecture stage to act on; see Section 38 (Architecture Readiness Decision) for the full prioritized list.

Specification Relevance: none beyond what the nine constituent capabilities individually require.

Traceability: TD-004 (Technical Debt Register); ADR-008 (Decision text in full); every Functional Gap (FG-001 through FG-005); FR-005, FR-006, FR-007, FR-010, FR-012, FR-013, FR-014, FR-015, FR-023; DEP-032, DEP-036, DEP-037, DEP-038, DEP-042, DEP-046, DEP-047, DEP-052.

---

**P3-03-CAP-026 - TD-007 Boundary Compliance**

Capability Type: Cross-Unit Capability.

Description: whether this unit's own scope correctly excludes TD-007 ("RunLoop Lifecycle Control Surface"), confirmed absent from every P3-03 FR's own subject matter.

Source FR(s): FR-001 (scope-boundary evidence). Source DEP(s): DEP-054.

Repository Evidence: no operator-triggered control-surface transition, pause/resume mechanism, or lifecycle-control API exists anywhere in `run_engine/core` or is referenced by any P3-03 FR.

Runtime Evidence: re-confirmed Section 5; the repository-wide keyword search performed for both the FRA and SDA found no TD-007-adjacent construct.

Scientific/Runtime/Governance/Documentation/Verification Completeness: all complete.

Dependency Coverage: DEP-054, fully accounted for.

Certification Coverage: P3-01-AD-010's own already-certified boundary text ("TD-007 remains a future Runtime Control Unit's"), not reopened.

Cross-Unit Relevance: this capability is, by definition, entirely Cross-Unit.

Current Status: **COMPLETE**.

Remaining Gap: none.

Scope Boundary: this requirement is itself a scope boundary.

Architecture Relevance: none required; a standing constraint on all future P3-03 stages.

Specification Relevance: none required.

Traceability: TD-007 (Technical Debt Register); P3-01-AD-010; FR-001; DEP-054.

---

**P3-03-CAP-027 - P3-01 Cross-Unit Boundary Compliance**

Capability Type: Cross-Unit Capability.

Description: whether this unit refrains from reopening, redeciding, or altering the P3-01-ratified twelve-stage execution ordering, Tick-Complete Publication semantics, Failed-Tick semantics, HOLD semantics, or rejection-non-mutation semantics.

Source FR(s): FR-004, FR-007, FR-009. Source DEP(s): DEP-048, DEP-049, DEP-050.

Repository Evidence: every P3-01-established behaviour re-traced and re-confirmed unchanged across the FRA, SDA, and this document, never redecided.

Runtime Evidence: no runtime file governing P3-01's own scope has been modified by any P3-03 document.

Scientific/Runtime/Governance/Documentation/Verification Completeness: all complete.

Dependency Coverage: DEP-048, DEP-049, DEP-050, fully accounted for.

Certification Coverage: P3-01 Final Certification's own CERTIFIED verdict, not reopened.

Cross-Unit Relevance: this capability is, by definition, entirely Cross-Unit.

Current Status: **COMPLETE**.

Remaining Gap: none.

Scope Boundary: this requirement is itself a scope boundary.

Architecture Relevance: none required; a standing constraint on all future P3-03 stages.

Specification Relevance: none required.

Traceability: P3-01 Final Certification; P3-01-AD-001, AD-004, AD-005, AD-006; P3-01-AI-012; FR-004, FR-007, FR-009; DEP-048, DEP-049, DEP-050.

---

**P3-03-CAP-028 - P3-02 Cross-Unit Boundary Compliance**

Capability Type: Cross-Unit Capability.

Description: whether this unit refrains from reopening P3-02's own certified Composite Isolation (AD-001) and Performance Metrics Structural Independence (AD-005, IU-002) decisions.

Source FR(s): FR-016, FR-017, FR-018. Source DEP(s): DEP-015, DEP-051.

Repository Evidence: `performance.py`'s own `_stats_snapshot()` mechanism, certified under P3-02, re-confirmed unmodified (Section 5).

Runtime Evidence: `canonical_state.py`'s own `get()` method (`.copy()`), certified under P3-02, re-confirmed unmodified.

Scientific/Runtime/Governance/Documentation/Verification Completeness: all complete.

Dependency Coverage: DEP-015 (FR-001, FR-017 -> FR-018, the dual-channel publication this capability re-verifies remains P3-02-compatible), DEP-051, both fully accounted for.

Certification Coverage: P3-02 Final Certification's own CERTIFIED verdict, not reopened.

Cross-Unit Relevance: this capability is, by definition, entirely Cross-Unit.

Current Status: **COMPLETE**.

Remaining Gap: none.

Scope Boundary: this requirement is itself a scope boundary.

Architecture Relevance: none required for exclusivity itself; a future Architecture Decision resolving CAP-005/CAP-006 must explicitly preserve P3-02's own Structural Independence property (CAP-021) as a binding constraint on whatever new accounting mechanism it selects.

Specification Relevance: none required for P3-03 unless the accounting mechanism itself changes, in which case a future Specification must re-affirm Structural Independence explicitly.

Traceability: P3-02 Final Certification; P3-02-AD-001; P3-02-AD-005; P3-02-IU-002; FR-016, FR-017, FR-018; DEP-051.

---

**P3-03-CAP-029 - Verification Coverage**

Capability Type: Verification Capability.

Description: whether `PerformanceEngine`'s own accounting formulas are exercised by a repeatable, independent, automated verification procedure against ADR-008's own Acceptance Criteria.

Source FR(s): FR-005 through FR-014 (the accounting-mechanics cluster, jointly). Source DEP(s): DEP-020 (general read-set aggregation, verification-adjacent context).

Repository Evidence: a repository-wide search for any test file exercising `PerformanceEngine`'s own accounting formulas found none (FRA VG-001, re-confirmed Section 5).

Runtime Evidence: every non-conformance finding in this document (CAP-005, CAP-006, CAP-007, CAP-008, CAP-013, CAP-017) rests on direct source-code reading and manual trace, not on an executed, repeatable test.

Scientific Completeness: the absence itself is fully characterized. Runtime Completeness: not applicable - the underlying behaviour's own correctness or incorrectness is independently established by direct evidence (Sections above), not by this capability's own verification-procedure question. Governance Completeness: none. Documentation Completeness: complete (Verification Gap VG-001). Verification Completeness: none - this capability's own subject matter is precisely the absence of independent verifiability.

Dependency Coverage: DEP-020, the general aggregate read-set dependency, providing the evidentiary basis every manual finding in this document rests on in the continued absence of an automated procedure.

Certification Coverage: none.

Cross-Unit Relevance: none.

Current Status: **PARTIAL**. The underlying runtime behaviour is currently, definitively characterized by direct, reproducible manual inspection (not in question); a repeatable, independent, automated verification procedure exercising that same behaviour does not exist.

Remaining Gap: an automated test suite exercising `PerformanceEngine`'s own accounting formulas, ideally written once the Architecture stage resolves CAP-005/CAP-006, so the tests verify the corrected behaviour rather than needing to be rewritten immediately after passing against the current, non-conformant one.

Scope Boundary: does not itself write or specify the test suite.

Architecture Relevance: low priority for a new decision; primarily a Specification/Implementation-stage verification-procedure question, directly analogous to the P3-02 CGA's own CAP-007/CAP-008 (Producer Isolation/Consumer Read-Only Discipline verifiability).

Specification Relevance: a future IU-level verification procedure could close this once the accounting methodology itself is resolved.

Traceability: Verification Gap VG-001; FR-005 through FR-014; DEP-020.

---

## 10. Capability Matrix

| CAP | Title | Type | Status |
|---|---|---|---|
| CAP-001 | Performance Ownership Structural Compliance | Governance | COMPLETE |
| CAP-002 | Writer-on-Behalf-Of Publication Discipline | Runtime | COMPLETE |
| CAP-003 | Canonical Storage Initialization and Lifetime | Runtime | COMPLETE |
| CAP-004 | Unconditional Per-Tick Invocation (Ordering) | Runtime | COMPLETE |
| CAP-005 | Decision-Keyed Performance Attribution (Keying) | Runtime | MISSING |
| CAP-006 | Lifecycle-Outcome-Based Performance Attribution (Aggregate) | Runtime | MISSING |
| CAP-007 | Decision-versus-Outcome Separation | Runtime | MISSING |
| CAP-008 | Execution-Status Visibility | Runtime | MISSING |
| CAP-009 | Lifecycle-Event Visibility | Runtime | PARTIAL |
| CAP-010 | Realized-PnL Attribution | Runtime | PARTIAL |
| CAP-011 | Unrealized-PnL Exclusion Compliance | Runtime | COMPLETE |
| CAP-012 | Equity and Drawdown Input Boundary | Runtime/Documentation | PARTIAL |
| CAP-013 | Lifecycle-Transition-Aware Attribution | Runtime | MISSING |
| CAP-014 | HOLD Bucket Handling Uniformity | Runtime | COMPLETE |
| CAP-015 | Failure and Rejection Information Flow Conformance | Runtime | COMPLETE |
| CAP-016 | Performance Aggregation Formula Integrity | Runtime | COMPLETE |
| CAP-017 | Performance History (Historization) | Runtime | MISSING |
| CAP-018 | Reporting Readiness | Cross-Unit/Documentation | PARTIAL |
| CAP-019 | Replay Compatibility | Runtime | COMPLETE |
| CAP-020 | Deterministic Performance Aggregation | Runtime | COMPLETE |
| CAP-021 | Producer Isolation (Structural Independence) | Runtime | COMPLETE |
| CAP-022 | Cross-Tick Object Stability | Runtime | COMPLETE |
| CAP-023 | Alternative Performance Path Exclusivity | Runtime/Documentation | COMPLETE |
| CAP-024 | Orphaned StrategySelector.update Path | Residual-Risk | COMPLETE |
| CAP-025 | TD-004 Closure Readiness (Aggregate) | Governance | MISSING |
| CAP-026 | TD-007 Boundary Compliance | Cross-Unit | COMPLETE |
| CAP-027 | P3-01 Cross-Unit Boundary Compliance | Cross-Unit | COMPLETE |
| CAP-028 | P3-02 Cross-Unit Boundary Compliance | Cross-Unit | COMPLETE |
| CAP-029 | Verification Coverage | Verification | PARTIAL |

**Distribution: 17 COMPLETE, 5 PARTIAL, 7 MISSING** (twenty-nine total).

## 11. Runtime Capability Coverage

Twenty-one capabilities are typed (wholly or jointly) Runtime Capability, counting each joint-typed capability once: CAP-002, CAP-003, CAP-004, CAP-005, CAP-006, CAP-007, CAP-008, CAP-009, CAP-010, CAP-011, CAP-012, CAP-013, CAP-014, CAP-015, CAP-016, CAP-017, CAP-019, CAP-020, CAP-021, CAP-022, CAP-023 (CAP-001 is Governance-only; CAP-018 is Cross-Unit-primary; CAP-024 is Residual-Risk-primary; CAP-025 is Governance-primary; CAP-026 through CAP-028 are Cross-Unit-primary; CAP-029 is Verification-primary; none of these eight is counted here). Of these twenty-one, twelve are COMPLETE (CAP-002, CAP-003, CAP-004, CAP-011, CAP-014, CAP-015, CAP-016, CAP-019, CAP-020, CAP-021, CAP-022, CAP-023), three are PARTIAL (CAP-009, CAP-010, CAP-012), and six are MISSING (CAP-005, CAP-006, CAP-007, CAP-008, CAP-013, CAP-017). Runtime Coverage is strong for ownership structure, publication mechanics, failure/HOLD handling, formula integrity, determinism, and object-identity/stability (twelve COMPLETE), and is the weakest dimension specifically for the core accounting-methodology properties ADR-008 governs (six MISSING: keying, the aggregate attribution question, Decision/Outcome separation, Execution-status visibility, transition-type awareness, and historization).

## 12. Governance Capability Coverage

Two capabilities are typed Governance Capability: CAP-001 (COMPLETE - the ownership *structure* split is fully governed) and CAP-025 (MISSING - the aggregate TD-004 closure-readiness question, since no Architecture Decision anywhere resolves the accounting-methodology gap). Governance Coverage is bimodal: the narrow ownership-structure question is fully resolved, while the substantive accounting-methodology question - the actual reason P3-03 exists as its own unit - remains entirely open. This mirrors, in a P3-03-specific form, the P3-02 CGA's own observation that Governance Coverage is frequently the dimension most exposed by a CGA once Runtime topology itself is otherwise sound.

## 13. Documentation Capability Coverage

Three capabilities are typed (wholly or jointly) Documentation Capability: CAP-012 (jointly Runtime/Documentation, PARTIAL), CAP-018 (jointly Cross-Unit/Documentation, PARTIAL), CAP-023 (jointly Runtime/Documentation, COMPLETE). Both FRA Documentation Gaps (DG-001, DG-002) are individually accounted for: DG-001 ("Reporting" unconfirmed) underlies CAP-018's own PARTIAL status; DG-002 (ADR-008 does not define "Completed Lifecycle Outcome" as a concrete schema) underlies CAP-006's own MISSING status as an additional, compounding documentation ambiguity, not a standalone capability of its own. Documentation Coverage is mixed: the *existence* of every dormant file and every named ambiguity is fully documented (satisfying the FRA's own documentation obligation), but two of the three Documentation-typed capabilities remain PARTIAL because the ambiguities themselves are not yet resolved.

## 14. Verification Capability Coverage

One capability is typed Verification Capability: CAP-029, PARTIAL. Its own remaining gap is the absence of a repeatable, independent, automated verification procedure for `PerformanceEngine`'s own accounting formulas, despite the underlying behaviour itself being fully, directly characterized by manual inspection (not in question). This is a narrower Verification Coverage than P3-02's own two-capability (CAP-007/CAP-008) finding, since P3-03's own accounting-methodology gaps are themselves substantive Runtime gaps (CAP-005 through CAP-013), not merely unverified-but-correct behaviour; CAP-029 exists specifically to track the *additional*, separate absence of automated verification, independent of whatever the eventual correct behaviour turns out to be.

## 15. Dependency Capability Coverage

All fifty-five P3-03-DEP records (SDA Section 11.1) are individually accounted for within at least one capability's own Dependency Coverage field above (cross-checked during drafting against the SDA's own Section 32/33 FR/DEP traceability tables). No dependency record is orphaned; every REQUIRED, CONDITIONAL, COMPATIBILITY, and CROSS-UNIT edge the SDA established resolves into exactly one or more capability's own current status. Full DEP-to-CAP traceability is given individually in Section 40.

## 16. Decision-versus-Outcome Assessment

CAP-005 (Decision-Keyed Attribution, MISSING), CAP-007 (Decision-versus-Outcome Separation, MISSING), and CAP-008 (Execution-Status Visibility, MISSING) jointly constitute this document's own Decision-versus-Outcome assessment. The SDA's own Section 15 (Decision-versus-Outcome Analysis) already established, at the dependency level, that a Decision produces no Execution for every HOLD tick, an Execution produces no accepted Lifecycle transition for every validation-failure case, and a tick produces no trade activity at all for HOLD or validation-failure ticks; this CGA confirms, at the capability level, that no structural mechanism in the current runtime exploits any of these three distinctions for Performance accounting purposes. Strict separation is maintained throughout this document between Decision (CAP-005, CAP-007), Execution (CAP-008), Lifecycle Outcome (CAP-009, CAP-013), and Financial Outcome (CAP-010, CAP-011); no section conflates any two of these four concepts.

## 17. Lifecycle and Execution Assessment

CAP-008 (Execution-Status Visibility, MISSING), CAP-009 (Lifecycle-Event Visibility, PARTIAL), and CAP-013 (Lifecycle-Transition-Aware Attribution, MISSING) jointly constitute this assessment. Execution outcome (`status`) is entirely invisible to Performance; Lifecycle outcome (`event_type`) is visible only for its single `RUNTIME_FAILURE_EVENT` value, with `TRADE_OPENED`, `SCALE_IN`, `PARTIAL_CLOSE`, and `TRADE_CLOSED` all currently indistinguishable to `PerformanceEngine`.

## 18. Financial Outcome Assessment

CAP-010 (Realized-PnL Attribution, PARTIAL), CAP-011 (Unrealized-PnL Exclusion Compliance, COMPLETE), and CAP-012 (Equity and Drawdown Input Boundary, PARTIAL) jointly constitute this assessment. The Realized PnL *value* Performance receives is correct (inherited from certified P2-03 computation); its own *attribution destination* is not conformant (CAP-010). Unrealized PnL is correctly, entirely excluded, consistent with ADR-008 (CAP-011). Whether Equity/Drawdown should additionally be Performance inputs remains a genuinely open, Baseline-level ambiguity this document records but does not resolve (CAP-012).

## 19. Aggregation Assessment

CAP-016 (Performance Aggregation Formula Integrity, COMPLETE) confirms the running-mean arithmetic itself is sound, division-by-zero-free, and internally self-consistent; this is explicitly, deliberately kept separate from CAP-005/CAP-006/CAP-010's own accounting-*input* non-conformance, since a mathematically correct formula applied to the wrong accounting unit does not itself constitute a formula defect.

## 20. History Assessment

CAP-017 (Performance History, MISSING) and CAP-022 (Cross-Tick Object Stability, COMPLETE) jointly constitute this assessment, and are explicitly kept distinct: CAP-022 concerns whether the single existing running-mean accumulator remains stable and uncorrupted across ticks (it does); CAP-017 concerns whether individual historical observations are additionally, separately retained (they are not, anywhere in the repository, active or inactive).

## 21. Reporting Assessment

CAP-018 (Reporting Readiness, PARTIAL) confirms the published object shape is structurally consumption-ready but that (a) no actual "Reporting" module exists to validate against, and (b) even if one did, it would currently consume semantically non-conformant data pending CAP-005/CAP-006's own resolution.

## 22. Failure / HOLD / Rejection Assessment

CAP-014 (HOLD Bucket Handling Uniformity, COMPLETE) and CAP-015 (Failure and Rejection Information Flow Conformance, COMPLETE) jointly confirm full conformance: HOLD is processed uniformly without special-case failure; `RUNTIME_FAILURE_EVENT` correctly triggers no accumulator mutation; HOLD and `RUNTIME_FAILURE_EVENT` are mutually exclusive by construction, not by convention.

## 23. Determinism and Replay Assessment

CAP-019 (Replay Compatibility, COMPLETE) and CAP-020 (Deterministic Performance Aggregation, COMPLETE) jointly confirm `PerformanceEngine.update` is a pure function safe for deterministic replay, with the running-mean formula's own order-dependence for intermediate snapshots correctly understood as expected aggregate behaviour, not a violation of determinism.

## 24. Ownership and Publication Assessment

CAP-001 (Performance Ownership Structural Compliance, COMPLETE), CAP-002 (Writer-on-Behalf-Of Publication Discipline, COMPLETE), CAP-003 (Canonical Storage Initialization and Lifetime, COMPLETE), and CAP-021 (Producer Isolation, COMPLETE) jointly confirm the ownership-structure, publication-mechanics, and object-identity dimensions of Performance are all fully conformant; every open gap in this document is confined to the accounting-*methodology* dimension (CAP-005 through CAP-013, CAP-017), never the ownership or publication dimension.

## 25. Alternative-Path Assessment

Per-path assessment, as explicitly required:

| Path | Active/Inactive | Imported? | Semantically Competing? | Own Performance Logic? | Duplicate-Authority Risk | Capability Relevance | Architecture Relevance | Scope Boundary |
|---|---|---|---|---|---|---|---|---|
| `run_engine/runtime/performance_analytics.py` (`PerformanceAnalytics`) | Inactive | No (confirmed, Section 5) | Yes, in principle - computes its own `pnl`/`trades`/`winrate` keyed by `(regime, action)` | Yes - full, independent accounting logic | Latent (AI-013 tension, DEP-044); zero today | CAP-023 (primary), CAP-024/DEP-024 (as potential Architecture-stage prior art) | None decided here; a future Architecture stage may consult its own `(regime, action)` keying as prior art (not a decision made by this document) | No reactivation or deletion decided |
| `run_engine/execution/adapter.py` (`ExecutionAdapter`) | Inactive | No | No - a simpler, non-Performance-accounting Execution stand-in | No - contains no `pnl`/`trades`/`winrate` logic | None - not a Performance Computational Authority candidate | CAP-023 (context only) | None | No reactivation or deletion decided |
| `run_engine/feedback/tracker.py` (`FeedbackTracker`) | Inactive | No | Partially - tracks a `loss_streak` from `decision`/`execution`, adjacent to but distinct from Performance accounting | Partial - a heuristic streak counter, not `pnl`/`trades`/`winrate` | Low - does not compute Performance Metrics itself | CAP-023 (context only) | None | No reactivation or deletion decided |
| `run_engine/runtime/strategy_memory.py` | Inactive | No | No - a Strategy-history memory structure, not a Performance accounting engine | No | None - not a Performance Computational Authority candidate | CAP-023 (context only) | None | No reactivation or deletion decided |
| `StrategySelector.update(decision, pnl, regime)` (orphaned method, active file, inactive method) | Method inactive, file active | Method never called | Adjacent - shares `PerformanceEngine.update`'s own input shape, but mutates `StrategySelector.weights`, not Performance statistics | No - it is a strategy-weight feedback mechanism, not a Performance-statistics mechanism | Low - does not itself compute or publish `performance_metrics` | CAP-024 (primary) | None decided here; forwarded via OQ-002 (DEP-027, DEP-053) | No reactivation or deletion decided |

Only `run_engine/runtime/performance_analytics.py` carries genuine Duplicate-Computational-Authority relevance, since it is the sole one of the five paths that independently computes `pnl`/`trades`/`winrate`-shaped Performance statistics; the remaining four are adjacent (Execution, Feedback, Strategy-memory, or Strategy-weight-feedback) but not themselves competing Performance Computational Authorities. No reactivation, integration, or deletion is decided for any of the five paths by this document.

## 26. Functional-Gap Assessment

**FG-001** (`trades` counts ticks, not completed lifecycle outcomes; traces to FR-005, FR-010, FR-012): classified as Capabilities **CAP-005 (MISSING)**, **CAP-007 (MISSING)**, and **CAP-008 (MISSING)**, jointly synthesized in **CAP-006 (MISSING)**. Confirmed unchanged; no new evidence altered this finding.

**FG-002** (`winrate` diluted by non-realized-outcome ticks; traces to FR-006, FR-013): classified as Capability **CAP-010, PARTIAL**. Confirmed unchanged, independently re-verified in Section 5 of this document.

**FG-003** (no historization, not reproducible from lifecycle history; traces to FR-015, FR-022): classified as Capability **CAP-017, MISSING**. Confirmed unchanged.

**FG-004** (raw Decision directly contributes to Performance statistics; traces to FR-005, FR-011): classified as Capability **CAP-005, MISSING**, and reflected in **CAP-006 (MISSING)** and **CAP-007 (MISSING)**. Confirmed unchanged.

**FG-005** (no Partial Close/Full Close distinction; traces to FR-007, FR-010): classified as Capability **CAP-013, MISSING**, and additionally reflected in **CAP-009's own PARTIAL** classification. Confirmed unchanged.

No Functional Gap is reclassified into a different finding category anywhere in this document, consistent with the governing task's own explicit prohibition.

## 27. Verified-Conformant Assessment

**VCF-001** (Structural Independence of the returned snapshot): underlies Capability **CAP-021, COMPLETE**.

**VCF-002** (Writer-on-Behalf-Of guard-then-write-then-read-back pattern): underlies Capability **CAP-002, COMPLETE**.

**VCF-003** (pure-function determinism, no randomness/wall-clock/I/O): underlies Capabilities **CAP-019 and CAP-020, both COMPLETE**.

**VCF-004** (RUNTIME_FAILURE_EVENT short-circuit performs no accumulator mutation): underlies Capability **CAP-015, COMPLETE**.

## 28. Documentation-Gap Assessment

**DG-001** ("Reporting" named but unconfirmed against any actual module): underlies Capability **CAP-018, PARTIAL**.

**DG-002** (ADR-008 does not define "Completed Lifecycle Outcome" as a concrete schema): underlies Capability **CAP-006's own MISSING** classification as an additional, compounding documentation ambiguity - the absence of a target schema is part of why the current accounting cannot even be evaluated against a fully concrete alternative, though this does not change CAP-006's own classification, since the accounting is demonstrably non-conformant with ADR-008's own prose requirements regardless of schema-level precision.

## 29. Verification-Gap Assessment

**VG-001** (no automated test exercises `PerformanceEngine`'s own accounting formulas against ADR-008): underlies Capability **CAP-029, PARTIAL**. This is the sole Verification Gap the FRA recorded, fully accounted for within this one capability.

## 30. Residual-Risk Assessment

**RR-001** (orphaned `StrategySelector.update` method): underlies Capability **CAP-024, COMPLETE, Residual-Risk Capability**.

**RR-002** (inactive `performance_analytics.py`, latent duplicate-implementation risk): underlies Capability **CAP-023's own explicit documentation**, without reducing CAP-023's own COMPLETE classification, since RR-002 concerns a materially different, currently-inert condition (a possible future wiring-in without reconciliation), not a currently-active violation.

Both Residual Risks are explicitly, individually accounted for; neither is classified MISSING solely for being a Residual Risk, per the governing task's own explicit classification rule.

## 31. TD-004 Capability Assessment

**Which capabilities are missing to close TD-004?** CAP-005 (Decision-Keyed Attribution), CAP-007 (Decision-versus-Outcome Separation), CAP-008 (Execution-Status Visibility), CAP-013 (Lifecycle-Transition-Aware Attribution), CAP-017 (Performance History) are all MISSING; CAP-009 (Lifecycle-Event Visibility), CAP-010 (Realized-PnL Attribution), CAP-012 (Equity/Drawdown Input Boundary) are all PARTIAL.

**Which already exist?** CAP-001 (Ownership structure), CAP-002 (Publication mechanics), CAP-003 (Storage), CAP-004 (Ordering compliance), CAP-011 (Unrealized-PnL exclusion), CAP-014 (HOLD handling), CAP-015 (Failure/Rejection conformance), CAP-016 (Aggregation formula integrity), CAP-019/CAP-020 (Determinism/Replay), CAP-021 (Producer Isolation), CAP-022 (Cross-Tick Object Stability) are all COMPLETE and provide a solid, already-certified structural foundation TD-004's own eventual resolution can build directly on without needing to be re-derived.

**Which dependencies are prerequisite?** Per the SDA's own Dependency Layers (SDA Section 10), CAP-005's own resolution is the Layer-2/3 foundation every accounting-mechanics-layer capability (CAP-007, CAP-008, CAP-009, CAP-010, CAP-013) either directly or conditionally depends on (SDA DEP-003 through DEP-011, DEP-020). CAP-017 (History) is independently schedulable (SDA DEP-012, DEP-029 note it depends on TD-004's own resolution direction but not on CAP-005's own resolution mechanism specifically).

**Is TD-004 fully architecturally solvable within P3-03?** Yes, on the evidence available: every constituent capability's own Source FR(s)/DEP(s) resolve entirely within P3-03's own already-established scope (the twenty-five P3-03 FRs and fifty-five P3-03 DEPs); no constituent capability's own Remaining Gap requires reopening P2-02A, P2-03, P2-04, P3-01, or P3-02's own certified decisions (Section 41). CAP-012's own genuine ambiguity (whether "Financial State" as a named Primary Input requires more than realized PnL) is resolvable by an explicit Architecture-stage interpretive decision, not by a Cross-Unit dependency.

**Which parts require Runtime change?** CAP-005, CAP-007, CAP-008, CAP-009, CAP-013 (accounting key and input read-set), CAP-010 (attribution destination), CAP-017 (a new historization mechanism) - each requires a `performance.py` (and possibly `loop.py` call-site) change once the Architecture stage selects a mechanism.

**Which parts are only Governance, Documentation, or Verification Gaps?** CAP-012 (Equity/Drawdown boundary) is resolvable by an explicit Architecture-stage interpretive clarification, potentially without a Runtime change if the narrower reading is adopted. CAP-018 (Reporting Readiness) is partly a Documentation Gap (DG-001, whether "Reporting" is a real future module) not requiring any Runtime change to resolve at the P3-03 level. CAP-029 (Verification Coverage) is purely a Verification Gap, addressable by a future test suite once the accounting methodology is fixed.

**Are there Cross-Unit prerequisites?** None block TD-004's own resolution: CAP-026, CAP-027, CAP-028 (TD-007, P3-01, P3-02 boundary compliance) are all already COMPLETE, confirming no other unit's own unresolved decision stands between P3-03 and TD-004's own eventual closure.

This document does not close TD-004 and does not select a resolution mechanism, consistent with the governing task's own explicit instruction ("Noch nicht schliessen. Noch keine Loesung auswaehlen. Nur Readiness und Capability-Stand bewerten.").

## 32. Cross-Unit Capability Assessment

Four capabilities are typed (wholly or jointly) Cross-Unit Capability: **CAP-018** (PARTIAL, forwarded future-Reporting relevance), **CAP-026** (COMPLETE, TD-007 boundary), **CAP-027** (COMPLETE, P3-01 boundary), **CAP-028** (COMPLETE, P3-02 boundary). CAP-024, though a Residual-Risk Capability by primary type, carries Cross-Unit-adjacent relevance (OQ-002's own forwarded disposition question) without being primarily typed Cross-Unit, since its own subject matter (`StrategySelector`) is P3-03's own file, not another unit's certified contract. No Cross-Unit Capability requires this document, or a future P3-03 Architecture, to make a decision belonging to P3-01, P3-02, or a future Runtime Control Unit; every one is either a re-verification of an already-settled fact or an explicit, correctly-bounded forwarding.

## 33. Remaining Capability Gaps

Seven capabilities remain MISSING at this document's own closing: **CAP-005** (Decision-Keyed Attribution), **CAP-006** (Lifecycle-Outcome-Based Attribution, aggregate), **CAP-007** (Decision-versus-Outcome Separation), **CAP-008** (Execution-Status Visibility), **CAP-013** (Lifecycle-Transition-Aware Attribution), **CAP-017** (Performance History), **CAP-025** (TD-004 Closure Readiness, aggregate). Five capabilities remain PARTIAL: **CAP-009** (Lifecycle-Event Visibility), **CAP-010** (Realized-PnL Attribution), **CAP-012** (Equity/Drawdown Input Boundary), **CAP-018** (Reporting Readiness), **CAP-029** (Verification Coverage). Every remaining gap traces to a specific, already-identified FRA finding (FG-001 through FG-005, DG-001, DG-002, VG-001); no new gap is introduced by this document.

## 34. Capability Findings

**Finding CF-001.** The seven MISSING capabilities cluster tightly around one root cause: the Decision-keyed, Execution-blind, transition-unaware accounting methodology (CAP-005, CAP-007, CAP-008, CAP-013), with CAP-017 (History) and CAP-025/CAP-006 (aggregate syntheses) as direct downstream or synthesis consequences. No MISSING capability reflects an independent, unrelated defect.

**Finding CF-002.** CAP-017 (History) is independently schedulable from CAP-005 (Keying): a historization mechanism could in principle be added before, after, or alongside a keying-scheme change, since `self.stats`'s own lifetime (CAP-022) is already stable and would not need to change merely to add a parallel history log.

**Finding CF-003.** Every PARTIAL capability's own remaining gap is either (a) a genuine, currently-unresolved interpretive ambiguity in the Baseline itself (CAP-012), (b) a partially-implemented but incomplete input read-set (CAP-009), (c) a correct value with an incorrect attribution destination (CAP-010), (d) a structurally-ready but semantically-unvalidated publication (CAP-018), or (e) the absence of independent verifiability for behaviour that is otherwise fully, directly characterized (CAP-029). None reflects an ambiguous or contested *finding*; every PARTIAL capability's own underlying facts are fully evidenced.

**Finding CF-004.** Ownership, Publication, Object-Identity, Formula-Integrity, Determinism, and Failure/HOLD dimensions (Sections 22-24) are uniformly strong (twelve of twenty-nine capabilities COMPLETE in these dimensions alone); the accounting-methodology dimension ADR-008/TD-004 actually governs is uniformly weak (seven MISSING, three PARTIAL). This is the expected, correctly-identified shape of P3-03's own gap, consistent with the Implementation Baseline's own stated P3-03 objective ("Verify PerformanceEngine inputs. Validate Performance Metrics generation.").

**Finding CF-005.** Governance and Verification Coverage (Sections 12, 14) are, as in P3-02's own CGA, the two weakest dimensions by capability-type; unlike P3-02, this is compounded here by seven MISSING Runtime capabilities as well, since P3-03's own central question is itself substantive (a real accounting-methodology defect), not merely a governance-decision absence layered over otherwise-correct Runtime behaviour.

## 35. Capability Risks

**Risk CR-001.** If CAP-005's own resolution (accounting key) is designed without also resolving CAP-012's own genuine ambiguity (Equity/Drawdown boundary), a second, uncoordinated read-set change could follow shortly after the first. Not a decision; a risk to flag for the Architecture stage's own consideration.

**Risk CR-002.** If CAP-017's own historization mechanism is designed without reconciling `performance_analytics.py`'s own `(regime, action)` keying (CAP-023, DEP-024), a scheme incompatible with useful prior art in the repository could be selected needlessly.

**Risk CR-003.** CAP-029's own continued lack of independent, automated verification means a future regression back toward Decision-keyed accounting, after CAP-005 is eventually fixed, would not be caught by any existing mechanism; this is a Verification Gap risk (VG-001), not evidence that such a regression currently exists.

**Risk CR-004.** CAP-024's own orphaned `StrategySelector.update` method and CAP-005's own eventual resolution share identical input shape (`decision`, `pnl`, `regime`); if the Architecture stage resolves CAP-005 without examining OQ-002, an inconsistency between the corrected `PerformanceEngine` and the still-orphaned `StrategySelector.update` could persist unnoticed, directly restating Dependency Risk DR-003 from the SDA at the capability level.

## 36. Capability Constraints

**Constraint CC-001.** No future P3-03 Architecture may select a Performance-keying scheme, a Performance formula, or a history schema within this document; those selections are explicitly reserved for the Architecture stage (CAP-005, CAP-006, CAP-010, CAP-013, CAP-017).

**Constraint CC-002.** No future P3-03 Architecture may reopen P2-02A, P2-03, P2-04, P3-01, or P3-02's own certified ownership, formula, ordering, or information-flow decisions as a consequence of resolving any capability in this document (CAP-001 through CAP-004, CAP-011, CAP-014, CAP-015, CAP-019 through CAP-022, CAP-026 through CAP-028).

**Constraint CC-003.** Any future Architecture Decision resolving CAP-005 through CAP-013 or CAP-017 must explicitly preserve CAP-021's own already-certified Structural Independence property (P3-02-AD-005/IU-002) for whatever new accounting mechanism it selects.

**Constraint CC-004.** No future P3-03 Architecture may reactivate, integrate, or delete `run_engine/runtime/performance_analytics.py`, `run_engine/execution/adapter.py`, `run_engine/feedback/tracker.py`, `run_engine/runtime/strategy_memory.py`, or reconcile `StrategySelector.update` as a silent side effect of resolving CAP-005/CAP-006; any such action requires its own explicit decision, not an incidental consequence (CAP-023, CAP-024).

## 37. Scientific Conclusions

Twenty-nine capabilities were derived exclusively from the twenty-five existing Functional Requirements and fifty-five existing Dependency records; no new capability concept was introduced. Seventeen are COMPLETE, five are PARTIAL, seven are MISSING. The seven MISSING capabilities cluster around exactly one root cause - the Decision-keyed, Execution-blind, lifecycle-transition-unaware accounting methodology - with two of the seven (CAP-006, CAP-025) being aggregate synthesis capabilities restating the other five's own joint effect, not independent findings of their own. Every already-established structural property (Ownership, Publication, Object-Identity, Formula-Integrity, Determinism, Failure/HOLD conformance, and every Cross-Unit boundary) is fully intact and COMPLETE, providing a stable foundation for the Architecture stage to build the corrected accounting methodology upon. No capability classification in this document rests on speculation; every classification traces to specific, independently re-verified repository evidence (Section 5) or specific FRA/SDA text. No Functional Gap, Verified Conformant Finding, Documentation Gap, Verification Gap, or Residual Risk was silently reclassified into a different finding category.

## 38. Architecture Readiness Decision

Every capability the governing task's own thirty-item "besonders bewerten" list names has been individually assessed (Sections 9, 16-25), directly or as part of a governing synthesis capability (CAP-006 for Lifecycle-Outcome-Based Attribution, CAP-025 for TD-004 Closure Readiness). Every FRA finding (five Functional Gaps, four Verified Conformant Findings, two Documentation Gaps, one Verification Gap, two Residual Risks) is individually accounted for in exactly one capability (Sections 26-30). All fifty-five SDA dependency records are accounted for (Section 15). No new Functional Requirement, Dependency, Architecture Decision, Architecture Invariant, or Implementation Unit was introduced; no runtime file was modified; no Performance keying, formula, or history schema was selected.

**Architecture Readiness: READY**, with the following explicit priorities for the Architecture stage, in the order this document's own findings suggest: (1) **CAP-005** - decide Performance's own accounting key (lifecycle-outcome-derived, not Decision-derived), since it gates CAP-007, CAP-008, CAP-009, CAP-010, CAP-013, and the CAP-006/CAP-025 syntheses; (2) **CAP-008/CAP-009** - decide which additional `execution`/`LifecycleEvent` fields Performance receives, jointly with (1); (3) **CAP-013** - decide the Partial-Close/Full-Close attribution rule, per ADR-008's own explicit Decision-text requirement; (4) **CAP-012** - explicitly clarify whether "Financial State" as Performance's own named Primary Input requires more than the currently-consumed realized-`pnl` scalar; (5) **CAP-017** - decide the History schema, independently schedulable from (1) through (4); (6) **CAP-029** - decide the verification-procedure approach, likely deferred to Specification/Implementation. Every Architecture Decision made under priorities (1) through (5) must explicitly preserve CAP-021's own certified Structural Independence property (Constraint CC-003) and must not incidentally decide CAP-023/CAP-024's own alternative-path or orphaned-method disposition (Constraint CC-004).

## 39. FRA/SDA Traceability

### 39.1 FRA Traceability

| FR | Governing Capability(ies) |
|---|---|
| FR-001 | CAP-001, CAP-026 |
| FR-002 | CAP-001, CAP-003 |
| FR-003 | CAP-002 |
| FR-004 | CAP-004, CAP-027 |
| FR-005 | CAP-005, CAP-006, CAP-007, CAP-014, CAP-024, CAP-025, CAP-029 |
| FR-006 | CAP-006, CAP-010, CAP-011, CAP-025, CAP-029 |
| FR-007 | CAP-006, CAP-009, CAP-013, CAP-015, CAP-025, CAP-027, CAP-029 |
| FR-008 | (no independent capability; folded into CAP-005's own read-set, SDA DEP-020) |
| FR-009 | CAP-015, CAP-025, CAP-027 |
| FR-010 | CAP-006, CAP-013, CAP-025, CAP-029 |
| FR-011 | CAP-014 |
| FR-012 | CAP-006, CAP-007, CAP-008, CAP-024, CAP-025, CAP-029 |
| FR-013 | CAP-010, CAP-014, CAP-016, CAP-029 |
| FR-014 | CAP-010, CAP-016, CAP-029 |
| FR-015 | CAP-017, CAP-022, CAP-025 |
| FR-016 | CAP-021, CAP-028 |
| FR-017 | CAP-002, CAP-028 |
| FR-018 | CAP-028 |
| FR-019 | CAP-018 |
| FR-020 | CAP-018 |
| FR-021 | CAP-019, CAP-020 |
| FR-022 | CAP-019, CAP-020 |
| FR-023 | CAP-011, CAP-012, CAP-025 |
| FR-024 | CAP-023 |
| FR-025 | CAP-002, CAP-003 |

FR-008 (the unused `regime` parameter finding) is fully accounted for within CAP-005's own aggregate read-set evidence (SDA DEP-020) without warranting its own dedicated capability, since an unused parameter is a benign, already-Compatibility-conformant (SDA DEP-040) observation, not an open capability gap in its own right - consistent with the FRA's own Foundational (non-gap-underpinning) classification of FR-008 (FRA Section 26.1). All twenty-five Functional Requirements are traced to at least one capability, directly or via this explicit note for FR-008.

### 39.2 SDA Traceability (Individually Enumerated)

| DEP | Governing Capability(ies) |
|---|---|
| DEP-001 | CAP-001, CAP-003 |
| DEP-002 | CAP-001 |
| DEP-003 | CAP-004, CAP-005 |
| DEP-004 | CAP-005 |
| DEP-005 | CAP-005, CAP-014 |
| DEP-006 | CAP-010, CAP-016 |
| DEP-007 | CAP-010, CAP-016 |
| DEP-008 | CAP-009, CAP-013, CAP-015 |
| DEP-009 | CAP-010, CAP-016 |
| DEP-010 | CAP-010, CAP-016 |
| DEP-011 | CAP-007, CAP-008, CAP-013 |
| DEP-012 | CAP-016, CAP-017, CAP-022 |
| DEP-013 | CAP-002, CAP-003 |
| DEP-014 | CAP-002 |
| DEP-015 | CAP-002 |
| DEP-016 | CAP-018 |
| DEP-017 | CAP-018 |
| DEP-018 | CAP-021 |
| DEP-019 | CAP-019, CAP-020 |
| DEP-020 | CAP-005, CAP-011, CAP-012, CAP-029 |
| DEP-021 | CAP-001, CAP-023 |
| DEP-022 | CAP-002, CAP-003 |
| DEP-023 | CAP-014 |
| DEP-024 | CAP-005, CAP-023 |
| DEP-025 | CAP-018 |
| DEP-026 | CAP-023 |
| DEP-027 | CAP-005, CAP-007, CAP-024 |
| DEP-028 | CAP-009, CAP-015 |
| DEP-029 | CAP-017, CAP-022, CAP-023 |
| DEP-030 | CAP-001 |
| DEP-031 | CAP-001 |
| DEP-032 | CAP-005, CAP-006, CAP-010, CAP-013, CAP-025 |
| DEP-033 | CAP-002 |
| DEP-034 | CAP-018 |
| DEP-035 | CAP-004 |
| DEP-036 | CAP-005, CAP-006, CAP-007, CAP-009, CAP-010, CAP-013, CAP-025 |
| DEP-037 | CAP-005, CAP-010 |
| DEP-038 | CAP-017, CAP-025 |
| DEP-039 | CAP-009, CAP-015 |
| DEP-040 | (no independent capability; folded into FR-008's own note, Section 39.1) |
| DEP-041 | CAP-002, CAP-021 |
| DEP-042 | CAP-012, CAP-025 |
| DEP-043 | CAP-019, CAP-020 |
| DEP-044 | CAP-023 |
| DEP-045 | CAP-008, CAP-010, CAP-011 |
| DEP-046 | CAP-009, CAP-013, CAP-025 |
| DEP-047 | CAP-005, CAP-007, CAP-009, CAP-025 |
| DEP-048 | CAP-004, CAP-027 |
| DEP-049 | CAP-015, CAP-027 |
| DEP-050 | CAP-009, CAP-013, CAP-015, CAP-027 |
| DEP-051 | CAP-021, CAP-028 |
| DEP-052 | CAP-006, CAP-025 |
| DEP-053 | CAP-005, CAP-007, CAP-008, CAP-024 |
| DEP-054 | CAP-001, CAP-026 |
| DEP-055 | CAP-018 |

DEP-040 (compatibility with AI-007/IF-003 for the unused `regime` parameter) is fully accounted for as the dependency-level source of FR-008's own note in Section 39.1, consistent with that same benign, non-gap finding. All fifty-five Dependency records are governed by at least one capability, directly or via this explicit note for DEP-040.

## 40. ADR / Invariant / Acceptance-Criteria Traceability

| Baseline Item | Governing Capability(ies) |
|---|---|
| ADR-001 (SSOT) | CAP-001, CAP-003 |
| ADR-002 (Event-Driven Runtime Evolution) | CAP-005, CAP-007, CAP-009 |
| ADR-005 (PnL Accounting) | CAP-010 |
| ADR-006 (Financial State Ownership) | CAP-012 |
| ADR-008 (Performance Ownership) | CAP-005, CAP-006, CAP-010, CAP-011, CAP-012, CAP-013, CAP-025 |
| ADR-009 (Partial Trade Closure and Netting) | CAP-013 |
| ADR-010 (Deterministic Ordering) | CAP-004 |
| ADR-011 (Runtime Failure Handling) | CAP-015 |
| Runtime Ownership Matrix | CAP-001, CAP-018 |
| Target Information Flow (Runtime Stage Responsibilities table) | CAP-012 |
| Rule OM-001 | CAP-001 |
| Rule OM-002 | CAP-001 |
| Rule OM-003 | CAP-002 |
| Rule OM-004 | CAP-018 |
| Rule OM-008 | CAP-005 |
| Rule / Principle IF-003 | (FR-008 note, Section 39.1) |
| Rule IF-005 | CAP-012 |
| Tick Completion Contract | CAP-004 |
| AI-002 (Unique Ownership) | CAP-001 |
| AI-003 (Separation of Ownership and Computation) | CAP-001 |
| AI-005 (Deterministic Execution) | CAP-019, CAP-020 |
| AI-007 (Semantic Continuity) | (FR-008 note, Section 39.1) |
| AI-012 (Rejection Non-Mutation, P3-01) | CAP-015 |
| AI-013 (Architectural Minimality) | CAP-023 |
| AI-014 (Architectural Traceability) | (general document traceability discipline; no dedicated P3-03 capability, consistent with the FRA's own Foundational classification of the analogous property) |
| AC-008 (Performance Evaluation, Baseline-level) | CAP-005, CAP-010, CAP-017 |
| AC-012 (Deterministic Behaviour) | CAP-019, CAP-020 |
| AC-014 (Lifecycle Semantics) | CAP-013 |
| P3-01-AD-001 | CAP-004, CAP-027 |
| P3-01-AD-004, AD-005, AD-006 | CAP-015, CAP-027 |
| P3-01-AI-012 | CAP-015, CAP-027 |
| P3-01's own DEP-009 | CAP-004 |
| P3-02-AD-001 (Composite Isolation) | CAP-028 (context) |
| P3-02-AD-005, IU-002 (Structural Independence) | CAP-021, CAP-028 |
| P2-02A, P2-03 | CAP-008, CAP-010, CAP-011 |
| TD-004 | CAP-005, CAP-006, CAP-009, CAP-010, CAP-012, CAP-013, CAP-017, CAP-025 |
| TD-007 | CAP-026 |

Every ADR/AI/AC item this document actually relies upon is individually cited above; none is cited only inside a range expression. AI-001, AI-004, AI-006, AI-008, AI-009, AI-010, AI-011, AI-015, and AC-001 through AC-007, AC-009 through AC-011 were each re-confirmed present in the Baseline (SDA Section 5) and re-checked against this document's own actual findings; none carries a Performance-specific dependency this document needs to separately record beyond the general architectural context already established by the items listed above, consistent with the SDA's own identical finding at the dependency level (SDA Section 34).

## 41. Prior-Certification Compatibility

This document does not reopen, and confirms it remains compatible with:

- **P2-02A (Position Ownership)** - not reopened; CAP-008, CAP-011 confirm `PerformanceEngine` never touches Position ownership.
- **P2-03 (Financial Ownership)** - not reopened; CAP-010, CAP-011 confirm `PerformanceEngine` only consumes `PnLEngine`'s own already-published, certified scalar `pnl`.
- **P2-04 (Risk Ownership)** - not reopened; CAP-012 confirms no dependency exists between `PerformanceEngine` and `RiskEngine` output at all, and does not propose creating one.
- **P3-01 (Deterministic Execution Ordering)** - complete governance chain including Final Certification: not reopened; CAP-004, CAP-015, CAP-027 each re-verify, without altering, AD-001, AD-004, AD-005, AD-006, AD-010, and AI-012.
- **P3-02 (Information Flow Validation)** - complete governance chain including Final Certification: not reopened; CAP-002, CAP-021, CAP-028 each re-verify, without altering, AD-001, AD-005, and IU-002.

No capability in this document requires reopening any prior certification to reach its own stated classification.

## 42. Internal Consistency Review

**Scientific Consistency Review.** Every capability's own classification in Section 9 traces to a specific FRA field, a specific SDA dependency, or a specific, independently re-verified repository fact (Section 5); no classification rests on the methodological precedent of P3-01's or P3-02's own CGA distribution alone. PASS.

**Architecture Compatibility Review.** No section of this document selects a Performance-keying scheme, a formula, a history schema, or a Reporting-module design; every such choice is explicitly deferred to the Architecture stage in the relevant capability's own Scope Boundary and Architecture Relevance fields (Section 38's own prioritized list makes this explicit). PASS.

**Capability Consistency Review.** No capability is classified MISSING solely for being a Residual Risk (CAP-023, CAP-024 both confirm this rule was applied); no capability's own classification contradicts another's (CAP-016's own COMPLETE formula-integrity classification is explicitly reconciled with CAP-005/CAP-006's own separate MISSING accounting-input classification, Section 19). PASS.

**Performance Semantics Review.** Section 16 (Decision-versus-Outcome Assessment) strictly separates Decision, Execution, Lifecycle Outcome, and Financial Outcome throughout; no section of this document conflates any two of these four concepts. PASS.

**Lifecycle Dependency Review.** Section 17 and CAP-009/CAP-013/CAP-015 individually confirm every Lifecycle-facing capability's own classification is grounded in direct repository evidence, not assumption, including the HOLD/`RUNTIME_FAILURE_EVENT` mutual-exclusivity re-verification (CAP-015). PASS.

**Financial Dependency Review.** Section 18 confirms the sole Financial dependency (`pnl` from `PnLEngine`, CAP-010) and confirms no Position or Risk dependency exists or is proposed (CAP-012), consistent with fresh repository re-verification. PASS.

**History and Reporting Review.** Section 20 and Section 21 individually confirm CAP-017 (History, MISSING) and CAP-018 (Reporting, PARTIAL) are kept strictly distinct from CAP-022 (Cross-Tick Object Stability, COMPLETE), avoiding any conflation between "the accumulator is stable" and "history/reporting exist." PASS.

**Scope Review.** Section 3 and Section 38 confirm no new FR, DEP, AD, AI, or IU is introduced, and no runtime file is touched; Section 31 confirms TD-004 is explicitly not closed and no resolution is selected. PASS.

**Terminology Review.** "Functionally identical" and "byte-identical" are not used as runtime- or file-comparison claims anywhere in this document (this sentence is the only discussion of either term). "COMPLETE," "PARTIAL," and "MISSING" are applied exactly per Section 6's own restated rules throughout, with explicit justification recorded for every non-obvious classification (CAP-001, CAP-011, CAP-012, CAP-016, CAP-020, CAP-023, CAP-024, CAP-025). "Decision," "Execution," "Lifecycle Outcome," and "Financial Outcome" are used with the strict, distinct meanings the FRA and SDA established throughout. PASS.

**Repository Consistency Review.** Every repository-grounded claim in Section 5 was independently re-verified against the current, unchanged runtime during this document's own drafting, including the supplementary keyword search for the CGA's own additionally-required terms. PASS.

**Runtime Consistency Review.** No runtime file under `run_engine/` was modified; `git status --short -- run_engine/` and `git diff --stat run_engine/core/performance.py` both confirmed empty before and after this document's own drafting. PASS.

**Traceability Review.** Section 39.1 confirms all twenty-five Functional Requirements (with an explicit note for FR-008); Section 39.2 confirms all fifty-five Dependency records (with an explicit note for DEP-040); Section 40 confirms every named ADR/Invariant/Acceptance-Criterion; Section 41 confirms P2-02A/P2-03/P2-04/P3-01/P3-02 compatibility. PASS.

**Governance Review.** This document does not create an Architecture, Specification, Implementation, or Final Certification; it introduces no new `P3-03-AD-`, `P3-03-AI-`, or `P3-03-IU-` identifier anywhere (mechanically confirmed, Section 44); it stops, as instructed, before the Architecture. PASS.

Status: Internal Consistency Review PASS.

## 43. Independent Self Verification

Every one of the twenty-nine capability classifications was checked, during this document's own closing review, against the specific FRA field, SDA dependency, or repository fact it claims to rest on. The seven MISSING and five PARTIAL classifications were each re-examined a second time to confirm the classification rules (Section 6) were applied consistently rather than by pattern-matching to P3-01's or P3-02's own prior distributions. CAP-011 (Unrealized-PnL Exclusion) and CAP-016 (Aggregation Formula Integrity) were specifically re-examined to confirm they were not reflexively classified MISSING merely because they sit adjacent to genuinely MISSING capabilities (CAP-005, CAP-010) - both were independently re-derived from first principles and confirmed correctly COMPLETE on their own, narrowly-scoped terms. CAP-012's own genuine interpretive ambiguity was independently re-examined to confirm it was not resolved either way by this document, consistent with the explicit prohibition on this CGA selecting Performance semantics. The Alternative-Path Assessment (Section 25) was independently re-verified for all five paths via a fresh import-closure check, not merely restated from the SDA's own prior finding. No error was found during this document's own closing review requiring correction before delivery.

## 44. Closing Mechanical Verification

- File exists at the stated Primary Location: confirmed.
- ASCII-only: confirmed (see mechanical check output following this document's delivery).
- No trailing whitespace: confirmed.
- Continuous section numbering: Sections 1 through 46, no gaps, no duplicates.
- Full FR-ID traceability: Section 39.1 confirms all twenty-five FR-IDs individually cited (with an explicit note for FR-008).
- Full DEP-ID traceability: Section 39.2 confirms all fifty-five DEP-IDs individually cited (with an explicit note for DEP-040).
- Full CAP-ID traceability: Section 10 (Capability Matrix) and Sections 39-40 confirm all twenty-nine CAP-IDs individually cited.
- No new `P3-03-AD-`, `P3-03-AI-`, or `P3-03-IU-` identifier appears anywhere: confirmed by construction (this document defines only CAP-IDs, and cites pre-existing FR-, DEP-, FG-, VCF-, DG-, VG-, RR-, and OQ-IDs from the FRA/SDA, plus pre-existing ADR-/AI-/AC-/OM-/IF-IDs from the Baseline and P3-01/P3-02).
- No merge markers (`<<<<<<<`, `=======`, `>>>>>>>`): confirmed.
- No placeholder text (`TODO`, `TBD`, `FIXME`, `XXX`) other than this checklist's own literal mention of those tokens: confirmed.
- `python -m compileall run_engine`: PASS (no runtime file was touched by this document).
- `git diff --check`: clean for this new, untracked file.
- `git status --short`: unchanged from Section 5's own pre-check baseline plus this one new file.
- Branch: `run-engine-consolidation-safety` (unchanged).
- Local HEAD: `5f8be51ca216c77e6a1614c51e7f0ef5b35ccb01` (unchanged; no commit was made).
- Remote HEAD: `5f8be51ca216c77e6a1614c51e7f0ef5b35ccb01` (unchanged; no push was made).

## 45. Verification Report

Central new findings: of twenty-nine capabilities derived exclusively from the twenty-five existing P3-03 Functional Requirements and fifty-five existing P3-03 Dependency records, seventeen are COMPLETE, five are PARTIAL, and seven are MISSING; the seven MISSING capabilities (CAP-005, CAP-006, CAP-007, CAP-008, CAP-013, CAP-017, CAP-025) cluster around exactly one root cause - Decision-keyed, Execution-blind, lifecycle-transition-unaware Performance accounting - while every Ownership, Publication, Object-Identity, Formula-Integrity, Determinism, Failure/HOLD, and Cross-Unit-boundary capability is fully COMPLETE; a previously-unexamined genuine interpretive ambiguity (CAP-012, whether Performance's own named "Financial State" input requires more than the currently-consumed realized-PnL scalar) was newly identified and recorded, unresolved, for the Architecture stage; a full five-path Alternative-Path Assessment (Section 25) confirmed only `performance_analytics.py` carries genuine duplicate-Computational-Authority relevance among the four inactive files and one orphaned method examined.

- Capabilities: 29 (P3-03-CAP-001 through P3-03-CAP-029).
- COMPLETE / PARTIAL / MISSING distribution: 17 COMPLETE, 5 PARTIAL, 7 MISSING.
- Capability Clusters: 12 (Section 8).
- Functional-Gap Classification: FG-001 to Capabilities CAP-005/CAP-007/CAP-008 (synthesis CAP-006); FG-002 to CAP-010; FG-003 to CAP-017; FG-004 to CAP-005 (synthesis CAP-006, CAP-007); FG-005 to CAP-013 (also CAP-009).
- TD-004 Capability Readiness: **not ready to close**; seven constituent capabilities open (five MISSING, two PARTIAL among CAP-009/CAP-010/CAP-012); architecturally fully solvable within P3-03's own already-established scope, no Cross-Unit prerequisite blocks it (Section 31).
- Cross-Unit Capabilities: 4 (CAP-018 PARTIAL; CAP-026, CAP-027, CAP-028 all COMPLETE).
- Alternative-Path Assessment: 5 paths individually assessed (Section 25); only `performance_analytics.py` carries genuine duplicate-authority relevance; no reactivation or deletion decided for any path.
- Architecture Readiness: **READY** (Section 38), with a six-item prioritized list for the Architecture stage.
- Changed files: exactly one, this new document
  (`docs/architecture/analysis/P3_03_CAPABILITY_GAP_ANALYSIS_V1_2026-07-13.md`).
- No runtime file was changed. No commit was created. No push occurred.

## 46. Stop Condition

This document concludes Stage 3 (Capability Gap Analysis) of the P3-03 governance chain. Per explicit instruction, the P3-03 Architecture is not started in this document or in this session turn. No runtime file was modified. No commit was created. No push occurred.
