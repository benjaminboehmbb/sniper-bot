# X1 Trade Inspector S5O Global Trade Database Repair Evidence — 2026-08-15

Status: **PASS**

Branch: `codex/x1-trade-inspector-s5o-global-trade-database-repair-2026-08-15`

Base commit: `561edf7c637da46561e6d1f4a419edd48d37e407`

## Scope

This change repairs the deterministic S5O V7C manifest failure previously frozen by the global-trade-database characterization gate.

Bound production surface:

- `export_global_trade_database` in `tools/trade_inspector/inspect_trades.py`.

No route is extracted or otherwise refactored in this change. The production delta is one manifest value.

## Root cause and historical contract

The route was originally introduced by commit `71c2676` with the literal manifest value:

```text
statistical_interpretation_allowed=no
```

Commit `b86e654` later replaced that literal with `statistical_allowed` while expanding separate cross-archive routes. No local definition or parameter for that name exists in `export_global_trade_database`, so V7C wrote its data CSV and summary and then raised `NameError` before writing its manifest.

The repair restores the original literal `no`. This is the correct semantic contract because V7C accepts one call-scope `archive_id`, rewrites every output row to that identity, labels its summary `single-archive validation`, and explicitly prohibits statistically robust cross-archive interpretation.

The repair does not infer permission from row count or archive-like fields embedded in input rows.

## Production identity

Before repair, `tools/trade_inspector/inspect_trades.py` SHA-256 was:

`2599e94b3b225f7d3750424cc34e094c1318d08b371e3b96fce1f140a6f07136`

After repair:

`51617fb019f3738c864c80582a68b91c243145543c20acaf7aefe4bf8dafb1eb`

| Binding | AST SHA-256 | Source-segment SHA-256 |
|---|---|---|
| repaired `export_global_trade_database` | `c90684e01fc6fdd739975f3772e1c23d9c9743358ae20af11b28b7a3975408b2` | `12f8372dd8696f641a1cd3ad1130814b79790b45e56b4d5711b3bd1fbe2ea983` |

Prepared characterization-test SHA-256:

`5c8940a4844c94daee17879f432b2ab6ae7b2628402acb6c7c9a3e814fbe4dc7`

## Repaired complete artifact contract

The three-row call-scope fixture now completes without exception and writes exactly three owned artifacts.

| Artifact | SHA-256 |
|---|---|
| `global_trades_v7c.csv` | `184fd8c2f3076e5b4509b77bf7ae0dd5bd513615c05b08de4677c2b35e4ca5ea` |
| `global_trades_v7c_manifest.csv` | `20151c6b74a0c4e96d9bc996f15340317e2b536373d2c00c20dba739539b3ba2` |
| `v7c_global_trade_database_summary.md` | `7a792198bed8f875edbec92d34020bec8b199bca84654bcfb49f2ce2c64e3094` |

Canonical filename-to-hash fingerprint:

`6b9fcf15e28a4e4249309665ac533abd087a6c57e2a336f52c93334c980c6abe`

The manifest is bound to:

- `archive_id=CALL-SCOPE`;
- `trade_count=3`;
- `output_file=global_trades_v7c.csv`;
- `summary_file=v7c_global_trade_database_summary.md`;
- `status=infrastructure_validation`;
- `statistical_interpretation_allowed=no`.

The existing 131-field data schema, final identity fields, local/global ID sequence, call-scope archive rewrite, one-based row indices, exact sorted stdout, and empty stderr remain bound.

## Empty, identity, boundary, and overwrite contracts

Empty input now completes with the same three filenames:

| Artifact | SHA-256 |
|---|---|
| `global_trades_v7c.csv` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `global_trades_v7c_manifest.csv` | `71792138676b4cdb42dd621de6c631a635935e2b5a74ade131d27ad2ffb73fd8` |
| `v7c_global_trade_database_summary.md` | `dbdf848215a5408060c79d170858a92f5697b7da8eeb594799e6ac1701bbf178` |

Canonical empty fingerprint:

`40d6f366a69f9c7e2462890a195be0fee455446032573b075171f44544eae37a`

The empty manifest binds `trade_count=0` and `statistical_interpretation_allowed=no`.

The existing local-ID fallback order remains `trade_id`, `stable_trade_id`, `local_trade_id`, `id`, then generated `T######`.

Boundary fixtures with 29 rows/two embedded archives, 30 rows/one embedded archive, and 30 rows/two embedded archives all complete with the exact call-scope row count and `statistical_interpretation_allowed=no`. Input archive-like fields therefore cannot elevate this single-archive infrastructure export.

The overwrite fixture proves that stale owned output is replaced, all repaired owned artifacts are created, a foreign file is preserved, and the exact sorted directory-listing output includes that foreign file without mutating it.

## Validation

Focused characterization:

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest -q tests.trade_inspector.test_inspect_trades_characterization

Ran 77 tests
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

Only the one-line V7C manifest repair, its S5O characterization contracts, and this evidence document changed. IU4 ENFORCED, Live-L1, Exchange, and Live remain locked. No source data or runtime input was changed.

After integrating this repair into `main`, the next development step is the structure-only S5O global-trade-database extraction. The extraction must preserve the repaired three-artifact fingerprints, manifest policy, facade binding, stdout/stderr, overwrite behavior, and all existing regression contracts.
