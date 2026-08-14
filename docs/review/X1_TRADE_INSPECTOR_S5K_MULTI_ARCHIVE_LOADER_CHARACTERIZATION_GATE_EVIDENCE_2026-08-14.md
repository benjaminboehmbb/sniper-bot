# X1 Trade Inspector S5K Multi-Archive Loader Characterization Gate Evidence — 2026-08-14

Status: **PASS**

Branch: `codex/x1-trade-inspector-s5k-multi-archive-loader-characterization-gate-2026-08-14`

Base commit: `58c8d3109029ec4f7f1af89c44fc78c2094b6dc7`

## Scope

This gate freezes the current S5K multi-archive-loader route before extraction from `tools/trade_inspector/inspect_trades.py`.

Bound production surface:

- `load_archive_registry_md`;
- `load_rows_for_archive`;
- `export_multi_archive_loader`.

No production implementation, CLI dispatch, runtime input, archive, market data, generated repository artifact, IU4 mode, exchange, or live path changed while establishing the gate.

## Production identity

`tools/trade_inspector/inspect_trades.py` remained byte-identical throughout the gate.

SHA-256 before and after:

`1f232a5d0b27fbe54be2acd45909079664e0bb7d43dfb4d5d77c0515318d9154`

| Binding | AST SHA-256 | Source-segment SHA-256 |
|---|---|---|
| `load_archive_registry_md` | `2837857e2fdb650642873476e408f877a9663ea0a8279d5d245fa6e4ec692867` | `49f3ea713db6d028acd87a75f1411c9278a7d0e731cc48ac6a56ddf51b73900b` |
| `load_rows_for_archive` | `54f0d3cc256d5ab55df629ea9da49bdb6d5547675c7434cdf4f891af2769c73a` | `530a6507bbe5a7cf92ce236fcbd306f3e46a9d5768fbb9a809fd6d4722f05cde` |
| `export_multi_archive_loader` | `0d9009cf5378224ef9026849ce93850507699fd8652ca13d7ac496845e1979c2` | `9c229e4b59fa5c7a7e2869ebe232356a7d7bde7713dda72ce2c3287772e23b02` |

Prepared characterization-test SHA-256:

`1d90ed5ed2e776b57665234ad5cb92975ad7f25f9d91348795410cc91b01c17b`

## Registry contract

The gate binds:

- the exact missing-file, missing-table, and no-included-archives `SystemExit` messages;
- Markdown table discovery from pipe-delimited lines;
- first table row as header and third and later rows as data;
- malformed-width data rows being skipped;
- case-insensitive inclusion aliases `yes`, `1`, `true`, and `y`;
- exclusion of other values;
- preservation of registry order, header order, and cell strings.

## Per-archive enrichment contract

A complete synthetic archive produces one 132-field row. The original 127 fields retain their order and the following fields are appended in order:

1. `archive_id`;
2. `archive_path`;
3. `local_trade_id`;
4. `global_trade_id`;
5. `v7g_archive_row_index`.

The archive-row index is one-based. The local-ID precedence remains `trade_id`, `stable_trade_id`, `local_trade_id`, `id`, then generated `T%06d`; the global ID remains `<archive_id>::<local_trade_id>`.

The normalized ordered enriched-row SHA-256 is:

`ed2db28c9d63e831e391cd042b7a4b246c4653837896fec8ce1b9995f0989eb3`

## Complete artifact contract

The two-archive fixture deliberately registers archive `B` before archive `A`. Both global rows and registry-summary rows retain that order. With two total trades, statistical interpretation remains disallowed.

Paths below are normalized by replacing the temporary fixture root with `<ROOT>` before hashing.

| Artifact | Normalized SHA-256 |
|---|---|
| `multi_archive_global_trades_v7g.csv` | `b9b5554bfbaff03fb0aa1d567f5efde36a434b21cd403adb960e13e27c24c26d` |
| `multi_archive_loader_errors_v7g.csv` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `multi_archive_loader_v7g_manifest.csv` | `c157dce37442446962a1fcb8eb9a023171a687117bbb3e055f2be6c4a73540fc` |
| `multi_archive_registry_loaded_v7g.csv` | `4cac5cc63358aa015dc1b348fad1eb5abe3e2091ca84fdcf234cdf10d122003e` |
| `v7g_multi_archive_loader_summary.md` | `d598dab0e7f9a907fad2ea853d632b2a9cc08043eae834da5becb0d5e7940194` |

Canonical normalized filename-to-hash fingerprint:

`91f811a59f9687770d03269879d161572c4e29af77c069b37eed3601bc697966`

The gate also binds recursive output-directory creation, exact stdout metric and sorted-directory-listing order, preservation and listing of a foreign file, empty stderr, zero-byte empty error CSV, and exact manifest and Markdown contents.

## Error continuation and partial-write contracts

Each homogeneous one-error fixture completes infrastructure export and records exactly one error. Normalized canonical error-row fingerprints are:

| Error | SHA-256 |
|---|---|
| `missing_archive_id` | `e93b3cfef1c0a494ac7a148d3e42d4a99cbdb6a1a1b90b8a64b7738ed01771e1` |
| `archive_path_missing` | `dd5014d19224ade97289dd010fdadcc52d2406186c8fab428ece8ae0dde2fafc` |
| `required_input_missing` | `696b967ea5fb8e98bd4e3f964562485c73a3307df82917e8aa16391acb64adfc` |
| caught `ValueError` | `034e77f01c2c16b18bc48b4d3dacddba40ece26116e4a722c8d6fba39666b020` |

The route's current heterogeneous-error behavior is also frozen: because `write_csv_rows` derives columns from the first row, a later error row with extra fields raises `ValueError`. At that point the global-trades and loaded-registry empty files exist, the errors CSV contains its header and first error, and neither the manifest nor Markdown summary exists. This gate documents current behavior only; it does not authorize weakening or silently fixing it during extraction.

## Statistical boundary contract

Statistical interpretation is allowed only when both conditions hold:

- at least 2 successfully loaded archives;
- at least 30 total trades.

The gate proves the exact transition using two archives: 29 trades produces `no`, while 30 trades produces `yes`, in both the CSV manifest and Markdown summary.

## Validation

Focused characterization:

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest -v tests.trade_inspector.test_inspect_trades_characterization

Ran 59 tests
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

Only characterization tests and this evidence document changed. IU4 ENFORCED, Live-L1, exchange, and live execution remain locked. No source data or runtime input was changed.

After integrating this gate into `main`, the next development step is the structure-only S5K extraction into a dedicated multi-archive-loader module, preserving all bound semantics and facade bindings.
