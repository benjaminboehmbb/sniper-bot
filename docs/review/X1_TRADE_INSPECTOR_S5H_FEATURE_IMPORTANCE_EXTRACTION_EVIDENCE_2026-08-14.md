# X1 Trade Inspector S5H Feature Importance Extraction Evidence — 2026-08-14

Status: **PASS**

Branch: `codex/x1-trade-inspector-s5h-feature-importance-extraction-2026-08-14`

Base commit: `7d8ccd2d5ec48028a20ef8724d9fbc807d371aa6`

## Decision

The characterized S5H feature-importance closure was extracted from `tools/trade_inspector/inspect_trades.py` into `tools/trade_inspector/feature_importance.py` without changing implementation semantics or public names.

Extracted bindings:

- `pearson_abs`;
- `feature_importance_rows`;
- `export_feature_importance`.

`inspect_trades.py` remains the stable CLI and import facade. Package imports and direct file execution both import and re-export the three exact new-module callables.

## Downstream-binding continuity

`feature_importance_rows` remains consumed by later feature-stability and cross-archive paths in the facade. The extraction preserves a single authoritative callable: the facade and new module expose the same object by identity, and existing downstream calls resolve the imported binding without a back-import.

CLI dispatch for `--export-feature-importance-dir` continues to invoke the stable facade name.

## Dependency closure

The new module depends only on:

- S5D aggregation primitive: `avg`;
- S5E ML-dataset construction: `build_ml_dataset_rows`;
- S5F feature preparation: `TARGET_COLUMNS` and `build_model_ready_rows`;
- S5G leakage audit: `audit_feature_leakage`;
- S5B generic persistence: `write_csv_rows`;
- S1 compatibility primitives: `safe_float` and `safe_text`;
- Python standard-library `Path` and `Any`.

None of these dependencies imports the feature-importance module or the facade. The facade imports the feature-importance module, so the dependency direction is acyclic in package and direct-script modes.

## Changed files

| File | Role | Prepared SHA-256 |
|---|---|---|
| `tools/trade_inspector/feature_importance.py` | New exact-semantics S5H module | `91f0b7fadd4124ddcce2be89b29dd1a481ba3e3c84896dd2580b0b49cabbadad` |
| `tools/trade_inspector/inspect_trades.py` | Stable facade and three re-exports | `6ef745632f4f2dc267094a9b7dcd70f3fe229309f20c9f729c971a72a9fde5bc` |
| `tests/trade_inspector/test_inspect_trades_characterization.py` | Exact three-callable identity assertions | `5676d539be4d6ed2cda4d6cf6c76bf102fdfd36331be7cbae7bf8d78de98702f` |

Pre-extraction facade SHA-256:

`902ea02dcf07c3597d3ab670a8f0f25f539b3ed5594f29550137a3fd96e6b5f9`

## Semantic identity

| Binding | AST SHA-256 | Source-segment SHA-256 |
|---|---|---|
| `pearson_abs` | `3f4c5d7e59965b09fb8a2dee9874140828cbe3d552597e3fcd90045e0ece6c66` | `e51811054409057df17de82a17919895babe1f268c4c89c7398a8b88c297c438` |
| `feature_importance_rows` | `02aea41098898781828db4f1d687970a118fb1d11f2a364ff1d9c7b5a9fae4a3` | `91fbb598f0cffb317c1586f97770eebf35bdb62b6d4335c46a5085dea369544b` |
| `export_feature_importance` | `ff4e6070188023436c00db807325ff05e581a49f461f5a0085f5cb0764b65d83` | `c8fe7c581d02023b87745df93aaf1f76b6777ea08f28f8f9b1cba45d7c4e4a74` |

All six fingerprints are unchanged. Boundary verification confirms exactly the three functions in the new module and no duplicate local definition in the facade.

## Artifact-contract continuity

| Artifact | SHA-256 |
|---|---|
| `feature_importance_v5.csv` | `3d0b7d717501abda8b9ca2b8923c137542a6892b9d0ce91225371aa033631208` |
| `feature_importance_v5_manifest.csv` | `7da05e42a2063959df060f14115948405ed3ffb267ceaaeacebd8d8a155a412c` |
| `feature_importance_v5_target_exit_efficiency_high.csv` | `2ea760565dc25a28abdc3d2ef53f9115489cf22f837d4436bb12a68712b97b5c` |
| `feature_importance_v5_target_future_return_24h_pct.csv` | `3ba3fc746c83c40cd83471d234d27c1af61667547e2a7efe6e3bdd39471fe009` |
| `feature_importance_v5_target_future_return_72h_pct.csv` | `27c1a66f6a20fbb9dd5ae2448d5b02b22079ce9962356bf2ad6cf2d0ef856f76` |
| `feature_importance_v5_target_loser.csv` | `18571ba0b8424372de4dcd639f7780d24602885447940e5b7cf740f74ea4a492` |
| `feature_importance_v5_target_opportunity_loss_high.csv` | `a72fbc2b0a5d344b007302a32af0770b758ac1f64b5f062da01613479a2df056` |
| `feature_importance_v5_target_pnl_pct.csv` | `cf0e8529066d5ecb33674c2766f81f6c2ff6edb007ba38a2d74152ee302e1435` |
| `feature_importance_v5_target_quality_bad.csv` | `64899183556b9fee75c05275f403737bdad50f990f3db8909cfe6a019384e485` |
| `feature_importance_v5_target_quality_good.csv` | `0d8e5de26a874dbca2f8ff79d5360e2770c73e467766dfee4f62bac3fdb7652a` |
| `feature_importance_v5_target_winner.csv` | `c12cbb10b7ad63862c1124d5a78776ad449fd236d49b3643a43a3dbab1c5f239` |
| Three-row filename-to-hash manifest | `6fcba2761ac06c53a3a2ec407855546fb6b0d8dee039f7426fe6fa0012bf5ca3` |
| Empty manifest CSV | `d7aeacdb72b1c8a94e3c5821810fbdfa4be0ff92291f7fb085a3f380a20914c1` |
| Empty filename-to-hash manifest | `2567d4677cc4ee0e4f3d3368ae5ed103b1cd76726434387ca6f0228b7fb33efa` |
| Zero-byte empty derived CSV | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |

The 32-feature by 9-target, 288-row contract, target ordering, Trade-ID join, unmatched-row exclusion, stable tie order, absolute-Pearson semantics, `rows_used`, method label, no-training declaration, exact 30-row reliability boundary, WARN/PASS status, warning text, filenames, CSV bytes, overwrite behavior, foreign-file preservation, exact stdout, and empty stderr all remain unchanged.

## Focused validation

Command:

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest -v tests.trade_inspector.test_inspect_trades_characterization
```

Result:

```text
Ran 43 tests
OK
```

The focused suite asserted exact identity for all three facade callables. The hermetic direct-execution test passed, covering the non-package import path.

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

- No Pearson behavior, join key, unmatched-row handling, feature order, target order, rank order, score, row count, threshold, warning, schema, filename, CSV byte, overwrite behavior, stdout behavior, or stderr behavior changed.
- No dataset, feature-preparation, leakage-audit, persistence, archive-intake, diagnosis, identity, aggregation, or label behavior changed.
- No CLI option, default path, dispatch order, public import name, package behavior, or direct-script behavior changed.
- No feature-stability, discovery, global, cross-archive, or multi-archive route moved.
- No archive, market data, label file, registry, runtime input, generated repository artifact, or live state was read or modified.
- IU4 ENFORCED, Live-L1, Exchange, Live, inputs, strategies, policies, and gates remain unchanged and locked.
- The foreign untracked file `scripts/build_rcc002_spec_bundle.py` was not read, modified, staged, or included.

## Outcome

S5H feature-importance extraction is complete within its characterized boundary. The next controlled work is S5H extraction branch integration followed by an S5I route-specific characterization gate for feature-stability export before any feature-stability extraction.
