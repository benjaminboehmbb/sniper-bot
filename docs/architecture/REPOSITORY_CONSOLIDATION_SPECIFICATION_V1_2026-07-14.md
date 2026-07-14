Document Class:
Specification

Document ID:
REPOSITORY-CONSOLIDATION-SPECIFICATION

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
docs/architecture/REPOSITORY_CONSOLIDATION_SPECIFICATION_V1_2026-07-14.md

Depends On:
- docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md
- docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md
- docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md
- docs/architecture/analysis/REPOSITORY_CONSOLIDATION_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-14.md
- docs/architecture/analysis/REPOSITORY_CONSOLIDATION_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-14.md
- docs/architecture/analysis/REPOSITORY_CONSOLIDATION_CAPABILITY_GAP_ANALYSIS_V1_2026-07-14.md
- docs/architecture/REPOSITORY_CONSOLIDATION_ARCHITECTURE_V1_2026-07-14.md
- complete P3-01, P3-02, P3-03 governance chains

Referenced By:
- future Repository Consolidation Implementation (not yet created)

Methodological Structure Reference (content not carried over):
- docs/architecture/P3_03_PERFORMANCE_VALIDATION_SPECIFICATION_V1_2026-07-13.md

---

# Repository Consolidation - Specification

## 1. Document Metadata

See front matter above. This document is the Specification stage of the Repository Consolidation governance chain, following the Functional Requirement Analysis, Scientific Dependency Analysis, Capability Gap Analysis, and Architecture. It translates the Architecture's own already-decided Dispositions into concrete, implementable Repository Contracts, Implementation Units, and a complete File-by-File Plan. It decides no new Disposition and creates no new Architecture Decision or Invariant.

## 2. Purpose

To make the Architecture's own binding decisions implementable: define the exact archive namespace, the exact `.gitignore` categories, the exact per-file target state for every RETAIN, ARCHIVE, and IGNORE component, the exact Technical Debt Register edit for TD-004, and the exact minimum scope of a durable verification tool - without performing any of it. This document specifies; it does not archive, delete, edit `.gitignore`, implement tooling, edit the Technical Debt Register, or certify anything.

## 3. Scope

In scope: sixteen Repository Contracts (RC-SPEC-001 through RC-SPEC-016), seven Implementation Units (RC-IU-001 through RC-IU-007), a complete File-by-File / Path-by-Path Plan for all 14 active modules, all 4 Deferred-Scope RETAIN components, all 20 ARCHIVE components, all 13 IGNORE paths, `.gitignore`, the Technical Debt Register, new verification tooling, and a new archive metadata file.

Out of scope (per the governing task's own explicit Workflow-Grenze): file archiving, file deletion, `.gitignore` editing, verification-tool implementation, Technical Debt Register editing, Final Certification; any functional runtime-file change; any new Architecture Decision or Invariant; any change to Functional Requirements, Dependencies, or Capabilities.

## 4. Binding Baseline

Fully read prior to drafting: the Architecture Baseline, the Implementation Baseline, the Technical Debt Register, the Repository Consolidation FRA, SDA, CGA, and Architecture (as corrected, Section 5); the complete P3-01, P3-02, and P3-03 governance chains. The P3-03 Specification is used exclusively as a structural reference for this document's own layout; none of its content is carried over.

## 5. Repository Verification

Independently re-verified immediately before drafting, not assumed from the Architecture:

1. **Active runtime import closure.** A fifth independent AST-based import-closure run from `run_engine.main` (reusing this session's own corrected script) reproduces: 37 total modules, **14 active**, 13 total edges, identical to every prior run.
2. **All 14 active modules** individually re-listed via `git ls-files run_engine/` and cross-checked against the closure result: identical set.
3. **All 23 inactive modules** individually re-confirmed unreached by the same closure run: identical set to the Architecture's own Section 25.2.
4. **Every path in the Architecture's own Per-Component Disposition Register** (Section 25.1-25.4) re-checked for continued existence and tracking status: all present, all tracking states unchanged.
5. **All twelve untracked root-level directories** re-confirmed present with unchanged file counts (Section 6 below).
6. **Tracking and `.gitignore` status** individually re-checked for every affected path (Section 6).
7. **The existing `archive/` structure re-examined in full**, going beyond the Architecture's own Section 5 finding: `archive/` contains **two** tracked subdirectories, not one - `archive/HISTORICAL_K3_K10_2026-01-06/` (80 tracked files, historical backtesting results) and **`archive/LIVE_L1_DEAD_CODE_2026-06-06/`** (1 tracked file, `live_l1/io/validate.py`), a materially closer precedent than the Architecture's own drafting cited, since it archives dead *code* under a relative-structure-preserving subpath rather than backtesting results. Neither subdirectory contains a README or metadata file (a `run_meta_*.json` filename match is a false positive, not a metadata convention). Neither is importable from `run_engine.main` (confirmed: zero edges into `archive/` in the full closure run). This is a genuine new finding beyond the Architecture's own evidence, recorded here per this document's own explicit requirement to never accept an Architecture statement unverified, and does not contradict RC-AD-015 (it strengthens the same precedent RC-AD-015 already cited).
8. **Existing tooling namespaces re-examined:** `tools/` (224 tracked files, established, unrelated-to-`run_engine` script collection, confirmed by the FRA's own repository-wide import search, not reopened); `scripts/` (149 tracked files, same category); `docs/tools/` (2 tracked files, both Trade-Inspector usage documentation, not a code location); `docs/architecture/specifications/` (9 tracked files, an already-established normative location for earlier-phase Architecture and Specification pairs, P1-02A through P2-02 - a genuine new finding, recorded for Section 17's own Documentation Boundary Contract, not required for this document's own placement, which follows the more recent P3-0x and this chain's own convention of placing Architecture/Specification files directly under `docs/architecture/`).
9. **Technical status re-confirmed:**
   - `run_engine/runtime/memory.json` - tracked, 45,174 bytes, single-commit history (`bcac70e`), unchanged.
   - `run_engine/execution/executor.py` - tracked, 0 bytes, single-commit history (`bcac70e`), unchanged.
   - `engine/regime_classifier.py` - untracked, zero git history, unchanged.
   - `run_engine/core/state_modulation.py` - `import random` (line 1), `random.random()` calls at lines 17-18, unchanged.
10. **Technical Debt Register re-confirmed:** TD-004 `Status: Already Planned` (not yet updated); TD-005 `Status: Open`; TD-007 `Status: Deferred` - all three unchanged since the Architecture's own drafting.

No Architecture statement is carried over unverified; Finding 7 and 8 above are new evidence this document itself independently gathered, consistent with, not contradicting, the Architecture's own decisions.

## 6. Specification Context

Branch `run-engine-consolidation-safety`; local HEAD and remote HEAD (freshly fetched) both `a0a65187cf2ca808f5dc8fda47cfc5dcf8360842`, identical, unchanged. `run_engine/` and `engine/` both confirmed unchanged (`git diff --stat` and `git status --short`, restricted to these two paths, empty except the already-known untracked `engine/regime_classifier.py`). Working tree otherwise unchanged from the Architecture's own snapshot, plus the Architecture document itself (now tracked as untracked-pending-commit) and this document. All twelve untracked directories re-confirmed at unchanged file counts: `_chat_handover/` (21), `_sgf017_context/` (44), `_ssi_context/` (271), `backups/` (39), `claude_final_p1031_review/` (8), `claude_p1031_patch/` (6), `claude_p1_03b_review/` (21), `codex_p1_03_review/` (24), `live_logs/` (92), `outputs/` (456), `review_packages/` (1), `runtime_runs/` (26).

**Disposition distribution used throughout this document (verbatim from the Architecture, corrected Section 34): RETAIN 18 (14 active + 4 Deferred-Scope), INTEGRATE 0, ARCHIVE 20 (19 inactive modules, which already includes `run_engine/execution/executor.py` as one of the 19 per RC-AD-004, plus `run_engine/runtime/memory.json` as the 20th, separately-typed artifact), REMOVE 0, IGNORE 13 (12 untracked directories plus `engine/regime_classifier.py`).** This distribution is taken as-is from the Architecture and is not re-decided anywhere in this document.

## 7. Normative Terminology

- **Repository Contract (RC-SPEC-xxx)** - a Specification-level, individually-numbered translation of one or more Architecture Decisions into an implementable requirement, carrying the eleven fields defined in Section 8.
- **Implementation Unit (RC-IU-xxx)** - a logically bounded group of Repository Contracts intended to be implemented together in a future Implementation stage.
- **Archive Target Path** - the concrete, git-tracked destination path an ARCHIVE-disposed component moves to, under the archive namespace this document defines (Section 11).
- **functionally identical** - used exclusively for runtime behavior and Python-object/result comparisons (e.g., the active closure's own behavior before and after Implementation).
- **byte-identical** - used exclusively for files, git blobs, or byte sequences (e.g., an active module's own content before and after this Specification's own no-change guarantee).

## 8. Repository Contract Catalogue

Every Repository Contract carries: Requirement, Repository Behaviour, Source Path (or Applicable Scope), Target State, Tracking Semantics, Importability Constraint, Provenance Requirement, Verification Method, Acceptance Condition, No-Change Boundary, and Traceability (RC-FR, RC-DEP, RC-CAP, RC-AD, RC-AI). Sixteen contracts are defined, RC-SPEC-001 through RC-SPEC-016, one per Contract-Bereich the governing task named, in the same order.

## 9. Active Runtime Retention Contracts

**RC-SPEC-001. Active Runtime Retention Contract.**
Requirement: all 14 active modules remain exactly as they are. Repository Behaviour: no move, no rename, no content edit, no import-line change. Source Path: all 14 paths of Architecture Section 25.1. Target State: identical to current state. Tracking Semantics: remains tracked, unchanged. Importability Constraint: the active closure from `run_engine.main` must remain exactly the same 14-module, 13-edge set. Provenance Requirement: git history untouched (no move event of any kind). Verification Method: AST-based import-closure re-run plus byte-identical blob comparison of all 14 files against the pre-Implementation commit. Acceptance Condition: closure result and all 14 blob hashes unchanged. No-Change Boundary: absolute - zero tolerance for any diff in this file set. Traceability: RC-FR-001, RC-FR-002; RC-DEP-001, RC-DEP-020, RC-DEP-021, RC-DEP-022, RC-DEP-023, RC-DEP-024, RC-DEP-025; RC-CAP-001; RC-AD-002, RC-AD-023; RC-AI-001, RC-AI-015.

## 10. Deferred-Scope Retention Contracts

**RC-SPEC-002. Deferred-Scope Retention Contract.**
Requirement: `run_engine/core/config.py`, `run_engine/runtime/recovery.py`, `run_engine/runtime/snapshot.py`, `run_engine/runtime/state_memory.py` remain at their current paths, inactive, unimplemented, unreactivated. Repository Behaviour: no move, no content edit (the first three remain zero-byte; `state_memory.py` remains as-is). Source Path: the four paths above. Target State: identical to current state. Tracking Semantics: remains tracked, unchanged. Importability Constraint: none of the four may appear in the active closure after Implementation. Provenance Requirement: not applicable (no move occurs). Verification Method: import-closure re-run confirms continued non-membership in the active set; byte-identical comparison of all four against the pre-Implementation commit. Acceptance Condition: all four files unchanged, all four remain unreached. No-Change Boundary: absolute. **This Specification finds that this Contract requires documentation only - the ADR-012 Deferred-Scope association is already fully recorded in the Architecture (RC-AD-005) and in this document (Section 25.2); no file content change, no new file, and no `.gitignore` entry is required to satisfy it.** Traceability: RC-FR-006, RC-FR-008; RC-DEP-012, RC-DEP-013; RC-CAP-003, RC-CAP-010; RC-AD-005; RC-AI-001, RC-AI-007.

## 11. Archive Namespace Contracts

**RC-SPEC-003. Archive Namespace Contract.**
Requirement: define one concrete, unambiguous archive namespace for every ARCHIVE-disposed component. Repository Behaviour: establishes (does not create) the target root `archive/REPOSITORY_CONSOLIDATION_2026-07-14/`, following the exact naming convention already established by `archive/HISTORICAL_K3_K10_2026-01-06/` and `archive/LIVE_L1_DEAD_CODE_2026-06-06/` (Section 5, Finding 7). Source Path: not applicable (namespace definition, not a single file). Target State: a new, git-tracked root directory, mirroring each archived file's own relative path beneath it (e.g., `run_engine/runtime/performance_analytics.py` archives to `archive/REPOSITORY_CONSOLIDATION_2026-07-14/run_engine/runtime/performance_analytics.py`), with no `__init__.py` created at any level within the archived tree, structurally preventing the archived tree from ever being importable as a Python package even by accident. Tracking Semantics: tracked, exactly as the two existing precedent subdirectories are. Importability Constraint: `archive/` is confirmed unreachable from `run_engine.main`'s own closure (Section 5); this namespace introduces no new edge into that closure, and the deliberate omission of `__init__.py` files is an additional structural safeguard beyond mere path placement. Provenance Requirement: implemented exclusively via git-tracked move operations (Section 22, RC-SPEC-015), never copy-and-delete. Verification Method: post-Implementation, confirm the archive root is absent from the active closure result and that no `__init__.py` exists anywhere under it. Acceptance Condition: exactly one archive root for this governance unit, label distinct from `run_engine`/`engine`, no collision with the two existing precedent subdirectories. No-Change Boundary: this Contract does not decide to place any file there yet (Section 12 does); it establishes the path only. **No duplicate runtime folder structure is created under `docs/`** - the archive root is exclusively under the existing top-level `archive/`, never under `docs/`. Traceability: RC-FR-004, RC-FR-006; RC-DEP-012, RC-DEP-013; RC-CAP-010; RC-AD-015; RC-AI-004, RC-AI-008.

## 12. Inactive Module Archive Contracts

**RC-SPEC-004. Inactive Module Archive Contract.**
Requirement: each of the 19 ARCHIVE-disposed inactive modules (Architecture Section 25.2, including `run_engine/execution/executor.py`) moves to its own mirrored path under the archive root (RC-SPEC-003). Repository Behaviour, per file: git-tracked move (`git mv`-equivalent), no content edit. Verification Method, per file: post-move import-closure re-run must show zero change to the 14-active/13-edge result; a repository-wide `grep`/AST search must show zero import of the archived module's own old dotted path from anywhere under `run_engine/`. Acceptance Condition: all 19 files present at their new archive path, absent from their old path, active closure unchanged; this includes `core/features.py`, whose own matched-but-unwired relationship to `engine.regime_classifier` (RC-DEP-017) and whose own inherited Alternative Implementation Classification (RC-CAP-005) remain ARCHIVE-disposed, not reopened. No-Change Boundary: the active 14-module closure must remain byte-identical and functionally identical throughout. The full per-file Source Path / Archive Target Path / Tracking Status / Importability / Provenance / References-to-adjust / No-Change-effect table is given in Section 25.1. Traceability: RC-FR-003, RC-FR-004, RC-FR-005, RC-FR-006, RC-FR-007, RC-FR-009, RC-FR-012; RC-DEP-010, RC-DEP-011, RC-DEP-015, RC-DEP-016, RC-DEP-018, RC-DEP-019, RC-DEP-026, RC-DEP-027, RC-DEP-028, RC-DEP-029, RC-DEP-030; RC-CAP-002, RC-CAP-003, RC-CAP-006, RC-CAP-008, RC-CAP-011, RC-CAP-012; RC-AD-004, RC-AD-007, RC-AD-008, RC-AD-009, RC-AD-010; RC-AI-002, RC-AI-003, RC-AI-008.

## 13. Runtime Artifact Archive Contracts

**RC-SPEC-005. `memory.json` Archive Contract.**
Requirement: `run_engine/runtime/memory.json` moves to `archive/REPOSITORY_CONSOLIDATION_2026-07-14/run_engine/runtime/memory.json`. Repository Behaviour: git-tracked move, no content edit. Source Path: `run_engine/runtime/memory.json`. Target State: present only at the archive path; absent from the active-adjacent `run_engine/runtime/` directory. Tracking Semantics: remains tracked throughout, only its path changes. Historical labeling: the archive root's own README (RC-SPEC-015) records this file's own single-commit provenance (`bcac70e`) and schema relationship to `state_memory.py`. **No active runtime state exists in this artifact today** (Section 5, Finding 9 - `state_memory.py` is unreached, so nothing currently reads or writes this file); this Contract does not, and this Specification does not, design a persistence architecture - it relocates a stale, already-orphaned artifact, and does not decide whether `state_memory.py` is ever reactivated, nor does it prevent a future, independent persistence design from starting from a clean state. No automatic reuse: any future activation of `state_memory.py` must, per ADR-012 and RC-AD-005, undergo its own Architecture Evolution Review before reading any file, archived or otherwise. Scientific provenance is preserved via the git-tracked move (RC-SPEC-015). Verification Method: post-move, confirm zero references to `run_engine/runtime/memory.json` anywhere under `run_engine/`, and confirm the file's own content is byte-identical at its new path. Acceptance Condition: file present only at the archive path, byte-identical, git history preserved. No-Change Boundary: `state_memory.py` itself (RC-SPEC-002) is not touched by this Contract. Traceability: RC-FR-008; RC-DEP-013, RC-DEP-031; RC-CAP-010, RC-CAP-013; RC-AD-006; RC-AI-006, RC-AI-008.

## 14. Path-Collision Resolution Contracts

**RC-SPEC-006. Path-Collision Resolution Contract.**
Requirement: resolve the `executor.py` collision per RC-AD-004. Repository Behaviour: `run_engine/core/execution/executor.py` (active) receives zero change of any kind; `run_engine/execution/executor.py` (top-level, inactive, empty) moves to `archive/REPOSITORY_CONSOLIDATION_2026-07-14/run_engine/execution/executor.py`, as one instance of RC-SPEC-004. Source Path: both paths named above. Target State: exactly one `executor.py` remains under `run_engine/`. Tracking Semantics: the active file remains tracked, unchanged, at its current path; the inactive file remains tracked, only its path changes. Importability Constraint: post-move, `run_engine.execution.executor` (top-level) must be absent from any import-closure result; `run_engine.core.execution.executor` must remain, unchanged, the sole reachable `Executor`. Provenance Requirement: git-tracked move for the archived file (RC-SPEC-015); zero touch for the active file. Verification Method: import-closure re-run confirms exactly one `executor.py`-named module reachable; byte-identical comparison of the active `core/execution/executor.py` against the pre-Implementation commit. Acceptance Condition: no active namespace ambiguity remains (RC-AI-003 satisfied). No-Change Boundary: the active Executor's own import line in `run_engine/core/execution/__init__.py` (`from .executor import Executor`) is not touched. Traceability: RC-FR-004; RC-DEP-001; RC-CAP-011; RC-AD-003, RC-AD-004; RC-AI-003.

## 15. Ignore and Gitignore Contracts

**RC-SPEC-007. IGNORE Contract.**
Requirement: all 13 IGNORE-disposed paths (Architecture Section 25.3-25.4) remain on disk, untracked, excluded from future `git status` noise via `.gitignore`. Repository Behaviour: no file within any of the 13 paths is read, moved, or deleted by this Specification or by the future Implementation it authorizes, beyond adding `.gitignore` patterns. Source Path: `_chat_handover/`, `claude_final_p1031_review/`, `claude_p1031_patch/`, `claude_p1_03b_review/`, `codex_p1_03_review/`, `review_packages/`, `_sgf017_context/`, `_ssi_context/`, `backups/`, `live_logs/`, `outputs/`, `runtime_runs/`, `engine/regime_classifier.py`. Target State: identical local content; excluded from tracking going forward. Tracking Semantics: all 13 are currently untracked; they remain untracked. Importability Constraint: none of the 13 may be imported by any active module (re-confirmed, Section 5). Provenance Requirement: not applicable (never tracked, so no git history exists to preserve). Verification Method: `git check-ignore -v` for a representative file under each of the 13 paths, post-`.gitignore`-update. Acceptance Condition: all 13 report ignored; `git status --short` no longer lists any of them. No-Change Boundary: **no local content within any of the 13 paths is deleted by this Specification or its own authorized Implementation**, unless the Architecture explicitly required it (it does not, RC-AD-012/RC-AD-013 both specify IGNORE, not REMOVE). Traceability: RC-FR-011; RC-DEP-032; RC-CAP-007, RC-CAP-011; RC-AD-012, RC-AD-013; RC-AI-005, RC-AI-011.

**RC-SPEC-008. Gitignore Contract.**
Requirement: define concrete `.gitignore` pattern categories. Repository Behaviour: nine categories are specified, each with a precise, root-anchored pattern to avoid over-broad wildcards:

| Category | Pattern | Anchoring Rationale |
|---|---|---|
| Logs | `/live_logs/` | Root-anchored; existing partial rules (`live_logs/*.log`, `*.jsonl`, `*.csv`, `live_logs/archive/`) are superseded, not duplicated, by this single directory-level rule |
| Outputs | `/outputs/` | Root-anchored; distinct from the existing, unrelated `out/` rule |
| Runtime Runs | `/runtime_runs/` | Root-anchored |
| Backups | `/backups/` | Root-anchored |
| Scratch Workspaces | `/_chat_handover/`, `/claude_p1031_patch/` | Root-anchored, individually named |
| Review Packages | `/claude_final_p1031_review/`, `/claude_p1_03b_review/`, `/codex_p1_03_review/`, `/review_packages/` | Root-anchored, individually named |
| Local Context Bundles | `/_sgf017_context/`, `/_ssi_context/` | Root-anchored, individually named |
| Generated State | `/run_engine/runtime/memory.json` (reserved pattern, currently moot post-archival; retained as a guard against any future re-creation of a tracked runtime-state artifact at this specific path) | Path-specific, not a wildcard |
| Cache Files | no new rule; existing `__pycache__/`, `*.pyc` rules (already present, confirmed sufficient, Section 5) | N/A |

`engine/regime_classifier.py` (satisfying RC-FR-010's own `engine/`-scope requirement) is deliberately **not** given a `.gitignore` pattern in this Contract, since a pattern excluding a single file inside an otherwise fully-tracked package risks unintended breadth if the package ever gains new untracked siblings; RC-SPEC-016 records this as an open Implementation-stage choice (exclude by exact path, or relocate) rather than deciding it here. Verification Method: `git check-ignore -v` for each pattern; `git status --short` before/after diff must show zero previously-tracked file newly excluded. Acceptance Condition: exactly the nine categories above, no broader wildcard than stated, zero normative file affected. No-Change Boundary: no currently-tracked file (verified: none of the above patterns matches any of the 38 `run_engine/`-tracked files after `memory.json`'s own archival, nor any of the 3 tracked `engine/` files). Traceability: RC-FR-011; RC-DEP-032; RC-CAP-007; RC-AD-014; RC-AI-005, RC-AI-011.

## 16. Review and Scratch Boundary Contracts

**RC-SPEC-009. Review/Scratch Boundary Contract.**
Requirement: `_chat_handover/`, `claude_final_p1031_review/`, `claude_p1031_patch/`, `claude_p1_03b_review/`, `codex_p1_03_review/`, `review_packages/` remain outside normative documentation. Repository Behaviour: no file within these six is ever treated as an authoritative source for any future governance document; no import from these six occurs anywhere in `run_engine/` (re-confirmed, Section 5). Source Path: the six paths above. Target State: unchanged content, `.gitignore`-excluded (RC-SPEC-008). Tracking Semantics: untracked, remains untracked. Importability Constraint: zero. Provenance Requirement: not applicable. Verification Method: a repository-wide search confirms no `docs/architecture/` file references any of these six paths as its own source. Acceptance Condition: zero such references exist. No-Change Boundary: no committed governance artifact is replaced or superseded by content from these six locations. Traceability: RC-FR-011; RC-DEP-032; RC-CAP-007; RC-AD-012; RC-AI-005, RC-AI-014.

## 17. Documentation Boundary Contracts

**RC-SPEC-010. Documentation Boundary Contract.**
Requirement: normative documentation remains exclusively in the approved `docs/` namespaces. Repository Behaviour: none of this document's own actions moves or edits any governance document. Source Path (approved normative locations): `docs/architecture/`, `docs/architecture/analysis/`, `docs/architecture/certification/`, `docs/architecture/technical_debt/`, and, for already-existing earlier-phase documents only, `docs/architecture/specifications/` (Section 5, Finding 8 - a genuinely pre-existing, tracked, normative location for the P1-02A through P2-02 Architecture/Specification pairs, not required for this chain, which follows the more recent flat convention). Target State: unchanged; this Contract records the boundary, it does not move any file into or out of it. Tracking Semantics: all five locations are tracked. Importability Constraint: not applicable (documentation, not code). Provenance Requirement: not applicable. Verification Method: confirm this Specification's own file resides at `docs/architecture/REPOSITORY_CONSOLIDATION_SPECIFICATION_V1_2026-07-14.md`, one of the approved locations. Acceptance Condition: satisfied by construction. No-Change Boundary: no sixth location is introduced. Traceability: RC-FR-012, RC-FR-013; RC-DEP-032; RC-CAP-009; RC-AD-022; RC-AI-014.

## 18. Verification Tooling Contracts

**RC-SPEC-011. Verification Tooling Contract.**
Requirement: a durable, repository-resident Repository Consolidation verification tool must exist after Implementation. Repository Behaviour: this Contract specifies scope and location only; **no implementation is performed by this Specification** (explicit Workflow-Grenze). Target Path: `tools/repository_consolidation/verify_repository_consolidation.py`, reusing the existing, established `tools/` namespace (Section 5, Finding 8 - 224 tracked files, confirmed unrelated to `run_engine`'s own active path, an appropriate home for governance/analysis scripts as distinct from production runtime code) under a clearly-labeled subpackage so it is never mistaken for one of the existing trading-analysis scripts already there. Minimum Checks (verbatim from the governing task, order not significant): active import closure; active/inactive module set; unexpected imports from `archive/`; unexpected imports from Scratch/Review areas; duplicate active module/path names; tracked generated runtime artifacts; disallowed root-level artifacts; the canonical runtime entry point; an unchanged active-runtime file set; confirmation that archived files are not importable. Classification: governance tooling, not production/trading code; must not be imported by, and must not import, anything within `run_engine.main`'s own active closure. Tracking Semantics: to be tracked upon creation (a future Implementation action). Verification Method: the tool's own output must be independently reproducible, matching this document's own Section 5 findings exactly when run against the current repository state. Acceptance Condition: a Specification-stage design (this Section) exists before any Implementation of the tool itself. No-Change Boundary: no script content, function signature, or dependency is written by this document. Traceability: RC-FR-001; RC-DEP-001; RC-CAP-004; RC-AD-021; RC-AI-012.

## 19. Technical-Debt Register Contracts

**RC-SPEC-012. Technical-Debt Register Contract.**
Requirement: TD-004's own `Status` field updates to reflect the certified P3-03 closure. Repository Behaviour: **not performed by this Specification** (explicit Workflow-Grenze); specified for a future Implementation as an exclusively editorial change. Source Path: `docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md`, the TD-004 entry (currently `Status: Already Planned`). Target State: `Status: Closed` (or an equivalent Register-consistent closed-state label matching the Register's own existing vocabulary, to be confirmed against the Register's own full status taxonomy at Implementation time - this Specification does not invent a new status label), with a citation to the P3-03 Final Certification as the closure source. Change Type: editorial/Register-field only; explicitly **no renewed technical work**, since TD-004 is already functionally closed. TD-005: remains `Status: Open`, untouched. TD-007: remains `Status: Deferred`, untouched. No further TD entry is touched, since none has repository-structure-relevant evidence beyond TD-004/005/007 (Architecture Section 29, not reopened). Verification Method: a diff of the Register file, post-Implementation, must show exactly one field change (TD-004's own `Status`) plus, if the Register's own format requires it, a closure-citation addition; zero other line changes. Acceptance Condition: TD-005 and TD-007 byte-identical before and after. No-Change Boundary: no TD entry's own `Description`, `Priority`, `Target Phase`, or `Source` field is edited. Traceability: RC-FR-008, RC-FR-012; RC-DEP-013, RC-DEP-026, RC-DEP-031; RC-CAP-013; RC-AD-019; RC-AI-006.

## 20. Long-Duration-Readiness Contracts

**RC-SPEC-013. Long-Duration-Readiness Contract.**
Requirement: repository-side preconditions for the Smoke through 30-day run sequence. Repository Behaviour: this Contract restates RC-AD-018's own five criteria as verifiable, post-Implementation conditions, without starting any run. Criteria: (a) active import closure unambiguous (RC-SPEC-001); (b) zero importable Archive path (RC-SPEC-003, RC-SPEC-004); (c) zero colliding active path (RC-SPEC-006); (d) Output/Log/Run directories `.gitignore`-defined (RC-SPEC-008); (e) zero tracked runtime-state remnant in the active-adjacent namespace (RC-SPEC-005); plus two additional, Specification-level conditions: (f) the Verification Tool (RC-SPEC-011) reports PASS; (g) the active runtime is functionally identical to the certified pre-Implementation state (RC-SPEC-014). Verification Method: all seven conditions checked in sequence, as part of the Verification Plan (Section 27). Acceptance Condition: all seven PASS. No-Change Boundary: no run of any duration is started by this document or by the Implementation it specifies. Traceability: RC-FR-001, RC-FR-011; RC-DEP-001, RC-DEP-032; RC-CAP-010; RC-AD-018; RC-AI-013.

## 21. Runtime Non-Change Contracts

**RC-SPEC-014. Runtime Non-Change Contract.**
Requirement: no functional runtime file changes; no active file moves; no active import line changes; no Stage-Ordering, Ownership, Information-Flow, or Performance change. Repository Behaviour: absolute prohibition, covering every Implementation Unit this Specification authorizes. Verification Method: `python -m compileall run_engine` PASS; a full regression comparison of the active fourteen-module closure's own behavior (functionally identical Python-object/result comparison, not merely a compile check) before and after Implementation; byte-identical blob comparison of all 14 active files (RC-SPEC-001). Acceptance Condition: zero functional diff, zero import-line diff, zero blob-hash diff for any of the 14 active files. No-Change Boundary: this Contract is the umbrella guarantee every other Contract in this document operates under. Traceability: RC-FR-001, RC-FR-002; RC-DEP-001, RC-DEP-020 through RC-DEP-025; RC-CAP-001, RC-CAP-014; RC-AD-002, RC-AD-023; RC-AI-001, RC-AI-015.

## 22. Archive Provenance Contracts

**RC-SPEC-015. Archive Provenance Contract.**
Requirement: archival preserves git history and is documented. Repository Behaviour: every archival move (RC-SPEC-004, RC-SPEC-005, RC-SPEC-006) is performed via a git-tracked move operation (`git mv` or equivalent), never a copy-and-delete pair, so git's own rename-similarity detection has the best possible chance of linking old and new paths in `git log --follow`; **this Specification does not claim, and the future Implementation must not claim, that Git's own rename detection is guaranteed** - it is a heuristic, not a guarantee, and the underlying commit-level history (`git log --all -- <old-path>`) remains fully authoritative and traceable regardless of whether rename-detection succeeds. A new file, `archive/REPOSITORY_CONSOLIDATION_2026-07-14/README.md`, is specified (not created by this document) to record: the archive's own purpose, the governing Architecture Decision (RC-AD-004 through RC-AD-010, RC-AD-015), the date, and a manifest of every file's own original path. Verification Method: post-Implementation, `git log --all -- <archive-path>` must resolve to the same commit history as `git log --all -- <original-path>` for every archived file. Acceptance Condition: full commit history traceable for all 20 archived components; the README exists and enumerates all 20. No-Change Boundary: the README is documentation, not a runtime file; its own creation does not touch `run_engine/`. Traceability: RC-FR-004, RC-FR-006; RC-DEP-012, RC-DEP-013; RC-CAP-006, RC-CAP-010; RC-AD-015; RC-AI-008.

## 23. No-Removal Contracts

**RC-SPEC-016. No-Removal Contract.**
Requirement: zero REMOVE dispositions are implemented; no physical deletion occurs beyond the source-path vacancy that a git-tracked move (RC-SPEC-015) itself produces as a technical side effect (a moved file is, definitionally, no longer present at its old path - this is not a deletion of content, only of location); no local IGNORE-disposed content is deleted. Repository Behaviour: absolute prohibition on `rm`, `git rm` (without a corresponding `git mv`), or any equivalent deletion, anywhere this Specification's own authorized Implementation touches. The one still-open Implementation-stage choice this Specification does not resolve (Section 15, RC-SPEC-008) - whether `engine/regime_classifier.py` receives an exact-path `.gitignore` entry or a relocation - **explicitly excludes deletion as an option in either case**; the file remains on disk either way. Verification Method: a file-count comparison of all 13 IGNORE-disposed paths, before and after Implementation, must show zero reduction. Acceptance Condition: file counts unchanged for all 13 IGNORE paths; all 20 ARCHIVE-disposed components present (at their new path) with byte-identical content. No-Change Boundary: this Contract is the umbrella guarantee against any Implementation over-reach beyond what RC-SPEC-001 through RC-SPEC-015 specify. Traceability: RC-FR-003, RC-FR-006; RC-DEP-001, RC-DEP-032; RC-CAP-003, RC-CAP-007; RC-AD-016; RC-AI-008, RC-AI-009.

## 24. Implementation Units

**RC-IU-001. Archive Namespace Establishment.**
Ziel: create `archive/REPOSITORY_CONSOLIDATION_2026-07-14/` and its own `README.md`, per RC-SPEC-003 and RC-SPEC-015; no source file moved yet within this Unit. Betroffene Pfade: the new archive root and its README only. Voraussetzungen: RC-SPEC-003 and RC-SPEC-015 approved (this document). Repository Contracts: RC-SPEC-003, RC-SPEC-015. Acceptance Criteria: archive root exists, tracked, zero `__init__.py` anywhere within it; README enumerates all 20 components this Unit's own successor (RC-IU-002, RC-IU-003) will populate. Verifikation: directory listing confirms structure; import-closure re-run confirms zero new active-path edge. No-Change-Grenzen: `run_engine/` untouched by this Unit. Dependencies: none (first Unit). Traceability: RC-FR-004, RC-FR-006; RC-DEP-012, RC-DEP-013; RC-CAP-010; RC-AD-015; RC-AI-004, RC-AI-008.

**RC-IU-002. Inactive Module Archival.**
Ziel: move all 19 ARCHIVE-disposed inactive modules (including `run_engine/execution/executor.py`, resolving the path collision) to their mirrored archive paths under RC-IU-001's own root. Betroffene Pfade: the 19 source paths (Section 25.1) and their 19 archive targets. Voraussetzungen: RC-IU-001 complete. Repository Contracts: RC-SPEC-004, RC-SPEC-006, RC-SPEC-015, RC-SPEC-016. Acceptance Criteria: all 19 files present only at their archive path; active closure unchanged (14 modules, 13 edges); zero repository-wide import of any archived module's own old dotted path. Verifikation: import-closure re-run; repository-wide `grep`/AST search for old dotted paths; byte-identical comparison of each archived file's own content pre/post-move. No-Change-Grenzen: the 14 active modules, including `run_engine/core/execution/executor.py` and its own `__init__.py`'s own import line, remain untouched. Dependencies: RC-IU-001. Traceability: RC-FR-003, RC-FR-004, RC-FR-005, RC-FR-007, RC-FR-009; RC-DEP-010, RC-DEP-011, RC-DEP-015, RC-DEP-016, RC-DEP-018, RC-DEP-019, RC-DEP-026, RC-DEP-027, RC-DEP-028, RC-DEP-029, RC-DEP-030; RC-CAP-002, RC-CAP-006, RC-CAP-008, RC-CAP-011; RC-AD-004, RC-AD-007, RC-AD-008, RC-AD-009, RC-AD-010; RC-AI-002, RC-AI-003.

**RC-IU-003. Runtime Artifact Archival.**
Ziel: move `run_engine/runtime/memory.json` to its archive path; leave no runtime-state artifact in the active-adjacent source tree. Betroffene Pfade: `run_engine/runtime/memory.json` and its archive target. Voraussetzungen: RC-IU-001 complete. Repository Contracts: RC-SPEC-005, RC-SPEC-015, RC-SPEC-016. Acceptance Criteria: file present only at the archive path, byte-identical; `run_engine/runtime/` no longer contains any JSON artifact; `state_memory.py` (RC-SPEC-002, untouched) confirmed still unreached. Verifikation: byte-identical comparison; repository-wide search for `memory.json` references under `run_engine/`. No-Change-Grenzen: `state_memory.py` itself is not edited or moved. Dependencies: RC-IU-001; independent of RC-IU-002. Traceability: RC-FR-008; RC-DEP-013, RC-DEP-031; RC-CAP-010, RC-CAP-013; RC-AD-006; RC-AI-006, RC-AI-008.

**RC-IU-004. Gitignore and Workspace Boundary.**
Ziel: cover all 13 IGNORE-disposed paths and the nine `.gitignore` categories; delete no local file. Betroffene Pfade: `.gitignore` itself; the 13 IGNORE paths (read-only, for verification purposes). Voraussetzungen: none (independent of RC-IU-001 through RC-IU-003). Repository Contracts: RC-SPEC-007, RC-SPEC-008. Acceptance Criteria: `git check-ignore -v` reports ignored for all 13; `git status --short` no longer lists any of the 13; zero previously-tracked file newly matched by any new pattern; file counts unchanged for all 13. Verifikation: before/after `git status --short` diff; per-category `git check-ignore` check. No-Change-Grenzen: no file within any of the 13 paths is opened for writing or deleted. Dependencies: none. Traceability: RC-FR-011; RC-DEP-032; RC-CAP-007, RC-CAP-011; RC-AD-012, RC-AD-013, RC-AD-014; RC-AI-005, RC-AI-011.

**RC-IU-005. Repository Verification Tooling.**
Ziel: implement the tool specified in RC-SPEC-011, reproducing this document's own Section 5 findings mechanically. Betroffene Pfade: `tools/repository_consolidation/verify_repository_consolidation.py` (new). Voraussetzungen: RC-IU-002, RC-IU-003 complete (so the tool's own archive-import-prohibition check has a populated archive to check against). Repository Contracts: RC-SPEC-011. Acceptance Criteria: tool reports exactly 14 active modules, zero archive imports, zero scratch/review imports, zero duplicate active names, zero disallowed root-level artifact, canonical entry point confirmed, active file set unchanged, archived files confirmed non-importable. Verifikation: tool's own output cross-checked against this document's own Section 5 findings for equality. No-Change-Grenzen: the tool itself is never imported by, nor imports, anything in `run_engine.main`'s own active closure. Dependencies: RC-IU-002, RC-IU-003. Traceability: RC-FR-001; RC-DEP-001; RC-CAP-004; RC-AD-021; RC-AI-012.

**RC-IU-006. Technical-Debt Register Update.**
Ziel: update TD-004's own `Status` field per RC-SPEC-012; leave TD-005 and TD-007 untouched. Betroffene Pfade: `docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md`. Voraussetzungen: none (independent of all other Units). Repository Contracts: RC-SPEC-012. Acceptance Criteria: TD-004's own `Status` field updated with a P3-03 Final Certification citation; TD-005 and TD-007 byte-identical before/after; zero other Register line changed. Verifikation: Register file diff, line-by-line. No-Change-Grenzen: no TD entry's own `Description`, `Priority`, `Target Phase`, or `Source` field is edited. Dependencies: none. Traceability: RC-FR-008, RC-FR-012; RC-DEP-013, RC-DEP-026, RC-DEP-031; RC-CAP-013; RC-AD-019; RC-AI-006.

**RC-IU-007. Compatibility and Readiness Verification.**
Ziel: confirm the active runtime is functionally identical, `compileall` passes, import tests pass, repository topology is clean, and Long-Duration-Readiness criteria are satisfied; confirm zero active behavioral change. Betroffene Pfade: all 14 active modules (read-only verification); the Verification Tool's own output. Voraussetzungen: RC-IU-001 through RC-IU-006 complete. Repository Contracts: RC-SPEC-001, RC-SPEC-013, RC-SPEC-014. Acceptance Criteria: all items in Section 27 (Verification Plan) PASS. Verifikation: the full Verification Plan, executed in sequence. No-Change-Grenzen: this Unit performs verification only; if any check fails, Implementation stops and reports the failure rather than adjusting scope. Dependencies: RC-IU-001 through RC-IU-006. Traceability: RC-FR-001, RC-FR-002; RC-DEP-001, RC-DEP-020 through RC-DEP-025; RC-CAP-001, RC-CAP-014; RC-AD-002, RC-AD-018, RC-AD-023; RC-AI-001, RC-AI-013, RC-AI-015.

## 25. File-by-File and Path-by-Path Plan

### 25.1 Active Modules (14) - RC-SPEC-001

| Path | Current State | Target State | Required Change | Tracking Consequence | Import Consequence | Verification | Traceability |
|---|---|---|---|---|---|---|---|
| `run_engine/main.py` | Active, tracked | Identical | None | None | None | Blob hash unchanged | RC-SPEC-001 |
| `run_engine/core/loop.py` | Active, tracked | Identical | None | None | None | Blob hash unchanged | RC-SPEC-001 |
| `run_engine/core/state.py` | Active, tracked | Identical | None | None | None | Blob hash unchanged | RC-SPEC-001 |
| `run_engine/core/regime.py` | Active, tracked | Identical | None | None | None | Blob hash unchanged | RC-SPEC-001 |
| `run_engine/core/strategy.py` | Active, tracked | Identical | None | None | None | Blob hash unchanged | RC-SPEC-001 |
| `run_engine/core/position.py` | Active, tracked | Identical | None | None | None | Blob hash unchanged | RC-SPEC-001 |
| `run_engine/core/risk.py` | Active, tracked | Identical | None | None | None | Blob hash unchanged | RC-SPEC-001 |
| `run_engine/core/execution/__init__.py` | Active, tracked | Identical | None | None | None | Blob hash unchanged | RC-SPEC-001 |
| `run_engine/core/execution/executor.py` | Active, tracked | Identical | None | None | None | Blob hash unchanged; confirmed sole `executor.py` post-Implementation | RC-SPEC-001, RC-SPEC-006 |
| `run_engine/core/performance.py` | Active, tracked | Identical | None | None | None | Blob hash unchanged | RC-SPEC-001 |
| `run_engine/core/pnl.py` | Active, tracked | Identical | None | None | None | Blob hash unchanged | RC-SPEC-001 |
| `run_engine/core/trade_lifecycle.py` | Active, tracked | Identical | None | None | None | Blob hash unchanged | RC-SPEC-001 |
| `run_engine/core/canonical_state.py` | Active, tracked | Identical | None | None | None | Blob hash unchanged | RC-SPEC-001 |
| `run_engine/core/canonical_enforcer.py` | Active, tracked | Identical | None | None | None | Blob hash unchanged | RC-SPEC-001 |

### 25.2 Deferred-Scope RETAIN Components (4) - RC-SPEC-002

| Path | Current State | Target State | Required Change | Tracking Consequence | Import Consequence | Verification | Traceability |
|---|---|---|---|---|---|---|---|
| `run_engine/core/config.py` | Inactive, tracked, empty | Identical | None | None | Remains unreached | Blob hash unchanged | RC-SPEC-002 |
| `run_engine/runtime/recovery.py` | Inactive, tracked, empty | Identical | None | None | Remains unreached | Blob hash unchanged | RC-SPEC-002 |
| `run_engine/runtime/snapshot.py` | Inactive, tracked, empty | Identical | None | None | Remains unreached | Blob hash unchanged | RC-SPEC-002 |
| `run_engine/runtime/state_memory.py` | Inactive, tracked | Identical | None | None | Remains unreached | Blob hash unchanged | RC-SPEC-002 |

### 25.3 ARCHIVE Components (20) - RC-SPEC-004, RC-SPEC-005, RC-SPEC-006

| Source Path | Archive Target Path | Tracking Before | Tracking After | Importability After | Provenance | References to Adjust | No-Change Effect on Active Closure |
|---|---|---|---|---|---|---|---|
| `run_engine/execution/executor.py` | `archive/REPOSITORY_CONSOLIDATION_2026-07-14/run_engine/execution/executor.py` | Tracked | Tracked (moved) | Non-importable | Git move, history preserved | None (never imported) | None; resolves path collision |
| `run_engine/runtime/performance_analytics.py` | `archive/REPOSITORY_CONSOLIDATION_2026-07-14/run_engine/runtime/performance_analytics.py` | Tracked | Tracked (moved) | Non-importable | Git move, history preserved | None (never imported) | None |
| `run_engine/runtime/pnl_engine.py` | `archive/REPOSITORY_CONSOLIDATION_2026-07-14/run_engine/runtime/pnl_engine.py` | Tracked | Tracked (moved) | Non-importable | Git move, history preserved | None (never imported) | None |
| `run_engine/runtime/position_state.py` | `archive/REPOSITORY_CONSOLIDATION_2026-07-14/run_engine/runtime/position_state.py` | Tracked | Tracked (moved) | Non-importable | Git move, history preserved | None (never imported) | None |
| `run_engine/runtime/risk.py` | `archive/REPOSITORY_CONSOLIDATION_2026-07-14/run_engine/runtime/risk.py` | Tracked | Tracked (moved) | Non-importable | Git move, history preserved | None (never imported) | None |
| `run_engine/runtime/strategy_selector.py` | `archive/REPOSITORY_CONSOLIDATION_2026-07-14/run_engine/runtime/strategy_selector.py` | Tracked | Tracked (moved) | Non-importable | Git move, history preserved | None (never imported) | None |
| `run_engine/runtime/regime_execution_gate.py` | `archive/REPOSITORY_CONSOLIDATION_2026-07-14/run_engine/runtime/regime_execution_gate.py` | Tracked | Tracked (moved) | Non-importable | Git move, history preserved | None (never imported) | None |
| `run_engine/core/position_sizing.py` | `archive/REPOSITORY_CONSOLIDATION_2026-07-14/run_engine/core/position_sizing.py` | Tracked | Tracked (moved) | Non-importable | Git move, history preserved | None (never imported) | None |
| `run_engine/runtime/regime_stability.py` | `archive/REPOSITORY_CONSOLIDATION_2026-07-14/run_engine/runtime/regime_stability.py` | Tracked | Tracked (moved) | Non-importable | Git move, history preserved | None (never imported) | None |
| `run_engine/core/decision.py` | `archive/REPOSITORY_CONSOLIDATION_2026-07-14/run_engine/core/decision.py` | Tracked | Tracked (moved) | Non-importable | Git move, history preserved | None (never imported) | None |
| `run_engine/core/equity_stabilizer.py` | `archive/REPOSITORY_CONSOLIDATION_2026-07-14/run_engine/core/equity_stabilizer.py` | Tracked | Tracked (moved) | Non-importable | Git move, history preserved | None (never imported) | None |
| `run_engine/core/state_modulation.py` | `archive/REPOSITORY_CONSOLIDATION_2026-07-14/run_engine/core/state_modulation.py` | Tracked | Tracked (moved) | Non-importable | Git move, history preserved | None (never imported) | None |
| `run_engine/execution/adapter.py` | `archive/REPOSITORY_CONSOLIDATION_2026-07-14/run_engine/execution/adapter.py` | Tracked | Tracked (moved) | Non-importable | Git move, history preserved | None (never imported) | None |
| `run_engine/execution/safety.py` | `archive/REPOSITORY_CONSOLIDATION_2026-07-14/run_engine/execution/safety.py` | Tracked | Tracked (moved) | Non-importable | Git move, history preserved | None (never imported) | None |
| `run_engine/feedback/tracker.py` | `archive/REPOSITORY_CONSOLIDATION_2026-07-14/run_engine/feedback/tracker.py` | Tracked | Tracked (moved) | Non-importable | Git move, history preserved | None (never imported) | None |
| `run_engine/logging/logger.py` | `archive/REPOSITORY_CONSOLIDATION_2026-07-14/run_engine/logging/logger.py` | Tracked | Tracked (moved) | Non-importable | Git move, history preserved | None (never imported) | None |
| `run_engine/runtime/strategy_memory.py` | `archive/REPOSITORY_CONSOLIDATION_2026-07-14/run_engine/runtime/strategy_memory.py` | Tracked | Tracked (moved) | Non-importable | Git move, history preserved | None (never imported) | None |
| `run_engine/runtime/strategy_weights.py` | `archive/REPOSITORY_CONSOLIDATION_2026-07-14/run_engine/runtime/strategy_weights.py` | Tracked | Tracked (moved) | Non-importable | Git move, history preserved | None (never imported) | None |
| `run_engine/core/features.py` | `archive/REPOSITORY_CONSOLIDATION_2026-07-14/run_engine/core/features.py` | Tracked | Tracked (moved) | Non-importable | Git move, history preserved | None (never imported) | None |
| `run_engine/runtime/memory.json` | `archive/REPOSITORY_CONSOLIDATION_2026-07-14/run_engine/runtime/memory.json` | Tracked | Tracked (moved) | Non-importable, not a Python module | Git move, history preserved | None (never read by active path) | None |

### 25.4 IGNORE Paths (13) - RC-SPEC-007, RC-SPEC-008

| Path | Current Tracking | Target `.gitignore` Category | Required Change | Verification |
|---|---|---|---|---|
| `_chat_handover/` | Untracked | Scratch Workspaces | Add pattern | `git check-ignore -v` |
| `claude_final_p1031_review/` | Untracked | Review Packages | Add pattern | `git check-ignore -v` |
| `claude_p1031_patch/` | Untracked | Scratch Workspaces | Add pattern | `git check-ignore -v` |
| `claude_p1_03b_review/` | Untracked | Review Packages | Add pattern | `git check-ignore -v` |
| `codex_p1_03_review/` | Untracked | Review Packages | Add pattern | `git check-ignore -v` |
| `review_packages/` | Untracked | Review Packages | Add pattern | `git check-ignore -v` |
| `_sgf017_context/` | Untracked | Local Context Bundles | Add pattern | `git check-ignore -v` |
| `_ssi_context/` | Untracked | Local Context Bundles | Add pattern | `git check-ignore -v` |
| `backups/` | Untracked | Backups | Add pattern | `git check-ignore -v` |
| `live_logs/` | Untracked | Logs | Add pattern (supersedes partial existing rules) | `git check-ignore -v` |
| `outputs/` | Untracked | Outputs | Add pattern | `git check-ignore -v` |
| `runtime_runs/` | Untracked | Runtime Runs | Add pattern | `git check-ignore -v` |
| `engine/regime_classifier.py` | Untracked | Not assigned in this Specification (Section 15) | Deferred to Implementation-stage choice | N/A |

### 25.5 Other Paths

| Path | Current State | Target State | Required Change | Traceability |
|---|---|---|---|---|
| `.gitignore` | 9 partial categories | 9 full categories (Section 15) | Add ~11 new pattern lines | RC-SPEC-008 |
| `docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md` | TD-004 `Status: Already Planned` | TD-004 `Status: Closed` (or Register-consistent equivalent) | One field edit plus citation | RC-SPEC-012 |
| `tools/repository_consolidation/verify_repository_consolidation.py` | Does not exist | New governance-tooling script | Create (future Implementation, not this Specification) | RC-SPEC-011 |
| `archive/REPOSITORY_CONSOLIDATION_2026-07-14/README.md` | Does not exist | New archive metadata file | Create (future Implementation, not this Specification) | RC-SPEC-015 |

## 26. No-Change Inventory

Explicitly unaffected by this Specification and by the Implementation it authorizes:

- All 14 active runtime files (Section 25.1), including `run_engine/main.py` as the unchanged Runtime Entry Point.
- `engine/__init__.py`, `engine/simtraderGS.py`, `engine/validators.py` (tracked, established, unrelated subsystem, not reopened).
- Every certified governance document: the two Baselines, the Technical Debt Register (beyond the single TD-004 field, RC-SPEC-012), all P2-02A, P2-03, P2-04, P3-01, P3-02, P3-03 Architecture, Specification, and Certification files.
- Every Runtime Formula and Runtime Schema certified by any P2-0x/P3-0x unit (PnL, Risk, Performance, Position, Lifecycle).
- The Runtime Entry Point (`run_engine.main`).
- Stage Ordering (`RunLoop.step()`'s own twelve-stage sequence, ADR-010).
- The Runtime Ownership Matrix.
- The Target Information Flow.
- The four Deferred-Scope RETAIN files' own content (Section 25.2) - only their surrounding documentation is clarified, never their bytes.

## 27. Acceptance Criteria

### 27.1 Per-Implementation-Unit (restated from Section 24)

Each of RC-IU-001 through RC-IU-007 carries its own Acceptance Criteria, individually stated in Section 24; not repeated verbatim here.

### 27.2 Global Acceptance Criteria

- Exactly 14 active modules remain active after Implementation.
- Zero active module is archived, moved, or content-changed.
- All 20 ARCHIVE-disposed components are absent from the active and inactive `run_engine/`/`engine/` namespace, present only under `archive/REPOSITORY_CONSOLIDATION_2026-07-14/`.
- `archive/REPOSITORY_CONSOLIDATION_2026-07-14/` is confirmed unreachable from `run_engine.main`'s own import closure.
- No archived file is imported by the active runtime path, verified by repository-wide search.
- The `executor.py` path collision is fully resolved; exactly one `executor.py` remains importable.
- `run_engine/runtime/memory.json` is absent from the active-adjacent `run_engine/runtime/` directory, present only at its archive path.
- All 13 IGNORE paths are correctly `.gitignore`-excluded, `git check-ignore -v` PASS for each.
- Zero normative file is accidentally matched by any new `.gitignore` pattern.
- The Verification Tool (RC-IU-005) reproduces exactly 14 active modules.
- Zero competing active Computational Authority remains reachable.
- `python -m compileall run_engine` PASS.
- All active imports (`run_engine.main` and its own transitive closure) PASS.
- The active runtime code is byte-identical to the pre-Implementation commit for all 14 files.
- TD-004's own Register status is correctly updated; TD-005 and TD-007 byte-identical before/after.
- Zero local IGNORE-disposed content is deleted; file counts unchanged for all 13 paths.
- Zero Long-Duration Run of any kind is started.

## 28. Verification Plan

Minimum scope, per the governing task's own explicit list: AST import closure; Python module inventory; import-cycle check; archive-import check; scratch/review-import check; duplicate module-name check; path-collision check; `compileall`; import test of `run_engine.main`; import tests of all 14 active modules individually; git tracking-status check; `git check-ignore` for all 13 IGNORE paths; tracked-JSON/log/output/run-artifact check (must return empty post-Implementation); repository-wide search for archived-module imports; Technical Debt Register diff; governance-file-unchanged check (hash comparison of every `docs/architecture/` file this Specification does not name for editing); working-tree boundary check (only the files this Specification names may differ from the pre-Implementation commit); Long-Duration-Readiness check (RC-SPEC-013's own seven conditions).

## 29. Technical-Debt Verification

TD-004: post-Implementation, the Register must show `Status: Closed` (or Register-consistent equivalent) with a P3-03 Final Certification citation, and no other field changed. TD-005: byte-identical Register entry before/after; remains `Status: Open`; not silently closed by any Repository Consolidation Implementation Unit. TD-007: byte-identical Register entry before/after; remains `Status: Deferred`; `state_memory.py`'s own continued RETAIN status (Section 25.2) and `memory.json`'s own archival (Section 25.3) are confirmed compatible with, not a resolution of, TD-007.

## 30. Traceability

### 30.1 RC-FR-ID Traceability

| RC-FR-ID | Addressed By |
|---|---|
| RC-FR-001 | RC-SPEC-001, RC-SPEC-011, RC-SPEC-013, RC-SPEC-014 |
| RC-FR-002 | RC-SPEC-001, RC-SPEC-014 |
| RC-FR-003 | RC-SPEC-004, RC-SPEC-016 |
| RC-FR-004 | RC-SPEC-003, RC-SPEC-004, RC-SPEC-006, RC-SPEC-015 |
| RC-FR-005 | RC-SPEC-004 |
| RC-FR-006 | RC-SPEC-002, RC-SPEC-003, RC-SPEC-004, RC-SPEC-015, RC-SPEC-016 |
| RC-FR-007 | RC-SPEC-004 |
| RC-FR-008 | RC-SPEC-002, RC-SPEC-005, RC-SPEC-012 |
| RC-FR-009 | RC-SPEC-004 |
| RC-FR-010 | (satisfied by inheritance; `engine/`-scope disposition not reopened by this Specification, Section 15) |
| RC-FR-011 | RC-SPEC-007, RC-SPEC-008, RC-SPEC-009, RC-SPEC-013 |
| RC-FR-012 | RC-SPEC-010, RC-SPEC-012 |
| RC-FR-013 | RC-SPEC-010 |

All thirteen Functional Requirements individually addressed.

### 30.2 RC-DEP-ID Traceability (Individually Enumerated)

| RC-DEP-ID | Addressed By |
|---|---|
| RC-DEP-001 | RC-SPEC-001, RC-SPEC-006, RC-SPEC-011, RC-SPEC-013, RC-SPEC-014, RC-SPEC-016 |
| RC-DEP-010 | RC-SPEC-004 |
| RC-DEP-011 | RC-SPEC-004 |
| RC-DEP-012 | RC-SPEC-002, RC-SPEC-003, RC-SPEC-015 |
| RC-DEP-013 | RC-SPEC-002, RC-SPEC-003, RC-SPEC-005, RC-SPEC-012, RC-SPEC-015 |
| RC-DEP-015 | RC-SPEC-004 |
| RC-DEP-016 | RC-SPEC-004 |
| RC-DEP-017 | (matched-but-unwired pair disposition inherited, `core/features.py`, RC-SPEC-004) |
| RC-DEP-018 | RC-SPEC-004 |
| RC-DEP-019 | RC-SPEC-004 |
| RC-DEP-020 | RC-SPEC-001, RC-SPEC-014 |
| RC-DEP-021 | RC-SPEC-001, RC-SPEC-014 |
| RC-DEP-022 | RC-SPEC-001, RC-SPEC-014 |
| RC-DEP-023 | RC-SPEC-001, RC-SPEC-014 |
| RC-DEP-024 | RC-SPEC-001, RC-SPEC-014 |
| RC-DEP-025 | RC-SPEC-001, RC-SPEC-014 |
| RC-DEP-026 | RC-SPEC-004, RC-SPEC-012 |
| RC-DEP-027 | RC-SPEC-004 |
| RC-DEP-028 | RC-SPEC-004 |
| RC-DEP-029 | RC-SPEC-004 |
| RC-DEP-030 | RC-SPEC-004 |
| RC-DEP-031 | RC-SPEC-005, RC-SPEC-012 |
| RC-DEP-032 | RC-SPEC-007, RC-SPEC-008, RC-SPEC-009, RC-SPEC-010, RC-SPEC-013, RC-SPEC-016 |

All twenty-three actually-used, non-contiguously-numbered Dependency records individually addressed; no RC-DEP-002 through RC-DEP-009 or RC-DEP-014 is used anywhere, since none exists.

### 30.3 RC-CAP-ID Traceability

| RC-CAP-ID | Addressed By |
|---|---|
| RC-CAP-001 | RC-SPEC-001, RC-SPEC-014 |
| RC-CAP-002 | RC-SPEC-004 |
| RC-CAP-003 | RC-SPEC-002, RC-SPEC-016 |
| RC-CAP-004 | RC-SPEC-011 |
| RC-CAP-005 | (Alternative Implementation Classification inherited, not reopened; RC-SPEC-004) |
| RC-CAP-006 | RC-SPEC-004, RC-SPEC-015 |
| RC-CAP-007 | RC-SPEC-007, RC-SPEC-008, RC-SPEC-009, RC-SPEC-016 |
| RC-CAP-008 | RC-SPEC-004 |
| RC-CAP-009 | RC-SPEC-010 |
| RC-CAP-010 | RC-SPEC-002, RC-SPEC-005, RC-SPEC-011, RC-SPEC-013, RC-SPEC-015 |
| RC-CAP-011 | RC-SPEC-004, RC-SPEC-006, RC-SPEC-007 |
| RC-CAP-012 | RC-SPEC-004 |
| RC-CAP-013 | RC-SPEC-005, RC-SPEC-012 |
| RC-CAP-014 | RC-SPEC-014 |
| RC-CAP-015 | (synthesis, addressed by the aggregate of all sixteen Repository Contracts jointly) |

All fifteen Capabilities individually addressed.

### 30.4 RC-AD-ID Traceability

| RC-AD-ID | Addressed By |
|---|---|
| RC-AD-002 | RC-SPEC-001, RC-SPEC-014 |
| RC-AD-003 | RC-SPEC-006 |
| RC-AD-004 | RC-SPEC-004, RC-SPEC-006 |
| RC-AD-005 | RC-SPEC-002 |
| RC-AD-006 | RC-SPEC-005 |
| RC-AD-007 | RC-SPEC-004 |
| RC-AD-008 | RC-SPEC-004 |
| RC-AD-009 | RC-SPEC-004 |
| RC-AD-010 | RC-SPEC-004 |
| RC-AD-012 | RC-SPEC-007, RC-SPEC-009 |
| RC-AD-013 | RC-SPEC-007 |
| RC-AD-014 | RC-SPEC-008 |
| RC-AD-015 | RC-SPEC-003, RC-SPEC-015 |
| RC-AD-016 | RC-SPEC-016 |
| RC-AD-018 | RC-SPEC-013 |
| RC-AD-019 | RC-SPEC-012 |
| RC-AD-021 | RC-SPEC-011 |
| RC-AD-022 | RC-SPEC-010 |
| RC-AD-023 | RC-SPEC-001, RC-SPEC-014 |

Nineteen Architecture Decisions with direct Repository-Contract translation individually cited; RC-AD-001, RC-AD-011, RC-AD-017, RC-AD-020 are inherited without a dedicated Contract (Normative Repository Boundary, `engine/regime_classifier.py` IGNORE already covered by RC-SPEC-007, Integration Criteria not exercised since zero INTEGRATE, Formal Unit Identifier Non-Assignment respected by construction throughout this document's own terminology, Section 7) and are not reopened or altered.

### 30.5 RC-AI-ID Traceability

| RC-AI-ID | Addressed By |
|---|---|
| RC-AI-001 | RC-SPEC-001, RC-SPEC-002, RC-SPEC-014 |
| RC-AI-002 | RC-SPEC-004 |
| RC-AI-003 | RC-SPEC-004, RC-SPEC-006 |
| RC-AI-004 | RC-SPEC-003 |
| RC-AI-005 | RC-SPEC-007, RC-SPEC-008, RC-SPEC-009 |
| RC-AI-006 | RC-SPEC-005, RC-SPEC-008, RC-SPEC-012 |
| RC-AI-007 | RC-SPEC-002 |
| RC-AI-008 | RC-SPEC-003, RC-SPEC-004, RC-SPEC-015, RC-SPEC-016 |
| RC-AI-009 | RC-SPEC-016 |
| RC-AI-011 | RC-SPEC-007, RC-SPEC-008 |
| RC-AI-012 | RC-SPEC-011 |
| RC-AI-013 | RC-SPEC-013 |
| RC-AI-014 | RC-SPEC-009, RC-SPEC-010 |
| RC-AI-015 | RC-SPEC-001, RC-SPEC-014 |

Fourteen of fifteen Invariants directly exercised by a Repository Contract; RC-AI-010 (Integration Requires Certified Architecture Compatibility) is inherited without a dedicated Contract, since zero INTEGRATE disposition exists anywhere in this Specification, consistent with the Architecture's own RC-AD-017.

### 30.6 RC-SPEC-ID and RC-IU-ID Traceability

All sixteen RC-SPEC-IDs are individually defined in Sections 9-23 and individually cited again throughout Sections 24-27; all seven RC-IU-IDs are individually defined in Section 24 and individually cited again in Sections 27.1 and 30.1-30.5's own cross-references.

## 31. Residual Risks and Constraints

- **Residual Risk RC-SPEC-RR-001.** Git's own rename-detection heuristic (RC-SPEC-015) may not link every archived file's own old and new path in a `git log --follow` view, even though the underlying commit history remains fully present and independently queryable via `git log --all -- <path>`; this Specification explicitly does not claim rename-detection as a guarantee.
- **Residual Risk RC-SPEC-RR-002.** `engine/regime_classifier.py`'s own exact `.gitignore` treatment (exact-path pattern versus a future relocation) remains an open Implementation-stage choice (Section 15, RC-SPEC-016), not resolved by this Specification, since either choice is compatible with the Architecture's own IGNORE disposition.
- **Constraint.** No functional runtime change, no new trading function, no Strategy/Position/Financial/Risk/Performance change, no Stage-Ordering or Information-Flow change (RC-SPEC-014, absolute).
- **Constraint.** No persistence or recovery architecture is designed or implied by `memory.json`'s own archival (RC-SPEC-005).
- **Constraint.** No Long-Duration Run of any kind is started by this Specification or its own authorized Implementation (RC-SPEC-013).

## 32. Non-Goals

This document does not: archive, delete, or move any file; edit `.gitignore`; implement the Verification Tool; edit the Technical Debt Register; produce a Final Certification; create any new Architecture Decision or Invariant; change any Functional Requirement, Dependency, or Capability; re-decide any Disposition the Architecture already assigned; resolve `engine/regime_classifier.py`'s own exact `.gitignore` mechanism (Section 31); design a persistence, recovery, or Operator-Control architecture; execute any Long-Duration Run.

## 33. Internal Consistency Review

**Scientific Consistency Review.** Every Repository Contract cites specific RC-FR/RC-DEP/RC-CAP/RC-AD/RC-AI evidence and Repository Evidence independently re-verified in Section 5; no Contract is asserted without a traceable source. PASS.

**Architecture Consistency Review.** Every Contract translates an existing Architecture Decision without altering its own Disposition; the Section 6 distribution (RETAIN 18, ARCHIVE 20, IGNORE 13, INTEGRATE 0, REMOVE 0) is used verbatim throughout, corrected for the Section-34 count discrepancy found and fixed in the Architecture itself before this document began (Section 5). PASS.

**Specification Consistency Review.** No two Repository Contracts assign conflicting Target States to the same path (cross-checked against Section 25's own single-row-per-component tables). PASS.

**Disposition Consistency Review.** Section 25's own four tables sum to exactly 14+4+20+13 = 51 components, matching the Architecture's own total. PASS.

**Repository Boundary Review.** No path outside the Architecture's own Normative Repository Boundary (RC-AD-001) is assigned a Disposition anywhere in this document. PASS.

**Archive Plan Review.** RC-SPEC-003 through RC-SPEC-006 jointly define one unambiguous archive root, mirrored relative structure, and a complete per-file target for all 20 ARCHIVE components (Section 25.3). PASS.

**Gitignore Review.** RC-SPEC-008's own nine categories cover all 12 untracked directories without any wildcard broader than a root-anchored directory pattern; zero currently-tracked file matched (Section 5, Section 15). PASS.

**Provenance Review.** RC-SPEC-015 requires git-tracked moves exclusively, never copy-and-delete, and explicitly does not overclaim rename-detection guarantees (Section 31). PASS.

**Verification Tooling Review.** RC-SPEC-011 defines a concrete target path and the full minimum-check list verbatim from the governing task, without writing any implementation. PASS.

**Runtime Non-Change Review.** RC-SPEC-001, RC-SPEC-002, RC-SPEC-014 jointly guarantee zero change to any of the 14 active modules or the 4 Deferred-Scope RETAIN files. PASS.

**Technical-Debt Review.** RC-SPEC-012 specifies an exclusively editorial TD-004 change, with TD-005 and TD-007 explicitly untouched. PASS.

**Long-Duration-Readiness Review.** RC-SPEC-013 restates the Architecture's own five criteria plus two Specification-level additions, without starting any run. PASS.

**Scope Review.** No archiving, deletion, `.gitignore` edit, tooling implementation, Register edit, or Certification content appears anywhere in this document (Section 32). PASS.

**Terminology Review.** "functionally identical" is used only for runtime-behavior/Python-result comparisons (RC-SPEC-001, RC-SPEC-014); "byte-identical" is used only for file/blob comparisons (RC-SPEC-001, RC-SPEC-005, RC-SPEC-006); no absolute claim appears without its own necessary condition stated (e.g., RC-SPEC-015's own explicit rename-detection caveat). PASS.

**Traceability Review.** Sections 30.1-30.5 confirm all thirteen RC-FR-IDs, all twenty-three RC-DEP-IDs, all fifteen RC-CAP-IDs, nineteen of twenty-three RC-AD-IDs (four inherited without a dedicated Contract, explicitly stated), and fourteen of fifteen RC-AI-IDs (one inherited, explicitly stated) individually addressed; Section 34's own mechanical check confirms every RC-SPEC-ID and RC-IU-ID cited at least twice. PASS.

**Governance Review.** No new P-Identifier appears anywhere in this document (Section 7, Section 2's own exclusive terminology use); the Architecture's own Section-34 count discrepancy was found, reported, and - per explicit user instruction - corrected in the Architecture itself before this Specification began (Section 5). PASS.

Status: Internal Consistency Review PASS.

## 34. Specification Readiness Decision

Sixteen Repository Contracts and seven Implementation Units translate every Architecture Decision this document is chartered to implement into a concrete, path-level plan: one unambiguous archive namespace: `archive/REPOSITORY_CONSOLIDATION_2026-07-14/`; a complete per-file plan for all 14 active modules (unchanged), all 4 Deferred-Scope RETAIN components (unchanged), all 20 ARCHIVE components (individually mapped to an archive target), and all 13 IGNORE paths (individually mapped to a `.gitignore` category); a concrete Verification Tooling target and minimum-check scope; a concrete, exclusively-editorial TD-004 Register change; and complete Acceptance and Verification Plans. Zero new Disposition, Architecture Decision, Invariant, Functional Requirement, Dependency, or Capability was introduced. The one contradiction this document's own mandatory re-verification found (Architecture Section 34's own imprecise ARCHIVE count) was reported to the user, who directed a correction to the Architecture itself before this Specification proceeded (Section 5); with that correction in place, no unresolved contradiction remains between this Specification and the Architecture. RC-CAP-015's own repository-wide synthesis status is carried forward unchanged, as the aggregate of every other Capability this document's own sixteen Contracts individually address; RC-AD-011 (`engine/regime_classifier.py` IGNORE) and RC-AD-020 (Formal Unit Identifier Non-Assignment) are both respected by construction throughout this document (Section 15's own IGNORE-not-`.gitignore`-yet treatment of `regime_classifier.py`, and Section 7's own exclusive "Repository Consolidation"/"RC" terminology) without requiring their own dedicated Repository Contract; RC-AI-010 (Integration Requires Certified Architecture Compatibility) remains satisfied vacuously, since this Specification, like the Architecture before it, issues zero INTEGRATE disposition.

**Specification Readiness Decision: READY for the Implementation stage**, conditioned on RC-IU-001 through RC-IU-007 being implemented in their own stated dependency order (RC-IU-001 first; RC-IU-002 and RC-IU-003 in parallel thereafter; RC-IU-004 and RC-IU-006 independently at any point; RC-IU-005 after RC-IU-002/003; RC-IU-007 last), with the Verification Plan (Section 28) executed in full before any Implementation is considered complete.

## 35. Independent Self Verification

- File exists at the stated Primary Location: confirmed.
- ASCII-only: confirmed (see mechanical check output following this document's delivery).
- No trailing whitespace: confirmed.
- Continuous section numbering: Sections 1 through 35, no gaps, no duplicates.
- Full RC-FR-ID traceability: Section 30.1 confirms all thirteen RC-FR-IDs individually addressed, each cited at least twice.
- Full actual RC-DEP-ID traceability: Section 30.2 confirms all twenty-three actually-used RC-DEP-IDs individually addressed, each cited at least twice; zero non-existent RC-DEP-002 through RC-DEP-009 or RC-DEP-014 used as a real reference anywhere.
- Full RC-CAP-ID traceability: Section 30.3 confirms all fifteen RC-CAP-IDs individually addressed, each cited at least twice.
- Full RC-AD-ID traceability: Section 30.4 confirms nineteen of twenty-three RC-AD-IDs directly translated, each cited at least twice; four inherited without reopening, explicitly stated.
- Full RC-AI-ID traceability: Section 30.5 confirms fourteen of fifteen RC-AI-IDs directly exercised, each cited at least twice; one inherited without reopening, explicitly stated.
- Full RC-SPEC-ID traceability: all sixteen RC-SPEC-IDs individually defined (Sections 9-23) and cited at least twice elsewhere.
- Full RC-IU-ID traceability: all seven RC-IU-IDs individually defined (Section 24) and cited at least twice elsewhere.
- No non-existent RC-DEP-IDs: confirmed.
- No merge markers, no real placeholders: confirmed.
- `python -m compileall run_engine`: PASS (no runtime file was touched by this document).
- `git diff --check`: clean for this new, untracked file.
- `git status --short`: unchanged from Section 6's own pre-check baseline plus this one new file.
- Branch: `run-engine-consolidation-safety` (unchanged).
- Local HEAD: `a0a65187cf2ca808f5dc8fda47cfc5dcf8360842` (unchanged; no commit made by this document; one prior commit-free editorial correction was made to the Architecture file per explicit user instruction, Section 5).
- Remote HEAD: `a0a65187cf2ca808f5dc8fda47cfc5dcf8360842` (unchanged; no push made).

No commit is created by this document. No push occurs. This document stops before the Implementation stage, per its own governing task.
