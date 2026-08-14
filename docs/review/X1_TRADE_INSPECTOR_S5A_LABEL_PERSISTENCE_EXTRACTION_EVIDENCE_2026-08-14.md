# X1 Trade Inspector S5A Label Persistence Extraction Evidence — 2026-08-14

Status: **PASS**

Branch: `codex/x1-trade-inspector-s5a-label-persistence-extraction-2026-08-14`

Base commit: `587dc873db1c1abd4008f9b824c01a42081c8b48`

## Decision

The approved S5A human-label and label-registry block was extracted from `tools/trade_inspector/inspect_trades.py` into `tools/trade_inspector/label_registry.py` without changing function implementations or public names.

Extracted boundary:

- `load_human_labels`;
- `load_label_registry`;
- `save_label_registry`;
- `assign_human_labels`.

`inspect_trades.py` remains the stable CLI and import façade. Package imports and direct file execution both import and re-export the exact new-module objects.

`DEFAULT_LABEL_LIST`, `DEFAULT_LABEL_REGISTRY`, the `--label-list`, `--label-registry`, and `--update-label-registry` options, and all dispatch logic remain in the façade.

## Changed files

| File | Role | Prepared SHA-256 |
|---|---|---|
| `tools/trade_inspector/label_registry.py` | New exact-semantics S5A module | `d90cb74b19cf9857d73aa5e0f95a6bbeb475ec7d53e8590380aa282c00e18048` |
| `tools/trade_inspector/inspect_trades.py` | Stable façade and S5A re-exports | `4386ba6db2966c51db46e28d76596af499d396cfe4b006667499817cfce01c9f` |
| `tests/trade_inspector/test_inspect_trades_characterization.py` | Exact four-function object re-export assertions | `cd51ad9248b3cae8c98ba14053a06c12ab3c7e43b744188e70873674ad410741` |

Pre-extraction façade SHA-256:

`48a8d77dac975c0a8127c0b85eae9fff37d64583a86aaadd95dffdd8bcf5d229`

## Semantic identity

AST hashes were recorded before extraction and re-derived from the new module after extraction:

| Binding | AST SHA-256 |
|---|---|
| `load_human_labels` | `d9d99a916ef61f2d95d293a409cb7a6fd10a61a8d9f245005c86adc4880085ce` |
| `load_label_registry` | `c104937935aaeefd1d521bbcd53b96ae933fd644cff98d8333d720fff6d7c0c2` |
| `save_label_registry` | `f041bf52b21ae35f2adda94914050a883334e08561c723ea57e5d66eda66ecfa` |
| `assign_human_labels` | `5a150c7b71e937a95dd09dfed4d69f365457ad4772d7ba37dc15daf6561d9b37` |

All four hashes are unchanged. Boundary verification confirms exactly four functions in the new module, 59 remaining local façade functions, and no duplicate S5A definitions in the façade.

The dependency direction remains acyclic:

- S5A uses S1 `safe_text`;
- S5A uses S4 `build_trade_id`;
- S1 and S4 do not depend on S5A.

## Byte-contract continuity

All S5 persistence gate fingerprints remain unchanged:

| Contract | SHA-256 |
|---|---|
| Non-empty saved registry | `eb96ee7fca17655042c102a3162d5d8cdbfaf1bda4ac17789ff00be245b159d6` |
| Empty saved registry | `451b629a29c79d2735940170b9a228bba8e67f66a373881534267240a5b21475` |
| Deterministic assignment | `e4f22c64c51f3a8405edf7252de58d057b7f759c208fe25eb7b10767954f6ec6` |
| Generic CSV fixture | `d1cf0f439a99544239b70e95fca11b48485fa190889083c92497d051eed8a57c` |
| Partial CSV failure artifact | `64c0dea2e1c321cbbcbf78285b8704a51abbc6b0be3117c8c3208ac6082a3284` |
| Raw 127-column ML CSV | `be6e308c2c2467a00f68a589f510e161d7414e4c815624c595c2aa8719173c29` |

Label validation precedence, exact exceptions, registry CRLF/header/order, missing-row handling, duplicate-key replacement, duplicate-label rejection, and fallback numbering all remain unchanged.

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

The hermetic summary CLI test executed `inspect_trades.py` directly and passed with deterministic output and empty stderr.

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

- No label validation, normalization, ordering, registry bytes, assignment, fallback, exception, or path behavior changed.
- No default path, CLI option, dispatch order, update trigger, public import name, or direct-script behavior changed.
- No repository label file, registry, archive, market data, runtime input, or generated artifact was read or modified.
- Generic CSV and raw ML CSV functions remain in the façade and were not refactored in S5A.
- Existing S1–S4 and S5 golden fingerprints remain unchanged.
- IU4, Live-L1, Exchange, Live, inputs, strategies, policies, and gates remain unchanged and locked.
- The foreign untracked file `scripts/build_rcc002_spec_bundle.py` was not read, modified, staged, or included.

## Outcome

S5A label persistence is complete within its approved boundary. The next controlled implementation is S5B extraction of only `write_csv_rows`, preserving its zero-byte empty output, first-row schema authority, CRLF, overwrite, and partial-failure contracts.
