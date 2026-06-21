#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Trade Inspector V14B

Scientific Planning Engine.

Builds research plans from V14A fused conclusions and V13A opportunities.

ASCII only.
"""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path
from typing import Any
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tools.trade_inspector.common import (
    clamp,
    now_utc,
    read_csv,
    stable_hash_id,
    to_float,
    write_csv,
)


PLAN_FIELDS = [
    "plan_id",
    "hypothesis_id",
    "planning_status",
    "planning_priority",
    "source_fused_conclusion_id",
    "source_opportunity_id",
    "goal",
    "step_1",
    "step_2",
    "step_3",
    "step_4",
    "estimated_knowledge_gain",
    "estimated_runtime_minutes",
    "estimated_cost_class",
    "dependency_status",
    "conflict_status",
    "success_criterion",
    "stop_criterion",
    "recommended_next_action",
    "planning_reason",
    "created_at_utc",
]

SUMMARY_FIELDS = ["metric", "value"]
MANIFEST_FIELDS = ["artifact", "path", "rows", "status"]


def index_by(rows: list[dict[str, str]], key: str) -> dict[str, dict[str, str]]:
    return {row[key]: row for row in rows if row.get(key)}


def priority(score: float, status: str) -> str:
    if "BLOCKED" in status:
        return "BLOCKED"
    if score >= 75:
        return "VERY_HIGH"
    if score >= 60:
        return "HIGH"
    if score >= 45:
        return "MEDIUM"
    return "LOW"


def cost_class(runtime: float) -> str:
    if runtime <= 30:
        return "LOW"
    if runtime <= 120:
        return "MEDIUM"
    return "HIGH"


def plan_steps(status: str, recommendation: str) -> tuple[str, str, str, str]:
    if status == "RESEARCH_READY_AFTER_EVIDENCE_EXPANSION":
        return (
            "collect_additional_archives",
            "rerun_v13a_intelligence",
            "rerun_v14a_reasoning",
            "prepare_targeted_validation_if_uncertainty_decreases",
        )

    if "CONFLICT" in status:
        return (
            "inspect_conflict_network",
            "identify_conflicting_evidence",
            "run_targeted_conflict_resolution",
            "recompute_scientific_reasoning",
        )

    if "DEPENDENCY" in status:
        return (
            "inspect_dependency_graph",
            "resolve_blocking_dependency",
            "rerun_opportunity_engine",
            "recompute_scientific_reasoning",
        )

    if recommendation in {"prioritize_research", "prepare_validation_or_keep_priority"}:
        return (
            "prepare_validation_design",
            "run_controlled_replay_validation",
            "update_research_memory",
            "recompute_reasoning_and_planning",
        )

    return (
        "keep_on_watchlist",
        "collect_future_evidence",
        "rerun_intelligence_after_new_data",
        "manual_review_if_priority_changes",
    )


def build_plan(
    conclusion: dict[str, str],
    opportunity: dict[str, str] | None,
) -> dict[str, Any]:
    hid = conclusion.get("hypothesis_id", "")
    status = conclusion.get("fusion_status", "")
    recommendation = conclusion.get("final_recommendation", "")

    opp_score = to_float(opportunity.get("opportunity_score") if opportunity else 0.0)
    strength = to_float(conclusion.get("combined_reasoning_strength"))
    uncertainty = to_float(conclusion.get("combined_uncertainty"))

    knowledge_gain = clamp(opp_score * 0.55 + strength * 0.30 + uncertainty * 0.15)
    runtime = 30.0

    if opportunity:
        exp = opportunity.get("recommended_experiment", "")
        if "archive" in exp:
            runtime = 20.0
        elif "replay" in exp:
            runtime = 60.0
        elif "conflict" in exp or "dependency" in exp:
            runtime = 45.0

    p1, p2, p3, p4 = plan_steps(status, recommendation)

    conflict_status = "blocked" if "CONFLICT" in status else "clear"
    dependency_status = "blocked" if "DEPENDENCY" in status else "clear"

    return {
        "plan_id": stable_hash_id("PLAN-", [hid, status, recommendation]),
        "hypothesis_id": hid,
        "planning_status": "READY" if "BLOCKED" not in status else "BLOCKED",
        "planning_priority": priority(knowledge_gain, status),
        "source_fused_conclusion_id": conclusion.get("fused_conclusion_id", ""),
        "source_opportunity_id": opportunity.get("opportunity_id", "") if opportunity else "",
        "goal": conclusion.get("final_conclusion", ""),
        "step_1": p1,
        "step_2": p2,
        "step_3": p3,
        "step_4": p4,
        "estimated_knowledge_gain": round(knowledge_gain, 4),
        "estimated_runtime_minutes": round(runtime, 4),
        "estimated_cost_class": cost_class(runtime),
        "dependency_status": dependency_status,
        "conflict_status": conflict_status,
        "success_criterion": opportunity.get("success_criterion", "scientific_reasoning_improves") if opportunity else "scientific_reasoning_improves",
        "stop_criterion": "uncertainty_increases_or_conflict_emerges",
        "recommended_next_action": recommendation,
        "planning_reason": "plan_generated_from_fused_scientific_conclusion_and_research_opportunity",
        "created_at_utc": now_utc(),
    }


def build_summary(plans: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = [{"metric": "planning_rows", "value": len(plans)}]

    status_counts: dict[str, int] = {}
    priority_counts: dict[str, int] = {}

    for row in plans:
        status_counts[str(row["planning_status"])] = status_counts.get(str(row["planning_status"]), 0) + 1
        priority_counts[str(row["planning_priority"])] = priority_counts.get(str(row["planning_priority"]), 0) + 1

    for key in sorted(status_counts):
        rows.append({"metric": f"planning_status_{key}", "value": status_counts[key]})
    for key in sorted(priority_counts):
        rows.append({"metric": f"planning_priority_{key}", "value": priority_counts[key]})

    return rows


def write_report(path: Path, plans: list[dict[str, Any]], summary: list[dict[str, Any]]) -> None:
    lines = [
        "# V14B SCIENTIFIC PLANNING ENGINE REPORT",
        "",
        f"Date: {date.today().isoformat()}",
        "Scope: Trade Inspector V14B",
        "",
        "## Summary",
        "",
        "| metric | value |",
        "|---|---:|",
    ]

    for row in summary:
        lines.append(f"| {row['metric']} | {row['value']} |")

    lines.extend([
        "",
        "## Top Plans",
        "",
        "| rank | plan_id | hypothesis | priority | status | step_1 |",
        "|---:|---|---|---|---|---|",
    ])

    for i, row in enumerate(plans[:20], 1):
        lines.append(
            f"| {i} | {row['plan_id']} | {row['hypothesis_id']} | "
            f"{row['planning_priority']} | {row['planning_status']} | {row['step_1']} |"
        )

    lines.extend([
        "",
        "## Guardrails",
        "",
        "- V14B does not execute plans.",
        "- V14B does not modify strategy logic.",
        "- V14B only creates scientific planning recommendations.",
        "",
    ])

    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fused-conclusions", required=True)
    parser.add_argument("--research-opportunities", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    conclusions = read_csv(args.fused_conclusions)
    opportunities = read_csv(args.research_opportunities)
    opportunity_by_hid = index_by(opportunities, "hypothesis_id")

    plans = [
        build_plan(conclusion, opportunity_by_hid.get(conclusion.get("hypothesis_id", "")))
        for conclusion in conclusions
    ]

    plans.sort(key=lambda r: (-to_float(r["estimated_knowledge_gain"]), str(r["plan_id"])))

    summary = build_summary(plans)

    plan_path = out_dir / "v14b_scientific_research_plans.csv"
    summary_path = out_dir / "v14b_planning_summary.csv"
    manifest_path = out_dir / "v14b_planning_manifest.csv"
    report_path = out_dir / f"V14B_SCIENTIFIC_PLANNING_ENGINE_REPORT_{date.today().isoformat()}.md"

    write_csv(plan_path, plans, PLAN_FIELDS)
    write_csv(summary_path, summary, SUMMARY_FIELDS)

    manifest = [
        {"artifact": "v14b_scientific_research_plans.csv", "path": str(plan_path), "rows": len(plans), "status": "created"},
        {"artifact": "v14b_planning_summary.csv", "path": str(summary_path), "rows": len(summary), "status": "created"},
        {"artifact": report_path.name, "path": str(report_path), "rows": 1, "status": "created"},
    ]
    write_csv(manifest_path, manifest, MANIFEST_FIELDS)
    write_report(report_path, plans, summary)

    print("V14B scientific planning engine completed")
    print("fused_conclusion_rows:", len(conclusions))
    print("research_opportunity_rows:", len(opportunities))
    print("planning_rows:", len(plans))
    print("report:", report_path)
    print("csv:", plan_path)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
