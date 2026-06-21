#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Trade Inspector V15C

Scientific Decision Calibration Engine.

Calibrates scientific decision quality using V15A decisions and V15B feedback.

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
)
from tools.trade_inspector.common import index_by


CALIBRATION_FIELDS = [
    "calibration_id",
    "decision_id",
    "campaign_id",
    "decision_type",
    "decision_priority",
    "expected_knowledge_gain",
    "observed_knowledge_gain",
    "prediction_error",
    "absolute_prediction_error",
    "decision_score",
    "decision_quality_score",
    "calibration_error",
    "prediction_bias",
    "confidence_bias",
    "calibration_class",
    "reliability_score",
    "recommended_weight_adjustment",
    "calibration_action",
    "calibration_reason",
    "created_at_utc",
]

SUMMARY_FIELDS = ["metric", "value"]
MANIFEST_FIELDS = ["artifact", "path", "rows", "status"]


def calibration_class(error_pct: float, bias: float) -> str:
    if error_pct <= 10:
        return "WELL_CALIBRATED"
    if error_pct <= 25:
        return "ACCEPTABLE"
    if bias > 0:
        return "UNDERCONFIDENT_OR_UNDERESTIMATED"
    return "OVERCONFIDENT_OR_OVERESTIMATED"


def weight_adjustment(error_pct: float, bias: float) -> str:
    if error_pct <= 10:
        return "keep_current_weights"
    if bias < 0:
        return "reduce_expected_knowledge_gain_weight"
    if bias > 0:
        return "increase_expected_knowledge_gain_weight_carefully"
    return "review_calibration_weights"


def build_calibration(decision: dict[str, str], feedback: dict[str, str]) -> dict[str, Any]:
    did = decision.get("decision_id", "")
    cid = decision.get("campaign_id", "")

    expected = to_float(decision.get("expected_knowledge_gain"))
    observed = to_float(feedback.get("observed_knowledge_gain"))
    pred_error = observed - expected
    abs_error = abs(pred_error)
    error_pct = (abs_error / expected * 100.0) if expected > 0 else 0.0

    decision_score = to_float(decision.get("decision_score"))
    quality_score = to_float(feedback.get("decision_quality_score"))

    confidence_bias = quality_score - decision_score
    reliability = clamp(100.0 - error_pct)
    cclass = calibration_class(error_pct, pred_error)

    if cclass == "WELL_CALIBRATED":
        action = "NO_CALIBRATION_CHANGE"
    elif cclass == "ACCEPTABLE":
        action = "MONITOR_CALIBRATION"
    else:
        action = "ADJUST_DECISION_MODEL_WEIGHTS"

    return {
        "calibration_id": stable_hash_id("CAL-", [did, cid, cclass, round(error_pct, 4)]),
        "decision_id": did,
        "campaign_id": cid,
        "decision_type": decision.get("decision_type", ""),
        "decision_priority": decision.get("decision_priority", ""),
        "expected_knowledge_gain": round(expected, 4),
        "observed_knowledge_gain": round(observed, 4),
        "prediction_error": round(pred_error, 4),
        "absolute_prediction_error": round(abs_error, 4),
        "decision_score": round(decision_score, 4),
        "decision_quality_score": round(quality_score, 4),
        "calibration_error": round(error_pct, 4),
        "prediction_bias": round(pred_error, 4),
        "confidence_bias": round(confidence_bias, 4),
        "calibration_class": cclass,
        "reliability_score": round(reliability, 4),
        "recommended_weight_adjustment": weight_adjustment(error_pct, pred_error),
        "calibration_action": action,
        "calibration_reason": "calibration_based_on_expected_vs_observed_knowledge_gain_and_decision_quality",
        "created_at_utc": now_utc(),
    }


def build_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = [{"metric": "calibration_rows", "value": len(rows)}]

    if rows:
        avg_error = sum(to_float(r["calibration_error"]) for r in rows) / len(rows)
        avg_reliability = sum(to_float(r["reliability_score"]) for r in rows) / len(rows)
        avg_bias = sum(to_float(r["prediction_bias"]) for r in rows) / len(rows)
    else:
        avg_error = 0.0
        avg_reliability = 0.0
        avg_bias = 0.0

    out.extend([
        {"metric": "avg_calibration_error", "value": round(avg_error, 4)},
        {"metric": "avg_reliability_score", "value": round(avg_reliability, 4)},
        {"metric": "avg_prediction_bias", "value": round(avg_bias, 4)},
    ])

    counts: dict[str, int] = {}
    for row in rows:
        counts[f"calibration_class_{row['calibration_class']}"] = counts.get(f"calibration_class_{row['calibration_class']}", 0) + 1
        counts[f"calibration_action_{row['calibration_action']}"] = counts.get(f"calibration_action_{row['calibration_action']}", 0) + 1

    for key in sorted(counts):
        out.append({"metric": key, "value": counts[key]})

    return out


def write_report(path: Path, rows: list[dict[str, Any]], summary: list[dict[str, Any]]) -> None:
    lines = [
        "# V15C SCIENTIFIC DECISION CALIBRATION ENGINE REPORT",
        "",
        f"Date: {date.today().isoformat()}",
        "Scope: Trade Inspector V15C",
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
        "## Calibration Rows",
        "",
        "| rank | calibration_id | decision | class | error | reliability | action |",
        "|---:|---|---|---|---:|---:|---|",
    ])

    for i, row in enumerate(rows[:20], 1):
        lines.append(
            f"| {i} | {row['calibration_id']} | {row['decision_id']} | "
            f"{row['calibration_class']} | {row['calibration_error']} | "
            f"{row['reliability_score']} | {row['calibration_action']} |"
        )

    lines.extend([
        "",
        "## Guardrails",
        "",
        "- V15C does not change decision weights automatically.",
        "- V15C does not modify upstream artifacts.",
        "- V15C only emits calibration diagnostics and recommendations.",
        "",
    ])

    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--decisions", required=True)
    parser.add_argument("--feedback", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    decisions = read_csv(args.decisions)
    feedback_rows = read_csv(args.feedback)
    feedback_by_decision = index_by(feedback_rows, "decision_id")

    calibration_rows = []
    for decision in decisions:
        feedback = feedback_by_decision.get(decision.get("decision_id", ""))
        if feedback:
            calibration_rows.append(build_calibration(decision, feedback))

    calibration_rows.sort(key=lambda r: (-to_float(r["calibration_error"]), str(r["calibration_id"])))
    summary = build_summary(calibration_rows)

    calibration_path = out_dir / "v15c_decision_calibration.csv"
    summary_path = out_dir / "v15c_calibration_summary.csv"
    manifest_path = out_dir / "v15c_calibration_manifest.csv"
    report_path = out_dir / f"V15C_SCIENTIFIC_DECISION_CALIBRATION_ENGINE_REPORT_{date.today().isoformat()}.md"

    write_csv(calibration_path, calibration_rows, CALIBRATION_FIELDS)
    write_csv(summary_path, summary, SUMMARY_FIELDS)

    manifest = [
        {"artifact": "v15c_decision_calibration.csv", "path": str(calibration_path), "rows": len(calibration_rows), "status": "created"},
        {"artifact": "v15c_calibration_summary.csv", "path": str(summary_path), "rows": len(summary), "status": "created"},
        {"artifact": report_path.name, "path": str(report_path), "rows": 1, "status": "created"},
    ]

    write_csv(manifest_path, manifest, MANIFEST_FIELDS)
    write_report(report_path, calibration_rows, summary)

    print("V15C scientific decision calibration engine completed")
    print("decision_rows:", len(decisions))
    print("feedback_rows:", len(feedback_rows))
    print("calibration_rows:", len(calibration_rows))
    print("report:", report_path)
    print("csv:", calibration_path)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
