# live_l1/core/timing_5m_v2.py
#
# L1-D: 5m Timing Core v2
# Step 4: Trend vs. Mean-Reversion scoring on last N candles.
#
# No execution.
# No side effects.
# Deterministic.

from __future__ import annotations

from typing import List, Optional, Literal, Dict
from dataclasses import dataclass


VoteDir = Literal["long", "short", "none"]


@dataclass(frozen=True)
class TimingVote:
    direction: VoteDir
    strength: float
    seed_id: Optional[str] = None


@dataclass(frozen=True)
class Candle5m:
    ts_open_utc: str
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass(frozen=True)
class GSSpec:
    seed_id: str
    direction: Literal["long", "short"]
    weights: Dict[str, float]


def compute_5m_timing_vote_v2(
    repo_root: str,
    symbol: str,
    now_utc: str,
    candles_5m: List[Candle5m],
    seeds: List[GSSpec],
    thresh: float,
    history_len: int = 3,
) -> TimingVote:

    if not candles_5m or not seeds:
        return TimingVote(direction="none", strength=0.0, seed_id=None)

    if history_len < 1:
        history_len = 1

    window = candles_5m[-history_len:]

    best_long_score: float = 0.0
    best_short_score: float = 0.0
    best_long_seed: Optional[str] = None
    best_short_seed: Optional[str] = None

    for seed in seeds:
        score = _evaluate_seed_on_window(seed, window)

        if seed.direction == "long":
            if score > best_long_score:
                best_long_score = score
                best_long_seed = seed.seed_id
        elif seed.direction == "short":
            if score > best_short_score:
                best_short_score = score
                best_short_seed = seed.seed_id

    if best_long_score < thresh and best_short_score < thresh:
        return TimingVote(direction="none", strength=max(best_long_score, best_short_score), seed_id=None)

    if best_long_score >= thresh and best_long_score > best_short_score:
        return TimingVote(direction="long", strength=best_long_score, seed_id=best_long_seed)

    if best_short_score >= thresh and best_short_score > best_long_score:
        return TimingVote(direction="short", strength=best_short_score, seed_id=best_short_seed)

    return TimingVote(direction="none", strength=max(best_long_score, best_short_score), seed_id=None)


def _evaluate_seed_on_window(seed: GSSpec, window: List[Candle5m]) -> float:
    """
    Trend vs mean-reversion on last N candles.

    We compute two components:
      - trend_strength: fraction of candles in direction of majority (0..1)
      - reversal_strength: 1 if last candle is opposite to majority else 0

    Then we combine into a single score using seed weights:
      - if seed contains key "trend": use it as weight for trend component
      - if seed contains key "reversal": use it as weight for reversal component
      - otherwise fall back to sum(abs(weights)) as base weight

    This is still a placeholder model, but now it distinguishes trend vs reversal.
    """

    if not window:
        return 0.0

    # Determine candle signs: +1 bull, -1 bear, 0 flat
    signs: List[int] = []
    for c in window:
        if c.close > c.open:
            signs.append(1)
        elif c.close < c.open:
            signs.append(-1)
        else:
            signs.append(0)

    # Majority direction (ignore zeros)
    pos = sum(1 for s in signs if s == 1)
    neg = sum(1 for s in signs if s == -1)

    if pos == 0 and neg == 0:
        majority = 0
    elif pos >= neg:
        majority = 1
    else:
        majority = -1

    # Trend strength: fraction aligned with majority, ignoring zeros
    denom = pos + neg
    if denom == 0 or majority == 0:
        trend_strength = 0.0
    else:
        aligned = pos if majority == 1 else neg
        trend_strength = aligned / float(denom)

    # Reversal strength: last candle opposite to majority
    last = signs[-1]
    if majority != 0 and last != 0 and last == -majority:
        reversal_strength = 1.0
    else:
        reversal_strength = 0.0

    # Base weights
    w_trend = float(seed.weights.get("trend", 0.0)) if seed.weights else 0.0
    w_reversal = float(seed.weights.get("reversal", 0.0)) if seed.weights else 0.0

    if w_trend == 0.0 and w_reversal == 0.0:
        # fallback: sum abs weights
        base = 0.0
        if seed.weights:
            for _, w in seed.weights.items():
                try:
                    base += abs(float(w))
                except Exception:
                    continue
        # Use base as trend weight (conservative)
        w_trend = base
        w_reversal = 0.0

    raw = abs(w_trend) * trend_strength + abs(w_reversal) * reversal_strength

    # Normalize to [0,1]
    if raw > 1.0:
        raw = 1.0
    if raw < 0.0:
        raw = 0.0

    return float(raw)



