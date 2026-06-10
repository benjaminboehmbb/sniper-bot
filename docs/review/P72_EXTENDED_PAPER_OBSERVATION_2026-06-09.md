# P72 EXTENDED PAPER OBSERVATION

Date: 2026-06-09

## Objective

Start controlled Paper Trading observation after successful infrastructure validation P62-P71.

This phase validates runtime behavior under extended PAPER profile operation.

## Environment

Device:

Workstation

Environment:

WSL Ubuntu

Repository:

/mnt/c/Users/workstation/Desktop/sniper-bot

## Pre-Run Cleanup

Before the run, existing runtime artifacts were inspected explicitly.

Files found in live_logs:

- execution_audit.jsonl
- l1_paper.log
- passive_shadow_close_accounting.csv
- passive_shadow_entry_multipliers.csv
- passive_shadow_risk_snapshots.csv
- trade_lifecycle_snapshots.csv
- trades_l1.jsonl

Files found in live_state:

- loss_cluster_state.json
- s2_position.jsonl
- s4_risk.jsonl

These files were archived to:

- live_logs/archive/P72_pre_run_2026-06-09/
- live_state/archive/P72_pre_run_2026-06-09/

After cleanup, no active files remained in live_logs or live_state.

## Run 1 Configuration

Profile:

PAPER

Flags:

- L1_REQUIRE_WSL=1
- L1_PROFILE=PAPER
- L1_STARTUP_RECOVERY=1
- L1_STARTUP_RECONCILIATION_GATE=1
- L1_DECISION_TICK_SECONDS=0
- L1_MARKET_CSV_PATH=data/l1_full_run.csv
- SEEDS_5M_CSV=seeds/5m/btcusdt_5m_timing_core_v2.csv

Max ticks:

100000

## Run 1 Result

RUNTIME_RC:

0

Final snapshot:

CSV-00100000

Final tick:

100000

Final timestamp:

2017-10-25 21:39 UTC

Final position:

FLAT

Closed trades:

24

trades_l1.jsonl lines:

24

## Reconciliation

Result:

PASS

Details:

- audit_json_valid: PASS, events=48, bad_json_lines=0
- audit_vs_s2_position: PASS, position=FLAT
- audit_vs_trades: PASS, closed_trades=24
- trade_time_order: PASS, trades_checked=24
- loss_cluster_state: PASS, pause_entries_remaining=0, recent_closed_trade_pnls=10

## Observations

Runtime completed successfully.

No crash.

No unhandled exception.

State persisted through tick 100000.

System stopped correctly because max_ticks was reached.

Observed at final tick:

- guard_reason=guard_ok
- s4_kill_level=SOFT
- position=FLAT

The SOFT kill level is noted for later operational metrics review in P73.

It is not treated as a blocker in this run because reconciliation passed, runtime completed with RC 0, and final position remained FLAT.

## Assessment

P72 Run 1:

PASS

## Next Recommended Step

Continue P72 with a resume-based observation run.

Recommended next run:

250000 additional ticks

Expected continuation:

CSV-00100000 -> CSV-00350000

State should be preserved before the next run.

---

# Run 2 Resume Observation

## Run 2 Objective

Validate continued PAPER runtime operation without cleaning active runtime state.

This run intentionally reused the existing state from Run 1.

## Run 2 Configuration

Profile:

PAPER

Flags:

- L1_REQUIRE_WSL=1
- L1_PROFILE=PAPER
- L1_STARTUP_RECOVERY=1
- L1_STARTUP_RECONCILIATION_GATE=1
- L1_DECISION_TICK_SECONDS=0
- L1_MARKET_CSV_PATH=data/l1_full_run.csv
- SEEDS_5M_CSV=seeds/5m/btcusdt_5m_timing_core_v2.csv

Max ticks:

250000

## Run 2 Result

RUNTIME_RC:

0

Final snapshot:

CSV-00350000

Final tick:

250000

Final timestamp:

2018-05-04 02:01 UTC

Final position:

FLAT

Closed trades:

54

trades_l1.jsonl lines:

54

## Resume Validation

Run 1 ended at:

CSV-00100000

Run 2 ended at:

CSV-00350000

Expected continuation:

100000 + 250000 = 350000

Observed:

CSV-00350000

Result:

PASS

## Reconciliation

Result:

PASS

Details:

- audit_json_valid: PASS, events=200, bad_json_lines=0
- audit_vs_s2_position: PASS, position=FLAT
- audit_vs_trades: PASS, closed_trades=54
- trade_time_order: PASS, trades_checked=54
- loss_cluster_state: PASS, pause_entries_remaining=25, recent_closed_trade_pnls=0

## Observations

Runtime completed successfully.

No crash.

No unhandled exception.

State persisted through tick 250000 of the resumed run.

System stopped correctly because max_ticks was reached.

Observed at final tick:

- guard_reason=guard_ok
- s4_kill_level=SOFT
- position=FLAT

The SOFT kill level remains noted for P73 operational metrics review.

## Assessment

P72 Run 2:

PASS

Resume-based extended PAPER observation is valid.

---

# Run 3 Long Resume Observation

## Run 3 Objective

Validate long-duration PAPER runtime continuation using preserved runtime state from Run 2.

This run intentionally reused active runtime logs and state files.

## Run 3 Configuration

Profile:

PAPER

Flags:

- L1_REQUIRE_WSL=1
- L1_PROFILE=PAPER
- L1_STARTUP_RECOVERY=1
- L1_STARTUP_RECONCILIATION_GATE=1
- L1_DECISION_TICK_SECONDS=0
- L1_MARKET_CSV_PATH=data/l1_full_run.csv
- SEEDS_5M_CSV=seeds/5m/btcusdt_5m_timing_core_v2.csv

Max ticks:

2000000

## Run 3 Result

RUNTIME_RC:

0

Final snapshot:

CSV-02350000

Final tick:

2000000

Final timestamp:

2022-02-25 00:02 UTC

Final position:

FLAT

Closed trades:

231

trades_l1.jsonl lines:

231

## Resume Validation

Run 2 ended at:

CSV-00350000

Run 3 ended at:

CSV-02350000

Expected continuation:

350000 + 2000000 = 2350000

Observed:

CSV-02350000

Result:

PASS

## Reconciliation

Result:

PASS

Details:

- audit_json_valid: PASS, events=951, bad_json_lines=0
- audit_vs_s2_position: PASS, position=FLAT
- audit_vs_trades: PASS, closed_trades=231
- trade_time_order: PASS, trades_checked=231
- loss_cluster_state: PASS, pause_entries_remaining=4, recent_closed_trade_pnls=0

## Observations

Runtime completed successfully.

No crash.

No unhandled exception.

State persisted through 2000000 additional ticks.

System stopped correctly because max_ticks was reached.

Observed at final tick:

- guard_reason=guard_ok
- s4_kill_level=SOFT
- position=FLAT

The SOFT kill level remains noted for P73 operational metrics review.

## Assessment

P72 Run 3:

PASS

Long resume-based PAPER observation is valid.
