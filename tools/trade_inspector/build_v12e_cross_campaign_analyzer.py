#!/usr/bin/env python3
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

from tools.trade_inspector.common.io import read_csv, write_csv
from tools.trade_inspector.common.utils import pick, to_float, to_int







def build_campaign_groups(rows: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        campaign_id = pick(row, ["campaign_id"], "unknown_campaign")
        groups[campaign_id].append(row)
    return dict(groups)


def analyze_campaigns(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    groups = build_campaign_groups(rows)
    output: list[dict[str, object]] = []

    for campaign_id, items in sorted(groups.items()):
        priorities = Counter(pick(r, ["priority"], "unknown") for r in items)
        statuses = Counter(pick(r, ["executor_status", "plan_status"], "unknown") for r in items)
        machines = Counter(pick(r, ["recommended_machine"], "unknown") for r in items)
        runtime_classes = Counter(pick(r, ["runtime_class"], "unknown") for r in items)

        roi_values = [to_float(pick(r, ["research_roi_score"], "0")) for r in items]
        minutes = [to_int(pick(r, ["estimated_runtime_minutes"], "0")) for r in items]

        total = len(items)
        blocked = statuses.get("blocked", 0)
        ready = statuses.get("ready", 0)
        planned = statuses.get("planned", 0)

        avg_roi = sum(roi_values) / total if total else 0.0
        total_runtime = sum(minutes)

        if blocked == total:
            health = "blocked"
        elif blocked > 0:
            health = "partial_block"
        elif avg_roi >= 0.75:
            health = "strong"
        elif avg_roi >= 0.55:
            health = "usable"
        else:
            health = "weak"

        dominant_machine = machines.most_common(1)[0][0] if machines else "unknown"
        dominant_priority = priorities.most_common(1)[0][0] if priorities else "unknown"
        dominant_runtime = runtime_classes.most_common(1)[0][0] if runtime_classes else "unknown"

        output.append(
            {
                "campaign_id": campaign_id,
                "items": total,
                "ready_items": ready,
                "planned_items": planned,
                "blocked_items": blocked,
                "dominant_priority": dominant_priority,
                "dominant_machine": dominant_machine,
                "dominant_runtime_class": dominant_runtime,
                "avg_research_roi_score": f"{avg_roi:.4f}",
                "total_estimated_runtime_minutes": total_runtime,
                "campaign_health": health,
                "recommended_next_action": (
                    "resolve_blockers"
                    if health in {"blocked", "partial_block"}
                    else "review_for_execution"
                    if health in {"strong", "usable"}
                    else "deprioritize_or_refine"
                ),
            }
        )

    return output


def analyze_cross_patterns(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    patterns: list[dict[str, object]] = []

    fields = [
        "priority",
        "recommended_machine",
        "runtime_class",
        "resource_class",
        "executor_status",
        "execution_window",
    ]

    for field in fields:
        counts = Counter(pick(r, [field], "unknown") for r in rows)
        for value, count in sorted(counts.items(), key=lambda x: (-x[1], x[0])):
            share = count / len(rows) if rows else 0.0
            patterns.append(
                {
                    "pattern_type": field,
                    "pattern_value": value,
                    "count": count,
                    "share": f"{share:.4f}",
                    "interpretation": interpret_pattern(field, value, share),
                }
            )

    return patterns


def interpret_pattern(field: str, value: str, share: float) -> str:
    if field == "executor_status" and value == "blocked" and share > 0.0:
        return "blocked_items_require_review"
    if field == "recommended_machine" and value == "Workstation" and share >= 0.5:
        return "workstation_capacity_relevant"
    if field == "runtime_class" and value == "long" and share >= 0.5:
        return "long_runtime_campaigns_dominate"
    if field == "priority" and value == "high" and share >= 0.5:
        return "high_priority_research_cluster"
    return "informational"


def build_summary(campaign_rows: list[dict[str, object]], pattern_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    total_campaigns = len(campaign_rows)
    blocked = sum(1 for r in campaign_rows if r["campaign_health"] in {"blocked", "partial_block"})
    strong = sum(1 for r in campaign_rows if r["campaign_health"] == "strong")
    total_runtime = sum(int(r["total_estimated_runtime_minutes"]) for r in campaign_rows)

    return [
        {"metric": "campaigns_analyzed", "value": total_campaigns},
        {"metric": "strong_campaigns", "value": strong},
        {"metric": "blocked_or_partial_block_campaigns", "value": blocked},
        {"metric": "cross_patterns_detected", "value": len(pattern_rows)},
        {"metric": "total_estimated_runtime_minutes", "value": total_runtime},
    ]


def write_report(
    path: Path,
    campaign_rows: list[dict[str, object]],
    pattern_rows: list[dict[str, object]],
    summary_rows: list[dict[str, object]],
    input_path: Path,
) -> None:
    lines = [
        "# V12E CROSS CAMPAIGN ANALYZER REPORT",
        "",
        f"Date: {date.today().isoformat()}",
        "",
        "## Objective",
        "",
        "Analyze campaign-level and cross-campaign patterns from V12D execution planning artifacts.",
        "",
        "## Input",
        "",
        f"- {input_path}",
        "",
        "## Guardrails",
        "",
        "- No strategy logic changes.",
        "- No runtime execution.",
        "- No replay execution.",
        "- No live trading.",
        "- Analysis-only output.",
        "",
        "## Summary",
        "",
        "| metric | value |",
        "|---|---:|",
    ]

    for row in summary_rows:
        lines.append(f"| {row['metric']} | {row['value']} |")

    lines += [
        "",
        "## Campaign Analysis",
        "",
        "| campaign_id | items | health | avg_roi | runtime_min | next_action |",
        "|---|---:|---|---:|---:|---|",
    ]

    for row in campaign_rows:
        lines.append(
            f"| {row['campaign_id']} | {row['items']} | {row['campaign_health']} | "
            f"{row['avg_research_roi_score']} | {row['total_estimated_runtime_minutes']} | "
            f"{row['recommended_next_action']} |"
        )

    lines += [
        "",
        "## Dominant Cross Patterns",
        "",
        "| pattern_type | pattern_value | count | share | interpretation |",
        "|---|---|---:|---:|---|",
    ]

    for row in pattern_rows[:20]:
        lines.append(
            f"| {row['pattern_type']} | {row['pattern_value']} | {row['count']} | "
            f"{row['share']} | {row['interpretation']} |"
        )

    lines += ["", "## Status", "", "Completed.", ""]

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="V12E Cross Campaign Analyzer")
    parser.add_argument("--execution-queue", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    input_path = Path(args.execution_queue)
    output_dir = Path(args.output_dir)

    rows = read_csv(input_path)

    campaign_rows = analyze_campaigns(rows)
    pattern_rows = analyze_cross_patterns(rows)
    summary_rows = build_summary(campaign_rows, pattern_rows)

    campaign_path = output_dir / "v12e_cross_campaign_analysis.csv"
    pattern_path = output_dir / "v12e_cross_campaign_patterns.csv"
    summary_path = output_dir / "v12e_cross_campaign_summary.csv"
    manifest_path = output_dir / "v12e_cross_campaign_manifest.csv"
    report_path = output_dir / f"V12E_CROSS_CAMPAIGN_ANALYZER_REPORT_{date.today().isoformat()}.md"

    campaign_fields = [
        "campaign_id",
        "items",
        "ready_items",
        "planned_items",
        "blocked_items",
        "dominant_priority",
        "dominant_machine",
        "dominant_runtime_class",
        "avg_research_roi_score",
        "total_estimated_runtime_minutes",
        "campaign_health",
        "recommended_next_action",
    ]

    pattern_fields = [
        "pattern_type",
        "pattern_value",
        "count",
        "share",
        "interpretation",
    ]

    write_csv(campaign_path, campaign_rows, campaign_fields)
    write_csv(pattern_path, pattern_rows, pattern_fields)
    write_csv(summary_path, summary_rows, ["metric", "value"])

    manifest_rows = [
        {"artifact": "v12e_cross_campaign_analysis.csv", "path": str(campaign_path), "rows": len(campaign_rows), "status": "created"},
        {"artifact": "v12e_cross_campaign_patterns.csv", "path": str(pattern_path), "rows": len(pattern_rows), "status": "created"},
        {"artifact": "v12e_cross_campaign_summary.csv", "path": str(summary_path), "rows": len(summary_rows), "status": "created"},
        {"artifact": "V12E_CROSS_CAMPAIGN_ANALYZER_REPORT", "path": str(report_path), "rows": 1, "status": "created"},
    ]
    write_csv(manifest_path, manifest_rows, ["artifact", "path", "rows", "status"])

    write_report(report_path, campaign_rows, pattern_rows, summary_rows, input_path)

    print("PASS: V12E cross campaign analyzer completed")
    print(f"campaigns: {len(campaign_rows)}")
    print(f"patterns: {len(pattern_rows)}")
    print(f"campaign_csv: {campaign_path}")
    print(f"pattern_csv: {pattern_path}")
    print(f"summary_csv: {summary_path}")
    print(f"manifest_csv: {manifest_path}")
    print(f"report_md: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
