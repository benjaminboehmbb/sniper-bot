# X1 Trade Inspector S5J Feature Discovery Characterization Gate Evidence — 2026-08-14

Status: **PASS**

Branch: `codex/x1-trade-inspector-s5j-feature-discovery-characterization-gate-2026-08-14`

Base commit: `7e1b2c7f5de8a1807d128e2c49a3b127f053f77c`

## Scope

This gate freezes the current S5J predictive-signal feature-discovery route before any extraction from `tools/trade_inspector/inspect_trades.py`.

Bound production surface:

- `safe_rate`;
- `discover_signal_groups`;
- `classify_signal_support`;
- `classify_signal_reliability`;
- `discover_pair_groups`;
- `export_predictive_signal_discovery`.

No production implementation, CLI dispatch, runtime input, archive, market data, label data, or generated repository artifact changed while establishing the gate.

## Production identity

`tools/trade_inspector/inspect_trades.py` remained byte-identical throughout the gate.

SHA-256 before and after:

`2ef1ecee3f5345979c0f7645ef5be81dd118d0896cbdd18ce7213247287b40cf`

| Binding | AST SHA-256 | Source-segment SHA-256 |
|---|---|---|
| `safe_rate` | `cdbf7e391d7bf7d91a0eef9835007156cf1c78502d21c7ad02c9dd3ab2808031` | `9668cadab9114e880ce70c70e19a4a7a75a12c2e669d4e992f80b776f191f43f` |
| `discover_signal_groups` | `265c1423add9ae07b27fb254fd3a5bf12cbed730dcbdeb6589a9349736bed5fd` | `a868dae8c64801191338e2321cf7c7b130aebef26624a4dae57a74dd6d4458f3` |
| `classify_signal_support` | `ba5f66acdd1d12718e70a386dae8e5fbe2dc3380ed65eeb77ef276a9efcb5e83` | `edb35ea10b3cfd781b6ed2e53e7c07fa72d7c1c962bc4024f4e8f433b4fe716e` |
| `classify_signal_reliability` | `d5d73d18a2552d74395750db846d368a3320d40ea153d9620b526e31aa87dab1` | `abf1c827b599eacb043607af195a640511b0dfb66e60e8b31e459cef01cf1333` |
| `discover_pair_groups` | `ffb3af2bcfe1b5f313577b5f38505047c90f78d25e909359b9187403ec915401` | `91e53a302262fe4c518585a0a9b7624548d57a6ce5b1250a0f438f46be249bb1` |
| `export_predictive_signal_discovery` | `72a6eca285509cc424e6a7defbbd62c12cb6dad5fff4a90dd5499b971bd41618` | `5aa9a6053bc9210d3e52175a826f52631defaa70798aeb49d3fb60f8065a3b0b` |

## Scoring and classification contract

The focused contract binds:

- zero-denominator rates return `0.0`;
- support classes change at counts 3, 10, and 30;
- datasets below 30 rows always return reliability score 0, `NOT_ACTIONABLE`, and `DATASET_TOO_SMALL`;
- reliability scoring preserves count, support-ratio, and discovery-status contributions;
- score 40 is exactly `WATCH_ONLY / MEDIUM`;
- score 70 is exactly `ACTIONABLE_CANDIDATE / LOW`;
- group edge and support scoring is clamped only at the final discovery score;
- discovery statuses preserve `LOW_SUPPORT`, `WEAK`, `WATCH`, and `PROMISING` precedence;
- pair discovery builds a copied composite key and does not mutate source rows;
- discovery output is sorted descending by score with stable tie order.

## Complete artifact contract

The three-row fixture binds 10 single-key group exports, 6 pair-key exports, all/top rollups, and the manifest.

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

Canonical filename-to-hash fingerprint:

`6584edce59c245c9d269ff0e5bc9da94b2ec256f81ffab4761715c4bd7558da0`

The complete fixture produces exactly 16 groups. All are LOW support, `NOT_ACTIONABLE`, and `DATASET_TOO_SMALL`; the overall route is `WARN`. Because there are fewer than 50 groups, the top artifact is byte-identical to the all-groups artifact.

## Empty-input and boundary contracts

Empty input creates the same 19 filenames. All derived artifacts except the manifest are zero-byte files with SHA-256:

`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`

The empty manifest CSV SHA-256 is:

`309dd83128ca34f11abee60ddc337db67364b08bba07e881adb34cdb1f508e00`

The empty filename-to-hash fingerprint is:

`f4a0db55691d25ce74b81075dfea479fff94a6bd0af18a777e4b134810438a3b`

The exact 30-row fixture with unique group values produces 480 evaluated groups, all `LOW_SUPPORT`, `NOT_ACTIONABLE`, and high-warning. The route changes to `PASS` with warning `none`; the top artifact contains exactly the first 50 rows of the sorted all-groups artifact.

## Filesystem and console contract

The gate binds recursive directory creation, route-owned overwrite, preservation and sorted listing of foreign CSVs, exact metric output order, exact path formatting, and empty stderr.

## Focused validation

Command:

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest -v tests.trade_inspector.test_inspect_trades_characterization
```

Result:

```text
Ran 53 tests
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
| `tests/trade_inspector/test_inspect_trades_characterization.py` | `63ae2bfce7174b1c5fb42a24d9f9d6ca2db28dd184f7d1eaf67b2fd7edebad94` |
| `tools/trade_inspector/inspect_trades.py` | `2ef1ecee3f5345979c0f7645ef5be81dd118d0896cbdd18ce7213247287b40cf` |

## Safety boundary

- Production code remained byte-identical.
- No rate, edge, score, clamp, status precedence, support threshold, reliability threshold, group order, pair construction, top cap, warning, schema, filename, CSV byte, overwrite behavior, stdout behavior, or stderr behavior changed.
- No archive, market data, label file, registry, runtime input, generated repository artifact, or live state was read or modified.
- IU4 ENFORCED, Live-L1, Exchange, Live, inputs, strategies, policies, and gates remain unchanged and locked.
- The foreign untracked file `scripts/build_rcc002_spec_bundle.py` was not read, modified, staged, or included.

## Outcome

S5J feature discovery is fully characterized for controlled extraction. The next controlled work is S5J characterization-gate branch integration followed by extraction of the feature-discovery closure into an acyclic module, with all six public callables re-exported for stable CLI and downstream consumers.
