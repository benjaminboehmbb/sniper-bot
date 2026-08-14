# X1 Trade Inspector S2 Archive-Intake Extraction Evidence — 2026-08-14

Status: **PASS**

Branch: `codex/x1-trade-inspector-s2-archive-intake-extraction-2026-08-14`

Base commit: `e73ff51ef5e92da88bf9338f561961e0922f81df`

## Decision

The two approved S2 functions were extracted from `tools/trade_inspector/inspect_trades.py` into `tools/trade_inspector/archive_intake.py` without changing their implementations or public names:

- `count_valid_jsonl`
- `run_archive_intake_validation`

`inspect_trades.py` remains the stable import and command-line façade. It imports and re-exports the extracted function objects. Both package execution and direct file execution retain explicit import paths.

## Changed files

| File | Role | SHA-256 before commit |
|---|---|---|
| `tools/trade_inspector/archive_intake.py` | New fail-closed archive-intake module | `5b09db70c4c50ec5e855b59bdeb5456fcd1e833c572ff1e791dc0af304b13678` |
| `tools/trade_inspector/inspect_trades.py` | Stable façade and re-exports | `fd266a102ea621cea7ac055330b28c17c3c4759bd768c9cf84f67b0ad0684e57` |
| `tests/trade_inspector/test_inspect_trades_characterization.py` | Exact module-object re-export assertions | `32bb7cbbd2a3a913293d4166ce220a239de8ade055023c02f9c27b3e13c01153` |

Pre-extraction façade SHA-256:

`a0fcc9779b59cb00ea24b43eb0208018365caf2d7301d6cf2a87a6e19c594737`

## Semantic identity

AST hashes were computed before extraction and re-derived from the new module after extraction:

| Function | AST SHA-256 |
|---|---|
| `count_valid_jsonl` | `5dbddefc21823025ce965e4c84f48ce51ae09c8de30c73fce11069f4c57413db` |
| `run_archive_intake_validation` | `09e0cea83e55666125bdc77098725391b92500eabd7bd0db310ebcd9eb1ca5ac` |

Both hashes are unchanged. Boundary verification also confirms that:

- the façade no longer defines either function;
- the new module defines exactly the two approved functions;
- façade attributes are the exact new-module function objects.

## Characterization contract

The integrated S2 gate continues to bind:

- complete hermetic archive PASS with exact output, zero warnings, and return value `0`;
- malformed trade JSONL plus metadata count mismatch with the exact five-warning, FAIL-marker, and two-error order and return value `1`;
- direct execution of `tools/trade_inspector/inspect_trades.py` through the existing hermetic CLI test.

## Focused validation

Command:

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest -v tests.trade_inspector.test_inspect_trades_characterization
```

Result:

```text
Ran 8 tests
OK
```

## Full regression

Command:

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -s tests/regression -p 'test_*.py'
```

Result:

```text
Ran 170 tests
OK
```

## Safety boundary

- No archive-intake implementation statement, branch order, file list, metadata field, status allowlist, warning, error, output line, or exit value changed.
- No CLI option, default, dispatcher order, or public import name changed.
- No repository archive, market data, runtime input, generated artifact, or label registry was read or modified.
- IU4, Live-L1, Exchange, Live, inputs, strategies, policies, and gates remain unchanged and locked.
- The foreign untracked file `scripts/build_rcc002_spec_bundle.py` was not read, modified, staged, or included.

## Outcome

S2 extraction is complete within its approved boundary. Broader archive, cross-archive, export, or CLI refactoring remains outside this change.
