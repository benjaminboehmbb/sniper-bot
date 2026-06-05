# LIVE L1 ONLINE SIGNAL AND REGIME DESIGN

Date:

- 2026-06-05

Status:

DESIGN PHASE

Implementation:

NOT STARTED

---

# Purpose

Current Live-L1 relies on precomputed CSV fields:

- *_signal
- regime_v1
- regime_v2
- allow_long
- allow_short

This is sufficient for paper-mode replay.

For a future fully autonomous live system, these values must be generated online from incoming market data.

This document defines the target architecture.

---

# Current Live-L1 Dependencies

Current inputs:

- rsi_signal
- bollinger_signal
- stoch_signal
- cci_signal
- ma200_signal
- mfi_signal
- atr_signal
- macd_signal
- ema50_signal
- adx_signal
- obv_signal
- roc_signal

Additional inputs:

- regime_v2
- allow_long
- allow_short

Current source:

Precomputed CSV rows.

Future source:

Online calculation.

---

# Signals Actually Used By Trading Logic

Current entry and exit logic actively uses:

- rsi_signal
- bollinger_signal
- stoch_signal
- cci_signal
- ma200_signal
- mfi_signal
- atr_signal

These signals form the current production-critical set.

Priority:

P1

Must be available online.

---

# Signals Currently Passive

Currently transported but not required for trade decisions:

- macd_signal
- ema50_signal
- adx_signal
- obv_signal
- roc_signal

These remain useful for:

- monitoring
- diagnostics
- future research
- future strategy upgrades

Priority:

P2

---

# Online Signal Builder

Future module:

live_l1/core/signal_builder.py

Responsibilities:

- maintain rolling indicator state
- process incoming OHLCV data
- generate production-compatible signals

Output:

- identical signal semantics as current CSV pipeline

Target:

Signal values must match historical builder behavior as closely as possible.

---

# Online Regime Builder

Future module:

live_l1/core/regime_builder.py

Responsibilities:

- compute regime_v1
- compute regime_v2

---

# Regime v1 Definition

Source verified during audit.

Bull:

- close > ma200
- ma200_slope_1440 > 0

Bear:

- close < ma200
- ma200_slope_1440 < 0

Side:

- otherwise

Output:

- bull = +1
- side = 0
- bear = -1

---

# Regime v2 Definition

Source verified during audit.

Inputs:

- regime_v1

Rules:

- minimum state duration:
  720 bars

Optional:

- no_direct_flip

Meaning:

Bull -> Bear transitions require Side state first.

Output:

- regime_v2

---

# Online Gate Builder

Future module:

live_l1/core/gate_builder.py

Responsibilities:

- allow_long generation
- allow_short generation

---

# allow_long Definition

Current audited definition:

allow_long =

- regime_v1 >= 0
- ADX >= 15

Output:

- 0
- 1

---

# allow_short Definition

Current audited definition:

allow_short =

- regime_v1 == -1
- ADX >= 20

Output:

- 0
- 1

---

# Required Rolling State

Future live implementation requires maintaining:

- OHLCV history
- MA200
- MA200 slope
- ATR
- MFI
- ADX
- RSI
- Bollinger
- Stochastic
- CCI
- Regime state machine

---

# Validation Requirements

Before activation:

1. Offline replay.
2. Online builder output.
3. Compare signal parity.
4. Compare regime parity.
5. Compare gate parity.
6. Quantify deviations.

Target:

No material divergence from historical pipeline.

---

# Future Development Order

P1

- online signal builder
- online regime builder
- online gate builder

P2

- online parity validation framework

P3

- production activation testing

---

# Conclusion

Current Live-L1 is operational using precomputed signals.

The next major live-readiness milestone is replacing precomputed signal, regime and gate fields with deterministic online generation while preserving parity with the validated historical pipeline.

