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


def classify(row: dict[str, str]) -> tuple[str, str, int]:
    score = num(row.get("knowledge_score"))
    success = num(row.get("successful_validations"))
    fail = num(row.get("failed_validations"))
    pending = num(row.get("pending_validations"))
    blocked = num(row.get("blocked_events"))
    updates = num(row.get("knowledge_updates"))
    status = row.get("research_status", "")

    if blocked > 0 and score > 0:
        return "BLOCKED_CONFLICT", "positive_score_but_blocked_events_exist", 1

    if status in {"STRONG_EVIDENCE", "MODERATE_EVIDENCE"} and score < 0:
        return "CONTRADICTORY", "positive_status_with_negative_score", 1

    if status == "WEAK_EVIDENCE" and score > 0:
        return "CONTRADICTORY", "weak_status_with_positive_score", 1

    if pending > 0 and score >= 2:
        return "PENDING_REPLAY", "pending_replay_despite_positive_evidence", 2

    if updates <= 1 and status not in {"BLOCKED", "PENDING"}:
        return "NEEDS_MORE_EVIDENCE", "single_update_not_enough_for_stable_knowledge", 3

    if success > 0 and fail > 0:
        return "MANUAL_REVIEW", "mixed_success_and_failure_history", 2

    if status == "BLOCKED":
        return "BLOCKED_CONFLICT", "blocked_status_requires_resolution", 2

    if status == "PENDING":
        return "PENDING_REPLAY", "pending_status_requires_real_replay_or_more_data", 3

    return "CONSISTENT", "no_internal_knowledge_conflict_detected", 4


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--v11c-csv", required=True)
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()

    source = Path(args.v11c_csv)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = read_csv(source)
    reviewed: list[dict[str, object]] = []

    for row in rows:
        consistency_class, reason, priority = classify(row)

        reviewed.append(
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
                "consistency_class": consistency_class,
                "consistency_reason": reason,
                "review_priority": priority,
            }
        )

    reviewed.sort(
        key=lambda r: (
            int(r["review_priority"]),
            str(r["hypothesis_id"]),
        )
    )

    out_csv = out_dir / "v11d_knowledge_consistency.csv"
    write_csv(out_csv, reviewed)

    counts: dict[str, int] = {}
    for row in reviewed:
        key = str(row["consistency_class"])
        counts[key] = counts.get(key, 0) + 1

    report = out_dir / "V11D_KNOWLEDGE_CONSISTENCY_ENGINE_REPORT_2026-06-19.md"

    lines = []
    lines.append("# V11D KNOWLEDGE CONSISTENCY ENGINE REPORT")
    lines.append("")
    lines.append("Date: 2026-06-19")
    lines.append("Scope: Trade Inspector V11D")
    lines.append("")
    lines.append("## Objective")
    lines.append("")
    lines.append("Evaluate the internal consistency of the V11C research knowledge base.")
    lines.append("")
    lines.append("## Input")
    lines.append("")
    lines.append(f"- Source file: {source}")
    lines.append(f"- Knowledge entries reviewed: {len(rows)}")
    lines.append("")
    lines.append("## Consistency Summary")
    lines.append("")
    lines.append("| consistency_class | count |")
    lines.append("|---|---:|")
    for key in sorted(counts):
        lines.append(f"| {key} | {counts[key]} |")
    lines.append("")
    lines.append("## Highest Priority Reviews")
    lines.append("")
    lines.append("| rank | hypothesis_id | group | research_status | consistency_class | reason |")
    lines.append("|---:|---|---|---|---|---|")
    for i, row in enumerate(reviewed[:30], 1):
        lines.append(
            f"| {i} | {row['hypothesis_id']} | {row['hypothesis_group']} | "
            f"{row['research_status']} | {row['consistency_class']} | {row['consistency_reason']} |"
        )
    lines.append("")
    lines.append("## Guardrail")
    lines.append("")
    lines.append("V11D creates a consistency review artifact only. It does not modify the knowledge base.")
    lines.append("")

    report.write_text("\n".join(lines), encoding="utf-8")

    print("V11D knowledge consistency engine completed")
    print("input_rows:", len(rows))
    print("review_rows:", len(reviewed))
    for key in sorted(counts):
        print(f"{key}:", counts[key])
    print("report:", report)
    print("csv:", out_csv)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
