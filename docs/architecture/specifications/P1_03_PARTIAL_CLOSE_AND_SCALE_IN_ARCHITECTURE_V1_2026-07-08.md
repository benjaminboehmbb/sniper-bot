
# Document Metadata

Document Class:
Architecture Specification

Document ID:
P1-03-ARCH

Version:
V1.0

Status:
Draft

Date:
2026-07-08

Project:
Trading-Bot Scientific Runtime

Subsystem:
Run Engine

Primary Location:

docs/architecture/specifications/P1_03_PARTIAL_CLOSE_AND_SCALE_IN_ARCHITECTURE_V1_2026-07-08.md

Depends On:

- RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md
- RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md
- P1_03_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-08.md
- P1_03_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-08.md
- P1_03_CAPABILITY_GAP_ANALYSIS_V1_2026-07-08.md

Referenced By:

- P1_03A_PARTIAL_CLOSE_AND_SCALE_IN_SPECIFICATION_V1_2026-07-08.md

-------------------------------------------------------------------------------

# 1. Purpose

This document derives the minimal architecture required to introduce
Quantity-aware Lifecycle Evolution.

The objective is not to redesign the certified P1-02 runtime.

The objective is to extend the lifecycle architecture while preserving all
approved ownership boundaries.

The following architectural principles remain unchanged.

- CanonicalState remains the Single Source of Truth for operational runtime
  state.

- TradeLifecycleEngine remains the Authoritative Owner of lifecycle history.

- PositionEngine remains a projection layer.

- PnLEngine remains the exclusive Computational Authority for financial
  computation.

- RunLoop remains the deterministic orchestration layer.

-------------------------------------------------------------------------------

# 2. Architectural Objective

The architecture shall support one active lifecycle whose quantity may evolve
over time without changing lifecycle identity.

The lifecycle shall remain one historical object from opening until final
closure.

Quantity changes shall be represented as explicit lifecycle transitions.

-------------------------------------------------------------------------------

# 3. Architectural Invariants

The following invariants are inherited from P1-02 and remain mandatory.

Invariant A-001

Exactly one active lifecycle exists.

-------------------------------------------------------------------------------

Invariant A-002

Exactly one lifecycle identity exists for one active lifecycle.

-------------------------------------------------------------------------------

Invariant A-003

Lifecycle history remains immutable.

-------------------------------------------------------------------------------

Invariant A-004

Financial computation remains outside TradeLifecycleEngine.

-------------------------------------------------------------------------------

Invariant A-005

Operational position remains a projection.

-------------------------------------------------------------------------------

Invariant A-006

CanonicalState remains the operational runtime model.

-------------------------------------------------------------------------------

Invariant A-007

RunLoop shall preserve deterministic execution order.

-------------------------------------------------------------------------------

# 4. Required Architectural Extension

The current lifecycle model

OPEN

↓

ACTIVE

↓

CLOSED

shall evolve into

OPEN

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

The ACTIVE lifecycle therefore becomes an evolving lifecycle rather than a
constant-quantity lifecycle.

Lifecycle identity never changes.

Only lifecycle state evolves.

-------------------------------------------------------------------------------

# 5. Runtime Ownership

TradeLifecycleEngine shall additionally own

- active lifecycle quantity,
- quantity evolution,
- quantity transition history,
- quantity delta history.

TradeLifecycleEngine shall continue not to own

- realized pnl,
- unrealized pnl,
- equity,
- drawdown,
- exposure,
- performance.

Financial ownership remains exclusively assigned to PnLEngine.

-------------------------------------------------------------------------------

# 6. Quantity Model

The lifecycle shall distinguish four independent concepts.

Opening Quantity

Quantity created during TRADE_OPENED.

-------------------------------------------------------------------------------

Current Quantity

Quantity currently remaining inside the active lifecycle.

-------------------------------------------------------------------------------

Execution Quantity

Quantity represented by the current execution.

-------------------------------------------------------------------------------

Quantity Delta

Difference between previous active quantity and resulting active quantity.

These concepts shall never be represented by one shared variable.

-------------------------------------------------------------------------------

# 7. Transition Model

The minimum transition model becomes

TRADE_OPENED

↓

SCALE_IN

↓

PARTIAL_CLOSE

↓

TRADE_CLOSED

Runtime Failure Events remain available from every transition.

Each transition shall represent exactly one semantic lifecycle event.

Multiple transitions shall never be encoded into one LifecycleEvent.

-------------------------------------------------------------------------------

# 8. Transition Semantics

TRADE_OPENED

Creates a new lifecycle.

-------------------------------------------------------------------------------

SCALE_IN

Increases Current Quantity.

Lifecycle identity remains unchanged.

-------------------------------------------------------------------------------

PARTIAL_CLOSE

Reduces Current Quantity.

Lifecycle identity remains unchanged.

-------------------------------------------------------------------------------

TRADE_CLOSED

Removes remaining Current Quantity.

Terminates lifecycle.

-------------------------------------------------------------------------------

RUNTIME_FAILURE

Rejects an invalid lifecycle transition.

Lifecycle remains unchanged.

-------------------------------------------------------------------------------

# 9. Event Architecture

Every quantity-changing transition shall generate exactly one LifecycleEvent.

The LifecycleEvent becomes the only downstream representation of that
transition.

Downstream components shall never reconstruct quantity evolution.

All required facts shall already exist inside the LifecycleEvent.

-------------------------------------------------------------------------------

# 10. Position Projection

PositionEngine shall continue projecting lifecycle state.

No lifecycle interpretation shall occur inside PositionEngine.

Projection shall consume only

- side,
- current quantity,
- entry basis,
- lifecycle status.

Projection remains deterministic.

-------------------------------------------------------------------------------

# 11. Financial Architecture

PnLEngine shall consume lifecycle facts.

PnLEngine shall never infer lifecycle transitions.

PnLEngine computes financial consequences exclusively from the received
LifecycleEvent.

Financial ownership remains unchanged.

-------------------------------------------------------------------------------

# 12. Performance Architecture

PerformanceEngine shall consume realized outcomes.

PerformanceEngine shall not distinguish between

- Full Close,
- Partial Close

by reconstruction.

LifecycleEvent semantics shall already provide this information.

-------------------------------------------------------------------------------

# 13. CanonicalState

CanonicalState remains unchanged architecturally.

Only projected runtime information becomes richer.

CanonicalState shall never duplicate lifecycle history.

CanonicalState shall never compute lifecycle semantics.

-------------------------------------------------------------------------------

# 14. Architectural Minimality

The architecture intentionally excludes

- multiple active trades,
- hedge mode,
- portfolio accounting,
- reversal support,
- broker execution modelling,
- order-book modelling,
- execution simulation.

Those capabilities remain outside the architectural scope of P1-03.

-------------------------------------------------------------------------------

# 15. Architecture Validation Criteria

The architecture shall satisfy the following conditions.

One lifecycle identity survives all quantity changes.

Scale-In never creates a second lifecycle.

Partial Close never terminates the lifecycle.

Trade Closed terminates the lifecycle exactly once.

PnLEngine remains the only financial computation authority.

PositionEngine performs no lifecycle decisions.

RunLoop remains deterministic.

CanonicalState ownership remains unchanged.

-------------------------------------------------------------------------------

# 16. Scientific Conclusion

The certified P1-02 architecture already provides correct ownership,
deterministic execution and explicit lifecycle management.

P1-03 introduces exactly one additional architectural capability:

Quantity-aware Lifecycle Evolution.

No ownership changes are introduced.

No financial ownership changes are introduced.

No runtime responsibility changes are introduced outside
TradeLifecycleEngine lifecycle semantics.

The architecture therefore represents a minimal extension of the certified
P1-02 baseline while preserving all previously validated architectural
contracts.

-------------------------------------------------------------------------------

# 17. Internal Review

Architecture Consistency

PASS

Ownership Consistency

PASS

Minimality Review

PASS

Scientific Consistency Review

PASS

Implementation Independence

PASS

Editorial Review

PASS

Status

Architecture Specification completed.

