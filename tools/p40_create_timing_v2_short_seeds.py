#!/usr/bin/env python3
# P40 Create Timing v2 Short Seeds
# ASCII-only.

from __future__ import annotations

import csv
from pathlib import Path

SEED = Path("seeds/5m/btcusdt_5m_timing_core_v2.csv")
DOC = Path("docs/review/P40_CREATE_TIMING_V2_SHORT_SEEDS_2026-06-06.md")

SHORT_ROWS = [
    {
        "seed_id": "S01_rsi_stoch_06",
        "direction": "short",
        "comb_json": "{'rsi': 0.6, 'stoch': 0.6}",
    },
    {
        "seed_id": "S02_rsi_stoch_08",
        "direction": "short",
        "comb_json": "{'rsi': 0.8, 'stoch': 0.8}",
    },
]


def main() -> int:
    if not SEED.exists():
        print("ERROR: missing seed file:", SEED)
        return 1

    with SEED.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames or []
        rows = list(reader)

    required = ["seed_id", "direction", "comb_json"]
    if fields != required:
        print("ERROR: unexpected seed schema:", fields)
        return 1

    existing_ids = {str(r.get("seed_id", "")).strip() for r in rows}

    added = []
    for row in SHORT_ROWS:
        if row["seed_id"] not in existing_ids:
            rows.append(row)
            added.append(row["seed_id"])

    with SEED.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=required)
        writer.writeheader()
        writer.writerows(rows)

    DOC.parent.mkdir(parents=True, exist_ok=True)

    with DOC.open("w", encoding="utf-8") as out:
        out.write("# P40 CREATE TIMING V2 SHORT SEEDS\n\n")
        out.write("Date: 2026-06-06\n")
        out.write("Device: G15 / AR15\n")
        out.write("Environment: WSL\n\n")

        out.write("## Objective\n\n")
        out.write("Add explicit short seeds to the v2 5m timing seed file.\n\n")

        out.write("## Modified File\n\n")
        out.write(f"{SEED}\n\n")

        out.write("## Schema\n\n")
        out.write("- seed_id\n")
        out.write("- direction\n")
        out.write("- comb_json\n\n")

        out.write("## Added Short Seeds\n\n")
        for seed_id in added:
            out.write(f"- {seed_id}\n")
        if not added:
            out.write("- none, already present\n")
        out.write("\n")

        out.write("## Final Rows\n\n")
        out.write(f"{len(rows)}\n\n")

        out.write("## Important Limitation\n\n")
        out.write("This step only adds structural short seed support.\n\n")
        out.write("It does not prove profitability or quality of short timing behavior.\n\n")

        out.write("## Required Next Step\n\n")
        out.write("P41 isolated timing short-seed test.\n\n")

        out.write("## Result\n\n")
        out.write("Status: PASS\n")

    print("P40 CREATE TIMING V2 SHORT SEEDS")
    print("seed:", SEED)
    print("added:", ",".join(added) if added else "none")
    print("rows:", len(rows))
    print("doc:", DOC)
    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
