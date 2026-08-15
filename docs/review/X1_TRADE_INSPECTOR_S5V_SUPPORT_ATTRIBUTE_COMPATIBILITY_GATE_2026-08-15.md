# X1 Trade Inspector S5V Support-Attribute Compatibility Gate

Date: 2026-08-15

Branch: `codex/x1-trade-inspector-s5v-support-attribute-compatibility-gate-2026-08-15`

Base commit: `08543c6c546297dc032ec643679bc3ba99696492`

## Decision

The four non-domain support attributes remain directly accessible on the `inspect_trades` facade:

- `Any`
- `Path`
- `annotations`
- `argparse`

Removal is not authorized by S5V.

S5T proved that no tracked production consumer uses these attributes and S5U excluded them from the explicit wildcard surface. That is sufficient to keep wildcard imports clean, but it cannot prove that untracked or external callers do not use direct attribute access. Removing them would also break the 104-name direct facade contract frozen by S5S. The fail-closed compatibility decision is therefore to retain the attributes while keeping them outside `__all__`.

## Repository-consumer evidence

The S5T audit covered all 785 tracked Python files and found:

- zero production Python facade consumers;
- zero direct facade-name imports;
- zero wildcard facade imports;
- one test-module facade consumer;
- no tracked repository dependency on any of the four support attributes outside facade characterization.

Executable-path and documentation consumers call `tools/trade_inspector/inspect_trades.py`; they do not consume its Python support namespace.

## Bound compatibility contract

S5V adds an explicit package/direct-script identity contract. In both import modes:

- `Any is typing.Any`;
- `Path is pathlib.Path`;
- `annotations is __future__.annotations`;
- `argparse` is the standard-library `argparse` module;
- none of the four names is present in `__all__`.

The ordered support-name fingerprint is:

`01a442aad12e7abe76c04b21fb679660d97604a1aabebb7be5f41fed6fd7da92`

It is computed from `Any`, `Path`, `annotations`, and `argparse`, joined by newlines with a final newline.

## Production identity

No production file changed in S5V. The facade SHA-256 remains:

`e292455230ec415f671200077d4f034dd2722f3390514d99014409fb8f251b6f`

The updated characterization-test SHA-256 is:

`74a0f499bd5cea7d0f9d76b92086517b79557cefe3d648c86f4fa9d44331fa89`

## Validation

Focused characterization:

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest -q tests.trade_inspector.test_inspect_trades_characterization

Ran 94 tests
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

IU4 ENFORCED, Live-L1, Exchange, and Live remain locked. No source data, runtime input, production behavior, or facade export list changed. The unrelated untracked `scripts/build_rcc002_spec_bundle.py` was not read, modified, staged, or committed.

## Next step

After integrating S5V into `main`, S5W should characterize the duplicated package/direct-script import table in the facade. That gate must bind owner identities, failure behavior, and the executable boundary before any attempt to consolidate the two 100-name import branches.
