#!/usr/bin/env python3
# P34 strict timing direction test.
# ASCII-only.

from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from live_l1.core.timing_5m import compute_5m_timing_vote


def write_seed(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def run_case(name: str, seed_csv: str, expected_direction: str) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "seeds.csv"
        write_seed(p, seed_csv)

        vote = compute_5m_timing_vote(
            seeds_csv=str(p),
            price=100.0,
            rsi_signal=1,
            stoch_signal=1,
            thresh=0.6,
        )

        actual = vote.direction
        if actual != expected_direction:
            raise AssertionError(
                name + " expected " + expected_direction + " got " + actual
            )

        print("PASS:", name, "direction=" + actual)


def main() -> int:
    run_case(
        "missing_direction_defaults_none",
        "seed_id,comb_json\nC01,\"{'rsi': 0.8, 'stoch': 0.8}\"\n",
        "none",
    )

    run_case(
        "explicit_long",
        "seed_id,direction,comb_json\nC01,long,\"{'rsi': 0.8, 'stoch': 0.8}\"\n",
        "long",
    )

    run_case(
        "explicit_short",
        "seed_id,direction,comb_json\nS01,short,\"{'rsi': 0.8, 'stoch': 0.8}\"\n",
        "short",
    )

    run_case(
        "invalid_direction_defaults_none",
        "seed_id,direction,comb_json\nX01,invalid,\"{'rsi': 0.8, 'stoch': 0.8}\"\n",
        "none",
    )

    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
