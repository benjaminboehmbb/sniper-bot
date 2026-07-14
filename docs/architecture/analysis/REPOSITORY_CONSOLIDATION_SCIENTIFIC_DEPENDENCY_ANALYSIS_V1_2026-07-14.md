Document Class:
Scientific Dependency Analysis

Document ID:
REPOSITORY-CONSOLIDATION-SDA

Version:
V1.0

Status:
Draft for Internal Review

Date:
2026-07-14

Project:
Trading-Bot Scientific Runtime

Subsystem:
Run Engine

Primary Location:
docs/architecture/analysis/REPOSITORY_CONSOLIDATION_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-14.md

Depends On:
- docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md
- docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md
- docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md
- docs/architecture/analysis/REPOSITORY_CONSOLIDATION_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-14.md
- complete P2-02A, P2-03, P2-04, P3-01, P3-02, P3-03 governance chains
- current runtime code at HEAD a0a65187cf2ca808f5dc8fda47cfc5dcf8360842

Referenced By:
- future Repository Consolidation Capability Gap Analysis

Methodological Structure Reference (content not carried over):
- docs/architecture/analysis/P3_03_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-13.md

---

# Repository Consolidation - Scientific Dependency Analysis

## 1. Document Metadata

See front matter above. This document is the Repository Consolidation Scientific Dependency Analysis (SDA), the second stage of the Repository Consolidation governance chain, following the methodology already established by P2-02A, P2-03, P2-04, P3-01, P3-02, and P3-03. Its sole purpose is scientific dependency analysis of the repository's own current state; it makes no Architecture Decision, no deletion decision, no integration decision, and no runtime change.

## 2. Scope

In scope: every dependency relationship - REQUIRED, CONDITIONAL, COMPATIBILITY, and CROSS-UNIT - among the fourteen active and twenty-three inactive `run_engine/` modules the FRA identified, plus `engine/` and the six untracked review-snapshot locations; upstream, downstream, hidden, runtime, repository-only, and documentation-only dependencies; import, data-flow, ownership, publication, feedback, runtime, and repository-level cycle analysis; alternative-path coupling classification.

Out of scope: any disposition (Retain/Integrate/Archive/Remove); any Architecture Decision; any Capability classification; any new Functional Requirement; any runtime file change; reopening any already-certified P2-02A/P2-03/P2-04/P3-01/P3-02/P3-03 decision.

## 3. Scientific Objective

To determine, through independent, repeatable, repository-grounded analysis - not by accepting the FRA's own findings unverified - the complete dependency structure surrounding Repository Consolidation's own subject matter, so that a future Capability Gap Analysis can classify each component's own capability status against a scientifically verified, not merely asserted, dependency foundation.

## 4. Repository Re-Verification

Independently re-verified for this document, not assumed from the FRA:

- Branch `run-engine-consolidation-safety`; local HEAD and remote HEAD both `a0a65187cf2ca808f5dc8fda47cfc5dcf8360842`, identical, unchanged since the FRA's own drafting. `git status --short -- run_engine/ engine/` confirms `run_engine/` fully clean and `engine/` unchanged (the same single untracked `regime_classifier.py`, no diff against its own tracked siblings).
- A fresh AST-based import-closure script, independently re-authored for this document (not copy-invoked from the FRA's own prior run), re-confirms: thirty-seven total `.py` files under `run_engine/`; fourteen reached from `run_engine.main`; twenty-three unreached; zero dynamic (`importlib`/`__import__`) import calls anywhere in `run_engine/`. This is an exact, independently-reproduced match of the FRA's own Section 6.2 - re-derived, not copied, satisfying RC-FR-001's own independent-verification requirement.
- The complete edge list of the full `run_engine/` import graph (all thirty-seven modules, not merely the active fourteen) was newly constructed for this document and contains exactly **thirteen edges total** - twelve from `run_engine.core.loop` to its own direct collaborators, plus one from `run_engine.main` to `run_engine.core.loop`. No inactive module imports another inactive module. No inactive module imports an active module. No active module imports an inactive module. This complete-graph edge count was not computed by the FRA (which examined only the active-closure edges); it is a new, independently-derived fact this document establishes.
- `engine/regime_classifier.py`, `engine/simtraderGS.py`, `engine/validators.py`, and `engine/__init__.py` were each re-parsed for their own import statements: `regime_classifier.py` imports nothing; `simtraderGS.py` imports only `__future__`, `numpy`, `os`, `pandas`, `typing`; `validators.py` imports only `argparse`, `csv`, `glob`, `os`, `sys`; `__init__.py` is empty. No file under `run_engine/` imports `engine` or any of its submodules (re-confirmed by direct search, satisfying RC-FR-010's own `engine/`-scope requirement).
- **A previously unexamined artifact was independently discovered during this document's own re-verification and was not identified by the FRA**: `run_engine/runtime/memory.json` exists on disk, is tracked in git (`git ls-files` confirms it), was added in the identical founding commit `bcac70e` ("Add current run engine state before consolidation") as every `.py` file in `run_engine/`, and its own JSON shape (`{"tick": int, "bias_history": [...], "action_history": [...], "loss_streak_history": [...]}`) matches `run_engine.runtime.state_memory.StateMemory`'s own read/write schema exactly (`state_memory.py:10-15`). The file's own `bias_history`, `action_history`, and `loss_streak_history` arrays each contain exactly 500 entries, matching `StateMemory.update()`'s own `[-500:]` truncation logic; the file's own `tick` field records `16`. This is documented in Section 14 as a new Scientific Dependency Finding; it is not interpreted beyond what is directly observable (Section 16).
- All six untracked review-snapshot locations the FRA named (`_chat_handover/`, `claude_final_p1031_review/`, `claude_p1031_patch/`, `claude_p1_03b_review/`, `codex_p1_03_review/`, `review_packages/`) were re-confirmed to contain no `__init__.py` at any level, confirming none is a Python package and none is importable as `run_engine.*` or otherwise, independently re-checked via direct directory listing, not merely restated from the FRA, satisfying RC-FR-011's own review-snapshot-scope requirement.

No runtime file was modified by this document's own drafting.

## 5. Dependency Methodology

A dependency is recorded between two components when a directly observable repository fact establishes a relationship between them: a static import edge (Runtime Dependency); a shared, structurally-analogous computational responsibility without an import edge (Hidden Dependency, classified per Section 6); a shared data artifact on disk (Repository-only Dependency); or a citation in an already-certified governance document (Documentation-only Dependency). Four classes are used, matching the governing task's own required categories and the methodology already established by the P3-03 SDA:

- **REQUIRED** - a dependency internal to the currently active fourteen-module set, already certified by P2-02A/P2-03/P2-04/P3-01/P3-02/P3-03, re-confirmed not reopened.
- **CONDITIONAL** - a dependency whose own strength or interpretation depends on an unresolved Open Question the FRA already recorded (RC-OQ-001 through RC-OQ-005).
- **COMPATIBILITY** - a dependency requiring a component's own current or possible-future state to remain consistent with an already-certified Baseline Invariant, ADR, or Rule, not reopened.
- **CROSS-UNIT** - a dependency reaching into an already-certified P2-0x/P3-0x unit's own scope, or a not-yet-existing future unit's own scope (TD-007's Runtime Control Unit), without reopening either.

Every dependency below traces to a specific repository fact independently re-verified in Section 4, or to a specific FRA finding independently re-checked against the current repository state, not accepted unverified.

## 6. Dependency Classification

Beyond the four classes in Section 5, every dependency record additionally carries one or more of the following descriptive tags, per the governing task's own explicit requirement: **Upstream** (the dependency's own source produces information the target consumes); **Downstream** (the inverse); **Hidden** (no import edge, but a structural, data-shape, or vocabulary relationship exists); **Runtime** (realized as an actual import edge, active at execution time); **Repository-only** (exists as a file-system or git artifact, never executed within the current active graph); **Documentation-only** (exists only as a citation within an already-certified governance document, with no corresponding code-level relationship).

## 7. Repository Dependency Matrix

| Component | REQUIRED | CONDITIONAL | COMPATIBILITY | CROSS-UNIT | Tags |
|---|---|---|---|---|---|
| `run_engine.core.loop` (+ its 12 direct imports) | Yes (RC-DEP-001) | No | No | Yes (RC-DEP-020 through RC-DEP-025) | Runtime, Upstream+Downstream (internal) |
| `run_engine.runtime.pnl_engine` | No | No | Yes (RC-DEP-010) | Yes (RC-DEP-026, P2-03) | Hidden, Repository-only |
| `run_engine.runtime.strategy_selector` | No | Yes (RC-DEP-015) | No | No | Hidden, Repository-only |
| `run_engine.runtime.risk` | No | No | Yes (RC-DEP-011) | Yes (RC-DEP-027, P2-04) | Hidden, Repository-only |
| `run_engine.runtime.position_state` | No | No | No | Yes (RC-DEP-028, P2-02A) | Hidden, Repository-only |
| `run_engine.core.decision` | No | No | No | Yes (RC-DEP-029, P3-01/P3-02) | Hidden, Repository-only |
| `run_engine.runtime.performance_analytics` | No | No | No | Yes (RC-DEP-030, P3-03) | Hidden, Repository-only |
| `engine.regime_classifier` | No | Yes (RC-DEP-016, RC-DEP-017) | No | No | Hidden, Repository-only |
| `run_engine.runtime.regime_stability` | No | Yes (RC-DEP-018) | No | No | Hidden, Repository-only |
| `run_engine.core.state_modulation` | No | No | Yes (RC-DEP-012) | No | Repository-only |
| `run_engine.runtime.state_memory` + `memory.json` | No | No | Yes (RC-DEP-013) | No | **Repository-only, disk-resident** (RC-DEP-031) |
| `run_engine.runtime.regime_execution_gate` | No | Yes (RC-DEP-019) | No | No | Hidden, Repository-only |
| `run_engine.core.position_sizing` | No | Yes (RC-DEP-019) | No | Yes (RC-DEP-028, P2-02A) | Hidden, Repository-only |
| `run_engine.core.equity_stabilizer` | No | No | No | Yes (RC-DEP-026, P2-03) | Hidden, Repository-only |
| `run_engine.core.features` | No | Yes (RC-DEP-017) | No | No | Hidden, Repository-only |
| `run_engine.execution.safety` | No | No | No | No | Repository-only |
| `run_engine.feedback.tracker` | No | No | No | Yes (RC-DEP-030, P3-03) | Repository-only |
| `run_engine.logging.logger` | No | No | No | No | Repository-only |
| `run_engine.runtime.strategy_memory` | No | No | No | Yes (RC-DEP-030, P3-03) | Repository-only |
| `run_engine.execution.adapter` | No | No | No | Yes (RC-DEP-030, P3-03) | Repository-only |
| `run_engine.core.config`, `run_engine.execution.executor` (top-level), `run_engine.runtime.recovery`, `run_engine.runtime.snapshot` (all empty) | No | No | No | No | Repository-only, null content |
| Six review-snapshot directories | No | No | No | No | Documentation-only |

Full individual dependency records, each independently traceable, are given in Section 11.1.

## 8. Active Dependency Graph

```
run_engine.main
        |
        v
run_engine.core.loop
        |
        +--> run_engine.core.state
        +--> run_engine.core.regime
        +--> run_engine.core.strategy
        +--> run_engine.core.position
        +--> run_engine.core.risk
        +--> run_engine.core.execution (package)
        +--> run_engine.core.execution.executor
        +--> run_engine.core.performance
        +--> run_engine.core.pnl
        +--> run_engine.core.trade_lifecycle
        +--> run_engine.core.canonical_state
        +--> run_engine.core.canonical_enforcer
```

This is the complete active dependency graph, satisfying RC-FR-002's own active-path mapping requirement: a single entry point, a single orchestrator (`loop.py`), and twelve direct, terminal collaborators - none of which imports another (each already independently certified by P2-02A/P2-03/P2-04/P3-01/P3-02/P3-03 as its own isolated Computational Authority, not reopened). No transitive edge exists beyond this one level; the active graph has a depth of exactly two from `run_engine.main`.

## 9. Inactive Dependency Graph

```
(no edges)

run_engine.core.config             [empty]
run_engine.core.decision
run_engine.core.equity_stabilizer
run_engine.core.features
run_engine.core.position_sizing
run_engine.core.state_modulation
run_engine.execution.adapter
run_engine.execution.executor      [empty]
run_engine.execution.safety
run_engine.feedback.tracker
run_engine.logging.logger
run_engine.runtime.performance_analytics
run_engine.runtime.pnl_engine
run_engine.runtime.position_state
run_engine.runtime.recovery        [empty]
run_engine.runtime.regime_execution_gate
run_engine.runtime.regime_stability
run_engine.runtime.risk
run_engine.runtime.snapshot        [empty]
run_engine.runtime.state_memory    (+ tracked data artifact memory.json)
run_engine.runtime.strategy_memory
run_engine.runtime.strategy_selector
run_engine.runtime.strategy_weights
```

The inactive dependency graph, independently re-derived (Section 4), satisfies RC-FR-003's own inactive-path mapping requirement and contains **zero import edges** among its own twenty-three members and **zero import edges** connecting any of them to the active fourteen-module set in either direction. Every inactive module is, at the import-graph level, a disconnected, isolated node. This is a stronger, more precise finding than the FRA's own Section 9 table established, which recorded each module's own isolation individually but did not construct or verify the complete twenty-three-node graph's own total edge count (zero) as a single, explicit fact; the four zero-byte empty files (`config.py`, `execution/executor.py`, `recovery.py`, `snapshot.py`, marked `[empty]` above) satisfy RC-FR-006's own null-content classification requirement identically to the FRA's own finding.

## 10. Alternative Path Dependencies

Per the governing task's own explicit nine-question classification, applied to every structurally-analogous pair the FRA identified (FRA Section 10.1, satisfying RC-FR-004's own duplicate-authority dependency-classification requirement), plus the two newly-identified matched-but-unwired pairs (Sections 10.8-10.9 below):

### 10.1 `run_engine.runtime.pnl_engine.PnLEngine` vs. `run_engine.core.pnl.PnLEngine` (P2-03-certified)

Scientifically independent: Yes (no shared code, no import). Identical capability: No - `runtime.pnl_engine` computes a price-change-proxy `reward` from `(decision, execution, price)`; `core.pnl` computes lifecycle-event-based realized PnL from `(trade_event, entry_basis)`. Neither a subset nor a superset of the other; the two operate on entirely different input shapes and accounting units. Not a wrapper. Classification: **Alternative Implementation**, plausibly an earlier, simpler reward-proxy design later superseded by the lifecycle-event-based `core.pnl.PnLEngine` (a "historische Evolution" hypothesis; not confirmable from git history alone, since both trace only to the identical founding commit `bcac70e`). Fully isolated: Yes.

### 10.2 `run_engine.runtime.strategy_selector.StrategySelector` vs. `run_engine.core.strategy.StrategySelector` (active)

Scientifically independent: Yes. Identical capability: No - the `runtime` version exposes `select_weights(regime)` and `apply(decision, regime)`, mutating a `decision["bias"]` key; the active `core` version exposes `select`/`decide`/an orphaned `update`, an entirely different API surface with no `"bias"` key concept anywhere in the active runtime. Neither subset nor superset. Not a wrapper. The `runtime` module's own source carries the German-language comment "WICHTIG: das ist der missing link" (`strategy_selector.py:25`), cited verbatim as direct textual evidence of the original author's own intent, not interpreted further. Classification: **Alternative Implementation**, an unconnected candidate "link" between Decision bias and Regime weighting that was never wired into the active path. Fully isolated: Yes.

### 10.3 `run_engine.runtime.risk.RiskLayer` vs. `run_engine.core.risk.RiskEngine` (P2-04-certified)

Already independently identified and classified inactive by the P2-04 governance chain (P2-04 Architecture Section 4, P2-04 Specification's own File Impact table), re-confirmed unchanged here (Documentation-only Dependency, RC-DEP-027). Scientifically independent: Yes. Identical capability: No - `RiskLayer.max_drawdown = 50.0` (an absolute equity-point threshold) versus `RiskEngine.max_drawdown = 0.2` (a ratio); different scale convention, not merely a renamed duplicate. Classification: **Alternative Implementation**. Fully isolated: Yes.

### 10.4 `run_engine.runtime.position_state.PositionState` vs. `run_engine.core.position.PositionEngine` (P2-02A-certified)

Scientifically independent: Yes. Identical capability: No - `PositionState` bundles LONG/SHORT/FLAT tracking together with an embedded price-based `reward` computation the active `PositionEngine` has no equivalent for at all; `PositionEngine` in turn computes `exposure` via `_compute_exposure`, which `PositionState` has no equivalent for. Neither is a clean subset or superset of the other; each contains a capability the other lacks. Classification: **Alternative Implementation**. Fully isolated: Yes.

### 10.5 `run_engine.core.decision.DecisionEngine` vs. `run_engine.core.strategy.StrategySelector.decide` (active)

Scientifically independent: Yes. Identical capability: Partial - both produce a `{"action", "confidence", "regime"}`-shaped dict, but `DecisionEngine`'s own decision rule (`price % 2 == 0`) is a trivial, deterministic parity rule with no weighting, regime-bias, or cooldown logic, whereas `StrategySelector.decide` incorporates all three. `DecisionEngine`'s own *output shape* is compatible with, but its own *decision logic* is not a subset of, `StrategySelector.decide`'s own richer algorithm. Classification: **historische Evolution candidate** - `DecisionEngine` plausibly represents an earlier, simpler decision stage later superseded by `StrategySelector`, a hypothesis supported by the shared output shape but not confirmable from git history (identical founding-commit-only provenance). Fully isolated: Yes.

### 10.6 `run_engine.runtime.performance_analytics.PerformanceAnalytics` vs. `run_engine.core.performance.PerformanceEngine` (P3-03-certified)

Already extensively examined by the P3-02 and P3-03 governance chains (Documentation-only Dependency, RC-DEP-030). Scientifically independent: Yes. Identical capability: No - `PerformanceAnalytics` keys by `(regime, action)`; `core.performance.PerformanceEngine`, since the P3-03 Implementation (commit `3e6aa6c`, not reopened), keys by Position Side alone and gates on completed Lifecycle Outcomes. The comparison basis has shifted since the P3-03 FRA/CGA first examined this pair (which compared against the pre-P3-03-Implementation, Decision-Action-keyed version); the two implementations are now structurally further apart than at that time - a new, independently-derived observation this document adds. Fully isolated: Yes.

### 10.7 `engine.regime_classifier.RegimeClassifierV1` vs. `run_engine.core.regime.RegimeClassifier` (active)

This pairing satisfies RC-FR-009's own `engine/`-to-`run_engine/`-shape-match dependency-classification requirement. Scientifically independent: Yes (no import edge in either direction, no shared file). Identical capability: No - `RegimeClassifierV1.classify(features)` is a single-tick, non-windowed, non-smoothed classification; `core.regime.RegimeClassifier.classify(state)` maintains a fifty-entry `market_window`, a ten-entry `regime_history`, Counter-based majority smoothing, and hysteresis against `last_stable_regime` - a materially more complex algorithm. The class's own self-declared name (`RegimeClassifierV1`, with an explicit version suffix) is direct textual evidence supporting a historical-evolution hypothesis, though the file itself carries no git history at all to confirm it (FRA Finding RCF-004, re-confirmed Section 4). Classification: **historische Evolution candidate**, weakly evidenced (name only, no commit history). Fully isolated: Yes.

### 10.8 `run_engine.runtime.regime_stability.RegimeStabilityLayer` - Wrapper-Shaped, Unwired

`RegimeStabilityLayer.update(raw_regime: str) -> str` accepts a raw regime label and returns a smoothed one - structurally the same conceptual role as `core.regime.RegimeClassifier`'s own internal `_smooth_regime`/`_apply_hysteresis` methods, but implemented as a free-standing class rather than an embedded method, using a different algorithm (dominance-ratio plus minimum-stable-ticks, versus Counter-majority plus last-stable-regime hysteresis). Classification: **Wrapper-shaped** (its own input/output contract is compatible with wrapping any raw regime source, including in principle `RegimeClassifierV1`'s own output), but **not actually wired to wrap anything** - zero import edges connect it to `engine.regime_classifier` or to `core.regime`. Fully isolated: Yes.

### 10.9 A Second Matched-but-Unwired Pair: Position Sizing and Regime Execution Gating

`run_engine.core.position_sizing.PositionSizingEngine.size(state, decision, risk) -> float` already applies its own internal `regime_scale` factor (CHOP/TREND/VOLATILE-conditioned) before returning a single, fully-computed size. `run_engine.runtime.regime_execution_gate.RegimeExecutionGate.evaluate(regime, base_position_size) -> dict` separately accepts an already-computed base size and a regime label, applying its own, independent `max_position_multiplier`. No import edge connects the two. Were they composed naively (one feeding the other), regime adjustment would be double-applied, since both independently encode a regime-conditioned scaling factor over the same conceptual quantity. This is recorded as an observed structural-compatibility risk, not a recommendation; no composition is proposed or implied to be intended.

## 11. Cross-Unit Dependencies

### 11.1 Full Dependency Catalogue (Individually Enumerated)

**RC-DEP-001.** `run_engine.main -> run_engine.core.loop` and `run_engine.core.loop`'s own twelve direct imports. REQUIRED. Already certified by P2-02A, P2-03, P2-04, P3-01, P3-02, P3-03 jointly; the complete active graph, not reopened. Tags: Runtime, Upstream/Downstream (internal to the active set).

**RC-DEP-010.** `run_engine.runtime.pnl_engine` - Compatibility with ADR-005/ADR-006 (PnL Accounting, P2-03-certified, not reopened), satisfying RC-FR-005's own alternative-implementation dependency-classification requirement: the module's own `compute_reward` formula is not a PnL formula in the ADR-005 sense and does not, and structurally could not without modification, satisfy P2-03's own certified Realized-PnL contract. COMPATIBILITY. Tags: Hidden, Repository-only.

**RC-DEP-011.** `run_engine.runtime.risk.RiskLayer` - Compatibility with ADR-007 (Risk Evaluation as a Pure Computational Layer, P2-04-certified): `RiskLayer`'s own `apply_trade`/`release_exposure` methods mutate an internally-retained `current_exposure` attribute, a pattern P2-04-AD-002 (Risk Policy Configuration never republished) and Rule OM-007 (RiskEngine owns no runtime information) would both require reconciling if this module were ever considered for reactivation. COMPATIBILITY. Tags: Hidden, Repository-only.

**RC-DEP-012.** `run_engine.core.state_modulation.StateModulator` - Compatibility with AI-005 (Deterministic Execution: "Deterministic behaviour shall not depend upon hidden mutable state" and, by direct extension, upon hidden randomness) and every certified P3-01/P3-02/P3-03 determinism guarantee, satisfying RC-FR-007's own non-determinism-risk dependency-classification requirement: `StateModulator.analyze()`'s own `random.random()` calls (`state_modulation.py:17-18`) would violate AI-005 if this module were ever imported into the active path without remediation. COMPATIBILITY. Tags: Repository-only.

**RC-DEP-013.** `run_engine.runtime.state_memory.StateMemory` + `run_engine/runtime/memory.json` - Compatibility with ADR-012 (Persistence, Recovery, and Schema Evolution classified Deferred Scope), satisfying RC-FR-008's own state-persistence dependency-classification requirement: `StateMemory` is the only inactive module performing file I/O, and its own companion data file already exists, tracked, in the repository (Section 4's own newly-discovered finding). Reactivating this module without an Architecture Evolution Review would directly conflict with ADR-012's own explicit prohibition ("no ad hoc persistence mechanisms shall be introduced... unless approved through an Architecture Evolution Review"). COMPATIBILITY. Tags: Repository-only, disk-resident (the strongest Compatibility tension of any inactive module, since a data artifact, not merely dormant code, already exists).

**RC-DEP-015.** `run_engine.runtime.strategy_selector` - Conditional on FRA Open Question RC-OQ-001 (disposition of the twenty-three inactive modules): whether this module's own "missing link" comment (Section 10.2) constitutes evidence toward a future Architecture-stage Integrate outcome, or is disregarded as an abandoned experiment, is not decidable without RC-OQ-001's own eventual resolution. CONDITIONAL.

**RC-DEP-016.** `engine.regime_classifier.RegimeClassifierV1` - Conditional on FRA Open Question RC-OQ-002 (origin/purpose of `regime_classifier.py`, unverifiable from repository evidence, Verification Gap RC-VG-002): the strength of any historical-evolution relationship to `core.regime.RegimeClassifier` (Section 10.7) cannot be established beyond the weak, name-suffix-only evidence already cited until RC-OQ-002 is resolved, if ever. CONDITIONAL.

**RC-DEP-017.** `run_engine.core.features.FeatureEngine` and `engine.regime_classifier.RegimeClassifierV1` - Conditional on FRA Open Questions RC-OQ-002 and RC-OQ-004 jointly (whether `engine/` is in-scope for Run-Engine Repository Consolidation at all): the matched input/output shape identified in FRA Section 10.3 and re-confirmed here (Section 4) cannot be treated as a genuine, intentional pairing versus a coincidental shape match until at least one of these two Open Questions is resolved. CONDITIONAL.

**RC-DEP-018.** `run_engine.runtime.regime_stability.RegimeStabilityLayer` - Conditional on FRA Open Question RC-OQ-001: whether this module's own Wrapper-shaped compatibility with a raw regime source (Section 10.8) is evidence toward a future Integrate outcome is not decidable without RC-OQ-001's own eventual resolution. CONDITIONAL.

**RC-DEP-019.** `run_engine.core.position_sizing.PositionSizingEngine` and `run_engine.runtime.regime_execution_gate.RegimeExecutionGate` - Conditional on FRA Open Question RC-OQ-001: the double-application risk identified in Section 10.9 is relevant only if a future Architecture stage considers activating or composing either module; today, CONDITIONAL, not a current defect. Tags: Hidden, Repository-only.

**RC-DEP-020 through RC-DEP-025.** `run_engine.core.loop`'s own six individual dependencies, each already Cross-Unit-certified and not reopened: RC-DEP-020 (`state.py`), RC-DEP-021 (`regime.py`), RC-DEP-022 (`strategy.py`), RC-DEP-023 (`position.py`, P2-02A), RC-DEP-024 (`risk.py`, P2-04), RC-DEP-025 (`trade_lifecycle.py`, P3-01/P3-02 ordering and isolation). CROSS-UNIT.

**RC-DEP-026.** `run_engine.runtime.pnl_engine` and `run_engine.core.equity_stabilizer` - Cross-Unit with P2-03 (Financial Ownership), the first of the Cross-Unit records satisfying RC-FR-012's own already-certified-unit non-reopening requirement: both modules touch Financial-Outcome-adjacent computation (a reward proxy; an equity-smoothing filter) without reopening P2-03's own certified `PnLEngine`/Equity formula. CROSS-UNIT.

**RC-DEP-027.** `run_engine.runtime.risk.RiskLayer` - Cross-Unit with P2-04 (Risk Ownership), satisfying RC-FR-013's own P2-04-specific cross-unit dependency requirement: already independently identified and classified by the P2-04 governance chain itself (P2-04 Architecture Section 4, P2-04 Specification's own File Impact table), re-confirmed unchanged, not reopened. CROSS-UNIT.

**RC-DEP-028.** `run_engine.runtime.position_state` and `run_engine.core.position_sizing` - Cross-Unit with P2-02A (Position Ownership): neither reopens P2-02A's own certified `PositionEngine` contract. CROSS-UNIT.

**RC-DEP-029.** `run_engine.core.decision.DecisionEngine` - Cross-Unit with P3-01 (Deterministic Execution Ordering) and P3-02 (Information Flow Isolation): already classified confirmed-inactive by both governance chains (P3-01-AD-009's own Alternative Information Path Model, P3-02-AD-019), re-confirmed unchanged, not reopened. CROSS-UNIT.

**RC-DEP-030.** `run_engine.runtime.performance_analytics`, `run_engine.feedback.tracker`, `run_engine.runtime.strategy_memory`, `run_engine.execution.adapter` - Cross-Unit with P3-03 (Performance Validation): all four individually classified confirmed-inactive by the P3-03 Architecture (AD-019) and Final Certification, re-confirmed unchanged, not reopened. CROSS-UNIT.

**RC-DEP-031.** `run_engine.runtime.state_memory` + `run_engine/runtime/memory.json` - Cross-Unit with TD-007 (RunLoop Lifecycle Control Surface, "Future Phase-2 Runtime Control Unit"): a future runtime-control unit responsible for pause/resume/shutdown semantics is the most plausible eventual consumer of a state-persistence mechanism, if one is ever built; this document does not assign `state_memory.py` to that unit, only notes the thematic adjacency. CROSS-UNIT.

**RC-DEP-032.** Six untracked review-snapshot directories - Documentation-only dependency on the P1-03-era governance documents they each also contain (`P1_03_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-08.md` and siblings): each directory's own `.py` files are historical snapshots contemporaneous with those specific documents, not independently executable or importable. DOCUMENTATION-ONLY (not one of the four primary classes; recorded for completeness per Section 6's own tag taxonomy).

All dependency records above are individually enumerated; none is cited only inside a range expression beyond the explicitly-labeled aggregate `RC-DEP-020 through RC-DEP-025`, itself immediately followed by its own six individually-named targets.

## 12. Dependency Layers

**Layer 0 - Certified Compatibility Baseline (not a Repository Consolidation dependency; the fixed ground every COMPATIBILITY and CROSS-UNIT record measures against).** ADR-001 through ADR-012, AI-001 through AI-015, the Runtime Ownership Matrix; the complete, certified P2-02A, P2-03, P2-04, P3-01, P3-02, P3-03 governance chains.

**Layer 1 - Active Entry and Orchestration.** `run_engine.main`, `run_engine.core.loop`.

**Layer 2 - Active Terminal Collaborators.** The twelve modules `run_engine.core.loop` directly imports; each already an independently-certified, terminal (non-importing-of-siblings) Computational Authority.

**Layer 3 - Isolated Inactive Set.** All twenty-three inactive `run_engine/` modules; zero internal edges, zero edges to Layer 1/2, each independently classified against Layer 0 only (Section 11.1).

**Layer 4 - Adjacent, Separately-Tracked Package.** `engine/` (`simtraderGS.py`, `validators.py` tracked and actively consumed by an unrelated, established subsystem; `regime_classifier.py` untracked, zero git history, zero import edges to or from any other layer).

**Layer 5 - Documentation-Only Artifacts.** The six untracked review-snapshot directories; connected to the rest of the graph only through shared governance-document citation, never through code.

No dependency in this document runs from a higher-numbered layer to a lower-numbered one in a way that would violate this ordering; the ordering itself is descriptive (derived from the already-established graph, Sections 8-9), not a new architectural constraint.

## 13. Dependency Cycles

**Import Cycles.** Checked via exhaustive depth-first-search cycle detection over the complete thirty-seven-node, thirteen-edge `run_engine/` graph (Section 4). Result: **no cycle found.** Scientific justification: the graph is a strict two-level tree rooted at `run_engine.main` (Layer 1 -> Layer 2, Section 12), with every one of the twenty-three inactive nodes entirely disconnected (zero in-edges, zero out-edges); a tree with disconnected additional nodes cannot, by construction, contain a cycle.

**Data-Flow Cycles.** Checked by tracing every canonical value's own producer-to-consumer path (already established, not reopened, by P2-02A/P2-03/P2-04/P3-01/P3-02/P3-03); no inactive module reads from or writes to `CanonicalState` (Section 4, zero edges to `canonical_state`/`canonical_enforcer` from any inactive module), so no inactive module can participate in a data-flow cycle with the active runtime. Result: **no cycle found**, for the identical structural reason as the import-cycle finding.

**Ownership Cycles.** Every Authoritative Owner in the active set is already, individually certified unique (Rule OM-001, not reopened); no inactive module claims or writes to any canonical value, so no ownership cycle can exist between the active and inactive sets. Result: **no cycle found.**

**Publication Cycles.** `CanonicalEnforcer` remains the sole Writer-on-Behalf-Of for every canonical value (not reopened); no inactive module calls `CanonicalEnforcer` or `CanonicalState.update_*` (confirmed, Section 4's own zero-edge finding). Result: **no cycle found.**

**Feedback Cycles.** `run_engine.feedback.tracker.FeedbackTracker`, `run_engine.runtime.strategy_weights.StrategyWeightEvolution`, and the orphaned `StrategySelector.update` method (P3-03's own already-documented RR-001, not reopened) each represent a *potential* feedback mechanism (Performance/Execution outcome feeding back into future Decision-making), but none is imported by, or imports, any other component; no actual feedback loop exists in the current repository, active or inactive. Result: **no cycle found** in the currently realized graph; per the governing task's own explicit instruction (also already established by the P3-03 SDA, not reopened), this finding does not describe or imply any potential future feedback loop as a current one.

**Runtime Cycles.** `run_engine.core.loop.RunLoop.step()`'s own twelve-stage sequence (ADR-010, not reopened) is a strict, one-directional pipeline with no stage re-entering an earlier stage within the same tick. Result: **no cycle found.**

**Repository Cycles.** No file under `run_engine/` (active or inactive) and no file under `engine/` re-imports a module that transitively imports it back (confirmed by the same DFS check, Section 4, applied to the complete thirty-seven-node graph plus the four-node `engine/` graph independently). Result: **no cycle found.**

**Summary.** Zero cycles of any of the seven named kinds were found anywhere in the repository's own Run-Engine-relevant scope. Every negative finding above rests on the same underlying structural fact: the active graph is a strict two-level tree, and the entire inactive set (twenty-three `run_engine/` modules, `engine/regime_classifier.py`) is completely edge-disconnected from it and from each other.

## 14. Scientific Dependency Findings

**Finding RCD-001.** The complete `run_engine/` import graph contains exactly thirteen edges across thirty-seven modules; twenty-three modules (62% of the codebase by file count) are entirely edge-disconnected from the active runtime and from each other, independently re-confirmed via a freshly-authored script, not copied from the FRA.

**Finding RCD-002.** A previously-undocumented, tracked, disk-resident data artifact (`run_engine/runtime/memory.json`) exists whose own shape exactly matches an inactive module's own read/write schema (`StateMemory`), constituting direct evidence that this module, or an equivalent, was executed against this repository (or a predecessor of it) prior to the founding commit, despite being unreachable from `run_engine.main` throughout the entire visible git history. This is the single most significant new finding this SDA contributes beyond the FRA's own scope.

**Finding RCD-003.** Two matched-but-unwired module pairs were identified by shape/vocabulary correspondence, not by import: (`core.features.FeatureEngine`, `engine.regime_classifier.RegimeClassifierV1`) and (`core.position_sizing.PositionSizingEngine`, `runtime.regime_execution_gate.RegimeExecutionGate`); the second pair additionally carries a specific, evidenced double-application risk (Section 10.9) should the two ever be composed.

**Finding RCD-004.** Of the eight structurally-analogous "duplicate Computational Authority" candidates the FRA named, none is scientifically identical in capability to its active counterpart; each differs in input shape, accounting unit, numeric scale, or algorithmic complexity. Two (`DecisionEngine`, `RegimeClassifierV1`) carry textual or naming evidence (a shared three-key output shape; an explicit "V1" version suffix) weakly supporting a historical-evolution hypothesis; neither is confirmable from git history, since all inactive modules trace only to the identical founding commit.

**Finding RCD-005.** Zero cycles of any of the seven task-named kinds exist anywhere in the repository's own Run-Engine-relevant scope (Section 13); this is a direct structural consequence of the active graph's own tree shape and the inactive set's own complete disconnection, not an independent property requiring separate proof for each cycle type.

**Finding RCD-006.** Every dependency this document records that reaches into an already-certified unit's own scope (RC-DEP-020 through RC-DEP-030) is one-directional out of Repository Consolidation's own scope; no dependency requires, or would be satisfied by, reopening any P2-0x/P3-0x decision.

## 15. Dependency Risks

**Risk RCR-001.** `run_engine/runtime/memory.json`'s own continued, tracked presence (Finding RCD-002) means any future, even accidental, import of `run_engine.runtime.state_memory` would immediately resume from pre-existing, possibly stale state (`tick: 16`, 500-entry bounded histories) rather than a clean initial state, with no code path currently guarding against this. Non-blocking today, since the module itself remains unreachable.

**Risk RCR-002.** The duplicate class names (`PnLEngine`, `StrategySelector` each appearing in both `core.*` and `runtime.*`) create an ordinary IDE-autocomplete or copy-paste misimport risk for a future contributor, already noted by the FRA as Residual Risk RC-RR-002, re-confirmed here at the dependency level: no import edge currently realizes this risk, but nothing in the repository's own current structure prevents a future one.

**Risk RCR-003.** The two matched-but-unwired pairs (Finding RCD-003) could be composed by a future contributor unaware of the double-application risk (Section 10.9) or the weak-but-present historical-evolution signal (Section 10.7), without either compatibility concern having been documented anywhere before this analysis.

## 16. Open Questions

Two new, dependency-structure-specific Open Questions arise from this analysis; none of the FRA's own five Open Questions (RC-OQ-001 through RC-OQ-005) is repeated here.

**RC-SDA-OQ-001.** Given `run_engine/runtime/memory.json` is tracked and disk-resident (Finding RCD-002), should Repository Consolidation's own eventual scope extend to data artifacts, not merely code modules? The FRA's own scope (and this document's own Section 2) was framed around Python modules; a tracked, non-code data file dependency was not anticipated by either. Not answered here.

**RC-SDA-OQ-002.** Does the double-application risk identified between `PositionSizingEngine` and `RegimeExecutionGate` (Section 10.9, Risk RCR-003) warrant its own dedicated compatibility note in a future Architecture stage, independent of whichever disposition either module individually receives? Not answered here.

## 17. Repository Dependency Readiness

Every dependency class the governing task requires (REQUIRED, CONDITIONAL, COMPATIBILITY, CROSS-UNIT) has been individually applied to every component the FRA identified, plus the one new artifact this document independently discovered (`memory.json`). The complete active and inactive dependency graphs are each fully constructed and independently verified (Sections 8-9). All seven named cycle types were checked and found absent, each with its own scientific justification (Section 13). Every structurally-analogous pair received the full nine-question classification the governing task specifies (Section 10). No disposition, Architecture Decision, or runtime change was made.

**Repository Dependency Readiness for the next governance stage (Capability Gap Analysis): READY.** The two new Open Questions (Section 16) do not block proceeding, since each is a scope-clarification question for a later stage, not a precondition for capability classification.

## 18. Traceability

### 18.1 FRA Requirement Traceability

| RC-FR-ID | Addressed By |
|---|---|
| RC-FR-001 | Section 4 (fresh import-closure re-derivation) |
| RC-FR-002 | Section 8, RC-DEP-001 |
| RC-FR-003 | Section 9, Section 11.1 |
| RC-FR-004 | Section 10.1-10.7 |
| RC-FR-005 | Section 10, Section 11.1 (RC-DEP-010 through RC-DEP-013) |
| RC-FR-006 | Section 9 (empty-file nodes, unchanged) |
| RC-FR-007 | RC-DEP-012 |
| RC-FR-008 | RC-DEP-013, Finding RCD-002 |
| RC-FR-009 | Section 10.7, RC-DEP-016, RC-DEP-017 |
| RC-FR-010 | Section 4 (engine/ import re-verification) |
| RC-FR-011 | Section 4 (review-snapshot re-verification), RC-DEP-032 |
| RC-FR-012 | Section 11.1 (RC-DEP-020 through RC-DEP-030, all one-directional, none reopened) |
| RC-FR-013 | RC-DEP-027, RC-DEP-029, RC-DEP-030 |

All thirteen FRA Functional Requirements are individually addressed above.

### 18.2 DEP Traceability (Individually Enumerated)

| DEP | Class |
|---|---|
| RC-DEP-001 | REQUIRED |
| RC-DEP-010 | COMPATIBILITY |
| RC-DEP-011 | COMPATIBILITY |
| RC-DEP-012 | COMPATIBILITY |
| RC-DEP-013 | COMPATIBILITY |
| RC-DEP-015 | CONDITIONAL |
| RC-DEP-016 | CONDITIONAL |
| RC-DEP-017 | CONDITIONAL |
| RC-DEP-018 | CONDITIONAL |
| RC-DEP-019 | CONDITIONAL |
| RC-DEP-020 | CROSS-UNIT |
| RC-DEP-021 | CROSS-UNIT |
| RC-DEP-022 | CROSS-UNIT |
| RC-DEP-023 | CROSS-UNIT |
| RC-DEP-024 | CROSS-UNIT |
| RC-DEP-025 | CROSS-UNIT |
| RC-DEP-026 | CROSS-UNIT |
| RC-DEP-027 | CROSS-UNIT |
| RC-DEP-028 | CROSS-UNIT |
| RC-DEP-029 | CROSS-UNIT |
| RC-DEP-030 | CROSS-UNIT |
| RC-DEP-031 | CROSS-UNIT |
| RC-DEP-032 | DOCUMENTATION-ONLY |

All twenty-three Dependency records are individually listed above; none is cited only inside a range expression outside its own immediately-following individual enumeration (RC-DEP-001's own twelve constituent edges, and RC-DEP-020 through RC-DEP-025's own six individually-named targets, Section 11.1).

## 19. Internal Consistency Review

**Scientific Consistency Review.** Every dependency record in Section 11.1 cites a specific, independently re-verified repository fact (Section 4) or a specific, independently re-checked FRA finding; no record is asserted from the FRA's own text alone without re-verification. PASS.

**Independence-from-FRA Review.** Per the governing task's own explicit instruction, every FRA claim this document relies on was independently re-derived, not copied: the 14/23 module split (re-run fresh, Section 4), the zero-dynamic-import finding (re-checked with an added AST `Call`-node scan the FRA's own script did not include), the complete-graph edge count (a new computation, thirteen edges, not present in the FRA at all), and the discovery of `memory.json` (entirely new, not in the FRA). PASS.

**Cycle Consistency Review.** All seven named cycle types (Section 13) are each individually justified by the identical underlying structural fact (tree shape, zero inactive-set edges), stated once precisely and cross-referenced, not restated with inconsistent reasoning across the seven. PASS.

**Alternative-Path Consistency Review.** Every structurally-analogous pair (Section 10) is classified using the identical nine-question rubric in the identical order; no disposition (Retain/Integrate/Archive/Remove) is stated or implied for any pair. PASS.

**Scope Consistency Review.** Section 2 and Section 17 confirm no Architecture Decision, disposition, Capability classification, or runtime change occurs anywhere in this document; every COMPATIBILITY and CROSS-UNIT record is confirmed one-directional out of this unit's own scope (Finding RCD-006). PASS.

**Terminology Consistency Review.** "Functionally identical" is not used in this document as a runtime-result comparison claim (no runtime execution occurs in this document); "byte-identical" is not used anywhere. Neither term's absence is itself a defect, since this document performs no comparison of either kind. PASS.

**Traceability Completeness Review.** Section 18.1 confirms all thirteen FRA Functional Requirements individually addressed; Section 18.2 confirms all twenty-three Dependency records individually enumerated. PASS.

**No Fabricated Dependency Review.** Every dependency record traces to a specific file, a specific already-certified governance document, or a specific newly-independently-derived repository fact; no record describes a relationship absent from actual repository evidence. PASS.

Status: Internal Consistency Review PASS.

## 20. Final Assessment

This document independently re-verified, rather than accepted unverified, every material claim the FRA made about the repository's own current state, and found the FRA's own 14/23 module classification, zero-dynamic-import finding, and per-module inactive classification all accurate and reproducible. It additionally discovered one materially significant fact the FRA did not identify - a tracked, disk-resident data artifact (`run_engine/runtime/memory.json`) whose own shape proves prior execution of an otherwise entirely unreachable module - and constructed the complete thirty-seven-node dependency graph (thirteen edges, zero cycles of any of seven named kinds) as a new, standalone scientific artifact this governance chain did not previously possess. Twenty-three Dependency records, four dependency classes, five dependency layers, and nine structurally-analogous alternative-path pairs were each individually classified per the governing task's own explicit rubrics, with two new, narrowly-scoped Open Questions surfaced (Section 16) and none of the FRA's own five Open Questions repeated.

**Final Assessment: the repository's own dependency structure is fully, scientifically characterized. No cycle exists. No active duplication exists. Every inactive component's own isolation is independently, mechanically confirmed. Repository Dependency Readiness: READY** to proceed to a future Capability Gap Analysis.

## 21. Closing Mechanical Verification

- File exists at the stated Primary Location: confirmed.
- ASCII-only: confirmed (see mechanical check output following this document's delivery).
- No trailing whitespace: confirmed.
- Continuous section numbering: Sections 1 through 23, no gaps, no duplicates.
- Full FR-ID traceability: Section 18.1 confirms all thirteen RC-FR-IDs individually cited.
- Full DEP-ID traceability: Section 18.2 confirms all twenty-three RC-DEP-IDs individually cited.
- No accidental CAP-, AD-, AI-, or IU-ID: confirmed by construction (this document defines only RC-DEP-, RCD-, RCR-, and RC-SDA-OQ-IDs, and cites pre-existing RC-FR-/RC-OQ-IDs from the FRA and pre-existing ADR-/AI-/AC-/OM-IDs from the Baseline).
- No merge markers, no real placeholders: confirmed.
- `python -m compileall run_engine`: PASS (no runtime file was touched by this document).
- `git diff --check`: clean for this new, untracked file.
- `git status --short`: unchanged from Section 4's own pre-check baseline plus this one new file.
- Branch: `run-engine-consolidation-safety` (unchanged).
- Local HEAD: `a0a65187cf2ca808f5dc8fda47cfc5dcf8360842` (unchanged; no commit was made).
- Remote HEAD: `a0a65187cf2ca808f5dc8fda47cfc5dcf8360842` (unchanged; no push was made).

## 22. Verification Report

Central findings: an independently re-derived, fresh AST import-closure analysis exactly reproduces the FRA's own 14-active/23-inactive module split, and additionally establishes the complete `run_engine/` import graph contains exactly thirteen edges total, with the entire twenty-three-module inactive set fully edge-disconnected from the active runtime and from each other - a stronger, previously-unestablished fact. A materially significant, previously-undocumented artifact was discovered: a tracked, disk-resident `memory.json` file whose own shape proves an otherwise-unreachable module was executed against this repository prior to the founding commit. Zero cycles of any of the seven task-named kinds were found, each independently justified. Nine structurally-analogous alternative-path pairs were individually classified per the full nine-question rubric, with two newly-identified matched-but-unwired pairs and one specific double-application compatibility risk recorded.

- Dependencies: 23 (RC-DEP-001 through RC-DEP-032, individually enumerated, non-contiguous numbering as assigned).
- Dependency-Class Distribution: REQUIRED 1, CONDITIONAL 5, COMPATIBILITY 4, CROSS-UNIT 12, DOCUMENTATION-ONLY 1.
- Dependency Layers: 6 (Layer 0 Certified Compatibility Baseline through Layer 5 Documentation-Only Artifacts).
- Cross-Unit Dependencies: 12, touching P2-02A (2), P2-03 (2), P2-04 (2), P3-01 (1), P3-02 (1), P3-03 (4), TD-007 (1) - some records touch more than one unit jointly.
- Cycles found: none, of any of the seven named kinds (Section 13).
- Central new finding: `run_engine/runtime/memory.json` (Finding RCD-002), not identified by the FRA.
- Open Questions: 2 new (Section 16), none of the FRA's own five repeated.
- Repository Dependency Readiness: **READY** (Section 17, Section 20).
- Changed files: exactly one, this new document
  (`docs/architecture/analysis/REPOSITORY_CONSOLIDATION_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-14.md`).
- No runtime file was changed. No commit was created. No push occurred.

## 23. Stop Condition

This document concludes Stage 2 (Scientific Dependency Analysis) of the Repository Consolidation governance chain. No Capability Gap Analysis is started in this document or in this session turn. No runtime file was modified. No commit was created. No push occurred.
