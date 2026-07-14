Document Class:
Architecture

Document ID:
REPOSITORY-CONSOLIDATION-ARCHITECTURE

Version:
V1.0

Status:
Draft for Internal Review

Date:
2026-07-14

Project:
Trading-Bot Scientific Runtime

Subsystem:
Run Engine / Repository

Primary Location:
docs/architecture/REPOSITORY_CONSOLIDATION_ARCHITECTURE_V1_2026-07-14.md

Depends On:
- docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md
- docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md
- docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md
- docs/architecture/analysis/REPOSITORY_CONSOLIDATION_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-14.md
- docs/architecture/analysis/REPOSITORY_CONSOLIDATION_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-14.md
- docs/architecture/analysis/REPOSITORY_CONSOLIDATION_CAPABILITY_GAP_ANALYSIS_V1_2026-07-14.md
- complete P2-02A, P2-03, P2-04, P3-01, P3-02, P3-03 governance chains

Referenced By:
- future Repository Consolidation Specification (not yet created)

Methodological Structure Reference (content not carried over):
- docs/architecture/P3_03_PERFORMANCE_VALIDATION_ARCHITECTURE_V1_2026-07-13.md

---

# Repository Consolidation - Architecture

## 1. Document Metadata

See front matter above. This document is the Architecture stage of the Repository Consolidation governance chain, following the Functional Requirement Analysis (FRA), Scientific Dependency Analysis (SDA), and Capability Gap Analysis (CGA). It resolves the repository-level Functional Gaps, Dependencies, and Capabilities those three documents established into binding Architecture Decisions. No formal P-number Unit Identifier exists for Repository Consolidation in any Baseline; this document invents none (Section 26.20, RC-AD-020) and refers to the unit exclusively as "Repository Consolidation" or "RC" throughout.

## 2. Purpose

To define the binding target architecture for Repository Consolidation: a single, unambiguous Normative Repository Boundary; exactly one protected active Runtime Path; an explicit, individually justified Disposition (RETAIN / INTEGRATE / ARCHIVE / REMOVE / IGNORE) for every component the FRA, SDA, and CGA identified; and the structural, documentary, and procedural rules needed to keep the repository scientifically consistent and maintainable going forward. This document decides; it does not implement. No file is moved, deleted, archived, or integrated by this document itself.

## 3. Scope

In scope: Architecture Decisions covering the Normative Repository Boundary, the Active Runtime Boundary, a Disposition for all 14 active modules, all 23 inactive modules, `engine/regime_classifier.py`, `run_engine/runtime/memory.json`, the path-name collision, all matched-but-unwired pairs, all twelve untracked root-level directories, and the repository-structure-relevant portions of TD-004, TD-005, and TD-007.

Out of scope (per the governing task's own explicit Workflow-Grenze): Specification, Implementation, Final Certification; any file move, deletion, archiving, or integration performed now; any runtime file change; any change to untracked directories; any new Functional Requirement, Dependency, or Capability classification; any P4/P5/P6 or other new formal Unit Identifier.

## 4. Binding Baseline

Fully read prior to drafting: the Architecture Baseline, the Implementation Baseline, the Technical Debt Register, the Repository Consolidation FRA (13 Functional Requirements, RC-FR-001 through RC-FR-013), SDA (23 Dependency records, RC-DEP-001 through RC-DEP-032, non-contiguous), and CGA (15 Capabilities, RC-CAP-001 through RC-CAP-015); the complete P2-02A, P2-03, P2-04, P3-01, P3-02, and P3-03 governance chains. The P3-03 Architecture is used exclusively as a structural reference for this document's own layout; none of its content is carried over.

## 5. Repository Re-Verification

Independently re-verified immediately before drafting, not assumed from the FRA/SDA/CGA:

- Branch `run-engine-consolidation-safety`; local HEAD and remote HEAD (freshly fetched) both `a0a65187cf2ca808f5dc8fda47cfc5dcf8360842`, identical, unchanged since the CGA's own drafting.
- `run_engine/` and `engine/` both confirmed unchanged (`git diff --stat` and `git status --short`, both restricted to these two paths, empty except the already-known untracked `engine/regime_classifier.py`).
- A fourth independent AST-based import-closure run (reusing this session's own corrected script, which itself resolves package `__init__.py` module names correctly, a defect self-caught and fixed during the CGA's own drafting) reproduces the identical result once more: **37 total `.py` files under `run_engine/`, 14 active, 23 inactive, 13 total edges.**
- All 38 tracked files under `run_engine/` (37 `.py` files plus `memory.json`) and all 3 tracked files under `engine/` (`__init__.py`, `simtraderGS.py`, `validators.py`) individually re-listed via `git ls-files`.
- All twelve untracked root-level directories re-confirmed present with unchanged file counts against the CGA's own figures: `_chat_handover/` (21), `_sgf017_context/` (44), `_ssi_context/` (271), `backups/` (39), `claude_final_p1031_review/` (8), `claude_p1031_patch/` (6), `claude_p1_03b_review/` (21), `codex_p1_03_review/` (24), `live_logs/` (92), `outputs/` (456), `review_packages/` (1), `runtime_runs/` (26) - the CGA's own six newly discovered directories together total 928 files, re-confirmed unchanged.
- **A new observation, made during this document's own mandatory "alle getrackten Repository-Root-Komponenten" re-verification, beyond `run_engine/` and `engine/`**: the repository root contains a tracked top-level `archive/` directory (80 tracked files, entirely under `archive/HISTORICAL_K3_K10_2026-01-06/...`, an established, unrelated historical-backtesting archive predating this governance chain) and a tracked, zero-byte top-level file named `main` (distinct from `run_engine/main.py`, not a Python package, not imported by anything). Neither is part of `run_engine/`, `engine/`, or any of the twelve untracked directories the FRA/SDA/CGA examined; neither has any FRA/SDA/CGA-established Functional Requirement or Dependency behind it. Per this document's own explicit prohibition on inventing new Functional Requirements (Section 3), **no disposition is decided for either** - `archive/` is cited only as Repository Evidence relevant to Architecture Question 15 (Section 26.15), and the top-level `main` file is noted only to avoid a false impression of an undiscovered namespace collision (it is not one: different path, not a package, not imported).
- Similarly out of scope, confirmed present but not decided: `config/` (4 tracked files) and `configs/` (1 tracked file), two similarly-named top-level directories with no FRA/SDA/CGA coverage; `data/`, `live_l1/`, `reports/`, `scripts/`, `seeds/`, `strategies/`, `tools/` (all tracked, all pre-existing, all unrelated to `run_engine/` per the FRA's own repository-wide import search). This document's own Normative Repository Boundary Model (Section 9) states this scope limitation explicitly rather than silently.
- The Technical Debt Register re-confirmed unchanged: TD-004 `Status` still "Already Planned" (not yet updated to reflect the certified P3-03 closure, Section 29); TD-007 `Status` still "Deferred."

## 6. Scientific Definitions

- **Normative Repository** - the subset of the repository whose own tracked content is authoritative for scientific, governance, or runtime purposes, as opposed to locally-generated, external, or working-copy content.
- **Active Runtime Path** - the set of modules reachable by AST-based import closure from `run_engine.main`, currently the fourteen-module set the SDA and this document's own Section 5 re-confirm.
- **Runtime Authority** - a component certified, by an already-existing ADR or governance decision, as the sole computational source of a specific runtime value or decision.
- **Repository Namespace** - a unique, unambiguous dotted module path or file-system path within the Normative Repository; a Namespace Collision exists when two distinct files would resolve to the same or a confusingly similar path.
- **Disposition** - one of RETAIN, INTEGRATE, ARCHIVE, REMOVE, IGNORE, as defined by the governing task's own Dispositionsmodell (Section 15), applied individually to every component in scope.
- **Historical Provenance** - the git-history-traceable origin of a component; preserved when a component's own commit history remains reachable in the repository's own version control, regardless of its own current Disposition.
- **Generated Artifact** - a file produced by executing code (logs, run snapshots, review outputs, analysis results), as distinct from authored source or governance documentation.
- **Scratch/Review Artifact** - a working-copy snapshot whose own content duplicates, wholly or substantially, content that already exists in the Normative Repository at an authoritative, tracked location.

## 7. Architecture Problem Statement

Fourteen certified, active modules coexist in the same repository as twenty-three inactive modules, one untracked external alternative (`engine/regime_classifier.py`), one tracked runtime-state data artifact with no active producer or consumer (`memory.json`), one direct path-name collision, several matched-but-unwired capability pairs, and twelve untracked directories totaling roughly a thousand files, none of them decided upon by any prior governance stage. The CGA's own Final Assessment found the repository fully capable of rigorous scientific analysis (RC-CAP-001, RC-CAP-005, RC-CAP-014 all COMPLETE) but not yet structurally unambiguous (RC-CAP-011 MISSING) or durably self-maintaining (eleven Capabilities PARTIAL). This Architecture exists to close that specific gap: not by re-analyzing what the FRA/SDA/CGA already established, but by deciding, for every component already classified, what its own place in the repository's own future should be.

## 8. Architecture Objectives

Per the governing task's own explicit Ziel: resolve all thirteen RC-FRs; account for all twenty-three actually-used, non-contiguously-numbered RC-DEPs; address all fifteen RC-CAPs; explicitly decide the four Repository Functional Gaps; make the repository structure unambiguous and durably maintainable; protect exactly one active runtime path; prevent competing Computational Authorities; resolve unclear path and namespace areas; bindingly determine the treatment of inactive, historical, experimental, and scratch artifacts; preserve scientific traceability; and prepare the repository for future Long-Duration Validation.

## 9. Normative Repository Boundary Model

The Normative Repository, for the purposes of Repository Consolidation, comprises: (a) `run_engine/` in its entirety (all 37 `.py` files plus `memory.json`, active and inactive alike - inactivity does not remove a component from the Normative Repository, it only affects its own Disposition); (b) `engine/__init__.py`, `engine/simtraderGS.py`, `engine/validators.py` (tracked, established, unrelated to `run_engine/`, not reopened by this document); (c) `engine/regime_classifier.py` (untracked, evaluated for its own relationship to `run_engine/` only, Section 26.11); (d) the twelve untracked root-level directories the FRA and CGA identified (Section 26.12-26.13); (e) the governance-document locations under `docs/architecture/` (Section 26.22). All other top-level repository components identified during Section 5's own re-verification (`archive/`, top-level `main`, `config/`, `configs/`, `data/`, `live_l1/`, `reports/`, `scripts/`, `seeds/`, `strategies/`, `tools/`) are **explicitly outside this document's own Normative Repository Boundary decision** - no FRA, SDA, or CGA evidence exists for them, and deciding their status would require a Functional Requirement Analysis this document is not chartered to perform (Section 3).

## 10. Active Runtime Boundary Model

`run_engine.main` remains the sole, repository-grounded Runtime Entry Point (RC-DEP-001, re-confirmed Section 5). The Active Runtime Boundary is defined as, and exactly as, the AST-based import closure from `run_engine.main`: currently fourteen modules (Section 5). No inactive component may possess implicit Runtime Authority; every one of the twenty-three inactive modules is, by this same closure computation, formally outside the boundary until a future, dedicated Specification and Implementation stage - never this Architecture - moves it across that boundary. This is formalized as RC-AI-001 (Section 27).

## 11. Repository Namespace Model

Every active module's own dotted path is unique and collision-free (re-confirmed, Section 5). One collision exists between an active and an inactive path: `run_engine/core/execution/executor.py` (active) and `run_engine/execution/executor.py` (inactive, empty, top-level). This document resolves it in RC-AD-004 (Section 26.4). Going forward, the binding namespace rule (RC-AI-003) is: no two files under `run_engine/`, active or inactive, may share an identical basename under an identically-named immediate parent directory at different tree depths.

## 12. Active and Inactive Module Model

Fourteen active modules (Section 5, Section 10) and twenty-three inactive modules (Section 5), identical in composition and count to the FRA's, SDA's, and CGA's own independently, repeatedly re-derived result. This document assigns each of the twenty-three an individual Disposition (Section 25); none receives a collective, undifferentiated decision.

## 13. Computational Authority Model

Every active module already holds sole, certified Computational Authority for its own domain (Position: `core.position`, P2-02A; Financial: `core.pnl`, P2-03; Risk: `core.risk`, P2-04; Performance: `core.performance`, P3-03; determinism/ordering: `core.loop`, P3-01/P3-02). Eight inactive or external modules carry structurally-analogous, non-certified logic touching the same domains without holding Authority (`runtime.pnl_engine`, `runtime.position_state`, `runtime.risk`, `runtime.performance_analytics`, `runtime.strategy_selector`, `core.decision`, `engine.regime_classifier`, `runtime.regime_stability`). This Architecture's own binding rule (RC-AI-002) is that no Disposition may grant, or leave ambiguous, Computational Authority to any of these eight; each receives ARCHIVE (Section 25), removing it from the active namespace without erasing its own historical record.

## 14. Alternative Implementation Model

Per the SDA's own nine-question classification (not repeated here), none of the nine structurally-analogous pairs is scientifically identical to its active counterpart. This Architecture treats "structurally analogous but not certified" as, by itself, insufficient grounds for INTEGRATE (Section 26.17's own Integration Criteria require a dedicated future Specification, not mere code existence); every such pair's own Disposition is ARCHIVE unless an ADR-012 Deferred-Scope tie applies (Section 26.5).

## 15. Disposition Model

The governing task's own five-way Dispositionsmodell (RETAIN / INTEGRATE / ARCHIVE / REMOVE / IGNORE, as defined verbatim in the governing task) is adopted without modification. This Architecture's own aggregate Disposition distribution (Section 25, Section 38): of the 14 active modules, all 14 RETAIN; of the 23 inactive modules, 4 RETAIN (ADR-012 Deferred-Scope tie) and 19 ARCHIVE; `engine/regime_classifier.py` and `memory.json` receive IGNORE and ARCHIVE respectively (Sections 26.11, 26.6); all twelve untracked directories receive IGNORE (Sections 26.12-26.13). Zero components receive REMOVE in this Architecture (Section 26.16 states why).

## 16. Archive Model

ARCHIVE means a component leaves the active `run_engine/` (or `engine/`) namespace but remains git-tracked, under a namespace that cannot be imported by the active runtime and is unambiguously labeled non-active. This Architecture reuses, as precedent, the repository's own pre-existing top-level `archive/` directory convention (Section 5), without deciding to place Repository-Consolidation-scope archived files there (Section 26.15 states the naming convention only; no file is moved by this document).

## 17. Remove Criteria Model

Per Section 26.16 (Architecture Question 16): REMOVE requires jointly - no active import; no normative governance dependency; no necessary scientific evidence; no unique Capability; no necessary historical provenance; no relevant Integration; complete git history; independent verification passed. Evaluated against all twenty-three inactive modules and `engine/regime_classifier.py`, `memory.json`: every one of them fails at least the "no necessary historical provenance" criterion (each is evidence of pre-consolidation or exploratory development this governance chain's own "wissenschaftliche Nachvollziehbarkeit erhalten" objective requires preserving), so **zero REMOVE dispositions are issued by this Architecture.**

## 18. Integration Criteria Model

Per Section 26.17 (Architecture Question 17): INTEGRATE requires jointly - a clearly useful Capability not already present; compatibility with the certified Architecture; no duplicate Authority; its own future Specification and Implementation; and explicitly not code existence alone. No component evaluated in this document currently satisfies all five jointly without a dedicated future Specification stage first assessing feasibility; **zero INTEGRATE dispositions are issued by this Architecture.** `core.features` (FeatureEngine) and `core.position_sizing` (PositionSizingEngine) are the two candidates most plausibly INTEGRATE-eligible in a future cycle (neither collides with a certified active Authority), explicitly not decided now (Section 25).

## 19. Generated Artifact Model

`live_logs/`, `outputs/`, `runtime_runs/` (CGA Finding RCG-001) are Generated Artifacts per Section 6's own definition - produced by executing code, not authored. RC-AI-011 (Section 27) requires Generated Artifacts to remain outside the Normative Source Tree; all three receive IGNORE (Section 26.13), consistent with this rule and with the repository's own existing, partial `.gitignore` coverage of `live_logs/`.

## 20. Review and Scratch Artifact Model

`_chat_handover/`, `claude_final_p1031_review/`, `claude_p1031_patch/`, `claude_p1_03b_review/`, `codex_p1_03_review/`, `review_packages/` (FRA-scoped) and `_sgf017_context/`, `_ssi_context/`, `backups/` (CGA-scoped) are Scratch/Review Artifacts per Section 6's own definition - each either duplicates already-authoritative tracked content or holds ad hoc, dated, personal working material unrelated to the certified `run_engine/` record. All nine receive IGNORE (Sections 26.12-26.13).

## 21. Version-Control Boundary Model

A component is version-control-normative only if (a) it is currently tracked, or (b) this Architecture explicitly assigns it RETAIN or ARCHIVE (both of which presuppose or require tracked status). IGNORE-disposed components remain, by definition, outside version control; where a currently-tracked component (none in this document) were ever assigned IGNORE, its own removal from tracking would itself require a future, explicit Implementation step, not performed here.

## 22. Verification Tooling Model

Per Architecture Question 13 (Section 26.13... cross-referenced as 26.21 for the AD): a durable, repository-resident verification capability is required, at minimum reproducing the AST-based import-closure check this governance chain's own FRA, SDA, CGA, and this Architecture have each independently re-derived (the CGA's own drafting having self-caught a genuine defect in one such re-derivation, RC-CAP-004). No concrete implementation, file path, or function signature is decided here (explicitly deferred to a future Specification).

## 23. Long-Duration-Validation Readiness Model

Per Architecture Question 18 (Section 26.18): before any Smoke, 1-hour, 6-hour, 24-hour, 7-day, or 30-day run, the repository must present exactly one unambiguous active runtime path (RC-AI-001, satisfied once RC-AD-004's own path-collision resolution and RC-AD-005/007/009's own ARCHIVE dispositions are implemented), no importable competing path (satisfied by the same), clearly bounded, gitignored output/log/run directories (partially satisfied today, Section 26.14 extends this), reproducible configuration, no tracked runtime-state remnants in the active path (`memory.json`'s own ARCHIVE disposition, Section 26.6, directly addresses this), and documented validation-artifact boundaries (Section 26.18). No Long-Duration Run is started by this document.

## 24. Cross-Unit Boundary Model

This Architecture touches, without reopening, P2-02A (Position - `runtime.position_state`, `core.position_sizing`), P2-03 (Financial - `runtime.pnl_engine`, `core.equity_stabilizer`), P2-04 (Risk - `runtime.risk`), P3-01/P3-02 (Ordering/Isolation - `core.decision`), and P3-03 (Performance - `runtime.performance_analytics`, `feedback.tracker`, `runtime.strategy_memory`, `execution.adapter`). Every Cross-Unit Disposition in Section 25 cites the certified unit whose own already-established "confirmed inactive" finding it rests on; none amends that unit's own certified contract.

## 25. Per-Component Disposition Register

### 25.1 Active Modules (14) - all RETAIN

| Path | Tracking | Active/Inactive | Import Reachability | Functional Role | Collision | Scientific Relevance | Historical Relevance | Disposition | Required Future Action | AD | Scope Boundary |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `run_engine/main.py` | Tracked | Active | Entry point | Runtime entry | None | Certified entry point | Founding commit | RETAIN | None | RC-AD-002 | In scope |
| `run_engine/core/loop.py` | Tracked | Active | Depth 1 | Orchestrator | None | Certified, P3-01/P3-02 | Founding commit | RETAIN | None | RC-AD-002 | In scope |
| `run_engine/core/state.py` | Tracked | Active | Depth 2 | State Engine | None | Certified | Founding commit | RETAIN | None | RC-AD-002 | In scope |
| `run_engine/core/regime.py` | Tracked | Active | Depth 2 | Regime Classifier | None | Certified | Founding commit | RETAIN | None | RC-AD-002 | In scope |
| `run_engine/core/strategy.py` | Tracked | Active | Depth 2 | Strategy Selector | None | Certified | Founding commit | RETAIN | None | RC-AD-002 | In scope |
| `run_engine/core/position.py` | Tracked | Active | Depth 2 | Position Engine | None | Certified, P2-02A | Founding commit | RETAIN | None | RC-AD-002 | In scope |
| `run_engine/core/risk.py` | Tracked | Active | Depth 2 | Risk Engine | None | Certified, P2-04 | Founding commit | RETAIN | None | RC-AD-002 | In scope |
| `run_engine/core/execution/__init__.py` | Tracked | Active | Depth 2 | Execution package | None | Certified | Founding commit | RETAIN | None | RC-AD-002 | In scope |
| `run_engine/core/execution/executor.py` | Tracked | Active | Depth 3 | Executor | Namespace-adjacent to inactive top-level file | Certified, P3-01/P3-02/P3-03 | Founding commit | RETAIN, confirmed normative path | None | RC-AD-004 | In scope |
| `run_engine/core/performance.py` | Tracked | Active | Depth 2 | Performance Engine | None | Certified, P3-03 | Founding commit, P3-03 Implementation | RETAIN | None | RC-AD-002 | In scope |
| `run_engine/core/pnl.py` | Tracked | Active | Depth 2 | PnL Engine | None | Certified, P2-03 | Founding commit | RETAIN | None | RC-AD-002 | In scope |
| `run_engine/core/trade_lifecycle.py` | Tracked | Active | Depth 2 | Trade Lifecycle Engine | None | Certified | Founding commit | RETAIN | None | RC-AD-002 | In scope |
| `run_engine/core/canonical_state.py` | Tracked | Active | Depth 2 | Canonical State | None | Certified | Founding commit | RETAIN | None | RC-AD-002 | In scope |
| `run_engine/core/canonical_enforcer.py` | Tracked | Active | Depth 2 | Canonical Enforcer | None | Certified | Founding commit | RETAIN | None | RC-AD-002 | In scope |

### 25.2 Inactive Modules (23)

| Path | Tracking | Import Reachability | Functional Role | Collision/Duplicate Authority | Scientific Relevance | Historical Relevance | Disposition | Required Future Action | AD | Scope Boundary |
|---|---|---|---|---|---|---|---|---|---|---|
| `run_engine/core/config.py` | Tracked | Unreached, empty | Reserved (ADR-012 Deferred Scope) | None | None (empty) | Founding-commit stub | RETAIN | None; remains reserved | RC-AD-005 | In scope |
| `run_engine/runtime/recovery.py` | Tracked | Unreached, empty | Reserved (ADR-012 Deferred Scope) | None | None (empty) | Founding-commit stub | RETAIN | None; remains reserved | RC-AD-005 | In scope |
| `run_engine/runtime/snapshot.py` | Tracked | Unreached, empty | Reserved (ADR-012 Deferred Scope) | None | None (empty) | Founding-commit stub | RETAIN | None; remains reserved | RC-AD-005 | In scope |
| `run_engine/runtime/state_memory.py` | Tracked | Unreached | Reserved (ADR-012 Deferred Scope), sole file-I/O-performing inactive module | None (no active persistence exists) | Deferred future candidate | Founding commit, companion to `memory.json` | RETAIN | Architecture Evolution Review required before any activation (ADR-012) | RC-AD-005 | In scope |
| `run_engine/execution/executor.py` (top-level) | Tracked | Unreached, empty | None; collides with active `core/execution/executor.py` | Namespace collision (Section 11) | None (empty) | Founding-commit evidence of the collision itself | ARCHIVE | Preserve as collision evidence outside active namespace | RC-AD-004 | In scope |
| `run_engine/runtime/performance_analytics.py` | Tracked | Unreached | (regime, action)-keyed performance tracker | Duplicate Authority vs. certified `core.performance` (P3-03) | Superseded by TD-004 closure | Pre-P3-03 methodology evidence | ARCHIVE | None beyond archiving | RC-AD-007 | In scope |
| `run_engine/runtime/pnl_engine.py` | Tracked | Unreached | Price-change-proxy reward | Duplicate class name vs. certified `core.pnl` (P2-03) | None established | Pre-consolidation reward-proxy evidence | ARCHIVE | None beyond archiving | RC-AD-007 | In scope |
| `run_engine/runtime/position_state.py` | Tracked | Unreached | Position + embedded reward | Duplicate Authority vs. certified `core.position` (P2-02A) | None established | Pre-consolidation evidence | ARCHIVE | None beyond archiving | RC-AD-007 | In scope |
| `run_engine/runtime/risk.py` | Tracked | Unreached | Absolute-scale risk/exposure layer | Duplicate Authority vs. certified `core.risk` (P2-04) | None established, already flagged by P2-04 | Pre-consolidation evidence | ARCHIVE | None beyond archiving | RC-AD-007 | In scope |
| `run_engine/runtime/strategy_selector.py` | Tracked | Unreached | Bias-mutation "missing link" | Duplicate class name vs. certified `core.strategy.StrategySelector` | Unconfirmed, self-annotated incomplete | Pre-consolidation evidence | ARCHIVE | None beyond archiving | RC-AD-007 | In scope |
| `run_engine/runtime/regime_execution_gate.py` | Tracked | Unreached | Regime-conditioned size gate | Matched-but-unwired with `position_sizing`; double-application risk if composed | Unconfirmed | Exploratory evidence | ARCHIVE | None beyond archiving | RC-AD-008 | In scope |
| `run_engine/core/position_sizing.py` | Tracked | Unreached | Regime-conditioned position sizing | Matched-but-unwired with `regime_execution_gate`; no active sizing Authority exists | Possibly unique Capability, unconfirmed | Exploratory evidence | ARCHIVE | Future Specification may reconsider INTEGRATE | RC-AD-008 | In scope |
| `run_engine/runtime/regime_stability.py` | Tracked | Unreached | Dominance-ratio regime smoothing | Wrapper-shaped, unwired; alternative to certified `core.regime` smoothing | None established | Exploratory evidence | ARCHIVE | None beyond archiving | RC-AD-009 | In scope |
| `run_engine/core/decision.py` | Tracked | Unreached | Parity-rule decision | Output-shape-compatible, not logic-compatible, with certified `core.strategy.decide` | None established | Possible early-stage evidence (unconfirmable) | ARCHIVE | None beyond archiving | RC-AD-009 | In scope |
| `run_engine/core/equity_stabilizer.py` | Tracked | Unreached | Alternative equity smoothing | Cross-Unit, P2-03; pre-flagged "deferred to Phase 6" by P2-02A | None established | Pre-consolidation evidence | ARCHIVE | None beyond archiving | RC-AD-009 | In scope |
| `run_engine/core/state_modulation.py` | Tracked | Unreached | Random-based state modulation | Uses `random.random()`; incompatible with AI-005 | Non-determinism risk, not a Capability gap | Exploratory evidence | ARCHIVE | None; integration categorically excluded | RC-AD-010 | In scope |
| `run_engine/execution/adapter.py` | Tracked | Unreached | Execution adapter (role unconfirmed) | Cross-Unit, P3-03 confirmed-inactive | None established | Exploratory evidence | ARCHIVE | None beyond archiving | RC-AD-009 | In scope |
| `run_engine/execution/safety.py` | Tracked | Unreached | Safety layer (role unconfirmed) | None | None established | Exploratory evidence | ARCHIVE | None beyond archiving | RC-AD-009 | In scope |
| `run_engine/feedback/tracker.py` | Tracked | Unreached | Feedback tracker | Cross-Unit, P3-03, RR-001-adjacent | Potential feedback mechanism, unwired | Exploratory evidence | ARCHIVE | None beyond archiving | RC-AD-009 | In scope |
| `run_engine/logging/logger.py` | Tracked | Unreached | Logging utility | None; no competing Authority | None established | Exploratory evidence | ARCHIVE | None beyond archiving | RC-AD-009 | In scope |
| `run_engine/runtime/strategy_memory.py` | Tracked | Unreached | Strategy memory (role unconfirmed) | Cross-Unit, P3-03 confirmed-inactive | None established | Exploratory evidence | ARCHIVE | None beyond archiving | RC-AD-009 | In scope |
| `run_engine/runtime/strategy_weights.py` | Tracked | Unreached | Strategy weight evolution | Feedback-cycle-adjacent, unwired | None established | Exploratory evidence | ARCHIVE | None beyond archiving | RC-AD-009 | In scope |
| `run_engine/core/features.py` | Tracked | Unreached | Feature computation (return/volatility/momentum/range) | Matched-but-unwired with `engine.regime_classifier`; no active counterpart | Possibly unique Capability, unconfirmed | Exploratory evidence | ARCHIVE | Future Specification may reconsider INTEGRATE | RC-AD-008 | In scope |

### 25.3 Other Artifacts

| Path | Tracking | Status | Disposition | Required Future Action | AD | Scope Boundary |
|---|---|---|---|---|---|---|
| `engine/regime_classifier.py` | Untracked, zero git history | Structurally analogous to `core.regime`, matched-shape with `core.features`, no import edge either direction | IGNORE | Excluded from the normative `engine/` namespace (mechanism not decided here) | RC-AD-011 | In scope |
| `run_engine/runtime/memory.json` | Tracked, single-commit history (`bcac70e`) | Schema-exact companion to `state_memory.py`; stale runtime-state snapshot | ARCHIVE | Preserve as historical evidence outside the active-adjacent namespace | RC-AD-006 | In scope |

### 25.4 Untracked Root-Level Directories (12)

| Path | Category | File Count | Disposition | Required Future Action | AD | Scope Boundary |
|---|---|---|---|---|---|---|
| `_chat_handover/` | Scratch/Review (FRA-scoped) | 21 | IGNORE | `.gitignore` extension recommended | RC-AD-012 | In scope |
| `claude_final_p1031_review/` | Scratch/Review (FRA-scoped) | 8 | IGNORE | `.gitignore` extension recommended | RC-AD-012 | In scope |
| `claude_p1031_patch/` | Scratch/Review (FRA-scoped) | 6 | IGNORE | `.gitignore` extension recommended | RC-AD-012 | In scope |
| `claude_p1_03b_review/` | Scratch/Review (FRA-scoped) | 21 | IGNORE | `.gitignore` extension recommended | RC-AD-012 | In scope |
| `codex_p1_03_review/` | Scratch/Review (FRA-scoped) | 24 | IGNORE | `.gitignore` extension recommended | RC-AD-012 | In scope |
| `review_packages/` | Scratch/Review (FRA-scoped) | 1 | IGNORE | `.gitignore` extension recommended | RC-AD-012 | In scope |
| `_sgf017_context/` | Context bundle, unrelated governance thread (CGA-scoped) | 44 | IGNORE | `.gitignore` extension recommended | RC-AD-013 | In scope |
| `_ssi_context/` | Context bundle, external tool tree (CGA-scoped) | 271 | IGNORE | `.gitignore` extension recommended | RC-AD-013 | In scope |
| `backups/` | Ad hoc dated debugging backups (CGA-scoped) | 39 | IGNORE | `.gitignore` extension recommended | RC-AD-013 | In scope |
| `live_logs/` | Generated Artifact (CGA-scoped) | 92 | IGNORE | `.gitignore` gap closure recommended | RC-AD-013 | In scope |
| `outputs/` | Generated Artifact, review outputs (CGA-scoped) | 456 | IGNORE | `.gitignore` extension recommended | RC-AD-013 | In scope |
| `runtime_runs/` | Generated Artifact, run snapshots (CGA-scoped) | 26 | IGNORE | `.gitignore` extension recommended | RC-AD-013 | In scope |

## 26. Architecture Decisions

**RC-AD-001. Normative Repository Boundary.**
Titel: Normative Repository Boundary Definition. Motivation: RC-CAP-011 (MISSING) requires a definitive statement of what the Normative Repository consists of. Decision: the Normative Repository, for Repository Consolidation, is `run_engine/` in full, the three tracked `engine/` members plus the one untracked `engine/regime_classifier.py`, the twelve untracked directories, and the relevant `docs/architecture/` locations; all other top-level paths (`archive/`, top-level `main`, `config/`, `configs/`, `data/`, `live_l1/`, `reports/`, `scripts/`, `seeds/`, `strategies/`, `tools/`) are explicitly out of this document's own boundary decision. Scientific Justification: bounding the decision to FRA/SDA/CGA-evidenced components avoids inventing new Functional Requirements. Repository Consequences: no immediate change; establishes the frame for every other RC-AD. Runtime Consequences: none. Governance Consequences: future Repository Consolidation work outside `run_engine/`/`engine/` requires its own FRA. Documentation Consequences: this boundary is binding for the Specification stage. Version-Control Consequences: none now. Historical-Provenance Consequences: none affected. Compatibility Constraints: none violated. Validation Consequences: none now. Acceptance Criteria: every component this document disposes of falls within the stated boundary. Traceability: RC-FR-004, RC-FR-011; RC-DEP-032; RC-CAP-011. Scope Boundary: architecture decision only, no repository change.

**RC-AD-002. Active Runtime Boundary.**
Titel: Active Runtime Boundary as Import Closure from `run_engine.main`. Motivation: RC-CAP-001 (COMPLETE) must be converted into a binding boundary rule, not left as analysis alone. Decision: `run_engine.main` is the sole Runtime Entry Point; the Active Runtime Boundary is exactly the AST-based import closure from it, currently fourteen modules (Section 5, Section 10), including the six direct collaborators individually covered by RC-DEP-020 (`state.py`), RC-DEP-021 (`regime.py`), RC-DEP-022 (`strategy.py`), RC-DEP-023 (`position.py`), RC-DEP-024 (`risk.py`), and RC-DEP-025 (`trade_lifecycle.py`). Scientific Justification: reproduced identically four times across FRA, SDA, CGA, and this Architecture. Repository Consequences: all fourteen active modules RETAIN unconditionally (Section 25.1). Runtime Consequences: none; this restates already-certified behavior. Governance Consequences: any future module crossing this boundary requires its own Specification and Implementation. Documentation Consequences: this boundary is the reference definition for all subsequent Sections. Version-Control Consequences: none now. Historical-Provenance Consequences: none affected. Compatibility Constraints: consistent with every certified P2-0x/P3-0x boundary statement. Validation Consequences: the boundary is independently re-verifiable (RC-AI-012). Acceptance Criteria: import closure from `run_engine.main` yields exactly the fourteen-module set. Traceability: RC-FR-001, RC-FR-002; RC-DEP-001, RC-DEP-020 through RC-DEP-025; RC-CAP-001. Scope Boundary: architecture decision only.

**RC-AD-003. Repository Namespace Uniqueness Rule.**
Titel: Binding Namespace Uniqueness Rule. Motivation: RC-CAP-011's own path-collision finding requires a durable rule, not only a one-time fix. Decision: no two files under `run_engine/` may share an identical basename under an identically-named immediate parent directory at different tree depths, going forward. Scientific Justification: this rule, applied retroactively, is exactly what identifies the one existing collision (Section 11). Repository Consequences: governs future additions; does not itself rename or move any current file. Runtime Consequences: none. Governance Consequences: binding on future Specification/Implementation stages. Documentation Consequences: recorded here as the reference rule. Version-Control Consequences: none now. Historical-Provenance Consequences: none. Compatibility Constraints: none violated. Validation Consequences: mechanically checkable by path-pattern scan. Acceptance Criteria: zero collisions after RC-AD-004 is implemented. Traceability: RC-FR-004; RC-DEP-001; RC-CAP-011. Scope Boundary: architecture decision only.

**RC-AD-004. Path Collision Resolution.**
Titel: `execution/executor.py` Path Collision Resolution. Motivation: two files share the basename `executor.py` under two `execution/` directories at different depths (Section 11). Decision: `run_engine/core/execution/executor.py` is the normative, sole Executor path (active, P3-01/P3-02/P3-03-certified); `run_engine/execution/executor.py` (top-level, empty, inactive) receives ARCHIVE, not REMOVE, preserving it as the direct evidence this exact collision existed. Scientific Justification: an empty file has no content-level historical value, but its own existence as founding-commit evidence of the collision does; REMOVE Criterion "no necessary historical provenance" (Section 17) fails for this specific reason. Repository Consequences: frees the top-level `execution/executor.py` path from active-namespace ambiguity once implemented. Runtime Consequences: none; the file is already unreached. Governance Consequences: closes Architecture Question 4. Documentation Consequences: Section 25.1/25.2 register both paths explicitly. Version-Control Consequences: git history preserved via ARCHIVE, not REMOVE. Historical-Provenance Consequences: preserved. Compatibility Constraints: none violated. Validation Consequences: post-Implementation, import closure must show zero `run_engine.execution.executor` (top-level) references. Acceptance Criteria: exactly one `executor.py` remains importable. Traceability: RC-FR-004; RC-DEP-001; RC-CAP-011. Scope Boundary: architecture decision only; no file moved now.

**RC-AD-005. ADR-012-Deferred-Scope Inactive Module Disposition.**
Titel: Disposition of Persistence/Recovery/Config/State-Memory Modules. Motivation: `core/config.py`, `runtime/recovery.py`, `runtime/snapshot.py`, `runtime/state_memory.py` are each tied to ADR-012's own explicit Deferred (not rejected) Scope. Decision: all four RETAIN at their current inactive paths, explicitly protected against implicit reactivation (RC-AI-001), pending a future, dedicated Architecture Evolution Review per ADR-012's own terms. Scientific Justification: REMOVE Criterion "no normative governance dependency" (Section 17) fails for all four, since ADR-012 is itself such a dependency; ARCHIVE would misrepresent Deferred Scope as historical/superseded, which it is not. Repository Consequences: none now; these four remain exactly as they are. Runtime Consequences: none; this Constraint explicitly forbids designing persistence/recovery architecture now (Section 28). Governance Consequences: closes Architecture Question 3 for these four files specifically. Documentation Consequences: Section 25.2 records the ADR-012 tie individually for each. Version-Control Consequences: none. Historical-Provenance Consequences: preserved by construction (RETAIN). Compatibility Constraints: ADR-012 itself. Validation Consequences: none now. Acceptance Criteria: none of the four is imported by the active path after this Architecture. Traceability: RC-FR-006, RC-FR-008; RC-DEP-012, RC-DEP-013; RC-CAP-003, RC-CAP-010. Scope Boundary: architecture decision only; no persistence design performed.

**RC-AD-006. `memory.json` Disposition.**
Titel: Disposition of the Tracked `runtime/memory.json` Artifact. Motivation: Architecture Question 8 requires a distinct decision for the data artifact, separate from the code module `state_memory.py`. Decision: `run_engine/runtime/memory.json` receives ARCHIVE, deliberately asymmetric to `state_memory.py`'s own RETAIN (RC-AD-005). Scientific Justification: the code module is a legitimate Deferred-Scope placeholder; the data file is a stale runtime-state snapshot (`tick: 16`, 500-entry-bounded histories, SDA Finding RCD-002) with no ongoing normative function today, and its continued presence at an active-adjacent path creates the stale-resume risk the SDA already flagged (RC-SDA Risk RCR-001). Archiving neutralizes that risk while preserving the artifact as historical evidence, without prejudging whether `state_memory.py` is ever activated. Repository Consequences: none now; ARCHIVE is decided, not executed. Runtime Consequences: none; the file is not read by the active path today. Governance Consequences: closes Architecture Question 8 without deciding any future persistence architecture. Documentation Consequences: Section 25.3 records this explicitly. Version-Control Consequences: git history preserved via ARCHIVE. Historical-Provenance Consequences: preserved. Compatibility Constraints: ADR-012 (no persistence mechanism may be introduced without a dedicated review; this decision removes a stale artifact, it does not introduce one). Validation Consequences: post-Implementation, `state_memory.py`, if ever activated, must not silently resume from this specific historical snapshot. Acceptance Criteria: the file is no longer present at its current active-adjacent path after Implementation. Traceability: RC-FR-008; RC-DEP-013, RC-DEP-031; RC-CAP-010, RC-CAP-013. Scope Boundary: architecture decision only; no persistence architecture decided.

**RC-AD-007. Duplicate/Competing Computational Authority Disposition.**
Titel: Disposition of Modules Competing with a Certified Authority. Motivation: `runtime/performance_analytics.py`, `runtime/pnl_engine.py`, `runtime/position_state.py`, `runtime/risk.py`, `runtime/strategy_selector.py` each carry logic structurally analogous to an already-certified active module, without holding Authority (Section 13). Decision: all five receive ARCHIVE. Scientific Justification: RC-AI-002 (No Duplicate Active Computational Authority) requires their removal from the active-adjacent namespace; none satisfies Integration Criteria (Section 18) absent a dedicated future Specification; REMOVE fails the historical-provenance criterion for each (each documents a distinct, non-certified prior approach to an already-certified domain). Repository Consequences: none now. Runtime Consequences: none; none is currently reachable. Governance Consequences: directly closes the "keine parallele Computational Authority" objective (Section 8). Documentation Consequences: Section 25.2 records each individually. Version-Control Consequences: git history preserved via ARCHIVE. Historical-Provenance Consequences: preserved. Compatibility Constraints: P2-02A, P2-03, P2-04, P3-03 certified contracts, none reopened. Validation Consequences: post-Implementation, none of the five is importable from the active path. Acceptance Criteria: zero duplicate-named active-adjacent classes remain reachable. Traceability: RC-FR-004, RC-FR-005; RC-DEP-010, RC-DEP-011, RC-DEP-015, RC-DEP-026, RC-DEP-027; RC-CAP-002, RC-CAP-008. Scope Boundary: architecture decision only.

**RC-AD-008. Matched-but-Unwired Component Disposition.**
Titel: Disposition of Matched-but-Unwired Pairs. Motivation: Architecture Question 6 requires clarifying `core.features`/`engine.regime_classifier`, `core.position_sizing`/`runtime.regime_execution_gate`. Decision: `runtime/regime_execution_gate.py` and `core/position_sizing.py` both receive ARCHIVE, classified as an incomplete/experimental pairing whose own composition would double-apply regime scaling (SDA Risk RCR-003), scientifically incompatible with the certified architecture as-is; `core/features.py` receives ARCHIVE, `engine/regime_classifier.py` receives IGNORE (Section 26.11), neither classified as historical evolution with confidence (SDA Section 10.7's own weak, name-suffix-only evidence, not strengthened here). Scientific Justification: none of the four satisfies Integration Criteria (Section 18) without a dedicated future Specification; `core/features.py` and `core/position_sizing.py` are flagged as the most plausible future INTEGRATE candidates precisely because neither collides with a certified Authority, but that determination is explicitly deferred. Repository Consequences: none now. Runtime Consequences: none. Governance Consequences: closes Architecture Question 6. Documentation Consequences: Section 25.2/25.3 record each individually. Version-Control Consequences: `core/features.py` and `core/position_sizing.py` preserved via ARCHIVE (git-tracked); `engine/regime_classifier.py` remains untracked (IGNORE). Historical-Provenance Consequences: preserved for the two tracked files; not applicable to the untracked one (no history exists). Compatibility Constraints: none violated. Validation Consequences: none now. Acceptance Criteria: none of the four is importable from the active path, and no composition of the sizing/gate pair occurs, after Implementation. Traceability: RC-FR-004, RC-FR-009; RC-DEP-016, RC-DEP-017, RC-DEP-018, RC-DEP-019; RC-CAP-005, RC-CAP-011. Scope Boundary: architecture decision only; no future INTEGRATE decided.

**RC-AD-009. Remaining Unwired/Experimental Inactive Module Disposition.**
Titel: Disposition of the Remaining Inactive Modules Without a Certified Competing Authority. Motivation: `runtime/regime_stability.py`, `core/decision.py`, `core/equity_stabilizer.py`, `execution/adapter.py`, `execution/safety.py`, `feedback/tracker.py`, `logging/logger.py`, `runtime/strategy_memory.py`, `runtime/strategy_weights.py` each lack both a certified active counterpart to compete with and an ADR-012 Deferred-Scope tie. Decision: all nine receive ARCHIVE, applying the same uniform rule as RC-AD-007 for consistency, individually justified per Section 25.2's own row-level evidence rather than as an undifferentiated batch. Scientific Justification: none establishes an independently confirmed, urgent scientific need (REMOVE's "no unique Capability" criterion is not conclusively satisfied for any of them either, so REMOVE is not issued); each retains historical/exploratory evidentiary value. Repository Consequences: none now. Runtime Consequences: none; none is currently reachable. Governance Consequences: applies the uniform Inactive Module Disposition Rule consistently across all components lacking a special (ADR-012 or matched-pair) status. Documentation Consequences: Section 25.2 records each individually, with its own Functional Role and evidence. Version-Control Consequences: git history preserved via ARCHIVE for all nine. Historical-Provenance Consequences: preserved. Compatibility Constraints: P3-03 (three of the nine are P3-03 Cross-Unit-cited, none reopened). Validation Consequences: none of the nine importable from the active path after Implementation. Acceptance Criteria: as above. Traceability: RC-FR-003, RC-FR-006, RC-FR-012; RC-DEP-001, RC-DEP-028, RC-DEP-029, RC-DEP-030; RC-CAP-003, RC-CAP-012. Scope Boundary: architecture decision only.

**RC-AD-010. Determinism-Risk Component Disposition.**
Titel: Disposition of `state_modulation.py`. Motivation: Architecture Question 9 requires a specific decision given the module's own `random.random()` usage (RC-DEP-012). Decision: `run_engine/core/state_modulation.py` receives ARCHIVE; integration into the active path is categorically excluded, now and by this Architecture's own binding rule (RC-AI-002, extended to non-determinism), regardless of any future disposition review. Scientific Justification: `random.random()` is structurally, permanently incompatible with AI-005's determinism guarantee as currently implemented; any future deterministic redesign would be a new component, not a reactivation of this one; REMOVE is not issued because the module retains exploratory/historical value and full git history exists, satisfying preservation over deletion. Repository Consequences: none now. Runtime Consequences: none; already unreached, and this decision makes that permanent absent a full redesign. Governance Consequences: directly satisfies "keine zufallsbasierte Komponente in den aktiven Pfad integrieren" (Section 8's own Constraint). Documentation Consequences: Section 25.2 records this explicitly, cross-referenced to AI-005. Version-Control Consequences: git history preserved via ARCHIVE. Historical-Provenance Consequences: preserved. Compatibility Constraints: AI-005 (Baseline), not reopened. Validation Consequences: post-Implementation, no active-path import of this module, verified by the same import-closure method. Acceptance Criteria: `random.random()` (or any non-seeded randomness) does not appear anywhere in the active fourteen-module closure. Traceability: RC-FR-007; RC-DEP-012; RC-CAP-012. Scope Boundary: architecture decision only.

**RC-AD-011. `engine/regime_classifier.py` Disposition.**
Titel: Disposition of the Untracked External Alternative. Motivation: Architecture Question 5 and the FRA's own Verification Gap RC-VG-002 require a decision despite unconfirmable origin. Decision: `engine/regime_classifier.py` receives IGNORE, the disposition explicitly defined for external, generated, or local work artifacts not intended to be part of the Normative Repository structure. Scientific Justification: it is untracked with zero git history (unlike every other component this document disposes of), sits inside an otherwise fully-tracked, active, unrelated `engine/` package, and its own origin/purpose is unconfirmable from repository evidence (RC-VG-002, not reopened); IGNORE, not ARCHIVE, since ARCHIVE presupposes tracked (or to-be-tracked) status this document does not decide to grant. Repository Consequences: none now; a future `.gitignore` extension or relocation is Implementation Impact only (Section 34), not decided here. Runtime Consequences: none; not imported by `run_engine/` or `engine/`'s own tracked members. Governance Consequences: closes Architecture Question 5 for this specific component. Documentation Consequences: Section 25.3 records this explicitly. Version-Control Consequences: remains untracked. Historical-Provenance Consequences: not applicable (no history exists to preserve or lose). Compatibility Constraints: none violated. Validation Consequences: none now. Acceptance Criteria: the file remains outside the Normative Repository's own tracked, active surface. Traceability: RC-FR-009, RC-FR-010; RC-DEP-016, RC-DEP-017; RC-CAP-006. Scope Boundary: architecture decision only; no relocation performed.

**RC-AD-012. Scratch/Review Directory Disposition (FRA-Scoped).**
Titel: Disposition of the Six FRA-Scoped Review/Handover Directories. Motivation: Architecture Question 10 requires an individual-or-grouped decision for `_chat_handover/`, `claude_final_p1031_review/`, `claude_p1031_patch/`, `claude_p1_03b_review/`, `codex_p1_03_review/`, `review_packages/`. Decision: all six receive IGNORE, grouped by shared, sufficient, common evidence (each holds working-copy content whose own authoritative version already exists tracked elsewhere in `docs/architecture/` or `run_engine/`), not as an undifferentiated inactivity-based decision. Scientific Justification: ARCHIVE is not issued because these are not the Normative Repository's own historical record - they are personal/session working copies of already-preserved content; retaining duplicates risks exactly the divergent-document-version problem Architecture Question 12 warns against. Repository Consequences: none now; `.gitignore` extension is recommended (Section 26.14) but not performed. Runtime Consequences: none; none contains anything importable by `run_engine/`. Governance Consequences: closes Architecture Question 10 and directly serves Architecture Question 12 (Scientific Documentation Boundary). Documentation Consequences: this decision itself establishes that these six locations are non-normative. Version-Control Consequences: remain untracked; recommended for explicit `.gitignore` exclusion. Historical-Provenance Consequences: not affected, since the authoritative record already exists elsewhere. Compatibility Constraints: none violated. Validation Consequences: none now. Acceptance Criteria: no governance document is ever sourced from these six locations in preference to its own tracked, authoritative counterpart. Traceability: RC-FR-011; RC-DEP-032; RC-CAP-007. Scope Boundary: architecture decision only; no `.gitignore` edit performed.

**RC-AD-013. Context/Backup/Output/Run Directory Disposition (CGA-Scoped).**
Titel: Disposition of the Six CGA-Identified Directories. Motivation: Architecture Question 11 requires a decision for `_sgf017_context/`, `_ssi_context/`, `backups/`, `live_logs/`, `outputs/`, `runtime_runs/` (CGA Finding RCG-001). Decision: all six receive IGNORE. Scientific Justification: `_sgf017_context/` and `_ssi_context/` are context bundles for unrelated governance/tooling threads (confirmed zero `run_engine` coupling, CGA Section 6); `backups/` holds ad hoc, self-evidently dated personal debugging snapshots; `live_logs/`, `outputs/`, `runtime_runs/` are Generated Artifacts per Section 6's own definition, produced by execution rather than authored, and belong outside the Normative Source Tree (RC-AI-011). None qualifies for ARCHIVE, since none is part of the Repository Consolidation scientific narrative this governance chain is building; none qualifies for REMOVE, since this document does not verify their content is safe to delete and REMOVE is reserved for Normative Repository components with confirmed no-provenance-value (Section 17), which these were never part of. Repository Consequences: none now; `.gitignore` extension/gap-closure recommended (Section 26.14). Runtime Consequences: none. Governance Consequences: closes Architecture Question 11 and CGA Recommendation 1 (supplementary classification), to the extent this Architecture is chartered to close it - the underlying content-level classification (what SDM/SSI-context actually is) remains outside this document's own scope (Section 3). Documentation Consequences: this decision marks all six as non-normative. Version-Control Consequences: remain untracked; `.gitignore` extension recommended. Historical-Provenance Consequences: not applicable; none held unique scientific evidence per Section 25.4. Compatibility Constraints: none violated. Validation Consequences: none now. Acceptance Criteria: none of the six is referenced as a normative source by any future governance document. Traceability: RC-FR-011; RC-DEP-032; RC-CAP-007, RC-CAP-011. Scope Boundary: architecture decision only; no deletion, no `.gitignore` edit performed.

**RC-AD-014. Gitignore Architecture.**
Titel: Target `.gitignore` Categories. Motivation: Architecture Question 14 requires binding target categories. Decision: eight target categories are defined for future Implementation: Logs (`live_logs/` in full, closing the existing partial coverage), Outputs (`outputs/`), Runtime Runs (`runtime_runs/`), Backups (`backups/`), Scratch Workspaces (`_chat_handover/`, `claude_p1031_patch/`), Review Packages (`claude_final_p1031_review/`, `claude_p1_03b_review/`, `codex_p1_03_review/`, `review_packages/`), Local Context Bundles (`_sgf017_context/`, `_ssi_context/`), Generated State (a category reserved for any future `memory.json`-equivalent artifact, not populated now). No Cache Files category is added beyond the existing `__pycache__/`/`*.pyc` rules, already present and sufficient. Scientific Justification: directly operationalizes the twelve IGNORE dispositions of Sections 26.12-26.13 without yet editing the file. Repository Consequences: none now; a future Implementation step would add these patterns. Runtime Consequences: none. Governance Consequences: gives the Specification stage a concrete, bounded editing target. Documentation Consequences: this Section is the binding reference. Version-Control Consequences: none until implemented. Historical-Provenance Consequences: none. Compatibility Constraints: must not exclude any currently-tracked file (verified: none of the twelve directories, nor any pattern above, currently matches a tracked path). Validation Consequences: `git status --short` should show none of the twelve directories after implementation. Acceptance Criteria: eight categories defined, zero tracked files affected. Traceability: RC-FR-011; RC-DEP-032; RC-CAP-007. Scope Boundary: architecture decision only; no `.gitignore` file edited.

**RC-AD-015. Archive Namespace Architecture.**
Titel: Archive Namespace Convention. Motivation: Architecture Question 15 requires a namespace convention for any future ARCHIVE-disposed file, given nineteen inactive modules plus `memory.json` and the collision file now carry that disposition. Decision: the repository's own pre-existing top-level `archive/` convention (Section 5's own newly-confirmed evidence: `archive/HISTORICAL_K3_K10_2026-01-06/...`, 80 tracked files, dated-label subdirectory pattern) is adopted as precedent; a future Repository-Consolidation-specific archive location would follow the identical `archive/<LABEL>_<date>/` pattern, under a label clearly distinct from `run_engine` or `engine` (avoiding any possibility of the archived namespace resembling an importable package). No file is moved and no directory is created by this document. Scientific Justification: reusing an established convention avoids introducing a second, competing archival pattern; the requirement that the archive namespace never be importable by the active runtime is satisfied by construction, since `archive/` is not, and has never been, on `run_engine.main`'s own import closure. Repository Consequences: none now. Runtime Consequences: none; `archive/` is confirmed unreachable from `run_engine.main`. Governance Consequences: closes Architecture Question 15. Documentation Consequences: this Section is the binding convention reference for the Specification stage. Version-Control Consequences: none now. Historical-Provenance Consequences: the convention itself is designed to preserve git history (RC-AI-008). Compatibility Constraints: must not collide with `archive/HISTORICAL_K3_K10_2026-01-06/`'s own existing label. Validation Consequences: a future archived path must not appear in any import-closure result. Acceptance Criteria: a documented, unambiguous archive label reserved in a future Specification. Traceability: RC-FR-004, RC-FR-006; RC-DEP-012, RC-DEP-013; RC-CAP-010. Scope Boundary: architecture decision only; no directory created.

**RC-AD-016. Remove Criteria Application.**
Titel: Formal Application of Remove Criteria. Motivation: Architecture Question 16 requires the criteria to be explicitly stated and applied, not merely referenced. Decision: the eight-part joint criteria (Section 17) are formally adopted as binding for any future REMOVE decision; applied against all twenty-three inactive modules and `engine/regime_classifier.py`/`memory.json` in this document, none currently satisfies all eight jointly, so zero REMOVE dispositions are issued now. Scientific Justification: satisfies the governing task's own hard quality rules against collective removal based on mere inactivity and against any file receiving REMOVE solely because it is inactive. Repository Consequences: none now. Runtime Consequences: none. Governance Consequences: establishes the criteria for any future Specification-stage REMOVE proposal. Documentation Consequences: Section 17 is the binding reference. Version-Control Consequences: none. Historical-Provenance Consequences: preserved by the absence of any REMOVE. Compatibility Constraints: none violated. Validation Consequences: future REMOVE proposals must show all eight criteria satisfied, individually, per file. Acceptance Criteria: zero REMOVE in this document; the criteria text is unambiguous for future reuse. Traceability: RC-FR-003, RC-FR-006; RC-DEP-001; RC-CAP-003. Scope Boundary: architecture decision only.

**RC-AD-017. Integration Criteria Application.**
Titel: Formal Application of Integration Criteria. Motivation: Architecture Question 17 requires the criteria to be explicitly stated and applied. Decision: the five-part joint criteria (Section 18) are formally adopted as binding for any future INTEGRATE decision; applied against every candidate in this document, none currently satisfies all five jointly absent a dedicated future Specification, so zero INTEGRATE dispositions are issued now; `core/features.py` and `core/position_sizing.py` are named as the most plausible future candidates without being decided. Scientific Justification: satisfies "keine Integration allein aufgrund vorhandenen Codes" as a hard quality rule. Repository Consequences: none now. Runtime Consequences: none. Governance Consequences: establishes the criteria for any future Specification-stage INTEGRATE proposal. Documentation Consequences: Section 18 is the binding reference. Version-Control Consequences: none. Historical-Provenance Consequences: not applicable. Compatibility Constraints: any future INTEGRATE must remain compatible with every certified P2-0x/P3-0x contract, not reopened. Validation Consequences: future INTEGRATE proposals must show all five criteria satisfied. Acceptance Criteria: zero INTEGRATE in this document. Traceability: RC-FR-004, RC-FR-009; RC-DEP-016, RC-DEP-019; RC-CAP-005. Scope Boundary: architecture decision only.

**RC-AD-018. Long-Duration-Validation Repository Readiness Criteria.**
Titel: Repository Preconditions for Smoke Through 30-Day Runs. Motivation: Architecture Question 18 requires binding repository-side (not runtime-side) preconditions. Decision: before any Smoke, 1-hour, 6-hour, 24-hour, 7-day, or 30-day run, the following must hold: exactly one importable active runtime path (RC-AI-001); zero importable competing paths (satisfied once RC-AD-004/007/008/009/010 are implemented); clearly bounded, gitignored output/log/run directories (RC-AD-014); no tracked runtime-state remnant in the active-adjacent namespace (RC-AD-006); reproducible configuration (not decided further here, out of scope); documented validation-artifact boundaries for the run's own outputs. Scientific Justification: directly operationalizes RC-AI-013. Repository Consequences: none now; these are preconditions for a future stage, not actions. Runtime Consequences: none; no Long-Duration Run is started. Governance Consequences: gives the eventual pre-Long-Duration-Validation checklist its own binding repository-side criteria. Documentation Consequences: this Section is the reference. Version-Control Consequences: none now. Historical-Provenance Consequences: none. Compatibility Constraints: none violated. Validation Consequences: each criterion is independently checkable before the first Smoke run. Acceptance Criteria: all five criteria satisfied before any run in the stated sequence begins. Traceability: RC-FR-001, RC-FR-011; RC-DEP-001, RC-DEP-032; RC-CAP-010. Scope Boundary: architecture decision only; no run started.

**RC-AD-019. Technical Debt Repository-Structure Disposition.**
Titel: Repository-Structure Disposition of TD-004, TD-005, TD-007. Motivation: Architecture Question 19 requires a repository-grounded, not functional, decision. Decision: TD-004's Register `Status` field requires updating to reflect the certified P3-03 closure - a documentation-currency action, not new technical work, explicitly not performed by this document (Register not yet changed, Section 29); TD-005 (Automated Regression Test Suite) remains open and is explicitly not silently closed by any disposition in this document; TD-007 remains deferred to a not-yet-existing future Runtime Control Unit, with `state_memory.py`/`memory.json` noted (RC-AD-005/006) as the most plausible eventual point of contact, not acted upon. Scientific Justification: none of the three debt items is repository-structurally resolved by ARCHIVE/RETAIN/IGNORE decisions alone; each requires its own future process. Repository Consequences: none now. Runtime Consequences: none. Governance Consequences: prevents Repository Consolidation from being read as having silently closed any of the three. Documentation Consequences: Section 29 restates this in Technical-Debt-Disposition form. Version-Control Consequences: none; TD Register unchanged. Historical-Provenance Consequences: none. Compatibility Constraints: TD Register's own existing entries, not reopened. Validation Consequences: none now. Acceptance Criteria: TD Register content identical before and after this document. Traceability: RC-FR-008, RC-FR-012; RC-DEP-013, RC-DEP-026, RC-DEP-031; RC-CAP-013. Scope Boundary: architecture decision only; Register not edited.

**RC-AD-020. Formal Unit Identifier Non-Assignment.**
Titel: No New Formal Unit Identifier Assigned. Motivation: Architecture Question 20 explicitly forbids inventing a P4/P5/P6 identifier. Decision: this document uses exclusively "Repository Consolidation" and "RC" throughout; no formal Phase/Unit Identifier is assigned; the identifier gap is documented as a Governance-Metadata question for a future Baseline update, not resolved here. Scientific Justification: assigning an identifier is a Baseline-level governance act outside an Architecture document's own authority. Repository Consequences: none. Runtime Consequences: none. Governance Consequences: leaves the identifier question explicitly open for the Baseline's own future maintainers. Documentation Consequences: consistent naming ("Repository Consolidation," "RC") used throughout this entire document. Version-Control Consequences: none. Historical-Provenance Consequences: none. Compatibility Constraints: none violated. Validation Consequences: none now. Acceptance Criteria: zero P4/P5/P6 (or similar) identifiers appear anywhere in this document. Traceability: RC-FR-012, RC-FR-013; RC-DEP-028, RC-DEP-029; RC-CAP-014. Scope Boundary: architecture decision only; no Baseline edited.

**RC-AD-021. Verification Tooling Requirement.**
Titel: Durable Repository-Verification Tooling Requirement. Motivation: Architecture Question 13 and RC-CAP-004 (PARTIAL, since the import-closure method is proven but not persisted) require a binding requirement, not yet an implementation. Decision: a future Specification must define a durable, repository-resident verification capability, at minimum reproducing the AST-based import-closure check (active/inactive module split, edge enumeration, cycle detection) this governance chain has independently re-derived four times; classified as governance tooling, not production/trading code; its own storage location, exact interface, and invocation are explicitly not decided here. Scientific Justification: directly closes the gap RC-CAP-004 identified (this session's own script defect, self-caught during the CGA, is direct evidence persistence would reduce re-derivation risk). Repository Consequences: none now. Runtime Consequences: none; governance tooling does not touch the active trading path. Governance Consequences: binding requirement for the Specification stage. Documentation Consequences: this Section is the reference requirement. Version-Control Consequences: none now. Historical-Provenance Consequences: none. Compatibility Constraints: must not import from, or be imported by, `run_engine.main`'s own active closure (governance tooling is not runtime code). Validation Consequences: the eventual tool's own output must be independently reproducible (RC-AI-012). Acceptance Criteria: a Specification-stage design exists before Implementation of this requirement. Traceability: RC-FR-001; RC-DEP-001; RC-CAP-004. Scope Boundary: architecture decision only; no script written or committed.

**RC-AD-022. Scientific Documentation Boundary.**
Titel: Normative Governance Document Locations. Motivation: Architecture Question 12 requires deciding which locations are normative for governance documentation. Decision: `docs/architecture/` (Architecture and Baseline documents), `docs/architecture/analysis/` (FRA, SDA, CGA and equivalents), `docs/architecture/certification/` (Final Certifications), and `docs/architecture/technical_debt/` (the TD Register) are the four normative governance-document locations; the twelve untracked directories (RC-AD-012, RC-AD-013) are explicitly non-normative, per the same reasoning already given. Scientific Justification: this matches the four locations already, consistently used throughout the entire P2-02A-through-P3-03 and Repository Consolidation chains, without introducing a fifth. Repository Consequences: none now. Runtime Consequences: none. Governance Consequences: prevents future duplicate or divergent document versions by naming the single authoritative location for each document class. Documentation Consequences: this Section is the binding reference. Version-Control Consequences: none now. Historical-Provenance Consequences: none. Compatibility Constraints: none violated; consistent with existing practice. Validation Consequences: any future governance document must be authored at one of these four locations to be considered normative. Acceptance Criteria: no new fifth location introduced without a future Architecture Decision. Traceability: RC-FR-012, RC-FR-013; RC-DEP-032; RC-CAP-009. Scope Boundary: architecture decision only.

**RC-AD-023. Certified Runtime Behavioral Invariance.**
Titel: This Architecture Changes No Certified Runtime Behavior. Motivation: every prior RC-AD above touches components adjacent to, but never active-path members of, the certified runtime; this decision makes that invariance explicit and binding in its own right, rather than leaving it implicit across twenty-two other decisions. Decision: no Architecture Decision in this document alters, or authorizes altering, any certified Strategy, Position, Financial, Risk, or Performance behavior, any Stage-Ordering, or any Information Flow established by ADR-001 through ADR-012 or by the P2-02A/P2-03/P2-04/P3-01/P3-02/P3-03 Final Certifications. Scientific Justification: every disposed component in Sections 25.1-25.2 is, and remains, outside the fourteen-module Active Runtime Boundary (RC-AD-002); ARCHIVE/RETAIN/IGNORE dispositions affect namespace and version-control status only. Repository Consequences: none beyond those already stated per RC-AD. Runtime Consequences: explicitly none. Governance Consequences: gives the eventual Final Certification a single, citable "no behavioral change" anchor decision. Documentation Consequences: this Section is the reference. Version-Control Consequences: none beyond RC-AD-004 through RC-AD-013. Historical-Provenance Consequences: none. Compatibility Constraints: all of ADR-001 through ADR-012, and all six certified units, jointly. Validation Consequences: a future Implementation must demonstrate functionally identical runtime output before and after, for the certified fourteen-module active path (Python-object/runtime-result comparison, not a file-byte comparison). Acceptance Criteria: zero change to any file in Section 25.1. Traceability: RC-FR-001, RC-FR-002; RC-DEP-001, RC-DEP-020 through RC-DEP-025; RC-CAP-001, RC-CAP-014. Scope Boundary: architecture decision only; governs all Implementation stages that follow.

## 27. Architecture Invariants

**RC-AI-001. Exactly One Active Runtime Path.** The AST-based import closure from `run_engine.main` yields exactly one connected active module set; no second entry point or parallel active path may exist. Traceability: RC-AD-002; RC-CAP-001.

**RC-AI-002. No Duplicate Active Computational Authority.** No two components may hold, or appear to hold, Computational Authority over the same domain within the Active Runtime Boundary. Traceability: RC-AD-007, RC-AD-010; RC-CAP-002, RC-CAP-008.

**RC-AI-003. No Active Namespace Collision.** No two files under `run_engine/` share an identical basename under an identically-named parent at different depths once RC-AD-004 is implemented. Traceability: RC-AD-003, RC-AD-004; RC-CAP-011.

**RC-AI-004. No Import from Archive.** No module within the Active Runtime Boundary may import from the `archive/` namespace (Section 26.15) once it exists. Traceability: RC-AD-015; RC-CAP-010.

**RC-AI-005. No Runtime Import from Scratch or Review Areas.** No module within the Active Runtime Boundary may import from any of the twelve IGNORE-disposed directories (Sections 26.12-26.13). Traceability: RC-AD-012, RC-AD-013; RC-CAP-007.

**RC-AI-006. No Generated Runtime Artifact Tracked Without Explicit Governance.** A Generated Artifact (Section 6) may be tracked only if an explicit Architecture Decision authorizes it; `memory.json` is the one currently-tracked exception, explicitly disposed (RC-AD-006), not silently permitted. Traceability: RC-AD-006, RC-AD-014; RC-CAP-013.

**RC-AI-007. No Ambiguous Active/Inactive Classification.** Every module under `run_engine/` has exactly one classification (active or inactive) per the current import closure, with zero modules left unclassified. Traceability: RC-AD-002; RC-CAP-001.

**RC-AI-008. Historical Provenance Preserved.** Every ARCHIVE disposition preserves git history; no Historical-Provenance-bearing component receives REMOVE. Traceability: RC-AD-004, RC-AD-006, RC-AD-007, RC-AD-009; RC-CAP-006.

**RC-AI-009. Removal Requires Independent Validation.** No future REMOVE disposition may be issued without satisfying all eight Remove Criteria (Section 17), independently verified. Traceability: RC-AD-016; RC-CAP-003.

**RC-AI-010. Integration Requires Certified Architecture Compatibility.** No future INTEGRATE disposition may be issued without satisfying all five Integration Criteria (Section 18), including compatibility with every certified P2-0x/P3-0x contract. Traceability: RC-AD-017; RC-CAP-005.

**RC-AI-011. Generated Outputs Stay Outside Normative Source Tree.** `live_logs/`, `outputs/`, `runtime_runs/`, and any future equivalent, remain outside the Normative Repository's own source-tree portion (`run_engine/`, `engine/`). Traceability: RC-AD-013, RC-AD-014; RC-CAP-012.

**RC-AI-012. Repository Verification Is Reproducible.** The active/inactive import-closure classification must be independently re-derivable by a correctly-implemented AST-based script, yielding the identical result each time (demonstrated four times across FRA, SDA, CGA, and this Architecture). Traceability: RC-AD-021; RC-CAP-004.

**RC-AI-013. Long-Duration Runs Use Defined Artifact Boundaries.** No Smoke, 1-hour, 6-hour, 24-hour, 7-day, or 30-day run may begin without satisfying the five criteria of Section 26.18. Traceability: RC-AD-018; RC-CAP-010.

**RC-AI-014. Governance Documents Have One Normative Location.** Every governance document has exactly one authoritative, tracked location among the four named in Section 26.22; no duplicate at a Scratch/Review location is treated as authoritative. Traceability: RC-AD-012, RC-AD-022; RC-CAP-009.

**RC-AI-015. Certified Runtime Behaviour Remains Unchanged by Consolidation.** No disposition in this document alters certified Strategy, Position, Financial, Risk, Performance, Stage-Ordering, or Information-Flow behavior. Traceability: RC-AD-023; RC-CAP-014.

## 28. Architecture Constraints

- No functional change to the certified runtime; no new trading function.
- No Strategy, Position, Financial, Risk, or Performance change.
- No Stage-Ordering change; no Information-Flow change.
- No persistence or recovery architecture is designed by this document (RC-AD-005, RC-AD-006 dispose of files without designing a persistence mechanism).
- No Operator-Control architecture is designed by this document.
- No Long-Duration Run is executed by this document.
- No integration of uncertified alternative logic (RC-AD-017: zero INTEGRATE issued).
- No deletion without independent evidence (RC-AD-016: zero REMOVE issued).
- No archive structure with an importable runtime namespace (RC-AI-004).
- No implicit P-Identifier assignment (RC-AD-020).

## 29. Technical-Debt Disposition

**TD-004 (Lifecycle-based Performance Evaluation).** Functionally closed by the certified P3-03 Final Certification. Repository-structure disposition: the Register's own `Status` field update is required but explicitly **not performed by this document** (Register not yet changed, per this document's own Vor-Beginn constraints); no renewed technical work is implied or required. `run_engine/runtime/performance_analytics.py`'s own ARCHIVE disposition (RC-AD-007) is the repository-structure-relevant action this Architecture takes in connection with TD-004.

**TD-005 (Automated Regression Test Suite).** Remains open. This document's own dispositions do not silently close TD-005; a project-wide regression test suite remains a distinct, unaddressed need, relevant before or during future Long-Duration Validation (Section 26.18), but not a Repository Consolidation deliverable.

**TD-007 (RunLoop Lifecycle Control Surface).** Remains deferred to a future Runtime Control Unit that does not yet exist under any identifier (consistent with RC-AD-020's own non-assignment). `run_engine/runtime/state_memory.py` (RETAIN, RC-AD-005) and `memory.json` (ARCHIVE, RC-AD-006) are noted as the most plausible eventual point of contact, not acted upon.

No other Technical Debt Register entry is addressed, since none has established repository-structure-relevant evidence within the FRA, SDA, or CGA.

## 30. FRA Traceability

| RC-FR-ID | Resolved By |
|---|---|
| RC-FR-001 | RC-AD-002, RC-AD-018, RC-AD-021 |
| RC-FR-002 | RC-AD-002, RC-AD-023 |
| RC-FR-003 | RC-AD-001, RC-AD-009, RC-AD-016 |
| RC-FR-004 | RC-AD-001, RC-AD-003, RC-AD-004, RC-AD-007, RC-AD-008, RC-AD-015, RC-AD-017 |
| RC-FR-005 | RC-AD-007, RC-AD-017 |
| RC-FR-006 | RC-AD-005, RC-AD-009, RC-AD-015, RC-AD-016 |
| RC-FR-007 | RC-AD-010 |
| RC-FR-008 | RC-AD-005, RC-AD-006, RC-AD-019 |
| RC-FR-009 | RC-AD-008, RC-AD-011, RC-AD-017 |
| RC-FR-010 | RC-AD-011 |
| RC-FR-011 | RC-AD-001, RC-AD-012, RC-AD-013, RC-AD-014, RC-AD-018 |
| RC-FR-012 | RC-AD-019, RC-AD-020, RC-AD-022 |
| RC-FR-013 | RC-AD-019, RC-AD-020, RC-AD-022 |

All thirteen Functional Requirements individually resolved by at least one Architecture Decision.

## 31. SDA Dependency Traceability

| RC-DEP-ID | Resolved By |
|---|---|
| RC-DEP-001 | RC-AD-002, RC-AD-003, RC-AD-016, RC-AD-018, RC-AD-021, RC-AD-023 |
| RC-DEP-010 | RC-AD-007 |
| RC-DEP-011 | RC-AD-007 |
| RC-DEP-012 | RC-AD-005, RC-AD-010, RC-AD-015 |
| RC-DEP-013 | RC-AD-005, RC-AD-006, RC-AD-015, RC-AD-019 |
| RC-DEP-015 | RC-AD-007 |
| RC-DEP-016 | RC-AD-008, RC-AD-011 |
| RC-DEP-017 | RC-AD-008, RC-AD-011 |
| RC-DEP-018 | RC-AD-008, RC-AD-017 |
| RC-DEP-019 | RC-AD-008, RC-AD-017 |
| RC-DEP-020 | RC-AD-002, RC-AD-023 |
| RC-DEP-021 | RC-AD-002, RC-AD-023 |
| RC-DEP-022 | RC-AD-002, RC-AD-023 |
| RC-DEP-023 | RC-AD-002, RC-AD-023 |
| RC-DEP-024 | RC-AD-002, RC-AD-023 |
| RC-DEP-025 | RC-AD-002, RC-AD-023 |
| RC-DEP-026 | RC-AD-007, RC-AD-019 |
| RC-DEP-027 | RC-AD-007 |
| RC-DEP-028 | RC-AD-009 |
| RC-DEP-029 | RC-AD-009 |
| RC-DEP-030 | RC-AD-009 |
| RC-DEP-031 | RC-AD-006, RC-AD-019 |
| RC-DEP-032 | RC-AD-001, RC-AD-012, RC-AD-013, RC-AD-014, RC-AD-018, RC-AD-022 |

All twenty-three actually-used, non-contiguously-numbered Dependency records individually resolved; no RC-DEP-002 through RC-DEP-009 or RC-DEP-014 is referenced anywhere, since none exists.

## 32. CGA Capability Traceability

| RC-CAP-ID | Resolved By |
|---|---|
| RC-CAP-001 | RC-AD-002, RC-AD-023 |
| RC-CAP-002 | RC-AD-007 |
| RC-CAP-003 | RC-AD-009, RC-AD-016 |
| RC-CAP-004 | RC-AD-021 |
| RC-CAP-005 | RC-AD-008, RC-AD-017 |
| RC-CAP-006 | RC-AD-011 |
| RC-CAP-007 | RC-AD-012, RC-AD-013 |
| RC-CAP-008 | RC-AD-002, RC-AD-007 |
| RC-CAP-009 | RC-AD-022 |
| RC-CAP-010 | RC-AD-005, RC-AD-006, RC-AD-015, RC-AD-018 |
| RC-CAP-011 | RC-AD-001, RC-AD-003, RC-AD-004, RC-AD-013 |
| RC-CAP-012 | RC-AD-009, RC-AD-010 |
| RC-CAP-013 | RC-AD-006, RC-AD-019 |
| RC-CAP-014 | RC-AD-020, RC-AD-023 |
| RC-CAP-015 | RC-AD-001 (synthesis, addressed by the aggregate of all twenty-three Architecture Decisions jointly) |

All fifteen Capabilities individually addressed.

## 33. Acceptance Criteria

- Every one of the 14 active modules retains its own current path and behavior, unconditionally (RC-AD-002, RC-AD-023).
- Every one of the 23 inactive modules carries exactly one Disposition, individually justified (Section 25.2): 4 RETAIN, 19 ARCHIVE.
- `engine/regime_classifier.py` carries IGNORE; `memory.json` carries ARCHIVE (Section 25.3).
- All 12 untracked directories carry IGNORE (Section 25.4).
- The `execution/executor.py` collision has exactly one normative resolution (RC-AD-004).
- Zero REMOVE and zero INTEGRATE dispositions appear anywhere in this document.
- All 13 RC-FR-IDs, all 23 RC-DEP-IDs, and all 15 RC-CAP-IDs are individually traced to at least one RC-AD (Sections 30-32).
- TD-004, TD-005, TD-007 are each addressed at the repository-structure level only, with the TD Register left unmodified.
- No runtime file is modified, moved, or deleted by this document.
- No P4/P5/P6 or other new formal Unit Identifier appears anywhere in this document.

## 34. Implementation Impact Inventory (High-Level Only)

- **Files likely RETAIN:** the 14 active modules (Section 25.1); `core/config.py`, `runtime/recovery.py`, `runtime/snapshot.py`, `runtime/state_memory.py` (Section 25.2).
- **Files likely INTEGRATE:** none decided by this document (Section 18).
- **Files likely ARCHIVE:** 20 total - 19 of the 23 inactive modules (Section 25.2, which already includes `run_engine/execution/executor.py` (top-level) as one of the 19, per RC-AD-004's own path-collision resolution, not an additional 20th module) plus `run_engine/runtime/memory.json` (Section 25.3) as the 20th, separately-typed data artifact.
- **Files likely REMOVE:** none decided by this document (Section 17).
- **Directories likely IGNORE:** all 12 untracked root-level directories (Section 25.4); `engine/regime_classifier.py` individually (Section 25.3).
- **Likely `.gitignore` adjustments:** eight target categories (Section 26.14), not yet implemented.
- **Possible archive structure:** a `archive/<LABEL>_<date>/`-pattern location, reusing existing repository convention, not yet created (Section 26.15).
- **Possible verification tooling:** a durable, repository-resident import-closure/governance-verification script, not yet designed in detail (Section 26.21).
- **Technical-Debt-Register update:** TD-004's own `Status` field, not yet performed (Section 29).

Explicitly not determined here: concrete commands, Implementation Units, exact file moves, concrete new file contents, code, or a commit plan.

## 35. Non-Goals

This document does not: design a Specification, Implementation Unit, or Final Certification; move, delete, archive, or integrate any file; change any runtime file; change any untracked directory's own content; create new Functional Requirements, Dependencies, or Capability classifications; assign a P4/P5/P6 or other formal Unit Identifier; decide the normative status of `archive/`, top-level `main`, `config/`, `configs/`, `data/`, `live_l1/`, `reports/`, `scripts/`, `seeds/`, `strategies/`, or `tools/`; design a persistence, recovery, or Operator-Control architecture; execute any Long-Duration Run; modify the Technical Debt Register.

## 36. Internal Consistency Review

**Scientific Consistency Review.** Every Architecture Decision cites specific RC-FR/RC-DEP/RC-CAP evidence and Repository Evidence independently re-verified in Section 5; no Decision is asserted without a traceable source. PASS.

**Architecture Consistency Review.** No two Architecture Decisions assign conflicting Dispositions to the same component (cross-checked against Section 25's own single-row-per-component structure). PASS.

**Architecture Integrity Review.** Every Disposition in Section 25 is backed by an explicit Architecture Decision (Sections 26.1-26.23), not left implicit in a table alone, per the governing task's own explicit requirement. PASS.

**Repository Boundary Review.** Section 9 explicitly excludes `archive/`, top-level `main`, `config/`, `configs/`, `data/`, `live_l1/`, `reports/`, `scripts/`, `seeds/`, `strategies/`, `tools/` from this document's own boundary decision, avoiding scope creep beyond FRA/SDA/CGA evidence. PASS.

**Active Runtime Boundary Review.** RC-AD-002 and RC-AI-001 jointly ensure exactly one active runtime path; RC-AI-007 confirms every module carries exactly one unambiguous active/inactive classification with none left undetermined; Section 25.1 confirms all fourteen active modules RETAIN unconditionally. PASS.

**Computational Authority Review.** RC-AD-007, RC-AD-010 jointly ensure zero components with a certified active counterpart, or with a determinism-incompatible mechanism, remain in the active-adjacent namespace after Implementation. PASS.

**Disposition Review.** Section 25 assigns exactly one Disposition to every component in scope; Section 15 confirms the aggregate distribution (14+4 RETAIN, 19+1 ARCHIVE, 13 IGNORE, 0 REMOVE, 0 INTEGRATE). PASS.

**Archive/Remove/Integrate Review.** RC-AD-016 and RC-AD-017 formally apply the Remove and Integration Criteria and document why neither disposition is issued anywhere in this document, consistent with RC-AI-009 (Removal Requires Independent Validation) and RC-AI-010 (Integration Requires Certified Architecture Compatibility). PASS.

**Historical Provenance Review.** RC-AI-008 and every ARCHIVE-issuing RC-AD (004, 006, 007, 009) explicitly preserve git history; zero REMOVE means zero provenance loss. PASS.

**Version-Control Boundary Review.** Section 21 states the rule; Section 25.4 confirms all twelve IGNORE-disposed directories remain untracked, consistent with the rule and with RC-AI-005 (No Runtime Import from Scratch or Review Areas) and RC-AI-006 (No Generated Runtime Artifact Tracked Without Explicit Governance). PASS.

**Long-Duration-Readiness Review.** RC-AD-018 states five repository-side preconditions without starting any run, consistent with Section 3's own scope limit. PASS.

**Scope Review.** No Specification, Implementation Unit, or Final Certification content appears anywhere in this document (Section 35). PASS.

**Terminology Review.** "Functionally identical" is used only for the future runtime-result comparison RC-AD-023 requires (Python-object comparison, not yet performed); "byte-identical" is not used anywhere, since no byte-level comparison occurs in an Architecture document. PASS.

**Repository Consistency Review.** Section 5's own re-verification found the repository unchanged from the CGA's own snapshot in every dimension checked. PASS.

**Runtime Compatibility Review.** RC-AD-023 and every certified-unit cross-reference (Section 24) confirm no certified contract is reopened or altered, consistent with RC-AI-015 (Certified Runtime Behaviour Remains Unchanged by Consolidation). PASS.

**Traceability Review.** Sections 30-32 confirm all thirteen RC-FR-IDs, all twenty-three RC-DEP-IDs, and all fifteen RC-CAP-IDs individually resolved by at least one RC-AD; Section 38's own mechanical check confirms every RC-AD-ID and RC-AI-ID cited at least twice. PASS.

**Governance Review.** RC-AD-020 documents the Formal Unit Identifier gap without resolving it; RC-AD-019 documents the TD Register-currency gap without editing the Register; RC-AI-014 (Governance Documents Have One Normative Location) is satisfied by Section 26.22's own single-location rule. PASS.

Status: Internal Consistency Review PASS.

## 37. Architecture Readiness Decision

Twenty-three Architecture Decisions and fifteen Architecture Invariants resolve all thirteen Functional Requirements, all twenty-three Dependencies, and all fifteen Capabilities the FRA, SDA, and CGA established. Every one of the four Repository Functional Gaps the FRA identified is explicitly decided through the Disposition Register (Section 25) and its own backing Architecture Decisions. The repository's own active runtime path is protected as exactly one, unambiguous boundary (RC-AD-002, RC-AI-001); competing Computational Authorities are eliminated from the active-adjacent namespace (RC-AD-007, RC-AD-010); the one confirmed namespace collision is resolved (RC-AD-004); every inactive, historical, experimental, and scratch artifact receives an individually-justified Disposition (Section 25); scientific traceability is preserved by construction (zero REMOVE, RC-AI-008); and repository-side Long-Duration-Validation preconditions are established without executing any run (RC-AD-018).

**Architecture Readiness Decision: READY for the Specification stage**, conditioned on the Implementation Impact Inventory (Section 34) being treated as scope guidance, not a pre-authorized action list - every file move, archive-directory creation, `.gitignore` edit, and Register update named in this document remains to be designed in a Specification and performed in an Implementation, neither of which this document begins.

## 38. Independent Self Verification

- File exists at the stated Primary Location: confirmed.
- ASCII-only: confirmed (see mechanical check output following this document's delivery).
- No trailing whitespace: confirmed.
- Continuous section numbering: Sections 1 through 38, no gaps, no duplicates.
- Full RC-FR-ID traceability: Section 30 confirms all thirteen RC-FR-IDs individually resolved, each cited at least twice across this document.
- Full actual RC-DEP-ID traceability: Section 31 confirms all twenty-three actually-used RC-DEP-IDs individually resolved, each cited at least twice; zero non-existent RC-DEP-002 through RC-DEP-009 or RC-DEP-014 appear anywhere.
- Full RC-CAP-ID traceability: Section 32 confirms all fifteen RC-CAP-IDs individually resolved, each cited at least twice.
- Full RC-AD-ID traceability: all twenty-three RC-AD-IDs individually defined (Section 26) and each cited at least twice elsewhere in this document (Sections 25, 27-32).
- Full RC-AI-ID traceability: all fifteen RC-AI-IDs individually defined (Section 27) and each cited at least twice.
- No accidental IU-IDs: confirmed by construction; this document defines no Implementation Units.
- No non-existent RC-DEP-IDs: confirmed (Section 31's own explicit statement, mechanically re-verified).
- No merge markers, no real placeholders: confirmed.
- `python -m compileall run_engine`: PASS (no runtime file was touched by this document).
- `git diff --check`: clean for this new, untracked file (pre-existing violations in `SGF_013...md` are unrelated and unchanged).
- `git status --short`: unchanged from Section 5's own pre-check baseline plus this one new file.
- Branch: `run-engine-consolidation-safety` (unchanged).
- Local HEAD: `a0a65187cf2ca808f5dc8fda47cfc5dcf8360842` (unchanged; no commit made).
- Remote HEAD: `a0a65187cf2ca808f5dc8fda47cfc5dcf8360842` (unchanged; no push made).

No commit is created. No push occurs. This document stops before the Specification stage, per its own governing task.
