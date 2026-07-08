# Document Metadata

Document Class: Scientific Dependency Analysis
Document ID: P1-03-SDA
Version: V1.0
Status: Draft
Date: 2026-07-08

Project: Trading-Bot Scientific Runtime

Subsystem:
Run Engine

Primary Location:
docs/architecture/analysis/P1_03_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-08.md

Depends On:

- RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md
- RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md
- P1_03_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-08.md

Referenced By:

- P1_03_CAPABILITY_GAP_ANALYSIS_V1_2026-07-08.md
- P1_03_PARTIAL_CLOSE_AND_SCALE_IN_ARCHITECTURE_V1_2026-07-08.md
- P1_03A_PARTIAL_CLOSE_AND_SCALE_IN_SPECIFICATION_V1_2026-07-08.md

-------------------------------------------------------------------------------

# 1. Purpose

The Functional Requirement Analysis identified the missing runtime capability as
Quantity-aware Lifecycle Evolution.

Before architecture or implementation may begin, the dependency structure of
this capability must be derived.

The objective of this document is therefore not to propose a solution.

Its objective is to determine which scientific capabilities are prerequisites
for Quantity-aware Lifecycle Evolution and in which order they must become
available.

No implementation decisions are made.

No interfaces are introduced.

No runtime structures are modified.

-------------------------------------------------------------------------------

# 2. Dependency Analysis Methodology

Every candidate capability is evaluated according to the following process.

1. Scientific Definition

2. Dependency Identification

3. Upstream Requirements

4. Downstream Consumers

5. Architectural Necessity

6. Removal Test

7. Dependency Classification

Only capabilities that survive the Removal Test may become architectural
requirements for P1-03.

-------------------------------------------------------------------------------

# 3. Scientific Target Capability

Target Capability

Quantity-aware Lifecycle Evolution

Definition

A runtime capability that allows one active lifecycle to evolve while preserving
its identity as execution quantity changes over time.

Observable runtime behaviour includes:

- Scale-In
- Partial Close
- Full Close
- Invalid Quantity Transition

The capability itself is more fundamental than any of these observable
behaviours.

-------------------------------------------------------------------------------

# 4. Candidate Dependency D-001

Quantity Semantics

Definition

The runtime must possess one unambiguous definition of active quantity.

Quantity must represent the currently active exposure owned by one lifecycle.

Quantity is neither:

- execution size,
- cumulative traded volume,
- historical quantity,
- financial exposure,
- position value.

Quantity represents only the currently active lifecycle quantity.

-------------------------------------------------------------------------------

Upstream Dependencies

None.

Quantity represents a primitive lifecycle property.

-------------------------------------------------------------------------------

Downstream Consumers

- TradeLifecycleEngine
- PositionEngine
- PnLEngine
- PerformanceEngine
- Future RiskEngine extensions

-------------------------------------------------------------------------------

Removal Test

If Quantity Semantics are removed, the runtime cannot distinguish:

- Full Close
- Partial Close
- Scale-In
- Over-close
- Remaining exposure

Every quantity-changing execution becomes ambiguous.

Result

FAILED REMOVAL TEST

-------------------------------------------------------------------------------

Classification

Mandatory Primary Dependency

-------------------------------------------------------------------------------

# 5. Candidate Dependency D-002

Lifecycle Identity Preservation

Definition

A lifecycle must remain the same historical entity while its quantity evolves.

Quantity changes shall not implicitly create new lifecycle identities.

-------------------------------------------------------------------------------

Upstream Dependencies

Requires:

D-001 Quantity Semantics

-------------------------------------------------------------------------------

Downstream Consumers

- Lifecycle history
- Trade reconstruction
- Performance analysis
- Scientific replay
- Runtime auditing

-------------------------------------------------------------------------------

Removal Test

Without lifecycle identity preservation:

every Scale-In could appear to create a new trade,

every Partial Close could terminate one trade and begin another,

historical reconstruction becomes implementation dependent.

Scientific replay loses determinism.

Result

FAILED REMOVAL TEST

-------------------------------------------------------------------------------

Classification

Mandatory Dependency

-------------------------------------------------------------------------------

# 6. Candidate Dependency D-003

Quantity Delta Semantics

Definition

The runtime must distinguish between:

Current Quantity

and

Executed Quantity.

These are different scientific concepts.

Example

Current quantity

1.50 BTC

Incoming execution

SELL 0.40 BTC

Remaining quantity

1.10 BTC

The execution quantity is the delta.

The remaining quantity is lifecycle state.

-------------------------------------------------------------------------------

Upstream Dependencies

Requires

- D-001
- D-002

-------------------------------------------------------------------------------

Removal Test

Without Quantity Delta Semantics the runtime cannot determine:

- how much changed,
- what remains,
- what became realized.

Only final state remains visible.

Transition information disappears.

Result

FAILED REMOVAL TEST

-------------------------------------------------------------------------------

Classification

Mandatory Dependency

-------------------------------------------------------------------------------

# 7. Candidate Dependency D-004

Lifecycle Transition Semantics

Definition

The runtime must classify every quantity-changing execution into exactly one
lifecycle transition.

Minimum transition classes:

TRADE_OPENED

SCALE_IN

PARTIAL_CLOSE

TRADE_CLOSED

RUNTIME_FAILURE

Every execution must map deterministically onto one transition class.

-------------------------------------------------------------------------------

Upstream Dependencies

Requires

- D-001
- D-002
- D-003

-------------------------------------------------------------------------------

Removal Test

Without transition semantics:

identical executions may produce different lifecycle behaviour.

Runtime determinism is lost.

PnL calculation becomes ambiguous.

Replay consistency cannot be guaranteed.

Result

FAILED REMOVAL TEST

-------------------------------------------------------------------------------

Classification

Mandatory Dependency

-------------------------------------------------------------------------------

# 8. Candidate Dependency D-005

Partial Realization Semantics

Definition

The runtime must distinguish:

remaining unrealized lifecycle quantity

from

realized closed quantity.

These concepts become different immediately after a Partial Close.

-------------------------------------------------------------------------------

Upstream Dependencies

Requires

- D-001
- D-002
- D-003
- D-004

-------------------------------------------------------------------------------

Downstream Consumers

PnLEngine

PerformanceEngine

Future scientific analytics

-------------------------------------------------------------------------------

Removal Test

Without Partial Realization Semantics

the runtime can only compute realized outcome after complete lifecycle closure.

Partial realization disappears completely.

Scientific correctness is reduced.

Result

FAILED REMOVAL TEST

-------------------------------------------------------------------------------

Classification

Mandatory Dependency

-------------------------------------------------------------------------------

# 9. Candidate Dependency D-006

Invalid Quantity Transition Detection

Definition

The runtime must detect executions that violate lifecycle constraints.

Examples include:

closing more quantity than exists,

negative remaining quantity,

invalid same-direction transitions,

future unsupported reversal behaviour.

Invalid transitions must become explicit Runtime Failure Events.

-------------------------------------------------------------------------------

Upstream Dependencies

Requires

all previous dependencies.

-------------------------------------------------------------------------------

Removal Test

Without explicit invalid transition detection

illegal runtime states may silently enter the lifecycle history.

Scientific traceability is broken.

Repository behaviour becomes implementation dependent.

Result

FAILED REMOVAL TEST

-------------------------------------------------------------------------------

Classification

Mandatory Dependency

-------------------------------------------------------------------------------

# 10. Dependency Hierarchy

The resulting dependency graph is:

Quantity Semantics

↓

Lifecycle Identity

↓

Quantity Delta Semantics

↓

Lifecycle Transition Semantics

↓

Partial Realization Semantics

↓

Invalid Quantity Transition Detection

Every dependency requires all dependencies above it.

No dependency inversion was identified.

-------------------------------------------------------------------------------

# 11. Dependency Minimality Review

The following capabilities were evaluated but rejected as prerequisites for
P1-03.

Multiple simultaneous positions

Reason

Not required for one evolving lifecycle.

-------------------------------------------------------------------------------

Portfolio accounting

Reason

Financial aggregation is downstream of lifecycle evolution.

-------------------------------------------------------------------------------

Order-book simulation

Reason

Execution modelling is independent of lifecycle quantity evolution.

-------------------------------------------------------------------------------

Exchange fill modelling

Reason

Exchange behaviour is not required to derive lifecycle semantics.

-------------------------------------------------------------------------------

Multi-asset support

Reason

Asset abstraction already exists.

Quantity evolution is asset-independent.

-------------------------------------------------------------------------------

Reversal support

Reason

Reversal introduces an additional capability beyond quantity evolution.

Current architecture may classify reversal attempts as Runtime Failure Events.

Reversal therefore remains outside P1-03.

-------------------------------------------------------------------------------

# 12. Scientific Conclusion

The Functional Requirement Analysis identified one missing runtime capability:

Quantity-aware Lifecycle Evolution.

The Scientific Dependency Analysis demonstrates that this capability depends on
six mandatory prerequisite capabilities.

The dependency chain is linear.

No circular dependencies were identified.

No architectural contradiction was identified.

The highest-priority prerequisite is Quantity Semantics.

Every remaining dependency is derived from this foundation.

Architecture work may therefore begin only after these dependencies have been
accepted as the scientific basis of P1-03.

-------------------------------------------------------------------------------

# 13. Internal Consistency Review

Scientific Dependency Analysis

PASS

Dependency Ordering

PASS

Removal Test

PASS

Architecture Independence

PASS

Implementation Independence

PASS

Editorial Review

PASS

Status

Scientific Dependency Analysis completed.

