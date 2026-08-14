# X1 Trade Inspector S5H Feature Importance Characterization Gate Evidence — 2026-08-14

Status: **PASS**

Branch: `codex/x1-trade-inspector-s5h-feature-importance-characterization-gate-2026-08-14`

Base commit: `6e11fab0007b60f78b220d208065029b99a49b02`

## Scope

This gate freezes the current S5H feature-importance route before any extraction from `tools/trade_inspector/inspect_trades.py`.

Bound production surface:

- `pearson_abs`;
- `feature_importance_rows`;
- `export_feature_importance`.

No production implementation, CLI dispatch, runtime input, archive, market data, label data, or generated repository artifact changed while establishing the gate.

## Production identity

`tools/trade_inspector/inspect_trades.py` remained byte-identical throughout the gate.

SHA-256 before and after:

`902ea02dcf07c3597d3ab670a8f0f25f539b3ed5594f29550137a3fd96e6b5f9`

| Binding | AST SHA-256 | Source-segment SHA-256 |
|---|---|---|
| `pearson_abs` | `3f4c5d7e59965b09fb8a2dee9874140828cbe3d552597e3fcd90045e0ece6c66` | `e51811054409057df17de82a17919895babe1f268c4c89c7398a8b88c297c438` |
| `feature_importance_rows` | `02aea41098898781828db4f1d687970a118fb1d11f2a364ff1d9c7b5a9fae4a3` | `91fbb598f0cffb317c1586f97770eebf35bdb62b6d4335c46a5085dea369544b` |
| `export_feature_importance` | `ff4e6070188023436c00db807325ff05e581a49f461f5a0085f5cb0764b65d83` | `c8fe7c581d02023b87745df93aaf1f76b6777ea08f28f8f9b1cba45d7c4e4a74` |

## Pearson and ranking contract

The focused contract binds the current absolute-Pearson behavior:

- empty, one-element, and unequal-length inputs return `0.0`;
- a constant input returns `0.0`;
- perfect positive and negative correlations both return `1.0`;
- features and targets are joined by `trade_id`, not by incidental row position;
- unmatched target rows are excluded from `rows_used`;
- rankings are descending by absolute Pearson correlation;
- equal scores retain the allowed-feature order;
- every row records `method=absolute_pearson_correlation` and `model_training=not_performed`.

## Complete artifact contract

The three-row fixture uses trade IDs `A`, `K`, and `Z` and binds the complete 32-feature by 9-target ranking surface.

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

Canonical filename-to-hash fingerprint:

`6fcba2761ac06c53a3a2ec407855546fb6b0d8dee039f7426fe6fa0012bf5ca3`

The combined artifact contains exactly 288 rows: 32 allowed features for each of these nine targets, in this order:

1. `target_winner`;
2. `target_loser`;
3. `target_quality_good`;
4. `target_quality_bad`;
5. `target_opportunity_loss_high`;
6. `target_exit_efficiency_high`;
7. `target_pnl_pct`;
8. `target_future_return_24h_pct`;
9. `target_future_return_72h_pct`.

The manifest contract is exactly:

- `engine_version=v5`;
- `rows_total=3`;
- `allowed_features=32`;
- `targets_evaluated=9`;
- `method=absolute_pearson_correlation`;
- `model_training=not_performed`;
- `status=WARN`;
- `warning=dataset_too_small_for_reliable_feature_importance`.

## Empty-input and reliability-boundary contracts

Empty input creates the same eleven filenames. Ten artifacts are zero-byte files with SHA-256:

`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`

The empty manifest CSV SHA-256 is:

`d7aeacdb72b1c8a94e3c5821810fbdfa4be0ff92291f7fb085a3f380a20914c1`

The empty filename-to-hash fingerprint is:

`2567d4677cc4ee0e4f3d3368ae5ed103b1cd76726434387ca6f0228b7fb33efa`

The empty route retains nine evaluated targets and reports zero rows and zero allowed features with the same `WARN` status and warning. The exact 30-row boundary changes the manifest and console status to `PASS` with no warning; no model is trained.

## Filesystem and console contract

The gate binds recursive directory creation, route-owned overwrite, preservation and sorted listing of foreign CSVs, exact metric output order, exact path formatting, and empty stderr.

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
| `tests/trade_inspector/test_inspect_trades_characterization.py` | `9dd6b878670eda471d2cba33105ce623e4009483df3fef1709517a4abd1ada77` |
| `tools/trade_inspector/inspect_trades.py` | `902ea02dcf07c3597d3ab670a8f0f25f539b3ed5594f29550137a3fd96e6b5f9` |

## Safety boundary

- Production code remained byte-identical.
- No Pearson behavior, join key, unmatched-row handling, feature order, target order, rank order, score, row count, threshold, warning, schema, filename, CSV byte, overwrite behavior, stdout behavior, or stderr behavior changed.
- No archive, market data, label file, registry, runtime input, generated repository artifact, or live state was read or modified.
- IU4 ENFORCED, Live-L1, Exchange, Live, inputs, strategies, policies, and gates remain unchanged and locked.
- The foreign untracked file `scripts/build_rcc002_spec_bundle.py` was not read, modified, staged, or included.

## Outcome

S5H feature importance is fully characterized for controlled extraction. The next controlled work is S5H characterization-gate branch integration followed by extraction of the feature-importance closure into an acyclic module, with `feature_importance_rows` re-exported for stability and cross-archive consumers.
