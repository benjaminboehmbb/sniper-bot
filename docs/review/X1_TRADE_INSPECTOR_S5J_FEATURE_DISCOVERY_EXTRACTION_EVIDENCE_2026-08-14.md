# X1 Trade Inspector S5J Feature Discovery Extraction Evidence — 2026-08-14

Status: **PASS**

Branch: `codex/x1-trade-inspector-s5j-feature-discovery-extraction-2026-08-14`

Base commit: `ff99ce71fcab6b7c4e58de2193e2034027936679`

## Scope

The S5J predictive-signal feature-discovery implementation was moved without semantic changes from `tools/trade_inspector/inspect_trades.py` into the dedicated module `tools/trade_inspector/feature_discovery.py`.

Extracted production surface:

- `safe_rate`;
- `discover_signal_groups`;
- `classify_signal_support`;
- `classify_signal_reliability`;
- `discover_pair_groups`;
- `export_predictive_signal_discovery`.

`tools/trade_inspector/inspect_trades.py` imports and reexports the six bindings in package and direct-script modes. The characterization test binds each facade symbol by object identity to the extracted implementation. No CLI dispatch, runtime input, archive, market data, generated repository artifact, IU4 mode, exchange, or live path changed.

## Semantic identity

Each extracted function retains both its pre-extraction AST fingerprint and exact source-segment fingerprint.

| Binding | AST SHA-256 | Source-segment SHA-256 |
|---|---|---|
| `safe_rate` | `cdbf7e391d7bf7d91a0eef9835007156cf1c78502d21c7ad02c9dd3ab2808031` | `9668cadab9114e880ce70c70e19a4a7a75a12c2e669d4e992f80b776f191f43f` |
| `discover_signal_groups` | `265c1423add9ae07b27fb254fd3a5bf12cbed730dcbdeb6589a9349736bed5fd` | `a868dae8c64801191338e2321cf7c7b130aebef26624a4dae57a74dd6d4458f3` |
| `classify_signal_support` | `ba5f66acdd1d12718e70a386dae8e5fbe2dc3380ed65eeb77ef276a9efcb5e83` | `edb35ea10b3cfd781b6ed2e53e7c07fa72d7c1c962bc4024f4e8f433b4fe716e` |
| `classify_signal_reliability` | `d5d73d18a2552d74395750db846d368a3320d40ea153d9620b526e31aa87dab1` | `abf1c827b599eacb043607af195a640511b0dfb66e60e8b31e459cef01cf1333` |
| `discover_pair_groups` | `ffb3af2bcfe1b5f313577b5f38505047c90f78d25e909359b9187403ec915401` | `91e53a302262fe4c518585a0a9b7624548d57a6ce5b1250a0f438f46be249bb1` |
| `export_predictive_signal_discovery` | `72a6eca285509cc424e6a7defbbd62c12cb6dad5fff4a90dd5499b971bd41618` | `5aa9a6053bc9210d3e52175a826f52631defaa70798aeb49d3fb60f8065a3b0b` |

Prepared file SHA-256 values:

| File | SHA-256 |
|---|---|
| `tools/trade_inspector/feature_discovery.py` | `975775619e1d63eb167526acb033e7e4c25749e0ad7a37fdf2137dabdebea980` |
| `tools/trade_inspector/inspect_trades.py` | `1f232a5d0b27fbe54be2acd45909079664e0bb7d43dfb4d5d77c0515318d9154` |
| `tests/trade_inspector/test_inspect_trades_characterization.py` | `d3afdd81a1f3902dc39d70c6cbbf8cdd03e132353c0c64d7a11ed53da1f9bec8` |

## Artifact parity

The complete three-row fixture reproduced all 19 gate-bound CSV artifacts exactly:

| Artifact | SHA-256 |
|---|---|
| `predictive_signal_discovery_by_entry_atr_signal.csv` | `3ad2be8913f34a464764f8fbfae03f148b6378cf8fd285bd2503da8da0f7adca` |
| `predictive_signal_discovery_by_entry_ma200_signal.csv` | `9ed93eef28752fbd016c0aa1b733ee87bb8a40c0de0ad7fb389bd0ca7b618a9a` |
| `predictive_signal_discovery_by_entry_ma200_signal__entry_mfi_signal.csv` | `9d5d28abf849010899b211db6320846f230d7b91259163131e1191de7b4963d8` |
| `predictive_signal_discovery_by_entry_mfi_signal.csv` | `383bdc338f946ec3840f8588f5a7c51b6bbd9cbe0940e122ad613ef72195c54d` |
| `predictive_signal_discovery_by_entry_regime_label.csv` | `700bd46a5571f850ff87f8dfef882ed5e5d72f16a0822bda1bd75b4978ed5abe` |
| `predictive_signal_discovery_by_entry_regime_label__entry_atr_signal.csv` | `4f3bdf904ff3ffbdefcc48ff917c4d6c4f450781d3f50f8dd831aa1c3701e14f` |
| `predictive_signal_discovery_by_entry_regime_label__entry_risk_label.csv` | `cae53cc8bba6fa20eba91ebc97ef59333924ac3af8a094ab3b56f84757189714` |
| `predictive_signal_discovery_by_entry_risk_label.csv` | `fc97279e76e73c8a19dd9c091d58cc72514ccd5033057e3571f56115646dc368` |
| `predictive_signal_discovery_by_entry_risk_label__regime_aligned.csv` | `be976117d93ca9362fb5b40d0365de9497332bb9398e98daec71f137c3d24bea` |
| `predictive_signal_discovery_by_entry_score_at_entry.csv` | `5579db97ea8072ed1d3a8211528dfe1521aee7613980caf19920ad67ddf57bf6` |
| `predictive_signal_discovery_by_entry_score_at_entry__entry_risk_label.csv` | `156fcd8ae05328fcb3862587364a0eca2bc46875362a99b2dc73680e3f857dbe` |
| `predictive_signal_discovery_by_regime_aligned.csv` | `359d827266721f5abc107137684f7c5fcc567f27ad41cadeafb365b0a1b954bb` |
| `predictive_signal_discovery_by_risk_good_at_entry.csv` | `e7f18ab9126f8c4e8fdf318e5fa308eba87c217047b60389c2241f131bb5e932` |
| `predictive_signal_discovery_by_trade_family.csv` | `a36e72e74bc6946db311f33ad29d005b1cf4fb96f4c111f21b85bca72b32abab` |
| `predictive_signal_discovery_by_trade_family_group.csv` | `2e7ceb7c0b3a02272fa3e0ff382a9cac3f5a8deaa1eaec5a0422cd93375beacb` |
| `predictive_signal_discovery_by_trade_family_group__entry_risk_label.csv` | `73b0eaad9740672e4774b95d7a4c51d9bdc4a20fbdf5d45d33b133706b52ad90` |
| `predictive_signal_discovery_v6_all.csv` | `e23c6f8e368e6c4f7e61348dcf21eab14fb3e2bc278be91ddb70c9cd77e18e42` |
| `predictive_signal_discovery_v6_manifest.csv` | `3fdb191601b73f5e286299427055c8514412454905e88f1b44429a632019cd9a` |
| `predictive_signal_discovery_v6_top.csv` | `e23c6f8e368e6c4f7e61348dcf21eab14fb3e2bc278be91ddb70c9cd77e18e42` |

Canonical complete filename-to-hash fingerprint:

`6584edce59c245c9d269ff0e5bc9da94b2ec256f81ffab4761715c4bd7558da0`

The empty-input contract also remains exact: all 18 derived CSVs are zero-byte files with SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`, the empty manifest SHA-256 is `309dd83128ca34f11abee60ddc337db67364b08bba07e881adb34cdb1f508e00`, and the empty filename-to-hash fingerprint is `f4a0db55691d25ce74b81075dfea479fff94a6bd0af18a777e4b134810438a3b`.

The exact 30-row fixture remains `PASS`, evaluates 480 unique groups, writes exactly 50 top rows, and preserves the top file as the sorted all-file prefix. Route-owned overwrite, foreign-CSV preservation and listing, stable sorting, pair-source immutability, stdout order, and empty stderr remain bound.

## Validation

Focused characterization:

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest -v tests.trade_inspector.test_inspect_trades_characterization

Ran 53 tests
OK
```

Full regression:

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -s tests/regression -p 'test_*.py'

Ran 170 tests
OK
```

`git diff --check` passed.

## Safety and next gate

This is a structure-only extraction. IU4 ENFORCED, Live-L1, exchange, and live execution remain locked. No source data or runtime input was changed.

After integrating this extraction branch into `main`, the next development step is the S5K multi-archive-loader characterization gate for `load_archive_registry_md`, `load_rows_for_archive`, and `export_multi_archive_loader`, before any corresponding extraction.
