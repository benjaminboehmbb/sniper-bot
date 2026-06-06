# P38 TIMING V2 MINI RUNTIME VALIDATION

Date: 2026-06-06
Device: G15 / AR15
Environment: WSL

## Objective

Validate that Live L1 runtime starts correctly after migrating the default 5m timing seed path to v2.

## Run Configuration

Command:

python3 live_l1/tools/safe_launch.py --max-ticks 50

Operational profile:

PAPER

## Runtime Seed Path

Confirmed in system_start log:

seeds_5m_csv=seeds/5m/btcusdt_5m_timing_core_v2.csv

## Segment Result

5m vote distribution:

- long: 50

Execution actions:

- NOOP: 50

## Interpretation

The runtime successfully uses the v2 timing seed file.

The v2 file currently contains only explicit long seeds, therefore long-only votes are expected.

No trading behavior change is expected yet beyond removing hidden implicit long fallback risk.

## Reconciliation

RESULT: PASS

## Monitoring

RESULT: PASS

Status:

WARN

Reason:

kill_level_active

## Result

Status: PASS
