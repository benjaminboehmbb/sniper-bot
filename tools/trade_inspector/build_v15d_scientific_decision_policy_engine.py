#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Trade Inspector V15D

Scientific Decision Policy Engine.

Applies scientific policy gates to V15A decisions using V15C calibration.

ASCII only.
"""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path
from typing import Any
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tools.trade_inspector.common import (
    clamp,
    now_utc,
    read_csv,
    stable_hash_id,
    to_float,
    write_csv,
    index_by,
)


POLICY_FIELDS = [
    "policy_id",
    "decision_id",
    "campaign_id",
    "policy_status",
    "policy_gate",
    "policy_priority",
    "decision_type",
    "decision_score",
    "execution_gate",
    "resource_class",
    "calibration_class",
    "calibration_error",
    "reliability_score",
    "evidence_policy",
    "calibration_policy",
    "resource_policy",
    "human_review_policy",
    "final_policy_decision",
    "allowed_next_action",
    "blocked_reason",
    "policy_reason",
    "created_at_utc",
]

SUMMARY_FIELDS = ["metric", "value"]
MANIFEST_FIELDS = ["artifact", "path", "rows", "status"]


def policy_priority(score: float, reliability: float, blocked: bool) -> str:
    if blocked:
        return "BLOCKED"
    if score >= 80 and reliability >= 80:
        return "VERY_HIGH"
    if score >= 65 and reliability >= 70:
        return "HIGH"
    if score >= 45:
        return "MEDIUM"
    return "LOW"


def build_policy(decision: dict[str, str], calibration: dict[str, str] | None) -> dict[str, Any]:
    did = decision.get("decision_id", "")
    cid = decision.get("campaign_id", "")

    decision_score = to_float(decision.get("decision_score"))
    runtime = to_float(decision.get("estimated_runtime_minutes"))

    cclass = calibration.get("calibration_class", "UNKNOWN") if calibration else "UNKNOWN"
    cerror = to_float(calibration.get("calibration_error") if calibration else 100.0)
    reliability = to_float(calibration.get("reliability_score") if calibration else 0.0)

    execution_gate = decision.get("execution_gate", "")
    resource = decision.get("resource_class", "")
    dtype = decision.get("decision_type", "")

    evidence_ok = decision_score >= 45
    calibration_ok = cerror <= 25 and reliability >= 70
    resource_ok = runtime <= 120
    human_review_required = (
        execution_gate == "MANUAL_APPROVAL_REQUIRED"
        or resource == "HEAVY"
        or cclass in {"OVERCONFIDENT_OR_OVERESTIMATED", "UNKNOWN"}
    )

    blocked_reasons: list[str] = []

    if dtype == "BLOCK":
        blocked_reasons.append("decision_type_blocked")
    if execution_gate == "CLOSED":
        blocked_reasons.append("execution_gate_closed")
    if not evidence_ok:
        blocked_reasons.append("insufficient_decision_score")
    if not calibration_ok:
        blocked_reasons.append("calibration_not_sufficient")
    if not resource_ok:
        blocked_reasons.append("resource_runtime_too_high")

    blocked = bool(blocked_reasons)

    if blocked:
        final = "BLOCK"
        allowed_action = "do_not_execute"
        policy_gate = "CLOSED"
        status = "BLOCKED"
    elif human_review_required:
        final = "ALLOW_WITH_HUMAN_REVIEW"
        allowed_action = "request_human_review_before_execution"
        policy_gate = "HUMAN_REVIEW"
        status = "REVIEW_REQUIRED"
    else:
        final = "ALLOW"
        allowed_action = decision.get("recommended_action", "")
        policy_gate = "OPEN"
        status = "APPROVED"

    return {
        "policy_id": stable_hash_id("POL-", [did, cid, final, policy_gate]),
        "decision_id": did,
        "campaign_id": cid,
        "policy_status": status,
        "policy_gate": policy_gate,
        "policy_priority": policy_priority(decision_score, reliability, blocked),
        "decision_type": dtype,
        "decision_score": round(decision_score, 4),
        "execution_gate": execution_gate,
        "resource_class": resource,
        "calibration_class": cclass,
        "calibration_error": round(cerror, 4),
        "reliability_score": round(reliability, 4),
        "evidence_policy": "PASS" if evidence_ok else "FAIL",
        "calibration_policy": "PASS" if calibration_ok else "FAIL",
        "resource_policy": "PASS" if resource_ok else "FAIL",
        "human_review_policy": "REQUIRED" if human_review_required else "NOT_REQUIRED",
        "final_policy_decision": final,
        "allowed_next_action": allowed_action,
        "blocked_reason": ";".join(blocked_reasons) if blocked_reasons else "none",
        "policy_reason": "policy_based_on_evidence_calibration_resources_and_human_review_gates",
        "created_at_utc": now_utc(),
    }


def build_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = [{"metric": "policy_rows", "value": len(rows)}]

    counts: dict[str, int] = {}
    for row in rows:
        for field in [
            "policy_status",
            "policy_gate",
            "policy_priority",
            "final_policy_decision",
            "evidence_policy",
            "calibration_policy",
            "resource_policy",
            "human_review_policy",
        ]:
            key = f"{field}_{row[field]}"
            counts[key] = counts.get(key, 0) + 1

    for key in sorted(counts):
        out.append({"metric": key, "value": counts[key]})

    return out


def write_report(path: Path, rows: list[dict[str, Any]], summary: list[dict[str, Any]]) -> None:
    lines = [
        "# V15D SCIENTIFIC DECISION POLICY ENGINE REPORT",
        "",
        f"Date: {date.today().isoformat()}",
        "Scope: Trade Inspector V15D",
        "",
        "## Summary",
        "",
        "| metric | value |",
        "|---|---:|",
    ]

    for row in summary:
        lines.append(f"| {row['metric']} | {row['value']} |")

    lines.extend([
        "",
        "## Policy Decisions",
        "",
        "| rank | policy_id | decision | final | gate | priority | blocked_reason |",
        "|---:|---|---|---|---|---|---|",
    ])

    for i, row in enumerate(rows[:20], 1):
        lines.append(
            f"| {i} | {row['policy_id']} | {row['decision_id']} | "
            f"{row['final_policy_decision']} | {row['policy_gate']} | "
            f"{row['policy_priority']} | {row['blocked_reason']} |"
        )

    lines.extend([
        "",
        "## Guardrails",
        "",
        "- V15D does not execute decisions.",
        "- V15D does not modify strategy logic.",
        "- V15D only approves, blocks, or routes scientific decisions through policy gates.",
        "",
    ])

    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--decisions", required=True)
    parser.add_argument("--calibration", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    decisions = read_csv(args.decisions)
    calibration_rows = read_csv(args.calibration)
    calibration_by_decision = index_by(calibration_rows, "decision_id")

    policy_rows = [
        build_policy(decision, calibration_by_decision.get(decision.get("decision_id", "")))
        for decision in decisions
    ]
    policy_rows.sort(key=lambda r: (str(r["policy_gate"]), -to_float(r["decision_score"]), str(r["policy_id"])))

    summary = build_summary(policy_rows)

    policy_path = out_dir / "v15d_decision_policy.csv"
    summary_path = out_dir / "v15d_policy_summary.csv"
    manifest_path = out_dir / "v15d_policy_manifest.csv"
    report_path = out_dir / f"V15D_SCIENTIFIC_DECISION_POLICY_ENGINE_REPORT_{date.today().isoformat()}.md"

    write_csv(policy_path, policy_rows, POLICY_FIELDS)
    write_csv(summary_path, summary, SUMMARY_FIELDS)

    manifest = [
        {"artifact": "v15d_decision_policy.csv", "path": str(policy_path), "rows": len(policy_rows), "status": "created"},
        {"artifact": "v15d_policy_summary.csv", "path": str(summary_path), "rows": len(summary), "status": "created"},
        {"artifact": report_path.name, "path": str(report_path), "rows": 1, "status": "created"},
    ]

    write_csv(manifest_path, manifest, MANIFEST_FIELDS)
    write_report(report_path, policy_rows, summary)

    print("V15D scientific decision policy engine completed")
    print("decision_rows:", len(decisions))
    print("calibration_rows:", len(calibration_rows))
    print("policy_rows:", len(policy_rows))
    print("report:", report_path)
    print("csv:", policy_path)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
