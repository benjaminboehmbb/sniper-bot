#!/usr/bin/env python3
# P32 5m Timing Seed v2 Creation
# ASCII-only.

from __future__ import annotations

import csv
from pathlib import Path

SRC = Path("seeds/5m/btcusdt_5m_long_timing_core_v1.csv")
OUT = Path("seeds/5m/btcusdt_5m_timing_core_v2.csv")
DOC = Path("docs/review/P32_5M_TIMING_SEED_V2_CREATION_2026-06-06.md")


def main() -> int:
    if not SRC.exists():
        print("ERROR: source seed file missing:", SRC)
        return 1

    rows = []

    with SRC.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)

        required = {"seed_id", "comb_json"}
        missing = required - set(reader.fieldnames or [])

        if missing:
            print("ERROR: missing columns:", sorted(missing))
            return 1

        for row in reader:
            seed_id = str(row.get("seed_id", "")).strip()
            comb_json = str(row.get("comb_json", "")).strip()

            if not seed_id or not comb_json:
                continue

            rows.append({
                "seed_id": seed_id,
                "direction": "long",
                "comb_json": comb_json,
            })

    OUT.parent.mkdir(parents=True, exist_ok=True)

    with OUT.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["seed_id", "direction", "comb_json"])
        writer.writeheader()
        writer.writerows(rows)

    DOC.parent.mkdir(parents=True, exist_ok=True)

    with DOC.open("w", encoding="utf-8") as out:
        out.write("# P32 5M TIMING SEED V2 CREATION\n\n")
        out.write("Date: 2026-06-06\n")
        out.write("Device: G15 / AR15\n")
        out.write("Environment: WSL\n\n")

        out.write("## Objective\n\n")
        out.write("Create a v2 5m timing seed file with explicit direction column.\n\n")

        out.write("## Source\n\n")
        out.write(f"{SRC}\n\n")

        out.write("## Output\n\n")
        out.write(f"{OUT}\n\n")

        out.write("## Schema\n\n")
        out.write("- seed_id\n")
        out.write("- direction\n")
        out.write("- comb_json\n\n")

        out.write("## Direction Assignment\n\n")
        out.write("All legacy v1 seeds are assigned direction=long.\n\n")
        out.write("Reason:\n\n")
        out.write("The source file is explicitly named as a long timing core seed file.\n\n")

        out.write("## Rows Created\n\n")
        out.write(f"{len(rows)}\n\n")

        out.write("## Limitation\n\n")
        out.write("This v2 seed file does not yet add short seeds.\n\n")
        out.write("It only removes the implicit long default by making long direction explicit.\n\n")

        out.write("## Result\n\n")
        out.write("Status: PASS\n")

    print("P32 5M TIMING SEED V2 CREATION")
    print("source:", SRC)
    print("out:", OUT)
    print("rows:", len(rows))
    print("doc:", DOC)
    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
