# X1 Trade Inspector S5R-B CLI Orchestration Extraction Evidence — 2026-08-15

Status: **PASS**

Branch: `codex/x1-trade-inspector-s5rb-cli-orchestration-extraction-2026-08-15`

Base commit: `d3f4cc9254b65ba87720098c8054540457f6a6ac`

## Scope

This change extracts the fully characterized and S5R-A-repaired CLI orchestration from `tools/trade_inspector/inspect_trades.py` into:

- `tools/trade_inspector/cli_orchestration.py`.

The facade imports and re-exports the exact `main` callable and all four default-path constants in both package and direct-script modes. The existing `if __name__ == "__main__"` block remains in `inspect_trades.py` and continues to terminate with `SystemExit(main())`.

No parser option, default value, route order, input order, export argument, diagnostic text, exit code, exception path, archive-intake repair, or cross-archive behavior changed.

## Structure and facade identity

The characterization suite binds these identities:

```text
inspect_trades.main is cli_orchestration.main
inspect_trades.DEFAULT_ARCHIVE_DIR is cli_orchestration.DEFAULT_ARCHIVE_DIR
inspect_trades.DEFAULT_MARKET_CSV is cli_orchestration.DEFAULT_MARKET_CSV
inspect_trades.DEFAULT_LABEL_LIST is cli_orchestration.DEFAULT_LABEL_LIST
inspect_trades.DEFAULT_LABEL_REGISTRY is cli_orchestration.DEFAULT_LABEL_REGISTRY
```

Calls continue through `inspect_trades.main`; dependency seams are patched at the new owning module. The facade contains no locally defined function. Its 241 lines retain the established compatibility re-exports and executable script boundary. The orchestration module contains 296 lines including focused imports, dual package/direct-script bindings, defaults, the exact moved function, and `__all__`.

| File | SHA-256 |
|---|---|
| `tools/trade_inspector/inspect_trades.py` | `5f0773af9ce542f68b4156683f7c7d27c61b72f431e5f2bc52821d8fa01a2339` |
| `tools/trade_inspector/cli_orchestration.py` | `332eb0831a471eb2483861eff1c7a003bf78fb0ddfbb5636d11e8497160585f6` |
| `tests/trade_inspector/test_inspect_trades_characterization.py` | `166d4ede3b4a55e444ebc53d05777c0cf55581ebd4212fd41d210e35244773ca` |

## Preserved main binding

The moved function remains identical to the repaired S5R-A production binding:

| Binding | Lines | AST SHA-256 | Source-segment SHA-256 |
|---|---:|---|---|
| `main` | 200 | `e156ee20dc356ac0468e36c341b5616e4b6f4cd49a0bb5cd9cb0052a9eb97deb` | `b24a8238935b6625390a809dbf13ea8d8b8757207b9bcec9c8afa353c794109d` |

This preserves:

- the complete 26-field parser namespace;
- regression-before-intake early precedence;
- fail-fast missing intake target;
- repaired requested intake-target binding;
- common input, labeling, persistence, and row-building order;
- trade-report precedence;
- all 15 ordered report/export delegates;
- cross-archive inclusion, loading, error aggregation, and call-scope ID behavior;
- exact no-selection output;
- return and `SystemExit` behavior.

## Package and direct-script ownership

`cli_orchestration.py` resolves every dependency directly from its owning module. Both import modes are present:

- relative package imports when loaded as `tools.trade_inspector.cli_orchestration`;
- direct sibling imports when `inspect_trades.py` is executed as a script.

The facade preserves its prior broader re-export surface. No compatibility import was removed as part of this structure-only step.

## Validation

Focused characterization:

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest -q tests.trade_inspector.test_inspect_trades_characterization

Ran 89 tests
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

Only the orchestration-module extraction, facade import/re-export wiring, dependency-owner and identity assertions, and this evidence document changed. IU4 ENFORCED, Live-L1, Exchange, and Live remain locked. No source data or runtime input was read or changed.

After integrating this extraction into `main`, the next development step is S5S: characterize the facade's complete public re-export and direct-script compatibility surface before considering any import cleanup or explicit `__all__`. No compatibility name may be removed without that gate.
