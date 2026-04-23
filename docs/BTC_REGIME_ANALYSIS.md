# BTC Historical Regime Analysis (2017-08-17 -> 2025-12-31)

## Data Basis

- Dataset: BTCUSDT 1m
- Start: 2017-08-17 04:00 UTC (offset = 0)
- End:   2025-12-31 23:59 UTC
- Total duration: ~8.4 years
- Offset unit: 1 offset = 1 minute

### Reference Offsets

offset = 0        -> 2017-08-17 04:00 UTC
offset = 500000   -> 2018-07-30 09:20 UTC
offset = 1000000  -> 2019-07-12 14:40 UTC
offset = 1300000  -> 2020-02-05 22:40 UTC
offset = 1600000  -> 2020-09-01 06:40 UTC

IMPORTANT:
- offset 1600000 is still 2020 (NOT 2021)

---

## Macro Regime Segmentation

### R1: Late 2017 Bull Run (Blow-off Phase)
Time:
- 2017-08 -> ~2018-01
Offsets:
- ~0 -> ~200000

Characteristics:
- strong uptrend
- high volatility
- momentum-dominated
- shallow pullbacks

Implication:
- trend-following performs well
- mean-reversion performs poorly

---

### R2: 2018 Bear Market
Time:
- ~2018-01 -> ~2018-12
Offsets:
- ~200000 -> ~600000

Characteristics:
- persistent downtrend
- relief rallies but weak structure
- frequent lower highs

Implication:
- short strategies favored
- long entries require strict filtering

---

### R3: 2019 Recovery Phase
Time:
- ~2019-01 -> ~2019-07
Offsets:
- ~600000 -> ~1000000

Characteristics:
- strong recovery trend
- high momentum bursts
- mixed trend + pullback behavior

Implication:
- hybrid strategies (trend + pullback) perform best

---

### R4: Late 2019 -> Early 2020 Transition / Stress
Time:
- ~2019-08 -> ~2020-03
Offsets:
- ~1000000 -> ~1350000

Characteristics:
- unstable structure
- increased uncertainty
- includes 2020 crash phase

Implication:
- exit quality becomes critical
- drawdown control tested

---

### R5: 2020 Post-Crash Recovery / Bull Build-up
Time:
- ~2020-03 -> ~2020-12
Offsets:
- ~1350000 -> ~1800000

Characteristics:
- clear regime shift after crash
- trend re-establishment
- increasing momentum reliability

Implication:
- early trend detection critical
- too tight TP/SL limits performance

---

### R6: 2021 Bull Market / Expansion + Distribution
Time:
- ~2021-01 -> ~2021-11

Characteristics:
- strong uptrend
- increased volatility vs 2017
- later instability (distribution)

Implication:
- profit maximization phase
- weak exits reduce total returns

---

### R7: 2022 Bear Market
Time:
- ~2021-12 -> ~2022-12

Characteristics:
- structural downtrend
- large drawdowns
- multiple acceleration phases

Implication:
- critical for robustness validation
- long-only logic often fails

---

### R8: 2023 Recovery / Mixed Regime
Time:
- 2023

Characteristics:
- partial recovery
- mixed trend + sideways
- regime inconsistency

Implication:
- market gate quality becomes critical
- chop detection required

---

### R9: 2024 Bull Phase
Time:
- 2024

Characteristics:
- renewed strong trend phases
- impulsive price movements

Implication:
- validates profit scalability
- entry responsiveness critical

---

### R10: 2025 Data-Driven Regime (NO ASSUMPTION)

Time:
- 2025

IMPORTANT:
- DO NOT assign regime based on assumptions
- MUST be classified via metrics

Required metrics:
- return
- volatility
- max drawdown
- trend strength
- directional persistence
- chop ratio

---

## Technical Regime Layer (Independent of Time)

Each window must also be classified as:

- UP_TREND_HIGH_VOL
- UP_TREND_LOW_VOL
- DOWN_TREND_HIGH_VOL
- DOWN_TREND_LOW_VOL
- SIDEWAYS_HIGH_VOL
- SIDEWAYS_LOW_VOL
- CRISIS_EVENT
- RECOVERY_PHASE

---

## Usage for Trading Bot

### Core Principle

DO NOT evaluate strategies only globally.

ALWAYS evaluate per regime:

1. select window (e.g. 200k ticks)
2. map to regime
3. evaluate metrics:
   - return_pct
   - profit_factor
   - max_drawdown_pct
   - num_trades
   - avg_pnl

---

### Critical Insight Target

Identify:

- strategies that only work in bull regimes
- strategies that collapse in bear regimes
- strategies that survive across all regimes

---

### Validation Rule

A strategy is only considered robust if:

- acceptable performance in:
  - bull
  - bear
  - transition

NOT only in one regime.

---

## Next Step (Mandatory)

Build automated regime classification:

Input:
- rolling window (e.g. 50k or 100k ticks)

Output per window:
- return
- volatility
- drawdown
- trend score
- regime label

Goal:
- fully automated regime-aware backtesting