#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

from tools.trade_inspector.common.io import read_csv, write_csv
from tools.trade_inspector.common.utils import pick, to_float






def decision_type(memory: dict[str, str]) -> str:
    memory_type = pick(memory, ["memory_type"], "")
    strength = pick(memory, ["memory_strength"], "")
    next_action = pick(memory, ["recommended_next_action"], "")

    if strength == "blocked":
        return "resolve_blocker"
    if next_action == "review_for_execution":
        return "approve_for_manual_review"
    if memory_type == "cross_campaign_pattern" and strength == "high":
        return "preserve_pattern_for_future_campaigns"
    if strength == "high":
        return "prioritize"
    if strength == "medium":
        return "monitor"
    return "deprioritize"


def confidence(memory: dict[str, str]) -> float:
    strength = pick(memory, ["memory_strength"], "low")
    roi = to_float(pick(memory, ["research_roi_score"], "0"))

    base = {
        "high": 0.90,
        "medium": 0.70,
        "low": 0.45,
        "blocked": 0.80,
    }.get(strength, 0.40)

    if roi > 0:
        base = (base + roi) / 2.0

    return round(max(0.0, min(1.0, base)), 4)


def director_priority(memory: dict[str, str]) -> str:
    strength = pick(memory, ["memory_strength"], "low")
    next_action = pick(memory, ["recommended_next_action"], "")

    if strength == "blocked":
        return "critical"
    if strength == "high":
        return "high"
    if next_action in {"review_for_execution", "resolve_blockers"}:
        return "high"
    if strength == "medium":
        return "medium"
    return "low"


def build_directives(memory_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    directives: list[dict[str, object]] = []

    for i, memory in enumerate(memory_rows, start=1):
        dtype = decision_type(memory)
        prio = director_priority(memory)
        conf = confidence(memory)

        directives.append(
            {
                "directive_id": f"V12G-DIRECTIVE-{i:03d}",
                "source_memory_id": pick(memory, ["memory_id"]),
                "source_memory_type": pick(memory, ["memory_type"]),
                "source_id": pick(memory, ["source_id"]),
                "decision_type": dtype,
                "director_priority": prio,
                "confidence_score": f"{conf:.4f}",
                "recommended_action": pick(memory, ["recommended_next_action"], ""),
                "dominant_machine": pick(memory, ["dominant_machine"], ""),
                "dominant_runtime_class": pick(memory, ["dominant_runtime_class"], ""),
                "estimated_runtime_minutes": pick(memory, ["total_estimated_runtime_minutes"], ""),
                "execution_allowed": "false",
                "requires_manual_review": "true",
                "directive_status": "active",
                "guardrails": "no_strategy_change; no_runtime; no_replay; no_live_trading; director_decision_only",
            }
        )

    directives.sort(
        key=lambda r: (
            {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(str(r["director_priority"]), 9),
            -float(r["confidence_score"]),
            str(r["directive_id"]),
        )
    )

    for rank, row in enumerate(directives, start=1):
        row["director_rank"] = rank

    return directives


def build_summary(directives: list[dict[str, object]]) -> list[dict[str, object]]:
    total = len(directives)
    critical = sum(1 for r in directives if r["director_priority"] == "critical")
    high = sum(1 for r in directives if r["director_priority"] == "high")
    medium = sum(1 for r in directives if r["director_priority"] == "medium")
    low = sum(1 for r in directives if r["director_priority"] == "low")

    return [
        {"metric": "directives_total", "value": total},
        {"metric": "critical_directives", "value": critical},
        {"metric": "high_directives", "value": high},
        {"metric": "medium_directives", "value": medium},
        {"metric": "low_directives", "value": low},
    ]


def write_report(
    path: Path,
    directives: list[dict[str, object]],
    summary: list[dict[str, object]],
    input_path: Path,
) -> None:
    lines = [
        "# V12G AUTONOMOUS RESEARCH DIRECTOR REPORT",
        "",
        f"Date: {date.today().isoformat()}",
        "",
        "## Objective",
        "",
        "Convert V12F research memory into ranked autonomous research directives.",
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
        "- Director decisions only.",
        "- Manual review required before any future execution.",
        "",
        "## Summary",
        "",
        "| metric | value |",
        "|---|---:|",
    ]

    for row in summary:
        lines.append(f"| {row['metric']} | {row['value']} |")

    lines += [
        "",
        "## Director Queue",
        "",
        "| rank | directive_id | priority | decision | confidence | source |",
        "|---:|---|---|---|---:|---|",
    ]

    for row in directives[:50]:
        lines.append(
            f"| {row['director_rank']} | {row['directive_id']} | {row['director_priority']} | "
            f"{row['decision_type']} | {row['confidence_score']} | {row['source_id']} |"
        )

    lines += [
        "",
        "## Status",
        "",
        "Completed.",
        "",
    ]

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="V12G Autonomous Research Director")
    parser.add_argument("--research-memory", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    input_path = Path(args.research_memory)
    output_dir = Path(args.output_dir)

    memory_rows = read_csv(input_path)
    directives = build_directives(memory_rows)
    summary = build_summary(directives)

    directive_path = output_dir / "v12g_autonomous_research_directives.csv"
    summary_path = output_dir / "v12g_autonomous_research_director_summary.csv"
    manifest_path = output_dir / "v12g_autonomous_research_director_manifest.csv"
    report_path = output_dir / f"V12G_AUTONOMOUS_RESEARCH_DIRECTOR_REPORT_{date.today().isoformat()}.md"

    directive_fields = [
        "director_rank",
        "directive_id",
        "source_memory_id",
        "source_memory_type",
        "source_id",
        "decision_type",
        "director_priority",
        "confidence_score",
        "recommended_action",
        "dominant_machine",
        "dominant_runtime_class",
        "estimated_runtime_minutes",
        "execution_allowed",
        "requires_manual_review",
        "directive_status",
        "guardrails",
    ]

    write_csv(directive_path, directives, directive_fields)
    write_csv(summary_path, summary, ["metric", "value"])

    manifest_rows = [
        {"artifact": "v12g_autonomous_research_directives.csv", "path": str(directive_path), "rows": len(directives), "status": "created"},
        {"artifact": "v12g_autonomous_research_director_summary.csv", "path": str(summary_path), "rows": len(summary), "status": "created"},
        {"artifact": "V12G_AUTONOMOUS_RESEARCH_DIRECTOR_REPORT", "path": str(report_path), "rows": 1, "status": "created"},
    ]
    write_csv(manifest_path, manifest_rows, ["artifact", "path", "rows", "status"])

    write_report(report_path, directives, summary, input_path)

    print("PASS: V12G autonomous research director completed")
    print(f"directives: {len(directives)}")
    print(f"directive_csv: {directive_path}")
    print(f"summary_csv: {summary_path}")
    print(f"manifest_csv: {manifest_path}")
    print(f"report_md: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
