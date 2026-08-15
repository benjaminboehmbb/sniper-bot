# X1 Trade Inspector S5N Cross-Archive Root Cause Extraction Evidence — 2026-08-15

Status: **PASS**

Branch: `codex/x1-trade-inspector-s5n-cross-archive-root-cause-extraction-2026-08-15`

Base commit: `444eb8051c00ceb963ae05614797f1014cd61965`

## Scope

The S5N cross-archive root-cause implementation was moved without semantic changes from `tools/trade_inspector/inspect_trades.py` into the dedicated module `tools/trade_inspector/cross_archive_root_cause.py`.

Gate-bound production surface:

- `export_cross_archive_root_cause`.

The extracted module depends only on existing downward seams:

- weighted root-cause attribution from `aggregate_csv.py`;
- CSV persistence from `csv_persistence.py`;
- compatibility conversions from `inspection_primitives.py`.

`tools/trade_inspector/inspect_trades.py` imports and reexports the binding in package and direct-script modes. The characterization suite binds the facade symbol by object identity to the extracted implementation. CLI dispatch, ID precedence, enrichment, attribution, artifact bytes, Markdown, stdout, thresholds, overwrite behavior, and directory listing remain unchanged.

## Semantic identity

The moved function retains both fingerprints established by the S5N characterization gate.

| Binding | AST SHA-256 | Source-segment SHA-256 |
|---|---|---|
| `export_cross_archive_root_cause` | `2cdfa581578d9b724d73f1ae8094329b5615472777e9ec1d6a0e88c7b648909f` | `d9a79a213df02a6c4aad04901f464770e3cb7cafa12ccf36eb44caf9b53892a9` |

Prepared file SHA-256 values:

| File | SHA-256 |
|---|---|
| `tools/trade_inspector/cross_archive_root_cause.py` | `73d283e4f8cca8aabfe4a43bf640d7517e4484cc3cd99ce1d0a7faad9913e4d6` |
| `tools/trade_inspector/inspect_trades.py` | `2599e94b3b225f7d3750424cc34e094c1318d08b371e3b96fce1f140a6f07136` |
| `tests/trade_inspector/test_inspect_trades_characterization.py` | `ea6f6f576d9be3a27697f822fa84ded6d55bff875f2fe50443d88a7ba3a3097a` |

## Artifact and behavioral parity

The complete three-row fixture reproduced all four gate artifacts exactly. Its canonical filename-to-hash fingerprint remains:

`16807c6d1bd1c8d6d8e8534cff39a55fd394543afd7b615d66361c93b47f8241`

The empty-input fingerprint remains:

`3ad06651f751952b31bad929b142c42e14dd0b3368f73dc8299f786c812b50d5`

The following contracts remain bound and passing:

- enriched trade, weighted attribution, manifest, and Markdown artifacts;
- ordered causes `early_exit`, `entry_filter_quality`, `risk_management` and their exact weighted values;
- local-ID precedence `trade_id`, `stable_trade_id`, `local_trade_id`, `id`, generated `T######`;
- global-ID construction and `unknown_cause` fallback;
- exact ordered stdout and empty stderr;
- overwrite behavior, foreign-file preservation, and sorted directory listing;
- 29 rows with two archives: statistical interpretation `no`;
- 30 rows with one archive: statistical interpretation `no`;
- 30 rows with two archives: statistical interpretation `yes`;
- manifest source-archive count and analysis mode;
- existing attribution enrichment with `archive_scope=single_archive_validation`, `archive_count=1`, and the call-scope source archive ID.

No gate was weakened and no input was rewritten.

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

The focused suite includes the hermetic direct-script CLI contract. `git diff --check` passed.

## Safety and next gate

This is a structure-only extraction. IU4 ENFORCED, Live-L1, Exchange, and Live remain locked. No source data, runtime input, archive, market dataset, policy, strategy, or generated runtime artifact was changed.

After integrating this extraction branch into `main`, the next development step is the S5O global trade-database characterization gate for `export_global_trade_database`, before any corresponding extraction.
