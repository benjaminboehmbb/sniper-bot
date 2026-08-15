# X1 Trade Inspector S5L Cross-Archive Signal Discovery Extraction Evidence — 2026-08-15

Status: **PASS**

Branch: `codex/x1-trade-inspector-s5l-cross-archive-signal-discovery-extraction-2026-08-15`

Base commit: `f54e89e61fc346fbcd641a15ddc4a03ce44fec30`

## Scope

The S5L cross-archive signal-discovery implementation was moved without semantic changes from `tools/trade_inspector/inspect_trades.py` into the dedicated module `tools/trade_inspector/cross_archive_signal_discovery.py`.

Gate-bound production surface:

- `export_cross_archive_signal_discovery`.

The extracted module depends only on the existing downward seams:

- `discover_signal_groups` and `discover_pair_groups` from `feature_discovery.py`;
- `write_csv_rows` from `csv_persistence.py`;
- `safe_float` and `safe_text` from `inspection_primitives.py`.

`tools/trade_inspector/inspect_trades.py` imports and reexports the binding in package and direct-script modes. The characterization suite binds the facade symbol by object identity to the extracted implementation. CLI parsing and dispatch, inputs, filenames, field order, Markdown, stdout, overwrite behavior, directory listing, statistical thresholds, and the current per-row archive-enrichment semantics remain unchanged.

## Semantic identity

The moved function retains both fingerprints established by the S5L characterization gate.

| Binding | AST SHA-256 | Source-segment SHA-256 |
|---|---|---|
| `export_cross_archive_signal_discovery` | `fe7c3efd1e2931eed29def91e1178b6e6db9cb335c99354a01531244a827c086` | `a1a193b1dd6f7d065d1dec9ba0afb530a921f6820c06372ff35e849af4d3083a` |

Prepared file SHA-256 values:

| File | SHA-256 |
|---|---|
| `tools/trade_inspector/cross_archive_signal_discovery.py` | `9c71603aa524975e68a5faa9bae23d230d87bc49ceea25eb558bdd53f49a4988` |
| `tools/trade_inspector/inspect_trades.py` | `e7e55f04fc178646b22dfec07691825b2e21198a98474cd7a9743d02c3c17c05` |
| `tests/trade_inspector/test_inspect_trades_characterization.py` | `2688f509672a82ec964f1d34a5264396fb39623848914a9f529a1a72852e35b1` |

## Artifact and behavioral parity

The complete three-row fixture reproduced all 20 gate artifacts exactly. Its canonical filename-to-hash fingerprint remains:

`e07b71e49bed90ac7618a15bb89b16eb5c09136637116cd545b21a72395811e2`

The empty-input fingerprint remains:

`43acf4c3008bf448036431de39f5ed16ffe9f8709c326a60a1e43ff7de19ab07`

The following contracts remain bound and passing:

- ten single-key and six pair-key exports;
- all/top rollups and the exact top-50 boundary;
- manifest and Markdown-summary bytes;
- exact ordered stdout and empty stderr;
- overwrite behavior, foreign-file preservation, and sorted directory listing;
- 29 rows with two archives: `WARN`, statistical interpretation `no`;
- 30 rows with one archive: `PASS`, statistical interpretation `no`;
- 30 rows with two archives: `PASS`, statistical interpretation `yes`;
- source archive count and mode in the manifest;
- existing row enrichment with `archive_scope=single_archive_validation`, row `archive_count=1`, and the call-scope source archive ID.

No gate was weakened and no input was rewritten.

## Validation

Focused characterization:

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest -q tests.trade_inspector.test_inspect_trades_characterization

Ran 63 tests
OK
```

Full regression:

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -s tests/regression -p 'test_*.py'

Ran 170 tests
OK
```

The focused suite includes the hermetic direct-script CLI contract. `git diff --check` passed.

## Safety and next gate

This is a structure-only extraction. IU4 ENFORCED, Live-L1, Exchange, and Live remain locked. No source data, runtime input, archive, market dataset, policy, strategy, or generated runtime artifact was changed.

After integrating this extraction branch into `main`, the next development step is the S5M cross-archive feature-importance characterization gate for `export_cross_archive_feature_importance`, before any corresponding extraction.
