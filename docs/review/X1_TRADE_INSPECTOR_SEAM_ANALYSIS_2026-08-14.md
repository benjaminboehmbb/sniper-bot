# X1 Trade Inspector Seam Analysis — 2026-08-14

Status: **COMPLETE — ANALYSIS ONLY**

Branch: `codex/x1-trade-inspector-seam-analysis-2026-08-14`

Analyzed commit: `681cf19de9f1e186f39e7b6e7de462885c53d3fe`

Production target: `tools/trade_inspector/inspect_trades.py`

Production SHA-256: `d8b6bc6ab6fdee30f01e5c058e165266c73c1ba64c2563665e0cd2df1f041b2f`

## Decision

The Trade Inspector can be modularized incrementally, but not as a broad split. Its internal function-call graph is acyclic, which permits leaf-first extraction. The existing characterization gate protects the row-building core and archive-intake failure path, but it does not yet protect most aggregate, feature, signal-discovery, cross-archive, or export behavior.

The first technically justified extraction is a small compatibility-primitives seam. High-level feature clusters must remain in place until each receives deterministic input/output fixtures and golden hashes.

No production extraction, import change, behavior change, or file move is authorized by this analysis.

## Safety boundary

- Analysis used the Python AST and tracked source at the analyzed commit.
- No Trade Inspector function or CLI command was executed against repository data.
- No market data, runtime archive, label registry, or generated artifact was read or changed.
- `tools/trade_inspector/inspect_trades.py` remained byte-identical.
- IU4, Live-L1, Exchange, Live, inputs, strategies, policies, and gates remained unchanged.
- The foreign untracked file `scripts/build_rcc002_spec_bundle.py` was not read, modified, staged, or included.

## Structural census

| Measure | Observed value |
|---|---:|
| Production lines | 3,672 |
| Top-level functions | 89 |
| Internal function-call edges | 240 |
| Multi-function strongly connected components | 0 |
| Largest strongly connected component | 1 |
| Module-level configuration/constant bindings | 11 |
| CLI options | 26 |
| `safe_text` internal callers | 39 |
| `safe_float` internal callers | 27 |
| `write_csv_rows` internal callers | 13 |

The graph contains no recursion or mutual-call cycle among top-level functions. This is the main evidence supporting a staged extraction. The primary coupling problem is not cyclicity; it is the high fan-in of compatibility helpers and the high fan-out of `main()` and `build_ml_row()`.

## Current behavioral protection

The hermetic characterization module is:

`tests/trade_inspector/test_inspect_trades_characterization.py`

Its direct anchors and their static internal call closure cover 36 of the 89 functions. The protected closure includes parsing, entry/exit matching, path and counterfactual calculations, diagnosis/confidence, regime extraction, trade identity/family, row construction, summary output, and fail-closed archive intake.

The remaining 53 functions are not represented by a deterministic hermetic output contract. Important unprotected groups include:

- aggregate CSV construction;
- ML targets and split evaluation;
- feature catalog/model-ready conversion;
- leakage audit;
- feature importance and stability;
- signal and pair discovery;
- multi-archive loading and all cross-archive exports;
- global-trade and ML-dataset exports;
- the P79A built-in regression route;
- label-registry persistence;
- detailed trade and aggregate presentation routes.

Static reachability is not line or branch coverage. The 36/89 figure is a conservative architectural map of the currently exercised semantic chain, not a coverage percentage.

## Cohesive regions at the analyzed commit

| Region | Lines | Functions | Function LOC | Current protection | Extraction status |
|---|---:|---:|---:|---|---|
| Foundation/parsing/matching | 32–202 | 13 | 147 | Strong for parsers/matching; helper edge cases partial | Candidate only after compatibility matrix is retained |
| Path and diagnosis | 205–608 | 7 | 391 | Strong representative row fingerprint | Eligible after primitives seam |
| Regime, labels, IDs, row builder | 613–921 | 12 | 282 | Row path strong; registry persistence weak | Split row logic from persistence before extraction |
| Presentation and aggregate intelligence | 924–1406 | 15 | 454 | Summary only | Blocked on snapshot/golden-output tests |
| Aggregate CSV and ML dataset basics | 1409–1642 | 9 | 217 | No hermetic file hashes | Blocked |
| Feature/leakage/importance/stability | 1685–2300 | 14 | 517 | No hermetic golden dataset | Blocked |
| Signal discovery | 2303–2519 | 6 | 205 | No hermetic discovery baseline | Blocked |
| Cross-archive/global exports | 2526–3110 | 7 | 573 | No hermetic multi-archive baseline | Blocked |
| ML export | 3113–3175 | 2 | 62 | No hermetic file hash | Blocked |
| Archive and built-in validation | 3180–3466 | 3 | 282 | Archive intake protected; P79A route artifact-bound | Archive intake eligible separately |
| CLI dispatcher | 3470–3668 | 1 | 199 | Summary route only | Keep as façade until last |

## Existing `common` helpers are not drop-in seams

The repository already has `tools/trade_inspector/common/`, and it should remain the preferred home for genuinely shared technical helpers. However, the monolith's current helpers are not behaviorally interchangeable with those modules:

| Current monolith behavior | Existing common behavior | Consequence |
|---|---|---|
| `safe_int("1.0", default)` returns the default | `common.utils.to_int("1.0", default)` returns `1` | Replacing the function would change row semantics |
| `group_rows` places empty/`None` keys in `UNKNOWN` | `common.collections.group_by` omits empty keys | Aggregate counts would change |
| `write_csv_rows([], path)` writes an empty file | `common.io.write_csv` requires explicit fields and writes a header | Empty-export bytes would change |
| `build_trade_id` uses a human-readable timestamp/side/symbol ID | `common.ids.stable_hash_id` uses a truncated JSON hash | IDs and downstream joins would change |

Therefore, “reuse common” requires explicit semantic migration tests; it is not a mechanical import replacement. Altering the existing shared helpers would also affect many V9–V17 modules and would expand the change beyond the approved Trade Inspector seam.

## Recommended extraction sequence

Module names below are implementation candidates, not new architectural authority.

### S1 — Compatibility primitives

Candidate functions:

- `safe_text`
- `safe_float`
- `safe_int`
- `parse_ts`
- `ts_key`

Recommended destination: `tools/trade_inspector/inspection_primitives.py`.

Reason: these functions are pure, form the highest-fan-in dependency layer, and are exercised by the current characterization gate. Keeping their exact implementations separate avoids changing the already-used `common` contracts. `inspect_trades.py` must import and re-expose the same names so existing import consumers remain compatible.

Acceptance boundary:

- production CLI and defaults unchanged;
- representative row SHA-256 remains `54fc961343d463d4e55d6489c70ec9ffcf3892acc9155b45b95e5f9408a2ce24`;
- 6/6 characterization tests and 170/170 regression tests pass;
- add an explicit conversion matrix for `None`, empty string, integer string, decimal string, invalid string, and boolean;
- one extraction commit only.

### S2 — Archive-intake validation

Candidate functions:

- `count_valid_jsonl`
- `run_archive_intake_validation`

Reason: the pair is cohesive, fail-closed, and already has a hermetic negative-path test. Before extraction, add one complete PASS fixture and assert exact warning/error ordering.

### S3 — Path and diagnosis core

Candidate functions and binding:

- `FUTURE_WINDOWS_MIN`
- `score_band`
- `signed_diagnosis`
- `trade_pnl_from_price`
- `quality_flags`
- `calculate_trade_path`
- `calculate_counterfactuals`
- `compute_quality_score`
- `interpretation_flags`
- `compute_diagnosis`
- `compute_confidence_layer`

Reason: this is a cohesive mostly-pure scientific computation block and is strongly represented by the row fingerprint. Add explicit long, short, missing-path, zero-PnL, and invalid-duration fixtures before moving it.

### S4 — Regime/identity/row assembly

Candidate functions:

- `build_regime_index`
- `extract_regime_features`
- `compact_trade_time`
- `chart_time`
- `build_trade_id`
- `build_trade_family`
- `build_ml_row`
- `build_rows`

Keep label registry load/save/assignment in an I/O-oriented module rather than mixing persistence into the row builder. Preserve `build_ml_row` field insertion order because CSV field order currently derives from the first row.

### S5 and later — Add gates before moving

Do not extract aggregate, ML feature, leakage, signal discovery, cross-archive, global export, or CLI routing regions yet. First add one hermetic fixture per public CLI route and bind:

- exit code;
- ordered stdout where human output is contractual;
- exact output filename set;
- CSV header order;
- row counts;
- SHA-256 for each generated artifact;
- fail-closed behavior for missing/invalid inputs.

Only then extract one cohesive region per commit.

## CLI compatibility rule

`tools/trade_inspector/inspect_trades.py` should remain the stable command-line façade throughout modularization. Its 26 option names, default paths, dispatch precedence, exit codes, example commands, stdout headings, output filenames, and update-label-registry behavior must not drift incidentally.

Moving the argument parser or changing dispatch order is a final-stage change, not part of S1–S4.

## Explicit non-goals

- no rewrite to classes or a plugin framework;
- no combining V8–V17 build tools with the inspection CLI;
- no renaming output columns or files;
- no migration from human-readable trade IDs to hashes;
- no replacement of custom helpers solely to reduce duplication;
- no statistical/model change;
- no deletion or archive decision;
- no IU4, Live-L1, Exchange, or Live enablement.

## Gate conclusion

**GO** for a separately authorized S1 compatibility-primitives extraction.

**NO-GO** for broad modularization or moving the 53 unprotected functions before route-specific deterministic tests exist.

The source remains unchanged by this analysis.
