# X1 Trade Inspector S5N Cross-Archive Root Cause Characterization Gate Evidence — 2026-08-15

Status: **PASS**

Branch: `codex/x1-trade-inspector-s5n-cross-archive-root-cause-characterization-gate-2026-08-15`

Base commit: `acecbf67fda81e62313d839106fabcc767511ac1`

## Scope

This gate freezes the current S5N cross-archive root-cause route before extraction from `tools/trade_inspector/inspect_trades.py`.

Bound production surface:

- `export_cross_archive_root_cause`.

The gate uses only synthetic Trade Inspector rows and temporary output directories. It does not read repository archives or market data and does not change production code, runtime inputs, policies, strategies, or generated runtime artifacts.

## Production identity

`tools/trade_inspector/inspect_trades.py` remained byte-identical throughout the gate.

SHA-256 before and after:

`06fe664120e2aca482aa84f43135f2bc5f3310e22ad190588c20841da64e542a`

| Binding | AST SHA-256 | Source-segment SHA-256 |
|---|---|---|
| `export_cross_archive_root_cause` | `2cdfa581578d9b724d73f1ae8094329b5615472777e9ec1d6a0e88c7b648909f` | `d9a79a213df02a6c4aad04901f464770e3cb7cafa12ccf36eb44caf9b53892a9` |

Prepared characterization-test SHA-256:

`6a7bac33556ac4a34f188c8999780861acc991a4a1aa6b44bfefe239f97ecc00`

## Complete artifact contract

The three-row single-archive fixture binds all four route artifacts.

| Artifact | SHA-256 |
|---|---|
| `cross_archive_root_cause_attribution_v7d.csv` | `518580900e60497996678b15f5628f1297ab1a5c075a88df51cfe37c3fbb7c52` |
| `cross_archive_root_cause_trades_v7d.csv` | `7e04210700f3d3168b7cee62edf188c6e74746ffacdf95107262e32f91903576` |
| `cross_archive_root_cause_v7d_manifest.csv` | `85fb3edad4fba9e64d197cefceb4538084b275ad85712a5d061c8b9e211b3be0` |
| `v7d_cross_archive_root_cause_summary.md` | `ae05713244443204e994f5db4b4aeaf9504472ee858043c56259164abfc086a2` |

Canonical filename-to-hash fingerprint:

`16807c6d1bd1c8d6d8e8534cff39a55fd394543afd7b615d66361c93b47f8241`

The fixture preserves three enriched trade rows and the ordered weighted attribution `early_exit`, `entry_filter_quality`, `risk_management` with cause shares `0.95`, `0.03`, `0.02`. Local/global IDs, 30-field trade schema, call-scope archive identity, row-level attribution enrichment, manifest values, exact stdout, and empty stderr are bound.

## Identity, empty, and boundary contracts

The local-ID fallback order is bound exactly:

1. `trade_id`;
2. `stable_trade_id`;
3. `local_trade_id`;
4. `id`;
5. generated `T######` from the one-based row index.

Global IDs remain `<call-scope archive_id>::<local_trade_id>`. Missing root cause remains `unknown_cause`; missing trade index falls back to the one-based row index.

Empty input creates the same four filenames. Both data CSV files are zero-byte artifacts. The empty manifest SHA-256 is `0eecd2fcd8575ac5a572ec0db7e50cbc3e04a4c262e6d6ae33a33d00599ca2ff`; the empty summary SHA-256 is `8acbc8bfb62086e55b366d668036dbb0455b624f72ea9a65f37303255d4c5037`; and the complete empty fingerprint is `3ad06651f751952b31bad929b142c42e14dd0b3368f73dc8299f786c812b50d5`.

Three boundary fixtures prove the independent conditions:

| Rows | Source archives | Mode | Statistical interpretation |
|---:|---:|---|---|
| 29 | 2 | `multi_archive_analysis` | `no` |
| 30 | 1 | `single_archive_infrastructure_validation` | `no` |
| 30 | 2 | `multi_archive_analysis` | `yes` |

The current asymmetric enrichment is explicitly frozen: the manifest reflects the actual source-archive count, while every attribution row retains `archive_scope=single_archive_validation`, `archive_count=1`, and the call-scope `source_archive_id`.

An overwrite fixture proves replacement of stale owned output while preserving and listing a foreign file. Exact sorted directory-listing output is bound.

## Validation

Focused characterization:

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest -q tests.trade_inspector.test_inspect_trades_characterization

Ran 72 tests
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

After integrating this gate into `main`, the next development step is the structure-only S5N extraction into a dedicated cross-archive root-cause module, preserving all bound semantics and facade bindings.
