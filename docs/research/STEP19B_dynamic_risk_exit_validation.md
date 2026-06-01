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

---

## 500k Validation

500k ticks @ offset 1500000

Original

- pnl: 1463.55
- pf: 2.4644
- max_dd_pct: 0.0517

STEP19B

- pnl: 1115.80
- pf: 1.8705
- max_dd_pct: 0.0544

Result

- pnl worse
- pf worse
- drawdown worse

Additional threshold sweep:

0.5 / 3
- pnl: 1115.80
- pf: 1.8705

0.5 / 5
- pnl: 1072.78
- pf: 1.7989

0.6 / 3
- pnl: 1060.21
- pf: 1.7927

0.6 / 5
- pnl: 1081.41
- pf: 1.8106

0.7 / 3
- pnl: 1060.21
- pf: 1.7927

Conclusion

The positive results observed on the three 200k windows did not generalize to the larger 500k validation window.

Current status:

- STEP19 Entry Gate: rejected
- STEP19 Dynamic Exit: not validated

Key finding:

shadow_risk_score contains predictive information for trade quality analysis but currently does not provide a robust standalone trading rule.
