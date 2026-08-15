# X1 Trade Inspector S5U Explicit Facade `__all__`

Date: 2026-08-15

Branch: `codex/x1-trade-inspector-s5u-explicit-facade-all-2026-08-15`

Base commit: `1d8d2bb4887217904bfb48744c309569573cc395`

## Scope

S5U implements the namespace policy approved by the S5T facade-consumer audit. The executable facade remains at `tools/trade_inspector/inspect_trades.py`, all existing direct attributes remain available, and wildcard exports are now explicit and deterministic.

No orchestration, analysis, persistence, archive intake, runtime input, or trading behavior changed.

## Implemented contract

The facade defines an ordered `__all__` tuple with exactly 100 unique domain/default names.

The four support names remain directly accessible for compatibility but are deliberately absent from wildcard export:

- `Any`
- `Path`
- `annotations`
- `argparse`

The ordered wildcard-name fingerprint is computed from the UTF-8 encoding of the names joined by newlines with a final newline:

`653b92ca002c2c8adc5aee88853b803fd952deb1f7aa69ed7a56952226fba517`

The contract is identical for:

1. package import through `tools.trade_inspector.inspect_trades`;
2. direct-script import through the `tools/trade_inspector` directory;
3. wildcard import from either import mode.

Every wildcard-exported object is identity-equal to the corresponding direct facade attribute. The existing 104-name direct public surface remains unchanged.

## Behavioral bindings

The characterization suite now binds:

- exact `__all__` order, count, uniqueness, and fingerprint;
- package-mode wildcard names and object identities;
- direct-script-mode wildcard names and object identities;
- exclusion of all four support names from both wildcard modes;
- continued direct accessibility of all four support names;
- the pre-existing complete 104-name direct facade surface;
- the pre-existing package/direct owner mapping.

The CLI owner and behavior remain unchanged. `inspect_trades.main` is still identity-bound to `cli_orchestration.main`, whose AST fingerprint remains:

`e156ee20dc356ac0468e36c341b5616e4b6f4cd49a0bb5cd9cb0052a9eb97deb`

## Artifact fingerprints

- `tools/trade_inspector/inspect_trades.py`: `e292455230ec415f671200077d4f034dd2722f3390514d99014409fb8f251b6f`
- `tests/trade_inspector/test_inspect_trades_characterization.py`: `5cda6f30c33dd325865db229176b7c60a3aa5c1cb6e1a30172dd97a13154a05e`

## Validation

Focused characterization:

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest -q tests.trade_inspector.test_inspect_trades_characterization

Ran 93 tests
OK
```

Full regression:

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -s tests/regression -p 'test_*.py'

Ran 170 tests
OK
```

`git diff --check` also passed.

## Safety

IU4 ENFORCED, Live-L1, Exchange, and Live remain locked. No source data or runtime input was changed. The unrelated untracked `scripts/build_rcc002_spec_bundle.py` was not read, modified, staged, or committed.

## Next step

After integrating S5U into `main`, S5V should be a separate support-attribute compatibility decision gate. It should determine whether the four non-wildcard support attributes must remain directly accessible for external compatibility or can later be removed through underscored imports. No direct attribute should be removed without that explicit gate.
