# X1 Trade Inspector S5P Console Reporting Extraction Evidence — 2026-08-15

Status: **PASS**

Branch: `codex/x1-trade-inspector-s5p-console-reporting-extraction-2026-08-15`

Base commit: `4bc5c37fda90f17a1f4d041066da6b82e2b907dd`

## Scope

This change extracts the seven-function console-reporting surface selected and frozen by the S5P characterization gate into:

- `tools/trade_inspector/console_reporting.py`.

The facade imports and re-exports all seven functions in both package and direct-script modes. No formatting, aggregation, ranking, sorting, fallback, stdout, or stderr behavior changed.

## Structure and facade identity

The extracted module contains:

- `print_trade_report`;
- `print_summary`;
- `print_group_table`;
- `print_trade_family_summary`;
- `print_top_improvement_candidates`;
- `print_root_cause_attribution`;
- `print_aggregate_intelligence`.

For every function, the test suite binds:

```text
inspect_trades.<name> is console_reporting.<name>
```

The facade now defines only `run_builtin_regression_validation` and `main`. Its size decreased from 899 to 571 lines. The reporting module contains 358 lines including imports and dual-mode dependency bindings.

| File | SHA-256 |
|---|---|
| `tools/trade_inspector/inspect_trades.py` | `73f12e702523f818757b6b6b2e1a29e2f6beaae637bc32a249a1028fad6f07a8` |
| `tools/trade_inspector/console_reporting.py` | `ea5b4de9af3e19eba384ad0047b51efa86a329bdf4c516cd0d26c13dcc0f890f` |
| `tests/trade_inspector/test_inspect_trades_characterization.py` | `7f68693326c5d6a37c3835726b5f2842244621a9fd51202c7afb8b0fd955de75` |

## Preserved reporting surface

| Function | AST SHA-256 | Source-segment SHA-256 |
|---|---|---|
| `print_trade_report` | `e76568b49f48eedbbd75535d057776fa27b1eb824a93e04c9b74bc3b4e4b1338` | `dcf21bb8d5cbc31fc7cb0c73e269a40f868618a270559d02aff2d370be001826` |
| `print_summary` | `7a5f2e3558472cd29253ca7df030b37010575bc98efc2f627a087d22480051e0` | `b328e627086d7fbd36e1405bee85cfbaea55ca290e29b68c0db47b90e80e7d4c` |
| `print_group_table` | `e82c94e2ecb9fff1ca7eaf391bdea5fb98bc24107d8daa68937a4a967e1d1c9a` | `bf444d4085e66f1f03a5e574f71a044bf83659ffe0f3ac35e2c0df144d498f68` |
| `print_trade_family_summary` | `7c23dbd86b9e82a0df9989a7df56a1fef0a8e0f8d0aab4f3cbc7f38c98ec55c3` | `5b8e4925158858647e9e86a0da6e133b1f07715e18b478a7d1ce1b23ba8cf8a5` |
| `print_top_improvement_candidates` | `66196f5a67dc9a1b1010ed5d777eb225ef55d298aeae01a017197b3fd2ccdee0` | `a3930cef6d1c03b55c1eb29e284b2ebb8be6dd8098bf46788c9dde97390eff08` |
| `print_root_cause_attribution` | `a1518d14096ce50a9b248acfad083d14dc36b24c3d74a5268cf7fd4e4b264207` | `58b803ca26166e347bf25b65023fa7777d1aad1b8efd0c3cd870ec8a32f953fa` |
| `print_aggregate_intelligence` | `a66a1ac4d85f8c5c2caa77a65c3983070bc384c85113f6420628aa24eefcb5c0` | `a6a373bc905b41524e31a779a95979b98a4dd41a40d089a770bfa11254e578e5` |

Canonical reporting-surface fingerprint remains:

`646ccc72d8fd8e4c4fc4bdd7da9b4893b85031f14b7b052486415f4276e5ae64`

## Preserved output contracts

| Scenario | stdout lines | stdout SHA-256 |
|---|---:|---|
| complete trade report | 118 | `761f3586f2718be32d5e7b6812ccc0189f138b318759c2b0e995d6a685d18a22` |
| three-row summary | 19 | `484345703e38ff381cbd33a40a76b1125a395f68e3846279cabfe3e109c33b21` |
| empty summary | 18 | `147e452576c2b62ef6437ca034350531d9e41137cf3583c6705ae38fa1d6ab65` |
| three-row aggregate intelligence | 64 | `0ac4243cebffe58a20ec3a4d12ca782b2a3104e5bc5275fa41b4882d12a89450` |
| empty aggregate intelligence | 51 | `c237b78299779d558eab6d708e85c7365b4cf7bc7c1575659c133d4495fa1a8a` |
| ascending group table | 5 | `42a9c58b2918c81a6ae9b448385cc7c6aa4afbe6be1746f6af324159962722ab` |

All scenarios retain empty stderr.

## Validation

Focused characterization:

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest -q tests.trade_inspector.test_inspect_trades_characterization

Ran 80 tests
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

Only the reporting module extraction, facade imports, callable-identity assertions, and this evidence document changed. IU4 ENFORCED, Live-L1, Exchange, and Live remain locked. No source data or runtime input was changed.

After integrating this extraction into `main`, the next development step is the S5Q characterization gate for `run_builtin_regression_validation`. That gate must bind pass and fail exit codes, exact diagnostic output, input seams, and orchestration side effects before the validation workflow can be extracted.
