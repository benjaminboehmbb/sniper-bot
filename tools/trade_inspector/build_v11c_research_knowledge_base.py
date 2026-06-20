#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path

from tools.trade_inspector.common.io import read_csv, write_csv
from tools.trade_inspector.common.utils import now_utc as now



def status(score, blocked, pending):
    if blocked > 0:
        return "BLOCKED"
    if pending > 0:
        return "PENDING"
    if score >= 3:
        return "STRONG_EVIDENCE"
    if score >= 1:
        return "MODERATE_EVIDENCE"
    if score <= -1:
        return "WEAK_EVIDENCE"
    return "UNKNOWN"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--v11b-csv", required=True)
    p.add_argument("--out-dir", required=True)
    args = p.parse_args()

    rows = read_csv(args.v11b_csv)

    kb = defaultdict(lambda: {
        "score": 0,
        "pass": 0,
        "fail": 0,
        "pending": 0,
        "blocked": 0,
        "updates": 0
    })

    for r in rows:
        h = r["hypothesis_id"]
        action = r["evidence_update_action"]

        kb[h]["updates"] += 1

        if action == "INCREASE_CONFIDENCE":
            kb[h]["score"] += 1
            kb[h]["pass"] += 1

        elif action == "DECREASE_CONFIDENCE":
            kb[h]["score"] -= 1
            kb[h]["fail"] += 1

        elif action == "KEEP_PENDING":
            kb[h]["pending"] += 1

        elif action in (
            "TECHNICAL_REMEDIATION_REQUIRED",
            "BLOCK_FROM_LEARNING"
        ):
            kb[h]["blocked"] += 1

    out = []

    for r in rows:
        h = r["hypothesis_id"]
        x = kb[h]

        out.append({
            "hypothesis_id": h,
            "hypothesis_group": r["hypothesis_group"],
            "knowledge_score": x["score"],
            "successful_validations": x["pass"],
            "failed_validations": x["fail"],
            "pending_validations": x["pending"],
            "blocked_events": x["blocked"],
            "knowledge_updates": x["updates"],
            "research_status": status(
                x["score"],
                x["blocked"],
                x["pending"]
            ),
            "updated_at_utc": now()
        })

    unique = []
    seen = set()

    for r in out:
        if r["hypothesis_id"] not in seen:
            unique.append(r)
            seen.add(r["hypothesis_id"])

    outdir = Path(args.out_dir)
    outdir.mkdir(parents=True, exist_ok=True)

    csv_file = outdir / "v11c_research_knowledge_base.csv"
    write_csv(csv_file, unique, ['hypothesis_id', 'hypothesis_group', 'knowledge_score', 'successful_validations', 'failed_validations', 'pending_validations', 'blocked_events', 'knowledge_updates', 'research_status', 'updated_at_utc'])

    counts = defaultdict(int)
    for r in unique:
        counts[r["research_status"]] += 1

    md = outdir / "V11C_RESEARCH_KNOWLEDGE_BASE_REPORT_2026-06-19.md"

    lines = [
        "# V11C RESEARCH KNOWLEDGE BASE REPORT",
        "",
        "## Summary",
        ""
    ]

    for k in sorted(counts):
        lines.append(f"- {k}: {counts[k]}")

    lines += [
        "",
        f"Hypotheses: {len(unique)}",
        "",
        "Generated files",
        "",
        "- v11c_research_knowledge_base.csv",
        "- V11C_RESEARCH_KNOWLEDGE_BASE_REPORT_2026-06-19.md"
    ]

    md.write_text("\n".join(lines), encoding="utf-8")

    print("V11C research knowledge base completed")
    print("input_rows:", len(rows))
    print("knowledge_entries:", len(unique))
    print("report:", md)
    print("csv:", csv_file)


if __name__ == "__main__":
    main()
