#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Trade Inspector V13A.3

Research Opportunity Engine.

Purpose:
- Convert V13A hypothesis intelligence, knowledge state, gaps, dependencies and conflicts
  into concrete research opportunities.
- Prioritize work by expected knowledge gain, uncertainty reduction, decision impact,
  feasibility and cost efficiency.
- Produce explainable next research opportunities.

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


OPPORTUNITY_FIELDS = [
    "opportunity_id",
    "opportunity_type",
    "scientific_priority",
    "hypothesis_id",
    "hypothesis_group",
    "knowledge_gap",
    "research_question",
    "expected_information_gain",
    "expected_decision_impact",
    "scientific_novelty",
    "feasibility_score",
    "cost_efficiency_score",
    "estimated_research_cost",
    "uncertainty_before",
    "expected_uncertainty_after",
    "confidence_before",
    "expected_confidence_after",
    "blocking_dependencies",
    "required_inputs",
    "success_criterion",
    "recommended_experiment",
    "recommended_next_action",
    "opportunity_score",
    "positive_drivers",
    "negative_drivers",
    "reason",
    "created_at_utc",
]

SUMMARY_FIELDS = [
    "metric",
    "value",
]

MANIFEST_FIELDS = [
    "artifact",
    "path",
    "rows",
    "status",
]


def index_by(rows: list[dict[str, str]], key: str) -> dict[str, dict[str, str]]:
    return {row[key]: row for row in rows if row.get(key)}


def group_by(rows: list[dict[str, str]], key: str) -> dict[str, list[dict[str, str]]]:
    out: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        value = row.get(key, "")
        if value:
            out.setdefault(value, []).append(row)
    return out


def cost_to_score(cost: float) -> float:
    return clamp(100.0 - cost)


def feasibility_score(dep_count: int, conflict_count: int, cost: float) -> float:
    raw = 100.0
    raw -= min(dep_count * 25.0, 50.0)
    raw -= min(conflict_count * 20.0, 40.0)
    raw -= min(cost * 0.30, 30.0)
    return clamp(raw)


def decision_impact(row: dict[str, str]) -> float:
    global_score = to_float(row.get("global_intelligence_score"))
    uncertainty = to_float(row.get("scientific_uncertainty"))
    coverage = to_float(row.get("research_coverage_score"))
    return clamp(global_score * 0.40 + uncertainty * 0.35 + (100.0 - coverage) * 0.25)


def opportunity_type_for(
    row: dict[str, str],
    gap_rows: list[dict[str, str]],
    dep_rows: list[dict[str, str]],
    conflict_rows: list[dict[str, str]],
) -> str:
    uncertainty = to_float(row.get("scientific_uncertainty"))
    coverage = to_float(row.get("research_coverage_score"))
    strength = to_float(row.get("evidence_strength"))
    info_gain = to_float(row.get("information_gain_score"))

    if conflict_rows:
        return "CONFLICT_RESOLUTION"
    if dep_rows:
        return "DEPENDENCY_RESOLUTION"
    if coverage < 35:
        return "COVERAGE_EXPANSION"
    if strength < 30:
        return "NEW_ARCHIVE_COLLECTION"
    if uncertainty >= 65:
        return "ROBUSTNESS_VALIDATION"
    if info_gain >= 65:
        return "REPLAY_VALIDATION"
    if gap_rows:
        return "KNOWLEDGE_CONSOLIDATION"
    return "BACKGROUND_RESEARCH"


def question_for(opportunity_type: str, row: dict[str, str]) -> str:
    group = row.get("hypothesis_group", "unknown_hypothesis")

    if opportunity_type == "CONFLICT_RESOLUTION":
        return f"What evidence is needed to resolve conflicts around {group}?"
    if opportunity_type == "DEPENDENCY_RESOLUTION":
        return f"Which dependency blocks stronger conclusions about {group}?"
    if opportunity_type == "COVERAGE_EXPANSION":
        return f"Which missing archive or validation would improve coverage for {group}?"
    if opportunity_type == "NEW_ARCHIVE_COLLECTION":
        return f"Which additional real archive is needed to strengthen evidence for {group}?"
    if opportunity_type == "ROBUSTNESS_VALIDATION":
        return f"Does {group} remain stable under additional validation conditions?"
    if opportunity_type == "REPLAY_VALIDATION":
        return f"Can replay validation confirm the expected information gain for {group}?"
    if opportunity_type == "KNOWLEDGE_CONSOLIDATION":
        return f"Which evidence should be consolidated before prioritizing {group} further?"
    return f"Should {group} remain on the research watchlist?"


def experiment_for(opportunity_type: str) -> str:
    return {
        "CONFLICT_RESOLUTION": "targeted_conflict_review",
        "DEPENDENCY_RESOLUTION": "dependency_resolution_review",
        "COVERAGE_EXPANSION": "collect_more_archives_then_recompute_v13a",
        "NEW_ARCHIVE_COLLECTION": "collect_real_archives",
        "ROBUSTNESS_VALIDATION": "controlled_replay_robustness_validation",
        "REPLAY_VALIDATION": "controlled_replay_validation",
        "KNOWLEDGE_CONSOLIDATION": "knowledge_consolidation_review",
        "BACKGROUND_RESEARCH": "watchlist_review",
    }.get(opportunity_type, "manual_research_review")


def required_inputs_for(opportunity_type: str) -> str:
    return {
        "CONFLICT_RESOLUTION": "conflict_network;related_hypotheses;validation_evidence",
        "DEPENDENCY_RESOLUTION": "dependency_graph;next_learning_need",
        "COVERAGE_EXPANSION": "additional_archives;v11_v12_refresh",
        "NEW_ARCHIVE_COLLECTION": "additional_real_archives",
        "ROBUSTNESS_VALIDATION": "replay_data;archive_comparison;stability_metrics",
        "REPLAY_VALIDATION": "replay_validation_plan;market_data;expected_metrics",
        "KNOWLEDGE_CONSOLIDATION": "knowledge_base;research_memory;relationship_graph",
        "BACKGROUND_RESEARCH": "future_evidence",
    }.get(opportunity_type, "manual_review")


def success_criterion_for(opportunity_type: str) -> str:
    return {
        "CONFLICT_RESOLUTION": "conflict_severity_reduced_or_explained",
        "DEPENDENCY_RESOLUTION": "blocking_dependency_removed_or_reclassified",
        "COVERAGE_EXPANSION": "research_coverage_score_increases",
        "NEW_ARCHIVE_COLLECTION": "evidence_strength_and_diversity_increase",
        "ROBUSTNESS_VALIDATION": "scientific_uncertainty_decreases_without_conflict_increase",
        "REPLAY_VALIDATION": "expected_information_gain_confirmed_by_replay",
        "KNOWLEDGE_CONSOLIDATION": "knowledge_fragmentation_decreases",
        "BACKGROUND_RESEARCH": "watchlist_status_preserved_or_reclassified",
    }.get(opportunity_type, "manual_success_review")


def priority_class(score: float) -> str:
    if score >= 85:
        return "CRITICAL"
    if score >= 75:
        return "VERY_HIGH"
    if score >= 60:
        return "HIGH"
    if score >= 45:
        return "MEDIUM"
    if score >= 30:
        return "LOW"
    return "BACKGROUND"


def positive_drivers(row: dict[str, str], feasibility: float, cost_eff: float, impact: float) -> str:
    parts: list[str] = []

    if to_float(row.get("expected_knowledge_gain")) >= 60:
        parts.append("high_expected_knowledge_gain")
    if to_float(row.get("scientific_uncertainty")) >= 55:
        parts.append("meaningful_uncertainty_reduction_potential")
    if to_float(row.get("novelty_score")) >= 60:
        parts.append("high_scientific_novelty")
    if impact >= 60:
        parts.append("high_decision_impact")
    if feasibility >= 70:
        parts.append("high_feasibility")
    if cost_eff >= 70:
        parts.append("good_cost_efficiency")

    return ";".join(parts) if parts else "no_strong_positive_driver"


def negative_drivers(row: dict[str, str], dep_count: int, conflict_count: int, cost: float) -> str:
    parts: list[str] = []

    if to_float(row.get("research_coverage_score")) < 35:
        parts.append("low_research_coverage")
    if dep_count > 0:
        parts.append("blocking_dependencies")
    if conflict_count > 0:
        parts.append("unresolved_conflicts")
    if cost >= 70:
        parts.append("high_estimated_cost")
    if to_float(row.get("evidence_strength")) < 30:
        parts.append("weak_evidence_strength")

    return ";".join(parts) if parts else "no_strong_negative_driver"


def build_opportunity(
    row: dict[str, str],
    gap_rows: list[dict[str, str]],
    dep_rows: list[dict[str, str]],
    conflict_rows: list[dict[str, str]],
) -> dict[str, Any]:
    hid = row.get("hypothesis_id", "")
    opportunity_type = opportunity_type_for(row, gap_rows, dep_rows, conflict_rows)

    expected_kg = to_float(row.get("expected_knowledge_gain"))
    uncertainty = to_float(row.get("scientific_uncertainty"))
    confidence = to_float(row.get("scientific_confidence"))
    novelty = to_float(row.get("novelty_score"))
    cost = to_float(row.get("research_cost_score"))

    dep_count = len(dep_rows)
    conflict_count = len(conflict_rows)

    feasibility = feasibility_score(dep_count, conflict_count, cost)
    cost_eff = cost_to_score(cost)
    impact = decision_impact(row)

    score = clamp(
        expected_kg * 0.30
        + impact * 0.25
        + novelty * 0.15
        + feasibility * 0.15
        + cost_eff * 0.15
    )

    expected_uncertainty_after = clamp(uncertainty - (score * 0.20))
    expected_confidence_after = clamp(confidence + (score * 0.15))

    if gap_rows:
        knowledge_gap = ";".join(sorted({g.get("gap_type", "") for g in gap_rows if g.get("gap_type")}))
    elif dep_rows:
        knowledge_gap = "dependency_blocks_research_progress"
    elif conflict_rows:
        knowledge_gap = "conflict_blocks_research_confidence"
    else:
        knowledge_gap = "no_major_gap_detected"

    return {
        "opportunity_id": stable_hash_id("ROP-", [hid, opportunity_type, knowledge_gap]),
        "opportunity_type": opportunity_type,
        "scientific_priority": priority_class(score),
        "hypothesis_id": hid,
        "hypothesis_group": row.get("hypothesis_group", ""),
        "knowledge_gap": knowledge_gap,
        "research_question": question_for(opportunity_type, row),
        "expected_information_gain": round(to_float(row.get("information_gain_score")), 4),
        "expected_decision_impact": round(impact, 4),
        "scientific_novelty": round(novelty, 4),
        "feasibility_score": round(feasibility, 4),
        "cost_efficiency_score": round(cost_eff, 4),
        "estimated_research_cost": round(cost, 4),
        "uncertainty_before": round(uncertainty, 4),
        "expected_uncertainty_after": round(expected_uncertainty_after, 4),
        "confidence_before": round(confidence, 4),
        "expected_confidence_after": round(expected_confidence_after, 4),
        "blocking_dependencies": ";".join(d.get("dependency_type", "") for d in dep_rows) if dep_rows else "none",
        "required_inputs": required_inputs_for(opportunity_type),
        "success_criterion": success_criterion_for(opportunity_type),
        "recommended_experiment": experiment_for(opportunity_type),
        "recommended_next_action": row.get("recommended_next_action_v13a", ""),
        "opportunity_score": round(score, 4),
        "positive_drivers": positive_drivers(row, feasibility, cost_eff, impact),
        "negative_drivers": negative_drivers(row, dep_count, conflict_count, cost),
        "reason": "prioritized_by_expected_knowledge_gain_decision_impact_feasibility_and_cost_efficiency",
        "created_at_utc": now_utc(),
    }


def write_report(path: Path, opportunities: list[dict[str, Any]], summary_rows: list[dict[str, Any]]) -> None:
    lines: list[str] = []
    lines.append("# V13A.3 RESEARCH OPPORTUNITY ENGINE REPORT")
    lines.append("")
    lines.append(f"Date: {date.today().isoformat()}")
    lines.append("Scope: Trade Inspector V13A.3")
    lines.append("")
    lines.append("## Objective")
    lines.append("")
    lines.append("Convert V13A intelligence artifacts into concrete research opportunities.")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("| metric | value |")
    lines.append("|---|---:|")
    for row in summary_rows:
        lines.append(f"| {row['metric']} | {row['value']} |")
    lines.append("")
    lines.append("## Top Opportunities")
    lines.append("")
    lines.append("| rank | opportunity_id | type | priority | hypothesis | score | experiment |")
    lines.append("|---:|---|---|---|---|---:|---|")
    for i, row in enumerate(opportunities[:20], 1):
        lines.append(
            f"| {i} | {row['opportunity_id']} | {row['opportunity_type']} | "
            f"{row['scientific_priority']} | {row['hypothesis_id']} | "
            f"{row['opportunity_score']} | {row['recommended_experiment']} |"
        )
    lines.append("")
    lines.append("## Guardrails")
    lines.append("")
    lines.append("- V13A.3 does not execute experiments.")
    lines.append("- V13A.3 does not modify strategy logic.")
    lines.append("- V13A.3 only recommends research opportunities.")
    lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--hypothesis-intelligence", required=True)
    parser.add_argument("--knowledge-state", required=True)
    parser.add_argument("--research-gaps", required=True)
    parser.add_argument("--relationship-graph", required=True)
    parser.add_argument("--dependency-graph", required=True)
    parser.add_argument("--conflict-network", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    intelligence_path = Path(args.hypothesis_intelligence)
    knowledge_state_path = Path(args.knowledge_state)
    gaps_path = Path(args.research_gaps)
    relationship_path = Path(args.relationship_graph)
    dependency_path = Path(args.dependency_graph)
    conflict_path = Path(args.conflict_network)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    intelligence_rows = read_csv(intelligence_path)
    knowledge_state_rows = read_csv(knowledge_state_path)
    gap_rows = read_csv(gaps_path)
    relationship_rows = read_csv(relationship_path)
    dependency_rows = read_csv(dependency_path)
    conflict_rows = read_csv(conflict_path)

    gaps_by_id = group_by(gap_rows, "hypothesis_id")
    deps_by_id = group_by(dependency_rows, "hypothesis_id")
    conflicts_by_id = group_by(conflict_rows, "hypothesis_id")

    opportunities: list[dict[str, Any]] = []

    for row in intelligence_rows:
        hid = row.get("hypothesis_id", "")
        opportunities.append(
            build_opportunity(
                row,
                gaps_by_id.get(hid, []),
                deps_by_id.get(hid, []),
                conflicts_by_id.get(hid, []),
            )
        )

    opportunities.sort(key=lambda r: -to_float(r.get("opportunity_score")))

    type_counts: dict[str, int] = {}
    priority_counts: dict[str, int] = {}
    for row in opportunities:
        type_counts[str(row["opportunity_type"])] = type_counts.get(str(row["opportunity_type"]), 0) + 1
        priority_counts[str(row["scientific_priority"])] = priority_counts.get(str(row["scientific_priority"]), 0) + 1

    summary_rows: list[dict[str, Any]] = [
        {"metric": "hypothesis_intelligence_rows", "value": len(intelligence_rows)},
        {"metric": "knowledge_state_rows", "value": len(knowledge_state_rows)},
        {"metric": "research_gap_rows", "value": len(gap_rows)},
        {"metric": "relationship_rows", "value": len(relationship_rows)},
        {"metric": "dependency_rows", "value": len(dependency_rows)},
        {"metric": "conflict_rows", "value": len(conflict_rows)},
        {"metric": "research_opportunity_rows", "value": len(opportunities)},
    ]

    for key in sorted(type_counts):
        summary_rows.append({"metric": f"opportunity_type_{key}", "value": type_counts[key]})

    for key in sorted(priority_counts):
        summary_rows.append({"metric": f"scientific_priority_{key}", "value": priority_counts[key]})

    opportunities_path = out_dir / "v13a_research_opportunities.csv"
    summary_path = out_dir / "v13a_research_opportunity_summary.csv"
    manifest_path = out_dir / "v13a_research_opportunity_manifest.csv"
    report_path = out_dir / f"V13A3_RESEARCH_OPPORTUNITY_ENGINE_REPORT_{date.today().isoformat()}.md"

    write_csv(opportunities_path, opportunities, OPPORTUNITY_FIELDS)
    write_csv(summary_path, summary_rows, SUMMARY_FIELDS)

    manifest_rows = [
        {"artifact": "v13a_research_opportunities.csv", "path": str(opportunities_path), "rows": len(opportunities), "status": "created"},
        {"artifact": "v13a_research_opportunity_summary.csv", "path": str(summary_path), "rows": len(summary_rows), "status": "created"},
        {"artifact": report_path.name, "path": str(report_path), "rows": 1, "status": "created"},
    ]
    write_csv(manifest_path, manifest_rows, MANIFEST_FIELDS)
    write_report(report_path, opportunities, summary_rows)

    print("V13A.3 research opportunity engine completed")
    print("hypothesis_intelligence_rows:", len(intelligence_rows))
    print("knowledge_state_rows:", len(knowledge_state_rows))
    print("research_gap_rows:", len(gap_rows))
    print("relationship_rows:", len(relationship_rows))
    print("dependency_rows:", len(dependency_rows))
    print("conflict_rows:", len(conflict_rows))
    print("research_opportunity_rows:", len(opportunities))
    print("report:", report_path)
    print("csv:", opportunities_path)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
