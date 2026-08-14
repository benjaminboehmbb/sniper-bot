# X1 Trade Inspector S5C Raw ML CSV Extraction Evidence — 2026-08-14

Status: **PASS**

Branch: `codex/x1-trade-inspector-s5c-raw-ml-csv-extraction-2026-08-14`

Base commit: `00662ea4068582e38d689316ef426226ca3d4dd6`

## Decision

The approved S5C raw ML CSV route was extracted from `tools/trade_inspector/inspect_trades.py` into `tools/trade_inspector/raw_ml_csv.py` without changing the function implementation or public name.

Extracted boundary:

- `export_ml_csv`.

`inspect_trades.py` remains the stable CLI and import façade. Package imports and direct file execution both import and re-export the exact new-module function object. The `--export-ml-csv` dispatch remains in the façade and resolves the re-exported binding.

The extracted function intentionally remains separate from generic `write_csv_rows`; its empty-input rejection, existing-file preservation in that failure case, and ordered success stdout are distinct contractual behavior.

## Changed files

| File | Role | Prepared SHA-256 |
|---|---|---|
| `tools/trade_inspector/raw_ml_csv.py` | New exact-semantics S5C module | `884b1a1acbd9fa22668e01a3509d91c135bb01d56bd3fc3cc28ca040dd93d914` |
| `tools/trade_inspector/inspect_trades.py` | Stable façade and `export_ml_csv` re-export | `2e959fb28d011b8322774e9a51362da65a9d6c9c55d4dead40a148c8f71ec8f5` |
| `tests/trade_inspector/test_inspect_trades_characterization.py` | Exact function-object re-export assertion | `b87d14053446eb4f2cf61a5f9c6f43338aa00d6e1ffe28fe8065bc29840a2976` |

Pre-extraction façade SHA-256:

`09561749fb0e34e2ae8522b4c32b891ca7b66a28655d5671ae6bb55aa357057c`

## Semantic identity

Fingerprints were recorded before extraction and re-derived from the new module after extraction:

| Binding | SHA-256 |
|---|---|
| `export_ml_csv` AST | `befc66d876824bf31193acf3595d5b995e5d3679d2ffd2a1652850bf57ddb346` |
| `export_ml_csv` source segment | `c2e8d508243e94f90f03d0dbcf78579e6027ee0c4ca6cfa68421e302e5a55a36` |

Both hashes are unchanged. Boundary verification confirms exactly one `export_ml_csv` definition in the new module and no duplicate local definition in the façade.

The new module depends only on the Python standard library: `csv`, `pathlib.Path`, and `typing.Any`. It does not depend on `csv_persistence.py`, which prevents accidental convergence of their different empty-input contracts.

## Artifact and route-contract continuity

| Contract | SHA-256 | Exact bound outcome |
|---|---|---|
| Raw 127-column ML CSV | `be6e308c2c2467a00f68a589f510e161d7414e4c815624c595c2aa8719173c29` | Complete representative S4 row export |
| Ordered 127-column header | `6a8d64f5cf94ddb6d5d53fa2c73f8cd5fd00c2191cd12849d51d02a3f9d6f85c` | First-row insertion order |
| Multi-row CSV with missing later field | `d1cf0f439a99544239b70e95fca11b48485fa190889083c92497d051eed8a57c` | Missing cell remains empty |
| Partial CSV after later extra-field failure | `64c0dea2e1c321cbbcbf78285b8704a51abbc6b0be3117c8c3208ac6082a3284` | Header and first row remain after `ValueError` |

The following route behavior remains exact:

- parent-directory creation before validation and output;
- direct overwrite at the final output path;
- first-row schema authority and CRLF CSV records;
- two ordered success stdout lines with path and full row count;
- exact `No trades to export.` exception for empty input;
- absent output remains absent after empty-input failure;
- existing output remains byte-identical after empty-input failure;
- no success stdout on empty-input or later-row schema failure;
- partial final-path artifact remains after later-row schema failure.

## Focused validation

Command:

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest -v tests.trade_inspector.test_inspect_trades_characterization
```

Result:

```text
Ran 24 tests
OK
```

The focused suite asserted exact object identity between the façade and new module. The hermetic summary CLI test executed `inspect_trades.py` directly and passed with deterministic output and empty stderr, covering the direct-script import path.

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

- No raw ML schema, field order, CSV dialect, newline, encoding, overwrite, exception, direct-write, partial-write, or stdout behavior changed.
- No generic CSV persistence or label persistence changed.
- No CLI option, default path, dispatch order, public import name, package behavior, or direct-script behavior changed.
- No high-level aggregate, ML-dataset, feature, discovery, global, cross-archive, or multi-archive exporter moved.
- No archive, market data, label file, registry, runtime input, generated artifact, or live state was read or modified.
- IU4, Live-L1, Exchange, Live, inputs, strategies, policies, and gates remain unchanged and locked.
- The foreign untracked file `scripts/build_rcc002_spec_bundle.py` was not read, modified, staged, or included.

## Outcome

S5C raw ML CSV extraction is complete within its approved boundary. The next controlled work is S5C branch integration followed by an S5D route-specific characterization gate for `export_aggregate_csvs` and its complete deterministic artifact set before any aggregate-export extraction.
