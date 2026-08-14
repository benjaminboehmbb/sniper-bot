# X1 Trade Inspector S4 Regime, Identity, and Row Characterization Gate Evidence — 2026-08-14

Status: **PASS**

Branch: `codex/x1-trade-inspector-s4-regime-identity-row-characterization-gate-2026-08-14`

Base commit: `b3871aff3c5191b211380160d5a1f25e26dbd411`

## Decision

The S4 pre-extraction characterization gate is complete. No production function, constant, import, registry path, or CLI path was changed.

The gate binds the current behavior of:

- regime-index construction, including empty-key rejection and last-row-wins duplicate handling;
- entry/exit regime-feature extraction for aligned LONG, aligned SHORT, counter-regime, regime-flip, risk, and missing-context cases;
- compact UTC time, chart time, fallback time, and trade-identity formatting;
- the complete six-level trade-family precedence order;
- the complete 127-field ML row, including exact insertion order;
- multi-trade input order, one-based indices, identity, label lookup, audit selection, and per-row schema equality.

Label-registry I/O and allocation remain deliberately outside the S4 extraction seam: `load_label_registry`, `save_label_registry`, and `assign_human_labels` were neither changed nor newly characterized by this gate.

This evidence makes a separately approved S4 extraction technically eligible. It does not authorize production extraction by itself.

## Changed file

| File | Role | SHA-256 before commit |
|---|---|---|
| `tests/trade_inspector/test_inspect_trades_characterization.py` | S4 synthetic fixtures, precedence matrix, schema-order contract, and golden fingerprints | `dc701947de8926a84f6b16443fb28bc661c4c0df1c57aa18b46ba1546b00f993` |

Production façade SHA-256 remained unchanged:

`ba4e48cd487fd3a37a20dbf3b600b5a9699d744317ac38bd656338fd5817ad37`

## Golden fingerprints

Canonical semantic encoding uses sorted-key compact ASCII JSON. Field-order and ordered-row fingerprints use compact ASCII JSON without key sorting.

| Contract | SHA-256 | Bound scope |
|---|---|---|
| Existing representative row semantics | `54fc961343d463d4e55d6489c70ec9ffcf3892acc9155b45b95e5f9408a2ce24` | All 127 field values |
| Exact field insertion order | `76c7ca3b7c1b1e5652bc5ece60648fb23f2eb09e32553bef63ddbb22f385e795` | Ordered list of all 127 field names |
| Ordered representative row | `a79a164bbbeb5a1584e34aadc3c0c04f451445c94e9eec2e9b0e171aadadb60b` | Field order and values together |
| Regime matrix | `d37f242b767fa32d6ffdbbee148dfd820805f07bdbf0e310090f068659db7b4a` | Four complete 17-field regime outcomes |
| Trade-family matrix | `18a1d2ccbd54647b09077dace28af5c7795eb34c90ff64660901962e17c7acab` | Family string and precedence group for six outcomes |
| Multi-row identity summary | `b8f5f7bd37b5be8f6a2cc3ca3eccec2b932da183f07143959bfc6133dc41fd45` | Two ordered rows, IDs, labels, audits, regimes, families, schema, and row semantics |

## Family precedence matrix

The gate fixes the current first-match precedence:

1. `exit_risk_trap`;
2. `exit_after_regime_flip`;
3. `aligned_good_risk`;
4. `chop_context`;
5. `counter_regime`;
6. `general`.

The empty-input fallback family remains:

`unknown_side_unknown_regime_unknown_risk_unknown_cause_neutral_regime`

## Time and identity boundaries

- `2026-01-01T01:00:00+01:00` normalizes to compact `20260101_000000` and chart `2026-01-01 00:00:00 UTC`.
- Naive `2026-01-01T00:00:00` retains the same clock value under the current formatter.
- Invalid and missing timestamps produce `UNKNOWN_TIME` for compact identity and an empty chart value.
- Missing side and symbol produce `T_UNKNOWN_TIME_UNKNOWN_SIDE_BTCUSDT`.

## Focused validation

Command:

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest -v tests.trade_inspector.test_inspect_trades_characterization
```

Result:

```text
Ran 18 tests
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
- S4 production functions remain in the current façade.
- Fixtures use only in-memory synthetic trades, audits, regimes, and price paths.
- No repository archive, runtime input, market-data file, label registry, or generated artifact was read or changed.
- No field, field order, timestamp rule, ID rule, classification precedence, score, diagnosis, or row-assembly behavior was changed.
- Label-registry loading, saving, and assignment remain outside the prospective extraction boundary.
- IU4, Live-L1, Exchange, Live, inputs, strategies, policies, and gates remain unchanged and locked.
- The foreign untracked file `scripts/build_rcc002_spec_bundle.py` was not read, modified, staged, or included.

## Outcome

The S4 regime/identity/row seam now has a deterministic contract for regime mapping, timestamp and trade identity, family precedence, the exact 127-field schema order, and multi-row assembly. A future extraction must preserve all golden fingerprints, 18/18 focused tests, 170/170 regression tests, and the unchanged public façade.
