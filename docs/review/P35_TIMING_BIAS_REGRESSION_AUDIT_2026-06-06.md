# P35 TIMING BIAS REGRESSION AUDIT

Date: 2026-06-06
Device: G15 / AR15
Environment: WSL

## Objective

Validate that strict 5m timing direction handling removed the implicit long fallback.

## Test Inputs

v1_seed: seeds/5m/btcusdt_5m_long_timing_core_v1.csv

v2_seed: seeds/5m/btcusdt_5m_timing_core_v2.csv

## Results

v1_direction: none

v1_strength: 0.0

v1_seed_id: None

v1_expected: none

v1_result: PASS

v2_direction: long

v2_strength: 1.0

v2_seed_id: C02_rsi_stoch_08

v2_expected: long

v2_result: PASS

## Interpretation

The old v1 seed file no longer becomes long implicitly.

The new v2 seed file with explicit direction=long still works.

## Result

Status: PASS
