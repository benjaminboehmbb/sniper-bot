# X1 Trade Inspector S5P Facade Inventory and Characterization Gate Evidence — 2026-08-15

Status: **PASS**

Branch: `codex/x1-trade-inspector-s5p-facade-inventory-characterization-gate-2026-08-15`

Base commit: `9a76cc13d8a51d5e8075b1b12690a8eea99546fb`

## Scope

This gate inventories the remaining top-level responsibilities in `tools/trade_inspector/inspect_trades.py`, selects the next cohesive extraction seam, and freezes its observable behavior before any production move.

The gate changes tests and evidence only. It does not change the facade, extracted modules, runtime inputs, policies, strategies, or generated runtime artifacts.

## Remaining facade inventory

After S5O integration, the 899-line facade contains nine locally defined functions:

| Responsibility | Functions | Source lines | Classification |
|---|---:|---:|---|
| Console reporting | 7 | 331 | cohesive pure-output seam |
| Built-in regression validation | 1 | 131 | validation orchestration |
| CLI entry point | 1 | 199 | top-level orchestration |

Detailed inventory:

| Function | Lines | Responsibility |
|---|---:|---|
| `print_trade_report` | 139 | single-trade console report |
| `print_summary` | 35 | compact row summary |
| `print_group_table` | 25 | grouped CSV-like terminal table |
| `print_trade_family_summary` | 14 | family/group reporting composition |
| `print_top_improvement_candidates` | 31 | ranked improvement report |
| `print_root_cause_attribution` | 28 | root-cause attribution report |
| `print_aggregate_intelligence` | 59 | aggregate reporting composition |
| `run_builtin_regression_validation` | 131 | regression-validation workflow |
| `main` | 199 | argument parsing and route orchestration |

## Selected S5P seam

The next extraction boundary is the seven-function console-reporting surface. These functions form one cohesive output layer: they write only to stdout, share formatting and aggregation helpers, and are called by orchestration without owning files, runtime state, source data, or policy decisions.

`run_builtin_regression_validation` and `main` remain in the facade for this step because they coordinate input loading, route selection, validation decisions, and process exit status.

Current facade SHA-256, unchanged by this gate:

`ca9a8fc748c87404a3b95a2f990e87e1f0d9c77ab89efb5b7cdbc14549941a13`

Prepared characterization-test SHA-256:

`6e886bb5f8dc121fc41bef3f8f0cf8f8adf812eeec3d8999b88032ce5f662daa`

## Reporting surface fingerprints

| Function | AST SHA-256 | Source-segment SHA-256 |
|---|---|---|
| `print_trade_report` | `e76568b49f48eedbbd75535d057776fa27b1eb824a93e04c9b74bc3b4e4b1338` | `dcf21bb8d5cbc31fc7cb0c73e269a40f868618a270559d02aff2d370be001826` |
| `print_summary` | `7a5f2e3558472cd29253ca7df030b37010575bc98efc2f627a087d22480051e0` | `b328e627086d7fbd36e1405bee85cfbaea55ca290e29b68c0db47b90e80e7d4c` |
| `print_group_table` | `e82c94e2ecb9fff1ca7eaf391bdea5fb98bc24107d8daa68937a4a967e1d1c9a` | `bf444d4085e66f1f03a5e574f71a044bf83659ffe0f3ac35e2c0df144d498f68` |
| `print_trade_family_summary` | `7c23dbd86b9e82a0df9989a7df56a1fef0a8e0f8d0aab4f3cbc7f38c98ec55c3` | `5b8e4925158858647e9e86a0da6e133b1f07715e18b478a7d1ce1b23ba8cf8a5` |
| `print_top_improvement_candidates` | `66196f5a67dc9a1b1010ed5d777eb225ef55d298aeae01a017197b3fd2ccdee0` | `a3930cef6d1c03b55c1eb29e284b2ebb8be6dd8098bf46788c9dde97390eff08` |
| `print_root_cause_attribution` | `a1518d14096ce50a9b248acfad083d14dc36b24c3d74a5268cf7fd4e4b264207` | `58b803ca26166e347bf25b65023fa7777d1aad1b8efd0c3cd870ec8a32f953fa` |
| `print_aggregate_intelligence` | `a66a1ac4d85f8c5c2caa77a65c3983070bc384c85113f6420628aa24eefcb5c0` | `a6a373bc905b41524e31a779a95979b98a4dd41a40d089a770bfa11254e578e5` |

Canonical reporting-surface fingerprint:

`646ccc72d8fd8e4c4fc4bdd7da9b4893b85031f14b7b052486415f4276e5ae64`

All seven callables are currently defined by the facade module. The extraction gate must later replace this inline identity with direct facade-to-module object identity.

## Observable output contracts

The complete single-trade fixture binds every report section, field order, separator, fallback, evidence list, diagnosis value, formatting rule, trailing blank line, and empty stderr.

The three-row reporting fixture binds compact summary and aggregate composition, including grouping, ranking, trade-family summaries, improvement candidates, and root-cause attribution. Empty input binds zero-count behavior. A direct `reverse=False` fixture binds the alternative group-table sort path.

| Scenario | stdout lines | stdout SHA-256 |
|---|---:|---|
| complete trade report | 118 | `761f3586f2718be32d5e7b6812ccc0189f138b318759c2b0e995d6a685d18a22` |
| three-row summary | 19 | `484345703e38ff381cbd33a40a76b1125a395f68e3846279cabfe3e109c33b21` |
| empty summary | 18 | `147e452576c2b62ef6437ca034350531d9e41137cf3583c6705ae38fa1d6ab65` |
| three-row aggregate intelligence | 64 | `0ac4243cebffe58a20ec3a4d12ca782b2a3104e5bc5275fa41b4882d12a89450` |
| empty aggregate intelligence | 51 | `c237b78299779d558eab6d708e85c7365b4cf7bc7c1575659c133d4495fa1a8a` |
| ascending group table | 5 | `42a9c58b2918c81a6ae9b448385cc7c6aa4afbe6be1746f6af324159962722ab` |

All scenarios bind empty stderr.

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

`git diff --check` passed.

## Safety and next step

Only characterization tests and this evidence document changed. IU4 ENFORCED, Live-L1, Exchange, and Live remain locked. No source data or runtime input was changed.

After integrating this gate into `main`, the next development step is the structure-only extraction of the seven reporting functions into `tools/trade_inspector/console_reporting.py`. The facade must import and re-export the exact callables for package and direct-script modes while preserving all bound AST, source, stdout, stderr, empty-input, and sort-order contracts.
