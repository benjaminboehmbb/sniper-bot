# X1 Script Inventory and Quality Audit — 2026-08-14

Status: **COMPLETE (documentation-only, fail-closed)**

Branch: `codex/x1-script-inventory-quality-audit-2026-08-14`

Audited commit: `af79a6b3298f58b53d3a742e929448e76d64b960`

Scope: every Git-tracked Python file under `scripts/`, `tools/`, and `live_l1/tools/`

## Executive decision

The tracked X1 script estate is not suitable for a broad cleanup. All 405 tracked Python files were mechanically inventoried and parsed, but the evidence supports **zero immediate deletions or archive moves**.

Three bounded follow-ups are justified:

1. isolate and test the `tools/trade_inspector/inspect_trades.py` monolith before any modularization;
2. turn the 22 import-executing `scripts/state_research/` programs into explicit, documented entry points before deciding whether the historical cohort belongs in an archive;
3. retire or harden `tools/download_binance_1min.py` only after its consumers and data products are proven, because its error-continuation behavior can produce incomplete output.

The current IU4, RCC-002, repository-governance, and Live-L1 toolchains remain active and untouched. This audit does not authorize runtime changes, input changes, archive operations, or gate weakening.

## Safety boundary

- Inventory source was `git ls-files`; filesystem-wide discovery was deliberately not used.
- The foreign untracked file `scripts/build_rcc002_spec_bundle.py` was not read, modified, staged, or included.
- No script was executed as part of the audit.
- No source file, input, runtime artifact, gate, or policy was changed.
- Existing dated audit utilities were inspected but not run because they use filesystem traversal and fixed output paths that would overwrite historical evidence.
- Exact-duplicate detection found no substantive duplicates. The only duplicate hashes were empty package `__init__.py` files.

## Complete tracked inventory

| Cohort | Files | LOC | Static disposition | Rationale |
|---|---:|---:|---|---|
| `scripts/` root | 106 | 17,960 | **KEEP / MAP BEFORE REVIEW** | Mixed Goldstandard generation, research, post-GS, downloader, orchestration, and launch entry points; no safe cohort-wide disposition. |
| `scripts/rcc002/` | 9 | 4,593 | **KEEP — GOVERNED GATES** | Normative RCC-002 validators/gates with extensive evidence references and regression coverage. |
| `scripts/state_research/` | 43 | 6,182 | **REVIEW COHORT — NOT ARCHIVE-VALIDATED** | Historical step pipeline; 22 files execute work during import, no matching tests were found, and no cohort entry-point map exists. |
| `tools/` root | 67 | 11,884 | **KEEP / MAP BEFORE REVIEW** | Mixed GS controls, phase audits, data utilities, test runners, and repository-audit tools. |
| `tools/repository_consolidation/` | 1 | 446 | **KEEP — GOVERNANCE** | Repository consolidation verifier with an explicit evidence contract. |
| `tools/ssi/` | 104 | 7,864 | **KEEP — DOCUMENT ENTRY POINTS** | Deliberately modular processor/renderer/persistence architecture; static imports resolve across the package. Missing cohort README/test map is a documentation gap, not dead-code proof. |
| `tools/trade_inspector/` | 53 | 16,108 | **KEEP — QUALITY REVIEW PRIORITY** | Strong documentation history, but no matching tests found and one 3,672-line module concentrates most logic. |
| `live_l1/tools/` | 22 | 7,479 | **KEEP — ACTIVE OPERATIONAL/IU4** | Current runtime, monitoring, replay, evidence, and test tooling with current documentation/test bindings. |
| **Total** | **405** | **72,516** |  |  |

LOC uses newline counts at the audited commit. By top-level scope: `scripts/` 28,735; `tools/` 36,302; `live_l1/tools/` 7,479.

The path rules and counts above form the complete inventory membership: every tracked `*.py` below the three declared roots belongs to exactly one row. This audit intentionally avoids a 405-row filename dump that would obscure the decisions; Git at the audited commit is the canonical member list.

## Mechanical quality results

| Check | Result |
|---|---:|
| Tracked Python files parsed with Python AST | 405/405 |
| Syntax errors in audit scope | 0 |
| Substantive byte-identical duplicates | 0 |
| `scripts/` files with `if __name__ == "__main__"` | 135/158 |
| `tools/` files with main guard | 124/225 |
| `live_l1/tools/` files with main guard | 19/22 |
| `scripts/state_research/` files without main guard and with direct import-time work | 22/43 |
| Files resolved as imports from other tracked Python | `scripts/`: 0; `tools/`: 81; `live_l1/tools/`: 13 |

Import resolution is a conservative static signal, not proof of use or non-use. Shell calls, documentation commands, scheduled tasks, and external consumers are not fully represented by Python imports.

Documentation/test-name evidence by cohort:

| Cohort | Tracked Markdown files mentioning cohort | Matching tracked test files found |
|---|---:|---:|
| `scripts/rcc002/` | 41 | 7 |
| `live_l1/tools/` | 48 | 13 |
| `tools/trade_inspector/` | 37 | 0 |
| `tools/ssi/` | 14 | 0 |
| `scripts/state_research/` | 7 | 0 |

“0 matching test files” means no test filename/content match was found in tracked test paths. It does not rule out self-checks embedded in a tool or external test harnesses.

## Findings and dispositions

### Q1 — Trade Inspector monolith (high priority)

`tools/trade_inspector/inspect_trades.py` contains 3,672 lines, 89 functions, and 408 static control-flow nodes. Thirteen tracked documents reference it, but no matching tracked test was found. Its size makes review, failure isolation, and regression protection expensive.

Disposition: **KEEP and test first**. Extract only after characterization tests pin input parsing, entry/exit matching, evidence generation, CLI behavior, and deterministic output hashes. A “split by file size” rewrite is not authorized.

### Q2 — State-research import side effects (high priority)

Twenty-two of the 43 files in `scripts/state_research/` have neither a main guard nor an inert module body. They read inputs, transform frames, print, and/or write reports at import time. Representative file `build_step18_core_pipeline.py` creates `reports/step18`, reads `live_logs/passive_shadow_risk_snapshots.csv`, and writes multiple CSVs directly from module scope.

Affected set:

- `analyze_step18_buckets.py`
- `analyze_step18_clusters.py`
- `analyze_step18_predictive_power.py`
- `analyze_step18_trade_lifetime.py`
- `analyze_step19B_real_exit_replay.py`
- `analyze_step19B_threshold_sweep.py`
- `analyze_step19_blocked_trades.py`
- `analyze_step19_blocked_winners.py`
- `analyze_step19_dynamic_exit_replay.py`
- `analyze_step19_entry_gate.py`
- `analyze_step19_gate_quality.py`
- `analyze_step19_risk_escalation.py`
- `analyze_step19_shadow_gate.py`
- `analyze_step19_shadow_gate_replay.py`
- `analyze_step19_threshold_fine.py`
- `analyze_step19_threshold_sweep.py`
- `analyze_step20C_live_replay.py`
- `analyze_step20D_dynamic_exposure_scaling.py`
- `analyze_step20D_sensitivity.py`
- `analyze_step20E_true_dynamic_exposure_replay.py`
- `analyze_step20_position_sizing_replay.py`
- `build_step18_core_pipeline.py`

Disposition: **REVIEW COHORT, not archive-validated**. First record required inputs, expected outputs, producing phase, and last authoritative evidence. Then add explicit `main()` boundaries without changing calculations. Only a later, separately authorized provenance review may recommend archival.

### Q3 — Competing Binance download paths (medium/high priority)

The two downloader files are not duplicates:

- `scripts/download_btcusdt_1m_binance_bulk.py` downloads official monthly/daily archives, validates published checksums when available, and preserves raw ZIPs.
- `tools/download_binance_1min.py` calls REST endpoints into CSV chunks and merges them. On exhausted fetch errors it logs a warning, advances the cursor, and continues; the final command can therefore complete with gaps unless a separate validator catches them.

Disposition: **KEEP the checksum-preserving bulk downloader as the reproducible path**. Mark the REST downloader as `REVIEW_FOR_DEPRECATION_OR_FAIL_CLOSED_HARDENING`; do not remove it until all consumers and historical outputs are mapped. If retained, any skipped interval must make the run non-zero and the output manifest must enumerate completeness.

### Q4 — SSI entry-point discoverability (medium priority)

The 104-file SSI tree is internally modular. The three 45-line runner modules are intentional orchestrators, not dead code. The quality gap is discoverability: no cohort README or authoritative entry-point/test matrix was found.

Disposition: **KEEP**. Add one architecture/entry-point document and a minimal package-level contract suite before refactoring. Do not collapse processor/renderer/persistence layers merely to reduce file count.

### Q5 — Dated audit utilities (medium priority)

`tools/dependency_entrypoint_audit.py`, `tools/repository_usage_audit.py`, and `tools/inspect_dead_code_candidates.py` encode the June 6 review method. They use fixed dated targets/output paths and filesystem traversal rather than a tracked-file boundary.

Disposition: **KEEP as historical methodology, do not rerun unchanged**. A future replacement should require an explicit audited commit, consume `git ls-files`, write to a caller-selected output path, refuse overwrite by default, and emit machine-readable hashes. This audit deliberately did not create a fourth overlapping audit utility.

### Q6 — Root script/tool estates (medium priority)

The 106 root scripts and 67 root tools contain several distinct lifecycles: GS generation/selection, post-GS experiments, current launch controls, data preparation, phase-numbered audits, and repository governance. Name similarity alone is insufficient for cleanup, and no substantive exact duplicates were found.

Disposition: **KEEP pending lifecycle map**. The next inventory iteration should label each root file `ACTIVE_ENTRYPOINT`, `ACTIVE_LIBRARY`, `REPRODUCIBILITY_REFERENCE`, `HISTORICAL_EXPERIMENT`, or `ARCHIVE_CANDIDATE`, with a document/test/consumer citation for every non-active label.

## Historical evidence applied

- `docs/inventory/P25B_DEAD_CODE_CANDIDATE_DECISION_2026-06-06.md` rejected broad cleanup and required manual reference checks.
- `docs/inventory/P25C_ARCHIVE_VALIDATED_DEAD_CODE_2026-06-06.md` archived only one validated Live-L1 file; it is not precedent for cohort deletion.
- The existing June 6 structure/usage/entry-point reports are historical snapshots, not current authority for deletion.
- Repository-consolidation evidence explicitly left top-level `scripts/`, most `tools/`, and `live_l1/` outside that consolidation decision.

## Bounded independent review bundle

If an external read-only Claude/Antigravity review is separately authorized, limit it to the following five tracked files and bind the response to these hashes:

| File | SHA-256 | Review question |
|---|---|---|
| `tools/trade_inspector/inspect_trades.py` | `d8b6bc6ab6fdee30f01e5c058e165266c73c1ba64c2563665e0cd2df1f041b2f` | What characterization seams allow safe modularization without output drift? |
| `tools/trade_inspector/build_v13a_hypothesis_intelligence_engine.py` | `0d273db82128b37c393462e87b0fce97583052c758ffcb3a758e6864931b135a` | Which patterns should be shared with, or remain separate from, the monolith? |
| `scripts/state_research/build_step18_core_pipeline.py` | `05bbf39e66bd87ede3902165c070847f25b86bee9c31f6d52a212b5f7d7a3ae9` | How can execution be enclosed behind an entry point with zero calculation drift? |
| `scripts/state_research/analyze_step20E_true_dynamic_exposure_replay.py` | `14667ea1f44d380e807523a0a71402b3786eeafff306d7ee3e4a8f44d29438ee` | What input/output contract is needed to preserve this historical replay? |
| `tools/download_binance_1min.py` | `4777d0454a35a0fa1408d16d0b10cdf25f1b280b2311eefab15fe7c52085e2e9` | Which failure paths permit silent gaps, and what fail-closed contract is minimal? |

Review constraints: read-only; no inputs or artifacts; no secrets; no claims about files outside the bundle; no gate weakening; distinguish observed facts from recommendations; return file/line evidence and an explicit “no deletion decision” unless provenance is independently proven.

## Ordered next work on X1

1. **Trade Inspector characterization gate** — add deterministic tests around current behavior before modularization.
2. **State Research provenance/entry-point map** — document all 43 files and contain the 22 import-time executors without changing math.
3. **Downloader completeness gate** — map consumers, then harden or deprecate the REST downloader.
4. **SSI entry-point and contract map** — documentation plus minimal integration tests.
5. **Root lifecycle inventory** — per-file evidence labels; archive review only after citations are complete.

No item above enables IU4 ENFORCED, Exchange, or Live. Those remain separately gated and locked.

## Verification performed

- tracked scope count: 405 files;
- AST parse: 405 passed, 0 failed;
- exact SHA-256 duplicate grouping: no substantive duplicates;
- static main-guard/import/complexity census completed;
- tracked Markdown/test-reference census completed;
- report-only diff required before commit.
