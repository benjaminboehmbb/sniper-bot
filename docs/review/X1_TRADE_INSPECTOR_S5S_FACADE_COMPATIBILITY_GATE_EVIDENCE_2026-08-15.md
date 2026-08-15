# X1 Trade Inspector S5S Facade Compatibility Gate Evidence — 2026-08-15

Status: **PASS**

Branch: `codex/x1-trade-inspector-s5s-facade-compatibility-gate-2026-08-15`

Base commit: `e747f0949cda966f0d213bb95b9c297bc063d9ed`

## Scope

This gate freezes the complete runtime-visible public namespace of `tools/trade_inspector/inspect_trades.py` after the S5R-B CLI extraction.

The gate binds:

- every non-underscore name currently reachable from the facade;
- exact object identity for every domain/default re-export;
- the four runtime-visible support names;
- exact owner coverage without duplicate ownership;
- equivalent public names and normalized owners in isolated direct-script mode;
- continued CLI execution through the existing script path.

Only runtime introspection, isolated subprocess probing, and tests are used. Production code and inputs remain unchanged.

## Production identity

`tools/trade_inspector/inspect_trades.py` remained byte-identical throughout the gate.

SHA-256 before and after:

`5f0773af9ce542f68b4156683f7c7d27c61b72f431e5f2bc52821d8fa01a2339`

Prepared characterization-test SHA-256:

`3e93fe1bcfc66db13eb1ae0988016f346ce5c2d8e6fa07553f10f2268ab8a8ea`

## Complete public surface

The facade exposes exactly 104 non-underscore names.

Canonical sorted-name SHA-256:

`e64235d88fcb39eb4da84e338130abe72cdaacf5c893aed2173e44e9957db3f6`

Canonical package-owner mapping SHA-256:

`7a972aa9123b7df650ce2c77b8c4eb11d58e43fe2e4cf7346627a72cb8c36f89`

Canonical normalized-owner mapping SHA-256:

`5f63601eec7f0a359a14e37e182809866c2d4fcd0a67c4a71f1446443b70e00f`

The 100 compatibility/default names are bound by exact object identity to these owners:

| Owner | Names |
|---|---:|
| aggregate CSV | 9 |
| archive intake | 2 |
| CLI orchestration/defaults | 5 |
| console reporting | 7 |
| CSV persistence | 1 |
| three cross-archive exporters | 3 |
| feature preparation | 7 |
| feature importance | 3 |
| feature discovery | 6 |
| feature stability | 4 |
| global-trade database | 1 |
| inspection primitives | 5 |
| label registry | 4 |
| leakage audit | 6 |
| ML dataset | 7 |
| multi-archive loader | 8 |
| path diagnosis | 11 |
| raw ML CSV | 1 |
| regression validation | 1 |
| regime/identity rows | 9 |

The test asserts that these groups cover every expected compatibility/default name exactly once and that every facade object is the same object as its owner export.

## Runtime-visible support names

Four additional names are currently public because they are imported into the facade module:

- `Any`;
- `Path`;
- `annotations`;
- `argparse`.

Their current identities are also frozen. This gate does not classify them as supported application API and does not authorize their removal. They are recorded as support-name leaks for a later consumer and namespace-policy review.

## Direct-script compatibility

An isolated subprocess uses `runpy.run_path` with a non-`__main__` probe name and the facade directory on `sys.path`. This exercises the direct sibling-import branch without invoking CLI parsing.

The direct-script namespace must expose the same exact 104-name tuple. For every name, the owner module's normalized tail must equal the package-mode owner tail. In particular, `main` remains owned by `cli_orchestration` in both modes.

The normal executable check also remains successful:

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python tools/trade_inspector/inspect_trades.py --help

exit 0
```

## Validation

Focused characterization:

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest -q tests.trade_inspector.test_inspect_trades_characterization

Ran 91 tests
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

After integrating this gate into `main`, the next development step is S5T: a repository-wide facade-consumer and namespace-policy audit. It must distinguish intentionally supported re-exports from incidental support names and wildcard-import behavior. No facade name may be removed or hidden until that audit proves the change safe and defines the compatibility policy.
