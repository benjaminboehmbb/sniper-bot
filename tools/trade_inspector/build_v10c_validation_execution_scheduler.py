#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Trade Inspector V10C

Validation Execution Scheduler

Converts V10B validation specifications into an ordered validation execution schedule.

ASCII only.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from tools.trade_inspector.common.io import read_csv, write_csv
from tools.trade_inspector.common.utils import to_int as inum





def runtime_weight(value: str) -> int:
    return {
        "none": 0,
        "low": 1,
        "medium": 2,
        "high": 3,
    }.get(str(value).strip().lower(), 2)


def validation_type_weight(vtype: str) -> int:
    return {
        "REPLAY_PLUS_RUNTIME": 1,
        "REPLAY_ONLY": 2,
        "DESIGN_ONLY": 3,
        "ARCHIVE_EXPANSION": 4,
        "NONE": 9,
    }.get(str(vtype).strip(), 5)


def status_weight(status: str) -> int:
    return {
        "READY_FOR_EXECUTION": 1,
        "DESIGN_REQUIRED": 2,
        "WAITING_FOR_ARCHIVES": 3,
        "REJECTED": 9,
    }.get(str(status).strip(), 5)


def schedule_class(row: dict[str, str]) -> str:
    status = row.get("status", "")
    vtype = row.get("validation_type", "")

    if status == "REJECTED" or vtype == "NONE":
        return "SKIP_REJECTED"

    if vtype == "ARCHIVE_EXPANSION":
        return "WAIT_FOR_ARCHIVES"

    if vtype == "DESIGN_ONLY":
        return "DESIGN_FIRST"

    if status == "READY_FOR_EXECUTION":
        return "RUN_NOW"

    return "DESIGN_FIRST"


def schedule_reason(row: dict[str, str], cls: str) -> str:
    if cls == "RUN_NOW":
        return "ready_validation_specification_with_execution_requirements"
    if cls == "DESIGN_FIRST":
        return "validation_design_required_before_execution"
    if cls == "WAIT_FOR_ARCHIVES":
        return "more_archive_or_trade_support_required"
    if cls == "SKIP_REJECTED":
        return "validation_rejected_or_not_required"
    return "unknown"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--v10b-csv", required=True)
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()

    v10b_csv = Path(args.v10b_csv)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = read_csv(v10b_csv)

    scheduled: list[dict[str, object]] = []

    for row in rows:
        cls = schedule_class(row)

        required_archives = inum(row.get("required_archives"))
        required_trades = inum(row.get("required_trades"))
        effort = runtime_weight(row.get("estimated_runtime", "medium"))

        sort_key = (
            status_weight(row.get("status", "")),
            validation_type_weight(row.get("validation_type", "")),
            required_archives,
            required_trades,
            effort,
            row.get("validation_id", ""),
        )

        scheduled.append(
            {
                "validation_id": row.get("validation_id", ""),
                "hypothesis_id": row.get("hypothesis_id", ""),
                "hypothesis_group": row.get("hypothesis_group", ""),
                "validation_phase": row.get("validation_phase", ""),
                "validation_type": row.get("validation_type", ""),
                "schedule_class": cls,
                "schedule_reason": schedule_reason(row, cls),
                "replay_required": row.get("replay_required", ""),
                "runtime_required": row.get("runtime_required", ""),
                "required_archives": required_archives,
                "required_trades": required_trades,
                "estimated_runtime": row.get("estimated_runtime", ""),
                "execution_environment": row.get("execution_environment", ""),
                "status": row.get("status", ""),
                "_sort_key": sort_key,
            }
        )

    scheduled.sort(key=lambda r: r["_sort_key"])

    output_rows: list[dict[str, object]] = []

    for order, row in enumerate(scheduled, 1):
        clean = {k: v for k, v in row.items() if k != "_sort_key"}
        clean["execution_order"] = order
        output_rows.append(clean)

    out_csv = out_dir / "v10c_validation_execution_schedule.csv"
    write_csv(out_csv, output_rows, ['validation_id', 'hypothesis_id', 'hypothesis_group', 'validation_phase', 'validation_type', 'schedule_class', 'schedule_reason', 'replay_required', 'runtime_required', 'required_archives', 'required_trades', 'estimated_runtime', 'execution_environment', 'status', '_sort_key'])

    class_counts: dict[str, int] = {}
    for row in output_rows:
        key = str(row["schedule_class"])
        class_counts[key] = class_counts.get(key, 0) + 1

    report = out_dir / "V10C_VALIDATION_EXECUTION_SCHEDULER_REPORT_2026-06-19.md"

    lines: list[str] = []
    lines.append("# V10C VALIDATION EXECUTION SCHEDULER REPORT")
    lines.append("")
    lines.append("Date: 2026-06-19")
    lines.append("Scope: Trade Inspector V10C")
    lines.append("")
    lines.append("## Objective")
    lines.append("")
    lines.append("Convert V10B validation specifications into an ordered execution schedule.")
    lines.append("")
    lines.append("## Input")
    lines.append("")
    lines.append(f"- Source file: {v10b_csv}")
    lines.append(f"- Specifications processed: {len(rows)}")
    lines.append("")
    lines.append("## Schedule Class Summary")
    lines.append("")
    lines.append("| schedule_class | count |")
    lines.append("|---|---:|")
    for key in sorted(class_counts):
        lines.append(f"| {key} | {class_counts[key]} |")
    lines.append("")
    lines.append("## Execution Schedule")
    lines.append("")
    lines.append("| order | validation_id | group | schedule_class | type | required_archives | required_trades | runtime |")
    lines.append("|---:|---|---|---|---|---:|---:|---|")

    for row in output_rows[:30]:
        lines.append(
            f"| {row['execution_order']} | {row['validation_id']} | {row['hypothesis_group']} | "
            f"{row['schedule_class']} | {row['validation_type']} | "
            f"{row['required_archives']} | {row['required_trades']} | {row['estimated_runtime']} |"
        )

    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    lines.append("- RUN_NOW items are ready for validation execution planning.")
    lines.append("- DESIGN_FIRST items need design approval before execution.")
    lines.append("- WAIT_FOR_ARCHIVES items need more archive/trade evidence.")
    lines.append("- SKIP_REJECTED items should not consume validation effort.")
    lines.append("")
    lines.append("## Guardrail")
    lines.append("")
    lines.append("V10C does not execute validations and does not modify strategy logic.")
    lines.append("")
    lines.append("## Generated Files")
    lines.append("")
    lines.append("- v10c_validation_execution_schedule.csv")
    lines.append("- V10C_VALIDATION_EXECUTION_SCHEDULER_REPORT_2026-06-19.md")
    lines.append("")

    report.write_text("\n".join(lines), encoding="utf-8")

    print("V10C validation execution scheduler completed")
    print("input_rows:", len(rows))
    print("schedule_rows:", len(output_rows))
    for key in sorted(class_counts):
        print(f"{key}:", class_counts[key])
    print("report:", report)
    print("csv:", out_csv)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
