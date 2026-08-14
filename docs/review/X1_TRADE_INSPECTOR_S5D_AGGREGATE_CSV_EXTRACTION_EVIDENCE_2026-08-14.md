# X1 Trade Inspector S5D Aggregate CSV Extraction Evidence — 2026-08-14

Status: **PASS**

Branch: `codex/x1-trade-inspector-s5d-aggregate-csv-extraction-2026-08-14`

Base commit: `f71799e69be0c1decbb1e6caf5a708c0a8b05326`

## Decision

The approved S5D aggregate CSV route and its coherent semantic dependency closure were extracted from `tools/trade_inspector/inspect_trades.py` into `tools/trade_inspector/aggregate_csv.py` without changing any function implementation or public name.

Extracted closure:

- `avg`;
- `group_rows`;
- `group_stats`;
- `parse_cause_weights`;
- `compute_root_cause_attribution`;
- `export_root_cause_attribution_csv`;
- `aggregate_group_rows`;
- `aggregate_top_improvement_rows`;
- `export_aggregate_csvs`.

`inspect_trades.py` remains the stable CLI and import façade. Package imports and direct file execution both import and re-export all nine exact new-module function objects. Existing print, feature, discovery, cross-archive, validation, and CLI paths continue to resolve their shared aggregation bindings through the façade.

## Dependency closure

The new module depends only on:

- S1 compatibility primitives: `safe_float`, `safe_int`, and `safe_text`;
- S5B generic persistence: `write_csv_rows`;
- Python standard-library `Path` and `Any`.

Neither dependency imports the aggregate module or the façade. The façade imports the aggregate module, so the dependency direction is acyclic in both package and direct-script modes.

Keeping `avg`, grouping, attribution, row construction, and the route together avoids a façade back-import and preserves exact object identity for consumers outside the CSV route.

## Changed files

| File | Role | Prepared SHA-256 |
|---|---|---|
| `tools/trade_inspector/aggregate_csv.py` | New exact-semantics S5D route module | `0d45ee33687670df13096caded89ae56f56f3118d09b56ef8e475c95b9009713` |
| `tools/trade_inspector/inspect_trades.py` | Stable façade and nine re-exports | `2e3fb86984772c6833169b246effd99a41e13011fac904e59967a02374536d40` |
| `tests/trade_inspector/test_inspect_trades_characterization.py` | Exact nine-object re-export assertions | `f0d6a280b021841feb22045a9488a3eae2f3a1921c5a98a1b6e24e92cce4af6f` |

Pre-extraction façade SHA-256:

`2e959fb28d011b8322774e9a51362da65a9d6c9c55d4dead40a148c8f71ec8f5`

## Semantic identity

Fingerprints were recorded before extraction and re-derived from the new module after extraction:

| Binding | AST SHA-256 | Source-segment SHA-256 |
|---|---|---|
| `avg` | `d1d1e44d4084e12ee4b002285ea339c9c3e733b53678b2be2f9aff72d15bea55` | `232333aebcecc30a4f4d247e8899bc856ed87666d541c36e814f41f5361c948e` |
| `group_rows` | `5cbbdb7bbc9123c5361373cc1b560e2c9396aad92ec3d6ad981847d31cb02d75` | `d05448be3b61224fb5efe1084d702ed8173a3b8b48c0c9a46227e213cabbf3b7` |
| `group_stats` | `506942f64d4287819a31a6f19cfcb349bb800f3135b6d75c0942e23ff03874e5` | `9924e6fd6ec083cdb79d0013c4aab6f34a5bf617940852da551189294450b34e` |
| `parse_cause_weights` | `5c0015eef13caaa8241fed7020a59cd5a278bdb005d938a24b5118bad5a0cf11` | `4ca34f675a03c95e5babc9e72fe2c8842798f306c71e339df3937c4bf10d3eb6` |
| `compute_root_cause_attribution` | `391ec341aed25c77402d2b0323018c6c484936b084e30b8b8e72cccbfe5d5aae` | `8a0c6388bf68c8738b5435e74ee100098ee37da176be157cf3894bd85cc33554` |
| `export_root_cause_attribution_csv` | `462350a5efee69c0e970b946d3a0b25b0fd5a8a302ac569d6bd2d5a52a8cc999` | `8ff22a7e40666c74fbb10de4609df87bb48fd427c5612814e392089915dd96cd` |
| `aggregate_group_rows` | `9cfe1fc6ce45032115db027e4c7364a6939669bb3fda1373e430daaf3048c4df` | `9c92d0549ebb0932a68680045b82efb9628c1d0b7316e118b72cd71dc1b24caa` |
| `aggregate_top_improvement_rows` | `a49c3badf74b725d142d4354a2056f8ebc300ac2fb075c973d06df76a3cc0091` | `fab6bd4f843a53f6bb92b6bfeabf4eb6823358fcaf9e9f1fcfa4b461548b9ccf` |
| `export_aggregate_csvs` | `3430a90baa6c71ac1219c21f4a398ddc821b224a5813af38aa1b61066a57a952` | `1c06dfd7ffe0e73320fe4edc250a0101e4766f5f20fbcba9abfce7d76a03700c` |

All eighteen fingerprints are unchanged. Boundary verification confirms exactly nine functions in the new module and no duplicate local definition in the façade.

## Artifact-contract continuity

The complete S5D artifact gate remains unchanged:

| Contract | SHA-256 |
|---|---|
| Three-row filename-to-hash manifest | `64e371f979cffe4ca2e01ad18d94fba14f0fea2a90755cb26f1de1a3b1ae1e98` |
| Empty-input filename-to-hash manifest | `94705901ba1a8aa982a011665f71480d353a066e83919fc930a429474a13a6c4` |
| Empty global-summary CSV | `4e0fcbcd6382b7330f800a27e4bee758b36434729406735abe18183d3b41870e` |
| Zero-byte empty derived CSV | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |

All twelve non-empty artifact hashes listed in the S5D characterization gate remain exact. Candidate ordering, group ordering, weighted attribution ordering, CRLF bytes, overwrite behavior, foreign CSV preservation, and sorted directory-content stdout listing all remain unchanged.

## Focused validation

Command:

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest -v tests.trade_inspector.test_inspect_trades_characterization
```

Result:

```text
Ran 27 tests
OK
```

The focused suite asserted exact object identity for all nine façade bindings. The hermetic summary CLI test executed `inspect_trades.py` directly and passed with deterministic output and empty stderr, covering the direct-script import path.

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

- No aggregation formula, coercion, grouping key, group order, sort key, limit, schema, field order, filename, CSV byte, overwrite behavior, or stdout behavior changed.
- No generic CSV, raw ML CSV, or label persistence changed.
- No CLI option, default path, dispatch order, public import name, package behavior, or direct-script behavior changed.
- No ML-dataset, feature, discovery, global, cross-archive, or multi-archive route moved.
- No archive, market data, label file, registry, runtime input, generated repository artifact, or live state was read or modified.
- IU4, Live-L1, Exchange, Live, inputs, strategies, policies, and gates remain unchanged and locked.
- The foreign untracked file `scripts/build_rcc002_spec_bundle.py` was not read, modified, staged, or included.

## Outcome

S5D aggregate CSV extraction is complete within its approved boundary. The next controlled work is S5D branch integration followed by an S5E route-specific characterization gate for the basic ML-dataset export and its complete artifact set before any ML-dataset route extraction.
