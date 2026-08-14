# X1 Trade Inspector S5E ML Dataset Extraction Evidence — 2026-08-14

Status: **PASS**

Branch: `codex/x1-trade-inspector-s5e-ml-dataset-extraction-2026-08-14`

Base commit: `cf4142b4c3a25647296110209df5956c7e465b69`

## Decision

The approved S5E ML-dataset route and its coherent semantic dependency closure were extracted from `tools/trade_inspector/inspect_trades.py` into `tools/trade_inspector/ml_dataset.py` without changing any function implementation or public name.

Extracted closure:

- `print_kv`;
- `add_ml_targets`;
- `dataset_split_from_trade_id`;
- `build_ml_dataset_rows`;
- `evaluate_split_quality`;
- `print_split_quality`;
- `export_ml_dataset`.

`inspect_trades.py` remains the stable CLI and import facade. Package imports and direct file execution both import and re-export all seven exact new-module function objects. Existing report, summary, feature-preparation, leakage, importance, stability, discovery, global-trade, cross-archive, validation, and CLI paths continue to resolve their shared bindings through the facade.

## Dependency closure

The new module depends only on:

- S1 compatibility primitives: `safe_float`, `safe_int`, and `safe_text`;
- S5B generic persistence: `write_csv_rows`;
- Python standard-library `Path` and `Any`.

Neither dependency imports the ML-dataset module or the facade. The facade imports the ML-dataset module, so the dependency direction is acyclic in both package and direct-script modes.

`print_kv` was moved with the closure and re-exported instead of duplicated. This preserves one exact callable for split-quality output and every pre-existing facade print consumer while avoiding a facade back-import from the new module.

## Changed files

| File | Role | Prepared SHA-256 |
|---|---|---|
| `tools/trade_inspector/ml_dataset.py` | New exact-semantics S5E route module | `cbc8ef197b314ccd0f38939f33db6ccc3e2bf99be98434b59e54e2dc2f6b3409` |
| `tools/trade_inspector/inspect_trades.py` | Stable facade and seven re-exports | `728e44666ba80e36d62c2dd24e74547493ab685a19761e3b5f2c8506f1103969` |
| `tests/trade_inspector/test_inspect_trades_characterization.py` | Exact seven-object re-export assertions | `47dee15e229d9eaad0712f5ab55f5e5021393f99e2a8dc1bd763ede7d5920ef3` |

Pre-extraction facade SHA-256:

`2e3fb86984772c6833169b246effd99a41e13011fac904e59967a02374536d40`

## Semantic identity

Fingerprints were recorded before extraction and re-derived from the new module after extraction:

| Binding | AST SHA-256 | Source-segment SHA-256 |
|---|---|---|
| `print_kv` | `524f3185fa6977d4ea0c2d4cf0f90899e36ffc3472d055780a27858da743eed6` | `c45113df433ec05ec07439192641c773f280780666089fb719aafbb728f1c805` |
| `add_ml_targets` | `a8a91036baa98e191cfe37375f399d0765114b571a3501cbc7e2402960b74921` | `cad519df8dd5a2aed5d60f15a106b96d2775b10f57555a66eed0f72b91d7378f` |
| `dataset_split_from_trade_id` | `76ffd80dad58e4981c09fc63687acc4f537e7b5b3d819a173ee271b874da247e` | `c44d2ae546a1142f7b0466e90bf33c7da54d6a8ae7897d04edeebc5a58038ed7` |
| `build_ml_dataset_rows` | `1623602b8492be93a253470fc859c2373e5ea588105ca568d0599c9e42dff3a8` | `36d0a2ac2d4a13e1155544747344da4df862263eb82c7dc4b359dcd85f358f6f` |
| `evaluate_split_quality` | `cbb8632a7b6ebc1207f877a87355409b35b1d4cffa14bb490307cd81c67d817b` | `c493c1c63bdee6c189d5a24c03544dc85aed48f2cf5fbd6534d3768ce0eba52e` |
| `print_split_quality` | `d37da44e16ff02e1b15661bf642038a54f037df008f16836155df20915385592` | `8c146cb357d5259313e11e4753f24a6853169babc1854001d4124817db0dc785` |
| `export_ml_dataset` | `86693dffdcd8bc5649ced78a4d0c3d0b532a541af97047c8d28323568683bb54` | `ae08f6aba06f16f38869e722ed41b2ac5b236986605761f8f04084602001ba5e` |

All fourteen fingerprints are unchanged. Boundary verification confirms exactly seven functions in the new module and no duplicate local definition in the facade.

## Artifact-contract continuity

The complete S5E artifact gate remains unchanged:

| Artifact | SHA-256 |
|---|---|
| `trade_dataset_v4a.csv` | `76b41d4813d9512fd660086866ce89c162cdfdeeb90740e758a5a9eac1f61df4` |
| `trade_dataset_v4a_manifest.csv` | `5d3df016b5266ada50bc4a56204d18cc7c70375715cc48fac980f009d1cd9629` |
| `trade_dataset_v4a_test.csv` | `5f08ba7342a7ff83fe050a77770f89e45b8f9300b8390c51fd96d58834654919` |
| `trade_dataset_v4a_train.csv` | `1c6274a814db00ffff5ab5f35d63aaa1bc660eef43185ce792109b29b2c1c969` |
| `trade_dataset_v4a_validation.csv` | `4cc320bf485a15e321c4e25303c7a8efbbf8b3aba38e38b323f2ec4dec196eec` |
| Three-row filename-to-hash manifest | `e9203c8dbef4325350d293e922b9968c417bf1089a822142d9ddd05765663686` |
| Empty manifest CSV | `5aa677b6250500aa3986259da909b636b6d8218d8c2fcf719eb66ecf9c8cadd2` |
| Empty filename-to-hash manifest | `5b6728110f59af120e350655e535d98f16f7325f2cf50a9928bcc8a7037b76c8` |
| Zero-byte empty dataset/split CSV | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |

Train/validation/test ASCII buckets, row and field order, target values, deterministic split values, split-quality statuses, warning order, manifest schema, CRLF bytes, overwrite behavior, foreign CSV preservation, exact stdout order, and empty stderr all remain unchanged.

## Focused validation

Command:

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest -v tests.trade_inspector.test_inspect_trades_characterization
```

Result:

```text
Ran 30 tests
OK
```

The focused suite asserted exact object identity for all seven facade bindings. The hermetic summary CLI test executed `inspect_trades.py` directly and passed with deterministic output and empty stderr, covering the direct-script import path.

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

- No target formula, coercion, threshold, split bucket, split status, warning, schema, field order, filename, CSV byte, overwrite behavior, stdout behavior, or stderr behavior changed.
- No generic CSV, raw ML CSV, aggregate CSV, label persistence, archive intake, path diagnosis, regime identity, or row construction changed.
- No CLI option, default path, dispatch order, public import name, package behavior, or direct-script behavior changed.
- No feature-preparation, leakage, importance, stability, discovery, global, cross-archive, or multi-archive route moved.
- No archive, market data, label file, registry, runtime input, generated repository artifact, or live state was read or modified.
- IU4 ENFORCED, Live-L1, Exchange, Live, inputs, strategies, policies, and gates remain unchanged and locked.
- The foreign untracked file `scripts/build_rcc002_spec_bundle.py` was not read, modified, staged, or included.

## Outcome

S5E ML-dataset extraction is complete within its approved boundary. The next controlled work is S5E extraction branch integration followed by an S5F route-specific characterization gate for the feature-preparation export before any feature-preparation route extraction.
