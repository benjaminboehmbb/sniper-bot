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


def artifact_exists(path_text: str) -> str:
    if path_text in ("", "none", "None"):
        return "not_required"
    if Path(path_text).exists():
        return "present"
    return "missing"


def derive_executor_status(plan: dict[str, str], artifact_status: str) -> tuple[str, str]:
    plan_status = pick(plan, ["plan_status"], "planned").lower()
    blocker = pick(plan, ["blocking_reason"], "")

    if plan_status == "blocked":
        return "blocked", blocker or "resource_plan_blocked"

    if artifact_status == "missing":
        return "blocked", "required_artifact_missing"

    if pick(plan, ["guardrails"], "").find("no_runtime") == -1:
        return "blocked", "guardrail_missing_no_runtime"

    if pick(plan, ["guardrails"], "").find("no_live_trading") == -1:
        return "blocked", "guardrail_missing_no_live_trading"

    return "ready", ""


def build_execution_plan(resource_plan: list[dict[str, str]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []

    for i, plan in enumerate(resource_plan, start=1):
        required_archives = pick(plan, ["required_archives"], "latest_available_archives")
        artifact_status = "present"
        if required_archives not in ("latest_available_archives", ""):
            artifact_status = artifact_exists(required_archives)

        executor_status, block_reason = derive_executor_status(plan, artifact_status)

        rows.append(
            {
                "executor_id": f"V12D-EXEC-{i:03d}",
                "plan_id": pick(plan, ["plan_id"]),
                "execution_rank": pick(plan, ["execution_rank"], str(i)),
                "experiment_id": pick(plan, ["experiment_id"]),
                "campaign_id": pick(plan, ["campaign_id"]),
                "priority": pick(plan, ["priority"]),
                "recommended_machine": pick(plan, ["recommended_machine"]),
                "runtime_class": pick(plan, ["runtime_class"]),
                "estimated_runtime_minutes": pick(plan, ["estimated_runtime_minutes"]),
                "resource_class": pick(plan, ["resource_class"]),
                "parallelizable": pick(plan, ["parallelizable"]),
                "execution_window": pick(plan, ["execution_window"]),
                "required_archives": required_archives,
                "required_artifact_status": artifact_status,
                "research_roi_score": pick(plan, ["research_roi_score"]),
                "executor_status": executor_status,
                "block_reason": block_reason,
                "execution_mode": "planning_only",
                "runtime_execution_allowed": "false",
                "replay_execution_allowed": "false",
                "strategy_change_allowed": "false",
                "live_trading_allowed": "false",
                "next_manual_action": "review_and_approve" if executor_status == "ready" else "resolve_blocker",
                "guardrails": "no_strategy_change; no_runtime; no_replay; no_live_trading; planning_only",
            }
        )

    rows.sort(
        key=lambda r: (
            1 if r["executor_status"] == "blocked" else 0,
            int(r["execution_rank"]) if str(r["execution_rank"]).isdigit() else 999999,
        )
    )

    return rows


def build_summary(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    total = len(rows)
    ready = sum(1 for r in rows if r["executor_status"] == "ready")
    blocked = sum(1 for r in rows if r["executor_status"] == "blocked")
    workstation = sum(1 for r in rows if r["recommended_machine"] == "Workstation")
    g15 = sum(1 for r in rows if r["recommended_machine"] == "G15")

    return [
        {"metric": "total_execution_items", "value": total},
        {"metric": "ready_items", "value": ready},
        {"metric": "blocked_items", "value": blocked},
        {"metric": "g15_items", "value": g15},
        {"metric": "workstation_items", "value": workstation},
    ]


def write_report(path: Path, rows: list[dict[str, object]], summary: list[dict[str, object]], input_path: Path) -> None:
    lines = [
        "# V12D CAMPAIGN EXECUTOR REPORT",
        "",
        f"Date: {date.today().isoformat()}",
        "",
        "## Objective",
        "",
        "Create a planning-only campaign execution queue from V12C resource/runtime plans.",
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
        "- Planning-only execution queue.",
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
        "| rank | executor_id | experiment_id | machine | status | next_manual_action |",
        "|---:|---|---|---|---|---|",
    ]

    for row in rows:
        lines.append(
            f"| {row['execution_rank']} | {row['executor_id']} | {row['experiment_id']} | "
            f"{row['recommended_machine']} | {row['executor_status']} | {row['next_manual_action']} |"
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
    parser = argparse.ArgumentParser(description="V12D Campaign Executor")
    parser.add_argument("--resource-plan", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    input_path = Path(args.resource_plan)
    output_dir = Path(args.output_dir)

    resource_plan = read_csv(input_path)
    execution_rows = build_execution_plan(resource_plan)
    summary_rows = build_summary(execution_rows)

    execution_fields = [
        "executor_id",
        "plan_id",
        "execution_rank",
        "experiment_id",
        "campaign_id",
        "priority",
        "recommended_machine",
        "runtime_class",
        "estimated_runtime_minutes",
        "resource_class",
        "parallelizable",
        "execution_window",
        "required_archives",
        "required_artifact_status",
        "research_roi_score",
        "executor_status",
        "block_reason",
        "execution_mode",
        "runtime_execution_allowed",
        "replay_execution_allowed",
        "strategy_change_allowed",
        "live_trading_allowed",
        "next_manual_action",
        "guardrails",
    ]

    execution_path = output_dir / "v12d_campaign_execution_queue.csv"
    summary_path = output_dir / "v12d_campaign_execution_summary.csv"
    manifest_path = output_dir / "v12d_campaign_execution_manifest.csv"
    report_path = output_dir / f"V12D_CAMPAIGN_EXECUTOR_REPORT_{date.today().isoformat()}.md"

    write_csv(execution_path, execution_rows, execution_fields)
    write_csv(summary_path, summary_rows, ["metric", "value"])

    manifest_rows = [
        {"artifact": "v12d_campaign_execution_queue.csv", "path": str(execution_path), "rows": len(execution_rows), "status": "created"},
        {"artifact": "v12d_campaign_execution_summary.csv", "path": str(summary_path), "rows": len(summary_rows), "status": "created"},
        {"artifact": "V12D_CAMPAIGN_EXECUTOR_REPORT", "path": str(report_path), "rows": 1, "status": "created"},
    ]
    write_csv(manifest_path, manifest_rows, ["artifact", "path", "rows", "status"])

    write_report(report_path, execution_rows, summary_rows, input_path)

    print("PASS: V12D campaign executor completed")
    print(f"execution_items: {len(execution_rows)}")
    print(f"execution_csv: {execution_path}")
    print(f"summary_csv: {summary_path}")
    print(f"manifest_csv: {manifest_path}")
    print(f"report_md: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
