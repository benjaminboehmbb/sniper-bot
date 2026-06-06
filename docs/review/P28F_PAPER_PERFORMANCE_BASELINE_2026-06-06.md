# P28F PAPER PERFORMANCE BASELINE

Date: 2026-06-06
Device: G15 / AR15
Environment: WSL

## Source

Source file: live_logs/l1_paper.log

Method: streaming reconstruction from market_snapshot and execution events.

Note: This is a log-derived baseline, not the official recovery trade ledger.

## Runtime Counts

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

## Signal / Gate Counts

Final intents:

- HOLD: 4298546
- BUY: 844
- SELL: 810

Gate counts:

- allow_long=0 allow_short=0: 1809486
- allow_long=1 allow_short=0: 1297050
- allow_long=0 allow_short=1: 1193664

## Execution Actions

- NOOP: 4299045
- CLOSE_LONG: 372
- OPEN_LONG: 335
- OPEN_SHORT: 224
- CLOSE_SHORT: 224

## Reconstructed Trade Baseline

closed_trades_reconstructed: 559

long_trades: 335

short_trades: 224

wins: 390

losses: 168

flat_trades: 1

winrate: 0.697674

total_pnl_points: 14021.680000

avg_pnl_points: 25.083506

gross_win_points: 34468.620000

gross_loss_points: 20446.940000

profit_factor_points: 1.685759

avg_duration_ticks: 27.23

bad_closes: 37

repeated_opens: 0

open_position_remaining: FLAT

## Exit Reasons

- SELL_CLOSES_LONG: 324
- BUY_CLOSES_SHORT: 154
- SHORT_TIME_STOP_HIT: 63
- SL_LONG_HIT: 8
- SL_SHORT_HIT: 7
- LONG_TIME_STOP_HIT: 3

## Result

Status: PASS
