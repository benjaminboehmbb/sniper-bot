#!/usr/bin/env python3
# live_l1/core/gate_builder.py
# Online allow gate builder for Live L1.
# Source of Truth:
# tools/gs_build_asymmetric_gate.py
# ASCII-only.

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GateDecision:
    allow_long: int
    allow_short: int
    regime_v2: int


def build_online_gates(regime_v2: int) -> GateDecision:
    r = int(regime_v2)

    allow_long = int(r == 1)
    allow_short = int(r == -1)

    return GateDecision(
        allow_long=allow_long,
        allow_short=allow_short,
        regime_v2=r,
    )
