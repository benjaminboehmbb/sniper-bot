#!/usr/bin/env python3
# P44 polarity-aware timing test.
# ASCII-only.

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from live_l1.core.timing_5m import compute_5m_timing_vote

SEED = "seeds/5m/btcusdt_5m_timing_core_v2.csv"


def assert_vote(name: str, expected: str, **signals) -> None:
    vote = compute_5m_timing_vote(
        seeds_csv=SEED,
        price=100.0,
        thresh=0.6,
        **signals,
    )
    if vote.direction != expected:
        raise AssertionError(
            name + " expected " + expected + " got " + vote.direction
        )
    print("PASS:", name, "direction=" + vote.direction, "seed_id=" + str(vote.seed_id))


def main() -> int:
    assert_vote("positive_signals_long", "long", rsi_signal=1, stoch_signal=1)
    assert_vote("negative_signals_short", "short", rsi_signal=-1, stoch_signal=-1)
    assert_vote("mixed_signals_none", "none", rsi_signal=1, stoch_signal=-1)
    assert_vote("missing_signal_none", "none", rsi_signal=1)
    assert_vote("below_threshold_none", "none", rsi_signal=0, stoch_signal=0)

    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
