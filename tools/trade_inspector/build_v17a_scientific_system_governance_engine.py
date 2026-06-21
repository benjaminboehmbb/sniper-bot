#!/usr/bin/env python3
"""
V17A Scientific System Governance Engine.

Purpose:
Evaluate governance health of the certified V11-V16 Scientific Core.

V17A may:
- read architecture certification artifacts
- read review outputs
- assess governance readiness
- detect architecture boundary risks
- produce governance recommendations

V17A must not:
- modify scientific decisions
- modify policies
- bypass V15D
- modify V16 execution plans
- execute experiments
- create strategy logic
- approve live deployment
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path
from typing import Dict, List, Tuple

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tools.trade_inspector.common.execution_utils import read_csv, write_csv, write_text


DEFAULT_CERTIFICATION = (
    "docs/trade_inspector/review_v11_v16/"
    "V11_TO_V16_SCIENTIFIC_ARCHITECTURE_CERTIFICATION_2026-06-21.md"
)

DEFAULT_PHASE5C = (
    "outputs/trade_inspector/review_v11_v16_2026-06-21/"
    "phase5c_v17_readiness_review.csv"
)

DEFAULT_PHASE5D = (
    "outputs/trade_inspector/review_v11_v16_2026-06-21/"
    "phase5d_final_architecture_judgment.md"
)


def read_text_file(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")
    return path.read_text(encoding="utf-8")


def contains_all(text: str, required_terms: List[str]) -> Tuple[bool, List[str]]:
    missing = [term for term in required_terms if term not in text]
    return len(missing) == 0, missing


def evaluate_certification(certification_text: str) -> Dict[str, str]:
    required_terms = [
        "SCIENTIFIC_ARCHITECTURE_CERTIFICATION: PASS",
        "CERTIFICATION_PASS",
        "V17A Scientific System Governance Engine",
        "V15 remains the scientific decision boundary.",
        "V16 remains the scientific execution-preparation and audit boundary.",
    ]

    passed, missing = contains_all(certification_text, required_terms)

    return {
        "governance_check": "certification_integrity",
        "status": "PASS" if passed else "WARN",
        "severity": "critical" if not passed else "none",
        "finding": "certification confirms V11-V16 scientific core readiness" if passed else "certification is incomplete",
        "missing_terms": ";".join(missing),
        "recommendation": "allow_governance_layer_start" if passed else "block_v17_until_certification_reviewed",
    }


def evaluate_v17_readiness(rows: List[Dict[str, str]]) -> Dict[str, str]:
    results = {row.get("result", "") for row in rows}
    has_constraints = "PASS_WITH_CONSTRAINTS" in results
    has_watch = "WATCH" in results

    if has_constraints:
        status = "PASS"
        finding = "V17 readiness exists with explicit scope constraints"
        recommendation = "start_v17a_governance_only"
    else:
        status = "WARN"
        finding = "V17 readiness constraints not found"
        recommendation = "block_v17_until_readiness_constraints_exist"

    return {
        "governance_check": "v17_readiness_constraints",
        "status": status,
        "severity": "watch" if has_watch else "none",
        "finding": finding,
        "missing_terms": "",
        "recommendation": recommendation,
    }


def evaluate_forbidden_scope(certification_text: str, phase5d_text: str) -> Dict[str, str]:
    combined = certification_text + "\n" + phase5d_text

    forbidden_terms = [
        "execution runner",
        "strategy generation layer",
        "decision override layer",
        "policy bypass layer",
        "live trading layer",
    ]

    passed, missing = contains_all(combined, forbidden_terms)

    return {
        "governance_check": "forbidden_scope_defined",
        "status": "PASS" if passed else "WARN",
        "severity": "critical" if not passed else "none",
        "finding": "forbidden V17 scopes are explicitly documented" if passed else "forbidden V17 scopes are incomplete",
        "missing_terms": ";".join(missing),
        "recommendation": "preserve_v17_scope_guardrails" if passed else "define_forbidden_v17_scope_before_expansion",
    }


def evaluate_protected_boundaries(certification_text: str) -> Dict[str, str]:
    required_terms = [
        "V15A Scientific Decision Engine",
        "V15D Scientific Decision Policy Engine",
        "must not be modified without a concrete defect",
    ]

    passed, missing = contains_all(certification_text, required_terms)

    return {
        "governance_check": "protected_boundaries",
        "status": "PASS" if passed else "WARN",
        "severity": "critical" if not passed else "none",
        "finding": "protected V15 decision boundary modules are documented" if passed else "protected boundary documentation incomplete",
        "missing_terms": ";".join(missing),
        "recommendation": "protect_v15a_v15d" if passed else "block_boundary_changes_until_documented",
    }


def build_summary(governance_rows: List[Dict[str, str]]) -> List[Dict[str, str]]:
    pass_count = sum(1 for row in governance_rows if row["status"] == "PASS")
    warn_count = sum(1 for row in governance_rows if row["status"] == "WARN")
    critical_count = sum(1 for row in governance_rows if row["severity"] == "critical")

    if critical_count > 0:
        governance_status = "BLOCKED"
    elif warn_count > 0:
        governance_status = "PASS_WITH_WATCH"
    else:
        governance_status = "PASS"

    return [
        {
            "module": "V17A Scientific System Governance Engine",
            "governance_checks": str(len(governance_rows)),
            "pass_count": str(pass_count),
            "warn_count": str(warn_count),
            "critical_count": str(critical_count),
            "governance_status": governance_status,
            "recommended_next_action": (
                "start_governance_layer_development"
                if governance_status in ("PASS", "PASS_WITH_WATCH")
                else "resolve_critical_governance_findings"
            ),
        }
    ]


def write_report(path: Path, summary: Dict[str, str], rows: List[Dict[str, str]]) -> None:
    lines: List[str] = []
    lines.append("# V17A Scientific System Governance Engine Report")
    lines.append("")
    lines.append("Date: 2026-06-21")
    lines.append("Project: Sniper-Bot / Trade Inspector")
    lines.append("")
    lines.append("## Status")
    lines.append("")
    lines.append(summary["governance_status"])
    lines.append("")
    lines.append("## Purpose")
    lines.append("")
    lines.append("V17A evaluates whether the certified V11-V16 scientific core remains ready for governance-layer expansion.")
    lines.append("")
    lines.append("## Guardrails")
    lines.append("")
    lines.append("- does not modify scientific decisions")
    lines.append("- does not modify policies")
    lines.append("- does not bypass V15D")
    lines.append("- does not modify V16 execution plans")
    lines.append("- does not execute experiments")
    lines.append("- does not create strategy logic")
    lines.append("- does not approve live deployment")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- governance_checks: {summary['governance_checks']}")
    lines.append(f"- pass_count: {summary['pass_count']}")
    lines.append(f"- warn_count: {summary['warn_count']}")
    lines.append(f"- critical_count: {summary['critical_count']}")
    lines.append(f"- recommended_next_action: {summary['recommended_next_action']}")
    lines.append("")
    lines.append("## Findings")
    lines.append("")

    for row in rows:
        lines.append(f"### {row['governance_check']}")
        lines.append("")
        lines.append(f"- status: {row['status']}")
        lines.append(f"- severity: {row['severity']}")
        lines.append(f"- finding: {row['finding']}")
        lines.append(f"- recommendation: {row['recommendation']}")
        if row["missing_terms"]:
            lines.append(f"- missing_terms: {row['missing_terms']}")
        lines.append("")

    write_text(path, "\n".join(lines) + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build V17A scientific system governance assessment."
    )
    parser.add_argument(
        "--certification",
        default=DEFAULT_CERTIFICATION,
        help="Path to V11-V16 architecture certification markdown.",
    )
    parser.add_argument(
        "--v17-readiness",
        default=DEFAULT_PHASE5C,
        help="Path to Phase 5C V17 readiness CSV.",
    )
    parser.add_argument(
        "--final-judgment",
        default=DEFAULT_PHASE5D,
        help="Path to Phase 5D final architecture judgment markdown.",
    )
    parser.add_argument(
        "--output-dir",
        default="outputs/trade_inspector/v17a/smoke_system_governance_2026-06-21",
        help="Output directory for V17A artifacts.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    certification_path = Path(args.certification)
    readiness_path = Path(args.v17_readiness)
    judgment_path = Path(args.final_judgment)
    output_dir = Path(args.output_dir)

    certification_text = read_text_file(certification_path)
    judgment_text = read_text_file(judgment_path)
    readiness_rows, _ = read_csv(readiness_path)

    governance_rows = [
        evaluate_certification(certification_text),
        evaluate_v17_readiness(readiness_rows),
        evaluate_forbidden_scope(certification_text, judgment_text),
        evaluate_protected_boundaries(certification_text),
    ]

    summary_rows = build_summary(governance_rows)

    governance_fields = [
        "governance_check",
        "status",
        "severity",
        "finding",
        "missing_terms",
        "recommendation",
    ]

    summary_fields = list(summary_rows[0].keys())

    write_csv(output_dir / "v17a_governance_assessment.csv", governance_rows, governance_fields)
    write_csv(output_dir / "v17a_governance_summary.csv", summary_rows, summary_fields)
    write_report(output_dir / "V17A_SCIENTIFIC_SYSTEM_GOVERNANCE_ENGINE_REPORT_2026-06-21.md", summary_rows[0], governance_rows)

    print("V17A Scientific System Governance Engine completed.")
    print(f"Governance checks: {len(governance_rows)}")
    print(f"Governance status: {summary_rows[0]['governance_status']}")
    print(f"Output dir: {output_dir}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
