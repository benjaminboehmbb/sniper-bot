#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
V9D Cross-Archive Consistency Engine

Evaluates consistency of V9B evidence stability rows.

ASCII-only.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(f"Missing input file: {path}")
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return

    fields = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def fnum(value: object, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except Exception:
        return default


def clamp(value: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, value))


def consistency_score(row: dict[str, str]) -> tuple[float, dict[str, float]]:
    observations = fnum(row.get("observations"))
    mean_score = fnum(row.get("mean_evidence_score"))
    latest_score = fnum(row.get("latest_evidence_score"))
    score_range = fnum(row.get("evidence_score_range"))
    score_delta = fnum(row.get("evidence_score_delta"))
    rank_drift = abs(fnum(row.get("rank_drift")))
    high_warning_count = fnum(row.get("high_warning_count"))
    validation_priority_count = fnum(row.get("validation_priority_count"))
    stable_action_count = fnum(row.get("stable_action_count"))

    support_component = clamp((observations / 3.0) * 100.0)
    score_component = clamp(mean_score)
    latest_component = clamp(latest_score)
    volatility_component = clamp(100.0 - score_range * 4.0)
    rank_component = clamp(100.0 - rank_drift * 5.0)

    if observations > 0:
        action_stability_component = clamp((stable_action_count / observations) * 100.0)
        validation_component = clamp((validation_priority_count / observations) * 100.0)
    else:
        action_stability_component = 0.0
        validation_component = 0.0

    warning_component = clamp(100.0 - high_warning_count * 35.0)

    if score_delta >= 0:
        trend_component = clamp(60.0 + score_delta * 2.0)
    else:
        trend_component = clamp(60.0 + score_delta * 3.0)

    components = {
        "support_component": support_component,
        "score_component": score_component,
        "latest_component": latest_component,
        "volatility_component": volatility_component,
        "rank_component": rank_component,
        "action_stability_component": action_stability_component,
        "validation_component": validation_component,
        "warning_component": warning_component,
        "trend_component": trend_component,
    }

    score = (
        0.15 * support_component
        + 0.20 * score_component
        + 0.15 * latest_component
        + 0.15 * volatility_component
        + 0.10 * rank_component
        + 0.10 * action_stability_component
        + 0.10 * validation_component
        + 0.03 * warning_component
        + 0.02 * trend_component
    )

    return clamp(score), components


def classify(row: dict[str, str], score: float) -> str:
    observations = fnum(row.get("observations"))
    latest_action = row.get("latest_recommended_action", "")
    latest_warning = row.get("latest_warning_level", "")
    stability_class = row.get("stability_class", "")

    if observations < 2:
        return "INSUFFICIENT_HISTORY"

    if latest_warning == "HIGH":
        return "REJECT"

    if stability_class in {"DECLINING", "UNSTABLE"} and score < 55:
        return "INCONSISTENT"

    if score >= 80 and latest_action.startswith("VALIDATION_PRIORITY"):
        return "CONSISTENT_STRONG"

    if score >= 65 and latest_action.startswith("VALIDATION_PRIORITY"):
        return "CONSISTENT_MODERATE"

    if score >= 50:
        return "CONSISTENT_WATCH"

    return "INCONSISTENT"


def recommended_action(consistency_class: str) -> str:
    if consistency_class == "CONSISTENT_STRONG":
        return "promote_to_controlled_validation_design"
    if consistency_class == "CONSISTENT_MODERATE":
        return "prepare_validation_candidate_review"
    if consistency_class == "CONSISTENT_WATCH":
        return "keep_on_consistency_watchlist"
    if consistency_class == "INSUFFICIENT_HISTORY":
        return "collect_more_archive_observations"
    if consistency_class == "INCONSISTENT":
        return "do_not_prioritize_until_stable"
    return "reject_for_now"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--v9b-csv", required=True)
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()

    v9b_csv = Path(args.v9b_csv)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = read_csv(v9b_csv)

    output_rows: list[dict[str, object]] = []

    for row in rows:
        score, components = consistency_score(row)
        cls = classify(row, score)

        output = {
            "group_key": row.get("group_key", ""),
            "group": row.get("group", ""),
            "observations": int(fnum(row.get("observations"))),
            "mean_evidence_score": round(fnum(row.get("mean_evidence_score")), 4),
            "latest_evidence_score": round(fnum(row.get("latest_evidence_score")), 4),
            "evidence_score_range": round(fnum(row.get("evidence_score_range")), 4),
            "evidence_score_delta": round(fnum(row.get("evidence_score_delta")), 4),
            "rank_latest": int(fnum(row.get("rank_latest"))),
            "rank_drift": int(fnum(row.get("rank_drift"))),
            "stability_class": row.get("stability_class", ""),
            "latest_recommended_action": row.get("latest_recommended_action", ""),
            "latest_warning_level": row.get("latest_warning_level", ""),
            "consistency_score": round(score, 4),
            "consistency_class": cls,
            "recommended_action": recommended_action(cls),
        }

        for key, value in components.items():
            output[key] = round(value, 4)

        output_rows.append(output)

    output_rows.sort(key=lambda r: float(r["consistency_score"]), reverse=True)

    out_csv = out_dir / "v9d_cross_archive_consistency.csv"
    write_csv(out_csv, output_rows)

    class_counts: dict[str, int] = {}
    for row in output_rows:
        key = str(row["consistency_class"])
        class_counts[key] = class_counts.get(key, 0) + 1

    report = out_dir / "V9D_CROSS_ARCHIVE_CONSISTENCY_REPORT_2026-06-18.md"

    lines: list[str] = []
    lines.append("# V9D CROSS-ARCHIVE CONSISTENCY REPORT")
    lines.append("")
    lines.append("Date: 2026-06-18")
    lines.append("Device: G15 / AR15")
    lines.append("Environment: WSL")
    lines.append("Scope: Trade Inspector V9D")
    lines.append("")
    lines.append("## Objective")
    lines.append("")
    lines.append("V9D evaluates whether evidence-ranked hypotheses are consistent across repeated evidence observations.")
    lines.append("")
    lines.append("## Input")
    lines.append("")
    lines.append(f"- Source file: {v9b_csv}")
    lines.append(f"- Hypotheses evaluated: {len(output_rows)}")
    lines.append("")
    lines.append("## Consistency Class Summary")
    lines.append("")
    lines.append("| consistency_class | count |")
    lines.append("|---|---:|")
    for key in sorted(class_counts):
        lines.append(f"| {key} | {class_counts[key]} |")
    lines.append("")
    lines.append("## Top Consistency-Ranked Hypotheses")
    lines.append("")
    lines.append("| rank | group_key | group | observations | consistency_score | consistency_class | stability_class | next_action |")
    lines.append("|---:|---|---|---:|---:|---|---|---|")

    for i, row in enumerate(output_rows[:20], 1):
        lines.append(
            f"| {i} | {row['group_key']} | {row['group']} | {row['observations']} | "
            f"{row['consistency_score']} | {row['consistency_class']} | "
            f"{row['stability_class']} | {row['recommended_action']} |"
        )

    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    lines.append("- V9D checks repeatability and consistency, not profitability by itself.")
    lines.append("- CONSISTENT_STRONG and CONSISTENT_MODERATE candidates may be considered for controlled validation design.")
    lines.append("- INSUFFICIENT_HISTORY means more archive observations are required.")
    lines.append("- REJECT and INCONSISTENT hypotheses should not consume validation effort now.")
    lines.append("")
    lines.append("## Guardrail")
    lines.append("")
    lines.append("No live strategy logic should be changed based only on V9D.")
    lines.append("")
    lines.append("## Generated Files")
    lines.append("")
    lines.append("- v9d_cross_archive_consistency.csv")
    lines.append("- V9D_CROSS_ARCHIVE_CONSISTENCY_REPORT_2026-06-18.md")
    lines.append("")

    report.write_text("\n".join(lines), encoding="utf-8")

    print("V9D cross-archive consistency completed")
    print("input_rows:", len(rows))
    print("consistency_rows:", len(output_rows))
    for key in sorted(class_counts):
        print(f"{key}:", class_counts[key])
    print("report:", report)
    print("csv:", out_csv)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
