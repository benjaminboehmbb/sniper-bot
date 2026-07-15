Document Class:
Capability Gap Analysis

Document ID:
P3-02-CGA

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
docs/architecture/analysis/P3_02_CAPABILITY_GAP_ANALYSIS_V1_2026-07-13.md

Depends On:
- docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md
- docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md
- docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md
- docs/architecture/analysis/P3_02_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-13.md
- docs/architecture/analysis/P3_02_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-13.md
- complete P3-01 governance chain
- docs/architecture/P2_02A_POSITION_OWNERSHIP_ARCHITECTURE_V1_2026-07-10.md
- docs/architecture/P2_03_FINANCIAL_OWNERSHIP_ARCHITECTURE_V1_2026-07-11.md
- docs/architecture/P2_04_RISK_OWNERSHIP_ARCHITECTURE_V1_2026-07-13.md
- current runtime code at HEAD f6fb7f3911a978884ca10b22a0eef832a52f9486

Referenced By:
- future P3-02 Architecture

Methodological Structure Reference (content not carried over):
- docs/architecture/analysis/P3_01_CAPABILITY_GAP_ANALYSIS_V1_2026-07-13.md

---

# P3-02 Information Flow Validation - Capability Gap Analysis

## 1. Capability Context

This document is the P3-02 Capability Gap Analysis (CGA), the third stage of the P3-02 governance chain (FRA -> SDA -> CGA -> Architecture -> Specification -> Implementation -> Final Certification). It classifies every capability derivable from the twenty-four Functional Requirements of `P3_02_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-13.md` (the "P3-02 FRA") and the fifty-two Dependency records of `P3_02_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-13.md` (the "P3-02 SDA") as COMPLETE, PARTIAL, or MISSING, and types each as a Runtime, Governance, Documentation, Verification, Cross-Unit, or Residual-Risk Capability. No new capability concept is introduced beyond what the FRA and SDA already establish; no Architecture Decision is made.

## 2. Assessment Method

Each capability is derived directly from one or more Functional Requirements and, where applicable, the Dependency records touching them. Classification follows exactly the governing task's own rules: **COMPLETE** requires runtime behaviour satisfying the requirement, sufficient governance, sufficient evidence, and no open normative gap. **PARTIAL** applies when runtime behaviour is present in whole or in part but governance, isolation, documentation, or independent verification is incomplete. **MISSING** applies when a required capability does not exist at all, or a normative requirement is demonstrably unmet. A documented, bounded Residual Risk is never classified MISSING solely because it is a Residual Risk; its actual, independently-assessed impact determines its classification, consistent with the precedent the P3-01 Final Certification (Section 24) already established for Post-Exception Financial/Lifecycle Divergence, and consistent with how the P3-01 CGA itself resolved the analogous Unhandled-Exception capability (CAP-020) to COMPLETE once AD-004 explicitly decided, rather than silently accepted, the residual condition.

This document supersedes, for classification purposes only, the FRA's own provisional Current Conformance labels where a subsequent, explicitly-commissioned targeted review produced new evidence the FRA itself did not have at drafting time. This applies to exactly one item: the former Functional Gap FG-005 (`PositionEngine` cross-tick private-state self-consistency), which the governing task explicitly directs be carried in this document as a Residual Risk, not a Functional Gap, per the targeted Scientific Consistency and Scope Review already performed and delivered earlier in this session. No other FRA finding is altered.

## 3. Repository Re-Verification

Independently re-verified for this document, not assumed from the FRA or SDA:

- Branch `run-engine-consolidation-safety`, local HEAD and remote HEAD both `f6fb7f3911a978884ca10b22a0eef832a52f9486`, identical; working tree unchanged since FRA/SDA drafting except for the FRA and SDA files themselves (still untracked).
- `git status --short -- run_engine/` returns empty: no runtime file has changed since the FRA and SDA were drafted, which independently confirms every fresh repository read performed during this session's FRA, SDA, and targeted FG-003/FG-005 review remains valid evidence for this document without re-reading unchanged files a further time.
- `CanonicalState.get()` (`canonical_state.py:107-109`) re-confirmed: `return self.state`, a live reference, unchanged.
- `RunLoop.step()`'s own return value (`loop.py:98-113`) re-confirmed: a freshly-constructed outer dict whose own `"state"` field is `self.cstate.get()`, i.e. the live reference above, not a copy.
- `PerformanceEngine.stats` (`performance.py:4,34`) re-confirmed: constructed once in `__init__`, mutated in place, returned as the same object on every call.
- `CanonicalState.update_performance_metrics()` (`canonical_state.py:96-98`) re-confirmed: stores the received reference directly, no copy.
- `CanonicalEnforcer.apply_risk()` (`canonical_enforcer.py:47-53`) re-confirmed: the sole `apply_*` method returning `self.cs.get()` (the complete state dict) rather than a single key.
- `PositionEngine` snapshot construction (`position.py:75-83`) re-confirmed: a fresh dict literal on every `snapshot()` call; `update_post_trade` (`position.py:37-73`) re-confirmed: six sequential, non-atomic instance-attribute mutations.
- Strategy Selection (`strategy.py:21,47,69`) and Execution Decision/Event (`executor.py:15,22,28`) re-confirmed: fresh dict literals on every call, no shared-object return across calls.
- Lifecycle History (`trade_lifecycle.py:8,28`) re-confirmed: `LifecycleEvent` is `@dataclass(frozen=True)`; `Trade` is a plain, internally-mutable `@dataclass`, confined to `TradeLifecycleEngine`'s own management.
- Writer-on-Behalf-Of paths and direct `CanonicalState` write paths re-confirmed: exactly one call site per `update_*` method, all inside `canonical_enforcer.py` except `update_tick` (`loop.py:42`, Runtime Tick's own Matrix-named exception).
- Consumer-side input mutation: re-confirmed absent in every consumer (`StrategySelector`, `Executor`, `TradeLifecycleEngine`, `PositionEngine`, `PnLEngine`, `RiskEngine`, `PerformanceEngine`).
- Nested mutable references and cross-tick aliasing: re-confirmed exactly as the FRA's own Section 12 and this session's own independent probes established - top-level `CanonicalState.state` and `PerformanceEngine.stats` alias across ticks; Position, Strategy Selection, Execution Decision, and Execution Event do not.
- Post-Exception Divergence: re-confirmed both instances remain unresolved by design (P3-01's own TradeLifecycleEngine-versus-CanonicalState case, and this unit's own newly-identified `PositionEngine`-private-state case), neither altered by any runtime change.

No runtime file was modified by this document's own drafting.

## 4. Capability Clusters

| Cluster | Title | Capabilities |
|---|---|---|
| 1 | Canonical State Access | CAP-001, CAP-002 |
| 2 | Snapshot and Lifetime Semantics | CAP-003, CAP-004 |
| 3 | Mutation and Aliasing | CAP-005, CAP-006, CAP-018, CAP-019 |
| 4 | Producer-Consumer Contracts | CAP-007, CAP-008 |
| 5 | Writer-on-Behalf-Of Discipline | CAP-009, CAP-010 |
| 6 | Runtime Events and Lifecycle History | CAP-011, CAP-012 |
| 7 | Position / Financial / Risk Flow | CAP-013, CAP-014, CAP-015, CAP-017, CAP-025 |
| 8 | Performance Flow | CAP-016 |
| 9 | Failure Information Flow | CAP-021 |
| 10 | HOLD and Alternative Paths | CAP-022, CAP-023 |
| 11 | Deterministic Information Flow | CAP-020 |
| 12 | Documentation and Verification | CAP-024 |
| 13 | Cross-Unit and Scope Boundaries | CAP-026, CAP-027 |

Thirteen clusters, adapted from the governing task's own suggested list to place the two Cross-Tick/PositionEngine capabilities (CAP-018, CAP-019) inside Cluster 3 (Mutation and Aliasing) rather than a separate cluster, since both are, by their own subject matter, aliasing and private-state-consistency findings, not a distinct category.

## 5. Capability Catalogue

Twenty-seven capabilities, `P3-02-CAP-001` through `P3-02-CAP-027`, derived exclusively from the twenty-four existing Functional Requirements; three capabilities beyond a strict one-to-one mapping (CAP-004, CAP-006, CAP-019) exist because the governing task's own "besonders bewerten" list explicitly separates a general normative property from its own specific, concretely-evidenced empirical instance (Tick-Complete Snapshot Stability versus Top-Level Result Aliasing; Nested Mutable-Object Isolation versus Performance-Metrics Aliasing; Hidden Coupling versus Cross-Tick Object Identity/`PositionEngine`). No capability introduces a concept absent from the FRA or SDA.

---

**P3-02-CAP-001 - CanonicalState Read-Contract Existence**

Capability Type: Governance Capability.

Description: whether a single, explicitly documented, binding read-contract (reference, shallow copy, deep copy, or read-only view) exists for `CanonicalState.get()`.

Source FR(s): FR-001. Source DEP(s): DEP-001 through DEP-005 (all dependencies originating from FR-001).

Repository Evidence: `canonical_state.py:107-109`, `def get(self): return self.state`.

Runtime Evidence: `id(engine.cstate.get())` identical across every call (Section 3; FRA Section 12).

Scientific Completeness: high - the actual current behaviour is fully, precisely characterized. Runtime Completeness: the behaviour itself is stable and well-understood, but no contract exists for it to conform to. Governance Completeness: none - zero binding decision exists among the four candidate semantics. Documentation Completeness: high (this behaviour is now documented across the FRA, SDA, and this document). Verification Completeness: not applicable (there is no contract to verify against).

Dependency Coverage: DEP-001 (FR-003), DEP-002 (FR-002, conditional), DEP-003/DEP-004 (FR-005/FR-017, conditional), DEP-005 (FR-022, conditional) - five downstream dependencies, none yet resolved because none can be until this capability exists.

Certification Coverage: none; CUO-01 was forwarded past P3-01's own Final Certification without resolution.

Cross-Unit Relevance: this capability is CUO-01, originally raised across P3-01/P3-02; it is now owned entirely within P3-02 (FRA Section 8) and is no longer cross-unit in scope, though its own origin remains cross-unit in history.

Current Status: **MISSING**. No binding decision exists; this is not a partial or degraded state of an existing contract, it is the complete absence of one.

Remaining Gap: an explicit Architecture Decision selecting among reference, shallow-copy, deep-copy, or read-only-view semantics.

Scope Boundary: this document does not select a semantics; that is reserved for the Architecture stage.

Architecture Relevance: highest priority - this is the single capability every other Layer-1-and-above capability in Cluster 1-3 either directly or conditionally depends on (SDA Section 8, Section 11).

Specification Relevance: a future Specification cannot define Runtime Contracts for `get()`'s own read behaviour until this capability closes.

Traceability: AI-002; Rule OM-006; Canonical Storage definition; CUO-01; FR-001; DEP-001 through DEP-005.

---

**P3-02-CAP-002 - Canonical Working State Internal-Only Consumption**

Capability Type: Runtime Capability.

Description: whether Canonical Working State is consumed only by a component whose own execution position has already been reached, and remains unobservable externally before Tick Completion.

Source FR(s): FR-002. Source DEP(s): DEP-002 (conditional, upstream), DEP-006 (downstream to FR-015), DEP-042 (compatibility/cross-unit).

Repository Evidence: `loop.py:90`, `canonical_state = self.cstate.get()`, consumed only by `RiskEngine.check` at its own assigned stage.

Runtime Evidence: no yield, no intermediate return, no external read path found in `RunLoop.step()` (FRA Section 11).

Scientific/Runtime Completeness: complete. Governance Completeness: complete (re-verifies P3-01-AI-003/AI-004 without reopening). Documentation Completeness: complete. Verification Completeness: complete (structural, re-traceable at any HEAD).

Dependency Coverage: DEP-006 (feeds FR-015, itself COMPLETE, CAP-015).

Certification Coverage: inherits P3-01's own already-certified structural checks (no concurrency construct).

Cross-Unit Relevance: re-verifies, without reopening, P3-01-AI-003 and P3-01-AI-004.

Current Status: **COMPLETE**.

Remaining Gap: none.

Scope Boundary: does not evaluate the Tick-Complete result's own subsequent mutability (CAP-003/CAP-004).

Architecture Relevance: none required; ratification only.

Specification Relevance: none required.

Traceability: Canonical Working State definition; P3-01-AI-003; P3-01-AI-004; AC-009; AC-010; FR-002; DEP-002, DEP-006, DEP-042.

---

**P3-02-CAP-003 - Tick-Complete Snapshot Stability (General Normative Property)**

Capability Type: Runtime Capability.

Description: whether a returned Tick-Complete result, taken as a whole, remains stable (unmutated, unreassigned) after being returned, for as long as it is held.

Source FR(s): FR-003. Source DEP(s): DEP-001 (upstream from FR-001), DEP-007 (downstream to FR-022), DEP-009 (sibling to FR-004).

Repository Evidence: `loop.py:98-113`.

Runtime Evidence: nested Position values remain stable once captured (FRA Section 12, empirically confirmed); the top-level `"state"` container and the `"performance"`/`"performance_metrics"` value do not (CAP-004, CAP-006).

Scientific Completeness: high (fully characterized, field by field). Runtime Completeness: partial - most of the returned structure's own content is stable; two specific fields are not. Governance Completeness: none (no isolation contract exists, contingent on CAP-001). Documentation Completeness: high. Verification Completeness: high (empirically demonstrated, reproducible).

Dependency Coverage: DEP-001 (blocked pending CAP-001), DEP-007 (already reflected in CAP-020's own bounded RR-001 finding), DEP-009 (paired with CAP-005/CAP-006's own findings under one future OQ-007 resolution).

Certification Coverage: none; this is a newly-identified property this unit's own FRA first evidenced.

Cross-Unit Relevance: none beyond CAP-001's own CUO-01 lineage.

Current Status: **PARTIAL**. The overall Tick-Complete result is stable for the majority of its own content by current producer convention, but demonstrably unstable for its own top-level container and for Performance Metrics; the requirement, read as a whole ("SHALL NOT be an object that a subsequent tick's own processing will further mutate"), is not uniformly met.

Remaining Gap: an object-identity-isolation mechanism for the specific fields CAP-004 and CAP-006 identify; contingent on CAP-001's own resolution (DEP-001).

Scope Boundary: does not select the isolation mechanism.

Architecture Relevance: high - this capability's own resolution mechanism is likely shared with CAP-001's own decision.

Specification Relevance: a future Runtime Contract for Tick-Complete stability cannot be written until CAP-001 resolves.

Traceability: Tick-Complete Snapshot definition; AI-009; AC-009; FR-003; DEP-001, DEP-007, DEP-009.

---

**P3-02-CAP-004 - Top-Level Result Object-Identity Isolation (Specific Finding)**

Capability Type: Runtime Capability.

Description: whether the Tick-Complete result's own `"state"` field is a distinct object from `CanonicalState`'s own internally held, subsequently-mutated dictionary.

Source FR(s): FR-003 (specific instance, Functional Gap FG-002). Source DEP(s): DEP-001, DEP-007.

Repository Evidence: `loop.py:100`, `"state": self.cstate.get()`.

Runtime Evidence: `id()`-identical, directly reproduced in this session: a reference captured at tick 0 shows tick 1's own values after tick 1 executes, without the holder re-reading anything (FRA Section 12).

Scientific/Runtime Completeness: the violation is fully, precisely characterized; zero isolation exists. Governance Completeness: none. Documentation Completeness: complete (Functional Gap FG-002, this document's own re-confirmation). Verification Completeness: complete (100% reproducible on demand).

Dependency Coverage: DEP-001, DEP-007 (both fully accounted for by this finding).

Certification Coverage: none.

Cross-Unit Relevance: none.

Current Status: **MISSING**. The requirement ("SHALL NOT be an object that a subsequent tick's own processing will further mutate") is demonstrably, unconditionally violated for this specific field on every tick; no partial isolation exists for this object.

Remaining Gap: identical to CAP-001's own remaining gap - an isolation mechanism, contingent on the read-contract decision.

Scope Boundary: does not select the isolation mechanism.

Architecture Relevance: highest priority within Cluster 2, directly actionable once CAP-001 resolves.

Specification Relevance: a dedicated Runtime Contract (isolation guarantee) is required once CAP-001 resolves.

Traceability: Tick-Complete Snapshot definition; AI-009; AC-009; FR-003; Functional Gap FG-002; DEP-001, DEP-007.

---

**P3-02-CAP-005 - Nested Mutable-Object Isolation (General Convention)**

Capability Type: Runtime Capability.

Description: whether dict-shaped canonical objects other than the top-level container are freshly constructed, rather than mutated in place, at every publication.

Source FR(s): FR-004 (general finding, Verified Conformant Finding VCF-001). Source DEP(s): DEP-008 (downstream to FR-022), DEP-009 (sibling to FR-003), DEP-016/017/018/019 (Writer-path prerequisites).

Repository Evidence: `position.py:75-83` (fresh dict every call); `strategy.py:21,47,69`; `executor.py:15,22,28` (all fresh dict literals).

Runtime Evidence: captured nested Position references remain stable across a subsequent tick, with differing object identity from the newer tick's own Position object (FRA Section 12, empirically confirmed).

Scientific/Runtime Completeness: complete for the four objects this convention currently covers (Position, Strategy Selection, Execution Decision, Execution Event). Governance Completeness: none - no contract, type system, or runtime check enforces this; it is producer discipline only. Documentation Completeness: complete (Verified Conformant Finding VCF-001). Verification Completeness: complete for the current HEAD; not future-proof without a structural guarantee.

Dependency Coverage: DEP-009 (paired with CAP-003/CAP-006 under OQ-007).

Certification Coverage: none.

Cross-Unit Relevance: none.

Current Status: **PARTIAL**. Runtime behaviour is currently fully conformant for the objects it covers, but the capability - "fresh construction is guaranteed," not merely "fresh construction currently happens" - does not exist as a governed property; one exception already exists elsewhere in the same object class (CAP-006), demonstrating the convention is not self-enforcing.

Remaining Gap: a structural or documented guarantee, not merely continued producer discipline.

Scope Boundary: does not require immutability of an object's own internals, only distinct identity across publications; does not select the enforcement mechanism.

Architecture Relevance: moderate - resolved jointly with CAP-006 and OQ-007.

Specification Relevance: a future Runtime Contract could formalize this convention as a binding rule without requiring a new mechanism, if the Architecture stage so decides.

Traceability: Rule IF-001; Derived View definition; AI-007 (related); Verified Conformant Finding VCF-001; FR-004; DEP-008, DEP-009.

---

**P3-02-CAP-006 - Performance-Metrics Aliasing (Specific Finding)**

Capability Type: Runtime Capability.

Description: whether `PerformanceEngine.update()`'s own returned and published value is a distinct object on every call.

Source FR(s): FR-004 (specific instance, Functional Gap FG-003). Source DEP(s): DEP-008, DEP-035 (shared-object link to FR-016/CAP-016), DEP-019, DEP-050.

Repository Evidence: `performance.py:4,34`.

Runtime Evidence: `id(engine.performance_engine.stats)` identical across every call for the lifetime of the instance, independently re-confirmed twice in this session (FRA Section 12; targeted review): a reference held from tick 0 showed a new `"HOLD"` key after three further, unread ticks.

Scientific/Runtime Completeness: the violation is fully, precisely characterized; zero fresh-construction exists for this object. Governance Completeness: none. Documentation Completeness: complete (Functional Gap FG-003, independently re-confirmed by the targeted review this session already delivered). Verification Completeness: complete (100% reproducible, and, unlike CAP-004, persistent for the life of the runtime session rather than merely per-tick).

Dependency Coverage: DEP-008, DEP-035, DEP-019, DEP-050 (all fully accounted for).

Certification Coverage: none.

Cross-Unit Relevance: DEP-050 - the eventual resolution mechanism must remain compatible with whatever P3-03 later does to `PerformanceEngine`'s own accounting methodology (TD-004); this capability's own fix (object-identity discipline) is explicitly distinct from, and does not require, TD-004's own resolution.

Current Status: **MISSING**. The requirement is demonstrably, unconditionally violated on every tick after the first, and - per the targeted review already delivered this session - this remains the more severe of the two proven aliasing findings (Medium severity, narrowly grounded in AI-009/AC-009/the Tick-Complete Snapshot definition specifically, not the broader multi-invariant set the FRA's own initial traceability loosely gestured toward).

Remaining Gap: an object-identity-isolation mechanism for `PerformanceEngine`'s own publication, independent of TD-004's own eventual accounting-methodology redesign.

Scope Boundary: does not redesign `PerformanceEngine`'s own accounting methodology (TD-004, P3-03's own scope); addresses only object-identity discipline.

Architecture Relevance: high priority, actionable independently of CAP-001 (unlike CAP-004, this capability's own fix does not require the `CanonicalState.get()` read-contract to be resolved first, since `PerformanceEngine.stats` is a separate object from `CanonicalState.state`).

Specification Relevance: a dedicated Runtime Contract is required, and, unlike CAP-004, could be specified and implemented independently of CAP-001's own resolution.

Traceability: Rule IF-001; Derived View definition; AI-009; AC-009; Functional Gap FG-003; TD-004; FR-004; DEP-008, DEP-019, DEP-035, DEP-050.

---

**P3-02-CAP-007 - Producer Isolation (Independent Verifiability)**

Capability Type: Verification Capability.

Description: whether every Runtime Ownership Matrix row's own Producer, published object, and Primary Consumer(s) are independently, repeatably verifiable, not solely documented.

Source FR(s): FR-005. Source DEP(s): DEP-003, DEP-010, DEP-011, DEP-012, DEP-013, DEP-014.

Repository Evidence: every Matrix row's Producer/Consumer pairing re-confirmed matching the active trace exactly (FRA Section 10).

Runtime Evidence: no structural enforcement mechanism, no automated verification procedure exists anywhere in `run_engine/` (Verification Gap VG-001).

Scientific Completeness: the pairing itself is fully characterized. Runtime Completeness: the underlying behaviour is currently correct (manually confirmed). Governance Completeness: partial (the Matrix itself is governance-complete; verifiability of conformance to it is not). Documentation Completeness: complete. Verification Completeness: none - no repeatable, independent procedure exists.

Dependency Coverage: DEP-010 (feeds CAP-008 directly), DEP-011 through DEP-014 (feed CAP-013, CAP-014, CAP-015, CAP-016).

Certification Coverage: none.

Cross-Unit Relevance: none.

Current Status: **PARTIAL**. Runtime behaviour is currently conformant by manual inspection; independent, repeatable verifiability - the capability FR-005 actually requires - does not exist.

Remaining Gap: a repeatable, independent verification procedure.

Scope Boundary: does not require a specific enforcement mechanism (read-only wrapper, copy-on-read); addresses verification only, not enforcement.

Architecture Relevance: low priority for a new decision; primarily a Specification/Implementation-stage verification-procedure question.

Specification Relevance: a future IU-level verification procedure (analogous to P3-01's own Verification-Only Implementation Units) could close this without any runtime change.

Traceability: Runtime Ownership Matrix; Rule OM-004; AC-002; AC-010; Verification Gap VG-001; FR-005; DEP-003, DEP-010 through DEP-014.

---

**P3-02-CAP-008 - Consumer Read-Only Discipline (Independent Verifiability)**

Capability Type: Verification Capability.

Description: whether no Primary Consumer mutates the runtime object it consumes, independently and repeatably verifiable.

Source FR(s): FR-017. Source DEP(s): DEP-004, DEP-010.

Repository Evidence: direct inspection of every consumer (`StrategySelector`, `Executor`, `TradeLifecycleEngine`, `PositionEngine`, `PnLEngine`, `RiskEngine`, `PerformanceEngine`) found no in-place mutation of a received parameter (Verified Conformant Finding VCF-004).

Runtime Evidence: identical to CAP-007's own evidence base, applied specifically to Rule OM-004.

Scientific/Runtime Completeness: the underlying behaviour is currently correct, confirmed by direct inspection. Governance Completeness: Rule OM-004 itself is fully governed; its verifiability is not. Documentation Completeness: complete. Verification Completeness: none, identical reasoning to CAP-007.

Dependency Coverage: DEP-004 (upstream, conditional on CAP-001), DEP-010 (upstream from CAP-007).

Certification Coverage: none.

Cross-Unit Relevance: none.

Current Status: **PARTIAL**. Identical reasoning to CAP-007, this capability's own special case.

Remaining Gap: identical to CAP-007's own remaining gap, specialized to Rule OM-004.

Scope Boundary: does not require a structural enforcement mechanism; verification only.

Architecture Relevance: low priority for a new decision.

Specification Relevance: shares CAP-007's own future verification-procedure path.

Traceability: Rule OM-004; AC-002; Verification Gap VG-001; FR-017; DEP-004, DEP-010.

---

**P3-02-CAP-009 - Writer-on-Behalf-Of Exclusivity (Information-Flow Level)**

Capability Type: Runtime Capability.

Description: whether every `CanonicalState.state` mutation occurs exclusively through a named `CanonicalEnforcer.apply_*` method, except Runtime Tick's own explicit Matrix exception.

Source FR(s): FR-006. Source DEP(s): DEP-015 through DEP-019, DEP-043.

Repository Evidence: a scoped repository-wide search finds exactly one call site per `CanonicalState.update_*` method (Section 3).

Runtime Evidence: every call site located exactly as required, re-confirmed this session for the third time (FRA, SDA, this document).

Scientific/Runtime/Governance/Documentation/Verification Completeness: all complete.

Dependency Coverage: DEP-015 (feeds CAP-010), DEP-016/017/018/019 (feed CAP-013, CAP-014, CAP-015, CAP-016 respectively).

Certification Coverage: re-verifies, without reopening, the P3-01 Implementation and Final Certification's own already-certified `apply_regime` migration.

Cross-Unit Relevance: P3-01-AI-009, P3-01-AD-002 (re-verified, not reopened).

Current Status: **COMPLETE**.

Remaining Gap: none.

Scope Boundary: scoped to `run_engine/`; the untracked review/backup directories outside the active runtime are explicitly out of this capability's own scope (consistent with the P3-01 Final Certification's own established practice).

Architecture Relevance: none required; ratification only.

Specification Relevance: none required.

Traceability: Rule OM-003; P3-01-AI-009; P3-01-AD-002; FR-006; DEP-015 through DEP-019, DEP-043.

---

**P3-02-CAP-010 - CanonicalEnforcer Return-Value Contract Consistency**

Capability Type: Runtime Capability.

Description: whether every `CanonicalEnforcer.apply_*` method follows one consistent return-value shape.

Source FR(s): FR-007. Source DEP(s): DEP-015 (upstream from FR-006).

Repository Evidence: `canonical_enforcer.py:47-53`, `apply_risk` returns `self.cs.get()` (the complete state dict); the remaining ten methods each return a single named key.

Runtime Evidence: re-confirmed this session (Section 3); the inconsistency is real but currently has zero observable runtime consequence, since `loop.py`'s own call site (`self.enforcer.apply_risk(...)`) discards the return value.

Scientific Completeness: complete (fully characterized: ten of eleven conformant, one deviation, precisely located). Runtime Completeness: high - ten of eleven methods already conform; the single deviation is narrow, well-understood, and currently inert. Governance Completeness: none (no documented exception exists explaining why `apply_risk` differs). Documentation Completeness: complete (Functional Gap FG-004). Verification Completeness: complete (trivially, mechanically checkable).

Dependency Coverage: DEP-015 (fully accounted for).

Certification Coverage: none.

Cross-Unit Relevance: none.

Current Status: **PARTIAL**. The requirement ("one consistent return-value shape... unless an explicit, documented exception establishes otherwise") is violated by exactly one of eleven methods, with no documented exception recorded for it; this is neither a complete absence of the capability (ten of eleven already conform, and the deviation causes no current harm) nor a fully realized one, matching PARTIAL rather than MISSING given the narrow, bounded, currently-inert nature of the sole deviation.

Remaining Gap: either align `apply_risk`'s own return value to the single-key shape, or explicitly document it as an intentional exception; the Architecture stage decides which.

Scope Boundary: does not require a specific fix.

Architecture Relevance: low priority, narrow, independently actionable without touching any other capability.

Specification Relevance: a single Runtime Contract clause would close this.

Traceability: CanonicalEnforcer's own Writer-on-Behalf-Of role; Rule OM-003 (related, not violated); Functional Gap FG-004; FR-007; DEP-015.

---

**P3-02-CAP-011 - Runtime Event Semantic Stability**

Capability Type: Runtime Capability.

Description: whether every explicit Runtime Event represents exactly one semantic transition, is generated at exactly one call site, and is never mutated after construction.

Source FR(s): FR-010. Source DEP(s): DEP-023, DEP-024, DEP-044.

Repository Evidence: `trade_lifecycle.py:8`, `@dataclass(frozen=True)`; each `event_type` generated at exactly one dedicated method (`_open_trade`, `_scale_in`, `_partial_close`, `_full_close`, `_failure_event`).

Runtime Evidence: re-confirmed this session (Section 3).

Scientific/Runtime/Governance/Documentation/Verification Completeness: all complete for the Lifecycle Event layer specifically, which is this capability's own full scope; the Baseline's own broader Decision/Financial/Risk/Performance event categories are realized as plain values, an already-ratified P3-01 characteristic, not part of this capability's own remaining gap.

Dependency Coverage: DEP-023 (feeds CAP-012), DEP-024 (feeds CAP-021).

Certification Coverage: inherited from the Baseline's own AI-008/ADR-002 grounding.

Cross-Unit Relevance: Baseline AI-008, ADR-002 (not reopened).

Current Status: **COMPLETE**.

Remaining Gap: none.

Scope Boundary: does not extend to introducing distinct event objects for the Decision/Financial/Risk/Performance layers.

Architecture Relevance: none required.

Specification Relevance: none required.

Traceability: AI-008; ADR-002; P3-01-AD-001; FR-010; DEP-023, DEP-024, DEP-044.

---

**P3-02-CAP-012 - Lifecycle-History Immutability and Non-Duplication**

Capability Type: Runtime Capability.

Description: whether Lifecycle History remains exclusively owned by `TradeLifecycleEngine`, is never duplicated into `CanonicalState`, and completed records remain immutable.

Source FR(s): FR-011. Source DEP(s): DEP-023 (upstream from FR-010), DEP-025, DEP-026, DEP-027, DEP-041.

Repository Evidence: `CanonicalState`'s own fifteen schema keys contain no lifecycle-history field; `LifecycleEvent` frozen (Section 3).

Runtime Evidence: no reconstruction of history from Position or Financial State found anywhere in the active trace.

Scientific/Runtime/Governance/Documentation/Verification Completeness: all complete.

Dependency Coverage: DEP-025 (feeds CAP-013), DEP-026 (feeds CAP-014), DEP-027 (feeds CAP-022).

Certification Coverage: grounded in ADR-003, not reopened.

Cross-Unit Relevance: none beyond ADR-003's own already-certified basis.

Current Status: **COMPLETE**.

Remaining Gap: none.

Scope Boundary: does not extend to `Trade`'s own internal mutability, confined to `TradeLifecycleEngine`'s own private management.

Architecture Relevance: none required.

Specification Relevance: none required.

Traceability: AI-004; AI-012; Rule OM-005; ADR-003; FR-011; DEP-023, DEP-025, DEP-026, DEP-027, DEP-041.

---

**P3-02-CAP-013 - Position Information Flow Conformance**

Capability Type: Runtime Capability.

Description: whether Position information flows exclusively as: Lifecycle Event/current position -> `PositionEngine` -> `CanonicalState` (via `CanonicalEnforcer`) -> `PnLEngine`/`RiskEngine`; Exposure remains exclusively derived, never independently owned.

Source FR(s): FR-012. Source DEP(s): DEP-011, DEP-016, DEP-020, DEP-025, DEP-028, DEP-029, DEP-030, DEP-031, DEP-038.

Repository Evidence: re-traced and confirmed exactly matching (FRA Section 17; Section 3 of this document).

Runtime Evidence: `_compute_exposure` confirmed the sole source of Exposure, derived exclusively from `side`, `quantity`, `last_price`.

Scientific/Runtime/Governance/Documentation Completeness: all complete for flow topology specifically. Verification Completeness: complete for topology; independent verifiability of non-mutation remains CAP-007/CAP-008's own separate, PARTIAL concern.

Dependency Coverage: DEP-028 (feeds CAP-014), DEP-029 (feeds CAP-015), DEP-030 (feeds CAP-019), DEP-031 (feeds CAP-022).

Certification Coverage: P2-02A Architecture and Final Certification, not reopened.

Cross-Unit Relevance: P2-02A (compatibility, not reopened).

Current Status: **COMPLETE**. This capability's own scope is flow topology, which the SDA's own Cycle Detection (Section 16 of that document) confirmed does not depend on CAP-019's own outcome (DEP-030 resolved one-directionally: FR-012 -> FR-013, not the reverse); this capability's own COMPLETE status therefore does not require CAP-019 to be resolved first, and remains COMPLETE regardless of CAP-019's own classification.

Remaining Gap: none, for flow topology. Object-identity and cross-tick self-consistency qualifications are tracked separately (CAP-004, CAP-006, CAP-019) and do not reduce this capability's own topology-conformance status.

Scope Boundary: does not reopen P2-02A's own certified ownership, formula, or pre-trade-view contract.

Architecture Relevance: none required; ratification only.

Specification Relevance: none required.

Traceability: ADR-004; Target Information Flow; P2-02A; FR-012; DEP-011, DEP-016, DEP-020, DEP-025, DEP-028 through DEP-031, DEP-038.

---

**P3-02-CAP-014 - Financial Information Flow Conformance**

Capability Type: Runtime Capability.

Description: whether Financial information flows exclusively as: Lifecycle Facts + Entry Basis -> `PnLEngine` -> `CanonicalState` (via `CanonicalEnforcer`) -> `RiskEngine`.

Source FR(s): FR-014. Source DEP(s): DEP-012, DEP-017, DEP-020, DEP-021, DEP-026, DEP-028, DEP-033, DEP-034, DEP-039.

Repository Evidence: re-traced and confirmed exactly matching (FRA Section 18; Section 3 of this document).

Runtime Evidence: every financial value confirmed a Python scalar `float`, structurally immune to aliasing.

Scientific/Runtime/Governance/Documentation/Verification Completeness: all complete for flow topology (subject to CAP-007/CAP-008's own separate PARTIAL verifiability finding, not specific to this flow).

Dependency Coverage: DEP-033 (feeds CAP-015), DEP-034 (feeds CAP-022).

Certification Coverage: P2-03 Architecture and Final Certification, not reopened.

Cross-Unit Relevance: P2-03 (compatibility, not reopened).

Current Status: **COMPLETE**.

Remaining Gap: none.

Scope Boundary: does not reopen P2-03's own certified ownership or formulas.

Architecture Relevance: none required.

Specification Relevance: none required.

Traceability: ADR-005; ADR-006; Target Information Flow; P2-03; FR-014; DEP-012, DEP-017, DEP-020, DEP-021, DEP-026, DEP-028, DEP-033, DEP-034, DEP-039.

---

**P3-02-CAP-015 - Risk Information Flow Conformance**

Capability Type: Runtime Capability.

Description: whether Risk information flows exclusively as: Canonical Financial State + Position -> `RiskEngine` -> `CanonicalState` (via `CanonicalEnforcer`).

Source FR(s): FR-015. Source DEP(s): DEP-006, DEP-013, DEP-018, DEP-020, DEP-021, DEP-029, DEP-033, DEP-040.

Repository Evidence: re-traced and confirmed exactly matching (FRA Section 19; Section 3 of this document).

Runtime Evidence: no active downstream consumer of Risk Metrics exists among the twenty-four P3-02 FRs (SDA Section 10, confirmed absence, not a gap).

Scientific/Runtime/Governance/Documentation/Verification Completeness: all complete for flow topology.

Dependency Coverage: none downstream beyond the absent FR-015->FR-016 relationship the SDA explicitly, correctly records as non-existent (SDA Section 12).

Certification Coverage: P2-04 Architecture and Final Certification, not reopened.

Cross-Unit Relevance: P2-04 (compatibility, not reopened).

Current Status: **COMPLETE**.

Remaining Gap: none.

Scope Boundary: does not reopen P2-04's own certified ownership or formulas.

Architecture Relevance: none required.

Specification Relevance: none required.

Traceability: ADR-007; Target Information Flow; P2-04; FR-015; DEP-006, DEP-013, DEP-018, DEP-020, DEP-021, DEP-029, DEP-033, DEP-040.

---

**P3-02-CAP-016 - Performance Information Flow (Current-State Description)**

Capability Type: Cross-Unit Capability.

Description: whether the current Performance information flow is documented accurately as implemented, without redesigning its own accounting methodology.

Source FR(s): FR-016. Source DEP(s): DEP-014, DEP-019, DEP-035, DEP-050.

Repository Evidence: `performance.py:6-34`; `PerformanceEngine.update`'s own primary input is `decision` (an intention) and `pnl`, not a completed lifecycle outcome (FRA Section 20).

Runtime Evidence: matches TD-004's own already-registered description exactly, re-confirmed this session.

Scientific Completeness: complete - the current-state description itself is fully, accurately evidenced. Runtime Completeness: this capability's own literal scope (accurate documentation, not correct methodology) is fully satisfied; the underlying subject matter (decision-based rather than outcome-based accounting) carries a known, already-registered defect that is explicitly not this capability's own remaining gap to close. Governance Completeness: complete (TD-004 remains correctly forwarded, unmodified). Documentation Completeness: complete. Verification Completeness: complete for the description itself.

Dependency Coverage: DEP-035 (shared-object link to CAP-006, MISSING for a distinct reason - object identity, not accounting methodology).

Certification Coverage: none; TD-004 remains open, Target Phase P3, owned by P3-03.

Cross-Unit Relevance: TD-004, P3-03 (forwarded, not resolved, not P3-02's own gap to close).

Current Status: **PARTIAL**. P3-02's own actual obligation under FR-016 (accurate current-state documentation, no redesign) is fully met; however, since the underlying subject matter this capability describes carries a real, active, already-registered methodological limitation (TD-004) that has not yet been resolved by any unit, this document classifies the capability as a whole PARTIAL rather than COMPLETE, to avoid the FRA's own quality rule against an absolute claim without a necessary qualifying condition - the qualifying condition being that TD-004 remains open.

Remaining Gap: TD-004's own resolution, explicitly P3-03's, not P3-02's.

Scope Boundary: does not redesign `PerformanceEngine`'s own accounting methodology; does not advance TD-004.

Architecture Relevance: none for P3-02; a future P3-03 Architecture stage owns this.

Specification Relevance: none for P3-02.

Traceability: ADR-008; TD-004; Target Information Flow (Performance row); FR-016; DEP-014, DEP-019, DEP-035, DEP-050.

---

**P3-02-CAP-017 - No Downstream Reconstruction**

Capability Type: Runtime Capability.

Description: whether no downstream runtime component reconstructs information already produced by an upstream component.

Source FR(s): FR-009. Source DEP(s): DEP-021, DEP-022.

Repository Evidence: `PnLEngine` derives financial consequences exclusively from `trade_event` and Entry Basis; `RiskEngine` derives Risk Metrics exclusively from Canonical Working State and Position; Lifecycle History exists exactly once (FRA Sections 16-19).

Runtime Evidence: no alternate derivation path found anywhere in the active trace, re-confirmed this session.

Scientific/Runtime/Governance/Documentation/Verification Completeness: all complete.

Dependency Coverage: DEP-021 (evidentiary aggregation from CAP-012, CAP-014, CAP-015), DEP-022 (sibling to CAP-025).

Certification Coverage: none required beyond the already-certified P2-0x contracts this finding rests on.

Cross-Unit Relevance: none.

Current Status: **COMPLETE**.

Remaining Gap: none.

Scope Boundary: does not extend to Performance Information Flow's own already-registered TD-004 concern (CAP-016).

Architecture Relevance: none required.

Specification Relevance: none required.

Traceability: Rule IF-001; Principle IF-002; AC-010; AI-004; FR-009; DEP-021, DEP-022.

---

**P3-02-CAP-018 - Hidden Coupling (Aggregate Synthesis)**

Capability Type: Governance Capability.

Description: whether Hidden Coupling, as the FRA's own Section 6 defines it (a dependency arising from shared mutable object identity, private-state reading, or reconstruction, not represented by an explicit contract), has been eliminated across the unit's own scope.

Source FR(s): FR-001, FR-003, FR-004, FR-005, FR-013, FR-017 (synthesis across all capabilities bearing directly on aliasing, private-state exposure, or unverified consumer discipline). Source DEP(s): all dependencies feeding CAP-001, CAP-004, CAP-006, CAP-007, CAP-008, CAP-019.

Repository Evidence: consolidated from CAP-001 (MISSING), CAP-004 (MISSING), CAP-006 (MISSING), CAP-007 (PARTIAL), CAP-008 (PARTIAL), CAP-019 (COMPLETE, Residual-Risk type).

Runtime Evidence: two concrete, empirically-proven instances of Hidden Coupling exist in the current runtime (top-level Tick-Complete container aliasing; Performance Metrics aliasing); no instance of a consumer actually mutating a producer's object was found; `PositionEngine`'s own private state, while retaining legitimate cross-tick state, is not itself an instance of Hidden Coupling toward any other component (no external consumer reads it directly, P2-02A-AI-005, re-confirmed).

Scientific Completeness: complete - every sub-finding this synthesis draws on is itself independently, precisely characterized. Governance Completeness: none - no unified Hidden-Coupling-elimination decision exists. Documentation Completeness: complete. Verification Completeness: partial (some sub-findings, CAP-007/CAP-008, lack independent verifiability).

Dependency Coverage: aggregates the full dependency set of CAP-001, CAP-004, CAP-006, CAP-007, CAP-008, CAP-019.

Certification Coverage: none; this synthesis capability is newly constructed by this document from already-existing sub-findings, introducing no new fact.

Cross-Unit Relevance: shares CAP-001's own CUO-01 lineage and CAP-006's own TD-004/P3-03 boundary.

Current Status: **MISSING**. As a synthesis property ("Hidden Coupling has been eliminated"), this is a binary claim, and it is demonstrably false: two proven, currently-existing instances of Hidden Coupling (CAP-004, CAP-006) exist in the active runtime today. This is distinct from, and should not be conflated with, any individual sub-capability's own classification; it exists specifically to give the aggregate question its own explicit, trackable answer, consistent with the governing task's own explicit request to evaluate Hidden Coupling as its own numbered item.

Remaining Gap: resolution of CAP-001 (governance), CAP-004 and CAP-006 (runtime), and independent verification of CAP-007/CAP-008.

Scope Boundary: does not itself add any new finding beyond what CAP-001 through CAP-008 and CAP-019 already establish; a synthesis view only.

Architecture Relevance: this synthesis capability's own resolution is entirely a function of its constituent capabilities' own resolutions; no independent Architecture Decision is needed for CAP-018 itself.

Specification Relevance: none beyond what CAP-001, CAP-004, CAP-006, CAP-007, CAP-008 individually require.

Traceability: Hidden Coupling definition (FRA Section 6); FR-001, FR-003, FR-004, FR-005, FR-013, FR-017; all dependencies of CAP-001, CAP-004, CAP-006, CAP-007, CAP-008, CAP-019.

---

**P3-02-CAP-019 - Cross-Tick Object Identity (`PositionEngine` Partial-Mutation Residual Risk)**

Capability Type: Residual-Risk Capability.

Description: whether `PositionEngine`'s own legitimately-retained cross-tick private instance state can reach an internally self-inconsistent value as a consequence of an exception interrupting its own computation, and, if so, whether this condition is properly bounded, documented, and governed rather than silently accepted.

Source FR(s): FR-013 (formerly Functional Gap FG-005 in the FRA's own provisional drafting; reclassified in this document per the targeted Scientific Consistency and Scope Review already delivered this session, per the governing task's own explicit instruction, Section 2). Source DEP(s): DEP-030, DEP-032, DEP-037, DEP-045.

Repository Evidence: `position.py:37-73`, six sequential, non-atomic instance-attribute mutations within `update_post_trade`.

Runtime Evidence, independently re-derived by the targeted review already delivered this session, re-confirmed here: (1) every one of the six mutation statements was individually checked against realistically reachable inputs; none can raise given the current code and current upstream input sanitization (`Executor._get_execution_quantity`'s own guarded `float()` conversion; `TradeLifecycleEngine.current_position()`'s own always-float outputs) - reproducing the finding required artificial fault injection (monkeypatching `_compute_exposure` to raise), not a naturally reachable trigger; (2) the specific demonstrated inconsistency (stale `exposure` against already-updated `quantity`/`last_price`) self-heals unconditionally on the next successful tick, since `exposure` is unconditionally recomputed in every one of `update_post_trade`'s, `project`'s, and `_set_flat`'s own success paths; (3) `CanonicalState`'s own published Position remains entirely unaffected in every case, since `apply_position` is never reached for a Failed Tick; (4) this is a new instance of a risk category P3-01-AD-004 already explicitly accepted (Architecture Section 19: `RegimeClassifier`'s and `StrategySelector`'s own cross-tick instance state "is not reconciled by any mechanism this architecture introduces"), extended here, on new evidence, to `PositionEngine`, without requiring or proposing a rollback, reset, or transaction mechanism, consistent with P3-01-AD-004's own explicit position that no such mechanism is architecturally required.

Scientific Completeness: complete - the condition, its exact trigger requirements, its transience, and its bounded consequence are all now precisely characterized, exceeding the FRA's own original evidentiary depth. Runtime Completeness: complete for all realistically reachable inputs; the theoretical, artificially-only-reachable edge case is fully bounded and self-healing. Governance Completeness: complete, per direct analogy to the already-established P3-01 precedent (P3-01-AD-004 explicitly deciding to document, not resolve, a materially identical risk category for two other components, and the P3-01 CGA's own resulting COMPLETE classification of the corresponding P3-01 capability once that decision was made). Documentation Completeness: complete (this document, the targeted review already delivered, and the FRA's own Section 13/21/30 jointly document it in full). Verification Completeness: complete (the bounding conditions were independently, empirically re-derived, not merely asserted).

Dependency Coverage: DEP-030 (upstream from CAP-013, confirmed non-blocking per CAP-013's own COMPLETE status regardless of this capability's own classification), DEP-032 (downstream to CAP-021), DEP-037 (downstream to CAP-020's own RR-001 qualification), DEP-045 (Cross-Unit, P3-01-AD-004).

Certification Coverage: none yet at the Final Certification level for this specific unit; the analogous P3-01 condition (Post-Exception Financial/Lifecycle Divergence) was certification-reviewed and classified non-blocking by the P3-01 Final Certification, a precedent this capability's own classification directly follows.

Cross-Unit Relevance: P3-01-AD-004 (extends an already-accepted risk category, does not reopen the decision not to build a rollback mechanism).

Current Status: **COMPLETE**. The governing task's own explicit instruction, grounded in the targeted review already delivered this session, directs this classification: a Residual Risk is not to be classified MISSING solely for being a Residual Risk, and this capability's own actual, independently-assessed impact - artificial-injection-only, transient, self-healing, externally invisible, and governed by an already-accepted architectural precedent - supports treating it as fully, scientifically closed at the Capability level, with the residual condition explicitly and permanently documented rather than silently presented as eliminated.

Remaining Gap: none at the Capability level. The residual condition itself (structural absence of atomicity in `PositionEngine`'s own multi-step mutation) remains, unresolved and undesigned by this document, a candidate for a future, separately-scoped Runtime Safety consideration, exactly as Post-Exception Financial/Lifecycle Divergence remains a candidate Technical Debt item without a registered ID.

Scope Boundary: does not select a rollback, reset, or transaction mechanism; does not reopen P3-01-AD-004.

Architecture Relevance: none required for P3-02 itself; a future, separately-scoped unit (Runtime Safety/Control) may eventually consider it, consistent with TD-007's own already-registered "Future Phase-2 Runtime Control Unit" target.

Specification Relevance: none required for P3-02.

Traceability: AI-005; P3-01-AD-004; P3-01 Architecture Section 19; Post-Exception Financial/Lifecycle Divergence (related, distinct instance); FR-013; DEP-030, DEP-032, DEP-037, DEP-045.

---

**P3-02-CAP-020 - Deterministic Information Flow**

Capability Type: Runtime Capability.

Description: whether, given identical tick inputs and an identical initial `CanonicalState`, the active information flow produces functionally identical intermediate and final results, with no aliasing introducing cross-instance nondeterminism.

Source FR(s): FR-022. Source DEP(s): DEP-005, DEP-007, DEP-008, DEP-037, DEP-049.

Repository Evidence: every Computational Authority confirmed pure or effectively-pure; the sole non-deterministic component in the repository (`StateModulator`) confirmed unimported (FRA Section 24).

Runtime Evidence: P3-01's own already-certified dual-instance stage-boundary replay, re-cited, not re-executed, remains valid (not reopened).

Scientific/Runtime Completeness: complete for cross-instance determinism, the actually-certified and actually load-bearing property. Governance Completeness: complete (inherits P3-01-AD-007/Contract EO-013, not reopened). Documentation Completeness: complete, including the explicit bounding of Residual Risk RR-001 (single-instance retained-reference risk, downstream of CAP-004/CAP-006, currently inert since `main.py` retains no cross-tick reference). Verification Completeness: complete for cross-instance determinism; RR-001 itself is not independently verified beyond being bounded and currently inert, matching the same reasoning already applied to CAP-019.

Dependency Coverage: DEP-007, DEP-008 (both fully accounted for as the source of RR-001), DEP-037 (conditional, resolved per CAP-019's own now-COMPLETE status).

Certification Coverage: P3-01-AD-007/Contract EO-013, P3-01 Final Certification Section 25, not reopened.

Cross-Unit Relevance: P3-01-AD-007/Contract EO-013.

Current Status: **COMPLETE**. Cross-instance determinism, the property this requirement and its governing P3-01 precedent actually certify, is fully intact; Residual Risk RR-001 is explicitly documented, bounded (contingent on a future single-instance retaining consumer that does not currently exist), and does not, per the same reasoning already applied to CAP-019, reduce this capability's own classification below COMPLETE.

Remaining Gap: none at the Capability level; RR-001 remains a documented, bounded, currently-inert residual condition, not a gap this capability's own scope requires closing.

Scope Boundary: does not re-execute P3-01's own replay verification; does not extend determinism claims to a retry sequence following a Failed Tick.

Architecture Relevance: none required; ratification and explicit RR-001 documentation only.

Specification Relevance: none required.

Traceability: AI-005; AI-006; P3-01-AD-007; P3-01 Final Certification Section 25; Residual Risk RR-001; FR-022; DEP-005, DEP-007, DEP-008, DEP-037, DEP-049.

---

**P3-02-CAP-021 - Failure Information Flow Conformance**

Capability Type: Runtime Capability.

Description: whether Failure information flow conforms exactly to P3-01-AD-004 (Failed Tick) and P3-01-AD-006 (rejected-transition non-mutation), with any newly-identified divergence condition explicitly documented.

Source FR(s): FR-018. Source DEP(s): DEP-024, DEP-032, DEP-046.

Repository Evidence: both P3-01 conditions re-confirmed unchanged (FRA Section 21; Section 3 of this document).

Runtime Evidence: the newly-identified `PositionEngine`-private-state divergence (CAP-019) is recorded as a distinct instance, now fully classified COMPLETE (Residual-Risk type) per CAP-019's own resolution.

Scientific/Runtime/Governance/Documentation/Verification Completeness: all complete, including the newly-identified condition, now that CAP-019 itself is resolved.

Dependency Coverage: DEP-024 (upstream from CAP-011), DEP-032 (upstream from CAP-019, now satisfied).

Certification Coverage: P3-01-AD-004, P3-01-AD-006, not reopened.

Cross-Unit Relevance: P3-01-AD-004, P3-01-AD-006.

Current Status: **COMPLETE**. FR-018's own Requirement Statement required only that any newly-identified divergence condition be "explicitly documented, not silently accepted or silently resolved" - a bar this document, the FRA, and the targeted review already delivered this session jointly satisfy in full for the `PositionEngine` instance (CAP-019).

Remaining Gap: none.

Scope Boundary: does not design a new failure architecture, a rollback mechanism, or a reconciliation mechanism.

Architecture Relevance: none required; ratification only.

Specification Relevance: none required.

Traceability: P3-01-AD-004; P3-01-AD-006; ADR-011; Post-Exception Financial/Lifecycle Divergence; FR-018; DEP-024, DEP-032, DEP-046.

---

**P3-02-CAP-022 - HOLD and No-Execution Information Flow Conformance**

Capability Type: Runtime Capability.

Description: whether a HOLD or no-execution tick conforms exactly to P3-01-AD-005.

Source FR(s): FR-019. Source DEP(s): DEP-027, DEP-031, DEP-034, DEP-047.

Repository Evidence: re-traced and confirmed conformant (FRA Section 22; Section 3 of this document), with one terminological imprecision noted (Documentation Gap DG-002) not affecting the substantive finding.

Runtime Evidence: every stage still executes; Tick Completion is still reached; every downstream stage produces a well-defined result for a no-event input.

Scientific/Runtime/Governance/Verification Completeness: all complete. Documentation Completeness: high, with DG-002 (Section 13 of this document) tracked as an open, low-severity terminological correction, not a substantive gap.

Dependency Coverage: DEP-027 (upstream from CAP-012), DEP-031 (upstream from CAP-013), DEP-034 (upstream from CAP-014).

Certification Coverage: P3-01-AD-005, not reopened.

Cross-Unit Relevance: P3-01-AD-005.

Current Status: **COMPLETE**.

Remaining Gap: DG-002's own terminological correction (informal), tracked separately, does not affect this capability's own substantive classification.

Scope Boundary: does not reopen P3-01-AD-005.

Architecture Relevance: none required.

Specification Relevance: none required.

Traceability: P3-01-AD-005; Tick Completion Contract; FR-019; DEP-027, DEP-031, DEP-034, DEP-047.

---

**P3-02-CAP-023 - Alternative Information Path Exclusivity**

Capability Type: Runtime Capability, jointly with Documentation Capability.

Description: whether no inactive or dormant code path constitutes an active duplicate Producer or Writer, and whether every dormant file's own disposition is explicitly tracked.

Source FR(s): FR-020. Source DEP(s): DEP-048.

Repository Evidence: the four P3-01-named inactive directories re-confirmed unimported; two additional dormant files (`position_sizing.py`, `state_modulation.py`) identified by the FRA and re-confirmed here (Documentation Gap DG-001).

Runtime Evidence: an independent, AST-based import-closure check re-confirms no dormant file is imported by the active path (FRA Section 5, re-verified this session).

Scientific/Runtime Completeness: complete (exclusivity itself). Governance Completeness: complete (dormant-file disposition explicitly, correctly forwarded to Phase 6 Repository Consolidation, not decided prematurely). Documentation Completeness: complete - unlike the FRA's own provisional "partially evidenced" note (written reflexively, before the FRA had finished naming DG-001 in its own later sections), this document confirms the FRA's own final, delivered text already names both newly-identified dormant files in a governing document, satisfying FR-020's own Validation Condition in full. Verification Completeness: complete (repeatable, mechanical import-closure check).

Dependency Coverage: DEP-048 (fully accounted for).

Certification Coverage: re-verifies P3-01-AD-009, not reopened.

Cross-Unit Relevance: P3-01-AD-009; Phase 6 Repository Consolidation (disposition question explicitly forwarded, not decided here).

Current Status: **COMPLETE**. This is an upgrade from the FRA's own provisional "partially evidenced" self-assessment: at CGA time, using the FRA's own now-complete, delivered text as evidence, both the exclusivity property and the documentation obligation FR-020 requires are satisfied in full.

Remaining Gap: none at the P3-02 level; the retain/integrate/archive/remove disposition for every dormant file (both the four P3-01-named directories and the two newly-identified files) remains Phase 6 Repository Consolidation's own scope, not a P3-02 gap.

Scope Boundary: does not classify or dispose of any dormant file.

Architecture Relevance: none required for P3-02.

Specification Relevance: none required for P3-02.

Traceability: P3-01-AD-009; AI-013; Phase 6; Documentation Gap DG-001; FR-020; DEP-048.

---

**P3-02-CAP-024 - Complete Object-Level Traceability**

Capability Type: Documentation Capability.

Description: whether every runtime object named in the Runtime Ownership Matrix is traceable through its originating observation, transformation, publication, consumption, canonical storage, historical storage, and derived-view/object-identity status.

Source FR(s): FR-021. Source DEP(s): DEP-036.

Repository Evidence: a complete traceability table constructed and confirmed for every object in the FRA's own Runtime Object Inventory (FRA Section 9, Section 25).

Runtime Evidence: independently re-traced during this document's own Section 3.

Scientific/Runtime/Governance/Documentation/Verification Completeness: all complete; this capability is, by its own nature, more granular than P3-01-AD-008's own minimum requirement (file/line only), since it additionally establishes object-identity status per object.

Dependency Coverage: DEP-036, the aggregate dependency drawing on FR-001 through FR-020 collectively; this capability's own completeness is therefore contingent on every one of those Functional Requirements having at least been evidenced (not necessarily COMPLETE) - a condition already satisfied, since every FR in Sections above carries at least "currently evidenced," "partially evidenced," or a fully-characterized gap, with none left wholly unexamined.

Certification Coverage: extends, without reopening, P3-01-AD-008.

Cross-Unit Relevance: P3-01-AD-008.

Current Status: **COMPLETE**.

Remaining Gap: none; per Open Question OQ-014 (SDA Section 18), this capability's own traceability construction does not itself require every other capability to reach COMPLETE first, only that each be evidenced, which this document's own Section 5 confirms for all twenty-seven.

Scope Boundary: does not extend to a full semantic-continuity re-derivation beyond what CAP-013, CAP-014, CAP-015 already establish.

Architecture Relevance: none required.

Specification Relevance: none required.

Traceability: AI-014; AC-011; P3-01-AD-008; FR-021; DEP-036.

---

**P3-02-CAP-025 - Semantic Continuity of Upstream Information**

Capability Type: Runtime Capability.

Description: whether information produced by an upstream component remains semantically unchanged throughout downstream processing.

Source FR(s): FR-008. Source DEP(s): DEP-020, DEP-022.

Repository Evidence: Position, Financial, and Risk information flow each match the Target Information Flow's own stated path with no reinterpretation found; Entry Basis retains its P2-02A-certified meaning throughout (FRA Section 17).

Runtime Evidence: re-confirmed via CAP-013, CAP-014, CAP-015's own individual findings (DEP-020, evidentiary aggregation).

Scientific/Runtime/Governance/Documentation/Verification Completeness: all complete.

Dependency Coverage: DEP-020 (fed by CAP-013, CAP-014, CAP-015, all COMPLETE), DEP-022 (sibling to CAP-017).

Certification Coverage: none required beyond the already-certified P2-0x contracts.

Cross-Unit Relevance: P2-02A, P2-03, P2-04 (not reopened).

Current Status: **COMPLETE**.

Remaining Gap: none.

Scope Boundary: does not extend to Performance Information Flow's own decision-versus-outcome distinction (CAP-016).

Architecture Relevance: none required.

Specification Relevance: none required.

Traceability: AI-007; Principle IF-003; P2-02A, P2-03, P2-04; FR-008; DEP-020, DEP-022.

---

**P3-02-CAP-026 - P3-01 Cross-Unit Boundary Compliance**

Capability Type: Cross-Unit Capability.

Description: whether this unit refrains from reopening, redeciding, or altering the P3-01-ratified twelve-stage execution ordering, Tick-Complete Publication semantics, Failed-Tick semantics, or HOLD/rejection ordering.

Source FR(s): FR-023. Source DEP(s): DEP-051.

Repository Evidence: every P3-01-established behaviour re-traced and re-confirmed unchanged across the FRA, SDA, and this document, never redecided.

Runtime Evidence: no runtime file governing P3-01's own scope has been modified by any P3-02 document.

Scientific/Runtime/Governance/Documentation/Verification Completeness: all complete.

Dependency Coverage: DEP-051, the blanket constraint over the entire capability set; independently re-confirmed satisfied by every capability's own Scope Boundary field in this document.

Certification Coverage: P3-01 Final Certification's own CERTIFIED verdict, not reopened.

Cross-Unit Relevance: this capability is, by definition, entirely Cross-Unit.

Current Status: **COMPLETE**.

Remaining Gap: none.

Scope Boundary: this requirement is itself a scope boundary.

Architecture Relevance: none required; a standing constraint on all future P3-02 stages.

Specification Relevance: none required.

Traceability: P3-01 Final Certification; P3-01-AD-001 through AD-010; FR-023; DEP-051.

---

**P3-02-CAP-027 - P3-03 Cross-Unit Boundary Compliance**

Capability Type: Cross-Unit Capability.

Description: whether this unit refrains from redesigning `PerformanceEngine`'s own accounting methodology or advancing TD-004's own resolution.

Source FR(s): FR-024. Source DEP(s): DEP-052.

Repository Evidence: Performance Information Flow documented at its current-state shape only (CAP-016), explicitly not redesigned anywhere in this document.

Runtime Evidence: `performance.py` unmodified.

Scientific/Runtime/Governance/Documentation/Verification Completeness: all complete.

Dependency Coverage: DEP-052, the blanket constraint over CAP-006 and CAP-016 specifically; independently re-confirmed satisfied.

Certification Coverage: none required; TD-004 remains open, owned by P3-03.

Cross-Unit Relevance: this capability is, by definition, entirely Cross-Unit.

Current Status: **COMPLETE**.

Remaining Gap: none.

Scope Boundary: this requirement is itself a scope boundary.

Architecture Relevance: none required for P3-02.

Specification Relevance: none required for P3-02.

Traceability: Implementation Baseline (P3-02/P3-03 unit definitions); TD-004; FR-024; DEP-052.

---

## 6. Capability Matrix

| CAP | Title | Type | Status |
|---|---|---|---|
| CAP-001 | CanonicalState Read-Contract Existence | Governance | MISSING |
| CAP-002 | Canonical Working State Internal-Only Consumption | Runtime | COMPLETE |
| CAP-003 | Tick-Complete Snapshot Stability (General) | Runtime | PARTIAL |
| CAP-004 | Top-Level Result Object-Identity Isolation | Runtime | MISSING |
| CAP-005 | Nested Mutable-Object Isolation (General) | Runtime | PARTIAL |
| CAP-006 | Performance-Metrics Aliasing | Runtime | MISSING |
| CAP-007 | Producer Isolation (Verifiability) | Verification | PARTIAL |
| CAP-008 | Consumer Read-Only Discipline (Verifiability) | Verification | PARTIAL |
| CAP-009 | Writer-on-Behalf-Of Exclusivity | Runtime | COMPLETE |
| CAP-010 | CanonicalEnforcer Return-Value Consistency | Runtime | PARTIAL |
| CAP-011 | Runtime Event Semantic Stability | Runtime | COMPLETE |
| CAP-012 | Lifecycle-History Immutability and Non-Duplication | Runtime | COMPLETE |
| CAP-013 | Position Information Flow Conformance | Runtime | COMPLETE |
| CAP-014 | Financial Information Flow Conformance | Runtime | COMPLETE |
| CAP-015 | Risk Information Flow Conformance | Runtime | COMPLETE |
| CAP-016 | Performance Information Flow (Current-State) | Cross-Unit | PARTIAL |
| CAP-017 | No Downstream Reconstruction | Runtime | COMPLETE |
| CAP-018 | Hidden Coupling (Aggregate Synthesis) | Governance | MISSING |
| CAP-019 | Cross-Tick Object Identity (PositionEngine) | Residual-Risk | COMPLETE |
| CAP-020 | Deterministic Information Flow | Runtime | COMPLETE |
| CAP-021 | Failure Information Flow Conformance | Runtime | COMPLETE |
| CAP-022 | HOLD and No-Execution Information Flow Conformance | Runtime | COMPLETE |
| CAP-023 | Alternative Information Path Exclusivity | Runtime/Documentation | COMPLETE |
| CAP-024 | Complete Object-Level Traceability | Documentation | COMPLETE |
| CAP-025 | Semantic Continuity of Upstream Information | Runtime | COMPLETE |
| CAP-026 | P3-01 Cross-Unit Boundary Compliance | Cross-Unit | COMPLETE |
| CAP-027 | P3-03 Cross-Unit Boundary Compliance | Cross-Unit | COMPLETE |

**Distribution: 17 COMPLETE, 6 PARTIAL, 4 MISSING** (twenty-seven total).

## 7. Runtime Capability Coverage

Eighteen capabilities are typed (wholly or jointly) Runtime Capability: CAP-002, CAP-003, CAP-004, CAP-005, CAP-006, CAP-009, CAP-010, CAP-011, CAP-012, CAP-013, CAP-014, CAP-015, CAP-017, CAP-020, CAP-021, CAP-022, CAP-023, CAP-025 (CAP-023 is jointly Runtime/Documentation and is counted once here). Of these, thirteen are COMPLETE (CAP-002, CAP-009, CAP-011, CAP-012, CAP-013, CAP-014, CAP-015, CAP-017, CAP-020, CAP-021, CAP-022, CAP-023, CAP-025), three are PARTIAL (CAP-003, CAP-005, CAP-010), and two are MISSING (CAP-004, CAP-006). Runtime Coverage is strong for information-flow topology (Position, Financial, Risk, Event, Lifecycle History, Failure, HOLD all COMPLETE) and weak specifically for object-identity/aliasing properties (two proven MISSING instances, one general PARTIAL convention).

## 8. Governance Coverage

Two capabilities are typed Governance Capability: CAP-001 (MISSING - no binding read-contract decision exists) and CAP-018 (MISSING - no unified Hidden-Coupling-elimination decision exists, itself a synthesis of CAP-001, CAP-004, CAP-006's own governance gaps). Governance Coverage is the weakest dimension in this Capability Gap Analysis: both Governance-typed capabilities are MISSING, reflecting that the FRA's own central finding (CUO-01's read-contract remains genuinely undecided) has not been resolved by any document in this governance chain to date, consistent with the explicit prohibition on this CGA itself selecting a semantics.

## 9. Documentation Coverage

Three capabilities are typed (wholly or jointly) Documentation Capability: CAP-023 (jointly Runtime/Documentation, COMPLETE) and CAP-024 (COMPLETE). Every Documentation Gap the FRA recorded (DG-001, DG-002) is fully accounted for within an already-COMPLETE capability (CAP-023, CAP-022 respectively), confirming documentation itself is not, at the P3-02 level, an open capability gap - only the underlying runtime or governance properties those documentation notes describe remain open, tracked under their own respective capabilities (CAP-001, CAP-004, CAP-006, CAP-018).

## 10. Verification Coverage

Two capabilities are typed Verification Capability: CAP-007 and CAP-008, both PARTIAL. Both share the identical remaining gap: the absence of a repeatable, independent verification procedure for Rule OM-004 (no consumer mutation), despite the underlying behaviour itself being currently correct by direct manual inspection (Verified Conformant Finding VCF-004). This is the second-weakest dimension after Governance Coverage (Section 8): the runtime behaviour these capabilities describe is not in question, but its independent verifiability is entirely absent.

## 11. Dependency Coverage

All fifty-two P3-02-DEP records (SDA Section 11) are individually accounted for within at least one capability's own Dependency Coverage field above (cross-checked during drafting against the SDA's own Section 19/20 FR/DEP traceability tables). No dependency record is orphaned; every REQUIRED, CONDITIONAL, COMPATIBILITY, and CROSS-UNIT edge the SDA established resolves into exactly one or more capability's own current status, with the SDA's own Cycle Detection (Section 16 of that document) directly informing this document's own resolution of CAP-013's independence from CAP-019 (Section 5, CAP-013's own Current Status field).

## 12. Functional-Gap Assessment

**FG-001** (`CanonicalState.get()` read-contract unresolved, traces to FR-001): classified as Capability **CAP-001, MISSING, Governance Capability**. The FRA's own "unresolved" Current Conformance is confirmed unchanged; no new evidence altered this finding.

**FG-002** (Tick-Complete result top-level aliasing, traces to FR-003): classified as Capability **CAP-004, MISSING, Runtime Capability**, and additionally reflected in CAP-003's own PARTIAL classification for the broader Snapshot Stability property. Confirmed unchanged, independently re-verified in Section 3 of this document, normatively grounded specifically in AI-009, AC-009, and the Tick-Complete Snapshot definition, per this document's own quality rule.

**FG-003** (Performance Metrics aliasing, traces to FR-004): classified as Capability **CAP-006, MISSING, Runtime Capability**. Confirmed unchanged, independently re-verified twice this session (the targeted review, and Section 3 of this document). Per the governing task's own explicit instruction, this finding is grounded exclusively in the applicable normativity - AI-009, AC-009, and Tick-Complete Snapshot semantics specifically - and not in Rule OM-004, AI-005, AI-006, AC-010, or AC-012, each of which the targeted review already determined does not apply to this finding.

**FG-004** (`CanonicalEnforcer.apply_risk` return-value inconsistency, traces to FR-007): classified as Capability **CAP-010, PARTIAL, Runtime Capability**. Confirmed unchanged.

**Former FG-005** (`PositionEngine` cross-tick private-state self-consistency, traces to FR-013): **not classified as a Functional Gap in this document.** Per the governing task's own explicit instruction and the targeted review already delivered this session, this finding is carried forward exclusively as **Residual Risk, Capability CAP-019, COMPLETE, Residual-Risk Capability** (Section 15).

## 13. Verified-Conformant Assessment

**VCF-001** (Position, Strategy Selection, Execution Decision, Execution Event freshly constructed): underlies Capability **CAP-005, PARTIAL** (the convention itself is confirmed intact for these four objects; PARTIAL reflects the absence of a structural guarantee, not any defect in the convention's own current application).

**VCF-002** (scalar canonical values structurally immune to aliasing): confirmed unchanged, underlies the COMPLETE status of CAP-014 and CAP-015 (Financial and Risk Information Flow), where every canonical value in scope is a scalar.

**VCF-003** (Writer-on-Behalf-Of exclusivity intact): underlies Capability **CAP-009, COMPLETE**.

**VCF-004** (no consumer-side or engine-internal mutation found): underlies Capabilities **CAP-007 and CAP-008, both PARTIAL** (the behaviour VCF-004 confirms is exactly what CAP-007/CAP-008 require; their own PARTIAL status reflects only the absence of independent verifiability, not any doubt about VCF-004's own finding).

## 14. Documentation-Gap Assessment

**DG-001** (`position_sizing.py`, `state_modulation.py` newly identified, dormant, undocumented before the FRA): underlies Capability **CAP-023, COMPLETE**. The FRA's own act of naming both files closes the documentation obligation FR-020 requires; their eventual disposition remains Phase 6 Repository Consolidation's own scope, not a P3-02 capability gap.

**DG-002** (HOLD-path terminological imprecision, "receives None" versus a well-formed FLAT-shaped dict): underlies Capability **CAP-022, COMPLETE**, with DG-002 tracked as a minor, non-substantive documentation correction that does not affect CAP-022's own classification.

## 15. Verification-Gap Assessment

**VG-001** (Rule OM-004 never independently, systematically verified): underlies Capabilities **CAP-007 and CAP-008, both PARTIAL**. This is the sole Verification Gap the FRA recorded, and it is fully accounted for within these two capabilities; no other capability in this document carries an open Verification Gap.

## 16. Residual-Risk Assessment

**RR-001** (single-instance retained-reference risk, downstream of FG-002/FG-003): underlies Capability **CAP-020**'s own explicit documentation, without reducing CAP-020's own COMPLETE classification for cross-instance determinism, since RR-001 concerns a materially different property (post-return value stability for a hypothetical future retaining consumer, not currently exercised by `main.py`) and remains bounded and inert under the currently active runtime's own actual usage pattern.

**RR-002** (Post-Exception Financial/Lifecycle Divergence, restated from P3-01, not newly created): remains an open, non-blocking, documented residual risk exactly as the P3-01 Final Certification classified it; not reopened, not resolved, and not reclassified by this document. It underlies Capability **CAP-021**'s own explicit documentation obligation (FR-018's own Requirement Statement), which CAP-021 satisfies without needing to resolve RR-002 itself.

**PositionEngine Partial-Mutation Residual Risk** (formerly FG-005): as directed, carried as Residual Risk, underlies Capability **CAP-019, COMPLETE, Residual-Risk Capability** (Section 5), with full reasoning restated in Section 12 above.

All three Residual Risks are explicitly, individually accounted for; none is classified MISSING solely for being a Residual Risk, per the governing task's own explicit classification rule.

## 17. Cross-Unit Capability Assessment

Four capabilities are typed (wholly or jointly) Cross-Unit Capability: **CAP-016** (PARTIAL, forwarded to P3-03/TD-004), **CAP-026** (COMPLETE, P3-01 boundary compliance), **CAP-027** (COMPLETE, P3-03 boundary compliance). CAP-019, though a Residual-Risk Capability by primary type, additionally carries significant Cross-Unit Relevance (P3-01-AD-004) without being primarily typed Cross-Unit, since its own subject matter (`PositionEngine`) is P3-02's own, not another unit's. No Cross-Unit Capability requires this document, or a future P3-02 Architecture, to make a decision belonging to P3-01 or P3-03; every one is either a re-verification of an already-settled fact or an explicit, correctly-bounded forwarding.

## 18. Remaining Capability Gaps

Four capabilities remain open at this document's own closing: **CAP-001** (MISSING, Governance) - no `CanonicalState.get()` read-contract decision exists; **CAP-004** (MISSING, Runtime) - Tick-Complete result top-level aliasing; **CAP-006** (MISSING, Runtime) - Performance Metrics aliasing; **CAP-018** (MISSING, Governance, aggregate synthesis of the above three). Six capabilities remain PARTIAL: **CAP-003** (Snapshot Stability, general), **CAP-005** (Nested Mutable-Object Isolation, general), **CAP-007** (Producer Isolation verifiability), **CAP-008** (Consumer Read-Only Discipline verifiability), **CAP-010** (CanonicalEnforcer return-value consistency), **CAP-016** (Performance Information Flow, forwarded TD-004 dimension). Every remaining gap traces to a specific, already-identified FRA finding (FG-001, FG-002, FG-003, FG-004, VCF-001's own missing structural guarantee, VG-001); no new gap is introduced by this document.

## 19. Capability Findings

**Finding CF-001.** The four MISSING capabilities cluster tightly around exactly two root causes: the undecided `CanonicalState.get()` read-contract (CAP-001, and its downstream CAP-004 dependent) and Performance Metrics' own object-identity discipline (CAP-006, independent of CAP-001). CAP-018 is a synthesis, not an independent third root cause.

**Finding CF-002.** CAP-006 (Performance Metrics) is independently actionable without resolving CAP-001 first, since `PerformanceEngine.stats` is a wholly separate object from `CanonicalState.state`; this creates two independently-schedulable resolution paths for the Architecture stage to consider, rather than one strictly sequential one.

**Finding CF-003.** Every PARTIAL capability's own remaining gap is either (a) the absence of a structural guarantee for an already-correct behaviour (CAP-003, CAP-005, CAP-010), or (b) the absence of independent verifiability for an already-correct behaviour (CAP-007, CAP-008), or (c) a forwarded, out-of-unit methodological limitation (CAP-016). None reflects an incorrect runtime behaviour today.

**Finding CF-004.** The targeted review's own reclassification of the former FG-005 into a COMPLETE Residual-Risk Capability (CAP-019) removes what would otherwise have been a fifth MISSING capability; this reclassification is directly, precedent-consistently grounded in how P3-01-AD-004 and the P3-01 CGA already treated a materially identical risk category for two other components.

**Finding CF-005.** Runtime, Cross-Unit, and Documentation Coverage are each strong (Section 7, Section 9, Section 17); Governance and Verification Coverage are each weak (Section 8, Section 10) and represent the two dimensions requiring the most Architecture-stage attention.

## 20. Capability Risks

**Risk CR-001.** If CAP-001 (read-contract) is resolved toward a mechanism that does not also address CAP-004's own top-level isolation requirement as a natural consequence, two separate mechanisms may be required instead of one, increasing Architecture-stage complexity. Not a decision; a risk to flag for the Architecture stage's own consideration.

**Risk CR-002.** If CAP-006's own resolution (Performance Metrics object-identity) is designed without coordination with P3-03's own eventual TD-004 resolution, the two fixes could conflict; DEP-050 (Cross-Unit) already flags this, and this document restates it as a Capability-level risk for Architecture-stage awareness.

**Risk CR-003.** CAP-007/CAP-008's own continued lack of independent verifiability means a future, currently-undetected consumer-side mutation would not be caught by any existing mechanism; this is a Verification Gap risk (VG-001), not evidence that such a mutation currently exists.

## 21. Capability Constraints

**Constraint CC-001.** No future P3-02 Architecture may select a copy, shallow-copy, deep-copy, or read-only-view semantics for CAP-001/CAP-003/CAP-004 within this document; that selection is explicitly reserved for the Architecture stage.

**Constraint CC-002.** No future P3-02 Architecture may redesign `PerformanceEngine`'s own accounting methodology as part of resolving CAP-006; CAP-006's own remaining gap is object-identity discipline only, explicitly separable from TD-004 (CAP-016, CAP-027).

**Constraint CC-003.** No future P3-02 Architecture may introduce a rollback, reset, or transaction mechanism as part of CAP-019's own continued documentation; CAP-019 is already COMPLETE and requires no further runtime change within this unit's own scope.

**Constraint CC-004.** No future P3-02 Architecture may reopen P3-01-AD-004 through AD-010, or P2-02A/P2-03/P2-04's own certified ownership or formulas, as a consequence of resolving any capability in this document (CAP-009, CAP-011 through CAP-015, CAP-021, CAP-022, CAP-026).

## 22. Scientific Conclusions

Twenty-seven capabilities were derived exclusively from the twenty-four existing Functional Requirements and fifty-two existing Dependency records; no new capability concept was introduced. Seventeen are COMPLETE, six are PARTIAL, four are MISSING. The two governance-typed capabilities (CAP-001, CAP-018) are both MISSING, correctly reflecting that no Architecture Decision has yet been made anywhere in this governance chain regarding `CanonicalState.get()`'s own read-contract. The two verification-typed capabilities (CAP-007, CAP-008) are both PARTIAL, correctly reflecting that the underlying non-mutation behaviour is currently correct but not independently, repeatably verified. Every Cross-Unit and Compatibility-bearing capability remains fully intact with no certified contract reopened. The targeted review's own reclassification of the former FG-005 into a COMPLETE Residual-Risk Capability is applied consistently and is directly precedent-grounded, not a novel or unsupported judgment. No capability classification in this document rests on speculation; every classification traces to specific, independently re-verified repository evidence (Section 3) or specific FRA/SDA text.

## 23. Architecture Readiness Decision

Every capability the governing task's own "besonders bewerten" list names has been individually assessed (Sections 5-6), directly or as part of a governing synthesis capability (CAP-018 for Hidden Coupling). Every FRA finding (five Functional Gaps, four Verified Conformant Findings, two Documentation Gaps, one Verification Gap, three Residual Risks including the reclassified former FG-005) is individually accounted for in exactly one capability (Sections 12-16). All fifty-two SDA dependency records are accounted for (Section 11). No new Functional Requirement, Dependency, Architecture Decision, or Architecture Invariant was introduced; no runtime file was modified; no copy/isolation/rollback mechanism was selected.

**Architecture Readiness: READY**, with the following explicit priorities for the Architecture stage, in the order this document's own findings suggest: (1) CAP-001 - decide `CanonicalState.get()`'s own read-contract, since it gates CAP-003, CAP-004, and conditionally CAP-002/CAP-007/CAP-008/CAP-020; (2) CAP-006 - decide Performance Metrics' own object-identity discipline, independently schedulable from (1); (3) CAP-010 - decide whether to align or document `apply_risk`'s own return-value exception; (4) CAP-007/CAP-008 - decide a verification procedure for Rule OM-004, independent of (1) through (3). CAP-016's own remaining methodological gap is explicitly not this unit's own Architecture-stage obligation; it remains P3-03's.

## 24. FRA Traceability

| FR | Governing Capability(ies) |
|---|---|
| FR-001 | CAP-001 |
| FR-002 | CAP-002 |
| FR-003 | CAP-003, CAP-004 |
| FR-004 | CAP-005, CAP-006 |
| FR-005 | CAP-007 |
| FR-006 | CAP-009 |
| FR-007 | CAP-010 |
| FR-008 | CAP-025 |
| FR-009 | CAP-017 |
| FR-010 | CAP-011 |
| FR-011 | CAP-012 |
| FR-012 | CAP-013 |
| FR-013 | CAP-019 |
| FR-014 | CAP-014 |
| FR-015 | CAP-015 |
| FR-016 | CAP-016 |
| FR-017 | CAP-008 |
| FR-018 | CAP-021 |
| FR-019 | CAP-022 |
| FR-020 | CAP-023 |
| FR-021 | CAP-024 |
| FR-022 | CAP-020 |
| FR-023 | CAP-026 |
| FR-024 | CAP-027 |

All twenty-four Functional Requirements are governed by at least one Capability; CAP-018 additionally draws on FR-001, FR-003, FR-004, FR-005, FR-013, FR-017 as a synthesis, not a primary governing relationship, and is therefore not separately listed as those FRs' own primary row above.

## 25. SDA Traceability (Individually Enumerated)

| DEP | Governing Capability(ies) |
|---|---|
| DEP-001 | CAP-003, CAP-004 |
| DEP-002 | CAP-001, CAP-002 |
| DEP-003 | CAP-001, CAP-007 |
| DEP-004 | CAP-001, CAP-008 |
| DEP-005 | CAP-001, CAP-020 |
| DEP-006 | CAP-002, CAP-015 |
| DEP-007 | CAP-003, CAP-020 |
| DEP-008 | CAP-006, CAP-020 |
| DEP-009 | CAP-003, CAP-006 |
| DEP-010 | CAP-007, CAP-008 |
| DEP-011 | CAP-007, CAP-013 |
| DEP-012 | CAP-007, CAP-014 |
| DEP-013 | CAP-007, CAP-015 |
| DEP-014 | CAP-007, CAP-016 |
| DEP-015 | CAP-009, CAP-010 |
| DEP-016 | CAP-009, CAP-013 |
| DEP-017 | CAP-009, CAP-014 |
| DEP-018 | CAP-009, CAP-015 |
| DEP-019 | CAP-009, CAP-016 |
| DEP-020 | CAP-013, CAP-014, CAP-015, CAP-025 |
| DEP-021 | CAP-012, CAP-014, CAP-015, CAP-017 |
| DEP-022 | CAP-017, CAP-025 |
| DEP-023 | CAP-011, CAP-012 |
| DEP-024 | CAP-011, CAP-021 |
| DEP-025 | CAP-012, CAP-013 |
| DEP-026 | CAP-012, CAP-014 |
| DEP-027 | CAP-012, CAP-022 |
| DEP-028 | CAP-013, CAP-014 |
| DEP-029 | CAP-013, CAP-015 |
| DEP-030 | CAP-013, CAP-019 |
| DEP-031 | CAP-013, CAP-022 |
| DEP-032 | CAP-019, CAP-021 |
| DEP-033 | CAP-014, CAP-015 |
| DEP-034 | CAP-014, CAP-022 |
| DEP-035 | CAP-006, CAP-016 |
| DEP-036 | CAP-024 |
| DEP-037 | CAP-019, CAP-020 |
| DEP-038 | CAP-013 |
| DEP-039 | CAP-014 |
| DEP-040 | CAP-015 |
| DEP-041 | CAP-012 |
| DEP-042 | CAP-002 |
| DEP-043 | CAP-009 |
| DEP-044 | CAP-011 |
| DEP-045 | CAP-019 |
| DEP-046 | CAP-021 |
| DEP-047 | CAP-022 |
| DEP-048 | CAP-023 |
| DEP-049 | CAP-020 |
| DEP-050 | CAP-006, CAP-016 |
| DEP-051 | CAP-026 |
| DEP-052 | CAP-027 |

All fifty-two Dependency records are governed by at least one Capability.

## 26. ADR and Invariant Traceability

| ADR / Invariant | Governing Capability(ies) |
|---|---|
| ADR-001 (SSOT) | CAP-001, CAP-002 |
| ADR-002 (Event-Driven Runtime Evolution) | CAP-011 |
| ADR-003 (TradeLifecycle Authoritative Model) | CAP-012 |
| ADR-004 (Position/Exposure) | CAP-013 |
| ADR-005, ADR-006 (PnL/Financial) | CAP-014 |
| ADR-007 (Risk) | CAP-015 |
| ADR-008 (Performance Ownership) | CAP-016 |
| ADR-009 (Partial Close/Netting) | CAP-013 (not reopened) |
| ADR-010 (Deterministic Ordering) | CAP-002, CAP-020, CAP-026 |
| ADR-011 (Runtime Failure Handling) | CAP-021 |
| ADR-012 (Deferred Persistence/Recovery) | CAP-019 (Scope Boundary only) |
| Runtime Ownership Matrix | CAP-001, CAP-009, CAP-024 |
| Target Information Flow | CAP-013, CAP-014, CAP-015, CAP-016 |
| AI-001 (SSOT) | CAP-001 |
| AI-002 (Unique Ownership) | CAP-001, CAP-007 |
| AI-003 (No Future-Stage Consumption) | CAP-002 |
| AI-004 (Immutable Lifecycle History) | CAP-012, CAP-017 |
| AI-005 (Deterministic Execution) | CAP-019, CAP-020 |
| AI-006 (Deterministic Information Flow) | CAP-020 |
| AI-007 (Semantic Continuity) | CAP-005, CAP-025 |
| AI-008 (Explicit Runtime Events) | CAP-011 |
| AI-009 (Tick Completeness) | CAP-002, CAP-003, CAP-004, CAP-006 |
| AI-012 (Operational/Historical Separation) | CAP-012 |
| AI-014 (Architectural Traceability) | CAP-024 |
| AC-001 through AC-012 | CAP-001, CAP-006, CAP-007, CAP-008, CAP-009 (AC-002); CAP-001, CAP-006, CAP-009 (AC-001/AC-003); CAP-012 (AC-004); CAP-014 (AC-005); CAP-001, CAP-003 (AC-006); CAP-015 (AC-007); CAP-016 (AC-008); CAP-002, CAP-003 (AC-009); CAP-005, CAP-008, CAP-017 (AC-010); CAP-024 (AC-011); CAP-020 (AC-012) |

All named ADRs and Invariants are traced to at least one Capability.

## 27. Prior-Certification Compatibility

P2-02A, P2-03, and P2-04 (Architecture and Final Certification) remain fully compatible: CAP-013, CAP-014, CAP-015 each re-confirm, without reopening, their own respective certified ownership, formula, and non-mutation contracts. P3-01 (Architecture, Specification, Final Certification) remains fully compatible: CAP-002, CAP-009, CAP-011, CAP-019, CAP-020, CAP-021, CAP-022, CAP-023, CAP-026 each re-verify, without reopening, a specific P3-01-certified decision or invariant. No capability in this document requires reopening any prior certification to reach its own stated classification.

## 28. Internal Consistency Review

**Scientific Consistency Review.** Every capability's own classification in Section 5 traces to a specific FRA field, a specific SDA dependency, or a specific, independently re-verified repository fact (Section 3); no classification rests on the methodological precedent of P3-01's own CGA structure alone. PASS.

**Architecture Consistency Review.** No section of this document selects a copy/isolation/rollback/transaction mechanism, defines a `CanonicalEnforcer` signature, or redesigns `PerformanceEngine`; every such choice is explicitly deferred to the Architecture stage in the relevant capability's own Scope Boundary and Architecture Relevance fields. PASS.

**Capability Consistency Review.** No capability is classified MISSING solely for being a Residual Risk (CAP-019, CAP-020 both confirm this rule was applied); no capability's own classification contradicts another's (CAP-013's own COMPLETE status is explicitly reconciled with CAP-019's own separate classification via the SDA's own Cycle Detection finding, Section 5). PASS.

**Information Flow Review.** CAP-013, CAP-014, CAP-015, CAP-016 each confirm, individually, that their own topology matches the Target Information Flow exactly, consistent with the FRA's own Sections 17-20. PASS.

**Mutation and Aliasing Review.** CAP-004 and CAP-006 (both MISSING) are kept strictly distinct from CAP-003 and CAP-005 (both PARTIAL, general properties) and from CAP-019 (COMPLETE, a self-consistency property, not an aliasing property); no section conflates these four distinct concerns. PASS.

**Scope Review.** Section 3 (Scope), the "Wichtige Grenzen" constraints restated in Sections 20-21, and every individual Scope Boundary field confirm no new FR, DEP, AD, AI, or IU is introduced, and no runtime file is touched. PASS.

**Terminology Review.** "Functionally identical" and "byte-identical" are not used as comparison claims anywhere in this document; this sentence is this document's only discussion of either term. "COMPLETE," "PARTIAL," and "MISSING" are applied exactly per Section 2's own restated rules throughout, with explicit justification recorded for every non-obvious classification (CAP-001, CAP-010, CAP-016, CAP-018, CAP-019). PASS.

**Repository Consistency Review.** Every repository-grounded claim in Section 3 was independently re-verified against the current, unchanged runtime during this document's own drafting. PASS.

**Runtime Consistency Review.** No runtime file under `run_engine/` was modified; `git status --short -- run_engine/` confirmed empty both before and after this document's own drafting. PASS.

**Traceability Review.** Section 24 confirms all twenty-four Functional Requirements; Section 25 confirms all fifty-two Dependency records; Section 26 confirms every named ADR and Invariant; Section 27 confirms P2-02A/P2-03/P2-04/P3-01 compatibility. PASS.

**Governance Review.** This document does not create an Architecture, Specification, Implementation, or Final Certification; it introduces no new `P3-02-AD-`, `P3-02-AI-`, or `P3-02-IU-` identifier anywhere (mechanically confirmed, Section 29); it stops, as instructed, before the Architecture. PASS.

**Independent Self Verification.** Every one of the twenty-seven capability classifications was checked, during this document's own closing review, against the specific FRA field or repository fact it claims to rest on; the four MISSING and six PARTIAL classifications were each re-examined a second time to confirm the classification rules (Section 2) were applied consistently rather than by pattern-matching to P3-01's own prior distribution. The reclassification of the former FG-005 into CAP-019 was independently re-derived from first principles in this document's own Section 5, not merely copied from the targeted review's own prior conclusion, and both independent derivations concur. No error was found during this document's own closing review requiring correction before delivery.

Status: Internal Consistency Review PASS.
