# X1 Trade Inspector S5G Leakage Audit Characterization Gate Evidence — 2026-08-14

Status: **PASS**

Branch: `codex/x1-trade-inspector-s5g-leakage-audit-characterization-gate-2026-08-14`

Base commit: `282af8b3d99645b65cc3dfb3093265162243b3b5`

## Scope

This gate freezes the current S5G leakage-audit route before any extraction from `tools/trade_inspector/inspect_trades.py`.

Bound production surface:

- `HIGH_LEAKAGE_PREFIXES`;
- `HIGH_LEAKAGE_EXACT`;
- `MEDIUM_LEAKAGE_EXACT`;
- `SAFE_ID_COLUMNS`;
- `audit_feature_leakage`;
- `export_leakage_audit_dataset`.

No production implementation, CLI dispatch, runtime input, archive, market data, label data, or generated repository artifact changed while establishing the gate.

## Production identity

`tools/trade_inspector/inspect_trades.py` remained byte-identical throughout the gate.

SHA-256 before and after:

`79128be78af0088b157078f526246b1b667e496fdbff4aa2afbf94702661f549`

| Binding | AST SHA-256 | Source-segment SHA-256 |
|---|---|---|
| `HIGH_LEAKAGE_PREFIXES` | `881ae4fdb572821de465f44f301a2d203b526b11907485febb892075748845ed` | `f071297a45fda0c51413b00b34b18620c8ec9b34d18ec0e3d574ad9523dd6065` |
| `HIGH_LEAKAGE_EXACT` | `99ca1cd7930be9754a28eac65d2925ae845b7e2ceb7bc3f44093d7055a7e09e9` | `aef872fc0aaab715425d76fd246711f83b2593d9b59dfa4a00542e0ce604fa2c` |
| `MEDIUM_LEAKAGE_EXACT` | `355ed37aa87344fa3ebb509634c0affde68c210b7bd2bce35840a01c6278c44d` | `fd9e2da847b3c5282eb0582f4435bcc288ccceba518d9a820ac8a1043d6320fb` |
| `SAFE_ID_COLUMNS` | `d9a970ea50ca63977c29257e91487d94c524402dff6f746659decd1c58567043` | `dc457bb181c58fe6820124cee63837a79a4ffb83b8d0dbc51fce89ecd74c5b48` |
| `audit_feature_leakage` | `89bf08ff9c6def1c063ed7752bfc8888596bdb2c8c479b7e559562d1a5441446` | `a5d5a5e3f450ee10d16a936e88125870bfa35a45c7a59bb28073eeaf85d7fb7e` |
| `export_leakage_audit_dataset` | `dc95d074004e11559f29d1cdd1fc1c963d4766907d19e4c6a717b5136ff218a0` | `fe3893cc36566fb53bb6e19656f9e1bccda8750bb76e47c9d3f216bf24bb10bb` |

## Leakage classification contract

The focused rule matrix binds column-order preservation and the exact decision precedence:

1. `trade_id`, `human_label`, and `ml_split` are skipped as safe identity columns;
2. `TARGET_COLUMNS` membership or a high-risk prefix yields `HIGH / target_or_future_information / blocked`;
3. exact high-risk membership yields `HIGH / post_trade_outcome_or_diagnosis / blocked`;
4. exact medium-risk membership yields `MEDIUM / exit_or_in_trade_information / blocked`;
5. every remaining feature yields `LOW / entry_or_static_feature / allowed`.

The report, allowed list, and blocked list preserve first-row model-column order. Empty model-ready input returns three empty lists.

## Complete artifact contract

The three-row fixture uses trade IDs `A`, `K`, and `Z`, preserving train, validation, and test identity through every row artifact.

| Artifact | SHA-256 |
|---|---|
| `trade_dataset_v4c_blocked_features.csv` | `b56bad304ae083fe6c2d5a6172e7bf437e637516b1c3c221adf4a4f3fe255fb6` |
| `trade_dataset_v4c_feature_catalog.csv` | `e1a9817db5033c910f3e6c89b4becdcee0f35f8f03af05ccb3e35bb8dfb07667` |
| `trade_dataset_v4c_leakage_report.csv` | `a4f52df0c9396f899732b0cc4d590e1913865452c87fc5062cf347a747c352a9` |
| `trade_dataset_v4c_manifest.csv` | `07b13029f7de0e06387cb801947c952858c3f7df776bb8f6c971cd7c6c3a39fb` |
| `trade_dataset_v4c_model_ready.csv` | `f381baf1d039ded694828552dd90f8e37796ef13d95257cfb4e697a066beaa4f` |
| `trade_dataset_v4c_targets.csv` | `5c1a03588e1039b020199cb4a7ae1aa5c7011e56dce27d9e5a37abda49aa2d04` |
| `trade_dataset_v4c_training_features.csv` | `810c439fabe9cd0afecd6931044129bad743b0bccfaf045d6d8084bc1c6b5a3b` |

Canonical filename-to-hash fingerprint:

`960027b4b0a035f309decd610c88ea2a3f43c40c67f65b09bf3c6ce722c1cb6c`

The full audit contract is exactly:

- 3 model rows and 128 audited columns;
- 86 HIGH, 10 MEDIUM, and 32 LOW features;
- 32 allowed and 96 blocked features;
- zero HIGH-risk features allowed for training;
- leakage score `268`;
- audit status `PASS`;
- 131 model-ready columns;
- 35 training-feature columns;
- 19 target columns;
- 99 blocked-feature columns.

All non-identity HIGH and MEDIUM features are excluded from training. All LOW features are included.

## Empty-input contract

Empty input creates the same seven filenames. Six artifacts are zero-byte files with SHA-256:

`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`

The empty manifest CSV SHA-256 is:

`3df387b8bcb32cade9870a54271187a90429dfd56256ad7ab499ed7fe8ef58de`

The empty filename-to-hash fingerprint is:

`56e25192ef9f9e0bf5eb8588155c4e31b37d5d1819c402edb435280a016f241a`

The empty route reports zero audited, allowed, blocked, HIGH, MEDIUM, and LOW features and retains `audit_status=PASS`.

## Filesystem and console contract

The gate binds recursive directory creation, route-owned overwrite, preservation and sorted listing of foreign CSVs, exact metric output order, exact path formatting, and empty stderr.

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

## Prepared evidence files

| File | Prepared SHA-256 |
|---|---|
| `tests/trade_inspector/test_inspect_trades_characterization.py` | `87c6c06fb6cb1519ef17221f2b499c4bec3faf8944bb63a1daa808cc3347a7ae` |
| `tools/trade_inspector/inspect_trades.py` | `79128be78af0088b157078f526246b1b667e496fdbff4aa2afbf94702661f549` |

## Safety boundary

- Production code remained byte-identical.
- No leakage rule, precedence, reason, allow/block decision, score, status, schema, column order, filename, CSV byte, overwrite behavior, stdout behavior, or stderr behavior changed.
- No archive, market data, label file, registry, runtime input, generated repository artifact, or live state was read or modified.
- IU4 ENFORCED, Live-L1, Exchange, Live, inputs, strategies, policies, and gates remain unchanged and locked.
- The foreign untracked file `scripts/build_rcc002_spec_bundle.py` was not read, modified, staged, or included.

## Outcome

S5G leakage audit is fully characterized for controlled extraction. The next controlled work is S5G characterization-gate branch integration followed by extraction of the leakage-audit closure into an acyclic module, with `audit_feature_leakage` re-exported for feature-importance, stability, and cross-archive consumers.
