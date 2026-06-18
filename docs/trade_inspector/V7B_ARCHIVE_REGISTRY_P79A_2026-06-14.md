# V7B ARCHIVE REGISTRY - P79A

Date: 2026-06-14
Device: G15 / AR15
Scope: Trade Inspector V7B
Status: Minimal registry for first archive

## Registered Archives

| archive_id | archive_path | run_label | created_at | source_device | market_data | strategy_profile | include_in_v7 |
|---|---|---|---|---|---|---|---|
| P79A_completed_2026-06-11 | live_logs/archive/P79A_completed_2026-06-11 | P79A completed workstation runtime archive | 2026-06-11 | workstation | data/l1_full_run.csv | Live L1 PAPER | yes |
| P82A_completed_7d_workstation_2026-06-18 | live_logs/archive/P82A_completed_7d_workstation_2026-06-18 | P82A completed 7-day workstation runtime archive | 2026-06-18 | workstation | data/l1_full_run.csv | Live L1 PAPER | yes |

## Notes

This is the first minimal V7 archive registry.

Known archive contents:

- 231 trades
- 951 audit events
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

Readable JSONL trade file with 231 trades.

