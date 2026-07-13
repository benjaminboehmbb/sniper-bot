Document Class:
Architecture Decision Document

Document ID:
P2-03-ARCH

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
docs/architecture/P2_03_FINANCIAL_OWNERSHIP_ARCHITECTURE_V1_2026-07-11.md

Depends On:
- docs/architecture/analysis/P2_03_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-11.md
- docs/architecture/analysis/P2_03_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-11.md
- docs/architecture/analysis/P2_03_CAPABILITY_GAP_ANALYSIS_V1_2026-07-11.md
- docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md
- docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md
- docs/architecture/certification/P2_02A_FINAL_CERTIFICATION_V1_2026-07-10.md
- docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md
- current runtime code at HEAD 815cd8a

Referenced By:
- future P2-03 Specification
- future P2-03 Implementation
- future P2-03 Certification

---

# P2-03 Financial Ownership Architecture

## 1. Purpose

This document makes the architecture decisions for P2-03 (Financial Ownership), resolving the ownership questions the P2-03 Functional Requirement Analysis (FRA), Scientific Dependency Analysis (SDA), and Capability Gap Analysis (CGA) established but deliberately left open. It decides, for every financial information object in scope, who computes it, who stores it, who may write it on whose behalf, who may read it, and what invariants the resulting design must uphold. It does not specify interfaces, method signatures, file layouts, or code; it does not implement anything; it does not modify any runtime file.

## 2. Scope

In scope: architecture decisions for Realized PnL (event), Realized PnL (cumulative), Equity, Peak Equity, Drawdown, and Drawdown Ratio, covering Computational Authority, Authoritative Ownership, Writer-on-Behalf-Of relationships, Canonical Publication, Financial Information Flow, Consumer Boundaries among `PnLEngine`, `RunLoop`, `CanonicalState`, `CanonicalEnforcer`, `RiskEngine`, and `PerformanceEngine`, State-versus-Event treatment, Derived Views, the architectural closure of TD-006, and Replay/Determinism invariants.

Out of scope, unchanged from the FRA (Section 24) and SDA (Section 2) and CGA (Section 2): RiskEngine's risk-limiting formula (`max_exposure`, `min_exposure`, `max_drawdown` thresholds, regime-dampening multipliers), Risk Policy, Position Sizing, PerformanceEngine's statistics model, Unrealized PnL and Mark-to-Market Portfolio Valuation, Multi-Asset Accounting, Fees/Funding/Slippage/Tax Accounting, Persistence, Recovery, repository cleanup, the automated regression test suite (TD-005), and any Specification-level interface shape or Implementation-level code. No decision in this document expands scope beyond what the FRA, SDA, and CGA already established as in scope.

## 3. Governing Baseline

- `docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md` - ADR-005 (Profit and Loss Accounting), ADR-006 (Canonical Financial State Ownership), ADR-007 (Risk Evaluation as a Pure Computational Layer), ADR-002 (Event-Driven Runtime Evolution, Financial Events), ADR-008 (Performance Ownership), ADR-010 (Deterministic Runtime Execution Ordering), ADR-011 (Runtime Failure Handling), ADR-004, ADR-009, the Runtime Ownership Matrix, Rules OM-001 through OM-009, Architecture Invariants AI-005 and AI-010.
- `docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md` - P2-03's unit definition ("Financial Ownership. Objectives: Implement PnLEngine ownership. Verify Realized PnL (cumulative). Verify Equity, Peak Equity and Drawdown consistency.").
- `docs/architecture/analysis/P2_03_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-11.md` - twenty functional requirements (FR-001 through FR-020), twelve Open Questions (OQ-001 through OQ-012), Functional Readiness: READY.
- `docs/architecture/analysis/P2_03_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-11.md` - eight capability clusters, eighteen dependency records (DEP-001 through DEP-018), Open Question classifications, seven Dependency Stages, Readiness for Capability Gap Analysis: READY.
- `docs/architecture/analysis/P2_03_CAPABILITY_GAP_ANALYSIS_V1_2026-07-11.md` - fifteen capabilities (CAP-001 through CAP-015), Current-vs-Target Matrix, TD-006 objective analysis, Overall Capability Readiness: READY.
- `docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md` - TD-001 through TD-007, in particular TD-006 (Deferred, Target Phase P2-03/P2-04).
- Current runtime code at HEAD `815cd8a`, re-verified for this document (Section 4).

## 4. Architectural Context

Repository state re-verified for this document: branch `run-engine-consolidation-safety`, HEAD `815cd8a`, matching the FRA's, SDA's, and CGA's own verification exactly. `run_engine/` remains clean. The nine runtime files named by the governing task (`pnl.py`, `loop.py`, `canonical_state.py`, `canonical_enforcer.py`, `risk.py`, `performance.py`, `trade_lifecycle.py`, `position.py`, `main.py`) were re-read in full for this document; no change since the CGA's own verification was found.

The CGA's own central finding (CGA Section 5) governs this document's starting position: every financial object's scientific definition is already settled by ADR-005 and ADR-006; three capabilities are already COMPLETE (Event Realized PnL, PerformanceEngine Consumption, Financial Compatibility), one is MISSING as an explicit object (Cumulative Realized PnL), and eleven are PARTIAL, in every case because Computational Authority, input source, storage completeness, or consumption boundary has not yet been operationally aligned with an already-settled definition. Architecture, in this document, therefore consists overwhelmingly of ownership-relocation decisions rather than new scientific definitions - the one genuine exception being Drawdown Ratio (CAP-006, FR-012), whose ownership no ADR previously assigned at all.

`PositionEngine.update_post_trade()` (`run_engine/core/position.py:37-73`) and `TradeLifecycleEngine` already establish two precedents this document draws on directly: (1) a Computational Authority component receiving the prior canonical value explicitly as an input parameter, rather than retaining its own persisted copy of canonical state, and returning a fresh snapshot each call; (2) a component's own instance state being scoped strictly to values no other component owns (`PositionEngine`'s `self.position`/`self.quantity`/etc. are themselves the Authoritative Owner for Position, not a duplicate of a `CanonicalState`-owned value). These two precedents inform this document's central design principle: `PnLEngine`, once it becomes Computational Authority for Equity, Peak Equity, and cumulative Realized PnL, must not retain its own persisted copy of these now-canonical values as instance state, since doing so would recreate - one level higher up - exactly the duplicate-ownership pattern TD-006 names for `RiskEngine`'s Peak Equity today.

## 5. Financial Information Objects

| Object | Current Computational Authority | Current Authoritative Owner | Current Status (CGA) |
|---|---|---|---|
| Realized PnL (event) | PnLEngine | not independently stored (tick-scoped return value, published via CanonicalState `pnl` key) | COMPLETE |
| Realized PnL (cumulative) | none (object does not exist) | none (object does not exist) | MISSING |
| Equity | RunLoop (non-conformant) | CanonicalState | PARTIAL |
| Peak Equity | CanonicalState and RiskEngine (dual, non-conformant) | CanonicalState (storage location correct) | PARTIAL |
| Drawdown | RiskEngine (correct component, wrong input source) | CanonicalState | PARTIAL |
| Drawdown Ratio | RiskEngine (mirrors Drawdown; no ADR assigns it) | CanonicalState | PARTIAL |

This table restates CGA Section 6/Section 7 findings as the starting position for the decisions in Section 7.

## 6. Financial Information Flow

Target flow, per tick, following AD-001 through AD-011 (Section 7): `RunLoop.step()` obtains the current canonical financial state from `CanonicalState.get()`; passes the relevant prior canonical values (cumulative Realized PnL, Equity, Peak Equity) together with the current tick's `trade_event` and `entry_basis` to `PnLEngine`; `PnLEngine`, as sole Computational Authority, returns the new Realized PnL (event), Realized PnL (cumulative), Equity, and Peak Equity together; `RunLoop` passes each returned value to `CanonicalEnforcer`'s Writer-on-Behalf-Of methods, performing no arithmetic of its own; `CanonicalEnforcer` writes each value into `CanonicalState`, which remains the sole Authoritative Owner; `RunLoop` then passes the resulting canonical state to `RiskEngine`, which reads canonical Equity and Peak Equity exclusively, computes Drawdown and Drawdown Ratio, and returns them for `CanonicalEnforcer` to publish; `PerformanceEngine` continues to read only the tick's Realized-PnL-event value, unchanged. This flow preserves the current call ordering and cadence (`RunLoop` calls `PnLEngine` before `RiskEngine`, every tick, matching AI-005/ADR-010's already-established Deterministic Execution Ordering) while relocating every computation to its architecturally correct owner.

## 7. Architectural Decisions

### P2-03-AD-001 - Computational Authority for Realized PnL (Event and Cumulative)

Problem: Realized PnL (event) is already correctly computed by `PnLEngine` (CAP-001, COMPLETE). Realized PnL (cumulative) has no Computational Authority at all; its economic effect exists only implicitly, entangled inside `RunLoop`'s own Equity accumulation (CAP-002, MISSING; FRA Section 13, Gap 2).

Decision: `PnLEngine` becomes, and remains, the exclusive Computational Authority for both Realized PnL (event) and Realized PnL (cumulative). Cumulative Realized PnL is computed by incremental accumulation - each tick's new cumulative value equals the prior canonical cumulative value plus the current tick's event-PnL - not by re-summation of full trade history on every tick. `PnLEngine` receives the prior canonical cumulative value as an explicit input each call and returns the new cumulative value; it does not retain its own persisted copy of the canonical cumulative total as instance state across ticks.

Scientific Rationale: ADR-005 names `PnLEngine` as the exclusive Computational Authority for exactly five values, including Realized PnL (event) and Realized PnL (cumulative).

Architectural Rationale: incremental accumulation matches the arithmetic `RunLoop` already performs today (`equity = self.cstate.get()["equity"] + pnl`, `run_engine/core/loop.py:71`) and preserves exact numeric equivalence under relocation (Section 16). Requiring `PnLEngine` to receive the prior value explicitly, rather than retaining it internally, applies the same architectural principle AD-005 applies to `RiskEngine`: a Computational Authority for a canonical value does not require a private, persisted copy of that value, since the canonical copy is available as an explicit input on every call; retaining one would recreate TD-006's duplicate-ownership pattern one level up.

Alternatives Considered: (a) `CanonicalState` reconstructs the cumulative total itself by summing incoming event-PnL values - rejected, this would make `CanonicalState` perform financial computation, contradicting ADR-006's storage-only role and Rule OM-006. (b) `RunLoop` continues to accumulate the running total, as it already does for Equity today - rejected, this is the exact non-conformance pattern this unit exists to close, merely extended to a second value. (c) `PnLEngine` retains the cumulative total as its own persisted instance attribute, publishing it but not receiving it as an input - rejected per the Architectural Rationale above.

Consequences: `PnLEngine`'s computation becomes a pure function of its explicit inputs (prior canonical cumulative value, current tick's `trade_event`, `entry_basis`) rather than a function of hidden internal state; `RunLoop` must retrieve the prior canonical cumulative value from `CanonicalState` before calling `PnLEngine` (Section 6).

Related FRA: FR-001, FR-002, FR-003, FR-004.
Related SDA: DEP-003, DEP-004, DEP-005, DEP-010, DEP-018.
Related Capability: CAP-001, CAP-002.
Related ADR: ADR-005.
Related Technical Debt: none.

### P2-03-AD-002 - Authoritative Ownership and Canonical Publication for Cumulative Realized PnL

Problem: no storage location for cumulative Realized PnL currently exists anywhere in `CanonicalState` (CGA CAP-002, CAP-007).

Decision: `CanonicalState` becomes the exclusive Authoritative Owner of cumulative Realized PnL, gaining exactly one new top-level key for it (exact key name a Specification-stage decision, not decided here). This key is written exclusively by `CanonicalEnforcer` on `PnLEngine`'s behalf (AD-010), never directly by `RunLoop` or `PnLEngine`.

Scientific Rationale: ADR-006 designates `CanonicalState` as the Authoritative Owner of all financial runtime state.

Architectural Rationale: extends the already-established pattern of `CanonicalState`'s existing `pnl`, `equity`, `peak_equity`, `drawdown`, `drawdown_ratio` keys to the one financial value currently missing a storage location, keeping all financial state under one schema rather than introducing a second storage location for financial values.

Alternatives Considered: (a) storing cumulative Realized PnL only as a derived-on-demand recomputation from full trade history rather than as a canonical key - rejected under AD-013 (Derived View Scope Restriction), since `PnLEngine` already computes it incrementally each tick under AD-001, making on-demand recomputation redundant and a second, competing computation path. (b) storing it as a nested field under the existing `pnl` key rather than a new top-level key - left open as a Specification-stage schema-shape decision, not resolved here.

Consequences: `CanonicalState`'s schema grows by one key; `CanonicalState.reset()` must zero this key (AD-014); every consumer that reads `CanonicalState.get()` gains access to this value without needing a separate accessor.

Related FRA: FR-003, FR-006 (indirectly), FR-011 (indirectly), FR-017.
Related SDA: DEP-001, DEP-002, DEP-003, DEP-014, DEP-018.
Related Capability: CAP-002, CAP-007, CAP-014.
Related ADR: ADR-006, Rule OM-006.
Related Technical Debt: none.

### P2-03-AD-003 - Computational Authority, Mechanism, and Storage Model for Equity

Problem: `RunLoop` currently computes Equity itself (`run_engine/core/loop.py:71`), not `PnLEngine`, the single most severe non-conformance this governance chain has identified (CGA CAP-003; FRA Section 16).

Decision: `PnLEngine` becomes the exclusive Computational Authority for Equity. `PnLEngine` gains a dedicated computation responsibility, distinct from its existing event-PnL computation, that runs every tick regardless of event type (mirroring the fact that Equity must remain current even on `HOLD` ticks, exactly as it does today via the `+ pnl` pattern where `pnl` is `0.0` on non-closing ticks). This dedicated responsibility receives the prior canonical Equity value together with the current tick's Realized PnL (event) (from AD-001) as explicit inputs, updates Equity according to the governing reconstruction rule, and returns the new Equity value; it is not folded into the same method call that computes event-PnL as an implicit side effect, since the two computations are triggered by different runtime conditions (event-PnL only on `TRADE_CLOSED`/`PARTIAL_CLOSE`; Equity every tick) and ADR-005 already treats them as five separately-named values. `RunLoop`'s role is reduced to orchestration: it retrieves the prior canonical Equity value, invokes `PnLEngine`, and passes the returned value to `CanonicalEnforcer.apply_equity()` unchanged; `RunLoop` performs no arithmetic on Equity.

Equity remains a stored canonical quantity (resolving OQ-003), not a value recomputed on demand from scratch on every read, consistent with FR-006's explicit requirement and with the storage location already in place today. Its stored value is bound by a reconstruction rule - Equity equals Initial Capital plus Realized PnL (cumulative) plus Unrealized PnL - that `PnLEngine` enforces at computation time on every write, mirroring the "stored-with-binding-reconstruction-rule" pattern (Option C) the P2-02A Architecture already established for Exposure. Since Unrealized PnL is confirmed absent and remains explicitly out of scope (FR-020), the reconstruction rule's third term is definitionally zero for the duration of this unit; this decision does not implement Unrealized PnL and does not require any code change to accommodate it.

Scientific Rationale: ADR-005's and ADR-006's Decision and Acceptance Criteria sections both explicitly and repeatedly name `PnLEngine` as Equity's Computational Authority.

Architectural Rationale: separating event-PnL computation from Equity computation preserves ADR-005's own five-value separation of concerns and avoids overloading a single method with two computations that fire under different conditions; requiring explicit prior-value input rather than internal persistence follows the same non-duplication principle as AD-001 and mirrors `PositionEngine.update_post_trade()`'s already-established pattern of receiving prior state explicitly.

Alternatives Considered: (a) `PnLEngine.update()`'s existing method implicitly computes and returns Equity as a byproduct of computing event-PnL - rejected, this would make Equity's computation conditional on the same event-type gate that correctly restricts event-PnL to closing events only, incorrectly suppressing Equity updates on non-closing ticks. (b) Equity becomes a fully computed-on-demand projection with no stored value at all - rejected (OQ-003), since FR-006 explicitly requires it to remain a stored canonical quantity, and every current consumer already depends on reading it directly from `CanonicalState` without recomputation. (c) `RiskEngine` remains a secondary computer of Equity for its own internal use - rejected, this is the precise CAP-004/TD-006 pattern being eliminated, not extended to a new value.

Consequences: `RunLoop` no longer performs any Equity arithmetic; `PnLEngine` gains a second distinct computation responsibility beyond event-PnL, called every tick rather than only on closing events; the literal method signature and call shape for this responsibility (single combined call versus separate calls) remain Specification-stage (OQ-004's literal-interface component, explicitly not decided here - see Section 21).

Related FRA: FR-005, FR-006, FR-007.
Related SDA: DEP-001, DEP-005, DEP-011, DEP-013, DEP-015.
Related Capability: CAP-003.
Related ADR: ADR-005, ADR-006.
Related Technical Debt: none.

### P2-03-AD-004 - Computational Authority and Mechanism for Peak Equity

Problem: Peak Equity is currently computed independently and non-conformantly by two components (`CanonicalState.update_equity()` and `RiskEngine.check()`), agreeing today only by coincidence of the synchronous execution model, not by architectural guarantee (CGA CAP-004; this is TD-006's Peak-Equity half).

Decision: `PnLEngine` becomes the exclusive Computational Authority for Peak Equity, computed as a direct byproduct of its own Equity computation (AD-003) within the same dedicated responsibility: `PnLEngine` receives the prior canonical Peak Equity as an additional explicit input alongside Equity's own prior value, and returns the new Peak Equity as `max(prior_peak_equity, new_equity)` together with the new Equity value. No other component computes or compares against Peak Equity to produce a new value; `CanonicalState.update_equity()`'s own internal max-comparison (`run_engine/core/canonical_state.py:64-65`) and `RiskEngine`'s independent tracking (AD-005) are both superseded by this single computation.

Scientific Rationale: ADR-006 names Peak Equity among the values requiring a single, unique Computational Authority; ADR-007 explicitly prohibits `RiskEngine` from owning Peak Equity in any form.

Architectural Rationale: computing Peak Equity as an immediate byproduct of Equity, within the same Computational Authority and the same call, is the only design that structurally forecloses a second, independently-drifting comparison from ever re-emerging, since there is no longer a second component positioned to perform the comparison at all.

Alternatives Considered: (a) `CanonicalState` performs the max-comparison itself upon receiving a new Equity value from `PnLEngine`, as it already does today - rejected, this would make `CanonicalState` a Computational Authority for Peak Equity, not merely its Authoritative Owner, contradicting ADR-006's separation of these two roles. (b) `RiskEngine` remains the Computational Authority for Peak Equity, since it already computes Drawdown from it - rejected, ADR-007 explicitly prohibits this ownership assignment regardless of convenience.

Consequences: `CanonicalState.update_equity()`'s internal max-comparison responsibility is superseded; `CanonicalState`'s role for Peak Equity becomes storage-only, receiving an already-computed value via `CanonicalEnforcer` rather than computing it on write. This decision, together with AD-005, constitutes this document's architectural closure of TD-006's Peak-Equity half (Section 18).

Related FRA: FR-008, FR-009.
Related SDA: DEP-006, DEP-007, DEP-008, DEP-009, DEP-011, DEP-014, DEP-017.
Related Capability: CAP-004.
Related ADR: ADR-006, ADR-007.
Related Technical Debt: TD-006.

### P2-03-AD-005 - Removal of RiskEngine's Persisted Peak-Equity and Equity Instance State

Problem: `RiskEngine.__init__` hardcodes `self.last_equity = 100.0` and `self.peak_equity = 100.0` (`run_engine/core/risk.py:9-10`), and `RiskEngine.check()` compares against and updates `self.peak_equity` internally (`run_engine/core/risk.py:21-22,51`), never reading `CanonicalState`'s own `peak_equity` key at all. This is TD-006 and OQ-006's subject.

Decision: `RiskEngine.__init__`'s `self.last_equity` and `self.peak_equity` instance attributes are removed entirely, not retained even as transient per-call-scoped locals beyond the lifetime of a single `check()` invocation. `RiskEngine.check()` reads Equity and Peak Equity exclusively from the canonical state dict it already receives as its `state` parameter on every call, with no value surviving from one call to the next as instance state.

Scientific Rationale: ADR-006 requires `RiskEngine` to calculate Drawdown exclusively from canonical financial state; ADR-007 states `RiskEngine` shall never own Equity or Peak Equity in any form, including transient internal tracking that duplicates canonical storage.

Architectural Rationale: full removal, rather than transient per-call retention, is the simpler design with no loss of function, since `RiskEngine` already receives the full canonical state dict as an argument on every call and therefore has no need to remember a value between calls; retaining any instance-level copy - even one nominally called "transient" - reintroduces the exact possibility of divergence TD-006 already demonstrates, since nothing would structurally prevent it from becoming persistent again over time. This resolves OQ-006 in favor of full removal.

Alternatives Considered: (a) retain `self.peak_equity` as a transient, per-call local variable only, reset from canonical state at the start of every `check()` call - rejected, since this variable would be functionally redundant (canonical state already supplies the value) while still occupying the conceptual space where the original defect grew; full removal is strictly simpler. (b) retain the instance attributes as a defensive fallback for cases where `state` might not contain `peak_equity` - rejected, since `CanonicalState` is the exclusive Authoritative Owner and always populates this key from initialization onward (`run_engine/core/canonical_state.py:30`), making a fallback unnecessary and itself a form of undeclared duplicate ownership.

Consequences: `RiskEngine` becomes fully stateless with respect to Equity, Peak Equity, Drawdown, and Drawdown Ratio - every value is read fresh from its `state` parameter and returned fresh each call, with no cross-tick persistence of any kind. This directly satisfies AD-014's Reset Consistency requirement for `RiskEngine` without requiring `RiskEngine` to gain a `reset()` method of its own, since there is no longer any instance state left to reset.

Related FRA: FR-009, FR-010, FR-013, FR-018.
Related SDA: DEP-007, DEP-008, DEP-009, DEP-012.
Related Capability: CAP-004, CAP-005, CAP-008, CAP-011.
Related ADR: ADR-006, ADR-007.
Related Technical Debt: TD-006.

### P2-03-AD-006 - Drawdown Computational Authority and Canonical Input Source

Problem: `RiskEngine` is the correctly-assigned Computational Authority for Drawdown, but computes it from its own internally-tracked `self.peak_equity` rather than from canonical state (CGA CAP-005; TD-006's Drawdown half).

Decision: `RiskEngine` remains the exclusive Computational Authority for Drawdown, reaffirmed unchanged. `RiskEngine.check()` computes Drawdown exclusively as canonical Peak Equity minus canonical Equity, both read from its `state` parameter, consistent with AD-005's removal of any internally-tracked alternative.

Scientific Rationale: ADR-006's explicit text: "RiskEngine SHALL calculate Drawdown exclusively from canonical financial state."

Architectural Rationale: this decision requires no change to which component computes Drawdown, only to which values feed the computation; it is a direct, structural consequence of AD-004 and AD-005 rather than an independent design choice.

Alternatives Considered: (a) relocate Drawdown's Computational Authority to `PnLEngine` alongside Equity and Peak Equity, since both source values now originate there - rejected, ADR-006 explicitly assigns Drawdown's computation to `RiskEngine`, and Drawdown is a Risk Metric by category (ADR-007), not a PnL Accounting value by category (ADR-005); relocating it would contradict the Baseline's own categorical separation without scientific justification.

Consequences: Drawdown's formula and Computational Authority are both unchanged from today's intent; only the source of its two inputs changes, from `RiskEngine`'s own tracker to `CanonicalState`'s canonical values, closing TD-006's Drawdown half.

Related FRA: FR-010, FR-011.
Related SDA: DEP-002, DEP-007, DEP-008, DEP-009, DEP-017.
Related Capability: CAP-005.
Related ADR: ADR-006.
Related Technical Debt: TD-006.

### P2-03-AD-007 - Drawdown Ratio Ownership Assignment

Problem: Drawdown Ratio is computed and stored today, sharing Drawdown's exact input-source characteristics, but no ADR names its Computational Authority or Authoritative Owner at all (CGA CAP-006; FRA FR-012; SDA Cluster A).

Decision: `RiskEngine` is designated the Computational Authority for Drawdown Ratio, computed in the same `check()` call as Drawdown, from the same canonical Equity and Peak Equity inputs (AD-006). `CanonicalState` is designated the Authoritative Owner, retaining its existing `drawdown_ratio` storage key unchanged.

Scientific Rationale: no prior ADR names Drawdown Ratio; this decision is the first explicit ownership assignment for it, extending ADR-006's Drawdown-input-source rule and ADR-007's Risk Metric categorization to Drawdown Ratio by direct analogy, since both values are computed identically (as a function of the same two canonical inputs, in the same method, for the same purpose of exposure control).

Architectural Rationale: assigning Drawdown Ratio to a different Computational Authority than Drawdown would require splitting one currently-unified computation (`run_engine/core/risk.py:24-30`) across two components for no scientific reason; keeping both together in `RiskEngine` preserves the existing, already-correct computational grouping while finally naming its ownership.

Alternatives Considered: (a) leave Drawdown Ratio's ownership formally unassigned pending a future ADR revision - rejected, since Section 5 of the governing task requires deciding Canonical Publication and Computational Authority for Drawdown Ratio explicitly, and no scientific obstacle prevents deciding it now. (b) assign `PnLEngine` as Drawdown Ratio's Computational Authority, grouping it with Equity/Peak-Equity instead - rejected, Drawdown Ratio is a Risk Metric derived from Drawdown, not a PnL Accounting value, and grouping it with `RiskEngine`'s existing Drawdown computation avoids introducing a cross-component dependency for a single derived ratio.

Consequences: FR-012's previously-undefined ownership question is closed; Drawdown Ratio's storage location and computation mechanism remain otherwise unchanged from today.

Related FRA: FR-012.
Related SDA: none (SDA confirmed FR-012 ungated by any dependency record).
Related Capability: CAP-006.
Related ADR: ADR-006 (extended), ADR-007.
Related Technical Debt: none.

### P2-03-AD-008 - CanonicalState Schema Completeness and Canonical Publication

Problem: five of six financial values already reside at their correct `CanonicalState` storage location; one (cumulative Realized PnL) does not yet exist there at all (CGA CAP-007).

Decision: `CanonicalState` is confirmed as the sole Authoritative Owner and sole canonical storage location for all six financial values in scope - Realized PnL (event, existing `pnl` key, unchanged), Realized PnL (cumulative, new key per AD-002), Equity (existing `equity` key, unchanged), Peak Equity (existing `peak_equity` key, unchanged), Drawdown (existing `drawdown` key, unchanged), and Drawdown Ratio (existing `drawdown_ratio` key, unchanged). No financial value in scope is ever stored, cached, or duplicated anywhere else in the runtime once this unit's decisions are implemented.

Scientific Rationale: ADR-006's Acceptance Criterion: "CanonicalState contains exactly one canonical financial state."

Architectural Rationale: this decision is the aggregate consequence of AD-002 (new key), AD-004/AD-005 (Peak Equity's single storage location, no `RiskEngine` duplicate), and AD-006 (Drawdown's canonical-only input source); it is recorded as its own decision because it is the direct architectural answer to the CGA's own aggregate capability, CAP-014 (Canonical Financial State).

Alternatives Considered: none scientifically defensible were found; every alternative storage arrangement considered under AD-002, AD-004, and AD-005 already addresses the relevant sub-question.

Consequences: `CanonicalState.get()` becomes the single point of truth for every financial value; every consumer (`RiskEngine`, `PerformanceEngine`) reads exclusively from this single source (Section 12).

Related FRA: FR-003, FR-006, FR-011, FR-016.
Related SDA: DEP-001, DEP-002, DEP-003, DEP-015, DEP-018.
Related Capability: CAP-002, CAP-007, CAP-014.
Related ADR: ADR-006, Rule OM-006.
Related Technical Debt: none directly; TD-006 indirectly, via AD-004/AD-005/AD-006's contribution.

### P2-03-AD-009 - Single-Source Initial Capital

Problem: the Initial Capital literal `100.0` is independently duplicated, undocumented, in `CanonicalState.__init__` (`run_engine/core/canonical_state.py:28,30`) and `RiskEngine.__init__` (`run_engine/core/risk.py:9-10`) (CGA CAP-007, FR-017).

Decision: Initial Capital is a configuration constant, not a Financial Runtime Object within this document's scope; `CanonicalState` does not own the configuration value itself. The canonical runtime state - in particular, Equity's initialized value - is initialized from the configured Initial Capital value; this document assigns Authoritative Ownership only for runtime financial objects (Section 5), not for configuration constants. Initial Capital is referenced from a single configuration source at initialization, eliminating the duplicated literal. `RiskEngine`, after AD-005's removal of its own `self.last_equity`/`self.peak_equity` instance attributes, retains no reference to Initial Capital at all; this decision's practical effect for `RiskEngine` is therefore fully achieved as a direct corollary of AD-005, requiring no independent action beyond it.

Scientific Rationale: AI-010 (Financial Consistency) requires the runtime to remain internally consistent at all times; a duplicated, independently-maintained constant is a latent internal-consistency risk even where both copies currently agree by value.

Architectural Rationale: eliminating the second copy structurally, by removing the component that held it (AD-005), is preferred over merely documenting the duplication as intentional, since a merely-documented duplication remains a duplication.

Alternatives Considered: (a) formally declare both copies intentional and equal by contract, documented but not eliminated - rejected, this would leave AI-010's internal-consistency invariant dependent on manual synchronization rather than structural guarantee. (b) introduce a shared constants module imported by both components - rejected as unnecessary once AD-005 removes `RiskEngine`'s need for the value entirely; introducing a new shared module for a value only one component needs would be scope expansion without justification.

Consequences: no second Initial Capital reference remains anywhere in the runtime once AD-005 is implemented; this decision requires no code change beyond what AD-005 already requires.

Related FRA: FR-017.
Related SDA: DEP-014.
Related Capability: CAP-007, CAP-011.
Related ADR: AI-010.
Related Technical Debt: none.

### P2-03-AD-010 - Writer-on-Behalf-Of Exclusivity

Problem: the Runtime Ownership Matrix requires that only designated components write canonical state on another component's behalf; this must be reaffirmed explicitly for the newly-relocated and newly-created financial values.

Decision: `CanonicalEnforcer` remains the sole Writer-on-Behalf-Of path for every financial value, including the new cumulative-Realized-PnL key (AD-002). `RunLoop` continues to call `CanonicalEnforcer`'s Writer-on-Behalf-Of methods exclusively and never writes to `CanonicalState.state` directly, for any financial value, under any circumstance. No component other than `CanonicalEnforcer` gains direct write access to `CanonicalState.state`.

Scientific Rationale: Rule OM-006 (`CanonicalState` exclusively owns active runtime state) implies a single, exclusive write path, since an Authoritative Owner whose state can be mutated through multiple paths cannot guarantee exclusivity.

Architectural Rationale: this decision changes nothing about `CanonicalEnforcer`'s already-correct existing pattern (`apply_pnl`, `apply_equity`, `apply_risk`, `run_engine/core/canonical_enforcer.py:15-37`); it extends the identical pattern to the one new value AD-002 introduces, and reaffirms it as an explicit architectural rule rather than an implicit convention, so that future units do not need to re-derive it.

Alternatives Considered: (a) allow `PnLEngine` to write directly to `CanonicalState` for its own newly-owned values, bypassing `CanonicalEnforcer` - rejected, this would create a second write path, contradicting Rule OM-006 and the Writer-on-Behalf-Of pattern every other financial value already follows.

Consequences: none beyond formalizing the existing pattern; no component's write access changes as a result of this decision alone.

Related FRA: all twenty (structural rule, not tied to one requirement).
Related SDA: DEP-001, DEP-002, DEP-003.
Related Capability: CAP-007.
Related ADR: ADR-006, Rule OM-006.
Related Technical Debt: none.

### P2-03-AD-011 - Consumer Boundary Matrix

Problem: `RiskEngine`'s current Peak-Equity duplication partially undermines its read-only boundary in substance even though its current read mechanism is already read-only in form (CGA CAP-008); the full consumer boundary set has not previously been stated as a single, explicit matrix for this unit's six financial values.

Decision: the following consumer boundary matrix is binding for all six financial values in scope.

| Component | Realized PnL (event) | Realized PnL (cumulative) | Equity | Peak Equity | Drawdown | Drawdown Ratio |
|---|---|---|---|---|---|---|
| PnLEngine | Computational Authority | Computational Authority | Computational Authority | Computational Authority | no access | no access |
| RunLoop | orchestrates only, no computation | orchestrates only, no computation | orchestrates only, no computation | orchestrates only, no computation | orchestrates only, no computation | orchestrates only, no computation |
| CanonicalState | Authoritative Owner (storage only) | Authoritative Owner (storage only) | Authoritative Owner (storage only) | Authoritative Owner (storage only) | Authoritative Owner (storage only) | Authoritative Owner (storage only) |
| CanonicalEnforcer | Writer-on-Behalf-Of | Writer-on-Behalf-Of | Writer-on-Behalf-Of | Writer-on-Behalf-Of | Writer-on-Behalf-Of | Writer-on-Behalf-Of |
| RiskEngine | no access | no access | read-only | read-only | Computational Authority | Computational Authority |
| PerformanceEngine | read-only | no access | no access | no access | no access | no access |

Scientific Rationale: ADR-007 (RiskEngine never owns Equity or Peak Equity; consumes canonical financial state only), ADR-008 and Rule OM-008 (PerformanceEngine owns no operational runtime information and remains a pure consumer of Realized PnL event only).

Architectural Rationale: stating the full matrix once, for all six values simultaneously, forecloses the possibility of a future unit re-introducing a partial-access pattern for a single value in isolation without noticing its inconsistency with the other five.

Alternatives Considered: (a) grant `RiskEngine` read access to Realized PnL (cumulative) for potential future risk-formula use - rejected as scope expansion; no FR in this unit requires it, and P2-04 (Risk Metrics ownership) is the correct venue if such a need is later established. (b) grant `PerformanceEngine` read access to Equity for potential future performance-metric use - rejected for the identical reason; ADR-008/Rule OM-008 already confirm `PerformanceEngine`'s current scope is correct and this document does not expand it.

Consequences: `RiskEngine`'s boundary for Equity/Peak-Equity becomes fully verifiable, not merely mechanically read-only, once AD-005 removes its competing internal tracker; `PerformanceEngine`'s already-correct boundary is reaffirmed unchanged.

Related FRA: FR-013, FR-014.
Related SDA: DEP-009, DEP-018.
Related Capability: CAP-008, CAP-009.
Related ADR: ADR-007, ADR-008, Rule OM-007, Rule OM-008.
Related Technical Debt: TD-006 (RiskEngine's boundary column).

### P2-03-AD-012 - State-Only Representation of Financial Objects (Financial Events Not Required)

Problem: ADR-002 architecturally names Financial Events ("Realized PnL Updated," "Unrealized PnL Updated," "Equity Updated," "Peak Equity Updated," "Drawdown Updated") but none exists as an implemented object anywhere in the runtime (FRA Section 11); OQ-008 asks whether this unit must implement them.

Decision: Financial Events are not a required P2-03 deliverable. Every financial value in scope is represented as canonical state - a `CanonicalState` field, overwritten each tick - rather than as a discrete, independently-published Event object. Realized PnL (event) remains what it already is today: the tick-scoped return value of `PnLEngine`'s computation, immediately consumed and published as state (via `pnl` and, once created, the new cumulative key), not retained as a standalone event record with its own identity or history.

Scientific Rationale: none of the FRA's twenty functional requirements' Validation Conditions requires a Financial Event object to exist (re-confirmed by direct re-check of FRA Sections 15 through 23, consistent with the SDA's own OQ-008 classification, NON-BLOCKING).

Architectural Rationale: the Implementation Baseline's own P2-03 objective text names only "PnLEngine ownership," "Realized PnL (cumulative)," and "Equity, Peak Equity and Drawdown consistency" - none of which requires an event object; introducing Financial Events now would be scope expansion beyond this explicit objective text, and ADR-002's naming remains available, unimplemented, for a future unit that establishes an explicit functional requirement for it.

Alternatives Considered: (a) implement a minimal Financial Event object now, to align with ADR-002's naming - rejected as scope expansion with no supporting functional requirement in this unit's own FRA. (b) formally retire ADR-002's Financial Events naming as no longer intended - rejected, this document makes no decision about a future unit's scope, and retiring an ADR-level naming is beyond this document's own scope (Section 2).

Consequences: this decision resolves OQ-008; no Event Model beyond the existing tick-scoped state-publication pattern is introduced by this unit.

Related FRA: FR-001 through FR-020 (structural scope decision, applies document-wide).
Related SDA: none directly (OQ-008 was classified NON-BLOCKING, referencing no dependency record).
Related Capability: none directly.
Related ADR: ADR-002.
Related Technical Debt: none.

### P2-03-AD-013 - Derived View Scope Restriction

Problem: the governing task requires defining Derived Views and their boundaries for this unit's financial objects.

Decision: no financial value in this unit's scope is treated as a Derived View recomputed independently by more than one component. Equity, Peak Equity, and cumulative Realized PnL are stored canonical quantities (AD-003), computed exclusively by `PnLEngine` and never independently recomputed by any other component. Drawdown and Drawdown Ratio are the only Derived-View-shaped elements in this unit's scope: each is computed once per tick, exclusively by `RiskEngine`, from canonical Equity and Peak Equity, and immediately published as canonical state via `CanonicalEnforcer` (AD-006, AD-007) - not recomputed independently by any other consumer of `CanonicalState`.

Scientific Rationale: AI-010 requires internal consistency at all times; a value independently recomputable by more than one component cannot structurally guarantee this, regardless of whether the components currently agree.

Architectural Rationale: restricting every Derived View to exactly one computing component, immediately publishing its result rather than leaving it to be recomputed on read, eliminates the specific failure mode TD-006 already demonstrated for Peak Equity and Drawdown.

Alternatives Considered: (a) allow `PerformanceEngine` or any future consumer to independently recompute Drawdown Ratio from Equity/Peak-Equity for local convenience - rejected, this reintroduces exactly the dual-computation pattern this document exists to eliminate.

Consequences: any future component requiring Drawdown or Drawdown Ratio must read the canonical, already-published value rather than recomputing it.

Related FRA: none directly (a structural rule spanning multiple requirements).
Related SDA: none directly.
Related Capability: CAP-005, CAP-006, CAP-014.
Related ADR: AI-010.
Related Technical Debt: none.

### P2-03-AD-014 - Reset Consistency for Cumulative Realized PnL and Dependent Values

Problem: `CanonicalState.reset()` correctly restores its own existing fields but has no key yet for cumulative Realized PnL (AD-002); `RiskEngine` has no `reset()` method at all today, a latent inconsistency (CGA CAP-011; OQ-009).

Decision: `CanonicalState.reset()` is extended to zero the new cumulative-Realized-PnL key unconditionally, exactly mirroring Equity's own reset to Initial Capital, since Equity's post-reset value is definitionally Initial Capital plus zero cumulative Realized PnL plus zero Unrealized PnL (AD-003's reconstruction rule, evaluated at the reset boundary). `RiskEngine` requires no `reset()` method of its own, since AD-005 removes every instance attribute it previously held for Equity, Peak Equity, Drawdown, and Drawdown Ratio; a component with no persisted state relevant to this unit's scope has nothing left to reset.

Scientific Rationale: AI-010 requires internal consistency at all times, including immediately following a reset.

Architectural Rationale: this decision follows directly and only from AD-002 (new key must be included in the existing reset mechanism) and AD-005 (no new reset mechanism needed for `RiskEngine`); no new reset architecture is introduced.

Alternatives Considered: (a) reset cumulative Realized PnL to a value other than zero - rejected, no functional requirement or ADR text supports any value other than zero at initialization or reset. (b) give `RiskEngine` an explicit no-op `reset()` method for symmetry with other components - left as a Specification-stage interface-consistency question, not an architecture decision, since it has no observable effect on any invariant in this document.

Consequences: `CanonicalState.reset()`'s existing structure (`self.__init__()`, `run_engine/core/canonical_state.py:104-106`) needs no new logic beyond including the new key in `__init__`'s own default dictionary.

Related FRA: FR-017, FR-018.
Related SDA: DEP-012, DEP-014.
Related Capability: CAP-011.
Related ADR: AI-010.
Related Technical Debt: none.

### P2-03-AD-015 - TD-006 Architectural Closure Boundary

Problem: TD-006's Target Phase is recorded as "P2-03 / P2-04" without further subdivision; OQ-007 asks whether its full closure belongs entirely to P2-03 or partly to P2-04.

Decision: TD-006 is architecturally closed, within this unit's scope, exactly to the boundary the FRA originally proposed and the CGA's objective analysis confirmed without deciding: the Equity/Peak-Equity-ownership half (AD-004) and the Drawdown-input-source half (AD-005, AD-006) are fully resolved by this document. Any change to `RiskEngine`'s own risk-limiting formula - `max_exposure`, `min_exposure`, `max_drawdown` thresholds, or regime-dampening multipliers (`run_engine/core/risk.py:5-7,33-49`) - remains explicitly outside this decision's scope and outside P2-03 entirely, deferred to P2-04 ("Verify Risk Metrics ownership. Validate deterministic RiskEngine behaviour," Implementation Baseline).

Scientific Rationale: the Implementation Baseline's own P2-03 objective text names "Equity, Peak Equity and Drawdown consistency" but does not name risk-formula correctness; P2-04's own named objective explicitly covers "Risk Metrics ownership" and "deterministic RiskEngine behaviour."

Architectural Rationale: TD-006's underlying defect - duplicate Computational Authority for Peak Equity, and a non-canonical input source for Drawdown - is fully and structurally eliminated by AD-004 through AD-006 without touching any risk-formula logic; no part of the risk-limiting formula depends on how Peak Equity or Drawdown's inputs are sourced, so this boundary introduces no coupling between the two units.

Alternatives Considered: (a) also review and re-architect `RiskEngine`'s risk-limiting formula as part of TD-006's closure, to avoid a second future document revisiting `RiskEngine` - rejected as scope expansion beyond this unit's Baseline objective and beyond the governing task's explicit exclusion of risk-formula changes (Section 2).

Consequences: TD-006's status may be updated to Resolved for its Equity/Peak-Equity/Drawdown-input-source scope once AD-004 through AD-006 are implemented and certified; its risk-formula-adjacent portion, if any is later found to exist, remains open for P2-04 to evaluate independently. This document does not itself change TD-006's Register status (Section 18).

Related FRA: FR-008, FR-009, FR-010.
Related SDA: DEP-006 through DEP-009, DEP-017.
Related Capability: CAP-004, CAP-005, CAP-008.
Related ADR: ADR-006, ADR-007.
Related Technical Debt: TD-006.

### P2-03-AD-016 - Replay and Determinism Preservation Requirement

Problem: Replay Consistency and Financial Determinism (CGA CAP-012, CAP-013) are already certified for the current, pre-P2-03 system but require re-verification once ownership relocates (SDA DEP-015).

Decision: every decision in this document (AD-001 through AD-015) must preserve functionally identical numerical results, under identical deterministic inputs, with the current system's output for any identical lifecycle-event sequence. The underlying arithmetic - incremental PnL accumulation, Initial-Capital-plus-cumulative-PnL for Equity, max-comparison for Peak Equity, subtraction for Drawdown, division for Drawdown Ratio - is unchanged by this document; only which component performs each computation, and from which explicit inputs, changes. No decision in this document introduces randomness, wall-clock dependence, or any input beyond the deterministic lifecycle-event and canonical-state values already flowing through the current runtime.

Scientific Rationale: AI-005 (Deterministic Execution) and ADR-010 (Deterministic Runtime Execution Ordering) require the runtime's call ordering and computation to remain fully deterministic; ADR-005 and ADR-006's own Acceptance Criteria require reproducibility for identical lifecycle histories.

Architectural Rationale: stating this as an explicit, binding requirement on every other decision in this document - rather than assuming it as an implicit byproduct - ensures the future Specification and Implementation stages treat numeric-equivalence verification as a first-class deliverable, not an afterthought.

Alternatives Considered: none; this is a preservation requirement on the decisions already made, not an independent design choice with alternatives of its own.

Consequences: the future Certification for this unit must include a replay/determinism comparison against the current, pre-P2-03 system's own certified output (P2-02A Final Certification Section 16 precedent), not merely a check against this document's own decisions in isolation.

Related FRA: FR-016.
Related SDA: DEP-015.
Related Capability: CAP-012, CAP-013.
Related ADR: ADR-005, ADR-006, AI-005.
Related Technical Debt: none.

## 8. Computational Authority Model

| Financial Object | Computational Authority | Decision |
|---|---|---|
| Realized PnL (event) | PnLEngine | AD-001 |
| Realized PnL (cumulative) | PnLEngine | AD-001 |
| Equity | PnLEngine | AD-003 |
| Peak Equity | PnLEngine | AD-004 |
| Drawdown | RiskEngine | AD-006 |
| Drawdown Ratio | RiskEngine | AD-007 |

Exactly two components hold Computational Authority across all six financial objects in scope: `PnLEngine` (PnL Accounting values, per ADR-005) and `RiskEngine` (Risk Metrics, per ADR-007). No object has more than one Computational Authority; no third component computes any financial value.

## 9. Authoritative Ownership Model

`CanonicalState` is the Authoritative Owner of all six financial objects in scope, without exception (AD-002, AD-008). No financial value is stored, cached, or duplicated anywhere else once AD-005 and AD-009 are implemented. This is a single-owner model: exactly one Authoritative Owner exists for the entire financial domain, distinct from but coordinated with the two-component Computational Authority model in Section 8.

## 10. Writer-on-Behalf-Of Model

`CanonicalEnforcer` is the exclusive Writer-on-Behalf-Of path for all six financial objects (AD-010). `PnLEngine` and `RiskEngine`, as Computational Authorities, never write to `CanonicalState` directly; each returns its computed value(s) to `RunLoop`, which passes them to the corresponding `CanonicalEnforcer.apply_*()` method. This is unchanged from today's already-correct pattern for the five values already following it, extended to the one new value AD-002 introduces.

## 11. Canonical Publication Model

Every financial object is published under exactly one `CanonicalState` key, readable via `CanonicalState.get()` by any consumer with read access under the Consumer Boundary Matrix (Section 12). No financial value is published through any channel other than `CanonicalState` - no separate event stream, no separate cache, no component-local snapshot exposed to other components (AD-012). Publication occurs once per tick, synchronously, within `RunLoop.step()`'s existing call sequence (Section 6).

## 12. Consumer Boundary Model

The binding matrix is stated in full at AD-011 (Section 7). Summary: `PnLEngine` and `RiskEngine` each have write access, via `CanonicalEnforcer`, only to the financial objects they hold Computational Authority for (Section 8); `RunLoop` has no computational access to any financial object, only orchestration access; `RiskEngine` has read-only access to Equity and Peak Equity; `PerformanceEngine` has read-only access to Realized PnL (event) only, and no access whatsoever to Equity, Peak Equity, Drawdown, or Drawdown Ratio.

## 13. Financial State Model

All six financial objects are State, not Event (AD-012): each is a `CanonicalState` field holding the current, single value, overwritten each tick by its Computational Authority via its Writer-on-Behalf-Of path. No financial object in this unit's scope has a historical, append-only, or event-sourced representation; the full trade history remains available only through `TradeLifecycleEngine`'s own `Trade`/`LifecycleEvent` records (unchanged, out of scope for this unit), which are not treated as a second representation of any of the six financial objects.

## 14. Event Model

Financial Events (ADR-002) are not implemented by this unit (AD-012, resolving OQ-008). The only event-shaped objects in scope remain `TradeLifecycleEngine`'s existing `LifecycleEvent` instances (`TRADE_OPENED`, `SCALE_IN`, `PARTIAL_CLOSE`, `TRADE_CLOSED`, `RUNTIME_FAILURE_EVENT`), which are inputs to `PnLEngine`'s computation (AD-001), not outputs of the financial-ownership domain this document governs. No new event type is introduced by any decision in Section 7.

## 15. Derived View Model

Drawdown and Drawdown Ratio are this unit's only Derived Views, each computed once per tick by `RiskEngine` from canonical Equity and Peak Equity and immediately published as canonical state (AD-013). Equity, Peak Equity, and cumulative Realized PnL are stored canonical quantities bound by a reconstruction rule enforced by their Computational Authority at write time (AD-003), not Derived Views computed independently by their readers. No consumer of `CanonicalState` recomputes any Derived View independently; every consumer reads the already-published result.

## 16. Replay and Determinism

Binding requirement: AD-016 (Section 7). Every decision in Sections 7 through 15 preserves the current system's arithmetic unchanged, relocating only which component performs each computation and from which explicit inputs it is drawn. No decision introduces non-determinism. The future Certification for this unit must verify numeric equivalence against the current, pre-P2-03 system's own certified behavior (P2-02A Final Certification Section 16 precedent) for an identical scripted lifecycle-event sequence, closing CAP-012 and CAP-013's pending-re-verification status.

## 17. Runtime Failure Behaviour

`RUNTIME_FAILURE_EVENT` continues to leave every financial object unmodified, extended to the two newly-relocated or newly-created values (Equity, Peak Equity relocated to `PnLEngine`; cumulative Realized PnL newly created). `PnLEngine`'s existing `event_type` guard (`run_engine/core/pnl.py:23-24`, already certified for event-PnL) is the architectural pattern this non-mutation contract must extend to Equity, Peak Equity, and cumulative Realized PnL under AD-001/AD-003/AD-004: none of these three values changes on a tick whose `trade_event` is `RUNTIME_FAILURE_EVENT`, exactly as event-PnL already does not change today. `PerformanceEngine`'s existing guard (`run_engine/core/performance.py:8-9`) remains unchanged and unaffected by any decision in this document. This closes CAP-010's pending-re-verification status once implemented and certified.

## 18. Technical Debt Resolution

TD-006 (RiskEngine Peak Equity and Drawdown Ownership Duplication) is architecturally resolved, within its P2-03 boundary, by AD-004, AD-005, and AD-006 jointly (AD-015). Its risk-formula-adjacent portion, if any, remains explicitly deferred to P2-04, per AD-015's boundary decision, itself resolving OQ-007. This document does not change TD-006's Register status field; the Register update is a Certification-stage action, consistent with how TD-001's Resolved status was only recorded after P2-02A's own certification, not during its Architecture stage.

No other Technical Debt Register item is affected by any decision in this document: TD-001 and TD-003 are referenced only as compatibility contracts preserved unchanged (AD-016's numeric-equivalence requirement); TD-002, TD-004, TD-005, and TD-007 remain entirely outside this document's scope, consistent with the CGA's own classification (CGA Section 14).

## 19. Architectural Invariants

### P2-03-INV-001 - Unique Computational Authority

Every financial object in scope has exactly one Computational Authority at all times. Established by: AD-001, AD-003, AD-004, AD-006, AD-007. Verified by: Section 8.

### P2-03-INV-002 - Unique Authoritative Owner

Every financial object in scope has exactly one Authoritative Owner (`CanonicalState`) at all times. Established by: AD-002, AD-008, AD-009. Verified by: Section 9.

### P2-03-INV-003 - No Duplicate Financial Computation

No financial object in scope is computed by more than one component. Established by: AD-004, AD-005, AD-006, AD-013. Verified by: Sections 8, 15.

### P2-03-INV-004 - No Duplicate Ownership

No financial object in scope is stored, cached, or persisted as instance state by any component other than `CanonicalState`. Established by: AD-001 (PnLEngine receives, does not persist, prior canonical values), AD-005 (RiskEngine's instance attributes removed), AD-009 (single-source Initial Capital). Verified by: Sections 4, 9.

### P2-03-INV-005 - Canonical Publication

Every financial object is published exclusively through `CanonicalState`, exclusively via `CanonicalEnforcer`'s Writer-on-Behalf-Of methods. Established by: AD-002, AD-008, AD-010. Verified by: Sections 10, 11.

### P2-03-INV-006 - Deterministic Financial Replayability

An identical lifecycle-event sequence produces an identical sequence of values for every financial object in scope, on every replay. Established by: AD-016. Verified by: Section 16.

### P2-03-INV-007 - RuntimeFailureEvent Non-Mutation

A tick whose `trade_event` is `RUNTIME_FAILURE_EVENT` leaves every financial object in scope unmodified. Established by: Section 17 (extending AD-001/AD-003/AD-004's guard pattern). Verified by: Section 17.

### P2-03-INV-008 - Consumers Never Write Financial State

`RiskEngine` and `PerformanceEngine`, as consumers rather than Computational Authorities for any object they read, never write to `CanonicalState`, directly or via `CanonicalEnforcer`, for any financial object they do not themselves hold Computational Authority for. Established by: AD-011. Verified by: Section 12.

### P2-03-INV-009 - RiskEngine Owns No Canonical Financial State

`RiskEngine` holds no Authoritative Ownership and no persisted instance state for Equity, Peak Equity, Realized PnL (event or cumulative). Established by: AD-005. Verified by: Sections 8, 9.

### P2-03-INV-010 - PerformanceEngine Owns No Canonical Financial State

`PerformanceEngine` holds no Authoritative Ownership and no persisted instance state for any of the six financial objects in scope. Established by: AD-011 (unchanged from today's already-correct state). Verified by: Sections 8, 9.

### P2-03-INV-011 - Writer-on-Behalf-Of Only by Explicit Designation

No component writes to `CanonicalState` except `CanonicalEnforcer`, and `CanonicalEnforcer` writes only the value a Computational Authority explicitly returned to it via `RunLoop`. Established by: AD-010. Verified by: Section 10.

### P2-03-INV-012 - CanonicalState Is the Sole Canonical Store

No financial object in scope has any representation - stored, cached, or event-sourced - outside `CanonicalState`. Established by: AD-008, AD-012, AD-013. Verified by: Sections 11, 13, 14, 15.

Twelve invariants are defined, matching the twelve the governing task named as the required minimum. Each cites the specific decision(s) that establish it and the section that verifies it, so that a future Specification or Certification document can check conformance against a named, traceable invariant rather than an implicit expectation.

## 20. Traceability

### FRA Traceability

Every one of the FRA's twenty functional requirements is addressed by at least one decision in Section 7: FR-001 (AD-001), FR-002 (AD-001), FR-003 (AD-001, AD-002, AD-008, AD-010), FR-004 (AD-001), FR-005 (AD-003), FR-006 (AD-002, AD-003, AD-008), FR-007 (AD-003), FR-008 (AD-004), FR-009 (AD-004, AD-005), FR-010 (AD-005, AD-006), FR-011 (AD-002, AD-006, AD-008), FR-012 (AD-007), FR-013 (AD-011), FR-014 (AD-011), FR-015 (Section 17), FR-016 (AD-016), FR-017 (AD-002, AD-009, AD-014), FR-018 (AD-005, AD-014), FR-019 (AD-016's numeric-equivalence requirement, preserving all compatibility contracts unchanged), FR-020 (respected as an explicit non-goal; no decision implements Unrealized PnL; AD-003 explicitly notes its reconstruction-rule term remains zero).

### SDA Traceability

Every one of the SDA's eighteen dependency records is addressed: DEP-001 (AD-002, AD-008), DEP-002 (AD-006), DEP-003 (AD-001, AD-002, AD-008), DEP-004 (AD-001), DEP-005 (AD-001, AD-003), DEP-006 (AD-004), DEP-007 (AD-004, AD-005, AD-006), DEP-008 (AD-004, AD-005, AD-006), DEP-009 (AD-004, AD-005, AD-006, AD-011), DEP-010 (AD-001, Section 17), DEP-011 (AD-003, AD-004, Section 17), DEP-012 (AD-005, AD-014), DEP-013 (AD-003), DEP-014 (AD-002, AD-004, AD-009, AD-014), DEP-015 (AD-016), DEP-016 (AD-016's compatibility preservation), DEP-017 (AD-004, AD-006), DEP-018 (AD-001, AD-011, AD-012).

### CGA Traceability

Every one of the CGA's fifteen capabilities is addressed: CAP-001 (AD-001, already COMPLETE, reaffirmed), CAP-002 (AD-001, AD-002), CAP-003 (AD-003), CAP-004 (AD-004, AD-005), CAP-005 (AD-005, AD-006), CAP-006 (AD-007), CAP-007 (AD-002, AD-008, AD-009, AD-010), CAP-008 (AD-005, AD-011), CAP-009 (AD-011, already COMPLETE, reaffirmed), CAP-010 (Section 17), CAP-011 (AD-005, AD-014), CAP-012 (AD-016), CAP-013 (AD-016), CAP-014 (AD-008), CAP-015 (AD-016, already COMPLETE, reaffirmed).

### ADR Traceability

ADR-002 (AD-012), ADR-004 (AD-016, compatibility preservation only), ADR-005 (AD-001, AD-003, AD-016), ADR-006 (AD-002 through AD-011, AD-013 through AD-016 - the governing ADR for the majority of this document's decisions), ADR-007 (AD-004, AD-005, AD-006, AD-007, AD-011), ADR-008 (AD-011), ADR-009 (AD-016, compatibility preservation only), ADR-010 (AD-016), ADR-011 (Section 17), AI-005 (AD-016), AI-010 (AD-009, AD-013, AD-014), Rule OM-006 (AD-002, AD-008, AD-010), Rule OM-007 (AD-005, AD-011), Rule OM-008 (AD-011).

### Technical Debt Traceability

TD-001 (referenced only, AD-016 compatibility preservation, unchanged), TD-002 (out of scope, not referenced by any decision), TD-003 (referenced only, AD-016 compatibility preservation, unchanged), TD-004 (out of scope, not referenced), TD-005 (out of scope, not referenced), TD-006 (AD-004, AD-005, AD-006, AD-015 - architecturally closed within its P2-03 boundary), TD-007 (out of scope, not referenced).

## 21. Open Questions Resolved

This document resolves the Open Questions the SDA classified CONDITIONALLY BLOCKING for subsequent Architecture decisions (SDA Section 15): OQ-001, OQ-003, OQ-004, OQ-005, OQ-006, OQ-007, and OQ-009. It additionally resolves OQ-008, classified NON-BLOCKING by the SDA but directly required by this document's own Section 14 (Event Model), since the governing task requires deciding State-versus-Event treatment for every financial object, and that decision cannot be made without first answering whether Financial Events are required at all.

- OQ-001 (cumulative-PnL accumulation mechanism): resolved by AD-001 - incremental accumulation from an explicit prior-value input, not internal persistence or full re-summation.
- OQ-003 (Equity storage versus projection): resolved by AD-003 - stored canonical quantity, bound by a reconstruction rule, not a computed-on-demand projection.
- OQ-004 (Equity's exact Computational Authority mechanism): resolved at the conceptual level by AD-003 - a dedicated computation responsibility within `PnLEngine`, run every tick, receiving prior canonical values as explicit input. This document notes an internal tension between the FRA's framing of OQ-004 as "the central architecture question this document's findings feed into" and the SDA's framing of the same question as "a Specification-stage interface question" (SDA Section 15); this document resolves the tension by deciding the conceptual mechanism here (Architecture-level, as the FRA anticipated) while explicitly leaving the literal method signature, parameter names, and return type structure to the Specification stage (as the SDA anticipated). Both framings are therefore honored, applied to the two different halves of the same question.
- OQ-005 (Peak Equity's exact Computational Authority mechanism): resolved by AD-004 under the identical conceptual/literal split applied to OQ-004 - byproduct of Equity's computation, within the same responsibility, literal signature left to Specification.
- OQ-006 (RiskEngine.self.peak_equity removal versus retention): resolved by AD-005 - full removal.
- OQ-007 (TD-006's P2-03/P2-04 boundary): resolved by AD-015 - Equity/Peak-Equity/Drawdown-input-source half is P2-03's; risk-formula half is P2-04's.
- OQ-008 (Financial Events required): resolved by AD-012 - not required by this unit.
- OQ-009 (cumulative-PnL reset semantics): resolved by AD-014 - unconditional zero, mirroring Equity's own reset.

Not resolved here, consistent with the SDA's own stage attribution and this document's instruction not to exceed the Architecture-phase scope:

- OQ-002 (event-PnL/cumulative-PnL publish interface shape - single call, two calls, or one structured object): the SDA and FRA both explicitly assign this to the Specification stage ("an interface-shape decision belongs to the Specification stage," FRA OQ-002; "a pure Specification-stage interface-shape question," SDA OQ-002). Not resolved here.
- OQ-010 (RiskEngine.check()'s generic state parameter naming): classified NON-BLOCKING and purely cosmetic by both the FRA and SDA; carries no architectural consequence. Not resolved here.
- OQ-011 (Drawdown Ratio's own future FR-level requirement number): classified NON-BLOCKING by the SDA as "a Specification-stage cataloging question." Not resolved here; AD-007 resolves Drawdown Ratio's ownership, which is the scientific substance OQ-011's cataloging concern depends on, without renumbering any FRA requirement.
- OQ-012 (PositionSizingEngine forward-compatibility note): classified DEFERRED by the SDA, contingent on a future Architecture decision renaming `CanonicalState`'s `"equity"` key or shape. No decision in this document renames or reshapes the `equity` key; OQ-012's trigger condition is not met, so it remains correctly deferred and is not resolved here.

## 22. Readiness Assessment

Sixteen Architecture Decisions (AD-001 through AD-016) and twelve Architectural Invariants (INV-001 through INV-012) are established. Every decision traces to at least one FRA requirement, SDA dependency, CGA capability, and governing ADR (Section 20); every Technical Debt Register item is classified (Section 18); eight of twelve Open Questions are resolved at the Architecture level, with the remaining four explicitly and individually justified as out of this phase's scope (Section 21).

No decision in this document specifies a method signature, a literal `CanonicalState` key name, a file to modify first, or a commit order; every such question is explicitly and repeatedly deferred to the Specification stage throughout Section 7. No decision expands scope beyond the FRA's, SDA's, and CGA's own boundaries (Section 2).

Readiness: READY. This document is sufficient to proceed to the P2-03 Specification stage, where OQ-002's interface shape, the literal `CanonicalState` schema (key names for cumulative Realized PnL), `PnLEngine`'s exact method signatures for its Equity/Peak-Equity/cumulative-PnL responsibility, and `CanonicalEnforcer`'s new Writer-on-Behalf-Of method name must be decided. No further Architecture-stage decision is required before that step. This readiness assessment applies to the current scientific and architectural baseline (Sections 3 through 21); it does not preclude future architectural revision under the normal governance process should new scientific evidence or an architectural conflict emerge before or during Specification.

## 23. Internal Consistency Review

Terminology consistency - "Computational Authority," "Authoritative Owner," "Writer-on-Behalf-Of," "Derived View," and "canonical" are used exactly as defined by the Architecture Baseline and inherited unchanged by the FRA, SDA, and CGA; no term is redefined in this document.

Scope consistency - no decision in Section 7 specifies a method signature, a literal key name, an implementation order, a file modification order, or a commit order; every instance where such a detail might have been decided is explicitly deferred to the Specification stage (most visibly in AD-002, AD-003, AD-004, and Section 21). Section 2 confirms the risk-limiting formula, Unrealized PnL, and every other previously-established out-of-scope topic remains untouched by any decision in this document.

Decision consistency - all sixteen decisions were cross-checked against each other for contradiction: AD-004 and AD-005 both assign Peak Equity's disposition consistently (PnLEngine computes it, RiskEngine's tracker is removed, with no third position implied anywhere else); AD-006 and AD-007 both ground Drawdown and Drawdown Ratio in the same canonical inputs without contradiction; AD-009's Initial Capital decision is fully consistent with, and does not duplicate, AD-005's removal of RiskEngine's own copy.

Invariant consistency - all twelve invariants (Section 19) are each traceable to at least one specific decision that establishes them and at least one section that verifies them; no invariant is asserted without a grounding decision.

Traceability consistency - all twenty FRA requirements, all eighteen SDA dependencies, all fifteen CGA capabilities, and every governing ADR/Invariant/Rule are accounted for in Section 20; every Technical Debt Register item is classified in Section 18.

Decision-ID and Invariant-ID uniqueness - P2-03-AD-001 through P2-03-AD-016 and P2-03-INV-001 through P2-03-INV-012 are each defined exactly once (Section 7, Section 19) and referenced only by ID thereafter.

No fabricated decision - every decision traces to a specific FRA requirement, SDA dependency, CGA capability, or ADR text; no decision in this document addresses a concern absent from the governing baseline documents.

Status: Internal Consistency Review PASS.
