# P59 EXTENDED SEGMENT VALIDATION

Date: 2026-06-06
Device: G15 / AR15
Environment: WSL

## Objective

Run a longer controlled Live L1 runtime segment after timing and signal-wiring fixes.

## Run Configuration

Command:

python3 live_l1/tools/safe_launch.py --max-ticks 5000

Operational profile:

PAPER

## Segment

live_logs/review_segments/p59_extended_segment.log

## Runtime Result

RUNTIME_RC: 0

## Final Intent Distribution

- HOLD: 4995
- BUY: 3
- SELL: 2

## 5m Timing Vote Distribution

- short: 1978
- none: 1782
- long: 1240

## Execution Action Distribution

- NOOP: 4994
- OPEN_LONG: 3
- CLOSE_LONG: 3

## Reconciliation

RESULT: PASS

## Monitoring

RESULT: PASS

Status:

WARN

Reason:

kill_level_active

## Entry Gate Condition Alignment

Rows:

5000

Condition counts:

- sell_core_ok: 104
- buy_score_ok: 116
- buy_core_ok: 525
- sell_score_ok: 59
- buy_full_entry_condition: 4
- sell_full_entry_condition: 0

## Interpretation

P59 confirms that the post-fix runtime can now produce real BUY and SELL raw/final intents over a longer segment.

The runtime executed 3 long entries and 3 long closes.

No short entries were executed because full short entry conditions did not align in this segment.

The timing layer is no longer structurally biased and produced long, short, and none states.

The system remained consistent after the extended run.

## Result

Status: PASS
