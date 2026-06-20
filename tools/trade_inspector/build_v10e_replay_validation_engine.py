#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Trade Inspector V10E

Replay Validation Engine

Safe first version:
- processes V10D validation results
- marks replay-ready validations
- does not execute actual replay/backtest yet
- does not modify strategy logic

ASCII only.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from tools.trade_inspector.common.io import read_csv, write_csv
from tools.trade_inspector.common.utils import now_utc



def replay_status(row: dict[str, str]) -> tuple[str, str, str]:
    runner_status = row.get("runner_status", "")

    if runner_status == "READY_TO_RUN":
        return (
            "REPLAY_READY",
            "ready_for_future_replay_attachment",
            "PASS",
        )

    if runner_status == "SKIPPED_DESIGN_REQUIRED":
        return (
            "REPLAY_SKIPPED",
            "validation_design_required_before_replay",
            "SKIP",
        )

    if runner_status == "SKIPPED_ARCHIVES_REQUIRED":
        return (
            "REPLAY_SKIPPED",
            "additional_archives_or_trades_required",
            "SKIP",
        )

    if runner_status == "SKIPPED_REJECTED":
        return (
            "REPLAY_REJECTED",
            "validation_rejected_before_replay",
            "REJECT",
        )

    return (
        "REPLAY_SKIPPED",
        "unknown_runner_status",
        "SKIP",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--v10d-csv", required=True)
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()

    v10d_csv = Path(args.v10d_csv)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = read_csv(v10d_csv)

    started_at = now_utc()
    results: list[dict[str, object]] = []

    for row in rows:
        status, reason, decision = replay_status(row)

        results.append(
            {
                "validation_id": row.get("validation_id", ""),
                "hypothesis_id": row.get("hypothesis_id", ""),
                "hypothesis_group": row.get("hypothesis_group", ""),
                "runner_status": row.get("runner_status", ""),
                "replay_validation_status": status,
                "replay_validation_decision": decision,
                "replay_validation_reason": reason,
                "replay_command_attached": "no",
                "replay_executed": "no",
                "runtime_executed": "no",
                "strategy_modified": "no",
                "started_at_utc": started_at,
                "finished_at_utc": now_utc(),
                "error_code": "",
            }
        )

    out_csv = out_dir / "v10e_replay_validation_results.csv"
    write_csv(out_csv, results, ['validation_id', 'hypothesis_id', 'hypothesis_group', 'runner_status', 'replay_validation_status', 'replay_validation_decision', 'replay_validation_reason', 'replay_command_attached', 'replay_executed', 'runtime_executed', 'strategy_modified', 'started_at_utc', 'finished_at_utc', 'error_code'])

    status_counts: dict[str, int] = {}
    decision_counts: dict[str, int] = {}

    for row in results:
        status_key = str(row["replay_validation_status"])
        decision_key = str(row["replay_validation_decision"])
        status_counts[status_key] = status_counts.get(status_key, 0) + 1
        decision_counts[decision_key] = decision_counts.get(decision_key, 0) + 1

    report = out_dir / "V10E_REPLAY_VALIDATION_ENGINE_REPORT_2026-06-19.md"

    lines: list[str] = []
    lines.append("# V10E REPLAY VALIDATION ENGINE REPORT")
    lines.append("")
    lines.append("Date: 2026-06-19")
    lines.append("Scope: Trade Inspector V10E")
    lines.append("")
    lines.append("## Objective")
    lines.append("")
    lines.append("Process V10D validation runner results and identify replay-ready validation items.")
    lines.append("")
    lines.append("## Input")
    lines.append("")
    lines.append(f"- Source file: {v10d_csv}")
    lines.append(f"- Rows processed: {len(rows)}")
    lines.append("")
    lines.append("## Replay Validation Status Summary")
    lines.append("")
    lines.append("| replay_validation_status | count |")
    lines.append("|---|---:|")
    for key in sorted(status_counts):
        lines.append(f"| {key} | {status_counts[key]} |")
    lines.append("")
    lines.append("## Replay Validation Decision Summary")
    lines.append("")
    lines.append("| decision | count |")
    lines.append("|---|---:|")
    for key in sorted(decision_counts):
        lines.append(f"| {key} | {decision_counts[key]} |")
    lines.append("")
    lines.append("## Results")
    lines.append("")
    lines.append("| validation_id | group | runner_status | replay_status | decision | reason |")
    lines.append("|---|---|---|---|---|---|")

    for row in results[:30]:
        lines.append(
            f"| {row['validation_id']} | {row['hypothesis_group']} | "
            f"{row['runner_status']} | {row['replay_validation_status']} | "
            f"{row['replay_validation_decision']} | {row['replay_validation_reason']} |"
        )

    lines.append("")
    lines.append("## Guardrail Verification")
    lines.append("")
    lines.append("- replay_command_attached: no")
    lines.append("- replay_executed: no")
    lines.append("- runtime_executed: no")
    lines.append("- strategy_modified: no")
    lines.append("")
    lines.append("## Generated Files")
    lines.append("")
    lines.append("- v10e_replay_validation_results.csv")
    lines.append("- V10E_REPLAY_VALIDATION_ENGINE_REPORT_2026-06-19.md")
    lines.append("")

    report.write_text("\n".join(lines), encoding="utf-8")

    print("V10E replay validation engine completed")
    print("input_rows:", len(rows))
    print("result_rows:", len(results))
    for key in sorted(status_counts):
        print(f"{key}:", status_counts[key])
    print("report:", report)
    print("csv:", out_csv)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
