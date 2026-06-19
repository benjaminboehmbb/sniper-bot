#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import argparse
import csv
from pathlib import Path


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return

    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def num(value: object, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except Exception:
        return default


def maturity_level(row: dict[str, str]) -> str:
    score = num(row.get("knowledge_score"))
    success = num(row.get("successful_validations"))
    fail = num(row.get("failed_validations"))
    pending = num(row.get("pending_validations"))
    blocked = num(row.get("blocked_events"))
    updates = num(row.get("knowledge_updates"))
    research_status = row.get("research_status", "")

    if blocked > 0 or research_status == "BLOCKED":
        return "BLOCKED"

    if pending > 0 or research_status == "PENDING":
        return "PENDING"

    if updates <= 1:
        return "NEW"

    if success >= 2 and score >= 2:
        return "VALIDATED"

    if fail > success or score < 0:
        return "DEGRADED"

    return "DEVELOPING"


def evolution_trend(row: dict[str, str]) -> str:
    score = num(row.get("knowledge_score"))
    success = num(row.get("successful_validations"))
    fail = num(row.get("failed_validations"))
    pending = num(row.get("pending_validations"))
    blocked = num(row.get("blocked_events"))
    updates = num(row.get("knowledge_updates"))

    if blocked > 0:
        return "BLOCKED"

    if updates <= 1:
        return "INSUFFICIENT_HISTORY"

    if pending > 0 and score == 0:
        return "INSUFFICIENT_HISTORY"

    if success > fail and score > 0:
        return "IMPROVING"

    if fail > success or score < 0:
        return "DECLINING"

    return "STABLE"


def next_learning_need(maturity: str, trend: str) -> str:
    if maturity == "BLOCKED":
        return "resolve_blocker_before_learning"
    if maturity == "PENDING":
        return "run_real_replay_or_collect_more_archives"
    if maturity == "NEW":
        return "collect_additional_validation"
    if maturity == "VALIDATED" and trend == "IMPROVING":
        return "candidate_for_priority_review"
    if maturity == "DEGRADED":
        return "deprioritize_or_review_failure_causes"
    return "continue_observation"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--v11c-csv", required=True)
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()

    source = Path(args.v11c_csv)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = read_csv(source)

    evolution: list[dict[str, object]] = []

    for row in rows:
        maturity = maturity_level(row)
        trend = evolution_trend(row)

        evolution.append(
            {
                "hypothesis_id": row.get("hypothesis_id", ""),
                "hypothesis_group": row.get("hypothesis_group", ""),
                "knowledge_score": row.get("knowledge_score", ""),
                "successful_validations": row.get("successful_validations", ""),
                "failed_validations": row.get("failed_validations", ""),
                "pending_validations": row.get("pending_validations", ""),
                "blocked_events": row.get("blocked_events", ""),
                "knowledge_updates": row.get("knowledge_updates", ""),
                "research_status": row.get("research_status", ""),
                "maturity_level": maturity,
                "evolution_trend": trend,
                "next_learning_need": next_learning_need(maturity, trend),
            }
        )

    evolution.sort(
        key=lambda r: (
            str(r["maturity_level"]) not in {"VALIDATED", "DEVELOPING"},
            str(r["evolution_trend"]) != "IMPROVING",
            str(r["hypothesis_id"]),
        )
    )

    out_csv = out_dir / "v11e_knowledge_evolution.csv"
    write_csv(out_csv, evolution)

    maturity_counts: dict[str, int] = {}
    trend_counts: dict[str, int] = {}

    for row in evolution:
        maturity_counts[str(row["maturity_level"])] = maturity_counts.get(str(row["maturity_level"]), 0) + 1
        trend_counts[str(row["evolution_trend"])] = trend_counts.get(str(row["evolution_trend"]), 0) + 1

    report = out_dir / "V11E_KNOWLEDGE_EVOLUTION_TRACKER_REPORT_2026-06-19.md"

    lines = []
    lines.append("# V11E KNOWLEDGE EVOLUTION TRACKER REPORT")
    lines.append("")
    lines.append("Date: 2026-06-19")
    lines.append("Scope: Trade Inspector V11E")
    lines.append("")
    lines.append("## Objective")
    lines.append("")
    lines.append("Track maturity and evolution trend of research knowledge per hypothesis.")
    lines.append("")
    lines.append("## Input")
    lines.append("")
    lines.append(f"- Source file: {source}")
    lines.append(f"- Knowledge entries processed: {len(rows)}")
    lines.append("")
    lines.append("## Maturity Summary")
    lines.append("")
    lines.append("| maturity_level | count |")
    lines.append("|---|---:|")
    for key in sorted(maturity_counts):
        lines.append(f"| {key} | {maturity_counts[key]} |")
    lines.append("")
    lines.append("## Trend Summary")
    lines.append("")
    lines.append("| evolution_trend | count |")
    lines.append("|---|---:|")
    for key in sorted(trend_counts):
        lines.append(f"| {key} | {trend_counts[key]} |")
    lines.append("")
    lines.append("## Top Evolution Items")
    lines.append("")
    lines.append("| rank | hypothesis_id | group | maturity | trend | next_learning_need |")
    lines.append("|---:|---|---|---|---|---|")
    for i, row in enumerate(evolution[:30], 1):
        lines.append(
            f"| {i} | {row['hypothesis_id']} | {row['hypothesis_group']} | "
            f"{row['maturity_level']} | {row['evolution_trend']} | "
            f"{row['next_learning_need']} |"
        )
    lines.append("")
    lines.append("## Guardrail")
    lines.append("")
    lines.append("V11E creates an evolution tracking artifact only. It does not modify the knowledge base or strategy logic.")
    lines.append("")

    report.write_text("\n".join(lines), encoding="utf-8")

    print("V11E knowledge evolution tracker completed")
    print("input_rows:", len(rows))
    print("evolution_rows:", len(evolution))
    for key in sorted(maturity_counts):
        print(f"{key}:", maturity_counts[key])
    print("report:", report)
    print("csv:", out_csv)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
