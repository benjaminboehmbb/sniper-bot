# X1 Trade Inspector S5 Persistence Characterization Gate Evidence — 2026-08-14

Status: **PASS**

Branch: `codex/x1-trade-inspector-s5-persistence-characterization-gate-2026-08-14`

Base commit: `a289b51b95fb9a3bfe8d51eb62e5269e450a31a4`

## Decision

The S5 pre-extraction persistence characterization gate is complete. No production function, import, CLI path, output schema, or persistence behavior was changed.

The gate binds exact behavior for:

- human-label list normalization, ordering, validation precedence, exceptions, and empty input;
- missing, malformed, duplicate-key, mixed-case, saved, and empty label registries;
- deterministic configured and fallback label assignment, including current fallback numbering;
- generic CSV parent creation, overwrite behavior, empty-file behavior, first-row field order, missing later fields, and partial output after a later extra-field failure;
- raw ML CSV overwrite, exact 127-column header order, complete artifact bytes, stdout, and empty-input failure state.

All fixtures use only synthetic rows and temporary directories.

This gate makes separately approved label-persistence, CSV-persistence, and raw-ML-export extractions technically eligible. It does not authorize those production extractions by itself.

## Changed file

| File | Role | SHA-256 before commit |
|---|---|---|
| `tests/trade_inspector/test_inspect_trades_characterization.py` | S5 label, registry, CSV, and raw-ML byte contracts | `31e4bdf414744b6750115e77f39fc5dd4f7f1bf98388359e63363e0d8afd09d8` |

Production façade SHA-256 remained unchanged:

`48a8d77dac975c0a8127c0b85eae9fff37d64583a86aaadd95dffdd8bcf5d229`

## Artifact fingerprints

| Contract | SHA-256 | Exact bound outcome |
|---|---|---|
| Non-empty saved registry | `eb96ee7fca17655042c102a3162d5d8cdbfaf1bda4ac17789ff00be245b159d6` | Fixed header, CRLF, sorted `T1`/`T2` rows |
| Empty saved registry | `451b629a29c79d2735940170b9a228bba8e67f66a373881534267240a5b21475` | Header-only registry |
| Deterministic label assignment | `e4f22c64c51f3a8405edf7252de58d057b7f759c208fe25eb7b10767954f6ec6` | Existing `beta` plus `auto_label_000002` and `auto_label_000005` |
| Generic CSV with missing later field | `d1cf0f439a99544239b70e95fca11b48485fa190889083c92497d051eed8a57c` | `b,a` header and empty second-row `a` cell |
| Partial CSV after extra-field failure | `64c0dea2e1c321cbbcbf78285b8704a51abbc6b0be3117c8c3208ac6082a3284` | Header and first row remain after `ValueError` |
| Raw 127-column ML CSV | `be6e308c2c2467a00f68a589f510e161d7414e4c815624c595c2aa8719173c29` | Complete representative S4 row export |

The zero-row generic CSV remains the standard zero-byte SHA-256:

`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`

## Human-label contract

The gate binds:

- comments and blank lines ignored;
- accepted labels lowercased in source order;
- missing file as `FileNotFoundError`;
- non-ASCII rejection before other validation;
- length validation before space validation (`two words` is reported as too long);
- a shorter spaced label reaches the space-specific error;
- case-normalized duplicate rejection;
- all-comment/all-blank input rejection.

## Registry and assignment contract

- Missing registry returns an empty mapping.
- Rows without both trade ID and label are ignored.
- Labels are lowercased on load.
- A later duplicate trade ID replaces its earlier label.
- Save creates parent directories, always writes `trade_id,human_label`, uses CRLF, and sorts by trade ID.
- Duplicate assigned label values fail before new assignment.
- Trade IDs are considered in sorted order.
- Current fallback numbering is bound exactly and is not normalized during extraction.

## CSV persistence contract

- `write_csv_rows([], path)` creates parents and a zero-byte final file.
- Existing files are overwritten.
- Field order comes from the first row only.
- Missing later fields serialize as empty cells.
- An extra later field raises `ValueError` under the default `csv.DictWriter` behavior.
- The already-written header and earlier row remain in the final file after that failure.

No atomicity or schema-normalization change is included in this gate.

## Raw ML CSV contract

- The exported representative row retains exactly 127 header fields.
- Exact bytes are fingerprinted.
- Successful stdout remains two ordered lines: artifact path and row count.
- Empty input creates the parent directory, raises `ValueError`, produces no stdout, and leaves the output file absent.

This distinct empty-input behavior prevents mechanically replacing the route with `write_csv_rows` during extraction.

## Focused validation

Command:

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest -v tests.trade_inspector.test_inspect_trades_characterization
```

Result:

```text
Ran 22 tests
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

## Safety boundary

- `tools/trade_inspector/inspect_trades.py` was not changed.
- No production import, function, default, CLI option, dispatch order, schema, newline, stdout, or failure behavior changed.
- No repository label registry, archive, market data, runtime input, or output directory was read or modified.
- Every created artifact lived under a temporary test directory.
- Existing S1–S4 fingerprints remain unchanged.
- IU4, Live-L1, Exchange, Live, inputs, strategies, policies, and gates remain unchanged and locked.
- The foreign untracked file `scripts/build_rcc002_spec_bundle.py` was not read, modified, staged, or included.

## Outcome

The small S5 persistence seams now have byte-level contracts. The next controlled implementation is S5A label-persistence extraction, followed by S5B generic CSV-persistence extraction and then S5C raw-ML-export extraction, each in a separate commit and each preserving the stable façade.
