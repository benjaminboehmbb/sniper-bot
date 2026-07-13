Document Class:
Capability Gap Analysis

Document ID:
P2-03-CGA

Version:
V1.0

Status:
Draft for Internal Review

Date:
2026-07-11

Project:
Trading-Bot Scientific Runtime

Subsystem:
Run Engine

Primary Location:
docs/architecture/analysis/P2_03_CAPABILITY_GAP_ANALYSIS_V1_2026-07-11.md

Depends On:
- docs/architecture/analysis/P2_03_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-11.md
- docs/architecture/analysis/P2_03_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-11.md
- docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md
- docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md
- docs/architecture/certification/P2_02A_FINAL_CERTIFICATION_V1_2026-07-10.md
- docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md
- current runtime code at HEAD 815cd8a

Referenced By:
- future P2-03 Architecture
- future P2-03 Specification
- future P2-03 Certification

---

# P2-03 Capability Gap Analysis

## 1. Purpose

This document performs the Capability Gap Analysis for P2-03 (Financial Ownership), following directly from `P2_03_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-11.md` (Status: Draft for Internal Review, Functional Readiness: READY) and `P2_03_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-11.md` (Status: Draft for Internal Review, Readiness for Capability Gap Analysis: READY).

This document determines, capability by capability, which financial-ownership capabilities already exist in the active runtime, which exist only partially, and which are entirely missing, measured strictly against the twenty functional requirements the FRA already established and the eighteen scientific dependencies the SDA already derived. It designs no solution, selects no interface, resolves no Open Question, and makes no architecture decision. Its sole purpose is objective capability determination, repository-grounded in every case.

## 2. Scope

In scope: gap analysis of the fifteen financial capabilities named by the governing task (Section 6), each mapped onto the FRA's twenty functional requirements (P2-03-FR-001 through P2-03-FR-020), the SDA's eight capability clusters and eighteen dependencies (P2-03-DEP-001 through P2-03-DEP-018), and the Architecture Baseline's ADR-005, ADR-006, and ADR-007.

Out of scope: the same boundaries already established by the FRA (Section 24 of that document) and the SDA (Section 2 of that document) apply unchanged - full RiskEngine redesign, Risk Policy, Position Sizing, full PerformanceEngine redesign, Unrealized PnL and Mark-to-Market Portfolio Valuation unless explicitly brought into scope by a later governing document, Multi-Asset Accounting, Fees/Funding/Slippage/Tax Accounting, Persistence, Recovery, the Tick-Complete Snapshot architecture beyond what is already implemented, repository cleanup, and the automated regression test suite (TD-005). No gap identified in these areas is treated as a P2-03 gap; each is recorded as external, deferred, or a future compatibility constraint, consistent with the FRA's and SDA's own scope protection. No architecture decision, interface shape, or implementation detail is proposed anywhere in this document; no runtime file is read for new evidence beyond what the FRA and SDA already established.

## 3. Governing Baseline

- `docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md` - ADR-005 (Profit and Loss Accounting), ADR-006 (Canonical Financial State Ownership), ADR-007 (Risk Evaluation as a Pure Computational Layer), ADR-002 (Event-Driven Runtime Evolution, Financial Events), ADR-008 (Performance Ownership), ADR-010 (Deterministic Runtime Execution Ordering), ADR-011 (Runtime Failure Handling), ADR-004, ADR-009, the Runtime Ownership Matrix, Rules OM-001 through OM-009, Architecture Invariants AI-005 and AI-010.
- `docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md` - the P2-03 unit definition ("Financial Ownership. Objectives: Implement PnLEngine ownership. Verify Realized PnL (cumulative). Verify Equity, Peak Equity and Drawdown consistency.").
- `docs/architecture/analysis/P2_03_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-11.md` - twenty functional requirements, six Required Capabilities, twelve Open Questions, as internally reviewed (Status: Internal Consistency Review PASS).
- `docs/architecture/analysis/P2_03_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-11.md` - eight capability clusters, eighteen dependency records, twelve classified Open Questions, seven Dependency Stages, as internally reviewed (Status: Internal Consistency Review PASS).
- `docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md` - TD-001 through TD-007, in particular TD-006 (RiskEngine Peak Equity and Drawdown Ownership Duplication, Target Phase P2-03/P2-04, Status Deferred).
- Current runtime code at HEAD `815cd8a`.

## 4. Verified Runtime Baseline

Repository state re-verified for this analysis: branch `run-engine-consolidation-safety`, HEAD `815cd8a`, matching the FRA's and SDA's own verification exactly. `run_engine/` remains clean (`git status --short run_engine/` returns no output). No runtime file has changed since the FRA and SDA were written; every finding in those two documents remains current.

This analysis relies on the FRA's Sections 6 through 23 and the SDA's Sections 7 through 24 without re-deriving their findings from the code a second time; every capability's Current Runtime Evidence entry below cites the specific FRA or SDA section, requirement ID, or dependency ID that already established the underlying fact, rather than re-quoting source code. The nine runtime files named by the governing task (`pnl.py`, `loop.py`, `canonical_state.py`, `canonical_enforcer.py`, `risk.py`, `performance.py`, `trade_lifecycle.py`, `position.py`, `main.py`) were re-read in full for this analysis; no new repository-grounded fact beyond what the FRA and SDA already recorded was found.

## 5. Scientific Context

This analysis inherits the SDA's own structural finding (SDA Section 4) as its starting context: the governing Architecture Baseline already establishes the intended architectural concepts for every financial object in scope (Realized PnL event and cumulative, Equity, Peak Equity, Drawdown; Drawdown Ratio's naming remains an open question, FR-012). Consequently, this Capability Gap Analysis does not, in the main, find capabilities that lack a scientific definition - it finds capabilities whose scientific definition is already settled but whose Computational Authority, Authoritative Owner, or consumption boundary has not yet been operationally realized to match that definition. This distinction - definitional completeness versus operational realization - is the organizing principle of every capability entry in Section 7.

Method: each capability is evaluated against a single Current Status (COMPLETE, PARTIAL, or MISSING), reflecting whether the capability's Computational Authority, Authoritative Owner, and consumption boundary all conform to the FRA/SDA-derived target simultaneously (COMPLETE), whether at least one of these three roles conforms while at least one does not (PARTIAL), or whether the capability's underlying information object does not exist in the active runtime in any observable form (MISSING). A capability whose economic effect is observable only as a side effect of a different, already-owned capability (for example, Realized PnL's cumulative effect being observable only inside Equity's running total) is classified MISSING as its own information object, with the implicit effect recorded separately, consistent with the FRA's own precision on this point (FRA Section 13, Gap 2).

## 6. Capability Inventory

| Capability ID | Name | Current Status |
|---|---|---|
| P2-03-CAP-001 | Event Realized PnL | COMPLETE |
| P2-03-CAP-002 | Cumulative Realized PnL | MISSING |
| P2-03-CAP-003 | Equity Ownership | PARTIAL |
| P2-03-CAP-004 | Peak Equity Ownership | PARTIAL |
| P2-03-CAP-005 | Drawdown Ownership | PARTIAL |
| P2-03-CAP-006 | Drawdown Ratio Ownership | PARTIAL |
| P2-03-CAP-007 | Canonical Financial Publication | PARTIAL |
| P2-03-CAP-008 | RiskEngine Financial Consumption | PARTIAL |
| P2-03-CAP-009 | PerformanceEngine Financial Consumption | COMPLETE |
| P2-03-CAP-010 | RuntimeFailure Financial Consistency | PARTIAL |
| P2-03-CAP-011 | Reset Consistency | PARTIAL |
| P2-03-CAP-012 | Replay Consistency | PARTIAL |
| P2-03-CAP-013 | Financial Determinism | PARTIAL |
| P2-03-CAP-014 | Canonical Financial State | PARTIAL |
| P2-03-CAP-015 | Financial Compatibility | COMPLETE |

Fifteen capabilities were evaluated, matching exactly the fifteen named by the governing task. No capability was found requiring artificial creation beyond this list; every capability below is grounded in a specific FRA requirement, SDA dependency, or ADR text, per the Section 5 method. Three capabilities (CAP-001, CAP-009, CAP-015) are already COMPLETE. One capability (CAP-002) is MISSING as an explicit information object. The remaining eleven are PARTIAL.

## 7. Current Financial Capabilities

### P2-03-CAP-001 - Event Realized PnL

Scientific Purpose: the financial consequence of exactly one completed lifecycle event (`TRADE_CLOSED` or `PARTIAL_CLOSE`), computed once per occurrence, per ADR-005.
Current Runtime Evidence: `PnLEngine.update()` (FRA Section 7) already computes this value exclusively and correctly, guarded to return `0.0` for every non-closing event, `RUNTIME_FAILURE_EVENT`, and `HOLD` ticks.
Current Status: COMPLETE.
Blocking Dependencies: none.
Related Functional Requirements: FR-001.
Related Dependency IDs: DEP-018 (fixed reference frame constraint on later work).
Related ADR: ADR-005.
Related Technical Debt: none.
Scope Classification: in scope; already satisfied, no further work required for this capability specifically.

### P2-03-CAP-002 - Cumulative Realized PnL

Scientific Purpose: the running total of every Realized PnL (event) value since runtime initialization, named explicitly by ADR-005 as one of five values `PnLEngine` must compute and by ADR-006's Equity formula as a distinct additive term.
Current Runtime Evidence: no field, method, or instance attribute anywhere in the active runtime computes or stores this running sum as its own object (FRA Section 6, item 7; FRA Section 13, Gap 2). Its economic effect is present but entirely implicit, entangled inside `CanonicalState.state["equity"]`'s own incremental running total (`run_engine/core/loop.py:71`).
Current Status: MISSING (as an explicit information object; its economic effect is implicitly present, not itself owned or separately verifiable).
Blocking Dependencies: none upstream; this capability itself gates CAP-003's formula-consistency half, CAP-007's new-storage-location half, and CAP-010's failure-non-mutation re-verification for this specific value.
Related Functional Requirements: FR-002, FR-003, FR-004.
Related Dependency IDs: DEP-003, DEP-004, DEP-005, DEP-010.
Related ADR: ADR-005, ADR-006.
Related Technical Debt: none directly logged; this capability's absence is a newly confirmed FRA finding, not a pre-existing debt item.
Scope Classification: in scope; the unit's Baseline-named central objective ("Verify Realized PnL (cumulative)").

### P2-03-CAP-003 - Equity Ownership

Scientific Purpose: exactly one Computational Authority (`PnLEngine`, per ADR-005/ADR-006) and exactly one Authoritative Owner (`CanonicalState`, per ADR-006) for Equity, internally consistent with `Initial Capital + Realized PnL (cumulative) + Unrealized PnL`.
Current Runtime Evidence: `RunLoop.step()` performs the Equity computation itself (`run_engine/core/loop.py:71`, `equity = self.cstate.get()["equity"] + pnl`), not `PnLEngine` (FRA Section 8). `CanonicalState.state["equity"]`'s storage location is already correct and already the sole Authoritative Owner (FRA Section 19, FR-006's Existing Evidence).
Current Status: PARTIAL - Authoritative Owner role COMPLETE; Computational Authority role violated (`RunLoop`, not `PnLEngine`).
Blocking Dependencies: none upstream.
Related Functional Requirements: FR-005, FR-006, FR-007.
Related Dependency IDs: DEP-001 (constraint from already-correct storage), DEP-005 (gates FR-007 on CAP-002), DEP-011 (gates CAP-010), DEP-013 (conditional, Unrealized-PnL scope), DEP-015 (gates CAP-013).
Related ADR: ADR-005, ADR-006.
Related Technical Debt: none directly logged; a newly confirmed FRA finding, the single most severe gap in this analysis (FRA Section 16, FR-005's Architectural Rationale).
Scope Classification: in scope; central to the Baseline's own stated objective ("Verify Equity ... consistency").

### P2-03-CAP-004 - Peak Equity Ownership

Scientific Purpose: exactly one Computational Authority (`PnLEngine`, per ADR-006) for Peak Equity, with no independently-tracked competing copy anywhere, per ADR-007's prohibition on `RiskEngine` owning Equity or Peak Equity in any form.
Current Runtime Evidence: two independent, non-communicating computations exist (FRA Section 9): `CanonicalState.update_equity()` (`run_engine/core/canonical_state.py:64-65`) and `RiskEngine.check()` (`run_engine/core/risk.py:9-10,21-22,51`, its own `self.peak_equity` instance attribute). Both are seeded with the same hardcoded `100.0` literal and currently agree only by coincidence of the synchronous execution model, not by architectural guarantee.
Current Status: PARTIAL - storage location (`CanonicalState.state["peak_equity"]`) matches the Runtime Ownership Matrix's Authoritative Owner assignment; Computational Authority role violated in both of its two current implementations, since neither is `PnLEngine`.
Blocking Dependencies: none upstream; this capability jointly gates CAP-005 (Drawdown's input source) and CAP-008 (RiskEngine's read-only boundary).
Related Functional Requirements: FR-008, FR-009.
Related Dependency IDs: DEP-006, DEP-007, DEP-008, DEP-009, DEP-011, DEP-014, DEP-017.
Related ADR: ADR-006, ADR-007.
Related Technical Debt: TD-006, directly and centrally (this capability's non-conformance is the precise defect TD-006 names).
Scope Classification: in scope; explicit Baseline objective ("Verify ... Peak Equity ... consistency"); TD-006's closure target.

### P2-03-CAP-005 - Drawdown Ownership

Scientific Purpose: `RiskEngine` as the Computational Authority for Drawdown (per ADR-006, correctly assigned already), computed exclusively from canonical financial state, not from any internally-tracked copy.
Current Runtime Evidence: `RiskEngine.check()` computes `drawdown = self.peak_equity - equity` (`run_engine/core/risk.py:24-25`) exclusively from its own internally-tracked `self.peak_equity` (CAP-004's non-conformant tracker); it never reads `CanonicalState.state["peak_equity"]` (confirmed by direct repository search, FRA Section 9).
Current Status: PARTIAL - Computational Authority assignment (`RiskEngine`) is itself correct per ADR-006; input source is wrong (own tracked copy instead of canonical financial state).
Blocking Dependencies: CAP-004 (Peak Equity), conditionally per DEP-007 and jointly per DEP-008.
Related Functional Requirements: FR-010, FR-011.
Related Dependency IDs: DEP-002, DEP-007, DEP-008, DEP-009, DEP-017.
Related ADR: ADR-006.
Related Technical Debt: TD-006, directly (this capability's non-conformance is TD-006's Drawdown-specific half).
Scope Classification: in scope; explicit Baseline objective ("Verify ... Drawdown consistency"); TD-006's closure target.

### P2-03-CAP-006 - Drawdown Ratio Ownership

Scientific Purpose: a normalized ratio (`drawdown / peak_equity`), a Risk Metric per ADR-007's general category, whose Computational Authority and Authoritative Owner are not independently named by any ADR text.
Current Runtime Evidence: `RiskEngine.check()` computes and `CanonicalState.state["drawdown_ratio"]` stores this value alongside Drawdown, sharing the same input-source characteristics as CAP-005 (`run_engine/core/risk.py:27-30`; FRA Section 10). Unlike Equity, Peak Equity, and Drawdown, no governing ADR explicitly assigns a unique Computational Authority and Authoritative Owner for Drawdown Ratio.
Current Status: PARTIAL - the mechanical computation and storage location exist and mirror CAP-005's own conformance profile; the ownership assignment itself (which ADR governs it, and therefore which component is its intended Computational Authority and Authoritative Owner) remains scientifically undefined, an open question the FRA itself records (FR-012) rather than resolves.
Blocking Dependencies: none; this capability is confirmed ungated by the SDA (SDA Section 21, "not bound to any specific stage").
Related Functional Requirements: FR-012.
Related Dependency IDs: none (SDA confirms no dependency record targets FR-012).
Related ADR: ADR-006 (by proximity to Drawdown), ADR-007 (by Risk Metric category); no ADR names Drawdown Ratio directly.
Related Technical Debt: none directly; adjacent to TD-006 only in that both concern `RiskEngine`'s current Drawdown-adjacent computation, per the FRA's own framing (FRA Section 21, FR-012's Related Technical Debt).
Scope Classification: in scope, as an open naming/ownership question; not yet resolved by any document in this governance chain.

### P2-03-CAP-007 - Canonical Financial Publication

Scientific Purpose: `CanonicalState` as the sole storage location and Writer-on-Behalf-Of path for every financial value, including a genuinely new storage location for Cumulative Realized PnL and a single, explicit source for the Initial Capital literal.
Current Runtime Evidence: `CanonicalState.state["pnl"]`, `["equity"]`, `["peak_equity"]`, `["drawdown"]`, `["drawdown_ratio"]` already exist and are already the correct Authoritative Owner locations (FRA Sections 19, 21). No `CanonicalState` key exists for Cumulative Realized PnL (CAP-002). The Initial Capital literal `100.0` is independently duplicated, undocumented, in `CanonicalState.__init__` and `RiskEngine.__init__` (FRA Section 6, item 9).
Current Status: PARTIAL - five of six storage locations are already conformant; the sixth (Cumulative Realized PnL) does not yet exist; the single-source Initial Capital requirement is unmet.
Blocking Dependencies: CAP-002 (for the new storage location's value-correctness half only; the key-existence half is ungated, per SDA's D1/D2-style split, SDA Section 9).
Related Functional Requirements: FR-003, FR-006, FR-011, FR-017.
Related Dependency IDs: DEP-001, DEP-002, DEP-003, DEP-014, DEP-018.
Related ADR: ADR-006, Rule OM-006.
Related Technical Debt: none directly; the Initial Capital duplication is described by the SDA as being "in kind" related to TD-006's "undeclared, silent coupling" framing without being TD-006 itself.
Scope Classification: in scope.

### P2-03-CAP-008 - RiskEngine Financial Consumption

Scientific Purpose: `RiskEngine` as a strictly read-only consumer of canonical Equity and Peak Equity, per ADR-007's "Risk Evaluation does not create runtime truth."
Current Runtime Evidence: `RiskEngine.check()`'s read of `state.get("equity", ...)` (`run_engine/core/risk.py:15`) is already read-only in mechanism; however, CAP-004's Peak-Equity ownership violation means `RiskEngine` simultaneously reads a canonical value and independently tracks its own competing copy, which undermines the read-only boundary in substance even though no single line of code mutates canonical state (FRA Section 22, FR-013's Existing Evidence).
Current Status: PARTIAL - mechanically read-only for Equity; not verifiably read-only for Peak Equity while CAP-004 remains unresolved.
Blocking Dependencies: CAP-004 (Peak Equity Ownership) and CAP-005 (Drawdown Ownership), jointly, per DEP-009.
Related Functional Requirements: FR-013.
Related Dependency IDs: DEP-009.
Related ADR: ADR-007.
Related Technical Debt: TD-006 (this capability's incomplete conformance is a direct symptom of TD-006).
Scope Classification: in scope.

### P2-03-CAP-009 - PerformanceEngine Financial Consumption

Scientific Purpose: `PerformanceEngine` as a strictly read-only consumer of Realized PnL (event), never independently computing, owning, or duplicating any canonical Financial State value, per ADR-008 and Rule OM-008.
Current Runtime Evidence: `PerformanceEngine` has never held any financial-state-owning field (FRA Section 11); its `stats["*"]["pnl"]` is a distinct, already-correctly-scoped Performance Metric (a per-action running mean), not a duplicate Realized PnL representation, and is never republished under a `CanonicalState` financial key.
Current Status: COMPLETE.
Blocking Dependencies: none.
Related Functional Requirements: FR-014.
Related Dependency IDs: DEP-018 (fixed reference frame constraint on later work).
Related ADR: ADR-008, Rule OM-008.
Related Technical Debt: none.
Scope Classification: in scope; already satisfied, no further work required for this capability specifically.

### P2-03-CAP-010 - RuntimeFailure Financial Consistency

Scientific Purpose: rejected transitions (`RUNTIME_FAILURE_EVENT`) SHALL never modify Realized PnL (event or cumulative), Equity, Peak Equity, Drawdown, Drawdown Ratio, or `PerformanceEngine.stats`, per ADR-011.
Current Runtime Evidence: `PnLEngine.update()`'s `event_type` guard (`run_engine/core/pnl.py:23-24`) and `PerformanceEngine.update()`'s equivalent guard (`run_engine/core/performance.py:8-9`) already correctly implement this contract for Realized PnL (event) and `PerformanceEngine.stats`, already certified in P1-04. No equivalent re-verification exists yet for Cumulative Realized PnL (CAP-002, not yet created) or for the relocated Equity/Peak-Equity computation (CAP-003/CAP-004, not yet relocated), since those code paths do not yet exist in their target form.
Current Status: PARTIAL - already-certified portion (event-PnL, PerformanceEngine.stats) COMPLETE; remaining portion (cumulative-PnL, relocated Equity/Peak-Equity) cannot yet be verified, since its subject does not yet exist in target form.
Blocking Dependencies: CAP-002, CAP-003, CAP-004.
Related Functional Requirements: FR-015.
Related Dependency IDs: DEP-010, DEP-011.
Related ADR: ADR-011.
Related Technical Debt: none.
Scope Classification: in scope.

### P2-03-CAP-011 - Reset Consistency

Scientific Purpose: every runtime component holding financial-adjacent state SHALL report values consistent with a freshly-initialized runtime after a complete reset sequence, per AI-010 (Financial Consistency).
Current Runtime Evidence: `CanonicalState.reset()` correctly restores its own `equity`/`peak_equity`/`pnl`/`drawdown`/`drawdown_ratio` defaults (`run_engine/core/canonical_state.py:101-106`). `RiskEngine` has no `reset()` method of any kind and would retain a stale `self.peak_equity` across any reset call; this is a latent, not presently-triggered, defect, since no active caller of `CanonicalState.reset()` exists anywhere in `run_engine/core` or `run_engine/main.py` today (FRA Section 9, Section 25).
Current Status: PARTIAL - `CanonicalState`'s own reset is complete for the fields it owns; the complete inventory of financial-adjacent state (including whatever `RiskEngine` retains after CAP-004's resolution) is not yet finalized, so full reset consistency cannot yet be certified.
Blocking Dependencies: CAP-004 (Peak Equity Ownership disposition determines the exact reset scope).
Related Functional Requirements: FR-017, FR-018.
Related Dependency IDs: DEP-012, DEP-014.
Related ADR: AI-010.
Related Technical Debt: none directly; related in kind to TD-006's "undeclared, silent coupling" framing (FRA Section 25).
Scope Classification: in scope.

### P2-03-CAP-012 - Replay Consistency

Scientific Purpose: a historical tick/decision sequence, replayed, SHALL reproduce a functionally identical financial-state sequence at every step - a sequence-level instance of the same underlying property CAP-013 (Financial Determinism) names at the single-tick level. The FRA and SDA do not scientifically separate "Replay" from "Determinism" as two distinct requirements; both are governed by the same FR-016 and the same evidence base. This capability entry records the sequence-replay framing explicitly, per the governing task's own naming, without introducing a requirement the FRA does not already contain.
Current Runtime Evidence: FR-016's own Validation Condition already specifies a replay-style check ("an identical scripted tick/decision sequence run twice produces functionally identical Realized-PnL/Equity/Peak-Equity/Drawdown/Drawdown-Ratio sequences," FRA Section 21). The P2-02A Final Certification (Section 16, Determinism and Replay Results) already established this property for the current, pre-P2-03 system.
Current Status: PARTIAL - established and certified for the current system; not yet re-verified against the system CAP-002 through CAP-011 will produce once resolved.
Blocking Dependencies: CAP-002 through CAP-011, collectively, per DEP-015.
Related Functional Requirements: FR-016.
Related Dependency IDs: DEP-015.
Related ADR: ADR-005, ADR-006, AI-005.
Related Technical Debt: none.
Scope Classification: in scope.

### P2-03-CAP-013 - Financial Determinism

Scientific Purpose: identical runtime inputs (lifecycle histories) SHALL always produce identical financial outputs, per ADR-005's and ADR-006's own Acceptance Criteria and AI-005 (Deterministic Execution) - the single-execution counterpart to CAP-012's sequence-replay framing, sharing the identical requirement (FR-016) and evidence base.
Current Runtime Evidence: identical to CAP-012 (FRA Section 21; P2-02A Final Certification Section 16).
Current Status: PARTIAL - identical basis and reasoning to CAP-012.
Blocking Dependencies: CAP-002 through CAP-011, collectively, per DEP-015.
Related Functional Requirements: FR-016.
Related Dependency IDs: DEP-015.
Related ADR: ADR-005, ADR-006, AI-005.
Related Technical Debt: none.
Scope Classification: in scope.

### P2-03-CAP-014 - Canonical Financial State

Scientific Purpose: the umbrella, aggregate property that `CanonicalState` contains exactly one canonical financial state in its entirety (per ADR-006's own Acceptance Criterion, "CanonicalState contains exactly one canonical financial state"), distinct from any single field's individual conformance and only fully true once every constituent capability (CAP-002 through CAP-006) is itself resolved.
Current Runtime Evidence: five of the six financial values already reside at their correct storage location (CAP-003's, CAP-005's, and CAP-006's Authoritative Owner halves); one (CAP-002) has no storage location at all; two (CAP-003, CAP-004) are populated by a non-conformant Computational Authority even though their storage location is correct.
Current Status: PARTIAL - the aggregate property is not yet true, since it requires every constituent capability's own conformance simultaneously.
Blocking Dependencies: CAP-002, CAP-003, CAP-004 (directly); CAP-005, CAP-006 (via their shared input-source and naming gaps).
Related Functional Requirements: FR-003, FR-006, FR-011 (directly); FR-016 (as final validation).
Related Dependency IDs: DEP-001, DEP-002, DEP-003, DEP-015, DEP-018.
Related ADR: ADR-006, Rule OM-006, AI-010.
Related Technical Debt: TD-006 (indirectly, via CAP-004's and CAP-005's contribution to this aggregate property).
Scope Classification: in scope; this is the Baseline Acceptance Criterion this entire unit exists to close.

### P2-03-CAP-015 - Financial Compatibility

Scientific Purpose: preservation of every already-certified P1-03, P1-03.1, P1-04, P2-01, P2-02, and P2-02A financial-adjacent contract (the `entry_basis` pre-trade handoff, weighted-average Scale-In entry price, the P1-04 `RUNTIME_FAILURE_EVENT` non-mutation contract, and the P2-02A Position/Exposure separation), a cross-cutting, continuously-reverified constraint rather than a build target.
Current Runtime Evidence: none of the FRA's twenty requirements requires touching `run_engine/core/position.py`, `run_engine/core/trade_lifecycle.py`, or the `entry_basis` parameter shape (FRA Section 26, FR-019's Architectural Rationale); every already-certified contract remains fully intact at HEAD `815cd8a` (unchanged since P2-02A's own certification).
Current Status: COMPLETE.
Blocking Dependencies: none (this capability constrains every other capability rather than being gated by any of them).
Related Functional Requirements: FR-019.
Related Dependency IDs: DEP-016.
Related ADR: ADR-004, ADR-009, ADR-011.
Related Technical Debt: TD-001, TD-003 (referenced only as contracts to preserve, both already resolved or partially resolved by prior units, neither reopened here).
Scope Classification: in scope, as a constraint layer continuously applied to every other capability, not a build target.

## 8. Current Runtime Deficiencies

This section synthesizes the cross-cutting deficiency patterns identified across the fifteen capabilities in Section 7, answering each question the governing task poses directly.

**Which capability already exists completely?** CAP-001 (Event Realized PnL), CAP-009 (PerformanceEngine Financial Consumption), CAP-015 (Financial Compatibility). All three require no further work; each is already conformant to its full FRA/SDA target.

**Which capability exists only partially?** CAP-003, CAP-004, CAP-005, CAP-006, CAP-007, CAP-008, CAP-010, CAP-011, CAP-012, CAP-013, CAP-014 - eleven of fifteen. In every one of these eleven, the underlying scientific definition is already settled (Section 5); what remains is Computational Authority relocation (CAP-003, CAP-004), input-source correction (CAP-005), an unresolved naming/ownership assignment (CAP-006), a missing storage location plus a duplicated constant (CAP-007), or pending re-verification once upstream capabilities resolve (CAP-008, CAP-010, CAP-011, CAP-012, CAP-013, CAP-014).

**Which capability is missing completely?** CAP-002 (Cumulative Realized PnL), as an explicit information object. No other capability was found missing in this sense; every other PARTIAL capability has at least a storage location, a computation, or an already-correct Authoritative Owner assignment in place.

**Which capability is present only implicitly?** CAP-002's economic effect (the correct, tick-by-tick accumulation of Realized PnL) is fully present, but only as an unlabeled side effect of CAP-003's (Equity's) own running total, never as its own separately-observable object. No other capability in this analysis was found to exist only implicitly in this specific sense.

**Which capability is jointly fulfilled by multiple components?** CAP-004 (Peak Equity) is currently fulfilled - non-conformantly - by two components simultaneously (`CanonicalState.update_equity()` and `RiskEngine.check()`), the precise duplicate-ownership pattern ADR-006/ADR-007/Rule OM-007 prohibit. CAP-010 (RuntimeFailure Financial Consistency) is conformantly fulfilled jointly by two components for its already-certified portion (`PnLEngine`'s and `PerformanceEngine`'s independent, structurally identical guards). CAP-014 (Canonical Financial State) is, by its own aggregate nature, fulfilled jointly by every other capability's individual conformance.

**Which capability violates current Ownership rules (Rule OM-001 through OM-009)?** CAP-004 violates Rule OM-001 ("every runtime information object possesses exactly one Authoritative Owner" - read here, per ADR-006's own text, as extending to Computational Authority uniqueness for this cluster) via its dual computation. CAP-003 violates the Computational-Authority-uniqueness expectation ADR-005/ADR-006 establish for Equity. CAP-007 violates Rule OM-006 ("CanonicalState exclusively owns active runtime state") for the one value (Cumulative Realized PnL) it does not yet store at all.

**Which capability violates current Computational Authority assignment?** CAP-003 (Equity: `RunLoop` instead of `PnLEngine`), CAP-004 (Peak Equity: `CanonicalState` and `RiskEngine` jointly, instead of `PnLEngine` exclusively). CAP-002 has no Computational Authority to violate, since the object itself does not exist; this is recorded as an absence, not a misassignment.

**Which capability violates current Canonical Publication?** CAP-002 (no canonical key exists for Cumulative Realized PnL) and, derivatively, CAP-014 (the aggregate "exactly one canonical financial state" property, unmet while CAP-002 remains missing and CAP-003/CAP-004 remain non-conformant).

**Which capability violates Determinism?** None. The FRA and SDA both confirm the current system is deterministic and reproducible for identical lifecycle histories (FRA Section 21; SDA Section 13; P2-02A Final Certification Section 16). CAP-012 and CAP-013 are classified PARTIAL not because determinism is currently violated, but because this property has not yet been re-verified against the system CAP-002 through CAP-011 will produce once resolved - a pending-verification status, not a violation.

**Which capability violates Replay?** None, for the identical reason given for Determinism immediately above; CAP-012 is PARTIAL for the same pending-re-verification reason, not because replay is currently broken.

**Which capability violates ADR-005, ADR-006, or ADR-007?** ADR-005 ("PnLEngine SHALL become the exclusive Computational Authority for financial accounting... Realized PnL (cumulative)... Equity... Peak Equity"): violated by CAP-002 (absence), CAP-003 (Computational Authority), CAP-004 (Computational Authority). ADR-006 ("CanonicalState SHALL become the Authoritative Owner of all financial runtime state... RiskEngine SHALL calculate Drawdown exclusively from canonical financial state... RiskEngine SHALL never own financial runtime information"): violated by CAP-002 (no Authoritative Owner location), CAP-004 (RiskEngine's competing tracker), CAP-005 (Drawdown's wrong input source). ADR-007 ("RiskEngine SHALL never own: ... Equity, Peak Equity"): violated by CAP-004 directly and CAP-008 derivatively (the read-only boundary cannot be fully verified while CAP-004 remains open).

## 9. Capability Gap Catalogue

For every non-COMPLETE capability, Current Capability, Target Capability, Gap Description, and Scientific Consequence are recorded below. COMPLETE capabilities (CAP-001, CAP-009, CAP-015) have no gap and are omitted from this catalogue by construction; their Section 7 entries record their already-satisfied state in full.

**P2-03-CAP-002 - Cumulative Realized PnL**
Current Capability: an implicit, unlabeled economic effect entangled inside Equity's running total; no explicit object exists.
Target Capability: a canonical, separately-owned, separately-observable value, computed exclusively by `PnLEngine`, stored under its own `CanonicalState` key.
Gap Description: complete absence of the information object itself, not a partial or misassigned implementation.
Scientific Consequence: ADR-005's five-value Computational Authority mandate cannot be fully satisfied; ADR-006's three-term Equity formula cannot be independently verified, since one of its three terms is not separately observable (FRA Section 13, Gap 2).

**P2-03-CAP-003 - Equity Ownership**
Current Capability: computed by `RunLoop`, stored correctly by `CanonicalState`.
Target Capability: computed exclusively by `PnLEngine`, stored by `CanonicalState` (unchanged storage assignment).
Gap Description: Computational Authority misassignment; Authoritative Owner assignment already correct and must not be disturbed by the fix.
Scientific Consequence: ADR-005's and ADR-006's textual, repeated Computational Authority mandate for Equity is directly and currently violated; this is the single most severe non-conformance this analysis identifies.

**P2-03-CAP-004 - Peak Equity Ownership**
Current Capability: computed independently, non-conformantly, by two components (`CanonicalState.update_equity()` and `RiskEngine.check()`), agreeing today only by coincidence of the synchronous execution model.
Target Capability: computed exclusively by `PnLEngine`; `RiskEngine` retains no independent tracking of this value in any form.
Gap Description: duplicate Computational Authority, the precise shape of TD-006.
Scientific Consequence: violates ADR-006's Computational Authority mandate and ADR-007's explicit ownership prohibition simultaneously; the current numeric agreement is an unenforced coincidence, not an architectural guarantee, and could silently diverge under any future change to either tracker or to `RiskEngine`'s invocation ordering.

**P2-03-CAP-005 - Drawdown Ownership**
Current Capability: computed correctly by `RiskEngine` (the correct Computational Authority component) but from its own non-canonical, internally-tracked Peak Equity copy.
Target Capability: computed by `RiskEngine` exclusively from `CanonicalState`'s own canonical Equity and Peak Equity.
Gap Description: input-source violation on an otherwise correctly-assigned Computational Authority.
Scientific Consequence: violates ADR-006's explicit text ("RiskEngine SHALL calculate Drawdown exclusively from canonical financial state"); Drawdown's correctness today depends on CAP-004's coincidental, not guaranteed, agreement.

**P2-03-CAP-006 - Drawdown Ratio Ownership**
Current Capability: computed and stored, sharing CAP-005's exact input-source profile, but with no ADR-level ownership definition at all.
Target Capability: an explicit Computational Authority and Authoritative Owner assignment, stated by a future Architecture document.
Gap Description: absent scientific-ownership definition, not an implementation defect per se.
Scientific Consequence: this value cannot be certified conformant or non-conformant to any ADR, since no ADR names it; it is presently classified only by proximity to Drawdown and by category to Risk Metrics.

**P2-03-CAP-007 - Canonical Financial Publication**
Current Capability: five of six financial values correctly published; Cumulative Realized PnL has no storage location; Initial Capital duplicated across two components.
Target Capability: all six financial values published under their own distinct `CanonicalState` key; a single, explicit Initial Capital source.
Gap Description: one missing storage location (contingent on CAP-002); one undeclared, duplicated constant.
Scientific Consequence: ADR-006's Acceptance Criterion ("CanonicalState contains exactly one canonical financial state") is not yet fully met; the duplicated Initial Capital literal is an "undeclared, silent coupling" of the same kind TD-006 already diagnosed for Peak Equity, though not itself logged as TD-006.

**P2-03-CAP-008 - RiskEngine Financial Consumption**
Current Capability: mechanically read-only for Equity; not verifiably read-only for Peak Equity while CAP-004 remains open.
Target Capability: strictly read-only for both, with no independent instance-level tracking of either surviving across calls.
Gap Description: boundary undermined in substance, though not in the specific mechanism of the current read.
Scientific Consequence: ADR-007's "Risk Evaluation does not create runtime truth" cannot be fully certified until CAP-004 closes; this capability's own resolution is a direct, automatic consequence of CAP-004's and CAP-005's resolution, not an independent fix.

**P2-03-CAP-010 - RuntimeFailure Financial Consistency**
Current Capability: correctly certified for Realized PnL (event) and `PerformanceEngine.stats`; unverifiable for Cumulative Realized PnL and relocated Equity/Peak-Equity, since those do not yet exist in target form.
Target Capability: the identical non-mutation contract, extended to every financial value this unit relocates or creates.
Gap Description: re-verification gap, not a known or suspected defect; the already-certified portion is not itself in question.
Scientific Consequence: ADR-011's non-mutation guarantee cannot be extended to the new/relocated values until they exist; deferring this re-verification until after CAP-002/CAP-003/CAP-004 resolve is scientifically necessary, not optional.

**P2-03-CAP-011 - Reset Consistency**
Current Capability: `CanonicalState`'s own fields reset correctly; `RiskEngine` has no reset mechanism at all, a latent (not presently-triggered) inconsistency.
Target Capability: every component holding financial-adjacent state, canonical or instance-local, reports values consistent with a freshly-initialized runtime after a full reset.
Gap Description: incomplete reset inventory, contingent on CAP-004's final disposition of `RiskEngine`'s own instance state.
Scientific Consequence: AI-010's "internally consistent... at all times" invariant would be violated on the first tick following any future reset call, if one is ever introduced, unless this gap closes alongside CAP-004.

**P2-03-CAP-012 - Replay Consistency**
Current Capability: certified for the current, pre-P2-03 system (P2-02A Final Certification Section 16).
Target Capability: re-certified for the system CAP-002 through CAP-011 will produce.
Gap Description: pending re-verification, not a known defect.
Scientific Consequence: none currently; this capability's closure is a downstream validation step, automatically achievable once its eleven prerequisite capabilities resolve, per SDA DEP-015.

**P2-03-CAP-013 - Financial Determinism**
Current Capability: identical to CAP-012.
Target Capability: identical to CAP-012.
Gap Description: identical to CAP-012.
Scientific Consequence: identical to CAP-012.

**P2-03-CAP-014 - Canonical Financial State**
Current Capability: an aggregate property, currently false, since it requires CAP-002 through CAP-006 to each individually conform.
Target Capability: true, once every constituent capability individually conforms.
Gap Description: an emergent gap, not independently fixable; closes automatically and only once its constituents close.
Scientific Consequence: ADR-006's own Acceptance Criterion remains formally unmet as a whole, even though five of its six constituent values are individually correct in at least their storage location.

## 10. Current vs Target Matrix

| Capability ID | Current | Target | Gap | Consequence |
|---|---|---|---|---|
| CAP-002 | Implicit effect only, inside Equity | Explicit canonical object | Object absent | ADR-005 five-value mandate, ADR-006 formula unverifiable |
| CAP-003 | RunLoop computes; CanonicalState stores | PnLEngine computes; CanonicalState stores | Computational Authority | ADR-005/006 direct violation |
| CAP-004 | CanonicalState and RiskEngine, both, independently | PnLEngine exclusively | Duplicate Computational Authority | ADR-006/007 violation; TD-006 |
| CAP-005 | RiskEngine, from own tracked copy | RiskEngine, from canonical state | Input source | ADR-006 explicit text violation |
| CAP-006 | Computed/stored, no ADR ownership | Explicit ADR-level ownership assignment | Definitional | Uncertifiable against any ADR |
| CAP-007 | 5/6 keys correct; 1 missing; Initial Capital duplicated | 6/6 keys; single Initial Capital source | Storage + duplication | ADR-006 Acceptance Criterion unmet |
| CAP-008 | Mechanically read-only for Equity only | Strictly read-only for Equity and Peak Equity | Boundary undermined by CAP-004 | ADR-007 not fully certifiable |
| CAP-010 | Certified for event-PnL/PerformanceEngine only | Certified for all relocated/new values | Re-verification pending | ADR-011 scope incomplete |
| CAP-011 | CanonicalState resets; RiskEngine does not | Complete, consistent reset scope | Incomplete inventory | AI-010 latent violation risk |
| CAP-012 | Certified for pre-P2-03 system | Certified for post-P2-03 system | Re-verification pending | none currently; downstream step |
| CAP-013 | Certified for pre-P2-03 system | Certified for post-P2-03 system | Re-verification pending | none currently; downstream step |
| CAP-014 | False (aggregate) | True (aggregate) | Emergent, non-independent | ADR-006 Acceptance Criterion unmet as a whole |

CAP-001, CAP-009, and CAP-015 are omitted from this matrix, being already at target with no recorded gap (Section 7).

## 11. Dependency Interaction

Every non-COMPLETE capability's Blocking Dependencies (Section 7) trace directly to the SDA's own Dependency Graph (SDA Section 17); no new dependency is introduced by this document. The interaction pattern confirms the SDA's own single-center structure (SDA Section 20): CAP-003 and CAP-004 (both within SDA Cluster B, Financial Ownership) are the two capabilities with no upstream blocking dependency of their own, and both directly or transitively gate every other non-COMPLETE capability in this catalogue:

- CAP-003 gates CAP-002's formula-consistency half (via DEP-005), CAP-010's Equity-relocation re-verification (via DEP-011), and CAP-012/CAP-013's final validation (via DEP-015).
- CAP-004 gates CAP-005 (via DEP-007/DEP-008), CAP-008 (via DEP-009), CAP-011 (via DEP-012), and, through CAP-005, CAP-008 a second time.
- CAP-002 (itself gated by nothing) gates CAP-007's value-correctness half (via DEP-003), CAP-014's aggregate closure (via DEP-003, DEP-004), and CAP-010's cumulative-PnL re-verification (via DEP-010).
- CAP-006 and the Initial-Capital half of CAP-007 (via FR-017) remain ungated, confirmed independently resolvable at any point (SDA Section 21, "not bound to any specific stage").
- CAP-015 (Financial Compatibility) constrains every capability above without being gated by any of them, exactly as SDA Cluster H (DEP-016) describes.

No capability interaction was found in this analysis that contradicts or extends the SDA's own Dependency Graph; this section is a capability-level restatement of that graph, not a new derivation.

## 12. Capability Readiness

**Capabilities requiring no further work (already at target):** CAP-001, CAP-009, CAP-015. Nothing further is required for these three specifically.

**Capabilities that are implementation-ready without any further Architecture-stage decision:** No remaining non-complete capability is implementation-ready without the Architecture phase. Every non-COMPLETE capability requires at least one Architecture-stage interface or mechanism decision before implementation can begin, even though the underlying ownership requirement itself is unambiguous in every case (Section 5). This is a direct, capability-level restatement of the SDA's own finding that seven Open Questions remain CONDITIONALLY BLOCKING (SDA Section 15): the requirement "PnLEngine SHALL become the exclusive Computational Authority for Equity" (CAP-003) is not in question, but exactly how `PnLEngine` receives the prior Equity value and returns the new one (OQ-004) is.

**Capabilities that require an Architecture decision first, and which decision:** CAP-002 requires OQ-001 (accumulation mechanism) and OQ-002 (publish interface shape). CAP-003 requires OQ-003 (storage-versus-projection) and OQ-004 (exact Computational Authority mechanism). CAP-004 requires OQ-005 (exact mechanism) and OQ-006 (whether `RiskEngine.self.peak_equity` is fully removed or retained transiently). CAP-005 shares OQ-006 with CAP-004. CAP-006 requires an entirely new ownership assignment decision (no OQ currently proposes an answer, only records the question, FR-012). CAP-007's Initial-Capital half is informed, softly, by CAP-004's OQ-006 resolution (DEP-014). CAP-011 requires OQ-006 (indirectly, via CAP-004) and OQ-009 (exact reset semantics for the new cumulative field).

**Capabilities that depend exclusively on already-known Open Questions (no new OQ required):** all twelve non-COMPLETE capabilities. No capability in this analysis was found to require an Open Question beyond the twelve the FRA already records (Section 13 below confirms this explicitly).

**Capabilities that possess no remaining scientific blocker, only implementation-detail questions:** CAP-002, CAP-003, CAP-004, CAP-005, CAP-007, CAP-008, CAP-010, CAP-011, CAP-012, CAP-013, CAP-014 - eleven of twelve non-COMPLETE capabilities. Every one of their governing ADRs already resolves the underlying scientific question (Section 5); only interface shape, exact mechanism, or re-verification timing remain open. The single exception is CAP-006, whose remaining question (Drawdown Ratio's ownership) is genuinely scientific/definitional, not merely a matter of implementation detail, since no ADR currently names an answer at all.

## 13. Open Question Interaction

Every capability's remaining work maps to at least one of the FRA's twelve already-recorded Open Questions (OQ-001 through OQ-012); no new Open Question was identified by this analysis.

| Open Question | SDA Classification | Interacting Capabilities |
|---|---|---|
| OQ-001 (cumulative-PnL accumulation mechanism) | CONDITIONALLY BLOCKING | CAP-002 |
| OQ-002 (event/cumulative publish interface shape) | NON-BLOCKING | CAP-002 |
| OQ-003 (Equity storage versus projection) | CONDITIONALLY BLOCKING | CAP-003 |
| OQ-004 (Equity Computational Authority mechanism) | CONDITIONALLY BLOCKING | CAP-003 |
| OQ-005 (Peak Equity Computational Authority mechanism) | CONDITIONALLY BLOCKING | CAP-004 |
| OQ-006 (RiskEngine.self.peak_equity full removal versus transient retention) | CONDITIONALLY BLOCKING | CAP-004, CAP-005, CAP-011 |
| OQ-007 (TD-006 P2-03/P2-04 boundary) | CONDITIONALLY BLOCKING | CAP-004, CAP-005 |
| OQ-008 (Financial Events required) | NON-BLOCKING | none directly (no capability's Validation Condition requires a Financial Event object; recorded for completeness only) |
| OQ-009 (Cumulative-PnL reset semantics) | CONDITIONALLY BLOCKING | CAP-007, CAP-011 |
| OQ-010 (RiskEngine parameter naming) | NON-BLOCKING | none (purely cosmetic) |
| OQ-011 (Drawdown Ratio's own future FR-ID) | NON-BLOCKING | CAP-006 |
| OQ-012 (PositionSizingEngine forward-compatibility note) | DEFERRED | none directly (contingent on a not-currently-anticipated future decision) |

No objectively new scientific question was found during this capability-level analysis beyond what the FRA and SDA already recorded. The closest candidate considered and rejected as genuinely new: whether Drawdown Ratio's eventual ownership assignment (CAP-006, FR-012) should be resolved independently of or jointly with Cumulative Realized PnL's naming (CAP-002, FR-002/FR-004) - this was found to already be implicitly covered by the FRA's own OQ-011 ("Should Drawdown Ratio be assigned its own P2-03-FR-level requirement number... or does it remain permanently subsumed under the general Risk Metrics Matrix row?") and does not constitute a distinct new question.

## 14. Technical Debt Interaction

| Technical Debt Item | Interaction Classification | Rationale |
|---|---|---|
| TD-001 (Canonical Position Source for PnLEngine) | Unverandert (unchanged) | Resolved by P2-02A; referenced only by CAP-015 as a contract to preserve; not reopened, not touched by any capability's gap. |
| TD-002 (Unify `_safe_float` implementations) | Ausserhalb des Scopes | `PnLEngine` has no `_safe_float` method of its own (FRA Section 27); no capability in this analysis implicates this item. |
| TD-003 (Document Pre-Trade Snapshot Dependency) | Unverandert (unchanged) | Partially Resolved by P2-02A; referenced only by CAP-015 as a contract to preserve; not reopened. |
| TD-004 (Lifecycle-based Performance Evaluation) | Ausserhalb des Scopes | `PerformanceEngine`'s statistics model (CAP-009) is unaffected by any capability's gap in this analysis. |
| TD-005 (Automated Regression Test Suite) | Ausserhalb des Scopes | Project-wide, explicitly excluded by both the FRA and SDA; no capability targets it. |
| TD-006 (RiskEngine Peak Equity and Drawdown Ownership Duplication) | Betroffen (directly affected) | See objective analysis below. |
| TD-007 (RunLoop Lifecycle Control Surface) | Ausserhalb des Scopes | Unrelated to Financial Ownership; no capability in this analysis references it. |

**Objective analysis of TD-006.** TD-006's own recorded description ("RiskEngine independently maintains peak equity and computes drawdown instead of consuming the CanonicalState-owned values, creating duplicate ownership contrary to ADR-006 and ADR-007") is, on direct comparison, an exact match for the combined non-conformance this analysis records under CAP-004 (Peak Equity Ownership, PARTIAL, duplicate Computational Authority) and CAP-005 (Drawdown Ownership, PARTIAL, wrong input source). No other capability in this fifteen-item catalogue implicates TD-006; CAP-003 (Equity)'s non-conformance is a separate, textually distinct ADR-005/ADR-006 violation (Computational Authority located in `RunLoop`, not `RiskEngine`) not previously logged under TD-006 at all. TD-006's register entry currently reads "Target Phase: P2-03 / P2-04," without further internal subdivision; this analysis does not subdivide or re-scope that entry, and does not change its Status field (still "Deferred" in the register). The FRA's own Open Question OQ-007 already records, without resolving, the precise boundary question this objective analysis surfaces again: whether TD-006's full closure (including any `RiskEngine` risk-formula implications beyond the narrow Equity/Peak-Equity/Drawdown-input-source scope CAP-004/CAP-005 name) belongs entirely to P2-03 or is partially P2-04's. This document takes no position beyond what the FRA and SDA already adopted (the Equity/Peak-Equity/Drawdown-input-source half is P2-03's, consistent with the Baseline objective's own explicit text); no Technical Debt Register file edit is made by this document, consistent with the FRA's and SDA's own practice.

## 15. Capability Traceability

| Capability ID | Related FR | Related DEP | Related ADR | Related TD |
|---|---|---|---|---|
| CAP-001 | FR-001 | DEP-018 | ADR-005 | none |
| CAP-002 | FR-002, FR-003, FR-004 | DEP-003, DEP-004, DEP-005, DEP-010 | ADR-005, ADR-006 | none |
| CAP-003 | FR-005, FR-006, FR-007 | DEP-001, DEP-005, DEP-011, DEP-013, DEP-015 | ADR-005, ADR-006 | none |
| CAP-004 | FR-008, FR-009 | DEP-006, DEP-007, DEP-008, DEP-009, DEP-011, DEP-014, DEP-017 | ADR-006, ADR-007 | TD-006 |
| CAP-005 | FR-010, FR-011 | DEP-002, DEP-007, DEP-008, DEP-009, DEP-017 | ADR-006 | TD-006 |
| CAP-006 | FR-012 | none | ADR-006, ADR-007 | none |
| CAP-007 | FR-003, FR-006, FR-011, FR-017 | DEP-001, DEP-002, DEP-003, DEP-014, DEP-018 | ADR-006 | none |
| CAP-008 | FR-013 | DEP-009 | ADR-007 | TD-006 |
| CAP-009 | FR-014 | DEP-018 | ADR-008 | none |
| CAP-010 | FR-015 | DEP-010, DEP-011 | ADR-011 | none |
| CAP-011 | FR-017, FR-018 | DEP-012, DEP-014 | AI-010 | none |
| CAP-012 | FR-016 | DEP-015 | ADR-005, ADR-006, AI-005 | none |
| CAP-013 | FR-016 | DEP-015 | ADR-005, ADR-006, AI-005 | none |
| CAP-014 | FR-003, FR-006, FR-011, FR-016 | DEP-001, DEP-002, DEP-003, DEP-015, DEP-018 | ADR-006, Rule OM-006, AI-010 | TD-006 |
| CAP-015 | FR-019 | DEP-016 | ADR-004, ADR-009, ADR-011 | TD-001, TD-003 |

## 16. FRA Traceability

Every one of the FRA's twenty functional requirements is covered by at least one capability above:

FR-001: CAP-001. FR-002: CAP-002. FR-003: CAP-002, CAP-007, CAP-014. FR-004: CAP-002. FR-005: CAP-003. FR-006: CAP-003, CAP-007, CAP-014. FR-007: CAP-003. FR-008: CAP-004. FR-009: CAP-004. FR-010: CAP-005. FR-011: CAP-005, CAP-007, CAP-014. FR-012: CAP-006. FR-013: CAP-008. FR-014: CAP-009. FR-015: CAP-010. FR-016: CAP-012, CAP-013, CAP-014. FR-017: CAP-007, CAP-011. FR-018: CAP-011. FR-019: CAP-015. FR-020: not directly mapped to any capability, since FR-020 is a scope-protection requirement (Unrealized PnL / Mark-to-Market Equity remaining explicitly out of scope) rather than a capability to be closed; it is recorded in Section 2 (Scope) as inherited out-of-scope protection, consistent with the FRA's own framing of FR-020 as "explicitly protected against silent scope expansion" rather than a build target.

All twenty FRA requirements are accounted for; nineteen map to at least one capability directly, and FR-020 is explicitly carried forward as a scope boundary rather than a capability.

## 17. SDA Traceability

Every one of the SDA's eighteen dependency records is referenced by at least one capability above:

DEP-001: CAP-003, CAP-007, CAP-014. DEP-002: CAP-005, CAP-007, CAP-014. DEP-003: CAP-002, CAP-007, CAP-014. DEP-004: CAP-002. DEP-005: CAP-002, CAP-003. DEP-006: CAP-004. DEP-007: CAP-004, CAP-005. DEP-008: CAP-004, CAP-005. DEP-009: CAP-004, CAP-005, CAP-008. DEP-010: CAP-002, CAP-010. DEP-011: CAP-003, CAP-004, CAP-010. DEP-012: CAP-011. DEP-013: CAP-003. DEP-014: CAP-004, CAP-007, CAP-011. DEP-015: CAP-003, CAP-012, CAP-013, CAP-014. DEP-016: CAP-015. DEP-017: CAP-004, CAP-005. DEP-018: CAP-001, CAP-007, CAP-009, CAP-014.

All eighteen SDA dependency records are accounted for; each is referenced by at least one capability's Related Dependency IDs field (Section 7, Section 15).

## 18. ADR Traceability

| ADR / Invariant / Rule | Related Capabilities |
|---|---|
| ADR-002 (Financial Events) | none directly (Section 11 of the FRA records their absence as an observation; no capability's Validation Condition requires them, consistent with OQ-008's NON-BLOCKING classification) |
| ADR-004 (Position Represents Current Market Exposure) | CAP-015 (compatibility preservation only) |
| ADR-005 (Profit and Loss Accounting) | CAP-001, CAP-002, CAP-003, CAP-012, CAP-013 |
| ADR-006 (Canonical Financial State Ownership) | CAP-002, CAP-003, CAP-004, CAP-005, CAP-006, CAP-007, CAP-012, CAP-013, CAP-014 |
| ADR-007 (Risk Evaluation as a Pure Computational Layer) | CAP-004, CAP-006, CAP-008 |
| ADR-008 (Performance Ownership) | CAP-009 |
| ADR-009 (Partial Trade Closure and Position Netting) | CAP-015 (compatibility preservation only) |
| ADR-010 (Deterministic Runtime Execution Ordering) | none directly; already-conformant ordering confirmed by FRA Section 12, not a capability gap |
| ADR-011 (Runtime Failure Handling) | CAP-010, CAP-015 |
| ADR-012 (Persistence, Recovery, Schema Evolution) | none; explicitly deferred scope, confirmed by FRA Section 24, not a capability in this catalogue |
| AI-005 (Deterministic Execution) | CAP-012, CAP-013 |
| AI-010 (Financial Consistency) | CAP-011, CAP-014 |
| Rule OM-006 (CanonicalState exclusively owns active runtime state) | CAP-007, CAP-014 |
| Rule OM-007 (RiskEngine owns no runtime information) | CAP-004, CAP-008 |
| Rule OM-008 (PerformanceEngine owns no operational runtime information) | CAP-009 |

Every ADR, Invariant, and Rule named as binding by the FRA (Section 3 of that document) and the SDA (Section 3 of that document) is accounted for above, either by direct capability association or by an explicit note confirming it is already satisfied, out of scope, or observation-only.

## 19. Technical Debt Traceability

All seven Technical Debt Register items are classified in Section 14: TD-001 (unverandert), TD-002 (ausserhalb des Scopes), TD-003 (unverandert), TD-004 (ausserhalb des Scopes), TD-005 (ausserhalb des Scopes), TD-006 (betroffen), TD-007 (ausserhalb des Scopes). No Technical Debt Register item is left unclassified. TD-006 additionally receives an explicit, objective, non-status-changing analysis (Section 14) as required by the governing task.

## 20. Overall Capability Readiness

Of fifteen financial capabilities: three are already COMPLETE (CAP-001, CAP-009, CAP-015), requiring no further work. One is MISSING as an explicit information object (CAP-002), though its economic effect is already correctly present, implicitly, inside an already-COMPLETE-adjacent capability (CAP-003). Eleven are PARTIAL, in every case because the underlying scientific definition is already settled (ADR-005/ADR-006/ADR-007) and only Computational Authority relocation, input-source correction, storage-location creation, consumption-boundary re-verification, or downstream re-validation remains.

No capability in this analysis was found to require a new scientific investigation beyond the FRA's and SDA's own twelve Open Questions (Section 13); no capability was found to require a new Technical Debt Register entry beyond TD-006, already logged (Section 14); no capability was found to contradict the SDA's own single-center dependency structure (Section 11). Exactly one capability (CAP-006, Drawdown Ratio Ownership) possesses a genuinely open scientific-definition question rather than a purely implementation-detail question, and this is the FRA's own already-recorded FR-012/OQ-011, not a new finding.

Readiness: READY. This document is sufficient to proceed to the P2-03 Architecture stage, where the twelve Open Questions this analysis and its predecessors have classified as CONDITIONALLY BLOCKING (OQ-001, OQ-003, OQ-004, OQ-005, OQ-006, OQ-007, OQ-009) must be resolved before Specification-level interface design can proceed for CAP-002, CAP-003, CAP-004, CAP-005, CAP-007, and CAP-011. No further Capability Gap investigation is required before that step.

## 21. Internal Consistency Review

Terminology consistency - "Capability," "Current Status," "Gap," "Target Capability," "COMPLETE," "PARTIAL," and "MISSING" are used exactly as defined in Section 5 throughout this document; every financial and dependency term used is inherited unchanged from the FRA's and SDA's own definitions, never redefined here.

Scope consistency - no capability entry proposes a formula, an interface shape, a storage mechanism, or a final ownership decision beyond what the FRA and SDA already establish; every Gap Description states what is non-conformant, not what should replace it. Section 2 confirms P2-04, P3-03, Financial-Events, Unrealized-PnL, repository-cleanup, and TD-005 topics all remain external, deferred, or future-compatibility items, consistent with the FRA and SDA.

Traceability consistency - all fifteen capabilities map to at least one FRA requirement (Section 16), at least one SDA cluster or dependency where applicable (Section 17), at least one ADR/Invariant/Rule (Section 18), and are explicitly classified against every Technical Debt Register item (Section 19); cross-checked capability by capability during drafting against Section 7's own Related-field entries.

Capability-ID uniqueness - P2-03-CAP-001 through P2-03-CAP-015 are each defined exactly once (Section 7) and referenced only by ID thereafter (Sections 8 through 20); no ID collision or reuse was introduced.

Status consistency - Section 6's summary table, Section 7's per-capability Current Status fields, Section 9's gap catalogue (which omits COMPLETE capabilities by construction), and Section 10's matrix (which likewise omits them) agree exactly: three COMPLETE, one MISSING, eleven PARTIAL.

Observation/gap/decision separation - Sections 4 and 5 contain only repository-grounded and FRA/SDA-grounded observations and the stated evaluation method. Section 7 contains only capability-level findings derived from those observations. Sections 8 through 10 synthesize and catalogue those findings without introducing new ones. Sections 11 through 14 map findings to the SDA's dependencies, readiness, Open Questions, and Technical Debt without resolving any of them. No architecture decision, formula selection, interface shape, or implementation detail is finalized anywhere in this document; no new Open Question is introduced (Section 13 explicitly confirms this); no Technical Debt Register status is changed (Section 14 explicitly confirms this).

No fabricated capability - every one of the fifteen capabilities traces to a specific FRA requirement, SDA dependency, or ADR text (Sections 16 through 18); no capability in this document assumes a state repository inspection did not confirm, consistent with the FRA's and SDA's own "No fabricated capability" consistency checks.

Status: Internal Consistency Review PASS.
