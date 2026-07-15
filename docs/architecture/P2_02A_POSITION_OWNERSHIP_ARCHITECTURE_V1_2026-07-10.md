Document Class:
Architecture

Document ID:
P2-02A-ARCH

Version:
V1.0

Status:
Draft for Internal Review

Date:
2026-07-10

Project:
Trading-Bot Scientific Runtime

Subsystem:
Run Engine

Primary Location:
docs/architecture/P2_02A_POSITION_OWNERSHIP_ARCHITECTURE_V1_2026-07-10.md

Depends On:
- docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md
- docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md
- ADR-004 (Position Represents Current Market Exposure), within the Architecture Baseline above
- docs/architecture/analysis/P2_02A_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-10.md
- docs/architecture/analysis/P2_02A_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-10.md
- docs/architecture/analysis/P2_02A_CAPABILITY_GAP_ANALYSIS_V1_2026-07-10.md
- docs/architecture/certification/P1_04_FINAL_CERTIFICATION_V1_2026-07-09.md
- docs/architecture/certification/P2_01_FINAL_CERTIFICATION_V1_2026-07-10.md
- docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md
- current runtime code at HEAD b88eae5

Referenced By:
- future P2-02A Specification
- future P2-02A Implementation
- future P2-02A Verification
- future P2-02A Certification

---

# P2-02A Position Ownership Architecture

## 1. Purpose

This document is the P2-02A Architecture. It converts the twenty functional requirements of the Functional Requirement Analysis, the nine capability clusters and thirteen dependencies of the Scientific Dependency Analysis, and the seventeen capability gaps of the Capability Gap Analysis into binding architecture decisions. Every Open Question the FRA left open (OQ-001, OQ-002, OQ-003, OQ-004, OQ-006) is decided explicitly in this document. OQ-005 remains explicitly DEFERRED OUT OF SCOPE.

This document does not write a Specification. It defines no Python signatures, no method bodies, no file diffs. It does not implement code, and it does not build a test suite. Its output is the binding target architecture the Specification stage must translate into an exact implementation contract.

---

## 2. Scope

In scope: the nine architectural areas listed in the governing task - operative Position semantics, Position-derived Exposure, canonical Position ownership, pre-trade and post-trade Position semantics, the canonical read path, runtime consumer access, Exposure naming separation, the RiskEngine consumption boundary, and validation/compatibility invariants.

Out of scope, per the FRA (Section 20), the SDA (Section 2, Section 25), and the CGA (Section 2): full Financial Ownership Consolidation (P2-03), full Equity/Peak-Equity/Drawdown consolidation, general RiskEngine redesign, TD-006 beyond the narrow Exposure-consumption boundary defined in Section 16, general RiskEngine risk-limiting policy, full Position Sizing logic, activation of PositionSizingEngine, the Lifecycle Control Surface (TD-007), the complete Tick-Complete Snapshot architecture (ADR-010/Phase 3), repository cleanup, the automated regression test suite (TD-005), and any Instrument Registry capability not made strictly necessary by the Exposure semantics chosen in Section 7 (Section 7 confirms none is necessary - see Architecture Decision AD-001).

---

## 3. Binding Inputs

- docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md - ADR-004, the Runtime Ownership Matrix, Rules OM-001 through OM-009, the Architecture Baseline's "Derived View" definition, Architecture Invariants AI-001 through AI-015 (baseline-level, distinct from this document's own P2-02A-AI series).
- docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md - the P2-02A unit definition, Principle IP-002.
- docs/architecture/analysis/P2_02A_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-10.md - twenty functional requirements, as edited and internally reviewed.
- docs/architecture/analysis/P2_02A_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-10.md - nine capability clusters, thirteen dependencies, Open Question classification, six Dependency Stages, as edited and internally reviewed.
- docs/architecture/analysis/P2_02A_CAPABILITY_GAP_ANALYSIS_V1_2026-07-10.md - seventeen capabilities, four-dimension status, Capability Gap Matrix, as edited and internally reviewed.
- docs/architecture/certification/P1_04_FINAL_CERTIFICATION_V1_2026-07-09.md and docs/architecture/certification/P2_01_FINAL_CERTIFICATION_V1_2026-07-10.md - the certified contract baseline this architecture must preserve.
- docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md - TD-001, TD-002, TD-003, TD-005, TD-006, TD-007.
- Current runtime code at HEAD b88eae5, re-traced in Section 19 against the exact RunLoop.step() sequence.

---

## 4. Verified Baseline

Repository state re-verified: branch run-engine-consolidation-safety, HEAD b88eae5, matching the FRA's, SDA's, and CGA's own verification exactly. run_engine/ and docs/architecture/ remain clean at the time of writing this document.

This architecture relies on the FRA's, SDA's, and CGA's repository findings without re-deriving them from the code a second time. Section 19 (Information Flow) re-traces the exact current RunLoop.step() call sequence, as required by the governing task, to confirm the target flow's ordering matches the active code precisely.

---

## 5. Architectural Problem Statement

The CGA found twelve of seventeen capabilities gapped (PARTIAL or MISSING), all traceable to two blocking Open Questions the SDA identified: OQ-001 (Exposure Semantics, BLOCKING) and OQ-003 (the TD-001 dual-state resolution mechanism, CONDITIONALLY BLOCKING). This document exists to resolve both, plus OQ-002, OQ-004, and OQ-006, converting the CGA's twelve gaps into a single, internally consistent target architecture.

---

## 6. Architectural Objectives

1. Define Position-derived Exposure scientifically and unambiguously (OQ-001), closing Capabilities 6, 7, 8.
2. Decide Exposure's storage model (OQ-006), closing Capability 9.
3. Establish exactly one authoritative Position value with a formally legitimate pre-trade temporal view (OQ-003, TD-001), closing Capabilities 2, 3, 10, 11, 13.
4. Define the complete, shape-consistent canonical Position record, closing Capability 5.
5. Separate Position-derived Exposure from RiskEngine's existing allocation value by name and location (OQ-002), closing Capability 15.
6. Define RiskEngine's read-only consumption boundary (OQ-004), closing Capability 14.
7. Preserve every already-certified P1-03/P1-03.1/P1-04/P2-01 contract without exception.

---

## 7. Scientific Definition of Position-derived Exposure

### 7.1 Candidates Evaluated

Nine candidates were evaluated against: scientific meaning, unit/dimension, side/sign semantics, FLAT semantics, required Position fields, required instrument metadata, determinism, replay-ability, ADR-004 compatibility, separation from PnL/Equity/Risk/Allocation, suitability for BTCUSDT and later instruments, minimality, and extensibility.

**Current market value (unsigned)**: quantity times last_price. Dimension: quote currency. Requires only Position fields already available (quantity, last_price). Fails to distinguish LONG from SHORT without also inspecting Side separately - a real information loss for a property ADR-004 calls "Current Exposure" in its own right.

**Signed current market value**: quantity times last_price times a side sign (+1 LONG, -1 SHORT). Same inputs, same dimension, but self-descriptive - the value alone communicates both magnitude and direction, without requiring the consumer to separately inspect Side. Matches the already-certified sign convention PnLEngine already uses (LONG gains as price rises, SHORT gains as price falls).

**Absolute nominal market exposure**: the unsigned magnitude of the signed value above. Rejected as the primary definition for the same reason as unsigned current market value - discards directional information the signed variant preserves at no additional cost.

**Committed capital / entry-basis notional**: quantity times entry_price (with or without sign). Rejected: this value does not change as the market moves, and only changes through Scale-In's weighted-average recomputation; it therefore does not describe the "Current" market exposure ADR-004 names, only a historical cost basis, which is already separately and correctly represented by Average Entry Price.

**Quantity-only exposure**: the raw quantity, with or without sign. Rejected: has no price dimension, so it is not a market-value exposure in any monetary sense, and is not comparable across instruments with different prices.

**Risk-adjusted exposure**: the existing RiskEngine allocation value. Rejected outright: this is Gap 2's own naming collision, not a candidate; it is computed from Equity, Drawdown, and Regime, directly violating the requirement (FRA FR-004) that Position-derived Exposure never depend on RiskEngine-owned state.

**Delta exposure**: an options/derivatives sensitivity measure. Rejected: no options or derivatives greeks model exists anywhere in the active runtime (confirmed by repository search, SDA Section 4); not applicable to the current Side/Quantity/Price spot-style Position model.

**Alternative minimal definitions** (for example unsigned quantity times entry_price, or a zero-dimension ratio): considered and subsumed by the candidates above; none was found scientifically superior to signed current market value under the stated preference criteria.

### 7.2 Removal Test, Compression Test, Counterfactual Review

Removal Test: removing the price dimension (quantity-only) fails ADR-004's "market" qualifier; removing the sign fails to make Exposure self-descriptive of direction; removing the "current" qualifier (using entry_price instead of last_price) fails ADR-004's "Current Exposure" naming and the already-ratified P1-04 policy that last_price tracks the market unconditionally.

Compression Test: Side and signed Exposure both encode direction, which is not strictly non-redundant - but the redundancy is intentional and minimal-cost, since Exposure is explicitly defined by ADR-004 as derived from Position (including Side), and the redundancy makes Exposure self-contained for any future consumer (for example a future aggregation capability, explicitly out of scope here) that would otherwise need to jointly inspect two fields to determine net direction and magnitude.

Counterfactual Review: what happens without a chosen definition - Capabilities 7, 8, 9, 14, 15 remain permanently MISSING or NOT APPLICABLE, per the CGA. Can the requirement be met more simply - no simpler definition satisfies "reflects current market conditions, requires no non-Position data, is unambiguous for LONG and SHORT" simultaneously. Does resolving this create a new necessary capability or only a different representation - it creates exactly one new deterministic computation (Section 8), reusing only already-existing Position fields.

### 7.3 Chosen Definition

**Position-derived Exposure is the signed current market value of the operative Position.**

Rejected alternatives: unsigned current market value, absolute nominal exposure, committed capital / entry-basis notional, quantity-only exposure, risk-adjusted exposure, delta exposure - each rejected for the specific reason given in Section 7.1.

Required Position fields: Side, Quantity, last_price (current mark price). No other Position field is required.

Required instrument metadata: **none**, for the current BTCUSDT-only active scope. Quantity is already expressed in base-asset units and last_price already expresses quote-currency value per base-asset unit; their product is already a correctly-dimensioned quote-currency notional value with no multiplier needed. This directly resolves SDA Dependency P2-02A-DEP-013: since the chosen semantics requires no instrument metadata, this conditional dependency resolves to none, and no external prerequisite capability is introduced by this architecture (Section 28).

Extension rule for instrument metadata: if a future instrument requires a contract multiplier or similar scaling factor, the formula extends to signed quantity times last_price times multiplier, with multiplier defaulting to 1 for every instrument that does not require one, preserving the base semantics without breaking it. This extension is explicitly deferred; it is not designed or specified further here.

---

## 8. Exposure Dimensionality and Sign Semantics

Unit: quote currency (for BTCUSDT, USDT), identical in kind to a monetary notional value, not a dimensionless ratio and not a raw quantity.

Sign rule: LONG positions carry positive Exposure; SHORT positions carry negative Exposure; this matches the sign convention already certified and in production use inside PnLEngine's realized-PnL computation (LONG gains as price rises, SHORT gains as price falls), so no new, unrelated sign convention is introduced anywhere in the system.

FLAT rule: Exposure is exactly 0.0 whenever Quantity is 0.0, evaluated as an explicit, unconditional rule (not as an incidental consequence of multiplying by a zero or undefined Side), so that Side being None at FLAT never produces an exception, NaN, or undefined value (Invariant P2-02A-AI-009, P2-02A-AI-015).

Mathematical semantics (not implementation syntax): Exposure equals (Side factor) multiplied by Quantity multiplied by last_price, where the Side factor is +1 for LONG, -1 for SHORT, and the whole expression is defined to be exactly 0.0 whenever Quantity is 0.0, regardless of Side.

---

## 9. Canonical Position Model

Position remains, per ADR-004, the description of only the current operational market state. This architecture extends the model with exactly one new member (Exposure) and formally clarifies one existing redundancy (Section 10), introducing no other new concept. TradeLifecycleEngine remains completely outside operational Position ownership (unchanged, already conformant, Invariant P2-02A-AI-012).

---

## 10. Canonical Position Shape

The complete canonical Position record, as published by CanonicalEnforcer.apply_position() and as CanonicalState's default shape (Architecture Decision AD-004):

**position** (classification): values FLAT, LONG, SHORT. Semantic meaning: the current market side, including the flat state. Type category: string. FLAT value: "FLAT". Ownership: Computational Authority PositionEngine, Authoritative Owner CanonicalState, Writer-on-Behalf-Of CanonicalEnforcer. Validation Invariant: position equals "FLAT" if and only if side is None; otherwise position equals side. This field is retained for full backward compatibility with every already-certified consumer (StrategySelector, Executor, RiskEngine, main.py logging); it is formally declared a Derived View of side (Section 10, next entry), not an independently-owned classification, resolving the redundancy without a breaking schema change. A future unit may normalize this away; this architecture does not.

**side**: values LONG, SHORT, None. Semantic meaning: the directional identity of the current trade. Type category: string or None. FLAT value: None. Ownership: identical triple to position. Validation Invariant: side is None only when quantity is 0.0.

**quantity**: non-negative float. Semantic meaning: the currently held size of the position, in base-asset units. Type category: float. FLAT value: 0.0. Ownership: identical triple. Validation Invariant: quantity is never negative; quantity is 0.0 if and only if position is FLAT.

**entry_price** (Average Entry Price): non-negative float. Semantic meaning: the quantity-weighted average price at which the current position was established, recomputed on Scale-In per the already-certified P1-03 weighted-average rule. Type category: float. FLAT value: 0.0. Ownership: identical triple. Validation Invariant: unchanged by rejected transitions (Invariant P2-02A-AI-013, ADR-011).

**last_price** (current mark price): float. Semantic meaning: the most recent observed market price, updated unconditionally on every tick regardless of trade acceptance or rejection, per the already-ratified P1-04 Architecture decision. Type category: float. FLAT value: the current tick's market price (unchanged behavior). Ownership: identical triple. Validation Invariant: updates every tick without exception.

**exposure** (Position-derived Exposure): signed float. Semantic meaning: as defined in Section 7 and Section 8. Type category: float. FLAT value: 0.0, exactly. Ownership: identical triple - Computational Authority PositionEngine (the same authority already responsible for quantity, entry_price, and last_price, consistent with ADR-004's assignment of Exposure derivation to Position's own computation), Authoritative Owner CanonicalState, Writer-on-Behalf-Of CanonicalEnforcer, published as part of the same atomic dict as every other field (Section 11). Validation Invariant: deterministic pure function of position/quantity/last_price (Invariant P2-02A-AI-008); never NaN or infinite (Invariant P2-02A-AI-015).

Decision on position versus side: both fields remain required in the canonical shape (Architecture Decision AD-004). position is formally a Derived View of side; existing fields are retained for compatibility; the architecture explicitly permits, but does not perform, later normalization.

**Capability 5 resolution**: CanonicalState's default (pre-first-tick) Position dict and the post-tick published Position dict are hereby defined to be identical in key set and type: both contain exactly the six keys above, with the FLAT-state values given for each. This closes Capability 5 completely (CGA Section 11).

---

## 11. Exposure Storage and Projection Model

### 11.1 Options Compared

**Option A - independently stored field**: Exposure stored as an ordinary CanonicalState field, written through its own mechanism. Risk: without an explicit, enforced reconstruction rule, this option alone does not by itself prevent an independent write path from emerging later.

**Option B - pure Derived View, never stored**: Exposure computed on demand by every consumer via a shared derivation function, never materialized in CanonicalState. Rejected: requires every consumer to import and correctly invoke the derivation logic itself, increasing coupling to the derivation implementation across multiple files rather than centralizing it once; degrades Tick-Complete Snapshot compatibility, since a serialized historical snapshot would be incomplete without also carrying the exact derivation logic version used at that time, a materially worse replay/audit property than recording the historical value directly.

**Option C - stored value with a binding reconstruction rule**: Exposure is stored as part of the canonical Position record, but is recomputed fresh, from Side, Quantity, and last_price, every single time Position itself is recomputed by its sole Computational Authority (PositionEngine), and is published exclusively as part of the same atomic write as every other Position field, through the same single Writer-on-Behalf-Of path (CanonicalEnforcer.apply_position()). No independent write path, no independent ownership, and no drift or staleness risk exists, because Exposure and the rest of Position are always computed and published together, never separately.

**Option D - other minimal variant**: no other variant was found to satisfy ADR-004's textual framing of Exposure as a Position member (favoring storage) while also fully satisfying "no independent ownership" (favoring strict, enforced derivation) as completely as Option C.

### 11.2 Decision

**Option C is adopted.** Exposure is stored, as the sixth member of the canonical Position dict (Section 10), computed fresh by PositionEngine on every Position computation, and published atomically with the rest of Position via the existing apply_position() path. No new CanonicalEnforcer method is introduced.

### 11.3 Justification Against Governing Criteria

ADR-004's "Current Exposure" wording, listing Exposure alongside Side, Quantity, and Average Entry Price as Position's members, favors treating it as a stored member of the same record, not an externally invoked function. The Architecture Baseline's Derived View definition ("no independent ownership... may be regenerated at any time") is satisfied because Exposure's value is, at every moment, exactly what fresh recomputation from the current Position would produce - it is never independently set, cached across a stale Position, or mutated outside PositionEngine's own computation. CanonicalState's schema gains exactly one nested key (position.exposure), no new top-level key. Serialization and future Tick-Complete Snapshot compatibility are improved, not degraded, since a snapshot already fully captures Exposure without requiring re-derivation. Drift and staleness risk is architecturally prevented as long as publication occurs exclusively through the defined canonical write path, via atomic co-computation and co-publication. The write path remains minimal: zero new write paths, one existing write path carries one additional field. Validation is straightforward: any test asserting Position correctness automatically covers Exposure, since they are the same record.

---

## 12. Position Ownership Model

Unchanged from ADR-004 and now fully realized rather than partially conformant: PositionEngine remains the exclusive Computational Authority for Position, now including Exposure (Section 10, Section 11). CanonicalState remains the exclusive Authoritative Owner of the canonical Position, now including Exposure. CanonicalEnforcer remains the sole Writer-on-Behalf-Of, via the existing apply_position() method, unchanged in shape. TradeLifecycleEngine remains completely independent from operational Position ownership (unchanged, already conformant).

The single remaining non-conformance the CGA identified - the pre-trade dual-state read pattern (TD-001) - is resolved in Section 13.

---

## 13. Pre-Trade and Post-Trade Temporal Model

### 13.1 The Core Clarification

There is exactly **one** canonical Position entity, owned exclusively by CanonicalState. "Pre-trade" and "post-trade" are not two entities and not two owners; they are two **temporal projections of the same single canonical entity**, observed at two different points within one tick's processing. This is the central architectural clarification this section makes binding.

- **Canonical previous-tick Position**: the value CanonicalState holds at the moment a new tick's processing begins - that is, whatever was published at the end of the prior tick (or the FLAT default, Section 10, at the very first tick).
- **Current tick pre-trade Position View**: an immutable, explicitly captured reference to the canonical previous-tick Position, held for the duration of the current tick's decision and execution processing, consumed by StrategySelector, Executor, and PnLEngine's entry_basis input.
- **Current tick post-trade canonical Position**: the new value computed by PositionEngine and published by CanonicalEnforcer at the Position Update stage of the current tick, which immediately becomes the canonical previous-tick Position for the next tick.

At any instant, exactly one of these is authoritative: before the current tick's Position Update stage runs, the pre-trade view is authoritative (nothing newer exists yet); after that stage runs, the post-trade value is authoritative and the pre-trade view becomes a fixed historical record of what was true before this tick's own update, no longer current but not thereby invalid - a Derived View is not a "second owner," it is a documented reference to what the single owner held at a specific, recorded moment.

### 13.2 Options Compared

**Option A - explicit copy from CanonicalState before tick processing**: satisfies Rule OM-001 directly; CanonicalState is the sole object ever read externally.

**Option B - PositionEngine.snapshot() formally redefined as a Derived View**: architecturally valid in principle (matches the Derived View definition), but leaves two physically distinct objects in existence (PositionEngine's own instance attributes and CanonicalState's copy) that must be kept synchronized by convention rather than by construction - weaker than Option A, since Rule OM-006 ("CanonicalState exclusively owns active runtime state") is most cleanly satisfied when only one physical storage location for Position exists at all.

**Option C - RunLoop holds an explicit immutable pre_trade_position value, sourced exclusively from CanonicalState**: a concrete refinement of Option A, specifying exactly where and how the capture happens.

**Option D - other minimal variant**: none found preferable; Options A and C converge on the same underlying principle.

### 13.3 Decision

**Options A and C are adopted together.** RunLoop captures an explicit, immutable pre-trade Position view, read exclusively from CanonicalState.state["position"], at the start of each tick, before any Regime, Strategy, Execution, or Lifecycle processing begins. This view - not PositionEngine's own live instance attributes - is what StrategySelector, Executor, and PnLEngine's entry_basis input consume.

PositionEngine's own internal instance state remains exactly what it already is: the Computational Authority's own private working state, necessary for it to perform its computation across calls. What changes is that this internal state is no longer treated as an external read API; no consumer outside PositionEngine itself sources a value from it directly. This is how P2-02A-AI-005 ("the pre-trade view is not a second ownership path") is enforced architecturally, not merely by convention.

### 13.4 Simultaneous Satisfaction of FR-008 and FR-019

FR-008 ("exactly one authoritative Position value per completed tick") is satisfied because CanonicalState.state["position"] remains the only object ever written to, and the only object any external consumer ultimately traces back to, even when a consumer reads a temporally earlier projection of it. FR-019 ("entry_basis handoff... pre-trade snapshot, not post-trade") is satisfied because the captured view is read before the current tick's own Position Update stage runs, preserving the exact timing semantics already certified in P1-03.1, with no change to which tick's value PnLEngine's entry_basis receives, only a change to which physical object that value is read from.

### 13.5 Numerical Non-Regression

Under the current synchronous, single-threaded RunLoop.step() execution model, CanonicalState.state["position"] at the start of a tick and PositionEngine's own instance attributes at that same moment are, by construction, always identical (PositionEngine only mutates itself once per tick, synchronized with CanonicalEnforcer's publication of that same value). Re-sourcing the pre-trade view from CanonicalState therefore produces byte-identical values to the current implementation at every tick, including the first tick (both sources hold the identical FLAT default, Section 10), fully preserving every already-certified P1-03.1/P1-04 PnL result (Validation Obligation, Architecture Decision AD-005).

---

## 14. Canonical Read Path

Following directly from Section 13's decision, the target canonical read path is:

- **StrategySelector** and **Executor** read the pre-trade Position view captured by RunLoop (Section 13), not PositionEngine directly.
- **PnLEngine** reads only entry_price from the same pre-trade Position view, as its explicit entry_basis parameter, unchanged in shape from the P1-03.1-certified contract.
- **RiskEngine** reads the post-trade Position value (including Exposure) via its existing position parameter, already passed at its current call site (Section 16).

No consumer that requires the authoritative value reads from PositionEngine's live instance attributes. This closes Capability 13 (Canonical Read Path) and Capability 10 (Runtime Consumer Access) as defined by the CGA.

---

## 15. Runtime Consumer Contracts

**StrategySelector** - Consumed View: pre-trade Position view (Section 13). Temporal Semantics: before the current tick's decision is finalized. Allowed Fields: the full six-field record is available; current certified usage reads only position (classification). Forbidden Mutations: none permitted; the view is immutable. Source: RunLoop's captured pre-trade view. Ownership Relationship: pure consumer, no ownership of any kind. Error Behaviour: unchanged - defaults to FLAT if the view is falsy, exactly as today. Validation Condition: identical weights output for identical Side/Quantity/Average-Entry-Price input sequences, regardless of the new Exposure field's presence (FR-016).

**Executor** - identical shape to StrategySelector: pre-trade view, classification field only in current usage, immutable, no ownership, unchanged error behaviour, validation condition identical execution decisions for identical inputs.

**PnLEngine** - Consumed View: entry_price only, from the pre-trade Position view, passed as the explicit entry_basis parameter (unchanged mechanism, certified P1-03.1, ratified P1-04). Temporal Semantics: strictly pre-trade. Allowed Fields: entry_price only; Exposure is never read by PnLEngine. Forbidden Mutations: none; forbidden also from ever again depending on the execution dict for entry_price (the exact P1-03.1 defect this architecture must not reintroduce). Source: RunLoop's captured pre-trade view. Ownership Relationship: pure consumer. Error Behaviour: unchanged from the certified P1-04 gate (entry_basis used only for TRADE_CLOSED and PARTIAL_CLOSE events). Validation Condition: identical realized PnL results for the LONG/SHORT, Scale-In, and Partial Close scenarios already certified in P1-03.1 (FR-019).

**RiskEngine** - Consumed View: the post-trade canonical Position (including Exposure), via its existing position parameter. Temporal Semantics: post-trade, matching the current, unchanged ADR-010 execution order (Position Update precedes Risk Evaluation). Allowed Fields: read-only access to all six fields, in particular exposure. Forbidden Mutations: RiskEngine may not own, cache independently, or republish Position or Exposure under any field name, in particular never under the name "exposure" (Section 17). Source: RunLoop's existing post-trade position local variable; no new parameter. Ownership Relationship: strictly read-only consumer (Section 16). Error Behaviour: exposure defaults to 0.0 if absent, never raising. Validation Condition: RiskEngine's Peak-Equity/Drawdown-related computation remains byte-for-byte unchanged (TD-006 non-regression); FR-010, FR-011.

**RunLoop** - Consumed View: none of its own; pure orchestrator. Temporal Semantics: spans the full tick. Allowed: reading CanonicalState, invoking PositionEngine and CanonicalEnforcer methods in the existing, unchanged order (Section 19). Forbidden Mutations: RunLoop computes neither Position nor Exposure itself. Source: not applicable. Ownership Relationship: none (matches the existing Runtime Ownership Matrix assignment of RunLoop to orchestration only). Error Behaviour: unchanged; no new exception handling introduced (consistent with the already-ratified P1-04 rejection of fabricated error-handling machinery). Validation Condition: the full pipeline sequence (Section 19) remains in strictly increasing, unreordered source order.

**CanonicalEnforcer** - Consumed View: the post-trade Position dict, as an opaque value to mediate. Temporal Semantics: invoked once per tick, at the Position Update stage. Allowed: mediating the write via the existing apply_position() shape; no computation. Forbidden Mutations: no new write path is introduced for Exposure; no apply_exposure() method exists. Source: PositionEngine's post-trade return value. Ownership Relationship: Writer-on-Behalf-Of only, never Authoritative Owner (Rule OM-003). Error Behaviour: unchanged from the existing four-line apply_position() shape. Validation Condition: FR-020, confirmed by diff inspection showing only additive change, if any, at Specification time.

**CanonicalState** - Consumed View: not applicable; pure storage. Temporal Semantics: holds the single current authoritative value at all times. Allowed: storing the six-field Position dict via update_position(); default shape matches published shape (Section 10). Forbidden Mutations: CanonicalState computes neither Position nor Exposure. Source: CanonicalEnforcer's update_position() calls only. Ownership Relationship: Authoritative Owner (Rule OM-006). Error Behaviour: default __init__ shape is now the full six-key FLAT record (Section 10), closing Capability 5. Validation Condition: FR-003, FR-007.

**PositionEngine** - Consumed View: not applicable to itself; it is the source. Temporal Semantics: computes both its own internal working state (across ticks) and the published post-trade value (once per tick). Allowed: full internal mutation of its own instance attributes; computation of Exposure alongside Side, Quantity, Average Entry Price, and last_price. Forbidden Mutations: no direct write to CanonicalState (must go through CanonicalEnforcer, unchanged); Exposure computation must never read Equity, Drawdown, Regime, or any RiskEngine-owned state (FR-004). Source: TradeLifecycleEngine's lifecycle position and the current tick's market price. Ownership Relationship: Computational Authority only (ADR-004). Error Behaviour: Exposure is exactly 0.0 at FLAT, unconditionally, never an exception or NaN (FR-018, Section 8). Validation Condition: FR-002, FR-004, FR-015, FR-018, plus full non-regression of the existing P1-03/P1-03.1/P1-04 FLAT/Open/Scale-In/Partial-Close/Full-Close lifecycle scenarios.

**TradeLifecycleEngine** - Consumed View: none related to Position ownership. Temporal Semantics: independent of Position tick timing; owns only historical lifecycle facts (ADR-003). Allowed: its own existing Trade and LifecycleEvent fields, entirely unchanged; no field is added for Position or Exposure. Forbidden Mutations: no operative Position ownership; no Exposure computation of any kind; no CanonicalState write rights of any kind (unchanged - TradeLifecycleEngine has never had CanonicalState access). Source: not applicable (upstream of Position in the pipeline). Ownership Relationship: Authoritative Owner of immutable lifecycle history only. Error Behaviour: unchanged existing RUNTIME_FAILURE_EVENT machinery. Validation Condition: FR-009, FR-013; confirmed by Specification-time diff inspection that trade_lifecycle.py requires zero changes.

---

## 16. RiskEngine Consumption Boundary

### 16.1 Decision (OQ-004)

RiskEngine's existing position parameter, already passed at its current, unchanged call site (risk = self.risk_engine.check(canonical_state, position, regime)), is **reused, not redesigned**. No new parameter, no new method signature, no new wiring is introduced. This matches the SDA's own prediction (OQ-004 classified NON-BLOCKING, a working fallback already structurally present).

### 16.2 Scope of Required Consumption

ADR-004 requires RiskEngine to "consume Position-derived Exposure," which this architecture interprets, for P2-02A's own narrow scope, as: RiskEngine.check() must be able to read position.get("exposure", 0.0) from its already-available parameter, in a strictly read-only manner. **P2-02A does not require RiskEngine's actual risk-limiting formula, exposure-scaling logic, or any other computation to functionally incorporate this value.** Meaningfully integrating Exposure into RiskEngine's own risk policy is explicitly P2-04's territory (Section 2, Section 28).

### 16.3 Explicit Prohibition

RiskEngine's own returned dict must never introduce a field literally or effectively named "exposure" of any kind, at any nesting level, since doing so would silently recreate the exact naming collision Section 17 resolves. If RiskEngine's own risk-adjusted allocation output requires referencing Position's Exposure for a future (P2-04) purpose, it must do so by reading directly from the position parameter it already receives, never by copying or republishing the value under a new, separately-owned name.

### 16.4 Explicit Scope Boundary Against TD-006 and General RiskEngine Redesign

This architecture makes **zero** change to: RiskEngine's Peak-Equity tracking, RiskEngine's Drawdown computation, RiskEngine's risk-limiting policy, RiskEngine's existing allocation-scaling formula (Section 17.1), or any other line of risk.py beyond the single, narrow addition of reading the already-available position.exposure field. TD-006 (RiskEngine's independent Peak-Equity/Drawdown duplication) remains exactly as logged, untouched, deferred to P2-03/P2-04.

---

## 17. Exposure Naming and Schema Separation

### 17.1 The Confirmed Collision

RiskEngine's existing "exposure" output (top-level CanonicalState.state["exposure"], populated via update_risk()) is, per the FRA and CGA's confirmed code analysis, a risk-adjusted capital-allocation sizing fraction, bounded to [min_exposure, max_exposure], computed from equity, drawdown_ratio, and regime - not a Position-derived market-value quantity in any sense.

### 17.2 Decision (OQ-002)

- **Position-derived Exposure** (Section 7, Section 8) is named **exposure**, nested exclusively inside the canonical Position record: CanonicalState.state["position"]["exposure"]. Its full, unambiguous path is scoped by its containment inside "position."
- **RiskEngine's existing risk-adjusted allocation value** is renamed from the top-level key "exposure" to **risk_allocation_factor**: CanonicalState.state["risk_allocation_factor"]. Its internal computation, formula, bounds, and behavior are entirely unchanged (Section 16.4); only its published key name changes. The term risk_allocation_factor denotes a dimensionless scaling factor and SHALL never represent market exposure.

### 17.3 Justification

Nesting alone (Position's exposure versus a top-level key) already prevents a literal dictionary-key collision, but FR-006 requires an explicit decision, not merely an incidental structural distinction, and leaving the top-level key named "exposure" would perpetuate exactly the semantic ambiguity Gap 2 diagnosed for any reader or future automated consumer scanning CanonicalState's schema. The rename is judged in scope for P2-02A, not RiskEngine redesign, because it changes only a label on an already-existing, already-computed value; RiskEngine's actual policy, formula, and behavior are provably unchanged (Section 16.4).

### 17.4 Transition Compatibility

**No alias and no transition period are required.** Repository-wide search (FRA Section 4, re-confirmed by the CGA) found exactly one consumer of the current top-level "exposure" key besides CanonicalState's own internal storage: PositionSizingEngine, which is confirmed inactive and not invoked anywhere in the active runtime (loop.py, main.py). A direct rename therefore has zero active-runtime consumer impact. Introducing a deprecated alias field would add dead-code-adjacent complexity with no active beneficiary, contrary to the minimality requirement.

### 17.5 PositionSizingEngine

PositionSizingEngine remains inactive and is **not activated** by this architecture (explicit scope protection, Section 2). If a future unit reactivates it, that unit is responsible for updating its reference from risk.get("exposure", 1.0) to risk.get("risk_allocation_factor", 1.0); this is recorded here as a forward-compatibility note, not a current obligation, since PositionSizingEngine is not on the active path today.

### 17.6 Naming Criteria Satisfied

The chosen names are unambiguous (no shared string anywhere in the schema, at any nesting level, refers to two concepts), dimension-bearing (exposure is a monetary notional value; risk_allocation_factor is explicitly named as a factor, signaling a dimensionless ratio), not risk-semantically ambiguous, compatible with later instruments (the extension rule in Section 7.3 does not require a name change), minimal (exactly one field renamed, one field added), and durably maintainable (no alias to eventually retire).

---

## 18. Canonical Publication Model

Publication remains governed by the existing Writer-on-Behalf-Of pattern (Rule OM-003), unchanged in mechanism. CanonicalEnforcer.apply_position() remains the sole path publishing the complete six-field Position record, including Exposure, as one atomic write, once per tick, at the existing Position Update stage (Section 19). No new CanonicalEnforcer method is introduced for Exposure. RiskEngine's renamed risk_allocation_factor continues to be published via the existing, unchanged apply_risk() path.

---

## 19. Information Flow

### 19.1 Verified Current Sequence

Re-traced directly against run_engine/core/loop.py at HEAD b88eae5, RunLoop.step()'s exact call order:

1. apply_runtime_status("RUNNING")
2. state_engine.update(tick)
3. cstate.update_tick(...)
4. regime_classifier.classify(state)
5. cstate.update_regime(regime)
6. position_engine.snapshot() -> position_pre
7. strategy_selector.select(state, regime, position_pre) -> weights
8. apply_strategy_selection(weights)
9. strategy_selector.decide(state, regime, weights) -> decision
10. apply_execution_decision(decision)
11. execution_engine.execute(decision, position_pre) -> execution
12. trade_lifecycle_engine.on_execution(execution, state) -> trade_event
13. trade_lifecycle_engine.current_position() -> lifecycle_position
14. position_engine.update_post_trade(execution, state, lifecycle_position) -> position
15. apply_position(position)
16. pnl_engine.update(trade_event, position_pre["entry_price"]) -> pnl
17. apply_pnl(pnl)
18. equity computation; apply_equity(equity)
19. cstate.get() -> canonical_state
20. risk_engine.check(canonical_state, position, regime) -> risk
21. apply_risk(risk)
22. performance_engine.update(...) -> performance
23. apply_performance_metrics(performance)

### 19.2 Target Sequence

The only change to this sequence is at step 6: position_pre is sourced from cstate.get()["position"] (Section 13) instead of position_engine.snapshot(). Every other step, and their strict order, is unchanged. Step 14 gains an internal computation (Exposure, alongside the existing Side/Quantity/Average-Entry-Price/last_price computation); step 15 publishes the now-six-field dict through the unchanged apply_position() call; step 20 gains the ability for RiskEngine to read position["exposure"] internally, with no change to the call signature.

### 19.3 Flow Segments

- **Pre-trade flow** (steps 1 through 6): concludes with RunLoop capturing the immutable pre-trade Position view from CanonicalState.
- **Execution/lifecycle flow** (steps 7 through 13): unchanged; consumes the pre-trade view (steps 7, 11) and produces the lifecycle-derived input to Position's post-trade computation (step 13).
- **Post-trade flow** (steps 14 through 15): PositionEngine computes the full six-field record, including the Exposure derivation point; CanonicalEnforcer publishes it atomically, the publication point.
- **Consumer read points**: StrategySelector and Executor at steps 7 and 11 (pre-trade view); PnLEngine at step 16 (pre-trade view, entry_price only); RiskEngine at step 20 (post-trade value, including exposure).
- **Failure flow / rejected-execution flow**: when trade_event (step 12) is a RUNTIME_FAILURE_EVENT, step 14 still executes and, per the already-certified P1-04 behavior, leaves Side, Quantity, and Average Entry Price unchanged while last_price still updates unconditionally from the current tick's market observation. Because Exposure is a function of last_price (Section 8), **Exposure's magnitude changes on a rejected tick whenever the market price moved, even though Side, Quantity, and Average Entry Price remain frozen.** This is not a violation of ADR-011: ADR-011 protects the trade-outcome-derived identity fields (Side, Quantity, Average Entry Price) from mutation by a rejected transition; Exposure, like last_price, is a market-observation-derived quantity, not a trade-outcome fact, and the already-ratified P1-04 Architecture decision established exactly this principle for last_price. Exposure's continued tracking of the market on a rejected tick is the direct, intended consequence of composing that already-ratified policy with this document's Section 7/8 definition, not a new decision this document introduces independently.

No new Tick-Complete Snapshot architecture is proposed or assumed by this section; the existing incremental-publication model (ADR-010, unchanged) is preserved exactly.

---

## 20. Failure and Invalid-State Semantics

Rejected transitions never mutate Side, Quantity, or Average Entry Price (Invariant P2-02A-AI-013, unchanged from P1-04). Exposure's market-price-driven magnitude may change on a rejected tick, per Section 19.3, by design, not by omission. Exposure is defined to be exactly 0.0 whenever Quantity is 0.0, for every reachable Position state including FLAT, with no exception, no NaN, and no infinite value possible for any finite Position input (Invariant P2-02A-AI-015; Quantity and last_price are already guaranteed finite and non-negative by the existing, certified PositionEngine and TradeLifecycleEngine quantity-validation machinery, established in P1-03.1).

---

## 21. Determinism and Replay Model

Exposure is a pure function of Side, Quantity, and last_price (Invariant P2-02A-AI-008); identical Position inputs always produce identical Exposure outputs, with no dependency on Equity, Drawdown, Regime, or any other mutable, non-Position runtime state. Because Exposure is stored as part of the canonical Position record (Section 11, Option C) rather than computed on demand by each reader, a historical CanonicalState snapshot at any past tick already contains the historical Exposure value directly, without requiring re-invocation of the derivation logic or dependency on which version of that logic exists at replay time - a stronger replay guarantee than a pure-projection model would provide.

---

## 22. Compatibility and Migration Model

No alias fields are introduced (Section 17.4). No transition period is required, since the only affected consumer of the renamed key is already confirmed inactive. Every already-certified P1-03, P1-03.1, P1-04, and P2-01 contract - RuntimeFailureEvent determinism, rejection non-mutation of Side/Quantity/Average-Entry-Price, Scale-In weighted-average entry price, Partial Close and Full Close semantics, mark-price-on-rejection policy, and entry_basis pre-trade timing - is preserved exactly, with the sourcing change in Section 13 producing byte-identical results under the current execution model (Section 13.5). No migration script, data conversion, or backward-compatibility shim is required, since this is a pre-existing, unreleased development branch with no external persisted state to migrate.

---

## 23. Architecture Decisions

### P2-02A-AD-001: Exposure Semantics

Decision: Position-derived Exposure is the signed current market value of the operative Position (Section 7.3).
Status: Accepted.
Context: OQ-001, the FRA/SDA's single BLOCKING open question; Gap 2 (FRA Section 9), Capabilities 6, 7, 8 (CGA).
Considered Alternatives: unsigned current market value, absolute nominal exposure, committed capital / entry-basis notional, quantity-only exposure, risk-adjusted exposure, delta exposure, alternative minimal definitions (Section 7.1).
Chosen Alternative: signed current market value (quantity times last_price times a LONG-positive/SHORT-negative sign).
Scientific Rationale: reflects current market conditions (uses last_price, not a frozen cost basis); self-descriptive of direction without redundant lookups; requires no non-Position data; matches the already-certified PnL sign convention; dimensionally sound (quote-currency notional).
Architectural Rationale: satisfies ADR-004's Decision text and Acceptance Criteria without introducing any new Authoritative Owner or Computational Authority; requires zero new instrument metadata for the active BTCUSDT scope (resolves SDA Dependency P2-02A-DEP-013 as not triggered).
Consequences: PositionEngine's Exposure computation depends only on already-available Side, Quantity, last_price.
Rejected Alternatives: Section 7.1, each with its specific rejection reason.
Related FRA Requirements: FR-001, FR-004, FR-015, FR-018.
Related SDA Dependencies: P2-02A-DEP-001, P2-02A-DEP-002, P2-02A-DEP-013.
Related Capabilities: 6, 7, 8.
Validation Obligations: FR-015 (pure function), FR-018 (well-defined at FLAT), re-verified per Section 21.
Scope Boundaries: does not require, propose, or activate any instrument metadata capability.

### P2-02A-AD-002: Exposure Dimensionality and Sign

Decision: Exposure's unit is quote currency; sign is +1 for LONG, -1 for SHORT; value is exactly 0.0 at FLAT, unconditionally (Section 8).
Status: Accepted.
Context: completes AD-001's semantic definition with precise dimensional and sign rules, as separately required by the governing task.
Considered Alternatives: unsigned magnitude with separate Side lookup; a dimensionless ratio.
Chosen Alternative: signed, quote-currency-denominated value with an explicit, unconditional FLAT rule.
Scientific Rationale: matches the already-certified PnLEngine sign convention; avoids any implicit multiplication-by-None failure mode at FLAT.
Architectural Rationale: supports FR-018's determinism-at-FLAT requirement by construction, not by incidental behavior.
Consequences: implementers must treat the FLAT case as an explicit branch, not an emergent multiplication result.
Rejected Alternatives: unsigned magnitude (Section 7.1); dimensionless ratio (would not describe a market-value quantity).
Related FRA Requirements: FR-004, FR-015, FR-018.
Related SDA Dependencies: P2-02A-DEP-002.
Related Capabilities: 6, 7, 8.
Validation Obligations: exposure equals 0.0 exactly whenever quantity equals 0.0, for every code path.
Scope Boundaries: none beyond AD-001's.

### P2-02A-AD-003: Storage versus Projection

Decision: Exposure is a stored member of the canonical Position record, recomputed and republished atomically with every other Position field, with no independent write path (Section 11, Option C).
Status: Accepted.
Context: OQ-006, CONDITIONALLY BLOCKING per the SDA; Capability 9 (CGA).
Considered Alternatives: independently stored field with no enforced reconstruction rule (Option A); pure computed projection, never stored (Option B); the adopted stored-with-binding-reconstruction-rule variant (Option C).
Chosen Alternative: Option C.
Scientific Rationale: matches ADR-004's textual framing of Exposure as a Position member while fully satisfying the Derived View definition's "no independent ownership" requirement through enforced, atomic co-computation.
Architectural Rationale: drift/staleness risk is architecturally prevented as long as publication occurs exclusively through the defined canonical write path; improves Tick-Complete Snapshot compatibility; adds zero new write paths.
Consequences: CanonicalState's schema gains exactly one nested key, no new top-level key, no new CanonicalEnforcer method.
Rejected Alternatives: Option A (insufficiently enforced against independent mutation); Option B (increases coupling to derivation logic across consumers; degrades replay completeness).
Related FRA Requirements: FR-005, FR-007.
Related SDA Dependencies: P2-02A-DEP-004, P2-02A-DEP-010.
Related Capabilities: 9.
Validation Obligations: Exposure's value at every observed CanonicalState snapshot equals fresh recomputation from that same snapshot's Side/Quantity/last_price.
Scope Boundaries: does not propose any Tick-Complete Snapshot architecture; only notes compatibility.

### P2-02A-AD-004: Canonical Position Shape

Decision: the canonical Position record has exactly six fields - position, side, quantity, entry_price, last_price, exposure - identical in default and published shape (Section 10).
Status: Accepted.
Context: Capability 5 (CGA), the one capability confirmed unblocked by any dependency.
Considered Alternatives: removing position in favor of side alone; adding new fields beyond the six required; leaving the default/published shape mismatch unresolved.
Chosen Alternative: retain both position and side for compatibility, with position formally declared a Derived View of side; fix the default-shape mismatch exactly to the six-field FLAT record.
Scientific Rationale: position and side are logically redundant (position equals "FLAT" if and only if side is None) but the redundancy is already deeply embedded in every certified consumer; removing it would be a breaking, unnecessary schema change.
Architectural Rationale: "no unnecessary schema expansion" is satisfied by adding only Exposure and by formalizing, not restructuring, the position/side relationship.
Consequences: a future unit may normalize position away; this architecture does not perform that normalization.
Rejected Alternatives: removing position (breaking, unnecessary); leaving the shape mismatch unresolved (leaves Capability 5 open).
Related FRA Requirements: FR-001, FR-003.
Related SDA Dependencies: P2-02A-DEP-004.
Related Capabilities: 1, 2, 5.
Validation Obligations: CanonicalState's default dict and any published dict have identical key sets and types, at every point in the process lifetime.
Scope Boundaries: no new fields beyond the six specified; no removal of existing fields.

### P2-02A-AD-005: Pre-Trade Derived View

Decision: RunLoop captures an explicit, immutable pre-trade Position view, sourced exclusively from CanonicalState, at the start of each tick, before any Regime/Strategy/Execution/Lifecycle processing (Section 13).
Status: Accepted.
Context: OQ-003, CONDITIONALLY BLOCKING per the SDA; TD-001; Capabilities 2, 3, 10, 11, 13 (CGA).
Considered Alternatives: explicit copy from CanonicalState (Option A); PositionEngine.snapshot() formally redefined as a Derived View (Option B); RunLoop-held explicit immutable value (Option C, adopted jointly with A); other minimal variant (Option D).
Chosen Alternative: Options A and C together.
Scientific Rationale: establishes that pre-trade and post-trade are temporal projections of one canonical entity, not two entities, consistent with the Architecture Baseline's Derived View definition and Rule OM-001.
Architectural Rationale: eliminates the dual-physical-object pattern entirely (unlike Option B, which would only relabel it), most cleanly satisfying Rule OM-006.
Consequences: PositionEngine's own instance state becomes purely internal working state, no longer an external read API for other components.
Rejected Alternatives: Option B, judged architecturally weaker (Section 13.2).
Related FRA Requirements: FR-008, FR-012, FR-019.
Related SDA Dependencies: P2-02A-DEP-005, P2-02A-DEP-006.
Related Capabilities: 2, 3, 10, 11, 13.
Validation Obligations: byte-identical entry_basis and lifecycle results versus the certified P1-03.1/P1-04 scenarios (Section 13.5).
Scope Boundaries: does not remove or rename PositionEngine's internal computation methods; only its role as an external source.

### P2-02A-AD-006: Canonical Read Path

Decision: StrategySelector, Executor, and PnLEngine's entry_basis input read the pre-trade view (AD-005); RiskEngine reads the post-trade value via its existing parameter (Section 14).
Status: Accepted.
Context: operationalizes AD-004 and AD-005 across every real consumer; Capabilities 10, 13.
Considered Alternatives: none beyond what AD-005 already establishes; this decision is the direct consequence of AD-004 and AD-005 applied to each consumer.
Chosen Alternative: as stated.
Scientific Rationale: Rule OM-001 requires exactly one canonical source; this decision names, per consumer, which temporal projection of that one source each is entitled to.
Architectural Rationale: closes TD-001 completely for all four real consumers.
Consequences: three consumer call sites change their Position source; RiskEngine's call site is unchanged in signature.
Rejected Alternatives: none additional.
Related FRA Requirements: FR-007, FR-008, FR-012.
Related SDA Dependencies: P2-02A-DEP-007, P2-02A-DEP-009.
Related Capabilities: 10, 13.
Validation Obligations: exactly one Position read path per consumer, traced to AD-004/AD-005's canonical source, confirmed at Specification/Implementation time.
Scope Boundaries: does not change any consumer's own Computational Authority or output semantics beyond its Position source.

### P2-02A-AD-007: Exposure Naming Separation

Decision: Position-derived Exposure is named exposure, nested inside the canonical Position record; RiskEngine's existing allocation value is renamed from the top-level exposure key to risk_allocation_factor (Section 17).
Status: Accepted.
Context: OQ-002; the confirmed naming collision (FRA Section 7, Gap 2); Capability 15.
Considered Alternatives: leave both values named "exposure," relying only on nesting-level separation; rename only Position's value; rename only RiskEngine's value (adopted); introduce an alias/transition period.
Chosen Alternative: rename RiskEngine's top-level key to risk_allocation_factor; no alias.
Scientific Rationale: the two concepts are dimensionally and semantically distinct (Section 17.1); a durable, explicit name change is more scientifically honest than relying on structural nesting alone.
Architectural Rationale: narrow, mechanical rename with zero change to RiskEngine's actual computation (Section 16.4); zero active-consumer impact (Section 17.4).
Consequences: canonical_state.py's update_risk() and its schema default gain a renamed key; risk.py's own internal variable names are unaffected (implementation detail, deferred to Specification).
Rejected Alternatives: relying on nesting alone (does not satisfy FR-006's requirement for an explicit decision); renaming Position's Exposure instead (would fight ADR-004's own terminology); an alias period (unnecessary given zero active consumers).
Related FRA Requirements: FR-005, FR-006.
Related SDA Dependencies: P2-02A-DEP-003, P2-02A-DEP-010.
Related Capabilities: 15.
Validation Obligations: no field named "exposure" exists anywhere in CanonicalState's schema except inside the Position record; PositionSizingEngine remains uninvoked.
Scope Boundaries: does not activate PositionSizingEngine; does not alter RiskEngine's allocation formula.

### P2-02A-AD-008: RiskEngine Consumption Boundary

Decision: RiskEngine reuses its existing, currently unused position parameter to read position.exposure, read-only, with no new parameter and no functional requirement to use the value in its own risk formula in this unit (Section 16).
Status: Accepted.
Context: OQ-004, NON-BLOCKING per the SDA; ADR-004's verbatim RiskEngine requirement; Capability 14; TD-006 boundary.
Considered Alternatives: a new, smaller immutable Exposure-only view passed separately; requiring RiskEngine to functionally incorporate Exposure into its risk-limiting formula now; the adopted reuse-and-read-only approach.
Chosen Alternative: reuse the existing parameter; read-only consumption; no mandated functional use.
Scientific Rationale: ADR-004 requires consumption, not a specific use; a narrower obligation is sufficient and avoids prematurely deciding P2-04's risk-formula design.
Architectural Rationale: zero new wiring; lowest possible implementation risk; preserves the explicit TD-006/P2-04 scope boundary (Section 16.4).
Consequences: RiskEngine.check() gains exactly one internal read; its signature, return shape (apart from the rename in AD-007), and formula are unchanged.
Rejected Alternatives: a new parameter (unnecessary, since the existing one already carries Position); mandating functional use now (would pull P2-04's scope into P2-02A).
Related FRA Requirements: FR-010, FR-011.
Related SDA Dependencies: P2-02A-DEP-008, P2-02A-DEP-009, P2-02A-DEP-012.
Related Capabilities: 14.
Validation Obligations: RiskEngine.check()'s Peak-Equity/Drawdown-related lines remain byte-for-byte unchanged; RiskEngine's own return dict never introduces an "exposure"-named field.
Scope Boundaries: explicitly excludes Peak Equity, Drawdown ownership, risk-limiting policy, and Position Sizing logic (all TD-006/P2-04).

### P2-02A-AD-009: Compatibility and Migration Policy

Decision: no alias fields, no transition period, no data migration; every already-certified P1-03/P1-03.1/P1-04/P2-01 contract is preserved exactly, verified by re-running its existing certified scenarios (Section 22).
Status: Accepted.
Context: Cluster I (SDA); Capability 16 (CGA); the governing task's compatibility requirements.
Considered Alternatives: a deprecation-period alias for the renamed RiskEngine key (rejected, Section 17.4); a versioned schema flag (rejected as unnecessary complexity for a pre-release development branch).
Chosen Alternative: direct, unconditional application of AD-001 through AD-008, with full regression re-verification.
Scientific Rationale: no external persisted state exists to migrate; the branch is pre-certification for this unit.
Architectural Rationale: minimality; avoids introducing compatibility-shim complexity this project's stated principles (IP-002, Architectural Philosophy) discourage.
Consequences: Specification and Implementation stages must re-run the full existing certification suite (manual, per TD-005) alongside any new P2-02A-specific validation.
Rejected Alternatives: alias/versioning approaches, as stated.
Related FRA Requirements: FR-013, FR-014, FR-016, FR-017, FR-019, FR-020.
Related SDA Dependencies: P2-02A-DEP-011.
Related Capabilities: 16.
Validation Obligations: full non-regression across all four prior certification chains (P1-03, P1-03.1, P1-04, P2-01).
Scope Boundaries: does not introduce any new persistence, versioning, or migration mechanism (ADR-012 Deferred Scope, unaffected).

---

## 24. Architecture Invariants

**P2-02A-AI-001** - Exactly one authoritative Position value exists at any point in time: CanonicalState.state["position"].

**P2-02A-AI-002** - PositionEngine is the exclusive Computational Authority for Position and for Exposure; no other component computes either.

**P2-02A-AI-003** - CanonicalState is the exclusive Authoritative Owner of the canonical Position, including Exposure.

**P2-02A-AI-004** - CanonicalEnforcer.apply_position() is the sole Writer-on-Behalf-Of path for publishing Position and Exposure; no second write path exists.

**P2-02A-AI-005** - The pre-trade Position view is a temporal Derived View of the single canonical Position, not a second ownership path; it is sourced exclusively from CanonicalState, never from PositionEngine's live instance state.

**P2-02A-AI-006** - The post-trade Position, published at the end of each tick's Position Update stage, is the canonical tick-end state and becomes the pre-trade view of the next tick.

**P2-02A-AI-007** - Exposure is not an independent runtime entity; it exists exclusively as a computed member of the canonical Position record.

**P2-02A-AI-008** - Exposure is a deterministic, pure function of Side, Quantity, and last_price; identical Position inputs always produce identical Exposure outputs.

**P2-02A-AI-009** - Exposure is exactly 0.0 whenever Quantity is 0.0 (FLAT), unconditionally.

**P2-02A-AI-010** - RiskEngine's risk-adjusted allocation value (risk_allocation_factor) is semantically and nominally distinct from Position-derived Exposure at every level of the CanonicalState schema; no field named "exposure" exists anywhere outside the canonical Position record.

**P2-02A-AI-011** - RiskEngine owns neither Position nor Exposure; its consumption of both is strictly read-only.

**P2-02A-AI-012** - TradeLifecycleEngine owns no operative Position or Exposure information.

**P2-02A-AI-013** - The already-certified P1-03/P1-03.1/P1-04/P2-01 contracts (entry_basis pre-trade timing, rejection non-mutation of Side/Quantity/Average Entry Price, Scale-In weighted-average entry price, Partial Close/Full Close semantics, mark-price-on-rejection policy) remain unchanged by this architecture.

**P2-02A-AI-014** - No hidden mutation of Position or Exposure occurs outside PositionEngine's own computation and CanonicalEnforcer's publication.

**P2-02A-AI-015** - Exposure is never NaN or infinite, for any reachable Position state.

**P2-02A-AI-016** - CanonicalState's default (pre-first-tick) Position shape and the post-tick published Position shape are identical in key set and type, for every key including Exposure.

---

## 25. FRA Requirement Traceability

| Requirement | Governing Architecture Decision(s) |
|---|---|
| FR-001 | AD-001, AD-004 |
| FR-002 | AD-004, AD-005 (Section 15, PositionEngine contract) |
| FR-003 | AD-004 |
| FR-004 | AD-001, AD-002 |
| FR-005 | AD-003, AD-007 |
| FR-006 | AD-007 |
| FR-007 | AD-004, AD-006 |
| FR-008 | AD-005, AD-006 |
| FR-009 | Section 15 (TradeLifecycleEngine contract, unchanged) |
| FR-010 | AD-008 |
| FR-011 | AD-008 |
| FR-012 | AD-005, AD-006 |
| FR-013 | AD-009, Section 20 |
| FR-014 | AD-009, Section 15 |
| FR-015 | AD-001, AD-002, Section 21 |
| FR-016 | AD-005, Section 15 (StrategySelector/Executor validation conditions) |
| FR-017 | AD-009, Section 20 |
| FR-018 | AD-002, Section 20 |
| FR-019 | AD-005, Section 13.4, Section 15 (PnLEngine contract) |
| FR-020 | AD-004, Section 18 |

All twenty FRA requirements are governed by at least one Architecture Decision.

---

## 26. SDA Dependency Conformance

| Dependency | Conformance |
|---|---|
| P2-02A-DEP-001 (A to B, HARD) | Satisfied - A already complete; B resolved by AD-001. |
| P2-02A-DEP-002 (B to C, HARD) | Satisfied - AD-001 (semantics) precedes AD-002/AD-003 (mechanics) in this document's own decision ordering. |
| P2-02A-DEP-003 (B to G, SOFT) | Satisfied - AD-001 informs AD-007's naming choice. |
| P2-02A-DEP-004 (C/OQ-006 to D2, CONDITIONAL) | Satisfied - AD-003 informs AD-004's final shape. |
| P2-02A-DEP-005 (E to D2, HARD) | Satisfied - AD-005 precedes and informs AD-004's ownership finalization and AD-006. |
| P2-02A-DEP-006 (E to F, HARD) | Satisfied - AD-005 precedes AD-006. |
| P2-02A-DEP-007 (D to F, HARD) | Satisfied - AD-004 precedes AD-006. |
| P2-02A-DEP-008 (C to H, HARD) | Satisfied - AD-001/AD-003 precede AD-008. |
| P2-02A-DEP-009 (F to H, CONDITIONAL) | Satisfied - AD-006 precedes AD-008; RiskEngine's read sourced from the same consolidated pattern. |
| P2-02A-DEP-010 (G/OQ-006 to D2, SOFT) | Satisfied - AD-003 and AD-007 jointly inform the final key name and nesting location. |
| P2-02A-DEP-011 (I, cross-cutting, HARD) | Satisfied throughout via AD-009 and Section 22/29-32's reviews. |
| P2-02A-DEP-012 (H to external TD-006 boundary, HARD) | Respected - AD-008.4 (Section 16.4) explicitly excludes TD-006. |
| P2-02A-DEP-013 (C to external instrument-metadata capability, CONDITIONAL) | **Resolved as not triggered** - AD-001's chosen semantics requires no instrument metadata for the active BTCUSDT scope; no external prerequisite capability is introduced. |

All thirteen SDA dependencies are either satisfied by this document's decision ordering or explicitly resolved as not triggered.

---

## 27. CGA Gap Closure Mapping

| Capability | Prior Status | Closure |
|---|---|---|
| 1. Position Semantics | PARTIAL | Closed - AD-001 completes the four-member tuple. |
| 2. Position Representation | PARTIAL | Closed - AD-005/AD-006 establish a single representation. |
| 3. Position Ownership | PARTIAL | Closed - AD-005 removes the dual-state pattern. |
| 4. Position Publication | COMPLETE | Unchanged; already satisfied. |
| 5. Canonical Position Shape | MISSING | Closed - AD-004. |
| 6. Position-derived Exposure | MISSING | Closed - AD-001, AD-002, AD-003. |
| 7. Exposure Semantics | MISSING | Closed - AD-001. |
| 8. Exposure Derivation | MISSING | Closed - AD-001, AD-002 (pure function fully defined). |
| 9. Exposure Storage / Projection | MISSING | Closed - AD-003. |
| 10. Runtime Consumer Access | PARTIAL | Closed - AD-006. |
| 11. Pre-Trade Snapshot | PARTIAL | Closed - AD-005. |
| 12. Post-Trade Snapshot | COMPLETE | Unchanged; already satisfied. |
| 13. Canonical Read Path | MISSING | Closed - AD-006. |
| 14. RiskEngine Consumption | MISSING | Closed - AD-008. |
| 15. Exposure Naming Separation | PARTIAL | Closed - AD-007. |
| 16. Compatibility Constraints | COMPLETE | Preserved and re-verified - AD-009. |
| 17. Validation Infrastructure | NOT APPLICABLE (to P2-02A) | Remains deferred - TD-005, unchanged, correctly out of scope. |

Sixteen of seventeen capabilities are closed or preserved by this architecture; the seventeenth (Validation Infrastructure) correctly remains a project-wide, out-of-scope item, consistent with the CGA's own conclusion.

---

## 28. External and Deferred Dependencies

- TD-006 (RiskEngine Peak-Equity/Drawdown ownership duplication) - untouched; AD-008 explicitly excludes it.
- P2-03 (Financial Ownership Consolidation) - future compatibility constraint only; AD-001's exclusion of Equity/Drawdown as Exposure inputs removes any foreseeable conflict.
- P2-04 (Risk Ownership Consolidation) - deferred; RiskEngine's functional use of Exposure in its own risk-limiting logic, and TD-006's resolution, remain P2-04's scope.
- TD-007 (Lifecycle Control Surface) - no dependency; unrelated.
- ADR-010 / Phase 3 (Tick-Complete Snapshot architecture) - future compatibility constraint; AD-003's storage decision is compatible with, but does not anticipate or design, that future architecture.
- PositionSizingEngine activation (OQ-005) - remains DEFERRED OUT OF SCOPE, per the governing task; not activated by this architecture (Section 17.5).
- Repository cleanup (position_sizing.py, equity_stabilizer.py, run_engine/runtime/) - deferred to Phase 6; unaffected.
- TD-005 (automated regression test suite) - deferred, project-wide; Capability 17 remains correctly out of scope (Section 27).
- Instrument Registry / instrument metadata - **not required**; AD-001 confirms the chosen Exposure semantics needs no instrument metadata for the active BTCUSDT scope, so SDA Dependency P2-02A-DEP-013 is resolved as not triggered and no external prerequisite is introduced.

---

## 29. Removal Test

Removing AD-001 (Exposure Semantics) leaves Capabilities 6, 7, 8, and transitively 9, 14, 15, permanently unresolvable - fails the Removal Test, confirming AD-001's necessity. Removing AD-005 (Pre-Trade Derived View) leaves TD-001 unresolved and FR-008/FR-019 in unresolved tension - fails the Removal Test. Every other Architecture Decision was checked the same way during drafting (Sections 7 through 18); none was found removable without leaving at least one FRA requirement, SDA dependency, or CGA capability gap unclosed. AD-009 (Compatibility and Migration Policy) is the sole decision whose removal would not reopen a gap but would remove the explicit verification obligation protecting against regression - still necessary, as a safeguard rather than a gap-closer.

---

## 30. Compression Test

AD-001 and AD-002 (Exposure Semantics and Dimensionality/Sign) are closely related but not merged, since the governing task requires them as separate, explicitly documented decisions, and because the semantic question (what Exposure represents) and the dimensional/sign question (how it is expressed numerically) are logically separable, matching the SDA's own finding that conflating "what" and "how" is a documented failure mode (SDA Section 8). AD-006 (Canonical Read Path) is not merged into AD-005 (Pre-Trade Derived View), since AD-005 establishes the temporal classification while AD-006 operationalizes it per consumer - the same separation already justified in the SDA (Cluster E versus Cluster F). No pair of the nine Architecture Decisions was found fully compressible into one without losing independently-traceable justification for a distinct FRA requirement or SDA dependency.

---

## 31. Counterfactual Review

Without AD-001, ADR-004 compliance for Exposure cannot be claimed under any circumstance, only assumed. Without AD-005, RunLoop's dual-state pattern would need to be "resolved" by an ad hoc, undocumented mechanism, reintroducing exactly the risk the SDA's Section 10 "Failure if Introduced Too Early" already warned against (silently breaking the certified entry_basis contract). Without AD-007, the naming collision persists indefinitely, regardless of how correctly AD-001 through AD-006 are implemented. No Architecture Decision in this document was found to be replaceable by a scientifically or architecturally simpler alternative that still satisfies its governing FRA requirements; where a simpler alternative existed, it was adopted (for example, AD-008's decision to reuse rather than redesign RiskEngine's parameter).

---

## 32. Scope Integrity Review

No decision in this document extends into P2-03 (Financial Ownership), P2-04 (full Risk Ownership), TD-006 beyond the narrow read boundary of AD-008, general RiskEngine policy, full Position Sizing logic, PositionSizingEngine activation, the Lifecycle Control Surface, the Tick-Complete Snapshot architecture, repository cleanup, or the automated test suite. AD-001 explicitly confirms no Instrument Registry capability is required, closing the one scope-expansion risk the governing task specifically flagged as conditional. Every Architecture Decision's "Scope Boundaries" field (Section 23) independently confirms this same constraint at the level of that individual decision.

---

## 33. Architecture Readiness Decision

Every Open Question the FRA identified as requiring resolution before Specification work begins has been explicitly decided: OQ-001 (AD-001), OQ-002 (AD-007), OQ-003 (AD-005), OQ-004 (AD-008), OQ-006 (AD-003). OQ-005 remains explicitly DEFERRED OUT OF SCOPE, per the governing task, and is not activated anywhere in this document. All twenty FRA requirements, all thirteen SDA dependencies, and all seventeen CGA capabilities are traced to at least one Architecture Decision or explicitly confirmed as already satisfied or correctly out of scope.

**Architecture Readiness: READY.** This document is sufficient to proceed to the P2-02A Specification. No further architectural investigation, and no additional Open Question resolution, is required before that step.

---

## 34. Internal Consistency Review

**Terminology consistency** - "Position," "Exposure," "Authoritative Owner," "Computational Authority," "Writer-on-Behalf-Of," and "Derived View" are used exactly as defined in the Architecture Baseline and the FRA/SDA/CGA throughout this document. "Exposure" unqualified always refers to Position-derived Exposure (Section 7); RiskEngine's value is always referred to as risk_allocation_factor from Section 17 onward.

**Dimensionality consistency** - Exposure's unit (quote currency) and sign convention (Section 8) are referenced identically in every subsequent section that discusses it (Sections 9 through 21); no section attributes a different unit or sign rule.

**Ownership consistency** - every field's ownership triple (Computational Authority PositionEngine, Authoritative Owner CanonicalState, Writer-on-Behalf-Of CanonicalEnforcer) is stated identically in Section 10 and is never contradicted elsewhere; no new Authoritative Owner or Computational Authority is introduced anywhere in this document, satisfying Rule OM-009 (no new Authoritative Owner without an Architecture Evolution Review - none is proposed).

**Information-flow consistency** - Section 19's target sequence changes exactly one step (step 6's source) relative to the verified current sequence (Section 19.1); no other step is added, removed, or reordered anywhere in this document.

**Temporal-semantics consistency** - Section 13's pre-trade/post-trade model is applied identically in Sections 14, 15, 19, and 20; no section describes pre-trade and post-trade as separate entities anywhere, consistent with Section 13.1's central clarification.

**Dependency conformance** - Section 26 confirms all thirteen SDA dependencies without introducing a new, unrecorded dependency anywhere else in the document.

**Naming-collision consistency** - after Section 17, no subsequent section uses the string "exposure" to refer to RiskEngine's allocation value; Section 16 and Section 20 both use risk_allocation_factor or "RiskEngine's allocation value" exclusively when that meaning is intended.

**Scope consistency** - Section 32's Scope Integrity Review is corroborated by every individual Architecture Decision's own Scope Boundaries field; no contradiction was found between the two.

**ID uniqueness** - P2-02A-AD-001 through P2-02A-AD-009 and P2-02A-AI-001 through P2-02A-AI-016 are each defined exactly once (Sections 23 and 24 respectively) and referenced only by ID thereafter; no ID collision or reuse was introduced.

**Traceability completeness** - Section 25 confirms all twenty FRA requirements; Section 26 confirms all thirteen SDA dependencies; Section 27 confirms all seventeen CGA capabilities; cross-checked against Sections 7 through 22 during drafting.

Status: Internal Consistency Review PASS.
