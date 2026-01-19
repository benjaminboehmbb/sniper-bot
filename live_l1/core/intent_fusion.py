#!/usr/bin/env python3
# live_l1/core/intent_fusion.py
#
# Purpose:
#   Minimal, deterministic fusion of 1m intent with 5m timing vote according to:
#   docs/POLICIES/L1_INTENT_5M_FUSION_POLICY_v1.md
#
# Notes:
#   - No market data logic here.
#   - No 5m aggregation here.
#   - Pure policy logic: input -> decision + reason_code.
#   - ASCII-only logs/strings.

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Literal


Intent = Literal["BUY", "SELL", "HOLD"]
VoteDir = Literal["long", "short", "none"]


@dataclass(frozen=True)
class TimingVote:
    direction: VoteDir
    strength: float
    seed_id: Optional[str] = None


@dataclass(frozen=True)
class FusionDecision:
    intent_final: Intent
    reason_code: str
    intent_1m_raw: Intent
    vote_5m_direction: VoteDir
    vote_5m_strength: float
    vote_5m_seed_id: Optional[str]
    allow_long: int
    allow_short: int
    thresh: float


def merge_intent_with_5m_vote(
    intent_1m_raw: Intent,
    vote: TimingVote,
    allow_long: int,
    allow_short: int,
    thresh: float = 0.60,
) -> FusionDecision:
    """
    Deterministic fusion policy v1.

    Inputs:
      - intent_1m_raw: BUY/SELL/HOLD
      - vote: TimingVote(direction in {long, short, none}, strength in [0,1], seed_id optional)
      - allow_long / allow_short: 0 or 1 (gate flags)
      - thresh: confirmation threshold (default 0.60)

    Output:
      - FusionDecision(intent_final, reason_code, ... context fields)
    """
    # sanitize allow flags
    allow_long_i = 1 if int(allow_long) == 1 else 0
    allow_short_i = 1 if int(allow_short) == 1 else 0

    # sanitize strength (keep deterministic, clamp)
    s = float(vote.strength)
    if s < 0.0:
        s = 0.0
    if s > 1.0:
        s = 1.0

    d = vote.direction

    # (1) HOLD passt durch
    if intent_1m_raw == "HOLD":
        return FusionDecision(
            intent_final="HOLD",
            reason_code="HOLD_RAW",
            intent_1m_raw=intent_1m_raw,
            vote_5m_direction=d,
            vote_5m_strength=s,
            vote_5m_seed_id=vote.seed_id,
            allow_long=allow_long_i,
            allow_short=allow_short_i,
            thresh=float(thresh),
        )

    # common conflict rule: vote none never confirms
    if d == "none":
        return FusionDecision(
            intent_final="HOLD",
            reason_code="NO_5M_VOTE",
            intent_1m_raw=intent_1m_raw,
            vote_5m_direction=d,
            vote_5m_strength=s,
            vote_5m_seed_id=vote.seed_id,
            allow_long=allow_long_i,
            allow_short=allow_short_i,
            thresh=float(thresh),
        )

    # (2) BUY path
    if intent_1m_raw == "BUY":
        if allow_long_i != 1:
            rc = "GATE_BLOCK_LONG"
            out = "HOLD"
        elif d != "long":
            rc = "5M_CONTRADICTS_1M"
            out = "HOLD"
        elif s < float(thresh):
            rc = "WEAK_5M_LONG_CONFIRM"
            out = "HOLD"
        else:
            rc = "CONFIRMED_1M_BUY_5M_LONG"
            out = "BUY"

        return FusionDecision(
            intent_final=out,  # type: ignore[arg-type]
            reason_code=rc,
            intent_1m_raw=intent_1m_raw,
            vote_5m_direction=d,
            vote_5m_strength=s,
            vote_5m_seed_id=vote.seed_id,
            allow_long=allow_long_i,
            allow_short=allow_short_i,
            thresh=float(thresh),
        )

    # (3) SELL path
    if intent_1m_raw == "SELL":
        if allow_short_i != 1:
            rc = "GATE_BLOCK_SHORT"
            out = "HOLD"
        elif d != "short":
            rc = "5M_CONTRADICTS_1M"
            out = "HOLD"
        elif s < float(thresh):
            rc = "WEAK_5M_SHORT_CONFIRM"
            out = "HOLD"
        else:
            rc = "CONFIRMED_1M_SELL_5M_SHORT"
            out = "SELL"

        return FusionDecision(
            intent_final=out,  # type: ignore[arg-type]
            reason_code=rc,
            intent_1m_raw=intent_1m_raw,
            vote_5m_direction=d,
            vote_5m_strength=s,
            vote_5m_seed_id=vote.seed_id,
            allow_long=allow_long_i,
            allow_short=allow_short_i,
            thresh=float(thresh),
        )

    # defensive fallback (should be unreachable with correct types)
    return FusionDecision(
        intent_final="HOLD",
        reason_code="INVALID_INTENT",
        intent_1m_raw=intent_1m_raw,
        vote_5m_direction=d,
        vote_5m_strength=s,
        vote_5m_seed_id=vote.seed_id,
        allow_long=allow_long_i,
        allow_short=allow_short_i,
        thresh=float(thresh),
    )


def _demo() -> None:
    # Simple deterministic smoke checks (prints only)
    cases = [
        ("HOLD", TimingVote("long", 1.0, "X"), 1, 1),
        ("BUY", TimingVote("none", 1.0, "X"), 1, 1),
        ("BUY", TimingVote("short", 1.0, "X"), 1, 1),
        ("BUY", TimingVote("long", 0.59, "X"), 1, 1),
        ("BUY", TimingVote("long", 0.60, "X"), 1, 1),
        ("SELL", TimingVote("long", 1.0, "X"), 1, 1),
        ("SELL", TimingVote("short", 0.60, "X"), 1, 1),
        ("SELL", TimingVote("short", 0.60, "X"), 1, 0),
    ]
    for intent, vote, al, ash in cases:
        d = merge_intent_with_5m_vote(intent, vote, al, ash, thresh=0.60)
        print(
            "intent_1m_raw=%s vote=(%s,%.2f) allow_long=%d allow_short=%d -> intent_final=%s reason=%s"
            % (
                d.intent_1m_raw,
                d.vote_5m_direction,
                d.vote_5m_strength,
                d.allow_long,
                d.allow_short,
                d.intent_final,
                d.reason_code,
            )
        )


if __name__ == "__main__":
    _demo()
