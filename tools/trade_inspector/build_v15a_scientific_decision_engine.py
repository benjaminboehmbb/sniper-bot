#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Trade Inspector V15A

Scientific Decision Engine.

Selects, prioritizes, defers, or blocks scientific campaigns.

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


DECISION_FIELDS = [
    "decision_id",
    "campaign_id",
    "decision_type",
    "decision_priority",
    "decision_status",
    "campaign_type",
    "campaign_priority",
    "campaign_status",
    "expected_knowledge_gain",
    "estimated_runtime_minutes",
    "knowledge_gain_per_minute",
    "resource_class",
    "decision_score",
    "decision_reason",
    "recommended_action",
    "execution_gate",
    "required_human_review",
    "success_criterion",
    "stop_criterion",
    "created_at_utc",
]

SUMMARY_FIELDS = ["metric", "value"]
MANIFEST_FIELDS = ["artifact", "path", "rows", "status"]


def resource_class(runtime: float) -> str:
    if runtime <= 30:
        return "LIGHT"
    if runtime <= 120:
        return "MEDIUM"
    return "HEAVY"


def decision_type(campaign: dict[str, str], score: float) -> str:
    status = campaign.get("campaign_status", "")
    priority = campaign.get("campaign_priority", "")

    if status == "BLOCKED":
        return "BLOCK"
    if priority == "VERY_HIGH" and score >= 65:
        return "EXECUTE_FIRST"
    if priority in {"HIGH", "VERY_HIGH"}:
        return "EXECUTE"
    if priority == "MEDIUM":
        return "DEFER"
    return "WATCHLIST"


def decision_priority(score: float, dtype: str) -> str:
    if dtype == "BLOCK":
        return "BLOCKED"
    if score >= 80:
        return "CRITICAL"
    if score >= 65:
        return "HIGH"
    if score >= 45:
        return "MEDIUM"
    return "LOW"


def execution_gate(dtype: str, runtime: float) -> str:
    if dtype == "BLOCK":
        return "CLOSED"
    if runtime > 120:
        return "MANUAL_APPROVAL_REQUIRED"
    return "OPEN"


def build_decision(campaign: dict[str, str]) -> dict[str, Any]:
    cid = campaign.get("campaign_id", "")
    gain = to_float(campaign.get("avg_estimated_knowledge_gain"))
    runtime = to_float(campaign.get("total_estimated_runtime_minutes"))
    kg_per_min = gain / runtime if runtime > 0 else 0.0

    runtime_efficiency = clamp(kg_per_min * 60.0)
    score = clamp(gain * 0.65 + runtime_efficiency * 0.25 + (100.0 - min(runtime, 100.0)) * 0.10)

    dtype = decision_type(campaign, score)
    dprio = decision_priority(score, dtype)
    gate = execution_gate(dtype, runtime)

    human_review = "yes" if gate == "MANUAL_APPROVAL_REQUIRED" or dtype == "BLOCK" else "no"

    if dtype == "EXECUTE_FIRST":
        action = "execute_campaign_first_after_human_confirmation"
    elif dtype == "EXECUTE":
        action = "execute_campaign_when_resources_available"
    elif dtype == "DEFER":
        action = "defer_until_higher_value_campaigns_complete"
    elif dtype == "BLOCK":
        action = "do_not_execute_until_blocker_resolved"
    else:
        action = "keep_campaign_on_watchlist"

    return {
        "decision_id": stable_hash_id("DEC-", [cid, dtype, dprio, gate]),
        "campaign_id": cid,
        "decision_type": dtype,
        "decision_priority": dprio,
        "decision_status": "READY" if gate == "OPEN" else gate,
        "campaign_type": campaign.get("campaign_type", ""),
        "campaign_priority": campaign.get("campaign_priority", ""),
        "campaign_status": campaign.get("campaign_status", ""),
        "expected_knowledge_gain": round(gain, 4),
        "estimated_runtime_minutes": round(runtime, 4),
        "knowledge_gain_per_minute": round(kg_per_min, 6),
        "resource_class": resource_class(runtime),
        "decision_score": round(score, 4),
        "decision_reason": "decision_based_on_expected_knowledge_gain_runtime_efficiency_and_campaign_status",
        "recommended_action": action,
        "execution_gate": gate,
        "required_human_review": human_review,
        "success_criterion": campaign.get("campaign_success_criterion", ""),
        "stop_criterion": campaign.get("campaign_stop_criterion", ""),
        "created_at_utc": now_utc(),
    }


def build_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = [{"metric": "decision_rows", "value": len(rows)}]

    counts: dict[str, int] = {}
    for row in rows:
        for field in ["decision_type", "decision_priority", "execution_gate", "resource_class"]:
            key = f"{field}_{row[field]}"
            counts[key] = counts.get(key, 0) + 1

    for key in sorted(counts):
        out.append({"metric": key, "value": counts[key]})

    return out


def write_report(path: Path, decisions: list[dict[str, Any]], summary: list[dict[str, Any]]) -> None:
    lines = [
        "# V15A SCIENTIFIC DECISION ENGINE REPORT",
        "",
        f"Date: {date.today().isoformat()}",
        "Scope: Trade Inspector V15A",
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
        "## Decisions",
        "",
        "| rank | decision_id | campaign | type | priority | score | gate |",
        "|---:|---|---|---|---|---:|---|",
    ])

    for i, row in enumerate(decisions[:20], 1):
        lines.append(
            f"| {i} | {row['decision_id']} | {row['campaign_id']} | "
            f"{row['decision_type']} | {row['decision_priority']} | "
            f"{row['decision_score']} | {row['execution_gate']} |"
        )

    lines.extend([
        "",
        "## Guardrails",
        "",
        "- V15A does not execute campaigns.",
        "- V15A does not modify strategy logic.",
        "- V15A only creates scientific execution decisions.",
        "- Human confirmation remains required before real execution.",
        "",
    ])

    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--campaigns", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    campaigns = read_csv(args.campaigns)
    decisions = [build_decision(c) for c in campaigns]
    decisions.sort(key=lambda r: (-to_float(r["decision_score"]), str(r["decision_id"])))

    summary = build_summary(decisions)

    decision_path = out_dir / "v15a_scientific_decisions.csv"
    summary_path = out_dir / "v15a_decision_summary.csv"
    manifest_path = out_dir / "v15a_decision_manifest.csv"
    report_path = out_dir / f"V15A_SCIENTIFIC_DECISION_ENGINE_REPORT_{date.today().isoformat()}.md"

    write_csv(decision_path, decisions, DECISION_FIELDS)
    write_csv(summary_path, summary, SUMMARY_FIELDS)

    manifest = [
        {"artifact": "v15a_scientific_decisions.csv", "path": str(decision_path), "rows": len(decisions), "status": "created"},
        {"artifact": "v15a_decision_summary.csv", "path": str(summary_path), "rows": len(summary), "status": "created"},
        {"artifact": report_path.name, "path": str(report_path), "rows": 1, "status": "created"},
    ]

    write_csv(manifest_path, manifest, MANIFEST_FIELDS)
    write_report(report_path, decisions, summary)

    print("V15A scientific decision engine completed")
    print("campaign_rows:", len(campaigns))
    print("decision_rows:", len(decisions))
    print("report:", report_path)
    print("csv:", decision_path)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
