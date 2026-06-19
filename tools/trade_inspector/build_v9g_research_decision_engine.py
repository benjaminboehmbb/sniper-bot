#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Trade Inspector V9G

Research Decision Engine

ASCII only.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


def read_csv(path: Path):
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def write_csv(path: Path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)

    if not rows:
        path.write_text("", encoding="utf-8")
        return

    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def fnum(value):
    try:
        return float(value)
    except Exception:
        return 0.0


def decide(row):
    portfolio_class = row.get("portfolio_class", "")
    portfolio_score = fnum(row.get("portfolio_score"))
    conflict_penalty = fnum(row.get("conflict_penalty"))

    if portfolio_class == "PRIORITY_1" and conflict_penalty <= 10 and portfolio_score >= 80:
        return (
            "RUN_CONTROLLED_VALIDATION",
            "highest priority candidate with acceptable conflict penalty",
            1,
        )

    if portfolio_class in {"PRIORITY_1", "PRIORITY_2"} and conflict_penalty <= 20:
        return (
            "PREPARE_VALIDATION_DESIGN",
            "candidate should be prepared for controlled validation design",
            2,
        )

    if portfolio_class == "WATCHLIST":
        return (
            "COLLECT_MORE_ARCHIVES",
            "candidate needs more observations before validation",
            3,
        )

    if portfolio_class == "REJECT":
        return (
            "REJECT_FOR_NOW",
            "candidate should not consume validation effort now",
            5,
        )

    return (
        "KEEP_ON_WATCHLIST",
        "candidate remains unresolved",
        4,
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--v9f-csv", required=True)
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()

    v9f_csv = Path(args.v9f_csv)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = read_csv(v9f_csv)

    decisions = []

    for row in rows:
        decision, reason, priority_rank = decide(row)

        decisions.append(
            {
                "hypothesis_id": row.get("hypothesis_id", ""),
                "group": row.get("group", ""),
                "portfolio_score": row.get("portfolio_score", ""),
                "portfolio_class": row.get("portfolio_class", ""),
                "conflict_penalty": row.get("conflict_penalty", ""),
                "research_decision": decision,
                "decision_reason": reason,
                "priority_rank": priority_rank,
            }
        )

    decisions.sort(
        key=lambda r: (
            int(r["priority_rank"]),
            -fnum(r["portfolio_score"]),
        )
    )

    out_csv = out_dir / "v9g_research_decisions.csv"
    write_csv(out_csv, decisions)

    counts = {}
    for row in decisions:
        key = row["research_decision"]
        counts[key] = counts.get(key, 0) + 1

    report = out_dir / "V9G_RESEARCH_DECISION_REPORT_2026-06-18.md"

    with report.open("w", encoding="utf-8") as fh:
        fh.write("# V9G RESEARCH DECISION REPORT\n\n")

        fh.write("Date: 2026-06-18\n")
        fh.write("Device: G15 / AR15\n")
        fh.write("Environment: WSL\n")
        fh.write("Scope: Trade Inspector V9G\n\n")

        fh.write("## Objective\n\n")
        fh.write("Convert the optimized V9F experiment portfolio into concrete research decisions.\n\n")

        fh.write("## Decision Summary\n\n")
        for key in (
            "RUN_CONTROLLED_VALIDATION",
            "PREPARE_VALIDATION_DESIGN",
            "COLLECT_MORE_ARCHIVES",
            "KEEP_ON_WATCHLIST",
            "REJECT_FOR_NOW",
        ):
            fh.write(f"- {key}: {counts.get(key, 0)}\n")

        fh.write("\n## Top Decisions\n\n")
        fh.write("|Rank|Hypothesis|Portfolio Score|Decision|Reason|\n")
        fh.write("|---:|---|---:|---|---|\n")

        for i, row in enumerate(decisions[:20], 1):
            fh.write(
                f"|{i}|{row['group']}|{row['portfolio_score']}|"
                f"{row['research_decision']}|{row['decision_reason']}|\n"
            )

        fh.write("\n## Interpretation\n\n")
        fh.write("- RUN_CONTROLLED_VALIDATION means the hypothesis is ready for a controlled validation run design.\n")
        fh.write("- PREPARE_VALIDATION_DESIGN means the hypothesis is promising but needs a validation specification first.\n")
        fh.write("- COLLECT_MORE_ARCHIVES means more evidence is needed before validation.\n")
        fh.write("- REJECT_FOR_NOW means the hypothesis should not consume effort now.\n\n")

        fh.write("## Guardrail\n\n")
        fh.write("V9G does not modify trading logic. It only produces research decisions.\n")

    print("V9G research decision engine completed")
    print("input:", len(rows))
    print("decisions:", len(decisions))
    print("report:", report)
    print("csv:", out_csv)


if __name__ == "__main__":
    main()

