# STEP20 Position Sizing Validation

## Hypothesis

Use shadow_risk_score as a position sizing mechanism instead of:

- entry filtering
- trade blocking
- dynamic exits

Sizing model:

- risk <= 0.30 -> 100%
- risk <= 0.50 -> 50%
- risk > 0.50 -> 25%

---

## Validation Window 1

200k ticks @ offset 0

Original

- pnl: 68.83
- pf: 1.1332
- max_dd_pct: 0.0186

STEP20A

- pnl: 353.99
- pf: 2.5677
- max_dd_pct: 0.0087

Result

- pnl improved
- pf improved
- drawdown reduced

---

## Validation Window 2

200k ticks @ offset 500000

Original

- pnl: 214.04
- pf: 3.5445
- max_dd_pct: 0.0051

STEP20A

- pnl: 238.23
- pf: 9.1092
- max_dd_pct: 0.0013

Result

- pnl improved
- pf improved strongly
- drawdown reduced strongly

---

## Validation Window 3

200k ticks @ offset 1000000

Original

- pnl: 246.84
- pf: 5.2996
- max_dd_pct: 0.0037

STEP20A

- pnl: 217.79
- pf: 7.2898
- max_dd_pct: 0.0018

Result

- pnl slightly lower
- pf improved
- drawdown reduced

---

## Validation Window 4

500k ticks @ offset 1500000

Original

- pnl: 1463.55
- pf: 2.4644
- max_dd_pct: 0.0517

STEP20A

- pnl: 1770.94
- pf: 5.0174
- max_dd_pct: 0.0216

Result

- pnl improved
- pf improved strongly
- drawdown reduced strongly

---

## Current Conclusion

STEP20A is the strongest result produced by the state-research track so far.

Validation summary:

- positive: 3 windows
- mixed positive: 1 window
- negative: 0 windows

Current status:

- STEP19 Entry Gate: rejected
- STEP19 Dynamic Exit: not validated
- STEP20 Position Sizing: validated candidate

Next validation step:

- 1M @ offset 2500000
- repeat STEP20A replay
- evaluate robustness before live integration

---

## Validation Window 5

1M ticks @ offset 2500000

Original

- pnl: 2648.74
- pf: 2.0156
- max_dd_pct: 0.0478

STEP20A

- pnl: 3490.28
- pf: 3.9539
- max_dd_pct: 0.0228

Result

- pnl improved
- pf improved strongly
- drawdown reduced strongly

Updated conclusion:

STEP20A remains positive on the first 1M validation window and is currently the strongest validated state-research candidate.
