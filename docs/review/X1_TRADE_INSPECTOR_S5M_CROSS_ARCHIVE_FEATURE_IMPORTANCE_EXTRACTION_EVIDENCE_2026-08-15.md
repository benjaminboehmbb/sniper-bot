# X1 Trade Inspector S5M Cross-Archive Feature Importance Extraction Evidence — 2026-08-15

Status: **PASS**

Branch: `codex/x1-trade-inspector-s5m-cross-archive-feature-importance-extraction-2026-08-15`

Base commit: `4ebe33268e0291851ae0218f193b5ffff2f75ead`

## Scope

The S5M cross-archive feature-importance implementation was moved without semantic changes from `tools/trade_inspector/inspect_trades.py` into the dedicated module `tools/trade_inspector/cross_archive_feature_importance.py`.

Gate-bound production surface:

- `export_cross_archive_feature_importance`.

The extracted module depends only on existing downward seams:

- ML row construction from `ml_dataset.py`;
- model-ready row construction and target columns from `feature_preparation.py`;
- leakage filtering from `leakage_audit.py`;
- feature-importance computation from `feature_importance.py`;
- CSV persistence and compatibility primitives.

`tools/trade_inspector/inspect_trades.py` imports and reexports the binding in package and direct-script modes. The characterization suite binds the facade symbol by object identity to the extracted implementation. CLI dispatch, computation, artifact names and bytes, schemas, Markdown, stdout, warnings, thresholds, archive enrichment, overwrite behavior, and directory listing remain unchanged.

## Semantic identity

The moved function retains both fingerprints established by the S5M characterization gate.

| Binding | AST SHA-256 | Source-segment SHA-256 |
|---|---|---|
| `export_cross_archive_feature_importance` | `5a2de6f4df421c607ce9b0ed26355eada464bab9155fa5bed2f0b2bc19063354` | `1c093aa95d7510719c474658369887d68e9ce8c91c5353f140160e22fb63f545` |

Prepared file SHA-256 values:

| File | SHA-256 |
|---|---|
| `tools/trade_inspector/cross_archive_feature_importance.py` | `b9bb5a90b376a2df27f93517a2627eb4dc04c58708d69b242c9cc17044bdd902` |
| `tools/trade_inspector/inspect_trades.py` | `06fe664120e2aca482aa84f43135f2bc5f3310e22ad190588c20841da64e542a` |
| `tests/trade_inspector/test_inspect_trades_characterization.py` | `8e2ba5d67c42e41c5748e98e95c7f6557f6c4f3b4fedf3268309f0cebbabd027` |

## Artifact and behavioral parity

The complete three-row fixture reproduced all twelve gate artifacts exactly. Its canonical filename-to-hash fingerprint remains:

`75d33b19cb909d65137f5bd7549266360a80e3d750e26637aa9e502870da6dc3`

The empty-input fingerprint remains:

`77e16b2cb6f2036de7a9926a7b884fb65c60f0cfeaa0144231f9d6e5206cdb8e`

The following contracts remain bound and passing:

- combined and nine target-specific CSV exports;
- manifest and Markdown-summary bytes;
- 297 rows from 33 allowed features across nine targets;
- global descending importance ordering and exact target membership;
- exact ordered stdout and empty stderr;
- overwrite behavior, foreign-file preservation, and sorted directory listing;
- 29 rows with two archives: `WARN`, statistical interpretation `no`;
- 30 rows with one archive: `PASS`, statistical interpretation `no`;
- 30 rows with two archives: `PASS`, statistical interpretation `yes`;
- manifest source-archive count and analysis mode;
- existing result-row enrichment with `archive_scope=single_archive_validation`, `archive_count=1`, and the call-scope source archive ID.

No gate was weakened and no input was rewritten.

## Validation

Focused characterization:

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest -q tests.trade_inspector.test_inspect_trades_characterization

Ran 67 tests
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

After integrating this extraction branch into `main`, the next development step is the S5N cross-archive root-cause characterization gate for `export_cross_archive_root_cause`, before any corresponding extraction.
