# P37 RUNTIME MIGRATION TO TIMING SEED V2

Date: 2026-06-06
Device: G15 / AR15
Environment: WSL

## Objective

Migrate the Live L1 runtime default 5m timing seed file from v1 to v2.

## Modified File

live_l1/core/loop.py

## Change

Old default:

seeds/5m/btcusdt_5m_long_timing_core_v1.csv

New default:

seeds/5m/btcusdt_5m_timing_core_v2.csv

## Scope

Only the default runtime seed path was changed.

No signal logic changed.

No execution logic changed.

No strategy rules changed.

No short seeds added.

## Reason

P30 found that the old v1 seed path had no explicit direction column and relied on implicit long fallback.

P32 created an explicit-direction v2 seed file.

P34/P35 removed and validated the removal of implicit long fallback.

P37 connects runtime default configuration to the explicit-direction v2 seed file.

## Validation

Performed:

- py_compile live_l1/core/loop.py
- grep verification of seed path
- P35 timing bias regression audit

Expected:

- v1 seed resolves to none
- v2 seed resolves to long
- runtime default path points to v2

## Result

Status: PASS
