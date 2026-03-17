#!/usr/bin/env python3
# live_l1/state/models.py
#
# Verbindliche State-Modelle fuer L1
# - NUR S2 (Position) und S4 (Risk)
# - Minimal, invariant
#
# ASCII-only.

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class PositionStateS2:
    symbol: str
    position: str  # FLAT/LONG/SHORT (L1: FLAT only)
    size: float    # 0.0 in L1
    entry_price: Optional[float]


@dataclass
class RiskStateS4:
    kill_level: str  # NONE/SOFT/HARD/EMERGENCY
    cooldown_until_utc: Optional[str]
