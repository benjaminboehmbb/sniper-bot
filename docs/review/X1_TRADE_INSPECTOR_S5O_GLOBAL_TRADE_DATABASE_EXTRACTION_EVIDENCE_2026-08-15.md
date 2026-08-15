# X1 Trade Inspector S5O Global Trade Database Extraction Evidence — 2026-08-15

Status: **PASS**

Branch: `codex/x1-trade-inspector-s5o-global-trade-database-extraction-2026-08-15`

Base commit: `9a544e26013669a762b088f17f82dae2dba917dd`

## Scope

This change extracts the repaired V7C global-trade-database export from the Trade Inspector facade into:

- `tools/trade_inspector/global_trade_database.py`.

`tools/trade_inspector/inspect_trades.py` imports and re-exports the same callable for both package and direct-script execution. No V7C data, identity, manifest, output, or overwrite semantics changed.

## Structure and identity

The facade no longer defines `export_global_trade_database`. The only production definition is in `global_trade_database.py`, and the characterization suite binds exact object identity:

```text
inspect_trades.export_global_trade_database is global_trade_database.export_global_trade_database
```

The extracted module depends only on `Path`, `Any`, and the existing `write_csv_rows` persistence seam. It supports both package-relative and direct-script imports consistently with the surrounding Trade Inspector modules.

| File | SHA-256 |
|---|---|
| `tools/trade_inspector/inspect_trades.py` | `ca9a8fc748c87404a3b95a2f990e87e1f0d9c77ab89efb5b7cdbc14549941a13` |
| `tools/trade_inspector/global_trade_database.py` | `496e79074aa2065a92962eca24e527e1b5039fa69f24fff27f72af75d8a04fa6` |
| `tests/trade_inspector/test_inspect_trades_characterization.py` | `2cd03dd4acf4b459010c4c6aa3937facf62bcbf00e8ed244196e8d82d73db489` |

| Extracted binding | AST SHA-256 | Source-segment SHA-256 |
|---|---|---|
| `export_global_trade_database` | `c90684e01fc6fdd739975f3772e1c23d9c9743358ae20af11b28b7a3975408b2` | `12f8372dd8696f641a1cd3ad1130814b79790b45e56b4d5711b3bd1fbe2ea983` |

The AST and source-segment fingerprints exactly match the repaired pre-extraction function.

## Preserved repaired artifact contract

The three-row call-scope fixture still writes exactly:

| Artifact | SHA-256 |
|---|---|
| `global_trades_v7c.csv` | `184fd8c2f3076e5b4509b77bf7ae0dd5bd513615c05b08de4677c2b35e4ca5ea` |
| `global_trades_v7c_manifest.csv` | `20151c6b74a0c4e96d9bc996f15340317e2b536373d2c00c20dba739539b3ba2` |
| `v7c_global_trade_database_summary.md` | `7a792198bed8f875edbec92d34020bec8b199bca84654bcfb49f2ce2c64e3094` |

Canonical complete fingerprint:

`6b9fcf15e28a4e4249309665ac533abd087a6c57e2a336f52c93334c980c6abe`

The repaired manifest remains `status=infrastructure_validation` and `statistical_interpretation_allowed=no`. The 131-field data schema, call-scope archive rewrite, local/global ID fallback order, one-based row index, exact stdout, and empty stderr remain unchanged.

Empty-input artifact hashes and canonical fingerprint remain:

- data CSV: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`;
- manifest CSV: `71792138676b4cdb42dd621de6c631a635935e2b5a74ade131d27ad2ffb73fd8`;
- summary: `dbdf848215a5408060c79d170858a92f5697b7da8eeb594799e6ac1701bbf178`;
- canonical fingerprint: `40d6f366a69f9c7e2462890a195be0fee455446032573b075171f44544eae37a`.

The count-independence and overwrite/foreign-file-preservation contracts also remain unchanged.

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

Direct-script import and parser path:

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python tools/trade_inspector/inspect_trades.py --help

exit 0
```

`git diff --check` passed.

## Safety and next step

Only the V7C module extraction, facade import, callable-identity assertion, and this evidence document changed. IU4 ENFORCED, Live-L1, Exchange, and Live remain locked. No source data or runtime input was changed.

After integrating this extraction into `main`, the next development step is the S5P seam inventory and characterization gate for the next remaining inline Trade Inspector responsibility. It must identify the next cohesive extraction boundary before any production move.
