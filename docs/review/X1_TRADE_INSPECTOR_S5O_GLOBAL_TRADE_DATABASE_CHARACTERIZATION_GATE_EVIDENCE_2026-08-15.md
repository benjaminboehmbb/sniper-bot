# X1 Trade Inspector S5O Global Trade Database Characterization Gate Evidence — 2026-08-15

Status: **PASS — FAIL-CLOSED ROUTE BOUND; EXTRACTION NO-GO UNTIL REPAIR**

Branch: `codex/x1-trade-inspector-s5o-global-trade-database-characterization-gate-2026-08-15`

Base commit: `3bcc2b7baa9d163c1e0cd470861bad7fbe77405a`

## Scope

This gate freezes the current S5O global-trade-database route before any repair or extraction from `tools/trade_inspector/inspect_trades.py`.

Bound production surface:

- `export_global_trade_database`.

The gate uses only synthetic Trade Inspector rows and temporary output directories. It does not read repository archives or market data and does not change production code, runtime inputs, policies, strategies, or generated runtime artifacts.

## Production identity

`tools/trade_inspector/inspect_trades.py` remained byte-identical throughout the gate.

SHA-256 before and after:

`2599e94b3b225f7d3750424cc34e094c1318d08b371e3b96fce1f140a6f07136`

| Binding | AST SHA-256 | Source-segment SHA-256 |
|---|---|---|
| `export_global_trade_database` | `7144c6125802d65e4c70ad94d40c68ebbb3ebfe92bb1d946db723fad291af3e1` | `815b067a953a7a83c0e74e29a74ada1d967f64188e13e4e57849a1445f2789a3` |

Prepared characterization-test SHA-256:

`d01967f1bb03f8b19a3bcc539df811672ddc226438b4be034062a962cdf2189a`

## Current fail-closed contract

The route currently writes two owned artifacts and then raises exactly:

```text
NameError: name 'statistical_allowed' is not defined
```

The failure occurs while constructing the manifest row. Consequently:

- `global_trades_v7c.csv` exists;
- `v7c_global_trade_database_summary.md` exists;
- `global_trades_v7c_manifest.csv` does not exist;
- stdout and stderr remain empty.

The three-row call-scope fixture binds the partial artifacts:

| Partial artifact | SHA-256 |
|---|---|
| `global_trades_v7c.csv` | `184fd8c2f3076e5b4509b77bf7ae0dd5bd513615c05b08de4677c2b35e4ca5ea` |
| `v7c_global_trade_database_summary.md` | `7a792198bed8f875edbec92d34020bec8b199bca84654bcfb49f2ce2c64e3094` |

Canonical filename-to-hash fingerprint:

`3401c9ed6f636842ba2aa8b125c5c633d3d99ab9852840645851fce481b5ec5f`

The partial CSV has 131 fields. Its final four fields are `archive_id`, `local_trade_id`, `global_trade_id`, and `v7_global_row_index`. The fixture binds local IDs `A`, `K`, and `Z`, their global IDs `CALL-SCOPE::A`, `CALL-SCOPE::K`, and `CALL-SCOPE::Z`, and their one-based row indices.

## Empty, identity, boundary, and overwrite contracts

Empty input reaches the same exact `NameError`. It writes a zero-byte `global_trades_v7c.csv` with SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` and a summary with SHA-256 `dbdf848215a5408060c79d170858a92f5697b7da8eeb594799e6ac1701bbf178`. Its canonical partial-artifact fingerprint is `4947fbb95f9d147b3c9d612c086e16298a9d0a6e62c49bfad4e8ac39220e008c`.

The local-ID fallback order before failure is bound exactly:

1. `trade_id`;
2. `stable_trade_id`;
3. `local_trade_id`;
4. `id`;
5. generated `T######` from the one-based row index.

The corresponding fixture produces `TRADE`, `STABLE`, `LOCAL`, `ID`, and `T000005`.

Three boundary fixtures prove that the current failure is independent of row and source-archive counts:

| Rows | Source archives | Observed result |
|---:|---:|---|
| 29 | 2 | exact `NameError`; manifest absent |
| 30 | 1 | exact `NameError`; manifest absent |
| 30 | 2 | exact `NameError`; manifest absent |

An overwrite fixture proves that a stale owned CSV is replaced before failure, a foreign file is preserved, and neither a manifest nor stdout is produced.

## Gate decision

The characterization gate passes because the full current behavior, including the longstanding partial-write failure, is deterministic and regression-bound. The production route itself is not approved for extraction: a structure-only move would preserve a known undefined-variable defect and an incomplete artifact set.

The required next change is a dedicated S5O defect repair. It must define the manifest's `statistical_interpretation_allowed` value with explicit single-archive semantics (`no`), preserve the bound ID/schema/overwrite behavior, establish complete success artifacts, and keep all failure paths fail-closed. Only after that repair is characterized and integrated may the route be extracted.

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

Only characterization tests and this evidence document changed. IU4 ENFORCED, Live-L1, Exchange, and Live remain locked. No source data or runtime input was changed.

After integrating this gate into `main`, the next development step is the targeted S5O global-trade-database defect repair described above. The repaired route must pass focused and full regression validation before any S5O extraction begins.
