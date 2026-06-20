#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

from tools.trade_inspector.common.io import read_csv, write_csv
from tools.trade_inspector.common.utils import pick, to_float






def memory_strength(health: str, roi: float) -> str:
    if health == "strong" and roi >= 0.75:
        return "high"
    if health in {"strong", "usable"} and roi >= 0.55:
        return "medium"
    if health in {"blocked", "partial_block"}:
        return "blocked"
    return "low"


def build_memory(campaign_analysis: list[dict[str, str]], patterns: list[dict[str, str]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []

    for i, row in enumerate(campaign_analysis, start=1):
        campaign_id = pick(row, ["campaign_id"], f"unknown_campaign_{i}")
        health = pick(row, ["campaign_health"], "unknown")
        roi = to_float(pick(row, ["avg_research_roi_score"], "0"))

        rows.append(
            {
                "memory_id": f"V12F-MEM-CAMPAIGN-{i:03d}",
                "memory_type": "campaign_state",
                "source_id": campaign_id,
                "source_field": "campaign_health",
                "source_value": health,
                "memory_strength": memory_strength(health, roi),
                "research_roi_score": f"{roi:.4f}",
                "recommended_next_action": pick(row, ["recommended_next_action"], ""),
                "dominant_priority": pick(row, ["dominant_priority"], ""),
                "dominant_machine": pick(row, ["dominant_machine"], ""),
                "dominant_runtime_class": pick(row, ["dominant_runtime_class"], ""),
                "total_estimated_runtime_minutes": pick(row, ["total_estimated_runtime_minutes"], "0"),
                "memory_status": "active",
                "created_date": date.today().isoformat(),
            }
        )

    offset = len(rows)

    for j, row in enumerate(patterns, start=1):
        interpretation = pick(row, ["interpretation"], "informational")
        share = to_float(pick(row, ["share"], "0"))

        if interpretation == "informational" and share < 0.50:
            strength = "low"
        elif interpretation == "informational":
            strength = "medium"
        else:
            strength = "high"

        rows.append(
            {
                "memory_id": f"V12F-MEM-PATTERN-{j:03d}",
                "memory_type": "cross_campaign_pattern",
                "source_id": pick(row, ["pattern_type"], "") + ":" + pick(row, ["pattern_value"], ""),
                "source_field": pick(row, ["pattern_type"], ""),
                "source_value": pick(row, ["pattern_value"], ""),
                "memory_strength": strength,
                "research_roi_score": "",
                "recommended_next_action": interpretation,
                "dominant_priority": "",
                "dominant_machine": "",
                "dominant_runtime_class": "",
                "total_estimated_runtime_minutes": "",
                "memory_status": "active",
                "created_date": date.today().isoformat(),
            }
        )

    return rows


def build_summary(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    total = len(rows)
    high = sum(1 for r in rows if r["memory_strength"] == "high")
    medium = sum(1 for r in rows if r["memory_strength"] == "medium")
    low = sum(1 for r in rows if r["memory_strength"] == "low")
    blocked = sum(1 for r in rows if r["memory_strength"] == "blocked")

    return [
        {"metric": "memory_items_total", "value": total},
        {"metric": "high_strength_items", "value": high},
        {"metric": "medium_strength_items", "value": medium},
        {"metric": "low_strength_items", "value": low},
        {"metric": "blocked_items", "value": blocked},
    ]


def write_report(path: Path, memory_rows: list[dict[str, object]], summary_rows: list[dict[str, object]]) -> None:
    lines = [
        "# V12F RESEARCH MEMORY REPORT",
        "",
        f"Date: {date.today().isoformat()}",
        "",
        "## Objective",
        "",
        "Persist campaign states and cross-campaign patterns as research memory for V12G.",
        "",
        "## Guardrails",
        "",
        "- No strategy logic changes.",
        "- No runtime execution.",
        "- No replay execution.",
        "- No live trading.",
        "- Memory-only output.",
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
        "## Memory Items",
        "",
        "| memory_id | type | source | strength | next_action |",
        "|---|---|---|---|---|",
    ]

    for row in memory_rows[:50]:
        lines.append(
            f"| {row['memory_id']} | {row['memory_type']} | {row['source_id']} | "
            f"{row['memory_strength']} | {row['recommended_next_action']} |"
        )

    lines += ["", "## Status", "", "Completed.", ""]

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="V12F Research Memory")
    parser.add_argument("--campaign-analysis", required=True)
    parser.add_argument("--cross-patterns", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    campaign_path = Path(args.campaign_analysis)
    pattern_path = Path(args.cross_patterns)
    output_dir = Path(args.output_dir)

    campaigns = read_csv(campaign_path)
    patterns = read_csv(pattern_path)

    memory_rows = build_memory(campaigns, patterns)
    summary_rows = build_summary(memory_rows)

    memory_path = output_dir / "v12f_research_memory.csv"
    summary_path = output_dir / "v12f_research_memory_summary.csv"
    manifest_path = output_dir / "v12f_research_memory_manifest.csv"
    report_path = output_dir / f"V12F_RESEARCH_MEMORY_REPORT_{date.today().isoformat()}.md"

    memory_fields = [
        "memory_id",
        "memory_type",
        "source_id",
        "source_field",
        "source_value",
        "memory_strength",
        "research_roi_score",
        "recommended_next_action",
        "dominant_priority",
        "dominant_machine",
        "dominant_runtime_class",
        "total_estimated_runtime_minutes",
        "memory_status",
        "created_date",
    ]

    write_csv(memory_path, memory_rows, memory_fields)
    write_csv(summary_path, summary_rows, ["metric", "value"])

    manifest_rows = [
        {"artifact": "v12f_research_memory.csv", "path": str(memory_path), "rows": len(memory_rows), "status": "created"},
        {"artifact": "v12f_research_memory_summary.csv", "path": str(summary_path), "rows": len(summary_rows), "status": "created"},
        {"artifact": "V12F_RESEARCH_MEMORY_REPORT", "path": str(report_path), "rows": 1, "status": "created"},
    ]
    write_csv(manifest_path, manifest_rows, ["artifact", "path", "rows", "status"])

    write_report(report_path, memory_rows, summary_rows)

    print("PASS: V12F research memory completed")
    print(f"memory_items: {len(memory_rows)}")
    print(f"memory_csv: {memory_path}")
    print(f"summary_csv: {summary_path}")
    print(f"manifest_csv: {manifest_path}")
    print(f"report_md: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
