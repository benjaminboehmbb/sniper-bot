# P49 MINI RUNTIME AFTER TIMING SIGNAL WIRING

Date: 2026-06-06
Device: G15 / AR15
Environment: WSL

## Objective

Validate Live L1 runtime after P48 wired runtime feature signals into compute_5m_timing_vote.

## Run Configuration

Command:

python3 live_l1/tools/safe_launch.py --max-ticks 100

Operational profile:

PAPER

## Runtime Result

RUNTIME_RC: 0

## Timing Vote Distribution

- long: 38
- short: 29
- none: 33

## Timing Seed Distribution

- C02_rsi_stoch_08: 38
- S02_rsi_stoch_08: 29
- None: 33

## Final Intent Distribution

- HOLD: 100

## Intent Reason Distribution

- HOLD_RAW: 100

## Execution Action Distribution

- NOOP: 100

## Reconciliation

RESULT: PASS

## Monitoring

RESULT: PASS

Status:

WARN

Reason:

kill_level_active

## Interpretation

P49 confirms that the full timing path now works in runtime:

Feature Snapshot
-> Runtime Signal Wiring
-> Polarity-Aware Timing Scoring
-> Timing Vote
-> Intent Fusion

Unlike P45, timing is no longer structurally forced to none.

Observed timing votes now include:

- long
- short
- none

No trades were generated in this 100-tick window because the 1m raw intent remained HOLD for all ticks.

This is not a timing failure.

The next assessment should focus on interaction between 1m raw intent, timing confirmation, gate state, and final intent fusion.

## Result

Status: PASS
