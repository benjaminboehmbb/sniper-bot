# P43 POLARITY-AWARE TIMING MODEL DESIGN

Date: 2026-06-06
Device: G15 / AR15
Environment: WSL

## Objective

Design a polarity-aware 5m timing model before changing timing_5m.py scoring logic.

No runtime code is changed in P43.

## Background

P41 showed that the v2 seed file with explicit short seeds still produced long votes for negative test signals.

P42 identified the root cause:

- _seed_score() only sums seed weights
- _seed_score() does not use current signal values
- _pick_best_seed() chooses the largest absolute static seed score
- signal polarity does not affect seed selection

Therefore the current 5m timing layer is not truly signal-driven.

## Design Goal

The 5m timing layer should select long, short, or none based on:

- seed direction
- seed weights
- current signal values
- threshold

## Inputs

The model should use signal keyword arguments passed into compute_5m_timing_vote.

Example:

- rsi_signal
- stoch_signal
- macd_signal
- mfi_signal
- ma200_signal

Only signals present in the seed comb_json are scored.

## Seed Format

Required columns:

- seed_id
- direction
- comb_json

Example:

seed_id,direction,comb_json
C02_rsi_stoch_08,long,"{'rsi': 0.8, 'stoch': 0.8}"
S02_rsi_stoch_08,short,"{'rsi': 0.8, 'stoch': 0.8}"

## Signal Naming Rule

For a seed key:

rsi

the runtime should look for:

rsi_signal

in kwargs.

For:

stoch

the runtime should look for:

stoch_signal

## Polarity Scoring

For long seeds:

score = sum(weight * signal_value)

For short seeds:

score = sum(weight * (-signal_value))

Rationale:

- positive signal values should support long seeds
- negative signal values should support short seeds

## Example

Signals:

rsi_signal = 1
stoch_signal = 1

Long seed:

0.8 * 1 + 0.8 * 1 = 1.6

Short seed:

0.8 * -1 + 0.8 * -1 = -1.6

Result:

long wins.

Signals:

rsi_signal = -1
stoch_signal = -1

Long seed:

0.8 * -1 + 0.8 * -1 = -1.6

Short seed:

0.8 * 1 + 0.8 * 1 = 1.6

Result:

short wins.

## Strength

strength should be derived from absolute positive support.

Recommended:

strength = min(abs(score), 1.0)

but only after directional acceptance.

## Direction Acceptance

A seed is valid only if:

- direction is long or short
- score is positive after direction-aware transformation
- strength >= threshold

If no seed passes:

return TimingVote(direction="none", strength=0.0, seed_id=None)

## Threshold Rule

Use the existing thresh parameter.

If thresh is None:

default to 0.6

A seed passes only if:

strength >= thresh

## Tie-Breaking

Tie-breaking must be deterministic.

Recommended order:

1. higher strength
2. higher raw score
3. lexicographically smaller seed_id

## None Behavior

Return none when:

- no seeds exist
- no seed has valid direction
- no seed reaches threshold
- relevant signal values are missing
- signal polarity conflicts with all seeds

## Backward Compatibility

Legacy v1 seeds without direction already resolve to none after P34/P35.

No additional legacy fallback should be added.

## Risk

This changes timing behavior materially.

Expected effects:

- long votes may decrease
- short votes may appear
- none votes may appear
- trade frequency may change
- performance metrics may change

## Validation Plan

P44:

Implement polarity-aware timing scoring.

P45:

Run isolated tests:

- positive_signals -> long
- negative_signals -> short
- mixed_signals -> none or deterministic winner
- missing_signals -> none
- below_threshold -> none

P46:

Mini runtime validation.

P47:

Trading behavior reassessment.

No long run before P46/P47.

## Decision

Proceed to implementation only with isolated tests.

## P43 Result

Polarity-aware timing model designed.

Status:

PASS
