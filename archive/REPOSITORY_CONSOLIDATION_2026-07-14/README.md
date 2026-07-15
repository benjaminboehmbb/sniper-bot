# Repository Consolidation Archive - 2026-07-14

## Purpose

This directory holds every component the Repository Consolidation governance chain disposed as ARCHIVE. It exists so that historical, exploratory, and superseded `run_engine/` and `run_engine`-adjacent code and data remain available as evidence, without occupying an active or ambiguous namespace inside `run_engine/`.

## Date

2026-07-14

## Origin

Repository Consolidation (no formal P-Unit Identifier assigned; see the Architecture's own RC-AD-020). Governed by:
- `docs/architecture/analysis/REPOSITORY_CONSOLIDATION_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-14.md`
- `docs/architecture/analysis/REPOSITORY_CONSOLIDATION_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-14.md`
- `docs/architecture/analysis/REPOSITORY_CONSOLIDATION_CAPABILITY_GAP_ANALYSIS_V1_2026-07-14.md`
- `docs/architecture/REPOSITORY_CONSOLIDATION_ARCHITECTURE_V1_2026-07-14.md` (RC-AD-004, RC-AD-006, RC-AD-007, RC-AD-008, RC-AD-009, RC-AD-010, RC-AD-015)
- `docs/architecture/REPOSITORY_CONSOLIDATION_SPECIFICATION_V1_2026-07-14.md` (RC-SPEC-003 through RC-SPEC-006, RC-SPEC-015)

## Status of Every Item in This Directory

- **Historical / inactive.** Every file here was, at the moment of archival, unreachable from `run_engine.main`'s own AST-based import closure.
- **No Computational Authority.** No file in this archive holds, or may be read as holding, Computational Authority over any certified runtime domain (Position, Financial, Risk, Performance, Strategy, Regime).
- **No active runtime path.** Nothing in this directory is, or may become, part of the active `run_engine/` import closure by virtue of its own presence here.
- **No reactivation without a new governance chain.** Any future use of any file in this archive - reactivation, integration, or reference implementation - requires its own Functional Requirement Analysis, Scientific Dependency Analysis, Capability Gap Analysis, and Architecture Decision. This README is not, and does not substitute for, that governance chain.
- **No persistence, recovery, or runtime semantics.** In particular, `run_engine/runtime/memory.json`'s own presence here is historical only; it does not define, imply, or pre-authorize any persistence or recovery architecture. `run_engine/runtime/state_memory.py` itself remains in place at its original path (RETAIN, ADR-012 Deferred Scope) and is not part of this archive.

## Provenance

Every file below was moved into this archive via a git-tracked move operation, never a copy-and-delete. The commit-level history for each original path remains fully queryable via `git log --all -- <original-path>`, independent of whether Git's own rename-similarity heuristic links the old and new path in a `git log --follow` view. **Git's own rename detection is a heuristic, not a guarantee**, and is not relied upon as the sole provenance mechanism; the underlying commit history is authoritative regardless.

## Archived Components (20)

| # | Original Path | Archive Path (this directory) | Disposition |
|---|---|---|---|
| 1 | `run_engine/execution/executor.py` | `run_engine/execution/executor.py` | ARCHIVE (RC-AD-004, path-collision resolution) |
| 2 | `run_engine/runtime/performance_analytics.py` | `run_engine/runtime/performance_analytics.py` | ARCHIVE (RC-AD-007) |
| 3 | `run_engine/runtime/pnl_engine.py` | `run_engine/runtime/pnl_engine.py` | ARCHIVE (RC-AD-007) |
| 4 | `run_engine/runtime/position_state.py` | `run_engine/runtime/position_state.py` | ARCHIVE (RC-AD-007) |
| 5 | `run_engine/runtime/risk.py` | `run_engine/runtime/risk.py` | ARCHIVE (RC-AD-007) |
| 6 | `run_engine/runtime/strategy_selector.py` | `run_engine/runtime/strategy_selector.py` | ARCHIVE (RC-AD-007) |
| 7 | `run_engine/runtime/regime_execution_gate.py` | `run_engine/runtime/regime_execution_gate.py` | ARCHIVE (RC-AD-008) |
| 8 | `run_engine/core/position_sizing.py` | `run_engine/core/position_sizing.py` | ARCHIVE (RC-AD-008) |
| 9 | `run_engine/runtime/regime_stability.py` | `run_engine/runtime/regime_stability.py` | ARCHIVE (RC-AD-009) |
| 10 | `run_engine/core/decision.py` | `run_engine/core/decision.py` | ARCHIVE (RC-AD-009) |
| 11 | `run_engine/core/equity_stabilizer.py` | `run_engine/core/equity_stabilizer.py` | ARCHIVE (RC-AD-009) |
| 12 | `run_engine/core/state_modulation.py` | `run_engine/core/state_modulation.py` | ARCHIVE (RC-AD-010, non-determinism risk) |
| 13 | `run_engine/execution/adapter.py` | `run_engine/execution/adapter.py` | ARCHIVE (RC-AD-009) |
| 14 | `run_engine/execution/safety.py` | `run_engine/execution/safety.py` | ARCHIVE (RC-AD-009) |
| 15 | `run_engine/feedback/tracker.py` | `run_engine/feedback/tracker.py` | ARCHIVE (RC-AD-009) |
| 16 | `run_engine/logging/logger.py` | `run_engine/logging/logger.py` | ARCHIVE (RC-AD-009) |
| 17 | `run_engine/runtime/strategy_memory.py` | `run_engine/runtime/strategy_memory.py` | ARCHIVE (RC-AD-009) |
| 18 | `run_engine/runtime/strategy_weights.py` | `run_engine/runtime/strategy_weights.py` | ARCHIVE (RC-AD-009) |
| 19 | `run_engine/core/features.py` | `run_engine/core/features.py` | ARCHIVE (RC-AD-008) |
| 20 | `run_engine/runtime/memory.json` | `run_engine/runtime/memory.json` | ARCHIVE (RC-AD-006, historical runtime-state artifact) |

The relative path beneath this archive root mirrors each component's own original path under `run_engine/`, unchanged, so the original location remains unambiguous without relying on Git rename-detection alone.

## Structural Guarantees

- No `__init__.py` file exists anywhere in this archive tree, at any depth, so this directory can never become an importable Python package, even by accident.
- This archive is not on `run_engine.main`'s own import closure and is not imported by any active module.
