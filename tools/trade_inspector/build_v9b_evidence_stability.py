#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
V9B Evidence Stability Engine

Compares multiple V9A evidence score CSV files and evaluates
hypothesis stability across runs or archives.

ASCII-only.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from statistics import mean


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


def classify_stability(
    observations: int,
    mean_score: float,
    latest_score: float,
    score_delta: float,
    score_range: float,
    latest_action: str,
    high_warning_count: int,
) -> str:
    if observations < 2:
        return "INSUFFICIENT_HISTORY"

    if high_warning_count > 0:
        if latest_score >= 65:
            return "UNSTABLE"
        return "DECLINING"

    if mean_score >= 75 and score_range <= 10 and latest_action.startswith("VALIDATION_PRIORITY"):
        return "STABLE_STRONG"

    if mean_score >= 60 and score_range <= 15 and latest_action.startswith("VALIDATION_PRIORITY"):
        return "STABLE_MODERATE"

    if score_delta >= 10:
        return "IMPROVING"

    if score_delta <= -10:
        return "DECLINING"

    if observations == 2 and latest_score >= 60:
        return "EMERGING"

    return "UNSTABLE"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        action="append",
        required=True,
        help="Input in form RUN_ID:path/to/v9a_evidence_scores.csv. Can be used multiple times.",
    )
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    runs: list[tuple[str, Path, list[dict[str, str]]]] = []

    for item in args.input:
        if ":" not in item:
            raise SystemExit("Input must use RUN_ID:path format")
        run_id, path_str = item.split(":", 1)
        run_id = run_id.strip()
        path = Path(path_str.strip())
        rows = read_csv(path)

        for rank, row in enumerate(rows, 1):
            row["_run_id"] = run_id
            row["_rank"] = str(rank)

        runs.append((run_id, path, rows))

    grouped: dict[tuple[str, str], list[dict[str, str]]] = {}

    for run_id, _path, rows in runs:
        for row in rows:
            key = (row.get("group_key", ""), row.get("group", ""))
            grouped.setdefault(key, []).append(row)

    output_rows: list[dict[str, object]] = []

    run_order = [r[0] for r in runs]

    for (group_key, group), observations_rows in grouped.items():
        observations_rows.sort(key=lambda r: run_order.index(r["_run_id"]))

        scores = [fnum(r.get("evidence_score")) for r in observations_rows]
        ranks = [int(fnum(r.get("_rank"))) for r in observations_rows]

        first = observations_rows[0]
        latest = observations_rows[-1]

        observations = len(observations_rows)
        first_score = scores[0]
        latest_score = scores[-1]
        mean_score = mean(scores)
        min_score = min(scores)
        max_score = max(scores)
        score_range = max_score - min_score
        score_delta = latest_score - first_score

        rank_best = min(ranks)
        rank_worst = max(ranks)
        rank_latest = ranks[-1]
        rank_drift = rank_latest - ranks[0]

        high_warning_count = sum(1 for r in observations_rows if r.get("warning_level") == "HIGH")
        validation_priority_count = sum(
            1 for r in observations_rows
            if str(r.get("recommended_action", "")).startswith("VALIDATION_PRIORITY")
        )

        stable_action_count = sum(
            1 for r in observations_rows
            if r.get("recommended_action") == latest.get("recommended_action")
        )

        stability_class = classify_stability(
            observations=observations,
            mean_score=mean_score,
            latest_score=latest_score,
            score_delta=score_delta,
            score_range=score_range,
            latest_action=latest.get("recommended_action", ""),
            high_warning_count=high_warning_count,
        )

        output_rows.append(
            {
                "group_key": group_key,
                "group": group,
                "observations": observations,
                "first_seen_run": first["_run_id"],
                "last_seen_run": latest["_run_id"],
                "first_evidence_score": round(first_score, 4),
                "latest_evidence_score": round(latest_score, 4),
                "mean_evidence_score": round(mean_score, 4),
                "min_evidence_score": round(min_score, 4),
                "max_evidence_score": round(max_score, 4),
                "evidence_score_range": round(score_range, 4),
                "evidence_score_delta": round(score_delta, 4),
                "rank_best": rank_best,
                "rank_worst": rank_worst,
                "rank_latest": rank_latest,
                "rank_drift": rank_drift,
                "latest_evidence_class": latest.get("evidence_class", ""),
                "latest_recommended_action": latest.get("recommended_action", ""),
                "latest_warning_level": latest.get("warning_level", ""),
                "high_warning_count": high_warning_count,
                "validation_priority_count": validation_priority_count,
                "stable_action_count": stable_action_count,
                "stability_class": stability_class,
            }
        )

    output_rows.sort(
        key=lambda r: (
            str(r["stability_class"]) not in {"STABLE_STRONG", "STABLE_MODERATE", "IMPROVING"},
            -float(r["mean_evidence_score"]),
            int(r["rank_latest"]),
        )
    )

    out_csv = out_dir / "v9b_evidence_stability.csv"
    write_csv(out_csv, output_rows)

    summary_counts: dict[str, int] = {}
    for row in output_rows:
        cls = str(row["stability_class"])
        summary_counts[cls] = summary_counts.get(cls, 0) + 1

    report = out_dir / "V9B_EVIDENCE_STABILITY_REPORT_2026-06-18.md"

    lines: list[str] = []
    lines.append("# V9B EVIDENCE STABILITY REPORT")
    lines.append("")
    lines.append("Date: 2026-06-18")
    lines.append("Scope: Trade Inspector V9B")
    lines.append("")
    lines.append("## Objective")
    lines.append("")
    lines.append("Evaluate whether evidence-ranked hypotheses remain stable across multiple V9A evidence runs.")
    lines.append("")
    lines.append("## Inputs")
    lines.append("")
    for run_id, path, rows in runs:
        lines.append(f"- {run_id}: {path} ({len(rows)} hypotheses)")
    lines.append("")
    lines.append("## Stability Class Summary")
    lines.append("")
    lines.append("| stability_class | count |")
    lines.append("|---|---:|")
    for cls, count in sorted(summary_counts.items()):
        lines.append(f"| {cls} | {count} |")
    lines.append("")
    lines.append("## Top Stability-Ranked Hypotheses")
    lines.append("")
    lines.append("| rank | group_key | group | observations | mean_score | latest_score | delta | rank_latest | stability_class | latest_action |")
    lines.append("|---:|---|---|---:|---:|---:|---:|---:|---|---|")

    for i, row in enumerate(output_rows[:25], 1):
        lines.append(
            f"| {i} | {row['group_key']} | {row['group']} | {row['observations']} | "
            f"{row['mean_evidence_score']} | {row['latest_evidence_score']} | "
            f"{row['evidence_score_delta']} | {row['rank_latest']} | "
            f"{row['stability_class']} | {row['latest_recommended_action']} |"
        )

    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    lines.append("- V9B is a stability and reproducibility layer.")
    lines.append("- Single-observation hypotheses remain INSUFFICIENT_HISTORY.")
    lines.append("- Stable moderate or strong hypotheses should be considered before unstable high-score hypotheses.")
    lines.append("- V9B does not approve live strategy changes.")
    lines.append("")
    lines.append("## Generated Files")
    lines.append("")
    lines.append("- v9b_evidence_stability.csv")
    lines.append("- V9B_EVIDENCE_STABILITY_REPORT_2026-06-18.md")
    lines.append("")

    report.write_text("\n".join(lines), encoding="utf-8")

    print("V9B evidence stability completed")
    print("runs:", len(runs))
    print("hypotheses_total:", len(output_rows))
    print("report:", report)
    print("csv:", out_csv)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
