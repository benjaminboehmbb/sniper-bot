#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from datetime import date
from pathlib import Path


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(f"Missing input file: {path}")
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def pick(row: dict[str, str], keys: list[str], default: str = "") -> str:
    for key in keys:
        value = row.get(key)
        if value not in (None, ""):
            return str(value)
    return default


def bool_text(value: bool) -> str:
    return "true" if value else "false"


def priority_weight(priority: str) -> float:
    p = priority.lower()
    if p == "high":
        return 1.00
    if p == "medium":
        return 0.70
    return 0.40


def readiness_weight(readiness: str) -> float:
    r = readiness.lower()
    if r == "ready_for_spec_review":
        return 1.00
    if r == "draft":
        return 0.60
    if r == "blocked":
        return 0.00
    return 0.40


def type_weight(experiment_type: str) -> float:
    t = experiment_type.lower()
    if t == "validation_spec":
        return 0.90
    if t == "cross_archive_analysis_spec":
        return 0.85
    if t == "conflict_resolution_spec":
        return 0.80
    if t == "replay_readiness_spec":
        return 0.70
    return 0.60


def runtime_class(priority: str, experiment_type: str) -> str:
    p = priority.lower()
    t = experiment_type.lower()

    if p == "high" and t in {"validation_spec", "cross_archive_analysis_spec"}:
        return "long"
    if p in {"high", "medium"}:
        return "medium"
    return "short"


def estimated_runtime_minutes(runtime: str) -> int:
    if runtime == "long":
        return 180
    if runtime == "medium":
        return 45
    return 10


def cpu_class(runtime: str) -> str:
    if runtime == "long":
        return "high"
    if runtime == "medium":
        return "medium"
    return "low"


def ram_class(runtime: str) -> str:
    if runtime in {"long", "medium"}:
        return "medium"
    return "low"


def resource_class(cpu: str, ram: str) -> str:
    if cpu == "high":
        return "large"
    if cpu == "medium" or ram == "medium":
        return "medium"
    return "small"


def recommended_machine(runtime: str, priority: str) -> str:
    if runtime == "long" or priority.lower() == "high":
        return "Workstation"
    return "G15"


def execution_window(runtime: str) -> str:
    if runtime == "long":
        return "dedicated_session"
    if runtime == "medium":
        return "planned_session"
    return "anytime"


def parallelizable(runtime: str, experiment_type: str) -> bool:
    if runtime == "long":
        return False
    if experiment_type == "validation_spec":
        return False
    return True


def blocking_reason(row: dict[str, str]) -> str:
    readiness = pick(row, ["readiness"], "draft").lower()
    status = pick(row, ["execution_status"], "").lower()

    if readiness == "blocked":
        return "readiness_blocked"
    if status == "blocked":
        return "execution_status_blocked"
    return ""


def research_roi(priority: str, readiness: str, experiment_type: str, runtime: str) -> float:
    value = (
        0.45 * priority_weight(priority)
        + 0.35 * readiness_weight(readiness)
        + 0.20 * type_weight(experiment_type)
    )

    runtime_penalty = {
        "short": 0.00,
        "medium": 0.05,
        "long": 0.12,
    }.get(runtime, 0.05)

    score = max(0.0, min(1.0, value - runtime_penalty))
    return round(score, 4)


def build_plan(experiments: list[dict[str, str]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []

    for exp in experiments:
        priority = pick(exp, ["priority"], "low")
        readiness = pick(exp, ["readiness"], "draft")
        experiment_type = pick(exp, ["experiment_type"], "research_planning_spec")
        runtime = runtime_class(priority, experiment_type)
        minutes = estimated_runtime_minutes(runtime)
        cpu = cpu_class(runtime)
        ram = ram_class(runtime)
        resources = resource_class(cpu, ram)
        machine = recommended_machine(runtime, priority)
        blocker = blocking_reason(exp)
        roi = research_roi(priority, readiness, experiment_type, runtime)
        can_parallel = parallelizable(runtime, experiment_type)

        rows.append(
            {
                "plan_id": "",
                "execution_rank": 0,
                "experiment_id": pick(exp, ["experiment_id"]),
                "campaign_id": pick(exp, ["campaign_id"]),
                "source_hypothesis_id": pick(exp, ["source_hypothesis_id"]),
                "priority": priority,
                "readiness": readiness,
                "experiment_type": experiment_type,
                "recommended_machine": machine,
                "runtime_class": runtime,
                "estimated_runtime_minutes": minutes,
                "cpu_class": cpu,
                "ram_class": ram,
                "resource_class": resources,
                "parallelizable": bool_text(can_parallel),
                "execution_window": execution_window(runtime),
                "required_archives": pick(exp, ["required_archives"], "latest_available_archives"),
                "dependencies": "manual_review_before_execution",
                "blocking_reason": blocker,
                "plan_status": "blocked" if blocker else "planned",
                "research_roi_score": f"{roi:.4f}",
                "guardrails": "no_strategy_change; no_runtime; no_replay; no_live_trading; planning_only",
            }
        )

    rows.sort(
        key=lambda r: (
            1 if r["plan_status"] == "blocked" else 0,
            -float(r["research_roi_score"]),
            r["estimated_runtime_minutes"],
            r["experiment_id"],
        )
    )

    for i, row in enumerate(rows, start=1):
        row["execution_rank"] = i
        row["plan_id"] = f"V12C-PLAN-{i:03d}"

    return rows


def build_summary(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    total = len(rows)
    blocked = sum(1 for r in rows if r["plan_status"] == "blocked")
    workstation = sum(1 for r in rows if r["recommended_machine"] == "Workstation")
    g15 = sum(1 for r in rows if r["recommended_machine"] == "G15")
    total_minutes = sum(int(r["estimated_runtime_minutes"]) for r in rows if r["plan_status"] != "blocked")

    return [
        {"metric": "total_plans", "value": total},
        {"metric": "blocked_plans", "value": blocked},
        {"metric": "g15_recommended", "value": g15},
        {"metric": "workstation_recommended", "value": workstation},
        {"metric": "estimated_active_runtime_minutes", "value": total_minutes},
    ]


def write_report(path: Path, rows: list[dict[str, object]], summary: list[dict[str, object]], input_path: Path) -> None:
    lines = [
        "# V12C RESOURCE RUNTIME PLANNER REPORT",
        "",
        f"Date: {date.today().isoformat()}",
        "",
        "## Objective",
        "",
        "Create a resource and runtime plan from V12B experiment specifications.",
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
        "- Planning-only output.",
        "",
        "## Summary",
        "",
        "| metric | value |",
        "|---|---:|",
    ]

    for item in summary:
        lines.append(f"| {item['metric']} | {item['value']} |")

    lines += [
        "",
        "## Execution Queue",
        "",
        "| rank | experiment_id | machine | runtime | minutes | roi | status |",
        "|---:|---|---|---|---:|---:|---|",
    ]

    for row in rows:
        lines.append(
            f"| {row['execution_rank']} | {row['experiment_id']} | {row['recommended_machine']} | "
            f"{row['runtime_class']} | {row['estimated_runtime_minutes']} | "
            f"{row['research_roi_score']} | {row['plan_status']} |"
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
    parser = argparse.ArgumentParser(description="V12C Resource Runtime Planner")
    parser.add_argument("--experiments", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    input_path = Path(args.experiments)
    output_dir = Path(args.output_dir)

    experiments = read_csv(input_path)
    plan_rows = build_plan(experiments)
    summary_rows = build_summary(plan_rows)

    plan_fields = [
        "plan_id",
        "execution_rank",
        "experiment_id",
        "campaign_id",
        "source_hypothesis_id",
        "priority",
        "readiness",
        "experiment_type",
        "recommended_machine",
        "runtime_class",
        "estimated_runtime_minutes",
        "cpu_class",
        "ram_class",
        "resource_class",
        "parallelizable",
        "execution_window",
        "required_archives",
        "dependencies",
        "blocking_reason",
        "plan_status",
        "research_roi_score",
        "guardrails",
    ]

    plan_path = output_dir / "v12c_resource_runtime_plan.csv"
    summary_path = output_dir / "v12c_resource_runtime_summary.csv"
    manifest_path = output_dir / "v12c_resource_runtime_manifest.csv"
    report_path = output_dir / f"V12C_RESOURCE_RUNTIME_PLANNER_REPORT_{date.today().isoformat()}.md"

    write_csv(plan_path, plan_rows, plan_fields)
    write_csv(summary_path, summary_rows, ["metric", "value"])

    manifest_rows = [
        {"artifact": "v12c_resource_runtime_plan.csv", "path": str(plan_path), "rows": len(plan_rows), "status": "created"},
        {"artifact": "v12c_resource_runtime_summary.csv", "path": str(summary_path), "rows": len(summary_rows), "status": "created"},
        {"artifact": "V12C_RESOURCE_RUNTIME_PLANNER_REPORT", "path": str(report_path), "rows": 1, "status": "created"},
    ]
    write_csv(manifest_path, manifest_rows, ["artifact", "path", "rows", "status"])

    write_report(report_path, plan_rows, summary_rows, input_path)

    print("PASS: V12C resource runtime planner completed")
    print(f"plans: {len(plan_rows)}")
    print(f"plan_csv: {plan_path}")
    print(f"summary_csv: {summary_path}")
    print(f"manifest_csv: {manifest_path}")
    print(f"report_md: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
