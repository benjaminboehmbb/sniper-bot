# X1 Trade Inspector S2 Archive-Intake Characterization Gate Evidence — 2026-08-14

Status: **PASS**

Branch: `codex/x1-trade-inspector-s2-archive-intake-characterization-gate-2026-08-14`

Base commit: `ae230125710ac6923238fc1a2699f5f303e2f47a`

## Decision

The S2 pre-extraction characterization gate is complete. No production function was moved or changed.

The gate now binds both sides of the existing archive-intake contract:

- a complete hermetic archive returns exit code `0` and emits the exact ordered PASS transcript with zero warnings;
- the existing malformed-JSON/count-mismatch fixture returns exit code `1` and emits the five optional-file warnings, the FAIL marker, and both errors in their exact current order.

This evidence makes the separately approved S2 extraction of `count_valid_jsonl` and `run_archive_intake_validation` technically eligible. It does not authorize that extraction by itself.

## Changed file

| File | Role | SHA-256 before commit |
|---|---|---|
| `tests/trade_inspector/test_inspect_trades_characterization.py` | Complete PASS fixture and ordered negative diagnostics | `68a6782fee1f3cb8d1b48582d41d6968fb4ad316998714c00143a6eef50bcb5f` |

Production façade SHA-256 remained unchanged:

`a0fcc9779b59cb00ea24b43eb0208018365caf2d7301d6cf2a87a6e19c594737`

## Complete PASS contract

The hermetic archive contains all four required files, all five optional files, complete metadata, two valid trade JSONL records, and two valid audit JSONL records.

The test binds:

- return value `0`;
- required-files check `PASS`;
- metadata-JSON check `PASS`;
- archive ID `fixture-pass`;
- trade counters `2` valid and `0` bad;
- audit counters `2` valid and `0` bad;
- warnings count `0`;
- terminal status `ARCHIVE_INTAKE: PASS`;
- every output line and blank line in exact order.

## Fail-closed ordering contract

The negative fixture binds this exact diagnostic sequence:

1. `CHECK warnings: 5`
2. missing `trade_lifecycle_snapshots.csv`
3. missing `monitor_status.json`
4. missing `runtime_control.json`
5. missing `loss_cluster_state.json`
6. missing `trades_l1_auto_analysis.csv`
7. `ARCHIVE_INTAKE: FAIL`
8. bad trade JSONL line count
9. metadata trade-count mismatch

The return value remains `1`.

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

- `tools/trade_inspector/inspect_trades.py` was not changed.
- `count_valid_jsonl` and `run_archive_intake_validation` remain in their current module.
- No CLI option, default, exit code, warning, error, output order, metadata rule, or file requirement was changed.
- Fixtures exist only inside temporary directories and do not read repository archives or market data.
- IU4, Live-L1, Exchange, Live, inputs, strategies, policies, and gates remain unchanged and locked.
- The foreign untracked file `scripts/build_rcc002_spec_bundle.py` was not read, modified, staged, or included.

## Outcome

The S2 archive-intake seam now has the complete positive and ordered negative contracts required by the seam analysis. A future extraction must preserve these 8/8 focused tests, the 170/170 regression result, and the unchanged façade behavior.
