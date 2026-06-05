#!/usr/bin/env python3
# live_l1/core/gate_builder.py
# Online allow gate builder for Live L1.
# ASCII-only.

from __future__ import annotations

from dataclasses import dataclass


ADX_LONG_THRESHOLD = 15.0
ADX_SHORT_THRESHOLD = 20.0


@dataclass(frozen=True)
class GateDecision:
    allow_long: int
    allow_short: int
    regime_v1: int
    adx: float


def build_online_gates(regime_v1: int, adx: float) -> GateDecision:
    r = int(regime_v1)
    a = float(adx)

    allow_long = int(r >= 0 and a >= ADX_LONG_THRESHOLD)
    allow_short = int(r == -1 and a >= ADX_SHORT_THRESHOLD)

    return GateDecision(
        allow_long=allow_long,
        allow_short=allow_short,
        regime_v1=r,
        adx=a,
    )
