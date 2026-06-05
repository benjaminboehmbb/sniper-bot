#!/usr/bin/env python3
# live_l1/core/gate_builder.py
# Online allow gate builder for Live L1.
# Source of Truth from data/l1_full_run.csv:
# allow_long  = (regime_v1 == 1)
# allow_short = (regime_v1 == -1)
# ASCII-only.

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GateDecision:
    allow_long: int
    allow_short: int
    regime_v1: int


def build_online_gates(regime_v1: int) -> GateDecision:
    r = int(regime_v1)

    allow_long = int(r == 1)
    allow_short = int(r == -1)

    return GateDecision(
        allow_long=allow_long,
        allow_short=allow_short,
        regime_v1=r,
    )
