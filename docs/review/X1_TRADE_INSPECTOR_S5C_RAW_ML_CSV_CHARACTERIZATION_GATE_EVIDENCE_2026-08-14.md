# X1 Trade Inspector S5C Raw ML CSV Characterization Gate Evidence — 2026-08-14

Status: **PASS — CHARACTERIZATION ONLY**

Branch: `codex/x1-trade-inspector-s5c-raw-ml-csv-characterization-gate-2026-08-14`

Base commit: `cb7750b3ab5b0309269cba13c53b7c22b56bc481`

## Decision

The route-specific pre-extraction characterization gate for `export_ml_csv` is complete. No production function, import, CLI path, output schema, persistence behavior, or runtime input changed.

The gate extends the earlier S5 persistence coverage and binds the raw ML CSV route independently from the generic `write_csv_rows` primitive. This distinction is material: raw ML export rejects empty input, preserves an existing output file in that failure case, and emits two ordered stdout lines only after a complete successful write.

## Changed file

| File | Role | Prepared SHA-256 |
|---|---|---|
| `tests/trade_inspector/test_inspect_trades_characterization.py` | Hermetic S5C route contracts | `7ec4f4d4f4dabb832b4da6a6e73f093acf94f34051709eb748da25e2a5fb7c4c` |

Production façade SHA-256 remained unchanged:

`09561749fb0e34e2ae8522b4c32b891ca7b66a28655d5671ae6bb55aa357057c`

Extracted generic CSV module SHA-256 remained unchanged:

`b1757524f779ac070b6221d6c47fc0f13a2675d4bdb89ea747b8cd238e661f25`

## Production identity

The unchanged production function was recorded before the gate:

| Binding | SHA-256 |
|---|---|
| `export_ml_csv` AST | `befc66d876824bf31193acf3595d5b995e5d3679d2ffd2a1652850bf57ddb346` |
| `export_ml_csv` source segment | `c2e8d508243e94f90f03d0dbcf78579e6027ee0c4ca6cfa68421e302e5a55a36` |

No production extraction was performed in this gate.

## Artifact fingerprints

| Contract | SHA-256 | Exact bound outcome |
|---|---|---|
| Raw 127-column ML CSV | `be6e308c2c2467a00f68a589f510e161d7414e4c815624c595c2aa8719173c29` | Complete representative S4 row export |
| Ordered 127-column header | `6a8d64f5cf94ddb6d5d53fa2c73f8cd5fd00c2191cd12849d51d02a3f9d6f85c` | Header insertion order from the first row |
| Multi-row CSV with missing later field | `d1cf0f439a99544239b70e95fca11b48485fa190889083c92497d051eed8a57c` | `b,a` header and empty second-row `a` cell |
| Partial CSV after later extra-field failure | `64c0dea2e1c321cbbcbf78285b8704a51abbc6b0be3117c8c3208ac6082a3284` | Header and first row remain after `ValueError` |

## Success contract

The gate binds:

- parent directories are created before opening the output;
- an existing output file is overwritten directly at the final path;
- field order and allowed fields come exclusively from the first row;
- the representative S4 row retains exactly 127 ordered header fields;
- the default `csv.DictWriter` dialect emits CRLF records;
- a later missing field serializes as an empty cell;
- stdout is exactly two ordered lines after success: `ML CSV exported: <path>` and `rows: <count>`;
- the reported row count is the full input-list length.

## Failure contract

The gate binds two distinct fail-closed paths:

1. Empty input:
   - parent directories are still created;
   - exact exception text is `No trades to export.`;
   - a previously absent output remains absent;
   - a previously existing output remains byte-identical;
   - stdout remains empty.
2. A later row contains a field absent from the first-row schema:
   - the default `csv.DictWriter` `ValueError` remains unchanged;
   - the already-written header and earlier row remain at the final path;
   - no success stdout is emitted.

These contracts prohibit replacing `export_ml_csv` mechanically with `write_csv_rows` during extraction.

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
- No raw ML schema, field order, CSV dialect, newline, encoding, overwrite, exception, direct-write, partial-write, or stdout behavior changed.
- No CLI option, default path, dispatch order, package import, or direct-script behavior changed.
- No archive, market data, label file, registry, runtime input, generated artifact, or live state was read or modified.
- IU4, Live-L1, Exchange, Live, inputs, strategies, policies, and gates remain unchanged and locked.
- The foreign untracked file `scripts/build_rcc002_spec_bundle.py` was not read, modified, staged, or included.

## Outcome

S5C is eligible for a separate exact-semantics extraction after this gate is integrated into `main`. The extraction must move only `export_ml_csv`, re-export the exact function through the façade, and preserve every success and failure contract above.
