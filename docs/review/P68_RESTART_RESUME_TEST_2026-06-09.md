# P68 RESTART / RESUME TEST

Date: 2026-06-09

## Objective

Validate that Live-L1 can continue from an existing runtime state instead of restarting from the beginning.

## Run A

Configuration:

- Device: Workstation
- Environment: WSL
- Market CSV: data/l1_full_run.csv
- Seeds: seeds/5m/btcusdt_5m_timing_core_v2.csv
- L1_STARTUP_RECOVERY=1
- L1_STARTUP_RECONCILIATION_GATE=1
- L1_DECISION_TICK_SECONDS=0
- Max Ticks: 250000

Result:

- RUNTIME_RC: 0
- Reconciliation: PASS
- Closed trades: 45
- Final position: FLAT
- Last snapshot: CSV-00250000
- Last tick id: 250000
- Last timestamp: 2018-02-23 15:21 UTC

## Run B

Restarted without deleting runtime logs/state.

Configuration:

- Max Ticks: 50000
- Same market CSV
- Same seeds
- Same recovery/reconciliation flags
- Same fast runtime mode

Result:

- Reconciliation: PASS
- Closed trades: 54
- Final position: FLAT
- Last snapshot: CSV-00300000
- Last tick id: 50000
- Last timestamp: 2018-03-30 08:41 UTC

## Key Finding

Run B continued from the previous market snapshot.

Expected resume continuity:

250000 + 50000 = 300000

Observed:

CSV-00300000

This confirms that the runtime did not restart from CSV-00000001.

## Conclusion

P68 PASS

Validated:

- Restart behavior
- Resume from previous snapshot
- State continuity
- Trade continuity
- Audit continuity
- Reconciliation after restart
- No overwrite of previous trade history
- Final state remained FLAT

Live-L1 restart/resume behavior is valid for the tested scenario.
