# P50 TRADING BEHAVIOR REASSESSMENT

Date: 2026-06-06
Device: G15 / AR15
Environment: WSL

## Objective

Reassess Live L1 trading behavior after P44-P49 timing redesign.

## Timing Vote Distribution

- long: 4300808 (100.00%)
- none: 133 (0.00%)
- short: 29 (0.00%)

## Timing Seed Distribution

- C02_rsi_stoch_08: 4300808
- None: 133
- S02_rsi_stoch_08: 29

## Final Intent Distribution

- HOLD: 4299314 (99.96%)
- BUY: 845 (0.02%)
- SELL: 811 (0.02%)

## Intent Reasons

- HOLD_RAW: 4299314
- CONFIRMED_1M_BUY_5M_LONG: 689
- ASYM_SELL_STRONG_5M_LONG_IGNORED: 478
- EXIT_LONG_ON_1M_SELL: 333
- EXIT_SHORT_ON_1M_BUY: 156

## Execution Actions

- NOOP: 4299813
- CLOSE_LONG: 373
- OPEN_LONG: 336
- OPEN_SHORT: 224
- CLOSE_SHORT: 224

## Assessment

- PASS: timing layer is no longer long-only.
- PASS: timing layer can remain neutral.
- PASS: all three timing states observed.

## Result

Status: PASS
