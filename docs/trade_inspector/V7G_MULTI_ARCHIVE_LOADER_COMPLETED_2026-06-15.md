# V7G MULTI-ARCHIVE LOADER - COMPLETED

Date: 2026-06-15
Device: G15 / AR15
Scope: Trade Inspector V7G
Status: Completed and validated on P79A

## Objective

V7G adds the first real multi-archive loader infrastructure.

The goal is to load registered archives from a markdown archive registry and merge them into a global trade dataset.

This bridges the gap between single-archive exports and future true cross-archive analysis.

## Implementation

Updated file:

tools/trade_inspector/inspect_trades.py

Added CLI options:

--export-multi-archive-loader-dir
--archive-registry-md

Added functions:

- load_archive_registry_md(...)
- load_rows_for_archive(...)
- export_multi_archive_loader(...)

## Registry Input

Current registry:

docs/trade_inspector/V7B_ARCHIVE_REGISTRY_P79A_2026-06-14.md

Current registered archive:

P79A_pre_run_2026-06-10

## Validation Command

python3 tools/trade_inspector/inspect_trades.py \
  --market-csv data/l1_full_run.csv \
  --export-multi-archive-loader-dir outputs/trade_inspector/v7g/P79A_2026-06-14 \
  --archive-registry-md docs/trade_inspector/V7B_ARCHIVE_REGISTRY_P79A_2026-06-14.md

## Validation Result

PASS

Observed result:

- archives_registered: 1
- archives_loaded: 1
- trade_count: 9
- errors: 0

## Output Files

Generated output files:

- multi_archive_global_trades_v7g.csv
- multi_archive_registry_loaded_v7g.csv
- multi_archive_loader_errors_v7g.csv
- multi_archive_loader_v7g_manifest.csv
- v7g_multi_archive_loader_summary.md

## Important Validation Details

The global trades output includes:

- archive_id
- archive_path
- local_trade_id
- global_trade_id
- v7g_archive_row_index

This confirms that archive-aware trade loading works.

## Interpretation Rule

Current data base:

- 1 archive
- 9 trades

Therefore:

statistical_interpretation_allowed = no

V7G currently validates loader infrastructure only.

## Future Use

When new Workstation archives become available, they should be added to the markdown archive registry.

Then V7G can load all included archives into one global trade dataset.

After that, V7C-V7F can be rerun against the expanded multi-archive dataset.

## Minimum Recommended Threshold

For meaningful cross-archive interpretation:

- at least 2 archives
- at least 30 trades

## Current Status

V7G completes the first cross-archive preparation layer.

The Trade Inspector now supports:

- single-archive inspection
- ML dataset generation
- leakage audit
- feature importance
- feature stability
- signal discovery
- reliability classification
- global trade export
- cross-archive root cause infrastructure
- cross-archive feature importance infrastructure
- cross-archive signal discovery infrastructure
- multi-archive loading infrastructure
