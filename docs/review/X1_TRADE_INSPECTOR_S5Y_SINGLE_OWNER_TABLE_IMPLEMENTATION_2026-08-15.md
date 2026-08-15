# X1 Trade Inspector S5Y Single-Owner-Table Implementation

Date: 2026-08-15

Branch: `codex/x1-trade-inspector-s5y-single-owner-table-implementation-2026-08-15`

Base commit: `512d067ac26852a4d1058980fd5d8828c6efe718`

## Result

S5Y implements the S5X-approved facade import consolidation.

The two duplicated 22-module/100-name package and direct-script import branches were replaced by:

1. one literal ordered `_EXPORTS_BY_OWNER` table;
2. one deterministic `__all__` derivation from that table;
3. one mode-aware owner prefix;
4. one uncaught `importlib.import_module` binding loop.

The facade decreased from 344 to 214 lines while retaining the complete compatibility surface and executable behavior.

## Preserved import table

The single table contains:

- 22 ordered owners;
- 100 exported domain/default names;
- 100 unique exported names;
- the exact S5W normalized table SHA-256: `e0e8d5371ce64583ffa8568d8305cf59d769362a76c20b16345eae79f2d072bb`.

The literal owner-table AST SHA-256 is:

`0d0c979e223a93426866ea250cf216c35579f70f4c30ffc39e9774c366ef0532`

The dynamic binding-loop AST SHA-256 is:

`4563a0e4fa008a81e4c53d07058ec5a71eaf565061b526ef2da155ce8267018c`

## Export surface

`__all__` is now derived by sorting the 100 names from the owner table. Its derivation AST SHA-256 is:

`74a0bea76fa176637f6359bc1fa415631a3c8d60652718330a4546c256e17002`

The resulting contract remains:

- `__all__` count: 100;
- `__all__` unique count: 100;
- ordered-name SHA-256: `653b92ca002c2c8adc5aee88853b803fd952deb1f7aa69ed7a56952226fba517`;
- direct public facade count: 104.

The four S5V support attributes remain directly available and excluded from `__all__`: `Any`, `Path`, `annotations`, and `argparse`.

## Mode identity

Package import resolves every owner as `tools.trade_inspector.<owner>`.

Direct-script import resolves every owner as `<owner>` from the script directory. A fresh direct-mode subprocess confirmed all 22 top-level owners and zero package-qualified owner modules.

All 100 facade objects remain identity-equal to their mode-specific owner attributes. `inspect_trades.main` remains identity-bound to `cli_orchestration.main`.

## Fail-closed behavior

The facade contains no `try` statement and does not catch `ImportError` or `ModuleNotFoundError`.

Blocking `tools.trade_inspector.aggregate_csv` in package mode or `aggregate_csv` in direct mode still propagates the original exact `ModuleNotFoundError`. There is no import-mode fallback, wrapper, proxy, or partial-success path.

## Executable boundary

The exact S5W boundary remains:

```python
if __name__ == "__main__":
    raise SystemExit(main())
```

Its AST SHA-256 remains:

`f0ea0be627ebd2887d7f161de9c610e749cbd38d176e8efffefbc0424d175c46`

Existing CLI output, argument defaults, archive-intake delegation, exit codes, and patch points remain covered by the characterization suite.

## Artifact fingerprints

- `tools/trade_inspector/inspect_trades.py`: `0bce51c0b48c1090175da54de48d0f7ee876641327678d22aeb545243139be59`
- `tests/trade_inspector/test_inspect_trades_characterization.py`: `7d5e390fc999ed6e190553e2056805be0af6f3148a70504c5b4d0f0f90dbf042`

## Validation

Focused characterization:

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest -q tests.trade_inspector.test_inspect_trades_characterization

Ran 97 tests
OK
```

Full regression:

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -s tests/regression -p 'test_*.py'

Ran 170 tests
OK
```

`git diff --check` passed.

## Safety

IU4 ENFORCED, Live-L1, Exchange, and Live remain locked. No source data or runtime input changed. The unrelated untracked `scripts/build_rcc002_spec_bundle.py` was not read, modified, staged, or committed.

## Next step

After integrating S5Y into `main`, S5Z should perform a Trade Inspector facade closure and quality audit. It should verify the final dependency graph, public and executable contracts, repository consumers, remaining duplication, and test ownership before declaring the facade refactor closed or selecting the next bounded seam.
