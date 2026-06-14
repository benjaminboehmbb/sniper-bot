# V7C GLOBAL TRADE DATABASE - COMPLETED

Date: 2026-06-14
Device: G15 / AR15
Scope: Trade Inspector V7C
Status: Completed and validated on P79A

## Objective

V7C adds the first infrastructure layer for a future cross-archive Trade Inspector.

The goal is to export a global trade database with archive-aware trade identifiers.

This is infrastructure preparation only.
It is not a statistical cross-archive analysis yet.

## Implementation

Updated file:

tools/trade_inspector/inspect_trades.py

Added CLI options:

--export-global-trades-dir
--archive-id

Added export:

export_global_trade_database(...)

## Test Archive

Archive:

live_logs/archive/P79A_pre_run_2026-06-10

Known contents:

- 9 trades
- 18 audit events
- 4,330,970 regime snapshots

## Validation Command

python3 tools/trade_inspector/inspect_trades.py \
  --archive-dir live_logs/archive/P79A_pre_run_2026-06-10 \
  --market-csv data/l1_full_run.csv \
  --export-global-trades-dir outputs/trade_inspector/v7/P79A_2026-06-14 \
  --archive-id P79A_pre_run_2026-06-10

## Validation Result

PASS

Observed output:

- global_trades: 9
- global_trades_v7c.csv created
- global_trades_v7c_manifest.csv created
- v7c_global_trade_database_summary.md created

## Output Files

outputs/trade_inspector/v7/P79A_2026-06-14/global_trades_v7c.csv

outputs/trade_inspector/v7/P79A_2026-06-14/global_trades_v7c_manifest.csv

outputs/trade_inspector/v7/P79A_2026-06-14/v7c_global_trade_database_summary.md

## Global ID Strategy

Each trade receives:

archive_id
local_trade_id
global_trade_id

Format:

archive_id::local_trade_id

Example:

P79A_pre_run_2026-06-10::T_20170817_040100_LONG_BTCUSDT

## Important Limitation

The current output validates the V7C infrastructure only.

It must not be interpreted as statistically robust trading analysis because the current database contains only:

- 1 archive
- 9 trades

## Next Step

Once more archives exist, V7C can be reused to generate a larger global trade database.

Only after that should V7D, V7E and V7F be used for:

- cross-archive root cause analysis
- cross-archive feature importance
- cross-archive signal discovery
