#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Trade Inspector V9F

Experiment Portfolio Optimizer.

Purpose:
- Combine V9D cross-archive consistency with V9E conflict evidence.
- Produce a stable, context-rich experiment portfolio.
- Avoid rank-order hypothesis ID coupling between V9D and V9E.

ASCII only.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
from typing import Any

from tools.trade_inspector.common.io import read_csv, write_csv
from tools.trade_inspector.common.utils import to_float as fnum


PORTFOLIO_FIELDS = [
    "hypothesis_id",
    "legacy_rank_id",
    "group_key",
    "group",
    "observations",
    "mean_evidence_score",
    "latest_evidence_score",
    "evidence_score_range",
    "evidence_score_delta",
    "rank_latest",
    "rank_drift",
    "stability_class",
    "latest_recommended_action",
    "latest_warning_level",
    "consistency_score",
    "consistency_class",
    "v9d_recommended_action",
    "support_component",
    "score_component",
    "latest_component",
    "volatility_component",
    "rank_component",
    "action_stability_component",
    "validation_component",
    "warning_component",
    "trend_component",
    "conflict_penalty",
    "conflict_count",
    "redundancy_count",
    "synergy_count",
    "portfolio_score",
    "portfolio_class",
    "portfolio_reason",
]





def stable_key(group_key: str, group: str) -> str:
    return f"{group_key.strip()}||{group.strip()}".lower()


def stable_hypothesis_id(group_key: str, group: str) -> str:
    raw = stable_key(group_key, group)
    digest = hashlib.sha1(raw.encode("utf-8")).hexdigest()[:12]
    return f"HYP-{digest}"


def conflict_penalty_for_relation(relation: str) -> tuple[float, str]:
    if relation == "MUTUALLY_EXCLUSIVE_CONTEXT":
        return 25.0, "hard_context_conflict"
    if relation == "POTENTIAL_CONFLICT":
        return 20.0, "potential_conflict"
    if relation == "REDUNDANT_PARENT_CHILD":
        return 10.0, "redundant_parent_child"
    return 0.0, "no_penalty"


def classify_portfolio(score: float, consistency_class: str, warning: str, observations: float) -> str:
    if warning == "HIGH":
        return "REJECT"
    if observations < 2:
        return "WATCHLIST"
    if consistency_class in {"REJECT", "INCONSISTENT"}:
        return "REJECT"
    if score >= 80.0:
        return "PRIORITY_1"
    if score >= 60.0:
        return "PRIORITY_2"
    if score >= 40.0:
        return "WATCHLIST"
    return "REJECT"


def portfolio_reason(row: dict[str, str], score: float, penalty: float) -> str:
    consistency_class = row.get("consistency_class", "")
    stability_class = row.get("stability_class", "")
    warning = row.get("latest_warning_level", "")
    observations = fnum(row.get("observations"))

    if warning == "HIGH":
        return "rejected_due_to_high_warning_level"
    if observations < 2:
        return "watchlist_due_to_insufficient_cross_archive_history"
    if consistency_class in {"REJECT", "INCONSISTENT"}:
        return "rejected_due_to_consistency_class"
    if penalty >= 25:
        return "downgraded_due_to_hard_or_repeated_conflicts"
    if score >= 80:
        return f"high_priority_consistent_candidate_{stability_class.lower() or 'unknown_stability'}"
    if score >= 60:
        return "medium_priority_candidate_prepare_before_validation"
    if score >= 40:
        return "watchlist_candidate_requires_more_evidence"
    return "low_priority_candidate"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--v9d-csv", required=True)
    parser.add_argument("--v9e-csv", required=True)
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()

    v9d_csv = Path(args.v9d_csv)
    v9e_csv = Path(args.v9e_csv)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    consistency = read_csv(v9d_csv)
    conflicts = read_csv(v9e_csv)

    penalty_by_key: dict[str, float] = {}
    conflict_count_by_key: dict[str, int] = {}
    redundancy_count_by_key: dict[str, int] = {}
    synergy_count_by_key: dict[str, int] = {}

    for row in conflicts:
        relation = row.get("relationship_class", "")
        penalty, _reason = conflict_penalty_for_relation(relation)

        a_key = stable_key(
            row.get("hypothesis_a_group_key", ""),
            row.get("hypothesis_a_group", ""),
        )
        b_key = stable_key(
            row.get("hypothesis_b_group_key", ""),
            row.get("hypothesis_b_group", ""),
        )

        for key in (a_key, b_key):
            if not key or key == "||":
                continue

            penalty_by_key[key] = penalty_by_key.get(key, 0.0) + penalty

            if relation in {"MUTUALLY_EXCLUSIVE_CONTEXT", "POTENTIAL_CONFLICT"}:
                conflict_count_by_key[key] = conflict_count_by_key.get(key, 0) + 1
            elif relation == "REDUNDANT_PARENT_CHILD":
                redundancy_count_by_key[key] = redundancy_count_by_key.get(key, 0) + 1
            elif relation == "SYNERGY":
                synergy_count_by_key[key] = synergy_count_by_key.get(key, 0) + 1

    portfolio: list[dict[str, Any]] = []

    for i, row in enumerate(consistency, start=1):
        group_key = row.get("group_key", "")
        group = row.get("group", "")
        key = stable_key(group_key, group)

        conflict_penalty = penalty_by_key.get(key, 0.0)
        consistency_score = fnum(row.get("consistency_score"))
        synergy_bonus = min(float(synergy_count_by_key.get(key, 0)) * 2.0, 10.0)

        score = consistency_score - conflict_penalty + synergy_bonus
        score = max(0.0, min(100.0, score))

        consistency_class = row.get("consistency_class", "")
        warning = row.get("latest_warning_level", "")
        observations = fnum(row.get("observations"))

        cls = classify_portfolio(score, consistency_class, warning, observations)

        out_row: dict[str, Any] = {
            "hypothesis_id": stable_hypothesis_id(group_key, group),
            "legacy_rank_id": f"H{i:03d}",
            "group_key": group_key,
            "group": group,
            "observations": row.get("observations", ""),
            "mean_evidence_score": row.get("mean_evidence_score", ""),
            "latest_evidence_score": row.get("latest_evidence_score", ""),
            "evidence_score_range": row.get("evidence_score_range", ""),
            "evidence_score_delta": row.get("evidence_score_delta", ""),
            "rank_latest": row.get("rank_latest", ""),
            "rank_drift": row.get("rank_drift", ""),
            "stability_class": row.get("stability_class", ""),
            "latest_recommended_action": row.get("latest_recommended_action", ""),
            "latest_warning_level": warning,
            "consistency_score": row.get("consistency_score", ""),
            "consistency_class": consistency_class,
            "v9d_recommended_action": row.get("recommended_action", ""),
            "support_component": row.get("support_component", ""),
            "score_component": row.get("score_component", ""),
            "latest_component": row.get("latest_component", ""),
            "volatility_component": row.get("volatility_component", ""),
            "rank_component": row.get("rank_component", ""),
            "action_stability_component": row.get("action_stability_component", ""),
            "validation_component": row.get("validation_component", ""),
            "warning_component": row.get("warning_component", ""),
            "trend_component": row.get("trend_component", ""),
            "conflict_penalty": round(conflict_penalty, 4),
            "conflict_count": conflict_count_by_key.get(key, 0),
            "redundancy_count": redundancy_count_by_key.get(key, 0),
            "synergy_count": synergy_count_by_key.get(key, 0),
            "portfolio_score": round(score, 4),
            "portfolio_class": cls,
            "portfolio_reason": portfolio_reason(row, score, conflict_penalty),
        }

        portfolio.append(out_row)

    portfolio.sort(
        key=lambda r: (
            {"PRIORITY_1": 1, "PRIORITY_2": 2, "WATCHLIST": 3, "REJECT": 4}.get(str(r["portfolio_class"]), 9),
            -fnum(r["portfolio_score"]),
            str(r["hypothesis_id"]),
        )
    )

    csv_out = out_dir / "v9f_experiment_portfolio.csv"
    report = out_dir / "V9F_EXPERIMENT_PORTFOLIO_REPORT_2026-06-18.md"

    write_csv(csv_out, portfolio, PORTFOLIO_FIELDS)

    counts: dict[str, int] = {}
    for row in portfolio:
        key = str(row["portfolio_class"])
        counts[key] = counts.get(key, 0) + 1

    lines: list[str] = []
    lines.append("# V9F EXPERIMENT PORTFOLIO REPORT")
    lines.append("")
    lines.append("Date: 2026-06-18")
    lines.append("Device: G15 / AR15")
    lines.append("Environment: WSL")
    lines.append("Scope: Trade Inspector V9F")
    lines.append("")
    lines.append("## Objective")
    lines.append("")
    lines.append("Build a stable experiment portfolio from V9D consistency and V9E conflict evidence.")
    lines.append("")
    lines.append("## Review Fixes Included")
    lines.append("")
    lines.append("- Uses stable content-derived hypothesis_id instead of rank-order H001/H002 coupling.")
    lines.append("- Applies V9E penalties by group_key/group natural key, not by unstable row order.")
    lines.append("- Preserves V9D context columns for downstream V9G/V10 decisions.")
    lines.append("- Writes a header-only CSV even when there are no portfolio rows.")
    lines.append("")
    lines.append("## Portfolio Summary")
    lines.append("")
    for key in ("PRIORITY_1", "PRIORITY_2", "WATCHLIST", "REJECT"):
        lines.append(f"- {key}: {counts.get(key, 0)}")
    lines.append("")
    lines.append("## Top Portfolio")
    lines.append("")
    lines.append("| rank | hypothesis_id | group_key | group | score | class | penalty | reason |")
    lines.append("|---:|---|---|---|---:|---|---:|---|")
    for i, row in enumerate(portfolio[:20], 1):
        lines.append(
            f"| {i} | {row['hypothesis_id']} | {row['group_key']} | {row['group']} | "
            f"{row['portfolio_score']} | {row['portfolio_class']} | "
            f"{row['conflict_penalty']} | {row['portfolio_reason']} |"
        )
    lines.append("")
    lines.append("## Guardrail")
    lines.append("")
    lines.append("V9F does not approve live strategy changes. It only ranks research candidates.")
    lines.append("")

    report.write_text("\n".join(lines), encoding="utf-8")

    print("V9F portfolio optimizer completed")
    print("input_consistency_rows:", len(consistency))
    print("input_conflict_rows:", len(conflicts))
    print("portfolio_rows:", len(portfolio))
    print("report:", report)
    print("csv:", csv_out)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
