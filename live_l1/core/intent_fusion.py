#!/usr/bin/env python3
# live_l1/core/intent_fusion.py
#
# Deterministic fusion of 1m intent with 5m timing vote.
# ASCII-only.

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Literal, Optional


Intent = Literal["BUY", "SELL", "HOLD"]
VoteDir = Literal["long", "short", "none"]


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


def fuse_intent_with_5m_timing(
    *,
    intent_1m_raw: Intent,
    vote_5m_direction: VoteDir,
    vote_5m_strength: float,
    thresh: float = 0.60,
    allow_long: int = 1,
    allow_short: int = 1,
    vote_5m_seed_id: Optional[str] = None,
) -> FusionDecision:
    allow_long_i = 1 if int(allow_long) == 1 else 0
    allow_short_i = 1 if int(allow_short) == 1 else 0
    s = _clamp01(vote_5m_strength)
    d = vote_5m_direction
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
        )

    if d == "none":
        return FusionDecision(
            intent_id=intent_id,
            intent_final="HOLD",
            reason_code="NO_5M_VOTE",
            intent_1m_raw=intent_1m_raw,
            vote_5m_direction=d,
            vote_5m_strength=s,
            vote_5m_seed_id=vote_5m_seed_id,
            allow_long=allow_long_i,
            allow_short=allow_short_i,
            thresh=float(thresh),
        )

    if intent_1m_raw == "BUY":
        if allow_long_i != 1:
            out = "HOLD"
            rc = "GATE_BLOCK_LONG"
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
        )

    if intent_1m_raw == "SELL":
        if allow_short_i != 1:
            out = "HOLD"
            rc = "GATE_BLOCK_SHORT"
        elif d != "short":
            out = "HOLD"
            rc = "5M_CONTRADICTS_1M"
        elif s < float(thresh):
            out = "HOLD"
            rc = "WEAK_5M_SHORT_CONFIRM"
        else:
            out = "SELL"
            rc = "CONFIRMED_1M_SELL_5M_SHORT"

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
        )

    return FusionDecision(
        intent_id=intent_id,
        intent_final="HOLD",
        reason_code="INVALID_INTENT",
        intent_1m_raw="HOLD",
        vote_5m_direction=d,
        vote_5m_strength=s,
        vote_5m_seed_id=vote_5m_seed_id,
        allow_long=allow_long_i,
        allow_short=allow_short_i,
        thresh=float(thresh),
    )


def merge_intent_with_5m_vote(
    intent_1m_raw: Intent,
    vote: TimingVote,
    allow_long: int,
    allow_short: int,
    thresh: float = 0.60,
) -> FusionDecision:
    return fuse_intent_with_5m_timing(
        intent_1m_raw=intent_1m_raw,
        vote_5m_direction=vote.direction,
        vote_5m_strength=vote.strength,
        vote_5m_seed_id=vote.seed_id,
        thresh=thresh,
        allow_long=allow_long,
        allow_short=allow_short,
    )

