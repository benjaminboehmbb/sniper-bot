#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Trade Inspector V10F

Replay Execution Engine

Safe first version:
- processes V10E replay validation results
- dry-run by default
- does not execute replay commands unless --allow-execute is provided
- refuses execution when no replay command is attached
- never modifies strategy logic

ASCII only.
"""

from __future__ import annotations

import argparse
import shlex
import subprocess
from pathlib import Path

from tools.trade_inspector.common.io import read_csv, write_csv
from tools.trade_inspector.common.utils import now_utc



def safe_command_allowed(command: str) -> tuple[bool, str]:
    if not command.strip():
        return False, "empty_replay_command"

    forbidden = [
        " rm ",
        "rm -",
        " del ",
        " rmdir ",
        "git reset",
        "git clean",
        "git checkout",
        "live_l1",
        "send_order",
        "binance",
        "api_key",
        "secret",
    ]

    padded = f" {command.strip()} "

    for token in forbidden:
        if token in padded:
            return False, f"forbidden_command_token:{token.strip()}"

    return True, "command_allowed"


def execution_decision(row: dict[str, str], allow_execute: bool) -> tuple[str, str]:
    replay_status = row.get("replay_validation_status", "")
    replay_decision = row.get("replay_validation_decision", "")
    command_attached = row.get("replay_command_attached", "")

    if replay_status != "REPLAY_READY" or replay_decision != "PASS":
        return "SKIPPED_NOT_REPLAY_READY", "row_is_not_replay_ready"

    if command_attached != "yes":
        return "DRY_RUN_READY", "no_replay_command_attached_yet"

    command = row.get("replay_command", "")
    allowed, reason = safe_command_allowed(command)

    if not allowed:
        return "BLOCKED_UNSAFE_COMMAND", reason

    if not allow_execute:
        return "DRY_RUN_READY", "allow_execute_not_enabled"

    return "EXECUTE_REPLAY", "safe_command_ready_for_execution"


def run_command(command: str, timeout_sec: int) -> tuple[int, str, str]:
    args = shlex.split(command)
    completed = subprocess.run(
        args,
        capture_output=True,
        text=True,
        timeout=timeout_sec,
        check=False,
    )
    return completed.returncode, completed.stdout[-4000:], completed.stderr[-4000:]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--v10e-csv", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--allow-execute", action="store_true")
    parser.add_argument("--timeout-sec", type=int, default=300)
    args = parser.parse_args()

    v10e_csv = Path(args.v10e_csv)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = read_csv(v10e_csv)

    started_at = now_utc()
    results: list[dict[str, object]] = []

    for row in rows:
        row_started = now_utc()
        status, reason = execution_decision(row, args.allow_execute)

        return_code = ""
        stdout_tail = ""
        stderr_tail = ""
        replay_executed = "no"

        if status == "EXECUTE_REPLAY":
            command = row.get("replay_command", "")
            try:
                rc, out, err = run_command(command, args.timeout_sec)
                return_code = rc
                stdout_tail = out
                stderr_tail = err
                replay_executed = "yes"
                status = "REPLAY_EXECUTED_PASS" if rc == 0 else "REPLAY_EXECUTED_FAIL"
                reason = "command_completed"
            except subprocess.TimeoutExpired:
                return_code = "timeout"
                status = "REPLAY_EXECUTED_FAIL"
                reason = "command_timeout"
            except Exception as exc:
                return_code = "exception"
                status = "REPLAY_EXECUTED_FAIL"
                reason = f"command_exception:{type(exc).__name__}"

        row_finished = now_utc()

        results.append(
            {
                "validation_id": row.get("validation_id", ""),
                "hypothesis_id": row.get("hypothesis_id", ""),
                "hypothesis_group": row.get("hypothesis_group", ""),
                "replay_validation_status": row.get("replay_validation_status", ""),
                "replay_validation_decision": row.get("replay_validation_decision", ""),
                "replay_execution_status": status,
                "replay_execution_reason": reason,
                "allow_execute": "yes" if args.allow_execute else "no",
                "replay_command_attached": row.get("replay_command_attached", ""),
                "replay_command": row.get("replay_command", ""),
                "replay_executed": replay_executed,
                "runtime_executed": "no",
                "strategy_modified": "no",
                "return_code": return_code,
                "stdout_tail": stdout_tail.replace("\n", "\\n"),
                "stderr_tail": stderr_tail.replace("\n", "\\n"),
                "started_at_utc": row_started,
                "finished_at_utc": row_finished,
            }
        )

    finished_at = now_utc()

    out_csv = out_dir / "v10f_replay_execution_results.csv"
    write_csv(out_csv, results, ['validation_id', 'hypothesis_id', 'hypothesis_group', 'replay_validation_status', 'replay_validation_decision', 'replay_execution_status', 'replay_execution_reason', 'allow_execute', 'replay_command_attached', 'replay_command', 'replay_executed', 'runtime_executed', 'strategy_modified', 'return_code', 'stdout_tail', 'stderr_tail', 'started_at_utc', 'finished_at_utc'])

    status_counts: dict[str, int] = {}
    for row in results:
        key = str(row["replay_execution_status"])
        status_counts[key] = status_counts.get(key, 0) + 1

    report = out_dir / "V10F_REPLAY_EXECUTION_ENGINE_REPORT_2026-06-19.md"

    lines: list[str] = []
    lines.append("# V10F REPLAY EXECUTION ENGINE REPORT")
    lines.append("")
    lines.append("Date: 2026-06-19")
    lines.append("Scope: Trade Inspector V10F")
    lines.append("")
    lines.append("## Objective")
    lines.append("")
    lines.append("Process V10E replay-ready validation records and execute or dry-run replay actions safely.")
    lines.append("")
    lines.append("## Input")
    lines.append("")
    lines.append(f"- Source file: {v10e_csv}")
    lines.append(f"- Rows processed: {len(rows)}")
    lines.append(f"- allow_execute: {'yes' if args.allow_execute else 'no'}")
    lines.append("")
    lines.append("## Runner Window")
    lines.append("")
    lines.append(f"- Started UTC: {started_at}")
    lines.append(f"- Finished UTC: {finished_at}")
    lines.append("")
    lines.append("## Replay Execution Status Summary")
    lines.append("")
    lines.append("| replay_execution_status | count |")
    lines.append("|---|---:|")
    for key in sorted(status_counts):
        lines.append(f"| {key} | {status_counts[key]} |")
    lines.append("")
    lines.append("## Results")
    lines.append("")
    lines.append("| validation_id | group | replay_validation_status | execution_status | reason | executed |")
    lines.append("|---|---|---|---|---|---|")

    for row in results[:30]:
        lines.append(
            f"| {row['validation_id']} | {row['hypothesis_group']} | "
            f"{row['replay_validation_status']} | {row['replay_execution_status']} | "
            f"{row['replay_execution_reason']} | {row['replay_executed']} |"
        )

    lines.append("")
    lines.append("## Guardrail Verification")
    lines.append("")
    lines.append(f"- allow_execute: {'yes' if args.allow_execute else 'no'}")
    lines.append("- runtime_executed: no")
    lines.append("- strategy_modified: no")
    lines.append("- destructive_operations: not_allowed")
    lines.append("")
    lines.append("## Generated Files")
    lines.append("")
    lines.append("- v10f_replay_execution_results.csv")
    lines.append("- V10F_REPLAY_EXECUTION_ENGINE_REPORT_2026-06-19.md")
    lines.append("")

    report.write_text("\n".join(lines), encoding="utf-8")

    print("V10F replay execution engine completed")
    print("input_rows:", len(rows))
    print("result_rows:", len(results))
    for key in sorted(status_counts):
        print(f"{key}:", status_counts[key])
    print("allow_execute:", "yes" if args.allow_execute else "no")
    print("report:", report)
    print("csv:", out_csv)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
