Document Class:
Specification

Document ID:
P3-02-SPEC

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
docs/architecture/P3_02_INFORMATION_FLOW_VALIDATION_SPECIFICATION_V1_2026-07-13.md

Depends On:
- docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md
- docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md
- docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md
- docs/architecture/analysis/P3_02_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-13.md
- docs/architecture/analysis/P3_02_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-13.md
- docs/architecture/analysis/P3_02_CAPABILITY_GAP_ANALYSIS_V1_2026-07-13.md
- docs/architecture/P3_02_INFORMATION_FLOW_VALIDATION_ARCHITECTURE_V1_2026-07-13.md
- docs/architecture/P3_01_DETERMINISTIC_EXECUTION_ORDERING_SPECIFICATION_V1_2026-07-13.md
- docs/architecture/certification/P3_01_FINAL_CERTIFICATION_V1_2026-07-13.md
- docs/architecture/P2_02A_POSITION_OWNERSHIP_SPECIFICATION_V1_2026-07-10.md
- docs/architecture/P2_03_FINANCIAL_OWNERSHIP_SPECIFICATION_V1_2026-07-11.md
- docs/architecture/P2_04_RISK_OWNERSHIP_SPECIFICATION_V1_2026-07-13.md
- docs/architecture/certification/P2_03_FINAL_CERTIFICATION_V1_2026-07-11.md
- docs/architecture/certification/P2_04_FINAL_CERTIFICATION_V1_2026-07-13.md
- current runtime code at HEAD f6fb7f3911a978884ca10b22a0eef832a52f9486

Referenced By:
- future P3-02 Implementation
- future P3-02 Final Certification

Methodological Structure Reference (content not carried over):
- docs/architecture/P3_01_DETERMINISTIC_EXECUTION_ORDERING_SPECIFICATION_V1_2026-07-13.md

---

# P3-02 Information Flow Validation Specification

## 1. Document Metadata

See front matter above. This document is the P3-02 Specification, the fifth stage of the P3-02 governance chain (FRA -> SDA -> CGA -> Architecture -> Specification -> Implementation -> Final Certification).

## 2. Purpose

This document translates the twenty Architecture Decisions of `P3_02_INFORMATION_FLOW_VALIDATION_ARCHITECTURE_V1_2026-07-13.md` (the "Architecture") into implementable technical directives: Runtime Contracts, Implementation Units, a File-by-File Change Plan, a No-Change Inventory, and Acceptance Criteria. This document does not decide architecture, does not introduce a new Functional Requirement, Dependency, Architecture Decision, or Architecture Invariant, does not perform a new scientific analysis or capability assessment, and does not specify a complete file diff or a test implementation. Its output is the binding technical contract a future P3-02 Implementation must satisfy.

## 3. Scope

In scope: twenty-one Runtime Contracts (`P3-02-IF-001` through `P3-02-IF-021`) realizing AD-001 through AD-020; four Implementation Units (IU-001 through IU-003, file-touching; IU-004, Verification-Only); a File-by-File Change Plan for all fourteen active runtime files; a No-Change Inventory with individual justification per file; Acceptance Criteria per IU plus global.

Out of scope: any new Functional Requirement, Dependency, Architecture Decision, or Architecture Invariant; any new scientific or capability analysis; any concrete Python signature, complete method body, or file diff; any test implementation as a fixed command; any P3-01 or P3-03 work; any Persistence, Recovery, or Operator Lifecycle Control mechanism; any Position, Financial, or Risk formula or ownership change; any rollback, reset, or transaction mechanism.

## 4. Binding Baseline

- `docs/architecture/P3_02_INFORMATION_FLOW_VALIDATION_ARCHITECTURE_V1_2026-07-13.md` - the sole source of the twenty Architecture Decisions, fifteen Architecture Invariants, and thirteen Architecture Constraints this Specification translates. AD-001, AD-005, and AD-006 require an executable runtime code change; AD-007/AD-008 are primarily verification-and-contract obligations, with functional consequences only insofar as AD-001/AD-005 already require them; every other decision ratifies already-conformant behaviour or is a documentation-only Cross-Unit ratification.
- `docs/architecture/analysis/P3_02_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-13.md`, `docs/architecture/analysis/P3_02_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-13.md`, `docs/architecture/analysis/P3_02_CAPABILITY_GAP_ANALYSIS_V1_2026-07-13.md` - the twenty-four Functional Requirements, fifty-two Dependencies, and twenty-seven Capabilities this Specification's own Traceability (Section 33) confirms complete coverage of, without re-deriving any of them.
- `docs/architecture/P2_02A_POSITION_OWNERSHIP_SPECIFICATION_V1_2026-07-10.md`, `docs/architecture/P2_03_FINANCIAL_OWNERSHIP_SPECIFICATION_V1_2026-07-11.md`, `docs/architecture/P2_04_RISK_OWNERSHIP_SPECIFICATION_V1_2026-07-13.md` - the certified Specification-level contracts IU-004's own Compatibility Verification checks against, without reopening any of them.
- `docs/architecture/P3_01_DETERMINISTIC_EXECUTION_ORDERING_SPECIFICATION_V1_2026-07-13.md`, `docs/architecture/certification/P3_01_FINAL_CERTIFICATION_V1_2026-07-13.md` - the certified P3-01 baseline this Specification's own Compatibility Verification treats as immutable.

## 5. Repository Verification

Repository state, verified directly, not assumed:

- Branch: `run-engine-consolidation-safety`; Local HEAD and Remote HEAD both `f6fb7f3911a978884ca10b22a0eef832a52f9486`, identical, unchanged since the Architecture's own drafting.
- Working tree: unchanged from the state the Architecture document itself verified; `run_engine/` confirmed clean (`git status --short -- run_engine/` empty).

Files re-read in full for this Specification: `run_engine/core/canonical_state.py` (re-confirmed: `get()` at line 107-109 returns `self.state` directly; `update_performance_metrics()` at line 96-98 stores the received reference directly, no copy; `update_risk()` at line 78-82 writes three scalar keys from whatever dict it receives), `run_engine/core/performance.py` (re-confirmed: `self.stats = {}` constructed once, line 4; mutated in place at lines 13-30; returned as the same object at both line 9, the `RUNTIME_FAILURE_EVENT` short-circuit, and line 34, the normal path), `run_engine/core/canonical_enforcer.py` (re-confirmed: eleven `apply_*` methods; `apply_risk` at lines 47-53 is the sole method returning `self.cs.get()`, the complete state dict, at both its `None`-guard branch, line 50, and its normal-write branch, line 53; `apply_performance_metrics` at lines 71-77 returns `self.cs.get()["performance_metrics"]`, a single-key read consistent with the other nine conformant methods), `run_engine/core/loop.py`, `run_engine/core/position.py`, `run_engine/core/risk.py`, `run_engine/core/trade_lifecycle.py` - all four confirmed unchanged from the Architecture's own re-verification.

**`loop.py`'s own return path, independently re-traced line by line for this Specification, per the governing task's own explicit instruction not to classify it as No-Change without repository-grounded confirmation.** `loop.py` contains exactly six `self.cstate.get()` call sites: line 47 (`position_pre = self.cstate.get()["position"]`), lines 68-70 (three scalar reads: `realized_pnl_cumulative`, `equity`, `peak_equity`), line 90 (`canonical_state = self.cstate.get()`, passed read-only, single-use, to `risk_engine.check()` at line 92), and line 100 (`"state": self.cstate.get()`, the Tick-Complete result's own `"state"` field). Every one of these six call sites uses the return value of `get()` exactly once, immediately, either for a single key-index (`["position"]`, three scalar keys) or as a direct pass-through argument or dict value; none of the six retains, compares by identity, or mutates the value `get()` returns, and none assumes `get()` returns the identical object across separate calls. Once `CanonicalState.get()` is changed to return a fresh shallow copy (IU-001), every one of these six call sites continues to behave identically at the value level, and the top-level-aliasing defect at line 100 (AD-004) is closed automatically, without any edit to `loop.py` itself. **`loop.py` therefore requires no functional change**, confirmed by direct, exhaustive trace of every one of its own six `get()` call sites, not merely asserted from the Architecture's own general reasoning.

Repository-wide search re-performed for (case-insensitive, scoped to `run_engine/`, excluding `__pycache__`): `return self.state`, `def get(`, `self.stats`, `performance_metrics`, `apply_risk`, `apply_performance_metrics`, `update_performance_metrics`, `update_risk`. No occurrence was found beyond what the FRA, SDA, CGA, and Architecture already established; no new fact emerged.

## 6. Specification Context

Three of the twenty Architecture Decisions require an executable runtime code change: AD-001 (`CanonicalState.get()`'s own shallow-copy contract), AD-005 (`PerformanceEngine`'s own Structurally Independent publication), and AD-006 (`apply_risk`'s own return-value correction). AD-004's own resolution is a direct, automatic structural consequence of AD-001, requiring no additional code change of its own. AD-007 and AD-008 are primarily verification-and-contract obligations: AD-007's own functional consequence is already fully discharged by AD-001 (top-level) and AD-005 (Performance Metrics), since every other Producer is already conformant (VCF-001); AD-008 introduces no structural mechanism at all, only a future verification obligation. Every remaining decision (AD-002, AD-003, AD-009 through AD-020) ratifies already-conformant behaviour, establishes a Verification-Only obligation, or is a documentation-only Cross-Unit ratification, requiring no runtime code change.

## 7. Normative Terminology

Restated, not newly invented, from the Architecture (Section 6) and binding for the remainder of this document: **Structural Independence, Composite Isolation** - as defined in the Architecture. **Functionally identical** is used in this document exclusively for Python-object, dictionary, and runtime-result comparisons. **Byte-identical/byte-for-byte** is reserved exclusively for file-, git-blob-, or source-line-level comparisons; every occurrence of either term in this document that is not such a comparison is meta-discussion, not a comparison claim.

## 8. Runtime Contract Catalogue

Twenty-one Runtime Contracts are specified, `P3-02-IF-001` through `P3-02-IF-021`, each traceable to exactly one or more governing Architecture Decisions, presented in Sections 9 through 25 grouped by the concrete contract area they realize.

## 9. Canonical Read Contracts

**Contract IF-001 (CanonicalState Read Contract).** Requirement: `CanonicalState.get()` SHALL return a freshly-constructed shallow copy of its own top-level state dictionary on every call, per AD-001. Runtime Behaviour: `get()` no longer returns `self.state` directly; it returns a new top-level `dict` object whose own key-value pairs are copied from `self.state` at the moment of the call. Input Semantics: no parameters. Output Semantics: a `dict` with the same fifteen keys and the same values (by reference, for nested/mutable values; by value, for scalars) `self.state` currently holds. Object Identity: the returned top-level `dict` is a distinct object from `self.state` on every call; `id(get())` differs across any two calls. Lifetime: Ephemeral for mid-tick (Canonical Working State) use; becomes Tick-Stable once incorporated into a Tick-Complete result (IF-002). Mutation Rights: a caller MAY freely mutate its own returned top-level dict without any effect on `CanonicalState`'s own held state; this SHALL NOT constitute a canonical mutation. Publication Contract: not applicable; this is a read contract. Consumer Contract: every consumer, internal (Canonical Working State, IF-018) and external (Tick-Complete result, IF-002/IF-003) alike, uses this identical mechanism. Failure Behaviour: `get()` immediately following a Failed Tick returns a copy reflecting whatever subset of `apply_*` calls already completed before the interrupting exception (IF-017); no special-casing. Acceptance Condition: `id()` of two values returned by two separate `get()` calls, with no intervening write to a copied key, are distinct top-level objects; every key's own value remains equal to `self.state`'s own value at the moment of the call. Verification Method: direct object-identity comparison (IU-001). Scope Boundary: does not, by itself, guarantee Structural Independence for nested mutable values (IF-004, IF-008, IF-010). Traceability: FR-001; DEP-001 through DEP-005; CAP-001; AD-001.

## 10. Canonical Working State Contracts

**Contract IF-018 (Canonical Working State Consumption).** Requirement: Canonical Working State SHALL remain consumable, via the identical `CanonicalState.get()` mechanism IF-001 establishes, only by a component whose own ADR-010 execution position has already been reached in the current tick, per AD-002. Runtime Behaviour: `RiskEngine.check()` remains the sole such consumer (`loop.py:90-92`), unchanged in call signature or position. Input Semantics: `RiskEngine.check(canonical_state, position, regime)` receives, at its own `canonical_state` parameter, the fresh shallow copy IF-001 now returns rather than a live reference; `RiskEngine.check()`'s own read-only usage (`state.get("equity")`, `state.get("peak_equity")`) is unaffected by this change. Output Semantics: not applicable to this contract; governed by IF-014/IF-015. Object Identity: the copy `RiskEngine.check()` receives is distinct from `CanonicalState.state` and from any other tick's own copy. Lifetime: Ephemeral, valid only for the duration of the single `check()` call that receives it. Mutation Rights: `RiskEngine.check()` SHALL NOT mutate its own received `canonical_state` parameter (already confirmed conformant, VCF-004); even if it did, IF-001's own copy semantics would prevent any effect on `CanonicalState`'s own held state. Publication Contract: not applicable. Consumer Contract: `RiskEngine` remains the sole internal Canonical Working State consumer; no future consumer may be added without re-verifying its own execution position. Failure Behaviour: not applicable directly; governed by IF-017. Acceptance Condition: a fresh trace confirms Canonical Working State is consumed only at or after its own producing stage, using the IF-001 mechanism. Verification Method: static re-trace plus behavioural confirmation (IU-004). Scope Boundary: does not decide whether any component's own legitimately-retained private cross-tick state requires isolation (CAP-019, not reopened). Traceability: FR-002; DEP-002, DEP-006, DEP-042; CAP-002; AD-002.

## 11. Tick-Complete Snapshot Contracts

**Contract IF-002 (Tick-Complete Snapshot Stability, General).** Requirement: a Tick-Complete result, once returned by `RunLoop.step()`, SHALL remain stable in every field for as long as it is retained, per AD-003. Runtime Behaviour: achieved compositely via IF-001 (top-level), IF-004/IF-005/IF-006 (Performance Metrics), and the already-conformant fresh-construction behaviour of Position, Strategy Selection, Execution Decision, and Execution Event (VCF-001, no change required). Input Semantics: not applicable; this is an emergent property of `RunLoop.step()`'s own already-existing return statement (`loop.py:98-113`), unchanged in its own construction. Output Semantics: the returned dict's own fourteen keys each individually satisfy Tick-Stable lifetime per their own governing contract (IF-001 for `"state"`; IF-004/IF-006 for `"performance"`; already-conformant for `"position"`, `"decision"`, `"execution"`, `"strategy_weights"`; scalar-immune for `"tick"`, `"regime"`, `"pnl"`, `"equity"`; immutable-by-construction for `"trade_event"`, a frozen `LifecycleEvent` or `None`). Object Identity: no field of a previously-returned result changes object identity or value as a consequence of a later tick. Lifetime: Tick-Stable, per the Architecture's own Information Lifetime Model. Mutation Rights: an external holder MAY mutate its own retained copy without affecting any subsequent tick's own processing (the converse of IF-001's own mutation-rights clause). Publication Contract: no change to `RunLoop.step()`'s own aggregate incremental-publication mechanism (P3-01-AD-003/VC-01, not reopened). Consumer Contract: any consumer, including one retaining a result across arbitrarily many further ticks, observes stable values. Failure Behaviour: a Failed Tick produces no Tick-Complete result at all (IF-017); this contract applies only to results actually returned. Acceptance Condition: a Tick-Complete result captured at tick N, re-inspected after ticks N+1 through N+k execute (k >= 1), remains functionally identical at every field, including every nested field, to its own value at the moment of return. Verification Method: multi-tick retained-reference comparison (IU-001, IU-002, jointly). Scope Boundary: does not require a new, dedicated snapshot-construction operation. Traceability: FR-003; DEP-001, DEP-007, DEP-009; CAP-003; AD-003.

**Contract IF-003 (Top-Level Result Object-Identity Isolation).** Requirement: `RunLoop.step()`'s own `"state"` field SHALL NOT be, and SHALL never again become, object-identical with `CanonicalState`'s own internally-held dictionary, per AD-004. Runtime Behaviour: achieved entirely as a structural, automatic consequence of IF-001; `loop.py:100`'s own `"state": self.cstate.get()` line requires no edit. Input Semantics: not applicable. Output Semantics: `result["state"]` is a fresh top-level dict, distinct from `engine.cstate.state`. Object Identity: `id(result["state"]) != id(engine.cstate.state)`, immediately and at every subsequent tick. Lifetime: Tick-Stable. Mutation Rights: per IF-001. Publication Contract: not applicable. Consumer Contract: any consumer holding `result["state"]` across ticks observes stable, correct values. Failure Behaviour: not applicable; governed by IF-017. Acceptance Condition: `id(result["state"])` differs from `id(engine.cstate.state)` immediately after every call to `RunLoop.step()`. Verification Method: direct object-identity comparison (IU-001). Scope Boundary: introduces no mechanism beyond IF-001; does not address any nested value's own aliasing (IF-004 through IF-006, IF-010). Traceability: FR-003; DEP-001, DEP-007; CAP-004; AD-004; Functional Gap FG-002.

## 12. Information Lifetime Contracts

**Contract IF-019 (Information Lifetime Classification).** Requirement: every canonical runtime object SHALL possess exactly one of three lifetimes - Ephemeral, Tick-Stable, or Historical - per the Architecture's own Information Lifetime Model (Section 12 of the Architecture). Runtime Behaviour: no runtime construct implements "lifetime" as an explicit, tagged property; lifetime is an emergent classification this Specification assigns per object, based on each object's own governing contract. Input Semantics: not applicable. Output Semantics: Ephemeral - any `CanonicalState.get()` result consumed strictly within one internal call (IF-018); Tick-Stable - any field of a returned Tick-Complete result (IF-002); Historical - Lifecycle History records (IF-012), never republished, only appended to. Object Identity: governed per-lifetime by IF-001 (Ephemeral/Tick-Stable transition boundary) and IF-012 (Historical, append-only). Lifetime: this contract is itself the lifetime taxonomy. Mutation Rights: per each constituent lifetime's own governing contract. Publication Contract: not applicable. Consumer Contract: a consumer's own expectations (safe to retain indefinitely, safe only for the current call, or permanently append-only) are determined by which lifetime the object it receives belongs to. Failure Behaviour: a Failed Tick produces no new Tick-Stable object; Ephemeral and Historical objects are unaffected by tick outcome, per IF-017. Acceptance Condition: every object in the Runtime Object Inventory (FRA Section 9) is classified into exactly one of the three lifetimes, with no object left unclassified. Verification Method: documentation cross-check (IU-004). Scope Boundary: introduces no new runtime data structure or explicit lifetime tag. Traceability: FR-003, FR-021; CAP-003, CAP-024; AD-003, AD-011.

## 13. Object Identity Contracts

**Contract IF-010 (Nested Mutable Structures, Full-Depth Independence).** Requirement: every canonical object possessing nested mutable structure SHALL have every nesting level's own Structural Independence guaranteed at its own publication time, per AD-009. Runtime Behaviour: currently, Performance Metrics (a dict of per-action dicts) is the sole canonical object with nested mutable structure; every other dict-shaped canonical object (Position, Strategy Selection, Execution Decision, Execution Event) is a single-level dict of scalars, already fully isolated once the dict itself is a distinct object (IF-008). Input Semantics: not applicable. Output Semantics: for Performance Metrics specifically, both the outer dict and every one of its own per-action inner dicts SHALL be distinct objects from the corresponding structures in `PerformanceEngine.stats` (IF-004). Object Identity: `id()` of every nesting level differs between the published value and the accumulator it was derived from. Lifetime: Tick-Stable once published (IF-002). Mutation Rights: `PerformanceEngine` MAY continue to mutate its own `self.stats` accumulator, at every nesting level, after publication; this SHALL have no effect on any already-published value. Publication Contract: governed by IF-004/IF-006. Consumer Contract: any consumer of Performance Metrics may safely retain it, including its own inner dicts, without aliasing exposure. Failure Behaviour: not applicable directly. Acceptance Condition: for Performance Metrics, `id()` of every per-action inner dictionary published at tick N differs from the corresponding inner dictionary published at tick N+1, in addition to the outer dictionary's own distinct identity. Verification Method: nested object-identity comparison (IU-002). Scope Boundary: does not itself specify the mechanism (a full or partial copy, or an equivalent independent-construction approach) by which full-depth independence is achieved; that is IU-002's own implementation-level concern, still without a concrete Python signature specified here. Traceability: FR-004; DEP-009; CAP-005, CAP-006; AD-009.

## 14. Producer Contracts

**Contract IF-008 (Producer Isolation, General).** Requirement: every Producer SHALL, at the moment it hands a dict-shaped value to `CanonicalEnforcer` for publication, supply a value that is Structurally Independent from any object it will itself further mutate, at every nesting level, per AD-007. Runtime Behaviour: already fully satisfied, without further change, for `PositionEngine.snapshot()` (`position.py:75-83`, a fresh dict literal every call), `StrategySelector.select`/`decide` (`strategy.py:21,47,69`), and `Executor.execute` (`executor.py:15,22,28`) - each independently re-confirmed this Specification's own Section 5. Requires one functional change, specified by IF-004, for `PerformanceEngine`. Input Semantics: each Producer's own existing input parameters, unchanged. Output Semantics: each Producer's own published value is distinct in object identity from any object the Producer itself continues to hold or mutate. Object Identity: `id()` of the value published at tick N differs, at every nesting level, from `id()` of the value published at tick N+1, whenever a publication occurs at both ticks. Lifetime: the published value becomes Tick-Stable (IF-002) upon publication; a Producer's own private accumulator (where one exists) remains Ephemeral to that Producer's own internal use. Mutation Rights: a Producer's own private, internally-retained working state MAY continue to exist and be mutated privately; only the value handed to `CanonicalEnforcer` is bound by this contract. Publication Contract: governed jointly with IF-011 (Writer-on-Behalf-Of). Consumer Contract: governed by IF-009. Failure Behaviour: not applicable directly. Acceptance Condition: for every canonical Producer, the published-value object-identity property above holds at every future HEAD. Verification Method: per-Producer object-identity comparison (IU-002 for Performance Metrics specifically; IU-004 for the four already-conformant Producers). Scope Boundary: does not require immutability of an object's own internals beyond independence from its own producer's own future mutation; does not select a specific isolation mechanism for any Producer beyond what IF-004 specifies for Performance Metrics. Traceability: FR-004, FR-005; DEP-008, DEP-009, DEP-011 through DEP-014; CAP-005, CAP-006, CAP-007; AD-007.

**Contract IF-004 (PerformanceEngine Publication Contract).** Requirement: `PerformanceEngine` MAY continue to retain and privately mutate `self.stats` across ticks; `PerformanceEngine.update()` SHALL, at the point it returns the value `RunLoop` publishes, supply a value that is Structurally Independent from `self.stats` at every nesting level `self.stats` itself mutates, per AD-005. Runtime Behaviour: `performance.py:9` (the `RUNTIME_FAILURE_EVENT` short-circuit) and `performance.py:34` (the normal return path) both currently `return self.stats` directly; both SHALL instead return a value that is a distinct object, at every nesting level, from `self.stats`. `PerformanceEngine`'s own internal accumulation logic (lines 11-32: the `+=`/weighted-average update formulas) remains entirely unchanged; only the shape of the value handed to the caller changes. Input Semantics: `update(decision, pnl, regime, trade_event)`, unchanged. Output Semantics: a dict with the same key structure (`{action: {'pnl': float, 'trades': int, 'winrate': float}}`) and the same numeric values `self.stats` currently holds, but constructed as an independent object at every level. Object Identity: per IF-010. Lifetime: the returned value becomes Tick-Stable upon publication (IF-002); `self.stats` itself remains Ephemeral, private, Producer-internal state, directly analogous to `PositionEngine`'s own already-certified private cross-tick state (P2-02A Section 13, not reopened). Mutation Rights: `PerformanceEngine` retains full mutation rights over its own `self.stats`; it loses no capability by this contract, only the ability to hand out that same object for publication. Publication Contract: `RunLoop.step()`'s own call site (`loop.py:95-96`, `performance = self.performance_engine.update(...)`; `self.enforcer.apply_performance_metrics(performance)`) requires no change, since it already forwards whatever `update()` returns. Consumer Contract: any future consumer of Performance Metrics observes stable, independent values. Failure Behaviour: `PerformanceEngine.update`'s own `RUNTIME_FAILURE_EVENT` short-circuit (line 8-9) is unaffected in its own trigger condition; only its own return value's object-identity property changes, identically to the normal path. Acceptance Condition: `id()` of the value returned at tick N differs, at every nesting level, from `id()` of the value returned at tick N+1; a value captured at tick N and re-inspected after further ticks execute remains functionally identical to its own value at capture. Verification Method: dual object-identity and multi-tick retained-value comparison (IU-002). Scope Boundary: does not redesign `PerformanceEngine`'s own accounting methodology (TD-004, P3-03's own scope, not reopened); does not introduce a new Performance Metric; does not specify a concrete Python mechanism (the specific technique achieving full-depth independence is an Implementation-stage choice, within IU-002's own scope). Traceability: FR-004; DEP-008, DEP-009, DEP-019, DEP-035, DEP-050; CAP-006; AD-005, AD-009; Functional Gap FG-003; TD-004 (not reopened).

## 15. Consumer Contracts

**Contract IF-009 (Consumer Read-Only Discipline).** Requirement: no Primary Consumer SHALL mutate the runtime object it consumes; this property SHALL be independently and repeatably verifiable, per AD-008. Runtime Behaviour: no structural read-only enforcement mechanism is introduced; every named Primary Consumer (`StrategySelector`, `Executor`, `TradeLifecycleEngine`, `PositionEngine`, `PnLEngine`, `RiskEngine`, `PerformanceEngine`) already exhibits no in-place mutation of a received parameter (VCF-004, re-confirmed this Specification's own Section 5). Input Semantics: unchanged for every consumer. Output Semantics: unchanged. Object Identity: not applicable directly; consumers receive values already isolated per IF-001/IF-008. Lifetime: not applicable to this contract. Mutation Rights: explicitly none, for any Primary Consumer, of any object it consumes. Publication Contract: not applicable. Consumer Contract: this contract is, in its entirety, the Consumer Contract for every named Primary Consumer. Failure Behaviour: not applicable. Acceptance Condition: a repeatable, independent procedure confirms, for every Primary Consumer named in the Runtime Ownership Matrix, that the object it receives is unchanged in every field after the consuming call returns. Verification Method: a dedicated before/after field-comparison procedure per consumer, executed independently of manual source inspection (IU-004). Scope Boundary: does not introduce a structural enforcement mechanism (no `MappingProxyType` or equivalent wrapper). Traceability: FR-005, FR-017; DEP-003, DEP-004, DEP-010; CAP-007, CAP-008; AD-008; Verification Gap VG-001; Verified Conformant Finding VCF-004.

## 16. Writer-on-Behalf-Of Contracts

**Contract IF-011 (Writer-on-Behalf-Of Exclusivity and Uniform Return Contract).** Requirement: `CanonicalEnforcer` SHALL remain the exclusive Writer-on-Behalf-Of publication path for every canonical object this Specification's scope covers, except Runtime Tick's own explicit Matrix exception; every `apply_*` method SHALL follow one uniform return-value contract, per AD-006 and AD-018. Runtime Behaviour: exactly one direct `CanonicalState.update_*` call site outside `CanonicalEnforcer` remains permitted (`update_tick`, `loop.py:42`); every other mutation occurs through a named `apply_*` method (re-confirmed, Section 5). `apply_risk` (`canonical_enforcer.py:47-53`) SHALL no longer return `self.cs.get()` (the complete state dict) at either its `None`-guard branch (line 50) or its normal-write branch (line 53); it SHALL instead return only the Risk Metrics it itself publishes via `update_risk` (Drawdown, Drawdown Ratio, `risk_allocation_factor`). Input Semantics: `apply_risk(risk)`, unchanged signature-level meaning (a dict or `None`). Output Semantics: the three published Risk Metric values, in a shape consistent with the other ten `apply_*` methods' own single-value-or-scoped-subset return convention; no unpublished input key (`equity`, `peak_equity`, already separately owned by `PnLEngine`) appears in the return value. Object Identity: the corrected return value, being newly constructed from already-scalar values, introduces no new aliasing surface (consistent with IF-008/IF-010). Lifetime: the returned value, if consumed, becomes Tick-Stable; currently unconsumed by any active caller. Mutation Rights: not applicable; scalars are immutable. Publication Contract: `apply_risk`'s own write behaviour (`self.cs.update_risk(risk)`) is entirely unchanged; only its own return value's shape changes. Consumer Contract: any future consumer of `apply_risk`'s own return value receives a correctly-scoped value. Failure Behaviour: not applicable directly; governed by IF-017. Acceptance Condition: `apply_risk`'s own return value contains exactly the Risk Metrics `update_risk` itself just wrote or confirmed, matching the shape every other `apply_*` method already follows; the complete `CanonicalState.state` dictionary is never returned by any `apply_*` method after this contract is implemented. Verification Method: direct return-value inspection (IU-003). Scope Boundary: does not change which three keys `apply_risk`/`update_risk` write; does not specify a concrete Python signature; scoped to `run_engine/`, not the untracked review/backup directories outside the active runtime. Traceability: FR-006, FR-007; DEP-015 through DEP-019, DEP-043; CAP-009, CAP-010; AD-006, AD-018; Rule OM-003; Functional Gap FG-004.

## 17. Runtime Event Contracts

**Contract IF-012 (Runtime Event Semantic Stability).** Requirement: every explicit Runtime Event SHALL remain a frozen, structurally immutable object after construction, generated at exactly one call site per transition type, per AD-010. Runtime Behaviour: `LifecycleEvent` (`trade_lifecycle.py:8-25`) remains `@dataclass(frozen=True)`; each of its own five `event_type` values (`TRADE_OPENED`, `SCALE_IN`, `PARTIAL_CLOSE`, `TRADE_CLOSED`, `RUNTIME_FAILURE_EVENT`) continues to originate from exactly one dedicated method (`_open_trade`, `_scale_in`, `_partial_close`, `_full_close`, `_failure_event` respectively); no code change required. Input Semantics: unchanged. Output Semantics: unchanged. Object Identity: events are passed by reference between Producer and Consumer, safely, since `frozen=True` already prevents mutation regardless of reference-sharing. Lifetime: an event, once appended to `Trade.events` or `TradeLifecycleEngine.failure_events`, becomes part of Historical lifetime (IF-013). Mutation Rights: none, for any consumer, structurally enforced by `frozen=True`. Publication Contract: not applicable in the Writer-on-Behalf-Of sense; `TradeLifecycleEngine` directly constructs and appends its own events. Consumer Contract: `PositionEngine` and `PnLEngine` each receive event references unchanged. Failure Behaviour: `RUNTIME_FAILURE_EVENT` generation remains scoped exclusively to lifecycle-transition rejection, never generated for a Failed Tick (IF-017, not extended). Acceptance Condition: a fresh trace confirms every `LifecycleEvent.event_type` still originates from exactly one call site, and the dataclass remains frozen, at any future HEAD. Verification Method: static source re-trace (IU-004). Scope Boundary: does not introduce distinct event objects for the Decision/Financial/Risk/Performance layers. Traceability: FR-010; DEP-023, DEP-024, DEP-044; CAP-011; AD-010.

## 18. Lifecycle History Contracts

**Contract IF-013 (Lifecycle History Immutability and Non-Duplication).** Requirement: Lifecycle History SHALL remain exclusively owned by `TradeLifecycleEngine`, SHALL NOT be duplicated into `CanonicalState`, and completed records SHALL remain immutable, per AD-011. Runtime Behaviour: `CanonicalState`'s own fifteen schema keys contain no lifecycle-history field (re-confirmed, Section 5); `current_position()` (`trade_lifecycle.py:89-103`) continues to return a freshly-constructed plain dict, never a live reference into `self.trades`/`self.active_trade`. Input Semantics: not applicable. Output Semantics: `current_position()`'s own returned dict is a Derived View, structurally independent of the `Trade` object it summarizes. Object Identity: no external consumer holds a reference to a live `Trade` object. Lifetime: Historical, permanent, append-only for `LifecycleEvent`/`Trade` records themselves; Ephemeral for `current_position()`'s own returned summary. Mutation Rights: `Trade`'s own internal mutability (`quantity`, `exit_price`, `exit_tick`, `status`, `events`) remains confined to `TradeLifecycleEngine`'s own private management; no external mutation right exists or is granted. Publication Contract: not applicable; History is never published via `CanonicalEnforcer`. Consumer Contract: `PositionEngine` (via `current_position()`) and `PnLEngine` (via `trade_event`) each receive Derived Views or immutable events, never live references. Failure Behaviour: not applicable directly; governed by IF-017. Acceptance Condition: `CanonicalState`'s own schema, re-enumerated at any future HEAD, continues to contain no lifecycle-history field. Verification Method: schema enumeration and reference-tracing (IU-004). Scope Boundary: does not extend to `Trade`'s own internal mutability. Traceability: FR-011; DEP-023, DEP-025 through DEP-027, DEP-041; CAP-012; AD-011.

## 19. Position Flow Contracts

**Contract IF-014 (Position Information Flow Conformance).** Requirement: Position information SHALL continue to flow exclusively as: Lifecycle Event/current position -> `PositionEngine` (Computational Authority) -> a Structurally Independent snapshot -> `CanonicalState` (Authoritative Owner, via `CanonicalEnforcer`) -> `PnLEngine`/`RiskEngine` (Primary Consumers), per AD-012. Runtime Behaviour: unchanged; `PositionEngine.snapshot()` already constructs a fresh dict on every call (re-confirmed, Section 5); `update_post_trade`'s own six-attribute sequential mutation pattern is unaffected by this Specification (CAP-019, not reopened). Input Semantics: unchanged (`execution`, `state`, `lifecycle_position`). Output Semantics: unchanged (`{"position", "side", "entry_price", "quantity", "last_price", "exposure"}`). Object Identity: already conformant, per IF-008. Lifetime: Tick-Stable upon publication. Mutation Rights: `PnLEngine` and `RiskEngine` remain read-only consumers of Position (already conformant, IF-009). Publication Contract: via `CanonicalEnforcer.apply_position`, unchanged. Consumer Contract: `PnLEngine` reads `position_pre["entry_price"]` (Entry Basis, pre-trade view, P2-02A's own already-certified contract, not reopened); `RiskEngine` reads the post-trade `position` parameter, including Exposure, derived exclusively from `side`/`quantity`/`last_price`. Failure Behaviour: governed by IF-017; CAP-019 not reopened. Acceptance Condition: a fresh trace confirms the same topology at any future HEAD; Exposure remains absent from the Runtime Ownership Matrix as an independent row. Verification Method: static re-trace and regression re-run (IU-004). Scope Boundary: does not reopen P2-02A's own certified ownership, formula, or pre-trade-view contract; does not reopen CAP-019's own classification. Traceability: FR-012; DEP-011, DEP-016, DEP-020, DEP-025, DEP-028 through DEP-031, DEP-038; CAP-013; AD-012; P2-02A (not reopened).

## 20. Financial Flow Contracts

**Contract IF-015 (Financial Information Flow Conformance).** Requirement: Financial information SHALL continue to flow exclusively as: Lifecycle Facts + Entry Basis -> `PnLEngine` (Computational Authority) -> `CanonicalState` (Authoritative Owner, via `CanonicalEnforcer`) -> `RiskEngine` (Primary Consumer), per AD-013. Runtime Behaviour: unchanged; every financial value remains a Python scalar (`pnl`, `realized_pnl_cumulative`, `equity`, `peak_equity`), structurally immune to aliasing (VCF-002, not reopened). Input Semantics: unchanged. Output Semantics: unchanged. Object Identity: not applicable to scalars. Lifetime: Tick-Stable upon publication (trivially, since scalars are immutable). Mutation Rights: `RiskEngine` remains a read-only consumer. Publication Contract: via `CanonicalEnforcer.apply_pnl`/`apply_realized_pnl_cumulative`/`apply_equity`/`apply_peak_equity`, unchanged. Consumer Contract: `RiskEngine.check()` reads `equity`/`peak_equity` from the Canonical Working State copy (IF-018). Failure Behaviour: governed by IF-017; Post-Exception Financial/Lifecycle Divergence (RR-002) remains documented, not resolved. Acceptance Condition: a fresh trace confirms the same topology at any future HEAD. Verification Method: static re-trace and P2-03 regression re-run (IU-004). Scope Boundary: does not reopen P2-03's own certified ownership or formulas. Traceability: FR-014; DEP-012, DEP-017, DEP-020, DEP-021, DEP-026, DEP-028, DEP-033, DEP-034, DEP-039; CAP-014; AD-013; P2-03 (not reopened).

## 21. Risk Flow Contracts

**Contract IF-016 (Risk Information Flow Conformance, Incorporating the apply_risk Correction).** Requirement: Risk information SHALL continue to flow exclusively as: Canonical Financial State (via IF-018) + Position -> `RiskEngine` (Computational Authority) -> `CanonicalState` (Authoritative Owner, via `CanonicalEnforcer`, with `apply_risk`'s own return value corrected per IF-011), per AD-014. Runtime Behaviour: `RiskEngine.check()`'s own formula (`risk.py:38-102`) is entirely unchanged; the sole change within this flow's own scope is IF-011's own `apply_risk` return-value correction. Input Semantics: `check(state, position, regime)`, unchanged. Output Semantics: `{"equity", "peak_equity", "drawdown", "drawdown_ratio", "exposure"}`, unchanged; `update_risk()` continues to extract and store exactly three of these five keys (`drawdown`, `drawdown_ratio`, renamed to `risk_allocation_factor` from `exposure`) as separate `CanonicalState` scalar keys, unchanged. Object Identity: not applicable to scalars. Lifetime: Tick-Stable upon publication. Mutation Rights: no active downstream consumer of Risk Metrics exists among the twenty-four P3-02 Functional Requirements (confirmed absent, SDA Section 12, not introduced by this Specification). Publication Contract: per IF-011. Consumer Contract: none currently active. Failure Behaviour: not applicable directly. Acceptance Condition: a fresh trace confirms the same topology, and `apply_risk`'s own corrected return value, at any future HEAD. Verification Method: static re-trace, direct `apply_risk` return-value test, and P2-04 regression re-run (IU-003, IU-004). Scope Boundary: does not reopen P2-04's own certified ownership or formulas; does not change `RiskEngine.check()`'s own formula. Traceability: FR-015; DEP-006, DEP-013, DEP-018, DEP-020, DEP-021, DEP-029, DEP-033, DEP-040; CAP-015; AD-014; P2-04 (not reopened).

## 22. Performance Flow Contracts

**Contract IF-005 (CanonicalState Performance Storage Contract).** Requirement: `CanonicalState.update_performance_metrics()` SHALL NOT accept a value that remains subject to further Producer mutation as its own canonical stored value; `CanonicalState.state["performance_metrics"]` SHALL be object-identity-distinct from `PerformanceEngine.stats`, per AD-005. Runtime Behaviour: `update_performance_metrics()` (`canonical_state.py:96-98`) itself requires no code change - its own existing behaviour (`self.state["performance_metrics"] = performance_metrics`, storing whatever reference it receives) already correctly stores a Structurally Independent value once `PerformanceEngine.update()` itself supplies one, per IF-004. The isolation responsibility rests entirely with the Producer (`PerformanceEngine`), not with `CanonicalState`'s own storage method, consistent with how every other `update_*` method already operates (none of `CanonicalState`'s own `update_*` methods performs its own copy; every one trusts its own Producer). Input Semantics: `update_performance_metrics(performance_metrics)`, unchanged signature. Output Semantics: `self.state["performance_metrics"]` holds exactly the value it received. Object Identity: distinct from `PerformanceEngine.stats` at every nesting level, as a direct, automatic consequence of IF-004; not independently re-verified by `CanonicalState` itself. Lifetime: Tick-Stable once stored. Mutation Rights: `CanonicalState` does not, and is not required to, defend against a hypothetically non-conformant Producer; IF-004's own contract is the sole isolation guarantee. Publication Contract: invoked exclusively by `CanonicalEnforcer.apply_performance_metrics` (IF-006). Consumer Contract: governed by IF-002 (Tick-Stable once read back). Failure Behaviour: not applicable directly. Acceptance Condition: `id(CanonicalState.state["performance_metrics"])` differs from `id(PerformanceEngine.stats)` at every tick after publication. Verification Method: object-identity comparison (IU-002). Scope Boundary: does not require `update_performance_metrics()` itself to perform a copy; the copy depth required (full nesting depth, per IF-010) is justified specifically because Performance Metrics is the sole canonical object with nested mutable structure - no unnecessary deep-copy obligation is introduced for any other object or storage method. Traceability: FR-004; DEP-008, DEP-009; CAP-006; AD-005, AD-009.

**Contract IF-006 (CanonicalEnforcer apply_performance_metrics Contract).** Requirement: Publication of Performance Metrics SHALL continue to occur exclusively via the existing `CanonicalEnforcer.apply_performance_metrics` path; its own return value SHALL equal the actually-published canonical value; the Producer-internal object and the returned published value SHALL NOT share mutable object identity, per AD-005/AD-018. Runtime Behaviour: `apply_performance_metrics` (`canonical_enforcer.py:71-77`) requires no code change - its own existing `None`-guard-then-write-then-return-stored-value shape already correctly returns `self.cs.get()["performance_metrics"]`, which, once IF-005 stores an already-independent value, is itself that same independent value, not the accumulator. Input Semantics: unchanged. Output Semantics: unchanged in shape; changed in the object-identity property of the value it returns, as an automatic consequence of IF-004/IF-005. Object Identity: the returned value is distinct from `PerformanceEngine.stats` (per IF-004) and, since IF-001 makes `get()` return a shallow copy, is read from that copy's own `"performance_metrics"` entry - itself the same nested object as `self.state["performance_metrics"]`, correctly reflecting IF-005's own stored value. Lifetime: Tick-Stable. Mutation Rights: not applicable; this is a read-back of an already-independent value. Publication Contract: this contract, together with IF-005, is the complete Publication Contract for Performance Metrics. Consumer Contract: per IF-002. Failure Behaviour: not applicable directly. Acceptance Condition: `apply_performance_metrics`'s own return value is object-identity-distinct from `PerformanceEngine.stats` at every tick. Verification Method: object-identity comparison (IU-002). Scope Boundary: no code change to this method; its own conformance is entirely a consequence of IF-001, IF-004, IF-005. Traceability: FR-004, FR-016; DEP-014, DEP-019, DEP-035, DEP-050; CAP-006, CAP-016; AD-005, AD-015; TD-004 (not reopened).

**Contract IF-007 (Performance Information Flow, Methodology Unchanged).** Requirement: Performance information's own current-state shape (decision-keyed, not lifecycle-outcome-keyed) SHALL remain entirely unchanged in accounting methodology; only object-identity discipline, per IF-004 through IF-006, changes, per AD-015. Runtime Behaviour: `PerformanceEngine.update()`'s own accounting formulas (`performance.py:20-32`) remain byte-for-byte unchanged from their own pre-Specification state - a genuine source-line comparison of the formula statements themselves - while the container those statements populate becomes Structurally Independent per IF-004. Input Semantics: unchanged (`decision, pnl, regime, trade_event`). Output Semantics: unchanged key structure and unchanged numeric values, per identical inputs. Object Identity: per IF-004. Lifetime: per IF-002. Mutation Rights: per IF-004. Publication Contract: per IF-005/IF-006. Consumer Contract: unaffected; no new consumer introduced. Failure Behaviour: `RUNTIME_FAILURE_EVENT` short-circuit unaffected in trigger condition. Acceptance Condition: `PerformanceEngine.update`'s own formula statements are byte-for-byte unchanged from pre-Specification source; its own returned object identity satisfies IF-004. Verification Method: source-line diff plus behavioural test (IU-002). Scope Boundary: does not redesign `PerformanceEngine`'s own accounting methodology; does not introduce a new Performance Metric; does not advance TD-004. Traceability: FR-016; DEP-014, DEP-019, DEP-035, DEP-050; CAP-016; AD-015; TD-004 (not reopened).

## 23. Failure Flow Contracts

**Contract IF-017 (Failed-Tick and Exception Information Flow).** Requirement: a Failed Tick SHALL continue to produce no Tick-Complete result; whatever `apply_*` calls already executed internally before the interrupting exception SHALL remain, unaltered, in `CanonicalState`'s own held state; Post-Exception Financial/Lifecycle Divergence (both instances) SHALL remain documented, non-blocking Residual Risks, per AD-016. Runtime Behaviour: no code change; `RunLoop.step()`'s own control flow already guarantees no `return` executes if an exception propagates (P3-01-AD-004, not reopened); IF-001's own copy-on-read semantics apply identically after a Failed Tick as during any normal tick. Input Semantics: not applicable. Output Semantics: no Tick-Complete result for a Failed Tick, under any circumstance. Object Identity: a `get()` call immediately following a Failed Tick returns a fresh copy (IF-001) reflecting whatever was already durably published. Lifetime: not applicable to a Failed Tick's own non-existent result; internally-published values retain their own already-established lifetime. Mutation Rights: no rollback, reset, or transaction mechanism exists or is introduced. Publication Contract: unaffected; whichever `apply_*` calls already ran, ran with their own already-specified contracts (IF-004 through IF-016, as applicable). Consumer Contract: no consumer, internal or external, ever observes a Failed Tick's own partial state externally; internal next-tick consumption of already-durable partial state is unchanged. Failure Behaviour: this contract is, in its entirety, a Failure Behaviour specification. Acceptance Condition: no field of any Failed Tick is ever observable in any Tick-Complete result; a fresh `get()` call immediately following a Failed Tick returns a value consistent with whatever `apply_*` calls actually completed. Verification Method: simulated-exception behavioural test at multiple injection points (IU-004). Scope Boundary: does not design a Persistence, Recovery, rollback, reset, or transaction mechanism; does not resolve RR-002 or the `PositionEngine` Residual Risk (CAP-019, not reopened). Traceability: FR-018; DEP-024, DEP-032, DEP-046; CAP-021, CAP-019; AD-016; P3-01-AD-004, P3-01-AD-006 (not reopened); RR-002; Post-Exception Financial/Lifecycle Divergence.

## 24. HOLD and No-Execution Contracts

**Contract IF-020 (HOLD and No-Execution Information Flow Conformance).** Requirement: a `HOLD` or no-execution tick SHALL continue to execute all twelve ADR-010 stages; the Tick-Complete Snapshot Stability guarantee (IF-002) SHALL apply identically to a HOLD tick's own returned result, per AD-017. Runtime Behaviour: unchanged; every already-certified `None`-input guard in `PnLEngine`, `PerformanceEngine`, and `PositionEngine` remains untouched; `TradeLifecycleEngine.current_position()`'s own no-active-trade branch continues to return a well-formed FLAT-shaped dict (Documentation Gap DG-002, a terminological note, not a substantive change). Input Semantics: unchanged. Output Semantics: every downstream stage produces a well-defined, numerically-unchanged result for a no-event input. Object Identity: per IF-001 through IF-010, applied identically regardless of tick outcome. Lifetime: per IF-002, applied identically to a HOLD tick's own result. Mutation Rights: unchanged. Publication Contract: unchanged; every stage still publishes via `CanonicalEnforcer`. Consumer Contract: unchanged. Failure Behaviour: `HOLD` is not a failure condition; not governed by IF-017. Acceptance Condition: a scripted HOLD-only tick sequence produces a complete, well-formed, Tick-Stable result at every tick, with every financial and risk key numerically unchanged from the prior tick. Verification Method: scripted behavioural test (IU-004). Scope Boundary: does not reopen P3-01-AD-005; does not evaluate `StrategySelector`'s own cooldown/weighting logic. Traceability: FR-019; DEP-027, DEP-031, DEP-034, DEP-047; CAP-022; AD-017.

## 25. Alternative Information Path Contracts

**Contract IF-021 (Alternative Information Path Exclusivity).** Requirement: exactly one active information-flow path SHALL exist; no alternative active path may bypass IF-001, IF-008, or IF-011, per AD-019. Runtime Behaviour: unchanged; `run_engine/core/decision.py`, `run_engine/runtime/`, `run_engine/execution/` (top-level), `run_engine/feedback/`, `run_engine/logging/`, `run_engine/core/position_sizing.py`, and `run_engine/core/state_modulation.py` remain confirmed unimported. Input Semantics: not applicable. Output Semantics: not applicable. Object Identity: not applicable. Lifetime: not applicable. Mutation Rights: not applicable. Publication Contract: no dormant file writes to `CanonicalState`, directly or indirectly. Consumer Contract: not applicable. Failure Behaviour: not applicable. Acceptance Condition: a repository-wide import search from `run_engine/main.py` and `run_engine/core/loop.py` continues to reach exactly the same active-collaborator set, with no import edge into any confirmed-inactive component, at any future HEAD. Verification Method: repository-wide, AST-based import-closure check (IU-004). Scope Boundary: does not classify or dispose of any dormant file; remains Phase 6 Repository Consolidation's own scope. Traceability: FR-020; DEP-048; CAP-023; AD-019.

Note on numbering: `IF-001` through `IF-021` are twenty-one distinct contract IDs, assigned by thematic section rather than by strict sequential position in Sections 9 through 25 (so, for example, `IF-018` and `IF-019` appear textually before `IF-004` through `IF-007`); every ID from `IF-001` through `IF-021` is defined exactly once above and individually and completely enumerated in Section 33.2.

## 26. Implementation Units

**IU-001 - Canonical Read and Snapshot Isolation.**

Ziel: realize IF-001 (`CanonicalState.get()`'s own shallow-copy contract), IF-002/IF-003 (Tick-Complete top-level isolation and prior-snapshot stability) as automatic structural consequences.

Betroffene Komponenten: `CanonicalState` (Computational mechanism change); `RunLoop` (verification only, no edit, per Section 5's own exhaustive trace).

Betroffene Dateien: `run_engine/core/canonical_state.py` (functional change: `get()`); `run_engine/core/loop.py` (verification only, confirmed No-Change, Section 5).

Dependencies: none upstream within this Specification; IU-002 and IU-003 both depend on IU-001's own `get()` change being in place first, since `apply_performance_metrics` and `apply_risk` both call `self.cs.get()` internally.

Voraussetzungen: repository state unchanged from Section 5's own verification.

Runtime Contracts: IF-001, IF-002, IF-003, IF-019.

Acceptance Criteria: **P3-02-SPEC-AC-001.** `CanonicalState.get()` returns a new top-level `dict` object on every call. **P3-02-SPEC-AC-002.** A value returned by `get()` before a subsequent write to `CanonicalState` remains, at every top-level key, equal to the value that was true when it was returned, regardless of how many further writes or ticks occur afterward. **P3-02-SPEC-AC-003.** `RunLoop.step()`'s own `"state"` field is never object-identical with `CanonicalState.state`. **P3-02-SPEC-AC-004.** `RunLoop`'s own six `get()` call sites (`loop.py:47,68,69,70,90,100`) each remain byte-for-byte unchanged in source line from their own pre-Implementation state (a genuine source-line comparison, confirming No-Change). **P3-02-SPEC-AC-005.** `python -m compileall run_engine` PASSes.

Testumfang: `compileall`; import test confirming `CanonicalState` imports without error; direct `get()` object-identity test (two calls, distinct `id()`); external-mutation-of-returned-value test (mutate the returned copy, confirm `CanonicalState.state` unaffected); multi-tick retained-reference stability test (capture a result at tick N, execute further ticks, re-inspect); HOLD-tick snapshot-stability test; `CanonicalState` schema-key-count and key-name unchanged test (still fifteen keys); full regression re-run of the already-certified P2-02A/P2-03/P2-04/P3-01 scenarios confirming every already-certified field remains functionally identical.

No-Change-Grenzen: no change to `CanonicalState`'s own schema, default values, or any `update_*` method's own write behaviour beyond `get()` itself; no change to `loop.py`.

---

**IU-002 - Performance Metrics Structural Isolation.**

Ziel: realize IF-004 (`PerformanceEngine`'s own Structurally Independent publication), IF-005 (`CanonicalState`'s own storage, confirmed No-Change), IF-006 (`apply_performance_metrics`, confirmed No-Change), IF-010 (full-depth nested independence), IF-007 (methodology unchanged).

Betroffene Komponenten: `PerformanceEngine` (functional change); `CanonicalState`, `CanonicalEnforcer` (verification only, no edit).

Betroffene Dateien: `run_engine/core/performance.py` (functional change: both `return self.stats` statements, lines 9 and 34); `run_engine/core/canonical_state.py` (verification only, `update_performance_metrics` confirmed No-Change beyond IU-001's own `get()` change); `run_engine/core/canonical_enforcer.py` (verification only, `apply_performance_metrics` confirmed No-Change).

Dependencies: IU-001 (this IU's own verification of `apply_performance_metrics`'s own read-back behaviour depends on `get()` already returning a shallow copy).

Voraussetzungen: IU-001 completed.

Runtime Contracts: IF-004, IF-005, IF-006, IF-007, IF-010.

Acceptance Criteria: **P3-02-SPEC-AC-006.** `PerformanceEngine.update()`'s own returned value is, at every nesting level, a distinct object from `self.stats` on every call, at both its `RUNTIME_FAILURE_EVENT` short-circuit and its normal return path. **P3-02-SPEC-AC-007.** `CanonicalState.state["performance_metrics"]` is object-identity-distinct from `PerformanceEngine.stats` at every tick. **P3-02-SPEC-AC-008.** A Performance Metrics value captured at tick N remains functionally identical, at every nesting level, after further ticks execute. **P3-02-SPEC-AC-009.** `PerformanceEngine.update`'s own accounting formula statements (lines 20, 22-27, 29-32) remain byte-for-byte unchanged from their own pre-Implementation source. **P3-02-SPEC-AC-010.** `python -m compileall run_engine` PASSes.

Testumfang: `compileall`; import test; `PerformanceEngine`-internal-state-vs-output object-identity test (both branches: `RUNTIME_FAILURE_EVENT` short-circuit and normal path); `CanonicalState.performance_metrics` object-identity test (against `self.stats`); `RunLoop`'s own tick-result `"performance"` field object-identity test; multi-tick retained-Performance-Metrics-snapshot stability test across a scripted BUY/HOLD/SELL sequence; direct numeric-value comparison confirming `'pnl'`/`'trades'`/`'winrate'` computation unchanged from pre-Implementation behaviour for an identical input sequence; confirmation that TD-004 remains unaddressed (no lifecycle-outcome-based accounting introduced, `performance.py`'s own decision-keying logic unchanged).

No-Change-Grenzen: no change to `PerformanceEngine`'s own accounting formulas (lines 11-32 apart from the two `return` statements); no change to `CanonicalState.update_performance_metrics()` or `CanonicalEnforcer.apply_performance_metrics()`; no new Performance Metric; no lifecycle-outcome-based accounting.

---

**IU-003 - Risk Publication Return Contract.**

Ziel: realize IF-011's own `apply_risk` correction and IF-016's own incorporation of that correction into the Risk Information Flow.

Betroffene Komponenten: `CanonicalEnforcer` (functional change).

Betroffene Dateien: `run_engine/core/canonical_enforcer.py` (functional change: both `return self.cs.get()` statements in `apply_risk`, lines 50 and 53).

Dependencies: none upstream within this Specification beyond IU-001 (shared file, sequential drafting convenience only, not a functional dependency, since `apply_risk`'s own correction does not itself depend on `get()`'s own new copy behaviour).

Voraussetzungen: repository state unchanged from Section 5's own verification.

Runtime Contracts: IF-011, IF-016.

Acceptance Criteria: **P3-02-SPEC-AC-011.** `apply_risk`'s own return value contains exactly the three Risk Metrics (`drawdown`, `drawdown_ratio`, `risk_allocation_factor`) `update_risk` itself just wrote, at both the `None`-guard branch and the normal-write branch. **P3-02-SPEC-AC-012.** No unpublished input key (`equity`, `peak_equity`) appears in `apply_risk`'s own return value. **P3-02-SPEC-AC-013.** `RiskEngine.check()`'s own formula remains byte-for-byte unchanged. **P3-02-SPEC-AC-014.** `python -m compileall run_engine` PASSes.

Testumfang: `compileall`; import test; direct `apply_risk()` test with an input dict containing additional, non-canonical keys (confirming they do not leak into the return value); return-value-versus-`CanonicalState`-risk-subset functional-identity comparison; P2-04 regression re-run confirming `RiskEngine.check()`'s own formula and every already-certified Risk Ownership contract remains functionally identical.

No-Change-Grenzen: no change to `RiskEngine.check()`'s own formula; no change to `CanonicalState.update_risk()`'s own write behaviour (still exactly three keys written); no change to which keys `apply_risk` writes, only to what it returns.

---

**IU-004 - Consumer, Event, History and Compatibility Verification.**

Ziel: independently verify, with no runtime code change, Rule OM-004 (Consumer Read-Only Discipline, IF-009), Runtime Event Semantic Stability (IF-012), Lifecycle History Immutability (IF-013), Position/Financial/Risk Compatibility (IF-014, IF-015, IF-016), P3-01 Ordering (not reopened), Cross-Unit Boundaries (AD-020), and Residual-Risk Disposition (RR-001 closed, RR-002 and the `PositionEngine` Residual Risk remain open and documented).

Betroffene Komponenten: every active runtime component, verification only.

Betroffene Dateien: none requiring modification; all fourteen active files subject to verification-only re-trace and regression re-run.

Dependencies: IU-001, IU-002, IU-003 (this IU's own compatibility and regression verification is performed after the three file-touching IUs are implemented, confirming they introduced no unintended side effect).

Voraussetzungen: IU-001, IU-002, IU-003 completed.

Runtime Contracts: IF-009, IF-012, IF-013, IF-014, IF-015, IF-016, IF-017, IF-018, IF-019, IF-020, IF-021.

Acceptance Criteria: **P3-02-SPEC-AC-015.** A repeatable, independent procedure confirms no Primary Consumer mutates the object it consumes, for every consumer named in the Runtime Ownership Matrix. **P3-02-SPEC-AC-016.** Every `LifecycleEvent.event_type` originates from exactly one call site, and the dataclass remains frozen. **P3-02-SPEC-AC-017.** `CanonicalState`'s own schema contains no lifecycle-history field. **P3-02-SPEC-AC-018.** Full P2-02A/P2-03/P2-04/P3-01 regression re-run produces functionally identical results for every already-certified field. **P3-02-SPEC-AC-019.** A dual-instance stage-boundary replay (re-using the P3-01 Final Certification's own established methodology) produces functionally identical results across two independent `RunLoop` instances, after IU-001 through IU-003 are implemented. **P3-02-SPEC-AC-020.** A repository-wide, AST-based import-closure check finds no dormant file imported by the active path. **P3-02-SPEC-AC-021.** A simulated unhandled exception, injected at multiple points within `RunLoop.step()`, produces no Tick-Complete result and no artificial `RUNTIME_FAILURE_EVENT` in every case, both before and after IU-001 through IU-003. **P3-02-SPEC-AC-022.** RR-001 is confirmed closed (no retained single-instance reference observes a stale value after IU-001/IU-002); RR-002 and the `PositionEngine` Residual Risk remain confirmed open, documented, and unresolved (not silently presented as resolved), consistent with AD-020.

Testumfang: Consumer-input-mutation tests (before/after field comparison per consumer); Producer-fresh-construction verification (Position, Strategy Selection, Execution Decision, Execution Event, confirming VCF-001 still holds after IU-001 through IU-003); Runtime-Event-mutation test (attempt to mutate a `LifecycleEvent`, confirm `FrozenInstanceError` or equivalent); Lifecycle-History-immutability test; Position-Flow, Financial-Flow, Risk-Flow regression tests; P3-01 stage-ordering regression re-trace; deterministic dual-instance replay; repository-wide alternative-active-information-path search; Failed-Tick verification (simulated exception injection at multiple points, confirming no Tick-Complete result, no artificial `RUNTIME_FAILURE_EVENT`, already-durable internal state unaffected, engine continues normally on the next tick); explicit re-confirmation that the `PositionEngine` Partial-Mutation Residual Risk remains reproducible only via artificial fault injection, remains transient/self-healing, and is not newly resolved or newly worsened by IU-001 through IU-003.

No-Change-Grenzen: no runtime file is modified by this Implementation Unit under any circumstance; if repository evidence during IU-004's own execution reveals any deviation from what IU-001 through IU-003 specify, that deviation is reported as a finding, not silently corrected within IU-004's own scope.

## 27. File-by-File Change Plan

| File | Change Required | Justification | Functional Scope | No-Change Boundary |
|---|---|---|---|---|
| `run_engine/main.py` | No | AD-016 ratifies `main.py`'s own existing exception-handling pattern as sufficient; no new responsibility assigned. | n/a | Entire file unchanged. |
| `run_engine/core/loop.py` | No | Exhaustively traced (Section 5): all six `get()` call sites already behave correctly once `get()` itself changes; no line requires edit. | n/a | Entire file unchanged, including all six `get()` call sites (`lines 47,68,69,70,90,100`), stage order, and every other line. |
| `run_engine/core/state.py` | No | `StateEngine`'s own computation is untouched by any Architecture Decision; not a Producer of any object this Specification's Contracts govern beyond its own already-fresh return value. | n/a | Entire file unchanged. |
| `run_engine/core/regime.py` | No | `RegimeClassifier`'s own Computational Authority role and cross-tick instance state are unaffected; Market Regime remains a scalar, structurally immune to aliasing. | n/a | Entire file unchanged. |
| `run_engine/core/strategy.py` | No | Already fully conformant with IF-008 (Verified Conformant Finding VCF-001); fresh dict construction on every call, re-confirmed Section 5. | n/a | Entire file unchanged. |
| `run_engine/core/decision.py` | No | Confirmed inactive (AD-019); not reclassified by this Specification. | n/a | Entire file unchanged. |
| `run_engine/core/execution/executor.py` | No | Already fully conformant with IF-008 (VCF-001); fresh dict construction on every call, re-confirmed Section 5. | n/a | Entire file unchanged. |
| `run_engine/core/trade_lifecycle.py` | No | Already fully conformant with IF-012/IF-013; `LifecycleEvent` frozen, `current_position()` already returns a fresh dict, re-confirmed Section 5. | n/a | Entire file unchanged. |
| `run_engine/core/position.py` | No | Already fully conformant with IF-008/IF-014 (VCF-001); `snapshot()` already returns a fresh dict, re-confirmed Section 5. CAP-019's own private-state finding is not reopened by this Specification. | n/a | Entire file unchanged, including `update_post_trade`'s own six-attribute sequential mutation pattern. |
| `run_engine/core/pnl.py` | No | Every value in this flow is a scalar, structurally immune to aliasing (VCF-002); IF-015 requires no change. | n/a | Entire file unchanged. |
| `run_engine/core/risk.py` | No | `RiskEngine.check()`'s own formula is unaffected by IF-016; the sole change within the Risk flow's own scope is `apply_risk`'s own return value, in `canonical_enforcer.py`, not `risk.py`. | n/a | Entire file unchanged, including the formula at lines 65-94. |
| `run_engine/core/performance.py` | **Yes** | IF-004/IF-010 require `PerformanceEngine.update()`'s own returned value to be Structurally Independent from `self.stats` at every nesting level. | Both `return self.stats` statements (lines 9 and 34) change to return a structurally independent value with the identical key structure and identical numeric values; the accumulation logic (lines 11-32) and the `self.stats` accumulator itself are unchanged. | No change to the accounting formulas; no new Performance Metric; no lifecycle-outcome-based accounting; `__init__` unchanged. |
| `run_engine/core/canonical_state.py` | **Yes** | IF-001 requires `get()` to return a shallow copy rather than `self.state` directly. | `get()` (lines 107-109) changes to construct and return a new top-level `dict` from `self.state`'s own current key-value pairs, rather than returning `self.state` itself. | No change to the schema (`__init__`, lines 12-51), to any `update_*` method's own write behaviour, or to `reset()`. `update_performance_metrics()` requires no change (IF-005). |
| `run_engine/core/canonical_enforcer.py` | **Yes** | IF-011 requires `apply_risk`'s own return value corrected to the uniform single-value-or-scoped-subset contract. | Both `return self.cs.get()` statements in `apply_risk` (lines 50 and 53) change to return only the published Risk Metrics. `apply_performance_metrics` (lines 71-77) and every other `apply_*` method require no change. | No change to `apply_risk`'s own write behaviour (`self.cs.update_risk(risk)` unchanged); no change to which keys `update_risk` writes; no change to any of the other ten `apply_*` methods. |

## 28. No-Change Inventory

No runtime code change is required for the following ten files the governing task's own instruction specifically names, each justification independently derived, not merely asserted:

**`run_engine/main.py`** - AD-016 ratifies its own existing `try`/`except Exception`/continue pattern as architecturally sufficient; no new responsibility is assigned by this Specification.

**`run_engine/core/state.py`** - `StateEngine`'s own computation is untouched by any Architecture Decision in this unit's own scope; it is not itself a Producer subject to IF-008 beyond its own already-conformant, already-fresh return value.

**`run_engine/core/regime.py`** - `RegimeClassifier`'s own Computational Authority role is unchanged; Market Regime remains a scalar (IF-015's own scalar-immunity reasoning applies identically here).

**`run_engine/core/strategy.py`** - Already fully conformant with IF-008 (VCF-001), re-confirmed by direct source re-reading this Specification's own Section 5.

**`run_engine/core/decision.py`** - confirmed inactive; AD-019 ratifies its continued exclusion from the active path; not reclassified.

**`run_engine/core/execution/executor.py`** - Already fully conformant with IF-008 (VCF-001), re-confirmed.

**`run_engine/core/trade_lifecycle.py`** - Already fully conformant with IF-012/IF-013, re-confirmed; `RUNTIME_FAILURE_EVENT` generation remains scoped exclusively to lifecycle-transition rejection.

**`run_engine/core/position.py`** - Already fully conformant with IF-008/IF-014, re-confirmed; CAP-019's own private-state finding remains, correctly, unreopened.

**`run_engine/core/pnl.py`** - Financial values remain scalar, structurally immune to aliasing (VCF-002).

**`run_engine/core/risk.py`** - `RiskEngine.check()`'s own formula is unaffected; the Risk flow's sole change (`apply_risk`'s own return value) is located in `canonical_enforcer.py`, not here.

**`run_engine/core/loop.py`** (additionally confirmed, per the governing task's own explicit conditional instruction) - classified No-Change only after the exhaustive, repository-grounded, line-by-line trace of all six of its own `get()` call sites performed in Section 5, confirming each one already behaves correctly once `CanonicalState.get()` itself changes, with no assumption of unchanged object identity across separate calls anywhere in the file.

## 29. Acceptance Criteria

Twenty-two Implementation-Unit-level Specification Acceptance Criteria are defined (`P3-02-SPEC-AC-001` through `P3-02-SPEC-AC-022`, Section 26). In addition, the following global criteria apply across all four Implementation Units, restating the governing task's own explicit minimum list:

**P3-02-SPEC-AC-G1.** `CanonicalState.get()` returns no live top-level alias of the internal `CanonicalState` container.
**P3-02-SPEC-AC-G2.** External mutation of a value `get()` returns does not alter `CanonicalState`'s own held state.
**P3-02-SPEC-AC-G3.** A later tick does not alter an earlier, already-returned Tick-Complete snapshot.
**P3-02-SPEC-AC-G4.** Performance Metrics of an earlier snapshot remain unchanged after later ticks execute.
**P3-02-SPEC-AC-G5.** `PerformanceEngine.stats` is not object-identical with the published Performance Metrics value, at any tick.
**P3-02-SPEC-AC-G6.** `CanonicalState.performance_metrics` is not object-identical with the continuing-to-mutate Producer state.
**P3-02-SPEC-AC-G7.** `apply_risk`'s own return value contains only published Risk Metrics.
**P3-02-SPEC-AC-G8.** No P3-01 stage order is altered.
**P3-02-SPEC-AC-G9.** No `CanonicalState` schema key is added, removed, or renamed.
**P3-02-SPEC-AC-G10.** No Authoritative Owner or Computational Authority changes for any object.
**P3-02-SPEC-AC-G11.** No Performance Metric methodology change occurs.
**P3-02-SPEC-AC-G12.** No Position, PnL, or Risk formula changes.
**P3-02-SPEC-AC-G13.** No new Failure, rollback, or Recovery semantics are introduced.
**P3-02-SPEC-AC-G14.** All Consumer-mutation tests PASS.
**P3-02-SPEC-AC-G15.** Runtime Events remain semantically stable (frozen, single call site per type).
**P3-02-SPEC-AC-G16.** Lifecycle History remains authoritative and non-duplicated.
**P3-02-SPEC-AC-G17.** Deterministic replay remains functionally identical across independent instances.
**P3-02-SPEC-AC-G18.** Full P2-02A/P2-03/P2-04/P3-01 regression PASSes.

## 30. Runtime Verification Plan

This section states the detailed verification procedure IU-001 through IU-004 jointly carry out, organized by governing task's own per-IU minimum checklist.

**IU-001.** `compileall`; import test; `CanonicalState.get()` object-identity test across two calls; external-mutation-of-returned-value test; multi-tick retained-reference stability test spanning at least three further ticks; HOLD-tick snapshot-stability test; `CanonicalState` schema-unchanged test (fifteen keys, same names).

**IU-002.** `PerformanceEngine`-internal-state-vs-output identity test (both code paths); `CanonicalState.performance_metrics` identity test; `RunLoop`'s own tick-result `"performance"` field identity test; multi-tick retained Performance-Metrics-snapshot stability test across a scripted BUY, HOLD, and SELL sequence; direct numeric comparison confirming `'pnl'`/`'trades'`/`'winrate'` computation values are unchanged from pre-Implementation behaviour for an identical input sequence; explicit confirmation TD-004 remains open and unadvanced.

**IU-003.** `apply_risk()` test with an input dict carrying additional, non-canonical keys, confirming they are absent from the return value; return-value-versus-`CanonicalState`-Risk-Metrics-subset functional-identity comparison; `RiskEngine.check()`'s own formula source-line comparison (byte-for-byte unchanged); full P2-04 regression re-run.

**IU-004.** Consumer-input-mutation tests for every named Primary Consumer; Producer-fresh-construction re-verification for Position, Strategy Selection, Execution Decision, Execution Event; Runtime-Event mutation-attempt test; Lifecycle-History immutability re-verification; Position/Financial/Risk Flow regression tests; P3-01 stage-ordering regression re-trace; dual-instance deterministic replay; repository-wide alternative-active-information-path search; Failed-Tick verification with exception injection at multiple points within `RunLoop.step()`; explicit re-confirmation of RR-001's own closure and RR-002's/the `PositionEngine` Residual Risk's own continued, documented, unresolved status.

## 31. Compatibility Verification Plan

**P2-02A.** Full regression re-run of the P2-02A-certified Position/Exposure scenarios; confirm `position.py` remains byte-for-byte unchanged from its own pre-Implementation state.

**P2-03.** Full regression re-run of the P2-03-certified Financial Ownership scenarios; confirm `pnl.py` remains byte-for-byte unchanged.

**P2-04.** Full regression re-run of the P2-04-certified Risk Ownership scenarios; confirm `risk.py` remains byte-for-byte unchanged; confirm `RiskEngine.check()`'s own formula source lines are byte-for-byte unchanged.

**P3-01.** Full regression re-trace of the twelve-stage ordering, Tick-Complete Publication semantics (now eleven `apply_*` calls, unchanged in count by this Specification's own scope), and Failed-Tick semantics; confirm `loop.py` remains byte-for-byte unchanged (Section 27).

**Runtime Ownership Matrix.** Confirm every row this Specification's own scope touches (Position, Market Regime not reopened, Risk Metrics, Performance Metrics) retains its own unchanged Authoritative Owner and Computational Authority; only the Writer-on-Behalf-Of mechanism's own return-value shape changes for Risk Metrics (IF-011), and only the Producer's own publication object-identity changes for Performance Metrics (IF-004).

**AI/AC (Baseline and P3-01/P3-02).** Re-check all fifteen P3-02-AI-series invariants (Architecture Section 29) against the post-Implementation runtime; re-confirm no Baseline-level or P3-01-level invariant is contradicted.

**TD (Technical Debt).** Confirm TD-004 and TD-007 remain unaddressed and unreopened; confirm `performance.py`'s own decision-keyed accounting basis is unchanged.

## 32. Residual-Risk Verification

**RR-001** (single-instance retained-reference risk): confirmed fully closed as a consequence of IU-001 and IU-002 - IU-004's own multi-tick retained-reference tests (Section 26, `P3-02-SPEC-AC-022`) confirm no field of a retained Tick-Complete result changes value after further ticks execute, for both the top-level container and Performance Metrics specifically.

**RR-002** (Post-Exception Financial/Lifecycle Divergence, the original `TradeLifecycleEngine`-versus-`CanonicalState` instance): confirmed to remain open, non-blocking, and documented; not resolved, not silently presented as resolved, by any Implementation Unit in this Specification. No IU-004 test attempts to close it.

**`PositionEngine` Partial-Mutation Residual Risk** (formerly FG-005, carried as CAP-019, COMPLETE, Residual-Risk Capability): confirmed to remain open, documented, artificial-injection-only, transient, and self-healing; IU-004's own verification explicitly re-confirms these four bounding properties still hold after IU-001 through IU-003 are implemented, without introducing any rollback, reset, or transaction mechanism.

## 33. Traceability

### 33.1 Functional Requirement Traceability (Individually Enumerated)

| FR | Governing Contract(s) |
|---|---|
| FR-001 | IF-001 |
| FR-002 | IF-018 |
| FR-003 | IF-002, IF-003, IF-019 |
| FR-004 | IF-004, IF-005, IF-006, IF-007, IF-008, IF-010 |
| FR-005 | IF-008, IF-009 |
| FR-006 | IF-011 |
| FR-007 | IF-011 |
| FR-008 | IF-014, IF-015, IF-016 (jointly) |
| FR-009 | IF-013, IF-015, IF-016 (jointly) |
| FR-010 | IF-012 |
| FR-011 | IF-013 |
| FR-012 | IF-014 |
| FR-013 | IF-017 (ratified, not reopened) |
| FR-014 | IF-015 |
| FR-015 | IF-016 |
| FR-016 | IF-007 |
| FR-017 | IF-009 |
| FR-018 | IF-017 |
| FR-019 | IF-020 |
| FR-020 | IF-021 |
| FR-021 | IF-001 through IF-021, jointly (traceability itself) |
| FR-022 | IF-001, IF-002, IF-004, IF-008 (jointly) |
| FR-023 | Section 3 (Non-Goals), Section 27 (No-Change for `loop.py`) |
| FR-024 | IF-007 |

All twenty-four Functional Requirements are governed by at least one Runtime Contract or explicit Specification-level provision.

### 33.2 SDA Dependency Traceability (Individually Enumerated)

| DEP | Governing Contract(s) |
|---|---|
| DEP-001 | IF-001, IF-002, IF-003 |
| DEP-002 | IF-001, IF-018 |
| DEP-003 | IF-001, IF-008, IF-009 |
| DEP-004 | IF-001, IF-009 |
| DEP-005 | IF-001, IF-002 |
| DEP-006 | IF-018, IF-016 |
| DEP-007 | IF-002, IF-003 |
| DEP-008 | IF-004, IF-005, IF-008 |
| DEP-009 | IF-002, IF-004, IF-010 |
| DEP-010 | IF-008, IF-009 |
| DEP-011 | IF-008, IF-014 |
| DEP-012 | IF-008, IF-015 |
| DEP-013 | IF-008, IF-016 |
| DEP-014 | IF-008, IF-007 |
| DEP-015 | IF-011 |
| DEP-016 | IF-014, IF-011 |
| DEP-017 | IF-015, IF-011 |
| DEP-018 | IF-016, IF-011 |
| DEP-019 | IF-006, IF-007, IF-011 |
| DEP-020 | IF-014, IF-015, IF-016 |
| DEP-021 | IF-013, IF-015, IF-016 |
| DEP-022 | Section 3 (semantic-continuity/reconstruction, ratified) |
| DEP-023 | IF-012, IF-013 |
| DEP-024 | IF-012, IF-017 |
| DEP-025 | IF-013, IF-014 |
| DEP-026 | IF-013, IF-015 |
| DEP-027 | IF-013, IF-020 |
| DEP-028 | IF-014, IF-015 |
| DEP-029 | IF-014, IF-016 |
| DEP-030 | IF-014 (ratified, not reopened) |
| DEP-031 | IF-014, IF-020 |
| DEP-032 | IF-017 (ratified, not reopened) |
| DEP-033 | IF-015, IF-016 |
| DEP-034 | IF-015, IF-020 |
| DEP-035 | IF-005, IF-006, IF-007 |
| DEP-036 | Section 33 (aggregate) |
| DEP-037 | IF-017 (ratified, not reopened) |
| DEP-038 | IF-014 (P2-02A not reopened) |
| DEP-039 | IF-015 (P2-03 not reopened) |
| DEP-040 | IF-016 (P2-04 not reopened) |
| DEP-041 | IF-013 (ADR-003 not reopened) |
| DEP-042 | IF-018 (P3-01 not reopened) |
| DEP-043 | IF-011 (P3-01 not reopened) |
| DEP-044 | IF-012 (Baseline not reopened) |
| DEP-045 | IF-017 (P3-01-AD-004 not reopened) |
| DEP-046 | IF-017 (P3-01-AD-004/AD-006 not reopened) |
| DEP-047 | IF-020 (P3-01-AD-005 not reopened) |
| DEP-048 | IF-021 (P3-01-AD-009 not reopened) |
| DEP-049 | IF-002 (P3-01-AD-007/EO-013 not reopened) |
| DEP-050 | IF-004, IF-007 (TD-004/P3-03 not reopened) |
| DEP-051 | Section 3 (P3-01 blanket, not reopened) |
| DEP-052 | Section 3 (P3-03 blanket, not reopened) |

All fifty-two Dependency records are governed by at least one Runtime Contract or explicit Specification-level provision.

### 33.3 CGA Capability Traceability (Individually Enumerated)

| CAP | Governing Contract(s) |
|---|---|
| CAP-001 | IF-001 |
| CAP-002 | IF-018 |
| CAP-003 | IF-002 |
| CAP-004 | IF-003 |
| CAP-005 | IF-008 |
| CAP-006 | IF-004, IF-005, IF-006, IF-010 |
| CAP-007 | IF-008, IF-009 |
| CAP-008 | IF-009 |
| CAP-009 | IF-011 |
| CAP-010 | IF-011 |
| CAP-011 | IF-012 |
| CAP-012 | IF-013 |
| CAP-013 | IF-014 |
| CAP-014 | IF-015 |
| CAP-015 | IF-016 |
| CAP-016 | IF-007 |
| CAP-017 | IF-013, IF-015, IF-016 |
| CAP-018 | Section 3 (aggregate, closed as consequence of CAP-001, CAP-004, CAP-006, CAP-007, CAP-008) |
| CAP-019 | IF-017 (ratified, not reopened) |
| CAP-020 | IF-001, IF-002, IF-004, IF-008 |
| CAP-021 | IF-017 |
| CAP-022 | IF-020 |
| CAP-023 | IF-021 |
| CAP-024 | Section 33 (aggregate) |
| CAP-025 | IF-014, IF-015, IF-016 |
| CAP-026 | Section 3 (P3-01 boundary) |
| CAP-027 | Section 3 (P3-03 boundary) |

All twenty-seven Capabilities are governed by at least one Runtime Contract or explicit Specification-level provision.

### 33.4 Architecture Decision Traceability

Architecture Decisions AD-001 through AD-020 are each individually realized by at least one Runtime Contract, individually cited throughout Sections 9-25 and Section 26; no further table is required beyond the individual citations already present in those sections.

### 33.5 Architecture Invariant Traceability (Individually Enumerated)

| Invariant | Governing Contract(s) |
|---|---|
| P3-02-AI-001 (Stable Tick-Complete Snapshot) | IF-002 |
| P3-02-AI-002 (No Cross-Tick Snapshot Mutation) | IF-001, IF-003, IF-004 |
| P3-02-AI-003 (No External Canonical-State Mutation) | IF-011, IF-018 |
| P3-02-AI-004 (No Consumer Input Mutation) | IF-009 |
| P3-02-AI-005 (No Producer Mutation of Published Snapshot) | IF-008 |
| P3-02-AI-006 (No Unauthorized Shared Mutable Reference) | IF-001, IF-004, IF-008, IF-010 |
| P3-02-AI-007 (Canonical Writer Discipline) | IF-011 |
| P3-02-AI-008 (One Semantic Source per Runtime Object) | IF-014, IF-015, IF-016 |
| P3-02-AI-009 (Runtime Event Semantic Stability) | IF-012 |
| P3-02-AI-010 (Lifecycle History Immutability) | IF-013 |
| P3-02-AI-011 (Operational and Historical Separation) | IF-013 |
| P3-02-AI-012 (Deterministic Information Flow) | IF-001, IF-004, IF-008 (jointly; re-verified by IU-004's own dual-instance replay) |
| P3-02-AI-013 (No Downstream Reconstruction) | IF-013, IF-015, IF-016 |
| P3-02-AI-014 (No Alternative Active Information Path) | IF-021 |
| P3-02-AI-015 (Certified Ownership Compatibility) | IF-014, IF-015, IF-016, IF-017, IF-020 |

All fifteen Architecture Invariants are individually re-checked by IU-004's own Compatibility Verification (Section 31) and, where applicable, by IU-001/IU-002/IU-003's own Acceptance Criteria directly.

### 33.6 Remaining Traceability

| Category | Coverage |
|---|---|
| Runtime Ownership Matrix | Re-checked by IU-004 (Section 31); every row this Specification's own scope touches confirmed unchanged in ownership. |
| ADR-001 through ADR-012 | Governing every Runtime Contract by inheritance from the Architecture's own Section 4. |
| AC-001 through AC-012 | Re-checked by IU-004 (Section 31), inherited from the Architecture's own Baseline-level citations. |
| P2-02A, P2-03, P2-04 | Compatibility re-verified by IU-004 (Section 26, Section 31); no contract reopened. |
| P3-01 | Compatibility re-verified by IU-004; `loop.py` confirmed byte-for-byte unchanged (Section 27); stage ordering not reopened. |
| TD-004, TD-007 | Confirmed unaddressed by IU-002/IU-004 (Section 26, Section 31). |
| RR-001, RR-002, PositionEngine Partial-Mutation Residual Risk | Disposition confirmed by Section 32. |

## 34. Non-Goals

Consistent with Section 3 and the governing task's own explicit prohibition list: no new architecture, no new scientific analysis, no new capability assessment, no new Functional Requirement, Dependency, Architecture Decision, or Architecture Invariant is introduced anywhere in this document; no concrete Python signature, complete file diff, or test implementation as a fixed command is specified; no P3-01 or P3-03 work is performed or anticipated beyond IF-017's/IF-020's/IF-021's own explicit non-resolution statements; no Persistence, Recovery, or Operator Lifecycle Control mechanism is designed; no rollback, reset, or transaction mechanism is designed; no Position, Financial, or Risk formula or ownership is altered; no Performance Metric methodology is redesigned.

## 35. Internal Consistency Review

**Terminology consistency.** "Computational Authority," "Authoritative Owner," "Writer-on-Behalf-Of," "Publication," "Storage," and "Consumption" are used exactly as defined in the Architecture Baseline and inherited unchanged from the Architecture document throughout this Specification; every Runtime Contract's own "Object Identity," "Producer," "Publication," and "Consumer" fields keep the concepts explicitly separate. "Functionally identical" is used exclusively for runtime-object, tick-result, and `CanonicalState`-snapshot comparisons throughout (Sections 9-26, Section 31). "Byte-identical"/"byte-for-byte" is used exclusively for genuine source-line-level comparisons of unchanged formula statements or unchanged files (Sections 22, 27, 28, 30, 31), consistent with the project's own strict reservation of that term; every other occurrence of either term in this document, including this sentence's own meta-discussion, is citation or definitional restatement, not an additional comparison claim.

**Specification consistency.** Every Runtime Contract in Sections 9-25 traces to exactly one or more governing Architecture Decisions; no contract introduces a requirement absent from the Architecture's own Section 28. Every Implementation Unit (Section 26) is either file-touching with a narrowly-scoped functional change (IU-001, IU-002, IU-003) or explicitly Verification-Only (IU-004), consistent with the Architecture's own Implementation Impact Inventory (Architecture Section 36).

**Architecture consistency.** No decision in this document contradicts or extends AD-001 through AD-020; every Runtime Contract restates, at the implementation-directive level, a decision the Architecture already made.

**Ownership consistency.** No Runtime Contract or Implementation Unit assigns a new Authoritative Owner or Computational Authority; IF-011 changes only Risk Metrics' own Writer-on-Behalf-Of return-value shape; IF-004 changes only Performance Metrics' own Producer-side object-identity discipline; neither changes ownership.

**Runtime consistency.** The File-by-File Change Plan (Section 27) and No-Change Inventory (Section 28) jointly account for all fourteen active runtime files; exactly three (`canonical_state.py`, `performance.py`, `canonical_enforcer.py`) require a functional change, and `loop.py`'s own No-Change classification rests on an exhaustive, repository-grounded, six-call-site trace, not an assumption.

**Traceability completeness.** Section 33 confirms all twenty-four Functional Requirements, all fifty-two Dependencies, all twenty-seven Capabilities, all twenty Architecture Decisions, and all fifteen Architecture Invariants are referenced by at least one Runtime Contract, Implementation Unit, or explicit Specification-level provision.

**No fabricated contract.** Every one of the twenty-one Runtime Contracts traces to a specific Architecture Decision's own Motivation, Decision, and Acceptance Criteria fields; no contract in this document addresses a concern absent from the Architecture.

Status: Internal Consistency Review PASS.

## 36. Specification Readiness Decision

Every capability the Architecture left to be translated into an implementable contract (CAP-001, CAP-004, CAP-006, CAP-010, and the general-convention closure of CAP-005/CAP-007/CAP-008) now has a corresponding Runtime Contract and Implementation Unit. Every Architecture Decision (AD-001 through AD-020) is realized by at least one Runtime Contract and accounted for in the Implementation Impact reasoning (Section 6). The File-by-File Change Plan (Section 27) and No-Change Inventory (Section 28) jointly, exhaustively account for all fourteen active runtime files, with `loop.py`'s own No-Change status independently, repository-grounded confirmed rather than assumed. No already-certified P2-02A, P2-03, P2-04, or P3-01 contract is reopened. Both Post-Exception Divergence instances (RR-002, and the `PositionEngine`-specific instance) remain explicitly, honestly documented as open, non-blocking Residual Risks (Section 32).

**Specification Readiness: READY.** This document is sufficient to proceed to the P3-02 Implementation. No further specification work is required before that step.

## 37. Independent Self Verification

Every claim in Sections 5 through 33 was independently re-derived during this Specification's own drafting: `canonical_state.py`, `performance.py`, `canonical_enforcer.py`, `loop.py`, `position.py`, `risk.py`, and `trade_lifecycle.py` were each re-read in full (Section 5), not inherited from the Architecture's own text without re-checking. `loop.py`'s own six `get()` call sites were individually, exhaustively traced line by line to confirm the No-Change classification is repository-grounded, not merely asserted from the Architecture's own general reasoning - the specific instruction the governing task raised. The repository-wide keyword search (Section 5) reproduced exactly the same call-site facts the FRA, SDA, CGA, and Architecture already established, confirming no new fact emerged since the Architecture's own drafting.

Cross-document consistency check: every AD-001 through AD-020 citation in this document (Sections 9-26) was compared against the current, final text of `P3_02_INFORMATION_FLOW_VALIDATION_ARCHITECTURE_V1_2026-07-13.md`, including that document's own post-review corrections (the two German-fragment/umlaut fixes, the "byte-for-byte" precision correction in AD-015), and found consistent - this document was drafted after, and reflects, the Architecture's own fully revised state.

Result: no error was found during this document's own closing review requiring correction before delivery. All findings from this document's own internal reviews (Section 35) are PASS.

Status: Independent Self Verification PASS.

No commit was made. No runtime file was changed. No push was made. This document is ready to be provided as `P3_02_INFORMATION_FLOW_VALIDATION_SPECIFICATION_V1_2026-07-13.md`.
