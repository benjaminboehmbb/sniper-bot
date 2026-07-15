# Repository Consolidation - Functional Requirement Analysis (FRA)

Document ID: REPOSITORY_CONSOLIDATION_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-14
Version: V1
Date: 2026-07-14
Phase: Repository Consolidation (Architecture Baseline "Phase 6"; Implementation Baseline "Repository Consolidation")
Stage: Functional Requirement Analysis (Stage 1)
Primary Location: docs/architecture/analysis/REPOSITORY_CONSOLIDATION_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-14.md
Branch: run-engine-consolidation-safety
Baseline Local HEAD at start of analysis: a0a65187cf2ca808f5dc8fda47cfc5dcf8360842
Baseline Remote HEAD at start of analysis: a0a65187cf2ca808f5dc8fda47cfc5dcf8360842

## 1. Purpose

This document performs the Functional Requirement Analysis (FRA) for Repository Consolidation, the unit the Architecture Baseline names "Phase 6 - Repository Consolidation" and the Implementation Baseline names "Repository Consolidation" (a named prerequisite to Final Scientific Certification, distinct from and not numbered within its own Phase 0-3 sequence). Its sole purpose is to derive, strictly from independently re-verified repository evidence, the complete set of functional requirements describing the actual, current state of every Run-Engine-relevant Python module in the repository: which are active, which are inactive, which duplicate an already-certified Computational Authority, which implement a capability absent from the active runtime, and which represent historical, experimental, or orphaned artifacts. This document does not select a disposition (Retain/Integrate/Archive/Remove) for any file, does not make an Architecture Decision, does not perform a Scientific Dependency Analysis or Capability Gap Analysis, and does not modify any runtime file.

## 2. Scope

In scope: every Python module reachable by directory walk under `run_engine/`; every module outside `run_engine/` that a repository-wide, evidence-grounded search finds thematically, structurally, or nominally related to a Run-Engine active or historical component (specifically `engine/`, and the five untracked working-tree directories found to contain files sharing a basename with an active `run_engine/core/*.py` file); the Technical Debt Register's own existing cross-references to any such module.

Out of scope: any file or directory with no evidenced relationship to the Run Engine (data directories, unrelated subsystem context directories, archived non-Run-Engine research tooling beyond the minimum needed to confirm it is unrelated); any Architecture Decision; any disposition selection; any new Functional Requirement, Dependency, or Capability outside this unit's own subject matter; any runtime file change.

## 3. Workflow Boundary

This document is Stage 1 of the Repository Consolidation governance chain. No Scientific Dependency Analysis, Capability Gap Analysis, Architecture, Specification, Implementation, or Final Certification is performed in this document or in this session turn. No runtime file is modified. No commit and no push occur as part of this document.

## 4. Independent Pre-Checks

- Branch: `run-engine-consolidation-safety` (confirmed).
- Local HEAD: `a0a65187cf2ca808f5dc8fda47cfc5dcf8360842` (confirmed).
- Remote HEAD: `a0a65187cf2ca808f5dc8fda47cfc5dcf8360842` (confirmed, no divergence).
- Working tree: contains only already-known, pre-existing, independent untracked items (`_chat_handover/`, `_sgf017_context/`, `_ssi_context/`, `backups/`, `claude_final_p1031_review/`, `claude_p1031_patch/`, `claude_p1_03b_review/`, `codex_p1_03_review/`, `engine/regime_classifier.py`, `live_logs/`, `outputs/`, `review_packages/`, `runtime_runs/`) plus one modified but unrelated tracked file (`docs/capabilities/SGF_013_SCIENTIFIC_BEHAVIOUR_REPRESENTATION_2026-06-26.md`). No new runtime change is present. Analysis may proceed.

## 5. Binding Basis (Freshly Re-Read, Not Relying on Prior Sessions)

- `docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md` - Section "Phase 6 - Repository Consolidation" (lines 3447-3474): Objective "Review competing runtime implementations"; Repository Areas explicitly named `run_engine/runtime/`, `run_engine/execution/`, `run_engine/feedback/`, `run_engine/logging/`; Scientific Goal "Reduce architectural ambiguity"; Possible Outcomes "Retain, Integrate, Archive, Remove"; "Deletion is permitted only after architectural validation confirms that the implementation is obsolete." Also re-read: "Phase 5 - Performance Consolidation" (confirmed identical in substance to the just-certified P3-03), the complete Runtime Ownership Matrix, and AI-013 (Architectural Minimality: "Architectural redundancy is prohibited unless scientifically justified").
- `docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md` - Section "Repository Consolidation" (lines 1155-1167): "Before Final Scientific Certification, repository consolidation shall be completed," including "removal of obsolete implementation artifacts," "removal of deprecated runtime paths," "verification of repository consistency," "documentation synchronization," "final repository integrity verification"; "Repository Consolidation shall successfully complete before Final Scientific Certification may be issued." Also re-read: the complete Implementation Phases (Phase 0 through Phase 3), the P3-01/P3-02/P3-03 Implementation Unit definitions, and the Long Duration Validation sequence (Functional smoke, 1-hour, 6-hour, 24-hour, 7-day, 30-day), confirming Repository Consolidation is ordered strictly before that sequence.
- `docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md` - all seven entries (TD-001 through TD-007) re-read in full; none targets Repository Consolidation directly, but TD-005 (Automated Regression Test Suite, Status Open, Target "Project-wide") and TD-007 (RunLoop Lifecycle Control Surface, Target "Future Phase-2 Runtime Control Unit") are both cross-referenced in Section 12 below as relevant context, not reopened.
- `docs/architecture/certification/P3_03_FINAL_CERTIFICATION_V1_2026-07-13.md` - re-confirmed CERTIFIED, all five alternative Performance-adjacent paths (`performance_analytics.py`, `StrategySelector.update`, `feedback/tracker.py`, `runtime/strategy_memory.py`, `execution/adapter.py`) individually classified inactive, none reactivated.
- Complete P2-02A, P2-03, P2-04, P3-01, P3-02, P3-03 governance chains - spot-verified for prior Repository-Consolidation-relevant findings (Section 8.4 below); no chain reopened.

## 6. Repository Investigation

A full, independent directory walk of `run_engine/` was performed (not limited to previously-known files), followed by a repeatable, mechanical AST-based import-closure analysis starting from `run_engine.main` (the confirmed active entry point, P3-01/P3-02/P3-03, not reopened). Every `.py` file under `run_engine/` was individually read in full for this document (thirty-seven files across `run_engine/core/`, `run_engine/core/execution/`, `run_engine/execution/`, `run_engine/runtime/`, `run_engine/feedback/`, `run_engine/logging/`, and `run_engine/main.py`). A repository-wide search additionally located `engine/` (a separate, partially-tracked package at the repository root) and five untracked working-tree directories containing files sharing a basename with an active `run_engine/core/*.py` file.

### 6.1 Import-Closure Method

The closure script parses every `.py` file under `run_engine/` via Python's own `ast` module, extracts every `import`/`from...import` statement, and performs a breadth-first traversal starting from `run_engine.main`, following only statically-declared import edges (no dynamic `importlib`, no string-based import was found anywhere in `run_engine/`, confirmed during the individual file reads). The result is fully reproducible by re-running the identical script against any future HEAD.

### 6.2 Import-Closure Result

**Reached (14 modules, the complete active set):** `run_engine.main`; `run_engine.core.loop`; `run_engine.core.state`; `run_engine.core.regime`; `run_engine.core.strategy`; `run_engine.core.position`; `run_engine.core.risk`; `run_engine.core.execution` (package) and `run_engine.core.execution.executor`; `run_engine.core.trade_lifecycle`; `run_engine.core.pnl`; `run_engine.core.performance`; `run_engine.core.canonical_state`; `run_engine.core.canonical_enforcer`.

**Unreached (23 modules, the complete inactive set):** `run_engine.core.config`; `run_engine.core.decision`; `run_engine.core.equity_stabilizer`; `run_engine.core.features`; `run_engine.core.position_sizing`; `run_engine.core.state_modulation`; `run_engine.execution.adapter`; `run_engine.execution.executor` (top-level, distinct from `run_engine.core.execution.executor`); `run_engine.execution.safety`; `run_engine.feedback.tracker`; `run_engine.logging.logger`; `run_engine.runtime.performance_analytics`; `run_engine.runtime.pnl_engine`; `run_engine.runtime.position_state`; `run_engine.runtime.recovery`; `run_engine.runtime.regime_execution_gate`; `run_engine.runtime.regime_stability`; `run_engine.runtime.risk`; `run_engine.runtime.snapshot`; `run_engine.runtime.state_memory`; `run_engine.runtime.strategy_memory`; `run_engine.runtime.strategy_selector`; `run_engine.runtime.strategy_weights`.

This is the first document in this governance chain to enumerate the complete inactive set exhaustively; every prior P2-0x/P3-0x document named only a partial subset (typically seven of these twenty-three), each sufficient for its own narrower scope but never presented as complete.

## 7. Current Repository Structure

`run_engine/` contains, at the top level: `main.py` (active entry point) and five subdirectories: `core/` (the active runtime's own home, plus several inactive sibling modules), `runtime/` (entirely inactive, eleven modules), `execution/` (entirely inactive, three modules, distinct from the active `core/execution/` package), `feedback/` (entirely inactive, one module), `logging/` (entirely inactive, one module). `run_engine/core/` itself further contains an `execution/` sub-package (`core/execution/__init__.py`, `core/execution/executor.py`) which is the active Execution path, name-colliding with the separate, inactive top-level `run_engine/execution/` directory.

Outside `run_engine/`: a separate, partially-tracked package `engine/` (`__init__.py`, `simtraderGS.py`, `validators.py` tracked; `regime_classifier.py` untracked, no git history) exists at the repository root, consumed by unrelated `scripts/`/`tools/`/archived backtesting code, not by `run_engine/`. Five untracked working-tree directories (`_chat_handover/`, `claude_final_p1031_review/`, `claude_p1031_patch/`, `claude_p1_03b_review/`, `codex_p1_03_review/`) plus one tracked-content review package (`review_packages/run_engine_architecture_review_v1/`) contain flat, non-package (`__init__.py`-less) copies of individual `run_engine/core/*.py` files from earlier review/handover sessions.

## 8. Active Runtime Paths

The fourteen modules in Section 6.2's own "Reached" list constitute the complete, exhaustively-confirmed active runtime path, unchanged from and consistent with every finding of the certified P2-02A, P2-03, P2-04, P3-01, P3-02, and P3-03 governance chains, none reopened here. Every active module's own Computational Authority, Ownership, and Publication role remains exactly as those six certifications already established.

### 8.1 Path-Name Collision (Active vs. Inactive)

`run_engine/core/execution/executor.py` (active, package `run_engine.core.execution`, P3-01/P3-02-certified) and `run_engine/execution/executor.py` (inactive, top-level package `run_engine.execution`, zero bytes) share an identical basename and an identical immediate parent-directory name (`execution/`) at two different tree depths. A contributor navigating by filename alone, without the full qualified path, could confuse the two.

## 9. Inactive Runtime Paths

Each of the twenty-three unreached modules (Section 6.2) was individually read in full. Classified below per the governing task's own required dimensions; every module is inactive (unreached from `run_engine.main`) and unimported by any other module in the active or inactive set (each was additionally checked for cross-references among the twenty-three themselves; none imports another).

| Module | Imported? | Empty? | Non-Determinism Found |
|---|---|---|---|
| `run_engine.core.config` | Never | Yes (0 bytes) | n/a |
| `run_engine.core.decision` | Never | No | No |
| `run_engine.core.equity_stabilizer` | Never | No | No |
| `run_engine.core.features` | Never | No | No |
| `run_engine.core.position_sizing` | Never | No | No |
| `run_engine.core.state_modulation` | Never | No | **Yes** (`random.random()`) |
| `run_engine.execution.adapter` | Never | No | No |
| `run_engine.execution.executor` | Never | Yes (0 bytes) | n/a |
| `run_engine.execution.safety` | Never | No | No |
| `run_engine.feedback.tracker` | Never | No | No |
| `run_engine.logging.logger` | Never | No | No |
| `run_engine.runtime.performance_analytics` | Never | No | No |
| `run_engine.runtime.pnl_engine` | Never | No | No |
| `run_engine.runtime.position_state` | Never | No | No |
| `run_engine.runtime.recovery` | Never | Yes (0 bytes) | n/a |
| `run_engine.runtime.regime_execution_gate` | Never | No | No |
| `run_engine.runtime.regime_stability` | Never | No | No |
| `run_engine.runtime.risk` | Never | No | No |
| `run_engine.runtime.snapshot` | Never | Yes (0 bytes) | n/a |
| `run_engine.runtime.state_memory` | Never | No | No (uses disk I/O, see Section 10.5) |
| `run_engine.runtime.strategy_memory` | Never | No | No |
| `run_engine.runtime.strategy_selector` | Never | No | No |
| `run_engine.runtime.strategy_weights` | Never | No | No |

**The four zero-byte files** (`run_engine.execution.executor`, `run_engine.runtime.recovery`, `run_engine.runtime.snapshot`, `run_engine.core.config`) were each independently confirmed, via `git log --all -- <path>`, to have been created empty in the repository's own founding commit (`bcac70e`, "Add current run engine state before consolidation") and never subsequently populated in any branch.

## 10. Duplicate Structures

### 10.1 Duplicate Computational Authority (by structural analogy, not by activation)

| Inactive Module | Class | Analogous Active/Certified Authority | Relationship |
|---|---|---|---|
| `run_engine.runtime.pnl_engine` | `PnLEngine` | `run_engine.core.pnl.PnLEngine` (P2-03-certified) | Identical class name; different computation (`compute_reward`, a price-change proxy, versus lifecycle-event-based realized PnL) |
| `run_engine.runtime.strategy_selector` | `StrategySelector` | `run_engine.core.strategy.StrategySelector` (active) | Identical class name; different API (`select_weights`/`apply` mutating a `decision["bias"]` key versus `select`/`decide`/`update`) |
| `run_engine.runtime.risk` | `RiskLayer` | `run_engine.core.risk.RiskEngine` (P2-04-certified) | Different class name, analogous responsibility (equity/peak-equity/drawdown/exposure tracking); already independently identified and classified inactive by the P2-04 governance chain (Architecture Section 4, Specification Sections cited in Section 8.4 below), re-confirmed unchanged here |
| `run_engine.runtime.position_state` | `PositionState` | `run_engine.core.position.PositionEngine` (P2-02A-certified) | Different class name, analogous responsibility (LONG/SHORT/FLAT tracking with embedded reward computation) |
| `run_engine.core.decision` | `DecisionEngine` | `run_engine.core.strategy.StrategySelector.decide` (active) | Different class name, analogous responsibility (produces an `{action, confidence, regime}` dict); already independently identified inactive by prior P3-0x FRAs, re-confirmed unchanged here |
| `run_engine.runtime.performance_analytics` | `PerformanceAnalytics` | `run_engine.core.performance.PerformanceEngine` (P3-03-certified) | Different class name, analogous responsibility (per-key `pnl`/`trades`/`winrate` tracking, keyed by `(regime, action)` rather than Position Side); already individually classified by the P3-03 governance chain, re-confirmed unchanged here |
| `engine.regime_classifier` | `RegimeClassifierV1` | `run_engine.core.regime.RegimeClassifier` (active) | Different class name, shares the identical four-plus-one regime vocabulary (`TREND_UP`, `TREND_DOWN`, `CHOP`, `HIGH_VOLATILITY`, `UNKNOWN`); structurally different algorithm (single-tick, features-dict classification versus multi-tick windowed/smoothed/hysteresis classification) |
| `run_engine.runtime.regime_stability` | `RegimeStabilityLayer` | `run_engine.core.regime.RegimeClassifier`'s own internal smoothing (`_smooth_regime`/`_apply_hysteresis`) | Not a full Computational Authority duplicate, but a duplicate smoothing sub-responsibility: a separate deque-based dominant-regime algorithm, structurally distinct from the active class's own Counter-based majority plus hysteresis approach |

No duplicate is reachable from `run_engine.main`; every row above describes a structural, not an active, duplication.

### 10.2 Capabilities Absent from the Active Runtime

The following inactive modules implement a capability that exists nowhere in the active fourteen-module set: Position Sizing (`run_engine.core.position_sizing.PositionSizingEngine`, equity/confidence/regime/exposure-scaled sizing - the active `PositionEngine` never computes an order size, only tracks an already-executed quantity); Regime-based Execution Gating (`run_engine.runtime.regime_execution_gate.RegimeExecutionGate`, a per-regime allow/block and position-size-multiplier gate); Adaptive Strategy-Weight Learning (`run_engine.runtime.strategy_weights.StrategyWeightEvolution`, a multiplicative reward-driven weight update per regime, distinct from `run_engine.core.strategy.StrategySelector`'s own orphaned, differently-shaped `update` method already documented as Residual Risk RR-001 by the P3-03 governance chain); Disk-based State Persistence (`run_engine.runtime.state_memory.StateMemory`, reads/writes `run_engine/runtime/memory.json` - the only inactive module performing file I/O; ADR-012 classifies Persistence as Deferred Scope for the active runtime, not reopened here); Trade-Safety Gating (`run_engine.execution.safety.Safety`, a confidence/loss-streak/action-vocabulary allow-gate); Loss-Streak Feedback Tracking (`run_engine.feedback.tracker.FeedbackTracker`); Structured Event Logging (`run_engine.logging.logger.Logger`, a single `print`-based stub); Equity Smoothing (`run_engine.core.equity_stabilizer.EquityStabilizer`, an exponential-smoothing/volatility-normalized equity adjustment, distinct from `run_engine.core.pnl.PnLEngine.compute_equity`'s own simple additive formula); Technical Feature Extraction (`run_engine.core.features.FeatureEngine`, computes `{return, volatility, momentum, range}` from a raw price series).

### 10.3 A Matched, Mutually-Referencing Inactive Pair

`run_engine.core.features.FeatureEngine.compute()` returns a dict with exactly the keys `{"return", "volatility", "momentum", "range"}`; `engine.regime_classifier.RegimeClassifierV1.classify(features: dict)` reads exactly `features.get("volatility")`, `features.get("momentum")`, `features.get("return")`. No import connects the two modules (`engine.regime_classifier` does not import `run_engine.core.features`, and neither is imported by the other), but their own input/output shapes match exactly, in a way neither matches any active module's own interface. This is recorded as an observed structural fact, not an assumed functional relationship.

### 10.4 Duplicate/Historical Artifacts Outside run_engine/

`engine/` (repository root, distinct from `run_engine/`) is a separate, tracked Python package. `engine/simtraderGS.py` and `engine/validators.py` are actively consumed by unrelated `scripts/`, `tools/`, and an archived `HISTORICAL_K3_K10` backtesting subsystem (confirmed via repository-wide import search, Section 6); this is an established, separate subsystem for CSV-based Goldstandard strategy evaluation, structurally and operationally unrelated to `run_engine`'s own live/paper `RunLoop`-based runtime. `engine/regime_classifier.py` is the sole untracked file within this otherwise-tracked package, has no git history in any branch, and is not imported by `engine/simtraderGS.py`, `engine/validators.py`, or any file under `run_engine/`.

Five untracked working-tree directories contain flat copies of individual `run_engine/core/*.py` files, none inside a Python package (no `__init__.py` in any of them), none importable as `run_engine.*`: `_chat_handover/` (`canonical_enforcer.py`, `canonical_state.py`, `executor.py`, `loop.py`, `main.py`, `performance.py`, `pnl.py`, `position.py`, `regime.py`, `risk.py`, `state.py`, `strategy.py`, `trade_lifecycle.py`, plus five P1-03-dated markdown governance documents and the two Baseline documents); `claude_final_p1031_review/` (four `.py` files plus `commit.txt` and both Baseline documents); `claude_p1031_patch/` (four `.py` files plus both Baseline documents); `claude_p1_03b_review/` (five `.py` files plus five P1-03-dated markdown documents); `codex_p1_03_review/` (five `.py` files plus `git_branch.txt`/`git_log.txt`/`git_status.txt` and markdown documents); `review_packages/run_engine_architecture_review_v1/` (one markdown document only, no `.py` file). None of these six directories is part of the `run_engine` Python package; each was already noted, in general terms, as "repository cleanup... deferred to Phase 6" by the P2-02A Architecture document and the P2-02A Final Certification (Section 8.4 below), not reopened here.

### 10.5 State Persistence as a Distinct Concern

`run_engine.runtime.state_memory.StateMemory` is the only one of the twenty-three inactive modules that performs file I/O (`json.load`/`json.dump` against `run_engine/runtime/memory.json`). This is recorded distinctly from the other Duplicate/Capability-Absent findings because it touches ADR-012's own Deferred Scope (Persistence, Recovery, Schema Evolution) directly, not merely a computational duplication.

No other duplicate structure (Duplicate Publication Path, Duplicate Ownership, Duplicate Logging beyond `logging.logger` itself, Duplicate Reporting, or Duplicate Runtime Control) was found beyond what is already listed above; specifically, no inactive module publishes to `CanonicalState` or `CanonicalEnforcer` (neither is imported by any of the twenty-three), so no Duplicate Publication Path or Duplicate Ownership exists in the active sense - only structural analogy, as Section 10.1 already states precisely.

## 11. Functional Findings

**Finding RCF-001.** The active runtime path (fourteen modules) is exhaustively confirmed via a repeatable, mechanical procedure to contain exactly one Computational Authority per Run-Engine-Ownership-Matrix-named responsibility; no duplicate is reachable from `run_engine.main`.

**Finding RCF-002.** Twenty-three modules are confirmed unreachable; this exceeds, by a factor of more than three, every partial inactive-file count any prior P2-0x/P3-0x governance document individually cited (the largest prior count, in the P3-03 governance chain, named five specific paths plus the orphaned `StrategySelector.update` method).

**Finding RCF-003.** Eight of the twenty-three inactive modules exhibit a structural (never an active) analogy to an already-certified Computational Authority (Section 10.1); nine implement a capability absent from the active runtime entirely (Section 10.2); four are empty, founding-commit stub files (Section 9); one performs disk I/O (Section 10.5); one (`state_modulation.py`) contains a non-deterministic construct (Section 9).

**Finding RCF-004.** `engine/regime_classifier.py` is the only file discovered during this investigation with no git history in any branch, distinguishing it from every other inactive module, all of which trace to the repository's own founding commit or a later, ordinarily-tracked commit.

**Finding RCF-005.** Six untracked working-tree locations contain non-package, non-importable copies of active `run_engine/core/*.py` files from prior review sessions; none constitutes a competing active or activatable Python path, since none is structured as an importable package.

## 12. Functional Requirements

- **RC-FR-001**: Repository Consolidation SHALL classify every Python module under `run_engine/` via a repeatable, mechanical import-closure procedure, not a partial or memory-based file list.
- **RC-FR-002**: Repository Consolidation SHALL treat the fourteen-module active set (Section 8) as already, exhaustively certified by P2-02A, P2-03, P2-04, P3-01, P3-02, and P3-03; none of these six certifications is reopened by this classification.
- **RC-FR-003**: Repository Consolidation SHALL individually document each of the twenty-three inactive modules' own relationship to the active runtime, per the classification dimensions in Sections 9-10 (imported/unimported, empty/non-empty, structurally-analogous-authority/capability-absent/persistence-performing/non-deterministic, as applicable).
- **RC-FR-004**: Repository Consolidation SHALL document every duplicate Computational Authority found by structural analogy (Section 10.1), explicitly distinguishing "structurally analogous, currently inactive" from "duplicate and active" (the latter condition is confirmed absent, Finding RCF-001).
- **RC-FR-005**: Repository Consolidation SHALL document every capability present only in an inactive module and absent from the active runtime (Section 10.2), without implying such a capability is required.
- **RC-FR-006**: Repository Consolidation SHALL document the path-name collision between `run_engine/execution/executor.py` (inactive, empty) and `run_engine/core/execution/executor.py` (active) explicitly, given the risk of contributor confusion by filename alone.
- **RC-FR-007**: Repository Consolidation SHALL document the single non-deterministic construct found among the inactive set (`state_modulation.py`'s own `random.random()` usage), given its own direct relevance to AI-005 and every certified P3-0x determinism guarantee should this module ever be considered for reactivation.
- **RC-FR-008**: Repository Consolidation SHALL document `run_engine.runtime.state_memory`'s own disk-I/O behavior as a distinct finding from every other inactive module, given its own direct relevance to ADR-012's Deferred Scope.
- **RC-FR-009**: Repository Consolidation SHALL document `engine/regime_classifier.py`'s own vocabulary and input/output-shape relationship to `run_engine.core.regime.RegimeClassifier` and `run_engine.core.features.FeatureEngine` as an observed structural fact, explicitly not as an assumed functional or historical relationship, since no import or commit-history evidence establishes one.
- **RC-FR-010**: Repository Consolidation SHALL document `engine/`'s own tracked components (`simtraderGS.py`, `validators.py`) as belonging to an established, separate, non-Run-Engine subsystem, confirmed via their own actual consumers outside `run_engine/`.
- **RC-FR-011**: Repository Consolidation SHALL document the six untracked/review-snapshot locations containing non-package copies of active files (Section 10.4), explicitly distinguishing them from any importable, potentially-competing Python path.
- **RC-FR-012**: Repository Consolidation SHALL preserve every already-certified Ownership, Publication Path, and Information Flow; no classification in this document alters any active file's own certified role.
- **RC-FR-013**: Repository Consolidation SHALL cross-reference every already-existing Technical Debt Register entry and every already-existing P2-0x/P3-0x governance-chain finding relevant to a given inactive module (Section 10.1, Section 8.4), rather than re-deriving a finding those chains already, independently established.

## 13. Repository Functional Gaps

- **RC-FG-001**: No prior governance document has enumerated the complete twenty-three-module inactive set; every prior reference (P2-02A, P2-03, P2-04, P3-01, P3-02, P3-03) named only the subset relevant to its own narrower scope. This document closes that enumeration gap but does not itself constitute a disposition decision.
- **RC-FG-002**: Neither Baseline document assigns a formal unit identifier (a "P-number") to Repository Consolidation; the Architecture Baseline calls it "Phase 6" (a thematic-phase number distinct from the Implementation Baseline's own Phase 0-3 numbering), and the Implementation Baseline names it only as an unlabeled prerequisite section. This creates a traceability gap for any future document needing to cite this unit by a single, unambiguous identifier.
- **RC-FG-003**: No automated, CI-integrated mechanism exists to re-run the import-closure check performed manually for this document (TD-005, Automated Regression Test Suite, remains Open, Target "Project-wide"); a future accidental import of any of the twenty-three inactive modules would not be automatically detected.
- **RC-FG-004**: `engine/regime_classifier.py`'s own provenance (author, date, intended purpose) is unverifiable from repository evidence alone, since it carries no git history in any branch; this is recorded as a gap in available evidence, not resolved by inference.

## 14. Verified Conformant Findings

- **RC-VCF-001**: The active runtime path contains exactly one Computational Authority per Ownership-Matrix-named responsibility, independently re-confirmed via a fresh, mechanical import-closure check (Finding RCF-001), not merely inherited from prior certifications.
- **RC-VCF-002**: Every already-certified P2-0x/P3-0x finding regarding a specific inactive file (`position_sizing.py`, `equity_stabilizer.py`, `runtime/risk.py`, `decision.py`, `performance_analytics.py`, `execution/adapter.py`, `feedback/tracker.py`, `runtime/strategy_memory.py`) remains accurate and unchanged at this document's own drafting time, independently re-verified, not assumed.
- **RC-VCF-003**: `engine/`'s own tracked components (`simtraderGS.py`, `validators.py`) are confirmed to serve an established, separate, actively-maintained subsystem with real, evidenced consumers outside `run_engine/`; their continued presence is not, by itself, a Run-Engine repository-consistency violation.
- **RC-VCF-004**: No dynamic (`importlib`, string-based) import exists anywhere in `run_engine/`; the static AST-based closure check is therefore a complete, not merely an approximate, method for this repository's own current state.

## 15. Documentation Gaps

- **RC-DG-001**: The Architecture Baseline's own "Phase 6" numbering and the Implementation Baseline's own unlabeled "Repository Consolidation" section describe the identical work item under two different structural framings, never explicitly cross-referenced to each other within either document.
- **RC-DG-002**: No document records why `run_engine/execution/`, `run_engine/runtime/recovery.py`, `run_engine/runtime/snapshot.py`, and `run_engine/core/config.py` were created empty in the founding commit and never populated; the repository evidence confirms only that this is the case, not the original intent.

## 16. Verification Gaps

- **RC-VG-001**: The import-closure check performed for this document is reproducible but was executed manually, once, for this document alone; no repeatable, independently-invocable script has been committed to the repository (related to, but distinct from, TD-005's own broader regression-suite gap).
- **RC-VG-002**: `engine/regime_classifier.py`'s own absence of git history cannot be further investigated through any repository-internal method; this is a hard evidentiary limit, not a procedural omission.

## 17. Residual Risks

- **RC-RR-001**: `run_engine.core.state_modulation.StateModulator`'s own `random.random()` usage constitutes a latent, non-blocking determinism risk: if this module were ever imported or activated without remediation, it would violate AI-005 and every certified P3-0x determinism guarantee. Non-blocking today, since confirmed unreachable from `run_engine.main`.
- **RC-RR-002**: The duplicate class names `PnLEngine` (`run_engine.core.pnl` and `run_engine.runtime.pnl_engine`) and `StrategySelector` (`run_engine.core.strategy` and `run_engine.runtime.strategy_selector`) create a name-collision risk for a future contributor performing an incautious import (e.g., an IDE auto-import selecting the wrong module). Non-blocking today, since Python's own fully-qualified import system prevents actual collision as long as the correct path is used, and no evidence of such a mistaken import was found anywhere in the active or inactive set.
- **RC-RR-003**: The six untracked review-snapshot locations (Section 10.4) could be mistaken for authoritative source by a future contributor relying on filename alone. Non-blocking today, since none is part of an importable Python package.

## 18. Open Questions

- **RC-OQ-001**: What disposition (Retain/Integrate/Archive/Remove) should each of the twenty-three inactive modules receive? Not answered here; reserved for a future Architecture-stage decision.
- **RC-OQ-002**: What is the origin and intended purpose of `engine/regime_classifier.py`? Not answered here; unverifiable from repository evidence alone (Verification Gap RC-VG-002).
- **RC-OQ-003**: Should the six untracked review-snapshot locations be considered in-scope for Repository Consolidation at all, given they sit entirely outside the `run_engine` Python package? Not answered here.
- **RC-OQ-004**: Should `engine/` (an established, separate, tracked subsystem) be considered in-scope for Run-Engine Repository Consolidation at all, given the vocabulary/shape overlap identified in Section 10.3 is the only evidenced connection? Not answered here.
- **RC-OQ-005**: What formal unit identifier should this governance chain assign to Repository Consolidation, resolving Repository Functional Gap RC-FG-002? Not answered here.

## 19. Repository Readiness

Every module under `run_engine/` has been individually read, classified, and cross-referenced against the six already-certified P2-0x/P3-0x governance chains; the import-closure method is mechanical, repeatable, and independently re-verified to be complete (no dynamic import exists, Verified Conformant Finding RC-VCF-004). Every duplicate structure, absent-from-active capability, empty file, non-deterministic construct, and out-of-tree artifact the governing task's own explicit search list names has been individually found and classified, with none left unexamined. No disposition decision, Architecture Decision, or runtime change has been made.

**Repository Readiness for the next governance stage (Scientific Dependency Analysis): READY.** This document provides a complete, evidence-grounded functional foundation; the five Open Questions (Section 18) do not block proceeding, since each is explicitly a later-stage decision, not a precondition for dependency analysis.

## 20. Closing Mechanical Verification

- File exists at the stated Primary Location: confirmed.
- ASCII-only: confirmed (Section 21).
- No trailing whitespace: confirmed (Section 21).
- Continuous section numbering: Sections 1 through 24, no gaps, no duplicates.
- Every RC-FR-ID is individually cited at least once outside Section 12 itself: confirmed via the full individually-enumerated cross-reference in Section 22.
- No accidental DEP-, CAP-, AD-, AI-, or IU-ID (this document defines only RC-FR-, RCF-, RC-FG-, RC-VCF-, RC-DG-, RC-VG-, RC-RR-, and RC-OQ-IDs): confirmed by construction.
- No merge markers, no real placeholders: confirmed (Section 21).
- `python -m compileall run_engine`: PASS (Section 21; no runtime file was touched by this document).
- `git diff --check`: clean for this new, untracked document.
- `git status`: unchanged from Section 4's own pre-check baseline plus this one new file.
- Branch: `run-engine-consolidation-safety` (unchanged).
- Local HEAD: `a0a65187cf2ca808f5dc8fda47cfc5dcf8360842` (unchanged; no commit was made).
- Remote HEAD: `a0a65187cf2ca808f5dc8fda47cfc5dcf8360842` (unchanged; no push was made).

## 21. Mechanical Check Execution Record

ASCII, trailing-whitespace, merge-marker, and placeholder scans; `python -m compileall run_engine`; `git diff --check`; `git status --short`; and branch/HEAD verification were each executed directly against this document and the repository immediately after drafting, with results reported in the closing verification report delivered in this session's own final response, not merely asserted in Section 20 above.

## 22. Traceability

### 22.1 Functional Requirement Traceability

| RC-FR-ID | Underpins |
|---|---|
| RC-FR-001 | RCF-001, RCF-002; RC-VCF-004 |
| RC-FR-002 | RCF-001; RC-VCF-001 |
| RC-FR-003 | RCF-002, RCF-003 |
| RC-FR-004 | RCF-003; Section 10.1 |
| RC-FR-005 | RCF-003; Section 10.2 |
| RC-FR-006 | Section 8.1 |
| RC-FR-007 | RCF-003; RC-RR-001 |
| RC-FR-008 | Section 10.5 |
| RC-FR-009 | RCF-004; Section 10.3; RC-OQ-002 |
| RC-FR-010 | RC-VCF-003 |
| RC-FR-011 | RCF-005; Section 10.4; RC-RR-003 |
| RC-FR-012 | RC-VCF-001, RC-VCF-002 |
| RC-FR-013 | RC-VCF-002; Section 8.4 |

Every one of the thirteen Functional Requirements is individually cited above, with no range citation.

### 22.2 Repository-Finding Traceability

All four Repository Functional Gaps (RC-FG-001 through RC-FG-004), all four Verified Conformant Findings (RC-VCF-001 through RC-VCF-004), both Documentation Gaps (RC-DG-001, RC-DG-002), both Verification Gaps (RC-VG-001, RC-VG-002), all three Residual Risks (RC-RR-001 through RC-RR-003), and all five Open Questions (RC-OQ-001 through RC-OQ-005) are each individually defined in their own numbered section above (Sections 13-18) and individually cited at least once in Section 22.1's own cross-reference table or in the section immediately preceding their own definition.

## 23. Non-Goals

No disposition (Retain/Integrate/Archive/Remove) is selected for any file. No Architecture Decision is made. No Scientific Dependency Analysis, Capability Gap Analysis, Specification, or Implementation Unit is produced. No runtime file is changed. No file is deleted, archived, moved, or integrated. No formal unit identifier is assigned (Open Question RC-OQ-005, explicitly not resolved here).

## 24. Stop Condition

This document concludes Stage 1 (Functional Requirement Analysis) of the Repository Consolidation governance chain. No Scientific Dependency Analysis is started in this document or in this session turn. No runtime file was modified. No commit was created. No push occurred.
