# X1 Trade Inspector S3 Path and Diagnosis Characterization Gate Evidence — 2026-08-14

Status: **PASS**

Branch: `codex/x1-trade-inspector-s3-path-diagnosis-characterization-gate-2026-08-14`

Base commit: `04305e739858336f1be128ae4130e3e881744fb8`

## Decision

The S3 pre-extraction characterization gate is complete. No production function, constant, import, or CLI path was changed.

The gate adds the five fixtures required by the seam analysis:

- LONG path and diagnosis;
- SHORT path and diagnosis;
- missing market path;
- zero PnL;
- invalid negative duration.

Each fixture binds the complete deterministic result across quality flags, quality score, trade path, all counterfactual windows, interpretation flags, diagnosis, cause ordering, confidence, evidence, impact, and priority. The score-band, signed-diagnosis, and trade-direction boundaries are also explicit.

This evidence makes a separately approved S3 extraction technically eligible. It does not authorize production extraction by itself.

## Changed file

| File | Role | SHA-256 before commit |
|---|---|---|
| `tests/trade_inspector/test_inspect_trades_characterization.py` | Five S3 fixtures, golden fingerprints, and boundary matrix | `d2a794ddfd80a81cb5fea1e0113deadb8d404863372f1d8196ccbeff29ee8cbe` |

Production façade SHA-256 remained unchanged:

`fd266a102ea621cea7ac055330b28c17c3c4759bd768c9cf84f67b0ad0684e57`

## Scenario fingerprints

Canonical encoding uses sorted-key compact ASCII JSON over the complete S3 snapshot.

| Scenario | SHA-256 | Key bound outcome |
|---|---|---|
| LONG | `de903d536a9874756c6a74bd6325f8e8bfea20ee6157222923efe024a5863aa1` | MFE `0.05`, root cause `early_exit`, priority `HIGH` |
| SHORT | `c9cd9800a4a4de3f2b64daf9c6ec3c7df328308615064c37aff5bc9441a23276` | best price `95.0`, worst price `100.0`, MFE `0.05` |
| Missing path | `c54567d7b491ea7bf5f52d7b3bdb1a6a3c7df8e7d2815cb3efc07746ff7126f1` | path unavailable, every counterfactual unavailable, reliability `60` |
| Zero PnL | `3ca07215b9a292188e019f10617e2c1537f384d049818b857cb7c583a3bb5f72` | `flat_trade`, quality `60/acceptable`, 24h efficiency `0.0` |
| Invalid duration | `12d34e43c7117698ea579014b503e539a8dff6bd07c3095ecaa2d9cc78656987` | ordered flags `negative_duration`, `very_short_trade`; quality `20/bad` |

## Boundary matrix

The gate binds current `score_band` and `signed_diagnosis` behavior at and around every threshold:

| Score | Band | Signed diagnosis |
|---:|---|---:|
| 39 | bad | -1 |
| 40 | weak | 0 |
| 59 | weak | 0 |
| 60 | acceptable | 0 |
| 74 | acceptable | 0 |
| 75 | good | 1 |
| 89 | good | 1 |
| 90 | excellent | 1 |

Directional PnL is explicitly bound as LONG `100 -> 105 = 5`, SHORT `100 -> 95 = 5`, and unknown side `= 0`.

## Focused validation

Command:

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest -v tests.trade_inspector.test_inspect_trades_characterization
```

Result:

```text
Ran 14 tests
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
- All S3 functions and `FUTURE_WINDOWS_MIN` remain in the façade.
- Fixtures use only in-memory synthetic trades and price paths.
- No repository archive, market data, runtime input, label registry, or generated artifact was read or changed.
- No scientific threshold, floating-point expression, list order, field order, score, diagnosis, confidence, or priority behavior was changed.
- IU4, Live-L1, Exchange, Live, inputs, strategies, policies, and gates remain unchanged and locked.
- The foreign untracked file `scripts/build_rcc002_spec_bundle.py` was not read, modified, staged, or included.

## Outcome

The S3 path-and-diagnosis seam now has the long, short, unavailable, flat, and invalid-duration contracts required by the seam analysis. A future extraction must preserve all five fingerprints, the boundary matrix, 14/14 focused tests, 170/170 regression tests, and the unchanged public façade.
