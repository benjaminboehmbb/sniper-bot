# P28D SIGNAL QUALITY REVIEW

Date: 2026-06-06
Device: G15 / AR15
Environment: WSL

## Objective

Review Live L1 signal quality from live_logs/l1_paper.log using streaming analysis.

## Event Counts

- clock_tick: 4300200
- market_snapshot: 4300200
- regime_snapshot: 4300200
- intent_fused: 4300200
- execution: 4300200
- state_update: 4300200
- state_persisted: 4300200
- system_stop: 18
- recovery_checked: 16
- system_start: 16

## Gate Counts allow_long/allow_short

- ('0', '0'): 1809486
- ('1', '0'): 1297050
- ('0', '1'): 1193664

## Regime Labels

- bull: 2220492
- bear: 2079381
- chop: 327

## Risk Labels

- bad_atr: 2459783
- good_atr: 1840319
- neutral_atr: 98

## Entry Scores

- 0: 2118263
- -1: 619439
- 1: 583349
- -2: 277594
- 2: 258392
- -3: 159264
- 3: 156011
- -4: 65192
- 4: 62696

## Raw 1m Intents

- HOLD: 4298546
- BUY: 844
- SELL: 810

## Final Intents

- HOLD: 4298546
- BUY: 844
- SELL: 810

## Intent Reason Codes

- HOLD_RAW: 4298546
- CONFIRMED_1M_BUY_5M_LONG: 688
- ASYM_SELL_STRONG_5M_LONG_IGNORED: 478
- EXIT_LONG_ON_1M_SELL: 332
- EXIT_SHORT_ON_1M_BUY: 156

## 5m Vote Directions

- long: 4300200

## Execution Actions

- NOOP: 4299045
- CLOSE_LONG: 372
- OPEN_LONG: 335
- OPEN_SHORT: 224
- CLOSE_SHORT: 224

## Execution Reasons

- HOLD_NO_EXECUTION: 4298448
- LOSS_CLUSTER_GATE_BLOCKED_ENTRY: 595
- BUY_FROM_FLAT: 335
- SELL_CLOSES_LONG: 324
- SELL_FROM_FLAT: 224
- BUY_CLOSES_SHORT: 154
- SHORT_TIME_STOP_HIT: 63
- LONG_TIME_STOP_HIT: 39
- SL_LONG_HIT: 8
- SL_SHORT_HIT: 7
- BUY_ALREADY_LONG: 2
- TP_LONG_HIT: 1

## Result

Status: PASS
