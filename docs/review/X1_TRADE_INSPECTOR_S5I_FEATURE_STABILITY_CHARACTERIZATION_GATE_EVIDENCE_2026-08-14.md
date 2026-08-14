# X1 Trade Inspector S5I Feature Stability Characterization Gate Evidence — 2026-08-14

Status: **PASS**

Branch: `codex/x1-trade-inspector-s5i-feature-stability-characterization-gate-2026-08-14`

Base commit: `f0cac45b6f7b1e54881e31c80659c1baba69d205`

## Scope

This gate freezes the current S5I feature-stability route before any extraction from `tools/trade_inspector/inspect_trades.py`.

Bound production surface:

- `median`;
- `std`;
- `stability_class`;
- `export_feature_stability`.

No production implementation, CLI dispatch, runtime input, archive, market data, label data, or generated repository artifact changed while establishing the gate.

## Production identity

`tools/trade_inspector/inspect_trades.py` remained byte-identical throughout the gate.

SHA-256 before and after:

`6ef745632f4f2dc267094a9b7dcd70f3fe229309f20c9f729c971a72a9fde5bc`

| Binding | AST SHA-256 | Source-segment SHA-256 |
|---|---|---|
| `median` | `b67488365efcb6e5e3322d112994195192e7eb794200294f5ad80e0c57437c80` | `e1746c4b99e4d481286bf01a0690decbd7d85e396e441346b0518f47519486b5` |
| `std` | `ed900163fb22577e4ad0f1cbae3d02d0466de21d2c20884dc2985f30b6deedca` | `9c80c04bd91b8d63435b729906a2fa52a163d09efb178e276cab5a03cf8185c3` |
| `stability_class` | `353087d190df313e902058fde8a2073874e2ed793b0670879d53a95d802dac66` | `356b1a1c820761776d194759836876d955abf68bd4a9e2cfdbc8150fd4eb6302` |
| `export_feature_stability` | `3d079b12c006efc992d31c051de4f72e5a2e0bd4f9a28480741efd5ca892df7e` | `0f1fad1a1b87072dcaec6cc4fe88dc5f41eab5cd3dda17091a267b3c3d8f5758` |

## Statistical and classification contract

The focused contract binds:

- empty median and samples shorter than two for standard deviation return `0.0`;
- median sorts its input values and uses the midpoint or the mean of the two center values;
- `std` is sample standard deviation with an `n-1` denominator;
- stability classes use inclusive lower bounds: elite at 90, stable at 75, moderate at 50, weak at 25, and unstable below 25;
- values above 100 remain elite and negative values remain unstable.

## Complete artifact contract

The three-row fixture uses trade IDs `A`, `K`, and `Z` and binds the complete 32-feature by 9-target stability surface.

| Artifact | SHA-256 |
|---|---|
| `feature_stability_v5c.csv` | `e065376bcb0c8ac50034ecedc568f1f42757c4de3e2f3d5664cf1728b19676c1` |
| `feature_stability_v5c_manifest.csv` | `c596df9916a3f2232c52a972d772f17a9ad51c3b1a977e1cb2148dac89866b7e` |
| `feature_stability_v5c_target_matrix.csv` | `b1d3e3e6eb1dd0b5957a5c421f267dbc82021ad6e77f3e99b7e4e6a622561f3c` |

Canonical filename-to-hash fingerprint:

`052de759d98246fd11e5c77beac125edee974e75f6aea4e0a6b6d9375b36031e`

The complete contract is exactly:

- 32 unique stability rows and 32 feature-matrix rows;
- 9 target measurements and ranks per feature;
- 90 total Top-10 memberships and 180 total Top-20 memberships;
- descending stable ordering by `stability_score`;
- alphabetically ordered feature-matrix rows;
- zero elite, stable, and moderate features;
- 10 weak and 22 unstable features;
- `method=multi_target_absolute_pearson_stability`;
- `status=WARN`;
- `warning=dataset_too_small_for_reliable_stability`.

The target order is:

1. `target_winner`;
2. `target_loser`;
3. `target_quality_good`;
4. `target_quality_bad`;
5. `target_opportunity_loss_high`;
6. `target_exit_efficiency_high`;
7. `target_pnl_pct`;
8. `target_future_return_24h_pct`;
9. `target_future_return_72h_pct`.

## Empty-input and reliability-boundary contracts

Empty input creates the same three filenames. The stability and target-matrix artifacts are zero-byte files with SHA-256:

`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`

The empty manifest CSV SHA-256 is:

`64f12c76958672da15694846fea8a67e4c99988381d0ae4d15076a2f561dd149`

The empty filename-to-hash fingerprint is:

`34061f834ca1aca459872696beb07e10bf199072d318b06aa47057225b30c52a`

The empty route retains nine analyzed targets and reports zero rows and zero features with the same `WARN` status and warning. The exact 30-row boundary changes the manifest and console status to `PASS` with warning `none`.

## Filesystem and console contract

The gate binds recursive directory creation, route-owned overwrite, preservation and sorted listing of foreign CSVs, exact metric output order, exact path formatting, and empty stderr.

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
| `tests/trade_inspector/test_inspect_trades_characterization.py` | `abf813d40e493f9bcb2463b8f024d4d75efc8c3d4dcc41c9dea6e7e3f45a40f4` |
| `tools/trade_inspector/inspect_trades.py` | `6ef745632f4f2dc267094a9b7dcd70f3fe229309f20c9f729c971a72a9fde5bc` |

## Safety boundary

- Production code remained byte-identical.
- No statistical formula, class threshold, feature or target order, rank, score, class count, reliability threshold, warning, schema, filename, CSV byte, overwrite behavior, stdout behavior, or stderr behavior changed.
- No archive, market data, label file, registry, runtime input, generated repository artifact, or live state was read or modified.
- IU4 ENFORCED, Live-L1, Exchange, Live, inputs, strategies, policies, and gates remain unchanged and locked.
- The foreign untracked file `scripts/build_rcc002_spec_bundle.py` was not read, modified, staged, or included.

## Outcome

S5I feature stability is fully characterized for controlled extraction. The next controlled work is S5I characterization-gate branch integration followed by extraction of the feature-stability closure into an acyclic module, with the four public callables re-exported for stable CLI and import consumers.
