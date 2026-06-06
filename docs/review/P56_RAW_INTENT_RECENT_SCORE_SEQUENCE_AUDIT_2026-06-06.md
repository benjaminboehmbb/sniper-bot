# P56 RAW INTENT RECENT-SCORE SEQUENCE AUDIT

Date: 2026-06-06
Device: G15 / AR15
Environment: WSL

## Objective

Audit whether post-fix runtime scores form the repeated score sequences required by raw 1m intent logic.

## Segment

live_logs/review_segments/p49_after_timing_signal_wiring_segment.log

## Counts

scores: 100

intents: 100

timing_votes: 100

## Score Distribution

- -4: 1
- -3: 3
- -1: 25
- 0: 30
- 1: 14
- 2: 11
- 3: 10
- 4: 6

## Raw Intent Distribution

- HOLD: 100

## Timing Distribution

- long: 38
- none: 33
- short: 29

## Sequence Checks

- last2_ge_3: 11
- last3_ge_3: 7
- last2_ge_4: 4
- last3_ge_4: 2
- last2_le_-3: 3
- last3_le_-3: 2
- last2_le_-4: 0
- last3_le_-4: 0

## Example Sequence Hits

- tick_index=2 check=last2_ge_3 last3=[3, 3] last2=[3, 3]
- tick_index=24 check=last2_le_-3 last3=[-1, -4, -3] last2=[-4, -3]
- tick_index=25 check=last2_le_-3 last3=[-4, -3, -3] last2=[-3, -3]
- tick_index=25 check=last3_le_-3 last3=[-4, -3, -3] last2=[-3, -3]
- tick_index=26 check=last2_le_-3 last3=[-3, -3, -3] last2=[-3, -3]
- tick_index=26 check=last3_le_-3 last3=[-3, -3, -3] last2=[-3, -3]
- tick_index=43 check=last2_ge_3 last3=[2, 4, 4] last2=[4, 4]
- tick_index=43 check=last2_ge_4 last3=[2, 4, 4] last2=[4, 4]
- tick_index=53 check=last2_ge_3 last3=[2, 3, 3] last2=[3, 3]
- tick_index=85 check=last2_ge_3 last3=[0, 3, 4] last2=[3, 4]
- tick_index=86 check=last2_ge_3 last3=[3, 4, 4] last2=[4, 4]
- tick_index=86 check=last3_ge_3 last3=[3, 4, 4] last2=[4, 4]
- tick_index=86 check=last2_ge_4 last3=[3, 4, 4] last2=[4, 4]
- tick_index=87 check=last2_ge_3 last3=[4, 4, 4] last2=[4, 4]
- tick_index=87 check=last3_ge_3 last3=[4, 4, 4] last2=[4, 4]
- tick_index=87 check=last2_ge_4 last3=[4, 4, 4] last2=[4, 4]
- tick_index=87 check=last3_ge_4 last3=[4, 4, 4] last2=[4, 4]
- tick_index=88 check=last2_ge_3 last3=[4, 4, 4] last2=[4, 4]
- tick_index=88 check=last3_ge_3 last3=[4, 4, 4] last2=[4, 4]
- tick_index=88 check=last2_ge_4 last3=[4, 4, 4] last2=[4, 4]

## Interpretation

If strong single scores exist but repeated sequence checks are zero, the raw intent logic is intentionally filtering isolated spikes.

## Result

Status: PASS
