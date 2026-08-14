# X1 Trade Inspector S5F Feature Preparation Extraction Evidence — 2026-08-14

Status: **PASS**

Branch: `codex/x1-trade-inspector-s5f-feature-preparation-extraction-2026-08-14`

Base commit: `313bd3b1bbc2d6e93fc664971f039d47b6f2faf1`

## Decision

The approved S5F feature-preparation route, its semantic helper closure, and its two shared column sets were extracted from `tools/trade_inspector/inspect_trades.py` into `tools/trade_inspector/feature_preparation.py` without changing any implementation or public name.

Extracted bindings:

- `NON_FEATURE_COLUMNS`;
- `TARGET_COLUMNS`;
- `is_number_like`;
- `build_category_maps`;
- `build_feature_catalog`;
- `build_model_ready_rows`;
- `export_feature_preparation`.

`inspect_trades.py` remains the stable CLI and import facade. Package imports and direct file execution both import and re-export all seven exact new-module objects.

## Shared-binding continuity

`TARGET_COLUMNS` is consumed by downstream leakage-audit, feature-importance, stability, discovery, and cross-archive routes. Moving the set with the S5F closure and re-exporting the exact object preserves one authoritative binding for all existing facade consumers.

`NON_FEATURE_COLUMNS` and every S5F function are handled the same way. The characterization suite asserts `is` identity between every facade binding and its new-module counterpart, preventing silent copies or divergent definitions.

## Dependency closure

The new module depends only on:

- S5E ML-dataset construction: `build_ml_dataset_rows`;
- S5B generic persistence: `write_csv_rows`;
- S1 compatibility primitives: `safe_float` and `safe_text`;
- Python standard-library `Path` and `Any`.

None of these dependencies imports the feature-preparation module or the facade. The facade imports the feature-preparation module, so the dependency direction is acyclic in package and direct-script modes.

## Changed files

| File | Role | Prepared SHA-256 |
|---|---|---|
| `tools/trade_inspector/feature_preparation.py` | New exact-semantics S5F module | `5921c31a798a6fdd052b79c7f80bfece13189e296fb94a7da6bb74063dccf559` |
| `tools/trade_inspector/inspect_trades.py` | Stable facade and seven re-exports | `79128be78af0088b157078f526246b1b667e496fdbff4aa2afbf94702661f549` |
| `tests/trade_inspector/test_inspect_trades_characterization.py` | Exact seven-object identity assertions | `33a167f49f522c3e6f6c9460126e62adcf270a3acba3fdf7a48bf8fb2d1dfc4e` |

Pre-extraction facade SHA-256:

`728e44666ba80e36d62c2dd24e74547493ab685a19761e3b5f2c8506f1103969`

## Semantic identity

Fingerprints were recorded before extraction and re-derived from the new module after extraction:

| Binding | AST SHA-256 | Source-segment SHA-256 |
|---|---|---|
| `NON_FEATURE_COLUMNS` | `694a03627bb29db3cf76075728be32a704c4d55d2cabba0302a4bf976dc3d982` | `3d9b562c1049a03c6b765c5e5baf9e6b86ea3853f9fd1d224ee0a2b973a4f6b7` |
| `TARGET_COLUMNS` | `c127912725ff9116a457fbed3d283ff8d801c33658ebc35634a1bab2a9abd94d` | `acfd19b2ebcab62d5fd25671dfb30872e74ae2e8c86775dd45082b66e3b34ee5` |
| `is_number_like` | `5d0f407217355432c696e07e43954088217aa8d4b0d6a0c19fd1a67c9c02b93e` | `19d7ebba4e8acc68f8dc3ca9e6cb1e65d7e5cdb5b9e0a8137a8384277bf335a5` |
| `build_category_maps` | `050fb37ad3b3f2e43c802c119fec01d2712fc43f4875f514e8afbf95fe6e8d01` | `c14d96a001781fc7b427e2b414867d9216f960016e02c580850069e930184b95` |
| `build_feature_catalog` | `2af2e75551553b1d9888dea0e83ec83e13e1f3d3037466785be8cfca3d406f5e` | `8d8da19fa1c7443267a19e6197ec15993e5079f5429276dec6ab6ece910967ef` |
| `build_model_ready_rows` | `f5a8e1a8e63b00bea280ef615527a701303add2224c9cdb7c1e3c77bf06fa869` | `4a3d7bedd75c194789e8b5b3cba300a89b54045d5df9ff69d8e99ac6dd98f9ff` |
| `export_feature_preparation` | `f71bc955364e19562345a305e34aa4fd177cf7e81ceb203639f6f913228e597e` | `62dfc9d8ed3ae3d7788288be66fc9bab29ac7d6108e07c09f11cad4fcbde1c41` |

All fourteen fingerprints are unchanged. Boundary verification confirms exactly the five functions and two sets in the new module and no duplicate local definition in the facade.

## Artifact-contract continuity

The complete S5F artifact gate remains unchanged:

| Artifact | SHA-256 |
|---|---|
| `trade_dataset_v4b_feature_catalog.csv` | `e1a9817db5033c910f3e6c89b4becdcee0f35f8f03af05ccb3e35bb8dfb07667` |
| `trade_dataset_v4b_feature_manifest.csv` | `5f4ddd082187a4dde4b5686356760b877034127596ce556fdaac0000d9b820eb` |
| `trade_dataset_v4b_model_ready.csv` | `f381baf1d039ded694828552dd90f8e37796ef13d95257cfb4e697a066beaa4f` |
| `trade_dataset_v4b_model_ready_test.csv` | `814ea2f70122edeecb0f36b4c339d78d7aa0818275d3e805876603cbda4b889b` |
| `trade_dataset_v4b_model_ready_train.csv` | `5892adcd003f2fc0726bbf7ecd01fc1b637f68a147b1b3f194de45c3eec89f3e` |
| `trade_dataset_v4b_model_ready_validation.csv` | `ef987f0557ebcdea1c3dbc08ffb6c1d272d38d5669154e854019fefe0a74a624` |
| Three-row filename-to-hash manifest | `627951215e9fe327e64f450234f09f376966a970a0fbdc20551876b5da604e9e` |
| Empty manifest CSV | `b86ec7a1b1873770c10015c990c4aea583e9bc57631a5b9c1131d2a2455ade82` |
| Empty filename-to-hash manifest | `806b317c5793aa295f6648634e71031d49d4a6aa5af744998c8ee187cfdf4120` |
| Zero-byte empty derived CSV | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |

The 112-feature catalog, 90/22 numeric/categorical counts, 16 targets, 131-column model schema, first-row candidate boundary, lexicographic category mapping, `0.0` numeric fallback, `-1` unknown-category fallback, split membership, field order, filenames, CSV bytes, overwrite behavior, foreign-file preservation, exact stdout order, and empty stderr all remain unchanged.

## Focused validation

Command:

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest -v tests.trade_inspector.test_inspect_trades_characterization
```

Result:

```text
Ran 34 tests
OK
```

The focused suite asserted exact object identity for all seven facade bindings. The hermetic summary CLI test executed `inspect_trades.py` directly and passed, covering the direct-script import path.

## Full regression

Command:

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -s tests/regression -p 'test_*.py'
```

Result:

```text
Ran 170 tests
OK
```

## Safety boundary

- No feature classification, category ordering, encoding, missing-value behavior, target order, feature order, schema, filename, CSV byte, overwrite behavior, stdout behavior, or stderr behavior changed.
- No dataset-target, dataset-split, generic CSV, raw ML CSV, aggregate CSV, label persistence, archive intake, path diagnosis, regime identity, or row construction changed.
- No CLI option, default path, dispatch order, public import name, package behavior, or direct-script behavior changed.
- No leakage, importance, stability, discovery, global, cross-archive, or multi-archive route moved.
- No archive, market data, label file, registry, runtime input, generated repository artifact, or live state was read or modified.
- IU4 ENFORCED, Live-L1, Exchange, Live, inputs, strategies, policies, and gates remain unchanged and locked.
- The foreign untracked file `scripts/build_rcc002_spec_bundle.py` was not read, modified, staged, or included.

## Outcome

S5F feature-preparation extraction is complete within its approved boundary. The next controlled work is S5F extraction branch integration followed by an S5G route-specific characterization gate for the leakage-audit export before any leakage-audit extraction.
