# X1 Trade Inspector S5M Cross-Archive Feature Importance Characterization Gate Evidence — 2026-08-15

Status: **PASS**

Branch: `codex/x1-trade-inspector-s5m-cross-archive-feature-importance-characterization-gate-2026-08-15`

Base commit: `dfde361543d5ed77d98ef3d2cc67507f9bb1272d`

## Scope

This gate freezes the current S5M cross-archive feature-importance route before extraction from `tools/trade_inspector/inspect_trades.py`.

Bound production surface:

- `export_cross_archive_feature_importance`.

The gate uses only synthetic Trade Inspector rows and temporary output directories. It does not read repository archives or market data and does not change production code, runtime inputs, policies, strategies, or generated runtime artifacts.

## Production identity

`tools/trade_inspector/inspect_trades.py` remained byte-identical throughout the gate.

SHA-256 before and after:

`e7e55f04fc178646b22dfec07691825b2e21198a98474cd7a9743d02c3c17c05`

| Binding | AST SHA-256 | Source-segment SHA-256 |
|---|---|---|
| `export_cross_archive_feature_importance` | `5a2de6f4df421c607ce9b0ed26355eada464bab9155fa5bed2f0b2bc19063354` | `1c093aa95d7510719c474658369887d68e9ce8c91c5353f140160e22fb63f545` |

Prepared characterization-test SHA-256:

`2b87c67266a878edfa7e35e483b999877961cee686bac8b1aa60842288756f48`

## Complete artifact contract

The three-row single-archive fixture binds the combined export, nine target-specific exports, manifest, and Markdown summary.

| Artifact | SHA-256 |
|---|---|
| `cross_archive_feature_importance_v7e.csv` | `749950a0dacef53d7e7a208ecb5a118ffbbe442403ec32a9a63fb2d93f2e8910` |
| `cross_archive_feature_importance_v7e_manifest.csv` | `0c7f7368ba18b46a769f9dbfe3d445a0037a8b61afbaa6c4a7e95e00ed194811` |
| `cross_archive_feature_importance_v7e_target_exit_efficiency_high.csv` | `47beb040614707771a8d8050c2c8969ad9ba27b61966179333c343d86129ecc0` |
| `cross_archive_feature_importance_v7e_target_future_return_24h_pct.csv` | `d225f91d6a3b15caeea9b81fcb10e6188e66c13a4349aca346e7e87bef755d3c` |
| `cross_archive_feature_importance_v7e_target_future_return_72h_pct.csv` | `880ea35a2b4c7980f0ef7db314e0256874de1959ca4455cf886b5da5c0d6d6d0` |
| `cross_archive_feature_importance_v7e_target_loser.csv` | `bcb0f9d2bdd682ceb38129dee56bc4db0516d7f39ec1e69183f12514e96afc5f` |
| `cross_archive_feature_importance_v7e_target_opportunity_loss_high.csv` | `ad928ff18362af19e2c6db67d8ae929f7d31dbc427822a9017f7fb8560c52c0e` |
| `cross_archive_feature_importance_v7e_target_pnl_pct.csv` | `27d01db73db281c77d3b42c19168fdbb504189a376de6c65ae851f813a1c692e` |
| `cross_archive_feature_importance_v7e_target_quality_bad.csv` | `e2c848c3212cec8e261299846f2a473cf6cefbb80cc7f76f93b6c5d3859d9457` |
| `cross_archive_feature_importance_v7e_target_quality_good.csv` | `e298ce3935cc72601e2506d78892dcff0159fa5778dd09d1ce05e8c7806488cf` |
| `cross_archive_feature_importance_v7e_target_winner.csv` | `197b101b8f83d51dcb40fa4b20a58ff7dc896a167a9e8aeef9d5f39353590808` |
| `v7e_cross_archive_feature_importance_summary.md` | `d013f26ac5cc6b9e79317314c6c10b4ba7ebc7e3a3154cc39b2c795782a985ad` |

Canonical filename-to-hash fingerprint:

`75d33b19cb909d65137f5bd7549266360a80e3d750e26637aa9e502870da6dc3`

The fixture produces 297 rows: 33 allowed features for each of nine targets. Global descending importance order, target membership, per-target row counts, method fields, row-level archive enrichment, manifest values, exact stdout, and empty stderr are bound.

## Empty and boundary contracts

Empty input creates the same twelve filenames. The combined and nine target-specific CSV files are zero-byte artifacts. The empty manifest SHA-256 is `a183b64db67889b1e2990cb6fb36a01357fdacb7b439b6c6b84f092f409db8ef`; the empty summary SHA-256 is `ae7216fce548b0cd30a0ed0e240d106e2df01d12a6f4df026ce932c20c4144b9`; and the complete empty filename-to-hash fingerprint is `77e16b2cb6f2036de7a9926a7b884fb65c60f0cfeaa0144231f9d6e5206cdb8e`.

Three boundary fixtures prove the independent conditions:

| Rows | Source archives | Mode | Status | Statistical interpretation |
|---:|---:|---|---|---|
| 29 | 2 | `multi_archive_analysis` | `WARN` | `no` |
| 30 | 1 | `single_archive_infrastructure_validation` | `PASS` | `no` |
| 30 | 2 | `multi_archive_analysis` | `PASS` | `yes` |

The current asymmetric enrichment is explicitly frozen: the manifest reflects the actual source-archive count, while every importance row retains `archive_scope=single_archive_validation`, `archive_count=1`, and the call-scope `source_archive_id`.

An overwrite fixture proves replacement of stale owned output while preserving and listing a foreign file. Exact sorted directory-listing output is bound.

## Validation

Focused characterization:

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest -q tests.trade_inspector.test_inspect_trades_characterization

Ran 67 tests
OK
```

Full regression:

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -s tests/regression -p 'test_*.py'

Ran 170 tests
OK
```

`git diff --check` passed.

## Safety and next step

Only characterization tests and this evidence document changed. IU4 ENFORCED, Live-L1, Exchange, and Live remain locked. No source data or runtime input was changed.

After integrating this gate into `main`, the next development step is the structure-only S5M extraction into a dedicated cross-archive feature-importance module, preserving all bound semantics and facade bindings.
