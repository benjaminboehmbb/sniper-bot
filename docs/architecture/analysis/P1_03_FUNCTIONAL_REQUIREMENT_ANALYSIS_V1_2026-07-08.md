# Document Metadata

Document Class: Functional Requirement Analysis
Document ID: P1-03-FRA
Version: V1.0
Status: Draft
Date: 2026-07-08
Project: Trading-Bot Scientific Runtime
Subsystem: Run Engine
Primary Location: docs/architecture/analysis/P1_03_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-08.md

Depends On:
- docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md
- docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md
- docs/architecture/specifications/P1_02A_TRADE_LIFECYCLE_CONSOLIDATION_SPECIFICATION_V1_2026-07-07.md
- docs/architecture/certification/P1_02_TRADE_LIFECYCLE_CONSOLIDATION_CERTIFICATION_V1_2026-07-08.md

Referenced By:
- docs/architecture/analysis/P1_03_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-08.md
- docs/architecture/analysis/P1_03_CAPABILITY_GAP_ANALYSIS_V1_2026-07-08.md
- docs/architecture/specifications/P1_03A_PARTIAL_CLOSE_AND_SCALE_IN_SPECIFICATION_V1_2026-07-08.md

---

# P1-03 Functional Requirement Analysis

## 1. Purpose

This document analyzes the functional requirement basis for P1-03.

P1-03 follows the certified P1-02 Trade Lifecycle Consolidation milestone.

P1-02 established the lifecycle ownership boundary:

- TradeLifecycleEngine owns lifecycle facts and lifecycle transitions.
- PositionEngine projects operational position from lifecycle state.
- PnLEngine computes financial consequences from lifecycle facts.
- RunLoop orchestrates deterministic execution order.
- CanonicalState stores operational runtime state.

P1-03 does not reopen this ownership model.

The purpose of P1-03 is to determine which functional capability remains missing after P1-02 when an active lifecycle must support quantity changes before final closure.

This document is analytical.

It does not define final interfaces.

It does not define implementation.

It does not define the final specification.

---

## 2. Certified P1-02 Baseline

The certified P1-02 lifecycle can represent a constant-quantity trade.

The functional model is:

```text
NO_POSITION
    -> TRADE_OPENED
    -> TRADE_CLOSED
    -> NO_POSITION

Supported runtime cases:

BUY from FLAT
    -> open LONG lifecycle

SELL from FLAT
    -> open SHORT lifecycle

SELL against active LONG
    -> close LONG lifecycle

BUY against active SHORT
    -> close SHORT lifecycle

This model is valid for trades whose quantity is created once at entry and remains unchanged until final close.

P1-02 therefore solved lifecycle ownership.

P1-02 did not solve lifecycle quantity evolution.
```
## 3. Functional Deficiency

The current certified model cannot represent an active lifecycle whose quantity changes while the lifecycle remains open.

The limitation appears in four runtime cases.

Case 1: Same-Direction Execution While Active
Active lifecycle:
    side = LONG
    quantity = 1.0

Incoming execution:
    action = BUY
    quantity = 0.5

Required meaning:

Increase active LONG quantity from 1.0 to 1.5.

The runtime must not treat this as:

an invalid duplicate BUY,
an independent unrelated trade,
a silent overwrite of the existing lifecycle.

This case requires Scale-In semantics.

Case 2: Opposite-Direction Execution Below Active Quantity
Active lifecycle:
    side = LONG
    quantity = 1.5

Incoming execution:
    action = SELL
    quantity = 0.5

Required meaning:

Reduce active LONG quantity from 1.5 to 1.0.
Keep lifecycle open.
Generate realized PnL for the reduced quantity.

The runtime must not treat this as:

full lifecycle closure,
opening a SHORT lifecycle,
overwriting the original quantity.

This case requires Partial Close semantics.

Case 3: Opposite-Direction Execution Equal To Active Quantity
Active lifecycle:
    side = LONG
    quantity = 1.0

Incoming execution:
    action = SELL
    quantity = 1.0

Required meaning:

Close remaining LONG quantity completely.
Terminate lifecycle exactly once.
Generate realized PnL for the closed quantity.

This case requires Full Close semantics.

Case 4: Opposite-Direction Execution Above Active Quantity
Active lifecycle:
    side = LONG
    quantity = 1.0

Incoming execution:
    action = SELL
    quantity = 1.5

Functional ambiguity:

The execution could mean:
1. close LONG quantity 1.0 and open SHORT quantity 0.5,
2. reject because reversal is not yet supported,
3. split the execution into close and reverse events.

P1-03 must classify this case explicitly.

Until reversal semantics are formally derived, this transition should be treated as an invalid quantity transition.

## 4. Core Functional Problem

The missing capability is not merely "Scale-In" or "Partial Close".

Scale-In and Partial Close are observable behaviours.

The deeper missing capability is:

Quantity-aware lifecycle evolution

Definition:

Quantity-aware lifecycle evolution is the capability of one active lifecycle to preserve its identity while its active quantity changes over time through deterministic lifecycle transitions.

This capability must preserve:

lifecycle identity,
active side,
active quantity,
ordered lifecycle history,
entry basis,
scale-in facts,
reduction facts,
realized reduction facts,
final close facts,
invalid transition evidence.

Without this capability, the runtime cannot distinguish:

one lifecycle that evolved,
multiple independent trades,
a partial reduction,
a full closure,
an invalid transition,
a silent state overwrite.

## 5. Functional Requirement Derivation

FR-Candidate-001: Lifecycle Identity Preservation

An active lifecycle must retain one stable lifecycle identity across Scale-In and Partial Close transitions.

Reason:

Quantity changes do not necessarily create a new trade lifecycle.

The lifecycle remains the same historical entity while its operational quantity evolves.

FR-Candidate-002: Explicit Quantity Delta Representation

Every quantity-changing lifecycle transition must record the quantity delta that caused the transition.

Reason:

The runtime must distinguish current active quantity from the executed quantity that changed it.

FR-Candidate-003: Scale-In Transition

Same-direction execution while a lifecycle is active must be representable as Scale-In.

Required facts:

lifecycle id,
side,
prior quantity,
execution quantity,
resulting quantity,
execution price,
tick,
reason or transition type.
FR-Candidate-004: Partial Close Transition

Opposite-direction execution below active quantity must be representable as Partial Close.

Required facts:

lifecycle id,
side,
prior quantity,
closed quantity,
remaining quantity,
entry basis,
close price,
tick,
realized PnL input facts.
FR-Candidate-005: Full Close Transition

Opposite-direction execution equal to active quantity must be representable as Full Close.

Required facts:

lifecycle id,
side,
prior quantity,
closed quantity,
remaining quantity = 0.0,
entry basis,
close price,
tick,
lifecycle terminal status.
FR-Candidate-006: Invalid Quantity Transition Handling

Opposite-direction execution above active quantity must not silently mutate lifecycle state.

Until reversal semantics are separately derived, this case must produce a Runtime Failure Event.

Required facts:

attempted action,
active side,
active quantity,
attempted quantity,
tick,
price,
rejection reason.
FR-Candidate-007: PnL Derivation From Lifecycle Facts

Realized PnL must be computed by PnLEngine from lifecycle facts.

TradeLifecycleEngine may generate the factual event.

TradeLifecycleEngine must not become the financial computation authority.

FR-Candidate-008: Position Projection From Resulting Lifecycle State

PositionEngine must project only the resulting operational position.

It must not reconstruct historical trade composition.

Required projected facts:

position,
side,
entry basis,
active quantity,
last price.
FR-Candidate-009: Performance From Realized Outcomes

PerformanceEngine must eventually evaluate realized lifecycle outcomes rather than runtime decisions.

Partial Close creates a realized outcome without terminating the lifecycle.

Full Close creates a realized outcome and terminates the lifecycle.

## 6. Minimality Analysis

The minimal required capability is not a portfolio model.

The minimal required capability is not multi-position support.

The minimal required capability is not reversal support.

The minimal required capability is not exchange-order simulation.

The minimal required capability is:

One active lifecycle can change quantity through explicit deterministic lifecycle transitions.

Minimum transition set:

TRADE_OPENED
SCALE_IN
PARTIAL_CLOSE
TRADE_CLOSED
RUNTIME_FAILURE

This set is sufficient to represent:

open lifecycle,
increase active quantity,
reduce active quantity without closure,
close remaining quantity,
reject invalid transition.

This set is not sufficient to represent:

simultaneous independent positions,
hedged long/short books,
immediate close-and-reverse,
multi-exchange fills,
order-book execution modelling.

Those capabilities remain outside P1-03.

## 7. Functional Non-Goals

P1-03 does not require:

multiple simultaneous active lifecycles,
portfolio-level position accounting,
leverage model redesign,
fee model redesign,
order-book simulation,
exchange execution modelling,
slippage modelling,
strategy redesign,
risk model redesign,
reversal implementation,
persistence redesign,
runtime logging redesign.

P1-03 must remain focused on lifecycle quantity evolution.

## 8. Dependency Analysis Preparation

The next document must determine which scientific dependency is primary.

Candidate dependencies:

Quantity semantics.
Lifecycle transition semantics.
Entry basis semantics.
Partial realization semantics.
Invalid transition semantics.
Projection semantics.
Performance outcome semantics.

The likely minimal prerequisite is quantity semantics.

Without quantity semantics, the system cannot distinguish Scale-In, Partial Close, Full Close and invalid reversal attempts.

This conclusion remains provisional until Scientific Dependency Analysis is completed.

## 9. Capability Gap Summary

P1-02 solved:

lifecycle ownership,
open lifecycle,
close lifecycle,
lifecycle-derived position projection,
realized PnL computation outside TradeLifecycleEngine.

P1-02 did not solve:

Scale-In,
Partial Close,
quantity delta events,
partial realized PnL,
active quantity evolution,
invalid over-close handling,
performance treatment of partial realization.

P1-03 must therefore derive and specify quantity-aware lifecycle evolution.

## 10. Internal Consistency Review
Ownership Consistency

PASS.

The document preserves P1-02 ownership boundaries.

TradeLifecycleEngine remains lifecycle owner.

PnLEngine remains financial computation authority.

PositionEngine remains projection layer.

Scope Consistency

PASS.

The document derives functional requirements only.

It does not define implementation details.

It does not introduce final interfaces.

Minimality Review

PASS.

The derived capability is limited to one active lifecycle with explicit quantity evolution.

No portfolio, reversal, execution simulation or strategy redesign is introduced.

Architecture Consistency

PASS.

The analysis remains aligned with the approved lifecycle transition model:

Open
Scale-In
Partial Close
Full Close
Runtime Failure

## 11. Conclusion

P1-03 is functionally justified.

The certified P1-02 runtime can represent constant-quantity lifecycle ownership.

It cannot represent lifecycle quantity evolution.

The required next capability is:

Quantity-aware lifecycle evolution

This capability must be analyzed through Scientific Dependency Analysis before implementation specification begins.



