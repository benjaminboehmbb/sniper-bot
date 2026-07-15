

# Document Metadata

Document Class: Capability Gap Analysis

Document ID:
P1-03-CGA

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

docs/architecture/analysis/P1_03_CAPABILITY_GAP_ANALYSIS_V1_2026-07-08.md

Depends On:

- RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md
- RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md
- P1_03_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-08.md
- P1_03_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-08.md

Referenced By:

- P1_03_PARTIAL_CLOSE_AND_SCALE_IN_ARCHITECTURE_V1_2026-07-08.md
- P1_03A_PARTIAL_CLOSE_AND_SCALE_IN_SPECIFICATION_V1_2026-07-08.md

-------------------------------------------------------------------------------

# 1. Purpose

The Functional Requirement Analysis identified the missing runtime capability.

The Scientific Dependency Analysis derived the scientific prerequisite
structure required to introduce that capability.

The purpose of this document is to compare the certified P1-02 runtime against
those required capabilities.

The objective is not to redesign the runtime.

The objective is to determine precisely which scientific capabilities already
exist, which capabilities are only partially available and which capabilities
are completely absent.

The result of this document defines the minimum architectural work required for
P1-03.

No implementation decisions are introduced.

No interfaces are defined.

No architecture is proposed.

-------------------------------------------------------------------------------

# 2. Analysis Methodology

Every required capability is evaluated using the same process.

1. Required Scientific Capability

2. Current Repository Capability

3. Capability Comparison

4. Remaining Gap

5. Scientific Impact

6. Architectural Priority

Only capability gaps that survive this comparison become architectural work for
P1-03.

-------------------------------------------------------------------------------

# 3. Certified P1-02 Baseline

The certified runtime already provides the following capabilities.

Lifecycle ownership.

Lifecycle identity.

Deterministic lifecycle transitions.

Lifecycle event generation.

Lifecycle-derived position projection.

Lifecycle-derived realized PnL computation.

Canonical runtime synchronization.

Deterministic runtime execution.

Runtime failure reporting.

No ownership contradiction remains inside the certified P1-02 architecture.

The runtime therefore correctly represents one constant-quantity lifecycle.

-------------------------------------------------------------------------------

# 4. Capability Assessment

Capability

Lifecycle Ownership

Required

Exactly one component owns lifecycle facts.

Current State

TradeLifecycleEngine is the Authoritative Owner.

Assessment

COMPLETE

Gap

None.

Architectural Priority

None.

-------------------------------------------------------------------------------

Capability

Lifecycle Identity

Required

One lifecycle shall preserve one stable identity throughout its existence.

Current State

Every trade receives one trade identifier that remains stable until closure.

Assessment

COMPLETE

Gap

None.

Architectural Priority

None.

-------------------------------------------------------------------------------

Capability

Lifecycle Event Generation

Required

Lifecycle transitions shall produce immutable lifecycle events.

Current State

LifecycleEvent already represents immutable lifecycle facts.

Assessment

COMPLETE

Gap

None.

Architectural Priority

None.

-------------------------------------------------------------------------------

Capability

Lifecycle Projection

Required

Operational position shall be projected from lifecycle state.

Current State

PositionEngine projects lifecycle state and no longer owns lifecycle transitions.

Assessment

COMPLETE

Gap

None.

Architectural Priority

None.

-------------------------------------------------------------------------------

Capability

Financial Ownership

Required

Financial computation shall be separated from lifecycle ownership.

Current State

PnLEngine computes realized PnL from lifecycle facts.

TradeLifecycleEngine no longer computes realized PnL.

Assessment

COMPLETE

Gap

None.

Architectural Priority

None.

-------------------------------------------------------------------------------

Capability

Deterministic Runtime Sequencing

Required

Lifecycle execution shall occur through one deterministic runtime sequence.

Current State

RunLoop executes the certified lifecycle sequence established in P1-02.

Assessment

COMPLETE

Gap

None.

Architectural Priority

None.

-------------------------------------------------------------------------------

Capability

Quantity Representation

Required

The runtime shall represent active lifecycle quantity.

Current State

Trade stores a quantity value.

Assessment

PARTIALLY COMPLETE

Observed Limitation

The quantity value never changes after TRADE_OPENED.

The runtime therefore models quantity as immutable.

Scientific Impact

Quantity evolution cannot be represented.

Architectural Priority

HIGH

-------------------------------------------------------------------------------

Capability

Quantity Evolution

Required

One lifecycle shall remain active while its quantity changes.

Current State

No runtime mechanism exists.

Assessment

MISSING

Observed Limitation

Every lifecycle is assumed to have constant quantity from entry until exit.

Scientific Impact

Scale-In and Partial Close cannot exist.

Architectural Priority

CRITICAL

-------------------------------------------------------------------------------

Capability

Quantity Delta

Required

Executed quantity and active quantity shall be represented independently.

Current State

LifecycleEvent stores only one quantity value.

Assessment

MISSING

Observed Limitation

The runtime cannot distinguish:

previous quantity,

executed quantity,

remaining quantity,

resulting quantity.

Scientific Impact

Lifecycle transitions cannot be reconstructed from runtime history.

Architectural Priority

CRITICAL

-------------------------------------------------------------------------------

Capability

Scale-In

Required

An active lifecycle shall support same-direction quantity increase.

Current State

BUY while LONG generates Runtime Failure.

SELL while SHORT generates Runtime Failure.

Assessment

MISSING

Observed Limitation

Same-direction execution is interpreted as invalid behaviour.

Scientific Impact

The runtime cannot increase active exposure.

Architectural Priority

CRITICAL

-------------------------------------------------------------------------------


Capability

Partial Close

Required

An active lifecycle shall support quantity reduction while preserving lifecycle
identity.

Current State

Every opposite-direction execution terminates the active lifecycle.

Assessment

MISSING

Observed Limitation

The runtime cannot distinguish:

- reduce active quantity,
- terminate lifecycle.

Every reduction is interpreted as a complete closure.

Scientific Impact

The runtime cannot represent partial realization.

Architectural Priority

CRITICAL

-------------------------------------------------------------------------------

Capability

Full Close

Required

The runtime shall terminate a lifecycle only when the remaining active quantity
becomes zero.

Current State

TRADE_CLOSED exists.

Assessment

PARTIALLY COMPLETE

Observed Limitation

Closure assumes that the remaining quantity always equals the opening quantity.

The runtime cannot distinguish:

- complete closure,
- completion of several previous Partial Close operations.

Scientific Impact

Lifecycle semantics remain incomplete.

Architectural Priority

HIGH

-------------------------------------------------------------------------------

Capability

Partial Realization

Required

The runtime shall distinguish between realized quantity and remaining active
quantity.

Current State

Realized PnL is generated only after TRADE_CLOSED.

Assessment

MISSING

Observed Limitation

No realized outcome exists while a lifecycle remains active.

Scientific Impact

The runtime cannot correctly represent realized financial history during an
active lifecycle.

Architectural Priority

HIGH

-------------------------------------------------------------------------------

Capability

Invalid Quantity Transition Detection

Required

The runtime shall detect illegal quantity transitions before lifecycle mutation
occurs.

Examples include:

- over-close,
- negative remaining quantity,
- invalid quantity,
- unsupported reversal.

Current State

Execution quantity is never validated against active quantity.

Assessment

MISSING

Observed Limitation

Illegal quantity transitions cannot be classified correctly.

Scientific Impact

Runtime correctness depends on implementation behaviour instead of explicit
scientific rules.

Architectural Priority

HIGH

-------------------------------------------------------------------------------

Capability

Quantity-aware Position Projection

Required

PositionEngine shall project the resulting active lifecycle quantity.

Current State

Projection already exists.

Assessment

PARTIALLY COMPLETE

Observed Limitation

Projection assumes constant quantity because lifecycle quantity never evolves.

Scientific Impact

Projection architecture is correct but currently underutilized.

Architectural Priority

MEDIUM

-------------------------------------------------------------------------------

Capability

Performance Evaluation

Required

Performance shall evaluate realized lifecycle outcomes independently of lifecycle
termination.

Current State

PerformanceEngine evaluates realized results after completed trades.

Assessment

PARTIALLY COMPLETE

Observed Limitation

Partial realized outcomes do not exist.

Performance therefore cannot distinguish:

- realized quantity,
- remaining quantity,
- cumulative realization.

Scientific Impact

Scientific performance evaluation remains incomplete.

Architectural Priority

MEDIUM

-------------------------------------------------------------------------------

# 5. Root Cause Analysis

All identified capability gaps originate from one common assumption.

Current lifecycle model

OPEN

↓

ACTIVE

↓

CLOSED

The ACTIVE state assumes immutable quantity.

Consequently:

- Scale-In cannot exist.
- Partial Close cannot exist.
- Partial realization cannot exist.
- Quantity deltas cannot exist.
- Over-close cannot be detected.
- Remaining quantity cannot evolve.

Every observed deficiency is therefore derived from one missing scientific
capability rather than multiple independent architectural defects.

-------------------------------------------------------------------------------

# 6. Scientific Gap Hierarchy

Primary Gap

Quantity-aware Lifecycle Evolution

↓

Secondary Gap

Quantity Delta Representation

↓

Transition Classification

↓

Scale-In

↓

Partial Close

↓

Partial Realization

↓

Over-close Detection

↓

Quantity-aware Projection

↓

Performance Extension

This hierarchy demonstrates that introducing Quantity-aware Lifecycle Evolution
automatically enables the remaining derived capabilities without introducing
unrelated architectural concepts.

-------------------------------------------------------------------------------

# 7. Architectural Impact Assessment

RunLoop

Impact

LOW

Only deterministic orchestration changes are expected.

-------------------------------------------------------------------------------

TradeLifecycleEngine

Impact

VERY HIGH

Lifecycle transition semantics must evolve from constant-quantity to
quantity-aware lifecycle management.

-------------------------------------------------------------------------------

PositionEngine

Impact

LOW

Projection architecture remains valid.

Only richer lifecycle information becomes available.

-------------------------------------------------------------------------------

PnLEngine

Impact

MEDIUM

Financial ownership remains unchanged.

The engine consumes richer lifecycle events.

-------------------------------------------------------------------------------

RiskEngine

Impact

LOW

Consumes projected CanonicalState.

No ownership changes are expected.

-------------------------------------------------------------------------------

PerformanceEngine

Impact

MEDIUM

May evaluate realized outcomes produced by Partial Close events.

-------------------------------------------------------------------------------

CanonicalState

Impact

LOW

Canonical ownership remains unchanged.

Only projected runtime information becomes richer.

-------------------------------------------------------------------------------

# 8. Scientific Minimality Review

The identified capability gaps do not justify introduction of:

- multiple simultaneous positions,
- portfolio accounting,
- hedge mode,
- leverage redesign,
- broker abstraction,
- exchange fill modelling,
- order-book simulation,
- strategy redesign,
- multi-leg execution.

Those capabilities solve different scientific problems.

They are therefore intentionally excluded from P1-03.

The minimal architectural extension is limited to one active lifecycle whose
quantity may evolve deterministically.

-------------------------------------------------------------------------------

# 9. Scientific Readiness Assessment

Functional Requirement Analysis

PASS

Scientific Dependency Analysis

PASS

Capability Gap Identification

PASS

Gap Prioritization

PASS

Scope Definition

PASS

Architecture Definition

NOT STARTED

Implementation

NOT STARTED

-------------------------------------------------------------------------------

# 10. Conclusion

The certified P1-02 runtime remains scientifically consistent.

No ownership contradiction has been identified.

No deterministic execution contradiction has been identified.

The only fundamental missing runtime capability is:

Quantity-aware Lifecycle Evolution.

Every remaining observed deficiency is a direct consequence of this missing
capability.

The next document shall derive the minimal architecture required to introduce
Quantity-aware Lifecycle Evolution while preserving all certified ownership,
information-flow and runtime principles established during P1-02.

-------------------------------------------------------------------------------

# 11. Internal Review

Capability Identification

PASS

Gap Classification

PASS

Scientific Dependency Consistency

PASS

Minimality Review

PASS

Architecture Independence

PASS

Implementation Independence

PASS

Editorial Review

PASS

Status

Capability Gap Analysis completed.

