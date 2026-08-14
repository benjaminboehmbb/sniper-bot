# X1 Trade Inspector S1 Primitives Extraction Evidence — 2026-08-14

Status: **PASS**

Branch: `codex/x1-trade-inspector-s1-primitives-extraction-2026-08-14`

Base commit: `6b85bc1b0e40bf42a5d8f5c709ee59649ab393c9`

## Decision

The five approved compatibility primitives were extracted from `tools/trade_inspector/inspect_trades.py` into `tools/trade_inspector/inspection_primitives.py` without changing their implementations or public names.

`inspect_trades.py` remains the stable command-line and import façade. Package imports re-export the extracted function objects, while direct execution of `python tools/trade_inspector/inspect_trades.py ...` uses an explicit non-package import branch. Both paths are exercised by the characterization suite.

## Changed files

| File | Role | SHA-256 before commit |
|---|---|---|
| `tools/trade_inspector/inspection_primitives.py` | New exact-semantics primitive module | `1c9e214547fd45e1071bf38e3aa51a92e26bb4c21f2f63bdfeacae1a1ed89e16` |
| `tools/trade_inspector/inspect_trades.py` | Stable façade; imports/re-exports primitives | `a0fcc9779b59cb00ea24b43eb0208018365caf2d7301d6cf2a87a6e19c594737` |
| `tests/trade_inspector/test_inspect_trades_characterization.py` | Adds re-export and conversion-matrix gate | `ed7f28fae5cc73333c2402e21948997bb15ea43d3ceb2b76c1e9d3453cbfc816` |

Pre-extraction façade SHA-256:

`d8b6bc6ab6fdee30f01e5c058e165266c73c1ba64c2563665e0cd2df1f041b2f`

## Extracted boundary

- `safe_text`
- `safe_float`
- `safe_int`
- `parse_ts`
- `ts_key`

AST boundary verification confirms that the façade now defines 84 functions, the primitive module defines exactly the five names above, and none of the five remains duplicated as a function definition in the façade.

## Compatibility evidence

The characterization gate verifies that façade attributes are the exact package-module function objects. The conversion matrix binds current behavior for:

| Input | `safe_float(..., -9.0)` | `safe_int(..., -9)` |
|---|---:|---:|
| `None` | `-9.0` | `-9` |
| empty string | `-9.0` | `-9` |
| `"1"` | `1.0` | `1` |
| `"1.0"` | `1.0` | `-9` |
| `"bad"` | `-9.0` | `-9` |
| `True` | `1.0` | `1` |

The representative 127-field row retains semantic SHA-256:

`54fc961343d463d4e55d6489c70ec9ffcf3892acc9155b45b95e5f9408a2ce24`

The existing hermetic CLI test executes the script by file path, so the direct-execution import branch is protected in addition to normal package imports.

## Focused validation

Command:

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest -v tests.trade_inspector.test_inspect_trades_characterization
```

Result:

```text
Ran 7 tests
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

- No CLI option, default path, dispatch order, exit code, output name, field order, trade ID, or scientific calculation was changed.
- Existing `tools/trade_inspector/common/` helpers were not altered because their conversion contracts differ.
- No runtime input, market data, archive, label registry, or generated artifact was changed.
- IU4, Live-L1, Exchange, and Live remain unchanged and locked.
- The foreign untracked file `scripts/build_rcc002_spec_bundle.py` was not read, modified, staged, or included.

## Outcome

S1 is complete and passes its defined acceptance boundary. Broad modularization remains disallowed. The next eligible seam is S2 archive-intake validation, but only after adding a hermetic complete-PASS fixture and exact warning/error-order assertions as required by the seam analysis.
