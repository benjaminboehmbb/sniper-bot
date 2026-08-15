# X1 Trade Inspector S5W Import-Table Characterization Gate

Date: 2026-08-15

Branch: `codex/x1-trade-inspector-s5w-import-table-characterization-gate-2026-08-15`

Base commit: `6a5c7d4f4fa8c21b06c5afb8f53980ccd3b2f64a`

## Scope

S5W characterizes the duplicated package/direct-script import boundary in `tools/trade_inspector/inspect_trades.py` before any consolidation is attempted.

No production file changes in this gate.

## Import-table contract

The facade contains one top-level `if __package__` import gate.

Both branches contain:

- exactly 22 `ImportFrom` statements;
- exactly 100 imported domain/default names;
- no duplicate imported name;
- the same ordered owner modules, names, and aliases;
- the complete name set defined by the 100-name explicit `__all__` contract.

The only structural difference is import level:

- package branch: every import has relative level 1;
- direct-script branch: every import has absolute level 0.

The normalized ordered import-table SHA-256 is:

`e0e8d5371ce64583ffa8568d8305cf59d769362a76c20b16345eae79f2d072bb`

The fingerprint is computed from compact JSON containing the ordered module/name/alias table, excluding the intentional relative-import level difference.

## Fail-closed import behavior

S5W blocks the first owner module in fresh subprocesses and binds exact propagation in both modes:

- package mode blocks `tools.trade_inspector.aggregate_csv`;
- direct mode blocks `aggregate_csv`;
- both imports fail with the original `ModuleNotFoundError`;
- neither mode silently switches to the other import strategy;
- no partially imported facade is accepted as success.

This contract rules out a broad `try relative import / except ImportError / use direct import` consolidation because such a fallback could mask a dependency failure inside an owner module.

## Executable boundary

The facade contains exactly one top-level `__name__ == "__main__"` boundary. It remains structurally equivalent to:

```python
if __name__ == "__main__":
    raise SystemExit(main())
```

Its AST SHA-256 is:

`f0ea0be627ebd2887d7f161de9c610e749cbd38d176e8efffefbc0424d175c46`

## Production identity

The unchanged facade SHA-256 is:

`e292455230ec415f671200077d4f034dd2722f3390514d99014409fb8f251b6f`

The updated characterization-test SHA-256 is:

`81b2ba71c253bcc7ede5dafe30a8ec5d30ae5d4a60aa57d69a8b4fb05d436743`

## Validation

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

`git diff --check` passed.

## Safety

IU4 ENFORCED, Live-L1, Exchange, and Live remain locked. No source data, runtime input, production behavior, or import implementation changed. The unrelated untracked `scripts/build_rcc002_spec_bundle.py` was not read, modified, staged, or committed.

## Next step

After integrating S5W into `main`, S5X should define the consolidation design and then replace the duplicate table only if the design preserves all S5W contracts. In particular, it must not use a broad `ImportError` fallback. Package/direct identities, exact fail-closed dependency errors, the 100-name facade surface, support-attribute compatibility, and the executable boundary must remain unchanged.
