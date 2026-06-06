# P40 CREATE TIMING V2 SHORT SEEDS

Date: 2026-06-06
Device: G15 / AR15
Environment: WSL

## Objective

Add explicit short seeds to the v2 5m timing seed file.

## Modified File

seeds/5m/btcusdt_5m_timing_core_v2.csv

## Schema

- seed_id
- direction
- comb_json

## Added Short Seeds

- S01_rsi_stoch_06
- S02_rsi_stoch_08

## Final Rows

4

## Important Limitation

This step only adds structural short seed support.

It does not prove profitability or quality of short timing behavior.

## Required Next Step

P41 isolated timing short-seed test.

## Result

Status: PASS
