# X1 Trade Inspector S5Q Regression Validation Characterization Gate Evidence — 2026-08-15

Status: **PASS**

Branch: `codex/x1-trade-inspector-s5q-regression-validation-characterization-gate-2026-08-15`

Base commit: `8bf8b82d7f5a270d0114bac878b2431feeac6ba1`

## Scope

This gate freezes `run_builtin_regression_validation` before extraction from `tools/trade_inspector/inspect_trades.py`.

The gate binds dependency paths and call order, PASS and FAIL exit codes, diagnostic output, analysis-count checks, global-ID checks, root-cause checks, stderr behavior, and input-exception propagation.

Only synthetic in-memory fixtures and patched dependency seams are used. No archive, market-data, label, registry, runtime-input, or production file is read or changed.

## Production identity

`tools/trade_inspector/inspect_trades.py` remained byte-identical throughout the gate.

SHA-256 before and after:

`73f12e702523f818757b6b6b2e1a29e2f6beaae637bc32a249a1028fad6f07a8`

| Binding | Lines | AST SHA-256 | Source-segment SHA-256 |
|---|---:|---|---|
| `run_builtin_regression_validation` | 131 | `ab7964f9e9b3429fe114af456d9db2787df2d170809996081bf87eafe2159a8f` | `d8dcfec37e79180d0f2ecc8280dd9c2e752a4bdbbcdc084729ccdf536e00787c` |

Prepared characterization-test SHA-256:

`e5e32f19f8afa1b8dc62951c282c39274aea46fc2c78bc375e42efce641d57ec`

## Bound input and orchestration seams

The gate binds the exact resolved input paths:

- `/fixture/archive/trades_l1.jsonl`;
- `/fixture/archive/execution_audit.jsonl`;
- `/fixture/archive/l1_paper.log`;
- `/fixture/market.csv`;
- `/fixture/labels.txt`;
- `/fixture/registry.csv`.

It also binds the call chain:

1. load trades and audit JSONL;
2. parse log rows and build regime index;
3. parse market rows;
4. load label list and registry;
5. assign labels;
6. build analysis rows;
7. evaluate ten ordered single-key discovery groups;
8. evaluate six ordered pair groups;
9. construct and count call-scope global IDs;
10. compute root-cause attribution;
11. return PASS or the complete ordered FAIL list.

The ten group keys and six pair specifications are asserted in their exact current order. Dependency call arguments are asserted by object identity for loaded fixtures.

## PASS and FAIL matrix

| Scenario | Rows | Signal groups | NOT_ACTIONABLE | High warnings | WATCH | Root groups | Exit | stdout lines | stdout SHA-256 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| PASS | 9 | 57 | 57 | 57 | 6 | 4 | 0 | 18 | `08b621f09760de5e98c2d241213d20099062c1b9bd36e544ac7ea22084426927` |
| row/count FAIL | 8 | 57 | 57 | 57 | 6 | 4 | 1 | 22 | `bde1c54afb6f13653649bf3b6e434d0e2eb205cbb34de0857e9fbc70c9a43f10` |
| analysis-count FAIL | 9 | 0 | 0 | 0 | 0 | 0 | 1 | 23 | `8ee9b0b64ad4736ed424582802e553708c4841a6d1ddc5755ebdf6bb6c62bb60` |

The row/count failure binds four ordered errors:

1. unexpected trade count;
2. unexpected built-row count;
3. unexpected global-trade-row count;
4. unexpected global-ID count.

The analysis-count failure binds five ordered errors:

1. unexpected signal-group count;
2. unexpected NOT_ACTIONABLE count;
3. unexpected high-warning count;
4. unexpected WATCH count;
5. unexpected root-cause-group count.

All three completed scenarios bind empty stderr.

## Exception propagation

An input-failure fixture makes the first `read_jsonl` call raise `ValueError("broken fixture")`. The function prints only its deterministic four-line header, emits no stderr, performs no later dependency call, and propagates the original exception unchanged. It does not translate an unreadable input into a false PASS or an incomplete validation result.

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

`git diff --check` passed.

## Safety and next step

Only characterization tests and this evidence document changed. IU4 ENFORCED, Live-L1, Exchange, and Live remain locked. No source data or runtime input was changed.

After integrating this gate into `main`, the next development step is the structure-only extraction of `run_builtin_regression_validation` into `tools/trade_inspector/regression_validation.py`. The facade must import and re-export the exact callable in package and direct-script modes while preserving dependency patchability, all output hashes, exit codes, exception propagation, and call-order contracts.
