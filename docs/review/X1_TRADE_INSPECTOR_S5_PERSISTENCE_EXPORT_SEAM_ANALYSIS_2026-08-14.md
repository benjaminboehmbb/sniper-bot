# X1 Trade Inspector S5 Persistence and Export Seam Analysis — 2026-08-14

Status: **COMPLETE — ANALYSIS ONLY**

Branch: `codex/x1-trade-inspector-s5-persistence-export-seam-analysis-2026-08-14`

Analyzed commit: `665299d189a23f337166fa1991f44330bfd6d95a`

Production target: `tools/trade_inspector/inspect_trades.py`

Production SHA-256: `48a8d77dac975c0a8127c0b85eae9fff37d64583a86aaadd95dffdd8bcf5d229`

## Decision

Persistence and export must not be extracted as one broad module. The current façade contains two small, technically separable persistence seams and thirteen high-level export routes that still mix computation, artifact serialization, directory enumeration, Markdown generation, and human output.

The first justified work is a deterministic S5 characterization gate for:

1. human-label and label-registry persistence;
2. generic CSV serialization;
3. the standalone raw ML CSV route.

Only after that gate passes should label persistence and generic CSV persistence be extracted in separate commits. Every aggregate, ML, feature, discovery, global, cross-archive, and multi-archive exporter still requires its own hermetic artifact gate before it can move.

No production extraction, import change, behavior change, output write, or data read is authorized by this analysis.

## Safety boundary

- Analysis used tracked source text and the Python AST at the analyzed commit.
- No Trade Inspector CLI command or exporter was executed against repository data.
- No archive, market data, runtime input, label registry, output directory, or generated artifact was read or changed.
- `tools/trade_inspector/inspect_trades.py` remained byte-identical.
- IU4, Live-L1, Exchange, Live, inputs, strategies, policies, and gates remained unchanged and locked.
- The foreign untracked file `scripts/build_rcc002_spec_bundle.py` was not read, modified, staged, or included.

## Structural census

| Measure | Observed value |
|---|---:|
| Façade lines | 2,817 |
| Façade top-level functions | 63 |
| Functions named `export_*` | 14 |
| Export-function LOC | 1,007 |
| CLI export routes | 13 |
| Direct callers of `write_csv_rows` | 13 |
| Label-list/registry region LOC | 74 |
| High-level routes producing CSV | 13 |
| Routes also producing Markdown | 5 |
| Statically named route artifacts in isolated directories | 108 |

The 108 artifacts comprise 103 CSV files and five Markdown summaries. This count includes all fixed group, pair, target, split, manifest, and summary outputs created by one invocation of every export route in a fresh isolated directory.

## Small persistence seams

### Label persistence

Candidate functions:

- `load_human_labels`;
- `load_label_registry`;
- `save_label_registry`;
- `assign_human_labels`.

This region is cohesive and acyclic. It depends downward on S1 compatibility primitives and on S4 `build_trade_id`; no S4 function depends on registry persistence.

Current behavior that must be bound before extraction:

- missing human-label file raises `FileNotFoundError`;
- blank/comment labels are ignored and accepted labels are lowercased;
- non-ASCII, longer-than-eight-character, space-containing, duplicate, and empty label lists fail;
- a missing registry returns `{}`;
- incomplete registry rows are ignored, labels are lowercased, and later duplicate trade IDs overwrite earlier rows;
- registry save creates parent directories, always writes the fixed two-column header, and sorts output by trade ID;
- assignment preserves existing mappings, rejects duplicate assigned labels, allocates configured labels in list order to sorted trade IDs, and uses deterministic `auto_label_*` fallbacks.

The current summary CLI test indirectly exercises missing-registry loading and deterministic assignment, but it does not write or fingerprint a registry artifact.

### Generic CSV serialization

Candidate function:

- `write_csv_rows`.

It is a leaf persistence primitive with 13 direct callers. Its behavior is not interchangeable with a generic shared writer:

- parent directories are created;
- empty input creates a zero-byte file with no header;
- non-empty field order comes only from the first row's insertion order;
- later missing fields serialize as empty cells;
- later extra fields use the default `csv.DictWriter` failure behavior;
- writes go directly to the final path without temporary-file replacement.

The zero-byte empty export and first-row schema authority are material contracts. They must not be silently “improved” during extraction.

### Raw ML CSV route

Candidate function after its own route gate:

- `export_ml_csv`.

This function intentionally differs from `write_csv_rows`: it creates the parent directory, rejects empty rows with `ValueError`, does not create the output file in that empty case, and prints two completion lines after a successful write. Refactoring it to call `write_csv_rows` during extraction would risk changing this contract and is therefore not a mechanical cleanup.

## High-level route inventory

| CLI route | Function | Artifact set in a fresh directory | Current deterministic artifact gate |
|---|---|---:|---|
| `--export-ml-csv` | `export_ml_csv` | 1 CSV | None |
| `--export-aggregate-csv-dir` | `export_aggregate_csvs` | 12 CSV | None |
| `--export-ml-dataset-dir` | `export_ml_dataset` | 5 CSV | None |
| `--export-feature-prep-dir` | `export_feature_preparation` | 6 CSV | None |
| `--export-leakage-audit-dir` | `export_leakage_audit_dataset` | 7 CSV | None |
| `--export-feature-importance-dir` | `export_feature_importance` | 11 CSV | None |
| `--export-feature-stability-dir` | `export_feature_stability` | 3 CSV | None |
| `--export-signal-discovery-dir` | `export_predictive_signal_discovery` | 19 CSV | None |
| `--export-global-trades-dir` | `export_global_trade_database` | 2 CSV + 1 Markdown | None |
| `--export-cross-archive-root-cause-dir` | `export_cross_archive_root_cause` | 3 CSV + 1 Markdown | None |
| `--export-cross-archive-feature-importance-dir` | `export_cross_archive_feature_importance` | 11 CSV + 1 Markdown | None |
| `--export-cross-archive-signal-discovery-dir` | `export_cross_archive_signal_discovery` | 19 CSV + 1 Markdown | None |
| `--export-multi-archive-loader-dir` | `export_multi_archive_loader` | 4 CSV + 1 Markdown | None |

The built-in V7H regression path validates selected row, signal, global-ID, and root-cause counts. It does not invoke these exporters and does not bind filenames, bytes, schemas, Markdown, stdout, or partial-write behavior.

## Coupling findings

### High-level exporters mix computation and persistence

The routes are not thin wrappers. They construct targets, feature catalogs, encoded model rows, leakage partitions, importance/stability measures, discovery groups, archive identities, manifests, and statistical-warning fields immediately before writing. Moving all exporters together would create a new 1,000-LOC module with the same mixed responsibilities.

### Schema order is data dependent

`write_csv_rows` and `export_ml_csv` derive fieldnames from the first row. Split or filtered outputs with no rows become zero-byte files under `write_csv_rows`, so they have no header from which a schema can be reconstructed. S4 protects the main 127-field row order, but it does not protect the many derived-row insertion orders.

### Output listing depends on directory contents

Most exporters print a sorted `glob()` of the output directory. Exact stdout therefore depends on whether unrelated files already exist. Route characterization must use a new empty temporary directory and separately test pre-existing-file behavior if that behavior is to remain contractual.

### Direct final-path writes are non-atomic

CSV and Markdown files are opened directly at their final paths. A mid-route exception can leave a partial artifact set, and a later-row schema mismatch can leave a partially written CSV. This is current behavior, not authorization to change it. Atomic output would require a separate functional requirement and migration gate.

### Cross-archive failure semantics differ

`export_multi_archive_loader` records per-archive load failures into an errors CSV and continues building infrastructure artifacts. The cross-archive routes assembled by `main()` collect load errors and terminate with `SystemExit` before export. These are distinct contracts and must not be collapsed during modularization.

## Required S5 characterization gate

The next gate should use only synthetic rows and temporary directories. It should bind exact bytes and SHA-256 values, not merely parsed CSV content.

### Fixture A — human-label list

- accepted comments, blanks, case normalization, and ordering;
- each validation failure class and exact exception type/message;
- missing and all-ignored files.

### Fixture B — label registry

- missing registry;
- incomplete rows and duplicate trade IDs;
- exact saved bytes, fixed header, newline format, sorted order, and empty-registry bytes;
- deterministic assignment with existing, configured, exhausted, and duplicate-label states;
- round-trip semantic and byte fingerprints.

### Fixture C — generic CSV writer

- zero-row output;
- one row with an intentional field order;
- multiple rows with missing fields;
- later extra fields and the resulting exception/partial-file state;
- parent-directory creation and overwrite behavior;
- exact bytes and SHA-256 for every outcome.

### Fixture D — raw ML CSV exporter

- one complete S4 row, preserving the 127-field header order;
- exact artifact SHA-256 and ordered stdout;
- empty rows: parent exists, output file absent, `ValueError` unchanged;
- overwrite behavior.

Acceptance boundary:

- no production change in the gate commit;
- package and direct-script behavior unchanged;
- all new persistence fingerprints pass;
- existing S1–S4 golden fingerprints remain unchanged;
- focused Trade Inspector tests and all 170 regression tests pass;
- only then may extraction be separately authorized.

## Recommended extraction sequence

### S5A — Label persistence

Recommended destination: `tools/trade_inspector/label_registry.py`.

Move the four label functions unchanged and re-export them through `inspect_trades.py`. Preserve default paths and `--update-label-registry` routing in the façade.

### S5B — CSV persistence primitive

Recommended destination: `tools/trade_inspector/csv_persistence.py`.

Move only `write_csv_rows` unchanged and re-export it through the façade. Do not simultaneously rewrite `export_ml_csv` or any high-level route.

### S5C — Raw ML CSV route

After its route-specific gate, move `export_ml_csv` in a separate commit while preserving its distinct empty-input and stdout behavior.

### S5D and later — One route family at a time

Suggested order after route-specific gates:

1. aggregate CSV export;
2. ML dataset basics;
3. feature preparation and leakage audit;
4. feature importance and stability;
5. predictive signal discovery;
6. global and cross-archive exports;
7. multi-archive loader.

For every route, bind before extraction:

- exit code or exception;
- ordered stdout;
- exact filename set;
- exact CSV header order;
- row counts;
- SHA-256 for every CSV and Markdown artifact;
- empty/small-data warning behavior;
- missing/invalid input and partial-output behavior.

The CLI parser and dispatch order remain in `inspect_trades.py` until the final modularization stage.

## Explicit exclusions

- no movement of archive, JSONL, market, or log readers as part of S5 output persistence;
- no statistical or ML computation change;
- no schema normalization or header synthesis for empty files;
- no atomic-write retrofit;
- no shared Markdown-template abstraction;
- no merging of continue-on-error and fail-closed cross-archive paths;
- no CLI option, default, precedence, filename, or stdout change;
- no broad `exports.py` module;
- no IU4, Live-L1, Exchange, or Live enablement.

## Gate conclusion

**GO** for a separately authorized S5 persistence characterization gate covering label persistence, `write_csv_rows`, and `export_ml_csv`.

**NO-GO** for extracting persistence functions before byte-level gates or for moving any high-level route without its complete artifact contract.

The production source remains unchanged by this analysis.
