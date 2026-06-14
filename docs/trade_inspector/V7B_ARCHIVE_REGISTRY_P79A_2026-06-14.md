# V7B ARCHIVE REGISTRY - P79A

Date: 2026-06-14
Device: G15 / AR15
Scope: Trade Inspector V7B
Status: Minimal registry for first archive

## Registered Archives

| archive_id | archive_path | run_label | created_at | source_device | market_data | strategy_profile | include_in_v7 |
|---|---|---|---|---|---|---|---|
| P79A_pre_run_2026-06-10 | live_logs/archive/P79A_pre_run_2026-06-10 | P79A pre run reference archive | 2026-06-10 | G15/AR15 | data/l1_full_run.csv | Live L1 PAPER | yes |

## Notes

This is the first minimal V7 archive registry.

Known archive contents:

- 9 trades
- 18 audit events
- 4,330,970 regime snapshots

Current use:

- framework validation
- V7 structure preparation
- not statistically robust trading analysis

## Validation Result

Archive path exists:

PASS

Required minimum input:

live_logs/archive/P79A_pre_run_2026-06-10/trades_l1.jsonl

Expected result:

Readable JSONL trade file with 9 trades.

