# P47 RUNTIME TIMING SIGNAL WIRING FIX DESIGN

Date: 2026-06-06
Device: G15 / AR15
Environment: WSL

## Objective

Design the runtime wiring fix so compute_5m_timing_vote receives the signal values required by polarity-aware timing scoring.

No runtime code is changed in P47.

## Background

P44 implemented polarity-aware timing scoring.

P44 isolated tests passed:

- positive signals -> long
- negative signals -> short
- mixed signals -> none

P45 mini runtime validation produced:

- vote_5m_direction=none: 100
- vote_5m_seed_id=None: 100

P46 audited live_l1/core/loop.py and found that compute_5m_timing_vote is called without signal kwargs.

Current call:

compute_5m_timing_vote(
    seeds_csv=...,
    thresh=...,
    symbol=...,
    now_utc=...,
)

Therefore timing_5m.py receives no rsi_signal, stoch_signal, or other *_signal values.

## Root Cause

Runtime signal wiring is incomplete.

features contains signal access via:

features.signal("rsi_signal")
features.signal("stoch_signal")
features.signal("mfi_signal")
features.signal("ma200_signal")
features.signal("atr_signal")

but these values are not passed into compute_5m_timing_vote.

## Design Decision

Pass a controlled signal kwargs set from live_l1/core/loop.py into compute_5m_timing_vote.

## Required Runtime Signals

Pass the full current Live L1 signal set:

- rsi_signal
- macd_signal
- bollinger_signal
- ma200_signal
- stoch_signal
- atr_signal
- ema50_signal
- adx_signal
- cci_signal
- mfi_signal
- obv_signal
- roc_signal

## Reason

The seed model uses seed keys such as:

- rsi
- stoch

and maps them internally to:

- rsi_signal
- stoch_signal

Passing the full signal set makes future seeds possible without further loop.py changes.

## Patch Location

File:

live_l1/core/loop.py

Call site:

compute_5m_timing_vote(...)

around the current vote_v1 assignment.

## Proposed Call Shape

compute_5m_timing_vote(
    seeds_csv=os.path.join(repo_root, cfg.seeds_5m_csv),
    thresh=cfg.thresh_5m,
    symbol=cfg.symbol,
    now_utc=tick.tick_started_utc,
    rsi_signal=features.signal("rsi_signal"),
    macd_signal=features.signal("macd_signal"),
    bollinger_signal=features.signal("bollinger_signal"),
    ma200_signal=features.signal("ma200_signal"),
    stoch_signal=features.signal("stoch_signal"),
    atr_signal=features.signal("atr_signal"),
    ema50_signal=features.signal("ema50_signal"),
    adx_signal=features.signal("adx_signal"),
    cci_signal=features.signal("cci_signal"),
    mfi_signal=features.signal("mfi_signal"),
    obv_signal=features.signal("obv_signal"),
    roc_signal=features.signal("roc_signal"),
)

## Validation Plan

P48 implementation must include:

1. py_compile live_l1/core/loop.py

2. py_compile live_l1/core/timing_5m.py

3. P44 isolated timing test

4. P45-style mini runtime run with new segment extraction

Expected after patch:

- vote_5m_direction should no longer be structurally forced to none
- vote_5m_seed_id should be populated when rsi/stoch signals support long or short
- reconciliation must PASS
- monitoring must PASS

## Acceptance Criteria

The wiring fix is accepted only if:

- code compiles
- isolated timing test remains PASS
- runtime starts
- runtime passes reconciliation
- runtime passes monitoring
- timing votes reflect real runtime signals

## Risk

Moderate.

This will materially affect runtime timing votes.

Possible outcomes:

- more none votes
- some long votes
- some short votes
- changed intent fusion behavior
- changed trade frequency

## Mitigation

Run only mini validation after implementation.

No full run before P49/P50.

## Decision

Proceed to P48 Runtime Timing Signal Wiring Implementation.

## P47 Result

Runtime timing signal wiring fix designed.

Status:

PASS
