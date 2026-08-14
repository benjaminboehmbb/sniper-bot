# X1 Trade Inspector S5D Aggregate CSV Characterization Gate Evidence — 2026-08-14

Status: **PASS — CHARACTERIZATION ONLY**

Branch: `codex/x1-trade-inspector-s5d-aggregate-csv-characterization-gate-2026-08-14`

Base commit: `dc72c6b7057158b1f0fe2e1dfb5083a5bb482f53`

## Decision

The route-specific pre-extraction characterization gate for `export_aggregate_csvs` is complete. No production function, import, CLI path, aggregation rule, output schema, persistence behavior, or runtime input changed.

The gate binds the complete deterministic twelve-CSV artifact set for a synthetic three-row fixture, the distinct empty-input artifact set, overwrite behavior, and the current sorted directory-listing behavior in the presence of an unrelated CSV.

## Changed file

| File | Role | Prepared SHA-256 |
|---|---|---|
| `tests/trade_inspector/test_inspect_trades_characterization.py` | Hermetic S5D route and complete artifact contracts | `c343ebabddca5a6bb052cd9d49329168501ebdd8953589ddfe092e08c6eeddd8` |

Production façade SHA-256 remained unchanged:

`2e959fb28d011b8322774e9a51362da65a9d6c9c55d4dead40a148c8f71ec8f5`

## Production identity

The route and its directly material semantic helpers were recorded before the gate:

| Binding | AST SHA-256 | Source-segment SHA-256 |
|---|---|---|
| `group_rows` | `5cbbdb7bbc9123c5361373cc1b560e2c9396aad92ec3d6ad981847d31cb02d75` | `d05448be3b61224fb5efe1084d702ed8173a3b8b48c0c9a46227e213cabbf3b7` |
| `group_stats` | `506942f64d4287819a31a6f19cfcb349bb800f3135b6d75c0942e23ff03874e5` | `9924e6fd6ec083cdb79d0013c4aab6f34a5bf617940852da551189294450b34e` |
| `compute_root_cause_attribution` | `391ec341aed25c77402d2b0323018c6c484936b084e30b8b8e72cccbfe5d5aae` | `8a0c6388bf68c8738b5435e74ee100098ee37da176be157cf3894bd85cc33554` |
| `export_root_cause_attribution_csv` | `462350a5efee69c0e970b946d3a0b25b0fd5a8a302ac569d6bd2d5a52a8cc999` | `8ff22a7e40666c74fbb10de4609df87bb48fd427c5612814e392089915dd96cd` |
| `aggregate_group_rows` | `9cfe1fc6ce45032115db027e4c7364a6939669bb3fda1373e430daaf3048c4df` | `9c92d0549ebb0932a68680045b82efb9628c1d0b7316e118b72cd71dc1b24caa` |
| `aggregate_top_improvement_rows` | `a49c3badf74b725d142d4354a2056f8ebc300ac2fb075c973d06df76a3cc0091` | `fab6bd4f843a53f6bb92b6bfeabf4eb6823358fcaf9e9f1fcfa4b461548b9ccf` |
| `export_aggregate_csvs` | `3430a90baa6c71ac1219c21f4a398ddc821b224a5813af38aa1b61066a57a952` | `1c06dfd7ffe0e73320fe4edc250a0101e4766f5f20fbcba9abfce7d76a03700c` |

No production extraction was performed in this gate.

## Complete non-empty artifact set

The synthetic fixture deliberately covers winners and losers, repeated and distinct groups, priority sorting, first-row schemas, missing aggregation categories, and weighted multi-cause attribution.

| Artifact | SHA-256 |
|---|---|
| `aggregate_by_entry_regime_label.csv` | `444f3135104d5db59c25f9238278f8d2c3171753aa03df9086c5c906318e297e` |
| `aggregate_by_entry_risk_label.csv` | `59635850e5544d1678b0900a207568a14c821d6f520e4c888c09baa4032a8ad4` |
| `aggregate_by_overall_score_band.csv` | `ed40fed361d3e53871b76611a2e0902da143c052ffef58533b1b6ab835d423af` |
| `aggregate_by_priority.csv` | `c04c2da04d8f90befd1facecc2dcb087cc707956de26ecabdd05ad52e76f4a2c` |
| `aggregate_by_quality_class.csv` | `6059f1334518898da1fbe0f70a14fd823b35653c639bad46e75556d8d97af692` |
| `aggregate_by_regime_aligned.csv` | `c963ddc782716568c05eaf0738193ff9378ea358e93bfec09bf5a08da793ab62` |
| `aggregate_by_root_cause.csv` | `af43230e510123d1ec07dee94a97dce530086195492d02bfb282b0e6553fa673` |
| `aggregate_by_trade_family.csv` | `07005bcfc3304fb9bf71233e0077d9560dff6b99150cdaaef1e7e93a9fe3dede` |
| `aggregate_by_trade_family_group.csv` | `eeef423cc6d382559ce3ed4d66a7a626c8c6a4d2708a1f5ca38ea1fbb6d4cd47` |
| `aggregate_global_summary.csv` | `59ea6e99813dd62b639afe7917b045fc37daa1317e7a41955db7be8c5cd8fa18` |
| `aggregate_root_cause_attribution.csv` | `330e09660421e0b5a178b308a6458242c9f8676ac9ce3e6e6f73927d18eff468` |
| `aggregate_top_improvement_candidates.csv` | `4e2b1fdc169e74a7695840eac490879014afec9b5f81825c9a3be47aea1b3ed9` |

Canonical filename-to-hash manifest SHA-256:

`64e371f979cffe4ca2e01ad18d94fba14f0fea2a90755cb26f1de1a3b1ae1e98`

The gate also binds these material orderings:

- top improvement candidates: `T-C`, `T-A`, `T-B`;
- root-cause group rows by descending total PnL: `entry_quality`, `early_exit`;
- weighted root-cause attribution: `early_exit`, `regime_mismatch`, `entry_quality`.

## Empty-input artifact set

Empty input still creates all twelve paths:

- `aggregate_global_summary.csv` contains one zero-statistics data row and has SHA-256 `4e0fcbcd6382b7330f800a27e4bee758b36434729406735abe18183d3b41870e`;
- the other eleven CSV files are exactly zero bytes, SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.

Canonical empty filename-to-hash manifest SHA-256:

`94705901ba1a8aa982a011665f71480d353a066e83919fc930a429474a13a6c4`

This asymmetry is contractual and must not be normalized during extraction.

## Output-directory contract

The gate binds:

- nested output-directory creation;
- direct overwrite of pre-existing route artifacts;
- preservation of an unrelated `foreign.csv` file;
- stdout header lines exactly naming the output directory and `files:`;
- sorted `*.csv` path listing after the writes;
- the unrelated `foreign.csv` is included in that stdout listing because current behavior enumerates directory contents rather than only route-owned artifacts;
- stderr remains empty.

The directory-content dependency is current behavior, not authorization to change it.

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

## Safety boundary

- No production source file changed.
- No aggregation formula, coercion, grouping key, group order, sort key, limit, schema, field order, filename, CSV byte, overwrite behavior, or stdout behavior changed.
- No CLI option, default path, dispatch order, package import, or direct-script behavior changed.
- No archive, market data, label file, registry, runtime input, generated repository artifact, or live state was read or modified.
- IU4, Live-L1, Exchange, Live, inputs, strategies, policies, and gates remain unchanged and locked.
- The foreign untracked file `scripts/build_rcc002_spec_bundle.py` was not read, modified, staged, or included.

## Outcome

S5D aggregate CSV export is eligible for a separately controlled extraction after this gate is integrated into `main`. Before production movement, the coherent dependency closure must be confirmed so the new module introduces no façade import cycle and preserves every route and helper contract above.
