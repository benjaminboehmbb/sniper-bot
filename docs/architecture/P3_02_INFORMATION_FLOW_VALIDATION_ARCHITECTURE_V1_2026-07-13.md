Document Class:
Architecture Decision Document

Document ID:
P3-02-ARCH

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
docs/architecture/P3_02_INFORMATION_FLOW_VALIDATION_ARCHITECTURE_V1_2026-07-13.md

Depends On:
- docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md
- docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md
- docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md
- docs/architecture/analysis/P3_02_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-13.md
- docs/architecture/analysis/P3_02_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-13.md
- docs/architecture/analysis/P3_02_CAPABILITY_GAP_ANALYSIS_V1_2026-07-13.md
- docs/architecture/P3_01_DETERMINISTIC_EXECUTION_ORDERING_ARCHITECTURE_V1_2026-07-13.md
- docs/architecture/P3_01_DETERMINISTIC_EXECUTION_ORDERING_SPECIFICATION_V1_2026-07-13.md
- docs/architecture/certification/P3_01_FINAL_CERTIFICATION_V1_2026-07-13.md
- docs/architecture/P2_02A_POSITION_OWNERSHIP_ARCHITECTURE_V1_2026-07-10.md
- docs/architecture/P2_03_FINANCIAL_OWNERSHIP_ARCHITECTURE_V1_2026-07-11.md
- docs/architecture/P2_04_RISK_OWNERSHIP_ARCHITECTURE_V1_2026-07-13.md
- docs/architecture/certification/P2_03_FINAL_CERTIFICATION_V1_2026-07-11.md
- docs/architecture/certification/P2_04_FINAL_CERTIFICATION_V1_2026-07-13.md
- current runtime code at HEAD f6fb7f3911a978884ca10b22a0eef832a52f9486

Referenced By:
- future P3-02 Specification
- future P3-02 Implementation
- future P3-02 Final Certification

---

# P3-02 Information Flow Validation Architecture

## 1. Document Metadata

See front matter above. This document is the P3-02 Architecture, the fourth stage of the P3-02 governance chain (FRA -> SDA -> CGA -> Architecture -> Specification -> Implementation -> Final Certification). It is the first P3-02 stage permitted to make binding decisions.

## 2. Purpose

This document converts the twenty-four Functional Requirements of `P3_02_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-13.md` (the "FRA"), the fifty-two Dependency records of `P3_02_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-13.md` (the "SDA"), and the twenty-seven Capability classifications of `P3_02_CAPABILITY_GAP_ANALYSIS_V1_2026-07-13.md` (the "CGA") into binding architecture decisions. Every remaining P3-02-owned capability gap (CAP-001, CAP-004, CAP-006, CAP-010, CAP-018, and the general-convention PARTIAL findings CAP-003, CAP-005, CAP-007, CAP-008) is decided explicitly in this document. This document does not write a Specification, does not define Python signatures, method bodies, or file diffs, does not implement code, and does not build a test suite. Its output is the binding target architecture the Specification stage must translate into an exact implementation contract.

## 3. Scope

In scope: the twenty Architecture questions the governing task names - CanonicalState Read Contract, Canonical Working State Semantics, Tick-Complete Snapshot Stability, Top-Level Result Aliasing, Performance-Metrics Object Identity, CanonicalEnforcer Return-Contract Consistency, Producer Isolation, Consumer Read-Only Discipline, Nested Mutable Structures, Runtime Event Identity and Semantic Stability, Lifecycle History Information Flow, Position/Financial/Risk/Performance Information Flow, Failure Information Flow, HOLD/No-Execution Information Flow, Direct CanonicalState Writes, Alternative Information Paths, and Cross-Unit Boundaries.

Out of scope, per the FRA (Section 3), the SDA (Section 3), the CGA (Section 3), and the governing task's own "Wichtige Grenzen": P3-01's own twelve-stage execution ordering (not reopened); Position, PnL, and Risk formula or ownership changes (P2-02A/P2-03/P2-04, not reopened); Performance metric methodology redesign (TD-004, remains P3-03's); Persistence, Recovery, and Schema Evolution (ADR-012, Deferred Scope); Operator Lifecycle Control (TD-007); parallel or asynchronous execution; concrete Python signatures, file diffs, Implementation Units, or tests; any new Functional Requirement, Dependency, or Capability classification.

## 4. Binding Baseline

- `docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md` - ADR-001 through ADR-012; the Runtime Ownership Matrix and Rules OM-001 through OM-009; the Target Information Flow, Principles IF-001 through IF-006, Rules IF-001 through IF-006; the ownership taxonomy; Architecture Invariants AI-001 through AI-015; Acceptance Criteria AC-001 through AC-013.
- `docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md` - the P3-02 unit definition ("Remove hidden coupling. Validate Runtime Tick processing. Validate Market Observation processing.") and the P3-03 unit definition.
- `docs/architecture/analysis/P3_02_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-13.md` - twenty-four Functional Requirements, five Functional Gaps (FG-001 through FG-005, the last reclassified in the CGA), four Verified Conformant Findings, two Documentation Gaps, one Verification Gap, two Residual Risks.
- `docs/architecture/analysis/P3_02_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-13.md` - fifty-two dependency records, twelve Capability Clusters, seven Dependency Layers, no cyclic dependency found.
- `docs/architecture/analysis/P3_02_CAPABILITY_GAP_ANALYSIS_V1_2026-07-13.md` - twenty-seven capabilities, seventeen COMPLETE, six PARTIAL (CAP-003, CAP-005, CAP-007, CAP-008, CAP-010, CAP-016), four MISSING (CAP-001, CAP-004, CAP-006, CAP-018). The former FG-005 is carried as a COMPLETE Residual-Risk Capability (CAP-019), not a Functional Gap, per the CGA's own explicit, precedent-grounded reclassification.
- `docs/architecture/P3_01_DETERMINISTIC_EXECUTION_ORDERING_ARCHITECTURE_V1_2026-07-13.md`, `docs/architecture/P3_01_DETERMINISTIC_EXECUTION_ORDERING_SPECIFICATION_V1_2026-07-13.md`, `docs/architecture/certification/P3_01_FINAL_CERTIFICATION_V1_2026-07-13.md` - the certified P3-01 twelve-stage ordering, Failed-Tick semantics, and replay determinism this document does not reopen.
- `docs/architecture/P2_02A_POSITION_OWNERSHIP_ARCHITECTURE_V1_2026-07-10.md`, `docs/architecture/P2_03_FINANCIAL_OWNERSHIP_ARCHITECTURE_V1_2026-07-11.md`, `docs/architecture/P2_04_RISK_OWNERSHIP_ARCHITECTURE_V1_2026-07-13.md`, and their Final Certifications - the certified contract baseline this architecture must preserve without exception.
- Current runtime code at HEAD `f6fb7f3911a978884ca10b22a0eef832a52f9486`, re-traced in Section 5 against the exact `RunLoop.step()` sequence.

## 5. Repository-Grounded Current State

Repository state re-verified: branch `run-engine-consolidation-safety`, local HEAD and remote HEAD both `f6fb7f3911a978884ca10b22a0eef832a52f9486`, identical. `git status --short -- run_engine/` returns empty: `run_engine/` is unchanged since the FRA, SDA, and CGA were drafted, independently confirming every fresh repository fact those documents established remains valid evidence for this document.

The following facts, each individually re-confirmed for this document, ground every Architecture Decision in Section 28:

- `canonical_state.py:107-109`: `def get(self): return self.state` - a direct, uncopied reference.
- `loop.py:47`: `position_pre = self.cstate.get()["position"]`; `loop.py:90`: `canonical_state = self.cstate.get()` (Canonical Working State, consumed once, internally, by `RiskEngine.check` at `loop.py:92`); `loop.py:100`: `"state": self.cstate.get()` (the Tick-Complete result's own `"state"` field).
- `performance.py:4`: `self.stats = {}`, constructed once; `performance.py:20,25,29,34`: mutated in place across every call; `return self.stats` returns the identical object every time.
- `canonical_state.py:96-98`: `update_performance_metrics` stores the received reference directly, no copy.
- `canonical_enforcer.py:47-53`: `apply_risk` is the sole `apply_*` method returning `self.cs.get()` (the complete state dict) rather than a single named key; the other ten each return one key.
- `position.py:75-83`: `snapshot()` constructs a fresh dict literal on every call; `position.py:37-73`: `update_post_trade` mutates six of `PositionEngine`'s own instance attributes sequentially, without atomicity, before returning that fresh snapshot.
- `strategy.py:21,47,69` and `executor.py:15,22,28`: Strategy Selection, Execution Decision, and Execution Event are each freshly constructed dict literals on every call.
- `trade_lifecycle.py:8`: `LifecycleEvent` is `@dataclass(frozen=True)`; `trade_lifecycle.py:28`: `Trade` is a plain, internally-mutable dataclass, confined to `TradeLifecycleEngine`'s own private management.
- A scoped repository-wide search finds exactly one call site per `CanonicalState.update_*` method: every one inside `canonical_enforcer.py` except `update_tick` (`loop.py:42`, Runtime Tick's own explicitly Matrix-named exception).
- No consumer-side or engine-internal mutation of a received parameter was found in any of the fourteen active files (`main.py`, `loop.py`, `state.py`, `regime.py`, `strategy.py`, `decision.py` (confirmed inactive), `execution/executor.py`, `trade_lifecycle.py`, `position.py`, `pnl.py`, `risk.py`, `performance.py`, `canonical_state.py`, `canonical_enforcer.py`), independently re-read for this document.
- The four P3-01-named inactive directories (`run_engine/runtime/`, `run_engine/execution/` top-level, `run_engine/feedback/`, `run_engine/logging/`) and `run_engine/core/decision.py` remain confirmed unimported; `run_engine/core/position_sizing.py` and `run_engine/core/state_modulation.py`, newly named by the FRA, remain confirmed unimported.

**The four essential Capability Gaps, re-confirmed unchanged before any decision is made:** CAP-001 (`CanonicalState.get()` read-contract, MISSING, Governance), CAP-004 (Tick-Complete top-level aliasing, MISSING, Runtime), CAP-006 (Performance Metrics aliasing, MISSING, Runtime), CAP-010 (`apply_risk` return-contract inconsistency, PARTIAL, Runtime).

**FRA findings, re-confirmed unchanged: FG-001 through FG-004** (traceable to CAP-001, CAP-004, CAP-006, CAP-010 respectively); **VCF-001 through VCF-004** (fresh-construction convention for Position/Strategy Selection/Execution Decision/Execution Event; scalar immunity; Writer-on-Behalf-Of exclusivity; no consumer/engine mutation found); **DG-001, DG-002** (two newly-identified dormant files; a minor HOLD-path terminological imprecision); **VG-001** (Rule OM-004 never independently, systematically verified); **RR-001** (single-instance retained-reference risk), **RR-002** (Post-Exception Financial/Lifecycle Divergence, restated from P3-01, not resolved), and the **`PositionEngine` Partial-Mutation Residual Risk** (formerly FG-005, carried as a Residual Risk per the CGA's own reclassification, artificial-injection-only, transient, self-healing, P3-01-AD-004-compatible).

## 6. Scientific Definitions

Restated, not newly invented, from the Architecture Baseline and the FRA (Section 6), governing the rest of this document: **Single Source of Truth, Authoritative Owner, Computational Authority, Writer-on-Behalf-Of, Canonical Storage, Derived View, Canonical Working State, Tick-Complete Snapshot** - as defined in the Architecture Baseline. **Hidden Coupling, Aliasing, Object-Identity Isolation** - as defined in the FRA, Section 6, unchanged.

**Structural Independence** (introduced by this document) - the property that a returned or published value, once handed to a caller, contains no object (at any nesting depth) that its own producer, or any other component, will later mutate in a way observable through the returned reference. Structural Independence is stronger than object-identity distinctness at the top level alone: a top-level copy whose own nested values remain shared with a still-mutating source does not achieve Structural Independence for those nested values.

**Composite Isolation** (introduced by this document, Section 9) - the specific mechanism this Architecture adopts for `CanonicalState.get()`: a freshly-constructed shallow copy of the top-level state dictionary, taken on every call, combined with a binding requirement (Section 15) that every nested, dict-shaped canonical value already be, or become, Structurally Independent at its own publication time. Composite Isolation achieves full Structural Independence for the complete Tick-Complete result without requiring a single, recursive deep copy of the entire canonical state on every call.

## 7. Architecture Problem Statement

The CGA found four capabilities MISSING (CAP-001, CAP-004, CAP-006, CAP-018 - the last an aggregate synthesis of the first three plus two PARTIAL verification findings) and six PARTIAL (CAP-003, CAP-005, CAP-007, CAP-008, CAP-010, CAP-016), all traceable to a small number of Architecture-stage questions the FRA and SDA already isolated: the undecided `CanonicalState.get()` read-contract (CUO-01, now owned by this unit), the Tick-Complete result's own top-level and Performance-Metrics-specific aliasing, and the `CanonicalEnforcer.apply_risk` return-value inconsistency. This document exists to resolve every one of these, to formally ratify the seventeen already-COMPLETE capabilities as a binding architectural contract, and to convert the CGA's own remaining open items into a single, internally consistent target architecture - without reopening P3-01's own certified ordering or P2-02A/P2-03/P2-04's own certified ownership contracts, and without redesigning `PerformanceEngine`'s own accounting methodology (TD-004, P3-03's own scope).

## 8. Architecture Objectives

1. Resolve the `CanonicalState.get()` read-contract (CAP-001), closing the last item CUO-01 left open across this entire governance chain.
2. Resolve Tick-Complete Snapshot Stability, both as a general property (CAP-003) and for its two concrete violations - the top-level container (CAP-004) and Performance Metrics (CAP-006) - fully realizing AI-009 and AC-009 for the first time in this governance chain.
3. Resolve `CanonicalEnforcer.apply_risk`'s own return-contract inconsistency (CAP-010), bringing all eleven `apply_*` methods under one uniform contract.
4. Elevate the currently-observed, currently-conformant Producer fresh-construction convention (CAP-005, VCF-001) and Consumer non-mutation behaviour (CAP-007, CAP-008, VCF-004) into binding contracts, closing the remaining Governance and Verification gaps without requiring a new structural enforcement mechanism where copying already forecloses the risk.
5. Ratify every already-COMPLETE information-flow topology (Runtime Event, Lifecycle History, Position, Financial, Risk, Failure, HOLD, Alternative-Path, Traceability, Determinism - CAP-011 through CAP-015, CAP-017, CAP-020 through CAP-025) exactly as currently evidenced, introducing no change.
6. Formally ratify the Cross-Unit boundary (CAP-016, CAP-026, CAP-027): TD-004/Performance methodology remains P3-03's; TD-007 remains a future Runtime Control Unit's; P3-01's own ordering remains untouched; both Post-Exception-Divergence conditions (RR-002 and the `PositionEngine`-specific instance) remain documented, non-blocking Residual Risks, neither silently resolved nor upgraded to a Functional Gap.
7. Preserve every already-certified P2-02A/P2-03/P2-04/P3-01 contract without exception.

## 9. Canonical Read Model

`CanonicalState.get()` SHALL return a freshly-constructed shallow copy of its own top-level state dictionary, uniformly, on every call, for every caller - internal (mid-tick, e.g. `RiskEngine`) and external (post-Tick-Completion, the Tick-Complete result's own `"state"` field) alike (AD-001). No separate method or calling convention is introduced to distinguish internal from external access; both are served by the identical mechanism. A shallow copy alone is not, by itself, sufficient to guarantee full isolation of every nested value; this model is therefore explicitly paired with the Producer Isolation Model (Section 15) and the Nested Mutable Structures resolution (AD-009), which together guarantee that every dict-shaped nested value the shallow-copied top level references is itself already, or becomes, Structurally Independent (Section 6) at its own publication time. Together, these form Composite Isolation (Section 6), the read-contract this Architecture adopts.

## 10. Canonical Working State Model

Canonical Working State remains consumable, via the identical Canonical Read Model (Section 9), only by a component whose own ADR-010 execution position has already been reached in the current tick (AD-002, ratifying P3-01-AD-001, not reopened). `RiskEngine.check()` remains the sole mid-tick consumer, unchanged. Because every `get()` call now returns a shallow copy (AD-001), no mutation an internal consumer might perform on its own received copy can propagate back into `CanonicalState`'s own held state - Rule OM-004's own consumer-mutation prohibition is therefore structurally reinforced, though not structurally enforced beyond the copy boundary itself, for this consumption path. Future or not-yet-reached stages remain excluded by the twelve-stage ordering itself (P3-01-AD-001), not by any new mechanism this document introduces. This model does not decide, and explicitly defers to any future Runtime Safety consideration, whether a component's own legitimately-retained cross-tick private working state (for example, `PositionEngine`'s or `PerformanceEngine`'s own accumulators) requires an isolation mechanism distinct from the Canonical Working State boundary itself - that is CAP-019's own, already-resolved (COMPLETE, Residual-Risk Capability) scope, not reopened here (AD-020).

## 11. Tick-Complete Snapshot Model

A Tick-Complete result, once returned by `RunLoop.step()`, SHALL remain stable: no field of a previously-returned result SHALL change value as a consequence of any subsequently-executed tick (AD-003, fully resolving AI-009 and AC-009). This stability is achieved compositely: the result's own top-level `"state"` field is a fresh copy per AD-001/AD-004, and every dict-shaped nested value it contains (Position, Strategy Selection, Execution Decision, Execution Event, and, from this Architecture forward, Performance Metrics per AD-005) is itself Structurally Independent at its own publication time. Scalar values (Drawdown, Drawdown Ratio, `risk_allocation_factor`, Realized PnL, cumulative Realized PnL, Equity, Peak Equity, Runtime Status, Market Regime, Runtime Tick, Price) remain structurally immune to aliasing by Python's own scalar immutability, requiring no isolation mechanism (VCF-002, not reopened). This model does not require, and this Architecture does not introduce, a single atomic snapshot-construction operation distinct from `RunLoop.step()`'s own already-certified aggregate incremental-publication mechanism (P3-01-AD-003/VC-01, not reopened); stability is achieved entirely through per-object isolation at each object's own point of publication or read, not through a new snapshot-taking operation.

## 12. Information Lifetime Model

Every canonical runtime object possesses exactly one of three lifetimes, determined by this Architecture: **Ephemeral** (Canonical Working State, valid only for the duration of the internal read that produced the copy, superseded without consequence by the next tick's own values - applies to any mid-tick `get()` result); **Tick-Stable** (a value published as part of a Tick-Complete result, guaranteed stable for as long as the holder retains it, per the Tick-Complete Snapshot Model - applies to every field of a returned `RunLoop.step()` result); **Historical** (Lifecycle History, permanently retained, immutable once recorded, owned exclusively by `TradeLifecycleEngine`, never subject to the Tick-Stable lifetime's own per-tick supersession since it is never republished or replaced, only appended to - unchanged, not reopened). No canonical object possesses a fourth, undefined lifetime; every object named in the Runtime Ownership Matrix falls into exactly one of these three categories (Section 32).

## 13. Object Identity Model

Every dict-shaped or otherwise mutable canonical object published via `CanonicalEnforcer` SHALL possess an object identity distinct from the value it replaces (AD-007, ratifying and binding VCF-001, closing CAP-005's own general PARTIAL finding). This requirement extends to every nesting depth a given object contains (AD-009): a top-level container being freshly constructed does not, by itself, satisfy this model for any nested mutable value it still shares with a continuously-mutating source (the precise failure mode Performance Metrics currently exhibits, AD-005). Scalar values require no object-identity guarantee, being immutable by construction (VCF-002). A component's own legitimately-retained private working state (for example, `PositionEngine`'s or `RegimeClassifier`'s own cross-tick instance attributes) is explicitly exempt from this model, since that state is never itself published as a canonical object - only the fresh, independent value each component constructs FROM that state at publication time is subject to this model.

## 14. Producer-Consumer Model

Every Runtime Ownership Matrix row's own Producer, published object, and Primary Consumer(s) SHALL remain independently, repeatably verifiable (AD-007, AD-008, ratifying and closing the verification dimension of CAP-007/CAP-008, while leaving the underlying pairing itself, already CAP-013/CAP-014/CAP-015-conformant, unchanged). This model does not introduce a new Producer, a new Consumer, or a new published object beyond what the Runtime Ownership Matrix already names; it binds the currently-observed, currently-conformant pairing (FRA Section 10) as a governed contract, closing the Governance dimension of CAP-007 without altering the topology CAP-013/CAP-014/CAP-015 already ratify.

## 15. Producer Isolation Model

Every Producer SHALL, at the moment it hands a dict-shaped value to `CanonicalEnforcer` for publication, supply a value that is Structurally Independent (Section 6) from any object it will itself further mutate (AD-007). A Producer's own internal accumulator or working state MAY continue to exist and be privately mutated across ticks (matching `PositionEngine`'s own already-legitimate, P2-02A-certified pattern, and, from this Architecture forward, `PerformanceEngine`'s own pattern under AD-005) - what changes is only that the value handed to `CanonicalEnforcer` is never that same, continuously-mutated object. This model is already fully satisfied, without further change, for Position, Strategy Selection, Execution Decision, and Execution Event (VCF-001); it requires one functional change for Performance Metrics (AD-005).

## 16. Consumer Read-Only Model

No Primary Consumer SHALL mutate the runtime object it consumes (Rule OM-004, ratified, not reopened). This Architecture does NOT introduce a structural read-only enforcement mechanism (no `MappingProxyType` wrapper, no immutable-dataclass conversion, no copy-on-read guard beyond what AD-001/AD-007 already provide) (AD-008). This is a deliberate, justified minimality decision: because AD-001 (Canonical Read Model) and AD-007 (Producer Isolation) already guarantee that every value a consumer receives is a copy or a freshly-constructed object distinct from any canonical or producer-held original, the specific harm Rule OM-004 exists to prevent - a consumer's own mutation corrupting shared canonical or producer state - is already structurally foreclosed for every object those two decisions cover, without an additional wrapper layer. What remains open is independent verifiability (VG-001), which this model requires (a repeatable, independent procedure confirming no consumer mutates what it receives) without mandating a specific verification mechanism, deferred to the Specification stage.

## 17. Writer-on-Behalf-Of Model

`CanonicalEnforcer` remains the exclusive Writer-on-Behalf-Of publication path for every canonical object this document's scope covers, with the single, explicitly ratified exception of Runtime Tick, whose own Runtime Ownership Matrix row explicitly and uniquely names `RunLoop` itself (AD-018, ratifying P3-01-AD-002, not reopened). Every `CanonicalEnforcer.apply_*` method SHALL follow one uniform, consistent return-value contract: the specific canonical value(s) it itself just published, and nothing beyond that value - explicitly resolving `apply_risk`'s own current deviation (AD-006, closing CAP-010).

## 18. Runtime Event Model

Every explicit Runtime Event (currently realized, in the active trace, exclusively as `LifecycleEvent` instances) SHALL remain a frozen, structurally immutable object after construction, generated at exactly one call site per transition type, representing exactly one semantic transition (AD-010, ratifying AI-008/ADR-002, already fully conformant, CAP-011, not reopened). This model does not require introducing distinct event objects for the Decision, Financial, Risk, or Performance layers, which the active trace realizes as plain published values rather than discrete event objects - an already-ratified P3-01 characteristic (P3-01-AD-001's own observable-versus-structural normativity principle), not reopened by this document.

## 19. Lifecycle History Model

Lifecycle History remains exclusively owned by `TradeLifecycleEngine`, permanently retained (Historical lifetime, Section 12), never duplicated into `CanonicalState`, with completed records immutable (AD-011, ratifying AI-004/AI-012/Rule OM-005, already fully conformant, CAP-012, not reopened). History-consuming components (currently: `PositionEngine` via `current_position()`, `PnLEngine` via `trade_event`) receive freshly-constructed Derived Views (a plain dict, or the `LifecycleEvent` object itself, structurally immutable), never a live reference into `TradeLifecycleEngine`'s own internal `trades`/`failure_events` lists.

## 20. Position Information Flow Model

Position information flows exclusively as: Lifecycle Event/current position -> `PositionEngine` (Computational Authority) -> a Structurally Independent snapshot -> `CanonicalState` (Authoritative Owner, via `CanonicalEnforcer`) -> `PnLEngine`/`RiskEngine` (Primary Consumers) (AD-012, ratifying ADR-004, the Target Information Flow, and P2-02A, not reopened, already fully conformant, CAP-013). Exposure remains exclusively a derived property of Position (`side`, `quantity`, `last_price`), never an independently owned object. This ratification is confirmed, per the SDA's own Cycle Detection finding (SDA Section 16), independent of CAP-019's own separate classification: this flow's own topology-conformance does not depend on, and is not qualified by, the `PositionEngine` private-state self-consistency question CAP-019 already, separately, resolves.

## 21. Financial Information Flow Model

Financial information flows exclusively as: Lifecycle Facts + Entry Basis -> `PnLEngine` (Computational Authority) -> `CanonicalState` (Authoritative Owner, via `CanonicalEnforcer`) -> `RiskEngine` (Primary Consumer for Equity/Peak Equity) (AD-013, ratifying ADR-005/ADR-006, the Target Information Flow, and P2-03, not reopened, already fully conformant, CAP-014). Every financial value in this flow remains a Python scalar, structurally immune to aliasing (VCF-002).

## 22. Risk Information Flow Model

Risk information flows exclusively as: Canonical Financial State (Canonical Working State) + Position -> `RiskEngine` (Computational Authority) -> `CanonicalState` (Authoritative Owner, via `CanonicalEnforcer`) (AD-014, ratifying ADR-007, the Target Information Flow, and P2-04, not reopened, already fully conformant, CAP-015 for topology). The sole change within this flow's own scope is the Writer-on-Behalf-Of Model's own `apply_risk` return-contract correction (AD-006, AD-017): `apply_risk`'s own return value becomes the published Risk Metrics themselves, not the complete live `CanonicalState` dictionary. No downstream active consumer of Risk Metrics exists among the twenty-four P3-02 Functional Requirements (SDA Section 12, confirmed absence, not a gap); this Architecture does not introduce one.

## 23. Performance Information Flow Model

Performance information's own current-state shape (input: `decision`, `pnl`, `regime`, `trade_event`; output: a per-action statistics dictionary) remains unchanged in its own accounting methodology (AD-015, ratifying ADR-008, explicitly not redesigning TD-004's own eventual resolution, P3-03's scope, not reopened). What changes, exclusively within this model's own scope (object identity, Publication, Canonical Storage, Snapshot stability, Consumer boundaries, per the governing task's own explicit item 15 boundary): `PerformanceEngine`'s own publication of its per-tick statistics SHALL yield a Structurally Independent value at every nesting level (AD-005), not the same, continuously-mutated accumulator object; `CanonicalState.state["performance_metrics"]` and every Tick-Complete result's own `"performance"` field SHALL therefore remain Tick-Stable (Section 12) once published, exactly as every other dict-shaped canonical object already is or becomes under this Architecture. No new Performance Metric is introduced; no lifecycle-outcome-based accounting is introduced; TD-004 remains entirely untouched.

## 24. Failure Information Flow Model

A Failed Tick (P3-01-AD-004, not reopened) SHALL continue to produce no Tick-Complete result; consequently, no information from a Failed Tick ever becomes externally observable, regardless of how many `CanonicalEnforcer.apply_*` calls already executed internally before the interrupting exception (AD-016). Whatever subset of those calls already executed remains present in `CanonicalState`'s own internally-held state, valid and consumable by the next tick's own internal processing exactly as before AD-001, since AD-001's own copy-on-read semantics apply identically after a Failed Tick as during any normal tick - a fresh `get()` call after a Failed Tick returns a fresh copy reflecting whatever was already durably published. A genuine rejected lifecycle transition (`RUNTIME_FAILURE_EVENT`) SHALL continue to execute all twelve stages and reach Tick Completion, with Position/Financial/Performance fields unmutated (P3-01-AD-006, not reopened). Post-Exception Financial/Lifecycle Divergence (both the original TradeLifecycleEngine-versus-CanonicalState instance, RR-002, and the `PositionEngine`-private-state instance, CAP-019) SHALL remain explicitly documented, non-blocking Residual Risks; this model introduces no rollback, reset, recovery, or transaction mechanism to resolve either.

## 25. HOLD and No-Execution Information Flow Model

A `HOLD` or no-execution tick SHALL continue to execute all twelve ADR-010 stages, in the same order as any other tick, with every downstream stage producing a well-defined, numerically-unchanged result for a no-event input (AD-017, ratifying P3-01-AD-005, already fully conformant, CAP-022, not reopened). The Tick-Complete Snapshot Model's own stability guarantee (Section 11) applies identically to a HOLD tick's own returned result as to any other tick's; no special-casing is introduced.

## 26. Alternative Information Path Model

Exactly one active information-flow path is architecturally permitted: `run_engine/main.py` invoking `RunLoop.step()` (AD-019, ratifying P3-01-AD-009, already fully conformant, CAP-023, not reopened). `run_engine/core/decision.py`, the four P3-01-named inactive directories, and the two newly-identified dormant files (`position_sizing.py`, `state_modulation.py`) remain classified exactly as the FRA established - confirmed unimported, structurally isolated, reserved for Phase 6 Repository Consolidation's own future classification, not decided here. No alternative active path may bypass this Architecture's own Canonical Read Model, Producer Isolation Model, or Writer-on-Behalf-Of Model.

## 27. Cross-Unit Boundary Model

Six items are formally ratified as outside this unit's own resolution scope (AD-020): P3-01's own twelve-stage ordering, Tick-Complete Publication semantics, and Failed-Tick semantics remain entirely unchanged, not reopened. TD-004 (Lifecycle-based Performance Evaluation) and `PerformanceEngine`'s own broader accounting methodology remain P3-03's own scope; this Architecture's own AD-005/AD-015 explicitly and exclusively address object-identity discipline, not methodology. TD-007 (RunLoop Lifecycle Control Surface) remains a future Runtime Control Unit's own scope, not conflated with this Architecture's own Information Lifetime or Failure Information Flow decisions. Post-Exception Financial/Lifecycle Divergence (RR-002) remains a documented, non-blocking Residual Risk, exactly as the P3-01 Final Certification classified it, not silently presented as resolved. The `PositionEngine` Partial-Mutation Residual Risk (formerly FG-005) remains classified a Residual Risk, per the CGA's own explicit, precedent-grounded reclassification - this Architecture does not upgrade it to a P3-02 Functional Gap, and does not introduce a rollback, reset, or transaction mechanism for it. No Persistence, Recovery, or Schema Evolution architecture is introduced (ADR-012, Deferred Scope, not reopened).

## 28. Architecture Decisions

### P3-02-AD-001 - CanonicalState Read Contract

**Title.** CanonicalState Read Contract: Composite Isolation via Uniform Shallow Copy.

**Motivation.** CAP-001 (MISSING) found no binding decision exists for `CanonicalState.get()`'s own read semantics; `get()` currently returns a live reference to `CanonicalState`'s own internal `self.state` dictionary (`canonical_state.py:107-109`), the root cause of CAP-004 (Tick-Complete top-level aliasing) and a contributing structural condition for CAP-003's own PARTIAL status. This is CUO-01, forwarded by P3-01 and formally received into this unit's own scope by the FRA (Section 8).

**Decision.** `CanonicalState.get()` SHALL return a freshly-constructed shallow copy of its own top-level state dictionary on every call. This applies uniformly to every caller, internal and external, with no separate method or calling convention distinguishing the two. Live-reference semantics (the current implementation), full recursive deep-copy semantics, and a bare read-only view (for example, a `MappingProxyType` wrapper with no underlying copy) are each explicitly rejected as the sole mechanism: live reference is the demonstrated root cause of CAP-004; a full deep copy on every call (approximately fifteen or more calls per tick, per the FRA's own trace) would recursively copy substantial state that is either already scalar-immune (VCF-002) or already, or soon to be, independently isolated at its own publication boundary (AD-007, AD-009), making full recursion unnecessary cost without additional isolation benefit; a bare read-only view wraps rather than freezes its own underlying object, and therefore does not, by itself, prevent a later tick's own top-level key reassignment from becoming visible through an already-returned view - it addresses Rule OM-004's own mutation-prevention concern but not the Tick-Complete Snapshot Model's own point-in-time stability requirement. This decision, combined with AD-007 and AD-009, constitutes Composite Isolation (Section 6).

**Scientific Justification.** AI-002 (Unique Ownership) and Rule OM-006 (CanonicalState exclusively owns active runtime state) presuppose one well-defined access contract; an undefined contract leaves every consumer's own aliasing exposure undefined by construction. A shallow copy taken at every call boundary is sufficient, and minimal, once every nested value the copy references is independently guaranteed Structurally Independent (Section 6) - the "no speculation, minimal already-evidenced option" methodology this governance chain has consistently applied.

**Information-Flow Consequences.** Every `get()` call becomes a distinct object-identity boundary; a value obtained from one call is never affected by any subsequent write, regardless of how many further ticks or internal writes occur afterward.

**Ownership Consequences.** None. `CanonicalState` remains the exclusive Authoritative Owner and Canonical Storage of active runtime state; this decision changes only the read mechanism, not ownership.

**Producer Consequences.** None directly; Producers already publish via `CanonicalEnforcer`, unaffected by how `get()` itself is later read.

**Consumer Consequences.** Every consumer, internal or external, now receives a value it may safely retain across ticks without further aliasing exposure at the top level, contingent on AD-007/AD-009 for nested values.

**Publication Consequences.** None; this decision concerns reading, not publishing.

**Mutation and Aliasing Consequences.** Closes CAP-004 in full (Section 28, AD-004). Provides the top-level component of CAP-003's own resolution (Section 28, AD-003). Does not, by itself, close CAP-006 (Performance Metrics' own nested aliasing), which requires AD-005 in addition.

**Compatibility Constraints.** `CanonicalState`'s own schema, default values, and semantic meaning of every key remain unchanged; only the read mechanism changes. No P2-02A, P2-03, or P2-04 contract is affected, since every consumer of a scalar value is unaffected by copy-versus-reference semantics (VCF-002).

**Failure Consequences.** A shallow copy taken after a Failed Tick correctly reflects whatever subset of that tick's own `apply_*` calls already completed (AD-016); no rollback or reset semantics are introduced or required by this decision.

**Determinism Consequences.** None; the copy operation itself is deterministic and introduces no new source of nondeterminism. Directly resolves the specific single-instance retained-reference risk this document's own FR-022/CAP-020 lineage names (RR-001), for every field this decision and AD-007/AD-009 jointly cover.

**Acceptance Criteria.** `id()` of two values returned by two separate `CanonicalState.get()` calls, with no intervening write to the copied key, are distinct objects; a value returned by `get()` before a subsequent tick's own write to that key remains, at every field, equal to the value that was true when it was returned.

**Traceability.** FR-001; DEP-001 through DEP-005; CAP-001, CAP-004; AI-002; AI-009; Rule OM-006; CUO-01.

**Scope Boundary.** Does not itself guarantee Structural Independence for nested mutable values; that is AD-007 and AD-009's own scope. Does not introduce a distinct method for Canonical Working State access versus Tick-Complete access.

---

### P3-02-AD-002 - Canonical Working State Semantics

**Title.** Canonical Working State Semantics: Internal-Only, Read-Only-by-Copy Consumption.

**Motivation.** CAP-002 was already COMPLETE; this decision formally ratifies that finding under the new Canonical Read Model (AD-001) rather than reopening it.

**Decision.** Canonical Working State SHALL remain consumable, via the identical `CanonicalState.get()` mechanism AD-001 establishes, only by a component whose own ADR-010 execution position has already been reached in the current tick. `RiskEngine.check()` SHALL remain the sole such consumer. No component SHALL consume a Canonical Working State value corresponding to a stage not yet reached. Because AD-001 now makes every `get()` call return a fresh copy, mutation of a received Canonical Working State copy by an internal consumer SHALL have no effect on `CanonicalState`'s own held state - a structural reinforcement of Rule OM-004 for this specific consumption path, though not itself an exhaustive enforcement mechanism (AD-008).

**Scientific Justification.** The Baseline's own Canonical Working State definition already requires internal-only, order-gated visibility; AD-001's own uniform copy semantics satisfies this without requiring a separate access method, consistent with this document's own minimality principle.

**Information-Flow Consequences.** None beyond AD-001's own already-stated consequences, applied to this specific consumption path.

**Ownership Consequences.** None.

**Producer Consequences.** None.

**Consumer Consequences.** `RiskEngine` continues to receive a value reflecting every write completed before its own call, per its own already-certified ADR-010 execution position; no functional change to what `RiskEngine` observes.

**Publication Consequences.** None.

**Mutation and Aliasing Consequences.** Closes CAP-002's own remaining ratification obligation under the new read model.

**Compatibility Constraints.** Preserves `RiskEngine`'s own already-certified P2-04 input contract exactly.

**Failure Consequences.** Not applicable; governed by AD-016.

**Determinism Consequences.** None; ratifies already-conformant, deterministic behaviour.

**Acceptance Criteria.** A fresh trace confirms Canonical Working State is consumed only at or after its own producing stage, using the AD-001 mechanism, at any future HEAD.

**Traceability.** FR-002; DEP-002, DEP-006, DEP-042; CAP-002; P3-01-AI-003, P3-01-AI-004; AC-009, AC-010.

**Scope Boundary.** Does not decide whether any component's own legitimately-retained private cross-tick state (distinct from Canonical Working State itself) requires isolation; that is CAP-019's own, already-resolved scope (AD-020).

---

### P3-02-AD-003 - Tick-Complete Snapshot Stability

**Title.** Tick-Complete Snapshot Stability: Full Realization of AI-009 and AC-009.

**Motivation.** CAP-003 (PARTIAL) found the overall Tick-Complete result stable for most of its own content by convention, but not uniformly, since its own top-level container (CAP-004) and Performance Metrics (CAP-006) violated the stability AI-009 and AC-009 require.

**Decision.** A Tick-Complete result, once returned by `RunLoop.step()`, SHALL remain stable in every one of its own fields for as long as it is retained by a caller: no subsequently-executed tick SHALL cause any field of a previously-returned result to change value. This stability SHALL be achieved compositely: the top-level container via AD-001/AD-004; every dict-shaped nested value via AD-007/AD-009, specifically including Performance Metrics via AD-005; every scalar value inherently, by Python's own immutability (VCF-002). This decision does not require, and does not introduce, a single, additional, dedicated snapshot-construction operation distinct from the already-certified aggregate incremental-publication mechanism (P3-01-AD-003/VC-01, not reopened) - stability is achieved through per-object isolation at each object's own publication or read boundary.

**Scientific Justification.** AI-009 ("Every runtime tick SHALL terminate with one Tick-Complete CanonicalState Snapshot") and AC-009 ("exactly one externally observable Tick-Complete CanonicalState Snapshot") both presuppose a point-in-time value under the ordinary meaning of "Snapshot"; a container whose own fields continue to change after being returned does not satisfy this term. This decision closes the gap between the term's own already-certified use (P3-01) and its own full, object-identity-level realization, first identified by this unit's own FRA.

**Information-Flow Consequences.** A Tick-Complete result becomes a genuinely immutable-in-effect value once returned, safe for a future consumer to retain across arbitrarily many further ticks.

**Ownership Consequences.** None; no Authoritative Owner or Computational Authority changes.

**Producer Consequences.** Every Producer whose own published object becomes part of a Tick-Complete result is bound by AD-007's own Structural Independence requirement.

**Consumer Consequences.** A future consumer retaining a Tick-Complete result across ticks now observes correct, stable values, closing Residual Risk RR-001 for every field this decision covers.

**Publication Consequences.** None beyond AD-001, AD-005, AD-007's own already-stated consequences.

**Mutation and Aliasing Consequences.** This decision is the synthesis point for CAP-003, CAP-004, and CAP-006's own individual resolutions.

**Compatibility Constraints.** Preserves P3-01-AD-003/VC-01's own aggregate incremental-publication mechanism exactly; no atomic publish/commit action is introduced.

**Failure Consequences.** A Failed Tick continues to produce no Tick-Complete result at all (P3-01-AD-004, not reopened); this decision's own stability guarantee applies only to results that are, in fact, returned.

**Determinism Consequences.** Fully resolves Residual Risk RR-001 (single-instance retained-reference risk) for every field AD-001/AD-005/AD-007 cover; does not extend to, and does not claim to resolve, the pre-existing P3-01 qualification regarding retry-after-Failed-Tick non-determinism (not reopened).

**Acceptance Criteria.** A Tick-Complete result captured at tick N, re-inspected after ticks N+1 through N+k execute (for any k >= 1), remains, at every field including every nested field, functionally identical to its own value at the moment of return.

**Traceability.** FR-003; DEP-001, DEP-007, DEP-009; CAP-003; AI-009; AC-009; Tick-Complete Snapshot definition.

**Scope Boundary.** Does not extend to Canonical Working State's own intentionally non-isolated, internal, mid-tick consumption (AD-002).

---

### P3-02-AD-004 - Top-Level Result Aliasing

**Title.** Top-Level Result Aliasing: Structural Elimination via AD-001.

**Motivation.** CAP-004 (MISSING) found `RunLoop.step()`'s own returned `"state"` field object-identical to `CanonicalState`'s own internally-held dictionary, empirically confirmed to silently reflect later ticks' own values.

**Decision.** `RunLoop.step()`'s own `"state"` field SHALL NOT be, and under this Architecture SHALL never again become, the identical object as `CanonicalState`'s own internally-held dictionary. This is achieved entirely as a structural, automatic consequence of AD-001: since `loop.py:100`'s own call to `self.cstate.get()` already invokes the same `get()` method AD-001 requires to return a fresh shallow copy on every call, no mechanism beyond AD-001 is required, defined, or permitted for this specific case.

**Scientific Justification.** A targeted fix specific to this one call site would introduce an inconsistency with every other `get()` call site's own semantics; resolving it as a direct consequence of the general read-contract decision (AD-001) is the minimal, already-evidenced, non-duplicative resolution.

**Information-Flow Consequences.** The Tick-Complete result's own `"state"` field becomes Tick-Stable (Section 12), closing the single most concretely demonstrated aliasing finding this governance chain has produced.

**Ownership Consequences.** None.

**Producer Consequences.** None beyond AD-001's own already-stated consequences.

**Consumer Consequences.** A caller holding `result["state"]` across ticks now observes stable, correct values.

**Publication Consequences.** None; `RunLoop.step()`'s own publication sequence (the twelve ADR-010 stages) is entirely unchanged.

**Mutation and Aliasing Consequences.** Fully closes CAP-004.

**Compatibility Constraints.** No change to `loop.py`'s own stage sequence, call order, or any other field of the returned dictionary.

**Failure Consequences.** Not applicable; a Failed Tick produces no Tick-Complete result at all (P3-01-AD-004, not reopened).

**Determinism Consequences.** Removes the top-level component of Residual Risk RR-001.

**Acceptance Criteria.** `id(result_tick_N["state"])` differs from `id(engine.cstate.state)` immediately after every call to `RunLoop.step()`.

**Traceability.** FR-003; DEP-001, DEP-007; CAP-004; AI-009; AC-009; Functional Gap FG-002.

**Scope Boundary.** Introduces no mechanism beyond AD-001; does not itself address any nested value's own aliasing (AD-005, AD-009).

---

### P3-02-AD-005 - Performance-Metrics Object Identity

**Title.** Performance-Metrics Object Identity: Structurally Independent Publication, Methodology Unchanged.

**Motivation.** CAP-006 (MISSING) found `PerformanceEngine.update()`'s own returned and published value to be the identical, continuously-mutated `self.stats` object on every call, for the entire lifetime of the runtime session - the more persistent and, per the targeted review already delivered this session, the more severe of the two proven aliasing findings.

**Decision.** `PerformanceEngine` MAY continue to retain and privately mutate its own internal accumulator (`self.stats`) across ticks; this is legitimate Computational-Authority working state, directly analogous to `PositionEngine`'s own already-certified private cross-tick state (P2-02A Section 13). `PerformanceEngine.update()` SHALL, however, at the point it returns the value `RunLoop` publishes via `CanonicalEnforcer.apply_performance_metrics`, supply a value that is Structurally Independent (Section 6) from its own accumulator at every nesting level the accumulator itself mutates - specifically including each per-action inner dictionary (`'pnl'`, `'trades'`, `'winrate'`), not merely the outer dictionary's own top level. No concrete Python mechanism (copy method, data structure change, or otherwise) is specified; only this functional property is decided, deferred to the Specification stage.

**Scientific Justification.** Rule IF-001 ("information already produced upstream shall never be reconstructed downstream") and the Derived View definition ("may be regenerated at any time") both presuppose that publication yields a value distinct from any object still subject to further mutation; a value that is the same object as a continuously-mutated accumulator cannot be a Derived View in the sense the Baseline defines. Treating Performance Metrics identically to Position (already fresh-constructed) removes the sole confirmed exception to the Producer Isolation Model without introducing a new principle.

**Information-Flow Consequences.** `CanonicalState.state["performance_metrics"]` and every Tick-Complete result's own `"performance"` field become Tick-Stable, matching every other dict-shaped canonical object.

**Ownership Consequences.** None; `PerformanceEngine` remains the exclusive Computational Authority for Performance Metrics; `CanonicalState` remains the Authoritative Owner.

**Producer Consequences.** `PerformanceEngine`'s own internal accumulation logic (the `+=`/weighted-average update formulas) is entirely unchanged; only the shape of the value it hands to its own caller for publication changes.

**Consumer Consequences.** Any consumer of Performance Metrics (including a future retaining consumer) now observes stable, correct, tick-specific values.

**Publication Consequences.** `CanonicalEnforcer.apply_performance_metrics`'s own contract (accept a value, store it, return the stored value) is unchanged; it now receives, and stores, a Structurally Independent value rather than the accumulator itself.

**Mutation and Aliasing Consequences.** Fully closes CAP-006, the most severe of the two proven MISSING Runtime capabilities.

**Compatibility Constraints.** No change to the accounting formulas (`'pnl'`, `'trades'`, `'winrate'` computation), the statistics dictionary's own key structure, or `PerformanceEngine`'s own decision-based (not lifecycle-outcome-based) accounting basis - TD-004 remains entirely untouched, and this decision does not advance or preempt its own eventual P3-03 resolution.

**Failure Consequences.** Not applicable beyond AD-016's own general treatment.

**Determinism Consequences.** Removes the Performance-Metrics component of Residual Risk RR-001.

**Acceptance Criteria.** `id()` of the value published at tick N differs, at every nesting level, from `id()` of the value published at tick N+1; a Performance Metrics value captured at tick N and re-inspected after further ticks execute remains functionally identical to its own value at the moment of capture.

**Traceability.** FR-004; DEP-008, DEP-009, DEP-019, DEP-035, DEP-050; CAP-006; Rule IF-001; Derived View definition; AI-009; AC-009; Functional Gap FG-003; TD-004 (not reopened).

**Scope Boundary.** Does not redesign `PerformanceEngine`'s own accounting methodology; does not introduce a new Performance Metric; does not resolve or advance TD-004; does not specify a concrete Python mechanism.

---

### P3-02-AD-006 - CanonicalEnforcer Return-Contract Consistency

**Title.** CanonicalEnforcer Return-Contract Consistency: apply_risk Aligned to the Uniform Contract.

**Motivation.** CAP-010 (PARTIAL) found `apply_risk` the sole `apply_*` method returning the complete live `CanonicalState.state` dictionary rather than the single canonical value it itself publishes, a deviation from the otherwise-uniform ten-method contract.

**Decision.** `CanonicalEnforcer.apply_risk`'s own return value SHALL be brought into conformance with the uniform contract every other `apply_*` method follows: it SHALL return only the Risk Metrics it itself publishes (Drawdown, Drawdown Ratio, `risk_allocation_factor`) via `CanonicalState.update_risk`, not the complete live state dictionary. No input key `RiskEngine.check()`'s own returned dictionary carries for read-only, pass-through context (`equity`, `peak_equity`, already separately owned and published by `PnLEngine`, not written by `update_risk`) SHALL appear in `apply_risk`'s own return value. Every `CanonicalEnforcer.apply_*` method SHALL, from this Architecture forward, follow exactly this uniform semantic return-contract: the specific canonical value(s) the method itself writes or confirms, and nothing else.

**Scientific Justification.** Consistency of a Writer-on-Behalf-Of's own publication contract is a precondition for any future consumer to rely on that contract without individually inspecting each method's own implementation; an unexplained, single exception increases the risk of an unintended full-state exposure to a future caller that does use the return value, which the current implementation's own zero-consumption of `apply_risk`'s own return value has so far masked.

**Information-Flow Consequences.** `apply_risk`'s own return value becomes meaningfully scoped to Risk Metrics specifically, matching the Risk Information Flow Model (Section 22).

**Ownership Consequences.** None; Risk Metrics' own Computational Authority (`RiskEngine`) and Authoritative Owner (`CanonicalState`) are unchanged.

**Producer Consequences.** None beyond the return-value shape itself; `RiskEngine.check()`'s own computation is entirely unchanged.

**Consumer Consequences.** Any future consumer of `apply_risk`'s own return value (currently none, per the active trace) will receive a correctly-scoped value rather than the complete live state dictionary.

**Publication Consequences.** `apply_risk` continues to write exactly the same three `CanonicalState` keys it already writes via `update_risk`; only its own return value's own shape changes.

**Mutation and Aliasing Consequences.** Closes CAP-010; incidentally, since the corrected return value is a subset of scalars (or, if returned as a dict, a freshly-scoped dict of scalars), it introduces no new aliasing surface, consistent with AD-007/AD-009.

**Compatibility Constraints.** No change to `RiskEngine.check()`'s own formula, `CanonicalState.update_risk()`'s own write behaviour, or any of the three published Risk Metric values themselves; P2-04's own certified contract is unaffected.

**Failure Consequences.** Not applicable.

**Determinism Consequences.** None; this decision does not affect computation, only a currently-unconsumed return-value shape.

**Acceptance Criteria.** `apply_risk`'s own return value contains exactly the Risk Metrics `update_risk` itself just wrote, matching the shape every other `apply_*` method already follows; the complete `CanonicalState.state` dictionary is never returned by any `apply_*` method after this decision is implemented.

**Traceability.** FR-007; DEP-015; CAP-010; Rule OM-003 (related, not violated); Functional Gap FG-004.

**Scope Boundary.** Does not specify a concrete Python signature. Does not change which three keys `apply_risk`/`update_risk` write.

---

### P3-02-AD-007 - Producer Isolation

**Title.** Producer Isolation: Structural Independence at Publication, Binding for Every Producer.

**Motivation.** CAP-005 (PARTIAL) found the currently-conformant fresh-construction convention (VCF-001) unenforced by any contract, type system, or runtime check - a behavioural observation, not a governed property - with Performance Metrics already demonstrating the convention's own fragility (CAP-006).

**Decision.** Every Producer SHALL, at the moment it hands a dict-shaped (or otherwise mutable) value to `CanonicalEnforcer` for publication, supply a value that is Structurally Independent from any object that Producer will itself further mutate, at every nesting level. A Producer's own private, internally-retained working state (cross-tick accumulators, computational scratch state) MAY continue to exist and be mutated privately; only the value handed to `CanonicalEnforcer` is bound by this decision. This requirement is already fully satisfied, without further change, for Position (`PositionEngine.snapshot()`), Strategy Selection and Execution Decision (`StrategySelector.select`/`decide`), and Execution Event (`Executor.execute`) - each already constructs a fresh dict literal on every call (VCF-001). It requires one functional change, specified by AD-005, for Performance Metrics.

**Scientific Justification.** Elevates an already-observed, already-conformant convention into a binding architectural contract, removing the single confirmed exception (Performance Metrics) and foreclosing any future silent reintroduction of a similar exception by a new or modified Producer.

**Information-Flow Consequences.** Every canonical publication becomes, by contract rather than mere convention, a genuinely independent Derived View.

**Ownership Consequences.** None; no Computational Authority or Authoritative Owner changes for any object.

**Producer Consequences.** Binding, going forward, on every current and future Producer: `StateEngine`, `RegimeClassifier`, `StrategySelector`, `Executor`, `TradeLifecycleEngine`, `PositionEngine`, `PnLEngine`, `RiskEngine`, `PerformanceEngine`.

**Consumer Consequences.** Every consumer may safely retain any published value without aliasing exposure to its own producer's own subsequent mutation.

**Publication Consequences.** No change to which object publishes which canonical value (the Runtime Ownership Matrix is unchanged); only the object-identity property of what is published is now contractually guaranteed.

**Mutation and Aliasing Consequences.** Closes the general-convention dimension of CAP-005; provides the general mechanism AD-005 applies specifically to Performance Metrics.

**Compatibility Constraints.** No formula, computation, or ownership change for any Producer; P2-02A, P2-03, P2-04 are unaffected, since every already-conformant Producer requires no change.

**Failure Consequences.** Not applicable directly.

**Determinism Consequences.** None beyond what AD-003's own Tick-Complete Snapshot Stability already establishes.

**Acceptance Criteria.** For every canonical Producer, `id()` of the value published at tick N differs, at every nesting level, from `id()` of the value published at tick N+1, whenever a publication occurs at both ticks.

**Traceability.** FR-004, FR-005; DEP-008, DEP-009, DEP-011 through DEP-014; CAP-005, CAP-006, CAP-007; Rule IF-001; Derived View definition; Verified Conformant Finding VCF-001.

**Scope Boundary.** Does not require immutability of an object's own internals beyond independence from its own producer's own future mutation; does not select a specific isolation mechanism (copy, immutable construction, or otherwise), deferred to the Specification stage.

---

### P3-02-AD-008 - Consumer Read-Only Discipline

**Title.** Consumer Read-Only Discipline: Behavioural Contract, Independently Verifiable, No Structural Wrapper.

**Motivation.** CAP-007 and CAP-008 (both PARTIAL) found the underlying non-mutation behaviour already correct (VCF-004) but lacking any independent, repeatable verification procedure (VG-001).

**Decision.** No Primary Consumer SHALL mutate the runtime object it consumes (Rule OM-004, ratified). This Architecture does NOT introduce a structural read-only enforcement mechanism (no `MappingProxyType` wrapper, no immutable-dataclass conversion, no additional copy-on-read guard beyond what AD-001 and AD-007 already provide) as a general requirement for every consumer relationship. This non-mutation property SHALL, however, be independently and repeatably verifiable, not solely maintained by manual source inspection; the specific verification mechanism (a dedicated test suite, a static analysis check, or another repeatable procedure) is not specified here, deferred to the Specification stage.

**Scientific Justification.** Because AD-001 (Canonical Read Model) and AD-007 (Producer Isolation) already guarantee that every value a consumer receives is either a copy (`CanonicalState.get()`'s own output) or a freshly, independently constructed object (every Producer's own published value), the specific harm Rule OM-004 exists to prevent - a consumer's own mutation corrupting shared canonical or producer-held state - is already structurally foreclosed for every object those two decisions cover. Introducing an additional structural wrapper on top of an already-copied or already-independent value would add complexity without closing any remaining risk, violating this governance chain's own minimality principle (AI-013).

**Information-Flow Consequences.** None beyond AD-001/AD-007's own already-stated consequences.

**Ownership Consequences.** None.

**Producer Consequences.** None beyond AD-007's own already-stated consequences.

**Consumer Consequences.** Every named Primary Consumer (`StrategySelector`, `Executor`, `TradeLifecycleEngine`, `PositionEngine`, `PnLEngine`, `RiskEngine`, `PerformanceEngine`) remains bound by Rule OM-004 as a behavioural contract, now subject to a future independent verification obligation.

**Publication Consequences.** None.

**Mutation and Aliasing Consequences.** Closes the Verification dimension of CAP-007/CAP-008, contingent on the Specification stage defining the actual verification procedure.

**Compatibility Constraints.** No change to any consumer's own existing, already-conformant behaviour.

**Failure Consequences.** Not applicable.

**Determinism Consequences.** None.

**Acceptance Criteria.** A repeatable, independent procedure exists and confirms, for every Primary Consumer named in the Runtime Ownership Matrix, that the object it receives is unchanged in every field after the consuming call returns.

**Traceability.** FR-005, FR-017; DEP-003, DEP-004, DEP-010; CAP-007, CAP-008; Rule OM-004; AC-002; AC-010; Verification Gap VG-001; Verified Conformant Finding VCF-004.

**Scope Boundary.** Does not specify a concrete verification mechanism; does not introduce a structural enforcement wrapper.

---

### P3-02-AD-009 - Nested Mutable Structures

**Title.** Nested Mutable Structures: Full-Depth Structural Independence, Standing Requirement.

**Motivation.** CAP-005's own general finding, and CAP-006's own specific finding, both concern nested (not merely top-level) mutable structure; a decision naming this explicitly, and extending it as a standing design constraint, is required so that AD-001's own shallow-copy mechanism is not silently assumed sufficient on its own.

**Decision.** Every canonical object possessing nested mutable structure (currently: Performance Metrics alone, a dictionary of per-action dictionaries) SHALL have every nesting level's own Structural Independence guaranteed at its own publication time, per AD-005/AD-007 - a shallow copy of only the outermost level is explicitly insufficient for such an object and SHALL NOT be treated as satisfying this Architecture's own isolation requirements. Every canonical object without nested mutable structure (Position, Strategy Selection, Execution Decision, Execution Event, and every scalar value) requires no isolation mechanism beyond the outermost level, since a single-level dictionary of scalars is already fully isolated once the dictionary itself is a distinct object. Any future canonical object introducing nested mutable structure SHALL be subject to the identical full-depth isolation requirement this decision establishes for Performance Metrics, as a standing design constraint for this unit's own scope, not merely a one-time fix.

**Scientific Justification.** A shallow copy's own well-known limitation - that it does not decouple nested mutable values - is precisely why AD-001 alone does not close CAP-006; naming this explicitly prevents a future Specification or Implementation from mistakenly treating a shallow, single-level fix as sufficient for a multiply-nested object.

**Information-Flow Consequences.** Establishes the precise depth requirement AD-005's own Performance Metrics fix must satisfy.

**Ownership Consequences.** None.

**Producer Consequences.** Directly specializes AD-007 for any Producer whose own published object has nested mutable structure.

**Consumer Consequences.** None beyond AD-007/AD-008's own already-stated consequences.

**Publication Consequences.** None beyond AD-005's own already-stated consequences.

**Mutation and Aliasing Consequences.** Prevents a partial, top-level-only resolution of CAP-006 from being mistaken for a complete one.

**Compatibility Constraints.** None beyond AD-005's own.

**Failure Consequences.** Not applicable.

**Determinism Consequences.** None beyond AD-003/AD-005's own already-stated consequences.

**Acceptance Criteria.** For Performance Metrics specifically, `id()` of every per-action inner dictionary published at tick N differs from `id()` of the corresponding inner dictionary published at tick N+1, in addition to the outer dictionary's own distinct identity.

**Traceability.** FR-004; DEP-009; CAP-005, CAP-006; Derived View definition; AI-009.

**Scope Boundary.** Does not itself specify the mechanism by which full-depth independence is achieved; that is AD-005's and the Specification stage's own scope.

---

### P3-02-AD-010 - Runtime Event Identity and Semantic Stability

**Title.** Runtime Event Identity and Semantic Stability Ratification.

**Motivation.** CAP-011 was already COMPLETE; this decision formally ratifies that finding.

**Decision.** Every explicit Runtime Event (currently realized exclusively as `LifecycleEvent` instances) SHALL remain a frozen, structurally immutable dataclass after construction, generated at exactly one call site per transition type (`_open_trade`, `_scale_in`, `_partial_close`, `_full_close`, `_failure_event`), representing exactly one semantic transition. Events SHALL be passed between Producer (`TradeLifecycleEngine`) and Consumer (`PositionEngine`, `PnLEngine`) unchanged, by reference, since their own frozen construction already makes reference-sharing safe (no consumer can mutate a frozen dataclass regardless of how it is passed). This decision does not require introducing distinct event objects for the Decision, Financial, Risk, or Performance layers, realized in the active trace as plain published values rather than discrete event objects - an already-ratified P3-01 characteristic (P3-01-AD-001's own observable-versus-structural normativity principle), not reopened.

**Scientific Justification.** AI-008 ("Every runtime state transition SHALL originate from one explicit Runtime Event... implicit runtime mutations are prohibited") is already fully satisfied for the Lifecycle Event layer by Python's own `frozen=True` construction, requiring no further mechanism.

**Information-Flow Consequences.** None; ratifies already-conformant behaviour.

**Ownership Consequences.** None.

**Producer Consequences.** None; `TradeLifecycleEngine`'s own event-generation logic is unchanged.

**Consumer Consequences.** None; existing event consumers are unaffected.

**Publication Consequences.** None.

**Mutation and Aliasing Consequences.** Frozen dataclasses are structurally immune to the aliasing concerns AD-001/AD-005/AD-007 address for mutable dict-shaped objects; no isolation mechanism is required for `LifecycleEvent` instances.

**Compatibility Constraints.** Preserves ADR-002's own event model and ADR-011's own Runtime Failure Event semantics exactly.

**Failure Consequences.** `RUNTIME_FAILURE_EVENT` generation remains governed exclusively by `TradeLifecycleEngine`'s own lifecycle-transition-rejection logic (AD-016, not extended to Failed Ticks).

**Determinism Consequences.** None; ratifies already-deterministic behaviour.

**Acceptance Criteria.** A fresh trace confirms every `LifecycleEvent.event_type` still originates from exactly one call site, and the dataclass remains frozen, at any future HEAD.

**Traceability.** FR-010; DEP-023, DEP-024, DEP-044; CAP-011; AI-008; ADR-002.

**Scope Boundary.** Does not introduce distinct event objects for the Decision/Financial/Risk/Performance layers.

---

### P3-02-AD-011 - Lifecycle History Information Flow

**Title.** Lifecycle History Information Flow Ratification.

**Motivation.** CAP-012 was already COMPLETE; this decision formally ratifies that finding.

**Decision.** Lifecycle History SHALL remain exclusively owned by `TradeLifecycleEngine` (Historical lifetime, Section 12), SHALL NOT be duplicated into `CanonicalState`, and completed records SHALL remain immutable. History-consuming components SHALL continue to receive freshly-constructed Derived Views (`current_position()`'s own already-fresh dict) or structurally immutable event objects (AD-010), never a live reference into `TradeLifecycleEngine`'s own internal `trades`/`failure_events` lists.

**Scientific Justification.** AI-004 (Immutable Lifecycle History) and AI-012 (Operational and Historical Separation) are already fully satisfied; ratification, not a new mechanism, is required.

**Information-Flow Consequences.** None; ratifies already-conformant behaviour.

**Ownership Consequences.** None; `TradeLifecycleEngine` remains the exclusive Authoritative Owner of Lifecycle History.

**Producer Consequences.** None.

**Consumer Consequences.** None.

**Publication Consequences.** Not applicable; Lifecycle History is never "published" to `CanonicalState` in the Writer-on-Behalf-Of sense - it is directly appended to by its own owner.

**Mutation and Aliasing Consequences.** `Trade`'s own internal mutability (unlike `LifecycleEvent`) remains confined to `TradeLifecycleEngine`'s own private management; no external consumer holds a reference to a live `Trade` object.

**Compatibility Constraints.** Preserves ADR-003 exactly.

**Failure Consequences.** Not applicable beyond AD-016's own general treatment.

**Determinism Consequences.** None; ratifies already-deterministic behaviour.

**Acceptance Criteria.** `CanonicalState`'s own schema, re-enumerated at any future HEAD, continues to contain no lifecycle-history field.

**Traceability.** FR-011; DEP-023, DEP-025 through DEP-027, DEP-041; CAP-012; AI-004; AI-012; Rule OM-005; ADR-003.

**Scope Boundary.** Does not extend to `Trade`'s own internal mutability.

---

### P3-02-AD-012 - Position Information Flow

**Title.** Position Information Flow Ratification.

**Motivation.** CAP-013 was already COMPLETE; this decision formally ratifies that finding, explicitly independent of CAP-019's own separate classification.

**Decision.** Position information SHALL continue to flow exclusively as: Lifecycle Event/current position -> `PositionEngine` (Computational Authority) -> a Structurally Independent snapshot (already conformant, AD-007) -> `CanonicalState` (Authoritative Owner, via `CanonicalEnforcer`) -> `PnLEngine`/`RiskEngine` (Primary Consumers). Exposure SHALL remain exclusively a derived property of Position, never an independently owned object. This ratification is confirmed independent of CAP-019's own `PositionEngine`-private-state self-consistency finding, per the SDA's own Cycle Detection (SDA Section 16, DEP-030 resolved one-directionally).

**Scientific Justification.** ADR-004 and the Target Information Flow are already fully satisfied; this decision ratifies, without reopening, P2-02A's own certified contract.

**Information-Flow Consequences.** None; ratifies already-conformant behaviour.

**Ownership Consequences.** None; not reopened.

**Producer Consequences.** `PositionEngine` remains bound by AD-007 (already conformant).

**Consumer Consequences.** None.

**Publication Consequences.** None beyond AD-017's own Writer-on-Behalf-Of ratification.

**Mutation and Aliasing Consequences.** None beyond what AD-007 already covers for Position specifically.

**Compatibility Constraints.** Does not reopen P2-02A's own certified ownership, formula, or pre-trade-view contract.

**Failure Consequences.** Governed by AD-016 and CAP-019 (not reopened here).

**Determinism Consequences.** None; ratifies already-deterministic behaviour.

**Acceptance Criteria.** A fresh trace confirms the same topology at any future HEAD.

**Traceability.** FR-012; DEP-011, DEP-016, DEP-020, DEP-025, DEP-028 through DEP-031, DEP-038; CAP-013; ADR-004; Target Information Flow; P2-02A.

**Scope Boundary.** Does not reopen P2-02A; does not reopen CAP-019's own classification.

---

### P3-02-AD-013 - Financial Information Flow

**Title.** Financial Information Flow Ratification.

**Motivation.** CAP-014 was already COMPLETE; this decision formally ratifies that finding.

**Decision.** Financial information SHALL continue to flow exclusively as: Lifecycle Facts + Entry Basis -> `PnLEngine` (Computational Authority) -> `CanonicalState` (Authoritative Owner, via `CanonicalEnforcer`) -> `RiskEngine` (Primary Consumer for Equity/Peak Equity).

**Scientific Justification.** ADR-005/ADR-006 and the Target Information Flow are already fully satisfied; ratifies, without reopening, P2-03's own certified contract.

**Information-Flow Consequences.** None; ratifies already-conformant behaviour.

**Ownership Consequences.** None; not reopened.

**Producer Consequences.** `PnLEngine` remains bound by AD-007; already conformant (every financial value is a scalar, VCF-002).

**Consumer Consequences.** None.

**Publication Consequences.** None beyond AD-017's own ratification.

**Mutation and Aliasing Consequences.** None; every value in this flow is scalar, structurally immune.

**Compatibility Constraints.** Does not reopen P2-03's own certified ownership or formulas.

**Failure Consequences.** Governed by AD-016 and RR-002 (not reopened here).

**Determinism Consequences.** None; ratifies already-deterministic behaviour.

**Acceptance Criteria.** A fresh trace confirms the same topology at any future HEAD.

**Traceability.** FR-014; DEP-012, DEP-017, DEP-020, DEP-021, DEP-026, DEP-028, DEP-033, DEP-034, DEP-039; CAP-014; ADR-005; ADR-006; Target Information Flow; P2-03.

**Scope Boundary.** Does not reopen P2-03.

---

### P3-02-AD-014 - Risk Information Flow

**Title.** Risk Information Flow Ratification, Incorporating the apply_risk Correction.

**Motivation.** CAP-015 was already COMPLETE for flow topology; this decision ratifies that finding and incorporates AD-006's own return-contract correction as the sole change within this flow's own scope.

**Decision.** Risk information SHALL continue to flow exclusively as: Canonical Financial State (Canonical Working State, AD-002) + Position -> `RiskEngine` (Computational Authority) -> `CanonicalState` (Authoritative Owner, via `CanonicalEnforcer`, with `apply_risk`'s own return value corrected per AD-006). No active downstream consumer of Risk Metrics exists among the twenty-four P3-02 Functional Requirements (confirmed absent, SDA Section 12); this Architecture does not introduce one.

**Scientific Justification.** ADR-007 and the Target Information Flow are already fully satisfied for topology; the sole open item (AD-006) is resolved separately and referenced here for completeness.

**Information-Flow Consequences.** Incorporates AD-006's own corrected return-value scoping.

**Ownership Consequences.** None; not reopened.

**Producer Consequences.** `RiskEngine` remains bound by AD-007; already conformant (every value scalar, VCF-002).

**Consumer Consequences.** None currently active.

**Publication Consequences.** `apply_risk`'s own return value corrected per AD-006; its own write behaviour (`update_risk`) unchanged.

**Mutation and Aliasing Consequences.** None beyond AD-006's own already-stated consequences.

**Compatibility Constraints.** Does not reopen P2-04's own certified ownership or formulas.

**Failure Consequences.** Governed by AD-016.

**Determinism Consequences.** None; ratifies already-deterministic behaviour.

**Acceptance Criteria.** A fresh trace confirms the same topology, and `apply_risk`'s own corrected return value, at any future HEAD.

**Traceability.** FR-015; DEP-006, DEP-013, DEP-018, DEP-020, DEP-021, DEP-029, DEP-033, DEP-040; CAP-015; ADR-007; Target Information Flow; P2-04.

**Scope Boundary.** Does not reopen P2-04.

---

### P3-02-AD-015 - Performance Information Flow

**Title.** Performance Information Flow Ratification, Incorporating the Object-Identity Correction.

**Motivation.** CAP-016 (PARTIAL) found the current-state description itself fully accurate, with an out-of-scope, forwarded methodological limitation (TD-004); this decision ratifies the description and incorporates AD-005's own object-identity fix, without touching methodology.

**Decision.** Performance information's own current-state shape (input: `decision`, `pnl`, `regime`, `trade_event`; output: a per-action statistics dictionary keyed by decision, not by completed lifecycle outcome) SHALL remain entirely unchanged in accounting methodology. Within this model's own explicit boundary - object identity, Publication, Canonical Storage, Snapshot stability, Consumer boundaries - `PerformanceEngine`'s own publication SHALL become Structurally Independent per AD-005/AD-009, and `CanonicalState.state["performance_metrics"]` SHALL become Tick-Stable per AD-003, exactly as every other dict-shaped canonical object.

**Scientific Justification.** ADR-008 governs Performance Ownership; TD-004 already, correctly, names the methodological limitation this decision does not resolve; the governing task's own explicit instruction restricts this decision to information-form properties only.

**Information-Flow Consequences.** Incorporates AD-005's own corrected object-identity discipline.

**Ownership Consequences.** None; `PerformanceEngine` remains the exclusive Computational Authority.

**Producer Consequences.** Per AD-005.

**Consumer Consequences.** Per AD-003/AD-005.

**Publication Consequences.** Per AD-005/AD-017.

**Mutation and Aliasing Consequences.** Per AD-005/AD-009.

**Compatibility Constraints.** No accounting formula, key structure, or decision-based accounting basis change; TD-004 untouched.

**Failure Consequences.** Governed by AD-016; `PerformanceEngine.update`'s own `RUNTIME_FAILURE_EVENT` short-circuit (returning `self.stats` unchanged for a rejected transition) is unaffected by this decision, since it is a computational, not object-identity, behaviour.

**Determinism Consequences.** None beyond AD-005's own already-stated consequences.

**Acceptance Criteria.** Per AD-005; additionally, the source lines computing `PerformanceEngine.update`'s own `'pnl'`, `'trades'`, and `'winrate'` accounting formulas remain byte-for-byte unchanged from their own pre-Architecture state (a genuine source-line comparison of the formula statements themselves), while the container object those statements populate becomes Structurally Independent per AD-005.

**Traceability.** FR-016; DEP-014, DEP-019, DEP-035, DEP-050; CAP-016; ADR-008; TD-004; Target Information Flow (Performance row).

**Scope Boundary.** Does not redesign `PerformanceEngine`'s own accounting methodology; does not introduce a new Performance Metric; does not advance TD-004.

---

### P3-02-AD-016 - Failure Information Flow

**Title.** Failure Information Flow Ratification, with Explicit Post-Exception Divergence Disposition.

**Motivation.** CAP-021 was already COMPLETE, including the newly-identified `PositionEngine`-instance (now CAP-019, COMPLETE); this decision formally ratifies both, together, at the information-flow level, and explicitly answers the governing task's own five specific sub-questions.

**Decision.** A Failed Tick (P3-01-AD-004, not reopened) SHALL continue to produce no Tick-Complete result; consequently, no information from a Failed Tick becomes externally observable, regardless of how many `CanonicalEnforcer.apply_*` calls already executed internally before the interrupting exception. Whatever subset of those calls already executed SHALL remain present, internally, in `CanonicalState`'s own held state, valid for the next tick's own processing; AD-001's own copy-on-read semantics apply identically after a Failed Tick as during any normal tick, so a fresh `get()` call after a Failed Tick correctly reflects this already-durable, partial state. A Failed Tick SHALL continue to be classified exactly as P3-01-AD-004 already defines it, introducing no new failure concept. A genuine rejected lifecycle transition (`RUNTIME_FAILURE_EVENT`) SHALL continue to execute all twelve stages, reach Tick Completion, and leave Position/Financial/Performance fields unmutated (P3-01-AD-006, not reopened). Post-Exception Financial/Lifecycle Divergence SHALL remain documented in both of its own currently-identified instances - the original `TradeLifecycleEngine`-versus-`CanonicalState` case (RR-002) and the `PositionEngine`-private-state case (CAP-019) - as explicitly named, non-blocking, unresolved Residual Risks, neither silently presented as resolved. This decision introduces no rollback, reset, recovery, or transaction mechanism for either.

**Scientific Justification.** P3-01-AD-004 already establishes that no rollback mechanism is architecturally required; this decision extends that already-certified reasoning to the information-flow level without reopening it, and explicitly, honestly documents rather than silently resolves the residual conditions, consistent with this governance chain's own established discipline (first applied by the P3-01 Architecture itself to the original Post-Exception Divergence finding).

**Information-Flow Consequences.** Confirms the precise boundary of external observability for a Failed Tick: none, ever, for any Failed Tick, regardless of how much internal progress occurred.

**Ownership Consequences.** None.

**Producer Consequences.** None beyond AD-007's own already-stated consequences, which apply identically whether or not a given tick ultimately fails.

**Consumer Consequences.** No consumer ever observes a Failed Tick's own partial state, externally; internal, next-tick consumption of already-durable partial state is unchanged from before this Architecture.

**Publication Consequences.** None beyond AD-001 through AD-009's own already-stated consequences.

**Mutation and Aliasing Consequences.** None new; AD-001's own copy semantics apply uniformly, including immediately after a Failed Tick.

**Compatibility Constraints.** Does not alter any already-certified P2-02A/P2-03/P2-04 non-mutation contract; does not reopen P3-01-AD-004 or P3-01-AD-006.

**Failure Consequences.** This decision is, in its entirety, a Failure Consequence definition, restating and extending P3-01-AD-004's own reasoning to the information-flow level.

**Determinism Consequences.** A retry following a Failed Tick remains explicitly not guaranteed deterministic relative to an uninterrupted run, per P3-01's own already-stated qualification (Architecture Section 19, not reopened, not extended by this decision).

**Acceptance Criteria.** No field of any Failed Tick is ever observable in any Tick-Complete result; a fresh `get()` call immediately following a Failed Tick returns a value consistent with whatever `apply_*` calls actually completed before the exception.

**Traceability.** FR-018; DEP-024, DEP-032, DEP-046; CAP-021; CAP-019; P3-01-AD-004; P3-01-AD-006; ADR-011; RR-002; Post-Exception Financial/Lifecycle Divergence.

**Scope Boundary.** Does not design a Persistence, Recovery, rollback, reset, or transaction mechanism.

---

### P3-02-AD-017 - HOLD and No-Execution Information Flow

**Title.** HOLD and No-Execution Information Flow Ratification.

**Motivation.** CAP-022 was already COMPLETE; this decision formally ratifies that finding and confirms the new Tick-Complete Snapshot Stability guarantee applies identically to a HOLD tick.

**Decision.** A `HOLD` or no-execution tick SHALL continue to execute all twelve ADR-010 stages, in the same order as any other tick, with every downstream stage producing a well-defined, numerically-unchanged result for a no-event input. Tick Completion SHALL remain reachable, and SHALL be reached, without any Execution Event having occurred. The Tick-Complete Snapshot Model's own stability guarantee (AD-003) SHALL apply identically to a HOLD tick's own returned result as to any other tick's; no special-casing is introduced.

**Scientific Justification.** ADR-010 names no conditional or skippable stage; a `HOLD` decision is itself a valid Execution Decision, not the absence of one; already fully established by P3-01-AD-005, not reopened.

**Information-Flow Consequences.** None new beyond confirming AD-003's own universal applicability.

**Ownership Consequences.** None.

**Producer Consequences.** None beyond AD-007's own already-stated consequences, unconditional on tick outcome.

**Consumer Consequences.** None.

**Publication Consequences.** None.

**Mutation and Aliasing Consequences.** None new.

**Compatibility Constraints.** Preserves every already-certified `None`-input guard in `PnLEngine`, `PerformanceEngine`, and `PositionEngine` exactly.

**Failure Consequences.** Not applicable; `HOLD` is not a failure condition.

**Determinism Consequences.** Confirms HOLD's own deterministic, guard-based handling remains compatible with the full Tick-Complete Snapshot Stability guarantee.

**Acceptance Criteria.** A scripted HOLD-only tick sequence produces a complete, well-formed, Tick-Stable result at every tick, with every financial and risk key numerically unchanged from the prior tick.

**Traceability.** FR-019; DEP-027, DEP-031, DEP-034, DEP-047; CAP-022; P3-01-AD-005; Tick Completion Contract.

**Scope Boundary.** Does not reopen P3-01-AD-005; does not evaluate `StrategySelector`'s own cooldown/weighting logic.

---

### P3-02-AD-018 - Direct CanonicalState Writes

**Title.** Direct CanonicalState Write-Path Exclusivity Ratification.

**Motivation.** CAP-009 was already COMPLETE; this decision formally ratifies that finding as a standing constraint.

**Decision.** Exactly one direct `CanonicalState.update_*` call site outside `CanonicalEnforcer` SHALL remain permitted: Runtime Tick's own explicitly Matrix-named `RunLoop`-direct exception (`update_tick`, `loop.py:42`). Every other `CanonicalState.state` mutation SHALL occur exclusively through a named `CanonicalEnforcer.apply_*` method. No new direct write exception is introduced or permitted by this Architecture.

**Scientific Justification.** Rule OM-003 and P3-01-AD-002 already establish this exclusivity; this decision ratifies it as a P3-02-scoped, information-flow-level standing constraint, not merely an inherited fact.

**Information-Flow Consequences.** None; ratifies already-conformant behaviour.

**Ownership Consequences.** None.

**Producer Consequences.** None.

**Consumer Consequences.** None.

**Publication Consequences.** Directly establishes the Writer-on-Behalf-Of Model (Section 17), which AD-006 further refines for `apply_risk` specifically.

**Mutation and Aliasing Consequences.** None new.

**Compatibility Constraints.** Preserves P3-01-AD-002 exactly.

**Failure Consequences.** Not applicable.

**Determinism Consequences.** None; ratifies already-deterministic behaviour.

**Acceptance Criteria.** A scoped repository-wide search at any future HEAD continues to find exactly one call site per `CanonicalState.update_*` method, located exactly as this decision specifies.

**Traceability.** FR-006; DEP-015 through DEP-019, DEP-043; CAP-009; Rule OM-003; P3-01-AI-009; P3-01-AD-002.

**Scope Boundary.** Does not introduce a new exception; scoped to `run_engine/`, not the untracked review/backup directories outside the active runtime.

---

### P3-02-AD-019 - Alternative Information Paths

**Title.** Alternative Information Path Exclusivity Ratification.

**Motivation.** CAP-023 was already COMPLETE; this decision formally ratifies that finding, including the two newly-identified dormant files.

**Decision.** Exactly one active information-flow path SHALL exist: `run_engine/main.py` invoking `RunLoop.step()`. `run_engine/core/decision.py`, `run_engine/runtime/`, `run_engine/execution/` (top-level), `run_engine/feedback/`, `run_engine/logging/`, `run_engine/core/position_sizing.py`, and `run_engine/core/state_modulation.py` SHALL remain classified as confirmed-inactive, reserved for Phase 6 Repository Consolidation's own future retain/integrate/archive/remove decision, not decided here. No alternative active path may bypass this Architecture's own Canonical Read Model, Producer Isolation Model, or Writer-on-Behalf-Of Model.

**Scientific Justification.** AI-013 (Architectural Minimality) already requires every competing implementation to eventually receive an explicit classification; this decision defers that classification, consistent with P3-01-AD-009's own already-established treatment, while formally including the two dormant files this unit's own FRA newly identified.

**Information-Flow Consequences.** None; ratifies already-conformant behaviour and extends the already-established dormant-file documentation obligation.

**Ownership Consequences.** None.

**Producer Consequences.** None.

**Consumer Consequences.** None.

**Publication Consequences.** None.

**Mutation and Aliasing Consequences.** None.

**Compatibility Constraints.** None beyond P3-01-AD-009's own already-established treatment.

**Failure Consequences.** Not applicable.

**Determinism Consequences.** Confirms the sequence-uniqueness constituent of determinism (AD-003) is not threatened by any dormant path.

**Acceptance Criteria.** A repository-wide import search from `run_engine/main.py` and `run_engine/core/loop.py` continues to reach exactly the same active-collaborator set, with no import edge into any confirmed-inactive component, at any future HEAD.

**Traceability.** FR-020; DEP-048; CAP-023; P3-01-AD-009; AI-013; Phase 6; Documentation Gap DG-001.

**Scope Boundary.** Does not classify or dispose of any dormant file; that remains Phase 6 Repository Consolidation's own scope.

---

### P3-02-AD-020 - Cross-Unit Boundary Ratification

**Title.** Cross-Unit Boundary Ratification.

**Motivation.** The FRA's own Section 8, the SDA's own Cross-Unit Dependencies (Section 15), and the CGA's own Cross-Unit Capability Assessment (Section 17) jointly established six items outside this unit's own resolution scope. This decision formally ratifies that boundary as binding for this Architecture and any future Specification derived from it.

**Decision.** P3-01's own twelve-stage execution ordering, Tick-Complete Publication semantics, and Failed-Tick semantics SHALL remain entirely unchanged; no decision in this document reopens P3-01-AD-001 through AD-010. TD-004 (Lifecycle-based Performance Evaluation) and `PerformanceEngine`'s own broader accounting methodology SHALL remain P3-03's own resolution scope; AD-005/AD-015 address only object-identity discipline, never methodology, and this Architecture does not advance TD-004's own resolution. TD-007 (RunLoop Lifecycle Control Surface) SHALL remain a future Runtime Control Unit's own scope, explicitly distinguished from this Architecture's own Information Lifetime Model (Section 12) and Failure Information Flow Model (Section 24). Post-Exception Financial/Lifecycle Divergence (RR-002) SHALL remain a documented, non-blocking Residual Risk, exactly as the P3-01 Final Certification classified it. The `PositionEngine` Partial-Mutation Residual Risk (formerly FG-005) SHALL remain classified a Residual Risk (CAP-019), per the CGA's own explicit, precedent-grounded reclassification; this Architecture does not upgrade it to a Functional Gap and does not introduce a rollback, reset, or transaction mechanism for it. No Persistence, Recovery, or Schema Evolution architecture is introduced by any decision in this document (ADR-012, Deferred Scope, not reopened).

**Scientific Justification.** The Implementation Baseline's own P3-01 ("Implement ADR-010 execution sequence..."), P3-02 ("Remove hidden coupling..."), and P3-03 ("Verify PerformanceEngine inputs...") objective texts each remain, in substance, closer to their own respective forwarded item than to this unit's own scope; this decision ratifies, rather than re-derives, that already-established boundary.

**Information-Flow Consequences.** None beyond what AD-001 through AD-019 already establish.

**Ownership Consequences.** None.

**Producer Consequences.** None.

**Consumer Consequences.** None.

**Publication Consequences.** None.

**Mutation and Aliasing Consequences.** None.

**Compatibility Constraints.** None beyond AD-001 through AD-019's own already-established constraints.

**Failure Consequences.** Not applicable beyond AD-016's own already-stated treatment.

**Determinism Consequences.** Not applicable.

**Acceptance Criteria.** No future P3-02 Specification or Implementation document reopens P3-01-AD-001 through AD-010, advances TD-004's own resolution, designs a TD-007-adjacent control surface, silently resolves RR-002 or the `PositionEngine` Residual Risk, or introduces a Persistence/Recovery/Schema Evolution mechanism.

**Traceability.** FR-023, FR-024; DEP-045 through DEP-052; CAP-016, CAP-019, CAP-026, CAP-027; TD-004; TD-007; RR-002; ADR-012; Implementation Baseline (P3-01/P3-02/P3-03 unit definitions).

**Scope Boundary.** Proposes no P3-01, P3-03, or future-Runtime-Control-Unit solution, mechanism, or preference for any of the forwarded items.

## 29. Architecture Invariants

**P3-02-AI-001 - Stable Tick-Complete Snapshot.** A Tick-Complete result, once returned, shall remain unchanged in every field for as long as it is retained, regardless of subsequently-executed ticks. Established by AD-003.

**P3-02-AI-002 - No Cross-Tick Snapshot Mutation.** No subsequently-executed tick shall cause any field of a previously-returned Tick-Complete result to change value. Established by AD-001, AD-004, AD-005.

**P3-02-AI-003 - No External Canonical-State Mutation.** No component external to `CanonicalEnforcer`, other than Runtime Tick's own explicitly Matrix-named exception, shall mutate `CanonicalState`'s own held state directly. Established by AD-018.

**P3-02-AI-004 - No Consumer Input Mutation.** No Primary Consumer shall mutate the runtime object it consumes. Established by AD-008.

**P3-02-AI-005 - No Producer Mutation of Published Snapshot.** No Producer shall mutate a value after handing it to `CanonicalEnforcer` for publication. Established by AD-007.

**P3-02-AI-006 - No Unauthorized Shared Mutable Reference.** No two distinct canonical publications, and no canonical publication and any component's own private working state, shall share object identity for any mutable value. Established by AD-001, AD-005, AD-007, AD-009.

**P3-02-AI-007 - Canonical Writer Discipline.** Every `CanonicalState.state` mutation shall occur exclusively through a named `CanonicalEnforcer.apply_*` method, except Runtime Tick's own explicit exception, and every `apply_*` method shall follow one uniform return-value contract. Established by AD-006, AD-018.

**P3-02-AI-008 - One Semantic Source per Runtime Object.** Every runtime information object named in the Runtime Ownership Matrix shall possess exactly one Computational Authority and exactly one Authoritative Owner, unchanged from the Baseline. Established by AD-012 through AD-015, jointly, not independently re-derived.

**P3-02-AI-009 - Runtime Event Semantic Stability.** Every explicit Runtime Event shall represent exactly one semantic transition, originate from exactly one call site, and remain immutable after construction. Established by AD-010.

**P3-02-AI-010 - Lifecycle History Immutability.** Completed Lifecycle History records shall remain immutable and shall never be duplicated into `CanonicalState`. Established by AD-011.

**P3-02-AI-011 - Operational and Historical Separation.** `CanonicalState` shall remain the exclusive Authoritative Owner of operational truth; `TradeLifecycleEngine` shall remain the exclusive Authoritative Owner of historical truth; neither model replaces the other. Established by AD-011, ratifying AI-012 (Baseline).

**P3-02-AI-012 - Deterministic Information Flow.** Given identical tick inputs and an identical initial `CanonicalState`, the active information flow shall produce functionally identical intermediate and final results across independent runtime instances; no aliasing shall introduce cross-instance nondeterminism, and the single-instance retained-reference risk RR-001 shall remain fully closed for every field AD-001, AD-005, and AD-007 cover. Established by AD-001 through AD-009, jointly.

**P3-02-AI-013 - No Downstream Reconstruction.** No downstream runtime component shall reconstruct information already produced by an upstream component. Established by AD-011 through AD-015, jointly, ratifying, not independently re-deriving.

**P3-02-AI-014 - No Alternative Active Information Path.** Exactly one active information-flow path shall exist at any point in this unit's own scope. Established by AD-019.

**P3-02-AI-015 - Certified Ownership Compatibility.** No decision in this document, and no future implementation of it, may alter any P2-02A-certified, P2-03-certified, P2-04-certified, or P3-01-certified ownership, formula, ordering, or non-mutation contract. Established by AD-012 through AD-014, AD-016, AD-017, AD-020, jointly.

Every Architecture Invariant above is directly traceable to one or more Architecture Decisions in Section 28; none is asserted without a corresponding decision establishing it. None of the fifteen invariants above contradicts or redefines any Architecture Baseline-level Invariant (AI-001 through AI-015); each is a P3-02-specific specialization of the general principle the corresponding Baseline Invariant already establishes, and none duplicates any P3-01-specific invariant (P3-01-AI-001 through AI-012) already established by the certified P3-01 Architecture.

## 30. Architecture Constraints

**Constraint C-001.** P3-01's own twelve-stage execution ordering (ADR-010, P3-01-AD-001) remains entirely unchanged; no future P3-02 Specification or Implementation may reorder, skip, or duplicate any stage.

**Constraint C-002.** Tick execution remains synchronous and single-threaded; no future P3-02 Specification or Implementation may introduce concurrent or asynchronous stage execution.

**Constraint C-003.** No Persistence mechanism (ADR-012, Deferred Scope) shall be introduced by any future P3-02 Specification or Implementation.

**Constraint C-004.** No Recovery mechanism shall be introduced, including as a resolution to RR-002 or the `PositionEngine` Residual Risk (CAP-019).

**Constraint C-005.** No Schema Evolution mechanism shall be introduced.

**Constraint C-006.** No Operator Lifecycle Control mechanism (TD-007) shall be introduced or conflated with this Architecture's own Failure Information Flow Model.

**Constraint C-007.** No `PerformanceEngine` accounting-methodology redefinition (Gap 4/TD-004) shall be introduced; this remains P3-03's own scope per AD-020.

**Constraint C-008.** No Position, PnL, or Risk formula change shall be introduced; P2-02A, P2-03, P2-04 remain unreopened per AD-012 through AD-014.

**Constraint C-009.** No new Authoritative Owner or Computational Authority shall be introduced for any runtime information object.

**Constraint C-010.** No Lifecycle-semantics change (Scale-In/Partial Close/Full Close, ADR-009) shall be introduced.

**Constraint C-011.** No rollback, reset, or transaction mechanism shall be introduced for `CanonicalState`, `PositionEngine`'s own private state, or any other component's own cross-tick state, including as a resolution to any Residual Risk this document names.

**Constraint C-012.** A Residual Risk shall not, by its own existence alone, be reclassified a Functional Gap; its own actual, independently-assessed impact governs its classification, per the CGA's own already-established rule, not reopened by this Architecture.

**Constraint C-013.** No concrete Python signature, method body, complete file diff, or Implementation Unit shall be specified anywhere in this document.

## 31. Technical-Debt and Residual-Risk Disposition

**TD-004** (Lifecycle-based Performance Evaluation) remains explicitly out of this unit's own scope, ratified as P3-03's territory by AD-020; this document does not close it, does not partially close it, and does not alter its Register status. AD-005/AD-015's own object-identity corrections are explicitly, textually distinguished from TD-004's own methodological concern throughout Section 28.

**TD-007** (RunLoop Lifecycle Control Surface) remains explicitly out of this unit's own scope, ratified as a future Runtime Control Unit's territory by AD-020; this document does not conflate it with AD-016's own Failure Information Flow decisions.

**RR-001** (single-instance retained-reference risk) is fully closed, as far as this unit's own scope permits, by AD-001, AD-005, and AD-007, jointly: every field of a Tick-Complete result becomes Tick-Stable (Section 12), removing the specific mechanism that gave rise to RR-001. No residual instance of RR-001 remains open after this Architecture's own decisions are implemented, since RR-001's own entire substance was the top-level container's and Performance Metrics' own lack of isolation, both now structurally resolved.

**RR-002** (Post-Exception Financial/Lifecycle Divergence, the original `TradeLifecycleEngine`-versus-`CanonicalState` instance) remains an open, non-blocking, documented Residual Risk, exactly as the P3-01 Final Certification classified it. This Architecture does not resolve it, does not silently present it as resolved, and does not design a Recovery mechanism for it (Constraint C-004).

**`PositionEngine` Partial-Mutation Residual Risk** (formerly FG-005) remains classified a Residual Risk, per the CGA's own explicit, precedent-grounded reclassification (CAP-019, COMPLETE, Residual-Risk Capability). This Architecture ratifies that classification (AD-020) without reopening it, and does not introduce a rollback, reset, or transaction mechanism (Constraint C-011).

**No new Technical Debt candidate is identified as scientifically required by this document.** Unlike the P3-01 Architecture, which recommended (without registering) a new Technical Debt candidate for Post-Exception Financial/Lifecycle Divergence, this document's own analysis finds every open item within this unit's own scope (CAP-001, CAP-004, CAP-006, CAP-010, and the general PARTIAL findings) fully and directly resolved by the Architecture Decisions in Section 28, requiring no further, separately-tracked recommendation.

## 32. FRA Traceability

| Requirement | Governing Architecture Decision(s) |
|---|---|
| FR-001 | AD-001 |
| FR-002 | AD-002 |
| FR-003 | AD-003, AD-004 |
| FR-004 | AD-005, AD-007, AD-009 |
| FR-005 | AD-007, AD-008 |
| FR-006 | AD-018 |
| FR-007 | AD-006 |
| FR-008 | AD-012, AD-013, AD-014 (jointly, not independently re-derived) |
| FR-009 | AD-011, AD-013, AD-014 (jointly) |
| FR-010 | AD-010 |
| FR-011 | AD-011 |
| FR-012 | AD-012 |
| FR-013 | AD-020 (ratifies CAP-019, not reopened) |
| FR-014 | AD-013 |
| FR-015 | AD-014 |
| FR-016 | AD-015 |
| FR-017 | AD-008 |
| FR-018 | AD-016 |
| FR-019 | AD-017 |
| FR-020 | AD-019 |
| FR-021 | AD-001 through AD-020, jointly (traceability itself, not independently decided) |
| FR-022 | AD-001, AD-003, AD-005, AD-007 (jointly) |
| FR-023 | AD-020 |
| FR-024 | AD-020 |

All twenty-four Functional Requirements are governed by at least one Architecture Decision.

## 33. SDA Dependency Traceability

Every one of the fifty-two Dependency records is individually resolved by the Architecture Decision(s) governing its own source Functional Requirement (Section 32); no dependency remains without an explicit Architecture-stage disposition.

| Dependency | Disposition |
|---|---|
| DEP-001 | Closed - AD-001 (read-contract resolved). |
| DEP-002 | Ratified - AD-002 (unaffected by AD-001's own resolution direction). |
| DEP-003 | Closed - AD-001, AD-007, AD-008 (jointly resolve the verifiability question). |
| DEP-004 | Closed - AD-001, AD-008. |
| DEP-005 | Closed - AD-001, AD-003 (RR-001 fully addressed). |
| DEP-006 | Ratified - AD-002, AD-014. |
| DEP-007 | Closed - AD-003, AD-004. |
| DEP-008 | Closed - AD-005. |
| DEP-009 | Closed - AD-003, AD-005, AD-009 (unified under one OQ-007 resolution). |
| DEP-010 | Closed - AD-007, AD-008. |
| DEP-011 | Ratified - AD-007 applied to AD-012. |
| DEP-012 | Ratified - AD-007 applied to AD-013. |
| DEP-013 | Ratified - AD-007 applied to AD-014. |
| DEP-014 | Ratified - AD-007 applied to AD-015. |
| DEP-015 | Closed - AD-006, AD-018. |
| DEP-016 | Ratified - AD-012, AD-018. |
| DEP-017 | Ratified - AD-013, AD-018. |
| DEP-018 | Ratified - AD-014, AD-018. |
| DEP-019 | Ratified - AD-015, AD-018. |
| DEP-020 | Ratified - AD-012 through AD-014 (evidentiary basis for AD-011-through-015-jointly's own semantic-continuity ratification). |
| DEP-021 | Ratified - AD-011, AD-013, AD-014. |
| DEP-022 | Ratified - joint semantic-continuity/reconstruction ratification. |
| DEP-023 | Ratified - AD-010, AD-011. |
| DEP-024 | Ratified - AD-010, AD-016. |
| DEP-025 | Ratified - AD-011, AD-012. |
| DEP-026 | Ratified - AD-011, AD-013. |
| DEP-027 | Ratified - AD-011, AD-017. |
| DEP-028 | Ratified - AD-012, AD-013. |
| DEP-029 | Ratified - AD-012, AD-014. |
| DEP-030 | Ratified - AD-012, AD-020 (confirmed non-blocking, SDA's own Cycle Detection). |
| DEP-031 | Ratified - AD-012, AD-017. |
| DEP-032 | Ratified - AD-016, AD-020. |
| DEP-033 | Ratified - AD-013, AD-014. |
| DEP-034 | Ratified - AD-013, AD-017. |
| DEP-035 | Closed - AD-005, AD-015 (shared-object, both resolved jointly). |
| DEP-036 | Ratified - AD-001 through AD-020 (aggregate, FR-021's own traceability). |
| DEP-037 | Ratified - AD-003, AD-020 (CAP-019/CAP-020 both COMPLETE, qualification resolved). |
| DEP-038 | Ratified - AD-012 (P2-02A not reopened). |
| DEP-039 | Ratified - AD-013 (P2-03 not reopened). |
| DEP-040 | Ratified - AD-014 (P2-04 not reopened). |
| DEP-041 | Ratified - AD-011 (ADR-003 not reopened). |
| DEP-042 | Ratified - AD-002 (P3-01-AI-003/AI-004 not reopened). |
| DEP-043 | Ratified - AD-018 (P3-01-AI-009/AD-002 not reopened). |
| DEP-044 | Ratified - AD-010 (Baseline AI-008/ADR-002 not reopened). |
| DEP-045 | Ratified - AD-020 (P3-01-AD-004 not reopened; extended, not resolved). |
| DEP-046 | Ratified - AD-016 (P3-01-AD-004/AD-006 not reopened). |
| DEP-047 | Ratified - AD-017 (P3-01-AD-005 not reopened). |
| DEP-048 | Ratified - AD-019 (P3-01-AD-009 not reopened; Phase 6 forwarded). |
| DEP-049 | Ratified - AD-003 (P3-01-AD-007/EO-013 not reopened). |
| DEP-050 | Ratified - AD-005, AD-015, AD-020 (TD-004/P3-03 not reopened). |
| DEP-051 | Ratified - AD-020 (blanket P3-01 constraint, Constraint C-001 through C-002). |
| DEP-052 | Ratified - AD-020 (blanket P3-03 constraint, Constraint C-007). |

## 34. CGA Capability Traceability

| Capability | Prior Status | Disposition |
|---|---|---|
| CAP-001 | MISSING | Closed - AD-001. |
| CAP-002 | COMPLETE | Ratified unchanged - AD-002. |
| CAP-003 | PARTIAL | Closed - AD-003 (composite resolution of AD-001, AD-005, AD-007, AD-009). |
| CAP-004 | MISSING | Closed - AD-004 (direct structural consequence of AD-001). |
| CAP-005 | PARTIAL | Closed - AD-007, AD-009 (convention elevated to binding contract). |
| CAP-006 | MISSING | Closed - AD-005, AD-009. |
| CAP-007 | PARTIAL | Closed - AD-007, AD-008 (verifiability obligation established). |
| CAP-008 | PARTIAL | Closed - AD-008. |
| CAP-009 | COMPLETE | Ratified unchanged - AD-018. |
| CAP-010 | PARTIAL | Closed - AD-006. |
| CAP-011 | COMPLETE | Ratified unchanged - AD-010. |
| CAP-012 | COMPLETE | Ratified unchanged - AD-011. |
| CAP-013 | COMPLETE | Ratified unchanged - AD-012. |
| CAP-014 | COMPLETE | Ratified unchanged - AD-013. |
| CAP-015 | COMPLETE | Ratified unchanged, `apply_risk` correction incorporated - AD-014, AD-006. |
| CAP-016 | PARTIAL | Object-identity dimension closed - AD-005, AD-015; methodological dimension remains explicitly P3-03's, ratified forwarded - AD-020. |
| CAP-017 | COMPLETE | Ratified unchanged - AD-011, AD-013, AD-014. |
| CAP-018 | MISSING (aggregate synthesis) | Closed - resolved as a direct consequence of CAP-001, CAP-004, CAP-006, CAP-007, CAP-008 each individually closing (AD-001, AD-004, AD-005, AD-007, AD-008, AD-009); no independent decision required for the synthesis itself. |
| CAP-019 | COMPLETE (Residual-Risk Capability) | Ratified unchanged, not reopened - AD-020. |
| CAP-020 | COMPLETE | Ratified unchanged, RR-001 fully closed - AD-001, AD-003, AD-005, AD-007. |
| CAP-021 | COMPLETE | Ratified unchanged - AD-016. |
| CAP-022 | COMPLETE | Ratified unchanged - AD-017. |
| CAP-023 | COMPLETE | Ratified unchanged - AD-019. |
| CAP-024 | COMPLETE | Ratified unchanged - AD-001 through AD-020, jointly (traceability). |
| CAP-025 | COMPLETE | Ratified unchanged - AD-012, AD-013, AD-014. |
| CAP-026 | COMPLETE | Ratified unchanged - AD-020. |
| CAP-027 | COMPLETE | Ratified unchanged - AD-020. |

Twenty-three of twenty-seven capabilities are ratified unchanged; four (CAP-001, CAP-004, CAP-006, CAP-010) are closed by this Architecture, and CAP-018's own aggregate MISSING status is resolved as a direct, automatic consequence of its own five constituent capabilities each closing - no capability in this document remains open after Section 28's own twenty decisions.

## 35. Acceptance Criteria

**P3-02-AC-001.** `CanonicalState.get()` returns a freshly-constructed shallow copy on every call, for every caller, at any future HEAD.
**P3-02-AC-002.** A Tick-Complete result, once returned, remains functionally identical at every field regardless of how many further ticks execute afterward.
**P3-02-AC-003.** `RunLoop.step()`'s own `"state"` field is never object-identical with `CanonicalState`'s own internally-held dictionary.
**P3-02-AC-004.** `PerformanceEngine`'s own published value is, at every nesting level, a distinct object from its own accumulator on every call.
**P3-02-AC-005.** Every `CanonicalEnforcer.apply_*` method, including `apply_risk`, returns only the specific canonical value(s) it itself publishes.
**P3-02-AC-006.** Every canonical Producer supplies a Structurally Independent value at its own publication boundary, at any future HEAD.
**P3-02-AC-007.** A repeatable, independent procedure exists confirming no Primary Consumer mutates the object it consumes.
**P3-02-AC-008.** Exactly one direct `CanonicalState.update_*` call site remains outside `CanonicalEnforcer` (Runtime Tick's own exception); every other write occurs through a named `apply_*` method.
**P3-02-AC-009.** Every already-certified P2-02A, P2-03, P2-04, and P3-01 contract remains unaltered by any decision in this document.
**P3-02-AC-010.** No new Functional Requirement, Dependency, Capability classification, Persistence, Recovery, or rollback/reset/transaction mechanism is introduced by any decision in this document.

## 36. Implementation Impact Inventory

At the level of runtime-component impact only, no concrete Python signature, file plan, or Implementation Unit is defined here; that is the Specification stage's own scope.

**Components requiring a functional runtime change:** `run_engine/core/performance.py` (`PerformanceEngine.update` must supply a Structurally Independent value at every nesting level, AD-005, AD-009); `run_engine/core/canonical_state.py` (`CanonicalState.get()` must return a shallow copy rather than a direct reference, AD-001); `run_engine/core/canonical_enforcer.py` (`apply_risk`'s own return value must be corrected to the uniform single-value contract, AD-006).

**Components requiring verification only, no functional change:** `run_engine/core/loop.py` (AD-002, AD-004, AD-017, AD-018 - the `"state"` field's own isolation becomes a structural consequence of the `CanonicalState.get()` change, requiring no edit to `loop.py` itself; stage ordering, HOLD handling, and direct-write exclusivity are re-verified, not modified); `run_engine/core/position.py` (AD-007, AD-012 - already conformant, VCF-001, requires only re-verification); `run_engine/core/strategy.py`, `run_engine/core/execution/executor.py` (AD-007 - already conformant, VCF-001); `run_engine/core/trade_lifecycle.py` (AD-010, AD-011 - already conformant); `run_engine/core/pnl.py` (AD-013 - already conformant, scalar-only); `run_engine/core/risk.py` (AD-014 - `RiskEngine.check()`'s own computation is unaffected; only `CanonicalEnforcer`'s own consumption of its output changes, per AD-006); `run_engine/core/regime.py`, `run_engine/core/state.py` (unaffected by any decision in this document); `run_engine/main.py` (AD-016 - re-verified, unaffected).

**Components explicitly not to be changed:** `run_engine/core/decision.py`, `run_engine/runtime/*`, `run_engine/execution/adapter.py`, `run_engine/execution/safety.py`, `run_engine/feedback/tracker.py`, `run_engine/logging/logger.py`, `run_engine/core/position_sizing.py`, `run_engine/core/state_modulation.py` (AD-019 - all remain confirmed-inactive, not reclassified or touched by this Architecture).

**Decisions requiring a functional runtime change:** AD-001 (Canonical Read Model), AD-005 (Performance-Metrics Object Identity), AD-006 (apply_risk Return-Contract). Every other decision (AD-002 through AD-004, AD-007 through AD-020) ratifies already-conformant behaviour, establishes a Verification-Only obligation (AD-008), or is a documentation-only Cross-Unit ratification (AD-016, AD-019, AD-020), requiring no runtime code change on its own.

## 37. Non-Goals

Consistent with Section 3 and the governing task's own "Wichtige Grenzen": no Python signature, method body, or file diff is specified anywhere in this document; no Implementation Unit is defined; no test is designed as a fixed command; no P3-03 methodology decision is made or anticipated beyond AD-020's own explicit boundary-setting; no Persistence, Recovery, or Schema Evolution mechanism is designed (Constraint C-003 through C-005); no Operator Lifecycle Control mechanism is designed (Constraint C-006); no `PerformanceEngine` accounting redesign is performed (Constraint C-007); no Position, PnL, or Risk formula or ownership decision is reopened (Constraint C-008, C-009); no rollback, reset, or transaction mechanism is designed (Constraint C-011); no already-certified P2-02A, P2-03, P2-04, or P3-01 decision is reopened.

## 38. Internal Consistency Review

**Terminology consistency.** "Computational Authority," "Authoritative Owner," "Writer-on-Behalf-Of," "Publication," "Storage," and "Consumption" are used exactly as defined in the Architecture Baseline throughout this document and are kept strictly separate in every Architecture Decision's own "Ownership Consequences," "Producer Consequences," "Consumer Consequences," and "Publication Consequences" fields; no decision conflates any two. "Structural Independence" and "Composite Isolation" are used exactly as defined in Section 6 throughout. "Functionally identical" is used exclusively for runtime-object, dictionary, and result comparisons (Sections 11, 28 AD-003/AD-005 Acceptance Criteria). "Byte-identical"/"byte-for-byte" is used exactly once in this document (AD-015's own Acceptance Criteria field, describing a genuine single-source-line-level comparison of accounting formula statements, not an object-identity or runtime-result comparison), consistent with the project's own strict reservation of that term for file-, git-blob-, or byte-sequence-level comparisons; every other occurrence of "byte-identical" or "byte-for-byte" anywhere in this document, including this sentence's own meta-discussion, is citation or definitional restatement, not an additional comparison claim.

**Ownership consistency.** No Architecture Decision in Section 28 introduces a new Authoritative Owner or Computational Authority anywhere in this document; every decision touching an existing object explicitly states so in its own "Ownership Consequences" field, satisfying Rule OM-009 (no new Authoritative Owner without an Architecture Evolution Review - none is proposed).

**Scope consistency.** No decision in Section 28 specifies a Python signature, a file diff, an Implementation Unit, or a test. Section 3 confirms P3-01 ordering, P2-02A/P2-03/P2-04 formulas and ownership, TD-004/TD-007, Persistence/Recovery/Schema Evolution, and Operator Control all remain untouched by any decision in this document.

**Ordering consistency.** AD-018's own ratification of Writer-on-Behalf-Of exclusivity and every Model section's own reference to the twelve-stage sequence are applied identically throughout; no section describes a different or competing ordering, and P3-01-AD-001 is never reopened.

**Mutation and aliasing consistency.** The three-tier resolution (AD-001 top-level; AD-005/AD-009 nested; AD-007 general Producer contract) is applied identically wherever aliasing is discussed (Sections 9, 11, 13, 15, and every relevant AD's own "Mutation and Aliasing Consequences" field); no section proposes a competing or inconsistent isolation mechanism.

**Failure-semantics consistency.** AD-016 (Failure Information Flow) and AD-020 (Cross-Unit Boundary) are kept explicitly, consistently distinct from CAP-019's own already-resolved classification throughout; no section conflates a Failed Tick with a rejected lifecycle transition, and no section proposes a rollback/reset/transaction mechanism anywhere (Constraint C-011, verified by direct text search during drafting: no such term appears as a positive design proposal anywhere in Section 28).

**Determinism consistency.** RR-001's own full closure (Section 31) is stated once, precisely, in AD-003's own "Determinism Consequences" field and Section 31, and referenced rather than restated with different wording elsewhere (Sections 20, 22 of the CGA's own prior text are not contradicted).

**Traceability completeness.** Section 32 confirms all twenty-four FRA requirements; Section 33 confirms all fifty-two SDA dependencies; Section 34 confirms all twenty-seven CGA capabilities; cross-checked against Section 28's own twenty Architecture Decisions during drafting.

**No fabricated decision.** Every decision in Section 28 traces to a specific FRA requirement, SDA dependency, CGA capability, or Baseline ADR/AI/Rule text; no decision in this document addresses a concern absent from the governing baseline or the P3-02 governance chain's own prior documents.

Status: Internal Consistency Review PASS.

## 39. Architecture Readiness Decision

Every capability the CGA left open (CAP-001, CAP-004, CAP-006, CAP-010, CAP-018, and the general-convention dimension of CAP-003, CAP-005, CAP-007, CAP-008) has been explicitly decided (Section 34). Every Functional Gap the FRA and CGA jointly tracked (FG-001 through FG-004) is closed; the former FG-005 remains, as directed, a ratified Residual Risk (CAP-019), not reopened or upgraded. All twenty-four FRA requirements, all fifty-two SDA dependencies, and all twenty-seven CGA capabilities are traced to at least one Architecture Decision or explicitly confirmed as ratified. Both Post-Exception Divergence instances (RR-002, and the `PositionEngine`-specific instance) remain explicitly, honestly documented as open, non-blocking Residual Risks, never silently presented as resolved. No already-certified P2-02A, P2-03, P2-04, or P3-01 contract is reopened.

**Architecture Readiness: READY.** This document is sufficient to proceed to the P3-02 Specification. No further architectural investigation is required before that step.
