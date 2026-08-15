# X1 Trade Inspector S5R-A Archive-Intake Argument Repair Evidence — 2026-08-15

Status: **PASS**

Branch: `codex/x1-trade-inspector-s5ra-archive-intake-argument-repair-2026-08-15`

Base commit: `6fe5b077276ab2ac401e162ae2d74993c33da7c0`

## Scope

This change repairs the S5R-observed mismatch between the CLI's required `--archive-intake-dir` argument and the archive-intake validator's expected `args.archive_dir` input.

Immediately before delegating to `run_archive_intake_validation`, `main` now binds:

```text
args.archive_dir = args.archive_intake_dir
```

No parser option, route priority, validator implementation, output format, input file, export path, or runtime safety boundary changed.

## Repair contract

The repaired early route retains this exact behavior:

1. regression validation still has higher priority than archive intake;
2. `--run-archive-intake` without `--archive-intake-dir` still raises the exact fail-fast `SystemExit` message;
3. no normal archive input is loaded before delegation;
4. the archive-intake delegate's return code is returned unchanged;
5. both `args.archive_intake_dir` and the validator-facing `args.archive_dir` identify the explicitly requested path.

The mock-bound target is exactly `/fixture/intake` for both fields.

## Real validator target and fail-closed proof

A separate hermetic test invokes `main` through the real archive-intake validator with a unique, nonexistent requested directory.

The result is exit code 1 and stdout contains:

```text
archive_dir: <requested-target>
ERROR: archive directory missing: <requested-target>
ARCHIVE_INTAKE: FAIL
```

The previous default target `live_logs/archive/P79A_pre_run_2026-06-10` is absent from the validator output. stderr remains empty. This proves that the requested directory is the effective validation target and that a missing target remains fail-closed.

## Production and test identity

| File | Before SHA-256 | After SHA-256 |
|---|---|---|
| `tools/trade_inspector/inspect_trades.py` | `d19622fa4f9c6d8f3f272708bdb03348f3e13dce72b9bbeb23a7b54227bf137e` | `aaabf99966cea5fd903a172901d4f0b20546cd7984c85ba5cef5bd00d81c8d90` |
| `tests/trade_inspector/test_inspect_trades_characterization.py` | `4f3e84fed8da63d02c10f638f3ff77c412dfc511fded8337be676a29012fcc8a` | `3d3930c1dfab4a165e4350e93a310d055187653e2ccf647a1a770a954232d071` |

Repaired `main` binding:

| Lines | AST SHA-256 | Source-segment SHA-256 |
|---:|---|---|
| 200 | `e156ee20dc356ac0468e36c341b5616e4b6f4cd49a0bb5cd9cb0052a9eb97deb` | `b24a8238935b6625390a809dbf13ea8d8b8757207b9bcec9c8afa353c794109d` |

The production diff is exactly one inserted assignment. The characterization diff updates the formerly observed target assertion and adds the real-validator fail-closed test.

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

Direct-script parser path:

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python tools/trade_inspector/inspect_trades.py --help

exit 0
```

`git diff --check` passed.

## Safety and next step

Only the one-line argument repair, its target-identity tests, and this evidence document changed. IU4 ENFORCED, Live-L1, Exchange, and Live remain locked. No source data or runtime input was read or changed.

After integrating this repair into `main`, the next development step is the S5R-B structure-only extraction of the now-characterized CLI orchestration. The facade must continue to expose `main`, preserve direct-script execution, and retain all 89 characterization and 170 regression contracts.
