# ARCHIVE METADATA STANDARD

Date: 2026-06-15
Scope: Sniper-Bot / Trade Inspector
Status: Standard definition

## 1. Objective

This document defines the standard metadata format for future runtime archives.

Purpose:

- make archives comparable
- prevent unclear archive naming
- support V7G multi-archive loading
- support later cross-archive analysis
- avoid losing important run context

## 2. Archive Directory Naming

Recommended archive directory format:

live_logs/archive/<RUN_ID>_<short_description>_<YYYY-MM-DD>

Example:

live_logs/archive/P79B_workstation_full_run_2026-06-19

## 3. Required Archive Files

Each archive should contain at minimum:

- trades_l1.jsonl
- execution_audit.jsonl
- l1_paper.log
- archive_metadata.json

Optional but recommended:

- trade_lifecycle_snapshots.csv
- monitor_status.json
- runtime_control.json
- loss_cluster_state.json
- trades_l1_auto_analysis.csv

## 4. Required Metadata File

Each archive must contain:

archive_metadata.json

Required fields:

- archive_id
- archive_path
- created_at
- source_device
- run_type
- strategy_profile
- market_symbol
- market_csv
- seeds_5m_csv
- max_ticks
- tick_offset
- decision_tick_seconds
- start_time_utc
- end_time_utc
- trade_count
- audit_event_count
- status
- notes

## 5. Recommended Metadata Template

{
  "archive_id": "P79B_workstation_full_run_2026-06-19",
  "archive_path": "live_logs/archive/P79B_workstation_full_run_2026-06-19",
  "created_at": "2026-06-19",
  "source_device": "Workstation",
  "run_type": "runtime_validation",
  "strategy_profile": "Live L1 PAPER",
  "market_symbol": "BTCUSDT",
  "market_csv": "data/l1_full_run.csv",
  "seeds_5m_csv": "seeds/5m/btcusdt_5m_timing_core_v2.csv",
  "max_ticks": "",
  "tick_offset": "",
  "decision_tick_seconds": "",
  "start_time_utc": "",
  "end_time_utc": "",
  "trade_count": "",
  "audit_event_count": "",
  "status": "created",
  "notes": ""
}

## 6. Archive Status Values

Allowed status values:

- created
- validated
- rejected
- archived
- superseded

Meaning:

created:
Archive exists but has not been validated.

validated:
Archive passed minimum validation and may be used for V7.

rejected:
Archive is invalid and must not be used.

archived:
Archive is preserved for history.

superseded:
Archive was replaced by a better or corrected archive.

## 7. Minimum Validation Criteria

Before an archive is added to V7 registry, verify:

- archive directory exists
- trades_l1.jsonl exists
- execution_audit.jsonl exists
- l1_paper.log exists
- archive_metadata.json exists
- trades_l1.jsonl is valid JSONL
- execution_audit.jsonl is valid JSONL
- trade_count in metadata matches actual count
- archive_id is unique

## 8. V7 Registry Use

Only archives with:

status = validated

should be included in V7 multi-archive analysis.

The archive_id from archive_metadata.json must match the registry archive_id.

## 9. Interpretation Rule

Archive metadata does not make results statistically valid.

Statistical interpretation still requires:

- at least 2 archives
- at least 30 trades

Until then:

statistical_interpretation_allowed = no

## 10. Current Reference Archive

Current reference archive:

live_logs/archive/P79A_pre_run_2026-06-10

Known contents:

- 9 trades
- 18 audit events
- 4,330,970 regime snapshots

Current role:

framework validation only

## 11. Next Use

When the current Workstation runtime run finishes, create a new archive directory and add archive_metadata.json before adding it to the V7 registry.
