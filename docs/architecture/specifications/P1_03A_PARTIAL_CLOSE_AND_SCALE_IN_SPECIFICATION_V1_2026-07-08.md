
# Document Metadata

Document Class:
Implementation Specification

Document ID:
P1-03A

Version:
V1.0

Status:
Implementation Preparation

Date:
2026-07-08

Project:
Trading-Bot Scientific Runtime

Subsystem:
Run Engine

Primary Location:

docs/architecture/specifications/P1_03A_PARTIAL_CLOSE_AND_SCALE_IN_SPECIFICATION_V1_2026-07-08.md

Depends On:

- RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md
- RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md
- P1_03_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-08.md
- P1_03_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-08.md
- P1_03_CAPABILITY_GAP_ANALYSIS_V1_2026-07-08.md
- P1_03_PARTIAL_CLOSE_AND_SCALE_IN_ARCHITECTURE_V1_2026-07-08.md

Referenced By:

- P1-03 Implementation
- P1-03 Validation
- P1-03 Certification

-------------------------------------------------------------------------------

# 1. Objective

This specification defines the implementation contract for P1-03.

The purpose of P1-03 is to extend the certified lifecycle model with
Quantity-aware Lifecycle Evolution.

No ownership changes are introduced.

No runtime responsibilities are reassigned.

Only lifecycle semantics are extended.

-------------------------------------------------------------------------------

# 2. Scope

Included

- quantity evolution
- Scale-In
- Partial Close
- quantity-aware lifecycle transitions
- lifecycle quantity validation
- lifecycle event extension
- lifecycle projection update
- validation

Excluded

- multi-position support
- hedge mode
- portfolio accounting
- leverage redesign
- exchange execution modelling
- broker abstraction
- order-book simulation
- reversal support
- persistence redesign

-------------------------------------------------------------------------------

# 3. Architectural Principles

The following architectural contracts remain mandatory.

TradeLifecycleEngine

Authoritative Owner of lifecycle history.

-------------------------------------------------------------------------------

PositionEngine

Projection layer only.

-------------------------------------------------------------------------------

PnLEngine

Exclusive Computational Authority for financial computation.

-------------------------------------------------------------------------------

CanonicalState

Operational runtime state only.

-------------------------------------------------------------------------------

RunLoop

Deterministic orchestration only.

-------------------------------------------------------------------------------

# 4. Target Lifecycle Model

The target lifecycle becomes

TRADE_OPENED

↓

ACTIVE

↓

SCALE_IN

↓

ACTIVE

↓

PARTIAL_CLOSE

↓

ACTIVE

↓

TRADE_CLOSED

Runtime Failure Events remain available from every transition.

-------------------------------------------------------------------------------

# 5. Required Runtime Behaviour

Case 1

No active lifecycle.

Incoming BUY.

Result

Open LONG lifecycle.

-------------------------------------------------------------------------------

Case 2

No active lifecycle.

Incoming SELL.

Result

Open SHORT lifecycle.

-------------------------------------------------------------------------------

Case 3

Active LONG.

Incoming BUY.

Result

Scale-In.

Lifecycle remains active.

-------------------------------------------------------------------------------

Case 4

Active SHORT.

Incoming SELL.

Result

Scale-In.

Lifecycle remains active.

-------------------------------------------------------------------------------

Case 5

Active LONG.

Incoming SELL.

Execution quantity smaller than current quantity.

Result

Partial Close.

Lifecycle remains active.

-------------------------------------------------------------------------------

Case 6

Active SHORT.

Incoming BUY.

Execution quantity smaller than current quantity.

Result

Partial Close.

Lifecycle remains active.

-------------------------------------------------------------------------------

Case 7

Active LONG.

Incoming SELL.

Execution quantity equals current quantity.

Result

Trade Closed.

-------------------------------------------------------------------------------

Case 8

Active SHORT.

Incoming BUY.

Execution quantity equals current quantity.

Result

Trade Closed.

-------------------------------------------------------------------------------

Case 9

Execution quantity exceeds current quantity.

Result

Runtime Failure Event.

Lifecycle remains unchanged.

-------------------------------------------------------------------------------

# 6. Execution Quantity Origin

Execution Quantity is an explicit runtime object.

Execution Quantity shall never be inferred inside
TradeLifecycleEngine.

Execution Quantity shall be produced exclusively by
the Execution subsystem.

The Execution subsystem is the single authoritative
owner responsible for determining execution quantity.

TradeLifecycleEngine shall never determine,
estimate or modify execution quantity.

Execution Quantity shall be forwarded unchanged to
TradeLifecycleEngine as part of the immutable
execution object.

TradeLifecycleEngine shall consume Execution Quantity
as an immutable execution fact.

The ownership of Execution Quantity is assigned to the
Execution subsystem.

TradeLifecycleEngine shall never determine execution
size autonomously.

Execution Quantity shall be available before lifecycle
transition classification begins.

Every execution reaching TradeLifecycleEngine shall
contain at minimum

- action
- execution quantity
- execution price
- execution tick

Lifecycle transition classification shall consume these
execution facts without modification.

-------------------------------------------------------------------------------


# 7. Lifecycle Data Requirements

Trade shall additionally maintain

Opening Quantity

Current Quantity

Lifecycle Status

Lifecycle Identifier

Lifecycle History

The implementation shall not duplicate lifecycle ownership.

-------------------------------------------------------------------------------

# 8. LifecycleEvent Requirements

event_type
trade_id
side
price
tick
entry_price
prior_quantity
execution_quantity
resulting_quantity
quantity_delta
closed_quantity
remaining_quantity
reason

-------------------------------------------------------------------------------


# 9. Entry Basis Rules

TradeLifecycleEngine shall record immutable Entry Facts only.

TradeLifecycleEngine shall never calculate or modify Average Entry Price.

Average Entry Price is part of the operational Position.

PositionEngine shall become the exclusive Computational Authority for Average Entry Price evolution.

PnLEngine shall consume

- immutable Entry Facts,
- Position,

to calculate realized and unrealized financial outcomes.

The accounting convention used for realized PnL calculation
(e.g. weighted average, FIFO or another approved method)
is defined exclusively by PnLEngine.

TradeLifecycleEngine remains independent from accounting methodology.


-------------------------------------------------------------------------------

# 10. TradeLifecycleEngine Responsibilities

TradeLifecycleEngine shall

open lifecycle

perform Scale-In

perform Partial Close

perform Full Close

validate quantity transitions

generate LifecycleEvents

generate Runtime Failure Events

TradeLifecycleEngine shall not

compute realized pnl

compute equity

compute drawdown

compute exposure

compute performance

-------------------------------------------------------------------------------

# 11. PositionEngine Responsibilities

PositionEngine shall project

side

current quantity

entry basis

last price

No lifecycle interpretation shall occur inside PositionEngine.

-------------------------------------------------------------------------------

# 12. PnLEngine Responsibilities

PnLEngine shall consume

- immutable LifecycleEvents,
- immutable Entry Facts,
- Position.

PnLEngine is the exclusive Computational Authority for

- realized PnL,
- unrealized PnL,
- accounting methodology.

PnLEngine shall explicitly define and apply the accounting convention used for realized financial outcomes.

TradeLifecycleEngine shall remain independent from accounting methodology.

PnLEngine shall not modify lifecycle history.


-------------------------------------------------------------------------------

# 13. RunLoop Responsibilities

RunLoop execution order remains

Runtime Tick

↓

State

↓

Regime

↓

Strategy

↓

Execution

↓

TradeLifecycle

↓

Position

↓

PnL

↓

Risk

↓

Performance

↓

Tick-Complete CanonicalState Publication

RunLoop shall publish CanonicalState exactly once after all
mandatory runtime stages have completed.

No runtime component shall consume a Tick-Complete
CanonicalState before publication.


-------------------------------------------------------------------------------

# 14. Validation Requirements

Validation Group 1

Lifecycle Identity Preservation

Verify that

- one lifecycle identifier remains unchanged throughout the complete lifecycle,
- Scale-In never creates a second lifecycle,
- Partial Close never creates a second lifecycle,
- Full Close terminates exactly one lifecycle.

PASS Criteria

Exactly one lifecycle identifier exists from TRADE_OPENED until TRADE_CLOSED.

-------------------------------------------------------------------------------

Validation Group 2

Scale-In Validation

Verify that

- Scale-In increases current quantity,
- prior quantity remains historically correct,
- resulting quantity is computed correctly,
- quantity delta is correct,
- one LifecycleEvent is generated,
- lifecycle identity remains unchanged.

PASS Criteria

Resulting quantity equals

prior quantity + execution quantity.

-------------------------------------------------------------------------------

Validation Group 3

Partial Close Validation

Verify that

- current quantity decreases correctly,
- closed quantity is recorded,
- remaining quantity is correct,
- realized facts are generated,
- lifecycle remains active.

PASS Criteria

Remaining quantity equals

prior quantity - execution quantity.

-------------------------------------------------------------------------------

Validation Group 4

Full Close Validation

Verify that

- remaining quantity becomes zero,
- lifecycle status becomes CLOSED,
- exactly one TRADE_CLOSED event is generated,
- lifecycle terminates exactly once.

PASS Criteria

No active lifecycle remains after TRADE_CLOSED.

-------------------------------------------------------------------------------

Validation Group 5

Multiple Scale-In Validation

Verify that

- multiple consecutive Scale-In operations are supported,
- lifecycle identity remains unchanged,
- quantities accumulate correctly,
- one LifecycleEvent is generated for every Scale-In.

PASS Criteria

Current quantity equals the cumulative quantity of all Scale-In operations.

-------------------------------------------------------------------------------

Validation Group 6

Multiple Partial Close Validation

Verify that

- multiple Partial Close operations are supported,
- remaining quantity is updated correctly,
- realized facts are generated for every Partial Close,
- lifecycle remains active until remaining quantity reaches zero.

PASS Criteria

Remaining quantity equals

opening quantity

+

all Scale-In quantities

-

all closed quantities.

-------------------------------------------------------------------------------

Validation Group 7

Mixed Transition Validation

Verify that

- Scale-In after Partial Close is supported,
- Partial Close after Scale-In is supported,
- lifecycle identity remains unchanged,
- transition order remains deterministic.

PASS Criteria

The resulting lifecycle state is identical regardless of internal implementation strategy.

-------------------------------------------------------------------------------

Validation Group 8

Invalid Quantity Validation

Verify that execution quantity

- is present,
- is numeric,
- is finite,
- is greater than zero.

Invalid quantity shall never mutate lifecycle state.

PASS Criteria

Every invalid quantity generates one Runtime Failure Event.

Lifecycle state remains unchanged.

-------------------------------------------------------------------------------

Validation Group 9

Over-Close Validation

Define the comparison tolerance

QUANTITY_EPSILON

for floating-point quantity comparisons.

Verify that

current_quantity + QUANTITY_EPSILON < execution_quantity

generates

Runtime Failure Event.

Verify that

abs(current_quantity - execution_quantity) <= QUANTITY_EPSILON

is classified as Full Close.

No lifecycle mutation shall occur after an Over-Close.

PASS Criteria

Exactly one Runtime Failure Event is generated for every Over-Close.

Lifecycle state remains unchanged.

Floating-point rounding shall never change transition classification.


-------------------------------------------------------------------------------

Validation Group 10

Repeated Runtime Failure Validation

Verify that repeated invalid executions

- do not mutate lifecycle state,
- preserve lifecycle identity,
- preserve quantity,
- generate deterministic Runtime Failure Events.

PASS Criteria

Lifecycle state before and after repeated failures is identical.

-------------------------------------------------------------------------------

Validation Group 11

PnLEngine Validation

Verify that

PnLEngine computes realized outcomes exclusively from LifecycleEvents.

PnLEngine shall not reconstruct lifecycle transitions.

PASS Criteria

Identical LifecycleEvents always produce identical realized outcomes.

-------------------------------------------------------------------------------

Validation Group 12

PerformanceEngine Validation

Verify that

- PerformanceEngine consumes realized PnLEngine outputs only.
- PerformanceEngine does not consume LifecycleEvents directly.
- PerformanceEngine does not distinguish Partial Close and Full Close by interpreting lifecycle history.
- PerformanceEngine evaluates realized outcomes provided by PnLEngine.

PASS Criteria

PerformanceEngine produces identical evaluation results for identical realized PnLEngine outputs.

PerformanceEngine performs no lifecycle reconstruction.


-------------------------------------------------------------------------------

Validation Group 13

RunLoop Validation

Verify that execution order remains

State

↓

Regime

↓

Strategy

↓

Execution

↓

TradeLifecycle

↓

Position

↓

PnL

↓

CanonicalState

↓

Risk

↓

Performance

PASS Criteria

Execution order remains deterministic for every lifecycle transition.

-------------------------------------------------------------------------------

Validation Group 14

CanonicalState Validation

Verify that

CanonicalState remains an operational projection only.

CanonicalState shall not own lifecycle history.

PASS Criteria

CanonicalState ownership remains unchanged compared to P1-02.

-------------------------------------------------------------------------------

# 15. Acceptance Criteria

The implementation is accepted only if

all lifecycle transitions are deterministic,

lifecycle identity is preserved,

quantity evolution is correct,

financial ownership remains unchanged,

projection ownership remains unchanged,

runtime determinism is preserved,

all validation groups pass.

-------------------------------------------------------------------------------

# 16. Implementation Sequence

Implementation Unit 1

Extend lifecycle quantity model.

-------------------------------------------------------------------------------

Implementation Unit 2

Extend LifecycleEvent.

-------------------------------------------------------------------------------

Implementation Unit 3

Implement Scale-In transitions.

-------------------------------------------------------------------------------

Implementation Unit 4

Implement Partial Close transitions.

-------------------------------------------------------------------------------

Implementation Unit 5

Implement quantity validation.

-------------------------------------------------------------------------------

Implementation Unit 6

Update Position projection.

-------------------------------------------------------------------------------

Implementation Unit 7

Update PnLEngine consumption.

-------------------------------------------------------------------------------

Implementation Unit 8

Execute validation suite.

-------------------------------------------------------------------------------

Implementation Unit 9

Certification.

-------------------------------------------------------------------------------

# 17. Scientific Conclusion

P1-03 introduces one additional runtime capability:

Quantity-aware Lifecycle Evolution.

The implementation preserves every ownership contract established during P1-02.

No additional runtime ownership is introduced.

No existing architectural responsibility is reassigned.

The implementation therefore represents a minimal scientific extension of the
certified Run Engine architecture.

-------------------------------------------------------------------------------

# 18. Internal Review

Architecture Consistency

PASS

Implementation Consistency

PASS

Ownership Consistency

PASS

Scientific Consistency Review

PASS

Minimality Review

PASS

Editorial Review

PASS

Status

Implementation Specification completed.