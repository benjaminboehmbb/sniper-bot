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


def index_by_hypothesis(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {row.get("hypothesis_id", ""): row for row in rows if row.get("hypothesis_id", "")}


def consistency_score(cls: str) -> float:
    return {
        "CONSISTENT": 35.0,
        "NEEDS_MORE_EVIDENCE": 10.0,
        "PENDING_REPLAY": 5.0,
        "MANUAL_REVIEW": -5.0,
        "CONTRADICTORY": -25.0,
        "BLOCKED_CONFLICT": -40.0,
    }.get(cls, -10.0)


def maturity_score(maturity: str) -> float:
    return {
        "VALIDATED": 30.0,
        "DEVELOPING": 20.0,
        "NEW": 5.0,
        "PENDING": 0.0,
        "DEGRADED": -20.0,
        "BLOCKED": -35.0,
    }.get(maturity, 0.0)


def trend_score(trend: str) -> float:
    return {
        "IMPROVING": 25.0,
        "STABLE": 10.0,
        "INSUFFICIENT_HISTORY": 0.0,
        "DECLINING": -20.0,
        "BLOCKED": -30.0,
    }.get(trend, 0.0)


def priority_class(score: float, consistency: str, maturity: str, trend: str) -> str:
    if consistency == "BLOCKED_CONFLICT" or maturity == "BLOCKED" or trend == "BLOCKED":
        return "BLOCKED"

    if consistency == "CONTRADICTORY":
        return "DEPRIORITIZE"

    if score >= 75:
        return "PRIORITY_HIGH"

    if score >= 50:
        return "PRIORITY_MEDIUM"

    if score >= 25:
        return "WATCHLIST"

    return "DEPRIORITIZE"


def recommended_next_action(priority: str, consistency: str, maturity: str, trend: str) -> str:
    if priority == "PRIORITY_HIGH":
        return "prepare_controlled_validation_or_replay_execution"

    if priority == "PRIORITY_MEDIUM":
        return "keep_in_next_validation_batch"

    if priority == "WATCHLIST":
        return "collect_more_evidence_before_validation"

    if priority == "BLOCKED":
        return "resolve_blocker_before_any_validation"

    if consistency == "CONTRADICTORY":
        return "manual_review_required_before_reuse"

    if maturity == "DEGRADED" or trend == "DECLINING":
        return "deprioritize_and_review_failure_causes"

    return "do_not_prioritize_now"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--v11d-csv", required=True)
    parser.add_argument("--v11e-csv", required=True)
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()

    v11d_csv = Path(args.v11d_csv)
    v11e_csv = Path(args.v11e_csv)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    d_rows = read_csv(v11d_csv)
    e_rows = read_csv(v11e_csv)

    d_map = index_by_hypothesis(d_rows)
    e_map = index_by_hypothesis(e_rows)

    ids = sorted(set(d_map) | set(e_map))

    prioritized: list[dict[str, object]] = []

    for hid in ids:
        d = d_map.get(hid, {})
        e = e_map.get(hid, {})

        group = e.get("hypothesis_group") or d.get("hypothesis_group", "")

        k_score = num(e.get("knowledge_score") or d.get("knowledge_score"))
        success = num(e.get("successful_validations") or d.get("successful_validations"))
        fail = num(e.get("failed_validations") or d.get("failed_validations"))

        consistency = d.get("consistency_class", "UNKNOWN")
        maturity = e.get("maturity_level", "UNKNOWN")
        trend = e.get("evolution_trend", "UNKNOWN")

        score = (
            50.0
            + consistency_score(consistency)
            + maturity_score(maturity)
            + trend_score(trend)
            + (k_score * 5.0)
            + (success * 2.0)
            - (fail * 3.0)
        )

        if score < 0:
            score = 0.0
        if score > 100:
            score = 100.0

        pclass = priority_class(score, consistency, maturity, trend)

        prioritized.append(
            {
                "hypothesis_id": hid,
                "hypothesis_group": group,
                "priority_score": round(score, 4),
                "priority_class": pclass,
                "recommended_next_action": recommended_next_action(pclass, consistency, maturity, trend),
                "consistency_class": consistency,
                "consistency_reason": d.get("consistency_reason", ""),
                "maturity_level": maturity,
                "evolution_trend": trend,
                "next_learning_need": e.get("next_learning_need", ""),
                "knowledge_score": k_score,
                "successful_validations": success,
                "failed_validations": fail,
            }
        )

    prioritized.sort(
        key=lambda r: (
            {
                "PRIORITY_HIGH": 0,
                "PRIORITY_MEDIUM": 1,
                "WATCHLIST": 2,
                "DEPRIORITIZE": 3,
                "BLOCKED": 4,
            }.get(str(r["priority_class"]), 9),
            -float(r["priority_score"]),
            str(r["hypothesis_id"]),
        )
    )

    out_csv = out_dir / "v11f_hypothesis_priorities.csv"
    write_csv(out_csv, prioritized)

    counts: dict[str, int] = {}
    for row in prioritized:
        key = str(row["priority_class"])
        counts[key] = counts.get(key, 0) + 1

    report = out_dir / "V11F_HYPOTHESIS_PRIORITIZATION_ENGINE_REPORT_2026-06-19.md"

    lines: list[str] = []
    lines.append("# V11F HYPOTHESIS PRIORITIZATION ENGINE REPORT")
    lines.append("")
    lines.append("Date: 2026-06-19")
    lines.append("Scope: Trade Inspector V11F")
    lines.append("")
    lines.append("## Objective")
    lines.append("")
    lines.append("Prioritize hypotheses using knowledge consistency and knowledge evolution.")
    lines.append("")
    lines.append("## Input")
    lines.append("")
    lines.append(f"- V11D source: {v11d_csv}")
    lines.append(f"- V11E source: {v11e_csv}")
    lines.append(f"- Hypotheses prioritized: {len(prioritized)}")
    lines.append("")
    lines.append("## Priority Summary")
    lines.append("")
    lines.append("| priority_class | count |")
    lines.append("|---|---:|")
    for key in sorted(counts):
        lines.append(f"| {key} | {counts[key]} |")
    lines.append("")
    lines.append("## Top Priorities")
    lines.append("")
    lines.append("| rank | hypothesis_id | group | score | priority | next_action |")
    lines.append("|---:|---|---|---:|---|---|")
    for i, row in enumerate(prioritized[:30], 1):
        lines.append(
            f"| {i} | {row['hypothesis_id']} | {row['hypothesis_group']} | "
            f"{row['priority_score']} | {row['priority_class']} | "
            f"{row['recommended_next_action']} |"
        )
    lines.append("")
    lines.append("## Guardrail")
    lines.append("")
    lines.append("V11F creates a prioritized research queue only. It does not modify strategy logic.")
    lines.append("")

    report.write_text("\n".join(lines), encoding="utf-8")

    print("V11F hypothesis prioritization engine completed")
    print("v11d_rows:", len(d_rows))
    print("v11e_rows:", len(e_rows))
    print("prioritized:", len(prioritized))
    for key in sorted(counts):
        print(f"{key}:", counts[key])
    print("report:", report)
    print("csv:", out_csv)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
