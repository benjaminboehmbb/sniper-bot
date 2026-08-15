# X1 Trade Inspector S5T Facade Consumer and Namespace Policy Audit — 2026-08-15

Status: **PASS**

Branch: `codex/x1-trade-inspector-s5t-facade-consumer-namespace-audit-2026-08-15`

Base commit: `af371b77fb044436ce6dffc0ad3f7f568826b99f`

## Scope

This audit determines how the repository consumes the 104-name `tools.trade_inspector.inspect_trades` facade frozen by S5S and defines the safe namespace policy for the next step.

The audit covers all 785 tracked Python files, direct facade-module imports, direct name imports, wildcard imports, facade attribute access, executable script references, and documentation references.

The foreign untracked file `scripts/build_rcc002_spec_bundle.py` was explicitly excluded and was not read, changed, staged, or committed.

## Reproducible scan basis

Tracked Python file-list count:

`785`

Tracked Python file-list SHA-256:

`cdb304876eff2da5afabdd29f056a9ab6d40ee225195c2f4fac0f659cce19ae9`

Every tracked Python file was parsed with `ast`. Facade import aliases, direct imports, wildcard imports, and attribute accesses were resolved structurally rather than by text matching.

## Consumer findings

| Consumer class | Result |
|---|---:|
| production Python consumers | 0 |
| test Python consumers | 1 |
| direct facade-name imports | 0 |
| wildcard facade imports | 0 |
| facade module aliases | 1 (`inspector`) |

The sole Python consumer is:

`tests/trade_inspector/test_inspect_trades_characterization.py`

Outside the two S5S self-characterization methods, that suite accesses 75 facade names.

Used-name count and SHA-256:

`75 / 47337a29c29cb28b2379c8350b85e444bb080e81fe5aa9343024c69a87a454e3`

Unused-name count and SHA-256:

`29 / 4b9b4f9724dde3487f629033b59f905ea182ea23d5669963ce5a5b1c7bdb8103`

The 29 repository-internally unused names are:

- `Any`;
- `HIGH_LEAKAGE_EXACT`;
- `HIGH_LEAKAGE_PREFIXES`;
- `MEDIUM_LEAKAGE_EXACT`;
- `NON_FEATURE_COLUMNS`;
- `Path`;
- `SAFE_ID_COLUMNS`;
- `add_ml_targets`;
- `aggregate_group_rows`;
- `aggregate_top_improvement_rows`;
- `annotations`;
- `argparse`;
- `avg`;
- `build_category_maps`;
- `build_ml_dataset_rows`;
- `build_ml_row`;
- `compute_root_cause_attribution`;
- `evaluate_split_quality`;
- `export_root_cause_attribution_csv`;
- `group_stats`;
- `market_price`;
- `market_timestamp`;
- `parse_cause_weights`;
- `parse_key_value_log`;
- `print_kv`;
- `print_root_cause_attribution`;
- `print_split_quality`;
- `print_top_improvement_candidates`;
- `print_trade_family_summary`.

Repository-internal non-use is not treated as proof that external consumers do not exist. Therefore it does not authorize deleting any compatibility re-export.

## Script and documentation findings

The executable path `tools/trade_inspector/inspect_trades.py` appears in 62 tracked files. Twelve tracked files contain the canonical `python3 tools/trade_inspector/inspect_trades.py` command form.

These are command/documentation consumers of the stable script path, not Python namespace consumers. They reinforce the requirement to retain the facade file and its `__main__` boundary.

## Namespace policy decision

The safe policy is:

1. retain all 100 domain/default re-exports as directly accessible facade attributes;
2. retain the `inspect_trades.py` executable path and direct-script import branch;
3. do not remove the four support-name attributes (`Any`, `Path`, `annotations`, `argparse`) in the next step;
4. define an explicit `__all__` containing exactly the 100 domain/default names and excluding only those four support names;
5. bind package and direct-script wildcard behavior before considering any later attribute deletion;
6. require a separate compatibility decision before removing any direct attribute, including repository-internally unused names.

Because the audit found zero wildcard consumers, introducing the explicit 100-name `__all__` does not change any tracked repository consumer. Direct attribute access remains unchanged.

## Production identity and validation

Production facade SHA-256 remained:

`5f0773af9ce542f68b4156683f7c7d27c61b72f431e5f2bc52821d8fa01a2339`

Characterization-test SHA-256 remained:

`3e93fe1bcfc66db13eb1ae0988016f346ce5c2d8e6fa07553f10f2268ab8a8ea`

Focused characterization:

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest -q tests.trade_inspector.test_inspect_trades_characterization

Ran 91 tests
OK
```

Full regression:

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -s tests/regression -p 'test_*.py'

Ran 170 tests
OK
```

## Safety and next step

Only this audit evidence document changed. IU4 ENFORCED, Live-L1, Exchange, and Live remain locked. No source data or runtime input was changed.

After integrating this audit into `main`, the next development step is S5U: add and characterize an explicit 100-name `__all__` to the facade. Package and direct-script wildcard exports must match exactly, the four support names must remain directly accessible but be absent from wildcard export, and all existing tests and script behavior must remain green.
