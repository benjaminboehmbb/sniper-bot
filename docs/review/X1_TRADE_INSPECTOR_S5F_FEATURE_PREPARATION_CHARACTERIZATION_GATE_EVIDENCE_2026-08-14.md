# X1 Trade Inspector S5F Feature Preparation Characterization Gate Evidence — 2026-08-14

Status: **PASS**

Branch: `codex/x1-trade-inspector-s5f-feature-preparation-characterization-gate-2026-08-14`

Base commit: `77f48dedb1e5a284680f95d6a515f1c98c5038a5`

## Scope

This gate freezes the current S5F feature-preparation route before any extraction from `tools/trade_inspector/inspect_trades.py`.

Bound production surface:

- `NON_FEATURE_COLUMNS`;
- `TARGET_COLUMNS`;
- `is_number_like`;
- `build_category_maps`;
- `build_feature_catalog`;
- `build_model_ready_rows`;
- `export_feature_preparation`.

No production implementation, CLI dispatch, runtime input, archive, market data, label data, or generated repository artifact changed while establishing the gate.

## Production identity

`tools/trade_inspector/inspect_trades.py` remained byte-identical throughout the gate.

SHA-256 before and after:

`728e44666ba80e36d62c2dd24e74547493ab685a19761e3b5f2c8506f1103969`

Function fingerprints:

| Binding | AST SHA-256 | Source-segment SHA-256 |
|---|---|---|
| `is_number_like` | `5d0f407217355432c696e07e43954088217aa8d4b0d6a0c19fd1a67c9c02b93e` | `19d7ebba4e8acc68f8dc3ca9e6cb1e65d7e5cdb5b9e0a8137a8384277bf335a5` |
| `build_category_maps` | `050fb37ad3b3f2e43c802c119fec01d2712fc43f4875f514e8afbf95fe6e8d01` | `c14d96a001781fc7b427e2b414867d9216f960016e02c580850069e930184b95` |
| `build_feature_catalog` | `2af2e75551553b1d9888dea0e83ec83e13e1f3d3037466785be8cfca3d406f5e` | `8d8da19fa1c7443267a19e6197ec15993e5079f5429276dec6ab6ece910967ef` |
| `build_model_ready_rows` | `f5a8e1a8e63b00bea280ef615527a701303add2224c9cdb7c1e3c77bf06fa869` | `4a3d7bedd75c194789e8b5b3cba300a89b54045d5df9ff69d8e99ac6dd98f9ff` |
| `export_feature_preparation` | `f71bc955364e19562345a305e34aa4fd177cf7e81ceb203639f6f913228e597e` | `62dfc9d8ed3ae3d7788288be66fc9bab29ac7d6108e07c09f11cad4fcbde1c41` |

Shared-set fingerprints:

| Binding | AST SHA-256 | Source-segment SHA-256 |
|---|---|---|
| `NON_FEATURE_COLUMNS` | `694a03627bb29db3cf76075728be32a704c4d55d2cabba0302a4bf976dc3d982` | `3d9b562c1049a03c6b765c5e5baf9e6b86ea3853f9fd1d224ee0a2b973a4f6b7` |
| `TARGET_COLUMNS` | `c127912725ff9116a457fbed3d283ff8d801c33658ebc35634a1bab2a9abd94d` | `acfd19b2ebcab62d5fd25671dfb30872e74ae2e8c86775dd45082b66e3b34ee5` |

## Complete artifact contract

The three-row fixture uses stable trade IDs `A`, `K`, and `Z`, exercising train, validation, and test respectively.

| Artifact | SHA-256 |
|---|---|
| `trade_dataset_v4b_feature_catalog.csv` | `e1a9817db5033c910f3e6c89b4becdcee0f35f8f03af05ccb3e35bb8dfb07667` |
| `trade_dataset_v4b_feature_manifest.csv` | `5f4ddd082187a4dde4b5686356760b877034127596ce556fdaac0000d9b820eb` |
| `trade_dataset_v4b_model_ready.csv` | `f381baf1d039ded694828552dd90f8e37796ef13d95257cfb4e697a066beaa4f` |
| `trade_dataset_v4b_model_ready_test.csv` | `814ea2f70122edeecb0f36b4c339d78d7aa0818275d3e805876603cbda4b889b` |
| `trade_dataset_v4b_model_ready_train.csv` | `5892adcd003f2fc0726bbf7ecd01fc1b637f68a147b1b3f194de45c3eec89f3e` |
| `trade_dataset_v4b_model_ready_validation.csv` | `ef987f0557ebcdea1c3dbc08ffb6c1d272d38d5669154e854019fefe0a74a624` |

Canonical filename-to-hash fingerprint:

`627951215e9fe327e64f450234f09f376966a970a0fbdc20551876b5da604e9e`

The manifest contract is exactly:

- dataset version `v4b`;
- 3 total rows;
- 112 features;
- 90 numeric features;
- 22 categorical label-encoded features;
- 16 targets;
- purpose `feature_importance_preparation`;
- `model_training=not_performed`.

Each model-ready row has exactly 131 columns: three stable identity/split columns, sixteen lexicographically ordered targets, and 112 lexicographically ordered encoded features.

## Feature transformation contract

The focused gate proves the current implementation rather than assuming a stronger preprocessing model:

- feature candidates are taken from first-row column order only;
- `NON_FEATURE_COLUMNS` and `TARGET_COLUMNS` are excluded from the feature catalog;
- columns with no non-empty values are omitted;
- a column is numeric only when every non-empty observed value passes Python float conversion;
- numeric missing values are written as `0.0` through `safe_float`;
- categorical values are sorted lexicographically and encoded from zero;
- empty or unknown categorical values are encoded as `-1`;
- encoded feature rows follow catalog `encoded_name` order;
- later-only columns absent from the first row are ignored.

The current route does not scale numeric values and does not perform model training. The gate intentionally preserves that observed boundary without claiming normalization or training behavior.

## Empty-input contract

Empty input creates the same six filenames. Five artifacts are zero-byte files with SHA-256:

`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`

The empty manifest CSV SHA-256 is:

`b86ec7a1b1873770c10015c990c4aea583e9bc57631a5b9c1131d2a2455ade82`

The empty filename-to-hash fingerprint is:

`806b317c5793aa295f6648634e71031d49d4a6aa5af744998c8ee187cfdf4120`

The empty manifest records zero rows and features, sixteen targets, the same purpose, and `model_training=not_performed`.

## Filesystem and console contract

The gate also binds:

- recursive output-directory creation;
- overwrite of route-owned stale CSVs;
- preservation of foreign CSVs;
- inclusion of foreign CSVs in the sorted stdout directory listing;
- exact stdout headings, prefixes, path formatting, and ordering;
- empty stderr.

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

## Prepared evidence files

| File | Prepared SHA-256 |
|---|---|
| `tests/trade_inspector/test_inspect_trades_characterization.py` | `c09d74cfc5399d2abc6a7ad84e2bf2fa82ffc0c3cf00955102f8c5b303b941fd` |
| `tools/trade_inspector/inspect_trades.py` | `728e44666ba80e36d62c2dd24e74547493ab685a19761e3b5f2c8506f1103969` |

## Safety boundary

- Production code remained byte-identical.
- No feature classification, category ordering, encoding, missing-value behavior, target order, feature order, schema, filename, CSV byte, overwrite behavior, stdout behavior, or stderr behavior changed.
- No archive, market data, label file, registry, runtime input, generated repository artifact, or live state was read or modified.
- IU4 ENFORCED, Live-L1, Exchange, Live, inputs, strategies, policies, and gates remain unchanged and locked.
- The foreign untracked file `scripts/build_rcc002_spec_bundle.py` was not read, modified, staged, or included.

## Outcome

S5F feature preparation is fully characterized for controlled extraction. The next controlled work is S5F characterization-gate branch integration followed by extraction of the feature-preparation closure into an acyclic module while preserving the two shared column sets for downstream leakage, importance, stability, discovery, and cross-archive consumers.
