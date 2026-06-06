# P44 POLARITY-AWARE TIMING SCORING IMPLEMENTED

Date: 2026-06-06
Device: G15 / AR15
Environment: WSL

## Objective

Implement polarity-aware scoring for the Live L1 5m timing layer.

## Modified File

live_l1/core/timing_5m.py

## Change

Before:

Seed selection used static seed weights only.

After:

Seed selection uses:

- seed direction
- seed weights
- current signal values
- threshold

## Scoring

Long seed:

score = sum(weight * signal_value)

Short seed:

score = sum(weight * -signal_value)

## Acceptance Rule

A seed is eligible only if:

- direction is long or short
- score > 0
- strength >= threshold

If no seed passes:

TimingVote(direction="none", strength=0.0, seed_id=None)

## Validation

Test file:

tools/test_p44_polarity_aware_timing.py

Cases:

- positive_signals_long
- negative_signals_short
- mixed_signals_none
- missing_signal_none
- below_threshold_none

Expected:

RESULT: PASS

## Result

Status: PASS
