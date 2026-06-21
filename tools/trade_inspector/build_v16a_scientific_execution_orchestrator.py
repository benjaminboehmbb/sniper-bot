#!/usr/bin/env python3
"""
V16A Scientific Execution Orchestrator.

Purpose:
Read approved scientific decision policy outputs and convert them into a
controlled execution plan.

Guardrails:
- Does not execute experiments.
- Does not modify policies.
- Does not modify hypotheses.
- Does not modify evidence.
- Does not recalculate scientific scores.
- Does not allocate external resources.
- Does not approve deployment.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
from typing import Dict, Iterable, List

from tools.trade_inspector.common.execution_utils import read_csv, stable_hash, write_csv, write_text


DEFAULT_POLICY_INPUT = (
    "outputs/trade_inspector/v15d/"
    "smoke_decision_policy_2026-06-21/"
    "v15d_decision_policy.csv"
)


APPROVE_TOKENS = (
    "approve",
    "approved",
    "execute",
    "proceed",
    "run",
    "accepted",
    "allow",
    "allowed",
)

BLOCK_TOKENS = (
    "reject",
    "rejected",
    "block",
    "blocked",
    "hold",
    "defer",
    "deferred",
    "stop",
    "deny",
    "denied",
)



def get_first_present(row: Dict[str, str], candidates: Iterable[str]) -> str:
    for key in candidates:
        value = row.get(key, "")
        if value is not None and str(value).strip():
            return str(value).strip()
    return ""


def classify_policy(row: Dict[str, str]) -> Tuple[str, str]:
    decision_text = get_first_present(
        row,
        (
            "final_policy_decision",
            "policy_decision",
            "decision",
            "final_decision",
            "policy_action",
            "recommended_action",
            "recommended_next_action",
            "action",
            "status",
        ),
    ).lower()

    if not decision_text:
        return "requires_human_review", "No explicit policy decision column was detected."

    if any(token in decision_text for token in BLOCK_TOKENS):
        return "held", "Policy text contains a block, hold, reject, defer, or stop token."

    if decision_text in ("allow", "allowed"):
        return "ready", "Final policy decision allows controlled execution planning."

    if any(token in decision_text for token in APPROVE_TOKENS):
        return "ready", "Policy text contains an approval or execution token."

    return "requires_human_review", "Policy text could not be safely mapped to ready or held."


def derive_priority(row: Dict[str, str]) -> str:
    raw = get_first_present(
        row,
        (
            "priority",
            "policy_priority",
            "execution_priority",
            "rank",
            "decision_rank",
        ),
    )

    if not raw:
        return "medium"

    text = raw.strip().lower()

    if text in ("critical", "high", "medium", "low"):
        return text

    try:
        value = float(text)
    except ValueError:
        return "medium"

    if value <= 1:
        return "high"
    if value <= 3:
        return "medium"
    return "low"


def build_execution_plan(rows: List[Dict[str, str]]) -> List[Dict[str, str]]:
    plan_rows: List[Dict[str, str]] = []

    for index, row in enumerate(rows, start=1):
        execution_state, guardrail_reason = classify_policy(row)
        priority = derive_priority(row)

        source_id = get_first_present(
            row,
            (
                "policy_id",
                "decision_id",
                "hypothesis_id",
                "research_object_id",
                "campaign_id",
                "experiment_id",
            ),
        )

        payload = {
            "row_index": str(index),
            "source_id": source_id,
            "row": row,
        }

        execution_id = stable_hash(payload, "EXEC")

        execution_allowed = "true" if execution_state == "ready" else "false"

        plan_rows.append(
            {
                "execution_id": execution_id,
                "source_policy_id": source_id,
                "execution_state": execution_state,
                "execution_allowed": execution_allowed,
                "execution_priority": priority,
                "execution_order": str(index),
                "execution_type": "scientific_policy_execution_plan",
                "orchestrator_action": "prepare_execution_plan",
                "requires_human_approval": "true",
                "external_execution_permitted": "false",
                "guardrail_reason": guardrail_reason,
                "input_row_hash": stable_hash(row, "ROW"),
            }
        )

    return plan_rows


def build_manifest(
    input_path: Path,
    output_dir: Path,
    plan_rows: List[Dict[str, str]],
) -> List[Dict[str, str]]:
    ready = sum(1 for row in plan_rows if row["execution_state"] == "ready")
    held = sum(1 for row in plan_rows if row["execution_state"] == "held")
    review = sum(1 for row in plan_rows if row["execution_state"] == "requires_human_review")

    return [
        {
            "module": "V16A Scientific Execution Orchestrator",
            "input_file": str(input_path),
            "output_dir": str(output_dir),
            "total_execution_plan_rows": str(len(plan_rows)),
            "ready_count": str(ready),
            "held_count": str(held),
            "requires_human_review_count": str(review),
            "guardrail_no_execution": "true",
            "guardrail_no_policy_modification": "true",
            "guardrail_no_score_recalculation": "true",
            "status": "PASS",
        }
    ]


def write_summary(path: Path, manifest: Dict[str, str]) -> None:
    text = f"""# V16A Scientific Execution Orchestrator Summary

## Status

PASS

## Purpose

V16A converts approved scientific policy outputs into a controlled execution plan.

It does not execute experiments.

## Input

{manifest["input_file"]}

## Output

{manifest["output_dir"]}

## Counts

- total_execution_plan_rows: {manifest["total_execution_plan_rows"]}
- ready_count: {manifest["ready_count"]}
- held_count: {manifest["held_count"]}
- requires_human_review_count: {manifest["requires_human_review_count"]}

## Guardrails

- no external execution
- no policy modification
- no hypothesis modification
- no evidence modification
- no scientific score recalculation
- human approval remains required

## Interpretation

V16A is an execution planning layer only. It separates scientific decision
approval from controlled execution preparation.
"""
    write_text(path, text)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build V16A scientific execution orchestration plan."
    )
    parser.add_argument(
        "--policy-input",
        default=DEFAULT_POLICY_INPUT,
        help="Path to V15D policy summary CSV.",
    )
    parser.add_argument(
        "--output-dir",
        default="outputs/trade_inspector/v16a/smoke_execution_orchestrator_2026-06-21",
        help="Output directory for V16A artifacts.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    input_path = Path(args.policy_input)
    output_dir = Path(args.output_dir)

    rows, _ = read_csv(input_path)
    plan_rows = build_execution_plan(rows)

    plan_fields = [
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

    manifest_rows = build_manifest(input_path, output_dir, plan_rows)
    manifest_fields = list(manifest_rows[0].keys())

    write_csv(output_dir / "v16a_execution_plan.csv", plan_rows, plan_fields)
    write_csv(output_dir / "v16a_execution_manifest.csv", manifest_rows, manifest_fields)
    write_summary(output_dir / "v16a_execution_summary.md", manifest_rows[0])

    print("V16A Scientific Execution Orchestrator completed.")
    print(f"Input rows: {len(rows)}")
    print(f"Execution plan rows: {len(plan_rows)}")
    print(f"Output dir: {output_dir}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
