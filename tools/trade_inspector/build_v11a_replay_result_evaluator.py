#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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


def evaluate(row: dict[str, str]) -> tuple[str, str, str]:
    status = row.get("replay_execution_status", "")
    replay_executed = row.get("replay_executed", "")
    return_code = str(row.get("return_code", "")).strip()
    strategy_modified = row.get("strategy_modified", "")

    if strategy_modified == "yes":
        return "INVALID", "strategy_modified_guardrail_violation", "do_not_use_result"

    if status == "REPLAY_EXECUTED_PASS" and replay_executed == "yes" and return_code == "0":
        return "VALIDATION_PASS", "replay_command_completed_successfully", "increase_hypothesis_confidence"

    if status == "REPLAY_EXECUTED_FAIL" and replay_executed == "yes":
        return "VALIDATION_FAIL", "replay_command_failed", "decrease_hypothesis_confidence"

    if status == "DRY_RUN_READY":
        return "NEEDS_REAL_REPLAY", "dry_run_only_no_real_replay_executed", "keep_pending"

    if status == "BLOCKED_UNSAFE_COMMAND":
        return "BLOCKED", "unsafe_replay_command_blocked", "fix_replay_command"

    if status == "SKIPPED_NOT_REPLAY_READY":
        return "SKIPPED", "not_replay_ready", "no_learning_update"

    return "INVALID", "unknown_replay_execution_status", "manual_review_required"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--v10f-csv", required=True)
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()

    v10f_csv = Path(args.v10f_csv)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = read_csv(v10f_csv)
    evaluated: list[dict[str, object]] = []

    for row in rows:
        outcome, reason, learning_action = evaluate(row)

        evaluated.append({
            "validation_id": row.get("validation_id", ""),
            "hypothesis_id": row.get("hypothesis_id", ""),
            "hypothesis_group": row.get("hypothesis_group", ""),
            "replay_execution_status": row.get("replay_execution_status", ""),
            "replay_executed": row.get("replay_executed", ""),
            "return_code": row.get("return_code", ""),
            "validation_outcome": outcome,
            "evaluation_reason": reason,
            "learning_action": learning_action,
            "strategy_modified": row.get("strategy_modified", ""),
        })

    out_csv = out_dir / "v11a_replay_result_evaluation.csv"
    write_csv(out_csv, evaluated)

    counts: dict[str, int] = {}
    for row in evaluated:
        key = str(row["validation_outcome"])
        counts[key] = counts.get(key, 0) + 1

    report = out_dir / "V11A_REPLAY_RESULT_EVALUATOR_REPORT_2026-06-19.md"

    lines = []
    lines.append("# V11A REPLAY RESULT EVALUATOR REPORT")
    lines.append("")
    lines.append("Date: 2026-06-19")
    lines.append("Scope: Trade Inspector V11A")
    lines.append("")
    lines.append("## Objective")
    lines.append("")
    lines.append("Evaluate V10F replay execution results and convert them into validation learning outcomes.")
    lines.append("")
    lines.append("## Input")
    lines.append("")
    lines.append(f"- Source file: {v10f_csv}")
    lines.append(f"- Rows evaluated: {len(rows)}")
    lines.append("")
    lines.append("## Outcome Summary")
    lines.append("")
    lines.append("| validation_outcome | count |")
    lines.append("|---|---:|")
    for key in sorted(counts):
        lines.append(f"| {key} | {counts[key]} |")
    lines.append("")
    lines.append("## Results")
    lines.append("")
    lines.append("| validation_id | group | replay_status | outcome | learning_action |")
    lines.append("|---|---|---|---|---|")
    for row in evaluated[:30]:
        lines.append(
            f"| {row['validation_id']} | {row['hypothesis_group']} | "
            f"{row['replay_execution_status']} | {row['validation_outcome']} | "
            f"{row['learning_action']} |"
        )
    lines.append("")
    lines.append("## Guardrail")
    lines.append("")
    lines.append("V11A evaluates existing results only. It does not execute replay and does not modify strategy logic.")
    lines.append("")

    report.write_text("\n".join(lines), encoding="utf-8")

    print("V11A replay result evaluator completed")
    print("input_rows:", len(rows))
    print("evaluated_rows:", len(evaluated))
    for key in sorted(counts):
        print(f"{key}:", counts[key])
    print("report:", report)
    print("csv:", out_csv)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
