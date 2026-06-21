#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Trade Inspector V15B

Scientific Decision Feedback Engine.

Evaluates scientific decisions and creates learning events.

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
    group_by,
    index_by,
    clamp,
    now_utc,
    read_csv,
    stable_hash_id,
    to_float,
    write_csv,
)


FEEDBACK_FIELDS = [
    "feedback_id",
    "decision_id",
    "campaign_id",
    "decision_type",
    "decision_status",
    "decision_outcome",
    "expected_knowledge_gain",
    "observed_knowledge_gain",
    "prediction_error",
    "calibration_error",
    "decision_quality_score",
    "recommendation_accuracy",
    "knowledge_update_required",
    "reasoning_update_required",
    "planning_update_required",
    "campaign_update_required",
    "feedback_action",
    "feedback_reason",
    "created_at_utc",
]

LEARNING_EVENT_FIELDS = [
    "learning_event_id",
    "source_feedback_id",
    "decision_id",
    "campaign_id",
    "event_type",
    "event_priority",
    "target_layer",
    "learning_signal",
    "recommended_update",
    "created_at_utc",
]

SUMMARY_FIELDS = ["metric", "value"]
MANIFEST_FIELDS = ["artifact", "path", "rows", "status"]


def infer_observed_gain(decision: dict[str, str], campaign: dict[str, str] | None) -> float:
    # No real execution outcome exists yet.
    # Use conservative proxy from current campaign readiness.
    expected = to_float(decision.get("expected_knowledge_gain"))
    status = campaign.get("campaign_status", "") if campaign else decision.get("campaign_status", "")
    gate = decision.get("execution_gate", "")

    if status == "BLOCKED" or gate == "CLOSED":
        return 0.0
    if gate == "MANUAL_APPROVAL_REQUIRED":
        return expected * 0.50
    return expected * 0.85


def outcome_class(expected: float, observed: float) -> str:
    if expected <= 0 and observed <= 0:
        return "NO_SIGNAL"
    ratio = observed / expected if expected > 0 else 0.0
    if ratio >= 0.90:
        return "CONFIRMED"
    if ratio >= 0.65:
        return "PARTIALLY_CONFIRMED"
    if ratio >= 0.30:
        return "WEAKLY_CONFIRMED"
    return "NOT_CONFIRMED"


def quality_score(expected: float, observed: float, gate: str) -> float:
    if expected <= 0:
        return 0.0
    error = abs(expected - observed)
    base = 100.0 - (error / max(expected, 1.0) * 100.0)
    if gate == "OPEN":
        base += 5.0
    elif gate == "CLOSED":
        base -= 25.0
    return clamp(base)


def bool_text(flag: bool) -> str:
    return "yes" if flag else "no"


def build_feedback(
    decision: dict[str, str],
    campaign: dict[str, str] | None,
) -> dict[str, Any]:
    did = decision.get("decision_id", "")
    cid = decision.get("campaign_id", "")

    expected = to_float(decision.get("expected_knowledge_gain"))
    observed = infer_observed_gain(decision, campaign)
    pred_error = observed - expected
    calib_error = abs(pred_error)
    qscore = quality_score(expected, observed, decision.get("execution_gate", ""))
    outcome = outcome_class(expected, observed)

    knowledge_update = outcome in {"CONFIRMED", "PARTIALLY_CONFIRMED", "NOT_CONFIRMED"}
    reasoning_update = outcome in {"WEAKLY_CONFIRMED", "NOT_CONFIRMED"}
    planning_update = outcome in {"PARTIALLY_CONFIRMED", "WEAKLY_CONFIRMED", "NOT_CONFIRMED"}
    campaign_update = decision.get("decision_type") in {"BLOCK", "DEFER"} or outcome == "NOT_CONFIRMED"

    if outcome == "CONFIRMED":
        action = "UPDATE_KNOWLEDGE"
    elif outcome == "PARTIALLY_CONFIRMED":
        action = "UPDATE_KNOWLEDGE_AND_PLANNING"
    elif outcome == "WEAKLY_CONFIRMED":
        action = "UPDATE_REASONING_AND_PLANNING"
    elif outcome == "NOT_CONFIRMED":
        action = "REVIEW_DECISION_MODEL"
    else:
        action = "NO_CHANGE"

    return {
        "feedback_id": stable_hash_id("FB-", [did, cid, outcome, round(observed, 4)]),
        "decision_id": did,
        "campaign_id": cid,
        "decision_type": decision.get("decision_type", ""),
        "decision_status": decision.get("decision_status", ""),
        "decision_outcome": outcome,
        "expected_knowledge_gain": round(expected, 4),
        "observed_knowledge_gain": round(observed, 4),
        "prediction_error": round(pred_error, 4),
        "calibration_error": round(calib_error, 4),
        "decision_quality_score": round(qscore, 4),
        "recommendation_accuracy": round(qscore, 4),
        "knowledge_update_required": bool_text(knowledge_update),
        "reasoning_update_required": bool_text(reasoning_update),
        "planning_update_required": bool_text(planning_update),
        "campaign_update_required": bool_text(campaign_update),
        "feedback_action": action,
        "feedback_reason": "feedback_generated_from_expected_vs_observed_knowledge_gain_proxy",
        "created_at_utc": now_utc(),
    }


def build_learning_events(feedback_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []

    for row in feedback_rows:
        feedback_id = str(row["feedback_id"])
        did = str(row["decision_id"])
        cid = str(row["campaign_id"])
        outcome = str(row["decision_outcome"])

        targets: list[tuple[str, str, str]] = []

        if row["knowledge_update_required"] == "yes":
            targets.append(("KNOWLEDGE_UPDATE", "V11_V13", "refresh_knowledge_state"))
        if row["reasoning_update_required"] == "yes":
            targets.append(("REASONING_UPDATE", "V14A", "recompute_reasoning_rules"))
        if row["planning_update_required"] == "yes":
            targets.append(("PLANNING_UPDATE", "V14B", "recompute_research_plans"))
        if row["campaign_update_required"] == "yes":
            targets.append(("CAMPAIGN_UPDATE", "V14C", "recompute_campaign_grouping"))

        if not targets:
            targets.append(("NO_CHANGE", "NONE", "no_update_required"))

        for event_type, target_layer, update in targets:
            priority = "HIGH" if outcome in {"NOT_CONFIRMED", "WEAKLY_CONFIRMED"} else "MEDIUM"

            events.append(
                {
                    "learning_event_id": stable_hash_id("LEARN-", [feedback_id, event_type, target_layer]),
                    "source_feedback_id": feedback_id,
                    "decision_id": did,
                    "campaign_id": cid,
                    "event_type": event_type,
                    "event_priority": priority,
                    "target_layer": target_layer,
                    "learning_signal": outcome,
                    "recommended_update": update,
                    "created_at_utc": now_utc(),
                }
            )

    return events



def build_summary(feedback_rows: list[dict[str, Any]], learning_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = [
        {"metric": "feedback_rows", "value": len(feedback_rows)},
        {"metric": "learning_event_rows", "value": len(learning_rows)},
    ]

    counts: dict[str, int] = {}
    for row in feedback_rows:
        counts[f"decision_outcome_{row['decision_outcome']}"] = counts.get(f"decision_outcome_{row['decision_outcome']}", 0) + 1
        counts[f"feedback_action_{row['feedback_action']}"] = counts.get(f"feedback_action_{row['feedback_action']}", 0) + 1

    for row in learning_rows:
        counts[f"learning_event_type_{row['event_type']}"] = counts.get(f"learning_event_type_{row['event_type']}", 0) + 1

    for key in sorted(counts):
        rows.append({"metric": key, "value": counts[key]})

    return rows


def write_report(path: Path, feedback_rows: list[dict[str, Any]], learning_rows: list[dict[str, Any]], summary: list[dict[str, Any]]) -> None:
    lines = [
        "# V15B SCIENTIFIC DECISION FEEDBACK ENGINE REPORT",
        "",
        f"Date: {date.today().isoformat()}",
        "Scope: Trade Inspector V15B",
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
        "## Feedback",
        "",
        "| rank | feedback_id | decision | outcome | quality | action |",
        "|---:|---|---|---|---:|---|",
    ])

    for i, row in enumerate(feedback_rows[:20], 1):
        lines.append(
            f"| {i} | {row['feedback_id']} | {row['decision_id']} | "
            f"{row['decision_outcome']} | {row['decision_quality_score']} | "
            f"{row['feedback_action']} |"
        )

    lines.extend([
        "",
        "## Guardrails",
        "",
        "- V15B does not modify upstream artifacts.",
        "- V15B does not execute campaigns.",
        "- V15B only creates feedback and learning events.",
        "",
    ])

    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--decisions", required=True)
    parser.add_argument("--campaigns", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    decisions = read_csv(args.decisions)
    campaigns = read_csv(args.campaigns)
    campaign_by_id = index_by(campaigns, "campaign_id")

    feedback_rows = [
        build_feedback(decision, campaign_by_id.get(decision.get("campaign_id", "")))
        for decision in decisions
    ]
    learning_rows = build_learning_events(feedback_rows)
    summary = build_summary(feedback_rows, learning_rows)

    feedback_path = out_dir / "v15b_decision_feedback.csv"
    learning_path = out_dir / "v15b_learning_events.csv"
    summary_path = out_dir / "v15b_feedback_summary.csv"
    manifest_path = out_dir / "v15b_feedback_manifest.csv"
    report_path = out_dir / f"V15B_SCIENTIFIC_DECISION_FEEDBACK_ENGINE_REPORT_{date.today().isoformat()}.md"

    write_csv(feedback_path, feedback_rows, FEEDBACK_FIELDS)
    write_csv(learning_path, learning_rows, LEARNING_EVENT_FIELDS)
    write_csv(summary_path, summary, SUMMARY_FIELDS)

    manifest = [
        {"artifact": "v15b_decision_feedback.csv", "path": str(feedback_path), "rows": len(feedback_rows), "status": "created"},
        {"artifact": "v15b_learning_events.csv", "path": str(learning_path), "rows": len(learning_rows), "status": "created"},
        {"artifact": "v15b_feedback_summary.csv", "path": str(summary_path), "rows": len(summary), "status": "created"},
        {"artifact": report_path.name, "path": str(report_path), "rows": 1, "status": "created"},
    ]

    write_csv(manifest_path, manifest, MANIFEST_FIELDS)
    write_report(report_path, feedback_rows, learning_rows, summary)

    print("V15B scientific decision feedback engine completed")
    print("decision_rows:", len(decisions))
    print("campaign_rows:", len(campaigns))
    print("feedback_rows:", len(feedback_rows))
    print("learning_event_rows:", len(learning_rows))
    print("report:", report_path)
    print("csv:", feedback_path)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
