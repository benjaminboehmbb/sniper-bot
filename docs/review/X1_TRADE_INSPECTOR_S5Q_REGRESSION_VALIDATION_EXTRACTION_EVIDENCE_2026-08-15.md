# X1 Trade Inspector S5Q Regression Validation Extraction Evidence — 2026-08-15

Status: **PASS**

Branch: `codex/x1-trade-inspector-s5q-regression-validation-extraction-2026-08-15`

Base commit: `401173f50cc34cdfd7e6060dcb91097c00a15b49`

## Scope

This change extracts the S5Q-gated `run_builtin_regression_validation` workflow from `tools/trade_inspector/inspect_trades.py` into:

- `tools/trade_inspector/regression_validation.py`.

The facade imports and re-exports the exact callable in package and direct-script modes. The function body, dependency order, diagnostic text, stdout and stderr behavior, exit codes, and exception propagation are unchanged.

## Structure and facade identity

The characterization suite binds:

```text
inspect_trades.run_builtin_regression_validation is regression_validation.run_builtin_regression_validation
```

Calls continue through the facade export while dependency seams are patched at their new owning module. The facade now defines only `main`; it contains 439 lines. The extracted module contains 152 lines including imports and dual-mode dependency bindings.

| File | SHA-256 |
|---|---|
| `tools/trade_inspector/inspect_trades.py` | `d19622fa4f9c6d8f3f272708bdb03348f3e13dce72b9bbeb23a7b54227bf137e` |
| `tools/trade_inspector/regression_validation.py` | `8a5e18d3e14e3df5a5e4ca85535cfee1d2e21957d41f1c3655b8578f3ec3a624` |
| `tests/trade_inspector/test_inspect_trades_characterization.py` | `1990c3d192d69dee481ca5c51e9db569295d74a9695b973bc2ad9193a24ec2c1` |

## Preserved production binding

The moved function remains identical to the S5Q characterization gate:

| Binding | Lines | AST SHA-256 | Source-segment SHA-256 |
|---|---:|---|---|
| `run_builtin_regression_validation` | 131 | `ab7964f9e9b3429fe114af456d9db2787df2d170809996081bf87eafe2159a8f` | `d8dcfec37e79180d0f2ecc8280dd9c2e752a4bdbbcdc084729ccdf536e00787c` |

This preserves the complete ordered workflow from input loading through regime construction, labeling, row construction, discovery analysis, global-ID validation, root-cause attribution, and PASS/FAIL reporting.

## Preserved output and failure contracts

| Scenario | Exit | stdout lines | stdout SHA-256 |
|---|---:|---:|---|
| PASS | 0 | 18 | `08b621f09760de5e98c2d241213d20099062c1b9bd36e544ac7ea22084426927` |
| row/count FAIL | 1 | 22 | `bde1c54afb6f13653649bf3b6e434d0e2eb205cbb34de0857e9fbc70c9a43f10` |
| analysis-count FAIL | 1 | 23 | `8ee9b0b64ad4736ed424582802e553708c4841a6d1ddc5755ebdf6bb6c62bb60` |

All three completed scenarios retain empty stderr. An input exception still propagates unchanged after the exact deterministic four-line header, with empty stderr and without invoking later dependencies.

## Validation

Focused characterization:

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest -q tests.trade_inspector.test_inspect_trades_characterization

Ran 82 tests
OK
```

Full regression:

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -s tests/regression -p 'test_*.py'

Ran 170 tests
OK
```

Direct-script import and parser path:

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python tools/trade_inspector/inspect_trades.py --help

exit 0
```

`git diff --check` passed.

## Safety and next step

Only the regression-validation module extraction, facade imports, callable-identity and dependency-owner assertions, and this evidence document changed. IU4 ENFORCED, Live-L1, Exchange, and Live remain locked. No source data or runtime input was read or changed.

After integrating this extraction into `main`, the next development step is the S5R characterization gate for the remaining `main`/CLI orchestration. That gate must bind parser defaults, route precedence, delegated calls, exit codes, and side-effect boundaries before the final facade orchestration can be minimized.
