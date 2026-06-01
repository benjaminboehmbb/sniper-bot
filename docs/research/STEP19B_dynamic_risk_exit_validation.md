# STEP19B Dynamic Risk Exit Validation

## Configuration

Dynamic Exit Trigger

- shadow_risk_score > 0.50
- 3 consecutive lifecycle snapshots
- exit at lifecycle current_price

Lifecycle logging upgraded from:

- every 5 minutes after 15 minutes

to:

- every 1 minute after 1 minute

This was required to obtain sufficient trade lifecycle coverage.

---

## Validation Window 1

200k ticks @ offset 1000000

Original

- pnl: 246.84
- pf: 5.2996
- max_dd_pct: 0.0037

STEP19B

- pnl: 271.88
- pf: 10.0536
- max_dd_pct: 0.0020

Result

- pnl improved
- pf improved strongly
- drawdown reduced

---

## Validation Window 2

200k ticks @ offset 0

Original

- pnl: 68.83
- pf: 1.1332
- max_dd_pct: 0.0186

STEP19B

- pnl: 154.84
- pf: 1.3600
- max_dd_pct: 0.0143

Result

- pnl improved
- pf improved
- drawdown reduced

---

## Validation Window 3

200k ticks @ offset 500000

Original

- pnl: 214.04
- pf: 3.5445
- max_dd_pct: 0.0051

STEP19B

- pnl: 251.42
- pf: 8.0842
- max_dd_pct: 0.0015

Result

- pnl improved
- pf improved strongly
- drawdown reduced

---

## Current Conclusion

Three independent validation windows produced the same directional outcome:

- higher pnl
- higher profit factor
- lower drawdown

The original STEP19 entry-gate hypothesis failed.

The dynamic in-trade risk escalation hypothesis remains viable and is currently the strongest STEP19 candidate.

Next validation step:

- 500k @ offset 1500000
- repeat STEP19B replay
- evaluate robustness before any live integration
