#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tools.trade_inspector.common.execution_utils import read_csv, write_csv, write_text

DEFAULT_GOVERNANCE = "outputs/trade_inspector/v17a/smoke_system_governance_2026-06-21/v17a_governance_assessment.csv"
DEFAULT_PERFORMANCE = "outputs/trade_inspector/v17b/smoke_performance_meta_2026-06-21/v17b_performance_evaluation.csv"
DEFAULT_ARCHITECTURE = "outputs/trade_inspector/v17c/smoke_architecture_health_2026-06-21/v17c_architecture_health.csv"
DEFAULT_OUTPUT = "outputs/trade_inspector/v17d/smoke_system_improvement_2026-06-21"


def make_proposal(pid, proposal_type, source_module, source_evidence, affected_layer,
                  affected_module, priority, risk_level, expected_benefit,
                  proposal_reason, recommended_next_action):
    return {
        "proposal_id": f"PROP-{pid:04d}",
        "proposal_type": proposal_type,
        "source_module": source_module,
        "source_evidence": source_evidence,
        "affected_layer": affected_layer,
        "affected_module": affected_module,
        "priority": priority,
        "risk_level": risk_level,
        "expected_benefit": expected_benefit,
        "implementation_allowed": "false",
        "automatic_execution_allowed": "false",
        "manual_review_required": "true",
        "proposal_reason": proposal_reason,
        "recommended_next_action": recommended_next_action,
    }


def build_proposals(governance_rows, performance_rows, architecture_rows):
    proposals = []
    pid = 1

    for row in governance_rows:
        proposals.append(make_proposal(
            pid,
            "GOVERNANCE_REVIEW",
            "V17A",
            row.get("governance_check", ""),
            "V17",
            "Governance",
            "LOW",
            "LOW",
            "Maintain governance quality",
            row.get("finding", ""),
            row.get("recommendation", "manual_review"),
        ))
        pid += 1

    for row in performance_rows:
        proposals.append(make_proposal(
            pid,
            "PERFORMANCE_MONITORING",
            "V17B",
            row.get("metric", ""),
            "V17",
            "Performance Meta-Evaluation",
            "LOW",
            "LOW",
            "Maintain scientific-system performance visibility",
            f"Metric status: {row.get('status', '')}",
            row.get("recommendation", "manual_review"),
        ))
        pid += 1

    for row in architecture_rows:
        proposals.append(make_proposal(
            pid,
            "ARCHITECTURE_HEALTH_MONITORING",
            "V17C",
            row.get("metric", ""),
            "V17",
            "Architecture Health",
            "LOW",
            row.get("risk_level", "LOW"),
            "Maintain architecture health visibility",
            f"Architecture health status: {row.get('status', '')}",
            row.get("recommendation", "manual_review"),
        ))
        pid += 1

    return proposals


def parse_args():
    parser = argparse.ArgumentParser(
        description="Build V17D scientific system improvement proposals."
    )
    parser.add_argument("--governance-input", default=DEFAULT_GOVERNANCE)
    parser.add_argument("--performance-input", default=DEFAULT_PERFORMANCE)
    parser.add_argument("--architecture-input", default=DEFAULT_ARCHITECTURE)
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main():
    args = parse_args()
    out = Path(args.output_dir)

    governance_rows, _ = read_csv(Path(args.governance_input))
    performance_rows, _ = read_csv(Path(args.performance_input))
    architecture_rows, _ = read_csv(Path(args.architecture_input))

    proposals = build_proposals(governance_rows, performance_rows, architecture_rows)

    fields = [
        "proposal_id",
        "proposal_type",
        "source_module",
        "source_evidence",
        "affected_layer",
        "affected_module",
        "priority",
        "risk_level",
        "expected_benefit",
        "implementation_allowed",
        "automatic_execution_allowed",
        "manual_review_required",
        "proposal_reason",
        "recommended_next_action",
    ]

    write_csv(out / "v17d_improvement_proposals.csv", proposals, fields)

    high_risk = sum(1 for row in proposals if row["risk_level"] == "HIGH")
    summary = [{
        "module": "V17D Scientific System Improvement Planner",
        "proposal_count": str(len(proposals)),
        "high_risk_count": str(high_risk),
        "implementation_allowed_count": "0",
        "automatic_execution_allowed_count": "0",
        "overall_status": "PASS",
        "recommended_next_action": "manual_review",
    }]

    write_csv(out / "v17d_improvement_summary.csv", summary, list(summary[0].keys()))

    report = (
        "# V17D Scientific System Improvement Planner\n\n"
        "Status: PASS\n\n"
        f"Generated proposals: {len(proposals)}\n\n"
        "All proposals require manual review.\n\n"
        "No implementation or automatic execution is allowed.\n"
    )

    write_text(
        out / "V17D_SCIENTIFIC_SYSTEM_IMPROVEMENT_PLANNER_REPORT_2026-06-21.md",
        report,
    )

    print("V17D Scientific System Improvement Planner completed.")
    print(f"Improvement proposals: {len(proposals)}")
    print("Overall status: PASS")
    print(f"Output dir: {out}")


if __name__ == "__main__":
    main()
