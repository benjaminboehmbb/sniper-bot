# X1 Trade Inspector S5G Leakage Audit Extraction Evidence — 2026-08-14

Status: **PASS**

Branch: `codex/x1-trade-inspector-s5g-leakage-audit-extraction-2026-08-14`

Base commit: `09340733194eeaf7f6b9f3802666a1113d8746e9`

## Decision

The approved S5G leakage-audit route, its classification helper, and all four rule objects were extracted from `tools/trade_inspector/inspect_trades.py` into `tools/trade_inspector/leakage_audit.py` without changing any implementation or public name.

Extracted bindings:

- `HIGH_LEAKAGE_PREFIXES`;
- `HIGH_LEAKAGE_EXACT`;
- `MEDIUM_LEAKAGE_EXACT`;
- `SAFE_ID_COLUMNS`;
- `audit_feature_leakage`;
- `export_leakage_audit_dataset`.

`inspect_trades.py` remains the stable CLI and import facade. Package imports and direct file execution both import and re-export all six exact new-module objects.

## Downstream-binding continuity

`audit_feature_leakage` is also consumed by feature-importance, feature-stability, and cross-archive analysis paths in the facade. The extraction preserves a single authoritative callable: the facade and the new module expose the same object by identity, and all existing downstream calls resolve the imported binding without a back-import.

The four rule objects are re-exported identically rather than copied, preventing policy drift between direct module and facade consumers.

## Dependency closure

The new module depends only on:

- S5E ML-dataset construction: `build_ml_dataset_rows`;
- S5F feature preparation: `TARGET_COLUMNS` and `build_model_ready_rows`;
- S5B generic persistence: `write_csv_rows`;
- S1 compatibility primitive: `safe_text`;
- Python standard-library `Path` and `Any`.

None of these dependencies imports the leakage-audit module or the facade. The facade imports the leakage-audit module, so the dependency direction is acyclic in package and direct-script modes.

## Changed files

| File | Role | Prepared SHA-256 |
|---|---|---|
| `tools/trade_inspector/leakage_audit.py` | New exact-semantics S5G module | `9877181b5288c7554e0cba7ec8b73acf5656f64b670253891e84e081c57cee8f` |
| `tools/trade_inspector/inspect_trades.py` | Stable facade and six re-exports | `902ea02dcf07c3597d3ab670a8f0f25f539b3ed5594f29550137a3fd96e6b5f9` |
| `tests/trade_inspector/test_inspect_trades_characterization.py` | Exact six-object identity assertions | `68dfc7aadb645afe888d85e312729e654581f1a28b7b035fc02be952e8d77bb8` |

Pre-extraction facade SHA-256:

`79128be78af0088b157078f526246b1b667e496fdbff4aa2afbf94702661f549`

## Semantic identity

| Binding | AST SHA-256 | Source-segment SHA-256 |
|---|---|---|
| `HIGH_LEAKAGE_PREFIXES` | `881ae4fdb572821de465f44f301a2d203b526b11907485febb892075748845ed` | `f071297a45fda0c51413b00b34b18620c8ec9b34d18ec0e3d574ad9523dd6065` |
| `HIGH_LEAKAGE_EXACT` | `99ca1cd7930be9754a28eac65d2925ae845b7e2ceb7bc3f44093d7055a7e09e9` | `aef872fc0aaab715425d76fd246711f83b2593d9b59dfa4a00542e0ce604fa2c` |
| `MEDIUM_LEAKAGE_EXACT` | `355ed37aa87344fa3ebb509634c0affde68c210b7bd2bce35840a01c6278c44d` | `fd9e2da847b3c5282eb0582f4435bcc288ccceba518d9a820ac8a1043d6320fb` |
| `SAFE_ID_COLUMNS` | `d9a970ea50ca63977c29257e91487d94c524402dff6f746659decd1c58567043` | `dc457bb181c58fe6820124cee63837a79a4ffb83b8d0dbc51fce89ecd74c5b48` |
| `audit_feature_leakage` | `89bf08ff9c6def1c063ed7752bfc8888596bdb2c8c479b7e559562d1a5441446` | `a5d5a5e3f450ee10d16a936e88125870bfa35a45c7a59bb28073eeaf85d7fb7e` |
| `export_leakage_audit_dataset` | `dc95d074004e11559f29d1cdd1fc1c963d4766907d19e4c6a717b5136ff218a0` | `fe3893cc36566fb53bb6e19656f9e1bccda8750bb76e47c9d3f216bf24bb10bb` |

All twelve fingerprints are unchanged. Boundary verification confirms exactly the two functions and four rule objects in the new module and no duplicate local definition in the facade.

## Artifact-contract continuity

| Artifact | SHA-256 |
|---|---|
| `trade_dataset_v4c_blocked_features.csv` | `b56bad304ae083fe6c2d5a6172e7bf437e637516b1c3c221adf4a4f3fe255fb6` |
| `trade_dataset_v4c_feature_catalog.csv` | `e1a9817db5033c910f3e6c89b4becdcee0f35f8f03af05ccb3e35bb8dfb07667` |
| `trade_dataset_v4c_leakage_report.csv` | `a4f52df0c9396f899732b0cc4d590e1913865452c87fc5062cf347a747c352a9` |
| `trade_dataset_v4c_manifest.csv` | `07b13029f7de0e06387cb801947c952858c3f7df776bb8f6c971cd7c6c3a39fb` |
| `trade_dataset_v4c_model_ready.csv` | `f381baf1d039ded694828552dd90f8e37796ef13d95257cfb4e697a066beaa4f` |
| `trade_dataset_v4c_targets.csv` | `5c1a03588e1039b020199cb4a7ae1aa5c7011e56dce27d9e5a37abda49aa2d04` |
| `trade_dataset_v4c_training_features.csv` | `810c439fabe9cd0afecd6931044129bad743b0bccfaf045d6d8084bc1c6b5a3b` |
| Three-row filename-to-hash manifest | `960027b4b0a035f309decd610c88ea2a3f43c40c67f65b09bf3c6ce722c1cb6c` |
| Empty manifest CSV | `3df387b8bcb32cade9870a54271187a90429dfd56256ad7ab499ed7fe8ef58de` |
| Empty filename-to-hash manifest | `56e25192ef9f9e0bf5eb8588155c4e31b37d5d1819c402edb435280a016f241a` |
| Zero-byte empty derived CSV | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |

The 128-column audit, 86/10/32 HIGH/MEDIUM/LOW counts, 32/96 allow/block partition, zero HIGH-risk training admission, leakage score 268, PASS status, 131/35/19/99 row-artifact schemas, split identity, classification precedence, reason labels, row/column ordering, CSV bytes, overwrite behavior, foreign-file preservation, exact stdout, and empty stderr all remain unchanged.

## Focused validation

Command:

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest -v tests.trade_inspector.test_inspect_trades_characterization
```

Result:

```text
Ran 38 tests
OK
```

The focused suite asserted exact identity for all six facade bindings. The hermetic direct execution test passed, covering the non-package import path.

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

- No leakage rule, precedence, reason, allow/block decision, score, status, schema, column order, filename, CSV byte, overwrite behavior, stdout behavior, or stderr behavior changed.
- No dataset, feature-preparation, persistence, archive-intake, diagnosis, identity, aggregation, or label behavior changed.
- No CLI option, default path, dispatch order, public import name, package behavior, or direct-script behavior changed.
- No feature-importance, stability, discovery, global, cross-archive, or multi-archive route moved.
- No archive, market data, label file, registry, runtime input, generated repository artifact, or live state was read or modified.
- IU4 ENFORCED, Live-L1, Exchange, Live, inputs, strategies, policies, and gates remain unchanged and locked.
- The foreign untracked file `scripts/build_rcc002_spec_bundle.py` was not read, modified, staged, or included.

## Outcome

S5G leakage-audit extraction is complete within its approved boundary. The next controlled work is S5G extraction branch integration followed by an S5H route-specific characterization gate for feature-importance export before any feature-importance extraction.
