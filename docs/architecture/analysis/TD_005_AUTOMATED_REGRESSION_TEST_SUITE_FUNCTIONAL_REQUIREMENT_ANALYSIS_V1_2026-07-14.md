Document Class:
Functional Requirement Analysis

Document ID:
TD005-FRA

Title:
TD-005 Automated Regression Test Suite - Functional Requirement Analysis

Version:
V1.1

Date:
2026-07-14

Status:
DRAFT - EDITORIAL AND SCIENTIFIC REVIEW COMPLETED

Storage Location:
docs/architecture/analysis/

Filename:
TD_005_AUTOMATED_REGRESSION_TEST_SUITE_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-14.md

Technical Debt Item:
TD-005 - Automated Regression Test Suite (docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md)

Scope:
Functional requirements only. No dependency analysis, capability gap analysis, architecture decision, specification, or implementation content.

Dependencies:
- docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md
- docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md
- docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md
- docs/architecture/REPOSITORY_CONSOLIDATION_ARCHITECTURE_V1_2026-07-14.md
- docs/architecture/REPOSITORY_CONSOLIDATION_SPECIFICATION_V1_2026-07-14.md
- docs/architecture/certification/REPOSITORY_CONSOLIDATION_FINAL_CERTIFICATION_V1_2026-07-14.md
- docs/architecture/certification/P3_01_FINAL_CERTIFICATION_V1_2026-07-13.md
- docs/architecture/certification/P3_02_FINAL_CERTIFICATION_V1_2026-07-13.md
- docs/architecture/certification/P3_03_FINAL_CERTIFICATION_V1_2026-07-13.md

Referenced By:
- future TD-005 Scientific Dependency Analysis (not yet created)

Supersedes:
None. This is a revision of the same document (V1.0 to V1.1); no separate prior document is superseded.

Language:
English

Encoding:
ASCII

---

# TD-005 Automated Regression Test Suite - Functional Requirement Analysis

## 1. Metadata Header

See front matter above.

## 2. Document Control

This document is a Functional Requirement Analysis (FRA). It derives functional requirements only. It does not perform Scientific Dependency Analysis, Capability Gap Analysis, Architecture, or Specification work, and it does not implement, design, or select a test framework, test fixture, or CI configuration. No architecture or implementation decision is made anywhere in this document. All findings are grounded in repository evidence independently inspected on 2026-07-14 against branch run-engine-consolidation-safety.

### 2.1 Revision History

- **V1.0 (2026-07-14).** Initial Functional Requirement Analysis. Twenty-eight Functional Requirements across thirteen capability domains.
- **V1.1 (2026-07-14).** Editorial and Scientific Review. Reclassified four requirements (non-interference, no-alternative-runtime-path, repository-scope compatibility, deterministic test environment) from Functional Requirements to individually numbered Constraints (TD005-CON-001 through TD005-CON-004). Removed the coverage-completeness requirement and the Executor-namespace-uniqueness requirement from the Functional Requirement list and relocated their full normative meaning into a new Section 13, Deferred Specification and Coverage Obligations. Abstracted all remaining Functional Requirements to implementation-neutral functional verification objectives, removing concrete test-design language (execute-twice, byte comparison, event counting, table-driven checks, import-closure scans, and similar). Added TD005-FR-020 (Behavioural Equivalence as the Basis of Regression) and TD005-FR-021 (Certified-Contract Boundary for Regression Evaluation) as new, central Functional Requirements. Consolidated two pairs of closely related requirements for atomicity (Tick-Complete Publication Uniqueness with No Partial-State Observation; Rejected-Transition Non-Mutation with Runtime Failure Event Generation). Replaced the thirteen-domain model with six scientifically coherent capability domains. Renumbered all Functional Requirements continuously (TD005-FR-001 through TD005-FR-022). Rebuilt the Requirement Traceability section in full. Revised OQ-001 to avoid implying a prematurely selected invocation boundary and added OQ-006 (Scientific Definition of Regression Equivalence). Revised FRA Completion Criteria accordingly. No repository evidence was weakened or removed; only classification, numbering, and abstraction level were revised.

## 3. Executive Summary

TD-005 ("Automated Regression Test Suite," Register status Open, Priority Medium, Target Phase Project-wide, Source P1-03.1 Final Certification Finding 6) requires an automated regression test suite for run_engine/core. Independent repository inspection confirms that no such suite currently exists: the tests/ directory contains no test files at all (only an empty, untracked tests/ssi/ subdirectory unrelated to run_engine), no test framework appears in requirements.txt, and no file in the tracked repository imports pytest or unittest. Every one of the six certified governance units (P2-02A, P2-03, P2-04, P3-01, P3-02, P3-03) and the Repository Consolidation unit instead relied on hand-authored, one-off verification scripts created during each unit's own Implementation and Final Certification stages, none of which persists as a reusable, repeatable regression capability. The Implementation Baseline's own methodology already mandates a "Regression Validation" layer for every implementation phase ("Regression failures shall be treated as implementation failures"), but this layer has been executed manually throughout the P1-P3 chain, not automatically.

This revised (V1.1) document derives twenty-two individually numbered Functional Requirements (TD005-FR-001 through TD005-FR-022) across six capability domains, four individually numbered Constraints (TD005-CON-001 through TD005-CON-004), and two clearly identified Deferred Specification and Coverage Obligations, grounded in the two Baselines, the six certified units, and direct inspection of the fourteen currently-active run_engine modules. This revision strengthens scientific level separation: Functional Requirements now state only what capability is required; boundary conditions on the capability's own behavior are stated as Constraints; premature coverage and repository-integrity obligations are deferred explicitly rather than folded into Functional Requirements; and every remaining Functional Requirement's own verification intent is stated as an implementation-neutral functional verification objective rather than a concrete test design.

## 4. Analysis Objective

To determine, from repository evidence alone, what a future automated regression capability for the active Run Engine must functionally achieve, without selecting how it achieves it and without prescribing how its own achievement will be tested. This document defines the problem, the current-state evidence, the functional capability boundaries, the individually-numbered functional requirements, the individually-numbered constraints on the capability's own behavior, and the deferred obligations needed to close TD-005. It does not decide which test framework, directory layout, or CI mechanism will be used, and it does not decide the exact algorithm by which behavioural regression will be determined.

## 5. Scope

In scope: functional requirements for automated regression verification of the fourteen currently-active run_engine modules (Section 6.3) and their certified behavioral contracts (deterministic ordering, canonical publication, lifecycle integrity, financial integrity, risk evaluation, performance evaluation, executor behavior, failure handling), as established by the Architecture Baseline's ADRs and Acceptance Criteria and by the P2-02A/P2-03/P2-04/P3-01/P3-02/P3-03/Repository-Consolidation certified units; the boundary conditions (Constraints, Section 12) the future capability's own behavior must respect; and the obligations (Section 13) whose full functional definition is deferred to a future Specification stage rather than resolved here.

Out of scope (Section 15, Non-Goals): performance optimization, production monitoring, live-trading validation, long-duration scientific validation itself, strategy-quality assessment, market-data validation unrelated to Run Engine behavior, Run Engine architecture redesign, unrelated technical debt, CI/CD design, test framework selection, and any implementation detail, including the exact algorithm used to determine behavioural equivalence (Section 11, TD005-FR-020). This document also does not perform SDA, CGA, Architecture, or Specification work, and does not modify any file other than itself.

## 6. Authoritative Repository Evidence

### 6.1 TD-005 Register Definition (Verified)

Read directly from docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md:

- Title: Automated Regression Test Suite
- Priority: Medium
- Target Phase: Project-wide
- Status: Open
- Source: P1-03.1 Final Certification - Finding 6
- Description: "Create an automated regression test suite for run_engine/core."

### 6.2 Verified Absence of Existing Automated Test Infrastructure

- `tests/` exists as a directory but contains, in its entirety, one empty, untracked subdirectory `tests/ssi/` with zero files (verified via `find tests -type f`, zero results; `git ls-files tests/`, zero results). Nothing under `tests/` references `run_engine`.
- `requirements.txt` (12 lines, verified in full) lists only `certifi`, `charset-normalizer`, `idna`, `numpy`, `pandas`, `python-dateutil`, `pytz`, `PyYAML`, `requests`, `six`, `tzdata`, `urllib3`. No test framework (pytest, unittest extensions, hypothesis, coverage) is present.
- A repository-wide search (`git grep`) for `import pytest`, `import unittest`, `from pytest`, `from unittest` across all tracked `.py` files returns zero matches.
- `README.md` (8 lines, verified in full) contains no testing, build, or CI instructions of any kind.
- No `pytest.ini`, `setup.cfg`, `pyproject.toml`, or `tox.ini` exists at the repository root.

### 6.3 Verified Active Run Engine Module Set (Corrected From the Governing Task's Own List)

An independent AST-based import closure from `run_engine.main`, freshly re-run for this document, confirms exactly fourteen active modules (the `run_engine/` tree now contains 18 `.py` files total, 14 active, 4 inactive, following Repository Consolidation):

1. run_engine/main.py
2. run_engine/core/loop.py
3. run_engine/core/state.py
4. run_engine/core/regime.py
5. run_engine/core/strategy.py
6. run_engine/core/position.py
7. run_engine/core/risk.py
8. run_engine/core/execution/__init__.py
9. run_engine/core/execution/executor.py
10. run_engine/core/performance.py
11. run_engine/core/pnl.py
12. run_engine/core/trade_lifecycle.py
13. run_engine/core/canonical_state.py
14. run_engine/core/canonical_enforcer.py

An originally-provided file list named `run_engine/execution/__init__.py` and `run_engine/execution/executor.py` (without `core/`). Independent verification found these two paths do not exist in the current repository. The correct, currently active paths are `run_engine/core/execution/__init__.py` and `run_engine/core/execution/executor.py`, confirmed present and confirmed part of the active closure above. This is a direct consequence of the Repository Consolidation Final Certification's own RC-AD-004 path-collision resolution (the top-level `run_engine/execution/executor.py` was archived to `archive/REPOSITORY_CONSOLIDATION_2026-07-14/run_engine/execution/executor.py` and is no longer part of the active tree). This correction is itself repository evidence supporting the Deferred Repository-Integrity Regression Obligation (Section 13.2).

Four additional tracked `run_engine/` files exist but are confirmed inactive (unreached by the import closure): `run_engine/core/config.py`, `run_engine/runtime/recovery.py`, `run_engine/runtime/snapshot.py`, `run_engine/runtime/state_memory.py`. These are RETAIN-Deferred-Scope components under ADR-012 (Repository Consolidation Architecture RC-AD-005) and are explicitly out of this FRA's own scope, since they hold no active Computational Authority.

### 6.4 Verified Architecture Baseline Obligations

Read directly from docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md:

- ADR-010 (Deterministic Runtime Execution Ordering): the runtime SHALL execute a fixed twelve-stage sequence per tick (Runtime Tick Acquisition, State Acquisition and Normalization, Regime Classification, Strategy Selection, Execution Decision Generation, Executor Event Generation, TradeLifecycle Update, Position Update, Financial Accounting, Risk Evaluation, Performance Evaluation, Tick-Complete CanonicalState Publication); no component may observe partially updated state; Tick-Complete CanonicalState publication occurs exactly once per tick.
- AC-001 through AC-015 (Scientific Acceptance Criteria) define, among others: Canonical Runtime Ownership (AC-001), Unique Information Ownership (AC-002), Lifecycle Integrity (AC-004), Financial Integrity (AC-005), Risk Evaluation determinism and non-ownership (AC-007), Performance Evaluation gated on completed lifecycle outcomes (AC-008), Tick Completion uniqueness (AC-009), Information Flow non-reconstruction (AC-010), Deterministic Behaviour (AC-012), Lifecycle Semantics distinctness of Scale-In/Partial-Close/Full-Close (AC-014), and Runtime Failure Handling (AC-015).
- A full-text search of this Baseline for "test" or "regression" (case-insensitive) returns zero matches - the Architecture Baseline itself defines no testing methodology; testing is addressed only in the separate Implementation Baseline (Section 6.5).

### 6.5 Verified Implementation Baseline Regression Validation Layer

Read directly from docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md: "Validation Layer 4: Regression Validation" is explicitly defined with Purpose "Verify that previously validated functionality remains correct," Validation Activities "Existing functionality verification, Runtime regression tests, Historical replay comparison, Output consistency verification," and the explicit statement "Regression failures shall be treated as implementation failures." This validation layer is listed as a required exit-criterion component for every implementation phase (Phase 1 through Phase 6) and for overall Scientific Implementation Certification. The Long Duration Validation sequence is fixed as: Functional smoke validation, 1-hour validation, 6-hour validation, 24-hour validation, 7-day validation, 30-day validation, with "every validation stage shall complete successfully before the next duration is attempted," and "successful 30-day runtime validation is the mandatory minimum requirement for Final Scientific Certification."

### 6.6 Verified Repository Consolidation Evidence

The Repository Consolidation Architecture (RC-AD-019, Section 29) and Final Certification (Section 27, Finding RC-FG-003) both independently confirm: TD-005 remains Open and is not silently closed by Repository Consolidation; a new governance-tooling script, `tools/repository_consolidation/verify_repository_consolidation.py`, now exists and provides a reproducible, deterministic, directly-executable check, but its own scope is repository-structure verification (active/inactive module set, namespace collisions, archive non-importability, tracked generated artifacts) - not runtime behavioral regression of run_engine/core, and it is explicitly not CI-integrated. The Repository Consolidation Final Certification's own Section 27 states verbatim: "no CI pipeline invokes this tool automatically... TD-005 (Automated Regression Test Suite) remains, correctly and by design, Status: Open." This confirms TD-005's own subject matter (behavioral regression of run_engine/core) is materially distinct from, and unaddressed by, the repository-structure tool Repository Consolidation produced.

### 6.7 Verified Certified-Unit Manual Verification Precedent

The P3-01, P3-02, and P3-03 Final Certifications (all verdict CERTIFIED, verified directly) each independently constructed hand-authored Python verification scripts during their own Implementation and Certification stages (e.g., import-closure re-derivations, blob comparisons, deterministic replay checks, fault-injection probes) to establish their own CERTIFIED verdicts. None of these scripts is checked into the repository as a persistent, reusable asset; each was created ad hoc for its own governance stage and is not independently re-invocable today. This is direct, repeated repository-history evidence of the operational cost TD-005 exists to eliminate.

### 6.8 Verified Determinism Baseline of the Active Module Set

Direct inspection of all fourteen active files (Section 6.3) for `import random`, `from random`, `import time` used for control flow, or `datetime.now()` calls: zero matches. This confirms the active Run Engine currently contains no non-deterministic input source, which is itself a necessary precondition for TD005-FR-002 and TD005-CON-004 (Section 11, Section 12) to be achievable in principle. Direct inspection of `run_engine/core/trade_lifecycle.py` confirms the lifecycle event vocabulary is exactly `TRADE_OPENED`, `SCALE_IN`, `PARTIAL_CLOSE`, `TRADE_CLOSED`, `RUNTIME_FAILURE_EVENT`. Direct inspection of `run_engine/core/canonical_state.py` confirms exactly twelve `update_*` methods (tick, position, equity, peak_equity, pnl, realized_pnl_cumulative, risk, regime, strategy_selection, execution_decision, performance_metrics, runtime_status), each the sole write path for its own field. Direct inspection of `run_engine/core/performance.py` confirms `REALIZED_EVENT_TYPES = {"PARTIAL_CLOSE", "TRADE_CLOSED"}` gates every statistics update, keyed by Position Side. Direct inspection of `run_engine/core/position.py` confirms Position Side is constrained to the set `{"LONG", "SHORT"}`.

## 7. Current-State Assessment

No automated regression capability exists for run_engine/core today (Section 6.2). Validation of every certified behavioral contract to date has depended on manually-authored, non-reusable verification scripts created anew for each governance unit (Section 6.7). The Implementation Baseline's own methodology already requires a "Regression Validation" layer for every phase and treats regression failures as implementation failures (Section 6.5), but this requirement has been satisfied manually, not automatically, throughout the P1-P3 governance chain. The Repository Consolidation unit's own new tooling (Section 6.6) addresses a materially different concern (repository structure) and explicitly does not close TD-005. The active module set is small (14 files), fully deterministic by direct inspection (Section 6.8), and each module's own certified behavioral contract is precisely documented in the Architecture Baseline and in the six certified units - meaning the necessary behavioral specification already exists in governance documentation; what is verifiably absent is an automated, repeatable mechanism to check the active runtime against it.

## 8. Problem Definition

The current absence of an automated regression capability for run_engine/core means every one of the fourteen active modules' own certified behavioral guarantees (Section 6.4, Section 6.8) can only be re-verified by manually re-authoring a verification script, as has occurred independently at least four times already in this repository's own history (P3-01, P3-02, P3-03, Repository Consolidation, Section 6.7). This creates the following verified, evidence-grounded risks:

- **Undetected behavioral regression.** A future change to any active module could silently violate a certified Acceptance Criterion (AC-001 through AC-015) or Architecture Decision (ADR-001 through ADR-012) without any automatic signal, since no persistent check exists to run against it.
- **Undetected ordering regression.** ADR-010's own twelve-stage sequence has no automated guard; a future refactor of `run_engine/core/loop.py` could silently reorder stages without triggering any failure.
- **Undetected lifecycle or state-isolation regression.** AC-004 (Lifecycle Integrity), AC-006 (Canonical Runtime State), and AC-014 (Lifecycle Semantics) have no automated guard against a future violation (for example, a Partial Close that terminates the lifecycle, or a canonical field written by more than one component).
- **Undetected performance-semantics regression.** The P3-03-certified gating of `PerformanceEngine` on `REALIZED_EVENT_TYPES` (Section 6.8) has no automated guard; a future change could silently revert to decision-tick-based evaluation, the exact defect TD-004 already closed once.
- **Undetected information-flow regression.** AC-010 (no downstream reconstruction of upstream semantic information) has no automated guard.
- **Operational cost of manual re-verification.** Each governance unit's own Implementation and Final Certification stage has independently re-derived overlapping verification logic (import closures, blob comparisons, determinism checks) from scratch, at a real, repeated authoring cost, rather than reusing a shared, persistent capability.
- **TD-005 as a precondition for Long-Duration Validation.** The Implementation Baseline's own mandatory Long Duration Validation sequence (Functional smoke through 30-day, Section 6.5) requires "every validation stage shall complete successfully before the next duration is attempted." Without an automated regression capability, each of the six stages would require the same manual, ad hoc re-verification effort already shown to be costly and non-reusable (Section 6.7), for a sequence that by its own design repeats over increasingly long durations - making automation not merely convenient but a precondition for the sequence to be practically executable at all before committing capital-adjacent runtime to a 30-day unattended validation window.

## 9. Stakeholders and Functional Consumers

Identified strictly from roles already evidenced in this repository's own governance documents; no organizational role is invented:

- **Maintainers** who modify `run_engine/core` and need to know, before committing, whether a change violates a certified behavioral contract.
- **Reviewers** (the "Independent Review Policy" named in the Architecture Baseline: Codex, Claude, ChatGPT) who need a reproducible, evidence-based signal distinct from manual re-reading of source code.
- **Implementation agents** executing a future Implementation Unit, who need a regression gate consistent with the Implementation Baseline's own "Regression Validation" layer (Section 6.5).
- **Certification activities** (Final Certification stages, as performed for P3-01/P3-02/P3-03/Repository Consolidation) that currently re-author bespoke verification scripts each time (Section 6.7) and would benefit from a reusable baseline to build upon.
- **Long-Duration Validation stages** (Section 6.5), which require a pre-validated, repeatable regression pass before each of the six mandatory durations.
- **Repository governance** itself (the FRA/SDA/CGA/Architecture/Specification/Implementation/Certification sequence this document is itself part of), which requires TD-005's own eventual closure to be evidence-based, consistent with every prior TD closure in this repository (TD-004, Section 6.6).

## 10. Functional Capability Domains

Six domains, each grounded in Section 6's own evidence, used to organize the Functional Requirements in Section 11. Every remaining Functional Requirement maps to exactly one primary domain; no domain exists solely to hold a single requirement.

- **D1 - Deterministic Runtime Behaviour.** Execution ordering and repeated-run determinism (2 requirements).
- **D2 - Canonical State and Information Integrity.** Tick-Complete publication, canonical ownership, snapshot isolation, information-flow validity (4 requirements).
- **D3 - Lifecycle and Financial Behaviour.** Position lifecycle transitions, Partial/Full Close/Scale-In semantics, realized and unrealized financial consistency (6 requirements).
- **D4 - Risk, Performance, and Execution Behaviour.** Risk evaluation, performance-evaluation gating and aggregation, executor behavior, failure handling (5 requirements).
- **D5 - Regression Detection and Evidence.** Cross-unit regression detection, behavioural equivalence, certified-contract boundary (3 requirements).
- **D6 - Validation Integration and Governance.** Reproducible failure reporting, Long-Duration-Validation precondition support (2 requirements).

## 11. Functional Requirements

**TD005-FR-001. Deterministic Execution Ordering Verification.**
Requirement: The capability SHALL verify, for tested runtime ticks, that `run_engine.core.loop.RunLoop.step()` executes its constituent stages in the exact order established by ADR-010 (Runtime Tick Acquisition, State Acquisition and Normalization, Regime Classification, Strategy Selection, Execution Decision Generation, Executor Event Generation, TradeLifecycle Update, Position Update, Financial Accounting, Risk Evaluation, Performance Evaluation, Tick-Complete CanonicalState Publication).
Rationale: ADR-010 is a binding Architecture Decision with no existing automated guard (Section 8).
Source: Architecture Baseline ADR-010 (Section 6.4).
Functional verification objective: Demonstrate that the certified execution stage order is preserved for representative runtime ticks.
Domain: D1.

**TD005-FR-002. Repeated-Run Determinism.**
Requirement: The capability SHALL verify that equivalent runtime input sequences produce identical behavioural output across repeated execution of the active RunLoop.
Rationale: AC-012 (Deterministic Behaviour) requires identical inputs to always produce identical outputs; this is only actually verified, not merely assumed, by an automated repeated-execution comparison.
Source: Architecture Baseline AC-012 (Section 6.4); Section 6.8's own confirmation of zero non-determinism sources in the active module set.
Functional verification objective: Demonstrate that equivalent runtime inputs preserve identical behavioural output across repeated execution.
Domain: D1.

**TD005-FR-003. Tick-Complete Publication Integrity.**
Requirement: The capability SHALL verify that exactly one Tick-Complete CanonicalState Snapshot is published per runtime tick and that no consumer of `RunLoop.step()`'s own return value observes a CanonicalState that is not Tick-Complete.
Rationale: AC-009 (Tick Completion) and ADR-010 jointly require exactly-once publication with no observation of intermediate runtime state; both are facets of the same publication-integrity property and are consolidated here for atomicity.
Source: Architecture Baseline AC-009, ADR-010 (Section 6.4).
Functional verification objective: Demonstrate that Tick-Complete publication occurs exactly once per tick and that no partially-updated runtime state is observable prior to that publication.
Domain: D2.

**TD005-FR-004. Canonical Ownership Non-Duplication.**
Requirement: The capability SHALL verify that each of the twelve canonical fields (tick, position, equity, peak_equity, pnl, realized_pnl_cumulative, risk, regime, strategy_selection, execution_decision, performance_metrics, runtime_status) is written by exactly one component per tick, via its own single `CanonicalState.update_*` method.
Rationale: AC-001 (Canonical Runtime Ownership) and AC-002 (Unique Information Ownership) require single-writer discipline; Section 6.8 confirms the current twelve-method structure this requirement targets.
Source: Architecture Baseline AC-001, AC-002 (Section 6.4); direct inspection of `run_engine/core/canonical_state.py` (Section 6.8).
Functional verification objective: Demonstrate that each canonical runtime field is written by exactly one component, consistent with its certified Authoritative Owner.
Domain: D2.

**TD005-FR-005. Snapshot Isolation.**
Requirement: The capability SHALL verify that a Tick-Complete Snapshot returned for one tick does not share mutable state with a snapshot returned for a different tick, such that mutating one could observably affect the other.
Rationale: AC-006 (Canonical Runtime State) requires exactly one authoritative representation; snapshot aliasing would silently violate this even if the write-ownership rules (TD005-FR-004) are otherwise satisfied.
Source: Architecture Baseline AC-006 (Section 6.4); analytical derivation (no direct Baseline text names "aliasing," but the Single-Source-of-Truth principle and Canonical Working State/Tick-Complete Snapshot distinction in the Baseline's own Ownership Terminology section directly imply this property).
Functional verification objective: Demonstrate that snapshots representing different ticks remain independently observable without cross-tick interference.
Domain: D2.

**TD005-FR-006. Information Flow Non-Reconstruction.**
Requirement: The capability SHALL verify that no downstream stage of `RunLoop.step()` recomputes semantic information already produced by an upstream stage in the same tick.
Rationale: AC-010 (Information Flow) requires semantic continuity without redundant reconstruction.
Source: Architecture Baseline AC-010 (Section 6.4).
Functional verification objective: Demonstrate that semantic information is computed exactly once per tick and is not redundantly reconstructed downstream.
Domain: D2.

**TD005-FR-007. Position Lifecycle State Machine Integrity.**
Requirement: The capability SHALL verify that Position transitions (FLAT to LONG or SHORT, quantity increase via Scale-In, quantity decrease via Partial Close, return to FLAT via Full Close) occur only in response to a corresponding TradeLifecycleEngine event and never independently.
Rationale: AC-004 (Lifecycle Integrity) requires TradeLifecycleEngine to exclusively own lifecycle history, from which Position state is derived.
Source: Architecture Baseline AC-004 (Section 6.4); direct inspection of `run_engine/core/trade_lifecycle.py` and `run_engine/core/position.py` event/side vocabulary (Section 6.8).
Functional verification objective: Demonstrate that Position state changes only as a consequence of a corresponding certified lifecycle event.
Domain: D3.

**TD005-FR-008. Partial Close Realized PnL Without Termination.**
Requirement: The capability SHALL verify that a PARTIAL_CLOSE lifecycle event generates realized PnL while the associated trade's own lifecycle record remains open (not TRADE_CLOSED).
Rationale: AC-014 (Lifecycle Semantics) explicitly requires Partial Close to generate realized PnL without terminating the lifecycle.
Source: Architecture Baseline AC-014 (Section 6.4); direct inspection of `run_engine/core/trade_lifecycle.py`'s own `PARTIAL_CLOSE` event_type (Section 6.8).
Functional verification objective: Demonstrate that a Partial Close transition realizes PnL while the associated lifecycle remains open.
Domain: D3.

**TD005-FR-009. Full Close Terminates Lifecycle Exactly Once.**
Requirement: The capability SHALL verify that a TRADE_CLOSED lifecycle event terminates its associated trade record exactly once and that no subsequent event mutates that same trade record.
Rationale: AC-014 requires Full Close to terminate the lifecycle exactly once; AC-004 requires completed lifecycle records to be immutable.
Source: Architecture Baseline AC-004, AC-014 (Section 6.4); direct inspection of `run_engine/core/trade_lifecycle.py`'s own `TRADE_CLOSED` event_type (Section 6.8).
Functional verification objective: Demonstrate that a Full Close transition terminates its lifecycle exactly once and that the resulting record remains immutable thereafter.
Domain: D3.

**TD005-FR-010. Scale-In Quantity Accumulation Integrity.**
Requirement: The capability SHALL verify that a SCALE_IN lifecycle event correctly accumulates position quantity while preserving the certified entry-price and side attribution rules already established for the affected trade.
Rationale: AC-014 requires Scale-In to remain a semantically distinct, correctly-defined lifecycle transition, kept individually atomic from Partial Close and Full Close (TD005-FR-008, TD005-FR-009) because AC-014 itself requires all three to remain semantically distinct.
Source: Architecture Baseline AC-014 (Section 6.4); direct inspection of `run_engine/core/trade_lifecycle.py`'s own `SCALE_IN` event_type (Section 6.8).
Functional verification objective: Demonstrate that a Scale-In transition correctly accumulates quantity while preserving certified entry-price and side attribution.
Domain: D3.

**TD005-FR-011. Realized PnL Computation Reproducibility.**
Requirement: The capability SHALL verify that PnLEngine's own realized PnL computation, given a fixed lifecycle event history, is reproducible.
Rationale: AC-005 (Financial Integrity) requires financial state to remain reproducible from immutable lifecycle history.
Source: Architecture Baseline AC-005 (Section 6.4).
Functional verification objective: Demonstrate that realized PnL remains reproducible from a fixed lifecycle history.
Domain: D3.

**TD005-FR-012. Unrealized PnL, Equity, and Drawdown Internal Consistency.**
Requirement: The capability SHALL verify that unrealized PnL, equity, peak equity, and drawdown values remain internally consistent with each other at every tick.
Rationale: AC-005 (Financial Integrity) and AC-006 (Canonical Runtime State) jointly require these values to form one internally consistent financial picture; kept distinct from TD005-FR-011 because reproducibility and cross-field consistency are separate verifiable properties.
Source: Architecture Baseline AC-005, AC-006 (Section 6.4).
Functional verification objective: Demonstrate that unrealized PnL, equity, peak equity, and drawdown remain internally consistent at each tick.
Domain: D3.

**TD005-FR-013. Risk Evaluation Determinism and Non-Ownership.**
Requirement: The capability SHALL verify that RiskEngine consumes only Canonical Working State at its own assigned execution stage, produces deterministic risk metrics for a given input, and does not itself become the Authoritative Owner of any canonical field it reads.
Rationale: AC-007 (Risk Evaluation) requires exactly this consumption discipline and determinism.
Source: Architecture Baseline AC-007 (Section 6.4).
Functional verification objective: Demonstrate that risk evaluation is deterministic for a given runtime state and does not acquire ownership of canonical information.
Domain: D4.

**TD005-FR-014. Performance Evaluation Gated on Completed Lifecycle Outcomes.**
Requirement: The capability SHALL verify that PerformanceEngine updates its own statistics only when the associated lifecycle event's own `event_type` is a member of the certified realized-event-type set (currently PARTIAL_CLOSE, TRADE_CLOSED), and never on a raw decision or non-realized event.
Rationale: AC-008 (Performance Evaluation) requires evaluation of completed lifecycle outcomes exclusively; this is the exact property TD-004 certified via P3-03 and that any future regression must continue to protect.
Source: Architecture Baseline AC-008 (Section 6.4); direct inspection of `run_engine/core/performance.py`'s own `REALIZED_EVENT_TYPES` constant (Section 6.8); P3-03 Final Certification (Section 6.7).
Functional verification objective: Demonstrate that performance statistics update only in response to certified realized lifecycle outcomes.
Domain: D4.

**TD005-FR-015. LONG/SHORT Aggregation Keying Integrity.**
Requirement: The capability SHALL verify that PerformanceEngine's own statistics are aggregated exclusively by Position Side (the set LONG, SHORT), with no cross-contamination of one side's own statistics by an event belonging to the other side.
Rationale: This is the certified P3-03 keying model; a regression here would silently corrupt performance measurement without any other symptom.
Source: direct inspection of `run_engine/core/performance.py` and `run_engine/core/position.py`'s own `{"LONG", "SHORT"}` side vocabulary (Section 6.8); P3-03 Final Certification (Section 6.7).
Functional verification objective: Demonstrate that performance statistics remain correctly separated by Position Side without cross-attribution.
Domain: D4.

**TD005-FR-016. Executor Action-to-Status Mapping Correctness.**
Requirement: The capability SHALL verify that Executor produces the certified execution status for each certified combination of decision action and current position state.
Rationale: Executor is one of the fourteen active modules (Section 6.3) with a directly observable, certified action/status mapping; no automated guard exists today.
Source: direct inspection of `run_engine/core/execution/executor.py` (Section 6.3).
Functional verification objective: Demonstrate that Executor produces the certified execution status for the certified range of decision and position-state combinations.
Domain: D4.

**TD005-FR-017. Runtime Failure Handling Integrity.**
Requirement: The capability SHALL verify that a rejected runtime transition never modifies canonical runtime state and generates exactly one Runtime Failure Event, preserved in immutable lifecycle history and reproducible on repeated execution of the same rejected transition.
Rationale: AC-015 (Runtime Failure Handling) requires both non-mutation and exactly-once, reproducible Runtime Failure Event generation as two facets of the same certified guarantee for a rejected transition; consolidated here for atomicity.
Source: Architecture Baseline AC-015 (Section 6.4); direct inspection of `run_engine/core/trade_lifecycle.py`'s own `RUNTIME_FAILURE_EVENT` event_type (Section 6.8).
Functional verification objective: Demonstrate that rejected transitions leave canonical runtime state unchanged and produce exactly one reproducible Runtime Failure Event.
Domain: D4.

**TD005-FR-018. Regression Detection Across Certified Units.**
Requirement: The capability SHALL detect a deviation from the previously-certified behaviour associated with any of the P2-02A, P2-03, P2-04, P3-01, P3-02, or P3-03 certified units.
Rationale: This is TD-005's own core purpose as stated in its Register Description ("automated regression test suite for run_engine/core"); Section 6.7 documents that no such cross-unit regression detection currently persists.
Source: Technical Debt Register TD-005 (Section 6.1); P3-01/P3-02/P3-03 Final Certifications (Section 6.7).
Functional verification objective: Demonstrate that a deviation from certified behaviour in any of the certified governance units is detected.
Domain: D5.

**TD005-FR-019. Reproducible Failure Reporting.**
Requirement: The capability SHALL report a detected regression with sufficient detail (at minimum: the affected tick, the affected stage or component, the expected value, and the actual value) to allow the failure to be independently reproduced without re-executing the complete suite.
Rationale: A regression capability that fails without actionable detail does not functionally satisfy TD-005's own purpose of enabling maintainers, reviewers, and certification activities (Section 9) to act on a detected regression; this requirement concerns how evidence integrates with governance stakeholders, distinct from the act of detection itself (TD005-FR-018), and is grouped accordingly.
Source: analytical derivation from Section 9's own stakeholder needs and Section 6.5's own "Regression failures shall be treated as implementation failures" requirement, which presupposes an actionable failure signal.
Functional verification objective: Demonstrate that a detected regression is reported with sufficient detail to be independently reproduced.
Domain: D6.

**TD005-FR-020. Behavioural Equivalence as the Basis of Regression.**
Requirement: The capability SHALL determine regression based on deviation from certified behavioural contracts and SHALL NOT treat implementation differences alone as regressions when certified behaviour remains equivalent.
Rationale: A regression capability defined at the level of source-code identity or byte identity would produce false positives for every legitimate refactor and would not measure what TD-005 actually exists to protect - certified behaviour. Four distinct notions must not be conflated: **behavioural equivalence** (the property this requirement protects - equivalent certified outcomes for equivalent certified inputs), **implementation equivalence** (identical internal algorithm or code structure, not required), **byte identity** (identical file content, not required and not sufficient on its own, since an unchanged file can still exhibit a runtime regression caused by an upstream dependency), and **source identity** (identical source text, neither required nor sufficient for the same reason). This requirement establishes the principle only; it does not define the exact algorithm, tolerance, or comparison method by which behavioural equivalence is determined, which is deferred to a future Scientific Dependency Analysis, Architecture, and Specification (Section 19, OQ-006).
Source: analytical derivation from the Technical Debt Register's own TD-005 purpose (Section 6.1), the Implementation Baseline's own "Regression Validation" purpose statement "Verify that previously validated functionality remains correct" (Section 6.5, which is itself a behavioural, not literal, standard), and Architecture Baseline AC-012 (Deterministic Behaviour, Section 6.4), which is defined over runtime inputs and outputs rather than over source code.
Functional verification objective: Demonstrate that an implementation change preserving certified behavioural contracts is not reported as a regression, and that a change violating a certified behavioural contract is reported as a regression. Verification method to be defined during Specification.
Domain: D5.

**TD005-FR-021. Certified-Contract Boundary for Regression Evaluation.**
Requirement: The capability SHALL evaluate regression only against certified behavioural contracts, approved normative baselines, and explicitly accepted runtime invariants, and SHALL NOT convert incidental, undocumented, or accidental current behaviour into a binding regression contract merely because that behaviour exists in the current implementation.
Rationale: Without this boundary, a future regression capability could silently "freeze" an undocumented implementation detail as if it were a certified guarantee, preventing legitimate future changes and misrepresenting the actual scope of this project's own scientific governance. TD-005's own Register purpose is bounded to "run_engine/core," and this project's own established governance sequence (FRA, SDA, CGA, Architecture, Specification, Implementation, Final Certification) is the sole mechanism by which a behaviour becomes certified; a regression capability must respect that boundary rather than substitute for it.
Source: Architecture Baseline (Section 6.4, the complete set of ADRs and Acceptance Criteria constituting the certified contract); Implementation Baseline (Section 6.5, "Regression Validation" defined as verifying "previously validated functionality," which presupposes a prior validation event, not mere prior existence); the six certified governance units (Section 6.7); Technical Debt Register TD-005 purpose (Section 6.1).
Functional verification objective: Demonstrate that regression evaluation is bounded to certified behavioural contracts and approved normative baselines, and does not treat undocumented incidental behaviour as a binding contract. Verification method to be defined during Specification.
Domain: D5.

**TD005-FR-022. Long-Duration-Validation Precondition Support.**
Requirement: The capability SHALL be usable, without modification, before each of the six mandatory stages of the Long Duration Validation sequence (Functional smoke, 1-hour, 6-hour, 24-hour, 7-day, 30-day).
Rationale: The Implementation Baseline's own mandatory sequence requires every stage to complete successfully before the next is attempted (Section 6.5); without a reusable, automated pass, each of the six stages would require repeating the same costly manual re-verification already evidenced in Section 6.7.
Source: Implementation Baseline, Long Duration Validation section (Section 6.5).
Functional verification objective: Demonstrate that the same regression capability can be applied, unmodified, before each stage of the Long Duration Validation sequence.
Domain: D6.

All twenty-two Functional Requirements are individually numbered with no gap; none is referenced elsewhere in this document only via a compressed range.

## 12. Constraints

The following bound the future regression capability's own behavior. They are constraints on the capability, not functional capabilities the capability must itself achieve, and are stated separately from Section 11 to preserve scientific level separation between "what the capability must do" and "what the capability must not do or must not require."

**TD005-CON-001. Non-Interference With Runtime Behavior.**
Constraint: The capability SHALL NOT alter the content of any active run_engine file, SHALL NOT alter active import behavior, and SHALL NOT produce any side effect observable by the certified active RunLoop during or after test execution.
Rationale: A regression suite that itself alters the system under test would invalidate its own results and would violate the certified runtime's own behavioral guarantees (AC-012).
Source: Architecture Baseline AC-012 (Section 6.4); analytical derivation from the governing task's own explicit non-interference requirement.
Trace: formerly TD005-FR-023 (V1.0); reclassified as a constraint in this revision.

**TD005-CON-002. No Alternative Runtime Execution Path.**
Constraint: The capability SHALL exercise the certified active `RunLoop` and SHALL NOT introduce a parallel or alternative execution path that could itself diverge from the certified runtime's own behavior.
Rationale: A parallel execution path would risk exactly the "Parallel Runtime Architectures" defect (Architecture Defect AD-007) the Architecture Baseline's own Scientific Architecture Diagnosis already identified and resolved for the production runtime; a regression suite must not reintroduce an analogous risk for its own test harness. The exact invocation boundary through which the capability exercises `RunLoop` is not decided by this constraint (Section 19, OQ-001).
Source: Architecture Baseline, Architecture Defect AD-007 (Section 6.4, cross-referenced); analytical derivation.
Trace: formerly TD005-FR-024 (V1.0); reclassified as a constraint in this revision.

**TD005-CON-003. Repository-Scope Compatibility.**
Constraint: The capability's own artifacts SHALL reside within a location compatible with the Repository Consolidation's own Normative Repository Boundary and SHALL NOT cause any archived (ARCHIVE-disposed) or locally-ignored (IGNORE-disposed) component to become reachable from `run_engine.main`'s own active import closure.
Rationale: Repository Consolidation's own RC-AI-004 (No Import from Archive) and RC-AI-005 (No Runtime Import from Scratch or Review Areas) invariants remain binding on any future addition to the repository, including regression-capability artifacts.
Source: Repository Consolidation Architecture RC-AI-004, RC-AI-005 (dependency listed in front matter).
Trace: formerly TD005-FR-025 (V1.0); reclassified as a constraint in this revision.

**TD005-CON-004. Deterministic Test Execution Environment.**
Constraint: The capability SHALL execute without reliance on wall-clock time, network access, or non-seeded randomness, consistent with the active runtime's own determinism guarantee.
Rationale: AC-012 (Deterministic Behaviour) requires identical inputs to always produce identical outputs; a regression capability whose own execution environment introduces non-determinism could produce false positives or false negatives unrelated to any actual runtime regression.
Source: Architecture Baseline AC-012 (Section 6.4); Section 6.8's own confirmation that the active module set itself contains zero non-determinism sources, establishing this constraint as satisfiable in principle.
Trace: formerly TD005-FR-027 (V1.0); reclassified as a constraint in this revision.

All four Constraints are individually numbered with no gap.

## 13. Deferred Specification and Coverage Obligations

The following obligations are real and binding on a future TD-005 Specification, but are not stated as Functional Requirements in Section 11, because each names a specific coverage target or a specific historical repository condition rather than an independent runtime function the capability itself performs. Formalizing either as a Functional Requirement would blur the distinction between "what capability is required" (Section 11) and "what that capability must eventually be shown to cover" (this section) - a Specification-level, not FRA-level, concern.

### 13.1 Active Module Coverage Obligation

A future Specification for TD-005 SHALL define complete coverage of the currently active run_engine module set (Section 6.3, fourteen modules) by the Functional Requirements enumerated in Section 11, without this FRA prescribing the specific test cases, coverage metrics, tooling, or file layout by which that coverage is achieved or measured.

Rationale: TD-005's own Register Description names "run_engine/core" as its subject (Section 6.1); the fourteen-module active set (Section 6.3) is the complete, currently-verified definition of that subject. Leaving any active module functionally unaddressed by the eventual capability would be inconsistent with TD-005's own stated purpose. However, the precise mapping of coverage to test cases is a Specification-level decision, not a Functional Requirement, since it concerns how completeness is demonstrated rather than what capability is required.

Source: Technical Debt Register TD-005 (Section 6.1); Section 6.3's own independently re-derived fourteen-module active set.

Trace: formerly TD005-FR-028 (V1.0); relocated to this deferred obligation in this revision; no Functional Requirement ID is assigned.

### 13.2 Repository-Integrity Regression Obligation (Executor Namespace)

A future Specification for TD-005 SHALL define a regression check confirming that exactly one Executor implementation remains reachable from `run_engine.main`'s own active import closure, protecting the path-collision resolution the Repository Consolidation Final Certification already certified (RC-AD-004), without this FRA prescribing the specific mechanism (for example, an import-closure scan) by which that check is performed.

Rationale: This obligation primarily protects a Repository Consolidation invariant (namespace uniqueness under RC-AD-004) rather than defining an independent Run Engine behavioral function; it is historically specific to a defect this repository's own governance chain already found and fixed once (Repository Consolidation Architecture Section 11, Section 18). Presenting it as a general Run Engine behavioral Functional Requirement would misrepresent its own scientific character. It is nonetheless a real, evidence-grounded regression concern this repository has already experienced and is therefore recorded here rather than silently dropped.

Source: Repository Consolidation Architecture RC-AD-004; Repository Consolidation Final Certification (Section 18, dependency listed in front matter); active import-closure evidence independently re-derived for this document (Section 6.3).

Trace: formerly TD005-FR-018 (V1.0); relocated to this deferred obligation in this revision; no Functional Requirement ID is assigned.

## 14. Assumptions

- The fourteen-module active set identified in Section 6.3 remains the authoritative definition of "run_engine/core" for the purposes of this FRA; should a future repository change alter this set, the Functional Requirements in Section 11 remain applicable to whatever set is then active, since they are stated in terms of certified behavioral properties (deterministic ordering, canonical publication, lifecycle integrity, and so on) rather than fixed file names. The Active Module Coverage Obligation (Section 13.1) would require re-verification against a changed active set.
- The Architecture Baseline's ADRs and Acceptance Criteria and the six certified units' own established contracts (Section 6.4, Section 6.7) remain the authoritative behavioral specification against which regression is defined; this FRA does not reopen or reinterpret any of them.
- No assumption is made about which test framework, directory structure, or CI mechanism will eventually be selected, nor about the exact algorithm by which behavioural equivalence (TD005-FR-020) will be determined; these are explicitly out of scope (Section 15) and left to future governance stages.

## 15. Non-Goals

TD-005, and this FRA specifically, explicitly excludes:

- Performance optimization of the Run Engine or of any future test suite.
- Production monitoring or live-trading validation of any kind.
- Long-duration scientific validation itself (the Functional-smoke-through-30-day sequence, Section 6.5) - this FRA defines a precondition capability for that sequence, not the sequence itself.
- Strategy-quality assessment (trading-strategy performance, profitability, or backtesting quality).
- Market-data validation unrelated to Run Engine behavior.
- Redesign of the Run Engine architecture.
- Correction of any technical debt item other than TD-005 (TD-004 is already closed per the Repository Consolidation Implementation, Section 6.6; TD-006 and TD-007 are not addressed here).
- CI/CD pipeline design, unless a later Architecture stage explicitly justifies it as necessary to satisfy a Functional Requirement.
- Selection of a specific test framework (pytest, unittest, or otherwise).
- The exact algorithm, tolerance, or comparison method used to determine behavioural equivalence (TD005-FR-020) or to bound certified-contract evaluation (TD005-FR-021).
- Any implementation detail: file layout, fixture design, mock strategy, or code.

## 16. Risks of Non-Implementation

- Continued reliance on manually-authored, non-reusable verification scripts for every future governance unit (Section 6.7's own evidenced pattern), with repeated authoring cost and no guarantee of consistent coverage across units.
- Continued absence of any automated guard against regression in deterministic ordering (ADR-010), canonical publication (AC-001, AC-002, AC-006, AC-009), lifecycle integrity (AC-004, AC-014), financial integrity (AC-005), risk evaluation (AC-007), performance evaluation (AC-008), information flow (AC-010), and failure handling (AC-015) - each a certified, binding contract with no automated protection today.
- A materially higher operational cost and risk profile for the Implementation Baseline's own mandatory Long Duration Validation sequence (Section 6.5), since each of its six stages would otherwise require repeating the same manual re-verification effort already shown to be costly (Section 6.7), directly increasing the risk that a real regression is not caught before a long-duration run consumes days or weeks of runtime.
- Continued risk of the specific defect class TD-004 already closed once (decision-tick-based rather than lifecycle-outcome-based performance evaluation, Section 6.8) recurring undetected in a future change, absent an automated guard (TD005-FR-014).
- Absent TD005-FR-020 and TD005-FR-021, a future regression capability could be built at the wrong level of abstraction (source or byte identity, or unbounded coverage of incidental behaviour), producing either false positives that block legitimate work or a false sense of protection that does not actually correspond to TD-005's own certified-behaviour purpose.

## 17. Requirement Traceability

### 17.1 Functional Requirements

| Requirement ID | Source Evidence | Repository File(s) |
|---|---|---|
| TD005-FR-001 | Architecture Baseline ADR-010 | docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md; run_engine/core/loop.py |
| TD005-FR-002 | Architecture Baseline AC-012; Section 6.8 | docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md; run_engine/core/loop.py |
| TD005-FR-003 | Architecture Baseline AC-009, ADR-010 | docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md; run_engine/core/canonical_state.py |
| TD005-FR-004 | Architecture Baseline AC-001, AC-002; Section 6.8 | run_engine/core/canonical_state.py; run_engine/core/canonical_enforcer.py |
| TD005-FR-005 | Architecture Baseline AC-006; analytical derivation | run_engine/core/canonical_state.py |
| TD005-FR-006 | Architecture Baseline AC-010 | run_engine/core/loop.py; run_engine/core/risk.py |
| TD005-FR-007 | Architecture Baseline AC-004; Section 6.8 | run_engine/core/trade_lifecycle.py; run_engine/core/position.py |
| TD005-FR-008 | Architecture Baseline AC-014; Section 6.8 | run_engine/core/trade_lifecycle.py |
| TD005-FR-009 | Architecture Baseline AC-004, AC-014; Section 6.8 | run_engine/core/trade_lifecycle.py |
| TD005-FR-010 | Architecture Baseline AC-014; Section 6.8 | run_engine/core/trade_lifecycle.py |
| TD005-FR-011 | Architecture Baseline AC-005 | run_engine/core/pnl.py |
| TD005-FR-012 | Architecture Baseline AC-005, AC-006 | run_engine/core/pnl.py; run_engine/core/canonical_state.py |
| TD005-FR-013 | Architecture Baseline AC-007 | run_engine/core/risk.py |
| TD005-FR-014 | Architecture Baseline AC-008; Section 6.8; P3-03 Final Certification | run_engine/core/performance.py |
| TD005-FR-015 | Section 6.8; P3-03 Final Certification | run_engine/core/performance.py; run_engine/core/position.py |
| TD005-FR-016 | Direct inspection, Section 6.3 | run_engine/core/execution/executor.py |
| TD005-FR-017 | Architecture Baseline AC-015; Section 6.8 | run_engine/core/trade_lifecycle.py; run_engine/core/canonical_state.py |
| TD005-FR-018 | TD-005 Register; P3-01/P3-02/P3-03 Final Certifications | docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md; docs/architecture/certification/P3_01_FINAL_CERTIFICATION_V1_2026-07-13.md; docs/architecture/certification/P3_02_FINAL_CERTIFICATION_V1_2026-07-13.md; docs/architecture/certification/P3_03_FINAL_CERTIFICATION_V1_2026-07-13.md |
| TD005-FR-019 | Analytical derivation; Section 6.5 | docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md |
| TD005-FR-020 | TD-005 Register; Implementation Baseline; Architecture Baseline AC-012; analytical derivation | docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md; docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md; docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md |
| TD005-FR-021 | Architecture Baseline; Implementation Baseline; six certified units; TD-005 Register | docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md; docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md; docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md |
| TD005-FR-022 | Implementation Baseline, Long Duration Validation | docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md |

All twenty-two Functional Requirement IDs are individually listed above.

### 17.2 Constraints

| Constraint ID | Source Evidence | Repository File(s) |
|---|---|---|
| TD005-CON-001 | Architecture Baseline AC-012; analytical derivation | all 14 active files, Section 6.3 |
| TD005-CON-002 | Architecture Baseline, Architecture Defect AD-007; analytical derivation | run_engine/core/loop.py |
| TD005-CON-003 | Repository Consolidation RC-AI-004, RC-AI-005 | docs/architecture/REPOSITORY_CONSOLIDATION_ARCHITECTURE_V1_2026-07-14.md |
| TD005-CON-004 | Architecture Baseline AC-012; Section 6.8 | all 14 active files, Section 6.3 |

All four Constraint IDs are individually listed above.

### 17.3 Deferred Specification and Coverage Obligations

| Obligation | Source Evidence | Repository File(s) |
|---|---|---|
| Section 13.1, Active Module Coverage Obligation | TD-005 Register; Section 6.3 | docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md; all 14 active files, Section 6.3 |
| Section 13.2, Repository-Integrity Regression Obligation | Repository Consolidation RC-AD-004; Final Certification | docs/architecture/REPOSITORY_CONSOLIDATION_ARCHITECTURE_V1_2026-07-14.md; docs/architecture/certification/REPOSITORY_CONSOLIDATION_FINAL_CERTIFICATION_V1_2026-07-14.md; run_engine/core/execution/executor.py |

Neither obligation carries a Functional Requirement ID, consistent with Section 13's own explicit classification.

### 17.4 Open Questions

| Open Question | Related Requirement or Constraint |
|---|---|
| OQ-001 | TD005-CON-002 |
| OQ-002 | TD005-FR-018 |
| OQ-003 | Section 6.3 (RETAIN-Deferred-Scope files) |
| OQ-004 | TD005-FR-022 |
| OQ-005 | Section 13.1 |
| OQ-006 | TD005-FR-020, TD005-FR-021 |

## 18. FRA Completion Criteria

This Functional Requirement Analysis is complete and ready for a future Scientific Dependency Analysis when:

- Complete repository-evidence review has occurred (Section 6, eight independently-verified evidence subsections), and no evidence was weakened in this revision.
- Functional Requirements are individually enumerated, not compressed into ranges (Section 11, twenty-two individually-numbered requirements; Section 17.1, all twenty-two individually traced).
- Functional Requirements are correctly separated from Constraints: every requirement in Section 11 states a capability the future suite must achieve; every requirement in Section 12 states a boundary condition on the suite's own behavior; none of the four Constraints (Section 12) is stated as a Functional Requirement, and none of the twenty-two Functional Requirements (Section 11) states a boundary condition instead of a capability.
- No Functional Requirement prescribes a concrete test design; every Functional Requirement's own verification intent is stated as an implementation-neutral functional verification objective (Section 11), with the two Functional Requirements whose own eventual verification method is genuinely undecided (TD005-FR-020, TD005-FR-021) explicitly deferring that method to Specification.
- The behavioural-equivalence principle (TD005-FR-020) is explicit, distinguishes behavioural equivalence from implementation equivalence, byte identity, and source identity, and does not define the exact equivalence algorithm.
- The certified-contract boundary (TD005-FR-021) is explicit and prevents incidental or undocumented behaviour from being treated as a binding regression contract.
- Deferred coverage and repository-integrity obligations are clearly identified outside the Functional Requirement list (Section 13), each individually traceable, with neither assigned a Functional Requirement ID.
- No premature architecture or implementation decision has been made (verified: Section 11's own requirement statements are implementation-neutral; no test framework, file layout, invocation boundary, or CI mechanism is named as a decision anywhere in this document).
- Complete source traceability exists for every Functional Requirement, every Constraint, and every deferred obligation (Section 17).
- Explicit scope and non-goals are stated (Section 5, Section 15).
- Consistency with active baselines and certifications is maintained (Section 6.4 through 6.7, each independently re-verified against current repository content, not assumed from any handover text).
- No unresolved contradiction is hidden as an assumption (Section 14's own three assumptions are each explicitly stated as assumptions, not asserted as verified fact; Section 19 lists the genuine open questions this FRA does not resolve, including no unresolved architectural choice - such as the invocation boundary of OQ-001 or the equivalence definition of OQ-006 - disguised as a settled requirement).
- Numbering is continuous and internally consistent: Functional Requirements TD005-FR-001 through TD005-FR-022 with no gap; Constraints TD005-CON-001 through TD005-CON-004 with no gap; Open Questions OQ-001 through OQ-006 with no gap; every cross-reference affected by this revision's own renumbering has been updated.

All criteria above are satisfied by this document.

## 19. Open Questions for Scientific Dependency Analysis

- **OQ-001.** Which certified public or internal invocation boundary is scientifically appropriate for regression verification, while preserving the active runtime path (TD005-CON-002), is a Dependency- and Architecture-level question, not resolved here. This question is deliberately left open rather than presupposing any specific harness boundary such as direct invocation of `RunLoop.step()`.
- **OQ-002.** Whether TD005-FR-018's own "previously-certified behaviour" baseline should be captured from the certified units' own historical Implementation/Certification commits, or freshly established at TD-005 Implementation time, is not resolved here; both are consistent with this FRA's own requirement text.
- **OQ-003.** Whether the four inactive RETAIN-Deferred-Scope files (Section 6.3) should ever be brought into TD-005's own coverage scope is explicitly not addressed here, since they hold no active Computational Authority today; a future SDA should confirm this remains true before finalizing coverage boundaries.
- **OQ-004.** Whether TD005-FR-022's own "usable, without modification" property implies any specific execution-time budget compatible with being run before a Functional smoke validation (which is, by its own name, expected to be fast) is not resolved here; this is an Architecture-level tradeoff, not a Functional Requirement.
- **OQ-005.** This document did not locate any existing repository convention for where future automated test code should reside (Section 6.2 confirms `tests/` currently holds no run_engine-relevant content); the SDA should independently assess whether `tests/` itself, `tools/`, or another location is dependency-compatible with the Normative Repository Boundary, without this FRA prejudging that choice.
- **OQ-006. Scientific Definition of Regression Equivalence.** TD005-FR-020 establishes that regression is defined by behavioural equivalence rather than implementation or byte identity, but does not define what "equivalent" means in measurable terms. A future governance stage must resolve: which observable runtime properties (canonical field values, event sequences, published snapshots, or another set) constitute the basis of comparison; which differences represent acceptable implementation variation (for example, floating-point representation, object identity, or internal intermediate variables) as opposed to a genuine behavioural regression; whether equivalence should be evaluated as exact equality, a normalized comparison, a tolerance-bounded numeric comparison, a state-based comparison (final canonical values), an event-based comparison (the sequence of lifecycle and failure events), or a contract-based comparison (conformance to the specific Acceptance Criterion or Architecture Decision each requirement traces to); and which of these aspects belongs to the Scientific Dependency Analysis (identifying what the comparison depends on), which belongs to the Architecture (deciding the comparison model), and which belongs to the Specification (defining the exact comparison contract). This question is not answered here.

All six Open Question IDs are individually listed above with no gap.

## 20. Conclusion

TD-005 addresses a verified, evidence-grounded gap: no automated regression capability exists for run_engine/core today, and every certified governance unit to date has instead relied on manually-authored, non-reusable verification scripts (Section 6.7). This revised (V1.1) document derives twenty-two individually-numbered, implementation-neutral Functional Requirements (TD005-FR-001 through TD005-FR-022) across six capability domains, four individually-numbered Constraints (TD005-CON-001 through TD005-CON-004) bounding the future capability's own behavior, and two clearly identified Deferred Specification and Coverage Obligations whose own full functional definition is left to a future Specification stage. This revision strengthens the FRA's own scientific level separation relative to V1.0: functional capability, behavioral boundary conditions, and deferred coverage/repository-integrity obligations are now each stated in their own appropriate section rather than uniformly as Functional Requirements, and every Functional Requirement's own verification intent is now stated as an implementation-neutral functional verification objective rather than a concrete test design. Two new, central Functional Requirements (TD005-FR-020, Behavioural Equivalence as the Basis of Regression; TD005-FR-021, Certified-Contract Boundary for Regression Evaluation) establish the scientific principle that regression is determined by deviation from certified behaviour, not by source-code or byte identity, and that regression evaluation itself must remain bounded to certified contracts rather than incidental implementation behaviour. This document makes no architecture or implementation decision and defers test-framework, file-layout, invocation-boundary, CI-mechanism, and equivalence-algorithm selection entirely to future governance stages. This document is ready for a future TD-005 Scientific Dependency Analysis.
