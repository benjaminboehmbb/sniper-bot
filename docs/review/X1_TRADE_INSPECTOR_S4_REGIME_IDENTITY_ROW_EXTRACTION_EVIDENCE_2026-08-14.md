# X1 Trade Inspector S4 Regime, Identity, and Row Extraction Evidence — 2026-08-14

Status: **PASS**

Branch: `codex/x1-trade-inspector-s4-regime-identity-row-extraction-2026-08-14`

Base commit: `7457dfeb29a9e31e1b1bca205f0dcc6915e04777`

## Decision

The approved S4 regime, identity, family, and row-assembly block was extracted from `tools/trade_inspector/inspect_trades.py` into `tools/trade_inspector/regime_identity_rows.py` without changing function implementations or public names.

Extracted boundary:

- `build_regime_index`;
- `extract_regime_features`;
- `compact_trade_time`;
- `chart_time`;
- `build_trade_id`;
- `build_trade_family`;
- `build_ml_row`;
- `build_rows`.

`find_matching_entry_exit` moved unchanged as the direct audit-matching dependency of `build_rows`, avoiding a circular import or duplicated matcher.

`inspect_trades.py` remains the stable command-line and import façade. Package imports and direct file execution both import and re-export the exact new-module objects.

The persistence and allocation boundary remains in the façade. `load_label_registry`, `save_label_registry`, and `assign_human_labels` are not present in the new module.

## Changed files

| File | Role | Prepared SHA-256 |
|---|---|---|
| `tools/trade_inspector/regime_identity_rows.py` | New exact-semantics S4 module | `9be383c4f406c310e89d1513d72945572efba101c37c91f0fa996f1ef7317190` |
| `tools/trade_inspector/inspect_trades.py` | Stable façade and S4 re-exports | `48a8d77dac975c0a8127c0b85eae9fff37d64583a86aaadd95dffdd8bcf5d229` |
| `tests/trade_inspector/test_inspect_trades_characterization.py` | Exact function-object re-export and registry-boundary assertions | `518e9eaf80050b3e673a6824912a2ff84a95712e78003bcaa341787746cb2239` |

Pre-extraction façade SHA-256:

`ba4e48cd487fd3a37a20dbf3b600b5a9699d744317ac38bd656338fd5817ad37`

## Semantic identity

AST hashes were recorded before extraction and re-derived from the new module after extraction:

| Binding | AST SHA-256 |
|---|---|
| `find_matching_entry_exit` | `c09b7db9007fbc4395a84b8a937f7af9e513c1b94affb170748093319ac247ff` |
| `build_regime_index` | `88ab7287fb1c43ac51d3786010a4aa41273fbd0ed578b20ec76637cbd0c98ac8` |
| `extract_regime_features` | `1a409e4746f9ec42e9f71d517f005369ee796d38e9fc39c63f27723af24f02e6` |
| `compact_trade_time` | `3299e81bdd130f450bde42d8e5d8c076866c8b41bdded6df6b4875587eacc85a` |
| `chart_time` | `0281b00523bbeb64fa455b7eef8ab8082e3fba13b0869ff1f04199ca056374dc` |
| `build_trade_id` | `631a0b68b415684ca4282addaa68aada3d4ff3d08d9aa1dc9872ac828299788e` |
| `build_trade_family` | `c25e05e25389d2658c62c75194a8a89164b9737867251e6e324c5a2f60081fe4` |
| `build_ml_row` | `eb66f09a808e7ffb79206ce5805bb5d1168087e83c099eb5aecab3fa8b5f9091` |
| `build_rows` | `1d1e74bfc2a87a1513b92b2f4858f2793e2d8971423d2cfeb30ca7ae00d14fe5` |

All nine hashes are unchanged. Boundary verification confirms exactly nine functions in the new module, 63 remaining local façade functions, no duplicate S4 definitions in the façade, and no registry functions in the new module.

## Characterization continuity

All S4 gate fingerprints remain unchanged:

| Contract | SHA-256 |
|---|---|
| Representative row semantics | `54fc961343d463d4e55d6489c70ec9ffcf3892acc9155b45b95e5f9408a2ce24` |
| Exact 127-field insertion order | `76c7ca3b7c1b1e5652bc5ece60648fb23f2eb09e32553bef63ddbb22f385e795` |
| Ordered representative row | `a79a164bbbeb5a1584e34aadc3c0c04f451445c94e9eec2e9b0e171aadadb60b` |
| Regime matrix | `d37f242b767fa32d6ffdbbee148dfd820805f07bdbf0e310090f068659db7b4a` |
| Trade-family matrix | `18a1d2ccbd54647b09077dace28af5c7795eb34c90ff64660901962e17c7acab` |
| Multi-row identity summary | `b8f5f7bd37b5be8f6a2cc3ca3eccec2b932da183f07143959bfc6133dc41fd45` |

The S1, S2, and S3 characterization contracts also remain green in the same focused test module.

## Focused validation

Command:

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest -v tests.trade_inspector.test_inspect_trades_characterization
```

Result:

```text
Ran 18 tests
OK
```

The hermetic summary CLI test executed `inspect_trades.py` directly and passed with empty stderr and deterministic output.

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

- No regime rule, UTC conversion, fallback, ID, family precedence, field value, field order, audit-selection rule, label lookup, or multi-row ordering changed.
- No CLI option, default, dispatcher order, public import name, or direct-script execution path changed.
- Label-registry loading, saving, and assignment remain in the façade and outside the new module.
- No repository archive, market data, runtime input, label registry, or generated artifact was read or modified.
- IU4, Live-L1, Exchange, Live, inputs, strategies, policies, and gates remain unchanged and locked.
- The foreign untracked file `scripts/build_rcc002_spec_bundle.py` was not read, modified, staged, or included.

## Outcome

S4 extraction is complete within its approved regime/identity/row boundary. Persistence, presentation, aggregate, export, and CLI regions remain outside this change.
