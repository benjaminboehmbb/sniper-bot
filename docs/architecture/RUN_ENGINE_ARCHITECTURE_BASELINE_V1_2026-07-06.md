# RUN_ENGINE_ARCHITECTURE_BASELINE_V1

---

# Document Metadata

**Document Class**

Scientific Software Architecture Baseline

---

**Project**

Trading-Bot Scientific Runtime

---

**Subsystem**

Run Engine

---

**Document ID**

RUN_ENGINE_ARCHITECTURE_BASELINE_V1

---

**Version**

Working Baseline V1

---

**Status**

Architecture Working Baseline

---

**Repository**

sniper-bot

---

**Primary Location**

`docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md`

---

**Architecture Scope**

Complete runtime execution architecture responsible for transforming incoming market observations into deterministic, scientifically traceable trading actions.

---

**Related Standards**

- Scientific Compute Governance (SCG)
- Scientific Governance Framework (SGF)
- Scientific Derivation Methodology (SDM)

---

**Repository Safety Baseline**

Development Branch

`run-engine-consolidation-safety`

Repository Safety

PASS

Compilation

PASS

Import Validation

PASS

Repository Analysis

Completed

Codex Technical Repository Review

Completed

Independent Architecture Review

Planned after completion of this baseline

---

# Scientific Purpose

The Run Engine is the deterministic execution architecture responsible for transforming market observations into validated runtime actions while maintaining complete scientific traceability throughout every execution step.

The Run Engine is not responsible for:

- market prediction,
- strategy research,
- parameter optimization,
- machine learning.

Its sole responsibility is the deterministic execution of already established trading logic.

The architecture therefore prioritizes:

- deterministic execution,
- explicit information ownership,
- scientific traceability,
- reproducibility,
- architectural consistency,
- minimal ownership duplication,
- explainability.

Implementation convenience shall never override architectural correctness.

---

# Scope

This baseline governs the active runtime execution architecture contained within the repository.

The current consolidation scope begins at

```text
run_engine/main.py
```

and continues through the active runtime implementation located under

```text
run_engine/core/
```

The purpose of this baseline is not to redesign the runtime.

Its purpose is to consolidate the existing implementation into one scientifically consistent execution architecture while preserving validated functionality whenever architecturally justified.

Legacy implementations and competing runtime structures remain outside the current consolidation scope until the active runtime architecture has been stabilized.

---

# Architectural Philosophy

The Run Engine shall evolve according to scientific architectural principles rather than implementation convenience.

Every runtime component shall possess one clearly defined primary responsibility.

Every runtime information object shall possess exactly one authoritative owner.

Whenever ownership ambiguity exists, the architecture shall be modified until ownership becomes explicit.

Architectural simplicity is considered an engineering objective.

Additional complexity shall only be introduced when it creates demonstrably necessary scientific capability.

Equivalent architectural capability shall always be implemented using the simpler architecture.

---

# Scientific Design Principles

## Principle 1 — Single Responsibility

Every runtime component performs one primary scientific responsibility.

Responsibilities shall not overlap.

---

## Principle 2 — Explicit Information Ownership

Every runtime information object possesses exactly one Authoritative Owner.

Ownership shall never depend on execution order.

Duplicate ownership is prohibited.

---

## Principle 3 — Canonical Runtime State

The architecture maintains exactly one authoritative active runtime state.

All other runtime representations are derived views.

CanonicalState SHALL become the Single Source of Truth for active runtime information.

---

## Principle 4 — Deterministic Runtime Behaviour

Identical runtime inputs shall always produce identical runtime outputs.

Hidden mutable state shall be eliminated wherever architecturally possible.

Implicit side effects shall be minimized.

---

## Principle 5 — Event-Driven Runtime Evolution

Runtime state evolves only through explicit Runtime Events or explicitly approved CanonicalState updates.

Implicit runtime mutations are prohibited.

---

## Principle 6 — Scientific Traceability

Every runtime output shall be traceable through:

- originating observation,
- runtime state,
- execution decision,
- lifecycle transition,
- financial accounting,
- risk evaluation,
- resulting runtime state.

No runtime result shall exist without a complete derivation path.

---

# Repository Status at Baseline Creation

Repository Safety Branch

PASS

Current Runtime committed

PASS

Remote Backup

PASS

Compilation

PASS

Import Validation

PASS

Repository Inspection

Completed

Codex Repository Review

Completed

Architecture Diagnosis

Completed

No implementation work had begun when this architectural baseline was established.

This document therefore represents the governing architectural baseline for all subsequent Run Engine consolidation work.

# Current Repository State

---

# Purpose of this Section

This section documents the verified architectural state of the repository at the time this baseline was established.

Its purpose is descriptive rather than prescriptive.

Only observations supported by repository inspection, engineering validation and independent repository review are included.

No architectural decisions are introduced in this section.

Architectural conclusions are deferred until the Scientific Architecture Diagnosis.

---

# Repository Validation

The following validation activities were completed before architectural consolidation began.

## Repository Safety

Verified.

A dedicated safety branch was created before any architectural modification.

The complete runtime implementation was committed locally and remotely before architectural work began.

The baseline implementation therefore remains fully recoverable.

---

## Repository Integrity

Verified.

Repository compilation completed successfully.

Import validation completed successfully.

No syntax errors preventing architectural investigation were detected.

Repository analysis therefore proceeded from an executable code base.

---

## Independent Repository Review

Verified.

An independent technical repository review was performed using Codex.

Codex was instructed to:

- reconstruct the active execution path,
- identify ownership conflicts,
- identify duplicated responsibilities,
- identify inactive competing implementations,
- identify integration defects,

while explicitly avoiding:

- architectural redesign,
- feature implementation,
- source code modification.

The Codex review is treated as an independent technical observation rather than an architectural authority.

Architectural conclusions remain governed by this baseline.

---

# Verified Active Execution Path

Repository inspection confirms one primary execution path.

```text
run_engine/main.py

↓

RunLoop

↓

StateEngine

↓

RegimeClassifier

↓

StrategySelector

↓

Executor

↓

TradeLifecycleEngine

↓

PositionEngine

↓

PnLEngine

↓

RiskEngine

↓

PerformanceEngine

↓

CanonicalState
```

This represents the intended active runtime execution pipeline governed by this baseline.

Competing implementations outside this path are intentionally excluded from the current consolidation scope.

---

# Verified Active Runtime Modules

## Runtime Entry

```text
run_engine/main.py
```

Responsibility

- initialize runtime,
- receive runtime ticks,
- invoke RunLoop.

---

## RunLoop

```text
run_engine/core/loop.py
```

Responsibility

- deterministic orchestration,
- execution sequencing,
- runtime coordination.

Repository analysis indicates that RunLoop still contains several embedded responsibilities that should later migrate into dedicated runtime components.

---

## StateEngine

```text
run_engine/core/state.py
```

Responsibility

- normalize observations,
- construct runtime state representation.

No significant ownership conflicts were identified.

---

## RegimeClassifier

```text
run_engine/core/regime.py
```

Responsibility

- classify current market regime.

Consumes StateEngine output.

---

## StrategySelector

```text
run_engine/core/strategy.py
```

Responsibility

- transform runtime state into execution decisions.

Current implementation combines weighting and decision generation but remains internally coherent.

---

## Executor

```text
run_engine/core/execution/executor.py
```

Responsibility

- transform execution decisions into execution events.

Repository inspection confirms that Executor no longer performs direct Position mutation.

---

## TradeLifecycleEngine

Repository inspection confirms that lifecycle infrastructure already exists.

Current integration into the active runtime path remains incomplete.

Lifecycle infrastructure therefore represents an existing architectural capability that requires integration rather than redesign.

---

## PositionEngine

```text
run_engine/core/position.py
```

Responsibility

- maintain current operational Position.

Repository inspection confirms separation between pre-trade and post-trade updates.

---

## PnLEngine

```text
run_engine/core/pnl.py
```

Responsibility

- calculate financial consequences of lifecycle events.

Repository inspection indicates that lifecycle-based accounting already exists conceptually but is not yet fully integrated into the active execution path.

---

## RiskEngine

```text
run_engine/core/risk.py
```

Responsibility

- evaluate runtime risk.

Repository analysis indicates remaining ownership ambiguity regarding financial runtime state.

---

## PerformanceEngine

```text
run_engine/core/performance.py
```

Responsibility

- evaluate realized trading performance.

Current implementation still evaluates runtime decisions more strongly than completed lifecycle outcomes.

---

## CanonicalState

```text
run_engine/core/canonical_state.py
run_engine/core/canonical_enforcer.py
```

Responsibility

- maintain centralized active runtime state.

Repository inspection confirms that CanonicalState provides the structural basis for centralized ownership.

Current implementation still behaves primarily as a synchronized runtime snapshot rather than the complete authoritative runtime state.

---

# Verified Architectural Observations

Observation O-001

One primary runtime execution path exists.

---

Observation O-002

TradeLifecycle infrastructure already exists.

---

Observation O-003

TradeLifecycle is not yet fully integrated into the active runtime execution path.

---

Observation O-004

CanonicalState infrastructure already exists.

---

Observation O-005

CanonicalState is not yet the complete Authoritative Owner of active runtime information.

---

Observation O-006

Multiple runtime components still maintain partially overlapping mutable runtime state.

---

Observation O-007

PnLEngine has already evolved toward lifecycle-oriented accounting.

---

Observation O-008

RunLoop currently bypasses parts of the lifecycle infrastructure.

---

Observation O-009

Risk evaluation still depends on partially duplicated ownership.

---

Observation O-010

Performance evaluation is currently more decision-oriented than lifecycle-oriented.

---

# Scientific Findings

SF-001

The repository already contains most major runtime capabilities.

---

SF-002

The principal architectural problem is incomplete integration rather than missing functionality.

---

SF-003

Ownership ambiguity represents the dominant architectural weakness.

---

SF-004

The existing implementation provides a scientifically suitable foundation for architectural consolidation rather than architectural replacement.

---

# Internal Review

Architecture Review

PASS

Scientific Consistency Review

PASS

Editorial Review

PASS

Status

Current Repository State completed.

# Scientific Architecture Diagnosis

---

# Purpose of this Section

The purpose of this section is to identify and formally describe the architectural deficiencies of the current Run Engine.

Unlike the previous section, this chapter evaluates the observed runtime architecture against the scientific design principles established in this baseline.

No implementation decisions are introduced.

No corrective actions are proposed.

The objective is to establish a scientifically justified diagnosis explaining why architectural consolidation is required.

---

# Diagnostic Methodology

Every architectural defect is evaluated using the following process.

1. Repository Observation
2. Ownership Analysis
3. Information Flow Analysis
4. Responsibility Analysis
5. Scientific Consistency Evaluation
6. Architectural Consequence Assessment

Only after all significant architectural deficiencies have been diagnosed may Architecture Decision Records (ADRs) be introduced.

---

# Architecture Defect AD-001

## Missing Lifecycle Integration

### Repository Situation

TradeLifecycle infrastructure already exists inside the repository.

However, the active runtime execution path still bypasses parts of that infrastructure.

Trade evolution therefore exists physically but not architecturally.

---

### Scientific Diagnosis

A scientific runtime architecture requires explicit lifecycle representation.

Without lifecycle integration the runtime cannot distinguish between:

- trade creation,
- trade evolution,
- partial close,
- full close,
- realized financial outcome,
- historical execution record.

These concepts become implicit implementation behaviour instead of explicit runtime semantics.

---

### Scientific Consequences

- lifecycle traceability becomes incomplete,
- realized PnL cannot be derived exclusively from lifecycle facts,
- performance becomes partially disconnected from realized execution,
- future explainability becomes weaker.

---

### Severity

Critical

---

# Architecture Defect AD-002

## Fragmented Runtime Ownership

### Repository Situation

Multiple runtime components currently maintain partially overlapping mutable runtime state.

Ownership is distributed across:

- PositionEngine
- PnLEngine
- RiskEngine
- PerformanceEngine
- CanonicalState

---

### Scientific Diagnosis

Scientific systems require unique ownership.

The architectural problem is not duplicated information.

The architectural problem is duplicated authority.

Whenever two components can legitimately claim ownership of identical runtime information, deterministic reasoning becomes dependent upon implementation details.

---

### Scientific Consequences

- execution-order dependency,
- synchronization complexity,
- increased maintenance effort,
- reduced architectural clarity,
- reduced reproducibility.

---

### Severity

Critical

---

# Architecture Defect AD-003

## CanonicalState Is Not Yet the Authoritative Runtime State

### Repository Situation

CanonicalState already exists.

However, several runtime components still maintain independent authoritative runtime information.

CanonicalState therefore behaves primarily as a synchronized runtime snapshot.

---

### Scientific Diagnosis

Canonical storage alone does not establish architectural consistency.

Scientific consistency requires canonical ownership.

Without unique ownership, runtime consumers cannot determine which representation constitutes authoritative runtime truth.

---

### Scientific Consequences

- ownership ambiguity,
- hidden coupling,
- duplicated mutable state,
- increased implementation complexity,
- reduced auditability.

---

### Severity

Critical

---

# Architecture Defect AD-004

## Incomplete Information Flow

### Repository Situation

Several runtime components reconstruct information already available earlier in the execution pipeline.

Semantic information is therefore partially lost and later recreated.

---

### Scientific Diagnosis

Scientific runtime systems shall preserve semantic continuity.

Runtime information shall never require downstream reconstruction when it already exists upstream.

Every reconstruction introduces unnecessary coupling.

---

### Scientific Consequences

- weaker explainability,
- duplicated interpretation,
- unnecessary computational complexity,
- increased architectural coupling.

---

### Severity

Critical

---

# Architecture Defect AD-005

## Decision-Oriented Performance Evaluation

### Repository Situation

Performance evaluation is currently influenced by runtime decisions instead of exclusively by realized lifecycle outcomes.

---

### Scientific Diagnosis

Runtime decisions represent intentions.

Trading performance represents realized outcomes.

These concepts are scientifically different.

Performance shall therefore evaluate realized execution rather than intended execution.

---

### Scientific Consequences

- misleading trade statistics,
- ambiguous win rate,
- reduced statistical validity,
- weaker scientific evaluation.

---

### Severity

Important

---

# Architecture Defect AD-006

## Distributed Financial Ownership

### Repository Situation

Financial runtime information currently participates in multiple update paths.

Equity ownership is not yet formally consolidated.

---

### Scientific Diagnosis

Financial runtime state represents cumulative system state.

Cumulative quantities require exactly one authoritative ownership path.

Duplicate ownership introduces financial inconsistency risk.

---

### Scientific Consequences

- execution-order dependency,
- increased accounting complexity,
- reduced reproducibility,
- more difficult validation.

---

### Severity

Important

---

# Architecture Defect AD-007

## Parallel Runtime Architectures

### Repository Situation

Repository inspection identified several partially overlapping runtime implementations.

Only one participates in the active runtime execution path.

---

### Scientific Diagnosis

Parallel implementations are acceptable during architectural evolution.

However, every competing implementation must eventually receive one explicit classification:

- active,
- integrated,
- archived,
- removed.

---

### Scientific Consequences

Without classification:

- repository complexity increases,
- architectural reviews become slower,
- inactive implementations may accidentally re-enter production.

---

### Severity

Important

---

# Ownership Violations

OV-001

Trade ownership is incomplete.

---

OV-002

Financial ownership remains partially fragmented.

---

OV-003

Performance ownership is not yet fully lifecycle-oriented.

---

OV-004

Canonical runtime ownership is not yet complete.

---

# Hidden Coupling Analysis

Repository analysis identified four principal forms of hidden coupling.

---

Lifecycle Coupling

Financial accounting depends upon lifecycle semantics without explicit lifecycle integration.

---

State Synchronization Coupling

Multiple runtime components maintain overlapping mutable runtime information.

---

Execution Order Coupling

Correct runtime behaviour currently depends upon execution ordering rather than explicit architectural contracts.

---

Semantic Coupling

Multiple runtime components currently interpret concepts such as Position, Exposure, Equity and Trade without one formally defined semantic owner.

---

# Scientific Conclusions

The repository should not be regarded as architecturally incorrect.

Repository analysis instead indicates an implementation that already contains most required architectural capabilities but has not yet completed its transition toward explicit ownership.

Consequently, repository evolution shall prioritize:

- lifecycle integration,
- ownership consolidation,
- deterministic information flow,
- canonical runtime ownership,

rather than architectural redesign.

---

# Scientific Findings

SF-005

Ownership ambiguity represents the principal architectural risk.

---

SF-006

Lifecycle integration provides the highest architectural value.

---

SF-007

Canonical ownership creates greater long-term benefit than introducing additional runtime functionality.

---

SF-008

The existing runtime implementation provides a scientifically valid foundation for architectural consolidation.

---

# Internal Review

Architecture Review

PASS

Scientific Consistency Review

PASS

Ownership Review

PASS

Editorial Review

PASS

Status

Scientific Architecture Diagnosis completed.

# Architecture Decisions

---

# Purpose of this Section

This section transforms the scientific diagnosis into binding architectural decisions.

Unlike observations, findings or review comments, every Architecture Decision Record (ADR) defined in this section represents a normative architectural contract.

Future implementation shall conform to these decisions unless they are explicitly superseded through an Architecture Evolution Review.

The purpose of these ADRs is not to redesign the Run Engine.

Their purpose is to establish one internally consistent scientific runtime architecture with:

- explicit ownership,
- deterministic execution,
- explicit information flow,
- complete traceability,
- reproducible runtime behaviour.

Every ADR therefore specifies:

- Motivation
- Decision
- Scientific Justification
- Architectural Consequences
- Acceptance Criteria

Together these ADRs form the governing architectural contract for every subsequent implementation activity.

---

# Ownership Terminology

The following terminology is normative throughout this baseline.

---

## Single Source of Truth

Single Source of Truth (SSOT) is an architectural property.

It means that the active runtime architecture exposes exactly one authoritative operational state model.

In this baseline, CanonicalState is the SSOT for active runtime state.

SSOT does not mean that CanonicalState computes all values.

SSOT does not mean that CanonicalState owns historical lifecycle facts.

---

## Authoritative Owner

The Authoritative Owner owns the semantic truth of one runtime information object.

Exactly one Authoritative Owner shall exist for every runtime information object.

Ownership includes:

- semantic definition,
- consistency responsibility,
- lifecycle responsibility where applicable.

---

## Computational Authority

The Computational Authority exclusively computes a runtime value.

Computation does not imply ownership.

A computed value becomes canonical only after publication to the Authoritative Owner or CanonicalState where applicable.

---

## Writer-on-Behalf-Of

A Writer-on-Behalf-Of publishes computed information into CanonicalState.

Writing does not establish ownership.

The Writer transfers already-authoritative computation results into canonical runtime storage.

---

## Canonical Storage

Canonical Storage is the physical or structural representation of active runtime state.

CanonicalState is the Canonical Storage for active runtime state.

Canonical Storage stores operational truth but does not automatically become the Computational Authority for every stored value.

---

## Derived View

A Derived View is reconstructed from authoritative runtime information.

Derived Views possess no independent ownership.

They may be regenerated at any time.

---

## Canonical Working State

Canonical Working State is the internal canonical state under construction during one runtime tick.

It may be consumed only by components whose execution order has already been reached.

It is not externally observable.

---

## Tick-Complete Snapshot

A Tick-Complete Snapshot is the externally observable canonical runtime state after all mandatory runtime stages have completed for the current tick.

RiskEngine and PerformanceEngine consume the Canonical Working State at their assigned execution stage.

External downstream consumers consume only Tick-Complete Snapshots.

No component may consume state from a future or incomplete execution stage.

---

# Runtime Scope Clarification

The runtime architecture distinguishes two complementary authoritative models.

---

## CanonicalState

CanonicalState is the Single Source of Truth for the active runtime state.

CanonicalState answers the question:

> "What is true now?"

CanonicalState contains only operational runtime information.

---

## TradeLifecycleEngine

TradeLifecycleEngine is the Authoritative Owner of historical trade evolution.

TradeLifecycleEngine answers the question:

> "How did we arrive here?"

TradeLifecycleEngine owns:

- trade identifiers,
- lifecycle states,
- lifecycle transitions,
- entry facts,
- exit facts,
- immutable lifecycle history.

TradeLifecycleEngine does not own:

- Position,
- Equity,
- Risk,
- Performance,
- operational runtime state.

The two architectural models are complementary rather than competing.

---

# ADR-001

## CanonicalState as the Single Source of Truth

### Motivation

Repository analysis identified fragmented runtime ownership distributed across multiple runtime components.

Although CanonicalState already exists, it currently behaves primarily as a synchronized runtime snapshot instead of the authoritative runtime state.

Scientific runtime architectures require one unambiguous operational truth.

---

### Decision

CanonicalState SHALL become the Single Source of Truth (SSOT) for the complete active runtime state.

Every runtime component shall either:

- compute runtime information,
- consume runtime information,

but shall never maintain competing authoritative runtime state.

CanonicalState SHALL contain the authoritative representation of:

- Position,
- Equity,
- Peak Equity,
- Drawdown,
- Risk Metrics,
Runtime Status represents the current operational execution status of the Run Engine.

Examples include:

- Initializing
- Running
- Paused
- Stopping
- Stopped
- Error

RunLoop is the exclusive Computational Authority for Runtime Status.

Strategy Context and Execution Context are transient runtime artefacts.

They may participate in runtime processing but are not required to become part of the canonical operational runtime state.

Only information required to reconstruct the current operational runtime state shall be stored within CanonicalState.

Historical lifecycle information remains exclusively owned by TradeLifecycleEngine.

CanonicalState may reference lifecycle entities through stable identifiers but shall never duplicate lifecycle history.

---

### Scientific Justification

Scientific reproducibility requires unique ownership.

Separating operational runtime state from immutable historical lifecycle information eliminates ownership ambiguity while preserving complete traceability.

CanonicalState therefore becomes the authoritative operational model.

TradeLifecycleEngine becomes the authoritative historical model.

---

### Architectural Consequences

CanonicalState becomes the authoritative operational runtime model.

TradeLifecycleEngine remains the authoritative historical runtime model.

PositionEngine becomes the Computational Authority for Position.

PnLEngine becomes the Computational Authority for financial state.

RiskEngine becomes a pure computational consumer.

PerformanceEngine evaluates completed lifecycle outcomes.

No future runtime component may introduce competing authoritative runtime state without an Architecture Evolution Review.

---

### Acceptance Criteria

- Exactly one Authoritative Owner exists for every active runtime information object.
- CanonicalState contains the complete active runtime state.
- TradeLifecycleEngine contains the complete immutable lifecycle history.
- Active runtime information is never duplicated across authoritative owners.
- Historical lifecycle information never exists inside CanonicalState.
- Runtime consumers access operational runtime state exclusively through CanonicalState.
- Historical consumers access lifecycle information exclusively through TradeLifecycleEngine.
- No competing long-term mutable runtime state exists.

# ADR-002

## Event-Driven Runtime Evolution

### Motivation

Repository analysis demonstrated that semantic information is currently lost between execution, lifecycle processing, financial accounting and downstream evaluation.

Several runtime components reconstruct information that already existed earlier in the execution pipeline.

Scientific runtime architectures shall preserve semantic continuity rather than reconstruct runtime meaning.

---

### Decision

The runtime SHALL evolve exclusively through explicit Runtime Events and explicitly approved CanonicalState updates.

Every state transition shall be represented by one deterministic Runtime Event.

The minimum event model consists of:

**Observation Events**

- Market Observation
- Runtime Tick
- State Updated

---

**Decision Events**


- Regime Classified
- Strategy Selected
- Execution Decision Generated

Decision Events terminate before execution begins.

---

**Execution Events**

- Order Submitted
- Order Accepted
- Order Rejected
- Order Executed

Execution Events are generated by Executor.

---

**Trade Lifecycle Events**

- Trade Opened
- Trade Updated
- Partial Close
- Full Close
- Runtime Failure Event

Trade Lifecycle Events are generated exclusively by TradeLifecycleEngine from Execution Events.

---

**Financial Events**

- Realized PnL Updated
- Unrealized PnL Updated
- Equity Updated
- Peak Equity Updated
- Drawdown Updated

---

**Risk Events**

- Risk Evaluated

---

**Performance Events**

- Performance Updated

Every Runtime Event shall represent exactly one semantic transition.

One Runtime Event shall never represent multiple architectural responsibilities.

Runtime Event hierarchy is normative.

Market Observation
        ↓
Decision Events
        ↓
Execution Events
        ↓
Trade Lifecycle Events
        ↓
Financial Events
        ↓
Risk Events
        ↓
Performance Events

Each layer consumes the event output of the immediately preceding layer as its primary transition input.

A runtime layer may additionally consume Canonical Working State or immutable lifecycle history when explicitly required by its ADR-defined responsibility.

No runtime component shall bypass the event hierarchy for state transitions.

---

### Scientific Justification

Scientific reasoning requires explicit causality.

Every runtime state shall be reproducible from an ordered sequence of Runtime Events.

Explicit Runtime Events:

- preserve semantic continuity,
- eliminate hidden state transitions,
- enable deterministic replay,
- improve auditability,
- provide the foundation for future Scientific Reasoning layers.

---

### Architectural Consequences

RunLoop becomes a deterministic orchestration layer.

TradeLifecycleEngine consumes explicit lifecycle events.

PnLEngine consumes lifecycle events instead of reconstructing trade completion.

RiskEngine evaluates Canonical Working State at its assigned execution stage.

PerformanceEngine evaluates completed lifecycle outcomes.

Future runtime modules integrate through Runtime Events rather than direct coupling.

---

### Acceptance Criteria

- Every runtime transition produces an explicit Runtime Event.
- No downstream component reconstructs information already available upstream.
- Runtime replay reproduces identical Runtime Event sequences.
- Runtime Event ordering remains deterministic.
- Every CanonicalState mutation is traceable to one or more Runtime Events.

---

# ADR-003

## TradeLifecycle as the Authoritative Trade Model

### Motivation

Repository analysis confirmed that TradeLifecycle infrastructure already exists.

However, the active runtime execution path still bypasses parts of that infrastructure.

As a result, lifecycle history, financial accounting and performance evaluation are only partially connected.

---

### Decision

TradeLifecycleEngine SHALL become the Authoritative Owner of trade lifecycle information.

TradeLifecycleEngine exclusively owns:

- Trade Identifier
- Lifecycle Status
- Entry Facts
- Exit Facts
- Lifecycle Timestamps
- Lifecycle History
- Immutable Lifecycle Record

TradeLifecycleEngine SHALL NOT compute:

- Realized PnL
- Unrealized PnL
- Equity
- Peak Equity
- Drawdown
- Risk Metrics
- Performance Metrics

PnLEngine SHALL become the exclusive Computational Authority for all financial consequences derived from lifecycle facts.

---

### Scientific Justification

Lifecycle facts and financial consequences represent different scientific concepts.

TradeLifecycleEngine answers:

> "What happened?"

PnLEngine answers:

> "What are the financial consequences?"

Separating historical facts from financial interpretation preserves scientific clarity and eliminates responsibility overlap.

---

### Architectural Consequences

Trade history exists exactly once.

Lifecycle transitions become immutable.

PnLEngine derives financial state exclusively from lifecycle facts.

PerformanceEngine evaluates completed lifecycle outcomes.

CanonicalState references active lifecycle entities where operational context is required but never duplicates lifecycle history.

Future lifecycle extensions remain independent from accounting implementation.

---

### Acceptance Criteria

- Trade identifiers remain globally unique.
- Lifecycle history exists exactly once.
- Completed lifecycle records are immutable.
- PnLEngine never owns lifecycle history.
- TradeLifecycleEngine never performs financial accounting.
- Historical lifecycle information is never duplicated into CanonicalState.
- Every completed trade is reproducible from the immutable lifecycle record.

# ADR-004

## Position Represents Current Market Exposure

### Motivation

Repository analysis and the independent architecture review identified an ambiguity between the concepts of Position and Exposure.

Previous architectural revisions treated Position and Exposure as partially independent runtime entities.

This ambiguity introduced inconsistent ownership responsibilities between PositionEngine, RiskEngine and CanonicalState.

The architecture therefore requires precise scientific definitions.

---

### Scientific Definitions

**Position**

Position represents the current operational market state.

A Position consists of:

- Side
- Quantity
- Average Entry Price
- Current Exposure

Position describes only the current operational runtime situation.

Position never represents historical execution.

---

**Exposure**

Exposure is not an independent runtime entity.

Exposure is a quantitative property of Position.

Exposure therefore possesses no independent architectural ownership.

Every runtime component requiring Exposure shall derive it directly from Position.

---

### Decision

PositionEngine SHALL become the exclusive Computational Authority for Position evolution.

CanonicalState SHALL become the Authoritative Owner of the canonical Position.

Exposure SHALL always be derived from Position.

RiskEngine SHALL consume Position-derived Exposure.

RiskEngine SHALL never maintain an independent canonical Exposure representation.

TradeLifecycleEngine SHALL remain completely independent from operational Position management.

---

### Scientific Justification

Operational Position and historical execution represent different scientific abstractions.

Historical execution answers:

> "What happened?"

Operational Position answers:

> "What is currently active?"

Separating both concepts eliminates duplicate ownership while preserving complete traceability.

Representing Exposure as a Position property removes an unnecessary architectural entity.

---

### Architectural Consequences

Position becomes the single operational runtime representation.

Exposure no longer exists as an independently owned runtime object.

RiskEngine consumes Position-derived Exposure.

PnLEngine consumes Position for mark-to-market valuation.

TradeLifecycleEngine remains independent from operational Position updates.

CanonicalState stores the canonical Position.

---

### Acceptance Criteria

- Exactly one canonical Position exists.
- Exposure never exists independently from Position.
- RiskEngine never owns Position.
- RiskEngine never owns Exposure.
- TradeLifecycleEngine never owns operational Position.
- CanonicalState contains the authoritative operational Position.

---

# ADR-005

## Profit and Loss Accounting

### Motivation

Repository analysis confirmed that lifecycle management and financial accounting currently overlap conceptually.

TradeLifecycle determines historical facts.

PnLEngine determines financial consequences.

These responsibilities shall remain completely separated.

---

### Decision

PnLEngine SHALL become the exclusive Computational Authority for financial accounting.

PnLEngine computes:

- Realized PnL
- Unrealized PnL
- Realized PnL (cumulative)
- Equity
- Peak Equity

TradeLifecycleEngine SHALL provide immutable lifecycle facts only.

TradeLifecycleEngine SHALL never calculate financial values.

CanonicalState SHALL store the resulting canonical financial runtime state.

---

### Scientific Justification

Lifecycle information represents immutable historical facts.

Financial accounting represents quantitative interpretation of those facts.

Separating factual history from financial computation preserves modularity, determinism and auditability.

Financial algorithms may evolve independently from lifecycle semantics.

---

### Architectural Consequences

TradeLifecycleEngine becomes independent from accounting algorithms.

PnLEngine becomes independent from lifecycle persistence.

CanonicalState stores canonical financial runtime state.

RiskEngine consumes canonical financial state.

PerformanceEngine evaluates realized financial outcomes.

---

### Acceptance Criteria

- Realized PnL originates exclusively from PnLEngine.
- Unrealized PnL originates exclusively from PnLEngine.
- TradeLifecycleEngine performs no financial computation.
- CanonicalState contains exactly one canonical financial state.
- Financial values remain reproducible from identical lifecycle history.

---

# ADR-006

## Canonical Financial State Ownership

### Motivation

Independent architecture review identified that ownership alone is insufficient unless the financial model itself is formally defined.

Equity, Peak Equity and Drawdown therefore require explicit scientific definitions.

---

### Scientific Definitions

**Equity**

```
Equity =
Initial Capital
+ Realized PnL (cumulative)
+ Current Unrealized PnL
```

---

**Peak Equity**

Highest Equity observed since runtime initialization.

---

**Drawdown**

```
Drawdown =
Peak Equity
−
Current Equity
```

Drawdown is a derived financial metric.

---

### Decision

PnLEngine SHALL become the exclusive Computational Authority for:

- Realized PnL
- Unrealized PnL
- Equity
- Peak Equity

CanonicalState SHALL become the Authoritative Owner of all financial runtime state.

RiskEngine SHALL calculate Drawdown exclusively from canonical financial state.

RiskEngine SHALL never own financial runtime information.

CanonicalState SHALL store the canonical Drawdown value.

Equity SHALL be recomputed whenever:

- Realized PnL changes, or
- Unrealized PnL changes.

---

### Scientific Justification

Financial state is cumulative.

Cumulative quantities require unique ownership.

Separating computation from ownership preserves determinism while eliminating duplicate authority.

---

### Architectural Consequences

Financial correctness becomes independent of execution ordering.

Risk evaluation always operates on canonical financial state.

Future accounting improvements remain isolated inside PnLEngine.

CanonicalState becomes the single authoritative financial runtime model.

---

### Acceptance Criteria

- Exactly one authoritative Equity exists.
- Exactly one authoritative Peak Equity exists.
- Exactly one authoritative Drawdown exists.
- RiskEngine owns no financial runtime state.
- Financial state remains deterministic for identical lifecycle histories.

# ADR-007

## Risk Evaluation as a Pure Computational Layer

### Motivation

Repository analysis and the independent architecture review identified recurring ownership ambiguity regarding RiskEngine.

Risk evaluation requires access to runtime information.

Risk evaluation does not justify ownership of runtime information.

The architecture therefore separates runtime ownership from runtime evaluation.

---

### Scientific Definitions

**Risk Evaluation**

Risk Evaluation is the deterministic assessment of the current runtime state.

Risk Evaluation does not create runtime truth.

Risk Evaluation derives quantitative metrics from already established runtime information.

---

**Risk Metric**

A Risk Metric is a derived quantity calculated from canonical runtime state.

Examples include:

- Drawdown
- Exposure Utilization
- Position Risk
- Portfolio Risk
- Margin Utilization
- Risk Level

Risk Metrics are derived values.

They are not primary runtime entities.

---

### Decision

RiskEngine SHALL operate exclusively as a Computational Layer.

RiskEngine SHALL consume only Canonical Working State at its assigned execution stage.

RiskEngine SHALL never own:

- Position
- Exposure
- Trade
- Trade History
- Equity
- Peak Equity
- Canonical Runtime State

RiskEngine computes derived Risk Metrics.

CanonicalState stores the resulting canonical Risk Metrics.

---

### Scientific Justification

Scientific evaluation must remain independent from scientific ownership.

Allowing RiskEngine to own runtime state would introduce circular dependencies between runtime evaluation and runtime generation.

Restricting RiskEngine to deterministic computation preserves modularity, reproducibility and architectural clarity.

---

### Architectural Consequences

RiskEngine becomes stateless between runtime ticks except for transient computational variables.

Future risk models may evolve independently without changing runtime ownership.

CanonicalState remains the unique authoritative runtime representation.

---

### Acceptance Criteria

- RiskEngine consumes only Canonical Working State at its assigned execution stage.
- RiskEngine owns no canonical runtime information.
- Risk Metrics remain deterministic for identical Canonical Working State at the assigned RiskEngine execution stage.
- Exactly one ownership path exists for every runtime information object.

---

# ADR-008

## Performance Ownership

### Motivation

Repository analysis identified that the current implementation evaluates runtime decisions rather than realized trading outcomes.

Runtime decisions represent intentions.

Trading performance represents realized outcomes.

These concepts shall remain separated.

---

### Decision

PerformanceEngine SHALL evaluate completed lifecycle outcomes.

Performance SHALL be derived exclusively from:

- completed lifecycle events,
- realized financial outcomes.

The fundamental accounting unit becomes:

- Completed Lifecycle Outcome

rather than:

- Runtime Decision.

Partial Close events SHALL contribute realized performance when realized PnL is generated.

Full Close SHALL terminate the lifecycle exactly once.

---

### Scientific Justification

Scientific evaluation measures observable outcomes.

Intentions cannot be evaluated as realized performance.

Using completed lifecycle outcomes establishes reproducible and statistically meaningful performance measurements.

---

### Architectural Consequences

PerformanceEngine consumes:

- TradeLifecycleEngine,
- Realized PnL,
- Canonical Financial State.

PerformanceEngine does not evaluate strategy intentions.

Future statistical modules inherit consistent semantics.

---

### Acceptance Criteria

- Trade Count equals completed lifecycle outcomes.
- Win Rate derives exclusively from realized outcomes.
- Performance statistics remain reproducible from lifecycle history.
- Runtime decisions never directly contribute to performance statistics.

---

# ADR-009

## Partial Trade Closure and Position Netting

### Motivation

The architecture must explicitly distinguish between:

- Scale-In,
- Partial Close,
- Full Close.

Without explicit semantics, PositionEngine, TradeLifecycleEngine, PnLEngine and PerformanceEngine could interpret identical execution sequences differently.

Scientific runtime architectures require one deterministic lifecycle model.

---

### Scientific Definitions

**Scale-In**

Increase of exposure within an already active Position.

---

**Partial Close**

Reduction of exposure while the lifecycle remains active.

Partial Close realizes a portion of accumulated profit or loss.

The lifecycle remains active.

---

**Full Close**

Remaining Position reaches zero.

The lifecycle terminates exactly once.

---

### Decision

TradeLifecycleEngine SHALL explicitly distinguish:

- Scale-In,
- Partial Close,
- Full Close.

PositionEngine SHALL maintain only the resulting operational Position.

PositionEngine SHALL never reconstruct historical trade composition.

PnLEngine SHALL calculate realized financial consequences for every Partial Close.

PerformanceEngine SHALL account for realized Partial Close outcomes.

---

### Lifecycle Transition Table

| Current State | Event | Next State |
|--------------|-------|------------|
| No Position | Trade Opened | Open |
| Open | Scale-In | Open |
| Open | Partial Close | Open |
| Open | Full Close | Closed |
| Closed | Trade Opened | Open |

All other transitions are invalid and SHALL generate a Runtime Failure Event.

---

### Scientific Justification

Operational Position and historical execution represent different scientific abstractions.

Explicit lifecycle semantics eliminate interpretation ambiguity.

Deterministic lifecycle semantics guarantee deterministic accounting and deterministic performance evaluation.

---

### Architectural Consequences

Lifecycle history becomes deterministic.

Financial accounting becomes deterministic.

Performance accounting becomes deterministic.

Position management remains operationally simple.

---

### Acceptance Criteria

- Partial Close generates realized PnL without terminating the lifecycle.
- Full Close terminates the lifecycle exactly once.
- PositionEngine stores only operational Position.
- TradeLifecycleEngine stores complete historical execution.
- PnLEngine derives financial consequences exclusively from lifecycle facts.
- PerformanceEngine evaluates realized lifecycle outcomes.

# ADR-010

## Deterministic Runtime Execution Ordering

### Motivation

Repository analysis identified that several runtime components implicitly depend upon execution order.

Execution ordering currently represents implementation behaviour rather than an explicit architectural contract.

Scientific runtime architectures require deterministic information flow.

Every runtime component shall consume a fully consistent runtime state.

No runtime component shall observe partially updated information.

---

### Decision

The runtime SHALL execute the following deterministic processing sequence during every runtime tick.

1. Runtime Tick Acquisition
2. State Acquisition and Normalization
3. Regime Classification
4. Strategy Selection
5. Execution Decision Generation
6. Executor Event Generation
7. TradeLifecycle Update
8. Position Update
9. Financial Accounting
10. Risk Evaluation
11. Performance Evaluation
12. Tick-Complete CanonicalState Publication

Only after completion of Step 12 may external downstream consumers observe the resulting Tick-Complete CanonicalState Snapshot.

Intermediate runtime state shall remain internal to the execution pipeline.

---

### Scientific Justification

Deterministic execution ordering guarantees that identical runtime inputs produce identical runtime outputs.

It eliminates hidden execution-order dependencies.

It prevents downstream components from observing partially updated runtime information.

This establishes a stable scientific foundation for deterministic replay, validation and explainability.

---

### Architectural Consequences

RunLoop becomes the deterministic orchestration layer.

Every runtime component receives one well-defined execution position.

RiskEngine and PerformanceEngine consume Canonical Working State at their assigned execution stages.

Future runtime components integrate into the defined execution sequence rather than creating independent execution paths.

---

### Acceptance Criteria

- Exactly one execution sequence exists.
- No runtime component consumes partially updated runtime state.
- Execution ordering remains deterministic.
- Tick-Complete CanonicalState publication occurs exactly once per runtime tick.

---

# ADR-011

## Runtime Failure Handling

### Motivation

Scientific runtime architectures require deterministic handling of rejected or failed runtime transitions.

Without explicit failure semantics, Position, Lifecycle, Financial State and Performance may diverge.

Failure handling therefore forms part of the architectural contract.

---

### Decision

Rejected lifecycle transitions SHALL never modify canonical runtime state.

Rejected transitions SHALL never:

- modify Position,
- modify Equity,
- modify Realized PnL,
- modify Unrealized PnL,
- modify Performance,
- terminate a lifecycle.

Instead, every rejected transition SHALL generate exactly one immutable Runtime Failure Event.

Runtime Failure Events become part of the immutable lifecycle history.

Operational runtime evolution continues independently.

---

### Scientific Justification

Failed execution attempts are historical observations.

Historical observations shall be preserved.

Operational runtime state shall reflect only successfully completed runtime transitions.

Separating failure history from operational runtime state preserves deterministic semantics.

---

### Architectural Consequences

TradeLifecycleEngine records Runtime Failure Events.

PnLEngine ignores rejected lifecycle transitions.

PositionEngine ignores rejected lifecycle transitions.

RiskEngine evaluates only successfully established runtime state.

Future diagnostic systems may analyse Runtime Failure Events without affecting operational execution.

---

### Acceptance Criteria

- Rejected transitions never modify canonical runtime state.
- Every rejected transition generates exactly one Runtime Failure Event.
- Operational runtime behaviour remains deterministic after failures.
- Runtime Failure Events remain permanently reproducible.

---

# ADR-012

## Persistence, Recovery and Schema Evolution

### Motivation

Persistence, runtime recovery and schema evolution are important architectural capabilities.

However, they are not prerequisites for establishing scientifically correct runtime ownership.

Introducing them before ownership consolidation would unnecessarily increase architectural complexity.

---

### Decision

Persistence, Recovery and Schema Evolution are explicitly classified as Deferred Scope.

During the current consolidation:

- no ad hoc persistence mechanisms shall be introduced,
- no runtime recovery mechanism shall be implemented,
- no schema migration mechanism shall be introduced,

unless approved through an Architecture Evolution Review.

---

### Scientific Justification

Stable ownership is a prerequisite for durable persistence.

Recovery mechanisms built upon unstable ownership models increase long-term technical debt.

Scientific architectural consolidation shall therefore precede infrastructure evolution.

---

### Architectural Consequences

Current consolidation remains focused on deterministic runtime architecture.

Future persistence work begins from an already validated ownership model.

Architecture Evolution Review becomes mandatory before introducing unattended production recovery mechanisms.

Persistence, Recovery and Schema Evolution remain independent architectural work packages.

---

### Acceptance Criteria

- No ad hoc persistence exists.
- Recovery mechanisms require Architecture Evolution Review approval.
- Schema evolution remains explicitly version-controlled.
- Deferred Scope remains documented until formally released.

---

# Internal Review

Architecture Review

PASS

Scientific Consistency Review

PASS

Architecture Integrity Review

PASS

Ownership Review

PASS

Editorial Review

PASS

Status

ADR-001 through ADR-012 completed.

Architecture Decisions completed.

# Runtime Ownership Matrix

---

# Purpose of this Section

The Runtime Ownership Matrix defines the normative ownership model of the Run Engine.

Every runtime information object shall appear exactly once within this matrix.

This matrix is the authoritative reference for ownership responsibilities throughout the complete runtime architecture.

Whenever implementation behaviour conflicts with this matrix, the matrix takes precedence.

The matrix distinguishes four architectural responsibilities.

- Authoritative Owner
- Computational Authority
- Writer-on-Behalf-Of
- Primary Consumers

No runtime information object shall possess more than one Authoritative Owner.


Market Observations originate outside the Run Engine.

They are external runtime inputs rather than internally owned runtime information.

Therefore they are intentionally excluded from the Runtime Ownership Matrix.

---

| Runtime Information                   | Authoritative Owner  | Computational Authority | Writer-on-Behalf-Of  | Primary Consumers                            |
| ------------------------------------- | -------------------- | ----------------------- | -------------------- | -------------------------------------------- |
| Runtime Tick                          | RunLoop              | RunLoop                 | RunLoop              | StateEngine                                  |
| Normalized Runtime State              | CanonicalState       | StateEngine             | StateEngine          | RegimeClassifier                             |
| Market Regime                         | CanonicalState       | RegimeClassifier        | RegimeClassifier     | StrategySelector                             |
| Strategy Selection                    | CanonicalState       | StrategySelector        | StrategySelector     | Executor                                     |
| Execution Decision                    | CanonicalState       | StrategySelector        | StrategySelector     | Executor                                     |
| Execution Event                       | TradeLifecycleEngine | Executor                | Executor             | TradeLifecycleEngine                         |
| Trade Identifier                      | TradeLifecycleEngine | TradeLifecycleEngine    | TradeLifecycleEngine | PnLEngine, PerformanceEngine                 |
| Lifecycle State                       | TradeLifecycleEngine | TradeLifecycleEngine    | TradeLifecycleEngine | PositionEngine, PnLEngine, PerformanceEngine |
| Entry Facts                           | TradeLifecycleEngine | TradeLifecycleEngine    | TradeLifecycleEngine | PositionEngine, PnLEngine                    |
| Exit Facts                            | TradeLifecycleEngine | TradeLifecycleEngine    | TradeLifecycleEngine | PnLEngine, PerformanceEngine                 |
| Lifecycle History                     | TradeLifecycleEngine | TradeLifecycleEngine    | TradeLifecycleEngine | PerformanceEngine                            |
| Runtime Failure Event                 | TradeLifecycleEngine | TradeLifecycleEngine    | TradeLifecycleEngine | Diagnostics                                  |
| Position                              | CanonicalState       | PositionEngine          | PositionEngine       | PnLEngine, RiskEngine                        |
| Realized PnL                          | CanonicalState       | PnLEngine               | PnLEngine            | RiskEngine, PerformanceEngine                |
| Unrealized PnL                        | CanonicalState       | PnLEngine               | PnLEngine            | RiskEngine                                   |
| Equity                                | CanonicalState       | PnLEngine               | PnLEngine            | RiskEngine                                   |
| Peak Equity                           | CanonicalState       | PnLEngine               | PnLEngine            | RiskEngine                                   |
| Drawdown                              | CanonicalState       | RiskEngine              | RiskEngine           | PerformanceEngine                            |
| Risk Metrics | CanonicalState | RiskEngine | RiskEngine | PerformanceEngine || Runtime Status                        | CanonicalState       | RunLoop                 | RunLoop              | All runtime components                       |
| Performance Metrics                   | CanonicalState       | PerformanceEngine       | PerformanceEngine    | Reporting                                    |
| Tick-Complete CanonicalState Snapshot | CanonicalState       | RunLoop                 | RunLoop              | All downstream runtime components            |


The Runtime Ownership Matrix defines ownership categories rather than individual event instances.

Individual Runtime Events defined in ADR-002 inherit the ownership of their corresponding category.

For example:

- Order Submitted, Order Accepted, Order Rejected and Order Executed inherit Execution Event ownership.
- Trade Opened, Trade Updated, Partial Close and Full Close inherit Lifecycle State ownership.
- Realized PnL Updated inherits Realized PnL ownership.
- Risk Evaluated inherits Risk Metrics ownership.
- Performance Updated inherits Performance Metrics ownership.

Execution Events are generated by Executor.

TradeLifecycleEngine becomes the Authoritative Owner only after accepted Execution Events have been incorporated into immutable lifecycle history.

Executor owns execution event generation.

TradeLifecycleEngine owns historical lifecycle recording.

---

# Ownership Rules

The following rules are mandatory.

---

## Rule OM-001

Every runtime information object possesses exactly one Authoritative Owner.

---

## Rule OM-002

Computational Authority may differ from Authoritative Owner.

---

## Rule OM-003

Writer-on-Behalf-Of never establishes ownership.

---

## Rule OM-004

Primary Consumers shall never modify consumed information.

---

## Rule OM-005

TradeLifecycleEngine exclusively owns immutable historical execution.

---

## Rule OM-006

CanonicalState exclusively owns active runtime state.

---

## Rule OM-007

RiskEngine owns no runtime information.

RiskEngine computes derived quantities only.

---

## Rule OM-008

PerformanceEngine owns no operational runtime information.

PerformanceEngine evaluates completed lifecycle outcomes only.

---

## Rule OM-009

No runtime component may introduce additional Authoritative Owners without an approved Architecture Evolution Review.

---

# Internal Review

Ownership Review

PASS

Scientific Consistency Review

PASS

Architecture Integrity Review

PASS

Editorial Review

PASS

Status

Runtime Ownership Matrix completed.

# Target Information Flow

---

# Purpose of this Section

The Target Information Flow defines the normative propagation of information through the Run Engine.

It specifies **how** information moves through the architecture.

The Runtime Ownership Matrix specifies **who owns** information.

Together, both sections define the complete scientific information model of the Run Engine.

Every runtime information object shall move exactly once through the execution pipeline.

Information shall never be recreated after it has already been produced.

---

# Scientific Information Flow Principles

## Runtime Tick and Market Observation

Runtime Tick is the deterministic execution trigger generated by RunLoop.

Market Observation is the external input processed during the current Runtime Tick.

Each Runtime Tick processes exactly one Market Observation.

Market Observation is external runtime input.

Runtime Tick is the internal execution trigger.

## Principle IF-001

Information is produced exactly once.

---

## Principle IF-002

Information is never reconstructed downstream.

---

## Principle IF-003

Every transformation preserves semantic meaning.

---

## Principle IF-004

Every runtime stage consumes only completed upstream information.

---

## Principle IF-005

Every runtime stage produces information for downstream consumers.

---

## Principle IF-006

Information flow is strictly acyclic.

Feedback mechanisms may influence future runtime ticks but shall never modify already completed runtime processing.

---

Market Observation
        │
        ▼
Runtime Tick
        │
        ▼
StateEngine
        │
        ▼
RegimeClassifier
        │
        ▼
StrategySelector
        │
        ▼
Executor
        │
        ▼
TradeLifecycleEngine
        │
        ▼
PositionEngine
        │
        ▼
PnLEngine
        │
        ├──────────────┐
        ▼              │
Canonical Working State│
        │              │
        ▼              │
RiskEngine ◄───────────┘
        │
        ▼
PerformanceEngine
        │
        ▼
CanonicalState Publication
        │
        ▼
Tick-Complete CanonicalState Snapshot

---

# Runtime Stage Responsibilities

| Runtime Stage | Primary Input | Primary Output |
|---------------|---------------|----------------|
| RunLoop | Runtime Tick | Execution Sequence |
| StateEngine | Market Observation | Normalized Runtime State |
| RegimeClassifier | Canonical Runtime State | Market Regime |
| StrategySelector | Canonical Runtime State | Strategy Selection |
| Executor | Strategy Selection | Execution Events |
| TradeLifecycleEngine | Execution Events | Lifecycle Events |
| PositionEngine | Lifecycle Events | Current Position |
| PnLEngine | Lifecycle Events + Position | Financial Runtime State |
| RiskEngine | Canonical Financial State + Position | Risk Metrics |
| PerformanceEngine | Lifecycle History + Financial State | Performance Metrics |
| CanonicalState | Runtime Outputs | Tick-Complete Snapshot |

---

# Information Preservation Rules

## Rule IF-001

Information already produced upstream shall never be reconstructed downstream.

---

## Rule IF-002

TradeLifecycleEngine becomes the permanent historical source of execution semantics.

---

## Rule IF-003

PnLEngine derives financial consequences exclusively from lifecycle information.

---

## Rule IF-004

RiskEngine derives risk exclusively from canonical runtime state.

---

## Rule IF-005

PerformanceEngine derives performance exclusively from completed lifecycle outcomes.

---

## Rule IF-006

CanonicalState stores the final operational runtime truth after completion of every runtime tick.

---

# Tick Completion Contract

A runtime tick is complete only when all mandatory runtime stages have executed successfully.

Completion requires:

- Lifecycle updated
- Position updated
- Financial state updated
- Risk evaluated
- Performance evaluated
- CanonicalState published

Only after successful completion shall the Tick-Complete Snapshot become externally observable.

No downstream runtime component may consume intermediate runtime state.

---

# Scientific Information Flow Guarantees

The target architecture guarantees:

- deterministic execution,
- explicit ownership,
- semantic continuity,
- complete traceability,
- reproducible replay,
- elimination of downstream reconstruction,
- acyclic runtime information flow,
- one authoritative operational runtime state.

---

# Internal Review

Information Flow Review

PASS

Scientific Consistency Review

PASS

Architecture Integrity Review

PASS

Editorial Review

PASS

Status

Target Information Flow completed.

# Architecture Invariants

---

# Purpose of this Section

Architecture Invariants define the fundamental properties of the Run Engine architecture.

Unlike implementation details, Architecture Invariants shall remain true throughout every future architectural evolution.

No implementation, optimization or architectural extension may violate these invariants unless they are explicitly superseded through an approved Architecture Evolution Review.

---

# Invariant AI-001

## Single Source of Truth

CanonicalState SHALL remain the unique authoritative representation of the active runtime state.

No competing authoritative operational runtime state may exist.

---

# Invariant AI-002

## Unique Ownership

Every runtime information object SHALL possess exactly one Authoritative Owner.

Ownership ambiguity is prohibited.

Duplicate ownership is prohibited.

---

# Invariant AI-003

## Separation of Ownership and Computation

Authoritative Ownership and Computational Authority are independent architectural concepts.

A runtime component may compute information without owning it.

A runtime component may own information without computing it.

---

# Invariant AI-004

## Immutable Lifecycle History

TradeLifecycleEngine SHALL remain the unique authoritative owner of historical trade evolution.

Completed lifecycle records are immutable.

Historical execution shall never be reconstructed from operational runtime state.

---

# Invariant AI-005

## Deterministic Execution

Identical runtime inputs SHALL produce identical runtime outputs.

Deterministic behaviour shall not depend upon hidden mutable state.

---

# Invariant AI-006

## Deterministic Information Flow

Runtime information SHALL propagate through one deterministic execution sequence.

Runtime information shall never move backwards through the execution pipeline.

---

# Invariant AI-007

## Semantic Continuity

Information produced by an upstream runtime component SHALL remain semantically unchanged throughout downstream processing.

Downstream runtime components shall derive new information rather than reinterpret existing information.

---

# Invariant AI-008

## Explicit Runtime Events

Every runtime state transition SHALL originate from one explicit Runtime Event.

Implicit runtime mutations are prohibited.

---

# Invariant AI-009

## Tick Completeness

Every runtime tick SHALL terminate with one Tick-Complete CanonicalState Snapshot.

External downstream consumers shall consume only Tick-Complete Snapshots.

---

# Invariant AI-010

## Financial Consistency

Financial runtime state SHALL remain internally consistent.

At all times:

```
Equity =
Initial Capital
+ Realized PnL (cumulative)
+ Unrealized PnL
```

Peak Equity shall never decrease.

Drawdown shall always be derived from:

```
Peak Equity − Current Equity
```

---

# Invariant AI-011

## Lifecycle Consistency

Every trade SHALL follow one deterministic lifecycle.

Valid lifecycle transitions are explicitly defined.

Completed lifecycle records remain immutable.

Rejected runtime transitions become Runtime Failure Events.

---

# Invariant AI-012

## Operational and Historical Separation

Operational runtime state and historical runtime state SHALL remain separate architectural concepts.

CanonicalState owns operational truth.

TradeLifecycleEngine owns historical truth.

Neither architectural model replaces the other.

---

# Invariant AI-013

## Architectural Minimality

Every runtime component SHALL justify its existence through one unique scientific responsibility.

Architectural redundancy is prohibited unless scientifically justified.

---

# Invariant AI-014

## Architectural Traceability

Every runtime output SHALL be traceable through:

- originating observation,
- runtime state,
- execution decision,
- lifecycle event,
- financial accounting,
- risk evaluation,
- resulting runtime state.

No runtime result shall exist without a complete derivation path.

---

# Invariant AI-015

## Scientific Evolution

Future architectural evolution SHALL preserve all Architecture Invariants unless an Architecture Evolution Review explicitly approves their modification.

Architectural convenience alone shall never justify changing an invariant.

---

# Internal Review

Architecture Review

PASS

Scientific Consistency Review

PASS

Architecture Integrity Review

PASS

Editorial Review

PASS

Status

Architecture Invariants completed.

# Scientific Acceptance Criteria

---

# Purpose of this Section

The Scientific Acceptance Criteria define the minimum conditions that shall be satisfied before the Run Engine architecture can be considered scientifically consolidated.

Unlike implementation milestones, these criteria validate the architecture itself.

Every criterion shall be objectively verifiable.

Partial fulfillment is insufficient.

---

# AC-001

## Canonical Runtime Ownership

CanonicalState operates as the Single Source of Truth for the complete active runtime state.

No competing authoritative operational runtime state exists.

---

# AC-002

## Unique Information Ownership

Every runtime information object possesses exactly one Authoritative Owner.

The ownership model is fully documented by the Runtime Ownership Matrix.

No ownership ambiguity exists.

---

# AC-003

## Separation of Ownership and Computation

Every runtime information object possesses exactly one Computational Authority.

Computational Authority and Authoritative Ownership remain explicitly separated.

No component implicitly acquires ownership through computation.

---

# AC-004

## Lifecycle Integrity

TradeLifecycleEngine exclusively owns lifecycle history.

Trade history exists exactly once.

Completed lifecycle records are immutable.

Every lifecycle transition is reproducible.

---

# AC-005

## Financial Integrity

PnLEngine exclusively performs financial accounting.

Financial state remains reproducible from immutable lifecycle history.

Financial equations remain internally consistent.

---

# AC-006

## Canonical Runtime State

CanonicalState contains exactly one authoritative representation of:

- Position
- Realized PnL
- Unrealized PnL
- Equity
- Peak Equity
- Drawdown
- Risk Metrics
- Runtime Status

No duplicate operational runtime state exists elsewhere.

---

# AC-007

## Risk Evaluation

RiskEngine consumes only Canonical Working State at its assigned execution stage.

RiskEngine owns no canonical runtime information.

Risk evaluation remains deterministic.

---

# AC-008

## Performance Evaluation

PerformanceEngine evaluates completed lifecycle outcomes exclusively.

Runtime decisions never directly contribute to performance statistics.

Performance remains reproducible from lifecycle history.

---

# AC-009

## Tick Completion

Every runtime tick produces exactly one externally observable Tick-Complete CanonicalState Snapshot.

No downstream runtime component observes partially updated runtime state.

---

# AC-010

## Information Flow

No downstream runtime component reconstructs semantic information already produced upstream.

Semantic continuity is preserved throughout the complete runtime pipeline.

---

# AC-011

## Scientific Traceability

Every runtime output is completely traceable through:

- originating observation,
- normalized runtime state,
- strategy selection,
- execution decision,
- lifecycle transition,
- financial accounting,
- risk evaluation,
- performance evaluation,
- Tick-Complete CanonicalState.

---

# AC-012

## Deterministic Behaviour

Identical runtime inputs always produce identical runtime outputs.

No runtime behaviour depends upon undocumented execution ordering or hidden mutable state.

---

# AC-013

## Architecture Consistency

No contradiction exists between:

- Scientific Design Principles
- Scientific Architecture Diagnosis
- Architecture Decision Records
- Runtime Ownership Matrix
- Target Information Flow
- Architecture Invariants
- Scientific Acceptance Criteria

The complete architecture forms one internally consistent model.

---

# AC-014

## Lifecycle Semantics

Scale-In, Partial Close and Full Close shall remain semantically distinct lifecycle transitions.

Partial Close shall generate realized PnL without terminating the lifecycle.

Full Close shall terminate the lifecycle exactly once.

Every lifecycle transition shall remain reproducible.

---

# AC-015

## Runtime Failure Handling

Rejected runtime transitions shall never modify canonical runtime state.

Every rejected runtime transition shall generate exactly one Runtime Failure Event.

Runtime Failure Events shall remain reproducible and permanently preserved within immutable lifecycle history.

---

# Architecture Readiness Criteria

The architecture is implementation-ready only when all conditions below are verified.

- AC-001 through AC-015 PASS.
- ADR-001 through ADR-012 are internally consistent.
- Runtime Ownership Matrix has no duplicate Authoritative Owner.
- Target Information Flow matches ADR-010.
- Architecture Invariants match ADR-001 through ADR-012.
- Scientific Consistency Review: PASS.
- Architecture Integrity Review: PASS.
- Editorial Pass: PASS.

---

# Internal Review

Scientific Acceptance Review

PASS

Scientific Consistency Review

PASS

Architecture Integrity Review

PASS

Editorial Review

PASS

Status

Scientific Acceptance Criteria completed.

# Scientific Implementation Governance


This section governs the implementation of the approved architecture.

Architecture Decisions define the target architecture.

Implementation Governance defines the mandatory engineering process used to achieve that architecture.

No implementation activity may violate the approved Architecture Decision Records.

---

# Purpose of this Section

The purpose of this section is to govern the implementation of the approved Run Engine architecture.

The preceding sections define **what** the architecture shall become.

This section defines **how** architectural evolution shall be performed.

Implementation quality is treated as an architectural property rather than a programming activity.

Every implementation step shall preserve architectural correctness.

---


## Phase 1 — Lifecycle Integration

### Objective

Integrate TradeLifecycleEngine into the active runtime execution path.

### Primary Components

```text
run_engine/core/trade_lifecycle.py
run_engine/core/loop.py
run_engine/core/canonical_state.py
run_engine/core/canonical_enforcer.py
```

### Scientific Goal

Transform implicit trade evolution into explicit lifecycle events.

### Completion Criteria

- Lifecycle fully integrated.
- Explicit Open events.
- Explicit Partial Close events.
- Explicit Full Close events.
- Lifecycle-derived realized PnL.
- Compilation PASS.
- Import Validation PASS.
- Lifecycle Validation PASS.

---

## Phase 2 — Runtime Ownership Consolidation

### Objective

Complete CanonicalState ownership.

### Primary Components

```text
run_engine/core/canonical_state.py
run_engine/core/canonical_enforcer.py
run_engine/core/loop.py
```

### Scientific Goal

Remove fragmented runtime ownership.

### Completion Criteria

- CanonicalState owns operational runtime state.
- Duplicate ownership eliminated.
- Ownership Review PASS.
- Compilation PASS.

---

## Phase 3 — Position Consolidation

### Objective

Separate operational Position from historical lifecycle information.

### Primary Components

```text
run_engine/core/position.py
run_engine/core/trade_lifecycle.py
```

### Scientific Goal

Separate operational runtime state from historical execution.

### Completion Criteria

- Position contains only operational information.
- Lifecycle contains only historical execution.
- Compilation PASS.

---

## Phase 4 — Financial Consolidation

### Objective

Complete financial ownership.

### Primary Components

```text
run_engine/core/pnl.py
run_engine/core/risk.py
run_engine/core/canonical_state.py
```

### Scientific Goal

Establish deterministic financial accounting.

### Completion Criteria

- Realized PnL validated.
- Unrealized PnL validated.
- Equity validated.
- Peak Equity validated.
- Drawdown validated.

---

## Phase 5 — Performance Consolidation

### Objective

Evaluate completed lifecycle outcomes.

### Primary Components

```text
run_engine/core/performance.py
```

### Scientific Goal

Scientific evaluation of realized trading performance.

### Completion Criteria

- Trade Count validated.
- Win Rate validated.
- Performance Metrics validated.

---

## Phase 6 — Repository Consolidation

### Objective

Review competing runtime implementations.

### Repository Areas

```text
run_engine/runtime/
run_engine/execution/
run_engine/feedback/
run_engine/logging/
```

### Scientific Goal

Reduce architectural ambiguity.

### Possible Outcomes

- Retain
- Integrate
- Archive
- Remove

Deletion is permitted only after architectural validation confirms that the implementation is obsolete.

---

# Engineering Workflow

Every implementation shall follow the mandatory workflow below.

```text
Repository Investigation
        │
        ▼
Architecture Verification
        │
        ▼
Single-File Implementation
        │
        ▼
Compilation
        │
        ▼
Import Validation
        │
        ▼
Targeted Runtime Validation
        │
        ▼
Architecture Review
        │
        ▼
Git Commit
        │
        ▼
Git Push
        │
        ▼
Next Implementation Unit
```

Implementation proceeds one logical implementation unit at a time.

Each implementation unit shall successfully complete:

- Compilation
- Import Validation
- Targeted Runtime Validation
- Ownership Validation
- Architecture Validation

before subsequent implementation work begins.


Repository-wide modifications are prohibited.


---

# Engineering Gates

## EG-001

Compilation PASS

---

## EG-002

Import Validation PASS

---

## EG-003

Runtime Validation PASS

---

## EG-004

Ownership Validation PASS

No duplicate ownership introduced.

---

## EG-005

Architecture Validation PASS

Implementation conforms to all approved ADRs.

---

## EG-006

Repository Validation PASS

Repository remains internally consistent.

---

# Scientific Review Gates

Every implementation phase shall additionally pass:

- Scientific Architecture Review
- Scientific Ownership Review
- Scientific Information Flow Review
- Scientific Traceability Review
- Scientific Consistency Review

Implementation shall not continue while any review remains unresolved.

---

# Independent Review Policy

## Codex

Purpose:

Independent technical repository analysis.

Responsibilities:

- implementation verification,
- repository consistency,
- dependency analysis,
- cleanup verification.

Codex shall not define architecture.

---

## Claude

Purpose:

Independent architecture review.

Responsibilities:

- architecture consistency,
- ownership model,
- hidden coupling,
- scientific completeness,
- architectural risks.

Claude shall not replace repository analysis.

---

## ChatGPT

Purpose:

Architecture governance.

Responsibilities:

- scientific methodology,
- architecture development,
- implementation planning,
- review integration,
- final architectural certification.

---

# Repository Cleanup Policy

Repository cleanup shall begin only after successful architectural consolidation.

Mandatory sequence:

1. Classify competing implementations.
2. Verify dependencies.
3. Archive uncertain implementations.
4. Remove obsolete implementations.
5. Perform repository-wide validation.
6. Approve architectural simplification.

Deletion shall always require architectural evidence.

---

# Final Scientific Certification

The Run Engine architecture shall be considered scientifically consolidated only when all of the following conditions are simultaneously satisfied.

- Scientific Design Principles satisfied.
- Scientific Architecture Diagnosis resolved.
- ADR-001 through ADR-012 implemented.
- Runtime Ownership Matrix validated.
- Target Information Flow validated.
- Architecture Invariants validated.
- Scientific Acceptance Criteria satisfied.
- Engineering Gates PASS.
- Scientific Review Gates PASS.
- Codex Technical Review PASS.
- Claude Architecture Review PASS.
- Repository Cleanup completed.
- Final Architecture Certification approved.


---

# Final Internal Review

Architecture Governance Review

PASS

Scientific Consistency Review

PASS

Architecture Integrity Review

PASS

Implementation Governance Review

PASS

Editorial Review

PASS

Status

RUN_ENGINE_ARCHITECTURE_BASELINE_V1 completed.

END OF DOCUMENT




