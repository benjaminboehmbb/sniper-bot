#!/usr/bin/env python3
# live_l1/core/intent_fusion.py
#
# Purpose:
#   Minimal, deterministic fusion of 1m intent with 5m timing vote according to:
#   docs/POLICIES/L1_INTENT_5M_FUSION_POLICY_v1.md
#
# Shadow-mode support:
#   Optionally accept a second "shadow" 5m vote (e.g. v2) for comparison/logging only.
#   IMPORTANT: Shadow vote NEVER changes intent_final or reason_code. v1 remains authoritative.
#
# Notes:
#   - No market data logic here.
#   - No 5m aggregation here.
#   - Pure policy logic: input -> decision + reason_code (+ optional shadow context).
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
    # authoritative result (v1)
    intent_final: Intent
    reason_code: str

    # inputs/context
    intent_1m_raw: Intent
    vote_5m_direction: VoteDir
    vote_5m_strength: float
    vote_5m_seed_id: Optional[str]
    allow_long: int
    allow_short: int
    thresh: float

    # optional shadow vote context (v2)
    shadow_vote_direction: Optional[VoteDir] = None
    shadow_vote_strength: Optional[float] = None
    shadow_vote_seed_id: Optional[str] = None
    shadow_tag: Optional[str] = None


def merge_intent_with_5m_vote(
    intent_1m_raw: Intent,
    vote: TimingVote,
    allow_long: int,
    allow_short: int,
    thresh: float = 0.60,
    shadow_vote: Optional[TimingVote] = None,
    shadow_tag: str = "v2",
) -> FusionDecision:
    """
    Deterministic fusion policy v1 (authoritative) with optional shadow vote for logging only.

    Inputs:
      - intent_1m_raw: BUY/SELL/HOLD
      - vote: TimingVote(direction in {long, short, none}, strength in [0,1], seed_id optional) [AUTHORITATIVE]
      - allow_long / allow_short: 0 or 1 (gate flags)
      - thresh: confirmation threshold (default 0.60)
      - shadow_vote: optional TimingVote for comparison only (NEVER affects result)
      - shadow_tag: label for the shadow vote (default "v2")

    Output:
      - FusionDecision(intent_final, reason_code, ... context fields + optional shadow context)
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

    # sanitize shadow vote (do not affect anything)
    sv_dir: Optional[VoteDir] = None
    sv_str: Optional[float] = None
    sv_seed: Optional[str] = None
    sv_tag: Optional[str] = None

    if shadow_vote is not None:
        sv_dir = shadow_vote.direction
        try:
            x = float(shadow_vote.strength)
        except Exception:
            x = 0.0
        if x < 0.0:
            x = 0.0
        if x > 1.0:
            x = 1.0
        sv_str = x
        sv_seed = shadow_vote.seed_id
        sv_tag = str(shadow_tag) if shadow_tag else "v2"

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
            shadow_vote_direction=sv_dir,
            shadow_vote_strength=sv_str,
            shadow_vote_seed_id=sv_seed,
            shadow_tag=sv_tag,
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
            shadow_vote_direction=sv_dir,
            shadow_vote_strength=sv_str,
            shadow_vote_seed_id=sv_seed,
            shadow_tag=sv_tag,
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
            shadow_vote_direction=sv_dir,
            shadow_vote_strength=sv_str,
            shadow_vote_seed_id=sv_seed,
            shadow_tag=sv_tag,
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
            shadow_vote_direction=sv_dir,
            shadow_vote_strength=sv_str,
            shadow_vote_seed_id=sv_seed,
            shadow_tag=sv_tag,
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
        shadow_vote_direction=sv_dir,
        shadow_vote_strength=sv_str,
        shadow_vote_seed_id=sv_seed,
        shadow_tag=sv_tag,
    )


def format_timing_compare_log(dec: FusionDecision) -> str:
    """
    Build an ASCII-only one-line compare string for logs.

    This is purely a helper; the caller decides whether to emit it.
    """
    if dec.shadow_vote_direction is None:
        return "timing_compare shadow=none"

    return (
        "timing_compare "
        "v1_dir=%s v1_strength=%.6f v1_seed=%s "
        "%s_dir=%s %s_strength=%.6f %s_seed=%s"
        % (
            dec.vote_5m_direction,
            float(dec.vote_5m_strength),
            str(dec.vote_5m_seed_id),
            str(dec.shadow_tag),
            str(dec.shadow_vote_direction),
            str(dec.shadow_tag),
            float(dec.shadow_vote_strength if dec.shadow_vote_strength is not None else 0.0),
            str(dec.shadow_tag),
            str(dec.shadow_vote_seed_id),
        )
    )


def _demo() -> None:
    # Simple deterministic smoke checks (prints only)
    cases = [
        ("HOLD", TimingVote("long", 1.0, "X"), TimingVote("short", 1.0, "Y"), 1, 1),
        ("BUY", TimingVote("none", 1.0, "X"), TimingVote("long", 1.0, "Y"), 1, 1),
        ("BUY", TimingVote("short", 1.0, "X"), TimingVote("long", 1.0, "Y"), 1, 1),
        ("BUY", TimingVote("long", 0.59, "X"), TimingVote("long", 1.0, "Y"), 1, 1),
        ("BUY", TimingVote("long", 0.60, "X"), TimingVote("long", 1.0, "Y"), 1, 1),
        ("SELL", TimingVote("long", 1.0, "X"), TimingVote("short", 1.0, "Y"), 1, 1),
        ("SELL", TimingVote("short", 0.60, "X"), TimingVote("short", 1.0, "Y"), 1, 1),
        ("SELL", TimingVote("short", 0.60, "X"), TimingVote("short", 1.0, "Y"), 1, 0),
    ]
    for intent, vote1, vote2, al, ash in cases:
        d = merge_intent_with_5m_vote(intent, vote1, al, ash, thresh=0.60, shadow_vote=vote2, shadow_tag="v2")
        print(
            "intent_1m_raw=%s v1=(%s,%.2f) v2=(%s,%.2f) allow_long=%d allow_short=%d -> intent_final=%s reason=%s | %s"
            % (
                d.intent_1m_raw,
                d.vote_5m_direction,
                d.vote_5m_strength,
                str(d.shadow_vote_direction),
                float(d.shadow_vote_strength if d.shadow_vote_strength is not None else 0.0),
                d.allow_long,
                d.allow_short,
                d.intent_final,
                d.reason_code,
                format_timing_compare_log(d),
            )
        )


if __name__ == "__main__":
    _demo()

