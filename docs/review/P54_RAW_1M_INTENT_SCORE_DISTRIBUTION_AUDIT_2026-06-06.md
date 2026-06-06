# P54 RAW 1M INTENT SCORE DISTRIBUTION AUDIT

Date: 2026-06-06
Device: G15 / AR15
Environment: WSL

## Objective

Quantify raw 1m intent and related score distributions on post-fix runtime segments.

## Audited Segments

- live_logs/review_segments/p49_after_timing_signal_wiring_segment.log

## Runtime Rows

intent_rows: 100

## Raw 1m Intent Distribution

- HOLD: 100

## 5m Timing Distribution

- long: 38
- none: 33
- short: 29

## Reason Code Distribution

- HOLD_RAW: 100

## Entry Score Distribution

- -4: 1
- -3: 3
- -1: 25
- 0: 30
- 1: 14
- 2: 11
- 3: 10
- 4: 6

## Regime Distribution

- bear: 100

## Risk Distribution

- bad_atr: 66
- good_atr: 34

## Interpretation

This audit separates raw 1m intent behavior from 5m timing behavior.

If raw 1m intent remains HOLD while timing varies, the current bottleneck is raw 1m intent generation.

## Result

Status: PASS
