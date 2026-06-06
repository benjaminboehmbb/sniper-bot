#!/usr/bin/env python3
# P35 Timing Bias Regression Audit
# ASCII-only.

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from live_l1.core.timing_5m import compute_5m_timing_vote

V1 = Path("seeds/5m/btcusdt_5m_long_timing_core_v1.csv")
V2 = Path("seeds/5m/btcusdt_5m_timing_core_v2.csv")
DOC = Path("docs/review/P35_TIMING_BIAS_REGRESSION_AUDIT_2026-06-06.md")


def check_seed(path: Path) -> tuple[str, float, str]:
    vote = compute_5m_timing_vote(
        seeds_csv=str(path),
        price=100.0,
        rsi_signal=1,
        stoch_signal=1,
        thresh=0.6,
    )
    return vote.direction, float(vote.strength), str(vote.seed_id)


def main() -> int:
    if not V1.exists():
        print("ERROR: missing v1 seed:", V1)
        return 1

    if not V2.exists():
        print("ERROR: missing v2 seed:", V2)
        return 1

    v1_direction, v1_strength, v1_seed_id = check_seed(V1)
    v2_direction, v2_strength, v2_seed_id = check_seed(V2)

    v1_pass = v1_direction == "none"
    v2_pass = v2_direction == "long"

    status = "PASS" if v1_pass and v2_pass else "FAIL"

    DOC.parent.mkdir(parents=True, exist_ok=True)

    with DOC.open("w", encoding="utf-8") as out:
        out.write("# P35 TIMING BIAS REGRESSION AUDIT\n\n")
        out.write("Date: 2026-06-06\n")
        out.write("Device: G15 / AR15\n")
        out.write("Environment: WSL\n\n")

        out.write("## Objective\n\n")
        out.write("Validate that strict 5m timing direction handling removed the implicit long fallback.\n\n")

        out.write("## Test Inputs\n\n")
        out.write(f"v1_seed: {V1}\n\n")
        out.write(f"v2_seed: {V2}\n\n")

        out.write("## Results\n\n")
        out.write(f"v1_direction: {v1_direction}\n\n")
        out.write(f"v1_strength: {v1_strength}\n\n")
        out.write(f"v1_seed_id: {v1_seed_id}\n\n")
        out.write(f"v1_expected: none\n\n")
        out.write(f"v1_result: {'PASS' if v1_pass else 'FAIL'}\n\n")

        out.write(f"v2_direction: {v2_direction}\n\n")
        out.write(f"v2_strength: {v2_strength}\n\n")
        out.write(f"v2_seed_id: {v2_seed_id}\n\n")
        out.write(f"v2_expected: long\n\n")
        out.write(f"v2_result: {'PASS' if v2_pass else 'FAIL'}\n\n")

        out.write("## Interpretation\n\n")
        if status == "PASS":
            out.write("The old v1 seed file no longer becomes long implicitly.\n\n")
            out.write("The new v2 seed file with explicit direction=long still works.\n\n")
        else:
            out.write("Regression audit failed. Do not proceed to runtime validation.\n\n")

        out.write("## Result\n\n")
        out.write(f"Status: {status}\n")

    print("P35 TIMING BIAS REGRESSION AUDIT")
    print("v1_direction:", v1_direction)
    print("v1_expected: none")
    print("v1_result:", "PASS" if v1_pass else "FAIL")
    print("v2_direction:", v2_direction)
    print("v2_expected: long")
    print("v2_result:", "PASS" if v2_pass else "FAIL")
    print("doc_out:", DOC)
    print("RESULT:", status)

    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
