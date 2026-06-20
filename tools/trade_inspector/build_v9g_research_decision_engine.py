#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Trade Inspector V9G

Research Decision Engine.

Purpose:
- Convert the V9F experiment portfolio into concrete research decisions.
- Preserve full context needed by V10+.
- Avoid reducing hypotheses to only group/score/class.

ASCII only.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from tools.trade_inspector.common.io import read_csv, write_csv
from tools.trade_inspector.common.utils import to_float as fnum


DECISION_FIELDS = [
    "hypothesis_id",
    "legacy_rank_id",
    "group_key",
    "group",
    "observations",
    "consistency_score",
    "consistency_class",
    "stability_class",
    "latest_warning_level",
    "latest_recommended_action",
    "v9d_recommended_action",
    "conflict_penalty",
    "conflict_count",
    "redundancy_count",
    "synergy_count",
    "portfolio_score",
    "portfolio_class",
    "portfolio_reason",
    "research_decision",
    "decision_reason",
    "priority_rank",
    "next_required_input",
    "v10_readiness",
]





def decide(row: dict[str, str]) -> tuple[str, str, int, str, str]:
    portfolio_class = row.get("portfolio_class", "")
    portfolio_score = fnum(row.get("portfolio_score"))
    conflict_penalty = fnum(row.get("conflict_penalty"))
    observations = fnum(row.get("observations"))
    consistency_class = row.get("consistency_class", "")
    stability_class = row.get("stability_class", "")
    warning = row.get("latest_warning_level", "")

    if warning == "HIGH":
        return (
            "REJECT_FOR_NOW",
            "high warning level blocks validation effort",
            5,
            "additional_archives_or_manual_review",
            "NOT_READY",
        )

    if observations < 2:
        return (
            "COLLECT_MORE_ARCHIVES",
            "insufficient cross-archive history for controlled validation",
            3,
            "additional_real_archives",
            "NOT_READY",
        )

    if portfolio_class == "PRIORITY_1" and portfolio_score >= 80 and conflict_penalty <= 10:
        return (
            "RUN_CONTROLLED_VALIDATION",
            "highest priority candidate with stable evidence and acceptable conflict penalty",
            1,
            "v10_validation_plan",
            "READY",
        )

    if portfolio_class in {"PRIORITY_1", "PRIORITY_2"} and conflict_penalty <= 20:
        return (
            "PREPARE_VALIDATION_DESIGN",
            "candidate is promising but should receive explicit validation design before execution",
            2,
            "v10_validation_specification",
            "PARTIAL",
        )

    if portfolio_class == "WATCHLIST":
        return (
            "COLLECT_MORE_ARCHIVES",
            "candidate needs more observations before validation",
            3,
            "additional_real_archives",
            "NOT_READY",
        )

    if consistency_class in {"INCONSISTENT", "REJECT"}:
        return (
            "REJECT_FOR_NOW",
            "consistency evidence does not justify validation effort",
            5,
            "new_evidence_before_reconsideration",
            "NOT_READY",
        )

    if stability_class in {"DECLINING", "UNSTABLE"}:
        return (
            "KEEP_ON_WATCHLIST",
            "stability class does not support immediate validation",
            4,
            "stability_recheck_after_more_archives",
            "NOT_READY",
        )

    if portfolio_class == "REJECT":
        return (
            "REJECT_FOR_NOW",
            "portfolio optimizer rejected the candidate",
            5,
            "new_evidence_before_reconsideration",
            "NOT_READY",
        )

    return (
        "KEEP_ON_WATCHLIST",
        "candidate remains unresolved after portfolio review",
        4,
        "manual_research_review",
        "NOT_READY",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--v9f-csv", required=True)
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()

    v9f_csv = Path(args.v9f_csv)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = read_csv(v9f_csv)

    decisions: list[dict[str, Any]] = []

    for row in rows:
        decision, reason, priority_rank, next_input, readiness = decide(row)

        decisions.append(
            {
                "hypothesis_id": row.get("hypothesis_id", ""),
                "legacy_rank_id": row.get("legacy_rank_id", ""),
                "group_key": row.get("group_key", ""),
                "group": row.get("group", ""),
                "observations": row.get("observations", ""),
                "consistency_score": row.get("consistency_score", ""),
                "consistency_class": row.get("consistency_class", ""),
                "stability_class": row.get("stability_class", ""),
                "latest_warning_level": row.get("latest_warning_level", ""),
                "latest_recommended_action": row.get("latest_recommended_action", ""),
                "v9d_recommended_action": row.get("v9d_recommended_action", ""),
                "conflict_penalty": row.get("conflict_penalty", ""),
                "conflict_count": row.get("conflict_count", ""),
                "redundancy_count": row.get("redundancy_count", ""),
                "synergy_count": row.get("synergy_count", ""),
                "portfolio_score": row.get("portfolio_score", ""),
                "portfolio_class": row.get("portfolio_class", ""),
                "portfolio_reason": row.get("portfolio_reason", ""),
                "research_decision": decision,
                "decision_reason": reason,
                "priority_rank": priority_rank,
                "next_required_input": next_input,
                "v10_readiness": readiness,
            }
        )

    decisions.sort(
        key=lambda r: (
            int(r["priority_rank"]),
            -fnum(r["portfolio_score"]),
            str(r["hypothesis_id"]),
        )
    )

    out_csv = out_dir / "v9g_research_decisions.csv"
    report = out_dir / "V9G_RESEARCH_DECISION_REPORT_2026-06-18.md"

    write_csv(out_csv, decisions, DECISION_FIELDS)

    counts: dict[str, int] = {}
    readiness_counts: dict[str, int] = {}

    for row in decisions:
        decision_key = str(row["research_decision"])
        readiness_key = str(row["v10_readiness"])
        counts[decision_key] = counts.get(decision_key, 0) + 1
        readiness_counts[readiness_key] = readiness_counts.get(readiness_key, 0) + 1

    lines: list[str] = []
    lines.append("# V9G RESEARCH DECISION REPORT")
    lines.append("")
    lines.append("Date: 2026-06-18")
    lines.append("Device: G15 / AR15")
    lines.append("Environment: WSL")
    lines.append("Scope: Trade Inspector V9G")
    lines.append("")
    lines.append("## Objective")
    lines.append("")
    lines.append("Convert the optimized V9F experiment portfolio into concrete research decisions.")
    lines.append("")
    lines.append("## Review Fixes Included")
    lines.append("")
    lines.append("- Preserves hypothesis_id, group_key, consistency, stability, warning and conflict context.")
    lines.append("- Adds next_required_input and v10_readiness for cleaner V9 to V10 handoff.")
    lines.append("- Writes a header-only CSV even when there are no decision rows.")
    lines.append("")
    lines.append("## Decision Summary")
    lines.append("")
    for key in (
        "RUN_CONTROLLED_VALIDATION",
        "PREPARE_VALIDATION_DESIGN",
        "COLLECT_MORE_ARCHIVES",
        "KEEP_ON_WATCHLIST",
        "REJECT_FOR_NOW",
    ):
        lines.append(f"- {key}: {counts.get(key, 0)}")
    lines.append("")
    lines.append("## V10 Readiness Summary")
    lines.append("")
    for key in ("READY", "PARTIAL", "NOT_READY"):
        lines.append(f"- {key}: {readiness_counts.get(key, 0)}")
    lines.append("")
    lines.append("## Top Decisions")
    lines.append("")
    lines.append("| rank | hypothesis_id | group_key | group | score | decision | readiness | reason |")
    lines.append("|---:|---|---|---|---:|---|---|---|")
    for i, row in enumerate(decisions[:20], 1):
        lines.append(
            f"| {i} | {row['hypothesis_id']} | {row['group_key']} | {row['group']} | "
            f"{row['portfolio_score']} | {row['research_decision']} | "
            f"{row['v10_readiness']} | {row['decision_reason']} |"
        )
    lines.append("")
    lines.append("## Guardrail")
    lines.append("")
    lines.append("V9G does not modify trading logic. It only produces research decisions.")
    lines.append("")

    report.write_text("\n".join(lines), encoding="utf-8")

    print("V9G research decision engine completed")
    print("input_rows:", len(rows))
    print("decision_rows:", len(decisions))
    print("report:", report)
    print("csv:", out_csv)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
