# P32 5M TIMING SEED V2 CREATION

Date: 2026-06-06
Device: G15 / AR15
Environment: WSL

## Objective

Create a v2 5m timing seed file with explicit direction column.

## Source

seeds/5m/btcusdt_5m_long_timing_core_v1.csv

## Output

seeds/5m/btcusdt_5m_timing_core_v2.csv

## Schema

- seed_id
- direction
- comb_json

## Direction Assignment

All legacy v1 seeds are assigned direction=long.

Reason:

The source file is explicitly named as a long timing core seed file.

## Rows Created

2

## Limitation

This v2 seed file does not yet add short seeds.

It only removes the implicit long default by making long direction explicit.

## Result

Status: PASS
