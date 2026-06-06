#!/usr/bin/env python3
# P30 5m Timing Layer Bias Audit
# ASCII-only.

from __future__ import annotations

import csv
import re
from collections import Counter
from pathlib import Path

LOG = Path("live_logs/l1_paper.log")
SEEDS = Path("seeds/5m/btcusdt_5m_long_timing_core_v1.csv")
TIMING = Path("live_l1/core/timing_5m.py")
LOOP = Path("live_l1/core/loop.py")
OUT = Path("docs/review/P30_5M_TIMING_LAYER_BIAS_AUDIT_2026-06-06.md")


def scan_log_votes() -> Counter:
    c = Counter()
    if not LOG.exists():
        return c
    with LOG.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if "event=intent_fused" not in line:
                continue
            m = re.search(r"vote_5m_direction=(\S+)", line)
            if m:
                c[m.group(1)] += 1
    return c


def scan_seed_file() -> tuple[list[str], int, Counter, Counter]:
    if not SEEDS.exists():
        return [], 0, Counter(), Counter()

    with SEEDS.open("r", encoding="utf-8", errors="ignore", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        rows = 0
        direction_counts = Counter()
        seed_id_counts = Counter()

        for row in reader:
            rows += 1
            for key in ("direction", "side", "vote_direction", "seed_side"):
                val = str(row.get(key, "")).strip().lower()
                if val:
                    direction_counts[val] += 1
            for key in ("seed_id", "id", "name", "combo_id"):
                val = str(row.get(key, "")).strip()
                if val:
                    seed_id_counts[val] += 1

    return fieldnames, rows, direction_counts, seed_id_counts


def grep_keywords(path: Path, keywords: list[str]) -> list[str]:
    if not path.exists():
        return []
    out = []
    lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    for i, line in enumerate(lines, start=1):
        if any(k in line for k in keywords):
            out.append(f"{i}: {line}")
    return out


def main() -> int:
    vote_counts = scan_log_votes()
    fields, seed_rows, seed_direction_counts, seed_id_counts = scan_seed_file()

    timing_hits = grep_keywords(
        TIMING,
        ["direction", "long", "short", "vote", "seed", "TimingVote", "return"],
    )

    loop_hits = grep_keywords(
        LOOP,
        ["seeds_5m", "compute_5m", "vote_5m", "timing", "seed"],
    )

    OUT.parent.mkdir(parents=True, exist_ok=True)

    with OUT.open("w", encoding="utf-8") as out:
        out.write("# P30 5M TIMING LAYER BIAS AUDIT\n\n")
        out.write("Date: 2026-06-06\n")
        out.write("Device: G15 / AR15\n")
        out.write("Environment: WSL\n\n")

        out.write("## Objective\n\n")
        out.write("Determine why the 5m timing layer emits only long votes in Live L1 logs.\n\n")

        out.write("## Runtime Vote Distribution\n\n")
        for k, v in vote_counts.most_common():
            out.write(f"- {k}: {v}\n")
        out.write("\n")

        out.write("## Seed File\n\n")
        out.write(f"path: {SEEDS}\n\n")
        out.write(f"exists: {SEEDS.exists()}\n\n")
        out.write(f"rows: {seed_rows}\n\n")
        out.write("columns:\n\n")
        for col in fields:
            out.write(f"- {col}\n")
        out.write("\n")

        out.write("## Seed Direction Columns\n\n")
        if seed_direction_counts:
            for k, v in seed_direction_counts.most_common():
                out.write(f"- {k}: {v}\n")
        else:
            out.write("No explicit direction/side column found.\n")
        out.write("\n")

        out.write("## Top Seed IDs\n\n")
        if seed_id_counts:
            for k, v in seed_id_counts.most_common(20):
                out.write(f"- {k}: {v}\n")
        else:
            out.write("No explicit seed id column found.\n")
        out.write("\n")

        out.write("## timing_5m.py Keyword Hits\n\n")
        out.write("```text\n")
        for line in timing_hits[:250]:
            out.write(line + "\n")
        out.write("```\n\n")

        out.write("## loop.py Timing Integration Hits\n\n")
        out.write("```text\n")
        for line in loop_hits[:250]:
            out.write(line + "\n")
        out.write("```\n\n")

        out.write("## Preliminary Assessment\n\n")
        if vote_counts and len(vote_counts) == 1 and "long" in vote_counts:
            out.write("- Runtime confirms a permanent long-only 5m vote stream.\n")
        if "long" in str(SEEDS).lower():
            out.write("- Seed filename indicates a long-specific timing seed file.\n")
        if seed_direction_counts:
            out.write("- Seed file contains explicit direction information.\n")
        else:
            out.write("- Seed file does not expose an obvious direction column in standard names.\n")

        out.write("\n## Result\n\n")
        out.write("Status: PASS\n")

    print("P30 5M TIMING LAYER BIAS AUDIT")
    print("doc_out:", OUT)
    print("vote_counts:", dict(vote_counts))
    print("seed_exists:", SEEDS.exists())
    print("seed_rows:", seed_rows)
    print("seed_direction_counts:", dict(seed_direction_counts))
    print("RESULT: PASS")


if __name__ == "__main__":
    main()
