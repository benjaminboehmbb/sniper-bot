#!/usr/bin/env python3
# live_l1/core/intent_fusion.py
#
# Deterministic fusion of 1m intent with 5m timing vote.
#
# Clean separation of responsibilities:
# - intent.py: raw 1m intent
# - intent_fusion.py: 1m/5m fusion + exit handling only
# - market_gate.py: hard market entry filtering
#
# Policy:
# - Exits must always remain possible
# - Fusion must NOT hard-block entries via allow_long / allow_short
# - allow_long / allow_short are logged for observability only
#
# Current asymmetric policy:
# - BUY from FLAT still requires 5m long confirmation
# - SELL from FLAT is primarily driven by 1m and is only blocked by a
#   strong opposing 5m long vote
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


def _norm_vote_dir(value: object) -> VoteDir:
    s = "" if value is None else str(value).strip().lower()
    if s in ("long", "short", "none"):
        return s  # type: ignore[return-value]
    if s in ("buy", "bull", "up"):
        return "long"
    if s in ("sell", "bear", "down"):
        return "short"
    return "none"


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
    d = _norm_vote_dir(vote_5m_direction)
    pos = _norm_position(current_position)
    t = float(thresh)
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
            thresh=t,
            current_position=pos,
        )

    if intent_1m_raw == "BUY":
        # Exit from SHORT must always remain possible.
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
                thresh=t,
                current_position=pos,
            )

        # FLAT -> BUY is now asymmetric like SELL:
        # 1m BUY is allowed unless there is a strong opposing short vote.
        if d == "none":
            out = "BUY"
            rc = "ASYM_BUY_NO_5M_VOTE"
        elif d == "long":
            if s < t:
                out = "BUY"
                rc = "ASYM_BUY_WEAK_5M_LONG_ALLOWED"
            else:
                out = "BUY"
                rc = "CONFIRMED_1M_BUY_5M_LONG"
        elif d == "short":
            if s >= t:
                out = "HOLD"
                rc = "ASYM_BUY_BLOCKED_BY_STRONG_5M_SHORT"
            else:
                out = "BUY"
                rc = "ASYM_BUY_WEAK_5M_SHORT_IGNORED"
        else:
            out = "BUY"
            rc = "ASYM_BUY_UNKNOWN_5M_ALLOWED"

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
            thresh=t,
            current_position=pos,
        )

    if intent_1m_raw == "SELL":
        # Exit from LONG must always remain possible.
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
                thresh=t,
                current_position=pos,
            )

        # FLAT -> SELL is now asymmetric:
        # 1m SELL is allowed unless there is a strong opposing long vote.
        if d == "none":
            out = "SELL"
            rc = "ASYM_SELL_NO_5M_VOTE"
        elif d == "short":
            if s < t:
                out = "SELL"
                rc = "ASYM_SELL_WEAK_5M_SHORT_ALLOWED"
            else:
                out = "SELL"
                rc = "CONFIRMED_1M_SELL_5M_SHORT"
        elif d == "long":
            if s >= t:
                out = "SELL"
                rc = "ASYM_SELL_STRONG_5M_LONG_IGNORED"
            else:
                out = "SELL"
                rc = "ASYM_SELL_WEAK_5M_LONG_IGNORED"
        else:
            out = "SELL"
            rc = "ASYM_SELL_UNKNOWN_5M_ALLOWED"

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
            thresh=t,
            current_position=pos,
        )

    return FusionDecision(
        intent_id=intent_id,
        intent_final="HOLD",
        reason_code="UNKNOWN_INTENT_FAILSAFE",
        intent_1m_raw="HOLD",
        vote_5m_direction=d,
        vote_5m_strength=s,
        vote_5m_seed_id=vote_5m_seed_id,
        allow_long=allow_long_i,
        allow_short=allow_short_i,
        thresh=t,
        current_position=pos,
    )

