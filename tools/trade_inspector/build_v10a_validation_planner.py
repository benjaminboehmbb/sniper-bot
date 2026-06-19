#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Trade Inspector V10A

Validation Planner

Converts V9G research decisions into a concrete validation plan.

ASCII only.
"""

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


def fnum(value: object, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except Exception:
        return default


def validation_phase(decision: str, portfolio_class: str) -> str:
    if decision == "RUN_CONTROLLED_VALIDATION":
        return "CONTROLLED_REPLAY_READY"
    if decision == "PREPARE_VALIDATION_DESIGN":
        return "DESIGN_ONLY"
    if decision == "COLLECT_MORE_ARCHIVES":
        return "ARCHIVE_EXPANSION_REQUIRED"
    if decision == "REJECT_FOR_NOW":
        return "REJECTED"
    if portfolio_class == "PRIORITY_1":
        return "RUNTIME_VALIDATION_READY"
    return "DESIGN_ONLY"


def priority(decision: str, portfolio_score: float) -> int:
    if decision == "RUN_CONTROLLED_VALIDATION":
        return 1
    if decision == "PREPARE_VALIDATION_DESIGN":
        return 2
    if decision == "COLLECT_MORE_ARCHIVES":
        return 3
    if portfolio_score >= 60:
        return 3
    return 5


def required_archives(decision: str, portfolio_class: str) -> int:
    if decision == "RUN_CONTROLLED_VALIDATION":
        return 2
    if decision == "PREPARE_VALIDATION_DESIGN":
        return 3
    if decision == "COLLECT_MORE_ARCHIVES":
        return 4
    if portfolio_class in {"PRIORITY_1", "PRIORITY_2"}:
        return 3
    return 0


def required_trades(decision: str, portfolio_class: str) -> int:
    if decision == "RUN_CONTROLLED_VALIDATION":
        return 500
    if decision == "PREPARE_VALIDATION_DESIGN":
        return 750
    if decision == "COLLECT_MORE_ARCHIVES":
        return 1000
    if portfolio_class in {"PRIORITY_1", "PRIORITY_2"}:
        return 750
    return 0


def metrics_for_group(group: str) -> str:
    g = group.lower()

    metrics = [
        "trade_count",
        "winrate",
        "pnl_pct_mean",
        "pnl_pct_median",
        "profit_factor",
        "max_drawdown_proxy",
        "mfe_mae_ratio",
        "opportunity_loss",
    ]

    if "early_exit" in g:
        metrics.extend(["exit_efficiency", "future_return_24h", "future_return_72h"])

    if "risk" in g or "atr" in g:
        metrics.extend(["adverse_move", "risk_label_distribution", "atr_context"])

    if "bull" in g or "bear" in g or "aligned" in g:
        metrics.extend(["regime_alignment", "regime_specific_pnl"])

    return ",".join(dict.fromkeys(metrics))


def acceptance_criteria(decision: str, group: str) -> str:
    base = [
        "sample_size_requirement_met",
        "no_high_warning_conflict",
        "positive_or_neutral_pnl_edge",
        "no_drawdown_deterioration",
    ]

    g = group.lower()

    if "early_exit" in g:
        base.append("exit_efficiency_improves_or_opportunity_loss_reduces")

    if "risk" in g or "atr" in g:
        base.append("adverse_move_reduces_or_profit_factor_improves")

    if decision == "RUN_CONTROLLED_VALIDATION":
        base.append("replay_result_passes_before_runtime")

    return ",".join(base)


def failure_criteria(group: str) -> str:
    criteria = [
        "pnl_edge_turns_negative",
        "profit_factor_degrades",
        "drawdown_proxy_increases",
        "sample_support_collapses",
    ]

    if "early_exit" in group.lower():
        criteria.append("opportunity_loss_increases")

    return ",".join(criteria)


def effort(decision: str, conflict_penalty: float) -> str:
    if decision == "REJECT_FOR_NOW":
        return "none"
    if conflict_penalty >= 30:
        return "high"
    if decision == "RUN_CONTROLLED_VALIDATION":
        return "medium"
    if decision == "PREPARE_VALIDATION_DESIGN":
        return "medium"
    return "low"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--v9g-csv", required=True)
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()

    v9g_csv = Path(args.v9g_csv)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = read_csv(v9g_csv)

    plan: list[dict[str, object]] = []

    for i, row in enumerate(rows, 1):
        decision = row.get("research_decision", "")
        group = row.get("group", "")
        portfolio_class = row.get("portfolio_class", "")
        portfolio_score = fnum(row.get("portfolio_score"))
        conflict_penalty = fnum(row.get("conflict_penalty"))

        phase = validation_phase(decision, portfolio_class)
        validation_id = f"VAL10A-{i:03d}"

        plan.append(
            {
                "validation_id": validation_id,
                "hypothesis_id": row.get("hypothesis_id", ""),
                "group": group,
                "research_decision": decision,
                "decision_reason": row.get("decision_reason", ""),
                "portfolio_score": round(portfolio_score, 4),
                "portfolio_class": portfolio_class,
                "conflict_penalty": round(conflict_penalty, 4),
                "validation_phase": phase,
                "validation_priority": priority(decision, portfolio_score),
                "required_archives_min": required_archives(decision, portfolio_class),
                "required_trades_min": required_trades(decision, portfolio_class),
                "required_metrics": metrics_for_group(group),
                "acceptance_criteria": acceptance_criteria(decision, group),
                "failure_criteria": failure_criteria(group),
                "blocking_dependencies": "none" if conflict_penalty <= 20 else "resolve_conflict_penalty",
                "estimated_effort": effort(decision, conflict_penalty),
                "documentation_required": "yes",
                "execution_environment": "Workstation WSL",
            }
        )

    plan.sort(
        key=lambda r: (
            int(r["validation_priority"]),
            -float(r["portfolio_score"]),
        )
    )

    out_csv = out_dir / "v10a_validation_plan.csv"
    write_csv(out_csv, plan)

    phase_counts: dict[str, int] = {}
    for row in plan:
        key = str(row["validation_phase"])
        phase_counts[key] = phase_counts.get(key, 0) + 1

    report = out_dir / "V10A_VALIDATION_PLANNER_REPORT_2026-06-19.md"

    lines: list[str] = []
    lines.append("# V10A VALIDATION PLANNER REPORT")
    lines.append("")
    lines.append("Date: 2026-06-19")
    lines.append("Scope: Trade Inspector V10A")
    lines.append("")
    lines.append("## Objective")
    lines.append("")
    lines.append("Convert V9G research decisions into a structured validation plan.")
    lines.append("")
    lines.append("## Input")
    lines.append("")
    lines.append(f"- Source file: {v9g_csv}")
    lines.append(f"- Decisions processed: {len(rows)}")
    lines.append("")
    lines.append("## Validation Phase Summary")
    lines.append("")
    lines.append("| validation_phase | count |")
    lines.append("|---|---:|")
    for key in sorted(phase_counts):
        lines.append(f"| {key} | {phase_counts[key]} |")
    lines.append("")
    lines.append("## Top Validation Plan Items")
    lines.append("")
    lines.append("| rank | validation_id | group | phase | priority | required_archives | required_trades | effort |")
    lines.append("|---:|---|---|---|---:|---:|---:|---|")

    for i, row in enumerate(plan[:25], 1):
        lines.append(
            f"| {i} | {row['validation_id']} | {row['group']} | "
            f"{row['validation_phase']} | {row['validation_priority']} | "
            f"{row['required_archives_min']} | {row['required_trades_min']} | "
            f"{row['estimated_effort']} |"
        )

    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    lines.append("- CONTROLLED_REPLAY_READY items can be converted into concrete replay validation specs.")
    lines.append("- DESIGN_ONLY items need a validation design before execution.")
    lines.append("- ARCHIVE_EXPANSION_REQUIRED items need more archive/trade support first.")
    lines.append("- REJECTED items should not consume validation effort now.")
    lines.append("")
    lines.append("## Guardrail")
    lines.append("")
    lines.append("V10A does not execute validations and does not modify live strategy logic.")
    lines.append("")
    lines.append("## Generated Files")
    lines.append("")
    lines.append("- v10a_validation_plan.csv")
    lines.append("- V10A_VALIDATION_PLANNER_REPORT_2026-06-19.md")
    lines.append("")

    report.write_text("\n".join(lines), encoding="utf-8")

    print("V10A validation planner completed")
    print("input_rows:", len(rows))
    print("plan_rows:", len(plan))
    for key in sorted(phase_counts):
        print(f"{key}:", phase_counts[key])
    print("report:", report)
    print("csv:", out_csv)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
