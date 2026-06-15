# V7I ARCHIVE INTAKE PIPELINE - COMPLETED

Date: 2026-06-15
Device: G15 / AR15
Scope: Trade Inspector V7I
Status: Completed and validated on P79A

## Objective

V7I adds archive intake validation for future runtime archives.

The goal is to validate an archive before it is added to the V7 registry or used for multi-archive analysis.

## Implementation

Updated file:

tools/trade_inspector/inspect_trades.py

Added CLI options:

--run-archive-intake
--archive-intake-dir

Added functions:

- count_valid_jsonl(...)
- run_archive_intake_validation(...)

## Validation Checks

V7I checks:

- archive directory exists
- required files exist
- archive_metadata.json exists
- trades_l1.jsonl is valid JSONL
- execution_audit.jsonl is valid JSONL
- trade_count matches metadata
- audit_event_count matches metadata
- metadata status is valid

## Required Files

Required archive files:

- trades_l1.jsonl
- execution_audit.jsonl
- l1_paper.log
- archive_metadata.json

## Optional Files

Optional archive files:

- trade_lifecycle_snapshots.csv
- monitor_status.json
- runtime_control.json
- loss_cluster_state.json
- trades_l1_auto_analysis.csv

Missing optional files create warnings only.

## Validation Archive

Archive:

live_logs/archive/P79A_pre_run_2026-06-10

Temporary metadata file created for validation:

live_logs/archive/P79A_pre_run_2026-06-10/archive_metadata.json

This metadata file is inside live_logs and is not committed.

## Validation Command

python3 tools/trade_inspector/inspect_trades.py \
  --run-archive-intake \
  --archive-intake-dir live_logs/archive/P79A_pre_run_2026-06-10

## Validation Result

PASS

Observed:

- required_files: PASS
- archive_metadata_json: PASS
- archive_id: P79A_pre_run_2026-06-10
- trades_valid_jsonl: 9
- trades_bad_jsonl: 0
- audit_valid_jsonl: 18
- audit_bad_jsonl: 0
- warnings: 3
- ARCHIVE_INTAKE: PASS

Warnings:

- optional file missing: monitor_status.json
- optional file missing: runtime_control.json
- optional file missing: loss_cluster_state.json

These warnings are acceptable for P79A.

## Important Rule

V7I does not automatically modify the archive registry.

It only validates archive readiness.

Registry updates remain a deliberate manual step.

## Next Use

When the Workstation runtime run finishes:

1. archive runtime files
2. create archive_metadata.json
3. run V7I intake validation
4. only if PASS, add archive to V7 registry
5. rerun V7G multi-archive loader
