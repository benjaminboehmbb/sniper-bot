#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
V9C Strategy Opportunity Scoring

Turns V9A evidence scores into prioritized strategy-development opportunities.

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


def warning_penalty(warning: str) -> float:
    return {
        "LOW": 0.0,
        "MEDIUM": 12.0,
        "HIGH": 35.0,
    }.get(warning, 20.0)


def complexity_penalty(group_key: str, group: str) -> float:
    text = f"{group_key} {group}".lower()

    if "trade_family" in text:
        return 20.0
    if "entry_score" in text:
        return 12.0
    if "entry_regime" in text:
        return 15.0
    if "risk" in text or "atr" in text:
        return 10.0
    if "ma200" in text or "mfi" in text:
        return 8.0

    return 18.0


def experiment_type(group_key: str, group: str) -> str:
    text = f"{group_key} {group}".lower()

    if "early_exit" in text:
        return "exit_logic_review"
    if "entry_filter_quality" in text:
        return "entry_filter_review"
    if "risk" in text or "good_atr" in text or "bad_atr" in text:
        return "risk_filter_review"
    if "regime" in text or "bull" in text or "bear" in text or "aligned" in text:
        return "regime_alignment_review"
    if "entry_score" in text:
        return "score_threshold_review"
    if "atr" in text:
        return "atr_context_review"

    return "generic_hypothesis_review"


def expected_benefit_proxy(winrate_edge: float, pnl_edge: float, count: float) -> float:
    support_factor = min(count / 400.0, 1.0)
    win_component = clamp(winrate_edge * 250.0, 0.0, 50.0)
    pnl_component = clamp(pnl_edge * 10000.0, 0.0, 50.0)
    return clamp((win_component + pnl_component) * (0.5 + 0.5 * support_factor))


def classify(score: float) -> str:
    if score >= 75:
        return "HIGH_VALUE_EXPERIMENT"
    if score >= 55:
        return "MEDIUM_VALUE_EXPERIMENT"
    if score >= 35:
        return "WATCH_ONLY"
    return "REJECT"


def recommended_next_step(opportunity_class: str, exp_type: str) -> str:
    if opportunity_class == "HIGH_VALUE_EXPERIMENT":
        return f"design_controlled_validation_for_{exp_type}"
    if opportunity_class == "MEDIUM_VALUE_EXPERIMENT":
        return f"prepare_hypothesis_review_for_{exp_type}"
    if opportunity_class == "WATCH_ONLY":
        return "keep_on_watchlist_until_more_archives"
    return "do_not_validate"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--v9a-csv", required=True)
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()

    v9a_csv = Path(args.v9a_csv)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = read_csv(v9a_csv)

    opportunities: list[dict[str, object]] = []

    for row in rows:
        group_key = row.get("group_key", "")
        group = row.get("group", "")
        count = fnum(row.get("count"))
        evidence_score = fnum(row.get("evidence_score"))
        winrate_edge = fnum(row.get("winrate_edge"))
        pnl_edge = fnum(row.get("pnl_edge"))
        warning = row.get("warning_level", "")
        recommended_action = row.get("recommended_action", "")

        exp_type = experiment_type(group_key, group)
        benefit = expected_benefit_proxy(winrate_edge, pnl_edge, count)
        complexity = complexity_penalty(group_key, group)
        warn_penalty = warning_penalty(warning)

        validation_bonus = 0.0
        if recommended_action == "VALIDATION_PRIORITY_HIGH":
            validation_bonus = 15.0
        elif recommended_action == "VALIDATION_PRIORITY_MEDIUM":
            validation_bonus = 8.0
        elif recommended_action == "WATCHLIST_ONLY":
            validation_bonus = 0.0
        else:
            validation_bonus = -10.0

        opportunity_score = clamp(
            0.45 * evidence_score
            + 0.35 * benefit
            + validation_bonus
            - complexity
            - warn_penalty
        )

        opportunity_class = classify(opportunity_score)

        opportunities.append(
            {
                "group_key": group_key,
                "group": group,
                "experiment_type": exp_type,
                "count": int(count),
                "evidence_score": round(evidence_score, 4),
                "expected_benefit_proxy": round(benefit, 4),
                "complexity_penalty": round(complexity, 4),
                "warning_penalty": round(warn_penalty, 4),
                "validation_bonus": round(validation_bonus, 4),
                "opportunity_score": round(opportunity_score, 4),
                "opportunity_class": opportunity_class,
                "recommended_action": recommended_action,
                "recommended_next_step": recommended_next_step(opportunity_class, exp_type),
                "warning_level": warning,
                "evidence_class": row.get("evidence_class", ""),
                "reliability_class": row.get("reliability_class", ""),
                "discovery_status": row.get("discovery_status", ""),
            }
        )

    opportunities.sort(key=lambda r: float(r["opportunity_score"]), reverse=True)

    out_csv = out_dir / "v9c_strategy_opportunities.csv"
    write_csv(out_csv, opportunities)

    class_counts: dict[str, int] = {}
    type_counts: dict[str, int] = {}

    for row in opportunities:
        class_counts[str(row["opportunity_class"])] = class_counts.get(str(row["opportunity_class"]), 0) + 1
        type_counts[str(row["experiment_type"])] = type_counts.get(str(row["experiment_type"]), 0) + 1

    report = out_dir / "V9C_STRATEGY_OPPORTUNITY_REPORT_2026-06-18.md"

    lines: list[str] = []
    lines.append("# V9C STRATEGY OPPORTUNITY REPORT")
    lines.append("")
    lines.append("Date: 2026-06-18")
    lines.append("Device: G15 / AR15")
    lines.append("Environment: WSL")
    lines.append("Scope: Trade Inspector V9C")
    lines.append("")
    lines.append("## Objective")
    lines.append("")
    lines.append("V9C translates V9A evidence-ranked hypotheses into prioritized strategy-development opportunities.")
    lines.append("")
    lines.append("V9C does not approve strategy changes.")
    lines.append("It identifies which hypotheses deserve controlled validation first.")
    lines.append("")
    lines.append("## Input")
    lines.append("")
    lines.append(f"- Source file: {v9a_csv}")
    lines.append(f"- Hypotheses evaluated: {len(opportunities)}")
    lines.append("")
    lines.append("## Opportunity Class Summary")
    lines.append("")
    lines.append("| opportunity_class | count |")
    lines.append("|---|---:|")
    for key in sorted(class_counts):
        lines.append(f"| {key} | {class_counts[key]} |")
    lines.append("")
    lines.append("## Experiment Type Summary")
    lines.append("")
    lines.append("| experiment_type | count |")
    lines.append("|---|---:|")
    for key in sorted(type_counts):
        lines.append(f"| {key} | {type_counts[key]} |")
    lines.append("")
    lines.append("## Top Strategy Opportunities")
    lines.append("")
    lines.append("| rank | group_key | group | experiment_type | opportunity_score | opportunity_class | next_step |")
    lines.append("|---:|---|---|---|---:|---|---|")

    for i, row in enumerate(opportunities[:20], 1):
        lines.append(
            f"| {i} | {row['group_key']} | {row['group']} | {row['experiment_type']} | "
            f"{row['opportunity_score']} | {row['opportunity_class']} | {row['recommended_next_step']} |"
        )

    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    lines.append("- HIGH_VALUE_EXPERIMENT means the hypothesis deserves a controlled validation design.")
    lines.append("- MEDIUM_VALUE_EXPERIMENT means the hypothesis is potentially useful but should be reviewed before testing.")
    lines.append("- WATCH_ONLY means more data is required.")
    lines.append("- REJECT means no validation effort should be spent now.")
    lines.append("")
    lines.append("## Guardrail")
    lines.append("")
    lines.append("No live strategy logic should be changed based only on V9C.")
    lines.append("V9C is a prioritization layer for controlled validation.")
    lines.append("")
    lines.append("## Generated Files")
    lines.append("")
    lines.append("- v9c_strategy_opportunities.csv")
    lines.append("- V9C_STRATEGY_OPPORTUNITY_REPORT_2026-06-18.md")
    lines.append("")

    report.write_text("\n".join(lines), encoding="utf-8")

    print("V9C strategy opportunity scoring completed")
    print("input_rows:", len(rows))
    print("opportunities:", len(opportunities))
    for key in sorted(class_counts):
        print(f"{key}:", class_counts[key])
    print("report:", report)
    print("csv:", out_csv)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
