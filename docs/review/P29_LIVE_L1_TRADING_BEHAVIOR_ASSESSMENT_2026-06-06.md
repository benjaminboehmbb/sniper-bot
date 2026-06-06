# P29 LIVE L1 TRADING BEHAVIOR ASSESSMENT

Date: 2026-06-06

## Regime Distribution

- bull: 2220849
- bear: 2079471
- chop: 400

## Gate Distribution

- allow_long=0 allow_short=0: 1809660
- allow_long=1 allow_short=0: 1297396
- allow_long=0 allow_short=1: 1193664

## Intent Distribution

- HOLD: 4299064
- BUY: 845
- SELL: 811

## 5m Vote Distribution

- long: 4300720

## Intent Reasons

- HOLD_RAW: 4299064
- CONFIRMED_1M_BUY_5M_LONG: 689
- ASYM_SELL_STRONG_5M_LONG_IGNORED: 478
- EXIT_LONG_ON_1M_SELL: 333
- EXIT_SHORT_ON_1M_BUY: 156

## Assessment

- WARNING: 5m timing layer appears permanently biased to LONG.
- HOLD ratio: 0.999615
- Gate blocked ratio: 0.420781
- Infrastructure validated in P28.
- Future work should focus on signal quality and trading behavior.

## Result

Status: PASS
