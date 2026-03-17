#!/usr/bin/env python3
# live_l1/core/intent.py
# Deterministic 1m intent logic for L1 paper loop.
# ASCII-only.

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Tuple

from live_l1.core.feature_snapshot import FeatureSnapshot


IntentAction = Literal["BUY", "SELL", "HOLD"]


@dataclass(frozen=True)
class Intent:
    action: IntentAction


def make_hold_intent() -> Intent:
    return Intent(action="HOLD")


def compute_1m_intent_raw(*, cfg, tick_id: int, features: FeatureSnapshot) -> Tuple[IntentAction, bool]:
    """
    Returns:
        (intent_1m_raw, forced)

    Behavior:
    - Warmup ticks: HOLD
    - Forced mode: deterministic SELL/BUY rules for tests
    - Normal mode: derive 1m intent from feature snapshot signal score

    Conservative thresholds:
    - score >= +2 -> BUY
    - score <= -2 -> SELL
    - otherwise HOLD
    """

    warmup = int(getattr(cfg, "test_force_warmup_ticks", 0))
    if tick_id <= warmup:
        return ("HOLD", False)

    force_enabled = bool(getattr(cfg, "test_force_intents", False))
    if force_enabled:
        sell_every = int(getattr(cfg, "test_force_sell_every", 0))
        buy_every = int(getattr(cfg, "test_force_buy_every", 0))

        if sell_every > 0 and tick_id % sell_every == 0:
            return ("SELL", True)

        if buy_every > 0 and tick_id % buy_every == 0:
            return ("BUY", True)

        return ("HOLD", False)

    score = features.signal_score()

    if score >= 2:
        return ("BUY", False)

    if score <= -2:
        return ("SELL", False)

    return ("HOLD", False)