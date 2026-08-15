# X1 Trade Inspector S5X Import-Consolidation Design

Date: 2026-08-15

Branch: `codex/x1-trade-inspector-s5x-import-consolidation-design-2026-08-15`

Base commit: `c295186b0c5360328174fddd37c5518676f5ebad`

## Decision

The duplicated package/direct-script import branches may be consolidated in the next implementation step, but only through one explicit owner table and uncaught `importlib.import_module` calls.

A broad relative-import `try` with an `ImportError` direct-import fallback is forbidden. Such a fallback cannot distinguish an unavailable package context from a dependency failure raised inside a valid owner module and would violate the S5W fail-closed contract.

S5X is design-only. No production or test file changes in this step.

## Approved design

The implementation must use one literal ordered owner table with the 22 existing owner names and their 100 existing exported attributes. Conceptually:

```python
import importlib as _importlib

_EXPORTS_BY_OWNER = (
    ("aggregate_csv", (...)),
    ...
    ("regime_identity_rows", (...)),
)

__all__ = tuple(sorted(
    name
    for _owner_name, _export_names in _EXPORTS_BY_OWNER
    for name in _export_names
))

_owner_prefix = f"{__package__}." if __package__ else ""
for _owner_name, _export_names in _EXPORTS_BY_OWNER:
    _owner_module = _importlib.import_module(f"{_owner_prefix}{_owner_name}")
    for _export_name in _export_names:
        globals()[_export_name] = getattr(_owner_module, _export_name)
```

All implementation-only names must start with an underscore so they do not expand the direct public facade surface. No import exception may be caught or translated.

## Preserved module identity

The prefix selection preserves the current module identity split:

- package mode imports `tools.trade_inspector.<owner>`;
- direct-script mode imports `<owner>` after Python has placed the script directory on `sys.path`;
- no package-mode owner is silently replaced by a top-level owner;
- no direct-mode owner is silently replaced by a package owner.

This is important because the current facade returns the exact objects owned by the mode-specific modules, not copies or wrappers.

## Single-source export policy

The explicit 100-name `__all__` remains deterministic but is derived from the single owner table rather than maintained as a second independent 100-name literal.

Sorting the names extracted from the S5W table produces:

- count: 100;
- unique count: 100;
- exact S5U ordered-name SHA-256: `653b92ca002c2c8adc5aee88853b803fd952deb1f7aa69ed7a56952226fba517`.

The four S5V support attributes remain direct attributes and remain absent from the owner table and `__all__`:

- `Any`
- `Path`
- `annotations`
- `argparse`

## Prototype validation

The approved algorithm was evaluated read-only against the current S5W import table in fresh package and direct-script processes.

Package mode result:

```text
owners=22
names=100
unique=100
identity=true
name_set_matches___all__=true
```

Direct-script mode result:

```text
owners=22
names=100
unique=100
identity=true
name_set_matches___all__=true
```

All 100 resolved objects were identity-equal to the corresponding current facade attributes in both modes. The owner order remains the S5W order and its normalized table fingerprint remains:

`e0e8d5371ce64583ffa8568d8305cf59d769362a76c20b16345eae79f2d072bb`

## Required implementation gates

The implementation step must update the structural S5W test from dual `ImportFrom` branches to the single literal table and dynamic binding loop while preserving all behavioral contracts:

1. exactly 22 owners and 100 unique domain/default names;
2. exact owner/name/alias table fingerprint;
3. exact 100-name `__all__` order and fingerprint;
4. package/direct object identity for all 100 names;
5. exact package/direct full owner-module mode;
6. uncaught original `ModuleNotFoundError` when an owner is blocked;
7. no broad `ImportError` handler in the facade;
8. unchanged four support-attribute identities and wildcard exclusion;
9. unchanged `inspect_trades.main is cli_orchestration.main` binding;
10. unchanged `if __name__ == "__main__": raise SystemExit(main())` boundary;
11. unchanged CLI output and exit behavior;
12. complete focused and regression suites.

## Rejected alternatives

### Broad import fallback

Rejected because an internal dependency failure could be misclassified as an import-mode mismatch.

### Mutating `__package__` or `sys.path` in the facade

Rejected because it changes interpreter-visible module context and may create duplicate package/top-level owner modules.

### Wrapper or proxy exports

Rejected because wrappers break object identity, signatures, defaults, and patch points.

### Keeping two generated import branches

Rejected because it retains the duplication and leaves drift possible.

## Baseline validation

Focused characterization:

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest -q tests.trade_inspector.test_inspect_trades_characterization

Ran 96 tests
OK
```

Full regression:

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -s tests/regression -p 'test_*.py'

Ran 170 tests
OK
```

Unchanged baseline fingerprints:

- facade: `e292455230ec415f671200077d4f034dd2722f3390514d99014409fb8f251b6f`;
- characterization tests: `81b2ba71c253bcc7ede5dafe30a8ec5d30ae5d4a60aa57d69a8b4fb05d436743`.

## Safety

IU4 ENFORCED, Live-L1, Exchange, and Live remain locked. No source data, runtime input, production file, or test file changed. The unrelated untracked `scripts/build_rcc002_spec_bundle.py` was not read, modified, staged, or committed.

## Next step

After integrating S5X into `main`, S5Y should implement the approved single-owner-table binding, update the S5W structural characterization without weakening it, run all focused and regression tests, and commit production code, tests, and implementation evidence on a separate branch.
