# X1 Trade Inspector S5K Multi-Archive Loader Extraction Evidence — 2026-08-14

Status: **PASS**

Branch: `codex/x1-trade-inspector-s5k-multi-archive-loader-extraction-2026-08-14`

Base commit: `9b9a2ed4767733106ba5075eb5cf62ab302fc39b`

## Scope

The S5K multi-archive-loader implementation was moved without semantic changes from `tools/trade_inspector/inspect_trades.py` into the dedicated module `tools/trade_inspector/multi_archive_loader.py`.

Gate-bound production surface:

- `load_archive_registry_md`;
- `load_rows_for_archive`;
- `export_multi_archive_loader`.

To keep the extracted module independently importable and avoid a cyclic dependency on the facade, its five existing source-reader dependencies were co-located unchanged:

- `read_jsonl`;
- `market_timestamp`;
- `market_price`;
- `parse_market_rows`;
- `parse_key_value_log`.

`tools/trade_inspector/inspect_trades.py` imports and reexports all eight bindings in package and direct-script modes. Characterization tests bind the facade symbols by object identity to the extracted implementations. No CLI dispatch, runtime input, archive, market data, generated repository artifact, IU4 mode, exchange, or live path changed.

## Semantic identity

Every moved function retains both its pre-extraction AST fingerprint and exact source-segment fingerprint.

| Binding | AST SHA-256 | Source-segment SHA-256 |
|---|---|---|
| `read_jsonl` | `1d9fdad4bcb1fffaf2936a54c3003a40e03d874fb2117bdc2a3527c70aaae114` | `b587168ea339dde05909274911e5f9ab469557a52e9a1022e4f79c9de4ca8707` |
| `market_timestamp` | `0cd3583053206c124ba6566b03172cec0be536051c35483178ae13a78394f912` | `7e03309c7ff580af9a98929388b6d002c35013fab7c02f3467eff2bd811affe7` |
| `market_price` | `2637440a0447adcde424fb9dd29ee72c9c39c2cf2e14e249e4c867fafb4e8611` | `6f934cf54d07b98288b93f95ba5dd749450b813271dfc50afe9ad5aacd4531a0` |
| `parse_market_rows` | `52764fe7faec4973f811271758718785cdb373025a21128797c9183aa0059d3a` | `0999807699cc6d79452dd22c6ed76857977f9304af5217bb41b1816af97c3a74` |
| `parse_key_value_log` | `095e1d8eea86d8a17742f1aff3385b05e5cb85d348c98e8020a7ded9c309528b` | `3c912576ecdcbbc5c70d2ac75ac513316827914233fb6d9a254e9120445daa28` |
| `load_archive_registry_md` | `2837857e2fdb650642873476e408f877a9663ea0a8279d5d245fa6e4ec692867` | `49f3ea713db6d028acd87a75f1411c9278a7d0e731cc48ac6a56ddf51b73900b` |
| `load_rows_for_archive` | `54f0d3cc256d5ab55df629ea9da49bdb6d5547675c7434cdf4f891af2769c73a` | `530a6507bbe5a7cf92ce236fcbd306f3e46a9d5768fbb9a809fd6d4722f05cde` |
| `export_multi_archive_loader` | `0d9009cf5378224ef9026849ce93850507699fd8652ca13d7ac496845e1979c2` | `9c229e4b59fa5c7a7e2869ebe232356a7d7bde7713dda72ce2c3287772e23b02` |

Prepared file SHA-256 values:

| File | SHA-256 |
|---|---|
| `tools/trade_inspector/multi_archive_loader.py` | `d96d669c14c58cc7753597c51416d6834cd65c9511b7144589648e8f38af88bd` |
| `tools/trade_inspector/inspect_trades.py` | `23e980aaf8749103fbeb2abd1527585fda354e1428cd469eb0a6b8e5130d92c4` |
| `tests/trade_inspector/test_inspect_trades_characterization.py` | `60682aa313110d9a1c9a81aa560814e8a67b2d155e9c5ae66f80738ca0a86494` |

## Artifact and behavioral parity

The two-archive fixture reproduced all five normalized gate artifacts exactly:

| Artifact | Normalized SHA-256 |
|---|---|
| `multi_archive_global_trades_v7g.csv` | `b9b5554bfbaff03fb0aa1d567f5efde36a434b21cd403adb960e13e27c24c26d` |
| `multi_archive_loader_errors_v7g.csv` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `multi_archive_loader_v7g_manifest.csv` | `c157dce37442446962a1fcb8eb9a023171a687117bbb3e055f2be6c4a73540fc` |
| `multi_archive_registry_loaded_v7g.csv` | `4cac5cc63358aa015dc1b348fad1eb5abe3e2091ca84fdcf234cdf10d122003e` |
| `v7g_multi_archive_loader_summary.md` | `d598dab0e7f9a907fad2ea853d632b2a9cc08043eae834da5becb0d5e7940194` |

Canonical normalized filename-to-hash fingerprint:

`91f811a59f9687770d03269879d161572c4e29af77c069b37eed3601bc697966`

The ordered enriched-row fingerprint remains `ed2db28c9d63e831e391cd042b7a4b246c4653837896fec8ce1b9995f0989eb3`.

All four homogeneous error-row fingerprints remain unchanged:

- `missing_archive_id`: `e93b3cfef1c0a494ac7a148d3e42d4a99cbdb6a1a1b90b8a64b7738ed01771e1`;
- `archive_path_missing`: `dd5014d19224ade97289dd010fdadcc52d2406186c8fab428ece8ae0dde2fafc`;
- `required_input_missing`: `696b967ea5fb8e98bd4e3f964562485c73a3307df82917e8aa16391acb64adfc`;
- caught `ValueError`: `034e77f01c2c16b18bc48b4d3dacddba40ece26116e4a722c8d6fba39666b020`.

Registry inclusion and order, 132-field enrichment, exact stdout and empty stderr, foreign-file preservation and listing, the documented heterogeneous-error partial write, and the 29/30-trade statistical boundary all remain unchanged.

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

The hermetic direct-script CLI test passed, proving the direct import mode remains operational. `git diff --check` passed.

## Safety and next gate

This is a structure-only extraction. IU4 ENFORCED, Live-L1, exchange, and live execution remain locked. No source data or runtime input was changed.

After integrating this extraction branch into `main`, the next development step is the S5L cross-archive signal-discovery characterization gate for `export_cross_archive_signal_discovery`, before any corresponding extraction.
