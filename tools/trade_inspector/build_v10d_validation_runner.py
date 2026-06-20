#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Trade Inspector V10D

Validation Runner

Safely processes V10C validation execution schedules.

ASCII only.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from tools.trade_inspector.common.io import read_csv, write_csv
from tools.trade_inspector.common.utils import now_utc



def runner_status(schedule_class: str) -> tuple[str, str]:
    if schedule_class == "RUN_NOW":
        return "READY_TO_RUN", "safe_runner_did_not_execute_replay_yet"
    if schedule_class == "DESIGN_FIRST":
        return "SKIPPED_DESIGN_REQUIRED", "validation_design_required_before_execution"
    if schedule_class == "WAIT_FOR_ARCHIVES":
        return "SKIPPED_ARCHIVES_REQUIRED", "additional_archives_or_trades_required"
    if schedule_class == "SKIP_REJECTED":
        return "SKIPPED_REJECTED", "validation_was_rejected"
    return "SKIPPED_UNKNOWN", "unknown_schedule_class"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--v10c-csv", required=True)
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()

    schedule_path = Path(args.v10c_csv)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = read_csv(schedule_path)

    started_at = now_utc()
    results: list[dict[str, object]] = []

    for row in rows:
        row_started = now_utc()
        status, reason = runner_status(row.get("schedule_class", ""))
        row_finished = now_utc()

        results.append(
            {
                "execution_order": row.get("execution_order", ""),
                "validation_id": row.get("validation_id", ""),
                "hypothesis_id": row.get("hypothesis_id", ""),
                "hypothesis_group": row.get("hypothesis_group", ""),
                "schedule_class": row.get("schedule_class", ""),
                "validation_type": row.get("validation_type", ""),
                "runner_status": status,
                "runner_reason": reason,
                "replay_executed": "no",
                "runtime_executed": "no",
                "strategy_modified": "no",
                "started_at_utc": row_started,
                "finished_at_utc": row_finished,
                "error_code": "",
                "execution_environment": row.get("execution_environment", ""),
            }
        )

    finished_at = now_utc()

    out_csv = out_dir / "v10d_validation_results.csv"
    write_csv(out_csv, results, ['execution_order', 'validation_id', 'hypothesis_id', 'hypothesis_group', 'schedule_class', 'validation_type', 'runner_status', 'runner_reason', 'replay_executed', 'runtime_executed', 'strategy_modified', 'started_at_utc', 'finished_at_utc', 'error_code', 'execution_environment'])

    status_counts: dict[str, int] = {}
    for row in results:
        key = str(row["runner_status"])
        status_counts[key] = status_counts.get(key, 0) + 1

    report = out_dir / "V10D_VALIDATION_RUNNER_REPORT_2026-06-19.md"

    lines: list[str] = []
    lines.append("# V10D VALIDATION RUNNER REPORT")
    lines.append("")
    lines.append("Date: 2026-06-19")
    lines.append("Scope: Trade Inspector V10D")
    lines.append("")
    lines.append("## Objective")
    lines.append("")
    lines.append("Safely process V10C validation execution schedules and produce execution status records.")
    lines.append("")
    lines.append("## Input")
    lines.append("")
    lines.append(f"- Source file: {schedule_path}")
    lines.append(f"- Schedule rows processed: {len(rows)}")
    lines.append("")
    lines.append("## Runner Window")
    lines.append("")
    lines.append(f"- Started UTC: {started_at}")
    lines.append(f"- Finished UTC: {finished_at}")
    lines.append("")
    lines.append("## Runner Status Summary")
    lines.append("")
    lines.append("| runner_status | count |")
    lines.append("|---|---:|")
    for key in sorted(status_counts):
        lines.append(f"| {key} | {status_counts[key]} |")
    lines.append("")
    lines.append("## Results")
    lines.append("")
    lines.append("| order | validation_id | group | schedule_class | runner_status | reason |")
    lines.append("|---:|---|---|---|---|---|")

    for row in results[:30]:
        lines.append(
            f"| {row['execution_order']} | {row['validation_id']} | {row['hypothesis_group']} | "
            f"{row['schedule_class']} | {row['runner_status']} | {row['runner_reason']} |"
        )

    lines.append("")
    lines.append("## Guardrail Verification")
    lines.append("")
    lines.append("- replay_executed: no")
    lines.append("- runtime_executed: no")
    lines.append("- strategy_modified: no")
    lines.append("")
    lines.append("## Generated Files")
    lines.append("")
    lines.append("- v10d_validation_results.csv")
    lines.append("- V10D_VALIDATION_RUNNER_REPORT_2026-06-19.md")
    lines.append("")

    report.write_text("\n".join(lines), encoding="utf-8")

    print("V10D validation runner completed")
    print("input_rows:", len(rows))
    print("result_rows:", len(results))
    for key in sorted(status_counts):
        print(f"{key}:", status_counts[key])
    print("report:", report)
    print("csv:", out_csv)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
