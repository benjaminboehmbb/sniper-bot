# X1 Trade Inspector S5R Main/CLI Characterization Gate Evidence — 2026-08-15

Status: **PASS WITH OBSERVED DEFECT**

Branch: `codex/x1-trade-inspector-s5r-main-cli-characterization-gate-2026-08-15`

Base commit: `272abaa9cb542db98a905f752ac82cfa3ea1d82e`

## Scope

This gate freezes the remaining `main`/CLI orchestration in `tools/trade_inspector/inspect_trades.py` before any further structural extraction.

The gate binds all parser defaults, early-route precedence, common input and labeling order, label-registry update placement, trade-report precedence, the complete ordered reporting/export delegation chain, cross-archive registry behavior, aggregated cross-archive failure behavior, return codes, stderr boundaries, and the no-selection output.

Only synthetic in-memory fixtures and patched dependency seams are used. No archive, market-data, label, registry, runtime-input, or production file is read or changed.

## Production identity

`tools/trade_inspector/inspect_trades.py` remained byte-identical throughout the gate.

SHA-256 before and after:

`d19622fa4f9c6d8f3f272708bdb03348f3e13dce72b9bbeb23a7b54227bf137e`

| Binding | Lines | AST SHA-256 | Source-segment SHA-256 |
|---|---:|---|---|
| `main` | 199 | `1c72e19eba5ac2fe4c7dd6395e154b2c11239a57f56a261c506f0c01fc2ef1ce` | `0f2cf6fe1a2102f1f0e0d0e53e5b6edff5049951963ef4eaebe136474273b287` |

Prepared characterization-test SHA-256:

`4f3e84fed8da63d02c10f638f3ff77c412dfc511fded8337be676a29012fcc8a`

## Parser and early-route contracts

The gate binds the complete 26-field parsed namespace, including all path defaults, empty export selections, Boolean defaults, default archive ID, and default registry path.

Early routing is fixed as:

1. `--run-regression-tests` delegates immediately and returns the delegate's exit code;
2. `--run-archive-intake` is considered only when regression validation was not selected;
3. missing `--archive-intake-dir` raises exactly `--archive-intake-dir is required with --run-archive-intake`;
4. neither early route may load the normal archive inputs.

## Common loading and ordered route chain

For non-early routes, the gate binds this exact common order:

1. trades JSONL;
2. execution-audit JSONL;
3. key/value log;
4. regime index;
5. market rows;
6. human-label list;
7. label registry;
8. label assignment;
9. optional label-registry persistence;
10. analysis-row construction.

The trade-index path then binds entry/exit lookup and the complete reporting argument tuple. When all representative lower-priority selections are also present, only the trade report executes.

After the trade-index route, the complete delegated priority chain is:

1. summary;
2. aggregate intelligence;
3. raw ML CSV;
4. aggregate CSVs;
5. ML dataset;
6. feature preparation;
7. leakage audit;
8. feature importance;
9. feature stability;
10. predictive-signal discovery;
11. global-trade database;
12. cross-archive root cause;
13. cross-archive feature importance;
14. cross-archive signal discovery;
15. multi-archive loader.

Every priority case is executed with all lower-priority selections simultaneously. The gate asserts that exactly the first eligible delegate runs, with the exact `Path`, row, and archive-ID arguments, and that every lower delegate remains uncalled.

## Cross-archive contracts

Registry rows are eligible only when `include_in_v7`, after trimming and lowercasing, equals `yes`. Eligible archives retain registry order and are loaded with the shared market, label-list, and label-registry paths.

A successful load concatenates rows in archive order, changes the call-scope archive ID to `MULTI_ARCHIVE_REGISTRY`, and reports both total rows and the unfiltered registry-row count.

All eligible load failures are collected. Two failures are bound to the exact terminal message:

```text
Cross-archive load failed: A: broken A | B: broken B
```

No partial export is permitted after that failure.

## No-selection output

The no-selection path returns zero after common loading and emits the exact 29-line header/example block.

stdout SHA-256:

`639ae94c84d7c8157a65b6b1de039e545f0a8c4613945d71ed8df5ad3c62b85f`

stderr remains empty.

## Observed archive-intake defect

The characterization exposes a pre-existing CLI/implementation mismatch:

- the CLI requires and parses `--archive-intake-dir`;
- `main` passes the parsed namespace unchanged to `run_archive_intake_validation`;
- `run_archive_intake_validation` reads `args.archive_dir`, not `args.archive_intake_dir`;
- therefore the requested intake directory is currently ignored and the default normal archive path remains the effective validation target.

The gate records this behavior so it cannot be changed accidentally. It is **not** approved as desired compatibility behavior and must be repaired explicitly, with fail-closed tests, before `main` is extracted or minimized.

## Validation

Focused characterization:

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest -q tests.trade_inspector.test_inspect_trades_characterization

Ran 88 tests
OK
```

Full regression:

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -s tests/regression -p 'test_*.py'

Ran 170 tests
OK
```

Direct-script parser path:

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python tools/trade_inspector/inspect_trades.py --help

exit 0
```

`git diff --check` passed.

## Safety and next step

Only characterization tests and this evidence document changed. IU4 ENFORCED, Live-L1, Exchange, and Live remain locked. No source data or runtime input was changed.

After integrating this gate into `main`, the next development step is the S5R-A archive-intake argument repair. It must make the explicitly supplied `--archive-intake-dir` the validation target, preserve early-route precedence and delegate exit codes, add direct target-identity tests, and remain fail-closed. Only after that repair is integrated may the remaining CLI orchestration be structurally extracted.
