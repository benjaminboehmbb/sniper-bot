#!/usr/bin/env python3
# P41 Isolated Timing Short-Seed Test
# ASCII-only.

from __future__ import annotations

from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from live_l1.core.timing_5m import compute_5m_timing_vote

SEED_V2 = Path("seeds/5m/btcusdt_5m_timing_core_v2.csv")
DOC = Path("docs/review/P41_ISOLATED_TIMING_SHORT_SEED_TEST_2026-06-06.md")


def run_vote(seed_csv: Path, rsi_signal: int, stoch_signal: int):
    return compute_5m_timing_vote(
        seeds_csv=str(seed_csv),
        price=100.0,
        rsi_signal=rsi_signal,
        stoch_signal=stoch_signal,
        thresh=0.6,
    )


def main() -> int:
    if not SEED_V2.exists():
        print("ERROR: missing seed file:", SEED_V2)
        return 1

    cases = []

    vote_long = run_vote(SEED_V2, 1, 1)
    cases.append(("positive_signals", vote_long.direction, vote_long.strength, vote_long.seed_id))

    vote_short = run_vote(SEED_V2, -1, -1)
    cases.append(("negative_signals", vote_short.direction, vote_short.strength, vote_short.seed_id))

    vote_mixed = run_vote(SEED_V2, 1, -1)
    cases.append(("mixed_signals", vote_mixed.direction, vote_mixed.strength, vote_mixed.seed_id))

    expected = {
        "positive_signals": "long",
        "negative_signals": "short",
    }

    failures = []

    for name, direction, strength, seed_id in cases:
        exp = expected.get(name)
        if exp is not None and direction != exp:
            failures.append(f"{name}: expected {exp}, got {direction}")

    status = "PASS" if not failures else "FAIL"

    DOC.parent.mkdir(parents=True, exist_ok=True)

    with DOC.open("w", encoding="utf-8") as out:
        out.write("# P41 ISOLATED TIMING SHORT-SEED TEST\n\n")
        out.write("Date: 2026-06-06\n")
        out.write("Device: G15 / AR15\n")
        out.write("Environment: WSL\n\n")

        out.write("## Objective\n\n")
        out.write("Validate that the v2 5m timing seed file can emit both long and short votes in isolated timing tests.\n\n")

        out.write("## Seed File\n\n")
        out.write(f"{SEED_V2}\n\n")

        out.write("## Test Cases\n\n")
        for name, direction, strength, seed_id in cases:
            out.write(f"### {name}\n\n")
            out.write(f"direction: {direction}\n\n")
            out.write(f"strength: {strength}\n\n")
            out.write(f"seed_id: {seed_id}\n\n")

        out.write("## Failures\n\n")
        if failures:
            for item in failures:
                out.write(f"- {item}\n")
        else:
            out.write("none\n")
        out.write("\n")

        out.write("## Result\n\n")
        out.write(f"Status: {status}\n")

    print("P41 ISOLATED TIMING SHORT-SEED TEST")
    for name, direction, strength, seed_id in cases:
        print(name + ":", "direction=" + str(direction), "strength=" + str(strength), "seed_id=" + str(seed_id))
    if failures:
        for item in failures:
            print("FAIL:", item)
    print("doc_out:", DOC)
    print("RESULT:", status)

    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
