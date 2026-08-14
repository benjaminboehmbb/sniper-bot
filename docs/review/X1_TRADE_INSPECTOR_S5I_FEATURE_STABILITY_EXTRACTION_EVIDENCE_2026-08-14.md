# X1 Trade Inspector S5I Feature Stability Extraction Evidence — 2026-08-14

Status: **PASS**

Branch: `codex/x1-trade-inspector-s5i-feature-stability-extraction-2026-08-14`

Base commit: `55f11101a514d5902d3b6b336046e998c1ff71a6`

## Decision

The characterized S5I feature-stability closure was extracted from `tools/trade_inspector/inspect_trades.py` into `tools/trade_inspector/feature_stability.py` without changing implementation semantics or public names.

Extracted bindings:

- `median`;
- `std`;
- `stability_class`;
- `export_feature_stability`.

`inspect_trades.py` remains the stable CLI and import facade. Package imports and direct file execution both import and re-export the four exact new-module callables.

## CLI and binding continuity

CLI dispatch for `--export-feature-stability-dir` continues to invoke the stable facade name. The facade and new module expose each extracted callable as the same object by identity, so existing imports retain one authoritative implementation without wrappers or copied thresholds.

## Dependency closure

The new module depends only on:

- S5D aggregation primitive: `avg`;
- S5H feature importance: `feature_importance_rows`;
- S5E ML-dataset construction: `build_ml_dataset_rows`;
- S5F feature preparation: `TARGET_COLUMNS` and `build_model_ready_rows`;
- S5G leakage audit: `audit_feature_leakage`;
- S5B generic persistence: `write_csv_rows`;
- S1 compatibility primitives: `safe_float` and `safe_text`;
- Python standard-library `Path` and `Any`.

None of these dependencies imports the feature-stability module or the facade. The facade imports the feature-stability module, so the dependency direction is acyclic in package and direct-script modes.

## Changed files

| File | Role | Prepared SHA-256 |
|---|---|---|
| `tools/trade_inspector/feature_stability.py` | New exact-semantics S5I module | `cc586210413b67ed9338d20236fdf111e9dd745fff1f5bd97fcbf843636a7599` |
| `tools/trade_inspector/inspect_trades.py` | Stable facade and four re-exports | `2ef1ecee3f5345979c0f7645ef5be81dd118d0896cbdd18ce7213247287b40cf` |
| `tests/trade_inspector/test_inspect_trades_characterization.py` | Exact four-callable identity assertions | `daa2dfbaad11021e04b69b471ac792fc8d1af798ebbc8743f0792b37112ef889` |

Pre-extraction facade SHA-256:

`6ef745632f4f2dc267094a9b7dcd70f3fe229309f20c9f729c971a72a9fde5bc`

## Semantic identity

| Binding | AST SHA-256 | Source-segment SHA-256 |
|---|---|---|
| `median` | `b67488365efcb6e5e3322d112994195192e7eb794200294f5ad80e0c57437c80` | `e1746c4b99e4d481286bf01a0690decbd7d85e396e441346b0518f47519486b5` |
| `std` | `ed900163fb22577e4ad0f1cbae3d02d0466de21d2c20884dc2985f30b6deedca` | `9c80c04bd91b8d63435b729906a2fa52a163d09efb178e276cab5a03cf8185c3` |
| `stability_class` | `353087d190df313e902058fde8a2073874e2ed793b0670879d53a95d802dac66` | `356b1a1c820761776d194759836876d955abf68bd4a9e2cfdbc8150fd4eb6302` |
| `export_feature_stability` | `3d079b12c006efc992d31c051de4f72e5a2e0bd4f9a28480741efd5ca892df7e` | `0f1fad1a1b87072dcaec6cc4fe88dc5f41eab5cd3dda17091a267b3c3d8f5758` |

All eight fingerprints are unchanged. Boundary verification confirms exactly the four functions in the new module and no duplicate local definition in the facade.

## Artifact-contract continuity

| Artifact | SHA-256 |
|---|---|
| `feature_stability_v5c.csv` | `e065376bcb0c8ac50034ecedc568f1f42757c4de3e2f3d5664cf1728b19676c1` |
| `feature_stability_v5c_manifest.csv` | `c596df9916a3f2232c52a972d772f17a9ad51c3b1a977e1cb2148dac89866b7e` |
| `feature_stability_v5c_target_matrix.csv` | `b1d3e3e6eb1dd0b5957a5c421f267dbc82021ad6e77f3e99b7e4e6a622561f3c` |
| Three-row filename-to-hash manifest | `052de759d98246fd11e5c77beac125edee974e75f6aea4e0a6b6d9375b36031e` |
| Empty manifest CSV | `64f12c76958672da15694846fea8a67e4c99988381d0ae4d15076a2f561dd149` |
| Empty filename-to-hash manifest | `34061f834ca1aca459872696beb07e10bf199072d318b06aa47057225b30c52a` |
| Zero-byte empty stability or matrix CSV | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |

The 32-feature by 9-target contract, 90 Top-10 and 180 Top-20 memberships, feature and target ordering, matrix schema, sample-standard-deviation semantics, stability-score formula and clamps, class thresholds, exact 30-row reliability boundary, WARN/PASS status, warning text, filenames, CSV bytes, overwrite behavior, foreign-file preservation, exact stdout, and empty stderr all remain unchanged.

## Focused validation

Command:

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest -v tests.trade_inspector.test_inspect_trades_characterization
```

Result:

```text
Ran 48 tests
OK
```

The focused suite asserted exact identity for all four facade callables. The hermetic direct-execution test passed, covering the non-package import path.

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

- No statistical formula, class threshold, feature or target order, rank, score, class count, reliability threshold, warning, schema, filename, CSV byte, overwrite behavior, stdout behavior, or stderr behavior changed.
- No dataset, feature-preparation, leakage-audit, feature-importance, persistence, archive-intake, diagnosis, identity, aggregation, or label behavior changed.
- No CLI option, default path, dispatch order, public import name, package behavior, or direct-script behavior changed.
- No feature-discovery, global, cross-archive, or multi-archive route moved.
- No archive, market data, label file, registry, runtime input, generated repository artifact, or live state was read or modified.
- IU4 ENFORCED, Live-L1, Exchange, Live, inputs, strategies, policies, and gates remain unchanged and locked.
- The foreign untracked file `scripts/build_rcc002_spec_bundle.py` was not read, modified, staged, or included.

## Outcome

S5I feature-stability extraction is complete within its characterized boundary. The next controlled work is S5I extraction branch integration followed by an S5J route-specific characterization gate for feature-discovery export before any feature-discovery extraction.
