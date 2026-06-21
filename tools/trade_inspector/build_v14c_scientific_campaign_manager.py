#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Trade Inspector V14C

Scientific Campaign Manager.

Groups V14B research plans into efficient scientific campaigns.

ASCII only.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
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


CAMPAIGN_FIELDS = [
    "campaign_id",
    "campaign_type",
    "campaign_priority",
    "campaign_status",
    "hypothesis_ids",
    "plan_ids",
    "plan_count",
    "primary_step",
    "shared_goal",
    "total_estimated_knowledge_gain",
    "avg_estimated_knowledge_gain",
    "total_estimated_runtime_minutes",
    "estimated_cost_class",
    "dependency_status",
    "conflict_status",
    "campaign_success_criterion",
    "campaign_stop_criterion",
    "recommended_execution_mode",
    "campaign_reason",
    "created_at_utc",
]

SUMMARY_FIELDS = ["metric", "value"]
MANIFEST_FIELDS = ["artifact", "path", "rows", "status"]


def cost_class(runtime: float) -> str:
    if runtime <= 30:
        return "LOW"
    if runtime <= 120:
        return "MEDIUM"
    return "HIGH"


def campaign_priority(avg_gain: float, plan_count: int, blocked: bool) -> str:
    if blocked:
        return "BLOCKED"
    if avg_gain >= 75 or (avg_gain >= 60 and plan_count >= 3):
        return "VERY_HIGH"
    if avg_gain >= 60:
        return "HIGH"
    if avg_gain >= 45:
        return "MEDIUM"
    return "LOW"


def execution_mode(plan_count: int, runtime: float, blocked: bool) -> str:
    if blocked:
        return "WAIT"
    if plan_count >= 3:
        return "BATCH"
    if runtime <= 30:
        return "FAST_SINGLE"
    return "SEQUENTIAL"


def campaign_type_for(primary_step: str) -> str:
    if "archive" in primary_step:
        return "ARCHIVE_EXPANSION_CAMPAIGN"
    if "conflict" in primary_step:
        return "CONFLICT_RESOLUTION_CAMPAIGN"
    if "dependency" in primary_step:
        return "DEPENDENCY_RESOLUTION_CAMPAIGN"
    if "validation" in primary_step or "replay" in primary_step:
        return "VALIDATION_CAMPAIGN"
    return "WATCHLIST_CAMPAIGN"


def build_campaign(group_key: str, plans: list[dict[str, str]]) -> dict[str, Any]:
    hypothesis_ids = sorted({p.get("hypothesis_id", "") for p in plans if p.get("hypothesis_id")})
    plan_ids = sorted({p.get("plan_id", "") for p in plans if p.get("plan_id")})
    primary_step = group_key

    gains = [to_float(p.get("estimated_knowledge_gain")) for p in plans]
    runtimes = [to_float(p.get("estimated_runtime_minutes")) for p in plans]

    total_gain = sum(gains)
    avg_gain = total_gain / len(gains) if gains else 0.0
    total_runtime = sum(runtimes)

    dep_blocked = any(p.get("dependency_status") == "blocked" for p in plans)
    conf_blocked = any(p.get("conflict_status") == "blocked" for p in plans)
    blocked = dep_blocked or conf_blocked

    ctype = campaign_type_for(primary_step)
    priority = campaign_priority(avg_gain, len(plans), blocked)
    mode = execution_mode(len(plans), total_runtime, blocked)

    return {
        "campaign_id": stable_hash_id("CAMP-", [ctype, primary_step, hypothesis_ids, plan_ids]),
        "campaign_type": ctype,
        "campaign_priority": priority,
        "campaign_status": "BLOCKED" if blocked else "READY",
        "hypothesis_ids": ";".join(hypothesis_ids),
        "plan_ids": ";".join(plan_ids),
        "plan_count": len(plans),
        "primary_step": primary_step,
        "shared_goal": f"Execute shared research step: {primary_step}",
        "total_estimated_knowledge_gain": round(total_gain, 4),
        "avg_estimated_knowledge_gain": round(avg_gain, 4),
        "total_estimated_runtime_minutes": round(total_runtime, 4),
        "estimated_cost_class": cost_class(total_runtime),
        "dependency_status": "blocked" if dep_blocked else "clear",
        "conflict_status": "blocked" if conf_blocked else "clear",
        "campaign_success_criterion": "campaign_reduces_uncertainty_or_increases_coverage",
        "campaign_stop_criterion": "stop_if_conflict_or_uncertainty_increases",
        "recommended_execution_mode": mode,
        "campaign_reason": "plans_grouped_by_shared_primary_research_step",
        "created_at_utc": now_utc(),
    }


def build_campaigns(plans: list[dict[str, str]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)

    for plan in plans:
        key = plan.get("step_1", "unknown_step")
        grouped[key].append(plan)

    campaigns = [build_campaign(key, rows) for key, rows in grouped.items()]
    campaigns.sort(
        key=lambda r: (
            str(r["campaign_status"]),
            -to_float(r["avg_estimated_knowledge_gain"]),
            str(r["campaign_id"]),
        )
    )
    return campaigns


def build_summary(campaigns: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = [{"metric": "campaign_rows", "value": len(campaigns)}]

    type_counts: dict[str, int] = {}
    status_counts: dict[str, int] = {}
    priority_counts: dict[str, int] = {}

    for c in campaigns:
        type_counts[str(c["campaign_type"])] = type_counts.get(str(c["campaign_type"]), 0) + 1
        status_counts[str(c["campaign_status"])] = status_counts.get(str(c["campaign_status"]), 0) + 1
        priority_counts[str(c["campaign_priority"])] = priority_counts.get(str(c["campaign_priority"]), 0) + 1

    for key in sorted(type_counts):
        rows.append({"metric": f"campaign_type_{key}", "value": type_counts[key]})
    for key in sorted(status_counts):
        rows.append({"metric": f"campaign_status_{key}", "value": status_counts[key]})
    for key in sorted(priority_counts):
        rows.append({"metric": f"campaign_priority_{key}", "value": priority_counts[key]})

    return rows


def write_report(path: Path, campaigns: list[dict[str, Any]], summary: list[dict[str, Any]]) -> None:
    lines = [
        "# V14C SCIENTIFIC CAMPAIGN MANAGER REPORT",
        "",
        f"Date: {date.today().isoformat()}",
        "Scope: Trade Inspector V14C",
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
        "## Campaigns",
        "",
        "| rank | campaign_id | type | priority | status | plans | runtime | mode |",
        "|---:|---|---|---|---|---:|---:|---|",
    ])

    for i, row in enumerate(campaigns[:20], 1):
        lines.append(
            f"| {i} | {row['campaign_id']} | {row['campaign_type']} | "
            f"{row['campaign_priority']} | {row['campaign_status']} | "
            f"{row['plan_count']} | {row['total_estimated_runtime_minutes']} | "
            f"{row['recommended_execution_mode']} |"
        )

    lines.extend([
        "",
        "## Guardrails",
        "",
        "- V14C does not execute campaigns.",
        "- V14C does not modify strategy logic.",
        "- V14C only groups plans into scientific campaigns.",
        "",
    ])

    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--research-plans", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    plans = read_csv(args.research_plans)
    campaigns = build_campaigns(plans)
    summary = build_summary(campaigns)

    campaign_path = out_dir / "v14c_scientific_campaigns.csv"
    summary_path = out_dir / "v14c_campaign_summary.csv"
    manifest_path = out_dir / "v14c_campaign_manifest.csv"
    report_path = out_dir / f"V14C_SCIENTIFIC_CAMPAIGN_MANAGER_REPORT_{date.today().isoformat()}.md"

    write_csv(campaign_path, campaigns, CAMPAIGN_FIELDS)
    write_csv(summary_path, summary, SUMMARY_FIELDS)

    manifest = [
        {"artifact": "v14c_scientific_campaigns.csv", "path": str(campaign_path), "rows": len(campaigns), "status": "created"},
        {"artifact": "v14c_campaign_summary.csv", "path": str(summary_path), "rows": len(summary), "status": "created"},
        {"artifact": report_path.name, "path": str(report_path), "rows": 1, "status": "created"},
    ]

    write_csv(manifest_path, manifest, MANIFEST_FIELDS)
    write_report(report_path, campaigns, summary)

    print("V14C scientific campaign manager completed")
    print("research_plan_rows:", len(plans))
    print("campaign_rows:", len(campaigns))
    print("report:", report_path)
    print("csv:", campaign_path)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
