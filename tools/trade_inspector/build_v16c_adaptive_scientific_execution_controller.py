#!/usr/bin/env python3
"""
V16C Adaptive Scientific Execution Controller.

Purpose:
Adaptively control already prepared and monitored scientific execution plans.

V16C may:
- read V16A execution plans
- read V16B monitor outputs
- derive safe execution control classes
- assign controlled execution order
- preserve guardrails

V16C must not:
- execute experiments
- modify policies
- modify hypotheses
- modify evidence
- recalculate scientific scores
- approve deployment
- override human approval
- allocate external resources
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
from typing import Dict, List

from tools.trade_inspector.common.execution_utils import index_by, read_csv, safe_int, write_csv, write_text


DEFAULT_EXECUTION_PLAN = (
    "outputs/trade_inspector/v16a/"
    "smoke_execution_orchestrator_2026-06-21_final/"
    "v16a_execution_plan.csv"
)

DEFAULT_MONITOR_INPUT = (
    "outputs/trade_inspector/v16b/"
    "smoke_execution_monitor_2026-06-21/"
    "v16b_execution_monitor.csv"
)

PRIORITY_RANK = {
    "critical": 0,
    "high": 1,
    "medium": 2,
    "low": 3,
}



def normalize_priority(value: str) -> str:
    text = str(value or "").strip().lower()
    if text in PRIORITY_RANK:
        return text
    return "medium"


def classify_control(
    plan_row: Dict[str, str],
    monitor_row: Dict[str, str] | None,
) -> Dict[str, str]:
    execution_id = plan_row.get("execution_id", "").strip()
    source_policy_id = plan_row.get("source_policy_id", "").strip()
    execution_state = plan_row.get("execution_state", "").strip().lower()
    execution_allowed = plan_row.get("execution_allowed", "").strip().lower()
    execution_priority = normalize_priority(plan_row.get("execution_priority", ""))
    original_order = safe_int(plan_row.get("execution_order", ""), 999999)

    monitor_status = ""
    monitor_action = ""
    monitor_issues = ""

    if monitor_row is not None:
        monitor_status = monitor_row.get("monitor_status", "").strip()
        monitor_action = monitor_row.get("monitor_action", "").strip()
        monitor_issues = monitor_row.get("monitor_issues", "").strip()

    issues: List[str] = []

    if not execution_id:
        issues.append("missing_execution_id")

    if monitor_row is None:
        issues.append("missing_monitor_row")

    if monitor_status and monitor_status != "PASS":
        issues.append("monitor_not_pass")

    if monitor_issues:
        issues.append("monitor_issues_present")

    if execution_state != "ready":
        issues.append("execution_not_ready")

    if execution_allowed != "true":
        issues.append("execution_not_allowed")

    if plan_row.get("requires_human_approval", "").strip().lower() != "true":
        issues.append("human_approval_guardrail_not_enforced")

    if plan_row.get("external_execution_permitted", "").strip().lower() != "false":
        issues.append("external_execution_guardrail_violation")

    if issues:
        control_status = "HOLD"
        control_action = "do_not_schedule"
        adaptive_control_class = "blocked_or_review_required"
        control_reason = ";".join(issues)
    else:
        control_status = "READY"
        control_action = "schedule_for_human_reviewed_execution"
        adaptive_control_class = "safe_ready_control"
        control_reason = "plan_ready_monitor_pass_guardrails_intact"

    priority_score = PRIORITY_RANK[execution_priority]

    return {
        "execution_id": execution_id,
        "source_policy_id": source_policy_id,
        "control_status": control_status,
        "control_action": control_action,
        "adaptive_control_class": adaptive_control_class,
        "execution_priority": execution_priority,
        "priority_score": str(priority_score),
        "original_execution_order": str(original_order),
        "monitor_status": monitor_status,
        "monitor_action": monitor_action,
        "control_reason": control_reason,
        "human_approval_required": "true",
        "external_execution_permitted": "false",
        "policy_override_permitted": "false",
        "score_recalculation_permitted": "false",
    }


def build_control_plan(
    plan_rows: List[Dict[str, str]],
    monitor_rows: List[Dict[str, str]],
) -> List[Dict[str, str]]:
    monitor_by_execution_id = index_by(monitor_rows, "execution_id")

    control_rows = [
        classify_control(row, monitor_by_execution_id.get(row.get("execution_id", "").strip()))
        for row in plan_rows
    ]

    control_rows.sort(
        key=lambda row: (
            0 if row["control_status"] == "READY" else 1,
            safe_int(row["priority_score"], 999),
            safe_int(row["original_execution_order"], 999999),
            row["execution_id"],
        )
    )

    for index, row in enumerate(control_rows, start=1):
        row["adaptive_execution_order"] = str(index)

    return control_rows


def build_manifest(
    execution_plan_path: Path,
    monitor_input_path: Path,
    output_dir: Path,
    control_rows: List[Dict[str, str]],
) -> List[Dict[str, str]]:
    ready_count = sum(1 for row in control_rows if row["control_status"] == "READY")
    hold_count = sum(1 for row in control_rows if row["control_status"] == "HOLD")

    return [
        {
            "module": "V16C Adaptive Scientific Execution Controller",
            "execution_plan_input": str(execution_plan_path),
            "monitor_input": str(monitor_input_path),
            "output_dir": str(output_dir),
            "total_control_rows": str(len(control_rows)),
            "ready_control_count": str(ready_count),
            "hold_control_count": str(hold_count),
            "guardrail_no_execution": "true",
            "guardrail_no_policy_modification": "true",
            "guardrail_no_hypothesis_modification": "true",
            "guardrail_no_evidence_modification": "true",
            "guardrail_no_score_recalculation": "true",
            "guardrail_human_approval_required": "true",
            "status": "PASS",
        }
    ]


def write_summary(path: Path, manifest: Dict[str, str]) -> None:
    text = f"""# V16C Adaptive Scientific Execution Controller Summary

## Status

{manifest["status"]}

## Purpose

V16C adaptively controls already prepared and monitored scientific execution
plans.

It does not execute experiments.

## Inputs

- execution_plan_input: {manifest["execution_plan_input"]}
- monitor_input: {manifest["monitor_input"]}

## Output

{manifest["output_dir"]}

## Counts

- total_control_rows: {manifest["total_control_rows"]}
- ready_control_count: {manifest["ready_control_count"]}
- hold_control_count: {manifest["hold_control_count"]}

## Guardrails

- no execution
- no policy modification
- no hypothesis modification
- no evidence modification
- no scientific score recalculation
- no external resource allocation
- human approval remains required
- policy override is not permitted

## Interpretation

V16C is an adaptive control layer only. It may order and classify already
approved execution plans, but it cannot create or change scientific decisions.
"""
    write_text(path, text)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build V16C adaptive scientific execution control plan."
    )
    parser.add_argument(
        "--execution-plan",
        default=DEFAULT_EXECUTION_PLAN,
        help="Path to V16A execution plan CSV.",
    )
    parser.add_argument(
        "--monitor-input",
        default=DEFAULT_MONITOR_INPUT,
        help="Path to V16B execution monitor CSV.",
    )
    parser.add_argument(
        "--output-dir",
        default="outputs/trade_inspector/v16c/smoke_adaptive_execution_controller_2026-06-21",
        help="Output directory for V16C artifacts.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    execution_plan_path = Path(args.execution_plan)
    monitor_input_path = Path(args.monitor_input)
    output_dir = Path(args.output_dir)

    plan_rows, _ = read_csv(execution_plan_path)
    monitor_rows, _ = read_csv(monitor_input_path)

    control_rows = build_control_plan(plan_rows, monitor_rows)

    control_fields = [
        "execution_id",
        "source_policy_id",
        "control_status",
        "control_action",
        "adaptive_control_class",
        "execution_priority",
        "priority_score",
        "original_execution_order",
        "adaptive_execution_order",
        "monitor_status",
        "monitor_action",
        "control_reason",
        "human_approval_required",
        "external_execution_permitted",
        "policy_override_permitted",
        "score_recalculation_permitted",
    ]

    manifest_rows = build_manifest(
        execution_plan_path,
        monitor_input_path,
        output_dir,
        control_rows,
    )
    manifest_fields = list(manifest_rows[0].keys())

    write_csv(output_dir / "v16c_adaptive_execution_control.csv", control_rows, control_fields)
    write_csv(output_dir / "v16c_adaptive_execution_control_manifest.csv", manifest_rows, manifest_fields)
    write_summary(output_dir / "v16c_adaptive_execution_control_summary.md", manifest_rows[0])

    print("V16C Adaptive Scientific Execution Controller completed.")
    print(f"Input plan rows: {len(plan_rows)}")
    print(f"Input monitor rows: {len(monitor_rows)}")
    print(f"Control rows: {len(control_rows)}")
    print(f"Status: {manifest_rows[0]['status']}")
    print(f"Output dir: {output_dir}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
