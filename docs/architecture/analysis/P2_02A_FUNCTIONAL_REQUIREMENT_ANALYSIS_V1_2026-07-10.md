Document Class:
Functional Requirement Analysis

Document ID:
P2-02A-FRA

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
docs/architecture/analysis/P2_02A_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-10.md

Depends On:
- docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md
- docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md
- ADR-004 (Position Represents Current Market Exposure), within the Architecture Baseline above
- docs/architecture/certification/P1_04_FINAL_CERTIFICATION_V1_2026-07-09.md
- docs/architecture/certification/P2_01_FINAL_CERTIFICATION_V1_2026-07-10.md
- docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md
- current runtime code at HEAD b88eae5

Referenced By:
- future P2-02A Scientific Dependency Analysis
- future P2-02A Capability Gap Analysis
- future P2-02A Architecture
- future P2-02A Specification
- future P2-02A Certification

---

# P2-02A Functional Requirement Analysis

## 1. Purpose

This document performs the Functional Requirement Analysis for P2-02A (Position Ownership), the unit named directly after P2-02 (Runtime Status Consolidation, certified complete) in the approved Phase 2 sequence of RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md.

This document does not decide architecture. It does not define interfaces. It does not implement code. Its sole purpose is to establish, from direct repository inspection, the verified current state of Position and Exposure ownership, and to derive the functional requirements that a later Architecture document must satisfy.

---

## 2. Scope

In scope: operative Position, Position ownership, Position projection, Position publication in CanonicalState, Position-derived Exposure, and the consumer contracts for Position and Exposure across the active runtime.

Out of scope (see Section 20 for full detail): full PnL/Equity/Peak-Equity consolidation (P2-03), full RiskEngine consolidation beyond what ADR-004 directly requires of it (P2-04 and the already-logged TD-006), the lifecycle control surface (TD-007), the complete Tick-Complete Snapshot architecture (Phase 3 / ADR-010), general repository cleanup, and technical debt not directly implicated by Position/Exposure ownership.

---

## 3. Binding Architectural Baseline

- docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md - ADR-004 ("Position Represents Current Market Exposure"), the Runtime Ownership Matrix, Rules OM-001 through OM-009, Architecture Invariants AI-001 through AI-015.
- docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md - Phase 2 Implementation Units, specifically the P2-02A entry: "Position Ownership. Objectives: Implement ADR-004 Position ownership. Verify Position as the authoritative operational runtime entity. Verify that Exposure remains a Position property and never becomes an independent runtime object."
- docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md - TD-001 (Canonical Position Source for PnLEngine, Target Phase P2/P2-02A), TD-002 (unify _safe_float, Target Phase P2), TD-003 (document pre-trade snapshot dependency), TD-006 (RiskEngine Peak Equity/Drawdown duplication, Target Phase P2-03/P2-04), TD-007 (RunLoop lifecycle control surface, deferred).

ADR-004's binding text, quoted for traceability:

"Position represents the current operational market state. A Position consists of: Side, Quantity, Average Entry Price, Current Exposure. Position describes only the current operational runtime situation. Position never represents historical execution."

"Exposure is not an independent runtime entity. Exposure is a quantitative property of Position. Exposure therefore possesses no independent architectural ownership. Every runtime component requiring Exposure shall derive it directly from Position."

"PositionEngine SHALL become the exclusive Computational Authority for Position evolution. CanonicalState SHALL become the Authoritative Owner of the canonical Position. Exposure SHALL always be derived from Position. RiskEngine SHALL consume Position-derived Exposure. RiskEngine SHALL never maintain an independent canonical Exposure representation. TradeLifecycleEngine SHALL remain completely independent from operational Position management."

Acceptance Criteria (ADR-004): "Exactly one canonical Position exists. Exposure never exists independently from Position. RiskEngine never owns Position. RiskEngine never owns Exposure. TradeLifecycleEngine never owns operational Position. CanonicalState contains the authoritative operational Position."

---

## 4. Verified Repository and Runtime Baseline

Repository state, verified directly, not assumed:

- Branch: run-engine-consolidation-safety (confirmed via git branch --show-current).
- HEAD: b88eae5 ("Implement P2-02 runtime status consolidation"), matching the stated starting point exactly (confirmed via git rev-parse HEAD and git log --oneline -1).
- Working tree: one modified file unrelated to run_engine (docs/capabilities/SGF_013_SCIENTIFIC_BEHAVIOUR_REPRESENTATION_2026-06-26.md) and a set of pre-existing untracked directories (_chat_handover/, _sgf017_context/, _ssi_context/, backups/, claude_final_p1031_review/, claude_p1031_patch/, claude_p1_03b_review/, codex_p1_03_review/, engine/regime_classifier.py, live_logs/, outputs/, review_packages/, runtime_runs/) - all pre-existing from prior sessions, none inside run_engine/, none touched by this analysis. run_engine/ and docs/architecture/ are clean.
- All three baseline documents named in Section 3 confirmed present at their stated paths.

File-path correction (repository-grounded, not assumed): the task description names position_engine.py, risk_engine.py, pnl_engine.py, trade_lifecycle_engine.py, and run_loop.py. Direct enumeration of run_engine/core/*.py confirms the actual filenames are position.py, risk.py, pnl.py, trade_lifecycle.py, and loop.py, each containing a class named PositionEngine, RiskEngine, PnLEngine, TradeLifecycleEngine, and RunLoop respectively. This document analyzes the actual files; the class names match the task description even where the filenames do not.

Additional active-path files identified during this analysis, not named in the task description: run_engine/core/canonical_state.py, run_engine/core/canonical_enforcer.py, run_engine/core/strategy.py, run_engine/core/execution/executor.py, run_engine/core/performance.py, run_engine/main.py - all confirmed either imported by RunLoop (loop.py) or by main.py, and therefore part of the Verified Active Execution Path.

Files found but confirmed inactive (not imported anywhere in the active path):

- run_engine/core/position_sizing.py (PositionSizingEngine) - confirmed by repository-wide search: no import of PositionSizingEngine exists anywhere under run_engine/core, including loop.py.
- run_engine/core/equity_stabilizer.py (EquityStabilizer) - same result, confirmed unused.
- run_engine/runtime/position_state.py (PositionState) and run_engine/runtime/risk.py (RiskLayer) - confirmed by repository-wide search: no file under run_engine/core or run_engine/main.py imports anything from run_engine.runtime. This matches the Architecture Baseline's own diagnosis (AD-007, "Parallel Runtime Architectures") that run_engine/runtime/ is a competing, inactive implementation outside the current consolidation scope.
- engine/regime_classifier.py (top-level, untracked) - confirmed unrelated: no file under run_engine/ imports from a top-level engine package, and this file is not imported by anything found in the repository.

Test files: a repository-wide search for run_engine.core, PositionEngine, or CanonicalState inside tools/test_*.py and live_l1/tools/test_*.py returns zero matches. These test files belong to a separate subsystem (timing, monitor failure injection, operational profiles) unrelated to the Run Engine consolidation project. No test coverage of run_engine/core exists anywhere in the repository, consistent with TD-005 (Automated Regression Test Suite, still open).

---

## 5. Scientific Definitions

These definitions are restated from ADR-004 and the Architecture Baseline, not newly invented, and govern the rest of this document.

Position - the current operational market state, consisting of Side, Quantity, Average Entry Price, and Current Exposure. Position never represents historical execution.

Exposure - a quantitative property derived from Position. Exposure possesses no independent architectural ownership and no independent runtime existence.

PositionEngine - the exclusive Computational Authority for Position evolution (ADR-004). Computation, not ownership.

CanonicalState - the Authoritative Owner of the canonical Position (ADR-004, ADR-001, Rule OM-006).

TradeLifecycleEngine - owner of immutable historical trade evolution; explicitly independent from operational Position management (ADR-004, ADR-003).

Risk Metrics - derived quantities computed by RiskEngine from canonical runtime state (ADR-007), a distinct category from Position/Exposure.

Financial quantities (Realized PnL, Unrealized PnL, Equity, Peak Equity, Drawdown) - owned per ADR-005/ADR-006, exclusively PnLEngine's (financial) or RiskEngine's (drawdown) computational domain; not part of Position or Exposure, and not re-opened by this document (P2-03/P2-04 territory).

---

## 6. Current Position Representation

Direct inspection of run_engine/core/position.py, class PositionEngine:

- Instance state: self.position ("FLAT"/"LONG"/"SHORT"), self.side, self.entry_price, self.quantity, self.last_price - five attributes, no sixth attribute of any kind.
- snapshot() returns exactly {"position", "side", "entry_price", "quantity", "last_price"} - five keys. No exposure key exists in this return value.
- project(lifecycle_position, state) - builds Position from a TradeLifecycleEngine.current_position()-shaped input (position, side, entry_price, quantity) plus the current market price (for last_price). Used when self.position and the projected lifecycle position diverge (a reversal-style transition into project()'s fallback branch).
- update_post_trade(execution, state, lifecycle_position) - the primary per-tick update path. Correctly leaves side/quantity/entry_price unchanged when the lifecycle position is unchanged (already verified in the P1-04 certification chain); recomputes a weighted-average entry_price on Scale-In (projected_quantity > self.quantity) via _weighted_average_entry_price(); unconditionally updates last_price from state["price"] on every call (already verified and architecturally ratified in the P1-04 Architecture document, Section 11, for the rejected-transition case - this document does not reopen that decision).
- _set_flat(price) - resets position="FLAT", side=None, entry_price=0.0, quantity=0.0, retains last_price=price.

CanonicalState.state["position"] (run_engine/core/canonical_state.py, __init__): initialized to {"position": "FLAT", "entry_price": None, "last_price": None} - three keys only. This default shape is missing side and quantity, both of which are present in every value PositionEngine.snapshot()/update_post_trade() actually returns. CanonicalState.update_position(position) performs an unconditional whole-dict replacement (self.state["position"] = position), so the true five-key shape is restored the first time CanonicalEnforcer.apply_position() is called (first tick's Position Update stage) - but the three-key default is observable to any code that reads CanonicalState.get()["position"] between construction and the first completed step() call.

Two distinct Position representations exist simultaneously, confirmed by direct trace of RunLoop.step() (run_engine/core/loop.py):

1. position_pre = self.position_engine.snapshot() - read once, near the top of step(), directly from PositionEngine's live instance attributes, bypassing CanonicalState entirely. This is the value passed to StrategySelector.select(), StrategySelector.decide() (indirectly, via state/regime/weights, not position_pre itself), Executor.execute(), and - as position_pre["entry_price"] - to PnLEngine.update() as entry_basis.
2. position = self.position_engine.update_post_trade(...) followed by self.enforcer.apply_position(position) - the post-trade snapshot, published into CanonicalState.state["position"].

Under the current synchronous, single-threaded RunLoop.step() execution model, position_pre (representation 1) always equals the end-of-previous-tick value of representation 2 - they do not diverge in value, only in timing and in which object a given consumer actually reads from. This is the exact pattern already identified and logged as TD-001 ("Canonical Position Source for PnLEngine," Target Phase P2/P2-02A) and already explicitly named in the P2-02A objectives given for this unit ("Position als massgebliche operative Runtime-Entitaet verifizieren"). This document confirms TD-001 is still present, unchanged, at HEAD b88eae5.

Consumers of position_pre (i.e., of PositionEngine.snapshot() directly, bypassing CanonicalState), confirmed by direct code trace of loop.py:
- StrategySelector.select(state, regime, position_pre) (run_engine/core/strategy.py) - reads position.get("position", "FLAT") only.
- Executor.execute(decision, position_pre) (run_engine/core/execution/executor.py) - reads position.get("position", "FLAT") only.
- PnLEngine.update(trade_event, position_pre["entry_price"]) - reads entry_price only, as the entry_basis for realized PnL (this is TD-001's specific, already-certified-as-load-bearing case; see TD-003).

Consumers of CanonicalState.state["position"] (the published representation):
- RiskEngine.check(canonical_state, position, regime) - receives position as its second positional argument, but this is the tick's own local position variable (update_post_trade()'s direct return value), not read from canonical_state["position"] inside RiskEngine.check(). RiskEngine.check()'s body never reads its position parameter at all (Section 7 below) - it is accepted but entirely unused in the current implementation.
- Any external caller reading RunLoop.step()'s returned "state" key (self.cstate.get()) or "position" key (the raw return value of update_post_trade()) - no such caller exists in the active runtime; main.py's print(result) is the only consumer, for logging.

Historical trade responsibility inside PositionEngine: confirmed absent. PositionEngine holds no list of past trades, no trade identifiers, and no historical price/quantity series - its five attributes describe only the current tick's operational state, consistent with ADR-004 ("Position never represents historical execution") and already-certified P1-02/P1-03 lifecycle-ownership boundaries.

Hidden mutations, caches, or ownership couplings identified: none beyond the already-logged TD-001 (dual-state read pattern) and the newly observed CanonicalState default-shape inconsistency (three keys vs. five) noted above. No additional cache, no additional mutable Position-shaped object, was found in run_engine/core.

Behavior across FLAT, LONG, SHORT, Scale-In, Partial Close, Full Close - re-traced against position.py and confirmed unchanged from the behavior already certified through P1-04:
- FLAT: self.position == "FLAT", side=None, entry_price=0.0, quantity=0.0.
- Open (FLAT to LONG/SHORT): handled via project()'s fallback path inside update_post_trade() (the self.position == projected_position branch condition fails when transitioning from FLAT), which calls self.project(lifecycle_position, state).
- Scale-In (same side, quantity increases): entry_price recomputed via weighted average; side/position unchanged.
- Partial Close (same side, quantity decreases but remains positive): entry_price left unchanged (the weighted-average branch only triggers when projected_quantity > self.quantity); quantity updated to the projected (reduced) value.
- Full Close (lifecycle_position["position"] == "FLAT"): routed to _set_flat().

No new defect was found in this re-trace beyond what P1-03/P1-03.1/P1-04 already certified.

---

## 7. Current Exposure Representation

No field named exposure exists anywhere inside PositionEngine or inside the Position representation (neither PositionEngine.snapshot() nor CanonicalState.state["position"] contains an exposure key). ADR-004's "Current Exposure" as a Position property is not implemented anywhere in the current runtime.

A field literally named "exposure" does exist, but at the top level of CanonicalState.state (a sibling of "position", not nested inside it), and it is populated exclusively from RiskEngine.check()'s return value, via CanonicalState.update_risk(risk_dict):

    run_engine/core/canonical_state.py, update_risk():
        self.state["exposure"] = risk_dict.get("exposure", 1.0)

RiskEngine.check() (run_engine/core/risk.py) computes this value as follows, quoted directly:

    exposure = self.max_exposure                # starts at 1.0

    if drawdown_ratio > self.max_drawdown:
        exposure = self.min_exposure             # drops to 0.1

    if regime == "CHOP":
        exposure *= 0.7
    if regime == "TREND":
        exposure *= 1.0
    if regime == "VOLATILE":
        exposure *= 0.5

    exposure = max(self.min_exposure, min(self.max_exposure, exposure))

This computation references only self.max_exposure, self.min_exposure, drawdown_ratio (itself derived from equity and self.peak_equity), and regime. It contains no reference to Position.quantity, Position.entry_price, Position.last_price, or any other Position field, anywhere. This is a risk-adjusted capital-allocation fraction (a "how much of the account may currently be risked" signal, bounded to [0.1, 1.0]), not a Position-derived market-exposure quantity in the ADR-004 sense.

This directly contradicts ADR-004's binding decision text, quoted again for emphasis: "Exposure SHALL always be derived from Position. RiskEngine SHALL consume Position-derived Exposure. RiskEngine SHALL never maintain an independent canonical Exposure representation." RiskEngine currently computes and is the sole source of an "exposure" value that is entirely independent of Position - the precise condition ADR-004 prohibits.

RiskEngine.check(state, position, regime) already receives a position parameter - confirmed by its signature and by loop.py's call site (risk = self.risk_engine.check(canonical_state, position, regime), where position is the tick's own update_post_trade() output) - but the method body never reads this parameter. It is accepted and silently discarded. This is a distinct, separately noteworthy observation from the exposure-computation issue itself: the wiring needed to pass Position into RiskEngine already exists; only the consumption of it does not.

Confirmed additional "exposure" consumer, inactive: PositionSizingEngine.size(state, decision, risk) (run_engine/core/position_sizing.py) reads risk.get("exposure", 1.0) as one multiplicative factor of a computed trade size. PositionSizingEngine is confirmed not imported or invoked anywhere in loop.py or main.py - it is present in the repository but not wired into the active execution path. Its existence demonstrates the codebase's historical intent for "exposure" was allocation-sizing, reinforcing that the collision with ADR-004's Position-Exposure terminology is a naming collision inherited from that history, not a deliberate architectural choice.

Confirmed collision check result (per instruction, item 6): the suspected Exposure semantic collision is real and present in the active runtime. Two distinct concepts share the name "exposure":

1. Position Exposure (ADR-004) - a derived Position property. Not implemented anywhere in the current code.
2. Risk-Adjusted Allocation Exposure (actual RiskEngine.check() / CanonicalState.state["exposure"]) - a capital-allocation sizing fraction, independent of Position, currently implemented and currently the only thing the field name "exposure" refers to anywhere in the active runtime.

A third, unrelated meaning (RiskLayer.current_exposure, an additive/releasable allocation counter capped at 3.0, run_engine/runtime/risk.py) exists in the confirmed-inactive run_engine/runtime/ package and does not affect the active runtime, but is recorded here as evidence that "exposure" has carried at least three non-interchangeable meanings across this repository's history.

Distinguishing Exposure from other confirmed distinct concepts (repeated from the P2-02 governance chain, re-verified unchanged at this HEAD): Risk Metrics (drawdown, drawdown_ratio - RiskEngine/CanonicalState), Lifecycle State (Trade.status, "OPEN"/"CLOSED" - TradeLifecycleEngine), Execution Result (execution["status"] - Executor), and Runtime Status (CanonicalState.state["runtime_status"] - RunLoop, certified in P2-02) are all confirmed structurally separate from both meanings of "exposure" above, with no code path conflating any of them.

---

## 8. Current Ownership and Information Flow

Position (Side, Quantity, Average Entry Price):
- Authoritative Owner (actual): CanonicalState (post-tick) / PositionEngine (pre-tick, via position_pre) - dual-state.
- Computational Authority (actual): PositionEngine.
- Matches ADR-004: Partially - Computational Authority correct; Authoritative Owner split by TD-001's dual-state pattern.

Exposure (ADR-004 sense):
- Authoritative Owner (actual): None - not implemented.
- Computational Authority (actual): None - not implemented.
- Matches ADR-004: No - the property does not exist.

"exposure" (actual field):
- Authoritative Owner (actual): CanonicalState (published).
- Computational Authority (actual): RiskEngine, computed independently of Position.
- Matches ADR-004: No - contradicts "RiskEngine SHALL consume Position-derived Exposure" and "RiskEngine SHALL never maintain an independent canonical Exposure representation."

Trade history:
- Authoritative Owner (actual): TradeLifecycleEngine.
- Computational Authority (actual): TradeLifecycleEngine.
- Matches ADR-004: Yes - confirmed independent from operational Position.

Information flow, as traced through RunLoop.step(): PositionEngine.snapshot() (pre-trade) feeds StrategySelector, Executor, and PnLEngine's entry_basis directly; TradeLifecycleEngine.current_position() feeds PositionEngine.update_post_trade(); PositionEngine.update_post_trade()'s return value feeds CanonicalEnforcer.apply_position() (publishing to CanonicalState) and is also passed as RiskEngine.check()'s unused position argument.

---

## 9. Functional Problem Statement

Two distinct functional gaps exist, both directly named in the P2-02A objectives:

Gap 1 - Position is not yet a single authoritative operational entity. A verified, unchanged instance of TD-001: PositionEngine.snapshot() is read directly by three consumers (StrategySelector, Executor, PnLEngine) before CanonicalState is updated for the current tick. CanonicalState.state["position"] is the published, not the sole, representation. No numeric divergence currently exists (confirmed unchanged from the P1-03.1 and P2-01 certification chains), but two physically distinct read paths exist for what ADR-004 requires to be "exactly one canonical Position."

Gap 2 - Exposure does not exist as a Position property, and the runtime instead maintains an independent, non-Position-derived value under the same name. This is not a partial implementation of ADR-004's Exposure requirement; it is a complete absence of it, combined with a naming collision against an unrelated, already-implemented RiskEngine allocation-sizing metric. This is the more severe of the two gaps, since it is a direct, textual contradiction of ADR-004's Decision section, not merely an unconsolidated read path.

Both gaps are squarely within the P2-02A objectives as given ("Implement ADR-004 Position ownership," "sicherstellen, dass Exposure ausschliesslich eine Eigenschaft von Position bleibt," "verhindern, dass Exposure als eigenstaendiges Runtime-Objekt... existiert"). Neither requires reopening P2-03 (financial ownership) or the already-logged TD-006 (RiskEngine's independent Peak-Equity/Drawdown tracking) - those remain distinct, separately-scoped, already-named issues (Section 20).

---

## 10. Required Functional Capabilities

RC-1 - Exactly one canonical Position representation, read by every consumer, with no consumer reading PositionEngine's live instance state directly.

RC-2 - A Position-derived Exposure quantity, derived from Position and, where scientifically required, immutable instrument metadata, with no independent Exposure source anywhere.

RC-3 - Explicit, permanent separation of Position-Exposure (ADR-004) from the existing RiskEngine risk-adjusted allocation metric, resolving the naming collision without silently merging the two concepts' meanings.

RC-4 - RiskEngine consumption of Position-derived Exposure as an input, without RiskEngine acquiring ownership of Position or Exposure.

RC-5 - Preservation of every already-certified P1-03/P1-03.1/P1-04/P2-01 Position-related contract (entry-basis handoff, rejection non-mutation, weighted-average Scale-In semantics, mark-price-on-rejection policy) unless this unit's own governance chain explicitly re-certifies a change.

---

## 11. Position-State Requirements

P2-02A-FR-001 - Position SHALL contain at least the following properties:

- Side
- Quantity
- Average Entry Price
- Current Exposure

Additional Position properties are permitted provided they do not violate ADR-004 ownership or semantic boundaries.

P2-02A-FR-002 - PositionEngine SHALL remain the exclusive Computational Authority for Position evolution; no other component SHALL compute Side, Quantity, or Average Entry Price.

P2-02A-FR-003 - CanonicalState's default (pre-first-tick) Position representation SHALL contain the same fields as the Position representation published after the first tick, so that no consumer observes a shape that varies between "not yet ticked" and "ticked."

---

## 12. Exposure-Derivation Requirements

P2-02A-FR-004 - Position-derived Exposure SHALL be derived from Position and, where required, immutable instrument metadata necessary for deterministic exposure calculation.

Exposure SHALL NOT be derived from Equity, Drawdown, Regime, or other RiskEngine-owned runtime state.

P2-02A-FR-005 - Exposure SHALL possess no independent storage location distinct from being a property derived from Position; it SHALL NOT be stored as an independently-owned sibling field with no formal derivation relationship to Position.

P2-02A-FR-006 - The existing RiskEngine risk-adjusted allocation value (currently named exposure, computed from max_exposure/min_exposure/drawdown_ratio/regime) SHALL be explicitly and permanently distinguished, by name and by ownership, from Position-derived Exposure; the two SHALL NOT share a field name, a computation, or a storage location without an explicit architectural decision documenting why.

---

## 13. Canonical Ownership Requirements

P2-02A-FR-007 - CanonicalState SHALL be the Authoritative Owner of the canonical Position, including its derived Exposure, consistent with ADR-004 and Rule OM-006.

P2-02A-FR-008 - Exactly one authoritative Position value SHALL exist per completed tick; no second, independently-readable Position-shaped value SHALL exist for consumers that require the authoritative value (Rule OM-001).

P2-02A-FR-009 - TradeLifecycleEngine SHALL NOT acquire ownership of, or independently compute, operational Position or Exposure (ADR-004; already conformant, re-verified in Section 6 - this requirement records the invariant, it does not change current behavior).

---

## 14. Runtime Consumer Requirements

P2-02A-FR-010 - RiskEngine SHALL consume Position-derived Exposure as an input to its own risk computation; it SHALL NOT maintain an independent canonical Exposure representation (ADR-004, verbatim).

P2-02A-FR-011 - RiskEngine SHALL NOT own Position or Exposure; its consumption of Position-derived Exposure SHALL be read-only (ADR-004 Acceptance Criteria).

P2-02A-FR-012 - Every consumer of Position that requires the authoritative value (at minimum: StrategySelector, Executor, PnLEngine's entry-basis input, RiskEngine) SHALL read from the single canonical source established by FR-008, not from PositionEngine's live instance state, unless an explicit, documented exception (matching the P1-03.1 TD-003 precedent for PnLEngine's entry-basis timing requirement) is recorded.

---

## 15. Lifecycle Separation Requirements

P2-02A-FR-013 - Position SHALL continue to describe only the current operational state; it SHALL NOT be extended to carry historical execution facts (ADR-004; already conformant, re-verified in Section 6).

P2-02A-FR-014 - The existing lifecycle transition contracts (FLAT, Open, Scale-In, Partial Close, Full Close) verified in Section 6 SHALL be preserved exactly as currently implemented, unless this unit's governance chain explicitly re-certifies a change to them.

---

## 16. Determinism and Replay Requirements

P2-02A-FR-015 - Position-derived Exposure computation SHALL be a pure function of the current Position (and any explicitly approved additional canonical inputs); identical Position values SHALL always produce identical Exposure values (Invariant AI-005).

P2-02A-FR-016 - Resolving the dual-state pattern (RC-1/FR-008/FR-012) SHALL NOT introduce any new source of non-determinism (e.g., ordering dependency, hidden caching) beyond what already exists and is certified in the P1-04/P2-01 chain.

---

## 17. Failure and Invalid-State Requirements

P2-02A-FR-017 - The existing ADR-011 protections already certified in P1-04 (rejected transitions never mutate Position's Side/Quantity/Average Entry Price) SHALL remain intact after any Position-ownership change made under this unit.

P2-02A-FR-018 - If Exposure derivation requires a Position field that can be undefined or zero (e.g., Quantity 0.0 at FLAT), the derivation SHALL produce a well-defined, deterministic result (not an exception, not NaN) for every reachable Position state, including FLAT.

---

## 18. Compatibility Requirements

P2-02A-FR-019 - The already-certified entry_basis handoff (position_pre["entry_price"] passed explicitly into PnLEngine.update(), certified P1-03.1, ratified P1-04) SHALL continue to function; any change to how Position is sourced SHALL preserve this handoff's timing semantics (pre-trade snapshot, not post-trade) unless TD-003 is resolved as part of this unit with explicit re-certification.

P2-02A-FR-020 - The CanonicalEnforcer.apply_position() mediation method and its existing call site in RunLoop.step() SHALL remain the sole Writer-on-Behalf-Of path for publishing Position into CanonicalState, consistent with the pattern already used for seven other fields (Rule OM-003).

---

## 19. Validation Requirements

Each functional requirement above has a corresponding validation condition, to be executed once implementation exists (this document does not implement or execute them):

- FR-001/FR-003: assert CanonicalState's Position shape (key set) is identical before and after the first step() call.
- FR-002/FR-009: repository-wide search confirms no component other than PositionEngine writes Side/Quantity/Average Entry Price; TradeLifecycleEngine.Trade has no Exposure field.
- FR-004/FR-005: repository-wide search confirms the Exposure derivation function references only Position fields and, where explicitly approved, immutable instrument metadata; it also confirms that no independent Exposure storage location exists outside the Position-derivation path.
- FR-006: confirm, by name and by call graph, that the RiskEngine allocation metric and Position-derived Exposure are distinguishable and not merged.
- FR-007/FR-008/FR-012: confirm exactly one Position read path exists for each listed consumer, by direct call-site inspection.
- FR-010/FR-011: confirm RiskEngine.check()'s Exposure-relevant computation reads its position parameter and does not independently compute or own it.
- FR-013/FR-014: re-run the FLAT/Open/Scale-In/Partial-Close/Full-Close scenarios already used in the P1-03/P1-03.1/P1-04 certification chain; confirm identical results.
- FR-015/FR-016: run identical Position inputs twice; confirm identical Exposure outputs; confirm no new ordering dependency introduced.
- FR-017: re-run the P1-04 rejected-transition scenarios; confirm Position fields remain protected.
- FR-018: evaluate Exposure derivation at quantity=0.0 (FLAT) and confirm a defined, non-exceptional, non-NaN result.
- FR-019: re-run the P1-03.1/P1-04 entry-basis scenarios (LONG/SHORT, Scale-In, Partial Close); confirm identical realized PnL results.
- FR-020: confirm, by diff inspection at implementation time, that apply_position() remains the sole Position write path.

---

## 20. Explicit Non-Goals and Deferred Scope

- Full PnL/Equity/Peak-Equity consolidation - P2-03's stated scope ("Verify Realized PnL (cumulative). Verify Equity, Peak Equity and Drawdown consistency"). Not addressed here.
- Full RiskEngine consolidation beyond Exposure consumption - TD-006 (RiskEngine's independent Peak-Equity/Drawdown tracking, contrary to ADR-006/ADR-007) is a separate, already-logged, already-targeted (P2-03/P2-04) defect. This document's Section 7/Gap 2 finding (RiskEngine's independent Exposure computation) is a different ADR-004 non-conformance from TD-006's ADR-006/ADR-007 non-conformance, even though both live inside RiskEngine.check(). This document addresses only the Exposure aspect (P2-02A's own named scope); the Peak-Equity/Drawdown aspect remains TD-006's, unchanged, not reopened here.
- Lifecycle control surface - TD-007, unaffected.
- Complete Tick-Complete Snapshot architecture - ADR-010/Phase 3, unaffected.
- General repository cleanup - the confirmed-inactive run_engine/core/position_sizing.py, run_engine/core/equity_stabilizer.py, and run_engine/runtime/ package are recorded as findings (Section 4) but their classification (retain/integrate/archive/remove) belongs to Phase 6 Repository Consolidation, not P2-02A.
- Not-immediately-necessary technical debt - TD-002 (unify _safe_float), TD-003 (document pre-trade snapshot dependency - relevant as context for FR-019 but not required to be resolved by this unit), TD-005 (automated test suite) - none are required by P2-02A's own objectives and none are pulled in.
- No new architecture decision is proposed by this document. Section 9's two gaps and Sections 11-18's requirements describe what must become true; how (interface shapes, exact derivation formula, exact consolidation mechanism for the dual-state pattern) is explicitly deferred to the P2-02A Architecture document.

---

## 21. Functional Requirement Catalogue

P2-02A-FR-001 - Position contains at least Side, Quantity, Average Entry Price, and Current Exposure; additional properties remain subject to ADR-004 ownership and semantic boundaries. Source: ADR-004.
P2-02A-FR-002 - PositionEngine is exclusive Computational Authority for Position. Source: ADR-004.
P2-02A-FR-003 - CanonicalState default Position shape matches post-tick shape. Source: Section 6 finding.
P2-02A-FR-004 - Position-derived Exposure is derived from Position and, where required, immutable instrument metadata; it is not derived from RiskEngine-owned runtime state. Source: ADR-004.
P2-02A-FR-005 - Exposure has no independent storage. Source: ADR-004.
P2-02A-FR-006 - RiskEngine's existing allocation metric permanently distinguished from Position-Exposure. Source: Section 7 finding.
P2-02A-FR-007 - CanonicalState is Authoritative Owner of canonical Position. Source: ADR-004.
P2-02A-FR-008 - Exactly one authoritative Position value per tick. Source: ADR-004 AC / Rule OM-001.
P2-02A-FR-009 - TradeLifecycleEngine never owns operational Position/Exposure. Source: ADR-004.
P2-02A-FR-010 - RiskEngine consumes Position-derived Exposure. Source: ADR-004 (verbatim).
P2-02A-FR-011 - RiskEngine never owns Position or Exposure; read-only consumption. Source: ADR-004 AC.
P2-02A-FR-012 - All required consumers read the single canonical Position source. Source: TD-001.
P2-02A-FR-013 - Position never carries historical execution facts. Source: ADR-004.
P2-02A-FR-014 - Existing lifecycle transition contracts preserved. Source: P1-03/P1-03.1/P1-04.
P2-02A-FR-015 - Exposure derivation is a pure function of Position. Source: AI-005.
P2-02A-FR-016 - No new non-determinism introduced. Source: AI-005.
P2-02A-FR-017 - ADR-011 rejection protections remain intact. Source: P1-04.
P2-02A-FR-018 - Exposure derivation well-defined at FLAT/zero quantity. Source: Failure/edge case.
P2-02A-FR-019 - entry_basis handoff timing preserved. Source: TD-003, P1-03.1.
P2-02A-FR-020 - CanonicalEnforcer.apply_position remains sole write path. Source: Rule OM-003.

---

## 22. Traceability to ADR-004 Acceptance Criteria

- "Exactly one canonical Position exists" - covered by FR-007, FR-008, FR-012.
- "Exposure never exists independently from Position" - covered by FR-004, FR-005, FR-015.
- "RiskEngine never owns Position" - covered by FR-011.
- "RiskEngine never owns Exposure" - covered by FR-006, FR-010, FR-011.
- "TradeLifecycleEngine never owns operational Position" - covered by FR-009, FR-013.
- "CanonicalState contains the authoritative operational Position" - covered by FR-007.

All six ADR-004 Acceptance Criteria are covered by at least one functional requirement above. No ADR-004 Acceptance Criterion is left untraced.

---

## 23. Open Questions

OQ-001 - What is the scientific definition of Position-derived Exposure?

Before selecting a mathematical formula, the architecture must define which quantity Exposure represents (for example market value, committed capital, nominal exposure, risk exposure, delta exposure, or another scientifically justified concept).

The mathematical derivation shall be selected only after the semantic definition has been established.

OQ-002 - Should the existing RiskEngine allocation-sizing value (currently named exposure) be renamed, or should Position-derived Exposure be given a different field name to avoid the collision? Either resolves the naming conflict (FR-006); which one is an Architecture-document decision affecting CanonicalState's schema, not resolved here.

OQ-003 - Should resolving the TD-001 dual-state pattern (FR-008/FR-012) route all listed consumers through CanonicalState directly, or through some other single-source mechanism? This mirrors the still-unresolved Scientific Dependency Analysis question already on record via TD-001's own description; not resolved here.

OQ-004 - RiskEngine.check()'s currently-unused position parameter (Section 7) suggests the wiring for FR-010 may already be structurally anticipated. Whether to reuse this exact parameter or redesign the call is an Architecture/Specification-level decision, not resolved here.

OQ-005 - Should PositionSizingEngine (currently inactive) be wired into the active path as part of resolving the Exposure collision, or left inactive and reclassified separately under Phase 6? Not resolved here; recorded as a question the Architecture document should explicitly answer or explicitly defer.

OQ-006 - Should Position-derived Exposure be stored as part of the canonical Position representation, or should it remain a deterministic computed projection derived whenever required?

The decision affects CanonicalState representation, serialization, replay determinism, snapshot architecture and future Tick-Complete Snapshot design, and therefore requires an explicit architectural decision.

---

## 24. Functional Readiness Decision

This analysis finds two confirmed, repository-grounded functional gaps (Section 9) directly within P2-02A's stated objectives, both traceable to specific ADR-004 text and both localized to a small, already-understood set of files (position.py, canonical_state.py, canonical_enforcer.py, risk.py, loop.py, and the read call sites in strategy.py/executor.py/pnl.py). No blocking ambiguity was found in the existing baseline text that would prevent proceeding: ADR-004's Decision and Acceptance Criteria sections are unambiguous; only the derivation formula (OQ-001) and the naming resolution (OQ-002) require an architectural decision, which is expected and normal at this stage of the governance sequence (consistent with how P1-04 and P2-01 each left comparable decisions to their own Architecture documents).

Functional Readiness: READY. This document is sufficient to proceed to the P2-02A Scientific Dependency Analysis. No further repository investigation is required before that step.

---

## 25. Internal Consistency Review

Terminology consistency - "Position," "Exposure," "Authoritative Owner," "Computational Authority," and "Writer-on-Behalf-Of" are used exactly as defined in the Architecture Baseline throughout this document. "Exposure" is never used to mean the RiskEngine allocation metric without explicit qualification ("risk-adjusted allocation exposure" or "the existing RiskEngine value").

Ownership consistency - No requirement in Sections 11-18 assigns ownership of any concept to a component other than what ADR-004 or the Runtime Ownership Matrix already assigns. No new Authoritative Owner or Computational Authority is proposed.

Scope consistency - Every requirement traces to either ADR-004 text directly, a Section 6/7 repository finding, or an already-logged Technical Debt Register item explicitly targeted at P2-02A (TD-001, TD-003 contextually). No requirement duplicates P2-03 or P2-04 scope; Section 20 explicitly excludes both.

Traceability consistency - Section 21's catalogue and Section 22's ADR-004 Acceptance Criteria mapping are cross-checked: all 20 functional requirements appear in exactly one catalogue row each; all six ADR-004 Acceptance Criteria are covered.

Observation/requirement/decision separation - Sections 6, 7, and 8 contain only observations, each with a direct file/function/line citation. Sections 9 through 18 contain only requirements derived from those observations plus the binding baseline. Section 23 contains only open questions explicitly deferred to a future Architecture document; no architecture decision is made anywhere in this document.

Status: Internal Consistency Review PASS.
