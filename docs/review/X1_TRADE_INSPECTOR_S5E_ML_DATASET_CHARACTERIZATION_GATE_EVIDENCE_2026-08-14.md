# X1 Trade Inspector S5E ML Dataset Characterization Gate Evidence — 2026-08-14

Status: **PASS — CHARACTERIZATION ONLY**

Branch: `codex/x1-trade-inspector-s5e-ml-dataset-characterization-gate-2026-08-14`

Base commit: `2bd388a7bff7936578b34f7a1673325f1316628e`

## Decision

The route-specific pre-extraction characterization gate for the basic `export_ml_dataset` route is complete. No production function, import, CLI path, target rule, split rule, schema, persistence behavior, or runtime input changed.

The gate binds the complete five-CSV `v4a` artifact set for a synthetic three-row fixture spanning train, validation, and test; the distinct empty-input artifact and warning set; overwrite behavior; and current sorted directory-listing behavior in the presence of an unrelated CSV.

## Changed file

| File | Role | Prepared SHA-256 |
|---|---|---|
| `tests/trade_inspector/test_inspect_trades_characterization.py` | Hermetic S5E split, output, and complete artifact contracts | `cd5f853054c0181a5bfb355f9ed38218a16d882fed10e6861f2cd2afe149acef` |

Production façade SHA-256 remained unchanged:

`2e3fb86984772c6833169b246effd99a41e13011fac904e59967a02374536d40`

## Production identity

The route and its directly material target, split, quality, and output helpers were recorded before the gate:

| Binding | AST SHA-256 | Source-segment SHA-256 |
|---|---|---|
| `print_kv` | `524f3185fa6977d4ea0c2d4cf0f90899e36ffc3472d055780a27858da743eed6` | `c45113df433ec05ec07439192641c773f280780666089fb719aafbb728f1c805` |
| `add_ml_targets` | `a8a91036baa98e191cfe37375f399d0765114b571a3501cbc7e2402960b74921` | `cad519df8dd5a2aed5d60f15a106b96d2775b10f57555a66eed0f72b91d7378f` |
| `dataset_split_from_trade_id` | `76ffd80dad58e4981c09fc63687acc4f537e7b5b3d819a173ee271b874da247e` | `c44d2ae546a1142f7b0466e90bf33c7da54d6a8ae7897d04edeebc5a58038ed7` |
| `build_ml_dataset_rows` | `1623602b8492be93a253470fc859c2373e5ea588105ca568d0599c9e42dff3a8` | `36d0a2ac2d4a13e1155544747344da4df862263eb82c7dc4b359dcd85f358f6f` |
| `evaluate_split_quality` | `cbb8632a7b6ebc1207f877a87355409b35b1d4cffa14bb490307cd81c67d817b` | `c493c1c63bdee6c189d5a24c03544dc85aed48f2cf5fbd6534d3768ce0eba52e` |
| `print_split_quality` | `d37da44e16ff02e1b15661bf642038a54f037df008f16836155df20915385592` | `8c146cb357d5259313e11e4753f24a6853169babc1854001d4124817db0dc785` |
| `export_ml_dataset` | `86693dffdcd8bc5649ced78a4d0c3d0b532a541af97047c8d28323568683bb54` | `ae08f6aba06f16f38869e722ed41b2ac5b236986605761f8f04084602001ba5e` |

No production extraction was performed in this gate.

## Complete three-split artifact set

The synthetic fixture uses the trade IDs `A`, `K`, and `Z`. Their ASCII sums deterministically exercise the current three buckets:

- `A` → `train`;
- `K` → `validation`;
- `Z` → `test`.

| Artifact | SHA-256 |
|---|---|
| `trade_dataset_v4a.csv` | `76b41d4813d9512fd660086866ce89c162cdfdeeb90740e758a5a9eac1f61df4` |
| `trade_dataset_v4a_manifest.csv` | `5d3df016b5266ada50bc4a56204d18cc7c70375715cc48fac980f009d1cd9629` |
| `trade_dataset_v4a_test.csv` | `5f08ba7342a7ff83fe050a77770f89e45b8f9300b8390c51fd96d58834654919` |
| `trade_dataset_v4a_train.csv` | `1c6274a814db00ffff5ab5f35d63aaa1bc660eef43185ce792109b29b2c1c969` |
| `trade_dataset_v4a_validation.csv` | `4cc320bf485a15e321c4e25303c7a8efbbf8b3aba38e38b323f2ec4dec196eec` |

Canonical filename-to-hash manifest SHA-256:

`e9203c8dbef4325350d293e922b9968c417bf1089a822142d9ddd05765663686`

The gate explicitly binds:

- combined row order `A`, `K`, `Z`;
- exactly one row in each deterministic split artifact;
- all target columns added by `add_ml_targets`;
- `ml_split` and `ml_dataset_version=v4a` placement and bytes;
- manifest version, row counts, shares, target-column string, feature scope, and split-method string;
- split-quality status `PASS` with warning `dataset_too_small_for_reliable_ml` for the three-row fixture;
- exact ordered split-quality stdout, output-directory line, and sorted file listing;
- empty stderr.

## Empty-input artifact and warning set

Empty input still creates all five paths:

- combined, train, validation, and test CSVs are exactly zero bytes with SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`;
- the non-empty manifest CSV has SHA-256 `5aa677b6250500aa3986259da909b636b6d8218d8c2fcf719eb66ecf9c8cadd2`.

Canonical empty filename-to-hash manifest SHA-256:

`5b6728110f59af120e350655e535d98f16f7325f2cf50a9928bcc8a7037b76c8`

The exact empty warning order is:

`dataset_too_small_for_reliable_ml|empty_train_split|empty_validation_split|empty_test_split`

Status remains `WARN`; every count and share remains zero. This behavior must not be normalized during extraction.

## Output-directory contract

The gate binds:

- nested output-directory creation;
- direct overwrite of a pre-existing combined dataset artifact;
- preservation of an unrelated `foreign.csv` file;
- ordered split-quality stdout before the output-directory summary;
- sorted `*.csv` path listing after all writes;
- inclusion of unrelated `foreign.csv` in stdout because current behavior enumerates directory contents rather than only route-owned artifacts;
- empty stderr.

The directory-content dependency is current behavior, not authorization to change it.

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

All fixtures are synthetic and use temporary directories. The hermetic summary CLI test also executed `inspect_trades.py` directly and passed with deterministic output and empty stderr.

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

## Future extraction boundary

`export_ml_dataset` directly depends on target construction, ASCII split assignment, split-quality evaluation, split-quality printing, generic CSV persistence, and compatibility primitives. `print_split_quality` calls the façade-level `print_kv`, which is also used by other display paths.

A later extraction must therefore either include and re-export the exact `print_kv` object with the ML-dataset closure or establish another acyclic exact-object boundary. Importing `print_kv` back from the façade is prohibited because it would create a cycle.

## Safety boundary

- No production source file changed.
- No target threshold, ASCII bucket, split name, warning precedence, status rule, schema, field order, filename, CSV byte, overwrite behavior, or stdout behavior changed.
- No CLI option, default path, dispatch order, package import, or direct-script behavior changed.
- No feature-preparation, leakage, importance, stability, discovery, global, cross-archive, or multi-archive route moved.
- No archive, market data, label file, registry, runtime input, generated repository artifact, or live state was read or modified.
- IU4, Live-L1, Exchange, Live, inputs, strategies, policies, and gates remain unchanged and locked.
- The foreign untracked file `scripts/build_rcc002_spec_bundle.py` was not read, modified, staged, or included.

## Outcome

S5E basic ML-dataset export is eligible for a separately controlled extraction after this gate is integrated into `main`. The extraction must preserve the seven recorded function contracts, all five artifacts, both manifest fingerprints, and the complete stdout/stderr behavior above.
