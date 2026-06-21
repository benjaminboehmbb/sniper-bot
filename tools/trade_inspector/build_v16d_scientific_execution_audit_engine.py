#!/usr/bin/env python3
"""
V16D Scientific Execution Audit Engine.

Purpose:
Create a reproducible audit trail across the V15D -> V16A -> V16B -> V16C
scientific execution chain.

V16D may:
- read V15D policy decisions
- read V16A execution plans
- read V16B monitor outputs
- read V16C adaptive control outputs
- verify ID continuity and guardrails
- produce audit records, manifest, and summary

V16D must not:
- execute experiments
- modify policies
- modify execution plans
- modify monitor outputs
- modify control outputs
- modify hypotheses
- modify evidence
- recalculate scientific scores
- allocate external resources
- approve deployment
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
from typing import Dict, List

from tools.trade_inspector.common.execution_utils import index_by, read_csv, stable_hash, write_csv, write_text


DEFAULT_POLICY_INPUT = (
    "outputs/trade_inspector/v15d/"
    "smoke_decision_policy_2026-06-21/"
    "v15d_decision_policy.csv"
)

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

DEFAULT_CONTROL_INPUT = (
    "outputs/trade_inspector/v16c/"
    "smoke_adaptive_execution_controller_2026-06-21/"
    "v16c_adaptive_execution_control.csv"
)



def audit_row(
    execution_row: Dict[str, str],
    policy_by_id: Dict[str, Dict[str, str]],
    monitor_by_execution_id: Dict[str, Dict[str, str]],
    control_by_execution_id: Dict[str, Dict[str, str]],
) -> Dict[str, str]:
    execution_id = execution_row.get("execution_id", "").strip()
    policy_id = execution_row.get("source_policy_id", "").strip()

    policy_row = policy_by_id.get(policy_id)
    monitor_row = monitor_by_execution_id.get(execution_id)
    control_row = control_by_execution_id.get(execution_id)

    issues: List[str] = []

    if not execution_id:
        issues.append("missing_execution_id")

    if not policy_id:
        issues.append("missing_source_policy_id")

    if policy_row is None:
        issues.append("missing_policy_row")

    if monitor_row is None:
        issues.append("missing_monitor_row")

    if control_row is None:
        issues.append("missing_control_row")

    execution_allowed = execution_row.get("execution_allowed", "").strip().lower()
    external_execution_permitted = execution_row.get("external_execution_permitted", "").strip().lower()
    requires_human_approval = execution_row.get("requires_human_approval", "").strip().lower()

    if execution_allowed != "true":
        issues.append("execution_not_allowed")

    if external_execution_permitted != "false":
        issues.append("external_execution_guardrail_violation")

    if requires_human_approval != "true":
        issues.append("human_approval_guardrail_not_enforced")

    policy_decision = ""
    if policy_row is not None:
        policy_decision = policy_row.get("final_policy_decision", "").strip()
        if policy_decision.upper() != "ALLOW":
            issues.append("policy_not_allow")

    monitor_status = ""
    if monitor_row is not None:
        monitor_status = monitor_row.get("monitor_status", "").strip()
        if monitor_status != "PASS":
            issues.append("monitor_not_pass")
        if monitor_row.get("monitor_issues", "").strip():
            issues.append("monitor_issues_present")

    control_status = ""
    if control_row is not None:
        control_status = control_row.get("control_status", "").strip()
        if control_status != "READY":
            issues.append("control_not_ready")
        if control_row.get("policy_override_permitted", "").strip().lower() != "false":
            issues.append("policy_override_guardrail_violation")
        if control_row.get("score_recalculation_permitted", "").strip().lower() != "false":
            issues.append("score_recalculation_guardrail_violation")

    audit_status = "PASS" if not issues else "WARN"
    audit_reason = "chain_complete_guardrails_intact" if not issues else ";".join(issues)

    payload = {
        "execution_id": execution_id,
        "policy_id": policy_id,
        "policy_decision": policy_decision,
        "monitor_status": monitor_status,
        "control_status": control_status,
        "audit_status": audit_status,
        "audit_reason": audit_reason,
    }

    return {
        "audit_id": stable_hash(payload, "AUDIT"),
        "execution_id": execution_id,
        "policy_id": policy_id,
        "policy_decision": policy_decision,
        "execution_state": execution_row.get("execution_state", "").strip(),
        "execution_allowed": execution_allowed,
        "monitor_status": monitor_status,
        "control_status": control_status,
        "audit_status": audit_status,
        "audit_reason": audit_reason,
        "v15d_policy_present": "true" if policy_row is not None else "false",
        "v16a_execution_present": "true",
        "v16b_monitor_present": "true" if monitor_row is not None else "false",
        "v16c_control_present": "true" if control_row is not None else "false",
        "human_approval_required": requires_human_approval,
        "external_execution_permitted": external_execution_permitted,
        "policy_override_permitted": (
            control_row.get("policy_override_permitted", "").strip().lower()
            if control_row is not None
            else ""
        ),
        "score_recalculation_permitted": (
            control_row.get("score_recalculation_permitted", "").strip().lower()
            if control_row is not None
            else ""
        ),
    }


def build_audit(
    policy_rows: List[Dict[str, str]],
    execution_rows: List[Dict[str, str]],
    monitor_rows: List[Dict[str, str]],
    control_rows: List[Dict[str, str]],
) -> List[Dict[str, str]]:
    policy_by_id = index_by(policy_rows, "policy_id")
    monitor_by_execution_id = index_by(monitor_rows, "execution_id")
    control_by_execution_id = index_by(control_rows, "execution_id")

    return [
        audit_row(
            execution_row,
            policy_by_id,
            monitor_by_execution_id,
            control_by_execution_id,
        )
        for execution_row in execution_rows
    ]


def build_manifest(
    policy_path: Path,
    execution_plan_path: Path,
    monitor_input_path: Path,
    control_input_path: Path,
    output_dir: Path,
    audit_rows: List[Dict[str, str]],
) -> List[Dict[str, str]]:
    pass_count = sum(1 for row in audit_rows if row["audit_status"] == "PASS")
    warn_count = sum(1 for row in audit_rows if row["audit_status"] == "WARN")
    status = "PASS" if warn_count == 0 else "WARN"

    return [
        {
            "module": "V16D Scientific Execution Audit Engine",
            "policy_input": str(policy_path),
            "execution_plan_input": str(execution_plan_path),
            "monitor_input": str(monitor_input_path),
            "control_input": str(control_input_path),
            "output_dir": str(output_dir),
            "total_audit_rows": str(len(audit_rows)),
            "audit_pass_count": str(pass_count),
            "audit_warn_count": str(warn_count),
            "guardrail_no_execution": "true",
            "guardrail_no_input_modification": "true",
            "guardrail_no_policy_modification": "true",
            "guardrail_no_hypothesis_modification": "true",
            "guardrail_no_evidence_modification": "true",
            "guardrail_no_score_recalculation": "true",
            "status": status,
        }
    ]


def write_summary(path: Path, manifest: Dict[str, str]) -> None:
    text = f"""# V16D Scientific Execution Audit Engine Summary

## Status

{manifest["status"]}

## Purpose

V16D creates a reproducible audit trail across the V15D -> V16A -> V16B ->
V16C scientific execution chain.

It does not execute experiments.

## Inputs

- policy_input: {manifest["policy_input"]}
- execution_plan_input: {manifest["execution_plan_input"]}
- monitor_input: {manifest["monitor_input"]}
- control_input: {manifest["control_input"]}

## Output

{manifest["output_dir"]}

## Counts

- total_audit_rows: {manifest["total_audit_rows"]}
- audit_pass_count: {manifest["audit_pass_count"]}
- audit_warn_count: {manifest["audit_warn_count"]}

## Guardrails

- no execution
- no input modification
- no policy modification
- no hypothesis modification
- no evidence modification
- no scientific score recalculation
- no external resource allocation
- no deployment approval

## Interpretation

V16D is an audit layer only. It verifies continuity and guardrail consistency
across the scientific execution chain.
"""
    write_text(path, text)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build V16D scientific execution audit trail."
    )
    parser.add_argument(
        "--policy-input",
        default=DEFAULT_POLICY_INPUT,
        help="Path to V15D decision policy CSV.",
    )
    parser.add_argument(
        "--execution-plan",
        default=DEFAULT_EXECUTION_PLAN,
        help="Path to V16A execution plan CSV.",
    )
    parser.add_argument(
        "--monitor-input",
        default=DEFAULT_MONITOR_INPUT,
        help="Path to V16B monitor CSV.",
    )
    parser.add_argument(
        "--control-input",
        default=DEFAULT_CONTROL_INPUT,
        help="Path to V16C control CSV.",
    )
    parser.add_argument(
        "--output-dir",
        default="outputs/trade_inspector/v16d/smoke_execution_audit_2026-06-21",
        help="Output directory for V16D artifacts.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    policy_path = Path(args.policy_input)
    execution_plan_path = Path(args.execution_plan)
    monitor_input_path = Path(args.monitor_input)
    control_input_path = Path(args.control_input)
    output_dir = Path(args.output_dir)

    policy_rows, _ = read_csv(policy_path)
    execution_rows, _ = read_csv(execution_plan_path)
    monitor_rows, _ = read_csv(monitor_input_path)
    control_rows, _ = read_csv(control_input_path)

    audit_rows = build_audit(policy_rows, execution_rows, monitor_rows, control_rows)

    audit_fields = [
        "audit_id",
        "execution_id",
        "policy_id",
        "policy_decision",
        "execution_state",
        "execution_allowed",
        "monitor_status",
        "control_status",
        "audit_status",
        "audit_reason",
        "v15d_policy_present",
        "v16a_execution_present",
        "v16b_monitor_present",
        "v16c_control_present",
        "human_approval_required",
        "external_execution_permitted",
        "policy_override_permitted",
        "score_recalculation_permitted",
    ]

    manifest_rows = build_manifest(
        policy_path,
        execution_plan_path,
        monitor_input_path,
        control_input_path,
        output_dir,
        audit_rows,
    )
    manifest_fields = list(manifest_rows[0].keys())

    write_csv(output_dir / "v16d_scientific_execution_audit.csv", audit_rows, audit_fields)
    write_csv(output_dir / "v16d_scientific_execution_audit_manifest.csv", manifest_rows, manifest_fields)
    write_summary(output_dir / "v16d_scientific_execution_audit_summary.md", manifest_rows[0])

    print("V16D Scientific Execution Audit Engine completed.")
    print(f"Policy rows: {len(policy_rows)}")
    print(f"Execution rows: {len(execution_rows)}")
    print(f"Monitor rows: {len(monitor_rows)}")
    print(f"Control rows: {len(control_rows)}")
    print(f"Audit rows: {len(audit_rows)}")
    print(f"Status: {manifest_rows[0]['status']}")
    print(f"Output dir: {output_dir}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
