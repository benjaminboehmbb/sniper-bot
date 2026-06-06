# P41 ISOLATED TIMING SHORT-SEED TEST

Date: 2026-06-06
Device: G15 / AR15
Environment: WSL

## Objective

Validate that the v2 5m timing seed file can emit both long and short votes in isolated timing tests.

## Seed File

seeds/5m/btcusdt_5m_timing_core_v2.csv

## Test Cases

### positive_signals

direction: long

strength: 1.0

seed_id: C02_rsi_stoch_08

### negative_signals

direction: long

strength: 1.0

seed_id: C02_rsi_stoch_08

### mixed_signals

direction: long

strength: 1.0

seed_id: C02_rsi_stoch_08

## Failures

- negative_signals: expected short, got long

## Result

Status: FAIL
