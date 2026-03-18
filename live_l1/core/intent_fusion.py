#!/usr/bin/env python3
# live_l1/core/intent_fusion.py
#
# Deterministic fusion of 1m intent with 5m timing vote.
#
# L1-I policy:
# - BUY remains strict for LONG entries
# - SELL remains strict for SHORT entries
# - BUT exits must always remain possible
#
# Exit rules:
# - if current_position == LONG and 1m says SELL:
#     allow SELL as exit, regardless of 5m direction
# - if current_position == SHORT and 1m says BUY:
#     allow BUY as exit, regardless of 5m direction
#
# This decouples exit handling from directional entry gating.
#
# ASCII-only.

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Literal, Optional


Intent = Literal["BUY", "SELL", "HOLD"]
VoteDir = Literal["long", "short", "none"]
Position = Literal["FLAT", "LONG", "SHORT"]


@dataclass(frozen=True)
class TimingVote:
    direction: VoteDir
    strength: float
    seed_id: Optional[str] = None


@dataclass(frozen=True)
class FusionDecision:
    intent_id: str
    intent_final: Intent
    reason_code: str
    intent_1m_raw: Intent
    vote_5m_direction: VoteDir
    vote_5m_strength: float
    vote_5m_seed_id: Optional[str]
    allow_long: int
    allow_short: int
    thresh: float
    current_position: str


def _new_intent_id() -> str:
    return "IN-" + uuid.uuid4().hex[:12]


def _clamp01(x: float) -> float:
    try:
        v = float(x)
    except Exception:
        return 0.0
    if v < 0.0:
        return 0.0
    if v > 1.0:
        return 1.0
    return v


def _norm_position(value: object) -> str:
    s = "" if value is None else str(value).strip().upper()
    if s in ("FLAT", "LONG", "SHORT"):
        return s
    return "FLAT"


def fuse_intent_with_5m_timing(
    *,
    intent_1m_raw: Intent,
    vote_5m_direction: VoteDir,
    vote_5m_strength: float,
    thresh: float = 0.60,
    allow_long: int = 1,
    allow_short: int = 1,
    vote_5m_seed_id: Optional[str] = None,
    current_position: str = "FLAT",
) -> FusionDecision:
    allow_long_i = 1 if int(allow_long) == 1 else 0
    allow_short_i = 1 if int(allow_short) == 1 else 0
    s = _clamp01(vote_5m_strength)
    d = vote_5m_direction
    pos = _norm_position(current_position)
    intent_id = _new_intent_id()

    if intent_1m_raw == "HOLD":
        return FusionDecision(
            intent_id=intent_id,
            intent_final="HOLD",
            reason_code="HOLD_RAW",
            intent_1m_raw="HOLD",
            vote_5m_direction=d,
            vote_5m_strength=s,
            vote_5m_seed_id=vote_5m_seed_id,
            allow_long=allow_long_i,
            allow_short=allow_short_i,
            thresh=float(thresh),
            current_position=pos,
        )

    if intent_1m_raw == "BUY":
        # L1-I: BUY must always be allowed as exit from an existing SHORT.
        if pos == "SHORT":
            return FusionDecision(
                intent_id=intent_id,
                intent_final="BUY",
                reason_code="EXIT_SHORT_ON_1M_BUY",
                intent_1m_raw="BUY",
                vote_5m_direction=d,
                vote_5m_strength=s,
                vote_5m_seed_id=vote_5m_seed_id,
                allow_long=allow_long_i,
                allow_short=allow_short_i,
                thresh=float(thresh),
                current_position=pos,
            )

        # Otherwise BUY remains directional / entry-like behaviour.
        if allow_long_i != 1:
            out = "HOLD"
            rc = "GATE_BLOCK_LONG"
        elif d == "none":
            out = "HOLD"
            rc = "NO_5M_VOTE"
        elif d != "long":
            out = "HOLD"
            rc = "5M_CONTRADICTS_1M"
        elif s < float(thresh):
            out = "HOLD"
            rc = "WEAK_5M_LONG_CONFIRM"
        else:
            out = "BUY"
            rc = "CONFIRMED_1M_BUY_5M_LONG"

        return FusionDecision(
            intent_id=intent_id,
            intent_final=out,
            reason_code=rc,
            intent_1m_raw="BUY",
            vote_5m_direction=d,
            vote_5m_strength=s,
            vote_5m_seed_id=vote_5m_seed_id,
            allow_long=allow_long_i,
            allow_short=allow_short_i,
            thresh=float(thresh),
            current_position=pos,
        )

    if intent_1m_raw == "SELL":
        # L1-I: SELL must always be allowed as exit from an existing LONG.
        if pos == "LONG":
            return FusionDecision(
                intent_id=intent_id,
                intent_final="SELL",
                reason_code="EXIT_LONG_ON_1M_SELL",
                intent_1m_raw="SELL",
                vote_5m_direction=d,
                vote_5m_strength=s,
                vote_5m_seed_id=vote_5m_seed_id,
                allow_long=allow_long_i,
                allow_short=allow_short_i,
                thresh=float(thresh),
                current_position=pos,
            )

        # Otherwise SELL remains directional / entry-like behaviour.
        if d == "long":
            out = "HOLD"
            rc = "5M_CONTRADICTS_1M"
        elif d == "short":
            if s < float(thresh):
                out = "HOLD"
                rc = "WEAK_5M_SHORT_CONFIRM"
            else:
                out = "SELL"
                if allow_short_i == 1:
                    rc = "CONFIRMED_1M_SELL_5M_SHORT"
                else:
                    rc = "CONFIRMED_1M_SELL_5M_SHORT_EXIT_ONLY"
        elif d == "none":
            out = "SELL"
            if allow_short_i == 1:
                rc = "SELL_EXIT_ON_NEUTRAL_5M"
            else:
                rc = "SELL_EXIT_ONLY_ON_NEUTRAL_5M"
        else:
            out = "HOLD"
            rc = "UNKNOWN_5M_DIRECTION"

        return FusionDecision(
            intent_id=intent_id,
            intent_final=out,
            reason_code=rc,
            intent_1m_raw="SELL",
            vote_5m_direction=d,
            vote_5m_strength=s,
            vote_5m_seed_id=vote_5m_seed_id,
            allow_long=allow_long_i,
            allow_short=allow_short_i,
            thresh=float(thresh),
            current_position=pos,
        )

    return FusionDecision(
        intent_id=intent_id,
        intent_final="HOLD",
        reason_code="UNKNOWN_INTENT",
        intent_1m_raw="HOLD",
        vote_5m_direction=d,
        vote_5m_strength=s,
        vote_5m_seed_id=vote_5m_seed_id,
        allow_long=allow_long_i,
        allow_short=allow_short_i,
        thresh=float(thresh),
        current_position=pos,
    )

