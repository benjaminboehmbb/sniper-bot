# STEP20 FINAL SUMMARY

## Purpose

The STEP20 research track investigated whether shadow-risk information derived from the state-research framework could be transformed into a practical risk-management mechanism for the Sniper-Bot.

The primary goal was to determine whether shadow-risk information contains predictive value and whether that value can be converted into a live-compatible trading improvement.

---

# Initial Hypothesis

High-risk trades should receive lower exposure.

Low-risk trades should receive higher exposure.

Expected benefits:

- improved profit factor
- reduced drawdown
- improved robustness
- improved risk-adjusted returns

---

# STEP20A

## Research Replay

Method:

Use mean shadow risk over the complete trade lifetime.

Position sizing:

- risk <= 0.30 -> 1.00x
- risk <= 0.50 -> 0.50x
- risk > 0.50 -> 0.25x

Important:

STEP20A uses future information and is therefore not live-compatible.

---

## Validation Results

Validated on:

- 200k @ offset 0
- 200k @ offset 500000
- 200k @ offset 1000000
- 500k @ offset 1500000
- 1M @ offset 2500000
- 4.3M @ offset 0

---

## 4.3M Full History Result

Original

- pnl: 14022.01
- pf: 1.6859
- max_dd_pct: 0.1556

STEP20A

- pnl: 22389.30
- pf: 3.4704
- max_dd_pct: 0.0322

Result:

- strongly positive
- strongest state-research result achieved so far

---

# STEP20B

## Live Design

Objective:

Design a live-compatible implementation path.

Result:

Design completed.

No implementation performed.

---

# STEP20C

## Entry-Time Position Sizing

Method:

Use only information available at trade entry.

Result:

Original

- pnl: 13979.01
- pf: 1.6838
- max_dd_pct: 0.1561

STEP20C

- pnl: 9396.09
- pf: 1.7203
- max_dd_pct: 0.1212

Conclusion:

Entry-time shadow risk alone is not sufficiently predictive.

STEP20C not validated.

---

# STEP20D

## Dynamic Exposure Scaling

Concept:

Reduce exposure during trade lifetime when risk rises.

Proof-of-concept replay:

Original

- pnl: 14022.01
- pf: 1.6859
- max_dd_pct: 0.1556

STEP20D

- pnl: 19564.81
- pf: 4.1823
- max_dd_pct: 0.0283

Result:

Very strong performance.

However:

The replay applied final multipliers retroactively.

Methodologically optimistic.

Not suitable for production conclusions.

---

# STEP20E

## True Dynamic Exposure Replay

Objective:

Correct the methodological limitation of STEP20D.

Exposure reductions were applied dynamically during trade lifetime.

Result:

Original

- pnl: 14022.01
- pf: 1.6859
- max_dd_pct: 0.1556

STEP20E

- pnl: 9597.75
- pf: 1.5180
- max_dd_pct: 0.1084

Conclusion:

The live-compatible implementation did not reproduce STEP20A performance.

STEP20E not validated.

---

# Most Important Discovery

The most important discovery of STEP20 is not position sizing itself.

The key finding is:

Trade-lifetime shadow risk contains strong predictive information.

Examples:

- mean_risk vs pnl ≈ -0.42
- mean_risk vs win ≈ -0.57

High-risk trades:

- PF approximately 0.07

Low-risk trades:

- PF approximately 2.74

This relationship remained visible throughout the research process.

---

# Final Conclusions

Confirmed:

- shadow-risk information contains real predictive value
- trade-lifetime risk is strongly associated with trade quality
- high-risk trades perform substantially worse than low-risk trades

Not confirmed:

- simple entry-time sizing
- naive dynamic exposure reduction
- direct live-compatible replication of STEP20A

---

# Research Outcome

STEP20A

- validated research result

STEP20B

- design completed

STEP20C

- tested
- not validated

STEP20D

- proof of concept only

STEP20E

- tested
- not validated

---

# Recommended Future Use

The strongest future application is currently:

- monitoring
- diagnostics
- trade-quality analysis
- state evaluation
- post-trade analytics

Rather than immediate integration into live trading decisions.

---

# Status

STEP20 research track completed.

All major hypotheses have been tested, documented, archived and version-controlled.

Further work should only continue if a fundamentally new approach to exploiting trade-lifetime risk information is identified.

