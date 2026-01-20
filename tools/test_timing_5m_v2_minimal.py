# tools/test_timing_5m_v2_minimal.py
#
# Minimal isolated test for timing_5m_v2.py
# With explicit sys.path fix for repo-root imports.
# ASCII-only.

import os
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from live_l1.core.timing_5m_v2 import (
    compute_5m_timing_vote_v2,
    Candle5m,
    GSSpec,
)


def make_dummy_candle(open_p: float, close_p: float) -> Candle5m:
    return Candle5m(
        ts_open_utc="2026-01-20T12:00:00Z",
        open=float(open_p),
        high=max(float(open_p), float(close_p)),
        low=min(float(open_p), float(close_p)),
        close=float(close_p),
        volume=123.0,
    )


def test_long_wins_on_bull_candle():
    candle = make_dummy_candle(100.0, 102.0)  # bull candle

    seeds = [
        GSSpec(seed_id="L1", direction="long", weights={"a": 0.8, "b": 0.7}),
        GSSpec(seed_id="S1", direction="short", weights={"a": 0.2}),
    ]

    vote = compute_5m_timing_vote_v2(
        repo_root=".",
        symbol="BTCUSDT",
        now_utc="2026-01-20T12:05:00Z",
        candles_5m=[candle, candle, candle],
        seeds=seeds,
        thresh=0.5,
    )

    print("LONG TEST:", vote)
    assert vote.direction == "long"
    assert vote.seed_id == "L1"
    assert vote.strength >= 0.5


def test_short_wins_on_bear_candle():
    candle = make_dummy_candle(102.0, 100.0)  # bear candle

    seeds = [
        GSSpec(seed_id="L1", direction="long", weights={"a": 0.2}),
        GSSpec(seed_id="S1", direction="short", weights={"a": 0.9, "b": 0.6}),
    ]

    vote = compute_5m_timing_vote_v2(
        repo_root=".",
        symbol="BTCUSDT",
        now_utc="2026-01-20T12:05:00Z",
        candles_5m=[candle, candle, candle],
        seeds=seeds,
        thresh=0.5,
    )

    print("SHORT TEST:", vote)
    assert vote.direction == "short"
    assert vote.seed_id == "S1"
    assert vote.strength >= 0.5


def test_none_when_flat_candle():
    candle = make_dummy_candle(100.0, 100.0)  # flat candle

    seeds = [
        GSSpec(seed_id="L1", direction="long", weights={"a": 0.9}),
        GSSpec(seed_id="S1", direction="short", weights={"a": 0.9}),
    ]

    vote = compute_5m_timing_vote_v2(
        repo_root=".",
        symbol="BTCUSDT",
        now_utc="2026-01-20T12:05:00Z",
        candles_5m=[candle, candle, candle],
        seeds=seeds,
        thresh=0.5,
    )

    print("NONE TEST:", vote)
    assert vote.direction == "none"
    assert vote.seed_id is None
    assert vote.strength >= 0.0


if __name__ == "__main__":
    test_long_wins_on_bull_candle()
    test_short_wins_on_bear_candle()
    test_none_when_flat_candle()
    print("[OK] timing_5m_v2 minimal tests passed.")



