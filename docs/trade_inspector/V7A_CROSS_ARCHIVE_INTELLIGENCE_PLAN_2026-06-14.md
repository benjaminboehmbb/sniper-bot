# V7A CROSS-ARCHIVE INTELLIGENCE PLAN

Date: 2026-06-14
Device: G15 / AR15
Scope: Trade Inspector
Status: Planning only

## 1. Objective

V7A prepares the Trade Inspector for cross-archive analysis.

The goal is to move from single-archive analysis to multi-archive intelligence.

Current limitation:

- only one reference archive
- only 9 trades
- not enough statistical mass

Therefore V7A does not add another statistical layer yet.
V7A defines the structure required for later robust analysis across multiple archived runs.

## 2. Current Source Archive

Current reference archive:

live_logs/archive/P79A_pre_run_2026-06-10

Known contents:

- 9 trades
- 18 audit events
- 4,330,970 regime snapshots

This archive is sufficient for framework validation.
It is not sufficient for robust trading conclusions.

## 3. V7 Target

V7 Cross-Archive Intelligence shall later support:

- global trade database
- archive registry
- cross-archive root cause analysis
- cross-archive trade family analysis
- cross-archive feature importance
- cross-archive feature stability
- cross-archive predictive signal discovery
- ML-ready datasets across multiple runs

## 4. Planned V7 Modules

Target location:

tools/trade_inspector/

Current source of truth:

tools/trade_inspector/inspect_trades.py

Planned logical V7 sections inside inspect_trades.py:

- V7A archive registry validation
- V7B archive loading
- V7C global trade database builder
- V7D cross-archive root cause aggregation
- V7E cross-archive feature importance
- V7F cross-archive signal discovery

No separate module split is planned yet.
The current project structure uses one main Trade Inspector script.

## 5. Planned Config Files

Planned registry path:

config/trade_inspector/archive_registry_2026-06-14.csv

Expected columns:

- archive_id
- archive_path
- run_label
- created_at
- source_device
- market_data
- strategy_profile
- notes
- include_in_v7

Example archive_id:

P79A_pre_run_2026-06-10

## 6. Planned Output Paths

Planned output directory:

outputs/trade_inspector/v7/

Planned output files:

- global_trades_2026-06-14.csv
- global_trade_features_2026-06-14.csv
- cross_archive_root_causes_2026-06-14.csv
- cross_archive_trade_families_2026-06-14.csv
- cross_archive_feature_importance_2026-06-14.csv
- cross_archive_feature_stability_2026-06-14.csv
- cross_archive_signal_discovery_2026-06-14.csv
- v7_cross_archive_summary_2026-06-14.md

## 7. Global Trade ID Strategy

Each trade in V7 must receive a globally unique ID.

Format:

archive_id + "::" + local_trade_id

Example:

P79A_pre_run_2026-06-10::T000001

This prevents collisions when multiple archives contain local trade IDs with the same value.

## 8. Required Archive Inputs

Each archive should ideally contain:

- trades_l1.jsonl
- execution_audit.jsonl
- trade_lifecycle_snapshots.csv or equivalent lifecycle output
- monitor_status.json if available
- relevant runtime metadata if available

Minimum required for V7A validation:

- trades_l1.jsonl

## 9. V7A Rules

V7A must not disturb any running runtime process.

The current Workstation run must not be touched.

No large runtime tests are allowed on the G15.

V7A is documentation and structure preparation only.

## 10. Implementation Order

Recommended order:

1. Create archive registry file
2. Validate registry paths
3. Load trades from listed archives
4. Add global_trade_id
5. Build global_trades dataset
6. Run basic cross-archive summary
7. Only then expand to root cause, feature importance and signal discovery

## 11. Current Decision

Do not build full V7 yet.

Reason:

The current data base is too small.

V7 should be implemented once at least one additional archive exists or once the current Workstation run has produced new validated trade data.

## 12. Current Status

V7A planning completed.

Next recommended technical step:

Create a minimal archive registry file for the existing P79A archive, then validate that the path exists and that trades_l1.jsonl can be read.

