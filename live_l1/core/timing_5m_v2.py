# live_l1/core/timing_5m_v2.py
#
# L1-D: 5m Timing Core v2
# Step 3: History-based candle evaluation (last N candles).
#
# No execution.
# No side effects.
# Deterministic.

from __future__ import annotations

from typing import List, Optional, Literal, Dict
from dataclasses import dataclass


VoteDir = Literal["long", "short", "none"]


# ----------------------------
# Data Structures
# ----------------------------

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


# ----------------------------
# Core API
# ----------------------------

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

    # Use only last N candles
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

    # Decide
    if best_long_score < thresh and best_short_score < thresh:
        return TimingVote(direction="none", strength=max(best_long_score, best_short_score), seed_id=None)

    if best_long_score >= thresh and best_long_score > best_short_score:
        return TimingVote(direction="long", strength=best_long_score, seed_id=best_long_seed)

    if best_short_score >= thresh and best_short_score > best_long_score:
        return TimingVote(direction="short", strength=best_short_score, seed_id=best_short_seed)

    return TimingVote(direction="none", strength=max(best_long_score, best_short_score), seed_id=None)


# ----------------------------
# Seed Evaluation v3 (history-based)
# ----------------------------

def _evaluate_seed_on_window(seed: GSSpec, window: List[Candle5m]) -> float:
    """
    History-based scoring on last N 5m candles.

    Logic:
        - base_weight = sum(abs(weights))
        - for each candle:
            +1 if close > open
            -1 if close < open
             0 if equal
        - avg_signal = mean(candle_signals)
        - raw_score = base_weight * avg_signal
        - final_score = clamp(abs(raw_score), 0, 1)
    """

    if not seed.weights or not window:
        return 0.0

    base_weight = 0.0
    for _, w in seed.weights.items():
        try:
            base_weight += abs(float(w))
        except Exception:
            continue

    if base_weight <= 0.0:
        return 0.0

    # Aggregate candle signals
    s = 0.0
    for c in window:
        if c.close > c.open:
            s += 1.0
        elif c.close < c.open:
            s -= 1.0
        else:
            s += 0.0

    avg_signal = s / float(len(window))

    raw_score = base_weight * avg_signal

    score = abs(raw_score)
    if score > 1.0:
        score = 1.0

    return float(score)


