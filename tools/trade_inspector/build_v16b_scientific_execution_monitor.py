#!/usr/bin/env python3
"""
V16B Scientific Execution Monitor.

Purpose:
Monitor V16A scientific execution plans and produce execution readiness,
guardrail, and review-status reports.

Guardrails:
- Does not execute experiments.
- Does not modify execution plans.
- Does not modify policies.
- Does not modify hypotheses.
- Does not modify evidence.
- Does not recalculate scientific scores.
- Does not allocate external resources.
- Does not approve deployment.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Dict, List, Tuple


DEFAULT_EXECUTION_PLAN = (
    "outputs/trade_inspector/v16a/"
    "smoke_execution_orchestrator_2026-06-21_final/"
    "v16a_execution_plan.csv"
)


REQUIRED_COLUMNS = [
    "execution_id",
    "source_policy_id",
    "execution_state",
    "execution_allowed",
    "execution_priority",
    "execution_order",
    "execution_type",
    "orchestrator_action",
    "requires_human_approval",
    "external_execution_permitted",
    "guardrail_reason",
    "input_row_hash",
]


def read_csv(path: Path) -> Tuple[List[Dict[str, str]], List[str]]:
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")

    with path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = [dict(row) for row in reader]
        fieldnames = list(reader.fieldnames or [])

    if not fieldnames:
        raise ValueError(f"Input file has no header: {path}")

    return rows, fieldnames


def write_csv(path: Path, rows: List[Dict[str, str]], fieldnames: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def validate_schema(fieldnames: List[str]) -> List[str]:
    return [col for col in REQUIRED_COLUMNS if col not in fieldnames]


def normalize_bool(value: str) -> str:
    return str(value or "").strip().lower()


def monitor_row(row: Dict[str, str]) -> Dict[str, str]:
    execution_id = row.get("execution_id", "").strip()
    execution_state = row.get("execution_state", "").strip().lower()
    execution_allowed = normalize_bool(row.get("execution_allowed", ""))
    requires_human_approval = normalize_bool(row.get("requires_human_approval", ""))
    external_execution_permitted = normalize_bool(row.get("external_execution_permitted", ""))

    issues: List[str] = []

    if not execution_id:
        issues.append("missing_execution_id")

    if execution_state not in ("ready", "held", "requires_human_review"):
        issues.append("unknown_execution_state")

    if execution_allowed not in ("true", "false"):
        issues.append("invalid_execution_allowed")

    if requires_human_approval != "true":
        issues.append("human_approval_guardrail_not_enforced")

    if external_execution_permitted != "false":
        issues.append("external_execution_guardrail_violation")

    if execution_state == "ready" and execution_allowed != "true":
        issues.append("ready_but_not_allowed")

    if execution_state != "ready" and execution_allowed == "true":
        issues.append("not_ready_but_allowed")

    if issues:
        monitor_status = "WARN"
        monitor_action = "review_required"
    elif execution_state == "ready":
        monitor_status = "PASS"
        monitor_action = "ready_for_controlled_execution_review"
    elif execution_state == "held":
        monitor_status = "PASS"
        monitor_action = "keep_held"
    else:
        monitor_status = "PASS"
        monitor_action = "human_review_required"

    return {
        "execution_id": execution_id,
        "source_policy_id": row.get("source_policy_id", "").strip(),
        "execution_state": execution_state,
        "execution_allowed": execution_allowed,
        "requires_human_approval": requires_human_approval,
        "external_execution_permitted": external_execution_permitted,
        "monitor_status": monitor_status,
        "monitor_action": monitor_action,
        "monitor_issues": ";".join(issues),
    }


def build_monitor(rows: List[Dict[str, str]]) -> List[Dict[str, str]]:
    return [monitor_row(row) for row in rows]


def build_manifest(
    input_path: Path,
    output_dir: Path,
    missing_columns: List[str],
    monitor_rows: List[Dict[str, str]],
) -> List[Dict[str, str]]:
    pass_count = sum(1 for row in monitor_rows if row["monitor_status"] == "PASS")
    warn_count = sum(1 for row in monitor_rows if row["monitor_status"] == "WARN")
    ready_count = sum(1 for row in monitor_rows if row["execution_state"] == "ready")
    held_count = sum(1 for row in monitor_rows if row["execution_state"] == "held")
    review_count = sum(1 for row in monitor_rows if row["execution_state"] == "requires_human_review")

    status = "PASS" if not missing_columns and warn_count == 0 else "WARN"

    return [
        {
            "module": "V16B Scientific Execution Monitor",
            "input_file": str(input_path),
            "output_dir": str(output_dir),
            "total_execution_rows": str(len(monitor_rows)),
            "ready_count": str(ready_count),
            "held_count": str(held_count),
            "requires_human_review_count": str(review_count),
            "monitor_pass_count": str(pass_count),
            "monitor_warn_count": str(warn_count),
            "missing_required_columns": ";".join(missing_columns),
            "guardrail_no_execution": "true",
            "guardrail_no_plan_modification": "true",
            "guardrail_no_policy_modification": "true",
            "guardrail_no_score_recalculation": "true",
            "status": status,
        }
    ]


def write_summary(path: Path, manifest: Dict[str, str]) -> None:
    text = f"""# V16B Scientific Execution Monitor Summary

## Status

{manifest["status"]}

## Purpose

V16B monitors V16A scientific execution plans for readiness, review status,
and guardrail consistency.

It does not execute experiments.

## Input

{manifest["input_file"]}

## Output

{manifest["output_dir"]}

## Counts

- total_execution_rows: {manifest["total_execution_rows"]}
- ready_count: {manifest["ready_count"]}
- held_count: {manifest["held_count"]}
- requires_human_review_count: {manifest["requires_human_review_count"]}
- monitor_pass_count: {manifest["monitor_pass_count"]}
- monitor_warn_count: {manifest["monitor_warn_count"]}

## Schema

- missing_required_columns: {manifest["missing_required_columns"]}

## Guardrails

- no execution
- no execution plan modification
- no policy modification
- no hypothesis modification
- no evidence modification
- no scientific score recalculation
- no external resource allocation
- no deployment approval

## Interpretation

V16B is a monitoring layer only. It evaluates whether prepared execution plans
remain structurally safe and ready for controlled human-reviewed execution.
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build V16B scientific execution monitor report."
    )
    parser.add_argument(
        "--execution-plan",
        default=DEFAULT_EXECUTION_PLAN,
        help="Path to V16A execution plan CSV.",
    )
    parser.add_argument(
        "--output-dir",
        default="outputs/trade_inspector/v16b/smoke_execution_monitor_2026-06-21",
        help="Output directory for V16B artifacts.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    input_path = Path(args.execution_plan)
    output_dir = Path(args.output_dir)

    rows, fieldnames = read_csv(input_path)
    missing_columns = validate_schema(fieldnames)
    monitor_rows = build_monitor(rows)

    monitor_fields = [
        "execution_id",
        "source_policy_id",
        "execution_state",
        "execution_allowed",
        "requires_human_approval",
        "external_execution_permitted",
        "monitor_status",
        "monitor_action",
        "monitor_issues",
    ]

    manifest_rows = build_manifest(input_path, output_dir, missing_columns, monitor_rows)
    manifest_fields = list(manifest_rows[0].keys())

    write_csv(output_dir / "v16b_execution_monitor.csv", monitor_rows, monitor_fields)
    write_csv(output_dir / "v16b_execution_monitor_manifest.csv", manifest_rows, manifest_fields)
    write_summary(output_dir / "v16b_execution_monitor_summary.md", manifest_rows[0])

    print("V16B Scientific Execution Monitor completed.")
    print(f"Input rows: {len(rows)}")
    print(f"Monitor rows: {len(monitor_rows)}")
    print(f"Status: {manifest_rows[0]['status']}")
    print(f"Output dir: {output_dir}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
