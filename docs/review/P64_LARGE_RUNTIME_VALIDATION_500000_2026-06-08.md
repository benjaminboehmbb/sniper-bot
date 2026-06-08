# P64 LARGE RUNTIME VALIDATION (500000 TICKS)

Date: 2026-06-08

## Runtime Configuration

- Device: Workstation
- Environment: WSL
- Market CSV: data/l1_full_run.csv
- Seeds: seeds/5m/btcusdt_5m_timing_core_v2.csv
- L1_STARTUP_RECOVERY=1
- L1_STARTUP_RECONCILIATION_GATE=1
- L1_DECISION_TICK_SECONDS=0
- Max Ticks: 500000

## Results

Execution:

- OPEN_LONG: 39
- CLOSE_LONG: 39
- OPEN_SHORT: 23
- CLOSE_SHORT: 23

Trades:

- Closed Trades: 62

Reconciliation:

- audit_json_valid: PASS
- audit_vs_s2_position: PASS
- audit_vs_trades: PASS
- trade_time_order: PASS
- loss_cluster_state: PASS

Final State:

- Position: FLAT

Runtime:

- RUNTIME_RC: 0
- Exit Reason: max_ticks_reached

## Conclusion

P64 PASS

Validated:

- Long execution path
- Short execution path
- Runtime stability
- Reconciliation
- State persistence
- Fast runtime mode

Live L1 remained stable over 500000 ticks.
