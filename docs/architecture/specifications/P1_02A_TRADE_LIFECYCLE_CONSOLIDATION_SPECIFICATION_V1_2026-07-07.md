# P1_02A_TRADE_LIFECYCLE_CONSOLIDATION_SPECIFICATION_V1_2026-07-07

---

# Document Metadata

**Document Class**

Implementation Specification

**Repository Location**

```text
docs/architecture/specifications/
```

**Filename**

```text
P1_02A_TRADE_LIFECYCLE_CONSOLIDATION_SPECIFICATION_V1_2026-07-07.md
```

**Status**

Implementation Preparation

**Implementation Phase**

P1-02 — TradeLifecycle Consolidation

**Depends On**

* RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md
* RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md

**Referenced By**

* P1-02 Implementation
* P1-02 Validation
* P1-02 Certification

---

# 1. Objective

This specification defines the implementation contract for TradeLifecycle Consolidation.

Its purpose is to transform the current runtime implementation into the architecture defined by the approved Run Engine Architecture Baseline.

The specification defines implementation responsibilities, integration order, validation requirements and implementation boundaries.

No architectural decisions are introduced or modified by this document.

---

# 2. Scope

This specification covers only the implementation activities required for P1-02.

Included:

* TradeLifecycleEngine integration
* RunLoop integration
* Position responsibility consolidation
* Lifecycle event generation
* Runtime information flow adaptation
* Validation activities

Excluded:

* Financial ownership consolidation
* Risk ownership consolidation
* Performance ownership consolidation
* Information Flow Consolidation beyond TradeLifecycle integration
* Repository cleanup
* Runtime optimization
* Performance optimization

No functionality outside the defined implementation scope shall be modified during P1-02.

These activities belong to later implementation phases.

---

# 3. Architectural References

This implementation shall remain fully consistent with the approved architecture.

Primary governing Architecture Decision Records:

* ADR-002 Runtime Information Flow
* ADR-003 Trade Lifecycle
* ADR-004 Position Ownership
* ADR-005 Financial Ownership
* ADR-009 Lifecycle Transition Semantics
* ADR-010 Deterministic Runtime Execution
* ADR-011 Runtime Failure Handling

If implementation and architecture conflict, the Architecture Baseline shall always take precedence.

---

# 4. Current Implementation State

Repository analysis identified the following current runtime structure.

RunLoop currently performs deterministic execution sequencing.

TradeLifecycleEngine already exists as an independent runtime component.

PnLEngine already consumes lifecycle-derived trade events.

PositionEngine still performs operational lifecycle responsibilities that belong to TradeLifecycleEngine.

As a consequence, lifecycle responsibilities remain distributed across multiple runtime components.

This implementation phase removes that responsibility overlap while preserving deterministic runtime behaviour.

---

# 5. Target Implementation State

After completion of P1-02:

* TradeLifecycleEngine becomes the single operational authority for lifecycle transitions.
* Trade events originate exclusively from TradeLifecycleEngine.
* PositionEngine no longer performs lifecycle state transitions.
* PositionEngine becomes a projection of lifecycle state.
* PnLEngine consumes lifecycle-generated trade events.
* RunLoop follows the deterministic execution sequence defined by ADR-010.
* CanonicalState continues to represent the authoritative operational runtime state.

After certification, lifecycle state shall have exactly one operational source of truth throughout the runtime.

# 6. Target Runtime Information Flow

The implementation shall establish the following deterministic runtime execution sequence.

```text
StateEngine
        │
        ▼
RegimeClassifier
        │
        ▼
StrategySelector
        │
        ▼
Decision
        │
        ▼
Executor
        │
        ▼
TradeLifecycleEngine
        │
        ├── Lifecycle State
        ├── Trade Event
        ├── Position State
        └── Realized PnL
                 │
                 ▼
PositionEngine (Projection)
                 │
                 ▼
PnLEngine
                 │
                 ▼
Financial State
                 │
                 ▼
RiskEngine
                 │
                 ▼
PerformanceEngine
                 │
                 ▼
CanonicalState Update
                 │
                 ▼
Tick-Complete CanonicalState Snapshot
```

No runtime component may bypass this sequence.

---

# 7. Component Responsibilities

## RunLoop

Responsibilities:

* deterministic execution sequencing,
* component orchestration,
* CanonicalState coordination,
* tick completion.

RunLoop shall not implement lifecycle business logic.

---

## TradeLifecycleEngine

Responsibilities:

* lifecycle transitions,
* trade creation,
* trade closing,
* lifecycle validation,
* lifecycle event generation,
* realized PnL generation,
* operational position ownership.

TradeLifecycleEngine becomes the operational source of truth for lifecycle state.

---

## PositionEngine

Responsibilities:

* lifecycle state projection,
* runtime position representation,
* canonical position view.

PositionEngine shall no longer perform lifecycle transitions.

PositionEngine shall not open or close trades.

---

## PnLEngine

Responsibilities:

* consume lifecycle-generated trade events,
* calculate realized PnL,
* publish financial information.

PnLEngine shall never reconstruct lifecycle state independently.

---

## CanonicalState

Responsibilities:

* authoritative operational runtime state,
* deterministic runtime representation,
* tick-complete publication.

CanonicalState shall store implementation results but shall not generate lifecycle decisions.

---

# 8. Implementation Sequence

Implementation shall proceed in the following order.

Step 1

TradeLifecycleEngine

* API completion
* lifecycle event contract
* transition verification

Validation required.

---

Step 2

PositionEngine

* remove lifecycle transitions
* convert to projection model

Validation required.

---

Step 3

RunLoop

* integrate TradeLifecycleEngine
* remove obsolete lifecycle handling
* update execution ordering

Validation required.

---

Step 4

PnLEngine verification

* verify lifecycle event integration
* verify realized PnL generation

Validation required.

Implementation shall not change more than one implementation unit before validation has completed.

---

# 9. Validation Strategy

Every implementation step requires:

* Python compilation,
* import validation,
* deterministic runtime validation,
* architecture compliance verification,
* regression verification,
* git diff verification.

No implementation step may proceed after a failed validation.

---

# 10. Rollback Strategy

Every completed implementation unit shall produce:

* one validated Git commit,
* one verified rollback point,
* one implementation validation result.

Rollback shall always restore the last certified implementation state.

Rollback procedures shall never bypass validated repository history.

# 11. Implementation Checklist

The following implementation checklist shall be completed before P1-02 certification.

| Item                                                | Required |
| --------------------------------------------------- | -------- |
| TradeLifecycleEngine API completed                  | PASS     |
| Lifecycle Event Contract implemented                | PASS     |
| Lifecycle transition validation completed           | PASS     |
| PositionEngine converted to projection model        | PASS     |
| PositionEngine lifecycle logic removed              | PASS     |
| RunLoop integrated with TradeLifecycleEngine        | PASS     |
| PnLEngine consumes lifecycle-generated trade events | PASS     |
| Runtime execution sequence verified                 | PASS     |
| Deterministic runtime behaviour verified            | PASS     |
| Compile validation PASS                             | PASS     |
| Import validation PASS                              | PASS     |
| Runtime validation PASS                             | PASS     |
| Regression validation PASS                          | PASS     |
| Git diff verification PASS                          | PASS     |
| Repository rollback point created                   | PASS     |

P1-02 shall not be certified until every checklist item has passed.

---

# 12. Definition of Done

P1-02 is complete only when all of the following conditions are satisfied.

Functional completion:

* TradeLifecycleEngine is fully integrated into the active runtime path.
* Lifecycle transitions originate exclusively from TradeLifecycleEngine.
* PositionEngine performs projection only.
* RunLoop executes the approved deterministic lifecycle sequence.
* PnLEngine consumes lifecycle-generated trade events.
* CanonicalState remains the authoritative operational runtime state.

Validation completion:

* Static Validation PASS.
* Architectural Validation PASS.
* Runtime Validation PASS.
* Regression Validation PASS.

Governance completion:

* Repository synchronized.
* Git rollback point available.
* Validation evidence archived.
* P1-02 Certification approved.

Partial completion shall never be interpreted as implementation completion.

---

# 13. Certification Criteria

P1-02 certification requires objective implementation evidence.

Certification shall confirm that:

* implementation conforms to the approved Run Engine Architecture Baseline,
* implementation conforms to the Run Engine Implementation Baseline,
* lifecycle ownership is unique,
* runtime execution remains deterministic,
* information flow remains architecture compliant,
* no duplicate operational ownership exists,
* validation evidence is complete.

Certification shall be evidence-based.

Architecture compliance shall be verified against the approved Run Engine Architecture Baseline before P1-02 certification is granted.

---

# 14. Transition to P1-03

Successful completion of P1-02 authorizes the start of P1-03.

P1-03 continues implementation using the certified lifecycle foundation established during P1-02.

No P1-03 implementation activity may begin before P1-02 certification has been successfully completed.

The certified P1-02 implementation becomes the mandatory implementation baseline for all subsequent implementation phases.

# Appendix A – Implementation Order

The following file order shall be used during P1-02 implementation.

| Order | File                                 | Purpose                                                        |
| ----: | ------------------------------------ | -------------------------------------------------------------- |
|     1 | `run_engine/core/trade_lifecycle.py` | Complete lifecycle ownership and event contract                |
|     2 | `run_engine/core/position.py`        | Convert to Position Projection                                 |
|     3 | `run_engine/core/loop.py`            | Integrate TradeLifecycleEngine into the active runtime path    |
|     4 | `run_engine/core/pnl.py`             | Verify lifecycle event consumption and realized PnL generation |

Each file shall be completed and validated before the next file is modified.

---

# Appendix B – Validation Evidence

The following evidence shall be archived after every implementation step.

* Python compilation result
* Import validation result
* Runtime validation result
* Architecture compliance result
* Git diff verification
* Git commit identifier
* Rollback verification

Implementation evidence shall remain traceable to the corresponding implementation unit.

---

# Appendix C – Implementation Constraints

The following implementation constraints are mandatory.

* No architectural modifications.
* No implementation shortcuts.
* No duplicate operational ownership.
* No bypass of deterministic execution order.
* No modification of unrelated runtime components.
* One implementation unit at a time.
* Validation before every commit.
* Certification before the next implementation phase.

These constraints remain in force throughout the complete P1 implementation phase.

