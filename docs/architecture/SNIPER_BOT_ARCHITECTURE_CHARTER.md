# SNIPER-BOT ARCHITECTURE CHARTER

Date: 2026-06-21  
Project: Sniper-Bot  
Document Type: Scientific Decision Architecture Charter  
Status: Active Architecture Reference

---

## 1. Core Vision

Leitsatz: The Sniper-Bot is a scientific engineering project whose objective is not to maximize short-term trading performance, but to maximize the long-term quality of evidence-based decision making through elegant, explainable and self-improving architecture.

Engineering Integrity: Jede technische Entscheidung muss mit den Grundprinzipien des Projekts vereinbar sein – auch dann, wenn eine schnellere oder einfachere Abkürzung möglich wäre.


The Sniper-Bot project is not only a trading-bot project.

It is a scientific decision and research platform whose first application domain is algorithmic trading.

The long-term objective is not merely to optimize a single strategy, but to build a system that continuously improves the process that discovers, validates, explains, and prioritizes better strategies.

The system should not only become better.

It should understand why it becomes better.

---

## 2. Architectural North Star

The central goal is:

> Build a modular, scientifically grounded, explainable, uncertainty-aware, self-improving decision system.

The Sniper-Bot must optimize the research process that creates better trading decisions.

Not only:

```text
Market Data -> Strategy -> Trade -> Profit
3. Fundamental Principle

The project does not optimize for more code.

The project optimizes for more reliable knowledge.

Every new component must make the system at least one of the following:

more intelligent
more explainable
more robust
more reproducible
more scientifically useful
more reusable
more decision-relevant

If a component does not improve one of these properties, it does not belong in the core architecture.

4. Quality Hierarchy

The project follows this priority order:

Foundation
  -> Intelligence
  -> Capability
  -> Optimization
4.1 Foundation

Includes:

data integrity
reproducibility
stable IDs
clean architecture
common utilities
documentation
testing
guardrails
traceability

Foundation has the highest priority because every later capability depends on it.

4.2 Intelligence

Includes:

evidence evaluation
uncertainty modeling
knowledge graphs
research questions
information gain
scientific reasoning
explainability

Intelligence determines whether the system can make better future decisions.

4.3 Capability

Includes:

new strategy modules
new model classes
new indicators
new regime modules
new validation workflows

Capabilities are only valuable when the foundation and intelligence layers can evaluate them properly.

4.4 Optimization

Includes:

speed
parallelization
convenience
automation
UI improvements

Optimization is useful, but it must never damage correctness, explainability, or stability.

5. Scientific Development Philosophy

The Sniper-Bot follows the scientific method as a software process.

Observation
  -> Hypothesis
  -> Experiment
  -> Evidence
  -> Knowledge
  -> Reasoning
  -> Improvement
  -> New Observation

This means:

Every important idea should be testable.
Every experiment should produce interpretable evidence.
Every result should update knowledge.
Every decision should be explainable.
Every conclusion should preserve uncertainty.
Every improvement should be reproducible.
6. Knowledge First Engineering

The primary engineering question is:

Does this component increase useful knowledge or reduce relevant uncertainty?

A new component should only be added if it satisfies most of these criteria:

It creates new knowledge.
It reduces uncertainty.
It improves future decisions.
It is explainable.
It is reproducible.
It is modular.
It is reusable outside its first use case.
It has clear inputs and outputs.
It has guardrails.
It can be tested.

If these criteria are not met, the idea should remain outside the core architecture.

7. Explainability Standard

No black-box decision is acceptable as a core architectural principle.

Every score, recommendation, priority, and rejection must be explainable.

A weak output is:

Score = 84.2

A strong output is:

Score = 84.2

Positive contributors:
- high evidence stability
- high expected knowledge gain
- strong relationship network

Negative contributors:
- limited archive diversity
- medium uncertainty
- unresolved dependency risk

Every major intelligence module should preserve:

raw metrics
derived scores
decision class
positive explanations
negative explanations
recommended next action
8. Measurement and Interpretation Must Be Separate

The system must separate:

Raw Metrics
  -> Derived Intelligence
  -> Decision

Raw metrics must be preserved.

Derived scores may change over time.

This allows later reweighting without rerunning expensive analyses.

Example:

evidence_strength
evidence_stability
novelty_score
information_gain_score
scientific_confidence
scientific_uncertainty
global_intelligence_score

The raw components must remain available even if the final score formula changes.

9. Uncertainty Is First-Class Information

Confidence and uncertainty are not the same.

The system must track both.

Example:

scientific_confidence = 82
scientific_uncertainty = 18

or:

scientific_confidence = 47
scientific_uncertainty = 63

High evidence does not automatically mean low uncertainty.

Uncertainty can result from:

low sample size
conflicting evidence
regime dependence
missing archives
unstable results
outdated evidence
weak validation
narrow test coverage

A system that knows its uncertainty can make safer and better decisions.

10. Expected Knowledge Gain

Expected Knowledge Gain is a central long-term research metric.

The key question is not only:

Which strategy is most profitable?

but also:

Which experiment increases system knowledge the most?

Expected Knowledge Gain should consider:

novelty
uncertainty
missing coverage
relationship to other hypotheses
conflict resolution potential
research cost
decision impact

A high-value experiment is not necessarily the one with the highest immediate ROI.

It is the one that most improves future decision quality.

11. Data Philosophy

The project follows strict data preservation principles.

Rules:

Raw data is never discarded without explicit reason.
Analysis outputs must be traceable.
Result files should be descriptively named.
Important outputs should include date stamps.
Metrics should be reproducible.
Interpretation should not overwrite measurement.
Intermediate artifacts may be valuable later.
Expensive runs should be archived.

Data is not only input.

Data is scientific memory.

12. Stable Identity Principle

No important object should rely on position-based IDs.

Weak:

H001
VAL001
EXP001

Strong:

HYP-<stable_hash>
VAL-<stable_hash>
EXP-<stable_hash>

Stable IDs should be based on meaningful payloads.

Examples:

hypothesis content
validation type
source object
research object
campaign definition

This prevents silent corruption when ordering changes.

13. Layer Architecture

The long-term architecture is layered.

L0  Market Data
L1  Evidence
L2  Validation
L3  Learning
L4  Research Management
L5  Research Intelligence
L6  Scientific Reasoning
L7  Strategy Discovery
L8  Portfolio Intelligence
L9  Adaptive Intelligence
L10 Autonomous Scientific Assistant

Each layer must add a distinct scientific capability.

No layer should exist only to produce more files.

14. Current Trade Inspector Layer Mapping

Current mapping:

V1-V8   Trade Analysis
V9      Evidence
V10     Validation
V11     Learning
V12     Research Management
V13     Research Intelligence
V14     Scientific Reasoning
V15     Strategy Discovery

Each version must answer:

What new reasoning ability does the system gain?

15. Research Object Model

The system should eventually analyze not only hypotheses.

It should analyze Research Objects.

Possible object types:

hypothesis
strategy
feature
indicator
parameter
regime
entry_rule
exit_rule
risk_rule
dataset
model
validation_plan
experiment

A hypothesis is only one type of Research Object.

This allows the architecture to remain reusable and expandable.

16. Scientific Memory

The system should maintain several kinds of memory.

16.1 Operational Memory

Includes:

trades
orders
positions
execution records
risk events
16.2 Scientific Memory

Includes:

hypotheses
experiments
validations
evidence
conflicts
uncertainty
conclusions
16.3 Meta Memory

Includes:

which research paths worked
which metrics were misleading
which experiments produced useful knowledge
which assumptions failed
which architecture choices improved stability

The highest level is not only learning about markets.

It is learning about the learning process itself.

17. Research Questions

The system should not only answer questions.

It should learn which questions need to be asked.

Examples:

Which regimes are under-tested?
Which exits fail only under high volatility?
Which indicators create redundant evidence?
Which hypotheses contradict each other?
Which experiments would reduce uncertainty most?
Which strategy family has high promise but weak evidence?
Which assumptions were never validated?

Open Research Questions are a core output of a scientific research system.

18. Knowledge State

The system should track the state of its knowledge.

Important dimensions:

knowledge completeness
knowledge consistency
knowledge diversity
knowledge freshness
knowledge stability
knowledge uncertainty
knowledge confidence
knowledge maturity

This allows the system to answer:

How well do we understand this area?

not only:

Which hypothesis has the highest score?

19. Decision Quality

A decision is high quality if it is:

based on evidence
aware of uncertainty
reproducible
explainable
traceable
robust under new data
useful for future decisions

A profitable result without explanation is not enough.

A lower-profit result that teaches the system something important may be more valuable scientifically.

20. Module Design Rules

Every module must have:

clear purpose
clear input files
clear output files
stable IDs
explicit schemas
guardrails
documentation
smoke test
no hidden side effects
no untracked strategy modifications
no silent data loss
no unnecessary duplication
21. Guardrail Standard

Modules must state what they do not do.

Examples:

does not execute trades
does not modify strategy logic
does not overwrite source data
does not approve live deployment
does not replace human approval
does not execute external commands unless explicitly allowed

Guardrails are part of the architecture, not comments.

22. Testing Philosophy

Testing must follow the project quality standard.

Order:

compile test
  -> help test
  -> smoke test
  -> schema inspection
  -> output inspection
  -> documentation
  -> commit

Large runs should never be the first validation step.

Mini-tests and smoke-tests are mandatory before full runs.

23. Documentation Philosophy

Documentation is not optional.

Every meaningful change should document:

what changed
why it changed
what problem it solves
what files were affected
how it was tested
what remains open
whether future work is required

Documentation should preserve project memory.

A future reader should understand not only what exists, but why it exists.

24. Refactoring Philosophy

Refactoring is allowed only when it has clear technical value.

Valid reasons:

remove duplication
reduce inconsistency
improve stability
improve testability
improve maintainability
prevent known failure modes
improve traceability

Invalid reasons:

cosmetic preference
unnecessary abstraction
premature generalization
change for its own sake

After major refactoring, no new functionality should be added until stability is confirmed.

25. Complexity Rule

Complexity must earn its place.

A complex component is acceptable only if it produces a clear benefit in:

knowledge quality
decision quality
robustness
reproducibility
explainability
long-term maintainability

Otherwise, simpler is better.

26. Anti-Patterns

The following are explicitly discouraged:

black-box scoring
unexplainable recommendations
position-based IDs
duplicated helper logic
undocumented assumptions
untested full runs
hidden side effects
silent schema changes
excessive module proliferation
optimizing speed before correctness
replacing evidence with intuition
mixing raw metrics with interpretations
losing raw data after generating summaries
27. Research Priority Rule

When choosing between possible next tasks, prefer the one that improves:

foundation
intelligence
decision quality
uncertainty reduction
explainability
reusable architecture

over the one that only adds more features.

28. Trading-Specific Principle

The trading bot is the first application domain.

But the architecture should not be limited to trading.

Reusable components should also be useful for:

monitoring
anomaly detection
forecasting
risk analysis
scientific analytics
Forge
other data-driven projects

This increases the long-term value of every high-quality building block.

29. Strategy Development Philosophy

A strategy is not only judged by profit.

It is judged by:

profit
drawdown
robustness
regime dependence
explainability
evidence quality
validation depth
uncertainty
risk contribution
compatibility with portfolio logic

A strategy should not be trusted because it performed well once.

It should earn confidence through evidence.

30. Future Adaptive System

The long-term Sniper-Bot should become a multi-layer adaptive system.

It should include:

regime detection
specialized strategy modules
independent risk budgets
dynamic model selection
dynamic capital allocation
performance-aware portfolio control
scientific feedback loops
continuous validation

Adaptation must be evidence-based, not arbitrary.

31. Human Role

The human remains responsible for final strategic decisions.

The system may:

recommend
prioritize
warn
explain
detect gaps
suggest experiments

The system must not silently make irreversible strategic or live-trading decisions without explicit approval.

32. Architectural Review Questions

Before implementing a major component, ask:

What knowledge does this create?
What uncertainty does this reduce?
Which future decision does it improve?
What raw metrics does it preserve?
How is it explained?
How is it tested?
How does it fail safely?
Is it reusable?
Does it increase or reduce complexity?
Would this still make sense in five years?
33. Long-Term Product Definition

The Sniper-Bot is not merely:

a trading bot

It is:

a scientific self-improvement system for decision-making,
with algorithmic trading as its first domain.
34. The Central Optimization Target

The system should not only optimize:

ROI
winrate
profit factor
drawdown

It should also optimize:

knowledge quality
uncertainty reduction
expected knowledge gain
decision robustness
scientific confidence
research efficiency

Better knowledge should eventually produce better trading decisions.

35. Architectural Oath

We will not optimize for speed at the expense of correctness.

We will not introduce complexity without measurable benefit.

We will not accept black-box decisions as core architecture.

We will not discard raw information that may be useful for future reasoning.

We will not add modules only to increase module count.

We will not treat performance without evidence as knowledge.

We will prefer reusable scientific building blocks over isolated features.

We will preserve explainability.

We will model uncertainty explicitly.

We will document important decisions.

We will test before scaling.

We will value stability as a core function.

We will build the process that creates better systems.

The objective is not to create more code.

The objective is to create more reliable knowledge.

36. Final Statement

The Sniper-Bot project aims to become a modular, scientifically grounded, self-improving decision architecture.

Its first domain is trading.

Its deeper purpose is to build a system that observes, hypothesizes, validates, learns, reasons, and improves in a reproducible and explainable way.

Every future component should be judged by whether it makes the whole system more intelligent, more stable, more understandable, or more capable of producing reliable knowledge.

This document is the architectural reference for that standard.
